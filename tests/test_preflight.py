"""Tests for ``task_agent_preflight.py``.

The preflight module's job is to fail fast on the classes of issue the smoke
test caught (F1/F2/F3/F4). We don't have a network or real Supabase here, so
these tests focus on the parts that can run offline.
"""

from __future__ import annotations

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
    import pytest
    with pytest.raises(ValueError):
        _parse_combo_arg("Rust")


# ---------------------------------------------------------------------------
# Global preflight
# ---------------------------------------------------------------------------


def test_global_preflight_runs_without_crashing() -> None:
    """Smoke — global preflight must always be runnable.

    May ``fail`` or ``warn`` depending on the test environment, but it must
    not raise. The test environment has no real OpenAI key (conftest sets a
    placeholder) so registry + import + brace-dryrun should still pass.
    """
    report = run_global_checks()
    # The registry, imports, and brace-dryrun checks should all pass.
    # Env-var check may fail in CI without secrets — that's by design.
    info = "\n".join(report.info + report.warnings + report.issues)
    assert "prompt registry" in info, info


def test_global_preflight_catches_registry_regression(monkeypatch) -> None:
    """If utils.py regresses to a tiny registry, preflight must fail loudly."""
    import task_agent_preflight as preflight

    # Patch the import target inside the function namespace.
    fake = {"only one entry": []}
    monkeypatch.setattr("utils._PROMPT_REGISTRY", fake)
    monkeypatch.setattr(preflight, "_MIN_REGISTRY_SIZE", 50)
    report = PreflightReport(name="t")
    preflight._check_prompt_registry(report)
    assert not report.passed
    assert any("regress" in i.lower() or "expected" in i.lower() for i in report.issues)


def test_global_preflight_catches_requirements_conflict(tmp_path, monkeypatch) -> None:
    """If requirements.txt has merge markers, preflight must fail."""
    import task_agent_preflight as preflight

    bad = tmp_path / "requirements.txt"
    bad.write_text("openai\n<<<<<<< feat\nfoo\n=======\nbar\n>>>>>>> main\n", encoding="utf-8")
    monkeypatch.setattr(preflight, "REQUIREMENTS_TXT", bad)
    report = PreflightReport(name="t")
    preflight._check_requirements_no_conflict(report)
    assert not report.passed
    assert any("conflict" in i.lower() for i in report.issues)


def test_global_preflight_catches_missing_brace_validator(monkeypatch) -> None:
    """If someone removes _simulate_format_call from validator.py, preflight catches it."""
    import task_agent_preflight as preflight
    import prompt_generator.validator as v

    # Replace with a no-op so the known-bad fixture passes through silently.
    monkeypatch.setattr(v, "_simulate_format_call", lambda src: [])
    report = PreflightReport(name="t")
    preflight._check_validator_format_dryrun(report)
    assert not report.passed
    assert any("dry-run" in i.lower() or "known-bad" in i.lower() for i in report.issues)
