# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_FASTAPI_KAFKA_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how Kafka is used in FastAPI-based event-driven systems at an intermediate level — such as reliable asynchronous service communication, idempotent event handling, consumer group orchestration, retry and dead-letter strategies, transactional consistency between API state and Kafka events, and production-grade async message processing?
"""

PROMPT_FASTAPI_KAFKA_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a FastAPI and Kafka assessment task.

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

Based on the above inputs, briefly state:
1. Which scenario you selected and why
2. What the task will involve

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""

PROMPT_FASTAPI_KAFKA_INSTRUCTIONS_INTERMEDIATE = """
## GOAL
As a technical architect super experienced in Python FastAPI, Apache Kafka, and event-driven backend systems, you are given a list of real world scenarios and proficiency levels for FastAPI and Kafka.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to maintain and improve production-style FastAPI services that communicate through Kafka at an intermediate level.
The candidate's responsibility is to analyze a working but incomplete or flawed event-driven FastAPI system, identify reliability and async-processing issues, and implement focused improvements without being told the exact solution.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python FastAPI application stack that is already deployed with Kafka and a relational database. The application includes:
- A FastAPI service with routers, Pydantic models, SQLAlchemy-based persistence, and Kafka producer or consumer code that is operational but has realistic reliability and consistency issues
- A Kafka broker with relevant topics for the selected scenario, such as primary event topics, retry topics, or failure-analysis topics
- A PostgreSQL database that is FULLY POPULATED with realistic initial schema and data when the selected scenario requires transactional API state
- Existing tests or test scaffolding using Pytest and FastAPI dependency overrides, with enough structure for the candidate to add targeted coverage
- Working Docker-based infrastructure so the candidate can focus on FastAPI, async Kafka flows, message reliability, and observability rather than manual setup

The candidate is expected to operate at INTERMEDIATE proficiency level with 3-5 years experience. They should be able to reason about async/await boundaries, FastAPI lifespan management, aiokafka producer and consumer lifecycle, Kafka keys and partition ordering, idempotent processing, at-least-once delivery, dead-letter handling, SQLAlchemy transactions, structured logging, and maintainable API organization.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level FastAPI and Kafka reliability or event-processing scenario.
- Task must ask the candidate to fix, refactor, or complete focused functionality in an existing event-driven FastAPI system rather than build a full platform from scratch.
- **CRITICAL**: The FastAPI service and infrastructure should be FULLY FUNCTIONAL at startup, but the business workflow should contain realistic gaps such as duplicate event publication, incorrect message keys, unsafe offset handling, blocking request paths, missing idempotency protection, weak validation, or incomplete outbox publishing.
- **CRITICAL**: The task must align with INTERMEDIATE proficiency level (3-5 years experience) and should require architectural thinking without demanding deep advanced Kafka cluster operations, Kubernetes operators, multi-datacenter replication, Kafka Streams, ksqlDB, Flink, or full schema-registry administration.
- **CRITICAL**: Keep the candidate workload focused on 3-4 objectives that can be completed within {minutes_range} minutes with AI assistance allowed.
- **CRITICAL**: The task should evaluate practical FastAPI + Kafka implementation skills, including async lifecycle management, producer or consumer reliability, event key strategy, idempotency, retry or dead-letter behavior, and observable failure handling.
- **CRITICAL**: Do NOT require the candidate to administer a production Kafka cluster, configure TLS/SASL security, perform broker reassignment, run Cruise Control, build Kafka Streams topologies, or deploy Kafka on Kubernetes. Those are beyond the required task scope for this combined FastAPI implementation assessment.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The starter code may include intentionally flawed but realistic behavior, but it must not include comments that directly reveal the fix.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, and not just patch the first visible error.
- The task should naturally involve one FastAPI service and Kafka, with PostgreSQL included when the selected scenario requires transactional state, deduplication, or an outbox-style workflow.
- Suitable intermediate task themes include:
  - Making an endpoint idempotent so retries do not create duplicate side effects or duplicate Kafka events
  - Correcting Kafka message keys so ordering is preserved for the actual business aggregate
  - Moving slow or fragile Kafka publishing out of the request path while preserving transactional consistency
  - Completing a background outbox publisher that marks events as sent only after broker acknowledgment
  - Adding focused validation and tests around event payloads, database writes, and Kafka publishing behavior
  - Adding structured logs with correlation identifiers so failed message processing can be diagnosed
  - Handling retryable and non-retryable processing failures without losing messages or corrupting state
- The task should include measurable symptoms, such as duplicate downstream notifications, hot partitions, request failures when Kafka is slow, repeated processing of the same event, or missing observability during failures.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, FastAPI documentation, Kafka documentation, Python documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem.
- Candidates may use AI to help with implementation details, but the assessment should still require them to understand async FastAPI behavior, Kafka delivery semantics, idempotency, and reliable event-processing trade-offs.
- The generated task should be specific enough to evaluate engineering judgment and debugging ability, not rote memorization of framework APIs.

## Code Generation Instructions
Based on the real-world scenarios provided, create a FastAPI + Kafka task that:
- Draws inspiration from the input_scenarios given above to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for intermediate async and event-driven reasoning.
- Tests practical FastAPI implementation and Kafka integration skills in Python, especially aiokafka-based non-blocking producer or consumer patterns.
- Time constraints: Each task should be finished within {minutes_range} minutes total.
- At every time pick different real-world scenario from the list provided above to ensure variety.
- Provide a working local project rooted at /root/task with Docker Compose infrastructure for Kafka, PostgreSQL if persistence is needed, and the FastAPI application.
- Prefer a single cohesive FastAPI service with background processing when the selected scenario is endpoint-centric; use a second lightweight worker process only if the scenario genuinely needs separate consumer behavior.
- Include source files that demonstrate routers, schemas, services, repository or database access, Kafka integration, configuration, and tests.
- Use Python 3.11+ with FastAPI, Pydantic, SQLAlchemy or SQLModel where persistence is required, aiokafka for Kafka communication, uvicorn as the ASGI server, and Pytest for tests.
- Use Kafka for the event-driven portion of the task and do not invent Redis, MongoDB, MySQL, Qdrant, or additional infrastructure unless explicitly required by the selected scenario.
- The Kafka broker should use a reliable Docker image such as `confluentinc/cp-kafka:7.6.1` and must start cleanly in the sandbox.
- Include PostgreSQL only when the selected scenario requires persisted API state, idempotency records, transactional integrity, or an outbox table.
- The generated code should be valid, importable, and executable, with the initial system booting successfully.
- The project should include intentionally incomplete or flawed implementation details that are appropriate for candidate work, not infrastructure-breaking defects.

## Infrastructure Requirements
- MUST include a complete docker-compose.yml because this is an infra-shaped FastAPI + Kafka task.
- MUST include run.sh because the environment needs to start Kafka, the FastAPI app, and any required database in one command.
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic and no cleanup script is needed.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The infrastructure setup is AUTOMATED - candidates will NOT manually deploy Kafka or initialize the database before beginning the assessment.
- The generated stack must start successfully on the first run. Kafka must be ready, topics must exist or be auto-created safely, the database must be initialized when present, and the FastAPI health endpoint must respond.
- Do NOT include `apt-get install`, `pip install`, or similar dependency installation commands in run.sh. Runtime and common libraries are handled by the container build or the E2B template, not by the run script.

### Docker-compose Instructions
- docker-compose.yml must include the Kafka broker service and the FastAPI application service.
- Include PostgreSQL service only when the selected scenario requires persistence, idempotency records, SQLAlchemy transactions, or an outbox table.
- **MUST NOT include any version specification** as a top-level `version:` field in the docker-compose.yml file.
- **MUST NOT include environment variables or .env file references**. Do not use `.env` files or shell-style variable substitution. If an official container requires an environment section, use hardcoded literal values only and never reference external environment files.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore or broker exposed to the host, including Kafka and PostgreSQL.
- Use hardcoded internal service names such as `kafka` and `postgres` for container-to-container communication.
- Configure Kafka listeners so the FastAPI container can connect on the Docker network and host tools can connect through the localhost-bound port.
- Use health checks and depends_on conditions so the FastAPI service waits for Kafka and PostgreSQL readiness where applicable.
- Use named volumes for Kafka and PostgreSQL persistence when a database is included.
- The FastAPI service should expose its API port to localhost, for example `127.0.0.1:8000:8000`.
- The compose file should build the FastAPI app from the provided Dockerfile and should not rely on host virtual environments.

### init_database.sql and Kafka Topic Instructions
- Include init_database.sql when PostgreSQL is part of the selected scenario.
- init_database.sql must create the required tables, relationships, constraints, and seed data needed for the scenario.
- For idempotency or outbox-style tasks, include realistic tables such as business aggregate tables, request deduplication tables, or outbox event tables, but do not implement the final candidate solution in SQL.
- SQL must be valid PostgreSQL and must run automatically through `/docker-entrypoint-initdb.d/` during container initialization.
- Do not create database users or run seed scripts from run.sh. PostgreSQL initialization must happen through mounted SQL files.
- Kafka topics must exist before the application depends on them. This may be done with safe broker auto-creation, an init container, or a small topic-creation service in docker-compose.
- Topic names must be realistic for the selected scenario, such as payment-events, patient-arrivals, application-stage-events, retry topics, or dead-letter topics.
- Do not expose solution-specific Kafka tuning values in README.md, but the starter code may include basic safe defaults in configuration files.

### Run.sh Instructions
- run.sh must use `#!/usr/bin/env bash` and `set -e` at the top.
- run.sh must `cd /root/task` before running Docker commands.
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d --build`.
- WAIT MECHANISM: Implements bounded health-check loops that wait for Kafka readiness, PostgreSQL readiness if present, and FastAPI readiness.
- VALIDATION: Validates that the FastAPI health endpoint responds successfully after infrastructure starts.
- DATABASE SETUP: SQL files are automatically executed by the PostgreSQL container during initialization when present; run.sh MUST NOT manually execute SQL or create users.
- TOPIC READINESS: Confirms Kafka is ready enough for the app to produce or consume events before declaring success.
- ERROR HANDLING: If any check fails after retries, run.sh should print relevant `docker compose logs` output and exit with code 1.
- SUCCESS OUTPUT: End with a clear success message showing localhost URLs for the FastAPI app and docs.
- run.sh must not install Python, Kafka, Docker, PostgreSQL, or application dependencies on the host.

### Dockerfile Instructions
- Include a Dockerfile for the FastAPI application container.
- Use a Python 3.11+ base image appropriate for FastAPI, such as python:3.11-slim.
- Set WORKDIR to /root/task or a service subdirectory under /root/task consistently with docker-compose.
- Install Python dependencies from a requirements.txt or pyproject.toml during image build, not in run.sh.
- Copy application source files into the container with paths matching the generated project structure.
- Expose the application port used by uvicorn.
- Start the app with uvicorn using host 0.0.0.0 and the configured port.
- Avoid .env dependencies and external secret files.
- Keep the Dockerfile functional and simple; the candidate's main task is FastAPI + Kafka reliability, not Docker optimization.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Python, Docker, Kafka, PostgreSQL, IDE, and test artifact exclusions)
  - docker-compose.yml (Kafka broker, FastAPI app, and PostgreSQL if the scenario requires persistence)
  - run.sh (Script to deploy and validate the infrastructure; no kill.sh)
  - Dockerfile (FastAPI application container)
  - requirements.txt or pyproject.toml (Python dependencies for FastAPI, aiokafka, SQLAlchemy, Pytest, and related libraries)
  - init_database.sql (Only when PostgreSQL is required by the selected scenario)
  - app/main.py (FastAPI application entry point with lifespan where appropriate)
  - app/api/... (Routers and endpoint modules)
  - app/schemas/... (Pydantic request, response, and event models)
  - app/services/... (Business logic and Kafka-facing service code)
  - app/db/... (SQLAlchemy models, session management, repositories, and migrations-lite setup when applicable)
  - app/kafka/... (Producer, consumer, topic, serialization, and message helper code)
  - tests/... (Focused Pytest tests for validation, idempotency, Kafka key/payload behavior, or outbox publishing)

## Code file requirements
- Generate a realistic FastAPI project structure with multiple Python files and clear separation of routers, schemas, services, persistence, Kafka integration, and tests.
- Code should follow modern Python best practices including type hints, async/await, Pydantic models, dependency injection, structured error handling, and consistent naming.
- The generated code files should provide partial implementations that require intermediate-level completion, but the app and infrastructure must still boot.
- Include tests that are runnable with Pytest and that can be extended by the candidate.
- Include FastAPI-specific dependency override patterns or mocks where tests need to isolate Kafka and database behavior.
- Use aiokafka or a similarly appropriate async Kafka client for application code.
- Include SQLAlchemy-based persistence when the scenario uses PostgreSQL.
- Do not include blocking Kafka or database calls in request handlers unless that is the intentional symptom candidates need to identify and correct.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include comments that give away hints, solutions, exact Kafka patterns, or implementation steps.
- DO NOT include comments like "Add outbox here", "Use idempotent producer", "Create dead-letter topic", or "Commit offset after processing".
- The code should include enough realistic behavior for candidates to inspect request flow, event payloads, database records, and logs.
- The task should leave the core candidate work in application logic, async lifecycle handling, reliability behavior, tests, and observability.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for Python, FastAPI, Kafka, PostgreSQL, and Docker development:
- Python cache directories including __pycache__/, *.py[cod], *$py.class, and *.so
- Virtual environments including venv/, env/, .venv/, and .Python
- IDE and editor files including .idea/, .vscode/, *.swp, and *.swo
- Testing artifacts including .pytest_cache/, .coverage, htmlcov/, and coverage.xml
- Environment files including .env and .env.*
- Log files including *.log and logs/
- Distribution artifacts including dist/, build/, and *.egg-info/
- Docker and local data directories including data/, volumes/, kafka-data/, postgres-data/
- OS-specific files including .DS_Store and Thumbs.db
- Any other common development artifacts for Python FastAPI projects

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following candidate-facing sections in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected FastAPI + Kafka scenario.
All sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific event-driven FastAPI task scenario being generated.
Use concrete business context, not generic descriptions.
The README must NOT contain database connection details, Kafka broker connection details, usernames, passwords, client-tool suggestions, `<DROPLET_IP>` placeholders, setup commands, or deployment commands.

### Task Overview
- This section must contain 3-4 meaningful sentences.
- Do not use a bullet list in this section.
- Describe the business scenario, current state, and why the problem matters.
- Explain the observable reliability, consistency, performance, or event-processing problem without revealing the specific fix.
- NEVER generate empty content.
- Do not include bold time-budget callouts.

### Objectives
- Include 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: 'Improve Kafka reliability.'
- GOOD: 'Payment capture requests currently fail when the message broker is slow even after the payment record is saved; after your changes, successful captures should remain durable and produce one traceable event for downstream systems.'

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Tips may encourage candidates to reason about async boundaries, duplicate requests, message ordering, retry behavior, transactional consistency, and observability.
- Do not include direct implementation advice or exact configuration values.

### How to Verify
- Include 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run or observe, such as API response behavior, test output, message count, response latency, log line, durable database state, or duplicate-event behavior.
- Do not provide setup commands or exact solution commands.
- Verification should help the candidate demonstrate both functional correctness and event-driven reliability.

### CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Make sure you do not include the following in the README.md file:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, `uvicorn`, or any deployment commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database-connection details, Kafka broker connection details, usernames, passwords, ports, or client-tool suggestions
- `<DROPLET_IP>` placeholders
- Specific Kafka configuration values or producer and consumer code patterns
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", or "configure the following"

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the FastAPI and Kafka task without using spaces or title casing.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from name, and focused on the event-driven FastAPI and Kafka improvement being assessed.",
  "question": "A full candidate-facing task description that explains the selected business scenario, the current flawed FastAPI and Kafka behavior, the focused implementation goals, and the expected observable improvements without revealing the exact solution.",
  "code_files": {{
    "README.md": "Candidate-facing README content following exactly the required sections Task Overview, Objectives, Helpful Tips, and How to Verify, with concise open-ended guidance and no setup commands or connection details.",
    ".gitignore": "A comprehensive ignore file for Python, FastAPI, Docker, Kafka, PostgreSQL data directories, test artifacts, editor files, logs, and environment files.",
    "docker-compose.yml": "A complete Docker Compose file without a top-level version field that starts Kafka, the FastAPI app, and PostgreSQL only if required, with localhost-bound exposed ports and no .env references.",
    "run.sh": "A bash script that changes to /root/task, starts the stack with docker compose up -d --build, waits for service readiness, validates the FastAPI health endpoint, prints logs on failure, and does not install dependencies.",
    "Dockerfile": "A functional Dockerfile for the FastAPI application using a Python 3.11+ base image, installing project dependencies during build and starting uvicorn on the configured application port.",
    "requirements.txt": "A Python dependency manifest containing the libraries needed for the generated FastAPI, aiokafka, SQLAlchemy, Pydantic, uvicorn, and Pytest project.",
    "init_database.sql": "A PostgreSQL initialization script included only when persistence is required, creating the scenario schema and seed data without implementing the candidate's final reliability fix.",
    "app/main.py": "The FastAPI application entry point with router registration, health endpoint, and lifespan behavior where appropriate for Kafka resources.",
    "app/api/routes.py": "The route module containing the scenario endpoint or endpoints with enough working behavior for the candidate to investigate and improve.",
    "app/schemas/models.py": "Pydantic request, response, and event schemas with validation structure appropriate for the scenario while leaving focused candidate changes where needed.",
    "app/services/business_service.py": "The business service layer coordinating validation, persistence, and event publication or processing with realistic incomplete reliability behavior.",
    "app/kafka/client.py": "Kafka producer or consumer helper code that is operational but requires candidate-level improvement around reliability, lifecycle, message keys, or error handling.",
    "app/db/database.py": "Database connection and session management code included when PostgreSQL is used, configured with hardcoded local Docker service settings rather than environment files.",
    "app/db/models.py": "SQLAlchemy models for the selected business entities and supporting reliability tables when persistence is part of the scenario.",
    "tests/test_workflow.py": "Focused Pytest tests or starter tests that exercise validation, idempotency, Kafka payload construction, route behavior, or failure handling and can be extended by the candidate.",
    "additional files": "Any additional source modules, package initializers, repositories, utilities, or tests needed to make the generated project coherent, bootable, and assessable."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected FastAPI, async processing, Kafka reliability, idempotency, transactional consistency, testing, and observability improvements for the selected scenario.",
  "definitions": "An object mapping important FastAPI, Kafka, async programming, and reliability terms used in the task to concise definitions that help assessors and candidates share terminology.",
  "hints": "A single line nudging the candidate toward investigating request durability, duplicate processing, message ordering, async boundaries, and observable failure behavior without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable reliability, consistency, latency, duplicate-prevention, and observability improvements in the FastAPI and Kafka workflow. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed for the task, covering Docker Compose, Python FastAPI, Kafka messaging basics, async programming, Pytest, and SQLAlchemy when the scenario uses a database.",
  "short_overview": "Exactly 3 plain sentences: the first states what event-driven FastAPI system is being built or improved, the second states what the candidate must do, and the third states what success looks like, with no label prefixes."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, Dockerfile, Python dependency manifest, FastAPI source files, Kafka integration files, tests, and init_database.sql only when PostgreSQL is required.
3. **Do not include kill.sh** — E2B sandboxes are destroyed as a whole, so cleanup is automatic.
4. **Deployment must succeed in one go** — Kafka must be ready, topics must exist or be safely auto-created, PostgreSQL must initialize when included, and FastAPI must pass a health check.
5. **docker-compose.yml must NOT have a `version:` field**.
6. **SECURITY-CRITICAL**: datastore and broker ports exposed to the host MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
7. **MUST NOT include environment variables or .env file references**; avoid .env files and variable substitution, and use hardcoded literal configuration values where container configuration is required.
8. **Task must be completable within {minutes_range} minutes** for INTERMEDIATE proficiency.
9. **Focus on FastAPI + Kafka implementation skills**: async lifecycle, event publishing or consuming, idempotency, message ordering, retry or failure handling, SQLAlchemy consistency when needed, tests, and structured logging.
10. **Stay within scope**: do not require Kafka Streams, ksqlDB, Flink, Kafka Connect clusters, Schema Registry administration, TLS/SASL security, Kubernetes Kafka operators, multi-datacenter disaster recovery, or deep broker operations.
11. **No solution comments in code**: do not include TODOs, direct hints, or comments that reveal exactly what the candidate should implement.
12. **README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify** as candidate-facing sections, with no access details, setup commands, or solution-revealing guidance.
13. **title** must be in `<action verb> <subject>` format and different from `name`.
"""

PROMPT_REGISTRY = {
    "Kafka (INTERMEDIATE), Python - FastAPI (INTERMEDIATE)": [
        PROMPT_FASTAPI_KAFKA_CONTEXT_INTERMEDIATE,
        PROMPT_FASTAPI_KAFKA_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_FASTAPI_KAFKA_INSTRUCTIONS_INTERMEDIATE,
    ],
}