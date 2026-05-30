"""End-to-end: session → multi-turn chat → complete brief → generate.

A4 + B2 refactor: the server now persists conversations to a Supabase
``conversations`` table and enqueues runs onto ``generation_jobs`` instead
of spawning a thread. The integration test mocks the Supabase client + the
``enqueue_job`` call so we don't need a real DB.
"""
import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from task_builder import conversation_repo, server
from task_builder.slots import SessionState, TaskBrief


def _bot(reply, slots, ready):
    choice = MagicMock()
    choice.message.content = json.dumps({
        "reply": reply, "slots_update": slots, "ready_to_generate": ready,
    })
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def _supabase_competency_ok():
    sb = MagicMock()
    table = sb.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = \
        MagicMock(data=[{"name": "Java"}])
    return sb


def test_full_conversation_to_ready_then_generate():
    """Walk a complete brief through the chat → generate flow.

    Conversation persistence is faked by an in-memory dict so each /api/chat
    round-trips through the (mocked) Supabase layer.
    """
    fake_store: dict[str, SessionState] = {}

    def fake_create(env="dev", started_by=None):
        sid = f"conv-{len(fake_store) + 1}"
        fake_store[sid] = SessionState(session_id=sid)
        return sid

    def fake_load(env, sid):
        return fake_store.get(sid)

    def fake_save(env, session):
        fake_store[session.session_id] = session

    def fake_mark_submitted(env, sid):
        pass

    client = TestClient(server.app)
    with patch.object(server, "create_conversation", side_effect=fake_create), \
         patch.object(server, "load_session", side_effect=fake_load), \
         patch.object(server, "save_session", side_effect=fake_save), \
         patch.object(server, "mark_submitted", side_effect=fake_mark_submitted), \
         patch.object(server, "get_supabase", return_value=_supabase_competency_ok()), \
         patch.object(server, "enqueue_job", return_value="job-123") as enqueue:

        sid = client.post("/api/session").json()["session_id"]
        assert sid.startswith("conv-")

        # Turn 1: collect proficiency + competencies.
        with patch.object(server, "build_bot_client",
                          return_value=_bot("ok",
                                            {"proficiency": "BASIC", "competencies": ["Java"]},
                                            False)):
            client.post("/api/chat", json={"session_id": sid, "message": "java basic"})

        # Turn 2: fill the rest and mark ready.
        with patch.object(server, "build_bot_client",
                          return_value=_bot("Ready!",
                                            {"role": "Backend Engineer",
                                             "focus_areas": ["idempotency"],
                                             "domain": "fintech"},
                                            True)):
            final = client.post("/api/chat", json={
                "session_id": sid, "message": "backend, idempotency, fintech",
            }).json()

        assert final["ready"] is True
        assert fake_store[sid].brief.is_complete()

        run = client.post("/api/generate", json={"session_id": sid, "env": "dev"})
        assert run.status_code == 200, run.json()
        body = run.json()
        assert body["run_id"] == "job-123"
        assert body["job_id"] == "job-123"
        enqueue.assert_called_once()
        kwargs = enqueue.call_args.kwargs
        assert kwargs["conversation_id"] == sid
        assert kwargs["env"] == "dev"
        # The brief flowed through with the orchestrator helper field set.
        assert kwargs["brief"]["competencies"] == ["Java"]
        assert kwargs["brief"]["competency_names"] == ["Java"]
        assert kwargs["brief"]["proficiency"] == "BASIC"
