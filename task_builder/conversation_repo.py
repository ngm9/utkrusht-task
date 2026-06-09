"""Persistence helpers for the ``conversations`` table — B2.

Wraps the chat dialogue + interview brief in a Supabase-backed row so the
task-builder UI survives a process restart and so the operator-facing
dialogue is recoverable for review or re-run.

The shape mirrors the ``conversations`` migration in the Utkrushta backend
repo (``supabase/migrations/20260530000001_create_conversations.sql``).
"""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Any

from generators.task.persistence import init_supabase
from task_builder.slots import Message, SessionState, TaskBrief

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _serialise_messages(history: list[Message]) -> list[dict[str, Any]]:
    return [{"role": m.role, "content": m.content} for m in history]


def _deserialise_messages(rows: list[dict[str, Any]] | None) -> list[Message]:
    if not rows:
        return []
    out: list[Message] = []
    for row in rows:
        role = row.get("role")
        content = row.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            out.append(Message(role=role, content=content))
    return out


def create_conversation(env: str = "dev", started_by: str | None = None) -> str:
    """INSERT an empty active conversation; return its uuid.

    ``started_by`` is the verified testmaker UUID forwarded by the Next.js
    admin proxy via ``X-Testmaker-Id``. When None (local dev / unauthenticated
    direct hit) the column stays NULL.
    """
    sb = init_supabase(env)
    payload: dict[str, Any] = {
        "messages": [],
        "missing_slots": list(TaskBrief().missing_slots()),
        "status": "active",
    }
    if started_by:
        payload["started_by"] = started_by
    result = sb.table("conversations").insert(payload).execute()
    if not result.data:
        raise RuntimeError("create_conversation: Supabase returned no row")
    return str(result.data[0]["id"])


def load_session(env: str, conversation_id: str) -> SessionState | None:
    """Reconstruct a SessionState from a row. None when the row is gone."""
    sb = init_supabase(env)
    result = (
        sb.table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .single()
        .execute()
    )
    row = result.data
    if not row:
        return None
    session = SessionState(session_id=str(row["id"]))
    session.history = _deserialise_messages(row.get("messages"))
    brief_dict = row.get("brief") or {}
    if brief_dict:
        try:
            session.brief = TaskBrief(**brief_dict)
        except Exception as exc:
            logger.warning(
                "conversation %s brief deserialise failed (%s) — starting fresh",
                conversation_id, exc,
            )
    return session


def save_session(env: str, session: SessionState) -> None:
    """Patch the row with the latest history + brief + missing slots."""
    sb = init_supabase(env)
    payload = {
        "messages": _serialise_messages(session.history),
        "brief": session.brief.model_dump(),
        "missing_slots": session.brief.missing_slots(),
    }
    sb.table("conversations").update(payload).eq("id", session.session_id).execute()


def mark_submitted(env: str, conversation_id: str) -> None:
    """Flip status to 'submitted' when /api/generate fires."""
    sb = init_supabase(env)
    sb.table("conversations").update({
        "status": "submitted",
        "submitted_at": _now_iso(),
    }).eq("id", conversation_id).execute()


def mark_abandoned(env: str, conversation_id: str) -> None:
    """Flip status to 'abandoned' — used by the nightly sweep."""
    sb = init_supabase(env)
    sb.table("conversations").update({
        "status": "abandoned",
        "abandoned_at": _now_iso(),
    }).eq("id", conversation_id).execute()
