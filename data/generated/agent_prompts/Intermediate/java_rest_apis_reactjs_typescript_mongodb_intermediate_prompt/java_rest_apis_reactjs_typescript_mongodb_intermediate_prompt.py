# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java, MongoDB, REST APIs, ReactJs, and TypeScript assessment task.

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
- The task MUST be a full-stack DESIGN/BUILD task, not a repair task: the candidate builds or reworks a feature end to end across a React + TypeScript frontend, a Java REST API backend, and MongoDB
- The backend MUST use Java 21 with Maven and Spring Boot style layering: controller -> service -> repository
- The frontend MUST use React with TypeScript and typed API contracts that stay aligned with the backend request and response model
- The task MUST include docker-compose.yml for MongoDB, a MongoDB initialization/migration script that creates schema validation, indexes, and realistic seed data, and run.sh as the readiness gate

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, full-stack technical context, and product feature the candidate will build or rework)
2. What will the task look like? (Describe the Java Spring REST API, MongoDB modeling/query work, and React TypeScript implementation required, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java Spring Boot, REST API design, MongoDB data modeling, React, and TypeScript, you are given a list of real world scenarios and proficiency levels for full-stack Java + MongoDB + React development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to think, design, build, implement, debug, and deliver a production-oriented full-stack feature end to end at an intermediate level.

The task MUST be a DESIGN/BUILD task, not a repair task. The candidate should receive a realistic, runnable monorepo foundation and build or rework one coherent feature across:
- Java 21 backend with Maven and Spring Boot style layering: controller -> service -> repository
- REST API contracts with appropriate HTTP semantics, validation, pagination/filtering, response structure, and error handling
- MongoDB collections with realistic relationships, indexes, schema validation, status lifecycles, audit fields, and production-shaped seed data
- React + TypeScript frontend using typed API contracts and maintainable state/data-flow patterns

The candidate's responsibility is to make architectural and implementation decisions without being handed the solution. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL local project scaffold with a Java Spring Boot backend, React TypeScript frontend, and MongoDB database initialization that can be started and inspected from /root/task. The initial project includes:
- A multi-module monorepo structure with separate backend, frontend, shared contract, and database initialization areas
- Java 21 Maven backend with conventional Spring Boot layering, including controllers, services, repositories, DTOs, configuration, exception handling, and tests
- React + TypeScript frontend with Vite, typed API models, realistic components, API client utilities, and state/data-flow foundations
- MongoDB docker-compose service with localhost-only port binding, initialization scripts, schema validation, indexes, and realistic seeded data
- A run.sh readiness gate that installs dependencies, starts MongoDB, waits for health, verifies backend and frontend builds on the UNSOLVED starter, and exits 0
- **CRITICAL**: The starting environment must be deployable and inspectable, but the candidate must still design and complete the feature behavior; do not ship the finished solution
- **CRITICAL**: The relevant implementation work must NOT be obvious from the first file opened; the candidate should navigate multiple modules and reason across frontend, API, service, repository, and MongoDB design
- **CRITICAL**: This is INTERMEDIATE level work for engineers with roughly 3-6 years of hands-on experience. The codebase must be substantial and realistic, not a toy snippet or a single-file exercise

The candidate's primary responsibility is to deliver one deep, coherent full-stack feature or rework that exercises Java application design, REST API modeling, MongoDB schema/query/index decisions, and React TypeScript integration. The task should require changes across more than one file and more than one layer, but it should still be scoped so it can be completed within {minutes_range} minutes.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or rework a full-stack feature end to end; it must NOT be framed as fixing a broken production bug
- **CRITICAL — DESIGN/BUILD ONLY**: Do not describe the current system as defective in a way that names the required mechanism. The scenario should say the business needs a more trustworthy, usable, scalable, or maintainable capability, and the candidate must design how to achieve that outcome
- **CRITICAL — Task Depth Over Breadth**: The task should present 1-2 major implementation areas that are architecturally meaningful and require deep thinking, NOT a checklist of many shallow fixes
- **CRITICAL**: The backend must be Java 21 with Maven and Spring Boot style layering: controller -> service -> repository
- **CRITICAL**: The frontend must be React with TypeScript, using typed contracts shared or mirrored in a clear contract layer so frontend and backend request/response expectations stay aligned
- **CRITICAL**: MongoDB must be part of the task's own docker-compose.yml and must not rely on a database provided by the runtime template
- **CRITICAL**: The MongoDB initialization file must create schema validation, collections, indexes, and realistic seed data using programmatic generation where volume calls for it
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, runnable full-stack monorepo foundation with enough starter code for the candidate to begin confidently, but DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fill in obvious blanks
- The question should be a real-world business scenario that tests architectural thinking and applied implementation, not a trick question and not syntax trivia
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-6 years experience), ensuring that no two questions generated are similar
- For INTERMEDIATE level proficiency, the task must require a substantial and realistic starter codebase:
  - Multiple interacting backend modules and files in a real Java project layout
  - Multiple frontend components, hooks or utilities, typed API model files, and client-side state/data-flow code
  - Existing domain models, DTOs, and repository abstractions that the candidate must understand before extending
  - Meaningful MongoDB seed data that cannot be understood by eyeballing one file
  - Changes that span more than one file and more than one architectural layer
- **CRITICAL — Production Realism Required**: The task must feel like an afternoon inside a real production repository, not an exercise. Include all three realism dimensions:
  - **DATA**: Several related MongoDB collections with real relationships, schema validation, status/enum lifecycles, indexes, audit columns or embedded audit objects such as createdAt and updatedAt, and soft-delete or archived flags. Never use one flat collection. Name things the way the selected domain would.
  - **VOLUME**: Seed hundreds to a few thousand documents so the answer cannot be seen by eyeballing the seed file. The candidate must query, aggregate, inspect the data shape, or reason about access patterns to build the feature well.
  - **MESSY CONTENT**: Include production-like data: nullable fields where the domain allows them, near-duplicates that differ in one field, soft-deleted or archived records that must be excluded from active views, unicode and apostrophes in names, timestamps crossing day and timezone boundaries, money stored as exact Decimal128 values rather than floating point, out-of-order or back-dated events, and rows at rule boundaries.
  - **CONSISTENCY**: The seeded data must be internally consistent: referenced IDs resolve, totals reconcile, status lifecycles are legal, and a candidate who investigates finds a coherent world rather than random noise.
  - **SETUP**: Include pinned Maven and npm dependencies, environment/config handling with sane local defaults, database initialization files, healthchecks, and conventional project layout.
  - **PRODUCTION CONCERNS**: Pick only concerns the chosen scenario genuinely exercises, such as pagination over large result sets, transaction boundaries where appropriate, validation at trust boundaries, authorization scoping, timezone and locale handling, money precision, index usage under volume, projection efficiency, aggregation design, and migration safety.
- **HARD BOUND**: Realism must not break the readiness gate. Everything must install, build, seed, and start inside run.sh's time budget on a small sandbox with 2 vCPU and about 2 GB RAM. Do NOT seed millions of rows, pull heavyweight images, or add dependencies that take minutes to install.
- MongoDB scope for intermediate tasks may include embedded vs referenced document modeling, aggregation pipelines, compound or partial indexes, projection, seek/range pagination, explain-plan reasoning, schema validation, update semantics, and Spring Data MongoDB usage
- REST API scope for intermediate tasks may include resource modeling, proper HTTP methods/status codes, request/response contracts, validation, structured errors, pagination/filtering/sorting, basic auth/authorization awareness where scenario-appropriate, OpenAPI documentation, and API-client integration
- Java scope for intermediate tasks may include OOP/SOLID, collections and streams, service/repository separation, exception handling, logging, basic resilience, Maven, JUnit/Mockito tests, and Spring Data usage
- ReactJs and TypeScript scope should stay scenario-driven and focused on integration behavior, API consumption, typed contracts, state/data-flow reasoning, edge cases, maintainability, loading/error/empty states, and code organization rather than obscure syntax or framework configuration
- The question must NOT include hints about specific implementation mechanisms. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to modern Java 21, Spring Boot, REST API, MongoDB, React, and TypeScript best practices for intermediate-level engineers
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Java documentation, Spring Boot documentation, MongoDB documentation, React documentation, TypeScript documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific full-stack engineering problem, rather than testing rote memorization
- Tasks should involve multi-layered full-stack challenges that require understanding of API contracts, backend layering, MongoDB access patterns, frontend state, typed data flow, and production maintainability
- Candidates will be encouraged to use AI to help with boilerplate and research, but not replace their own architectural judgment, debugging, and implementation skill

## Code Generation Instructions:
Based on the real-world scenarios provided, create a full-stack Java + MongoDB + React TypeScript DESIGN/BUILD task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency (3-6 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for genuine full-stack engineering skill
- Tests practical intermediate-level Java, REST API, MongoDB, React, and TypeScript skills in 1-2 deep implementation areas
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided above to ensure variety in task generation
- **CRITICAL**: The task must be a DESIGN/BUILD task. Do not generate a repair task, do not seed obvious broken behavior, and do not ask candidates to fix a named bug
- **CRITICAL**: The generated project must be COMPLETE, RUNNABLE, and WELL-STRUCTURED, while still leaving the core feature design and implementation for the candidate
- The backend MUST use Java 21, Maven, and Spring Boot style conventions with packages that separate controller, service, repository, model/document, dto, config, and exception concerns
- The frontend MUST use React with TypeScript, Vite, typed contracts, API client utilities, route/page-level components, reusable domain components, loading/error/empty states, and tests where useful
- The MongoDB initialization script MUST create collections, schema validation, indexes, and realistic seed data; generate bulk data programmatically in the init script rather than hand-writing hundreds of literal inserts
- The starter code must be substantial and realistic: do not ship only a small set of code or a single obvious file
- Do not include TODO comments, placeholder comments, or comments that reveal the solution
- Leave the core architectural decisions to the candidate: what contract shape, UI state structure, repository query shape, aggregation flow, validation boundary, and pagination/filtering behavior best satisfy the outcome
- The generated task must include a readiness run.sh that succeeds on the UNSOLVED starter and does not run grader tests that are expected to fail after scaffolding

## Infrastructure Requirements:
- MUST include docker-compose.yml with a MongoDB service used by the task itself
- MUST include a MongoDB initialization/migration file, such as mongo-init/init-mongo.js, that creates schema validation, indexes, application database user, and realistic seed data
- MUST include run.sh as a readiness gate that installs dependencies, starts MongoDB with `docker compose up -d`, waits for health, builds the Java backend and React frontend, and exits 0 on the UNSOLVED starter
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic and no project cleanup script is needed
- Application containers are not required; the Java and React projects may be built directly by run.sh using Maven and npm while MongoDB runs in Docker
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **CRITICAL**: The database comes from the task's own docker-compose.yml, never from the template
- **CRITICAL**: Initial deployment and readiness must succeed before candidate changes. The starter can be incomplete in feature behavior, but it must install, build, initialize MongoDB, and load successfully

### Docker-compose Instructions:
  - Include a MongoDB service only unless the selected scenario genuinely requires another datastore; do not invent extra services from the template datastore list
  - Use the official MongoDB image with authentication enabled through inline service environment values
  - MongoDB initialization MUST be performed through mounted `/docker-entrypoint-initdb.d/` scripts; do not create users or run seed scripts from run.sh
  - The MongoDB user, password, database, and authSource used by the Java backend configuration must match the initialization script exactly
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT use `.env` files or `${{VAR}}` host indirection** for datastore configuration; inline service environment values are required where the image needs them
  - For MongoDB, set inline initialization environment values such as `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, and `MONGO_INITDB_DATABASE`, and create the application user in the initialization script
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:27017:27017`
  - Include a healthcheck that uses `mongosh` with the configured credentials and database/authSource consistently
  - Mount the MongoDB initialization directory from /root/task into `/docker-entrypoint-initdb.d/`
  - Use named volumes for MongoDB data where needed, but ensure the initialization runs on a fresh volume in the readiness flow
  - **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else becomes bash's positional parameters and is silently dropped. Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`
  - Do not include application service containers unless the generated task explicitly provides a Dockerfile and the readiness budget remains safe

### MongoDB Initialization Instructions:
  - Create a file such as `mongo-init/init-mongo.js`
  - The initialization file MUST create the application database, application user, collections, schema validation rules, indexes, and seed data
  - Create several related collections appropriate to the selected scenario, such as customers, orders, payments, order_events, products, inventory_snapshots, support_cases, or equivalent domain-specific collections
  - Include real relationships using ObjectId references or embedded subsets where appropriate; model the tradeoff authentically for MongoDB rather than copying relational tables directly
  - Include status lifecycle fields, audit fields such as createdAt and updatedAt, and soft-delete or archive flags
  - Use Decimal128 for money values; never use floats for money
  - Seed hundreds to a few thousand documents programmatically with loops/generators
  - Include messy but consistent production-like content: nullable fields, near-duplicates, unicode names, apostrophes, timezone boundary timestamps, back-dated events, archived records, and boundary cases
  - Create baseline indexes that make the starter usable, but do not pre-solve every access pattern the candidate is expected to design
  - Include schema validation that is realistic but not so strict that the candidate cannot evolve the feature
  - Keep seed volume small enough to initialize in seconds on a small sandbox
  - Do not include comments that reveal the feature's intended implementation strategy or the optimal query/index design

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Installs task dependencies, starts MongoDB using `docker compose up -d`, waits for MongoDB readiness, builds the starter backend and frontend, and exits 0 on the UNSOLVED starter
  + FIRST STEP: Install the task's own third-party dependencies. For the Java backend, run Maven dependency/build commands from /root/task/backend. For the React TypeScript frontend, run `npm ci` from /root/task/frontend
  + WAIT MECHANISM: Implements a bounded wait loop that checks MongoDB health through docker compose or `mongosh` using localhost and the configured credentials
  + VALIDATION: Verifies MongoDB is accepting connections, the Java backend compiles with Maven, backend tests that are scaffold-safe can run or compile, and the React TypeScript frontend type-checks/builds
  + STARTER SAFETY: run.sh is a readiness/self-check, NOT the grader. It MUST NOT run a hidden grader suite or any test suite designed to fail until the candidate solves the task
  + EXIT CONTRACT: run.sh must exit 0 when the UNSOLVED starter can install, initialize MongoDB, compile, and build successfully; exit non-zero only when the scaffold cannot boot, dependencies cannot install, MongoDB cannot become healthy, or builds cannot run
  + DATABASE SETUP: User creation, schema creation, indexes, and seed data are executed automatically during MongoDB container initialization through `/docker-entrypoint-initdb.d/`; run.sh MUST NOT create users or manually execute seed scripts
  + MONITORING: Prints clear progress messages for dependency installation, container startup, health waiting, backend build, frontend build, and readiness completion
  + ERROR HANDLING: Includes proper error handling for failed dependency installs, container starts, database readiness, and build failures
  + LOCATION: All files are located in /root/task directory and all paths must reference this base directory
  + Use `docker compose`, not legacy `docker-compose`, unless compatibility fallback is explicitly needed

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below with exactly four markdown headings)
  - .gitignore (Standard full-stack Java, Maven, React, TypeScript, MongoDB, Docker, and IDE exclusions)
  - docker-compose.yml (MongoDB service only unless another datastore is truly required by the scenario)
  - run.sh (Readiness gate for installing dependencies, starting MongoDB, waiting for health, and building the starter)
  - mongo-init/init-mongo.js (MongoDB schema validation, indexes, app user creation, and realistic seed data)
  - backend/pom.xml (Maven build configuration for Java 21 and Spring Boot)
  - backend/src/main/java/com/example/task/Application.java (Spring Boot entry point)
  - backend/src/main/java/com/example/task/config/MongoConfig.java (MongoDB configuration aligned with docker-compose initialization)
  - backend/src/main/java/com/example/task/controller/FeatureController.java (REST controller foundation)
  - backend/src/main/java/com/example/task/service/FeatureService.java (Service layer foundation)
  - backend/src/main/java/com/example/task/repository/FeatureRepository.java (Spring Data MongoDB or MongoTemplate repository foundation)
  - backend/src/main/java/com/example/task/model/DomainDocument.java (Representative MongoDB document models)
  - backend/src/main/java/com/example/task/dto/ApiDtos.java (Request and response DTOs aligned with frontend contracts)
  - backend/src/main/java/com/example/task/exception/ApiExceptionHandler.java (Structured error response foundation)
  - backend/src/main/resources/application.yml (Local configuration with MongoDB connection values that match initialization)
  - backend/src/test/java/com/example/task/FeatureContractTest.java (Scaffold-safe test or contract smoke test)
  - frontend/package.json (React, TypeScript, Vite dependencies and scripts)
  - frontend/tsconfig.json (Strict TypeScript configuration)
  - frontend/vite.config.ts (Vite configuration)
  - frontend/index.html (Frontend entry point)
  - frontend/src/main.tsx (React entry point)
  - frontend/src/App.tsx (Application shell)
  - frontend/src/api/client.ts (Typed API client foundation)
  - frontend/src/contracts/api.ts (Typed frontend contract definitions aligned with backend DTOs)
  - frontend/src/pages/FeaturePage.tsx (Feature page foundation)
  - frontend/src/components/FeaturePanel.tsx (Reusable feature component foundation)
  - frontend/src/components/ResultList.tsx (Reusable result display foundation)
  - frontend/src/hooks/useFeatureData.ts (Data-flow hook foundation)
  - frontend/src/styles.css (Basic styling)
  - shared/api-contracts/order-contracts.ts (Shared or mirrored TypeScript API contract file when useful for the selected scenario)

## Code file requirements:
- Use realistic file paths and names that follow Java Spring Boot, Maven, React, TypeScript, Vite, and MongoDB conventions
- Code should follow modern best practices and demonstrate intermediate-level patterns for the chosen stack
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion in the 1-2 focused feature areas
- Include existing routes/controllers, services, repository abstractions, DTOs, frontend components, hooks, API client code, and contract files that need to be extended or integrated
- The core architectural decisions that the candidate needs to make MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add cursor pagination here", "Implement aggregation here", "Use this index", "Add this hook", or "Create this component"
- DO NOT add comments that give away hints, solution, or implementation details
- The generated project structure should be runnable locally, but will require architectural work to satisfy the task
- Provide pinned, realistic dependencies in backend/pom.xml and frontend/package.json that intermediate developers should be familiar with
- Java code must use Java 21 and Spring Boot style practices, with clear controller/service/repository separation
- REST endpoints must use meaningful resource-oriented API design and structured JSON responses, but the question and README must not reveal exact implementation mechanics
- MongoDB access should use Spring Data MongoDB repositories and/or MongoTemplate in a way appropriate to the scenario
- Frontend code must use React functional components with hooks and TypeScript types
- The frontend and backend contract representations must be aligned enough that the candidate can reason about request/response shape without duplicating inconsistent models
- Include OpenAPI or a lightweight contract artifact only if it helps the scenario; do not let generated documentation reveal the solution
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for a Java Spring Boot, Maven, React, TypeScript, MongoDB, and Docker full-stack project that includes:
- Maven build directories and artifacts such as target/, *.class, *.jar, *.war
- Node and frontend artifacts such as node_modules/, dist/, build/, coverage/, .vite/
- IDE files such as .idea/, .vscode/, *.iml, .classpath, .project, .settings/
- Environment files such as .env, .env.local, .env.*.local
- Log files such as *.log and logs/
- MongoDB data directories and local Docker volume directories
- OS-specific files such as .DS_Store and Thumbs.db
- Temporary files, cache directories, and coverage reports
- Any other standard exclusions for Java/Spring Boot, React/TypeScript, MongoDB, Maven, npm, and Docker development

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this order and NO others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four README sections MUST be emitted as an actual markdown heading using the same heading level consistently, for example:
## Task Overview
## Objectives
## Helpful Tips
## How to Verify

A plain unmarked text line with the section name is INVALID and counts as a missing section. Do not add Database Access, Initial Setup Status, Application Access, Architecture, Implementation Notes, or NOT TO INCLUDE as README sections.

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences. No bullet list.
It must describe the business scenario, current state, and why the full-stack feature matters. It must explain that the project is a realistic Java Spring Boot + MongoDB + React TypeScript system where the candidate is building or reworking a product capability across layers.
NEVER generate empty content — always provide substantial business context. Do NOT include bold time-budget callouts.

### Objectives
For this INTERMEDIATE DESIGN/BUILD task, Objectives MUST be concise, open-ended, plain goal statements:
- Use 3-4 bullets max; fewer, tighter is better
- Each objective is ONE SHORT PLAIN SENTENCE, roughly 10-15 words
- Do not use stakeholder framing for this DESIGN/BUILD task
- Name the outcome the system must achieve, not the mechanism that achieves it
- Imperative mood is correct here
- One concern per bullet; split a bullet that bundles two separable concerns
- Do NOT name APIs, libraries, framework features, patterns, algorithms, config knobs, files, file paths, directories, functions, methods, classes, variables, collections, indexes, or direct code references
- Do NOT describe current-vs-after behavior
- If a bullet could be pasted into the codebase as the change description, it is too specific

GOOD design/build objective examples:
- Build a customer workflow that remains useful as account history grows.
- Keep financial and status information consistent across every visible layer.
- Make the feature understandable when records are missing, delayed, or archived.
- Preserve clear contracts between the browser experience and backend data.

BAD objective examples:
- Add a compound index on customerId, status, createdAt, and _id.
- Replace skip pagination with cursor pagination in OrderRepository.
- Use React Query to cache order responses.
- Implement GET /api/v1/customers/{{customerId}}/orders/history.

### Helpful Tips
Provide practical guidance without revealing specific implementations:
- Use 4-5 bullets max
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze"
- Tips guide discovery and tradeoff thinking
- Tips MUST NOT name the specific API, library, function, pattern, data structure, index, aggregation stage, hook, component, endpoint, or algorithm that solves the task
- Tips may point candidates toward cross-layer consistency, data shape, user experience under edge cases, and observable behavior without naming how to implement it

### How to Verify
Frame verification in terms of experiments the candidate can run and where to look. Because this is a DESIGN/BUILD task, the bullets name an experiment to run and where to look, and MUST NOT state what the correct result is.
- Use 3-5 bullets max
- One probe per Objective where possible, in the same order
- Pattern: "<make this change or perform this action>, and <where to look>"
- Do NOT state the pass condition or implementation-specific result
- At most ONE bullet may reference the task environment directly
- Before emitting, read the Objectives and How to Verify together as a candidate would: between them they must still not give away any rule the candidate is meant to derive

GOOD design/build verification probe examples:
- Load an older customer account, vary the visible filters, and compare the browser view with the API response.
- Add records near a status boundary, and inspect how the workflow presents them.
- Change only the browser contract assumptions, and check where the mismatch appears.
- Restart the local stack, open the feature, and review the backend logs for the request path.

BAD design/build verification probes:
- Confirm that the API returns a nextCursor field based on createdAt and _id.
- Verify that the new compound index is used by explain().
- Check that archived orders are excluded from every page.
- Ensure the React hook uses AbortController during request changes.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
Keep the following OUT of the README entirely:
- Setup commands such as `npm install`, `npm ci`, `npm run build`, `mvn test`, `mvn spring-boot:run`, `docker compose up`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Database connection details such as host, port, username, password, connection strings, or client-tool suggestions
- Specific APIs, method names, library names, pattern names, aggregation stages, index definitions, hook names, component names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- File names, file paths, directories, function names, method names, class names, collection names, or field names that reveal where to make the change
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", or "configure the following"

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "A short kebab-case GitHub repository name under 50 characters that reflects the selected full-stack business feature without exposing the implementation mechanism.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, describing the full-stack feature outcome in plain English.",
  "question": "A candidate-facing scenario paragraph plus direct imperative ask at the same altitude as the README Objectives. Use plain prose with no bullets: first state who the candidate is and what system they are working on, then describe that the existing monorepo and MongoDB data are present but the product capability is not yet trustworthy or complete, then ask them to rework or build the feature so the outcomes are achieved. Do NOT leak the answer: no file names, paths, endpoint names, function or method references, collection names, field names, index names, aggregation stages, library APIs, or direct solution statements.",
  "code_files": {{{{
    "README.md": "Candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "Comprehensive full-stack exclusions for Java, Maven, React, TypeScript, npm, MongoDB local data, Docker artifacts, logs, IDE files, operating-system files, caches, and coverage reports.",
    "docker-compose.yml": "Docker Compose file with no version key, a localhost-only MongoDB port binding, inline MongoDB initialization environment values, a healthcheck, named volume, and mounted initialization directory.",
    "run.sh": "Executable readiness gate that installs backend and frontend dependencies, starts MongoDB with docker compose, waits for database health, builds the Java backend and React TypeScript frontend, and exits 0 on the unsolved starter when the scaffold is deployable.",
    "mongo-init/init-mongo.js": "MongoDB initialization and migration script that creates the application database user, schema validation, related collections, indexes, and realistic programmatically generated seed data with production-like messy but internally consistent records.",
    "backend/pom.xml": "Maven build configuration for Java 21, Spring Boot, Spring Web, Spring Data MongoDB, validation, logging, testing, and any scenario-appropriate dependencies with pinned versions or managed Spring Boot versions.",
    "backend/src/main/java/com/example/task/Application.java": "Spring Boot application entry point for the backend service.",
    "backend/src/main/java/com/example/task/config/MongoConfig.java": "MongoDB configuration class or property binding aligned with the docker-compose database, user, and authSource values.",
    "backend/src/main/java/com/example/task/controller/FeatureController.java": "REST controller foundation that exposes the selected business feature at a resource-oriented boundary without containing the final implementation answer.",
    "backend/src/main/java/com/example/task/service/FeatureService.java": "Service layer foundation containing domain orchestration structure and leaving the key design work for the candidate.",
    "backend/src/main/java/com/example/task/repository/FeatureRepository.java": "Repository or data-access abstraction for MongoDB queries and aggregations, structured so the candidate must make appropriate data-access decisions.",
    "backend/src/main/java/com/example/task/model/CustomerDocument.java": "Representative MongoDB document model for a primary domain entity, using realistic fields, audit data, and validation annotations where appropriate.",
    "backend/src/main/java/com/example/task/model/OrderDocument.java": "Representative MongoDB document model for a related domain entity, using exact-money representation and status lifecycle fields where the selected scenario fits.",
    "backend/src/main/java/com/example/task/model/PaymentDocument.java": "Representative MongoDB document model for financial or operational records related to the selected scenario.",
    "backend/src/main/java/com/example/task/model/EventDocument.java": "Representative MongoDB document model for status, audit, or lifecycle events related to the selected scenario.",
    "backend/src/main/java/com/example/task/dto/FeatureRequest.java": "Request DTO foundation for the feature with validation structure but without revealing the complete solution design.",
    "backend/src/main/java/com/example/task/dto/FeatureResponse.java": "Response DTO foundation aligned with the frontend contract while leaving candidate-level contract refinement to the task.",
    "backend/src/main/java/com/example/task/dto/ErrorResponse.java": "Structured error response DTO for consistent REST API errors.",
    "backend/src/main/java/com/example/task/exception/ApiExceptionHandler.java": "Central exception handler foundation for validation, domain, and infrastructure failures.",
    "backend/src/main/resources/application.yml": "Spring Boot local configuration with MongoDB connection settings that match docker-compose and initialization credentials, using safe local defaults.",
    "backend/src/test/java/com/example/task/FeatureContractTest.java": "Scaffold-safe backend test or smoke test that validates the starter application context and contract shape without giving away the solution.",
    "frontend/package.json": "React, TypeScript, Vite, linting, type-check, build, and test script manifest with realistic pinned or compatible dependency versions.",
    "frontend/tsconfig.json": "Strict TypeScript configuration suitable for a Vite React application.",
    "frontend/vite.config.ts": "Vite configuration for the React TypeScript frontend.",
    "frontend/index.html": "HTML entry point for the frontend application.",
    "frontend/src/main.tsx": "React application bootstrap file.",
    "frontend/src/App.tsx": "Application shell that routes or composes the selected feature page without containing the final feature answer.",
    "frontend/src/api/client.ts": "Typed API client foundation for communicating with the Java backend while leaving key behavior decisions to the candidate.",
    "frontend/src/contracts/api.ts": "Frontend TypeScript contract definitions aligned with the backend DTO intent and suitable for shared typed API reasoning.",
    "frontend/src/pages/FeaturePage.tsx": "Feature page foundation for the selected business workflow with realistic loading, empty, and error state structure left for candidate completion.",
    "frontend/src/components/FeaturePanel.tsx": "Reusable domain component foundation for the feature workflow.",
    "frontend/src/components/ResultList.tsx": "Reusable result presentation component foundation for data returned by the backend.",
    "frontend/src/components/FilterControls.tsx": "Reusable filtering or selection component foundation when the selected scenario needs user-controlled narrowing.",
    "frontend/src/hooks/useFeatureData.ts": "Custom hook foundation for feature data flow and API integration without revealing the complete state strategy.",
    "frontend/src/styles.css": "Basic maintainable styling for the starter UI.",
    "shared/api-contracts/order-contracts.ts": "Shared or mirrored TypeScript contract artifact used to keep frontend-facing types explicit and aligned with the backend API contract when appropriate to the selected scenario."
  }}}},
  "answer": "Evaluator-facing high-level solution approach describing the expected architectural direction across React TypeScript UI, typed contracts, Java Spring controller/service/repository layers, REST semantics, MongoDB schema/query/index choices, validation, and observability without requiring one exact implementation.",
  "definitions": "An object of term-to-definition pairs for important concepts in this task, such as REST resource modeling, DTO, schema validation, aggregation pipeline, compound index, seek pagination, Decimal128, audit fields, soft delete, typed contract, and service layer.",
  "hints": "A single line hint that nudges the candidate to reason across the browser contract, API boundary, and MongoDB access pattern without revealing the specific implementation, endpoint, index, aggregation, hook, or data model change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable product behavior, cross-layer consistency, production-quality code, and maintainable full-stack architecture. Use simple english. Include one line stating that the submission writes production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Java 21 and Maven proficiency, comfort with Spring Boot REST APIs, familiarity with MongoDB modeling and queries, and React TypeScript experience. Do not include setup commands or verification steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first describe what the system does and its current product situation, second open with 'This rework needs to ...' or 'This calls for ...' and state outcomes without mechanisms, third state what separates a strong submission and close on whether the design reasoning is sound."
}}}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case, under 50 characters, and different from title
3. **title** must be human-readable, 50-80 characters, and in `<action verb> <subject>` format
4. **question** must be outcome-altitude prose and must not leak file names, paths, endpoint names, collection names, field names, methods, classes, indexes, aggregation stages, or direct solution mechanisms
5. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, mongo-init/init-mongo.js, backend Maven files, Java source files, frontend React TypeScript files, and contract files with real concrete paths
6. **code_files** keys must be real file paths with real extensions; do not emit placeholder-style keys such as additional_files, supporting_scripts, selected_stack_manifest_and_source, or files_as_needed
7. **README.md** must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as an actual markdown heading
8. **README.md** must not contain setup commands, database connection details, direct solutions, implementation guides, specific APIs, file paths, code snippets, or any NOT TO INCLUDE heading
9. **Design/build README rules apply**: Objectives are short plain goal statements, and How to Verify uses probe-style experiments without stating the correct result
10. **Infrastructure shape is mandatory**: include docker-compose.yml for MongoDB and run.sh; do not include kill.sh
11. **docker-compose.yml** must not include a version key and must bind MongoDB to localhost only with `127.0.0.1:27017:27017`
12. **MongoDB initialization** must be done by `/docker-entrypoint-initdb.d/` scripts, not by run.sh
13. **run.sh** must install dependencies first, start MongoDB, wait for health, build the Java backend and React frontend, and exit 0 on the UNSOLVED starter
14. **Starter code** must be substantial, realistic, multi-module, and runnable, but must not contain the solution or comments that reveal the solution
15. **Production realism is required**: several related collections, schema validation, status lifecycles, audit fields, indexes, realistic generated seed volume, messy consistent data, and safe readiness performance
16. **Task must be completable within the allocated time** for INTERMEDIATE proficiency while still reflecting 3-6 years of full-stack engineering experience
17. **outcomes** must include one bullet or line on production-level clean code with best practices, design patterns, naming conventions, exception handling, logging, and observability
18. **short_overview** must be exactly three bullets in plain non-technical business English, must not instruct the candidate, and must not enumerate solution mechanisms
19. **pre_requisites** must contain assumed knowledge only and never imperative setup or verify steps
20. **hints** must be a single line and must not reveal the implementation
"""

PROMPT_REGISTRY = {
    "Java (INTERMEDIATE), MongoDB (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_CONTEXT,
        PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_JAVA_MONGODB_REST_REACT_TYPESCRIPT_INTERMEDIATE_INSTRUCTIONS,
    ],
}