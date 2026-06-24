# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role.

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competencies:
{competencies}

As a technical architect super experienced in production LLM agents and tool-using agent systems, you are given a list of real world scenarios and proficiency levels for production agent engineering and tool use for agents.

Use this context ONLY to understand who is hiring, the expected engineering maturity, and the seniority calibration. The employer's industry is NOT automatically the business domain of the assessment task unless the selected real-world scenario explicitly matches it. Generate a practical assessment for an INTERMEDIATE engineer who can build and harden production-grade LLM agents with tools, state, validation, observability, and bounded autonomy.
"""

PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Production Agent Engineering and Tool Use for Agents assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION CALIBRATION SIGNAL:
{question_prompt}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Scope it as a focused production fix: about 5-10 minutes to read and run the scaffold, 5-10 minutes to inspect traces/tests/schema expectations, and 20-30 minutes to implement or repair one coherent agent/tool boundary decision.

SCENARIO FOCUS:
The candidate is an intermediate Production Agent Engineering and Tool Use for Agents practitioner working on a real agent repository. The scenario should involve an LLM-driven agent that calls one or more real business tools backed by a PostgreSQL datastore. The repository is FULLY FUNCTIONAL as a starting environment, but deliberately incomplete or unsafe at the tool boundary: for example, invalid structured outputs being persisted, malformed tool calls being passed through, duplicate side-effecting tool execution, missing idempotency, unsafe retries, or insufficient validation before writing to the database.

You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task. Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level. The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.

Good scenario shapes for this combined competency include:
- A healthcare benefits coverage agent that calls a policy-search tool, asks a real LLM for a typed coverage decision, validates fields such as covered, preauthorization requirement, and evidence document identity, and prevents unsupported decisions from being persisted.
- A logistics delivery-change agent that lets an LLM call a side-effecting reschedule tool, but must enforce idempotency so repeated client retries do not create duplicate business events.
- A support or operations agent that repairs malformed tool arguments through a bounded LLM/tool loop, normalizes structured tool results, and escalates safely when the result cannot be validated.

The task MUST be a build-it coding task, not an essay, quiz, architecture memo, or pure prompt-writing exercise. The candidate should work in a Python project with a real LLM SDK or router, real tool definitions, a PostgreSQL-backed business table, and candidate-facing tests or replay scripts. The candidate supplies their own provider key in `.env` at runtime. The generation-time readiness check must not require a key.

Before generating the final task, briefly internalize:
1. Which real-world scenario you are using and why it fits both Production Agent Engineering and Tool Use for Agents at INTERMEDIATE level.
2. Which single production decision is being tested: typed structured output validation, safe tool dispatch, idempotent side effects, bounded repair/retry, fallback/escalation, or traceable persistence.
3. Which PostgreSQL tables and seed records are required to make the task realistic and self-contained.
4. Which 1-2 files the candidate edits, and which provided tests/replay fixtures expose the expected behavior without giving away the solution.
5. How the repository can call a real model after the candidate adds a key, while `./run.sh` remains key-free and only proves the scaffold, database, schemas, and fixtures are ready.
"""

PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in production LLM agents, tool-calling workflows, PostgreSQL-backed business systems, and production reliability, generate ONE realistic INTERMEDIATE build-it assessment task for Production Agent Engineering and Tool Use for Agents.

The candidate receives a FULLY FUNCTIONAL, FULLY POPULATED local repository under `/root/task` with a real agent scaffold, a PostgreSQL datastore, realistic fixtures, and candidate-facing tests or replay checks. The repository is deliberately incomplete at one production-critical tool-use boundary. The candidate must make the agent safe enough for production by implementing the missing logic and repairing the planted flaw.

The generated task MUST exercise a REAL LLM/agent loop. The candidate's code must call a real model through a runtime SDK or router such as LiteLLM, OpenAI SDK, or Anthropic SDK. The candidate supplies their own provider key at runtime via `.env`. The candidate-filled stubs ARE the agent logic: structured output validation, tool selection/dispatch, retry/repair control, idempotency, state handling, database persistence, error handling, and observability. They are NOT a fake model.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is at INTERMEDIATE proficiency. They should be able to work independently on a single production agent workflow that uses tools and a backing store, but should not be asked to build a broad agent platform or solve an advanced multi-agent architecture problem.

The task should probe practical judgment:
- Distinguishing a production agent from a prototype chatbot by requiring clear tool contracts, bounded autonomy, validation, persistence safety, observability, and failure handling.
- Designing safe, reusable tool boundaries with explicit input/output contracts, strong typing, structured errors, and side-effect controls.
- Handling structured LLM outputs with validation before persistence.
- Managing retries, idempotency, fallback, escalation, or repair loops without infinite loops or duplicate side effects.
- Keeping model calls, tool calls, database writes, and logs traceable enough for debugging.
- Applying security and privacy basics such as least privilege, no secrets in model-visible context, no PII leakage in logs, and prompt-injection-aware tool dispatch.

**CRITICAL**: Keep the scope to ONE senior production decision, at most two tightly related ones. Examples: typed JSON validation plus safe persistence; idempotency plus structured tool result reuse; bounded tool-call repair plus structured escalation. Do NOT combine schema validation, RAG, multi-agent routing, cost optimization, human approval, vector search, and deployment all in one task.

**CRITICAL**: The task must be completable within {minutes_range}. Candidate-written code should usually be 60-150 lines across 1-2 files.

**CRITICAL**: The employer context is only hiring context. The business domain must come from the selected real-world scenario, not from the employer's background unless they happen to match.

## INSTRUCTIONS

### Nature of the Task
- Generate a build-it coding task in a Python repository for an INTERMEDIATE Production Agent Engineering and Tool Use for Agents candidate.
- The repository must contain a real LLM-driven agent loop that uses one or more real business tools. The agent may use LiteLLM, OpenAI SDK, Anthropic SDK, LangGraph, or a lightweight custom orchestrator, but it must not use a fake model.
- The task must be infra-shaped: include PostgreSQL via docker-compose, an `init_database.sql` seed file, `run.sh`, and `kill.sh`.
- The generated project must include a runtime-native manifest such as `pyproject.toml`, plus source files, fixtures, and tests or replay scripts.
- The candidate should discover the missing logic by reading the code and running the provided checks. The `question` and README should describe the symptoms and outcomes, not the implementation steps.
- **CRITICAL**: Do NOT create a pure design-review task. The candidate must edit code.
- **CRITICAL**: Do NOT create a fake deterministic agent. The model call must be real once the candidate provides a key.
- **CRITICAL**: Do NOT create a regex or keyword intent parser standing in for the model.
- **CRITICAL**: Do NOT use `time.sleep()` or `asyncio.sleep()` to simulate agent or tool thinking.
- **CRITICAL**: Do NOT require a model key during generation-time readiness. `./run.sh` must prove the scaffold, database, schemas, and fixtures are ready without calling the model. If a provider key is present, an optional direct one-token model ping may run, but it must not execute the candidate's unfinished agent loop.
- The production flaw must naturally derive from the competency scopes: invalid structured output, malformed tool arguments, unsafe tool dispatch, duplicate side effects, missing idempotency, bounded retry/repair, safe fallback, state consistency, validation before persistence, or traceable logging.
- The task should not require advanced concepts outside the scope such as full multi-agent platform design, fine-tuning, complex distributed systems, statistical eval design, or frontend work.
- Include realistic traces, replay fixtures, or pytest tests that make the expected behavior observable. These checks are candidate-facing; they are not a substitute for the real agent loop.
- The candidate-facing materials must not leak the reference implementation.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, PostgreSQL documentation, LiteLLM/OpenAI/Anthropic/LangGraph documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The use of external resources is not considered cheating. The assessment is designed to evaluate the candidate's ability to understand a realistic production issue, navigate an existing codebase, make sound implementation decisions, and deliver a working improvement.

Candidates should still be able to explain and justify the changes they make. A strong submission demonstrates applied judgment, not copy-pasted framework trivia.

The generated task should be specific enough that generic AI output is insufficient without reading the repository, fixtures, database schema, and failure symptoms.

## Code Generation Instructions
Generate a complete repository under `/root/task`.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

Use Python as the implementation runtime unless the selected scenario explicitly states a different runtime. Include `pyproject.toml` as the native manifest. Do NOT include `apt-get install`, `pip install`, or `npm install` commands in `run.sh` for the primary runtime or common libraries; the environment template provides the runtime and common libraries. The manifest should still declare the libraries used by the project.

The project should typically include:
- `README.md` with the exact four candidate-facing sections specified below.
- `pyproject.toml` declaring the package, test command dependencies, and libraries such as psycopg, pydantic, python-dotenv, litellm or openai/anthropic, pytest, and any lightweight agent orchestration library actually used.
- `agent/__init__.py`.
- `agent/__main__.py` with a key-free selfcheck path and an optional key-gated direct model ping.
- Agent orchestration modules such as `agent/orchestrator.py`, `agent/prompts.py`, `agent/models.py`, or `agent/state.py`.
- Tool boundary modules such as `agent/tools.py`, `agent/tool_contracts.py`, `agent/validation.py`, or `agent/idempotency.py`.
- Candidate-stub files with `NotImplementedError` in the functions the candidate must complete.
- PostgreSQL access code that uses the local datastore configured by docker-compose. Keep connection details local and simple; do not expose database credentials in README.
- `fixtures/` containing realistic replay traces, tool results, or saved requests from the selected scenario.
- `tests/` or `invariants/` containing candidate-facing tests that validate observable outcomes.
- `docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`.

The repository must be solution-free:
- Candidate stubs may contain neutral docstrings describing WHAT the function is responsible for, never HOW to implement it.
- Do not include commented-out solution code.
- Do not include TODO comments that reveal the approach.
- Do not name helper functions in a way that gives away the exact answer beyond normal domain clarity.
- Put root causes and expected fixes only in the evaluator-facing `answer` field.

The real LLM loop must be reachable after the candidate provides a key. For example, a CLI command can replay one request through the agent, call a real model to produce a structured tool decision, validate or repair it, invoke the tool, and persist the result. The selfcheck path must not call the unfinished loop.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## Infrastructure Requirements
This task is infra-shaped. The generated repository MUST include PostgreSQL as an external datastore using docker-compose. The datastore should support the selected scenario's business tables, for example `coverage_decisions`, `policy_documents`, `agent_tool_requests`, `delivery_events`, `tool_audit_log`, or similarly domain-appropriate tables.

The datastore is part of the assessment because the competencies include production integration with databases, business systems, state, idempotency, validation before persistence, and auditability. Do not replace it with SQLite or in-memory dictionaries.

### Docker-compose Instructions
Create `docker-compose.yml` for the datastore required by the scenario.

Docker-compose rules:
- **MUST NOT include any version specification**. Do not include a top-level `version:` key.
- **MUST NOT include environment variables or .env file references** in docker-compose.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Use a deterministic project/service name that matches the task.
- Mount `init_database.sql` into the database initialization path or otherwise ensure it is applied automatically.
- Include a healthcheck so `run.sh` can wait for the datastore before running selfcheck.
- Do not add extra datastores that the selected scenario does not exercise.
- Do not include an app container unless the scenario explicitly requires a service container. A local Python process talking to containerized PostgreSQL is preferred for this assessment.

Because docker-compose must not include environment variables, configure PostgreSQL without `.env` references. If using the official PostgreSQL image, use an entrypoint/command approach or another safe local-only configuration that allows a local development database without embedding secrets. Bind it only to localhost and keep it suitable for assessment use.

### init_database.sql Instructions
Create `init_database.sql` with a FULLY POPULATED schema and seed data for the selected scenario.

The SQL file must:
- Create all required tables, indexes, constraints, and seed records.
- Include realistic domain data that the agent tools can query or modify.
- Include tables needed for traceability, such as a tool audit log or agent execution log, when relevant.
- Include constraints that reinforce the production behavior being tested, such as uniqueness for idempotency keys, foreign keys for evidence document IDs, or check constraints for status fields.
- Avoid putting secrets, provider keys, or environment-specific values in the database.
- Be idempotent enough for repeated local setup when combined with `kill.sh`.
- Keep the dataset small but realistic: enough rows to support the fixtures and tests without overwhelming a {minutes_range} task.

### Run.sh Instructions
Create `run.sh` that starts the datastore and runs a key-free readiness probe.

`run.sh` must:
- Start with `#!/usr/bin/env bash`.
- Use `set -euo pipefail`.
- `cd /root/task`.
- Run `docker compose up -d` for PostgreSQL and wait for health/readiness.
- Perform a simple database round-trip that does not depend on candidate-completed code.
- Run the application's selfcheck command, such as `python -m agent --selfcheck`.
- Print useful progress logs.
- End by printing `ready`.
- Exit non-zero if the datastore, schema, imports, fixtures, or selfcheck are broken.
- Never call candidate stub functions.
- Never run the unfinished agent loop.
- Never require an LLM provider key.
- If a provider key is present, only an optional direct model ping may run, and it must not dispatch tools, write business rows, or execute candidate stubs.
- Not install the runtime or common libraries with `apt-get`, `pip install`, or `npm install`.

The selfcheck should validate:
- Python package imports.
- Required files exist.
- Tool schemas or contract modules load.
- Fixtures parse.
- PostgreSQL is reachable.
- Seed tables contain expected rows.
- The optional model ping is skipped when no key is present.

## kill.sh file instructions
Create a `kill.sh` script that completely cleans the local task environment. It must follow this 9-step shape:

1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print a clear log line before every cleanup step.
3. Stop all docker-compose services for the task using `docker compose down --remove-orphans || true`.
4. Remove named volumes used by the task using `docker volume rm ... || true`.
5. Remove task-specific Docker networks using `docker network rm ... || true`.
6. Force-remove task-specific images if any were built using `docker rmi -f ... || true`.
7. Run `docker system prune -a --volumes -f || true`.
8. Remove the task directory with `rm -rf /root/task || true`.
9. Print `Cleanup completed successfully!` as the final message.

The script must be idempotent. Use `|| true` for cleanup commands that may legitimately find nothing to remove. Do not prompt for input.

### Dockerfile Instructions
Do not include a Dockerfile unless the selected scenario explicitly requires an app container. Prefer running the Python agent locally against the PostgreSQL docker-compose service.

If an app container is included:
- Keep it minimal.
- Do not install unnecessary OS packages.
- Do not bake API keys or secrets into the image.
- Do not use environment variables or `.env` references from docker-compose to pass secrets.
- Ensure the app container is not required for candidate editing if a local Python workflow is simpler.

The output should be a valid json schema:
- `README.md`: Candidate-facing task overview with exactly the four required sections and no solution details.
- `pyproject.toml`: Native Python manifest declaring package metadata and dependencies used by the scaffold.
- `docker-compose.yml`: PostgreSQL datastore configuration with no top-level version, no environment variables, no `.env` references, and localhost-only port binding.
- `init_database.sql`: FULLY POPULATED PostgreSQL schema and seed data matching the selected scenario.
- `run.sh`: Readiness script that starts PostgreSQL, verifies the scaffold key-free, and prints `ready`.
- `kill.sh`: Idempotent cleanup script following the required 9-step shape.
- `agent/__init__.py`: Package initializer.
- `agent/__main__.py`: CLI entry point with `--selfcheck` and optional real agent execution path.
- `agent/prompts.py`: System/developer prompt text guiding real tool use, safety, structured outputs, and escalation.
- `agent/tools.py`: Deterministic business tools wrapping database operations with explicit contracts.
- `agent/tool_contracts.py` or equivalent: Typed schemas for tool inputs, tool outputs, structured LLM decisions, and structured errors.
- `agent/orchestrator.py` or equivalent: Real LLM-driven tool-use loop with candidate stubs at the production boundary.
- `agent/db.py`: PostgreSQL connection and query helpers.
- `fixtures/*.json` or `fixtures/*.jsonl`: Realistic replay inputs and saved tool results for the selected scenario.
- `tests/test_*.py` or `invariants/test_*.py`: Candidate-facing checks for the expected production outcomes.

## Code file requirements
Code files must be complete, runnable, and internally consistent.

Requirements:
- All code and scripts must reference `/root/task` as the base directory.
- The repository must be self-contained except for the candidate's LLM provider key.
- The agent must call a real LLM provider when the candidate runs the actual agent flow with a key.
- The readiness path must not call the real agent flow or any candidate stub.
- Include `.env.example` with provider key names such as `OPENAI_API_KEY=` or `ANTHROPIC_API_KEY=`. Do not include real secrets.
- The generated code may read `.env` for provider keys at runtime, but docker-compose must not reference `.env`.
- Use explicit schemas for LLM outputs and tool inputs/outputs. Pydantic models, dataclasses with validation, or equivalent typed validation are appropriate.
- Tools should return structured results and structured errors with machine-readable codes.
- Side-effecting tools must be clearly separated from read-only tools.
- If the scenario involves duplicate client retries, include an idempotency table and ensure tests can observe that only one business-side effect occurs.
- If the scenario involves structured LLM output, include tests that prove malformed, unsupported, or ungrounded outputs are not persisted.
- If the scenario involves bounded repair, include tests that prove retry count is capped and escalation happens on terminal failures.
- Include logs or trace records that allow a reviewer to follow model decision, tool call, validation result, and persistence outcome without leaking secrets or excessive PII.
- Candidate-facing tests must check observable behavior, not implementation details.
- Keep file count lean. Prefer 8-14 files total, excluding small fixtures, unless the selected scenario truly needs more.
- Do not include generated lockfiles unless necessary.
- Do not include large datasets.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` appropriate for a Python agent repository.

It should exclude:
- `.env` and other local secret files.
- Python caches such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, and `*.pyc`.
- Virtual environments such as `.venv/`, `venv/`, and `env/`.
- Local coverage/build artifacts such as `.coverage`, `htmlcov/`, `dist/`, and `build/`.
- Local logs and temporary files.
- OS/editor files such as `.DS_Store` and `.idea/`.

Do not ignore the starter fixtures, SQL seed file, source files, README, or tests.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The candidate-facing README.md MUST contain exactly these output sections, in this order, and no others:
1. `## Task Overview`
2. `## Helpful Tips`
3. `## Objectives`
4. `## How to Verify`

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. NEVER empty. NO bold time-budget callouts.

The overview should mention the observable production symptoms, such as invalid database rows, duplicate side effects, unsafe tool execution, unvalidated model output, or failed replay traces. It must not name the exact stub functions, reveal the solution, or list implementation steps.

### Helpful Tips
Write 4-5 bullets max.

Provide practical guidance without revealing specific implementations. Each bullet starts with an action word: `Consider`, `Think about`, `Explore`, `Review`, or `Analyze`. Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

Helpful Tips must not include direct implementation instructions, exact method names, exact schema fixes, exact query names, or the answer.

### Objectives
Write 4-6 bullets max.

Frame objectives around outcomes rather than specific technical implementations. Objectives describe the `what` and `why`, never the `how`. Each bullet states an observable end-state, not a step or an API/library to use.

Good objective style:
- The agent rejects or safely escalates unsupported model decisions instead of persisting them.
- Replayed duplicate requests produce one business-side effect with traceable repeat responses.
- Tool calls and persistence outcomes are observable without exposing secrets or unnecessary sensitive data.

Bad objective style:
- Implement `validate_decision()` using Pydantic.
- Add a unique index to `agent_tool_requests`.
- Use LiteLLM retries and this exact prompt.

### How to Verify
Write 4-6 bullets max.

Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write. Each bullet is a check the candidate can run, such as test output, response shape, latency observation, log line, database row count, or memory reading.

Mention running `./run.sh` for readiness and then running the provided candidate-facing tests or replay script after adding a key. Do not include setup commands beyond what is necessary to verify readiness and behavior.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
Keep all of the following OUT of the generated README:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or equivalent package installation instructions.
- Database-connection details such as host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like `you should implement`, `add this middleware`, `create this class`, or `use <specific API>`.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each value must be filled with actual task content, not placeholder text.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the production agent/tool-use task.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the name.",
  "question": "A full candidate-facing task description written like a realistic engineering ticket or incident message that states the symptoms, business impact, constraints, and how to begin without revealing the implementation.",
  "code_files": {{
    "README.md": "Complete candidate-facing README content using exactly the four required sections in the required order: Task Overview, Helpful Tips, Objectives, and How to Verify.",
    "pyproject.toml": "Complete Python project manifest declaring the package metadata and libraries used by the scaffold without requiring install commands in run.sh.",
    ".gitignore": "Complete gitignore content appropriate for a Python agent repository with local secrets, caches, logs, build artifacts, and virtual environments excluded.",
    ".env.example": "Example provider-key file with empty API key variables and no real secrets.",
    "docker-compose.yml": "Complete PostgreSQL docker-compose configuration with no top-level version, no environment variables, no .env references, a localhost-only port binding, persistent task-specific volume, and a healthcheck.",
    "init_database.sql": "Complete PostgreSQL schema and seed data for the selected scenario, including realistic business tables, constraints, and audit/idempotency tables as needed.",
    "run.sh": "Complete readiness script that starts PostgreSQL, waits for readiness, performs a database round-trip, runs a key-free selfcheck, and prints ready.",
    "kill.sh": "Complete idempotent cleanup script following the required nine-step cleanup shape and ending with Cleanup completed successfully.",
    "agent/__init__.py": "Complete package initializer for the agent code.",
    "agent/__main__.py": "Complete CLI entry point containing a key-free selfcheck path and a separate real agent execution path that can call the model only when a provider key is present.",
    "agent/db.py": "Complete PostgreSQL connection and query helper module used by tools, selfcheck, and tests.",
    "agent/prompts.py": "Complete prompt module containing system and developer instructions that guide real LLM tool use, structured output, safety constraints, and escalation without exposing secrets.",
    "agent/tool_contracts.py": "Complete typed schema module for tool inputs, tool outputs, structured LLM decisions, validation errors, and trace records.",
    "agent/tools.py": "Complete deterministic tool module wrapping database-backed business operations with explicit input/output contracts and structured errors.",
    "agent/orchestrator.py": "Complete agent orchestration module containing the deliberately incomplete candidate stubs and the real LLM-driven tool-use loop.",
    "fixtures/replay_cases.jsonl": "Realistic replay fixtures aligned with the selected scenario and database seed data.",
    "tests/test_agent_invariants.py": "Candidate-facing pytest tests or invariants that verify observable production outcomes such as safe validation, idempotent side effects, bounded repair, and traceable persistence."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the root cause, expected strong fix, important tradeoffs, and evidence in the repository, without including full filled solution files.",
  "definitions": "An object of concise term-to-definition pairs for domain and agent/tool-use concepts used in the task, such as structured output validation, idempotency key, tool contract, bounded repair, audit log, and escalation.",
  "hints": "A single line nudging the candidate to inspect the agent trace, tool contracts, fixtures, and database side effects without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable production improvements such as valid persisted decisions, no duplicate side effects, bounded retries, structured errors, traceable logs, and production-clean code. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Python, basic PostgreSQL, real LLM API keys, structured JSON outputs, typed validation, tool calling, idempotency, and pytest-style local checks.",
  "short_overview": "A bullet list summarising the business problem, the production agent/tool-use technical focus, the provided repository shape, and the expected observable outcome."
}}

Use these EXACT keys. Do NOT use synonyms such as `task_title`, `files`, `repository`, `context`, `solution`, or `steps`. Do NOT emit `criterias`; the pipeline injects it. Output raw JSON only — no markdown fences and no prose outside the JSON object.

## CRITICAL REMINDERS
- Output must be valid JSON only, beginning with `{{` and ending with `}}`.
- Generate exactly one INTERMEDIATE build-it task for the combined competencies: Production Agent Engineering and Tool Use for Agents.
- Use ONE real-world scenario as the source of truth for the business domain and production symptoms.
- The task is infra-shaped: include `docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`.
- Use PostgreSQL for the scenario datastore unless the selected scenario explicitly requires a different external datastore.
- Docker-compose must not include a top-level version, environment variables, or `.env` references.
- Every exposed datastore port must use localhost-only binding with `127.0.0.1:<port>:<port>`.
- The generated agent must call a REAL model when the candidate provides a key. No FakeLLM, StubLLM, deterministic stand-in, regex intent parser, or keyword-only router may replace the model.
- `./run.sh` must be key-free and must not call candidate stubs or run the unfinished agent loop.
- The candidate-facing README must contain exactly four sections in this order: Task Overview, Helpful Tips, Objectives, How to Verify.
- Do not leak the reference answer into README, code comments, stubs, fixtures, tests, or question text.
- Candidate stubs should raise `NotImplementedError` with neutral contracts only.
- Keep the task focused on one production tool-use boundary decision and solvable within {minutes_range}.
- Ensure database schema, seed data, fixtures, prompts, code, tests, question, and answer are internally consistent.
- Include production-clean code expectations in outcomes: clear naming, structured errors, explicit validation, safe persistence, useful logging, and maintainable separation between orchestration, prompts, tools, and database access.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (INTERMEDIATE), Tool Use for Agents (INTERMEDIATE)": [
        PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_CONTEXT,
        PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_TOOL_USE_INTERMEDIATE_INSTRUCTIONS,
    ]
}