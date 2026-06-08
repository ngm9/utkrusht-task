"""FastAPI app for Task Builder.

A4 + B2 refactor (2026-05-29):

* Conversations are persisted to Supabase (`conversations` table) instead of
  the in-memory ``SESSIONS`` dict — survives a process restart.
* Generation runs are recorded in the ``generation_jobs`` table and executed
  IN-PROCESS by a background daemon thread (``task_builder.jobs.enqueue_job``
  → ``task_builder.runner``). The heavyweight ``infra.jobs`` queue + external
  worker were retired in the 2026-06-04 consolidation; this is the lean path.
* The SSE endpoint polls the job row, which the in-process runner keeps
  current (stage / status / per-stage log tail).

The chat-bot turn logic, slot validation, and competency lookup remain
unchanged — those live in ``task_builder.conversation``.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from generators.input_files.generator import init_supabase as _init_competency_supabase
from task_builder.jobs import JobStatus, enqueue_job
from task_builder.conversation import apply_turn, build_bot_client
from task_builder.conversation_repo import (
    create_conversation,
    load_session,
    mark_submitted,
    save_session,
)
from task_builder.slots import SessionState, TaskBrief

logger = logging.getLogger("task_builder.server")

app = FastAPI(title="Task Builder")

_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

# v1 default env. Override per request via the body, or set
# TASK_BUILDER_ENV to flip the global default.
_DEFAULT_ENV = os.environ.get("TASK_BUILDER_ENV", "dev")

# Shared secret for proxied requests from the Next.js admin panel. When set,
# every /api/* request must carry a matching X-Internal-Token header. When
# unset (local dev), the check is bypassed — convenient for ``python -m
# task_builder`` against localhost but DO NOT deploy without the env var set.
_INTERNAL_TOKEN = os.environ.get("INTERNAL_PROXY_TOKEN", "").strip()

# Paths that bypass the internal-token check. Static + health are needed for
# container liveness probes and for the legacy static UI direct test path.
_PUBLIC_PATHS = ("/api/health", "/static", "/")


@app.middleware("http")
async def _enforce_internal_token(request: Request, call_next):
    """Reject /api/* requests lacking a valid X-Internal-Token header.

    The Next.js admin proxy stamps the header on every forwarded request;
    direct browser hits do not, so they 403. The check is opt-in via the
    INTERNAL_PROXY_TOKEN env var — leaving it empty (local dev) disables the
    middleware entirely so contributors can hit the UI directly.
    """
    if not _INTERNAL_TOKEN:
        return await call_next(request)

    path = request.url.path
    if any(path == p or path.startswith(p + "/") or path == "/" for p in _PUBLIC_PATHS):
        return await call_next(request)

    if not path.startswith("/api/"):
        return await call_next(request)

    provided = request.headers.get("x-internal-token") or ""
    if provided != _INTERNAL_TOKEN:
        return JSONResponse(
            status_code=403,
            content={"detail": "forbidden: missing or invalid X-Internal-Token"},
        )

    return await call_next(request)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


_GREETING = (
    "Hi! I'll help you put together a coding assessment. "
    "First — what tech stack should the candidate work in?"
)


def get_supabase() -> Any:
    """Supabase client for competency validation (dev env)."""
    return _init_competency_supabase(_DEFAULT_ENV)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/greeting")
def greeting() -> dict[str, str]:
    """Return the opening bot message without creating a conversation row.

    The UI calls this on mount so a stray page-load doesn't persist an
    empty session. Conversation creation is deferred to ``/api/session``,
    which the UI now calls lazily on the user's first submitted message.
    """
    return {"greeting": _GREETING}


@app.get("/api/conversations/{conversation_id}")
def conversation_detail(
    conversation_id: str,
    env: str = _DEFAULT_ENV,
    x_testmaker_id: str | None = Header(default=None, alias="X-Testmaker-Id"),
) -> dict[str, Any]:
    """Full conversation row including the messages transcript.

    The history list endpoint (``GET /api/history``) returns lightweight
    rows for the timeline; this fetches one with the full message log so
    the admin UI can re-render the chat. Also includes the most recent
    generation_job so the UI can decide whether to show "Resume" or "View".

    When ``X-Testmaker-Id`` is present, returns 404 if the conversation
    belongs to a different testmaker (scope guard).
    """
    from generators.task.persistence import init_supabase
    sb = init_supabase(env)

    rows = (
        sb.table("conversations")
        .select(
            "id,started_by,messages,brief,missing_slots,status,"
            "created_at,updated_at,submitted_at,abandoned_at",
        )
        .eq("id", conversation_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(status_code=404, detail="conversation not found")
    conv = rows[0]
    if x_testmaker_id and conv.get("started_by") and conv["started_by"] != x_testmaker_id:
        raise HTTPException(status_code=404, detail="conversation not found")

    jobs = (
        sb.table("generation_jobs")
        .select(
            "id,status,stage,env,error,result_task_id,"
            "started_at,finished_at,created_at",
        )
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    return {**conv, "jobs": jobs}


@app.get("/api/history")
def history(
    env: str = _DEFAULT_ENV,
    limit: int = 50,
    x_testmaker_id: str | None = Header(default=None, alias="X-Testmaker-Id"),
) -> dict[str, Any]:
    """List recent task-creation sessions for the calling testmaker.

    Joins ``conversations`` to their ``generation_jobs`` so the admin UI can
    render a single timeline: "this conversation produced these runs".

    When ``X-Testmaker-Id`` is forwarded by the Next.js proxy, results are
    scoped to that testmaker. Without the header (local dev / direct hit),
    returns the most recent ``limit`` conversations across all testmakers.
    """
    from generators.task.persistence import init_supabase
    sb = init_supabase(env)

    conv_q = (
        sb.table("conversations")
        .select(
            "id,started_by,brief,status,created_at,updated_at,submitted_at",
        )
        .order("created_at", desc=True)
        .limit(limit)
    )
    if x_testmaker_id:
        conv_q = conv_q.eq("started_by", x_testmaker_id)
    conversations = (conv_q.execute()).data or []

    if not conversations:
        return {"conversations": []}

    conv_ids = [c["id"] for c in conversations]
    jobs = (
        sb.table("generation_jobs")
        .select(
            "id,conversation_id,status,stage,env,error,result_task_id,"
            "started_at,finished_at,created_at,attempts",
        )
        .in_("conversation_id", conv_ids)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    jobs_by_conv: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        jobs_by_conv.setdefault(job["conversation_id"], []).append(job)

    out_conversations = []
    for conv in conversations:
        out_conversations.append({
            **conv,
            "jobs": jobs_by_conv.get(conv["id"], []),
        })

    return {"conversations": out_conversations}


@app.post("/api/session")
def create_session(
    env: str = _DEFAULT_ENV,
    x_testmaker_id: str | None = Header(default=None, alias="X-Testmaker-Id"),
) -> dict:
    """Start a conversation. Persists an active row in `conversations`.

    The Next.js admin proxy forwards the verified testmaker UUID via the
    ``X-Testmaker-Id`` header. Direct local hits send no header and the
    column stays NULL.
    """
    conversation_id = create_conversation(env=env, started_by=x_testmaker_id)
    return {"session_id": conversation_id, "reply": _GREETING}


@app.post("/api/chat")
def chat(req: ChatRequest, env: str = _DEFAULT_ENV) -> dict:
    """Run one conversation turn against the session's brief."""
    session = load_session(env, req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")

    result = apply_turn(
        session, req.message,
        client=build_bot_client(), supabase=get_supabase(),
    )
    save_session(env, session)
    return {
        "reply": result.reply,
        "brief": result.brief.model_dump(),
        "missing_slots": result.missing_slots,
        "ready": result.ready,
    }


class GenerateRequest(BaseModel):
    session_id: str
    env: str = "dev"


@app.post("/api/generate")
def generate(req: GenerateRequest) -> dict:
    """Enqueue a pipeline run for a session whose brief is complete.

    Returns the `job_id` (which becomes the SSE stream key). The actual
    work runs in an in-process background thread (task_builder.jobs) — this
    endpoint never blocks on the pipeline.
    """
    if req.env not in ("dev", "prod"):
        raise HTTPException(status_code=400, detail="env must be 'dev' or 'prod'")

    session = load_session(req.env, req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    if not session.brief.is_complete():
        raise HTTPException(status_code=400, detail="Brief is not complete")

    brief_payload = session.brief.model_dump()
    # Stash the competency names list separately for the orchestrator —
    # the input_files stage takes a comma-joined string.
    brief_payload["competency_names"] = brief_payload.get("competencies", [])
    brief_payload["proficiency"] = (brief_payload.get("proficiency") or "BASIC").upper()

    job_id = enqueue_job(
        brief=brief_payload, env=req.env,
        conversation_id=req.session_id,
    )
    mark_submitted(req.env, req.session_id)
    return {"run_id": job_id, "job_id": job_id}


_PIPELINE_STAGES = (
    "00_preflight",
    "01_input_files",
    "02_scenarios",
    "03_prompt",
    "04_tasks",
)


def _build_stage_progression(
    current_stage: str | None,
    overall_status: str,
) -> list[dict[str, Any]]:
    """Derive a per-stage status list from the job's overall + current cursor.

    The orchestrator runs the five stages in a fixed order and writes the
    label of whichever is in flight to ``generation_jobs.stage``. From that
    cursor + the row's ``status`` we can reconstruct a UI-ready checklist:

      * stages before the cursor → ``ok``    (already passed)
      * the cursor stage          → mirrors the overall status
        (``running`` while the job is running, ``failed`` if it died there)
      * stages after the cursor   → ``pending``

    Terminal states (``done`` / ``failed`` at the end) collapse the whole
    list to that state.
    """
    # Queue / never-claimed jobs: everything pending.
    if overall_status in ("queued",) or current_stage is None:
        return [{"label": s, "status": "pending"} for s in _PIPELINE_STAGES]

    # Fully done — every stage succeeded.
    if overall_status == "done":
        return [{"label": s, "status": "ok"} for s in _PIPELINE_STAGES]

    out: list[dict[str, Any]] = []
    cursor_passed = False
    for stage in _PIPELINE_STAGES:
        if stage == current_stage:
            # The current stage takes its status from the overall job state.
            ui_status = (
                "failed" if overall_status in ("failed", "cancelled") else "running"
            )
            out.append({"label": stage, "status": ui_status})
            cursor_passed = True
        elif not cursor_passed:
            out.append({"label": stage, "status": "ok"})
        else:
            out.append({"label": stage, "status": "pending"})
    return out


@app.get("/api/runs/{job_id}/state")
def run_state(
    job_id: str,
    env: str = _DEFAULT_ENV,
) -> dict[str, Any]:
    """One-shot JSON snapshot of a generation_jobs row, plus a derived
    per-stage progression list. Designed for polling clients (Vercel +
    edge-friendly) — counterpart to the SSE ``/api/runs/{id}/events``.

    Response shape:
      {
        "id": uuid,
        "status": "queued"|"running"|"done"|"failed"|"cancelled",
        "stage": "00_preflight"|... | null,
        "stages": [{"label": "00_preflight", "status": "ok"}, ...],
        "result_task_id": uuid | null,
        "error": str | null,
        "started_at": iso | null,
        "finished_at": iso | null,
        "attempts": int,
      }
    """
    from generators.task.persistence import init_supabase
    sb = init_supabase(env)
    rows = (
        sb.table("generation_jobs")
        .select(
            "id,status,stage,error,result_task_id,started_at,finished_at,"
            "attempts,stage_logs,stage_log_urls",
        )
        .eq("id", job_id)
        .limit(1)
        .execute()
    ).data or []
    if not rows:
        raise HTTPException(status_code=404, detail="job not found")
    row = rows[0]
    stage_logs = row.pop("stage_logs", None) or {}
    stage_log_urls = row.pop("stage_log_urls", None) or {}
    progression = _build_stage_progression(
        row.get("stage"), row.get("status") or ""
    )
    # Splice the log tail + S3 URL onto each stage entry so the UI only
    # deals with one list shape instead of parallel maps.
    for entry in progression:
        log = stage_logs.get(entry["label"])
        if log:
            entry["log"] = log
        log_url = stage_log_urls.get(entry["label"])
        if log_url:
            entry["log_url"] = log_url
    return {**row, "stages": progression}


@app.get("/api/runs/{job_id}/events")
async def run_events(job_id: str, env: str = _DEFAULT_ENV):
    """SSE stream of job state.

    Polls the ``generation_jobs`` row every 500ms; emits one event per
    stage change, plus a terminal event when status hits done/failed.
    """

    async def event_source():
        prev_stage: str | None = None
        prev_status: str | None = None

        while True:
            try:
                row = await asyncio.to_thread(_fetch_job_row, env, job_id)
            except Exception as exc:
                yield {"data": json.dumps({"stage": "done", "status": "failed", "detail": str(exc)})}
                break

            if row is None:
                yield {"data": json.dumps({"stage": "done", "status": "failed", "detail": "job not found"})}
                break

            stage = row.get("stage")
            status = row.get("status")
            if stage != prev_stage or status != prev_status:
                payload = {
                    "stage": stage or "queued",
                    "status": _ui_status(status),
                    "detail": row.get("error") or "",
                    "task_id": row.get("result_task_id"),
                }
                yield {"data": json.dumps(payload)}
                prev_stage = stage
                prev_status = status

            if status in (JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value):
                yield {"data": json.dumps({
                    "stage": "done",
                    "status": _ui_status(status),
                    "detail": row.get("error") or "",
                    "task_id": row.get("result_task_id"),
                })}
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_source())


def _ui_status(status: str | None) -> str:
    return {
        JobStatus.QUEUED.value: "queued",
        JobStatus.RUNNING.value: "running",
        JobStatus.DONE.value: "completed",
        JobStatus.FAILED.value: "failed",
        JobStatus.CANCELLED.value: "failed",
    }.get(status or "", "running")


def _fetch_job_row(env: str, job_id: str) -> dict[str, Any] | None:
    """Read a single job row. Lives outside the async generator so we can
    run it in a thread (Supabase client is sync).
    """
    from generators.task.persistence import init_supabase
    sb = init_supabase(env)
    result = (
        sb.table("generation_jobs")
        .select("status, stage, error, result_task_id")
        .eq("id", job_id)
        .single()
        .execute()
    )
    return result.data
