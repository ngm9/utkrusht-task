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


def _raw_tail(output: str) -> str:
    parts = _failure_excerpt(output).split("--- recent run.sh output ---")
    return parts[1] if len(parts) > 1 else parts[0]


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


def test_raw_tail_excludes_docker_noise():
    """The raw-output tail half of the excerpt must ALSO drop docker-pull noise.
    For a docker-compose task the literal last-N-chars is almost entirely
    Extracting/Pull-complete spam (it streams to stderr → end of the combined
    output), which buries the real run.sh signal."""
    tail = _raw_tail(_OUTPUT)
    assert "Extracting layers" not in tail
    # ...and the tail still carries real run.sh signal, not just empty bytes.
    assert "ModuleNotFoundError" in tail or "did not respond" in tail


def test_raw_tail_drops_trailing_layer_id_lines():
    """Bare layer-id progress lines (e.g. `a1b2c3d4e5f6  Pulling`) are dropped
    so they don't crowd out the tail."""
    out = (
        "real error: connection refused on :5432\n"
        + "a1b2c3d4e5f6   Downloading [===>   ]  12MB/40MB\n" * 50
    )
    tail = _raw_tail(out)
    assert "Downloading" not in tail
    assert "connection refused" in tail


def test_excerpt_falls_back_to_tail_when_no_error_lines():
    benign = "just some benign output line\n" * 50
    ex = _failure_excerpt(benign)
    assert "Key error" not in ex
    assert "benign output" in ex


def test_fallback_excludes_docker_noise():
    """No error lines → plain-tail fallback, but it must still drop docker
    noise so a lone benign signal isn't buried under pull spam."""
    benign = (
        "Pull complete\n" * 100
        + "service started on port 8080\n"
        + "Extracting\n" * 100
    )
    ex = _failure_excerpt(benign)
    assert "Key error" not in ex
    assert "service started on port 8080" in ex
    assert "Pull complete" not in ex
    assert "Extracting" not in ex
