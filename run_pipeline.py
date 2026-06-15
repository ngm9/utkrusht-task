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

from dotenv import load_dotenv

# run_pipeline reads TRACE_S3_BUCKET / S3_REGION / AWS creds for the end-of-run
# log upload; the stage subprocesses load .env themselves, but the parent does
# not otherwise, so load it here.
load_dotenv()

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


def _run_stage_streaming(cmd, stdout_path, stderr_path, stage_env, combo_dir,
                         live_split) -> int:
    """Run ``cmd`` streaming its stderr line-by-line so focused sub-logs appear
    DURING the stage, not after it.

    Every stderr line is written to ``stderr_path`` (the full log, unchanged) and
    ALSO fanned into each ``(filename, markers)`` sub-log whose markers it matches
    — each sub-log is created lazily on its first matching line and flushed per
    line, so e.g. ``04_tasks.evals.log`` shows up the moment the eval starts.
    stdout goes straight to its file (only stderr is a pipe → no deadlock).
    Returns the child's exit code.
    """
    sub_handles: dict = {}
    try:
        with stdout_path.open("w", encoding="utf-8") as out, \
                stderr_path.open("w", encoding="utf-8") as err:
            proc = subprocess.Popen(
                cmd, stdout=out, stderr=subprocess.PIPE, cwd=REPO_ROOT,
                env=stage_env, text=True, bufsize=1, encoding="utf-8",
                errors="replace",
            )
            for line in proc.stderr:
                err.write(line)
                err.flush()
                for fname, markers in live_split:
                    if any(m in line for m in markers):
                        fh = sub_handles.get(fname)
                        if fh is None:
                            fh = (combo_dir / fname).open("w", encoding="utf-8")
                            sub_handles[fname] = fh
                        fh.write(line)
                        fh.flush()
            proc.wait()
            return proc.returncode
    finally:
        for fh in sub_handles.values():
            try:
                fh.close()
            except Exception:  # noqa: BLE001
                pass


def _run_stage(combo_dir: Path, label: str, cmd: list[str],
               live_split: "list | None" = None) -> dict:
    """Run one stage as a subprocess; capture stdout/stderr/timing.

    ``live_split`` (a list of ``(filename, markers)``) streams the stage's stderr
    and fans matching lines into live sub-logs as they're produced (used by the
    task stage so the eval / e2b-gate logs appear during the run).

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
    # Force unbuffered stdout/stderr in EVERY stage subprocess so each line is
    # flushed to its log file as it is produced. Without this the non-04 stages
    # block-buffer their output (it only lands when the stage exits), so the
    # live trace_ui viewer couldn't stream them. Stage 04 already line-buffers
    # via _run_stage_streaming; this makes the rest stream too.
    stage_env["PYTHONUNBUFFERED"] = "1"
    # Pipeline tracing is captured for the LLM-bearing stages (input_files /
    # scenarios / prompt / tasks) — each opens trace_run(TRACE_RUN_ID) in its
    # __main__ and writes into the shared run-<ts>/traces/ dir. Preflight has no
    # LLM calls. Force the flag explicitly per stage (not setdefault) so an
    # enabled value inherited from the parent shell can't turn on a non-wired
    # stage. TRACE_RUN_ID is inherited via {**os.environ}. Stages run
    # sequentially, so there are no concurrent writers to the shared JSONL.
    _traced = ("input_files", "scenarios", "prompt", "tasks")
    stage_env["PIPELINE_TRACING_ENABLED"] = "1" if any(s in label for s in _traced) else "0"
    if live_split:
        returncode = _run_stage_streaming(
            cmd, stdout_path, stderr_path, stage_env, combo_dir, live_split,
        )
    else:
        with stdout_path.open("w", encoding="utf-8") as out, \
             stderr_path.open("w", encoding="utf-8") as err:
            returncode = subprocess.run(
                cmd, stdout=out, stderr=err, cwd=REPO_ROOT, env=stage_env,
            ).returncode
    duration = round(time.time() - start, 1)

    record = {
        "label": label,
        "cmd": cmd,
        "duration_s": duration,
        "exit_code": returncode,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }
    timing_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    flag = "ok" if returncode == 0 else f"FAIL exit={returncode}"
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
        # Skip paths that cannot be stat()'d — Windows MAX_PATH (260 chars)
        # makes deeply-nested input-file paths unreadable even though rglob
        # still enumerates the dirent. Without this guard a single offending
        # file kills _locate_input_files even when the freshly-written stage 1
        # output is perfectly accessible.
        def _mtime_or_none(p: Path) -> float | None:
            try:
                return p.stat().st_mtime
            except OSError:
                return None
        statted: list[tuple[Path, float]] = []
        for p in hits:
            mt = _mtime_or_none(p)
            if mt is not None:
                statted.append((p, mt))
        if not statted:
            return None
        # Match the combo's EXACT directory as a path SEGMENT (not a substring):
        # slug 'nodejs' must match the dir literally named 'input_nodejs', NOT
        # 'input_reactjs_nodejs' (which merely contains 'nodejs'). Level is also
        # matched as a segment. Applied to BOTH branches so a freshly-written
        # file from a *different* combo can't win the mtime tiebreak either.
        want_dir = f"input_{slug}"

        def _in_combo_dir(p: Path) -> bool:
            segs = [seg.lower() for seg in p.parts]
            return want_dir in segs and level_l in segs

        combo = [(p, mt) for p, mt in statted if _in_combo_dir(p)]
        fresh = [(p, mt) for p, mt in combo if mt >= since - 1]
        pool = fresh or combo
        if not pool:
            return None
        return max(pool, key=lambda item: item[1])[0]

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


_RESOLVED_INPUTS_MARKER = "__INPUT_FILES_RESOLVED__"


def _parse_resolved_inputs(stdout_path: Path) -> tuple[Path, Path] | None:
    """Read the EXACT competency+background paths stage 1 reported, if present.

    Stage 1 (``generators.input_files``) emits a
    ``__INPUT_FILES_RESOLVED__ {json}`` line carrying the absolute paths it
    targeted. Consuming that is exact and robust — unlike re-globbing
    ``input_files/`` by slug, which mis-resolved a 'NodeJs' selection to the
    'reactjs_nodejs' combo dir (substring collision + mtime tiebreak when stage 1
    skipped writing pre-existing files).

    Returns ``(competency, background)`` when the marker is present and both
    paths exist on disk; otherwise ``None`` so the caller falls back to the
    legacy locate-by-glob (older ``input_files`` builds without the marker).
    """
    try:
        text = stdout_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in reversed(text.splitlines()):  # last marker wins
        if not line.startswith(_RESOLVED_INPUTS_MARKER):
            continue
        try:
            payload = json.loads(line[len(_RESOLVED_INPUTS_MARKER):].strip())
            comp = Path(payload["competency"])
            bg = Path(payload["background"])
        except (ValueError, KeyError, TypeError):
            return None
        return (comp, bg) if comp.is_file() and bg.is_file() else None
    return None


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


# Markers used to split the interleaved stage-4 stderr into focused sub-logs.
# The infra_assessor logger writes the E2B gate and LLM-eval lines to stderr;
# this is a best-effort substring filter (kept here so the orchestrator owns
# the run-dir layout, with no change to the task-generation code).
_E2B_GATE_MARKERS = ("[e2b-gate]", "sandbox gate", "Eval gate rejected", "readiness gate")
_EVAL_MARKERS = (
    "task eval", "code eval", "task evaluation", "code evaluation",
    "Running task eval", "Running code eval", "Running task evaluations",
    "blocking_issues", "validated_criteria", "Task generation attempt",
    "Applying feedback from previous attempt", "is_task_hollow", "hollow",
)


def _split_stage4_logs(combo_dir: Path) -> list[str]:
    """Extract focused e2b-gate and eval sub-logs from the interleaved
    ``04_tasks.stderr``.

    Writes ``04_tasks.e2b_gate.log`` and ``04_tasks.evals.log`` into the combo
    run dir so the gate verdict and eval outcomes are easy to inspect without
    grepping the full stderr. Returns the list of filenames actually written.
    """
    src = combo_dir / "04_tasks.stderr"
    if not src.exists():
        return []
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    written: list[str] = []
    for fname, markers in (
        ("04_tasks.e2b_gate.log", _E2B_GATE_MARKERS),
        ("04_tasks.evals.log", _EVAL_MARKERS),
    ):
        matched = [ln for ln in lines if any(m in ln for m in markers)]
        if matched:
            (combo_dir / fname).write_text("\n".join(matched) + "\n", encoding="utf-8")
            written.append(fname)
    return written


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
    # Pipeline tracing: share the run id with the task-gen subprocess so its
    # captured LLM-call traces land under .task_agent_runs/run-<ts>/traces/
    # (the sink prepends "run-" itself, so pass the bare timestamp).
    os.environ["TRACE_RUN_ID"] = ts
    combo_label = _combo_slug(names) + "_" + level.lower()
    # Share the combo slug with the task-gen subprocess too, so its trace upload
    # lands under the same `combo=<slug>/` S3 partition as the stage-log upload.
    os.environ["TRACE_COMBO"] = combo_label
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

    # Prefer the EXACT paths stage 1 reported (robust handoff); only fall back
    # to the legacy locate-by-glob when the marker is absent (older builds).
    resolved = _parse_resolved_inputs(combo_dir / "01_input_files.stdout")
    if resolved is not None:
        comp_json, bg_json = resolved
    else:
        try:
            comp_json, bg_json = _locate_input_files(names, level, t0)
        except FileNotFoundError as e:
            print(f"\n  {e}")
            _write_summary(combo_dir, names, level, stages, "ABORTED_LOCATING_INPUTS")
            return 1

    def _rel(p: Path) -> Path:
        try:
            return p.relative_to(REPO_ROOT)
        except ValueError:
            return p
    print(f"    competency: {_rel(comp_json)}")
    print(f"    background: {_rel(bg_json)}")

    # --- Stage 2: scenarios -----------------------------------------------
    # `--env` MUST be threaded here too: generators.scenarios defaults to dev,
    # so a `--env prod` run would otherwise write scenarios to the dev DB while
    # stage 4 reads from prod — leaving stage 4 with an empty scenario pool.
    scenario_cmd = [
        py, "-m", "generators.scenarios",
        "--competency-file", str(comp_json),
        "--background-file", str(bg_json),
        "--count", str(args.count), "--env", args.env, "--append",
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
    ], live_split=[
        # Stream the eval + e2b-gate sub-logs LIVE so they appear when the eval
        # starts, not only after the task stage finishes.
        ("04_tasks.e2b_gate.log", _E2B_GATE_MARKERS),
        ("04_tasks.evals.log", _EVAL_MARKERS),
    ])
    stages.append(rec)
    # Final reconcile: re-derive the sub-logs from the complete stderr in case the
    # live stream missed anything (idempotent — same content).
    sublogs = _split_stage4_logs(combo_dir)
    if sublogs:
        print(f"    stage-4 sub-logs: {', '.join(sublogs)}")
    task_outcome = _summarise_task_stage(Path(rec["stdout"]))

    status = "COMPLETED" if rec["exit_code"] == 0 else "STAGE_4_ERROR"
    _write_summary(combo_dir, names, level, stages, status, task_outcome)

    # Upload the stage logs to S3 alongside the JSONL traces (env-gated on
    # TRACE_S3_BUCKET, failure-isolated). Done here — after the summary + sub-log
    # reconcile — because this is where every log file is finalized. `ts` is the
    # bare run_id (matches the traces upload).
    from infra.tracing import upload_run_logs

    log_prefix = upload_run_logs(ts, combo_dir)
    if log_prefix:
        print(f"   Logs uploaded: {log_prefix}")

    # --- Final report -----------------------------------------------------
    total = round(sum(s["duration_s"] for s in stages), 1)
    print(f"\n{'─' * 68}")
    print(f" PIPELINE DONE  ·  {' + '.join(names)} ({level})")
    print(f"{'─' * 68}")
    for s in stages:
        print(f"   {s['label']:<16} {s['duration_s']:>7.1f}s   exit={s['exit_code']}")
    print(f"   {'TOTAL':<16} {total:>7.1f}s")

    # Per-stage LLM cost (estimated from captured token usage). Uses the same
    # shared pricing as the trace_ui Result panel — best-effort, never fatal.
    try:
        from infra.tracing.cost import compute_cost

        cost = compute_cost(RUNS_DIR / f"run-{ts}" / "traces")
    except Exception:  # noqa: BLE001
        cost = None
    if cost:
        print(f"\n   {'stage':<14} {'cost':>9} {'tokens':>9} {'time':>8}")
        for r in cost["by_stage"]:
            tks = r["input_tokens"] + r["output_tokens"]
            t = f"{r['duration_ms'] / 1000:.1f}s" if r.get("duration_ms") is not None else "-"
            print(f"   {r['stage']:<14} {'$' + format(r['usd'], '.4f'):>9} {tks:>9,} {t:>8}")
        print(f"   {'TOTAL':<14} {'$' + format(cost['total_usd'], '.4f'):>9} {cost['total_tokens']:>9,} {total:>6.1f}s")
        print("   (cost ≈ estimated from token usage × model pricing)")

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
