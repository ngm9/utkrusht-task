"""Unit tests for task_quality.semantic.

Single consolidated LLM call that BOTH judges the candidate AND emits
rewrites for every failing field. Tests use a mocked LLM client whose
``.responses.create(...)`` returns a fixed structured-output payload, so
the parser logic + Violation construction + rewrite extraction can be
exercised without any network call.
"""
import json
from unittest.mock import MagicMock

import pytest


def _candidate() -> dict:
    """Minimal task context the judge prompt needs."""
    return {
        "name": "voice-agent-eval-framework",
        "title": "voice-agent-eval-framework",   # intentionally bad
        "question": "Build it.",                  # intentionally too short
        "pre_requisites": ["Familiarity with Python."],
        "outcomes": ["• Build it."],
        "short_overview": ["x", "y", "z", "w"],   # wrong count
        "criterias": [
            {"name": "Voice Agent Evaluation", "proficiency": "INTERMEDIATE"},
        ],
    }


def _empty_rewrites() -> dict:
    return {
        "title": None,
        "short_overview": None,
        "outcomes": None,
        "pre_requisites": None,
        "question": None,
    }


def _mock_client_returning(payload: dict) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.output_text = json.dumps(payload)
    client.responses.create.return_value = response
    return client


# ---------------------------------------------------------------------------
# Happy path: clean task
# ---------------------------------------------------------------------------

class TestJudgeAndRewriteHappyPath:
    def test_clean_task_returns_empty_issues_and_no_rewrites(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        payload = {"issues_found": [], "rewrites": _empty_rewrites()}
        client = _mock_client_returning(payload)

        result = judge_and_rewrite_task_quality(_candidate(), client=client, model="m")

        assert result["issues_found"] == []
        assert result["rewrites"] == _empty_rewrites()

    def test_exactly_one_llm_call(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        client = _mock_client_returning({"issues_found": [], "rewrites": _empty_rewrites()})
        judge_and_rewrite_task_quality(_candidate(), client=client, model="m")
        assert client.responses.create.call_count == 1


# ---------------------------------------------------------------------------
# Issues + rewrites returned for failing fields
# ---------------------------------------------------------------------------

class TestRewritesParsed:
    def test_title_issue_carries_rewrite(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"

        payload = {
            "issues_found": [
                {"field_path": "title", "reason": "kebab-case slug, not human-readable Title Case"},
            ],
            "rewrites": rewrites,
        }
        client = _mock_client_returning(payload)

        result = judge_and_rewrite_task_quality(_candidate(), client=client, model="m")

        assert len(result["issues_found"]) == 1
        assert result["issues_found"][0]["field_path"] == "title"
        assert result["rewrites"]["title"] == "Design Voice Agent Eval Framework"
        # Untouched fields stay null
        assert result["rewrites"]["short_overview"] is None
        assert result["rewrites"]["question"] is None

    def test_multiple_fields_with_rewrites(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        rewrites = _empty_rewrites()
        rewrites["title"] = "Design Voice Agent Eval Framework"
        rewrites["short_overview"] = [
            "Build an evaluation harness for a production voice agent.",
            "Score every recorded interaction against a structured rubric.",
            "Every scored interaction is persisted with rubric breakdown.",
        ]
        rewrites["outcomes"] = [
            "Score every voice-agent response on a structured rubric.",
            "Persist scored interactions to postgres.",
        ]

        payload = {
            "issues_found": [
                {"field_path": "title", "reason": "kebab slug"},
                {"field_path": "short_overview", "reason": "wrong count (4); must be 3"},
                {"field_path": "outcomes[0]", "reason": "starts with `•` bullet glyph"},
            ],
            "rewrites": rewrites,
        }
        client = _mock_client_returning(payload)

        result = judge_and_rewrite_task_quality(_candidate(), client=client, model="m")

        assert len(result["issues_found"]) == 3
        assert result["rewrites"]["title"] == "Design Voice Agent Eval Framework"
        assert len(result["rewrites"]["short_overview"]) == 3
        assert len(result["rewrites"]["outcomes"]) == 2


# ---------------------------------------------------------------------------
# Error handling: infra failures propagate (research.md Decision 7)
# ---------------------------------------------------------------------------

class TestInfraErrorPropagation:
    def test_transport_error_raises(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        client = MagicMock()
        client.responses.create.side_effect = RuntimeError("portkey down")

        with pytest.raises(Exception) as exc_info:
            judge_and_rewrite_task_quality(_candidate(), client=client, model="m")
        assert "judge" in str(exc_info.value).lower() or "portkey down" in str(exc_info.value)

    def test_unparseable_response_raises(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        client = MagicMock()
        response = MagicMock()
        response.output_text = "not valid json {{{"
        client.responses.create.return_value = response

        with pytest.raises(Exception):
            judge_and_rewrite_task_quality(_candidate(), client=client, model="m")

    def test_empty_response_raises(self):
        from task_quality.semantic import judge_and_rewrite_task_quality

        client = MagicMock()
        response = MagicMock()
        response.output_text = None
        client.responses.create.return_value = response

        with pytest.raises(Exception):
            judge_and_rewrite_task_quality(_candidate(), client=client, model="m")
