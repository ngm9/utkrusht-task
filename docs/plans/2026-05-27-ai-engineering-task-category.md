# AI-Engineering Task Category (ADVANCED)

> **Status:** Draft · 2026-05-27 · Rev 2026-06-03 — gate & readiness · Owner: Rohan
>
> This markdown mirrors the canonical HTML
> ([`2026-05-27-ai-engineering-task-category.html`](./2026-05-27-ai-engineering-task-category.html)).
> Sister docs: [unified-classifier-template-schema](./2026-05-27-unified-classifier-template-schema.md) ·
> [task-classifier](../task-classifier/classifier.html) ·
> [e2b-templates](../task-classifier/e2b-templates.html).

> **TL;DR.** Add senior-IC competencies for engineers who've built and operated AI agents. Each task
> is **build-it**: the candidate gets a real agent codebase and builds / extends / hardens / fixes
> the relevant piece — the same task shape the pipeline already produces. The new parts are a
> `python-ai-agent` template (agent frameworks layered on the Python family) and the classifier
> routing to it from the competency. The gate is the **existing persona eval critics + a
> `run.sh` readiness check** (does the scaffold boot — exit 0/non-zero) — **we drop the pytest
> pass/fail step**: it fought the fix-it task shape and turned a non-deterministic real-LLM run
> into a coin-flip gate. The agent calls a **real model**, but only when the **candidate** runs
> it, on **their own key** — so the gate is now **key-free**: no API key sits in a sandbox at
> generation, and no per-gate-run LLM cost. Everything else — output schema, prompt keying,
> two-repo persistence — is reused unchanged. **No new column, no new storage, no new
> task-shape machinery.**

> **Platform prerequisite (cross-cutting, not AI-specific).** This category depends on one
> platform change, documented separately: the Python **template family + build-time inheritance**
> (the substrate `python-ai-agent` is built on). **Routing needs no change** — the existing
> classifier picks `python-ai-agent` from its capability sheet once it's registered; we are *not*
> feeding `scope` into the classifier. See
> [Platform Prerequisites](./2026-06-01-platform-prereqs.md) for the template-family detail. The
> rest of this doc covers only what is AI-engineering-specific.

## What we're trying to do

Build a way to assess engineers who have **actually built and operated AI agent systems in
production** — not just watched the LangChain tutorial. That means four senior-level
competencies, tested the way you'd test a senior hire: hand them a realistic agent codebase
and have them build, extend, harden, or fix the relevant piece with real frameworks.

## What we have today

**The pipeline.** Competency + scenario JSON → the classifier picks a sandbox template → an
LLM generates a task (description + starter code) → the gate runs the persona critics and a
sandbox boot check → the task is stored to Supabase + GitHub. That machinery is solid and we
reuse all of it.

**The competencies.** ~60 tech stacks across Beginner / Basic / Intermediate. A handful are
AI-flavored — LangChain, LlamaIndex, RAG, Vector Databases, Prompt Engineering — but all at
framework-tutorial depth ("wire a chain", "build a basic RAG").

**The one task shape.** Every task the pipeline makes today has the same form: *here's a repo
with empty slots → write the code → we check it boots → ready/not-ready.*

**Things that already exist** (so we don't rebuild them):

- The **`utkrusht-python` template** already bundles `langchain llama-index openai anthropic`
  + every web framework + DB clients, has **Docker-in-Docker** (tasks bring their own
  `docker-compose.yml`), tops up per-task `requirements.txt` at gate time, and even pre-bakes
  an embedding model (`.fastembed_cache`). It is the substrate the Python template family
  inherits from.
- The **E2B build flow** (`infra/e2b/templates/…/template.py` + a declarative `manifest.json`
  capability sheet, manifest-hash landed in `45d398f`) already supports composing one template
  from another at build time — the mechanism inheritance rides on.
- The **classifier** (LLM-based, `infra/classifier/llm_classifier.py`) already maps a competency →
  a template by reading the template capability sheets, and routes the eval critic by `persona`.
  **Used as-is** — registering `python-ai-agent` (with its agent-framework capability sheet) + the
  new competencies is enough for it to route there; no classifier change.
- The **gate** itself: the **persona-routed eval critics** (`llm_task_eval` + `llm_code_eval`)
  and the **E2B sandbox check** (`infra/e2b/sandbox_eval.py` — boot, `docker compose up`,
  `pip install`). We reuse these and have the sandbox check run `run.sh` for deployment-readiness
  (see [the gate](#the-gate--realistic--deployable-at-generation-time)). **We do not run
  `pytest` at the gate** — see why below.
- The **output schema** (`ANSWER_CODE_SCHEMA`), the **prompt keying**, and the **two-repo
  persistence** (template repo + answer repo) — reused unchanged.

## The problem

1. **No senior-IC AI competencies.** Our AI competencies test "can you use this tool," not
   "have you shipped and operated an agent." There's no signal for someone who's debugged a
   runaway agent at 3am or argued about a context budget.
2. **The candidate's sandbox has no LLM access.** An agent's whole job is to *call a model*.
   So for the candidate to test their own work, the sandbox needs a working LLM endpoint during
   their session. Today there isn't one. (Note: the *gate* does not need this — it never runs
   the agent; see [the gate](#the-gate--realistic--deployable-at-generation-time).)

## How we're solving it

Three moves, all inside the existing pipeline — no forked flow:

1. **Four competencies** (see below) — skill-areas like `Microservices`, not technologies
   like `Django`.
2. **A `python-ai-agent` template that inherits from the Python family** — it layers ~6 agent
   frameworks (langgraph, pydantic-ai, crewai, mem0, langfuse, openinference) on the shared
   base; long-tail libs come per-task via `requirements.txt`. Inheritance keeps each image lean
   and isolates agent-framework pins from the web/data tasks. The sandbox env carries a **real
   LLM API key** (routed through the existing Portkey gateway) so agent code runs for real —
   see [LLM access](#llm-access--the-one-new-piece-of-wiring).
3. **One build-it task shape** — give the candidate an agent codebase to build / extend /
   harden / fix. It's the existing task shape with agent frameworks added; reuse
   `ANSWER_CODE_SCHEMA` and the existing prompt keying. The **existing gate** (persona eval
   critics + the E2B build/test check) proves each task builds and its tests pass at generation
   time — unchanged from every other task.

## Four competencies (topic-style)

The original brief listed seven items; one — true multi-modal / vision — is **out of scope** for
now, leaving six. Of those, #1 "building AI systems" is an umbrella (testing it directly collides
with everything), and #6 "agent architecture (memory, orchestration, tool use)" is an explicit
superset of #2/#3/#4/#5. **Decision: four distinct task-surfaces, each covering one or more of the
six.** Topic-style naming (matches
`Vector Databases`, `Prompt Engineering`); these are **skill-areas** like `Microservices` /
`System Design`, not technologies.

| Competency (topic-style) | What it tests | Covers from the brief |
|---|---|---|
| **Production Agent Engineering** | Build, ship, and operate a single agent reliably — retries, fallbacks, cost ceilings, observability, memory. | #1 building AI systems, #2 production agents, memory/reliability of #6 |
| **Multi-Agent Systems** | Orchestration, handoffs, multi-step pipelines, and the coordination failures unique to multi-agent systems. | #3 multi-agent systems, orchestration of #6 |
| **Context & Cost Engineering** | Token budgets, context-window management, pruning, caching, cost ceilings, prompt-size discipline. | #4 context engineering |
| **Tool Use for Agents** | Tool schemas, function calling, tool routing, argument validation, and tool-call error handling. | #5 tool use, tool slice of #6 |

**Why these four:** #1 is the umbrella (folded into Production Agent Engineering, not its own
competency, to avoid dedup-collision); #6 is decomposed across Production (memory), Multi-Agent
(orchestration), and Tool Use (tools) rather than kept as a superset that would make us pay for
the same signal three times. Every one is a distinct task-surface a testmaker would assign
separately.

### How a competency pins its framework

A competency is a skill-area, but a *task* has to be concrete: someone must pick the framework
(the reference solution and hidden tests are written against one), and two candidates assessed on
the same competency should face the **same** framework — otherwise their scores partly reflect
which tool they happened to know, not the skill. A 25-minute task in an unfamiliar framework
tests ramp-up speed, not architecture. So the competency does **not** stay open ("commits to
none" just defers the choice to the scenario): it **commits to a primary framework**, disclosed
to the candidate up front.

| Layer | Owns |
|---|---|
| **Competency** | commits to a **primary framework** (the canonical one for the skill) + a short list of explicitly-allowed alternates. The comparability anchor and the default. |
| **Scenario** | defaults to the competency's primary; picks an allowed alternate *only* when we deliberately want cross-framework coverage — and the pick is disclosed in the brief via `**Stack:**`. |
| **Template** | installs the whole allowed set, so any allowed pick just runs. |

The scope text still says framework-API trivia is not the bar — the skill is the architecture —
but the framework is **pinned and disclosed** so the candidate isn't ambushed by an unfamiliar
API and scores stay comparable. (Strictest variant: exactly one framework per competency, no
alternates — a fine place to start; add alternates only once we actually want coverage.)

| Competency | Primary framework |
|---|---|
| Production Agent Engineering | LangGraph + LiteLLM |
| Multi-Agent Systems | CrewAI *(alt: LangGraph)* |
| Context & Cost Engineering | framework-light: LiteLLM + tiktoken + Mem0 |
| Tool Use for Agents | Anthropic tool use, via LiteLLM |

## Task examples — build-it, not memo-it

Every task is a real codebase the candidate works inside. Candidate writes 100–300 lines using
real agent frameworks. The generation-time gate runs `pytest` — with the agent calling a real
LLM through the sandbox's API key — to prove the task builds and its tests pass before it ships.

| Competency | Stack candidate uses | What they build & how it's graded |
|---|---|---|
| Production Agent Engineering | LiteLLM + FastAPI + Anthropic/OpenAI SDKs + Langfuse | Customer-support reply agent with model fallback, cost ceiling, streaming, and observability. Tests assert avg cost < $0.05/ticket, ≥8/10 eval cases correct, graceful fallback on 5K-token outlier. |
| Tool Use for Agents | Anthropic tool use or OpenAI function calling, via LiteLLM | Rewrite 23 broken tool definitions + add a RAG router for the tool catalogue. Tests assert wrong-tool rate < 10% on a 100-query eval set. |
| Multi-Agent Systems | CrewAI or LangGraph | Code-review crew (Planner→Reviewer→Critic→Tiebreaker), where Tiebreaker is NOT just another LLM call. Tests cover verdict accuracy, latency, cost, deterministic tiebreaker firing. |
| Context & Cost Engineering | fastembed + tiktoken + Mem0 + Anthropic SDK | Context-budgeting middleware + long-term memory around a provided agent. Tests assert p95 prompt size ≤ 12K tokens AND quality stays ≥ baseline on 30 Q&A pairs. |

**Every task is build-it** — a real coding session, not a write-a-memo exercise.

## Two worked examples (scenario → task)

To make "build-it" concrete, here are two scenarios as they'd appear in a scenarios file, plus a
sketch of the task the pipeline generates from each — showing the invariant-style tests, the real
key at gen time, and the LLM-free `run.sh`.

### Example 1 — Production Agent Engineering

**Scenario** (free-form string in the scenarios file):

```
**Stack:** LangGraph + LiteLLM (Anthropic primary, OpenAI fallback)
**Domain:** customer-support reply agent for an e-commerce SaaS
**Candidate writes:** agent/policy.py (model fallback + cost ceiling); bound the loop in agent/graph.py
**Provided broken:** an unbounded graph loop; policy hooks stubbed (NotImplementedError);
                     the agent hard-crashes when the primary model 5xxes
**Tests verify:** loop terminates in <= 6 model calls; on primary 5xx the agent falls back to the
                  secondary model via the LiteLLM router (not a try/except swallow); projected
                  per-ticket cost <= $0.05 enforced BEFORE the call; >= 8/10 canned tickets get a
                  non-empty, on-policy reply
**Senior signal:** fallback via the router, cost ceiling pre-call, bounded loop
```

**Generated task** (`ANSWER_CODE_SCHEMA` → `{files, steps}`):

```
agent/
  graph.py           # LangGraph graph — loop node UNBOUNDED (candidate bounds it)
  policy.py          # STUB: enforce_budget() + choose_model() raise NotImplementedError
  tools.py  prompts.py    # working
tests/test_agent.py  # hidden, invariant-style
fixtures/tickets.jsonl    # 10 tickets + allowed policy labels
run.sh               # readiness self-check (no model call)
requirements.txt     # langgraph litellm anthropic openai pytest
.env.example         # ANTHROPIC_API_KEY= / OPENAI_API_KEY=
```

- **Candidate brief:** "This support agent runs away (unbounded loop) and hard-crashes when the
  primary model 5xxes. Make it production-safe: bound the loop, add LiteLLM model fallback,
  enforce a per-ticket cost ceiling, keep replies on-policy. Put your API key in `.env` and run
  `./run.sh`."
- **Hidden tests (invariants — run at gen time with our key):** `test_loop_bounded` (a model that
  always says 'continue' → ≤ 6 calls, no hang); `test_fallback_on_5xx` (primary raises 529 → the
  router uses the secondary and a reply is produced — asserted via the router/call-log, not exact
  text); `test_cost_ceiling` (a projected >$0.05 call is blocked pre-call); `test_quality`
  (≥ 8/10 fixture tickets → non-empty reply with an allowed policy label).
- **`run.sh` (deploy readiness, LLM-free):** `python -m agent --selfcheck` — imports the graph,
  checks a key var is set, dry-loads prompts/tools — exit 0. No model call.

### Example 2 — Tool Use for Agents

**Scenario:**

```
**Stack:** Anthropic tool use, via LiteLLM
**Domain:** internal "ops assistant" with a catalogue of 23 tools (deploy, rollback, query-logs,
            page-oncall, ...)
**Candidate writes:** fix the 23 tool schemas in tools/schemas.py; implement tools/validate.py
                      (arg validation); implement tools/router.py (RAG router over the catalogue,
                      using the baked fastembed)
**Provided broken:** 23 tool dicts with planted bugs (missing required, wrong JSON-schema types,
                     name typos, free-text where enums belong); a router stub that dumps ALL 23
                     tools into context
**Tests verify:** every schema validates against the tool spec; a missing required arg is rejected
                  BEFORE dispatch; the router returns <= 5 tools and includes the gold tool for
                  >= 90% of a 100-query eval set; end-to-end wrong-tool rate < 10%
**Senior signal:** validation at the boundary, RAG routing instead of all-tools-in-context
                   (context-cost discipline)
```

**Generated task:**

```
tools/
  schemas.py     # 23 buggy tool defs (candidate fixes)
  validate.py    # STUB: validate_args() raises NotImplementedError
  router.py      # STUB: returns ALL tools (candidate makes it a fastembed RAG router)
  catalogue.md   # human tool descriptions (router corpus)
agent.py         # working; calls the model with router + validate
tests/  test_schemas.py  test_validation.py  test_router.py   # hidden, invariant-style
fixtures/eval_queries.jsonl    # 100 queries -> expected tool name
run.sh   requirements.txt (litellm anthropic fastembed pytest)   .env.example
```

- **Candidate brief:** "The ops assistant calls the wrong tool ~30% of the time and sometimes with
  malformed args; all 23 tools are shoved into every prompt. Fix the schemas, validate args at the
  boundary, and build a RAG router that returns only the relevant tools per query."
- **Hidden tests (invariants):** `test_schemas_valid` (all 23 validate; each has `required`; legal
  JSON-schema types); `test_validation_rejects` (a missing required arg raises before dispatch);
  `test_router_topk` (≤ 5 tools, gold tool present for ≥ 90% of the 100 queries);
  `test_wrong_tool_rate` (end-to-end, our key, wrong-tool rate < 10% with a tolerance band).
- **`run.sh`:** import the schemas and assert all validate, build the fastembed index over
  `catalogue.md`, exit 0. No model call.

## The task shape: build-it

Every task gives the candidate a real agent codebase and asks them to **build / extend / harden
/ fix** the relevant piece. That is the same shape the pipeline already produces (a repo with
incomplete or buggy code the candidate completes) — the agent-specific part is only that the
repo uses agent frameworks and calls a [real LLM](#llm-access--the-one-new-piece-of-wiring)
through the sandbox's API key.

Because it is the existing shape, it reuses the existing machinery:

- **Output**: the existing `ANSWER_CODE_SCHEMA` (`{files, steps}`) — an agent task is a code
  task with more files (agent code, candidate stubs, tests, config).
- **Prompt selection**: the existing `(competency, proficiency)` keying — one `ai_agent_build`
  prompt with the competency's scope injected.
- **Routing**: the classifier's `ResolvedPlan` (`template` + `persona`) — unchanged.
- **Gate**: the persona eval critics + `template.build_cmd` / `test_cmd`; infra boots from the
  task's own `docker-compose.yml`.
- **Persistence**: the existing template-repo + answer-repo + `tasks` row.

## Pipeline walkthrough, top-to-bottom

**1. CLI entry — unchanged.** `cli/main.py::generate_tasks`. Same inputs (competency JSON,
background JSON, scenarios JSON).

**2. Classifier — routes to `python-ai-agent` as-is (no change).** The existing classifier routes
the AI competencies to `python-ai-agent` with **no code change**. It's LLM-based and reads the
template capability sheets, so once `python-ai-agent` is registered (its sheet lists the agent
frameworks) and the competencies exist, "Production Agent Engineering" matches it the same way
every other competency matches its template. We are *not* feeding `scope` into the classifier —
that was a considered enhancement we're skipping. (Assumption: the classifier distinguishes
`python-ai-agent` from the leaner `python` base by their capability sheets; if AI tasks ever
mis-route to base `python`, that's the point to revisit feeding `scope`.)

**3. Scenario load — read the directives.** Scenarios stay free-form strings but gain
load-bearing headers:

```
**Stack:** LangGraph + LiteLLM
**Domain:** customer support for e-commerce SaaS
**Candidate writes:** agent.py
**Tests verify:** loop bounded, fallback on primary-model failure, cost < $0.05/ticket
**Senior signal:** model fallback via LiteLLM (not try/except), cost ceiling pre-LLM-call
```

`**Stack:**` fixes the concrete framework for this task; the rest is guidance for the gen LLM.
There is **no `**Answer:**` directive** — every task is the one build-it shape.

**4. Prompt selection — one agent prompt × competency scope.** Reuse today's
`(competency, proficiency)` keying. One `ai_agent_build` structure prompt, with the competency's
scope snippet injected for domain — 1 prompt + 5 scope snippets = **6 files**:

```
task_generation_prompts/Advanced/
  ai_agent_build_advanced_prompt.py        # the one build-it structure prompt
  _scope/                                  # competency scope snippets (one per competency)
    production_agent_engineering.py
    multi_agent_systems.py
    context_and_cost_engineering.py
    tool_use_for_agents.py
```

**5. Generation LLM — fills `ANSWER_CODE_SCHEMA`.** The LLM fills today's `ANSWER_CODE_SCHEMA`
(`{files, steps}`) — an agent task is a code task with more files (agent code + stubs + tests +
config). No new schema.

**6. Gate — persona critics + run.sh readiness (no pytest).** Boot `python-ai-agent`, run the
**persona eval critics** (in the pipeline process), then **`run.sh`** in the sandbox (boots the
env — deps, services — and exits 0 if the scaffold is ready). That's it. **No `pytest` step**
— see [the gate](#the-gate--realistic--deployable-at-generation-time) for why, and
[readiness](#readiness--runsh--the-deployability-check) for what `run.sh` proves. The gate
never runs the agent, so no LLM key is in the sandbox at generation.

**7. Retry feedback — agent-specific failure modes.** Today: a failing task is fed back to the
LLM with "fix it." For agent tasks we surface the gate's verdict kind — see
[Retry feedback](#retry-feedback--failure-kinds).

## The sandbox: the `python-ai-agent` template

The AI category runs in `python-ai-agent`, the agent-focused member of the Python **template
family** (the family is split by *framework family* — `python-base` → `python-web` /
`python-data` / `python-ai-agent` — not by datastore tier; each tier bundles the common DB
clients). The family split, how build-time inheritance works, why the DB needs no schema change
for it, and the open mechanism choice are all **platform concerns** — see
[Platform Prerequisites §2](./2026-06-01-platform-prereqs.md) and
[the classifier doc](../task-classifier/classifier.html#choices). This section covers only what
`python-ai-agent` adds on top.

### What `python-ai-agent` adds (AI-specific)

1. **~6 agent frameworks** on top of `python-llm`: `langgraph pydantic-ai crewai mem0 langfuse
   openinference-instrumentation` (langchain / llama-index / openai / anthropic are already in
   `python-llm`).
2. **Use the already-baked `fastembed`** (from `python-llm`) for embeddings in retrieval /
   context tasks — do *not* add `sentence-transformers` (it drags in torch, ~2–3GB).
3. **A real LLM API key in the env** (routed through Portkey), so agent code can call a model
   from inside the sandbox — the one new piece of wiring. See
   [LLM access](#llm-access--the-one-new-piece-of-wiring) below.
4. **Long-tail libs** (a task that wants autogen/dspy/…) go in *that task's* `requirements.txt`
   — topped up at gate time, as today.

> **The dependency-conflict question is scoped to this one image.** crewai/langgraph/mem0 carry
> heavy, opinionated pins (pydantic-core, langchain-core, httpx). Because the family isolates
> them in `python-ai-agent`, the question is just "does `python-ai-agent` build green and pass
> its own task suite?" — the web/DB tasks on the leaner base are untouched.

### TypeScript / Mastra?

Out of scope for now. Python covers 80%+ of agent work; a parallel TS template doubles
maintenance for marginal coverage. Revisit when usage justifies it.

## LLM access — a real model, no mock

An agent's whole job is to *call a model*, so its code has to reach an LLM to run at all. We use a
**real model** through the existing Portkey gateway — the same path the pipeline already uses to
call OpenAI/Anthropic. No mock, no fixtures. Whoever *runs* the agent supplies the key:

- **At generation, we run it** (the gate exercises the agent), so it uses **our** key. This is the
  one place our key sits inside a sandbox — and it is *not* for the eval critics (those run in the
  pipeline process and call Portkey directly, as today), it is so the *agent's own* model calls
  work while `pytest` exercises it.
- **During the candidate's session, the candidate runs it**, so it uses **their** key (set in
  `.env` / the session env; the SDKs read it — no code change in the repo). Per-candidate API
  spend stays off us.

Because the model is real, tests grade **invariants** — the loop terminates within N steps, a tool
was called with valid args, cost ≤ ceiling, the output is parseable, quality ≥ baseline with a
tolerance band — not exact strings. The gen-time cost ceiling is the one knob left to set (see
[Open questions](#open-questions)).

## The gate — readiness + correctness, at generation time

An agent task runs the same gate every task does, with one addition you flagged: it runs `run.sh`
at **generation time**, so a task that won't deploy is caught while we can still regenerate it.
Three things happen, all at gen time; any failure retries with feedback:

| Step | What it does — and why it's its own thing |
|---|---|
| **1. Persona eval critics** (`generators/task/evaluator.py`) | `llm_task_eval` + `llm_code_eval` — is the task realistic, well-scoped, the right difficulty. Run in the pipeline; nothing in the sandbox. |
| **2. `run.sh` — readiness** (the gate at gen time; `sandbox_manager.py` at deploy) | Brings the *whole* environment up — `pip install`, `docker compose up` the services, whatever the task needs — then a readiness probe, and **exits 0 (ready) / non-zero (broken)**. This is the candidate-facing boot script. You're right that it does "everything related to the task," **including the `pip install`** — so that isn't a separate gate step; it lives *inside* `run.sh`. |
| **3. `pytest` — correctness** (`infra/e2b/sandbox_eval.py`) | Runs the **hidden test suite** against the reference solution to confirm the task is actually solvable. This is the *one* thing `run.sh` can't do, because the hidden tests are **secret** — they live in the private answer repo, never in the candidate repo that `run.sh` ships inside. So the gate injects them and runs `pytest` itself, only at gen time. The agent calls a real model here, so this is the one place **our** key is in the sandbox. |

So it isn't three setup steps — it's **two questions**: *"does the environment boot?"* (`run.sh`'s
exit code, candidate-facing, no secrets) and *"does the reference pass the hidden tests?"*
(`pytest`, gate-only, secret). `pip install` is just part of booting, so it belongs to `run.sh`.
The `run.sh` in step 2 is the *same* script the deploy path runs when the task goes live
(`sandbox_manager.py` raises if it exits non-zero), and a wall-clock timeout wraps every command so
a runaway loop fails fast.

### What "ready" means for an agent task (the exit-0/1 signal)

For a web task `run.sh` ends by polling `/health` — a running service answers → exit 0 → "ready."
An agent build task has **no running service** to poll, *and* its scaffold is deliberately
incomplete (the candidate hasn't filled the stubs yet), so it can't complete a real run either. So
"ready" means *"the environment is set up and the scaffold loads, so the candidate can start
coding"* — the agent-equivalent of `/health`:

```bash
#!/usr/bin/env bash
set -e                                # any failure -> non-zero exit -> "not ready"
pip install -r requirements.txt       # deps the scaffold + candidate need
docker compose up -d --wait           # vector DB / tool server, if the task has them
python -m agent --selfcheck           # imports the package, loads config / prompts / tool defs,
                                      # pings the services. Does NOT call the LLM and does NOT run
                                      # the agent loop (the stubs aren't filled in yet).
echo "ready"                          # reached only if every step above exited 0
```

Exit **0** → shown as **ready**; any non-zero (bad dep, service down, scaffold import error) →
**not ready** — the same contract as a web task, with a self-check in place of the HTTP poll. The
probe per task family:

| Task family | Readiness probe (exit 0 = ready) |
|---|---|
| Web service (today) | `curl -sf localhost:8000/health` returns 200. |
| Agent wrapped as a service | Same — `curl` the agent's `/health` / `/invoke` endpoint. |
| Agent as a CLI / loop | `python -m agent --selfcheck` — imports + config + services load. No model call. |
| Agent as a library | A tiny script imports the entry point, asserts deps + config load, exits 0/1. |

It stays **LLM-free**, so it needs no key — the first real model call happens later, on the
candidate's key, once they've filled the stubs and run the agent themselves. (`run.sh` shape is
already persona-driven — e.g. `persona="pm"` ships no `run.sh` at all.)

## Retry feedback — failure kinds

`evaluator.py::build_retry_feedback` already re-renders the gate's verdict and re-feeds the
failing candidate JSON so the LLM patches its own output. For agent tasks the verdicts worth
distinguishing are:

| Gate verdict | Feedback to gen LLM |
|---|---|
| `test failed` | "Tests fail. stderr: `...`. Patch the code (or the test) so the suite passes." |
| `pip_failed` | "`pip install -r requirements.txt` failed — a dependency is wrong or conflicts. Fix the requirements." |
| `compose_failed` | "`docker compose up` failed — the task's service containers don't start. Fix the compose file." |
| `timeout` | "The agent exceeded the sandbox timeout — likely an unbounded loop. Add the step/call ceiling the scenario asks for." |
| `task / code eval failed` | The persona critic's `blocking_issues` are passed back verbatim (existing behaviour). |

## Decisions locked in

| Area | Decision | Why |
|---|---|---|
| Top-level flow | Single unified flow — the existing pipeline. **Not** a new `flows/ai_agent/` folder. | Agent tasks share inputs, schema, gate, and persistence with regular tasks; only the template + prompt differ. |
| Proficiency level | Use the existing `ADVANCED` tier. **No migration.** Just create `task_generation_prompts/Advanced/`. | ADVANCED is already in `PROFICIENCY_LEVELS`, the loader scans `Advanced/`, and the only proficiency CHECK already allows it. Proficiency is text+CHECK, not an enum. |
| Template (AI-specific) | Runs in `python-ai-agent`, the agent member of the Python family, adding ~6 agent frameworks. | Isolates heavy agent pins (crewai/langgraph/mem0) from web/DB tasks. *The family split + inheritance are platform decisions — see [Platform Prerequisites](./2026-06-01-platform-prereqs.md). Routing uses the existing classifier, unchanged.* |
| LLM access in sandbox | **A real model via Portkey, no mock.** Our key when *we* run the agent (the gen-time gate — only so the agent's own calls work during `pytest`, not for the eval critics); the candidate's key when *they* run it (their session). `run.sh` readiness stays LLM-free. | Agent code must call a model to run; a real key matches how the pipeline already calls LLMs. Tests grade invariants, not exact output; per-candidate spend stays on the candidate. |
| Gate | Reuse the existing gate unchanged: persona eval critics + the E2B build/test check. **No two-run gate, no per-shape dispatch.** | An agent task is the existing code shape; the existing gate already proves build + tests. The only addition is the real API key in the sandbox env. |
| Test style | Tests assert **invariants** (termination, valid tool-calls, cost ≤ ceiling, parseable output, quality ≥ baseline with tolerance), not exact model output. | A real LLM is not perfectly deterministic; grading invariants keeps the gate (and candidate grading) stable. |
| Embeddings in the image | Use the already-baked `fastembed` for retrieval / context tasks; do **not** add `sentence-transformers`/torch. | torch is ~2–3GB and would bloat the image for every Python task, including junior CRUD. |
| Competency set | **4 distinct task-surfaces:** Production Agent Engineering, Multi-Agent Systems, Context & Cost Engineering, Tool Use for Agents. | Covers the agent-build JD bullets; #1 is the umbrella (folded into Production), #6 the superset (decomposed across Production/Multi-Agent/Tool Use). No dedup-collision. |
| Competency naming | Topic-style (`Production Agent Engineering`). | Matches the repo's convention. Rohan's call. |
| Task shape | **One shape: build-it.** No shape selector, no new output schema. Reuse `ANSWER_CODE_SCHEMA` + existing prompt keying. | All 7 JD needs are best tested by having the candidate build/extend/harden/fix a real agent codebase — the existing task shape. Debugging is a variant of it (a planted bug). |
| Framework selection | The competency **commits to a primary framework** (+ a short allowed set), disclosed to the candidate; the scenario defaults to it and picks an alternate only for deliberate coverage; all are installed in the template. | A skill-area still, but pinned so tasks under one competency are comparable and the reference + hidden tests share common ground. "Commits to none" just defers the choice and lets scores reflect tool-familiarity. |
| Hidden-artifact storage | Reuse the existing private **answer repo** for the reference solution + hidden tests. | The answer repo is already the private channel for solution artifacts; no new storage needed. |
| TypeScript / Mastra | Out of scope for now. Python only. | Python covers most of the ecosystem; a TS template doubles maintenance. Revisit later. |
| Scenario files | One ADVANCED scenarios file per competency (as today), all `agent_build` shape. | One shape ⇒ no per-shape scenario split needed. |

## Files: created / modified

### Created

```
migrations/
  2026-05-28-seed-competencies-ai-engineering.sql  # 4 competency rows (scope text) — the ONLY DB change
  + a templates-seed row for python-ai-agent (platform prereq, see classifier doc)
  # the only DB change — no new task columns

task_generation_prompts/Advanced/                  # the folder the loader already scans
  ai_agent_build_advanced_prompt.py                # the ONE build-it structure prompt
  _scope/  production_agent_engineering.py + 3 more  # one per competency

data/generated/scenarios/
  one ADVANCED scenarios file per competency (all agent_build shape)

data/generated/input_files/                        # competency + background per competency, ADVANCED
  input_production_agent_engineering/advanced/ + 3 more


docs/task-classifier/ai-engineering-category.md

tests/
  test_ai_agent_prompt_contract.py
  test_sandbox_llm_key.py   # asserts the gate injects the API key into the sandbox env
```

### Modified

```
infra/e2b/templates/python-{base,web,data,ai-agent}/  # the framework-shaped family (platform prereq);
  template.py + manifest.json                        #   python-ai-agent inherits + agent frameworks
infra/e2b/sandbox_eval.py                        # run run.sh (deployment-readiness) in the gate + make our LLM key reachable for the agent's own calls during pytest
migrations/...templates seed                     # insert the python-ai-agent capability row + bump registry_version
generators/prompts/slugs.py                      # 5 new competency aliases
generators/task/evaluator.py                     # (optional) agent-aware retry feedback labels
README.md / CLAUDE.md                            # ADVANCED ai-engineering category
```

> Note: the **classifier is unchanged** — no `scope` input, no `leanest-superset` rule; registering
> `python-ai-agent` + the competencies is enough for it to route. `persistence.py`, `gate.py`, and
> `creator.py` are unchanged. The template-family rows are a
> [platform prerequisite](./2026-06-01-platform-prereqs.md), shared with the wider system.

## Phases

### Phase 0 — Resolve the unknowns before any code

Goal: clear the questions that change scope.

- Run the **dependency-conflict test**: build `python-ai-agent` (+ the 6 agent frameworks) → run
  its own task suite → green? (The family isolates these pins, so this scopes the risk to one
  image.)
- Confirm the **API-key injection path**: get a real key (via Portkey) into the E2B sandbox env
  and verify agent code can call the model from inside the sandbox — and decide the **cost
  ceiling** per gate run.
- Author the 4 competency `scope` texts (they define each competency, name its **primary
  framework**, and are injected into the build prompt). These are *not* a classifier input —
  routing is the existing classifier.
- Answer the [open questions](#open-questions).

**Checkpoint —** a green `python-ai-agent` build, a working in-sandbox LLM call, + the 5 scopes
authored gate Phase A.

### Phase A — MVP slice (one competency, end-to-end)

Goal: generate a build-it agent task for ONE competency, gate-verified, persisted. Everything
else iterates on this.

- DB change: the 4 competency-seed rows only — no new columns.
- Seed the `python-ai-agent` capability row + the new competencies so the existing classifier
  routes to it; bump `registry_version`. **No classifier code change.**
- Wire the gate to run `run.sh` (deployment readiness) and make our LLM key reachable in the
  gen-time sandbox so the agent's own calls work during `pytest` (`infra/e2b/sandbox_eval.py`);
  verify from inside E2B.
- Author the `ai_agent_build` prompt + ONE scope snippet (`production_agent_engineering.py`) +
  ONE scenario (the scheduling-agent), reusing the existing `(competency, proficiency)` prompt
  keying + `ANSWER_CODE_SCHEMA`.
- Run the pipeline once. Verify: candidate template repo, answer repo populated with the
  reference + hidden tests, the gate (persona eval critics + `pytest`) passes.

**Checkpoint —** end-to-end agent task generation works on dev Supabase on the existing
`utkrusht-python` image (agent frameworks installed per-task via `requirements.txt`; real API key
in the sandbox env — no image rebuild needed yet).

### Phase B — Build the `python-ai-agent` template

Goal: the agent frameworks are pre-installed in a dedicated image so gate runs don't pip-install
them every time.

- On the `feat/utkrusht-python-fat-template` worktree, define `python-ai-agent` with `FROM
  python-llm` + the 6 frameworks; compose its `manifest.json` from the parent's; rebuild;
  recompute manifest hash.
- Build `python-ai-agent` on its own and run its task suite (the conflict gate scoped to one
  image). Insert its resolved capability-sheet row into `templates` and bump `registry_version`.
- Until built, the agent frameworks install via per-task `requirements.txt` — so Phase A doesn't
  block on this.

**Checkpoint —** agent_build gates are fast (no per-run framework install); the existing classifier
routes AI competencies to `python-ai-agent` via its capability sheets.

### Phase C — The remaining text competencies

Goal: the 3 remaining text competencies (Multi-Agent Systems, Context & Cost Engineering, Tool
Use for Agents) each have scope + 4–6 scenarios + a gate-verified task.

- Author 3 more scope snippets + 4–6 scenarios each; seed competency rows.
- Run the pipeline for the 3 competencies; persist to dev Supabase.

**Checkpoint —** all four competencies × ~5 = ~20 build-it tasks live. **v1 shipped.**

## Open questions

1. **Multi-Modal as a 5th competency?** The original parked multi-modal; the scenario list wants
   it. Decision needed in Phase 0: add **Multi-Modal Agent Engineering** as its own competency
   (needs a Gemini/Claude-vision primary framework + scope text), or carry multi-modal as example
   tasks under Production Agent Engineering?
2. **AI Evaluation as its own competency?** The LLM-as-judge task is arguably the highest-signal
   task here. Own competency, or eval slice under Production Agent Engineering? **Decide in Phase 0.**
3. **Cost control (now much smaller).** The gate is key-free, so there is *no per-gate-run, no-retry
   LLM cost* — the earlier "real calls cost money on every gate run" concern is retired.
   Remaining cost is per-candidate, on the candidate's key, during their session. Decide only the
   per-candidate-session guardrail (a Portkey-level rate/spend cap on the candidate key).
4. **Reference-solution visibility.** Is the answer repo ever shown to a candidate? Affects
   whether the gen prompt must avoid giveaways. (Note: the answer repo is currently public per
   `persistence.py:289`; Phase A includes making it private.)
5. **Observability stack.** Langfuse / OpenInference, or something else, for the observability
   slice of Production Agent Engineering — and what to bake into `python-ai-agent`.

## Anti-goals

- **No separate `flows/ai_agent/` folder.** One build-it shape inside the existing pipeline.
- **No new task-shape machinery.** Reuse `ANSWER_CODE_SCHEMA`, the existing prompt keying, and
  the two-repo persistence — no new output schema, no new column, no new storage.
- **No pytest pass/fail gate.** Reuse the persona eval critics + the `run.sh` readiness check —
  no generation-time pytest, no two-run gate, no per-shape dispatch. Invariants live in the
  candidate self-check + reviewer rubric.
- **No our-key in a sandbox.** The gate never runs the agent; the only model calls happen in
  the candidate's session on their key (plus the key-gated readiness ping).
- **No mock-LLM.** When the agent does run (the candidate's session), it calls a real model
  through the existing Portkey gateway. *Any in-flight mock-LLM work (e.g. the
  `agent_runtime/` worktree) is retired in favor of the candidate-key approach.*
- **No fat monolith.** The Python runtime is an inheritance family; `python-ai-agent` layers
  agent frameworks on the shared base.
- **No DB schema for template inheritance.** Inheritance is build-time only; the stored
  capability sheet is already resolved.
- **No `sentence-transformers`/torch in the image.** Use the baked `fastembed`.
- **No TypeScript / Mastra template for now.** Python covers it.
- **No fat monolith.** The Python runtime is an inheritance family; `python-ai-agent` layers
  agent frameworks on the shared base.
- **No DB schema for template inheritance.** Inheritance is build-time only; the stored
  capability sheet is already resolved.
- **No `sentence-transformers`/torch in the image.** Use the baked `fastembed`.
- **No TypeScript / Mastra template for now.** Python covers it.
