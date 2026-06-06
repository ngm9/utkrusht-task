# Feature Specification: Supabase Write Validation Layer

**Feature Branch**: `002-supabase-validation-layer`
**Created**: 2026-05-18
**Status**: Draft
**Input**: User description: "Add Pydantic models and a DAO layer to validate task data before Supabase writes so inconsistent data is rejected before it lands in the database."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Invalid Task Rejected Before Insert (Priority: P1)

A pipeline run generates a task where one or more fields are missing, empty, or the wrong type — for example, a `criterias` list that is empty, a `definitions` object that contains blank values, or a `task_blob` field missing a required sub-key. Today the task is inserted into Supabase anyway, producing a broken record. After this feature, the pipeline must detect the problem before any write occurs and exit with a clear error message naming every failing field.

**Why this priority**: A task with missing or malformed fields is invisible to candidates and produces confusing downstream errors. Catching this before the insert is the highest-value guardrail — it prevents silent corruption with zero schema-design risk.

**Independent Test**: Construct a task dict with a known bad field (e.g., empty `definitions`, missing `outcomes`). Call the validation layer directly and confirm it raises a structured error naming the field before any Supabase call is made.

**Acceptance Scenarios**:

1. **Given** a task dict where `definitions` is an empty object, **When** the validation layer is called, **Then** it returns a validation failure identifying `definitions` as the failing field with the reason "must not be empty" — no Supabase insert is attempted.
2. **Given** a task dict with a `criterias` list that is empty, **When** the validation layer is called, **Then** it returns a validation failure identifying `criterias` with reason "must contain at least one entry" — no Supabase insert is attempted.
3. **Given** a task dict where all required fields are present and correctly typed, **When** the validation layer is called, **Then** validation passes and the insert proceeds normally.
4. **Given** multiple fields are invalid simultaneously, **When** the validation layer is called, **Then** the error message lists **all** failing fields at once — not just the first one — so the operator can fix everything in one pass.

---

### User Story 2 — Missing Competency FK Caught Before Insert (Priority: P1)

A pipeline run produces a task whose `criterias` list references a `competency_id` that does not exist in the target environment's `competencies` table. Today the task is inserted first; the `task_competencies` relationship insert then silently fails, leaving the task with zero competency links and invisible to any candidate filter. After this feature, the pipeline must verify every `competency_id` exists in the correct environment **before** the task insert runs and abort with a clear error if any is missing.

**Why this priority**: This is the exact bug that caused a task to be invisible to candidates in production. A task with zero competency links cannot be fixed without a manual DB patch. Preventing it at insert time is cheaper than any post-hoc repair.

**Independent Test**: Use a `competency_id` value that does not exist in the dev `competencies` table. Call the validation layer pointing at dev. Confirm validation fails with a message naming the missing competency ID, and that zero rows are written to `tasks` or `task_competencies`.

**Acceptance Scenarios**:

1. **Given** a task whose `criterias` references a `competency_id` not present in the dev `competencies` table, **When** the validation layer runs pre-flight checks against dev, **Then** validation fails with a message listing the unknown competency ID — no task row is inserted.
2. **Given** a task whose `criterias` references a `competency_id` present in dev but not in prod, **When** the validation layer runs pre-flight checks against prod, **Then** validation fails with a message naming the missing competency ID and the environment — no task row is inserted.
3. **Given** all `competency_id` values in `criterias` exist in the target environment, **When** the validation layer runs pre-flight checks, **Then** validation passes and the insert proceeds.
4. **Given** a `criterias` entry where `competency_id` is null or an empty string, **When** the validation layer runs, **Then** validation fails with a message identifying the malformed criteria entry.

---

### User Story 3 — Silent Relationship-Link Failures Become Loud Errors (Priority: P2)

After a task is successfully inserted, the pipeline inserts rows into `task_competencies` to link the task to its competencies. Today, if any of these secondary inserts fail, the error is logged but execution continues — leaving the task partially linked in Supabase with no visible alert to the operator. After this feature, a failure in any `task_competencies` insert must abort the run and surface a clear error rather than a silent log line.

**Why this priority**: Post-insert relationship failures produce the same broken outcome as Story 2 but are harder to detect (the task row exists). Eliminating silent continuation of a partially-failed write is necessary to make the pipeline trustworthy.

**Independent Test**: Successfully insert a task, then simulate a `task_competencies` insert failure. Confirm the run aborts with a non-zero exit code and the error names the competency ID that failed to link and the task ID that was already inserted.

**Acceptance Scenarios**:

1. **Given** a task insert succeeds but a subsequent `task_competencies` insert fails, **When** the pipeline runs, **Then** the run exits with an error naming the failing competency ID and the task ID that was already inserted — execution does not continue to GitHub/Gist steps.
2. **Given** multiple `task_competencies` inserts are needed and the second one fails, **When** the pipeline runs, **Then** all failures are reported together (not just the first) before aborting.

---

### User Story 4 — Validation Errors Are Actionable (Priority: P2)

An operator receives a validation error mid-run. Today, errors from the pipeline are often single-line logger messages that don't tell the operator which record, which environment, or what value was actually wrong. After this feature, every validation error must be self-contained: it names the record being validated, the failing field, the actual value (or a safe truncation), and the expected constraint — enough for the operator to fix the input and re-run without reading any source code.

**Why this priority**: Unclear errors multiply debug time. A clear error is the difference between a 2-minute fix and a 30-minute investigation.

**Independent Test**: Trigger a validation failure on a known bad input. Confirm the error output contains: (a) which record was being processed, (b) which field failed, (c) what the actual value was, (d) what constraint was violated.

**Acceptance Scenarios**:

1. **Given** a task with a `criterias` entry that has a malformed `proficiency` value, **When** validation runs, **Then** the error message includes the field name, the actual bad value, and the list of accepted values.
2. **Given** a competency FK check fails, **When** validation runs, **Then** the error message includes the `competency_id` value that was not found and the environment that was checked.
3. **Given** validation passes, **When** the run completes, **Then** a one-line summary is printed naming the number of checks that passed (e.g., "Validation passed: 14 checks on task 'MySQL Basic'").

---

### Edge Cases

- **Supabase unreachable during FK check**: pre-flight FK query fails with a network error. Validation must abort with "could not reach Supabase [env]" — not silently skip the check and proceed.
- **Duplicate `competency_id` values in `criterias`**: detected and rejected before any insert, since duplicates would violate the `task_competencies` unique constraint.
- **A required field is present but `None`**: treated as missing — same error as an absent field.
- **Validation passes but the Supabase insert still fails** (network blip, race condition): this is an infra error, not a validation error — existing exception handling is sufficient and out of scope.
- **Non-task Supabase writes** (`gist_manager.py`, `generate_input_files`): out of scope for v1 — this feature targets only the `tasks` + `task_competencies` writes in `multiagent.py`.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST validate all task data fields against a defined schema before any row is written to the `tasks` table. Validation MUST cover: field presence, field type, non-empty constraints, and accepted value sets (e.g., `proficiency` must be one of `BASIC`, `INTERMEDIATE`, `ADVANCED`).
- **FR-002**: The system MUST verify that every `competency_id` referenced in `criterias` exists in the target environment's `competencies` table before the task insert runs. This check MUST happen in the same pipeline invocation as the write — no separate command required.
- **FR-003**: If any field-level validation fails, the system MUST reject the write and report **all** failing fields in a single structured error — never just the first failure.
- **FR-004**: If any pre-flight FK check fails, the system MUST reject the write and name every missing `competency_id` plus the environment checked.
- **FR-005**: If a `task_competencies` insert fails after the task row is successfully inserted, the system MUST abort the run with an error naming the failing competency ID and the already-inserted task ID, with an explicit instruction to clean up the orphaned row.
- **FR-006**: Validation MUST distinguish between missing fields, null fields, wrong-type fields, and empty-but-present fields — each requires a distinct error message.
- **FR-007**: Duplicate `competency_id` values within a single task's `criterias` list MUST be detected and rejected before any insert.
- **FR-008**: All validation logic MUST be callable as standalone functions against a task dict + a Supabase client — testable without running the full pipeline.
- **FR-009**: Adding a new required field constraint to the task schema MUST require changing exactly one file (the schema definition) — not scattered type checks across the codebase.
- **FR-010**: The validation layer MUST respect the existing `--env dev|prod` flag — FK checks run against the environment the pipeline is targeting.
- **FR-011**: Validation MUST NOT add more than 3 seconds of overhead per task on a typical developer workstation (the FK check is a single indexed lookup per competency ID).
- **FR-012**: The existing `validate_task()` function and all inline `isinstance` type checks in `multiagent.py` MUST be replaced by the new validation layer — not supplemented alongside it.

### Key Entities

- **Task Schema**: the authoritative definition of what a valid task looks like before insert — field names, types, non-empty rules, and accepted value sets. Single source of truth; all validation derives from it.
- **Validation Result**: the outcome of a validation attempt — contains pass/fail status, a list of structured errors (field name, actual value, constraint violated), and the count of checks run.
- **FK Check Result**: the outcome of a pre-flight competency existence check — contains the list of missing competency IDs and the environment that was queried.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero tasks with missing or broken competency links can reach Supabase — every pipeline run that references an unknown `competency_id` aborts before the `tasks` insert, confirmed by attempting an insert with a known-bad competency ID in the test suite.
- **SC-002**: An operator receiving a validation error can identify the problem and fix the input in **under 3 minutes** — without reading any source code — based solely on the error output.
- **SC-003**: Pipeline run time increases by **no more than 3 seconds** per task due to validation overhead, measured on a standard developer workstation against the dev Supabase instance.
- **SC-004**: Adding a new required field constraint to the task schema requires editing **exactly one file**, confirmed by making such a change and verifying no other file needs updating.
- **SC-005**: The existing `validate_task()` function and all inline `isinstance` checks in `multiagent.py` are removed — zero direct type-checking calls remain in the pipeline orchestration code, verified by grep after implementation.
- **SC-006**: Validation logic has unit test coverage runnable without a live Supabase connection (field-level checks) and integration test coverage runnable against dev Supabase (FK checks).
- **SC-007**: Re-running the pipeline after fixing a validation error produces a successful insert on the second attempt with no orphaned records from the first (failed) attempt, because no write was made during the failed run.
