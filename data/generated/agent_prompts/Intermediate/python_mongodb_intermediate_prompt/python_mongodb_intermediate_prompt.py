# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_PYTHON_MONGODB_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_MONGODB_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and MongoDB assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (intermediate: 2-5 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python and MongoDB implementation or fix required, the expected deliverables, and how it aligns with the intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_MONGODB_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python and MongoDB, you are given a list of real world scenarios and proficiency levels for MongoDB.
Your job is to generate an entire task definition, including code files, database initialization, Docker setup, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python application that is already connected to MongoDB with existing schema and data. The project should be runnable and deployed through the provided infrastructure. The candidate is expected to modify application code and MongoDB design/query behavior to fix correctness and performance issues at an intermediate level (2-5 years experience).
The Python application includes:
- Complete application structure with modules, packages, and a clear entry point
- Working MongoDB connection setup using Python MongoDB libraries
- Existing endpoints or service functions with realistic but subtle bugs or inefficiencies
- Pre-populated MongoDB collections with realistic sample data
- Basic tests or verification paths that expose the current incorrect or inefficient behavior

**CRITICAL**: The environment must be FULLY FUNCTIONAL at the start. The candidate should not need to repair broken infrastructure. Their job is to analyze the given scenario, identify the root causes, and implement pragmatic fixes in Python code and MongoDB usage.
**CRITICAL**: The task should feel like inheriting a moderate-complexity production codebase, not building a toy project from scratch.
**CRITICAL**: Keep the task grounded in the provided scenario and aligned with intermediate Python and MongoDB expectations rather than advanced database administration as the primary work.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Python and MongoDB scenario.
- Task must ask to fix bugs in the existing code and/or implement a moderate feature on top of a working Python application backed by MongoDB.
- **CRITICAL**: The Python application should be FULLY FUNCTIONAL but contain subtle logical issues, inefficient MongoDB access patterns, missing indexes, weak payload handling, incorrect update behavior, or inconsistent error handling suitable for intermediate-level engineers.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to solve the task, but DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, make sound tradeoff decisions, and not just patch a single line.
- The question should be a real-world scenario and not a trick question based on syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with the proficiency level required in the competency definition, ensuring that no two questions generated are similar.
- For INTERMEDIATE level proficiency, the questions must be more specific and less open ended than advanced/expert, but still require genuine engineering judgement, debugging, and implementation decisions.
- The task should stay within intermediate Python scope such as modular code organization, exception handling, file/data handling when relevant, CRUD-oriented API logic, serialization, validation, performance improvements, and maintainable code structure.
- The MongoDB work should stay within practical intermediate scope such as schema decisions around embedding vs references when directly relevant, CRUD/update correctness, aggregation pipelines of moderate complexity, projection, pagination, idempotent writes, JSON-schema validation when relevant, indexing strategies such as compound/unique/TTL indexes, explain-plan-informed improvements, and predictable query behavior.
- Do NOT require advanced replica-set administration, sharding operations, backup orchestration, or security platform administration as the main task. Those may be mentioned as context only, not as core candidate work.
- **CRITICAL**: Favor realistic scenarios like fixing inefficient session lookup, correcting update semantics, making an import flow idempotent, improving filtered listing performance, or repairing a Python service that misuses MongoDB queries and document updates.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest best practices and language versions. Strictly avoid using outdated Python or MongoDB patterns.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, MongoDB documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates may use AI to accelerate implementation, but the task should still require them to reason about correctness, performance, maintainability, and tradeoffs in a realistic Python + MongoDB codebase.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Python and MongoDB task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements.
- Matches the complexity level appropriate for intermediate proficiency level (2-5 years experience), keeping in mind that AI assistance is allowed.
- Tests practical Python implementation and debugging skills together with practical MongoDB query, schema, and index reasoning.
- Ensures the candidate must work in both Python code and MongoDB-related logic exposed through the application.
- Uses a Python web service or service-oriented application shape that is easy to run and validate in Docker.
- **CRITICAL**: The application should be COMPLETE and FULLY FUNCTIONAL with realistic code structure, but it should behave incorrectly or inefficiently in one or more important paths aligned to the selected scenario.
- Include realistic sample data and enough scale to make the bad behavior visible without making the task too large for the allotted time.
- Use Python modules and packages with clear separation such as app entry point, database access layer, service layer, schemas/models, and utility helpers where appropriate.
- Prefer PyMongo for straightforward MongoDB integration in Python tasks unless the scenario clearly benefits from another common Python MongoDB library.
- Include at least one meaningful MongoDB design or query issue such as:
  - missing unique/compound/TTL index
  - incorrect use of `$push` instead of `$addToSet`
  - overwriting fields with empty values instead of selective `$set`/`$unset`
  - inefficient repeated lookups that should be consolidated
  - returning too many fields instead of using projection
  - non-idempotent write behavior
  - poor pagination behavior where a simpler intermediate improvement is appropriate
  - improper handling of duplicate key errors or not-found conditions
- Include at least one meaningful Python engineering issue such as:
  - duplicated logic that should be refactored into reusable functions/middleware/helpers
  - weak validation or inconsistent exception handling
  - poor module organization or leaky business logic boundaries
  - inefficient file or payload handling
  - avoidable repeated computation or repeated database access
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## Infrastructure Requirements
- MUST include a complete, fully functional Python application structure that integrates with MongoDB.
- MUST include a Dockerfile for the Python application.
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc.
- A docker-compose.yml file which contains all the applications — a docker for running the Python application and a docker for running the MongoDB database.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working application and database connection.

### Docker-compose Instructions
- Include a MongoDB service and a Python app service.
- The MongoDB user the Python app authenticates as MUST be created DURING MongoDB container initialization by mounting an init script into `/docker-entrypoint-initdb.d/`.
- The app's MongoDB connection string, username, password, database, and `authSource` MUST match the user created by the init script exactly.
- The Python app service should depend on MongoDB and should start successfully even if MongoDB takes a short time to become ready.
- The Python app service MUST use `restart: unless-stopped`.
- Include volume mounts for MongoDB data persistence.
- Include volume mounts for initialization files required to create the MongoDB user and seed data.
- Network configuration for service communication.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- **MUST NOT include environment variables or .env file references**.
- Use hardcoded configuration values instead of environment variables.
- For user and password, use hardcoded values in the docker-compose.yml file and in the corresponding init files.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
- Expose only the ports actually needed for verification, typically MongoDB 27017 and the Python app port.
- **CRITICAL**: Docker-compose handles both container orchestration AND database initialization through volume mounts.
- **CRITICAL**: Do not include extra services that are not required by the chosen scenario.

### MongoDB Initialization Instructions
- Include initialization files mounted into `/docker-entrypoint-initdb.d/` so that MongoDB creates the required database user and initial dataset on first startup.
- The initialization approach may use `.js` or other MongoDB-supported init files, but it must be fully automatic on first container start.
- Seed realistic collections and sample data that expose the intended issue.
- **CRITICAL**: Do not implement the final solution in the init files. The seeded schema, data, and indexes should intentionally leave room for the candidate to diagnose and improve the task.
- If the scenario needs missing or incorrect indexes, seed the collections in a way that leaves those indexes absent or incomplete.
- If the scenario needs duplicate-key handling or idempotency behavior, seed data that makes those behaviors observable.
- Use realistic document structures and field types suitable for the scenario.
- Keep the data volume moderate but meaningful for intermediate-level debugging and performance reasoning.

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`.
- WAIT MECHANISM: Implements proper health checks or retry loops to wait for MongoDB service to be fully ready and accepting connections.
- VALIDATION: Validates that the Python application is responding and connected to the database.
- DATABASE SETUP: MongoDB user creation and seed data execution must happen automatically during MongoDB container initialization via `/docker-entrypoint-initdb.d/`. run.sh MUST NOT create users or run seed scripts itself.
- MONITORING: Monitors container status and provides feedback on successful deployment.
- ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The script must be simple, robust, and idempotent enough for repeated environment setup in an automated workflow.

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes (MongoDB volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and mongo).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, init files, seed files, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."
- Commands that should be included:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|mongo' || true) || true`
  - `rm -rf /root/task`
- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all MongoDB data directories that were mounted via volumes.
  - Ensure that both the custom application container and the MongoDB container are cleaned up.
- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the Python application.
- Should use an appropriate Python base image such as `python:3.11-slim` or similar.
- Should install dependencies from requirements.txt.
- Should expose the appropriate application port.
- Should include proper working directory set to /root/task.
- Should include a proper entry point for the Python application.
- Must be production-ready and follow Docker best practices.
- **DO NOT use environment variables or .env files**.
- **CRITICAL**: Set WORKDIR to /root/task to match the file location.

The output should be a valid json schema:
- README.md (CRITICAL - Follow exact structure specified below)
- requirements.txt (Python dependencies including pymongo and any minimal framework dependencies required by the scenario)
- docker-compose.yml (MongoDB and Python app services configuration)
- Dockerfile (MUST be included - Docker configuration for Python app)
- run.sh (Script to deploy and validate the complete environment)
- kill.sh (Script to completely clean up all resources created by the task)
- .gitignore (Ignore Python caches, virtual environments, logs, local data, and editor files)
- MongoDB initialization files mounted into `/docker-entrypoint-initdb.d/`
- All Python code files following a clear project structure for the chosen scenario

## Code file requirements
- More than 1 file can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP 8 guidelines.
- The code files generated must be valid and executable.
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should provide a working baseline with the intended bugs, inefficiencies, or incomplete behavior suitable for the candidate to improve.
- The application should run, but key business behavior should remain incorrect or inefficient until the candidate completes the task.
- If the task is to fix bugs, make sure the starter code has logical bugs or weak design decisions, not syntactic errors.
- If the task is to implement a moderate feature, make sure the starter code only provides a good starting point and supporting structure.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- Include proper Python package structure with `__init__.py` files where appropriate.
- If tests are included, they should validate observable behavior without revealing the exact implementation approach.
- The code should demonstrate realistic module boundaries such as routes/api layer, service layer, database access, schemas, and utilities where appropriate.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Python and MongoDB development tasks that includes:
- Python bytecode and cache files
- Virtual environment directories
- Build and distribution artifacts
- IDE and editor files
- Log files
- Local MongoDB data directories or task data directories
- Testing artifacts
- OS-specific files
- Any other standard exclusions for Python and MongoDB development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

The README.md file content MUST be fully populated with meaningful, specific content relevant to the generated Python and MongoDB task.
Task Overview section MUST contain the exact business scenario from the task description.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific task scenario being generated.
Use concrete business context, not generic descriptions.
The README must NOT contain database connection details, host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

### Objectives
- Objectives must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run based on visible behavior such as API responses, logs, data state, latency observation, or repeated action consistency.

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "The GitHub repository name in kebab-case under 50 characters and suitable for the generated Python and MongoDB task.",
  "title": "A human-readable display title in the format '<action verb> <subject>', between 50 and 80 characters, and clearly different from the name field.",
  "question": "The full candidate-facing task description explaining the business scenario, the current behavior of the provided Python and MongoDB application, and the specific outcomes the candidate must achieve without revealing the exact implementation approach.",
  "code_files": {{
    "README.md": "Candidate-facing README content that follows exactly the required sections Task Overview, Helpful Tips, Objectives, How to Verify, and NOT TO INCLUDE in README, populated with scenario-specific content.",
    ".gitignore": "A comprehensive ignore file appropriate for Python and MongoDB task development, including cache files, virtual environments, logs, local data folders, editor files, and OS artifacts.",
    "requirements.txt": "A Python dependency manifest listing only the packages actually needed to run the provided Python application and interact with MongoDB for this task.",
    "docker-compose.yml": "A compose file defining the MongoDB datastore and Python application services with localhost-only port bindings, hardcoded configuration, restart behavior, and mounted initialization files.",
    "Dockerfile": "A complete container build file for the Python application using an appropriate Python base image, /root/task as WORKDIR, dependency installation, and the correct startup command.",
    "run.sh": "An executable setup script that starts the Docker services, waits for MongoDB readiness, validates the Python application health, prints progress logs, and references /root/task paths.",
    "kill.sh": "An executable cleanup script that stops containers, removes volumes, networks, related images, prunes Docker resources, deletes /root/task, remains idempotent, and prints logs for every cleanup step.",
    "docker/mongo-init.js": "A MongoDB initialization file executed automatically on first container startup to create the application user, seed the database, and establish the intended starting state without embedding the final solution.",
    "app/__init__.py": "An empty file or minimal package marker required for valid Python package structure.",
    "app/main.py": "The Python application entry point that starts the web service or main process and wires the application together in a runnable way.",
    "app/database.py": "The MongoDB connection and database access setup for the Python application, including robust startup behavior appropriate for a Dockerized task.",
    "app/routes.py": "The request-routing or API layer exposing the main candidate-facing behaviors that currently contain realistic issues to fix.",
    "app/services.py": "Business logic functions or classes that currently contain the subtle correctness or performance issues the candidate is expected to improve.",
    "app/schemas.py": "Request and response validation or serialization definitions used by the Python application to structure incoming and outgoing data.",
    "app/utils.py": "Supporting utility functions used by the application where shared behavior belongs, without revealing the final task solution.",
    "tests/test_app.py": "A test or verification file that checks externally observable behavior of the application without prescribing the exact internal implementation."
  }},
  "answer": "A high-level evaluator-facing solution approach describing the intended root causes, the broad Python and MongoDB improvements expected, and the reasoning behind those improvements without including line-by-line code.",
  "definitions": {{
    "term_1": "A concise definition of a scenario-relevant technical term that appears in the task and may help the evaluator or candidate understand the context.",
    "term_2": "A concise definition of another scenario-relevant technical term that appears in the task and may help the evaluator or candidate understand the context."
  }},
  "hints": "A single line nudging investigation toward the relevant Python and MongoDB behaviors without revealing the fix or naming the exact implementation details to apply.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable correctness, consistency, and performance improvements in the Python application and its MongoDB interactions. Use simple english.",
  "pre_requisites": "A bullet list of tools, environment knowledge, and practical skills needed to work on the task, such as Python 3.10+, Docker, Docker Compose, Git, basic API debugging, and intermediate familiarity with MongoDB CRUD and indexing.",
  "short_overview": "A bullet list summarising the business problem, the technical focus across Python and MongoDB, and the expected outcome after the candidate resolves the issues."
}}

## CRITICAL REMINDERS
1. The task MUST draw inspiration from ONE of the provided real-world scenarios and closely align with that scenario's business and technical context.
2. The task MUST remain within intermediate Python and MongoDB scope for a candidate with roughly 2-5 years of experience.
3. The environment must be FULLY FUNCTIONAL at the start, with working infrastructure and a runnable Python application already connected to MongoDB.
4. **CRITICAL**: Do not generate a database-only task. The candidate must work with both Python application code and MongoDB usage through that codebase.
5. **CRITICAL**: Do not generate a build-from-scratch project. The candidate should inherit an existing codebase with realistic issues.
6. **CRITICAL**: Do not give away the solution in the starter code, README, comments, tests, or task question.
7. **CRITICAL**: All code and script references must use /root/task as the base directory.
8. **CRITICAL**: `docker-compose.yml` MUST NOT include any version specification.
9. **CRITICAL**: `docker-compose.yml` MUST NOT include environment variables or .env file references.
10. **SECURITY-CRITICAL**: Any exposed service ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
11. The README must use exactly these section names and order: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.
12. The REQUIRED OUTPUT JSON STRUCTURE descriptions must remain verbose descriptive strings, not placeholder arrays or example objects.
13. If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), Python (INTERMEDIATE)": [
        PROMPT_PYTHON_MONGODB_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_MONGODB_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_MONGODB_INTERMEDIATE_INSTRUCTIONS,
    ]
}