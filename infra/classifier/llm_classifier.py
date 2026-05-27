"""Single-call LLM classifier.

Two entry points live here during Phase 2 of
``docs/plans/2026-05-27-unified-classifier-template-schema.md``:

* ``classify_with_llm`` (LEGACY) — emits ``TaskRuntime`` from competencies
  alone. Used by today's ``resolve_plan``. Phase 4 deletes it.
* ``classify_match_v2`` (NEW) — emits ``TaskTemplateMatch`` by picking
  one template_id from the active set's capability sheets. Used by
  ``resolve_plan_v2`` (Phase 2 next task).

Neither function knows about caching or persistence — that's
``runtime_resolver.py``'s job.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from pydantic import ValidationError

from infra.classifier.runtime import Competency, TaskRuntime, TaskTemplateMatch

_MODEL = "claude-sonnet-4-6"

_SYSTEM_PROMPT = """You classify a list of technical competencies into a \
structured infrastructure spec for an automated assessment platform.

For each input list of (competency name, proficiency) tuples, output a single \
JSON object with EXACTLY these fields:

  • runtime: one of "python","node","java","php","go","rust","flutter","ruby","scala","none"
             "none" only when the task is pure SQL (db_only) or non-code.
  • frameworks: array of named framework strings (e.g. ["fastapi"], ["spring-boot","hibernate"]).
                Empty list if no framework competency is present.
  • datastores: array of DB server names (e.g. ["postgres"], ["mongo","redis"]).
                Empty if the task does not need a database.
  • messaging: array of broker names (e.g. ["kafka"]). Empty if not applicable.
  • needs_browser: true for Playwright/Selenium/Cypress tasks; otherwise false.
  • kind: one of "app","script","mobile","frontend","testing","db_only","llm","vector_db","non_code".
  • confidence: a float in [0.0, 1.0] for how sure you are. Use < 0.7 if the
                input is ambiguous so a human can review.

CRITICAL: respond with ONLY the JSON object. No prose, no markdown fences, no
explanation. Any value not in the listed Literals is invalid."""

_RETRY_NUDGE_PREFIX = (
    "Your previous reply did not match the schema. "
    "Reply again with ONLY the JSON object — no prose, no markdown."
)


def _format_parse_error(exc: Exception) -> str:
    """Render a parse/validation exception as model-actionable feedback."""
    if isinstance(exc, ValidationError):
        return "; ".join(
            f"{'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
    return str(exc)


@dataclass(frozen=True)
class ClassifierResult:
    runtime: TaskRuntime
    confidence: float


def build_client() -> openai.OpenAI:
    """Portkey gateway → Anthropic, mirroring task_builder/conversation.py."""
    return openai.OpenAI(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="anthropic",
            api_key=os.getenv("PORTKEY_API_KEY"),
        ),
    )


def _user_message(competencies: list[Competency]) -> str:
    lines = "\n".join(f"- {c.name} ({c.proficiency})" for c in competencies)
    return f"Classify these competencies:\n\n{lines}"


def _extract_json(text: str) -> dict:
    """Find the first top-level JSON object in `text`."""
    start = text.find("{")
    if start == -1:
        raise ValueError("invalid JSON: no '{' found")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("invalid JSON: unbalanced braces")


def _parse(raw: str) -> ClassifierResult:
    """Parse raw LLM text into a ClassifierResult; raises ValueError on failure."""
    data = _extract_json(raw)
    confidence = float(data.pop("confidence", 1.0))
    runtime = TaskRuntime.model_validate(data)
    return ClassifierResult(runtime=runtime, confidence=confidence)


def classify_with_llm(
    competencies: list[Competency],
    *,
    client: openai.OpenAI | None = None,
) -> ClassifierResult:
    """Ask the LLM to classify these competencies. Retries once on bad JSON.

    Raises ValueError if the LLM still produces invalid JSON after the retry.
    """
    if not competencies:
        raise ValueError("classify_with_llm requires at least one competency")
    client = client or build_client()
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _user_message(competencies)},
    ]

    resp = client.chat.completions.create(model=_MODEL, messages=messages)
    raw = resp.choices[0].message.content or ""
    try:
        return _parse(raw)
    except (ValueError, ValidationError, json.JSONDecodeError) as first_err:
        error_detail = _format_parse_error(first_err)

    # Retry once with the specific error fed back to the model
    nudge_msg = f"{_RETRY_NUDGE_PREFIX} Specific errors: {error_detail}"
    nudge = messages + [
        {"role": "assistant", "content": raw or "(empty response)"},
        {"role": "user", "content": nudge_msg},
    ]
    resp = client.chat.completions.create(model=_MODEL, messages=nudge)
    raw = resp.choices[0].message.content or ""
    try:
        return _parse(raw)
    except (ValueError, ValidationError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON after retry: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────
# v2: classify against capability sheets, emit TaskTemplateMatch.
# Phase 2 of unified-classifier-template-schema.
# ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ActiveTemplate:
    """One built template's capability sheet, as the LLM sees it.

    Hydrated by ``runtime_resolver._load_active_templates`` from rows
    where ``templates.status = 'built'``.
    """

    template_id: str
    primary_runtime: str
    personas: list[str]
    eval_methods: list[str]
    capabilities: dict
    description: str | None = None


_SYSTEM_PROMPT_V2 = """You match a list of technical competencies to a \
deployable E2B template from the active set below.

ACTIVE TEMPLATES:
{templates_block}

YOUR JOB:
1. Read the competencies the user sends.
2. Pick the template_id (from the active set above) whose capabilities \
best match what these competencies imply the task will need.
3. Pick exactly ONE persona from that template's personas list — the \
reviewer specialty most appropriate for this combo.
4. Set confidence: a float in [0.0, 1.0]. Use < 0.7 when ambiguous so a \
human can review.

WHEN TO RETURN no_match:
- No active template's capabilities cover what the competencies need \
(e.g. "Kubernetes + Helm + Terraform" when no utkrusht-infra exists).
- DO NOT pick a template just because it shares one capability — if the \
core need isn't covered, return no_match.

When no_match: omit template_id and persona (use null), set \
no_match_reason (one short sentence explaining why nothing fits), set \
missing_capabilities (array of canonical names: \
["helm","kubectl","terraform"] etc.), and optionally suggest a future \
template name in suggested_template (e.g. "utkrusht-infra").

OUTPUT FORMAT: ONLY a JSON object with EXACTLY these fields. No prose, no \
markdown fences:

  • template_id: string (one of the active IDs) OR null
  • persona: string (one of the chosen template's personas) OR null
  • confidence: float in [0.0, 1.0]
  • no_match_reason: string (null if template_id is set)
  • missing_capabilities: array of strings (empty if template_id is set)
  • suggested_template: string (null if template_id is set)
"""


def _render_templates_block(active: list[ActiveTemplate]) -> str:
    """Format active templates as a numbered list of capability sheets."""
    if not active:
        return "  (no built templates available — every classification " \
               "must be no_match)"
    lines = []
    for tmpl in active:
        lines.append(f"\n- template_id: {tmpl.template_id}")
        lines.append(f"  primary_runtime: {tmpl.primary_runtime}")
        lines.append(f"  personas: {tmpl.personas}")
        lines.append(f"  eval_methods: {tmpl.eval_methods}")
        lines.append(f"  capabilities: {json.dumps(tmpl.capabilities, sort_keys=True)}")
        if tmpl.description:
            lines.append(f"  description: {tmpl.description}")
    return "\n".join(lines)


def _user_message_v2(competencies: list[Competency]) -> str:
    lines = "\n".join(f"- {c.name} ({c.proficiency})" for c in competencies)
    return f"Classify these competencies:\n\n{lines}"


def _validate_match_against_templates(
    match: TaskTemplateMatch,
    active_templates: list[ActiveTemplate],
) -> None:
    """Enforce the match references only known template_id + persona.

    Raises ``ValueError`` with a message suitable for feeding back to the
    model on retry.
    """
    if match.template_id is not None:
        active_by_id = {t.template_id: t for t in active_templates}
        if match.template_id not in active_by_id:
            raise ValueError(
                f"template_id {match.template_id!r} is not in the active "
                f"templates list. Allowed: {sorted(active_by_id)}"
            )
        tmpl = active_by_id[match.template_id]
        if match.persona is None:
            raise ValueError(
                f"template_id is set ({match.template_id!r}) but persona is "
                f"null. Pick one of {tmpl.personas}."
            )
        if match.persona not in tmpl.personas:
            raise ValueError(
                f"persona {match.persona!r} is not in template "
                f"{tmpl.template_id!r}'s personas. Allowed: {tmpl.personas}."
            )
    else:
        if not match.no_match_reason:
            raise ValueError(
                "template_id is null but no_match_reason is empty. Either "
                "pick a template_id or explain in no_match_reason."
            )


def _parse_match(raw: str) -> TaskTemplateMatch:
    """Parse raw LLM text into a TaskTemplateMatch."""
    data = _extract_json(raw)
    return TaskTemplateMatch.model_validate(data)


def classify_match_v2(
    competencies: list[Competency],
    active_templates: list[ActiveTemplate],
    *,
    client: openai.OpenAI | None = None,
) -> TaskTemplateMatch:
    """Pick a template_id + persona for a competency combo.

    Inputs:
      - competencies: the sorted, proficiency-suffixed competency list
      - active_templates: rows from ``templates WHERE status = 'built'``

    Output: a validated ``TaskTemplateMatch``. Either ``template_id`` is
    set (and persona is one of that template's personas), or
    ``no_match_reason`` is set.

    No scenario / background input — those go to the content-generation
    LLM, which separately emits ``TaskIntent`` per task.

    Raises ``ValueError`` if the LLM produces invalid JSON or references
    a non-existent template/persona, after one retry with feedback.
    """
    if not competencies:
        raise ValueError("classify_match_v2 requires at least one competency")

    client = client or build_client()
    system_prompt = _SYSTEM_PROMPT_V2.format(
        templates_block=_render_templates_block(active_templates),
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": _user_message_v2(competencies)},
    ]

    def _try_one(msgs: list[dict]) -> TaskTemplateMatch:
        resp = client.chat.completions.create(model=_MODEL, messages=msgs)
        raw = resp.choices[0].message.content or ""
        match = _parse_match(raw)
        _validate_match_against_templates(match, active_templates)
        return match

    try:
        return _try_one(messages)
    except (ValueError, ValidationError, json.JSONDecodeError) as first_err:
        error_detail = _format_parse_error(first_err)

    # Retry once with the specific error fed back to the model
    nudge_msg = f"{_RETRY_NUDGE_PREFIX} Specific errors: {error_detail}"
    nudge = messages + [
        {"role": "assistant", "content": "(previous reply was invalid)"},
        {"role": "user", "content": nudge_msg},
    ]
    try:
        return _try_one(nudge)
    except (ValueError, ValidationError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid match after retry: {exc}") from exc
