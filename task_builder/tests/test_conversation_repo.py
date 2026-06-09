"""Unit tests for task_builder.conversation_repo (B2)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from task_builder import conversation_repo
from task_builder.slots import Message, SessionState, TaskBrief


def test_create_conversation_returns_id():
    sb = MagicMock()
    sb.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "c1"}],
    )
    with patch.object(conversation_repo, "init_supabase", return_value=sb):
        out = conversation_repo.create_conversation(env="dev")
    assert out == "c1"
    payload = sb.table.return_value.insert.call_args[0][0]
    assert payload["status"] == "active"
    assert payload["messages"] == []
    assert "competencies" in payload["missing_slots"]


def test_load_session_returns_none_when_row_missing():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)
    with patch.object(conversation_repo, "init_supabase", return_value=sb):
        assert conversation_repo.load_session("dev", "c1") is None


def test_load_session_rebuilds_brief_and_history():
    row = {
        "id": "c1",
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ],
        "brief": {"competencies": ["Python"], "proficiency": "BASIC"},
        "status": "active",
    }
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=row)
    with patch.object(conversation_repo, "init_supabase", return_value=sb):
        session = conversation_repo.load_session("dev", "c1")
    assert session is not None
    assert session.session_id == "c1"
    assert len(session.history) == 2
    assert session.history[0].role == "user"
    assert session.brief.competencies == ["Python"]
    assert session.brief.proficiency == "BASIC"


def test_save_session_serialises_messages_and_brief():
    sb = MagicMock()
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "c1"}])
    session = SessionState(session_id="c1")
    session.history.append(Message(role="user", content="hi"))
    session.brief = TaskBrief(competencies=["Python"], proficiency="BASIC")

    with patch.object(conversation_repo, "init_supabase", return_value=sb):
        conversation_repo.save_session("dev", session)

    payload = sb.table.return_value.update.call_args[0][0]
    assert payload["messages"][0]["role"] == "user"
    assert payload["brief"]["proficiency"] == "BASIC"
    # missing_slots should still include the ones not yet provided
    assert "role" in payload["missing_slots"]


def test_mark_submitted_sets_status_and_timestamp():
    sb = MagicMock()
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "c1"}])
    with patch.object(conversation_repo, "init_supabase", return_value=sb):
        conversation_repo.mark_submitted("dev", "c1")
    payload = sb.table.return_value.update.call_args[0][0]
    assert payload["status"] == "submitted"
    assert "submitted_at" in payload
