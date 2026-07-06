# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GOLANG_KAFKA_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, especially focusing on how Go services use Kafka in production-grade event-driven systems at an intermediate level?
"""

PROMPT_GOLANG_KAFKA_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Go and Apache Kafka assessment task.

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

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and Kafka-backed Go service problem the candidate will be solving)
2. What will the task look like? (Describe the type of Go implementation, Kafka integration fix, expected deliverables, and how it aligns with INTERMEDIATE Go + Kafka proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GOLANG_KAFKA_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Go, Apache Kafka, distributed messaging systems, and event-driven backend services, you are given a list of real world scenarios and proficiency levels for Go and Kafka.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a Kafka-backed Go service problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL and deployable Go application with a BASIC WORKING Kafka setup. The infrastructure must start successfully, Kafka must be reachable by the Go service, and the starter application must provide enough realistic behavior for the candidate to explore before making changes.

The candidate's primary responsibility is to improve a production-style Go Kafka service that has realistic intermediate-level reliability, throughput, delivery guarantee, offset handling, schema compatibility, or observability gaps. The task should evaluate both Go engineering skill and Kafka reasoning: idiomatic package structure, context-aware goroutines, bounded concurrency, error wrapping, testability, consumer offset strategy, partition-aware processing, idempotency, retry behavior, dead-letter handling, message metadata, and operational logging.

The starting environment must be FULLY POPULATED with source files, Go module files, Docker infrastructure, topic setup, and test scaffolding. It may include deliberate production-readiness problems, but it must not contain syntax errors, missing dependencies, broken Docker wiring, or incomplete files that prevent the candidate from building, running, and investigating the system.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a focused feature from scratch, refactor existing Go Kafka code, or fix complex bugs in an existing event-driven Go codebase.
- **CRITICAL**: The task must align with INTERMEDIATE proficiency level for Go and Kafka, suitable for a developer with 3-6 years of Go experience and practical Kafka production exposure.
- **CRITICAL**: The task must be completable within {minutes_range} minutes, so keep the implementation scope focused to 3-4 meaningful objectives rather than a broad platform build.
- **CRITICAL**: The initial Kafka and Go deployment MUST be successful and functional. Candidate explores first, then improves reliability, correctness, throughput, or observability.
- **CRITICAL**: The task should test applied work rather than trivia, installation, memorized command flags, pure syntax, or broad Kafka administration.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix errors.
- The question should be a real-world scenario that tests architectural thinking and practical event-driven debugging, not just implementation skills.
- For INTERMEDIATE level of proficiency, the task should test a focused subset of these capabilities:
  - **Idiomatic Go Design**: interfaces, composition, package boundaries, context propagation, custom errors, error wrapping, and testable abstractions.
  - **Go Concurrency Safety**: goroutines, channels, bounded worker execution, cancellation, synchronization, graceful shutdown, avoiding race conditions and goroutine leaks.
  - **Kafka Consumer Correctness**: consumer group behavior, partition-aware processing, offset commit timing, retryable failures, dead-letter routing, and avoiding message loss or duplicate side effects.
  - **Kafka Producer Reliability**: message keys, headers, delivery guarantees, batching trade-offs, idempotent publishing concepts, and structured error handling.
  - **Kafka Data Modeling**: topic naming, partition key choice, schema-compatible payload evolution, header metadata, and safe handling of old and new event versions.
  - **Operational Observability**: structured logs with topic, partition, offset, key, correlation identifiers, lag-related signals, and meaningful wrapped errors.
  - **Testing and Verification**: Go unit tests, integration tests against Kafka where useful, table-driven tests, and race-aware validation.
- Prefer scenarios such as a lagging consumer group, unsafe offset commits, duplicate processing, hot partitions, schema evolution failures, retry and dead-letter gaps, producer reliability problems, or missing observability in a Go Kafka worker.
- Avoid requiring advanced Kafka Streams, ksqlDB, Flink, multi-cluster disaster recovery, complex Kafka Connect deployment, Kubernetes operators, TLS/SASL security setup, or deep broker administration as the primary task.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Go best practices and current Kafka client development standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Go documentation, Kafka documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- The complexity of the tasks should reflect intermediate Go and Kafka proficiency while requiring genuine engineering judgment that goes beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution for reliability, maintainability, and operational clarity.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Go + Kafka task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level, keeping in mind that AI assistance is allowed.
- Tests practical Go and Kafka skills that require architectural thinking, concurrency reasoning, delivery guarantee awareness, and production-oriented debugging.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on a Go service or small set of Go packages that publish to or consume from Kafka topics.
- Should test the candidate's ability to structure a maintainable Go application while reasoning about Kafka message flow and failure behavior.
- The starter application should be buildable with `go build ./...` and testable with `go test ./...`.
- The generated task should include meaningful tests or a lightweight harness that exposes the production-readiness issue without handing the solution to the candidate.
- Use common Go Kafka client libraries that are reasonable for an intermediate developer, but do not require the candidate to install system packages manually.
- Keep the Kafka infrastructure simple: one broker is sufficient unless the selected scenario explicitly requires broker-level replication reasoning.
- Do not include any datastore configuration beyond Kafka unless the selected real-world scenario explicitly requires another external service.

## Infrastructure Requirements
- MUST include a complete, fully functional Go application that integrates with Kafka.
- MUST include BASIC WORKING Kafka setup with the topic or topics needed for the selected scenario.
- MUST include working docker-compose.yml with Kafka and the Go application service.
- MUST include a run.sh script with the end-to-end responsibility of deploying the infrastructure, waiting for Kafka readiness, creating topics, and validating the Go service or worker startup.
- Do NOT include kill.sh. E2B sandboxes are destroyed as a whole when the session ends, so container cleanup is automatic.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- **CRITICAL**: The infrastructure setup is automated and MUST work on first deployment.
- **CRITICAL**: The candidate should not need to install Go, Kafka, Docker, or common libraries manually from run.sh.

### Docker-compose Instructions
- Include a Kafka broker service and a Go application service.
- Use Kafka in a simple local development mode appropriate for an assessment. Use ONLY `confluentinc/cp-kafka:7.6.1` as the Kafka Docker image — do NOT use `bitnami/kafka` (image no longer available on Docker Hub).
- Use hardcoded service configuration values and Docker service names for internal container communication.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- **MUST NOT include environment variables or .env file references**.
- Do not include an `.env` file and do not reference one from compose, run.sh, Dockerfile, Go code, or README.md.
- If Kafka requires configuration, provide it through explicit command arguments or mounted configuration files rather than environment variable blocks.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Bind the Kafka host listener to localhost only if it is exposed for diagnostics.
- Application ports, if exposed, should also prefer localhost bindings for the local assessment environment.
- Ensure Kafka is healthy before the Go service starts consuming or publishing.
- Include named volumes only when needed for Kafka runtime data.
- The compose file must be valid and deployable from `/root/task`.

### Kafka Configuration Instructions
- Include only the Kafka topics required by the selected scenario.
- Topic names should be realistic and versioned when appropriate, such as business-event-name.v1 or business-event-name.v2.
- Configure minimal baseline topic settings that allow the starter system to work, while leaving the candidate to improve application-level reliability, message handling, or configuration decisions required by the task.
- If the scenario involves retries or failed events, include a topic that can support failure observation without explicitly solving the retry strategy for the candidate.
- If the scenario involves schema evolution, include representative old and new sample messages or fixtures in the Go test files rather than introducing a full Schema Registry unless the scenario specifically requires it.
- Do not require advanced broker operations, multi-node replication, rack awareness, or security setup as the primary work.
- Avoid asking the candidate to memorize Kafka CLI flags; topic creation in run.sh should be automated.

### Run.sh Instructions
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- The script must `cd /root/task` before running project commands.
- PRIMARY RESPONSIBILITY: Starts all services using `docker compose up -d --build`.
- WAIT MECHANISM: Implements a readiness loop that waits for Kafka to accept broker operations before topic creation and service validation.
- TOPIC CREATION: Creates the required Kafka topics with baseline settings if they do not already exist.
- VALIDATION: Validates that the Go application container starts and that a basic smoke check succeeds.
- TEST DATA: Optionally produces a small number of representative events only if needed for the selected scenario.
- MONITORING: Prints concise deployment status, service health, and any useful local URLs without adding database credentials or manual setup steps to the README.
- ERROR HANDLING: If startup fails, print recent compose logs and exit with a non-zero status.
- **FILE LOCATION**: All commands and paths must assume `/root/task` as the base directory.
- Do not include `apt-get install`, `go install`, `pip install`, `npm install`, or runtime installation commands.

### Dockerfile Instructions
- MUST be complete and functional for the Go application service.
- Use a multi-stage or otherwise reproducible Go build appropriate for local assessment infrastructure.
- The Dockerfile must build the Go module from `/root/task`, run the application binary, and expose only the port needed by the scenario.
- Do not use environment variables or .env files for required configuration.
- Do not include comments that reveal the candidate's solution.
- The Dockerfile should support fast rebuilds by copying Go module files before the full source tree when appropriate.
- **CRITICAL**: Dockerfile must work correctly for initial deployment.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - go.mod (Go module definition)
  - go.sum (Go dependencies checksum, populated when dependencies require it)
  - .gitignore (Standard Go, Kafka, Docker, and IDE exclusions)
  - docker-compose.yml (Complete working Kafka and Go service setup with no version field)
  - Dockerfile (Complete and functional Go application Dockerfile)
  - run.sh (Complete setup script that starts Kafka, creates topics, waits for readiness, and validates the app)
  - Any Go source files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Any Go test files, fixtures, or sample message files needed to verify the expected behavior.
  - Include realistic folder structure such as cmd/worker/, internal/consumer/, internal/producer/, internal/events/, internal/codec/, internal/service/, internal/logging/, and testdata/ where appropriate.

## Code file requirements
- Generate realistic Go folder structure with clear package boundaries.
- Code should follow Go best practices and demonstrate intermediate-level patterns.
- Use appropriate Go idioms, interfaces, context propagation, error wrapping, structured logging, and composition patterns.
- Use modern Go module conventions and include dependencies that intermediate developers should be familiar with.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion.
- **CRITICAL**: The generated project structure should be compilable and deployable, but tests or scenario behavior may expose the reliability issue the candidate must fix.
- Include Kafka producer or consumer code that is basic and functional but has focused production-readiness gaps aligned to the selected scenario.
- Include some existing interfaces, structs, utilities, tests, or harness code that the candidate needs to work with or extend.
- The core architectural decisions, Kafka delivery behavior, concurrency control, offset handling, retry behavior, schema compatibility, or observability solution that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT include comments like "commit after processing", "add worker pool here", "implement dead-letter topic", "cache schema here", or "use idempotency key".
- DO NOT add comments that reveal Kafka configuration values, Go patterns, functions, data structures, or algorithms that solve the task.
- Include tests that are meaningful but do not prescribe the implementation approach.
- Include race-safety or concurrency-oriented test guidance when the selected scenario involves goroutines or shared state.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Go, Kafka, and Docker projects including binary executables, vendor directories, IDE configurations (.idea/, .vscode/, .DS_Store), compiled binaries, coverage files (*.out, *.test), log files, Kafka local data directories, Docker volume directories, temporary files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content.
Task Overview section MUST contain the exact business scenario from the task description.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific Go + Kafka task scenario being generated.
Use concrete business context, not generic descriptions.
The README must NOT contain database-connection details, Kafka broker connection details, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences.
- Do not use a bullet list in this section.
- It must describe the business scenario, current state, and why the problem matters.
- It must NEVER be empty.
- It must not include bold time-budget callouts.
- It should explain why correct Go and Kafka behavior matters for reliability, latency, data correctness, or operational stability without revealing the implementation approach.

### Objectives
- Objectives must contain 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix. A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like. It does NOT name the API, library, pattern, or algorithm that solves it. Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Improve consumer performance."
- GOOD: "The reminder worker falls behind during normal appointment spikes and can lose failed messages; after your changes it should keep up with the provided workload while preserving retryable failures."
- Objectives should cover both functional behavior and code quality outcomes appropriate for intermediate Go and Kafka.
- Objectives should be measurable but must not prescribe exact Kafka APIs, Go functions, design patterns, commit calls, worker-pool details, or configuration values.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Tips should guide candidates toward reasoning about message ordering, offset safety, retries, backpressure, schema compatibility, concurrency safety, and observability only when those areas are relevant to the selected scenario.
- Examples of proper framing:
  - "Consider how failures should affect whether a message is treated as completed."
  - "Think about how parallel work can change ordering guarantees for records that share the same partition."
  - "Explore what information would help an operator diagnose a stuck or repeatedly failing event."
  - "Review how older and newer event shapes can coexist during a rolling deployment."

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run, such as test output, response shape, latency observation, log line, consumer progress, retry behavior, or race-safety result.
- Include verification for normal paths, failure paths, and at least one operational signal when relevant.
- Do not reveal the exact implementation approach, function names, Kafka API calls, or configuration values in the verification instructions.
- Verification can mention broad commands like `go test ./...` or `go test -race ./...` when appropriate, but it must not provide step-by-step setup instructions.

Directive — CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
- Setup commands such as `go mod tidy`, `go build`, `go test`, `go run`, `docker compose up`, or similar installation and deployment steps.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Specific Kafka configuration parameters, exact commit strategies, exact retry topic design, or exact partitioning implementation details that give away the answer.
- Code snippets that give away the answer.
- Database connection details, Kafka broker connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", "call this method", or "configure the following".

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that clearly reflects the Go and Kafka task domain without duplicating the display title.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on the Go Kafka reliability or messaging problem.",
  "question": "A detailed candidate-facing task description explaining the selected business scenario, the current Go Kafka service behavior, the specific reliability or performance problem, and what outcomes the candidate must achieve without revealing the implementation.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify, fully populated and non-revealing.",
    ".gitignore": "A comprehensive ignore file covering Go build outputs, coverage files, IDE files, Docker artifacts, Kafka local data, logs, and temporary files.",
    "go.mod": "A Go module definition with realistic dependencies for the generated Go Kafka application and tests.",
    "go.sum": "The Go dependency checksum file corresponding to the dependencies included in go.mod.",
    "docker-compose.yml": "A complete Docker Compose configuration with Kafka and the Go application service, no version field, no environment variable or .env references, and localhost-only host bindings for datastore ports.",
    "Dockerfile": "A complete Dockerfile that builds and runs the Go application from /root/task and supports the automated deployment.",
    "run.sh": "A complete executable setup script that starts services with docker compose, waits for Kafka readiness, creates required topics, validates startup, and prints concise status.",
    "cmd/worker/main.go": "The Go application entry point that wires configuration, logging, Kafka producer or consumer components, context cancellation, and graceful startup behavior.",
    "internal/consumer/consumer.go": "Kafka consumer starter code that is functional but leaves the selected intermediate reliability, concurrency, offset, retry, or observability issue for the candidate to solve.",
    "internal/producer/producer.go": "Kafka producer starter code included when the selected scenario requires publishing events, with enough implementation to exercise the task without revealing the final reliability design.",
    "internal/events/events.go": "Domain event structs, validation helpers, or message metadata types needed by the selected scenario, including compatibility fixtures when schema evolution is relevant.",
    "internal/service/service.go": "Business processing logic or interfaces that the Kafka layer calls, designed to be realistic and testable without prescribing the solution.",
    "internal/logging/logging.go": "Logging setup or helpers that allow structured operational output without directly solving the observability requirement.",
    "internal/config/config.go": "Hardcoded local assessment configuration for Kafka topics, broker addresses, and service settings without environment variable or .env dependencies.",
    "internal/consumer/consumer_test.go": "Go tests or table-driven tests that validate the expected candidate-facing behavior for the selected Kafka consumer problem.",
    "internal/events/events_test.go": "Go tests for event decoding, validation, schema compatibility, or metadata behavior when relevant to the scenario.",
    "testdata/sample-events.jsonl": "Representative Kafka message fixtures for normal, edge, old-version, new-version, or failure-path cases when useful for the task.",
    "additional files": "Any additional Go source, test, fixture, or configuration files required to make the generated task complete, runnable, and realistic."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected Go and Kafka reasoning, key design trade-offs, and production-readiness improvements without requiring a single exact implementation.",
  "definitions": "An object mapping 5-7 relevant Go concurrency and Kafka messaging terms used in the task to concise candidate-friendly definitions.",
  "hints": "A single line nudging investigation toward the most important Go Kafka reliability or observability concern without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements to message correctness, reliability, throughput, observability, and idiomatic Go quality. Use simple english.",
  "pre_requisites": "Exactly 2-3 concise bullets covering the runtime/toolchain, local project environment, and key Go Kafka knowledge needed; each bullet must be 120 characters or fewer.",
  "short_overview": "Exactly 3 plain sentences: the first states what Go Kafka system is being built or improved, the second states what the candidate must do, and the third states what success looks like. Do not use label prefixes."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and different from `name`.
4. **code_files** must include README.md, .gitignore, go.mod, go.sum, docker-compose.yml, Dockerfile, run.sh, and realistic Go source and test files.
5. **Do NOT include kill.sh** because E2B sandboxes are destroyed as a whole when the session ends.
6. **KAFKA IMAGE**: Use ONLY `confluentinc/cp-kafka:7.6.1` — NEVER `bitnami/kafka` (removed from Docker Hub; sandbox will fail to pull it).
7. **docker-compose.yml must NOT have a `version:` field**.
7. **docker-compose.yml, Dockerfile, run.sh, Go code, and README.md must NOT include environment variables or .env file references**.
8. **GO DEPENDENCIES**: Use ONLY the Go standard library and `github.com/segmentio/kafka-go` — do NOT add `go.uber.org/zap`, `gorilla/mux`, `gin`, or any other external package. The go.sum must match go.mod exactly.
9. **DOCKERFILE**: The Dockerfile MUST run `RUN go mod tidy` before `RUN go build` to ensure all checksums are resolved. Do NOT rely on `go mod download` alone.
10. **SECURITY-CRITICAL**: datastore ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
11. **Initial deployment MUST succeed** — Kafka must be ready, required topics must exist, and the Go service must start successfully.
12. **Task must be completable within the allocated time** for INTERMEDIATE proficiency.
13. **NO comments in code** that reveal the solution.
14. **README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify** and must not contain setup commands, connection details, or solution-revealing guidance.
15. **short_overview** must be exactly 3 plain sentences with no label prefixes.
16. Focus on practical Go Kafka application work: delivery behavior, offset safety, message modeling, concurrency, retries, idempotency, lag, observability, and tests.
"""

PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE), Kafka (INTERMEDIATE)": [
        PROMPT_GOLANG_KAFKA_INTERMEDIATE_CONTEXT,
        PROMPT_GOLANG_KAFKA_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_GOLANG_KAFKA_INTERMEDIATE_INSTRUCTIONS,
    ],
}