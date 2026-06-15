"""E2B ``run.sh`` readiness gate — the deployability check.

After the LLM eval critics pass a generated task, this gate boots an E2B
sandbox, writes the generated code (``code_files``) AND the candidate's
``run.sh`` into it, then runs ``run.sh``. Exit 0 = the task deploys cleanly
and a candidate can start coding. Non-zero = retry generation with feedback.

This is a deliberate replacement for the older build/test/compile-cmd trio:

* ``build_cmd`` (``pip install -r requirements.txt``) — ``run.sh`` already
  does this; the per-template recipe duplicates it.
* ``test_cmd`` (``python -m pytest -q --tb=short``) — pytest is the wrong
  gate for agent tasks. A "make these failing tests pass" task has no
  single blessed reference, and a real LLM in a non-deterministic run turns
  a probabilistic invariant suite into a coin-flip. Per the AI-engineering
  plan (2026-05-27), invariants live in the candidate's self-check and the
  reviewer rubric, NOT in a generation-time gate.
* ``compile_cmd`` (``python -m compileall -q .``) — handled implicitly by
  ``run.sh``'s ``python -m <module> --selfcheck`` shape: the import step IS
  the compile check for a no-running-service agent task.

The new contract:

* ``run.sh`` is the single source of truth. It's the candidate-facing boot
  script the candidate runs in their session, AND the deployability check
  the gate runs at generation.
* LLM-free at the gate: no key in the sandbox at generation, so any
  ``run.sh`` ping that calls a model is skipped. The first real model call
  happens later, on the candidate's key.
* Legacy fallback: if a task has no ``run.sh`` (an older task shape) and
  the template carries ``build_cmd``/``test_cmd``, fall through to the old
  build+test path. Once every task ships ``run.sh``, the fallback deletes
  cleanly.

Scope (v1): ``runtime == "python"`` only. Other runtimes are SKIPPED — logged,
not failed — until their templates exist.

Gated behind the ``SANDBOX_EVAL_ENABLED`` env flag. Pipeline runs
(``run_pipeline.py`` and the task-builder) default it ON; a raw
``multiagent.py`` call leaves it off unless the flag is set.

Every gate run logs a structured, ``[e2b-gate]``-prefixed block — boot, file
write, ``run.sh`` execution, the tail of ``run.sh``'s output, and the final
verdict — so the run is readable in the stage log.
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
_RUN_SH_TIMEOUT_S = int(os.getenv("E2B_RUNSH_GATE_TIMEOUT", "300"))
_RUN_SH_FILENAME = "run.sh"

# Prefix on every gate log line, so the block is greppable and visually grouped.
_GATE = "[e2b-gate]"


@dataclass
class SandboxEvalResult:
    """Outcome of one sandbox-eval pass.

    ``skipped`` means the gate did not run a verdict (no template for the
    runtime, no code, no run.sh and no legacy build/test recipe, or an E2B
    infra failure) — callers must treat a skip as NEITHER pass nor fail:
    never block a task because our infra flaked.
    """

    passed: bool = True
    skipped: bool = False
    verdict: str = "ok"
    detail: str = ""
    stdout_tail: str = ""

    def __post_init__(self) -> None:
        # Strict invariant: a skip is NEITHER pass nor fail, so it must never
        # report ``passed=True``. Every skip/infra_error construction omits
        # ``passed=`` and would otherwise inherit the ``True`` default, leaking
        # a contradictory ``passed: true`` + ``skipped: true`` blob into the
        # persisted eval_info. Centralise the guard here so no call site can
        # reintroduce it.
        if self.skipped:
            self.passed = False

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


def _run(sb, cmd: str, *, timeout: int = _RUN_SH_TIMEOUT_S,
         cwd: str | None = None) -> tuple[int, str, str]:
    """Run a command in the sandbox; return (exit_code, stdout, stderr).

    E2B's ``commands.run`` raises ``CommandExitException`` on a non-zero exit.
    The gate needs the exit code (``run.sh`` exit 1 = readiness failure), so
    this wrapper normalises both paths into a plain tuple.
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
    except Exception as exc:  # noqa: BLE001 — E2B raises a TimeoutError-ish when the wall-clock trips
        # ``commands.run(timeout=...)`` can raise on the SDK side rather than
        # returning a non-zero exit; surface it as a clean timeout verdict
        # so the gate's caller sees one shape, not a crash.
        if "timeout" in str(exc).lower() or "deadline" in str(exc).lower():
            return 124, "", str(exc)
        raise


def _log_output(label: str, output: str, lines: int = 30) -> None:
    """Log the tail of a sandbox command's output, indented for readability."""
    tail = [ln for ln in output.splitlines() if ln.strip()][-lines:]
    if not tail:
        return
    logger.info(f"{_GATE}   ── {label} (last {len(tail)} lines) ──")
    for ln in tail:
        logger.info(f"{_GATE}   | {ln}")


# Readiness/endpoint-probe lines that run.sh prints itself (health code, endpoint
# HTTP codes, warnings) + the final exception line of any app traceback. Surfaced
# separately so they survive the last-30-lines tail truncation (which, for a
# buggy-code task, is just the traceback) — letting a reviewer confirm "scaffold
# up + endpoint behavior" from the gate log without re-running the sandbox.
_READINESS_RE = re.compile(
    r"HTTP\s*\d{3}|responding|is up|is ready|is healthy|became ready|"
    r"did not (respond|become)|search endpoint|/health|deployment complete|"
    r"environment is up|seed complete|WARNING:|ERROR:|"
    r"[A-Za-z_]\w*(Error|Exception):",
    re.I,
)


def _log_readiness(output: str, lines: int = 14) -> None:
    """Surface run.sh's own readiness/endpoint-probe lines into the gate log so
    the verdict is confirmable from the log alone. Log-only — does not affect
    the verdict (still run.sh's exit code)."""
    hits = [ln.strip() for ln in output.splitlines() if _READINESS_RE.search(ln)]
    if not hits:
        return
    logger.info(f"{_GATE}   ── readiness probe (from run.sh) ──")
    for ln in hits[-lines:]:
        logger.info(f"{_GATE}   ‣ {ln[:200]}")


# Broad error markers for the retry-feedback excerpt — compile errors, panics,
# non-zero exits, failed/refused/timeout, missing deps. Broader than the
# readiness probe (which is health-focused) so a build/compile failure's real
# cause is captured, not just the docker pull/extract noise that dominates a
# naive tail.
_FAILURE_LINE_RE = re.compile(
    r"\b(errors?|failed|failure|fatal|panic|exception|traceback|cannot|"
    r"could not|unable to|not found|undefined|denied|refused|timeout|timed out|"
    r"no such|exit(?:ed)?[ =]?(?:status |code )?[1-9])\b"
    r"|^\s*[\w./-]+\.\w+:\d+[:)]"      # file.ext:line: — compiler errors
    r"|^\s*panic:",
    re.I,
)


def _failure_excerpt(output: str, *, tail_chars: int = 1000, max_summary: int = 1800) -> str:
    """Sharp failure excerpt for the retry feedback: the actual error +
    readiness lines first (so the LLM sees the *cause*, not docker pull/extract
    noise), then the last chunk of raw output for context. Falls back to a plain
    tail when nothing matches."""
    # Dedupe: a crash-looping service repeats the same traceback many times;
    # collapsing identical lines keeps the budget for DISTINCT signals (e.g. the
    # run.sh "ERROR: … did not respond" / "exit 1" framing) instead of 8 copies
    # of one error.
    hits: list[str] = []
    seen: set[str] = set()
    for ln in output.splitlines():
        s = ln.strip()
        if not s:
            continue
        if _FAILURE_LINE_RE.search(s) or _READINESS_RE.search(s):
            # Dedup on a digit-normalized key so retry-counter lines that differ
            # only by a number ("Attempt 1/20…", "Attempt 2/20…") collapse to one.
            norm = re.sub(r"\d+", "#", s)
            if norm in seen:
                continue
            seen.add(norm)
            hits.append(s)
    raw_tail = output[-tail_chars:]
    if not hits:
        return output[-(max_summary + tail_chars):]
    summary = "Key error / readiness lines:\n" + "\n".join(hits[-25:])
    if len(summary) > max_summary:
        summary = summary[:max_summary] + "…"
    return summary + "\n\n--- recent run.sh output ---\n" + raw_tail


def _verdict_label(result: SandboxEvalResult) -> str:
    """PASS / FAIL / SKIP — the one-word outcome class for a result."""
    if result.skipped:
        return "SKIP"
    return "PASS" if result.passed else "FAIL"


def _finish(result: SandboxEvalResult) -> SandboxEvalResult:
    """Log the final gate verdict and return the result unchanged.

    Every ``run_sandbox_eval`` return path funnels through here, so the verdict
    line is always emitted and the log block is always closed.
    """
    logger.info(f"{_GATE} verdict: {result.verdict} [{_verdict_label(result)}] "
                f"— {result.detail}")
    logger.info(f"{_GATE} {'─' * 60}")
    return result


# ---------------------------------------------------------------------------
# Legacy build/test/compile path — kept for tasks that don't yet ship run.sh.
# Every new build-it task (per docs/plans/2026-05-27-ai-engineering-task-
# category.html) ships run.sh, so this path shrinks over time. It is NOT
# removed in this change — the contract is "run.sh if present, else build/
# test if the template has a recipe, else skip". Deleting the legacy path
# is a separate cleanup once every existing task is re-generated with run.sh.
# ---------------------------------------------------------------------------


def _classify_pytest(exit_code: int, output: str) -> SandboxEvalResult:
    """Map a pytest exit code (legacy test_suite path) to a gate verdict.

    The legacy gate does NOT require tests to PASS — a generated starter ships
    by-design failing tests (the candidate's job is to make them green). It
    fails only when the suite cannot COMPILE or RUN.

    pytest exit codes: 0 all-passed · 1 some-failed · 2 interrupted/collection
    · 3 internal-error · 4 usage-error · 5 no-tests-collected.
    """
    low = output.lower()
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
               "cleanly.",
        stdout_tail=output[-2000:],
    )


def _run_legacy_build_test(
    sb,
    template_spec: Any,
    code_files: dict,
    names: set[str],
) -> SandboxEvalResult:
    """The pre-run.sh gate: build_cmd → test_cmd, compile_cmd as no-tests fallback.

    Used only when ``run.sh`` is absent AND the template carries build_cmd +
    test_cmd. New tasks don't hit this path.
    """
    build_cmd = template_spec.build_cmd
    test_cmd = template_spec.test_cmd
    compile_cmd = template_spec.compile_cmd or "python -m compileall -q ."

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
            return SandboxEvalResult(
                passed=False, verdict="compose_failed",
                detail="`docker compose up` failed — the task's service "
                       "containers do not start.",
                stdout_tail=(out + err)[-3000:])

    # Install the task's declared Python deps (the template pre-installs the
    # common set; this tops up anything task-specific).
    if "requirements.txt" in names:
        ts = time.time()
        code, out, err = _run(sb, build_cmd, cwd=_TASK_DIR, timeout=240)
        ok = code == 0
        logger.info(f"{_GATE} build_cmd ({build_cmd!r})… "
                    f"{'ok' if ok else f'FAILED exit={code}'} "
                    f"({time.time() - ts:.1f}s)")
        if not ok:
            _log_output("build output", out + err)
            return SandboxEvalResult(
                passed=False, verdict="pip_failed",
                detail=f"`{build_cmd}` failed.",
                stdout_tail=(out + err)[-3000:])

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
            return SandboxEvalResult(
                passed=True, verdict="no_tests_compile_ok",
                detail="task ships no tests, but every source file compiles")
        _log_output("compile output", cc_out + cc_err)
        return SandboxEvalResult(
            passed=False, verdict="compile_error",
            detail=f"task ships no tests and `{compile_cmd}` found a "
                   "syntax error.",
            stdout_tail=(cc_out + cc_err)[-3000:])

    return _classify_pytest(code, combined)


# ---------------------------------------------------------------------------
# The run.sh gate — the new default.
# ---------------------------------------------------------------------------


def _run_runsh(
    sb,
    run_sh: str,
    template_spec: Any,
) -> SandboxEvalResult:
    """Run the task's ``run.sh`` in the sandbox; map the exit code to a verdict.

    Wall-clock bounded by ``_RUN_SH_TIMEOUT_S``; an SDK-side timeout is
    surfaced as ``runsh_timeout`` (not a crash). LLM-free at the gate:
    no key is set in the sandbox, so any key-gated ping inside ``run.sh``
    short-circuits to the static-check path and exits 0.
    """
    ts = time.time()
    code, out, err = _run(
        sb,
        f"chmod +x {_RUN_SH_FILENAME} && bash {_RUN_SH_FILENAME}",
        cwd=_TASK_DIR,
        timeout=_RUN_SH_TIMEOUT_S,
    )
    combined = out + "\n" + err
    logger.info(f"{_GATE} run.sh… exit={code} ({time.time() - ts:.1f}s)")
    _log_readiness(combined)
    _log_output("run.sh output", combined)

    if code == 124:
        return SandboxEvalResult(
            passed=False, verdict="runsh_timeout",
            detail=(f"run.sh exceeded the {_RUN_SH_TIMEOUT_S}s gate wall-clock "
                    "— likely a hang in `docker compose up` or a service "
                    "readiness wait. Tighten the readiness probe."),
            stdout_tail=_failure_excerpt(combined),
        )
    if code == 0:
        return SandboxEvalResult(
            passed=True, verdict="ready",
            detail="run.sh exited 0 — scaffold + services load, task is "
                   "deployable; a candidate can start coding.",
            stdout_tail=combined[-1000:],
        )
    return SandboxEvalResult(
        passed=False, verdict="runsh_failed",
        detail=f"run.sh exited {code} — the scaffold or its services did not "
               "come up cleanly. Fix the scaffold so the readiness selfcheck "
               "passes (without filling the candidate stubs).",
        stdout_tail=_failure_excerpt(combined),
    )


def run_sandbox_eval(
    code_files: dict,
    plan: Any,
    run_sh: str | None = None,
) -> SandboxEvalResult:
    """Boot a sandbox, write the code + ``run.sh`` in, verify readiness.

    Contract:

    * If ``run_sh`` is provided (the new build-it contract), it is the gate.
      Exit 0 = ready, non-zero = ``runsh_failed``, wall-clock = ``runsh_timeout``.
      ``run.sh`` MUST be LLM-free at the gate (the sandbox has no API key
      here; only the candidate's session has one).
    * If ``run_sh`` is absent and the template carries ``build_cmd`` +
      ``test_cmd``, fall through to the legacy build/test path. Used by
      older tasks until they're re-generated.
    * Otherwise skip (``no_runsh``) — a skip never blocks a task.
    * Skip also on no template, no code, or E2B infra failure.

    ``plan`` is a ``ResolvedPlan`` (or any object exposing a ``.template``
    with ``.template_id``/``.primary_runtime``/``.build_cmd``/``.test_cmd``);
    ``None`` is also accepted and treated as an explicit no-template skip.
    """
    template_spec = getattr(plan, "template", None)
    template = template_spec.template_id if template_spec is not None else None
    runtime = template_spec.primary_runtime if template_spec is not None else None

    logger.info(f"{_GATE} {'─' * 60}")
    logger.info(f"{_GATE} E2B run.sh readiness gate — runtime={runtime!r} "
                f"template={template or '<none>'} files={len(code_files or {})} "
                f"has_runsh={bool(run_sh)}")

    if template is None:
        return _finish(SandboxEvalResult(
            skipped=True, verdict="no_template",
            detail=f"no sandbox template for runtime={runtime!r} — gate skipped"))
    if not code_files:
        return _finish(SandboxEvalResult(
            skipped=True, verdict="no_code",
            detail="no code_files to evaluate — gate skipped"))

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
        # ``run.sh`` is the gate's primary input. Write it (if supplied) as
        # an executable at the task root so the candidate-facing shape and
        # the gate's shape are identical: same script, same exit semantics.
        if run_sh:
            sb.files.write(
                f"{_TASK_DIR}/{_RUN_SH_FILENAME}",
                run_sh if isinstance(run_sh, str) else str(run_sh),
            )
            sb.commands.run(
                f"chmod +x {_TASK_DIR}/{_RUN_SH_FILENAME}",
                timeout=10,
                user="root",
            )
        logger.info(f"{_GATE} wrote {len(code_files)} code file(s) "
                    f"+ {'run.sh' if run_sh else 'no run.sh'} to {_TASK_DIR}")

        # Mirror the deploy runtime (sandbox_manager._symlink_root_task): many
        # tasks hardcode /root/task (the legacy droplet path) in run.sh and
        # docker-compose volume mounts. The deploy path aliases it to
        # /home/user/task, so the gate must too — otherwise it false-negatives
        # tasks that would actually deploy and boot cleanly.
        try:
            sb.commands.run(
                f"ln -sfn {_TASK_DIR} /root/task",
                timeout=10,
                user="root",
            )
        except Exception as exc:
            logger.warning(f"{_GATE} could not symlink /root/task: {exc}")

        # Path A — new default: run.sh IS the gate.
        if run_sh:
            return _finish(_run_runsh(sb, run_sh, template_spec))

        # Path B — legacy fallback for tasks that don't yet ship run.sh.
        # Collapses to ``no_runsh`` once every task is re-generated with
        # the new build-it shape (per docs/plans/2026-05-27-ai-engineering-
        # task-category.html).
        names = {str(p).lstrip("/") for p in code_files}
        has_legacy_recipe = bool(
            getattr(template_spec, "build_cmd", None)
            and getattr(template_spec, "test_cmd", None)
        )
        if has_legacy_recipe:
            logger.info(f"{_GATE} no run.sh — falling back to legacy "
                        f"build_cmd/test_cmd path for template={template}")
            return _finish(_run_legacy_build_test(sb, template_spec, code_files, names))

        return _finish(SandboxEvalResult(
            skipped=True, verdict="no_runsh",
            detail="task ships no run.sh and the template has no build/test "
                   "recipe — gate skipped (caller should generate a task with "
                   "run.sh per the AI-engineering plan)."))
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
