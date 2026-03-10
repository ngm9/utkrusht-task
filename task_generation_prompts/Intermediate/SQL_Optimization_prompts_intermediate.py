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
2. What will the task look like? (Describe the type of Python FastAPI and PostgreSQL implementation required, the expected deliverables, and how it aligns with the given proficiency level)

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

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a PARTIALLY FUNCTIONAL FastAPI application that is connected to PostgreSQL database but WITHOUT complete implementation. The FastAPI application includes:
- Basic REST API endpoint structure with skeleton implementations
- Database connection and configuration setup
- Basic middleware and error handling framework
- Minimal SQLAlchemy models and Pydantic schemas as starting templates
- **CRITICAL**: API endpoints will have placeholder implementations that need to be completed

The candidate's RESPONSIBILITY includes:
- Writing PostgreSQL queries from scratch with complex joins and subqueries
- Designing/optimizing database schema with advanced relationships and constraints
- Implementing database-related optimizations including indexing strategies
- **CRITICAL**: Completing FastAPI endpoint implementations to integrate with designed database schema
- **CRITICAL**: Implementing proper error handling and validation in API endpoints
- **CRITICAL**: Writing comprehensive database queries to support business logic in API endpoints
- Using provided database credentials to connect via database client tools

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement complex database schemas from scratch with advanced relationships, constraints, and indexes
- **CRITICAL**: The FastAPI application should have SKELETON endpoints that require completion - candidates MUST implement both database schema AND FastAPI endpoint logic.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a partially complete FastAPI application that connects to PostgreSQL, requiring the candidate to design database schema AND complete API endpoint implementations.
- DO NOT GIVE AWAY THE SOLUTION IN THE DATABASE SCHEMA OR API ENDPOINTS - provide skeleton implementations only.
- A major part of the task completion is to watch the candidate implement PostgreSQL best practices, design complex database schema correctly, AND integrate it properly with FastAPI endpoints.
- The question should be a real-world business scenario requiring both complex database schema design AND API endpoint implementation.
- The complexity of the task and specific ask expected from the candidate must align with intermediate proficiency level (3-5 years experience), ensuring scenarios involve multi-table relationships, complex business logic, and performance considerations.
- For INTERMEDIATE level proficiency, the questions must require complex schema design (multiple related tables, normalization, indexing strategies, constraints, views) AND sophisticated API endpoint implementations with proper error handling and business logic.
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions. Strictly avoid using outdated PostgreSQL features or syntax.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, FastAPI documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt PostgreSQL and FastAPI solutions to solve complex problems, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate-level requirements with complex database relationships and sophisticated API implementations that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided , create a PostgreSQL and FastAPI integration task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed.
- Tests practical PostgreSQL schema design skills AND FastAPI implementation skills that require understanding of complex business requirements, database design principles, and API development best practices.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.

## Infrastructure Requirements:
- MUST include a partially complete REST API structure using Python FastAPI that integrates with PostgreSQL
- MUST include skeleton API endpoints that require completion by the candidate
- MUST include a Dockerfile for the FastAPI application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Python FastAPI REST API and a docker for running the PostgreSQL db.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with skeleton API and database connection.

### Run.sh Instructions:
  + Starts Docker containers using docker-compose up
  + Waits for PostgreSQL service to be fully ready and accepting connections before proceeding
  + Executes schema.sql file (initially empty - candidate will populate) to create tables, relationships, indexes, and constraints
  + Executes sample_data.sql file (initially empty - candidate will populate) to insert sample data into tables
  + **CRITICAL**: Only handles SQL file execution AFTER containers are running - does NOT duplicate container startup
  + Creates database users and roles that candidates can use to connect via database client tools
  + Validates that FastAPI application is responding and connected to database (even with skeleton endpoints)
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
  - For user and password, use hardcoded values in the docker-compose.yml file
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
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|postgres:15-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all PostgreSQL data directories that were mounted via volumes (e.g., `/root/task/data/pgdata`).
  - Ensure that both the custom application container and the postgres container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

## Starter Code Instructions:
- **CRITICAL**: The FastAPI application should have SKELETON IMPLEMENTATIONS with incomplete endpoint logic that requires database integration.
- **NO ORM USAGE**: Do not use SQLAlchemy ORM or any other ORM. Use raw SQL queries with database connection libraries like psycopg2.
- The database connection setup should use direct PostgreSQL connection, not ORM-based connections.
- **CRITICAL**: FastAPI routes should have skeleton implementations with TODO comments indicating where database integration is needed.
- **CRITICAL**: API endpoints should include proper input validation, error handling frameworks, and response formatting that candidates need to complete.
- **CRITICAL**: Include complex business logic requirements that need sophisticated database queries (joins, aggregations, subqueries).
- The database should initially be empty - candidates must design schema and populate with realistic sample data.
- **CRITICAL**: Candidates must complete BOTH database schema design AND FastAPI endpoint implementations that work together.
- The code files generated must have valid skeleton structure that can be extended.
- **CRITICAL**: Include advanced requirements like transaction handling, data validation, performance optimization considerations.
- **CRITICAL**: Ensure proper Python package structure with __init__.py files in all directories.
- **CRITICAL**: API endpoints should require implementing complex business rules that involve multiple table relationships and advanced SQL operations.

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
- **CRITICAL**: The FastAPI application files MUST have skeleton implementations with clear areas for candidate completion.
- **NO ORM USAGE**: Use raw SQL queries with psycopg2 or similar PostgreSQL drivers
- **EMPTY SQL FILES**: schema.sql and data/sample_data.sql should be EMPTY files - candidates will write the database schema and insert sample data from scratch
- **NEW**: Database connection setup and FastAPI routes should have skeleton implementations with clear integration points for candidate-designed schemas.
- **NEW**: Tasks should focus on both complex schema design AND sophisticated API endpoint implementation with business logic.
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: Only starts containers and handles service dependencies
  - run.sh: Executes SQL files after containers are running to avoid conflicts
  - FastAPI app: Should handle database connection retries and include skeleton endpoint implementations
- **NEW**: Include TODO comments in FastAPI code indicating where candidates need to implement database integration
- **NEW**: Include skeleton error handling and validation frameworks that candidates need to complete
- The FastAPI application should be immediately runnable but will have incomplete functionality until candidate completes both database design and endpoint implementations.
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **DATABASE AND API DESIGN**: Both schema design and API endpoint completion are candidate's responsibility - SQL files start empty and API endpoints have skeleton implementations
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
   - Guidance
   - Database Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific PostgreSQL and FastAPI integration task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and also explain why implementing both the database schema AND API endpoints is important for the business requirements.
NEVER generate empty content - always provide substantial business context that explains what complex database schema and API functionality the candidate needs to design and implement, and why it matters for the business.

###  Guidance
  - Provide a clear explanation of how to effectively approach the complex task involving both database design and API development
  - Mention that the API infrastructure has skeleton implementations but both database schema and endpoint logic need completion
  - Highlight key files or folders in the codebase that candidates should review before starting, including both database and API components
  - Emphasize that candidates must complete BOTH database schema design AND FastAPI endpoint implementations that work together
  - **NEW**: Mention the need to implement complex business logic that requires advanced SQL queries and proper API error handling
  - **NEW**: Highlight that endpoints have skeleton implementations with TODO comments indicating integration points
  - Ensure the explanation is always given in bullet points for clarity and ease of reading

  ### Database Access
    - Provide the database connection details (host(droplet-ip), port, database name, username, password)
    - Mention can use any preferred database client tools (eg:pgAdmin, DBeaver, psql)
    - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address
    - **NEW**: Mention that API endpoints can be tested using tools like Postman or curl after implementation
  

### Objectives
  - Clear, measurable goals for the candidate focusing on both complex database schema design AND complete API endpoint implementation
  - This is what the candidate should be able to do successfully to say that they have completed the task.
  - These objectives will also be used to verify the task completion and award points.
  - Should focus on advanced schema design objectives, database population, AND functional API endpoint completion
  - **CRITICAL**: Include objectives for implementing complex business logic in API endpoints
  - **CRITICAL**: Include objectives for proper error handling and data validation in both database and API layers

### How to Verify
  - Specific checkpoints after database schema creation, data insertion, AND API endpoint completion
  - Observable behaviors or outputs to validate both database functionality and API responses
  - Should include testing both schema design and complete API functionality through endpoint testing
  - Include verification steps for schema creation, data population, AND working API endpoints with proper business logic
  - **CRITICAL**: Include verification of complex query performance and API response handling
  - **CRITICAL**: Include testing of error scenarios and edge cases in both database and API layers

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Complete FastAPI implementation guides (skeleton code is provided for completion)
  - Step-by-step database connection setup (connection details are provided)
  - Instructions to run the run.sh file (deployment is automated)
  - Pre-written schema or API implementation examples (candidates must complete from skeleton code)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A comprehensive description of the task scenario including specific business requirements that need both complex database schema design AND complete API endpoint implementations — what business problem needs to be solved through advanced database design and sophisticated API functionality, and what tables/relationships/endpoints need to be created and implemented?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Guidance, Objectives, and How to Verify for both database and API components",
      ".gitignore": "Proper Python, Docker, and PostgreSQL exclusions",
      "requirements.txt": "Python dependencies list including PostgreSQL drivers and FastAPI dependencies (NO ORM libraries)",
      "docker-compose.yml": "Docker services for PostgreSQL and FastAPI (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for FastAPI application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "app/__init__.py": "Empty file for Python package structure",
      "app/main.py": "FastAPI application with skeleton endpoint structure and TODO comments",
      "app/database.py": "Complete database connection configuration (NO ORM, raw SQL) with connection pooling",
      "app/routes/__init__.py": "Empty file for Python package structure",
      "app/routes/api.py": "Skeleton API route implementations with TODO comments for database integration",
      "app/schemas/__init__.py": "Empty file for Python package structure",
      "app/schemas/schemas.py": "Basic Pydantic schemas for API requests/responses that candidates need to extend",
      "app/models/__init__.py": "Empty file for Python package structure",
      "app/models/database_models.py": "Skeleton data model classes without ORM - for raw SQL query organization",
      "schema.sql": "EMPTY FILE - Candidate will write complex database schema with tables, relationships, indexes, constraints, and views",
      "data/sample_data.sql": "EMPTY FILE - Candidate will write comprehensive sample data insertion scripts with realistic business data"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on functional complex database schema design, successful API integration with sophisticated business logic, and complete endpoint implementations with proper error handling. Use simple english.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task. Mention things like Python 3.10+, Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver), API testing tools (Postman/curl), Git, pip, virtual environment support, intermediate knowledge of SQL joins and subqueries, FastAPI routing and middleware concepts, etc.",
  "answer": "High-level solution approach focusing on both complex database schema design principles AND comprehensive API endpoint implementation strategy for the given business requirements, including advanced SQL techniques and FastAPI best practices",
  "hints": "A single line hint on what a good approach to solve both the database schema design AND API implementation task could include. These hints must NOT give away the answer, but gently nudge the candidate toward good database design principles AND proper API development practices for intermediate-level complexity.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
    }}
}}
"""

PROMPT_FASTAPI_POSTGRESQL_OPTIMIZATION_INSTRUCTIONS_INTER ="""
## GOAL
As a technical architect super experienced in PostgreSQL database and Python FastAPI integration, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional API and some initial schema but either with logical bugs or performance issues that require intermediate-level database optimization skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL FastAPI application that is already connected to PostgreSQL database with existing schema and data. The FastAPI application includes:
- Complete REST API endpoints with business logic implemented but with suboptimal database queries requiring intermediate-level optimization
- Full database connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete database models and API schemas
- Pre-populated database with realistic data and intentionally complex inefficient queries/schema design that demand advanced problem-solving

The candidate's responsibility is to fix an issue with the database according to the task requirements and then make any code changes in the app to support the fixes. - A part of the task completion is to watch the candidate implement PostgreSQL optimization best practices and improve database performance at an intermediate level (3-5 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level optimization scenario
- Task must provide a working application with existing database schema, data, and intentionally suboptimal queries/database design requiring intermediate-level optimization skills
- **CRITICAL**: The FastAPI application should be FULLY functional but performing poorly due to complex database inefficiencies that require sophisticated analysis and optimization techniques
- **CRITICAL**: Candidates must understand that optimizing the database schema/queries requires corresponding changes in the FastAPI application code. The task should make it clear that after fixing database issues (indexes, queries, schema design), they must also update the API endpoints, models, and database query logic in the FastAPI application to properly utilize these optimizations and maintain functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a complete, working FastAPI application with PostgreSQL database that has performance issues or bugs according to the task requirements suitable for intermediate-level engineers (3-5 years experience).
- **PROVIDE COMPLEX PROBLEMATIC DATABASE DESIGN**: Include init_database.sql with multiple inefficient table structures AND missing complex indexes AND poor relationships AND suboptimal queries that require comprehensive analysis and multi-layered optimization approaches.
- The question should be a real-world business scenario requiring intermediate-level database performance optimization involving multiple tables, complex queries, and advanced optimization strategies, NOT building from scratch.
- The complexity of the optimization task and specific improvements expected from the candidate must align with intermediate proficiency level (3-5 years experience) requiring advanced database optimization techniques including:
  - Complex query optimization with joins across multiple tables
  - Advanced indexing strategies (composite indexes, partial indexes, covering indexes)
  - Query plan analysis and interpretation
  - Database relationship improvements and normalization
  - Performance bottleneck identification in multi-table operations
  - Advanced PostgreSQL features utilization
  - Complex WHERE clause optimization
  - Subquery and CTE optimization
  - Connection pooling and query batching considerations
- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions for intermediate-level optimization.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize complex PostgreSQL performance issues at an intermediate level, rather than testing rote memorization. Therefore, the complexity of the optimization tasks should require genuine intermediate-level database performance engineering and advanced problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Tasks should involve multi-layered optimization challenges that require understanding of database internals, query execution plans, and advanced PostgreSQL features.
- Candidates will be encouraged to use AI to help with boilerplate code and other bugs but not replace their own thinking and analysis skills.

## Code Generation Instructions:
Based on the real-world scenarios provided above, create a PostgreSQL optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced database optimization skills.
- Tests practical intermediate-level PostgreSQL query optimization and performance tuning skills that require deep understanding of database internals, query execution plans, and advanced optimization principles.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The FastAPI application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and database connection setup, but with intentionally complex inefficient database queries requiring intermediate-level optimization.
- The database connection setup should use ORM-based connections (SQLAlchemy) for intermediate-level complexity.
- All FastAPI routes should be implemented and working but with suboptimal SQL queries involving multiple tables, complex joins, and advanced scenarios that need intermediate-level optimization.
- The database should come with realistic sample data and intentionally complex poor schema design requiring advanced optimization practices.
- The code files generated must be valid and executable but perform poorly due to complex database issues requiring intermediate-level solutions.
- **CRITICAL**: The task focuses on optimizing existing complex poorly performing queries and advanced database design issues, NOT building from scratch.
- For INTERMEDIATE level proficiency: **ORM USAGE**: Use SQLAlchemy ORM logically and appropriately with complex relationships, advanced queries, and sophisticated database interactions that require intermediate-level optimization skills.

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Python FastAPI that integrates with PostgreSQL using advanced patterns
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
  - FastAPI service should start the application with complex inefficient database queries requiring intermediate optimization
  - **CRITICAL**: Docker-compose handles both container orchestration AND database initialization through volume mounts

### init_database.sql instructions:
- While the SQL files must create an initial schema, BUT THEY SHOULD BE SUBOPTIMAL with complex inefficiencies requiring intermediate-level optimization skills.
- **CRITICAL: Do not implement the solution in the SQL files, create complex schema with multiple performance issues that require sophisticated analysis and multi-layered optimization approaches suitable for intermediate-level candidates.**
- Include multiple tables with complex relationships requiring advanced optimization
- Create scenarios involving heavy joins, subqueries, and complex WHERE conditions
- Include missing composite indexes, improper foreign key relationships, and denormalization issues

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
  + WAIT MECHANISM: Implements proper health check to wait for PostgreSQL service to be fully ready and accepting connections
  + VALIDATION: Validates that FastAPI application is responding and connected to database
  + DATABASE SETUP: SQL files are automatically executed by PostgreSQL container during initialization (no manual SQL execution needed)
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  + SIMPLIFIED APPROACH: No manual SQL file execution - PostgreSQL handles initialization automatically through mounted volumes

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.  
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes (Postgres volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and postgres:15-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, schema.sql, sample data, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|postgres:15-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all PostgreSQL data directories that were mounted via volumes (e.g., `/root/task/data/pgdata`).
  - Ensure that both the custom application container and the postgres container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).


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
  - requirements.txt (Python dependencies including fastapi, sqlalchemy, psycopg2-binary, uvicorn and other dependencies required for intermediate-level ORM usage)
  - docker-compose.yml (PostgreSQL and FastAPI services configuration)
  - Dockerfile (MUST be included - Docker configuration for FastAPI app)
  - run.sh (Script to deploy and setup the complete environment)
  - .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, data/)
  - All FastAPI code files following the project structure above with complex database interactions
  - PostgreSQL schema files with complex performance issues requiring intermediate-level optimization
  - **CRITICAL**: Include ALL __init__.py files for proper Python package structure

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP8 guidelines and include complex PostgreSQL performance anti-patterns requiring intermediate-level optimization
- **CRITICAL**: The FastAPI application files MUST be complete and fully functional with all endpoints, error handling, and advanced database integration code using SQLAlchemy ORM, but with intentionally complex inefficient queries.
- **COMPLEX PROBLEMATIC SQL FILE**: `init_database.sql` should contain both the complex inefficient database schema with multiple tables, relationships, AND comprehensive sample data insertion in a single file to ensure proper execution order
- Database connection setup and FastAPI routes should use complex suboptimal SQL queries involving multiple tables and advanced scenarios that need intermediate-level improvement.
- Tasks should focus on identifying and optimizing existing complex performance bottlenecks requiring advanced database skills.
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: Handles container orchestration AND database initialization through volume mounts
  - run.sh: Starts containers, implements health checks, and validates deployment
  - FastAPI app: Should work but perform poorly due to complex database inefficiencies requiring intermediate-level solutions
- DO NOT include any 'TODO' or placeholder comments in FastAPI code
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that give way hints or any of the direct or indirect solution in the files 
- The FastAPI application should be immediately runnable but will perform poorly until candidate applies intermediate-level optimization techniques to database queries and schema.
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **COMPLEX DATABASE OPTIMIZATION**: Existing schema and queries need advanced improvement - SQL file contains multiple complex performance issues requiring intermediate-level solutions
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for PostgreSQL and FastAPI development tasks that includes:
- Python bytecode and cache files
- Virtual environment directories
- Build and distribution artifacts
- IDE and editor files
- Log files
- PostgreSQL data directories
- Any other standard exclusions for Python/FastAPI/PostgreSQL development

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Guidance
   - Database Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level optimization challenges
- Task Overview section MUST contain the exact business scenario and complex performance problems that need intermediate-level optimization
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific complex PostgreSQL optimization scenario being generated
- Use concrete business context explaining complex performance bottlenecks requiring advanced optimization techniques, not generic descriptions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the specific complex performance problems affecting the application that need intermediate-level database optimization involving multiple tables, complex queries, and advanced optimization strategies.
NEVER generate empty content - always provide substantial business context that explains what complex performance issues exist and why advanced optimization is critical for business operations.

### Helpful Tips
Write in clear and comprehensive language so intermediate-level candidates clearly understand the complex performance challenges:
  - Explain what kinds of complex performance issues exist in the database (e.g., slow multi-table joins, missing composite indexes, complex query optimization, or poor relationship structures)
  - Point out which parts of the database might be causing delays or slowness involving multiple tables and complex operations, but do not provide the actual solution
  - Mention that the optimization will require analysis of query execution plans, advanced indexing strategies, and complex query optimization
  - Keep it informative and challenging, so intermediate-level candidates understand the advanced optimization expectations and the need for coordinated database and API changes
  - Use bullet points to keep the explanation clean and readable

### Database Access
  - Provide the database connection details (host(droplet-ip), port, database name, username, password)
  - Mention can use any preferred database client tools (eg:pgAdmin, DBeaver, psql) for advanced performance analysis and query plan examination
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address
  - Emphasize the importance of using EXPLAIN ANALYZE for query performance analysis

### Objectives
  - Clear, measurable goals for the candidate focusing on advanced database performance optimization requiring intermediate-level skills
  - This is what the candidate should be able to do successfully to demonstrate intermediate-level database optimization competency.
  - These objectives will also be used to verify the task completion and award points.
  - Should focus on complex performance improvement objectives with measurable outcomes (significant response time improvements, complex query execution time reductions, multi-table operation optimization)
  - Include advanced optimization goals like query plan improvements, index strategy implementation, and relationship optimization

### How to Verify
  - Specific checkpoints after optimization showing significant improved performance metrics
  - Observable behaviors to validate advanced database performance improvements through the API
  - Should include verification steps for complex query performance improvements and response time enhancements
  - Include methods to measure and compare before/after optimization results for complex operations
  - Mention verification of query execution plans and index utilization improvements

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - FastAPI implementation guides (API is already complete)
  - Step-by-step database connection setup (connection details are provided)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific optimization solutions (candidates must analyze and implement advanced improvements)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words)",
   "question": "A short description of the intermediate-level optimization task scenario including the specific complex performance problems in the existing database that need to be identified and resolved using advanced techniques — what complex performance bottlenecks exist involving multiple tables and advanced queries, and what intermediate-level optimizations are needed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Complex Performance Issues, Advanced Objectives, and How to Verify for intermediate-level optimization",
      ".gitignore": "Proper Python, Docker, and PostgreSQL exclusions",
      "requirements.txt": "Python dependencies list including PostgreSQL drivers AND SQLAlchemy ORM libraries for intermediate-level usage",
      "docker-compose.yml": "Docker services for PostgreSQL and FastAPI (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for FastAPI application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "app/__init__.py": "Empty file for Python package structure",
      "app/main.py": "Complete FastAPI application with all endpoints but complex inefficient database queries requiring intermediate optimization",
      "app/database.py": "Complete database connection configuration using SQLAlchemy ORM for advanced patterns",
      "app/models/__init__.py": "Empty file for Python package structure",
      "app/models/models.py": "SQLAlchemy ORM models with complex relationships but inefficient design",
      "app/routes/__init__.py": "Empty file for Python package structure",
      "app/routes/api.py": "Complete API route implementations with complex suboptimal SQL queries needing intermediate-level optimization",
      "app/schemas/__init__.py": "Empty file for Python package structure",
      "app/schemas/schemas.py": "Pydantic schemas for API requests/responses with complex data structures",
      "init_database.sql": "Complete database initialization file containing both complex schema creation with multiple performance issues AND comprehensive sample data insertion - ensures proper execution order in Docker"
      
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable complex performance improvements and optimized advanced database operations requiring intermediate-level skills. Use simple english.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the intermediate-level optimization task. Mention things like Python 3.10+, Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver), Git, pip, virtual environment support, advanced query analysis tools (EXPLAIN ANALYZE), SQLAlchemy ORM knowledge, intermediate PostgreSQL concepts, etc.",
  "answer": "High-level solution approach focusing on advanced database optimization strategies and intermediate-level performance tuning techniques for the given complex performance issues",
  "hints": "A single line hint on what a good intermediate-level approach to analyze and optimize the complex database performance could include. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward advanced database performance analysis practices suitable for intermediate-level skills.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
    }}
}}
"""
PROMPT_REGISTRY = {
    "PostgreSQL (INTERMEDIATE), Python - FastAPI (INTERMEDIATE)": [
        PROMPT_FASTAPI_POSTGRESQL_CONTEXT,
        PROMPT_FASTAPI_POSTGRESQL_INPUT_AND_ASK,
        PROMPT_FASTAPI_POSTGRESQL_OPTIMIZATION_INSTRUCTIONS_INTER,
    ]
}
