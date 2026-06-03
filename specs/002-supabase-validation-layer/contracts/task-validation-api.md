# Contract: task_validation.py Public API

**Module**: `task_validation` (root-level, imported by `multiagent.py`)  
**Date**: 2026-05-18

This document defines the public interface of `task_validation.py`. All symbols below are the stable contract; internal helpers are private (prefixed `_`).

---

## Exceptions

### `TaskValidationError(Exception)`

Raised by `validate_task_for_db()` when schema or FK validation fails. Nothing has been written to Supabase when this is raised.

```python
class TaskValidationError(Exception):
    failures: list[ValidationFailure]   # all failures, never empty
    task_name: str                       # for operator context in error message
```

### `TaskWriteError(Exception)`

Raised by `insert_task_with_competencies()` when a `task_competencies` insert fails after the task row was already inserted.

```python
class TaskWriteError(Exception):
    task_id: str                         # UUID of the orphaned task row
    all_failures: list[str]              # all competency_ids that failed to link
    environment: str                     # "dev" or "prod"
```

---

## Functions

### `validate_task_for_db(task_data: dict, supabase_client: Client, env: str = "dev") -> None`

Validates `task_data` against the `TaskForDB` Pydantic schema and runs a pre-flight FK check for all `competency_id` values against the target environment.

**Raises**: `TaskValidationError` if any check fails — collects ALL failures before raising.  
**Returns**: `None` on success.  
**Side effects**: One `SELECT` query against `competencies` table in `env`. No writes.

```
validate_task_for_db(task_data_for_db, supabase_client, env="dev")
  ├── schema validation (Pydantic, no network)
  ├── duplicate competency_id check (no network)
  └── FK check: SELECT id FROM competencies WHERE id IN (...)
```

---

### `insert_task_with_competencies(task_data: dict, supabase_client: Client) -> str`

Inserts a validated task into `tasks` and creates all `task_competencies` rows. Must only be called after `validate_task_for_db()` returns without raising.

**Raises**: `TaskWriteError` if any `task_competencies` insert fails (task row is already written).  
**Raises**: `Exception` for infra errors on the `tasks` insert itself (nothing written).  
**Returns**: `task_id` (UUID string) on full success.

---

### `validate_and_insert_task(task_data: dict, supabase_client: Client, env: str = "dev") -> str`

Convenience wrapper: runs `validate_task_for_db()` then `insert_task_with_competencies()` in sequence.

**Raises**: `TaskValidationError` | `TaskWriteError` | `Exception`  
**Returns**: `task_id` string on full success.

This is the primary call-site replacement for the existing inline `supabase.table("tasks").insert(...)` block in `multiagent.py`.

---

## Usage Pattern (in `multiagent.py`)

**Before** (current code, lines 483–502):
```python
supabase = init_supabase()
result = supabase.table("tasks").insert(task_data_for_db).execute()
# ... extract task_id ...
for criteria in task_data["criterias"]:
    competency_id = criteria.get("competency_id")
    if competency_id:
        try:
            supabase.table("task_competencies").insert({...}).execute()
        except Exception as e:
            logger.error(f"Failed to insert task-competency relationship: {str(e)}")
```

**After**:
```python
from task_validation import validate_and_insert_task, TaskValidationError, TaskWriteError

supabase = init_supabase(env)
try:
    task_id = validate_and_insert_task(task_data_for_db, supabase, env=env)
except TaskValidationError as e:
    logger.error(str(e))
    raise
except TaskWriteError as e:
    logger.error(str(e))
    raise
```

---

## Validation Checklist (run by `validate_task_for_db`)

| Check | Type | Field |
|-------|------|-------|
| All required top-level fields present | schema | `created_at`, `answer`, `criterias`, `task_blob`, `is_deployed`, `is_shared_infra_required`, `readme_content`, `eval_info`, `solutions` |
| `criterias` non-empty list | schema | `criterias` |
| Each criteria has non-empty `competency_id` | schema | `criterias[*].competency_id` |
| Each criteria has valid `proficiency` | schema | `criterias[*].proficiency` |
| No duplicate `competency_id` in `criterias` | cross-field | `criterias` |
| `is_deployed` is `False` | schema | `is_deployed` |
| `task_blob.definitions` non-empty dict with all non-empty values | schema | `task_blob.definitions` |
| `task_blob.question` non-empty | schema | `task_blob.question` |
| `task_blob.title` non-empty | schema | `task_blob.title` |
| `task_blob.resources.github_repo` present and non-empty | schema | `task_blob.resources` |
| `eval_info` contains `task_eval` and `code_eval` keys | schema | `eval_info` |
| `solutions` contains `steps` and `files` keys | schema | `solutions` |
| All `competency_id` values exist in target env | FK (network) | `criterias[*].competency_id` |
