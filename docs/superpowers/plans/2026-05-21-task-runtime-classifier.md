# TaskRuntime Classifier Implementation Plan

> **Status:** Implemented; staged for review on branch `feat/task-runtime-classifier`.
> Tests green (47 passed).

**Goal:** Replace the rule-based `TaskCategory` enum classifier in `prompt_generator/` with a structured `TaskRuntime` pydantic model produced by a single LLM call.

**Architecture:** One LLM call (Claude Sonnet 4.6 via Portkey gateway) per invocation, returning a `TaskRuntime` record. The result is persisted on a new `tasks.task_runtime` JSONB column. No separate cache table — the backfill script does in-memory dedup so each unique competency-set incurs exactly one LLM call.

**Spec:** [docs/research/task-classifier-and-templates.md](../../research/task-classifier-and-templates.md)

> ⚠️ **Why no cache table?** An earlier draft of this plan added a `task_runtime_cache` table keyed by a sorted competency string. The numbers didn't justify it: ~50 unique competency-sets in the dev DB × ~$0.001 per LLM call = **$0.05** lifetime saving — at the cost of a permanent table, two indexes, and a 65-line `runtime_cache.py` module. Refactored away. In-memory dedup at backfill time gets the same cost saving without the schema overhead.

---

## File structure (as shipped)

**Created:**
- `prompt_generator/runtime.py` — `TaskRuntime` pydantic model + `Competency` dataclass + `Runtime` / `Kind` Literal type aliases (53 lines)
- `prompt_generator/llm_classifier.py` — single LLM call with strict JSON parsing + one retry (130 lines)
- `migrations/2026-05-22-task-runtime-column.sql` — `ALTER TABLE tasks ADD COLUMN task_runtime JSONB` + analytics index (13 lines)
- `scripts/backfill_task_runtime.py` — one-shot backfill with in-memory dedup (136 lines)

**Modified:**
- `prompt_generator/classifier.py` — full rewrite (~35 lines, was ~200). Deletes `TaskCategory`, every `_*_TOKENS` list, every `_has_*` helper, and the old `classify_task_category` function. New entry point: `classify_task_runtime(competencies, *, llm_client=None) -> TaskRuntime`.
- `prompt_generator/__init__.py` — re-exports `classify_task_runtime`, `to_competencies`, `Competency`, `TaskRuntime`.
- `prompt_generator/agent.py` — DSPy `GeneratePromptSignature` and `VerifyPromptSignature` now declare four structured input fields (`runtime`, `frameworks`, `datastores`, `kind`) instead of one `task_category` string. HARD CONSTRAINT block rewritten to instruct the LLM in those terms, including the explicit "DO NOT install runtime/libs in run.sh" rule. `agent.forward()` calls `classify_task_runtime` at Step 1 and threads the four fields into both Generate and Verify calls.
- `prompt_generator/retriever.py` — reference selection now keys off `(runtime, kind)` instead of `task_category`. `RetrievalResult.runtime: TaskRuntime | None` replaces `category: TaskCategory`. `retrieve_references` takes an optional `runtime` argument; Level 5 fallback fires only when supplied.
- `prompt_generator/trainset.py` + `prompt_generator/compile.py` — emit four structured fields per training example instead of one `task_category` string.
- `task_agent_preflight.py` — drag-along fix: was reading `result.category.value`; updated to use `RetrievalResult`'s new shape.

**Tests:**
- `prompt_generator/tests/test_prompt_generator_runtime.py` — 7 tests (field defaults, validation, JSON round-trip, immutability, Competency.name_lower)
- `prompt_generator/tests/test_prompt_generator_llm_classifier.py` — 6 tests (mocked Sonnet client; parse, prose tolerance, retry, retry failure, empty input, system-prompt sanity)
- `prompt_generator/tests/test_prompt_generator_classifier_entry.py` — 4 tests (thin LLM wrapper)
- **Deleted:** `prompt_generator/tests/test_classifier.py` — tested the old enum API

Test convention note: tests for the `prompt_generator` package live in `prompt_generator/tests/`, alongside existing `test_retriever.py` / `test_input_files.py` / `test_slugs.py`. The top-level `tests/` directory is reserved for cross-package integration tests.

---

## Tasks (history)

### Task 1 — `TaskRuntime` pydantic model
Files: `prompt_generator/runtime.py`, `prompt_generator/tests/test_prompt_generator_runtime.py`.
`TaskRuntime(BaseModel, frozen=True)` with `runtime`, `frameworks`, `datastores`, `messaging`, `needs_browser`, `kind` and Literal-typed enums. `Competency` frozen dataclass with `name`, `proficiency`, `name_lower` property.

### Task 2 — LLM classifier
File: `prompt_generator/llm_classifier.py`.
`classify_with_llm(competencies, *, client=None) -> ClassifierResult` makes one Sonnet call via the Portkey gateway (mirrors `task_builder/conversation.py`), parses the JSON, validates against the `TaskRuntime` pydantic schema, retries once on bad output, then fails with `ValueError`. Exports `ClassifierResult(runtime, confidence)`, `_SYSTEM_PROMPT`, `build_client`.

### Task 3 — Supabase migration
File: `migrations/2026-05-22-task-runtime-column.sql`.
```sql
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS task_runtime JSONB;
CREATE INDEX IF NOT EXISTS idx_tasks_task_runtime_kind
    ON tasks ((task_runtime->>'kind'));
```
Apply via the Supabase SQL editor on dev first, then prod.

### Task 4 — `classify_task_runtime` entry point
File: `prompt_generator/classifier.py`.
Thin wrapper — delegates to `classify_with_llm` and returns the runtime. No cache lookup, no `supabase` param. Existing `to_competencies(items)` helper kept for converting raw JSON dicts. The deleted code: `TaskCategory` enum, every `_*_TOKENS` list, `_matches_any`, `_has_db` / `_has_web_framework` / `_has_backend_language` / `_has_frontend_only` / `_has_container`, and the old `classify_task_category`.

### Task 5 — Package re-exports
File: `prompt_generator/__init__.py`.
```python
from prompt_generator.classifier import classify_task_runtime, to_competencies
from prompt_generator.runtime import Competency, TaskRuntime
__all__ = ["Competency", "TaskRuntime", "classify_task_runtime", "to_competencies"]
```

### Task 6 — Rewrite `agent.py`
File: `prompt_generator/agent.py`.
- Import switched from `TaskCategory, classify_task_category` to `classify_task_runtime` + `TaskRuntime`.
- HARD CONSTRAINT block (lines 154-170) rewritten to derive structure from `runtime` / `frameworks` / `datastores` / `kind` / `needs_browser`, with an explicit rule that runtime/libs are pre-installed by the E2B template — so generated `run.sh` doesn't install them.
- STRUCTURE MISMATCH replaces the verifier's CATEGORY MISMATCH check.
- `GeneratePromptSignature` and `VerifyPromptSignature` gain four `dspy.InputField`s (`runtime`, `frameworks`, `datastores`, `kind`) — `task_category` removed.
- `agent.forward()` calls `runtime = classify_task_runtime(competencies)` at Step 1; passes the four fields to both `self.generate(...)` and `self.verify(...)`.

### Task 7 — Rewrite `retriever.py`
File: `prompt_generator/retriever.py`.
- Import switched to `from prompt_generator.runtime import Competency, TaskRuntime`.
- `RetrievalResult.category: TaskCategory` → `runtime: TaskRuntime | None = None`.
- `_find_category_examples` → `_find_runtime_examples(runtime, proficiency, limit)` — heuristic file-name matching now keys off `runtime.kind`, `runtime.datastores`, `runtime.messaging`, `runtime.needs_browser`.
- `retrieve_references` takes an optional `runtime` argument. Level 5 fallback fires only when supplied. `task_agent_preflight.py` calls without it (skips Level 5); `agent.py` and `trainset.py` pass it.

### Task 8 — Rewrite `trainset.py` and `compile.py`
Both files emit four structured fields per training example instead of one `task_category` string. Column schemas updated in lockstep so dry-run output matches.

### Task 9 — Backfill script
File: `scripts/backfill_task_runtime.py`.
- Loads every row of `tasks` with `criterias` not null and `task_runtime` null.
- Groups by an order-invariant `frozenset((name.lower().strip(), proficiency))` fingerprint.
- Calls `classify_with_llm` **once per unique group**, fans the resulting `TaskRuntime` to every task in the group with a `tasks` UPDATE.
- Surfaces any group whose `confidence < 0.7` for human review.
- Idempotent — re-runs skip rows that already have a `task_runtime`.

Estimated cost: ~50 unique groups across 339 dev tasks → ~$0.05 + ~3 min wall time.

### Task 10 (user action) — Validation run + report
Apply the migration via the Supabase SQL editor on dev, then:
```bash
PYTHONPATH=. .venv/bin/python scripts/backfill_task_runtime.py --env dev
```
Capture the resulting distribution. The expected outcome (per the design doc): `kind="script"` with empty `frameworks` / `datastores` / `messaging` drops from ~54% under the rule-based classifier to under 15% — that's the success bar this PR is verified against.

---

## Sequencing into the broader plan

```
┌────────────────────────────────────────────────────────────┐
│ THIS PR — classifier refactor                              │   ~3220 / 311
│ • TaskRuntime pydantic model + Competency                  │   one-time LLM
│ • LLM classifier (Sonnet via Portkey)                      │   spend ≈ $0.05
│ • Migration: tasks.task_runtime JSONB column               │
│ • Rewrite agent.py / retriever.py / trainset.py / compile  │
│ • Backfill script with in-memory dedup                     │
│ • 47 tests (model, LLM, entry-point + existing retriever)  │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ task-eval-optimizer Phase 1 — persona-routed eval critics  │   ~120 LOC
│ Routes by TaskRuntime.kind (DBA for db_only, MLE for llm,  │
│ SRE for containerised, …)                                  │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ E2B template buildout — ~10 templates beyond python-sql    │   per template:
│ Verified SDK capabilities documented in design doc § 'E2B  │   ~80 LOC + start.sh
│ SDK capabilities — verified'.                              │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ task-eval-optimizer Phase 3 — E2B build/test gate          │   ~250 LOC
│ (FOLLOWUPS.md F12)                                         │
└────────────────────────────────────────────────────────────┘
```

---

## What changed vs the original draft of this plan

Earlier drafts (version dated 2026-05-21, before review) proposed a separate `task_runtime_cache` Supabase table keyed by a sorted competency-set string, with a `runtime_cache.py` module wrapping cache lookups and upserts. That added two indexes, a 65-line module, an 80-line test file, and a 24-line migration — to save $0.29 over the lifetime of the dev DB.

The refactor (this version) keeps only the per-task JSONB column. De-duplication moves from the production schema into the backfill script, where it's a 30-line in-memory grouping.

Other diffs vs the earlier draft:

- The implementation plan no longer includes per-task `git commit` steps. The user reviews and commits manually (see project memory `agent-commits-user-reviews-first`).
- Test file location was corrected from `tests/test_prompt_generator_*.py` to `prompt_generator/tests/test_prompt_generator_*.py` — the package's own `tests/` subdir is the existing convention.
- `runtime_cache.py` and its test file (`test_prompt_generator_runtime_cache.py`) were dropped entirely.
- `prompt_generator/classifier.py` is no longer a thin orchestration layer that calls cache + LLM + cache-write; it's just an LLM call.
- `agent.py` and `trainset.py` no longer pass `supabase=` to `classify_task_runtime` — the function doesn't need it.
