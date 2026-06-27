"""Task-gen cost optimizations (2026-06-22).

#1 Lean retry: a retry (feedback present) makes ONE correction call instead of
   re-running the full 3-prompt generation and then correcting.
#2 Cheap repair: a MECHANICAL-failure retry routes to the cheaper repair model;
   substantive failures and the first attempt stay on the default model.
"""
from __future__ import annotations

import types


# ── shared fakes ─────────────────────────────────────────────────────────────
def _fake_response(content, in_tok=100, out_tok=50):
    msg = types.SimpleNamespace(content=content)
    choice = types.SimpleNamespace(message=msg, finish_reason="stop")
    usage = types.SimpleNamespace(
        prompt_tokens=in_tok, completion_tokens=out_tok,
        prompt_tokens_details=types.SimpleNamespace(cached_tokens=0),
    )
    return types.SimpleNamespace(choices=[choice], usage=usage)


class _FakeClient:
    def __init__(self, content):
        self._content = content
        self.calls = 0
        self.models_seen = []
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls += 1
        self.models_seen.append(kwargs.get("model"))
        return _fake_response(self._content)


_VALID = '{"name":"t","title":"T","question":"q","code_files":{}}'


def _data():
    return {
        "competencies": [{"name": "GraphQL", "proficiency": "INTERMEDIATE"}],
        "background": {},
        "scenarios": [],
    }


# ── #1 lean retry ────────────────────────────────────────────────────────────
def test_base_generation_makes_three_calls(monkeypatch):
    import infra.utils as U
    monkeypatch.setattr(U, "get_task_prompt_by_technology_stack",
                        lambda stack, data: ["P1", "P2", "P3"])
    c = _FakeClient(_VALID)
    out = U.generate_task_with_code(c, _data(), feedback="")
    assert c.calls == 3            # 3 base prompts, no correction
    assert out["name"] == "t"


def test_lean_retry_makes_single_correction_call(monkeypatch):
    import infra.utils as U
    monkeypatch.setattr(U, "get_task_prompt_by_technology_stack",
                        lambda stack, data: ["P1", "P2", "P3"])
    monkeypatch.setattr(U, "TASK_GEN_LEAN_RETRY", True)
    c = _FakeClient(_VALID)
    out = U.generate_task_with_code(c, _data(), feedback="FAILED: patch this")
    assert c.calls == 1            # ONE correction call — no 3-prompt regen
    assert out["name"] == "t"


def test_lean_off_falls_back_to_regenerate_then_correct(monkeypatch):
    import infra.utils as U
    monkeypatch.setattr(U, "get_task_prompt_by_technology_stack",
                        lambda stack, data: ["P1", "P2", "P3"])
    monkeypatch.setattr(U, "TASK_GEN_LEAN_RETRY", False)
    c = _FakeClient(_VALID)
    out = U.generate_task_with_code(c, _data(), feedback="FAILED: patch this")
    assert c.calls == 4            # 3 regen + 1 correction (old behavior)
    assert out["name"] == "t"


def test_lean_retry_uses_passed_model(monkeypatch):
    import infra.utils as U
    monkeypatch.setattr(U, "get_task_prompt_by_technology_stack",
                        lambda stack, data: ["P1", "P2", "P3"])
    monkeypatch.setattr(U, "TASK_GEN_LEAN_RETRY", True)
    c = _FakeClient(_VALID)
    U.generate_task_with_code(c, _data(), feedback="FAILED", model="claude-sonnet-4-6")
    assert c.models_seen == ["claude-sonnet-4-6"]


# ── #2 cheap repair routing ──────────────────────────────────────────────────
def test_repair_model_selection():
    from generators.task.creator import (
        _repair_model_for, _TASK_GEN_MODEL, _TASK_GEN_REPAIR_MODEL,
    )
    # first attempt (no feedback) → default model
    assert _repair_model_for("") == _TASK_GEN_MODEL
    # mechanical failures → cheaper repair model
    assert _repair_model_for("ModuleNotFoundError: No module named 'psycopg'") == _TASK_GEN_REPAIR_MODEL
    assert _repair_model_for("E2B sandbox gate FAILED (runsh_failed): run.sh exited 1") == _TASK_GEN_REPAIR_MODEL
    assert _repair_model_for("npm error Missing: get-caller-file from lock file") == _TASK_GEN_REPAIR_MODEL
    assert _repair_model_for(
        "Criterion 5: Runtime reasonableness — graphql-tag not listed in package.json"
    ) == _TASK_GEN_REPAIR_MODEL
    # substantive failures stay on the default (Opus) model
    assert _repair_model_for(
        "Criterion 6: DOMAIN ALIGNMENT — the scenario drifted into the employer's domain"
    ) == _TASK_GEN_MODEL
    assert _repair_model_for("Agent prompt encodes a FAKE LLM; require a real model call") == _TASK_GEN_MODEL
