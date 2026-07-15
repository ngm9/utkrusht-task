"""LLM-written 'instructions' suggestion chips for the Task Builder review step.

Lifted from trace_ui/server.py (_suggest_instructions / _parse_suggestions) so
the task_builder review step can offer the same competency-tailored directive
chips the trace-UI "New run" modal shows. The directive is the AUTHORITATIVE
free-text input the prompt stage consumes (``--instructions``) — it shapes the
task (force infra vs non-infra, require a dependency like Redis, add a
deliverable, cover an edge case).
"""
from __future__ import annotations

import json
import logging

from infra.llm_provider import make_llm_client, resolve_model

logger = logging.getLogger("task_builder.suggestions")

# Bounded in-process cache so re-opening the review step for the same combo
# doesn't re-hit the LLM. Keyed by (sorted names, proficiency).
_CACHE: dict[tuple, list[str]] = {}
_CACHE_MAX = 128

VALID_PROFICIENCIES = ("BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED")


def _parse_suggestions(text: str) -> list[str]:
    """Best-effort: pull a JSON array of strings from the LLM reply; fall back to
    bullet/numbered lines. Never raises."""
    if not text:
        return []
    t = text.strip()
    if t.startswith("```"):  # strip a ```json … ``` fence
        parts = t.split("```")
        t = parts[1] if len(parts) >= 2 else t.strip("`")
        if t.lstrip().lower().startswith("json"):
            t = t.lstrip()[4:]
    start, end = t.find("["), t.rfind("]")
    if start != -1 and end > start:
        try:
            arr = json.loads(t[start:end + 1])
            out = [str(s).strip() for s in arr if str(s).strip()]
            if out:
                return out[:6]
        except ValueError:
            pass
    lines = []
    for ln in text.splitlines():
        ln = ln.strip().lstrip("-*0123456789.) ").strip().strip('"').strip()
        if len(ln) > 8:
            lines.append(ln)
    return lines[:6]


def _suggest(names: list[str], proficiency: str) -> list[str]:
    """LLM-written, competency-tailored instruction directives (≤6 short ones).
    Uses the active Claude-role provider's cheaper model (Anthropic or GLM)."""
    combo = ", ".join(names)
    sys_prompt = (
        "You help an assessment author write a short 'instructions' directive that "
        "shapes how a realistic coding assessment task is generated. A good directive "
        "is concrete and actionable: a required deliverable/artifact, a sub-feature to "
        "implement, an infra dependency to include, or an edge case to cover."
    )
    user_prompt = (
        f"Competency/competencies: {combo} (proficiency: {proficiency}).\n"
        "Propose 4 distinct, concrete instruction directives an author could attach to "
        "the task generator for THIS competency at THIS proficiency. Each must be ONE "
        "sentence, specific, and immediately usable. Return ONLY a JSON array of "
        "strings — no prose, no markdown."
    )
    client = make_llm_client()
    resp = client.chat.completions.create(
        model=resolve_model("repair"),
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
    )
    text = (resp.choices[0].message.content or "") if resp.choices else ""
    return _parse_suggestions(text)


def suggest_instructions(names: list[str], proficiency: str) -> list[str]:
    """Cached wrapper around ``_suggest``. Raises on LLM failure — the caller
    soft-handles so the review step degrades to a plain textarea."""
    prof = (proficiency or "").upper()
    if prof not in VALID_PROFICIENCIES:
        prof = "BASIC"
    key = (tuple(sorted(names)), prof)
    if key in _CACHE:
        return _CACHE[key]
    suggestions = _suggest(names, prof)
    if suggestions:
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[key] = suggestions
    return suggestions
