# Task Classifier

> **Status:** Design decided (2026-05-27). Current implementation is partially aligned; the migration path below closes the gap.
> **Updated:** 2026-05-27
> **Sister doc:** [E2B Templates](./e2b-templates.md) — operational details for the templates this design uses as its capability sheet.

## Problem statement

The pipeline needs one consistent answer to:

> *"What infrastructure does this competency combo need, and which reviewer should grade it?"*

That answer flows into four downstream systems:

1. The **prompt-generator agent** — DSPy InputFields + HARD CONSTRAINT rules shaping the generated `run.sh`, `docker-compose.yml`, etc.
2. The **reference retriever** — picks structural exemplars by shape match.
3. The **eval critic personas** — DBA / MLE / SDET / … chosen by task shape.
4. The **E2B build/test gate** — boots the sandbox the candidate will receive.

If the answer is wrong, every downstream system inherits the lie. A FastAPI task misclassified as `PURE_CODE` gets generic boilerplate, a generic reviewer, and no template. The cost compounds.

A previous rule-based classifier (`prompt_generator/classifier.py`) tried to answer with hand-coded `if` branches over token lists. It dumped 183 of 339 dev tasks (54%) into the `PURE_CODE` default through three structural bugs: a framework-without-database check that returned `False` whenever both matched, missing tokens for entire languages (Flutter, Dart, Scala, Playwright, React Native, MERN), and wrong branches on edge cases like `Golang + Redis`. Rules go stale, substring matching has false positives, bugs emerge from rule interactions. Rules are not the answer here.

---

## The design — classifier picks `template_id` directly

A single LLM call matches a task's competency combo against the deployable template set. Each template carries a **capability sheet**: the runtime, frameworks, datastores, tools, and personas it can host. The LLM reads those sheets and returns either a match or a structured no-match.

```
                  competency combo (sorted, proficiency-suffixed)
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  LLM reads templates WHERE status = 'built'                   │
   │  Each row is a capability sheet:                              │
   │    template_id, runtime, frameworks, datastores, tools,       │
   │    personas, build_cmd, test_cmd, manifest_hash               │
   └──────────────────────────────┬───────────────────────────────┘
                                  │
                  ┌───────────────┴──────────────────┐
                  ▼                                  ▼
          MATCH                                NO MATCH
   { template_id,                        { no_match: true,
     persona,                              missing_capabilities,
     confidence }                          suggested_template,
                                           reason }
```

**Match** picks a template the LLM is confident can host the task, plus one persona from that template's `personas: text[]` list.

**No-match** is a first-class output, not a silent skip. It captures *why* no template fits — what capabilities the task needs, what template name the LLM proposes for it. The first time an infra / shell / Terraform task lands in the pipeline, no-match generates a structured "build new template" ticket; it doesn't quietly route to the Python template and hope.

There is no intermediate `Runtime` enum, no rule-based picker, no separate "what runtime" decision before "which template." The template rows ARE the classifier's input set. Adding a template is adding a row; the system can never claim to support tech it doesn't actually deploy.

### Why this shape

1. **One source of truth for what's deployable.** Today the `Runtime` Literal enum says we support `python | node | java | ...`, while `template_registry.status` says only `python` is built. Two versions of the same fact, maintained separately. With the merged design, the rows ARE the truth — the LLM literally cannot return a runtime we don't deploy.

2. **`no_match` is a first-class signal.** Infra / shell / Terraform tasks that fall through today become structured tickets with capability gaps and a suggested template name. Two years of these is a better template roadmap than any human-driven prioritization.

3. **Adding a template is data, not code.** No enum bump, no picker branch, no Python migration. Insert a row; the LLM considers it on the next cold classification.

4. **Shape and persona separate cleanly.** Shape is implied by the template (an `utkrusht-infra` task is by construction infra-shape). Specialty is the `persona` picked from the template's `personas` list. The conflated `kind` field disappears.

5. **Polyglot is honest.** A polyglot task with no matching template surfaces as `no_match` with a clear capability gap, not as a silent runtime collision.

### The schema

Two tables — same row count as today, but the seam moves to a useful place.

```sql
-- templates: the registry IS the capability sheet
CREATE TABLE templates (
  template_id        text PRIMARY KEY,        -- "utkrusht-python", "utkrusht-node-playwright"
  status             text NOT NULL,           -- "built" | "proposed" | "deprecated"

  -- Capability sheet (what the LLM reads to match)
  runtime            text NOT NULL,           -- "python3.12" — primary language/VM
  language_versions  jsonb DEFAULT '{}',      -- {"node":"20.11","python":"3.12"}
  frameworks         text[] DEFAULT '{}',     -- ["fastapi","sqlalchemy"]
  datastores         text[] DEFAULT '{}',     -- ["postgresql-16","redis-7"]
  tools              text[] DEFAULT '{}',     -- ["pytest","ruff","docker","helm"]
  needs_browser      boolean DEFAULT false,
  needs_gpu          boolean DEFAULT false,
  capabilities_note  text,                    -- free-form for anything structured fields miss

  -- Personas this template can host (list, not scalar — one image serves multiple personas)
  personas           text[] NOT NULL,         -- ["backend","data","mle"]

  -- Execution
  build_cmd          text NOT NULL,
  test_cmd           text NOT NULL,
  compile_cmd        text,

  -- Drift control (load-bearing for year-2 durability)
  manifest_hash      text NOT NULL,           -- sha256 of source Dockerfile/manifest
  generated_at       timestamptz NOT NULL,    -- when sheet was last regenerated from manifest
  registry_version   integer NOT NULL         -- monotonic; bumps on any sheet change
);

CREATE INDEX templates_active_idx ON templates(status) WHERE status = 'built';

-- task_template_match: the classification cache, pointing at templates
CREATE TABLE task_template_match (
  combo_key             text PRIMARY KEY,
  template_id           text REFERENCES templates(template_id), -- NULL = no_match
  persona               text NOT NULL,                          -- one of template.personas
  confidence            real,

  -- no_match path
  no_match_reason       text,
  missing_capabilities  text[],                                 -- ["terraform-cli","tflint"]
  suggested_template    text,                                   -- "utkrusht-infra"

  -- Cache invalidation keys
  classifier_model      text NOT NULL,                          -- "claude-sonnet-4-6"
  registry_version      integer NOT NULL,                       -- value at classification time
  classified_at         timestamptz DEFAULT now(),

  CHECK (
    (template_id IS NOT NULL AND no_match_reason IS NULL) OR
    (template_id IS NULL     AND no_match_reason IS NOT NULL)
  )
);
```

A cache hit requires `classifier_model = current AND registry_version = current_registry_version`. Either bumping invalidates stale entries automatically.

---

## Where we are today

The shipped pipeline implements the same input-to-deploy flow, but via two decision surfaces stitched together by a rule-based picker.

```
   competencies ──► TaskRuntime ──────► template_registry lookup ──► template_name
                    (runtime, kind,     (runtime PK lookup;            (used by gate
                     frameworks,         frameworks/needs_browser       and downstream)
                     datastores,         stored but not consulted)
                     needs_browser)
```

### Shipped components

| Component | Where |
|---|---|
| LLM classifier (Sonnet 4.6 via Portkey, strict JSON, retry-with-validation-error) | [`infra/classifier/llm_classifier.py`](../../infra/classifier/llm_classifier.py) |
| `TaskRuntime` Pydantic model — single closed `Runtime` Literal | [`infra/classifier/runtime.py`](../../infra/classifier/runtime.py) |
| `competency_combo_classification` cache table | [migration](../../migrations/2026-05-25-create-competency-combo-classification.sql) |
| `template_registry` table — `runtime` PK, one row per language | [migration](../../migrations/2026-05-25-create-template-registry.sql) |
| `resolve_plan(combo_key)` orchestrator — single registry-aware entry point | [`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) |
| `utkrusht-python` (only `built` row; node/java/php/go/rust/flutter/ruby/scala are `proposed`) | E2B registry |
| `sandbox_eval` reads `template_name` from registry | [`e2b_flow/sandbox_eval.py`](../../e2b_flow/sandbox_eval.py) |
| Persona-routed eval critics keyed off `TaskRuntime.kind` | [`evals.py`](../../evals.py) |

The picker function `_get_template(runtime)` in `runtime_resolver.py:140-188` is the entire current routing logic. It's a PK lookup by runtime; `kind`, `frameworks`, `needs_browser` are stored on the classification row but unused by routing.

### Gaps vs. the design

| Gap | Effect today |
|---|---|
| Closed `Runtime` Literal | New tech requires code change + migration + redeploy |
| No `personas: text[]` on templates | `kind` carries persona — conflated with shape, one value per task |
| No first-class `no_match` output | Infra / shell / Terraform tasks skip silently with `no_template` |
| No `manifest_hash` / capability sheet provenance | Image content can drift from documented commands; no CI check |
| No `(classifier_model, registry_version)` cache invalidation | Stale rows survive model upgrades and template changes |
| Picker ignores `frameworks` and `needs_browser` | Template variants (`python-llm` vs `python-web`) can't coexist under the `runtime` PK |
| `Runtime` enum and `template_registry.status` duplicate the same fact | Classifier can claim to support runtimes we don't actually deploy |

---

## Why the current shape doesn't carry us forward

The two-layer model isn't wrong by intent — it was the natural shape with one template and one runtime. As task variety grows, the seam between classifier output and routing accumulates structural failures. Concrete cases from real tasks:

| # | Task | Current model says | What breaks |
|---|---|---|---|
| A | Helm chart for a microservice | `runtime=none`, no `kind` fits | No infra template; gate skips; no quality signal |
| B | Rust backend + React frontend (polyglot) | Must pick one runtime | The other half can't build or test |
| C | MySQL → Postgres data migration | `datastores=[mysql, postgres]` | Source/target roles erased; eval can't verify directionality |
| D | Jupyter notebook analysis | None of the `kind` values fit | `pytest` is the wrong eval; no notebook execution path |
| E | PyTorch sentiment classifier | `runtime=python`, no GPU expression | Train-to-convergence isn't a test suite |
| F | Solana smart contract in Anchor | `runtime=rust` | `utkrusht-rust` has no `solana-test-validator`; classifier looks fine but template can't run tests |
| G | gRPC payments service in Go | `runtime=go`, `frameworks=[grpc]` | Wire protocol implicit in frameworks; no `.proto`/`protoc` step |
| H | Postgres primary + replica routing | `datastores=[postgres]` | Two role-distinct stores collapse into one entry |

Every failure has the same shape: **a single field forced to carry information about multiple independent dimensions**. The intuitive fix is "add more axes" — split `kind` into `shape`+`specialty`, plural-ize `runtime`, add `protocols`, add `eval_method`. But more axes doesn't fix the *seam*. It makes both sides more complex: the picker branch tree grows, the LLM has more enums to satisfy, and adding new tech still requires editing closed enums.

The structural fix is the design above: **stop carrying the task's needs through an intermediate model**. The template rows describe what we can deploy; the classifier matches against them directly. There's no model to "underdimension" because there's no model — just rows and a matcher.

---

## Migration path

The current implementation is partially aligned with the design. The migration is additive and reversible until the final step.

### Step 1 — extend `template_registry` (additive, reversible)

```sql
ALTER TABLE template_registry
  ADD COLUMN personas          text[] NOT NULL DEFAULT '{}',
  ADD COLUMN frameworks        text[] DEFAULT '{}',
  ADD COLUMN datastores        text[] DEFAULT '{}',
  ADD COLUMN tools             text[] DEFAULT '{}',
  ADD COLUMN needs_gpu         boolean DEFAULT false,
  ADD COLUMN language_versions jsonb DEFAULT '{}',
  ADD COLUMN capabilities_note text,
  ADD COLUMN manifest_hash     text,
  ADD COLUMN generated_at      timestamptz,
  ADD COLUMN registry_version  integer NOT NULL DEFAULT 1;
```

Backfill the `utkrusht-python` row with its current sheet (extracted from `infra/e2b/templates/python/template.py`).

### Step 2 — switch the PK from `runtime` to `template_id`

The current `runtime` PK blocks template variants — `utkrusht-python-llm` and `utkrusht-python-web` can't coexist when `runtime='python'` is unique. The new PK is `template_id`; `runtime` stays as a non-unique descriptor.

```sql
ALTER TABLE template_registry DROP CONSTRAINT template_registry_pkey;
ALTER TABLE template_registry RENAME COLUMN template_name TO template_id;
ALTER TABLE template_registry ADD PRIMARY KEY (template_id);
```

### Step 3 — manifest-hash CI gate (**the durability decision**)

Without this step, capability sheets drift from reality within months; the LLM picks based on stale info; the merged design rots. With it, sheets cannot lie. This is the single load-bearing investment.

- Each `infra/e2b/templates/<name>/template.py` emits a `manifest.json` at build time (apt packages, pip packages, language versions, exposed ports, `start.sh` commands).
- The build pipeline hashes the manifest and writes it to `template_registry.manifest_hash` for that row.
- CI gate: if the template's source changed but the row's `manifest_hash` doesn't match the freshly built manifest, the build fails.
- Bumping `manifest_hash` also bumps `registry_version`, invalidating the classification cache.

**If the team isn't ready to invest in this, stop at Step 2 and stay on the two-layer model.** The rule-based picker survives lying data better than an LLM does.

### Step 4 — classifier emits `template_id` + `persona`

Update the prompt in `infra/classifier/llm_classifier.py` to:

- Receive the active template rows (`status='built'`) inline in the prompt.
- Return `{ template_id, persona, confidence }` or `{ no_match: true, missing_capabilities, suggested_template, reason }`.
- Validate against the live row set: `template_id` must exist with `status='built'`; `persona` must be in that row's `personas`.

`TaskRuntime` stays — it becomes a *projection* of the picked template, computed on read for downstream consumers (prompt generator, reference retriever) that still read its fields. Migrate consumers off it one at a time.

### Step 5 — `task_template_match` table

Replaces `competency_combo_classification` for new rows. Backfill: copy old rows, derive `template_id` via the legacy picker, `registry_version=1`.

### Step 6 — wire the `no_match` path

Rows with `template_id IS NULL` are the template roadmap. A simple query against the `task_template_match` table — group by `missing_capabilities`, count, sort — produces "what to build next."

### Step 7 — drop the `Runtime` Literal enum

Irreversible. Do this only after at least one new template has landed via the new path. The enum is now redundant with the templates table; removing it makes the design unambiguous.

---

## Choices along the way

A handful of decisions inside this design are load-bearing enough to call out separately.

### Capability sheets are generated, not hand-written

The single failure mode that determines whether this design ages well. Someone bumps a Dockerfile (Node 20→22, adds `redis-cli`) but forgets the row; the classifier picks on stale info; the bug surfaces weeks later in eval. Mitigation: sheets generated from the image manifest at build time, hashed (`manifest_hash`), CI-checked. See Step 3 of the migration.

### Personas are a list, not a scalar

One template legitimately hosts multiple personas. `utkrusht-python` is reasonable for `backend`, `data`, `mle`, and `llm` tasks — same image, different reviewer. Forcing a single persona onto the template means either over-fragmenting templates or moving persona to the classification row (re-introducing the seam). Persona is a list on the template; the LLM picks one per task.

If a single task genuinely needs multi-persona review (full-stack task wanting both backend and frontend graders), that's an eval-layer concern — `task_template_match.persona` can become `personas[]` later. For now, one persona per match.

### No catch-all template

A `utkrusht-base` that runs any task feels safe but erases the highest-value signal the design produces. A `no_match` row with `missing_capabilities: ["terraform"]` is a roadmap. A catch-all that vaguely runs it as Python is silent failure dressed up as success.

### Cache invalidation has two keys

`classifier_model` and `registry_version`. Either bumping invalidates cached rows. Both are needed:

- Sonnet 4.6 → 5.x quietly changes decisions on borderline cases; without `classifier_model` in the key, cached rows survive the upgrade and the system drifts.
- A template's sheet gains `redis-cli`; without `registry_version` in the key, rows classified before the update never reconsider the now-better-fit template.

### Sibling templates, not E2B inheritance

When `utkrusht-python` splits into `utkrusht-python-nlp` / `utkrusht-python-llm` / `utkrusht-python-web` (which it will as task volume grows), the variants should each `FROM` a common Docker base, **not** chain via E2B's `from_template()`. Inheritance feels DRY but makes rebuild graphs ugly and CVE patching cascades. Siblings duplicate a small amount and are independently buildable / patchable.

---

## Template fragmentation policy

`utkrusht-python` is fat by design today. As task volume grows, real splits will be needed. The split decision should be signal-driven, not speculative.

### Signals that justify a split

1. **Base image bloat** — build time on the base past ~60 s or image size past some MB threshold. CI metric.
2. **Over-serving** — most tasks routed to the base also `pip install pandas / transformers / langchain` at sandbox-boot time. The `build_cmd` repeats "install X" per sandbox. Bake X into a sibling template.
3. **`no_match` clustering** — multiple `no_match` rows with the same `missing_capabilities`. Five `no_match` rows in a month asking for `["torch","transformers"]` is a `utkrusht-python-llm` ticket.

Signal (3) is the one the merged design gives you for free — the highest-signal source of "what template to build next," generated automatically rather than guessed at by product instinct.

### Sprawl avoidance

- Capability sheets must be **distinctive**. Two templates with 90% overlap confuse the LLM matcher. That's the signal to merge them, or sharpen the sheet.
- `status = "deprecated"` is for templates we've replaced; rows stay (cache validity) but the LLM stops picking them.
- Every CVE patch is N rebuilds. ~12 templates at the two-year mark is reasonable; 30 is sprawling.

---

## How this design ages

| Horizon | What we'll see | What we'll need |
|---|---|---|
| **6 months** | First sheet inconsistency (`"postgres"` vs `"postgresql-16"`) confuses matching. LLM occasionally picks the "plausible but wrong" template (`utkrusht-python` when task wanted `utkrusht-python-llm`). | Controlled vocabulary in capability columns; sharpen sheets where matches collide. |
| **2 years** | 15–25 templates. Cold classifications read 8–15 k tokens of sheets — cacheable, tractable. `no_match` clusters become the template roadmap. | Manifest-hash CI gate (without it, sheets drift); `status='deprecated'` policy to retire old variants. |

The **compounding win** is the `no_match` corpus: every task that doesn't fit yields a structured ticket. Two years of these is a better template roadmap than any human-driven guess.

The **compounding risk** is sheet-vs-reality drift. Mitigated only by the manifest-hash CI gate. Without that one investment, the design rots.

### Vs. the two-layer model

The two-layer model fails in two years on *closed-vocab drift* — Bun ships, the LLM emits `runtime=node, frameworks=['bun']` because Bun isn't in the enum, the picker routes to Node, Bun-specific behaviour fails subtly. Three months pass before anyone debugs it. Closed-vocab drift compounds silently.

The merged model fails on *sheet ambiguity* — LLM picks the wrong but plausible template. Surfaces in eval failure; fix is to sharpen the sheet (one row update). Louder failure, faster feedback.

---

## How `resolve_plan` works (current implementation)

[`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) is the single entry point. Every consumer goes through it; there is no second classification site anywhere in the codebase.

```
combo_key = make_combo_key(competencies)
                ▼
  SELECT runtime, kind, frameworks, datastores, messaging, needs_browser
    FROM competency_combo_classification
   WHERE combo_key = ?
                ▼
   ┌── HIT  → return ResolvedPlan(
   │            TaskRuntime(from row),
   │            template = _get_template(runtime)
   │          )                                       (~10 ms, $0)
   │
   └── MISS → classify_with_llm(competencies)         (~2 s, ~$0.001)
                ▼
              UPSERT competency_combo_classification
                ▼
              return ResolvedPlan(new TaskRuntime, template)
```

**Economics.** ~50 unique competency combos across 339 dev tasks → ~50 LLM calls ever → ~$0.05 to populate the cache. After that, every consumer reads a column. Misses happen at task-generation time, never on a user-facing hot path.

**Determinism.** Same input → same output, because the read path is a column lookup. The "LLM is non-deterministic" objection doesn't survive once a row exists.

**Override path.** Edit the Supabase row. Every consumer reads the cache directly, so the corrected row is authoritative — no code change needed when the LLM hallucinates once.

After the migration, the orchestrator's shape stays the same — only the cache table and the LLM output change.

### Consumers

| Consumer | Field used today | Field after migration |
|---|---|---|
| `multiagent.py:create_task` | `plan.kind` (persona) | `plan.persona` |
| `multiagent.py:create_task` | `plan.template.name` | `plan.template_id` |
| `generators/prompts/agent.py:step1` | `plan.task_runtime` (whole object) | `plan.task_runtime` (projection of the template row) |
| `e2b_flow/sandbox_eval.py` | `template_name_for_runtime(plan.runtime)` | `_get_template(plan.template_id)` |

---

## Failure modes — graceful degradation

The principle: **classifier failures never block task generation.** A task without a classification gets the generic eval critic and skips the build/test gate — exactly the prior behaviour before classification existed.

| Failure | Behaviour |
|---|---|
| Supabase unreachable at lookup time | Warn, fall through to direct LLM call (no upsert this call) |
| Supabase upsert fails at write time | Warn, return the resolved plan anyway; next call re-classifies |
| `SUPABASE_URL_APTITUDETESTSDEV` / `_API_KEY_…` env vars missing | Skip cache entirely, plain LLM path (used in unit tests) |
| LLM classifier raises after retry | Return empty `ResolvedPlan` — callers skip persona routing and the gate, never crash |
| Classifier returns `template_id` not in registry (post-migration) | Treat as `no_match`; log warning; do not boot a hallucinated template |
| `template_id` exists but `status != 'built'` | `_get_template` filters via `.eq("status", "built")`; gate skips with `no_template` |
| API role missing `GRANT` on the table | `permission denied for table` warning; same fall-through — needs the GRANT migration |

---

## Bootstrap — migrations to apply (in order)

| # | File | What it does |
|---|---|---|
| 1 | [`2026-05-25-create-template-registry.sql`](../../migrations/2026-05-25-create-template-registry.sql) | Creates the template registry |
| 2 | [`2026-05-25-create-competency-combo-classification.sql`](../../migrations/2026-05-25-create-competency-combo-classification.sql) | Creates the classification cache with FK to (1) |
| 3 | [`2026-05-25-grant-cache-tables.sql`](../../migrations/2026-05-25-grant-cache-tables.sql) | Grants `SELECT/INSERT/UPDATE/DELETE` to `anon`, `authenticated`, `service_role`. **Without this the cache silently fails on every call.** |
| 4 | [`2026-05-26-classification-drop-org-id.sql`](../../migrations/2026-05-26-classification-drop-org-id.sql) | Drops `organization_id` — over-applied multi-tenancy (classifications are platform-global) |
| 5 | *to be written* | Step 1 of the migration path — additive ALTER on `template_registry` |
| 6 | *to be written* | Step 2 — switch PK to `template_id` |
| 7 | *to be written* | Step 5 — create `task_template_match`, backfill from `competency_combo_classification` |

---

## Implementation status (2026-05-27)

| Component | Status |
|---|---|
| LLM classifier (Sonnet 4.6, strict JSON, retry) | **Shipped** |
| `TaskRuntime` Pydantic model | **Shipped — to be deprecated** at Step 7 |
| `competency_combo_classification` cache | **Shipped — to be superseded** by `task_template_match` at Step 5 |
| `template_registry` table (one row per runtime) | **Shipped — to be evolved** at Steps 1–2 |
| `resolve_plan` orchestrator | **Shipped — output shape changes** at Step 4 |
| `utkrusht-python` template (only `built` row) | **Shipped** |
| `sandbox_eval` reads `template_name` from registry | **Shipped** |
| `sandbox_eval` reads `build_cmd`/`test_cmd` from registry | **Proposed** (~15 LOC, see [E2B Templates](./e2b-templates.md)) |
| Persona-routed eval critics keyed off `TaskRuntime.kind` | **Shipped — re-keys off `persona`** at Step 4 |
| `personas: text[]` column on templates | **Proposed — Step 1** |
| Manifest-hash CI gate | **Proposed — Step 3, the durability gate** |
| Classifier emits `template_id` + `persona` | **Proposed — Step 4** |
| `task_template_match` table | **Proposed — Step 5** |
| Drop `Runtime` Literal enum | **Proposed — Step 7, irreversible** |

---

## What we should do next

The migration path above is the sequence. Order matters; latency-to-value is in the first few steps.

1. **Wire `sandbox_eval` to read build/test commands from `template_registry`** (~15 LOC). Validates the "registry as source of truth" pattern before the schema grows. See [E2B Templates](./e2b-templates.md).
2. **Step 1 of migration** — additive ALTER on `template_registry`, backfill the `utkrusht-python` row. Cheap, reversible.
3. **Step 3 — build the manifest-hash CI gate before the second template lands.** This is the only step whose absence makes the design rot.
4. **Defer Steps 4–7** until the second built template is real. The LLM-picks-template_id change is cheap to implement but premature when there's only one template to pick.
5. **Build the second template (`utkrusht-node-base`) with `personas[]` and a generated `manifest_hash` from day one.** Retrofitting these onto a growing template set is harder than starting with them.
