"""LLM-based evaluation of generated tasks + retry-feedback helpers.

Owns three things lifted from ``multiagent.py`` unchanged in behaviour:

* ``is_task_hollow`` — guards against placeholder rows (empty title /
  question / code_files) before the LLM evals run.
* ``build_retry_feedback`` — composes the corrective feedback the next
  generation attempt sees when a previous attempt failed.
* ``run_evaluations`` — runs the persona-routed task + code eval critics
  and returns the structured ``eval_info`` dict the retry loop consumes.

Structural diff from the old multiagent.py code: the openai client and
the eval model come from ``task_generation._clients`` instead of module
globals here.
"""
from __future__ import annotations

from typing import Dict, Optional

from evals import llm_code_eval, llm_task_eval

from task_generation._clients import EVAL_MODEL, openai_client


# Reminder appended to retry feedback whenever output was hollow — the
# hollow failure mode is almost always a synonym-key mistake (task_title /
# files / context instead of name / code_files / question).
_CANONICAL_KEYS_REMINDER = (
    'The response MUST be ONE JSON object using these EXACT top-level keys: '
    '"name" (string), "question" (string), "code_files" (object: filepath -> '
    'file contents), "answer", "outcomes", "short_overview", "pre_requisites", '
    '"hints", "definitions". Do NOT use synonym names such as "task_title", '
    '"files", "context", or "candidate_instructions" — synonyms make the task '
    'unusable.'
)


def is_task_hollow(task_data: Dict) -> tuple[bool, list[str]]:
    """Return ``(is_hollow, reasons)``.

    A task is *hollow* when any required field is empty — guards Supabase
    against placeholder rows when the LLM produces a structurally-shaped but
    content-empty response.
    """
    reasons: list[str] = []
    title = (task_data.get("title") or task_data.get("name") or "").strip()
    question = (task_data.get("question") or "").strip()
    code = task_data.get("code_files") or {}
    if not title:
        reasons.append("title is empty")
    if not question:
        reasons.append("question is empty")
    if not code:
        reasons.append("code_files is empty")
    return (bool(reasons), reasons)


def build_retry_feedback(
    hollow_reasons: list[str], eval_info: Optional[Dict]
) -> str:
    """Compose the feedback message handed to the next generation attempt.

    Concrete failure detail (hollow reasons, eval issues) so the LLM corrects
    its own prior output rather than re-rolling blind.
    """
    parts = [
        "PREVIOUS ATTEMPT FAILED. Correct it and return the full task JSON again."
    ]
    if hollow_reasons:
        parts.append(
            "Problem: the response was hollow — " + "; ".join(hollow_reasons) + "."
        )
        parts.append(_CANONICAL_KEYS_REMINDER)
    if eval_info:
        te = eval_info.get("task_eval", {})
        ce = eval_info.get("code_eval", {})
        if not te.get("pass", True):
            detail = (
                "; ".join(te.get("issues") or [])
                or te.get("feedback")
                or "unspecified"
            )
            parts.append(f"Task eval FAILED — {detail}")
        if not ce.get("pass", True):
            detail = (
                "; ".join(ce.get("issues") or [])
                or ce.get("feedback")
                or "unspecified"
            )
            parts.append(f"Code eval FAILED — {detail}")
    parts.append("Address every issue above. Return ONLY the corrected JSON object.")
    return "\n\n".join(parts)


def run_evaluations(task_data: Dict, kind: Optional[str] = None) -> Dict:
    """Run the LLM-based eval critics on the task and code.

    When ``kind`` is supplied (one of the ``TaskRuntime.kind`` values from
    ``prompt_generator.runtime``), both eval critics receive a domain-specific
    persona prompt prepended to their generic checklist — a senior DBA reviews
    db_only tasks, a senior MLE reviews llm tasks, etc. Falls back to the
    plain prompt when ``kind`` is ``None``.
    """
    prof_levels = [
        criteria["proficiency"].upper()
        for criteria in task_data.get("criterias", [])
    ]
    yoe = task_data.get("background", {}).get("yoe", "")
    time_constraint = (
        25 if "ADVANCED" in prof_levels
        else 20 if "INTERMEDIATE" in prof_levels
        else 15
    )

    task_eval_result = llm_task_eval(
        task_data,
        prof_levels[-1] if prof_levels else "BASIC",
        yoe,
        time_constraint,
        openai_client,
        EVAL_MODEL,
        kind=kind,
    )

    code_eval_result = llm_code_eval(
        task_data.get("code_files", {}),
        task_data.get("description", ""),
        openai_client,
        EVAL_MODEL,
        kind=kind,
    )

    # Preserve ``issues`` and ``feedback`` (not just ``pass``) so the retry
    # loop can feed concrete failure detail back into the next attempt
    # instead of re-rolling blind.
    return {
        "task_eval": {
            "pass": task_eval_result.get("pass", False),
            "validated_criteria": task_eval_result.get("validated_criteria", []),
            "issues": task_eval_result.get("issues", []),
            "feedback": task_eval_result.get("feedback", ""),
        },
        "code_eval": {
            "pass": code_eval_result.get("pass", False),
            "validated_criteria": code_eval_result.get("validated_criteria", []),
            "issues": code_eval_result.get("issues", []),
            "feedback": code_eval_result.get("feedback", ""),
        },
    }
