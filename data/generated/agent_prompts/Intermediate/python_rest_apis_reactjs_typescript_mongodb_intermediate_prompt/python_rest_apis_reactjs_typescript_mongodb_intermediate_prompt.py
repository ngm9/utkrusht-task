# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a full-stack Python REST API, React, TypeScript, and MongoDB assessment task.

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
- This must be a full-stack DESIGN/BUILD task, not a repair task: the candidate builds or reworks a feature end to end across a React + TypeScript frontend, a Python REST API backend, and a MongoDB database

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and full-stack product capability the candidate will build or rework)
2. What will the task look like? (Describe the Python REST API, React + TypeScript frontend, MongoDB schema/data work, expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python REST APIs, React, TypeScript, and MongoDB, you are given a list of real world scenarios and proficiency levels for full-stack application development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an **INTERMEDIATE LEVEL (3-5 years of experience)**.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL local full-stack starter project that installs, starts its MongoDB datastore, builds the frontend, loads the backend application, and passes the readiness gate even though the product capability is intentionally incomplete.

The generated repository MUST include:
- A React 18 + TypeScript frontend using a realistic multi-module layout with typed contracts shared with, or derived from, the backend contract surface
- A Python 3 REST API backend using FastAPI or Flask with a clear router -> service -> repository layering
- A MongoDB datastore created by this task's own docker-compose.yml, not by the runtime template
- A MongoDB init/migration file that creates collections, JSON Schema validators, indexes, users, and realistic seed data
- A run.sh readiness gate that installs dependencies, starts MongoDB with docker compose, waits for health, validates the starter can build/load, and exits 0 on the UNSOLVED starter
- A kill.sh cleanup script because this full-stack task explicitly ships one as part of the requested assessment artifact set

**CRITICAL**: This is a DESIGN/BUILD task, not a repair task. Nothing should be framed as a known production defect with a hidden root cause. The candidate is expected to extend or rework the feature so that the system reaches a production-ready standard while making their own design decisions.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or rework one meaningful end-to-end feature across the frontend, backend REST API, and MongoDB datastore.
- **CRITICAL — Design/Build Shape**: Do NOT generate a repair task, bug hunt, or "find the broken file" exercise. The task should provide a working scaffold and ask the candidate to complete a product capability to a clear standard.
- **CRITICAL — Outcome Altitude**: The candidate-facing question, README Objectives, README How to Verify, and short_overview must describe outcomes, not the concrete implementation rules that would solve the task.
- The frontend must be React with TypeScript and should consume the Python REST API through typed contracts. Use shared TypeScript interfaces, an OpenAPI-derived contract, or a clearly maintained contract module, but do not reveal the candidate's exact solution strategy.
- The backend must be Python 3 using FastAPI or Flask. It MUST demonstrate router -> service -> repository layering in the starter project, with enough existing modules that the candidate must read more than one file before changing behavior.
- The MongoDB work must be meaningful and naturally connected to the feature: resource modeling, validation, indexes, aggregation, pagination, filtering, audit fields, status lifecycle, or consistency checks may be relevant depending on the selected scenario.
- **CRITICAL — Intermediate Codebase Size**: The starter codebase MUST be substantial and realistic, NOT a toy snippet. Require MULTIPLE interacting modules/files in a real project layout, with non-trivial existing logic the candidate must read and reason about before changing. Changes should naturally span MORE THAN ONE file.
- **CRITICAL — Production Realism**: The task must feel like an afternoon inside a real production repository, not a short classroom exercise. Include realistic conventions, meaningful separation of concerns, configuration, error handling, validation boundaries, and project structure.
- Keep the task focused on 1-2 major design/build areas. Do NOT create a checklist of unrelated features such as auth, rate limiting, caching, charts, exports, and admin screens all at once.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The starter code must not put the most relevant logic in the first file opened. The candidate should need to navigate frontend components/hooks, backend route/service/repository modules, and MongoDB seed/model assumptions.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Python, REST API, React, TypeScript, and MongoDB best practices.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

**PRODUCTION REALISM REQUIREMENTS FOR DATA**:
- MongoDB must include several related collections with real relationships, lifecycle statuses, audit fields such as createdAt and updatedAt, soft-delete or archived markers, and indexes. Never use one flat collection.
- Seed enough rows that the answer CANNOT be seen by eyeballing the seed file. The candidate must query, aggregate, inspect data shape, or reason about access patterns. Hundreds to a few thousand documents is the right order of magnitude.
- Generate high-volume seed content programmatically inside the init/migration file using loops or helper functions, not by hand-writing thousands of literal documents.
- Include production mess that remains internally consistent: nullable fields, near-duplicates, soft-deleted rows, unicode and apostrophes in names, timestamps crossing day and timezone boundaries, exact decimal money values using MongoDB Decimal128, out-of-order or back-dated sequences, and boundary rows for the selected business rule.
- Keep foreign-key-like references resolvable, totals reconcilable, statuses in a legal lifecycle, and audit metadata coherent. A candidate who investigates must find a coherent world, not random noise.
- Realistic SHAPE and realistic MESS are what matter, not raw volume. Everything must still install, build, seed and start inside run.sh's time budget on a small sandbox.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, FastAPI or Flask documentation, React documentation, TypeScript documentation, MongoDB documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate full-stack engineering proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution for a production-like full-stack feature.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a full-stack Python REST API, React, TypeScript, and MongoDB task that:
- Draws inspiration from the input_scenarios given to determine the business context, technical requirements, and domain vocabulary
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed
- Tests practical Python modularity, REST resource design, React component/state structure, TypeScript contract safety, and MongoDB data modeling/query design in one coherent feature
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- Uses Python 3 for the backend REST API, preferably FastAPI unless the selected scenario strongly favors Flask
- Uses a React + TypeScript frontend with a conventional Vite or comparable local build setup
- Uses MongoDB through PyMongo or Motor from the Python backend, with repository modules isolating database access
- Includes starter source files that are valid and executable but leave the core product decisions and feature completion to the candidate
- Includes a realistic monorepo-style structure with backend/, frontend/, shared/ or contracts/, db/, and scripts as appropriate
- Requires the backend API design to use resource-oriented routes, meaningful status codes, consistent JSON response shapes, request validation, and structured error handling
- Requires the frontend to handle data fetching, typed request/response boundaries, state transitions, loading/error/empty states, and user-facing presentation without hard-coding the answer
- Requires MongoDB collections, validators, indexes, and seed data that support the business domain and give the candidate realistic data to inspect
- Avoids framework trivia and installation mechanics as the assessment focus; configuration exists so the candidate can spend time on engineering decisions

**CRITICAL — Design/Build README Alignment**:
- Because this is a DESIGN/BUILD task, README Objectives must be short plain goal statements, not stakeholder-framed repair objectives.
- Because this is a DESIGN/BUILD task, README How to Verify must use probe-style checks: each bullet names an experiment to run and where to look, without stating the correct result.
- The "question" and "short_overview" fields must stay at the same outcome altitude as the README Objectives. They must NOT enumerate hidden rules, exact implementation steps, specific endpoints, file paths, function names, indexes, aggregation stages, or collection names as direct solution instructions.

## Infrastructure Requirements
- MUST include docker-compose.yml for MongoDB. The database comes from the task's own docker-compose.yml, never from the template.
- MUST include a MongoDB init/migration file, for example `db/init_mongo.js`, mounted into `/docker-entrypoint-initdb.d/`, that creates the application database, creates the application user, creates collections with validators, creates indexes, and seeds realistic data.
- MUST include run.sh as a readiness/self-check script, not the grader. It brings MongoDB up, waits for health, installs dependencies, verifies the starter builds/loads, and exits 0 on the UNSOLVED starter.
- MUST include kill.sh as a cleanup script for this requested full-stack task artifact set.
- No application container is required unless the selected scenario truly needs one. Prefer local frontend/backend project files plus MongoDB in Compose so the readiness gate remains fast and clear.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- Infrastructure must be automated and reliable in a small E2B sandbox. Do not require manual database setup, manual user creation, or template-provided datastore services.
- Do NOT include `init_database.sql`; this is a MongoDB task and must use a MongoDB JavaScript initialization/migration file instead.

### Docker-compose Instructions
- docker-compose.yml MUST define a MongoDB service only unless an app container is explicitly justified by the selected scenario.
- **MUST NOT include any version specification** in docker-compose.yml.
- MongoDB ports MUST be exposed only to localhost.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:27017:27017`.
- The MongoDB service MUST include inline initialization environment values, not `.env` indirection. Use `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, and `MONGO_INITDB_DATABASE` inline in the MongoDB service.
- Forbid `.env` files or `${{VAR}}` host indirection in docker-compose.yml. Inline service environment values are required because the image will not initialize correctly without them.
- The init script, healthcheck, and backend connection string must use consistent database, username, password, and authSource values.
- The MongoDB application user the Python backend authenticates as MUST be created DURING MongoDB container initialization by the mounted init script. Do NOT create database users from run.sh.
- Mount the init/migration file into `/docker-entrypoint-initdb.d/` so MongoDB initializes the database automatically on first start.
- Use a named volume for MongoDB data. Do not bind-mount data into source directories that could pollute the task.
- Include a healthcheck that uses mongosh and authenticates consistently with the configured root or application user.
- Use a project-specific container name or compose project name only if it helps cleanup; avoid hard-coded paths outside /root/task.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else (flags, paths, `&&`, the rest of the pipeline) becomes bash's positional parameters and is silently dropped (e.g. `mkdir -p /a && tail -f /dev/null` breaks into `mkdir: missing operand`). Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.
- Do not add Redis, PostgreSQL, MySQL, queues, search engines, or other datastores unless the selected real-world scenario explicitly requires them. For this task family, MongoDB should be the exercised datastore.

### MongoDB init/migration file Instructions
- Create a MongoDB JavaScript init/migration file such as `db/init_mongo.js`.
- The file must create the app database, create the app user and roles, define collections, apply JSON Schema validators, create indexes, and seed realistic data.
- The schema should include several related collections appropriate to the selected domain, for example domain entities, actors, events/activities, financial or status records, and audit/history records.
- Include lifecycle status fields, createdAt, updatedAt, nullable deletedAt or archivedAt fields, and relationship identifiers between collections.
- Use MongoDB Decimal128 for money-like values. Do not use floats for currency.
- Generate hundreds to a few thousand internally consistent documents programmatically using loops/helper functions in the init file.
- Include nullable values, near-duplicates, unicode names, apostrophes, timezone boundary timestamps, soft-deleted/archived records, back-dated sequences, and boundary cases tied to the business domain.
- Create indexes that represent the starter system's reasonable baseline, but do not encode the candidate's entire solution. The candidate should still need to make design/build decisions.
- The init/migration file must not contain comments or names that reveal the desired solution. Avoid labels such as "index needed by the candidate" or "slow query fix".
- The file must be safe to run during MongoDB container initialization and must not depend on external network access.

### Run.sh Instructions
- run.sh MUST be located at `/root/task/run.sh` and must use `/root/task` as the working directory.
- run.sh's FIRST steps MUST install the task's own third-party dependencies because the template only pre-installs primary runtimes, not project dependencies.
- For the frontend, run the native Node install command such as `npm ci` from `/root/task/frontend` when package-lock.json is included, or the equivalent manifest install command chosen for the generated project.
- For the backend, run `python -m pip install -q -r /root/task/backend/requirements.txt`.
- run.sh MUST start MongoDB with `docker compose -f /root/task/docker-compose.yml up -d`.
- run.sh MUST wait for MongoDB readiness using a bounded loop and an authenticated mongosh ping or equivalent health probe.
- run.sh MUST NOT create users or run seed scripts manually. User creation, collection creation, indexes, and seed data are performed by MongoDB initialization through `/docker-entrypoint-initdb.d/`.
- run.sh MUST validate that the starter frontend builds, for example by running the configured TypeScript build command. This build must succeed on the UNSOLVED starter.
- run.sh MUST validate that the backend imports or loads successfully, for example by importing the app object or running a lightweight route listing/smoke command that does not require the candidate's unfinished feature to work.
- run.sh MUST NOT run the grader test suite or any tests designed to fail until the candidate solves the task.
- run.sh MUST exit 0 when dependencies install, MongoDB is healthy, seed data exists, the frontend builds, and the backend loads on the UNSOLVED starter.
- Include clear logging and bounded timeouts. Fail non-zero only when the scaffold cannot install, start, build, or load.
- Use `docker compose`, not legacy `docker-compose`, unless compatibility fallback is added safely.
- All connection details used by run.sh must use `localhost`, not a droplet IP or remote host placeholder.

kill.sh requirements to include in code_files:
- kill.sh MUST stop and remove the compose stack, volumes, and task-related containers/networks.
- It must be idempotent and safe to run multiple times, using `|| true` for cleanup steps that may already be complete.
- It should remove MongoDB volumes created by the task and clean local generated dependency/build artifacts where appropriate.
- It should not depend on a droplet IP or remote environment.
- It should print clear progress logs.
- Because this task explicitly asks for kill.sh, include it even though run.sh is the main readiness gate.

### Dockerfile Instructions
Omit Dockerfile unless the selected scenario explicitly requires an application container. If a Dockerfile is included, it must be justified by the task scenario, must use /root/task as the working directory, must not install the primary runtime through apt-get, and must not depend on `.env` indirection for datastore initialization.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (MongoDB service only unless an app container is justified; no version key; localhost-only port binding)
  - db/init_mongo.js (MongoDB init/migration file that creates schema, users, indexes, and realistic seed data)
  - run.sh (readiness gate that installs deps, starts MongoDB, waits for health, builds/loads starter, exits 0 on unsolved starter)
  - kill.sh (idempotent cleanup script requested for this full-stack task)
  - backend/requirements.txt (Python dependencies including FastAPI or Flask, PyMongo or Motor, validation/config libraries, and test utilities if included)
  - backend/app/main.py (Python REST API application entrypoint)
  - backend/app/api/routes.py (router layer exposing resource-oriented API routes)
  - backend/app/services/feature_service.py (service layer coordinating domain behavior without revealing the final design)
  - backend/app/repositories/feature_repository.py (repository layer isolating MongoDB access)
  - backend/app/models/schemas.py (request/response schemas or validation models)
  - backend/app/core/config.py (local configuration with safe defaults for localhost MongoDB)
  - frontend/package.json (React + TypeScript dependency manifest and scripts)
  - frontend/tsconfig.json (strict TypeScript configuration)
  - frontend/vite.config.ts (Vite configuration for React TypeScript)
  - frontend/src/main.tsx (React entrypoint)
  - frontend/src/App.tsx (application shell)
  - frontend/src/api/client.ts (API client boundary)
  - frontend/src/contracts/api.ts (shared or generated typed contract surface used by the frontend)
  - frontend/src/components/FeatureView.tsx (representative feature UI component)
  - frontend/src/hooks/useFeatureData.ts (frontend data/state hook)
  - frontend/src/styles.css (minimal styling if needed)
  - .gitignore (standard Python, Node, MongoDB, Docker, environment, IDE, logs, coverage, and build exclusions)
  - Any additional concrete files required for a realistic full-stack starter project. Every additional key must be a real filepath with a real extension, never a placeholder key.

## Code file requirements
- Use realistic file paths and names that follow the conventions of Python backend projects, React + TypeScript frontend projects, and MongoDB initialization.
- Code should follow Python PEP 8 guidelines and modern TypeScript/React best practices.
- Use functional React components with hooks exclusively.
- Use TypeScript strictly enough to assess contract thinking, including meaningful interfaces, union types, type guards, or generics where they naturally fit.
- The backend must use router -> service -> repository layering. Do not collapse business logic directly into route handlers.
- MongoDB access must be isolated in repository modules using PyMongo or Motor. Do not scatter database calls throughout route handlers or frontend code.
- The generated project structure should be runnable locally, but the feature should require meaningful design/build work to be complete.
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should provide comprehensive boilerplate, proper project architecture, existing supporting flows, and foundation code.
- For design/build tasks, starter stubs may provide safe minimal behavior but must not reveal the final algorithm, exact aggregation, exact index strategy, or frontend architecture the candidate should choose.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- DO NOT include comments like "Add aggregation here", "Implement filtering here", "Use this index", "Add this hook", "Call this endpoint", or "Solution goes here".
- Do not put direct solution instructions in docstrings, variable names, fixture names, seed labels, or test names.
- Include realistic dependency manifests with pinned versions. Pin Python dependencies in requirements.txt and Node dependencies in package-lock.json if emitted.
- Include enough existing frontend and backend files that an intermediate engineer must navigate a meaningful codebase, not edit one obvious file.
- Include minimal tests only if they support the task without revealing the solution. If included, run.sh must not fail merely because candidate-facing tests are red by design.
- No generated file may contain a droplet IP placeholder. Use localhost wherever host access is needed.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore file that covers all standard exclusions for this full-stack project, including:
- Python files and folders: `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.venv/`, `venv/`
- Node and React files: `node_modules/`, `dist/`, `build/`, `.vite/`, npm/yarn/pnpm debug logs
- Environment and secrets: `.env`, `.env.*`, except do not require `.env` for MongoDB startup
- Logs and runtime artifacts: `*.log`, `logs/`, temporary files
- Coverage and test artifacts: `coverage/`, `.coverage`, `htmlcov/`
- Docker and MongoDB local data artifacts: `.docker/`, `mongo-data/`, `data/mongo/`
- IDE/editor and OS files: `.vscode/`, `.idea/`, `.DS_Store`, `Thumbs.db`, swap files
- Any generated contract/build artifacts that should not be committed unless the task intentionally needs them

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this exact order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four sections MUST be emitted as an actual markdown heading using the same heading level consistently:
- `## Task Overview`
- `## Objectives`
- `## Helpful Tips`
- `## How to Verify`

A plain unmarked text line with the section name is INVALID and counts as a missing section.

The README.md file content MUST be fully populated with meaningful, specific content relevant to the generated full-stack design/build task. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the selected real-world scenario. Use concrete business context, not generic descriptions.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences.
- No bullet list in Task Overview.
- It must describe the business scenario, current state, and why the problem matters.
- It must make clear that a working starter exists and the candidate is building or reworking an end-to-end capability.
- It must NEVER be empty.
- It must contain NO bold time-budget callouts.
- It must not name specific files, directories, functions, methods, indexes, aggregation stages, or direct solution mechanisms.

### Objectives
- Because this is an INTERMEDIATE DESIGN/BUILD task, Objectives MUST be concise and OPEN-ENDED.
- Include 3-4 bullets max; fewer and tighter is better.
- Because this is a DESIGN/BUILD task, each objective is ONE SHORT PLAIN SENTENCE, roughly 10-15 words.
- Use plain goal statements, not stakeholder framing and not before/after repair phrasing.
- Imperative mood is correct here.
- Each bullet should name the outcome the system must achieve, not the mechanism.
- One concern per bullet; split a bullet that bundles two separable concerns.
- Do NOT name any API path, library, framework API, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, collection, index, or direct code reference.
- Do NOT describe the current broken behavior or use phrasing like "currently does X" / "after your changes".
- GOOD design/build objective style: "Build a workflow that makes schedule summaries reliable across realistic clinic data."
- GOOD design/build objective style: "Keep the user experience clear when data is incomplete or delayed."
- BAD design/build objective style: "Add an aggregation pipeline with early match and group by clinicId."
- BAD design/build objective style: "A change to the repository should create the compound index."

### Helpful Tips
Provide practical guidance without revealing specific implementations:
- Helpful Tips must include 4-5 bullets max.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips must guide discovery and must NOT name the specific API, library function, MongoDB stage, index shape, React hook, component pattern, data structure, endpoint path, file name, or algorithm that solves the task.
- Tips may encourage thinking about data boundaries, contracts, state ownership, validation, and observability without prescribing how to implement them.
- Tips must not include setup commands.

### How to Verify
- How to Verify must include 3-5 bullets max.
- Because this is a DESIGN/BUILD task, the bullets must name an EXPERIMENT TO RUN and where to look, and MUST NOT state what the correct result is.
- Pattern: "<make this change or try this interaction>, and <where to look>".
- Include one probe per Objective where possible, in the same order.
- Do NOT state pass conditions that reveal the hidden implementation rule.
- At most ONE bullet may reference the task environment directly.
- Frame verification in terms of observable outcomes. Describe WHAT to inspect or exercise, not the specific implementation to write.
- Before emitting, read the Objectives and How to Verify TOGETHER as a candidate would: between them they must still not give away any rule the candidate is meant to derive.
- GOOD design/build probe: "Change the date range in the interface, and compare the view with the API response."
- GOOD design/build probe: "Introduce incomplete seeded records, and inspect how the page and response behave."
- BAD design/build probe: "The endpoint should use a compound index and return grouped counts by local day."
- BAD design/build probe: "Each query should avoid COLLSCAN and use IXSCAN."

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
The following guidance is an instruction to you, the task generator, about what to keep OUT of README.md. Do NOT emit this as a README heading or README section.
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `pytest`, or `npm run build`
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, MongoDB stages, index definitions, React hooks, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this aggregation", or "use this API"
- Database connection details such as host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Any heading named "NOT TO INCLUDE", "CONTENT TO EXCLUDE", "Database Access", "Database Schema Overview", "Setup", "Installation", or similar

## REQUIRED OUTPUT JSON STRUCTURE
The generated response must be valid JSON only and must match this structure exactly. Each value below describes what you must fill in; do not copy placeholder examples literally.

{{
  "name": "A short kebab-case GitHub repository name under 50 characters that reflects the selected full-stack product capability without mentioning hidden implementation details.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, describing the full-stack feature work in plain English.",
  "question": "A full candidate-facing task description written as one scenario paragraph followed by a direct imperative ask, at the same outcome altitude as the README Objectives; state who the candidate is, what full-stack system exists, that it runs but needs a more trustworthy end-to-end capability, and what outcomes the work must achieve, without bullets, file names, paths, function names, endpoint paths, collection names, indexes, aggregation stages, or direct solution statements.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "A comprehensive full-stack gitignore covering Python, Node, React, TypeScript, MongoDB data, Docker artifacts, logs, environment files, coverage, build output, IDE files, and OS files.",
    "docker-compose.yml": "A docker-compose file with no version key that starts the task-owned MongoDB service, uses localhost-only 127.0.0.1:27017:27017 binding, inline MongoDB initialization environment values, a mounted init script, a named volume, and a consistent authenticated healthcheck.",
    "db/init_mongo.js": "A MongoDB JavaScript initialization and migration file that creates the app database, app user, related collections with validators, indexes, and programmatically generated realistic seed data with production-like edge cases.",
    "run.sh": "A readiness script located for /root/task that installs frontend and backend dependencies, starts MongoDB with docker compose, waits for authenticated readiness, verifies seeded data exists, builds the React TypeScript starter, verifies the Python backend imports or loads, does not run failing grader tests, and exits 0 on the unsolved starter.",
    "kill.sh": "An idempotent cleanup script that stops the compose stack, removes task containers, networks, volumes, MongoDB data artifacts, local build/dependency artifacts as appropriate, and logs each cleanup step while ignoring already-removed resources safely.",
    "backend/requirements.txt": "Pinned Python dependencies for the selected FastAPI or Flask backend, MongoDB driver, validation/config support, and any lightweight test or tooling dependencies needed by the scaffold.",
    "backend/app/main.py": "The Python REST API application entrypoint wiring configuration, middleware, health behavior, and route registration without embedding core feature logic.",
    "backend/app/api/routes.py": "The backend router layer exposing resource-oriented routes and delegating to services without containing repository queries or final business decisions.",
    "backend/app/services/feature_service.py": "The service-layer module containing orchestration boundaries and incomplete product behavior that candidates must complete without solution-revealing comments.",
    "backend/app/repositories/feature_repository.py": "The repository-layer module isolating MongoDB access, baseline data retrieval helpers, and incomplete persistence/query behavior without giving away final query or index strategy.",
    "backend/app/models/schemas.py": "Request and response schema definitions or validation models that establish safe API boundaries without over-specifying the candidate's final design.",
    "backend/app/core/config.py": "Backend configuration using safe localhost defaults and a MongoDB connection string consistent with docker-compose and the init script.",
    "frontend/package.json": "A React and TypeScript dependency manifest with scripts for installing, building, and optionally testing the frontend using the runtime-native Node toolchain.",
    "frontend/tsconfig.json": "A strict TypeScript configuration appropriate for a React application.",
    "frontend/vite.config.ts": "A Vite configuration for the React TypeScript frontend.",
    "frontend/index.html": "The frontend HTML entrypoint required by the chosen React build setup.",
    "frontend/src/main.tsx": "The React application entrypoint that mounts the app and imports global styling.",
    "frontend/src/App.tsx": "The React application shell that composes the main feature area without embedding all feature logic in one file.",
    "frontend/src/api/client.ts": "The frontend API client boundary for calling the backend and translating transport errors into application-level results without hard-coding the answer.",
    "frontend/src/contracts/api.ts": "The TypeScript contract surface shared with or derived from the backend contract so frontend requests and responses remain typed.",
    "frontend/src/components/FeatureView.tsx": "A representative feature component that renders the product capability and leaves meaningful state and interaction behavior for the candidate to complete.",
    "frontend/src/hooks/useFeatureData.ts": "A custom hook or state module that coordinates frontend data loading and state transitions without prescribing the final architecture.",
    "frontend/src/styles.css": "Minimal styling that makes the starter usable while leaving product behavior as the focus.",
    "package.json": "An optional root workspace or convenience manifest only if the generated project uses one; if emitted, it must contain real scripts and not replace the concrete frontend and backend manifests.",
    "backend/tests/test_contract_smoke.py": "Optional lightweight backend smoke or contract tests if useful; if emitted, they must not reveal the full solution and run.sh must not treat intentional candidate-facing failures as scaffold failure.",
    "frontend/src/__tests__/FeatureView.test.tsx": "Optional lightweight frontend test if useful; if emitted, it must support the task without revealing implementation details."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the main frontend, backend, REST contract, and MongoDB design decisions a strong candidate might make, without requiring one exact implementation when multiple defensible approaches exist.",
  "definitions": "An object of relevant term-to-definition pairs for the selected task, such as REST resource, schema validation, repository layer, typed contract, lifecycle status, Decimal128, pagination, and aggregation, with clear concise definitions.",
  "hints": "A single-line hint that nudges investigation toward full-stack boundaries and data access tradeoffs without naming the specific implementation, query shape, index, endpoint, React pattern, or file to change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable full-stack behavior, maintainable layered code, type-safe API integration, and realistic MongoDB-backed data handling. Use simple english.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3 proficiency, comfort with React and TypeScript, familiarity with REST API design, and understanding of MongoDB data modeling; never include imperative setup, install, run, configure, or verify steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first describe what the system is and the situation today, second open with 'This rework needs to ...' or 'This calls for ...' and state outcomes without mechanisms, and third describe what separates a strong submission while closing on whether the design reasoning is sound."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences outside JSON string values.
2. **name** must be short, descriptive, kebab-case, under 50 characters, and different from title.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and human-readable.
4. **question** must be a scenario paragraph plus direct imperative ask at outcome altitude; no file names, directory paths, function names, endpoint paths, collection names, MongoDB stages, index definitions, or solution statements.
5. **code_files** must include README.md, .gitignore, docker-compose.yml, db/init_mongo.js, run.sh, kill.sh, backend files, frontend files, manifests, and all source files using real concrete file paths with real extensions.
6. **README.md** must contain exactly `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify` in that order; no Database Access, Setup, Installation, Guidance, or NOT TO INCLUDE section.
7. **README Objectives** must follow the DESIGN/BUILD branch: 3-4 short plain goal statements, not stakeholder-framed repair objectives and not implementation instructions.
8. **README How to Verify** must follow the DESIGN/BUILD branch: probe-style experiments and where to look, without stating the correct result or revealing hidden rules.
9. **docker-compose.yml** must not include a version key and must bind MongoDB with `127.0.0.1:27017:27017`.
10. MongoDB initialization values must be inline in docker-compose.yml; forbid `.env` and `${{VAR}}` indirection for datastore initialization.
11. The init script, healthcheck, backend connection string, app user, database name, and authSource must be consistent.
12. run.sh is a readiness gate, NOT the grader. It must install dependencies, start MongoDB, wait for health, build/load the starter, and exit 0 on the unsolved starter.
13. run.sh must not manually create users or run seed scripts; MongoDB initialization must happen through `/docker-entrypoint-initdb.d/`.
14. kill.sh must be idempotent and clean up task-created containers, networks, volumes, and local artifacts safely.
15. The backend must use Python with router -> service -> repository layering.
16. The frontend must use React with TypeScript and typed contracts shared with or derived from the backend contract surface.
17. The MongoDB seed data must be realistic, internally consistent, programmatically generated, and rich enough that the candidate cannot solve by eyeballing one flat seed file.
18. Starter code must be runnable and substantial but must NOT contain the core solution, TODO comments, solution-revealing comments, or hidden-answer names.
19. short_overview must be exactly three bullets, one sentence each, plain non-technical business English, with no backticks, file paths, mechanism names, or seeded defect enumeration.
20. Task must be completable within {minutes_range} minutes for an INTERMEDIATE full-stack engineer while still feeling like a realistic production repository.
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), Python (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)": [
        PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_CONTEXT,
        PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_FULLSTACK_PYTHON_REACT_MONGODB_INTERMEDIATE_INSTRUCTIONS,
    ],
}