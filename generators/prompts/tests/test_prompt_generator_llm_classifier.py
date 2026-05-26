"""LLM classifier — one call, strict JSON schema, retry on invalid JSON."""
import json
from unittest.mock import MagicMock

import pytest

from infra.classifier.llm_classifier import (
    classify_with_llm,
    ClassifierResult,
    _SYSTEM_PROMPT,
)
from infra.classifier.runtime import Competency, TaskRuntime


def _make_client(response_text: str) -> MagicMock:
    """Build a mock OpenAI client that returns `response_text` once."""
    msg = MagicMock()
    msg.content = response_text
    choice = MagicMock(); choice.message = msg
    resp = MagicMock(); resp.choices = [choice]
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    return client


def test_classifier_parses_valid_llm_output():
    client = _make_client(json.dumps({
        "runtime": "python",
        "frameworks": ["fastapi"],
        "datastores": ["postgres"],
        "messaging": [],
        "needs_browser": False,
        "kind": "app",
        "confidence": 0.93,
    }))
    comps = [Competency(name="Python", proficiency="INTERMEDIATE"),
             Competency(name="FastAPI", proficiency="INTERMEDIATE"),
             Competency(name="Postgres", proficiency="INTERMEDIATE")]
    result = classify_with_llm(comps, client=client)
    assert isinstance(result, ClassifierResult)
    assert result.runtime.runtime == "python"
    assert result.runtime.frameworks == ["fastapi"]
    assert result.runtime.datastores == ["postgres"]
    assert result.runtime.kind == "app"
    assert result.confidence == pytest.approx(0.93)
    assert client.chat.completions.create.call_count == 1


def test_classifier_tolerates_prose_around_json():
    client = _make_client(
        'Here is the classification: {"runtime":"flutter","frameworks":[],'
        '"datastores":[],"messaging":[],"needs_browser":false,'
        '"kind":"mobile","confidence":0.9} end of message.'
    )
    comps = [Competency(name="Flutter", proficiency="INTERMEDIATE")]
    result = classify_with_llm(comps, client=client)
    assert result.runtime.runtime == "flutter"
    assert result.runtime.kind == "mobile"


def test_classifier_retries_once_on_invalid_json():
    msg_bad = MagicMock(); msg_bad.content = "totally not json"
    choice_bad = MagicMock(); choice_bad.message = msg_bad
    resp_bad = MagicMock(); resp_bad.choices = [choice_bad]

    msg_ok = MagicMock(); msg_ok.content = json.dumps({
        "runtime": "go", "frameworks": [], "datastores": ["redis"],
        "messaging": [], "needs_browser": False, "kind": "app",
        "confidence": 0.88,
    })
    choice_ok = MagicMock(); choice_ok.message = msg_ok
    resp_ok = MagicMock(); resp_ok.choices = [choice_ok]

    client = MagicMock()
    client.chat.completions.create.side_effect = [resp_bad, resp_ok]
    comps = [Competency(name="Golang", proficiency="INTERMEDIATE"),
             Competency(name="Redis", proficiency="INTERMEDIATE")]
    result = classify_with_llm(comps, client=client)
    assert result.runtime.runtime == "go"
    assert client.chat.completions.create.call_count == 2


def test_classifier_raises_after_two_bad_responses():
    msg = MagicMock(); msg.content = "still not json"
    choice = MagicMock(); choice.message = msg
    resp = MagicMock(); resp.choices = [choice]
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    comps = [Competency(name="Python", proficiency="BASIC")]
    with pytest.raises(ValueError, match="invalid JSON"):
        classify_with_llm(comps, client=client)
    assert client.chat.completions.create.call_count == 2


def test_classifier_empty_competencies_raises():
    with pytest.raises(ValueError):
        classify_with_llm([], client=MagicMock())


def test_retry_message_carries_specific_validation_error():
    """The retry user message must echo the first attempt's validation error
    (e.g. an invalid `kind`), not a generic nudge — otherwise the model often
    repeats the same mistake."""
    bad_payload = json.dumps({
        "runtime": "python", "frameworks": ["fastapi"], "datastores": [],
        "messaging": [], "needs_browser": False,
        "kind": "application",  # not in the Literal set
        "confidence": 0.9,
    })
    good_payload = json.dumps({
        "runtime": "python", "frameworks": ["fastapi"], "datastores": [],
        "messaging": [], "needs_browser": False,
        "kind": "app", "confidence": 0.9,
    })

    msg_bad = MagicMock(); msg_bad.content = bad_payload
    choice_bad = MagicMock(); choice_bad.message = msg_bad
    resp_bad = MagicMock(); resp_bad.choices = [choice_bad]

    msg_ok = MagicMock(); msg_ok.content = good_payload
    choice_ok = MagicMock(); choice_ok.message = msg_ok
    resp_ok = MagicMock(); resp_ok.choices = [choice_ok]

    client = MagicMock()
    client.chat.completions.create.side_effect = [resp_bad, resp_ok]
    comps = [Competency(name="Python", proficiency="INTERMEDIATE")]

    result = classify_with_llm(comps, client=client)
    assert result.runtime.kind == "app"
    assert client.chat.completions.create.call_count == 2

    retry_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
    retry_user_msg = retry_messages[-1]["content"]
    assert "kind" in retry_user_msg, (
        "retry message should name the offending field ('kind')"
    )
    assert "Specific errors" in retry_user_msg


def test_system_prompt_lists_required_fields():
    """Sanity: the prompt mentions every TaskRuntime field by name."""
    for field in ("runtime", "frameworks", "datastores", "messaging",
                  "needs_browser", "kind", "confidence"):
        assert field in _SYSTEM_PROMPT
