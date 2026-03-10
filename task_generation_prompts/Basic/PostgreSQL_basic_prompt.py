PROMPT_POSTGRESQL_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a PostgreSQL assessment task.

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

1. What will the task be about? (Describe the business domain, data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of SQL or database fix required, the expected deliverables, and how it aligns with BASIC PostgreSQL proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_POSTGRESQL_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_POSTGRESQL_BASIC_INSTRUCTIONS="""
## GOAL
As a database architect super experienced in PostgreSQL, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional database with initial schema and data but with basic logical bugs or simple performance issues that require foundational-level database skills.
The candidate's responsibility is to identify the database issues and fix them directly in PostgreSQL. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL PostgreSQL database that is already deployed with existing schema and data. The database includes:
- Pre-populated tables with realistic data
- Simple inefficient queries, missing basic indexes, or fundamental schema issues
- Basic performance bottlenecks that demand foundational-level problem-solving (1-2 years experience)
- Real-world business scenarios requiring basic database optimization

The candidate's responsibility is to analyze the database, identify basic performance issues, and implement PostgreSQL optimizations directly using SQL commands, psql, or any database client tool of their choice.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the basic-level optimization scenario
- Task must provide a working database with existing schema, data, and intentionally suboptimal design requiring foundational-level optimization skills
- **CRITICAL**: The PostgreSQL database should be FULLY populated and functional but performing poorly due to simple database inefficiencies that require basic analysis and optimization techniques
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working PostgreSQL database that has basic performance issues according to the task requirements suitable for foundational-level engineers (1-2 years experience)
- **PROVIDE SIMPLE PROBLEMATIC DATABASE DESIGN**: Include init_database.sql with straightforward inefficient table structures AND missing basic indexes AND simple relationship issues that require fundamental analysis and optimization approaches
- The question should be a real-world business scenario requiring basic-level database performance optimization involving 2-4 tables and simple queries
- The complexity of the optimization task and specific improvements expected from the candidate must align with basic proficiency level (1-2 years experience) requiring foundational database optimization techniques including:
  - Simple query optimization with basic joins (2-3 tables)
  - Basic indexing strategies (single-column indexes on frequently queried columns)
  - Simple query plan analysis using EXPLAIN
  - Basic WHERE clause optimization
  - Understanding of primary keys and foreign keys
  - Simple data type optimization
  - Basic understanding of NULL handling
  - Fundamental PostgreSQL concepts (SELECT, JOIN, WHERE, ORDER BY, LIMIT)
  - Basic understanding of sequential scans vs index scans
- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions for basic-level optimization
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize basic PostgreSQL performance issues at a foundational level, rather than testing rote memorization
- Therefore, the complexity of the optimization tasks should require genuine basic-level database understanding and fundamental problem-solving skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve straightforward optimization challenges that require understanding of basic database concepts and simple query execution
- Candidates will be encouraged to use AI to help with basic query optimization and analysis but not replace their own thinking and diagnostic skills

## Database Generation Instructions:
Based on the real-world scenarios provided, create a PostgreSQL optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for basic proficiency level (1-2 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for foundational database skills
- Tests practical basic-level PostgreSQL query optimization and performance tuning skills that require understanding of fundamental database concepts
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided to ensure variety in task generation
- **CRITICAL**: The PostgreSQL database should be COMPLETE and FULLY POPULATED with realistic data, but with intentionally simple inefficient schema, missing basic indexes, and poor query performance requiring foundational-level optimization
- The database should contain 2-4 tables with simple relationships, realistic data volumes (hundreds to tens of thousands of rows), and simple queries that expose basic performance issues
- Include sample queries in the documentation that demonstrate the performance problems (slow execution times)
- The database should have clear basic performance bottlenecks that can be measured and improved
- **CRITICAL**: The task focuses on optimizing existing poorly performing database design and queries, NOT building from scratch

## Infrastructure Requirements:
- MUST include a complete PostgreSQL database deployment using Docker
- A run.sh which has the end-to-end responsibility of deploying the database infrastructure
- A docker-compose.yml file which contains the PostgreSQL database service
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working database connection

### Docker-compose Instructions:
  - PostgreSQL service with proper configuration (database, username, password)
  - Database creation with User and Password is mandatory
  - Volume mounts for data persistence (PostgreSQL data directory)
  - **Volume mount for SQL files** - Mount the SQL files directory to PostgreSQL container for initialization
  - Network configuration if needed for external access
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - For user and password, use hardcoded values in the docker-compose.yml file
  - **INITIALIZATION APPROACH**: Use PostgreSQL's built-in initialization by mounting SQL files to `/docker-entrypoint-initdb.d/` in the PostgreSQL container
  - Expose PostgreSQL port for external client connections (5432)
  - **CRITICAL**: Docker-compose handles container orchestration AND database initialization through volume mounts

### init_database.sql instructions:
- Create a simple database schema with 2-4 tables (appropriate for basic level)
- Include basic relationships between tables (simple foreign keys, one-to-many)
- **CRITICAL: Do not implement the solution in the SQL files, create simple schema with basic performance issues that require fundamental analysis and optimization approaches suitable for basic-level candidates**
- Include intentional basic performance problems such as:
  - Missing indexes on commonly queried columns
  - Missing indexes on foreign key columns
  - Inefficient basic data types
  - Missing primary keys on lookup tables
  - Simple queries that result in full table scans
- Populate tables with realistic data volumes:
  - Lookup tables: hundreds to a few thousand rows
  - Main tables: thousands to tens of thousands of rows
  - Use realistic data that makes basic performance issues evident
- Include comments in the SQL file that describe the business context but NOT the optimization solutions
- Data should be simple enough for basic analysis but sufficient to show performance issues

### Run.sh Instructions:
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
  - WAIT MECHANISM: Implements proper health check to wait for PostgreSQL service to be fully ready and accepting connections
  - VALIDATION: Validates that PostgreSQL database is responding and accessible
  - DATABASE SETUP: SQL files are automatically executed by PostgreSQL container during initialization (no manual SQL execution needed)
  - MONITORING: Monitors container status and provides feedback on successful deployment
  - ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
  - SIMPLIFIED APPROACH: No manual SQL file execution - PostgreSQL handles initialization automatically through mounted volumes

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml
- Instructions:
  1. Stop and remove all containers created by docker-compose
  2. Remove all associated Docker volumes (Postgres volume, any named volumes, and anonymous volumes)
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task (postgres:15-alpine or postgres:16-alpine)
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f postgres:15-alpine || true` (or appropriate postgres version)
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Remove all PostgreSQL data directories that were mounted via volumes (e.g., `/root/task/data/pgdata`)
  - Ensure that the postgres container is cleaned up completely

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (PostgreSQL service configuration)
  - run.sh (Script to deploy the database environment)
  - kill.sh (Complete cleanup script)
  - .gitignore (Ignore data/, *.log, .DS_Store)
  - init_database.sql (Complete database schema with intentional basic performance issues AND comprehensive sample data insertion)
  - sample_queries.sql (Sample queries that demonstrate the basic performance problems - these should run slowly before optimization)

## Code file requirements:
- All SQL files should be valid and executable PostgreSQL SQL
- **SIMPLE PROBLEMATIC SQL FILE**: `init_database.sql` should contain both the simple inefficient database schema with 2-4 tables, basic relationships, AND comprehensive sample data insertion in a single file to ensure proper execution order
- Include realistic business scenarios in table structures and data
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that hint at the direct or indirect solution in the files
- The database should be immediately queryable but will perform poorly until candidate applies basic-level optimization techniques
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for PostgreSQL development tasks that includes:
- PostgreSQL data directories
- Log files
- Backup files (*.sql.gz, *.dump, *.backup)
- IDE and editor files
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for PostgreSQL development

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Database Access
   - Helpful Tips
   - Objectives
   - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content relevant to basic-level optimization challenges
- Task Overview section MUST contain the exact business scenario and simple performance problems that need foundational-level optimization
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific basic PostgreSQL optimization scenario being generated
- Use concrete business context explaining simple performance bottlenecks requiring basic optimization techniques, not generic descriptions

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the specific simple performance problems affecting the database that need basic-level database optimization involving 2-4 tables and simple queries.
NEVER generate empty content - always provide substantial business context that explains what basic performance issues exist and why optimization is important for business operations.

### Database Access
  - Provide the database connection details (host(droplet-ip), port, database name, username, password)
  - Mention can use any preferred database client tools (e.g., pgAdmin, DBeaver, psql, DataGrip) for basic performance analysis
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address

### Helpful Tips
  - **Basic database context** and foundational guidance points for PostgreSQL optimization
  - **Technical basics** covering PostgreSQL indexing fundamentals, simple query optimization, basic performance considerations
  - **Important considerations** for basic query performance and data integrity
  - **Database fundamentals** and simple optimization workflow considerations
  
### Objectives
  - Clear, measurable goals for the candidate focusing on basic database performance optimization requiring foundational-level skills
  - This is what the candidate should be able to do successfully to demonstrate basic-level database optimization competency
  - These objectives will also be used to verify the task completion and award points
  - Should focus on simple performance improvement objectives with measurable outcomes (moderate query execution time improvements, basic query optimization, simple index implementation)
  
### How to Verify
  - Specific checkpoints after optimization showing improved performance metrics
  - Measure query execution time improvements
  - Validate that optimization goals are met
  - Include specific commands to test performance improvements

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific optimization solutions (candidates must analyze and implement basic improvements)
  - Step-by-step optimization guides

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words)",
   "question": "A short description of the basic-level optimization task scenario including the specific simple performance problems in the existing database that need to be identified and resolved using foundational techniques — what basic performance bottlenecks exist involving 2-4 tables and simple queries, and what basic-level optimizations are needed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Database Schema Overview, Database Access, Performance Issues, Objectives, How to Verify, and Tools for basic-level optimization",
      ".gitignore": "Proper PostgreSQL and Docker exclusions",
      "docker-compose.yml": "Docker service for PostgreSQL (NO version specifications, NO env vars)",
      "run.sh": "Complete setup script for database deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "init_database.sql": "Complete database initialization file containing both simple schema creation with basic performance issues AND comprehensive sample data insertion - ensures proper execution order in Docker",
      "sample_queries.sql": "Sample queries that demonstrate the basic performance problems before optimization - these should include EXPLAIN output examples showing poor performance"
   }},
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable basic performance improvements and optimized database operations requiring foundational-level skills. Use simple english.",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific database optimization goal, and (3) the expected outcome emphasizing measurable performance improvements.",
   "pre_requisites": "Bullet-point list of tools, knowledge, and environment required to complete the basic-level optimization task. Mention things like Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver/psql), basic SQL knowledge, understanding of EXPLAIN, foundational PostgreSQL concepts (indexes, simple queries, data types), etc.",
   "answer": "High-level solution approach focusing on basic database optimization strategies and foundational-level performance tuning techniques for the given simple performance issues. Include specific basic optimization techniques like: which simple indexes to create, basic query improvements needed, simple schema changes required, etc.",
   "hints": "A single line hint on what a good basic-level approach to analyze and optimize the database performance could include. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward basic database performance analysis practices suitable for foundational-level skills (e.g., 'Start by checking if frequently queried columns have indexes').",
   "definitions": {{
      "terminology_1": "definition_1",
      "terminology_2": "definition_2"
   }}
}}


## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **NO API CODE**: Do not generate any FastAPI, Flask, or any application code. Focus purely on PostgreSQL database optimization
3. **DATABASE ONLY**: Candidates will work directly with the PostgreSQL database using SQL commands and database client tools
4. **BASIC LEVEL**: Ensure complexity matches 1-2 years of PostgreSQL experience
5. **MEASURABLE PROBLEMS**: Performance issues must be clearly measurable and observable through query execution times
6. **REALISTIC DATA**: Include sufficient data volume to make basic performance problems evident
7. **BUSINESS CONTEXT**: Always ground the task in a realistic business scenario
8. **NO SOLUTIONS IN CODE**: Do not include optimized queries, correct indexes, or any solutions in the generated files
9. **VERIFICATION**: Provide clear methods to verify optimization success through measurable metrics
10. **SIMPLICITY**: Keep the number of tables (2-4), relationships, and queries simple for foundational-level candidates
11. **FUNDAMENTAL CONCEPTS**: Focus on core PostgreSQL concepts like basic indexes, simple joins, WHERE clauses, and primary/foreign keys
"""
PROMPT_REGISTRY = {
    "PostgreSQL (BASIC)": [
        PROMPT_POSTGRESQL_CONTEXT,
        PROMPT_POSTGRESQL_INPUT_AND_ASK,
        PROMPT_POSTGRESQL_BASIC_INSTRUCTIONS,
    ]
}
