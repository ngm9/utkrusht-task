#!/usr/bin/env python
"""run_pipeline.py — linear orchestrator for the task-generation pipeline.

Chains the five stages into one command:

    preflight -> generate_input_files -> scenario_generator
              -> prompt_generator -> multiagent.py generate_tasks

This is NOT the autonomous task agent. There is no coordinator-agent
intelligence, no per-stage verifier agents, and no prompt-level escalation —
it is a plain linear runner. It removes the manual path-juggling you would
otherwise do between generate_input_files (which creates files) and the stages
that consume them. The smart autonomous version is the Phase 2 design in
docs/research/autonomous-task-agent/autonomous-task-agent.md.

Behaviour:
  - Stops at the first stage that fails (non-zero exit).
  - Stage 4 (task creation) exit 0 even when the eval gate rejects the task —
    the summary inspects stdout to report REJECTED vs CREATED.
  - Every stage's stdout/stderr/timing is logged under
    .task_agent_runs/run-<UTC timestamp>/<combo>/.

Usage:
    python run_pipeline.py --name "Python - Django" --proficiency BASIC
    python run_pipeline.py --name "Python, SQL" --proficiency BASIC --count 3
    python run_pipeline.py -n Python -n Pinecone -p INTERMEDIATE --env dev
    python run_pipeline.py --name "Rust" --proficiency BASIC --skip-preflight

Run it with the project venv's Python (.venv/bin/python) so the subprocess
stages inherit the right interpreter.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()
RUNS_DIR = REPO_ROOT / ".task_agent_runs"
INPUT_FILES_ROOT = REPO_ROOT / "data" / "generated" / "input_files"
SCENARIOS_ROOT = REPO_ROOT / "data" / "generated" / "scenarios"


def scenarios_file_for(level: str) -> Path:
    """Return the scenarios file that stage 02 actually writes for `level`.

    Mirrors generators.scenarios.generator.get_target_scenario_file —
    INTERMEDIATE goes to its own file, everything else lands in
    task_scenarios.json. Keep this in lockstep with the generator.
    """
    if level.upper() == "INTERMEDIATE":
        return SCENARIOS_ROOT / "task_scenarios_intermediate.json"
    return SCENARIOS_ROOT / "task_scenarios.json"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _pick_python() -> str:
    """Prefer the project venv interpreter; fall back to whatever ran us."""
    venv_py = REPO_ROOT / ".venv" / "bin" / "python"
    return str(venv_py) if venv_py.exists() else sys.executable


def _parse_names(raw: list[str]) -> list[str]:
    """Accept --name "A, B" and repeated --name A --name B."""
    names: list[str] = []
    for item in raw:
        names.extend(part.strip() for part in item.split(",") if part.strip())
    return names


def _combo_slug(names: list[str]) -> str:
    """Mirror the slug logic the other modules use, via prompt_generator.slugs."""
    from generators.prompts.slugs import slugify
    return "_".join(slugify(n) for n in names)


def _run_stage(combo_dir: Path, label: str, cmd: list[str]) -> dict:
    """Run one stage as a subprocess; capture stdout/stderr/timing.

    Returns a dict: {label, cmd, duration_s, exit_code, stdout_path, ...}.
    """
    stdout_path = combo_dir / f"{label}.stdout"
    stderr_path = combo_dir / f"{label}.stderr"
    timing_path = combo_dir / f"{label}.timing.json"

    print(f"  ▶ {label}: {' '.join(cmd)}", flush=True)
    start = time.time()
    # The E2B build/test gate is opt-out for pipeline runs: default it ON so
    # the task-creation stage exercises it (the gate itself no-ops for the
    # other stages). An explicit SANDBOX_EVAL_ENABLED in the environment wins.
    stage_env = {**os.environ}
    stage_env.setdefault("SANDBOX_EVAL_ENABLED", "true")
    with stdout_path.open("w", encoding="utf-8") as out, \
         stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, stdout=out, stderr=err, cwd=REPO_ROOT,
                              env=stage_env)
    duration = round(time.time() - start, 1)

    record = {
        "label": label,
        "cmd": cmd,
        "duration_s": duration,
        "exit_code": proc.returncode,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }
    timing_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    flag = "ok" if proc.returncode == 0 else f"FAIL exit={proc.returncode}"
    print(f"  ◀ {label}: {flag}  ({duration}s)", flush=True)
    return record


def _locate_input_files(names: list[str], level: str, since: float) -> tuple[Path, Path]:
    """Find the competency_*.json + background_*.json that stage 1 produced.

    Strategy: prefer files modified after the stage started (newly written);
    fall back to files whose path matches the combo slug + level. Picks the
    newest of each. Raises if either cannot be found.
    """
    slug = _combo_slug(names)
    level_l = level.lower()

    def _best(pattern: str) -> Path | None:
        hits = list(INPUT_FILES_ROOT.rglob(pattern))
        if not hits:
            return None
        fresh = [p for p in hits if p.stat().st_mtime >= since - 1]
        pool = fresh or [
            p for p in hits
            if slug in str(p).lower() and level_l in str(p).lower()
        ]
        if not pool:
            return None
        return max(pool, key=lambda p: p.stat().st_mtime)

    comp = _best("competency_*.json")
    bg = _best("background_*.json")
    if comp is None:
        raise FileNotFoundError(
            f"Could not locate the competency JSON for {names} {level} "
            f"after generate_input_files. Check the stage 1 log."
        )
    if bg is None:
        raise FileNotFoundError(
            f"Could not locate the background JSON for {names} {level} "
            f"after generate_input_files. Check the stage 1 log."
        )
    return comp, bg


def _summarise_task_stage(stdout_path: Path) -> str:
    """Read the multiagent stdout and classify the outcome."""
    text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
    if "EVAL GATE REJECTED TASK" in text:
        return "EVAL GATE REJECTED — no task created (3 attempts failed)"
    if "TASK CREATION COMPLETED SUCCESSFULLY" in text or "Task Creation Successful" in text:
        return "TASK CREATED"
    if "ERROR CREATING TASK" in text:
        return "ERROR — see stage 4 logs"
    return "UNKNOWN — inspect stage 4 logs"


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--name", action="append", required=True,
                    help='Competency name(s). Comma-separated or repeated.')
    ap.add_argument("-p", "--proficiency", required=True,
                    choices=["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"])
    ap.add_argument("--env", default="dev", choices=["dev", "prod"])
    ap.add_argument("--count", type=int, default=2,
                    help="Number of scenarios to generate (default 2).")
    ap.add_argument("--focus-areas", action="append", default=[],
                    help="Focus area(s) for scenarios. Comma-separated or repeated.")
    ap.add_argument("--domain", default=None,
                    help="Pin all scenarios to one business domain.")
    ap.add_argument("--skip-preflight", action="store_true",
                    help="Skip the preflight stage (not recommended).")
    ap.add_argument("--python", default=None,
                    help="Python interpreter for subprocess stages "
                         "(default: project venv, else current).")
    args = ap.parse_args()

    py = args.python or _pick_python()
    names = _parse_names(args.name)
    level = args.proficiency.upper()
    focus_areas: list[str] = []
    for item in args.focus_areas:
        focus_areas.extend(p.strip() for p in item.split(",") if p.strip())
    if not names:
        print("ERROR: no competency names parsed from --name", file=sys.stderr)
        return 2

    # Set up the run directory.
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    combo_label = _combo_slug(names) + "_" + level.lower()
    combo_dir = RUNS_DIR / f"run-{ts}" / combo_label
    combo_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 68}")
    print(f" TASK PIPELINE  ·  {' + '.join(names)}  ({level})")
    print(f" env={args.env}  scenarios={args.count}  python={py}")
    print(f" logs: {combo_dir}")
    print(f"{'=' * 68}\n")

    stages: list[dict] = []

    # --- Stage 0: preflight ------------------------------------------------
    if not args.skip_preflight:
        combo_arg = f"{','.join(names)}:{level}"
        rec = _run_stage(combo_dir, "00_preflight", [
            py, "task_agent_preflight.py", "--combo", combo_arg, "--env", args.env,
        ])
        stages.append(rec)
        if rec["exit_code"] != 0:
            print("\n  Preflight FAILED — aborting. See 00_preflight.stdout.")
            _write_summary(combo_dir, names, level, stages, "ABORTED_AT_PREFLIGHT")
            return 1

    # --- Stage 1: input files ---------------------------------------------
    t0 = time.time()
    input_cmd = [
        py, "-m", "generators.input_files",
        "--competency-name", ", ".join(names),
        "--proficiency", level, "--env", args.env,
    ]
    if args.domain:
        input_cmd += ["--domain", args.domain]
    rec = _run_stage(combo_dir, "01_input_files", input_cmd)
    stages.append(rec)
    if rec["exit_code"] != 0:
        print("\n  generate_input_files FAILED — aborting.")
        _write_summary(combo_dir, names, level, stages, "ABORTED_AT_INPUT_FILES")
        return 1

    try:
        comp_json, bg_json = _locate_input_files(names, level, t0)
    except FileNotFoundError as e:
        print(f"\n  {e}")
        _write_summary(combo_dir, names, level, stages, "ABORTED_LOCATING_INPUTS")
        return 1
    print(f"    competency: {comp_json.relative_to(REPO_ROOT)}")
    print(f"    background: {bg_json.relative_to(REPO_ROOT)}")

    # --- Stage 2: scenarios -----------------------------------------------
    scenario_cmd = [
        py, "-m", "generators.scenarios",
        "--competency-file", str(comp_json),
        "--background-file", str(bg_json),
        "--count", str(args.count), "--append",
    ]
    for area in focus_areas:
        scenario_cmd += ["--focus-areas", area]
    if args.domain:
        scenario_cmd += ["--domain", args.domain]
    rec = _run_stage(combo_dir, "02_scenarios", scenario_cmd)
    stages.append(rec)
    if rec["exit_code"] != 0:
        print("\n  scenario_generator FAILED — aborting.")
        _write_summary(combo_dir, names, level, stages, "ABORTED_AT_SCENARIOS")
        return 1

    # --- Stage 3: prompt generator ----------------------------------------
    rec = _run_stage(combo_dir, "03_prompt", [
        py, "-m", "generators.prompts",
        "--name", ", ".join(names),
        "--proficiency", level, "--env", args.env, "--force", "--verbose",
    ])
    stages.append(rec)
    if rec["exit_code"] != 0:
        print("\n  prompt_generator FAILED — aborting.")
        _write_summary(combo_dir, names, level, stages, "ABORTED_AT_PROMPT")
        return 1

    # --- Stage 4: task creation -------------------------------------------
    # `--env` MUST be threaded here — multiagent.py stores the task in the
    # Supabase environment it is told; without this flag it silently defaults
    # to `dev`, so a `--env prod` run would create the task but store it in dev.
    rec = _run_stage(combo_dir, "04_tasks", [
        py, "multiagent.py", "generate_tasks",
        "-c", str(comp_json), "-b", str(bg_json),
        "-s", str(scenarios_file_for(level)),
        "--env", args.env,
    ])
    stages.append(rec)
    task_outcome = _summarise_task_stage(Path(rec["stdout"]))

    status = "COMPLETED" if rec["exit_code"] == 0 else "STAGE_4_ERROR"
    _write_summary(combo_dir, names, level, stages, status, task_outcome)

    # --- Final report -----------------------------------------------------
    total = round(sum(s["duration_s"] for s in stages), 1)
    print(f"\n{'─' * 68}")
    print(f" PIPELINE DONE  ·  {' + '.join(names)} ({level})")
    print(f"{'─' * 68}")
    for s in stages:
        print(f"   {s['label']:<16} {s['duration_s']:>7.1f}s   exit={s['exit_code']}")
    print(f"   {'TOTAL':<16} {total:>7.1f}s")
    print(f"\n   Stage 4 outcome: {task_outcome}")
    print(f"   Logs: {combo_dir}")
    print(f"{'─' * 68}\n")
    return 0


def _write_summary(combo_dir: Path, names: list[str], level: str,
                   stages: list[dict], status: str, task_outcome: str = "") -> None:
    summary = {
        "competencies": names,
        "proficiency": level,
        "status": status,
        "task_outcome": task_outcome,
        "stages": [
            {"label": s["label"], "duration_s": s["duration_s"], "exit_code": s["exit_code"]}
            for s in stages
        ],
        "total_duration_s": round(sum(s["duration_s"] for s in stages), 1),
    }
    (combo_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
