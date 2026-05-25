# Task Eval Optimizer — design

> Status: Design only. Nothing in this doc is shipped yet.
> Successor / sister doc to [prompt-generator-agent.md](../prompt-generator/prompt-generator-agent.md).
> Recovered design notes from `prompt-generator-optimized.md` §10 (commit `86d1b38`).

## TL;DR

`evals.py` at the repo root is the gatekeeper between **generated tasks** and **Supabase / GitHub publication**. Today it runs one generic LLM critic over every task, regardless of whether the task is a Postgres-modelling exercise, a Kafka consumer, or a Vector DB retrieval question. It also never actually runs the generated code.

This doc proposes three layered upgrades — implementable independently, sequenced by ROI:

| # | Upgrade | Implementation cost | Quality lift | Risk |
|---|---|---|---|---|
| 1 | **Persona-routed critics** keyed by `task_category` | ~120 LOC in `evals.py` | High — biggest single fix | Low |
| 2 | **Empirical sandbox-exec gate** via existing E2B wiring | ~250 LOC, new module | Medium — catches a different bug class | Medium (cost + latency) |
| 3 | **Multi-judge ensemble** for high-stakes generations | ~80 LOC, opt-in flag | Low — diminishing returns | Low |

Plus one supporting prerequisite:

| Prereq | Why it matters |
|---|---|
| Promote `task_category` to a real Supabase column on `tasks` | Audit trail for persona accuracy, queryable analytics, removes runtime re-classification |

---

## Why this matters

The prompt generator (the *upstream* system documented in [prompt-generator-agent.md](../prompt-generator/prompt-generator-agent.md)) produces a template. `multiagent.py` then uses that template plus a competency + background JSON to produce a concrete task — description, input/ask, instructions, code files. Before that task is committed to GitHub and recorded in Supabase, `evals.py` reviews it.

If `evals.py` lets a broken task through, the candidate sees it. There is no second gate. So eval quality directly controls the false-positive rate of the entire pipeline.

The two failure modes we see in practice:

1. **Domain-blind judging** — the generic critic doesn't know what "good" looks like for a Kafka task vs a SQL task vs a React task. A task with a normalisation flaw passes because the critic has nothing in its prompt about third normal form. Same critic prompt judges everything.

2. **No empirical check** — the LLM can think the code "looks right" while the task literally won't run: wrong Python interpreter alias, pinned dep that no longer resolves, port collision, missing `kill.sh`. The judge can't see any of that without executing the code.

Persona routing fixes #1. Sandbox exec fixes #2. Ensemble fixes the long-tail variance in #1.

---

## Current state

### What `evals.py` does today

`evals.py` is 223 lines, two LLM-driven functions:

```python
EVAL_MODEL = os.getenv("EVAL_MODEL", "gpt-5-nano-2025-08-07")
MAX_EVAL_RETRIES = 2

def llm_task_eval(task_json, proficiency, yoe, time_constraint, openai_client, model):
    # Single TASK_EVAL_PROMPT, single model call, JSON-schema-enforced response
    ...

def llm_code_eval(code_data, task_description, openai_client, model):
    # Single CODE_EVAL_PROMPT, single model call, JSON-schema-enforced response
    ...
```

`TASK_EVAL_PROMPT` asks one question: *"Is the scenario realistic and relevant?"* That's it. No category awareness, no domain depth, no execution.

`CODE_EVAL_PROMPT` asks three questions: code is appropriate for assessment, doesn't give the answer, well-structured.

Both go through Portkey → OpenAI Responses API with a strict JSON schema; failures retry up to `MAX_EVAL_RETRIES` times via the regeneration loop in `multiagent.py`.

### What the prompt generator's internal evals do

Different layer, frequently confused. The prompt generator (which produces the *template*, not the task) has its own:

- `prompt_generator/validator.py` — deterministic `ast.parse`, `PROMPT_REGISTRY` key check, format-var presence
- `prompt_generator/agent.py:VerifyPromptSignature` — LLM critic inside the Generate ⇄ Verify loop, capped at 5 iterations
- `prompt_generator/metric.py` — `quality_metric(gold, predicted) → [0, 1]` for DSPy compilation (dead code at runtime since we shipped uncompiled)

**Those evals do not run on the task `evals.py` evaluates.** They only judge the prompt template.

---

## The three upgrades

### 1. Persona-routed critics

**Problem.** One generic critic prompt for every task. A senior DBA would catch a missing `NOT NULL` on a junction-table FK; the generic critic has no reason to look. A senior MLE would catch a chunking strategy that conflicts with the retrieval evaluation question; the generic critic doesn't know what chunking is.

**Solution.** Use the `task_category` already classified upstream by [prompt_generator/classifier.py](../../prompt_generator/classifier.py) to pick a specialised persona prompt at eval time.

#### Persona mapping

| `task_category` | Persona | What this persona looks for |
|---|---|---|
| `DB_ONLY` | senior DBA | normalisation, indexes, FK constraints, query plan implications |
| `SCRIPT_AND_DB` | senior backend | data flow, transactional boundaries, error handling at the I/O edge |
| `APP_AND_DB` | senior backend + API design | request lifecycle, validation layer, status code semantics |
| `LLM_FRAMEWORK` | senior MLE | chunking strategy, retrieval eval design, prompt-injection surface |
| `VECTOR_DB` | senior MLE + index sanity | embedding model fit, dimensionality, distance metric appropriateness |
| `MESSAGING` | senior distributed-systems | ordering guarantees, idempotency, DLQ / poison-message handling |
| `MICROSERVICES` | senior distributed-systems | service boundaries, contract evolution, failure isolation |
| `FRONTEND` | senior UX engineer | accessibility (a11y), semantic HTML, keyboard navigation, ARIA |
| `CONTAINERIZED_APP` | senior platform / SRE | image hygiene, healthchecks, port exposure, kill.sh cleanup |
| `PURE_CODE` | generic senior backend | fallback; same as today's prompt |
| `NON_CODE` | senior PM / eval engineer | rubric clarity, anchor quality, observable behaviours |

#### Wiring

```python
# evals.py — sketch

from prompt_generator.classifier import TaskCategory, classify_task_category, to_competencies

PERSONA_PROMPTS = {
    TaskCategory.DB_ONLY: """You are a senior database administrator with 10+ years of experience in production
    OLTP systems. Review this task for: schema normalisation (3NF unless denormalised
    deliberately), index coverage on FK and query predicates, NOT NULL discipline,
    and whether the task's question rewards good schema design.""",
    TaskCategory.LLM_FRAMEWORK: """You are a senior ML engineer specialising in retrieval-augmented systems.
    Review this task for: chunking strategy alignment with retrieval question,
    embedding model appropriateness, eval methodology, prompt-injection awareness.""",
    # ... one entry per TaskCategory member
}

def _persona_for(competencies: list[dict], proficiency: str) -> str:
    """Return the persona prompt for these competencies, or generic fallback."""
    comps = to_competencies(competencies)
    category = classify_task_category(comps)
    return PERSONA_PROMPTS.get(category, GENERIC_PERSONA_PROMPT)


def llm_task_eval(task_json, proficiency, yoe, time_constraint, openai_client, model, competencies):
    persona = _persona_for(competencies, proficiency)
    prompt = persona + "\n\n" + TASK_EVAL_RUBRIC.format(...)
    # ... existing Responses API call
```

Three notes on this sketch:

- `competencies` becomes a new parameter on `llm_task_eval` and `llm_code_eval`. The call site in `multiagent.py` already has it in scope.
- `PERSONA_PROMPTS` lives alongside `TASK_EVAL_PROMPT` in `evals.py`. ~50–80 lines of prose total.
- The fallback to `GENERIC_PERSONA_PROMPT` for any unmapped category preserves today's behaviour as a baseline.

#### Validation strategy

Hard to A/B test rigorously without a labelled regression set. Two cheap checks:

1. **Re-eval 20 known-good and 20 known-bad historical tasks.** Persona critic should agree with the human verdict more often than the generic critic.
2. **Track per-category pass rates** in Supabase. If persona routing reduces the pass rate for a category (say, `DB_ONLY` drops from 92% → 78%), that's the persona catching things the generic critic missed.

#### Cost

Same model, same number of calls. Marginal extra tokens from persona prompts (~200 tokens each). Effectively free.

---

### 2. Empirical sandbox-exec gate

**Problem.** LLM eval is "vibes by judge." Tasks pass that don't actually run:

- `python` invoked on a container where only `python3` exists.
- A `pip install` line with a pin that no longer resolves on PyPI.
- A `docker-compose.yml` with a port already in use by another service in the stack.
- A `kill.sh` that doesn't actually clean up — leaves daemons running, leaks state into the next deploy.

The LLM critic reads the source and sees code that *looks* correct. It can't see the runtime failure.

**Solution.** After the LLM evals pass, spin up an E2B sandbox (already wired into the codebase for deployment) and try running the task end to end.

#### Gate logic

```
post-llm-eval task
        │
        ▼
┌──────────────────────────────────────┐
│ Boot E2B sandbox (timeout 60s)       │
│ Copy code_files into /task/          │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ If docker-compose.yml exists:        │
│   docker-compose up -d --wait        │
│ Else:                                │
│   ./run.sh                           │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ Probes:                              │
│ - exit code = 0                      │
│ - declared port(s) listening         │
│ - logs contain no FATAL / PANIC      │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ Run kill.sh                          │
│ Verify all processes terminated      │
└──────────────────────────────────────┘
        │
        ▼
   pass / fail
```

A single failure at any step rejects the task even if both LLM evals passed.

#### Bug classes this catches

| Bug | LLM eval verdict | Sandbox verdict |
|---|---|---|
| `python` vs `python3` mismatch | PASS (code looks fine) | FAIL (`/usr/bin/env: 'python': No such file`) |
| Broken pinned dep (`flask==2.x.y` yanked) | PASS | FAIL (`pip install` exits non-zero) |
| Port collision in `docker-compose.yml` | PASS | FAIL (bind error) |
| `kill.sh` missing `docker-compose down` | PASS | FAIL (containers still running after kill) |
| Healthcheck never goes green | PASS | FAIL (`docker-compose up --wait` times out) |
| Wrong file path in `Dockerfile COPY` | PASS | FAIL (`COPY failed: file not found`) |

#### Cost & latency

- ~30–60s per gate invocation, depending on whether `docker-compose up` is involved.
- E2B sandbox cost (varies by tier; currently we use them for deployment so spend is already budgeted).
- Increases task-generation total latency from ~2-3 min to ~3-4 min.

Mitigations: run the gate in parallel with the code-eval LLM call (both gate the same downstream commit); skip the gate when `task_category == NON_CODE` (no executable code to run).

#### Implementation surface

- New module `task_eval_sandbox/runner.py` (~200 LOC) wrapping the existing E2B client.
- New helper in `evals.py` — `sandbox_exec_eval(task_id, code_files, task_category) -> EvalResult`.
- Wire into `multiagent.py` after `llm_code_eval` passes, before the GitHub/Supabase commit.
- Add a `SANDBOX_EVAL_ENABLED` env flag for kill-switching during incidents.

#### Out of scope (for the first version)

- Network-isolated assessment of the candidate's environment.
- Static analysis (ruff/eslint/etc.) — the LLM critic covers this, mostly.
- Coverage measurement of provided tests.

---

### 3. Multi-judge ensemble

**Problem.** Single-judge LLM evals are noisy. A given task can pass or fail depending on temperature setting, model release, and time of day. The variance is high enough that some genuinely-broken tasks slip through and some genuinely-good ones bounce.

**Solution.** Run 3 judges, require 2-of-3 to pass.

#### Configuration

| Judge | Model | Temperature | Persona |
|---|---|---|---|
| 1 | `gpt-5-nano` (current) | 0.2 | `task_category`-routed persona |
| 2 | `gpt-5-nano` | 0.7 | Same persona, higher creativity |
| 3 | `claude-sonnet-4-6` (optional) | 0.4 | Same persona, second model family |

Sequential calls (single-judge cost × 3) or parallelised via `asyncio.gather`. Either way, ~3× the per-task eval cost.

#### When to enable

Not always-on. Three triggers:

- High-stakes generations (e.g. brand-new combos with no prior precedent in Supabase).
- Tasks that previously failed eval and are on their retry.
- Generations near the eval pass threshold (e.g. judge confidence < 0.7).

For routine generations, a single persona-routed judge suffices.

#### Opt-in flag

```python
def llm_task_eval(..., ensemble: bool = False):
    if ensemble:
        return _ensemble_eval(...)
    return _single_judge_eval(...)
```

Caller (`multiagent.py`) sets `ensemble=True` based on the triggers above.

---

## Prerequisite — `tasks.task_category` Supabase column

Section #1 (persona routing) can technically work without this — `evals.py` can call `classify_task_category` at runtime. But three things break:

1. **No audit trail.** If a persona's prompt drifts and starts producing bad evals, we can't query "which `DB_ONLY` tasks failed eval in the last 30 days?" to see the regression in retrospect.
2. **Re-classification fragility.** Competency naming in Supabase can drift (`PostgreSQL` vs `Postgres`). Persisting the classified category at task-creation time means eval-time logic is stable even if the upstream classifier evolves.
3. **Analytics blocked.** Product wants per-category pass rates. Without the column, every dashboard query has to re-classify every row.

#### Migration

```sql
-- New column on existing tasks table
ALTER TABLE tasks
  ADD COLUMN task_category text;

CREATE INDEX idx_tasks_task_category ON tasks(task_category);

-- Backfill — classify each existing task from its competencies column
UPDATE tasks
SET task_category = ...  -- run a one-off backfill job from Python
WHERE task_category IS NULL;
```

The backfill runs through Python (`classify_task_category` over the existing `competencies` array) — not pure SQL — because the classifier is the source of truth.

`multiagent.py` writes `task_category` on every new task creation, post-classification, pre-eval.

#### Schema notes

- Stored as text (enum value, e.g. `'containerized_app'`), not a Postgres enum type — avoids migration friction when `TaskCategory` gains new members.
- Indexed because we'll query by category frequently in analytics.

---

## Sequencing

```
┌─────────────────────────────────────┐
│ Phase 1 — Persona routing           │  ~1 PR, ~120 LOC
│ • Add PERSONA_PROMPTS dict          │  Biggest quality lift
│ • Update llm_task_eval signature    │  Zero schema risk
│ • Update llm_code_eval signature    │
│ • Update multiagent.py call site    │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Phase 2 — Supabase column            │  ~1 PR, migration + backfill
│ • ADD COLUMN task_category           │  Unlocks analytics
│ • Python backfill script             │
│ • multiagent.py writes on create     │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Phase 3 — Empirical sandbox gate    │  ~1 PR, new module
│ • task_eval_sandbox/runner.py       │  Catches LLM blind spots
│ • SANDBOX_EVAL_ENABLED env flag     │  Behind feature flag initially
│ • Wire after llm_code_eval          │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Phase 4 — Ensemble (if needed)       │  ~1 PR, opt-in
│ • _ensemble_eval helper              │  Only if FP rate stays high
│ • Trigger logic                      │
└─────────────────────────────────────┘
```

Phase 1 is the only one that's unambiguously worth doing. Phases 2-4 should be decided based on Phase 1's measurable impact.

---

## Open questions

- **Persona prompt source of truth.** Inline strings in `evals.py` vs `task_generation_prompts/_evals/<category>.py`? Inline keeps reviews simple; per-file makes the personas reviewable independently. Lean inline for v1.
- **Sandbox gate retries.** If the sandbox times out (E2B flake, not task failure), do we retry the gate or pass through? Lean toward 1 retry, then pass through with a warning logged (don't punish the task for our infra).
- **Should the prompt-generator's `task_category` flow into the task's row?** Currently the generator classifies, the multiagent re-classifies. One source of truth would be better — likely the generator's enum, persisted via Supabase as part of the task creation row.
- **What about pr_review_flow and design_review_flow?** Both have their own eval pipelines. Persona routing applies cleanly. Sandbox gate doesn't (no code to run). Out of scope for this doc; revisit after Phase 1 lands.

---

## Future work — not covered here

- **Eval-driven prompt regression detection.** If a category's pass rate dips, autodiff against the last-known-good version of that category's prompt template. Requires Phase 2.
- **Candidate-side eval signals.** Feed back signals from actual candidate sessions (time to complete, hint usage, abandon rate) into the eval as additional features.
- **Cross-judge agreement metrics.** Track when ensemble judges disagree — disagreement clusters are signal about ambiguous task design.

---

## References

- `evals.py` at repo root — current implementation
- [prompt-generator-agent.md](../prompt-generator/prompt-generator-agent.md) — upstream system that produces the templates
- `prompt-generator-optimized.md` §10 — original design notes; recoverable via `git show 86d1b38:docs/research/prompt-generator-optimized.md`
- [prompt_generator/classifier.py](../../prompt_generator/classifier.py) — `TaskCategory` enum + `classify_task_category` (the routing key for §10.1)
- `multiagent.py` — main task-generation orchestrator; integration point
- E2B SDK — `e2b_code_interpreter` package, already in `requirements.txt`
