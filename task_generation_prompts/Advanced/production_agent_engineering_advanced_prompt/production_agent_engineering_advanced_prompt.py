# task_generation_prompts/Advanced/production_agent_engineering_advanced_prompt/production_agent_engineering_advanced_prompt.py
#
# CURATED task-generation prompt module for AI-agent BUILD-IT tasks.
# Competency: "Production Agent Engineering"  ·  Proficiency: ADVANCED
#
# DROP-IN for infra/utils.py::_build_prompt_registry. The loader filesystem-walks
# task_generation_prompts/<Level>/<slug>/<slug>.py (level "Advanced" IS in the
# walk: infra/utils.py:55) and calls registry.update(PROMPT_REGISTRY). Contract
# (do NOT change without updating the loader):
#   * Export a top-level dict named exactly  PROMPT_REGISTRY.
#   * Key it exactly "Production Agent Engineering (ADVANCED)" — the
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

PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_CONTEXT = """
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
employer's domain. You are generating an assessment for a senior engineer who has
actually shipped production agents — calibrate accordingly.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_INPUT_AND_ASK = """
You are generating ONE realistic, ADVANCED "build-it" assessment task for a
Production Agent Engineering candidate. The candidate clones a real agent
repository, sets their own API key in `.env`, runs `./run.sh`, and writes
~100-300 lines of code inside it using real agent frameworks. This is a coding
session, NOT a write-a-memo / essay / quiz exercise. Debugging is just a
build-it variant with a planted bug; the skill under test is architecture and
operational JUDGMENT, never framework trivia.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong ADVANCED candidate. Budget it
as: ~5-10 min setup (clone, .env, ./run.sh) + ~5-15 min reading/experimenting +
20-30 min writing code. Hold "candidate writes" to 1-2 stub files, roughly
60-150 lines, isolating ONE senior decision.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CORE JOB — SCENARIO -> AGENT REPO.
Each scenario is a free-form string with fields like:
  **Stack:** ...            (frameworks + provider, e.g. LangGraph + LiteLLM)
  **Domain:** ...           (the business setting)
  **Candidate writes:** ... (the stub file(s) the candidate fills)
  **Provided broken:** ...  (what ships broken: unbounded loop, stubbed hooks)
  **Invariants:** ...       (what a correct submission must satisfy)
  **Senior signal:** ...    (the one senior decision being probed)

PICK EXACTLY ONE scenario and translate it FIELD-BY-FIELD into a runnable repo
that is deliberately BROKEN as described:
  - **Stack**       -> the framework set + the files you generate against it
  - **Domain**      -> the business setting (lock to it; never the employer's)
  - **Provided broken** -> the planted defect(s) in the working files
  - **Candidate writes** -> the NotImplementedError stub file(s)
  - **Invariants**  -> the candidate-facing pytest tests under invariants/
  - **Senior signal** -> the single decision the stub isolates
Do not blend scenarios, invent a domain, or drift to the employer's domain.
Honor the scenario's pinned **Stack** — the candidate is told the framework up
front, so generate against that exact framework set.

Before generating, briefly internalize:
1. Which single scenario you picked and why it suits an ADVANCED agent task.
2. The agent's TASK FAMILY (web service / agent-as-service / agent CLI-or-loop /
   agent-as-library / backing-store / graph-orchestration) — this dictates the
   run.sh readiness probe.
3. Which file(s) the candidate writes, and which provided file(s) are broken or
   stubbed to create the senior decision.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_INSTRUCTIONS = """
## GOAL
Generate ONE ADVANCED Production Agent Engineering "build-it" task: a real,
runnable agent repository that is deliberately incomplete. It ships broken agent
code plus candidate stubs that raise `NotImplementedError`, and the candidate
makes it production-safe by filling those stubs and fixing the planted flaws.
The candidate uses real frameworks (langgraph, litellm, the anthropic / openai
SDKs, crewai, mem0, fastapi, fastembed) and calls a real model on THEIR OWN key.
There is NO pytest pass/fail generation gate — the task is judged by the eval
critics plus the run.sh readiness check.

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

## SCENARIO LOCK (mandatory)
- Pick EXACTLY ONE scenario from `real_world_task_scenarios`. The task's BUSINESS
  DOMAIN must match it. Do NOT invent a new domain.
- The broken implementation and the candidate's required work come from that
  chosen scenario, adapted to Production Agent Engineering.
- `organization_background` describes who is administering the assessment — it is
  NOT automatically the task domain.
- If you drift into a domain not in `real_world_task_scenarios`, STOP and restart
  with one listed scenario.
- If `real_world_task_scenarios` is empty or "(none provided)", explicitly state
  which generic agent domain you picked and why. Do not silently default to the
  employer's domain.

## COMPETENCY SCOPE (center the chosen scenario on a senior decision drawn here)
Production Agent Engineering at ADVANCED covers the full agent lifecycle:
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
Combine SEVERAL of these into ONE coherent build-it item (e.g. bounded loop +
pre-call cost ceiling + router fallback; OR tool-arg validation + idempotency +
compensation; OR retrieval freshness + memory contamination + escalation). The
senior signal is JUDGMENT not syntax: router fallback (not a try/except swallow),
cost enforced BEFORE the call, bounded loop, relevance-keyed recall (not
dump-all), routing with a confidence escape hatch (not keyword if/else).

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
names). Do NOT instruct the downstream model to run `pip install`.

## THE BUILD-IT REPO SHAPE (6-9 files, lean but real)
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
- `docker-compose.yml` ONLY if the task has a backing store (vector DB / tool
  server); if present, run.sh uses `docker compose up -d --wait` + a round-trip.
- `README_task.md` with the candidate brief (states WHAT is broken + the
  invariants, never HOW to fix).
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
  field (evaluator-facing), never in `code_files`, `README_task.md`, or comments.

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
- state the symptom (what's broken / unbounded / crashing),
- name which file(s) the candidate must write and which are provided,
- specify the concrete deliverables and the INVARIANTS the solution must satisfy
  (e.g. "loop terminates in <= 6 model calls", "on a primary-model 5xx, fall back
  via the router — not a swallowed try/except", "projected per-task cost <= $0.05
  enforced BEFORE the call", ">= 8/10 cases get a non-empty on-policy result"),
- state constraints (preserve behavior, respect safety policy, stay within the
  latency/cost budget),
- tell the candidate to put their key in `.env` and run `./run.sh` (the first
  real model call happens on THEIR key),
- contain NO hints (hints go only in the `hints` field).

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

## DIFFICULTY CALIBRATION (ADVANCED)
Combine several advanced concerns into ONE coherent work item. The candidate
writes ~100-300 lines using real frameworks — never an entire platform from
scratch. Solvable within {minutes_range}.

## REQUIRED OUTPUT EXAMPLE SHAPE (schema only — replace all values; every literal
## brace inside file contents must be escaped as the candidate needs)
{{
  "name": "harden-support-reply-agent",
  "title": "Harden Support Reply Agent with Model Fallback and Cost Ceiling",
  "question": "From: on-call channel\\n\\nThis support agent runs away on an unbounded loop and hard-crashes when the primary model 5xxes...\\n\\nYour task: bound the loop in agent/graph.py, implement enforce_budget() and choose_model() in agent/policy.py, add LiteLLM fallback...\\n\\nInvariants your fix must satisfy: loop terminates in <= 6 model calls; on a primary 5xx fall back via the router; projected per-ticket cost <= $0.05 enforced BEFORE the call; >= 8/10 tickets get a non-empty on-policy reply.\\n\\nPut your key in .env and run ./run.sh. The first real model call happens on YOUR key.",
  "code_files": {{
    "README_task.md": "...what is broken + deliverables + invariants; NO fix...",
    "agent/__main__.py": "import sys, os, json\\nfrom pathlib import Path\\n...selfcheck(): static checks; key-gated _ping_model()...",
    "agent/graph.py": "# LangGraph graph — loop node UNBOUNDED (candidate bounds it)\\n...",
    "agent/policy.py": "def enforce_budget(...):\\n    raise NotImplementedError(\\"enforce a per-ticket cost ceiling before the model call\\")\\n\\ndef choose_model(...):\\n    raise NotImplementedError(\\"select primary then fall back via the router\\")\\n",
    "agent/prompts.py": "...working...",
    "agent/tools.py": "...working...",
    "invariants/test_agent.py": "...test_loop_bounded / test_fallback_on_5xx / test_cost_ceiling / test_quality...",
    "fixtures/tickets.jsonl": "...10 tickets + allowed policy labels...",
    "run.sh": "#!/usr/bin/env bash\\nset -euo pipefail\\npip install -q -r requirements.txt\\npython -m agent --selfcheck\\necho \\"ready\\"\\n",
    "requirements.txt": "langgraph\\nlitellm\\nanthropic\\nopenai\\npytest\\n",
    ".env.example": "ANTHROPIC_API_KEY=\\nOPENAI_API_KEY=\\n"
  }},
  "answer": {{
    "summary": "...",
    "root_causes": ["unbounded loop node", "no pre-call cost check", "primary 5xx not routed to fallback"],
    "expected_fixes": ["bound the loop to <= 6 model calls", "enforce_budget() blocks projected >$0.05 calls pre-call", "choose_model() routes to secondary on 5xx via the LiteLLM router"],
    "tradeoffs": ["latency vs reliability of fallback", "cost ceiling vs answer completeness"]
  }},
  "definitions": {{
    "model fallback": "...",
    "cost ceiling": "...",
    "bounded loop": "..."
  }},
  "hints": ["...", "..."],
  "outcomes": "A strong submission bounds the loop, routes to the fallback model on 5xx, enforces the cost ceiling pre-call, keeps replies on-policy, and ships production-clean code (clear naming, explicit error handling, structured logging, sensible structure).",
  "pre_requisites": ["Python 3.10+", "LangGraph", "LiteLLM model routing", "Anthropic/OpenAI SDKs", "pytest", "a provider API key via .env"],
  "short_overview": ["Make an unbounded, crash-prone support agent production-safe", "Bound the loop, add model fallback + cost ceiling", "Keep replies on-policy within budget"]
}}

## FINAL REMINDERS
- Output raw JSON only — exactly the keys: name, title, question, code_files,
  answer, definitions, hints, outcomes, pre_requisites, short_overview. Do NOT
  emit `criterias` (the pipeline injects it).
- Pick EXACTLY ONE scenario; honor its pinned Stack; map its fields field-by-field.
- Ship the defect UNFIXED + candidate stubs raising NotImplementedError in
  code_files; the reference fix lives ONLY in `answer`.
- The run.sh readiness probe must match the TASK FAMILY and obey all five
  readiness invariants (no stub call, no candidate-work dependency, LLM-free at
  the gate, key-gated ping, never run the unbounded loop / hard-require the key).
- Invariants ship as candidate-facing pytest tests, never as a generation gate.
- `outcomes` must include one bullet on production-clean code (naming, error
  handling, logging, structure).
- Never leak the reference answer into code_files.
- Keep it ADVANCED, build-it, and solvable in {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (ADVANCED)": [
        PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_CONTEXT,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_ADVANCED_INSTRUCTIONS,
    ]
}
