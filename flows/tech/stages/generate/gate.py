"""E2B build/test gate invocation for the create-task retry loop.

Wraps the *policy* of "when do we run the gate and what does the loop do
with the result" — separates that from the gate's own mechanics, which live
in ``infra/e2b/sandbox_eval``.

The retry loop in ``create_task`` calls :func:`run_gate_for_attempt` after
the LLM eval critics pass. The function returns one of four outcomes via
:class:`GateOutcome` so the loop never needs to inspect the raw
``SandboxEvalResult`` itself:

* ``PASS`` — gate ran and passed → proceed to storage.
* ``SKIPPED`` — gate produced no verdict (no template for the runtime, no
  code, infra flake) → proceed to storage normally; a skip never blocks.
* ``DISABLED`` — ``SANDBOX_EVAL_ENABLED`` is off → proceed to storage.
* ``RETRY`` — gate FAILED → retry the generation with the returned
  ``feedback`` string.
"""
from __future__ import annotations

import os
import time
from enum import Enum
from typing import Dict, Optional, Tuple

from infra.logger_config import logger

# A sandbox can die mid-run from a transient E2B infra fault (boot failure, or
# a mid-run StreamReset when the sandbox is terminated early). That surfaces as
# ``verdict == "infra_error"`` (a skip), which would otherwise let a task ship
# WITHOUT a deployability verdict. Retry the whole eval a bounded number of
# times on infra_error — a fresh sandbox usually succeeds. Deterministic skips
# (no_template / no_code / no_runsh) and real pass/fail are NOT retried.
# Bounded so a genuinely-down E2B doesn't stall task generation.
_INFRA_ERROR_VERDICT = "infra_error"
_INFRA_GATE_RETRIES = int(os.getenv("E2B_GATE_INFRA_RETRIES", "2"))
_INFRA_RETRY_BACKOFF_S = float(os.getenv("E2B_GATE_INFRA_BACKOFF_S", "3"))

# ``infra.metrics`` was dropped with the deployment layer. This no-op stub keeps
# the ``metrics.inc(...)`` call sites working without the metrics subsystem.
class _Metrics:
    def inc(self, *args, **kwargs) -> None:
        pass


metrics = _Metrics()

from infra.e2b.sandbox_eval import (
    run_non_infra_gate,
    run_sandbox_eval,
    sandbox_eval_enabled,
)
from flows.tech.stages.generate.evaluator import build_retry_feedback
from flows.tech.stages.generate.runtime_resolver import ResolvedPlan


class GateOutcome(Enum):
    """What the retry loop should do after the gate runs."""

    PASS = "pass"          # gate ran and passed → proceed to storage
    SKIPPED = "skipped"    # gate produced no verdict → proceed to storage
    DISABLED = "disabled"  # SANDBOX_EVAL_ENABLED is off → proceed to storage
    RETRY = "retry"        # gate FAILED → retry generation with feedback


def _eval_with_infra_retry(plan, candidate, on_pass=None):
    """Run the sandbox eval, retrying ONLY on a transient ``infra_error``.

    Returns the first result that is not a transient infra_error (a real
    pass/fail, or a deterministic skip), or — if every attempt flaked — the
    last infra_error result so the caller still records the SKIP.
    """
    attempts = _INFRA_GATE_RETRIES + 1
    result = None
    for i in range(attempts):
        result = run_sandbox_eval(
            candidate.get("code_files", {}),
            plan,
            run_sh=candidate.get("run_script"),
            on_pass=on_pass,
        )
        if not (result.skipped and result.verdict == _INFRA_ERROR_VERDICT):
            return result
        if i < attempts - 1:
            logger.warning(
                f"  sandbox gate infra_error (attempt {i + 1}/{attempts}) — "
                f"retrying: {result.detail}"
            )
            metrics.inc("gate_infra_retry_total", attempt=str(i + 1))
            if _INFRA_RETRY_BACKOFF_S > 0:
                time.sleep(_INFRA_RETRY_BACKOFF_S)
    logger.warning(
        f"  sandbox gate infra_error persisted after {attempts} attempt(s) — "
        f"accepting SKIP: {result.detail}"
    )
    return result


def run_gate_for_attempt(
    plan: Optional[ResolvedPlan],
    candidate: Dict,
    candidate_eval: Dict,
    attempt: int,
    task_shape: Optional[str] = None,
    on_pass=None,
) -> Tuple[GateOutcome, str]:
    """Run the E2B build/test gate for one ``create_task`` attempt.

    Mutates ``candidate_eval`` to add the ``sandbox_eval`` verdict dict when
    the gate actually ran a verdict. Returns the outcome the retry loop
    should act on, plus the retry-feedback string (empty unless ``RETRY``).

    ``on_pass`` (optional ``callable(sandbox)``) is threaded to
    ``run_sandbox_eval`` and fires with the still-live sandbox only when the
    gate passes — the tour step verifies its commands there before teardown.

    Skip condition (yields ``DISABLED`` — loop proceeds to storage):

      * ``SANDBOX_EVAL_ENABLED`` env var is off (the original global
        kill-switch — unchanged).

    ``task_shape == "non_infra"`` routes to ``run_non_infra_gate`` instead of
    the run.sh gate: a pure-local project has no template and no run.sh, but
    its own suite must still install and collect. This used to skip outright
    ("nothing to build in the sandbox"), which let a starter ship with a suite
    that could not be collected at all — the LLM task + code evals read the
    code, they never execute it, so nothing caught it.
    """
    if not sandbox_eval_enabled():
        metrics.inc("gate_outcome_total", outcome="disabled")
        return GateOutcome.DISABLED, ""

    if task_shape == "non_infra":
        # A pure-local project has no template and no run.sh, so the run.sh
        # gate cannot apply — but its own suite still has to install and
        # collect. Skipping outright let a starter whose tests could not be
        # collected at all ship green (the LLM evals read the code, they never
        # run it). Failing tests still PASS here: the starter is meant to be red.
        logger.info("Running non-infra install/collect gate")
        sb_result = run_non_infra_gate(candidate.get("code_files", {}))
        candidate_eval["sandbox_eval"] = sb_result.as_dict()

        if sb_result.skipped:
            logger.info(f"  non-infra gate skipped: {sb_result.detail}")
            metrics.inc("gate_outcome_total", outcome="skipped",
                        runtime="non_infra",
                        reason=(sb_result.detail or "no_reason")[:40])
            return GateOutcome.SKIPPED, ""

        if not sb_result.passed:
            metrics.inc("gate_outcome_total", outcome="retry", runtime="non_infra")
            logger.warning(
                f"Attempt {attempt}: non-infra gate FAILED "
                f"({sb_result.verdict}) — {sb_result.detail}"
            )
            feedback = build_retry_feedback(
                [],
                candidate_eval,
                prior_candidate=candidate,
            )
            return GateOutcome.RETRY, feedback

        metrics.inc("gate_outcome_total", outcome="pass", runtime="non_infra")
        logger.info(f"  non-infra gate passed: {sb_result.detail}")
        return GateOutcome.PASS, ""

    logger.info("Running E2B run.sh readiness gate")
    # ``plan`` carries both the runtime AND the template recipe
    # (``plan.template.build_cmd`` / ``test_cmd`` / ``compile_cmd``) so the
    # gate falls back to the legacy build/test path cleanly if ``run.sh``
    # is absent. The primary gate is the candidate's own ``run.sh`` (LLM-free
    # at the gate, key-gated ping in their session).
    sb_result = _eval_with_infra_retry(plan, candidate, on_pass=on_pass)
    candidate_eval["sandbox_eval"] = sb_result.as_dict()

    runtime_label = (plan.match.template_id or plan.match.suggested_template or "unknown") if (plan and plan.match) else "unknown"
    if sb_result.skipped:
        logger.info(f"  sandbox gate skipped: {sb_result.detail}")
        metrics.inc(
            "gate_outcome_total", outcome="skipped",
            runtime=runtime_label, reason=(sb_result.detail or "no_reason")[:40],
        )
        return GateOutcome.SKIPPED, ""

    if not sb_result.passed:
        metrics.inc("gate_outcome_total", outcome="retry", runtime=runtime_label)
        logger.warning(
            f"Attempt {attempt}: sandbox gate FAILED "
            f"({sb_result.verdict}) — {sb_result.detail}"
        )
        # The gate verdict (verbatim stdout tail + verdict + detail) is
        # already on ``candidate_eval["sandbox_eval"]`` from the line above,
        # so ``build_retry_feedback`` re-renders it via the structured path
        # rather than us passing it as a free-form hollow_reason string.
        # The big win: pass ``candidate`` so the LLM sees its own failing
        # JSON in the next-attempt feedback (no more "regenerate from
        # scratch + describe past bug" pathology).
        feedback = build_retry_feedback(
            [],
            candidate_eval,
            prior_candidate=candidate,
        )
        return GateOutcome.RETRY, feedback

    metrics.inc("gate_outcome_total", outcome="pass", runtime=runtime_label)
    return GateOutcome.PASS, ""
