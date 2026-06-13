"""trace_ui.server — FastAPI app for the LIVE trace/log viewer.

Endpoints:

* ``GET /``                              — the single static index.html page.
* ``GET /api/runs``                      — JSON list of runs (run-picker).
* ``GET /api/runs/{run_id}/stream/logs`` — SSE; tails every ``*.stdout`` /
  ``*.stderr`` / ``*.log`` in the combo dir concurrently. Each event payload is
  ``{stage, stream, line}`` (stage derived from the filename, stream one of
  ``stdout`` / ``stderr`` / ``log``).
* ``GET /api/runs/{run_id}/stream/traces`` — SSE; tails ``traces/llm_calls.jsonl``
  (``{kind:'llm_call', record}``) and ``traces/stages.jsonl``
  (``{kind:'stage', record}``).

SSE is implemented with a plain FastAPI ``StreamingResponse`` (no sse-starlette
dependency). A heartbeat comment (``:\n\n``) is emitted every ~15s so idle
connections survive proxy timeouts. ``run_id`` is validated through
``tailer.resolve_run_dir``; a malformed id returns HTTP 400.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from trace_ui import tailer
from trace_ui.tailer import (
    InvalidRunIdError,
    RunNotFoundError,
    resolve_run_dir,
    tail_file,
    tail_jsonl,
)

# So /api/competencies has Supabase creds and a spawned pipeline inherits the env.
load_dotenv()

app = FastAPI(title="trace_ui")

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_REPO_ROOT = Path(__file__).resolve().parent.parent

# SSE media type + headers that keep proxies from buffering / caching the
# stream. ``X-Accel-Buffering: no`` disables nginx response buffering.
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

_HEARTBEAT_INTERVAL_S = 15.0

# Which log files in the combo dir we follow. We classify each by its suffix.
_LOG_GLOBS = ("*.stdout", "*.stderr", "*.log")


# ----------------------------------------------------------------------
# Static page + runs list
# ----------------------------------------------------------------------

@app.get("/")
def index() -> FileResponse:
    """Serve the single-page UI."""
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/api/runs")
def api_runs() -> JSONResponse:
    """Return the list of runs for the picker (newest first)."""
    return JSONResponse(tailer.list_runs())


# Links a completed run produces, scraped from the task-gen logs.
_GIST_RE = re.compile(r"https://gist\.github\.com/[A-Za-z0-9_./-]+")
_REPO_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_TASKID_RE = re.compile(
    r"Task ID:\s*([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)


def _read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — missing/partial file → no data
        return None


def _compute_cost(run_dir: Path) -> Optional[dict]:
    """Per-stage + overall cost for the Result panel. Delegates to the shared
    infra.tracing.cost module so the pipeline log + the UI use one pricing
    table (no drift)."""
    from infra.tracing.cost import compute_cost

    return compute_cost(run_dir / "traces")


def _parse_result(run_dir: Path) -> dict:
    """Assemble a run's result: manifest (task id/name/outcome/env) + combo
    summary (status/outcome/duration) + links scraped from the 04_tasks logs
    (gist + GitHub repos). Best-effort; missing pieces are simply omitted."""
    manifest = _read_json(run_dir / "traces" / "manifest.json") or {}
    combo = _combo_dir(run_dir)
    summary = (_read_json(combo / "summary.json") if combo else None) or {}

    links: list[dict] = []
    seen: set[str] = set()
    task_id = manifest.get("task_id")

    def _add(label: str, url: str) -> None:
        url = url.rstrip(".,)")
        if url not in seen:
            seen.add(url)
            links.append({"label": label, "url": url})

    if combo is not None:
        for p in sorted(combo.glob("04_tasks.*")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in _GIST_RE.finditer(text):
                _add("Gist", m.group(0))
            for m in _REPO_RE.finditer(text):
                url = m.group(0).rstrip(".,)")
                label = "Solution repo" if url.endswith(("-solution", "_solution")) else "GitHub repo"
                _add(label, url)
            if not task_id:
                tm = _TASKID_RE.search(text)
                if tm:
                    task_id = tm.group(1)

    return {
        "run_id": run_dir.name,
        "task_id": task_id,
        "task_name": manifest.get("task_name"),
        "outcome": manifest.get("outcome"),
        "competencies": manifest.get("competencies") or summary.get("competencies"),
        "proficiency": summary.get("proficiency"),
        "env": manifest.get("env"),
        "status": summary.get("status"),
        "task_outcome": summary.get("task_outcome"),
        "duration_s": summary.get("total_duration_s"),
        "links": links,
        "cost": _compute_cost(run_dir),
    }


@app.get("/api/runs/{run_id}/result")
def api_result(run_id: str) -> JSONResponse:
    """Run-level result summary for the UI's Result panel."""
    run_dir = _resolve_or_400(run_id)
    return JSONResponse(_parse_result(run_dir))


# ----------------------------------------------------------------------
# Launcher: list competencies + start a new pipeline run
# ----------------------------------------------------------------------

_PROFICIENCIES = ("BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED")


def _supabase_creds(env: str) -> tuple[Optional[str], Optional[str]]:
    if env == "prod":
        return (os.getenv("SUPABASE_URL_APTITUDETESTS"),
                os.getenv("SUPABASE_API_KEY_APTITUDETESTS"))
    return (os.getenv("SUPABASE_URL_APTITUDETESTSDEV"),
            os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV"))


def _list_competencies(env: str) -> list[dict]:
    """Distinct (name, proficiency) pairs from the competencies table, sorted.
    supabase is imported lazily so the server has no hard dependency on it."""
    from supabase import create_client

    url, key = _supabase_creds(env)
    if not url or not key:
        raise RuntimeError(f"Missing Supabase credentials for env={env} (check .env)")
    client = create_client(url, key)
    res = client.table("competencies").select("name, proficiency").execute()
    seen: set = set()
    out: list[dict] = []
    for r in (res.data or []):
        name = (r.get("name") or "").strip()
        prof = (r.get("proficiency") or "").strip()
        if not name or (name, prof) in seen:
            continue
        seen.add((name, prof))
        out.append({"name": name, "proficiency": prof})
    out.sort(key=lambda r: (r["name"].lower(), r["proficiency"]))
    return out


@app.get("/api/competencies")
def api_competencies(env: str = "dev") -> JSONResponse:
    """List competencies (name + proficiency) for the New-run modal."""
    if env not in ("dev", "prod"):
        raise HTTPException(status_code=400, detail="env must be 'dev' or 'prod'")
    try:
        return JSONResponse({"competencies": _list_competencies(env)})
    except Exception as exc:  # noqa: BLE001 — soft error so the modal can show why
        return JSONResponse({"competencies": [], "error": str(exc)}, status_code=503)


class RunRequest(BaseModel):
    names: list[str]
    proficiency: str
    count: int = 2
    env: str = "dev"


def _spawn_pipeline(cmd: list[str]) -> None:
    """Launch run_pipeline.py detached. It writes its own logs to
    .task_agent_runs, which the run-list poll then surfaces."""
    subprocess.Popen(  # noqa: S603 — argv list (no shell), validated inputs
        cmd,
        cwd=str(_REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


@app.post("/api/runs")
def api_launch(req: RunRequest) -> JSONResponse:
    """Start a new pipeline run. Inputs are validated and passed as argv (never
    a shell string), so this localhost-only endpoint can't be used for injection."""
    names = [n.strip() for n in (req.names or []) if n and n.strip()]
    prof = (req.proficiency or "").upper()
    env = req.env if req.env in ("dev", "prod") else "dev"
    if not names:
        raise HTTPException(status_code=400, detail="at least one competency name is required")
    if prof not in _PROFICIENCIES:
        raise HTTPException(status_code=400, detail=f"proficiency must be one of {list(_PROFICIENCIES)}")
    if any(any(ord(ch) < 32 for ch in n) for n in names):
        raise HTTPException(status_code=400, detail="competency name contains invalid characters")
    count = req.count if isinstance(req.count, int) and 1 <= req.count <= 20 else 2

    cmd = [sys.executable, "run_pipeline.py", "-p", prof, "--env", env, "--count", str(count)]
    for n in names:
        cmd += ["-n", n]
    try:
        _spawn_pipeline(cmd)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"failed to launch pipeline: {exc}") from exc
    return JSONResponse({"ok": True, "names": names, "proficiency": prof, "env": env, "count": count})


def _resolve_or_400(run_id: str) -> Path:
    """Resolve a run_id, mapping tailer errors onto HTTP 400/404."""
    try:
        return resolve_run_dir(run_id)
    except InvalidRunIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RunNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _stage_from_filename(name: str) -> str:
    """Derive a stage label from a log filename.

    ``04_tasks.stdout`` -> ``04_tasks``; ``04_tasks.evals.log`` -> ``04_tasks``
    (the leading dotted component, i.e. everything before the first dot).
    """
    return name.split(".", 1)[0]


def _stream_kind(name: str) -> str:
    """Classify a log filename into ``stdout`` / ``stderr`` / ``log``."""
    if name.endswith(".stdout"):
        return "stdout"
    if name.endswith(".stderr"):
        return "stderr"
    return "log"


def _combo_dir(run_dir: Path) -> Path | None:
    for child in sorted(run_dir.iterdir()):
        if child.is_dir() and child.name != "traces":
            return child
    return None


def _sse(payload: dict) -> str:
    """Format a dict as a single SSE ``data:`` event frame."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _merge_to_queue(
    agen: AsyncIterator,
    queue: asyncio.Queue,
    wrap,
) -> None:
    """Drain an async generator into ``queue``, wrapping each item via ``wrap``.

    Runs as a background task per source so many files can be followed
    concurrently and interleaved into one SSE stream. Cancellation (client
    disconnect) propagates cleanly through the generator.
    """
    try:
        async for item in agen:
            await queue.put(wrap(item))
    except asyncio.CancelledError:  # graceful shutdown on disconnect
        raise
    except Exception:  # noqa: BLE001 - never let one source kill the stream
        return


async def _multiplex(sources: list[tuple[AsyncIterator, object]]) -> AsyncIterator[str]:
    """Interleave many tail sources into one heartbeat-keepalive SSE stream.

    ``sources`` is a list of ``(async_generator, wrap_callable)``. Each source
    is pumped by its own task into a shared queue; we yield queued frames as
    they arrive and inject a ``:\\n\\n`` heartbeat comment whenever the stream is
    idle for ``_HEARTBEAT_INTERVAL_S`` seconds.
    """
    queue: asyncio.Queue = asyncio.Queue()
    tasks = [
        asyncio.create_task(_merge_to_queue(agen, queue, wrap))
        for agen, wrap in sources
    ]
    try:
        # Open the stream immediately so the client's onopen fires.
        yield ":\n\n"
        while True:
            try:
                frame = await asyncio.wait_for(queue.get(), timeout=_HEARTBEAT_INTERVAL_S)
            except asyncio.TimeoutError:
                yield ":\n\n"  # heartbeat comment
                continue
            yield frame
    finally:
        for task in tasks:
            task.cancel()
        # Allow cancellations to settle without raising back into the response.
        await asyncio.gather(*tasks, return_exceptions=True)


# ----------------------------------------------------------------------
# SSE: logs
# ----------------------------------------------------------------------

def _log_files_in_order(combo: Path) -> list[Path]:
    """Every stdout/stderr/log file in the combo dir, sorted by name so they
    fall into pipeline-stage order (the ``00_``/``01_``/``02_``… prefix), with a
    stage's streams grouped together. Sorting the NAME is what gives step-wise
    order — globbing per-suffix would group by extension instead."""
    files: dict[str, Path] = {}
    for pattern in _LOG_GLOBS:
        for p in combo.glob(pattern):
            files[p.name] = p
    return [files[name] for name in sorted(files)]


def _read_complete_lines(path: Path, offset: int = 0) -> tuple[list[str], int]:
    """Read newline-terminated lines from ``offset``. Returns
    ``(lines, new_offset)`` where ``new_offset`` is just past the last complete
    line — a trailing partial line is left for the follow phase to pick up."""
    try:
        with path.open("rb") as fh:
            fh.seek(offset)
            data = fh.read()
    except OSError:
        return [], offset
    nl = data.rfind(b"\n")
    if nl == -1:
        return [], offset  # nothing newline-terminated yet
    complete = data[: nl + 1]
    text = complete.decode("utf-8", errors="replace")
    return text.split("\n")[:-1], offset + len(complete)


async def _ordered_log_stream(files: list[Path]) -> AsyncIterator[str]:
    """Ordered catch-up (stage order) then a live multiplexed follow.

    Phase 1 emits each file's existing lines IN STAGE ORDER, so a finished run
    reads top-to-bottom in pipeline order — fixing the cross-stage interleaving
    you'd get from following every file concurrently from the start. Phase 2
    follows lines appended after the snapshot, resuming from each file's exact
    end offset so the handoff drops/duplicates nothing.
    """
    yield ":\n\n"  # open immediately so the client's onopen fires
    follow: list[tuple[AsyncIterator, object]] = []
    for path in files:
        wrap = _make_log_wrap(_stage_from_filename(path.name), _stream_kind(path.name))
        lines, end = await asyncio.to_thread(_read_complete_lines, path, 0)
        for ln in lines:
            yield wrap(ln)
        follow.append((tail_file(path, start_offset=end), wrap))
    async for frame in _multiplex(follow):
        yield frame


@app.get("/api/runs/{run_id}/stream/logs")
def stream_logs(run_id: str) -> StreamingResponse:
    """SSE stream of every stdout/stderr/log line in the combo dir, replayed in
    pipeline-stage order then followed live."""
    run_dir = _resolve_or_400(run_id)
    combo = _combo_dir(run_dir)
    files = _log_files_in_order(combo) if combo is not None else []
    return StreamingResponse(
        _ordered_log_stream(files),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


def _make_log_wrap(stage: str, stream: str):
    """Build a closure wrapping a raw log line into an SSE frame.

    Bound as a factory so each file's ``stage``/``stream`` is captured by value
    (avoids the classic late-binding loop-variable bug).
    """
    def wrap(line: str) -> str:
        return _sse({"stage": stage, "stream": stream, "line": line})

    return wrap


# ----------------------------------------------------------------------
# SSE: traces
# ----------------------------------------------------------------------

@app.get("/api/runs/{run_id}/stream/traces")
def stream_traces(run_id: str) -> StreamingResponse:
    """SSE stream of LLM-call + stage trace records."""
    run_dir = _resolve_or_400(run_id)
    traces_dir = run_dir / "traces"

    def wrap_llm(record: dict) -> str:
        return _sse({"kind": "llm_call", "record": record})

    def wrap_stage(record: dict) -> str:
        return _sse({"kind": "stage", "record": record})

    sources: list[tuple[AsyncIterator, object]] = [
        (tail_jsonl(traces_dir / "llm_calls.jsonl", from_start=True), wrap_llm),
        (tail_jsonl(traces_dir / "stages.jsonl", from_start=True), wrap_stage),
    ]
    return StreamingResponse(
        _multiplex(sources),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )
