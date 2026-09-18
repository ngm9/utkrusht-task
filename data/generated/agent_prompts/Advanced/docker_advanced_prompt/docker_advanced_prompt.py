# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_DOCKER_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

A Docker engineer at the advanced level is expected to independently design, operate, and improve production-grade container platforms, including image build systems, runtime security controls, networking, storage, observability, and CI/CD integration. They own complex Docker decisions such as base-image strategy, hardened runtime configuration, container performance tuning, health orchestration, filesystem permissions, signal handling, and incident diagnosis across Linux namespaces, cgroups, storage drivers, and network paths.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DOCKER_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an advanced Docker assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION PROMPT CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given advanced Docker skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- The generated repository MUST be an infra-shaped Docker task with docker-compose.yml, per-service Dockerfiles, entrypoint scripts, verification files, and run.sh
- The task MUST pair Docker with exactly ONE mainstream host application stack selected to fit the scenario: Node.js, Go, or Java
- The selected application stack must stay dependency-light and fast to build, using slim or alpine base images only
- The task may include up to two supporting backing services selected from postgres:16-alpine, redis:7-alpine, or a tiny stdlib-based sidecar, but do not invent services not needed by the scenario
- All defects must live in the Docker, compose, entrypoint, configuration, filesystem, healthcheck, resource, or orchestration layer; application source must be correct and must not require modification

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the business domain, selected scenario, selected host application stack, service topology, and Docker incident the candidate will resolve.
2. What will the task look like? Describe the 3-4 service repository, Docker/Compose artifacts, interacting container-layer defects, verification approach, and how it aligns with advanced Docker proficiency.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DOCKER_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Docker, container runtime behavior, and production Compose-based systems, you are given a list of real world scenarios and proficiency levels for Docker. Your job is to generate an advanced Docker troubleshooting and hardening task where a candidate receives a realistic multi-service repository with correct application code and 5-7 interacting defects exclusively in the Docker, compose, entrypoint, runtime security, filesystem, health orchestration, resource, or configuration layer.

**CRITICAL**: The repository MUST include per-service Dockerfiles, docker-compose.yml, optionally docker-compose.override.yml when the scenario uses one, entrypoint scripts, verification files, and run.sh. The task MUST be infra-shaped and must exercise genuinely advanced Docker competence without asking the candidate to change business application source.

**CRITICAL**: Pair Docker with exactly ONE mainstream host application stack chosen to fit the selected scenario: Node.js, Go, or Java. Do not mix application stacks. Use only dependency-light, fast-building application code with slim or alpine base images such as node:20-alpine, golang:1.22-alpine, or eclipse-temurin:21-jre-alpine. Supporting services are limited to postgres:16-alpine, redis:7-alpine, or a tiny stdlib-based sidecar when needed.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a FULLY POPULATED, realistic multi-directory Docker repository that models a production-like incident in a 3-4 service local stack. The application source is intentionally small, correct, and dependency-light, while the containerization layer contains advanced operational defects that interact with each other.

The repository includes:
- A selected business scenario derived from the provided real-world task scenarios
- Exactly one mainstream host application stack across the application services: Node.js, Go, or Java
- 3-4 Compose services, typically an api service, a worker or sidecar service, and one or two backing services when the scenario requires them
- Per-service Dockerfiles, real source files, concrete manifests, entrypoint scripts, config files, docker-compose.yml, optional docker-compose.override.yml, run.sh, README.md, .gitignore, and meaningful .dockerignore files
- A verification suite in shell or pytest that starts the stack, waits on health, validates readiness truthfulness, exercises service-to-service behavior by Compose service name, sends SIGTERM, checks graceful shutdown, validates non-root/read-only constraints, verifies persistence where required, and tears down afterward
- Correct application code that should not be modified; the candidate's work should be Docker and Compose remediation only

**CRITICAL**: The task should feel like an advanced production container incident: fixing one Docker-layer issue should expose or make measurable the next issue. The defects must be interacting rather than seven unrelated lint findings.

**FILE LOCATION**: All code and scripts must be valid when the repository is placed at /root/task as the base directory. However, emitted run.sh, entrypoint scripts, verification files, and test files MUST use repo-root-relative path resolution such as `cd "$(dirname "$0")"` or an equivalent pattern, and MUST NOT hardcode /root/task inside verification files or tests.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, crisp, and clearly describe the Docker incident or hardening scenario
- **MANDATORY**: The task MUST be derived from and aligned with ONE provided real-world scenario. Use that scenario's business context, operational risk, domain entities, and service relationships
- **CRITICAL**: This is ADVANCED Docker proficiency. The candidate should need to reason across image construction, Compose orchestration, PID 1 behavior, Linux filesystem permissions, non-root users, cgroup resource limits, healthchecks, and persistent volumes
- **CRITICAL**: The starter codebase MUST be substantial and realistic, NOT a toy snippet. Require multiple interacting modules, multiple service directories, per-service Dockerfiles, entrypoint scripts, configuration, and verification files in a real project layout
- **CRITICAL**: Application source stays correct and dependency-light. All defects live ONLY in Dockerfiles, docker-compose.yml, docker-compose.override.yml when present, entrypoint scripts, filesystem mounts, environment/config wiring, healthchecks, resource constraints, user/permissions, runtime security flags, or volume declarations
- **CRITICAL**: Do NOT ask candidates to implement new application features, change handlers, alter business logic, or rewrite source code. The host application exists only to make Docker behavior observable
- The task MUST include 5-7 interacting advanced Docker defects selected from the following families:
  - BuildKit-conscious layer ordering and cache-busting mistakes that slow rebuilds
  - Multi-stage builds with a wrong, bloated, or leaky final stage
  - Non-root USER directives combined with file-ownership or bind-mount permission failures
  - Read-only root filesystems with missing tmpfs or writable mounts
  - Entrypoint shell-form or wrapper mistakes that break signal propagation
  - PID-1 behavior that orphans children or skips graceful shutdown
  - Healthcheck start_period, interval, timeout, or retries that make orchestration lie about readiness
  - Resource limits such as memory or cpus that make a service OOM-killed or starved
  - Compose override files or profiles wiring the wrong environment
  - Secrets or config passed insecurely or interpolated to wrong defaults
  - Volume or bind-mount permission clashes with non-root users
- Defects must be observable through container status, health transitions, logs, signal behavior, service-to-service calls, permissions, persistence, image size, build cache behavior, or resource events
- The repository MUST orchestrate 3-4 services with docker-compose.yml. Use docker-compose.override.yml only when it is part of the selected scenario, for example a local profile or environment override that miswires configuration
- The selected host stack MUST be exactly one of Node.js, Go, or Java and all application services must use that one stack consistently
- The application code must be SMALL, CORRECT, and dependency-light. Prefer stdlib or near-stdlib application code so Docker builds stay fast under an E2B Ubuntu hard time budget
- run.sh MUST pre-pull every base image used by Dockerfiles and backing services before building
- Complexity must align with advanced proficiency while remaining completable within {minutes_range} minutes
- The question scenario must be clear with accurate facts and relevant context, but must NOT enumerate the exact defects or reveal specific Dockerfile or Compose keys to change
- README Objectives must be open-ended and stakeholder-oriented, not a defect checklist
- Questions, hints, README tips, and visible verification descriptions must guide investigation without giving away the implementation
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The task assesses the candidate's ability to diagnose, reason about, and improve a realistic advanced Docker system, not memorization of command syntax
- Candidates may use AI to accelerate investigation, compare Docker behaviors, or review configuration options, but the submitted work must reflect sound operational judgment and working remediation
- The assessment rewards practical Docker debugging, correct tradeoffs, secure container runtime behavior, resilient orchestration, and evidence-driven verification

## Code Generation Instructions
Create an advanced Docker-focused infrastructure task that:
- Draws inspiration from input_scenarios for business context, technical requirements, and operational stakes
- Uses the provided real-world scenario as the basis for this task - do not invent a different domain
- Matches advanced Docker proficiency and expects production-grade reasoning across build, runtime, security, orchestration, resources, and filesystem behavior
- Uses exactly ONE host application stack chosen from Node.js, Go, or Java
- Keeps application code small, correct, complete, and dependency-light so container builds remain fast
- Uses slim or alpine base images only for the selected stack, such as node:20-alpine, golang:1.22-alpine, or eclipse-temurin:21-jre-alpine
- Includes up to two supporting backing services only when the scenario actually needs them, selected from postgres:16-alpine, redis:7-alpine, or a tiny stdlib-based sidecar
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list for variety
- Build a realistic multi-directory repository, for example services/api/, services/worker/, docker/entrypoints/, scripts/, verify/ or tests/, config/, root .env, docker-compose.yml, optional docker-compose.override.yml, run.sh, README.md, .gitignore, and .dockerignore files per build context where meaningful
- Ensure every emitted file has a real, concrete path and extension appropriate to the selected stack. NEVER emit placeholder-style names like `selected_stack_manifest_and_source`, `additional_files_as_needed`, `supporting_scripts`, or `or_verify_files`
- When an output structure key is illustrative, mark it as EXAMPLE ENTRY ONLY and still use a real concrete file path
- Make all run.sh, entrypoint, and verification paths repo-root-relative. Do not hardcode /root/task inside tests or verification files
- Ensure the task is fully self-contained for E2B: Docker and Docker Compose are available, the primary runtime image is pulled by Docker, and no apt-get/system runtime installation is required
- The candidate should improve Docker artifacts and scripts, not application source

## Infrastructure Requirements
- MUST include docker-compose.yml orchestrating 3-4 services
- MUST include per-service Dockerfiles for application services and any tiny stdlib-based sidecar service
- MUST include entrypoint scripts for services whose lifecycle, permission, or signal behavior is part of the task
- MUST include run.sh at repository root
- MUST include a shell or pytest verification suite under a concrete directory such as verify/ or tests/
- MUST include README.md, .gitignore, .dockerignore files where meaningful, config files, and a root .env when the scenario uses local defaults
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole and container cleanup is automatic outside the verification teardown
- MUST NOT include Kubernetes, Helm, Terraform, Ansible, Packer, Swarm cluster setup, private registry setup, cosign signing implementation, or multi-host networking as primary deliverables for this task
- MUST NOT require candidates to install the runtime on the host. Docker image builds provide the host application runtime
- The initial repository must be realistic and diagnosable. It may start with unhealthy or unreliable service behavior as part of the candidate-facing task, but the scaffold itself must be buildable and inspectable
- run.sh is a readiness and scaffold self-check, NOT the grader. It must not run the candidate verification suite that is expected to fail until the Docker issues are solved

### Docker-compose Instructions
- docker-compose.yml MUST NOT include any version specification
- Compose must define 3-4 services with realistic names such as api, worker, postgres, redis, or a scenario-specific sidecar
- Compose must use exactly one host application stack across app services: Node.js, Go, or Java
- Compose may include up to two supporting backing services when required by the scenario. Do not include unused datastores
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore or application service exposed to the host
- For postgres services, REQUIRE standard init env vars inline in `environment:`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`. The image will NOT initialize without them. The init SQL, healthcheck, and connection string must use the same user and database
- For mysql services if a scenario somehow requires mysql, REQUIRE standard init env vars inline in `environment:` using the matching `MYSQL_*` values. Do not choose mysql unless the selected scenario explicitly requires it
- For redis services, use redis:7-alpine and configure only the minimum needed to make the scenario observable
- Forbid `.env` files, `env_file`, and `${{VAR}}` host indirection for datastore initialization credentials. Inline datastore environment values are required so containers initialize reliably
- A root .env may exist as a candidate-facing config artifact only when it is part of the Docker/config defect scenario; it must not be the sole source of required datastore init credentials
- Include healthchecks that are functional enough to expose readiness problems, but deliberately include one or more advanced readiness defects when selected
- Use service names for cross-service communication inside the Compose network, never localhost from one container to another
- Compose override files or profiles may be included only when the scenario uses them; if included, they should participate in one of the interacting defects without becoming the entire task
- Resource limits, read-only root filesystems, tmpfs mounts, volumes, user directives, capabilities, and security options should be used realistically and may contain advanced defects for the candidate to resolve
- Do not rely on remote hosts, droplet IPs, or external services

### Datastore and Configuration Instructions
- Include postgres:16-alpine and/or redis:7-alpine only if the selected scenario requires persistence, caching, queues, or shared state
- If postgres is included, provide a real init_database.sql under a concrete path such as docker/postgres/init_database.sql or db/init_database.sql, and mount it into the correct initialization directory
- init_database.sql must be small, deterministic, and directly relevant to the selected scenario
- Datastore configuration must be internally consistent enough to diagnose Docker-layer issues; do not create arbitrary SQL bugs
- If persistence is part of the scenario, include a named volume and verification that data users expect to keep survives container restart
- Avoid exposing database connection details in README.md. If connection details appear in docker-compose healthchecks, run.sh probes, or verification scripts, the host must use localhost for host-side checks
- Do not include remote host placeholders, droplet IP placeholders, or client-tool setup instructions in README.md
- Configuration files under config/ should be realistic and may intentionally participate in Docker-level configuration wiring defects
- Secrets/config defects must be Docker/Compose defects, such as insecure file placement or wrong Compose interpolation defaults, not application parsing bugs

### Run.sh Instructions
- run.sh MUST be located at repository root
- run.sh MUST use repo-root-relative path handling such as:
  - `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"`
  - `cd "$SCRIPT_DIR"`
- run.sh MUST NOT hardcode /root/task
- run.sh MUST install or prepare only task-owned third-party dependencies if the verification harness needs them. Do not apt-get or system-install Docker, Docker Compose, Node.js, Go, Java, or other primary runtimes
- run.sh MUST pre-pull every base image and backing-service image before building, including selected stack images such as node:20-alpine, golang:1.22-alpine, eclipse-temurin:21-jre-alpine, and services such as postgres:16-alpine or redis:7-alpine
- run.sh MUST use `docker compose up -d --build` or an equivalent docker compose command to build and start the stack
- run.sh MUST be a deployability and scaffold-readiness probe, NOT the grader. It MUST NOT run the verify/ or tests/ suite that is designed to fail until the candidate solves the task
- run.sh should verify that Docker is available, pre-pull images, build images, start containers, print service status, and perform lightweight scaffold checks that prove the repository can be inspected
- Because the starter intentionally contains Docker-layer defects, run.sh may report unhealthy or degraded containers as candidate-facing observations, but it should exit 0 when images build and the stack is created sufficiently for investigation
- run.sh must exit non-zero only when the scaffold is broken beyond the intended task, such as missing files, Docker unavailable, image build syntax failure unrelated to intended defects, or Compose unable to parse the project
- run.sh should print concise next-step guidance pointing candidates to README.md and the verification suite without revealing fixes
- Do not include kill.sh; teardown belongs inside verification files where needed, and the E2B sandbox lifecycle handles cleanup

### Dockerfile Instructions
- Each application service MUST have its own Dockerfile under a concrete service directory such as services/api/Dockerfile or services/worker/Dockerfile
- If a tiny sidecar is implemented as a local service rather than a public image, it MUST also have a concrete Dockerfile under its service directory
- Use fast slim or alpine base images only:
  - Node.js tasks should use node:20-alpine
  - Go tasks should use golang:1.22-alpine for builder stages and a small alpine or scratch-style final stage when appropriate
  - Java tasks should use eclipse-temurin:21-jre-alpine for runtime and an appropriately small builder only when compilation is included
- Dockerfiles should be intentionally realistic but flawed in advanced ways, such as poor layer ordering, cache-busting COPY patterns, bloated final stages, wrong ownership after COPY, non-root permission failures, or missing writable paths under read-only root filesystems
- Defects must be advanced and interacting. Do not create trivial syntax errors, missing files, impossible builds, or application code bugs
- Use BuildKit-conscious patterns and mistakes where relevant, but keep builds fast under the E2B time budget
- Include .dockerignore files per build context where meaningful. They may be incomplete or mis-scoped as part of the Docker optimization challenge
- Application source should not contain TODO comments and should not need candidate modification
- Entrypoint scripts must be real files with executable shell content and may deliberately demonstrate shell-vs-exec or child-process lifecycle defects
- Dockerfiles and entrypoints must be sufficient for candidates to reason about signal handling, ownership, PID 1 behavior, and filesystem writability

The output should be a valid json schema and include the following files in `code_files` using concrete real paths:
- `README.md` with exactly Task Overview, Objectives, Helpful Tips, and How to Verify, each written as a markdown heading (`## Task Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify`) — plain unmarked section-name lines are INVALID
- `.gitignore`
- `.env` when the selected scenario uses local config defaults
- `docker-compose.yml`
- `docker-compose.override.yml` only if the scenario uses an override or profile defect
- `run.sh`
- `docker/entrypoints/api-entrypoint.sh` or an equivalent real per-service entrypoint path
- `docker/entrypoints/worker-entrypoint.sh` or an equivalent real per-service entrypoint path
- `docker/postgres/init_database.sql` only if postgres is included
- `verify/verify_stack.sh` or `tests/test_stack.py` as the concrete verification suite
- For a Go selected stack, real files such as `services/api/go.mod`, `services/api/main.go`, `services/api/internal/server/server.go`, `services/worker/go.mod`, and `services/worker/main.go`
- For a Node.js selected stack, real files such as `services/api/package.json`, `services/api/server.js`, `services/api/lib/health.js`, `services/worker/package.json`, and `services/worker/worker.js`
- For a Java selected stack, real files such as `services/api/pom.xml`, `services/api/src/main/java/com/example/Main.java`, `services/worker/pom.xml`, and `services/worker/src/main/java/com/example/WorkerMain.java`
- Per-service `.dockerignore` files such as `services/api/.dockerignore` and `services/worker/.dockerignore`
- Any additional emitted file must have a real, concrete path and extension; never emit placeholder-style filenames

## Code file requirements
- Generate a realistic multi-directory repository, not a single-file Docker example
- The application source must be COMPLETE, CORRECT, dependency-light, and small enough to build quickly
- The selected application stack must be exactly one of Node.js, Go, or Java
- Do not include files from multiple host application stacks in the same task
- All app services must use the same selected application stack
- The candidate's expected changes should span multiple Docker/Compose/entrypoint/configuration files, not one obvious line
- All defects must be in Dockerfiles, docker-compose.yml, optional docker-compose.override.yml, entrypoint scripts, runtime filesystem settings, volumes, healthchecks, resource limits, users, permissions, or config wiring
- Do not require changes to application business logic or source files
- Include realistic service-to-service behavior so verification can exercise communication by Compose service name
- Include verification that detects readiness truthfulness: a service must not report healthy before it can actually serve its expected traffic
- Include verification that sends SIGTERM to an application service and asserts graceful shutdown within a bounded window
- Include verification that checks non-root and read-only constraints hold after remediation
- Include persistence verification if the scenario requires durable state
- Verification files must bring the stack up, wait, assert observable outcomes, and tear down with `docker compose down --volumes --remove-orphans` or an equivalent cleanup inside the verification flow
- Verification files must use repo-root-relative paths and must not hardcode /root/task
- Use localhost only for host-side checks in run.sh and verification files
- Use service names only for container-to-container checks
- Keep builds fast: pre-pull bases in run.sh, avoid heavyweight dependencies, and avoid large generated fixtures
- Do NOT include comments that reveal the defects or the solution
- **FILE LOCATION**: All code and scripts must be valid under /root/task as the base directory, while scripts and tests should calculate the repository root dynamically

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file for Docker and the selected host stack including:
- OS files such as .DS_Store and Thumbs.db
- Editor and IDE files such as .idea/, .vscode/, *.swp, and *.swo
- Logs and temporary files such as *.log, logs/, tmp/, and *.tmp
- Docker local artifacts and generated data directories
- Test caches such as .pytest_cache/ if pytest is used
- Node.js artifacts such as node_modules/, npm-debug.log*, coverage/, and dist/ only when Node.js is selected
- Go artifacts such as bin/, *.test, *.out, coverage.out, and vendor/ only when Go is selected
- Java artifacts such as target/, build/, *.class, and .gradle/ only when Java is selected
- Do not ignore files that must be committed for the task, such as the intentionally provided root .env if the scenario requires it

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following output sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
- 3-4 meaningful sentences. No bullet list
- Describes the business scenario, current state, and why the problem matters operationally
- NEVER empty
- NO bold time-budget callouts
- Explain that the application behavior is already present and the operational risk is in the containerized delivery path
- Do not reveal specific Dockerfile, Compose, entrypoint, healthcheck, resource, or filesystem defects

### Objectives
For ADVANCED proficiency, Objectives MUST be concise and OPEN-ENDED.
- Use 3-4 bullets max, fewer and tighter is better
- For this Docker task, write each objective as a full natural sentence from a stakeholder point of view such as an operator, on-call engineer, platform engineer, or downstream consumer
- Each bullet should be roughly 10-16 words where possible
- Each objective states ONE desired outcome and why it matters operationally
- Describe the what and why, NEVER the how
- NEVER enumerate defects
- NEVER say phrases like currently does, currently fails, broken because, or fix the
- NEVER name Dockerfile keys, Compose keys, files, flags, commands, method names, class names, variables, exact healthcheck settings, mount names, or implementation details
- GOOD style: An engineer joining on-call should trust stack health before serving traffic
- GOOD style: Downstream consumers should experience clean shutdowns without partial work loss
- BAD style: Fix the healthcheck start_period in docker-compose.yml so readiness works
- BAD style: Change the entrypoint to exec form and add tmpfs mounts

### Helpful Tips
- 4-5 bullets max
- Provide practical guidance without revealing specific implementations
- Each bullet must start with a varied action word such as Consider, Review, Analyze, Explore, or Think about
- Do not use the same action word for every bullet
- Tips guide discovery and MUST NOT name the specific API, library, Dockerfile instruction, Compose key, method, pattern, data structure, or exact command that solves the task
- Tips may point candidates toward observing build behavior, lifecycle events, health transitions, filesystem access, service relationships, and runtime constraints at a high level

### How to Verify
- 3-5 bullets max
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write
- Use varied sentence openings; never make every bullet start with Confirm the
- Each bullet is a natural action the candidate takes plus what they should observe
- Verification may mention broad actions such as bringing the stack up from a cold start, watching services reach healthy state, exercising cross-service behavior, stopping the stack, and checking expected persistence
- Do not include setup commands, docker compose commands, exact file names, or implementation snippets in README.md
- Do not include database connection details, hostnames, usernames, passwords, ports, client-tool suggestions, droplet IPs, or remote-host placeholders

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of README.md:
- Setup commands such as npm install, pip install, docker compose up, mvn test, go test, or run.sh
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, Dockerfile instruction names, Compose key names, flag names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like you should implement, add this middleware, create this class, use this API, change this Dockerfile key, or set this Compose option
- Defect enumerations or lists of exactly what is broken
- Database connection details, credentials, host/port details, client-tool suggestions, droplet IP placeholders, or remote-host placeholders
- Any README heading other than Task Overview, Objectives, Helpful Tips, and How to Verify

## REQUIRED OUTPUT JSON STRUCTURE
The response MUST be valid JSON only, with no markdown fences, no explanations, and no commentary. Each field below must be populated with real task content. The `code_files` object must map concrete repository file paths to full file contents.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that describes the advanced Docker incident without naming the exact fixes.",
  "title": "A human-readable display title in action-verb plus subject format, 50-80 characters, different from name, and focused on the operational Docker outcome.",
  "question": "A complete candidate-facing task description explaining the selected business scenario, the 3-4 service Docker stack, the operational symptoms, the restriction that application source is correct, and the expectation that the candidate resolves Docker/Compose/entrypoint/runtime issues without enumerating the exact fixes.",
  "code_files": {{
    "README.md": "The complete candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify — plain unmarked section-name lines are INVALID), with concise open-ended advanced-level wording and no solution-revealing sections.",
    ".gitignore": "A complete .gitignore tailored to Docker plus the selected host stack, excluding local artifacts while preserving committed task files that are required for the scenario.",
    ".env": "A root environment/configuration file with scenario-specific local defaults only if needed by the task; it must not be the sole source of required datastore initialization credentials.",
    "docker-compose.yml": "The complete Compose V2 file with no version field, 3-4 services, localhost-bound exposed ports, concrete service names, inline datastore initialization environment when needed, and intentional advanced Docker-layer defects.",
    "docker-compose.override.yml": "EXAMPLE ENTRY ONLY: include this concrete file only when the scenario uses an override or profile defect, with realistic local-environment wiring that participates in the Docker issue.",
    "run.sh": "The repository-root deployability script that resolves its own directory, pre-pulls every base and service image, builds and starts the stack with docker compose, reports status, avoids running the failing verification suite, and exits non-zero only for broken scaffold conditions.",
    "docker/entrypoints/api-entrypoint.sh": "A real executable entrypoint script for the api service that participates in lifecycle, permission, or signal-handling behavior without containing comments that reveal the fix.",
    "docker/entrypoints/worker-entrypoint.sh": "A real executable entrypoint script for the worker or sidecar service that participates in lifecycle, permission, or signal-handling behavior without containing comments that reveal the fix.",
    "docker/postgres/init_database.sql": "EXAMPLE ENTRY ONLY: include this concrete SQL file only when postgres is selected, with deterministic scenario data and credentials aligned to docker-compose.yml.",
    "verify/verify_stack.sh": "A concrete shell verification suite that resolves repo root dynamically, starts the stack, waits on health, checks readiness truthfulness, exercises service-to-service behavior by service name, sends SIGTERM and checks graceful shutdown, validates runtime constraints, verifies persistence if required, and tears down.",
    "tests/test_stack.py": "EXAMPLE ENTRY ONLY: use this concrete pytest verification file instead of verify/verify_stack.sh only if Python-based verification is selected, with the same observable Docker checks and repo-root-relative paths.",
    "services/api/Dockerfile": "A concrete per-service Dockerfile for the api service using the selected host stack base image and containing realistic advanced Docker-layer defects while remaining buildable.",
    "services/api/.dockerignore": "A concrete api build-context ignore file that is realistic and may be incomplete or mis-scoped as part of the Docker investigation.",
    "services/worker/Dockerfile": "A concrete per-service Dockerfile for the worker service using the same selected host stack and containing realistic advanced Docker-layer defects while remaining buildable.",
    "services/worker/.dockerignore": "A concrete worker build-context ignore file that is realistic and may be incomplete or mis-scoped as part of the Docker investigation.",
    "services/api/go.mod": "EXAMPLE ENTRY ONLY for a Go-selected task: the complete Go module manifest for the api service with minimal dependencies and no unnecessary packages.",
    "services/api/main.go": "EXAMPLE ENTRY ONLY for a Go-selected task: the complete correct api service source with graceful behavior expected by the scenario and no required candidate modification.",
    "services/api/internal/server/server.go": "EXAMPLE ENTRY ONLY for a Go-selected task: a concrete internal api module containing correct lightweight server logic relevant to the selected scenario.",
    "services/worker/go.mod": "EXAMPLE ENTRY ONLY for a Go-selected task: the complete Go module manifest for the worker service with minimal dependencies and no unnecessary packages.",
    "services/worker/main.go": "EXAMPLE ENTRY ONLY for a Go-selected task: the complete correct worker service source with observable cross-service behavior and no required candidate modification.",
    "services/api/package.json": "EXAMPLE ENTRY ONLY for a Node.js-selected task: the complete api package manifest with minimal scripts and dependencies needed for the scenario.",
    "services/api/server.js": "EXAMPLE ENTRY ONLY for a Node.js-selected task: the complete correct api server source with lightweight behavior and no required candidate modification.",
    "services/worker/package.json": "EXAMPLE ENTRY ONLY for a Node.js-selected task: the complete worker package manifest with minimal scripts and dependencies needed for the scenario.",
    "services/worker/worker.js": "EXAMPLE ENTRY ONLY for a Node.js-selected task: the complete correct worker source with observable cross-service behavior and no required candidate modification.",
    "services/api/pom.xml": "EXAMPLE ENTRY ONLY for a Java-selected task: the complete minimal api Maven manifest or equivalent Java manifest appropriate to the selected task.",
    "services/api/src/main/java/com/example/Main.java": "EXAMPLE ENTRY ONLY for a Java-selected task: the complete correct api service entry point with lightweight behavior and no required candidate modification.",
    "services/worker/pom.xml": "EXAMPLE ENTRY ONLY for a Java-selected task: the complete minimal worker Maven manifest or equivalent Java manifest appropriate to the selected task.",
    "services/worker/src/main/java/com/example/WorkerMain.java": "EXAMPLE ENTRY ONLY for a Java-selected task: the complete correct worker entry point with observable cross-service behavior and no required candidate modification.",
    "config/app.json": "A concrete scenario-specific configuration file when needed, containing realistic local defaults that may participate in Docker or Compose configuration wiring defects."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the Docker-layer remediations expected, including build-stage cleanup, cache-aware layer ordering, final-stage minimization, ownership and non-root fixes, writable filesystem design, truthful health orchestration, resource tuning, secure config handling, signal-safe entrypoints, and persistence validation without requiring application-source changes.",
  "definitions": "An object of Docker, Compose, runtime, filesystem, healthcheck, and scenario-specific term-to-definition pairs that clarify relevant concepts without giving away the exact fixes.",
  "hints": "A single-line nudge encouraging the candidate to compare what the stack reports with what containers actually do across build, startup, readiness, filesystem, and shutdown behavior, without naming the specific fixes.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable Docker improvements such as reliable healthy startup, truthful readiness, fast cached builds, graceful shutdown, non-root/read-only runtime safety, correct persistence, and stable service-to-service behavior.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, such as advanced Docker and Compose proficiency, comfort reading Dockerfiles and shell entrypoints, and familiarity with container health, signals, permissions, cgroups, and volumes; do not include setup or verification steps.",
  "short_overview": "A bullet list summarising the business problem, the advanced Docker operational focus, the 3-4 service stack shape, and the expected reliable production-like outcome in simple language."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be kebab-case, under 50 characters, and different from title
3. **title** must be a human-readable action-verb plus subject title, 50-80 characters
4. **code_files** must map real concrete file paths to complete file contents; do not emit placeholder-style filenames
5. **README.md** must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, and no other headings — each MUST be a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify). A plain unmarked text line with the section name is INVALID and counts as a missing section.
6. **Objectives** must be advanced, open-ended, stakeholder-oriented, and must not enumerate defects or name files, flags, commands, Dockerfile instructions, Compose keys, or implementation details
7. **Helpful Tips** must use varied action words and guide discovery without revealing fixes
8. **How to Verify** must use varied sentence openings and describe observable outcomes without setup commands or implementation details
9. **docker-compose.yml** MUST NOT include any version specification
10. **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every exposed service
11. For postgres, inline `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are required, and init SQL, healthcheck, and connection strings must align
12. The task MUST include docker-compose.yml, per-service Dockerfiles, entrypoint scripts, verification files, and run.sh
13. Do NOT include kill.sh
14. run.sh MUST pre-pull every base image before building and MUST NOT run the failing verification suite
15. run.sh, entrypoints, and verification files must use repo-root-relative paths and must not hardcode /root/task
16. The host application source must be correct and must not require modification
17. Defects must be advanced, interacting, and restricted to Docker, Compose, entrypoint, runtime, filesystem, resource, healthcheck, volume, or config layers
18. The task must be completable within {minutes_range} minutes for advanced Docker proficiency
"""

PROMPT_REGISTRY = {
    "Docker (ADVANCED)": [
        PROMPT_DOCKER_ADVANCED_CONTEXT,
        PROMPT_DOCKER_ADVANCED_INPUT_AND_ASK,
        PROMPT_DOCKER_ADVANCED_INSTRUCTIONS,
    ]
}