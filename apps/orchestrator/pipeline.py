"""In-process orchestrator (A2).

Runs the 5 pipeline stages as Python function calls inside a single
worker process. Each stage writes its stdout/stderr to a per-run log
file under the workspace, so the SSE log-tail in task_builder still
gets per-stage output.

Stages today use Click's ``standalone_mode=False`` invoke path for the
CLI-shaped engines and direct function calls for the task creator. As
each engine grows a clean Python entry point, the wrapper here will be
replaced with the bare function call.

This module is consumed by ``infra.jobs.worker`` (production path) and
can also be invoked from a CLI for local debugging — see
``apps.orchestrator.cli`` (TODO follow-up).
"""
from __future__ import annotations

import contextlib
import datetime as _dt
import io
import json
import logging
import shutil
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from infra.storage import s3 as storage_s3

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    label: str
    status: str            # "ok" | "failed" | "skipped"
    duration_s: float
    log_path: Path | None = None
    error: str | None = None
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    job_id: str | None
    status: str             # "ok" | "failed"
    workspace: Path
    stages: list[StageResult] = field(default_factory=list)
    task_id: str | None = None
    error: str | None = None

    @property
    def total_duration_s(self) -> float:
        return round(sum(s.duration_s for s in self.stages), 1)


# ---------------------------------------------------------------------------
# Stage adapters — each takes (brief, workspace, env, **kwargs)
# ---------------------------------------------------------------------------

def _capture_stdout_and_run(log_path: Path, fn: Callable[[], Any]) -> tuple[Any, str | None]:
    """Run ``fn``, capturing its stdout/stderr to ``log_path``.

    Returns ``(value, error)`` where ``error`` is None on success.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    err: str | None = None
    value: Any = None
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            value = fn()
        except SystemExit as exc:
            # Click commands exit 0 on success in standalone mode; we use
            # standalone_mode=False to avoid that, but defensively handle it.
            if exc.code not in (0, None):
                err = f"SystemExit({exc.code})"
        except Exception:
            err = traceback.format_exc()
    log_path.write_text(buf.getvalue(), encoding="utf-8")
    return value, err


def _stage_preflight(brief: dict[str, Any], workspace: Path, env: str) -> StageResult:
    label = "00_preflight"
    log_path = workspace / f"{label}.log"
    t0 = time.monotonic()

    def runner() -> int:
        # Lazy import — preflight loads heavy DSPy / supabase deps.
        from task_agent_preflight import run_combo_checks, run_global_checks

        global_report = run_global_checks()
        names = brief.get("competency_names") or []
        proficiency = (brief.get("proficiency") or "BASIC").upper()

        combo_report = None
        if names:
            combo_report = run_combo_checks(names, proficiency, env=env)

        if not global_report.passed:
            print(global_report.render())
            raise RuntimeError("preflight (global) blockers present — see log")
        if combo_report is not None and not combo_report.passed:
            print(combo_report.render())
            raise RuntimeError("preflight (combo) blockers present — see log")
        return 0

    _, err = _capture_stdout_and_run(log_path, runner)
    duration = round(time.monotonic() - t0, 2)
    return StageResult(
        label=label,
        status="failed" if err else "ok",
        duration_s=duration,
        log_path=log_path,
        error=err,
    )


def _resolve_input_file_paths(brief: dict[str, Any]) -> tuple[Path, Path]:
    """Compute the deterministic competency + background file paths the
    input_files generator will (or already did) write to. Mirrors the
    naming logic in ``generators.input_files.generator``.
    """
    from generators.input_files.generator import (
        BASE_DIR,
        resolve_output_folder,
        sanitize_folder_name,
    )

    names = brief.get("competency_names") or []
    level = (brief.get("proficiency") or "BASIC").lower()
    combined_slug = "_".join(n.lower() for n in names)
    tech_slug = sanitize_folder_name(combined_slug)
    output_dir = resolve_output_folder(tech_slug, level)
    tech_short = tech_slug.replace("input_", "", 1)
    comp_path = output_dir / f"competency_{tech_short}_{level}_Utkrusht.json"
    bg_path = output_dir / f"background_forQuestions_utkrusht_{tech_short}_{level}.json"
    # Touch BASE_DIR so static analysers know it's intentionally imported
    # (it shapes the path via resolve_output_folder above).
    _ = BASE_DIR
    return comp_path, bg_path


def _mirror_to_s3(
    brief: dict[str, Any],
    env: str,
    *,
    kind: str,
    local_path: Path,
) -> str | None:
    """Mirror a stage-produced file to S3 under task_builder/{job_id}/{kind}.

    Returns the public URL on success, None when:
    - storage isn't configured (dev without AWS creds)
    - the brief has no job_id (running outside the worker, e.g. local CLI)
    - the upload itself fails (logs a warning; never raises)

    Stage failures should not be caused by storage hiccups — task
    generation is the expensive bit and should still be usable for
    inspection even if mirroring is broken.
    """
    if not storage_s3.is_enabled():
        return None
    job_id = brief.get("__job_id")
    if not job_id:
        return None
    try:
        bucket = storage_s3.bucket_for(env)
        key = storage_s3.key_for_run(job_id, kind, ext=local_path.suffix.lstrip(".") or "json")
        if local_path.suffix == ".json":
            with local_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            url = storage_s3.upload_json(bucket, key, data)
        else:
            url = storage_s3.upload_text(bucket, key, local_path.read_text(encoding="utf-8"))
        return url
    except Exception as exc:  # noqa: BLE001
        logger.warning("s3 mirror failed kind=%s local=%s: %s", kind, local_path, exc)
        return None


def _stage_input_files(brief: dict[str, Any], workspace: Path, env: str) -> StageResult:
    label = "01_input_files"
    log_path = workspace / f"{label}.log"
    t0 = time.monotonic()

    # NB: generate_input_files only accepts competency-name / proficiency /
    # role / domain / folder-name / force / dry-run / env. focus_areas isn't
    # a CLI flag here — it threads through the brief into later stages
    # (scenarios + task creation).
    args = [
        "--competency-name", ", ".join(brief.get("competency_names") or []),
        "--proficiency", (brief.get("proficiency") or "BASIC").upper(),
        "--env", env,
    ]
    if brief.get("domain"):
        args += ["--domain", brief["domain"]]
    if brief.get("role"):
        args += ["--role", brief["role"]]

    def runner():
        from generators.input_files.generator import generate_input_files
        return generate_input_files.main(args=args, standalone_mode=False)

    _, err = _capture_stdout_and_run(log_path, runner)
    duration = round(time.monotonic() - t0, 2)

    # On success, stamp the produced file paths into the brief so the next
    # stages don't have to parse them out of stdout. The generator's path
    # convention is deterministic — we recompute it the same way it does.
    if not err:
        try:
            comp_path, bg_path = _resolve_input_file_paths(brief)
        except Exception as exc:
            err = f"path resolution after input_files: {exc}"
        else:
            if not comp_path.exists():
                err = f"input_files completed but competency file missing: {comp_path}"
            elif not bg_path.exists():
                err = f"input_files completed but background file missing: {bg_path}"
            else:
                brief["competency_file"] = str(comp_path)
                brief["background_file"] = str(bg_path)
                comp_url = _mirror_to_s3(brief, env, kind="competency", local_path=comp_path)
                bg_url = _mirror_to_s3(brief, env, kind="background", local_path=bg_path)
                if comp_url:
                    brief["competency_url"] = comp_url
                if bg_url:
                    brief["background_url"] = bg_url

    return StageResult(
        label=label, status="failed" if err else "ok",
        duration_s=duration, log_path=log_path, error=err,
    )


def _stage_scenarios(brief: dict[str, Any], workspace: Path, env: str) -> StageResult:
    label = "02_scenarios"
    log_path = workspace / f"{label}.log"
    t0 = time.monotonic()

    def runner():
        competency_path = brief.get("competency_file")
        background_path = brief.get("background_file")
        if not competency_path:
            raise RuntimeError(
                "brief missing competency_file — 01_input_files did not "
                "propagate its output paths"
            )

        args = [
            "--competency-file", str(competency_path),
            "--count", str(brief.get("scenario_count", 6)),
            "--env", env,
        ]
        if background_path:
            args += ["--background-file", str(background_path)]
        if brief.get("domain"):
            args += ["--domain", brief["domain"]]
        if brief.get("focus_areas"):
            for fa in brief["focus_areas"]:
                args += ["--focus-areas", fa]

        from generators.scenarios.__main__ import generate_scenarios_cli
        return generate_scenarios_cli.main(args=args, standalone_mode=False)

    _, err = _capture_stdout_and_run(log_path, runner)
    duration = round(time.monotonic() - t0, 2)

    if not err:
        # Scenarios are appended to a shared file determined by proficiency.
        try:
            from generators.scenarios.generator import get_target_scenario_file
            competencies = [
                {"name": n, "proficiency": (brief.get("proficiency") or "BASIC").upper()}
                for n in (brief.get("competency_names") or [])
            ]
            scenarios_path = get_target_scenario_file(competencies, is_non_code=False)
            brief["scenarios_file"] = str(scenarios_path)
            if scenarios_path.exists():
                scenarios_url = _mirror_to_s3(
                    brief, env, kind="scenarios", local_path=scenarios_path,
                )
                if scenarios_url:
                    brief["scenarios_url"] = scenarios_url
        except Exception as exc:
            err = f"scenarios path resolution: {exc}"

    return StageResult(
        label=label, status="failed" if err else "ok",
        duration_s=duration, log_path=log_path, error=err,
    )


def _stage_prompts(brief: dict[str, Any], workspace: Path, env: str) -> StageResult:
    label = "03_prompt"
    log_path = workspace / f"{label}.log"
    t0 = time.monotonic()

    args = [
        "--name", ", ".join(brief.get("competency_names") or []),
        "--proficiency", (brief.get("proficiency") or "BASIC").upper(),
        "--env", env, "--force",
    ]

    def runner():
        from generators.prompts.__main__ import cli as prompts_cli
        return prompts_cli.main(args=args, standalone_mode=False)

    _, err = _capture_stdout_and_run(log_path, runner)
    duration = round(time.monotonic() - t0, 2)
    return StageResult(
        label=label, status="failed" if err else "ok",
        duration_s=duration, log_path=log_path, error=err,
    )


def _stage_tasks(brief: dict[str, Any], workspace: Path, env: str) -> StageResult:
    label = "04_tasks"
    log_path = workspace / f"{label}.log"
    t0 = time.monotonic()

    competency_file = brief.get("competency_file")
    background_file = brief.get("background_file")
    scenarios_file = brief.get("scenarios_file")

    task_id: str | None = None

    def runner():
        nonlocal task_id
        from generators.task.creator import create_task
        result = create_task(
            competency_file=Path(competency_file),
            background_file=Path(background_file),
            scenarios_file=Path(scenarios_file) if scenarios_file else None,
            env=env,
        )
        task_id = result.get("task_id")
        print(f"Task ID: {task_id}")
        return result

    _, err = _capture_stdout_and_run(log_path, runner)
    duration = round(time.monotonic() - t0, 2)
    return StageResult(
        label=label,
        status="failed" if err else "ok",
        duration_s=duration,
        log_path=log_path,
        error=err,
        outputs={"task_id": task_id} if task_id else {},
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

STAGE_ORDER: list[tuple[str, Callable[[dict[str, Any], Path, str], StageResult]]] = [
    ("00_preflight",   _stage_preflight),
    ("01_input_files", _stage_input_files),
    ("02_scenarios",   _stage_scenarios),
    ("03_prompt",      _stage_prompts),
    ("04_tasks",       _stage_tasks),
]


class Orchestrator:
    """Runs the five pipeline stages in a single Python process."""

    def __init__(
        self,
        *,
        brief: dict[str, Any],
        workspace: Path | None = None,
        env: str = "dev",
        skip_preflight: bool = False,
        on_stage: Callable[[StageResult], None] | None = None,
    ) -> None:
        self.brief = brief
        self.env = env
        self.skip_preflight = skip_preflight
        self.on_stage = on_stage
        self.workspace = self._ensure_workspace(workspace)

    def _ensure_workspace(self, workspace: Path | None) -> Path:
        if workspace is not None:
            workspace.mkdir(parents=True, exist_ok=True)
            return workspace
        ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = Path(tempfile.gettempdir()) / "utkrusht-runs" / f"run-{ts}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def cleanup(self) -> None:
        """Best-effort delete the workspace. Worker calls this after the
        log bundle is shipped to object storage."""
        try:
            shutil.rmtree(self.workspace, ignore_errors=True)
        except Exception as exc:
            logger.warning("workspace cleanup failed %s: %s", self.workspace, exc)

    def run(self, *, job_id: str | None = None) -> PipelineResult:
        result = PipelineResult(job_id=job_id, status="ok", workspace=self.workspace)
        # Stash job_id in the brief so per-stage helpers (e.g. _mirror_to_s3)
        # can produce job-scoped object keys without a wider signature change.
        if job_id:
            self.brief["__job_id"] = job_id

        for label, stage_fn in STAGE_ORDER:
            if label == "00_preflight" and self.skip_preflight:
                continue
            stage_result = stage_fn(self.brief, self.workspace, self.env)
            result.stages.append(stage_result)
            if self.on_stage is not None:
                try:
                    self.on_stage(stage_result)
                except Exception as exc:
                    logger.warning("on_stage hook raised: %s", exc)
            if stage_result.status == "failed":
                result.status = "failed"
                result.error = f"{label}: {stage_result.error}"
                return result
            if label == "04_tasks":
                result.task_id = stage_result.outputs.get("task_id")

        return result


# ---------------------------------------------------------------------------
# Convenience for the B3 worker
# ---------------------------------------------------------------------------

def run_pipeline_for_job(
    *,
    job_id: str,
    brief: dict[str, Any],
    env: str = "dev",
    workspace: Path | None = None,
    on_stage: Callable[[StageResult], None] | None = None,
) -> PipelineResult:
    """Single-call entry point used by the jobs worker."""
    orch = Orchestrator(
        brief=brief, workspace=workspace, env=env, on_stage=on_stage,
    )
    return orch.run(job_id=job_id)
