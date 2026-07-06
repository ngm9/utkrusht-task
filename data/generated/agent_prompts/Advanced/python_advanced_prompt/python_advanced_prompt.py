# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_PYTHON_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python assessment task.

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
- For this Python ADVANCED backend task, prefer a production-style API performance, database interaction, concurrency, refactoring, reliability, or maintainability problem that requires senior-level Python judgment rather than rote syntax recall
- The task must include PostgreSQL infrastructure only when the selected scenario needs persisted relational data and SQLAlchemy-backed performance work

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python, FastAPI, SQLAlchemy, and PostgreSQL-backed services, you are given a list of real world scenarios and proficiency levels for Python.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL Python backend application that contains realistic performance, scalability, maintainability, and database interaction issues requiring advanced-level Python skills to diagnose, refactor, and optimize.

The task should assess whether the candidate can work like an advanced Python engineer: reason about production bottlenecks, profile and improve inefficient ORM code, apply appropriate asynchronous or concurrent patterns where relevant, improve secure and maintainable application design, and preserve API compatibility while making measurable improvements.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY POPULATED and FULLY FUNCTIONAL Python backend project with PostgreSQL infrastructure and realistic seeded data. The application must run successfully before the candidate changes anything, but it should exhibit deliberate advanced-level issues such as slow API responses, inefficient SQLAlchemy usage, excessive database round trips, weak transaction boundaries, poor pagination behavior, blocking work in request paths, or fragile error handling.

The project must include:
- A complete Python FastAPI backend service with implemented routes, service layer code, SQLAlchemy models, database session handling, and tests or verification scripts
- A PostgreSQL datastore seeded with enough realistic data to make the performance issue observable without requiring external services
- A docker-compose.yml and run.sh that bring up the application and PostgreSQL database from /root/task
- A Dockerfile for the Python application container
- A FULLY FUNCTIONAL baseline where all existing endpoints respond, but one or more paths are measurably inefficient or architecturally weak
- Clear current behavior in the task description without directly naming the exact implementation changes needed
- Advanced-level work appropriate for a senior Python backend engineer, not a basic feature implementation task

The candidate's primary responsibility is to improve the Python application and its database interactions while keeping the observable API contract stable. The expected work may include profiling, SQLAlchemy query refactoring, indexing decisions, response serialization improvements, concurrency-aware design, transaction management, focused testing, and maintainability improvements. The task completion should require advanced Python proficiency and practical production judgment, while remaining achievable within {minutes_range} minutes.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, descriptive, under 50 characters, and use kebab-case
- Task title MUST be human-readable, different from the name, and use an action-oriented format such as "Optimize Admin Order Search Performance"
- Task must present a realistic Python backend work item based on ONE of the provided real-world scenarios
- **CRITICAL**: The provided application must be FULLY FUNCTIONAL and runnable before candidate changes begin; the candidate must not spend time repairing broken infrastructure
- **CRITICAL**: The starter project must perfectly implement the current inefficient or fragile state described in the question, no more and no less
- **CRITICAL**: The task must require advanced Python judgment: profiling, refactoring, ORM optimization, database interaction design, scalable architecture, secure coding practices, and maintainable code structure
- **CRITICAL**: The task must stay within Python ADVANCED scope: complex scalable applications, performance optimization, decorators or context managers where useful, concurrency only if naturally relevant, advanced OOP design, profiling/debugging, pytest or unittest, SQLAlchemy ORM optimization, REST APIs, containerized services, and secure maintainable implementation
- **CRITICAL**: Do NOT make the candidate implement unrelated infrastructure, Kubernetes, cloud deployment, CI/CD pipelines, machine learning models, OpenCV workflows, or broad distributed-system redesigns unless the selected scenario directly and realistically requires a small bounded part of that work
- **CRITICAL**: This is not a trivia task and not a syntax puzzle. It should require applied reasoning, debugging approach, implementation judgment, maintainability awareness, and measurable outcomes
- **CRITICAL**: For a PostgreSQL and SQLAlchemy scenario, include enough seeded rows and realistic relationships to make query behavior measurable, such as orders and customers for an e-commerce admin API
- The current implementation should be inefficient but not catastrophically broken: it should return correct responses, but too slowly or with too many database statements under realistic seeded data
- The required changes should ask for outcomes such as lower latency, fewer database round trips, stable pagination, improved error boundaries, or reduced serialization overhead without revealing the exact API, library method, or query pattern that solves it
- The task must include measurable success criteria, such as endpoint latency under seeded data, maximum SQL statements per request, stable response shape, or test pass requirements
- The question must NOT include hints about specific fixes. The hints will be provided only in the "hints" field
- The task must be completable within {minutes_range} minutes by an advanced Python candidate with production backend experience
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate enough starter code that gives the candidate a clear starting point for investigating the issue without giving away the solution
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE
- DO NOT include TODO comments, placeholder comments, or comments that reveal the expected optimization
- Ensure that all questions and scenarios adhere to Python 3.11+ best practices, PEP 8 style, secure coding practices, and maintainable project structure
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, FastAPI documentation, SQLAlchemy documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a realistic advanced Python backend problem, rather than testing rote memorization
- Tasks should involve multi-layered engineering challenges that require understanding of Python application design, database interactions, profiling, scalability, and maintainability
- Candidates may use AI to help analyze symptoms and compare possible approaches, but the final implementation must demonstrate their own judgment, testing discipline, and production-quality reasoning

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python backend optimization and refactoring task that:
- Draws inspiration from the input scenarios to determine the business context and technical requirements
- Uses the provided real-world scenario as the basis for this task - do not invent a different domain
- Matches the complexity level appropriate for Python ADVANCED proficiency, keeping in mind that AI assistance is allowed but should not diminish the need for advanced design, debugging, and optimization skills
- Tests practical advanced-level Python work involving FastAPI, SQLAlchemy, PostgreSQL, profiling, refactoring, maintainable architecture, and secure coding practices
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- Provide a complete, working Python FastAPI application with an existing inefficient implementation that candidates must improve
- Prefer a scenario like an e-commerce admin order search endpoint where current SQLAlchemy code filters large tables, performs excessive ORM loading, and serializes results inefficiently
- Ensure the baseline project has enough realistic seeded data to reproduce slow behavior without external network dependencies
- Ensure the candidate can validate improvements using tests, a benchmark script, application logs, response timing, or SQL statement counting
- Ensure the application's existing response shape is backward compatible and must remain unchanged after optimization
- Ensure the task focuses primarily on advanced Python and SQLAlchemy application work, not on Docker optimization
- Do not require candidates to install system packages in run.sh; the Python runtime, FastAPI, SQLAlchemy, and common libraries are pre-installed by the E2B template

## Infrastructure Requirements
- MUST include a complete, fully functional Python FastAPI application
- MUST include PostgreSQL infrastructure because the scenario exercises persisted relational data and SQLAlchemy query performance
- MUST include docker-compose.yml for the FastAPI application service and PostgreSQL datastore
- MUST include init_database.sql that creates and populates realistic PostgreSQL tables needed for the task
- MUST include run.sh that starts the datastore and application using docker compose, waits for readiness, and validates that the project is runnable
- MUST include Dockerfile for the Python application container
- MUST NOT include kill.sh; E2B sandboxes are destroyed as a whole, so container cleanup is automatic
- MUST NOT include extra datastores such as Redis, MySQL, MongoDB, or Qdrant unless the selected real-world scenario explicitly needs them. For the default e-commerce order scenario, use PostgreSQL only
- The infrastructure must be functional, deterministic, and self-contained under /root/task

### Docker-compose Instructions
  - Include a PostgreSQL service and a Python FastAPI application service
  - The PostgreSQL service must expose its port only to localhost using `127.0.0.1:5432:5432`
  - The FastAPI service must expose its port only to localhost using `127.0.0.1:8000:8000`
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore or application service exposed to the host
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT reference .env files or use `${{VARIABLE}}` substitution syntax** — all configuration values must be hardcoded literals
  - **MUST use `image: postgres:16`** directly for the postgres service — do NOT build a custom postgres Dockerfile or use a custom entrypoint
  - **MUST set PostgreSQL startup environment variables as hardcoded literal values** in the `environment:` block of the postgres service: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` must all be present with hardcoded string values (e.g. `POSTGRES_USER: postgres`, `POSTGRES_PASSWORD: postgres`, `POSTGRES_DB: orders_db`). These environment variables are REQUIRED by the postgres:16 image to initialize; omitting them causes the container to exit immediately.
  - **MUST NOT use a custom postgres Dockerfile** — there must be no `docker/postgres/Dockerfile` or custom postgres image build in the project
  - **MUST NOT override the postgres entrypoint or command** — use the default `postgres:16` entrypoint so `/docker-entrypoint-initdb.d/` scripts run automatically
  - Use service names that are stable and easy to understand, such as `postgres` and `api`
  - Mount `init_database.sql` into `/docker-entrypoint-initdb.d/init_database.sql` using a relative path (`./init_database.sql`) so the seed SQL runs automatically on first startup
  - Include health checks or readiness behavior sufficient for run.sh to wait until services are usable
  - Do not add unrelated services, external queues, search engines, or caches unless the selected scenario explicitly requires them
  - Keep compose configuration production-like enough for a realistic assessment but do not make Docker optimization the focus of the task

### init_database.sql Instructions
  - Create all PostgreSQL tables, indexes, constraints, and seed data needed for the selected business scenario
  - For an e-commerce admin API scenario, include realistic tables such as customers and orders with relational keys and enough rows to make inefficient ORM behavior visible
  - Seed data must be deterministic and large enough to expose the intended performance issue within the time limit
  - Include only baseline schema objects that support the current implementation and task; do not pre-solve the optimization if the candidate is expected to add or adjust an index
  - If the task requires the candidate to reason about indexing, the baseline schema should intentionally omit or under-specify the performance-critical index while remaining valid and functional
  - Use realistic timestamps, statuses, amounts, and customer attributes where relevant
  - The SQL must run cleanly on container startup with no syntax errors
  - Do not include passwords, secrets, or external connection details in the README

### Run.sh Instructions
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d` and ensures deployment is complete
  + The script must run from /root/task and reference /root/task paths explicitly where needed
  + The script must not run apt-get install, pip install, npm install, or any runtime dependency installation commands
  + The script must wait for PostgreSQL readiness before validating the API
  + The script must wait for the FastAPI service readiness before completing
  + The script must run basic smoke checks against localhost-only endpoints, such as health and the target API route
  + The script may run a lightweight benchmark or verification command to display baseline latency or query-count symptoms without revealing the fix
  + The script must use robust error handling and print clear logs for each startup and validation step
  + The script must be idempotent enough to rerun during candidate investigation
  + The script must not include cleanup behavior; no kill.sh is needed

### Dockerfile Instructions
  - Include a Dockerfile for the Python FastAPI application container ONLY — do NOT create a postgres Dockerfile
  - The Dockerfile must be functional and appropriate for running the app in the assessment environment
  - The Dockerfile should not be the primary source of the candidate challenge
  - Do not deliberately create bloated or broken Docker behavior unless the selected scenario explicitly asks for container optimization
  - Do not require the candidate to fix Dockerfile issues before investigating the Python task
  - Use Python 3.11+ compatible behavior and a standard application startup command
  - Do not include secrets, environment variable references, or external service credentials
  - Ensure all paths align with /root/task and the docker-compose.yml build context

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Functional PostgreSQL and FastAPI service orchestration; uses `image: postgres:16` with hardcoded POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB environment vars; no custom postgres build)
  - init_database.sql (PostgreSQL schema and deterministic seed data for the selected scenario; must run cleanly on postgres:16 with zero errors)
  - Dockerfile (Functional Python application container definition — for the FastAPI app only, NOT for postgres)
  - run.sh (Script to start infrastructure, wait for readiness, and validate the baseline)
  - pyproject.toml or requirements.txt (Python dependency manifest suitable for the generated project)
  - .gitignore (Python, test, IDE, and local artifact exclusions)
  - app/main.py (FastAPI application entry point)
  - app/api/routes.py or equivalent router files (API endpoints for the scenario)
  - app/db/session.py or equivalent database session setup
  - app/db/models.py or equivalent SQLAlchemy model definitions
  - app/services/*.py (Service layer containing the current inefficient or fragile implementation)
  - app/schemas/*.py or equivalent response/request schema definitions
  - tests/*.py or scripts/*.py as needed to verify behavior and performance symptoms
  - Additional Python files as needed following a clean FastAPI project structure

## Code file requirements
- Multiple files will be generated following a production-like FastAPI project structure
- Python code must be valid, executable, and compatible with Python 3.11+
- The application must run successfully with the provided infrastructure before candidate modifications
- **CRITICAL**: The starter code must perfectly implement the current inefficient or fragile state described in the task
- **CRITICAL**: The code must not include the core optimization or refactor the candidate is expected to implement
- **CRITICAL**: The candidate should not need to repair syntax errors, import errors, missing modules, broken Docker startup, or missing seed data
- The target endpoint or workflow must be clearly identifiable from the task description and README without exposing the exact solution
- Include realistic observability for the candidate to diagnose the problem, such as logs, a benchmark script, query count helper, or tests that expose the symptom
- Include tests or verification scripts that can pass once the candidate completes the work and that meaningfully check behavior, backward compatibility, and measurable improvement
- Do not make tests brittle by relying on exact machine timing alone; combine latency checks with deterministic indicators such as query count, response shape, or bounded result size
- Keep application structure maintainable, with routes, services, models, database setup, and schemas separated appropriately
- Use SQLAlchemy ORM patterns in the baseline and ensure the inefficient behavior is realistic, such as repeated lazy loads, inefficient filtering, excessive serialization work, or missing database support for common filters
- Do not include TODO comments, placeholder comments, or comments that reveal the expected solution
- Do not include hardcoded secrets or .env file usage
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Python FastAPI, SQLAlchemy, PostgreSQL, Docker, and test development that includes:
- Python cache directories (__pycache__/, *.pyc, *.pyo, *.pyd)
- Virtual environments (venv/, env/, .venv/)
- IDE files (.idea/, .vscode/, *.swp, .python-version)
- Testing artifacts (.pytest_cache/, .coverage, htmlcov/)
- Log files (*.log, logs/)
- Local database dumps or generated data files if any
- Docker volumes and temporary local runtime artifacts
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for Python/FastAPI/Docker development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order and no others:
  1. Task Overview
  2. Objectives
  3. Helpful Tips
  4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected advanced Python backend scenario.
All sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific Python, FastAPI, SQLAlchemy, and PostgreSQL task scenario being generated.
Use concrete business context explaining why the backend behavior matters to users, operators, cost, reliability, or product workflows.
Do NOT include database connection details such as host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences and no bullet list
- Describe the business scenario, current state, and why the problem matters
- NEVER generate empty content - always provide substantial business context
- Mention that the backend is already functional but has measurable performance, scalability, or reliability issues
- Do not include bold time-budget callouts
- Do not directly tell candidates what to implement or name the exact fix

### Objectives
- Objectives must contain 4-6 bullets max
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix. A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like. It does NOT name the API, library, pattern, or algorithm that solves it. Objectives describe the 'what' and 'why', never the 'how'
- Each bullet should be a full, context-rich sentence — not a two-word label
- BAD: "Improve query performance."
- GOOD: "The product search endpoint returns results in 4-6 seconds under normal load; after your changes it should respond in under 500ms for typical query patterns."
- Objectives should focus on measurable outcomes such as response latency, bounded query counts, stable pagination, backward-compatible response shape, graceful error handling, or maintainable code boundaries
- Do not name the specific SQLAlchemy method, loader strategy, database index structure, API call, pattern, or algorithm that solves the task

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max
- Provide practical guidance without revealing specific implementations
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze"
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task
- Good tips may nudge candidates to compare current behavior to expected behavior, inspect database activity, measure before and after changes, preserve response contracts, or reason about where work belongs in the application
- Do not include code snippets, commands that reveal the solution, exact method names, or implementation recipes

### How to Verify
- How to Verify must contain 4-6 bullets max
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write
- Each bullet is a check the candidate can run or observe, such as test output, response shape, latency observation, log line, query-count reading, or memory reading
- Include verification of functional correctness and backward compatibility
- Include verification of measurable improvement without relying only on an exact wall-clock threshold that may be machine-dependent
- Do not include step-by-step setup instructions

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
- Setup commands such as `pip install`, `docker compose up`, `pytest`, or similar tool commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Database connection details including host, port, username, password, or client-tool suggestions
- `<DROPLET_IP>` placeholders
- Separate sections named Database Schema Overview, Database Access, Current State & Baseline Metrics, Application Access, Performance Issues, or NOT TO INCLUDE

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A kebab-case GitHub repository name under 50 characters that clearly identifies the advanced Python backend optimization scenario without using spaces or title case.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from name, and focused on the main advanced Python backend improvement.",
  "question": "A complete candidate-facing task description that explains the business scenario, the current functional but inefficient implementation, the required observable outcomes, constraints, and success criteria without revealing the specific implementation technique.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify sections with meaningful non-revealing guidance for the generated scenario.",
    ".gitignore": "A comprehensive ignore file for Python, FastAPI, SQLAlchemy, test artifacts, IDE files, logs, Docker local artifacts, and operating-system files.",
    "docker-compose.yml": "A functional Docker Compose configuration with FastAPI and PostgreSQL services; no version key; uses `image: postgres:16` (not a custom postgres build); includes hardcoded POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB in the postgres `environment:` block; mounts init_database.sql via `./init_database.sql:/docker-entrypoint-initdb.d/init_database.sql:ro`; localhost-only port bindings using `127.0.0.1:<port>:<port>`.",
    "init_database.sql": "A deterministic PostgreSQL initialization script that creates the scenario schema and seeded data needed to reproduce the baseline behavior without pre-solving the candidate's optimization work.",
    "Dockerfile": "A functional Python application container definition that starts the FastAPI app reliably and does not distract from the Python and database optimization task.",
    "run.sh": "A robust startup and validation script that runs from /root/task, starts docker compose in detached mode, waits for PostgreSQL and the API to become ready, and performs baseline smoke checks.",
    "pyproject.toml or requirements.txt": "A Python dependency manifest containing the packages required by the generated FastAPI, SQLAlchemy, PostgreSQL, and testing project without unnecessary installation instructions.",
    "app/main.py": "The FastAPI application entry point with router registration, health behavior, and application setup needed for the task.",
    "app/api/routes.py": "The API route definitions for the selected scenario, including the target endpoint whose current behavior is correct but inefficient.",
    "app/db/session.py": "Database engine and session management code using hardcoded local container configuration values and safe request-scoped behavior.",
    "app/db/models.py": "SQLAlchemy ORM model definitions matching the PostgreSQL schema and relationships used by the task.",
    "app/schemas/order.py": "Response or request schema definitions that preserve the existing API contract expected by the candidate and tests.",
    "app/services/orders.py": "The service layer containing the current functional but inefficient implementation that the candidate must diagnose and improve.",
    "tests/test_orders.py": "A pytest-based verification suite or equivalent checks that validate response compatibility, bounded result behavior, and performance-related symptoms after candidate changes.",
    "scripts/benchmark_orders.py": "An optional lightweight benchmark or diagnostic script that reports observable baseline behavior without revealing the solution.",
    "additional Python files as needed": "Any supporting modules required for clean project organization, deterministic data access, logging, or verification while keeping the core challenge focused."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected advanced Python refactor, database-interaction improvement, profiling or measurement strategy, compatibility preservation, and verification approach without requiring one exact code layout.",
  "definitions": {{
    "term_1": "definition of term_1 relevant to this task",
    "term_2": "definition of term_2 relevant to this task"
  }},
  "hints": "A single line nudging candidates to measure the current request path and compare database activity with response behavior, without naming the specific optimization, query method, index, or implementation pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable backend improvements such as reduced endpoint latency, fewer database round trips, stable pagination, unchanged JSON shape, and maintainable Python code. Use simple english.",
  "pre_requisites": "Exactly 2-3 concise bullets where each bullet covers one item only: Python/FastAPI runtime knowledge, local Docker project readiness, and SQLAlchemy/PostgreSQL performance awareness if relevant.",
  "short_overview": "Exactly 3 plain sentences: first sentence states what is being built or improved, second sentence states what the candidate must do, and third sentence states what success looks like. Do not use label prefixes such as Business problem:, Technical focus:, Expected outcome:, or any other Label: form."
}}

## CRITICAL REMINDERS
1. **Environment must be fully working** — The project must run perfectly with the provided run.sh; zero syntax errors; zero missing files; the candidate does NOT fix infrastructure before starting the Python task.
2. **Starter code must be runnable** but must NOT contain the core optimization or refactor the candidate is expected to implement.
3. **Starter code must perfectly match the described Current Implementation** and exhibit the intended advanced-level performance or design issue.
4. **Task must be completable within {minutes_range} minutes** by a Python ADVANCED backend candidate.
5. **Focus on advanced Python concepts** appropriate to the competency scope: scalable services, performance optimization, SQLAlchemy/database interactions, profiling, debugging, maintainable architecture, secure coding practices, and production-quality refactoring.
6. **Use Python 3.11+**, FastAPI, SQLAlchemy, PostgreSQL, and standard style where applicable.
7. **Do not require Kubernetes, cloud deployment, CI/CD setup, unrelated machine learning work, or broad distributed-system redesigns** for this task.
8. **README.md MUST contain exactly four sections**: Task Overview, Objectives, Helpful Tips, and How to Verify, with no additional README headings.
9. **docker-compose.yml MUST NOT include any version specification** and MUST NOT reference .env files or use ${{VAR}} substitution. The postgres service MUST use `image: postgres:16` (no custom build) and MUST include hardcoded `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` in the `environment:` block — the container will not start without them.
10. **SECURITY-CRITICAL**: every exposed service port must be bound to localhost only using `127.0.0.1:<port>:<port>`.
11. **No kill.sh** should be generated because E2B sandboxes are destroyed as a whole.
12. **All code and scripts must reference /root/task as the base directory**.
13. **The REQUIRED OUTPUT JSON STRUCTURE must use exactly the canonical keys**: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, and short_overview.
14. **Every JSON schema field value must be a verbose one-sentence description** of what to fill in, not placeholder arrays or example objects.
15. **Select a real-world scenario from the provided list** and keep the generated task domain aligned with that scenario.
"""

PROMPT_REGISTRY = {
    "Python (ADVANCED)": [
        PROMPT_PYTHON_ADVANCED_CONTEXT,
        PROMPT_PYTHON_ADVANCED_INPUT_AND_ASK,
        PROMPT_PYTHON_ADVANCED_INSTRUCTIONS,
    ]
}