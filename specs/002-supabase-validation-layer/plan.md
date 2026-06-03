# Implementation Plan: Supabase Write Validation Layer

**Branch**: `002-supabase-validation-layer` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-supabase-validation-layer/spec.md`

---

## Summary

Replace the ad-hoc `validate_task()` function and scattered `isinstance` checks in `multiagent.py` with a single `task_validation.py` module that uses Pydantic v2 models (already installed) to validate all task fields and runs a pre-flight batch FK check against the target Supabase environment before any row is written. Post-insert `task_competencies` failures are promoted from silent log lines to hard aborts. The result is a single schema definition file, zero silent failures, and actionable error messages that name every failing field at once.

---

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Pydantic 2.12.5 (already in `requirements.txt`), supabase-py (already in use), `logger_config.py` (existing)  
**Storage**: Supabase dev + prod (via existing `init_supabase(env)` pattern)  
**Testing**: pytest (to be added to `requirements.txt`); unit tests run without Supabase; integration tests require dev credentials  
**Target Platform**: Developer workstation / CI pipeline (Linux + Windows)  
**Project Type**: Internal library module — new root-level file `task_validation.py`, same shape as `utils.py`, `evals.py`, `schemas.py`  
**Performance Goals**: FK check adds < 3 seconds per task (single indexed batch SELECT)  
**Constraints**: No breaking changes to `multiagent.py`'s CLI interface; all validation callable without running the full pipeline  
**Scale/Scope**: 1 new file, ~150 LOC; replaces ~45 LOC in `multiagent.py`

---

## Constitution Check

*GATE: Pre-Phase-0. Re-checked post-design below.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Small Correct Thing First | ✅ PASS | Single new file; replaces existing function; no new abstractions |
| II. CLI-First / Plugin Registry | ✅ PASS | Internal library module, not a CLI entry point; doesn't affect plugin registry |
| III. Portkey Gateway Only | ✅ PASS | No LLM calls in the validation layer |
| IV. Database Safety | ✅ PASS | This feature *implements* the FK pre-flight check required by this principle |
| V. Local-First Artifact Saving | ✅ PASS | Validation runs before any local save or Supabase write |
| VI. Pipeline Determinism & Idempotency | ✅ PASS | Validation is stateless and deterministic; same input → same result |
| VII. Pre-Flight Validation & Schema Discipline | ✅ PASS | This feature *is* the pre-flight validation principle being enforced |
| VIII. No Customer-Source Leakage | ✅ N/A | No code generation or candidate-facing artifacts |
| IX. Manual Preview Gate | ✅ N/A | Validation is internal to the pipeline, not a parser preview stage |
| X. Cost Discipline | ✅ PASS | No LLM calls; one indexed DB lookup per run |
| XI. DRY | ✅ PASS | Eliminates 5+ scattered `isinstance` blocks; single schema definition |
| XII. Security by Default | ✅ PASS | Validates input before DB write; prevents malformed data in Supabase |
| XIII. Continuous Process Improvement | ⚠️ REQUIRED | The silent `task_competencies` failure must be added to `docs/known_pipeline_pitfalls.md` as part of this PR |

**Gate result**: PASS. No violations. XIII is a required action in the implementation tasks, not a blocker.

**Post-design re-check**: All principles still pass. The chosen design (single file, Pydantic v2, batch FK check) is the minimum-complexity correct solution.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-supabase-validation-layer/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── task-validation-api.md   ← Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             ← Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code

```text
task_validation.py          ← NEW: Pydantic models + DAO functions + exceptions
tests/
├── unit/
│   └── test_task_validation.py   ← field-level checks, no Supabase needed
└── integration/
    └── test_task_validation_integration.py  ← FK checks against dev Supabase

multiagent.py               ← MODIFIED: delete validate_task(), replace insert block
requirements.txt            ← MODIFIED: add pytest
docs/
└── known_pipeline_pitfalls.md   ← MODIFIED: add silent task_competencies failure entry
```

**Structure Decision**: Single root-level module. Matches the existing pattern of `utils.py`, `schemas.py`, `evals.py`, `github_utils.py`. No sub-package needed — the module is never invoked directly as a CLI.

---

## Implementation Phases

### Phase A — Core Module (`task_validation.py`)

1. Define `ValidationFailure` dataclass
2. Define `TaskValidationError` and `TaskWriteError` exceptions with formatted `__str__`
3. Define Pydantic models: `CriteriaEntry` → `TaskBlob` → `TaskForDB`
4. Implement `validate_task_for_db(task_data, supabase_client, env)` — schema + FK check
5. Implement `insert_task_with_competencies(task_data, supabase_client)` — DB writes with hard failures
6. Implement `validate_and_insert_task(task_data, supabase_client, env)` — convenience wrapper

### Phase B — Replace Call Sites in `multiagent.py`

1. Delete `validate_task()` (lines 206–247)
2. Remove all ad-hoc `isinstance` type checks that are now covered by Pydantic
3. Replace inline `supabase.table("tasks").insert(...)` block (lines 483–502) with `validate_and_insert_task()`
4. Import `validate_and_insert_task`, `TaskValidationError`, `TaskWriteError` from `task_validation`
5. Add catch blocks for both exception types

### Phase C — Tests

1. `tests/unit/test_task_validation.py` — happy path, each failure type, multi-failure, duplicate competency_id
2. `tests/integration/test_task_validation_integration.py` — real FK check against dev Supabase
3. Add `pytest` to `requirements.txt`

### Phase D — Documentation

1. Add pitfall entry to `docs/known_pipeline_pitfalls.md`: "Silent task_competencies link failure leaves task with zero competency rows"

---

## Complexity Tracking

*No Constitution violations requiring justification.*
