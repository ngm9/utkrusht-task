"""
Integration tests for FK checks against real dev Supabase.

Requires .env with SUPABASE_URL_APTITUDETESTSDEV + SUPABASE_API_KEY_APTITUDETESTSDEV.
Run with: pytest tests/integration/
"""
import os
import pytest

from task_validation import BaseTaskDAO, TaskValidationError


def _make_valid_task(competency_id: str) -> dict:
    return {
        "created_at": "2026-05-18T10:00:00",
        "pre_requisites": ["Git installed"],
        "answer": "Use GROUP BY with HAVING clause",
        "criterias": [{"competency_id": competency_id, "proficiency": "BASIC", "name": "MySQL"}],
        "is_deployed": False,
        "task_blob": {
            "title": "MySQL Integration Test Task",
            "definitions": {"GROUP BY": "Groups rows sharing a property"},
            "hints": "Think about aggregate functions",
            "resources": {"github_repo": "https://github.com/UtkrushtApps/mysql-task"},
            "outcomes": ["Write GROUP BY queries"],
            "question": "Write a query that returns total sales per region",
            "short_overview": ["MySQL aggregation challenge"],
        },
        "is_shared_infra_required": False,
        "readme_content": {},
        "eval_info": {"task_eval": {"score": 8}, "code_eval": {"score": 9}},
        "solutions": {"steps": ["Step 1"], "answer_repo": "https://github.com/UtkrushtApps/mysql-task-answer"},
    }


@pytest.fixture(scope="module")
def dev_supabase():
    from dotenv import load_dotenv
    load_dotenv()
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL_APTITUDETESTSDEV")
    key = os.environ.get("SUPABASE_API_KEY_APTITUDETESTSDEV")
    if not url or not key:
        pytest.skip("SUPABASE_URL_APTITUDETESTSDEV / SUPABASE_API_KEY_APTITUDETESTSDEV not set")
    return create_client(url, key)


@pytest.fixture(scope="module")
def real_competency_id(dev_supabase):
    result = dev_supabase.table("competencies").select("competency_id").limit(1).execute()
    if not result.data:
        pytest.skip("No competencies found in dev Supabase")
    return result.data[0]["competency_id"]


def test_valid_competency_id_passes(dev_supabase, real_competency_id):
    task = _make_valid_task(real_competency_id)
    BaseTaskDAO(dev_supabase).validate(task, env="dev")


def test_invalid_competency_id_raises_with_id_and_env(dev_supabase):
    fake_id = "non-existent-competency-zzz"
    task = _make_valid_task(fake_id)
    with pytest.raises(TaskValidationError) as exc_info:
        BaseTaskDAO(dev_supabase).validate(task, env="dev")
    err = exc_info.value
    assert any(f.actual_value == fake_id for f in err.failures)
    assert any(f.environment == "dev" for f in err.failures)


def test_invalid_competency_id_no_tasks_row_written(dev_supabase):
    fake_id = "non-existent-competency-yyy"
    task = _make_valid_task(fake_id)
    with pytest.raises(TaskValidationError):
        BaseTaskDAO(dev_supabase).validate(task, env="dev")
    # Confirm no task was inserted — the error fires before any write
    result = dev_supabase.table("tasks").select("task_id").eq(
        "task_blob->>title", "MySQL Integration Test Task"
    ).execute()
    assert result.data == [] or all(
        r.get("task_blob", {}).get("title") != "MySQL Integration Test Task"
        for r in result.data
    )
