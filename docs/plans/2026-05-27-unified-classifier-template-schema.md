# Plan: Unified Classifier ↔ Template Schema (Merge Proposal + v2 Intent)

> **Status:** Plan locked 2026-05-27. Not yet implemented. Supersedes the v2 TaskRuntime stress-test proposal and the standalone merge proposal in [`classifier.md`](../task-classifier/classifier.md) — this is the single source of truth for the direction.
> **Owner:** Rohan
> **Author note:** Naman's merge proposal (PR #19, branch `docs/classifier-template-merge-proposal`) is the structural base; this plan extends it with per-task intent.

## What we're doing

Collapsing the current two-table architecture (closed `Runtime` enum + `template_registry` keyed on runtime + `competency_combo_classification` cache) into a unified three-layer model:

```
  templates                    capability sheets the LLM reads to match
       ↑
  task_template_match          which template+persona matched this combo (cache)
       ↑
  tasks.task_intent            per-task USE of the matched template's capabilities
```

**One direction. No v1 fallback.** The current `TaskRuntime`, `Kind`, `Runtime` Literal enums, and `template_name_for_runtime()` picker get deleted in Phase 4.

## Decisions locked in

| Area | Decision | Why |
|---|---|---|
| Table names | `templates` + `task_template_match` (renamed from `template_registry` + `competency_combo_classification`) | Per Naman's merge proposal commit |
| Capability storage | `capabilities jsonb` for extensible dimensions; `text[]` only for `personas`, `eval_methods`, `primary_runtime` | Extensible dimensions (frameworks, datastores, protocols, tools, requires) shouldn't need migrations to add. Closed enums stay typed for LLM-pick-one semantics. |
| Per-task intent | `tasks.task_intent jsonb` — separate from match cache | Match is per-combo (cached, reusable). Intent is per-task (datastore roles, protocol used, eval method, secondaries). Different keys, different lifecycles. |
| Combo cache key | `combo_key` only | `resolve_plan()` is a pure combo→template+persona mapping. Per-task variation captured in `task_intent` instead. |
| Scenario NOT passed to classifier | `resolve_plan(competencies)` — no scenario, no background | The content-generation LLM already sees the scenario. Passing it to the classifier too is double-paying. The classifier's job (pick template + default persona + detect no_match) doesn't need scenario for ~95% of combos. Edge cases (persona varies by scenario) are handled by `task_intent.persona_override`. |
| Manifest hash discipline | Required before any merge-model code lands | Without CI sheet-from-Dockerfile generation, capability sheets rot. This is the durability gate. |
| `no_match` path | First-class — `template_id IS NULL` + `missing_capabilities[]` + `suggested_template` | Drives the template-build roadmap from data. |
| Polyglot | Install secondary runtime at boot via `templates.install_cmd`; `task_intent.secondary_runtimes` records the choice | Avoids building polyglot templates per pair until usage data justifies it. |
| Old enums / picker | Deleted in Phase 4 after consumer cutover | No indefinite coexistence. |

## The schema

### `templates` — capability sheets

```sql
CREATE TABLE templates (
    template_id           text PRIMARY KEY,                  -- "utkrusht-python", "utkrusht-node-playwright"
    status                text NOT NULL
                          CHECK (status IN ('built','proposed','deprecated')),

    -- Typed: closed enums, LLM picks one per task
    primary_runtime       text NOT NULL,                     -- "python", "node", "rust", ...
    personas              text[] NOT NULL,                   -- ["backend","data","mle"]
    eval_methods          text[] NOT NULL
                          DEFAULT ARRAY['test_suite'],       -- which eval runners this template supports

    -- Extensible: new dimensions added without migration
    capabilities          jsonb NOT NULL DEFAULT '{}',
    -- Convention (validated in Python, not Postgres):
    -- {
    --   "extra_runtimes":     ["node"],                     // only for fat polyglot templates
    --   "language_versions":  {"python":"3.12","node":"20.11"},
    --   "frameworks":         ["fastapi","sqlalchemy"],
    --   "datastores":         ["postgres","mongo","redis"],
    --   "protocols":          ["rest","grpc","websocket"],
    --   "tools":              ["pytest","docker","helm"],
    --   "requires":           {"browser": false, "gpu": false},
    --   "tags":               ["arm64-built","cve-patched-2026-05"]
    -- }

    -- Execution recipes (runtime-idiomatic)
    build_cmd             text NOT NULL,                     -- "pip install -r requirements.txt"
    test_cmd              text NOT NULL,                     -- "python -m pytest"
    compile_cmd           text,                              -- optional

    -- Polyglot install-at-boot — how to install THIS template's primary runtime
    -- when it's used as a secondary in another sandbox
    install_cmd           text,                              -- "curl rustup.rs | sh -s -- -y"
    install_verify        text,                              -- "cargo --version"
    install_seconds       int,                               -- ~60

    -- Drift control — the durability gate
    manifest_hash         text NOT NULL,                     -- sha256 of source Dockerfile/manifest
    manifest_generated_at timestamptz NOT NULL,
    registry_version      integer NOT NULL,                  -- monotonic; bumps invalidate cached matches

    description           text
);

CREATE INDEX templates_active_idx
    ON templates(status) WHERE status = 'built';
CREATE INDEX templates_primary_runtime_idx
    ON templates(primary_runtime) WHERE status = 'built';
```

### `task_template_match` — combo → template+persona cache

```sql
CREATE TABLE task_template_match (
    combo_key             text PRIMARY KEY,                  -- sorted "Python (INTERMEDIATE), PostgreSQL (INTERMEDIATE)"

    template_id           text REFERENCES templates(template_id)
                          ON DELETE SET NULL,                -- NULL = no_match
    persona               text,                              -- one of templates.personas; NULL when no_match
    confidence            real,

    -- no_match path: first-class signal, drives template roadmap
    no_match_reason       text,
    missing_capabilities  text[],                            -- ["helm","terraform","kubectl"]
    suggested_template    text,                              -- "utkrusht-infra"

    -- Cache invalidation
    classifier_model      text NOT NULL,                     -- "claude-sonnet-4-6"
    registry_version      integer NOT NULL,                  -- snapshot at classify time
    classified_at         timestamptz NOT NULL DEFAULT now(),

    CHECK (
        (template_id IS NOT NULL AND no_match_reason IS NULL) OR
        (template_id IS NULL     AND no_match_reason IS NOT NULL)
    )
);
```

A row is valid for serving only when `classifier_model = current_classifier_model AND registry_version = (SELECT registry_version FROM templates WHERE template_id = ...)`. Stale rows auto-re-classify.

### `tasks.task_intent` — per-task use of the matched template

```sql
ALTER TABLE tasks
    ADD COLUMN task_intent jsonb DEFAULT '{}';

-- Shape (validated in Python):
-- {
--   "datastores": [
--     {"name": "postgres", "role": "primary"},
--     {"name": "mysql",    "role": "source"}
--   ],
--   "protocols_used":     ["grpc"],
--   "eval_method":        "test_suite",
--   "secondary_runtimes": [],
--   "persona_override":   null         // or "data" — overrides match.persona for THIS task
-- }
```

Five fields:
- **`datastores`** — array of `{name, role}` where role ∈ `primary | replica | source | target | cache`. Subset of `templates.capabilities.datastores` (the menu); roles are per-task.
- **`protocols_used`** — subset of `templates.capabilities.protocols`. The protocol(s) this task actually implements.
- **`eval_method`** — one of `templates.eval_methods`. Dispatches the eval gate's runner.
- **`secondary_runtimes`** — runtime names (e.g. `["node"]`) to install at boot via each one's `install_cmd`. Empty for single-runtime tasks.
- **`persona_override`** — optional. When the content-generation LLM (which sees the scenario) judges that the cached match's persona is wrong for THIS task, it sets this to the correct persona. Eval critic reads this override before falling back to `match.persona`. ~95% of tasks: absent. ~5%: scenario-specific.

Everything else (which frameworks the task actually exercises, messaging brokers, etc.) is derivable from the generated task code itself, so doesn't need to be stored.

## Python models

```python
# infra/classifier/runtime.py — replaces TaskRuntime entirely

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Role       = Literal["primary","replica","source","target","cache"]
Protocol   = Literal["rest","grpc","graphql","websocket","none"]
EvalMethod = Literal["test_suite","notebook","validator","lint","benchmark","compile_only"]


class DatastoreRef(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    role: Role


class TaskIntent(BaseModel):
    """Per-task USE of the matched template's capabilities.

    Lives on tasks.task_intent. Emitted by the content-generation LLM
    (which already has the scenario in scope), NOT by the classifier.
    """
    model_config = ConfigDict(frozen=True)
    datastores:         list[DatastoreRef] = Field(default_factory=list)
    protocols_used:     list[Protocol]     = Field(default_factory=list)
    eval_method:        EvalMethod         = "test_suite"
    secondary_runtimes: list[str]          = Field(default_factory=list)
    persona_override:   str | None         = None   # overrides match.persona for THIS task


class TaskTemplateMatch(BaseModel):
    """The match decision for one combo. The ONLY thing the classifier emits.

    Cached in task_template_match. Per-combo, not per-task.
    """
    model_config = ConfigDict(frozen=True)

    template_id:          str | None = None
    persona:              str | None = None             # default for this combo
    confidence:           float      = 0.0

    no_match_reason:      str | None       = None
    missing_capabilities: list[str]        = Field(default_factory=list)
    suggested_template:   str | None       = None
```

```python
# generators/task/runtime_resolver.py

@dataclass(frozen=True)
class TemplateSpec:
    """Hydrated row from `templates`, attached to ResolvedPlan."""
    template_id:           str
    primary_runtime:       str
    capabilities:          dict             # the jsonb blob
    personas:              list[str]
    eval_methods:          list[str]
    build_cmd:             str
    test_cmd:              str
    compile_cmd:           str | None
    install_cmd:           str | None
    install_verify:        str | None
    install_seconds:       int | None
    manifest_hash:         str
    registry_version:      int
    description:           str | None


@dataclass(frozen=True)
class InstallCmd:
    """Polyglot prelude — installing a secondary runtime at boot."""
    runtime:    str
    cmd:        str
    verify_cmd: str | None
    seconds:    int


@dataclass(frozen=True)
class ResolvedPlan:
    """The bundle every downstream consumer reads.

    Carries the match (cached per combo) + the template the match resolves to.
    Does NOT carry task_intent — that's emitted later by the content-generation LLM
    and lives on tasks.task_intent.
    """
    combo_key:           str
    match:               TaskTemplateMatch | None     # None on LLM failure
    template:            TemplateSpec | None          # None on no_match (match.no_match_reason has why)


def resolve_plan(
    competencies: Iterable[Competency],
    *,
    supabase=None,
) -> ResolvedPlan:
    """Cache-aware classification — combo → template + default persona.

    Pure mapping. Same competencies always produce the same plan.

    1. Look up task_template_match by combo_key + validate registry_version.
    2. On hit + valid: return ResolvedPlan with the cached match.
    3. On miss/stale: call the LLM with competencies + active templates'
       capability sheets; UPSERT the match row.

    Scenario / background are NOT inputs — they're for the content-generation
    LLM, which emits TaskIntent (including any persona_override) per task.

    Always returns; never raises. Empty plan on LLM failure.
    """
    ...


# Per-task intent is emitted by the content-generation LLM, not resolve_plan.
# Signature roughly (lives in generators/prompts/agent.py or creator.py):

def generate_task_content(
    competencies: Iterable[Competency],
    scenario:     str,
    background:   dict | None,
    plan:         ResolvedPlan,                     # already has template + default persona
) -> tuple[TaskData, TaskIntent]:
    """Generates task files AND emits TaskIntent.

    The LLM here sees the scenario and produces the per-task content
    (description, files, run.sh, compose, tests) plus the structured intent
    that describes how the task uses the template (datastore roles, protocols
    used, eval method, polyglot secondaries, optional persona override).
    """
    ...


# install_secondaries is derived AFTER the content LLM emits intent.secondary_runtimes:

def install_secondaries_for(intent: TaskIntent, supabase) -> list[InstallCmd]:
    """For each runtime in intent.secondary_runtimes, look up the install_cmd
    on the templates table (any built template whose primary_runtime matches)."""
    ...
```

## Migration plan — 5 phases

Each phase is independently shippable; later phases assume earlier ones landed.

---

### Phase 0 — Manifest discipline (the durability gate)

**Cannot skip.** Without manifest hashing, the LLM reads capability sheets that can silently lie about what's in the image.

| Step | Task | Files |
|---|---|---|
| 0.1 | Write a manifest emitter for `utkrusht-python` template. The emitter runs at template build time, introspects the built image, and writes `manifest.json` with `{language_versions, installed_packages, system_pkgs, tools}` | `e2b_flow/templates/python-sql/manifest.py` (new) + `build_prod.py` hook |
| 0.2 | Compute `sha256(manifest.json)` → `manifest_hash`. Write the hash to a sidecar file next to the manifest | same |
| 0.3 | CI step: if any `e2b_flow/templates/**/template.py` or `Dockerfile` changes in a PR, the corresponding `manifest.json` and `manifest_hash` files must also have changed. Fail otherwise. | `.github/workflows/template-manifest-check.yml` (new) |
| 0.4 | Run the emitter for the existing `utkrusht-python` and commit `manifest.json` + `manifest_hash` to the repo so the next phase has values to backfill | `e2b_flow/templates/python-sql/manifest.json` (new) |

**Definition of done:** CI fails on a Dockerfile change that doesn't bump the manifest. The existing python template has a tracked manifest.

**Estimated:** 3 days.

---

### Phase 1 — Schema migration (additive)

Create the new tables; copy data from the old ones. Old tables remain for fallback during Phase 3.

| Step | Task | Files |
|---|---|---|
| 1.1 | `2026-05-28-create-templates.sql` — `CREATE TABLE templates`; copy `template_registry` rows; transform old columns into the new shape (`runtime` → `primary_runtime`; `description` → unchanged; build new `capabilities jsonb` from the existing typed columns plus reasonable defaults; set `personas = ['backend']` for python row); set `manifest_hash` from the file emitted in Phase 0; `registry_version = 1` | `migrations/2026-05-28-create-templates.sql` |
| 1.2 | `2026-05-28-create-task-template-match.sql` — `CREATE TABLE task_template_match`; copy `competency_combo_classification` rows; derive `template_id` from `template_runtime` via existing picker; default `persona = 'backend'`; `registry_version = 1` | `migrations/2026-05-28-create-task-template-match.sql` |
| 1.3 | `2026-05-28-add-task-intent-to-tasks.sql` — `ALTER TABLE tasks ADD COLUMN task_intent jsonb DEFAULT '{}'`; backfill the column for existing tasks with a sensible default (`{"datastores": [], "protocols_used": [], "eval_method": "test_suite", "secondary_runtimes": []}`) | `migrations/2026-05-28-add-task-intent-to-tasks.sql` |
| 1.4 | `2026-05-28-grant-new-tables.sql` — GRANT SELECT/INSERT/UPDATE on the new tables to `anon, authenticated, service_role` (matching the existing pattern from `2026-05-25-grant-cache-tables.sql`) | `migrations/2026-05-28-grant-new-tables.sql` |

**Definition of done:** Both new tables exist in dev. Row counts match the old tables (~50 + 1). `\d` reveals the expected schema. Old tables untouched.

**Estimated:** 1 day.

---

### Phase 2 — Classifier rewrite

Build the new classification path alongside the old one. Feature-flag the consumer cutover in Phase 3.

| Step | Task | Files |
|---|---|---|
| 2.1 | New Pydantic models: `DatastoreRef`, `TaskTemplateMatch`, `TaskIntent` (NOT a classifier output — emitted by the content-generation LLM) | `infra/classifier/runtime.py` (additive — keep TaskRuntime for now) |
| 2.2 | Update LLM classifier system prompt: input is competencies + `SELECT template_id, capabilities, personas, eval_methods FROM templates WHERE status='built'`. Output schema: `TaskTemplateMatch` only (template_id + persona + no_match fields). **No scenario.** | `infra/classifier/llm_classifier.py` |
| 2.3 | Strict validation: `match.template_id` must be in the active templates list OR `match.no_match_reason` must be set. Pydantic + a custom validator | `infra/classifier/llm_classifier.py` |
| 2.4 | New `resolve_plan_v2(competencies)` — no scenario, no background. Writes to `task_template_match` + reads from `templates`. Returns `ResolvedPlan` (match + template only). Old `resolve_plan` stays callable for backward compat | `generators/task/runtime_resolver.py` |
| 2.5 | Tests: cache hit, miss, stale (`registry_version` bump), no_match path, template_id-doesn't-exist rejection. Polyglot test moves to Phase 3 (intent is generated there, not by resolve_plan). | `tests/test_runtime_resolver_v2.py` (new) |

**Definition of done:** `resolve_plan_v2(["Python (INTERMEDIATE)"])` writes one row to `task_template_match` and returns a `ResolvedPlan` with `template.template_id == "utkrusht-python"`, `match.persona == "backend"`. All new tests pass.

**Estimated:** 2 days.

---

### Phase 3 — Consumer cutover (feature-flagged, parallelizable)

Each consumer migrates behind `USE_UNIFIED_CLASSIFICATION=true`. Per-consumer rollback if needed.

| Consumer | Change | File |
|---|---|---|
| **`generators/task/creator.py`** | Call `resolve_plan_v2(competencies)` for the match + template. Pass `scenario`, `background`, and the resolved template to the content-generation LLM (the existing agent in `generators/prompts/agent.py`). That LLM emits content + `task_intent`. Persist `task_intent` to `tasks.task_intent` at task-creation time. | `generators/task/creator.py` |
| **`generators/prompts/agent.py`** (the content-generation LLM) | **This is the LLM call that sees the scenario.** Inputs: competencies, scenario, background, `plan.template` (capabilities + persona). Outputs: TWO things — (a) task content (description, files, run.sh, compose, tests) AND (b) `TaskIntent` (datastore roles, protocols used, eval_method, secondary_runtimes, optional persona_override). DSPy InputFields include `template_id`, template capabilities, default persona. | `generators/prompts/agent.py` |
| **`infra/e2b/sandbox_eval.py`** | Read `TemplateSpec` from new resolve_plan. Look up the task's `task_intent.secondary_runtimes` from the `tasks` row. **Before** `build_cmd`, iterate the resolved install_cmds and run each + verify. Read `task_intent.eval_method` to dispatch the right runner (`test_suite` → existing path; others stubbed initially). | `infra/e2b/sandbox_eval.py` |
| **`infra/evals.py`** | Persona routing: prefer `tasks.task_intent.persona_override` if set, else fall back to `match.persona`. (Both come from the resolved plan / task row, not from `TaskRuntime.kind`.) | `infra/evals.py` |
| **Reference retriever** (wherever it lives) | Match on `match.template_id` (exact) + `task_intent.datastores` (name overlap) + effective persona (override → match). | TBD — find it during impl |

**Rollback policy:** each consumer's PR ships behind the flag. Smoke-test on ≥3 representative tasks per consumer before flipping the flag. If any consumer regresses, flip its flag back without touching the others.

**Definition of done:** all four consumers running on the new path in dev. Smoke tests pass on a representative spread (single-runtime, polyglot, no_match cases).

**Estimated:** 3 days (parallelizable across consumers).

---

### Phase 4 — Cleanup

Delete the old paths. No coexistence drift.

| Step | Task |
|---|---|
| 4.1 | Drop `competency_combo_classification` and `template_registry` tables (data already copied) |
| 4.2 | Remove `TaskRuntime`, `Kind`, `Runtime` Literal enums from `infra/classifier/runtime.py` |
| 4.3 | Remove `template_name_for_runtime()` helper and any rule-based picker code in `runtime_resolver.py` |
| 4.4 | Remove the old `resolve_plan` shim; rename `resolve_plan_v2` → `resolve_plan` |
| 4.5 | Remove the `USE_UNIFIED_CLASSIFICATION` feature flag from all consumers |
| 4.6 | Delete the old test files that referenced `TaskRuntime` shape; the new tests are the spec |
| 4.7 | Update [`classifier.md`](../task-classifier/classifier.md), [`e2b-templates.md`](../task-classifier/e2b-templates.md), and the [`classifier-flow.excalidraw`](../drawings/task-classifier/classifier-flow.excalidraw) diagram to reflect the new schema as shipped (no more "Proposed" labels on these items) |

**Definition of done:** repo grep for `TaskRuntime`, `Kind` Literal, `template_registry`, `competency_combo_classification` returns zero results outside migration files.

**Estimated:** 1 day.

---

### Phase 5 — Build the second template (signal-driven, post-cutover)

Not part of the migration; this is the **payoff phase**. The new schema makes "what to build next?" a data question.

| Trigger from `task_template_match` data | Action |
|---|---|
| ≥5 `no_match` rows in a week with `missing_capabilities ⊇ {helm, kubectl, terraform}` | Build `utkrusht-infra`, insert row, gate boots automatically |
| ≥3 rows with `intent.secondary_runtimes = ["node"]` on python primaries | Build `utkrusht-python-node` (fat polyglot), update picker preference |
| ≥4 rows with `missing_capabilities ⊇ {torch, transformers}` | Build `utkrusht-python-ml` |
| Build-time on `utkrusht-python` over 90s | Sibling-split into `utkrusht-python-web` + `utkrusht-python-data` |

Each new template is one INSERT into `templates` (with manifest_hash from CI) + the existing classifier prompt automatically considers it. No code change to the picker, ever.

---

## Decision log — why each choice

### Why merge classifier + template_registry at all?

Today's closed `Runtime` enum is a deliberate gate that accumulates as a graveyard. Bun ships and the LLM emits `runtime=node` because Bun isn't in the enum — silent failure for three months until someone debugs. With capability sheets, the rows are the truth; adding a runtime is a row insert, not an enum bump + code change.

### Why `capabilities jsonb` instead of typed columns for everything?

Adding a new capability dimension (e.g. `accelerators`, `network_zones`) shouldn't require a migration. The LLM serializes templates as JSON for matching anyway, so structured columns vs JSONB makes no difference to the LLM's input quality. We keep typed columns only where they're closed enums the LLM picks ONE of per task (`personas`, `eval_methods`) — those benefit from `\d` discoverability + array operators.

### Why per-task intent on `tasks.task_intent` instead of in `task_template_match`?

The match (`combo → template + persona`) is **cacheable per combo** — same competencies always match the same template. The intent (datastore roles, protocols used, eval method) **varies per task** because scenarios differ. Putting them in the same table either bloats the cache (one row per scenario kills the memoization benefit) or duplicates data (intent stored alongside an effectively-immutable match).

The right division:
- `task_template_match` is the combo cache (~50 rows for 339 tasks)
- `tasks.task_intent` is per-task (339 rows, one per task)

### Why scenario is NOT passed to the classifier

Earlier drafts proposed `resolve_plan(competencies, scenario=, background=)`. That was overreach. The content-generation LLM (in `generators/prompts/agent.py`) already sees the scenario — it's the call that generates the actual task content. Passing scenario to the classifier too means we're paying for the same context twice.

What the classifier actually decides:
- `template_id` — 99% determined by competencies. "Python + FastAPI + Postgres" → `utkrusht-python` whether the task is CRUD or migration.
- `no_match` — determined by competencies vs available capabilities. Scenario doesn't change whether `helm` exists in any template.
- `persona` — mostly determined by competencies; rarely varies by scenario (e.g. "Python + Postgres" CRUD vs migration could plausibly want different reviewers).

The rare persona-by-scenario case is handled by `task_intent.persona_override`. The content-generation LLM, which has the scenario in scope, sets the override when the cached match's persona is wrong for THIS specific task. ~95% of tasks: no override. ~5%: scenario-driven correction.

Net effect: the classifier becomes a pure combo→template+persona mapping with a simple cache. Per-task variation lives where it belongs (on the per-task row).

### Why manifest_hash is mandatory before any code lands?

The merged model has one architectural weak point: the capability sheet can lie about the image (Dockerfile bumped Node 20→22, sheet wasn't updated). The LLM matches against the wrong reality.

Without manifest discipline, the merged model rots in year 2. With it, sheets can't lie because CI rejects PRs that update the Dockerfile without re-emitting the manifest. This is non-negotiable.

### Why polyglot install-at-boot instead of dedicated polyglot templates?

Three reasons:
1. **Data-driven template building.** We don't know which polyglot pairs are common yet. Install-at-boot works for any pair without speculation.
2. **Smaller blast radius.** Each new polyglot template is ~6 GiB and adds CVE-patch surface. Don't build them speculatively.
3. **Migration path is clean.** When `secondary_runtimes=["node"]` shows up 3+ times for python primaries, build `utkrusht-python-node` and the picker auto-prefers it. No code change.

The cost is a ~30-60s install regression at session start, paid once per session. Acceptable for a long-running candidate session; acceptable for the eval gate too (it's already not a hot path).

### Why feature-flag Phase 3 instead of a big-bang cutover?

Four consumers; if one regresses, we want to roll back that one without losing the others. The flag lives in each consumer's read site and dies in Phase 4 — short half-life, low cost.

## Risks

| Risk | Mitigation |
|---|---|
| **Phase 0 takes longer than 3 days.** Manifest emission is non-trivial — introspecting `apt list --installed` + `pip freeze` + version probes for each tool. | Time-box at 1 week. If overruns, defer the whole plan; Phase 0 is the gate. |
| **LLM hallucinates a `template_id` that doesn't exist.** | Hard validator in `llm_classifier.py`: reject the output if `match.template_id` is not in the live `templates WHERE status='built'` set. Retry once with explicit error feedback (same pattern as the existing ValidationError retry). |
| **`task_template_match` cache gives wrong persona for outlier tasks.** Same combo, very different scenarios (CRUD vs migration), but persona is cached per-combo. | Per-task override via `task_intent.persona_override` set by the content-generation LLM. If a combo's cached persona is wrong ≥3 times in a quarter, edit the cached row (the human-editable override path). |
| **Phase 1 data migration corrupts the existing 50 rows.** | Run the migration on a fresh dump first; assert row counts match before and after; keep the old tables for 7 days after Phase 4 before truly dropping them. |
| **Feature-flag Phase 3 lingers indefinitely.** | Phase 4 includes "remove the flag" as a checklist item. Add a calendar reminder for 30 days after Phase 3 ships. |
| **Capabilities jsonb shape drift.** Different templates use different keys in inconsistent ways. | Pydantic model `TemplateCapabilities` schema-validates the blob on every read; CI test that loads all `templates` rows and validates each blob. |

## Open questions

| Question | When to answer |
|---|---|
| Is the team committed to investing 3+ days in Phase 0 (manifest CI)? | Before Phase 0 starts. If no, defer the entire plan; the merged model is unsafe without it. |
| Where does the reference retriever live in the codebase? Not obvious from a quick grep. | During Phase 3 — find it, list it in the consumer migration table. |
| How are existing `tasks` rows backfilled for `task_intent`? Sensible defaults (`{"datastores":[], "protocols_used":[], "eval_method":"test_suite", "secondary_runtimes":[]}`), or one-time LLM re-classification ($0.30, ~5 minutes)? | Phase 1 step 1.3 — pick one before writing the migration. Defaults are cheaper; re-classification gives better analytics. |
| What's the rollback story if Phase 4's drop-old-tables breaks something? | Phase 4 step 4.1 keeps the old tables for 7 days post-drop via `ALTER TABLE ... RENAME TO _old`. Drop physically only after 7 days clean. |

## Out of scope (for now)

- **Sibling fragmentation of `utkrusht-python`.** Build-time and image-size thresholds aren't tripping yet. Defer until they are.
- **GPU / accelerator templates.** No demand. Add `needs_gpu` field is in the schema; building one is Phase 5+ if demand emerges.
- **Multi-tenancy on templates.** `organization_id` was removed in 2026-05-26 for classifications. Templates are platform-global the same way.
- **Streaming classification output.** The LLM call is ~2s once per combo; not on a user-facing path. Optimizing not worth it.

## Acceptance criteria — when this plan is "done"

1. Phase 0: CI fails on Dockerfile-without-manifest-update PR; existing `utkrusht-python` has a tracked manifest.
2. Phase 1: `templates` and `task_template_match` exist in dev; row counts match the old tables.
3. Phase 2: `resolve_plan_v2` passes all new tests including no_match, polyglot, and stale-registry-version cases.
4. Phase 3: ≥3 representative tasks run end-to-end on the new path in dev: a single-runtime python+postgres, a polyglot rust+node, and a no_match (infra task).
5. Phase 4: zero references to `TaskRuntime`, `Kind` Literal, `template_registry`, `competency_combo_classification` outside migration files.

When all five are checked, the unified schema is shipped and old paths are gone.

---

## Cross-references

- Naman's PR (the merge proposal): `origin/docs/classifier-template-merge-proposal` (PR #19)
- Current state docs: [`classifier.md`](../task-classifier/classifier.md), [`e2b-templates.md`](../task-classifier/e2b-templates.md)
- Flow diagram: [`classifier-flow.excalidraw`](../drawings/task-classifier/classifier-flow.excalidraw)
- Predecessor proposals (now superseded by this plan):
  - v2 TaskRuntime stress-test additions (`runtimes: list[Runtime]`, `shape`+`specialty`, `datastores` with role, `protocols`, `eval_method`) — folded into `tasks.task_intent` + `templates.capabilities` here
  - Polyglot install-at-boot from [`e2b-templates.md#polyglot`](../task-classifier/e2b-templates.md#polyglot-exception--secondary-runtime-install-at-boot) — kept, now driven by `task_intent.secondary_runtimes`
  - Classifier input signal proposal from [`classifier.md#input-signal`](../task-classifier/classifier.md#input-signal) — **reversed.** The earlier draft proposed `resolve_plan(competencies, scenario=, background=)`. This plan keeps `resolve_plan(competencies)` pure; scenario is consumed by the content-generation LLM (which already sees it) and produces `task_intent` per task. See "Why scenario is NOT passed to the classifier" in the Decision log above.
