# Platform Prerequisites for New Task Categories

> **Status:** Decisions (2026-06-01). `task_intent` removal is owned here in full; the
> template-family and scope-driven-classifier designs are owned by
> [`classifier.md`](../task-classifier/classifier.md) and only summarised here.
> **Why this doc exists:** these are *cross-cutting platform changes* — they apply
> system-wide, not to any one task category. They surfaced while planning the
> [AI-engineering category](./2026-05-27-ai-engineering-task-category.html) (its first
> consumer), but they don't belong inside that plan. Factoring them out keeps the
> category plan focused on what's AI-specific and gives these decisions a single home.

The AI-engineering category depends on all three. None is AI-specific.

---

## 1. Remove vestigial `task_intent`

**Decision:** stop stamping `tasks.task_intent`; do not build routing on it.

**What it is today.** `generators/task/creator.py` stamps `task_intent: {}` on every task
row. It is **read by no business logic** (verified) — `generators/task/runtime_resolver.py`
and `infra/classifier/runtime.py` both carry comments noting the column was dropped after it
landed with no live consumer. It is dead weight: a column that looks like a routing signal
but routes nothing.

**Why it's safe to drop.** The pipeline already routes without it, through two existing
surfaces:

- **The classifier's `ResolvedPlan`** — `template` (which sandbox to boot) + `persona`
  (which eval critic grades it). This is the infrastructure-and-reviewer decision.
- **The repo's own artifacts** — a `docker-compose.yml` in the task repo means "this task
  needs shared infra"; the presence of tests means "grade by running them." Grading is
  implicit in the bundle, not in a stored field.

A new task category that needs to vary task *shape* (e.g. build vs debug vs design) does it
with a **generation-time** value read from the scenario (`answer_schema`), resolved
in-memory and **never stored** — see the AI-engineering plan. The lesson generalises:
**route from the plan + the artifacts + generation-time scenario directives, not from a
stored per-task intent column.**

**The change.**

1. Stop writing `task_intent` in `creator.py` (drop the `{}` stamp).
2. Leave the column in place for now (dropping it is a separate, reversible migration once
   nothing writes it). No code reads it, so removing the write is safe immediately.

**Anti-goal.** Do **not** revive `task_intent` as the dispatch field for any new category.
If you find yourself wanting to store "what kind of task is this" on the row, that's the
signal to use generation-time routing + self-describing artifacts instead.

---

## 2. Template family + build-time inheritance

**Summary.** The Python runtime stops being one fat `utkrusht-python` image and becomes a
small **inheritance family, split by framework family** — `python-base` → `python-web` /
`python-data` / `python-ai-agent` — so heavy dependency pins are isolated by tier and each
image stays lean. (The split is **framework-shaped, not datastore-shaped** — see §3 for why:
scopes name the framework reliably but not the DB engine, and web tiers bundle the common DB
clients anyway.) **Inheritance is a build-time concern only:** the child image is built on
the parent's layers (Docker) and `manifest.py` composes the parent's capability dict at
authoring time, so the stored `manifest.json` is already fully resolved. The `templates`
table stores one self-contained capability sheet per row — **no `parent_template_id` column,
no query-time resolution, no schema change for inheritance.** The mechanism choice
(sibling-`FROM`-common-base vs E2B `from_template()` chaining) is open and should be decided
before the family is built.

**Full design + the mechanism trade-off:**
[`classifier.md` → "Template inheritance is a build-time concern"](../task-classifier/classifier.md).

---

## 3. Scope-driven classification (approach B)

**Summary.** Once more than one Python template exists, competency **name + proficiency** can
no longer pick the right one (an abstract name like "Production Agent Engineering" names no
framework at all). The fix is small and **system-wide**: feed each competency's `scope` into
the classifier and have it pick the **leanest template whose capability sheet is a superset**
of what the scope's framework menu implies. `combo_key` stays a valid cache key
(classification becomes a pure function of competency + scope).

**The signal is the framework family, not the datastore.** A dev spot-check of
`competencies.scope` found scopes **reliably name the framework** (Django/Flask/FastAPI/
langgraph are always present) but **not** a concrete datastore engine — Python - Django
INTERMEDIATE says "complex database queries and optimization" yet never "postgres". That's
why the family (§2) splits by framework family, not DB tier. The cost is therefore **narrow**:
not an audit of all ~60 scopes, but **authoring the 5 new AI competency scopes** so they name
their agent frameworks (langgraph / crewai / pydantic-ai / mock-LLM / observability) — else
they'd route to `python-web` — plus a spot-check that existing framework families are named
(they are).

**Full design (the `Competency.scope` change, the `_user_message` render, the "leanest
superset" prompt rule, the cache-validity argument, and the incomparable-templates →
`no_match` case):**
[`classifier.md` → "Scope-driven matching"](../task-classifier/classifier.md#scope-driven-matching).

---

## Sequencing

These compose as one platform change-set, ideally landed in this order:

1. **Stop stamping `task_intent`** — independent, do anytime (no reader, safe now).
2. **Manifest-hash CI drift-gate** — the durability gate that must exist *before* a second
   template lands (see `classifier.md`).
3. **First template-family split + scope-driven classifier together** — a second template is
   what *makes* scope-driven matching necessary, so they ship as one unit.
4. **Author the 5 AI scopes to name their agent frameworks** (+ spot-check existing scopes name their framework family) — alongside (3), so the new competencies route to `python-ai-agent`.

The [AI-engineering category](./2026-05-27-ai-engineering-task-category.html) is the first
category that exercises all of this end-to-end.
