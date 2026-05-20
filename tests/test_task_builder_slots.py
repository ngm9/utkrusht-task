"""TaskBrief slot model and merge logic."""
from task_builder.slots import TaskBrief, merge_brief, REQUIRED_SLOTS


def test_empty_brief_reports_all_required_slots_missing():
    brief = TaskBrief()
    assert brief.missing_slots() == list(REQUIRED_SLOTS)
    assert brief.is_complete() is False


def test_full_brief_is_complete():
    brief = TaskBrief(
        competencies=["Java"],
        proficiency="BASIC",
        role="Backend Engineer",
        focus_areas=["idempotency"],
        domain="fintech",
    )
    assert brief.missing_slots() == []
    assert brief.is_complete() is True


def test_scenario_count_defaults_to_six_and_is_not_required():
    brief = TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["x"], domain="fintech",
    )
    assert brief.scenario_count == 6


def test_merge_brief_returns_new_object_without_mutating():
    original = TaskBrief(competencies=["Java"])
    merged = merge_brief(original, {"proficiency": "BASIC"})
    assert merged.proficiency == "BASIC"
    assert original.proficiency is None  # immutability
    assert merged.competencies == ["Java"]


def test_merge_brief_ignores_unknown_keys():
    brief = TaskBrief()
    merged = merge_brief(brief, {"nonsense": "value", "domain": "saas"})
    assert merged.domain == "saas"
    assert not hasattr(merged, "nonsense")
