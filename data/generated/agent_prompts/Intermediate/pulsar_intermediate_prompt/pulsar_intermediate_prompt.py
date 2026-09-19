# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


"""Prompt registry entry for Pulsar INTERMEDIATE task generation."""

PROMPT_PULSAR_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_PULSAR_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a INTERMEDIATE assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION PROMPT CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must evaluate applied Apache Pulsar competence at INTERMEDIATE level: producers and consumers, topic and subscription strategy, schemas, retry/DLQ behavior, acknowledgments, ordering, batching, backpressure, and operational observability.
- The task must be a realistic work item involving existing starter code that is FULLY FUNCTIONAL as a scaffold but has messaging correctness, reliability, or performance issues the candidate must diagnose and improve.
- The task must be completable within {minutes_range} minutes by a candidate with 3-5 years of experience.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match INTERMEDIATE Pulsar level?
"""

PROMPT_PULSAR_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements (Apache Pulsar)

## GOAL
As a technical architect super experienced in Apache Pulsar, you are given a list of real world scenarios and proficiency levels for Apache Pulsar. Generate a complete assessment task — description, starter code files, infrastructure files, tests, and README — that tests a candidate at INTERMEDIATE proficiency in Pulsar.

The task must be a realistic, hands-on Pulsar integration or debugging task that requires the candidate to reason about message flow, subscriptions, schemas, delivery semantics, retry/DLQ behavior, ordering, batching, backpressure, and operational verification.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to have 3-5 years of engineering experience and practical intermediate familiarity with Apache Pulsar. They should be comfortable reading and modifying existing producer and consumer code, using a Pulsar client library, understanding persistent topics, message keys, acknowledgments, retry and dead-letter behavior, schema choices, and basic performance tuning.

The candidate should not be asked to perform deep BookKeeper internals work, production cluster topology design, advanced geo-replication implementation, or memorized CLI syntax. Focus on applied service-level Pulsar integration and pragmatic troubleshooting.

The generated starter project must be FULLY FUNCTIONAL and FULLY POPULATED as an assessment scaffold. It should run in a local E2B sandbox with Apache Pulsar supplied by docker-compose, and it should contain enough realistic code for the candidate to navigate multiple interacting files before making changes.

## INSTRUCTIONS
### Nature of the Task
- The task asks the candidate to fix or improve an existing Pulsar-backed service or pipeline. The current implementation must contain realistic issues such as opaque payloads where schemas are needed, wrong subscription type for ordering or parallelism, missing retry/DLQ behavior, poor acknowledgment handling, unbounded pending sends, batching/compression disabled in a hot path, inadequate message keys, or weak handling of malformed messages.
- **CRITICAL**: The task must stay within intermediate Apache Pulsar scope. It may require producers, consumers, schemas, message properties, partitioned topics, subscription type selection, batching, compression, retry topics, DLQ topics, acknowledgments, receiver queue sizing, idempotency reasoning, and basic metrics/log interpretation. It must not require expert-only cluster administration, custom broker plugins, deep BookKeeper tuning, complex geo-replication rollout, or security infrastructure beyond conceptual least-privilege discussion.
- **CRITICAL**: The task must be implementation-oriented and realistic, not a pure essay and not a recall quiz. The candidate should need to read existing code, infer current behavior, and make targeted changes across more than one file.
- **CRITICAL**: For INTERMEDIATE level, the starter codebase MUST be substantial and realistic, NOT a toy snippet. Require multiple interacting modules/files in a real project layout, with non-trivial existing logic the candidate must read and reason about before changing. Changes should span MORE THAN ONE file.
- The task should be completable within {minutes_range} minutes. Keep the work scoped to a moderate production issue in one service or pipeline, not an entire distributed system redesign.
- The current implementation must run cleanly as a scaffold. It may fail behavioral tests that represent the candidate's required fixes, but it must not have syntax errors, import errors, missing files, broken dependency installation, or infrastructure boot failures.
- Do NOT include the solution, TODO comments, or solution-revealing comments in starter code.
- Avoid tasks that are primarily about testing framework usage, environment setup, CLI flag memorization, or language/library syntax.
- The task name must be short, under 50 characters, kebab-case.
- The title must be a human-readable display name in "<action verb> <subject>" format, 50-80 characters, and different from the repository name.
- For executable code, always invoke interpreters by their explicit name where applicable, such as `python3`, never bare `python`.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Apache Pulsar documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The assessment is designed to evaluate how candidates solve realistic engineering tasks with the resources available to modern software engineers.

Candidates must still understand, adapt, and validate any code or guidance they use. The submitted solution should reflect their own engineering judgment.

The task must be specific enough that using external resources does not trivialize it, and must require candidate reasoning about the provided starter code and scenario.

## Code Generation Instructions
Generate a complete local project for a Pulsar-backed Python service or pipeline using the Apache Pulsar Python client. The generated code should include realistic modules for producers, consumers, schemas/models, configuration, message handling, and tests.

The starter code must reflect the selected scenario's current broken or incomplete implementation. It should include enough behavior to demonstrate the issue without giving away the fix.

The project should include:
- A Python dependency manifest such as `requirements.txt`.
- A source package containing Pulsar client integration code.
- Separate modules for producer behavior, consumer behavior, message model or schema handling, and business processing.
- Tests that encode observable expectations around Pulsar behavior, message handling, schema compatibility, ordering, retry/DLQ, acknowledgment decisions, or producer/consumer configuration.
- Local fixtures or sample messages that represent old and new event shapes where schema evolution is part of the scenario.
- A README.md following the README instructions below.
- A `.gitignore`.
- `docker-compose.yml` and `run.sh` because this is an infrastructure-shaped Pulsar task.

Do not require a candidate to connect to any remote host. All files and scripts must be designed for the local sandbox.

## Infrastructure Requirements
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

The generated infrastructure must start a local Apache Pulsar standalone service suitable for development and integration testing. The infrastructure is for candidate experimentation and readiness verification, not a production deployment.

No `kill.sh` is needed. E2B sandboxes are destroyed as a whole when the session ends, so container cleanup is automatic.

### Docker-compose Instructions
The `docker-compose.yml` file MUST:
- Define an Apache Pulsar standalone service suitable for local testing.
- **MUST NOT include any version specification** at the top level of the compose file.
- Bind every exposed Pulsar port to localhost only.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
- Expose the Pulsar binary protocol on `127.0.0.1:6650:6650`.
- Expose the Pulsar admin HTTP service on `127.0.0.1:8080:8080`.
- Include a healthcheck that verifies the local Pulsar service is responsive before run.sh continues.
- Use stable service names and avoid relying on external `.env` files or `${{VAR}}` host interpolation.
- Not include PostgreSQL, MySQL, Redis, Kafka, or any other datastore unless the selected real-world scenario explicitly requires that additional service. For a Pulsar messaging task, Pulsar standalone is normally sufficient.

### Pulsar Configuration Instructions
The Pulsar service should be configured for a local standalone development cluster. Keep configuration simple and reliable.

If the task requires tenant, namespace, partitioned topic, schema, retry topic, or DLQ setup, include this setup in `run.sh` using Pulsar admin commands executed against the local Pulsar container or admin endpoint. The setup should align with the selected scenario's domain, such as media playback events or courier location events.

Do not make candidates memorize CLI commands as the primary assessment. Infrastructure setup should support the task; the assessment should focus on Pulsar application behavior and design choices.

When topics are referenced in starter code, tests, README, or setup scripts, keep naming consistent. Use realistic persistent topic names in the Pulsar format, such as `persistent://tenant/namespace/topic-name`.

### Run.sh Instructions
The `run.sh` file MUST:
- Be executable and start with a robust shell preamble appropriate for readiness checks.
- Use `/root/task` as the base directory.
- Install the task's own third-party dependencies as its FIRST project step, for example `python3 -m pip install -q -r requirements.txt`.
- Run `docker compose up -d` to start the Pulsar service.
- Wait for Pulsar readiness using a bounded retry loop.
- Create any required tenant, namespace, partitioned topic, retry topic, or DLQ topic needed by the starter scenario.
- Verify the starter project compiles or imports successfully, such as with `python3 -m compileall` or a targeted import smoke check.
- If it runs tests as a deployability probe, it must treat failing behavioral tests as acceptable only when the test runner successfully collected and executed the suite. For pytest, mirror these exit codes: 0 and 1 mean the scaffold is deployable and `run.sh` exits 0; exit codes greater than or equal to 2, including no tests collected, mean the scaffold is broken and `run.sh` exits non-zero.
- Not run the grader as a pass/fail gate. `run.sh` is a readiness/self-check, not the final evaluator.
- Not include `docker compose down`, container deletion, or a `kill.sh` workflow.

### Dockerfile Instructions
Omit a Dockerfile unless the selected scenario explicitly requires an application container. For this local Pulsar task, prefer running Python code directly from `/root/task` against the Pulsar service exposed on localhost.

The output should be a valid json schema and include the following files in `code_files`:
- `README.md`: Candidate-facing task overview with the exact README sections described below.
- `.gitignore`: Standard Python, local environment, logs, cache, and editor exclusions.
- `requirements.txt`: Python dependencies needed by the starter project, tests, and Pulsar client integration.
- `docker-compose.yml`: Local Apache Pulsar standalone service with localhost-only port bindings and no top-level compose version.
- `run.sh`: Readiness script that installs dependencies, starts Pulsar, waits for health, creates required Pulsar resources, and verifies the scaffold loads.
- Source files under a realistic package path such as `src/`, `app/`, `pulsar_app/`, `routes/`, `producers/`, `consumers/`, `schemas/`, or `services/`.
- Tests under `tests/` that express the behavioral expectations the candidate must satisfy.
- Fixtures under a path such as `fixtures/` when sample events, schema examples, or malformed messages help ground the task.

## Code file requirements
- The starter code must be complete enough to run, import, and exercise locally.
- The starter code must implement exactly the "Current Implementation" described in the question. If the question says the producer sends raw JSON bytes, the starter code should actually do that. If it says the consumer fails to acknowledge malformed messages, the starter code should reflect that behavior.
- Keep solution-revealing comments out of the code. Do not add `TODO`, `FIXME`, or comments that directly name the required implementation.
- Include meaningful function and class names consistent with the business scenario, but do not make the one-line fix obvious.
- Tests may describe expected behavior, but they should not reveal a full implementation strategy.
- Include realistic edge cases such as older event shapes, malformed payloads, duplicate event identifiers, transient publish failures, redelivery, or per-key ordering when appropriate.
- Prefer a project layout where producer, consumer, schema/model, and business logic are separated into different files.
- The Pulsar service URL used by code and scripts should point to `pulsar://localhost:6650` for local execution unless the code is running inside the compose network.
- Admin or health checks should use `http://localhost:8080` from the sandbox host.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## .gitignore INSTRUCTIONS
The `.gitignore` file must include appropriate exclusions for:
- Python bytecode and cache directories.
- Virtual environments.
- Test and coverage artifacts.
- Local environment files such as `.env`.
- Logs and temporary files.
- Editor and operating-system metadata.

Do not exclude source files, tests, fixtures, README.md, docker-compose.yml, run.sh, or dependency manifests.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md file MUST contain exactly these sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. NEVER leave this section empty. Do not include bold time-budget callouts.

### Objectives
For INTERMEDIATE level, include 3-4 bullets max; fewer, tighter is better.

Objectives MUST be concise and OPEN-ENDED. Each objective states ONE desired outcome in a single short line, roughly 8-16 words, one deliverable each. Describe the what and why, NEVER the how. Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, or any other direct code reference. The candidate must discover both the mechanism and where to change it.

Bad objective examples:
- Improve query performance.
- The producer sends every event slowly; after your changes it should publish faster.
- Fix the lifecycle rule in main.tf so transitions apply to closed objects.
- Use Key_Shared subscriptions with message keys.

Good objective examples:
- Preserve per-entity ordering while allowing parallel event processing.
- Prevent malformed messages from causing unbounded redelivery.
- Keep publish latency responsive during normal peak traffic.

### Helpful Tips
Include 4-5 bullets max. Provide practical guidance without revealing specific implementations.

Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".

Tips guide discovery. They MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task. They should help the candidate inspect message flow, delivery semantics, ordering expectations, schema compatibility, backlog behavior, or operational symptoms without revealing the exact fix.

### How to Verify
Include 3-5 bullets max. Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.

Each bullet should be a check the candidate can run or observe, such as test output, response shape, message flow behavior, backlog stabilization, retry or dead-letter behavior, latency observation, log line, or schema compatibility result.

Use `localhost` for any legitimate local verification command that references Pulsar endpoints. Do not use droplet IPs, remote hosts, or placeholders like `<DROPLET_IP>`.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section):**
Keep the following out of the generated README:
- Setup commands such as `pip install`, `docker compose up`, or `pytest`.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, configuration names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Database-connection details, usernames, passwords, client-tool suggestions, droplet IP placeholders, or remote-host placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context`; synonyms produce a hollow, unusable task.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the Pulsar task without duplicating the title.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from the repository name.",
  "question": "The full candidate-facing task description; MUST include clearly labeled 'Current Implementation' and 'Required Changes' subsections describing the existing Pulsar behavior and the outcomes the candidate must deliver without revealing the solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, following all README constraints above.",
    ".gitignore": "A stack-appropriate ignore file covering Python caches, virtual environments, local environment files, logs, coverage artifacts, and editor metadata without excluding task source files.",
    "requirements.txt": "The Python dependency list required for the Pulsar client integration, tests, and local scaffold verification.",
    "docker-compose.yml": "A local Apache Pulsar standalone compose configuration with localhost-only port bindings, no top-level version field, and a healthcheck suitable for run.sh readiness.",
    "run.sh": "An executable readiness script that installs dependencies, starts Pulsar, waits for health, prepares required Pulsar resources, and verifies that the unsolved starter project loads without using tests as a failing gate.",
    "src_or_package_files": "Multiple realistic Python source files implementing the current producer, consumer, schema or model, configuration, and business-processing behavior for the selected scenario.",
    "tests": "A focused test suite that captures expected Pulsar messaging behavior, compatibility, ordering, retry, DLQ, acknowledgment, or configuration outcomes without including the solution.",
    "fixtures": "Task-specific sample events, malformed messages, or schema examples that make the scenario reproducible and grounded."
  }},
  "answer": "Evaluator-facing high-level solution approach explaining the intended Pulsar concepts, code changes, and reasoning paths without being shown to candidates.",
  "definitions": "An object mapping important Pulsar and scenario terms to concise definitions relevant to the task, such as topic, subscription, message key, schema compatibility, retry topic, DLQ, backlog, or acknowledgment.",
  "hints": "A single-line hint nudging investigation toward the right Pulsar behavior or tradeoff without naming the exact implementation or configuration to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable messaging correctness, reliability, ordering, latency, backlog, schema, or retry/DLQ improvements using simple English.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3.11 proficiency, familiarity with Apache Pulsar producers and consumers, comfort with local Docker-backed services, and understanding of delivery semantics; do not include imperative setup or verification steps.",
  "short_overview": "A bullet list summarizing the business problem, the Pulsar technical focus, and the expected operational outcome."
}}

## CRITICAL REMINDERS
1. Output JSON uses the CANONICAL key names above — this is non-negotiable.
2. The `question` field MUST include the labels "Current Implementation" and "Required Changes".
3. Environment runs perfectly out of the box; the candidate fixes the Pulsar task, not the environment.
4. Starter code is runnable but does NOT contain the core solution.
5. Starter code perfectly matches the described Current Implementation.
6. Do not include solution-revealing comments, TODO markers, or hidden implementation instructions.
7. docker-compose.yml MUST NOT include any top-level version specification.
8. **SECURITY-CRITICAL**: all exposed Pulsar ports must bind to `127.0.0.1`.
9. run.sh must install project dependencies before readiness checks and must not act as the final grader.
10. Completable within {minutes_range} minutes by an intermediate candidate.
"""

PROMPT_REGISTRY = {
    "Pulsar (INTERMEDIATE)": [
        PROMPT_PULSAR_INTERMEDIATE_CONTEXT,
        PROMPT_PULSAR_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PULSAR_INTERMEDIATE_INSTRUCTIONS,
    ]
}