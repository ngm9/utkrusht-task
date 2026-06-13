"""litellm callback that captures DSPy / litellm completions into the trace sink.

The prompt generator (`generators/prompts/agent.py`) runs through **DSPy**, which
calls **litellm** under the hood — NOT the OpenAI SDK that
:func:`infra.tracing.client.trace_client` wraps. So those LLM calls are invisible
to the client wrapper. Registering this litellm ``CustomLogger`` makes litellm
emit the SAME ``emit_llm_call`` record shape (model / messages / output / usage /
latency), tagged with the current run/stage context.

Idempotent (registers once), opt-in (no-op unless ``PIPELINE_TRACING_ENABLED``),
and failure-isolated (a capture error logs a warning, never breaks the call).
``litellm`` is imported lazily so this module has no hard dependency on it.
"""
from __future__ import annotations

from typing import Any

from infra.logger_config import logger
from infra.tracing import context
from infra.tracing.sink import emit_llm_call, tracing_enabled

_REGISTERED = False


def _emit(kwargs: dict, response_obj: Any, start_time, end_time, status: str,
          error: Any = None) -> None:
    """Build + emit one trace record from a litellm callback payload."""
    try:
        model = kwargs.get("model")
        messages = kwargs.get("messages")
        text = None
        try:
            text = response_obj.choices[0].message.content
        except Exception:  # noqa: BLE001
            text = None
        rec = {
            "trace_id": context.new_trace_id(),
            "run_id": context.get_run_id(),
            "task_id": context.get_task_id(),
            "stage": context.get_stage(),
            "attempt": context.get_attempt(),
            "provider": "litellm",
            "call_type": "litellm.completion",
            "model": model,
            "request": {"model": model, "messages": messages},
            "response": {"raw_text": text},
            "status": status,
            "schema_version": 1,
        }
        usage = getattr(response_obj, "usage", None)
        if usage is not None:
            rec["usage"] = {
                "input_tokens": getattr(usage, "prompt_tokens", None),
                "output_tokens": getattr(usage, "completion_tokens", None),
            }
        try:
            if start_time is not None and end_time is not None:
                rec["latency_ms"] = int((end_time - start_time).total_seconds() * 1000)
        except Exception:  # noqa: BLE001
            pass
        if error is not None:
            rec["error"] = str(error)[:1000]
        emit_llm_call(rec)
    except Exception as exc:  # noqa: BLE001 — capture must never break the call
        logger.warning(f"[trace] litellm capture failed: {exc}")


def register_litellm_tracing() -> None:
    """Register the litellm tracing callback once. No-op when tracing is disabled
    or already registered; failures are swallowed (never break prompt-gen)."""
    global _REGISTERED
    if _REGISTERED or not tracing_enabled():
        return
    try:
        import litellm
        from litellm.integrations.custom_logger import CustomLogger

        class _TracingLogger(CustomLogger):
            def log_success_event(self, kwargs, response_obj, start_time, end_time):
                _emit(kwargs, response_obj, start_time, end_time, "ok")

            def log_failure_event(self, kwargs, response_obj, start_time, end_time):
                _emit(kwargs, response_obj, start_time, end_time, "error",
                      kwargs.get("exception"))

            async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
                _emit(kwargs, response_obj, start_time, end_time, "ok")

            async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
                _emit(kwargs, response_obj, start_time, end_time, "error",
                      kwargs.get("exception"))

        existing = list(getattr(litellm, "callbacks", None) or [])
        litellm.callbacks = existing + [_TracingLogger()]
        _REGISTERED = True
        logger.info("[trace] litellm tracing callback registered")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"[trace] could not register litellm tracing: {exc}")
