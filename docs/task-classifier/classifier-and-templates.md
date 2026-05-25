# Task Classifier & E2B Template Strategy

> **Status:** Partially shipped — design + first cache layer implemented (2026-05-25).
> **Original design date:** 2026-05-20.
> Sister doc to [task-eval-optimizer](./task-eval-optimizer/task-eval-optimizer.md).

## Implementation status (2026-05-25)

| Component | Status | Where |
|---|---|---|
| `TaskRuntime` Pydantic model (replaces `TaskCategory` enum) | **Shipped** | [`prompt_generator/runtime.py`](../../prompt_generator/runtime.py) |
| LLM classifier (Sonnet via Portkey, strict JSON, retry-with-validation-error) | **Shipped** | [`prompt_generator/llm_classifier.py`](../../prompt_generator/llm_classifier.py) |
| `tasks.task_runtime` JSONB column (write-only first attempt) | **Dropped** — replaced by combo cache | [migration](../../migrations/2026-05-22-drop-task-runtime-column.sql) |
| `competency_combo_classification` cache table (B1) | **Shipped** — migration + Python read/write | [migration](../../migrations/2026-05-25-create-competency-combo-classification.sql) |
| `template_registry` table (B6) | **Shipped** — migration + python seed row | [migration](../../migrations/2026-05-25-create-template-registry.sql) |
| `resolve_plan(combo_key)` — single cache-aware entry point | **Shipped** | [`task_generation/runtime_resolver.py`](../../task_generation/runtime_resolver.py) |
| `prompt_generator/agent.py` routes through `resolve_plan` | **Shipped** — no more double classification | [agent.py:386](../../prompt_generator/agent.py#L386) |
| `e2b_flow/sandbox_eval.py` shares the template registry via `template_name_for_runtime` | **Shipped** — no more local copy | [sandbox_eval.py:175](../../e2b_flow/sandbox_eval.py#L175) |
| Persona-routed eval critics keyed off `TaskRuntime.kind` | **Shipped** | [`evals.py`](../../evals.py) |
| E2B build/test gate (Python only — `utkrusht-python`) | **Shipped** | [`e2b_flow/sandbox_eval.py`](../../e2b_flow/sandbox_eval.py) |
| Additional E2B templates (node/java/go/flutter/playwright/…) | **Proposed** — design only | — |
| `classifier_version` cache-invalidation tooling (backfill script) | **Proposed** | — |
| Multi-tenancy (`organization_id` on all tables) | **Shipped — hardcoded UUID** via `UTKRUSHT_ORG_ID` env var | `.env` |
| RLS policies + authenticated `auth.org_id()` (v2 multi-tenant) | **Proposed** — deferred until customer orgs | — |

**What this means for the rest of this doc.** Sections below describe the *target* design as of 2026-05-20. The "Why this matters" / "Problem 1" / "Problem 2" sections describe the *old* state before the refactor — kept as historical context. "The solution" and "PR #1 — concrete scope" sections describe what was actually built; "Out of scope" items remain on the roadmap.

The single shipped change closest to the doc's original framing: classification is now per-combo (cached in `competency_combo_classification`) rather than per-task. ~50 unique combos × ~$0.001 per LLM call = ~$0.05 to populate the cache, then column reads forever. Override path: edit the row directly; the cache reads it.

## Shipped architecture — two tables, one resolver

What actually went into the dev DB on 2026-05-25 is a **two-table cache** plus a single Python entry point (`resolve_plan`) that reads through it. The "tasks.task_runtime JSONB column" referenced in the legacy diagrams below (Step 2 / Step 3) was the first attempt — it has been **dropped** in favour of the shape described here.

### Table 1 — `template_registry` (B6)

Applied first; the combo cache has a foreign key to it.

| column | type | role |
|---|---|---|
| `runtime` | `text` PK | `python`, `node`, `java`, … |
| `template_name` | `text` | E2B template id, e.g. `utkrusht-python` |
| `build_cmd` | `text` | e.g. `pip install --break-system-packages -r requirements.txt` |
| `test_cmd` | `text` | e.g. `python -m pytest -q --tb=short` |
| `compile_cmd` | `text` | optional |
| `needs_browser` | `bool` | for Playwright lanes |
| `description` | `text` | what's baked into the image |

One row per runtime. Seeded today with `python` mirroring the existing in-memory recipe. Adding `node` / `java` / `go` is a one-row INSERT, not a code change.

### Table 2 — `competency_combo_classification` (B1)

| column | type | role |
|---|---|---|
| `combo_key` | `text` PK | e.g. `"FastAPI (INTERMEDIATE), Python (INTERMEDIATE)"` |
| `organization_id` | `uuid` | Utkrusht UUID for v1 (multi-tenant-ready from day one) |
| `runtime`, `kind` | `text` | the classifier's verdict |
| `frameworks`, `datastores`, `messaging` | `text[]` | structured `TaskRuntime` fields |
| `needs_browser` | `bool` | |
| `template_runtime` | `text` FK → `template_registry(runtime)` | which template to boot; `NULL` when no template exists yet |
| `classifier_version` | `text` | bump when the LLM prompt/model changes; old rows can then be re-classified |
| `confidence` | `numeric(3,2)` | rows `< 0.7` surface for human review |

One row per `(organization_id, combo_key)`. The combo_key is built by `make_combo_key()` (sorted competency names with proficiency suffix), so the same competency set always hashes to the same key regardless of input order.

### How `resolve_plan(competencies)` uses them

```
combo_key = make_combo_key(competencies)
                ▼
  SELECT runtime, kind, frameworks, datastores, messaging, needs_browser
    FROM competency_combo_classification
   WHERE combo_key = ? AND organization_id = ?
                ▼
   ┌─── HIT  → return ResolvedPlan(
   │             TaskRuntime(from row),
   │             template_registry row joined via template_runtime FK
   │           )                                       (~10 ms, $0)
   │
   └─── MISS → classify_with_llm(competencies)         (~2 s, ~$0.001)
                  • Sonnet via Portkey
                  • strict Pydantic schema
                  • retry once with the specific ValidationError fed back
                ▼
              UPSERT competency_combo_classification (
                  combo_key, organization_id,
                  runtime, kind, frameworks, datastores, messaging, needs_browser,
                  template_runtime,           -- FK; NULL if no template seeded
                  classifier_version='v1',
                  confidence
              )
                ▼
              return ResolvedPlan(new TaskRuntime, template)
```

### Who reads `ResolvedPlan`

| Consumer | Field used | Effect |
|---|---|---|
| `multiagent.py:create_task` | `plan.kind` | persona-routed eval critics (DBA / MLE / SDET / …) |
| `multiagent.py:create_task` | `plan.template.name` | E2B build/test gate template id |
| `prompt_generator/agent.py:step1` | `plan.task_runtime` | DSPy InputFields + HARD CONSTRAINT block |
| `e2b_flow/sandbox_eval.py` | `template_name_for_runtime(plan.runtime)` | sandbox boot |

Every consumer goes through `resolve_plan` — there is no longer a second classification site.

### Failure modes & graceful degradation

| Failure | Behaviour |
|---|---|
| Supabase unreachable at cache-lookup time | Warn, fall through to direct LLM call (no caching this call) |
| Supabase upsert fails at cache-write time | Warn, return the resolved plan anyway; next call re-classifies |
| `UTKRUSHT_ORG_ID` env var missing | Skip cache entirely, plain LLM path (used in unit tests) |
| LLM classifier raises after retry | Return empty `ResolvedPlan` — callers skip persona routing and the gate, never crash |
| `template_runtime` not yet in `template_registry` | Stored as `NULL` (FK respected); the gate skips with `no_template` |
| API role missing GRANT on the table | `permission denied for table` warning, same fall-through as Supabase-down — needs the GRANT migration applied (see below) |

### Bootstrap — three migrations to apply in order

1. [`migrations/2026-05-25-create-template-registry.sql`](../../migrations/2026-05-25-create-template-registry.sql) — creates B6 + seeds the `python` row.
2. [`migrations/2026-05-25-create-competency-combo-classification.sql`](../../migrations/2026-05-25-create-competency-combo-classification.sql) — creates B1 with FK to B6 + the two indexes.
3. [`migrations/2026-05-25-grant-cache-tables.sql`](../../migrations/2026-05-25-grant-cache-tables.sql) — grants `SELECT/INSERT/UPDATE/DELETE` to `anon`, `authenticated`, `service_role` so the PostgREST API (used by `supabase-py`) can read and write. **Without this the cache silently fails on every call** — tables created in the SQL editor default to `postgres`-only ownership.

---

## TL;DR

The rule-based classifier at `prompt_generator/classifier.py` dumps **54% (183/339)** of dev tasks into `PURE_CODE`, the "I dunno" default. Three failure modes drive it: a structural bug where *framework-without-database* falls through every branch; missing tokens for whole languages (Flutter, Dart, Scala, Playwright, React Native, MERN); and collapsing a multi-dimensional infrastructure spec into a single enum value.

The proposed refactor: replace the enum with a structured `TaskRuntime` record everywhere it's read; classify with an LLM call wrapped by a Supabase-backed cache (~50 unique combos in the DB → ~$0.05 to backfill, then never again — no maintained token lists, no substring-match bugs, new tech is auto-handled); define ~11 pre-built E2B templates, one per (runtime, framework lane), each used for **both** the future eval gate and candidate-facing deployment so production parity is guaranteed. Service containers stay where they already are — in each task's own `docker-compose.yml`.

The classifier is the input to both persona-routed eval critics and the future E2B build/test gate. Fixing it first unblocks both.

---

## Why this matters

`classify_task_category(competencies)` answers one question — *"what infrastructure does this task need?"* — and that single answer flows into:

- The **prompt generator's DSPy signature** (`prompt_generator/agent.py:209`, `:272`): the value is an input field on both the Generate and Verify steps; the docstring (`agent.py:155-160`) tells the LLM "The `task_category` field determines the file structure."
- The **reference retriever** (`prompt_generator/retriever.py:293`): picks reference prompts by category match.
- The **planned persona eval critics** ([task-eval-optimizer.md](./task-eval-optimizer/task-eval-optimizer.md) §1): one persona per category — DBA for `DB_ONLY`, MLE for `LLM_FRAMEWORK`, SRE for `CONTAINERIZED_APP`, etc.
- The **planned E2B build/test gate** (`.task_agent_runs/FOLLOWUPS.md` F12): the sandbox needs to know which template to boot.

If the classifier mislabels `Python + FastAPI` as `PURE_CODE`, every downstream system inherits the lie.

---

## Problem 1 — the classifier lies on most tasks

### 1.1  The data

Re-classified every row of the dev `tasks` table (339 rows). Distribution:

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

### 1.2  Three concrete failures

#### A — `Python - FastAPI (BASIC)` × 9 tasks: structural bug

A FastAPI service is unambiguously an app. Current verdict: `PURE_CODE`.

Trace `classify_task_category()` (`classifier.py:155-183`):

```python
has_db        = False   # no SQL/postgres/mongo/… in the name
has_framework = True    # matches "fastapi"
has_backend   = False   # ← BUG. _has_backend_language() requires
                        #   backend-token AND NOT framework-token.
                        #   "Python - FastAPI" matches both → returns False.
has_container = False

# Every branch needs has_db or has_container → all False:
if has_db and (has_framework or has_web_app_lang):   # False
if has_db and has_backend:                           # False
if has_db:                                           # False
if has_container and (has_backend or has_framework): # False
# → PURE_CODE
```

Same hole eats `PHP - Laravel` (11 tasks), `Java + Spring Boot` (3+ tasks), `Java + Hibernate`.

#### B — `Flutter (INTERMEDIATE)` × 2 tasks: missing tokens

`"flutter"` appears in no token list. No frontend, no backend, no anything → `PURE_CODE`. Same wall: `React Native + Firebase` × 8, `Scala` × 1, `Apache Camel` × 1.

#### C — `Golang, Redis`: wrong branch

Should be `APP_AND_DB` (Go binaries are servers). Current verdict: `SCRIPT_AND_DB`. Why? Go is in `_BACKEND_LANG_TOKENS` but not in `_WEB_APP_LANG_TOKENS`, so backend+DB without a framework defaults to "script + DB" — wrong for Go.

### 1.3  More holes from the DB pile

```
9x  Python - FastAPI                → app
8x  QA and Automation - MERN Stack  → app_and_db (Mongo+Express+React+Node)
8x  Firebase, React Native          → mobile (new category)
7x  PHP - Laravel                   → app
6x  REST APIs                       → concept-only, ignore
6x  Playwright                      → e2e_testing (needs browser)
5x  HTML and CSS, Javascript        → frontend
4x  Java + Spring Boot variants     → app
3x  Flutter                         → mobile
1x  Scala                           → app
```

These are the things to fix.

---

## Problem 2 — what an E2B template actually is

The intuitive *"one template per task type"* plan dies under the math (8 runtimes × 5 frameworks × 4 DBs × … ≈ 480+ templates). But the real shape of the problem is different, and the existing code in `e2b_flow/templates/python-sql/` already shows it.

### 2.1  An E2B template is a pre-built VM snapshot

Look at `e2b_flow/templates/python-sql/template.py`:

```python
from e2b import AsyncTemplate

template = (
    AsyncTemplate()
    .from_image("e2bdev/code-interpreter:latest")
    .run_cmd("apt-get install -y ... postgresql-client netcat-openbsd ...")
    .run_cmd("install docker-ce docker-compose-plugin ...")        # DinD
    .run_cmd("pip install psycopg2-binary sqlalchemy pandas")       # libs baked in
    .run_cmd("install ttyd ...")                                    # browser terminal
    .run_cmd("dpkg -i code-server_4.96.4_amd64.deb")               # browser VS Code
    .run_cmd("install adminer ...")                                 # browser DB GUI
    .copy("start.sh", "/usr/local/bin/start.sh")
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
```

Built once via `python build_prod.py` → registered with E2B as `utkrusht-python-sql`. A sandbox boots from this snapshot in ~150ms. **Nothing is installed at boot.** Pip/npm/apt at runtime is exactly the wrong pattern.

### 2.2  Service containers come from the task, not the platform

The template provides **DinD** (Docker daemon inside the sandbox). The task ships its own `docker-compose.yml` that brings up Postgres-server, Redis, Mongo, whatever it needs. The task's `run.sh` does `docker compose up`; `kill.sh` does `docker compose down`.

`DEFAULT_PROBE_PORTS` in `sandbox_manager.py` confirms the split:

```python
DEFAULT_PROBE_PORTS = (
    5432, 8000, 3000, 6379, 27017, 8080, 6443,
    5000, 7681, 8443,
)
```

| Ports baked into the template | Ports the task brings via compose |
|---|---|
| 7681 (ttyd), 8443 (code-server), 8080 (Adminer) | 5432 (Postgres), 6379 (Redis), 27017 (Mongo) |
| Plus 8000/3000/5000 — the candidate's app dev server |

### 2.3  This collapses the maintenance surface

| Owner | Maintains | Cardinality |
|---|---|---|
| **Platform (us)** | E2B templates (`template.py` + `start.sh` per template) | **~11**, one per runtime+lane |
| **Each task** | Its own `docker-compose.yml` + `run.sh` + `kill.sh` | brought with the task |

We never maintain a "sidecar library." Each task carries its own service containers. So template count is bounded by runtime × framework-lane, **not** by databases × messaging × etc.

---

## The solution

### Step 1 — replace the lossy enum with a structured spec

A single `TaskCategory` enum compresses a multi-dimensional infrastructure spec into one flat value. Replace it with a record (no derived enum, no backward compat — nothing is stored yet):

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class TaskRuntime:
    runtime:        Literal["python","node","java","php","go","rust",
                            "flutter","ruby","scala","none"]
    frameworks:     tuple[str, ...]   # ("fastapi",), ("spring-boot",), ("laravel",)
    datastores:     tuple[str, ...]   # ("postgres",), ("mongo","redis")
    messaging:      tuple[str, ...]   # ("kafka",)
    needs_browser:  bool              # Playwright/Selenium
    kind:           Literal["app","script","mobile","frontend","testing",
                            "db_only","llm","vector_db","non_code"]
```

This is the **only** classifier output. `TaskCategory` is deleted.

### Step 2 — LLM classifier with persistent caching

The classifier is a single LLM call wrapped by a cache. No token lists, no substring matching, no hand-tuned rule branches.

```
                competencies
                     │
                     ▼
        ┌────────────────────────────┐
        │ Cache lookup               │
        │ keyed by sorted-set hash   │  Supabase
        │ of competency names        │  tasks.task_runtime
        └─────────────┬──────────────┘
                      │
              HIT     │     MISS
                      ▼
              TaskRuntime
              (~10 ms, $0)

              MISS path:
                      ▼
        ┌────────────────────────────┐
        │ LLM classifier (Sonnet)    │  ~1.5 s, ~$0.001
        │ strict JSON schema → TR    │
        └─────────────┬──────────────┘
                      ▼
        ┌────────────────────────────┐
        │ Write to cache             │  tasks.task_runtime row
        │ + classifier_source="llm"  │  + confidence score
        └─────────────┬──────────────┘
                      ▼
              TaskRuntime
```

The DB has ~50 distinct competency sets across 339 tasks → ~50 LLM calls ever, **~$0.05 to backfill the entire dev DB**. After that, classification is a 10ms column read.

**Why no rules layer.** Earlier drafts proposed rules-first with LLM fallback. The trade-off doesn't work in favour of rules:

- Token lists go stale every time new tech emerges (Elixir, Mojo, Bun, Phoenix LiveView). The LLM doesn't — its training data is current.
- Substring matching has false positives — `"rust"` substring-matches `"trusted"`, `"go"` substring-matches `"mongo"`. Maintaining substring tokens is fighting your tools.
- The framework-no-DB bug we found was an emergent property of rule complexity. Removing rules removes that category of bug entirely.
- The rules-vs-LLM latency gap (~5 ms vs ~1.5 s) only matters on the first sight of a combo — at task-generation time, not in any user-facing hot path.

**Determinism via cache, not via constraints on the LLM.** Same input → same output, because it's a column read. The "LLM is non-deterministic" concern doesn't survive caching.

**Safety rails for the LLM:**
- Strict JSON schema enforcement — invalid output is rejected and retried.
- A `confidence` field on every classification. Anything `< 0.7` is queued for human review before downstream code trusts it.
- Persist `classifier_source` (`"llm"` / `"manual_override"`) so we can audit later and diff drift.
- **Override path.** A row in `tasks.task_runtime` can be edited directly. The cache reads it. If the LLM hallucinates once, fix the row, done. No code change needed for one-off corrections.

### Step 3 — E2B templates: one snapshot per runtime+lane

**~11 templates**, each a pre-built E2B v2 microVM snapshot. Each is one `template.py` + one `start.sh` (the file layout is incidental — what matters is the contents). Final shape is gated on the SDK verifications listed below.

```
TEMPLATE                     RUNTIME    BAKES IN (in addition to common boilerplate)
─────────────────────────────────────────────────────────────────────────────────────
utkrusht-python-sql ✅       python     psycopg2-binary, sqlalchemy, pandas, postgresql-client
utkrusht-python-web          python     fastapi, flask, django, uvicorn, httpx, sqlalchemy
utkrusht-python-llm          python     langchain, llama-index, openai, anthropic, pinecone-client
utkrusht-node-web            node       express, react, next, typescript, jest, vitest
utkrusht-node-mobile         node       react-native CLI, expo CLI
utkrusht-java-spring         java       JDK 17, maven, gradle, spring-boot-starter-*
utkrusht-php-laravel         php        php-fpm, composer, laravel installer
utkrusht-go-base             go         go toolchain (binaries are static — no preinstall needed)
utkrusht-rust-base           rust       cargo + common crates (tokio, serde, sqlx)
utkrusht-flutter             flutter    dart SDK + flutter
utkrusht-playwright          node       chromium preinstalled + playwright pkg
```

**Common boilerplate baked into every template:**

- Docker daemon (DinD) so tasks can `docker compose up` against their own compose file
- `ttyd` browser terminal on port 7681
- `code-server` browser VS Code on port 8443
- Adminer browser DB GUI on port 8080 (for any task using a SQL DB)
- Compose v1→v2 shim, `netcat-openbsd`, `git`, `jq`

### Step 3a — one template lineage, used for both eval and deployment

We do **not** maintain "eval templates" and "deploy templates" as separate sets. Each of the ~11 templates above serves **both** the future E2B build/test gate (task-eval-optimizer Phase 3) and candidate-facing deployment. Reasons:

- **Production parity.** Anything that passes eval must run on the template the candidate actually gets. A split would re-introduce F12-class bugs at the template layer — "eval template was fine, deploy template missing a library." That's the exact failure mode F12 surfaced at the eval layer.
- **Single source of truth.** Adding a Python package means updating one template, not two.
- **The "dead weight" cost is negligible.** Browser tools running during automated eval are background processes on a microVM; they cost nothing observable.
- **Boot time is fine for eval.** Even 5–10 s per eval is acceptable — eval runs at task-generation time, not per candidate request.

The eval gate boots a sandbox from the same template the candidate would receive, copies the task code in, runs `run.sh`, captures pass/fail + stderr/stdout, then kills the sandbox. Candidates get the same template, with a longer idle timeout and the browser URLs exposed.

### Step 4 — TaskRuntime → template_id picker

Mechanical mapping:

```python
def pick_template(rt: TaskRuntime) -> str:
    if rt.kind == "mobile" and rt.runtime == "flutter": return "utkrusht-flutter"
    if rt.kind == "mobile" and rt.runtime == "node":    return "utkrusht-node-mobile"
    if rt.kind == "testing" and rt.needs_browser:       return "utkrusht-playwright"
    if rt.kind == "llm":                                return "utkrusht-python-llm"
    if rt.runtime == "python" and "postgres" in rt.datastores:
                                                        return "utkrusht-python-sql"
    if rt.runtime == "python" and rt.frameworks:        return "utkrusht-python-web"
    if rt.runtime == "node":                            return "utkrusht-node-web"
    if rt.runtime == "java":                            return "utkrusht-java-spring"
    if rt.runtime == "php":                             return "utkrusht-php-laravel"
    if rt.runtime == "go":                              return "utkrusht-go-base"
    if rt.runtime == "rust":                            return "utkrusht-rust-base"
    raise ValueError(f"no template for {rt}")
```

Service containers are NOT a picker concern — they're brought by the task's compose file.

---

## E2B SDK capabilities — verified

The ~11-template list above doesn't need to ride on assumptions. The following was confirmed against the v2 SDK installed from `requirements.txt` (introspected) and current E2B docs.

### Findings

**1. Template composition / inheritance — YES.**
`AsyncTemplate().from_template("utkrusht-python-base")` chains from a parent template; verified via SDK introspection. Plus E2B ships **layer-level cache sharing** across templates within a team — identical early `run_cmd()` sequences automatically share build cache even without explicit inheritance. (Source: SDK introspection + `docs/template/caching`.)

**2. Multi-container natively — NO.** No first-class sidecar primitive. The documented pattern for multi-service tasks is Docker-in-Docker: install Docker + docker-compose into the template, run `docker compose up` inside the sandbox. This is exactly what `python-sql` already does. (Source: `docs/template/examples/docker`.)

**3. Account-level limits — not a constraint.** Pro tier ($150/mo): 100 concurrent sandboxes (expandable to 1100), 24-hour sessions, **20 GiB storage**. 13 templates × ~1.5 GB fits comfortably. Hobby tier (free) includes a $100 usage credit and 10 GiB. Per-sandbox usage is ~$0.10/hour at 2 vCPU. (Source: `e2b.dev/pricing`.)

**4. Cold-start latency — ~78–180 ms.** Firecracker microVM snapshot boot. The "5–10 s" earlier drafts worried about is **start-cmd execution** (dockerd + ttyd + code-server initialising), not the snapshot itself. Image size affects start-cmd, not snapshot. (Source: public benchmarks, Jan 2026.)

**5. Best-practice base image.** The v2 SDK exposes **language-specific convenience methods**: `from_python_image()`, `from_node_image()`, `from_bun_image()`, `from_ubuntu_image()`, `from_debian_image()`, `from_base_image()` (which uses `e2bdev/base:latest` — minimal E2B-flavoured base). `python-sql` currently uses `from_image("e2bdev/code-interpreter:latest")`, which is heavier (ships Jupyter) — we don't need that. Each template can call exactly one base method. (Source: `docs/template/base-image` + SDK introspection.)

### What this changes in the design

1. **Use language-specific base methods, not `e2bdev/code-interpreter`.** Every `utkrusht-*` template's `template.py` starts with `from_python_image()` / `from_node_image()` / etc. — leaner than what `python-sql` does today.
2. **Embrace `from_template()` for composition.** Build `utkrusht-python-base` once (Python + DinD + ttyd + code-server + adminer + compose-shim). Then leaf templates `from_template("utkrusht-python-base")` and add only their lane-specific libraries. Maintenance per leaf drops to ~20 LOC.
3. **DinD stays.** No design change; the task's own `docker-compose.yml` brings up its services.
4. **Don't pre-optimise image size.** 20 GiB of headroom on Pro covers any reasonable shape.
5. **Cold-start is dominated by start-cmd, not snapshot.** If eval-gate latency ever matters, profile `start.sh` (dockerd warm-up, etc.); the VM boot itself is ~150 ms and not the bottleneck.

### Revised template hierarchy (composition-aware)

```
utkrusht-python-base   from_python_image()
                       + DinD, ttyd, code-server, adminer, compose-shim, common deps
   ├── utkrusht-python-sql       from_template("utkrusht-python-base") + psycopg2, sqlalchemy, postgresql-client
   ├── utkrusht-python-web       from_template("utkrusht-python-base") + fastapi, flask, django, uvicorn
   └── utkrusht-python-llm       from_template("utkrusht-python-base") + langchain, llama-index, openai, anthropic

utkrusht-node-base     from_node_image()
                       + DinD, ttyd, code-server, adminer, compose-shim
   ├── utkrusht-node-web         from_template("utkrusht-node-base") + express, react, next, typescript, jest
   ├── utkrusht-node-mobile      from_template("utkrusht-node-base") + react-native, expo
   └── utkrusht-playwright       from_template("utkrusht-node-base") + chromium-headless, playwright

utkrusht-java-base     from_debian_image() + JDK 17 + maven + gradle + DinD + browser tools
   └── utkrusht-java-spring      from_template("utkrusht-java-base") + spring-boot starters

# stand-alone (no leaves yet):
utkrusht-php-laravel   from_debian_image() + php-fpm + composer + laravel + DinD + browser tools
utkrusht-go-base       from_debian_image() + go toolchain + DinD + browser tools
utkrusht-rust-base     from_debian_image() + cargo + common crates + DinD + browser tools
utkrusht-flutter       from_debian_image() + dart SDK + flutter + browser tools  (no DinD — mobile tasks don't need compose)
```

**Effective maintenance surface:** 7 roots + ~6 leaves = ~13 template files. Each leaf is ~20 LOC.

---

## What changes in generated task content

The prompt generator currently instructs the LLM to produce `run.sh` and `kill.sh` that install Docker, install the language runtime, install system packages, then bring up services. That made sense for the droplet target (bare VM). For the E2B target, **most of that boilerplate is already in the template** and should be stripped.

`run.sh` and `kill.sh` themselves **stay** — they remain the contract between task and platform. The change is what goes inside them.

### Before (current generated content — droplet-shaped)

```bash
# run.sh
apt-get update
apt-get install -y python3 python3-pip postgresql-client docker.io
pip install -r requirements.txt
docker compose up -d
psql -h localhost -U postgres < seed.sql
python app/main.py
```

### After (sandbox-aware — template provides infra)

```bash
# run.sh
docker compose up -d              # task's own compose for postgres-server
psql -h localhost -U postgres < seed.sql
python app/main.py
```

Same for `kill.sh` — drop the uninstall steps; keep `docker compose down`.

### Where this lands in code

The prompt generator's `GeneratePromptSignature` docstring (`prompt_generator/agent.py:155-160`) currently reads "The `task_category` field determines the file structure. Match it exactly: PURE_CODE → no Docker… APP_AND_DB → Docker + DB…". This becomes:

```
The TaskRuntime fields determine the generated content:
  • runtime, frameworks, libraries — already pre-installed by the E2B template.
    Do NOT include apt-get install, pip install, or npm install for these in run.sh.
  • datastores — generate a docker-compose.yml that brings up these service
    containers (Postgres, Redis, Mongo, …). run.sh does `docker compose up`,
    kill.sh does `docker compose down`.
  • kind="mobile" — no Dockerfile, no compose; the template ships the SDK.
    run.sh runs the runtime's native test command (e.g. `flutter test`).
  • needs_browser — the template (utkrusht-playwright) already ships chromium;
    do NOT install it in run.sh.
```

---

## Worked examples

| Task | Current (broken) | TaskRuntime | Template | Task's compose |
|---|---|---|---|---|
| `Python - FastAPI` | `PURE_CODE` ❌ | `runtime=python`, frameworks=`(fastapi,)`, kind=`app` | `utkrusht-python-web` | (none) |
| `Python - FastAPI + Postgres` | `APP_AND_DB` ✓ | `runtime=python`, frameworks=`(fastapi,)`, datastores=`(postgres,)`, kind=`app` | `utkrusht-python-sql` | postgres-server |
| `Flutter` | `PURE_CODE` ❌ | `runtime=flutter`, kind=`mobile` | `utkrusht-flutter` | (none) |
| `Golang, Redis` | `SCRIPT_AND_DB` ⚠️ | `runtime=go`, datastores=`(redis,)`, kind=`app` | `utkrusht-go-base` | redis-server |
| `Playwright` | `PURE_CODE` ❌ | `runtime=node`, kind=`testing`, needs_browser=`True` | `utkrusht-playwright` | (none) |
| `Python + LlamaIndex` | `LLM_FRAMEWORK` ✓ | `runtime=python`, frameworks=`(llama-index,)`, kind=`llm` | `utkrusht-python-llm` | (none) |
| `Java + Spring Boot + Postgres` | `APP_AND_DB` ✓ | `runtime=java`, frameworks=`(spring-boot,)`, datastores=`(postgres,)`, kind=`app` | `utkrusht-java-spring` | postgres-server |
| `MySQL` (alone) | `DB_ONLY` ✓ | `runtime=none`, datastores=`(mysql,)`, kind=`db_only` | `utkrusht-python-sql` (reused; has psql client + Adminer) | mysql-server |
| `MERN Stack` | `PURE_CODE` ❌ | `runtime=node`, frameworks=`(express, react)`, datastores=`(mongo,)`, kind=`app` | `utkrusht-node-web` | mongo-server |
| `Firebase + React Native` | `PURE_CODE` ❌ | `runtime=node`, frameworks=`(react-native, firebase)`, kind=`mobile` | `utkrusht-node-mobile` | (none) |

Ten wildly different tasks, all assembled from **~11 templates + each task's own compose**.

---

## Where this fits in the wider plan

```
┌────────────────────────────────────────────────────────────┐
│ PR #1 — classifier refactor + prompt-generator rewrite     │   ~250 LOC
│ • TaskRuntime struct (replaces TaskCategory entirely)      │   ~$0.05 one-time
│ • LLM classifier + Supabase-cached results                 │   Supabase migration
│ • Rewrite agent.py:155-160 HARD CONSTRAINT block           │
│ • Rewrite agent.py:209 + :272 dspy.InputFields             │
│ • Rewrite retriever.py:293 to use TaskRuntime              │
│ • Rewrite trainset.py:380 column schema                    │
│ • Add tasks.task_runtime JSONB; backfill 339 rows          │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ task-eval-optimizer Phase 1 — persona-routed critics       │   ~120 LOC
│ Keyed off TaskRuntime.kind                                 │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ E2B SDK capability check + template buildout               │   per-template:
│ (see "Verify against the E2B SDK" above)                   │   ~80 LOC + start.sh
│ Then build ~10 templates beyond python-sql                 │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ task-eval-optimizer Phase 3 — E2B build/test gate          │   ~250 LOC
│ • Template picker reads TaskRuntime                        │
│ • Per-stack install + test commands                        │
│ • Adversarial test check (FOLLOWUPS.md F12)                │
└────────────────────────────────────────────────────────────┘
```

---

## PR #1 — concrete scope (~250 LOC)

1. Introduce `TaskRuntime` dataclass in `prompt_generator/classifier.py`. **Delete `TaskCategory`** and the entire rule-based classifier (`_DB_TOKENS`, `_WEB_FRAMEWORK_TOKENS`, all the `_has_*` helpers, `_matches_any`).
2. Implement the **LLM classifier** — strict JSON schema, returns `TaskRuntime`. Wrap with a Supabase-backed cache keyed by a sorted-competency-set hash. Persist `confidence` and `classifier_source` columns alongside the runtime payload.
3. Add `tasks.task_runtime JSONB` column. **Backfill all 339 rows** by running the LLM classifier once per unique combo (~50 LLM calls, ~$0.05 total). Surface any `confidence < 0.7` rows for manual review before the next PR builds on them.
4. **Rewrite the four call sites in `prompt_generator/`**:
   - `agent.py:155-160` HARD CONSTRAINT block — instruct the LLM in terms of `runtime`/`frameworks`/`datastores`/`kind`, with the explicit "DO NOT install runtime/libs in run.sh" rule.
   - `agent.py:209` and `:272` `dspy.InputField`s — replace `task_category: str` with structured fields (`runtime: str`, `frameworks: str`, `datastores: str`, `kind: str`).
   - `retriever.py:293` — reference matching now keys off `(runtime, kind)`.
   - `trainset.py:380` — column schema updates.
5. **Validation**: re-classify all 339 dev tasks; every row gets a `TaskRuntime`. The old `PURE_CODE` default bucket should drop to ~zero (the LLM knows the difference between a script and an app). Anything `< 0.7` confidence goes on the review queue, not into production.

Estimated **~250 LOC** + Supabase migration + ~$0.05 in classifier calls. The LLM is the classifier — there is no PR #2 just for "the LLM fallback."

---

## Out of scope (handled in later PRs)

- E2B SDK capability verification (the questions in the "Verify against the E2B SDK" section) — a separate spike before template buildout begins.
- Building the ~10 additional E2B templates (separate epic — design in this doc, build under `e2b_flow/templates/`).
- The E2B build/test gate itself (task-eval-optimizer Phase 3).
- Migrating the (deployed) droplet flow to E2B for tasks already running — outside the prompt-generator's concern.

---

## Open questions

- **Do we need a separate `utkrusht-python-web` template, or can `utkrusht-python-sql` cover both?** `python-sql` already has Python + DinD + postgresql-client + Adminer. The only thing missing is FastAPI/Flask/Django pre-installed. Could either bake those into `python-sql` (one fewer template to maintain) or keep them separate (smaller image for non-DB tasks). Lean **bake in** — saves a template, marginal image-size cost.
- **`utkrusht-go-base` necessity**: Go binaries are statically linked; the template barely needs anything beyond the toolchain. Could just rely on the e2bdev base image + `apt-get install golang`. Worth profiling whether building a dedicated template is worth it vs. baking Go into `python-sql`-style base.
- **How do we handle multi-runtime tasks** like `Frontend (React) + Backend (Python FastAPI)`? Current model picks ONE template. Option a: pick the dominant runtime and pre-install the other's CLI as a "helper"; option b: a new combo template. Need a real example from the DB before deciding — there are very few such combos.
- **Should the prompt generator know which template will be picked?** Yes — knowing the template informs the generated `run.sh` (e.g., "you can assume `psycopg2` is importable"). Probably pass `template_id` as a derived `dspy.InputField` alongside the `TaskRuntime` fields.
- **`is_shared_infra_required` migration**: today 53% of tasks have it set. Maps roughly to "task has a `docker-compose.yml`." Worth a sanity check during backfill — when `is_shared_infra_required=True` but the new classifier infers no `datastores`/`messaging`, surface as an outlier for manual review.

---

## References

- `prompt_generator/classifier.py` — current implementation
- `prompt_generator/agent.py:155-160, 209, 272` — the `task_category` consumers in the DSPy signatures (the rewrite targets)
- `e2b_flow/templates/python-sql/template.py` — the canonical E2B template pattern (v2 SDK, `AsyncTemplate`)
- `e2b_flow/templates/python-sql/start.sh` — the boot-time supervisor (dockerd + ttyd + code-server + adminer)
- `e2b_flow/sandbox_manager.py` — `DEFAULT_PROBE_PORTS` confirms the template/task split for ports
- [prompt-generator-agent.md](./prompt-generator/prompt-generator-agent.md) — context on the 5 signals fed to the LLM
- [task-eval-optimizer.md](./task-eval-optimizer/task-eval-optimizer.md) — downstream Phase 1 (persona critics) and Phase 3 (E2B gate)
- `.task_agent_runs/FOLLOWUPS.md` — F12 (non-compiling code passed eval) is the strongest argument for the E2B gate, which depends on this work
- Supabase `tasks` table (dev environment, 339 rows analysed 2026-05-20)
