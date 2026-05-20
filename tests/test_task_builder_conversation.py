"""Conversation engine — structured-output slot-filling (Approach B)."""
import json
from unittest.mock import MagicMock

from task_builder.conversation import run_turn, _extract_json, ConversationTurn, apply_turn, ChatResult
from task_builder.slots import SessionState


def _client_returning(content: str) -> MagicMock:
    """Fake Portkey/OpenAI client whose chat completion returns `content`."""
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def test_extract_json_pulls_object_from_surrounding_text():
    text = 'Sure! {"reply": "hi", "slots_update": {}, "ready_to_generate": false} done'
    assert _extract_json(text) == {"reply": "hi", "slots_update": {},
                                   "ready_to_generate": False}


def test_run_turn_parses_a_clean_json_response():
    payload = json.dumps({
        "reply": "What stack?",
        "slots_update": {"proficiency": "BASIC"},
        "ready_to_generate": False,
    })
    client = _client_returning(payload)
    turn = run_turn(client, history=[], user_message="hello")
    assert isinstance(turn, ConversationTurn)
    assert turn.reply == "What stack?"
    assert turn.slots_update == {"proficiency": "BASIC"}
    assert turn.ready_to_generate is False


def test_run_turn_retries_once_on_invalid_json_then_succeeds():
    good = json.dumps({"reply": "ok", "slots_update": {}, "ready_to_generate": False})
    client = MagicMock()
    bad_choice = MagicMock()
    bad_choice.message.content = "not json at all"
    good_choice = MagicMock()
    good_choice.message.content = good
    client.chat.completions.create.side_effect = [
        MagicMock(choices=[bad_choice]),
        MagicMock(choices=[good_choice]),
    ]
    turn = run_turn(client, history=[], user_message="hello")
    assert turn.reply == "ok"
    assert client.chat.completions.create.call_count == 2


def test_run_turn_gives_graceful_fallback_when_retry_also_fails():
    client = _client_returning("still not json")
    turn = run_turn(client, history=[], user_message="hello")
    assert turn.slots_update == {}
    assert turn.ready_to_generate is False
    assert turn.reply  # non-empty graceful message


def _client_seq(*payloads):
    """Fake client returning each payload in order across calls."""
    client = MagicMock()
    choices = []
    for p in payloads:
        c = MagicMock()
        c.message.content = p
        choices.append(MagicMock(choices=[c]))
    client.chat.completions.create.side_effect = choices
    return client


def _supabase_ok():
    client = MagicMock()
    table = client.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = \
        MagicMock(data=[{"name": "Java"}])
    return client


def test_apply_turn_merges_valid_slots_into_session_brief():
    session = SessionState(session_id="s1")
    payload = json.dumps({
        "reply": "Got it.",
        "slots_update": {"proficiency": "basic", "role": "Backend Engineer"},
        "ready_to_generate": False,
    })
    result = apply_turn(session, "I need a basic backend task",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert isinstance(result, ChatResult)
    assert session.brief.proficiency == "BASIC"   # normalised
    assert session.brief.role == "Backend Engineer"
    assert "proficiency" not in result.missing_slots


def test_apply_turn_rejects_invalid_proficiency_and_does_not_store_it():
    session = SessionState(session_id="s1")
    bad = json.dumps({"reply": "ok", "slots_update": {"proficiency": "wizard"},
                       "ready_to_generate": False})
    corrected = json.dumps({"reply": "Which level?", "slots_update": {},
                             "ready_to_generate": False})
    result = apply_turn(session, "make it wizard level",
                        client=_client_seq(bad, corrected), supabase=_supabase_ok())
    assert session.brief.proficiency is None
    assert "proficiency" in result.missing_slots


def test_apply_turn_ready_only_when_server_agrees_brief_is_complete():
    session = SessionState(session_id="s1")
    session.brief = session.brief.model_copy(update={
        "competencies": ["Java"], "proficiency": "BASIC", "role": "Eng",
        "focus_areas": ["idempotency"], "domain": "fintech",
    })
    payload = json.dumps({"reply": "Ready!", "slots_update": {},
                           "ready_to_generate": True})
    result = apply_turn(session, "looks good",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert result.ready is True


def test_apply_turn_not_ready_when_llm_says_ready_but_brief_incomplete():
    """Server overrides a premature ready_to_generate from the LLM."""
    session = SessionState(session_id="s1")  # empty brief
    payload = json.dumps({"reply": "Ready!", "slots_update": {},
                          "ready_to_generate": True})
    result = apply_turn(session, "go",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert result.ready is False
    assert result.missing_slots  # brief still incomplete


def test_apply_turn_validates_competency_using_proficiency_from_earlier_turn():
    """Competency given after the proficiency was already set is still validated."""
    session = SessionState(session_id="s1")
    session.brief = session.brief.model_copy(update={"proficiency": "BASIC"})
    payload = json.dumps({"reply": "ok", "slots_update": {"competencies": ["Java"]},
                          "ready_to_generate": False})
    result = apply_turn(session, "use Java",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert session.brief.competencies == ["Java"]
    assert "competencies" not in result.missing_slots
