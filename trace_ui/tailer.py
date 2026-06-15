"""trace_ui.tailer — safe run-dir helpers + an async file tailer.

The pipeline (``run_pipeline.py``) writes each run under
``.task_agent_runs/run-<UTC-ts>/`` with:

* a combo subdir (e.g. ``python_redis_intermediate/``) holding the per-stage
  ``NN_<name>.{stdout,stderr,timing.json}`` logs, the stage-4 sub-logs
  ``04_tasks.evals.log`` / ``04_tasks.e2b_gate.log``, and ``summary.json``.
* a ``traces/`` subdir holding append-only JSONL: ``llm_calls.jsonl`` (one
  captured LLM call per line), ``stages.jsonl`` (one stage outcome per line),
  and optionally ``manifest.json``.

This module gives the server three things:

1. :func:`list_runs` — enumerate runs for the run-picker.
2. :func:`resolve_run_dir` — turn an untrusted ``run_id`` into a real path,
   rejecting traversal / absolute paths / anything escaping ``RUNS_DIR``.
3. :func:`tail_file` / :func:`tail_jsonl` — async generators that follow a
   file as it is appended to (``tail -f`` semantics) by polling offsets.

Everything here is filesystem-only and import-safe (no network, no DB), so it
is straightforward to unit-test by monkeypatching :data:`RUNS_DIR`.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import AsyncIterator, Optional

# ----------------------------------------------------------------------
# Locations
# ----------------------------------------------------------------------

# Repo root is two parents up from this file (trace_ui/tailer.py -> repo/).
REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / ".task_agent_runs"

# Only these characters are allowed in a run_id. Note: this deliberately
# excludes "/" and whitespace, so "../foo", "/etc/passwd", and "a b" are all
# rejected before we ever touch the filesystem. Timestamps use ":" in some
# environments, hence it is included.
_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")

# The UTC timestamp embedded in a ``run-<YYYYMMDDTHHMMSSZ>`` dir name. Used to
# order runs chronologically without trusting dir mtime (which churns whenever a
# file is added to an old run dir — e.g. an S3 log backfill — and would float a
# stale run to the top). Fixed-width ISO-basic, so lexicographic == chronological.
_RUN_TS_RE = re.compile(r"\d{8}T\d{6}Z$")

# How often the tailer re-checks a file for new bytes.
_POLL_INTERVAL_S = 0.25


class RunNotFoundError(Exception):
    """Raised when a run_id does not resolve to an existing run dir."""


class InvalidRunIdError(ValueError):
    """Raised when a run_id is malformed or attempts path traversal."""


# ----------------------------------------------------------------------
# Run-dir resolution (security boundary)
# ----------------------------------------------------------------------

def resolve_run_dir(run_id: str) -> Path:
    """Resolve ``run_id`` to its run directory under :data:`RUNS_DIR`.

    The ``run_id`` is the directory name (e.g. ``run-20260612T040014Z`` or the
    bare ``20260612T040014Z`` timestamp). This is a security boundary: the
    server passes untrusted input here, so we:

    1. reject anything not matching ``^[A-Za-z0-9_.:-]+$`` (no slashes, no
       ``..``, no absolute paths, no whitespace);
    2. resolve the candidate and confirm it is *strictly inside* RUNS_DIR;
    3. confirm the directory exists.

    Raises :class:`InvalidRunIdError` on a malformed / traversing id and
    :class:`RunNotFoundError` when the (valid) id has no directory.
    """
    if not isinstance(run_id, str) or not run_id:
        raise InvalidRunIdError("run_id must be a non-empty string")
    if not _RUN_ID_RE.match(run_id):
        raise InvalidRunIdError(f"run_id contains illegal characters: {run_id!r}")
    # Belt-and-braces: even though the regex blocks them, an absolute path or a
    # ".." segment must never reach the filesystem.
    if os.path.isabs(run_id) or ".." in run_id.split("/"):
        raise InvalidRunIdError(f"run_id is not a bare directory name: {run_id!r}")

    runs_dir = RUNS_DIR.resolve()
    candidate = (runs_dir / run_id).resolve()

    # Confirm the resolved path is contained within RUNS_DIR. is_relative_to is
    # 3.9+; fall back to commonpath for safety.
    try:
        contained = candidate.is_relative_to(runs_dir)  # type: ignore[attr-defined]
    except AttributeError:  # pragma: no cover - py<3.9
        contained = os.path.commonpath([str(candidate), str(runs_dir)]) == str(runs_dir)
    if not contained or candidate == runs_dir:
        raise InvalidRunIdError(f"run_id escapes the runs directory: {run_id!r}")

    if not candidate.is_dir():
        raise RunNotFoundError(f"no run directory for run_id {run_id!r}")
    return candidate


def _combo_dir(run_dir: Path) -> Optional[Path]:
    """Return the single combo subdir inside a run dir, if there is one.

    A run dir holds one combo subdir (e.g. ``python_redis_intermediate``)
    alongside the ``traces`` dir. We pick the first non-``traces`` subdirectory.
    """
    for child in sorted(run_dir.iterdir()):
        if child.is_dir() and child.name != "traces":
            return child
    return None


def _read_json(path: Path) -> Optional[dict]:
    """Best-effort JSON read; returns None on missing / malformed file."""
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return None


# ----------------------------------------------------------------------
# Listing runs
# ----------------------------------------------------------------------

def list_runs() -> list[dict]:
    """Enumerate runs under :data:`RUNS_DIR`, newest first.

    Scans ``run-*`` directories. For each:

    * ``run_id``    — the directory name.
    * ``combo``     — the combo subdir name (the tech/level slug), or None.
    * ``status``    — ``summary.json['status']`` if present, else ``"running"``.
    * ``started``   — directory mtime as an epoch float (cheap, monotonicish).
    * ``task_id`` / ``task_name`` — from ``traces/manifest.json`` if present.

    Returns ``[]`` if the runs dir does not exist. Never raises on a single
    malformed run dir — it is skipped gracefully.
    """
    runs_dir = RUNS_DIR
    if not runs_dir.is_dir():
        return []

    out: list[dict] = []
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir() or not run_dir.name.startswith("run-"):
            continue
        try:
            entry = _describe_run(run_dir)
        except Exception:  # noqa: BLE001 - one bad dir must not break the list
            continue
        out.append(entry)

    # Newest first. Primary key is the timestamp embedded in the run name (immune
    # to dir-mtime churn); runs whose id is not a ``run-<timestamp>`` fall back to
    # mtime via an empty primary key. See _run_sort_key.
    out.sort(key=_run_sort_key, reverse=True)
    return out


def _run_sort_key(entry: dict) -> tuple[str, float]:
    """Newest-first sort key: ``(embedded_timestamp_or_empty, dir_mtime)``.

    Prefers the UTC timestamp in the ``run-<YYYYMMDDTHHMMSSZ>`` name so that
    re-touching an old run dir (e.g. an S3 log backfill bumping its mtime)
    can't float a stale run above a newer one. Non-timestamp ids (e.g. a uuid
    fallback) get an empty primary key and are ordered by mtime instead.
    """
    name = entry["run_id"]
    ts = name[4:] if name.startswith("run-") else name
    return (ts if _RUN_TS_RE.match(ts) else "", entry["started"])


def _describe_run(run_dir: Path) -> dict:
    combo = _combo_dir(run_dir)
    combo_name = combo.name if combo is not None else None

    status = "running"
    if combo is not None:
        summary = _read_json(combo / "summary.json")
        if summary and summary.get("status"):
            status = str(summary["status"])

    task_id = None
    task_name = None
    manifest = _read_json(run_dir / "traces" / "manifest.json")
    if manifest:
        task_id = manifest.get("task_id")
        task_name = manifest.get("task_name")

    try:
        started = run_dir.stat().st_mtime
    except OSError:
        started = 0.0

    return {
        "run_id": run_dir.name,
        "combo": combo_name,
        "status": status,
        "started": started,
        "task_id": task_id,
        "task_name": task_name,
    }


# ----------------------------------------------------------------------
# Async tailing
# ----------------------------------------------------------------------

async def tail_file(
    path: Path,
    from_start: bool = True,
    poll_interval: float = _POLL_INTERVAL_S,
    start_offset: Optional[int] = None,
) -> AsyncIterator[str]:
    """Async generator yielding text lines as they are appended to ``path``.

    Semantics are like ``tail -F``: it tolerates the file not existing yet
    (waiting for it to appear), then follows appends forever, polling every
    ``poll_interval`` seconds.

    * ``from_start=True``  — yield existing content first, then new lines.
    * ``from_start=False`` — skip to EOF, yield only lines appended afterwards.
    * ``start_offset=N``   — begin following at byte ``N`` (overrides
      ``from_start``). Used to resume after an ordered catch-up read so no line
      is duplicated or dropped at the handoff.

    Each yielded value is a single line WITHOUT its trailing newline. A partial
    last line (not yet newline-terminated) is buffered and only emitted once its
    newline arrives, so consumers never see a half-written line.

    The generator runs until the consumer stops iterating (e.g. the SSE client
    disconnects and the task is cancelled). File reads are offloaded to a thread
    so the event loop is never blocked.
    """
    offset = 0
    buffer = ""
    started = False  # have we positioned the initial offset yet?

    while True:
        exists = await asyncio.to_thread(path.exists)
        if not exists:
            # File not created yet — wait for it to appear.
            await asyncio.sleep(poll_interval)
            continue

        if not started:
            if start_offset is not None:
                offset = start_offset
            elif not from_start:
                try:
                    offset = await asyncio.to_thread(lambda: path.stat().st_size)
                except OSError:
                    offset = 0
            started = True

        chunk, new_offset = await asyncio.to_thread(_read_from, path, offset)
        if new_offset < offset:
            # File was truncated/rotated — restart from the top.
            offset = 0
            buffer = ""
            continue
        offset = new_offset

        if chunk:
            buffer += chunk
            # Split out every complete line; keep the trailing partial in buffer.
            *lines, buffer = buffer.split("\n")
            for line in lines:
                yield line
        else:
            await asyncio.sleep(poll_interval)


def _read_from(path: Path, offset: int) -> tuple[str, int]:
    """Read new bytes from ``offset`` to EOF; return (decoded_text, new_offset).

    Runs in a worker thread. Decodes as UTF-8 with replacement so a partial
    multibyte sequence at the boundary never raises (worst case: a replacement
    char that the next poll corrects — acceptable for a log viewer).
    """
    try:
        size = path.stat().st_size
    except OSError:
        return "", offset
    if size <= offset:
        return "", size
    with path.open("rb") as fh:
        fh.seek(offset)
        data = fh.read()
    return data.decode("utf-8", errors="replace"), offset + len(data)


async def tail_jsonl(
    path: Path,
    from_start: bool = True,
    poll_interval: float = _POLL_INTERVAL_S,
) -> AsyncIterator[dict]:
    """Async generator yielding parsed dict records from an append-only JSONL.

    Wraps :func:`tail_file` and ``json.loads`` each complete line. Blank lines
    and lines that fail to parse (e.g. a half-flushed record the writer is still
    completing) are skipped silently — the next poll will pick up the rewritten
    line. Only ``dict`` records are yielded.
    """
    async for line in tail_file(path, from_start=from_start, poll_interval=poll_interval):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict):
            yield record
