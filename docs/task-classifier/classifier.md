# Task Classifier

> **Status:** Classifier + classification registry shipped (2026-05-25). Shape/specialty split AND a structural "merge classifier and template registry" proposal are documented below — neither implemented.
> **Updated:** 2026-05-26
> **Sister doc:** [E2B Templates](./e2b-templates.md) — what the classifier output gets handed to. (The "merge into one decision" proposal below would collapse the seam between the two docs; until then they remain sisters.)

## Problem statement

The pipeline needs one consistent answer to the question:

> *"What infrastructure does this competency combo need?"*

That answer flows into **four** downstream systems:

1. The **prompt-generator agent** (DSPy InputFields + HARD CONSTRAINT rules that shape the generated `run.sh`, `docker-compose.yml`, etc.)
2. The **reference retriever** (picks structural exemplars by shape match)
3. The **eval critic personas** (DBA / MLE / SDET / … chosen by task shape)
4. The **E2B build/test gate** (template lookup — see the [E2B Templates doc](./e2b-templates.md))

If the answer is wrong, **every downstream system inherits the lie**. A FastAPI task misclassified as `PURE_CODE` gets generic boilerplate from the prompt generator, a generic reviewer from the eval critics, and no template from the gate. The cost compounds across the four consumers.

### The old broken state

A rule-based classifier (`prompt_generator/classifier.py`) was answering this question by walking token lists and applying hand-coded `if` branches. It had three structural failure modes:

**Failure A — framework-without-database structural bug.** The `_has_backend_language()` check required `backend-token AND NOT framework-token`. For `Python - FastAPI`, both matched, so the function returned `False`, and every branch fell through to the `PURE_CODE` default. 9 FastAPI tasks, 11 Laravel tasks, 3+ Spring Boot tasks all landed in `PURE_CODE`.

**Failure B — missing tokens for entire languages.** Flutter, Dart, Scala, Playwright, React Native, MERN — none of these appeared in any token list. Every task using them defaulted to `PURE_CODE`.

**Failure C — wrong branch on edge cases.** Go is in `_BACKEND_LANG_TOKENS` but not `_WEB_APP_LANG_TOKENS`. So `Golang + Redis` landed in `SCRIPT_AND_DB` instead of `APP_AND_DB`. Wrong template, wrong eval persona.

**The data.** Re-classified all 339 rows of the dev `tasks` table:

```
pure_code               183     ← the "default" bucket (54%)
frontend                 46
app_and_db               37
non_code                 17
db_only                  12
llm_framework            11
messaging                10
containerized_app         9
microservices             6
vector_db                 5
script_and_db             3
```

**183 of 339 tasks (54%) landed in PURE_CODE** — the "I dunno" default. Of those 183, the vast majority were genuine apps, scripts, or mobile tasks the classifier just couldn't recognise.

### Why rules can't be saved

- **Token lists go stale.** Every time new tech emerges (Elixir, Mojo, Bun, Phoenix LiveView), someone has to remember to update the token list. The LLM doesn't — its training data is current.
- **Substring matching has false positives.** `"rust"` substring-matches `"trusted"`. `"go"` substring-matches `"mongo"`. Maintaining substring tokens is fighting your own pattern.
- **Bugs are emergent from rule complexity.** The framework-no-DB bug wasn't there by intent — it emerged from the interaction of three independent `if` branches. Removing rules removes that whole *category* of bug.

---

## Solution: LLM classifier with Supabase registry

One Sonnet call per unique competency combo, ever. The result is stored in a Supabase **classification registry** keyed by the sorted competency set. Every consumer reads from the registry directly; on a miss (no row yet) we call the LLM and insert one.

```
                competencies (list of name + proficiency)
                          │
                          ▼
         ┌────────────────────────────────────┐
         │ combo_key = make_combo_key(...)    │
         └────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │ SELECT … FROM                       │
         │   competency_combo_classification   │
         │   WHERE combo_key = ?               │
         └────────────────────────────────────┘
                          │
              HIT         │         MISS
                          ▼
                   TaskRuntime
                   (~10 ms, $0)
                          │
                          │  MISS path:
                          ▼
         ┌────────────────────────────────────┐
         │ classify_with_llm(competencies)    │  ~2 s, ~$0.001
         │   • Sonnet via Portkey             │
         │   • strict Pydantic schema         │
         │   • retry once with ValidationError │
         │     fed back to the model          │
         └─────────────────┬──────────────────┘
                          ▼
         ┌────────────────────────────────────┐
         │ UPSERT competency_combo_classification│
         │   classifier_version, confidence    │
         └─────────────────┬──────────────────┘
                          ▼
                   TaskRuntime
```

**Economics.** ~50 unique competency combos across 339 dev tasks → ~50 LLM calls ever → **~$0.05 to populate the registry**. After that, every consumer reads a column. Latency: ~10 ms when the row already exists vs ~2 s on first encounter. Misses only happen at task-generation time, never on a user-facing hot path.

**Determinism.** Same input → same output, because the read path is a column lookup. The "LLM is non-deterministic" objection doesn't survive once a row exists — the LLM is only consulted on first encounter.

**Override path.** Edit the row in Supabase. Every consumer reads the registry directly, so the corrected row is authoritative — no code change needed when the LLM hallucinates once.

### Why no rules layer at all

Earlier drafts proposed rules-first with LLM fallback. The trade-off doesn't favour rules at our scale:

| Concern | Rules answer | LLM-only answer |
|---|---|---|
| New tech emerges weekly | Manual token-list updates | Auto-handled by training data currency |
| Substring false positives | Constant fighting | Doesn't exist (LLM judges meaning) |
| Bug surface | Emergent from rule complexity | Bounded — one prompt, one parser |
| Latency | ~5 ms | ~2 s — but only on first encounter |
| Cost | $0 forever | ~$0.05 once, then $0 |
| Determinism | Yes | Yes via the registry |

The latency argument is the only one rules win on, and it only matters on the first sight of a new combo (task-generation time, not user-facing).

---

## The `TaskRuntime` model

### Current shape (shipped)

[`infra/classifier/runtime.py`](../../infra/classifier/runtime.py):

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Runtime = Literal[
    "python", "node", "java", "php", "go", "rust",
    "flutter", "ruby", "scala", "none",
]
Kind = Literal[
    "app", "script", "mobile", "frontend", "testing",
    "db_only", "llm", "vector_db", "non_code",
]

class TaskRuntime(BaseModel):
    model_config = ConfigDict(frozen=True)
    runtime:       Runtime
    frameworks:    list[str] = Field(default_factory=list)
    datastores:    list[str] = Field(default_factory=list)
    messaging:     list[str] = Field(default_factory=list)
    needs_browser: bool = False
    kind:          Kind
```

The `kind` enum carries two different things:

| `Kind` value | What it really describes |
|---|---|
| `app`, `script`, `mobile`, `frontend`, `testing`, `non_code` | **Shape of output** — what files/structure the task ships |
| `db_only`, `llm`, `vector_db` | **Specialty** — which reviewer persona should evaluate it |

A `kind="app"` is a *shape* (HTTP service + tests + maybe compose). A `kind="vector_db"` is a *specialty* (the reviewer should focus on dimensionality, distance metric, recall@k). They're not at the same level of description. This shows up as disambiguation pain at classification time:

| Task | Could plausibly be |
|---|---|
| "Pinecone + REST API for similarity search" | `kind="app"` (it's a backend app) **or** `kind="vector_db"` (vector specialty) |
| "RAG pipeline with Chroma" | `kind="llm"` (RAG) **or** `kind="vector_db"` (Chroma-specific) |
| "pgvector schema design" | `kind="db_only"` (schema) **or** `kind="vector_db"` (vector specifics) |

The LLM has to pick *one*, but both are true.

### Proposed evolution — split `kind` into `shape` + `specialty`

```python
Shape = Literal[
    "app", "script", "mobile", "frontend", "testing",
    "non_code", "infra",   # ← "infra" is also new (K8s, Helm, Terraform)
]
Specialty = Literal[
    "backend", "frontend", "data", "dba", "llm",
    "vector_db", "mle", "sdet", "none",
]

class TaskRuntime(BaseModel):
    model_config = ConfigDict(frozen=True)
    runtime:       Runtime
    shape:         Shape       # ← what files/structure
    specialty:     Specialty = "none"   # ← which reviewer persona
    frameworks:    list[str] = Field(default_factory=list)
    datastores:    list[str] = Field(default_factory=list)
    messaging:     list[str] = Field(default_factory=list)
    needs_browser: bool = False
```

Now the disambiguation cases resolve cleanly:

| Task | Shape | Specialty |
|---|---|---|
| "Pinecone + REST API for similarity search" | `app` | `vector_db` |
| "RAG pipeline with Chroma" | `app` | `llm` |
| "pgvector schema design" | `non_code` (or `infra`) | `dba` |
| "Plain FastAPI + Postgres CRUD" | `app` | `backend` |
| "Build a Helm chart for a microservice" | `infra` | `backend` |
| "Pure SQL schema design" | `non_code` | `dba` |
| "Flutter mobile app" | `mobile` | `none` |

Concretely, what each consumer reads changes:

| Consumer | Today reads | Proposed reads |
|---|---|---|
| Prompt generator HARD CONSTRAINT block | `kind` | `shape` |
| Reference retriever filename matching | `kind` + `datastores` + `needs_browser` | `shape` + same |
| Eval critic persona routing | `kind` | `specialty` (with `shape` as fallback when `specialty="none"`) |
| E2B template picker | `runtime` (+ small `kind` checks) | `runtime` + `shape` |

**Migration path.** When this lands:
1. Add both columns to `competency_combo_classification` (NULL-able initially).
2. Update the LLM system prompt to emit both fields.
3. Re-classify the existing rows (~50 LLM calls, ~$0.05).
4. Update consumers one at a time, defaulting to the legacy `kind` until each is migrated.
5. Once all four consumers are migrated, drop `kind`.

**Why defer it.** At ~50 combos and one functioning persona-routing flow today, the cost of disambiguation pain is small. Ship this split when:
- You add `kind="infra"` (K8s / Helm / Terraform tasks become common enough to need a reviewer persona)
- You have ≥3 tasks where the kind/specialty conflict caused a wrong reviewer choice
- You're already touching the schema for an unrelated reason

Until then the single-field `kind` carries both axes at the cost of occasional ambiguity.

---

## Stress-testing the model — where `TaskRuntime` breaks

The shape/specialty split fixes one ambiguity (`kind="vector_db"`). It does **not** fix the structural rigidity. Running concrete tasks through the current model reveals a deeper pattern: closed enums keep collapsing axes that are genuinely orthogonal.

### Eight cases that exercise the model

| # | Task | Current model says | What actually breaks |
|---|---|---|---|
| **A** | Helm chart for a microservice | `runtime=none` (or `python`?), no `kind` fits | No `shape="infra"`. No template (`utkrusht-infra`). No eval recipe (`helm lint`, `kubectl --dry-run`). Gate skips, no quality signal. |
| **B** | Rust backend + React frontend (polyglot monorepo) | `runtime=rust` OR `runtime=node` — must pick one | Template picker boots only one runtime's sandbox. The other half of the task can't build or test. Eval persona is ambiguous. |
| **C** | MySQL → Postgres data migration | `datastores=[mysql, postgres]` | Flat list erases that mysql is the *source* (read-only) and postgres is the *target* (write). Eval can't verify directionality. |
| **D** | Analyze a dataset in a Jupyter notebook | `shape=script`? `non_code`? None fit | `pytest` is the wrong eval. Notebooks need `papermill` / `nbclient`. No template variant for notebook execution. |
| **E** | Train a sentiment classifier in PyTorch | `runtime=python`, `specialty=mle` (if shipped) | No `resources` field for GPU. Eval shape is wrong — train-to-convergence isn't a test suite. |
| **F** | Solana smart contract in Anchor (Rust) | `runtime=rust`, `frameworks=[anchor]` | `utkrusht-rust` has no `solana-test-validator`. The classifier output looks reasonable but the template fundamentally can't run the tests. `specialty="blockchain"` not in proposed enum. |
| **G** | gRPC payments service in Go | `runtime=go`, `frameworks=[grpc]` | Wire protocol (gRPC vs REST vs GraphQL vs WebSocket) is implicit in `frameworks`. Prompt generator can't reliably emit a `.proto` file + `protoc` step. |
| **H** | Postgres primary + read replica routing | `datastores=[postgres]` | Two role-distinct datastores collapse into one entry. Eval can't verify "writes to primary, reads to replica." |

### The pattern — closed enum collapses orthogonal axes

Every failure is the same shape: a single field is forced to carry information about multiple independent dimensions.

| Axis that needs to exist | Currently squashed into | Cases affected |
|---|---|---|
| Multi-runtime (polyglot) | `runtime: Runtime` (single literal) | B |
| Shape vs specialty | `kind` (already known) | A, D, E, F |
| Datastore role (source/target/replica/cache) | `datastores: list[str]` | C, H |
| Wire protocol (REST/gRPC/GraphQL/WS) | implicit in `frameworks` | G |
| Resource needs (GPU/RAM/time) | not expressible | E |
| Eval method (pytest/notebook/validator/lint/benchmark) | implicit from `runtime` | D, E, F |
| Long-tail runtimes (C++/C#/Kotlin/Swift/R/Julia/shell/yaml) | closed `Runtime` enum | not in cases above, but real |

The rigidity isn't inherently wrong — it's correct *as long as the downstream consumers are also bounded*. We have ~9 templates, ~5 eval personas, ~4 prompt-generator branches. The schema mirrors that. But every time a new consumer or task type lands with finer-grained needs, the schema cracks.

### Recommended schema changes

Don't open up everything. Open up *exactly* the axes that already broke, with closed enums (so type-checking still catches typos):

1. **`runtimes: list[Runtime]` (rename plural).** Picker uses the first for template choice; full list goes to eval persona + prompt generator. Solves Case B.
2. **Ship the shape/specialty split** (already proposed). Adds `shape="infra"` for K8s/Terraform/Helm. Adds `specialty="mle" | "dba" | "blockchain" | "security" | "devops"`. Solves A, D (partial), E, F.
3. **`datastores: list[{name: str, role: Literal["primary","replica","source","target","cache"]}]`**. Solves C and H.
4. **`protocols: list[Literal["rest","grpc","graphql","websocket","none"]]`**. Solves G.
5. **`eval_method: Literal["pytest","notebook","validator","lint","benchmark","compile_only"]`** with defaults by runtime. Solves D, E, and the "what does the gate actually run?" question for special-case templates.
6. **Hold the line on `Runtime`.** Don't add C++/C#/Kotlin/Swift until there's a real template behind each. Otherwise the gate quietly skips and we've added noise. The enum *should* track "what we can actually run."

Two things to explicitly *not* do:

- **No `tags: list[str]`.** Loses type safety; every consumer becomes a string-parsing pile. The current closed-enum-per-axis is right; we just have too few axes.
- **No `resources` field yet.** No consumer reads GPU/memory/time today. Add when E2B template variants actually offer them.

### Superset model proposal — one rich shape, consumer projections

A second question: should we keep one `TaskRuntime` model that everyone reads, or split into a rich superset + consumer-specific projections?

**Option A — keep one model (current).**
```python
class TaskRuntime(BaseModel):
    runtimes: list[Runtime]
    shape: Shape
    specialty: Specialty
    datastores: list[DatastoreRef]
    protocols: list[Protocol]
    frameworks: list[str]
    messaging: list[str]
    needs_browser: bool
    eval_method: EvalMethod
```
Every consumer reads the whole thing; ignores fields it doesn't need.

**Option B — superset + projections.**
```python
class TaskRuntime(BaseModel):   # source of truth; the LLM emits this
    # all of the above, plus freeform notes the LLM wants to surface
    notes: str = ""

class TemplateRequest(BaseModel):    # projection for the template picker
    runtime: Runtime
    shape: Shape
    needs_browser: bool

class EvalContext(BaseModel):        # projection for persona routing
    shape: Shape
    specialty: Specialty
    eval_method: EvalMethod

class PromptContext(BaseModel):      # projection for the prompt generator
    runtimes: list[Runtime]
    frameworks: list[str]
    datastores: list[DatastoreRef]
    protocols: list[Protocol]
```
The classifier always emits the rich superset; each consumer constructs the projection it actually wants.

**My honest take: Option A for now, B when forced.**

Option B looks clean on paper but pays a cost: more types, more conversion code, more places to keep in sync. The argument for it kicks in when *consumers genuinely diverge*. Today they mostly read overlapping subsets — the template picker reads `runtime` + a tiny bit of shape, the eval persona reads `shape` + `specialty`, the prompt generator reads almost everything. There's no point projecting "almost everything" through a separate type.

When to flip to B:
- A 5th or 6th consumer lands with a genuinely different read pattern (e.g. a deployment-cost estimator that only needs `resources`).
- The model grows past ~10 fields and consumers start picking very different subsets.
- A consumer needs to *mutate or augment* the model (today none do — everything is read-only).

Until then, one model with field-level optionality (some fields with sensible defaults, most consumers ignoring most fields) is cheaper and equally honest.

### Template implications — polyglot is composition's real argument

The fat-vs-composition discussion in the templates doc recommends *fat templates* because image size doesn't affect cold-start latency. That stands — for single-runtime tasks. But Case B (polyglot) is where composition has a unique payoff the fat argument missed:

- Baking Rust + Node + Python + Java into one fat image is *not* like baking Python's fastapi/django/flask into one image. It's adding entire SDKs whose dependencies don't overlap and conflict-spaces don't simplify.
- A monorepo with Rust backend + React frontend genuinely needs both `cargo` and `npm` in the sandbox.
- E2B's `from_template()` is **single-parent inheritance** (like Docker `FROM`) — you can't chain multiple parents to build "Rust + Node = polyglot." That rules out the cleanest version of composition.

That leaves three viable shapes for polyglot:
1. **Dedicated polyglot templates** for common pairs (`utkrusht-node-python` for typical web stacks, `utkrusht-rust-node` for backend+frontend). Built fat, but with multiple runtimes. Costs disk; honest about the use case.
2. **Pick a primary runtime; install the secondary at runtime.** Slow (defeats the "no pip/npm at boot" rule) but uses existing single-runtime templates. Acceptable for rare polyglot.
3. **Skip the gate for polyglot** until the pair becomes common. Concretely: when `len(runtimes) > 1`, classifier writes a row, template_runtime stays NULL, gate skips with `polyglot_skipped`. Lossy but visible.

**Recommendation:** option 3 short-term (it's visible and honest), option 1 only when a specific polyglot pair recurs ≥3 times. Don't preemptively build `utkrusht-node-python` until at least three tasks need it. The classifier change (`runtimes: list[Runtime]`) is what unlocks the *data* to drive that decision later — without it, we can't even count how often polyglot is asked for.

### Status of this section

| Idea | Status | Trigger to revisit |
|---|---|---|
| Shape/specialty split | Proposed (above) | `kind="infra"` or ≥3 misrouted reviewers |
| `runtimes: list[Runtime]` | Proposed (this section) | First polyglot task that gets skipped |
| `datastores` with role | Proposed (this section) | First migration / replica task in the wild |
| `protocols` field | Proposed (this section) | First gRPC / GraphQL task needing a different prompt branch |
| `eval_method` field | Proposed (this section) | First notebook / benchmark / infra task that needs non-pytest eval |
| Superset + projections | Deferred | 5+ consumers OR model >10 fields |
| Polyglot templates | Deferred | ≥3 tasks asking for the same runtime pair |

The model isn't rigid in the *bad* sense (over-specified). It's rigid in the *underdimensioned* sense — too few axes, each axis nearly correct. The fix is **more axes, not looser axes**.

---

## Proposed evolution: merge `TaskRuntime` and `template_registry` into one decision

### The structural alternative to "more axes"

The section above concludes: the model is *underdimensioned* and the fix is *more axes*. There's a second answer that doesn't add fields at all — **collapse the classifier output and the template registry into a single decision surface**.

The current two-table shape encodes a conceptual seam:

```
                  classifier emits             picker resolves
competencies ──► TaskRuntime ───────────────► template_id
                  (runtime + frameworks +     (template_registry lookup
                   datastores + needs_browser  keyed on runtime)
                   + kind)
```

Two LLM-readable surfaces (the prompt's enums + the registry's templates), two PKs (`runtime`, `combo_key`), two places to keep aligned. The seam is where bugs of the "classifier said `node`, but `utkrusht-node` doesn't exist" shape live — and where shell / Terraform / infra tasks fall through silently today.

The alternative collapses that to:

```
                                                LLM reads capability sheets
competencies ─────────────────────────────────► picks template_id (+ persona)
                                                OR returns structured no_match
```

The classifier's job is *only* to match a task against the deployable set. The template registry rows ARE the capability sheets the classifier reads — the registry stops being a downstream lookup and becomes the classifier's input.

### Why this is structurally better

1. **One place knows what we can run.** Today the `Runtime` Literal in `infra/classifier/runtime.py` says we support `python | node | java | ...`, while `template_registry.status` says only `python` is actually built. Both are versions of the same fact, maintained separately. With the merged model, the rows are the truth — the LLM literally can't return a runtime we don't deploy.

2. **"No template fits" becomes a first-class signal.** Today an infra / shell / Terraform task hits the rule-based picker, the picker falls through, the gate skips with `no_template`, and nobody notices. With the merged model the LLM returns `match: null, missing_capabilities: ["terraform-cli","tflint"], suggested_template: "utkrusht-infra"` — a build-new-template ticket generated automatically the first time a task needs it.

3. **Adding a template is a row insert, not an enum bump.** The closed `Runtime` enum is a deliberate gate today, but accumulates as a graveyard (you can't remove old values that cached rows reference). Capability sheets carry that information instead — open at the edges, validated at consumption.

4. **The shape/specialty split becomes moot.** "Shape" is implied by the template (an `utkrusht-infra` task is by construction an infra-shape task). "Specialty / persona" lives on the template as a `personas: text[]` column; the LLM picks one per task. The proposal earlier in this doc to split `kind` into `shape` + `specialty` is resolved structurally rather than by adding more fields.

5. **Polyglot is honest about what it is.** A polyglot task with no matching template surfaces as `no_match`, not as a silent runtime collision. Build-or-skip becomes data-driven.

### The proposed schema

Same row count as today — but the seam moves to a useful place.

```sql
-- templates: the registry IS the capability sheet
CREATE TABLE templates (
  template_id        text PRIMARY KEY,        -- "utkrusht-python", "utkrusht-node-playwright"
  status             text NOT NULL,           -- "built" | "proposed" | "deprecated"

  -- Capability sheet (what the LLM reads to match)
  runtime            text NOT NULL,           -- "python3.12" - primary language/VM
  language_versions  jsonb DEFAULT '{}',      -- {"node":"20.11","python":"3.12"}
  frameworks         text[] DEFAULT '{}',     -- ["fastapi","sqlalchemy"]
  datastores         text[] DEFAULT '{}',     -- ["postgresql-16","redis-7"]
  tools              text[] DEFAULT '{}',     -- ["pytest","ruff","docker","helm"]
  needs_browser      boolean DEFAULT false,
  needs_gpu          boolean DEFAULT false,
  capabilities_note  text,                    -- free-form for anything the structured fields miss

  -- Personas this template can host (list, not scalar — one image serves multiple personas)
  personas           text[] NOT NULL,         -- ["backend","data","mle"]

  -- Execution
  build_cmd          text NOT NULL,
  test_cmd           text NOT NULL,
  compile_cmd        text,

  -- Drift control: load-bearing for year-2 durability
  manifest_hash      text NOT NULL,           -- sha256 of source Dockerfile/manifest
  generated_at       timestamptz NOT NULL,    -- when sheet was last regenerated from manifest
  registry_version   integer NOT NULL         -- monotonic; bumps on any sheet change
);

CREATE INDEX templates_active_idx ON templates(status) WHERE status = 'built';

-- task_template_match: the classification cache, now pointing at templates
CREATE TABLE task_template_match (
  combo_key             text PRIMARY KEY,
  template_id           text REFERENCES templates(template_id), -- NULL = no_match
  persona               text NOT NULL,                          -- one of template.personas
  confidence            real,

  -- no_match path: first-class signal, not a silent skip
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

A cache hit requires `classifier_model = current AND registry_version = current_registry_version`. Stale entries get re-classified automatically when either bumps.

### Contrast — same row count, better seam

| Concern | Current (two tables) | Merged (two tables) |
|---|---|---|
| Primary entity | `runtime` enum | `template_id` row set |
| Adding new tech | Enum bump + code PR + migration + registry row | One row insert |
| Adding a template variant (e.g. `python-ml`) | Awkward — `runtime` PK blocks it | Natural — second row |
| "What's in this template?" | Implicit in `template_name` string | Explicit in capability columns |
| Reviewer persona | `kind` (scalar, conflated with shape) | `personas[]` on template; one picked per task |
| Picker logic | `if/else` on runtime / kind / frameworks (growing) | LLM reads capability sheets |
| "No template fits" | Silent `no_template` skip | Structured `missing_capabilities` + suggested name |
| Cache staleness on template change | Not modeled | `registry_version` bump invalidates |
| Cache staleness on model upgrade | Implicit | `classifier_model` in cache key, explicit policy |
| Drift between sheet and reality | N/A — no sheet | `manifest_hash` + CI check |

### The load-bearing decision — sheets are generated, not hand-written

The merged model has one architectural weak point: **the sheet can lie about the image**. Someone bumps the Dockerfile (Node 20 → 22, adds `redis-cli`) but forgets the row. The classifier picks based on stale info.

The fix: sheets are *generated*, not hand-maintained.

- Each template's Dockerfile (or `e2b_flow/templates/<name>/template.py`) emits a manifest at build time.
- The manifest is hashed → `manifest_hash` column.
- CI gate: "Dockerfile changed but sheet wasn't regenerated → fail build."
- Bumping the row bumps `registry_version`, invalidating cached classifications.

Without this discipline the merged model rots in year 2. With it, sheets can't lie and the cache-invalidation story is clean. **This is the single decision that determines whether the merged model is sound at year 2.** If the team isn't ready to invest in manifest generation, stay on the two-layer model — the rule-based picker survives lying data better than an LLM does.

### Template fragmentation policy

`utkrusht-python` is fat by design today. As task volume grows, real splits will be needed (e.g. `utkrusht-python-nlp` once pandas + transformers become heavy enough to bake separately; later `utkrusht-python-llm` for the LangChain / LlamaIndex lane). The split decision should be signal-driven, not speculative.

**Signals that justify a split:**
1. **Base image bloat** — build time on the base past some threshold (~60 s) or image size past some MB. CI metric.
2. **Over-serving** — most tasks routed to the base also pull `pandas` / `transformers` / `langchain` at install time. The `build_cmd` is "install X" over and over per sandbox. Bake X into a sibling template.
3. **No-match clustering** — multiple `no_match` rows with the same `missing_capabilities`. Five no-matches in a month asking for `["torch","transformers"]` is a `utkrusht-python-llm` ticket.

Signal (3) is what the merged model gives you for free — the highest-signal source of "what template to build next," generated automatically rather than guessed at by humans.

**Sprawl avoidance — the equally-important policy:**
- Capability sheets must be *distinctive*. Two templates with 90 % overlap confuse the LLM matcher. That's the signal to merge them, or to make the sheet sharper.
- `status = "deprecated"` is for templates we've replaced; rows stay (cache validity) but the LLM stops picking them.
- Every CVE patch is N rebuilds — keep N small. ~12 templates at the two-year mark is reasonable; 30 is sprawling.

**Inheritance vs siblings.** When `utkrusht-python` splits, the variants should be **siblings** (each `FROM` a common base image), not E2B `from_template()` inheritance. Inheritance feels DRY but makes rebuild graphs ugly and CVE patching cascades. Siblings duplicate a small amount and are independently buildable / patchable.

### How the two designs age

**Two-layer model (current).** Fails worst on *closed-vocab drift*. Bun ships, the LLM emits `runtime=node, frameworks=['bun']` because Bun isn't in the enum, the picker routes to the Node template, Bun-specific behaviour fails subtly. By the time someone debugs it, three months have passed. This is the canonical failure mode of closed-vocab classification in a fast-moving domain — and the tech-stack-for-assessments domain is fast-moving.

**Merged model.** Fails worst on *sheet ambiguity*. The LLM picks `utkrusht-python` for a task that wanted `utkrusht-python-llm` because the LLM-libs distinction wasn't sharp in the sheet. Surfaces in eval failure; fix is to sharpen the sheet (one row update). Louder failure mode, faster feedback loop.

Closed-vocab drift compounds silently. Sheet ambiguity is loud. The merged model fails *better* over years — but only with the manifest-hash discipline above.

### Migration path

1. **Add `personas: text[]` to `template_registry`** (additive; defaults `[]`). Cheap.
2. **Add `manifest_hash`, `generated_at`, `registry_version`** columns. Backfill from existing rows. Cheap.
3. **Build the manifest-emitting CI step.** Each template's `build_prod.py` writes a manifest JSON; CI hashes it and compares to the row. **This is the durability gate** — don't merge classifier and registry without it.
4. **Extend the classifier system prompt** to receive the active template rows (only `status='built'`) and return `template_id` + `persona` (or structured `no_match`). The current `TaskRuntime` keeps existing — it becomes a projection derivable from the picked template.
5. **Wire the `no_match` path.** Rows with `template_id IS NULL` log a structured ticket. After a few weeks, the most common `missing_capabilities` is the template roadmap.
6. **Once stable, drop the `Runtime` Literal enum.** Now redundant with the templates table. Irreversible step; do it after at least one new template has landed via the new path.

Existing `competency_combo_classification` rows become the seed for `task_template_match` — same `combo_key`, derived `template_id` via the current picker, `registry_version = 1`.

### Status of this proposal

| Idea | Status | Trigger to ship |
|---|---|---|
| `personas: text[]` on template | **Proposed** | Whenever persona-routing next needs to handle a template serving multiple personas (already true of `utkrusht-python`) |
| `manifest_hash` + CI sheet-from-Dockerfile check | **Proposed — required for full merge** | Before adding the second built template; this is the durability gate |
| First-class `no_match` output | **Proposed** | First infra / shell / Terraform task that surfaces the gap |
| Full merge — LLM picks `template_id` directly | **Proposed** | When (a) the second built template lands, or (b) ≥3 "wrong runtime" misclassifications in a quarter |
| Sibling-template fragmentation of `utkrusht-python` | **Deferred** | When build-time, image-size, or no-match clustering signals fire (see "Template fragmentation policy" above) |

The shape/specialty split proposed earlier in this doc remains valid as an intermediate move *if* the full merge is deferred. If the merge ships, the split becomes structurally unnecessary — shape comes from the template, specialty from the picked persona.

---

## The classification registry — `competency_combo_classification` (B1)

Schema:

| column | type | role |
|---|---|---|
| `combo_key` | `text` PK | e.g. `"FastAPI (INTERMEDIATE), Python (INTERMEDIATE)"` — sorted, proficiency-suffixed |
| `runtime`, `kind` | `text` | the classifier's verdict |
| `frameworks`, `datastores`, `messaging` | `text[]` | structured `TaskRuntime` fields |
| `needs_browser` | `bool` | for Playwright/Selenium |
| `template_runtime` | `text` FK → `template_registry(runtime)` | which template to boot; `NULL` when no template seeded yet |
| `classifier_version` | `text` | bump when the LLM prompt/model changes; old rows can be re-classified |
| `confidence` | `numeric(3,2)` | rows `< 0.7` surface for human review |

**One row per `combo_key`. No `organization_id`** — the classifier output for a given competency set is platform-global (e.g. "Python + FastAPI + Postgres" is always `kind=app, runtime=python, frameworks=[fastapi], datastores=[postgres]`, regardless of which org is using it). Earlier versions had `organization_id NOT NULL`; that was over-applied multi-tenancy and was reverted on 2026-05-26.

**combo_key** is built by `make_combo_key()` — sorts competencies by name, suffixes each with its proficiency. The same competency set always hashes to the same key regardless of input order.

---

## How `resolve_plan` uses the registry

[`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py):

```
combo_key = make_combo_key(competencies)
                ▼
  SELECT runtime, kind, frameworks, datastores, messaging, needs_browser
    FROM competency_combo_classification
   WHERE combo_key = ?
                ▼
   ┌─── HIT  → return ResolvedPlan(
   │             TaskRuntime(from row),
   │             template = _get_template(runtime)
   │           )                                       (~10 ms, $0)
   │
   └─── MISS → classify_with_llm(competencies)         (~2 s, ~$0.001)
                ▼
              UPSERT competency_combo_classification (
                  combo_key,
                  runtime, kind, frameworks, datastores, messaging, needs_browser,
                  template_runtime,           -- FK; NULL if no template seeded
                  classifier_version='v1',
                  confidence
              )
                ▼
              return ResolvedPlan(new TaskRuntime, template)
```

Never raises. Failure modes degrade gracefully (see below).

---

## Who reads `ResolvedPlan`

| Consumer | Field used | Effect |
|---|---|---|
| `multiagent.py:create_task` | `plan.kind` | persona-routed eval critics (DBA / MLE / SDET / …) |
| `multiagent.py:create_task` | `plan.template.name` | E2B build/test gate template id |
| `generators/prompts/agent.py:step1` | `plan.task_runtime` | DSPy InputFields + HARD CONSTRAINT block |
| `e2b_flow/sandbox_eval.py` | `template_name_for_runtime(plan.runtime)` | sandbox boot |

Every consumer goes through `resolve_plan`. There is no longer a second classification site anywhere in the codebase.

---

## Failure modes — graceful degradation

| Failure | Behaviour |
|---|---|
| Supabase unreachable at registry-lookup time | Warn, fall through to direct LLM call (no insert this call) |
| Supabase upsert fails at registry-write time | Warn, return the resolved plan anyway; next call re-classifies |
| `SUPABASE_URL_APTITUDETESTSDEV` / `SUPABASE_API_KEY_APTITUDETESTSDEV` env vars missing | Skip the registry entirely, plain LLM path (used in unit tests via `supabase=None` + patched `_build_supabase_client`) |
| LLM classifier raises after retry | Return empty `ResolvedPlan` — callers skip persona routing and the gate, never crash |
| `template_runtime` not yet in `template_registry` | Stored as `NULL` (FK respected); the gate skips with `no_template` |
| API role missing `GRANT` on the table | `permission denied for table` warning, same fall-through as Supabase-down — needs the GRANT migration applied |

The principle: **classifier failures never block task generation.** A task without a classification just gets the generic eval critic and skips the build/test gate — exactly the prior behaviour before classification existed.

---

## Bootstrap — migrations to apply (in order)

| # | File | What it does |
|---|---|---|
| 1 | [`2026-05-25-create-template-registry.sql`](../../migrations/2026-05-25-create-template-registry.sql) | Creates the template registry that the classification registry's FK references (see [E2B Templates doc](./e2b-templates.md)) |
| 2 | [`2026-05-25-create-competency-combo-classification.sql`](../../migrations/2026-05-25-create-competency-combo-classification.sql) | Creates the classification registry with FK to (1) |
| 3 | [`2026-05-25-grant-cache-tables.sql`](../../migrations/2026-05-25-grant-cache-tables.sql) | Grants `SELECT/INSERT/UPDATE/DELETE` to `anon`, `authenticated`, `service_role`. **Without this the registry silently fails on every call.** Tables created in the SQL editor default to `postgres`-only ownership. |
| 4 | [`2026-05-26-classification-drop-org-id.sql`](../../migrations/2026-05-26-classification-drop-org-id.sql) | Drops the `organization_id` column (over-applied multi-tenancy — classifications are platform-global). Safe against empty dev table. |

---

## Implementation status (2026-05-26)

| Component | Status | Where |
|---|---|---|
| `TaskRuntime` Pydantic model (replaces `TaskCategory` enum) | **Shipped** | [`infra/classifier/runtime.py`](../../infra/classifier/runtime.py) |
| LLM classifier (Sonnet via Portkey, strict JSON, retry-with-validation-error) | **Shipped** | [`infra/classifier/llm_classifier.py`](../../infra/classifier/llm_classifier.py) |
| `tasks.task_runtime` JSONB column (write-only first attempt) | **Dropped** — replaced by the classification registry | [migration](../../migrations/2026-05-22-drop-task-runtime-column.sql) |
| `competency_combo_classification` classification registry (B1) | **Shipped** — migration + Python read/write | [migration](../../migrations/2026-05-25-create-competency-combo-classification.sql) |
| `resolve_plan(combo_key)` — single registry-aware entry point | **Shipped** | [`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) |
| `generators/prompts/agent.py` routes through `resolve_plan` | **Shipped** — no more double classification | — |
| `e2b_flow/sandbox_eval.py` shares the template registry via `template_name_for_runtime` | **Shipped** — no more local copy | — |
| Persona-routed eval critics keyed off `TaskRuntime.kind` | **Shipped** | [`evals.py`](../../evals.py) |
| `organization_id` on classifier tables | **Reverted (2026-05-26)** — over-applied multi-tenancy | [migration](../../migrations/2026-05-26-classification-drop-org-id.sql) |
| Shape + specialty split in `TaskRuntime` | **Proposed** — see "Stress-testing the model" above | — |
| Merged classifier ↔ template-registry decision (LLM picks `template_id` directly) | **Proposed** — see "Proposed evolution: merge `TaskRuntime` and `template_registry`" above | — |
| `personas: text[]` on template rows | **Proposed** — prerequisite for the merge | — |
| Manifest-hash sheet-from-Dockerfile CI gate | **Proposed** — durability gate for the merge | — |
| First-class `no_match` output (missing_capabilities + suggested_template) | **Proposed** — value-driver for the merge | — |
| `classifier_version` re-classification tooling (backfill script) | **Proposed** | — |

---

## What we should do next

1. **Apply the four migrations** above to dev (and then prod) — currently all created, pending application.
2. **Wire `sandbox_eval` to read commands from `template_registry`** — today the build / test / compile commands are hardcoded in `sandbox_eval.py`; the registry stores the same values but isn't read at runtime. See the [E2B Templates doc](./e2b-templates.md) for the full discussion. *(This is also the smallest change that validates the registry pattern before the merge proposal below lands.)*
3. **Decide on the merged-model direction.** The "Proposed evolution" section above lays out the merge of `TaskRuntime` and `template_registry` into one decision surface. The blocking prerequisite is **manifest-hash + CI sheet-from-Dockerfile generation** — without that the merged model rots within a year. If the team isn't ready to invest in manifest generation, defer the merge and ship the shape+specialty split instead.
4. **Defer the shape + specialty split** until either (a) `kind="infra"` becomes a real need, (b) ≥3 ambiguous classifications cause wrong reviewer routing, (c) you're touching the schema for an unrelated reason, or (d) the merged-model proposal lands (in which case the split becomes structurally unnecessary).
5. **Optionally backfill** the registry from the existing 339 tasks (one script call, ~$0.05, surfaces low-confidence combos for review *before* they affect real generation). Currently the table is empty — populates organically as tasks are generated.
