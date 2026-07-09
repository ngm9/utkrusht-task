# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_POSTGRESQL_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_POSTGRESQL_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a PostgreSQL assessment task.

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

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, database architecture context, operational symptoms, and PostgreSQL problem the candidate will be solving)
2. What will the task look like? (Describe the type of advanced PostgreSQL diagnosis, optimization, schema/index/partitioning, concurrency, or operational remediation required, the expected deliverables, and how it aligns with ADVANCED proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_POSTGRESQL_ADVANCED_INSTRUCTIONS = """
## GOAL
As a database architect super experienced in PostgreSQL, you are given a list of real world scenarios and proficiency levels for PostgreSQL.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional PostgreSQL database with initial schema and data but either with logical bugs, performance issues, operational risks, or architectural tradeoffs that require advanced-level PostgreSQL diagnosis and remediation skills.
The candidate's responsibility is to identify the database issues and fix them directly in PostgreSQL. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL PostgreSQL database that is already deployed with existing schema, data, workload artifacts, and diagnostic entry points. The database includes:
- Pre-populated tables with realistic production-like data distributions
- Intentionally inefficient queries, indexing gaps, schema problems, partitioning issues, statistics problems, concurrency risks, or operational anti-patterns
- Performance and reliability bottlenecks that demand advanced-level problem-solving by an experienced PostgreSQL professional
- Real-world business scenarios requiring careful tradeoff analysis across correctness, latency, maintainability, availability, and operational safety

The candidate's responsibility is to analyze the database, identify root causes, and implement PostgreSQL improvements directly using SQL commands, psql, or any database client tool of their choice. The task should assess applied production judgment, not trivia or rote syntax recall.

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the advanced-level PostgreSQL scenario
- Task must provide a working database with existing schema, data, and intentionally suboptimal design requiring advanced PostgreSQL architecture, query tuning, indexing, partitioning, concurrency, or operational troubleshooting skills
- **CRITICAL**: The PostgreSQL database should be FULLY populated and functional but performing poorly, behaving riskily, or exposing operational weaknesses due to database inefficiencies that require expert analysis and advanced remediation techniques
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working PostgreSQL database that has performance or reliability issues according to the task requirements suitable for advanced PostgreSQL engineers who can independently own production database design, tuning, and operations
- **CRITICAL**: The task must be completable within {minutes_range} minutes, so it should focus on one coherent advanced production incident or optimization work item rather than a broad system redesign
- **PROVIDE ADVANCED PROBLEMATIC DATABASE DESIGN**: Include init_database.sql with realistic schema, data, diagnostic structures, and deliberate issues that require advanced PostgreSQL reasoning, while keeping the number of required fixes bounded and verifiable
- The question should be a real-world business scenario requiring advanced PostgreSQL performance optimization, data modeling correction, partitioning improvement, locking/concurrency diagnosis, operational remediation, or a focused combination of these
- The complexity of the optimization task and specific improvements expected from the candidate must align with ADVANCED proficiency requiring deep PostgreSQL expertise including:
  - Interpreting EXPLAIN and EXPLAIN ANALYZE plans with estimated rows, actual rows, join strategies, scan types, timing, buffers, and sort/hash behavior
  - Designing B-tree, GIN, GiST, BRIN, partial, expression, composite, or covering indexes appropriate to the workload
  - Reasoning about JSONB, range types, full-text search, generated columns, materialized views, or other PostgreSQL-specific features where appropriate
  - Identifying planner misestimation and using ANALYZE, extended statistics, query rewrites, or data modeling improvements where appropriate
  - Diagnosing N+1-style query patterns, row-by-row processing, inefficient predicates, harmful casts, functions in predicates, and CTE materialization issues
  - Evaluating partitioning, partition pruning, retention, archival, and large-table maintenance tradeoffs for time-series or tenant-scoped data
  - Understanding MVCC, VACUUM/autovacuum behavior, bloat, visibility maps, long transactions, and their effect on query plans and index-only scans
  - Reasoning about locking, isolation levels, deadlocks, DDL lock impact, advisory locks, and safe low-downtime changes
  - Considering WAL volume, checkpoint behavior, replication lag, backup impact, and operational risk when proposing fixes
  - Applying security and governance concepts such as roles, privileges, RLS, auditing, and least privilege only when directly relevant to the selected scenario
- **CRITICAL**: The task should not require high availability cluster setup, external orchestration tools, production failover automation, or cloud provider configuration. It may include HA/DR concepts as diagnostic context only if they are directly relevant and solvable inside the provided PostgreSQL database
- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest PostgreSQL best practices and versions for advanced-level optimization and operations
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize complex PostgreSQL performance and reliability issues at an advanced level, rather than testing rote memorization
- Therefore, the complexity of the optimization tasks should require genuine advanced-level database engineering, judgment, and problem-solving skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve production-like tradeoffs that require understanding of PostgreSQL internals, query execution plans, indexing behavior, MVCC, locking, storage, and operational impact
- Candidates will be encouraged to use AI to help with investigation and analysis but not replace their own reasoning, prioritization, and validation skills

## Database Generation Instructions:
Based on the real-world scenarios provided, create a PostgreSQL optimization and troubleshooting task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for ADVANCED proficiency, keeping in mind that AI assistance is allowed but should not diminish the need for expert database engineering judgment
- Tests practical advanced-level PostgreSQL query optimization, schema design, indexing, partitioning, concurrency, and operational troubleshooting skills that require deep understanding of database internals and production tradeoffs
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided to ensure variety in task generation
- **CRITICAL**: The PostgreSQL database should be COMPLETE and FULLY POPULATED with realistic data, but with intentionally problematic schema, query patterns, indexes, partitioning choices, statistics, or operational artifacts requiring advanced analysis
- The database should contain multiple related tables with realistic distributions, tenant skew, time-based data, JSONB attributes, status fields, or other data characteristics that expose the selected issue
- Include sample queries in the documentation or sample_queries.sql that demonstrate the performance or reliability problems
- The database should have clear bottlenecks or correctness risks that can be measured, explained, and improved
- **CRITICAL**: The task focuses on optimizing or safely remediating an existing poorly performing PostgreSQL design and workload, NOT building a database from scratch
- Make the candidate-facing task open-ended enough that candidates must investigate, but bounded enough that the expected answer can be evaluated objectively
- Do NOT require candidates to install extensions unless the generated database already enables them and the task can run in the provided PostgreSQL container
- Prefer one coherent advanced theme per task, such as:
  - a tenant-scoped ledger/search workload with JSONB predicates and time-range filters
  - a time-series event table with partition pruning and retention problems
  - an analytics query suffering from planner misestimation, spills, and poor join strategy
  - a scheduling workload needing range-aware integrity and efficient overlap checks
  - a multi-tenant reporting database with RLS, indexing, and materialized view tradeoffs
  - a long-transaction or locking incident that blocks maintenance and causes bloat
  - a bulk ingestion or backfill workflow that creates excessive WAL, temp files, or blocking risk
  - a full-text or geospatial search workload that uses the wrong access paths

## Infrastructure Requirements:
- MUST include a complete PostgreSQL database deployment using Docker
- A run.sh which has the end-to-end responsibility of deploying the database infrastructure
- A docker-compose.yml file which contains the PostgreSQL database service
- No kill.sh is needed because E2B sandboxes are destroyed as a whole when the session ends
- No application container, API code, frontend code, or Dockerfile should be generated for this PostgreSQL-only assessment
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with a working PostgreSQL database
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

### Docker-compose Instructions:
  - PostgreSQL service with proper configuration using deterministic hardcoded values
  - Database creation with User and Password is mandatory
  - Volume mounts for data persistence using a task-local data directory or named volume
  - **Volume mount for SQL files** - Mount the SQL files directory to PostgreSQL container for initialization
  - Network configuration if needed for local access
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of external environment variable references
  - For user and password, use hardcoded values in the docker-compose.yml file
  - **INITIALIZATION APPROACH**: Use PostgreSQL's built-in initialization by mounting SQL files to `/docker-entrypoint-initdb.d/` in the PostgreSQL container
  - Expose PostgreSQL port for local client connections on 5432
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`
  - **CRITICAL**: Docker-compose handles container orchestration AND database initialization through volume mounts
  - Keep the service simple and deterministic; do not add Redis, MySQL, Elasticsearch, Kafka, application services, or any datastore not exercised by the PostgreSQL scenario

### init_database.sql Instructions:
- Create a comprehensive PostgreSQL schema with multiple related tables appropriate for advanced-level diagnosis, typically 6-12 tables unless the selected scenario is intentionally focused on one very large table plus supporting lookup tables
- Include realistic relationships between tables, such as foreign keys, one-to-many relationships, many-to-many relationships, tenant boundaries, time-series relationships, audit/event structures, or domain-specific constraints
- **CRITICAL: Do not implement the solution in the SQL files. Create a realistic schema and workload with performance, modeling, statistics, partitioning, concurrency, or operational issues that require advanced PostgreSQL analysis**
- Include intentional advanced PostgreSQL problems such as a focused subset of:
  - Missing or poorly ordered composite indexes for common tenant/time/status filters
  - Missing partial indexes for highly selective production predicates
  - Missing expression indexes for JSONB, text, date/time, or case-insensitive predicates
  - Incorrect use of functions or casts in predicates that prevents efficient access paths
  - Poor use of JSONB where constraints, generated columns, or indexing choices matter
  - Planner misestimation caused by skewed data distributions or correlated columns
  - Missing extended statistics for correlated predicates where appropriate
  - Inefficient CTEs, subqueries, joins, or aggregation patterns
  - Large table design that would benefit from bounded partitioning or archival strategy
  - Partitioning that exists but does not prune effectively because of query or schema choices
  - Bloat or vacuum pressure simulated through table structure, fillfactor choices, stale statistics, or workload artifacts
  - Locking and transaction-risk artifacts represented by tables, functions, sample transactions, or diagnostic notes
  - Materialized view refresh or reporting-table freshness tradeoffs
  - Excessive, redundant, or low-value indexes that create write overhead without supporting the workload
  - Missing constraints that allow data quality problems affecting query correctness and planner selectivity
- Populate tables with realistic data volumes sufficient to make performance problems evident in an assessment sandbox:
  - Lookup/configuration tables: tens to thousands of rows
  - Tenant/account/entity tables: hundreds to tens of thousands of rows
  - Transactional/event/ledger tables: tens of thousands to several hundred thousand rows, using generate_series where appropriate
  - Skewed distributions that expose planner and indexing issues
- Use deterministic SQL data generation where possible so the task is reproducible
- Include comments in the SQL file that describe the business context but NOT the optimization solutions
- Data should be complex enough to make performance or reliability symptoms observable when running sample queries
- Keep the initialization time reasonable for the assessment environment; do not generate millions of rows if the sandbox cannot initialize within the expected task setup time
- Include only valid executable PostgreSQL SQL and avoid relying on external files unless those files are also included in code_files
- If using extensions such as pg_stat_statements, pg_trgm, btree_gin, citext, uuid-ossp, or PostGIS, only include them when directly relevant and available in the standard PostgreSQL image or clearly supported by the generated compose setup

### Run.sh Instructions:
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  - WAIT MECHANISM: Implements proper health check to wait for PostgreSQL service to be fully ready and accepting connections
  - VALIDATION: Validates that PostgreSQL database is responding and accessible
  - DATABASE SETUP: SQL files are automatically executed by PostgreSQL container during initialization (no manual SQL execution needed)
  - MONITORING: Monitors container status and provides feedback on successful deployment
  - ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
  - SIMPLIFIED APPROACH: No manual SQL file execution - PostgreSQL handles initialization automatically through mounted volumes
  - Do not include apt-get install, pip install, npm install, or runtime installation commands
  - Use /root/task as the working directory and base path for all file references

### Dockerfile Instructions:
- Omit Dockerfile entirely. This is a database-only PostgreSQL assessment with no application container.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (PostgreSQL service configuration)
  - run.sh (Script to deploy the database environment)
  - .gitignore (Ignore data/, logs, backups, temporary files, editor files, and OS files)
  - init_database.sql (Complete PostgreSQL schema with intentional advanced performance, modeling, or operational issues and comprehensive sample data insertion)
  - sample_queries.sql (Sample queries and optional diagnostic commands that demonstrate the problems before optimization)

## Code file requirements:
- All SQL files should be valid and executable PostgreSQL SQL
- **ADVANCED PROBLEMATIC SQL FILE**: `init_database.sql` should contain both the advanced database schema and comprehensive sample data insertion in a single file to ensure proper execution order
- Include realistic business scenarios in table structures, data distributions, query paths, and operational artifacts
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that hint at the direct or indirect solution in the files
- DO NOT include optimized queries, correct final indexes, final partitioning fixes, or complete remediation scripts in the starter files
- The database should be immediately queryable but will perform poorly or expose risk until the candidate applies advanced PostgreSQL techniques
- sample_queries.sql should include representative queries or diagnostic commands that reveal symptoms, such as slow execution, poor scan types, row-estimate mismatch, temp-file-prone sorts, missing partition pruning, lock-risk flows, or incorrect access paths
- sample_queries.sql may include EXPLAIN or EXPLAIN ANALYZE statements, but should not include the improved versions of those statements
- Keep the task self-contained and deterministic
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for PostgreSQL development tasks that includes:
- PostgreSQL data directories
- Log files
- Backup files such as *.sql.gz, *.dump, and *.backup
- Temporary files and generated reports
- IDE and editor files
- OS-specific files such as .DS_Store and Thumbs.db
- Any other standard exclusions for PostgreSQL and Docker-based local database work

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

- The README.md file content MUST be fully populated with meaningful, specific content relevant to advanced PostgreSQL optimization or troubleshooting challenges
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific PostgreSQL scenario being generated
- Do NOT include database connection details, hostnames, ports, usernames, passwords, database client suggestions, or `<DROPLET_IP>` placeholders in the README
- Do NOT include setup commands or manual deployment instructions because the environment is automated

### Task Overview
- Task Overview must be 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters. NEVER empty. NO bold time-budget callouts.
- The section should explain the observable production-style symptoms and business impact without naming the exact fix.
- Do not reveal specific indexes, query rewrites, partitioning changes, statistics changes, constraint changes, or operational commands needed to solve the task.

### Objectives
- Objectives must be 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix. A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like. It does NOT name the API, library, pattern, or algorithm that solves it. Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label. BAD: 'Improve query performance.' GOOD: 'The product search endpoint returns results in 4-6 seconds under normal load; after your changes it should respond in under 500ms for typical query patterns.'
- Objectives should focus on measurable PostgreSQL outcomes such as reduced query latency, improved plan stability, safer concurrent behavior, reduced maintenance risk, bounded reporting runtime, or reliable data integrity.
- Do not reveal exact SQL statements, index definitions, partition boundaries, extension choices, or configuration parameters.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Tips may point candidates toward investigating query plans, row counts, timing, table relationships, data distributions, locking symptoms, or operational evidence, but must not prescribe the fix.

### How to Verify
- How to Verify must be 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as test output, response shape, latency observation, log line, memory reading, query plan observation, lock behavior, row-count validation, or before/after runtime comparison.
- Verification should include measurable before/after database behavior where appropriate, such as reduced execution time, improved scan shape, stable row estimates, less temporary disk usage, successful integrity checks, or safe concurrent execution.
- Do not include direct solution commands or exact DDL statements.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of the README.md entirely:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, `psql` setup commands, or any manual deployment command
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, exact PostgreSQL functions, exact index definitions, exact operator classes, exact partitioning strategies, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database-connection details including host, port, username, password, database name, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", "create this index", "rewrite the query as", or "partition the table by"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the PostgreSQL assessment task without using spaces or title casing.",
   "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from the repository name, and specific to the selected PostgreSQL scenario.",
   "question": "A full candidate-facing task description that explains the business scenario, the existing PostgreSQL database symptoms, the expected investigation and remediation scope, and the measurable outcome required without revealing the exact solution.",
   "code_files": {{
      "README.md": "Candidate-facing README content with exactly the required Task Overview, Objectives, Helpful Tips, and How to Verify sections, written concisely and without setup commands, database connection details, or direct solution guidance.",
      ".gitignore": "A PostgreSQL and Docker-oriented gitignore file that excludes database data directories, logs, backups, temporary files, editor files, and operating-system artifacts.",
      "docker-compose.yml": "A Docker Compose configuration containing only the PostgreSQL service needed for the task, with no version field, no .env references, localhost-only port binding, deterministic hardcoded configuration, and initialization through mounted SQL files.",
      "run.sh": "A shell script located under /root/task assumptions that starts the PostgreSQL container with docker compose up -d, waits for readiness, validates connectivity, prints clear progress logs, and avoids installing runtime dependencies.",
      "init_database.sql": "A complete executable PostgreSQL initialization file that creates the intentionally problematic advanced schema, relationships, optional extensions if needed, and realistic deterministic seed data without including the final optimization solution.",
      "sample_queries.sql": "A SQL file containing representative workload and diagnostic queries that expose the initial performance, planning, locking, partitioning, or operational symptoms without including optimized replacement queries or final remediation DDL."
   }},
   "answer": "An evaluator-facing high-level solution approach describing the expected root causes, the types of PostgreSQL changes a strong advanced candidate would make, the reasoning behind those changes, and how the improvements should be validated.",
   "definitions": "An object mapping PostgreSQL terms used by the task to concise definitions, focused on concepts such as query plans, MVCC, WAL, indexes, partitioning, statistics, locking, bloat, or other domain terms relevant to the generated scenario.",
   "hints": "A single line hint nudging investigation toward appropriate PostgreSQL diagnostics and tradeoff analysis without naming the specific indexes, rewrites, commands, functions, extension choices, or schema changes needed.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable database performance, correctness, reliability, or operational improvements. Use simple english.",
   "pre_requisites": "Exactly 2-3 concise bullets describing the tools and knowledge needed, with each bullet covering one item such as PostgreSQL access, Docker-based local environment availability, or advanced PostgreSQL diagnostic knowledge.",
   "short_overview": "Exactly 3 plain sentences: the first states what database scenario is being worked on, the second states what the candidate must diagnose and improve, and the third states what successful completion looks like with no label prefixes."
}}

## CRITICAL REMINDERS:
1. **NO API CODE**: Do not generate any FastAPI, Flask, Express, frontend, worker, or application code. Focus purely on PostgreSQL database optimization and troubleshooting.
2. **DATABASE ONLY**: Candidates will work directly with the PostgreSQL database using SQL commands or database tooling available in the environment.
3. **ADVANCED LEVEL**: Ensure complexity matches advanced PostgreSQL proficiency involving production-grade reasoning about plans, indexes, MVCC, locking, storage, partitioning, operations, or security where relevant.
4. **MEASURABLE PROBLEMS**: Performance, reliability, or correctness issues must be clearly measurable and observable through query execution times, query plans, row counts, lock behavior, statistics, or other PostgreSQL diagnostics.
5. **REALISTIC DATA**: Include sufficient realistic data volume and skew to make PostgreSQL problems evident without making initialization impractically slow.
6. **BUSINESS CONTEXT**: Always ground the task in one realistic business scenario selected from the provided real-world scenarios.
7. **NO SOLUTIONS IN CODE**: Do not include optimized queries, correct final indexes, final partitioning changes, remediation scripts, or comments that reveal the answer in generated files.
8. **VERIFICATION**: Provide clear methods to verify success through observable database behavior without prescribing exact implementation steps.
9. **NO KILL SCRIPT**: Do not include kill.sh in the generated output because the sandbox lifecycle handles cleanup.
10. **VALID JSON ONLY**: The final generated task output must be valid JSON with the exact required keys and file mappings.
"""

PROMPT_REGISTRY = {
    "PostgreSQL (ADVANCED)": [
        PROMPT_POSTGRESQL_ADVANCED_CONTEXT,
        PROMPT_POSTGRESQL_ADVANCED_INPUT_AND_ASK,
        PROMPT_POSTGRESQL_ADVANCED_INSTRUCTIONS,
    ]
}