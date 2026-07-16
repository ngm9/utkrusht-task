"""Run the five-stage pipeline for a TaskBrief, emitting a StageEvent per stage."""
from __future__ import annotations

import datetime
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from flows.tech.pipeline import (
    REPO_ROOT,
    RUNS_DIR,
    _locate_input_files,
    _pick_python,
    _run_stage,
    _summarise_task_stage,
    scenarios_file_for,
)
from task_builder.log_tail import StageLogTailer
from task_builder.slots import TaskBrief

# Ordered stage labels the runner walks through.
STAGES = ("00_preflight", "01_input_files", "02_scenarios", "03_prompt", "04_tasks")


@dataclass(frozen=True)
class StageEvent:
    """One progress event streamed to the browser."""

    stage: str               # a STAGES label, or "done"
    status: str              # "running" | "ok" | "failed" | "completed"
    detail: str = ""
    duration_s: float | None = None
    outcome: str | None = None
    task_id: str | None = None
    task_url: str | None = None
    task_name: str | None = None
    task_type: str | None = None
    competencies: str | None = None
    env: str | None = None


EmitFn = Callable[[StageEvent], None]


# stage-4 stdout label -> result-dict key. "Competencies Covered:" is matched
# as the full phrase so it does not also catch the later bare "Competencies:"
# summary line.
# Order matters: a more-specific label must precede any label that is a prefix
# of it, because the extractor loop does a substring match and breaks on the
# first hit.
_RESULT_LABELS: tuple[tuple[str, str], ...] = (
    ("Task ID:", "task_id"),
    ("Task Name:", "task_name"),
    ("Competencies Covered:", "competencies"),
    ("Task Type:", "task_type"),
    ("GitHub Repository:", "task_url"),
)


def _extract_task_result(stdout_path: Path) -> dict[str, str | None]:
    """Pull the task's identifying fields from the stage-4 stdout.

    Returns a dict with keys task_id, task_url, task_name, task_type,
    competencies — each None when its line is absent (a failed run, a missing
    file, or an older multiagent.py).
    """
    fields: dict[str, str | None] = {
        "task_id": None, "task_url": None, "task_name": None,
        "task_type": None, "competencies": None,
    }
    if not stdout_path.exists():
        return fields
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        for label, key in _RESULT_LABELS:
            if label in line:
                fields[key] = line.split(label, 1)[1].strip() or None
                break
    return fields


def _make_stage_runner(combo_dir: Path, emit: EmitFn) -> Callable[[str, list[str]], dict]:
    """Build the `_stage(label, cmd)` helper bound to one combo_dir + emit.

    Emits running/log/ok/failed StageEvents around a subprocess, live-tailing
    its stdout/stderr so the browser sees output as it is produced.
    """
    def _stage(label: str, cmd: list[str]) -> dict:
        emit(StageEvent(stage=label, status="running"))
        start = time.time()
        tailer = StageLogTailer(
            [combo_dir / f"{label}.stdout", combo_dir / f"{label}.stderr"],
            lambda chunk: emit(StageEvent(stage=label, status="log", detail=chunk)),
        )
        tailer.start()
        try:
            rec = _run_stage(combo_dir, label, cmd)
        finally:
            tailer.stop()
        ok = rec["exit_code"] == 0
        emit(StageEvent(stage=label, status="ok" if ok else "failed",
                        duration_s=round(time.time() - start, 1),
                        detail="" if ok else f"exit code {rec['exit_code']}"))
        return rec

    return _stage


def _combo_dir(runs_root: Path, run_id: str) -> Path:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return runs_root / f"web-{ts}-{run_id}"


def run_prepare_for_brief(brief: TaskBrief, *, run_id: str, emit: EmitFn,
                          env: str = "dev", runs_root: Path = RUNS_DIR) -> None:
    """Phase 1 of the human-in-the-loop flow: run preflight → input_files →
    scenarios so a candidate scenario pool exists for the combo.

    Leaves the pool in the ``generated_scenarios`` DB table (and the input
    files on disk) for ``run_generate_for_brief`` to reuse. Always emits a
    terminal "done" event; on success the caller then loads the pool and shows
    it for selection.
    """
    py = _pick_python()
    names = list(brief.competencies)
    level = (brief.proficiency or "BASIC").upper()
    combo_dir = _combo_dir(runs_root, run_id)
    _stage = _make_stage_runner(combo_dir, emit)

    try:
        combo_dir.mkdir(parents=True, exist_ok=True)
        rec = _stage("00_preflight", [
            py, "-m", "flows.tech.stages.preflight",
            "--combo", f"{','.join(names)}:{level}", "--env", env,
        ])
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="preflight failed"))

        t0 = time.time()
        input_cmd = [
            py, "-m", "flows.tech.stages.input_files",
            "--competency-name", ", ".join(names),
            "--proficiency", level, "--role", brief.role or "", "--env", env,
        ]
        if brief.domain:
            input_cmd += ["--domain", brief.domain]
        rec = _stage("01_input_files", input_cmd)
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="input files failed"))

        comp_json, bg_json = _locate_input_files(names, level, t0)
        scenario_cmd = [
            py, "-m", "flows.tech.stages.scenarios",
            "--competency-file", str(comp_json), "--background-file", str(bg_json),
            "--count", str(brief.scenario_count), "--env", env, "--append",
        ]
        for area in brief.focus_areas:
            scenario_cmd += ["--focus-areas", area]
        if brief.domain:
            scenario_cmd += ["--domain", brief.domain]
        rec = _stage("02_scenarios", scenario_cmd)
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="scenario stage failed"))

        emit(StageEvent("done", "completed", detail="scenarios ready", env=env))
    except Exception as exc:  # noqa: BLE001 — surface any stage crash to the UI
        emit(StageEvent("done", "failed", detail=f"runner error: {exc}"))


def run_generate_for_brief(brief: TaskBrief, *, run_id: str, emit: EmitFn,
                           env: str = "dev", runs_root: Path = RUNS_DIR,
                           instructions: str = "", selected_scenario: str = "",
                           scenarios_prepared: bool = False) -> None:
    """Execute the pipeline for `brief`, calling `emit` before and after each stage.

    `env` selects the Supabase environment ("dev" or "prod") used by every
    stage, including stage 4's task storage.

    `instructions` is the authoritative free-text directive → passed to the
    prompt stage (`--instructions`); it shapes the task (infra vs non-infra,
    required deliverables, dependencies like Redis).

    `selected_scenario` is one human-picked scenario → written to a file and
    passed to stage 4 (`--scenario-file`), which locks generation to it.

    `scenarios_prepared` — when True the scenario pool already exists (a prior
    `run_prepare_for_brief` produced it), so stages 00–02 are skipped and the
    run reuses the on-disk input files + DB scenarios. When False the full
    five-stage pipeline runs.

    Stops at the first failing stage. Always emits a terminal "done" event.
    """
    py = _pick_python()
    names = list(brief.competencies)
    level = (brief.proficiency or "BASIC").upper()
    combo_dir = _combo_dir(runs_root, run_id)
    _stage = _make_stage_runner(combo_dir, emit)

    # Run 00_preflight + 01_input_files; return the located (comp, bg) JSON, or
    # None after emitting the failure. Shared by the fresh run and the
    # prepared-but-input-files-missing fallback.
    def _gen_input_files() -> tuple[Path, Path] | None:
        rec = _stage("00_preflight", [
            py, "-m", "flows.tech.stages.preflight",
            "--combo", f"{','.join(names)}:{level}", "--env", env,
        ])
        if rec["exit_code"] != 0:
            emit(StageEvent("done", "failed", detail="preflight failed"))
            return None
        t0 = time.time()
        input_cmd = [
            py, "-m", "flows.tech.stages.input_files",
            "--competency-name", ", ".join(names),
            "--proficiency", level, "--role", brief.role or "", "--env", env,
        ]
        if brief.domain:
            input_cmd += ["--domain", brief.domain]
        rec = _stage("01_input_files", input_cmd)
        if rec["exit_code"] != 0:
            emit(StageEvent("done", "failed", detail="input files failed"))
            return None
        return _locate_input_files(names, level, t0)

    try:
        combo_dir.mkdir(parents=True, exist_ok=True)

        if scenarios_prepared:
            # Reuse the pool + input files produced by the prepare phase.
            # since=0 → accept the existing on-disk input files regardless of age.
            try:
                comp_json, bg_json = _locate_input_files(names, level, 0.0)
            except FileNotFoundError:
                # Input files live on the container disk (data/generated/…) and
                # are wiped on redeploy, while the scenario pool persists in the
                # DB — so "prepared" can be True with the input files gone.
                # Regenerate them (not the pool) instead of failing at stage 03.
                located = _gen_input_files()
                if located is None:
                    return
                comp_json, bg_json = located
        else:
            located = _gen_input_files()
            if located is None:
                return
            comp_json, bg_json = located

            scenario_cmd = [
                py, "-m", "flows.tech.stages.scenarios",
                "--competency-file", str(comp_json), "--background-file", str(bg_json),
                "--count", str(brief.scenario_count), "--env", env, "--append",
            ]
            for area in brief.focus_areas:
                scenario_cmd += ["--focus-areas", area]
            if brief.domain:
                scenario_cmd += ["--domain", brief.domain]
            rec = _stage("02_scenarios", scenario_cmd)
            if rec["exit_code"] != 0:
                return emit(StageEvent("done", "failed", detail="scenario stage failed"))

        prompt_cmd = [
            py, "-m", "flows.tech.stages.prompts", "--name", ", ".join(names),
            "--proficiency", level, "--env", env, "--force", "--verbose",
        ]
        if instructions and instructions.strip():
            prompt_cmd += ["--instructions", instructions.strip()]
        rec = _stage("03_prompt", prompt_cmd)
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="prompt stage failed"))

        generate_cmd = [
            py, "-m", "flows.tech.stages.generate",
            "-c", str(comp_json), "-b", str(bg_json),
            "-s", str(scenarios_file_for(level)),
            "--env", env,
        ]
        if selected_scenario and selected_scenario.strip():
            scenario_path = combo_dir / "selected_scenario.txt"
            scenario_path.write_text(selected_scenario.strip(), encoding="utf-8")
            generate_cmd += ["--scenario-file", str(scenario_path)]
        rec = _stage("04_tasks", generate_cmd)
        outcome = _summarise_task_stage(Path(rec["stdout"]))
        if rec["exit_code"] != 0 or "REJECTED" in outcome or "ERROR" in outcome or "UNKNOWN" in outcome:
            return emit(StageEvent("done", "failed", detail=outcome, outcome=outcome))

        result = _extract_task_result(Path(rec["stdout"]))
        emit(StageEvent("done", "completed", detail=outcome, outcome=outcome,
                        task_id=result["task_id"], task_url=result["task_url"],
                        task_name=result["task_name"],
                        task_type=result["task_type"],
                        competencies=result["competencies"], env=env))
    except Exception as exc:  # noqa: BLE001 — surface any stage crash to the UI
        emit(StageEvent("done", "failed", detail=f"runner error: {exc}"))


# Back-compat alias — the original single-shot entry point (full five-stage run,
# no scenario selection). Retained so any external caller keeps working.
def run_pipeline_for_brief(brief: TaskBrief, *, run_id: str, emit: EmitFn,
                           env: str = "dev", runs_root: Path = RUNS_DIR,
                           instructions: str = "") -> None:
    run_generate_for_brief(brief, run_id=run_id, emit=emit, env=env,
                           runs_root=runs_root, instructions=instructions)
