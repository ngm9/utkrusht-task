# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Go (Golang) and RabbitMQ assessment task.

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
- The task must reflect authentic messaging and Go service challenges that would be encountered in the role described in the role context
- The task should assess applied RabbitMQ usage from a Go service perspective, not memorization of broker commands, plugin installation, framework configuration, or library trivia

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, RabbitMQ topology context, Go service behavior, and production problem the candidate will be solving)
2. What will the task look like? (Describe the type of Go producer/consumer implementation, refactor, debugging task, or failure-handling improvement required, the expected deliverables, and how it aligns with INTERMEDIATE RabbitMQ and Go proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Go, RabbitMQ, AMQP 0-9-1, and production messaging systems, you are given a list of real world scenarios and proficiency levels for Go and RabbitMQ development.
Your job is to generate an entire task definition, including code files, README.md, docker-compose.yml, run.sh, kill.sh, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a messaging problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to operate as an intermediate RabbitMQ and Go engineer with roughly 3-5 years of relevant experience.
They should be able to reason about AMQP exchanges, queues, bindings, routing keys, connections, channels, acknowledgements, publisher confirms, prefetch, retry and dead-letter behavior, and apply those concepts in a Go service without needing step-by-step instructions.
The generated task must provide a FULLY FUNCTIONAL and FULLY POPULATED starter project that compiles and can connect to a local RabbitMQ broker, while leaving the core reliability, routing, lifecycle, idempotency, acknowledgement, retry, or concurrency decisions for the candidate.
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a realistic RabbitMQ-backed Go service feature, refactor an existing producer/consumer flow, or fix production-like bugs in the existing messaging codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just patch a single line.
- The question should be a real-world scenario that tests architectural thinking, RabbitMQ lifecycle reasoning, and idiomatic Go implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Go and RabbitMQ experience), ensuring that no two questions generated are similar.
- **CRITICAL**: Keep the task achievable within {minutes_range} minutes. The task should be bar-raiser style but scoped to one focused work item, not a full messaging platform build.
- **CRITICAL**: The task must focus on applied RabbitMQ usage from a Go service perspective. Do not ask for pure RabbitMQ command syntax, plugin installation steps, Helm setup, CI configuration, or exact library API memorization.
- **CRITICAL**: The candidate should work with a real RabbitMQ broker via docker-compose. Do not replace RabbitMQ behavior with an in-memory queue, fake broker, mocked AMQP server, or deterministic stand-in.
- **CRITICAL**: The starter project must be runnable and buildable before the candidate solves the task. It may have intentionally incomplete business behavior, safe no-op branches, logical flaws, or failing grader tests, but it must not contain syntax errors.
- The candidate should be asked to make pragmatic decisions around message lifecycle behavior, routing, acknowledgement timing, back-pressure, durability, idempotency, retry/dead-letter strategy, graceful shutdown, and error handling.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **RabbitMQ Topology Design**: exchanges, queues, bindings, routing keys, durable topology declarations, vhosts, and appropriate use of direct, fanout, topic, headers, or default exchange behavior.
  - **Message Lifecycle Reasoning**: publish, route, enqueue, deliver, ack, nack, reject, requeue, dead-letter, discard, and unroutable message handling using mandatory publishing concepts where appropriate.
  - **Producer and Consumer Structure in Go**: connection and channel reuse, avoiding per-message connections, startup topology declaration, publisher confirms, manual acknowledgements, reconnect-aware design, and graceful shutdown.
  - **Delivery Semantics**: at-most-once and at-least-once tradeoffs, application-level idempotency, duplicate handling, redelivery behavior, and why exactly-once is approximated outside the broker.
  - **Flow Control and Concurrency**: QoS prefetch, consumer concurrency, fairness versus throughput, avoiding goroutine leaks, using context cancellation, and preventing race conditions or deadlocks.
  - **Retry and Dead-letter Handling**: DLX/DLQ usage, TTL-driven retry loops or delayed delivery concepts, poison-message isolation, avoiding tight retry loops, and deciding when to drop, retry, requeue, or dead-letter.
  - **Message Contract Quality**: headers, properties, content-type, correlation-id, reply-to where relevant, JSON payload compatibility, optional fields, and trace or tenant identifiers.
  - **Observability and Troubleshooting**: queue depth, ready and unacked messages, publish and consume rates, connection and channel churn, DLQ growth, redelivery spikes, heartbeat timeouts, and routing or binding misconfiguration.
  - **Idiomatic Go Design**: interfaces, package organization, context propagation, error wrapping, custom errors, table-driven tests, dependency boundaries, and Go module structure.
  - **Operational Judgment**: safe remediation for stuck consumers, poison messages, retry storms, queue growth, and routine broker incidents while staying within intermediate-level scope.
- The task must NOT require advanced clustering operations, multi-region active-active designs, quorum queue tuning internals, BEAM VM debugging, mutual TLS implementation, OAuth2 plugin configuration, or large-scale platform automation as primary skills.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Go best practices (Go 1.18+) and current RabbitMQ client usage patterns.
- Tasks should require candidates to make reasonable architectural decisions and justify their approach through code and observable behavior.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, RabbitMQ documentation, Go documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate Go and RabbitMQ proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution for messaging reliability, delivery semantics, operational safety, and maintainable Go code.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Go and RabbitMQ task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years Go and RabbitMQ experience), keeping in mind that AI assistance is allowed.
- Tests practical Go and RabbitMQ skills that require architectural thinking, message lifecycle reasoning, failure handling, and concurrency awareness.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on a small production-like Go service with a RabbitMQ producer, consumer, worker, or request/reply component that needs reliability or routing improvements.
- Should test the candidate's ability to structure a scalable Go application that interacts with RabbitMQ safely.
- Generate a professional Go module using go.mod, go.sum, source files, tests, and scripts.
- The starter code must include a RabbitMQ connection path, topology setup entry point, and at least one producer or consumer flow, but must leave the important completion work to the candidate.
- The generated code files must be valid and executable with `go build ./...` after dependencies are installed.
- Include tests or test scaffolding that can be used by the candidate or grader to validate expected behavior. Grader-oriented tests may fail until the candidate completes the task, but the run.sh readiness script must not run those failing tests.
- Include realistic folder structure such as cmd/worker/, cmd/publisher/, internal/messaging/, internal/service/, internal/model/, internal/config/, internal/observability/, and internal/testsupport/ when appropriate.
- Include some existing interfaces, structs, configuration helpers, and utilities that the candidate needs to work with or extend.
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues, not syntactic errors, that require intermediate-level RabbitMQ and Go thinking to resolve.
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper interface design, lifecycle management, and messaging decisions.
- **CRITICAL**: Do not include comments that reveal the solution, exact acknowledgement strategy, exact retry loop, exact idempotency structure, or exact routing decisions.
- **CRITICAL**: Do not include TODO comments, placeholder comments, or comments like "add publisher confirms here", "implement worker pool", "nack this message", or "use this exchange".
- Use modern Go libraries only when helpful. The task may use the common AMQP Go client dependency, but the README must not reveal specific APIs or method names that solve the task.
- Prefer focused scenarios such as order fulfillment events, payment review work queues, notification routing, fraud-review retries, tenant-based topic routing, delayed retries, dead-letter remediation, or request/reply correlation, if those match the provided real-world scenarios.

## Infrastructure Requirements
- This is an infra-shaped task. The generated output MUST include docker-compose.yml, run.sh, and kill.sh.
- The external service for this task is RabbitMQ. Do not invent PostgreSQL, MySQL, Redis, Kafka, Elasticsearch, or any other datastore unless the selected real-world scenario explicitly requires it.
- The Go application should run locally against the RabbitMQ container. Do not create an application Dockerfile unless the selected scenario absolutely requires an app container.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The project must not rely on any .env file or host-specific environment variables for RabbitMQ startup. Inline service environment values are required in docker-compose.yml.
- Credentials in starter code may be local development credentials only and must be clearly scoped to the local docker-compose environment.
- run.sh is a readiness and self-check script, NOT the grader. It must install dependencies, start RabbitMQ, wait for health, validate the starter project builds or loads, and exit 0 on the UNSOLVED starter.
- run.sh MUST NOT run the grader test suite that is designed to fail until the candidate solves the task.

### Docker-compose Instructions
- Generate a docker-compose.yml file in /root/task/docker-compose.yml.
- **MUST NOT include any version specification** in docker-compose.yml.
- Include a RabbitMQ service using a management-enabled RabbitMQ image suitable for local development.
- The RabbitMQ container must define inline environment values for:
  - RABBITMQ_DEFAULT_USER
  - RABBITMQ_DEFAULT_PASS
  - RABBITMQ_DEFAULT_VHOST
- Do not use .env files, `${{VAR}}` host interpolation, or any host-provided indirection for the RabbitMQ service environment.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every service exposed to the host.
- RabbitMQ AMQP port 5672 must be bound as `127.0.0.1:5672:5672`.
- RabbitMQ management port 15672 may be exposed only as `127.0.0.1:15672:15672` if the task benefits from observability or troubleshooting through the management UI.
- Include a persistent named volume for RabbitMQ data only if the scenario benefits from restart or durability behavior. If included, kill.sh must remove it.
- Include a healthcheck that uses RabbitMQ diagnostics or another RabbitMQ-native readiness check.
- Use a deterministic container_name only if it helps scripts remain simple and reliable.
- The RabbitMQ URL used by Go code, run.sh checks, and README scenario assumptions must use the same local user, password, vhost, host, and port defined in docker-compose.yml.

### RabbitMQ Configuration Instructions
- The task must use RabbitMQ topology that is meaningful for the selected scenario, such as exchanges, queues, bindings, routing keys, DLX/DLQ, retry queues, or request/reply queues.
- Topology declarations should generally live in Go startup code so candidates can reason about durable topology recovery and application-owned messaging resources.
- If the starter code includes predeclared exchanges or queues, make sure their names are realistic, domain-specific, and not generic placeholders.
- The topology should be simple enough for an intermediate candidate to understand within the allocated time but rich enough to test RabbitMQ reasoning.
- The generated task may include one or more of the following, when appropriate to the scenario:
  - A direct, fanout, topic, headers, or default exchange.
  - Durable queues and persistent messages for reliability-sensitive flows.
  - Manual acknowledgements with clear observable consequences.
  - QoS prefetch or consumer concurrency boundaries.
  - Publisher confirms or unroutable-message handling expectations.
  - Dead-letter exchanges and dead-letter queues for poison-message isolation.
  - Retry behavior using routing, TTL, or delayed delivery concepts without requiring plugin installation.
  - Correlation identifiers and reply-to behavior for request/reply flows.
  - Message headers and properties for tenant, trace, schema version, or idempotency metadata.
- Do not require advanced cluster administration, RabbitMQ plugin installation, Shovel, Federation, Kubernetes, Terraform, Ansible, or production TLS setup as part of the candidate implementation.
- The task may ask the candidate to document or reason about tradeoffs, but the primary work should be implementable in Go against the local RabbitMQ container.

### Run.sh Instructions
- Generate a run.sh file in /root/task/run.sh.
- run.sh must start with a shebang and use strict shell behavior such as `set -euo pipefail`.
- run.sh's FIRST project action MUST install Go dependencies using the native Go module workflow, for example `go mod download`, from /root/task.
- run.sh must run from /root/task and reference /root/task explicitly where paths are needed.
- run.sh must start RabbitMQ using `docker compose up -d`.
- run.sh must wait until RabbitMQ is healthy before continuing. Use a retry loop with clear logs.
- run.sh must verify RabbitMQ readiness using docker compose health status, a RabbitMQ diagnostics command, or a small local AMQP connection smoke check.
- run.sh must verify the starter Go project compiles using `go build ./...`.
- run.sh may run only smoke checks that pass on the unsolved starter. It MUST NOT run tests that are intentionally designed to fail until the candidate solves the task.
- run.sh must print useful logs at every stage: dependency installation, broker startup, readiness waiting, build validation, and final readiness success.
- run.sh must exit 0 when the unsolved starter environment is ready.
- run.sh must be idempotent enough to run multiple times safely in /root/task.

## kill.sh file instructions
Create a kill.sh script that completely cleans up the task environment. It must:
1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print clear logs at every step so the user can see what is being cleaned up.
3. Change into /root/task if it exists, then stop and remove docker-compose services with `docker compose down --remove-orphans -v || true`.
4. Stop any remaining containers related to this task using labels, names, or project filters where possible, and use `|| true` for idempotency.
5. Remove named Docker volumes created for RabbitMQ or the docker-compose project, using `|| true` so the script can be run repeatedly.
6. Remove Docker networks created for the docker-compose project, using `|| true` for idempotency.
7. Force-remove any task-specific Docker images if any were created, using `docker rmi -f ... || true`. If no application image is created, still include a logged step that states no app image is expected.
8. Run `docker system prune -a --volumes -f || true` to aggressively remove leftover containers, images, networks, build cache, and volumes.
9. Remove the task directory with `rm -rf /root/task || true` and print the final message `Cleanup completed successfully!`.
- Every destructive Docker command must include `|| true` where appropriate so kill.sh is safe to run multiple times.
- kill.sh must not require any external environment variables.
- kill.sh must not prompt for confirmation.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (RabbitMQ service only unless the selected scenario explicitly requires another external service)
  - run.sh (Readiness script that installs Go dependencies, starts RabbitMQ, waits for health, verifies Go build, and exits successfully on the unsolved starter)
  - kill.sh (Complete cleanup script following the 9-step cleanup requirements)
  - go.mod (Go module definition)
  - go.sum (Go dependencies checksum - can be empty initially when appropriate)
  - .gitignore (Standard Go project gitignore)
  - Go source files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Go test files or test scaffolding where appropriate. These may validate message contracts, topology decisions, idempotency behavior, or consumer lifecycle behavior.
  - Code files should demonstrate partial architecture that candidate needs to complete or extend.
  - Include realistic folder structure such as cmd/worker/, cmd/publisher/, internal/messaging/, internal/service/, internal/model/, internal/config/, internal/observability/, internal/testsupport/, and pkg/ where appropriate.

## Code file requirements
- Generate realistic folder structure following Go project conventions.
- Code should follow Go best practices and demonstrate intermediate-level patterns.
- Use appropriate Go idioms, interfaces, composition, context propagation, and error wrapping.
- Focus on modern Go features (Go 1.18+) and development best practices.
- Include RabbitMQ-specific code paths that are realistic but incomplete enough to require candidate reasoning.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion.
- Include some existing interfaces, structs, message types, configuration types, and utilities that need to be extended or integrated.
- The core RabbitMQ lifecycle decisions, acknowledgement handling, retry strategy, idempotency strategy, publisher confirmation handling, routing behavior, graceful shutdown, or concurrency control that the candidate needs to implement MUST be left for the candidate to design.
- The starter code must compile with `go build ./...` after `go mod download`.
- Do not include syntax errors.
- Do not rely on hidden files to make the starter project compile.
- Do not include any 'TODO' or placeholder comments.
- Do not include comments that give away hints or solutions.
- Do not include comments like "Add nack here", "Use DLQ here", "Implement publisher confirms here", "Use prefetch here", or "Create worker pool here".
- Do not add comments that reveal solution or implementation details.
- The generated project structure should be compilable with `go build ./...`, but will require implementation to function correctly under the candidate-facing requirements.
- Provide realistic dependencies in go.mod that intermediate developers should be familiar with, especially a maintained Go AMQP client if RabbitMQ interaction is implemented.
- Any tests included must be realistic and must not require network access beyond the local RabbitMQ container.
- If tests need RabbitMQ, make sure they can read the same local connection configuration used by docker-compose and run.sh.
- Avoid requiring global Go tools, system package installation, or apt-get. The Go runtime is pre-installed by the environment.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Go and local infrastructure projects including binary executables, vendor directories, IDE configurations (.idea/, .vscode/, .DS_Store), compiled binaries, coverage files (*.out, *.test), log files, temporary files, local RabbitMQ data artifacts if any are mounted into the project, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

- The README.md file content MUST be fully populated with meaningful, specific content.
- Task Overview section MUST contain the exact business scenario from the task description.
- ALL sections must have substantial content - no empty or placeholder text allowed.
- Content must be directly relevant to the specific task scenario being generated.
- Use concrete business context, not generic descriptions.
- The README must NOT contain setup commands.
- The README must NOT contain database or broker connection details such as host, port, username, password, vhost, client-tool suggestions, or management UI instructions.
- The README must NOT contain `<DROPLET_IP>` placeholders.
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions.

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why reliable RabbitMQ-backed Go service behavior matters for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper message lifecycle decisions are crucial.
Do not use a bullet list in this section.
Do not include bold time-budget callouts.

### Helpful Tips
Provide practical guidance without revealing specific implementations.
This section must contain 4-5 bullets max.
Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
Frame suggestions around RabbitMQ and Go principles and outcomes rather than specific implementation details.
Examples of proper framing:
  - "Consider how message ownership changes as work moves through the broker and service."
  - "Think about how the service should behave when processing succeeds, fails temporarily, or cannot safely continue."
  - "Explore how concurrent processing can improve throughput without hiding failure signals."
  - "Review how message metadata can help trace work across services."
  - "Analyze how repeated failures should become visible instead of looping indefinitely."

### Objectives
This section must contain 4-6 bullets max.
Frame objectives around outcomes rather than specific technical implementations. Objectives describe the 'what' and 'why', never the 'how'.
Each bullet must state an observable end-state, not a step or an API/library to use.
Objectives should be measurable but not prescribe specific patterns or approaches.
Guide candidates to think about reliability, delivery behavior, routing correctness, maintainability, observability, concurrency safety, and idiomatic Go.
Examples of proper framing:
  - "Ensure messages reach the intended business workflow and failures become observable."
  - "Create behavior that preserves useful work while preventing unsafe duplicate side effects."
  - "Support concurrent processing while maintaining predictable shutdown behavior."
  - "Keep message contracts understandable and compatible with downstream consumers."
  - "Make failure paths clear enough for operators to diagnose queue growth or redelivery spikes."
**CRITICAL**: Objectives describe the "what" and "why", never the "how".

### How to Verify
This section must contain 4-6 bullets max.
Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
Each bullet is a check the candidate can run or observe, such as test output, response shape, message movement, queue depth behavior, log line, redelivery count, or successful build.
Include both functional testing and architectural assessment criteria.
Guide candidates to test functionality, edge cases, failure scenarios, concurrency safety, shutdown behavior, and message lifecycle outcomes.
Examples of proper framing:
  - "Verify that successful work is recorded once and does not remain stuck as unacknowledged work."
  - "Confirm temporary failures are visible and do not cause an uncontrolled retry loop."
  - "Check that invalid or poison messages can be isolated for later investigation."
  - "Validate that concurrent processing does not produce duplicate side effects or data races."
  - "Confirm the service shuts down without losing in-flight work."
**CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section):**
Make sure you keep the following out of the README.md file:
  - Setup commands such as `go mod download`, `go build`, `go test`, `go run`, `docker compose up`, `docker compose down`, or any equivalent setup command.
  - Direct solutions or architectural decisions.
  - Step-by-step implementation guides.
  - Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
  - Code snippets that give away the answer.
  - Exact acknowledgement, retry, prefetch, publisher-confirm, idempotency, routing, or dead-letter implementation details.
  - Interface names or specific implementation strategies that would reveal the solution.
  - Broker connection details such as host, port, username, password, vhost, management UI URL, or client-tool suggestions.
  - Directive phrases like "you should implement", "add this middleware", "create this class", "create this interface", "use this specific API", or "make sure to add".

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "A short, descriptive, kebab-case GitHub repository name under 50 characters that reflects the RabbitMQ and Go task without using spaces or punctuation other than hyphens.",
   "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, different from the name, and specific to the selected business scenario.",
   "question": "A detailed candidate-facing task description that explains the business scenario, the existing Go and RabbitMQ starter system, the specific reliability or routing problem to solve, and the observable requirements without including hints or direct implementation instructions.",
   "code_files": {{
      "README.md": "The complete candidate-facing README content with exactly the Task Overview, Helpful Tips, Objectives, and How to Verify sections, written concisely and without setup commands or solution-revealing details.",
      ".gitignore": "A comprehensive Go and local-infrastructure gitignore covering binaries, coverage outputs, logs, IDE files, temporary files, and local runtime artifacts that should not be committed.",
      "docker-compose.yml": "A RabbitMQ-only docker-compose configuration with no version field, localhost-only port bindings, inline RabbitMQ user password and vhost environment values, a healthcheck, and any required volume definitions.",
      "run.sh": "A readiness script that installs Go module dependencies, starts RabbitMQ with docker compose, waits for broker health, verifies the starter project builds, prints clear logs, and exits successfully on the unsolved starter without running failing grader tests.",
      "kill.sh": "A complete cleanup script that stops compose services, removes task containers volumes networks images and /root/task, runs docker system prune with volumes, uses idempotent guards, and prints Cleanup completed successfully at the end.",
      "go.mod": "The Go module definition with a realistic module path, Go version, and necessary dependencies for RabbitMQ integration and testing.",
      "go.sum": "The Go dependency checksum file content or an empty string when the generated starter dependencies do not require precomputed checksums.",
      "cmd/worker/main.go": "A compilable Go worker entry point that loads local configuration, initializes the messaging components, starts the relevant consumer or service loop, and leaves the core candidate work incomplete without solution-revealing comments.",
      "cmd/publisher/main.go": "A compilable Go publisher or sample producer entry point when useful for the scenario, allowing local message flow checks while leaving important reliability behavior for the candidate.",
      "internal/config/config.go": "Configuration loading code for local RabbitMQ settings and service behavior that compiles and avoids host-specific secret dependencies.",
      "internal/model/message.go": "Domain message types, metadata structures, and validation-oriented fields relevant to the selected business scenario.",
      "internal/messaging/topology.go": "Starter RabbitMQ topology declaration code with realistic exchange queue and binding concepts appropriate to the scenario while leaving key design decisions for the candidate.",
      "internal/messaging/producer.go": "Starter producer code that can publish representative messages but requires candidate work for the scenario-specific reliability or routing requirements.",
      "internal/messaging/consumer.go": "Starter consumer code that can receive messages but requires candidate work for acknowledgement timing, failure behavior, idempotency, concurrency, or shutdown requirements.",
      "internal/service/service.go": "Business service code that represents the domain workflow and provides integration points for messaging behavior without containing the completed solution.",
      "internal/observability/logging.go": "Minimal logging or event-recording helpers that support observable behavior without dictating the candidate's implementation strategy.",
      "internal/testsupport/fixtures.go": "Deterministic test fixtures or helper data for local validation of message contracts and service behavior.",
      "internal/messaging/messaging_test.go": "Go tests or test scaffolding that validate expected message lifecycle behavior, routing outcomes, or failure handling and may fail until the candidate completes the task.",
      "starter_code_file_name": "Any additional starter source file path needed for the selected scenario, with compilable content that supports the task without revealing the solution.",
      "starter_code_file_name_2": "Any second additional starter source file path needed for the selected scenario, with realistic content and no placeholder comments."
   }},
   "answer": "An evaluator-facing high-level solution approach describing the expected RabbitMQ topology, Go lifecycle handling, delivery semantics, failure behavior, concurrency considerations, and tradeoffs without requiring one exact implementation.",
   "definitions": "An object mapping relevant RabbitMQ and Go terms to concise definitions, covering concepts such as exchange, queue, binding, routing key, acknowledgement, dead-letter queue, prefetch, publisher confirm, idempotency, context cancellation, and graceful shutdown when relevant.",
   "hints": "A single line hint nudging the candidate toward investigating message lifecycle, failure visibility, and safe Go service boundaries without revealing the specific fix or implementation approach.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable messaging reliability, correct routing or retry behavior, safe concurrent processing, and maintainable Go architecture. Use simple english.",
   "pre_requisites": "A bullet-point list of tools and knowledge needed, including intermediate Go modules and testing familiarity, RabbitMQ and AMQP concepts, docker compose usage for local services, and basic understanding of producer consumer workflows.",
   "short_overview": "A bullet-point list summarising the business problem, the RabbitMQ and Go technical focus, and the expected outcome emphasizing reliability, observability, and correct message lifecycle behavior."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be 50-80 characters, human-readable, and different from name.
4. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, kill.sh, go.mod, go.sum, and Go source files.
5. **README.md** must follow exactly four sections: Task Overview, Helpful Tips, Objectives, How to Verify.
6. **README.md** must not include setup commands, broker connection details, direct solutions, architecture decisions, or step-by-step implementation guidance.
7. **docker-compose.yml** must not include a version field and must bind every exposed RabbitMQ port to localhost only.
8. **RabbitMQ service environment values must be inline** in docker-compose.yml and must not use .env files or `${{VAR}}` host interpolation.
9. **run.sh** must install Go dependencies first, start RabbitMQ, wait for health, run a starter build check, and must not run failing grader tests.
10. **kill.sh** must follow the required cleanup sequence, include `docker system prune -a --volumes -f || true`, remove /root/task, and print `Cleanup completed successfully!`.
11. **Starter code** must be compilable and runnable enough for readiness checks but must NOT contain the solution.
12. **No TODO comments or solution-revealing comments** may appear in starter code.
13. **hints** must be a single line and must not reveal the fix.
14. **definitions** must include relevant RabbitMQ and Go terms for the generated task.
15. **Task must be completable within the allocated time** for INTERMEDIATE proficiency.
16. **Use Go 1.18+** conventions throughout.
"""

PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE), RabbitMQ (INTERMEDIATE)": [
        PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_CONTEXT,
        PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_GOLANG_RABBITMQ_INTERMEDIATE_INSTRUCTIONS,
    ]
}