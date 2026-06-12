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

from infra.e2b.sandbox_eval import run_sandbox_eval, sandbox_eval_enabled
from generators.task.evaluator import build_retry_feedback
from generators.task.runtime_resolver import ResolvedPlan


class GateOutcome(Enum):
    """What the retry loop should do after the gate runs."""

    PASS = "pass"          # gate ran and passed → proceed to storage
    SKIPPED = "skipped"    # gate produced no verdict → proceed to storage
    DISABLED = "disabled"  # SANDBOX_EVAL_ENABLED is off → proceed to storage
    RETRY = "retry"        # gate FAILED → retry generation with feedback


def _eval_with_infra_retry(plan, candidate):
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
) -> Tuple[GateOutcome, str]:
    """Run the E2B build/test gate for one ``create_task`` attempt.

    Mutates ``candidate_eval`` to add the ``sandbox_eval`` verdict dict when
    the gate actually ran a verdict. Returns the outcome the retry loop
    should act on, plus the retry-feedback string (empty unless ``RETRY``).

    Behind ``SANDBOX_EVAL_ENABLED`` — when off, returns ``DISABLED``
    immediately and the loop proceeds to storage exactly as before the
    gate existed.
    """
    if not sandbox_eval_enabled():
        metrics.inc("gate_outcome_total", outcome="disabled")
        return GateOutcome.DISABLED, ""

    logger.info("Running E2B run.sh readiness gate")
    # ``plan`` carries both the runtime AND the template recipe
    # (``plan.template.build_cmd`` / ``test_cmd`` / ``compile_cmd``) so the
    # gate falls back to the legacy build/test path cleanly if ``run.sh``
    # is absent. The primary gate is the candidate's own ``run.sh`` (LLM-free
    # at the gate, key-gated ping in their session).
    sb_result = _eval_with_infra_retry(plan, candidate)
    candidate_eval["sandbox_eval"] = sb_result.as_dict()

    runtime_label = (plan.match.template_id or plan.match.suggested_template or "unknown") if plan else "unknown"
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
