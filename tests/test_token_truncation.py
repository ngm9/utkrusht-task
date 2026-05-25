"""F11 — token-truncation detection in generate_task_with_code."""
from unittest.mock import MagicMock, patch

import pytest

from infra.evals import LLMOutputTruncated


def test_llm_output_truncated_carries_partial_and_attempt():
    exc = LLMOutputTruncated("partial json {", attempt=2)
    assert exc.partial_text == "partial json {"
    assert exc.attempt == 2
    assert "truncated" in str(exc).lower()


def _mock_chat_response(content: str, finish_reason: str) -> MagicMock:
    """Mock an openai chat.completions.create response object."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    choice.finish_reason = finish_reason
    usage = MagicMock()
    usage.prompt_tokens = 100
    usage.completion_tokens = 200
    resp = MagicMock()
    resp.choices = [choice]
    resp.usage = usage
    return resp


def test_generate_task_raises_on_length_finish_reason():
    """A finish_reason of 'length' means max_tokens was hit mid-output —
    generate_task_with_code must raise LLMOutputTruncated, not a generic
    parse error."""
    from infra import utils

    client = MagicMock()
    client.chat.completions.create.return_value = _mock_chat_response(
        '{"name": "partial task with no closing brace',
        finish_reason="length",
    )
    input_data = {
        "competencies": [{"name": "Python", "proficiency": "BASIC"}],
        "background": {},
        "scenarios": [],
    }
    with patch("infra.utils.get_task_prompt_by_technology_stack",
               return_value=["dummy generation prompt"]):
        with pytest.raises(LLMOutputTruncated) as excinfo:
            utils.generate_task_with_code(client, input_data)

    assert excinfo.value.attempt == 1
    assert "no closing brace" in excinfo.value.partial_text
