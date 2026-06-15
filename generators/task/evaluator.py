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

import json
import re
from typing import Dict, Optional

from infra.evals import llm_code_eval, llm_task_eval

from generators.task._clients import openai_client


# Proficiency → (years-of-experience phrase, time budget in minutes). The
# task-eval PROFICIENCY FIT critic (infra/evals.py Criterion 2) needs a
# CONCRETE experience target to validate task complexity against — a blank YoE
# makes it fail the criterion. The old code read yoe from
# ``task_data["background"]["yoe"]``, a key the task-gen path never populates,
# so yoe was ALWAYS "" → a deterministic PROFICIENCY FIT failure no retry could
# fix. Derive it here instead, and keep the time budget in the SAME table so
# the YoE and the minutes the critic sees always agree.
PROFICIENCY_PROFILE: dict[str, tuple[str, int]] = {
    "ADVANCED": ("6+ years", 25),
    "INTERMEDIATE": ("3-5 years", 20),
    "BASIC": ("1-2 years", 15),
}


def proficiency_profile(proficiency: str) -> tuple[str, int]:
    """Return ``(yoe_phrase, time_budget_minutes)`` for a proficiency level.

    Falls back to the BASIC profile for unknown / blank levels.
    """
    return PROFICIENCY_PROFILE.get(
        (proficiency or "").upper(), PROFICIENCY_PROFILE["BASIC"]
    )


# Criterion numbers whose inputs the task-gen LLM CANNOT change on a retry,
# because we stamp them deterministically: Criterion 2 (PROFICIENCY FIT) reads
# the code-derived YoE + time budget, and Criterion 5 (CRITERIA COVERAGE) reads
# the code-stamped ``criterias`` (creator.py sets ``candidate["criterias"]``
# from the declared competencies). When an eval fails ONLY on these, the inputs
# are identical next time, so a full regeneration is wasted spend.
_DETERMINISTIC_BLOCKER_RE = re.compile(
    r"criterion\s*2\b|criterion\s*5\b|proficiency\s*fit|criteria\s*coverage",
    re.I,
)


def blockers_are_deterministic_only(eval_info: Dict) -> bool:
    """True when an eval failure is attributable ONLY to deterministic-metadata
    criteria (PROFICIENCY FIT / CRITERIA COVERAGE) and the code eval passed.

    Those criteria gate on fields the generator does not control — YoE, time
    budget and ``criterias`` are all code-stamped — so a full regeneration
    cannot change them; the failure is judge variance. The retry loop uses this
    to re-score the SAME candidate cheaply instead of re-rolling a fresh task.

    Returns False if there are no blockers, if the code eval failed, or if any
    task blocker references a content criterion (1/3/4/6) — those ARE fixable
    by regeneration and must keep their normal retry path.
    """
    task_eval = eval_info.get("task_eval", {}) or {}
    code_eval = eval_info.get("code_eval", {}) or {}
    if not code_eval.get("pass", False):
        return False
    blockers = task_eval.get("blocking_issues") or []
    if not blockers:
        return False
    return all(_DETERMINISTIC_BLOCKER_RE.search(str(b)) for b in blockers)


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

# Cap on how much of the prior task JSON we re-feed to the LLM. Most failed
# candidates are 15-25 KB; 60 KB is enough headroom to keep code_files intact
# without blowing the context budget on a 3-prompt-template + retry turn.
_PRIOR_CANDIDATE_CHAR_CAP = 60_000


def _format_prior_candidate(candidate: Optional[Dict]) -> str:
    """Render the failing candidate's JSON for re-feeding into the next attempt.

    Returns '' when ``candidate`` is None / falsy. Truncates payloads larger
    than ``_PRIOR_CANDIDATE_CHAR_CAP`` chars to keep token budget bounded.
    Truncation is conservative — the bug-fix LLM gets the same top-level
    structure and either the full or a clearly-marked partial code body.
    """
    if not candidate:
        return ""
    try:
        body = json.dumps(candidate, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        # Fall back to a shallow repr if the candidate has un-serialisable
        # nested values — better than dropping the prior context entirely.
        body = repr(candidate)
    if len(body) > _PRIOR_CANDIDATE_CHAR_CAP:
        head = body[: _PRIOR_CANDIDATE_CHAR_CAP]
        body = (
            head
            + f"\n…[truncated; original was {len(body):,} chars, kept first "
            f"{_PRIOR_CANDIDATE_CHAR_CAP:,}]"
        )
    return body


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
    hollow_reasons: list[str],
    eval_info: Optional[Dict],
    prior_candidate: Optional[Dict] = None,
) -> str:
    """Compose the feedback message handed to the next generation attempt.

    ``prior_candidate`` is the FAILING task JSON from the previous attempt.
    When supplied it is embedded verbatim in the feedback so the LLM can
    patch its own concrete output rather than re-rolling a fresh task that
    bears no relation to the bug being reported. This is the convergence
    fix — without it, each attempt regenerates from scratch and the feedback
    references a task the LLM never produced (the F12-class "different bug
    every attempt" pathology).

    The instructions explicitly tell the model:
      * stay with the SAME scenario as the prior attempt
      * patch the specific files mentioned in the failure detail
      * do NOT regenerate from scratch

    Without ``prior_candidate``, falls back to the legacy textual-only
    feedback (used by tests + the hollow-output path where no candidate
    exists yet).
    """
    parts = [
        "PREVIOUS ATTEMPT FAILED. PATCH your prior task JSON — do NOT regenerate "
        "from scratch and do NOT switch scenarios. Keep the same name, the same "
        "scenario, and the same file layout; fix only what the failure detail "
        "below identifies."
    ]
    if hollow_reasons:
        parts.append(
            "Problem: the response was hollow — " + "; ".join(hollow_reasons) + "."
        )
        parts.append(_CANONICAL_KEYS_REMINDER)
    if eval_info:
        te = eval_info.get("task_eval", {})
        ce = eval_info.get("code_eval", {})

        def _blockers(d: Dict) -> list[str]:
            """Prefer blocking_issues (new schema) over legacy issues."""
            return list(d.get("blocking_issues") or d.get("issues") or [])

        if not te.get("pass", True):
            detail = (
                "; ".join(_blockers(te))
                or te.get("feedback")
                or "unspecified"
            )
            parts.append(f"Task eval FAILED — {detail}")
        if not ce.get("pass", True):
            detail = (
                "; ".join(_blockers(ce))
                or ce.get("feedback")
                or "unspecified"
            )
            parts.append(f"Code eval FAILED — {detail}")
        sandbox = eval_info.get("sandbox_eval")
        if isinstance(sandbox, dict) and sandbox.get("passed") is False \
                and not sandbox.get("skipped"):
            verdict = sandbox.get("verdict") or "unknown"
            detail = sandbox.get("detail") or ""
            tail = sandbox.get("stdout_tail") or ""
            parts.append(
                f"E2B sandbox gate FAILED ({verdict}): {detail}\n"
                f"Sandbox stdout tail (most-recent error first):\n{tail}"
            )

    prior_blob = _format_prior_candidate(prior_candidate)
    if prior_blob:
        parts.append(
            "Below is the EXACT JSON you sent on the failing attempt. Find the "
            "specific files / sections that caused the failure and edit ONLY "
            "those. Resend the full corrected JSON with the same top-level "
            "keys.\n\n"
            "=== PRIOR FAILED CANDIDATE (yours, verbatim) ===\n"
            f"{prior_blob}\n"
            "=== END PRIOR FAILED CANDIDATE ==="
        )

    parts.append(
        "Address every issue above by editing the prior JSON in place. "
        "Return ONLY the corrected JSON object (no prose, no markdown fences)."
    )
    return "\n\n".join(parts)


def run_evaluations(
    task_data: Dict,
    persona: Optional[str] = None,
    scenarios: Optional[list[str]] = None,
) -> Dict:
    """Run the LLM-based eval critics on the task and code.

    When ``persona`` is supplied (one of the matched template's personas, e.g.
    ``"backend"`` / ``"dba"`` / ``"mle"``), both eval critics receive a
    domain-specific persona prompt prepended to their generic checklist —
    a senior DBA reviews db-heavy tasks, a senior MLE reviews LLM/RAG tasks,
    etc. Falls back to the plain prompt when ``persona`` is ``None``.

    ``scenarios`` is the list of real-world scenarios that were fed into the
    task-generation LLM. Threaded into ``llm_task_eval`` so Criterion 6
    (DOMAIN ALIGNMENT) can detect when the generated task drifted into the
    employer's domain instead of using one of the provided scenarios.
    """
    prof_levels = [
        criteria["proficiency"].upper()
        for criteria in task_data.get("criterias", [])
    ]
    # Judge a mixed-level combo at its ceiling, then derive BOTH the YoE phrase
    # and the time budget from the same profile so the PROFICIENCY FIT critic
    # always sees a concrete, self-consistent experience target. (The old
    # `background.yoe` lookup was always blank — see PROFICIENCY_PROFILE.)
    if "ADVANCED" in prof_levels:
        prof = "ADVANCED"
    elif "INTERMEDIATE" in prof_levels:
        prof = "INTERMEDIATE"
    else:
        prof = "BASIC"
    yoe, time_constraint = proficiency_profile(prof)

    task_eval_result = llm_task_eval(
        task_data,
        prof,
        yoe,
        time_constraint,
        openai_client,
        persona=persona,
        scenarios=scenarios,
    )

    code_eval_result = llm_code_eval(
        task_data.get("code_files", {}),
        task_data.get("description", ""),
        openai_client,
        persona=persona,
    )

    # Preserve every field the critic emitted so the retry loop can feed
    # concrete failure detail back into the next attempt instead of
    # re-rolling blind. blocking_issues drives retry; suggestions are
    # informational only — see infra/schemas.py:EVAL_RESPONSE_SCHEMA.
    def _pack(result: Dict) -> Dict:
        return {
            "pass": result.get("pass", False),
            "validated_criteria": result.get("validated_criteria", []),
            # Layer B (blocking vs nice-to-have) — primary fields the
            # retry feedback reads.
            "blocking_issues": result.get("blocking_issues", []),
            "suggestions": result.get("suggestions", []),
            # Legacy mirror so callers that still read .issues continue
            # to work without migration churn.
            "issues": result.get("issues", []),
            "feedback": result.get("feedback", ""),
        }

    return {
        "task_eval": _pack(task_eval_result),
        "code_eval": _pack(code_eval_result),
    }
