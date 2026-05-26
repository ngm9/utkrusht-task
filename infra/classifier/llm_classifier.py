"""Single-call LLM classifier that emits a validated TaskRuntime.

This module owns ONE concern: take a list of competencies, ask an LLM, parse
the response, return a (TaskRuntime, confidence) pair. It does NOT know about
caching or persistence — that's runtime_cache.py's job.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from pydantic import ValidationError

from infra.classifier.runtime import Competency, TaskRuntime

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
