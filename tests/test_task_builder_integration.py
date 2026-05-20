"""End-to-end: session → multi-turn chat → complete brief → generate (mocked LLM)."""
import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from task_builder.server import app, SESSIONS


def _bot(reply, slots, ready):
    choice = MagicMock()
    choice.message.content = json.dumps({
        "reply": reply, "slots_update": slots, "ready_to_generate": ready,
    })
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def _supabase_ok():
    sb = MagicMock()
    table = sb.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = \
        MagicMock(data=[{"name": "Java"}])
    return sb


def test_full_conversation_to_ready_then_generate():
    client = TestClient(app)
    with patch("task_builder.server.get_supabase", return_value=_supabase_ok()), \
         patch("task_builder.server._launch_run") as launch:
        sid = client.post("/api/session").json()["session_id"]

        # Turn 1: collect proficiency + competencies.
        with patch("task_builder.server.build_bot_client",
                   return_value=_bot("ok", {"proficiency": "BASIC",
                                            "competencies": ["Java"]}, False)):
            client.post("/api/chat", json={"session_id": sid, "message": "java basic"})

        # Turn 2: fill the rest and mark ready.
        with patch("task_builder.server.build_bot_client",
                   return_value=_bot("Ready!", {"role": "Backend Engineer",
                                                "focus_areas": ["idempotency"],
                                                "domain": "fintech"}, True)):
            final = client.post("/api/chat", json={
                "session_id": sid, "message": "backend, idempotency, fintech",
            }).json()

        assert final["ready"] is True
        assert SESSIONS[sid].brief.is_complete()

        run = client.post("/api/generate", json={"session_id": sid})
        assert run.status_code == 200
        launch.assert_called_once()
