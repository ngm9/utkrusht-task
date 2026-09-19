# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how Node.js REST APIs, React, TypeScript, and MongoDB are used together to deliver production-grade full-stack product features at an intermediate level?
"""

PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a full-stack Node.js, React, TypeScript, REST API, and MongoDB assessment task.

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
- The task must be a DESIGN/BUILD task, not a repair task. The candidate should build or rework a feature end to end across a React + TypeScript frontend, a Node.js REST API backend, and a MongoDB database
- The generated task must keep the question, README Objectives, and short_overview at outcome altitude. Do not enumerate the implementation mechanisms that solve the task

Based on the above inputs, briefly state:
1. Which scenario you selected and why
2. What the task will involve as an end-to-end full-stack design/build challenge

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""

PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Node.js REST APIs, React, TypeScript, and MongoDB, you are given a list of real world scenarios and proficiency levels for full-stack TypeScript development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to design, build, implement, debug, and reason through an end-to-end production-style feature at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL, buildable full-stack TypeScript repository with a React frontend, a Node.js REST API backend, shared typed contracts, and a FULLY POPULATED MongoDB database initialized by Docker Compose.
The starter application must compile and boot, but the feature area being assessed is intentionally incomplete or under-shaped so the candidate must make design decisions across the frontend, API, service, repository, and database layers.

The generated repository should feel like an afternoon inside a real production codebase for an engineer with 3-6 years of hands-on experience:
- The backend must be a Node.js REST API written in TypeScript using Express or NestJS, with clear route -> controller or handler -> service -> repository layering
- The frontend must be React with TypeScript, using functional components, hooks, typed API clients, realistic UI state, and shared contracts from the backend or a shared package
- The MongoDB data model must include several related collections with relationships, status lifecycles, audit columns, indexes, and realistic seed data
- The relevant logic must NOT be concentrated in the first file opened. The candidate should need to navigate multiple interacting modules before deciding where and how to change the system
- The task is a DESIGN/BUILD task, not a repair task: nothing should be described as a known bug with a single hidden fix. The candidate is reworking or extending a feature to meet product and operational outcomes

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or rework one cohesive feature end to end across React + TypeScript, a Node.js REST API, and MongoDB.
- **CRITICAL — DESIGN/BUILD ONLY**: This must not be framed as a repair task. Do not say that a specific endpoint, component, query, file, or function is broken. Present a product need and a working foundation that must be extended to a production-quality outcome.
- **CRITICAL — Task Depth Over Breadth**: The task should present 1-2 major implementation areas that are architecturally meaningful and require deep thinking, not a shopping list of unrelated features.
- **CRITICAL — Outcome Altitude**: The candidate-facing question must not enumerate the mechanisms that satisfy the task. It should explain who the candidate is, what system exists, why the feature matters, and what outcomes the rework must achieve.
- The complexity of the task must align with INTERMEDIATE proficiency level for Node.js, REST APIs, React, TypeScript, and MongoDB, suitable for engineers with 3-6 years of experience.
- **CRITICAL TIME BUDGET**: The total task time is {minutes_range} minutes. The candidate needs time to inspect the code, verify behavior, and make focused changes. Keep the feature substantial but completable with AI assistance.
- Generate a substantial, realistic starter codebase, not a toy snippet. Require multiple interacting modules and changes that reasonably span more than one file.
- The backend should include realistic route, controller or handler, service, repository, model, validation, configuration, logging, and error-handling modules.
- The frontend should include realistic pages or route-level views, reusable components, hooks, typed API client code, state handling, loading and error states, and shared type usage.
- The shared TypeScript contracts should be used by both frontend and backend where appropriate, but must not hand the solution to the candidate.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- DO NOT include TODO comments, placeholder comments, or comments such as "add cursor pagination here", "create index here", "fix state here", "use this hook", or any comments that reveal the solution.
- The question scenario must be clear and based on one selected real-world scenario. It must use concrete business context, not generic ecommerce or dashboard filler unless that is the scenario provided.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fill in obvious blanks.
- For INTERMEDIATE level, the task should test a focused combination of the following, chosen according to the selected scenario:
  - RESTful resource modeling, request and response design, meaningful status codes, and consistent error responses
  - Pagination, filtering, sorting, or endpoint shaping for realistic data volumes
  - Input validation, authorization-aware scoping, and safe handling of untrusted client data
  - Route -> service -> repository separation with maintainable business logic boundaries
  - MongoDB schema design using embedded versus referenced data where appropriate
  - MongoDB aggregation, query planning, indexes, and data access patterns that support the feature workload
  - Multi-document consistency, retryable operations, idempotency, or transaction boundaries when the scenario genuinely exercises them
  - React component composition, custom hooks, typed API consumption, resilient UI states, and maintainable client data flow
  - TypeScript interfaces, unions, generics where useful, strict compiler settings, and shared contract discipline
  - Structured logging and basic observability that help diagnose API and data-flow issues
- **Production Realism — DATA**: The MongoDB initialization must create several related collections with real relationships, status or lifecycle fields, validation, indexes, constraints where MongoDB supports them, audit fields such as createdAt and updatedAt, and soft-delete or archive fields where the scenario needs them.
- **Production Realism — VOLUME**: Seed hundreds to a few thousand documents programmatically so the answer cannot be found by eyeballing the seed file. The candidate should need to query, aggregate, inspect responses, or reason about data access patterns.
- **Production Realism — MESS**: Include realistic production data mess: nulls in nullable fields, near-duplicates that differ in one field, archived or soft-deleted records, unicode and apostrophes in names, timestamps crossing timezone and day boundaries, Decimal128 money values, out-of-order or back-dated sequences, and boundary cases around the feature rules.
- **Production Realism — CONSISTENCY**: Seeded data must be internally consistent. References must resolve, lifecycle statuses must be legal, derived totals must reconcile, and messy data must be intentional rather than random corruption.
- **Production Realism — SETUP**: Include dependency manifests with pinned versions, TypeScript compiler configuration, conventional project layout, Docker-backed MongoDB initialization, service healthchecks, and a run.sh readiness gate.
- **Production Realism — HARD BOUND**: Everything must still install, build, seed, and start inside run.sh's time budget on a small sandbox with about 2 vCPU and 2 GB RAM. Use realistic shape and mess, not raw volume. Do not seed millions of documents or add heavyweight dependencies that take minutes to install.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Node.js documentation, React documentation, TypeScript documentation, MongoDB documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- The complexity of the tasks should require genuine engineering judgment, architecture, implementation, and tradeoff analysis that goes beyond simple copy-pasting from a generative AI.
- Candidates should be able to use external help while still demonstrating that they understand the codebase, can make coherent design decisions, and can deliver a maintainable full-stack feature.

## Code Generation Instructions
Based on the real-world scenarios provided, create a full-stack Node.js + React + TypeScript + MongoDB task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level, keeping in mind that AI assistance is allowed
- Tests practical full-stack TypeScript engineering through one cohesive design/build feature, not a collection of disconnected fixes
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list to ensure variety
- Uses Node.js 18+ or 20+ with TypeScript for the backend
- Uses Express or NestJS for the REST API; Express is preferred unless the scenario strongly suggests NestJS
- Uses React 18+ with TypeScript for the frontend, preferably Vite for a lightweight local developer workflow
- Uses MongoDB through the official driver or Mongoose; choose the option that best supports the scenario and intermediate-level assessment
- Shares typed contracts between frontend and backend through a real local shared package or workspace
- Provides meaningful starter code across backend, frontend, shared types, infrastructure, and database initialization
- Leaves the core feature design and implementation decisions to the candidate without emitting solution-shaped stubs
- Ensures all code and scripts are valid, buildable, and reference /root/task as the base directory

## Infrastructure Requirements
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

**CRITICAL — ONE-GO READINESS**: When run.sh is executed, dependencies must install, MongoDB must start from the repository's own docker-compose.yml, the database must initialize and seed through the mounted MongoDB init script, and the TypeScript starter must build successfully. Deployment readiness must succeed on the UNSOLVED starter.

The infrastructure is for the datastore only unless you intentionally choose to run app services in containers. For this full-stack task, prefer a local Node.js workspace plus Docker Compose for MongoDB so the E2B Node runtime template can install and build quickly.

Do not include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup scripts are unnecessary and must not be part of the generated repository.

### Docker-compose Instructions
- docker-compose.yml MUST include a MongoDB service for the task's own database. The database must come from this repository's docker-compose.yml, never from the runtime template.
- docker-compose.yml MUST NOT include any version specification.
- **SECURITY-CRITICAL**: MongoDB ports MUST be bound to localhost only using `127.0.0.1:27017:27017`.
- Use inline environment values required by the MongoDB image, such as MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD, and MONGO_INITDB_DATABASE. Do not use `.env` files or host variable indirection.
- Mount the MongoDB initialization file into `/docker-entrypoint-initdb.d/` so collection creation, validation, indexes, application user creation, and seeding happen during container initialization.
- The init script, healthcheck, and backend connection string must use the same database and compatible credentials. If the backend authenticates against the application database, create the application user in that database and use the matching authSource.
- Include a healthcheck that confirms MongoDB is accepting authenticated commands.
- Use named volumes for MongoDB data persistence.
- Do not add PostgreSQL, MySQL, Redis, Kafka, or any other datastore unless the selected scenario explicitly requires it. For this competency combination, MongoDB is the datastore to exercise.
- Do not rely on `.env` files for docker-compose values.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST, `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:`. Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.

### MongoDB Initialization Instructions
- Include a concrete MongoDB init or migration file, such as `infra/mongo/001_init_mongo.js`, mounted into `/docker-entrypoint-initdb.d/`.
- The file must create the application database, application user, collections, JSON Schema validators where appropriate, indexes, and realistic seed data.
- The seed data must be generated programmatically where volume calls for it. Use loops or generators rather than hand-writing hundreds of literal documents.
- Include several related collections appropriate to the selected domain, such as customers, orders, payments, shipments, products, accounts, transactions, cases, messages, invoices, or other scenario-specific resources.
- Model real relationships through ObjectId references, embedded subsets, extended references, or other MongoDB-appropriate patterns. The choice should fit the scenario and leave design room for the candidate.
- Include status lifecycles, audit fields, nullable fields, soft-deleted or archived rows, unicode names, apostrophes, timestamps crossing timezone and day boundaries, Decimal128 money fields, near-duplicates, and boundary cases.
- Include indexes that make the starter realistic, but do not pre-solve every data access challenge. The generated task should leave appropriate schema, query, or access-pattern decisions for the candidate.
- Keep initialization fast. The init script must run in seconds on a small sandbox.

### Run.sh Instructions
- Include run.sh for readiness, not grading.
- run.sh MUST start with `#!/usr/bin/env bash` and use `set -e` except where intentionally capturing command exit codes.
- run.sh MUST `cd /root/task` before running commands.
- run.sh's first project step MUST install dependencies using the runtime-native manifest command, such as `npm ci`.
- run.sh MUST start MongoDB using `docker compose up -d`.
- run.sh MUST wait for MongoDB readiness with a bounded retry loop and print useful status messages.
- run.sh MUST NOT create MongoDB users or run seed scripts manually. Database setup is performed automatically by MongoDB entrypoint initialization through mounted files.
- run.sh MUST verify the starter builds on the UNSOLVED starter, for example by running the shared package build, backend TypeScript build, and frontend TypeScript or Vite build through a root workspace script such as `npm run build`.
- run.sh MUST NOT run the grader test suite or any candidate-facing failing tests. It is a deployability and readiness gate only.
- run.sh MUST exit 0 when dependencies install, MongoDB becomes healthy, and the starter compiles or loads successfully.
- run.sh should print a concise success message that indicates the database is reachable on localhost and that the workspace build passed.
- All paths in run.sh must reference /root/task.

### Dockerfile Instructions
Omit Dockerfile files unless you intentionally place the frontend or backend application in containers. For this task shape, prefer no app Dockerfile and no app container because the Node.js runtime is already available in the E2B template and docker-compose is only required for MongoDB.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Standard Node.js, React, TypeScript, MongoDB, Docker, and IDE exclusions)
  - docker-compose.yml (MongoDB service only unless app containers are intentionally required; no version key)
  - run.sh (Readiness gate that installs dependencies, starts MongoDB, waits for health, builds the starter, and exits 0 on the unsolved starter)
  - package.json (Root workspace manifest with pinned dependencies and scripts)
  - package-lock.json (Include if generated consistently for npm ci)
  - tsconfig.base.json (Shared TypeScript compiler configuration)
  - shared/package.json, shared/tsconfig.json, and shared/src/index.ts (Shared typed contracts used by frontend and backend)
  - api/package.json, api/tsconfig.json, and api/src/server.ts (Backend package, compiler config, and application entry point)
  - api/src/app.ts, api/src/routes/*.ts, api/src/controllers/*.ts, api/src/services/*.ts, api/src/repositories/*.ts, api/src/models/*.ts, api/src/middleware/*.ts, api/src/config/*.ts, and api/src/utils/*.ts (Real backend layers and support modules)
  - web/package.json, web/tsconfig.json, web/vite.config.ts, web/index.html, and web/src/main.tsx (Frontend package, compiler config, Vite config, and entry point)
  - web/src/App.tsx, web/src/pages/*.tsx, web/src/components/*.tsx, web/src/hooks/*.ts, web/src/api/*.ts, web/src/state/*.ts, web/src/styles.css, and web/src/utils/*.ts (Real React application modules)
  - infra/mongo/001_init_mongo.js (MongoDB init and seed script that creates schema, indexes, user, and realistic data)

## Code file requirements
- Generate a realistic monorepo-style project structure using npm workspaces or another simple Node-native workspace setup.
- Use concrete file paths and names. Do not emit placeholder-style keys such as `additional_files_as_needed`, `selected_stack_manifest_and_source`, or `supporting_scripts`.
- Use TypeScript throughout backend, frontend, and shared contracts.
- Backend code must follow route -> controller or handler -> service -> repository layering with clear separation of concerns.
- Backend routes must expose RESTful resources using appropriate HTTP methods, status codes, request validation, and response shapes.
- Backend code must include structured error handling and basic structured logging suitable for intermediate-level assessment.
- MongoDB access must be encapsulated in repositories or data access modules. Do not put all database logic directly inside route handlers.
- React code must use functional components and hooks exclusively.
- React code must include realistic UI composition, typed API consumption, loading states, error states, and enough existing structure for the candidate to work within.
- Shared contracts must be real TypeScript exports consumed by both frontend and backend.
- The generated starter must be buildable and bootable but incomplete with respect to the assessed feature.
- The core product workflow, API contract refinements, state management choices, data access strategy, and schema or index tradeoffs needed for the final feature MUST be left for the candidate to design.
- Do not include comments that reveal hints, solutions, file locations to edit, or implementation details.
- Do not include TODO comments or placeholder comments.
- Do not include syntactic errors. Any failing behavior should be because the design/build feature is not complete, not because the scaffold is broken.
- Include realistic dependencies in package.json files with pinned versions that intermediate developers should be familiar with.
- Include tests only if they are self-check invariants that can run after the candidate implements the feature. run.sh must not require those tests to pass on the unsolved starter.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore file that covers all standard exclusions for Node.js, React, TypeScript, MongoDB, Docker-backed local development, and common editors:
- node_modules/
- dist/, build/, coverage/, .nyc_output/
- .vite/, .turbo/, .cache/
- logs/, *.log, npm-debug.log*, yarn-debug.log*, yarn-error.log*
- .env, .env.local, .env.*.local
- MongoDB local data folders and Docker volume artifacts
- .DS_Store, Thumbs.db
- .idea/, .vscode/, *.swp, *.swo
- temporary files, lock artifacts that should not be committed, and generated local state

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain exactly these sections in this exact order, each written as a markdown heading:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The section headings must be actual markdown headings using the same heading level consistently, such as `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify`. A plain unmarked text line with the section name is INVALID and counts as a missing section.

### Task Overview
- Must contain 3-4 meaningful sentences.
- Must not be a bullet list.
- Must describe the business scenario, current state, and why the end-to-end feature matters.
- Must be concrete and scenario-specific.
- Must never be empty or generic.
- Must not include bold time-budget callouts.
- Must not include setup commands, database credentials, localhost port instructions, or implementation hints.

### Objectives
- Because this is an INTERMEDIATE DESIGN/BUILD task, Objectives MUST be concise, open-ended goal statements.
- Include 3-4 bullets max; fewer, tighter is better.
- Each objective must be ONE SHORT PLAIN SENTENCE, roughly 10-15 words, naming the outcome the system must achieve.
- Use plain goal statements, not stakeholder framing, because this is a design/build task.
- Imperative mood is acceptable, but do not name mechanisms.
- One concern per bullet; split a bullet that bundles separable concerns.
- Describe the outcome, never the implementation approach.
- Do NOT name any API route, library, framework API, file, path, function, method, class, variable, collection, index, data structure, or pattern that solves the task.
- GOOD design/build style: "Make customer activity easy to review without overwhelming the page."
- GOOD design/build style: "Keep business records consistent as work moves through the interface."
- BAD design/build style: "Add cursor pagination to the orders endpoint."
- BAD design/build style: "Create a compound partial index for customer order lookups."

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery across full-stack architecture, API contracts, data modeling, type safety, and user experience.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, index strategy, hook, route, class, method, or algorithm that solves the task.
- Do not include code snippets or step-by-step instructions.

### How to Verify
- Include 3-5 bullets max.
- Because this is a DESIGN/BUILD task, each bullet must name an experiment to run and where to look, but MUST NOT state what the correct result is.
- Pattern: "Make this kind of change or interaction, and look at what the system shows or records."
- One probe per Objective, in the same order where practical.
- At most ONE bullet may reference the task environment directly.
- Do not reveal pass conditions that the Objectives intentionally withheld.
- Do not name exact routes, file paths, functions, implementation mechanisms, database indexes, or code-level checks.
- Frame verification in terms of observable outcomes: UI behavior, API response shape at a high level, build output, logs, or persisted data consistency.
- Before emitting, read the Objectives and How to Verify together as a candidate would: between them they must still not give away any rule the candidate is meant to derive.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Do not include the following in README.md:
- Setup commands such as npm install, npm ci, npm run build, docker compose up, or run.sh usage
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, index names, hook names, collection names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database connection details, credentials, client-tool suggestions, droplet IP placeholders, or remote-host placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use this specific API"
- A heading named "NOT TO INCLUDE", "CONTENT TO EXCLUDE", "Database Access", "Service Access", "Setup", or any README section other than the four required sections

## REQUIRED OUTPUT JSON STRUCTURE
The final response must be valid JSON only — no markdown fences, no commentary, and no explanatory text outside the JSON object.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the full-stack feature without exposing solution mechanisms.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, describing the full-stack design/build work in plain English.",
  "question": "A candidate-facing scenario paragraph plus direct imperative ask written at the same outcome altitude as the README Objectives: explain who the candidate is, what full-stack system exists, why it is not yet trusted or complete enough, and what outcomes the rework must achieve without naming file paths, routes, functions, classes, database collections, indexes, libraries, or direct solution mechanisms.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading such as ## Task Overview, ## Objectives, ## Helpful Tips, and ## How to Verify; a plain unmarked text line with the section name is invalid and counts as a missing section.",
    ".gitignore": "A comprehensive Node.js, React, TypeScript, MongoDB, Docker, operating-system, log, coverage, build-output, and editor exclusion file.",
    "docker-compose.yml": "A Docker Compose file with no version key that starts the task's MongoDB service, binds MongoDB only to localhost, mounts the MongoDB initialization script, sets required inline MongoDB initialization environment values, defines a healthcheck, and uses named volumes.",
    "run.sh": "A readiness script that cd's to /root/task, installs npm dependencies, starts MongoDB with docker compose up -d, waits for MongoDB health, builds the unsolved TypeScript starter, avoids running failing grader tests, and exits 0 when the scaffold is deployable.",
    "package.json": "A root npm workspace manifest with pinned scripts and dependencies or devDependencies needed to install, build, and coordinate the shared, api, and web packages.",
    "package-lock.json": "A consistent npm lockfile suitable for npm ci when the generated dependency tree is included.",
    "tsconfig.base.json": "A shared strict TypeScript compiler configuration used by the backend, frontend, and shared contracts packages.",
    "shared/package.json": "The shared package manifest exposing typed contracts consumed by both the frontend and backend.",
    "shared/tsconfig.json": "The shared package TypeScript configuration that builds shared contract exports.",
    "shared/src/index.ts": "Shared TypeScript domain contracts, request and response shapes, and safe cross-package types that support the scenario without giving away implementation mechanisms.",
    "api/package.json": "The backend package manifest with pinned Node.js, TypeScript, Express or NestJS, MongoDB or Mongoose, validation, logging, and build dependencies.",
    "api/tsconfig.json": "The backend TypeScript compiler configuration using strict settings and output appropriate for a Node.js REST API.",
    "api/src/server.ts": "The backend server entry point that loads configuration, initializes the app, connects to MongoDB with bounded retry behavior, and starts listening without embedding business logic.",
    "api/src/app.ts": "The backend application composition file that wires middleware, routes, health checks, errors, and request handling in a maintainable structure.",
    "api/src/config/database.ts": "MongoDB connection configuration using localhost defaults suitable for run.sh and Docker Compose, with no dependency on an external template database.",
    "api/src/config/runtime.ts": "Runtime configuration defaults for ports, database connection strings, logging, and feature-safe constants that do not pre-solve the task.",
    "api/src/routes/index.ts": "The backend route composition module that mounts scenario-specific REST resources without placing business logic in the router.",
    "api/src/routes/feature.routes.ts": "A scenario-specific REST routing module that delegates to controllers or handlers and reflects resource-oriented API design.",
    "api/src/controllers/feature.controller.ts": "A controller or handler module that validates high-level request flow, maps service results to HTTP responses, and leaves core design work to the service layer.",
    "api/src/services/feature.service.ts": "A service module containing scenario-level orchestration boundaries and partial feature behavior without implementing the candidate's core design decisions.",
    "api/src/repositories/feature.repository.ts": "A repository module encapsulating MongoDB reads and writes for the scenario while leaving appropriate data-access decisions for the candidate.",
    "api/src/models/feature.models.ts": "MongoDB or Mongoose model definitions reflecting several related domain collections, validation choices, audit fields, status lifecycles, and relationship structure.",
    "api/src/middleware/errorHandler.ts": "A centralized error handling module that produces structured responses and supports maintainable REST API behavior.",
    "api/src/middleware/requestLogger.ts": "A lightweight structured request logging module suitable for tracing frontend-to-backend interactions during development.",
    "api/src/utils/httpErrors.ts": "Reusable HTTP error helpers or typed error classes used across controller and service code without revealing feature logic.",
    "web/package.json": "The frontend package manifest with pinned React, TypeScript, Vite, testing or linting dependencies if included, and scripts for local build.",
    "web/tsconfig.json": "The frontend TypeScript compiler configuration for a strict React application.",
    "web/vite.config.ts": "The Vite configuration for the React frontend with appropriate development proxy or build settings that do not hardcode remote hosts.",
    "web/index.html": "The React application's HTML entry point.",
    "web/src/main.tsx": "The React entry point that renders the application root.",
    "web/src/App.tsx": "The top-level React component that composes the scenario interface without containing all feature logic.",
    "web/src/pages/FeaturePage.tsx": "A scenario-specific page component that coordinates UI sections and delegates data and state behavior to hooks and child components.",
    "web/src/components/FeatureSummary.tsx": "A reusable presentational or container component for scenario-level information that is meaningful but not solution-complete.",
    "web/src/components/FeatureList.tsx": "A reusable list, table, timeline, or board component appropriate to the selected scenario that leaves key interaction behavior to be completed.",
    "web/src/components/FeatureFilters.tsx": "A reusable filtering or control component that participates in the scenario workflow without prescribing the final API or state design.",
    "web/src/hooks/useFeatureData.ts": "A custom React hook for typed API consumption and UI state boundaries that provides a realistic starting point without revealing the completed workflow.",
    "web/src/api/client.ts": "A typed API client module that centralizes HTTP calls and response handling for the frontend.",
    "web/src/state/featureState.ts": "A frontend state helper or reducer module that supports the scenario while leaving design choices to the candidate.",
    "web/src/styles.css": "Concise application styling that makes the starter usable without making styling the assessment focus.",
    "infra/mongo/001_init_mongo.js": "A MongoDB initialization script that creates the application database, app user, collections, JSON Schema validators where useful, indexes, and programmatically generated realistic seed data across several related collections."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected full-stack architecture, API design considerations, React state and type-safety decisions, MongoDB modeling and query tradeoffs, and production-readiness qualities without requiring one exact implementation.",
  "definitions": "An object of term-to-definition pairs covering relevant concepts such as REST resource modeling, shared TypeScript contracts, MongoDB document modeling, aggregation, index, optimistic UI, validation, and structured error response.",
  "hints": "A single-line hint that nudges the candidate toward investigating the feature across client state, API boundaries, and data access patterns without naming the specific solution or implementation mechanism.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable product behavior, maintainable full-stack structure, reliable data handling, and production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging, and observability.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Node.js and TypeScript proficiency, comfort with React and REST APIs, and familiarity with MongoDB data modeling; do not include imperative setup, install, run, configure, or test steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first describe what the system does and its current situation, second describe what this rework needs to achieve at outcome altitude without mechanisms, and third describe what separates a strong submission while closing on whether the design reasoning is sound."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **PROMPT OUTPUT MUST NOT INCLUDE kill.sh** — E2B destroys the sandbox as a whole, so no cleanup script is required.
3. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, root package files, shared TypeScript contracts, backend TypeScript REST API files, frontend React TypeScript files, and the MongoDB init script.
4. **docker-compose.yml must NOT have a version field**.
5. **SECURITY-CRITICAL**: MongoDB must bind to localhost only using `127.0.0.1:27017:27017`.
6. MongoDB must be initialized by the mounted `/docker-entrypoint-initdb.d/` script, not by run.sh.
7. run.sh is a readiness gate only: it installs dependencies, starts MongoDB, waits for health, builds the starter, and exits 0 on the UNSOLVED starter.
8. The task must be a DESIGN/BUILD task with goal-statement Objectives and probe-style How to Verify bullets.
9. The question and short_overview must remain at outcome altitude and must not enumerate the hidden implementation rules.
10. The README must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as a markdown heading.
11. Do not include Database Access, Service Access, Setup, NOT TO INCLUDE, or any other README section.
12. Do not include droplet IP placeholders or remote-host placeholders anywhere. Any legitimate host reference in scripts or verification must use localhost.
13. The starter code must be substantial, realistic, multi-module, and buildable, but must not contain the solution.
14. Seed data must be realistic, internally consistent, generated programmatically, and large enough that candidates must investigate rather than eyeball the seed file.
15. Keep the task completable within the allocated time for INTERMEDIATE proficiency while still requiring meaningful full-stack reasoning.
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), NodeJs (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_CONTEXT,
        PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_FULLSTACK_NODE_REACT_MONGODB_INTERMEDIATE_INSTRUCTIONS,
    ],
}