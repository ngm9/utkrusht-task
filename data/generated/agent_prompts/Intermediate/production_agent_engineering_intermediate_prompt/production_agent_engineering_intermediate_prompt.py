# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


# task_generation_prompts/Intermediate/production_agent_engineering_intermediate_prompt.py
#
# CURATED task-generation prompt module for Production Agent Engineering
# Competency: "Production Agent Engineering" · Proficiency: INTERMEDIATE
#
# Contract:
#   * Export PROMPT_REGISTRY.
#   * Registry key must be exactly "Production Agent Engineering (INTERMEDIATE)".
#   * Values are prompt strings replayed as sequential user turns.
#   * The only legal single-brace placeholders inside prompt strings are:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     Every other literal brace inside prompt strings is doubled.

PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_CONTEXT = """
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
who can build and harden production LLM agents, integrate them with business
systems, and reason about reliability, safety, observability, and bounded tool
execution.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic, INTERMEDIATE "build-it" assessment task for a
Production Agent Engineering candidate. This is a coding session, NOT a
write-a-memo, essay, quiz, or framework trivia exercise.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget
it as: ~5-10 min setup, ~5-10 min reading the scaffold and fixtures, and
20-30 min writing code. Hold "candidate writes" to 1-2 focused files, roughly
60-150 lines total, isolating ONE production-agent decision or at most two
tightly-related decisions.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

You MUST draw inspiration from ONE of the real-world scenarios provided above to
create the task. Use the provided real-world scenario as the basis for this task -
do not invent a different domain. When multiple scenarios are listed, pick the
one whose technical surface area best fits the candidate level. The task scenario
should closely align with the business context, technical requirements, and
domain described in the selected real-world scenario.

The generated repository must be a FULLY FUNCTIONAL, deliberately incomplete
production-agent service or CLI with:
- a REAL LLM/agent loop using a real provider SDK or router such as LiteLLM,
  OpenAI SDK, Anthropic SDK, LangChain, or LangGraph;
- PostgreSQL infrastructure because the provided scenarios exercise persisted
  business state such as pending confirmations, service orders, tool-call logs,
  idempotency keys, or retry-safe records;
- candidate-facing stubs that raise `NotImplementedError` for the agent logic
  under assessment, such as confirmation gating, typed tool validation,
  idempotency, retry-safe tool dispatch, bounded escalation, structured error
  handling, or audit logging;
- candidate-facing tests or invariant checks that demonstrate the expected
  behavior after the candidate completes the work;
- `run.sh` that installs dependencies, starts PostgreSQL with Docker Compose,
  waits for readiness, verifies database connectivity, imports/loads the starter
  app, and exits 0 on the UNSOLVED starter without running the grader tests.

The repository must NOT contain a FakeLLM, StubLLM, regex/keyword intent parser
standing in for the model, a deterministic replacement for the LLM, or sleeps
that simulate agent or tool thinking. The candidate's code is the production
agent logic around a real model call.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in production LLM agents, you are
given a list of real world scenarios and proficiency levels for Production Agent
Engineering. Generate ONE INTERMEDIATE build-it task that asks the candidate to
harden a real, runnable production agent integrated with PostgreSQL-backed
business state.

The generated task must be FULLY FUNCTIONAL as a starting environment and
deliberately incomplete in the assessed areas. It must contain a real LLM/agent
loop that calls a real provider through LiteLLM, OpenAI SDK, Anthropic SDK,
LangChain, LangGraph, or equivalent runtime SDK. The candidate-filled stubs ARE
the assessed agent logic: confirmation gates, tool validation, tool dispatch,
retry/idempotency handling, structured output parsing, error handling,
escalation, observability, or state management. They are NOT a fake model.

**CRITICAL**: Do not generate a FakeLLM, StubLLM, deterministic stand-in for the
model, regex or keyword intent parser as the agent decision-maker, or
`time.sleep()` / `asyncio.sleep()` to simulate agent or tool work. A real
production-agent task must exercise a real model loop; the readiness gate may be
LLM-free, but the task itself must not replace the model.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate AI Agent Engineer. They should be able to
design and implement LLM-driven production agents with reliability, observability,
security, bounded autonomy, escalation points, structured outputs, and safe tool
integration. They have a few years of experience and should be able to complete
a focused production-hardening task within {minutes_range}.

This task should sit above basic framework wiring and below a broad senior
platform build. It should probe practical judgment in one production-agent
failure mode drawn from the selected scenario: unsafe tool execution, missing
confirmation state, invalid tool arguments, duplicate side effects on retries,
missing idempotency, weak audit logging, brittle structured-output handling, or
poor graceful degradation.

The employer described in the company context is administering the assessment.
The employer's industry is not necessarily the task domain. Use ONE of the
provided real-world scenarios as the domain and do not drift into the employer's
domain unless the selected scenario explicitly matches it.

## INSTRUCTIONS

### Nature of the Task
- Generate a build-it coding task, not a memo, quiz, or system-design-only
  exercise.
- The candidate receives a FULLY FUNCTIONAL repository under `/root/task` with
  Python source, a package dependency manifest, PostgreSQL infrastructure,
  fixtures, candidate-facing tests, `run.sh`, `kill.sh`, `.env.example`,
  `.gitignore`, and a concise `README.md`.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base
  directory. Scripts must `cd /root/task` before running project commands.
- The selected scenario is the source of truth for domain, business entities,
  endpoint shape, tool names, database tables, and production symptom. Do not
  invent a different business domain.
- **CRITICAL**: Keep the task focused on Production Agent Engineering at
  INTERMEDIATE level. The candidate should implement one coherent production
  safety improvement, such as:
  - requiring explicit confirmation before a destructive tool call and persisting
    pending confirmation state;
  - validating typed LLM tool-call arguments before dispatch and returning a
    structured validation error;
  - making a side-effecting tool idempotent across retries with a stable request
    key;
  - enforcing bounded tool execution with audit logs and graceful escalation.
- Do not stack three or more unrelated concerns. A single scenario may include
  database persistence plus safe tool dispatch, but do not also require a full
  vector store, multi-agent supervisor, CI/CD pipeline, and eval framework in the
  same task.
- The candidate should write roughly 60-150 lines across 1-2 stub files. The
  rest of the repository should be complete, readable, and production-flavored.
- The starter must include `NotImplementedError` stubs in the assessed logic.
  Stub messages should neutrally describe the contract and must not reveal the
  implementation.
- The app must include a real LLM call path. The candidate may configure their
  provider key in `.env`; `.env.example` must show the needed variables.
- The generation-time readiness gate must not require a provider key and must not
  run the incomplete agent loop. It should import the app, validate static
  fixtures, connect to PostgreSQL, and optionally perform a provider ping only
  when a key is present.
- Candidate-facing tests under `tests/` or `invariants/` are allowed and
  encouraged, but `run.sh` must NOT run the grader or failing solved-behavior
  suite. The candidate/grader runs tests separately after implementation.
- If you include diagrams, ensure they are written in mermaid format, properly
  indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Python
documentation, PostgreSQL documentation, OpenAI/Anthropic/LiteLLM/LangGraph
documentation, and AI-powered tools, agentic IDEs, or Large Language Models
(LLMs).

- The assessment evaluates the candidate's ability to understand, modify, and
  harden production-oriented agent code, not their ability to memorize APIs.
- Candidates may use AI assistance to explore implementation options, but they
  remain responsible for code correctness, safety, readability, and tradeoffs.
- The task should be difficult enough that blind copy/paste from an AI tool is
  unlikely to produce a complete, safe solution without understanding the code.
- Do not include any instruction that prohibits external resources or AI tools.

## Code Generation Instructions
Generate a Python project that can run locally from `/root/task`. Use Python as
the runtime and include `requirements.txt` for third-party dependencies. The
primary runtime itself is already installed by the environment; do NOT install
Python with `apt-get` or system package commands. The task's own dependencies are
not pre-installed, so `run.sh` must install them first with
`pip install -q -r requirements.txt`.

The repository should typically include:
- `app/` or `agent/` package modules for configuration, database access, LLM
  client wrapper, tool definitions, orchestration, endpoint or CLI entry point,
  and candidate stub logic.
- A real model client wrapper using LiteLLM, OpenAI SDK, Anthropic SDK, or a real
  agent framework. This wrapper must be complete and not a candidate stub.
- A FastAPI endpoint if the selected scenario is HTTP-shaped, such as
  `POST /api/utilities/agent/move`, `POST /api/iot/agent/device-help`, or
  `POST /api/leasing/agent/start-screening`; otherwise provide a CLI entry point.
- A real tool-dispatch path where the LLM output is parsed or tool-called and the
  candidate logic gates, validates, persists, or deduplicates the side effect.
- PostgreSQL access code using a normal Python driver such as `psycopg` or
  SQLAlchemy. Keep schema and queries small enough for the time limit.
- Candidate-facing tests under `tests/` or `invariants/` that exercise the
  business invariant from the selected scenario.
- Realistic fixtures with accounts, devices, conversations, sessions, applicant
  records, tool-call logs, or vendor-call rows as appropriate.

**CRITICAL**: The model must be real in the task path. You may make readiness
skip the model call when no key is present, but do not ship fake model classes,
fake chat-completion functions, keyword routers, or deterministic model
substitutes as part of the assessed agent behavior. The candidate should improve
the production logic around a real model call.

## Infrastructure Requirements
This is an infra-shaped task. The generated repository MUST include
`docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`. It must use
PostgreSQL because the selected scenarios require persisted business state,
transactional side-effect records, confirmation/session state, tool-call logs,
or idempotency keys.

Do not include unrelated infrastructure. Do not add Redis, MySQL, Qdrant, Kafka,
or any other service unless the selected scenario explicitly requires it. For the
given scenario set, PostgreSQL is the correct datastore.

### Docker-compose Instructions
Create `docker-compose.yml` for PostgreSQL only.

Requirements:
- **MUST NOT include any version specification** at the top of the compose file.
- Service name should be clear, such as `postgres` or `agent-postgres`.
- Use an official `postgres` image.
- Include the standard PostgreSQL initialization environment variables inline in
  the service:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- The init SQL, healthcheck, and application connection string must use the same
  user and database.
- Do not use `.env` files or host-variable indirection such as `${{POSTGRES_USER}}`
  for datastore initialization. Inline service environment values are required
  because the image will not initialize without them.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using
  `127.0.0.1:5432:5432`.
- Mount `./init_database.sql` into `/docker-entrypoint-initdb.d/init_database.sql`
  as read-only.
- Include a healthcheck using `pg_isready` with the same user and database.
- Use a named volume for PostgreSQL data.
- Use a named project/network convention that is easy for `kill.sh` to clean.

### init_database.sql Instructions
Create `init_database.sql` that fully initializes the database for the selected
scenario. It must be FULLY POPULATED with enough rows for the starter app and
tests to run.

The schema should be small and focused. Depending on the selected scenario, it
may include:
- utilities move-service tables such as `move_sessions`, `service_accounts`,
  `service_orders`, and `agent_audit_events`;
- IoT firmware tables such as `devices`, `firmware_jobs`, `tool_call_logs`, and
  `agent_validation_events`;
- leasing screening tables such as `screening_orders`, `screening_vendor_calls`,
  `applicants`, and `agent_audit_events`.

Requirements:
- Include `DROP TABLE IF EXISTS` statements or an idempotent initialization
  pattern so repeated setup is predictable.
- Include primary keys and the minimal constraints needed to make the production
  behavior meaningful.
- For idempotency tasks, include a unique constraint on the stable idempotency
  key.
- For confirmation-gate tasks, include a session table that can persist pending
  confirmation state across turns.
- For validation tasks, include logs or job tables that show invalid tool calls
  are not executed.
- Seed 5-10 realistic rows with IDs and values that match fixtures, tests,
  README, and question text.
- Do not include secrets or real customer data.

### Run.sh Instructions
Create `run.sh` as a readiness/self-check script, not a grader.

Requirements:
- Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
- `cd /root/task`.
- First install Python dependencies with `pip install -q -r requirements.txt`.
- Start PostgreSQL with Docker Compose using `docker compose up -d --wait` or an
  equivalent `docker compose up -d` followed by an explicit health wait loop.
- Verify PostgreSQL readiness with a small connection check or `psql`/Python
  round-trip. If using Python, the check should insert/read/delete or select from
  a known table without calling candidate stubs.
- Run an import/static app readiness check, such as `python -m app --selfcheck`
  or `python -m agent --selfcheck`.
- If the app is a FastAPI service, `run.sh` may start it briefly and check
  `curl -sf http://127.0.0.1:8000/health`, then stop it. Do not leave a hanging
  foreground process.
- The readiness probe must pass on the UNSOLVED starter repository. It must not
  run the candidate-facing tests that are expected to fail before the candidate
  fills stubs.
- The readiness probe must not require a provider API key and must not run the
  incomplete agent loop.
- It may include a key-gated direct provider ping only if a key is present, but
  it must skip this ping cleanly when no key is set.
- End by printing a clear success message such as `ready`.

## kill.sh file instructions
Create a `kill.sh` script that aggressively and idempotently cleans the task
environment. The script must follow this shape:

1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print a log line explaining that cleanup is starting.
3. `cd /root/task || true`.
4. Stop containers with `docker compose down --remove-orphans || true`.
5. Remove volumes associated with the compose project with
   `docker compose down -v --remove-orphans || true` and, if needed,
   explicit `docker volume rm ... || true`.
6. Remove networks associated with the compose project with
   `docker network rm ... || true`.
7. Force-remove task-specific images if any were created, using
   `docker image rm -f ... || true`. If no app images are created, still print
   that there are no task-specific app images to remove.
8. Run `docker system prune -a --volumes -f || true`.
9. Remove the task directory with `rm -rf /root/task || true`, print logs at
   every step, and end with the exact message `Cleanup completed successfully!`.

Every destructive command should use `|| true` where appropriate so cleanup is
idempotent. Do not require user input.

The output should be a valid json schema:
- `README.md`: Candidate-facing README with exactly the four required sections
  specified below.
- `requirements.txt`: Python dependency manifest. Include only libraries the
  project imports, such as `fastapi`, `uvicorn`, `psycopg`, `pydantic`,
  `python-dotenv`, `litellm` or provider SDK, and `pytest`.
- `.env.example`: Provider API key placeholders and database connection string
  matching docker-compose values. Do not include real secrets.
- `.gitignore`: Standard Python, environment, cache, and local database ignores.
- `docker-compose.yml`: PostgreSQL service with localhost-only port binding,
  inline initialization environment, healthcheck, init SQL mount, and named
  volume.
- `init_database.sql`: Complete schema and seed data for the selected scenario.
- `run.sh`: Readiness script that installs dependencies, starts PostgreSQL,
  checks database/app readiness, and exits 0 on the unsolved starter.
- `kill.sh`: Idempotent cleanup script following the nine-step shape above.
- `app/` or `agent/` source files: Complete scaffold plus `NotImplementedError`
  candidate stubs in the assessed production-agent logic.
- `tests/` or `invariants/` files: Candidate-facing tests for the selected
  scenario's production invariant. These are not run by `run.sh`.

## Code file requirements
The generated `code_files` must be a flat mapping of file path to complete file
contents. Do not use nested file objects.

Code quality requirements:
- All source files must be syntactically valid and importable.
- Keep the project small but real: 8-14 files is appropriate for this infra
  task.
- Candidate stubs must be isolated and obvious from `NotImplementedError`, but
  comments and docstrings must not reveal the solution.
- The app must include structured logging or audit-event hooks appropriate to
  production agent behavior.
- Database queries should be parameterized.
- Tool-call inputs should use typed request/response models where appropriate.
- The real LLM client wrapper must be complete and must call a real SDK/router
  on the live task path. It must not be a candidate stub.
- Use `.env.example` for provider keys and local database connection settings.
- Avoid heavyweight dependencies not needed for the scenario.
- Ensure all scripts use Unix line endings and are executable in intent.
- Ensure all IDs, endpoint paths, table names, tool names, and fixture values
  match across code, SQL, tests, README, and question.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` appropriate for a local Python agent project. Include:
- Python caches: `__pycache__/`, `*.pyc`, `.pytest_cache/`
- Virtual environments: `.venv/`, `venv/`, `env/`
- Local environment files: `.env`
- Coverage and build outputs: `.coverage`, `htmlcov/`, `dist/`, `build/`
- Editor/system files: `.DS_Store`, `.idea/`, `.vscode/`
- Local logs and temporary files: `*.log`, `tmp/`

Do not ignore files required by the task such as `init_database.sql`,
`docker-compose.yml`, fixtures, tests, or `.env.example`.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the
implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and
guidance to help them discover solutions.

The candidate-facing README must contain EXACTLY these output sections, in this
order, and no others:
1. `## Task Overview`
2. `## Helpful Tips`
3. `## Objectives`
4. `## How to Verify`

### Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describes the business scenario, current state, observable production symptom,
  and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Do not name stub files, functions, database constraints, or exact tests.
- Do not reveal the fix.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: `Consider`, `Think about`, `Explore`,
  `Review`, or `Analyze`.
- Tips guide discovery — they MUST NOT name the specific API, library, function,
  pattern, data structure, or algorithm that solves the task.
- Do not include setup commands.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical
  implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to
  use.
- Do not enumerate source files, function names, SQL constraints, or invariant
  thresholds as a checklist.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify
  and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as readiness
  output, response shape, database row count, log line, repeated retry behavior,
  or test output.
- Do not include database credentials, hostnames, ports, usernames, passwords,
  client-tool suggestions, or `<DROPLET_IP>` placeholders.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README
section)**:
Keep all of the following OUT of the README:
- Setup commands such as `npm install`, `pip install`, `docker compose up`,
  `mvn test`, `pytest`, or similar command recipes.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware",
  "create this class", or "use this specific API".
- Database-connection details such as host, port, username, password, database
  name, or client-tool suggestions.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each key
must be filled with complete task data, not placeholders. Do NOT emit
`criterias`; the pipeline injects it.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the task and is different from the display title.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, clearly describing the production-agent hardening work without duplicating the repository name.",
  "question": "The full candidate-facing task description written like a realistic work ticket or incident-channel message. It should state the observable production symptom, the business impact, the high-level desired outcome, the need to configure their own provider key, and that they should run the provided readiness script, without naming the exact stub functions or giving implementation steps.",
  "code_files": "An object mapping every required file path to its complete file contents as a flat path-to-string dictionary. Include README.md, requirements.txt, .env.example, .gitignore, docker-compose.yml, init_database.sql, run.sh, kill.sh, Python source files, fixtures if used, and candidate-facing tests or invariants. File contents must be solution-free where candidate work is expected.",
  "answer": "Evaluator-facing high-level solution guidance that summarizes the expected root cause analysis, the shape of a strong implementation, important tradeoffs around safety, reliability, latency, cost, and observability, and the evidence reviewers should look for. Do not include a full filled solution repository here.",
  "definitions": "An object of concise term-to-definition pairs for domain and production-agent terms used in the task, such as confirmation gate, idempotency key, tool validation, structured tool error, audit event, bounded autonomy, or provider key.",
  "hints": "A single line nudging the candidate toward investigating the agent flow, persisted state, tool boundary, retry behavior, and observable side effects without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable production-agent behavior, safe tool execution, correct persistence, graceful error handling, and production-clean code. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Python, local shell usage, Docker Compose, PostgreSQL basics, HTTP or CLI testing as appropriate, provider API key configuration, and practical understanding of LLM tool-calling or agent orchestration.",
  "short_overview": "A bullet list summarising the business problem, the production-agent technical focus, the provided infrastructure, and the expected safe end-state."
}}

Use these EXACT keys. Do NOT use synonyms such as `task_title`, `files`,
`repository`, `context`, `prompt`, `solution`, or `steps`. Output raw JSON only
with no markdown fences or commentary.

## CRITICAL REMINDERS
- Output raw JSON only — no markdown fences, no prose before or after the JSON.
- The JSON must contain exactly these keys: `name`, `title`, `question`,
  `code_files`, `answer`, `definitions`, `hints`, `outcomes`,
  `pre_requisites`, and `short_overview`.
- The task must be based on ONE provided real-world scenario. Do not invent a
  different domain.
- Because this is an infra-shaped task, include `docker-compose.yml`,
  `init_database.sql`, `run.sh`, and `kill.sh`.
- Use PostgreSQL only; do not invent unrelated datastores.
- `docker-compose.yml` MUST NOT include a version specification.
- PostgreSQL compose configuration must use inline `POSTGRES_USER`,
  `POSTGRES_PASSWORD`, and `POSTGRES_DB` values, and must bind the exposed port
  to `127.0.0.1:5432:5432`.
- `run.sh` must install dependencies first, start PostgreSQL, wait for health,
  verify database/app readiness, and exit 0 on the unsolved starter. It must not
  run the failing candidate-facing tests or grader suite.
- `kill.sh` must be idempotent and end with `Cleanup completed successfully!`.
- The task must integrate a REAL LLM/agent loop through a real provider SDK or
  router. Do not include FakeLLM, StubLLM, keyword routers, deterministic model
  substitutes, or sleep-based simulations.
- The readiness gate may skip model calls when no key is present, but the task
  itself must require the candidate to work around a real model call path.
- Candidate stubs should raise `NotImplementedError` and should not contain
  comments, docstrings, or names that reveal the solution.
- README.md must contain exactly `## Task Overview`, `## Helpful Tips`,
  `## Objectives`, and `## How to Verify`, in that order, with no other
  candidate-facing sections.
- Never leak the reference answer into `code_files`, README, comments, fixtures,
  or hints.
- Keep the task INTERMEDIATE, focused, practical, and solvable within
  {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (INTERMEDIATE)": [
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_CONTEXT,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS,
    ]
}