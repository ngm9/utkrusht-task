"""Consolidated LLM judge + rewriter for content-quality checks.

ONE LLM call per attempt. The call BOTH (a) judges the candidate task
on every content-quality rule and (b) returns a corrected version of
every failing field. The runner splices the rewrites directly into the
candidate and proceeds to persistence — no retry is burned on
content-quality issues alone.

Rules covered by the prompt:

- ``title`` — human-readable Title Case (not the kebab `name` slug, not
  all-lowercase, not all-uppercase). Reference: "Design Voice Agent Eval
  Framework".
- ``short_overview`` — exactly 3 bullets in (artifact, goal, expected
  outcome) order; recruiter-readable; no leading bullet glyphs; no
  ``**X**:`` markers.
- ``outcomes`` and ``pre_requisites`` — candidate-readable sentences,
  each anchored to this specific task (no generic boilerplate); no
  leading bullet glyphs; no ``**X**:`` markers. No count cap.
- ``question`` — short and direct, between 120 and 1500 chars; setup
  detail belongs in the README.

Routes through the same Portkey → OpenAI path as ``infra/evals.py``.

A non-content error during the LLM call (transport, malformed JSON)
propagates as a plain ``Exception`` — the runner treats this as an
infra failure and aborts the attempt without writing artefacts.
"""
from __future__ import annotations

import json
from typing import Any

from infra.schemas import CONTENT_QUALITY_RESPONSE_SCHEMA


_SYSTEM_PROMPT = (
    "You are a senior assessment-content reviewer. Inspect the candidate "
    "task against an explicit content-quality rubric. For every field that "
    "violates a rule, list the issue AND emit a corrected version of that "
    "field. Return ONLY the structured JSON specified by the response schema."
)


_RUBRIC_PROMPT = """\
RULES — apply every one. For each rule, if the candidate fails, add an
entry to `issues_found` AND emit a corrected value in `rewrites`. If the
candidate already satisfies the rule, leave the corresponding rewrite
key as null.

(1) `title` — must be a human-readable Title Case phrase. It must contain
    at least one space, must not equal the kebab `name` slug, and must
    not be all-lowercase or all-uppercase. Connector words (a, an, the,
    of, to, in, on, for, and, or, with, by, at, vs) may be lowercase
    when they are not the first word.
    Positive example: "Design Voice Agent Eval Framework"
    Negative example: "voice-agent-eval-framework"

(2) `short_overview` — exactly THREE bullets, in this order:
    [0] describes the task artifact (what is being built)
    [1] describes the candidate goal (what the candidate has to do)
    [2] describes the expected outcome (what the world looks like when solved)
    These bullets are read by RECRUITERS — keep them crisp.
    Positive example:
      [0] "Build a production-grade event-driven pipeline for processing candidate assessment results reliably."
      [1] "The platform processes thousands of daily submissions but the current pipeline can silently drop submissions, produce duplicate results, and has no observability."
      [2] "Every submission is processed exactly once, scored results are published downstream, failed messages route to a dead-letter topic, and the entire pipeline is observable through structured logs."
    NO leading bullet glyphs (•, ‣, ▪, ▶, ◦, ⁃, -, *, –, —). NO numbered
    prefixes ("1. ", "1) ", "(1) "). NO residual Markdown markers like
    `**Goal**:` or `**Challenge**:` anywhere in the string.

(3) `outcomes` — bullets read by the CANDIDATE at task start. Every
    bullet must (a) be a complete candidate-readable sentence (starts
    with a capital, ends with terminal punctuation, ≥ 6 words), AND
    (b) anchor to this specific task (mention a concept from the title,
    question, competency names, or starter files — not generic
    boilerplate like "It works." or "Understanding of testing"). NO
    leading bullet glyphs, NO `**X**:` markers, NO blank items, NO
    duplicates. No upper bound on item count.

(4) `pre_requisites` — same rules as outcomes. A bullet such as
    "Familiarity with Python" on a task where Python is the assumed
    stack is too generic and must be rewritten to reference the
    specific concepts the candidate will actually use.

(5) `question` — the candidate-facing task statement. Must be short
    enough to read in a few seconds (between 120 and 1500 chars).
    Setup, background, and constraints belong in the README, not here.
    Positive example:
      "A streaming-events pipeline stores in-flight events as a singly
       linked list. Occasionally a buggy publisher links the tail of the
       list back to an earlier node, creating an infinite loop for any
       consumer that walks the list naively.

       Write a function has_cycle that takes the head node of a singly
       linked list and returns true if any node's next chain eventually
       revisits an earlier node, and false otherwise."

REWRITE GUIDANCE — the rewritten value MUST satisfy the rule it is
fixing. Preserve as much of the original wording as possible; change
only what the rule requires. Do not invent unrelated content.
"""


def _build_user_prompt(task: dict) -> str:
    competency_names = [
        c.get("name", "")
        for c in (task.get("criterias") or [])
        if isinstance(c, dict)
    ]
    return (
        _RUBRIC_PROMPT
        + "\n\nCANDIDATE TASK:\n"
        + json.dumps(
            {
                "title": task.get("title", ""),
                "name": task.get("name", ""),
                "question": task.get("question", ""),
                "competencies": competency_names,
                "pre_requisites": task.get("pre_requisites") or [],
                "outcomes": task.get("outcomes") or [],
                "short_overview": task.get("short_overview") or [],
            },
            indent=2,
        )
    )


def judge_and_rewrite_task_quality(
    task: dict,
    *,
    client: Any | None = None,
    model: str | None = None,
) -> dict:
    """Run the consolidated judge+rewriter on ``task``.

    Returns the raw response payload as a dict with the documented shape:

        {
            "issues_found": [{"field_path": str, "reason": str}, ...],
            "rewrites": {
                "title": str | None,
                "short_overview": list[str] | None,
                "outcomes": list[str] | None,
                "pre_requisites": list[str] | None,
                "question": str | None,
            },
        }

    Parameters
    ----------
    task: candidate task dict (top-level keys: title, name, question,
        pre_requisites, outcomes, short_overview, criterias).
    client: a Portkey-routed OpenAI client. Defaults to
        ``eval_openai_client`` from ``infra.evals``. Tests inject a MagicMock.
    model: model name. Defaults to ``EVAL_MODEL`` from ``infra.evals``.

    Raises
    ------
    Exception
        Transport error, parse failure, or empty response. The runner
        treats this as infra failure and aborts the attempt — no Supabase
        or GitHub write occurs.
    """
    if client is None or model is None:
        # Lazy import keeps the test harness from booting the Portkey client.
        from infra.evals import EVAL_MODEL, eval_openai_client
        client = client or eval_openai_client
        model = model or EVAL_MODEL

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(task)},
    ]

    try:
        response = client.responses.create(
            model=model,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": CONTENT_QUALITY_RESPONSE_SCHEMA["name"],
                    "schema": CONTENT_QUALITY_RESPONSE_SCHEMA["schema"],
                    "strict": CONTENT_QUALITY_RESPONSE_SCHEMA["strict"],
                },
            },
        )
    except Exception as exc:
        raise Exception(f"content-quality judge unreachable: {exc}") from exc

    raw = getattr(response, "output_text", None)
    if not raw:
        raise Exception("content-quality judge returned no output_text")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Exception(
            f"content-quality judge returned unparseable JSON: {exc}"
        ) from exc

    return payload
