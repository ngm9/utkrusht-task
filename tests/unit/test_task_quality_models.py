"""Unit tests for task_quality.models."""
import pytest


# ---------------------------------------------------------------------------
# Violation
# ---------------------------------------------------------------------------

class TestViolation:
    def test_construction_with_required_fields(self):
        from task_quality.models import Violation

        v = Violation(field_path="title", reason="kebab-case slug")
        assert v.field_path == "title"
        assert v.reason == "kebab-case slug"
        assert v.actual_value is None
        assert v.rewrite_applied is None

    def test_construction_with_actual_and_rewrite(self):
        from task_quality.models import Violation

        v = Violation(
            field_path="title",
            reason="kebab-case slug",
            actual_value="voice-agent-eval-framework",
            rewrite_applied="Design Voice Agent Eval Framework",
        )
        assert v.actual_value == "voice-agent-eval-framework"
        assert v.rewrite_applied == "Design Voice Agent Eval Framework"

    def test_is_frozen(self):
        from dataclasses import FrozenInstanceError

        from task_quality.models import Violation

        v = Violation(field_path="x", reason="r")
        with pytest.raises(FrozenInstanceError):
            v.field_path = "mutated"  # type: ignore[misc]

    def test_value_equality(self):
        from task_quality.models import Violation

        a = Violation(field_path="x", reason="r", actual_value=1, rewrite_applied=2)
        b = Violation(field_path="x", reason="r", actual_value=1, rewrite_applied=2)
        assert a == b


# ---------------------------------------------------------------------------
# QualityReport
# ---------------------------------------------------------------------------

class TestQualityReport:
    def test_passing_report_defaults(self):
        from task_quality.models import QualityReport

        report = QualityReport(passed=True)
        assert report.passed is True
        assert report.violations == []
        assert report.rewrites_applied == {}
        assert report.llm_call_count == 0

    def test_full_construction(self):
        from task_quality.models import QualityReport, Violation

        v = Violation(field_path="title", reason="kebab slug")
        report = QualityReport(
            passed=False,
            violations=[v],
            rewrites_applied={"title": "Design X"},
            llm_call_count=1,
        )

        assert report.passed is False
        assert report.violations == [v]
        assert report.rewrites_applied == {"title": "Design X"}
        assert report.llm_call_count == 1
