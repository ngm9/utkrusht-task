"""Unit tests for the Anthropic prompt-cache helper (infra/prompt_cache).

Structure only — no network. The end-to-end cache-read behaviour through Portkey
is verified separately against the live API."""
from __future__ import annotations

import infra.prompt_cache as pc

_EPH = {"type": "ephemeral"}


def test_noop_for_glm_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "glm")
    msgs = [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}]
    assert pc.cache_messages(msgs) is msgs  # returned unchanged (no-op)


def test_noop_for_empty(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert pc.cache_messages([]) == []


def test_marks_system_and_last_only(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    msgs = [
        {"role": "system", "content": "S"},
        {"role": "user", "content": "U1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "U2"},
    ]
    out = pc.cache_messages(msgs)

    # system (first) carries a breakpoint, content normalised to a text block
    assert out[0]["content"][0] == {"type": "text", "text": "S", "cache_control": _EPH}
    # last message carries a breakpoint
    assert out[-1]["content"][-1] == {"type": "text", "text": "U2", "cache_control": _EPH}
    # middle messages: normalised to blocks but NO cache_control
    assert out[1]["content"][0] == {"type": "text", "text": "U1"}
    assert out[2]["content"][0] == {"type": "text", "text": "A1"}

    # immutable: the caller's original list/dicts are untouched (still strings)
    assert msgs[0]["content"] == "S" and isinstance(msgs[3]["content"], str)


def test_single_system_message_marked_once(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    out = pc.cache_messages([{"role": "system", "content": "only"}])
    assert out[0]["content"][0]["cache_control"] == _EPH


def test_no_system_marks_last(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    out = pc.cache_messages([{"role": "user", "content": "a"}, {"role": "user", "content": "b"}])
    assert "cache_control" not in out[0]["content"][0]
    assert out[1]["content"][-1]["cache_control"] == _EPH


def test_preexisting_block_content_preserved(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    msgs = [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]
    out = pc.cache_messages(msgs)
    assert out[0]["content"][0] == {"type": "text", "text": "hi", "cache_control": _EPH}
    # original block dict not mutated
    assert "cache_control" not in msgs[0]["content"][0]
