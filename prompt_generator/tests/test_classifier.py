"""Regression tests for ``classify_task_category``.

Each test pins one categorisation rule that previously misbehaved. New rules
should add a case here; existing cases must continue to pass.
"""

from __future__ import annotations

import pytest

from prompt_generator.classifier import (
    Competency,
    TaskCategory,
    classify_task_category,
)


def _comps(*names: str, level: str = "BASIC") -> list[Competency]:
    return [Competency(name=n, proficiency=level) for n in names]


@pytest.mark.parametrize(
    ("competencies", "expected"),
    [
        # Containerised — formerly classified as PURE_CODE because Docker was
        # not a recognised infrastructure token.
        (_comps("Java", "Docker"), TaskCategory.CONTAINERIZED_APP),
        (_comps("Python", "Docker"), TaskCategory.CONTAINERIZED_APP),
        (_comps("Go", "Docker"), TaskCategory.CONTAINERIZED_APP),
        (_comps("Python", "FastAPI", "Docker"), TaskCategory.CONTAINERIZED_APP),
        (_comps("Java", "Kubernetes"), TaskCategory.CONTAINERIZED_APP),

        # DB ⇒ APP_AND_DB / SCRIPT_AND_DB win over Docker — the DB is the
        # stronger infrastructure signal even when containerisation is present.
        (_comps("Python", "FastAPI", "PostgreSQL", "Docker"), TaskCategory.APP_AND_DB),
        (_comps("Node.js", "PostgreSQL"), TaskCategory.APP_AND_DB),
        (_comps("Python", "SQL"), TaskCategory.SCRIPT_AND_DB),

        # Redis — plain "Redis" name was previously missed because only the
        # legacy "redis_cache" token existed.
        (_comps("Go", "Redis"), TaskCategory.SCRIPT_AND_DB),
        (_comps("Python", "Redis"), TaskCategory.SCRIPT_AND_DB),

        # Existing rules — keep passing.
        (_comps("SQL"), TaskCategory.DB_ONLY),
        (_comps("Python"), TaskCategory.PURE_CODE),
        (_comps("React"), TaskCategory.FRONTEND),
        (_comps("Python", "Langchain"), TaskCategory.LLM_FRAMEWORK),
        (_comps("Python", "Vector Databases"), TaskCategory.VECTOR_DB),
        (_comps("Java", "Kafka"), TaskCategory.MESSAGING),
        (_comps("Microservices", "Java"), TaskCategory.MICROSERVICES),
    ],
)
def test_classify_task_category(competencies, expected):
    assert classify_task_category(competencies) == expected


def test_empty_competencies_raises():
    with pytest.raises(ValueError):
        classify_task_category([])
