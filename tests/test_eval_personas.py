"""Persona-routed eval critics — coverage + prompt-prepending behaviour."""
import typing
from unittest.mock import MagicMock, patch

from infra import evals
from infra.evals import PERSONA_PROMPTS, _persona_prefix, llm_code_eval, llm_task_eval
from infra.classifier.runtime import Kind


def test_persona_prompts_cover_every_kind():
    """Every TaskRuntime.kind value must have a persona — no silent gaps."""
    kinds = set(typing.get_args(Kind))
    assert set(PERSONA_PROMPTS) == kinds, (
        f"persona/kind mismatch — missing: {kinds - set(PERSONA_PROMPTS)}, "
        f"extra: {set(PERSONA_PROMPTS) - kinds}"
    )


def test_persona_prefix_empty_for_none():
    assert _persona_prefix(None) == ""


def test_persona_prefix_empty_for_unknown_kind():
    assert _persona_prefix("not-a-real-kind") == ""


def test_persona_prefix_populated_for_known_kind():
    prefix = _persona_prefix("db_only")
    assert "senior database administrator" in prefix
    assert prefix.endswith("\n\n")  # cleanly separated from the generic body


def _mock_eval_response(payload: str) -> MagicMock:
    """Build a mock Responses-API response carrying `payload` as output_text."""
    resp = MagicMock()
    resp.output_text = payload
    return resp


_OK_PAYLOAD = '{"pass": true, "issues": [], "validated_criteria": []}'


def test_llm_task_eval_prepends_persona_when_kind_supplied():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval({"name": "x"}, "BASIC", "2", 20, MagicMock(), "ignored",
                      kind="db_only")

    prompt_sent = captured["input"][0]["content"]
    assert "senior database administrator" in prompt_sent
    # The generic checklist is still present after the persona block.
    assert "expert technical assessment reviewer" in prompt_sent


def test_llm_task_eval_no_persona_when_kind_none():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval({"name": "x"}, "BASIC", "2", 20, MagicMock(), "ignored")

    prompt_sent = captured["input"][0]["content"]
    assert prompt_sent.lstrip().startswith("You are an expert technical assessment reviewer")
    for persona in PERSONA_PROMPTS.values():
        assert persona.strip() not in prompt_sent


def test_llm_code_eval_prepends_persona_when_kind_supplied():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_code_eval({"a.py": "x"}, "task desc", MagicMock(), "ignored",
                      kind="frontend")

    prompt_sent = captured["input"][0]["content"]
    assert "senior UX engineer" in prompt_sent
    assert "expert technical assessment reviewer" in prompt_sent
