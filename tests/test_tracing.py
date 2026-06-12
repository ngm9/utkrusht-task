"""Unit tests for infra.tracing — the pipeline tracing / training-data capture.

Pins the load-bearing contract:
* The traced client is **transparent**: it returns the real response / re-raises
  the real exception, and a sink failure NEVER breaks the call.
* Every captured record carries run/stage context + request + response + usage.
* Tracing is **opt-in** (PIPELINE_TRACING_ENABLED) and **secret-redacting**.
* S3 upload is a no-op without a bucket.
"""
from __future__ import annotations

import json
import types

import pytest

from infra.tracing import (
    emit_llm_call,
    redact,
    trace_client,
    trace_run,
    trace_stage,
    upload_run_traces,
)
import infra.tracing.client as client_mod


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


class _Usage:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class _RespAPI:
    """Mimics an OpenAI Responses-API response."""

    def __init__(self, text, usage=None, status="completed"):
        self.output_text = text
        self.usage = usage
        self.status = status


class _ChatAPI:
    """Mimics a Chat-Completions response."""

    def __init__(self, content, prompt_tokens=3, completion_tokens=7):
        self.choices = [
            types.SimpleNamespace(
                message=types.SimpleNamespace(content=content),
                finish_reason="stop",
            )
        ]
        self.usage = _Usage(
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
        )


def _fake_client(responses_create=None, chat_create=None):
    """An object shaped like openai.OpenAI for the two traced call paths."""
    return types.SimpleNamespace(
        responses=types.SimpleNamespace(create=responses_create or (lambda **k: None)),
        chat=types.SimpleNamespace(
            completions=types.SimpleNamespace(create=chat_create or (lambda **k: None))
        ),
    )


def _read_jsonl(path):
    return [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]


@pytest.fixture
def tracing_on(monkeypatch, tmp_path):
    monkeypatch.setenv("PIPELINE_TRACING_ENABLED", "1")
    monkeypatch.setenv("TRACE_DIR", str(tmp_path))
    return tmp_path


# --------------------------------------------------------------------------
# redaction
# --------------------------------------------------------------------------


def test_redact_strips_secret_keys_recursively():
    out = redact(
        {
            "api_key": "sk-secret",
            "nested": {"Authorization": "Bearer x", "ok": 1},
            "list": [{"token": "t"}, {"keep": "v"}],
            "model": "gpt-x",
        }
    )
    assert out["api_key"] == "<REDACTED>"
    assert out["nested"]["Authorization"] == "<REDACTED>"
    assert out["nested"]["ok"] == 1
    assert out["list"][0]["token"] == "<REDACTED>"
    assert out["list"][1]["keep"] == "v"
    assert out["model"] == "gpt-x"  # non-secret prompt data preserved


# --------------------------------------------------------------------------
# opt-in gating
# --------------------------------------------------------------------------


def test_sink_is_noop_when_disabled(monkeypatch, tmp_path):
    monkeypatch.delenv("PIPELINE_TRACING_ENABLED", raising=False)
    monkeypatch.setenv("TRACE_DIR", str(tmp_path))
    emit_llm_call({"x": 1})
    assert not (tmp_path / "llm_calls.jsonl").exists()


# --------------------------------------------------------------------------
# responses-api capture
# --------------------------------------------------------------------------


def test_traced_responses_capture(tracing_on):
    tmp = tracing_on
    c = _fake_client(
        responses_create=lambda **k: _RespAPI("hello out", _Usage(input_tokens=10, output_tokens=5))
    )
    trace_client(c, provider="openai")
    with trace_run("run-A", task_id="task-1"), trace_stage("task_gen"):
        out = c.responses.create(
            model="gpt-x",
            input=[{"role": "user", "content": "hi"}],
            reasoning={"effort": "low"},
        )
    assert out.output_text == "hello out"  # transparent passthrough

    (rec,) = _read_jsonl(tmp / "llm_calls.jsonl")
    assert rec["provider"] == "openai" and rec["call_type"] == "responses"
    assert rec["run_id"] == "run-A" and rec["task_id"] == "task-1"
    assert rec["stage"] == "task_gen" and rec["model"] == "gpt-x"
    assert rec["request"]["reasoning"] == {"effort": "low"}
    assert rec["request"]["input"] == [{"role": "user", "content": "hi"}]
    assert rec["response"]["raw_text"] == "hello out"
    assert rec["usage"] == {"input_tokens": 10, "output_tokens": 5}
    assert rec["status"] == "ok" and isinstance(rec["latency_ms"], int)
    assert rec["trace_id"] and rec["schema_version"] == 1


def test_traced_chat_completions_capture(tracing_on):
    tmp = tracing_on
    c = _fake_client(chat_create=lambda **k: _ChatAPI("chat out"))
    trace_client(c, provider="anthropic")
    with trace_run("run-B"):
        out = c.chat.completions.create(model="claude-x", messages=[{"role": "user", "content": "yo"}])
    assert out.choices[0].message.content == "chat out"

    (rec,) = _read_jsonl(tmp / "llm_calls.jsonl")
    assert rec["call_type"] == "chat.completions" and rec["provider"] == "anthropic"
    assert rec["response"]["raw_text"] == "chat out"
    assert rec["response"]["finish_reason"] == "stop"
    assert rec["usage"] == {"input_tokens": 3, "output_tokens": 7}


# --------------------------------------------------------------------------
# transparency / failure isolation
# --------------------------------------------------------------------------


def test_sink_failure_never_breaks_the_call(tracing_on, monkeypatch):
    def boom(rec):
        raise RuntimeError("sink down")

    monkeypatch.setattr(client_mod, "emit_llm_call", boom)
    c = _fake_client(responses_create=lambda **k: _RespAPI("still works"))
    trace_client(c, provider="openai")
    with trace_run("run-C"):
        out = c.responses.create(model="m")  # must not raise
    assert out.output_text == "still works"


def test_upstream_exception_propagates_and_is_recorded(tracing_on):
    tmp = tracing_on

    def upstream_boom(**k):
        raise ValueError("upstream 500")

    c = _fake_client(responses_create=upstream_boom)
    trace_client(c, provider="openai")
    with trace_run("run-D"):
        with pytest.raises(ValueError, match="upstream 500"):
            c.responses.create(model="m")
    (rec,) = _read_jsonl(tmp / "llm_calls.jsonl")
    assert rec["status"] == "error" and "upstream 500" in rec["error"]


def test_wrap_is_idempotent(tracing_on):
    tmp = tracing_on
    c = _fake_client(responses_create=lambda **k: _RespAPI("o"))
    trace_client(c, provider="openai")
    trace_client(c, provider="openai")  # second wrap must not double-capture
    with trace_run("run-E"):
        c.responses.create(model="m")
    assert len(_read_jsonl(tmp / "llm_calls.jsonl")) == 1


# --------------------------------------------------------------------------
# stage spans
# --------------------------------------------------------------------------


def test_trace_stage_records_ok_and_error(tracing_on):
    tmp = tracing_on
    with trace_run("run-F"):
        with trace_stage("classifier"):
            pass
        with pytest.raises(ValueError):
            with trace_stage("gate"):
                raise ValueError("boom")
    recs = _read_jsonl(tmp / "stages.jsonl")
    by_stage = {r["stage"]: r for r in recs}
    assert by_stage["classifier"]["status"] == "ok"
    assert "duration_ms" in by_stage["classifier"]
    assert by_stage["gate"]["status"] == "error" and "boom" in by_stage["gate"]["error"]
    assert by_stage["classifier"]["run_id"] == "run-F"


# --------------------------------------------------------------------------
# s3
# --------------------------------------------------------------------------


def test_s3_upload_noop_without_bucket(monkeypatch):
    monkeypatch.delenv("TRACE_S3_BUCKET", raising=False)
    assert upload_run_traces("run-X") is None


def test_upload_run_logs_keys_and_filter(monkeypatch, tmp_path):
    from infra.tracing import upload_run_logs
    import infra.tracing.s3 as s3mod

    # no-op without a bucket
    monkeypatch.delenv("TRACE_S3_BUCKET", raising=False)
    assert upload_run_logs("rZ", tmp_path) is None

    combo = tmp_path / "python_redis_intermediate"
    combo.mkdir()
    (combo / "04_tasks.evals.log").write_text("eval")
    (combo / "04_tasks.stderr").write_text("err")
    (combo / "summary.json").write_text("{}")
    (combo / "notes.txt").write_text("skip me")  # wrong suffix → excluded

    monkeypatch.setenv("TRACE_S3_BUCKET", "mybucket")
    monkeypatch.setenv("TRACE_S3_PREFIX", "traces")
    monkeypatch.delenv("TRACE_COMBO", raising=False)  # combo derives from log_dir.name
    calls = []

    class _FakeS3:
        def upload_file(self, path, bucket, key):
            calls.append(key)

    monkeypatch.setattr(s3mod, "_s3_client", lambda: _FakeS3())
    pref = upload_run_logs("20260612T0000Z", combo, date="2026-06-12")

    # combo is now a partition (from log_dir.name); logs drop the trailing /<combo>
    base = "traces/dt=2026-06-12/combo=python_redis_intermediate/run=20260612T0000Z/logs"
    assert pref == f"s3://mybucket/{base}/"
    assert sorted(calls) == [
        f"{base}/04_tasks.evals.log",
        f"{base}/04_tasks.stderr",
        f"{base}/summary.json",
    ]  # notes.txt (wrong suffix) excluded


def test_upload_run_traces_combo_partition(monkeypatch, tmp_path):
    import infra.tracing.s3 as s3mod
    from infra.tracing.s3 import _safe_combo

    (tmp_path / "llm_calls.jsonl").write_text("{}")
    (tmp_path / "manifest.json").write_text("{}")

    monkeypatch.setenv("TRACE_S3_BUCKET", "mybucket")
    monkeypatch.setenv("TRACE_S3_PREFIX", "traces")
    monkeypatch.setenv("TRACE_COMBO", "python_redis_intermediate")
    calls = []

    class _FakeS3:
        def upload_file(self, path, bucket, key):
            calls.append(key)

    monkeypatch.setattr(s3mod, "_s3_client", lambda: _FakeS3())
    pref = upload_run_traces("20260612T0000Z", local_dir=tmp_path, date="2026-06-12")

    base = "traces/dt=2026-06-12/combo=python_redis_intermediate/run=20260612T0000Z"
    assert pref == f"s3://mybucket/{base}/"
    assert sorted(calls) == [f"{base}/llm_calls.jsonl", f"{base}/manifest.json"]

    # the slug is sanitized into a safe key segment; empty → "adhoc"
    assert _safe_combo("java, kafka:BASIC") == "java-kafka-BASIC"
    assert _safe_combo(None) == "adhoc"
    assert _safe_combo("") == "adhoc"


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# litellm hook (DSPy / prompt-generator capture)
# --------------------------------------------------------------------------


def test_litellm_hook_emits_record_from_callback_payload(tracing_on):
    import datetime

    from infra.tracing.litellm_hook import _emit

    resp = types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="dspy out"))],
        usage=_Usage(prompt_tokens=12, completion_tokens=34),
    )
    t0 = datetime.datetime(2026, 1, 1, 0, 0, 0)
    t1 = datetime.datetime(2026, 1, 1, 0, 0, 2)
    with trace_run("run-LL"), trace_stage("prompt"):
        _emit(
            {"model": "openai/gpt-5.4", "messages": [{"role": "user", "content": "hi"}]},
            resp, t0, t1, "ok",
        )
    (rec,) = _read_jsonl(tracing_on / "llm_calls.jsonl")
    assert rec["provider"] == "litellm" and rec["call_type"] == "litellm.completion"
    assert rec["stage"] == "prompt" and rec["run_id"] == "run-LL"
    assert rec["model"] == "openai/gpt-5.4"
    assert rec["response"]["raw_text"] == "dspy out"
    assert rec["usage"] == {"input_tokens": 12, "output_tokens": 34}
    assert rec["latency_ms"] == 2000


def test_register_litellm_tracing_is_noop_when_disabled(monkeypatch):
    monkeypatch.delenv("PIPELINE_TRACING_ENABLED", raising=False)
    import litellm

    import infra.tracing.litellm_hook as lh

    monkeypatch.setattr(lh, "_REGISTERED", False)
    before = list(getattr(litellm, "callbacks", None) or [])
    lh.register_litellm_tracing()  # disabled → must not register
    assert list(getattr(litellm, "callbacks", None) or []) == before
    assert lh._REGISTERED is False


def test_write_manifest_redacts_and_persists(tracing_on):
    from infra.tracing import write_manifest

    write_manifest(
        {"run_id": "run-Z", "outcome": "ok", "api_key": "sk-leak"}, run_id="run-Z"
    )
    data = json.loads((tracing_on / "manifest.json").read_text())
    assert data["run_id"] == "run-Z" and data["outcome"] == "ok"
    assert data["api_key"] == "<REDACTED>"
