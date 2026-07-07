# Set by the prompt-generator open-ended dial — do not edit.
# Consumed by infra.utils so the task row records which kind of task
# (specified vs withhold-the-solution) this combo produces.
OPEN_ENDED = True


# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


# task_generation_prompts/Intermediate/production_agent_engineering_redis_stream_orchestration_prompt.py
#
# CURATED task-generation prompt module for AI-agent BUILD-IT tasks.
# Competency: "Production Agent Engineering"  ·  Proficiency: INTERMEDIATE
#
# Contract:
#   * Export a top-level dict named exactly PROMPT_REGISTRY.
#   * Key it exactly "Production Agent Engineering (INTERMEDIATE)".
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal single-brace placeholders inside prompt strings are:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled so str.format() survives.

PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_CONTEXT = """
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
employer's domain. You are generating an assessment for an intermediate engineer
who has shipped production agents and can reason about orchestration, observability,
bounded autonomy, cancellation, and operational controls.
"""

PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic, INTERMEDIATE "build-it" assessment task for a
Production Agent Engineering candidate.

For this run, the task MUST be about an agent orchestration service that publishes
intermediate reasoning-step summaries / orchestration events to a Redis Stream and
allows a separate consumer process to monitor and cancel runaway agent tasks. The
events must be observable production traces, not private hidden chain-of-thought.
The candidate should work on the orchestration logic, stream publication, monitor
behavior, cancellation handling, and production safety around a real LLM call.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget it
as: ~5-10 min setup, ~5-15 min reading and running the scaffold, and ~20-30 min
writing code. Hold "candidate writes" to 1-2 stub files, roughly 60-150 lines,
isolating ONE senior production decision with at most one tightly-related supporting
decision.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CORE JOB — BUILD ONE AGENT REPO from these fields:
  **Stack:** Python 3.11, Redis Streams, redis-py asyncio client, a small agent
  orchestration service or CLI, pytest invariants, and a real LLM client through
  litellm or the OpenAI / Anthropic SDK.
  **Domain:** Use the provided real-world scenario as the basis for this task -
  do not invent a different domain. When multiple scenarios are listed, pick the
  one whose technical surface area best fits the candidate level. If no concrete
  scenario is provided, choose a realistic operations-heavy domain such as travel,
  logistics, legal intake, fintech operations, healthcare scheduling, or devtools.
  **Candidate writes:** A small orchestration / monitoring module whose bare stubs
  name only the symptom: runaway tasks are not observable or cancellable.
  **Provided broken:** The scaffold starts an agent task and calls a real model
  wrapper, but task progress is not safely surfaced to Redis and a separate monitor
  cannot stop runaway work without corrupting state.
  **Invariants:** Candidate-facing pytest tests and small fixtures that exercise
  observability, cancellation, stream consumption, and non-hanging behavior. These
  tests ship in the repo but are NOT run by run.sh.
  **Senior signal:** Production judgment around bounded autonomy, event design,
  cancellation, observability, and safety for a real LLM agent loop.

SCENARIO HANDLING — READ CAREFULLY:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to
  create the task.
- Use the provided real-world scenario as the basis for this task - do not invent
  a different domain. When multiple scenarios are listed, pick the one whose
  technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical
  requirements, and domain described in the selected real-world scenario.
- If the scenario list is empty or "(none provided)", design your own realistic
  production-agent domain, but keep the mandated Redis Stream orchestration and
  cancellation focus.

Before generating, briefly internalize:
1. The selected business domain and why Redis-streamed agent progress plus
   cancellation is a realistic production need there.
2. The exact task family: an agent orchestration service with Redis as the backing
   stream/control plane.
3. Which candidate stubs remain bare and open-ended, and which surrounding files
   are complete enough that ./run.sh passes on the unsolved starter.
"""

PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in production LLM agents, Redis-backed
coordination, and Python services, you are given a list of real world scenarios
and proficiency levels for Production Agent Engineering.

Generate ONE INTERMEDIATE Production Agent Engineering "build-it" task: a real,
runnable Python repository where an agent orchestration service publishes
intermediate reasoning-step summaries / orchestration events to a Redis Stream and
a separate monitor process can observe and cancel runaway agent tasks. The system
must call a REAL LLM through litellm or the OpenAI / Anthropic SDK on the
candidate's own key. The candidate's work is the production orchestration logic
around the real model: event publication, stream consumption, cancellation,
timeouts, state handling, observability, and bounded autonomy.

**CRITICAL**: the task must be open-ended. Underspecify the SOLUTION, never the
PROBLEM. The production symptom must be crisp: agent tasks become runaway,
operators cannot see reliable intermediate progress, and the monitor cannot cancel
work safely. Do NOT pre-decide the event schema, cancellation protocol, timeout
thresholds, status vocabulary, retry budget, or policy constants. The candidate
chooses and defends those tradeoffs through code.

**CRITICAL**: published Redis Stream entries may contain concise, operationally
useful summaries of intermediate reasoning steps, tool decisions, prompt phases,
model-call boundaries, and cancellation state. They MUST NOT expose hidden
chain-of-thought, secrets, raw provider payloads, or sensitive user data.

The generated repository must be FULLY FUNCTIONAL as a starting environment:
dependencies install, Redis starts, the package imports, static fixtures load, a
Redis readiness round-trip succeeds, and ./run.sh exits 0 on the unsolved starter.
It is deliberately incomplete only in the candidate stubs and planted production
behavior.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate Production Agent Engineering practitioner. They
should be comfortable implementing LLM-driven production agents with clear SLAs,
observability, safety boundaries, retries, state, bounded autonomy, cancellation,
and real external systems. They are not being asked to build a full platform, a
distributed scheduler, or an advanced multi-agent control plane.

Calibrate the task to a few years of applied experience:
- The candidate can read an existing Python agent service and identify where
  orchestration state, progress events, and cancellation should be handled.
- The candidate can integrate Redis Streams as a production observability/control
  mechanism without turning the exercise into Redis trivia.
- The candidate can reason about runaway loops, model calls, operator visibility,
  partial failures, cleanup, idempotency, and safe degradation.
- The candidate can call a real LLM and design operational guardrails around it.

## INSTRUCTIONS

### Nature of the Task
- Create a realistic build-it coding assessment, not a quiz, essay, memo, or pure
  design exercise.
- The selected scenario must involve an agent orchestration service that already
  launches or coordinates an LLM-backed task but does not give operators reliable
  progress visibility or safe cancellation.
- The task MUST include Redis Streams as the external datastore/control surface.
  The repo must include docker-compose.yml for Redis, run.sh to start Redis and
  verify readiness, and kill.sh to clean everything up.
- The task should be an agent-as-service or agent CLI/service hybrid. It may expose
  a tiny FastAPI API, or it may provide a CLI entry point plus a separate monitor
  process. Choose the simpler shape that best fits {minutes_range}.
- The separate consumer process must be a real component in the repo. It should
  read from the Redis stream or consumer group, surface progress, and request or
  observe cancellation of runaway tasks.
- The LLM path must be real. The candidate's orchestration code must call through
  a complete LLM client wrapper that uses litellm or the OpenAI / Anthropic SDK
  when AGENT_TEST_MODE is off. Do NOT use a FakeLLM, StubLLM, regex intent parser,
  keyword router, deterministic model stand-in, or sleeps to simulate thinking.
- AGENT_TEST_MODE may exist ONLY to keep readiness and candidate-facing invariant
  tests offline/key-free. It must not replace the task's real LLM requirement.
- The candidate-facing stubs MUST be bare: a function signature and a one-line
  purpose that names the symptom only. No "Expected shape" block, no required keys,
  no enum vocabulary, no policy constants, no threshold values, no reference to a
  named config constant, and no comments that reveal the solution.
- Do NOT pre-set the decision values that are the core signal: confidence floors,
  retry budgets, timeout budgets, freshness windows, stream field vocabulary,
  task-state enums, cancellation reasons, or maximum step counts. The candidate
  designs these.
- Candidate-facing README Objectives must state observable outcomes, not
  implementation steps. Helpful Tips must orient to the symptom and where to look,
  not name the API, library call, exact Redis command, schema, data structure, or
  algorithm that solves the task.
- How to Verify must describe observable end-states only. It may tell the candidate
  to run ./run.sh and the provided tests, but must not list exact hidden cases,
  fixtures, stream fields, thresholds, or status values.
- The problem design space must admit several defensible architectures: direct
  stream writes from the orchestrator, a trace adapter, cooperative cancellation,
  cancellation tokens, monitor-issued cancellation messages, stream-compacted
  state, or separate control keys are all possible. Do not pre-decide the approach.
- Keep the scope to ONE senior decision with at most one tightly-related support
  decision: observable orchestration plus cancellation for runaway work. Do NOT
  stack unrelated model fallback, RAG tuning, auth systems, billing, or complex
  multi-agent routing unless the scenario explicitly requires a tiny piece of it.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base
  directory.
- If you include diagrams, ensure they are written in mermaid format, properly
  indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Redis documentation,
Python documentation, LLM provider documentation, and AI-powered tools, agentic
IDEs, or Large Language Models (LLMs).

The assessment is not a memorization test. It evaluates whether the candidate can
understand a production agent failure mode, make sound engineering tradeoffs, and
deliver a safe, observable, runnable fix.

Candidates may use AI assistance for exploration, debugging, and implementation,
but the submitted code must be their own integrated solution and must satisfy the
behavioral requirements of the repository.

Do not forbid external resources in the README, question, or code comments.

## Code Generation Instructions
Generate a Python 3.11 project under /root/task. The project should be lean but
real, usually 9-14 files, with complete surrounding scaffold and bare candidate
stubs.

Recommended repo shape:
- `README.md` with exactly the four required sections described below.
- `requirements.txt` including the exact PyPI packages used, such as redis,
  python-dotenv, pytest, litellm or openai / anthropic, and fastapi / uvicorn only
  if a service API is actually used.
- `.env.example` declaring `OPENAI_API_KEY=` and/or `ANTHROPIC_API_KEY=`,
  `AGENT_TEST_MODE=0`, and Redis connection defaults appropriate for localhost.
- `agent_orchestrator/config.py` that loads environment and Redis URL defaults
  without hard-coding solution policy values.
- `agent_orchestrator/llm_client.py` that is complete and calls a real provider
  when test mode is off. It may return deterministic fixture responses only when
  `AGENT_TEST_MODE=1`.
- `agent_orchestrator/orchestrator.py` or similar, containing the incomplete
  orchestration behavior and bare candidate stubs.
- `agent_orchestrator/streaming.py` or similar, containing stream-publishing or
  stream-reading seams with bare stubs only where the candidate must design the
  production behavior.
- `agent_orchestrator/monitor.py` or similar, implementing the separate consumer
  process shape. It may be incomplete where the candidate must decide monitoring
  and cancellation behavior.
- `agent_orchestrator/__main__.py` with a selfcheck that imports all modules,
  validates fixtures, and performs a Redis readiness probe without calling
  candidate stubs or a live LLM.
- `fixtures/*.json` or `fixtures/*.jsonl` with realistic task requests and trace
  fragments drawn from the selected domain.
- `invariants/test_*.py` with candidate-facing tests that exercise the symptoms
  after candidates fill the stubs. These tests are NOT run by run.sh.
- `docker-compose.yml`, `run.sh`, and `kill.sh`.

Real LLM requirements:
- Ship a complete LLM wrapper; do not make provider plumbing the assessed stub.
- The live path must use litellm or a provider SDK and the candidate's own key.
- The test/offline path may use deterministic fixture responses only behind
  AGENT_TEST_MODE so readiness can run without a key.
- Never require the generation-time readiness gate to call a model.
- Never simulate agent thinking with time.sleep or asyncio.sleep. If tests need a
  runaway symptom, use bounded local fixture loops, cancellation checks, or
  deterministic test hooks, not fake latency.

Open-ended starter requirements:
- Candidate stubs must contain only a bare signature and one-line symptom purpose.
- No return-shape contract, no enum vocabulary, no exact stream field names, no
  sample implementation, no algorithm hints, and no policy constants.
- Any provided comments should explain the business symptom, not the fix.
- Keep code readable enough that candidates can discover where to work.

## Infrastructure Requirements
This is an infra-shaped task. The generated repository MUST include Docker-backed
Redis because Redis Streams are the external coordination surface of the scenario.

The infrastructure must be minimal and robust:
- Redis is the only required datastore unless the selected scenario absolutely
  demands another external service. Do not invent extra databases, queues, vector
  stores, or brokers.
- The Python application runs locally from /root/task; docker-compose is for Redis
  unless you explicitly choose an app container for a strong reason.
- `run.sh` is a readiness/self-check, NOT the grader. It brings Redis up, waits
  for health, verifies a Redis stream round-trip, installs dependencies, imports
  the starter project, and exits 0 on the UNSOLVED starter.
- `run.sh` MUST NOT run the candidate-facing pytest suite as a pass/fail gate
  because those tests are designed to fail until the candidate solves the task.
- All scripts must be executable in content and use /root/task as the base
  directory.
- Do not use `.env` files or host-variable interpolation for docker-compose
  initialization. Inline service environment values are allowed when needed.
- For Redis, no init SQL is needed and no database bootstrap file should be
  generated.

### Docker-compose Instructions
Generate `docker-compose.yml` for Redis.

Required docker-compose rules:
- **MUST NOT include any version specification**.
- Define a single Redis service unless the scenario truly needs more.
- Use a stable Redis image, for example `redis:7-alpine`.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using
  `127.0.0.1:6379:6379` for Redis. Do not expose Redis on all interfaces.
- Include a healthcheck using `redis-cli ping`.
- Use a named volume only if useful for stream durability during candidate runs.
  If a volume is used, kill.sh must remove it.
- Do not use host interpolation such as `$${{REDIS_PORT}}` or `.env` indirection
  inside docker-compose.yml.
- Do not include an app container unless you also include a Dockerfile and have a
  clear reason. Prefer running Python locally for this assessment.

### Redis Configuration Instructions
Redis should be configured simply and consistently:
- Use logical stream names that fit the scenario, but do not reveal the solution
  schema through exhaustive field lists in the README.
- The code may default to `redis://localhost:6379/0` or an equivalent local URL.
- Readiness must verify Redis with a harmless stream write/read/delete or trim
  operation that does not depend on candidate stubs.
- Candidate-facing tests may inspect Redis behavior, but run.sh must only perform
  a minimal round-trip and package selfcheck.
- The task should involve Redis Streams or consumer groups as the production
  event surface. Plain pub/sub alone is not sufficient for this directive.

### Run.sh Instructions
Generate `run.sh` as a readiness probe.

Required run.sh behavior:
1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. `cd /root/task`.
3. Install task dependencies as the FIRST operational step after changing
   directories: `pip install -q -r requirements.txt`.
4. Start Redis with `docker compose up -d`.
5. Wait for Redis health using docker compose health status or
   `docker compose exec -T redis redis-cli ping` in a bounded loop.
6. Perform a small Redis Stream readiness round-trip that does not invoke the
   candidate's unfilled orchestration stubs.
7. Run a package selfcheck such as `python -m agent_orchestrator --selfcheck`.
   The selfcheck must import modules, validate fixtures, and confirm configuration
   loads. It must not run the agent loop, call a candidate stub, or require a
   provider key.
8. If a provider key is present, the selfcheck may perform a tiny direct model
   ping through the completed LLM client only after all static checks pass. If no
   key is present, print a note and skip the ping.
9. Print a final ready message and exit 0 when the starter is deployable.

Because this is infra-shaped, run.sh should not use the non-infra pytest exit-code
contract. It must not run the grader or candidate-facing tests. The tests are run
separately by the candidate after they choose and implement their solution.

### kill.sh file instructions
Generate `kill.sh` to be aggressive, idempotent, and safe for repeated use. It
must:

1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print clear logs before every cleanup step.
3. Change to `/root/task` if it exists; otherwise continue cleanup from the
   current directory.
4. Stop containers with `docker compose down --remove-orphans || true`.
5. Remove any named Docker volumes created by the compose project with
   `docker volume rm ... || true`.
6. Remove any Docker networks created by the compose project with
   `docker network rm ... || true`.
7. Force-remove task-specific images if any were built, using `docker rmi -f ... || true`.
8. Run `docker system prune -a --volumes -f || true`.
9. Remove the task directory with `rm -rf /root/task || true`, then print
   `Cleanup completed successfully!`.

Every destructive command must be idempotent with `|| true` where appropriate.
The final message must be exactly `Cleanup completed successfully!`.

The output should be a valid json schema:
- `README.md`: candidate-facing overview with only the four required sections.
- `requirements.txt`: Python dependencies needed by the local project.
- `.env.example`: provider key placeholders and local Redis defaults.
- `docker-compose.yml`: Redis service with localhost-bound port and healthcheck.
- `run.sh`: readiness probe that installs dependencies, starts Redis, checks Redis,
  imports the package, and exits 0 on the unsolved starter.
- `kill.sh`: idempotent cleanup script following the nine-step cleanup shape.
- `agent_orchestrator/*.py`: complete scaffold plus bare candidate stubs for the
  open-ended orchestration and cancellation work.
- `fixtures/*`: realistic domain fixtures that reproduce the production symptom.
- `invariants/test_*.py`: candidate-facing tests that are shipped but not run by
  run.sh.

## Code file requirements
The generated `code_files` must contain a complete runnable starter repo.

General code quality:
- Use clear Python modules with explicit imports and type hints where helpful.
- Keep candidate-write surface small: 1-2 files and approximately 60-150 lines of
  candidate implementation.
- Surrounding scaffold must be complete and import cleanly.
- Do not include commented-out solutions, reference implementations, or TODOs that
  name the solution technique.
- Do not call candidate stubs from module import time, run.sh, or selfcheck.
- Do not leak hidden chain-of-thought in traces, logs, Redis stream entries, test
  fixtures, README, or comments.
- Model-call wrappers must be complete and safe enough for a candidate to use.
- Redis connections must close cleanly.
- Any background tasks, monitor loops, or async workers must terminate under
  selfcheck and tests; no indefinite loops in readiness.
- Candidate-facing tests can fail on the starter, but they must be syntactically
  valid and runnable after dependencies install.
- The task must be solvable without modifying docker-compose.yml or requirements
  unless the candidate chooses to add a small helper dependency.

Open-ended code constraints:
- Bare stubs only: one-line purpose naming the symptom and `raise NotImplementedError`.
- No exact expected dict keys, stream fields, enum names, return shape, thresholds,
  retry counts, timeout budgets, or maximum iteration constants in the stub
  docstrings.
- Fixtures and tests should expose the production problem through symptoms and
  observable behavior, not by handing the candidate a prescribed schema.
- Do not make a single exact architecture unavoidable; several defensible designs
  should be possible.

Redis and monitor requirements:
- Include a separate consumer/monitor entry point or module that can be run apart
  from the orchestrator.
- The monitor must be meaningful: it observes progress from Redis Streams and
  participates in cancellation or cancellation observation.
- Cancellation must be cooperative and safe, not process-kill-only.
- The system should preserve enough audit information for operators to understand
  what happened without exposing private model reasoning.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` suitable for a Python agent project:
- Ignore `.env`, virtual environments, caches, `__pycache__/`, `.pytest_cache/`,
  coverage files, build artifacts, local logs, and temporary Redis dump files.
- Do not ignore `.env.example`.
- Do not ignore fixtures, invariants, README, run.sh, kill.sh, docker-compose.yml,
  or source files.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the implementation
approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance
to help them discover solutions.

The candidate-facing README must contain EXACTLY these output sections, in this
order, and NO others:

### Task Overview
- Use the markdown heading `## Task Overview`.
- 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Describe the observable production symptom: runaway agent tasks are hard to
  monitor and cancel because progress and cancellation are not reliable.
- Do not name stub files, function names, stream schemas, exact Redis commands,
  or the solution approach.

### Objectives
- Use the markdown heading `## Objectives`.
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
  Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- For open-endedness, objectives must state the symptom and reproducible business
  outcome, not a checklist of functions to build or policies to set.
- Do not include exact thresholds, stream field names, status vocabularies, or
  cancellation protocol details.

### Helpful Tips
- Use the markdown heading `## Helpful Tips`.
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore",
  "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function,
  pattern, data structure, Redis command, schema, or algorithm that solves the task.
- For this open-ended task, keep tips few and symptom-oriented.

### How to Verify
- Use the markdown heading `## How to Verify`.
- 4-6 bullets max.
- Because this task calls a real LLM and ships `.env.example`, How to Verify MUST
  open with this GitHub note admonition embedded INSIDE the section as a blockquote,
  never as a new heading:
  `> [!NOTE]`
  `> Copy .env.example to .env and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.`
- Frame verification in terms of observable outcomes. Describe WHAT to verify and
  the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as readiness output, monitor
  output, stream-visible progress, cancellation observation, non-hanging behavior,
  test output, response shape, latency observation, log line, or memory reading.
- Do not list exact fixtures, exact cases, exact Redis fields, exact thresholds,
  or the expected internal policy.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
Keep all of the following OUT of the README:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, or other
  step-by-step command blocks beyond high-level verification references.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, Redis command names,
  or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create
  this class", "use this specific API", or equivalent solution-revealing wording.
- Database or Redis connection details such as host, port, username, password, or
  client-tool suggestions.
- `<DROPLET_IP>` placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each field
below describes what to fill in; do not output placeholders or examples.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that is distinct from the display title and reflects the Redis-streamed agent orchestration task.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, describing the production-agent orchestration and cancellation work.",
  "question": "The full candidate-facing task description written like a realistic incident or work-ticket message; it states the observable runaway-agent and monitoring/cancellation symptoms, mentions Redis Streams and the separate monitor at a high level, tells the candidate to set their provider key and run ./run.sh, and avoids naming stub functions or revealing the solution.",
  "code_files": "An object mapping every repository filepath to its full file contents as a flat path-to-content dictionary, including README.md, requirements.txt, .env.example, docker-compose.yml, run.sh, kill.sh, Python source files, fixtures, and candidate-facing invariant tests.",
  "answer": "Evaluator-facing high-level solution guidance that summarizes likely root causes, the properties of a strong fix, tradeoffs around observability/cancellation/safety/latency, and evidence reviewers should look for, without providing full filled solution files.",
  "definitions": "An object mapping important task terms to concise definitions, focused on production-agent concepts such as Redis Streams, cooperative cancellation, orchestration event, monitor consumer, bounded autonomy, real model call, and audit-safe trace.",
  "hints": "A single concise line nudging candidates to investigate the runtime symptoms and event flow without naming the implementation pattern, exact Redis commands, schema, thresholds, or cancellation design.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable production behavior: observable agent progress, safe cancellation of runaway work, no hidden reasoning leakage, real model integration, and production-clean code with clear naming, explicit error handling, logging, and sensible structure.",
  "pre_requisites": "A bullet list of assumed prior knowledge and skills using declarative capability phrases only, such as Python 3.11 proficiency, comfort with async or service-oriented agent code, familiarity with Redis-backed coordination, understanding of production LLM calls, and a provider key via .env.",
  "short_overview": "A bullet list summarising the business problem, the Redis-streamed orchestration focus, the separate monitor/cancellation requirement, and the expected observable outcome."
}}

Required field rules:
- Use exactly the canonical keys above. Do NOT use synonyms such as `task_title`,
  `files`, `repository`, `context`, `prompt`, `solution`, or `criteria`.
- `code_files` must be a flat object mapping filepath to file contents.
- `pre_requisites` must be declarative assumed knowledge only. NEVER include
  imperative setup or verification steps such as "Run...", "Use...", "Configure...",
  "Install...", or "Test...".
- `definitions` must define terms used in the task without naming the hidden
  solution.
- `hints` must not reveal the fix.
- `outcomes` must include production-clean code expectations.
- Output raw JSON only. No markdown fences, no commentary, no extra keys.

## CRITICAL REMINDERS
- The generated task MUST satisfy the directive: an agent orchestration service
  publishes intermediate reasoning-step summaries / orchestration events to a
  Redis Stream, and a separate consumer process monitors and cancels runaway agent
  tasks.
- This is Production Agent Engineering at INTERMEDIATE level. Stay within
  production robustness, observability, bounded autonomy, cancellation, safe state,
  real LLM calls, and operational controls. Do not turn it into an advanced
  distributed-systems platform or a pure Redis syntax exercise.
- The task is infra-shaped: include docker-compose.yml for Redis, run.sh, and
  kill.sh. Do not omit them.
- docker-compose.yml MUST NOT include any version specification.
- **SECURITY-CRITICAL**: Redis ports MUST be bound to localhost only using
  `127.0.0.1:6379:6379`.
- run.sh's FIRST project step must install dependencies with
  `pip install -q -r requirements.txt`.
- run.sh is readiness only. It must start Redis, verify health, do a harmless
  Redis Stream round-trip, import/selfcheck the package, and exit 0 on the
  unsolved starter. It must NOT run the candidate-facing pytest suite, call
  candidate stubs, run the agent loop, hang, or require an LLM key.
- The repo must call a REAL model through litellm or a provider SDK in normal
  operation. FakeLLM, StubLLM, regex/keyword model stand-ins, and sleeps that
  simulate thinking are forbidden.
- Open-endedness is mandatory: do not hand over event schemas, status enums,
  cancellation protocols, thresholds, retry budgets, timeout constants, or exact
  return contracts. Stubs are bare and symptom-only.
- README.md must contain exactly `## Task Overview`, `## Objectives`,
  `## Helpful Tips`, and `## How to Verify` in that order, with no extra README
  sections.
- The README must be concise, outcome-oriented, and non-revealing. It must not
  include setup commands, direct solutions, step-by-step guides, specific APIs,
  code snippets, exact Redis connection details, or a "NOT TO INCLUDE" heading.
- kill.sh must follow the nine-step cleanup shape, use `|| true` for idempotency
  where appropriate, run `docker system prune -a --volumes -f || true`, remove
  `/root/task`, and print `Cleanup completed successfully!`.
- All code and scripts must reference `/root/task` as the base directory.
- Never leak the evaluator-facing answer into code_files, README, comments, hints,
  definitions, fixtures, or tests.
- If diagrams are included, they must be mermaid diagrams in code blocks.
- The final response from the task generator must be valid raw JSON only, starting
  with `{{` and ending with `}}`.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (INTERMEDIATE)": [
        PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_CONTEXT,
        PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_REDIS_STREAM_INTERMEDIATE_INSTRUCTIONS,
    ]
}