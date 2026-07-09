"""LLM classifier — picks template_id + persona from active templates with
strict JSON output and one retry on bad output.
"""
import json
from unittest.mock import MagicMock

import pytest

from infra.classifier.llm_classifier import (
    ActiveTemplate,
    _SYSTEM_PROMPT,
    classify_match,
)
from infra.classifier.runtime import Competency, TaskTemplateMatch


def _python_template() -> ActiveTemplate:
    return ActiveTemplate(
        template_id="utkrusht-python",
        primary_runtime="python",
        personas=["backend", "data", "mle"],
        eval_methods=["test_suite"],
        capabilities={
            "frameworks": ["fastapi", "sqlalchemy"],
            "datastores": ["postgres"],
        },
    )


def _make_client(response_text: str) -> MagicMock:
    """Build a mock OpenAI client that returns `response_text` once."""
    msg = MagicMock()
    msg.content = response_text
    choice = MagicMock(); choice.message = msg
    resp = MagicMock(); resp.choices = [choice]
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    return client


def test_classifier_parses_valid_match():
    client = _make_client(json.dumps({
        "template_id": "utkrusht-python",
        "persona": "backend",
        "confidence": 0.93,
        "no_match_reason": None,
        "missing_capabilities": [],
        "suggested_template": None,
    }))
    comps = [Competency(name="Python", proficiency="INTERMEDIATE"),
             Competency(name="FastAPI", proficiency="INTERMEDIATE"),
             Competency(name="Postgres", proficiency="INTERMEDIATE")]
    match = classify_match(comps, [_python_template()], client=client)
    assert isinstance(match, TaskTemplateMatch)
    assert match.template_id == "utkrusht-python"
    assert match.persona == "backend"
    assert match.confidence == pytest.approx(0.93)
    assert client.chat.completions.create.call_count == 1


def test_classifier_tolerates_prose_around_json():
    client = _make_client(
        'Here is the match: {"template_id":"utkrusht-python","persona":"data",'
        '"confidence":0.9,"no_match_reason":null,"missing_capabilities":[],'
        '"suggested_template":null} end of message.'
    )
    comps = [Competency(name="Python", proficiency="INTERMEDIATE")]
    match = classify_match(comps, [_python_template()], client=client)
    assert match.template_id == "utkrusht-python"
    assert match.persona == "data"


def test_classifier_retries_once_on_invalid_json():
    msg_bad = MagicMock(); msg_bad.content = "totally not json"
    choice_bad = MagicMock(); choice_bad.message = msg_bad
    resp_bad = MagicMock(); resp_bad.choices = [choice_bad]

    msg_ok = MagicMock(); msg_ok.content = json.dumps({
        "template_id": "utkrusht-python", "persona": "mle",
        "confidence": 0.88, "no_match_reason": None,
        "missing_capabilities": [], "suggested_template": None,
    })
    choice_ok = MagicMock(); choice_ok.message = msg_ok
    resp_ok = MagicMock(); resp_ok.choices = [choice_ok]

    client = MagicMock()
    client.chat.completions.create.side_effect = [resp_bad, resp_ok]
    comps = [Competency(name="Python", proficiency="INTERMEDIATE")]
    match = classify_match(comps, [_python_template()], client=client)
    assert match.template_id == "utkrusht-python"
    assert match.persona == "mle"
    assert client.chat.completions.create.call_count == 2


def test_classifier_raises_after_two_bad_responses():
    msg = MagicMock(); msg.content = "still not json"
    choice = MagicMock(); choice.message = msg
    resp = MagicMock(); resp.choices = [choice]
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    comps = [Competency(name="Python", proficiency="BASIC")]
    with pytest.raises(ValueError, match="invalid match after retry"):
        classify_match(comps, [_python_template()], client=client)
    assert client.chat.completions.create.call_count == 2


def test_classifier_empty_competencies_raises():
    with pytest.raises(ValueError):
        classify_match([], [_python_template()], client=MagicMock())


def test_classifier_rejects_unknown_template_id():
    """If the model invents a template_id, the validator rejects + retries."""
    bad = json.dumps({
        "template_id": "utkrusht-quantum",  # not in active set
        "persona": "backend", "confidence": 0.9,
        "no_match_reason": None, "missing_capabilities": [],
        "suggested_template": None,
    })
    good = json.dumps({
        "template_id": "utkrusht-python", "persona": "backend",
        "confidence": 0.9, "no_match_reason": None,
        "missing_capabilities": [], "suggested_template": None,
    })

    msg_bad = MagicMock(); msg_bad.content = bad
    choice_bad = MagicMock(); choice_bad.message = msg_bad
    resp_bad = MagicMock(); resp_bad.choices = [choice_bad]

    msg_ok = MagicMock(); msg_ok.content = good
    choice_ok = MagicMock(); choice_ok.message = msg_ok
    resp_ok = MagicMock(); resp_ok.choices = [choice_ok]

    client = MagicMock()
    client.chat.completions.create.side_effect = [resp_bad, resp_ok]
    comps = [Competency(name="Python", proficiency="INTERMEDIATE")]

    match = classify_match(comps, [_python_template()], client=client)
    assert match.template_id == "utkrusht-python"
    assert client.chat.completions.create.call_count == 2

    retry_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
    retry_user_msg = retry_messages[-1]["content"]
    assert "utkrusht-quantum" in retry_user_msg, (
        "retry message should echo the rejected template_id"
    )


def test_classifier_accepts_no_match():
    """The classifier may return no_match when no template covers the combo."""
    client = _make_client(json.dumps({
        "template_id": None, "persona": None, "confidence": 0.8,
        "no_match_reason": "needs helm + kubectl + terraform",
        "missing_capabilities": ["helm", "kubectl", "terraform"],
        "suggested_template": "utkrusht-infra",
    }))
    comps = [Competency(name="Kubernetes", proficiency="INTERMEDIATE"),
             Competency(name="Helm", proficiency="INTERMEDIATE")]
    match = classify_match(comps, [_python_template()], client=client)
    assert match.template_id is None
    assert match.no_match_reason == "needs helm + kubectl + terraform"
    assert match.missing_capabilities == ["helm", "kubectl", "terraform"]


def test_system_prompt_lists_required_output_fields():
    """Sanity: the prompt mentions every TaskTemplateMatch field by name."""
    for field in ("template_id", "persona", "confidence",
                  "no_match_reason", "missing_capabilities", "suggested_template"):
        assert field in _SYSTEM_PROMPT
