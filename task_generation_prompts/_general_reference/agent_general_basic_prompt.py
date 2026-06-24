# GENERIC AGENT-ENGINEERING REFERENCE PROMPT (competency-neutral, BASIC).
# Reference-only: the prompt-generator pins this as the TOP structural template
# for ALL agent competencies (Multi-Agent Systems, Production Agent Engineering,
# Tool Use for Agents, Context Engineering) at BASIC proficiency. It defines NO
# PROMPT_REGISTRY, so it never resolves to a competency / is never used to
# generate a task directly.
# Derived from agent_general_intermediate_prompt.py, DOWN-CALIBRATED to BASIC
# (regenerate from it after editing the intermediate baseline).

# task_generation_prompts/Intermediate/production_agent_engineering_intermediate_prompt/production_agent_engineering_intermediate_prompt.py
#
# CURATED task-generation prompt module for AI-agent BUILD-IT tasks.
# Competency: "Agent Engineering"  ·  Proficiency: BASIC
#
# DROP-IN for infra/utils.py::_build_prompt_registry. The loader filesystem-walks
# task_generation_prompts/<Level>/<slug>/<slug>.py (level "Intermediate" IS in the
# walk: infra/utils.py:55) and calls registry.update(PROMPT_REGISTRY). Contract
# (do NOT change without updating the loader):
#   * Export a top-level dict named exactly  PROMPT_REGISTRY.
#   * Key it exactly "Agent Engineering (BASIC)" — the
#     "<name> (<PROFICIENCY-UPPER>)" string get_task_prompt_by_technology_stack
#     builds + sorts from the competency (infra/utils.py:449-451).
#   * Value is a LIST of prompt strings, replayed as sequential user turns
#     (infra/utils.py:474  [t.format(**fmt_args) for t in templates]).
#   * The ONLY legal {placeholders} are the six fmt_args keys (infra/utils.py:463-473):
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.
#
# SCHEMA NOTE (the one load-bearing judgment): the gen-LLM envelope is NOT
# ANSWER_CODE_SCHEMA. infra/utils.py:627-690 json.loads the model output with no
# schema validation; the pipeline then reads canonical keys directly
# (creator.py draft_payload :528-546; save_files_locally consumes code_files as a
# FLAT path->contents dict). ANSWER_CODE_SCHEMA's {files,steps} governs the
# SEPARATE generate_answer_code_and_steps OpenAI call (creator.py:206-219) that
# builds the answer repo from solutions_data (creator.py:511,576) — NOT this
# envelope. task_data['answer'] is passed through opaquely (creator.py:531) and
# never parsed for .files/.steps. So `answer` here is free-form evaluator
# guidance; do NOT make the gen-LLM duplicate the filled solution into it.
# `criterias` is INJECTED by the pipeline (creator.py:444) from the input
# competencies — the gen-LLM must NOT emit it. is_task_hollow requires only
# title-or-name + question + code_files (evaluator.py:78-86).

PROMPT_AGENT_GENERIC_BASIC_CONTEXT = """
Let me provide you with some context about the company and role.

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competencies:
{competencies}

Use this context ONLY to gauge who is hiring and how senior the engineer must be.
The employer's industry is NOT the business domain of the assessment task unless
the scenario you pick explicitly matches it. Do not drift the task into the
employer's domain. You are generating an assessment for an engineer with ~1-2 years of experience
who is getting started building real agents — calibrate accordingly: ONE clear
concept, correctly wired against a real model, not a senior multi-decision design.
"""

PROMPT_AGENT_GENERIC_BASIC_INPUT_AND_ASK = """
You are generating ONE realistic, BASIC "build-it" assessment task
for a Agent Engineering candidate. The candidate clones a real agent
repository, sets their own API key in `.env`, runs `./run.sh`, and writes
~40-100 lines of code inside it using real agent frameworks. This is a coding
session, NOT a write-a-memo / essay / quiz exercise. Debugging is just a
build-it variant with a planted bug; the skill under test is architecture and
operational JUDGMENT, never framework trivia.

CALIBRATION: this is a FOUNDATIONAL agent task — it tests whether the candidate
can correctly wire ONE clear piece of agent logic against a real model, NOT a
senior multi-decision design. Scope it to ONE concept (occasionally two tightly-
related, but prefer one); never a multi-subsystem platform and never a task that
hinges on production "judgment" calls. It sits BELOW a standard intermediate task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a BASIC candidate (~1-2 years). Budget it
as: ~5-10 min setup (clone, .env, ./run.sh) + ~5-10 min reading + 15-25 min
writing code. Hold "candidate writes" to ONE stub file (occasionally two), roughly
40-100 lines, isolating ONE clear concept.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CORE JOB — BUILD ONE AGENT REPO from these fields:
  **Stack:** ...            (frameworks + provider, e.g. LangGraph + LiteLLM)
  **Domain:** ...           (the business setting)
  **Candidate writes:** ... (the stub file(s) the candidate fills)
  **Provided broken:** ...  (what ships broken: unbounded loop, stubbed hooks)
  **Invariants:** ...       (what a correct submission must satisfy)
  **Core signal:** ...      (the one concept being probed)

SCENARIO HANDLING — READ CAREFULLY:
- If `REAL-WORLD SCENARIOS` above contains a concrete scenario (anything other
  than "(none provided)"), you MUST BUILD THAT SCENARIO. Adopt its Stack, Domain,
  Provided-broken, Candidate-writes, Invariants, and Senior-signal FIELD-BY-FIELD.
  The provided scenario IS the spec — do NOT invent a different domain, a
  different stack, or a different bug archetype, and do NOT fall back to a generic
  "bound a runaway loop + cost ceiling" task when the scenario asks for something
  else (e.g. supervisor/router orchestration, tool-schema/RAG routing, context
  budgeting/memory). Honor the COMPETENCY ARCHETYPE block below.
- ONLY when `REAL-WORLD SCENARIOS` is empty / "(none provided)" may you design
  your own realistic domain + senior bug archetype — and even then it MUST fit the
  COMPETENCY ARCHETYPE below.

Translate the chosen fields FIELD-BY-FIELD into a runnable repo that is
deliberately BROKEN:
  - **Stack**       -> the framework set + the files you generate against it
  - **Domain**      -> the business setting (a self-standing product; never the
                       employer's industry)
  - **Provided broken** -> the planted defect(s) in the working files
  - **Candidate writes** -> the NotImplementedError stub file(s)
  - **Invariants**  -> the candidate-facing pytest tests under invariants/
  - **Core signal** -> the single concept the stub isolates
Keep the task to ONE coherent domain; do not drift into the employer's domain.
Honor the pinned **Stack** exactly — the candidate is told the framework up front.

Before generating, briefly internalize:
1. The scenario you are building (the provided one if present, else your own) and
   why it fits this competency's archetype + a BASIC agent task.
2. The agent's TASK FAMILY (web service / agent-as-service / agent CLI-or-loop /
   agent-as-library / backing-store / graph-orchestration) — this dictates the
   run.sh readiness probe.
3. Which file(s) the candidate writes, and which provided file(s) are broken or
   stubbed to create the senior decision.
"""

PROMPT_AGENT_GENERIC_BASIC_INSTRUCTIONS = """
## GOAL
Generate ONE BASIC Agent Engineering "build-it" task: a real,
runnable agent repository that is deliberately incomplete. It ships broken agent
code plus candidate stubs that raise `NotImplementedError`, and the candidate
makes it production-safe by filling those stubs and fixing the planted flaws.
The candidate uses real frameworks (langgraph, litellm, the anthropic / openai
SDKs, crewai, mem0, fastapi, fastembed) and calls a real model on THEIR OWN key.
There is NO pytest pass/fail generation gate — the task is judged by the eval
critics plus the run.sh readiness check.

## 0. REAL LLM / AGENT LOOP — MANDATORY (this is the task's substance)
This is an AGENT-ENGINEERING task: the repository MUST contain a REAL LLM/agent
loop, and the candidate's work IS the agent logic around a real model.
  - The agent calls a REAL model via litellm or the anthropic / openai SDK on the
    candidate's OWN key. NEVER a FakeLLM. NEVER a regex / keyword "intent parser".
    NEVER any deterministic stand-in for the model.
  - The candidate-filled `NotImplementedError` stubs ARE the assessed agent logic:
    context construction, tool selection / dispatch, retry / timeout, output
    parsing, memory / state, budgeting — NOT a fake model.
  - NEVER use `time.sleep()` / `asyncio.sleep()` to simulate an agent or a tool
    "thinking" or "working". Tools do real local work or call a real service;
    latency is not the skill under test.
  - Determinism is NOT a goal of the TASK. Grading judges the candidate's diff
    with an LLM critic and never runs a pass/fail suite, so a real
    (non-deterministic) model is correct and expected. Use fixtures only to make
    tool INPUTS / retrieval corpora deterministic — never to replace the model.

REQUIRED real-model wiring (the proven AGENT_TEST_MODE pattern). The client
library is a FREE CHOICE — litellm (a router), the openai / anthropic SDK
directly, or an agent framework (langgraph / langchain / crewai). The mandate is
a REAL model call, NOT a specific library.
  - Ship a COMPLETE LLM-client wrapper (e.g. `agent/llm_client.py`) exposing a
    `chat_completion(messages, model, ...)`-style call (retry + token capture),
    built on the chosen client. It is PROVIDED COMPLETE — NOT a candidate stub.
    The candidate writes the AGENT logic around it (orchestrator, tools), never
    the model plumbing.
  - Ship `config.py` reading env: model names (e.g. INTENT_MODEL / REPLY_MODEL)
    and `AGENT_TEST_MODE = os.getenv("AGENT_TEST_MODE", "0") == "1"`.
  - `AGENT_TEST_MODE=1` → the client returns DETERMINISTIC FIXTURE responses so
    the readiness gate + invariants run offline/key-free. `AGENT_TEST_MODE=0`
    (default) → a REAL model call on the candidate's OWN provider key.
  - Ship `.env.example` with `OPENAI_API_KEY=` / `ANTHROPIC_API_KEY=` and
    `AGENT_TEST_MODE=0`. Add the chosen client (+ provider SDK) to the runtime
    manifest and to `pre_requisites`.

Per-competency emphasis — a real model call matters MOST where the MODEL'S OWN
DECISIONS are the assessed skill:
  - Tool Use for Agents / Multi-Agent Systems / Agent Engineering →
    a REAL model call is ESSENTIAL: tool-selection / coordination / agent
    reasoning IS the skill. A regex/keyword "decision" tests nothing.
  - Context Engineering → the assessed skill is the CONTEXT the candidate builds
    (bounded packing, retrieval, caching, ordering), verifiable on the constructed
    context itself. A real model is preferred (AGENT_TEST_MODE pattern), but a
    clearly-modeled LLM consumer is acceptable PROVIDED the context/retrieval
    logic is real — never a sleep/regex stand-in for the agent.

The universal rule is NOT "use litellm" — it is: never fake the agent's own
decision with a regex/keyword matcher or time.sleep. The model-client and whether
the call is live follow from the competency above.

The "LLM-free / no API key" rule in sections 1-2 below applies ONLY to the
generation-time run.sh READINESS GATE (imports + fixture/schema validation
without a key). It MUST NOT be generalized to the task: the shipped task is a
real agent loop that runs on the candidate's key.

# ============================================================================
# SENIOR SIGNAL FIRST — the run.sh readiness probe and the five invariants are
# the load-bearing correctness contract. Get these right BEFORE envelope
# mechanics: a task that violates "never call a stub" or "LLM-free at the gate"
# is structurally broken no matter how good the prose is.
# ============================================================================

## 1. THE run.sh READINESS PROBE (per TASK FAMILY) — REQUIRED
`run.sh` proves the environment is set up and the scaffold loads so the candidate
can START coding. "ready" does NOT mean "solved" — the scaffold is deliberately
incomplete, so "ready" means "deps installed + scaffold imports + static
artifacts valid". It runs at the deploy gate with NO API key. Shape:

    #!/usr/bin/env bash
    set -euo pipefail
    pip install -q -r requirements.txt
    # docker compose up -d --wait      # ONLY if the task has a backing store
    python -m agent --selfcheck         # or the family probe below
    echo "ready"

Start with `#!/usr/bin/env bash` and `set -euo pipefail` so any failed step exits
non-zero. The probe must TERMINATE (no hang) and be the LAST thing run.sh does
before `echo "ready"`. The EXIT CODE is the signal (0 = ready, non-zero = broken).

Pick the row that matches the TASK FAMILY of the repo you generated:

| Task family | Readiness probe (exit 0 = ready) |
|---|---|
| Web service | `curl -sf localhost:8000/health` returns 200. |
| Agent wrapped as a service | Same — `curl -sf` the agent's `/health` or `/invoke`. |
| Agent as a CLI / loop | `python -m agent --selfcheck` — imports the package, loads config / prompts / tool defs, validates fixtures + schemas. Does NOT call the stubs or run the loop. Model ping only if a key is present. |
| Agent as a library | A tiny script imports the entry point, asserts deps + config load, exits 0/1. |
| Task with a backing store | `docker compose up --wait`, then a dummy write/read/delete round-trip against the store (e.g. a key-free fastembed vector). No chat-model call. |
| Graph / orchestration | `build_graph().compile()` — the topology (nodes/edges) resolves WITHOUT executing any node. All specialists/nodes must import. |

The CLI/loop `--selfcheck` is the DEFAULT for this competency unless the scenario
clearly demands a service, a store, or a graph.

## 2. THE FIVE READINESS INVARIANTS — NON-NEGOTIABLE
run.sh runs against the CANDIDATE repo (stubs still raise NotImplementedError)
and at the gate there is NO key in the sandbox. So:
1. NEVER CALL A STUBBED FUNCTION. Readiness IMPORTS the candidate-stub modules to
   prove they load (importing a body that raises NotImplementedError is fine —
   the raise only fires on CALL), but must NOT invoke `enforce_budget()`,
   `choose_model()`, `recall()`, `route()`, etc., and must NOT run the agent loop.
2. DON'T DEPEND ON THE CANDIDATE'S UNFILLED WORK. Readiness must pass on the repo
   as shipped. If the "stub" is buggy DATA the candidate must fix (e.g. broken
   tool schemas), readiness LOADS the module but must NOT validate that data —
   fixing it IS the task. Readiness only proves the scaffold loads + fixtures exist.
3. LLM-FREE AT THE GATE. No model call may be REQUIRED for readiness. Readiness
   never calls a chat model and never runs the agent loop. The first real model
   call happens later, on the candidate's key.
4. KEY-GATED MODEL PING. Include a `_ping_model()` that fires ONLY when a key is
   present, pinging the model DIRECTLY (not through the agent graph, so it can't
   trip the very loop the candidate must bound):

       # at the END of selfcheck(), after imports/fixtures/schema checks:
       if os.getenv("ANTHROPIC_API_KEY"):   # absent at the gate -> skipped (free, deterministic)
           _ping_model()                    # present in candidate session -> 1-token call
       else:
           print("note: no ANTHROPIC_API_KEY — skipping model ping")

   At the gate (no key) the ping is skipped and the probe stays free/deterministic;
   in the candidate's session it fires and catches endpoint / auth / model-name
   misconfig the import check cannot.
5. NEVER RUN THE UNBOUNDED LOOP and never hard-require the key, so the probe
   passes BOTH at the gate (no key) and in a candidate's session before `.env`.

Invariant checks (loop terminates, valid tool-calls, cost <= ceiling, output
parseable, quality >= baseline) ship as a CANDIDATE-FACING self-check under
invariants/ for the candidate's own feedback — NOT as part of the readiness exit
code, and NOT as a generation-time pytest gate.

## SCENARIO SOURCE
- If `real_world_task_scenarios` contains a concrete scenario, it is the SPEC:
  build it field-by-field (Stack / Domain / Provided-broken / Candidate-writes /
  Invariants / Senior-signal). Do NOT swap the domain, stack, or bug archetype,
  and do NOT collapse it into a generic loop+cost task — match what it asks and
  the COMPETENCY ARCHETYPE below.
- ONLY if it is empty / "(none provided)" do you design your own: pick ONE
  concrete domain (e.g. fintech, healthcare, logistics, travel, e-commerce,
  devtools) and ONE senior bug archetype that FITS THE COMPETENCY ARCHETYPE
  below; state in a single line which domain + archetype you chose.
- `organization_background` describes who is ADMINISTERING the assessment — do
  NOT make the employer's industry the task domain. The domain must stand on its
  own as a realistic product, distinct from the employer.
- When designing your own, prefer a domain NOT already covered by any EXISTING
  TASKS listed in `real_world_task_scenarios` (the de-dup block) — keep diverse.

## COMPETENCY SCOPE (center the chosen scenario on ONE concept drawn here)
Agent Engineering at BASIC covers a FOCUSED SLICE of the agent lifecycle — pick
the SIMPLEST viable concern that touches one of:
- Architecture & orchestration: API layer, orchestrator, tools, workers, queues,
  datastores; ReAct, planner-executor, reflection/repair, multi-agent.
- Multi-step planning, task decomposition, bounded reasoning loops.
- Tool contracts: schema validation, arg sanitization, retries, backoff,
  timeouts, idempotency, transactional integrity, partial-failure / compensation.
- Retrieval, memory, and state: short/long-term, episodic/semantic, vector
  stores, indexing, knowledge freshness, dedup, cross-tenant isolation.
- Safety & guardrails: system-prompt policy, input/output filtering, prompt-
  injection defense, least-privilege tool access, escalation, approval workflows,
  audit logging (incl. PII / compliance handling).
- Reliability & observability: structured error categorization, tracing, metrics,
  SLOs, model-provider fallback, circuit breakers, graceful degradation.
- Evaluation: golden sets, scenario/regression tests, LLM-as-judge, rubric-based
  verdicts, agreement checks.
- Performance & cost: latency budgets, caching, parallel vs sequential tool
  calls, multi-model routing, per-task cost ceilings.
Pick ONE clear concept for a coherent build-it item (e.g. bound a runaway loop to
a max number of model calls; OR parse + validate the model's structured output and
retry once on invalid; OR validate one tool's args before dispatch; OR a single
bounded retry/timeout around one flaky call). Do NOT stack multiple concerns —
that tips into intermediate. The signal is a CORRECTLY WIRED primitive, not senior
judgment: a real bound (not an unchecked while-True), real validation (not blind
trust of model output), a real retry (not a bare `except: pass`).

Stay inside this scope. Do NOT turn the task into: a pure framework-syntax drill,
a generic ML-modeling / fine-tuning task, a frontend task, a pure prompt-writing
task, or a system-design essay with no runnable artifact.

## AGENT FRAMEWORKS (use what the scenario's Stack pins)
Generate against the pinned Stack directly. Typical pins for this competency:
- `langgraph` + `litellm` (model routing / fallback) — the primary stack.
- `anthropic` and/or `openai` SDKs (primary + fallback providers).
- `fastembed` for local, key-free embeddings (retrieval / context tasks) — do
  NOT pull in `sentence-transformers` or `torch`.
- `tiktoken` for token accounting; `mem0` (mem0ai) or a vector store (e.g.
  `qdrant`) for memory; `crewai` only if the scenario explicitly calls for a crew.
- `pytest` for the candidate-facing invariant tests.
List exactly the libraries the task uses in `requirements.txt` (standard PyPI
names). run.sh's FIRST step MUST be `pip install -q -r requirements.txt`: the E2B
readiness gate does NOT pre-install the task's own third-party deps (psycopg,
litellm, langgraph, …), so skipping it fails readiness on the very first attempt
with `ModuleNotFoundError`. (Do NOT `apt-get`/system-install the runtime itself —
only the task's PyPI deps via requirements.txt.)

## THE BUILD-IT REPO SHAPE (5-8 files, lean but real)
A typical CLI/loop build-it repo:
- working modules the candidate reads but does not change (e.g. `agent/prompts.py`,
  `agent/tools.py`) — all import cleanly and load.
- the PROVIDED-BROKEN file(s): e.g. an unbounded graph loop, a router that dumps
  all tools into context, a single-turn agent that forgets between sessions.
- the CANDIDATE-STUB file(s): functions that `raise NotImplementedError("<one
  neutral line naming WHAT, never HOW>")` (e.g. `enforce_budget()`,
  `choose_model()`, `recall()`, `validate_args()`, `route()`).
- `invariants/test_*.py`: candidate-facing invariant tests (the candidate runs
  these themselves AFTER filling the stubs; NOT a generation-time gate; run.sh
  must NOT depend on them).
- `fixtures/*.jsonl` (or images/text): realistic, internally-consistent data that
  exercises the invariants (include the ONE discriminating fixture — the outlier
  ticket, the blurry image, the ambiguous request).
- `run.sh`: the family-appropriate readiness probe honoring the five invariants.
- `requirements.txt`, `.env.example` (e.g. `ANTHROPIC_API_KEY=` / `OPENAI_API_KEY=`).
- AVOID a backing store at BASIC: prefer in-memory state / a local JSON or SQLite
  file / key-free local fastembed. Add `docker-compose.yml` ONLY if the pinned
  scenario Stack truly requires a server (it usually does NOT at BASIC) — a docker
  backing store makes the readiness gate fragile. If present, run.sh uses
  `docker compose up -d --wait` + a round-trip.
- `README.md` — the candidate-facing repo readme in the REQUIRED four-section
  format (see "## README.md REQUIREMENTS"): system context + outcome-level
  objectives. It must NOT name the stub files/functions, must NOT restate the
  invariants as a checklist, and must NOT describe the fix.
Include only files the candidate genuinely needs.

## DO NOT LEAK THE REFERENCE ANSWER INTO THE CANDIDATE REPO
The `code_files` are CANDIDATE-FACING and must be solution-free:
- Candidate-stub functions raise `NotImplementedError` with a one-line neutral
  docstring of the contract — no implementation, no commented-out solution, no
  TODO that reveals the fix, no step-by-step docstring.
- No comments / method names that give away the approach.
- The repo must be runnable (`./run.sh` exits 0) but the graded behavior stays
  incomplete/incorrect until the candidate finishes.
- The full solution, root causes, and expected fixes go ONLY in the `answer`
  field (evaluator-facing), never in `code_files`, `README.md`, or comments.

## OUTPUT ENVELOPE — EMIT EXACTLY THESE TOP-LEVEL KEYS (this is paramount)
Output a SINGLE raw JSON object with EXACTLY these keys and no others:
- `"name"`: string, task name in kebab-case (e.g. "harden-support-reply-agent").
- `"title"`: string, human-readable "<verb> <subject>" title, 50-80 chars,
  different from `name` (read with name-fallback downstream; safe to include).
- `"question"`: string, full candidate-facing brief (see QUESTION REQUIREMENTS).
- `"code_files"`: object mapping file path -> full file contents (the whole repo,
  as a FLAT path->contents dict).
- `"answer"`: object or string, EVALUATOR-FACING solution guidance (NOT shipped to
  the candidate, NOT parsed for files/steps — free-form reviewer guidance).
- `"definitions"`: object or string of concise term definitions used in the task.
- `"hints"`: array or string of optional candidate hints (NOT inside `question`).
- `"outcomes"`: string/array describing what a strong submission demonstrates.
- `"pre_requisites"`: string/array of assumed knowledge, tools, frameworks.
- `"short_overview"`: string/array summarizing the task.

Use these EXACT keys. Do NOT use synonyms: not `task_title`/`heading` for `title`,
not `files`/`repository_structure`/`repo` for `code_files`, not `context`/`prompt`
for `question`, not `solution` for `answer`. Do NOT emit `criterias` — the
pipeline injects it. Output raw JSON only — no markdown fences, no prose around it.

## QUESTION REQUIREMENTS
`"question"` must read like a real ticket / incident-channel message from a
teammate, and must:
- open with a short realistic work-context message,
- state the SYMPTOMS (what's observably broken / unbounded / crashing / costly in
  production) — describe the failure, not the fix,
- frame the high-level ask in business terms (what "fixed" looks like: "stops
  running away", "stays within budget", "degrades gracefully when the model is
  down") — do NOT name the stub files/functions, do NOT enumerate implementation
  steps, and do NOT restate the invariant thresholds as a checklist. The candidate
  DISCOVERS the stubs (they raise NotImplementedError) and the precise acceptance
  bar (in `invariants/test_*.py`) themselves — that diagnosis is the senior signal,
- state real constraints (preserve behavior, respect safety policy, stay within
  the latency/cost budget),
- tell the candidate to put their key in `.env` and run `./run.sh` (the first
  real model call happens on THEIR key),
- contain NO hints (hints go only in the `hints` field).

## README.md REQUIREMENTS — the candidate-facing repo readme
`README.md` MUST use EXACTLY these four markdown section headers, in this order
(the pipeline parses them into `readme_content`; ANY other shape parses to an
EMPTY readme — this is non-negotiable):

`## Task Overview` — a short context paragraph: what the system is (product +
domain), how it's used, and what is OBSERVABLY going wrong in production (the
symptoms). Frame the objective at a high level. Do NOT name the stub
files/functions, do NOT say which functions to implement, do NOT list the
invariants, do NOT describe the fix.

`## Objectives` — 3-5 bullets describing WHAT must be true when the work is done:
OUTCOMES, never instructions. Describe the "what", NEVER the "how".
  GOOD: "- The agent stays within its per-task cost budget even under load."
  BAD:  "- Implement enforce_budget() in agent/policy.py to block >$0.05 calls."
Do NOT enumerate files, functions, or invariant thresholds as a checklist — the
candidate discovers the stubs (NotImplementedError) and the right approach
themselves; that diagnosis IS the senior signal.

`## How to Verify` — 2-4 bullets on how the candidate checks their OWN work: put
the API key in `.env`, run `./run.sh` (readiness), then run the provided
`invariants/` tests and exercise the fixtures. Verification steps only — never
the solution.

`## Helpful Tips` — 2-3 light, non-revealing pointers (e.g. "trace the control
flow in the provided graph before changing it"). Never name the fix, the function
bodies, or the specific library calls that give away the approach.

The README is CONTEXT + OUTCOMES, never a how-to and never a deliverables list.
The reference fix, root causes, and expected approach live ONLY in `answer`.

## ANSWER REQUIREMENTS (evaluator-facing, never shipped to the candidate)
`"answer"` summarizes: the root cause(s), the expected shape of a strong fix, the
key tradeoffs/residual risks (safety, reliability, latency, cost), and which
evidence in the provided files supports the diagnosis. High-level guidance, not a
full chain-of-thought, and NOT the filled solution files.

## DATA & INTERNAL CONSISTENCY
Fixtures, traces, eval rows, and configs must be realistic and consistent across
docs, code, fixtures, run.sh, and .env.example: IDs, tool names, model names,
timestamps, statuses, latency/cost numbers, ports, and policy labels must line
up. Failures in the evidence must be plausible consequences of the planted flaws —
exposing the problem indirectly without handing over the answer. Include the
single discriminating fixture that separates a senior fix from a shortcut.

## DIFFICULTY CALIBRATION (BASIC)
Isolate ONE clear concept into a coherent work item — ONE stub (occasionally two
tightly-related), NOT several stacked concerns and NOT a platform. The candidate
writes ~40-100 lines using real frameworks. It tests whether they can wire ONE
piece of agent logic against a real model CORRECTLY — easier than an intermediate
task (no senior multi-decision design, no production-judgment calls, no
multi-subsystem sprawl), but still a real runnable agent loop, never a fake-LLM
toy. Solvable within {minutes_range}.

## REQUIRED OUTPUT EXAMPLE SHAPE (schema only — replace all values; every literal
## brace inside file contents must be escaped as the candidate needs)
{{
  "name": "validate-support-reply-output",
  "title": "Validate and Recover a Support Agent's Structured Reply",
  "question": "From: support-tooling channel\\n\\nOur support reply agent asks the model for a strict JSON reply (a category plus a customer-facing message), but sometimes the model returns malformed or off-schema JSON and we ship it straight to customers — occasionally as a raw error string. We need it to only ever return a valid reply, and to fail safe when the model misbehaves.\\n\\nMake the agent parse and validate the model's output, retry once when it's invalid, and fall back to a safe canned reply if it still can't get a valid one. Clone the repo, set your key in .env, and run ./run.sh — the first real model call happens on YOUR key. (Read the code and the invariants/ tests to find what's incomplete.)",
  "code_files": {{
    "README.md": "## Task Overview\\n<product + domain context, how it's used, and the production symptom: malformed / off-schema model replies reaching customers; NO file names, NO invariants, NO fix>\\n\\n## Objectives\\n- The agent only ever returns a reply that matches the required schema.\\n- When the model returns invalid output, the agent recovers instead of shipping it.\\n\\n## How to Verify\\n- Put your API key in .env and run ./run.sh\\n- Run the invariants/ tests and exercise the fixtures to check your work\\n\\n## Helpful Tips\\n- Trace how the raw model response flows into the reply the customer sees.\\n",
    "agent/__main__.py": "import sys, os, json\\nfrom pathlib import Path\\n...selfcheck(): static checks; key-gated _ping_model()...",
    "agent/client.py": "# PROVIDED COMPLETE: real model call (litellm / openai SDK) + token capture — NOT a stub\\n...",
    "agent/reply.py": "def parse_and_validate(raw):\\n    raise NotImplementedError(\\"parse the model output and validate it against the reply schema\\")\\n",
    "agent/schema.py": "# the required reply schema + the safe fallback reply (working, candidate reads)\\n...",
    "invariants/test_reply.py": "...test_valid_output_passes / test_malformed_json_recovers / test_offschema_falls_back...",
    "fixtures/model_outputs.jsonl": "...a valid reply, a malformed-JSON reply, an off-schema reply...",
    "run.sh": "#!/usr/bin/env bash\\nset -euo pipefail\\npip install -q -r requirements.txt\\npython -m agent --selfcheck\\necho \\"ready\\"\\n",
    "requirements.txt": "litellm\\nopenai\\npytest\\n",
    ".env.example": "OPENAI_API_KEY=\\nAGENT_TEST_MODE=0\\n"
  }},
  "answer": {{
    "summary": "...",
    "root_causes": ["raw model output trusted without parsing", "no schema validation", "no retry or safe fallback on invalid output"],
    "expected_fixes": ["parse the JSON defensively", "validate the parsed object against the reply schema", "retry once on invalid, then fall back to the safe canned reply"],
    "tradeoffs": ["one retry adds latency/cost vs reliability", "strict schema vs accepting a partial reply"]
  }},
  "definitions": {{
    "structured output": "...",
    "schema validation": "...",
    "safe fallback": "..."
  }},
  "hints": ["...", "..."],
  "outcomes": "A strong submission parses the model output defensively, validates it against the schema, retries once on invalid output, falls back to the safe reply when needed, and ships production-clean code (clear naming, explicit error handling, sensible structure).",
  "pre_requisites": ["Python 3.10+", "calling a real LLM via litellm or the OpenAI SDK", "JSON parsing + schema validation", "pytest", "a provider API key via .env"],
  "short_overview": ["Make a support agent only ever return a schema-valid reply", "Parse + validate the model output, retry once, fall back safely", "One real model call on the candidate's key"]
}}

## FINAL REMINDERS
- Output raw JSON only — exactly the keys: name, title, question, code_files,
  answer, definitions, hints, outcomes, pre_requisites, short_overview. Do NOT
  emit `criterias` (the pipeline injects it).
- Use ONE coherent domain (adopt a listed scenario OR design your own); if you
  adopt one, honor its pinned Stack and map its fields field-by-field.
- Ship the defect UNFIXED + candidate stubs raising NotImplementedError in
  code_files; the reference fix lives ONLY in `answer`.
- The run.sh readiness probe must match the TASK FAMILY and obey all five
  readiness invariants (no stub call, no candidate-work dependency, LLM-free at
  the gate, key-gated ping, never run the unbounded loop / hard-require the key).
- Invariants ship as candidate-facing pytest tests, never as a generation gate.
- README.md MUST use the four headers (## Task Overview / ## Objectives / ## How
  to Verify / ## Helpful Tips) — context + OUTCOMES only; no file/function names,
  no invariant checklist, no fix. (Any other shape → empty readme_content.)
- `outcomes` must include one bullet on production-clean code (naming, error
  handling, logging, structure).
- Never leak the reference answer into code_files.
- Keep it BASIC, build-it, and solvable in {minutes_range}.
"""

# ──────────────────────────────────────────────────────────────────────────
# Per-competency ARCHETYPE packs. The base (CONTEXT + INPUT_AND_ASK +
# INSTRUCTIONS) is shared; this competency-specific block is appended LAST so
# the generated task matches the COMPETENCY's SHAPE — not a generic "bound a
# runaway loop + cost ceiling" task for every competency. The base prompt
# refers to "the COMPETENCY ARCHETYPE block"; these are it. (No {placeholders}
# here — they pass through str.format() untouched.)
# ──────────────────────────────────────────────────────────────────────────

_ARCHETYPE_PRODUCTION_AGENT_ENGINEERING = """
## COMPETENCY ARCHETYPE — Agent Engineering
Center the task on ONE production-robustness PRIMITIVE of a single agent (not a
combination). Valid single concepts: bound an unbounded reasoning/reflection loop
to a max number of model calls; a single bounded retry/timeout around one flaky
model or tool call; parse + validate the model's structured output and recover on
invalid; one pre-call guard (reject an empty/oversized request). Pick exactly ONE.
TASK FAMILY: agent-CLI / agent-as-service. Readiness:
`python -m agent --selfcheck` (or `curl -sf /health` for a service). Prefer no
backing store / no docker at BASIC.
"""

_ARCHETYPE_MULTI_AGENT_SYSTEMS = """
## COMPETENCY ARCHETYPE — Multi-Agent Systems
This task MUST involve more than one agent, but keep coordination MINIMAL at BASIC:
exactly TWO agents with ONE handoff — a simple supervisor/router that picks one of
two specialists and threads the result back out. The concept under test is a
single correct HANDOFF + state pass-through, NOT confidence routing, NOT
arbitration, NOT a multi-step crew (those are intermediate). The router may use the
model to pick the specialist; do NOT fake it with keyword if/else.
TASK FAMILY: graph-orchestration (small). Readiness: `build_graph().compile()`
resolves the topology (both specialists + the router import, edges resolve)
WITHOUT running any node or calling a model. Prefer no docker at BASIC.
HARD RULE: there MUST be two coordinated agents joined by exactly ONE simple
handoff — not a single-agent task, and not a sprawling crew/pipeline.
"""

_ARCHETYPE_TOOL_USE = """
## COMPETENCY ARCHETYPE — Tool Use for Agents
Center the task on ONE tool at the boundary. Valid single concepts:
- validate ONE tool's arguments before dispatch (reject malformed args with a
  structured error, never pass them through); OR
- fix ONE broken tool JSON-Schema (required / types / enums) so the model can call
  it correctly.
ONE tool, ONE concept — NOT a tool catalogue, NOT RAG tool-routing, NOT a
multi-step repair loop (those are intermediate).
TASK FAMILY: agent-CLI / agent-as-service. Readiness: import the tool module +
confirm the eval fixtures load; do NOT validate the buggy schema when fixing it IS
the candidate's task. Prefer no docker at BASIC.
HARD RULE: the task MUST center on ONE tool's definition or argument validation —
NOT a generic loop task and NOT a tool catalogue.
"""

_ARCHETYPE_CONTEXT_ENGINEERING = """
## COMPETENCY ARCHETYPE — Context Engineering
Center the task on ONE context primitive. Valid single concepts:
- count tokens with tiktoken and TRIM/truncate the context to stay under a
  prompt-size ceiling (keep the most important parts, drop the rest); OR
- simple top-k RETRIEVAL over a small local corpus with fastembed (return the k
  most relevant chunks, NOT the whole corpus).
ONE concept — NOT a budget middleware + retrieval + memory stack, NOT long-term
memory dedup/staleness, NOT cross-tenant isolation (those are intermediate).
TASK FAMILY: agent-CLI with an IN-PROCESS store — fastembed is local (no server)
and any state is a local JSON/SQLite file. NO docker-compose at BASIC: a docker
backing store makes the readiness gate fragile.
Readiness: `python -m agent --selfcheck` — imports the budget / retrieval module,
dry-loads the corpus + probe fixtures, confirms fastembed loads locally; key-free,
no services, no docker.
HARD RULE: the task MUST center on ONE context / retrieval primitive — NOT a
generic loop task and NOT a full memory subsystem.
"""

# Shared base, replayed as sequential user turns; the per-competency archetype
# is appended LAST so each competency gets a shape-specialized variant.
_BASE_BASIC = [
    PROMPT_AGENT_GENERIC_BASIC_CONTEXT,
    PROMPT_AGENT_GENERIC_BASIC_INPUT_AND_ASK,
    PROMPT_AGENT_GENERIC_BASIC_INSTRUCTIONS,
]

_ARCHETYPE_BY_COMPETENCY = {
    "Agent Engineering": _ARCHETYPE_PRODUCTION_AGENT_ENGINEERING,
    "Multi-Agent Systems": _ARCHETYPE_MULTI_AGENT_SYSTEMS,
    "Tool Use for Agents": _ARCHETYPE_TOOL_USE,
    "Context Engineering": _ARCHETYPE_CONTEXT_ENGINEERING,
}

# Reference-only skeleton -- intentionally defines no PROMPT_REGISTRY.
