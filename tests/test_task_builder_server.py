"""FastAPI routes — chat (/api/session, /api/chat) and generation (/api/generate).

A4 + B2: conversations are persisted to Supabase (mocked here via in-memory
fakes) and runs are enqueued onto the ``generation_jobs`` table rather than
spawned as in-process threads.
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from task_builder import server
from task_builder.slots import SessionState, TaskBrief


def _payload(reply: str, slots: dict, ready: bool) -> str:
    """Bot reply matching the {reply, slots_update, ready_to_generate} contract."""
    return json.dumps({"reply": reply, "slots_update": slots,
                       "ready_to_generate": ready})


@pytest.fixture
def fake_conversations():
    """In-memory replacement for the conversations Supabase table."""
    store: dict[str, SessionState] = {}

    def fake_create(env="dev", started_by=None):
        sid = f"conv-{len(store) + 1}"
        store[sid] = SessionState(session_id=sid)
        return sid

    def fake_load(env, sid):
        return store.get(sid)

    def fake_save(env, session):
        store[session.session_id] = session

    with patch.object(server, "create_conversation", side_effect=fake_create), \
         patch.object(server, "load_session", side_effect=fake_load), \
         patch.object(server, "save_session", side_effect=fake_save), \
         patch.object(server, "mark_submitted"):
        yield store


def _complete_brief() -> TaskBrief:
    return TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["idempotency"], domain="fintech",
    )


def test_health_endpoint():
    resp = TestClient(server.app).get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_session_then_chat_flow(fake_conversations):
    client = TestClient(server.app)
    bot = MagicMock()
    choice = MagicMock()
    choice.message.content = _payload("Hi! What stack?", {}, False)
    bot.chat.completions.create.return_value = MagicMock(choices=[choice])

    with patch.object(server, "build_bot_client", return_value=bot), \
         patch.object(server, "get_supabase", return_value=MagicMock()):
        session = client.post("/api/session").json()
        assert "session_id" in session

        chat_resp = client.post("/api/chat", json={
            "session_id": session["session_id"],
            "message": "I want a task",
        }).json()
        assert "reply" in chat_resp
        assert "brief" in chat_resp
        assert "missing_slots" in chat_resp
        assert chat_resp["ready"] is False


def test_chat_with_unknown_session_returns_404(fake_conversations):
    client = TestClient(server.app)
    resp = client.post("/api/chat", json={"session_id": "nope", "message": "hi"})
    assert resp.status_code == 404


def test_generate_rejects_incomplete_brief(fake_conversations):
    client = TestClient(server.app)
    session = client.post("/api/session").json()
    resp = client.post("/api/generate", json={"session_id": session["session_id"], "env": "dev"})
    assert resp.status_code == 400


def test_generate_starts_a_run_for_a_complete_brief(fake_conversations):
    client = TestClient(server.app)
    sid = client.post("/api/session").json()["session_id"]
    fake_conversations[sid].brief = _complete_brief()

    with patch.object(server, "enqueue_job", return_value="job-1") as enqueue:
        resp = client.post("/api/generate", json={"session_id": sid, "env": "dev"})
        assert resp.status_code == 200
        assert resp.json()["run_id"] == "job-1"
        enqueue.assert_called_once()


def test_generate_rejects_invalid_env(fake_conversations):
    client = TestClient(server.app)
    sid = client.post("/api/session").json()["session_id"]
    fake_conversations[sid].brief = _complete_brief()
    resp = client.post("/api/generate", json={"session_id": sid, "env": "staging"})
    assert resp.status_code == 400


def test_generate_passes_chosen_env_to_enqueue(fake_conversations):
    client = TestClient(server.app)
    sid = client.post("/api/session").json()["session_id"]
    fake_conversations[sid].brief = _complete_brief()

    with patch.object(server, "enqueue_job", return_value="job-2") as enqueue:
        resp = client.post("/api/generate", json={"session_id": sid, "env": "prod"})
        assert resp.status_code == 200
        assert enqueue.call_args.kwargs["env"] == "prod"


def test_generate_defaults_env_explicitly_required(fake_conversations):
    """The new API requires `env` in the body (no implicit dev). The Pydantic
    model defaults env='dev' if omitted, so this test verifies that the
    default still flows through to enqueue."""
    client = TestClient(server.app)
    sid = client.post("/api/session").json()["session_id"]
    fake_conversations[sid].brief = _complete_brief()

    with patch.object(server, "enqueue_job", return_value="job-3") as enqueue:
        resp = client.post("/api/generate", json={"session_id": sid})
        assert resp.status_code == 200
        assert enqueue.call_args.kwargs["env"] == "dev"


def test_root_serves_the_task_builder_page():
    resp = TestClient(server.app).get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Task Builder" in resp.text
    assert 'id="chat"' in resp.text
    assert 'id="msg"' in resp.text
