"""Run / stage context for pipeline tracing, carried via ``contextvars``.

Threads ``run_id`` / ``task_id`` / ``stage`` / ``attempt`` through the call
stack so the traced LLM-client wrapper (``infra.tracing.client``) can tag every
captured call with WHERE in the pipeline it happened — without plumbing those
values through every function signature.

Contextvars (not globals) so the tagging survives nested scopes cleanly and
propagates to ``asyncio`` tasks (which inherit a copy of the current context).

NOTE: contextvars do NOT auto-propagate into ``threading.Thread`` workers — a
new thread starts with an empty context, so an LLM call made there would be
tagged ``run_id=None``. If the wiring step ever runs a stage in a worker
thread, copy the context explicitly:
``ctx = contextvars.copy_context(); threading.Thread(target=lambda: ctx.run(fn))``.
The phase-1 task-gen pipeline is synchronous, so this does not apply yet.
"""
from __future__ import annotations

import contextlib
import contextvars
import time
import uuid
from typing import Iterator, Optional

_run_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_run_id", default=None
)
_task_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_task_id", default=None
)
_stage: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_stage", default=None
)
_attempt: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "trace_attempt", default=None
)


def new_trace_id() -> str:
    """A fresh per-call trace id (uuid4 hex)."""
    return uuid.uuid4().hex


def get_run_id() -> Optional[str]:
    return _run_id.get()


def get_task_id() -> Optional[str]:
    return _task_id.get()


def get_stage() -> Optional[str]:
    return _stage.get()


def get_attempt() -> Optional[int]:
    return _attempt.get()


def set_task_id(task_id: Optional[str]) -> None:
    """Set the current task id (e.g. once the draft row is inserted).

    Intended to be called *within* an active :func:`trace_run`, which restores
    the prior value on exit; a bare call outside one leaks the value.
    """
    _task_id.set(task_id)


def set_stage(stage: Optional[str]) -> None:
    """Imperatively set the current stage tag (no span/duration record).

    Lighter than :func:`trace_stage` — use when wrapping a region in a ``with``
    block is awkward and you only need subsequent LLM-call records tagged with
    the stage. Overwritten by the next ``set_stage``; reset on ``trace_run`` exit
    is NOT automatic, so prefer :func:`trace_stage` when you want a clean span.
    """
    _stage.set(stage)


def set_attempt(n: Optional[int]) -> None:
    """Imperatively set the current generation-attempt number (plain setter,
    like :func:`set_task_id`). For a scoped span use :func:`trace_attempt`."""
    _attempt.set(n)


@contextlib.contextmanager
def trace_run(run_id: str, *, task_id: Optional[str] = None) -> Iterator[None]:
    """Bind a ``run_id`` (and optional ``task_id``) for the duration of a run."""
    rtok = _run_id.set(run_id)
    ttok = _task_id.set(task_id) if task_id is not None else None
    try:
        yield
    finally:
        _run_id.reset(rtok)
        if ttok is not None:
            _task_id.reset(ttok)


@contextlib.contextmanager
def trace_attempt(n: Optional[int]) -> Iterator[None]:
    """Bind the current generation-attempt number (for the retry loop).

    A context manager (like :func:`trace_run` / :func:`trace_stage`) — use with
    ``with trace_attempt(2): ...``. A bare call without ``with`` is a no-op.
    """
    tok = _attempt.set(n)
    try:
        yield
    finally:
        _attempt.reset(tok)


@contextlib.contextmanager
def trace_stage(stage: str) -> Iterator[None]:
    """Mark a pipeline stage span. Emits a ``stages.jsonl`` record on exit with
    status (ok/error) + duration. Re-raises any exception unchanged — the span
    is observability only and never alters control flow.
    """
    tok = _stage.set(stage)
    t0 = time.time()
    status = "ok"
    err: Optional[str] = None
    try:
        yield
    except Exception as exc:  # noqa: BLE001 — record then re-raise, don't swallow
        status = "error"
        err = repr(exc)[:500]
        raise
    finally:
        _stage.reset(tok)
        record = {
            "run_id": _run_id.get(),
            "task_id": _task_id.get(),
            "stage": stage,
            "status": status,
            "duration_ms": int((time.time() - t0) * 1000),
            "error": err,
        }
        # Emit is best-effort; importing here avoids an import cycle and a
        # sink failure must never turn a successful stage into a crash.
        try:
            from infra.tracing.sink import emit_stage

            emit_stage(record)
        except Exception:  # noqa: BLE001
            pass
