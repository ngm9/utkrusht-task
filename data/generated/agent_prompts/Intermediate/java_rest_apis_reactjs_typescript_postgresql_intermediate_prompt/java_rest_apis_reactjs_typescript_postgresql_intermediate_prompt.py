# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java, REST APIs, ReactJs, TypeScript, and PostgreSQL assessment task.

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
- The generated task MUST be a full-stack DESIGN/BUILD task, not a repair task: the candidate builds or reworks a feature end to end across a React + TypeScript frontend, a Java 21 Spring Boot REST API backend, and a PostgreSQL database
- The backend MUST follow Spring Boot style layering from controller to service to repository, and the frontend MUST consume typed contracts that remain aligned with the backend API contract
- The repository MUST be shaped for the utkrusht-java-fullstack runtime template and must include Docker-backed PostgreSQL from the task's own docker-compose.yml

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and feature the candidate will build or rework end to end)
2. What will the task look like? (Describe the Java Spring Boot REST API, React + TypeScript frontend, PostgreSQL schema/data, expected deliverables, and how it aligns with INTERMEDIATE full-stack proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java Spring Boot, REST API design, React, TypeScript, and PostgreSQL, you are given a list of real world scenarios and proficiency levels for full-stack product engineering.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to think, design, build, implement, debug, optimize, or in general solve a problem end to end at an INTERMEDIATE LEVEL (3-5 years of experience).
The task must be a full-stack DESIGN/BUILD task where the candidate builds or reworks a feature across a Java 21 Maven backend, a React + TypeScript frontend, and a PostgreSQL database, while preserving outcome-level task wording that does not give away the implementation.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL local full-stack repository with:
- A Java 21 Maven backend using Spring Boot style layering: controller, service, repository, DTO/model/configuration packages, and tests
- A React + TypeScript frontend with Vite, typed API contracts, realistic component organization, data-fetching utilities, and existing screens that the candidate must extend or rework
- A PostgreSQL database deployed from the task's own docker-compose.yml, initialized through an init/migration SQL file that creates schema and seeds data
- Several related PostgreSQL tables with real foreign keys, constraints, lifecycle/status columns, audit columns, soft-delete or archived flags, indexes where appropriate, and intentionally incomplete application-facing feature support
- Seeded data large and messy enough that the candidate must query, aggregate, inspect behavior, or reason through access patterns rather than eyeballing the seed file
- Build scripts and manifests that allow the starter project to install, build, seed, and start inside the sandbox budget on a small environment
- **CRITICAL**: The initial deployment MUST be successful and functional on the UNSOLVED starter; candidates explore first, then design and implement the feature
- **CRITICAL**: This is not a bug-hunt repair task. The candidate must make practical design choices for a feature that spans API contract, backend service behavior, database access, and frontend user experience

The candidate is expected to work like an intermediate full-stack engineer with 3-5 years of experience: independently deliver a medium-complexity product feature, design clear REST contracts, apply validation and error handling, write maintainable Java and TypeScript, use PostgreSQL efficiently, and keep the implementation aligned with established project patterns.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or rework one substantial feature end to end, not fix a seeded defect and not complete a checklist of unrelated small items.
- **CRITICAL — DESIGN/BUILD task shape**: The scenario should describe a product capability the business needs, not a broken behavior with a known root cause. Do not frame the task as "currently does X; after your changes Y." State desired outcomes at a high level and let the candidate determine the implementation.
- **CRITICAL — Task Depth Over Breadth**: The task should present 1-2 major implementation areas that require deep thinking across frontend, backend, and database layers, NOT 4-6 shallow additions bundled together.
- **CRITICAL**: The starter repository must be FULLY FUNCTIONAL and buildable before the candidate changes anything. It may not already implement the core feature, but it must compile, the frontend must build, the backend must build, and PostgreSQL must initialize successfully.
- **CRITICAL**: The backend must use Java 21 with Maven and Spring Boot style layering. Generated code should include realistic controller, service, repository, DTO, entity/model, configuration, and test structure.
- **CRITICAL**: The frontend must be React with TypeScript, use functional components and hooks, and consume typed contracts that are kept consistent with backend request/response models through an OpenAPI-style contract file, shared generated TypeScript contract, or explicitly mirrored typed contract module.
- **CRITICAL**: The PostgreSQL schema and seed data must feel production-realistic for intermediate hands-on engineers: several related tables, status lifecycles, audit columns, constraints, meaningful indexes, exact decimal money fields where relevant, timestamps crossing day/timezone boundaries, nullable columns, near-duplicates, unicode and apostrophes in names, soft-deleted or archived rows, and internally consistent relationships.
- **CRITICAL**: Seed enough rows, from hundreds to a few thousand, generated programmatically inside the init/migration SQL file using PostgreSQL set-generating functions or loops where volume calls for it. Do not hand-write thousands of INSERT statements.
- **CRITICAL**: Keep raw data volume modest enough for a 2 vCPU, 2 GB sandbox. Realistic shape and mess matter more than raw volume.
- The generated task should require changes across more than one file and more than one layer; the relevant logic must NOT be located in the first file opened.
- The backend and frontend starter code should be multi-module or clearly separated by module directories, with conventional project structure the candidate must read before changing.
- The task must stay inside intermediate scope: RESTful resource modeling, request/response DTOs, pagination/filtering/sorting when appropriate, validation, structured errors, logging, efficient repository access, transaction boundaries, typed frontend API consumption, state/data consistency, and user-facing failure behavior.
- The task may exercise one or two production concerns that fit the selected scenario, such as pagination over large result sets, N+1 access patterns, transaction boundaries, validation at the trust boundary, authorization scoping, timezone handling, money precision, index usage under volume, and migration safety.
- The task must not require expert-only PostgreSQL internals, advanced distributed systems, cloud deployment, advanced security architecture, or obscure framework trivia.
- The question scenario must be clear, historically plausible, and grounded in the selected real-world scenario.
- The question must NOT include hints, file paths, method names, class names, direct endpoint implementation details, or direct solution statements. The hints will be provided only in the "hints" field and must still remain non-revealing.
- The candidate should be able to complete the task within {minutes_range} minutes while still navigating a realistic codebase.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Java documentation, Spring Boot documentation, PostgreSQL documentation, React documentation, TypeScript documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization
- The complexity of the tasks should reflect intermediate full-stack proficiency while requiring genuine engineering and architectural skill that goes beyond simple copy-pasting from a generative AI
- Candidates may use AI to assist with boilerplate, syntax, or research, but the assessment should still reveal whether they can make sound design tradeoffs across API, database, and frontend boundaries

## Code Generation Instructions:
Based on the real-world scenarios provided, create a full-stack Java + REST APIs + React + TypeScript + PostgreSQL DESIGN/BUILD task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed
- Tests practical intermediate-level full-stack skills through a single coherent feature spanning database design/querying, Java Spring Boot service/API design, typed contracts, and React TypeScript integration
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- Use the selected real-world scenario as the basis for the task and do not invent a different domain
- Focus on a deep, layered Spring Boot + React challenge that requires the candidate to make real architectural decisions, not a breadth-first checklist
- Use Java 21 with Maven for the backend and React + TypeScript with Vite for the frontend
- Include realistic dependency manifests with pinned versions or version ranges appropriate to the stack
- Include source files that compile and demonstrate established project conventions but do not implement the core solution
- Include visible tests or smoke checks where useful, but do not make run.sh execute the grader suite if it is designed to fail before the candidate solves the task
- Ensure the starter code has no syntax errors, no missing imports, no missing manifest entries, and no intentionally failing readiness path
- Do not include TODO comments or solution-shaped comments in generated source files
- Do not overfit the feature to a single obvious code edit; the candidate must reason about API shape, data access, user state, and edge cases

## Infrastructure Requirements:
- MUST include docker-compose.yml with a PostgreSQL service owned by the task itself; the task must never depend on any database supplied by the runtime template
- MUST include an init/migration SQL file that creates the schema and seeds realistic data
- MUST include run.sh as a readiness gate that installs dependencies, starts PostgreSQL with docker compose, waits for database health, builds the Java backend, builds the React frontend, performs a light starter smoke check if appropriate, and exits 0 on the UNSOLVED starter
- MUST include kill.sh because this full-stack assessment explicitly requires a cleanup artifact; make it idempotent and safe to run repeatedly
- MUST include a backend Dockerfile if app container packaging is included in the generated repository; docker-compose may still contain only PostgreSQL if the app is built locally by run.sh
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **IMPORTANT**: The infrastructure setup is automated and MUST work on first deployment. Candidates should not need to manually create the database or run migrations before starting work
- run.sh is a READINESS/self-check, NOT the grader. It must not run the candidate-facing failing test suite as a pass/fail gate

### Docker-compose Instructions:
  - Include a PostgreSQL service using the official PostgreSQL image
  - The docker-compose.yml file MUST NOT include any version specification
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`
  - For PostgreSQL, REQUIRE the standard init environment variables inline in `environment:`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
  - The init SQL, healthcheck, and backend connection string must use the same user and database
  - Forbid `.env` files and `${{VAR}}` host indirection in docker-compose. Inline service environment values are required and allowed because the image will not initialize without them
  - Mount the SQL initialization file into `/docker-entrypoint-initdb.d/` so PostgreSQL creates and seeds the database automatically
  - Include a PostgreSQL healthcheck using `pg_isready` with the same database/user values declared in the service environment
  - Use a named volume or project-local data directory only if needed, and ensure kill.sh removes it
  - Do not include MongoDB, MySQL, Redis, Kafka, or any other datastore unless the selected real-world scenario explicitly requires it. For this task shape, PostgreSQL is the required datastore
  - **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else (flags, paths, `&&`, the rest of the pipeline) becomes bash's positional parameters and is silently dropped (e.g. `mkdir -p /a && tail -f /dev/null` breaks into `mkdir: missing operand`). Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`

### init_database.sql Instructions:
- Create a comprehensive PostgreSQL schema with several related tables appropriate to the selected scenario, usually 5-8 tables for intermediate full-stack work
- Include real relationships with foreign keys, unique constraints where appropriate, status lifecycle columns, audit columns such as created_at and updated_at, and soft-delete or archive fields where the domain calls for them
- Include indexes that represent realistic baseline production schema choices, but leave the candidate room to make data-access and query-design decisions where the task requires it
- Include data types that match the domain: `numeric(18,2)` or similarly exact decimal types for money, timestamptz for timeline data, enums or constrained text for lifecycles, nullable columns where the business process allows unknown values, and JSONB only when it is domain-appropriate
- Seed hundreds to a few thousand rows using PostgreSQL generation techniques such as `generate_series`, INSERT...SELECT, arrays, deterministic functions, or PL/pgSQL loops where helpful
- Include production-like mess: NULLs in nullable columns, near-duplicate names or records that differ by one field, soft-deleted/archived rows, unicode and apostrophes in names, timezone/day-boundary timestamps, back-dated or out-of-order sequences, and boundary-case rows for the feature's business rules
- Keep seeded data internally consistent: foreign keys resolve, totals reconcile, statuses follow a legal lifecycle, and audit trails do not contradict primary records
- Do not include comments that give away how to implement the feature, which indexes to add, which query to write, or which records matter most
- Ensure the init file runs in a fresh PostgreSQL container without manual intervention and completes quickly inside a small sandbox

### Run.sh Instructions:
  - FIRST step must install the task's own dependencies because third-party dependencies are not pre-installed: use Maven dependency/build steps for Java and `npm ci` for the frontend
  - Use `/root/task` as the working directory and reference all files from that base path
  - Start PostgreSQL using `docker compose up -d`
  - Wait for PostgreSQL readiness using a loop around `docker compose exec` or `pg_isready`, with clear timeout and error messages
  - Validate that the initialized database exists and contains expected starter tables without revealing any solution query
  - Build the Java backend using Maven in the backend module, such as `mvn -q -DskipTests package` or an equivalent compile/package command that succeeds on the unsolved starter
  - Build the React + TypeScript frontend using the package manifest, such as `npm ci` followed by `npm run build`
  - Optionally perform an import/application context smoke check that proves the starter loads, but do not run a grader suite designed to fail before the candidate solves the task
  - The readiness gate MUST exit 0 on the UNSOLVED starter if the scaffold installs, PostgreSQL starts, migrations run, and both projects build
  - The readiness gate MUST exit non-zero only for broken scaffold/deployability problems such as dependency install failure, database health failure, migration failure, or compilation/build failure
  - Print concise progress logs for dependency install, database startup, health waiting, backend build, frontend build, and final readiness success
  - Use `set -euo pipefail` carefully, but do not conflate designed candidate test failures with a broken scaffold

### Dockerfile Instructions:
- Include a backend Dockerfile at `backend/Dockerfile` if the generated repository includes app container packaging
- The Dockerfile should use a Java 21 compatible base image, perform a Maven build or copy the built artifact in a conventional way, and run the Spring Boot application
- Keep the Dockerfile functional and production-oriented without making docker image build the main readiness bottleneck
- Do not install the Java runtime with apt-get; the selected base image should provide the runtime/build environment
- If frontend container packaging is included, use a separate concrete file path such as `frontend/Dockerfile`, but do not require it unless the scenario genuinely benefits from app container packaging
- The Dockerfile must not contain TODO comments, solution hints, or hard-coded secrets beyond harmless local development values already used by docker-compose

The output should be a valid json schema:
  - README.md (CRITICAL - containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order)
  - .gitignore (standard Java, Maven, React, TypeScript, Node, PostgreSQL, Docker, IDE, log, and OS exclusions)
  - .dockerignore (efficient Docker build exclusions for backend/frontend artifacts)
  - docker-compose.yml (PostgreSQL service only unless the selected scenario truly requires an app container service)
  - database/init_database.sql (schema creation and realistic seed data in one executable initialization file)
  - run.sh (readiness gate for dependency installation, PostgreSQL startup, database health, backend build, and frontend build)
  - kill.sh (idempotent cleanup script for this task's compose resources, volumes, generated data, build artifacts, and /root/task)
  - pom.xml (root Maven aggregator or project metadata if appropriate)
  - backend/pom.xml (Java 21 Spring Boot Maven backend dependencies and plugins)
  - backend/Dockerfile (functional backend container packaging if included)
  - backend/src/main/java/com/example/fullstack/Application.java (Spring Boot application entry point)
  - backend/src/main/java/com/example/fullstack/config/CorsConfig.java (local frontend/backend integration configuration)
  - backend/src/main/java/com/example/fullstack/config/JacksonConfig.java (date/time and JSON configuration if useful)
  - backend/src/main/java/com/example/fullstack/controller/FeatureController.java (REST controller foundation for the selected feature)
  - backend/src/main/java/com/example/fullstack/service/FeatureService.java (service layer foundation for the selected feature)
  - backend/src/main/java/com/example/fullstack/repository/FeatureRepository.java (repository/data access foundation for the selected feature)
  - backend/src/main/java/com/example/fullstack/domain/DomainEntity.java (representative JPA entity or domain model appropriate to the scenario)
  - backend/src/main/java/com/example/fullstack/dto/FeatureRequest.java (request DTO foundation)
  - backend/src/main/java/com/example/fullstack/dto/FeatureResponse.java (response DTO foundation)
  - backend/src/main/java/com/example/fullstack/dto/PageResponse.java (typed page/collection response contract if the selected feature needs it)
  - backend/src/main/java/com/example/fullstack/error/ApiError.java (structured error response model)
  - backend/src/main/java/com/example/fullstack/error/GlobalExceptionHandler.java (starter exception mapping foundation)
  - backend/src/main/resources/application.yml (local datasource, JPA, logging, and application settings)
  - backend/src/test/java/com/example/fullstack/ApplicationSmokeTest.java (starter smoke test that compiles without solving the task)
  - contracts/openapi.yaml (shared REST contract source or equivalent typed contract artifact)
  - frontend/package.json (React, TypeScript, Vite dependencies and scripts)
  - frontend/tsconfig.json (strict TypeScript configuration)
  - frontend/tsconfig.node.json (Vite/node TypeScript configuration if needed)
  - frontend/vite.config.ts (Vite configuration)
  - frontend/index.html (frontend HTML entry point)
  - frontend/src/main.tsx (React entry point)
  - frontend/src/App.tsx (application shell)
  - frontend/src/api/client.ts (typed API client foundation)
  - frontend/src/api/contracts.ts (TypeScript API contract types aligned with the backend/OpenAPI contract)
  - frontend/src/components/FeaturePage.tsx (feature page foundation)
  - frontend/src/components/FeatureFilters.tsx (user input/filtering foundation if needed)
  - frontend/src/components/FeatureTable.tsx (result/list/presentation foundation if needed)
  - frontend/src/hooks/useFeatureData.ts (custom hook foundation for data loading/state)
  - frontend/src/styles.css (basic styling)
  - frontend/src/test/App.test.tsx (frontend smoke or starter test if test tooling is included)

## Code file requirements
- Use realistic file paths and names that follow Java Spring Boot, Maven, React, TypeScript, Vite, and PostgreSQL conventions
- Code should follow modern best practices and demonstrate intermediate-level patterns without completing the candidate's design work
- **CRITICAL**: The generated code files should provide a substantial, realistic starter codebase with multiple interacting modules and files; do not ship a toy snippet or a single obvious file to edit
- **CRITICAL**: The generated starter code must compile and build successfully before the candidate solves the task
- Include existing backend controllers, services, repositories, DTOs, models/entities, configuration, and error handling that the candidate needs to extend or rework
- Include existing frontend components, hooks, API client utilities, typed contracts, and state/data flow foundations that the candidate needs to extend or rework
- Include realistic PostgreSQL schema and data that candidates must investigate through the application and/or SQL, not a one-table or tiny seed example
- The core feature design decisions that the candidate needs to make MUST be left for the candidate to design
- Do not include any TODO comments, placeholder comments, or comments that reveal the solution
- Do not include comments like "add pagination here", "implement validation here", "optimize this query", "use this hook", or any equivalent solution hint
- Do not include direct references in candidate-facing files to exact method names, file names, or class names that identify where the answer belongs
- Keep Java code modular, legible, and production-oriented with meaningful naming, encapsulation, exception handling, logging, and clear separation of responsibilities
- Keep TypeScript strict, typed, and aligned with the backend contract, while still leaving business behavior and UI state decisions for the candidate
- Keep PostgreSQL SQL valid, deterministic, and executable by the official PostgreSQL Docker image
- The generated repository must be runnable and buildable locally through the provided run.sh readiness gate
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- kill.sh must be included and must be idempotent. It should stop and remove compose resources, remove associated volumes/networks, clean project build artifacts such as `backend/target` and `frontend/dist`, remove task-owned data directories, and remove `/root/task` while ignoring already-removed resources with `|| true` where appropriate
- kill.sh should print logs at every cleanup step and end with a concise completion message. It must not be required for normal candidate work, but it must exist as a complete cleanup artifact

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for a Java Spring Boot, React TypeScript, PostgreSQL, and Docker full-stack project that includes:
- Java and Maven build outputs such as `target/`, `*.class`, `*.jar`, `*.war`, and related build artifacts
- Node and frontend outputs such as `node_modules/`, `dist/`, `build/`, coverage directories, and npm/yarn logs
- IDE/editor files such as `.idea/`, `.vscode/`, `*.iml`, `.classpath`, `.project`, and `.settings/`
- Environment and secret files such as `.env`, `.env.*`, local credentials, and generated secret files
- PostgreSQL data directories, Docker volume directories, and local database dumps/backups
- Log files, temp files, cache directories, OS-specific files such as `.DS_Store` and `Thumbs.db`
- Any other standard exclusions for Java, Maven, React, TypeScript, PostgreSQL, Docker, and local development

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this exact order, and NO others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four sections MUST be emitted as an actual markdown heading using `##` consistently:
- `## Task Overview`
- `## Objectives`
- `## Helpful Tips`
- `## How to Verify`

A plain unmarked text line with the section name is INVALID and counts as a missing section. Do not add `Database Access`, `Application Access`, `Initial Setup Status`, `Guidance`, `Performance Issues`, `Schema Overview`, `Setup`, or `NOT TO INCLUDE` as README sections.

### Task Overview
- This section MUST contain 3-4 meaningful sentences and no bullet list
- It must describe the business scenario, current state of the product or workflow, and why the feature matters
- It must be written at outcome altitude: describe the feature capability the business needs, not the implementation mechanism
- It must NEVER be empty and must not include bold time-budget callouts
- It must not mention file paths, class names, method names, exact endpoint names that reveal the implementation, database connection details, or setup commands

### Objectives
- For this INTERMEDIATE DESIGN/BUILD task, Objectives MUST use the DESIGN/BUILD branch: each bullet is one short plain goal statement, roughly 10-15 words, naming the outcome the system must achieve
- Use 3-4 bullets max; fewer, tighter objectives are better
- Do not use stakeholder-framed repair wording, because this is not a repair task
- Imperative mood is correct for DESIGN/BUILD objectives, but do not reveal the mechanism
- One concern per bullet; split any bullet that bundles separable concerns
- Do not name APIs, libraries, frameworks, patterns, algorithms, config knobs, files, file paths, directories, functions, methods, classes, variables, tables, columns, endpoints, or other direct code references
- Do not describe current broken behavior or before/after diffs
- Good design/build style: "Build a workflow that keeps account activity usable across large histories."
- Good design/build style: "Keep customer-facing data consistent across the page, API, and database."
- Bad design/build style: "Add cursor pagination to GET /api/v1/accounts/{{id}}/transactions."
- Bad design/build style: "Create an index on posted_at and account_id."

### Helpful Tips
- Provide practical guidance without revealing specific implementations
- Use 4-5 bullets max
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze"
- Tips should guide discovery across API contract, backend layering, database access, frontend state, validation, and edge cases
- Tips MUST NOT name the specific API, library, function, pattern, data structure, query, index, hook, class, method, file, or algorithm that solves the task
- Tips should not provide step-by-step implementation guidance or solution-shaped architecture

### How to Verify
- For this INTERMEDIATE DESIGN/BUILD task, How to Verify MUST use probe-style verification
- Use 3-5 bullets max
- Each bullet names an experiment to run and where to look, without stating what the correct result is
- Pattern: "<make this change or try this workflow>, and <where to look>"
- Keep one probe per Objective where possible, in the same order
- Do not state pass conditions that give away hidden requirements or exact implementation rules
- At most one bullet may reference the task environment directly
- Do not include setup commands such as `npm install`, `npm run build`, `mvn test`, `docker compose up`, or `./run.sh`
- Before emitting, read the Objectives and How to Verify together as a candidate would: between them they must still not give away any rule the candidate is meant to derive

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of README.md:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, `npm run build`, or `./run.sh`
- Manual deployment instructions or instructions to run the readiness script
- Database connection details, including host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, SQL statements, index definitions, hook names, component names, or data-structure names that reveal the solution
- Code snippets, query snippets, configuration snippets, or JSON examples that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", or "add this index"
- Any heading named "NOT TO INCLUDE", "Content to Exclude", "Database Access", "Application Access", "Setup", or "Initial Setup Status"

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Provide a short descriptive kebab-case GitHub repository name under 50 characters that reflects the selected full-stack feature scenario without exposing the solution.",
  "title": "Provide a human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, describing the full-stack feature work in plain English.",
  "question": "Write the full candidate-facing task description as one scenario paragraph plus a direct imperative ask, at the same outcome altitude as the README Objectives: identify who the candidate is, what business system exists, why the current product capability is not sufficient, and what outcomes the rework must achieve without naming files, paths, functions, methods, classes, tables, columns, endpoint routes, or direct solution mechanisms.",
  "code_files": {{
    "README.md": "Create the candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "Create a comprehensive gitignore for Java, Maven, React, TypeScript, Node, PostgreSQL, Docker, IDE files, logs, environment files, build artifacts, and local data.",
    ".dockerignore": "Create Docker build exclusions for Maven targets, frontend dependencies and builds, IDE files, git metadata, logs, and local database data.",
    "docker-compose.yml": "Create a compose file with no version key that starts PostgreSQL only unless an app service is genuinely required, uses localhost-only port binding, inline POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB values, a matching healthcheck, and an init SQL mount.",
    "database/init_database.sql": "Create one executable PostgreSQL initialization file that defines the realistic relational schema and programmatically seeds internally consistent production-like data for the selected scenario.",
    "run.sh": "Create a readiness script rooted at /root/task that installs backend and frontend dependencies, starts PostgreSQL with docker compose, waits for health, verifies database initialization, builds the Java backend, builds the React frontend, and exits 0 on the unsolved starter.",
    "kill.sh": "Create an idempotent cleanup script that stops and removes task compose resources, volumes, networks, build artifacts, task-owned data, and /root/task while printing progress and ignoring already-removed resources.",
    "pom.xml": "Create a root Maven aggregator or project metadata file appropriate for the repository layout if the backend module is nested under backend/.",
    "backend/pom.xml": "Create the Java 21 Spring Boot Maven backend manifest with pinned practical dependencies for web, validation, data persistence, PostgreSQL, testing, and build plugins.",
    "backend/Dockerfile": "Create a functional Java 21 backend Dockerfile for app packaging if included, without making container build required for solving the task.",
    "backend/src/main/java/com/example/fullstack/Application.java": "Create the Spring Boot backend application entry point.",
    "backend/src/main/java/com/example/fullstack/config/CorsConfig.java": "Create local integration configuration that allows the frontend starter to communicate with the backend safely in development.",
    "backend/src/main/java/com/example/fullstack/config/JacksonConfig.java": "Create JSON date/time serialization configuration if useful for the selected scenario.",
    "backend/src/main/java/com/example/fullstack/controller/FeatureController.java": "Create a REST controller foundation for the selected feature that follows project conventions without completing the candidate's core design work.",
    "backend/src/main/java/com/example/fullstack/service/FeatureService.java": "Create a service-layer foundation that coordinates domain behavior and repository access without embedding the final feature solution.",
    "backend/src/main/java/com/example/fullstack/repository/FeatureRepository.java": "Create a repository or data-access foundation appropriate to the selected schema while leaving the central data-access design for the candidate.",
    "backend/src/main/java/com/example/fullstack/domain/DomainEntity.java": "Create representative JPA entity or domain model files using concrete names from the selected domain; if multiple entities are needed, emit each with its real file name instead of this generic example.",
    "backend/src/main/java/com/example/fullstack/dto/FeatureRequest.java": "Create a request DTO foundation using a concrete domain name if more appropriate, with validation annotations where they do not reveal the solution.",
    "backend/src/main/java/com/example/fullstack/dto/FeatureResponse.java": "Create a response DTO foundation using a concrete domain name if more appropriate, aligned with the shared contract.",
    "backend/src/main/java/com/example/fullstack/dto/PageResponse.java": "Create a reusable typed collection or page response DTO only if the selected feature genuinely needs collection-style responses.",
    "backend/src/main/java/com/example/fullstack/error/ApiError.java": "Create a structured error response model suitable for REST API consumers.",
    "backend/src/main/java/com/example/fullstack/error/GlobalExceptionHandler.java": "Create a starter centralized exception mapping foundation that compiles without revealing exact feature behavior.",
    "backend/src/main/resources/application.yml": "Create backend configuration for the local PostgreSQL datasource, JPA/Hibernate behavior, logging, and server settings using values consistent with docker-compose.",
    "backend/src/test/java/com/example/fullstack/ApplicationSmokeTest.java": "Create a backend smoke test that confirms the starter context or core wiring compiles without requiring the candidate's final solution.",
    "contracts/openapi.yaml": "Create a shared API contract source or equivalent contract artifact that keeps backend DTO expectations and frontend TypeScript types aligned without overspecifying the hidden implementation.",
    "frontend/package.json": "Create the React TypeScript Vite package manifest with pinned practical dependencies and scripts for development, build, preview, and tests if included.",
    "frontend/tsconfig.json": "Create strict TypeScript compiler configuration appropriate for a React Vite project.",
    "frontend/tsconfig.node.json": "Create TypeScript configuration for Vite/node tooling if required by the frontend setup.",
    "frontend/vite.config.ts": "Create a Vite configuration that supports the local React TypeScript app and backend integration.",
    "frontend/index.html": "Create the frontend HTML entry point.",
    "frontend/src/main.tsx": "Create the React application entry point.",
    "frontend/src/App.tsx": "Create the application shell that routes or renders the selected feature area without implementing the final candidate behavior.",
    "frontend/src/api/client.ts": "Create a typed API client foundation that centralizes backend communication without hard-coding the final feature logic.",
    "frontend/src/api/contracts.ts": "Create TypeScript contract types aligned with the backend/OpenAPI contract and selected scenario.",
    "frontend/src/components/FeaturePage.tsx": "Create a concrete feature page component using a domain-specific file name where appropriate and leaving core behavior for the candidate.",
    "frontend/src/components/FeatureFilters.tsx": "Create a concrete input/filter component if the selected scenario needs user-controlled query or workflow inputs.",
    "frontend/src/components/FeatureTable.tsx": "Create a concrete display component if the selected scenario needs list, table, or result presentation.",
    "frontend/src/hooks/useFeatureData.ts": "Create a custom hook foundation using a concrete domain-specific name where appropriate, without completing the final state/data behavior.",
    "frontend/src/styles.css": "Create basic styling sufficient for a usable starter interface.",
    "frontend/src/test/App.test.tsx": "Create a frontend smoke or starter test if test tooling is included, ensuring it does not require the candidate's final solution to make run.sh succeed."
  }},
  "answer": "Provide an evaluator-facing high-level solution approach that explains the intended full-stack design across REST contract, Java service layering, repository/database access, PostgreSQL schema/query considerations, typed frontend integration, validation, errors, and user experience without being shown to the candidate.",
  "definitions": "Provide an object of concise term-to-definition pairs for relevant full-stack concepts such as REST resource modeling, DTO, typed contract, repository layer, transaction boundary, pagination, validation, PostgreSQL index, and audit column.",
  "hints": "Provide a single-line non-revealing hint that nudges the candidate to trace the feature through the contract, backend layers, data model, and frontend state before choosing an implementation.",
  "outcomes": "Provide 2-3 lines describing measurable expected results in simple English, including correct end-to-end feature behavior, consistent API/frontend/database handling, and production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.",
  "pre_requisites": "Provide a bullet list of assumed prior knowledge only, using declarative capability phrases such as Java 21 and Maven proficiency, comfort with Spring Boot REST APIs and PostgreSQL, and familiarity with React and TypeScript; do not include setup, install, run, configure, or verification steps.",
  "short_overview": "Provide exactly three bullets, one sentence each, in plain non-technical business English: first describe what the system is and its current product situation, second open with 'This rework needs to ...' or similar and state only outcome-level goals, and third describe what separates a strong submission while closing on whether the design reasoning is sound."
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
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences outside JSON
2. **name** must be short, descriptive, kebab-case, under 50 characters, and different from title
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and human-readable for display
4. **question** must be outcome-altitude prose with no bullets, no file paths, no method/function/class names, no endpoint routes, no table/column names, and no direct solution statements
5. **short_overview** must contain exactly three bullets, one sentence each, in plain non-technical business English, with no backticks, file paths, mechanism names, or seeded-defect enumeration
6. **README.md** must contain exactly `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify` in that order; no other README headings are allowed
7. **README Objectives** must follow the DESIGN/BUILD branch: 3-4 short plain goal statements, one concern per bullet, no stakeholder repair framing, and no implementation mechanisms
8. **README How to Verify** must use probe-style experiments and must not state the correct result or hidden pass condition
9. **docker-compose.yml** must include PostgreSQL with no version key, localhost-only binding `127.0.0.1:5432:5432`, inline POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB, matching healthcheck, and no `.env` or `${{VAR}}` host indirection
10. **run.sh** must install dependencies first, start PostgreSQL, wait for health, verify initialization, build backend and frontend, and exit 0 on the unsolved starter
11. **kill.sh** must be included as a concrete artifact and must clean task-owned compose resources, volumes, networks, build artifacts, data directories, and `/root/task`
12. **Starter code** must be substantial and realistic for INTERMEDIATE proficiency, with multiple interacting modules and files across backend, frontend, and database
13. **Database seed data** must include several related tables, real relationships, lifecycle/status columns, audit columns, indexes, generated row volume, NULLs, near-duplicates, soft-deleted rows, unicode names, timezone-boundary timestamps, exact decimal money where relevant, and internally consistent records
14. **Do not include TODO comments or solution hints** in source code, SQL, README, question, or starter comments
15. **Task must be completable within the allocated time** for an intermediate engineer with 3-5 years of full-stack experience
"""

PROMPT_REGISTRY = {
    "Java (INTERMEDIATE), PostgreSQL (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_CONTEXT,
        PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_JAVA_REST_REACT_TYPESCRIPT_POSTGRESQL_INTERMEDIATE_INSTRUCTIONS,
    ],
}