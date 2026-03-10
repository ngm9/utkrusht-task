PROMPT_NODEJS_POSTGRESQL_INPUT_AND_ASK = """
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

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of database schema design and Node.js integration required, the expected deliverables, and how it aligns with the given PostgreSQL and Node.js proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_POSTGRESQL_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_NODEJS_POSTGRESQL_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in PostgreSQL database design, administration, and Node.js integration, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate an entire task definition, including code files (complete REST API structure using Node.js Express), database schema, Docker setup, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve database-related problems end to end.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL Node.js Express application with complete REST API endpoints. The Node.js application includes:
- Complete REST API endpoints with business logic implemented
- Express server setup with middleware and error handling
- All necessary route handlers and response formatting
- Basic application structure and configuration

However, the application will NOT have:
- Database connection implementation
- Database schema design
- Database integration in the API endpoints
- Any ORM/database models or schemas

The candidate's responsibility is:
- Writing PostgreSQL queries from scratch
- Designing/optimizing database schema from scratch
- Implementing database connection in Node.js
- Integrating database operations into existing API endpoints
- Using provided database credentials to connect via database client tools
- Modifying Node.js endpoints to work with their designed database schema

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement database schemas from scratch and integrate with Node.js endpoints
- **CRITICAL**: The Node.js application should have COMPLETE API endpoints but NO database integration - candidates must implement database connection and integration from scratch.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a complete, working Node.js Express application with endpoints that currently return mock/placeholder data, but requires the candidate to design database schema and integrate it from scratch.
- DO NOT GIVE AWAY THE SOLUTION IN THE DATABASE SCHEMA - provide empty schema.sql file.
- DO NOT include any database models, schemas, or connection code in the Node.js application.
- A part of the task completion is to watch the candidate implement PostgreSQL best practices and design the database schema correctly from scratch, then integrate it with Node.js.
- The question should be a real-world business scenario requiring database schema design AND Node.js database integration.
- The complexity of the task and specific ask expected from the candidate must align with the proficiency level required in the competency definition, ensuring that no two questions generated are similar. 
- For BEGINNER and BASIC and INTERMEDIATE levels of proficiency, the questions must be more specific and less open ended. The scenarios must focus on simple schema design (basic tables, simple relationships, primary/foreign keys) and basic database integration.
- For ADVANCED and EXPERT levels of proficiency, the questions must be more open ended and require complex schema design (complex relationships, normalization, indexing strategies, constraints, views) and advanced database integration patterns.
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions. Strictly avoid using outdated PostgreSQL features or syntax.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens).Examples like "node-postgres-optmization-api","dashboard-dataleak-fix".


## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, Node.js documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt PostgreSQL solutions with Node.js to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine database engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided , create a PostgreSQL + Node.js task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for proficiency level and years of experience given as input, keeping in mind that AI assistance is allowed.
- Tests practical PostgreSQL schema design skills AND Node.js database integration that require understanding of business requirements and database design principles.
- Time constraints: Each task should be finished within 30-40 minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Do not provide any of the comments in the file giving the solution or instructions to the candidate
- Not to provide the solution or direct or indirect hint for any of the implementation in the files
- Any Comments or TODO in the code do not give away the solution or hint for the implementation

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Node.js Express that currently returns mock data
- MUST include a Dockerfile for the Node.js application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Node.js Express REST API and a docker for running the PostgreSQL db.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and database connection.

### Run.sh Instructions:
  + Starts Docker containers using docker-compose up
  + Waits for PostgreSQL service to be fully ready and accepting connections before proceeding
  + Executes schema.sql file (initially empty - candidate will populate) to create tables, relationships, indexes, and constraints
  + Executes sample_data.sql file (initially empty - candidate will populate) to insert sample data into tables
  + **CRITICAL**: Only handles SQL file execution AFTER containers are running - does NOT duplicate container startup
  + Creates database users and roles that candidates can use to connect via database client tools
  + Validates that Node.js application is responding 
  + **IMPORTANT**: The run.sh script orchestrates the complete setup by first starting containers, then executing database setup
  + **LOCATION**: All files are located in /root/task directory, ensure Docker paths reference this location

### Docker-compose Instructions:
  - PostgreSQL service with proper configuration (database, username, password)
  - Node.js service with dependency on PostgreSQL using depends_on
  - Volume mounts for data persistence (PostgreSQL data directory)
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include any environment variables or .env file references**
  - **MUST NOT execute SQL files or database initialization in docker-compose**
  - **MUST include a valid Dockerfile** that will be used by the docker-compose.yml file to run the Node.js application
  - Use hardcoded configuration values instead of environment variables
  - For user and password, use hardcoded values in the docker-compose.yml file
  - PostgreSQL service should only start the database server, NOT execute schema files
  - Nodejs service should start and database should be connected to the node service 
  - both the services should start properly during droplet 
  - **CRITICAL**: Docker-compose only handles container orchestration, SQL execution happens via run.sh

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile for the Node.js application
  - Should use appropriate Node.js base image (node:18-alpine or similar)
  - Should install dependencies from package.json
  - Should expose appropriate port for Express server
  - Should include proper working directory set to /root/task
  - Should include proper entry point
  - Must be production-ready and follow Docker best practices
  - **DO NOT use environment variables or .env files**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location

## kill.sh file instructions:

- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.  
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes (Postgres volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (nodejs_app and postgres:15-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, schema.sql, sample data, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'nodejs_app|postgres:15-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Node.js files (`node_modules`, `.npm`, `*.log`) are also removed if present in `/root/task/`.
  - Remove all PostgreSQL data directories that were mounted via volumes (e.g., `/root/task/data/pgdata`).
  - Ensure that both the custom Node.js container and the postgres container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

## Starter Code Instructions:
- **CRITICAL**: The Node.js application should have COMPLETE API endpoints with mock/placeholder data responses, but NO database integration.
- **NO DATABASE CONNECTION**: Do not include any database connection setup, models, or schemas in the Node.js code.
- **NO ORM USAGE**: Do not include Sequelize, Prisma, TypeORM, or any other ORM setup. Candidates will implement raw SQL queries.
- All Express routes should be implemented and working with mock data, ready for database integration.
- The Node.js application should return realistic mock responses that give candidates hints about the expected data structure.
- Candidates need to design database schema, implement database connection, and integrate it with existing endpoints.
- The code files generated must be valid and executable Node.js code.
- **CRITICAL**: The Node.js application should run successfully but return mock data until candidates integrate the database.
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: Only starts containers and handles service dependencies
  - run.sh: Executes SQL files after containers are running to avoid conflicts
  - Node.js app: Should initially work with mock data and be ready for database integration
- DO NOT include any 'TODO' or placeholder comments that give away database integration hints
- DO NOT include any database connection libraries in package.json initially
- The Node.js application should be immediately runnable with mock data responses.
- **DATABASE DESIGN**: Schema design and database integration is candidate's responsibility - SQL files start empty
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Have a sensible gitignore suited for PostgreSQL and Node.js tasks:
- node_modules/
- npm-debug.log*
- yarn-debug.log*
- yarn-error.log*
- .env
- .env.local
- .env.development.local
- .env.test.local
- .env.production.local
- .npm
- .eslintcache
- .nyc_output
- coverage/
- build/
- dist/
- *.tgz
- *.tar.gz
- .DS_Store
- *.log
- data/pgdata/
- postgres_data/
- *.swp
- *.swo
- *~
- .vscode/
- .idea/

## README.md STRUCTURE (Node.js + PostgreSQL Basic)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the PostgreSQL + Node.js task scenario being generated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Helpful Tips
3. Database Access
4. Objectives
5. How to Verify

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario requiring database schema design from scratch and Node.js database integration. Explain that the API infrastructure is complete but currently returns mock data and has no database integration. State what database schema the candidate needs to design and how it should integrate with the Node.js API. Connect the business problem to the need for proper schema design and integration. The README.md file content MUST be fully populated with meaningful, specific content relevant to the PostgreSQL + Node.js task. ALL sections must have substantial content - no empty or placeholder text allowed.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider how to approach designing a database schema that fits the business scenario
- Think about what tables, relationships, and constraints the API endpoints will need
- Review which parts of the codebase currently return mock data and need database integration
- Explore key files or folders that define the API structure and expected data shape
- Consider that you need to design schema AND implement database connectivity in Node.js endpoints
- Think about coordination between SQL schema files and Node.js endpoint integration
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### Database Access

- Provide the database connection details (host (droplet-ip), port, database name, username, password)
- Mention that candidates can use any preferred database client tools (e.g., pgAdmin, DBeaver, psql)
- For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address

### Objectives

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate focusing on database schema design AND Node.js database integration
- What the candidate should achieve to complete the task successfully (schema from empty SQL files, integration in mock endpoints)
- Schema design objectives and Node.js integration objectives
- These objectives will be used to verify task completion and award points

**CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify

Verification approaches for schema design and Node.js integration:

- Call API endpoints and confirm responses return real database data (not mock data)
- Use a database client (pgAdmin, DBeaver, psql) to verify tables, relationships, and sample data exist
- Verify API response shape and values match the expected schema and business rules
- Test create/read/update flows through the API and confirm data persists in the database
- Check that schema constraints (e.g. foreign keys, unique, not null) are enforced
- Verify all relevant endpoints that previously returned mock data now use the database

**CRITICAL**: Focus on measurable, verifiable outcomes

### NOT TO INCLUDE:

- Manual deployment instructions (environment is automated via run.sh)
- Node.js implementation guides beyond database integration (API endpoints are already complete)
- Step-by-step database connection setup details (candidates must figure out integration approach)
- Instructions to run run.sh (deployment is automated)
- Pre-written schema, database models, or integration examples (candidates must implement from scratch)
- Step-by-step implementation instructions or exact code solutions or schema examples
- Phrases like "you should implement", "add the following code"

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "task-name-in-kebab-case",
   "question": "A short description of the task scenario including the specific business requirements that need a database schema designed from scratch AND integrated with existing Node.js API endpoints — what business problem needs to be solved through database design and Node.js integration?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview (MANDATORY 2-3 sentences), Helpful Tips (practical guidance without revealing implementations), Database Access (connection details and client tools), Objectives (outcomes for the task), and How to Verify (measurable verification approaches)",
      ".gitignore": "Proper Node.js, Docker, and PostgreSQL exclusions",
      "package.json": "Node.js dependencies (Express, basic middleware - NO database libraries initially)",
      "docker-compose.yml": "Docker services for PostgreSQL and Node.js (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for Node.js application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "src/app.js": "Complete Express application setup with middleware",
      "src/server.js": "Server startup configuration",
      "src/routes/index.js": "Main route file importing all API routes",
      "src/routes/api.js": "Complete API route implementations with mock data responses (NO database integration)",
      "src/middleware/errorHandler.js": "Error handling middleware",
      "src/controllers/controller.js": "Controller functions with mock data (ready for database integration)",
      "schema.sql": "EMPTY FILE - Candidate will write database schema with tables, relationships, indexes, and constraints",
      "data/sample_data.sql": "EMPTY FILE - Candidate will write sample data insertion scripts"
  }},
  "outcomes": "Bullet-point list in simple language. Must include: 'Design and implement PostgreSQL database schema from scratch following best practices (tables, relationships, indexes, constraints) and integrate with Node.js API' and 'Write production-level clean code with best practices including proper error handling, naming conventions, schema design principles, and Node.js database integration patterns'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business problem requiring database design and Node.js integration, (2) the specific goal (schema from scratch + API integration), and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task. Mention things like Node.js 18+, npm, Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver), Git, basic knowledge of SQL and Node.js, etc.",
  "answer": "High-level solution approach focusing on database schema design principles, Node.js database integration patterns, and data modeling approach for the given business requirements",
  "hints": "A single line Hint on what a good approach to solve the database schema design and Node.js integration task could include. These hints must NOT give away the answer, but gently nudge the candidate toward good database design principles and integration patterns.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
    }}
}}
"""
PROMPT_REGISTRY = {
    "NodeJs, PostgreSQL": [
        PROMPT_NODEJS_POSTGRESQL_CONTEXT,
        PROMPT_NODEJS_POSTGRESQL_INPUT_AND_ASK,
        PROMPT_NODEJS_POSTGRESQL_INSTRUCTIONS,
    ]
}
