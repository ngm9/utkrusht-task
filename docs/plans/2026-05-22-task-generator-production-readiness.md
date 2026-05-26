# Task Generator — Refactor & Production-Readiness Plan

**Date:** 2026-05-22
**Owner:** TBD
**Status:** Proposal — for team review
**v1 scope:** Utkrusht-internal admin panel · multi-tenant-ready schema from day one

---

## TL;DR

The pipeline today is good prototype code in the wrong shape — a 2255-line
`multiagent.py` monolith + a subprocess-chain `run_pipeline.py` + writes into
the source tree + in-memory job state. It works for one operator on one
machine; it cannot sit behind even an internal admin panel without breakage on
the first concurrent run.

The rebuild is **two threads**:

- **Thread A — Refactor.** Split the monolith, replace the subprocess chain
  with an in-process orchestrator, introduce a generator + verifier pattern
  per stage. Foundation for everything else.
- **Thread B — Production state.** Combo classification cache, durable jobs
  table, conversations table, per-run workspace, transactional create,
  template registry, observability.

**v1 ships behind the Utkrusht admin panel** (single org). The data model is
multi-tenant from day one so opening to customer orgs (v2) is data-only, not
a schema change.

Total estimate: ~4–5 weeks of focused work for v1.

---

## Why this plan

Today's pipeline:

```
0. preflight                  task_agent_preflight.py
1. input files                generate_input_files          → writes into task_input_files/  in the repo
2. scenarios                  scenario_generator            → appends into shared task_scenarios.json
3. prompt generator           prompt_generator (DSPy)       → classifies independently; writes into agent_generated_prompts/
4. task creation              multiagent.py create_task     → classifies again, evals, gates, creates GitHub + gist + Supabase
```

…driven either by `run_pipeline.py` (CLI; spawns each stage as a subprocess
from a thread per request) or `task_builder/server.py` (web UI; same threading
model).

Concrete problems that block production:

1. `multiagent.py` is 2255 lines doing eight unrelated jobs.
2. `run_pipeline.py` is a subprocess chain — stages talk to each other via
   files on local disk; the next stage *reads* what the previous one *wrote*.
3. Stages **write into the source tree** (`task_input_files/`,
   `task_scenarios/`, `task_generation_prompts/agent_generated_prompts/`).
4. `scenario_generator` **appends** to a single shared `task_scenarios.json`.
   Two concurrent requests race → corrupted JSON.
5. Run state is an in-memory dict in `task_builder/server.py:RUNS`. Restart =
   in-flight runs gone with no trace.
6. The classifier runs in two places (`multiagent.py` + `prompt_generator/agent.py`);
   the stored `task_runtime` column is read by nobody (now removed); the
   template choice lives in a third place (`_TEMPLATE_FOR_RUNTIME`).
7. GitHub repos are created **before** the DB row exists → orphans on any
   mid-failure (including answer-repos = leaked solutions).
8. Gate covers 1 of 10 runtimes; the gate's tooling is hardcoded Python.
9. 3 of 4 task-type flows have no classification and no gate.
10. No tenancy column anywhere, no conversation persistence.

---

## v1 vs v2 scope — read this first

**v1 (now, ~4–5 weeks): Utkrusht-internal admin panel.**
- Single org. `organization_id` is hardcoded to Utkrusht's UUID everywhere.
- No row-level security yet. No per-customer GitHub org.
- *But* every table has `organization_id` from day one.

**v2 (later): open to customer orgs.**
- Switch from a hardcoded org_id to authenticated `auth.org_id()`.
- Add Supabase RLS policies.
- Per-org GitHub layout (sub-org or repo prefix).
- This is **data + policy**, not schema. Phase 3 of the old plan
  drops from "huge lift" to "a flip."

Designing the schema multi-tenant now is free; the v1→v2 transition is then
incremental, not a rewrite.

---

## Target architecture

```
┌─────────────────────────────────────────────┐
│  task_builder/                              │   UI + API + conversations
│  • FastAPI server                            │
│  • Conversation manager                      │
│  • POST /generate → enqueues a job          │
└──────────────────────┬──────────────────────┘
                       │ INSERT
                       v
┌─────────────────────────────────────────────┐
│  generation_jobs  (Supabase)                │
│   id, org_id, conversation_id, status, …    │
└──────────────────────┬──────────────────────┘
                       │ workers poll / SKIP LOCKED
                       v
┌─────────────────────────────────────────────┐
│  orchestrator/                              │   in-process; deterministic
│  • runs the 5 stages in order               │
│  • per-stage Generator + Verifier loop      │
│  • per-run /tmp/<run_id>/ workspace          │
└──┬──────┬──────┬──────┬──────┬──────────────┘
   v      v      v      v      v
preflight inputs scenarios prompts tasks      (each: generator + verifier)
                                  │
                                  v
                       ┌─────────────────────────────────┐
                       │  task_generation/  (refactor of │
                       │      multiagent.py)             │
                       │  • runtime_resolver (combo cache)│
                       │  • creator                      │
                       │  • evaluator                    │
                       │  • gate                         │
                       │  • persistence (DB + GitHub)    │
                       └─────────────────────────────────┘

                       ┌─────────────────────────────────┐
                       │  e2b_flow/                      │
                       │  • template_registry            │
                       │  • sandbox_eval (gate)          │
                       │  • templates/                   │
                       └─────────────────────────────────┘

                       ┌─────────────────────────────────┐
                       │  e2b_flow/                      │
                       │  • sandbox_manager (deploy)     │
                       │  • supabase_helpers             │
                       │  • CLI: python -m e2b_flow      │
                       └─────────────────────────────────┘
                       (DigitalOcean droplet deploy was
                        removed; E2B is the only live
                        deploy path.)
```

### Repository layout — engines, apps, data

The shape today mixes engine code with its own outputs, and curated source
with auto-generated outputs:

- `task_generation_prompts/` holds **both** curated prompts (`Basic/`,
  `Intermediate/`, `Beginner/`, `_general_reference/`) **and** agent-generated
  prompts (`agent_generated_prompts/`). You can't tell from the path which is
  source and which is output.
- `task_input_files/` similarly holds combo-input JSON (per-combo, generated)
  alongside `task_scenarios/` (scenario JSON, generated, with the shared-file
  append-bug source).
- Engines (`generate_input_files/`, `scenario_generator/`, `prompt_generator/`,
  `task_generation/`) sit at the same root level as the data they produce, with
  no naming cue.

**Three principles** drive the new layout:

| Principle | Means |
|---|---|
| **Engine vs. Data** | Code that *produces* outputs lives separately from the outputs themselves. |
| **Curated vs. Generated** | Hand-written, committed source data lives separately from auto-produced data (gitignored, ideally per-run `/tmp` once B4 lands). |
| **App vs. Engine** | User-facing apps (UI, CLI, orchestrator worker) live separately from the engines they invoke. |

**Target tree.**

```
utkrusht-task/
├── apps/                      ── USER-FACING ENTRY POINTS
│   ├── task_builder/          (was task_builder/) — FastAPI + chat + conversations
│   ├── cli/                   (new) — Click commands extracted from multiagent.py
│   └── orchestrator/          (replaces run_pipeline.py) — pipeline runner + stage agents
│
├── generators/                ── ENGINES (produce outputs)
│   ├── input_files/           (was generate_input_files/)
│   ├── scenarios/             (was scenario_generator/)
│   ├── prompts/               (was prompt_generator/ — DSPy agent + retriever)
│   └── task/                  (was task_generation/ — creator/evaluator/gate/persistence)
│
├── flows/                     ── SPECIALTY TASK-TYPE FLOWS
│   ├── pr_review/             (was pr_review_flow/)
│   ├── design_review/         (was design_review_flow/)
│   └── non_tech/              (was non_tech_flow/)
│
├── infra/                     ── SHARED INFRASTRUCTURE / UTILITIES
│   ├── classifier/            (extract: TaskRuntime + classify_task_runtime + llm_classifier)
│   ├── e2b/                   (was e2b_flow/ — gate + sandbox_manager + supabase_helpers + templates/ + deploy CLI)
│   ├── github_utils.py
│   ├── utils.py
│   ├── schemas.py
│   ├── evals.py
│   └── logger_config.py
│
├── data/                      ── ALL DATA — NO CODE HERE
│   ├── curated/               ── HAND-WRITTEN, COMMITTED TO REPO
│   │   ├── prompts/           (was task_generation_prompts/{Basic,Intermediate,Beginner}/)
│   │   └── prompts_reference/ (was task_generation_prompts/_general_reference/)
│   └── generated/             ── AUTO-PRODUCED (gitignored; per-run /tmp once B4 lands)
│       ├── input_files/       (was task_input_files/input_<combo>/)
│       ├── scenarios/         (was task_input_files/task_scenarios/)
│       ├── agent_prompts/     (was task_generation_prompts/agent_generated_prompts/)
│       └── task_artifacts/    (was infra_assets/tasks/)
│
├── docs/                      (already feature-organized)
├── tests/
├── migrations/
└── scripts/
```

**Why these names.**

- `apps/` — convention from many service repos. "Who calls who" reads
  top-down: `apps → generators → infra`.
- `generators/` — every subdir produces something. Plural because there are
  several engines, each focused on one stage.
- `data/curated/` vs `data/generated/` — the single most important split.
  Glance at a path; instantly know if you're looking at hand-written source
  or pipeline output.
- `infra/classifier/` — the TaskRuntime classifier is consumed by **both**
  `generators/task/` and `generators/prompts/`. Pulling it out of
  `prompt_generator/` (where it lives today) ends the double-classify and
  matches the combo-cache design in B1.
- `flows/` — distinct from `generators/`: a flow *uses* the generators to
  build a specific kind of task (PR review, design review, non-tech).
- No leading underscores on data dirs — `_curated/_generated` confuses
  tooling that treats `_*` as private. Plain `data/curated/` reads better.

**Concrete renames.**

| From | To |
|---|---|
| `task_builder/` | `apps/task_builder/` |
| `task_generation/` | `generators/task/` |
| `generate_input_files/` | `generators/input_files/` |
| `scenario_generator/` | `generators/scenarios/` |
| `prompt_generator/` | split: agent → `generators/prompts/`; classifier → `infra/classifier/` |
| `e2b_flow/` | `infra/e2b/` (carries the live deploy CLI — droplet path is gone) |
| `pr_review_flow/` | `flows/pr_review/` |
| `design_review_flow/` | `flows/design_review/` |
| `non_tech_flow/` | `flows/non_tech/` |
| `task_generation_prompts/{Basic,Intermediate,Beginner}/` | `data/curated/prompts/` |
| `task_generation_prompts/_general_reference/` | `data/curated/prompts_reference/` |
| `task_generation_prompts/agent_generated_prompts/` | `data/generated/agent_prompts/` |
| `task_input_files/input_<combo>/` | `data/generated/input_files/<combo>/` |
| `task_input_files/task_scenarios/` | `data/generated/scenarios/` |
| `infra_assets/tasks/` | `data/generated/task_artifacts/` |
| `run_pipeline.py` | **DELETE** (replaced by `apps/orchestrator/`) |
| `multiagent.py` | **DELETE** after refactor — only the `generate_tasks` shim remains, will move to `apps/cli/` |
| `droplet_utils.py` | **DELETED** (droplet deploy path retired) |

**Migration in three phases — none big-bang.**

| Phase | Work | Lands with |
|---|---|---|
| **0** *(done)* | `task_generation/` package already exists with the right shape. | A1 done. |
| **1a — generated data dirs** *(done 2026-05-25)* | Moved `task_input_files/input_*/`, `task_input_files/task_scenarios/`, `task_generation_prompts/agent_generated_prompts/`, `infra_assets/tasks/` → `data/generated/{input_files,scenarios,agent_prompts,task_artifacts}`. 7 path-constant updates: `generate_input_files/generator.py`, `prompt_generator/input_files.py`, `prompt_generator/__main__.py`, `run_pipeline.py`, `task_input_parser/prepare_inputs.py`, `scenario_generator/generator.py`, `utils.py`, `pr_review_flow/pr_review_utils.py`. `.gitignore` updated (gitignore `data/generated/task_artifacts/` + `pr_review_tasks/`, keep `agent_prompts/` + `scenarios/` tracked). **143 pass / 1 pre-existing fail.** | A1 follow-up. |
| **1b — curated prompts** *(deferred)* | The curated prompts in `task_generation_prompts/{Basic,Intermediate,Beginner,_general_reference}/` are **Python source modules**, not data — moving them under `data/curated/` either requires converting them to `.md` strings (with retriever / registry / validator rewrites) or making `data/` contain Python packages (violates the no-code-in-data principle). Deferred to its own scoped phase. | TBD. |
| **2 — engine packages** *(done 2026-05-25)* | All engines + flows + shared utilities moved into `generators/`, `infra/`, `flows/`. `task_generation/` → `generators/task/`. `generate_input_files/` → `generators/input_files/`. `scenario_generator/` → `generators/scenarios/`. `prompt_generator/` split: DSPy + retriever + validator + slugs → `generators/prompts/`; `runtime.py` + `llm_classifier.py` + `classifier.py` → `infra/classifier/` (breaks the prior import cycle permanently). `e2b_flow/` → `infra/e2b/`. `pr_review_flow/` → `flows/pr_review/`. `non_tech_flow/` → `flows/non_tech/`. Shared utilities (`github_utils.py`, `utils.py`, `schemas.py`, `evals.py`, `logger_config.py`) → `infra/`. CLI entry points (`python -m generators.{input_files,scenarios,prompts}`, `python -m infra.e2b`, `python multiagent.py`, `python -m cli`) all verified. **143 tests pass, 1 pre-existing fail.** | A1 → A2 boundary. |
| **3 — apps layer** | Build `apps/`: move `cli/` → `apps/cli/`, build `apps/orchestrator/` to replace `run_pipeline.py`, move `task_builder/` → `apps/task_builder/`. **1–2 days.** | A2 + A4. |

After Phase 3 the source tree has **no remaining references** to
`multiagent.py` or `run_pipeline.py`, and `git status` is clean after any
pipeline run (B4 invariant).

> **Decision recorded 2026-05-25** during plan review. Two open questions are
> tracked below (naming convention + `data/generated/` policy).

---

## Thread A — Refactor (the foundation)

### A1. Split `multiagent.py` into `task_generation/`

**Goal.** End the 2255-line monolith. One module per responsibility.

**Mapping.**

| Today (in `multiagent.py`) | Tomorrow |
|---|---|
| `create_task` + retry loop | `task_generation/creator.py` |
| `run_evaluations` + retry feedback helpers | `task_generation/evaluator.py` |
| `classify_task_runtime` call + plan resolution | `task_generation/runtime_resolver.py` |
| Gate invocation (lines 510-529) | `task_generation/gate.py` |
| GitHub + gist + Supabase writes | `task_generation/persistence.py` |
| Deploy + reset commands (droplet) | **DELETED** — E2B is the live deploy path (`python -m e2b_flow deploy-task`) |
| `generate_tasks` Click command | `cli/generate.py` |

**Estimate:** 2–3 days. Pure code reorganization; no behavior change.

### A2. Replace `run_pipeline.py` with an in-process orchestrator

**Goal.** Kill the subprocess chain. Stages run as in-process function calls
in one Python process per job.

**New shape (`orchestrator/pipeline.py`).**

```python
class Orchestrator:
    def __init__(self, job_id, brief, workspace: Path): ...

    def run(self) -> Result:
        plan = self.stage("preflight",   PreflightStage(self.brief))
        inputs = self.stage("inputs",    InputFilesStage(plan, self.brief))
        scenarios = self.stage("scenarios", ScenariosStage(plan, inputs, self.brief))
        prompt = self.stage("prompts",   PromptStage(plan, inputs, scenarios))
        task = self.stage("tasks",       TaskCreationStage(plan, prompt, inputs, scenarios))
        return task

    def stage(self, label, stage):
        # update job row → running, label
        # capture logs to object storage
        # call stage.run() with the workspace
        ...
```

**Benefits.**
- No subprocess fork per stage; ~seconds saved per run.
- Stages pass data **objects**, not files.
- Logs captured per-stage to object storage, referenced by the job row.
- Workspace is per-run `/tmp/utkrusht-runs/<run_id>/` for any stage I/O that
  genuinely needs disk (none after the orchestrator refactor, ideally).

**Estimate:** 1–2 days.

### A3. Per-stage Generator + Verifier agents

**Goal.** Extend the pattern already in `prompt_generator/agent.py` (DSPy
`Generate` ⇄ `Verify` signatures) to every stage that benefits from
reasoning-with-validation.

**Base classes (`orchestrator/agents.py`).**

```python
class Generator(Protocol):
    def generate(self, inputs: dict, feedback: str = "") -> Output: ...

class Verifier(Protocol):
    def verify(self, output: Output) -> Verdict:  # pass / fail with reasons
        ...

class GenerateVerifyLoop:
    def __init__(self, generator, verifier, max_attempts=3): ...
    def run(self, inputs) -> Output:
        feedback = ""
        for _ in range(self.max_attempts):
            out = self.generator.generate(inputs, feedback=feedback)
            v = self.verifier.verify(out)
            if v.passed: return out
            feedback = v.feedback
        raise VerifierGaveUp(...)
```

**Where this pays off.**
- Stage 2 scenarios — generator + a stricter verifier than today's (currently
  ≥1-passes-is-pass is too lax; verifier should check structural validity,
  scope-fit, novelty).
- Stage 3 prompt generation — already follows the pattern in DSPy form.
- Stage 4 task creation — already loops on eval critics; standardize on the
  same `GenerateVerifyLoop`.

**LLMs at decision points; deterministic at flow control.** The orchestrator
itself is plain Python. Reasoning lives inside specific stages where
verification adds value.

**Estimate:** 2–3 days for the framework + 1–2 days per stage to migrate.

### A4. `task_builder/` stays the UI/API/conversations module

After the refactor:
- `task_builder/server.py` exposes `POST /api/generate` (creates a conversation
  if needed, inserts a `generation_jobs` row, returns `job_id`).
- `task_builder/conversation.py` owns the chat that produces the brief.
- `task_builder/runner.py` becomes a thin SSE streamer reading from the job's
  log location — **no more spawning subprocesses from a thread**.

**Estimate:** 1–2 days (mostly subtraction).

---

## Thread B — Production state

### B1. Combo classification cache

**Goal.** Classify each competency combo **once, ever**. Every consumer reads
from one place.

**Schema.**

```sql
CREATE TABLE competency_combo_classification (
    combo_key            text PRIMARY KEY,         -- "Python (INTERMEDIATE), MongoDB (INTERMEDIATE)"
    organization_id      uuid NOT NULL,            -- multi-tenant from day one
    runtime              text NOT NULL,            -- python | java | none | ...
    kind                 text NOT NULL,            -- app | script | non_code | ...
    frameworks           text[]  NOT NULL DEFAULT '{}',
    datastores           text[]  NOT NULL DEFAULT '{}',
    messaging            text[]  NOT NULL DEFAULT '{}',
    needs_browser        boolean NOT NULL DEFAULT false,
    template_runtime     text REFERENCES template_registry(runtime),  -- FK to B6
    classifier_version   text NOT NULL,            -- bump when classifier prompt/model changes
    created_at           timestamptz NOT NULL DEFAULT now(),
    updated_at           timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, combo_key)
);
```

`tasks.combo_key text REFERENCES competency_combo_classification(combo_key)`.

**`resolve_plan(combo_key)`** in `task_generation/runtime_resolver.py`:
- Lookup → cache hit, return ResolvedPlan (combo + joined template recipe).
- Miss → one LLM call, INSERT, return.

**Estimate:** 1–2 days.

### B2. Conversations table (new — separate from jobs)

**Goal.** Persist the task-builder UI dialogue per org. Same conversation can
produce multiple job runs over time (refine the brief, re-generate, etc.).

**Schema.**

```sql
CREATE TABLE conversations (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   uuid NOT NULL,
    started_by        uuid,                        -- user_id
    messages          jsonb NOT NULL DEFAULT '[]', -- [{role, content, ts}, ...]
    final_brief       jsonb,                       -- the TaskBrief once the user confirms
    status            text NOT NULL DEFAULT 'active',  -- active | submitted | abandoned
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    submitted_at      timestamptz,
    abandoned_at      timestamptz
);
CREATE INDEX ON conversations (organization_id, created_at DESC);
```

A conversation is the **user-intent capture**; a job is the **system
execution**. One conversation → 0..N jobs (each "generate again" creates a
new job referencing the conversation).

**Estimate:** 1 day.

### B3. Generation jobs table

**Schema.**

```sql
CREATE TABLE generation_jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     uuid NOT NULL,
    conversation_id     uuid REFERENCES conversations(id),
    requested_by        uuid,
    brief               jsonb NOT NULL,             -- snapshot of TaskBrief at submit
    status              text NOT NULL DEFAULT 'queued', -- queued|running|failed|done
    stage               text,                       -- last stage label
    log_url             text,                       -- object storage path
    result_task_id      uuid REFERENCES tasks(task_id),
    error               text,
    started_at          timestamptz,
    finished_at         timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON generation_jobs (status, created_at);
CREATE INDEX ON generation_jobs (organization_id, created_at DESC);
```

**Worker.** `python -m orchestrator.worker` polls with `SELECT … FOR UPDATE
SKIP LOCKED`, claims one, runs the Orchestrator, updates the row at each
stage. On crash, watchdog returns long-stuck rows to `queued` / `failed`.

**Tech choice:** Postgres-backed queue (no Redis/Celery). Cap concurrent
workers via process count.

**Estimate:** 3–5 days.

### B4. Per-run workspace; stop writing the source tree

**Goal.** Source tree is code, not data. Every run has its own scratch.

- Stages accept an `output_dir` arg (default: `/tmp/utkrusht-runs/<run_id>/`).
- `scenario_generator` stops appending to shared `task_scenarios.json` —
  scenarios go to Supabase (a `generated_scenarios` table keyed by combo) or
  per-run files; never the repo.
- `prompt_generator` writes the generated prompt to the combo cache row
  (B1's `competency_combo_classification.template` could grow a `prompt_body`
  column, or a separate `combo_prompts` table). Never `agent_generated_prompts/`.

**Validation.** Fire 5 concurrent generations for the same combo → no file
corruption, no source-tree changes (`git status` clean after).

**Estimate:** 2–3 days.

### B5. Transactional task creation + reconciler

**Goal.** Stop orphan GitHub repos / gists.

**Reorder `create_task`:**
1. `INSERT INTO tasks (organization_id, combo_key, status='draft', ...) RETURNING task_id`.
2. Create GitHub template repo named with `task_id`.
3. Create answer repo, upload solution.
4. Create gist.
5. `UPDATE tasks SET status='ready', resources={...}`.
- Any failure 2–5 → `status='failed'` + best-effort cleanup.

**Reconciler** (daily): for each `ready` task, verify repo + gist still exist;
mark `broken` on drift. Delete artifacts for `failed` tasks > N days old.

**Estimate:** 1–2 days + 1 day for reconciler.

### B6. Template registry — separate table, owns recipes

**Goal.** One source of truth for "what does each runtime need." Shared by the
combo cache, the gate, and deploy.

**Schema.**

```sql
CREATE TABLE template_registry (
    runtime         text PRIMARY KEY,        -- python | java | node | go | ...
    template_name   text NOT NULL,           -- utkrusht-python | utkrusht-java | ...
    build_cmd       text NOT NULL,           -- pip install / mvn package / npm ci / ...
    test_cmd        text NOT NULL,           -- python -m pytest / mvn test / npm test / ...
    compile_cmd     text,                    -- compileall / tsc --noEmit / go vet / ...
    needs_browser   boolean NOT NULL DEFAULT false,
    description     text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);
```

Seed it with python (utkrusht-python + pip+pytest), and incrementally add
java/node/go as templates are built.

**Why a separate table from the combo cache.** Java's test command lives in
*one* place, not duplicated across every Java combo. Combo cache references
the runtime; resolve-time joins.

**Composable templates (later).** A second `template_layers` table for browser /
GPU / etc. capabilities; resolve-time picks base + needed layers. Not v1.

**`run_sandbox_eval`** reads `plan.build_cmd / plan.test_cmd` from the joined
ResolvedPlan instead of hardcoded `pip install` / `python -m pytest`.

**Estimate:** 2–3 days for the registry + the gate rewire. More if new
templates are built.

### B7. Observability + safety nets

- Metrics: jobs queued/running/failed (by org), stage timings p50/p95,
  classifier cache hit ratio, gate verdicts + **skips by reason and runtime**
  (so "we shipped K Java tasks unverified" is visible), orphan count, LLM cost
  per org/flow.
- Alerts: classifier failure rate, gate skips for *known* runtimes, queue
  depth, oldest queued job age, orphan count.
- Logs: keep the `[e2b-gate]` structured-block pattern; extend to other
  stages (`[classifier]`, `[orchestrator]`, `[jobs]`). All push to object
  storage; the job row points to the log URL.

**Estimate:** Ongoing. Initial setup 2–3 days.

### B8. Multi-tenant hardening (v2 — when opening to customers)

v1 has `organization_id` on every row, hardcoded to Utkrusht's UUID. v2 work:
- Switch from hardcoded `UTKRUSHT_ORG_ID` to authenticated `auth.org_id()`.
- Add Supabase RLS policies on every multi-tenant table.
- Per-org GitHub: prefix `<org-slug>-<task-name>` on repos, or per-org GitHub
  App installation.
- Per-org cost dashboards (already in B7).

**Estimate:** 3–5 days when triggered.

---

## Template assignment — best practice

**Today.** A static dict `_TEMPLATE_FOR_RUNTIME = {"python": "utkrusht-python"}`.
For Java/Go/Node/etc. the gate skips with `no_template`. The gate's commands
are hardcoded Python.

**Why static-only is fragile.**
- Hard rules over a single key. The pandas case the user raised: if the combo
  key is "Python" (not "Python+Pandas"), a string-match map can't say
  "this needs pandas." (In practice, `utkrusht-python` ships pandas in the
  fat base — so it's not a problem there, but the pattern is brittle.)
- Doesn't capture *capabilities* (browser, GPU, specific clients) — only the
  runtime label.
- LLM misclassification → wrong template. Mis-picking Elixir as `ruby` would
  boot a Ruby sandbox for an Elixir task → false failure.

**The good architecture.** Three layers:

1. **Classifier outputs facts**, not template names:
   `{runtime, kind, frameworks, datastores, messaging, needs_browser}`. The
   LLM never names a template (it would hallucinate names of templates we
   haven't built).

2. **Fat base templates** cover the common 95%:
   - `utkrusht-python`: fastapi, flask, django, sqlalchemy, redis, pymongo,
     langchain, llama-index, pandas, numpy, pytest — already there.
   - `utkrusht-java`, `utkrusht-node`, `utkrusht-go` to be built.
   - Task-specific libs come via the task's `requirements.txt` /
     `package.json` / `go.mod`, installed by the gate at run time.

3. **Composable capability layers** for the long tail (deferred to v2):
   - `+browser` (Playwright/Chromium) for `needs_browser=true`.
   - `+gpu` if ever needed.
   - Resolution picks base from `runtime`, adds layers from facts.

In v1 the resolution is a deterministic function:

```python
def resolve_template(runtime, needs_browser, ...) -> TemplateSpec:
    base = template_registry[runtime]            # may be None
    if base is None: return None                  # explicit no_template
    return base
```

Layers ship in v2. The combo cache's `template_runtime` FK to
`template_registry` makes the picture flat and auditable; the function above
is the only place "smarts" live.

**Confidence + escalation (nice-to-have).** The classifier could output a
confidence; below a threshold → human review (a row in a `needs_human_review`
table). Not v1.

---

## Storage decisions — what goes where

| What | Where | Why |
|---|---|---|
| `tasks`, `conversations`, `generation_jobs`, `competency_combo_classification`, `template_registry` | Supabase DB | durable, queryable, multi-tenant |
| Stage logs (`04_tasks.stderr`, etc.), generated code archives | Object storage (Supabase Storage / S3) | large blobs, cheap |
| Per-run scratch (stage I/O) | `/tmp/utkrusht-runs/<run_id>/` | transient, deleted at end |
| GitHub template repo + answer repo + gist | GitHub | candidate-facing canonical |
| `infra_assets/tasks/<id>/` local copy | Local FS (dev convenience) | optional; not authoritative |
| Source tree | **NEVER** | code, not data |

The post-refactor invariant: **`git status` is clean after any number of
pipeline runs.**

---

## Sequencing — v1 (Utkrusht admin panel)

```
Week 1   A1  split multiagent.py            (2–3 days)
         A2  in-process orchestrator        (1–2 days)
Week 2   B1  combo classification cache     (1–2 days)   ← lands BEFORE A3
         B6  template registry              (2–3 days)   ← lands BEFORE A3
         A3  generator + verifier framework (2–3 days)
         A4  task_builder thinning          (1–2 days)
Week 3   B2  conversations table            (1 day)
         B3  generation_jobs + worker       (3–5 days)
Week 4   B4  per-run workspace              (2–3 days)
         B5  transactional create + recon   (2–3 days)
Week 5   B7  observability                  (2–3 days, ongoing)
Later    B8  multi-tenant for customers     (3–5 days when triggered)
```

> **Why B1 and B6 land before A3 (combo cache + template registry before
> the agents).** The Generator + Verifier agents consume a ``ResolvedPlan``
> (runtime + kind + template + build/test recipe). If A3 ships before B1/B6,
> the agents are built around the *current* per-task classifier + scattered
> template logic — and will need refactoring when the combo cache + template
> registry land. Doing B1 + B6 first means agents are built on the right
> data shape from day one. (Decision recorded 2026-05-22 during plan review.)

**Minimum viable for "behind the Utkrusht admin panel":** A1–A4 + B1, B2, B3,
B4, B5 + B6. ~3–4 weeks.

Each phase has a rollback path; nothing is one-way.

---

## Open questions (decide before starting)

1. **Job queue technology.** Postgres-backed (`FOR UPDATE SKIP LOCKED`) is
   simplest and adds no infra. Alternatives: Celery+Redis, RQ. **Recommend:**
   Postgres-backed.
2. **Generator + Verifier framework.** Roll-our-own protocols (lightest), or
   adopt DSPy more widely (already used in `prompt_generator/agent.py`).
   **Recommend:** roll our own thin Protocol; reuse DSPy where it already
   lives.
3. **Object storage.** Supabase Storage (already authenticated) vs S3 vs
   GCS. **Recommend:** Supabase Storage for v1; switch only if we hit limits.
4. **Per-run workspace location.** `/tmp` on the worker box vs object storage.
   **Recommend:** `/tmp` for stage I/O, object storage for the final
   per-run log bundle.
5. **Stored generated prompts.** Add `prompt_body text` to the combo cache row,
   or a separate `combo_prompts` table. **Recommend:** start with a column on
   the combo cache row; promote to a separate table only if prompt history
   becomes important.
6. **`tasks.combo_key` FK type.** `text` (the natural key) or a generated
   `uuid`. **Recommend:** `text` FK to the combo's primary key — easier to
   read in tools, no extra joins.
7. **Repository top-level naming.** `apps/ + generators/ + flows/ + infra/ + data/`
   (as proposed in *Repository layout — engines, apps, data*) vs. flatter
   alternatives (e.g. `src/` + `lib/` + `data/`). **Recommend:** the
   five-bucket layout — names map 1:1 to the principles (engine vs. data,
   curated vs. generated, app vs. engine) so directory-glance answers
   "what is this?" without opening a file.
8. **`data/generated/` policy.** Gitignored entirely, or keep slim `.gitkeep`
   anchors with the dir committed? **Recommend:** gitignore the directory
   contents; commit a `.gitkeep` per subdir so the tree shape is stable in a
   fresh clone. Per B4 the *actual* outputs land in `/tmp/utkrusht-runs/<run_id>/`
   anyway; the repo's `data/generated/` exists for tooling-friendliness, not
   long-term storage.

---

## Out of scope

- Replacing OpenAI / Portkey / Claude.
- Re-doing the eval critics (already shipped).
- Replacing GitHub as the task-artifact host.
- DigitalOcean → E2B deploy migration (separate spike).
- Customer billing.

---

## Status snapshot — what's already done

- ✅ LLM `TaskRuntime` classifier (PR #1 / merged).
- ✅ Persona-routed eval critics (PR #2 / `feat/eval-personas`).
- ✅ Token-truncation hygiene (F11).
- ✅ E2B build/test gate + `utkrusht-python` template (PR #2 cont'd).
- ✅ Gate enabled by default for pipeline runs + structured `[e2b-gate]` logs +
  `stdout_tail` persisted to `eval_info.sandbox_eval`.
- ✅ Domain threaded through `generate_input_files` so org background reflects
  the picked domain.
- ✅ `tasks.task_runtime` column drop staged (migration in `migrations/2026-05-22-drop-task-runtime-column.sql`,
  write removed from `multiagent.py`, backfill script deleted).
- ✅ Comprehensive E2B build/test gate doc at `docs/eval-system/e2b-build-test-gate.md`.
- ✅ **A1 substantially landed** (`feat/task-generator-refactor`): `task_generation/`
  package with `_clients`, `runtime_resolver`, `evaluator`, `gate`, `persistence`,
  `creator` modules. `multiagent.py` trimmed from 2255 → 1519 lines (-32%).
  `create_task` now lives at `task_generation.creator`; multiagent.py is a
  thin shell for env validation + deploy/reset CLI commands. **43 tests
  passing** (9 new for `resolve_plan`, 5 new for `run_gate_for_attempt`).
  Remaining in A1: extract deploy code into `deployment/`, CLI commands into
  `cli/` (clean follow-ups, not blocking A2).
- ✅ **Repository layout decided** (2026-05-25): the *Repository layout —
  engines, apps, data* section captures the engines vs. data, curated vs.
  generated, app vs. engine split, with a three-phase migration that lines
  up with A1 → A2 → A4. Phase 1 (data dir renames) is the next concrete
  step after A1 wraps; nothing else in Thread A or B is blocked on it.
- ✅ **Droplet deploy path retired** (2026-05-25): `deployment/`,
  `droplet_utils.py`, and the `multiagent.py deploy_task` / `reset_task`
  Click commands were removed. E2B (`python -m e2b_flow deploy-task`) is
  the only live deploy / reset surface. `multiagent.py` now exposes only
  `generate_tasks`. The plan's earlier mention of `infra/deployment/` is
  also gone — the droplet code never made it past the dead-path stage.
- ✅ **Phase 1a layout migration shipped** (2026-05-25): generated outputs
  moved from `task_input_files/`, `task_generation_prompts/agent_generated_prompts/`,
  and `infra_assets/tasks/` into `data/generated/{input_files,scenarios,agent_prompts,task_artifacts}`.
  Curated prompts remain at `task_generation_prompts/` pending Phase 1b
  (conversion to `.md`). 143 tests pass; CLI smoke-checked.
- ✅ **Phase 2 layout migration shipped** (2026-05-25): all engines, flows,
  and shared utilities moved into `generators/`, `flows/`, and `infra/`.
  The load-bearing extraction is `infra/classifier/` — the TaskRuntime model
  and LLM classifier now live as shared infrastructure, breaking the prior
  two-way dependency between `task_generation/` and `prompt_generator/`.
  CLI entry points renamed: `python -m generators.{input_files,scenarios,prompts}`
  and `python -m infra.e2b`. 143 tests pass.
- ✅ **B6 — template registry wired** (2026-05-25): `_get_template()` in
  `generators/task/runtime_resolver.py` now reads from the `template_registry`
  Supabase table with a per-process cache and graceful fallback to the
  `_TEMPLATES` in-memory seed when the DB is unreachable. `run_sandbox_eval`
  in `infra/e2b/sandbox_eval.py` now takes a `ResolvedPlan` and reads
  `plan.template.build_cmd / test_cmd / compile_cmd` — no more hardcoded
  `pip install` / `python -m pytest`. **Pending one-off action:** apply
  `migrations/2026-05-25-grant-cache-tables.sql` on dev Supabase so the API
  role can SELECT from `template_registry` and `competency_combo_classification`.

These are *prototype-good*. The plan above turns them into *service-good*
behind the Utkrusht admin panel, with the schema designed so v2 (customer-facing
multi-tenant) is data + policy, not a rewrite.
