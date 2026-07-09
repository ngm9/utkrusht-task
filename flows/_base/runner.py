"""Generic, flow-agnostic subprocess pipeline runner.

Extracted verbatim from ``run_pipeline.py`` (behaviour-preserving) so every flow
can share the same machinery: per-stage stdout/stderr/timing capture, live
stderr sub-log splitting, the venv interpreter picker, and the run summary
writer. Only module addresses changed; behaviour is identical.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# repo root = two levels up from flows/_base/runner.py
REPO_ROOT = Path(__file__).resolve().parents[2]

# Stages whose label implies LLM tracing when `traced` is not passed explicitly
# (preserves the original run_pipeline substring behaviour).
_TRACED_SUBSTRINGS = ("input_files", "scenarios", "prompt", "tasks")

# Markers used to split the interleaved stage-4 stderr into focused sub-logs.
# The infra_assessor logger writes the E2B gate and LLM-eval lines to stderr;
# this is a best-effort substring filter.
E2B_GATE_MARKERS = ("[e2b-gate]", "sandbox gate", "Eval gate rejected", "readiness gate")
EVAL_MARKERS = (
    "task eval", "code eval", "task evaluation", "code evaluation",
    "Running task eval", "Running code eval", "Running task evaluations",
    "blocking_issues", "validated_criteria", "Task generation attempt",
    "Applying feedback from previous attempt", "is_task_hollow", "hollow",
)


def pick_python() -> str:
    """Prefer the project venv interpreter; fall back to whatever ran us.

    Checks BOTH the POSIX (``.venv/bin/python``) and Windows
    (``.venv/Scripts/python.exe``) venv layouts.
    """
    for parts in (("bin", "python"), ("Scripts", "python.exe")):
        venv_py = REPO_ROOT.joinpath(".venv", *parts)
        if venv_py.exists():
            return str(venv_py)
    return sys.executable


def run_stage_streaming(cmd, stdout_path, stderr_path, stage_env, combo_dir,
                        live_split) -> int:
    """Run ``cmd`` streaming its stderr line-by-line so focused sub-logs appear
    DURING the stage, not after it.

    Every stderr line is written to ``stderr_path`` (the full log, unchanged) and
    ALSO fanned into each ``(filename, markers)`` sub-log whose markers it matches
    — each sub-log is created lazily on its first matching line and flushed per
    line. stdout goes straight to its file (only stderr is a pipe → no deadlock).
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


def run_stage(combo_dir: Path, label: str, cmd: list[str],
              live_split: "list | None" = None,
              traced: "bool | None" = None) -> dict:
    """Run one stage as a subprocess; capture stdout/stderr/timing.

    ``live_split`` (a list of ``(filename, markers)``) streams the stage's stderr
    and fans matching lines into live sub-logs as they're produced (used by the
    task stage so the eval / e2b-gate logs appear during the run).

    ``traced`` sets ``PIPELINE_TRACING_ENABLED``. When ``None`` (default) it is
    derived from the label substrings — preserving the original behaviour so
    existing callers need no change; the registry-driven pipeline passes it
    explicitly.

    Returns a dict: {label, cmd, duration_s, exit_code, stdout, stderr}.
    """
    stdout_path = combo_dir / f"{label}.stdout"
    stderr_path = combo_dir / f"{label}.stderr"
    timing_path = combo_dir / f"{label}.timing.json"

    print(f"  ▶ {label}: {' '.join(cmd)}", flush=True)
    start = time.time()
    # The E2B build/test gate is opt-out for pipeline runs: default it ON so the
    # task-creation stage exercises it (the gate no-ops for other stages). An
    # explicit SANDBOX_EVAL_ENABLED in the environment wins.
    stage_env = {**os.environ}
    stage_env.setdefault("SANDBOX_EVAL_ENABLED", "true")
    # Force unbuffered stdout/stderr in EVERY stage subprocess so each line is
    # flushed to its log file as it is produced (live trace_ui streaming).
    stage_env["PYTHONUNBUFFERED"] = "1"
    # Pipeline tracing is captured for the LLM-bearing stages. Force the flag
    # explicitly per stage so an enabled value inherited from the parent shell
    # can't turn on a non-wired stage.
    if traced is None:
        traced = any(s in label for s in _TRACED_SUBSTRINGS)
    stage_env["PIPELINE_TRACING_ENABLED"] = "1" if traced else "0"
    if live_split:
        returncode = run_stage_streaming(
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


def write_summary(combo_dir: Path, names: list[str], level: str,
                  stages: list[dict], status: str, task_outcome: str = "") -> None:
    """Write the per-run ``summary.json`` into the combo run dir."""
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
