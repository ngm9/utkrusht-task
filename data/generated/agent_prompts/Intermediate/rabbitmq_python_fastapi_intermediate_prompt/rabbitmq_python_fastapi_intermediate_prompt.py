# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI and RabbitMQ assessment task.

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

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python FastAPI and RabbitMQ implementation or fix required, the expected deliverables, and how it aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python FastAPI and RabbitMQ, you are given a list of real world scenarios and proficiency levels for FastAPI services integrated with RabbitMQ.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to be an intermediate Python FastAPI and RabbitMQ developer with roughly 3-5 years of experience. They should be able to work with moderately complex API services, Pydantic validation, routers, dependency injection, async request handling, structured error responses, RabbitMQ exchanges, queues, bindings, routing keys, durable topology, message properties, manual acknowledgements, QoS prefetch, retry and dead-letter flows, correlation IDs, and environment-driven connection settings.

The generated task should test practical engineering judgment in a realistic service integration scenario, not trivia, syntax recall, package installation, or broker administration beyond the level needed for an application developer. The candidate should not be required to design expert-level RabbitMQ clusters, perform advanced Erlang/BEAM debugging, implement multi-region active-active messaging, or tune production broker internals.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in an existing FastAPI service that integrates with RabbitMQ.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL as a local project and must start with RabbitMQ available through Docker Compose; the candidate should not spend assessment time fixing package imports, broken scripts, missing directories, invalid Python syntax, or unusable broker configuration.
- **CRITICAL**: The task must stay within intermediate RabbitMQ and FastAPI application-integration skills: exchanges, queues, bindings, routing keys, durable declarations, JSON message contracts, Pydantic validation, correlation IDs, publisher message properties, connection/channel reuse, publisher confirms conceptually, manual ack/nack/reject behavior, prefetch, idempotency or deduplication at an application level, retries, DLX/DLQ, and practical diagnostics from queue depth or logs.
- **CRITICAL**: Do not require advanced RabbitMQ clustering, quorum queue tuning, multi-region federation/shovel design, Kubernetes Helm deployment, TLS certificate rotation, OAuth2 broker plugins, Terraform, Ansible, PerfTest capacity modeling, or deep broker internals as the main candidate task.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The task may involve one of these realistic work items: repairing a FastAPI endpoint that publishes to the wrong RabbitMQ exchange or queue, adding durable topic routing for multiple consumers, moving slow synchronous work from an API request into a RabbitMQ worker, making a consumer safe under at-least-once delivery, adding DLQ/retry behavior for poison messages, or improving validation and correlation metadata for asynchronous workflows.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency, ensuring that no two questions generated are similar.
- For BEGINNER and BASIC and INTERMEDIATE levels of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible for these levels.
- For this INTERMEDIATE task, make the expected changes substantial enough to reveal practical judgment but small enough to complete within {minutes_range} minutes.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest best practices and language versions. Strictly avoid using outdated versions of Python, FastAPI, Pydantic, or RabbitMQ client usage in the code scenarios.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, FastAPI documentation, RabbitMQ documentation, Pika documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates must still produce a coherent, working solution that fits the provided codebase, business scenario, operational constraints, and expected behavior.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Python FastAPI and RabbitMQ task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency and 3-5 years of experience, keeping in mind that AI assistance is allowed.
- Tests practical FastAPI skills around application structure, routers, Pydantic request/event models, dependency management, async endpoints, consistent errors, and observable responses.
- Tests practical RabbitMQ skills around AMQP 0-9-1 concepts, exchange/queue/binding design, routing keys, durable topology, message properties, correlation IDs, manual acknowledgements, prefetch, retry behavior, and dead-letter handling.
- Avoids tasks that primarily ask about testing framework configuration, exact command memorization, broker installation, CI setup, or advanced RabbitMQ operations.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- The generated project should include a small but realistic FastAPI app, a RabbitMQ integration module, a worker module or consumer entry point if the scenario needs consumption behavior, and tests or smoke checks that help verify the intended behavior after the candidate completes the task.
- Use Python 3.10+ style and a modern FastAPI/Pydantic-compatible dependency set.
- The starter code should be runnable and importable before the candidate changes anything, but the task-specific behavior should be incomplete or logically flawed in a way that matches the question.

## Infrastructure Requirements
- This is an infra-shaped task because the scenario exercises RabbitMQ as an external broker.
- The generated task MUST include docker-compose.yml, run.sh, and kill.sh.
- The generated task MUST include RabbitMQ configuration through Docker Compose only; do not include PostgreSQL, Redis, MySQL, Kafka, or other datastores unless the selected scenario explicitly requires them. For this competency combination, RabbitMQ is the expected infrastructure.
- The FastAPI app should run locally using Python dependencies from requirements.txt; do not require an application Docker container unless the scenario has an unavoidable reason.
- The project must be usable from /root/task and scripts must be written as if they are executed from /root/task.
- The candidate-facing code should read RabbitMQ host, port, username, password, and vhost from environment variables with sensible local defaults that match docker-compose.yml.
- Do not use .env files or host variable indirection for docker-compose service initialization. Inline service environment values are required for the RabbitMQ container.

### Docker-compose Instructions
- docker-compose.yml MUST be included in code_files for this task.
- **MUST NOT include any version specification** in docker-compose.yml.
- Include a RabbitMQ service using the management image so the broker is available for AMQP traffic and basic observability.
- RabbitMQ MUST set initialization environment variables inline in the service, including RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS, and RABBITMQ_DEFAULT_VHOST. Forbid .env files and ${{VAR}} host indirection for these values.
- The RabbitMQ vhost, username, and password used by the app defaults, tests, healthcheck, and README assumptions must match the inline compose environment.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every RabbitMQ port exposed to the host.
- Bind AMQP port 5672 as `127.0.0.1:5672:5672` and management port 15672 as `127.0.0.1:15672:15672` if the task uses the management UI or HTTP API for observability.
- Include a RabbitMQ healthcheck that uses a broker-native command such as `rabbitmq-diagnostics -q ping` or an equivalent readiness check.
- Use a named volume for RabbitMQ data if persistence across container restarts is useful for the task, but make kill.sh remove it.
- Do not add unrelated services, external networks, privileged mode, or broad host port exposure.

### RabbitMQ Configuration Instructions
- The starter application should declare its own required topology at startup or worker startup, rather than relying on manual broker setup.
- The topology should be modest and task-specific: direct, fanout, topic, or default exchange usage; durable queues; bindings; routing keys; optional dead-letter exchange and retry queue when the scenario needs failure handling.
- If the selected scenario involves fan-out or routing, use exchange and queue names that clearly match the business domain and show why a single shared queue is incorrect.
- If the selected scenario involves retries, include a dead-letter exchange, a DLQ, and optionally a retry queue using TTL and dead-letter routing back to the work queue. Avoid tight retry loops.
- If the selected scenario involves request/reply, include correlation_id and reply_to requirements, but keep the implementation small enough for {minutes_range} minutes.
- Message payloads should be JSON and validated by Pydantic before publishing. Message properties should include content_type=`application/json` and correlation_id when traceability is part of the task.
- Important events or jobs should be persistent messages when durability is part of the scenario.
- Consumers should use manual acknowledgements for at-least-once delivery scenarios and should only ack after successful processing. Permanent failures should be rejected or routed to a DLQ according to the scenario.
- Use a reasonable prefetch setting when the worker consumes messages; do not leave unbounded consumer delivery for a task focused on reliability or back-pressure.
- The starter code must not connect once per message in the correct path; if connection misuse is the bug, the current implementation may show that flaw, and the question should ask the candidate to fix it.

### Run.sh Instructions
- run.sh MUST be included in code_files for this task.
- run.sh must be executable and must use `#!/usr/bin/env bash` with strict mode such as `set -euo pipefail`.
- run.sh's first step MUST install the project dependencies using `pip install -q -r requirements.txt` from /root/task because the runtime is available but task-specific third-party libraries are not pre-installed.
- run.sh must start RabbitMQ using `docker compose up -d`.
- run.sh must wait until RabbitMQ is healthy before running any smoke checks. Use docker compose health status or a broker-native command through docker compose exec.
- run.sh is a READINESS/self-check, NOT the grader. It must verify that the starter project imports, compiles, and can reach RabbitMQ, then exit 0 on the UNSOLVED starter.
- run.sh MUST NOT run the grader test suite if those tests are designed to fail until the candidate solves the task.
- Good readiness checks include `python -m compileall app tests`, an import smoke test, checking FastAPI app object import, and checking that the RabbitMQ container is healthy.
- run.sh should print clear progress logs for dependency installation, broker startup, readiness waiting, Python smoke checks, and final success.
- run.sh must not require any secret beyond the local RabbitMQ defaults defined in docker-compose.yml.

## kill.sh file instructions
Create a comprehensive kill.sh script that performs complete cleanup of the Docker environment and task files. The script must:

1. Stop all running containers for this task using docker compose down from /root/task and print a log message before and after this step.
2. Remove all Docker volumes associated with the task, including RabbitMQ named volumes, using docker compose down -v and explicit docker volume rm commands where helpful.
3. Remove any Docker networks created for this task using docker network rm commands where helpful.
4. Force-remove task-related Docker images if any were built for this task, using docker rmi -f, and make this step safe even when no image exists.
5. Run `docker system prune -a --volumes -f` to remove unused Docker resources after the task-specific cleanup.
6. Remove the /root/task directory using `rm -rf /root/task` after Docker cleanup is complete.
7. Use `|| true` for cleanup commands that may fail when resources are already absent so the script is idempotent and can be run multiple times.
8. Print logs at every step so users can see what cleanup action is happening.
9. Print `Cleanup completed successfully!` as the final message.

The kill.sh script must use `#!/usr/bin/env bash`, strict mode where practical, and must not fail simply because containers, volumes, networks, or images have already been removed.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastapi, uvicorn, pydantic-compatible packages, pika or aio-pika depending on the starter design, pytest/httpx if tests are included, and any other dependencies required in the scenario)
  - docker-compose.yml (RabbitMQ service only unless the selected scenario explicitly needs more infrastructure)
  - run.sh (Dependency installation, RabbitMQ startup, readiness wait, and starter import/compile smoke checks only)
  - kill.sh (Full cleanup script following the 9-step cleanup instructions)
  - .gitignore (Ignore .pyc files, __pycache__, venv/, .venv/, .env, *.log, .pytest_cache/, and other Python artifacts)
  - Any FastAPI, RabbitMQ producer, consumer, worker, schema, configuration, and test files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.

## Code file requirements
- More than 1 file can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP 8 guidelines.
- The generated project structure should be realistic but compact, such as `app/main.py`, `app/api.py`, `app/schemas.py`, `app/rabbitmq.py`, `app/worker.py`, and `tests/test_contract.py` when appropriate.
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- **CRITICAL**: The starter code must be FULLY FUNCTIONAL for its described current state. It must run, import, and expose the baseline FastAPI app without syntax errors or missing dependencies.
- The core business logic functions or class methods that the candidate needs to implement must be left incomplete, simplified, or logically flawed according to the task scenario, but not broken by syntax errors.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- Avoid comments such as:
"
async def publish_order_paid(event: OrderPaidEvent):
    # TODO publish to topic exchange with routing key order.paid
    pass
"
This is BAD. DO NOT INCLUDE COMMENTS LIKE "Intended", "insert logic here", "use DLQ here", "add manual ack", or any solution-revealing notes.
- If the task is to fix bugs, make sure the starter code has logical or design bugs substantial enough to test intermediate proficiency, such as using the default exchange incorrectly for a fan-out requirement, using auto_ack where at-least-once delivery is required, omitting correlation IDs, opening a RabbitMQ connection per request, requeueing poison messages forever, or blocking a FastAPI request with slow work.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point with clear seams for candidate work.
- Tests may assert current contract expectations or provide helper fixtures, but they must not reveal the complete implementation. If tests are intended as the grader, run.sh must not execute them.
- The generated project should be runnable, but the code requiring implementation will not fully satisfy the task until the candidate completes it.
- Use environment-driven configuration for RabbitMQ connection parameters and keep defaults aligned with docker-compose.yml.
- Do not include unrelated database models, ORM setup, or external services unless the selected scenario explicitly requires them.

## .gitignore INSTRUCTIONS
Have a sensible gitignore suited for the task, especially for Python FastAPI and RabbitMQ integration tasks.
- __pycache__/
- *.pyc
- .env
- .venv/
- venv/
- .mypy_cache/
- .pytest_cache/
- *.egg-info/
- build/
- dist/
- .DS_Store
- *.log
- .coverage
- htmlcov/
- .ruff_cache/

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

- The README.md contains EXACTLY the following sections in this order:
  1. Task Overview
  2. Helpful Tips
  3. Objectives
  4. How to Verify
- The README.md file content MUST be FULLY POPULATED with meaningful, specific content.
- Task Overview section MUST contain the exact business scenario from the task description.
- ALL sections must have substantial content - no empty or placeholder text allowed.
- Content must be directly relevant to the specific task scenario being generated.
- Use concrete business context, not generic descriptions.
- The README must NOT contain extra sections such as Database Schema Overview, Database Access, Setup, Installation, Architecture, Performance Issues, or NOT TO INCLUDE.
- The README must NOT contain `<DROPLET_IP>` placeholders or any database-connection details. For this task, do not include RabbitMQ host, port, username, password, management UI instructions, or client-tool suggestions in the README.

### Task Overview
- Task Overview must be 3-4 meaningful sentences.
- Use paragraph form only. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, routing key, exchange type, queue argument, acknowledgement method, or algorithm that solves the task.
- Helpful Tips may point candidates toward the relevant files or concepts at a high level, but must not provide step-by-step instructions.

### Objectives
- Objectives must be 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should cover API behavior, message delivery correctness, validation/error handling, reliability under failure, and observability where relevant.
- Do not reveal exact exchange names, queue names, method names, or solution mechanics in objectives unless those names are already part of the task's fixed business contract.

### How to Verify
- How to Verify must be 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, API response shape, queue depth change, worker log line, duplicate handling result, DLQ observation, or latency behavior.
- Do not include setup commands such as pip install, docker compose up, pytest, or uvicorn commands.
- Keep verification focused on user-visible or operator-visible behavior.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, `pytest`, `uvicorn`, or similar.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, queue arguments, RabbitMQ client calls, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", "declare this exchange", or "call this acknowledgement method".
- RabbitMQ connection details, management UI login details, hostnames, ports, usernames, passwords, or client-tool suggestions.

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that clearly reflects the business scenario and technical focus without using spaces or title case.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, that is different from the repository name and summarizes the candidate task.",
  "question": "The full candidate-facing task description, including the selected business scenario, the current implementation state, the required behavioral changes, and the constraints the candidate must satisfy without including hints or the answer.",
  "code_files": {{
    "README.md": "The fully populated candidate-facing README content using exactly the four required sections: Task Overview, Helpful Tips, Objectives, and How to Verify.",
    ".gitignore": "A complete Python-focused gitignore suitable for a FastAPI project with local environment files, cache directories, logs, and build artifacts excluded.",
    "requirements.txt": "The Python dependency manifest containing FastAPI, an ASGI server if useful, RabbitMQ client dependencies, Pydantic-compatible packages, and any lightweight testing dependencies needed by the generated project.",
    "docker-compose.yml": "The Docker Compose configuration for the RabbitMQ broker, with no version specification, localhost-only port bindings, inline RabbitMQ default user/password/vhost values, and a broker healthcheck.",
    "run.sh": "An executable readiness script that installs Python dependencies, starts RabbitMQ with docker compose, waits for broker health, runs starter import or compile smoke checks, and exits successfully on the unsolved starter.",
    "kill.sh": "An executable cleanup script that stops containers, removes volumes and networks, prunes Docker resources, removes /root/task, remains idempotent with safe failure handling, and prints progress logs including the final success message.",
    "app/main.py": "The FastAPI application entry point or equivalent module that wires routers and application-level dependencies while leaving the core task behavior incomplete or logically flawed according to the scenario.",
    "app/schemas.py": "The Pydantic request, response, or event schema module that provides enough structure for the candidate to extend validation or message contracts without revealing the full solution.",
    "app/rabbitmq.py": "The RabbitMQ connection, topology, producer, or helper module that provides a realistic starting point for broker integration while preserving the intended intermediate-level work for the candidate.",
    "app/worker.py": "The consumer or worker module when the scenario includes asynchronous processing, manual acknowledgement behavior, retry handling, or DLQ behavior that the candidate must complete or fix.",
    "tests/test_task_behavior.py": "Optional lightweight tests or contract checks that describe observable behavior after completion without giving away the full implementation approach."
  }},
  "answer": "The evaluator-facing high-level solution approach explaining the expected FastAPI structure, RabbitMQ topology or message-flow corrections, validation behavior, acknowledgement and retry strategy, and reliability tradeoffs without requiring exact code.",
  "definitions": "An object of term-to-definition pairs for relevant FastAPI and RabbitMQ terms used in the task, such as exchange, binding, routing key, durable queue, correlation ID, manual acknowledgement, prefetch, dead-letter queue, Pydantic model, and dependency injection.",
  "hints": "A single line hint on what a good intermediate-level approach should investigate without revealing the specific fix, exact RabbitMQ calls, or implementation sequence.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable API behavior, correct message routing or processing, failure handling, and maintainable integration. Use simple english.",
  "pre_requisites": "A bullet-point list of tools and knowledge needed to complete the task, including Python 3.10+, pip, Git, Docker with Docker Compose, FastAPI fundamentals, and intermediate RabbitMQ messaging concepts.",
  "short_overview": "A bullet-point list in simple language summarising the selected business problem, the FastAPI and RabbitMQ technical focus, and the expected reliable outcome after the candidate completes the work."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be human-readable, 50-80 characters, and different from name.
4. **code_files** must include README.md, .gitignore, requirements.txt, docker-compose.yml, run.sh, kill.sh, and Python source files.
5. **docker-compose.yml** must include RabbitMQ only unless the selected scenario explicitly requires another service, must have no version specification, and must bind ports to localhost only.
6. **run.sh** must install Python dependencies first, start RabbitMQ, wait for health, run only readiness smoke checks, and must not run failing grader tests.
7. **kill.sh** must follow the 9-step cleanup shape, use `|| true` where appropriate, remove /root/task, and print `Cleanup completed successfully!`.
8. **README.md** must follow exactly Task Overview, Helpful Tips, Objectives, How to Verify, with no extra sections.
9. **README.md** must be concise, open-ended, and must not contain setup commands, direct solutions, RabbitMQ credentials, connection details, or step-by-step implementation guides.
10. **Starter code** must be runnable and FULLY FUNCTIONAL for the described current state but must NOT contain the solution.
11. **NO comments in code** that reveal the solution or give hints.
12. **Task must be completable within {minutes_range} minutes** for an intermediate candidate.
13. **Use Python 3.10+ and FastAPI** best practices throughout.
14. **Use RabbitMQ concepts within intermediate scope**: routing, durable topology, JSON contracts, message properties, manual ack/nack/reject, prefetch, retries, DLQ, and practical operational reasoning.
15. **Do not require expert RabbitMQ operations** such as clustering internals, multi-region active-active, advanced broker tuning, or Kubernetes deployment as the core task.
16. **Select a different real-world scenario** each time for variety and keep the task domain aligned with the provided scenarios.
"""

PROMPT_REGISTRY = {
    "Python - FastAPI (INTERMEDIATE), RabbitMQ (INTERMEDIATE)": [
        PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_FASTAPI_RABBITMQ_INTERMEDIATE_INSTRUCTIONS,
    ]
}