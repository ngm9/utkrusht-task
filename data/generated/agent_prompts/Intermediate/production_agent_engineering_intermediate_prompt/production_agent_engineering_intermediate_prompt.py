# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


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
the selected real-world scenario explicitly matches it. Do not drift the task
into the employer's domain. You are generating an assessment for an intermediate
AI Agent Engineer who can build and harden production-grade LLM agents, context
pipelines, retrieval/tool integrations, and reliability controls.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic INTERMEDIATE build-it assessment task for a
Production Agent Engineering candidate. The candidate receives a runnable local
Python agent project with an external datastore started by docker-compose, reads
the provided code and tests, and completes a small production hardening change.
This is a coding task, NOT a system-design essay, quiz, or framework trivia test.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget
it as a short setup/read phase plus one focused implementation pass. The
candidate should generally write or change 1-2 files and roughly 60-140 lines of
code, with enough surrounding scaffold to feel like a real production agent repo.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

You MUST draw inspiration from ONE of the real-world scenarios provided above to
create the task. Use the provided real-world scenario as the basis for this task -
do not invent a different domain. When multiple scenarios are listed, pick the
one whose technical surface area best fits the candidate level and the required
infra-shaped repository. The task scenario should closely align with the business
context, technical requirements, and domain described in the selected real-world
scenario.

Because this prompt is for an infra-shaped task, select or shape the scenario so
the candidate uses a real external service through docker-compose. Good fits are
agent/tool reliability or context-pipeline tasks backed by Redis, Postgres, or a
small local service dependency from the selected scenario. Do not add unrelated
datastores. The datastore must be required by the work item, not decorative.

CORE JOB — BUILD ONE AGENT REPO from these fields:
  **Stack:** Python agent service or CLI, pytest invariant tests, and the selected
  datastore dependency started by docker-compose.
  **Domain:** The concrete business setting from the selected scenario.
  **Candidate writes:** The one or two implementation files containing focused
  stubs or intentionally incomplete logic.
  **Provided broken:** The production defect, such as repeated tool calls without
  cache, missing timeout/retry around an MCP-style tool, unsafe retrieval/context
  assembly, or incomplete fallback behavior.
  **Invariants:** Candidate-facing tests that prove the observable production
  behavior is fixed.
  **Senior signal:** The one production judgment being assessed, such as bounded
  tool reliability, datastore-backed caching, tenant-safe context retrieval,
  structured failure propagation, or latency/cost-aware context assembly.

Before generating, briefly internalize:
1. Which real-world scenario you selected and why it fits Production Agent
   Engineering at INTERMEDIATE proficiency.
2. Which external datastore or service is actually needed and how docker-compose
   will start it.
3. Which exact code path the candidate must improve without expanding the task
   into a whole platform.
4. How run.sh proves the environment is FULLY FUNCTIONAL without requiring the
   candidate to have already solved the task.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in production LLM agents, context
pipelines, tool orchestration, and reliability engineering, you are given a list
of real world scenarios and proficiency levels for Production Agent Engineering.
Generate ONE INTERMEDIATE build-it assessment task that ships a FULLY FUNCTIONAL
local project scaffold and a FULLY POPULATED external datastore or service
configuration. The candidate must complete a focused production hardening change
inside the scaffold.

The generated task must evaluate whether the candidate can distinguish a
prototype agent from a production agent: clear behavior under failure, bounded
latency/cost, safe tool or context handling, structured errors, observability,
and tests that capture business outcomes.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate AI Agent Engineer with a few years of practical
experience building agentic applications. They should be able to implement and
debug moderately complex context pipelines, tool integrations, retrieval flows,
and reliability controls, but they are not expected to design a multi-team agent
platform from scratch.

The company context describes who is administering the assessment. It is NOT the
task domain unless the selected real-world scenario says so. The assessment
domain must come from one of the provided real-world scenarios.

The task must fit in {minutes_range}. It should require practical engineering
judgment, but it must remain scoped to one focused production defect or
improvement. Avoid trivia, pure prompt-writing, broad architecture memos,
fine-tuning work, frontend tasks, or open-ended platform design.

## INSTRUCTIONS

### Nature of the Task
- Generate a runnable Python project for a production-style LLM agent, agent
  service, context pipeline, or tool-using workflow.
- **CRITICAL**: The task must be infra-shaped. The repository MUST include
  `docker-compose.yml`, `run.sh`, and `kill.sh`. It must include only the
  external datastore or service that the selected scenario actually exercises.
- **CRITICAL**: Do not create a decorative datastore. If the task is Redis-backed
  caching, Redis must be used in the implementation and tests. If the task is a
  Postgres-backed tool lookup, Postgres must be populated and used. If the
  scenario does not need an external service, choose a different provided
  scenario that does.
- **CRITICAL**: Keep the implementation focused on one production agent
  engineering decision: caching read-only tool results, timeout and retry with
  structured fallback, tenant-scoped retrieval, context budget enforcement,
  bounded tool repair, safe error propagation, or similar.
- **CRITICAL**: Do not stack three or more separate concerns. For example, do not
  ask for cache, retries, RAG ranking, model fallback, PII redaction, and tracing
  all in one task. One senior decision, or two tightly related ones, is enough.
- The candidate should complete the task by editing 1-2 files. Other files should
  be realistic scaffold, fixtures, tests, and documentation.
- The provided project should run locally from `/root/task`. **FILE LOCATION**:
  All code and scripts must reference /root/task as the base directory.
- The task may use a fake or deterministic local LLM adapter in tests so the
  readiness path and invariant tests do not require paid API calls. If the
  project includes optional real model configuration, it must be optional and
  key-gated.
- The question must read like a real incident-channel or engineering ticket:
  describe symptoms and business impact, not the implementation steps.
- The candidate-facing repo must not leak the solution. Stubs may raise
  `NotImplementedError` with a neutral one-line contract, but comments and README
  content must not reveal the fix.

Intermediate Production Agent Engineering scope includes:
- designing and implementing production-grade agents with clear reliability,
  observability, bounded autonomy, and security expectations;
- integrating agents with APIs, databases, vector stores, caches, and business
  systems through safe reusable tools;
- handling structured outputs, validation, retries, timeouts, fallbacks, and
  compensation logic;
- managing state, memory, context, and retrieval while respecting freshness,
  privacy, access control, and consistency;
- optimizing latency and cost by avoiding unnecessary LLM/tool calls and
  analyzing bottlenecks;
- using tests, traces, metrics, and logs to iteratively improve agent behavior.

Stay inside that scope. Do not require advanced distributed systems, Kubernetes,
custom model training, statistical evaluation frameworks, or vendor-specific
framework trivia.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Python
documentation, Redis or PostgreSQL documentation, agent framework documentation,
and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The assessment is designed to evaluate applied production engineering judgment,
  not memorization.
- Candidates may use AI tools to inspect code, explain errors, or draft changes,
  but the final implementation must satisfy the provided behavior and tests.
- The task should require enough repository-specific reasoning that a generic LLM
  answer is insufficient without understanding the scaffold.
- Do not prohibit AI usage in the README or question.

## Code Generation Instructions
Generate a complete, runnable local Python project. The project should look like
a realistic small production agent repository, not a toy script.

Recommended file shape:
- `README.md` with exactly the four required sections described below.
- `pyproject.toml` or `requirements.txt` defining the Python dependencies used by
  the scaffold.
- `src/agent_app/` or `agent_app/` modules for the agent workflow, tools,
  datastore client, context assembly, configuration, and CLI or service entry
  point.
- `tests/` or `invariants/` with candidate-facing pytest tests that exercise the
  production behavior after the candidate completes the task.
- `fixtures/` with realistic JSON, JSONL, or CSV records from the selected
  scenario.
- `docker-compose.yml` for the selected datastore or external service.
- `init_database.sql` only when the selected datastore is PostgreSQL and seed
  tables are required.
- `run.sh` and `kill.sh` at the repository root.
- `.gitignore`.

Use simple, maintainable Python. Prefer explicit function boundaries, typed data
structures where helpful, structured errors, clear logs, and small modules. The
candidate should not need to learn a large framework during the assessment.

If you include diagrams, ensure they are written in mermaid format, properly
indented and also in code blocks.

## Infrastructure Requirements
The repository MUST be infra-shaped. It must start the external datastore or
service with docker-compose and verify readiness locally. The generated task must
be safe to run in an isolated environment and deterministic enough for
assessment.

### Docker-compose Instructions
Create a `docker-compose.yml` file for only the datastore or service the selected
scenario actually requires.

Mandatory compose rules:
- `docker-compose.yml` **MUST NOT include any version specification**.
- `docker-compose.yml` **MUST NOT include environment variables or .env file
  references**.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using
  `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Include a healthcheck whenever the service supports a simple reliable health
  command.
- Use named volumes only when persistence is needed for the scenario. Otherwise
  keep the service ephemeral.
- Do not include an application container unless the task explicitly needs one.
  Prefer running Python locally and using compose only for Redis, Postgres, or
  the selected backing service.
- Do not add unrelated services such as admin UIs, dashboards, queues, or vector
  stores unless the scenario directly requires them.

For Redis scenarios:
- Use the official Redis image.
- Bind Redis to localhost only.
- The task should use Redis for the actual behavior under test, such as a TTL
  cache for read-only tool results.
- Do not cache tool errors or stale failure responses unless the selected
  scenario explicitly asks for that behavior.

For PostgreSQL scenarios:
- Use the official Postgres image.
- Bind Postgres to localhost only.
- Provide `init_database.sql` to create and seed the exact tables needed by the
  scenario.
- Do not include credentials in the README. Keep connection details inside code
  defaults or test configuration only.

### Datastore Initialization Instructions
If the selected scenario uses PostgreSQL, include `init_database.sql` with
realistic seed data. The file must create the tables, indexes, and rows required
for the task and tests. It must be idempotent where practical.

If the selected scenario uses Redis, do not include `init_database.sql`. Redis
starts empty, and the project or tests should populate keys through normal code
paths.

If the selected scenario uses another local service, include only the minimal
configuration or fixture files needed to make that service FULLY FUNCTIONAL.
Never include secrets.

### Run.sh Instructions
Create a `run.sh` file at the repository root.

`run.sh` requirements:
- Start with `#!/usr/bin/env bash`.
- Use `set -euo pipefail`.
- Change to `/root/task` before running commands.
- Start the external service with `docker compose up -d`.
- Wait for the datastore or service to become healthy before running the local
  readiness probe.
- Do not run `apt-get install`, `pip install`, `npm install`, or other package
  installation commands in `run.sh`. The runtime and common libraries are
  pre-installed by the template.
- Run a lightweight readiness check that proves the scaffold imports, connects to
  the datastore, and can perform a safe deterministic smoke test.
- The readiness check must not require the candidate to have solved the task.
- The readiness check must not call a paid LLM API or require API keys.
- End by printing a clear success message such as `ready`.

The readiness probe should verify that the repository is usable, not solved. It
may create and remove a Redis key, run a simple Postgres read, import the agent
modules, or call a local health endpoint. It must not invoke candidate stubs if
those stubs intentionally raise `NotImplementedError`.

## kill.sh file instructions
Create a `kill.sh` file at the repository root that fully cleans the task
environment and is safe to run multiple times.

The script must follow this 9-step shape:
1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print a log line explaining that cleanup is starting.
3. Change to `/root/task` if it exists; otherwise continue without failing.
4. Stop compose containers with `docker compose down --volumes --remove-orphans`
   and append `|| true` so cleanup is idempotent.
5. Remove task-specific Docker volumes and append `|| true`.
6. Remove task-specific Docker networks and append `|| true`.
7. Force-remove task-specific Docker images if any were built and append
   `|| true`.
8. Run `docker system prune -a --volumes -f` and append `|| true`, then remove
   `/root/task` with `rm -rf /root/task || true`.
9. Print logs at every step and finish with exactly
   `Cleanup completed successfully!`.

Every destructive command in `kill.sh` must be idempotent. Use `|| true` wherever
a missing resource should not fail cleanup.

The output should be a valid json schema:
- `README.md`: The complete candidate-facing README using exactly the four
  required sections and no solution leakage.
- `pyproject.toml` or `requirements.txt`: The native Python dependency manifest
  for the local project.
- `docker-compose.yml`: The compose file for the selected datastore or local
  backing service.
- `init_database.sql`: The PostgreSQL initialization file only when PostgreSQL is
  actually used by the selected scenario.
- `run.sh`: The executable readiness script that starts compose and verifies the
  scaffold.
- `kill.sh`: The executable cleanup script that removes containers, volumes,
  networks, images, and `/root/task`.
- `.gitignore`: The ignore file for Python caches, virtual environments, logs,
  local databases, and secrets.
- Source files: The Python agent, context, tool, datastore, and service modules
  needed by the task.
- Test files: Candidate-facing pytest tests or invariant checks that verify the
  required production behavior after completion.
- Fixture files: Realistic data used by the tests and scaffold.

## Code file requirements
The `code_files` value must be a flat object mapping file paths to complete file
contents. Do not nest files under folders as objects.

Code requirements:
- The repository must run from `/root/task`.
- Candidate-facing code must be incomplete in a realistic way, with focused
  stubs or flawed logic that the candidate can repair.
- The scaffold must import cleanly before the candidate solves the task.
- Tests must initially fail because of the intended defect or missing logic, not
  because of syntax errors, missing files, broken compose configuration, or
  inconsistent fixtures.
- Include deterministic tests that simulate relevant tool responses, timeouts,
  cache behavior, retrieval filtering, or context assembly behavior without
  requiring real LLM calls.
- Use realistic identifiers, timestamps, merchant names, restaurant IDs, route
  IDs, policy labels, tenant IDs, or document metadata that match the selected
  domain.
- Preserve internal consistency across question, README, code, tests, fixtures,
  compose, and initialization files.
- The answer field may describe the expected solution, but the candidate-facing
  repository must not include the solution.
- Do not include large generated datasets. Keep fixtures small but realistic.
- Avoid overfitting tests to exact implementation details. Tests should check
  observable outcomes such as attempts logged, p95 latency proxy, cache hit
  behavior, structured fallback shape, tenant isolation, or context budget
  compliance.

## .gitignore INSTRUCTIONS
Include a `.gitignore` file appropriate for a Python infra-backed local project.
It should ignore:
- `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- virtual environments such as `.venv/` and `venv/`
- `.env` and other local secret files
- local logs and temporary output files
- local database or cache artifacts if the scaffold creates any
- OS/editor files such as `.DS_Store` and `.vscode/`

Do not ignore source files, fixtures, tests, `docker-compose.yml`,
`init_database.sql`, `run.sh`, `kill.sh`, or README.md.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the
implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and
guidance to help them discover solutions.

The README.md file must contain exactly these output sections, in this order, and
no others:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

### Task Overview
Use the heading `## Task Overview`.

Write 3-4 meaningful sentences. No bullet list. Describe the business scenario,
current state, and why the problem matters. NEVER empty. NO bold time-budget
callouts. Do not name the stub files or functions. Do not directly reveal the
implementation approach.

### Helpful Tips
Use the heading `## Helpful Tips`.

Write 4-5 bullets max. Provide practical guidance without revealing specific
implementations. Each bullet starts with an action word: `Consider`, `Think
about`, `Explore`, `Review`, or `Analyze`. Tips guide discovery — they MUST NOT
name the specific API, library, function, pattern, data structure, or algorithm
that solves the task.

### Objectives
Use the heading `## Objectives`.

Write 4-6 bullets max. Frame objectives around outcomes rather than specific
technical implementations. Objectives describe the what and why, never the how.
Each bullet states an observable end-state, not a step or an API/library to use.

### How to Verify
Use the heading `## How to Verify`.

Write 4-6 bullets max. Frame verification in terms of observable outcomes.
Describe WHAT to verify and the expected behavior, not the specific
implementation to write. Each bullet is a check the candidate can run, such as
test output, response shape, latency observation, log line, cache reading, or
memory reading.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of README.md:
- Setup commands such as `npm install`, `pip install`, `docker compose up`,
  `mvn test`, or similar.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like `you should implement`, `add this middleware`, `create
  this class`, or `use this specific API`.
- Database-connection details such as host, port, username, password, client-tool
  suggestions, or placeholder IP addresses.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with exactly the canonical keys below and no
others. Each value in this schema is a description of what to fill in.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that is different from the display title and starts with an action-oriented verb.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, clearly describing the production agent engineering task.",
  "question": "The full candidate-facing task description written like a realistic engineering ticket or incident message, including symptoms, business impact, constraints, and how to start, without naming the hidden solution or implementation steps.",
  "code_files": {{
    "README.md": "The complete candidate-facing README with exactly Task Overview, Helpful Tips, Objectives, and How to Verify sections in that order.",
    "pyproject.toml": "The complete native Python project manifest or dependency configuration needed by the local scaffold.",
    "docker-compose.yml": "The complete compose file for the selected external datastore or service, following localhost binding, no version field, and no environment-variable reference requirements.",
    "run.sh": "The complete executable readiness script that starts compose, waits for service health, runs deterministic scaffold checks, and prints a ready message.",
    "kill.sh": "The complete executable cleanup script following the required idempotent nine-step cleanup shape.",
    ".gitignore": "The complete ignore file for Python caches, local environments, secrets, logs, and temporary artifacts.",
    "src_or_package_files": "The complete Python source files for the agent workflow, tools, datastore access, context assembly, configuration, and candidate stubs or flawed logic.",
    "test_or_invariant_files": "The complete pytest files that verify observable production behavior after the candidate completes the task.",
    "fixture_files": "The complete realistic fixture files used by the scaffold and tests, with internally consistent domain data."
  }},
  "answer": "Evaluator-facing high-level solution guidance describing root causes, expected fix shape, important tradeoffs, residual risks, and evidence in the provided files, without including full replacement code.",
  "definitions": "An object of concise term-to-definition pairs for domain and agent-engineering terms used in the task, such as TTL cache, structured fallback, context budget, tool timeout, tenant scope, or grounded response.",
  "hints": "A single line nudging investigation toward tracing the failing production path and reading the invariant tests, without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable reliability, latency, safety, cost, or context-quality improvements and production-clean code. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as Python, pytest, docker compose, the selected datastore basics, and intermediate production agent engineering concepts.",
  "short_overview": "A bullet list summarising the business problem, the technical focus, the external service used, and the expected observable outcome."
}}

Use these exact keys. Do NOT use synonyms such as `task_title`, `files`,
`repository_structure`, `context`, `prompt`, or `solution`. Do NOT emit
`criterias`; the pipeline injects it. Output raw JSON only — no markdown fences,
no commentary around the JSON object.

## CRITICAL REMINDERS
- Output valid raw JSON only.
- Generate one coherent infra-shaped Production Agent Engineering task.
- Use ONE provided real-world scenario as the business domain and technical
  basis. Do not invent a different domain when scenarios are present.
- Include `docker-compose.yml`, `run.sh`, and `kill.sh`.
- Include `init_database.sql` only when PostgreSQL seed data is required.
- Do not include docker-compose version specifications.
- Do not include environment variables or `.env` references in docker-compose.
- Bind every exposed datastore port to localhost using `127.0.0.1:<port>:<port>`.
- Keep the candidate work focused to 1-2 files and one production decision.
- The scaffold must be FULLY FUNCTIONAL before the candidate solves it; tests may
  fail only for the intended production defect.
- The readiness check must not call an LLM, require secrets, or invoke unsolved
  candidate stubs.
- README.md must contain exactly `## Task Overview`, `## Helpful Tips`,
  `## Objectives`, and `## How to Verify`, in that order.
- Never leak the reference answer into code files, README, comments, hints, or
  question text.
- Keep the task INTERMEDIATE and solvable in {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (INTERMEDIATE)": [
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_CONTEXT,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS,
    ]
}