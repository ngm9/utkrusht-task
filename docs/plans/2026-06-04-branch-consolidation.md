# Branch Consolidation Plan — one clean branch (platform fixes + agent category)

> **Status:** Approved direction, not yet executed. Created 2026-06-04.
> **Owner:** Rohan. **Author:** consolidation session.
> Only change made so far: the `task_id` PK fix in `generators/task/persistence.py`.

## Goal

Collapse the scattered, all-uncommitted work into **one new branch** that has:

- the **architecture & fixes** from `feat/v1-production-readiness` — **not** the deployment/infra-heavy stuff,
- the **`run.sh` readiness gate** + **template family** from `feat/ai-engineering-v2`,
- the **agent-category proposal + implementation** (`docs/plans/2026-05-27-ai-engineering-task-category.html`),
- the **DAO/repository pattern extended** to the data-access code that still uses raw `sb.table()`.

## The decisive fact (why the strategy is "subtract")

`main` is a **pre-refactor ancestor** (top-level: `e2b_flow/`, `scenario_generator/`,
`generate_input_files/`, `pr_review_flow/`, `non_tech_flow/`). It has **none** of the
architecture — no `generators/`, no `infra/classifier/`, no `repository.py`, no
`sandbox_eval.py`. Everything good lives on `feat/v1-production-readiness` (which also
carries the deployment cruft).

**Therefore: base the new branch on `feat/v1-production-readiness` and DELETE the deployment
files** (small, safe subtraction) rather than base on `main` and re-apply ~57 commits
(huge, error-prone). Same end-state, a fraction of the risk.

## Branch topology (verified)

```
main (8cf2cb2, ancient) ──────●
                               \  (+57 commits, 0 behind)
                                ● feat/v1-production-readiness (f8bb1c7)  ← architecture + deployment, all here
                                   ├ feat/ai-engineering-category  (mock-LLM experiment — PARK)
                                   └ feat/ai-engineering-v2         (run.sh gate + template family — SALVAGE)
```
All three feature branches' work is **uncommitted** in their worktrees; branch pointers sit at f8bb1c7.

## Keep / Drop inventory

### ✅ KEEP — architecture & fixes (already on readiness)
- Module structure: the `generators/` + `infra/` + `flows/` + `cli/` refactor.
- Classifier + registry: `infra/classifier/*`, `generators/task/runtime_resolver.py`, `infra/e2b/manifest.py`.
- DAO exemplar: `generators/scenarios/repository.py`, `generators/task/persistence.py` (+ the `task_id` PK fix).
- Eval system: `infra/evals.py` (persona critics, token hygiene), `infra/e2b/sandbox_eval.py`.
- Task-gen hardening: `creator.py`, `evaluator.py` (hollow-task guards, retry feedback, dedup, canonical keys).
- Correctness migrations: templates / task_template_match / RLS / grants / `2026-06-04-grant-tasks-service-role.sql`.

### ❌ DROP — deployment / infra-heavy
- `infra/jobs/` (worker, Dockerfile), `infra/storage/s3.py`, `infra/metrics.py`.
- `docker-compose.task-builder.yml`, `*/Dockerfile`.
- `apps/orchestrator/` service (the CLI `create_task` path works without it).
- Deploy scripts: `scripts/reconcile_tasks.py`, `scripts/backfill_*`, `scripts/stage_upload_smoke.py`.
- **`task_builder/` web UI** — decided DROP for now (re-add cleanly later, decoupled from jobs/S3).

### Agent layer (from `ai-eng-v2` + the doc)
> **Canonical (06-04):** HTML plan rev 06-03 supersedes ADRs 0002/0003 — build the `python-ai-agent` template family + run.sh gate. ADR 0001's "grading is external (video-as-judge in Utkrushta)" stays true: the gate is gen-QA only, never a grading instrument.

- ✅ Bring in: `run.sh` readiness gate (`sandbox_eval.py` rewrite + `gate.py` + `tests/test_runsh_readiness_gate.py`) and the template family (`infra/e2b/templates/_base/python_common.py` → `python-base` + `python-ai-agent`) + the 4 migrations (register both templates, seed 4 ADVANCED competencies, bump registry).
- ❌ Drop from v2: the **scope-classifier** (`scope` field + leanest-superset prompt) — plan skips it; routing works off the capability sheet.
- 🅿️ Park: category's **mock-LLM** (`infra/agent_runtime/`, `generators/task/agent_scaffold.py`) — plan chose real-LLM + run.sh over mock+pytest.
- ✍️ **Author the `ai_agent_build` prompt (NEW work).** No curated `task_generation_prompts/Advanced/` exists; the only agent prompt today is a generic *generated* bootstrap (`data/generated/agent_prompts/Advanced/production_agent_engineering_advanced_prompt/`) loaded via `get_task_prompt_by_technology_stack()` keyed `"Production Agent Engineering (ADVANCED)"`. Author a curated `task_generation_prompts/Advanced/ai_agent_build_advanced_prompt.py` carrying the **task-family `run.sh` rules** (CLI `--selfcheck` / service `/health` / graph `.compile()` / store round-trip) + the invariants (never call a stub, key-gated model ping, LLM-free at gate), with competency scope injected. The family lives in the **prompt**, not a pipeline dispatcher — the gate stays family-agnostic (run `run.sh`, read exit 0/1).
- 🔧 **De-conflate agent-vs-ADVANCED in scenario gen (NEW work).** `get_proficiency_guardrails(proficiency)` ([generators/scenarios/prompts.py:701](generators/scenarios/prompts.py)) keys the agent-flavored guardrail purely on `proficiency == ADVANCED`, so "ADVANCED silently means agent." Key it on the **competency** instead (an `is_agent_competency()` / category-or-scope marker), so a future non-agent ADVANCED competency isn't force-fed agent guardrails. **No CLI flag** (`--free-form`/`--ai-agents`) — every scenario is free-form and the competency stays the selector.

## DAO extension — "do the same for the other stuff"

Pattern = function-modules (`init_supabase` → typed CRUD funcs), per
`generators/scenarios/repository.py`. Tables still on raw `sb.table()`, priority order:
1. **`tasks`** — sprawl across `persistence.py`, `creator.py`, `db_queries.py`, `runtime_resolver.py`, `infra/e2b/supabase_helpers.py` → new `generators/task/repository.py`.
2. **`templates` + `task_template_match`** — currently in `runtime_resolver.py` → a templates/match repo.
3. **`competencies`** — scattered across `generators/input_files/generator.py`, `generators/prompts/db_queries.py`, `task_builder/validation.py` → a competencies repo.
4. **`task_competencies`** junction — folds in once `tasks` is wrapped.

## ⚠️ Open conflicts to resolve before/at execution
1. **Competency UUID clash:** v2's seed migration inserts the 4 AI competencies with deterministic UUIDs (`a1a1…`), but dev already has Production Agent Engineering at `d31a…` (created via the generator). Pick one source of truth (recommend: adopt the deterministic-UUID seed; reconcile dev).
2. **Scope column:** dropping the scope-*classifier* while keeping v2's competency migration still lands `scope` prose in rows — harmless/unused. Confirm OK.

## Execution sequence (each step reviewable; no commits without Rohan's review)
1. Create the new branch off `feat/v1-production-readiness`. *(done — worktree `feat/agent-platform`)*
2. Subtract the DROP set (delete deployment files/dirs). Per the import-safety recipe: also **stub `gate.py`'s `from infra import metrics`** (no-op class) and **delete `tests/test_metrics.py`**. `apps/orchestrator/` + `infra/jobs/` stay DROP (override the classify agent, which over-kept them for their phase-gating edits).
3. Port the agent layer from `ai-eng-v2` (run.sh gate + template family + migrations); drop the scope-classifier parts.
4. **Author the curated `ai_agent_build` prompt** — task-family run.sh rules + invariants + competency scope.
5. **De-conflate agent-vs-ADVANCED** in the scenario guardrail (key on competency, not proficiency).
6. DAO extension: `tasks` repository first, then templates/match, then competencies.
7. Place the agent task-gen artifacts (input files, locked scenario, bootstrap prompt) + agent docs.
8. Resolve the two open conflicts (competency UUID, scope column).
9. Verify: end-to-end `create_task` run produces a real `tasks` row on dev.

## Already done
- `task_id` PK fix in `generators/task/persistence.py` (`mark_task_ready` + `mark_task_failed`: `.eq("id")` → `.eq("task_id")`). The `tasks` PK is `task_id`; `id` doesn't exist.
- `migrations/2026-06-04-grant-tasks-service-role.sql` (applied to dev; prod already had it).
