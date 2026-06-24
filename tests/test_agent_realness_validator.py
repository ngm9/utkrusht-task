"""Tests for the agent-realness validator guard (2026-06-19).

Background: all 8 Intermediate agent tasks shipped a FAKE LLM (FakeLLM / regex
intent parser / time.sleep "agents") because the prompt template encoded
"LLM-free / deterministic / stub" framing meant only for the readiness gate, and
the DSPy verifier is intentionally OFF. These tests pin the deterministic
validator guard that catches a regression to fake-agent prompts.

See docs/plans/2026-06-19-agent-task-fake-llm-rootcause.md
"""

from __future__ import annotations

from pathlib import Path

from generators.prompts.validator import (
    _agent_realness_issues,
    _is_agent_combo,
    _unnegated_fake_hits,
    validate_prompt_file,
)

_AGENT_COMP = [{"name": "Production Agent Engineering", "proficiency": "INTERMEDIATE"}]
_NON_AGENT_COMP = [{"name": "Python", "proficiency": "INTERMEDIATE"}]

_BASELINE = (
    Path(__file__).parent.parent
    / "task_generation_prompts"
    / "Intermediate"
    / "production_agent_engineering_intermediate_prompt"
    / "production_agent_engineering_intermediate_prompt.py"
)


# ── _is_agent_combo ─────────────────────────────────────────────────────────

def test_is_agent_combo_true_for_agent_competencies() -> None:
    for name in ("Multi-Agent Systems", "Production Agent Engineering",
                 "Tool Use for Agents", "Context Engineering"):
        assert _is_agent_combo([{"name": name, "proficiency": "INTERMEDIATE"}])


def test_is_agent_combo_false_for_backend() -> None:
    assert not _is_agent_combo(_NON_AGENT_COMP)
    assert not _is_agent_combo([{"name": "PostgreSQL", "proficiency": "BASIC"}])


# ── _unnegated_fake_hits (negation-aware proximity) ─────────────────────────

def test_unnegated_fake_hit_flagged_when_mandated() -> None:
    assert "fakellm" in _unnegated_fake_hits("we implement a fakellm here")


def test_fake_hit_not_flagged_when_prohibited() -> None:
    # A prohibition ("never a FakeLLM") must NOT be flagged.
    assert _unnegated_fake_hits("never a fakellm; call a real model") == []
    assert _unnegated_fake_hits("do not use a deterministic stand-in") == []


# ── _agent_realness_issues ──────────────────────────────────────────────────

def test_fake_mandate_is_flagged() -> None:
    issues = _agent_realness_issues("Implement a FakeLLM stand-in for the model.")
    assert any("FAKE LLM/agent" in i for i in issues)


def test_missing_real_mandate_is_flagged() -> None:
    # No fake pattern, but also no real-LLM mandate → flag the missing mandate.
    issues = _agent_realness_issues("The agent builds context and dispatches tools.")
    assert any("does not MANDATE a real LLM" in i for i in issues)


def test_real_mandate_with_negated_prohibition_passes() -> None:
    src = ("The agent calls a REAL model via litellm on the candidate's key. "
           "NEVER a FakeLLM. NEVER any deterministic stand-in for the model.")
    assert _agent_realness_issues(src) == []


# ── validate_prompt_file integration (scoped to agent competencies) ─────────

_FAKE_SRC = (
    'PROMPT_REGISTRY = {"Production Agent Engineering (INTERMEDIATE)": ["c", "i", "x"]}\n'
    'INSTRUCTIONS = "Implement a FakeLLM that returns canned responses."\n'
)


def test_validate_flags_agent_fake() -> None:
    res = validate_prompt_file(_FAKE_SRC, _AGENT_COMP, "INTERMEDIATE")
    assert res.passed is False
    assert any("FAKE LLM/agent" in i for i in res.issues)


def test_validate_ignores_fake_for_non_agent() -> None:
    # The same source under a non-agent competency must NOT raise the agent guard
    # (backend tasks legitimately have no LLM).
    res = validate_prompt_file(_FAKE_SRC, _NON_AGENT_COMP, "INTERMEDIATE")
    assert not any("FAKE LLM/agent" in i for i in res.issues)
    assert not any("does not MANDATE a real LLM" in i for i in res.issues)


# ── regression on the real corrected baseline artifact ──────────────────────

def test_corrected_baseline_passes_realness() -> None:
    """The fixed agent baseline must NOT trip the guard (mandates a real model,
    prohibitions are negated, no fake stand-in)."""
    source = _BASELINE.read_text(encoding="utf-8")
    assert _agent_realness_issues(source) == []
