# Task Classifier

> **Status:** Merged design **shipped** — the Phase 3 cutover landed `templates` + `task_template_match` + `resolve_plan` (canonical names; `*_v2` suffixes and the legacy `competency_combo_classification` / `template_registry` / `TaskRuntime` removed). The next decided-but-not-yet-implemented layer is **scope-driven matching + a Python template family** (see [Scope-driven matching](#scope-driven-matching) below) — needed once more than one Python template exists.
> **Updated:** 2026-06-01
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

## Scope-driven matching

> **Decided 2026-06-01, not yet implemented.** Needed the moment a *second* Python template exists. With one fat `utkrusht-python`, every Python combo trivially matches it — the classifier needs no more than the competency name. A **template family** changes that.

### The trigger: a Python template family

Instead of one fat image, the Python runtime is a small **inheritance family, split by framework family** (not by datastore tier — see the finding below):

```
python-base                       # python 3.13 + pytest + Docker-in-Docker + common DB clients
  ├─ python-web                   # + django/flask/fastapi/sqlalchemy   (≈ today's utkrusht-python)
  ├─ python-data                  # + pandas/polars/numpy               (if data competencies justify it)
  └─ python-ai-agent              # + langgraph/crewai/mem0 + mock-LLM   (see ai-engineering plan)
```

This isolates heavy dependency pins (an agent framework's `langchain-core` pin vs Django's) and keeps each image lean, instead of forcing every Python task — even junior CRUD — onto one large image. (See [the AI-engineering plan](../plans/2026-05-27-ai-engineering-task-category.html) for the concrete `python-ai-agent` member.)

> **Why framework-family, not datastore tier.** A spot-check of the dev `competencies.scope`
> texts showed that scopes **reliably name the framework** (Django/Flask/FastAPI/langgraph are
> always present) but **do *not* reliably name a concrete datastore engine** — e.g. Python -
> Django INTERMEDIATE talks about "complex database queries and optimization" yet never says
> "postgres"; Flask BASIC says "Flask-SQLAlchemy or direct DB drivers" (engine-agnostic). So a
> `python-base`-vs-`python-db` split isn't supported by the classification signal, and web
> frameworks assume *a* DB anyway. The signal that **is** reliably present is the framework
> family — so the family splits on that, and each tier bundles the common DB clients (exactly
> as `utkrusht-python` already lists `postgres/mysql/mongo/redis`). The task's own
> `docker-compose.yml` decides which engine actually boots.

### The classifier change: feed the competency `scope` (approach B)

Today `classify_match` sees only competency **name + proficiency** (`Competency` dataclass + `_user_message` in `infra/classifier/llm_classifier.py`). With one template that was enough. With a family it can't disambiguate the **framework family** from the name alone — an abstract competency like `"Production Agent Engineering (ADVANCED)"` or `"Context & Cost Engineering (ADVANCED)"` names no framework at all, and even concrete ones need their framework menu to route between `python-web` and `python-ai-agent`. **The name names the competency; the scope names the framework family.**

The change is small and **system-wide** (every classification, not just AI):

1. Add `scope` to the `Competency` dataclass.
2. Render it in `_user_message` so the LLM sees the competency's framework/datastore **menu**, not just its title.
3. Change the prompt rule from *"pick the template that best matches"* to **"pick the LEANEST template whose capability sheet is a superset of what the scope implies."**

The "leanest" word is load-bearing: without it the LLM defaults to the richest template for everything and the family delivers no boot-time saving. A scope that needs two **incomparable** templates (neither a superset of the other) returns `no_match` — the signal to build a combined template or split the competency.

### Why `combo_key` stays a valid cache key

Classification becomes a pure function of `(competency set + scope)`, and scope is stable per competency — so the `combo_key` PK still holds. The earlier worry ("two scenarios for the same combo need different templates → PK conflict") dissolves: a Flask combo classifies to `python-web` once, and every Flask task — DB-backed or in-memory — boots that same image (the web tier bundles the DB clients; the task's own `docker-compose.yml` decides what actually runs). Per-task variance is resolved at **generation time** (the scenario's stack + the answer-schema/grade routing), never at template-selection time. Bump `registry_version` once after the scope change to re-classify every cached combo.

### The scope-authoring cost (narrower than it first looks)

Approach B makes the classifier *depend* on scope naming the **framework family**. The dev
spot-check is reassuring here: existing scopes already name their framework reliably
(Django/Flask/FastAPI are always present), so web/data routing needs little or no rework.
The real, much smaller cost is **authoring the 5 new AI competency scopes** so they clearly
name their agent frameworks (langgraph / crewai / pydantic-ai / mock-LLM / observability) —
otherwise they'd be mistaken for generic Python and route to `python-web`. Plus a quick
spot-check that existing framework families are named (they are). This is "write 5 scopes
well," not "audit 60."

---

## Where we are today

The merged design is **shipped**. The Phase 3 cutover replaced the old two-layer model (`TaskRuntime` enum → `template_registry` PK lookup → `template_name`) with the single-surface match described above:

```
   competencies ──► classify_match ──────► task_template_match ──► resolve_plan
                    (reads templates'        (one row per             (returns ResolvedPlan:
                     capability sheets;        combo_key;               template + persona)
                     LLM picks template        cached, invalidated
                     + persona)                by model/registry_version)
```

### Shipped components

| Component | Where |
|---|---|
| LLM classifier (Sonnet 4.6 via Portkey, strict JSON, retry-with-validation-error) → `classify_match` | [`infra/classifier/llm_classifier.py`](../../infra/classifier/llm_classifier.py) |
| `TaskTemplateMatch` + `Competency` models (the closed `Runtime` enum is gone) | [`infra/classifier/runtime.py`](../../infra/classifier/runtime.py) |
| `task_template_match` cache table — `combo_key` PK, `template_id` FK, `no_match` first-class | [migration](../../migrations/2026-05-28-create-task-template-match.sql) |
| `templates` table — `template_id` PK, capability sheet jsonb, `personas[]`, `manifest_hash` | E2B manifest → `templates` row |
| `resolve_plan(competencies)` orchestrator — single entry point; cache-then-LLM | [`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) |
| `utkrusht-python` (only `built` template today; the family split is the next step) | E2B registry |
| `sandbox_eval` boots `plan.template` and reads its `build_cmd`/`test_cmd` | [`infra/e2b/sandbox_eval.py`](../../infra/e2b/sandbox_eval.py) |
| Persona-routed eval critics keyed off `match.persona` | [`infra/evals.py`](../../infra/evals.py) |

### What's still ahead (the gaps this doc tracks)

| Gap | Status |
|---|---|
| First-class `no_match` output | **Shipped** — `task_template_match` rows with `template_id IS NULL` carry `missing_capabilities` + `suggested_template` |
| `(classifier_model, registry_version)` cache invalidation | **Shipped** — both keys checked on every cache hit |
| `personas: text[]` on templates, persona ≠ shape | **Shipped** — `match.persona` routes the eval critic |
| `manifest_hash` / capability-sheet provenance | **Partial** — manifest module + hash landed (`45d398f`); the CI drift-gate is still honor-system |
| Scope fed to the classifier (multi-template disambiguation) | **Not yet** — see [Scope-driven matching](#scope-driven-matching); needed when the family lands |
| More than one `built` template | **Not yet** — `utkrusht-python` is still the only built row |

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

## Migration path (✅ complete — historical record)

> **This migration shipped in the Phase 3 cutover (2026-05-27).** Steps 1–2 (extend + re-key the registry) became the `templates` table; Steps 4–5 (classifier emits `template_id`+`persona`, `task_template_match` table) and Steps 6–7 (`no_match` path, drop the `Runtime` enum) are all done. The one item still open is **Step 3's CI drift-gate** for `manifest_hash` (the manifest module + hash landed in `45d398f`; the build-time enforcement is still honor-system). The steps below are kept as the record of how the schema got here.

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

### Template inheritance is a build-time concern — the DB never models it

When `utkrusht-python` splits into the family (`python-base` / `-db` / `-llm` / `-ai-agent`), inheritance lives **entirely in the E2B build flow**, in two places, and is invisible to the `templates` table:

1. **Docker layer** — the child image is built on the parent's layers, so it physically contains everything the parent installed.
2. **Manifest layer** — `manifest.py` is Python, so the child composes the parent's capability dict at authoring time (`{**parent_caps, "frameworks": [*parent, "langgraph", …]}`). The resulting `manifest.json` is **already fully resolved**.

That resolved sheet is what lands in `templates.capabilities`. The classifier reads a **self-contained** sheet per row — no parent pointer to follow, no union to compute at query time, no denormalization step. **There is no `parent_template_id` column and no schema change for inheritance**; the capability sheet jsonb is self-contained by construction. (A nullable `built_from` audit column is a harmless nice-to-have for provenance, but nothing reads it.)

**Open mechanism choice (flag for review).** Two ways to realise the Docker layer, with a real trade-off:

| Mechanism | Pro | Con |
|---|---|---|
| **Sibling `FROM` a common base** (each member's Dockerfile does `FROM utkrusht-python-base`) | Independently buildable / CVE-patchable; flat rebuild graph | Duplicates a few layer declarations |
| **E2B `from_template()` chaining** (`python-ai-agent` chains from `python-llm`) | Strict DRY layering, smallest diffs | Rebuild graph cascades — patching the base re-triggers every descendant |

The earlier position in this doc was **sibling-from-common-base**, for CVE-patch isolation. The family design works under either; the manifest composition and the self-contained stored sheet are identical regardless. **Decide which mechanism before building the family.**

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
combo_key = make_combo_key(competencies)         # sorted, proficiency-suffixed
                ▼
  SELECT template_id, persona, confidence, no_match_reason, …
    FROM task_template_match
   WHERE combo_key = ?
                ▼
   ┌── HIT (fresh: classifier_model + registry_version match)
   │     → return ResolvedPlan(match, template = _get_template(template_id))   (~10 ms, $0)
   │
   └── MISS / stale
         → classify_match(competencies, active_templates = templates WHERE status='built')   (~2 s)
                ▼
              UPSERT task_template_match (with classified_at, model, registry_version)
                ▼
              return ResolvedPlan(match, template)
```

When the [scope-driven](#scope-driven-matching) change lands, `classify_match` also receives each competency's `scope` and picks the leanest superset template; the cache key and flow are unchanged.

**Economics.** ~50 unique competency combos → ~50 LLM calls ever → ~$0.05 to populate the cache. After that, every consumer reads a column. Misses happen at task-generation time, never on a user-facing hot path.

**Determinism.** Same input → same output, because the read path is a column lookup. The "LLM is non-deterministic" objection doesn't survive once a row exists.

**Override path.** Edit the Supabase row. Every consumer reads the cache directly, so the corrected row is authoritative — no code change needed when the LLM hallucinates once.

### Consumers (post-cutover)

| Consumer | Field used |
|---|---|
| `generators/task/creator.py` | `plan.match.persona` (eval-critic routing) + `plan.template` (gate boot) |
| `generators/prompts/agent.py` | `plan.template` capability projection (prompt generation) |
| `infra/e2b/sandbox_eval.py` | `plan.template.build_cmd` / `test_cmd` (gate) |

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

| # | File | What it does | Status |
|---|---|---|---|
| 1–4 | the `2026-05-25`/`2026-05-26` registry + classification + grant + drop-org-id migrations | Bootstrapped the original two-layer cache | superseded by the cutover |
| 5 | [`2026-05-28-create-templates.sql`](../../migrations/2026-05-28-create-templates.sql) | The `templates` table (capability sheet, `personas[]`, `manifest_hash`) | **applied** |
| 6 | [`2026-05-28-create-task-template-match.sql`](../../migrations/2026-05-28-create-task-template-match.sql) | `task_template_match` cache, backfilled from the old classification table | **applied** |
| 7 | [`2026-05-29-add-timestamps.sql`](../../migrations/2026-05-29-add-timestamps.sql) | `templates.generated_at` + `task_template_match.classified_at` | pending apply |
| 8 | [`2026-05-29-drop-legacy-tables.sql`](../../migrations/2026-05-29-drop-legacy-tables.sql) | Drops `competency_combo_classification` + `template_registry` | apply after full smoke |

---

## Implementation status (2026-06-01)

| Component | Status |
|---|---|
| LLM classifier `classify_match` (Sonnet 4.6, strict JSON, retry) | **Shipped** |
| `templates` table (capability sheet, `personas[]`, `manifest_hash`) | **Shipped** |
| `task_template_match` cache (`combo_key` PK, `no_match` first-class) | **Shipped** |
| `(classifier_model, registry_version)` cache invalidation | **Shipped** |
| `resolve_plan(competencies)` orchestrator | **Shipped** |
| Classifier emits `template_id` + `persona`; persona routes the eval critic | **Shipped** |
| `Runtime` Literal enum + `TaskRuntime` + legacy cache | **Removed** (Phase 3 cutover) |
| `sandbox_eval` boots `plan.template` + reads `build_cmd`/`test_cmd` | **Shipped** |
| `utkrusht-python` template (only `built` row) | **Shipped** |
| Manifest module + `manifest_hash` | **Shipped** (`45d398f`) |
| Manifest-hash **CI drift-gate** | **Not yet** — the durability gate; still honor-system |
| Scope fed to the classifier + "leanest superset" rule | **Not yet** — [scope-driven matching](#scope-driven-matching) |
| Python template **family** (`-base`/`-db`/`-llm`/`-ai-agent`) | **Not yet** — first split lands with the AI-engineering work |

---

## What we should do next

1. **Build the manifest-hash CI drift-gate before the second template lands.** This is the one investment whose absence makes the design rot — sheets silently drift from the images and the LLM picks on lies. Everything else can wait; this can't.
2. **Land the first template-family split together with the scope-driven classifier change** — they're one unit of work (a second template is what *makes* scope-driven matching necessary). See [scope-driven matching](#scope-driven-matching) and the [AI-engineering plan](../plans/2026-05-27-ai-engineering-task-category.html).
3. **Decide the inheritance mechanism** (sibling-`FROM`-common-base vs E2B `from_template()` chaining) before authoring the family — see [the inheritance section](#template-inheritance-is-a-build-time-concern--the-db-never-models-it).
4. **Author the 5 new AI competency scopes to name their agent frameworks** (+ spot-check that existing scopes name their framework family — they do) so scope-driven matching routes them to `python-ai-agent` rather than `python-web`.
