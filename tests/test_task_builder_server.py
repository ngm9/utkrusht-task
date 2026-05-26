"""FastAPI routes — chat (/api/session, /api/chat) and generation (/api/generate)."""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from task_builder.server import app
from task_builder.slots import TaskBrief


def _payload(reply: str, slots: dict, ready: bool) -> str:
    """Build a JSON string matching the bot's {reply, slots_update, ready_to_generate} contract."""
    return json.dumps({"reply": reply, "slots_update": slots,
                       "ready_to_generate": ready})


@pytest.fixture(autouse=True)
def _clear_sessions():
    """Reset the in-memory session store before and after every test."""
    from task_builder.server import SESSIONS
    SESSIONS.clear()
    yield
    SESSIONS.clear()


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_session_then_chat_flow():
    client = TestClient(app)
    fake_client = MagicMock()
    choice = MagicMock()
    choice.message.content = _payload("Hi! What stack?", {}, False)
    fake_client.chat.completions.create.return_value = MagicMock(choices=[choice])

    with patch("task_builder.server.build_bot_client", return_value=fake_client), \
         patch("task_builder.server.get_supabase", return_value=MagicMock()):
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


def test_chat_with_unknown_session_returns_404():
    client = TestClient(app)
    resp = client.post("/api/chat", json={"session_id": "nope", "message": "hi"})
    assert resp.status_code == 404


def test_generate_rejects_incomplete_brief():
    client = TestClient(app)
    session = client.post("/api/session").json()
    resp = client.post("/api/generate", json={"session_id": session["session_id"]})
    assert resp.status_code == 400  # brief not ready


def test_generate_starts_a_run_for_a_complete_brief():
    client = TestClient(app)
    session = client.post("/api/session").json()
    sid = session["session_id"]

    # Inject a complete brief directly into the session store.
    from task_builder.server import SESSIONS
    SESSIONS[sid].brief = TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["idempotency"], domain="fintech",
    )

    with patch("task_builder.server._launch_run") as launch:
        resp = client.post("/api/generate", json={"session_id": sid})
        assert resp.status_code == 200
        assert "run_id" in resp.json()
        launch.assert_called_once()


def _inject_complete_brief(sid: str) -> None:
    """Put a ready-to-generate brief into the session store."""
    from task_builder.server import SESSIONS
    SESSIONS[sid].brief = TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["idempotency"], domain="fintech",
    )


def test_generate_rejects_invalid_env():
    client = TestClient(app)
    sid = client.post("/api/session").json()["session_id"]
    _inject_complete_brief(sid)
    resp = client.post("/api/generate", json={"session_id": sid, "env": "staging"})
    assert resp.status_code == 400


def test_generate_passes_chosen_env_to_launch_run():
    client = TestClient(app)
    sid = client.post("/api/session").json()["session_id"]
    _inject_complete_brief(sid)

    with patch("task_builder.server._launch_run") as launch:
        resp = client.post("/api/generate", json={"session_id": sid, "env": "prod"})
        assert resp.status_code == 200
        launch.assert_called_once()
        # _launch_run(run_id, brief, env) — env is the 3rd positional arg.
        args, kwargs = launch.call_args
        assert (args[2] if len(args) > 2 else kwargs.get("env")) == "prod"


def test_generate_defaults_env_to_dev_when_omitted():
    client = TestClient(app)
    sid = client.post("/api/session").json()["session_id"]
    _inject_complete_brief(sid)

    with patch("task_builder.server._launch_run") as launch:
        resp = client.post("/api/generate", json={"session_id": sid})
        assert resp.status_code == 200
        args, kwargs = launch.call_args
        assert (args[2] if len(args) > 2 else kwargs.get("env")) == "dev"


def test_root_serves_the_task_builder_page():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Task Builder" in resp.text
    assert 'id="chat"' in resp.text
    assert 'id="msg"' in resp.text
