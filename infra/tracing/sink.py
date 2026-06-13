"""Trace sink — append-only JSONL per run, failure-isolated + secret-redacting.

Writes to ``.task_agent_runs/run-<run_id>/traces/`` (``llm_calls.jsonl``,
``stages.jsonl``, ``manifest.json``). Co-located with the existing stage logs
so a run's traces sit next to its ``04_tasks.stderr`` etc.

Contract:
* **Never breaks the pipeline.** Every write is wrapped — a sink error logs a
  warning and returns; it never propagates.
* **Secret-redacting.** Secret-looking keys (api_key, authorization, token, …)
  are replaced with ``<REDACTED>`` before anything is persisted.
* **Opt-in.** No-op unless ``PIPELINE_TRACING_ENABLED`` is truthy, so importing
  / wiring the package can't change behavior until tracing is deliberately on.

Module-level functions (not a cached instance) so the destination follows the
current ``run_id`` from :mod:`infra.tracing.context`, and a process-wide lock
serializes appends across threads.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict

from infra.logger_config import logger

# infra/tracing/sink.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / ".task_agent_runs"

_LOCK = threading.Lock()

# Substrings that, if found in a (possibly nested) key, redact that value.
_REDACT_KEY_SUBSTRINGS = (
    "api_key",
    "apikey",
    "authorization",
    "x-api-key",
    "x-portkey-api-key",
    "secret",
    "password",
    "bearer",
    "credential",
)


def _is_secret_key(key: Any) -> bool:
    """True if a key name looks like it holds a secret. Matches singular
    ``token`` / ``*_token`` but NOT token *counts* (``input_tokens`` etc.)."""
    k = str(key).lower()
    if any(s in k for s in _REDACT_KEY_SUBSTRINGS):
        return True
    # "token" (singular secret) but never "...tokens" (usage counts).
    return "token" in k and "tokens" not in k


def tracing_enabled() -> bool:
    """True when ``PIPELINE_TRACING_ENABLED`` is a truthy env value."""
    return os.getenv("PIPELINE_TRACING_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def redact(obj: Any) -> Any:
    """Recursively replace secret-looking values with ``<REDACTED>``."""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if _is_secret_key(k):
                out[k] = "<REDACTED>"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [redact(v) for v in obj]
    return obj


def trace_dir(run_id: str | None = None) -> Path:
    """Resolve the traces directory for the current (or given) run.

    ``TRACE_DIR`` env overrides the location wholesale — **test-only**; it is a
    flat path with no per-run suffix, so concurrent runs would share files.
    Production relies on the default ``run-<run_id>/traces`` layout.
    """
    override = os.getenv("TRACE_DIR")
    if override:
        return Path(override)
    if run_id is None:
        from infra.tracing import context

        run_id = context.get_run_id()
    return RUNS_DIR / f"run-{run_id or 'adhoc'}" / "traces"


def _append(filename: str, record: Dict[str, Any]) -> None:
    if not tracing_enabled():
        return
    try:
        d = trace_dir()
        d.mkdir(parents=True, exist_ok=True)
        line = json.dumps(redact(record), ensure_ascii=False, default=str)
        with _LOCK:
            with open(d / filename, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except Exception as exc:  # noqa: BLE001 — tracing must never break the run
        logger.warning(f"[trace] sink write failed ({filename}): {exc}")


def emit_llm_call(record: Dict[str, Any]) -> None:
    """Append one LLM-call trace record to ``llm_calls.jsonl``."""
    _append("llm_calls.jsonl", record)


def emit_stage(record: Dict[str, Any]) -> None:
    """Append one stage-span record to ``stages.jsonl``."""
    _append("stages.jsonl", record)


def write_manifest(manifest: Dict[str, Any], run_id: str | None = None) -> None:
    """Write the per-run ``manifest.json`` (overwrites)."""
    if not tracing_enabled():
        return
    try:
        d = trace_dir(run_id)
        d.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(redact(manifest), ensure_ascii=False, indent=2, default=str)
        # ``"w"`` truncates — hold the lock so a concurrent append/write can't
        # interleave with the truncate.
        with _LOCK:
            with open(d / "manifest.json", "w", encoding="utf-8") as fh:
                fh.write(payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"[trace] manifest write failed: {exc}")
