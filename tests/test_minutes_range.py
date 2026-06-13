"""The code-flow {minutes_range} placeholder scales with proficiency.

get_task_prompt_by_technology_stack fills {minutes_range} with a per-proficiency
time budget (BASIC 15-20 / INTERMEDIATE 20-25 / ADVANCED 25-30); an explicit
input_data["minutes_range"] overrides.
"""
from unittest.mock import patch

import pytest

import infra.utils as u


def _input(proficiency: str) -> dict:
    return {
        "competencies": [{"name": "Python", "proficiency": proficiency}],
        "background": {
            "organization": {"organization_background": "org"},
            "role_context": "role",
            "questions_prompt": "q",
        },
        "scenarios": "some scenario text",
        "existing_task_titles": None,
    }


@pytest.mark.parametrize(
    "proficiency, expected",
    [("BASIC", "15-20"), ("INTERMEDIATE", "20-25"), ("ADVANCED", "25-30")],
)
def test_minutes_range_scales_with_proficiency(proficiency, expected):
    fake_registry = {f"Python ({proficiency})": ["{minutes_range}"]}
    with patch.object(u, "_PROMPT_REGISTRY", fake_registry):
        out = u.get_task_prompt_by_technology_stack("Python", _input(proficiency))
    assert out == [expected]


def test_explicit_minutes_range_overrides_proficiency_default():
    fake_registry = {"Python (BASIC)": ["{minutes_range}"]}
    inp = _input("BASIC")
    inp["minutes_range"] = "99-100"
    with patch.object(u, "_PROMPT_REGISTRY", fake_registry):
        out = u.get_task_prompt_by_technology_stack("Python", inp)
    assert out == ["99-100"]


def test_unknown_proficiency_falls_back_to_15_20():
    fake_registry = {"Python (BEGINNER)": ["{minutes_range}"]}
    with patch.object(u, "_PROMPT_REGISTRY", fake_registry):
        out = u.get_task_prompt_by_technology_stack("Python", _input("BEGINNER"))
    assert out == ["15-20"]


def test_minutes_range_read_from_background_input_file():
    # The user-editable value in the background input file wins over the
    # proficiency default (a BASIC task with an edited 42-45 budget).
    fake_registry = {"Python (BASIC)": ["{minutes_range}"]}
    inp = _input("BASIC")
    inp["background"]["minutes_range"] = "42-45"
    with patch.object(u, "_PROMPT_REGISTRY", fake_registry):
        out = u.get_task_prompt_by_technology_stack("Python", inp)
    assert out == ["42-45"]


def test_top_level_minutes_range_beats_background():
    fake_registry = {"Python (BASIC)": ["{minutes_range}"]}
    inp = _input("BASIC")
    inp["background"]["minutes_range"] = "42-45"
    inp["minutes_range"] = "99-100"  # explicit override wins over the input file
    with patch.object(u, "_PROMPT_REGISTRY", fake_registry):
        out = u.get_task_prompt_by_technology_stack("Python", inp)
    assert out == ["99-100"]
