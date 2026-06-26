PROMPT_PYTHON_REDIS_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, 
particularly in relation to using Python services with Redis for caching, rate limiting, distributed coordination, queue-like workflows, or performance-sensitive API behavior?
"""

PROMPT_PYTHON_REDIS_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Redis assessment task.

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
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python and Redis debugging, optimization, or integration work required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_REDIS_OPTIMIZATION_INSTRUCTIONS_INTER = """
## GOAL
As a technical architect super experienced in Python services and Redis integration, you are given a list of real world scenarios and proficiency levels for Python and Redis.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional Python API application with Redis integration but either with logical bugs, suboptimal Redis usage, correctness issues under concurrency, or performance problems that require intermediate-level Python and Redis problem-solving skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python FastAPI application that is already connected to Redis with existing implementation and realistic data. The application includes:
- Complete REST API endpoints with business logic implemented but with intentionally flawed Redis integration patterns requiring intermediate-level debugging and optimization
- Full Redis connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete data models and API schemas
- Pre-configured Redis with realistic data and intentionally inefficient or incorrect usage patterns such as poor key naming, missing or inconsistent TTLs, wrong data-structure choices, redundant round-trips, stale cache behavior, hot-key pressure, or concurrency-sensitive update flows
- Python code that is complete and runnable but requires moderate refactoring, debugging, and performance improvement consistent with 2-5 years of experience

The candidate's responsibility is to identify and fix Redis-related issues according to the task requirements and then make any code changes in the Python application to support the fixes. A part of the task completion is to watch the candidate implement Python and Redis best practices and improve correctness, maintainability, and performance at an intermediate level (2-5 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Python and Redis scenario
- Task must provide a working application with existing Redis integration and intentionally flawed implementation patterns requiring intermediate-level Python and Redis skills
- **CRITICAL**: The Python application should be FULLY functional but performing poorly, behaving inconsistently, or becoming unreliable under realistic usage because of inefficient or incorrect Redis usage that requires thoughtful analysis and moderate refactoring
- **CRITICAL**: The exact problem described in the task scenario MUST be perfectly replicated in the code files. For example, if the scenario mentions "stale counters caused by inconsistent key naming and missing expiry", the actual code MUST contain those exact issues. If it mentions "slow bulk reads due to repeated round-trips instead of batched access", the code MUST have that exact issue implemented. The candidate should ONLY need to debug, optimize, and improve the existing code, NOT build the system from scratch.
- **CRITICAL**: Candidates must understand that fixing Redis issues requires corresponding changes in the Python application code. The task should make it clear that after improving Redis usage patterns, they must also update the API endpoints, service logic, serialization behavior, and error handling so the application remains correct and fully functional.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate a complete, working Python FastAPI application with Redis integration that has realistic issues according to the task requirements suitable for intermediate-level engineers (2-5 years experience).
- **PROVIDE PROBLEMATIC REDIS INTEGRATION**: Include code with issues such as:
  - Poor key naming patterns and inconsistent namespaces
  - Missing, incorrect, or uneven TTL strategies
  - Inefficient data-structure usage such as storing complex mutable state in awkward forms
  - Repeated Redis round-trips for bulk operations where batching would be more appropriate
  - Cache invalidation gaps causing stale reads after writes
  - Serialization inefficiencies or inconsistent payload formats
  - Connection handling or pooling choices that create unnecessary latency or instability
  - Concurrency-sensitive update flows that can produce incorrect counters, duplicate work, or race conditions
  - Rate-limiting, queue-like, or coordination logic that works functionally but behaves poorly under moderate load
- The question should be a real-world business scenario requiring intermediate-level Python and Redis debugging and optimization involving multiple endpoints, realistic service logic, and moderate tradeoff analysis, NOT building from scratch.
- The complexity of the task and specific improvements expected from the candidate must align with intermediate proficiency level (2-5 years experience) requiring practical skills including:
  - Python refactoring for modularity, readability, and maintainability
  - Robust exception handling and graceful failure behavior
  - Appropriate Redis key-space design and TTL strategy
  - Proper Redis data-structure selection based on access patterns
  - Batched operations using pipelining or equivalent round-trip reduction where appropriate
  - Correctness under concurrent access for moderate-complexity workflows
  - Cache consistency reasoning across reads and writes
  - Basic observability and debugging using logs, timings, or simple diagnostics already present in the codebase
  - Performance improvement without over-engineering the solution
- **CRITICAL**: Keep the task within the competency scope. Do NOT make Sentinel, Cluster resharding, persistence tuning, ACL administration, TLS setup, or zero-data-loss migration the primary work. The task should focus on application-level Redis integration and Python service improvement.
- The question must NOT include hints about the specific fixes needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest Python and Redis best practices for intermediate-level application development and optimization.
- The task should be realistically completable within {minutes_range} minutes.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, Redis documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and improve Python and Redis integration issues at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the task should require genuine intermediate-level engineering judgment and practical debugging skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve multi-layered but bounded challenges that require understanding of Python application structure, Redis usage patterns, correctness tradeoffs, and performance implications
- Candidates will be encouraged to use AI to help with boilerplate code and other bugs but not replace their own thinking and analysis skills

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Python and Redis optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- **CRITICAL**: The scenario description MUST be perfectly replicated in the actual code files. Every bug, stale-data issue, latency problem, or incorrect Redis usage mentioned in the scenario MUST exist in the generated code exactly as described.
- Matches the complexity level appropriate for intermediate proficiency level (2-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for practical Python and Redis reasoning
- Tests practical intermediate-level Python and Redis integration skills that require understanding of application structure, data flow, caching behavior, and moderate concurrency concerns
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- **CRITICAL**: The Python application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and Redis connection setup, but with intentionally flawed Redis integration patterns requiring intermediate-level improvement
- The Redis connection setup should be valid and working but may contain suboptimal client usage patterns that require improvement
- All FastAPI routes should be implemented and working but with Redis-related correctness or performance issues that need intermediate-level debugging and optimization
- Redis should come with realistic sample data and intentionally poor usage patterns requiring practical improvement
- The code files generated must be valid and executable but perform poorly or behave incorrectly due to Redis integration issues requiring intermediate-level solutions
- **CRITICAL**: The task focuses on improving an existing Python service that uses Redis incorrectly or inefficiently, NOT building a new service from scratch
- For INTERMEDIATE level proficiency: Use Python with FastAPI and redis-py style integration patterns, but implement flawed application-level Redis usage that requires intermediate-level debugging, refactoring, and optimization skills

## Infrastructure Requirements
- MUST include a complete, fully functional REST API structure using Python FastAPI that integrates with Redis
- MUST include a Dockerfile for the Python application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Python API and a docker for running Redis
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and Redis connection.

### Docker-compose Instructions
  - Redis service with appropriate basic configuration for the scenario
  - **SECURITY-CRITICAL**: Redis ports MUST be bound to localhost only using `127.0.0.1:6379:6379` — NEVER use `6379:6379`
  - API service with dependency on Redis using depends_on
  - Expose the API port on localhost only as well when exposed to the host
  - Volume mounts for Redis data persistence only if the scenario genuinely benefits from it
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - API service should start the application with intentionally flawed Redis integration requiring intermediate optimization
  - **CRITICAL**: Docker-compose handles container orchestration and service communication

### Redis Configuration Instructions
- Redis should be configured simply and appropriately for an application-integration task
- Include realistic sample data in Redis through initialization scripts or application startup if needed
- Create scenarios with poor key patterns, missing TTLs, inefficient data structures, stale invalidation behavior, or excessive round-trips
- If the task includes concurrency-sensitive behavior, ensure the code reproduces it through the application logic rather than requiring advanced Redis infrastructure administration
- Do NOT make Sentinel, Cluster, ACL administration, persistence tuning, or failover orchestration the main task

### Run.sh Instructions
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  + WAIT MECHANISM: Implements proper health checks to wait for Redis service to be fully ready and accepting connections and for the API to become responsive
  + VALIDATION: Validates that the Python application is responding and connected to Redis
  + DATA INITIALIZATION: May include initial API warm-up or validation requests if needed, but keep setup simple
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling for failed container starts or Redis connection issues
  + **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
  + Use `docker compose`, not `docker-compose`, in run.sh

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes (Redis volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and redis:7-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|redis:7-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all Redis data directories that were mounted via volumes (for example `/root/task/data/redis`) if present.
  - Ensure that both the custom application container and the Redis container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

### Dockerfile Instructions
  - MUST generate a complete, valid Dockerfile for the Python application
  - Should use an appropriate Python base image such as python:3.11-slim
  - Should install dependencies from requirements.txt
  - Should expose the appropriate port for the API
  - Should include proper working directory set to /root/task
  - Should include proper entry point
  - Must be production-ready and follow Docker best practices
  - **DO NOT use environment variables or .env files**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastapi, redis, uvicorn, pytest, and any other dependencies required by the scenario)
  - docker-compose.yml (Redis and Python API services configuration)
  - Dockerfile (MUST be included - Docker configuration for the Python API app)
  - run.sh (Script to deploy and validate the complete environment)
  - kill.sh (Complete cleanup script to remove all resources created by the task)
  - .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, data/, .pytest_cache, .mypy_cache)
  - All Python code files following the project structure with flawed Redis integration patterns
  - **CRITICAL**: Include ALL __init__.py files for proper Python package structure
  - Tests or verification-oriented files may be included if they help make the task measurable without revealing the solution

## Code file requirements
- More than 1 files can be generated but make sure they are included in the JSON structure correctly
- Code should follow Python PEP 8 guidelines and include Redis integration anti-patterns requiring intermediate-level optimization
- **CRITICAL**: The Python application files MUST be complete and fully functional with all endpoints, error handling, and Redis integration code, but with intentionally flawed Redis usage patterns
- **CRITICAL**: The exact problems described in the task scenario MUST be present in the code. Do not implement optimized solutions - implement the problematic code exactly as described in the scenario.
- Redis connection setup and API routes should use suboptimal patterns that need intermediate-level improvement
- Tasks should focus on identifying and improving existing correctness and performance bottlenecks requiring practical Python and Redis skills
- **SEPARATION OF CONCERNS**:
  - docker-compose.yml: Handles container orchestration
  - run.sh: Starts containers, implements health checks, and validates deployment
  - Python app: Should work but perform poorly or incorrectly due to Redis integration issues requiring intermediate-level solutions
- DO NOT include any 'TODO' or placeholder comments in Python code
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that give hints or any direct or indirect solution in the files
- The Python application should be immediately runnable but will perform poorly or behave incorrectly until the candidate applies intermediate-level improvements
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Python, FastAPI, Docker, and Redis development tasks that includes:
- Python bytecode and cache files
- Virtual environment directories
- Build and distribution artifacts
- IDE and editor files
- Log files
- Redis dump files if applicable
- Test and type-checker caches
- Any other standard exclusions for Python/FastAPI/Redis development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections, in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level Python and Redis debugging and optimization challenges.
Task Overview section MUST contain the exact business scenario and the specific correctness, latency, or stale-data problems that need intermediate-level improvement.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific Python and Redis scenario being generated.
Use concrete business context explaining why the current Redis behavior is harming the service, not generic descriptions.
The README must NOT contain database-connection details, host, port, username, password, client-tool suggestions, or placeholder values like <DROPLET_IP>.

### Task Overview
- **CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- Explain that the service is already working but has Redis-related correctness or performance issues affecting the business workflow.
- NEVER generate empty content and do NOT include bold time-budget callouts.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Use 4-5 bullets max.
- Each bullet MUST start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Frame suggestions around principles, tradeoffs, and investigation paths rather than direct fixes.

### Objectives
- Use 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or a library choice.
- Focus on functional correctness, consistency of behavior, maintainability, and measurable performance improvement appropriate for intermediate level.

### How to Verify
- Use 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run, such as response behavior, consistency after repeated requests, latency improvement, reduced duplicate work, or stable behavior under concurrent access.
- Verification should help the candidate confirm both correctness and performance improvements without prescribing the exact fix.

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands (for example `pip install`, `docker compose up`, `pytest`, `uvicorn`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Manual deployment instructions (environment is automated)
- Instructions to run the run.sh file
- Redis connection details or client access instructions

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Kebab-case GitHub repository name under 50 characters describing the task scenario and suitable for use as a folder or repo name.",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 characters, clearly describing the candidate-facing task and different from the kebab-case name.",
  "question": "Full candidate-facing task description explaining the business scenario, the current Python service behavior, the Redis-related correctness or performance problems, the expected scope of investigation, and what the candidate must improve without revealing the exact solution.",
  "code_files": {{
    "README.md": "Candidate-facing README content following the exact required section names and order, written concisely and without revealing the implementation approach.",
    ".gitignore": "Comprehensive Python, FastAPI, Docker, Redis, editor, cache, and local artifact ignore rules appropriate for this project.",
    "requirements.txt": "Python dependency list needed to run the provided application, tests, and Redis integration for this task.",
    "docker-compose.yml": "Compose file defining the Python API service and Redis service with localhost-only port bindings, no version field, and no environment variables.",
    "Dockerfile": "Production-ready Dockerfile for the Python API application using /root/task as the working directory.",
    "run.sh": "Deployment and validation script that starts the stack, waits for readiness, and confirms the API and Redis are working.",
    "kill.sh": "Idempotent cleanup script that removes containers, volumes, networks, images, caches, and the /root/task directory.",
    "app/__init__.py": "Empty file for Python package structure.",
    "app/main.py": "Application entry point wiring the FastAPI app, routes, and startup behavior for the flawed but functional service.",
    "app/api/__init__.py": "Empty file for Python package structure.",
    "app/api/routes.py": "API route implementations exposing the business endpoints that currently suffer from Redis-related issues.",
    "app/services/__init__.py": "Empty file for Python package structure.",
    "app/services/service.py": "Core business logic layer where the main Redis integration bugs, stale-data behavior, or performance issues are implemented.",
    "app/redis_client.py": "Redis client setup and helper functions with working but suboptimal connection or usage patterns.",
    "app/models/__init__.py": "Empty file for Python package structure.",
    "app/models/schemas.py": "Pydantic models or related schemas used by the API for requests and responses.",
    "tests/test_app.py": "Executable verification-oriented tests or checks that validate baseline behavior and help measure whether the candidate's fixes preserve functionality."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended categories of fixes, tradeoffs, and reasoning expected from a strong intermediate candidate without requiring exact code.",
  "definitions": "Object of term-to-definition pairs covering important business or technical terminology used in the task so the evaluator and candidate context remain clear.",
  "hints": "A single line nudging investigation toward the right area of the Python and Redis integration without revealing the specific fix, command, API, or data structure to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable correctness, consistency, and performance improvements in simple English.",
  "pre_requisites": "Bullet list of tools, runtime knowledge, and practical familiarity needed to work on the task, such as Python, Docker, HTTP APIs, and Redis basics appropriate for intermediate level.",
  "short_overview": "Bullet list summarising the business problem, the technical focus of the task, and the expected end-state after the candidate improves the existing service."
}}

## CRITICAL REMINDERS
- `"title"` must be in `<action verb> <subject>` format and different from `"name"` — `name` is kebab-case for GitHub repo naming, `title` is human-readable for display
- The generated task must stay within the Python and Redis intermediate competency scope and should primarily assess application-level design, debugging, correctness, and performance improvement
- The task must be based on ONE selected real-world scenario from the provided list and should closely align with that scenario's business context
- The codebase must be FULLY FUNCTIONAL on day one, with the candidate fixing realistic bugs and inefficiencies rather than building the system from scratch
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- If Redis is exposed to the host, it must be bound to localhost only using `127.0.0.1:<port>:<port>`
- **MUST NOT include any version specification** in docker-compose.yml
- **MUST NOT include environment variables or .env file references**
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), Redis (INTERMEDIATE)": [
        PROMPT_PYTHON_REDIS_CONTEXT,
        PROMPT_PYTHON_REDIS_INPUT_AND_ASK,
        PROMPT_PYTHON_REDIS_OPTIMIZATION_INSTRUCTIONS_INTER,
    ]
}