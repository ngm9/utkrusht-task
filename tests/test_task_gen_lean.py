"""TASK_GEN_LEAN_FIRST (#2): the first task-gen attempt collapses the 3 staged
prompts (CONTEXT + INPUT_AND_ASK + INSTRUCTIONS) into ONE combined user message
and a SINGLE LLM call, instead of replaying them as 3 sequential turns where
turns 1-2 are generated, discarded, and paid for.

These mock the LLM client + prompt fetch so no network/key is used.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest


_VALID_TASK = json.dumps({
    "name": "n", "title": "t", "question": "q",
    "code_files": {"a.py": "x = 1\n"},
    "answer": "a", "definitions": {"d": "x"}, "hints": "h",
    "outcomes": "o", "pre_requisites": ["p"], "short_overview": ["s"],
})


def _fake_client(calls):
    """An OpenAI-shaped client whose create() records the messages it received."""
    def create(model, messages, **kw):
        calls.append(messages)
        return SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=_VALID_TASK),
                finish_reason="stop",
            )],
            usage=SimpleNamespace(
                prompt_tokens=10, completion_tokens=20,
                prompt_tokens_details=SimpleNamespace(cached_tokens=0),
            ),
        )
    return SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )


def _wire(monkeypatch):
    # lean path imports infra.evals (constructs an OpenAI client at import) — a
    # dummy key keeps that import from raising in the test env.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    from infra import utils
    import infra.pricing as pricing
    monkeypatch.setattr(utils, "get_task_prompt_by_technology_stack",
                        lambda stack, data: ["CTX_BLOCK", "ASK_BLOCK", "INSTR_BLOCK"])
    monkeypatch.setattr(utils, "cache_messages", lambda m: m)
    monkeypatch.setattr(utils, "provider_request_kwargs", lambda: {})
    monkeypatch.setattr(pricing, "price_per_million", lambda m: (1.0, 1.0))
    return utils


_INPUT = {"competencies": [{"name": "Python"}], "background": {}, "scenarios": []}


def test_lean_first_makes_one_call_with_combined_prompt(monkeypatch):
    utils = _wire(monkeypatch)
    monkeypatch.setattr(utils, "TASK_GEN_LEAN_FIRST", True)

    calls: list = []
    out = utils.generate_task_with_code(_fake_client(calls), _INPUT,
                                        feedback="", model="claude-test")

    # exactly ONE call (not three staged turns)
    assert len(calls) == 1
    # that call carries all three prompts in a SINGLE user message
    user_msgs = [m for m in calls[0] if m["role"] == "user"]
    assert len(user_msgs) == 1
    body = user_msgs[0]["content"]
    assert "CTX_BLOCK" in body and "ASK_BLOCK" in body and "INSTR_BLOCK" in body
    # and it still returns the parsed task
    assert out["name"] == "n"


def test_lean_first_off_falls_back_to_three_turns(monkeypatch):
    utils = _wire(monkeypatch)
    monkeypatch.setattr(utils, "TASK_GEN_LEAN_FIRST", False)

    calls: list = []
    utils.generate_task_with_code(_fake_client(calls), _INPUT,
                                  feedback="", model="claude-test")

    # legacy staged path = one call per prompt (3)
    assert len(calls) == 3
