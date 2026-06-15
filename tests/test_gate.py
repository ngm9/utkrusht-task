"""Unit tests for generators.task.gate — the retry-loop policy wrapper.

These cover the 4 outcomes returned by ``run_gate_for_attempt`` so the
create_task loop can rely on each branch behaving as documented.
"""
from unittest.mock import patch

from infra.e2b.sandbox_eval import SandboxEvalResult
from infra.classifier.runtime import TaskTemplateMatch
from generators.task.gate import GateOutcome, run_gate_for_attempt
from generators.task.runtime_resolver import ResolvedPlan, TemplateSpec


def _plan(template_id: str = "utkrusht-python", primary_runtime: str = "python") -> ResolvedPlan:
    match = TaskTemplateMatch(template_id=template_id, persona="backend", confidence=0.9)
    tpl = TemplateSpec(
        template_id=template_id,
        primary_runtime=primary_runtime,
        personas=["backend"],
        eval_methods=["test_suite"],
        capabilities={},
        build_cmd="pip install -r requirements.txt",
        test_cmd="python -m pytest",
    )
    return ResolvedPlan(combo_key="x", match=match, template=tpl)


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
            _plan("utkrusht-java", "java"),
            {"code_files": {"a.java": "x"}}, candidate_eval, attempt=1,
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


# ---------------------------------------------------------------------------
# infra_error retry — a transient sandbox death (StreamReset) must not
# silently skip the deployability check; retry it a bounded number of times.
# ---------------------------------------------------------------------------


def test_infra_error_is_retried_then_uses_real_verdict(monkeypatch):
    """A transient infra_error (e.g. sandbox StreamReset mid-run) is retried;
    once a real verdict comes back the gate uses it instead of skipping."""
    monkeypatch.setattr("generators.task.gate._INFRA_RETRY_BACKOFF_S", 0.0)
    flake = SandboxEvalResult(skipped=True, verdict="infra_error", detail="StreamReset")
    good = SandboxEvalResult(passed=True, skipped=False, verdict="ready", detail="run.sh exit 0")
    candidate_eval: dict = {}
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval",
               side_effect=[flake, flake, good]) as mock:
        outcome, fb = run_gate_for_attempt(
            _plan(), {"code_files": {"a.py": "x"}}, candidate_eval, attempt=1,
        )
    assert outcome == GateOutcome.PASS
    assert mock.call_count == 3          # 2 flakes + 1 real verdict
    assert candidate_eval["sandbox_eval"]["verdict"] == "ready"


def test_infra_error_persisting_is_skipped_after_bounded_retries(monkeypatch):
    """If every attempt flakes, the gate gives up as a SKIP (never blocks) —
    but only after the bounded number of retries, not on the first flake."""
    monkeypatch.setattr("generators.task.gate._INFRA_RETRY_BACKOFF_S", 0.0)
    monkeypatch.setattr("generators.task.gate._INFRA_GATE_RETRIES", 2)
    flake = SandboxEvalResult(skipped=True, verdict="infra_error", detail="StreamReset")
    candidate_eval: dict = {}
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=flake) as mock:
        outcome, fb = run_gate_for_attempt(
            _plan(), {"code_files": {"a.py": "x"}}, candidate_eval, attempt=1,
        )
    assert outcome == GateOutcome.SKIPPED
    assert mock.call_count == 3          # 1 initial + 2 retries
    assert candidate_eval["sandbox_eval"]["verdict"] == "infra_error"


def test_deterministic_skip_is_not_retried(monkeypatch):
    """A deterministic skip (no_template) must NOT be retried — retrying can't
    change it and would waste sandbox minutes."""
    monkeypatch.setattr("generators.task.gate._INFRA_RETRY_BACKOFF_S", 0.0)
    skip = SandboxEvalResult(skipped=True, verdict="no_template", detail="no template")
    with patch("generators.task.gate.sandbox_eval_enabled", return_value=True), \
         patch("generators.task.gate.run_sandbox_eval", return_value=skip) as mock:
        outcome, _ = run_gate_for_attempt(
            _plan(), {"code_files": {"a.py": "x"}}, {}, attempt=1,
        )
    assert outcome == GateOutcome.SKIPPED
    assert mock.call_count == 1
