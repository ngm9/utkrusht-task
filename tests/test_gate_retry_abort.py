"""No-progress abort for the task-gen retry loop (2026-06-19).

If the E2B gate fails with the SAME verdict two attempts running, the failure is
environmental/scaffold (e.g. a run.sh import path) — regenerating won't fix it,
so the loop must abort instead of burning another expensive task-gen call.
"""

from __future__ import annotations


def test_no_progress_when_same_verdict():
    from generators.task.creator import _gate_no_progress
    ev = {"sandbox_eval": {"verdict": "runsh_failed"}}
    abort, verdict = _gate_no_progress(ev, "runsh_failed")
    assert abort is True and verdict == "runsh_failed"


def test_progress_when_verdict_changes():
    from generators.task.creator import _gate_no_progress
    ev = {"sandbox_eval": {"verdict": "runsh_timeout"}}
    abort, verdict = _gate_no_progress(ev, "runsh_failed")
    assert abort is False and verdict == "runsh_timeout"


def test_first_attempt_never_aborts():
    from generators.task.creator import _gate_no_progress
    ev = {"sandbox_eval": {"verdict": "runsh_failed"}}
    abort, verdict = _gate_no_progress(ev, None)  # no prior verdict
    assert abort is False and verdict == "runsh_failed"


def test_missing_sandbox_eval_does_not_abort():
    from generators.task.creator import _gate_no_progress
    abort, verdict = _gate_no_progress({}, "runsh_failed")
    assert abort is False and verdict is None


# Fix 3 — targeted dep-error hint in the retry feedback.

def test_retry_feedback_adds_dep_hint_on_module_not_found():
    from generators.task import build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True}, "code_eval": {"pass": True},
        "sandbox_eval": {
            "passed": False, "skipped": False, "verdict": "runsh_failed",
            "detail": "run.sh exited 1",
            "stdout_tail": "Traceback (most recent call last):\nModuleNotFoundError: No module named 'psycopg'",
        },
    }
    fb = build_retry_feedback([], eval_info, prior_candidate={"name": "x"})
    assert "pip install -q -r requirements.txt" in fb
    assert "dependency error" in fb.lower()


def test_retry_feedback_no_dep_hint_for_non_module_failure():
    from generators.task import build_retry_feedback
    eval_info = {
        "task_eval": {"pass": True}, "code_eval": {"pass": True},
        "sandbox_eval": {
            "passed": False, "skipped": False, "verdict": "runsh_timeout",
            "detail": "timeout", "stdout_tail": "docker compose up hung waiting for health",
        },
    }
    fb = build_retry_feedback([], eval_info, prior_candidate={"name": "x"})
    assert "gate dependency error" not in fb.lower()
