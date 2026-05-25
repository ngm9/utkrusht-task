"""Pins the eval-gate + hollow-task guard in ``multiagent.py``.

Critical because before Fix 1 + Fix 2 (coordinator findings F8 + F9), hollow
Supabase rows could be created even when both eval critics returned
``pass=False`` — the worst kind of silent failure.
"""

from __future__ import annotations

import pytest

from evals import EvalGateError, MAX_EVAL_RETRIES


def test_max_eval_retries_default() -> None:
    """Don't accidentally drop the retry budget to zero."""
    assert MAX_EVAL_RETRIES >= 1, (
        f"MAX_EVAL_RETRIES={MAX_EVAL_RETRIES} would disable retries; "
        "the eval gate needs at least one retry budget."
    )


def test_eval_gate_error_carries_last_verdicts() -> None:
    last = {
        "task_eval": {"pass": False, "issues": ["x"]},
        "code_eval": {"pass": False, "issues": ["y"]},
    }
    e = EvalGateError(3, last)
    assert e.attempts == 3
    assert e.last_eval_info["task_eval"]["pass"] is False
    assert e.last_eval_info["code_eval"]["pass"] is False
    # Message should be inspectable
    s = str(e)
    assert "3 attempt" in s
    assert "task_eval.pass=False" in s


def test_hollow_task_detector_catches_empty_fields() -> None:
    """A task is hollow if title/question/code are missing or empty."""
    from task_generation import is_task_hollow
    cases = [
        {},
        {"title": ""},
        {"title": "X", "question": ""},
        {"title": "X", "question": "Y", "code_files": {}},
        {"title": "X", "question": "Y"},  # missing code_files
    ]
    for case in cases:
        hollow, reasons = is_task_hollow(case)
        assert hollow, f"Expected hollow for {case}; got passed-through"
        assert reasons, f"Expected reasons for {case}"


def test_hollow_task_detector_accepts_full_task() -> None:
    from task_generation import is_task_hollow
    good = {
        "title": "Fix the broken parser",
        "question": "Implement parse_payment so that ...",
        "code_files": {"src/main.py": "...", "Cargo.toml": "..."},
    }
    hollow, reasons = is_task_hollow(good)
    assert not hollow, f"Full task wrongly classified hollow: {reasons}"


def test_hollow_task_detector_accepts_name_as_title_alias() -> None:
    """task_generation historically uses ``name`` as a fallback for ``title``."""
    from task_generation import is_task_hollow
    payload = {
        "name": "X",   # title alias
        "question": "Y",
        "code_files": {"a.py": "..."},
    }
    hollow, _ = is_task_hollow(payload)
    assert not hollow
