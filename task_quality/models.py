"""Data primitives for the content-quality layer.

Kept independent of ``task_quality.runner`` and ``task_quality.semantic``
so they can be imported without circular dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Violation:
    """One issue the LLM judge identified, plus the field it applies to.

    ``actual_value`` is whatever the candidate had in that field before
    the rewrite was applied (truncated by the feedback composer for log
    safety); ``rewrite_applied`` is the corrected value the LLM emitted
    for the field (or ``None`` if no rewrite was issued — e.g. when the
    issue is about field count or shape and the LLM patched the whole
    list rather than the single offending item).
    """

    field_path: str
    reason: str
    actual_value: Any = None
    rewrite_applied: Any = None


@dataclass
class QualityReport:
    """Outcome of one judge-and-rewrite pass.

    ``passed`` is True iff the LLM reported zero issues. When False, the
    candidate has already been patched with whatever rewrites the LLM
    emitted — the report exists for logging + observability, not to gate
    the pipeline.

    ``rewrites_applied`` is the dict of {field_name: new_value} that was
    spliced into the candidate. Empty when the task was already clean.

    ``llm_call_count`` is always 1 on success — the layer is a single
    consolidated call.
    """

    passed: bool
    violations: list[Violation] = field(default_factory=list)
    rewrites_applied: dict = field(default_factory=dict)
    llm_call_count: int = 0
