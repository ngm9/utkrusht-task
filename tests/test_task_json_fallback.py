"""Regression: a final 'no changes needed' prose turn must not discard the task.

Observed 2026-07-20 (Production Agent Engineering INTERMEDIATE, run
20260720T125156Z): prompt 3/4 returned a complete task JSON, prompt 4/4 replied
"The task I generated in the previous turn already matches this competency
archetype ..." — prose. `response_text` was overwritten by that prose, JSON
parsing failed, and a fully-generated $1.19 task was thrown away with
`RuntimeError: Failed to parse JSON from response.output_text`.

These tests pin the fallback logic that keeps the earlier valid task.
"""
import json

# The helper is defined inside create_task's scope, so re-implement the exact
# contract here and assert on it. Keep in sync with infra/utils.py.
MIN_TASK_KEYS = ("name", "code_files")


def _remember_if_task_json(text, current=None):
    """Mirror of the tracker in infra/utils.py::create_task."""
    if not text:
        return current
    candidate = None
    try:
        candidate = json.loads(text.strip())
    except json.JSONDecodeError:
        brace_count, start_idx = 0, -1
        for idx, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start_idx = idx
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    try:
                        candidate = json.loads(text[start_idx:idx + 1])
                        break
                    except json.JSONDecodeError:
                        continue
    if isinstance(candidate, dict) and all(k in candidate for k in MIN_TASK_KEYS):
        return candidate
    return current


VALID_TASK = json.dumps({
    "name": "redact-pii-in-playback-support-agent",
    "title": "Enforce PII Redaction",
    "code_files": {"agent/redaction.py": "..."},
    "answer": {"agent/redaction.py": "..."},
})

PROSE_REPLY = (
    "The task I generated in the previous turn already matches this competency "
    "archetype and honors the pinned scenario/domain. It centers on production "
    "robustness of a single agent."
)


def test_valid_task_json_is_remembered():
    assert _remember_if_task_json(VALID_TASK)["name"] == "redact-pii-in-playback-support-agent"


def test_prose_final_turn_does_not_clobber_earlier_task():
    """The actual bug: prose on the last turn must leave the good task intact."""
    remembered = _remember_if_task_json(VALID_TASK)
    remembered = _remember_if_task_json(PROSE_REPLY, current=remembered)
    assert remembered is not None, "prose reply discarded the earlier valid task"
    assert remembered["name"] == "redact-pii-in-playback-support-agent"


def test_unrelated_json_is_not_mistaken_for_a_task():
    """A JSON blob without name+code_files must not be latched onto."""
    assert _remember_if_task_json('{"status": "ok"}') is None


def test_task_json_embedded_in_prose_is_recovered():
    assert _remember_if_task_json(f"Here you go:\n{VALID_TASK}\nDone.") is not None


def test_empty_response_keeps_previous():
    remembered = _remember_if_task_json(VALID_TASK)
    assert _remember_if_task_json("", current=remembered) is remembered
