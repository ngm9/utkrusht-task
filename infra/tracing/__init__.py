"""Pipeline tracing — structured capture of every stage + LLM call for
observability and future training-data.

See ``docs/plans/2026-06-11-pipeline-tracing.md``. Opt-in via
``PIPELINE_TRACING_ENABLED``; S3 upload opt-in via ``TRACE_S3_BUCKET``.

Typical wiring:

    from infra.tracing import trace_client, trace_run, trace_stage

    client = trace_client(openai.OpenAI(...), provider="openai")  # at build
    with trace_run(run_id), trace_stage("classifier"):
        client.chat.completions.create(...)   # auto-captured
"""
from infra.tracing.client import trace_client
from infra.tracing.context import (
    get_attempt,
    get_run_id,
    get_stage,
    get_task_id,
    new_trace_id,
    set_attempt,
    set_stage,
    set_task_id,
    trace_attempt,
    trace_run,
    trace_stage,
)
from infra.tracing.sink import (
    emit_llm_call,
    emit_stage,
    redact,
    trace_dir,
    tracing_enabled,
    write_manifest,
)
from infra.tracing.s3 import upload_run_logs, upload_run_traces
from infra.tracing.litellm_hook import register_litellm_tracing

__all__ = [
    "trace_client",
    "trace_run",
    "trace_stage",
    "trace_attempt",
    "set_attempt",
    "set_stage",
    "set_task_id",
    "get_run_id",
    "get_task_id",
    "get_stage",
    "get_attempt",
    "new_trace_id",
    "emit_llm_call",
    "emit_stage",
    "write_manifest",
    "trace_dir",
    "tracing_enabled",
    "redact",
    "upload_run_traces",
    "upload_run_logs",
    "register_litellm_tracing",
]
