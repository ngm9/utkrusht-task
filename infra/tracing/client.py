"""Traced OpenAI client wrapper — capture every LLM call's input + output.

``trace_client(client, provider=...)`` wraps a built ``openai.OpenAI`` so that
``.responses.create`` and ``.chat.completions.create`` emit a structured trace
record (request, response text, token usage, latency, errors) tagged with the
current run/stage context. The wrap is in-place on the SDK's cached resource
objects, so **call sites are unchanged** — callers keep using
``client.responses.create(...)`` exactly as before.

Hard guarantee: **tracing never breaks or alters the real call.** Capture is
wrapped in try/except around the genuine request; on any capture error the real
response (or the real exception) is returned/raised unchanged.
"""
from __future__ import annotations

import functools
import time
from typing import Any

from infra.logger_config import logger
from infra.tracing import context
from infra.tracing.sink import emit_llm_call

# Request kwargs worth keeping as the "prompt" side of a training pair.
_REQUEST_KEYS = (
    "model",
    "input",
    "messages",
    "instructions",
    "reasoning",
    "max_output_tokens",
    "max_tokens",
    "temperature",
    "top_p",
    "text",
    "response_format",
)


def trace_client(client: Any, *, provider: str) -> Any:
    """Wrap ``client.responses.create`` and ``client.chat.completions.create``
    in place for tracing. Idempotent; returns the same client.
    """
    try:
        _wrap(client.responses, "create", provider=provider, call_type="responses")
    except Exception as exc:  # noqa: BLE001 — never fail client construction
        logger.warning(f"[trace] could not wrap responses.create: {exc}")
    try:
        _wrap(
            client.chat.completions,
            "create",
            provider=provider,
            call_type="chat.completions",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"[trace] could not wrap chat.completions.create: {exc}")
    return client


def _wrap(resource: Any, name: str, *, provider: str, call_type: str) -> None:
    flag = f"_gx_traced_{name}"
    if getattr(resource, flag, False):
        return  # already wrapped (idempotent)
    orig = getattr(resource, name)

    @functools.wraps(orig)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0 = time.time()
        try:
            rec = _base_record(provider, call_type, kwargs)
        except Exception:  # noqa: BLE001 — capture must not break the call
            rec = None
        try:
            resp = orig(*args, **kwargs)
        except Exception as exc:
            if rec is not None:
                try:
                    rec["latency_ms"] = int((time.time() - t0) * 1000)
                    rec["status"] = "error"
                    rec["error"] = repr(exc)[:1000]
                    emit_llm_call(rec)
                except Exception:  # noqa: BLE001
                    pass
            raise
        if rec is not None:
            try:
                rec["latency_ms"] = int((time.time() - t0) * 1000)
                rec.update(_summarize_response(resp))
                emit_llm_call(rec)
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[trace] response capture failed: {exc}")
        return resp

    setattr(resource, name, wrapper)
    setattr(resource, flag, True)


def _base_record(provider: str, call_type: str, kwargs: dict) -> dict:
    return {
        "trace_id": context.new_trace_id(),
        "run_id": context.get_run_id(),
        "task_id": context.get_task_id(),
        "stage": context.get_stage(),
        "attempt": context.get_attempt(),
        "provider": provider,
        "call_type": call_type,
        "model": kwargs.get("model"),
        "request": {k: kwargs[k] for k in _REQUEST_KEYS if k in kwargs},
        "status": "ok",
        "schema_version": 1,
    }


def _summarize_response(resp: Any) -> dict:
    """Extract raw text + token usage from a Responses or Chat-Completions
    response, defensively (unknown shapes degrade to None, never raise)."""
    out: dict = {}
    text = getattr(resp, "output_text", None)
    if text is None:
        try:
            text = resp.choices[0].message.content
        except Exception:  # noqa: BLE001
            text = None
    finish = None
    try:
        finish = resp.choices[0].finish_reason
    except Exception:  # noqa: BLE001
        finish = getattr(resp, "status", None)
    out["response"] = {"raw_text": text, "finish_reason": finish}

    usage = getattr(resp, "usage", None)
    if usage is not None:
        out["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None)
            or getattr(usage, "prompt_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None)
            or getattr(usage, "completion_tokens", None),
        }
    return out
