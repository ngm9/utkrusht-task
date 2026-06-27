# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a GraphQL and Python FastAPI assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}


CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and GraphQL/FastAPI problem the candidate will be solving)
2. What will the task look like? (Describe the type of GraphQL schema, resolver, FastAPI integration, database, validation, authorization, testing, or performance work required, the expected deliverables, and how it aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in GraphQL and Python FastAPI, you are given a list of real world scenarios and proficiency levels for GraphQL and FastAPI.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to work at an INTERMEDIATE level with a few years of practical API development experience, not as a beginner and not as an expert architect.
The generated task should assess realistic engineering work in a FastAPI application that exposes a GraphQL endpoint and uses a relational datastore for resolver-backed behavior.
The candidate should be able to demonstrate practical judgment around schema evolution, resolver design, request context, validation, authorization, transactional behavior, query efficiency, and tests without being asked to solve advanced federation, gateway ownership, or large-scale subscription architecture.
The starting environment must be FULLY FUNCTIONAL and FULLY POPULATED: the app, database schema, seed data, and readiness scripts must run cleanly before the candidate changes anything.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor an existing GraphQL/FastAPI behavior, or fix meaningful logical bugs in the existing code.
- **CRITICAL**: The task must stay within INTERMEDIATE GraphQL and Python FastAPI scope: modular schema work, SDL maintenance, queries and mutations, nested resolvers, resolver context, Pydantic validation, SQLAlchemy-backed persistence, dependency injection, authentication or authorization checks, structured errors, batching/caching for N+1 avoidance, logging or observability hooks, and pytest-based integration tests are appropriate.
- **CRITICAL**: Do NOT require expert-level Apollo Federation design, advanced gateway architecture, production subscription reliability design, deep distributed systems design, or frontend client implementation as the primary task.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix errors.
- The question should be a real-world scenario and not a trick question based on syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with the proficiency level required in the competency definition, ensuring that no two questions generated are similar.
- For BEGINNER and BASIC and INTERMEDIATE levels of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible for these levels.
- For this INTERMEDIATE task, the candidate should make focused changes across a modest FastAPI/GraphQL project, such as improving one mutation, one query with nested resolvers, one authorization path, one validation/error flow, or one N+1 performance issue.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest best practices and language versions. Strictly avoid using outdated versions of Python, FastAPI, GraphQL libraries, SQLAlchemy, or testing patterns in the code scenarios.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE GraphQL and Python FastAPI proficiency.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The generated task must include a clear Current Implementation and Required Changes description so the starter code perfectly matches what the candidate receives and does not accidentally include the solution.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, GraphQL documentation, FastAPI documentation, SQLAlchemy documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.
- The candidate-facing task must still be specific, bounded, and verifiable so that AI assistance does not turn the assessment into an ambiguous architecture essay.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a GraphQL and Python FastAPI task that:
- Draws inspiration from the input scenarios given above to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency and the years of experience given as input, keeping in mind that AI assistance is allowed.
- Tests practical GraphQL and FastAPI skills that require more than a simple AI query to solve, even while keeping the competency scope and proficiency level in mind.
- Uses FastAPI as the HTTP application with a GraphQL endpoint such as `/graphql` or `/api/graphql`.
- Uses a Python GraphQL server library appropriate for FastAPI, such as Strawberry, Ariadne, Graphene, or another current Python GraphQL implementation.
- Uses PostgreSQL with SQLAlchemy or an equivalent Python database layer for realistic resolver persistence and integration tests.
- Includes schema definition files or modular GraphQL schema code that the candidate can extend or refactor without breaking existing clients.
- Prefer tasks such as adding a non-breaking mutation input type while keeping existing arguments, mapping validation failures to structured GraphQL errors, enforcing resolver-level authorization from FastAPI request context, reducing nested resolver query counts with batching, or improving transactional integrity around a mutation.
- Avoid pure syntax recall, installation trivia, broad architecture essays, or tasks where the only solution is to copy framework boilerplate.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.

## Infrastructure Requirements
The generated task is infrastructure-backed and MUST include a PostgreSQL datastore because the scenario exercises database-backed FastAPI GraphQL resolvers.
The candidate must receive a complete local project under /root/task with application code, tests, database initialization, docker-compose.yml, run.sh, and kill.sh.
The starter project must be runnable and must not require the candidate to repair syntax, imports, missing manifests, missing seed data, or broken infrastructure before starting the actual task.

### Docker-compose Instructions
- Include a `docker-compose.yml` file for PostgreSQL.
- The `docker-compose.yml` file **MUST NOT include any version specification**.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432` for PostgreSQL.
- The PostgreSQL service must use official PostgreSQL image tags appropriate for current local development.
- The PostgreSQL service MUST set the standard init environment variables inline in `environment:`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Do not use `.env` files or dollar-brace host variable indirection for PostgreSQL initialization values. Inline service environment values are required because the image will NOT initialize without them.
- The init SQL, healthcheck, application connection string, and tests must use the same PostgreSQL user and database.
- Add a healthcheck that uses `pg_isready` with the same user and database configured in the service environment.
- Mount `init_database.sql` into the standard PostgreSQL init directory so the database is FULLY POPULATED with schema and seed data on first startup.
- Use a named Docker volume for PostgreSQL data and a named network for task services.
- Do not include unrelated datastores, caches, queues, brokers, search engines, or application containers unless the selected scenario explicitly requires them.

### init_database.sql Instructions
- Include an `init_database.sql` file that creates all tables required by the selected scenario.
- The database must be FULLY POPULATED with realistic seed data that supports the GraphQL query, mutation, authorization, validation, transaction, or N+1 behavior being assessed.
- Include enough rows to make the issue observable for intermediate candidates, such as multiple users, roles, membership rows, parent-child records, nested GraphQL entities, and edge-case input rows.
- Keep the schema focused and small enough to complete within {minutes_range} minutes.
- Use straightforward relational constraints that support the scenario, such as primary keys, foreign keys, unique constraints, and relevant indexes.
- Do not hide the main challenge in obscure database tricks; the challenge should remain GraphQL and FastAPI application work.
- If the task involves query-count or performance behavior, seed enough related records so the baseline issue is visible without making the local test environment slow.

### Run.sh Instructions
- Include a `run.sh` file at the project root.
- `run.sh` must be executable and use `#!/usr/bin/env bash` with strict shell settings.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- `run.sh` is a readiness and self-check script, NOT the grader.
- The first step in `run.sh` MUST install the project dependencies using the Python-native dependency command, such as `pip install -q -r requirements.txt`.
- `run.sh` MUST bring PostgreSQL up using `docker compose up -d`.
- `run.sh` MUST wait for PostgreSQL health before running application smoke checks.
- `run.sh` MUST verify that the starter app imports successfully and that the FastAPI application object can be loaded.
- `run.sh` MAY run a lightweight smoke command that checks database connectivity or metadata creation, but it MUST NOT run the grader test suite that is designed to fail until the candidate solves the task.
- `run.sh` MUST exit 0 on the unsolved starter code when infrastructure and imports are healthy.
- `run.sh` must print clear logs at every step so candidates can understand readiness failures.
- Do not use `apt-get` or system package installation for Python itself; the runtime is pre-installed.

## kill.sh file instructions
1. Include a `kill.sh` file at the project root with `#!/usr/bin/env bash` and strict shell settings.
2. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
3. Stop running containers with `docker compose down --remove-orphans || true` from /root/task.
4. Remove Docker volumes associated with the task, including the named PostgreSQL volume, using `docker volume rm ... || true`.
5. Remove Docker networks associated with the task using `docker network rm ... || true`.
6. Force-remove task-related Docker images if any were built or tagged for the task, using `docker rmi -f ... || true`.
7. Run `docker system prune -a --volumes -f || true` to aggressively clean dangling resources.
8. Remove the task directory with `rm -rf /root/task || true`.
9. Print logs at every step, use `|| true` for idempotency, and end with the exact message `Cleanup completed successfully!`.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastapi, a Python GraphQL server library, SQLAlchemy or equivalent database library, PostgreSQL driver, pytest, and HTTP test client dependencies required in the scenario)
  - docker-compose.yml (PostgreSQL datastore only, with localhost-only port binding and no version specification)
  - init_database.sql (PostgreSQL schema and seed data for the selected scenario)
  - run.sh (Readiness script that installs dependencies, starts PostgreSQL, waits for health, and smoke-checks the starter app without running failing grader tests)
  - kill.sh (Idempotent cleanup script following the required cleanup instructions)
  - .gitignore (Ignore Python caches, virtual environments, environment files, logs, pytest artifacts, and local build artifacts)
  - Any Python package files, GraphQL schema files, tests, fixtures, or configuration files that are to be included as part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.

## Code file requirements
- More than 1 file can be generated but make sure all files are included in the JSON structure correctly.
- Code should follow Python PEP8 guidelines and current FastAPI practices.
- The generated project structure should use a sensible package layout such as `app/main.py`, `app/db.py`, `app/models.py`, `app/schema.py`, `app/resolvers.py`, and `tests/`.
- The FastAPI app and GraphQL endpoint must be FULLY FUNCTIONAL in the starter state.
- The database schema and seed data must match the starter code exactly.
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, existing flawed or incomplete behavior, and minimal setup code.
- **CRITICAL**: Starter code must perfectly implement only the Current Implementation described in the question. If the baseline has an N+1 issue, missing authorization, weak validation, or unstructured error handling, the starter code must exhibit exactly that behavior without syntax errors.
- The core business logic functions or class methods that the candidate needs to implement must be left incomplete only where appropriate, or implemented in the intentionally flawed baseline described in the task.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- Avoid comments such as "intended behavior", "add validation here", "use loader here", "wrap this in a transaction", or "check roles here".
- Existing starter functionality must run cleanly; the candidate should not need to fix imports, package setup, database connectivity, or broken app startup.
- Include tests that express the desired behavior but do not make `run.sh` execute them as the readiness gate.
- Tests may cover GraphQL response shape, error extensions, authorization outcomes, database row changes, transaction behavior, bounded query counts, and backward-compatible schema behavior.
- The candidate-facing task should require implementation or refactoring, not just editing documentation.
- Use environment-based configuration responsibly in the Python code, but do not require a README section with database credentials or connection details.

## .gitignore INSTRUCTIONS
Standard Python and local infrastructure gitignore:
- `__pycache__/`
- `*.pyc`
- `.env`
- `.venv/`
- `venv/`
- `.mypy_cache/`
- `.pytest_cache/`
- `*.egg-info/`
- `build/`
- `dist/`
- `.DS_Store`
- `*.log`
- `.coverage`
- `htmlcov/`
- local editor and temporary files

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order and no others:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content.
Task Overview section MUST contain the exact business scenario from the task description.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific task scenario being generated.
Use concrete business context, not generic descriptions.
The README must NOT contain database-connection details such as host, port, username, password, database name, client-tool suggestions, or placeholder deployment values.

### Task Overview
- Task Overview must be 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Helpful Tips may point candidates toward thinking about schema compatibility, request context, resolver behavior, validation boundaries, data consistency, performance observations, or test expectations in general terms.

### Objectives
- Objectives must be 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should be clear, measurable goals for the candidate.
- These objectives will also be used to verify task completion and award points.

### How to Verify
- How to Verify must be 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, GraphQL response shape, stable error payload, bounded query count, database row state, latency observation, or log line.
- These points will help the candidate verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points.

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `pytest`, `mvn test`, or any equivalent command.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use a specific API".
- Database-connection details including host, port, username, password, database name, and client-tool suggestions.
- Any heading named "NOT TO INCLUDE", "Do not include", "Database Schema Overview", "Database Access", or "Performance Issues".

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that describes the GraphQL and FastAPI task without using spaces or punctuation beyond hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, different from the repository name, and specific to the selected business scenario.",
  "question": "A complete candidate-facing task description that includes the business scenario, Current Implementation, Required Changes, constraints, and expected scope while avoiding solution hints.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Helpful Tips, Objectives, and How to Verify in that order, with no setup commands, direct solutions, database credentials, or extra sections.",
    ".gitignore": "A standard Python project gitignore that excludes caches, virtual environments, environment files, local logs, test artifacts, build outputs, and temporary files.",
    "requirements.txt": "A Python dependency manifest containing the runtime libraries needed for FastAPI, the selected Python GraphQL server integration, PostgreSQL database access, SQLAlchemy or equivalent persistence, validation, and testing.",
    "docker-compose.yml": "A Docker Compose configuration with no version specification that starts only the required PostgreSQL service using inline initialization environment variables, localhost-only port binding, a healthcheck, a named volume, and a named network.",
    "init_database.sql": "A PostgreSQL initialization script that creates the focused relational schema and realistic seed data required for the selected GraphQL and FastAPI scenario.",
    "run.sh": "An executable readiness script that installs Python dependencies, starts PostgreSQL, waits for health, verifies imports and application loading, and exits successfully on the unsolved starter without running the failing grader tests.",
    "kill.sh": "An executable idempotent cleanup script that stops compose services, removes task volumes, networks, images, prunes Docker resources, deletes /root/task, prints logs at each step, and ends with the required success message.",
    "app/main.py": "The FastAPI application entry point that wires configuration, database access, dependencies, and the GraphQL endpoint in a runnable starter state without containing the candidate's completed solution.",
    "app/db.py": "The database connection and session management module that supports PostgreSQL-backed app behavior and tests while keeping configuration simple and consistent with the compose service.",
    "app/models.py": "The persistence model definitions or table access layer that match init_database.sql and support the selected scenario's relationships and constraints.",
    "app/schema.py": "The GraphQL schema definition or schema assembly module that exposes the starter query or mutation surface and leaves room for the candidate's scoped schema evolution work.",
    "app/resolvers.py": "The resolver module containing the intentionally incomplete or flawed intermediate-level behavior described in Current Implementation, while remaining syntactically valid and runnable.",
    "tests/test_graphql_behavior.py": "A pytest test module that exercises the expected GraphQL behavior after completion, such as response shape, structured errors, authorization, transactional integrity, or bounded nested data access."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected schema, resolver, FastAPI context, validation, authorization, database, performance, and testing changes without requiring one exact implementation.",
  "definitions": "An object of concise term-to-definition pairs for relevant GraphQL, FastAPI, database, validation, authorization, and testing terminology used in the task.",
  "hints": "A single-line hint nudging investigation toward the right area of the GraphQL/FastAPI flow without revealing the exact fix, API, library call, or implementation pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable GraphQL response behavior, database correctness, security or validation outcomes, performance improvements where applicable, and passing tests in simple English.",
  "pre_requisites": "A bullet list of assumed prior knowledge and skills using declarative capability phrases only, such as Python 3.11 proficiency, comfort with FastAPI request handling, familiarity with GraphQL schemas and resolvers, understanding of SQL-backed persistence, and experience with pytest.",
  "short_overview": "A bullet list in simple English summarizing the business problem, the GraphQL and FastAPI technical focus, and the expected observable outcome after the candidate completes the work."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, under 50 characters, and kebab-case.
3. **title** must be a human-readable display name in action-verb format, 50-80 characters, and different from name.
4. **code_files** must include README.md, .gitignore, requirements.txt, docker-compose.yml, init_database.sql, run.sh, kill.sh, and all Python source and test files required for the task.
5. **README.md** must follow exactly Task Overview, Helpful Tips, Objectives, How to Verify, with no extra output sections.
6. **Starter code** must be runnable and FULLY FUNCTIONAL but must NOT contain the candidate's completed solution.
7. **run.sh** must install Python dependencies first, start PostgreSQL, wait for health, smoke-check imports/app loading, and must NOT run the failing grader tests.
8. **docker-compose.yml** MUST NOT include any version specification and MUST bind PostgreSQL to localhost only.
9. PostgreSQL initialization values must be inline in the compose service environment, and init SQL, healthcheck, app connection, and tests must use the same user and database.
10. **kill.sh** must follow the 9-step cleanup shape, use `|| true` for idempotency, print logs at every step, and end with `Cleanup completed successfully!`.
11. **hints** must be a single line and must not give away the answer.
12. **definitions** must include relevant GraphQL and FastAPI terms.
13. **outcomes** and **short_overview** must be concise bullet-style or short-line content in simple language.
14. **pre_requisites** must list assumed prior knowledge only, not setup or verification steps.
15. **Task must be completable within {minutes_range} minutes** for the given INTERMEDIATE proficiency level.
16. **NO comments in code** that reveal the solution or give hints.
17. **Use Python 3.11+, current FastAPI practices, current GraphQL library patterns, SQLAlchemy or equivalent database access, and pytest** throughout.
18. Select a different real-world scenario each time for variety.
"""

PROMPT_REGISTRY = {
    "GraphQL (INTERMEDIATE), Python - FastAPI (INTERMEDIATE)": [
        PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_CONTEXT,
        PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_GRAPHQL_PYTHON_FASTAPI_INTERMEDIATE_INSTRUCTIONS,
    ]
}