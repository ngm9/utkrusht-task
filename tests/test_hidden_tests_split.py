"""Phase 2: grading tests are withheld from the candidate, kept for the grader.

The leak this closes, observed in the shipped task
`redact-pii-in-playback-support-agent`: the stub said only "return a copy of
the record safe to persist to the log", but `invariants/test_log_redaction.py`
shipped alongside it with

    PII_VALUES = ["Priya Raman", "priya.raman@example.com", ..., "4242"]
    DEBUG_KEYS = ["trace_id", "tool_name", "latency_ms", ...]

i.e. the exact answer. Every stub-level withholding rule is cancelled by a test
file that writes the answer down next to it.

`hidden_tests` is stripped from the task before the template repo / DB row /
gist are built, and merged into the answer repo's files instead. These tests
pin that split, and above all that a hidden test can never reach the candidate.
"""
import pytest

# Mirrors the logic in creator.create_task. Kept as a pure function here so the
# invariant is testable without standing up the whole generation pipeline.
def split_hidden_tests(task_data, solutions_data, log=None):
    """Strip `hidden_tests` off task_data; merge into solutions_data['files']."""
    hidden = task_data.pop("hidden_tests", None) or {}
    if hidden:
        collided = [p for p in hidden if p in task_data.get("code_files", {})]
        for p in collided:
            hidden.pop(p, None)
        if collided and log is not None:
            log.append(("collision", collided))
    if hidden:
        solutions_data.setdefault("files", {})
        solutions_data["files"].update(hidden)
    return task_data, solutions_data, hidden


HIDDEN = {"grading/test_fields_survive.py": "assert row['plan_tier'] == 'premium'"}
VISIBLE = {"invariants/test_symptom.py": "assert no fixture value in log"}


def _task(**over):
    d = {"name": "t", "code_files": dict(VISIBLE), "hidden_tests": dict(HIDDEN)}
    d.update(over)
    return d


def test_hidden_tests_removed_from_task():
    task, _, _ = split_hidden_tests(_task(), {"files": {}})
    assert "hidden_tests" not in task, "hidden_tests must not survive onto the task row"


def test_hidden_tests_never_in_candidate_code_files():
    """The load-bearing property: the candidate must never receive them."""
    task, _, _ = split_hidden_tests(_task(), {"files": {}})
    assert "grading/test_fields_survive.py" not in task["code_files"]
    assert set(task["code_files"]) == set(VISIBLE)


def test_hidden_tests_land_in_answer_repo():
    _, sol, _ = split_hidden_tests(_task(), {"files": {"solution.py": "..."}})
    assert "grading/test_fields_survive.py" in sol["files"]
    assert "solution.py" in sol["files"], "must not clobber existing answer files"


def test_candidate_still_gets_a_runnable_suite():
    """Splitting must not leave the candidate with nothing to self-check."""
    task, _, _ = split_hidden_tests(_task(), {"files": {}})
    assert any(p.startswith("invariants/") for p in task["code_files"])


def test_colliding_path_is_dropped_not_shipped():
    """A hidden path that also exists candidate-side would leak by collision."""
    log = []
    collide = {"invariants/test_symptom.py": "assert plan_tier == 'premium'"}
    task, sol, hidden = split_hidden_tests(
        _task(hidden_tests=dict(collide)), {"files": {}}, log=log
    )
    assert hidden == {}, "colliding hidden test must be dropped"
    assert task["code_files"]["invariants/test_symptom.py"] == VISIBLE["invariants/test_symptom.py"], \
        "candidate-facing file must not be overwritten by a hidden one"
    assert sol.get("files", {}) == {}
    assert log and log[0][0] == "collision"


def test_absent_hidden_tests_is_a_no_op():
    """Tasks below ADVANCED ship one visible suite — nothing should change."""
    task = {"name": "t", "code_files": dict(VISIBLE)}
    task, sol, hidden = split_hidden_tests(task, {"files": {"a.py": "x"}})
    assert hidden == {}
    assert task["code_files"] == VISIBLE
    assert sol["files"] == {"a.py": "x"}


@pytest.mark.parametrize("empty", [None, {}])
def test_empty_hidden_tests_does_not_create_files_key(empty):
    _, sol, _ = split_hidden_tests(_task(hidden_tests=empty), {})
    assert "files" not in sol, "must not fabricate an empty answer-files payload"


def test_advanced_reference_documents_the_split():
    import pathlib
    ref = (pathlib.Path(__file__).parents[1] / "task_generation_prompts" /
           "_general_reference" / "agent_general_advanced_prompt.py").read_text(encoding="utf-8")
    assert "SPLITTING THE TESTS" in ref
    assert '"hidden_tests"' in ref
    assert "grading/" in ref


def test_intermediate_reference_does_not_split():
    """Split is ADVANCED-only — INTERMEDIATE must keep one visible suite."""
    import pathlib
    ref = (pathlib.Path(__file__).parents[1] / "task_generation_prompts" /
           "_general_reference" / "agent_general_intermediate_prompt.py").read_text(encoding="utf-8")
    assert "hidden_tests" not in ref
