"""E2B build/test gate — the deterministic correctness check.

After the LLM eval critics pass a generated task, this gate boots an E2B
sandbox, writes the generated code into it, and verifies the test suite
actually COMPILES and RUNS. It catches the F12 failure class: generated test
files that look right to an LLM critic but don't compile (the Flutter task in
``.task_agent_runs/FOLLOWUPS.md`` that passed both LLM evals with a test file
full of `implements dynamic` / missing-import errors).

Scope (v1): ``runtime == "python"`` only (the ``utkrusht-python`` template).
Other runtimes are SKIPPED — logged, not failed — until their templates exist.

Gated behind the ``SANDBOX_EVAL_ENABLED`` env flag. Pipeline runs
(``run_pipeline.py`` and the task-builder) default it ON; a raw ``multiagent.py``
call leaves it off unless the flag is set.

Every gate run logs a structured, ``[e2b-gate]``-prefixed block — boot, file
write, ``docker compose``, ``pip``, ``pytest``, the tail of each command's
output, and the final verdict — so the run is readable in the stage log.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Any

from infra.logger_config import logger

# The gate reads the template + build/test/compile commands from the
# ResolvedPlan the caller hands in (those values live in the ``templates``
# Supabase table; ``generators.task.runtime_resolver`` loads them and
# stamps them onto ``plan.template``). Doing it that way means this module
# touches no ``generators.task`` import at all — sidesteps the package-init
# import cycle that bit pytest collection earlier.

_TASK_DIR = "/home/user/task"
_SANDBOX_TIMEOUT_S = 300
_CMD_TIMEOUT_S = 240

# Prefix on every gate log line, so the block is greppable and visually grouped.
_GATE = "[e2b-gate]"


@dataclass
class SandboxEvalResult:
    """Outcome of one sandbox-eval pass.

    ``skipped`` means the gate did not run a verdict (no template for the
    runtime, no code, or an E2B infra failure) — callers must treat a skip as
    NEITHER pass nor fail: never block a task because our infra flaked.
    """

    passed: bool = True
    skipped: bool = False
    verdict: str = "ok"
    detail: str = ""
    stdout_tail: str = ""

    def as_dict(self) -> dict:
        return {
            "passed": self.passed,
            "skipped": self.skipped,
            "verdict": self.verdict,
            "detail": self.detail[:2000],
            # Persist the tail of the in-sandbox output so the gate run is
            # inspectable later from the stored eval_info, not just live logs.
            "stdout_tail": self.stdout_tail[-4000:],
        }


def sandbox_eval_enabled() -> bool:
    """True when SANDBOX_EVAL_ENABLED is a truthy env value."""
    return os.getenv("SANDBOX_EVAL_ENABLED", "").strip().lower() in ("1", "true", "yes")


def _run(sb, cmd: str, *, timeout: int = _CMD_TIMEOUT_S,
         cwd: str | None = None) -> tuple[int, str, str]:
    """Run a command in the sandbox; return (exit_code, stdout, stderr).

    E2B's ``commands.run`` raises ``CommandExitException`` on a non-zero exit.
    The gate needs the exit code (pytest exit 1 = tests failed = still a valid
    run), so this wrapper normalises both paths into a plain tuple.
    """
    from e2b import CommandExitException
    try:
        r = sb.commands.run(cmd, timeout=timeout, cwd=cwd, user="root")
        return r.exit_code, (r.stdout or ""), (r.stderr or "")
    except CommandExitException as e:
        code = getattr(e, "exit_code", None)
        out = getattr(e, "stdout", "") or ""
        err = getattr(e, "stderr", "") or ""
        if code is None:
            m = re.search(r"code (\d+)", str(e))
            code = int(m.group(1)) if m else 1
            err = err or str(e)
        return code, out, err


def _classify_pytest(exit_code: int, output: str) -> SandboxEvalResult:
    """Map a pytest run to a gate verdict.

    The gate does NOT require tests to PASS — a generated starter ships
    by-design failing tests (the candidate's job is to make them green). It
    fails only when the suite cannot COMPILE or RUN.

    pytest exit codes: 0 all-passed · 1 some-failed · 2 interrupted/collection
    · 3 internal-error · 4 usage-error · 5 no-tests-collected.
    """
    low = output.lower()
    # A collection error == a test (or imported source) file failed to
    # parse/import. This is the F12 bug class.
    if "error collecting" in low or "errors during collection" in low:
        return SandboxEvalResult(
            passed=False, verdict="collection_error",
            detail="pytest hit a collection error — a test or source file does "
                   "not compile or import cleanly.",
            stdout_tail=output[-2000:],
        )
    if exit_code in (0, 1):
        return SandboxEvalResult(
            passed=True, verdict="ok",
            detail="test suite compiled and executed",
            stdout_tail=output[-1000:],
        )
    if exit_code == 5:
        return SandboxEvalResult(
            passed=False, verdict="no_tests",
            detail="pytest collected 0 tests — the task ships no runnable tests.",
            stdout_tail=output[-2000:],
        )
    return SandboxEvalResult(
        passed=False, verdict="test_run_error",
        detail=f"pytest exited with code {exit_code} — the suite did not run "
               f"cleanly.",
        stdout_tail=output[-2000:],
    )


def _verdict_label(result: SandboxEvalResult) -> str:
    """PASS / FAIL / SKIP — the one-word outcome class for a result."""
    if result.skipped:
        return "SKIP"
    return "PASS" if result.passed else "FAIL"


def _log_output(label: str, output: str, lines: int = 30) -> None:
    """Log the tail of a sandbox command's output, indented for readability."""
    tail = [ln for ln in output.splitlines() if ln.strip()][-lines:]
    if not tail:
        return
    logger.info(f"{_GATE}   ── {label} (last {len(tail)} lines) ──")
    for ln in tail:
        logger.info(f"{_GATE}   | {ln}")


def _finish(result: SandboxEvalResult) -> SandboxEvalResult:
    """Log the final gate verdict and return the result unchanged.

    Every ``run_sandbox_eval`` return path funnels through here, so the verdict
    line is always emitted and the log block is always closed.
    """
    logger.info(f"{_GATE} verdict: {result.verdict} [{_verdict_label(result)}] "
                f"— {result.detail}")
    logger.info(f"{_GATE} {'─' * 60}")
    return result


def run_sandbox_eval(code_files: dict, plan: Any) -> SandboxEvalResult:
    """Boot a sandbox, write the generated code in, verify it compiles + runs.

    ``plan`` is a ``ResolvedPlan`` (or any object exposing a ``.template``
    with ``.template_id``/``.primary_runtime``/``.build_cmd``/``.test_cmd``);
    ``None`` is also accepted and treated as an explicit no-template skip.
    Returns ``skipped=True`` when the plan has no template, no code is
    provided, or E2B infra fails — a skip never blocks the task.
    """
    template_spec = getattr(plan, "template", None)
    template = template_spec.template_id if template_spec is not None else None
    runtime = template_spec.primary_runtime if template_spec is not None else None

    logger.info(f"{_GATE} {'─' * 60}")
    logger.info(f"{_GATE} E2B build/test gate — runtime={runtime!r} "
                f"template={template or '<none>'} files={len(code_files or {})}")

    if template is None:
        return _finish(SandboxEvalResult(
            skipped=True, verdict="no_template",
            detail=f"no sandbox template for runtime={runtime!r} — gate skipped"))
    if not code_files:
        return _finish(SandboxEvalResult(
            skipped=True, verdict="no_code",
            detail="no code_files to evaluate — gate skipped"))

    # Pulled from the ResolvedPlan so a future Java/Node/Go runtime gets its
    # own build/test/compile recipe without code changes here — the recipe
    # lives in ``templates``.
    build_cmd = template_spec.build_cmd
    test_cmd = template_spec.test_cmd
    compile_cmd = template_spec.compile_cmd or "python -m compileall -q ."

    from e2b import Sandbox

    t0 = time.time()
    logger.info(f"{_GATE} booting sandbox from {template}…")
    try:
        sb = Sandbox.create(template=template, timeout=_SANDBOX_TIMEOUT_S)
    except Exception as exc:  # noqa: BLE001 — infra failure must not fail the task
        logger.warning(f"{_GATE} could not boot {template}: {exc}")
        return _finish(SandboxEvalResult(
            skipped=True, verdict="infra_error",
            detail=f"sandbox boot failed: {exc}"))
    logger.info(f"{_GATE} sandbox up ({time.time() - t0:.1f}s)")

    try:
        for path, content in code_files.items():
            dest = f"{_TASK_DIR}/{str(path).lstrip('/')}"
            sb.files.write(dest, content if isinstance(content, str) else str(content))
        logger.info(f"{_GATE} wrote {len(code_files)} file(s) to {_TASK_DIR}")

        names = {str(p).lstrip("/") for p in code_files}

        # If the task brings service containers, start them before tests run.
        if any(n == "docker-compose.yml" or n.endswith("/docker-compose.yml")
               for n in names):
            ts = time.time()
            code, out, err = _run(sb, "docker compose up -d --wait",
                                  cwd=_TASK_DIR, timeout=240)
            ok = code == 0
            logger.info(f"{_GATE} docker compose up… "
                        f"{'ok' if ok else f'FAILED exit={code}'} "
                        f"({time.time() - ts:.1f}s)")
            if not ok:
                _log_output("docker compose output", out + err)
                return _finish(SandboxEvalResult(
                    passed=False, verdict="compose_failed",
                    detail="`docker compose up` failed — the task's service "
                           "containers do not start.",
                    stdout_tail=(out + err)[-3000:]))

        # Install the task's declared Python deps (the template pre-installs
        # the common set; this tops up anything task-specific). ``build_cmd``
        # comes from the ResolvedPlan / template_registry row.
        if "requirements.txt" in names:
            ts = time.time()
            code, out, err = _run(sb, build_cmd, cwd=_TASK_DIR, timeout=240)
            ok = code == 0
            logger.info(f"{_GATE} build_cmd ({build_cmd!r})… "
                        f"{'ok' if ok else f'FAILED exit={code}'} "
                        f"({time.time() - ts:.1f}s)")
            if not ok:
                _log_output("build output", out + err)
                return _finish(SandboxEvalResult(
                    passed=False, verdict="pip_failed",
                    detail=f"`{build_cmd}` failed.",
                    stdout_tail=(out + err)[-3000:]))

        ts = time.time()
        code, out, err = _run(sb, test_cmd, cwd=_TASK_DIR, timeout=240)
        combined = out + "\n" + err
        logger.info(f"{_GATE} test_cmd ({test_cmd!r})… "
                    f"exit={code} ({time.time() - ts:.1f}s)")
        _log_output("test output", combined)

        if code == 5:
            # No tests collected — fall back to a compile check so a task that
            # legitimately ships no tests still gets a parse gate.
            ts = time.time()
            cc_code, cc_out, cc_err = _run(sb, compile_cmd,
                                           cwd=_TASK_DIR, timeout=60)
            logger.info(f"{_GATE} no tests collected — compile_cmd "
                        f"({compile_cmd!r})… exit={cc_code} "
                        f"({time.time() - ts:.1f}s)")
            if cc_code == 0:
                return _finish(SandboxEvalResult(
                    passed=True, verdict="no_tests_compile_ok",
                    detail="task ships no tests, but every source file compiles"))
            _log_output("compile output", cc_out + cc_err)
            return _finish(SandboxEvalResult(
                passed=False, verdict="compile_error",
                detail=f"task ships no tests and `{compile_cmd}` found a "
                       "syntax error.",
                stdout_tail=(cc_out + cc_err)[-3000:]))

        return _finish(_classify_pytest(code, combined))
    except Exception as exc:  # noqa: BLE001 — unexpected; treat as an infra skip
        logger.warning(f"{_GATE} unexpected error: {exc}")
        return _finish(SandboxEvalResult(
            skipped=True, verdict="infra_error",
            detail=f"unexpected sandbox error: {exc}"))
    finally:
        try:
            sb.kill()
        except Exception:  # noqa: BLE001
            pass
