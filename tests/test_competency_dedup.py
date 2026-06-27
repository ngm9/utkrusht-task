"""Duplicate-competency robustness (2026-06-19).

The competencies table can hold multiple rows for the same (name, proficiency)
— e.g. two 'RabbitMQ (INTERMEDIATE)' rows. A RabbitMQ+Golang pipeline run failed
at task-gen because the creator built a registry key with the duplicate
('… RabbitMQ (INTERMEDIATE), RabbitMQ (INTERMEDIATE)') that didn't match the
prompt's deduped key. These tests pin the dedupe that prevents a recurrence.
"""

from __future__ import annotations


def test_dedupe_collapses_same_name_proficiency() -> None:
    from infra.utils import _dedupe_competencies
    comps = [
        {"name": "RabbitMQ", "proficiency": "INTERMEDIATE"},
        {"name": "RabbitMQ", "proficiency": "INTERMEDIATE"},  # duplicate row
        {"name": "Golang", "proficiency": "INTERMEDIATE"},
    ]
    out = _dedupe_competencies(comps)
    assert [c["name"] for c in out] == ["RabbitMQ", "Golang"]  # order preserved


def test_dedupe_keeps_distinct_proficiencies() -> None:
    from infra.utils import _dedupe_competencies
    comps = [
        {"name": "RabbitMQ", "proficiency": "BASIC"},
        {"name": "RabbitMQ", "proficiency": "INTERMEDIATE"},
    ]
    assert len(_dedupe_competencies(comps)) == 2  # different proficiency = distinct


def test_dedupe_skips_nameless_rows() -> None:
    from infra.utils import _dedupe_competencies
    out = _dedupe_competencies([{"proficiency": "BASIC"}, {"name": "X", "proficiency": "BASIC"}])
    assert out == [{"name": "X", "proficiency": "BASIC"}]


def test_registry_lookup_succeeds_with_duplicate_competencies(monkeypatch) -> None:
    """The exact failure: duplicate RabbitMQ must still resolve the prompt."""
    from infra import utils
    key = "Golang (INTERMEDIATE), RabbitMQ (INTERMEDIATE)"
    tmpl = "{organization_background}|{role_context}|{competencies}|{real_world_task_scenarios}|{minutes_range}"
    monkeypatch.setitem(utils._PROMPT_REGISTRY, key, [tmpl])
    input_data = {
        "competencies": [
            {"name": "RabbitMQ", "proficiency": "INTERMEDIATE"},
            {"name": "RabbitMQ", "proficiency": "INTERMEDIATE"},  # duplicate
            {"name": "Golang", "proficiency": "INTERMEDIATE"},
        ],
        "background": {"organization": {"organization_background": "org"}, "role_context": "role"},
        "scenarios": "scenario text",
    }
    # Without the dedupe this raises ValueError("No prompt registered…RabbitMQ…, RabbitMQ…").
    out = utils.get_task_prompt_by_technology_stack("RabbitMQ, RabbitMQ, Golang", input_data)
    assert out and out[0].startswith("org|role|")
