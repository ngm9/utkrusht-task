"""E2B build/test gate invocation for the create-task retry loop.

Wraps the *policy* of "when do we run the gate and what does the loop do
with the result" — separates that from the gate's own mechanics, which live
in ``e2b_flow/sandbox_eval``.

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

from enum import Enum
from typing import Dict, Optional, Tuple

from logger_config import logger

from e2b_flow.sandbox_eval import run_sandbox_eval, sandbox_eval_enabled
from task_generation.evaluator import build_retry_feedback
from task_generation.runtime_resolver import ResolvedPlan


class GateOutcome(Enum):
    """What the retry loop should do after the gate runs."""

    PASS = "pass"          # gate ran and passed → proceed to storage
    SKIPPED = "skipped"    # gate produced no verdict → proceed to storage
    DISABLED = "disabled"  # SANDBOX_EVAL_ENABLED is off → proceed to storage
    RETRY = "retry"        # gate FAILED → retry generation with feedback


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
        return GateOutcome.DISABLED, ""

    task_runtime = plan.task_runtime if plan else None
    logger.info("Running E2B sandbox build/test gate")
    sb_result = run_sandbox_eval(candidate.get("code_files", {}), task_runtime)
    candidate_eval["sandbox_eval"] = sb_result.as_dict()

    if sb_result.skipped:
        logger.info(f"  sandbox gate skipped: {sb_result.detail}")
        return GateOutcome.SKIPPED, ""

    if not sb_result.passed:
        logger.warning(
            f"Attempt {attempt}: sandbox gate FAILED "
            f"({sb_result.verdict}) — {sb_result.detail}"
        )
        feedback = build_retry_feedback(
            [
                f"E2B sandbox build/test gate failed "
                f"({sb_result.verdict}): {sb_result.detail} "
                f"{sb_result.stdout_tail}".strip()
            ],
            candidate_eval,
        )
        return GateOutcome.RETRY, feedback

    return GateOutcome.PASS, ""
