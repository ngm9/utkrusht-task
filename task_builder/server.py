"""FastAPI app for Task Builder — chat and pipeline-generation routes."""
from __future__ import annotations

import asyncio
import dataclasses
import json
import queue
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from generators.input_files.generator import init_supabase
from task_builder.conversation import apply_turn, build_bot_client
from task_builder.runner import StageEvent, run_pipeline_for_brief
from task_builder.slots import SessionState, TaskBrief

app = FastAPI(title="Task Builder")

_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


# In-memory session store — lost on restart (acceptable for a local single-user tool).
SESSIONS: dict[str, SessionState] = {}

# In-memory run registry: run_id -> a thread-safe event queue.
# Entries are not evicted — fine for a local single-user tool.
RUNS: dict[str, "queue.Queue[StageEvent]"] = {}


def _launch_run(run_id: str, brief: TaskBrief, env: str = "dev") -> None:
    """Start the pipeline in a worker thread; events land on RUNS[run_id]."""
    q: "queue.Queue[StageEvent]" = queue.Queue()
    RUNS[run_id] = q
    threading.Thread(
        target=run_pipeline_for_brief,
        args=(brief,),
        kwargs={"run_id": run_id, "emit": q.put, "env": env},
        daemon=True,
    ).start()


_GREETING = ("Hi! I'll help you put together a coding assessment. "
             "First — what tech stack should the candidate work in?")


def get_supabase() -> Any:
    """Supabase client for competency validation (dev environment)."""
    return init_supabase("dev")


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/session")
def create_session() -> dict:
    """Start a conversation; returns a session id and the bot's opening line."""
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = SessionState(session_id=session_id)
    return {"session_id": session_id, "reply": _GREETING}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    """Run one conversation turn against the session's brief."""
    session = SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")

    result = apply_turn(session, req.message,
                        client=build_bot_client(), supabase=get_supabase())
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
    """Kick off a pipeline run for a session whose brief is complete."""
    session = SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    if not session.brief.is_complete():
        raise HTTPException(status_code=400, detail="Brief is not complete")
    if req.env not in ("dev", "prod"):
        raise HTTPException(status_code=400, detail="env must be 'dev' or 'prod'")

    run_id = uuid.uuid4().hex
    _launch_run(run_id, session.brief, req.env)
    return {"run_id": run_id}


@app.get("/api/runs/{run_id}/events")
async def run_events(run_id: str):
    """Server-Sent Events stream of StageEvents for a run."""
    q = RUNS.get(run_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Unknown run")

    async def event_source():
        loop = asyncio.get_running_loop()
        while True:
            event: StageEvent = await loop.run_in_executor(None, q.get)
            yield {"data": json.dumps(dataclasses.asdict(event))}
            if event.stage == "done":
                break
        RUNS.pop(run_id, None)

    return EventSourceResponse(event_source())
