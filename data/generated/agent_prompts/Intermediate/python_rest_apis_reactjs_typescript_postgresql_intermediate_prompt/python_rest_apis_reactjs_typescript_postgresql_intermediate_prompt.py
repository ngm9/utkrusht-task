# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a full-stack Python REST API, React, TypeScript, and PostgreSQL assessment task.

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
- The generated task MUST be a full-stack DESIGN/BUILD task, not a repair task: the candidate builds or reworks a feature end to end across a React + TypeScript frontend, a Python REST API backend, and a PostgreSQL database
- The backend MUST use Python 3 with a REST API framework such as FastAPI or Flask and must follow router -> service -> repository layering
- The frontend MUST use React with TypeScript and share typed contracts with the backend
- The task MUST include PostgreSQL infrastructure owned by the repository through docker-compose.yml, a database init or migration file, and run.sh readiness automation

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the selected business domain, the full-stack technical context, and the end-to-end feature the candidate will build or rework)
2. What will the task look like? (Describe the Python REST API, React + TypeScript frontend, PostgreSQL schema/data, infrastructure artifacts, and how the deliverables align with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python REST APIs, React, TypeScript, and PostgreSQL, you are given a list of real world scenarios and proficiency levels for full-stack application development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an INTERMEDIATE LEVEL (3-5 years of experience).

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL local full-stack repository with:
- A Python 3 REST API backend using FastAPI or Flask with router -> service -> repository layering
- A React + TypeScript frontend with realistic component, hook, API-client, and shared-contract structure
- A PostgreSQL database that is already deployed through the task's own docker-compose.yml and initialized with realistic schema and data
- A run.sh readiness gate that installs dependencies, starts PostgreSQL, waits for database health, validates that the starter backend imports or builds, validates that the frontend builds, and exits 0 on the UNSOLVED starter
- A meaningful existing project layout that compiles and starts, while leaving the core end-to-end feature design and integration work for the candidate

The candidate's responsibility is to build or rework an end-to-end product feature across the UI, typed contracts, API layer, service layer, repository layer, and PostgreSQL-backed data workflow. The task must evaluate practical intermediate judgment around data flow, RESTful API design, TypeScript type safety, validation, error handling, SQL correctness, query efficiency, maintainability, and production-aware implementation.

## INSTRUCTIONS

### Nature of the Task
- Task must be a DESIGN/BUILD task, not a repair task. Nothing should be framed as a specific broken function, line, endpoint, component, query, or file that the candidate must fix.
- **CRITICAL**: The candidate should build or rework a coherent feature end to end across React + TypeScript, Python REST API, and PostgreSQL rather than completing a checklist of unrelated small changes.
- **CRITICAL — Task Depth Over Breadth**: The task should present 1-2 major implementation areas that require deep full-stack thinking, not 4-6 shallow requirements bundled together.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fill in obvious blanks.
- The question should be a real-world scenario that tests architectural thinking, data modeling judgment, API contract design, frontend integration, and database-aware implementation.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years experience), ensuring that no two questions generated are similar.
- **CRITICAL — Intermediate codebase volume**: The starter codebase MUST be substantial and realistic, not a toy snippet. Require multiple interacting modules and files in a real project layout, with non-trivial existing logic the candidate must read and reason about before changing. Changes should span more than one file.
- **CRITICAL — Relevant logic placement**: The relevant logic must NOT be obvious from the first file opened. The repository should require candidates to follow data flow through the frontend API client, shared contracts, backend router, service, repository, and schema.
- The task must stay inside the competency scope: Python applied development, REST API design and implementation, React + TypeScript practical data flow and type safety, and PostgreSQL applied schema/query work. Do not require expert-only database operations, cloud deployment, Kubernetes, advanced distributed systems, or obscure framework trivia.
- For INTERMEDIATE level, require candidates to make sound implementation decisions around RESTful resource modeling, pagination or filtering where appropriate, typed request and response contracts, frontend loading and error states, validation at trust boundaries, SQL joins or aggregations, indexing awareness, and maintainable layering.
- The task should be completable in {minutes_range} minutes by an intermediate hands-on engineer with AI and documentation access.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The question and README Objectives must be written together at outcome altitude. They must describe what the feature must achieve and why it matters, never the specific mechanisms, file paths, functions, query shape, index names, component names, or implementation approach.
- Since this is a DESIGN/BUILD task, README Objectives must use short plain goal statements, not stakeholder-framed repair symptoms.
- Ensure that all questions and scenarios adhere to modern best practices for Python 3, REST APIs, React 18+, TypeScript strict mode, and current PostgreSQL.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, FastAPI or Flask documentation, React documentation, TypeScript documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate full-stack proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches, make pragmatic trade-offs, and integrate frontend, backend, and database concerns cleanly.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a full-stack Python REST API, React, TypeScript, and PostgreSQL task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed.
- Tests practical full-stack skills that require architectural thinking, typed contract design, API implementation, SQL reasoning, and frontend integration.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Requires a Python 3 REST API backend using FastAPI or Flask, with clear router -> service -> repository layering.
- Requires a React + TypeScript frontend that consumes the REST API through a typed client and shares typed contracts with the backend through generated or mirrored contract files.
- Requires PostgreSQL schema and seed data that the candidate must investigate through application behavior, queries, aggregation, or query plans.
- Must be a DESIGN/BUILD task where the starter repository is runnable but intentionally leaves the core feature behavior incomplete or underdeveloped in an open-ended way.
- Must focus on 1-2 deep implementation areas, such as a production-grade admin workflow, operational dashboard, customer support workflow, commerce workflow, scheduling workflow, analytics workflow, or approval/review workflow.
- Must not ask for cloud deployment, Kubernetes, CI/CD, advanced HA replication, expert PostgreSQL internals tuning, or framework-specific trivia beyond the stated competency scopes.

Production realism is required:
- **DATA**: Include several related PostgreSQL tables with real foreign keys, indexes, constraints, status or enum columns, audit columns such as created_at and updated_at, and soft-delete or archived flags where the domain naturally calls for them.
- **DATA**: Seed enough rows that the answer cannot be seen by eyeballing the seed file. Hundreds to a few thousand rows is the right order of magnitude. The candidate must query, filter, aggregate, or inspect plans to understand the data.
- **DATA**: Include realistic messy production data: NULLs in nullable columns, near-duplicates that differ in one field, soft-deleted or archived rows that should not drive active results, unicode and apostrophes in names, timestamps crossing day and timezone boundaries, money as exact decimal types, out-of-order or back-dated sequences, and rows at important domain boundaries.
- **DATA**: Keep seeded data internally consistent. Foreign keys must resolve, totals must reconcile, statuses must follow a legal lifecycle, and candidate investigation must reveal a coherent business world rather than random noise.
- **DATA**: Generate large seed volume programmatically inside the init script using PostgreSQL functions, generate_series, arrays, or deterministic random-like expressions rather than hand-writing thousands of literal INSERT rows.
- **SETUP**: Include dependency manifests with pinned versions, environment/config handling with sane defaults, database init files, service healthchecks, and conventional project layout for the selected stack.
- **PRODUCTION CONCERNS**: Pick only concerns the chosen scenario genuinely exercises, such as pagination over large result sets, N+1 access patterns, transaction boundaries, idempotency, validation at the trust boundary, tenancy or authorization scoping, cache-control headers, timezone handling, money precision, index usage under volume, and migration safety.
- **HARD BOUND**: Everything must still install, build, seed, and start inside run.sh's budget on a small sandbox with 2 vCPU and about 2 GB RAM. Do not seed millions of rows, pull heavyweight images, or add dependencies that take minutes to install. Realistic shape and realistic mess matter more than raw volume.

## Infrastructure Requirements
- MUST include a complete PostgreSQL deployment using Docker Compose because this is an infra-shaped task.
- MUST include docker-compose.yml for the PostgreSQL service used by the scenario.
- MUST include a database initialization file that creates the schema and seeds the database.
- MUST include run.sh as a readiness gate that installs dependencies, starts PostgreSQL, waits for health, validates the starter builds or imports, and exits 0 on the UNSOLVED starter.
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic and no separate cleanup script is required.
- The database must come from the task's own docker-compose.yml, never from the template.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- Infrastructure must support a local developer opening the repository and running the provided readiness script without any manual database setup.
- The application services themselves should run locally from the source tree; do not require an app container or Dockerfile unless the selected scenario absolutely needs one. For this task shape, prefer no app Dockerfile.

### Docker-compose Instructions
- docker-compose.yml MUST define a PostgreSQL service only unless the selected scenario clearly needs another datastore from the real-world scenario. Do not invent extra caches, queues, brokers, or search services.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- Use the official PostgreSQL image with a modern lightweight tag such as postgres:16-alpine.
- PostgreSQL service MUST set initialization environment values inline under `environment:` using `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Forbid `.env` files and host variable indirection for Compose initialization. Do not use host interpolation such as external variable references for database user, password, or database name.
- The init SQL, healthcheck, and backend connection string must use the same PostgreSQL user and database.
- Mount the SQL initialization file into `/docker-entrypoint-initdb.d/` so PostgreSQL initializes the schema and seed data automatically on first container startup.
- Include a named volume for PostgreSQL data unless a bind mount is simpler for the generated task.
- Include a healthcheck that uses `pg_isready` with the same user and database configured in the service environment.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432` for PostgreSQL.
- Do not expose PostgreSQL on all interfaces.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST, `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:`. Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else becomes bash's positional parameters and is silently dropped. Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.

### init_database.sql Instructions
- Create a comprehensive PostgreSQL schema with several related tables, normally 5-8 tables for this intermediate full-stack task.
- Include realistic relationships between tables using primary keys, foreign keys, constraints, status lifecycles, and audit columns.
- Include indexes that a real starter application would already have, but do not fully solve every candidate-facing data access need in advance.
- Do not make a one-flat-table schema.
- Include status or enum-like constraints where the domain has lifecycle states.
- Include exact money fields using numeric types, never floating point.
- Include nullable columns where the domain naturally has incomplete information.
- Include soft-delete or archival columns where the domain needs historical records.
- Include timestamps spanning day and timezone boundaries.
- Include unicode names, apostrophes, near-duplicates, duplicate-looking records that differ in important fields, and boundary cases that force careful filtering or aggregation.
- Seed hundreds to a few thousand rows, generated programmatically in SQL using generate_series or equivalent deterministic expressions.
- Ensure the seeded data is internally consistent: foreign keys resolve, totals reconcile, statuses follow legal lifecycle transitions, and dates are plausible.
- Include enough data that candidates cannot eyeball the seed file to know the answer.
- Include comments that describe business context only. Do NOT include comments that reveal the implementation approach, query strategy, indexes to add, endpoint design, component strategy, or solution.

### Run.sh Instructions
- run.sh MUST be located at /root/task/run.sh and must use /root/task as the working directory.
- run.sh's first responsibility is dependency installation for this repository's own dependencies. The runtime template may provide Node and Python, but the task's third-party packages are not pre-installed.
- For the frontend, run the appropriate Node manifest install command such as `npm ci` from the frontend or root workspace path chosen by the generated project.
- For the backend, install Python dependencies using the task's manifest, such as `python -m pip install -q -r backend/requirements.txt`.
- PRIMARY INFRA RESPONSIBILITY: Start PostgreSQL using `docker compose up -d`.
- WAIT MECHANISM: Implement a reliable loop that waits for PostgreSQL health or readiness using `pg_isready` through docker compose exec or docker compose ps health status.
- VALIDATION: Verify PostgreSQL is accepting connections and that a small query against the configured database succeeds.
- STARTER BUILD VALIDATION: Validate the backend imports or starts far enough to prove the scaffold is deployable without requiring the candidate's unfinished feature to work.
- STARTER BUILD VALIDATION: Validate the React + TypeScript frontend builds successfully on the unsolved starter.
- run.sh is a READINESS and self-check script, NOT the grader.
- run.sh MUST NOT run the grader test suite or require feature-completion tests to pass.
- run.sh MUST exit 0 on the UNSOLVED starter when dependencies install, PostgreSQL starts, the schema seeds, backend scaffold imports or builds, and frontend compilation succeeds.
- run.sh MUST exit non-zero only when the project cannot install, boot, seed, import, or build.
- Include useful logs so a candidate can see which readiness step failed.
- Use `docker compose`, not legacy `docker-compose`, unless compatibility absolutely requires otherwise.
- Do not apt-get or system-install Node, Python, pip, or the primary runtime.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (PostgreSQL service configuration with localhost-only port binding and no version key)
  - db/init_database.sql (Complete schema creation and realistic seeded data)
  - run.sh (Readiness gate for dependency installation, PostgreSQL startup, health wait, backend validation, and frontend build)
  - .gitignore (Python, Node, React, PostgreSQL, Docker, IDE, OS, log, build, coverage, and environment exclusions)
  - package.json (Root or frontend Node manifest with pinned dependencies and build scripts)
  - package-lock.json (Lockfile if npm is used)
  - tsconfig.json (TypeScript strict-mode configuration)
  - vite.config.ts (React build configuration if Vite is used)
  - index.html (React application HTML entry)
  - src/main.tsx (React entry point)
  - src/App.tsx (Top-level React composition)
  - src/api/client.ts (Typed frontend API client scaffold)
  - src/api/contracts.ts (Shared or mirrored TypeScript contracts for API data)
  - src/features/workflow/WorkflowPage.tsx (Feature page scaffold with realistic UI composition)
  - src/features/workflow/components/WorkflowFilters.tsx (Feature UI component scaffold)
  - src/features/workflow/components/WorkflowResults.tsx (Feature UI component scaffold)
  - src/features/workflow/hooks/useWorkflowData.ts (Custom hook scaffold for data loading state)
  - src/styles.css (Minimal styling for a usable UI)
  - backend/requirements.txt (Pinned Python dependencies including the selected REST framework and PostgreSQL driver)
  - backend/app/main.py (Python application entry point)
  - backend/app/config.py (Configuration defaults for local PostgreSQL)
  - backend/app/db.py (Database connection/session setup)
  - backend/app/api/routes.py (REST router scaffold)
  - backend/app/services/workflow_service.py (Service layer scaffold)
  - backend/app/repositories/workflow_repository.py (Repository layer scaffold)
  - backend/app/schemas/workflow.py (Request and response schema scaffold)
  - backend/app/errors.py (Error handling scaffold)
  - backend/tests/test_contract_smoke.py (Visible smoke or contract tests that do not reveal the full solution)

## Code file requirements
- Use realistic file paths and names that follow conventions for a React + TypeScript frontend and Python REST API backend.
- Every file listed in the REQUIRED OUTPUT JSON STRUCTURE must be emitted with a real concrete path and a real extension.
- Do NOT emit placeholder-style filenames such as `additional_files_as_needed`, `starter_code_file_name`, `selected_stack_manifest_and_source`, `supporting_scripts`, or `local_config_files`.
- Code should follow modern best practices for Python, REST APIs, React, TypeScript, and PostgreSQL.
- Python code should follow PEP 8, use modules and packages cleanly, and keep router, service, and repository responsibilities separated.
- REST API code should use resource-oriented routes, meaningful status codes, validation at the trust boundary, consistent error responses, and maintainable request/response schemas.
- React code should use functional components with hooks and TypeScript types, and should include realistic state, loading, empty, and error UI scaffolding without handing over the solution.
- TypeScript should use strict mode and meaningful interfaces/types for shared contracts, API responses, UI state, and domain values.
- PostgreSQL access should use parameterized queries or an ORM/query layer in a way appropriate for intermediate Python engineers.
- The starter codebase must be runnable and buildable, but the end-to-end feature will require candidate implementation to become complete.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion in the 1-2 focused areas.
- Include existing routes, services, repositories, components, hooks, contracts, and schema files that the candidate needs to extend or connect.
- The core architectural decisions that the candidate needs to make MUST be left for the candidate to design.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- DO NOT include comments like "Add service here", "Implement pagination", "Add validation", "Use this query", "Add this index", "Wire this component", or "Implement loading states".
- DO NOT place the entire candidate task in one obvious missing function or one short file.
- Do not include syntax errors. The unsolved starter should build and run its readiness checks.
- Provide realistic pinned dependencies in package.json and backend/requirements.txt.
- Include visible smoke or contract tests only if they help the candidate understand the scaffold. These tests must not encode the complete solution or make run.sh fail on the unsolved starter.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore file that covers:
- Python bytecode, caches, virtual environments, pytest cache, coverage files, build artifacts, and local environment files
- Node modules, frontend build directories, Vite or bundler caches, coverage files, and package-manager logs
- PostgreSQL data directories, local Docker volumes, database dump files, and generated backup files
- Log files, temporary files, IDE/editor configuration, OS-specific files, and local secret files
- Include .env and .env.local exclusions while allowing safe example configuration files if the generated task includes them

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this exact order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four sections MUST be emitted as an actual markdown heading using the same heading level consistently, for example:
- `## Task Overview`
- `## Objectives`
- `## Helpful Tips`
- `## How to Verify`

A plain unmarked text line with the section name is INVALID and counts as a missing section.
Do NOT add Database Access, Database Schema Overview, Guidance, Performance Issues, Setup, Installation, Running Locally, Tools, or NOT TO INCLUDE as README sections.
The README must NOT contain droplet IP placeholders, remote-host placeholders, raw database credentials, database host/port details, or client-tool connection instructions.
Anywhere connection details legitimately appear outside the README, such as docker-compose healthchecks or run.sh readiness probes, the host must use localhost because the task runs inside an E2B sandbox.

### Task Overview
- Task Overview must be 3-4 meaningful sentences.
- No bullet list.
- It must describe the business scenario, current product or workflow state, and why the problem matters.
- It must clearly frame an end-to-end full-stack design/build feature, not a repair task.
- It must be concise, specific, and never empty.
- It must not include bold time-budget callouts.
- It must not mention exact file paths, functions, methods, SQL queries, index names, or implementation steps.

### Objectives
- For this INTERMEDIATE DESIGN/BUILD task, Objectives MUST be concise and open-ended plain goal statements.
- Use 3-4 bullets max; fewer and tighter is better.
- Each objective is ONE SHORT PLAIN SENTENCE, roughly 10-15 words, naming the outcome the system must achieve.
- Do not use stakeholder-framed repair symptoms for this design/build task.
- Imperative mood is acceptable for design/build objectives.
- One concern per bullet; split a bullet that bundles two separable concerns.
- Describe the outcome, never the mechanism.
- Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, query, index, or direct code reference.
- Do NOT describe current broken behaviour or use phrasing like "currently does X" or "after your changes".
- GOOD design/build objective style: "Build a workflow that makes high-priority customer issues easy to review."
- GOOD design/build objective style: "Keep displayed business totals consistent with the underlying operational records."
- BAD design/build objective style: "Add a partial index on orders where deleted_at is null."
- BAD design/build objective style: "Implement cursor pagination in backend/app/repositories/workflow_repository.py."
- The test is specificity: if a bullet could be pasted into the codebase as the change description, it is too specific.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery across product behavior, data shape, API boundaries, frontend state, and database-backed correctness.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, SQL construct, index strategy, component strategy, or algorithm that solves the task.
- Tips must not include setup commands or implementation steps.

### How to Verify
- How to Verify must be 3-5 bullets max.
- Because this is a DESIGN/BUILD task, How to Verify bullets must name experiments to run and where to look, and MUST NOT state the correct result.
- Use the pattern: make or exercise one product-level change, then inspect what the product, API response, database-backed data, or build output shows.
- One probe per Objective, in the same order as the Objectives where possible.
- Do NOT state pass conditions that reveal the hidden rule the candidate is meant to derive.
- At most ONE bullet may reference the task environment directly.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and where to observe it, not the specific implementation to write.
- Before emitting, read the Objectives and How to Verify together as a candidate would: between them they must still not give away any rule the candidate is meant to derive.
- Do not include setup commands such as npm install, pip install, docker compose up, or run.sh instructions.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section)**
Keep the following out of README.md:
- Setup commands such as npm install, pip install, docker compose up, pytest, npm test, or run.sh
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, SQL constructs, index names, table names, component names, hook names, data-structure names, or algorithm names that reveal the solution
- Code snippets that give away the answer
- Database connection details, host, port, username, password, client-tool suggestions, droplet IP placeholders, or remote-host placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this hook", "write this query", or "add this index"

## REQUIRED OUTPUT JSON STRUCTURE
The generated response MUST be valid JSON only. Do not include markdown fences, commentary, or explanations outside the JSON object.

{{
  "name": "A short kebab-case GitHub repository name under 50 characters that describes the full-stack task without using spaces or title case.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, clearly different from the kebab-case name.",
  "question": "A full candidate-facing task description written as one scenario paragraph plus a direct imperative ask at the same outcome altitude as the README Objectives; it must say who the candidate is, what product or workflow exists, why it is not yet trusted or complete, and what outcomes the rework must achieve without naming file paths, functions, methods, directories, SQL queries, tables, indexes, components, or direct solution mechanisms.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading such as ## Task Overview, ## Objectives, ## Helpful Tips, and ## How to Verify; a plain unmarked text line with the section name is invalid and counts as a missing section.",
    ".gitignore": "A comprehensive ignore file for Python, Node, React, PostgreSQL, Docker volumes, local environment files, logs, IDE files, coverage outputs, build outputs, and OS-specific artifacts.",
    "docker-compose.yml": "A Docker Compose file with no version key that starts the repository-owned PostgreSQL service using inline POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB values, localhost-only port binding, init SQL mounting, a named volume, and a healthcheck using the same database and user.",
    "db/init_database.sql": "A complete PostgreSQL initialization script that creates several related tables with constraints, relationships, lifecycle fields, audit columns, indexes, and programmatically generated realistic messy seed data in the hundreds to low thousands of rows.",
    "run.sh": "A readiness script rooted at /root/task that installs Node and Python project dependencies, starts PostgreSQL with docker compose up -d, waits for database health, verifies a simple database query, validates backend scaffold import or startup readiness, validates the frontend build, and exits 0 on the unsolved starter without running the grader tests.",
    "package.json": "A pinned Node manifest for the React and TypeScript frontend with scripts for building and optionally running frontend tests without requiring any global packages.",
    "package-lock.json": "An npm lockfile consistent with package.json so dependency installation is reproducible in the sandbox.",
    "tsconfig.json": "A strict TypeScript configuration suitable for a React application with modern module resolution and type checking enabled.",
    "vite.config.ts": "A Vite configuration file for building the React and TypeScript frontend in the local repository.",
    "index.html": "The frontend HTML entry point that mounts the React application without embedding solution-specific behavior.",
    "src/main.tsx": "The React entry file that renders the top-level application component using modern React APIs.",
    "src/App.tsx": "The top-level React composition file that wires the starter application shell without completing the candidate's core feature work.",
    "src/api/client.ts": "A typed frontend API client scaffold that centralizes HTTP calls and error handling seams without revealing the final API integration design.",
    "src/api/contracts.ts": "A TypeScript contract file containing shared or mirrored request and response shapes that support frontend-backend agreement without over-specifying the candidate's solution.",
    "src/features/workflow/WorkflowPage.tsx": "A feature page scaffold that composes existing UI pieces and leaves meaningful product behavior for the candidate to design and connect.",
    "src/features/workflow/components/WorkflowFilters.tsx": "A React component scaffold for user input or filtering controls that is realistic but does not encode the full solution.",
    "src/features/workflow/components/WorkflowResults.tsx": "A React component scaffold for presenting domain results with space for candidate-designed states and interactions.",
    "src/features/workflow/hooks/useWorkflowData.ts": "A custom hook scaffold for frontend data flow and state management that does not reveal the final loading, error, or transformation approach.",
    "src/styles.css": "A small stylesheet that makes the starter UI usable without becoming the focus of the assessment.",
    "backend/requirements.txt": "A pinned Python dependency manifest containing the selected REST framework, PostgreSQL driver or ORM/query helper, validation library if needed, test tools if included, and any small supporting packages.",
    "backend/app/main.py": "The Python REST application entry point that registers routes and error handling while leaving the feature's substantive behavior to layered modules.",
    "backend/app/config.py": "A configuration module with safe local defaults for the repository-owned PostgreSQL database and no secret leakage.",
    "backend/app/db.py": "A database connection or session module used by repositories to access PostgreSQL through parameterized operations or an appropriate query layer.",
    "backend/app/api/routes.py": "A REST router module that exposes resource-oriented endpoints for the scenario while delegating business decisions to the service layer.",
    "backend/app/services/workflow_service.py": "A service layer module that coordinates validation, business rules, and repository calls without embedding transport concerns.",
    "backend/app/repositories/workflow_repository.py": "A repository layer module that owns PostgreSQL data access seams and leaves candidate-level query and aggregation decisions open.",
    "backend/app/schemas/workflow.py": "A Python schema module for request and response validation that supports a typed API contract without fully prescribing the solution.",
    "backend/app/errors.py": "A backend error handling module that supports consistent API failures and leaves domain-specific refinement to the candidate.",
    "backend/tests/test_contract_smoke.py": "A visible smoke or contract test file that checks scaffold viability and broad integration expectations without revealing the complete feature solution."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the intended full-stack architecture, data flow, API contract decisions, database considerations, frontend state handling, validation, and production-quality trade-offs without requiring exact code.",
  "definitions": "An object of relevant term-to-definition pairs for concepts used in the task, such as REST resource, service layer, repository layer, typed contract, lifecycle status, soft delete, audit column, and exact decimal money, with concise candidate-friendly definitions.",
  "hints": "A single line nudging investigation across the UI, API boundary, service decisions, and database-backed data shape without revealing the implementation approach, specific files, SQL strategy, component design, or framework APIs.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable full-stack behavior, consistent business data, maintainable architecture, reliable API responses, and production-level clean code with best practices including naming, exception handling, logging, and observability.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3 proficiency, comfort with React and TypeScript, familiarity with REST API design, and understanding of PostgreSQL-backed application development; never include imperative setup, install, run, configure, or verify steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first what the system is and the situation today, second opening with 'This rework needs to' or 'This calls for' and stating outcomes without mechanisms, and third describing what separates a strong submission while closing on whether the design reasoning is sound."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be human-readable, in `<action verb> <subject>` format, 50-80 characters, and different from `name`.
4. **question** must be outcome-altitude prose for a design/build task and must not enumerate mechanisms, file paths, functions, methods, tables, queries, indexes, component names, or direct solution statements.
5. **code_files** must include README.md, .gitignore, docker-compose.yml, db/init_database.sql, run.sh, realistic frontend files, realistic backend files, dependency manifests, and all source files with concrete paths.
6. **Do NOT include kill.sh** because E2B sandbox cleanup is automatic.
7. **docker-compose.yml** must not include a version key and must bind PostgreSQL to `127.0.0.1:5432:5432`.
8. **docker-compose.yml** must use inline `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`; do not use `.env` files or host variable indirection for database initialization.
9. **run.sh** must install dependencies first, start PostgreSQL, wait for readiness, validate database access, validate backend readiness, validate frontend build, and exit 0 on the unsolved starter.
10. **run.sh** must not run the grader test suite or fail merely because the candidate has not implemented the feature yet.
11. **README.md** must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as a markdown heading.
12. **README.md** must not contain setup commands, database connection details, droplet IP placeholders, direct solutions, specific APIs, method names, file paths, implementation steps, or a NOT TO INCLUDE heading.
13. **Objectives** must follow the INTERMEDIATE DESIGN/BUILD rule: 3-4 short plain goal statements that name outcomes, not mechanisms.
14. **How to Verify** must use probe-style checks for design/build tasks and must not state the correct result when that result is the specification being assessed.
15. **Starter code** must be substantial, multi-module, buildable, and realistic, but must NOT contain the solution.
16. **Database seed data** must be realistic, messy, internally consistent, and large enough that the candidate must investigate rather than eyeball the init file.
17. **No comments in code** should reveal the solution or give hints.
18. **Task must be completable within the allocated time** for INTERMEDIATE proficiency while still feeling like real full-stack production work.
"""

PROMPT_REGISTRY = {
    "PostgreSQL (INTERMEDIATE), Python (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_CONTEXT,
        PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_FULLSTACK_PYTHON_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INSTRUCTIONS,
    ],
}