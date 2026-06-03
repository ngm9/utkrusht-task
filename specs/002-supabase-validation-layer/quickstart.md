# Quickstart: Supabase Write Validation Layer

**For**: developers implementing or testing this feature

---

## What changes

One new file is added and one existing function is replaced:

| Change | Details |
|--------|---------|
| **Add** `task_validation.py` | New root-level module with Pydantic models + DAO functions |
| **Delete** `validate_task()` from `multiagent.py:206` | Replaced entirely by the new module |
| **Replace** inline insert block in `multiagent.py:483–502` | Replaced by `validate_and_insert_task()` call |
| **Add** `tests/` directory | Unit + integration tests |
| **Add** `pytest` to `requirements.txt` | Test runner |

---

## Running the tests

```bash
# Unit tests (no Supabase connection required)
pytest tests/unit/

# Integration tests (requires .env with SUPABASE_URL_APTITUDETESTSDEV + SUPABASE_API_KEY_APTITUDETESTSDEV)
pytest tests/integration/

# All tests
pytest tests/
```

---

## Triggering validation manually (for debugging)

```python
from task_validation import validate_task_for_db, TaskValidationError
from multiagent import init_supabase

supabase = init_supabase("dev")

# Build a task_data_for_db dict (same structure multiagent.py assembles)
task_data = {
    "created_at": "2026-05-18T10:00:00",
    "pre_requisites": "",
    "answer": "Use GROUP BY with HAVING...",
    "criterias": [{"competency_id": "some-uuid", "proficiency": "BASIC", "name": "MySQL"}],
    "is_deployed": False,
    "task_blob": {
        "title": "MySQL Aggregation Task",
        "definitions": {"GROUP BY": "Groups rows sharing a property"},
        "hints": "Think about aggregate functions",
        "resources": {"github_repo": "https://github.com/UtkrushtApps/mysql-task"},
        "outcomes": ["Write GROUP BY queries", "Use HAVING clause"],
        "question": "Write a query that...",
        "short_overview": "MySQL aggregation challenge",
    },
    "is_shared_infra_required": False,
    "readme_content": {},
    "eval_info": {"task_eval": {...}, "code_eval": {...}},
    "solutions": {"steps": ["Step 1..."], "files": []},
}

try:
    validate_task_for_db(task_data, supabase, env="dev")
    print("Validation passed")
except TaskValidationError as e:
    print(e)  # prints all failures
```

---

## Adding a new required field constraint

1. Open `task_validation.py`
2. Find the relevant Pydantic model (`TaskForDB`, `TaskBlob`, or `CriteriaEntry`)
3. Add the field with its type annotation and validator
4. Add a test case in `tests/unit/test_task_validation.py`

No other files need to change (FR-009 / SC-004).

---

## Environment behaviour

Validation always runs against the environment passed to `init_supabase(env)`. The `--env dev|prod` flag in the `generate-tasks` Click command flows through to `validate_and_insert_task(..., env=env)`. No hardcoded environment names exist in `task_validation.py`.
