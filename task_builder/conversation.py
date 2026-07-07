"""Structured-output conversation engine (Approach B): one LLM call per turn."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import openai

from infra.llm_provider import make_llm_client, resolve_model
from infra.prompt_cache import cache_messages
from task_builder.prompts import SYSTEM_PROMPT
from task_builder.slots import Message, SessionState, TaskBrief, merge_brief
from task_builder.validation import validate_competency, validate_proficiency

# Provider-aware: claude-sonnet-4-6 for anthropic, the GLM slug for glm.
BOT_MODEL = resolve_model("bot")

_FALLBACK_REPLY = "Sorry — I got a bit confused there. Could you say that again?"


@dataclass(frozen=True)
class ConversationTurn:
    """One parsed bot turn."""

    reply: str
    slots_update: dict = field(default_factory=dict)
    ready_to_generate: bool = False


def build_bot_client() -> openai.OpenAI:
    """The active Claude-role client — Anthropic via Portkey, or GLM via
    OpenRouter when LLM_PROVIDER=glm. See infra/llm_provider."""
    return make_llm_client()


def _extract_json(text: str) -> dict:
    """Parse the first top-level JSON object from an LLM response.

    Tolerates leading/trailing prose. Raises ValueError if none is found.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in response")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unbalanced JSON object in response")


def _to_turn(parsed: dict) -> ConversationTurn:
    """Build a ConversationTurn from a parsed JSON dict, defaulting every field."""
    return ConversationTurn(
        reply=str(parsed.get("reply", "")).strip() or _FALLBACK_REPLY,
        slots_update=parsed.get("slots_update") or {},
        ready_to_generate=bool(parsed.get("ready_to_generate", False)),
    )


def _call(client: openai.OpenAI, messages: list[dict]) -> str:
    """Make one chat-completion call and return the raw response text."""
    resp = client.chat.completions.create(model=BOT_MODEL, messages=cache_messages(messages))
    return resp.choices[0].message.content or ""


def run_turn(client: openai.OpenAI, history: list[Message],
             user_message: str) -> ConversationTurn:
    """Run one conversation turn. Retries once on unparseable JSON, then degrades
    gracefully to a fallback reply rather than raising."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    raw = _call(client, messages)
    try:
        return _to_turn(_extract_json(raw))
    except (ValueError, json.JSONDecodeError):
        pass

    # Retry once. Insert the (bad) response as an assistant turn so the
    # message roles still alternate — the Anthropic API rejects two
    # consecutive user messages.
    nudge = messages + [
        {"role": "assistant", "content": raw or "(empty response)"},
        {"role": "user",
         "content": "Your last reply was not valid JSON. "
                    "Reply again with ONLY the JSON object."},
    ]
    try:
        return _to_turn(_extract_json(_call(client, nudge)))
    except (ValueError, json.JSONDecodeError):
        return ConversationTurn(reply=_FALLBACK_REPLY)


@dataclass
class ChatResult:
    """Result of one apply_turn call — the bot reply plus the current brief state."""

    reply: str
    brief: TaskBrief
    missing_slots: list[str]
    ready: bool


def _clean_slots_update(
    update: dict,
    supabase,
    current_proficiency: str | None = None,
) -> tuple[dict, list[str]]:
    """Validate a raw slots_update. Returns (accepted_fields, rejection_messages).

    Rejected fields are dropped — the server never stores an unvalidated value.

    current_proficiency: proficiency already established in the session (from a
    prior turn). Used as a fallback when validating competencies so that a tech
    stack given after the level is still accepted.
    """
    accepted: dict = {}
    rejections: list[str] = []

    if "proficiency" in update:
        check = validate_proficiency(str(update["proficiency"]))
        if check.ok:
            accepted["proficiency"] = check.cleaned
        else:
            rejections.append(check.error or "Invalid proficiency.")

    # competency validation needs a proficiency — prefer the just-accepted one,
    # falling back to whatever the session already holds.
    proficiency = accepted.get("proficiency") or current_proficiency
    if "competencies" in update and proficiency:
        names = update["competencies"] or []
        good: list[str] = []
        for name in names:
            check = validate_competency(str(name), proficiency, supabase)
            if check.ok:
                good.append(check.cleaned)
            else:
                hint = (f" Did you mean: {', '.join(check.suggestions)}?"
                        if check.suggestions else "")
                rejections.append((check.error or "Unknown competency.") + hint)
        if good:
            accepted["competencies"] = good

    for plain in ("role", "domain"):
        if update.get(plain):
            accepted[plain] = str(update[plain]).strip()
    if update.get("focus_areas"):
        accepted["focus_areas"] = [
            str(x).strip() for x in update["focus_areas"] if str(x).strip()
        ]
    count = update.get("scenario_count")
    if isinstance(count, int) and not isinstance(count, bool) and count > 0:
        accepted["scenario_count"] = count

    return accepted, rejections


def apply_turn(session: SessionState, user_message: str, *,
               client: openai.OpenAI, supabase) -> ChatResult:
    """Run one full chat turn: LLM call -> validate -> merge -> (corrective call)."""
    turn = run_turn(client, session.history, user_message)
    accepted, rejections = _clean_slots_update(
        turn.slots_update, supabase, current_proficiency=session.brief.proficiency
    )
    session.brief = merge_brief(session.brief, accepted)

    reply = turn.reply
    # If the server rejected something, give the bot one corrective turn so the
    # re-ask reaches the user inside this same response.
    if rejections:
        note = ("SERVER VALIDATION: the following values were rejected and NOT "
                "saved — " + " ".join(rejections) + " Ask the user to correct them.")
        corrective = run_turn(client, session.history,
                              user_message + "\n\n" + note)
        reply = corrective.reply

    session.history.append(Message(role="user", content=user_message))
    session.history.append(Message(role="assistant", content=reply))

    missing = session.brief.missing_slots()
    ready = turn.ready_to_generate and not missing
    return ChatResult(reply=reply, brief=session.brief,
                      missing_slots=missing, ready=ready)
