# Data Model: Supabase Write Validation Layer

**Feature**: 002-supabase-validation-layer  
**Date**: 2026-05-18

---

## Entities

### 1. `CriteriaEntry`

Represents one competency reference attached to a task.

| Field | Type | Constraints |
|-------|------|-------------|
| `competency_id` | `str` | Required; non-empty; must exist in `competencies` table of target env |
| `proficiency` | `str` | Required; one of `BASIC`, `INTERMEDIATE`, `ADVANCED` (case-insensitive input, stored uppercase) |
| `name` | `str` | Required; non-empty |
| `scope` | `str \| None` | Optional |

**Validation rules**:
- `competency_id` must not be empty string or None
- `proficiency` must be in the allowed set; an unrecognised value is a hard error
- Duplicate `competency_id` values within a task's `criterias` list are rejected (cross-field rule at `TaskForDB` level)

---

### 2. `TaskBlob`

The nested JSON object stored in the `task_blob` column of the `tasks` table.

| Field | Type | Constraints |
|-------|------|-------------|
| `title` | `str` | Required; non-empty |
| `definitions` | `Dict[str, str]` | Required; non-empty dict; every value must be a non-empty string |
| `hints` | `str \| List[str]` | Required; if string, non-empty; if list, at least one element |
| `resources` | `Dict[str, str]` | Required; must contain `github_repo` key with non-empty URL |
| `outcomes` | `str \| List[str]` | Required; non-empty string or non-empty list |
| `question` | `str` | Required; non-empty |
| `short_overview` | `str \| List[str]` | Required; non-empty string or non-empty list |

**Validation rules**:
- `definitions` — empty dict `{}` is rejected; any value that is blank string `""` or whitespace is rejected
- `resources.github_repo` — must be present and non-empty (the repo URL is set before validation runs)

---

### 3. `TaskForDB`

The top-level object passed to the `tasks` table insert. Maps directly to `task_data_for_db` in `multiagent.py`.

| Field | Type | Constraints |
|-------|------|-------------|
| `created_at` | `str` | Required; non-empty ISO 8601 datetime string |
| `pre_requisites` | `str` | Required; may be empty string (optional field in content) |
| `answer` | `str` | Required; non-empty |
| `criterias` | `List[CriteriaEntry]` | Required; min 1 entry; no duplicate `competency_id` values |
| `is_deployed` | `bool` | Required; must be `False` at insert time |
| `task_blob` | `TaskBlob` | Required; validated as nested model |
| `is_shared_infra_required` | `bool` | Required |
| `readme_content` | `dict` | Required; may be empty dict if README was not generated |
| `eval_info` | `dict` | Required; non-empty (must contain at least `task_eval` and `code_eval` keys) |
| `solutions` | `dict` | Required; must contain `steps` (list) and `files` (list) keys |

**Cross-field validation rules**:
- `criterias` list must have no duplicate `competency_id` values — checked at model level via `model_validator(mode='after')`
- `is_deployed` must be `False` — an insert with `is_deployed=True` is a data integrity violation

---

### 4. `ValidationFailure`

A single validation failure entry. Collected into a list inside `TaskValidationError`.

| Field | Type | Description |
|-------|------|-------------|
| `field` | `str` | Dot-path to the failing field (e.g., `criterias[0].proficiency`, `task_blob.definitions`) |
| `actual_value` | `Any` | The actual value that failed (truncated to 200 chars for strings) |
| `constraint` | `str` | Human-readable description of the violated constraint (e.g., `"must be one of BASIC, INTERMEDIATE, ADVANCED"`) |
| `environment` | `str \| None` | Set only for FK failures; names the Supabase environment checked (`dev` or `prod`) |

---

### 5. `TaskValidationError` (Exception)

Raised when pre-insert validation fails. Nothing has been written to Supabase at this point.

| Field | Type | Description |
|-------|------|-------------|
| `failures` | `List[ValidationFailure]` | All validation failures collected in one pass |
| `task_name` | `str` | Task name/title from the input, for operator context |

**Operator message format** (printed to stderr on raise):
```
ValidationError for task '{task_name}': {N} check(s) failed
  [1] criterias[0].proficiency: got 'basic', must be one of BASIC, INTERMEDIATE, ADVANCED
  [2] task_blob.definitions: value for key 'mysql_query' is empty
  [3] criterias[1].competency_id: 'abc-123' not found in competencies table (env=dev)
```

---

### 6. `TaskWriteError` (Exception)

Raised when a `task_competencies` insert fails after the task row was already inserted.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | UUID of the task row that was inserted |
| `failed_competency_id` | `str` | The competency_id whose link insert failed |
| `all_failures` | `List[str]` | All competency_ids that failed to link (collected before raising) |
| `environment` | `str` | `dev` or `prod` |

**Operator message format**:
```
TaskWriteError: task_competencies insert failed for task_id='<uuid>' in env=dev
  Failed competency links: ['comp-id-1', 'comp-id-2']
  ACTION REQUIRED: Manually delete tasks row with task_id='<uuid>' from Supabase dev before retrying.
```

---

## State Transitions

```
task_data_for_db (dict)
        │
        ▼
  [Schema validation]  ──FAIL──▶  TaskValidationError (nothing written)
        │ PASS
        ▼
  [FK check]           ──FAIL──▶  TaskValidationError (nothing written)
        │ PASS
        ▼
  [tasks INSERT]       ──FAIL──▶  Exception (infra error, nothing to clean up)
        │ SUCCESS
        ▼
  [task_competencies   ──FAIL──▶  TaskWriteError (task row exists, operator must clean up)
   INSERT loop]
        │ ALL SUCCESS
        ▼
  task_id returned to caller
```

---

## Relationships to Existing Code

| Existing symbol | Change |
|-----------------|--------|
| `validate_task(task: Dict) -> bool` in `multiagent.py:206` | **Deleted** — replaced by `validate_task_for_db()` in `task_validation.py` |
| `task_data_for_db` dict assembly (lines 458–481) | Unchanged — dict is passed into `validate_task_for_db()` before the insert |
| `supabase.table("tasks").insert(...)` (line 484) | Moved inside `task_validation.py`'s DAO function, called only after validation passes |
| `task_competencies` insert loop (lines 493–502) | Moved inside DAO function; failures now raise `TaskWriteError` instead of logging silently |
