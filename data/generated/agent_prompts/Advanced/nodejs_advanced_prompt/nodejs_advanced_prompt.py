# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_NODEJS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how advanced Node.js engineering is used in production backend systems — such as asynchronous programming, event loop behavior, non-blocking I/O, streams, worker threads, high-throughput API design, database access patterns, caching, profiling, reliability, security, testing, and deployment readiness?
"""

PROMPT_NODEJS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an advanced Node.js assessment task.

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
- Because this is an infrastructure-shaped task, include only the datastore or external service that the selected real-world scenario actually needs; do not add extra databases, caches, queues, brokers, or search services unless the scenario explicitly requires them

Based on the above inputs, briefly state:
1. Which scenario you selected and why
2. What the task will involve

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""

PROMPT_NODEJS_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in advanced Node.js production systems, you are given a list of real world scenarios and proficiency levels for Node.js.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to diagnose, refactor, optimize, and harden a production-style Node.js backend system at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL Node.js backend application that is already connected to the datastore or external service required by the selected real-world scenario. The system should be FULLY POPULATED with realistic data, working endpoints, scripts, and infrastructure, but it must contain production-relevant performance, reliability, or architectural issues that an advanced Node.js engineer can investigate and improve.

The Node.js application includes:
- Complete REST API endpoints or service entry points with business logic implemented but with advanced performance, concurrency, memory, or reliability problems
- Full datastore connection and configuration setup for the scenario-required datastore only, such as PostgreSQL, Redis, MongoDB, or another service explicitly required by the selected scenario
- Realistic data volume or workload patterns that expose the bottleneck without making the task impossible to run locally
- Existing error handling, logging, and validation that may be incomplete, inconsistent, or insufficient for production behavior
- A runnable Docker Compose environment that starts the application and all scenario-required infrastructure in one go

The candidate's responsibility is to improve the existing system according to the task requirements, while preserving the public API behavior and business outcome. A part of the task completion is to watch the candidate demonstrate advanced Node.js judgment: reasoning about the event loop, asynchronous boundaries, worker isolation, batching, backpressure, query efficiency, memory usage, operational failure modes, and maintainable code structure.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 characters and clearly describe the advanced Node.js production issue being solved.
- Task must provide a working application with existing data, infrastructure, and intentionally problematic implementation details requiring advanced Node.js engineering skills.
- **CRITICAL**: The application should be FULLY functional but should exhibit realistic production problems such as event loop blocking, unbounded concurrency, sequential awaits in hot paths, inefficient database access, excessive memory growth, poor stream handling, weak error boundaries, inconsistent failure responses, missing pagination, missing operational safeguards, or cache/database coordination issues.
- **CRITICAL**: The task must assess advanced Node.js capability, not trivia. The candidate should need to reason about asynchronous programming, non-blocking I/O, event loop impact, streams or buffers where relevant, worker threads or process isolation where relevant, database and cache access patterns, security-conscious API behavior, profiling, observability, and maintainability.
- **CRITICAL**: The task must stay within the advanced Node.js competency scope. It may involve SQL or NoSQL databases, Redis caching, REST APIs, testing, Docker deployment, performance profiling, memory leak detection, authentication or authorization hardening, and robust error handling when these naturally fit the selected scenario.
- **CRITICAL**: Do not make Kubernetes, cloud deployment, CI/CD pipeline setup, npm publishing, GraphQL schema design, OAuth provider setup, or team-management artifacts the primary deliverable unless the selected scenario explicitly requires that surface area and the task remains implementation-focused.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The question must NOT include hints about the exact optimizations needed. The hints will be provided in the "hints" field.
- The complexity of the task must align with ADVANCED proficiency level, approximately 5+ years of practical Node.js experience.
- **CRITICAL TIME BUDGET**: The total task time is {minutes_range} minutes. The candidate needs time to inspect, implement, and verify the fix, so the implementation scope must be focused and completable by an advanced-level developer with AI assistance allowed.
- **CRITICAL SCOPE**: The task must have 3-5 focused objectives that test advanced Node.js concepts such as:
  - Moving CPU-heavy work away from the main event loop while preserving a Promise-based service API
  - Applying bounded concurrency so load is controlled instead of spawning unbounded async work
  - Replacing sequential I/O in hot paths with batched or bounded parallel access patterns
  - Pushing filtering, ordering, aggregation, pagination, or limits into the datastore instead of doing large in-memory transformations
  - Using streams or buffers safely for large payloads without excessive memory growth
  - Returning consistent, secure, and observable errors for datastore, cache, or worker failures
  - Improving database index usage or query structure for a production access pattern
  - Preserving response shape and business behavior while reducing latency and memory pressure
  - Adding focused tests or verification scripts that prove the behavior and performance improvement
- For ADVANCED level, the scenario should require architectural judgment and involve a realistic combination of:
  - A Node.js HTTP API or service layer under load
  - At least one scenario-required datastore or external service, such as PostgreSQL or Redis, when the selected scenario requires it
  - Existing implementation problems that are subtle enough to require analysis, but focused enough for the time budget
  - Production-style failure handling, observability, and maintainability concerns
- The task should involve one cohesive Node.js application or a small set of tightly related service modules. Avoid creating unnecessary microservices unless the selected scenario truly requires multiple services.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Node.js documentation, datastore documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem.
- Candidates may use AI to help with implementation, but the task should still require them to make sound engineering decisions and validate the result.
- The assessment should reward practical problem-solving, maintainability, operational awareness, and correct behavior under realistic constraints.

## Code Generation Instructions
Based on the real-world scenarios provided, create an advanced Node.js task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for ADVANCED proficiency level, keeping in mind that AI assistance is allowed but should not diminish the need for advanced Node.js system reasoning
- Tests practical production-level Node.js debugging, optimization, reliability, and architecture skills
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list to ensure variety
- **CRITICAL**: The Node.js application should be COMPLETE and FULLY FUNCTIONAL with endpoints, datastore connections, scripts, and realistic sample data, but with intentionally problematic implementation requiring advanced analysis
- **CRITICAL**: The task must focus on improving an existing production-style service, not building a full system from scratch
- **CRITICAL**: The datastore or external service included must come from the selected scenario's actual need. For example, if the selected scenario needs PostgreSQL, include PostgreSQL and init_database.sql; if it needs Redis, include Redis configuration or seed data; if it needs both PostgreSQL and Redis, include both. Do not invent extra infrastructure.
- Use modern Node.js patterns with async/await, modular service layers, structured error handling, and realistic package.json scripts.
- The starter implementation must run successfully before the candidate changes it, even if it performs poorly or fails under specific load, edge-case, or dependency-failure conditions.
- Include a small verification script or test suite that the candidate can run after implementation to demonstrate observable improvement.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## Infrastructure Requirements
- MUST include a complete, fully functional Node.js backend application that integrates with the datastore or external service required by the selected scenario
- MUST include a Dockerfile for the Node.js application
- MUST include a run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools, and application containers
- MUST include a docker-compose.yml file that contains the Node.js application and the scenario-required datastore or external service
- MUST include kill.sh to fully clean up all containers, volumes, images, networks, and project files
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts during environment preparation
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- The infrastructure must start successfully in one go, seed data must be ready, and the API must be reachable after run.sh finishes
- Do not include Kafka, RabbitMQ, Elasticsearch, additional databases, or unrelated services unless the selected real-world scenario explicitly requires them
- Primary runtime and common Node.js libraries are pre-installed by the template, so do not include apt-get install, npm install, or runtime installation steps in run.sh

### Docker-compose Instructions
- Include the Node.js application service and only the datastore or external service required by the selected real-world scenario
- **MUST NOT include any version specification** in the docker-compose.yml file
- **MUST NOT include environment variables or .env file references**
- Use hardcoded local configuration values in source/config files and compose service definitions instead of .env files
- Use `docker compose` compatible syntax
- The Node.js service must be built from the included Dockerfile
- Use proper depends_on with health checks so the application starts only after the datastore or external service is ready
- Use named volumes for datastore persistence where appropriate
- Do not mount the application source over the container working directory in a way that overwrites node_modules
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host
- Application ports should also be bound to localhost unless the selected scenario requires broader exposure
- PostgreSQL, MongoDB, Redis, or other services must have health checks appropriate to that service
- Database initialization must be handled automatically through mounted initialization files or startup scripts
- Docker Compose must be able to bring up the entire task with no manual steps after files are written

### init_database.sql / Redis Configuration Instructions
- If the selected scenario uses PostgreSQL or another SQL database, include init_database.sql with complete schema creation, realistic seed data, and intentionally inefficient or incomplete indexes/query-support structures that expose the advanced Node.js performance problem
- If the selected scenario uses Redis, include any required Redis service configuration and seed data script only when needed for the scenario
- If the selected scenario uses MongoDB, include an initialization script that creates realistic collections and sample data needed to expose the issue
- The database or cache must be FULLY POPULATED with enough realistic data to demonstrate the bottleneck, but not so much that startup exceeds the task time budget
- **CRITICAL**: Do not implement the solution in initialization files. Initialization files should create the starting state that reveals the production problem
- Include realistic access patterns such as large ledger histories, shipment timelines, media processing jobs, cache lookups, account activity, inventory events, or other domain-specific data from the selected scenario
- Keep credentials, database names, and service names simple and hardcoded in generated files; do not reference .env files
- Do not include database connection details, usernames, passwords, ports, or client tool suggestions in README.md

### Run.sh Instructions
- Use `#!/usr/bin/env bash` and `set -e` at the top
- The script must `cd /root/task` before running commands
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d --build`
- WAIT MECHANISM: Implements proper health checks to wait for every datastore or external service to be fully ready and accepting connections
- VALIDATION: Validates that the Node.js application is responding through a health endpoint
- DATABASE SETUP: Initialization files must be automatically executed during datastore startup or by a deterministic one-time initialization container/script
- MONITORING: Monitors container status and provides feedback on successful deployment
- ERROR HANDLING: Includes proper error handling for failed container starts, failed datastore readiness, or failed application health checks
- If any validation fails after retries, print `docker compose logs` and exit with code 1
- End with a clear success message showing the local application URL and the verification command
- Do not run npm install in run.sh; dependencies should be installed inside the Docker build from package.json

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, Dockerfile, datastore files, and application files.
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes, including datastore volumes, named volumes, and anonymous volumes.
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task, including the custom Node.js image and scenario datastore images.
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed by using `|| true` where necessary.
  8. Print logs at every step, such as "Stopping containers...", "Removing volumes...", "Removing networks...", "Removing images...", and "Deleting folder..." so the user knows what is happening.
  9. After successful cleanup, print a final message exactly like "Cleanup completed successfully! Droplet is now clean."
- Commands that should be included:
  - `cd /root/task || true`
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker ps -q | xargs -r docker stop || true`
  - `docker ps -aq | xargs -r docker rm -f || true`
  - `docker volume prune -f || true`
  - `docker network prune -f || true`
  - `docker image prune -a -f || true`
  - `docker system prune -a --volumes -f || true`
  - `rm -rf /root/task || true`
- Dependencies cleanup:
  - Ensure that cached Node.js files such as node_modules, *.log, .npm, and .node-gyp are also removed if present in /root/task/
  - Remove all datastore data directories if any were mounted under /root/task/
  - Ensure that both custom application containers and datastore containers are cleaned up
- Extra instruction:
  - The script should be idempotent and safe to run multiple times without errors
  - Always use `set -e` at the top to exit on error except when explicitly ignored with `|| true`
  - Print "Cleanup completed successfully! Droplet is now clean." as the final message

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the Node.js application
- Use an appropriate Node.js base image such as node:20-alpine or node:18-alpine
- Set WORKDIR to /root/task to match the file location
- Copy package.json and package-lock.json if present before installing dependencies
- Install dependencies during image build using npm ci or npm install based on the generated manifest
- Copy the application source after dependencies are installed
- Expose the appropriate application port
- Start the application with a package.json script such as npm start
- Must be production-ready and follow Docker best practices
- **DO NOT use environment variables or .env files**
- **CRITICAL**: Set WORKDIR to /root/task to match the file location

The output should be a valid json schema:
- README.md: candidate-facing concise task description following the exact README instructions below
- .gitignore: comprehensive Node.js, Docker, datastore, logs, coverage, and editor exclusions
- package.json: Node.js manifest with realistic dependencies and scripts for start, test, and verification
- package-lock.json: include when useful for deterministic Docker builds
- Dockerfile: complete Dockerfile for the Node.js application
- docker-compose.yml: complete Compose file for the Node.js app and scenario-required datastore services
- run.sh: complete deployment and health validation script
- kill.sh: complete cleanup script following the exact cleanup requirements
- init_database.sql: include when the selected scenario requires PostgreSQL or another SQL database
- redis-seed.js or redis-init files: include only when the selected scenario requires Redis seed data
- src/server.js or src/app.js: application entry point and HTTP server setup
- src/routes/*.js: route handlers exposing the scenario API
- src/services/*.js: service logic containing the intentionally problematic advanced Node.js behavior
- src/repositories/*.js: datastore access layer when useful for the scenario
- src/workers/*.js: worker thread files when the selected scenario involves CPU-heavy work
- src/lib/*.js: shared utilities for logging, errors, metrics, configuration, and datastore clients
- test/*.js or scripts/*.js: focused verification tests or workload scripts that demonstrate the expected behavior before and after improvement

## Code file requirements
- Generate a realistic Node.js project structure with modular source files
- Code should follow modern Node.js best practices using async/await, clear module boundaries, structured error handling, and readable naming
- Use CommonJS or ES modules consistently across the project
- Include a realistic package.json with scripts for start, test, and verification
- Include a health endpoint that run.sh can use to validate startup
- Include starter code that is complete and runnable but intentionally contains advanced-level performance, concurrency, reliability, or data-access problems
- **CRITICAL**: The generated code files should provide partial or flawed implementations that require architectural completion or optimization
- The core implementation decisions, such as how to isolate CPU-heavy work, control concurrency, batch I/O, handle backpressure, reduce memory growth, improve query performance, or standardize failure behavior, MUST be left for the candidate to design
- DO NOT include any TODO or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "move this to a worker", "add index here", "batch these calls", "avoid sequential await", or "implement cache here"
- DO NOT add comments that reveal the solution or implementation details
- The generated project structure must be buildable and bootable with Docker Compose
- The application should expose observable behavior that lets the candidate prove improvement through tests, response times, stable memory usage, consistent errors, or log output
- Include realistic sample data volume but keep Docker startup reliable and fast
- Preserve the same external response shape expected by the scenario unless the task explicitly asks for an accepted asynchronous response, such as returning `202` with a queued job status
- Include focused tests or scripts that check correctness and basic performance expectations without requiring external paid services
- Avoid requiring the candidate to install global tools, configure cloud services, publish npm packages, or perform manual infrastructure setup

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file suitable for Node.js, Docker, and datastore-backed backend development tasks that includes:
- Node.js files such as node_modules/, .npm/, .node-gyp/, npm-debug.log*, yarn-debug.log*, and pnpm-debug.log*
- Build and distribution artifacts such as dist/, build/, coverage/, and .nyc_output/
- IDE and editor files such as .vscode/, .idea/, *.swp, and *.swo
- Environment files such as .env, .env.local, .env.*.local, and secrets files
- Log files such as *.log and logs/
- Temporary files and cache directories
- Docker and local datastore data directories if any are mounted under the project
- OS-specific files such as .DS_Store and Thumbs.db
- Any generated benchmark output, profiling snapshots, or local reports that should not be committed

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

The README.md file content MUST be fully populated with meaningful, specific content. ALL sections must have substantial content - no empty or placeholder text allowed. Content must be directly relevant to the specific advanced Node.js scenario being generated. Use concrete business context from the selected real-world scenario, not generic descriptions.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- Explain that the service is already functional but exhibits production-impacting behavior such as latency, event-loop delay, memory growth, dependency failure, or inconsistent API behavior.
- NEVER generate empty content.
- Do not include bold time-budget callouts.
- Do not include setup commands.
- Do not include database-connection details, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery toward advanced Node.js reasoning such as event-loop impact, workload size, dependency failure behavior, data movement, memory pressure, observability, or correctness under concurrency.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not include setup commands or implementation steps.

### Objectives
- Objectives must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step or an API/library to use.
- Objectives should cover functional correctness, performance or resource improvement, reliability under dependency failures, maintainability, and verification.
- Objectives should be measurable but not prescribe exact frameworks, APIs, method signatures, class names, query text, or implementation approaches.

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run, such as test output, response shape, latency observation, log line, event-loop delay reading, memory reading, or consistent error response.
- Include verification of the existing business behavior and the improved production characteristic.
- Do not reveal the solution or tell the candidate which internal code path to change.

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, `npm test`, or similar commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>"
- Database-connection details including host, port, username, password, database name, or client-tool suggestions
- `<DROPLET_IP>` placeholders
- Specific index definitions, worker implementation details, batching strategy names, retry strategy names, or profiling commands that reveal the solution
- Any direct answer that would prevent the assessor from evaluating the candidate's design judgment

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A kebab-case GitHub repository name under 50 characters that clearly identifies the advanced Node.js production issue without using placeholders or generic names.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, that is different from name and summarizes the advanced Node.js improvement task.",
  "question": "The full candidate-facing task description explaining the selected business scenario, current functional but problematic system behavior, the focused advanced Node.js outcomes required, and the observable success criteria without revealing the implementation.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content following the exact required sections: Task Overview, Helpful Tips, Objectives, How to Verify, and NOT TO INCLUDE in README, with concise non-revealing guidance and no setup or connection details.",
    ".gitignore": "A comprehensive .gitignore for Node.js, Docker, datastore artifacts, logs, coverage, editor files, temporary files, and local profiling or benchmark outputs.",
    "package.json": "A complete Node.js package manifest with realistic dependencies and scripts for starting the app, running focused tests, and running verification workloads without requiring global tools.",
    "Dockerfile": "A complete Dockerfile for the Node.js application using an appropriate Node.js base image, /root/task as WORKDIR, dependency installation during build, and a production-style start command.",
    "docker-compose.yml": "A Docker Compose file with no version field and no .env references that starts the Node.js application plus only the datastore or external service required by the selected scenario, with health checks, named volumes, localhost-bound exposed datastore ports, and reliable startup ordering.",
    "run.sh": "A complete idempotent deployment script that changes to /root/task, runs docker compose up -d --build, waits for all services to become healthy, validates the application endpoint, prints logs on failure, and ends with a concise success message.",
    "kill.sh": "A complete cleanup script that follows the required nine-step cleanup pattern, removes containers, volumes, networks, images, prunes Docker resources, deletes /root/task, uses || true for destructive commands, prints progress logs, and ends with the required cleanup success message.",
    "init_database.sql": "A complete SQL initialization file only when the selected scenario requires a SQL datastore, containing schema, seed data, and the intentionally incomplete starting database state needed to expose the performance or reliability issue.",
    "redis-seed.js": "A Redis seed or initialization file only when the selected scenario requires Redis, containing realistic cache or lookup data needed by the task without implementing the candidate's solution.",
    "src/server.js": "The Node.js application entry point that starts the HTTP server, registers routes, initializes shared clients, exposes a health endpoint, and uses structured startup and shutdown behavior.",
    "src/app.js": "The application composition module that wires routes, middleware, error handling, and shared services in a clean but intentionally improvable structure.",
    "src/routes/api.js": "The scenario-specific route handlers that expose the functional API surface and delegate to services while preserving the problematic behavior the candidate must analyze.",
    "src/services/domainService.js": "The main business service containing the existing advanced Node.js bottleneck or reliability problem in a realistic form without comments that reveal the solution.",
    "src/repositories/datastoreRepository.js": "The datastore access layer used by the service, including realistic queries or cache access patterns that are functional but need advanced improvement when the scenario requires it.",
    "src/lib/errors.js": "Shared error helpers or classes that support consistent API behavior while leaving meaningful failure-handling improvements for the candidate.",
    "src/lib/logger.js": "A lightweight structured logging utility suitable for observing request flow, failures, and verification output without requiring external services.",
    "src/workers/worker.js": "A worker-related file only when the selected scenario involves CPU-heavy work or isolated execution, included as starter structure without revealing the final implementation.",
    "test/task.test.js": "Focused tests that validate business behavior and key failure cases without prescribing the implementation approach.",
    "scripts/verify.js": "A verification workload script that exercises the important endpoint or service behavior and reports observable metrics such as latency, response status, memory usage, event-loop delay, or error shape."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected advanced Node.js reasoning, such as reducing event-loop blocking, controlling concurrency, moving work to appropriate boundaries, optimizing datastore access, improving failure behavior, and preserving API compatibility without exposing exact candidate-facing instructions.",
  "definitions": "An object containing concise term-to-definition pairs for important concepts used in the task, such as event loop delay, non-blocking I/O, worker isolation, bounded concurrency, backpressure, connection pooling, query selectivity, cache lookup, or graceful degradation, selected according to the generated scenario.",
  "hints": "A single line nudging the candidate toward investigation of runtime behavior, I/O patterns, resource usage, and dependency failure modes without revealing the specific fix or naming the exact API, pattern, index, or algorithm to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable performance, reliability, resource usage, and maintainability improvements in simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Node.js, npm, Docker, Docker Compose, REST API testing, async/await, event loop behavior, profiling basics, datastore query basics, and the specific datastore concepts required by the selected scenario.",
  "short_overview": "A bullet list summarising the business problem, the advanced Node.js technical focus, and the expected production-quality outcome."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **code_files** must include README.md, .gitignore, package.json, Dockerfile, docker-compose.yml, run.sh, kill.sh, source files, tests or verification scripts, and datastore initialization files required by the selected scenario.
3. **Deployment must succeed in one go** — run.sh must start the app and all scenario-required infrastructure, wait for readiness, and validate the health endpoint.
4. **docker-compose.yml must NOT have a `version:` field**.
5. **MUST NOT include environment variables or .env file references**.
6. **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
7. **kill.sh** must follow the exact cleanup pattern specified above and end with "Cleanup completed successfully! Droplet is now clean."
8. **Task must be completable within the allocated time** for ADVANCED proficiency.
9. **NO comments in code** that reveal the solution.
10. **README.md must use exactly these sections in order**: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.
11. **README.md must not include setup commands, database connection details, `<DROPLET_IP>` placeholders, direct solutions, or implementation-revealing API/library/pattern names.**
12. **Focus on advanced Node.js production engineering**: event loop behavior, async I/O, bounded concurrency, streams or workers when relevant, datastore access efficiency, memory behavior, failure handling, observability, and maintainable design.
13. **Do not invent extra infrastructure**. Include only the datastore or external service that the selected real-world scenario actually exercises.
14. **Starter code must be FULLY FUNCTIONAL and FULLY POPULATED**, but intentionally inefficient or fragile in ways that require advanced Node.js judgment to improve.
"""

PROMPT_REGISTRY = {
    "NodeJs (ADVANCED)": [
        PROMPT_NODEJS_ADVANCED_CONTEXT,
        PROMPT_NODEJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_NODEJS_ADVANCED_INSTRUCTIONS,
    ],
}