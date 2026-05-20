PROMPT_NODEJS_POSTGRESQL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_NODEJS_POSTGRESQL_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js and PostgreSQL assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, API/data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Node.js + PostgreSQL implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_POSTGRESQL_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Node.js application development and PostgreSQL-backed REST APIs, you are given a list of real world scenarios and proficiency levels for Node.js and PostgreSQL.
Your job is to generate a complete assessment task definition so that a candidate is presented with a working Node.js + PostgreSQL application that has a limited, well-scoped set of missing functionality or logical issues requiring BASIC-level full-stack backend skills.

The candidate should work on an existing application rather than designing a system from scratch. The task must assess practical ability with:
- basic Node.js and Express server development
- basic routing and request/response handling
- simple PostgreSQL schema usage and SQL queries
- connecting a Node.js app to PostgreSQL
- basic debugging and error handling
- small, realistic feature completion or bug fixing

## HARD SCOPE BOUNDARIES
You MUST stay within the competency scope.

### Node.js scope allowed
- JavaScript fundamentals
- Node.js setup and package management
- core modules where useful
- simple HTTP server concepts
- introductory Express.js usage
- basic routing
- callbacks and simple asynchronous operations
- JSON parsing/stringifying
- try/catch and callback error handling
- console-based debugging
- running apps locally and basic CLI usage

### Node.js scope not allowed as primary skill
- complex architecture design
- advanced async patterns
- Promises/async-await as the main assessment focus
- performance optimization as the main task theme
- advanced debugging
- security hardening
- advanced database integration patterns

### PostgreSQL scope allowed
- tables, schemas, constraints, primary/foreign keys
- basic and intermediate SQL queries
- joins, grouping, filtering, ordering, limit/offset
- INSERT/UPDATE/DELETE with RETURNING
- basic indexes
- transactions with BEGIN/COMMIT/ROLLBACK
- EXPLAIN / EXPLAIN ANALYZE at a simple level
- roles/privileges at a basic level if needed
- simple PL/pgSQL only if truly necessary
- pg_dump/restore concepts are allowed but should not be central

### PostgreSQL scope not appropriate as primary complexity escalator for this BASIC task
- advanced tuning as the main challenge
- complex locking/concurrency workflows
- advanced partitioning
- advanced security design
- deep operational DBA tasks as the main ask

## TASK CATEGORY REQUIREMENT: APP_AND_DB
The generated task MUST match APP_AND_DB structure:
- Docker-based setup
- PostgreSQL database container
- Node.js application container
- web framework app using Express.js
- no microservices
- no frontend application required

## PROFICIENCY REQUIREMENT: BASIC
This is a BASIC task for roughly 1-2 years of experience and should be completable in {minutes_range} minutes.

BASIC means:
- combine 2-3 concepts in one coherent task
- keep the feature or bug fix well-scoped
- provide enough starter code for a candidate to begin quickly
- avoid system design and advanced architecture
- avoid advanced concurrency, security hardening, and complex optimization
- do not turn the task into a DBA-heavy exercise

## TASK SHAPE
Generate a task where the candidate receives a FULLY RUNNABLE Express.js API connected to PostgreSQL, but one or more of the following are intentionally incomplete or logically incorrect:
- one or two API endpoints return mock data instead of database-backed results
- an endpoint writes incomplete or incorrect data to PostgreSQL
- a SQL query uses the wrong join/filter/order and needs correction
- pagination or filtering is expected but missing in a simple endpoint
- a transaction is needed for a small multi-step write flow but is not implemented correctly
- a foreign key / constraint / seed data relationship causes incorrect API behavior
- a route validates input only partially and causes bad inserts or updates

The task should feel like a realistic backend maintenance or feature-completion assignment for a small internal product.

## RECOMMENDED TASK THEMES
Choose ONE realistic business scenario inspired by the provided real-world scenarios. Good BASIC-level examples include:
- interview slot booking API
- support ticket assignment API
- training session registration API
- inventory restock request API
- meeting room reservation API
- simple order tracking API
- candidate assessment scheduling API

Keep the domain small and understandable.

## WHAT THE CANDIDATE SHOULD DO
The candidate should typically need to do a combination of the following:
- inspect existing Express routes and controller/service code
- connect one or two endpoints to PostgreSQL using a standard Node PostgreSQL driver
- fix a SQL query involving 2-3 tables max
- add or correct a simple schema constraint or index if needed
- ensure API responses are correct and consistent JSON
- handle basic invalid input and not-found cases
- verify behavior using the running API and database

## WHAT THE TASK MUST NOT BECOME
Do NOT generate a task centered on:
- advanced performance tuning
- caching
- message queues
- background jobs
- WebSockets
- authentication/authorization systems
- rate limiting
- distributed systems
- complex migrations framework design
- advanced ORM abstractions
- async/await mastery as the core challenge
- large-scale architecture decisions

## INFRASTRUCTURE REQUIREMENTS
The output task definition must require these files in the generated JSON:
- README.md
- .gitignore
- package.json
- docker-compose.yml
- Dockerfile
- run.sh
- kill.sh
- init_database.sql
- src/server.js
- src/app.js
- src/db.js
- src/routes/index.js
- src/routes/bookings.js or another domain-appropriate route file
- src/controllers/ or src/services/ files as needed
- optionally a small src/utils/ file

The application must be runnable in Docker and already wired to PostgreSQL.

## DOCKER-COMPOSE REQUIREMENTS
- MUST include a PostgreSQL service and a Node.js app service
- MUST NOT include a version field
- MUST NOT use .env files or environment variable references
- Use hardcoded credentials and connection values
- PostgreSQL should initialize automatically by mounting init_database.sql into /docker-entrypoint-initdb.d/
- Expose PostgreSQL on 5432 and app on a reasonable port such as 3000 or 5000
- Node.js service should depend on PostgreSQL
- Keep the setup simple and deterministic

## DOCKERFILE REQUIREMENTS
- Use a suitable Node.js image such as node:18-alpine
- Set WORKDIR to /root/task
- Install dependencies from package.json
- Expose the API port
- Start the app with npm start or node src/server.js
- No environment variable dependency

## RUN.SH REQUIREMENTS
- Start services with docker-compose up -d
- Wait until PostgreSQL is ready
- Validate that the API is responding
- Print clear progress logs
- Handle failures clearly
- Assume all files live under /root/task

## KILL.SH REQUIREMENTS
- Stop and remove containers, volumes, and networks created by docker-compose
- Remove related images where appropriate
- Run docker system prune -a --volumes -f
- Delete /root/task
- Use || true where needed so cleanup is idempotent
- Print logs for each step
- Use set -e at the top except where errors are intentionally ignored

## DATABASE REQUIREMENTS
The PostgreSQL database should be realistic but small enough for a BASIC task.

### init_database.sql should:
- create 2-4 tables
- include primary keys and foreign keys
- include realistic seed data
- include at least one intentionally missing or suboptimal piece that supports the task, such as:
  - a missing foreign key index
  - a nullable column that should be validated by the app flow
  - a query-relevant column without an index
  - seed data that exposes a join/filter bug
- avoid giving away the solution in comments
- keep SQL valid and executable

The schema should support straightforward SQL work only.

## NODE.JS APP REQUIREMENTS
Use Express.js in an introductory/basic way.

The app should include:
- app setup with express.json()
- basic route registration
- simple controller/service separation if useful
- PostgreSQL connection helper using a standard driver such as pg
- JSON responses
- basic error handling middleware or route-level try/catch

The code should be valid and runnable, but the core task area should remain incomplete or incorrect in a way that the candidate must fix.

## STARTER CODE REQUIREMENTS
- The starter code must be executable
- Do NOT leave the project empty
- Do NOT provide the full solution to the task
- Do NOT include comments that reveal the exact fix
- Do NOT include TODO comments that directly explain the implementation
- The bug or missing feature must be logical, not syntactic
- The candidate should be able to understand the project quickly within a few minutes

## README.md STRUCTURE
The README.md MUST contain these sections in this order:
1. Task Overview
2. Helpful Tips
3. Database Access
4. Objectives
5. How to Verify

### Task Overview
Write 2-3 substantial sentences describing the business scenario and the current state of the API. Make clear that the application is already running but some API behavior and database-backed functionality are incomplete or incorrect. Keep it specific to the chosen domain.

### Helpful Tips
Provide practical guidance without revealing the implementation.
Use concise bullets starting with:
- Consider
- Think about
- Explore
- Review

Guide the candidate toward inspecting routes, SQL queries, request payloads, and table relationships, but do not state the exact fix.

### Database Access
Provide:
- host as <DROPLET_IP>
- port
- database name
- username
- password
- mention that tools like psql, pgAdmin, or DBeaver may be used

### Objectives
List measurable outcomes such as:
- correct API responses from PostgreSQL-backed endpoints
- correct handling of invalid input or missing records
- correct join/filter/pagination behavior where relevant
- data consistency for create/update flows
- maintainable Node.js code and valid SQL changes

### How to Verify
Describe observable checks such as:
- calling specific endpoints and confirming expected JSON shape
- confirming rows are inserted/updated correctly in PostgreSQL
- checking that filters or pagination behave correctly
- optionally using EXPLAIN for a simple query if relevant, but do not make this the main verification path

### README MUST NOT INCLUDE
- manual deployment instructions
- step-by-step implementation guidance
- direct code solutions
- exact SQL fixes
- phrases like "add this code" or "create this exact query"

## AI AND EXTERNAL RESOURCE POLICY
Candidates are allowed to use external resources, documentation, Stack Overflow, and AI tools. The task should still require real understanding of basic Node.js and PostgreSQL concepts and should not be solvable by trivial copy-paste alone.

## REQUIRED OUTPUT JSON STRUCTURE
{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable title in '<action verb> <subject>' format",
  "question": "Short description of the business scenario and the specific Node.js + PostgreSQL fix or feature the candidate must complete",
  "code_files": {
    "README.md": "Candidate-facing README with the required sections",
    ".gitignore": "Node.js, Docker, and PostgreSQL exclusions",
    "package.json": "Dependencies and scripts for the Express app",
    "docker-compose.yml": "PostgreSQL + Node.js app services with hardcoded values and no version field",
    "Dockerfile": "Docker configuration for the Node.js app",
    "run.sh": "Deployment and validation script",
    "kill.sh": "Cleanup script",
    "init_database.sql": "Schema and seed data for PostgreSQL",
    "src/server.js": "Server entry point",
    "src/app.js": "Express app setup",
    "src/db.js": "PostgreSQL connection helper using pg",
    "src/routes/index.js": "Route registration",
    "src/routes/domain.js": "Domain routes",
    "src/controllers/domainController.js": "Controller logic with one or more incomplete or incorrect handlers",
    "src/services/domainService.js": "SQL access layer with one or more incomplete or incorrect queries"
  },
  "outcomes": "Bullet-point list in simple language. Must include: 'Build or fix a Node.js + PostgreSQL API flow by connecting Express endpoints to PostgreSQL with correct SQL queries, request handling, and consistent JSON responses' and 'Write production-level clean code with best practices including proper error handling, naming conventions, basic schema usage, and maintainable route/service structure'",
  "short_overview": "Bullet-point list in simple language describing the business problem, the backend/API task, and the expected outcome",
  "pre_requisites": "Bullet-point list of tools and knowledge required. Include Node.js 18+, npm, Docker, Docker Compose, PostgreSQL client tools, basic SQL, Express basics, JSON APIs, and Git",
  "answer": "High-level solution approach describing how the candidate would inspect the routes, fix the SQL/database interaction, and verify correct API behavior",
  "hints": "A single line hint that gently nudges the candidate toward checking route logic, SQL joins/filters, and how request data maps to the database without giving away the exact fix",
  "definitions": {
    "Express.js": "A minimal Node.js web framework used to build HTTP APIs and route requests",
    "Route": "A mapping between an HTTP request path/method and the code that handles it",
    "Foreign key": "A database constraint that links a column in one table to a primary key in another table",
    "JOIN": "A SQL operation used to combine rows from multiple tables based on a related column",
    "Transaction": "A sequence of database operations that succeed or fail as one unit"
  }
}

## FINAL QUALITY RULES
- Output must instruct generation of valid JSON only
- The generated task must be realistic, specific, and bounded
- Keep the number of tables and endpoints small
- Keep the Node.js app simple and Express-based
- Keep PostgreSQL work practical and not DBA-heavy
- Ensure the task is completable within {minutes_range} minutes
- Use the provided company context, role context, competencies, and one selected scenario to shape the task
- Do not copy any reference prompt content verbatim; adapt structure only
"""

PROMPT_REGISTRY = {
    "NodeJs (BASIC), PostgreSQL (BASIC)": [
        PROMPT_NODEJS_POSTGRESQL_BASIC_CONTEXT,
        PROMPT_NODEJS_POSTGRESQL_BASIC_INPUT_AND_ASK,
        PROMPT_NODEJS_POSTGRESQL_BASIC_INSTRUCTIONS,
    ]
}