# Tasks: Supabase Write Validation Layer

**Input**: Design documents from `/specs/002-supabase-validation-layer/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story. Each story is independently testable by calling `task_validation.py` functions directly — no full pipeline run required until Phase 7.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1–US4)

---

## Phase 1: Setup

**Purpose**: Add test infrastructure. No source changes yet.

- [x] T001 Add `pytest` to `requirements.txt`
- [x] T002 Create `tests/unit/__init__.py` and `tests/integration/__init__.py` (empty files, establishes test package structure)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Exception classes that ALL user story implementations depend on. Must be complete before any story phase begins.

**⚠️ CRITICAL**: Phases 3–6 all import from `task_validation.py` — this file must exist before story work starts.

- [x] T003 Create `task_validation.py` at repo root with `ValidationFailure` dataclass (fields: `field: str`, `actual_value: Any`, `constraint: str`, `environment: str | None`)
- [x] T004 [P] Add `TaskValidationError(Exception)` class to `task_validation.py` — stores `failures: list[ValidationFailure]` and `task_name: str`; `__str__` prints all failures in numbered list format per data-model.md
- [x] T005 [P] Add `TaskWriteError(Exception)` class to `task_validation.py` — stores `task_id: str`, `all_failures: list[str]`, `environment: str`; `__str__` prints task_id + all failed competency_ids + "ACTION REQUIRED: Manually delete..." instruction per data-model.md

**Checkpoint**: `task_validation.py` exists and both exception types are importable. T004 and T005 can be written in the same file sequentially since they are in the same module.

---

## Phase 3: User Story 1 — Invalid Task Rejected Before Insert (Priority: P1) 🎯 MVP

**Goal**: Any task dict with missing, null, wrong-type, or empty fields is caught by Pydantic schema validation before any Supabase call, with ALL failures reported at once.

**Independent Test**: `from task_validation import validate_task_for_db, TaskValidationError` — pass a dict with empty `definitions` and missing `outcomes`; confirm `TaskValidationError` is raised listing both failures, and that no Supabase client method was called.

### Implementation for User Story 1

- [x] T006 [P] [US1] Add `CriteriaEntry` Pydantic model to `task_validation.py` — fields: `competency_id: str` (non-empty), `proficiency: str` (validated as one of BASIC/INTERMEDIATE/ADVANCED, case-insensitive input), `name: str` (non-empty), `scope: str | None`
- [x] T007 [P] [US1] Add `TaskBlob` Pydantic model to `task_validation.py` — fields per data-model.md: `title`, `definitions` (non-empty dict, all values non-empty), `hints`, `resources` (must contain non-empty `github_repo`), `outcomes`, `question` (non-empty), `short_overview`
- [x] T008 [US1] Add `TaskForDB` Pydantic model to `task_validation.py` — fields per data-model.md, with `model_validator(mode='after')` that checks for duplicate `competency_id` values in `criterias` list and that `is_deployed` is `False` (depends on T006, T007)
- [x] T009 [US1] Implement schema-only validation path in `validate_task_for_db(task_data: dict, supabase_client, env: str = "dev") -> None` in `task_validation.py`: parse `task_data` into `TaskForDB`, catch Pydantic `ValidationError`, convert all field errors to `ValidationFailure` list, raise `TaskValidationError`; FK check is a no-op stub at this stage
- [x] T010 [P] [US1] Write unit tests for happy path and per-field failures in `tests/unit/test_task_validation.py`: empty `definitions`, empty `criterias`, invalid `proficiency`, null required field, missing required field — each must raise `TaskValidationError` naming the correct field
- [x] T011 [P] [US1] Write unit tests for multi-failure and cross-field rules in `tests/unit/test_task_validation.py`: two bad fields simultaneously returns both in one error; duplicate `competency_id` in `criterias` is caught by `TaskForDB` model_validator

**Checkpoint**: `pytest tests/unit/` passes. Validation catches bad schema data without touching Supabase.

---

## Phase 4: User Story 2 — Missing Competency FK Caught Before Insert (Priority: P1)

**Goal**: Every `competency_id` in `criterias` is verified to exist in the target environment's `competencies` table before any insert. Missing IDs cause a hard abort naming the IDs and environment.

**Independent Test**: Create a mock Supabase client whose `.table("competencies").select("id").in_("id", ...).execute()` returns fewer IDs than requested. Call `validate_task_for_db(task_data, mock_client, env="dev")` — confirm `TaskValidationError` is raised with a `ValidationFailure` entry naming the missing `competency_id` and `environment="dev"`.

### Implementation for User Story 2

- [x] T012 [US2] Extend `validate_task_for_db()` in `task_validation.py`: after schema validation passes, collect all unique `competency_id` values from `criterias`, run `supabase_client.table("competencies").select("id").in_("id", ids).execute()`, compare returned IDs against requested, add a `ValidationFailure(field="criterias[N].competency_id", actual_value=missing_id, constraint="must exist in competencies table", environment=env)` for each missing ID, raise `TaskValidationError` if any FK failures exist
- [x] T013 [US2] Write unit tests for FK check path in `tests/unit/test_task_validation.py` using a mock Supabase client: all IDs present → no error; one ID missing → error names the ID and env; multiple IDs missing → all listed in single error; Supabase network error → `TaskValidationError` with "could not reach Supabase [env]" message
- [x] T014 [US2] Write integration test in `tests/integration/test_task_validation_integration.py`: use a known-invalid `competency_id` UUID against real dev Supabase; confirm `TaskValidationError` raised before any `tasks` insert; use a known-valid `competency_id` and confirm validation passes

**Checkpoint**: `pytest tests/unit/` and `pytest tests/integration/` both pass. FK pre-flight check is live.

---

## Phase 5: User Story 3 — Silent Relationship-Link Failures Become Loud Errors (Priority: P2)

**Goal**: A `task_competencies` insert failure after a successful `tasks` insert raises `TaskWriteError` naming the orphaned task_id and all failed competency_ids. Execution never silently continues.

**Independent Test**: Call `insert_task_with_competencies(task_data, mock_client)` where the mock's `task_competencies` insert raises an exception on the second call. Confirm `TaskWriteError` is raised with the correct `task_id` and both failing `competency_id` values in `all_failures`.

### Implementation for User Story 3

- [x] T015 [US3] Implement `insert_task_with_competencies(task_data: dict, supabase_client) -> str` in `task_validation.py`: insert task row into `tasks`, extract `task_id`, loop over `criterias` and insert each `task_competencies` row — collect ALL failures rather than raising on first, then raise `TaskWriteError` if any failures occurred (task_id + all failed competency_ids)
- [x] T016 [US3] Implement `validate_and_insert_task(task_data: dict, supabase_client, env: str = "dev") -> str` convenience wrapper in `task_validation.py`: calls `validate_task_for_db()` then `insert_task_with_competencies()` in sequence; re-raises either exception type unchanged
- [x] T017 [US3] Write unit tests for `TaskWriteError` in `tests/unit/test_task_validation.py`: first `task_competencies` insert fails → error names task_id; second of two inserts fails → error names task_id and both failing competency_ids; `tasks` insert itself fails → plain `Exception` (not `TaskWriteError`, nothing was written)

**Checkpoint**: `pytest tests/unit/` passes. `insert_task_with_competencies` never silently swallows a link failure.

---

## Phase 6: User Story 4 — Validation Errors Are Actionable (Priority: P2)

**Goal**: Every error message is self-contained — names the record, the field, the actual value, and the constraint — so an operator can fix the input without reading source code.

**Independent Test**: Trigger `TaskValidationError` on a task with a bad `proficiency` value. Read `str(error)` — confirm it contains: the task name, the string `criterias[0].proficiency`, the actual bad value, and the accepted values list.

### Implementation for User Story 4

- [x] T018 [US4] Verify and harden `TaskValidationError.__str__` in `task_validation.py`: output must include `task_name`, numbered list of failures, each failure line shows `field`, truncated `actual_value` (max 200 chars), and `constraint`; FK failures additionally show `environment`; add `task_name` extraction from `task_data["task_blob"]["title"]` in `validate_task_for_db()`
- [x] T019 [US4] Add validation summary log line to `validate_task_for_db()` in `task_validation.py`: on success, call `logger.info(f"Validation passed: {N} checks on task '{task_name}'")`  using the existing `logger_config` logger
- [x] T020 [US4] Write unit tests for error message content in `tests/unit/test_task_validation.py` covering all 3 acceptance scenarios: (1) bad `proficiency` error lists field + actual value + accepted values; (2) FK failure error names competency_id + environment; (3) successful validation emits summary log

**Checkpoint**: `pytest tests/unit/ -v` passes. Error messages are verifiably self-contained.

---

## Phase 7: Polish — Wire into `multiagent.py` and Documentation

**Purpose**: Connect the completed validation layer to the live pipeline. All validation logic is already tested independently; this phase is pure wiring + cleanup.

- [x] T021 Add imports `from task_validation import validate_and_insert_task, TaskValidationError, TaskWriteError` to `multiagent.py` (top-of-file imports section, after existing local imports)
- [x] T022 Delete `validate_task()` function (lines 206–247) from `multiagent.py` and remove its call site (verify with grep that no other callers exist first)
- [x] T023 Replace the inline `supabase.table("tasks").insert(task_data_for_db).execute()` block and `task_competencies` loop (lines 483–502) in `multiagent.py` with a single `task_id = validate_and_insert_task(task_data_for_db, supabase, env=env)` call, wrapped in `try/except TaskValidationError` and `try/except TaskWriteError` blocks that call `logger.error(str(e))` and re-raise
- [x] T024 Remove ad-hoc `isinstance` type checks in `multiagent.py` that duplicate Pydantic model coverage (verify each removal doesn't leave an unhandled code path; run a grep for `isinstance` after to confirm count drops)
- [x] T025 [P] Add entry to `docs/known_pipeline_pitfalls.md`: "Silent task_competencies link failure — task row inserted but zero competency links created; task invisible to candidate filters. Fixed in 002-supabase-validation-layer by TaskWriteError."

**Checkpoint**: Full pipeline run (`python multiagent.py generate-tasks ...`) completes without regression. A run with a known-bad competency_id aborts before the Supabase insert with a clear error message.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all story phases
- **Phase 3 (US1)**: Depends on Phase 2 — schema models need exception types
- **Phase 4 (US2)**: Depends on Phase 3 — FK check extends `validate_task_for_db()`
- **Phase 5 (US3)**: Depends on Phase 2 — `insert_task_with_competencies()` uses `TaskWriteError`; can start in parallel with Phase 4
- **Phase 6 (US4)**: Depends on Phase 3 — hardens the error formatting started in `TaskValidationError.__str__`; can start in parallel with Phase 5
- **Phase 7 (Polish)**: Depends on Phases 3–6 complete — wires everything into multiagent.py

### User Story Dependencies

- **US1 (P1)**: After Phase 2. No story dependencies.
- **US2 (P1)**: After US1 (extends the same function).
- **US3 (P2)**: After Phase 2. Independent of US1/US2 (different functions). Can parallelize with US2.
- **US4 (P2)**: After US1 (hardens `TaskValidationError` formatting). Can parallelize with US3.

### Within Each Phase

- Models before the functions that use them (T006/T007 before T008, T008 before T009)
- Implementation before tests that call it
- T004 and T005 are [P] — different class definitions, same file, no dependency between them

---

## Parallel Execution Examples

### Phase 2 (Foundational)
```
Parallel: T004 (TaskValidationError) + T005 (TaskWriteError)
Sequential after: T003 must exist first
```

### Phase 3 (US1)
```
Parallel: T006 (CriteriaEntry) + T007 (TaskBlob) → then T008 (TaskForDB) → T009 → parallel T010 + T011
```

### Phases 4 + 5 in parallel (once Phase 3 is done)
```
Stream A: T012 → T013 → T014   (US2: FK check)
Stream B: T015 → T016 → T017   (US3: TaskWriteError insert)
```

---

## Implementation Strategy

### MVP (User Stories 1 + 2 only — core guard)

1. Phase 1: Setup (T001–T002)
2. Phase 2: Foundational (T003–T005)
3. Phase 3: US1 schema validation (T006–T011)
4. Phase 4: US2 FK check (T012–T014)
5. Phase 7 partial: T021–T024 (wire into multiagent.py)
6. **STOP and VALIDATE**: Run full pipeline with a known-bad competency_id — confirm abort before insert

### Full Delivery

Continue with Phase 5 (US3), Phase 6 (US4), then complete Phase 7 (T025 docs).

---

## Task Summary

| Phase | Tasks | User Story | Parallelizable |
|-------|-------|------------|----------------|
| 1: Setup | T001–T002 | — | No |
| 2: Foundational | T003–T005 | — | T004, T005 |
| 3: US1 Schema | T006–T011 | US1 | T006+T007, T010+T011 |
| 4: US2 FK Check | T012–T014 | US2 | — |
| 5: US3 Hard Fail | T015–T017 | US3 | Whole phase ∥ Phase 4 |
| 6: US4 Error UX | T018–T020 | US4 | Whole phase ∥ Phase 5 |
| 7: Polish/Wire | T021–T025 | — | T025 |
| **Total** | **25** | | |

**Suggested MVP scope**: Phases 1–4 + T021–T024 (19 tasks) — delivers the two P1 stories end-to-end.
