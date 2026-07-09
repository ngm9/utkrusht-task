# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_POSTGRESQL_FASTAPI_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_POSTGRESQL_FASTAPI_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI and PostgreSQL assessment task.

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

1. What will the task be about? (Describe the business domain, API/database context, and production problem the candidate will be solving)
2. What will the task look like? (Describe the type of FastAPI + PostgreSQL implementation, debugging, optimization, or refactoring required, the expected deliverables, and how it aligns with ADVANCED proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_POSTGRESQL_FASTAPI_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python FastAPI and PostgreSQL-backed API systems, you are given a list of real world scenarios and proficiency levels for Python FastAPI and PostgreSQL.
Your job is to generate a complete assessment task definition so that a candidate is presented with a FULLY FUNCTIONAL FastAPI application backed by a FULLY POPULATED PostgreSQL database, but with production-grade correctness, performance, concurrency, security, observability, or maintainability issues that require advanced-level backend and database engineering skills.

The candidate should work on an existing service rather than designing an entire platform from scratch. The task must assess practical ability with:
- advanced FastAPI routing, dependency injection, async request handling, Pydantic request/response models, and layered application structure
- PostgreSQL schema reasoning, complex SQL, indexing, transactions, query-plan analysis, and application/database integration
- production API concerns such as idempotency, authorization boundaries, consistent error models, structured logging, health/readiness behavior, and backwards-compatible contract changes
- diagnosing and fixing realistic bottlenecks such as N+1 queries, slow multi-table reads, unsafe transaction boundaries, blocking IO in async routes, missing constraints, or inefficient pagination
- delivering focused changes within the existing architecture without rewriting the whole application

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python FastAPI application with a FULLY POPULATED PostgreSQL database already wired together through Docker Compose. The starting project includes:
- a runnable FastAPI service with existing routers, schemas, services, repositories, dependency functions, and tests
- a PostgreSQL database initialized from `init_database.sql` with realistic schema relationships and enough seed data to expose the intended problem
- one or more API flows that work syntactically and respond to requests but exhibit deliberate advanced issues such as slow execution, incorrect transaction behavior, leaky response modeling, missing authorization checks, weak validation, inconsistent error handling, or poor async/database integration
- a clear baseline that candidates can inspect through API responses, logs, tests, sample queries, and measurable database behavior
- no syntax errors, no missing imports, and no broken environment setup

The candidate's responsibility is to analyze the existing application and database, identify the root causes, and implement a production-grade improvement that fits the existing codebase. The task completion should involve advanced reasoning across FastAPI, async Python, SQLAlchemy async or an equivalent async database layer, PostgreSQL query design, indexing, transactional integrity, and API contract preservation.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, descriptive, under 50 characters, and written in kebab-case.
- Task title MUST be human-readable in an "<action verb> <subject>" format and between 50-80 characters.
- Task must provide an existing FastAPI + PostgreSQL application that is FULLY FUNCTIONAL but intentionally flawed in a realistic production way.
- **CRITICAL**: The candidate must not need to repair the environment. The application and database must start successfully, pass basic smoke checks, and expose the intended buggy, risky, or slow behavior.
- **CRITICAL**: The task must assess ADVANCED proficiency. It should require independent diagnosis and implementation across API design, async-safe application code, PostgreSQL performance/correctness, and production-readiness tradeoffs.
- **CRITICAL**: Keep the task bounded enough to complete within {minutes_range} minutes. Advanced does not mean unlimited scope; the task should focus on one compact production work item with two to four related issues.
- **CRITICAL**: The starter code must perfectly implement the current flawed state described in the question. It must not accidentally include the fix, optimized query, corrected index, final transaction boundary, final authorization rule, or final validation behavior.
- **CRITICAL**: Do not turn this into a generic system-design prompt. The candidate must modify a working codebase and database artifacts.
- **CRITICAL**: Do not make installation, Docker troubleshooting, package management, or framework configuration the main challenge.
- The selected scenario should be a real-world API/data problem such as project activity feeds, audit-event search, entitlement-aware reporting, inventory reservations, billing ledger reconciliation, incident timelines, healthcare appointment intake, multi-tenant customer analytics, or support ticket SLA dashboards.
- Good advanced task shapes include one of the following:
  - a slow FastAPI endpoint caused by N+1 database access, missing PostgreSQL indexes, over-fetching response fields, and weak pagination limits
  - an unsafe write workflow where multiple rows are changed without an appropriate transaction or idempotency protection
  - a multi-tenant read or write path where authorization boundaries, row filtering, and response serialization are incomplete
  - an API endpoint whose Pydantic models leak internal database fields or mishandle partial update semantics
  - a background or streaming flow that blocks the event loop or performs database work with unsafe resource lifetimes
  - a complex reporting query that requires a better SQL shape, appropriate index strategy, and measurable verification
- The problem should require candidates to reason about both FastAPI code and PostgreSQL behavior. Avoid a database-only task and avoid an API-only task.
- The task should include enough starter code to reveal architecture and current behavior: routers, schemas, dependencies, services, repositories, SQL or ORM queries, test scaffolding, and seed data.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- The question must NOT include hints. The hints will be provided only in the "hints" field.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with ADVANCED proficiency in Python FastAPI and PostgreSQL.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, FastAPI documentation, PostgreSQL documentation, SQLAlchemy documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect advanced Python FastAPI and PostgreSQL proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates may use AI to help analyze code, SQL, and documentation, but the task should still require their own judgment about API contracts, transaction boundaries, query plans, performance tradeoffs, security boundaries, and maintainable implementation.

## Code and Database Generation Instructions
Based on real-world scenarios, create a Python FastAPI and PostgreSQL task that:
- Draws inspiration from the input scenarios for business context and technical requirements
- Matches ADVANCED proficiency level for engineers expected to own production-grade FastAPI services and PostgreSQL-backed workflows
- Can be completed within {minutes_range} minutes
- Tests practical advanced skills in FastAPI routing, dependency injection, async database access, Pydantic modeling, layered service/repository structure, transaction handling, query optimization, indexing, error modeling, tests, and observability-aware debugging
- Selects a different real-world scenario each time to ensure variety in task generation
- Provides a working application and database with one focused production issue or a small cluster of related issues
- Includes measurable current behavior and measurable expected behavior without revealing the implementation details in the candidate-facing README
- Uses Python 3.10+ style with clear type hints and modern FastAPI/Pydantic patterns appropriate to the generated codebase
- Uses PostgreSQL features appropriate for the selected problem, such as constraints, composite indexes, partial indexes, JSONB fields, CTEs, transactions, RETURNING, advisory locks, EXPLAIN-friendly sample queries, or row-level filtering when relevant
- Keeps all generated files valid, executable, and internally consistent

## Infrastructure Requirements
The generated task MUST include a Docker-based local infrastructure because this assessment requires PostgreSQL. The task definition must include:
- `docker-compose.yml` for the FastAPI application service and PostgreSQL service
- `Dockerfile` for the FastAPI application container
- `run.sh` that starts the environment with `docker compose up -d`, waits for readiness, and validates the API/database are responding
- `init_database.sql` that initializes PostgreSQL schema and seed data
- FastAPI source code, tests, dependency files, README.md, .gitignore, and any SQL files needed for sample diagnostics

No `kill.sh` is needed. E2B sandboxes are destroyed as a whole, so container cleanup is automatic.

### Docker-compose Instructions
- MUST include a PostgreSQL service and a FastAPI application service.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- **MUST NOT include environment variables or .env file references**.
- Use hardcoded configuration values instead of environment variables.
- PostgreSQL database name, username, password, and service host must be hardcoded consistently across Compose, application configuration, and tests.
- PostgreSQL should initialize automatically by mounting `init_database.sql` into `/docker-entrypoint-initdb.d/`.
- The FastAPI app service should depend on PostgreSQL and should start with a production-like ASGI command suitable for the generated project.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for PostgreSQL exposed to the host.
- Bind the FastAPI application port to localhost as well, for example `127.0.0.1:8000:8000`.
- Do not add Redis, Kafka, Elasticsearch, or any other datastore unless the selected scenario explicitly requires it. For this competency pair, PostgreSQL is the required datastore.
- Keep the infrastructure deterministic, simple to run, and focused on the FastAPI + PostgreSQL assessment.

### init_database.sql Instructions
- Create a realistic PostgreSQL schema aligned to the selected real-world scenario.
- Include enough schema complexity for ADVANCED proficiency: usually 4-8 related tables with primary keys, foreign keys, constraints, timestamps, and realistic relationships.
- Populate the database with realistic seed data sufficient to expose the intended API/database issue.
- Include larger synthetic data sets when performance is central, but keep initialization reliable within the assessment environment.
- Include intentional database-side issues only where they support the task, such as a missing composite index, missing uniqueness constraint, weak tenant boundary, inefficient query shape, poor data distribution for a planned query, or a transaction-sensitive relationship.
- Do NOT include optimized indexes, corrected constraints, rewritten queries, or any SQL that gives away the solution.
- Do NOT include comments that reveal the exact optimization or fix.
- SQL files must be valid and executable in PostgreSQL without manual intervention.
- If sample diagnostic queries are included in a separate SQL file, they must demonstrate current behavior without showing the final answer.

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- Use `set -e` and clear progress logs.
- Do not install Python, Docker, PostgreSQL, FastAPI, or common runtime dependencies in `run.sh`; the template and containers provide the runtime environment.
- Start from `/root/task` and validate required files exist before starting services.
- Wait until PostgreSQL is ready and accepting connections.
- Wait until the FastAPI application health or readiness endpoint responds successfully.
- Validate at least one application endpoint that demonstrates the service is reachable, without solving the candidate task.
- Print the local URLs and concise status information after validation.
- Do not run destructive cleanup commands.
- Do not require manual SQL execution; PostgreSQL initialization must happen through Docker entrypoint mounts.

### Dockerfile Instructions
- Use a suitable Python 3.10+ base image.
- Set WORKDIR to `/root/task`.
- Install only application dependencies from the generated dependency manifest.
- Copy the FastAPI application files into the image.
- Expose the FastAPI port used by docker-compose.
- Start the app with a clear ASGI command.
- Do not depend on `.env` files or external environment variables.
- The Dockerfile should be functional and reasonably production-like, but Docker optimization itself should not be the main candidate task unless the selected scenario specifically requires container improvements within the FastAPI/PostgreSQL scope.

The output should be a valid json schema:
  - README.md (CRITICAL - follow the exact structure specified below)
  - .gitignore (Python, FastAPI, PostgreSQL, Docker, IDE, and test exclusions)
  - docker-compose.yml (FastAPI app and PostgreSQL services, no version field, no environment variable references)
  - Dockerfile (FastAPI application container)
  - run.sh (deployment and readiness validation script using docker compose up -d)
  - init_database.sql (PostgreSQL schema and seed data with the intentional current-state issue)
  - requirements.txt or pyproject.toml (Python dependencies and test tooling appropriate for the generated project)
  - app/main.py (FastAPI application entry point)
  - app/api/routes or app/routers files (route definitions for the selected domain)
  - app/schemas files (Pydantic request/response models)
  - app/dependencies files (database session, auth, request context, or other dependencies as needed)
  - app/services files (business logic with the current flawed behavior)
  - app/repositories files (database access layer with the current flawed behavior)
  - app/db files (async PostgreSQL connection/session setup)
  - app/core files (configuration, errors, logging, health/readiness as needed)
  - tests files (focused tests that expose the required behavior but do not contain the solution)
  - optional sample_queries.sql (diagnostic SQL for performance-oriented tasks, without final optimized SQL)

## Code file requirements
- Multiple files will be generated following a maintainable FastAPI project structure.
- The application MUST be executable and must start successfully with the generated Docker infrastructure.
- The generated starter code MUST represent the exact current implementation described in the task question.
- DO NOT include TODO comments, placeholder comments, or comments that reveal the exact solution.
- DO NOT include the final optimized query, final index, final transaction boundary, final authorization rule, or final validation rule in starter code.
- Existing non-task functionality must work correctly.
- The candidate should be able to inspect and run tests, call endpoints, and observe the issue within a few minutes.
- Use async database access when the scenario involves async FastAPI request handling and database IO.
- Avoid blocking IO inside async route handlers unless that is the intentional issue to be fixed.
- Keep the scope focused: do not require a full authentication platform, distributed tracing system, message queue architecture, Kubernetes deployment, or a complete observability stack unless the selected scenario explicitly and narrowly requires a small related change.
- Tests should be meaningful and runnable, but they should not encode the full implementation solution.
- If the task involves performance, provide a way to measure baseline behavior through endpoint timing, query count, EXPLAIN output, logs, or a focused test.
- If the task involves security or tenancy, provide seed data that makes the boundary issue observable without exposing sensitive setup details in README.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Python FastAPI, PostgreSQL, Docker, and testing development that includes:
- Python cache directories and compiled files
- virtual environments
- test and coverage artifacts
- local database data directories and generated PostgreSQL files
- log files
- IDE and editor files
- OS-specific files
- Docker volume folders or local runtime artifacts
- local secrets and `.env` files even though the generated project must not depend on them

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md MUST contain exactly the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected FastAPI + PostgreSQL scenario. Use concrete business context, not generic descriptions. The README must not contain database connection details, credentials, hostnames, ports, client-tool suggestions, setup commands, deployment commands, or `<DROPLET_IP>` placeholders.

### Task Overview
- Must contain 3-4 meaningful sentences.
- Must be written as prose, not a bullet list.
- Must describe the business scenario, current state, and why the problem matters.
- Must clearly communicate that the application exists and has a focused issue to investigate, without revealing the specific fix.
- NEVER empty.
- NO bold time-budget callouts.

### Objectives
- Must contain 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: 'Improve query performance.'
- GOOD: 'The product search endpoint returns results in 4-6 seconds under normal load; after your changes it should respond in under 500ms for typical query patterns.'

### Helpful Tips
- Must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, SQL statement, index type, method name, or algorithm that solves the task.
- Tips may point candidates toward observing API behavior, reading existing layers, comparing response contracts, measuring database behavior, and thinking about edge cases.

### How to Verify
- Must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, response shape, latency observation, log line, query count, transaction behavior, or API error response.
- Include both functional correctness and maintainability/performance/security verification where relevant to the selected scenario.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of the README.md file:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, `python`, `uvicorn`, or similar commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, SQL statements, index names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database connection details, hostnames, ports, usernames, passwords, or client-tool suggestions
- `<DROPLET_IP>` placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this specific API", or "add this exact index"

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely reflects the selected FastAPI and PostgreSQL task domain.",
  "title": "A human-readable display name in '<action verb> <subject>' format, between 50 and 80 characters, and different from the repository name.",
  "question": "A complete candidate-facing task description that explains the business scenario, the exact current implementation state, the required changes, the constraints, and the expected behavior without revealing the solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no setup commands or database connection details.",
    ".gitignore": "A comprehensive ignore file for Python, FastAPI, PostgreSQL local data, Docker artifacts, logs, virtual environments, IDE files, and test outputs.",
    "docker-compose.yml": "A Docker Compose file with no version field and no environment variable references that starts localhost-bound PostgreSQL and FastAPI services with hardcoded deterministic configuration.",
    "Dockerfile": "A functional Dockerfile for the FastAPI application that uses /root/task as the working directory and starts the ASGI app consistently with docker-compose.",
    "run.sh": "A readiness script that runs from /root/task, starts services with docker compose up -d, waits for PostgreSQL and FastAPI readiness, and prints clear validation logs.",
    "init_database.sql": "A PostgreSQL initialization script that creates realistic schema and seed data, includes the intentional current-state database issue, and avoids solution-revealing comments or optimized fixes.",
    "requirements.txt": "A Python dependency manifest containing the FastAPI, ASGI, PostgreSQL, validation, and test dependencies required by the generated project.",
    "app/main.py": "The FastAPI application entry point that wires routers, exception handlers, middleware where relevant, and health/readiness routes without containing the final task solution.",
    "app/api/routes.py": "Domain route definitions that expose the selected API workflow and delegate to service layers while preserving the intentional current-state issue.",
    "app/schemas.py": "Pydantic request and response models that represent the current API contract and include only the validation behavior present in the starter state.",
    "app/dependencies.py": "Dependency functions for database sessions, request context, authentication stubs, or other cross-cutting concerns needed by the scenario.",
    "app/services.py": "Business logic for the selected domain with the current flawed or incomplete behavior that the candidate must diagnose and improve.",
    "app/repositories.py": "Database access code using async PostgreSQL interaction, SQLAlchemy async or an equivalent approach, with the intentional query or transaction issue preserved.",
    "app/db.py": "Database engine, session, connection, or pool setup that is functional and consistent with the hardcoded PostgreSQL configuration.",
    "app/core/errors.py": "Application error classes and response mapping helpers where relevant to the scenario, implemented enough for the current state but not solving the task.",
    "tests/test_domain_flow.py": "Focused tests or test scaffolding that exercise the API behavior and help candidates verify the expected outcome without embedding the implementation answer.",
    "sample_queries.sql": "Optional diagnostic SQL for performance-oriented tasks that helps observe baseline behavior without including the final optimized SQL."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the intended FastAPI, PostgreSQL, transaction, validation, security, testing, and performance changes needed to resolve the task.",
  "definitions": "An object mapping 4-6 relevant FastAPI and PostgreSQL terms from the generated task to concise candidate-friendly definitions.",
  "hints": "A single line nudging investigation toward the relevant API layer, database behavior, request contract, transaction boundary, or measurement signal without revealing the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable API correctness, database performance or consistency, preserved response contracts, and maintainable production-grade code.",
  "pre_requisites": "A concise bullet list of tools and knowledge needed, covering Docker, Python FastAPI, PostgreSQL, async API/database integration, and test execution without padding or sub-lists.",
  "short_overview": "Exactly 3 plain sentences: first state what is being built or maintained, second state what the candidate must do, and third state what success looks like, with no label prefixes."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only.
2. The generated task must use one selected real-world scenario as its business domain and technical inspiration.
3. The project must be FULLY FUNCTIONAL at startup; candidates must fix the intended application/database issue, not the environment.
4. The generated infrastructure MUST include docker-compose.yml, Dockerfile, run.sh, and init_database.sql.
5. Do NOT include kill.sh.
6. docker-compose.yml MUST NOT include a version field.
7. docker-compose.yml MUST NOT include environment variables or .env file references.
8. PostgreSQL host port exposure MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
9. All code and scripts must reference /root/task as the base directory.
10. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order.
11. README.md must not include setup commands, database access details, direct solutions, exact SQL fixes, specific APIs that reveal the answer, or `<DROPLET_IP>` placeholders.
12. Starter code must perfectly match the described current implementation and must not contain the final solution.
13. Do not include TODO comments or comments that reveal the fix.
14. The task must be completable within {minutes_range} minutes by an ADVANCED Python FastAPI and PostgreSQL candidate.
15. The task must require meaningful work in both FastAPI application code and PostgreSQL behavior.
16. The required output JSON schema values must be descriptive sentences, not placeholder arrays or hollow examples.
17. short_overview must be exactly 3 plain sentences with no label prefixes.
"""

PROMPT_REGISTRY = {
    "PostgreSQL (ADVANCED), Python - FastAPI (ADVANCED)": [
        PROMPT_POSTGRESQL_FASTAPI_ADVANCED_CONTEXT,
        PROMPT_POSTGRESQL_FASTAPI_ADVANCED_INPUT_AND_ASK,
        PROMPT_POSTGRESQL_FASTAPI_ADVANCED_INSTRUCTIONS,
    ]
}