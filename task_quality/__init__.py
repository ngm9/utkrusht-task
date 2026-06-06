"""Task content-quality eval layer.

ONE LLM call per attempt judges the candidate task on every content-quality
rule (title shape, short_overview 3-part shape + count, bullet hygiene,
question length, framing + relevance) AND emits a corrected version of
every failing field. The runner splices the rewrites directly into the
candidate and proceeds — content-quality is an autofix layer, not a
retry-gate.

Sits between the LLM-critic + E2B-gate (which judge semantic quality and
build correctness) and the Pydantic DAO validator (which checks shape +
FK at insert time).

Public surface:

- :class:`Violation`, :class:`QualityReport` — eval-result data primitives
- :func:`evaluate_and_patch_task`, :func:`run_quality_for_attempt` —
  the two entry points; ``run_quality_for_attempt`` is the one
  ``generators/task/creator.py`` calls.
"""
from task_quality.models import (
    QualityReport,
    Violation,
)
from task_quality.runner import (
    evaluate_and_patch_task,
    run_quality_for_attempt,
)

__all__ = [
    "Violation",
    "QualityReport",
    "evaluate_and_patch_task",
    "run_quality_for_attempt",
]
