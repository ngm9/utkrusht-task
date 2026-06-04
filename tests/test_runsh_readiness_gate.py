"""The ``run.sh`` readiness gate — the new build-it deployability check.

Pure-logic tests around ``run_sandbox_eval``'s contract: it boots a sandbox,
writes code + ``run.sh``, runs ``run.sh``, and maps the exit code to a
verdict (``ready`` / ``runsh_failed`` / ``runsh_timeout``). The integration
test (real E2B boot) is slow and lives elsewhere; this file pins the
*contract* the retry loop depends on.

Critical invariants pinned here:

* ``run.sh`` IS the gate — exit 0 = ready; non-zero = retry.
* The gate NEVER injects an API key (LLM-free at the gate; the key-gated
  ping inside ``run.sh`` is the candidate's, on the candidate's key, in
  the candidate's session).
* The legacy build/test path is preserved as a fallback ONLY when
  ``run.sh`` is absent AND the template carries a build/test recipe. New
  build-it tasks always ship ``run.sh``.
* A wall-clock trip surfaces as ``runsh_timeout``, not a crash.
* Sandbox boot failure surfaces as ``infra_error`` SKIP (never blocks).

The tests below stub the E2B ``Sandbox`` via ``sys.modules`` (the source
imports it lazily inside the function) so they run hermetically in CI.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock

from infra.classifier.runtime import TaskTemplateMatch
from infra.e2b.sandbox_eval import SandboxEvalResult, run_sandbox_eval
from generators.task.runtime_resolver import ResolvedPlan, TemplateSpec


# ---------------------------------------------------------------------------
# Test scaffolding
# ---------------------------------------------------------------------------


def _python_template(*, with_legacy_recipe: bool = True,
                    with_compose: bool = False) -> TemplateSpec:
    return TemplateSpec(
        template_id="utkrusht-python",
        primary_runtime="python",
        personas=["backend", "agent_engineer"],
        eval_methods=["test_suite"],
        capabilities={"frameworks": ["langgraph", "litellm", "fastapi"]},
        build_cmd="pip install -r requirements.txt" if with_legacy_recipe else None,
        test_cmd="python -m pytest -q" if with_legacy_recipe else None,
        compile_cmd="python -m compileall -q ." if with_legacy_recipe else None,
    )


def _plan(template: TemplateSpec | None) -> ResolvedPlan:
    match = (
        TaskTemplateMatch(template_id=template.template_id, persona="agent_engineer",
                          confidence=0.9)
        if template else
        TaskTemplateMatch(no_match_reason="no template", confidence=0.5)
    )
    return ResolvedPlan(combo_key="test-combo", match=match, template=template)


def _fake_sandbox(run_sh_exit: int = 0, run_sh_output: str = "ready\n"):
    """Build a mock sandbox whose ``bash run.sh`` returns the given exit.

    Also exposes the call-log so tests can assert what was written, what
    the chmod call looked like, and crucially: that no API key was set.
    """
    sb = MagicMock()
    calls = {"commands": [], "writes": []}
    sb.files.write.side_effect = lambda p, c: calls["writes"].append((p, c))

    def _run(cmd, timeout=None, cwd=None, user=None):
        calls["commands"].append({"cmd": cmd, "timeout": timeout, "cwd": cwd, "user": user})
        r = MagicMock()
        r.exit_code = run_sh_exit
        r.stdout = run_sh_output
        r.stderr = ""
        return r

    sb.commands.run.side_effect = _run
    return sb, calls


class _FakeE2B:
    """A fake ``e2b`` module exposing ``Sandbox`` and ``CommandExitException``
    — installed in ``sys.modules`` so the lazy imports inside
    ``run_sandbox_eval`` resolve to our MagicMocks.
    """
    Sandbox = MagicMock
    CommandExitException = type("CommandExitException", (Exception,), {})


def _install_fake_sandbox(monkeypatch, sb):
    """Wire a fake ``e2b`` module into ``sys.modules`` so the source's
    lazy ``from e2b import Sandbox`` picks up our mock.

    The ``create`` method on the mock class returns ``sb`` so each test
    controls the sandbox's behaviour.
    """
    fake = _FakeE2B()
    fake.Sandbox = MagicMock()
    fake.Sandbox.create = MagicMock(return_value=sb)
    monkeypatch.setitem(sys.modules, "e2b", fake)
    return fake


# ---------------------------------------------------------------------------
# run.sh IS the gate
# ---------------------------------------------------------------------------


def test_runsh_exit_zero_is_ready(monkeypatch):
    """Happy path: run.sh exits 0 → verdict=ready, gate passed."""
    sb, calls = _fake_sandbox(run_sh_exit=0, run_sh_output="selfcheck OK\n")
    _install_fake_sandbox(monkeypatch, sb)

    files = {"app.py": "x", "agent/policy.py": "pass"}
    run_sh = "python -m agent --selfcheck"
    r = run_sandbox_eval(files, _plan(_python_template()), run_sh=run_sh)

    assert r.passed is True
    assert r.skipped is False
    assert r.verdict == "ready"
    assert "run.sh" in r.detail or "deployable" in r.detail


def test_runsh_non_zero_is_failed(monkeypatch):
    """run.sh exit non-zero → verdict=runsh_failed, gate NOT passed."""
    sb, _ = _fake_sandbox(run_sh_exit=1, run_sh_output="ImportError: no module 'foo'\n")
    _install_fake_sandbox(monkeypatch, sb)

    r = run_sandbox_eval(
        {"app.py": "x"},
        _plan(_python_template()),
        run_sh="python -m agent --selfcheck",
    )

    assert r.passed is False
    assert r.skipped is False
    assert r.verdict == "runsh_failed"
    # The error tail must be preserved so the retry LLM can read it.
    assert "ImportError" in r.stdout_tail


def test_runsh_wall_clock_trip_is_timeout(monkeypatch):
    """SDK-side timeout surfaces as verdict=runsh_timeout (exit 124).

    The retry-loop depends on this verdict being distinct from
    ``runsh_failed`` — a hang needs a different fix (tighten the readiness
    probe) than a scaffold bug.
    """
    sb, _ = _fake_sandbox(run_sh_exit=124, run_sh_output="")
    _install_fake_sandbox(monkeypatch, sb)

    r = run_sandbox_eval(
        {"app.py": "x"},
        _plan(_python_template()),
        run_sh="docker compose up --wait && python -m agent --selfcheck",
    )

    assert r.passed is False
    assert r.verdict == "runsh_timeout"
    assert "wall-clock" in r.detail or "tighten" in r.detail


# ---------------------------------------------------------------------------
# The KEY-FREE invariant — regression guard for the doc's gate contract
# ---------------------------------------------------------------------------


def test_gate_does_not_inject_api_key(monkeypatch):
    """REGRESSION GUARD: the gate must never set an API key in the sandbox.

    The AI-engineering plan's "key-free gate" is the load-bearing piece of
    plumbing that retires per-gate-run LLM cost and the in-sandbox-key risk.
    A future refactor that adds ``os.environ['ANTHROPIC_API_KEY'] = …`` to
    the gate would silently re-introduce both. This test asserts the
    sandbox sees an environment with NO LLM key.
    """
    sb, calls = _fake_sandbox(run_sh_exit=0)
    _install_fake_sandbox(monkeypatch, sb)

    # Sanity: no key in this Python process's env (the test runner inherits
    # the CI env, which shouldn't have one; the test is hermetic regardless).
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)

    run_sandbox_eval(
        {"app.py": "x"},
        _plan(_python_template()),
        run_sh="python -m agent --selfcheck",
    )

    # The gate ONLY writes code_files + run.sh. It does not write a .env
    # file, and it does not pass -e flags on the run.sh invocation.
    written_env = [p for p, _ in calls["writes"] if p.endswith(".env") or p.endswith("/.env")]
    assert written_env == [], f"gate must not write a .env file, found: {written_env}"

    # The run.sh invocation must not smuggle a key via -e / env=...
    for c in calls["commands"]:
        assert "-e ANTHROPIC" not in c["cmd"]
        assert "-e OPENAI" not in c["cmd"]
        assert "env=ANTHROPIC" not in c["cmd"]


# ---------------------------------------------------------------------------
# run.sh is written into the sandbox as an executable
# ---------------------------------------------------------------------------


def test_runsh_written_into_sandbox_as_executable(monkeypatch):
    """The gate must write ``run.sh`` to the sandbox before running it.

    Asserts the candidate-facing boot script and the gate's input are the
    same physical file — so the deployability check and the candidate's
    session both exercise the identical artifact.
    """
    sb, calls = _fake_sandbox(run_sh_exit=0)
    _install_fake_sandbox(monkeypatch, sb)

    run_sandbox_eval(
        {"app.py": "x"},
        _plan(_python_template()),
        run_sh="#!/usr/bin/env bash\nset -e\npython -m agent --selfcheck\n",
    )

    written_paths = [p for p, _ in calls["writes"]]
    assert "/home/user/task/run.sh" in written_paths
    # The chmod call must come AFTER the write, before the bash run.sh.
    cmd_order = [c["cmd"] for c in calls["commands"]]
    assert any("chmod +x" in c and "run.sh" in c for c in cmd_order)
    # The bash invocation of run.sh must come after the chmod.
    bash_idx = next((i for i, c in enumerate(cmd_order) if "bash run.sh" in c), None)
    chmod_idx = next((i for i, c in enumerate(cmd_order) if "chmod +x" in c and "run.sh" in c), None)
    assert bash_idx is not None and chmod_idx is not None
    assert chmod_idx < bash_idx


# ---------------------------------------------------------------------------
# Legacy fallback — build/test path is preserved for tasks that don't ship run.sh
# ---------------------------------------------------------------------------


def test_legacy_fallback_when_no_runsh_but_template_has_recipe(monkeypatch):
    """Tasks without run.sh fall through to build_cmd + test_cmd.

    The legacy path's behavior is unchanged: it still maps to the same
    _classify_pytest verdicts (ok / collection_error / no_tests / etc).
    """
    sb, _ = _fake_sandbox(run_sh_exit=0, run_sh_output="=== 1 passed ===")
    _install_fake_sandbox(monkeypatch, sb)

    files = {"app.py": "x", "requirements.txt": "fastapi\n"}
    r = run_sandbox_eval(files, _plan(_python_template()), run_sh=None)

    # The legacy path returns _classify_pytest's verdict shape; on a clean
    # exit-0 it returns verdict=ok (NOT "ready" — that's the run.sh
    # path's verb). The contract: same shape callers already handle.
    assert r.passed is True
    assert r.verdict in ("ok", "no_tests_compile_ok")


# ---------------------------------------------------------------------------
# Skip paths — a skip never blocks
# ---------------------------------------------------------------------------


def test_skip_when_no_template_even_with_runsh():
    r = run_sandbox_eval({"app.py": "x"}, _plan(None), run_sh="echo ok")
    assert r.skipped and r.verdict == "no_template"


def test_skip_when_no_code_even_with_runsh():
    r = run_sandbox_eval({}, _plan(_python_template()), run_sh="echo ok")
    assert r.skipped and r.verdict == "no_code"


def test_skip_when_no_runsh_and_no_legacy_recipe():
    """New build-it tasks always ship run.sh. If neither run.sh nor a
    template build/test recipe is available, the gate skips — never blocks.
    """
    tpl = _python_template(with_legacy_recipe=False)
    r = run_sandbox_eval({"app.py": "x"}, _plan(tpl), run_sh=None)
    assert r.skipped and r.verdict == "no_runsh"
    assert "AI-engineering plan" in r.detail or "no run.sh" in r.detail


# ---------------------------------------------------------------------------
# Sandbox boot failure → infra_error skip
# ---------------------------------------------------------------------------


def test_sandbox_boot_failure_is_infra_error_skip(monkeypatch):
    """An E2B infra flake (template missing, network down) is a skip,
    NOT a fail. A skip never blocks the task — our infra failing must
    not punish the generation LLM."""
    sb, _ = _fake_sandbox(run_sh_exit=0)
    fake = _install_fake_sandbox(monkeypatch, sb)
    # Override create to raise — the gate's outer try/except catches it
    # and surfaces ``infra_error`` (skipped=True).
    fake.Sandbox.create = MagicMock(side_effect=RuntimeError("template not found"))

    r = run_sandbox_eval(
        {"app.py": "x"},
        _plan(_python_template()),
        run_sh="echo ok",
    )

    assert r.skipped is True
    assert r.verdict == "infra_error"
