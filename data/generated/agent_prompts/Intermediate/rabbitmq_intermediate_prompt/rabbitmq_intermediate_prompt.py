# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_RABBITMQ_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a INTERMEDIATE RabbitMQ assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must be a RabbitMQ-focused infrastructure and messaging-design task requiring practical AMQP 0-9-1 judgement, topology repair, delivery-semantics reasoning, and operational correctness.
- It must be completable within {minutes_range} minutes by a candidate with 3-5 years of RabbitMQ experience.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build, fix, or improve, and how does it match INTERMEDIATE RabbitMQ level?
"""

PROMPT_RABBITMQ_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements (RabbitMQ)

## GOAL
As a technical architect super experienced in RabbitMQ and AMQP 0-9-1, you are given a list of real world scenarios and proficiency levels for RabbitMQ. Generate a complete assessment task — description, starter files, RabbitMQ infrastructure, README — that tests a candidate at INTERMEDIATE proficiency. The task must be a realistic messaging work item that evaluates practical topology design, delivery semantics, reliability trade-offs, and troubleshooting judgement rather than trivia.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to have 3-5 years of hands-on experience building and operating RabbitMQ-backed workflows. They should be comfortable with exchanges, queues, bindings, routing keys, virtual hosts, users and permissions, durable topology declaration, publisher/consumer message lifecycle, acknowledgements, nacks, requeue decisions, dead-letter exchanges, retry queues, TTLs, prefetch, publisher confirms conceptually, correlation IDs, message properties, and operational visibility through the management UI or HTTP API.

The generated task must provide a FULLY FUNCTIONAL RabbitMQ local environment. The broker should start cleanly, expose the management UI only on localhost, and include enough broken or incomplete starter topology/configuration for the candidate to improve without needing to fix environment setup. The candidate's job is to fix the RabbitMQ task, not repair Docker, shell scripts, missing files, or invalid JSON.

## INSTRUCTIONS
- The task asks the candidate to implement, repair, or improve a RabbitMQ messaging workflow using infrastructure files and RabbitMQ topology definitions.
- The candidate should work with practical RabbitMQ artifacts such as `docker-compose.yml`, `rabbitmq.conf`, `definitions.json`, optional seed messages or topology notes, and verification scripts.
- The task must focus on 4-5 intermediate RabbitMQ concepts selected from the competency scope: exchange type selection, routing key and binding design, durable queues, alternate exchanges, DLX/DLQ, delayed retry using TTL plus DLX, manual ack/nack semantics, prefetch/back-pressure, idempotency metadata, correlation IDs, message TTL, queue length limits, and operational observability.
- Generate enough starter configuration to give a clear starting point WITHOUT giving away the solution.
- The starter RabbitMQ topology MUST be runnable and loadable, but it should represent the exact "Current Implementation" buggy or incomplete state described in the candidate question.
- Do NOT require advanced cluster operations, Kubernetes, Terraform, Helm, quorum-queue internals, Erlang/BEAM debugging, multi-region active-active messaging, extreme capacity planning, OAuth2/LDAP setup, mutual TLS certificate rotation, or organization-wide broker architecture.
- Do NOT create a task that primarily tests memorized CLI syntax, installing tools, language-library syntax, or definitions-only knowledge.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### Nature of the Task
**CRITICAL**: This is an INTERMEDIATE RabbitMQ task. It should require applied judgement, debugging, and implementation trade-offs, but it must not become a senior distributed-systems architecture exercise.

**CRITICAL**: The task must be infra-shaped. It MUST include RabbitMQ as an external broker service using Docker Compose. The generated files must include `docker-compose.yml`, `run.sh`, and `kill.sh`.

**CRITICAL**: The candidate-facing task should simulate a realistic work item such as:
- Replacing over-broad direct routing with topic routing and durable per-consumer-group queues.
- Adding alternate exchange handling for unroutable messages.
- Replacing immediate requeue retry loops with TTL retry queues and a DLQ.
- Correcting ack/nack and prefetch behavior to reduce message loss or redelivery storms.
- Separating tenant, region, or event-type routing without forcing consumers to filter unrelated messages in application code.
- Improving message metadata such as `correlation-id`, `content-type`, routing key convention, retry count headers, and idempotency keys.

**CRITICAL**: The task must include an intentionally incomplete or flawed "Current Implementation" that is observable from the starter files. Examples include a direct exchange with one broad routing key, queues missing DLX arguments, a retry queue that dead-letters to the wrong exchange, an unrouted event path that silently drops messages, non-durable critical queues, or missing metadata conventions. The flaw must be realistic and fixable within the time box.

**CRITICAL**: The task must avoid asking the candidate to build a fake broker, fake RabbitMQ client, or purely theoretical design document. The deliverable should include concrete RabbitMQ topology/configuration changes plus concise documentation or verification notes.

**CRITICAL**: The RabbitMQ container, management UI, and topology load path must be FULLY FUNCTIONAL before the candidate begins. `run.sh` is a readiness and self-check script only; it must not run a hidden grader or fail because the candidate has not solved the task yet.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, RabbitMQ documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The assessment is designed to evaluate the candidate's ability to understand, adapt, debug, and deliver working RabbitMQ solutions in a realistic environment. External resources are allowed because professional engineers routinely use documentation and tools.

Candidates must still produce their own final work. They should understand and be able to explain the changes they make, the trade-offs they choose, and the RabbitMQ behavior their solution depends on.

Do not include any instruction that prohibits AI tools, web search, RabbitMQ documentation, or other external learning resources.

## RabbitMQ Generation Instructions
- Generate a RabbitMQ-focused task using AMQP 0-9-1 concepts and RabbitMQ configuration/topology files.
- The starter topology should be represented with RabbitMQ definitions JSON or equivalent boot-time configuration so the broker starts in the flawed current state.
- Prefer `rabbitmq:3-management` or a similarly standard RabbitMQ management image.
- Include a vhost, application users, permissions, exchanges, queues, and bindings that reflect the selected scenario.
- Use durable exchanges and queues for business-critical flows unless the task intentionally asks the candidate to identify and fix a durability problem.
- Use meaningful names that match the scenario domain, such as `payments.events`, `payments.capture.q`, `payments.retry.q`, `payments.capture.dlq`, `patient.events`, `patient.lab.us.q`, or `patient.unrouted.q`.
- If the scenario involves retries, model the starter problem and expected outcome using DLX/DLQ concepts, message TTL or queue TTL, reject/nack without requeue for permanent failures, and delayed retry behavior without tight loops.
- If the scenario involves routing, model the starter problem and expected outcome using direct, fanout, topic, headers, default, or alternate exchanges only when appropriate to the business need.
- If the scenario involves observability, include queue names, expected routing keys, correlation metadata, and management-facing checks the candidate can reason about.
- The task may include small JSON seed-message examples or a topology note, but do not require a full application service unless the generated task clearly remains RabbitMQ-focused and time-boxed.
- Avoid requiring Testcontainers, Pact, spring-cloud-contract, Kubernetes, Terraform, Ansible, PerfTest, JMeter, Locust, MassTransit harnesses, or language-specific framework setup for the core task.

## Infrastructure Requirements
The generated project MUST run from `/root/task` and include RabbitMQ infrastructure that is ready for the candidate to inspect and modify. The environment must be deterministic enough for the candidate to verify topology loading and broker readiness locally.

### Docker-compose Instructions
- Include a `docker-compose.yml` file.
- The docker-compose file MUST NOT include any version specification.
- Use a RabbitMQ service named clearly, such as `rabbitmq`.
- Use the RabbitMQ management image so the broker and management API/UI are available.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every broker or management port exposed to the host. For RabbitMQ this means binding AMQP and management ports as localhost-only, for example `127.0.0.1:5672:5672` and `127.0.0.1:15672:15672`.
- Do not use `.env` files or `${{VAR}}` host indirection for required service environment values. Inline service environment values are allowed and required where the image needs them.
- Set RabbitMQ default user, password, and vhost inline in the service environment so the broker initializes consistently.
- Mount RabbitMQ configuration and definitions files from `/root/task` into the container using explicit paths.
- Include a healthcheck that verifies the broker is ready, such as `rabbitmq-diagnostics -q ping` or a management API readiness check.
- Use a named Docker volume for RabbitMQ data if persistence is needed for the scenario.
- Do not include unrelated services such as PostgreSQL, MySQL, Redis, Kafka, Elasticsearch, or application containers unless the selected scenario absolutely requires them. RabbitMQ should be the only external service for this competency task.

### RabbitMQ Configuration Instructions
- Include RabbitMQ configuration files needed to load the starter topology, such as `rabbitmq.conf`, `definitions.json`, and optionally `enabled_plugins`.
- If using `definitions.json`, it must be valid JSON and load successfully on broker startup.
- The definitions must include the scenario's initial vhost, user, permissions, exchanges, queues, bindings, and policies if policies are part of the starter state.
- The starter definitions should be FULLY POPULATED and intentionally reflect the current flawed or incomplete implementation described in the task.
- Include only RabbitMQ features within intermediate scope: exchange types, durable/non-durable queues, routing keys, alternate exchange arguments, dead-letter exchange arguments, TTL arguments, queue length or priority arguments, permissions, vhosts, and management plugin configuration.
- Do not require advanced cluster definitions, federation or shovel setup, external authentication backends, TLS certificate material, or Kubernetes manifests.
- Ensure queue and exchange argument names are accurate for RabbitMQ, for example `x-dead-letter-exchange`, `x-dead-letter-routing-key`, `x-message-ttl`, `x-expires`, `x-max-length`, `x-max-priority`, or alternate-exchange arguments when relevant.
- If including seed messages, provide them as JSON data files or a small script that publishes sample messages after the broker is healthy. The seed path must be safe to run repeatedly.

### Run.sh Instructions
- Include a `run.sh` script.
- `run.sh` must be executable and start from `/root/task`.
- `run.sh` must use `docker compose up -d` to bring up RabbitMQ.
- `run.sh` must wait for RabbitMQ health rather than sleeping blindly. It may poll `docker compose ps`, `rabbitmq-diagnostics`, or the management API.
- `run.sh` must verify the starter environment loads successfully on the UNSOLVED starter, such as confirming the broker is healthy and definitions are loaded.
- `run.sh` must print clear progress logs.
- `run.sh` is a READINESS/self-check, NOT the grader. It MUST NOT run a grader test suite designed to fail until the candidate solves the task.
- `run.sh` must not install RabbitMQ, Docker, Python, Node, or other system dependencies. The environment provides Docker and common tooling.
- If a small validation command is included, it should confirm broker readiness and topology presence without asserting the final solved behavior.

## kill.sh file instructions
Create a `kill.sh` file that performs complete cleanup for the Docker Compose environment. The script must:

1. Start with `#!/bin/bash` and `set -e`.
2. Print clear log messages before every cleanup step.
3. Change to `/root/task` before running Docker Compose commands.
4. Stop and remove containers using `docker compose down --remove-orphans || true`.
5. Remove named volumes related to the task using `docker volume rm` or `docker compose down -v || true`.
6. Remove Docker networks related to the task using `docker network rm` where appropriate, with `|| true` for idempotency.
7. Force-remove task-specific Docker images if any were created, using `docker rmi -f ... || true`. If no custom images exist, include a clear log message stating that no custom task images are expected.
8. Run `docker system prune -a --volumes -f || true`.
9. Remove the task directory with `rm -rf /root/task || true` and print `Cleanup completed successfully!` at the end.

Every destructive command must use `|| true` where needed so the script is idempotent and safe to rerun after partial failures.

The output should be a valid json schema:
- `README.md`: concise candidate-facing task instructions with exactly the required sections.
- `.gitignore`: exclusions for RabbitMQ data, logs, temporary files, editor files, and local OS artifacts.
- `docker-compose.yml`: RabbitMQ broker infrastructure with localhost-only port bindings and no compose version specification.
- `rabbitmq.conf`: RabbitMQ startup configuration that enables management loading of definitions or other required broker settings.
- `definitions.json`: FULLY POPULATED RabbitMQ starter topology that represents the current flawed or incomplete implementation.
- `run.sh`: readiness script that starts RabbitMQ, waits for health, and verifies the starter topology loads.
- `kill.sh`: complete cleanup script following the required nine-step cleanup shape.
- Optional supporting files: seed messages, topology notes, lightweight verification data, or sample event contracts when they make the RabbitMQ scenario clearer without revealing the solution.

## Code file requirements
- All files must be complete and syntactically valid.
- All shell scripts must use explicit paths and start from `/root/task`.
- Starter files must not contain the final solution.
- Starter files must not include TODO comments, solution-revealing comments, or hidden instructions.
- The task must include a clear "Current Implementation" and "Required Changes" in the candidate-facing question, and the starter files must exactly match that current implementation.
- RabbitMQ JSON definitions must be valid JSON. Do not include comments in JSON files.
- YAML must be valid and must not include a top-level `version` key in `docker-compose.yml`.
- The task should be verifiable through observable RabbitMQ state: exchange and queue declarations, bindings, DLX/DLQ paths, alternate exchange routing, message properties, queue depths, redelivery behavior, or management API visibility.
- If sample messages are included, they must be realistic, small, and safe to publish repeatedly.
- Do not include credentials, hostnames, or setup instructions in the README that would reveal environment internals beyond what is necessary for the task. Keep connection details out of the README.
- Avoid requiring a specific client library unless a small optional helper script is included and the dependency is already available in the environment.

## .gitignore INSTRUCTIONS
Create a `.gitignore` appropriate for a RabbitMQ Docker-based task. It should exclude:
- RabbitMQ data directories if bind-mounted locally.
- Logs, temporary files, PID files, and generated output.
- Editor and operating-system artifacts.
- Python, Node, Java, or Go cache folders only if those helper files are actually included.
- `.env` files and local secrets.
Do not ignore the required task files such as `docker-compose.yml`, `rabbitmq.conf`, `definitions.json`, `README.md`, `run.sh`, or `kill.sh`.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The `README.md` file inside `code_files` MUST contain exactly these output sections in this order and no others:

### Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: `Consider`, `Think about`, `Explore`, `Review`, or `Analyze`.
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, exchange argument, or algorithm that solves the task.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should reference business and messaging outcomes such as reduced unwanted deliveries, safer retries, preserved failed messages, clearer routing, or improved operational visibility.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as broker readiness, topology visibility, message routing behavior, queue depth, DLQ contents, management-visible bindings, log output, or redelivery reduction.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
Keep the following out of the README:
- Setup commands such as `docker compose up`, `docker compose down`, package installs, or language test commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, exchange arguments, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like `you should implement`, `add this middleware`, `create this class`, `use this API`, or `set this exact argument`.
- Database-connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context`; synonyms produce a hollow, unusable task.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the RabbitMQ task.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, different from the repository name.",
  "question": "The full candidate-facing task description including the business context, Current Implementation, Required Changes, constraints, and observable expectations without revealing the solution.",
  "code_files": {{
    "README.md": "The concise candidate-facing README content following exactly the required Task Overview, Helpful Tips, Objectives, and How to Verify sections.",
    ".gitignore": "A complete gitignore file suited to the generated RabbitMQ Docker task and any optional helper files.",
    "docker-compose.yml": "A complete Docker Compose file for the RabbitMQ broker with localhost-only port bindings, inline RabbitMQ environment values, healthcheck, mounted configuration files, and no version specification.",
    "rabbitmq.conf": "A complete RabbitMQ configuration file that loads the intended starter definitions and enables the required management behavior for the task.",
    "definitions.json": "A valid JSON RabbitMQ definitions file containing the FULLY POPULATED starter vhost, users, permissions, exchanges, queues, bindings, and optional policies representing the flawed current implementation.",
    "run.sh": "A complete executable readiness script that starts RabbitMQ with docker compose, waits for health, validates that the starter topology loads, prints progress logs, and exits successfully on the unsolved starter.",
    "kill.sh": "A complete executable cleanup script following the required nine-step Docker cleanup behavior and ending with the exact success message.",
    "optional supporting files": "Any optional seed messages, topology notes, or lightweight verification data needed to make the RabbitMQ scenario understandable without giving away the final solution."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended RabbitMQ topology, routing, acknowledgement, retry, dead-letter, metadata, and verification changes without including candidate-facing prose.",
  "definitions": "An object mapping RabbitMQ and messaging terms used in the task to concise definitions that help evaluation and reviewer understanding.",
  "hints": "A single line hint nudging investigation toward RabbitMQ topology, delivery semantics, or operational behavior without revealing the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable RabbitMQ behavior such as corrected routing, reduced redeliveries, preserved failed messages, and improved observability. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as Docker, Docker Compose, RabbitMQ management basics, AMQP exchanges, queues, bindings, acknowledgements, dead-lettering, and routing keys.",
  "short_overview": "A bullet list summarising the selected business problem, the RabbitMQ technical focus, and the expected operational outcome."
}}

## CRITICAL REMINDERS
1. The RabbitMQ environment runs perfectly out of the box; the candidate fixes the TASK, not the environment.
2. Starter topology is runnable and loadable but does NOT contain the core solution.
3. Starter files must perfectly match the "Current Implementation".
4. No solution-revealing comments, TODO comments, hidden fixes, or direct README implementation instructions.
5. The task must be completable within {minutes_range} minutes by an INTERMEDIATE RabbitMQ candidate.
6. Output JSON uses the CANONICAL key names above — this is non-negotiable.
7. `docker-compose.yml` MUST NOT include any version specification.
8. RabbitMQ ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
9. `run.sh` is only a readiness/self-check script and MUST succeed on the unsolved starter.
10. `kill.sh` must follow the required cleanup shape and print `Cleanup completed successfully!`.
"""

PROMPT_REGISTRY = {
    "RabbitMQ (INTERMEDIATE)": [
        PROMPT_RABBITMQ_INTERMEDIATE_CONTEXT,
        PROMPT_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_RABBITMQ_INTERMEDIATE_INSTRUCTIONS,
    ]
}