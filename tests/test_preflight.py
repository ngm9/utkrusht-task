"""Tests for ``task_agent_preflight.py``.

The preflight module fails fast on environment problems before the expensive
pipeline runs. After the trim (env + imports globally, Supabase + retriever
per-combo), these tests cover the report shape, the CLI combo parser, and a
smoke run of the global checks. Network-dependent checks aren't exercised here.
"""

from __future__ import annotations

import pytest

from task_agent_preflight import (
    PreflightReport,
    _parse_combo_arg,
    run_global_checks,
)


# ---------------------------------------------------------------------------
# Report shape
# ---------------------------------------------------------------------------


def test_preflight_report_starts_passing() -> None:
    r = PreflightReport(name="x")
    assert r.passed
    assert not r.issues


def test_preflight_report_fail_flips_state() -> None:
    r = PreflightReport(name="x")
    r.fail("boom")
    assert not r.passed
    assert "boom" in r.issues


def test_preflight_report_warn_does_not_flip_state() -> None:
    r = PreflightReport(name="x")
    r.warn("yellow")
    assert r.passed
    assert "yellow" in r.warnings


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------


def test_parse_combo_single_competency() -> None:
    names, level = _parse_combo_arg("Rust:BASIC")
    assert names == ["Rust"]
    assert level == "BASIC"


def test_parse_combo_multi_competency() -> None:
    names, level = _parse_combo_arg("Python, Pinecone:INTERMEDIATE")
    assert names == ["Python", "Pinecone"]
    assert level == "INTERMEDIATE"


def test_parse_combo_with_special_chars_in_name() -> None:
    """Competency names can contain dashes/spaces (e.g. 'Java - Hibernate')."""
    names, level = _parse_combo_arg("Java, Java - Hibernate:BASIC")
    assert names == ["Java", "Java - Hibernate"]


def test_parse_combo_rejects_missing_level() -> None:
    with pytest.raises(ValueError):
        _parse_combo_arg("Rust")


# ---------------------------------------------------------------------------
# Global preflight
# ---------------------------------------------------------------------------


def test_global_preflight_runs_without_crashing() -> None:
    """Smoke — global preflight (imports + env vars) must always be runnable.

    It may ``fail`` or ``warn`` depending on the environment (missing secrets
    in CI), but it must never raise, and must return a named PreflightReport.
    """
    report = run_global_checks()
    assert isinstance(report, PreflightReport)
    assert report.name == "global"
