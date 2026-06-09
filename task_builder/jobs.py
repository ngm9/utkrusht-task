"""In-process job execution for the Task Builder.

Lean replacement for the removed ``infra.jobs`` queue + external worker
(dropped in the 2026-06-04 consolidation). A generation run is still recorded
as a row in the ``generation_jobs`` table (which survives), but instead of being
claimed by a separate ``python -m infra.jobs.worker`` process it runs in a
background daemon **thread** inside the FastAPI process via
``task_builder.runner``. No S3, no metrics, no cross-process queue.

The server's SSE / state endpoints poll the ``generation_jobs`` row exactly as
before, so they need no change — this module just keeps that row up to date as
the pipeline progresses.

Concurrency is capped (``_MAX_CONCURRENT_JOBS``) so a burst of clicks can't
exhaust threads / subprocess slots; excess runs land in ``failed`` immediately.
"""
from __future__ import annotations

import datetime
import enum
import logging
import threading
import time
import uuid
from typing import Any, Dict, Optional

from generators.task.persistence import init_supabase
from task_builder.runner import StageEvent, run_pipeline_for_brief
from task_builder.slots import TaskBrief

logger = logging.getLogger("task_builder.jobs")

# Cap on how much per-stage log we persist into generation_jobs.stage_logs so a
# chatty stage can't bloat the row.
_STAGE_LOG_CAP = 8000
# Most one process should run at once (each run spawns subprocess + LLM chains).
_MAX_CONCURRENT_JOBS = 3
_JOB_SEMAPHORE = threading.BoundedSemaphore(_MAX_CONCURRENT_JOBS)
# Debounce stage-log writes: flush when a chunk is large OR enough time passed,
# instead of one Supabase round-trip per log line.
_LOG_FLUSH_BYTES = 600
_LOG_FLUSH_INTERVAL_S = 2.0


class JobStatus(enum.Enum):
    """Lifecycle of a generation run — values match the server's ``_ui_status``
    mapping."""

    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def enqueue_job(*, brief: Dict[str, Any], env: str, conversation_id: Optional[str]) -> str:
    """Record a generation run and start it in a background thread.

    Inserts the row as ``queued`` (the thread flips it to ``running`` once it
    claims a slot), then starts the daemon thread. Returns the ``job_id``
    immediately — the SSE stream key.
    """
    sb = init_supabase(env)
    inserted = (
        sb.table("generation_jobs")
        .insert({
            "conversation_id": conversation_id,
            "brief": brief,
            "status": JobStatus.QUEUED.value,
            "stage": "00_preflight",
            "env": env,
            "attempts": 1,
            "max_attempts": 1,
        })
        .execute()
    ).data
    job_id = str(inserted[0]["id"])

    # Reuse the same client in the worker thread (the request thread is done
    # with it after the insert) — avoids leaking a second HTTP session.
    thread = threading.Thread(
        target=_run_job,
        args=(job_id, _brief_from_payload(brief), env, sb),
        daemon=True,
        name=f"taskbuilder-job-{job_id[:8]}",
    )
    try:
        thread.start()
    except RuntimeError as exc:  # interpreter shutting down / OS thread limit
        _safe_update(sb, job_id, {
            "status": JobStatus.FAILED.value,
            "error": f"could not start run: {exc}",
            "finished_at": _now(),
        }, retries=2)
        raise
    logger.info("enqueue_job: started in-process run job_id=%s env=%s", job_id, env)
    return job_id


def _brief_from_payload(brief: Dict[str, Any]) -> TaskBrief:
    """Rebuild a ``TaskBrief`` from the server's serialized brief payload."""
    names = brief.get("competency_names") or brief.get("competencies") or []
    if not names:
        raise ValueError("brief must contain at least one competency name")
    return TaskBrief(
        competencies=list(names),
        proficiency=(brief.get("proficiency") or "BASIC").upper(),
        role=brief.get("role") or "",
        domain=brief.get("domain"),
        focus_areas=list(brief.get("focus_areas") or []),
        scenario_count=int(brief.get("scenario_count") or 6),
    )


def _safe_update(sb, job_id: str, update: Dict[str, Any], *, retries: int = 0) -> bool:
    """Best-effort ``generation_jobs`` patch. Returns True on success. ``retries``
    extra attempts for writes whose loss would strand the row (terminal/crash)."""
    update = {**update, "updated_at": _now()}
    last_exc: Optional[Exception] = None
    for _ in range(retries + 1):
        try:
            sb.table("generation_jobs").update(update).eq("id", job_id).execute()
            return True
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    logger.warning("job %s: progress write failed: %s", job_id, last_exc)
    return False


def _run_job(job_id: str, brief: TaskBrief, env: str, sb) -> None:
    """Background worker: run the five-stage pipeline, mirroring each
    ``StageEvent`` onto the ``generation_jobs`` row. Concurrency-capped and
    crash-safe — the row always reaches a terminal state."""
    if not _JOB_SEMAPHORE.acquire(blocking=False):
        _safe_update(sb, job_id, {
            "status": JobStatus.FAILED.value,
            "error": f"server busy: max {_MAX_CONCURRENT_JOBS} concurrent runs reached",
            "finished_at": _now(),
        }, retries=1)
        return

    stage_logs: Dict[str, str] = {}
    last_flush = time.monotonic()
    _safe_update(sb, job_id, {"status": JobStatus.RUNNING.value, "started_at": _now()})

    def emit(ev: StageEvent) -> None:
        nonlocal last_flush
        if ev.status == "log":
            stage_logs[ev.stage] = (stage_logs.get(ev.stage, "") + ev.detail)[-_STAGE_LOG_CAP:]
            now = time.monotonic()
            if len(ev.detail) >= _LOG_FLUSH_BYTES or (now - last_flush) >= _LOG_FLUSH_INTERVAL_S:
                _safe_update(sb, job_id, {"stage_logs": stage_logs})
                last_flush = now
            return
        if ev.stage != "done":
            _safe_update(sb, job_id, {
                "stage": ev.stage, "status": JobStatus.RUNNING.value,
                "stage_logs": stage_logs,
            })
            return
        # Terminal event — retry, since a lost write strands the row in 'running'.
        update: Dict[str, Any] = {"finished_at": _now(), "stage_logs": stage_logs}
        if ev.status == "completed":
            update["status"] = JobStatus.DONE.value
            task_id = _as_uuid(ev.task_id)
            if task_id:
                update["result_task_id"] = task_id
        else:
            update["status"] = JobStatus.FAILED.value
            update["error"] = ev.detail or "pipeline failed"
        if not _safe_update(sb, job_id, update, retries=2):
            logger.error("job %s: TERMINAL write failed — row may be stuck in 'running'", job_id)

    try:
        run_pipeline_for_brief(brief, run_id=job_id, emit=emit, env=env)
    except Exception as exc:  # noqa: BLE001 — never let a daemon thread die silently
        logger.exception("job %s: runner crashed", job_id)
        _safe_update(sb, job_id, {
            "status": JobStatus.FAILED.value,
            "error": f"runner crashed: {exc}",
            "finished_at": _now(),
        }, retries=2)
    finally:
        _JOB_SEMAPHORE.release()


def _as_uuid(value: Optional[str]) -> Optional[str]:
    """Return ``value`` only if it is a valid UUID — ``generation_jobs.result_task_id``
    is a uuid FK, so a non-uuid (e.g. a truncated log line) must not be written."""
    if not value:
        return None
    try:
        return str(uuid.UUID(str(value).strip()))
    except (ValueError, AttributeError):
        return None
