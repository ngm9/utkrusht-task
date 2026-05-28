"""Unit tests for the E2B sandbox eval gate — pure logic, no sandbox boot.

The live integration test (booting utkrusht-python and feeding it real
code_files) is run separately — it needs E2B and is too slow for the suite.
"""
import os
from unittest.mock import patch

from infra.classifier.runtime import TaskTemplateMatch
from infra.e2b.sandbox_eval import (
    SandboxEvalResult,
    _classify_pytest,
    run_sandbox_eval,
    sandbox_eval_enabled,
)
from generators.task.runtime_resolver import ResolvedPlan, TemplateSpec


def _python_template() -> TemplateSpec:
    return TemplateSpec(
        template_id="utkrusht-python",
        primary_runtime="python",
        personas=["backend"],
        eval_methods=["test_suite"],
        capabilities={},
        build_cmd="pip install -r requirements.txt",
        test_cmd="python -m pytest",
        compile_cmd="python -m compileall -q .",
    )


def _plan(template: TemplateSpec | None) -> ResolvedPlan:
    """Build a ResolvedPlan that mirrors what ``resolve_plan`` returns —
    template is None for the no_template skip path."""
    match = (
        TaskTemplateMatch(template_id=template.template_id, persona="backend",
                          confidence=0.9)
        if template else
        TaskTemplateMatch(no_match_reason="no template", confidence=0.5)
    )
    return ResolvedPlan(
        combo_key="test-combo",
        match=match,
        template=template,
    )


# --- _classify_pytest -------------------------------------------------------

def test_classify_all_passed():
    r = _classify_pytest(0, "=== 5 passed in 1.2s ===")
    assert r.passed and r.verdict == "ok"


def test_classify_some_failed_still_passes_gate():
    # exit 1 = tests failed, but they COMPILED + RAN. A generated starter has
    # by-design failing tests — the gate must not reject that.
    r = _classify_pytest(1, "=== 2 passed, 3 failed in 0.8s ===")
    assert r.passed and r.verdict == "ok"


def test_classify_collection_error_fails_gate():
    out = ("ERROR collecting test_app.py\n"
           "ImportError: cannot import name 'foo'\n=== 1 error in 0.3s ===")
    r = _classify_pytest(2, out)
    assert not r.passed and r.verdict == "collection_error"


def test_classify_collection_error_even_with_some_passes():
    # A collection error in one file alongside passing tests in another is
    # still a gate failure — something doesn't compile.
    out = ("errors during collection\nERROR collecting test_b.py\n"
           "=== 1 passed, 1 error in 0.5s ===")
    r = _classify_pytest(1, out)
    assert not r.passed and r.verdict == "collection_error"


def test_classify_no_tests_fails_gate():
    r = _classify_pytest(5, "=== no tests ran in 0.1s ===")
    assert not r.passed and r.verdict == "no_tests"


def test_classify_internal_error_fails_gate():
    r = _classify_pytest(3, "INTERNALERROR> ...")
    assert not r.passed and r.verdict == "test_run_error"


# --- run_sandbox_eval skip paths (no sandbox boot) --------------------------

def test_skips_no_template_in_plan():
    r = run_sandbox_eval({"app.py": "x"}, _plan(None))
    assert r.skipped and r.verdict == "no_template"


def test_skips_empty_code():
    r = run_sandbox_eval({}, _plan(_python_template()))
    assert r.skipped and r.verdict == "no_code"


def test_skips_none_plan():
    r = run_sandbox_eval({"app.py": "x"}, None)
    assert r.skipped and r.verdict == "no_template"


# --- flag + result shape ----------------------------------------------------

def test_sandbox_eval_enabled_flag():
    for truthy in ("true", "1", "yes", "TRUE"):
        with patch.dict(os.environ, {"SANDBOX_EVAL_ENABLED": truthy}):
            assert sandbox_eval_enabled() is True
    for falsy in ("", "false", "0", "no"):
        with patch.dict(os.environ, {"SANDBOX_EVAL_ENABLED": falsy}):
            assert sandbox_eval_enabled() is False


def test_as_dict_shape():
    r = SandboxEvalResult(passed=False, verdict="collection_error", detail="boom")
    assert r.as_dict() == {
        "passed": False, "skipped": False,
        "verdict": "collection_error", "detail": "boom",
        "stdout_tail": "",
    }


def test_as_dict_includes_stdout_tail():
    r = SandboxEvalResult(verdict="ok", detail="ran", stdout_tail="=== 3 passed ===")
    assert r.as_dict()["stdout_tail"] == "=== 3 passed ==="
