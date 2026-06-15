"""The gate retry-feedback excerpt (`_failure_excerpt`) must lead with the
ROOT CAUSE + run.sh framing, collapse crash-loop / retry-counter repeats, and
exclude docker pull/extract noise — so the LLM patching its own output sees the
cause, not 3000 chars of a repeated traceback tail.
"""
from __future__ import annotations

from infra.e2b.sandbox_eval import _failure_excerpt


# A realistic broken-task run: docker noise, mongo healthy, 20 readiness retries
# (differ only by counter), the run.sh ERROR framing, then a repeated traceback.
_RETRIES = "\n".join(
    f"Attempt {i}/20: App not ready (HTTP 000000). Waiting 5s..." for i in range(1, 21)
)
_TRACEBACK = "\n".join(
    [
        "Traceback (most recent call last):",
        "  import totally_missing_module_xyz  # injected failure",
        "ModuleNotFoundError: No module named 'totally_missing_module_xyz'",
    ]
    * 8
)
_OUTPUT = (
    "#9 11.67 Extracting layers...\n" * 30
    + "MongoDB is healthy.\n"
    + _RETRIES + "\n"
    + "ERROR: Application did not respond in time. Last HTTP code: 000000\n"
    + _TRACEBACK + "\n"
    + "#9 11.67 Extracting layers...\n" * 10
)


def _summary(output: str) -> str:
    return _failure_excerpt(output).split("--- recent run.sh output ---")[0]


def test_excerpt_leads_with_root_cause_and_framing():
    summary = _summary(_OUTPUT)
    assert "ModuleNotFoundError: No module named 'totally_missing_module_xyz'" in summary
    assert "did not respond" in summary
    assert "MongoDB is healthy." in summary


def test_excerpt_collapses_retry_counter_repeats():
    """The 20 "Attempt N/20" lines differ only by a counter → digit-normalized
    dedup must keep exactly one."""
    summary = _summary(_OUTPUT)
    assert summary.count("App not ready") == 1


def test_excerpt_collapses_repeated_traceback():
    """The 8 identical ModuleNotFoundError repeats collapse to one line."""
    summary = _summary(_OUTPUT)
    assert summary.count("ModuleNotFoundError: No module named") == 1


def test_excerpt_excludes_docker_noise():
    summary = _summary(_OUTPUT)
    assert "Extracting layers" not in summary


def test_excerpt_falls_back_to_tail_when_no_error_lines():
    benign = "just some benign output line\n" * 50
    ex = _failure_excerpt(benign)
    assert "Key error" not in ex
    assert "benign output" in ex
