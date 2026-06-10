"""Routing of agent competencies to the tighter INTERMEDIATE guardrail.

Agent competencies at INTERMEDIATE systematically over-scoped at the scenario
scope critic because the generic INTERMEDIATE guardrail tells the generator to
combine 4-5 concepts (a non-agent, DB-optimization shape). Agent competencies
now route to a dedicated, single-concern agent block via
``get_proficiency_guardrails`` — which both the generator and the eval critic
call, so they stay in agreement.
"""
from generators.scenarios.prompts import (
    AGENT_INTERMEDIATE_GUARDRAIL,
    PROFICIENCY_GUARDRAILS,
    get_proficiency_guardrails,
)

AGENT_HINT = "Tool Use for Agents"
NON_AGENT_HINT = "Python, PostgreSQL"


def test_agent_intermediate_routes_to_tight_agent_block():
    block = get_proficiency_guardrails("INTERMEDIATE", competency_hint=AGENT_HINT)
    assert block == AGENT_INTERMEDIATE_GUARDRAIL
    assert "ONE focused" in block
    assert "EXACTLY ONE primary concern" in block


def test_non_agent_intermediate_keeps_generic_block():
    block = get_proficiency_guardrails("INTERMEDIATE", competency_hint=NON_AGENT_HINT)
    assert block == PROFICIENCY_GUARDRAILS["INTERMEDIATE"]
    # generic (non-agent) INTERMEDIATE block markers
    assert "mid-senior developer" in block
    assert "DO NOT OVER-SCOPE" in block      # anti-bundling guard


def test_intermediate_blocks_are_tightly_scoped():
    # Both the agent and generic INTERMEDIATE blocks must cap bullets at 4 and
    # warn against bundling, so neither over-scopes at stage 2.
    generic = PROFICIENCY_GUARDRAILS["INTERMEDIATE"]
    assert "Max 4 bullet points" in generic
    assert "4-5 concepts" not in generic     # the old over-scoping instruction is gone


def test_empty_hint_intermediate_is_backward_compatible():
    # Legacy callers pass no hint — must keep the generic INTERMEDIATE block.
    assert get_proficiency_guardrails("INTERMEDIATE") == PROFICIENCY_GUARDRAILS["INTERMEDIATE"]


def test_agent_basic_is_unchanged():
    # Only INTERMEDIATE agent routing changes; BASIC stays generic.
    assert get_proficiency_guardrails("BASIC", competency_hint=AGENT_HINT) == PROFICIENCY_GUARDRAILS["BASIC"]


def test_agent_advanced_still_uses_agent_advanced_block():
    # ADVANCED already is agent-specific; agent hint keeps that block.
    assert get_proficiency_guardrails("ADVANCED", competency_hint=AGENT_HINT) == PROFICIENCY_GUARDRAILS["ADVANCED"]
