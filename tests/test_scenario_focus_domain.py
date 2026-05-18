"""Layer B — focus_areas and domain wiring in scenario_generator prompts."""
from scenario_generator.prompts import (
    build_focus_areas_block,
    build_domain_rule_block,
    build_generation_prompt,
)


def test_focus_areas_block_empty_when_none():
    assert build_focus_areas_block(None) == ""
    assert build_focus_areas_block([]) == ""


def test_focus_areas_block_lists_areas_when_set():
    block = build_focus_areas_block(["idempotency", "error handling"])
    assert "ASSESSMENT FOCUS" in block
    assert "idempotency" in block
    assert "error handling" in block


def test_domain_rule_block_default_keeps_variety():
    block = build_domain_rule_block(None)
    assert "DIFFERENT business domain" in block


def test_domain_rule_block_pins_one_domain_when_set():
    block = build_domain_rule_block("fintech payments")
    assert "fintech payments" in block
    assert "ALL scenarios" in block
    assert "DIFFERENT business domain" not in block


def test_generation_prompt_injects_focus_when_set():
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
        focus_areas=["idempotency"],
        domain=None,
    )
    assert "idempotency" in prompt
    assert "ASSESSMENT FOCUS" in prompt


def test_generation_prompt_pins_domain_when_set():
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
        focus_areas=None,
        domain="healthcare",
    )
    assert "ALL scenarios" in prompt
    assert "healthcare" in prompt
    assert "DIFFERENT business domain" not in prompt


def test_generation_prompt_unchanged_when_no_focus_or_domain():
    """Backward compatibility: omitting both flags = today's behaviour."""
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
    )
    assert "DIFFERENT business domain" in prompt
    assert "ASSESSMENT FOCUS" not in prompt


def test_generation_prompt_injects_focus_on_non_code_path():
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Product Manager",
        count=3,
        existing_scenarios=[],
        focus_areas=["metric selection"],
        domain="fintech",
        is_non_code=True,
    )
    assert "ASSESSMENT FOCUS" in prompt
    assert "metric selection" in prompt
    assert "ALL scenarios" in prompt
    assert "fintech" in prompt
