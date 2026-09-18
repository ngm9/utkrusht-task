# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_DOCKER_JAVA_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

A backend software engineer with intermediate Java and Docker proficiency is expected to maintain production-ready Spring Boot services and the Docker-based runtime packaging used in development, staging, and limited production environments. Their work includes implementing and debugging REST APIs, managing Maven or Gradle builds, integrating with relational persistence, writing tests, externalizing configuration safely, and creating secure, reproducible container images and Compose stacks. They should be comfortable troubleshooting build, startup, networking, storage, logging, resource, and health-check issues across Java applications and Docker infrastructure while making pragmatic tradeoffs that are appropriate for a 3-5 year engineer.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DOCKER_JAVA_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java and Docker assessment task.

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
- The generated task must be an infra-shaped Java Spring Boot task with Docker Compose, Dockerfile, run.sh, and PostgreSQL initialization because this assessment exercises containerized application delivery with a real datastore

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Java and Docker implementation, diagnosis, or improvement required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DOCKER_JAVA_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java Spring Boot, Docker containerization, Compose-based deployment, and production runtime troubleshooting, you are given a list of real world scenarios and proficiency levels for Docker and Java.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to diagnose, improve, and harden a realistic containerized Java service at an intermediate level.
The candidate's primary responsibility is to improve a FULLY FUNCTIONAL Spring Boot service and its Docker runtime setup without being handed the exact solution. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a realistic Java Spring Boot backend service with a BASIC WORKING Docker and PostgreSQL setup that is functional but not production-ready. The application includes:
- A FULLY FUNCTIONAL Spring Boot REST API with controllers, services, DTOs, persistence, configuration, and tests in a realistic project layout
- A FULLY POPULATED PostgreSQL database initialized through init_database.sql with enough sample data to explore the behavior
- A BASIC WORKING Dockerfile and docker-compose.yml that start successfully but contain intermediate-level containerization, runtime, networking, configuration, health, security, caching, logging, or persistence issues to improve
- Maven build configuration, Spring profiles, actuator endpoints, and application configuration that are realistic for a containerized Java service
- Multiple interacting Java modules/files so the candidate must reason about configuration boundaries, runtime behavior, and maintainability rather than edit one obvious snippet

The candidate should be able to complete the task within {minutes_range} minutes. The task should reflect intermediate proficiency (3-5 years experience): it should require real Docker and Java judgment, but it must not require expert-only platform architecture, multi-region orchestration, custom Docker plugins, or Kubernetes design.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, descriptive, and clearly describe the intermediate-level Java + Docker containerization scenario.
- Task must ask the candidate to improve, diagnose, or harden a containerized Java Spring Boot service that already runs with a PostgreSQL datastore.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL and deployable on first run. The candidate explores a working baseline first, then improves it.
- **CRITICAL**: Because this is INTERMEDIATE proficiency, the starter codebase MUST be substantial and realistic, NOT a toy snippet. Require multiple interacting modules/files in a real Spring Boot project layout, with non-trivial existing logic the candidate must read and reason about before changing.
- **CRITICAL**: Changes should span more than one file across Docker runtime configuration and Java/Spring configuration or service boundaries. Do NOT ship only a single short file or one obvious broken line.
- **CRITICAL**: The question scenario must be clear and reproducible, but the candidate-facing question MUST NOT name exact files, directories, functions, methods, classes, variables, line numbers, Docker directives, or direct solution statements. The candidate must diagnose where and what to change from the scenario and codebase.
- **CRITICAL**: The task should assess Docker and Java together: deterministic image builds, build context, layer caching, runtime configuration, Docker networking, Compose orchestration, health/readiness behavior, resource limits, persistence boundaries, non-root runtime, logging, and Java environment/profile handling.
- **CRITICAL**: The Java application should be production-shaped and maintainable. Java changes may include configuration externalization, actuator/security readiness behavior, temporary-work-directory handling, safe cleanup, logging, or persistence access adjustments, but the task must stay within intermediate Java scope.
- The task must not require custom Docker plugins, multi-region platforms, Kubernetes cluster architecture, advanced cloud IAM, or large-scale platform design.
- The task should leave room for multiple valid approaches. It may ask the candidate to review and improve an existing implementation, diagnose a deployment failure, reduce container risk, make runtime behavior safer, or explain tradeoffs through code/config changes.
- The task should use a concrete business scenario inspired by one provided real-world scenario, such as a logistics dispatch API, media processing service, order workflow, healthcare event intake, or another provided domain.
- The generated repository must include enough sample data and endpoints to make the system behavior observable without requiring external third-party services.
- The task must require a real datastore because task_shape is infra. Use PostgreSQL as the required datastore for this Java Spring Boot service. Include Redis only if the selected scenario explicitly requires caching behavior and the code actually exercises it; otherwise do not add Redis.
- The question must NOT include hints. The hints will be provided only in the "hints" field and must still avoid revealing the fix.
- Ensure that all questions and scenarios adhere to modern Java 17+ and current Docker Compose best practices.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, Java documentation, Spring Boot documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization
- Tasks should involve multi-layered Java and Docker challenges that require understanding of application configuration, container builds, networking, persistence, health, resource constraints, and production-readiness tradeoffs
- Candidates may use AI to help with boilerplate or syntax, but the assessment should still require their own engineering judgment about Docker runtime behavior and Java service design

## Code Generation Instructions
Based on the real-world scenarios provided, create a Java + Docker task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed
- Tests practical Docker and Java skills through a realistic Spring Boot service running with PostgreSQL
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- Generate a complete Spring Boot project using Java 17+ and Maven unless the selected scenario strongly suggests Gradle
- Include a BASIC WORKING Dockerfile and docker-compose.yml that are deployable, but leave meaningful production-readiness gaps for the candidate to improve
- Include a real PostgreSQL datastore initialized by init_database.sql with realistic schema and seed data
- Include application code that is complete enough to compile, boot, connect to the datastore, expose API behavior, and demonstrate the runtime issue or improvement target
- Include a small test suite or smoke-test class that compiles and can be run separately by the candidate, but do not make run.sh depend on a failing grader suite
- Avoid direct TODO comments, solution-shaped comments, or comments like "add a healthcheck here", "use a non-root user", "switch to service DNS", "create a volume", or "implement multi-stage build"
- Make the candidate-facing README concise and open-ended so the candidate discovers the implementation approach

## Infrastructure Requirements
- MUST include a complete Java Spring Boot service with a realistic package structure and Maven build.
- MUST include docker-compose.yml for the Java service and PostgreSQL datastore.
- MUST include init_database.sql to create and seed the PostgreSQL schema used by the service.
- MUST include run.sh that installs project dependencies, starts the Compose services, waits for datastore health and application readiness, verifies that the starter compiles/loads, and exits successfully on the unsolved starter.
- MUST include Dockerfile because this task assesses Java application containerization.
- MUST include .dockerignore so the baseline can be reviewed and improved if needed.
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so no cleanup script is needed.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The infrastructure setup must be automated and runnable from /root/task.

### Docker-compose Instructions
- Generate docker-compose.yml using Compose syntax without a top-level version field.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- Include a PostgreSQL service and a Java application service.
- PostgreSQL MUST set the standard initialization environment variables inline under the service: POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB. These values must match init_database.sql assumptions, healthcheck credentials, and the application connection string.
- Forbid .env files and host-side variable indirection such as `${{POSTGRES_USER}}` or `${{DATABASE_URL}}`. Inline service environment values are allowed and required for local assessment reliability.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host. Use `127.0.0.1:5432:5432` if PostgreSQL is exposed.
- If the application port is published, bind it to localhost as well, for example `127.0.0.1:8080:8080`.
- Include a real PostgreSQL healthcheck that uses the same user and database configured in the service environment.
- Use service DNS names inside containers for service-to-service communication; never use localhost for a container connecting to another container.
- Include named volumes for PostgreSQL persistence and any scenario-required runtime data. Use tmpfs only where scratch data should not persist.
- Include an application dependency relationship that waits for datastore health before the application starts.
- Include sensible baseline networking, restart behavior, logging considerations, and resource constraints that are realistic but may still be improved by the candidate.
- Do not include unrelated datastores simply because they are available in the template.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else (flags, paths, `&&`, the rest of the pipeline) becomes bash's positional parameters and is silently dropped (e.g. `mkdir -p /a && tail -f /dev/null` breaks into `mkdir: missing operand`). Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.

### init_database.sql Instructions
- Generate a complete init_database.sql file for PostgreSQL.
- The SQL must create all tables required by the Spring Boot service and insert realistic seed rows.
- The SQL must be idempotent enough for local assessment use where possible, using safe create statements and predictable seed data.
- Use table and column names that match the JPA mappings or JDBC queries in the Java code.
- Do not include credentials, hostnames, or connection strings in init_database.sql.
- Keep the schema realistic but small enough for an intermediate task completed within {minutes_range} minutes.
- Include data that allows the candidate to observe the problematic or non-production-ready runtime behavior through normal API usage.

### Run.sh Instructions
- Generate run.sh as an executable Bash script located at /root/task/run.sh.
- The script must start with `#!/usr/bin/env bash` and use robust error handling while still distinguishing readiness failures from candidate-solution failures.
- The FIRST step must install or resolve the task's own Java dependencies using the runtime-native manifest, for example `./mvnw -q -DskipTests package` if a Maven wrapper is generated, or `mvn -q -DskipTests package` when relying on Maven in the template.
- The primary runtime itself is pre-installed by the E2B template. Do NOT apt-get install Java, Maven, Docker, or system runtimes.
- The script must use /root/task as the base directory and `cd /root/task` before running project commands.
- The script must use `docker compose up -d --build` or an equivalent Compose v2 command to start the PostgreSQL datastore and application service.
- The script must wait for PostgreSQL to become healthy using docker compose health/status or pg_isready through the service container.
- The script must wait for the Java application to become reachable through an observable readiness endpoint or a lightweight API request on localhost.
- The script must verify the starter compiles/loads and the basic deployment is up, then exit 0 on the unsolved starter.
- The script is a READINESS/self-check, NOT the grader. It MUST NOT run the grader test suite or depend on tests that are designed to fail until the candidate solves the task.
- If you include a visible test suite, candidates may run it separately with Maven, but run.sh should only verify deployability and baseline readiness.
- Print concise status messages so candidates know whether dependencies, containers, datastore readiness, and app readiness succeeded.
- Do not include cleanup behavior in run.sh.

### Dockerfile Instructions
- Generate a Dockerfile for the Spring Boot application.
- The Dockerfile must be functional and build successfully in the starter repository.
- The baseline Dockerfile may be intentionally non-ideal in ways that require intermediate improvement, such as image size, cache behavior, runtime user, build determinism, layer ordering, metadata, health behavior, or build context assumptions.
- Do not make the Dockerfile syntactically broken; the initial deployment must succeed.
- Use a Java 17+ compatible base image family appropriate for Spring Boot.
- The task may require the candidate to improve multi-stage build design, dependency caching, minimal runtime image choice, non-root execution, health/readiness checks, labels, .dockerignore usage, BuildKit-friendly patterns, or JVM container resource behavior, but do not reveal the exact changes in candidate-facing text.
- Do not require expert-only multi-architecture buildx/qemu implementation unless it is framed as an optional discussion or tradeoff, not a mandatory deliverable.
- Do not bake secrets into image layers, build args, labels, or source files.
- Keep the Dockerfile aligned with Maven packaging and the generated application artifact.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Working Compose setup for Spring Boot and PostgreSQL, no version field)
  - Dockerfile (Functional baseline application container build)
  - .dockerignore (Docker build-context exclusions appropriate for Java projects)
  - run.sh (Readiness script that installs dependencies, starts Compose services, waits for health, and exits 0 on the starter)
  - init_database.sql (PostgreSQL schema and seed data)
  - pom.xml (Maven build configuration with Spring Boot, testing, actuator, validation, and PostgreSQL dependencies)
  - .gitignore (Java, Maven, Docker, IDE, logs, and local data exclusions)
  - src/main/resources/application.yml (Default Spring Boot configuration)
  - src/main/resources/application-docker.yml (Container profile configuration with datastore connectivity and runtime settings)
  - src/main/java/com/example/containerlab/Application.java (Spring Boot main application class)
  - src/main/java/com/example/containerlab/config/ActuatorSecurityConfig.java (Security or actuator configuration relevant to readiness without leaking the task solution)
  - src/main/java/com/example/containerlab/controller/DispatchController.java (REST controller exposing scenario behavior)
  - src/main/java/com/example/containerlab/service/DispatchService.java (Service layer with realistic business flow)
  - src/main/java/com/example/containerlab/service/RoutePlanningService.java (Supporting service containing non-trivial logic)
  - src/main/java/com/example/containerlab/repository/DispatchRepository.java (Persistence interface)
  - src/main/java/com/example/containerlab/model/Dispatch.java (JPA entity)
  - src/main/java/com/example/containerlab/dto/DispatchRequest.java (Request DTO)
  - src/main/java/com/example/containerlab/dto/DispatchResponse.java (Response DTO)
  - src/main/java/com/example/containerlab/exception/ApiExceptionHandler.java (Exception mapping and logging-safe error responses)
  - src/test/java/com/example/containerlab/DispatchServiceTest.java (Small visible test or smoke test that is not used by run.sh as a failing grader)

## Code file requirements
- Generate a realistic Spring Boot folder structure under /root/task with multiple interacting Java files.
- Java code should follow modern Java 17+ and Spring Boot best practices with dependency injection, layered design, validation, logging, and clean exception handling.
- **CRITICAL**: The generated code files should be complete, compilable, and bootable.
- **CRITICAL**: The starter system must run successfully with the provided Compose stack before the candidate starts.
- **CRITICAL**: The project should contain meaningful existing logic and configuration so an intermediate candidate must reason across Docker, Compose, Spring profiles, persistence, runtime health, and operational behavior.
- The core Docker and Java runtime decisions that the candidate needs to improve MUST be left for the candidate to design.
- Do NOT include any 'TODO' or placeholder comments in Java code.
- Do NOT include comments that reveal hints or solutions.
- Do NOT include comments like "change this to service DNS", "add non-root user", "create a tmpfs", "fix healthcheck", "optimize layer cache", or "use multi-stage build".
- Do NOT include candidate-facing text that names exact files, methods, properties, Docker directives, or configuration keys to change.
- The Java code should avoid sensitive-data leakage in logs and should include enough logging to diagnose runtime behavior.
- The application should use PostgreSQL through Spring Data JPA or JDBC in a way that is realistic for intermediate Java developers.
- Include Maven dependencies for Spring Web, validation, actuator, data access, PostgreSQL, testing, and any small utility library that is genuinely needed.
- The Docker and Compose files must reference /root/task as the base directory where appropriate.
- Use localhost only for host-side verification commands and published ports. Do not use droplet IP placeholders anywhere.

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Java Spring Boot and Docker development that includes:
- Maven build directories and generated artifacts such as target/
- IDE files such as .idea/, .vscode/, *.iml, .classpath, .project, and .settings/
- Java compiled files such as *.class, *.jar, and *.war
- Log files and runtime logs such as *.log and logs/
- Local Spring configuration such as application-local.yml and application-local.properties
- Docker local data directories and mounted data folders
- OS-specific files such as .DS_Store and Thumbs.db
- Any other standard exclusions for Java/Spring Boot/Docker development

## README.md INSTRUCTIONS
- The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
- Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.
- The README.md contains exactly the following sections in this order and no others:
  1. Task Overview
  2. Objectives
  3. Helpful Tips
  4. How to Verify
- Each of the four README sections MUST be emitted as an actual markdown heading using the same heading level consistently: `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify`.
- A plain unmarked text line with the section name is INVALID and counts as a missing section.
- The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected business scenario.
- The README must NOT contain setup commands such as Maven install commands, Docker Compose commands, package installation commands, or instructions to run run.sh.
- The README must NOT contain database connection details such as host, port, username, password, database name, connection strings, or database client-tool suggestions.
- The README must NOT contain `<DROPLET_IP>` placeholders or any remote-host placeholder. There is no droplet; the task runs inside an E2B sandbox.
- If any legitimate verification text mentions host access, it must use localhost.

### Task Overview
- Must be 3-4 meaningful sentences.
- Must use no bullet list.
- Must describe the business scenario, current state, and why the problem matters operationally.
- Must mention that the service already runs but needs production-readiness improvements in its Java/Docker runtime behavior.
- Must be concise, specific, and never empty.
- Must not contain bold time-budget callouts.
- Must not name exact files, methods, Docker directives, property keys, database credentials, or direct solution steps.

### Objectives
- Must contain 3-4 bullets max because this is INTERMEDIATE proficiency.
- Objectives MUST be concise and OPEN-ENDED.
- Each objective states ONE desired outcome as a full, natural sentence, roughly 10-24 words.
- Each objective must be written from a stakeholder's point of view, such as an operator, on-call engineer, downstream consumer, or end user.
- Each objective must say who relies on this and why it matters operationally, not just what the code should do.
- Describe the what and why, NEVER the how.
- Do NOT name any API, library, framework, Docker directive, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, or other direct code reference.
- Do NOT describe the current broken behavior or use phrasing like "currently does X" or "after your changes".
- State the desired end-state as a standing requirement, not a before/after diff.
- BAD: "Use a multi-stage Dockerfile to reduce image size."
- BAD: "Fix application-docker.yml so the service connects to dispatch-db."
- BAD: "Add a healthcheck to docker-compose.yml."
- GOOD: "Operators should be able to roll out the service quickly without wasting bandwidth or disk on unnecessary artifacts."
- GOOD: "On-call engineers should be able to trust startup signals before routing customer traffic to a new container."

### Helpful Tips
- Must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery and tradeoff analysis; they MUST NOT name the specific API, library, function, pattern, data structure, Docker directive, Compose field, or algorithm that solves the task.
- Tips may point candidates toward broad concerns such as build context, runtime isolation, service communication, persistence boundaries, startup signals, resource behavior, and diagnostic observations.
- Do NOT include commands, exact configuration keys, exact endpoints, exact file names, exact property names, or specific implementation choices.

### How to Verify
- Must contain 3-5 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as successful deployment readiness, response behavior, container restart behavior, log clarity, image footprint, resource readings, or persistence behavior.
- Verification text may mention localhost if discussing host-side access, but must not include database credentials, database client commands, or droplet placeholders.
- Do NOT include setup commands or step-by-step deployment instructions.
- Do NOT reveal exact Docker directives, exact Spring properties, exact method names, or exact files to inspect.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Make sure you do not include the following in the README.md file:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, `mvn spring-boot:run`, `gradle bootRun`, or instructions to run run.sh
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, Docker directives, Compose field names, Spring property names, pattern names, or data-structure names that reveal the solution
- Code snippets or configuration snippets that give away the answer
- Database connection details including host, port, username, password, database name, connection strings, or client-tool suggestions
- `<DROPLET_IP>` placeholders or any remote-host placeholder
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", "add HEALTHCHECK", "use multi-stage builds", or "set this property"

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the Java and Docker production-readiness task without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, clearly describing the containerized Java service improvement.",
  "question": "A candidate-facing scenario paragraph plus a direct imperative ask that describes the business problem and expected outcome without leaking file names, paths, function names, method names, class names, exact configuration keys, Docker directives, line numbers, or direct solution statements.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (`## Task Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify`) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "A comprehensive Java, Maven, Spring Boot, Docker, IDE, log, OS, and local runtime artifact ignore file appropriate for this repository.",
    ".dockerignore": "A Docker build-context exclusion file for a Java Spring Boot project that keeps local build artifacts, IDE files, VCS data, logs, and unnecessary development files out of image builds.",
    "pom.xml": "A complete Maven build descriptor for Java 17+ with Spring Boot web, validation, actuator, data access, PostgreSQL, logging, and test dependencies needed by the starter service.",
    "docker-compose.yml": "A working Compose v2 file with no version field that defines the Spring Boot application and PostgreSQL datastore, localhost-bound published ports, inline PostgreSQL initialization environment, health checks, networking, and persistence suitable for candidate improvement.",
    "Dockerfile": "A functional baseline Dockerfile for the Spring Boot service that builds and runs successfully while leaving intermediate-level image, security, caching, metadata, and runtime-readiness improvements for the candidate to discover.",
    "run.sh": "An executable readiness script that runs from /root/task, resolves Maven dependencies, builds the starter artifact, starts the Compose stack, waits for PostgreSQL and application readiness, performs a lightweight smoke check, and exits 0 on the unsolved starter without running the grader tests.",
    "init_database.sql": "A complete PostgreSQL initialization script that creates the schema and seed data used by the Spring Boot service without including credentials or connection strings.",
    "src/main/resources/application.yml": "Default Spring Boot configuration for local application settings that does not expose secrets and remains consistent with the generated code.",
    "src/main/resources/application-docker.yml": "Container profile configuration for the Spring Boot service that supports the Docker runtime and PostgreSQL connectivity without relying on .env files or host-side variable substitution.",
    "src/main/java/com/example/containerlab/Application.java": "The Spring Boot main application class for the generated service.",
    "src/main/java/com/example/containerlab/config/ActuatorSecurityConfig.java": "A Spring configuration class for health and security behavior relevant to container readiness while avoiding comments that reveal the candidate solution.",
    "src/main/java/com/example/containerlab/controller/DispatchController.java": "A REST controller exposing realistic scenario operations through clean request and response handling.",
    "src/main/java/com/example/containerlab/service/DispatchService.java": "A service-layer class containing meaningful business workflow logic that interacts with persistence and supporting services.",
    "src/main/java/com/example/containerlab/service/RoutePlanningService.java": "A supporting service with realistic non-trivial logic that gives the project enough depth for intermediate Java reasoning.",
    "src/main/java/com/example/containerlab/repository/DispatchRepository.java": "A persistence repository interface matching the generated domain model and initialized PostgreSQL schema.",
    "src/main/java/com/example/containerlab/model/Dispatch.java": "A JPA entity representing the main domain object used by the scenario and database schema.",
    "src/main/java/com/example/containerlab/dto/DispatchRequest.java": "A request DTO with validation annotations appropriate for the generated REST API.",
    "src/main/java/com/example/containerlab/dto/DispatchResponse.java": "A response DTO that presents scenario results without exposing internal persistence details.",
    "src/main/java/com/example/containerlab/exception/ApiExceptionHandler.java": "A centralized exception handler that returns safe, useful API errors and demonstrates production-style Java structure.",
    "src/test/java/com/example/containerlab/DispatchServiceTest.java": "A small visible Java test or smoke test that supports candidate self-checking and is not required by run.sh to pass a failing grader gate."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected Docker and Java runtime improvements, including build determinism, image efficiency, secure runtime posture, service networking, readiness behavior, persistence boundaries, resource/logging considerations, and minimal maintainable Java configuration changes without requiring one exact implementation.",
  "definitions": "An object mapping 5-7 relevant Docker and Java terms to concise definitions, such as image layer, build context, Compose service DNS, health check, named volume, Spring profile, and JVM container memory awareness.",
  "hints": "A single-line investigation hint that nudges the candidate toward comparing build-time, startup-time, and runtime container behavior without naming the specific fix, files, directives, or configuration keys.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements to deployability, startup confidence, image/runtime efficiency, container security posture, persistence safety, and maintainable Java configuration using simple English.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Java 17 and Spring Boot familiarity, Maven project comfort, Docker/Compose operational knowledge, and basic PostgreSQL-backed service understanding; do not include imperative setup, install, run, configure, or verify steps.",
  "short_overview": "A bullet list summarizing the business problem, the Java Spring Boot and Docker technical focus, and the expected production-readiness outcome in simple language."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown wrapper, no explanations, and no code fences.
2. The JSON must include exactly the canonical top-level keys: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, and short_overview.
3. **name** must be kebab-case, under 50 characters, and different from **title**.
4. **title** must be human-readable, 50-80 characters, and in `<action verb> <subject>` format.
5. **question** must not leak the answer: no file names, paths, directories, methods, classes, variables, exact config keys, Docker directives, line numbers, or direct solution statements.
6. **code_files** must include README.md, .gitignore, .dockerignore, pom.xml, docker-compose.yml, Dockerfile, run.sh, init_database.sql, and all concrete Java source files listed in the schema.
7. Do NOT include kill.sh.
8. docker-compose.yml must not include a version field and must not use .env files or `${{VAR}}` host-side substitutions.
9. PostgreSQL must use inline POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB values that match init_database.sql, healthchecks, and application connectivity.
10. Datastore ports must be bound to localhost only, for example `127.0.0.1:5432:5432`.
11. run.sh must install/resolve Maven dependencies first, use docker compose up, wait for health, perform deployability checks, and exit 0 on the unsolved starter without running failing grader tests.
12. README.md must contain exactly `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify` in that order, with no extra README sections.
13. README.md must not contain setup commands, database connection details, droplet placeholders, direct solutions, code snippets, or step-by-step implementation guides.
14. The starter project must be FULLY FUNCTIONAL and realistic, with multiple interacting files appropriate for INTERMEDIATE Java and Docker proficiency.
15. Keep the task within Docker and Java intermediate scope: production-ready first-class Docker features and maintainable Java/Spring service work, not expert platform architecture.
"""

PROMPT_REGISTRY = {
    "Docker (INTERMEDIATE), Java (INTERMEDIATE)": [
        PROMPT_DOCKER_JAVA_INTERMEDIATE_CONTEXT,
        PROMPT_DOCKER_JAVA_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_DOCKER_JAVA_INTERMEDIATE_INSTRUCTIONS,
    ],
}