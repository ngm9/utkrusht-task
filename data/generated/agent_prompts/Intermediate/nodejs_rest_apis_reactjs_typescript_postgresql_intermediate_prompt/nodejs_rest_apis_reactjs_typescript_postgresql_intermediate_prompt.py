# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how intermediate full-stack engineers deliver typed React + TypeScript user experiences, Node.js REST APIs, and PostgreSQL-backed features end to end?
"""

PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a full-stack Node.js, REST API, React, TypeScript, and PostgreSQL assessment task.

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
- The task MUST be a full-stack DESIGN/BUILD task, not a repair-only task: the candidate builds or reworks a feature end to end across a React + TypeScript frontend, a Node.js REST API backend, and a PostgreSQL database
- The backend MUST use TypeScript with Express or NestJS and route -> service -> repository layering
- The frontend MUST use React with TypeScript and share typed contracts with the backend
- The database MUST come from the task's own docker-compose.yml PostgreSQL service and init/migration SQL file

Based on the above inputs, briefly state:
1. Which scenario you selected and why
2. What the full-stack task will involve

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""

PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Node.js, REST APIs, React, TypeScript, and PostgreSQL, you are given a list of real world scenarios and proficiency levels for full-stack product engineering.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to design and build a production-realistic full-stack feature end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL full-stack TypeScript monorepo that is already scaffolded with:
- A React + TypeScript frontend with realistic feature folders, typed API clients, shared contracts, components, hooks, and stateful UI flows
- A Node.js TypeScript REST API using Express or NestJS with route -> service -> repository layering
- A PostgreSQL database deployed by the task's own docker-compose.yml and initialized from an init/migration SQL file
- A substantial, realistic schema and seed dataset that the candidate must investigate before completing the feature
- Existing conventions for error handling, configuration, logging, API response shapes, and shared types

The candidate's responsibility is to rework and extend the existing application so the feature achieves the intended product outcomes. This is a DESIGN/BUILD task, not a repair task: the task should leave room for the candidate to make architectural decisions across the frontend, backend, API contract, and PostgreSQL query/design surface without being handed a checklist solution.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or rework a full-stack feature end to end across React + TypeScript, Node.js REST APIs, and PostgreSQL.
- **CRITICAL**: This MUST be a DESIGN/BUILD task, not a repair task. Do not frame the task as finding one seeded bug or fixing one broken function. The candidate should improve the system to a clear product standard.
- **CRITICAL — Task Depth Over Breadth**: The task should present 1-2 major implementation areas that are architecturally meaningful, not a shopping list of disconnected fixes.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the selected real-world scenario.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The candidate should demonstrate best practices, proper design decisions, maintainable layering, type-safe contracts, thoughtful REST API design, practical PostgreSQL reasoning, and polished React data flow.
- The complexity of the task must align with INTERMEDIATE proficiency level (3-5 years experience across Node.js, REST APIs, React, TypeScript, and PostgreSQL).
- **CRITICAL TIME BUDGET**: The task must fit within {minutes_range} minutes total. The starter must be realistic but bounded so an intermediate developer with AI assistance can complete the core work within the timebox.
- **CRITICAL — Intermediate Codebase Volume**: The starter codebase MUST be substantial and realistic, NOT a toy snippet. Require multiple interacting modules and files in a real monorepo layout, with non-trivial existing logic the candidate must read and reason about before changing. The relevant logic must NOT be obvious from the first file opened.
- **CRITICAL — Multi-layer Backend**: The backend MUST be Node.js REST API code written in TypeScript using Express or NestJS. It must have route/controller, service, repository, validation, shared contract, and configuration layers.
- **CRITICAL — React + TypeScript Frontend**: The frontend MUST use React with TypeScript, functional components, hooks, realistic feature folders, typed API consumption, loading/error states, and shared typed contracts with the backend.
- **CRITICAL — PostgreSQL Role**: PostgreSQL must be meaningfully exercised by the scenario through schema design, queries, filtering, sorting, pagination, transaction boundaries, money precision, lifecycle statuses, or data integrity. Do not include PostgreSQL as decorative infrastructure.
- **CRITICAL — Production Realism Required**:
  - Schema must include several related tables with real foreign keys, indexes, constraints, status lifecycle columns, audit columns, and soft-delete or archived flags. Never use one flat table.
  - Seed enough rows, from hundreds to a few thousand, so the answer cannot be seen by eyeballing the seed file. The candidate must query, aggregate, inspect records, or reason about execution plans.
  - Include production data mess: NULLs in nullable columns, near-duplicates, soft-deleted rows, unicode and apostrophes in names, timestamps crossing day and timezone boundaries, money as exact decimals, out-of-order or back-dated sequences, and boundary-case rows.
  - Keep the seeded world internally consistent: foreign keys resolve, totals reconcile, and lifecycle statuses follow legal transitions.
  - Generate larger seed content programmatically in SQL using generate_series or equivalent SQL constructs rather than hand-writing thousands of literal rows.
- The task should focus on intermediate-level practical areas such as:
  - Resource-oriented REST API modeling and consistent response contracts
  - Pagination, filtering, sorting, and bounded result sets for operational screens
  - Meaningful status codes, validation, and error payloads
  - Type-safe contracts shared between frontend and backend
  - Route -> service -> repository separation and maintainable TypeScript modules
  - PostgreSQL schema/query reasoning with indexes, joins, timestamp handling, money precision, and soft-delete filtering
  - React state management, custom hooks, API integration, loading states, error states, and responsive UI behavior
  - Structured logging, request correlation, or health/readiness checks where natural to the scenario
- Do NOT require advanced-only PostgreSQL administration topics such as high-availability design, physical replication orchestration, PITR implementation, or deep storage internals as primary task skills.
- Do NOT require microservices, Kafka, Redis, GraphQL, Kubernetes, cloud deployment, or advanced distributed-system architecture unless the selected scenario absolutely demands it; this prompt is for a single full-stack monorepo with PostgreSQL.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Node.js documentation, React documentation, PostgreSQL documentation, TypeScript documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Candidates may use AI assistance, but the generated task must still require genuine engineering judgment across API design, frontend architecture, TypeScript typing, and database reasoning.
- The final submission should show the candidate's own ability to choose appropriate trade-offs, keep the feature maintainable, and validate observable behavior.

## Code Generation Instructions
Based on the real-world scenarios provided, create a full-stack Node.js + React + TypeScript + PostgreSQL task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed
- Tests practical end-to-end feature delivery across frontend, REST API, service/repository backend layers, and PostgreSQL
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list to ensure variety
- Uses a TypeScript monorepo structure with root package scripts and workspaces
- Uses React with TypeScript for the frontend, preferably Vite or another lightweight local React setup
- Uses Express or NestJS for the backend REST API in TypeScript
- Shares typed contracts between frontend and backend through a concrete shared package or folder
- Provides meaningful starter code across multiple modules but leaves the core feature design and implementation for the candidate
- Includes realistic frontend screens and backend endpoints that partially establish the domain but do not solve the target feature
- Includes tests or invariant checks only if they help candidates self-check without turning the design/build task into a narrow hidden-answer exercise
- Keeps all dependencies installable through npm without system-installing Node.js, because the Node runtime is already available in the E2B template
- Uses pinned dependency versions in package.json files
- Avoids comments that reveal the solution, direct TODO markers, placeholder comments, or comments such as "add pagination here", "implement validation here", or "create index here"

## Infrastructure Requirements
- MUST include a docker-compose.yml file with a PostgreSQL service used by this task.
- MUST include an init/migration SQL file that creates the schema AND seeds the database.
- MUST include run.sh as a readiness gate that installs dependencies, starts PostgreSQL, waits for health, verifies the starter builds, and exits 0 on the UNSOLVED starter.
- MUST include kill.sh because this full-stack task directive requires a cleanup artifact.
- The database comes from the task's own docker-compose.yml, never from the runtime template.
- The infrastructure must be reliable in a small sandbox and complete within the run.sh budget. Realistic SHAPE and MESS matter, not raw volume.
- Do not include MongoDB, MySQL, Redis, Kafka, queues, search services, or unrelated datastores unless the selected scenario explicitly requires them. For this prompt, PostgreSQL is the required datastore.
- The compose file should normally include only PostgreSQL. The React frontend and Node.js backend should build locally through npm scripts unless the generated scenario truly needs app containers.
- No kill.sh should be relied on by the readiness gate. run.sh must not call kill.sh.

### Docker-compose Instructions
- docker-compose.yml MUST define a PostgreSQL service using an official PostgreSQL image such as postgres:16-alpine.
- **MUST NOT include any version specification** in docker-compose.yml.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`.
- The PostgreSQL service MUST set the standard initialization environment variables inline in `environment:`:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- The init SQL, healthcheck, and backend connection string must use the same user and database.
- Forbid `.env` files and `${{VAR}}` host indirection in docker-compose.yml. Inline service environment values are required because the PostgreSQL image will not initialize without them.
- Mount the SQL initialization file into `/docker-entrypoint-initdb.d/` so PostgreSQL initializes the schema and seed data automatically.
- Use a named volume for PostgreSQL data.
- Include a PostgreSQL healthcheck that uses `pg_isready` with the same user and database declared in the inline environment variables.
- Use hardcoded local development values suitable for the sandbox; do not use remote hosts, droplet IPs, or external managed databases.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else becomes bash's positional parameters and is silently dropped. Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.
- If app containers are not used, do not include Dockerfiles and do not add backend/frontend services to compose.

### init_database.sql Instructions
- init_database.sql MUST create a comprehensive PostgreSQL schema for the selected business scenario and seed it.
- Include several related tables, normally 5-8 tables, with real relationships:
  - Primary keys, foreign keys, unique constraints where natural, check constraints, and useful baseline indexes
  - Status or lifecycle columns with valid state transitions represented in the data
  - Audit columns such as created_at and updated_at
  - Soft-delete or archived flags such as deleted_at, archived_at, or is_archived
  - Exact numeric columns for money, never floating point
  - Timestamptz columns where dates and timezones matter
- Seed hundreds to a few thousand rows using SQL generation techniques such as generate_series, CTEs, arrays, deterministic functions, or controlled random-like distributions.
- Include messy but internally consistent production-style data:
  - NULLs in nullable fields
  - Near-duplicate people or organizations differing in one field
  - Unicode names and apostrophes
  - Soft-deleted or archived rows
  - Back-dated and out-of-order sequences
  - Timestamps crossing local day boundaries and timezone-sensitive reporting windows
  - Boundary records around important statuses, dates, or amounts
- The seed data must be coherent: foreign keys resolve, totals reconcile, and status histories make sense.
- Do NOT implement the candidate's solution in the SQL file.
- Do NOT include SQL comments that reveal indexes, query rewrites, API rules, UI behavior, or design choices the candidate should discover.
- The init file must execute quickly in the sandbox. Do not seed millions of rows.

### Run.sh Instructions
- run.sh MUST use `#!/usr/bin/env bash` and must `cd /root/task` before running project commands.
- run.sh's FIRST project step MUST install dependencies using the Node runtime's manifest install command, normally `npm ci`.
- run.sh MUST start PostgreSQL using `docker compose up -d`.
- run.sh MUST wait for PostgreSQL health using a loop with `docker compose exec` or `docker compose ps` plus a real readiness probe.
- run.sh MUST build or typecheck the starter locally using npm scripts such as `npm run build`, `npm run typecheck`, or both.
- run.sh is a READINESS/self-check, NOT the grader. It MUST NOT run the grader test suite that is designed to fail until the candidate solves the task.
- run.sh MUST exit 0 on the UNSOLVED starter when dependencies install, PostgreSQL starts and seeds successfully, and the frontend/backend starter compiles.
- If the generated project ships a visible test suite where failing tests are the candidate deliverable, run.sh may execute the test runner only as a deployability probe and MUST treat "tests ran but failed" as deployable. For npm-based tests, capture the exit code and exit 0 for normal pass/fail outcomes, but exit non-zero for dependency, collection, configuration, or runner errors.
- run.sh MUST print clear progress messages and useful diagnostics when PostgreSQL fails to start or the starter fails to build.
- run.sh MUST NOT apt-get install Node.js or any primary runtime already provided by the template.
- run.sh MUST NOT depend on remote services, droplet IPs, or external databases.

### kill.sh Instructions
- kill.sh MUST use `#!/usr/bin/env bash` and `set -e` at the top.
- kill.sh MUST `cd /root/task` first when the directory exists.
- kill.sh MUST stop and remove the task's Docker Compose resources with volumes and orphans.
- kill.sh MUST remove containers, volumes, images, and dangling Docker resources related to the task while ignoring errors with `|| true` where appropriate.
- kill.sh MUST be idempotent and safe to run multiple times.
- kill.sh MUST print a progress message before every major step.
- kill.sh SHOULD include cleanup commands such as:
  - `docker compose down --volumes --remove-orphans || true`
  - `docker ps -q | xargs -r docker stop || true`
  - `docker ps -aq | xargs -r docker rm -f || true`
  - `docker volume prune -f || true`
  - `docker image prune -a -f || true`
  - `docker system prune -a --volumes -f || true`
- kill.sh MUST delete `/root/task` as the final cleanup step and print a final completion message.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Standard Node.js, React, TypeScript, PostgreSQL, Docker, and IDE exclusions)
  - docker-compose.yml (PostgreSQL service only unless app containers are truly required; no version key; localhost-only port binding)
  - run.sh (Readiness gate that installs npm dependencies, starts PostgreSQL, waits for health, builds/typechecks the starter, and exits 0 on the unsolved starter)
  - kill.sh (Cleanup script required for this task directive)
  - init_database.sql (Schema creation and realistic seeded PostgreSQL data)
  - package.json (Root workspace manifest with pinned scripts and dependencies)
  - package-lock.json (Lockfile consistent with the generated package manifests, if feasible)
  - tsconfig.base.json (Shared TypeScript configuration)
  - apps/api/package.json (Backend workspace manifest)
  - apps/api/tsconfig.json (Backend TypeScript configuration)
  - apps/api/src/server.ts (Backend entry point)
  - apps/api/src/app.ts (Express or NestJS application setup)
  - apps/api/src/routes/healthRoutes.ts (Health/readiness route wiring)
  - apps/api/src/routes/featureRoutes.ts (Concrete REST route file for the selected domain)
  - apps/api/src/controllers/featureController.ts (Controller layer for the selected domain)
  - apps/api/src/services/featureService.ts (Service layer for domain behavior)
  - apps/api/src/repositories/featureRepository.ts (Repository layer for PostgreSQL access)
  - apps/api/src/db/pool.ts (PostgreSQL connection pool configuration)
  - apps/api/src/middleware/errorHandler.ts (Centralized error handling)
  - apps/api/src/middleware/requestContext.ts (Request context or correlation handling if natural)
  - apps/api/src/config.ts (Local configuration with sane defaults)
  - apps/web/package.json (Frontend workspace manifest)
  - apps/web/tsconfig.json (Frontend TypeScript configuration)
  - apps/web/vite.config.ts (Vite configuration for React)
  - apps/web/index.html (React HTML entry point)
  - apps/web/src/main.tsx (React application entry point)
  - apps/web/src/App.tsx (Application shell)
  - apps/web/src/features/feature/FeaturePage.tsx (Concrete feature page for the selected domain)
  - apps/web/src/features/feature/components/FeatureFilters.tsx (Concrete feature component)
  - apps/web/src/features/feature/components/FeatureResults.tsx (Concrete feature component)
  - apps/web/src/features/feature/hooks/useFeatureData.ts (Concrete data hook)
  - apps/web/src/api/client.ts (Typed API client foundation)
  - apps/web/src/styles.css (Basic responsive styling)
  - packages/contracts/package.json (Shared contracts workspace manifest)
  - packages/contracts/src/index.ts (Shared TypeScript request and response contracts)
  - tests or invariants files with concrete paths if the generated task includes candidate-visible checks

## Code file requirements
- Use realistic file paths and names that follow TypeScript monorepo conventions.
- Generate a complete, buildable project rooted at /root/task.
- The generated code files should provide a realistic starter application that compiles and can connect to the seeded PostgreSQL database.
- The generated code should NOT contain the completed feature solution.
- Include a root package.json with npm workspaces for apps/api, apps/web, and packages/contracts.
- Include TypeScript strict mode and modern TypeScript patterns across frontend, backend, and shared contracts.
- Backend code must show route -> controller -> service -> repository layering.
- Repository code must use parameterized PostgreSQL queries and a connection pool.
- Frontend code must use React functional components, hooks, typed API calls, and realistic loading/error/empty states where appropriate.
- Shared contracts must be meaningful and used by both frontend and backend, but must not encode the full solution rules so tightly that the candidate is merely filling blanks.
- Include multiple existing backend routes or frontend components where natural, so the candidate must understand conventions before extending the feature.
- Include practical local configuration with safe defaults and no dependence on external secret files for the database.
- If API documentation is included, keep it lightweight and do not turn documentation tooling into the focus of the task.
- **CRITICAL**: The generated starter must be incomplete by design but not broken by syntax errors, missing imports, missing manifests, or invalid TypeScript configuration.
- **CRITICAL**: The relevant business logic must not all live in one obvious file. The candidate should need to reason across contracts, UI, API layers, repository queries, and schema.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- DO NOT include comments like "Add pagination here", "Create the index here", "Use this hook", "Implement validation here", or "This is where the solution goes".
- DO NOT include code snippets in README.md that reveal the answer.
- Do not include Dockerfiles unless the generated docker-compose.yml actually runs app containers. For the default shape, compose runs PostgreSQL only and no Dockerfile is required.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for Node.js, React, TypeScript, PostgreSQL, and Docker local development:
- node_modules/
- dist/, build/, coverage/, .nyc_output/
- Vite and frontend build artifacts
- TypeScript incremental build files
- environment files such as .env and .env.local
- logs and debug files such as *.log
- PostgreSQL data directories and local Docker volume folders
- IDE/editor files such as .idea/, .vscode/, *.swp, *.swo
- OS-specific files such as .DS_Store and Thumbs.db
- temporary files, cache directories, and other common generated artifacts

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

A plain unmarked text line with the section name is INVALID and counts as a missing section. Do NOT add extra README sections such as Service Access, Database Access, Setup, Architecture, Database Schema Overview, Performance Issues, Guidance, or Tools.

The README.md file content MUST be fully populated with meaningful, specific content directly relevant to the selected business scenario. Use concrete business context, not generic descriptions.

### Task Overview
- This section MUST contain 3-4 meaningful sentences.
- Use no bullet list in this section.
- Describe the business scenario, current state, and why the feature matters.
- NEVER generate empty content.
- Do not include bold time-budget callouts.
- Do not include setup commands, database connection details, droplet IP placeholders, hostnames, ports, usernames, passwords, or client-tool suggestions.

### Objectives
- Because this is an INTERMEDIATE DESIGN/BUILD task, Objectives MUST use the DESIGN/BUILD branch.
- Include 3-4 bullets max; fewer, tighter is better.
- Each objective is ONE SHORT PLAIN SENTENCE, roughly 10-15 words, naming the outcome the system must achieve.
- Use plain goal statements, not stakeholder framing.
- Imperative mood is correct here.
- One concern per bullet; split a bullet that bundles two separable concerns.
- State the desired outcomes, not mechanisms, APIs, files, functions, SQL clauses, indexes, React patterns, or implementation locations.
- Good design/build objective examples:
  - "Build an ordering workspace that remains responsive as operational data grows."
  - "Make filtered results reliable across status, date, and customer edge cases."
  - "Keep frontend and backend behavior aligned through shared product contracts."
  - "Preserve data correctness when business records span multiple related entities."
- Bad objective examples:
  - "Add cursor pagination to the admin orders endpoint."
  - "Create a composite index on placed_at and id."
  - "Use React Query to cache list responses."
  - "Update apps/api/src/repositories/orderRepository.ts to filter deleted rows."
- The test for objective quality is specificity, not mood. If a bullet could be pasted into the codebase as the change description, it is too specific.

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery and must NOT name the specific API, library, function, pattern, data structure, SQL index, SQL clause, React hook, package, file, method, class, or algorithm that solves the task.
- Keep tips at the level of architecture, data shape, user experience, consistency, and observability.

### How to Verify
- Include 3-5 bullets max.
- Because this is a DESIGN/BUILD task, How to Verify bullets must name an EXPERIMENT TO RUN and where to look, and MUST NOT state what the correct result is.
- Each bullet should use the pattern: make this change or perform this interaction, and look at what the application, API response, database records, logs, or UI actually shows.
- Put one probe per Objective, in the same order where practical.
- Do NOT state the pass condition if that pass condition gives away a rule the candidate is meant to derive.
- At most ONE bullet may reference the task environment directly.
- Good design/build probes:
  - "Change the visible filters, refresh the workspace, and compare the records that remain visible."
  - "Use a dataset boundary case, exercise the workflow, and inspect the API response shape."
  - "Create or update a representative record, and look at both the screen and persisted data."
  - "Run the project checks, and review any failures alongside the behavior you observed."
- Bad design/build probes:
  - "The endpoint should return exactly 25 rows ordered by placed_at and id."
  - "Soft-deleted records must be excluded from every query."
  - "The UI should use cursor pagination and never request more than one page."
  - "The database should use a composite partial index for this query."

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Do NOT include the following in README.md:
- Setup commands such as `npm install`, `npm ci`, `npm run dev`, `npm test`, `docker compose up`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, SQL clauses, index definitions, React hooks, TypeScript utility types, or data-structure names that reveal the solution
- Code snippets that give away the answer
- File paths, directory paths, function names, method names, class names, variable names, table-specific implementation instructions, or other direct code references that reveal where to change the system
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", or "add this index"
- Database-connection details, database usernames, passwords, hostnames, ports, remote-host placeholders, or `<DROPLET_IP>` placeholders
- Separate README sections named Setup, Service Access, Database Access, Database Schema Overview, Performance Issues, Guidance, Architecture, or NOT TO INCLUDE

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "A kebab-case GitHub repository name under 50 characters that describes the full-stack product feature without exposing the solution mechanism.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on the product feature being built.",
  "question": "A full candidate-facing task description written as one scenario paragraph plus a direct imperative ask. It must stay at outcome altitude: describe who the candidate is, what business system exists, that it needs to be reworked into a trustworthy full-stack feature, and the product outcomes it must achieve. Do not include bullet lists, file names, file paths, function names, method names, table names as implementation targets, endpoint names that reveal the solution, SQL clauses, index hints, React hook names, library names, or direct solution statements.",
  "code_files": {{
    "README.md": "Candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading such as ## Task Overview, ## Objectives, ## Helpful Tips, and ## How to Verify — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "Comprehensive Node.js, React, TypeScript, PostgreSQL, Docker, IDE, log, cache, coverage, and environment-file exclusions.",
    "docker-compose.yml": "Docker Compose file for the PostgreSQL service with no version key, localhost-only 127.0.0.1:5432:5432 port binding, inline POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB values, a healthcheck using the same database and user, a named volume, and init SQL mounted into /docker-entrypoint-initdb.d/.",
    "run.sh": "Readiness script that cd's to /root/task, installs npm dependencies first, starts PostgreSQL with docker compose up -d, waits for database health, builds or typechecks the unsolved starter, prints diagnostics on failure, and exits 0 when the starter is deployable.",
    "kill.sh": "Idempotent cleanup script that removes the task's Docker Compose resources, containers, volumes, images, dangling Docker resources, and finally deletes /root/task while ignoring already-removed resources.",
    "init_database.sql": "PostgreSQL initialization script that creates several related production-realistic tables with constraints, indexes, lifecycle and audit columns, then programmatically seeds hundreds to a few thousand internally consistent messy rows.",
    "package.json": "Root npm workspace manifest with pinned scripts for installing, building, typechecking, and running the frontend and backend workspaces.",
    "package-lock.json": "npm lockfile consistent with the generated workspace dependency manifests when feasible for the generated project.",
    "tsconfig.base.json": "Shared strict TypeScript compiler configuration used by the backend, frontend, and shared contract package.",
    "apps/api/package.json": "Backend workspace manifest with pinned TypeScript, Node.js REST API, PostgreSQL, validation, logging, and development dependencies appropriate to the selected framework.",
    "apps/api/tsconfig.json": "Backend TypeScript configuration extending the shared base configuration.",
    "apps/api/src/server.ts": "Backend process entry point that starts the REST API using local configuration and logs readiness without containing the task solution.",
    "apps/api/src/app.ts": "Express or NestJS application setup wiring middleware, routes, and centralized errors without embedding the completed feature logic.",
    "apps/api/src/routes/healthRoutes.ts": "Concrete health route module used by readiness checks.",
    "apps/api/src/routes/featureRoutes.ts": "Concrete REST route module for the selected domain that delegates to controller logic while leaving the core feature design incomplete.",
    "apps/api/src/controllers/featureController.ts": "Controller layer for request parsing and response shaping in the selected domain without revealing the final implementation approach.",
    "apps/api/src/services/featureService.ts": "Service layer containing partial domain orchestration that the candidate must complete through design decisions.",
    "apps/api/src/repositories/featureRepository.ts": "Repository layer for parameterized PostgreSQL access with starter queries and structure but without the final feature behavior.",
    "apps/api/src/db/pool.ts": "PostgreSQL pool setup using local development defaults aligned with docker-compose.yml.",
    "apps/api/src/middleware/errorHandler.ts": "Centralized error handling foundation with meaningful response envelopes.",
    "apps/api/src/middleware/requestContext.ts": "Request context or correlation middleware foundation when natural to the generated scenario.",
    "apps/api/src/config.ts": "Backend configuration module with sane local defaults and no dependency on a remote database.",
    "apps/web/package.json": "Frontend workspace manifest with pinned React, TypeScript, Vite, and UI development dependencies.",
    "apps/web/tsconfig.json": "Frontend TypeScript configuration extending the shared base configuration.",
    "apps/web/vite.config.ts": "Vite configuration for the React TypeScript frontend.",
    "apps/web/index.html": "HTML entry point for the React frontend.",
    "apps/web/src/main.tsx": "React application bootstrap using modern React rendering.",
    "apps/web/src/App.tsx": "Application shell that routes or displays the selected domain feature without containing the full solution.",
    "apps/web/src/features/feature/FeaturePage.tsx": "Concrete feature page for the selected domain with realistic composition and incomplete product behavior.",
    "apps/web/src/features/feature/components/FeatureFilters.tsx": "Concrete filter or control component appropriate to the scenario.",
    "apps/web/src/features/feature/components/FeatureResults.tsx": "Concrete results or detail component appropriate to the scenario.",
    "apps/web/src/features/feature/hooks/useFeatureData.ts": "Typed data-loading hook foundation that integrates with the API client without revealing the final data-flow solution.",
    "apps/web/src/api/client.ts": "Typed API client foundation used by React components to call the backend.",
    "apps/web/src/styles.css": "Basic responsive styling for the generated React application.",
    "packages/contracts/package.json": "Shared contracts workspace manifest used by both frontend and backend.",
    "packages/contracts/src/index.ts": "Shared TypeScript request and response contracts that support alignment between frontend and backend without over-specifying the solution."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the expected full-stack architecture, REST contract choices, TypeScript type-sharing strategy, PostgreSQL query/schema considerations, React data-flow decisions, and validation approach. This may name likely mechanisms because it is not candidate-facing.",
  "definitions": "An object of concise term-to-definition pairs for relevant full-stack concepts such as REST resource, response contract, repository layer, shared contract, connection pool, soft delete, pagination, and exact decimal money.",
  "hints": "A single-line candidate-facing hint that nudges investigation toward aligning product outcomes across UI, API contracts, and persisted data without revealing specific files, APIs, SQL clauses, indexes, or implementation mechanisms.",
  "outcomes": "Expected results after completion in 2-3 lines using simple English, focusing on observable product behavior, maintainable full-stack structure, reliable data handling, and one line that explicitly says: Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, with declarative capability phrases such as TypeScript and Node.js proficiency, comfort building React applications, familiarity with REST API design, and understanding of PostgreSQL schema/query basics. Do not include imperative setup, install, run, configure, or verify steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first, what the system is and who it serves today; second, opening with 'This rework needs to ...' or 'This calls for ...' and describing outcomes without mechanisms; third, what separates a strong submission and closing on whether the design reasoning is sound. No backticks, file paths, mechanism names, candidate-directed language, or enumeration of seeded defects."
}}


## READINESS GATE — run.sh MUST EXIT 0 ON THE UNSOLVED STARTER
This is the single most common reason a generated task is thrown away. Two failure
modes, both of which you must design out:
1. IMPORTED BUT NOT DECLARED. Every module referenced anywhere - application code and
   especially build-config files such as vite.config.ts, jest.config.ts, tsconfig
   "types", and any plugin import - MUST appear in the dependency manifest that
   installs it. A real run failed with `vite.config.ts(2,19): error TS2307: Cannot find
   module '@vitejs/plugin-react'` because package.json never declared it. Cross-check
   EVERY import, plugin and @types/* reference against package.json / pom.xml /
   requirements.txt before emitting.
2. A STRICT TYPECHECK THE STARTER CANNOT PASS. If run.sh runs `npm run typecheck`,
   `tsc --noEmit` or a full build while the starter still contains candidate stubs,
   the compiler fails and run.sh exits non-zero ON THE STARTER - which the gate
   rejects. Make every stub TYPE-COMPLETE BUT BEHAVIOURALLY INCOMPLETE: correct
   signature and return type, returning an empty collection / placeholder or throwing
   a "not implemented" error, so it COMPILES while the behaviour remains unimplemented.
   If a strict check still cannot pass on the starter, run.sh must not run that check -
   prefer install + an import/load smoke + service health.
run.sh must exit 0 on the UNSOLVED starter with NO candidate stub filled in. State this
requirement explicitly in the generated task's run.sh description.

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences outside JSON values.
2. **Task shape is infra** — code_files must include docker-compose.yml, init_database.sql, run.sh, and kill.sh.
3. **docker-compose.yml must NOT have a `version:` field**.
4. **PostgreSQL port binding must be localhost-only** using `127.0.0.1:5432:5432`.
5. **PostgreSQL inline initialization environment variables are required**: POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB. Do not use `.env` or `${{VAR}}` indirection for compose.
6. **run.sh must install npm dependencies first**, start PostgreSQL, wait for health, build or typecheck the starter, and exit 0 on the unsolved starter.
7. **run.sh must not run the failing grader suite as a pass/fail gate**.
8. **kill.sh is required by this task directive** and must be idempotent.
9. **README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify**, in that order, each as a markdown heading.
10. **Apply the DESIGN/BUILD README branch**: goal-statement Objectives, probe-style How to Verify, and no pass-condition leakage.
11. **question and short_overview must stay at outcome altitude** and must not enumerate the implementation mechanisms.
12. **Intermediate realism is mandatory**: multiple modules, route -> service -> repository backend layering, React TypeScript frontend, shared typed contracts, and a production-realistic PostgreSQL schema and seed dataset.
13. **Do not include solution-revealing comments, TODO comments, direct implementation hints, file-path hints in candidate-facing prose, or code snippets that give away the answer**.
14. **The starter must be buildable and deployable inside /root/task on the utkrusht-node-base style Node runtime without system-installing Node.js**.
"""

PROMPT_REGISTRY = {
    "NodeJs (INTERMEDIATE), PostgreSQL (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_CONTEXT,
        PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_FULLSTACK_NODE_REACT_POSTGRES_INTERMEDIATE_INSTRUCTIONS,
    ],
}