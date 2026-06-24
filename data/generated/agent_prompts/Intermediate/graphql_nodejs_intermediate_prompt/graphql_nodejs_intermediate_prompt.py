# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GRAPHQL_NODEJS_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how GraphQL is used in Node.js-based API systems at an intermediate level — such as schema design, resolver implementation, authorization through context, database-backed nested fields, query validation, batching/caching, and production-grade API reliability?
"""

PROMPT_GRAPHQL_NODEJS_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a GraphQL and Node.js assessment task.

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

PROMPT_GRAPHQL_NODEJS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in GraphQL, Apollo Server, Node.js, and database-backed API architecture, you are given a list of real world scenarios and proficiency levels for GraphQL + Node.js development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Node.js GraphQL API application that is already connected to PostgreSQL and exposes a working `/graphql` endpoint. The PostgreSQL database must be FULLY POPULATED with realistic seed data relevant to the selected business scenario.

The Node.js application includes:
- A working Apollo Server or graphql-js based GraphQL endpoint with SDL schema files, resolver modules, repository/data-access modules, context creation, logging, and tests
- Existing queries, mutations, nested resolvers, and database-backed data access that partially work but contain realistic intermediate-level issues
- A FULLY FUNCTIONAL local infrastructure setup with Docker Compose, PostgreSQL initialization, application containerization, and readiness scripts
- Existing integration or resolver tests that demonstrate current behavior and give the candidate a reliable way to verify improvements after implementation

The candidate's responsibility is to fix or extend the GraphQL API according to the task requirements while preserving backward compatibility for existing clients where appropriate. A part of the task completion is to watch the candidate apply GraphQL and Node.js best practices, design the solution correctly, demonstrate proper resolver architecture, handle errors safely, and not just make superficial changes.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a focused feature, refactor an existing schema/resolver flow, or fix complex bugs in the existing GraphQL Node.js codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors or add features hastily.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years GraphQL and Node.js experience), ensuring that no two questions generated are similar.
- **CRITICAL TIME BUDGET**: The total task time is {minutes_range} minutes. The candidate needs time to inspect the schema, run the app, and verify behavior, so the actual implementation work must be focused and achievable by an intermediate-level developer with AI assistance allowed.
- **CRITICAL SCOPE**: Keep the candidate task to 2-3 focused objectives. Do not require a full platform rewrite, a complete federation migration, a production gateway rollout, or expert-level subscription infrastructure.
- **CRITICAL**: The task must stay within intermediate GraphQL + Node.js expectations:
  - Defining and maintaining SDL schemas with object types, interfaces, enums, unions, input types, custom scalars, descriptions, and deprecations
  - Refactoring or extending schemas without breaking existing clients
  - Implementing field-level and nested resolvers with safe parent-child resolution
  - Integrating resolvers with PostgreSQL repositories, REST adapters, or internal service modules
  - Applying resolver-level authentication and authorization using request context
  - Preventing N+1 query behavior with batching/caching style approaches when the selected scenario naturally requires it
  - Returning meaningful GraphQL errors with appropriate extensions codes such as `BAD_USER_INPUT`, `FORBIDDEN`, or `QUERY_TOO_COMPLEX`
  - Applying input validation, safe filter mapping, limit enforcement, query depth awareness, and structured logging for rejected operations
  - Writing or updating Jest integration tests for schema behavior, resolver behavior, authorization, and error responses
- For INTERMEDIATE level, the scenarios should require practical design judgment and involve:
  - One Node.js GraphQL API service with a realistic modular structure
  - PostgreSQL-backed repositories with seeded scenario data
  - A schema/resolver issue that impacts API correctness, security, performance, or backward compatibility
  - Existing tests or test scaffolding that candidates can extend
  - Clear expected behavior that can be verified through GraphQL operations and test output
- The task should NOT require advanced Apollo Federation ownership, deep schema stitching across many services, production-grade real-time subscriptions, distributed tracing platforms, or expert-level query planning.
- The question must NOT include hints. The hints will be provided in the `"hints"` field.
- Ensure that all questions and scenarios adhere to modern Node.js best practices using Node.js 18+ and async/await patterns.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, GraphQL documentation, Apollo Server documentation, Node.js documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate GraphQL and Node.js proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution for schema design, resolver behavior, data access, security, and maintainability.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a GraphQL + Node.js task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years GraphQL and Node.js experience), keeping in mind that AI assistance is allowed
- Tests practical GraphQL API work that requires schema judgment, resolver design, error handling, authorization, performance awareness, and Node.js maintainability
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- Focus on one cohesive GraphQL API where the candidate fixes or extends schema and resolver behavior against a PostgreSQL data source
- The task environment must use Docker Compose to run PostgreSQL and the Node.js GraphQL API
- The starter app should be FULLY FUNCTIONAL and bootable, but intentionally incomplete or flawed in the specific area being assessed
- Do NOT make the task about building a GraphQL server from scratch unless the selected scenario is extremely small; intermediate signal should come from improving a realistic existing API

## Infrastructure Requirements
- MUST include a complete, fully functional Node.js GraphQL API structure using Apollo Server or graphql-js that integrates with PostgreSQL
- MUST include a Dockerfile for the Node.js GraphQL application
- MUST include a docker-compose.yml file containing the Node.js application service and PostgreSQL service
- MUST include init_database.sql to create tables and seed realistic data for the selected scenario
- MUST include run.sh that deploys the infrastructure and validates readiness without running the grader test suite
- MUST include kill.sh that completely cleans up the environment
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, all containers must start successfully, PostgreSQL must be ready, the database must be initialized, the GraphQL API must respond to a health or introspection-safe check, and deployment must NOT fail.
- run.sh is a READINESS/self-check, NOT the grader. It brings the datastore and app up, waits for health, verifies the starter compiles/loads with the runtime's build or import command, then exits 0 on the UNSOLVED starter. It MUST NOT run the grader test suite because those tests may be designed to fail until the candidate solves the task.

### Docker-compose Instructions
- Must include a PostgreSQL service and a Node.js GraphQL API service.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- Use hardcoded configuration values or inline service environment values only; do not use `.env` files and do not use `${{VAR}}` host indirection.
- PostgreSQL service MUST set the standard initialization environment variables inline in `environment:`:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- The init SQL, healthcheck, and Node.js database connection string must use the same PostgreSQL user and database.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- The Node.js API port should also be bound to localhost where practical, for example `127.0.0.1:4000:4000`.
- PostgreSQL healthcheck must use `pg_isready` with the same user and database configured in the inline environment.
- Node.js service must depend on PostgreSQL health using `depends_on` with a service health condition.
- Use named volumes for PostgreSQL persistence.
- Mount init_database.sql into `/docker-entrypoint-initdb.d/` so PostgreSQL initializes automatically.
- Do not rely on manual database setup commands after compose starts.
- Do not use host-mounted application source volumes that overwrite container `node_modules`.
- The compose setup must be able to build and run from `/root/task`.

### init_database.sql Instructions
- Must create a realistic PostgreSQL schema and seed data that directly supports the selected GraphQL scenario.
- The database must be FULLY POPULATED with enough realistic rows to expose the bug, security issue, schema evolution concern, validation issue, or performance issue being assessed.
- Use clear table names and columns that match the business domain selected from the real-world scenario.
- Include relationships needed for nested GraphQL resolvers, such as parent-child records, ownership fields, tenant/clinic/account identifiers, statuses, or sortable/filterable fields when relevant.
- Do not implement the candidate's solution in SQL. The seed data should expose the issue but not fix it.
- If the scenario involves authorization, seed at least two tenants, clinics, users, accounts, or organizations so both allowed and denied paths are testable.
- If the scenario involves query performance, seed enough related rows for inefficient nested resolver behavior or overly broad queries to be observable in tests or logs.
- Keep SQL deterministic and idempotent for container initialization.

### Run.sh Instructions
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- MUST `cd /root/task` first.
- FIRST step after changing directory MUST install project dependencies using `npm ci`.
- Run a non-grader readiness build or load check such as `npm run build` if a build script exists, or `node --check` / an import smoke check for the application entry point.
- Run `docker compose -f /root/task/docker-compose.yml up -d --build` to start all services.
- Include a health check loop that waits for PostgreSQL to be ready.
- Include a health check loop that waits for the GraphQL API to respond on its local endpoint.
- Validate readiness with a lightweight health endpoint or a simple GraphQL operation that works on the starter code and does not depend on the candidate's unfinished solution.
- If any check fails after retries, print `docker compose` logs and exit with code 1.
- End with a clear success message showing the local GraphQL API URL.
- Do NOT run `npm test`, Jest, integration tests, or any grader-oriented failing test suite inside run.sh.

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, Dockerfile, and init_database.sql.
- Instructions:
  1. Stop and remove all containers created by docker compose.
  2. Remove all associated Docker volumes, including PostgreSQL named volumes and anonymous volumes.
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task, including the Node.js application image and postgres image if present.
  5. Run `docker system prune -a --volumes -f` to remove dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed by using `|| true` where necessary.
  8. Print logs at every step, such as "Stopping containers...", "Removing volumes...", "Removing images...", and "Deleting folder...", so the user knows what is happening.
  9. After successful cleanup, print a final message exactly like "Cleanup completed successfully! Droplet is now clean."
- Commands that should be included:
  - `cd /root/task || true`
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker stop $(docker ps -q) || true`
  - `docker rm -f $(docker ps -aq) || true`
  - `docker volume prune -f || true`
  - `docker network prune -f || true`
  - `docker rmi -f $(docker images -q | grep -E 'graphql|node|postgres' || true) || true`
  - `docker image prune -a -f || true`
  - `docker system prune -a --volumes -f || true`
  - `rm -rf /root/task || true`
- Dependencies cleanup:
  - Ensure that cached Node.js files such as `node_modules`, `*.log`, `.npm`, `.node-gyp`, coverage output, and build artifacts are removed if present in `/root/task/`.
  - Remove any PostgreSQL data directories or mounted volumes used by the task.
  - Ensure that both the custom application container and the PostgreSQL container are cleaned up.
- Extra instruction:
  - The script should be idempotent and safe to run multiple times without errors.
  - Always use `set -e` at the top to exit on error except when explicitly ignored with `|| true`.
  - Print "Cleanup completed successfully!" as part of the final cleanup message.

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the Node.js GraphQL application.
- Use `node:18-alpine` or a compatible Node.js 18+ base image.
- Set WORKDIR to `/root/task` to match the file location.
- Copy package.json and package-lock.json before installing dependencies.
- Install dependencies using `npm ci`.
- Copy the application source files after dependency installation.
- Expose the GraphQL API port, typically 4000.
- Start the application with a package script such as `npm start`.
- Do not rely on `.env` files.
- Use Docker best practices and avoid copying local `node_modules` into the image.
- **CRITICAL**: Set WORKDIR to `/root/task` to match the file location.

The output should be a valid json schema:
- `README.md` with concise candidate-facing task context and verification guidance
- `.gitignore` with Node.js, Docker, PostgreSQL, logs, environment, IDE, and coverage exclusions
- `package.json` and `package-lock.json` for Node.js dependencies and scripts
- `docker-compose.yml` for PostgreSQL and the Node.js GraphQL API with no version field
- `Dockerfile` for the Node.js GraphQL API
- `run.sh` for readiness deployment and self-checks
- `kill.sh` for complete cleanup
- `init_database.sql` for PostgreSQL schema and seed data
- `src/` files for schema, resolvers, context, repositories, validation, errors, logging, and server startup
- `tests/` files for Jest resolver or integration tests that candidates can run separately

## Code file requirements
- Generate a realistic GraphQL + Node.js folder structure such as `src/schema/`, `src/resolvers/`, `src/repositories/`, `src/context/`, `src/errors/`, `src/utils/`, `src/server.js`, `src/app.js`, and `tests/`.
- Code should follow modern Node.js best practices using Node.js 18+, async/await, clear module boundaries, and structured error handling.
- Use Apollo Server, graphql-js, or a comparable GraphQL server library appropriate for Node.js.
- Use PostgreSQL access through `pg`, a lightweight query layer, or an ORM only if it fits the selected scenario. Do not add unnecessary frameworks.
- Include SDL schema files or schema modules with realistic descriptions and deprecations where relevant.
- Include resolver modules with enough existing behavior to make the app runnable.
- Include repository/data-access modules that demonstrate the current flawed or incomplete behavior without revealing the fix.
- Include context creation that can represent authenticated users in a deterministic local way, such as test headers or seeded users, without requiring external identity providers.
- Include Jest tests or integration tests that candidates can run manually after implementation.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion.
- The core schema evolution decisions, resolver authorization checks, typed input validation, batching/caching strategy, query depth protection, safe SQL scoping, or logging improvements that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT include comments like "Add authorization here", "Use DataLoader here", "Add query depth validation", or "Map this input safely".
- DO NOT add comments that give away hints, solution, or implementation details.
- The generated project structure should be buildable and bootable with Docker Compose, but will require GraphQL and Node.js work to satisfy the task objectives and tests.
- Provide realistic dependencies in package.json that intermediate developers should be familiar with, such as GraphQL server libraries, PostgreSQL client libraries, logging libraries, and Jest testing utilities.
- Ensure generated starter code has logical issues or missing behavior, not syntax errors.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for Node.js, GraphQL, PostgreSQL, Docker, and testing projects including node_modules/, build outputs such as dist/ and build/, IDE configurations such as .idea/ and .vscode/, swap files, compiled files, environment files such as .env and .env.local, database files, log files such as *.log and logs/, Docker volumes, coverage reports such as .nyc_output/ and coverage/, npm caches, and common operating system artifacts.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

- The README.md contains exactly the following sections in this order and no others:
  1. Task Overview
  2. Helpful Tips
  3. Objectives
  4. How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content.
- Task Overview section MUST contain the exact business scenario from the task description.
- ALL sections must have substantial content - no empty or placeholder text allowed.
- Content must be directly relevant to the specific GraphQL + Node.js task scenario being generated.
- Use concrete business context, not generic descriptions.
- The README must NOT contain `<DROPLET_IP>` placeholders or any database-connection details such as host, port, username, password, or client-tool suggestions.
- The README must NOT include setup commands or deployment instructions.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences.
- Use no bullet list in this section.
- Describe the business scenario, current state, and why the problem matters.
- NEVER generate empty content.
- Do not include bold time-budget callouts.
- Explain why correct GraphQL API behavior matters for client reliability, data safety, performance, or schema maintainability.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Tips should guide the candidate toward GraphQL schema, resolver, context, validation, testing, security, and performance reasoning without prescribing how to solve the task.

### Objectives
- Objectives must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should be measurable and appropriate for intermediate GraphQL + Node.js proficiency.
- Focus on functional correctness, schema compatibility, secure resolver behavior, predictable errors, performance awareness, tests, and production-level code quality.
- Include one objective that evaluates clean, maintainable, production-level Node.js code quality without prescribing implementation details.

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run or observe, such as test output, GraphQL response shape, error code, authorization result, latency observation, or log line.
- These points should help the candidate verify their own work and help the assessor see how thoroughly they checked their implementation.
- Do not include setup commands, dependency installation commands, Docker commands, or database connection details.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
- Setup commands such as `npm install`, `npm ci`, `npm test`, `docker compose up`, `docker-compose up`, or similar commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database-connection details including host, port, username, password, database name, or client-tool suggestions
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", or "add this resolver"
- Specific GraphQL validation rules, resolver helper names, SQL clauses, batching utilities, or logging method names that reveal the solution

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that clearly describes the GraphQL and Node.js task without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, that is different from name and clearly communicates the GraphQL API work to be completed.",
  "question": "A detailed candidate-facing task description that explains the selected business scenario, the current GraphQL and Node.js behavior, the specific issue or feature to address, and the observable expectations without revealing the solution.",
  "code_files": {{
    "README.md": "Candidate-facing README containing exactly Task Overview, Helpful Tips, Objectives, and How to Verify with concise open-ended guidance.",
    ".gitignore": "Comprehensive exclusions for Node.js, GraphQL development, Docker artifacts, PostgreSQL data, logs, environment files, IDE files, and test coverage output.",
    "package.json": "Node.js package manifest with scripts for starting the GraphQL API, running non-grader readiness checks, and running tests separately, plus realistic dependencies for GraphQL, PostgreSQL, logging, and Jest.",
    "package-lock.json": "Lockfile content consistent with package.json so npm ci can install dependencies deterministically.",
    "docker-compose.yml": "Docker Compose configuration with no version field that starts PostgreSQL and the Node.js GraphQL API using localhost-bound ports, inline PostgreSQL initialization environment values, health checks, and named volumes.",
    "Dockerfile": "Dockerfile for the Node.js GraphQL API using a Node.js 18+ base image, /root/task working directory, deterministic dependency installation, and a production-style start command.",
    "run.sh": "Readiness script that installs dependencies first, performs a build or import smoke check, starts Docker Compose, waits for PostgreSQL and the GraphQL API to become healthy, prints logs on failure, and exits successfully without running grader tests.",
    "kill.sh": "Idempotent cleanup script that stops compose services, removes containers, volumes, networks, images, prunes Docker resources, deletes /root/task, prints progress at every step, and ends with the required cleanup success message.",
    "init_database.sql": "PostgreSQL initialization script that creates realistic scenario tables and deterministic seed data needed to expose the GraphQL resolver, schema, authorization, validation, or performance issue.",
    "src/server.js": "Node.js application entry point that starts the GraphQL server and exposes the configured API endpoint and readiness check.",
    "src/app.js": "GraphQL application assembly module that wires schema, resolvers, context, repositories, logging, and server configuration while leaving the assessed behavior for the candidate to complete.",
    "src/schema/typeDefs.js": "SDL schema definitions with realistic GraphQL types, inputs, enums, interfaces, unions, descriptions, or deprecations appropriate to the selected scenario.",
    "src/resolvers/index.js": "Resolver map with existing query, mutation, nested field, and error handling behavior that is runnable but contains the focused flaw or missing intermediate-level behavior.",
    "src/context/createContext.js": "Request context module that supplies deterministic user/session information and shared dependencies for resolver authorization and data access.",
    "src/repositories/database.js": "PostgreSQL connection and query helper module using async/await and safe connection management.",
    "src/repositories/exampleRepository.js": "Scenario-specific repository module with current data access behavior that supports the task and may require candidate refinement.",
    "src/errors/graphqlErrors.js": "GraphQL error helper module or equivalent structure for consistent error formatting without exposing sensitive details.",
    "src/utils/logger.js": "Structured logging utility used by the starter application and available for candidate improvements.",
    "tests/graphql.integration.test.js": "Jest integration or resolver tests that exercise current and expected GraphQL behavior, including success and failure paths relevant to the selected scenario.",
    "additional files": "Any additional schema, resolver, repository, fixture, test, or utility files needed to make the task realistic, runnable, and appropriately scoped."
  }},
  "answer": "Evaluator-facing high-level solution approach that describes the intended schema, resolver, authorization, validation, data access, error handling, testing, and observability changes without requiring exact code.",
  "definitions": {{
    "GraphQL Schema": "A typed contract that describes the queries, mutations, object types, inputs, enums, interfaces, unions, and fields available to API clients.",
    "Resolver": "A function responsible for returning data for a GraphQL field, often using parent values, arguments, context, and data sources.",
    "Context": "Per-request data made available to resolvers, commonly used for authenticated user information, shared services, logging, and database access.",
    "Nested Resolver": "A resolver for a field inside another GraphQL type that often depends on the parent object and can introduce correctness, authorization, or performance concerns.",
    "GraphQL Error Extensions": "Structured metadata attached to GraphQL errors that helps clients understand categories such as bad input, forbidden access, or overly complex operations.",
    "Schema Deprecation": "A non-breaking schema evolution technique that marks an existing field or argument as discouraged while guiding clients toward a safer replacement."
  }},
  "hints": "A single line hint nudging the candidate toward examining schema behavior, resolver boundaries, context usage, data access, and observable GraphQL responses without revealing the specific fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on correct GraphQL behavior, secure and maintainable Node.js resolver design, measurable verification through tests or responses, and production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability. Use simple english.",
  "pre_requisites": "Bullet-point list of tools and knowledge required, including Node.js 18+, npm, Docker, Docker Compose, GraphQL SDL, Apollo Server or graphql-js concepts, resolver implementation, PostgreSQL basics, async/await, Jest testing, authorization concepts, input validation, and structured logging.",
  "short_overview": "Bullet-point list summarising the business problem, the GraphQL and Node.js technical focus, and the expected outcome in simple language suitable for both technical reviewers and non-engineering stakeholders."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and different from `name`.
4. **code_files** must include README.md, .gitignore, package.json, package-lock.json, docker-compose.yml, Dockerfile, run.sh, kill.sh, init_database.sql, Node.js GraphQL source files, and tests.
5. **docker-compose.yml must NOT have a `version:` field**.
6. PostgreSQL compose configuration MUST use inline `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`; do not use `.env` files or `${{VAR}}` host indirection.
7. **SECURITY-CRITICAL**: datastore ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
8. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
9. **run.sh** must install dependencies first, start Docker Compose, wait for PostgreSQL and GraphQL API readiness, and must NOT run the grader test suite.
10. **kill.sh** must follow the exact cleanup pattern specified above and end with the required cleanup success message.
11. **README.md** must contain exactly Task Overview, Helpful Tips, Objectives, and How to Verify in that order, with no database access section and no setup commands.
12. **Starter code** must be runnable and FULLY FUNCTIONAL enough for readiness checks, but must NOT contain the solution.
13. **NO comments in code** that reveal the solution or give hints.
14. **Task must be completable within the allocated time** for INTERMEDIATE proficiency.
15. Focus on intermediate GraphQL + Node.js work: schema evolution, resolver correctness, nested authorization, safe inputs, error extensions, batching/caching awareness, query complexity awareness, logging, and tests.
"""

PROMPT_REGISTRY = {
    "GraphQL (INTERMEDIATE), NodeJs (INTERMEDIATE)": [
        PROMPT_GRAPHQL_NODEJS_CONTEXT_INTERMEDIATE,
        PROMPT_GRAPHQL_NODEJS_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_GRAPHQL_NODEJS_INTERMEDIATE_INSTRUCTIONS,
    ],
}