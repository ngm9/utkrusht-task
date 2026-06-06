"""Orchestrates the single judge+rewrite call and splices the rewrites
into the candidate task dict.

Public surface:

- :func:`evaluate_and_patch_task` — judge + rewrite + splice in one call
- :func:`run_quality_for_attempt` — wrapper used by ``creator.py``

There is no ``RETRY`` outcome — content-quality issues are autofixed
in-place by the LLM and the (possibly-patched) candidate moves forward.
The full retry budget stays available for the *real* gates (LLM critic,
E2B build).
"""
from __future__ import annotations

from typing import Any

from task_quality.models import QualityReport, Violation
from task_quality.semantic import judge_and_rewrite_task_quality


# Top-level candidate field names the schema can rewrite. Keys present
# in the LLM response payload that are NOT in this set are ignored.
_REWRITABLE_FIELDS = (
    "title",
    "short_overview",
    "outcomes",
    "pre_requisites",
    "question",
)


def _apply_rewrites(candidate: dict, rewrites: dict) -> tuple[dict, dict]:
    """Return ``(patched_candidate, rewrites_actually_applied)``.

    Copies the candidate so the caller's input dict is not mutated. Only
    rewrites whose value is not ``None`` are spliced — the LLM emits
    ``null`` for fields it had no fix for.
    """
    if not rewrites:
        return dict(candidate), {}

    patched = dict(candidate)
    applied: dict = {}
    for field_name in _REWRITABLE_FIELDS:
        new_value = rewrites.get(field_name)
        if new_value is None:
            continue
        patched[field_name] = new_value
        applied[field_name] = new_value
    return patched, applied


def _build_violations(issues_found: list, rewrites_applied: dict, candidate: dict) -> list[Violation]:
    """Convert the LLM's ``issues_found`` array into :class:`Violation`s
    so callers can iterate them for logging.
    """
    violations: list[Violation] = []
    for issue in issues_found or []:
        field_path = issue.get("field_path", "")
        reason = issue.get("reason", "")
        # Top-level field for rewrite-lookup (strip any "[N]" index).
        top_level = field_path.split("[")[0]
        violations.append(
            Violation(
                field_path=field_path,
                reason=reason,
                actual_value=candidate.get(top_level),
                rewrite_applied=rewrites_applied.get(top_level),
            )
        )
    return violations


def evaluate_and_patch_task(
    candidate: dict,
    *,
    client: Any | None = None,
    model: str | None = None,
) -> tuple[dict, QualityReport]:
    """Run the consolidated judge+rewriter and splice rewrites into the
    candidate.

    Returns
    -------
    tuple[dict, QualityReport]
        ``(patched_candidate, report)``. ``patched_candidate`` is the
        input dict with any LLM-emitted rewrites spliced in (or an
        unchanged copy if no rewrites were emitted). The report carries
        the list of issues for logging.

    Raises
    ------
    Exception
        Propagates infra failures from the judge. The runner does NOT
        catch these — the caller in ``creator.py`` lets them bubble up
        and abort the run cleanly.
    """
    payload = judge_and_rewrite_task_quality(candidate, client=client, model=model)
    issues = payload.get("issues_found") or []
    rewrites_payload = payload.get("rewrites") or {}

    patched, rewrites_applied = _apply_rewrites(candidate, rewrites_payload)
    violations = _build_violations(issues, rewrites_applied, candidate)

    return patched, QualityReport(
        passed=not issues,
        violations=violations,
        rewrites_applied=rewrites_applied,
        llm_call_count=1,
    )


def run_quality_for_attempt(
    candidate: dict,
    attempt: int,
    *,
    client: Any | None = None,
    model: str | None = None,
) -> tuple[dict, QualityReport]:
    """Consumer-facing wrapper for ``generators/task/creator.py``.

    Always returns a usable candidate — either the original (when clean)
    or the patched version (when the LLM emitted rewrites). The retry
    loop in ``creator.py`` proceeds to persistence with the returned
    candidate; content-quality never triggers a retry.

    ``attempt`` is accepted for symmetry with ``run_gate_for_attempt`` and
    so future log lines can name the attempt number; the v1 implementation
    does not branch on it.
    """
    return evaluate_and_patch_task(candidate, client=client, model=model)
