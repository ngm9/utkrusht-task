# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Tool Use for Agents assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

INPUT QUESTION PROMPT / SKILL SIGNAL:
{question_prompt}

TASK FOCUS:
The candidate is an intermediate AI Agent Engineer working on a production-facing tool-using agent. The task must be a realistic engineering work item where an existing local project has a small but meaningful flaw in tool definition, schema validation, orchestration, retries, idempotency, state handling, traceability, or safe tool invocation. The candidate should improve the implementation and verify the behavior using tests and a seeded local datastore.

You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task. Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level. The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.

WHAT THIS TASK TESTS:
- Ability to understand the division of responsibility between the LLM planner, the orchestration layer, and deterministic tools
- Ability to design or repair clear tool schemas with required fields, validation rules, and structured error outputs
- Ability to reason about multi-step tool workflows, retries, idempotency, fallback behavior, and partial success
- Ability to inspect agent traces, logs, or seeded records to diagnose wrong tool arguments, missing fields, duplicate side effects, or stale state
- Ability to implement pragmatic fixes in a small codebase without turning the task into a framework installation exercise
- Ability to preserve auditability, traceability, privacy-aware logging, and predictable tool contracts
- Ability to communicate expected behavior through tests and concise documentation

EVALUATION SIGNALS:
- Strong candidates keep strict validation, business rules, and side-effect safety in code rather than relying only on the LLM prompt
- Strong candidates use structured input and output contracts for tools, including explicit machine-readable error codes
- Strong candidates account for retry safety, idempotency, and state consistency when a tool has side effects
- Strong candidates preserve existing behavior while fixing the targeted flaw
- Strong candidates add or update focused tests that prove the bug is fixed and avoid over-engineering unrelated architecture
- Weak candidates only add prose instructions to a prompt, ignore validation or idempotency boundaries, or hide failures instead of returning structured errors

CRITICAL TASK GENERATION REQUIREMENTS:
- The generated task must be completable within {minutes_range} minutes for an INTERMEDIATE proficiency candidate
- The task must include a FULLY FUNCTIONAL starter project with a FULLY POPULATED local datastore seeded through SQL
- The task must use docker-compose for the datastore needed by the chosen scenario, plus run.sh and kill.sh
- The candidate should work in an existing implementation, not build a full agent platform from scratch
- Include enough broken behavior and tests for the candidate to discover the issue, but do not reveal the exact code changes in the README
- Keep the task focused on one primary tool-use-agent competency area with one or two supporting concerns
- Do not require advanced research topics, custom agent framework internals, production cloud configuration, credentials management, or broad system redesign

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the selected business domain, the agent workflow, the tool or tools involved, the datastore-backed state, and the specific flaw the candidate must fix.
2. What will the task look like? Describe the starter files, docker-compose datastore setup, seed data, tests, README framing, and what observable behavior will prove the candidate solved the problem.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INSTRUCTIONS = """

## GOAL
As a technical architect super experienced in tool-using agents, you are given a list of real world scenarios and proficiency levels for tool-using agents. You must generate a realistic, hands-on engineering assessment for an INTERMEDIATE AI Agent Engineer who can design, debug, and refine LLM-driven agents that plan, select, and invoke tools with clear schemas, validation, state handling, retries, and traceability. The task should feel like a production bugfix or enhancement ticket in an agent platform, not a toy exercise or trivia question.

## CONTEXT & CANDIDATE EXPECTATION
The candidate has a few years of experience building or maintaining production-facing agents that call internal tools, APIs, or datastore-backed capabilities. They are expected to work independently on standard integrations and moderately complex multi-tool flows, while relying on senior engineers for broad autonomy boundaries or high-risk compliance decisions. The assessment should test applied competence in tool contracts, orchestration, validation, idempotency, error handling, state, evaluation traces, and pragmatic test-driven repair.

The generated task must be completable within {minutes_range} minutes. It should require focused code reading and implementation, not broad system design. The candidate should receive a FULLY FUNCTIONAL starter project with a FULLY POPULATED local datastore so they can run tests, observe the failing behavior, and implement the fix.

## INSTRUCTIONS

### Nature of the Task
- The task must present a realistic work item involving an LLM-driven agent that invokes one or more deterministic tools for data retrieval, business actions, computation, or coordination.
- **CRITICAL**: The business domain, endpoint names, tool names, table names, and failure mode must come from ONE of the provided real-world scenarios. Do not invent a different domain or default to a generic chatbot.
- **CRITICAL**: Keep the scope at INTERMEDIATE level. The candidate may repair a schema, add validation, improve idempotency, coordinate a small multi-tool flow, normalize tool outputs, or add structured error handling. Do not require building a full agent framework, implementing vector search from scratch, designing a full production incident response process, or solving open-ended architecture.
- **CRITICAL**: The task must exercise Tool Use for Agents, not general web CRUD. The code should make it clear where the LLM-facing tool contract begins, where deterministic orchestration or validation belongs, and where datastore-backed state or audit logs are written.
- **CRITICAL**: Include a real flaw in the starter implementation that maps to the competency scope, such as missing required response fields, malformed tool-call arguments, duplicate side-effect tool calls on retry, missing idempotency keys, lack of validation before persisting LLM output, unsafe retry behavior, stale state reads, or failure to preserve normalized tool result shape.
- **CRITICAL**: The candidate should have to implement a focused fix and verify it through tests. The task should not be answerable by only editing documentation or adding comments.
- The generated task should include existing tests that fail before the fix and pass after the fix. You may also include a small replay script or fixture-driven test that demonstrates agent trace behavior.
- The candidate should be able to inspect seeded database rows, logs, or test fixtures to understand the workflow. However, do NOT expose database credentials or connection details in the README.
- The generated project should be concise: one service or worker module, one tool contract or schema module, one datastore access module, one test file or small test suite, plus scripts and README.
- The work item should have multiple reasonable implementation paths, but the expected behavior must be specific and observable.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, tool-use-agent documentation, framework documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The task is designed to evaluate applied engineering judgment, debugging ability, and implementation quality, not memorization.
- Candidates may use AI assistance to understand the codebase, generate test ideas, or explore implementation options.
- Candidates remain responsible for validating the final behavior with the provided tests and for ensuring the solution is secure, reliable, and maintainable.
- The README should not discourage external resources or imply that AI tools are prohibited.

## Code Generation Instructions
Generate a complete, runnable local project under `/root/task`. The project should model a small agent workflow where an LLM-facing orchestration layer calls deterministic tools and writes or reads state from the datastore. The codebase must be intentionally small enough for an intermediate candidate to understand quickly, but realistic enough that the failure mode reflects real production agent work.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

The generated code should include:
- An agent or orchestration module that receives a user request or replay event, decides which tool function to call, validates or normalizes tool results, and returns a structured response
- One or more tool modules with explicit input and output contracts, using structured types where appropriate
- A datastore access layer that reads seeded records or writes audit/state rows
- A focused failing test suite that captures the current bug and expected fixed behavior
- A README that explains the work item at a high level without revealing the exact implementation
- Scripts to start the datastore and run tests from a clean environment

The implementation should avoid unnecessary complexity. Do not require the candidate to call a live LLM provider, configure API keys, use paid services, or rely on network services outside docker-compose. Simulate LLM output or tool-call emissions with fixtures, local functions, or seeded trace rows so the candidate can focus on tool-use-agent engineering fundamentals.

Common valid task patterns include:
- Validate an LLM-produced structured response before persisting it, returning a machine-readable validation error instead of writing malformed state
- Add an idempotency key to a side-effect tool contract and ensure replayed agent turns do not duplicate external actions
- Repair a multi-tool orchestration so independent read-only tool calls are performed concurrently while preserving result shape
- Normalize paginated or heterogeneous tool outputs before passing them back to the LLM planner
- Add bounded retry and fallback behavior for transient tool failures without retrying unsafe side-effect operations
- Add trace correlation IDs and structured error objects so failures can be diagnosed in replay tests

## Infrastructure Requirements
This is an infra-shaped task. The generated task MUST include a local datastore provisioned with docker-compose, a seed SQL file, a run.sh script, and a kill.sh cleanup script. Use the datastore actually required by the selected scenario. For the provided tool-use-agent scenarios, this will usually be PostgreSQL-compatible storage for agent state, coverage rules, traces, disputes, idempotency records, or audit logs. Do not add extra datastores that the scenario does not exercise.

The datastore must be FULLY POPULATED with realistic seed data that supports the failing tests and the candidate workflow. The project must run locally without external credentials.

### Docker-compose Instructions
Create `/root/task/docker-compose.yml`.

- **MUST NOT include any version specification** in docker-compose.
- **MUST NOT include environment variables or .env file references** from the host.
- Use explicit values directly in the compose file only for the local assessment datastore.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Include only the datastore services required by the chosen scenario. Do not add Redis, queues, search engines, or app containers unless the scenario explicitly requires them.
- Configure a healthcheck so `run.sh` can wait for the datastore to be ready before running tests or migrations.
- Mount the SQL seed file into the datastore initialization directory when using PostgreSQL-compatible storage.
- Use stable container, volume, and network names that include the generated task name or a short task-specific prefix.

### init_database.sql Instructions
Create `/root/task/init_database.sql`.

- The SQL file must create all tables needed by the starter project and tests.
- The SQL file must seed realistic records for the chosen domain: tool metadata, business records, agent traces, retry records, idempotency records, validation examples, or audit logs as appropriate.
- Seed data must be sufficient for the tests to demonstrate the existing bug before the candidate fix and the expected behavior after the fix.
- Keep the schema small and understandable. Prefer 2-5 tables with clear names over a large enterprise schema.
- Include constraints where they support the task, such as NOT NULL fields, uniqueness on idempotency keys, or foreign keys between agent turns and tool calls.
- Do not include secrets, production-looking credentials, or unrelated sample data.
- Ensure seeded IDs and values match the fixtures and tests exactly.

### Run.sh Instructions
Create `/root/task/run.sh`.

- The script must use `#!/usr/bin/env bash` and `set -euo pipefail`.
- It must use `/root/task` as the working directory.
- It must start the datastore with `docker compose up -d`.
- It must wait for the datastore healthcheck or readiness command before running tests.
- It must run the project’s native test command for the selected runtime after the datastore is ready.
- It must not install the primary runtime or common libraries already present in the environment.
- It must not use `apt-get install`, global package-manager installs, or external service setup.
- It must print clear progress messages for starting infrastructure, waiting for readiness, and running tests.
- It must exit non-zero if tests fail.

## kill.sh file instructions
Create `/root/task/kill.sh` that performs complete, idempotent cleanup. The script MUST use `#!/usr/bin/env bash` and may use `set +e` so cleanup continues even if some resources are already absent.

The script must follow this 9-step shape:

1. Print a log line indicating cleanup is starting.
2. Stop docker-compose services from `/root/task` using `docker compose down --remove-orphans || true`.
3. Remove docker-compose volumes using `docker compose down -v --remove-orphans || true`.
4. Remove any task-specific named Docker volumes with `docker volume rm ... || true`.
5. Remove any task-specific Docker networks with `docker network rm ... || true`.
6. Force-remove task-specific Docker images if any were built, using `docker rmi -f ... || true`.
7. Run `docker system prune -a --volumes -f || true`.
8. Remove the task directory using `rm -rf /root/task || true`.
9. Print the final message `Cleanup completed successfully!`.

Every destructive command must be idempotent and include `|| true`. The script must print logs at every step so candidates and evaluators can see what cleanup is doing.

The output should be a valid json schema:
- `README.md` with concise candidate-facing task instructions
- `docker-compose.yml` with only the required datastore services
- `init_database.sql` with schema and seed data
- `run.sh` to start infrastructure and run the native test command
- `kill.sh` to stop services, remove volumes and networks, prune Docker resources, and remove `/root/task`
- Runtime manifest such as `pyproject.toml`, `package.json`, `pom.xml`, `Cargo.toml`, or equivalent for the selected implementation stack
- Source files implementing the starter agent workflow, tool contracts, datastore access, and intentionally flawed behavior
- Test files that fail before the candidate fix and pass after the fix

## Code file requirements
- All generated files must live under `/root/task`.
- The code must be syntactically valid and runnable.
- The code must avoid external paid APIs and live LLM calls. Use deterministic fixtures, fake LLM outputs, seeded trace rows, or local test doubles.
- The code must include a clearly named module for tool definitions or tool contracts.
- The code must include a clearly named module for agent orchestration or workflow execution.
- The code must include explicit validation logic or a clear TODO-adjacent defect that the candidate must repair.
- The code must use structured errors for validation, authorization, retry, idempotency, or tool invocation failures where relevant.
- Tests must assert observable outcomes such as no malformed rows being inserted, one side-effect row after repeated replay, stable idempotency keys, preserved normalized result shape, bounded retry counts, or structured error codes.
- Do not include hidden evaluator-only files in `code_files`. Everything needed to run and understand the task should be visible.
- The starting code should contain a realistic flaw, but it must not be so broken that the project cannot start or the tests cannot run.
- Keep file count reasonable. Prefer 8-14 files total including scripts, manifest, README, source, tests, and SQL.
- Do not include Dockerfile unless the app itself must run in a container. For these tasks, prefer running the app/tests locally against the docker-compose datastore.

## .gitignore INSTRUCTIONS
Create `/root/task/.gitignore` with practical ignores for the selected runtime and local execution. Include runtime caches, test caches, virtual environments or dependency directories, log files, coverage output, editor files, and OS metadata. Do not ignore source files, tests, README, docker-compose.yml, init_database.sql, run.sh, or kill.sh.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The candidate-facing README has EXACTLY these output sections, in this order, and NO others:

1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. NEVER empty. NO bold time-budget callouts. Mention that the local project is already wired to a datastore and tests, but do not include setup commands, database connection details, or the exact solution.

### Helpful Tips
Write 4-5 bullets max. Provide practical guidance without revealing specific implementations. Each bullet must start with an action word: `Consider`, `Think about`, `Explore`, `Review`, or `Analyze`. Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

### Objectives
Write 4-6 bullets max. Frame objectives around outcomes rather than specific technical implementations. Objectives describe the 'what' and 'why', never the 'how'. Each bullet states an observable end-state, not a step or an API/library to use.

### How to Verify
Write 4-6 bullets max. Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write. Each bullet is a check the candidate can run, such as test output, response shape, latency observation, log line, database row count, or structured error response.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like `you should implement`, `add this middleware`, `create this class`, or `use <specific API>`
- Database-connection details including host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Extra README sections such as `Database Schema Overview`, `Database Access`, `Performance Issues`, `NOT TO INCLUDE`, `Guidance`, `Tips`, or `Recommendations`

## REQUIRED OUTPUT JSON STRUCTURE
Return a single valid JSON object with the following canonical keys. Each field must contain the generated task content described below, not commentary about the process.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the task and is different from the display title.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, describing the candidate work item.",
  "question": "The full candidate-facing task description as a concise work item that explains the scenario, the failing behavior, the expected deliverable, and the time-bounded scope without revealing the exact implementation.",
  "code_files": {{
    "README.md": "The complete README.md content with exactly the four required sections in order: Task Overview, Helpful Tips, Objectives, and How to Verify, written concisely and without solution-revealing details.",
    "docker-compose.yml": "The complete docker-compose.yml content for only the datastore services required by the selected scenario, with localhost-only port bindings, no version field, no .env references, and appropriate healthchecks.",
    "init_database.sql": "The complete SQL initialization file that creates the schema and seeds all datastore records needed by the starter code and tests.",
    "run.sh": "The complete executable shell script that starts docker-compose infrastructure, waits for datastore readiness, and runs the runtime-native test command from /root/task.",
    "kill.sh": "The complete executable shell script that idempotently stops compose services, removes volumes, networks, task images, prunes Docker resources, deletes /root/task, and prints cleanup progress including the final success message.",
    ".gitignore": "The complete .gitignore content appropriate for the selected runtime and local test execution.",
    "pyproject.toml or package.json or equivalent runtime manifest": "The complete native runtime manifest needed to run the local project and tests without installing the runtime itself.",
    "source files": "A mapping of source file paths to complete file contents for the starter agent workflow, tool contracts, datastore access, validation or idempotency logic, and the intentional flaw the candidate must repair.",
    "test files": "A mapping of test file paths to complete file contents for focused tests that fail before the candidate fix and pass when the expected tool-use-agent behavior is implemented."
  }},
  "answer": "A high-level evaluator-facing solution approach explaining the intended fix, the reasoning behind it, how it respects tool-use-agent boundaries, and which tests or observations should pass after completion.",
  "definitions": "An object mapping important task-specific terms to concise definitions, including relevant agent/tool concepts, domain terms, structured error terms, and datastore-backed state terms used in the task.",
  "hints": "A single line nudging investigation toward the relevant agent trace, tool contract, validation boundary, retry path, or persisted state without revealing the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable behavior such as valid structured responses, safe side effects, stable retries, preserved tool outputs, passing tests, and clean datastore state. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including reading a small codebase, running local tests, understanding structured tool contracts, interpreting agent traces, and reasoning about datastore-backed state.",
  "short_overview": "A bullet list summarising the business problem, the agent/tool workflow, the specific technical focus, and the expected observable outcome."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown explanations and no surrounding code fences. Emit the raw JSON object starting with `{{` and ending with `}}`.
2. The generated task MUST be an infra-shaped local project with docker-compose.yml, init_database.sql, run.sh, and kill.sh.
3. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
4. docker-compose.yml **MUST NOT include any version specification**.
5. docker-compose.yml **MUST NOT include environment variables or .env file references**.
6. **SECURITY-CRITICAL**: every datastore port exposed to the host MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
7. Include only the datastore required by the chosen scenario. Do not invent extra infrastructure.
8. Do not include a Dockerfile unless the app itself must run in a container; prefer local runtime-native tests against the docker-compose datastore.
9. run.sh must use `docker compose up -d`, wait for readiness, and run the native test command.
10. kill.sh must follow the 9-step cleanup shape, use `|| true` for idempotency, print logs at every step, run `docker system prune -a --volumes -f`, remove `/root/task`, and end with `Cleanup completed successfully!`.
11. README.md must contain exactly Task Overview, Helpful Tips, Objectives, and How to Verify, in that order, and no other sections.
12. README.md must not include setup commands, database connection details, direct solutions, code snippets, or solution-revealing API/library/function/pattern names.
13. The starter code must be FULLY FUNCTIONAL except for the intended failing behavior captured by tests.
14. The datastore must be FULLY POPULATED with realistic seed data that matches tests and fixtures.
15. The task must stay within INTERMEDIATE Tool Use for Agents scope: schema contracts, validation, orchestration, retries, idempotency, state, traceability, fallback behavior, and pragmatic debugging.
16. Do not require live LLM API keys, cloud services, paid APIs, production credentials, or broad platform setup.
17. Do not turn the task into generic CRUD, generic SQL tuning, or pure framework syntax recall. The central skill must be tool use for agents.
18. The answer field is evaluator-facing and may describe the expected solution, but the README and question must not give the fix away.
19. Ensure all JSON string values are validly escaped, especially file contents that contain quotes, newlines, shell scripts, SQL, or code.
20. The `code_files` object must include complete file contents, not placeholders or summaries.
"""

PROMPT_REGISTRY = {
    "Tool Use for Agents (INTERMEDIATE)": [
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_CONTEXT,
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_TOOL_USE_FOR_AGENTS_INTERMEDIATE_INSTRUCTIONS,
    ]
}