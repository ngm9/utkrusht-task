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
