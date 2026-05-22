"""E2B build/test gate — the deterministic correctness check.

After the LLM eval critics pass a generated task, this gate boots an E2B
sandbox, writes the generated code into it, and verifies the test suite
actually COMPILES and RUNS. It catches the F12 failure class: generated test
files that look right to an LLM critic but don't compile (the Flutter task in
``.task_agent_runs/FOLLOWUPS.md`` that passed both LLM evals with a test file
full of `implements dynamic` / missing-import errors).

Scope (v1): ``runtime == "python"`` only (the ``utkrusht-python`` template).
Other runtimes are SKIPPED — logged, not failed — until their templates exist.

Gated behind the ``SANDBOX_EVAL_ENABLED`` env flag; off by default.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from logger_config import logger

# runtime (TaskRuntime.runtime) -> E2B template name. Extend as templates ship.
_TEMPLATE_FOR_RUNTIME: dict[str, str] = {
    "python": "utkrusht-python",
}

_TASK_DIR = "/home/user/task"
_SANDBOX_TIMEOUT_S = 300
_CMD_TIMEOUT_S = 240


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


def run_sandbox_eval(code_files: dict, task_runtime: Any) -> SandboxEvalResult:
    """Boot a sandbox, write the generated code in, verify it compiles + runs.

    ``task_runtime`` is a TaskRuntime (or anything with a ``.runtime`` str).
    Returns ``skipped=True`` when there is no template for the runtime, no
    code, or E2B infra fails — a skip never blocks the task.
    """
    runtime = getattr(task_runtime, "runtime", None)
    template = _TEMPLATE_FOR_RUNTIME.get(runtime or "")
    if template is None:
        return SandboxEvalResult(
            skipped=True, verdict="no_template",
            detail=f"no sandbox template for runtime={runtime!r} — gate skipped",
        )
    if not code_files:
        return SandboxEvalResult(
            skipped=True, verdict="no_code",
            detail="no code_files to evaluate — gate skipped",
        )

    from e2b import Sandbox

    try:
        sb = Sandbox.create(template=template, timeout=_SANDBOX_TIMEOUT_S)
    except Exception as exc:  # noqa: BLE001 — infra failure must not fail the task
        logger.warning(f"sandbox eval: could not boot {template}: {exc}")
        return SandboxEvalResult(skipped=True, verdict="infra_error",
                                 detail=f"sandbox boot failed: {exc}")

    try:
        for path, content in code_files.items():
            dest = f"{_TASK_DIR}/{str(path).lstrip('/')}"
            sb.files.write(dest, content if isinstance(content, str) else str(content))

        names = {str(p).lstrip("/") for p in code_files}

        # If the task brings service containers, start them before tests run.
        if any(n == "docker-compose.yml" or n.endswith("/docker-compose.yml")
               for n in names):
            code, out, err = _run(sb, "docker compose up -d --wait",
                                  cwd=_TASK_DIR, timeout=240)
            if code != 0:
                return SandboxEvalResult(
                    passed=False, verdict="compose_failed",
                    detail="`docker compose up` failed — the task's service "
                           "containers do not start.",
                    stdout_tail=(out + err)[-2000:],
                )

        # Install the task's declared Python deps (the template pre-installs
        # the common set; this tops up anything task-specific).
        if "requirements.txt" in names:
            code, out, err = _run(
                sb, "pip install --break-system-packages -r requirements.txt",
                cwd=_TASK_DIR, timeout=240)
            if code != 0:
                return SandboxEvalResult(
                    passed=False, verdict="pip_failed",
                    detail="`pip install -r requirements.txt` failed.",
                    stdout_tail=(out + err)[-2000:],
                )

        code, out, err = _run(sb, "python -m pytest -q --tb=short",
                              cwd=_TASK_DIR, timeout=240)
        combined = out + "\n" + err

        if code == 5:
            # No tests collected — fall back to a compile check so a task that
            # legitimately ships no tests still gets a parse gate.
            cc_code, cc_out, cc_err = _run(sb, "python -m compileall -q .",
                                           cwd=_TASK_DIR, timeout=60)
            if cc_code == 0:
                return SandboxEvalResult(
                    passed=True, verdict="no_tests_compile_ok",
                    detail="task ships no tests, but every .py file compiles",
                )
            return SandboxEvalResult(
                passed=False, verdict="compile_error",
                detail="task ships no tests and `python -m compileall` found a "
                       "syntax error.",
                stdout_tail=(cc_out + cc_err)[-2000:],
            )

        return _classify_pytest(code, combined)
    except Exception as exc:  # noqa: BLE001 — unexpected; treat as an infra skip
        logger.warning(f"sandbox eval: unexpected error: {exc}")
        return SandboxEvalResult(skipped=True, verdict="infra_error",
                                 detail=f"unexpected sandbox error: {exc}")
    finally:
        try:
            sb.kill()
        except Exception:  # noqa: BLE001
            pass
