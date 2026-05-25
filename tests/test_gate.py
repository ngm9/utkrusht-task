"""Unit tests for task_generation.gate — the retry-loop policy wrapper.

These cover the 4 outcomes returned by ``run_gate_for_attempt`` so the
create_task loop can rely on each branch behaving as documented.
"""
from unittest.mock import patch

from infra.e2b.sandbox_eval import SandboxEvalResult
from infra.classifier.runtime import TaskRuntime
from generators.task.gate import GateOutcome, run_gate_for_attempt
from generators.task.runtime_resolver import ResolvedPlan, TemplateSpec


def _plan(runtime: str = "python") -> ResolvedPlan:
    tr = TaskRuntime(runtime=runtime, kind="app")
    tpl = TemplateSpec(
        name=f"utkrusht-{runtime}",
        build_cmd="pip install -r requirements.txt",
        test_cmd="python -m pytest",
    )
    return ResolvedPlan(combo_key="x", task_runtime=tr, template=tpl)


def test_disabled_when_env_flag_off():
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=False):
        outcome, fb = run_gate_for_attempt(_plan(), {}, {}, attempt=1)
    assert outcome == GateOutcome.DISABLED
    assert fb == ""


def test_pass_outcome_proceeds_to_storage():
    sb = SandboxEvalResult(
        passed=True, skipped=False, verdict="ok",
        detail="test suite compiled and executed",
    )
    candidate_eval: dict = {}
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=sb):
        outcome, fb = run_gate_for_attempt(
            _plan(), {"code_files": {"a.py": "x"}}, candidate_eval, attempt=1,
        )
    assert outcome == GateOutcome.PASS
    assert fb == ""
    # The verdict dict is mutated onto candidate_eval — the loop reads it later.
    assert candidate_eval["sandbox_eval"]["verdict"] == "ok"


def test_skipped_outcome_when_no_template():
    sb = SandboxEvalResult(
        passed=True, skipped=True, verdict="no_template",
        detail="no template for runtime='java'",
    )
    candidate_eval: dict = {}
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=sb):
        outcome, fb = run_gate_for_attempt(
            _plan("java"), {"code_files": {"a.java": "x"}}, candidate_eval, attempt=1,
        )
    assert outcome == GateOutcome.SKIPPED
    assert fb == ""


def test_retry_outcome_includes_feedback_with_verdict_and_tail():
    sb = SandboxEvalResult(
        passed=False, skipped=False, verdict="collection_error",
        detail="pytest hit a collection error — a test or source file does not compile",
        stdout_tail="SyntaxError: invalid syntax at line 5",
    )
    candidate_eval: dict = {
        "task_eval": {"pass": True},
        "code_eval": {"pass": True},
    }
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=sb):
        outcome, fb = run_gate_for_attempt(
            _plan(), {"code_files": {"t.py": "x"}}, candidate_eval, attempt=2,
        )
    assert outcome == GateOutcome.RETRY
    assert "collection_error" in fb
    assert "does not compile" in fb
    # The verdict landed on candidate_eval — caller can still persist it.
    assert candidate_eval["sandbox_eval"]["verdict"] == "collection_error"


def test_plan_none_passes_none_plan_to_gate():
    # If classifier failed and the plan is None, the gate still runs (with
    # plan=None) and returns no_template skip — never crashes.
    sb = SandboxEvalResult(skipped=True, verdict="no_template", detail="")
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=sb) as mock:
        outcome, _ = run_gate_for_attempt(None, {"code_files": {"a.py": "x"}}, {}, attempt=1)
    assert outcome == GateOutcome.SKIPPED
    # plan arg to run_sandbox_eval is None when the caller's plan is None
    assert mock.call_args.args[1] is None
