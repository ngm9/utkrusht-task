# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_DOCKER_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, particularly in relation to designing, operating, and troubleshooting production-grade Docker and Docker Compose workloads?
"""

PROMPT_DOCKER_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Docker assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL QUESTION CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, operational failures, and Docker/Compose symptoms described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic Docker orchestration, image build, networking, startup-ordering, persistence, and runtime-configuration challenges encountered in the role described in the role context.
- The task must pair Docker with exactly ONE mainstream host application stack chosen to fit the selected scenario: Node.js, Go, or Java. Vary the host stack across generated scenarios when possible.
- Application source code must be small, correct, dependency-light, and not part of the defect set; all seeded defects must live in Dockerfiles, docker-compose.yml, .dockerignore, entrypoints, healthchecks, service networking, volume mounts, build context, or environment interpolation.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the selected host application stack, the services in the Compose system, and the Docker operational problem the candidate will diagnose.)
2. What will the task look like? (Describe the 2-3 service Docker Compose topology, the Docker/Compose defect categories the candidate must reason about, the verification approach, and how it aligns with INTERMEDIATE Docker proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DOCKER_INTERMEDIATE_INSTRUCTIONS = r'''
## GOAL
As a technical architect super experienced in Docker, Docker Compose, and containerized application delivery, you are given a list of real world scenarios and proficiency levels for Docker.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a realistic multi-service repository whose application code is correct but whose Docker and Compose layer contains interacting defects requiring intermediate-level Docker troubleshooting skills.
The candidate's responsibility is to identify the Docker/Compose issues and fix them without being handed the solution. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a FULLY POPULATED repository for a small production-like service stack. The repository includes:
- Exactly ONE mainstream host application stack selected for the scenario: Node.js, Go, or Java
- Two or three Docker Compose services, such as an API service plus a worker service, and at most one supporting backing service using either `postgres:16-alpine` or `redis:7-alpine`
- Per-application-service Dockerfiles under realistic service directories such as `services/api/` and `services/worker/`
- A root `docker-compose.yml`, `.env`, `.dockerignore`, `run.sh`, verification tests or scripts, config files, and README.md
- Small, correct, dependency-light application code that exposes observable cross-service behavior
- Docker and Compose configuration that is intentionally defective in 4-6 interacting ways

The application source is not the exercise. It must be correct, compact, and easy to understand. The candidate should spend their time reasoning about Docker build contexts, multi-stage image wiring, Compose service discovery, startup ordering, healthchecks, named volumes, networks, .env interpolation, entrypoint/CMD behavior, and persistence.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Docker orchestration repair scenario.
- **CRITICAL**: This is an INFRA task. The repository MUST include per-application-service Dockerfiles, a root `docker-compose.yml`, and a root `run.sh`. It MUST NOT include `kill.sh` — E2B sandboxes are destroyed as a whole when the session ends.
- **CRITICAL**: The task must pair Docker with exactly ONE host application stack chosen to fit the scenario: Node.js, Go, or Java. Do not mix host application stacks in the same repository.
- **CRITICAL**: Application source defects are forbidden. The API, worker, and any shared application code must be small, correct, and dependency-light. The seeded defects live only in the Docker, Compose, .dockerignore, entrypoint/CMD, healthcheck, networking, volume, build-context, or environment-interpolation layer.
- **CRITICAL**: Seed exactly 4-6 interacting Docker/Compose defects so the candidate must reason about the stack as a system, not fix isolated lines.
- **CRITICAL**: Defects must be realistic intermediate production mistakes, not YAML syntax errors and not contrived one-line puzzles. The Compose file must parse as YAML, and every Dockerfile must be plausible enough for a real team to have shipped.
- Choose defect categories that fit the selected scenario, such as: a multi-stage Dockerfile copying the wrong build artifact; a build context that cannot see files the Dockerfile expects; a `.dockerignore` rule excluding required runtime assets; an entrypoint/CMD combination that prevents the service from receiving its intended arguments; a healthcheck probing the wrong path, port, or interface; `depends_on` using ordering without health readiness; service-to-service calls using localhost instead of Compose service DNS; host ports used for internal container networking; a named volume mount shadowing built assets; persistent data written to the wrong path; environment interpolation resolving to a misleading default; or a restart/health interaction that hides the real symptom.
- Compose must orchestrate 2-3 services: normally `api` plus `worker`, and optionally exactly one backing service if the scenario needs persistence or caching. Do not invent extra backing services.
- The main service Dockerfile should be multi-stage with a build stage and a slim/alpine runtime stage. Supporting application-service Dockerfiles may be simple or multi-stage, but they must still be realistic and fast.
- Use only slim/alpine base images: `node:20-alpine` for Node.js, `golang:1.22-alpine` plus an alpine/scratch-style runtime for Go, and `eclipse-temurin:21-jdk-alpine` for Java compilation with `eclipse-temurin:21-jre-alpine` for Java runtime.
- If a backing service is required, use at most one of `postgres:16-alpine` or `redis:7-alpine`.
- Application code must be SMALL, CORRECT, and dependency-light. Prefer standard library or near-standard-library implementations so image builds are fast.
- The repository file structure must be genuinely multi-directory and realistic, for example `services/api/`, `services/worker/`, `scripts/`, `tests/` or `verify/`, `config/`, `.dockerignore`, README.md, docker-compose.yml, and run.sh at the root.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Complexity must align with intermediate proficiency level (3-5 years Docker experience), requiring diagnosis across build, runtime, network, storage, and orchestration behavior.
- The question must NOT include hints about the specific defects. Hints belong only in the dedicated `hints` field.
- Ensure adherence to Docker and Docker Compose best practices for intermediate-level repair and operations.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- The task should be completable within {minutes_range} minutes.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, Docker Compose documentation, host-stack documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and repair Docker build and orchestration issues at an intermediate level, rather than testing rote memorization.
- Therefore, the defect set should require genuine Docker reasoning across image layers, build context, healthchecks, service discovery, volumes, and Compose dependency semantics.
- Candidates may use AI to help interpret logs or compare Docker patterns, but the system should require their own diagnostic thinking and validation discipline.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Docker repair task that:
- Draws inspiration from the selected scenario to determine the business context, service purpose, host stack, and whether a backing service is needed.
- Matches INTERMEDIATE Docker proficiency for a candidate with 3-5 years of experience.
- Uses exactly ONE host application stack from Node.js, Go, or Java, selected to fit the scenario. Vary the selected host stack across generated scenarios when possible.
- Produces a realistic multi-directory repository with two application services and optionally one backing service.
- Keeps application code small, correct, dependency-light, and not part of the required fix.
- Places exactly 4-6 interacting defects only in Dockerfiles, docker-compose.yml, .dockerignore, entrypoint/CMD wiring, healthcheck definitions, service networking, volume mounts, build context, or environment interpolation.
- Uses Compose concepts appropriate for intermediate proficiency: healthchecks, `depends_on` with conditions where appropriate, named volumes, a user-defined network, service DNS, local-only published ports, and environment interpolation from a root `.env` file.
- Includes a verification suite implemented as shell or pytest that runs Docker Compose, waits on healthchecks, asserts cross-service behavior, checks service-name networking, verifies persistence across a restart when the scenario requires it, confirms config values flow through, and tears the stack down.
- Verification files and shell scripts MUST use repository-root-relative paths with the `cd "$(dirname "$0")"` pattern or a robust parent-directory equivalent. Do not hardcode `/root/task` inside tests or verification files.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- Pick a different real-world scenario from the list when possible to ensure variety.

## Infrastructure Requirements
- MUST include a root `docker-compose.yml` orchestrating 2-3 services.
- MUST include per-application-service Dockerfiles such as `services/api/Dockerfile` and `services/worker/Dockerfile`.
- MUST include a root `run.sh`.
- MUST include a root `.env` file containing non-secret local configuration values consumed by Docker Compose interpolation.
- MUST include a realistic `.dockerignore`.
- MUST include verification under `tests/` or `verify/` that exercises the Compose stack and is RED on the starter, GREEN after the Docker/Compose defects are fixed.
- MUST NOT include `kill.sh`.
- MUST NOT include `init_database.sql` unless the selected scenario truly requires PostgreSQL initialization; prefer application-managed lightweight initialization for app-focused scenarios.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory in the generated repository context, but scripts and verification files must derive the active repository root relative to their own location so they work both in the sandbox and in a local clone.
- The E2B environment provides Docker and Docker Compose on Ubuntu. The primary runtime for this assessment is Docker; do not system-install Docker or the selected host runtime with apt-get.
- `run.sh` must pre-pull every base image used by the generated Dockerfiles and by any backing service before building.

### Docker-compose Instructions
- Generate `docker-compose.yml` with no top-level `version` key. **MUST NOT include any version specification**.
- Compose must define 2-3 services: an `api` service, a second application component such as `worker`, and optionally one backing service if the selected scenario needs persistence or caching.
- Compose must use a user-defined network for inter-service communication.
- Compose must use at least one named volume when the scenario requires persistence, restart behavior, or generated runtime state.
- Compose must include healthchecks for services whose readiness matters. Healthchecks should be realistic but may be part of the defect set when selected.
- Compose must exercise startup ordering with `depends_on`; when readiness matters, defects may involve missing or incorrect health conditions.
- Compose must use environment interpolation from the root `.env` file for non-secret application configuration such as ports, feature flags, queue names, cache namespaces, or public labels.
- Do not use `.env` interpolation for PostgreSQL container initialization variables. If PostgreSQL is selected, the service MUST set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` inline under `environment:` because the image will not initialize without them. Any init SQL, healthcheck, application connection string, and tests must use the same user and database.
- If Redis is selected, use `redis:7-alpine` and a named volume only if the scenario requires persistence.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every service exposed to the host, including API, Redis, and PostgreSQL. Never use a public bind such as `<port>:<port>`.
- Internal service-to-service traffic must use Compose service names and container ports, never host-published ports.
- The generated starter must include exactly 4-6 Docker/Compose layer defects. The README, question, and hints must not enumerate them.
- Compose must be valid YAML and should remain within normal Docker Compose v2 behavior available on Ubuntu.

### Backing Service Configuration Instructions
- Choose no backing service unless the selected scenario needs persistence, cache coordination, or cross-service state.
- If choosing PostgreSQL, use `postgres:16-alpine`, define `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` inline in the Compose service, add a healthcheck that uses the same user and database, and bind any host port to localhost only.
- If choosing Redis, use `redis:7-alpine`, configure localhost-only host binding when exposed, and use a healthcheck based on Redis readiness.
- Use at most one supporting backing service. Do not combine PostgreSQL and Redis in the same generated task.
- Backing service configuration may be correct or may participate in the selected Docker/Compose defect set, but defects must remain operational Docker defects rather than application source bugs.
- Do not include remote-host placeholders or droplet IPs. Any legitimate connection details in verification commands must use `localhost` for host access or service names for container-to-container communication.

### Run.sh Instructions
- Generate a root `run.sh` using repository-relative paths. It must begin by resolving the repository root with `cd "$(dirname "$0")"` or equivalent.
- The script must use Docker Compose v2 syntax: `docker compose`, not legacy `docker-compose`.
- The script must pre-pull every base image used by the selected host stack and any backing service before building. For example, pre-pull `node:20-alpine` for Node.js, `golang:1.22-alpine` for Go, `eclipse-temurin:21-jdk-alpine` and `eclipse-temurin:21-jre-alpine` for Java, plus `postgres:16-alpine` or `redis:7-alpine` when used.
- The script must verify the Docker daemon is reachable with `docker info` before running Compose commands.
- The script must install only the task's own host-side verification dependencies if they exist, using the runtime-appropriate or test-appropriate manifest. Do not apt-get install Docker, Docker Compose, Node.js, Go, Java, or other primary runtimes.
- The script must run a fast Docker/Compose readiness flow: validate Compose configuration, build the application images, start the stack with `docker compose up -d`, and perform bounded readiness checks that expose the starter's Docker symptoms without serving as the grader.
- The script must not hardcode `/root/task` in commands. It must work from a local clone as well as the sandbox.
- The script must print concise progress messages for pull, build, start, health/status, and final diagnostic output.
- The script must not run the full grader suite as its primary pass/fail gate. The candidate or grader runs the verification files separately.
- If the starter's seeded defects make a service unhealthy, the script should surface useful Docker diagnostics such as container status, health output, and recent logs while keeping the command sequence grounded in real Docker Compose behavior.
- The script must tear down only when its own short diagnostic flow requires a clean retry; do not include a separate cleanup script and do not delete the repository.

### Dockerfile Instructions
- Generate per-application-service Dockerfiles under service directories, not only at the repository root.
- The main service Dockerfile must be multi-stage with a build stage and a slim/alpine runtime stage.
- For Node.js, use `node:20-alpine` and keep dependencies minimal. If dependencies are needed, they must be declared in the service's package manifest and installed deterministically.
- For Go, use `golang:1.22-alpine` for building and a minimal alpine/scratch-style runtime where appropriate.
- For Java, use a tiny no-framework source layout compiled in `eclipse-temurin:21-jdk-alpine` and run with `eclipse-temurin:21-jre-alpine`; avoid Maven or Gradle unless the selected scenario truly requires them.
- Dockerfiles may contain defects only in build-context use, multi-stage artifact wiring, layer/copy ordering, entrypoint/CMD, healthcheck, working directory, user/runtime assumptions, or related Docker behavior.
- Dockerfiles must not contain TODO comments or comments that reveal the defects.
- Application code copied into images must be correct. Do not seed broken route handlers, broken business logic, broken SQL statements, broken Redis commands, or broken worker logic.
- Use slim/alpine images only, and keep builds fast.

The output should be a valid json schema:
  - README.md (candidate-facing instructions with exactly Task Overview, Objectives, Helpful Tips, and How to Verify, each written as a markdown heading: ## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify — plain unmarked section-name lines are INVALID)
  - .gitignore (Docker, selected host stack, test, and local-runtime exclusions)
  - .dockerignore (realistic build-context exclusions, possibly containing one selected defect)
  - .env (non-secret local Compose interpolation values required by the starter)
  - docker-compose.yml (2-3 services, no version key, healthchecks, depends_on, named volume, user-defined network, localhost-only ports)
  - run.sh (repo-relative Docker readiness and diagnostic script that pre-pulls every base image)
  - services/api/Dockerfile (main service Dockerfile, multi-stage)
  - services/worker/Dockerfile (second application service Dockerfile when the scenario uses a worker)
  - services/api/<selected-stack-files> (small correct API source and manifest for exactly one of Node.js, Go, or Java)
  - services/worker/<selected-stack-files> (small correct worker source and manifest for the same selected stack)
  - config/ or scripts/ files as needed for non-secret local configuration
  - tests/ or verify/ files (shell or pytest verification that runs Compose, waits on healthchecks, asserts cross-service behavior, checks persistence/config flow when relevant, and tears down)
  - additional files required for the selected host stack, while keeping application code correct and Docker defects unsolved

## Code file requirements
- Generate a substantial but focused intermediate repository, not a toy snippet. The starter must include multiple interacting directories and files that a 3-5 year Docker engineer must navigate.
- The generated project must include realistic directories such as `services/api/`, `services/worker/`, `scripts/`, `tests/` or `verify/`, and `config/`.
- Application code must be complete, correct, small, and dependency-light. It should expose one health endpoint and one or two scenario-relevant endpoints or worker behaviors sufficient for verification.
- The same host application stack must be used for all application services. Do not mix Node.js and Go, Go and Java, or Node.js and Java in the same generated task.
- Defects must be limited to Dockerfiles, Compose, .dockerignore, entrypoint/CMD wiring, healthchecks, network/hostname/port assumptions, named volumes, build contexts, and .env interpolation. Do not place defects in application source code.
- The verification suite must be RED on the starter and GREEN when the candidate fixes all seeded Docker/Compose defects.
- Verification must assert cross-service behavior, such as the API reaching a worker or backing service by service name, a worker observing API or queue state, data persisting across a restart when persistence is part of the scenario, and environment-derived config values appearing in observable behavior.
- Verification must clean up with `docker compose down --volumes --remove-orphans` in its own fixture or trap, ignoring cleanup errors where appropriate.
- All shell scripts and verification files must resolve the repository root relative to their own path. Do not hardcode `/root/task` inside tests or verification files.
- Do not include comments that give away the solution in Dockerfiles, Compose, scripts, source code, tests, or README.
- Do not include droplet IP placeholders anywhere.
- Use `localhost` only for host-to-container checks and service names only for container-to-container communication.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory in the generated assessment environment, while commands inside scripts and tests remain repository-root-relative for portability.

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore suitable for Docker and the selected host stack, including:
- Docker and Compose local state where appropriate
- Build artifacts, coverage output, test caches, log files, and temporary files
- Node.js exclusions such as node_modules, npm cache, and coverage when Node.js is selected
- Go exclusions such as binaries, coverage files, and test artifacts when Go is selected
- Java exclusions such as compiled classes, target/build directories, and logs when Java is selected
- IDE and editor files such as .idea/, .vscode/, *.swp
- OS-specific files such as .DS_Store and Thumbs.db
- Do not ignore required task files such as `.env`, docker-compose.yml, service Dockerfiles, verification files, or source directories.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain EXACTLY the following sections, in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
- Must contain 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, the operational Docker pain the team is feeling, and why the problem matters.
- Must be specific to the selected real-world scenario and the selected host stack.
- Must state that the application behavior is intended to be correct and the work is to make the containerized stack reliable.
- NEVER empty. NO bold time-budget callouts.
- Do not enumerate or name the Docker/Compose defects.

### Objectives
- INTERMEDIATE level: 3-4 bullets maximum; fewer, tighter is better.
- Objectives MUST be SHORT and OPEN-ENDED: one line each, roughly 8-18 words.
- Each objective must state ONE desired outcome from the operator's or user's point of view.
- Describe the what and why, NEVER the how.
- Do NOT name Dockerfile instructions, Compose keys, commands, file paths, service implementation details, exact mechanisms, or specific defects.
- Do NOT say "currently does X".
- Good objective style: "Every service must become healthy from a cold start with one documented command."
- Good objective style: "Cross-service requests must succeed through stable internal service discovery."
- Good objective style: "Important runtime state must survive the restart path users depend on."
- Bad objective style: "depends_on lacks a condition; add service_healthy so the api waits for postgres."
- Bad objective style: "Fix services/api/Dockerfile to copy the binary from the builder stage."

### Helpful Tips
- 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and must NOT name the specific Dockerfile instruction, Compose key, command, pattern, API, library, function, data structure, or exact defect that solves the task.
- Appropriate tips may orient candidates toward comparing container logs, health status, image contents, environment values, network reachability, and persistent state.
- One tip may mention that local Docker and Compose state are observable sources of truth, but must not prescribe exact fixes.

### How to Verify
- 3-5 bullets maximum.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- VARY the sentence openings — bullets must NOT all begin with the same word or stem (never five "Confirm the ..." lines). Write each as a natural action a candidate takes plus what they should observe, e.g. "Bring the stack up from a cold start and watch every service reach a healthy state." / "Restart the stack and check that previously recorded data is still there." / "Run the verification suite; it should complete cleanly."
- Each bullet is a check the candidate can run or observe: service health, cross-service response, restart/persistence behavior, config propagation, logs, or the verification suite result.
- Mention that verification runs against the local Docker daemon and uses localhost for host-visible endpoints.
- Do not include setup commands, package-install commands, or step-by-step implementation instructions.
- Do not include droplet IPs or remote-host placeholders.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of README.md:
- Setup commands such as npm install, go test, javac, docker compose up, or any equivalent installation/start commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific Dockerfile instructions, Compose keys, method names, library names, pattern names, or data-structure names that reveal the solution
- File names, file paths, service names tied to exact fixes, or command snippets that give away answers
- Code snippets that give away the answer
- A section heading named "NOT TO INCLUDE", "CONTENT TO EXCLUDE", or any similar exclusion heading
- Directive phrases like "you should implement", "add this key", "create this class", "use this instruction", or "configure the following"

## REQUIRED OUTPUT JSON STRUCTURE
The generated response must be valid JSON only and must follow this exact structure. Each field's value must be fully populated and candidate-safe.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the selected Docker orchestration scenario without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name and specific to the selected Docker repair problem.",
  "question": "A complete candidate-facing task description explaining the selected business scenario, the observable containerized-stack failures, the chosen host application stack, and the desired operational outcomes without revealing the specific Docker or Compose defects.",
  "code_files": {{
    "README.md": "Candidate-facing README content that follows exactly the required four sections: Task Overview, Objectives, Helpful Tips, and How to Verify, with concise open-ended guidance and no setup commands or defect enumeration.",
    ".gitignore": "Docker and selected-host-stack gitignore that excludes build artifacts, caches, logs, local test state, and editor files while keeping required task files tracked.",
    ".dockerignore": "Repository or service build-context ignore file that is realistic for the selected stack and may contain one carefully chosen Docker-layer defect without comments revealing the solution.",
    ".env": "Non-secret local configuration values consumed by Docker Compose interpolation, such as host ports, service labels, or runtime flags, with values safe to commit for the assessment.",
    "docker-compose.yml": "Root Compose file with no version key, two or three services, localhost-only published ports, healthchecks, user-defined network, named volume where relevant, environment interpolation from .env, and exactly the selected Docker/Compose defects.",
    "run.sh": "Root repository-relative shell script that checks Docker availability, pre-pulls every base image, validates Compose configuration, builds and starts the stack for diagnostic readiness, reports service health and logs, and does not run the full grader suite.",
    "services/api/Dockerfile": "Main API service Dockerfile using the selected host stack, including a multi-stage build and a slim/alpine runtime stage, with any seeded defect limited to Docker behavior rather than application logic.",
    "services/worker/Dockerfile": "Second application service Dockerfile for the same selected host stack, small and fast to build, with any seeded defect limited to Docker behavior rather than application logic.",
    "services/api/main.go": "EXAMPLE ENTRY ONLY — emit the REAL manifest and source files for the ONE selected stack under services/api/, using that stack's true file names: for Go emit services/api/go.mod and services/api/main.go; for Node.js emit services/api/package.json and services/api/server.js; for Java emit services/api/src/Main.java and its build file. All application code must be correct.",
    "services/worker/main.go": "EXAMPLE ENTRY ONLY — emit the REAL worker manifest and source files under services/worker/ using the SAME selected stack and its true file names (e.g. services/worker/go.mod + services/worker/main.go for Go). Correct, compact business logic used only to exercise orchestration behavior.",
    "config/app.json": "EXAMPLE ENTRY ONLY — emit the real small non-secret configuration file(s) the scenario needs, with real names (e.g. config/app.json or config/settings.yaml), written so any intended defect remains in Docker mounting or interpolation rather than in the application source.",
    "scripts/wait_for_health.sh": "EXAMPLE ENTRY ONLY — emit real repository-relative helper scripts with real names only when needed for verification or diagnostics, with no hardcoded /root/task paths and no comments that reveal the fixes.",
    "verify/verify.sh": "EXAMPLE ENTRY ONLY — emit the real verification suite with a real file name (e.g. verify/verify.sh or tests/test_stack.py): it runs Docker Compose, waits on service health, asserts cross-service behavior by service name, checks persistence or config flow when relevant, tears down the stack, and fails on the starter until the Docker defects are repaired."
  }},
  // CRITICAL: the code_files keys above marked "EXAMPLE ENTRY ONLY" are illustrations of the DIRECTORY layout, not literal file names to copy. Every key you emit in code_files MUST be a real, concrete file path with a real extension appropriate to the selected stack. NEVER emit placeholder-style names such as "selected_stack_manifest_and_source", "additional_files_as_needed", "local_config_files", "supporting_scripts", or "or_verify_files" — a repository containing any such file name is an automatic failure.
  "answer": "Evaluator-facing high-level solution approach describing each seeded Docker/Compose defect, its observable symptom, the intended repair, and the operational reasoning behind the fix without requiring application source changes.",
  "definitions": "An object of concise term-to-definition pairs for concepts relevant to the task, such as multi-stage build, build context, Compose service discovery, healthcheck, named volume, environment interpolation, localhost binding, entrypoint, image layer, and container network.",
  "hints": "A single-line candidate-safe hint that nudges investigation toward comparing build output, container health, logs, networking, environment values, and persisted state without naming any specific defect or fix.",
  "outcomes": "Two to three concise lines describing measurable expected results after completion, such as healthy cold starts, successful service-to-service communication, reliable restart behavior, correct config propagation, and clean verification results.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Docker and Docker Compose fundamentals, comfort reading container logs and health status, and familiarity with one of Node.js, Go, or Java service layouts.",
  "short_overview": "A bullet list summarizing the business problem, the Docker and Compose troubleshooting focus, the selected host stack context, and the expected operational outcome in simple English."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The generated task must align with INTERMEDIATE Docker proficiency for a candidate with 3-5 years of experience.
3. INFRA shape: docker-compose.yml + per-service Dockerfiles + run.sh REQUIRED; kill.sh FORBIDDEN.
4. The repository must contain 2-3 Compose services and exactly ONE host application stack chosen from Node.js, Go, or Java.
5. Use at most one backing service, either `postgres:16-alpine` or `redis:7-alpine`, only when the selected scenario needs it.
6. Application code must be small, correct, and dependency-light; all seeded defects must live only in Dockerfiles, Compose, .dockerignore, entrypoint/CMD, healthcheck, networking, volume, build-context, or environment interpolation.
7. Seed exactly 4-6 interacting Docker/Compose defects. Do not create syntax errors, application bugs, or missing source files that make the task unfair.
8. The main service Dockerfile must be multi-stage, and run.sh must pre-pull every base image before building.
9. docker-compose.yml must have no version key, must use localhost-only published ports, must include a user-defined network, and must use named volumes where persistence is relevant.
10. Compose must exercise healthchecks, startup ordering, internal service discovery, and .env interpolation in a way appropriate to the selected scenario.
11. If PostgreSQL is used, set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` inline in the service environment and keep healthchecks and connections consistent with those values.
12. Verification must run Docker Compose, wait on healthchecks, assert cross-service behavior, verify persistence or config propagation when relevant, and tear down the stack.
13. run.sh and verification files must use repo-root-relative paths and must never hardcode `/root/task`, so the same commands work in the sandbox and on a local clone.
14. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, each as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify). Plain unmarked section-name lines are INVALID.
15. README Objectives must be short, open-ended, operator/user-outcome statements and must never enumerate defects, name files, name commands, or name Docker/Compose keys.
16. The `pre_requisites` field must contain assumed prior knowledge only, not imperative setup or verification steps.
17. The `title` must be different from `name` and use plain English in '<action verb> <subject>' format.
18. The task must be completable within {minutes_range} minutes.
19. The generated task must reflect the selected real-world scenario closely and must not invent an unrelated domain.
'''

PROMPT_REGISTRY = {
    "Docker (INTERMEDIATE)": [
        PROMPT_DOCKER_INTERMEDIATE_CONTEXT,
        PROMPT_DOCKER_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_DOCKER_INTERMEDIATE_INSTRUCTIONS,
    ]
}