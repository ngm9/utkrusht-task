PROMPT_PYTHON_REDIS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, particularly in relation to using Python and Redis together for high-throughput backend services, caching, queueing, stream processing, concurrency, and production reliability?
"""

PROMPT_PYTHON_REDIS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Redis assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python and Redis implementation, debugging, optimization, or architecture fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_REDIS_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python and Redis, you are given a list of real world scenarios and proficiency levels for Python and Redis.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional Python backend application with Redis integration but either with logical bugs, concurrency flaws, atomicity gaps, stream-processing issues, poor key design, memory inefficiencies, or performance and reliability problems that require advanced-level Python and Redis engineering skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python backend application that is already connected to Redis with existing implementation and realistic data. The application includes:
- Complete API endpoints and/or worker flows with business logic implemented but with intentionally flawed Redis usage and Python-side coordination requiring advanced-level analysis
- Full Redis connection and configuration setup
- All necessary middleware, error handling, response formatting, and startup wiring
- Complete data models and API schemas
- Pre-configured Redis with realistic sample data and intentionally problematic patterns such as hot keys, poor key naming, weak TTL strategy, non-atomic read-modify-write flows, inefficient serialization, missing batching, stream consumer issues, ordering/idempotency gaps, or concurrency bottlenecks that demand advanced problem-solving
- A codebase that is runnable end to end, but whose correctness, latency, throughput, or operational behavior degrades under realistic usage patterns

The candidate's responsibility is to identify and fix the Python and Redis issues according to the task requirements and then make any code changes in the app to support the fixes. A part of the task completion is to watch the candidate implement Redis and Python best practices and improve correctness, performance, and maintainability at an advanced level (typically 5+ years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, descriptive, and under 50 characters in kebab-case
- Task title MUST be human-readable, in "<action verb> <subject>" format, and different from the kebab-case name
- Task must provide a working Python backend application with existing Redis-backed behavior and intentionally flawed implementation requiring advanced-level debugging, optimization, and design judgment
- **CRITICAL**: The application should be FULLY FUNCTIONAL but exhibit realistic production-grade issues involving BOTH Python application behavior and Redis usage
- **CRITICAL**: The exact problem described in the task scenario MUST be perfectly replicated in the code files. For example, if the scenario mentions "duplicate processing caused by non-atomic claim logic on a Redis-backed work queue", the actual code MUST contain that exact issue. If it mentions "latency spikes caused by hot-key access and repeated round trips", the code MUST have those exact behaviors implemented. The candidate should ONLY need to analyze and improve the existing system, NOT build the whole system from scratch.
- **CRITICAL**: Candidates must understand that fixing the Redis issue will usually require corresponding changes in the Python application code. The task should make it clear that after improving Redis-side behavior such as key design, TTL lifecycle, batching, stream handling, atomicity, or data structure choice, they must also update the Python endpoints, worker logic, concurrency flow, retry behavior, or serialization logic to properly utilize these improvements and maintain functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate a complete, working Python backend application with Redis integration that has correctness, performance, or reliability issues according to the task requirements suitable for advanced engineers.
- **PROVIDE PROBLEMATIC REDIS AND PYTHON IMPLEMENTATION**: Include code with issues such as:
  - Poor key naming patterns, namespace collisions, or missing versioning
  - Missing, inconsistent, or harmful TTL behavior
  - Hot-key amplification or repeated network round trips
  - Wrong Redis data structure choice for the access pattern
  - Missing pipelining or batching for bulk operations
  - Non-atomic read-modify-write flows causing race conditions
  - Stream consumer-group logic with duplicate processing, ordering gaps, or weak retry handling
  - Inefficient serialization or oversized payload handling
  - Improper connection pooling or client lifecycle management
  - Python concurrency issues involving async tasks, blocking calls, or worker coordination
  - Weak cache invalidation or stale-read behavior
  - Reliability gaps around retries, idempotency, or failure handling
- The question should be a real-world business scenario requiring advanced Python and Redis engineering involving multiple endpoints or worker flows, realistic load-sensitive behavior, and non-trivial trade-off analysis, NOT building from scratch.
- The complexity of the optimization task and specific improvements expected from the candidate must align with ADVANCED proficiency level, requiring strong judgment across:
  - Python concurrency, async I/O, profiling, debugging, and maintainable architecture
  - Redis data modeling, key lifecycle strategy, memory-aware design, and performance engineering
  - Atomic workflows using transactions, optimistic concurrency, or Lua/function-style server-side logic where appropriate
  - Queueing or stream-processing correctness including idempotency, ordering, and retry behavior
  - Client resiliency, connection management, and observability-minded debugging
  - Security-conscious and production-minded implementation choices
- For ADVANCED level proficiency, the task should be more open ended, require application of fundamental concepts, and be complex according to proficiency while still being realistically completable within {minutes_range} minutes.
- The question must NOT include hints about the specific fix. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to current Python 3 and Redis best practices and versions.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, Redis documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and improve realistic Python and Redis systems, rather than testing rote memorization.
- The complexity of the optimization tasks should require genuine advanced-level engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates will be encouraged to use AI to help with boilerplate code and other bugs but not replace their own thinking, trade-off analysis, and debugging skills.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Python and Redis task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- **CRITICAL**: The scenario description MUST be perfectly replicated in the actual code files. Every bug, race condition, stale-read path, latency issue, duplicate-processing path, or memory inefficiency mentioned in the scenario MUST exist in the generated code exactly as described.
- Matches the complexity level appropriate for advanced proficiency, keeping in mind that AI assistance is allowed but should not diminish the need for advanced Python and Redis engineering skills.
- Tests practical advanced-level Python and Redis skills that require deep understanding of concurrency, data modeling, atomicity, performance, and reliability.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The Python application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, worker flows, middleware, error handling, and Redis connection setup, but with intentionally flawed implementation requiring advanced analysis and improvement.
- Redis should come with realistic sample data and intentionally poor operational or modeling choices requiring advanced engineering judgment.
- The code files generated must be valid and executable but exhibit the intended correctness, latency, throughput, or reliability issues.
- **CRITICAL**: The task focuses on improving an existing system with realistic flaws, NOT building a greenfield service from scratch.
- Use Python with a backend web framework available in the template. FastAPI is preferred for the primary service shape because it supports realistic async and concurrency scenarios well.
- The task may include an API service plus a lightweight worker process if the selected scenario naturally requires queueing or stream processing.
- Keep the scope focused on one coherent advanced problem area, such as:
  - fixing a Redis-backed idempotent job-claim workflow in a Python service
  - improving a Redis Streams consumer-group implementation with duplicate processing and retry issues
  - correcting a cache-aside implementation with stale data, hot keys, and poor batching
  - refactoring a Python async service whose Redis access pattern causes latency spikes and inconsistent behavior
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## Infrastructure Requirements
- MUST include a complete, fully functional Python backend application structure using FastAPI or another suitable Python backend framework available in the template
- MUST include Redis as the only external service unless the selected scenario explicitly requires another external service, which should generally be avoided for this competency combination
- MUST include a Dockerfile for the Python application container
- MUST include a run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc.
- MUST include a docker-compose.yml file which contains all the applications needed for the task — at minimum a docker for running the Python backend application and a docker for running Redis
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working application and Redis connection.
- The infrastructure should support realistic debugging and verification of the intended issue without requiring any external cloud services
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

### Docker-compose Instructions
- Include a Python application service and a Redis service
- Redis service should use a stable official Redis image
- **SECURITY-CRITICAL**: Redis ports MUST be bound to localhost only using `127.0.0.1:6379:6379`
- **SECURITY-CRITICAL**: Application ports exposed to the host MUST also be bound to localhost only using `127.0.0.1:<port>:<port>`
- Use depends_on where appropriate for service ordering
- Include volume mounts only if they are necessary for persistence or local task files
- Network configuration should be simple and sufficient for service communication
- **MUST NOT include any version specification** in the docker-compose.yml file
- **MUST NOT include environment variables or .env file references**
- Use hardcoded configuration values instead of environment variables
- The Python service should start the application with the intentionally flawed Redis-backed behavior already active
- If a worker process is included, it may be a second Python service in the same project using the same Dockerfile or command override
- **CRITICAL**: Docker-compose handles container orchestration and service communication

### Redis Configuration Instructions
- Redis should be configured in a way that supports the selected scenario while remaining simple enough for a task environment
- Include realistic sample data in Redis through initialization scripts or application startup seeding
- Create scenarios with flawed key patterns, weak TTL strategy, poor data structure usage, duplicate-processing risk, or inefficient access patterns
- If the scenario involves streams or queueing, seed the relevant stream/group state in a way that reproduces the intended issue
- Do not require cluster, sentinel, TLS, or cloud-managed Redis setup in the task infrastructure itself; advanced reasoning about those topics may appear in the scenario or answer, but the runnable task should stay locally executable

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d --build`
- WAIT MECHANISM: Implements proper health checks or polling to wait for Redis service to be fully ready and for the Python application to be responding
- VALIDATION: Validates that the application is responding and connected to Redis
- DATA INITIALIZATION: May include initial Redis data population or verification if not already handled by application startup
- MONITORING: Monitors container status and provides feedback on successful deployment
- ERROR HANDLING: Includes proper error handling for failed container starts or Redis connection issues
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- The script should be production-minded, readable, and idempotent enough for repeated task setup in a disposable environment

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes (Redis volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task.
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."
- Commands that should be included:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q || true) || true`
  - `rm -rf /root/task`
- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`
  - Remove all Redis data directories that were mounted via volumes if present
  - Ensure that both the custom application container and the Redis container are cleaned up
- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the Python application
- Should use an appropriate modern Python base image such as python:3.11-slim
- Should install dependencies from requirements.txt
- Should expose the application port used by the service
- Should include proper working directory set to /root/task
- Should include a proper entry point or command
- Must be production-ready enough for a task environment and follow Docker best practices
- **DO NOT use environment variables or .env files**
- **CRITICAL**: Set WORKDIR to /root/task to match the file location

The output should be a valid json schema:
- README.md (CRITICAL - Follow exact structure specified below)
- requirements.txt (Python dependencies including fastapi, redis, uvicorn, pytest, and any other dependencies required by the scenario)
- docker-compose.yml (Redis and Python services configuration)
- Dockerfile (MUST be included - Docker configuration for the Python application)
- run.sh (Script to deploy and setup the complete environment)
- kill.sh (Complete cleanup script to remove all resources created by the task)
- .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, local data artifacts, Redis persistence files)
- All Python code files following the project structure with intentionally flawed Redis-backed behavior
- Tests or verification scripts if they help make the task measurable
- **CRITICAL**: Include ALL __init__.py files for proper Python package structure

## Code file requirements
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP 8 guidelines and include realistic Redis and Python anti-patterns requiring advanced optimization or correctness fixes
- **CRITICAL**: The Python application files MUST be complete and fully functional with all endpoints, error handling, and Redis integration code, but with intentionally flawed implementation matching the scenario.
- **CRITICAL**: The exact problems described in the task scenario MUST be present in the code. Do not implement the optimized solution - implement the problematic code exactly as described in the scenario.
- Redis connection setup and Python routes/workers should use flawed patterns that need advanced improvement.
- Tasks should focus on identifying and improving existing correctness, performance, concurrency, or reliability bottlenecks requiring advanced Python and Redis skills.
- **SEPARATION OF CONCERNS**:
  - docker-compose.yml: Handles container orchestration
  - run.sh: Starts containers, implements health checks, and validates deployment
  - Python app: Works but exhibits the intended Redis-backed issues requiring advanced solutions
- DO NOT include any 'TODO' or placeholder comments in Python code
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that give away hints or any direct or indirect solution in the files
- The Python application should be immediately runnable but will behave incorrectly or inefficiently until the candidate applies advanced improvements.
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Python and Redis backend development tasks that includes:
- Python bytecode and cache files
- Virtual environment directories
- Build and distribution artifacts
- IDE and editor files
- Log files
- Redis dump files such as dump.rdb and appendonly.aof
- Test caches and coverage artifacts
- Any other standard exclusions for Python backend and Redis development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

The README.md file content MUST be fully populated with meaningful, specific content relevant to the advanced Python and Redis scenario being generated.
Task Overview section MUST contain the exact business scenario and current system behavior that needs improvement.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific task scenario being generated.
Use concrete business context explaining why the Python and Redis behavior matters for the business, not generic descriptions.

### Task Overview
- **CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state of the system, and why the problem matters.
- NEVER generate empty content.
- Do NOT include bold time-budget callouts.
- Do NOT reveal the exact implementation approach.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Use 4-5 bullets max.
- Each bullet MUST start with an action word: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Frame suggestions around principles, trade-offs, and observable behavior rather than implementation details.
- Good examples of framing:
  - "Consider how correctness can break down when multiple workers or requests act on the same data at the same time."
  - "Think about whether the current data lifecycle matches the freshness and retention needs of the business flow."
  - "Explore where repeated remote calls or oversized payloads may be amplifying latency under load."
  - "Review how failure handling affects duplicate work, stale responses, or partial updates."
  - "Analyze whether the current design makes it easy to reason about consistency and recovery."

### Objectives
- Use 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step or a prescribed library/API choice.
- Objectives should cover both functional correctness and engineering quality where relevant.
- Good examples of framing:
  - "Ensure repeated requests or worker retries do not produce duplicate business effects."
  - "Improve the system so that high-traffic operations remain responsive under realistic concurrent usage."
  - "Preserve expected business behavior while reducing stale or inconsistent results."
  - "Make the service easier to reason about and safer to operate when failures occur."

### How to Verify
- Use 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as response behavior, duplicate-processing absence, latency improvement, log behavior, or state consistency.
- Good examples of framing:
  - "Verify that repeated submissions or retries no longer create duplicate downstream effects."
  - "Confirm that concurrent access produces stable, consistent results instead of intermittent failures or drift."
  - "Check that the most frequently used flow responds noticeably faster or with fewer visible delays than before."
  - "Validate that state transitions remain correct after restarts or transient failures."

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Database or Redis connection details such as host, port, username, password, container names, or client-tool suggestions
- Placeholder deployment values such as `<DROPLET_IP>`

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "Kebab-case GitHub repository name under 50 characters that is short, descriptive, and appropriate for the task.",
  "title": "Human-readable display title in '<action verb> <subject>' format, between 50 and 80 characters, clearly describing the candidate-facing task and different from the kebab-case name.",
  "question": "Full candidate-facing task description explaining the business scenario, the current system behavior, the expected outcomes, and the boundaries of what the candidate should improve without revealing the exact solution.",
  "code_files": {{
    "README.md": "Candidate-facing README that follows the exact required section names and order: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.",
    ".gitignore": "Comprehensive ignore file for Python, Redis, Docker, test caches, logs, build artifacts, and local development files relevant to this task.",
    "requirements.txt": "Python dependency list required to run the provided application, tests, and Redis integration for the selected scenario.",
    "docker-compose.yml": "Docker Compose configuration for the Python application service and Redis service, with localhost-only port bindings, no version field, and no environment variables.",
    "Dockerfile": "Dockerfile for the Python application container using a modern Python base image, /root/task as WORKDIR, and a runnable command for the provided service.",
    "run.sh": "Deployment script that starts the task environment, waits for services to become ready, validates application health, and prints useful progress logs.",
    "kill.sh": "Cleanup script that stops containers, removes volumes and networks, prunes Docker resources, deletes /root/task, and remains safe to run multiple times.",
    "app/__init__.py": "Empty file required so the main application package is a valid Python package.",
    "app/main.py": "Primary application entry point that wires routes, startup behavior, and the intentionally flawed Redis-backed business flow.",
    "app/api/__init__.py": "Empty file required so the API package is a valid Python package.",
    "app/api/routes.py": "HTTP route definitions exposing the business workflow or debugging surface relevant to the task scenario.",
    "app/core/__init__.py": "Empty file required so the core package is a valid Python package.",
    "app/core/config.py": "Application configuration module using hardcoded local task values rather than environment variables.",
    "app/redis/__init__.py": "Empty file required so the Redis integration package is a valid Python package.",
    "app/redis/client.py": "Redis client setup and lifecycle management containing the intentionally flawed connection or access behavior relevant to the task.",
    "app/services/__init__.py": "Empty file required so the services package is a valid Python package.",
    "app/services/business_flow.py": "Business logic module where the main correctness, concurrency, caching, queueing, or atomicity issue is implemented.",
    "app/models/__init__.py": "Empty file required so the models package is a valid Python package.",
    "app/models/schemas.py": "Request and response schemas or domain models used by the application.",
    "app/seed.py": "Startup or utility module that seeds Redis with realistic sample data needed to reproduce the scenario.",
    "tests/test_task_behavior.py": "Executable tests or verification checks that demonstrate the current flawed behavior and can be updated to pass after the candidate fixes the task."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended reasoning, trade-offs, and categories of improvements without requiring exact code listings.",
  "definitions": "Object of term-to-definition pairs covering important Python, Redis, concurrency, caching, queueing, consistency, or reliability terminology used in the task.",
  "hints": "A single line nudging investigation toward the right area of the system without revealing the exact fix, implementation choice, or Redis command/API to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable correctness, latency, throughput, consistency, or reliability improvements in simple English.",
  "pre_requisites": "Bullet-point list of tools, runtime knowledge, and practical experience needed to work on the task, such as Python 3.10+, Docker, Docker Compose, Git, HTTP API debugging, and Redis familiarity.",
  "short_overview": "Bullet-point list summarising the business problem, the technical focus of the task, and the expected end result after the candidate improves the system."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no code fences.
2. `"name"` must be short, descriptive, kebab-case, and under 50 characters.
3. `"title"` must be in `<action verb> <subject>` format and different from `"name"`.
4. `"code_files"` must include README.md, .gitignore, requirements.txt, docker-compose.yml, Dockerfile, run.sh, kill.sh, and all required Python source files.
5. README.md MUST follow the exact section names and order specified above.
6. The generated application environment must be FULLY FUNCTIONAL on startup; the candidate fixes the intended engineering problem, not the deployment.
7. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
8. **MUST NOT include any version specification** in docker-compose.yml.
9. **MUST NOT include environment variables or .env file references** anywhere in the task files.
10. Redis and application ports exposed to the host must be bound to localhost only.
11. The exact scenario described in the question MUST be reproduced in the code.
12. Do not include comments in code that reveal the solution or provide hidden hints.
13. Keep the task within the competency scope of advanced Python and advanced Redis, focusing on realistic backend engineering rather than unrelated infrastructure complexity.
14. If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
"""

PROMPT_REGISTRY = {
    "Python (ADVANCED), Redis (ADVANCED)": [
        PROMPT_PYTHON_REDIS_ADVANCED_CONTEXT,
        PROMPT_PYTHON_REDIS_ADVANCED_INPUT_AND_ASK,
        PROMPT_PYTHON_REDIS_ADVANCED_INSTRUCTIONS,
    ]
}