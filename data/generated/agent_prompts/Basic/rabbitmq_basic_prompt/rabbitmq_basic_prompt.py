# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


"""RabbitMQ BASIC task generation prompt."""

PROMPT_RABBITMQ_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_RABBITMQ_BASIC_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a BASIC RabbitMQ assessment task.

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
- The task must be a well-scoped RabbitMQ configuration, topology, publishing, consuming, acknowledgement, or routing fix combining 2-3 BASIC concepts.
- It must be completable within {minutes_range} minutes by a candidate with 1-2 years of focused RabbitMQ experience.
- Keep the scope small and realistic: diagnosing why messages are not reaching a queue, fixing an acknowledgement or redelivery issue, improving a simple durable queue/persistent message setup, or adding a basic DLQ path.
- The task must include a FULLY FUNCTIONAL local single-node RabbitMQ broker using Docker Compose with the Management Plugin enabled.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the RabbitMQ task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match BASIC level?
"""

PROMPT_RABBITMQ_BASIC_INSTRUCTIONS = """
# BASIC Task Requirements (RabbitMQ)

## GOAL
As a technical architect super experienced in RabbitMQ and AMQP 0-9-1, you are given a list of real world scenarios and proficiency levels for RabbitMQ. Generate a complete assessment task — description, starter files, RabbitMQ infrastructure, README — that tests a candidate at BASIC proficiency (1-2 years experience). The task must be a well-scoped feature or bug fix combining 2-3 practical RabbitMQ concepts.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to work like a RabbitMQ practitioner with roughly 1-2 years of focused experience. They should be able to reason about a single-node broker, the Management Plugin, exchanges, queues, bindings, routing keys, vhosts, channels, acknowledgements, prefetch, durable queues, persistent messages, dead-letter exchanges/dead-letter queues, and common routing or acknowledgement mistakes.

The generated task must give the candidate a FULLY FUNCTIONAL and FULLY POPULATED starting environment. The environment should start cleanly, RabbitMQ should become healthy, and the provided starter topology/scripts/configuration should represent the exact buggy or incomplete state described in the question. The candidate fixes the RabbitMQ task, not the environment.

## INSTRUCTIONS

### Nature of the Task
- The task asks the candidate to implement a small RabbitMQ feature or fix a realistic RabbitMQ bug in existing starter files. Focus on 2-3 BASIC concepts such as direct/topic/fanout routing, durable queue declarations, persistent publishing, manual acknowledgements, prefetch, dead-lettering, vhosts/users/permissions, or simple troubleshooting of missing bindings and incorrect routing keys.
- **CRITICAL**: Stay within BASIC RabbitMQ scope. Do not require clustering, quorum queues, stream queues, advanced federation/shovel design, advanced TLS automation, complex performance tuning, multi-region failover, Kubernetes operators, or deep Erlang/RabbitMQ internals.
- **CRITICAL**: The candidate should solve a realistic applied work item, not answer pure RabbitMQ trivia. Examples include fixing a direct exchange binding key mismatch, changing an unreliable auto-ack consumer to manual ack with a DLQ, making a queue/message durable enough to survive broker restart, or cleaning up a simple vhost/user/permission configuration.
- **CRITICAL**: The task should be completable within {minutes_range} minutes. Keep file count modest and the required code/configuration changes small.
- **CRITICAL**: Starter files must run cleanly and must not contain syntax errors, broken Docker syntax, missing scripts, missing permissions, or missing executable bits.
- Generate enough starter files to give a clear starting point WITHOUT giving away the solution.
- The starter state MUST exactly match the "Current Implementation" described in the task question.
- Do NOT include the solution, TODO comments, or solution-revealing comments in starter files.
- If client code is included, keep it simple and focused on RabbitMQ behavior rather than language trivia. Use a mainstream RabbitMQ client pattern only when it directly supports the scenario.
- If the task is primarily RabbitMQ configuration or operations oriented, it may use shell scripts, RabbitMQ definitions JSON, rabbitmqadmin/rabbitmqctl checks, and sample message payload files rather than a full application.
- The candidate should understand at-least-once delivery and duplicate processing implications, but the task must not require building a complex idempotency store.
- The generated task should include observable verification that a queue receives the right message, a failed message reaches a DLQ, a durable queue survives restart, permissions allow the intended action, or a routing/topology issue is corrected.
- Task name: short, under 50 characters, kebab-case.
- Task title: human-readable display name in "<action verb> <subject>" format, 50-80 characters.
- For executable scripts, always invoke tools explicitly and consistently. Use `bash` for shell scripts and avoid relying on aliases.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, RabbitMQ documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

However:
- The submitted work must be their own understanding and implementation of the requested RabbitMQ fix or feature.
- They should be able to explain the topology, routing, acknowledgement, durability, and verification choices they made.
- They must not paste in unrelated boilerplate that changes the task scope or bypasses the assessment.
- The task should be designed so that practical reasoning and careful changes matter more than memorizing exact commands.

## RabbitMQ Generation Instructions
- Generate a RabbitMQ-centered task with a single-node broker using the official RabbitMQ image with the Management Plugin enabled.
- Use a realistic vhost, exchange, queue, binding, routing key, user, and password naming scheme tied to the chosen business scenario.
- Include only the RabbitMQ concepts needed by the selected scenario. Do not add unrelated exchanges, queues, users, policies, plugins, or application services.
- The initial topology may be provided through RabbitMQ definitions JSON, startup scripts that call the Management API, or simple seed scripts, as long as the environment is reliable and clear.
- If using RabbitMQ definitions JSON, include users, vhosts, permissions, exchanges, queues, bindings, and policies needed for the starter state.
- If the task includes dead-lettering, keep it basic: one normal queue, one DLX, and one DLQ are sufficient.
- If the task includes durability, align durable queues with persistent messages and make the behavior verifiable after a broker restart.
- If the task includes acknowledgements, provide a clear starter consumer or script state where auto-ack/manual-ack behavior is the central issue.
- If the task includes routing, use simple direct, topic, or fanout behavior. Make routing-key and binding mismatches realistic and easy to inspect.
- Include starter payload examples using JSON when message contents are needed. Keep schemas small and business-relevant.
- Include basic verification scripts only when they are readiness or scenario helpers. Do not provide a script that solves the task.
- Avoid making the candidate install RabbitMQ locally outside Docker.

## Infrastructure Requirements

### Docker-compose Instructions
- You MUST include a `docker-compose.yml` file for the RabbitMQ broker.
- The compose file MUST use a RabbitMQ image with the Management Plugin enabled, such as `rabbitmq:3-management`.
- The compose file **MUST NOT include any version specification**.
- The compose service name should be clear, such as `rabbitmq`.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every RabbitMQ port exposed to the host.
- Expose AMQP and Management UI only if required for the task, using localhost bindings:
  - `127.0.0.1:5672:5672` for AMQP
  - `127.0.0.1:15672:15672` for the Management UI
- If TLS is not the focus of the task, do not expose port 5671.
- Do not expose clustering or Erlang distribution ports unless the task explicitly requires them; BASIC tasks should not require them.
- Set standard RabbitMQ startup environment values inline in `environment:`. At minimum include `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`, and `RABBITMQ_DEFAULT_VHOST` when a non-default starter account/vhost is used.
- Forbid `.env` files and host-variable indirection such as `${{RABBITMQ_DEFAULT_USER}}` or `${{RABBITMQ_DEFAULT_PASS}}`; use inline service environment values so the container initializes reliably.
- If definitions are loaded at startup, mount the definitions file read-only and set the appropriate RabbitMQ management load definitions configuration.
- Use a named volume for RabbitMQ data only when the scenario needs restart/durability verification. Otherwise keep the setup simple.
- Include a healthcheck that waits for RabbitMQ to be ready, such as `rabbitmq-diagnostics -q ping`.
- The broker, healthcheck, definitions, Management UI credentials, and any verification scripts must use the same vhost/user/password consistently.
- Do not include an application Dockerfile unless the selected scenario truly needs an app container. For BASIC RabbitMQ tasks, prefer local scripts plus RabbitMQ in Compose.

### RabbitMQ Configuration Instructions
- Include any required RabbitMQ definitions or configuration files in the JSON output under `code_files`.
- If using `definitions.json`, make it valid JSON and include only the starter topology needed for the task.
- If the starter state intentionally contains a RabbitMQ bug, make the bug realistic and isolated, such as an incorrect binding key, non-durable queue, missing DLQ argument, auto-ack consumer behavior, or missing permission.
- Keep RabbitMQ passwords and local-only credentials suitable for an assessment environment, and do not instruct candidates to reuse them in production.
- If a vhost is used, ensure exchanges, queues, bindings, permissions, and connection examples all reference that vhost.
- If policies are used, keep them simple and directly tied to the task, such as a TTL or dead-letter policy.
- If sample messages are provided, use small JSON payloads with business fields relevant to the selected scenario.
- Do not require exact command memorization. Provide enough scripts or documentation for candidates to inspect the environment and verify behavior.

### Run.sh Instructions
- You MUST include a `run.sh` script.
- The script must use `/root/task` as the base directory.
- The script must start RabbitMQ using `docker compose up -d`.
- The script must wait until RabbitMQ is healthy before running readiness checks.
- The script is a READINESS/self-check, NOT the grader. It must verify that the broker starts, the Management Plugin is reachable if used, and starter files are present/valid.
- The script MUST NOT run a candidate-solving test suite that is expected to fail before the candidate completes the task.
- The script may run non-solution readiness checks such as:
  - `docker compose ps`
  - waiting for `rabbitmq-diagnostics -q ping`
  - checking that expected files exist
  - validating JSON syntax for definitions or sample payloads
  - confirming the management endpoint responds with the configured local credentials
- The script should print clear logs for each readiness step.
- The script must exit 0 when the UNSOLVED starter environment is healthy.
- The script must fail fast if Docker Compose cannot start RabbitMQ or if RabbitMQ does not become healthy.
- Do not include `apt-get install`, `pip install`, `npm install`, or package installation commands in `run.sh`.

## kill.sh file instructions
The task MUST include a `kill.sh` script with the following cleanup behavior:

1. Start with a bash shebang and `set -e`.
2. Print logs at every cleanup step so the user can see what is happening.
3. Change to `/root/task` if it exists.
4. Stop Docker Compose services with `docker compose down --remove-orphans --volumes || true`.
5. Remove any project-specific Docker volumes with `docker volume rm ... || true` when named volumes are used.
6. Remove any project-specific Docker networks with `docker network rm ... || true` when named networks are used.
7. Force-remove any project-specific Docker images with `docker rmi -f ... || true` only if the task builds images.
8. Run `docker system prune -a --volumes -f || true`.
9. Remove the task directory with `rm -rf /root/task || true` and print `Cleanup completed successfully!` as the final message.

The script must be idempotent. Use `|| true` for cleanup operations that may safely fail if resources do not exist.

The output should be a valid json schema:
- `docker-compose.yml`: RabbitMQ broker infrastructure with localhost-bound ports, inline RabbitMQ environment values, and a healthcheck.
- `run.sh`: Readiness script that starts RabbitMQ, waits for health, checks starter assets, and exits successfully for the unsolved starter environment.
- `kill.sh`: Idempotent cleanup script following the 9-step cleanup shape above.
- `README.md`: Candidate-facing instructions with the exact README sections requested below.
- `.gitignore`: Standard exclusions for local artifacts, logs, caches, generated files, and RabbitMQ data if applicable.
- RabbitMQ configuration files such as `definitions.json`, `rabbitmq.conf`, or topology scripts when needed by the scenario.
- Optional sample payload files such as `sample_message.json` when needed to make the routing or acknowledgement behavior observable.
- Optional lightweight producer/consumer/helper scripts only when the scenario requires practical client interaction; these must start cleanly and represent the incomplete or buggy state.

## Code file requirements
- All file paths in `code_files` must be relative paths suitable for placement under `/root/task`.
- Starter files must be complete and runnable. Do not use placeholders such as "fill this in" or "your code here".
- Do not include TODO comments, solution-revealing comments, or comments that directly tell the candidate exactly what line to change.
- If shell scripts are included, make them robust, readable, and compatible with bash.
- If JSON files are included, they must be syntactically valid JSON.
- If client scripts are included, they must connect to the RabbitMQ broker using the configured localhost port, vhost, username, and password.
- If the task expects the candidate to change a client script, the script must have a real, minimal incomplete behavior that matches the question.
- If the task expects the candidate to change topology/configuration, the starter topology must reflect the exact misconfiguration described in the question.
- Do not include advanced framework scaffolding or unrelated business logic.
- Keep the task small enough for a BASIC candidate to inspect and fix within {minutes_range} minutes.
- The `answer` field must describe the evaluator-facing high-level solution approach, including the RabbitMQ concepts involved, without being included in README.md.

## .gitignore INSTRUCTIONS
The `.gitignore` file should include common local and generated artifacts for this task:
- OS/editor files such as `.DS_Store`, `.idea/`, `.vscode/`
- logs such as `*.log`
- temporary files such as `tmp/`, `temp/`
- local environment files such as `.env`
- cache directories such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` if any Python helpers are included
- dependency directories such as `node_modules/` only if Node helpers are included
- local RabbitMQ data directories if the task uses bind-mounted data
- generated output files created by helper scripts

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The `README.md` file inside `code_files` MUST contain exactly these candidate-facing sections, in this order, and no other headings:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

### Task Overview
- Include 3-4 meaningful sentences.
- Do not use a bullet list.
- Describe the business scenario, current state, and why the RabbitMQ problem matters.
- NEVER leave this section empty.
- Do not include bold time-budget callouts.
- Do not include database-connection details, RabbitMQ credentials, hostnames, ports, or Management UI login instructions in this section.

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not directly state the exact exchange type, routing key, acknowledgement method, queue argument, or setting the candidate must change if that would give away the solution.

### Objectives
- Include 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should focus on RabbitMQ behavior such as correct routing, reliable delivery, appropriate failure handling, durable broker state, or clean operational visibility.
- Avoid naming specific commands, method names, or exact configuration arguments that reveal the answer.

### How to Verify
- Include 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as readiness output, queue depth behavior, message location, restart behavior, log line, or management-visible state.
- Do not include setup commands such as `docker compose up`, package installation commands, or full step-by-step solutions.
- Do not include RabbitMQ host, port, username, password, or client-tool suggestions.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README. This is an instruction for task generation only and must never appear as a README heading:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or similar commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, data-structure names, exact queue arguments, exact acknowledgement calls, or exact RabbitMQ settings that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", or equivalent wording.
- `<DROPLET_IP>` placeholders.
- Database-connection details or RabbitMQ connection details such as host, port, username, password, Management UI URL, or client-tool login suggestions.
- Extra README sections such as `Database Schema Overview`, `Database Access`, `Performance Issues`, `NOT TO INCLUDE`, or `NOT TO INCLUDE in README`.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context` because synonyms produce a hollow, unusable task. Each field value below is a description of what to fill in.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the RabbitMQ task.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from the repository name.",
  "question": "The full candidate-facing task description including the business scenario, Current Implementation, Required Changes, and success criteria while staying within BASIC RabbitMQ scope.",
  "code_files": {{
    "README.md": "The concise candidate-facing README containing exactly Task Overview, Helpful Tips, Objectives, and How to Verify in that order with no extra headings.",
    ".gitignore": "A stack-appropriate gitignore covering local artifacts, logs, caches, generated files, environment files, and task-specific temporary output.",
    "docker-compose.yml": "The RabbitMQ Docker Compose infrastructure file with no version specification, localhost-bound ports, inline RabbitMQ environment values, and a healthcheck.",
    "run.sh": "A readiness script that uses /root/task, starts RabbitMQ with docker compose up -d, waits for health, validates starter assets, and exits 0 for the unsolved starter environment.",
    "kill.sh": "An idempotent cleanup script that stops compose services, removes volumes/networks/images as appropriate, prunes Docker resources, removes /root/task, and prints a final cleanup success message.",
    "RabbitMQ configuration and helper files": "Any definitions, configuration, sample payloads, or lightweight scripts needed to represent the incomplete starter state and support verification without revealing the solution."
  }},
  "answer": "Evaluator-facing high-level solution approach explaining the RabbitMQ topology, routing, acknowledgement, durability, permission, or dead-letter changes expected without being shown to the candidate.",
  "definitions": "An object mapping RabbitMQ and task-domain terms to concise definitions relevant to the assessment, such as exchange, queue, binding, routing key, acknowledgement, prefetch, durable queue, persistent message, vhost, DLX, or DLQ.",
  "hints": "A single line hint nudging investigation toward the relevant RabbitMQ behavior without revealing the exact fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable RabbitMQ behavior such as correct routing, reliable acknowledgement, DLQ placement, durable restart behavior, or clean queue state. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as Docker Compose basics, RabbitMQ Management Plugin awareness, AMQP concepts, and simple JSON/message-flow reasoning.",
  "short_overview": "A bullet list summarising the business problem, the RabbitMQ technical focus, and the expected operational outcome."
}}

## CRITICAL REMINDERS
1. Environment runs perfectly out of the box; the candidate fixes the RabbitMQ TASK, not the environment.
2. The task must include `docker-compose.yml`, `run.sh`, and `kill.sh` because this is an infra-shaped RabbitMQ assessment.
3. `docker-compose.yml` **MUST NOT include any version specification**.
4. **SECURITY-CRITICAL**: RabbitMQ ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
5. Inline RabbitMQ environment values are required; do not use `.env` files or host-variable indirection.
6. Starter files are runnable and FULLY FUNCTIONAL but do NOT contain the core solution.
7. Starter files perfectly match the "Current Implementation" described in the question.
8. No solution-revealing comments, TODOs, or README guidance that gives away the exact RabbitMQ fix.
9. Keep the task BASIC and completable within {minutes_range} minutes.
10. Output JSON uses the CANONICAL key names above — this is non-negotiable.
"""

PROMPT_REGISTRY = {
    "RabbitMQ (BASIC)": [
        PROMPT_RABBITMQ_BASIC_CONTEXT,
        PROMPT_RABBITMQ_BASIC_INPUT_AND_ASK,
        PROMPT_RABBITMQ_BASIC_INSTRUCTIONS,
    ]
}