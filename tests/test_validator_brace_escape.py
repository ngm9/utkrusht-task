"""Pins Fix 3 — the prompt-generator validator's brace-escape dry-run.

This was coordinator finding F4 + F6: the prompt_generator agent was emitting
literal JSON examples like ``{"title": "..."}`` without doubling the braces,
breaking the downstream ``str.format(**fmt_args)`` call inside ``utils.py``.

The validator now exec()s the source in a sandbox and dry-runs
``template.format()`` on every PROMPT_REGISTRY entry to catch this before
the file ever lands on disk.
"""

from __future__ import annotations

from generators.prompts.validator import _simulate_format_call


GOOD_SOURCE = '''
PROMPT_X_BASIC_CONTEXT = """{organization_background}\\n{role_context}"""
PROMPT_X_BASIC_INPUT_AND_ASK = """{competencies}\\n{real_world_task_scenarios}"""
PROMPT_X_BASIC_INSTRUCTIONS = """Output a JSON object with the answer field, then the task code files. {minutes_range}"""
PROMPT_REGISTRY = {
    "X (BASIC)": [
        PROMPT_X_BASIC_CONTEXT,
        PROMPT_X_BASIC_INPUT_AND_ASK,
        PROMPT_X_BASIC_INSTRUCTIONS,
    ]
}
'''

# The exact failure mode coordinator finding F4 caught.
BAD_SOURCE = '''
PROMPT_X_BASIC_CONTEXT = """{organization_background}"""
PROMPT_X_BASIC_INPUT_AND_ASK = """{competencies}\\n{real_world_task_scenarios}"""
PROMPT_X_BASIC_INSTRUCTIONS = """
Output format JSON:
{
  "title": "short title",
  "answer": "..."
}
"""
PROMPT_REGISTRY = {
    "X (BASIC)": [
        PROMPT_X_BASIC_CONTEXT,
        PROMPT_X_BASIC_INPUT_AND_ASK,
        PROMPT_X_BASIC_INSTRUCTIONS,
    ]
}
'''

PROPERLY_ESCAPED_SOURCE = '''
PROMPT_X_BASIC_CONTEXT = """{organization_background}"""
PROMPT_X_BASIC_INPUT_AND_ASK = """{competencies}\\n{real_world_task_scenarios}"""
PROMPT_X_BASIC_INSTRUCTIONS = """
Output format JSON:
{{
  "title": "short title",
  "answer": "..."
}}
"""
PROMPT_REGISTRY = {
    "X (BASIC)": [
        PROMPT_X_BASIC_CONTEXT,
        PROMPT_X_BASIC_INPUT_AND_ASK,
        PROMPT_X_BASIC_INSTRUCTIONS,
    ]
}
'''


def test_good_source_has_no_issues() -> None:
    issues = _simulate_format_call(GOOD_SOURCE)
    assert issues == []


def test_unescaped_json_example_is_caught() -> None:
    issues = _simulate_format_call(BAD_SOURCE)
    assert issues, "Validator must catch unescaped JSON example"
    msg = issues[0]
    assert "str.format() raises KeyError" in msg
    # Diagnostic should mention escaping
    assert "{{" in msg or "Double the braces" in msg


def test_double_brace_escaping_resolves_the_issue() -> None:
    issues = _simulate_format_call(PROPERLY_ESCAPED_SOURCE)
    assert issues == [], (
        f"Properly-escaped braces should pass validation; got: {issues}"
    )
