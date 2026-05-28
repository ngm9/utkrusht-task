"""Public classifier helpers.

Direct callers should use ``generators.task.runtime_resolver.resolve_plan``
to classify a competency combo — it owns the cache + LLM call. This module
keeps ``Competency`` re-exported and a tiny ``to_competencies`` helper so
existing imports continue to work.
"""
from __future__ import annotations

from infra.classifier.runtime import Competency


def to_competencies(items: list[dict]) -> list[Competency]:
    """Convert raw dicts (from competency JSON files) to Competency objects."""
    return [
        Competency(name=item["name"], proficiency=item.get("proficiency", "BASIC"))
        for item in items
    ]
