PROMPT_FASTAPI_POSTGRESQL_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI and PostgreSQL assessment task.

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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with the given Python FastAPI and PostgreSQL proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FASTAPI_POSTGRESQL_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_FASTAPI_POSTGRESQL_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in PostgreSQL database design, administration, and Python FastAPI integration, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate an entire task definition, including code files (complete REST API structure using Python FastAPI), database schema, Docker setup, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve database-related problems end to end.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL FastAPI application that is already connected to PostgreSQL database. The FastAPI application includes:
- Complete REST API endpoints with all business logic implemented
- Full database connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete SQLAlchemy models and Pydantic schemas

The candidate's ONLY responsibility is:
- Writing PostgreSQL queries from scratch
- Designing/optimizing database schema
- Implementing database-related optimizations
- Using provided database credentials to connect via database client tools
- NO changes to FastAPI code files are expected or required

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement database schemas from scratch and populate with sample data to make a functional application
- **CRITICAL**: The FastAPI application should be FULLY functional and ready to run - candidates should NOT need to implement FastAPI code. Their focus should be on PostgreSQL database schema design and data insertion only.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a complete, working FastAPI application that connects to PostgreSQL, but requires the candidate to design and populate the database schema from scratch.
- DO NOT GIVE AWAY THE SOLUTION IN THE DATABASE SCHEMA - provide empty schema.sql file.
- A part of the task completion is to watch the candidate implement PostgreSQL best practices and design the database schema correctly from scratch.
- The question should be a real-world business scenario requiring database schema design, NOT optimization or bug fixing.
- The complexity of the task and specific ask expected from the candidate must align with the proficiency level required in the competency definition, ensuring that no two questions generated are similar. 
- For BEGINNER and BASIC and INTERMEDIATE levels of proficiency, the questions must be more specific and less open ended. The scenarios must focus on simple schema design (basic tables, simple relationships, primary/foreign keys).
- For ADVANCED and EXPERT levels of proficiency, the questions must be more open ended and require complex schema design (complex relationships, normalization, indexing strategies, constraints, views).
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions. Strictly avoid using outdated PostgreSQL features or syntax.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt PostgreSQL solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine database engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided , create a PostgreSQL task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for proficiency level and years of experience given as input, keeping in mind that AI assistance is allowed.
- Tests practical PostgreSQL schema design skills that require understanding of business requirements and database design principles.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Python FastAPI that integrates with PostgreSQL
- MUST include a Dockerfile for the FastAPI application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Python FastAPI REST API and a docker for running the PostgreSQL db.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and database connection.

### Run.sh Instructions:
  + Starts Docker containers using docker-compose up
  + Waits for PostgreSQL service to be fully ready and accepting connections before proceeding
  + Executes schema.sql file (initially empty - candidate will populate) to create tables, relationships, indexes, and constraints
  + Executes sample_data.sql file (initially empty - candidate will populate) to insert sample data into tables
  + **CRITICAL**: Only handles SQL file execution AFTER containers are running - does NOT duplicate container startup
  + Creates database users and roles that candidates can use to connect via database client tools
  + Validates that FastAPI application is responding and connected to database
  + **IMPORTANT**: The run.sh script orchestrates the complete setup by first starting containers, then executing database setup
  + **LOCATION**: All files are located in /root/task directory, ensure Docker paths reference this location

### Docker-compose Instructions:
  - PostgreSQL service with proper configuration (database, username, password)
  - FastAPI service with dependency on PostgreSQL using depends_on
  - Volume mounts for data persistence (PostgreSQL data directory)
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include any environment variables or .env file references**
  - **MUST NOT execute SQL files or database initialization in docker-compose**
  - **MUST include a valid Dockerfile** that will be used by the docker-compose.yml file to run the FastAPI application
  - Use hardcoded configuration values instead of environment variables
  - PostgreSQL service should only start the database server, NOT execute schema files
  - FastAPI service should start the application but may need to handle database connection retries
  - **CRITICAL**: Docker-compose only handles container orchestration, SQL execution happens via run.sh

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile for the FastAPI application
  - Should use appropriate Python base image (python:3.11-slim or similar)
  - Should install dependencies from requirements.txt
  - Should expose appropriate port for FastAPI
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
  4. Force-remove all Docker images related to this task (bookstore_api and postgres:15-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, schema.sql, sample data, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'bookstore_api|postgres:15-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all PostgreSQL data directories that were mounted via volumes (e.g., `/root/task/data/pgdata`).
  - Ensure that both the custom application container and the postgres container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).


## Starter Code Instructions:
- **CRITICAL**: The FastAPI application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and database connection setup.
- **NO ORM USAGE**: Do not use SQLAlchemy ORM or any other ORM. Use raw SQL queries with database connection libraries like psycopg2.
- The database connection setup should use direct PostgreSQL connection, not ORM-based connections.
- All FastAPI routes should be implemented and working with the pre-populated database using raw SQL queries.
- The database should come with realistic sample data that candidates can work with, modify, or query.
- Candidates may need to optimize existing queries, modify schema design, fix performance issues, or implement additional database features.
- The code files generated must be valid and executable.
- If the task is to fix bugs, make sure the bug is in the database schema design, SQL queries, or database performance, NOT in the FastAPI code.
- If the task is to implement a feature, it should work with the existing database structure and data.
- **CRITICAL**: Ensure proper Python package structure with __init__.py files in all directories.


**CRITICAL**: All Docker and script references must account for the /root/task base directory.

# OUTPUT

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastapi, psycopg2-binary, uvicorn and other dependencies required - NO ORM libraries)
  - docker-compose.yml (PostgreSQL and FastAPI services configuration)
  - Dockerfile (MUST be included - Docker configuration for FastAPI app)
  - run.sh (Script to deploy and setup the complete environment)
  - kill.sh (Script to completely clean up all resources created by the task)
  - .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, data/)
  - All FastAPI code files following the project structure above
  - PostgreSQL schema files
  - **CRITICAL**: Include ALL __init__.py files for proper Python package structure

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP8 guidelines and PostgreSQL best practices
- **CRITICAL**: The FastAPI application files MUST be complete and fully functional with all endpoints, error handling, and database integration code.
- **NO ORM USAGE**: Use raw SQL queries with psycopg2 or similar PostgreSQL drivers
- **EMPTY SQL FILES**: schema.sql and data/sample_data.sql should be EMPTY files - candidates will write the database schema and insert sample data from scratch
- Database connection setup and FastAPI routes should use raw SQL queries and be ready to use.
- Tasks should focus on schema design and data insertion from scratch based on business requirements.
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: Only starts containers and handles service dependencies
  - run.sh: Executes SQL files after containers are running to avoid conflicts
  - FastAPI app: Should handle database connection retries and gracefully handle empty database initially
- DO NOT include any 'TODO' or placeholder comments in FastAPI code
- DO NOT include any comments that give away schema design hints or solutions
- The FastAPI application should be immediately runnable but will work with empty database until candidate populates schema and data.
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **DATABASE DESIGN**: Schema and data insertion is candidate's responsibility - SQL files start empty
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Have a sensible gitignore suited for PostgreSQL and FastAPI tasks:
- __pycache__/
- *.pyc
- *.pyo
- *.pyd
- .Python
- build/
- develop-eggs/
- dist/
- downloads/
- eggs/
- .eggs/
- lib/
- lib64/
- parts/
- sdist/
- var/
- wheels/
- *.egg-info/
- .installed.cfg
- *.egg
- .venv
- venv/
- ENV/
- env/
- .mypy_cache/
- .pytest_cache/
- .coverage
- htmlcov/
- .DS_Store
- *.log
- data/pgdata/
- postgres_data/
- *.swp
- *.swo
- *~

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Database Access
   - Objectives
   - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific PostgreSQL task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and aslo the why it is important to implement that scenarios  
NEVER generate empty content - always provide substantial business context that explains what database schema the candidate needs to design and why it matters for the business.

### Helpful Tips
  - Provide a clear explanation of how to effectively approach the task
  - Mention that the API infrastructure is complete but database schema and data are initially empty
  - Highlight key files or folders in the codebase that candidates should review before starting
  - Emphasize that FastAPI code is complete and candidates focus only on database schema design and data insertion
  - Ensure the explanation is always given in bullet points for clarity and ease of reading

  ### Database Access
    - Provide the database connection details (host(droplet-ip), port, database name, username, password)
    - Mention can use any preferred database client tools (eg:pgAdmin, DBeaver, psql)
    - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address
  

### Objectives
  - Clear, measurable goals for the candidate focusing on database schema design and data population
  - This is what the candidate should be able to do successfully to say that they have completed the task.
  - These objectives will also be used to verify the task completion and award points.
  - Should focus on schema design objectives and database population, starting from empty SQL files

### How to Verify
  - Specific checkpoints after database schema creation and data insertion
  - Observable behaviors or outputs to validate database functionality through the API
  - Should include testing schema design and data insertion through API endpoints
  - Include verification steps for both schema creation and data population

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - FastAPI implementation guides (API is already complete)
  - Step-by-step database connection setup (connection details are provided)
  - Instructions to run the run.sh file (deployment is automated)
  - Pre-written schema or data examples (candidates must write from scratch)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A short description of the task scenario including the specific business requirements that need a database schema designed from scratch — what business problem needs to be solved through database design and what tables/relationships need to be created?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Python, Docker, and PostgreSQL exclusions",
      "requirements.txt": "Python dependencies list including PostgreSQL drivers (NO ORM libraries)",
      "docker-compose.yml": "Docker services for PostgreSQL and FastAPI (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for FastAPI application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "app/__init__.py": "Empty file for Python package structure",
      "app/main.py": "Complete FastAPI application with all endpoints",
      "app/database.py": "Complete database connection configuration (NO ORM, raw SQL)",
      "app/routes/__init__.py": "Empty file for Python package structure",
      "app/routes/api.py": "Complete API route implementations with raw SQL queries",
      "app/schemas/__init__.py": "Empty file for Python package structure",
      "app/schemas/schemas.py": "Pydantic schemas for API requests/responses",
      "schema.sql": "EMPTY FILE - Candidate will write database schema with tables, relationships, indexes, and constraints",
      "data/sample_data.sql": "EMPTY FILE - Candidate will write sample data insertion scripts"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on functional database schema design and successful API integration with populated data. Use simple english.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific database schema design or optimization goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task. Mention things like Python 3.10+, Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver), Git, pip, virtual environment support, etc.",
  "answer": "High-level solution approach focusing on database schema design principles and data modeling approach for the given business requirements",
  "hints": "A single line hint on what a good approach to solve the database schema design task could include. These hints must NOT give away the answer, but gently nudge the candidate toward good database design principles.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
    }}
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case
3. **code_files** must include README.md, .gitignore, requirements.txt, Docker files, run.sh, kill.sh, and all Python/SQL source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Database Access, Objectives, How to Verify
5. **Starter code** must be runnable but the schema/data SQL files must be EMPTY for the candidate to fill
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant PostgreSQL/FastAPI terms
8. **Task must be completable within the allocated time** for the given proficiency level
9. **NO ORM usage** for BASIC level — use raw SQL with psycopg2
10. **All paths** must reference /root/task as the base directory
"""

PROMPT_FASTAPI_POSTGRESQL_OPTIMIZATION_INSTRUCTIONS ="""
## GOAL
As a technical architect super experienced in PostgreSQL database and Python FastAPI integration, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional API and some initial schema but with logical bugs, performance issues, or suboptimal API design patterns.
The candidate's responsibility is to identify the issues and fix them - both at the database level AND at the API endpoint level. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL FastAPI application that is already connected to PostgreSQL database with existing schema and data. The FastAPI application includes:
  - Complete REST API endpoints with business logic implemented but with suboptimal database queries AND inefficient API design patterns
  - Full database connection and configuration setup
  - All necessary middleware, error handling, and response formatting
  - Complete database models and API schemas
  - Pre-populated database with realistic data and intentionally inefficient queries/schema design

  The candidate's responsibility is to:
  1. Fix database-related issues according to the task requirements (query optimization, schema improvements, indexing strategies)
  2. Optimize API endpoints that have performance bottlenecks, inefficient patterns, or logical issues (N+1 queries in endpoints, missing pagination, inefficient data fetching, poor error handling, suboptimal response structures)
  3. Implement best practices for both database operations and API design to improve overall application performance

  A key part of the task completion is to watch the candidate implement PostgreSQL optimization best practices AND FastAPI performance patterns to improve both database and API performance.


## INSTRUCTIONS

### Nature of the Task
  - Task name MUST be within 50 words and short and concise, and meaningfully name the optimization scenario
  - Task must provide a working application with existing database schema, data, and intentionally suboptimal queries/database design AND inefficient API endpoint patterns
  - **CRITICAL**: The FastAPI application should be FULLY functional but performing poorly due to both database inefficiencies AND API endpoint design issues
  - The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
  - Generate a complete, working FastAPI application with PostgreSQL database that has performance issues or bugs at BOTH the database and API layer according to the task requirements.
  - **PROVIDE PROBLEMATIC DATABASE DESIGN**: Include init_database.sql with inefficient table structures OR missing indexes OR poor relationships OR suboptimal queries — pick one of the scenarios to do this.
  - **PROVIDE PROBLEMATIC API PATTERNS**: Include API endpoints with issues like N+1 query problems, missing pagination on large datasets, inefficient data fetching patterns, or poor response structures.
  - The question should be a real-world business scenario requiring both database performance optimization AND API endpoint optimization, NOT building from scratch.
  - the Fastapi API endpoints should also be suboptimal and need optimization according to the optimizations in the database schema and queries.
  - The complexity of the optimization task and specific improvements expected from the candidate must align with the proficiency level required in the competency definition.
  - For BEGINNER and BASIC levels: Focus on simple optimizations (adding basic indexes, fixing obvious N+1 queries, adding simple pagination, basic query improvements, simple API response optimization)
  - For INTERMEDIATE levels: Require complex query optimization, advanced indexing strategies, query plan analysis, relationship improvements, efficient API patterns, advanced pagination strategies, and response optimization
  - For ADVANCED and EXPERT levels: Demand comprehensive performance tuning, complex optimization scenarios, partitioning strategies, advanced PostgreSQL features, sophisticated API design patterns, caching strategies, and end-to-end performance optimization
  - The question must NOT include hints about the specific optimizations needed at either database or API level. The hints will be provided in the "hints" field.
  - Ensure that all questions and scenarios adhere to the latest PostgreSQL and FastAPI best practices and versions for optimization.
  - If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

  ## AI AND EXTERNAL RESOURCE POLICY:
  - Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, FastAPI documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
  - The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize both PostgreSQL performance issues AND API endpoint efficiency, rather than testing rote memorization. Therefore, the complexity of the optimization tasks for every proficiency level should reflect this, requiring genuine database performance engineering, API design skills, and problem-solving abilities that go beyond simple copy-pasting from a generative AI.
  - Candidates will be encouraged to use AI to help with boilerplate code and other bugs but not replace their own thinking.

  ## Code Generation Instructions:
  Based on the real-world scenarios provided above, create a PostgreSQL and FastAPI optimization task that:
  - Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
  - Matches the complexity level appropriate for proficiency level and years of experience given as input, keeping in mind that AI assistance is allowed.
  - Tests practical PostgreSQL query optimization, performance tuning skills, AND FastAPI API design patterns that require understanding of database internals, optimization principles, and efficient API architecture.
  - Time constraints: Each task should be finished within {minutes_range} minutes.
  - At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
  - **CRITICAL**: The FastAPI application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and database connection setup, but with intentionally inefficient database queries AND suboptimal API endpoint patterns.
  - The database connection setup should use direct PostgreSQL connection.
  - All FastAPI routes should be implemented and working but with suboptimal SQL queries AND inefficient API patterns that need optimization.
  - The database should come with realistic sample data and intentionally poor schema design for optimization practice.
  - The code files generated must be valid and executable but perform poorly due to both database AND API design issues.
  - **CRITICAL**: The task focuses on optimizing existing poorly performing queries, database design, AND API endpoints, NOT building from scratch.
  - For BEGINNER AND BASIC levels of proficiency:  **NO ORM USAGE**: Do not use SQLAlchemy ORM or any other ORM. Use raw SQL queries with database connection libraries like psycopg2.
  - For INTERMEDIATE AND ADVANCED levels of proficiency: **ORM USAGE**:  Use SQLAlchemy ORM logically and appropriately, do NOT overcomplicate the. The database connection setup should use ORM-based connections.

  ## Infrastructure Requirements:
  - MUST include a complete, fully functional REST API structure using Python FastAPI that integrates with PostgreSQL
  - MUST include a Dockerfile for the FastAPI application
  - A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
  - A docker-compose.yml file which contains all the applications — a docker for running the Python FastAPI REST API and a docker for running the PostgreSQL db.
  - **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and database connection.

  ### Docker-compose Instructions:
    - PostgreSQL service with proper configuration (database, username, password)
    - Database creation with User and Password is must 
    - FastAPI service with dependency on PostgreSQL using depends_on
    - Volume mounts for data persistence (PostgreSQL data directory)
    - **Volume mount for SQL files** - Mount the SQL files directory to PostgreSQL container for initialization
    - Network configuration for service communication
    - **MUST NOT include any version specification** in the docker-compose.yml file
    - **MUST NOT include environment variables or .env file references**
    - Use hardcoded configuration values instead of environment variables
    - For user and password, use hardcoded values in the docker-compose.yml file
    - **INITIALIZATION APPROACH**: Use PostgreSQL's built-in initialization by mounting SQL files to `/docker-entrypoint-initdb.d/` in the PostgreSQL container
    - **CRITICAL**: Docker-compose handles both container orchestration AND database initialization through volume mounts

  ### init_database.sql instructions:
  - While the SQL files must create an initial schema, BUT THEY SHOULD BE SUBOPTIMAL in line with the task requirements.
  - **CRITICAL: Do not implement the solution in the SQL files, be mindful when creating schema to only create schema required for initial task and leave the rest for the candidate to implement.**

  ### Run.sh Instructions:
    + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
    + WAIT MECHANISM: Implements proper health check to wait for PostgreSQL service to be fully ready and accepting connections
    + VALIDATION: Validates that FastAPI application is responding and connected to database
    + DATABASE SETUP: SQL files are automatically executed by PostgreSQL container during initialization (no manual SQL execution needed)
    + MONITORING: Monitors container status and provides feedback on successful deployment
    + ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
    + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
    + SIMPLIFIED APPROACH: No manual SQL file execution - PostgreSQL handles initialization automatically through mounted volumes

  ### Dockerfile Instructions:
    - MUST generate a complete, valid Dockerfile for the FastAPI application
    - Should use appropriate Python base image (python:3.11-slim or similar)
    - Should install dependencies from requirements.txt
    - Should expose appropriate port for FastAPI
    - Should include proper working directory set to /root/task
    - Should include proper entry point
    - Must be production-ready and follow Docker best practices
    - **DO NOT use environment variables or .env files**
    - **CRITICAL**: Set WORKDIR to /root/task to match the file location

  **CRITICAL**: All Docker and script references must account for the /root/task base directory.


  The output should be a valid json schema:
    - README.md (CRITICAL - Follow exact structure specified below)
    - requirements.txt (Python dependencies including fastapi, psycopg2-binary, uvicorn and other dependencies required)
    - docker-compose.yml (PostgreSQL and FastAPI services configuration)
    - Dockerfile (MUST be included - Docker configuration for FastAPI app)
    - run.sh (Script to deploy and setup the complete environment)
    - .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, data/)
    - All FastAPI code files following the project structure above
    - PostgreSQL schema files with performance issues
    - **CRITICAL**: Include ALL __init__.py files for proper Python package structure

  ## Code file requirements:
  - More than 1 files can be generated but make sure they are included in the JSON structure correctly.
  - Code should follow Python PEP8 guidelines and include both PostgreSQL performance anti-patterns AND FastAPI inefficient patterns for optimization
  - **CRITICAL**: The FastAPI application files MUST be complete and fully functional with all endpoints, error handling, and database integration code, but with intentionally inefficient queries AND suboptimal API endpoint patterns.
  - **PROBLEMATIC SQL FILE**: `init_database.sql` should contain both the inefficient database schema AND sample data insertion in a single file to ensure proper execution order
  - **PROBLEMATIC API PATTERNS**: API endpoints should have issues like N+1 queries, missing pagination, inefficient data fetching, or poor response structures
  - Database connection setup and FastAPI routes should use suboptimal SQL queries AND inefficient API patterns that need improvement.
  - Tasks should focus on identifying and optimizing existing performance bottlenecks at both database and API layers.
  - **SEPARATION OF CONCERNS**: 
    - docker-compose.yml: Handles container orchestration AND database initialization through volume mounts
    - run.sh: Starts containers, implements health checks, and validates deployment
    - FastAPI app: Should work but perform poorly due to database inefficiencies AND API design issues
  - DO NOT include any 'TODO' or placeholder comments in FastAPI code
  - DO NOT include any comments that give away optimization solutions
  - The FastAPI application should be immediately runnable but will perform poorly until candidate optimizes database queries, schema, AND API endpoints.
  - **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
  - **DATABASE AND API OPTIMIZATION**: Existing schema, queries, and API endpoints need improvement - SQL file contains performance issues and API files contain inefficient patterns
  - **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

  ## .gitignore INSTRUCTIONS:
  Provide standard Python, Docker, and PostgreSQL exclusion patterns. Include:
  - Python cache files and directories (__pycache__, *.pyc, *.pyo, etc.)
  - Virtual environment directories (venv/, ENV/, env/)
  - Build and distribution directories
  - IDE and editor files (.vscode/, .idea/, *.swp)
  - Log files (*.log)
  - PostgreSQL data directories (data/pgdata/, postgres_data/)
  - OS-specific files (.DS_Store)
  - Testing and coverage files

  ## README.md INSTRUCTIONS:
  - The README.md contains the following sections:
    - Task Overview
    - Helpful Tips
    - Database Access
    - Objectives
    - How to Verify
  - The README.md file content MUST be fully populated with meaningful, specific content
  - Task Overview section MUST contain the exact business scenario and performance problems that need optimization at BOTH database and API levels
  - ALL sections must have substantial content - no empty or placeholder text allowed
  - Content must be directly relevant to the specific PostgreSQL and FastAPI optimization scenario being generated
  - Use concrete business context explaining performance bottlenecks at both database and API layers, not generic descriptions

  ### Task Overview

  **CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the specific performance problems affecting the application that need optimization at BOTH the database level AND the API endpoint level.
  NEVER generate empty content - always provide substantial business context that explains what performance issues exist in the database (queries, schema, indexes) AND in the API endpoints (N+1 queries, missing pagination, inefficient patterns) and why optimization is critical for business operations.

  ### Helpful Tips
  Write in simple and easy-to-understand language so the candidate clearly understands what the problems are
    - Explain what kinds of performance issues exist in the database (e.g., slow queries, missing indexes, or poor table structure)
    - Explain what kinds of performance issues exist in the API endpoints (e.g., N+1 query problems, missing pagination on large datasets, inefficient data fetching patterns, slow response times)
    - Point out which parts of the database AND which API endpoints might be causing delays or slowness, but do not provide the actual solution
    - Make it clear that the FastAPI code is already done and functional, but the candidate should focus on fixing both database-related performance issues AND API endpoint optimization
    - Keep it friendly and informative, so candidates are confident about what's expected from them
    - Use bullet points to keep the explanation clean and readable

  ### Database Access
    - Provide the database connection details (host(droplet-ip), port, database name, username, password)
    - Mention can use any preferred database client tools (eg:pgAdmin, DBeaver, psql) for performance analysis
    - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address

  ### Objectives
    - Clear, measurable goals for the candidate focusing on both database performance optimization AND API endpoint optimization
    - This is what the candidate should be able to do successfully to say that they have completed the optimization task.
    - These objectives will also be used to verify the task completion and award points.
    - Should focus on performance improvement objectives with measurable outcomes (response time improvements, query execution time reductions, API endpoint response time improvements, pagination implementation, efficient data fetching)
    - Include objectives for both database-level improvements AND API-level improvements

  ### How to Verify
    - Specific checkpoints after optimization showing improved performance metrics at both database and API levels
    - Observable behaviors to validate database performance improvements AND API endpoint performance improvements through testing
    - Should include verification steps for query performance improvements, API response time enhancements, and overall application performance
    - Include methods to measure and compare before/after optimization results for both database queries and API endpoints

  ### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
    - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
    - FastAPI implementation guides (API is already complete)
    - Step-by-step database connection setup (connection details are provided)
    - Instructions to run the run.sh file (deployment is automated)
    - Specific optimization solutions at database or API level (candidates must analyze and implement improvements)

## REQUIRED OUTPUT JSON STRUCTURE

  {{
    "name": "Task Name(50 words max used for name of the task)",
    "question": "A short description of the optimization task scenario including the specific performance problems in the existing database AND API endpoints that need to be identified and resolved — what performance bottlenecks exist at both database and API layers and what optimizations are needed?",
    "code_files": {{
        "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Database Access, Objectives, and How to Verify",
        ".gitignore": "Standard Python, Docker, and PostgreSQL exclusion patterns",
        "requirements.txt": "Python dependencies list including PostgreSQL drivers (NO ORM libraries for BASIC level)",
        "docker-compose.yml": "Docker services for PostgreSQL and FastAPI (NO version specifications, NO env vars)",
        "Dockerfile": "Docker configuration for FastAPI application",
        "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
        "app/__init__.py": "Empty file for Python package structure",
        "app/main.py": "Complete FastAPI application with all endpoints but inefficient database queries AND suboptimal API patterns",
        "app/database.py": "Complete database connection configuration (NO ORM for BASIC, raw SQL)",
        "app/routes/__init__.py": "Empty file for Python package structure",
        "app/routes/api.py": "Complete API route implementations with suboptimal SQL queries AND inefficient API patterns needing optimization",
        "app/schemas/__init__.py": "Empty file for Python package structure",
        "app/schemas/schemas.py": "Pydantic schemas for API requests/responses",
        "init_database.sql": "Complete database initialization file containing both schema creation with performance issues AND sample data insertion - ensures proper execution order in Docker"
        
    }},
    "outcomes": "Expected results after completion in 2-3 lines focusing on measurable performance improvements at both database and API levels, optimized database operations, and efficient API endpoint performance. Use simple english.",
    "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific database and API optimization goal, and (3) the expected outcome emphasizing measurable performance improvements.",
    "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the optimization task. Mention things like Python 3.10+, Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver), Git, pip, virtual environment support, query analysis tools, API testing tools (Postman/curl), performance monitoring tools, etc.",
    "answer": "High-level solution approach focusing on database optimization strategies, performance tuning techniques, AND API endpoint optimization patterns for the given performance issues at both layers",
    "hints": "A single line hint on what a good approach to analyze and optimize both the database performance AND API endpoint efficiency could include. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward good database performance analysis practices AND efficient API design patterns.",
    "definitions": {{
      "terminology_1": "definition_1",
      "terminology_2": "definition_2"
      }}
  }}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, within 50 words
3. **code_files** must include README.md, .gitignore, requirements.txt, Docker files, run.sh, and all Python/SQL source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Database Access, Objectives, How to Verify
5. **Starter code** must be complete and runnable but performing poorly due to database AND API inefficiencies
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant PostgreSQL/FastAPI terms
8. **Task must be completable within the allocated time** for the given proficiency level
9. **NO solutions revealed** in starter code — no TODO comments, no hint comments
10. **All paths** must reference /root/task as the base directory
  """
PROMPT_REGISTRY = {
    "Python - FastAPI, PostgreSQL": [
        PROMPT_FASTAPI_POSTGRESQL_CONTEXT,
        PROMPT_FASTAPI_POSTGRESQL_OPTIMIZATION_INSTRUCTIONS,
        PROMPT_FASTAPI_POSTGRESQL_INPUT_AND_ASK,
    ]
}
