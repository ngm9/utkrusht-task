PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INPUT_AND_ASK = """
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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of PostgreSQL large-scale dataset optimization or schema design required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a database architect super experienced in PostgreSQL, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional database with initial schema and data but either with logical bugs, scalability flaws, or performance issues that require intermediate-level PostgreSQL large-scale dataset skills.
The candidate's responsibility is to identify the database issues and fix them directly in PostgreSQL. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL PostgreSQL database that is already deployed with existing schema and data. The database includes:
- Pre-populated tables with realistic data volumes and access patterns
- Existing schema design, ingestion flow, and reporting queries that work but do not scale well
- Intentionally inefficient table layouts, indexing choices, partitioning gaps, and operational maintenance issues suitable for intermediate-level engineers (3-5 years experience)
- Real-world business scenarios involving large tables, time-based growth, and concurrent analytical or operational access

The candidate's responsibility is to analyze the database, inspect schema and statistics, interpret execution plans, identify bottlenecks, and implement PostgreSQL improvements directly using SQL commands, psql, or any database client tool of their choice.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level large-scale PostgreSQL optimization scenario
- Task must provide a working database with existing schema, data, and intentionally suboptimal large-dataset design requiring intermediate-level optimization skills
- **CRITICAL**: The PostgreSQL database should be FULLY POPULATED and functional but performing poorly or scaling poorly due to realistic inefficiencies that require intermediate-level analysis of schema design, indexing, partitioning, query plans, maintenance, and ingestion patterns
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working PostgreSQL database that has issues according to the task requirements suitable for intermediate-level engineers (3-5 years experience)
- **PROVIDE COMPLEX PROBLEMATIC DATABASE DESIGN**: Include init_database.sql with multiple tables, realistic large-table patterns, missing or suboptimal indexes, partitioning or lifecycle gaps, ingestion inefficiencies, and query anti-patterns that require comprehensive analysis and multi-layered optimization approaches
- The question should be a real-world business scenario requiring intermediate-level PostgreSQL performance and scalability work involving multiple tables, large row counts, historical data growth, and advanced but in-scope optimization strategies
- The complexity of the optimization task and specific improvements expected from the candidate must align with intermediate proficiency level (3-5 years experience) and should stay within these PostgreSQL large-scale dataset concepts:
  - PostgreSQL architecture awareness relevant to large data workloads such as shared buffers, WAL, process model, and autovacuum behavior
  - Interpreting table, index, and database size metrics using pg_class and pg_stat_* views
  - Designing scalable schemas, appropriate data types, keys, schema evolution patterns, and audit/history structures
  - Selecting and maintaining appropriate indexes including B-tree, GIN, BRIN, partial indexes, and expression indexes where justified by access patterns
  - Interpreting EXPLAIN and EXPLAIN ANALYZE output and addressing query anti-patterns on large datasets
  - Implementing and managing table partitioning and partition lifecycle considerations
  - Applying MVCC awareness, choosing suitable transaction isolation where relevant, diagnosing lock contention, and structuring batched or bulk operations to minimize locking
  - Understanding autovacuum, diagnosing bloat, and planning VACUUM or REINDEX style maintenance for large tables
  - Efficient ingestion and transformation using COPY, staging tables, and ETL-oriented loading patterns
  - Using PostgreSQL monitoring and statistics views for capacity and health analysis
  - Applying role-based access control, basic encryption awareness, row-level security, and retention or auditing considerations only where relevant to the scenario
- **CRITICAL**: Do NOT require the candidate to build replication, perform failover orchestration, or execute backup tooling as the primary task; those may appear only as contextual documentation or verification awareness, not as the central assessed implementation
- **CRITICAL**: Do NOT require advanced application development, web framework changes, or non-database coding. This is a database-only task
- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to PostgreSQL best practices for intermediate-level database performance and scale work
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize complex PostgreSQL performance and scalability issues at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the optimization tasks should require genuine intermediate-level database engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve realistic large-dataset challenges that require understanding of statistics, execution plans, data growth, indexing trade-offs, partitioning, maintenance, and ingestion patterns
- Candidates will be encouraged to use AI to help with investigation and implementation but not replace their own thinking and diagnostic skills

## Database Generation Instructions
Based on the real-world scenarios provided, create a PostgreSQL optimization task that:
- Draws inspiration from ONE of the real-world scenarios provided in {real_world_task_scenarios} to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for intermediate PostgreSQL large-dataset skills
- Tests practical intermediate-level PostgreSQL schema, indexing, partitioning, query optimization, ingestion, and maintenance skills on large tables
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided to ensure variety in task generation
- **CRITICAL**: The PostgreSQL database should be COMPLETE and FULLY POPULATED with realistic data, but with intentionally inefficient schema choices, missing or poor indexes, large-table access issues, and maintenance blind spots requiring intermediate-level optimization
- The database should contain multiple related tables with realistic business entities and at least one very large fact or event table pattern
- Use realistic row counts and distributions that make planner behavior, table size, index selectivity, and data skew matter
- Include sample queries in the documentation or SQL files that demonstrate the performance or scalability problems
- The database should have clear measurable bottlenecks that can be improved through in-scope PostgreSQL techniques
- **CRITICAL**: The task focuses on optimizing an existing poorly scaling database design and workload, NOT building a database from scratch
- Optional datastore capabilities not covered by the assessed competency, such as MySQL if present in the environment capabilities, must not be central to the task and do not require initialization files or task logic around them

## Infrastructure Requirements
- MUST include a complete PostgreSQL database deployment using Docker
- A run.sh which has the end-to-end responsibility of deploying the database infrastructure
- A docker-compose.yml file which contains the PostgreSQL database service
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working database connection

### Docker-compose Instructions
  - PostgreSQL service with proper configuration using hardcoded database name, username, and password
  - Database creation with User and Password is mandatory
  - Volume mounts for data persistence
  - **Volume mount for SQL files** - Mount the SQL files directory to PostgreSQL container for initialization
  - Network configuration if needed for external access
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - For user and password, use hardcoded values in the docker-compose.yml file
  - **INITIALIZATION APPROACH**: Use PostgreSQL's built-in initialization by mounting SQL files to `/docker-entrypoint-initdb.d/` in the PostgreSQL container
  - Expose PostgreSQL port for external client connections
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`
  - **CRITICAL**: Docker-compose handles container orchestration AND database initialization through volume mounts

### init_database.sql Instructions
- Create a comprehensive database schema with multiple tables appropriate for a large-scale PostgreSQL workload
- Include realistic relationships between tables such as lookup tables, transactional tables, historical or audit tables, staging tables, and at least one large fact-style table
- **CRITICAL: Do not implement the solution in the SQL files, create schema and data with multiple performance and scalability issues that require intermediate-level analysis and optimization**
- Include intentional large-dataset problems such as:
  - Missing indexes on frequently filtered or joined columns
  - Missing composite indexes for common predicates
  - Index type mismatches relative to access patterns
  - Inefficient data types or schema layout choices
  - Large append-heavy tables without suitable partitioning strategy
  - Historical data mixed into hot operational tables without lifecycle separation
  - Missing foreign key supporting indexes
  - Batch load patterns that create avoidable write amplification or contention
  - Tables likely to accumulate bloat or require better maintenance planning
- Populate tables with realistic data volumes:
  - Small lookup tables: hundreds to thousands of rows
  - Dimension or reference tables: thousands to tens of thousands of rows
  - Main event or transaction tables: tens of thousands to hundreds of thousands of rows, large enough to make access patterns and execution plans meaningful
- Use realistic data skew, timestamp ranges, and filter patterns that expose planner and indexing issues
- Include comments in the SQL file that describe the business context but NOT the optimization solutions
- Data should be complex enough to make performance issues evident when querying
- If the scenario includes ingestion, include staging-table or bulk-load style data setup that the candidate can improve using in-scope PostgreSQL techniques

### Run.sh Instructions
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  - WAIT MECHANISM: Implements proper health check to wait for PostgreSQL service to be fully ready and accepting connections
  - VALIDATION: Validates that PostgreSQL database is responding and accessible
  - DATABASE SETUP: SQL files are automatically executed by PostgreSQL container during initialization
  - MONITORING: Monitors container status and provides feedback on successful deployment
  - ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
  - SIMPLIFIED APPROACH: No manual SQL file execution - PostgreSQL handles initialization automatically through mounted volumes
  - **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## kill.sh file instructions
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh and docker-compose.yml
- Instructions:
  1. Stop and remove all containers created by docker compose
  2. Remove all associated Docker volumes (Postgres volume, any named volumes, and anonymous volumes)
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task such as postgres:15-alpine or postgres:16-alpine
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f postgres:15-alpine || true` or `docker rmi -f postgres:16-alpine || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Remove all PostgreSQL data directories that were mounted via volumes such as `/root/task/data/pgdata`
  - Ensure that the postgres container is cleaned up completely

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (PostgreSQL service configuration)
  - run.sh (Script to deploy the database environment)
  - kill.sh (Complete cleanup script)
  - .gitignore (Ignore data/, *.log, .DS_Store, backup artifacts, editor files)
  - init_database.sql (Complete database schema with intentional large-scale performance issues AND comprehensive sample data insertion)
  - sample_queries.sql (Representative slow or poorly scaling queries that expose the issues)
  - diagnostics.sql (Read-only helper queries for size metrics, pg_stat_* inspection, EXPLAIN analysis entry points, or lock/statistics inspection without giving away the final fix)

## Code file requirements
- All SQL files should be valid and executable PostgreSQL SQL
- **COMPLEX PROBLEMATIC SQL FILE**: `init_database.sql` should contain both the inefficient large-scale database schema with multiple tables, relationships, and comprehensive sample data insertion in a single file to ensure proper execution order
- Include realistic business scenarios in table structures and data
- DO NOT include comments that give away the optimization solution
- DO NOT include comments that hint at the direct or indirect solution in the files
- The database should be immediately queryable but will perform poorly or scale poorly until the candidate applies intermediate-level PostgreSQL techniques
- `sample_queries.sql` should contain workload-style queries that highlight the bottlenecks without spelling out the fixes
- `diagnostics.sql` should help the candidate inspect table sizes, index usage, planner behavior, or lock/statistics information in a realistic way, but it must not prescribe the exact correction
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for PostgreSQL development tasks that includes:
- PostgreSQL data directories
- Log files
- Backup files such as `*.sql.gz`, `*.dump`, `*.backup`
- IDE and editor files
- OS-specific files such as `.DS_Store`, `Thumbs.db`
- Any other standard exclusions for PostgreSQL development

## README.md INSTRUCTIONS
 - The README.md contains the following sections:
   1. Task Overview
   2. Database Access
   3. Helpful Tips
   4. Objectives
   5. How to Verify
   6. NOT TO INCLUDE in README
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level PostgreSQL large-scale dataset challenges
- Task Overview section MUST contain the exact business scenario and the concrete large-data problems that need intermediate-level optimization
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific PostgreSQL scalability scenario being generated
- Use concrete business context explaining data growth, operational pressure, reporting or ingestion workload characteristics, and why scalable PostgreSQL design matters

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the specific large-scale PostgreSQL problems affecting the database that need intermediate-level optimization. The scenario should make clear that the database is operational but is struggling with one or more of: large table scans, poor index usage, weak partitioning strategy, ingestion overhead, lock pressure, bloat symptoms, or size growth affecting reporting and operational queries.
NEVER generate empty content - always provide substantial business context that explains what large-scale issues exist and why intermediate PostgreSQL improvements are critical for business operations.

### Database Access
  - Provide the database connection details using:
    - host: `<DROPLET_IP>`
    - port: `5432`
    - database name
    - username
    - password
  - Mention candidates can use any preferred database client tools such as `psql`, `pgAdmin`, `DBeaver`, or `DataGrip`
  - Mention that they may also use PostgreSQL CLI tools where relevant for inspection and verification

### Helpful Tips
  - Provide practical guidance without revealing the implementation
  - Mention investigation approaches around query plans, table and index sizes, data distribution, partition suitability, lock behavior, batched writes, and autovacuum or bloat observations
  - Keep the guidance focused on intermediate PostgreSQL large-scale dataset analysis rather than generic SQL basics
  - Use bullet points that help the candidate reason about workload patterns, growth over time, and planner behavior
  - Do not state the exact indexes, partition keys, or query rewrites to use

### Objectives
  - Clear, measurable goals for the candidate focusing on intermediate-level PostgreSQL scalability and performance optimization
  - This is what the candidate should be able to do successfully to demonstrate intermediate-level PostgreSQL large-scale dataset competency
  - These objectives will also be used to verify task completion and award points
  - Should focus on measurable outcomes such as improved execution plans, lower latency for representative queries, better indexing strategy, safer ingestion or batch operations, reduced unnecessary scans, or improved maintenance posture
  - Objectives may include schema or table-layout changes only when they are clearly justified by the workload and remain within the provided scope

### How to Verify
  - Specific checkpoints after optimization showing improved execution plans, reduced query times, or more appropriate index usage
  - Include commands or SQL statements to compare before and after behavior
  - Validate that representative queries now perform acceptably on the provided dataset
  - Validate that schema, indexing, partitioning, or maintenance changes do not break correctness
  - Where relevant, include checks around table sizes, index usage, row counts, or lock behavior
  - Keep verification measurable and practical

### NOT TO INCLUDE in README
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific optimization solutions
  - Step-by-step implementation guides
  - Full answers, exact index statements, or direct query rewrites that solve the task

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "A kebab-case GitHub repository name under 50 characters that uniquely identifies the PostgreSQL large-scale dataset task",
   "title": "A human-readable display title in '<action verb> <subject>' format, between 50 and 80 characters, clearly describing the PostgreSQL large-scale optimization scenario and different from the name field",
   "question": "The full candidate-facing task description explaining the business scenario, the current PostgreSQL large-data problems, the boundaries of what the candidate must improve, the expected deliverables, and the success criteria without revealing the exact solution",
   "code_files": {{
      "README.md": "A fully populated candidate-facing README containing the exact required sections in the required order: Task Overview, Database Access, Helpful Tips, Objectives, How to Verify, and NOT TO INCLUDE in README, all tailored to the chosen PostgreSQL large-scale dataset scenario",
      ".gitignore": "A comprehensive gitignore file suitable for a PostgreSQL Docker-based task, covering data directories, logs, backups, editor files, and OS-generated files",
      "docker-compose.yml": "A Docker Compose configuration for the PostgreSQL service only, using hardcoded credentials, no version field, no environment variable references, localhost-only port binding, and SQL initialization mounts",
      "run.sh": "A shell script that starts the PostgreSQL environment with docker compose, waits for readiness, validates connectivity, prints clear progress logs, and references /root/task paths throughout",
      "kill.sh": "An idempotent shell script that stops containers, removes volumes, networks, images, prunes Docker resources, deletes /root/task, prints progress logs, and completes successfully even if some resources are already absent",
      "init_database.sql": "A single PostgreSQL SQL file that creates the intentionally suboptimal large-scale schema and inserts realistic sample data volumes and distributions needed to reproduce the performance and scalability issues",
      "sample_queries.sql": "A PostgreSQL SQL file containing representative workload queries that expose the large-data bottlenecks and give the candidate measurable before-and-after verification targets without disclosing the exact fix",
      "diagnostics.sql": "A PostgreSQL SQL file containing read-only investigation queries for pg_class, pg_stat_* views, EXPLAIN or EXPLAIN ANALYZE entry points, size inspection, and related diagnostics that support analysis without prescribing the final implementation"
   }},
   "answer": "A high-level evaluator-facing solution approach describing the categories of PostgreSQL improvements expected, such as schema adjustments, index strategy changes, partitioning decisions, query rewrites, maintenance considerations, or ingestion optimizations, without providing the exact final code verbatim",
   "definitions": "An object mapping PostgreSQL large-scale dataset terms to simple definitions that help the evaluator understand the concepts referenced in the task, such as WAL, MVCC, BRIN, bloat, partition pruning, autovacuum, or staging table",
   "hints": "A single line nudging the candidate toward a strong intermediate-level investigation path focused on statistics, execution plans, size metrics, or workload patterns without revealing the exact optimization needed",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements in PostgreSQL query performance, scalability posture, and operational correctness on the provided large dataset. Use simple english.",
   "pre_requisites": "A bullet-point list of tools, PostgreSQL knowledge, and environment requirements needed to complete the task, such as Docker, Docker Compose, psql or GUI database clients, EXPLAIN ANALYZE familiarity, indexing basics, partitioning awareness, and large-dataset PostgreSQL concepts",
   "short_overview": "A bullet-point list summarising the business problem, the technical PostgreSQL large-scale dataset focus areas, and the expected optimization outcome in concise simple language"
}}

## CRITICAL REMINDERS
1. **DATABASE ONLY**: Do not generate application code, API code, or framework code. Focus purely on PostgreSQL database design, scalability, optimization, and operational analysis
2. **INTERMEDIATE LEVEL**: Ensure complexity matches 3-5 years of PostgreSQL experience and remains within the supplied competency scope
3. **REAL-WORLD SCENARIO**: Use exactly ONE of the provided scenarios in {real_world_task_scenarios} as task inspiration and align the business domain closely with it
4. **MEASURABLE PROBLEMS**: Performance or scalability issues must be observable through query timing, execution plans, statistics views, size metrics, or related PostgreSQL diagnostics
5. **REALISTIC DATA**: Include enough data volume and skew to make the large-dataset issues meaningful
6. **NO SOLUTIONS IN CODE**: Do not include optimized queries, correct final indexes, or direct answers in the generated files
7. **README STRUCTURE**: Use the exact README section names and order specified above
8. **JSON SCHEMA DESCRIPTIONS**: Every required output field must have a descriptive sentence, not example placeholder arrays or object literals
9. **SECURITY AND INFRASTRUCTURE**: Use localhost-only port exposure, no environment variable references, and no docker-compose version field
10. **OPTIONAL EXTRA DATASTORE**: If another datastore capability exists in the environment but is outside the assessed competency, do not build the task around it
"""

PROMPT_REGISTRY = {
    "PostgreSQL - Large Scale Datasets (INTERMEDIATE)": [
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_CONTEXT,
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INSTRUCTIONS,
    ]
}