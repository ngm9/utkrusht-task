"""Unit tests for the instruction-suggestion parser (no network)."""
from task_builder.suggestions import _parse_suggestions


def test_parses_plain_json_array():
    out = _parse_suggestions('["use Redis", "add a Dockerfile", "cover retries"]')
    assert out == ["use Redis", "add a Dockerfile", "cover retries"]


def test_strips_json_code_fence():
    text = '```json\n["make it infra", "include docker-compose"]\n```'
    assert _parse_suggestions(text) == ["make it infra", "include docker-compose"]


def test_falls_back_to_bulleted_lines():
    text = "- Require a Redis dependency\n- Add a run.sh deployment script"
    out = _parse_suggestions(text)
    assert out == ["Require a Redis dependency", "Add a run.sh deployment script"]


def test_caps_at_six():
    arr = [f"directive number {i}" for i in range(10)]
    out = _parse_suggestions(str(arr).replace("'", '"'))
    assert len(out) == 6


def test_empty_input_returns_empty():
    assert _parse_suggestions("") == []
    assert _parse_suggestions("   ") == []
