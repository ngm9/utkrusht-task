# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_NODEJS_REACT_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how an advanced React.js and Node.js engineer is expected to own full-stack features, reason across UI and API boundaries, optimize performance, preserve data consistency, and deliver production-grade maintainable systems?
"""

PROMPT_NODEJS_REACT_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React.js and Node.js full-stack assessment task.

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
2. What the task will involve across the React.js frontend, Node.js backend, and datastore

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""

PROMPT_NODEJS_REACT_ADVANCED_INSTRUCTIONS = """
# React.js + Node.js Advanced Full-Stack Task Requirements

## GOAL
As a technical architect super experienced in React.js, Node.js, production full-stack architecture, and PostgreSQL-backed web applications, you are given a list of real world scenarios and proficiency levels for React.js and Node.js.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL full-stack application with:
- A React.js frontend that renders successfully, integrates with the backend API, and contains realistic but incomplete or flawed behavior around state, race conditions, UX feedback, accessibility, error handling, or performance
- A Node.js backend API that starts successfully, connects to PostgreSQL, exposes working endpoints, and contains realistic but incomplete or flawed behavior around concurrency, transactions, query shape, payload design, validation, security, resilience, or performance
- A PostgreSQL database that is FULLY POPULATED with realistic sample data and schema definitions that support the chosen business scenario
- Docker-based infrastructure that can be deployed in one go, with the application and PostgreSQL available from /root/task

The candidate's responsibility is to make targeted full-stack changes according to the task requirements, improving the React.js user experience and the Node.js API/database behavior together. A part of the task completion is to watch the candidate make advanced engineering decisions, preserve correctness under realistic edge cases, improve maintainability, and avoid narrow fixes that only work for the happy path.

**CRITICAL FULL-STACK REQUIREMENT**: This task is NOT only about React.js UI work or only about Node.js API work. The generated task must require meaningful changes on BOTH fronts:
- React.js changes involving advanced client-side reasoning such as request lifecycle handling, state consistency, performance-aware rendering, reusable component design, error boundaries, accessibility, or stale response prevention
- Node.js changes involving advanced backend reasoning such as transaction boundaries, conflict handling, efficient query design, response shape control, async error handling, idempotency, secure validation, or production-grade API behavior
- PostgreSQL changes only when they naturally support the selected scenario, such as constraints, indexes, schema guards, seeded data, or query improvements needed by the Node.js API

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 characters, kebab-case, and clearly describe the advanced full-stack React.js + Node.js scenario.
- Task title MUST be human-readable in "<action verb> <subject>" format, 50-80 characters, and different from the name.
- Task must ask the candidate to implement a focused production-style improvement, refactor existing full-stack behavior, or fix complex logical bugs in an existing React.js + Node.js codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a strong starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix superficial errors.
- The question should be a real-world scenario that tests architectural thinking, debugging, optimization, and cross-layer reasoning, not a trick question based on syntax errors.
- **CRITICAL**: The complexity of the task and specific ask expected from the candidate must align with ADVANCED proficiency level (6+ years React.js and Node.js experience), ensuring that no two questions generated are similar.
- **CRITICAL**: For ADVANCED proficiency, the generated task should require the candidate to reason about at least three of the following, while still being completable within {minutes_range} minutes:
  - Correctness under concurrency, duplicate submissions, stale responses, partial failures, or conflicting updates
  - React.js architecture using modern functional components, hooks, Context API, reducers, reusable components, or carefully scoped state management
  - React.js performance and reliability using memoization, request cancellation or stale response handling, thoughtful render boundaries, error boundaries, or accessible user feedback
  - Node.js API design using async/await, robust request validation, response shaping, centralized error handling, secure defaults, and maintainable service boundaries
  - PostgreSQL-backed data consistency using transactions, constraints, query optimization, indexes, row-level conflict handling, or predictable HTTP error mapping
  - Full-stack observability through useful logs or response metadata without leaking sensitive information
  - Practical security considerations such as avoiding over-fetching, preventing unsafe input handling, and mapping backend failures to safe frontend messages
- **CRITICAL**: The generated task must be a focused work item, not a large product build. Prefer 3-4 implementation objectives that require advanced judgment across the stack.
- **CRITICAL**: The application must be FULLY FUNCTIONAL and deployable before the candidate changes it. The starter code should run and expose the flawed or incomplete behavior exactly as described.
- **CRITICAL**: Starter code must perfectly implement only the current flawed or incomplete implementation. It must NOT include the final transaction handling, stale request handling, optimized query, idempotency mechanism, accessibility improvement, memoization strategy, or other core solution that the candidate must design.
- The question must NOT include hints about the specific implementation needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React.js best practices (React 18+) and current Node.js standards. Use functional React components with hooks exclusively.
- Use TypeScript where it improves the advanced-level signal, but keep the file count and complexity realistic for the allotted time.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with ADVANCED proficiency (6+ years React.js and Node.js experience).
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, React.js documentation, Node.js documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect advanced React.js and Node.js proficiency while requiring genuine engineering judgment, debugging, architectural thinking, and production-quality implementation.
- Candidates will be encouraged to use AI to help with implementation but should understand, validate, and adapt the concepts being applied.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a React.js + Node.js + PostgreSQL full-stack task that:
- Draws inspiration from the input scenarios to determine the business context and technical requirements.
- Matches ADVANCED proficiency level (6+ years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced full-stack reasoning.
- Can be completed within {minutes_range} minutes.
- Tests practical production-grade React.js and Node.js skills that require cross-layer debugging, performance awareness, correctness, maintainability, and thoughtful tradeoffs.
- Selects a different real-world scenario each time to ensure variety in task generation.
- Provides a complete working application with realistic frontend, backend, and database files.
- Focuses on one coherent business flow, such as healthcare appointment booking, e-commerce product search, operations dashboards, customer support workflows, inventory reservation, real-time admin review queues, or another scenario directly provided in the input scenarios.
- Includes React.js code that currently exhibits a realistic advanced-level flaw, such as duplicate submissions, stale response rendering, fragile shared state, excessive re-renders, poor error recovery, inaccessible status messages, or inadequate handling of async request lifecycles.
- Includes Node.js code that currently exhibits a realistic advanced-level flaw, such as missing transaction boundaries, incorrect conflict mapping, inefficient query shape, over-fetching, weak validation, missing pagination limits, unsafe error responses, or poor async error handling.
- Includes PostgreSQL schema and seeded data that make the issue observable without requiring candidates to invent data.
- Uses a concise but realistic project structure. Avoid unnecessary framework complexity that distracts from the full-stack assessment.
- The task must not require Kubernetes, cloud deployment, CI/CD setup, npm publishing, or large-scale micro-frontend implementation even though advanced engineers may know those topics.

## Infrastructure Requirements
- MUST include a complete, fully functional full-stack application using React.js frontend, Node.js backend API, and PostgreSQL datastore.
- MUST include a Dockerfile for the application container.
- MUST include a docker-compose.yml file containing the application service and PostgreSQL service required by the scenario.
- MUST include an init_database.sql file that initializes schema, constraints that are part of the starting state, and realistic seed data.
- MUST include a run.sh file with the end-to-end responsibility of deploying the infrastructure and validating readiness.
- MUST include a kill.sh file that completely cleans up the created containers, volumes, networks, images, and /root/task.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- **CRITICAL**: The application must be deployable in one go and must not require candidates to install runtime dependencies manually.
- Do NOT include any datastore other than PostgreSQL unless the selected real-world scenario explicitly requires another external service.

### Docker-compose Instructions
- The docker-compose.yml file MUST include:
  - A PostgreSQL service for the scenario datastore.
  - An application service for the Node.js API and React.js frontend, built from the Dockerfile.
  - Proper depends_on and healthcheck configuration so the application starts only after PostgreSQL is ready.
  - Named volumes for PostgreSQL persistence.
  - A dedicated Docker network for service communication.
  - Hardcoded configuration values in service commands or application config files; do not use .env files.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- **MUST NOT include environment variables or .env file references** in docker-compose.yml, Dockerfile, run.sh, or application code.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for PostgreSQL and any application ports exposed to the host.
- PostgreSQL must expose its port only as `127.0.0.1:5432:5432`.
- The application API or web port must also be bound to localhost only, for example `127.0.0.1:3000:3000`.
- Use Docker service names for internal communication between app and PostgreSQL.
- The PostgreSQL service must mount `/root/task/init_database.sql` into the standard initialization location so the database is FULLY POPULATED on first startup.
- Do not include separate manual seed commands in run.sh unless absolutely necessary; database initialization should be automatic through the PostgreSQL container initialization mechanism.
- The application service must not use a bind mount that overwrites installed dependencies inside the container.
- All paths in docker-compose.yml must be valid relative to /root/task or absolute under /root/task.

### init_database.sql Instructions
- Generate a complete init_database.sql file for PostgreSQL.
- The SQL file must create all tables, relationships, constraints, and seed data needed for the selected scenario.
- The database must be FULLY POPULATED with realistic data that makes the current flawed behavior observable through the application.
- The schema should support advanced-level reasoning without becoming a database-only task.
- If the task involves duplicate booking, reservation, or conflicting writes, include starting schema/data that exposes the issue but do NOT include the final database guard if that guard is the candidate's required change.
- If the task involves search or performance, include enough data and query patterns to make inefficient behavior visible, but keep the SQL file size reasonable.
- Do NOT implement the complete solution in init_database.sql.
- Do NOT include comments that reveal the solution or hint at the exact index, constraint, transaction strategy, or query rewrite candidates should use.
- Use deterministic seed data so verification is repeatable.

### Run.sh Instructions
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- The PRIMARY RESPONSIBILITY is to start Docker containers using `docker compose up -d --build`.
- The script MUST `cd /root/task` before running Docker commands.
- Implement a wait mechanism that checks PostgreSQL readiness before validating the application.
- Validate that the Node.js API is responding and connected to PostgreSQL.
- Validate that the React.js frontend route or application health endpoint responds successfully.
- If validation fails after retries, print `docker compose logs` and exit with code 1.
- Print clear progress logs at every step.
- End with a clear success message showing the localhost URLs for the running application.
- Do NOT include `apt-get install`, `pip install`, `npm install`, or runtime installation commands in run.sh.
- Do NOT include environment variables or .env file references.
- All file and Docker paths must reference /root/task as the base directory.

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, Dockerfile, and PostgreSQL data.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes including PostgreSQL named volumes and anonymous volumes.
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task including the custom application image and postgres image.
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, init_database.sql, source files, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed by using `|| true` where necessary.
  8. Print logs at every step, for example "Stopping containers...", "Removing volumes...", "Removing images...", "Deleting folder..." so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."
- Commands that should be included:
  - `cd /root/task || true`
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker ps -q | xargs -r docker stop || true`
  - `docker ps -aq | xargs -r docker rm -f || true`
  - `docker volume prune -f || true`
  - `docker image prune -a -f || true`
  - `docker system prune -a --volumes -f || true`
  - `docker rmi -f $(docker images -q | grep -E 'react-node|node-react|fullstack|postgres' || true) || true`
  - `rm -rf /root/task`
- Dependencies cleanup:
  - Ensure that any cached Node.js files such as `node_modules`, `*.log`, `.npm`, `.node-gyp`, build outputs, and coverage folders are also removed if present in `/root/task/`.
  - Remove all PostgreSQL data directories that were mounted via volumes.
  - Ensure that both the custom application container and the PostgreSQL container are cleaned up.
- Extra instruction:
  - The script should be idempotent and safe to run multiple times without errors.
  - Always use `set -e` at the top to exit on error except when explicitly ignored.
  - Every destructive command MUST end with `|| true`.
  - The final cleanup message must be exactly meaningful and clear, ending with "Cleanup completed successfully! Droplet is now clean."

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the full-stack Node.js application.
- Use an appropriate Node.js base image such as node:18-alpine or node:20-alpine.
- The Dockerfile may build the React.js frontend and serve it through the Node.js API, or may run a single Node.js process that serves both API routes and static frontend assets.
- Install dependencies from package.json using npm or yarn inside the image build, not in run.sh.
- Expose the application port used by the Node.js server.
- Set WORKDIR to `/root/task` to match the file location.
- Include a proper entry point such as `npm start` or `node server.js`.
- Must be production-ready enough for the assessment environment and follow Docker best practices.
- **DO NOT use environment variables or .env files**.
- **CRITICAL**: Set WORKDIR to /root/task to match the file location.
- The Dockerfile must not include comments that reveal the candidate's solution.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Comprehensive exclusions for React.js, Node.js, PostgreSQL, Docker, logs, build artifacts, and editor files)
  - package.json (Full-stack Node.js package manifest with scripts for starting the API and building/serving the React.js frontend)
  - docker-compose.yml (Application and PostgreSQL services only, no version field, no environment variables or .env references)
  - Dockerfile (Builds and runs the full-stack application from /root/task)
  - run.sh (Automated deployment and health validation script)
  - kill.sh (Complete cleanup script following the required cleanup pattern)
  - init_database.sql (PostgreSQL schema and seed data)
  - backend source files such as server.js, routes, services, database access, validation, and error handling files
  - frontend source files such as React entry point, App component, components, hooks, utilities, styles, and API client files
  - Any additional source files needed for the scenario, while keeping the project focused and runnable

## Code file requirements
- Generate a realistic full-stack folder structure, for example `server/`, `client/`, `shared/`, or another clear organization suitable for the chosen scenario.
- Code should follow modern Node.js best practices using async/await, structured error handling, clear service boundaries, and safe response formatting.
- React.js code should use functional components with hooks exclusively, React 18+, modern JavaScript or TypeScript, and accessible UI states.
- Include a package.json with all required scripts, including at minimum a start script for the container and a script that can build or serve the frontend as part of the application lifecycle.
- Include frontend code that is valid, builds successfully, and renders the current implementation.
- Include backend code that is valid, starts successfully, connects to PostgreSQL, and exposes the current implementation.
- The generated project must run cleanly with Docker Compose after run.sh executes.
- **CRITICAL**: The generated code files should provide partial implementations that require advanced full-stack completion.
- Include existing components, API client code, routes, services, and database access code that the candidate needs to extend or refactor.
- The core architectural decisions, transaction strategy, concurrency guard, stale request handling, performance optimization, conflict mapping, response shaping, or state management solution that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- DO NOT include comments like "Add transaction here", "Use AbortController here", "Add index here", "Disable submit here", or "Implement debounce here".
- DO NOT add comments that reveal solution or implementation details.
- The starter code must be runnable and demonstrate the current flawed behavior, but must not contain the core logic solution.
- Keep file count realistic for {minutes_range} minutes. Prefer focused, cohesive files over a large scaffold.
- Avoid using frontend or backend libraries solely to hide the real assessment behind framework setup.
- Do not include testing framework configuration as the central task. Tests may be present only if they help verify the scenario and are already runnable.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore file suitable for advanced React.js, Node.js, PostgreSQL, and Docker development tasks that includes:
- Node.js files such as node_modules, .npm, .node-gyp
- React and frontend build outputs such as dist/, build/, coverage/
- Server build and distribution artifacts
- IDE and editor files such as .vscode/, .idea/, *.swp, *.swo
- Environment files such as .env, .env.local, .env.* even though the task must not use them
- Log files such as *.log and logs/
- PostgreSQL data directories and Docker volume folders
- Testing artifacts such as .nyc_output/ and coverage/
- OS-specific files such as .DS_Store and Thumbs.db
- Any other standard exclusions for React.js, Node.js, PostgreSQL, and Docker development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md MUST contain the following sections in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

The README.md file content MUST be fully populated with meaningful, specific content. Content must be directly relevant to the specific React.js + Node.js full-stack task scenario being generated. Use concrete business context from the selected real-world scenario, not generic descriptions. Do not include database-connection details, usernames, passwords, client-tool suggestions, hostnames, port numbers, or `<DROPLET_IP>` placeholders in the README.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- The section must explain the current full-stack behavior at a high level without revealing the specific implementation approach.
- NEVER generate empty content.
- NO bold time-budget callouts.
- The Task Overview section MUST contain the exact business scenario from the task description in concise language.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, SQL construct, React hook, Node.js method, or algorithm that solves the task.
- Tips may point candidates toward reasoning about user experience, request lifecycle, backend consistency, observable performance, failure handling, and edge cases.
- Do NOT include direct solutions, architectural decisions, or implementation steps.

### Objectives
- Objectives must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step or an API/library to use.
- Objectives should cover both React.js frontend behavior and Node.js backend/database behavior.
- Include outcomes around correctness, user feedback, API predictability, performance, maintainability, reliability, or security as appropriate for the selected scenario.
- Objectives will be used to verify task completion and award points.

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run or observe, such as UI behavior, API response shape, latency observation, log line, repeated action behavior, conflict response, or data consistency result.
- Include both frontend and backend verification checkpoints.
- Focus on measurable, verifiable outcomes that confirm the task is complete without revealing the exact solution.

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands such as `npm install`, `npm start`, `npm test`, `docker compose up`, `docker-compose up`, `mvn test`, or any equivalent setup/run commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, SQL statements, database index names, React hook names, Node.js method names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", or "add this query"
- Database access details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Specific file-by-file implementation instructions that would reveal the solution

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely describes the full-stack task without using placeholders or examples.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, and specific to the selected business scenario.",
  "question": "A complete candidate-facing task description that includes the selected business scenario, the current implementation behavior, the required changes at a full-stack level, and the success criteria without revealing exact solution steps.",
  "code_files": "An object mapping every filepath to its complete file contents, including README.md, .gitignore, package.json, docker-compose.yml, Dockerfile, run.sh, kill.sh, init_database.sql, backend source files, frontend source files, and any focused supporting files needed for a runnable advanced full-stack task.",
  "answer": "An evaluator-facing high-level solution approach describing the expected React.js, Node.js, and PostgreSQL improvements, including key tradeoffs and correctness considerations without requiring a single exact implementation.",
  "definitions": "An object of important term-to-definition pairs relevant to the generated task, using concise definitions for concepts such as request lifecycle, transaction boundary, conflict response, stale data, idempotency, query shape, or accessibility when applicable.",
  "hints": "A single line hint nudging the candidate toward investigating cross-layer state, request timing, backend consistency, and observable behavior without naming the exact fix or giving away the implementation.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable full-stack correctness, predictable API behavior, improved user experience, maintainable code, and production-grade reliability. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed to complete the task, including React.js, Node.js, PostgreSQL, Docker, Docker Compose, REST APIs, async JavaScript, browser developer tools, and advanced full-stack debugging concepts.",
  "short_overview": "A bullet list summarising the business problem, the technical full-stack focus across React.js and Node.js, and the expected outcome after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **code_files must include README.md, .gitignore, package.json, docker-compose.yml, Dockerfile, run.sh, kill.sh, init_database.sql, backend source files, frontend source files, and any focused supporting files needed for the scenario.**
3. **Deployment must succeed in one go** — PostgreSQL must initialize, the Node.js API must connect, and the React.js frontend must be reachable.
4. **docker-compose.yml must NOT have a `version:` field.**
5. **MUST NOT include environment variables or .env file references** in any generated infrastructure or application code.
6. **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for PostgreSQL and exposed application ports.
7. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
8. **kill.sh must follow the exact cleanup pattern specified above** and must be idempotent.
9. **Task must be completable within {minutes_range} minutes** for ADVANCED proficiency.
10. **NO comments in code** that reveal the solution or give hints.
11. **Starter code must be runnable and FULLY FUNCTIONAL** but must not contain the core logic solution.
12. **Starter code must perfectly match the Current Implementation** described in the question.
13. **README.md must use exactly these section names in order**: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.
14. **README.md must not include setup commands, database connection details, direct solutions, implementation guides, or specific APIs/method names that reveal the solution.**
15. **Focus on advanced React.js and Node.js full-stack concepts** including correctness, performance, maintainability, resilience, security, and production-quality behavior.
16. **Use the provided real-world scenario as the basis for this task** and do not invent a different domain.
"""

PROMPT_REGISTRY = {
    "NodeJs (ADVANCED), ReactJs (ADVANCED)": [
        PROMPT_NODEJS_REACT_ADVANCED_CONTEXT,
        PROMPT_NODEJS_REACT_ADVANCED_INPUT_AND_ASK,
        PROMPT_NODEJS_REACT_ADVANCED_INSTRUCTIONS,
    ],
}