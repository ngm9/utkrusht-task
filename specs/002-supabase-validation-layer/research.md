# Research: Supabase Write Validation Layer

**Feature**: 002-supabase-validation-layer  
**Date**: 2026-05-18  
**Status**: Complete — no NEEDS CLARIFICATION remaining

---

## Decision 1: Pydantic v2 as the Schema Definition Layer

**Decision**: Use Pydantic v2 (already installed at 2.12.5) for all schema models. No new dependency needed.

**Rationale**: Pydantic v2 is already in `requirements.txt` and installed. It provides:
- Single-call full-model validation that returns ALL errors at once (via `ValidationError` which collects all field failures, not just the first)
- `model_validator(mode='before')` for cross-field checks (e.g., duplicate competency_id detection)
- `field_validator` for per-field constraints (non-empty strings, accepted enum values)
- Clean separation: schema definition in one place, calling code unchanged

**Alternatives considered**:
- `jsonschema` — already used in `schemas.py` for OpenAI structured outputs, but it returns one error at a time and the error messages are harder to format for operators
- `marshmallow` — not installed, not needed since Pydantic is already present
- Ad-hoc `isinstance` checks (status quo) — scattered across `multiagent.py`, returns only first failure, no single source of truth

---

## Decision 2: Module Placement — New Root-Level File `task_validation.py`

**Decision**: Add a single new file `task_validation.py` at the repo root, alongside `utils.py`, `schemas.py`, `evals.py`.

**Rationale**: Every shared utility in this codebase is a root-level module (`utils.py`, `schemas.py`, `evals.py`, `github_utils.py`, `droplet_utils.py`, `logger_config.py`). The validation layer is the same shape: a shared library imported by `multiagent.py`. Creating a sub-package would add `__init__.py` indirection and an extra import path for zero benefit — the file does not need a `__main__.py` because it is never invoked directly.

**Alternatives considered**:
- Sub-package `task_validation/` with `__init__.py` — unnecessary complexity for a single-file module (Constitution Principle I)
- Adding to existing `schemas.py` — wrong file; `schemas.py` is exclusively for OpenAI structured-output schemas and mixing Supabase write schemas would blur its purpose
- Adding to `utils.py` — `utils.py` is already overloaded; merging more unrelated logic compounds the problem

---

## Decision 3: FK Check Strategy — Single Batch Query per Run

**Decision**: Collect all unique `competency_id` values from the task's `criterias` list, then run a single `supabase.table("competencies").select("id").in_("id", ids)` query. Compare returned IDs against requested IDs to find missing ones.

**Rationale**: A single IN-clause query is one round-trip regardless of how many competency IDs are in the task (typically 1–3). This satisfies FR-011 (< 3 second overhead) easily. Individual per-ID queries would be 3× slower and add unnecessary DB load.

**Alternatives considered**:
- Individual `select().eq("id", cid)` per competency_id — N round-trips vs 1; rejected for performance
- Caching competency IDs locally — premature optimization; the competency table changes infrequently but a stale cache would defeat the purpose of the FK check

---

## Decision 4: Error Reporting — Structured `ValidationError` Exception

**Decision**: Define a custom `TaskValidationError(Exception)` that carries a list of `ValidationFailure(field, actual_value, constraint, environment)` dataclass instances. Raise it instead of returning a bool. Callers in `multiagent.py` catch it and re-raise as a pipeline abort.

**Rationale**: The spec requires ALL failures in a single error (FR-003, FR-004). Pydantic's `ValidationError` already collects all field errors; we wrap it with our own exception that also carries FK check failures in the same list. A single exception type means `multiagent.py` has one catch block, not two.

**Alternatives considered**:
- Return `(bool, list[str])` tuple — caller must remember to check the bool; easy to silently ignore a `False` return. Exceptions are harder to accidentally swallow.
- Logging + returning False (status quo) — silent failures; breaks FR-005 requirement that post-insert failures abort the run

---

## Decision 5: Replacement vs Supplement of `validate_task()`

**Decision**: Delete `validate_task()` from `multiagent.py` entirely and replace the call site with `validate_task_for_db(task_data_for_db, supabase_client)` from `task_validation.py`. The old function's checks are a strict subset of the new schema's checks.

**Rationale**: FR-012 explicitly requires replacement, not supplementation. Keeping both in place creates two sources of truth that will drift. The new Pydantic model covers every check the old function does (field presence, type, non-empty `definitions`) plus the new ones (FK checks, duplicate competency_id, proficiency enum).

**Alternatives considered**:
- Keeping `validate_task()` and adding FK checks to it — violates FR-009 (schema in one file) and FR-012; also keeps the `isinstance`-scattered pattern
- Wrapping `validate_task()` inside the new module — unnecessary indirection; the old function becomes dead code within one release

---

## Decision 6: `task_competencies` Insert Failure Handling

**Decision**: Wrap the `task_competencies` insert loop in a try/except that raises `TaskWriteError` (separate from `TaskValidationError`) on any failure. The error carries the task_id that was already inserted and the competency_id that failed, with an explicit operator instruction to delete the orphaned task row.

**Rationale**: FR-005 requires abort + named task_id on failure. Since the task row was already inserted when this failure occurs, the operator needs the task_id to clean up manually. Distinguishing `TaskValidationError` (pre-insert, nothing written) from `TaskWriteError` (post-insert, task row exists) gives the operator the right mental model for recovery.

**Alternatives considered**:
- Transactional rollback — Supabase's Python client does not expose transaction control directly; Supabase edge functions would be needed, which is far out of scope
- Re-using `TaskValidationError` for both — confusing; pre-insert and post-insert failures have different recovery procedures

---

## No Open Questions

All NEEDS CLARIFICATION items are resolved. Proceed to Phase 1.
