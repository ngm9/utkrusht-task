"""The agent reference prompts carry the open-endedness rules — deterministically.

Why these exist: HARD CONSTRAINT #1 in the prompt-generator signature is
STRUCTURAL MIMICRY — the generator copies the reference prompts far more
reliably than it follows written rules. So the stub-level withholding rules
have to live in the REFERENCES, not only in constraint #9. Observed 2026-07-20:
two ADVANCED generations from the same command, one honoured #9 fully and one
dropped it entirely, because no reference backed it up.

Also pins that ADVANCED has its own baseline. It previously fell back to the
INTERMEDIATE file, so ADVANCED agent tasks were shaped by an intermediate
exemplar while being told to be harder.
"""
import importlib.util
import pathlib

import pytest

REF_DIR = pathlib.Path(__file__).parents[1] / "task_generation_prompts" / "_general_reference"

FMT_KEYS = dict(
    organization_background="ORG", role_context="ROLE", minutes_range="45-60",
    competencies="COMP", real_world_task_scenarios="SCEN", question_prompt="Q",
)

AGENT_LEVELS = ["beginner", "basic", "intermediate", "advanced"]
# Levels where the solution must be withheld at the stub level.
OPEN_ENDED_LEVELS = ["intermediate", "advanced"]


def _load(level):
    name = f"agent_general_{level}_prompt"
    spec = importlib.util.spec_from_file_location(name, REF_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _text(level):
    return (REF_DIR / f"agent_general_{level}_prompt.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("level", AGENT_LEVELS)
def test_agent_reference_exists(level):
    assert (REF_DIR / f"agent_general_{level}_prompt.py").exists()


def test_advanced_does_not_fall_back_to_intermediate():
    """The bug this closes: ADVANCED had no file, so it borrowed INTERMEDIATE's."""
    from flows.tech.stages.prompts.retriever import _agent_baseline_path
    assert _agent_baseline_path("ADVANCED").name == "agent_general_advanced_prompt.py"
    assert _agent_baseline_path("INTERMEDIATE").name == "agent_general_intermediate_prompt.py"


@pytest.mark.parametrize("level", AGENT_LEVELS)
def test_reference_still_formats(level):
    """A stray single brace would crash str.format() at generation time."""
    mod = _load(level)
    const = f"_BASE_{level.upper()}"
    turns = getattr(mod, const, None)
    if turns is None:  # beginner/basic may name their base differently
        pytest.skip(f"{const} not defined in {level} reference")
    for turn in turns:
        turn.format(**FMT_KEYS)


@pytest.mark.parametrize("level", OPEN_ENDED_LEVELS)
def test_stub_level_withholding_present(level):
    """Stub docstrings must not hand over the data shape."""
    body = _text(level)
    assert "Expected shape:" in body, "must forbid an Expected-shape block"
    assert "enum vocabulary" in body, "must forbid enum vocabulary in stubs"
    assert "DESIGNS" in body or "designs" in body, "candidate must design the shape"


@pytest.mark.parametrize("level", OPEN_ENDED_LEVELS)
def test_policy_constants_not_pre_set(level):
    """Thresholds/budgets are the candidate's decision, not a filled-in default."""
    body = _text(level)
    assert "pre-set" in body.lower()
    assert "retry" in body.lower() and "budget" in body.lower()


def test_advanced_is_calibrated_harder_than_intermediate():
    adv, inter = _text("advanced"), _text("intermediate")
    assert "DIFFICULTY CALIBRATION (ADVANCED)" in adv
    assert "DIFFICULTY CALIBRATION (INTERMEDIATE)" in inter
    assert "DIFFICULTY CALIBRATION (INTERMEDIATE)" not in adv, "stale INTERMEDIATE calibration"
    # The ADVANCED distinguishing idea: decisions that conflict with each other.
    assert "INTERACTING" in adv or "interacting" in adv


def test_advanced_keys_registry_at_advanced():
    """A copy-paste slip here would key the prompt at the wrong proficiency."""
    adv = _text("advanced")
    assert "Agent Engineering (ADVANCED)" in adv
    assert "Agent Engineering (INTERMEDIATE)" not in adv


def test_advanced_still_ships_a_runnable_suite():
    """Withholding the solution must never mean the candidate cannot self-check.

    Phase 2 splits the suite (derivable checks stay visible, answer-revealing
    ones move to `grading/`), so the guarantee is no longer "all tests ship" —
    it is "a runnable `invariants/` suite always ships".
    """
    adv = _text("advanced")
    assert "ALWAYS receives a runnable test suite" in adv
    assert "invariants/" in adv


def test_advanced_hidden_tests_are_grader_only():
    """The split must be explicit that hidden tests never reach the candidate."""
    adv = _text("advanced")
    assert "NEVER shipped" in adv
    assert "answer repo" in adv
