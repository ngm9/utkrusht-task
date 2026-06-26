# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GOLANG_KAFKA_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_KAFKA_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Golang and Kafka assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Golang and Kafka proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GOLANG_KAFKA_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Golang and Kafka, you are given a list of real world scenarios and proficiency levels for Golang and Kafka.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at a basic level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY POPULATED project that includes a small Go application and Kafka infrastructure already scaffolded for local execution.
The project should feel like a realistic day-to-day work item for a BASIC Golang and Kafka engineer, typically 1-3 years of experience, but the actual implementation scope must remain achievable in {minutes_range} minutes.
The candidate is expected to work on straightforward producer/consumer behavior, basic message validation or routing, simple topic usage, offsets or consumer-group behavior, graceful shutdown, and observable message flow in a development environment.
The candidate must not be required to make senior-level architecture decisions, design large distributed systems, implement advanced transactions, or perform deep cluster tuning.
A part of the task completion is to watch the candidate read an existing Go codebase, understand a small Kafka-backed workflow, and implement or fix a focused issue using fundamental Golang and Kafka knowledge.
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a straightforward feature, complete partially implemented code, or fix simple but realistic bugs in an existing Go + Kafka codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The question should be a real-world scenario that tests applied understanding and not just syntax memorization.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level and roughly 1 year of practical experience.
- **CRITICAL**: This is a BASIC Golang and Kafka task, so the candidate should be able to finish it within {minutes_range} minutes.
- **CRITICAL**: The task must be specific and constrained, not open-ended. It should focus on one small event-driven workflow rather than multiple unrelated requirements.
- **CRITICAL**: The task must assess practical Golang and Kafka usage together. It must not become a pure Kafka theory task or a pure Golang syntax task.
- For BASIC level of proficiency, the task should focus on practical day-to-day concepts such as:
  - Building and running a small Go service with `go build`, `go run`, and `go test`
  - Working with structs, slices, maps, functions, error returns, and standard library packages
  - Basic goroutines, channels, or `sync.WaitGroup` only where naturally needed for simple coordination
  - Producing messages to Kafka with basic reliability settings appropriate for development or small-scale workloads
  - Consuming messages from Kafka using a consumer group and handling simple success/failure paths
  - Understanding partitions, ordering within a partition, offsets, and how keys affect partitioning at a basic level
  - Handling graceful shutdown and making sure the producer or consumer exits cleanly
  - Applying simple retry or fallback logic where appropriate, without advanced transactional or exactly-once requirements
  - Verifying message flow with basic logs, simple scripts, or lightweight checks
  - Using simple JSON payloads and basic validation or transformation logic in Go
  - Using topic setup that reflects sensible basic choices such as partition count, retention, and replication assumptions suitable for local development
- The task may include a small amount of topic administration or validation through scripts or app startup logic, but it must remain basic and directly relevant to the candidate workflow.
- The task must NOT require advanced stream-processing frameworks, complex Kafka Connect pipelines, deep JVM tuning, multi-AZ capacity planning, advanced ACL design, or production-grade exactly-once semantics.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Go best practices and current Kafka development patterns while staying within basic scope.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Golang documentation, Kafka documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, and apply solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect basic Golang and Kafka proficiency while still requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to reason about message flow, correctness, reliability, and maintainable Go code in a small realistic service.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Golang and Kafka task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for BASIC proficiency level, keeping in mind that AI assistance is allowed.
- Tests practical Golang and Kafka skills that require more than a simple AI query to solve, while remaining fully achievable within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focuses on a small Go service that publishes to and/or consumes from Kafka for one clear business workflow.
- Uses realistic but basic Kafka behavior such as topic selection, partition-aware message keys, consumer-group reading, offset progression, or handling malformed messages.
- Encourages the candidate to reason about correctness, reliability, and simple observability in the event-driven flow.
- **CRITICAL**: any type of comments in the code files is strictly prohibited. The code files should not contain any comments at all.
- **CRITICAL**: The generated project must be runnable locally using Docker Compose for Kafka infrastructure and Go for the application.
- **CRITICAL**: Keep the Kafka setup simple and local-development oriented. A single broker setup is preferred for this BASIC task unless the chosen scenario absolutely requires one additional supporting container such as a UI or init container.
- **CRITICAL**: Do not make cluster administration the primary task. Kafka infrastructure exists to support the coding task, not to become the entire assessment.

## Infrastructure Requirements
- MUST include Kafka infrastructure required for the scenario using docker-compose.yml.
- MUST include a small Go application project using go.mod and Go source files.
- MUST include run.sh which has the responsibility of starting the local infrastructure and validating readiness.
- MUST include kill.sh which completely cleans up the task resources.
- MUST include a Dockerfile for the Go application if the application is run as a container within docker-compose.
- The project should provide a working local environment where Kafka is available and the Go app can be started or exercised.
- **IMPORTANT**: The infrastructure setup is automated through scripts and Docker Compose.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

### Docker-compose Instructions
- Include a Kafka service and any strictly necessary supporting service for a local development setup.
- A simple KRaft-based Kafka setup is preferred for this BASIC task to reduce unnecessary complexity.
- The compose file may include an app container for the Go service when appropriate.
- **MUST NOT include any version specification** in docker-compose.yml.
- **MUST NOT include environment variables or .env file references**.
- Use hardcoded configuration values instead of environment variables.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every exposed service.
- The Kafka service configuration must be complete enough for the local task to run successfully without manual editing.
- Include only the minimum required ports and services. Do not add unnecessary monitoring stacks, schema registry, or extra brokers unless the selected scenario truly needs them.
- If the app is containerized, ensure it depends on Kafka readiness appropriately.
- Docker paths and mounted files must correctly reference /root/task.

### Kafka Configuration Instructions
- Include any Kafka topic bootstrap or initialization behavior needed for the scenario.
- This can be handled by a small init script, app startup logic, or a dedicated lightweight setup container, as long as the setup remains simple and local.
- Topic choices must be basic and realistic, including sensible partition count and retention settings for the scenario.
- The task may involve one or two topics maximum.
- If the code exercises ordering, ensure the setup naturally supports reasoning about key-based partitioning without requiring advanced partition management.
- If the code exercises consumer behavior, ensure the starter project exposes enough logs or testable outputs to observe offsets, lag symptoms, or successful processing.
- Do not require advanced security configuration, complex connectors, or production-hardening steps as part of the main task.

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Start Docker containers using `docker compose up -d`.
- WAIT MECHANISM: Implement proper readiness checks to wait until Kafka is ready to accept client connections.
- VALIDATION: Validate that the Kafka service is reachable and that the local setup has started successfully.
- If the task includes an app container, validate that it has started successfully as well.
- The script should print clear progress logs for each step.
- The script should fail clearly if Kafka does not become ready in a reasonable time.
- The script may create topics or invoke lightweight readiness commands if required by the chosen setup.
- It must not install the runtime or common libraries using package managers.
- **FILE LOCATION**: All script paths and references must use /root/task.

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes, including named and anonymous volumes.
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task, including the Go app image and Kafka image if present locally for this project.
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed by using `|| true` where necessary.
  8. Print logs at every step so the user knows what is happening.
  9. After successful cleanup, print a final message exactly like: `Cleanup completed successfully!` or longer with the same meaning.
- Commands that should be included in equivalent form:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `rm -rf /root/task`
- Extra instruction:
  - The script should be idempotent and safe to run multiple times.
  - Always use `set -e` at the top to exit on error except when explicitly ignored.

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the Go application if the app is containerized in the scenario.
- Use an appropriate Go base image.
- Should set the working directory appropriately.
- Must build and run the Go application cleanly.
- Do not use environment variables or .env files.
- **CRITICAL**: Set WORKDIR to /root/task to match the file location.
- Keep the Dockerfile simple and aligned with BASIC-level project needs.

## OUTPUT
The output should be a valid json schema:
- `README.md` describing the candidate-facing task using the exact structure specified below
- `.gitignore` with sensible exclusions for Go, Docker, and local artifacts
- `go.mod` for the Go module
- `go.sum` if needed for dependencies
- `docker-compose.yml` for Kafka infrastructure used by the scenario
- `run.sh` for infrastructure startup and validation
- `kill.sh` for cleanup
- `Dockerfile` if the Go application is containerized
- Go code files that provide a runnable starter project without containing the full solution
- Any small scripts or config files needed to bootstrap the Kafka topic or local workflow

## Code file requirements
- Generate realistic folder structure following Go project conventions.
- Code should follow Go best practices with proper package organization.
- Use clear variable names and straightforward but well-structured logic.
- Focus on fundamental Go features while demonstrating proper project organization.
- Each package should have a clear, single responsibility.
- The generated code files must be valid and executable with `go build ./...` or a similarly straightforward Go command.
- Include test files using the standard `testing` package when appropriate for the scenario.
- **CRITICAL**: The generated code files should provide partial implementations that require basic completion or debugging.
- **CRITICAL**: The core Kafka message handling logic, validation logic, consumer processing path, or producer behavior that the candidate needs to implement or fix MUST be left incomplete or incorrect in a realistic way.
- DO NOT include any `TODO` or placeholder comments.
- **CRITICAL**: not include any comments in any file. Comments should not be there at all.
- DO NOT include comments that give away hints or solutions.
- The generated project should be runnable, but it can remain functionally incomplete until the candidate finishes the required task.
- The project should use common Go Kafka libraries appropriately for a basic local task.
- Keep the file count reasonable for a {minutes_range}-minute task.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore file that covers standard exclusions for Go, Docker, and local development tasks including binary executables, IDE configurations, compiled binaries, coverage files, log files, Docker override files if any, temporary task output files, and OS artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

### Task Overview
- MUST contain 3-4 meaningful sentences.
- No bullet list in this section.
- Describe the business scenario, current state of the Go + Kafka workflow, and why the problem matters.
- The content must be concrete and specific to the selected real-world scenario.
- NEVER leave this section empty.
- Do not include bold time-budget callouts.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Use 4-5 bullets maximum.
- Every bullet must start with an action word such as `Consider`, `Think about`, `Explore`, `Review`, or `Analyze`.
- Tips must guide discovery and reasoning.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Focus on areas such as message flow, ordering expectations, handling malformed events, shutdown behavior, reliability tradeoffs, and verifying the right data reaches the right downstream path.

### Objectives
- Use 4-6 bullets maximum.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the `what` and `why`, never the `how`.
- Each bullet must state an observable end-state, not a step, API choice, or library instruction.
- Focus on expected behavior of the Go service and Kafka-backed workflow, such as correct event handling, predictable message processing, resilient failure behavior, and maintainable code organization.

### How to Verify
- Use 4-6 bullets maximum.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run to confirm the system works correctly.
- Verification may mention observable logs, produced and consumed records, repeatable processing behavior, graceful shutdown behavior, and handling of invalid inputs or duplicate situations when relevant.

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands such as `go build`, `go test`, `go run`, `docker compose up`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like `you should implement`, `add this middleware`, `create this class`, or `use <specific API>`
- Any database or infrastructure access details beyond what is naturally observable from the local project files

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that reflects the Golang and Kafka task scenario.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, clearly describing the candidate task and different from the name field.",
  "question": "The full candidate-facing task description explaining the selected business scenario, the current Go and Kafka workflow, the observable problem, and the exact scope of what needs to be fixed or completed without revealing the solution.",
  "code_files": {{
    "README.md": "Candidate-facing README content containing the exact required sections in the correct order with concise, scenario-specific guidance.",
    ".gitignore": "A comprehensive ignore file suitable for a Go and Kafka local development task with Docker-related artifacts excluded where appropriate.",
    "go.mod": "The Go module manifest defining the module path and required dependencies for the starter project.",
    "go.sum": "The Go dependency checksum file when dependencies are required by the generated starter project.",
    "docker-compose.yml": "Docker Compose configuration that starts the Kafka datastore and any strictly necessary supporting services for the scenario without using version fields or environment variable references.",
    "run.sh": "A startup script that launches the Docker Compose infrastructure, waits for Kafka readiness, validates the local environment, and logs each step clearly.",
    "kill.sh": "A cleanup script that fully removes containers, volumes, networks, images, and the /root/task folder in an idempotent way.",
    "Dockerfile": "The Dockerfile for the Go application when the scenario runs the app in a container and needs an application image.",
    "cmd/app/main.go": "The Go application entry point that wires configuration, startup, shutdown, and the high-level application flow.",
    "internal/config/config.go": "Configuration definitions and simple loading helpers for application settings used by the starter project.",
    "internal/model/event.go": "Domain structs representing the Kafka message payloads or related application data used in the workflow.",
    "internal/kafka/producer.go": "Kafka producer setup and send-path starter code with partial or intentionally incomplete behavior that the candidate must reason about.",
    "internal/kafka/consumer.go": "Kafka consumer setup and processing loop starter code with partial or intentionally incomplete behavior relevant to the task.",
    "internal/service/service.go": "Core business logic that validates, transforms, routes, or records event processing outcomes for the selected scenario.",
    "internal/app/app.go": "Application orchestration code that connects the service layer with Kafka components and shutdown handling.",
    "internal/storage/storage.go": "A simple in-memory or file-backed helper package when the task needs lightweight local state to observe outcomes.",
    "internal/handler/handler.go": "A small supporting package for parsing, validation, or result handling when needed by the scenario.",
    "tests_or_additional_files": "Any additional Go source files, test files, scripts, or local configuration files required to make the starter project coherent, runnable, and appropriately incomplete for the assessment."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the reasoning, code areas, and Kafka behavior that a strong BASIC-level candidate is expected to address without dumping full code.",
  "definitions": "An object of term-to-definition pairs covering relevant Golang and Kafka concepts used in the task, written in simple language.",
  "hints": "A single line nudging the candidate toward a productive area of investigation without revealing the fix, exact API, or exact implementation approach.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable correctness of the Go service, Kafka message flow, and reliability behavior. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Go, Docker, Docker Compose, and basic Kafka producer-consumer understanding appropriate for this task.",
  "short_overview": "A bullet list summarising the business problem, the technical focus on Golang plus Kafka, and the expected end result after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case.
3. **title** must be human-readable, different from **name**, and in `<action verb> <subject>` format.
4. **code_files** must include README.md, .gitignore, go.mod, docker-compose.yml, run.sh, and kill.sh.
5. If an app container is used, **code_files** must also include Dockerfile.
6. The task must remain within BASIC Golang and Kafka scope and be completable within the allocated time.
7. The starter project must be runnable but must NOT contain the full solution.
8. **README.md** must follow the exact structure above with the exact section names and order.
9. Do not include setup commands or solution-revealing implementation details in README.md.
10. **MUST NOT include any version specification** in docker-compose.yml.
11. **MUST NOT include environment variables or .env file references**.
12. **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
13. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
14. If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
15. Keep the task focused on a realistic Go + Kafka work item such as fixing message handling, improving reliability of a producer/consumer path, or correcting a simple event-processing workflow — not on advanced cluster engineering.
"""

PROMPT_REGISTRY = {
    "Golang (BASIC), Kafka (BASIC)": [
        PROMPT_GOLANG_KAFKA_BASIC_CONTEXT,
        PROMPT_GOLANG_KAFKA_BASIC_INPUT_AND_ASK,
        PROMPT_GOLANG_KAFKA_BASIC_INSTRUCTIONS,
    ]
}