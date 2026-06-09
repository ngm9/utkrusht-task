"""Tests for the canonical-output-key enforcement (Fix C1) and the
feedback-aware retry (Fix A).

Background — finding F10 (2026-05-15 validation run): the agent-generated
PHP+Laravel prompt instructed the downstream LLM to emit synonym keys
(``task_title`` / ``files`` / ``context``) instead of the canonical
``name`` / ``code_files`` / ``question``. multiagent.py read every field as
empty and produced a hollow task. These tests pin the two fixes that prevent
a recurrence.
"""

from __future__ import annotations

import inspect

from generators.prompts.validator import (
    REQUIRED_JSON_SCHEMA_KEYS,
    TITLE_KEY_ALTERNATIVES,
    _missing_json_schema_keys,
)


# ---------------------------------------------------------------------------
# Fix C1 — validator requires canonical output keys
# ---------------------------------------------------------------------------

# Canonical: a prompt INSTRUCTIONS block that requests the right keys.
_CANONICAL_SCHEMA = '''
PROMPT_X_INSTRUCTIONS = """
Return JSON:
{{
  "name": "...",
  "question": "...",
  "code_files": {{"a.py": "..."}},
  "answer": "...",
  "outcomes": "...",
  "hints": "..."
}}
"""
'''

# The PHP+Laravel failure mode — synonym keys.
_SYNONYM_SCHEMA = '''
PROMPT_X_INSTRUCTIONS = """
Return JSON:
{{
  "task_title": "...",
  "context": "...",
  "files": {{"a.py": "..."}},
  "answer": "..."
}}
"""
'''


def test_required_keys_constant_covers_the_pipeline_reads() -> None:
    """multiagent.py reads code_files / question / answer — all must be required."""
    assert "code_files" in REQUIRED_JSON_SCHEMA_KEYS
    assert "question" in REQUIRED_JSON_SCHEMA_KEYS
    assert "answer" in REQUIRED_JSON_SCHEMA_KEYS


def test_canonical_schema_has_no_missing_keys() -> None:
    assert _missing_json_schema_keys(_CANONICAL_SCHEMA) == []


def test_synonym_schema_is_flagged_missing() -> None:
    missing = _missing_json_schema_keys(_SYNONYM_SCHEMA)
    # synonyms task_title/context/files do NOT satisfy name/question/code_files
    assert "code_files" in missing
    assert "question" in missing
    assert any("name" in m for m in missing)  # the name/title alternative


def test_title_alternative_either_name_or_title_satisfies() -> None:
    with_name = 'x = """{{ "name": "a", "question": "b", "code_files": {{}}, "answer": "c" }}"""'
    with_title = 'x = """{{ "title": "a", "question": "b", "code_files": {{}}, "answer": "c" }}"""'
    assert "name/title" not in " ".join(_missing_json_schema_keys(with_name))
    assert "name/title" not in " ".join(_missing_json_schema_keys(with_title))


def test_title_alternatives_constant() -> None:
    assert set(TITLE_KEY_ALTERNATIVES) == {"name", "title"}


# ---------------------------------------------------------------------------
# Fix A — feedback-aware retry
# ---------------------------------------------------------------------------


def test_generate_task_with_code_accepts_feedback_param() -> None:
    """The retry loop passes feedback= into the generator."""
    from infra.utils import generate_task_with_code
    params = inspect.signature(generate_task_with_code).parameters
    assert "feedback" in params
    # default empty so existing callers are unaffected
    assert params["feedback"].default == ""


def test_build_retry_feedback_hollow_includes_canonical_reminder() -> None:
    from generators.task import build_retry_feedback as _build_retry_feedback
    fb = _build_retry_feedback(["title is empty", "code_files is empty"], None)
    assert "hollow" in fb.lower()
    # must spell out the canonical keys so the LLM corrects the synonym mistake
    assert '"name"' in fb and '"code_files"' in fb and '"question"' in fb
    assert "task_title" in fb  # explicitly names the synonyms to avoid


def test_build_retry_feedback_eval_failure_includes_issues() -> None:
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": False, "issues": ["scenario unrealistic", "too hard"]},
        "code_eval": {"pass": True},
    }
    fb = _build_retry_feedback([], eval_info)
    assert "Task eval FAILED" in fb
    assert "scenario unrealistic" in fb
    assert "Code eval FAILED" not in fb  # code_eval passed — not mentioned


def test_build_retry_feedback_falls_back_to_feedback_string() -> None:
    """When issues[] is empty, use the free-text feedback field."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": False, "issues": [], "feedback": "needs more depth"},
        "code_eval": {"pass": True},
    }
    fb = _build_retry_feedback([], eval_info)
    assert "needs more depth" in fb


def test_build_retry_feedback_embeds_prior_candidate_json() -> None:
    """The failing candidate JSON must be embedded so the LLM patches its
    own concrete output instead of regenerating from scratch with a
    different scenario / different bugs."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True},
        "code_eval": {"pass": False, "issues": ["missing filtering on date range"]},
    }
    prior = {
        "name": "fix-assessment-attempt-viewset",
        "question": "Add filtering + N+1 fix to AssessmentAttemptViewSet",
        "code_files": {
            "app/views.py": "class AssessmentAttemptViewSet(...): pass\n",
            "app/tests/test_api.py": "from rest_framework.test import APIClient\n",
        },
    }
    fb = _build_retry_feedback([], eval_info, prior_candidate=prior)
    # The prior JSON must be embedded verbatim in a labelled block.
    assert "PRIOR FAILED CANDIDATE" in fb
    assert "fix-assessment-attempt-viewset" in fb
    assert "AssessmentAttemptViewSet" in fb
    assert "from rest_framework.test import APIClient" in fb
    # Instructions tell the model NOT to switch scenarios / NOT to regenerate.
    assert "PATCH" in fb
    assert "do NOT regenerate" in fb
    assert "do NOT switch scenarios" in fb
    # The structured eval issue must still be present.
    assert "missing filtering on date range" in fb


def test_build_retry_feedback_no_prior_candidate_omits_block() -> None:
    """When no prior candidate is provided (hollow path), the verbatim
    block is omitted but the patch instruction still appears."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    fb = _build_retry_feedback(["title is empty"], None)
    assert "PRIOR FAILED CANDIDATE" not in fb
    # Patch / no-regenerate language still present so hollow retries don't
    # accidentally re-roll a new scenario either.
    assert "PATCH" in fb


def test_build_retry_feedback_includes_sandbox_verdict_when_present() -> None:
    """Gate failures end up on candidate_eval['sandbox_eval']; build_retry_feedback
    must surface the verdict + stdout tail so the LLM sees the actual error."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True},
        "code_eval": {"pass": True},
        "sandbox_eval": {
            "passed": False,
            "skipped": False,
            "verdict": "collection_error",
            "detail": "pytest hit a collection error",
            "stdout_tail": "ImproperlyConfigured: Requested setting REST_FRAMEWORK",
        },
    }
    fb = _build_retry_feedback([], eval_info, prior_candidate={"name": "x"})
    assert "E2B sandbox gate FAILED (collection_error)" in fb
    assert "pytest hit a collection error" in fb
    assert "ImproperlyConfigured" in fb


def test_build_retry_feedback_prefers_blocking_issues_over_legacy_issues() -> None:
    """Layer B: blocking_issues (new schema) drives retry over legacy issues
    field. If both populated, blocking_issues wins (it's the authoritative one)."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True},
        "code_eval": {
            "pass": False,
            "blocking_issues": ["Criterion 2: stubs are missing"],
            "suggestions": ["consider adding caching"],  # MUST NOT appear in feedback
            "issues": ["legacy field — should be ignored when blocking_issues present"],
        },
    }
    fb = _build_retry_feedback([], eval_info, prior_candidate={"name": "x"})
    assert "Criterion 2: stubs are missing" in fb
    # Suggestions never make it into retry feedback
    assert "consider adding caching" not in fb
    # Legacy `issues` is ignored when blocking_issues is present
    assert "legacy field" not in fb


def test_build_retry_feedback_falls_back_to_legacy_issues_when_no_blocking() -> None:
    """Layer B back-compat: if a critic only emits the legacy `issues` field
    (e.g. mocked test or pre-migration caller), the feedback still works."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True},
        "code_eval": {
            "pass": False,
            # No blocking_issues — legacy shape only
            "issues": ["legacy issue text"],
        },
    }
    fb = _build_retry_feedback([], eval_info)
    assert "legacy issue text" in fb


def test_build_retry_feedback_truncates_huge_prior_candidate() -> None:
    """Prior candidates over the char cap must be truncated to keep the
    next LLM call within token budget."""
    from generators.task import build_retry_feedback as _build_retry_feedback
    from generators.task.evaluator import _PRIOR_CANDIDATE_CHAR_CAP
    huge_value = "x" * (_PRIOR_CANDIDATE_CHAR_CAP * 2)
    prior = {"name": "huge", "code_files": {"big.py": huge_value}}
    fb = _build_retry_feedback([], None, prior_candidate=prior)
    assert "[truncated;" in fb
    # The feedback string overall must still be bounded — the cap + a few
    # KB of system+verdict text. Anything close to 2x the cap = bug.
    assert len(fb) < _PRIOR_CANDIDATE_CHAR_CAP + 5_000
