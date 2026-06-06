"""Unit tests for task_quality.runner.

Runner shape: one LLM call → splice rewrites → return ``(patched_candidate,
QualityReport)``. No deterministic rules, no RETRY outcome.
"""
import json
from unittest.mock import MagicMock

import pytest


def _candidate() -> dict:
    return {
        "name": "voice-agent-eval-framework",
        "title": "voice-agent-eval-framework",   # bad: kebab slug
        "question": "Build it.",                  # bad: too short
        "pre_requisites": ["Familiarity with Python."],   # bad: generic
        "outcomes": ["• Build the harness."],     # bad: bullet glyph
        "short_overview": ["x", "y", "z", "w"],   # bad: wrong count
        "criterias": [{"name": "Voice Agent Evaluation", "proficiency": "INTERMEDIATE"}],
    }


def _empty_rewrites() -> dict:
    return {
        "title": None,
        "short_overview": None,
        "outcomes": None,
        "pre_requisites": None,
        "question": None,
    }


def _full_rewrites() -> dict:
    return {
        "title": "Design Voice Agent Eval Framework",
        "short_overview": [
            "Build an evaluation harness for a production voice agent.",
            "Score every recorded interaction against a structured rubric.",
            "Every scored interaction is persisted with rubric breakdown.",
        ],
        "outcomes": [
            "Score every voice-agent response on a structured rubric.",
        ],
        "pre_requisites": [
            "Familiarity with structured-output APIs in the OpenAI SDK.",
        ],
        "question": (
            "Build an evaluation harness that scores recorded voice-agent "
            "interactions against a structured safety + accuracy rubric, "
            "persists results, and supports re-scoring on rubric changes."
        ),
    }


def _mock_client(payload: dict) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.output_text = json.dumps(payload)
    client.responses.create.return_value = response
    return client


# ---------------------------------------------------------------------------
# evaluate_and_patch_task — clean candidate
# ---------------------------------------------------------------------------

class TestEvaluateAndPatchCleanCandidate:
    def test_no_issues_passed_true_no_rewrites(self):
        from task_quality.runner import evaluate_and_patch_task

        client = _mock_client({"issues_found": [], "rewrites": _empty_rewrites()})
        patched, report = evaluate_and_patch_task(_candidate(), client=client, model="m")

        assert report.passed is True
        assert report.violations == []
        assert report.rewrites_applied == {}
        assert report.llm_call_count == 1

    def test_candidate_unchanged_when_no_rewrites(self):
        from task_quality.runner import evaluate_and_patch_task

        client = _mock_client({"issues_found": [], "rewrites": _empty_rewrites()})
        original = _candidate()
        patched, _ = evaluate_and_patch_task(original, client=client, model="m")

        # Every key+value matches the input (copy preserved, no mutation).
        assert patched == original
        # And the original was not mutated.
        assert original["title"] == "voice-agent-eval-framework"


# ---------------------------------------------------------------------------
# evaluate_and_patch_task — rewrites spliced
# ---------------------------------------------------------------------------

class TestEvaluateAndPatchWithRewrites:
    def test_title_rewrite_spliced(self):
        from task_quality.runner import evaluate_and_patch_task

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"
        client = _mock_client({
            "issues_found": [{"field_path": "title", "reason": "kebab slug"}],
            "rewrites": rewrites,
        })

        patched, report = evaluate_and_patch_task(_candidate(), client=client, model="m")

        assert patched["title"] == "Design Voice Agent Eval Framework"
        assert report.passed is False
        assert report.rewrites_applied == {"title": "Design Voice Agent Eval Framework"}
        assert len(report.violations) == 1
        assert report.violations[0].field_path == "title"
        assert report.violations[0].rewrite_applied == "Design Voice Agent Eval Framework"

    def test_all_fields_rewritten_spliced(self):
        from task_quality.runner import evaluate_and_patch_task

        rewrites = _full_rewrites()
        issues = [
            {"field_path": "title", "reason": "kebab"},
            {"field_path": "short_overview", "reason": "wrong count"},
            {"field_path": "outcomes[0]", "reason": "glyph prefix"},
            {"field_path": "pre_requisites[0]", "reason": "generic"},
            {"field_path": "question", "reason": "too short"},
        ]
        client = _mock_client({"issues_found": issues, "rewrites": rewrites})

        patched, report = evaluate_and_patch_task(_candidate(), client=client, model="m")

        assert patched["title"] == rewrites["title"]
        assert patched["short_overview"] == rewrites["short_overview"]
        assert patched["outcomes"] == rewrites["outcomes"]
        assert patched["pre_requisites"] == rewrites["pre_requisites"]
        assert patched["question"] == rewrites["question"]
        assert report.passed is False
        assert set(report.rewrites_applied.keys()) == {
            "title", "short_overview", "outcomes", "pre_requisites", "question",
        }
        assert len(report.violations) == 5

    def test_only_failing_field_rewrites_applied(self):
        """A null in `rewrites` for an otherwise unrelated field must NOT
        replace the candidate's existing value with None."""
        from task_quality.runner import evaluate_and_patch_task

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"
        # short_overview stays None — even though the candidate has bad short_overview
        client = _mock_client({
            "issues_found": [{"field_path": "title", "reason": "kebab"}],
            "rewrites": rewrites,
        })

        original = _candidate()
        patched, report = evaluate_and_patch_task(original, client=client, model="m")

        assert patched["title"] == "Design Voice Agent Eval Framework"
        # short_overview unchanged — not blown away by None
        assert patched["short_overview"] == original["short_overview"]
        assert "short_overview" not in report.rewrites_applied

    def test_original_candidate_not_mutated(self):
        from task_quality.runner import evaluate_and_patch_task

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"
        client = _mock_client({
            "issues_found": [{"field_path": "title", "reason": "kebab"}],
            "rewrites": rewrites,
        })

        original = _candidate()
        original_title_before = original["title"]
        evaluate_and_patch_task(original, client=client, model="m")

        # Caller's dict untouched.
        assert original["title"] == original_title_before


# ---------------------------------------------------------------------------
# Infra error handling
# ---------------------------------------------------------------------------

class TestInfraErrorPropagation:
    def test_transport_error_propagates(self):
        from task_quality.runner import evaluate_and_patch_task

        client = MagicMock()
        client.responses.create.side_effect = RuntimeError("portkey down")

        with pytest.raises(Exception):
            evaluate_and_patch_task(_candidate(), client=client, model="m")


# ---------------------------------------------------------------------------
# run_quality_for_attempt — wrapper that creator.py consumes
# ---------------------------------------------------------------------------

class TestRunQualityForAttempt:
    def test_returns_patched_candidate_and_report(self):
        from task_quality.runner import run_quality_for_attempt

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"
        client = _mock_client({
            "issues_found": [{"field_path": "title", "reason": "kebab"}],
            "rewrites": rewrites,
        })

        patched, report = run_quality_for_attempt(
            _candidate(), attempt=1, client=client, model="m"
        )

        assert patched["title"] == "Design Voice Agent Eval Framework"
        assert report.passed is False
        assert report.rewrites_applied == {"title": "Design Voice Agent Eval Framework"}

    def test_clean_candidate_returns_identical(self):
        from task_quality.runner import run_quality_for_attempt

        client = _mock_client({"issues_found": [], "rewrites": _empty_rewrites()})
        original = _candidate()

        patched, report = run_quality_for_attempt(
            original, attempt=1, client=client, model="m"
        )

        assert patched == original
        assert report.passed is True
