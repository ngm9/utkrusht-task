# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role.

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competencies:
{competencies}

Use this context ONLY to understand who is hiring, the expected engineering maturity, and the kind of production environment the candidate may work in. The employer's industry is NOT necessarily the task domain. The business domain for the assessment task must come from the real-world scenarios provided later unless no concrete scenario is available.
"""

PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Tool Use for Agents assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task. Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level. The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.

The task must be a realistic build-it repository for a tool-using LLM agent. It should center on a production failure at the tool boundary: wrong tool choice, unsafe side-effecting tool invocation, malformed tool arguments, missing validation, brittle retry behavior, poor structured tool errors, missing traceability, or weak handoff from tool output back to the LLM. The candidate should implement a focused fix in code, not write an essay.

This is an INTERMEDIATE task. The candidate has a few years of experience building or maintaining production-facing agents, but is not expected to design an entire agent platform. Keep the work scoped to ONE clear tool-use decision, or at most two tightly related decisions, and make it completable within the time budget.

The generated repository must include a REAL LLM/agent loop. The LLM must be the planner/router/reasoning component that selects or repairs tool calls. Tools must provide deterministic business actions, data retrieval, validation, or side effects. Do NOT create a FakeLLM, deterministic stand-in, regex intent parser, keyword router, or simulated model. The candidate-filled stubs are the agent logic around real tool use, not a replacement for the model.

Before proceeding to the detailed task generation instructions, briefly confirm your understanding by summarizing:
1. Which scenario you selected and what production tool-use failure the task will model.
2. Which tool-use capability the candidate must improve: schema, validation, dispatch, retry, structured error handling, side-effect gating, audit logging, or tool-result post-processing.
3. Which files the candidate will inspect and which focused stubs they will complete.
"""

PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in LLM-driven agents, tool-calling systems, Python, PostgreSQL-backed state, and production integration design, you are given a list of real world scenarios and proficiency levels for Tool Use for Agents. Generate ONE INTERMEDIATE build-it assessment task that evaluates whether a candidate can make a tool-using agent safer, more reliable, and more traceable at the boundary between the LLM and business tools.

The output must be a FULLY FUNCTIONAL repository scaffold. It must be deliberately incomplete in a small number of candidate-facing stubs, but the starting environment must be FULLY POPULATED with realistic code, fixtures, database initialization, run scripts, and candidate-facing checks. The candidate should be able to clone the task, provide their own model provider key in `.env`, start the PostgreSQL-backed environment with `./run.sh`, inspect the code and traces, then implement the missing tool-use logic.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an INTERMEDIATE AI Agent Engineer working on a production-facing agent that uses tools to retrieve data, perform business actions, and coordinate multi-step workflows. The task should test applied judgment around tool definitions, structured arguments, validation, retries, idempotency, side-effect gating, audit logging, post-processing, and safe recovery after tool failures.

The task is not a trivia question, framework syntax drill, system-design essay, or prompt-only review. It is a realistic coding work item where the candidate improves a small tool-use path in a runnable agent repository.

**CRITICAL**: The candidate must interact with a real agent loop. The repository must call a REAL model through a runtime SDK or router such as LiteLLM, OpenAI SDK, Anthropic SDK, LangChain, or LangGraph. The candidate provides their own provider key at runtime via `.env`.

**CRITICAL**: Do NOT create a FakeLLM, StubLLM, deterministic stand-in for the model, regex intent parser, keyword router, or any placeholder that pretends to be the LLM. Do NOT use `time.sleep()` or `asyncio.sleep()` to simulate agent or tool thinking. Determinism for grading is not required; production grades the candidate's diff with an LLM judge. Fixtures may make tool inputs and database state deterministic, but they must never replace the model's tool-selection or repair behavior.

## INSTRUCTIONS

### Nature of the Task
- Generate ONE realistic INTERMEDIATE build-it task centered on Tool Use for Agents.
- The task must be grounded in ONE selected real-world scenario from `{real_world_task_scenarios}`. If several scenarios are present, choose the one whose technical surface area best fits an intermediate tool-use task. Do not drift into the employer's industry unless the selected scenario itself uses that domain.
- **CRITICAL**: Keep the task focused on tool boundaries: clear tool contracts, JSON schemas, argument validation, safe dispatch, structured tool errors, retry/fallback behavior, side-effect gating, idempotency, state handoff, audit logging, and post-processing of tool outputs.
- **CRITICAL**: The agent must include a real LLM-driven planning or tool-selection step. The candidate may implement validation, dispatch, retry, repair-loop, state, or policy code, but the model must still be the component that reasons about which tool call to attempt or how to respond after a structured tool error.
- **CRITICAL**: Scope the implementation to approximately 60-140 candidate-written lines across 1-2 files. The task should fit in {minutes_range}; do not require building a full platform, multi-agent supervisor, vector search layer, large authentication system, or complex frontend.
- Acceptable task archetypes include:
  - Preventing unsafe side-effecting tool calls until required confirmation or state is present.
  - Validating and normalizing model-produced tool arguments before dispatch.
  - Returning structured tool errors such as `{{"code": "VALIDATION_ERROR", "message": "...", "retryable": false, "attempts": 1}}` so the LLM can recover safely.
  - Retrying only safe, idempotent tool calls for transient errors with bounded attempts.
  - Recording traceable audit rows for every tool invocation with `trace_id`, `tool_name`, arguments summary, status, latency, and error code.
  - Repairing malformed tool calls by feeding structured validation errors back to the model with bounded retries.
  - Handling pagination or result limits before passing tool output back to the LLM.
- Do NOT require advanced concepts outside the stated scope, such as fine-tuning models, building a distributed workflow engine, implementing a full auth provider, creating a vector database retrieval platform, complex multi-agent orchestration, or writing a long design document.
- The starting repository must contain realistic traces, fixtures, prompts, and database state that expose the issue indirectly. Do NOT label files as flawed or explain the fix in comments.
- The candidate-facing `question` and `README.md` must describe symptoms and desired outcomes, not implementation steps or exact function names.
- The evaluator-facing `answer` may describe the expected fix, root cause, and tradeoffs, but code_files and README.md must not reveal the solution.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, PostgreSQL documentation, agent framework documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The use of AI tools is allowed as part of the assessment workflow.
- The task should evaluate the candidate's ability to understand, modify, and validate a realistic codebase rather than memorizing APIs.
- The submitted work must still satisfy the behavior expected by the repository and must preserve safety, correctness, and maintainability.
- Do not include restrictions in the generated task that prohibit candidates from using LLMs, documentation, or other external resources.

## Code Generation Instructions
Generate a Python-based agent repository with a real LLM client and a PostgreSQL-backed state or audit store. The repository must include a small service or CLI entry point, realistic tools, prompts, tool schemas, database access helpers, fixtures, candidate-facing invariant tests, and scripts.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

The generated repository should generally include:
- `agent/__init__.py` as a minimal package marker.
- `agent/config.py` to load `.env` values and model configuration.
- `agent/llm_client.py` as a complete real-model wrapper using LiteLLM, OpenAI SDK, Anthropic SDK, or a comparable real provider SDK. This file is provided complete and is not the candidate's main work.
- `agent/prompts.py` with system and developer prompts that guide tool use, distinguish system policy from user instructions, and describe when to call tools, ask clarifying questions, decline unsafe requests, or recover from structured tool errors.
- `agent/tool_schemas.py` or `agent/tools.py` with realistic tool definitions and JSON-style argument contracts.
- `agent/orchestrator.py`, `agent/tool_dispatch.py`, `agent/policy.py`, or similar candidate-focused files containing small stubs with `raise NotImplementedError`.
- `agent/db.py` for PostgreSQL connection helpers and state/audit persistence.
- `agent/__main__.py` or `app.py` for a CLI or minimal service entry point and `--selfcheck`.
- `fixtures/` with realistic scenario inputs, trace examples, or tool-call cases.
- `invariants/test_*.py` with candidate-facing pytest tests that verify behavior after the candidate finishes. These tests must NOT be run by `run.sh`.
- `requirements.txt` listing the Python dependencies used by the repository.
- `.env.example` showing provider key variables and the local PostgreSQL connection string.
- `docker-compose.yml`, `init_database.sql`, `run.sh`, `kill.sh`, `.gitignore`, and `README.md`.

The LLM client must call a real model by default when a provider key is present. The readiness path may skip the model ping when no key is present, but this must not become an LLM-free task. A good pattern is:
- `AGENT_TEST_MODE` may be used only for offline fixture or invariant paths that validate tool inputs and schemas without a provider key.
- `AGENT_TEST_MODE` must never be described as the real agent behavior.
- The normal candidate path must call a real provider using the candidate's key.
- A key-gated `_ping_model()` may run only when a provider key exists and must call the model directly without executing candidate stubs or unsafe tools.

Do not instruct the downstream task to run `pip install`, `apt-get install`, or other installation commands inside `run.sh` for the runtime or common libraries. The E2B template provides the runtime and common libraries. The repository may still include `requirements.txt` so candidates know what the project uses.

## Infrastructure Requirements
This is an infra-shaped task. The generated task MUST include PostgreSQL as the external datastore because tool-using agents in these scenarios need durable business state, conversation/task state, tool invocation audit rows, or traceable side-effect records.

The generated task MUST include:
- `docker-compose.yml` defining a PostgreSQL service.
- `init_database.sql` creating the tables and seed data needed by the chosen scenario.
- `run.sh` that starts PostgreSQL with Docker Compose, waits for readiness, performs a simple database smoke check, verifies the Python scaffold imports or self-checks, and exits 0 on the UNSOLVED starter repository.
- `kill.sh` that tears down containers, volumes, networks, images, and `/root/task` idempotently.

`run.sh` is a readiness/self-check script, not the grader. It must NOT run the candidate-facing invariant tests because those are expected to fail until the candidate completes the task.

### Docker-compose Instructions
Create a `docker-compose.yml` file for PostgreSQL.

**MUST NOT include any version specification** in `docker-compose.yml`.

The PostgreSQL service must:
- Use a standard PostgreSQL image such as `postgres:16`.
- Set standard initialization environment variables inline under the service: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Use the same user, password, and database name in `init_database.sql`, the healthcheck, and the application connection string.
- Mount `./init_database.sql` into `/docker-entrypoint-initdb.d/init_database.sql:ro`.
- Define a persistent named volume for PostgreSQL data.
- Include a healthcheck using `pg_isready` with the same database user and database.
- Use `restart: unless-stopped`.

**SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`. Do not expose PostgreSQL on `0.0.0.0`, and do not use an unqualified `5432:5432` mapping.

Do not use `.env` files or `${{VAR}}` host indirection for database initialization values in `docker-compose.yml`. Inline service environment values are required because the image will not initialize without them.

### init_database.sql Instructions
Create an `init_database.sql` file that fully initializes the scenario's PostgreSQL state. It should be realistic but small enough for a candidate to understand quickly.

The SQL should:
- Create all tables required by the chosen scenario, such as conversation state, tool invocation audit rows, business entities, bookings, orders, accounts, or requests.
- Insert realistic seed rows that match the scenario and fixtures.
- Include enough data to exercise success, validation failure, retryable failure, unsafe side-effect prevention, and traceability paths where relevant.
- Use primary keys, foreign keys, timestamps, status fields, and simple constraints where helpful.
- Avoid complex stored procedures, triggers, or advanced DBA topics that would distract from Tool Use for Agents.
- Use the same database name and user assumed by `docker-compose.yml` and application configuration.

### Run.sh Instructions
Create a `run.sh` file at the repository root.

The script must:
- Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
- `cd /root/task`.
- Start PostgreSQL using `docker compose up -d`.
- Wait until PostgreSQL is healthy using `docker compose ps`, `pg_isready`, or a small Python database connection loop.
- Perform a small read/write/delete or select smoke check against PostgreSQL to confirm the initialized schema is usable.
- Run an import or self-check command such as `python -m agent --selfcheck` that verifies the scaffold, fixtures, tool definitions, prompts, and database connection load.
- Exit 0 on the unsolved starter repository.
- Print clear logs for each readiness step.
- End with a clear success message such as `Ready: PostgreSQL is healthy and the agent scaffold loads.`

The script must NOT:
- Run `pytest`, `invariants/`, or any grader-like test suite.
- Invoke candidate stubs that raise `NotImplementedError`.
- Run the live agent loop.
- Require an API key at readiness time.
- Call unsafe write tools as part of readiness.
- Use `pip install`, `apt-get install`, `npm install`, or similar dependency installation commands for the runtime or common libraries.

If the self-check includes a model ping, it must be key-gated: when no provider key is present, print a note and skip the ping; when a provider key is present, ping the model directly without executing candidate stubs or tool side effects.

## kill.sh file instructions
Create a `kill.sh` file at the repository root that is safe and idempotent. It must:

1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print a clear message before each cleanup phase.
3. Change to `/root/task` if the directory exists, but continue safely if it does not.
4. Stop running Docker Compose services with `docker compose down --remove-orphans || true`.
5. Remove Docker volumes created by the task with `docker compose down -v --remove-orphans || true` or explicit `docker volume rm ... || true`.
6. Remove Docker networks created by the task with `docker network rm ... || true`.
7. Force-remove task-related Docker images if any were created, using `docker rmi -f ... || true`.
8. Run `docker system prune -a --volumes -f || true`.
9. Remove `/root/task` with `rm -rf /root/task || true`.

Every destructive command must use `|| true` where needed so repeated cleanup attempts do not fail. The script must print logs at every step and finish with the exact final message:
`Cleanup completed successfully!`

The output should be a valid json schema:
- `README.md`: Candidate-facing overview using exactly the required README sections.
- `.gitignore`: Local Python, environment, cache, and database artifacts to ignore.
- `.env.example`: Provider key placeholders and local database connection string.
- `requirements.txt`: Python package names needed by the generated repository.
- `docker-compose.yml`: PostgreSQL service with localhost-only port binding and no version field.
- `init_database.sql`: Full database initialization and seed data for the selected scenario.
- `run.sh`: Readiness script that starts PostgreSQL and validates the scaffold without running grader tests.
- `kill.sh`: Idempotent teardown script following the required nine-step cleanup shape.
- `agent/`: Python package containing the real LLM client, prompts, tools, tool schemas, database helpers, orchestration, and candidate stubs.
- `fixtures/`: Small realistic fixture files that drive the scenario.
- `invariants/`: Candidate-facing tests that validate completed behavior but are not executed by `run.sh`.

## Code file requirements
All generated code must be realistic, internally consistent, and runnable as a starter scaffold.

The code must:
- Use Python for the agent implementation.
- Use PostgreSQL for the scenario's durable state, tool audit trail, or business records.
- Include a real LLM client wrapper built on a real provider SDK or router.
- Keep candidate work focused in 1-2 files with clearly named functions that raise `NotImplementedError` and include neutral contract descriptions only.
- Include structured logging or audit persistence for tool calls where relevant.
- Use structured tool inputs and outputs. Tool errors should be machine-readable, with fields such as code, message, retryable, attempts, and trace_id when applicable.
- Separate business tools from the LLM orchestration layer. Strict validation, authorization-like checks, idempotency checks, and side-effect gating should live in code or tools, not purely in model instructions.
- Avoid leaking the solution in comments, docstrings, README text, variable names, or tests.
- Include candidate-facing invariant tests that are clear enough to run after implementation but do not become step-by-step solution instructions.
- Keep fixtures small, realistic, and aligned with database seed data.

Do NOT:
- Include a fake model or deterministic model stand-in.
- Use regex or keyword matching as the agent's tool-selection brain.
- Simulate work or latency with sleeps.
- Ask candidates to implement authentication providers, billing platforms, full observability stacks, or advanced distributed systems.
- Hide the entire task in a single monolithic file.
- Include external secrets or real credentials.
- Include database host, port, username, password, or client-tool suggestions in the README.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` suitable for a Python agent repository with Docker-backed PostgreSQL. It should include:
- Python caches and build artifacts such as `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `dist/`, and `build/`.
- Virtual environments such as `.venv/`, `venv/`, and `env/`.
- Environment and secret files such as `.env`, `.env.*`, while allowing `.env.example` to be committed.
- Local logs, coverage files, and temporary artifacts.
- OS/editor files such as `.DS_Store` and `.vscode/`.
- Local database dumps or generated runtime data if the repository creates them.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md file must contain EXACTLY these sections in this order and no other markdown section headings:

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. This section is NEVER empty. Do not include bold time-budget callouts. Describe observable symptoms and business impact, not the implementation approach. Do not name specific stub files or functions.

### Helpful Tips
Write 4-5 bullets max. Provide practical guidance without revealing specific implementations. Each bullet must start with an action word: `Consider`, `Think about`, `Explore`, `Review`, or `Analyze`. Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

### Objectives
Write 4-6 bullets max. Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how". Each bullet must state an observable end-state, not a step or an API/library to use.

### How to Verify
Write 4-6 bullets max. Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write. Each bullet should be a check the candidate can run, such as readiness output, invariant test output, response shape, latency observation, log row, audit record, or database state.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of README.md:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, or `./run.sh` command recipes beyond high-level verification phrasing.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use this specific API".
- Database connection details, including host, port, username, password, database name, or client-tool suggestions.
- `<DROPLET_IP>` placeholders.
- Separate sections such as Database Schema Overview, Database Access, Performance Issues, Deliverables, or Not To Include.

## REQUIRED OUTPUT JSON STRUCTURE
Output a single raw JSON object with EXACTLY these keys and no others. Each value must be fully populated for the generated task.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that starts with an action verb and summarizes the tool-use agent task.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, different from the repository name.",
  "question": "The full candidate-facing task description written as a realistic work-item message that states the production symptoms, high-level business goal, safety constraints, use of their own model provider key, and where to begin without revealing the implementation details.",
  "code_files": "An object mapping every required filepath to its complete file contents, including README.md, .gitignore, .env.example, requirements.txt, docker-compose.yml, init_database.sql, run.sh, kill.sh, Python agent package files, fixtures, and candidate-facing invariant tests.",
  "answer": "Evaluator-facing high-level solution guidance describing root causes, expected fix shape, key tradeoffs, and evidence in the starter repository without providing chain-of-thought or duplicating full solution files.",
  "definitions": "An object of concise term-to-definition pairs for domain terms and agent/tool-use concepts that appear in the task, such as tool schema, structured tool error, idempotency, side-effecting tool, trace_id, confirmation gate, or retryable error.",
  "hints": "A single-line non-revealing hint that nudges the candidate toward inspecting the agent trace, tool contract, validation boundary, or audit records without naming the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on safe tool use, correct business behavior, structured recovery, traceability, and production-clean code with clear naming, error handling, logging, and maintainable structure. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Python, basic PostgreSQL-backed local development, real LLM provider keys, tool-calling agents, JSON-style schemas, structured errors, and running candidate-facing tests.",
  "short_overview": "A bullet list summarising the business problem, the tool-use failure under investigation, the technical focus, and the expected safe production outcome."
}}

Use these EXACT keys. Do NOT use synonyms such as `task_title`, `files`, `repo`, `context`, `prompt`, or `solution`. Do NOT emit `criterias`; the pipeline injects it. Output raw JSON only with no markdown fences and no commentary outside the JSON object.

## CRITICAL REMINDERS
- Output must be valid JSON only — no markdown fences and no explanatory prose around the object.
- The task must be infra-shaped and MUST include `docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`.
- `docker-compose.yml` MUST NOT include any version specification.
- PostgreSQL environment variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` must be inline in the service definition; do not use `.env` or `${{VAR}}` host indirection for initialization values.
- **SECURITY-CRITICAL**: PostgreSQL ports MUST be bound to localhost only using `127.0.0.1:5432:5432`.
- `run.sh` must start PostgreSQL, wait for readiness, perform a database smoke check, and validate the scaffold without running invariant tests or invoking candidate stubs.
- `kill.sh` must follow the nine-step cleanup shape, use idempotent `|| true` cleanup commands, remove `/root/task`, and end with `Cleanup completed successfully!`.
- The repository MUST include a REAL LLM/agent loop using a provider SDK, router, or agent framework. The candidate supplies their own provider key at runtime.
- NEVER include a FakeLLM, StubLLM, deterministic stand-in for the model, regex intent parser, keyword router, or sleep-based simulation.
- Candidate stubs are the tool-use logic: validation, dispatch, repair, retry, side-effect gating, state handling, post-processing, or audit logging.
- Keep the task focused on Tool Use for Agents, not generic model fallback, pure prompt writing, fine-tuning, frontend work, or a database-only exercise.
- README.md must contain exactly the four required sections in the required order: Task Overview, Helpful Tips, Objectives, How to Verify.
- README.md must not include setup commands, database connection details, direct solutions, step-by-step implementation guidance, or headings outside the required four.
- The `answer` field is evaluator-facing; never leak the reference fix into `code_files`, comments, README.md, or hints.
- Keep the implementation intermediate-level and solvable within {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Tool Use for Agents (INTERMEDIATE)": [
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_CONTEXT,
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INSTRUCTIONS,
    ]
}