"""New-run modal: free-text `instructions` (replaces the infra/non_infra force)
threaded to run_pipeline, plus the LLM-backed /api/suggest-instructions endpoint
(parse + cache + threading), with the LLM call mocked."""
from __future__ import annotations

import json

import pytest
from fastapi import HTTPException


# ----------------------------------------------------------------------
# RunRequest shape: instructions in, infra/task_shape out
# ----------------------------------------------------------------------

def test_runrequest_dropped_infra_added_instructions():
    from trace_ui.server import RunRequest
    f = RunRequest.model_fields
    assert "instructions" in f
    assert "task_shape" not in f
    assert "infra_kind" not in f


# ----------------------------------------------------------------------
# api_launch threads --instructions (and no longer --task-shape/--infra-kind)
# ----------------------------------------------------------------------

def test_launch_threads_instructions_stripped(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))

    srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC",
                              instructions="   include docker-compose + run.sh   "))
    cmd = cap["cmd"]
    assert "--instructions" in cmd
    assert cmd[cmd.index("--instructions") + 1] == "include docker-compose + run.sh"  # stripped
    # the removed flags must be gone entirely
    assert "--task-shape" not in cmd and "--infra-kind" not in cmd


def test_launch_omits_instructions_when_blank(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))

    srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC", instructions="   "))
    assert "--instructions" not in cap["cmd"]


def test_launch_caps_instructions_length(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))

    srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC", instructions="x" * 9000))
    cmd = cap["cmd"]
    assert len(cmd[cmd.index("--instructions") + 1]) == 4000


# ----------------------------------------------------------------------
# suggestion parsing (no network)
# ----------------------------------------------------------------------

def test_parse_suggestions_json_array():
    from trace_ui.server import _parse_suggestions
    assert _parse_suggestions('["a clear directive", "another directive"]') == \
        ["a clear directive", "another directive"]


def test_parse_suggestions_fenced_json():
    from trace_ui.server import _parse_suggestions
    out = _parse_suggestions('```json\n["fenced directive one", "fenced directive two"]\n```')
    assert out == ["fenced directive one", "fenced directive two"]


def test_parse_suggestions_line_fallback():
    from trace_ui.server import _parse_suggestions
    out = _parse_suggestions("- first long directive here\n2) second long directive here")
    assert out == ["first long directive here", "second long directive here"]


def test_parse_suggestions_empty():
    from trace_ui.server import _parse_suggestions
    assert _parse_suggestions("") == []
    assert _parse_suggestions("nope no json no bullets") == ["nope no json no bullets"]


# ----------------------------------------------------------------------
# /api/suggest-instructions endpoint (LLM call mocked)
# ----------------------------------------------------------------------

def test_suggest_endpoint_returns_and_caches(monkeypatch):
    from trace_ui import server as srv

    calls: list = []

    def fake(names, prof):
        calls.append((tuple(names), prof))
        return [f"directive for {','.join(names)} @ {prof}"]

    monkeypatch.setattr(srv, "_suggest_instructions", fake)
    srv._SUGGEST_CACHE.clear()

    resp = srv.api_suggest_instructions(names="Python,Kafka", proficiency="intermediate")
    body = json.loads(bytes(resp.body).decode())
    assert body["suggestions"] == ["directive for Python,Kafka @ INTERMEDIATE"]

    # same combo (order-insensitive key) → served from cache, no second LLM call
    resp2 = srv.api_suggest_instructions(names="Kafka,Python", proficiency="INTERMEDIATE")
    body2 = json.loads(bytes(resp2.body).decode())
    assert body2.get("cached") is True
    assert len(calls) == 1


def test_suggest_endpoint_requires_names():
    from trace_ui import server as srv
    with pytest.raises(HTTPException) as ei:
        srv.api_suggest_instructions(names="   ", proficiency="BASIC")
    assert ei.value.status_code == 400


def test_suggest_endpoint_soft_errors(monkeypatch):
    from trace_ui import server as srv

    def boom(names, prof):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(srv, "_suggest_instructions", boom)
    srv._SUGGEST_CACHE.clear()
    resp = srv.api_suggest_instructions(names="Python", proficiency="BASIC")
    assert resp.status_code == 503
    body = json.loads(bytes(resp.body).decode())
    assert body["suggestions"] == [] and "error" in body
