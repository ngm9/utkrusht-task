"""Guard: the prompt generator must teach the run.sh DEPLOYABILITY contract.

A build-it task ships a test suite the candidate must make pass — the fresh
checkout's tests fail BY DESIGN. The E2B gate runs the task's own ``run.sh``
and reads its exit code (0 = ready, non-zero = ``runsh_failed`` → wasted retry).
If the generated ``run.sh`` wraps ``pytest`` in a bare ``set -e``, a red test
(pytest rc=1) makes ``run.sh`` exit 1 → the gate falsely fails a perfectly
deployable task (observed in run-20260616T042756Z).

The legacy fallback path (``_classify_pytest``) already treats pytest rc∈{0,1}
as success; this locks in that the *generator instructions* push the run.sh
path to mirror that same contract, so it can't silently regress.
"""
import inspect

from generators.prompts.agent import GeneratePromptSignature


def _instructions() -> str:
    return (
        getattr(GeneratePromptSignature, "instructions", None)
        or inspect.getdoc(GeneratePromptSignature)
        or ""
    )


def test_generator_prescribes_runsh_deployability_contract():
    text = _instructions()
    assert "DEPLOYABILITY" in text, (
        "generator must frame run.sh as a deployability probe, not a pass/fail gate"
    )
    # It must say the test suite running-but-failing is still a success.
    low = text.lower()
    assert "even if tests fail" in low or "failing-as-designed" in low, (
        "generator must tell run.sh to exit 0 when tests RAN even if they FAILED"
    )


def test_generator_forbids_bare_set_e_around_tests():
    """The exact failure mode: `set -e; pytest` conflates a designed red test
    with a broken scaffold. The instruction must steer away from it."""
    low = _instructions().lower()
    assert "set -e" in low and "conflate" in low, (
        "generator must warn against a bare `set -e` that conflates a designed "
        "test failure with a broken scaffold"
    )


def test_generator_pins_pytest_exit_code_mapping():
    """The concrete pytest contract (rc 0/1 → exit 0; >=2 → non-zero) must be
    spelled out so the run.sh path mirrors `_classify_pytest`."""
    text = _instructions()
    assert "pytest" in text.lower()
    # rc 0 and 1 succeed; >= 2 (and 5 = no tests) fail.
    assert "exits 0" in text and ">= 2" in text and "no tests" in text.lower()
