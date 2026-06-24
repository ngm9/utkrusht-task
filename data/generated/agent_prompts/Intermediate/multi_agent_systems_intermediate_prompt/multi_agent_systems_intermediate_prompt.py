# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_MULTI_AGENT_SYSTEMS_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MULTI_AGENT_SYSTEMS_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Multi-Agent Systems assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- Because this is an infrastructure-shaped task, the generated project MUST include local infrastructure services needed by the selected scenario, such as Redis, Qdrant, a message log database, or another explicitly scenario-relevant service

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Multi-Agent Systems implementation, debugging, review, or improvement required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_MULTI_AGENT_SYSTEMS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Multi-Agent Systems, LLM-based agent orchestration, structured agent communication, tool-using agents, agent memory, workflow coordination, reliability, safety, and observability, you are given a list of real world scenarios and proficiency levels for Multi-Agent Systems.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to operate like an intermediate AI Agent Engineer who can independently work on mid-sized multi-agent applications with limited oversight.
The task should assess practical judgment around agent roles, state, goals, tool boundaries, structured messaging, coordination, retries, timeouts, memory, guardrails, observability, and trade-offs between quality, latency, cost, and reliability.
The candidate should receive a FULLY FUNCTIONAL starter project with a FULLY POPULATED README.md and runnable local infrastructure so they can focus on the Multi-Agent Systems problem rather than project setup.
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, review or improve an unsafe workflow, fix coordination bugs, or optimize an existing multi-agent workflow.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix errors.
- The question should be a real-world scenario that tests Multi-Agent Systems architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years experience with agentic systems, orchestration, backend workflows, or applied AI systems).
- **CRITICAL**: Keep the task completable within {minutes_range} minutes. Prefer one focused workflow or failure mode over a broad platform build.
- **CRITICAL**: The task must remain within intermediate Multi-Agent Systems scope. It may test agent decomposition, role boundaries, state, goals, policies, actions, lifecycle, memory, structured messages, communication, coordination, planning, verification, safety, logging, metrics, and practical orchestration trade-offs.
- **CRITICAL**: The task must NOT require expert-level MARL implementation, advanced reinforcement learning algorithms, Kubernetes deployment, production secrets management, complex vector database tuning, advanced prompt research, or large-scale distributed platform design as the primary skill.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Agent Fundamentals**: Distinguishing agents from traditional services, defining autonomy, reactivity, proactiveness, social ability, bounded rationality, and appropriate multi-agent decomposition.
  - **Agent Roles and Boundaries**: Designing clear responsibilities for planner, executor, worker, critic, verifier, policy checker, manager, or specialist agents without creating unnecessary agent sprawl.
  - **Agent State and Memory**: Managing private and shared state, short-term context, bounded history, summarization, conversation IDs, correlation IDs, and separation of runtime data from policy or prompt definitions.
  - **Structured Communication**: Implementing direct, broadcast, or environment-mediated communication using JSON schemas, typed payloads, sender/receiver metadata, ontology-like fields, and conversation state.
  - **Coordination Patterns**: Applying manager-worker, planner-executor, critic-solver, mediator, announce-bid-award, consensus, or verification-loop patterns where appropriate.
  - **Failure Handling**: Handling timeouts, retries, dead-letter behavior, invalid tool arguments, duplicate work, cascading errors, deadlocks, livelocks, conflicting instructions, and fallback or escalation paths.
  - **Planning and Decision-Making**: Decomposing tasks into subgoals, choosing utility-based or heuristic policies, handling uncertainty, using confidence to trigger verification, and preserving human approval gates for higher-risk actions.
  - **Tool and Infrastructure Integration**: Integrating agents with HTTP services, caches, queues, vector stores, message logs, or sandboxed tools while maintaining clear separation of concerns.
  - **Evaluation and Observability**: Producing logs of messages, decisions, tool calls, assignments, and errors; measuring success rate, latency, cost, communication overhead, error rate, and workflow quality.
  - **Reliability and Safety**: Applying allow/deny boundaries, policy/checker agents, structured rejection messages, audit trails, budget/rate constraints, and safe escalation when agents are uncertain or disagree.
  - **Scalability and Optimization**: Reducing redundant tool calls, batching or caching read-only results, bounded concurrency, avoiding combinatorial message explosion, and identifying bottlenecks in orchestrators, shared tools, or infrastructure.
  - **Documentation and Trade-offs**: Communicating architecture diagrams, interface contracts, message formats, runbooks, trade-offs, limitations, and operational checks.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Python agent application best practices and current development standards.
- The starter task may use simple custom agents, a lightweight FastAPI service, pytest-based replay tests, and local infrastructure. Do not force a heavy agent framework unless it is genuinely helpful for the selected scenario.
- Tasks should require candidates to make architectural decisions and justify their approach through code structure, tests, logs, and observable behavior.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official Python documentation, FastAPI documentation, Redis documentation, Qdrant documentation, Multi-Agent Systems references, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate Multi-Agent Systems proficiency while requiring genuine engineering, reasoning, debugging, and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution for the given agent workflow, constraints, and failure modes.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Multi-Agent Systems task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years applied agent systems or backend AI workflow experience), keeping in mind that AI assistance is allowed.
- Tests practical Multi-Agent Systems skills that require architectural thinking, reliability considerations, structured communication, state management, and workflow evaluation.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on one realistic agent workflow such as an edtech tutor recommendation loop, healthcare intake triage workflow, logistics dispatch quote workflow, marketplace allocation workflow, customer support escalation workflow, or another scenario explicitly provided in the real-world scenarios.
- The task MUST include local infrastructure services that the selected scenario actually exercises. For example, if the selected scenario involves repeated tool lookups, use Redis and/or Qdrant only if the scenario calls for them; if it involves structured message audit logs, use an appropriate local database only if required by the scenario; if it involves asynchronous agent messages, use the broker or queue only if the scenario calls for it.
- Do not invent unrelated infrastructure services. The infrastructure should support the Multi-Agent Systems behavior under assessment, not distract from it.
- The generated project should usually be a Python project with a runtime-native manifest such as pyproject.toml, a small app package, tests or replay scripts, and local infrastructure scripts.
- The code files generated must be valid and executable from /root/task with the local infrastructure started via docker compose.
- Provide a realistic project structure with agent classes, tool adapters, message models, orchestration logic, logging or metrics utilities, and tests/replay scripts.
- A part of the task completion is to watch the candidate implement Multi-Agent Systems best practices, design the solution correctly, demonstrate proper communication, coordination, validation, observability, and safety decisions.
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues, not syntactic errors, that require intermediate-level thinking to resolve.
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper agent architecture and coordination patterns.
- Starter code should include realistic partial implementations that require candidates to complete or improve the core agent workflow.
- Include a docker-compose.yml that sets up required infrastructure services for the selected scenario.

## Infrastructure Requirements
- The task is infrastructure-shaped and MUST include docker-compose.yml, run.sh, and kill.sh.
- The docker-compose.yml must define only the external services actually needed by the selected Multi-Agent Systems scenario, such as Redis for short-lived read-through caching, Qdrant for vector search simulation, PostgreSQL or SQLite-compatible external service only when the selected scenario requires a message audit log, or a lightweight broker only when the scenario explicitly requires asynchronous message flow.
- Do not include Docker Compose services that are not used by the generated starter code or verification path.
- Do not require candidates to install system packages or runtime dependencies inside run.sh. The primary runtime and common libraries are pre-installed by the template.
- run.sh and all generated commands must use /root/task as the base directory.
- The infrastructure must be fully local and deterministic enough for the candidate to verify the task quickly.

### Docker-compose Instructions
- Create docker-compose.yml in /root/task.
- docker-compose.yml MUST be sufficient to start the selected scenario's local infrastructure services.
- **MUST NOT include any version specification** in docker-compose.yml.
- **MUST NOT include environment variables or .env file references** unless an official image cannot run without a minimal non-secret setting. Never require secrets.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore or infrastructure service exposed to the host.
- Include health checks for services where practical so run.sh can wait for readiness.
- Use stable official images suitable for the selected services.
- For Redis, expose `127.0.0.1:6379:6379` only when Redis is needed by the selected task.
- For Qdrant, expose `127.0.0.1:6333:6333` only when Qdrant is needed by the selected task.
- For PostgreSQL, expose `127.0.0.1:5432:5432` only when a database is needed by the selected task, and use non-secret local-only defaults inside compose only when required by the image.
- Use named volumes only when persistence is useful for the scenario; otherwise keep services ephemeral and easy to reset.
- Ensure service names are simple and referenced consistently by README-free code configuration and scripts.
- The docker-compose.yml should not start the application container unless the task explicitly needs an app container. Prefer running the Python project directly on the host runtime with infrastructure in Compose.

### Redis/Qdrant/PostgreSQL Configuration Instructions
- Include configuration files or Python settings only for services that the selected scenario actually exercises.
- Provide minimal, local-only connection defaults such as localhost ports in code configuration files when needed for runnable starter code.
- Do not include credentials, secrets, cloud endpoints, API keys, or .env files.
- If using Redis for MAS caching or coordination, seed no data unless the scenario needs deterministic tests.
- If using Qdrant for vector-search simulation, provide a small seed script or fixture only when the scenario needs a repeatable lesson/document/tool search corpus.
- If using PostgreSQL or another database for message logs or audit trails, include a simple initialization file only when required by the scenario and make sure it is listed in code_files.
- Any `init_database.sql` file must be minimal, deterministic, and focused on the task's message logs, audit records, replay cases, or agent workflow state.
- Configuration should support local tests and replay scripts without requiring the candidate to know private infrastructure details.

### Run.sh Instructions
- Create run.sh in /root/task.
- run.sh must be executable and start from /root/task.
- run.sh must start local infrastructure with `docker compose up -d`.
- run.sh must wait for required services to become reachable before running the project health check, seed script, or test collection.
- run.sh must not run `apt-get install`, `pip install`, `npm install`, or install common runtime libraries. The runtime and common libraries are pre-installed by the template.
- If the generated project ships a test suite with intentionally failing tests that the candidate must make pass, run.sh is a DEPLOYABILITY probe, NOT a pass/fail gate.
- For pytest-based projects, run.sh must capture the pytest exit code and exit 0 when tests were collected and executed even if some tests fail. Specifically, pytest exit codes 0 and 1 should make run.sh exit 0, while exit codes 2, 3, 4, or 5 should make run.sh exit non-zero.
- A valid pytest deployability pattern is:
  `python -m pytest -q; rc=$?`
  `if [ "$rc" -le 1 ]; then exit 0; else exit "$rc"; fi`
- If using another runner, apply the same principle: a designed assertion failure is acceptable for deployability, but import errors, missing dependencies, configuration errors, interrupted runs, usage errors, or no tests collected are not acceptable.
- Print clear logs for each step: changing directory, starting compose services, waiting for service readiness, running seed scripts if present, running tests or health checks, and final deployability status.
- The script must be idempotent and safe to rerun.

## kill.sh file instructions
1. Create kill.sh in /root/task and make it executable.
2. The script must print logs at every step so cleanup progress is visible.
3. The script must stop all docker compose services for the task using `docker compose down --remove-orphans || true`.
4. The script must remove task-specific named volumes using `docker volume rm <volume_name> || true` for every named volume declared in docker-compose.yml.
5. The script must remove task-specific docker networks using `docker network rm <network_name> || true` when custom networks are declared.
6. The script must force-remove images used only by this task when appropriate using `docker rmi -f <image_name> || true`; do not remove broad unrelated images unless they are clearly task-specific.
7. The script must run `docker system prune -a --volumes -f || true` to clean dangling containers, images, networks, and volumes.
8. The script must remove the task directory with `rm -rf /root/task || true`.
9. The script must be idempotent by using `|| true` for cleanup commands that may fail when resources are already absent, and it must print the final message `Cleanup completed successfully!`.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pyproject.toml (Python project metadata, dependencies already available in the environment, pytest configuration if needed)
  - .gitignore (Standard Python, IDE, pytest, cache, logs, and local artifact exclusions)
  - docker-compose.yml (Infrastructure services required by the selected Multi-Agent Systems scenario)
  - run.sh (Starts infrastructure and verifies deployability from /root/task)
  - kill.sh (Stops infrastructure and removes task artifacts according to the cleanup instructions)
  - init_database.sql (Only if the selected scenario requires a database-backed message log, replay table, audit trail, or workflow state store)
  - app/__init__.py (Python package marker)
  - app/main.py (Optional FastAPI or CLI entrypoint if the scenario needs an API or runnable workflow)
  - app/agents/*.py (Agent role implementations or partial implementations)
  - app/orchestrator.py (Starter orchestration flow that the candidate must improve or complete)
  - app/messages.py (Structured message models, schemas, or validation boundaries)
  - app/tools/*.py (Tool adapters such as catalog search, scheduling, quote services, vector search, or cache-backed read-only services)
  - app/memory.py (Short-term or shared memory abstractions when required by the scenario)
  - app/observability.py (Logging, metrics, correlation ID, or trace helper starter code)
  - app/config.py (Local-only configuration for infrastructure endpoints used by the selected scenario)
  - scripts/seed_*.py (Optional deterministic seed scripts for vector stores, databases, replay data, or fixtures)
  - tests/*.py (Pytest tests or replay tests that expose the MAS behavior the candidate must fix or complete)
  - Any additional code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial Multi-Agent Systems architecture that candidate needs to complete, refactor, or debug.
  - Include realistic folder structure such as app/agents, app/tools, app/messages, app/tests or tests/.

## Code file requirements
- Generate realistic Python project structure under /root/task with app/, tests/, scripts/, pyproject.toml, README.md, .gitignore, docker-compose.yml, run.sh, and kill.sh.
- Code should follow modern Python best practices and demonstrate intermediate-level Multi-Agent Systems patterns.
- Use type hints, dataclasses or pydantic-style models where appropriate, structured logging, clear module boundaries, and simple dependency injection through constructors or configuration objects.
- The generated code files must provide partial implementations that require Multi-Agent Systems architectural completion.
- Include some existing agent classes, tool adapters, orchestrator methods, message models, replay tests, and observability helpers that need to be extended, fixed, or integrated.
- The core architectural decisions, communication validation, coordination pattern, caching strategy, verification loop, concurrency boundary, policy check, memory management, or failure handling that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- DO NOT include comments like "Add validation here", "Implement retry logic here", "Use Redis cache here", "Run agents concurrently here", or "Create a policy checker here".
- DO NOT add comments that give away hints, solution, or implementation details.
- The generated project structure should be runnable, importable, and testable, but will require Multi-Agent Systems completion to satisfy the task objectives.
- Starter code should have logical gaps, incomplete behavior, or realistic coordination flaws, but no syntax errors.
- If the task uses FastAPI, provide a minimal endpoint only when useful for the selected scenario; otherwise a CLI or pytest replay shape is acceptable.
- If the task uses Redis, Qdrant, PostgreSQL, or another infrastructure service, include only the minimal code configuration necessary to connect locally and verify behavior.
- Tests should be meaningful and scenario-based. They may initially fail because the candidate needs to complete the behavior, but they must collect and execute.
- Tests should verify observable MAS outcomes such as message validation, no invalid tool calls, reduced redundant calls, preserved response shape, bounded concurrency, structured rejection messages, correlation IDs in logs, dead-letter behavior, or correct escalation on uncertainty.
- Do not include real LLM API calls, real API keys, cloud vector stores, or paid external services. Simulate LLM output or tool responses with deterministic fixtures when needed.
- Do not require advanced MARL frameworks or heavyweight orchestration platforms unless the selected scenario explicitly requires conceptual comparison rather than implementation.
- If diagrams are included in README.md or question text, they must be written in mermaid format, properly indented and also in code blocks.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Python Multi-Agent Systems projects including __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, .ruff_cache/, .coverage, htmlcov/, .venv/, venv/, env/, build/, dist/, *.egg-info/, IDE configurations (.idea/, .vscode/), logs, local databases, temporary replay artifacts, Docker volumes, generated trace files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content.
Task Overview section MUST contain the exact business scenario from the task description.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific Multi-Agent Systems task scenario being generated.
Use concrete business context, not generic descriptions.
Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations.
Do NOT specify exact implementation approaches, specific APIs, class names, method signatures, package structure decisions, or configuration properties that reveal the solution.
The README must NOT contain `<DROPLET_IP>` placeholders or any database-connection details such as host, port, username, password, client-tool suggestions, or credential-like values.

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why Multi-Agent Systems architectural considerations matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper agent coordination, communication, safety, or observability is crucial.
No bullet list.
NO bold time-budget callouts.

### Helpful Tips
Provide practical guidance without revealing specific implementations.
Use 4-5 bullets max.
Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
Frame suggestions around principles and outcomes rather than specific implementations.
Examples of proper framing:
  - "Consider how agents should communicate when a tool response is incomplete or invalid."
  - "Think about what information should be recorded so a failed episode can be replayed and understood."
  - "Explore how independent agent work can be coordinated without changing the final response contract."
  - "Review how uncertainty or disagreement should affect escalation and verification."
  - "Analyze whether repeated work is caused by agent boundaries, shared state, or missing coordination."

### Objectives
Use 4-6 bullets max.
Frame objectives around outcomes rather than specific technical implementations.
Objectives describe the "what" and "why", never the "how".
Each bullet states an observable end-state, not a step or an API/library to use.
Clear, measurable goals for the candidate appropriate for intermediate Multi-Agent Systems level.
Objectives should guide candidates to think about agent communication, coordination, validation, state, reliability, safety, performance, observability, or evaluation without prescribing exact implementation choices.
Examples of proper framing:
  - "Ensure the agent workflow produces valid structured messages before any high-impact tool action occurs."
  - "Reduce redundant read-only tool work while preserving the returned domain results."
  - "Maintain the existing response contract while improving coordination across independent agents."
  - "Record enough message and decision context to diagnose failed or rejected workflow episodes."
  - "Handle invalid, unavailable, or uncertain agent outputs without cascading failures."
  - "Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability."

### How to Verify
Use 4-6 bullets max.
Frame verification in terms of observable outcomes.
Describe WHAT to verify and the expected behavior, not the specific implementation to write.
Each bullet is a check the candidate can run or observe, such as test output, response shape, latency observation, log line, replay result, cache behavior, or memory reading.
These points will help the candidate verify their own work, and the recording of them performing these checks will help the assessor evaluate thoroughness.
Examples of proper framing:
  - "Run the provided replay or test suite and confirm the failing scenario now reaches the expected outcome."
  - "Verify that invalid agent messages are rejected with enough context to understand the reason."
  - "Confirm that repeated requests do not trigger unnecessary duplicate read-only tool work."
  - "Check that the workflow preserves the existing response shape for successful and failure cases."
  - "Inspect logs or metrics to confirm conversation IDs and agent decisions can be followed across the episode."
  - "Validate that infrastructure-backed behavior remains stable after services are restarted."

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Make sure you do not include the following in the README.md file:
  - Setup commands such as `npm install`, `pip install`, `docker compose up`, `pytest`, `python -m pytest`, `mvn test`, or similar commands
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
  - Code snippets that give away the answer
  - Specific class implementation details that would give away the solution to the task
  - Specific agent framework calls, message broker configuration, cache configuration, vector-store calls, or validation method names that would dictate the implementation
  - Producer, consumer, tool, service, or orchestrator method signatures that would reveal the solution
  - Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", "add validation here", or "call this method"
  - Package structure decisions that would dictate the architectural approach
  - Any database-connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "A short kebab-case GitHub repository name under 50 characters that describes the Multi-Agent Systems task without using spaces or title case.",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters, clearly describing what the candidate will do in plain English and different from the kebab-case name.",
  "question": "A detailed candidate-facing description of the selected real-world scenario, the current multi-agent workflow state, the specific problem to solve, the expected deliverables, the infrastructure involved, and the constraints the candidate must respect without revealing the solution.",
  "code_files": {{
    "README.md": "Candidate-facing README with exactly Task Overview, Helpful Tips, Objectives, and How to Verify sections, fully populated and concise according to the README instructions.",
    ".gitignore": "Comprehensive Python, IDE, pytest, cache, log, local artifact, and Docker-related exclusions for the generated project.",
    "pyproject.toml": "Python project manifest with project metadata and pytest configuration or tooling configuration needed for the starter project to run in the pre-installed runtime environment.",
    "docker-compose.yml": "Docker Compose configuration for only the local infrastructure services required by the selected Multi-Agent Systems scenario, with localhost-only port bindings and no Compose version field.",
    "run.sh": "Executable deployability script that starts Docker Compose services from /root/task, waits for readiness, runs the appropriate health check or test collection, and treats designed test failures as deployable when the test runner executed.",
    "kill.sh": "Executable cleanup script that stops Compose services, removes task-specific volumes and networks, prunes Docker resources, removes /root/task, uses idempotent cleanup commands, and prints cleanup logs.",
    "init_database.sql": "Optional database initialization SQL for message logs, audit trails, replay cases, or workflow state only when the selected scenario requires a database service.",
    "app/__init__.py": "Python package marker for the starter Multi-Agent Systems application.",
    "app/main.py": "Application entrypoint or lightweight API/CLI wrapper for exercising the generated agent workflow when the scenario requires one.",
    "app/config.py": "Local-only configuration module for infrastructure endpoints and runtime settings used by the starter project without secrets or .env references.",
    "app/messages.py": "Structured message, event, or tool-call schema definitions that establish the communication contract between agents without completing the core solution.",
    "app/orchestrator.py": "Starter orchestration flow coordinating the scenario's agents, containing the incomplete or flawed behavior the candidate must improve.",
    "app/agents/planner.py": "Starter planner, manager, triage, tutor, dispatch, or equivalent role agent code appropriate to the selected scenario.",
    "app/agents/worker.py": "Starter worker, specialist, critic, verifier, schedule, capacity, ETA, catalog, or equivalent agent code appropriate to the selected scenario.",
    "app/tools/service_adapter.py": "Tool or external-service adapter starter code such as catalog search, scheduling, quote services, vector search, cache-backed lookup, or audit logging as required by the scenario.",
    "app/observability.py": "Logging, metrics, tracing, correlation ID, or replay instrumentation helper code that supports diagnosing the agent workflow.",
    "scripts/seed_data.py": "Optional deterministic seed script for vector-store collections, message-log tables, replay fixtures, or other local infrastructure data required by the selected scenario.",
    "tests/test_agent_workflow.py": "Pytest-based scenario or replay tests that collect and execute against the starter project and expose the behavior the candidate must fix or complete.",
    "additional_file_name": "Any additional starter source, fixture, script, or test file needed to make the task realistic while still withholding the solution."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended Multi-Agent Systems improvements, major design choices, communication flow, infrastructure use, validation or coordination strategy, and verification expectations without needing full code.",
  "definitions": "Object mapping important Multi-Agent Systems terms used in the task to concise definitions, such as agent, orchestrator, tool call, structured message, conversation ID, memory, critic, verifier, dead-letter handling, idempotency, observability, or bounded concurrency.",
  "hints": "A single line hint nudging the candidate toward a good intermediate-level investigation or design direction without revealing the specific implementation, API, pattern, or code change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable workflow correctness, reliability, latency, validation, observability, or infrastructure-backed behavior, using simple English.",
  "pre_requisites": "Bullet-point list of tools, runtime knowledge, and conceptual background needed, including Python, pytest, Docker Compose, local infrastructure relevant to the selected scenario, structured agent communication, orchestration, logging, and intermediate Multi-Agent Systems fundamentals.",
  "short_overview": "Bullet-point list summarising the business problem, the Multi-Agent Systems technical focus, and the expected candidate outcome in simple English."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, human-readable, and different from `name`.
4. **code_files** must include README.md, .gitignore, pyproject.toml, docker-compose.yml, run.sh, kill.sh, and relevant Python source and test files.
5. Because this is an infrastructure-shaped task, docker-compose.yml, run.sh, and kill.sh are mandatory.
6. docker-compose.yml must include only the infrastructure services required by the selected scenario and **MUST NOT include any version specification**.
7. docker-compose.yml **MUST NOT include environment variables or .env file references** unless a local official image cannot start without minimal non-secret defaults.
8. **SECURITY-CRITICAL**: every exposed infrastructure port must be bound to localhost only using `127.0.0.1:<port>:<port>`.
9. run.sh must use /root/task, start infrastructure with `docker compose up -d`, and follow the deployability contract for failing-as-designed tests.
10. kill.sh must follow the 9-step cleanup shape, use `|| true` for idempotency, run `docker system prune -a --volumes -f || true`, remove `/root/task`, and print `Cleanup completed successfully!`.
11. README.md must contain exactly Task Overview, Helpful Tips, Objectives, and How to Verify in that order, with no extra README sections.
12. README.md must exclude setup commands, direct solutions, step-by-step implementation instructions, specific APIs, method names, library names, code snippets, and database connection details.
13. Starter code must be runnable and test-collectable, but must NOT contain the solution.
14. Do not include comments in code that reveal hints or solution direction.
15. The task must be completable within {minutes_range} minutes for INTERMEDIATE proficiency.
16. The task must assess applied Multi-Agent Systems competence, not trivia, pure syntax, framework installation, or memorized protocol names.
17. The task should include realistic logs, tests, replay data, metrics, or observable outputs so the candidate can demonstrate debugging and verification.
18. If diagrams are included, ensure they are written in mermaid format, properly indented and also in code blocks.
"""

PROMPT_REGISTRY = {
    "Multi-Agent Systems (INTERMEDIATE)": [
        PROMPT_MULTI_AGENT_SYSTEMS_CONTEXT_INTERMEDIATE,
        PROMPT_MULTI_AGENT_SYSTEMS_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_MULTI_AGENT_SYSTEMS_INTERMEDIATE_INSTRUCTIONS,
    ],
}