"""Supabase-backed CRUD for the ``generation_jobs`` queue.

The supabase-py client doesn't expose SELECT ... FOR UPDATE SKIP LOCKED
directly, so the claim step uses a small RPC-style pattern: a single UPDATE
that targets the oldest queued row by ``id`` and flips it to ``running``
in one round-trip.

The UPDATE itself takes a row-level lock; SKIP LOCKED semantics are
emulated by combining the WHERE on ``status='queued'`` with the unique
``id`` returned by the inner SELECT. If two workers race, only one
UPDATE matches; the other returns 0 rows and the worker tries again.
"""
from __future__ import annotations

import datetime as _dt
import logging
import socket
import os
from typing import Any

from generators.task.persistence import init_supabase
from infra.jobs.models import GenerationJob, JobStatus

logger = logging.getLogger(__name__)


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _worker_tag() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


def enqueue_job(
    *,
    brief: dict[str, Any],
    env: str = "dev",
    conversation_id: str | None = None,
    max_attempts: int = 1,
) -> str:
    """Insert a new ``queued`` job. Returns the new ``id``."""
    sb = init_supabase(env)
    payload: dict[str, Any] = {
        "brief": brief,
        "env": env,
        "status": JobStatus.QUEUED.value,
        "max_attempts": max_attempts,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    result = sb.table("generation_jobs").insert(payload).execute()
    if not result.data:
        raise RuntimeError("enqueue_job: Supabase returned no row")
    return str(result.data[0]["id"])


def claim_next_job(env: str = "dev") -> GenerationJob | None:
    """Atomically claim the next queued job.

    Strategy: SELECT the oldest queued row id, then UPDATE … WHERE
    id = <id> AND status = 'queued'. The WHERE clause is the race guard —
    a competing worker that also picked that id will fail its UPDATE
    (0 rows affected) because status is no longer 'queued'.

    Returns ``None`` when the queue is empty or another worker won the race.
    """
    sb = init_supabase(env)

    candidates = (
        sb.table("generation_jobs")
        .select("id")
        .eq("status", JobStatus.QUEUED.value)
        .order("created_at")
        .limit(1)
        .execute()
    )
    rows = candidates.data or []
    if not rows:
        return None
    job_id = rows[0]["id"]

    claim = (
        sb.table("generation_jobs")
        .update({
            "status": JobStatus.RUNNING.value,
            "locked_by": _worker_tag(),
            "locked_at": _now(),
            "started_at": _now(),
            "attempts": rows[0].get("attempts", 0) + 1,
        })
        .eq("id", job_id)
        .eq("status", JobStatus.QUEUED.value)
        .execute()
    )
    if not claim.data:
        logger.debug("claim race lost for job_id=%s", job_id)
        return None

    # Re-fetch the full row so the caller has everything (incl. brief).
    full = (
        sb.table("generation_jobs")
        .select("*")
        .eq("id", job_id)
        .single()
        .execute()
    )
    if not full.data:
        return None
    return GenerationJob.from_row(full.data)


def update_stage(
    job_id: str,
    stage: str,
    *,
    env: str = "dev",
    workspace_path: str | None = None,
) -> None:
    """Patch the live ``stage`` cursor."""
    update: dict[str, Any] = {"stage": stage}
    if workspace_path is not None:
        update["workspace_path"] = workspace_path
    sb = init_supabase(env)
    sb.table("generation_jobs").update(update).eq("id", job_id).execute()


def append_stage_log(
    job_id: str,
    stage: str,
    log_text: str,
    *,
    env: str = "dev",
    max_bytes: int = 4096,
) -> None:
    """Persist the tail of one stage's stdout onto the job row.

    Bytes are capped per stage so total payload stays under PostgREST's
    practical jsonb update size. We tail (last N bytes) — the start of the
    log is the boilerplate; the tail is what's diagnostic.
    """
    if not log_text:
        return
    text = log_text[-max_bytes:] if len(log_text) > max_bytes else log_text
    sb = init_supabase(env)
    # Read-modify-write: PostgREST doesn't support jsonb_set in updates, so
    # we pull the current value, splice the key, and write the whole map.
    row = (
        sb.table("generation_jobs")
        .select("stage_logs")
        .eq("id", job_id)
        .limit(1)
        .execute()
    ).data or [{}]
    logs: dict[str, Any] = (row[0] or {}).get("stage_logs") or {}
    logs[stage] = text
    sb.table("generation_jobs").update({"stage_logs": logs}).eq("id", job_id).execute()


def update_brief(job_id: str, brief: dict[str, Any], *, env: str = "dev") -> None:
    """Overwrite the row's ``brief`` jsonb with the post-run snapshot.

    The orchestrator mutates ``brief`` in-place to stamp produced file
    paths and S3 URLs onto it (``competency_url``, ``background_url``,
    ``scenarios_url``); persisting it back makes those URLs available
    to anyone reading the row later (admin UI, downstream jobs, audits).
    """
    payload = {k: v for k, v in brief.items() if not k.startswith("__")}
    sb = init_supabase(env)
    sb.table("generation_jobs").update({"brief": payload}).eq("id", job_id).execute()


def update_stage_log_urls(
    job_id: str, urls: dict[str, str], *, env: str = "dev",
) -> None:
    """Persist per-stage full-log S3 URLs.

    Replaces (does not merge) the map. The worker calls this once at
    job termination with the full set of stages it uploaded.
    """
    if not urls:
        return
    sb = init_supabase(env)
    sb.table("generation_jobs").update({"stage_log_urls": urls}).eq("id", job_id).execute()


def mark_done(
    job_id: str,
    *,
    env: str = "dev",
    result_task_id: str | None = None,
    log_url: str | None = None,
) -> None:
    """Flip the row to ``done``."""
    update: dict[str, Any] = {
        "status": JobStatus.DONE.value,
        "finished_at": _now(),
        "stage": "done",
    }
    if result_task_id:
        update["result_task_id"] = result_task_id
    if log_url:
        update["log_url"] = log_url
    sb = init_supabase(env)
    sb.table("generation_jobs").update(update).eq("id", job_id).execute()


def mark_failed(
    job_id: str,
    *,
    env: str = "dev",
    error: str,
    log_url: str | None = None,
) -> None:
    """Flip the row to ``failed`` with a short error message."""
    update: dict[str, Any] = {
        "status": JobStatus.FAILED.value,
        "finished_at": _now(),
        "error": (error or "")[:2000],
    }
    if log_url:
        update["log_url"] = log_url
    sb = init_supabase(env)
    sb.table("generation_jobs").update(update).eq("id", job_id).execute()


def requeue_stuck_jobs(
    env: str = "dev",
    *,
    stuck_after_minutes: int = 30,
) -> int:
    """Watchdog — return rows stuck in ``running`` to ``queued`` (or fail
    them if ``attempts`` already hit ``max_attempts``).

    Returns the number of rows updated. Intended to be called on a timer
    (every 5 min) by the worker or a separate cron.
    """
    sb = init_supabase(env)
    cutoff = (
        _dt.datetime.now(_dt.timezone.utc)
        - _dt.timedelta(minutes=stuck_after_minutes)
    ).isoformat()

    stuck = (
        sb.table("generation_jobs")
        .select("id, attempts, max_attempts")
        .eq("status", JobStatus.RUNNING.value)
        .lte("locked_at", cutoff)
        .execute()
    )
    rows = stuck.data or []
    updated = 0
    for row in rows:
        attempts = int(row.get("attempts") or 0)
        max_attempts = int(row.get("max_attempts") or 1)
        if attempts >= max_attempts:
            patch = {
                "status": JobStatus.FAILED.value,
                "finished_at": _now(),
                "error": "watchdog: stuck in running > threshold",
            }
        else:
            patch = {
                "status": JobStatus.QUEUED.value,
                "locked_by": None,
                "locked_at": None,
            }
        sb.table("generation_jobs").update(patch).eq("id", row["id"]).execute()
        updated += 1
    if updated:
        logger.warning("requeue_stuck_jobs: updated %d stuck rows", updated)
    return updated
