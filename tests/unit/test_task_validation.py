"""Unit tests for task_validation.py — no live Supabase connection required."""
import pytest
from unittest.mock import MagicMock

from task_validation import (
    BaseTaskDAO,
    CriteriaEntry,
    TaskBlob,
    TaskForDB,
    TaskValidationError,
    TaskWriteError,
    ValidationFailure,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_valid_task(**overrides) -> dict:
    base = {
        "created_at": "2026-05-18T10:00:00",
        "pre_requisites": ["Git installed"],
        "answer": "Use GROUP BY with HAVING clause",
        "criterias": [{"competency_id": "comp-uuid-1", "proficiency": "BASIC", "name": "MySQL"}],
        "is_deployed": False,
        "task_blob": {
            "title": "MySQL Aggregation Task",
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
    base.update(overrides)
    return base


def _mock_supabase(found_ids=None):
    """Return a mock Supabase client that reports the given competency IDs as found."""
    if found_ids is None:
        found_ids = ["comp-uuid-1"]
    client = MagicMock()
    client.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
        {"competency_id": cid} for cid in found_ids
    ]
    client.table.return_value.insert.return_value.execute.return_value.data = [
        {"task_id": "task-uuid-1"}
    ]
    return client


# ---------------------------------------------------------------------------
# T010: Happy path + per-field failures (US1)
# ---------------------------------------------------------------------------

class TestSchemaValidationHappyPath:
    def test_valid_task_passes(self):
        task = _make_valid_task()
        client = _mock_supabase()
        BaseTaskDAO(client).validate(task, env="dev")  # must not raise

    def test_valid_task_does_not_call_insert(self):
        task = _make_valid_task()
        client = _mock_supabase()
        BaseTaskDAO(client).validate(task, env="dev")
        client.table.return_value.insert.assert_not_called()


class TestPerFieldFailures:
    def _run(self, task):
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(_mock_supabase()).validate(task, env="dev")
        return exc_info.value

    def test_empty_definitions_rejected(self):
        task = _make_valid_task()
        task["task_blob"]["definitions"] = {}
        err = self._run(task)
        assert any("definitions" in f.field for f in err.failures)
        assert any("must not be empty" in f.constraint for f in err.failures)

    def test_empty_criterias_rejected(self):
        task = _make_valid_task()
        task["criterias"] = []
        err = self._run(task)
        assert any("criterias" in f.field for f in err.failures)

    def test_invalid_proficiency_rejected(self):
        task = _make_valid_task()
        task["criterias"] = [{"competency_id": "comp-uuid-1", "proficiency": "junior", "name": "MySQL"}]
        err = self._run(task)
        fields = [f.field for f in err.failures]
        assert any("proficiency" in fld for fld in fields)
        constraint_text = " ".join(f.constraint for f in err.failures)
        assert "BASIC" in constraint_text

    def test_null_required_field_rejected(self):
        task = _make_valid_task()
        task["answer"] = None
        err = self._run(task)
        assert any("answer" in f.field for f in err.failures)

    def test_missing_required_field_rejected(self):
        task = _make_valid_task()
        del task["answer"]
        err = self._run(task)
        assert any("answer" in f.field for f in err.failures)

    def test_blank_definition_value_rejected(self):
        task = _make_valid_task()
        task["task_blob"]["definitions"] = {"GROUP BY": "   "}
        err = self._run(task)
        assert any("definitions" in f.field for f in err.failures)

    def test_is_deployed_true_rejected(self):
        task = _make_valid_task()
        task["is_deployed"] = True
        err = self._run(task)
        assert any("is_deployed" in f.field for f in err.failures)

    def test_empty_question_rejected(self):
        task = _make_valid_task()
        task["task_blob"]["question"] = ""
        err = self._run(task)
        assert any("question" in f.field for f in err.failures)

    def test_missing_github_repo_in_resources_rejected(self):
        task = _make_valid_task()
        task["task_blob"]["resources"] = {"other_key": "value"}
        err = self._run(task)
        assert any("resources" in f.field for f in err.failures)

    def test_eval_info_missing_task_eval_key(self):
        task = _make_valid_task()
        task["eval_info"] = {"code_eval": {}}
        err = self._run(task)
        assert any("eval_info" in f.field for f in err.failures)

    def test_solutions_missing_answer_repo_key(self):
        task = _make_valid_task()
        task["solutions"] = {"steps": []}
        err = self._run(task)
        assert any("solutions" in f.field for f in err.failures)


# ---------------------------------------------------------------------------
# T011: Multi-failure and cross-field rules (US1)
# ---------------------------------------------------------------------------

class TestMultipleFailuresAndCrossField:
    def test_two_bad_fields_reported_together(self):
        task = _make_valid_task()
        task["task_blob"]["definitions"] = {}
        task["task_blob"]["question"] = ""
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(_mock_supabase()).validate(task, env="dev")
        err = exc_info.value
        assert len(err.failures) >= 2, f"Expected >=2 failures, got: {err.failures}"

    def test_duplicate_competency_id_caught(self):
        task = _make_valid_task()
        task["criterias"] = [
            {"competency_id": "comp-uuid-1", "proficiency": "BASIC", "name": "MySQL"},
            {"competency_id": "comp-uuid-1", "proficiency": "INTERMEDIATE", "name": "MySQL Advanced"},
        ]
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(_mock_supabase(["comp-uuid-1"])).validate(task, env="dev")
        err = exc_info.value
        assert len(err.failures) >= 1
        assert any("duplicate" in f.constraint.lower() for f in err.failures)

    def test_no_supabase_call_when_schema_fails(self):
        task = _make_valid_task()
        task["criterias"] = []
        client = _mock_supabase()
        with pytest.raises(TaskValidationError):
            BaseTaskDAO(client).validate(task, env="dev")
        # FK check must not run when schema fails
        client.table.return_value.select.assert_not_called()


# ---------------------------------------------------------------------------
# T013: FK check path (US2)
# ---------------------------------------------------------------------------

class TestFKCheck:
    def test_all_ids_present_passes(self):
        task = _make_valid_task()
        client = _mock_supabase(found_ids=["comp-uuid-1"])
        BaseTaskDAO(client).validate(task, env="dev")  # no exception

    def test_one_missing_id_raises_with_id_and_env(self):
        task = _make_valid_task()
        client = _mock_supabase(found_ids=[])  # returns nothing
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(client).validate(task, env="dev")
        err = exc_info.value
        failure_values = [f.actual_value for f in err.failures]
        failure_envs = [f.environment for f in err.failures]
        assert "comp-uuid-1" in failure_values
        assert "dev" in failure_envs

    def test_multiple_missing_ids_all_listed(self):
        task = _make_valid_task()
        task["criterias"] = [
            {"competency_id": "comp-a", "proficiency": "BASIC", "name": "A"},
            {"competency_id": "comp-b", "proficiency": "BASIC", "name": "B"},
        ]
        client = _mock_supabase(found_ids=[])  # both missing
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(client).validate(task, env="prod")
        err = exc_info.value
        missing_vals = {f.actual_value for f in err.failures}
        assert "comp-a" in missing_vals
        assert "comp-b" in missing_vals

    def test_supabase_network_error_raises_validation_error(self):
        task = _make_valid_task()
        client = MagicMock()
        client.table.return_value.select.return_value.in_.return_value.execute.side_effect = (
            ConnectionError("network down")
        )
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(client).validate(task, env="dev")
        err = exc_info.value
        assert any("could not reach Supabase" in f.constraint for f in err.failures)

    def test_env_prod_shown_in_error(self):
        task = _make_valid_task()
        client = _mock_supabase(found_ids=[])
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(client).validate(task, env="prod")
        err = exc_info.value
        assert any(f.environment == "prod" for f in err.failures)


# ---------------------------------------------------------------------------
# T017: TaskWriteError (US3)
# ---------------------------------------------------------------------------

class TestInsertTaskWithCompetencies:
    def _make_client_with_link_failure(self, fail_on_competency_id: str):
        client = MagicMock()

        def table_side_effect(table_name):
            table_mock = MagicMock()
            if table_name == "tasks":
                table_mock.insert.return_value.execute.return_value.data = [
                    {"task_id": "task-uuid-1"}
                ]
            elif table_name == "task_competencies":
                def link_insert(data):
                    m = MagicMock()
                    if data.get("competency_id") == fail_on_competency_id:
                        m.execute.side_effect = Exception("FK violation")
                    else:
                        m.execute.return_value.data = [{"id": "link-1"}]
                    return m
                table_mock.insert.side_effect = link_insert
            return table_mock

        client.table.side_effect = table_side_effect
        return client

    def test_successful_insert_returns_row(self):
        task = _make_valid_task()
        client = _mock_supabase()
        row = BaseTaskDAO(client).insert(task, env="dev")
        assert row["task_id"] == "task-uuid-1"

    def test_link_failure_raises_task_write_error(self):
        task = _make_valid_task()
        client = self._make_client_with_link_failure("comp-uuid-1")

        with pytest.raises(TaskWriteError) as exc_info:
            BaseTaskDAO(client).insert(task, env="dev")

        err = exc_info.value
        assert err.task_id == "task-uuid-1"
        assert "comp-uuid-1" in err.all_failures
        assert err.environment == "dev"

    def test_task_write_error_str_contains_action_required(self):
        err = TaskWriteError("task-abc", ["comp-1", "comp-2"], "prod")
        msg = str(err)
        assert "ACTION REQUIRED" in msg
        assert "task-abc" in msg
        assert "comp-1" in msg
        assert "prod" in msg

    def test_tasks_insert_failure_raises_dao_error(self):
        task = _make_valid_task()
        client = MagicMock()
        client.table.return_value.insert.return_value.execute.return_value.data = []
        with pytest.raises(Exception) as exc_info:
            BaseTaskDAO(client).insert(task, env="dev")
        assert not isinstance(exc_info.value, TaskWriteError)


# ---------------------------------------------------------------------------
# T020: Error message format (US4)
# ---------------------------------------------------------------------------

class TestErrorMessageFormat:
    def test_bad_proficiency_error_includes_field_value_and_constraint(self):
        task = _make_valid_task()
        task["criterias"] = [{"competency_id": "comp-uuid-1", "proficiency": "junior", "name": "MySQL"}]
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(_mock_supabase()).validate(task, env="dev")
        err = exc_info.value
        msg = str(err)
        assert "proficiency" in msg
        assert "junior" in msg
        assert "BASIC" in msg

    def test_fk_failure_error_includes_competency_id_and_env(self):
        task = _make_valid_task()
        client = _mock_supabase(found_ids=[])
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(client).validate(task, env="prod")
        msg = str(err := exc_info.value)
        assert "comp-uuid-1" in msg
        assert "prod" in msg

    def test_task_name_appears_in_error(self):
        task = _make_valid_task()
        task["criterias"] = []
        with pytest.raises(TaskValidationError) as exc_info:
            BaseTaskDAO(_mock_supabase()).validate(task, env="dev")
        assert "MySQL Aggregation Task" in str(exc_info.value)

    def test_validation_failure_str_format(self):
        f = ValidationFailure(
            field="criterias[0].proficiency",
            actual_value="expert",
            constraint="must be one of BASIC, INTERMEDIATE, ADVANCED",
        )
        s = str(f)
        assert "criterias[0].proficiency" in s
        assert "expert" in s
        assert "BASIC" in s

    def test_validation_failure_with_env_shows_environment(self):
        f = ValidationFailure(
            field="criterias[0].competency_id",
            actual_value="bad-id",
            constraint="must exist in competencies table",
            environment="dev",
        )
        assert "dev" in str(f)

    def test_task_validation_error_lists_all_failures_numbered(self):
        failures = [
            ValidationFailure("f1", "v1", "c1"),
            ValidationFailure("f2", "v2", "c2"),
        ]
        err = TaskValidationError(failures, task_name="My Task")
        msg = str(err)
        assert "[1]" in msg
        assert "[2]" in msg
        assert "My Task" in msg
