# Set by the prompt-generator open-ended dial — do not edit.
# Consumed by infra.utils so the task row records which kind of task
# (specified vs withhold-the-solution) this combo produces.
OPEN_ENDED = False


# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_CONTEXT = """
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
who can build practical production-facing agents that choose tools, validate
arguments, chain tool outputs, cache safe intermediate results, and recover from
tool failures with sound judgment.
"""

PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic, INTERMEDIATE "build-it" assessment task for a
Tool Use for Agents candidate.

As a technical architect super experienced in Python, LLM tool-calling agents,
Redis, and PostgreSQL, you are given a list of real world scenarios and
proficiency levels for Tool Use for Agents. Create a runnable repository that
tests the candidate's ability to implement a real LLM-driven tool-using agent
with explicit tool contracts, multi-tool chaining, external state, and fallback
behavior.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget
it as: ~5-10 minutes setup, ~5-10 minutes reading the scaffold and tool traces,
and ~20-35 minutes implementing the focused tool orchestration logic.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

PRIMARY TASK SHAPE TO GENERATE:
Build a Python agent repository for a customer-report workflow where a real LLM
agent uses tools at the boundary:
- a Redis-backed cache tool stores and retrieves intermediate reasoning or
  normalized report-planning results so repeated report requests avoid redundant
  recomputation;
- a PostgreSQL-backed customer lookup tool retrieves customer records from a
  running database started by docker-compose;
- a formatting tool accepts the normalized customer record produced by the lookup
  tool and generates a concise report payload;
- the agent demonstrates tool chaining by passing the output of the PostgreSQL
  lookup tool into the formatting tool;
- the agent falls back to recomputation only when Redis misses or returns an
  invalid cache value;
- the task must include docker-compose.yml for Redis and PostgreSQL, an
  init_database.sql seed file, run.sh, and kill.sh.

SCENARIO HANDLING:
- You MUST draw inspiration from ONE of the real-world scenarios provided above
  to create the task when those scenarios are concrete.
- Use the provided real-world scenario as the basis for this task - do not invent
  a different domain. When multiple scenarios are listed, pick the one whose
  technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical
  requirements, and domain described in the selected real-world scenario.
- If no concrete scenario is provided, use a realistic customer-success or
  account-operations domain where an internal support agent generates customer
  account reports from system-of-record data.

Before generating the final task, briefly internalize:
1. The business workflow the agent is supporting and why Redis plus PostgreSQL are
   both necessary for the scenario.
2. Which candidate-written stubs isolate the intermediate-level tool-use signal:
   tool argument validation, tool output normalization, cache miss handling, and
   passing one tool's structured output into the next.
3. Which files are fully functional starter infrastructure and which files are
   deliberately incomplete.
4. How run.sh proves the environment is ready without solving the task or running
   the candidate-facing test suite as the deployability gate.
"""

PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
Generate ONE INTERMEDIATE Tool Use for Agents "build-it" task: a real, runnable
Python agent repository that is deliberately incomplete. The candidate fills
well-scoped stubs to make an LLM-driven agent reliably call a Redis cache tool, a
PostgreSQL customer lookup tool, and a report formatting tool in the correct
sequence.

The generated task MUST center on tool use at the boundary: clear tool schemas,
typed input/output contracts, validation before dispatch, multi-tool data flow,
cache-hit versus cache-miss behavior, and structured recovery from partial tool
failure. The repository must call a REAL model through a runtime SDK or router
using the candidate's own provider key. A fake LLM, keyword router, regex intent
parser, or deterministic stand-in for the model is not acceptable.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate AI Agent Engineer with a few years of experience
building or refining production-facing agents. They should be able to work with
Python, a real LLM client, Redis, PostgreSQL, typed tool contracts, structured
logging, pytest, and docker-compose-backed local services.

This is a coding session, NOT a write-a-memo, quiz, or framework trivia exercise.
The candidate should read a realistic agent scaffold, run the local services,
inspect the tests and traces, then implement a focused tool orchestration fix.
The task should be harder than a basic wiring exercise but below a full
advanced/senior platform build. Keep the candidate-written code to roughly
60-150 lines across 1-2 files.

The employer described in Company Context is administering the assessment. The
business domain of the generated task comes from the selected scenario or, if no
scenario is concrete, from a realistic customer account reporting workflow. Do
not turn this into the employer's domain by default.

## INSTRUCTIONS

### Nature of the Task
- **CRITICAL**: The task MUST implement a real LLM-driven tool-using agent. The
  candidate's work is the agent tool orchestration, not a fake model.
- **CRITICAL**: The agent must use Redis as a tool-accessed cache for
  intermediate reasoning or normalized planning/report inputs. On cache hit, the
  agent should reuse the stored intermediate result when it is valid. On cache
  miss or invalid cached data, it should recompute through the normal tool chain
  and update the cache.
- **CRITICAL**: The agent must use a PostgreSQL database tool to look up customer
  records. The database must be started by docker-compose and seeded by
  init_database.sql.
- **CRITICAL**: The agent must use a separate formatting tool that receives the
  structured output of the PostgreSQL lookup tool and produces a report-ready
  payload. This is the visible tool-chaining requirement: output from tool one is
  passed as input to tool two.
- **CRITICAL**: The candidate-facing scaffold may include explicit contracts,
  enum values, retry budgets, cache TTLs, and expected return shapes because this
  is a specified intermediate task. Do not make it a vague design essay.
- **CRITICAL**: The task must stay inside Tool Use for Agents at INTERMEDIATE
  proficiency: tool definitions, schemas, validation, tool chaining, fallback
  behavior, caching, traceability, and evaluation. Do not require fine-tuning,
  custom ML modeling, a multi-agent platform, advanced distributed systems, or a
  pure frontend implementation.
- The generated repository should be FULLY FUNCTIONAL as a starter environment:
  dependencies install, Redis and PostgreSQL start, the seed data loads, the
  package imports, selfcheck succeeds, and the candidate can begin work.
- The starter agent should be deliberately incomplete or flawed in a narrow way:
  for example, it may skip the cache, pass raw database rows directly to the LLM,
  fail to validate a cached payload, fail to pass the lookup result into the
  formatter, or collapse structured tool errors into a generic exception.
- Candidate-facing tests under a tests or invariants directory should exercise
  the intended behavior after the candidate solves the task, but run.sh must not
  use those tests as the deployability gate.
- If you include diagrams, ensure they are written in mermaid format, properly
  indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base
  directory.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Python
documentation, Redis documentation, PostgreSQL documentation, and AI-powered
tools, agentic IDEs, or Large Language Models (LLMs).

The task must be designed so that resource usage does not replace the assessed
skill. The assessment evaluates whether the candidate can inspect a realistic
agent scaffold, reason about tool boundaries, implement safe tool orchestration,
and validate behavior.

Candidates may use AI assistance to understand libraries or draft code, but they
remain responsible for the correctness, safety, and maintainability of their
submission.

Do not include any policy that forbids AI tools or external references. Do not
make the task depend on memorizing obscure API syntax.

## Code Generation Instructions
Generate a Python project using a native Python dependency manifest such as
requirements.txt or pyproject.toml. Python is the assumed runtime for this task.

The repository MUST include a real LLM client wrapper, for example
agent/llm_client.py, built on litellm, openai, or anthropic. The wrapper is
provided complete and is not the main candidate stub. The default task behavior
uses a real provider key from .env. The selfcheck path may use AGENT_TEST_MODE=1
or key-free static checks only for readiness, but the actual agent workflow must
call a real model when the candidate runs an end-to-end invocation with a key.

The generated code should include:
- a tool catalogue with explicit metadata, names, descriptions, JSON-like
  argument schemas, and structured result contracts;
- a Redis cache tool that can get, validate, set, and expire intermediate results;
- a PostgreSQL lookup tool that retrieves customer records using parameterized
  SQL and returns a normalized structured object;
- a formatting tool that receives the normalized lookup output and creates a
  report payload suitable for the final agent response;
- an orchestrator or agent runner that lets the LLM plan/select tool calls while
  code enforces validation, allowed tool names, structured errors, and the
  required lookup-to-format data flow;
- candidate stubs in 1-2 files that raise NotImplementedError and isolate the
  intended tool-use behavior;
- candidate-facing pytest tests or invariants that verify cache hits, cache
  misses, invalid cache fallback, PostgreSQL lookup normalization, tool chaining,
  and structured errors;
- fixtures or trace examples with realistic customer IDs and report requests.

For this specified intermediate task, stubs may include docstrings that state the
expected argument and return contracts. It is acceptable to provide constants
such as cache TTL, allowed report types, retry counts, or structured error codes
when those help keep the task focused and solvable within {minutes_range}.

Do NOT leak the full reference answer into code comments, README.md, or starter
files. The filled solution and expected fix details belong only in the answer
field.

## Infrastructure Requirements
This is an infra-shaped task. The generated repository MUST include
docker-compose.yml, init_database.sql, run.sh, and kill.sh. It MUST use
docker-compose to start both Redis and PostgreSQL. Do not omit either datastore.

The task must be runnable from /root/task. All scripts must cd to /root/task or
otherwise reference /root/task as the base directory. The candidate should be
able to clone/unpack the repository, copy .env.example to .env, add a provider
key, run ./run.sh to verify readiness, and then run the candidate-facing tests
separately while implementing the stubs.

run.sh is a READINESS/self-check, NOT the grader. It brings Redis and PostgreSQL
up, waits for health, verifies the seed data and Redis round trip, installs
Python dependencies, checks that the package imports, and exits 0 on the
unsolved starter. It MUST NOT run the candidate-facing pytest suite as a required
pass/fail gate because those tests are designed to fail until the candidate
solves the task.

### Docker-compose Instructions
Create a docker-compose.yml that starts exactly the datastore services needed by
this task: PostgreSQL and Redis. It must be complete and runnable.

- **MUST NOT include any version specification** in docker-compose.yml.
- PostgreSQL service must use an official postgres image and define the standard
  initialization environment variables inline in the service:
  POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB.
- The init SQL, healthcheck, and application connection string must use the same
  PostgreSQL user and database. The image will not initialize correctly without
  these inline service environment values.
- Redis service must use an official redis image and expose the standard Redis
  port only to localhost.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using
  127.0.0.1:<port>:<port> for every datastore exposed to the host. PostgreSQL
  should use 127.0.0.1:5432:5432 unless you choose a clearly documented alternate
  host port. Redis should use 127.0.0.1:6379:6379 unless you choose a clearly
  documented alternate host port.
- Do not use .env files or host-variable interpolation inside docker-compose.yml
  for required database initialization values. Inline service environment values
  are required.
- Add healthchecks for both services. PostgreSQL should use pg_isready with the
  configured user and database. Redis should use redis-cli ping.
- Mount init_database.sql into the PostgreSQL initialization directory so the
  seed schema and rows are loaded on first container start.
- Use named volumes for PostgreSQL and Redis data so kill.sh can remove them
  deterministically.

### init_database.sql and Redis Configuration Instructions
Create init_database.sql with a small but realistic customer-account dataset for
the chosen domain. The schema should be simple enough for an intermediate task
and should support lookup by customer_id or account_id.

The seed data should include:
- 5-8 customers or accounts with realistic IDs, names, plan/status fields, dates,
  support tier, risk flags, or recent activity fields relevant to the scenario;
- at least one missing or inactive customer case for structured error handling;
- enough fields for the formatting tool to produce a useful report without
  asking the LLM to invent facts;
- no real secrets, real emails, or sensitive personal data beyond obviously fake
  sample values.

The PostgreSQL tool should use parameterized SQL and return a normalized,
minimal, LLM-safe record. It should not dump entire raw rows or unnecessary PII
into the model context.

Redis should be configured through the docker-compose Redis service and accessed
from the Python cache tool using a local connection string. The cache key design
may be provided in config for this specified task. Cache values should be JSON
serialized and validated before reuse. Invalid JSON, schema mismatches, expired
records, or missing keys should be treated as cache misses that trigger
recomputation.

### Run.sh Instructions
Create run.sh as an executable Bash script.

run.sh MUST:
1. Start with #!/usr/bin/env bash and set -euo pipefail.
2. cd /root/task.
3. Install the task's Python dependencies as the first substantive step, for
   example pip install -q -r requirements.txt. The runtime may be pre-installed,
   but task dependencies such as redis, psycopg, pydantic, pytest, python-dotenv,
   litellm, openai, or anthropic are not pre-installed.
4. Start the datastores with docker compose up -d. Prefer docker compose up -d
   --wait when healthchecks are defined, but include explicit fallback polling if
   needed.
5. Wait until PostgreSQL is healthy using a pg_isready-based check with the same
   user and database configured in docker-compose.yml.
6. Wait until Redis is healthy using redis-cli ping or a Python redis client ping.
7. Verify PostgreSQL seed readiness with a simple read-only count or lookup from
   the customer table.
8. Verify Redis readiness with a write/read/delete round trip using a harmless
   readiness key.
9. Run a key-free agent selfcheck such as AGENT_TEST_MODE=1 python -m agent
   --selfcheck. The selfcheck may import modules, load tool definitions, validate
   fixtures, check config, compile simple schemas, and optionally skip a model
   ping when no provider key is present. It must not invoke candidate stubs, run
   the full agent loop, call a real model without a key, or run the candidate
   pytest suite.
10. Print a clear ready message and exit 0 when the scaffold is ready.

run.sh MUST NOT run the grader or candidate-facing tests as the deployability
gate. The candidate can run pytest separately after implementation. The fresh
starter may have tests that fail by design; that must not make run.sh fail.

## kill.sh file instructions
Create a kill.sh script that performs aggressive, idempotent cleanup for the
task. It must be safe to run multiple times and must print logs at every step.

The kill.sh script MUST follow this 9-step shape:
1. Start with #!/usr/bin/env bash and set -euo pipefail.
2. Print that cleanup is starting and cd to /root/task if it exists.
3. Stop docker-compose containers for this task using docker compose down
   --remove-orphans || true.
4. Remove docker volumes associated with this task, including PostgreSQL and Redis
   named volumes, using docker volume rm ... || true.
5. Remove docker networks associated with this task using docker network rm ...
   || true.
6. Force-remove any task-specific images if an app image was created, using
   docker rmi -f ... || true. If there is no app image, print that no app image
   removal is needed.
7. Run docker system prune -a --volumes -f || true.
8. Remove /root/task using rm -rf /root/task || true.
9. Print Cleanup completed successfully!

Every destructive command should include || true where appropriate so cleanup is
idempotent. The final line must clearly include the message:
Cleanup completed successfully!

The output should be a valid json schema:
- README.md: candidate-facing instructions using exactly the required four README
  sections.
- docker-compose.yml: Redis and PostgreSQL services with localhost-only port
  bindings, healthchecks, inline PostgreSQL initialization environment variables,
  and no version specification.
- init_database.sql: PostgreSQL schema and seed rows for the customer lookup
  tool.
- run.sh: readiness script that installs dependencies, starts datastores, checks
  health, performs datastore round trips, and runs a key-free selfcheck without
  running the candidate-facing test suite.
- kill.sh: idempotent cleanup script following the 9-step cleanup shape.
- requirements.txt or pyproject.toml: Python dependency manifest for all
  third-party libraries used by the scaffold.
- .env.example: provider key placeholders and local datastore URLs or settings.
- agent package files: complete scaffold plus candidate stubs for the tool-use
  behavior.
- tests or invariants files: candidate-facing tests that exercise the completed
  behavior but are not used by run.sh as the deployability gate.
- fixtures or traces: realistic request examples and expected observable
  behavior for the scenario.

## Code file requirements
The generated code_files object must contain complete file contents, not
summaries. Every file needed to run the task locally must be included.

Recommended lean repository shape:
- README.md
- requirements.txt
- .env.example
- docker-compose.yml
- init_database.sql
- run.sh
- kill.sh
- agent/__init__.py
- agent/__main__.py
- agent/config.py
- agent/llm_client.py
- agent/tools.py
- agent/orchestrator.py or agent/agent.py
- agent/schemas.py
- tests/test_tool_flow.py or invariants/test_tool_flow.py
- fixtures/report_requests.jsonl or fixtures/traces.jsonl

The exact names may vary, but keep the repository lean and coherent. Include
only files the candidate genuinely needs.

The code must:
- use structured tool result objects rather than raw strings for important tool
  boundaries;
- validate tool inputs before dispatch and return machine-readable structured
  errors for malformed calls;
- preserve a clear distinction between deterministic tools and LLM reasoning;
- prevent untrusted user text from directly becoming SQL, Redis keys, or tool
  parameters without validation and normalization;
- use parameterized SQL for PostgreSQL;
- serialize Redis cache values as JSON and validate them before reuse;
- include structured logs or trace records that make cache hit, cache miss,
  database lookup, formatting, and final response synthesis observable;
- ensure the agent calls a real model in normal operation through the provided
  LLM client wrapper.

The starter may include NotImplementedError stubs with explicit contracts because
open-endedness is set to false for this task. Good stub locations include
functions that decide whether a cached value is reusable, normalize a customer
record for the formatter, dispatch the next tool using the prior tool output, or
convert structured tool errors into safe agent-visible messages.

Do not include solved implementations in the candidate-facing files. Do not hide
the only acceptance contract in the evaluator answer; candidate-facing tests and
stub docstrings may make the expected behavior discoverable.

## .gitignore INSTRUCTIONS
Create a .gitignore that is appropriate for a Python project with local
datastores and environment files.

It should ignore:
- __pycache__/
- *.pyc
- .pytest_cache/
- .mypy_cache/
- .ruff_cache/
- .venv/
- venv/
- .env
- *.log
- local Redis or PostgreSQL dump files if any are generated
- coverage artifacts

Do not ignore source files, tests, fixtures, README.md, docker-compose.yml,
init_database.sql, run.sh, kill.sh, requirements.txt, or .env.example.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the
implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and
guidance to help them discover solutions.

The README.md generated inside code_files must contain EXACTLY these output
sections, in this order, and NO other markdown section headings:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario,
the current state, and why the problem matters. This section is NEVER empty. Do
not include bold time-budget callouts. Mention the observable symptom at a high
level, such as repeated reports recomputing unnecessarily, report output missing
data from the customer record, or tool failures not being handled cleanly. Do not
name the exact stub functions or explain the fix.

### Objectives
Write 4-6 bullets max. Frame objectives around outcomes rather than specific
technical implementations. Objectives describe the "what" and "why", never the
"how". Each bullet states an observable end-state, not a step or an API/library
to use.

Acceptable objective themes include:
- repeated requests reuse safe cached intermediate results;
- cache misses still complete through the normal customer lookup and formatting
  workflow;
- customer lookup data flows into report formatting without losing required
  fields;
- malformed tool arguments or missing customers produce structured, safe errors;
- the agent remains traceable and does not invent facts absent from tools.

Do not write objectives as step-by-step instructions such as "implement this
function" or "call this method."

### Helpful Tips
Write 4-5 bullets max. Provide practical guidance without revealing specific
implementations. Each bullet starts with an action word: "Consider", "Think
about", "Explore", "Review", or "Analyze". Tips guide discovery — they MUST NOT
name the specific API, library, function, pattern, data structure, or algorithm
that solves the task.

Helpful Tips may point candidates toward reading the tool traces, comparing cache
hit versus cache miss behavior, checking how data moves between tools, and
looking for places where structured errors become ambiguous.

### How to Verify
Write 4-6 bullets max. Frame verification in terms of observable outcomes.
Describe WHAT to verify and the expected behavior, not the specific
implementation to write. Each bullet is a check the candidate can run or observe:
test output, response shape, latency observation, log line, cache hit/miss trace,
or report content.

Because this task calls a real LLM when run end-to-end and ships a .env.example
declaring provider keys, How to Verify MUST open with a GitHub note admonition
embedded INSIDE the section as a blockquote, never as a new heading:
> [!NOTE]
> Copy `.env.example` to `.env` and set your provider key. The invariant tests
> run offline and need no key; only the end-to-end run does.

The README must not contain database connection details such as host, port,
username, password, or client-tool suggestions. It must not contain
<DROPLET_IP> placeholders.

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
Keep the following out of the README entirely:
- Setup commands such as npm install, pip install, docker compose up, mvn test,
  or similar commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create
  this class", or "use <specific API>".
- Any heading named "NOT TO INCLUDE", "Do not include", or similar.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these canonical top-level keys and
no others. Each value below describes what the downstream task generator must
fill in; do not emit placeholder arrays or placeholder dictionaries.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that is distinct from the display title and reflects the customer-report tool-use task.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, focused on fixing or completing the Redis/PostgreSQL tool-chaining agent.",
  "question": "The full candidate-facing work item written like a realistic teammate message that explains the observable production symptoms, states the high-level business outcome, tells the candidate to copy .env.example to .env for a provider key, and avoids revealing the implementation steps.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content with exactly Task Overview, Objectives, Helpful Tips, and How to Verify sections in that order and no solution-revealing setup commands.",
    "requirements.txt": "The complete Python dependency manifest containing every third-party package used by the scaffold, including the LLM client, Redis client, PostgreSQL client, dotenv/config helper, validation library, and pytest if tests are included.",
    ".env.example": "A complete environment example with provider key placeholders, AGENT_TEST_MODE, model name settings, and local datastore connection settings without real secrets.",
    "docker-compose.yml": "A complete docker-compose configuration for Redis and PostgreSQL with no version specification, localhost-only port bindings, healthchecks, inline PostgreSQL initialization environment values, and deterministic named volumes.",
    "init_database.sql": "A complete PostgreSQL initialization script that creates the customer records schema and inserts realistic seed rows for the lookup tool and error cases.",
    "run.sh": "An executable readiness script that installs dependencies, starts datastores, waits for health, performs PostgreSQL and Redis round trips, runs a key-free selfcheck, and does not run the candidate-facing test suite as the deployability gate.",
    "kill.sh": "An executable cleanup script following the required nine-step idempotent cleanup shape with docker compose down, volume/network/image cleanup, docker system prune, removal of /root/task, and a final success message.",
    ".gitignore": "A Python-appropriate gitignore that excludes caches, virtual environments, logs, local environment files, and generated artifacts while keeping all task source and fixture files tracked.",
    "agent/__init__.py": "The package initializer needed for clean imports in the readiness selfcheck.",
    "agent/config.py": "The complete configuration module that reads environment settings, model names, datastore URLs, AGENT_TEST_MODE, cache TTLs, and safe defaults used by the scaffold.",
    "agent/llm_client.py": "A complete real-model client wrapper using litellm, openai, or anthropic in normal operation while allowing key-free readiness checks without replacing the actual task's model call.",
    "agent/schemas.py": "Typed request, tool argument, tool result, cache payload, customer record, and report payload schemas used to enforce clear contracts at tool boundaries.",
    "agent/tools.py": "The tool catalogue and deterministic tool implementations or stubs for Redis cache access, PostgreSQL customer lookup, and report formatting, with candidate work isolated where appropriate.",
    "agent/orchestrator.py": "The incomplete agent orchestration module where the candidate completes cache handling, tool dispatch validation, lookup-to-format chaining, and structured fallback behavior.",
    "agent/__main__.py": "A CLI entry point that supports a key-free selfcheck and a normal end-to-end run without invoking candidate stubs during readiness.",
    "tests/test_tool_flow.py": "Candidate-facing pytest tests or invariants that exercise cache hits, cache misses, invalid cache fallback, customer lookup, formatting, structured errors, and tool chaining after the candidate solves the task.",
    "fixtures/report_requests.jsonl": "Realistic report-request fixtures or traces with customer IDs and observable outcomes that support the tests without containing a solved implementation."
  }},
  "answer": "Evaluator-facing high-level solution guidance summarizing the root causes, expected strong fix, important tradeoffs around validation, caching, latency, privacy, and traceability, and evidence reviewers should look for in the candidate's changes.",
  "definitions": "An object mapping concise task-specific terms such as tool schema, structured tool error, cache miss, cache hit, tool chaining, normalized customer record, and report payload to plain-English definitions.",
  "hints": "A single non-revealing line nudging candidates to inspect the trace of cache behavior and the handoff between customer lookup and report formatting without naming the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable cache reuse, correct cache-miss recomputation, reliable PostgreSQL-to-formatter chaining, structured error handling, and production-clean code with clear naming, logging, and maintainable structure.",
  "pre_requisites": "A bullet list of assumed prior knowledge stated as declarative capabilities only, such as Python 3.11 proficiency, comfort with docker-compose-backed Redis and PostgreSQL, familiarity with real LLM tool-calling agents, understanding of structured schemas and pytest, and a provider key via .env.",
  "short_overview": "A bullet list summarizing the business problem, the Redis and PostgreSQL tool-use focus, the expected agent behavior, and the observable outcome of a strong submission."
}}

Use these EXACT keys. Do NOT use synonyms: not task_title for title, not files for
code_files, not context for question, and not solution for answer. Do NOT emit
criterias because the pipeline injects it. Output raw JSON only with no markdown
fences or explanatory prose around the JSON object.

## CRITICAL REMINDERS
- Output raw JSON only — exactly the keys: name, title, question, code_files,
  answer, definitions, hints, outcomes, pre_requisites, short_overview.
- The generated task MUST include Redis and PostgreSQL via docker-compose and
  MUST include docker-compose.yml, init_database.sql, run.sh, and kill.sh.
- docker-compose.yml MUST NOT include any version specification.
- PostgreSQL MUST set POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB inline in
  the service environment, and the init SQL, healthcheck, and connection string
  must use the same user and database.
- **SECURITY-CRITICAL**: every datastore port exposed to the host MUST be bound
  to localhost only using 127.0.0.1:<port>:<port>.
- run.sh must install Python dependencies first, start the datastores, wait for
  health, perform datastore round trips, and run a key-free selfcheck without
  calling candidate stubs, requiring a model key, running the full agent loop, or
  running the candidate-facing test suite.
- The task must use a REAL LLM/agent loop in normal operation. Never use FakeLLM,
  StubLLM, regex intent parsing, keyword-only routing, or sleep calls to simulate
  agent thinking.
- The core competency signal is Tool Use for Agents: tool schemas, validation,
  tool selection/dispatch, Redis-backed caching, PostgreSQL lookup, formatting
  tool chaining, structured errors, and fallback behavior.
- Keep it INTERMEDIATE and solvable within {minutes_range}. Do not expand into a
  multi-agent platform, fine-tuning project, frontend task, or broad system
  design essay.
- README.md must use exactly the four required sections in order: Task Overview,
  Objectives, Helpful Tips, How to Verify. Do not add any other README headings.
- Do not leak the reference answer into code_files, README.md, comments, hints,
  or tests. The complete solution guidance belongs only in answer.
"""

PROMPT_REGISTRY = {
    "Tool Use for Agents (INTERMEDIATE)": [
        PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_CONTEXT,
        PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_TOOL_USE_AGENTS_INTERMEDIATE_INSTRUCTIONS,
    ]
}