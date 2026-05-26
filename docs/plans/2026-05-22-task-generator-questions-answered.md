# Task Generator Plan — Your Questions Answered

**Date:** 2026-05-22
**Companion to:** [2026-05-22-task-generator-production-readiness.md](./2026-05-22-task-generator-production-readiness.md)
**Purpose:** Maps each question raised during the planning session to the decision in the main plan, with a short answer + detail + pointer to the section that covers it.

---

## Index of questions

| # | Question | Type |
|---|---|---|
| 1 | Where do generated artifacts go (if not the source tree)? | Data placement |
| 2 | Why `build_cmd` / `test_cmd` columns? | Schema |
| 3 | Is `combo_key` a foreign key in `tasks`? | Schema |
| 4 | How do we make template assignment smarter than a static map? | Architecture |
| 5 | Why `/tmp` for per-run files, not permanent storage? | Data placement |
| 6 | Autonomous agent system vs `run_pipeline.py`? | Architecture |
| 7 | Sequencing — agent system first or productionization first? | Sequencing |
| 8 | A `conversations` table — is it the same as `generation_jobs`? | Schema |
| 9 | Scope — Utkrusht-only v1 vs customer-facing? | Scope |
| 10 | Refactor `multiagent.py` into proper folders? | Architecture |
| 11 | One major plan doc covering all of the above. | Deliverable |
| 12 | Order of rebuild work? | Sequencing |
| 13 | Best practice for the orchestrator vs `task_builder` split? | Architecture |

---

## Q1. Where do we write generated artifacts if not the source tree?

**Short answer.** Three storage layers, each with a clear job. The source tree
is **never** one of them.

**The layers.**

| What | Where | Why |
|---|---|---|
| `tasks`, `conversations`, `generation_jobs`, `competency_combo_classification`, `template_registry` | **Supabase DB** | Durable, queryable, multi-tenant. |
| Stage logs (`[e2b-gate]` blocks, `04_tasks.stderr`, etc.), generated code archives | **Object storage** (Supabase Storage / S3) | Large blobs, cheap. The job row points at the URL. |
| Per-run stage I/O — files Stage 1 writes that Stage 2 reads *in the same run* | **`/tmp/utkrusht-runs/<run_id>/`** | Transient; deleted at end of run. |
| Candidate-facing template repo + answer repo + gist | **GitHub** | Canonical for the candidate. Tracked by the DB row's `resources`. |
| Source tree (`task_input_files/`, `task_generation_prompts/agent_generated_prompts/`, `task_scenarios/*.json`) | **NEVER** | Code is code; data isn't code. |

**Specifically.** Generated **scenarios** stop appending to the shared
`task_scenarios.json`; they're either written to a `generated_scenarios`
Supabase table (keyed by combo) or kept ephemeral per run. Generated
**prompts** (from the prompt-generator agent) move out of
`task_generation_prompts/agent_generated_prompts/` and into a column on the
combo cache row (or a `combo_prompts` side-table).

**Invariant after refactor:** `git status` is clean after any number of
pipeline runs.

**See main plan:** *Storage decisions — what goes where.*

---

## Q2. Why do we need `build_cmd` and `test_cmd` columns?

**Short answer.** They're needed — but **not on the combo cache table.**
They belong on a separate `template_registry` table (one row per runtime).

**Why we need them at all.** Today the gate hardcodes `pip install -r
requirements.txt` and `python -m pytest`. That works for Python only. To gate
Java tasks we need `mvn package` / `mvn test`. Go: `go build` / `go test`.
Node: `npm ci` / `npm test`. Without these stored somewhere, the gate can
never work for anything but Python.

**Why on `template_registry` and not on the combo cache.**

- Java's test command lives **once**, on the `java` row of `template_registry`.
- Every Java combo (`Java+Spring Boot`, `Java+Kafka`, `Java+MongoDB`)
  references that one row — no duplication.
- Compare: if we put `build_cmd / test_cmd` on the combo cache, every Java
  combo would store its own copy → drift, maintenance burden.

**Schema.**

```sql
CREATE TABLE template_registry (
    runtime         text PRIMARY KEY,        -- python | java | node | go | ...
    template_name   text NOT NULL,           -- utkrusht-python | utkrusht-java | ...
    build_cmd       text NOT NULL,           -- "pip install -r requirements.txt" / "mvn package"
    test_cmd        text NOT NULL,           -- "python -m pytest" / "mvn test" / "npm test"
    compile_cmd     text,                    -- optional parse/type check
    needs_browser   boolean NOT NULL DEFAULT false,
    description     text,
    created_at, updated_at timestamptz
);

CREATE TABLE competency_combo_classification (
    combo_key            text PRIMARY KEY,
    runtime              text NOT NULL REFERENCES template_registry(runtime),  -- FK
    kind                 text NOT NULL,
    frameworks           text[] NOT NULL DEFAULT '{}',
    datastores           text[] NOT NULL DEFAULT '{}',
    -- NO build_cmd / test_cmd here — looked up via the runtime FK
    ...
);
```

`resolve_plan(combo_key)` joins the two and returns a `ResolvedPlan` with
template + commands inline.

**See main plan:** *Thread B → B6. Template registry — separate table.*

---

## Q3. Is `combo_key` a foreign key in `tasks`?

**Short answer.** Yes.

```sql
ALTER TABLE tasks
  ADD COLUMN combo_key text REFERENCES competency_combo_classification(combo_key);
```

**Why it matters.**

- DB-level integrity — you can't insert a task pointing at a non-existent combo.
- Update the combo row (re-classify with a better prompt, fix a wrong field)
  → every task referencing it picks up the new value automatically. No
  per-task migration, no stale snapshots.
- Cheap join when querying ("show me all tasks classified as `kind=app` with
  MongoDB").

**About the dropped `tasks.task_runtime` column.** That column stored a
per-task snapshot, was read by nobody, and went stale on classifier
improvements. Dropping it (already staged in `migrations/2026-05-22-drop-task-runtime-column.sql`)
is the right move precisely because the FK to the combo cache replaces it
properly.

**See main plan:** *Thread B → B1. Combo classification cache.*

---

## Q4. How do we make template assignment smarter than a static map?

**Short answer.** Three layers. The classifier outputs **facts**, not template
names. A deterministic `resolve_template(facts)` picks a base. Capability
**layers** handle the long tail. The LLM never names a template.

**The pandas case you raised.** A task needs pandas, but the combo key is
just "Python." A pure `combo_key → template` lookup would seem to miss this.

In practice this is fine *today* because `utkrusht-python` ships pandas in
its fat base — so any Python combo has pandas available. But the *pattern* is
brittle. The right architecture is three layers:

**Layer 1 — Fat base per runtime.** Templates pre-install the common 95% of
libraries for that runtime. `utkrusht-python` already includes
fastapi/flask/django/sqlalchemy/redis/pymongo/langchain/llama-index/**pandas**/numpy/pytest.
For Java the future `utkrusht-java` ships maven/junit/spring base deps.

**Layer 2 — Task-specific via `requirements.txt`.** Anything not in the base
comes from the generated task's own dependency file. The gate runs
`pip install -r requirements.txt` (and the equivalent for other runtimes) at
gate time — picks up `redis-py-cluster`, custom ML libs, etc. So missing libs
get installed on demand.

**Layer 3 — Composable capability layers (future, v2).** For genuinely
different shapes — Playwright/Chromium, GPU, specific protocol stacks —
templates compose: pick a base by `runtime`, add layers by `needs_browser`
etc. The classifier outputs the facts; resolution picks base + layers
deterministically.

**The key principle.** The **classifier outputs facts**:

```
{ runtime: "python", needs_browser: true, datastores: ["mongodb"], ... }
```

**Not template names.** Because the LLM doesn't know which templates we've
actually built and would hallucinate ("utkrusht-python-with-mongo-extras").

A **deterministic function** then picks the template:

```python
def resolve_template(plan: ResolvedPlan) -> TemplateSpec | None:
    base = template_registry.get(plan.runtime)
    if base is None:
        return None  # explicit no_template — visible in metrics
    # v2: compose layers
    # if plan.needs_browser: base = base.with_layer(BROWSER_LAYER)
    return base
```

Auditable. Trace-able. No LLM in the picking loop. Smart but not mystic.

**Confidence + escalation (nice-to-have).** The classifier could output a
confidence; below threshold → flag for human review instead of guessing.
Deferred to v2.

**See main plan:** *Template assignment — best practice.*

---

## Q5. Why `/tmp` for per-run files, not permanent storage?

**Short answer.** Because `/tmp` is the right tool for *transient* stage I/O.
Anything that needs to survive lives in DB or object storage.

**What goes in `/tmp/utkrusht-runs/<run_id>/`.**

- Stage 1 wrote a `competency.json` file → Stage 2 needs to read it → Stage
  4 doesn't care after generation finishes. Pure handoff. **Transient.**
- Deleted automatically when the run finishes (or by tmpreaper on the box).
- Per-run isolated → no two runs see each other's files → no concurrent
  corruption.

**What does NOT go in `/tmp`.**

- The **task** itself → Supabase + GitHub (durable, canonical).
- **Stage logs** → object storage; the job row points at the URL.
- **Conversation messages** → `conversations` table.
- **Combo classifications** → `competency_combo_classification` table.
- **Template definitions** → `template_registry` table.

`/tmp` is *only* for in-flight scratch within one run. Once the run finishes,
nothing that mattered is in `/tmp` — it's all in DB or object storage.

**Why not put scratch in permanent storage too?** Because then:
- The "permanent storage" grows with every run, becomes a junkyard.
- Concurrent runs need isolated scratch anyway (one job's Stage 2 must not
  see another job's Stage 1 output).
- Permanent storage is slower (network round-trip per read) than local disk.
- Costs more.

The pattern is industry-standard for any batch pipeline: **durable state in
DB/object storage, ephemeral scratch in local disk per job.**

**See main plan:** *Storage decisions — what goes where; Thread B → B4. Per-run workspace.*

---

## Q6. Autonomous agent system vs `run_pipeline.py`?

**Short answer.** Don't go fully autonomous. Use a **deterministic
orchestrator** with **per-stage Generator + Verifier agents** where reasoning
adds value. LLMs at decision points; deterministic at flow control.

**Why not fully autonomous.** A "let the LLM decide what stages to run and
when" orchestrator is:

- **Slow.** Each routing decision = an LLM call. The pipeline already does
  4–6 LLM calls per run; doubling that to also let an LLM *decide* the steps
  pushes 5 min runs to 10+.
- **Expensive.** Same reason — more calls.
- **Non-deterministic.** Two identical inputs can take different paths.
  Customer support nightmare ("why did this task get classified differently
  than the one I generated yesterday?").
- **Hard to test.** Unit tests for "what does the agent choose to do here"
  are hard to write and brittle.
- **Hard to debug.** When something goes wrong, the trace is a chain of LLM
  reasoning steps. Reproducing requires the same model + the same prompt + the
  same temperature.

**The actually-good pattern: orchestrator + per-stage Generator + Verifier.**

- **Orchestrator** (a plain Python class) knows the 5 stages, the order, the
  retry rules, the failure handling. Deterministic. Fully testable.
- Inside each stage, where reasoning helps, a **Generator + Verifier loop**:
  Generator produces output (an LLM call), Verifier checks it (another LLM
  call OR rules), loop until accepted or budget exhausted.
- This is exactly the pattern already in `prompt_generator/agent.py` (DSPy
  `Generate` ⇄ `Verify` signatures). Just extended to other stages.

**Where Generator+Verifier pays off.**

- Stage 2 scenarios — generator + a stricter verifier than today's
  (today: ≥1 passes → ok, too lax). Verifier checks structural validity,
  scope-fit, novelty.
- Stage 3 prompt generation — already DSPy.
- Stage 4 task creation — already loops on eval critics. Standardize on the
  same `GenerateVerifyLoop`.

**Net.** You get reasoning-with-validation where it matters, and predictable
flow control everywhere else. That's the prod-grade pattern.

**See main plan:** *Thread A → A2 (orchestrator) and A3 (Generator + Verifier).*

---

## Q7. Sequencing — agent system first, productionization after?

**Short answer.** Largely yes for the *refactor* (A1+A2) — but **B1 and B6
land before A3**, not after. The Generator+Verifier agents are built ON
TOP of the combo cache + template registry, not the other way around.

**Why refactor first.**

- Building production features on top of the 2255-line monolith and the
  subprocess chain *bakes the wrong shape in deeper*. Tenancy, jobs, and
  transactional create are far cleaner to add to focused modules than to a
  monolith.
- Once stages are in-process function calls (A1+A2), adding a job row +
  worker process (B3) is a small change instead of a fundamental rewrite.

**Why B1 (combo cache) and B6 (template registry) come BEFORE A3.**

The Generator + Verifier agents in A3 consume a `ResolvedPlan` — runtime,
kind, template, build/test recipe. If A3 ships first, the agents are wired
to the *current* per-task classifier and the scattered template logic; the
moment B1 and B6 land, those agents need refactoring. Doing B1 + B6 first
means agents are built on the right data shape from day one — one
classification per combo, one source of truth for templates, all read
through `resolve_plan()`.

**Concrete week-by-week (revised 2026-05-22):**

```
Week 1   A1 split multiagent.py · A2 in-process orchestrator
Week 2   B1 combo cache · B6 template registry · A3 generator+verifier · A4 task_builder thinning
Week 3   B2 conversations · B3 jobs + worker
Week 4   B4 per-run workspace · B5 transactional create
Week 5   B7 observability
Later    B8 multi-tenant when opening to customers
```

**Minimum to put behind the Utkrusht admin panel:** A1–A4 + B1, B2, B3, B4,
B5, B6 (~3–4 weeks).

**See main plan:** *Sequencing — v1 (Utkrusht admin panel).*

---

## Q8. Is `conversations` the same as `generation_jobs`?

**Short answer.** No — different concerns. Both needed. They link via
`job.conversation_id`.

**The two things they capture.**

- **`conversations`** — the **user-intent capture**. The back-and-forth in
  the task-builder chat that produces the brief. Multiple messages, abandon-able,
  the user can refine over time.
- **`generation_jobs`** — the **system execution record**. One row per
  generate-button press. Status: queued → running → done/failed. References
  the conversation that produced it.

**Cardinality.** One conversation → 0..N jobs.
- 0 jobs if the user starts a conversation and abandons it.
- 1 job if the user submits once.
- N jobs if the user refines the brief and generates again (each "Generate
  again" is a new job, same conversation).

**Schemas.**

```sql
CREATE TABLE conversations (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   uuid NOT NULL,
    started_by        uuid,
    messages          jsonb NOT NULL DEFAULT '[]',  -- [{role, content, ts}, ...]
    final_brief       jsonb,                        -- the TaskBrief once confirmed
    status            text NOT NULL DEFAULT 'active', -- active | submitted | abandoned
    created_at, updated_at, submitted_at, abandoned_at
);

CREATE TABLE generation_jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     uuid NOT NULL,
    conversation_id     uuid REFERENCES conversations(id),  -- the source
    brief               jsonb NOT NULL,    -- snapshot at submit time
    status              text NOT NULL DEFAULT 'queued',
    stage, log_url, result_task_id, error, started_at, finished_at, ...
);
```

**Why separate.** A conversation can outlive any single job (refine + regen).
A job is a *snapshot* of the brief at submit time + the system's attempt to
execute it. Conflating them would lose either the conversation history or
the per-attempt job state.

**See main plan:** *Thread B → B2 (conversations) and B3 (jobs).*

---

## Q9. Utkrusht-only v1 vs customer-facing — what changes?

**Short answer.** v1 hardcodes `organization_id = UTKRUSHT_ORG_ID` everywhere
but the **schema is multi-tenant from day one**. v2 (opening to customers) is
a data + policy change, not a schema rewrite.

**What v1 looks like.**

- Every row in every multi-tenant table has `organization_id`. v1 hardcodes
  it to Utkrusht's UUID.
- No Supabase RLS (Row-Level Security) policies yet — single-org doesn't
  need them.
- One shared GitHub org (`UtkrushtApps`) under one shared bot token.
- The admin panel is internal — Utkrusht employees only.

**What v2 (later) adds.**

- Replace `UTKRUSHT_ORG_ID` constant with authenticated `auth.org_id()`.
- Add Supabase RLS policies on every multi-tenant table:
  `USING (organization_id = auth.org_id())`.
- Per-org GitHub layout — either prefix repos with the org slug or use per-org
  GitHub App installations.
- Per-org cost dashboards / quotas / billing surfaces.

**Why design multi-tenant from day one even though we're single-org now.**
Adding `organization_id` to existing tables later is a migration. *Refactoring
the code* to use `auth.org_id()` is hard if it was never threaded through.
Designing it in now is essentially free; pulling it apart later is expensive.

**See main plan:** *v1 vs v2 scope — read this first; Thread B → B8.*

---

## Q10. Refactor `multiagent.py` — into what?

**Short answer.** A `task_generation/` package + a `deployment/` package +
a `cli/` package. The 2255-line monolith becomes a small handful of focused
modules.

**Why `multiagent` is the wrong name.** It doesn't run multiple agents. It's
a CLI orchestrator that does eight unrelated jobs in one file: classify, generate,
eval, gate, GitHub repos, gist, Supabase storage, droplet deploy, reset.

**The split.**

| Today (in `multiagent.py`) | Tomorrow |
|---|---|
| `create_task` + retry loop | `task_generation/creator.py` |
| `run_evaluations` + retry feedback helpers | `task_generation/evaluator.py` |
| `classify_task_runtime` call + `ResolvedPlan` | `task_generation/runtime_resolver.py` |
| Gate invocation (lines 510–529) | `task_generation/gate.py` |
| GitHub repo + gist + Supabase writes | `task_generation/persistence.py` |
| `deploy_task` + `reset_task` + droplet code | `deployment/droplet.py` |
| `e2b_flow/sandbox_manager.py` content | `deployment/e2b_sandbox.py` |
| `droplet_utils.py` content | `deployment/droplet.py` (merged) |
| Click `@cli.command` definitions | `cli/{generate,deploy,reset}.py` |

**After the refactor:** `multiagent.py` is **deleted**. `run_pipeline.py` is
**deleted** (replaced by `orchestrator/`). `droplet_utils.py` is **merged**.

**See main plan:** *Module layout after refactor; Thread A → A1.*

---

## Q11. One major plan doc covering all of this.

**Delivered.** [`2026-05-22-task-generator-production-readiness.md`](./2026-05-22-task-generator-production-readiness.md)
in this same directory.

**What it covers, briefly.**

- TL;DR + scope (v1 Utkrusht / v2 customer-facing).
- The two threads: Thread A (refactor) and Thread B (production state).
- 13 sub-phases (A1–A4 + B1–B8) with goal, schema, code, validation,
  rollback, estimate per phase.
- Target architecture diagram + module layout.
- Storage decisions table.
- Template assignment best-practice section.
- Open questions to decide before starting.
- Out-of-scope list.
- Status snapshot of what's already done.

This Q&A doc is the **companion** that maps your questions to the right
sections.

---

## Q12. Order of rebuild work?

**Short answer.** Refactor first (A1+A2), then per-stage agents (A3), then
the data foundations (B1+B6+B2), then the job model + workspace + transactional
create (B3+B4+B5), then observability (B7). Multi-tenant hardening (B8) when
you decide to open to customers.

**Why this order.**

1. **A1 + A2 first** — splitting the monolith and killing the subprocess chain
   makes every later change easier. Pure code reorg, no behavior change, no
   risk.
2. **A3 (Generator + Verifier) next** — gives you the agent pattern, which the
   verifier in later stages needs.
3. **A4 (thin task_builder)** — cleanup; small.
4. **B1 + B6 + B2** — the data foundations (combo cache, template registry,
   conversations). These unblock the rest.
5. **B3 (jobs + worker)** — the durable execution model. Builds on the
   orchestrator from A2.
6. **B4 (per-run workspace) + B5 (transactional create)** — the safety layer.
   Source-tree-clean invariant + no orphan repos.
7. **B7 observability** — light it up so you can see what's happening.
8. **B8 multi-tenant hardening** — only when actually opening to customers.

**See main plan:** *Sequencing — v1 (Utkrusht admin panel).*

---

## Q13. Best practice for the orchestrator vs `task_builder` split?

**Short answer.** They're different layers and they stay separate.
`task_builder` is the **API/UI/conversation layer**; the **orchestrator**
is the pipeline runner that `task_builder` invokes through a job.

**Their responsibilities, side by side.**

| `task_builder/` | `orchestrator/` |
|---|---|
| FastAPI server | Pipeline class |
| Conversation state machine | Stage modules (preflight, inputs, scenarios, prompts, tasks) |
| Slot validation | Generator + Verifier framework |
| `POST /api/generate` → **inserts a job** | Worker process that **runs the job** |
| Server-side rendering / SSE log stream | Per-run workspace setup |
| Knows about users / orgs / conversations | Knows nothing about HTTP; pure pipeline |

**They communicate via the `generation_jobs` table.** `task_builder` writes
a job row; the worker (running the orchestrator) reads it. No in-process
threading. No subprocess chain. The DB is the queue.

**Why this is best-practice.** Web APIs and long-running pipelines have
**totally different scaling profiles** — APIs need many lightweight
connections, pipelines need few heavy workers. Coupling them means scaling
one means scaling the other. Decoupling via a job table means:

- Restart the API server without killing in-flight runs.
- Run 3 API servers + 2 workers, or 1 + 10, or any combination.
- Add another worker process and you've added concurrency, no API change.
- Workers can run on different machines from the API.

**See main plan:** *Target architecture diagram; Thread A → A4 (task_builder)
+ Thread B → B3 (jobs).*

---

## Summary table — each question to its plan section

| # | Question | Main plan section |
|---|---|---|
| 1 | Where to write generated artifacts | *Storage decisions* |
| 2 | `build_cmd` / `test_cmd` placement | *Thread B → B6* |
| 3 | `combo_key` FK | *Thread B → B1* |
| 4 | Smart template assignment | *Template assignment — best practice* |
| 5 | `/tmp` vs permanent | *Storage decisions; Thread B → B4* |
| 6 | Autonomous agent vs orchestrator | *Thread A → A2 + A3* |
| 7 | Sequencing (agent first?) | *Sequencing — v1* |
| 8 | Conversations vs jobs | *Thread B → B2 + B3* |
| 9 | Utkrusht-only v1 scope | *v1 vs v2 scope; Thread B → B8* |
| 10 | Refactor `multiagent.py` | *Module layout; Thread A → A1* |
| 11 | One major doc | The main plan doc itself |
| 12 | Order of work | *Sequencing — v1* |
| 13 | Orchestrator vs `task_builder` | *Target architecture; A4 + B3* |
