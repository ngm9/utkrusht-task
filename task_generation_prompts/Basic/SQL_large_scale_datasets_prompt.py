PROMPT_SQL_LARGE_SCALE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SQL_LARGE_SCALE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a SQL - Large Scale Datasets assessment task.

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

1. What will the task be about? (Describe the business domain, the large-scale data context, and the analytics or performance problem the candidate will be solving)
2. What will the task look like? (Describe the type of SQL work required — query writing, optimization, window functions, CTEs — the expected deliverables, and how it aligns with BASIC large-scale SQL proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SQL_LARGE_SCALE_BASIC = """
# SQL - Large Scale Datasets Basic Task Requirements

## GOAL
As a data engineering architect with deep experience in large-scale SQL and analytical databases, you are given real-world scenarios and proficiency levels for SQL on large-scale datasets. Your job is to generate an entire task definition — including database schema files, README.md, expected outcomes, etc. — that effectively assesses a candidate's ability to write correct, performant SQL against large analytical datasets. The task is SQL and database only — no application code (no FastAPI, Flask, APIs, or backend frameworks). The candidate works purely with SQL, a PostgreSQL client, and the database.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to write, fix, or optimize SQL for a large-scale analytical scenario: e.g., write analytics queries using window functions and CTEs, fix slow aggregations on large fact tables, add appropriate indexes or rewrite non-sargable predicates, or correct logic errors in multi-step analytical SQL.
- The scenario must be grounded in a real analytics or data engineering business context — reporting, dashboarding, data pipelines, operational analytics, etc.
- **CRITICAL — FULLY FUNCTIONAL DEPLOYMENT**: The candidate receives a database that is created and populated in ONE GO. When run.sh is executed, the database must be created successfully, all schema and data must be loaded without errors, and the deployment must NOT fail. The environment is fully working from the start. The candidate's ONLY job is to fix, write, or improve the given SQL/database problem — they do NOT fix deployment or initialization.
- The database MUST reflect a large-scale analytics schema: at least one large fact table (simulated with thousands of rows — representing millions in production) and supporting dimension/lookup tables, using realistic fact/dimension relationships (star or snowflake style). This models what the candidate will face on the job.
- Intentional issues must be at BASIC level: missing indexes on frequently filtered/joined columns, non-sargable predicates (functions on indexed columns in WHERE clauses), unbounded sorts without LIMIT on large result sets, missing or incorrect use of CTEs or window functions where they are clearly called for, full table scans due to absent composite indexes. All issues are logical/performance only — no syntax or runtime errors in the provided SQL.
- DO NOT GIVE AWAY THE SOLUTION in any file or comment. The candidate must diagnose and implement the fix.
- The scenario must be realistic: business reports that are running too slowly, analytics queries returning incorrect aggregations, pipelines that scan too much data unnecessarily.
- The complexity and specific ask must align with BASIC proficiency level (1-2 years SQL/large-scale data experience). For BASIC level, focus on:
  - Core constructs on large tables: SELECT, JOINs (2-4 tables), WHERE, GROUP BY, HAVING, ORDER BY, DISTINCT, LIMIT/OFFSET
  - Basic aggregations (COUNT, SUM, AVG, MIN, MAX) on large fact tables
  - Simple window functions: ROW_NUMBER, RANK, DENSE_RANK, SUM OVER (PARTITION BY), running totals
  - CTEs (WITH clauses) for query clarity and reusability
  - Fact/dimension schema understanding (star schema style)
  - Recognizing and fixing non-sargable predicates (e.g. WHERE YEAR(date_col) = 2024 → WHERE date_col BETWEEN ...)
  - Basic composite and single-column indexing on high-cardinality filter/join columns
  - Reading EXPLAIN to identify sequential scans and sort costs on large tables
  - NULL handling and data quality checks (COALESCE, IS NULL, deduplication)
  - Partition key awareness: understanding how WHERE clauses should use partition keys for pruning
  - Understanding OLTP vs OLAP data patterns at a foundational level
- The question must NOT include hints. Hints will be provided in the "hints" field.
- Ensure all scenarios adhere to standard SQL and PostgreSQL best practices (current stable version). Use PostgreSQL as the engine.
- If you include diagrams, write them in mermaid format, properly indented in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC large-scale SQL proficiency (1-2 years experience).
- **Task name**: short, under 50 characters, kebab-case (e.g. "sql-sales-report-window-fix", "sql-fact-index-optimization").

### Database and SQL File Requirements

**WHAT MUST BE INCLUDED:**
- A complete, working PostgreSQL database deployment (Docker-based): docker-compose.yml, run.sh, kill.sh, init_database.sql.
- **CRITICAL**: The database must be created and fully populated in one go when the environment is deployed. run.sh must result in a successful deployment with zero failures — schema created, all data inserted, database ready to query. The candidate only fixes or improves the SQL; they do not fix deployment or initialization.
- **init_database.sql**: Single file that creates the schema and inserts all data, runs to completion without errors. Schema must include:
  - 1 large fact table (minimum 50,000–200,000 rows generated via `generate_series` or looped inserts — this simulates the millions-of-rows production reality while keeping Docker init fast)
  - 2–4 dimension/lookup tables (hundreds to low thousands of rows each)
  - Realistic star-schema-style foreign key relationships
  - Intentional BASIC-level issues: missing indexes on high-cardinality join/filter columns, non-sargable predicates in provided sample queries, unbounded sorts, missing window function logic, or incorrect aggregation logic — as logical/performance issues only, zero syntax/runtime errors
  - Use `generate_series` to efficiently populate the large fact table rather than writing thousands of individual INSERT statements
  - No solution hints in comments
- **sample_queries.sql**: Queries that currently run slowly or return incorrect results on the large dataset. Must demonstrate observable performance problems (sequential scans, high cost). Optional: include EXPLAIN output examples showing poor performance. Do NOT include fixed or optimized versions.
- **README.md**: Task Overview, Objectives, Database Access, How to Verify, Helpful Tips — in that order. All sections fully populated.
- **.gitignore**: Suitable for PostgreSQL/Docker development (data dirs, logs, backups, IDE/OS files).

**WHAT MUST NOT BE INCLUDED:**
- DO NOT include any application code (no FastAPI, Flask, Node, etc.). SQL and database only.
- DO NOT give away the solution in init_database.sql, sample_queries.sql, or any other file (no correct indexes, no optimized queries, no comments hinting at the fix).
- No syntax or execution errors in any SQL file — the database must be fully queryable from the start.
- **NO comments** that reveal the solution or give hints in any generated file.

### Data Generation Strategy (CRITICAL)
- The fact table MUST use `generate_series` to produce 50,000–200,000 rows efficiently. Example pattern:
  ```sql
  INSERT INTO fact_sales (product_id, customer_id, region_id, sale_date, amount, quantity)
  SELECT
    (random() * 999 + 1)::int,
    (random() * 4999 + 1)::int,
    (random() * 9 + 1)::int,
    DATE '2022-01-01' + (random() * 730)::int,
    ROUND((random() * 9900 + 100)::numeric, 2),
    (random() * 49 + 1)::int
  FROM generate_series(1, 100000);
  ```
- Dimension tables use realistic named inserts (hundreds of rows). Use `generate_series` for dimensions too if more than ~50 rows are needed.
- The large fact table must expose the performance issues clearly (full scans are costly at this scale, making EXPLAIN output instructive).

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources including Google, Stack Overflow, official PostgreSQL documentation, and AI-powered tools or LLMs.
- Tasks are designed to assess the candidate's ability to analyze, diagnose, and fix/optimize large-scale SQL, not rote memorization. Complexity must require genuine problem-solving — understanding of analytical query patterns, EXPLAIN output interpretation, and performance concepts for large data volumes — that goes beyond simple copy-pasting.

### Code Generation Instructions
Based on real-world scenarios, create a SQL large-scale datasets task that:
- Draws inspiration from ONE input scenario for business context and technical focus
- Matches BASIC proficiency (1-2 years SQL/large-scale data experience)
- Can be completed within {minutes_range} minutes using only SQL and a database client (psql, pgAdmin, DBeaver)
- Tests practical large-scale SQL skills: analytics queries, window functions, CTEs, index optimization, non-sargable predicate fixes, or aggregation correctness
- Selects a different real-world scenario each time for variety
- Uses a star-schema-style layout (1 large fact table + 2–4 dimension tables), with clear success criteria (measurable performance improvement or correct query results on the large dataset)

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the large-scale analytics scenario and specific ask — what SQL/database problem must the candidate fix, write, or optimize? Include what is wrong or missing in the current database (e.g. slow aggregation, incorrect window function results, missing index on fact table) and what the candidate must deliver.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Objectives, Database Access, How to Verify, and Helpful Tips in that order (see README structure below)",
    ".gitignore": "PostgreSQL/Docker and development exclusions",
    "docker-compose.yml": "PostgreSQL service only (no version specs, no .env; hardcoded config)",
    "run.sh": "Script to start containers and wait for DB ready — deployment must succeed in one go",
    "kill.sh": "Script to tear down containers, volumes, and remove task directory",
    "init_database.sql": "Star-schema creation with large fact table (50k–200k rows via generate_series) and dimension tables, plus intentional basic-level performance/logic issues — single file, zero errors",
    "sample_queries.sql": "Sample analytics queries that demonstrate current performance or correctness problems on the large dataset"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion (e.g. faster analytics queries, correct window function results, index scans replacing sequential scans on fact table).",
  "short_overview": "Bullet-point list: (1) business context and large-scale data problem, (2) what the candidate must do in SQL, (3) expected outcome.",
  "pre_requisites": "Bullet-point list of tools and knowledge: Docker, Docker Compose, PostgreSQL client (psql/pgAdmin/DBeaver), SQL core constructs, window functions (ROW_NUMBER/RANK/SUM OVER), CTEs, EXPLAIN, basic indexing, star schema concepts, NULL handling, and large-scale data awareness.",
  "answer": "High-level solution approach (which indexes, query rewrites, CTE restructuring, or window function fixes; no full code). Include specific reasoning about why each fix improves performance or correctness at large data volumes.",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but nudge toward the right large-scale SQL analysis approach.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (SQL Large Scale Datasets Basic)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the specific large-scale SQL analytics scenario being generated.

1. Task Overview (MANDATORY — 2–3 substantial sentences)
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview (MANDATORY — 2–3 substantial sentences)

**CRITICAL**: Describe the specific business analytics scenario where a PostgreSQL database (with a large fact table of hundreds of thousands of rows) is experiencing performance or correctness issues in its analytical queries or reports. Explain that the database is fully deployed and populated (schema and data load in one go with no deployment failure), but has intentional basic-level issues (e.g. slow aggregation reports, incorrect ranking results, full scans on the fact table, missing indexes on high-cardinality columns) that the candidate must identify and fix using SQL only. Connect the business problem to the need for efficient large-scale SQL analytics. Make clear this is a **time-bounded SQL optimization/fix task** — the candidate only fixes or improves the given SQL problem; they do not fix deployment or setup. The README.md content MUST be fully populated with meaningful, specific content. ALL sections must have substantial content — no empty or placeholder text allowed.

### Objectives

Define goals focusing on outcomes for the analytics optimization/fix task:

- Clear, measurable goals appropriate for BASIC large-scale SQL proficiency (e.g. rewrite a slow aggregation query using a CTE and appropriate index, fix incorrect ROW_NUMBER partitioning, replace a non-sargable date filter with a range predicate, add a composite index for a JOIN-heavy fact query).
- What the candidate should be able to do successfully to demonstrate task completion. Objectives will be used to verify completion and award points.
- Scope achievable within the allocated time; objectives serve as benchmarks for task completion and scoring.

**CRITICAL**: Focus on measurable, verifiable outcomes (e.g. index scan replacing sequential scan, correct analytics result, faster execution time on large fact table).

### Database Access

- Provide the database connection details (host: use placeholder `<DROPLET_IP>`, port, database name, username, password).
- Mention that candidates can use any preferred database client tools (e.g. pgAdmin, DBeaver, psql, DataGrip) for analysis and running SQL.
- Note that the database contains a large fact table with hundreds of thousands of rows representing a production analytics dataset.

### How to Verify

- Specific checkpoints after the candidate's fix: how to run sample queries, what to measure (execution time, EXPLAIN cost, result correctness), and how to confirm success (e.g. EXPLAIN shows index scan on fact table instead of sequential scan, window function returns correct ranked results, aggregation returns expected totals).
- Observable behaviors to validate large-scale query performance or correctness improvements.
- Methods to measure before/after (query timing with `\timing` in psql, EXPLAIN ANALYZE, result set comparison).
- Include concrete steps or commands where helpful.

**CRITICAL**: Focus on measurable, verifiable improvements relevant to large-scale analytics.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider how large fact tables differ from small tables when thinking about query performance — full scans become very expensive at scale
- Think about which columns in the fact table are used in WHERE clauses, JOINs, and window function PARTITION BY / ORDER BY, and whether they have appropriate indexes
- Explore how EXPLAIN ANALYZE reveals sequential scans and high estimated row counts on the fact table
- Consider how CTEs (WITH clauses) can help break a complex analytics query into readable, reusable steps
- Think about whether date/time filters in WHERE clauses are written in a way that allows index use (sargable vs non-sargable predicates)
- Review how window functions (ROW_NUMBER, RANK, SUM OVER PARTITION BY) work and what PARTITION BY and ORDER BY mean in an analytics context
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions or specific index names/query rewrites.

### NOT TO INCLUDE:
- Manual deployment instructions (environment is automated via run.sh; deployment succeeds in one go)
- Instructions to run run.sh (deployment is automated)
- Specific optimization solutions or exact SQL that gives away the answer
- Step-by-step solution guides, index names, or query rewrites that reveal the fix
- Phrases like "you should implement", "add the following code"

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, the database must be created and fully populated in one go. Deployment must NOT fail. The candidate receives a working database from the start; their only job is to fix or improve the given SQL problem.

### docker-compose.yml
- PostgreSQL service only — no other services.
- Hardcoded database name, username, and password — no `.env` file references, no environment variable placeholders.
- Mount `init_database.sql` to `/docker-entrypoint-initdb.d/init_database.sql` so PostgreSQL runs it automatically on first start.
- Expose port `5432` on the host.
- **No `version:` field** in the compose file.
- Use a named volume for PostgreSQL data (e.g. `pgdata`) so the container survives restarts during the session.
- No application containers, no additional services.

### run.sh
Generate this script with the following EXACT structure and behaviour:

**run.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- Replace `<db_user>`, `<db_name>`, `<fact_table_name>` with the actual hardcoded values from the task.
- The health check loop MUST use `docker-compose exec -T postgres psql` — do NOT use `pg_isready` alone as it returns ready before init scripts finish.
- The row count validation MUST query the main fact table to confirm `generate_series` data was loaded successfully.
- If either check fails, print the docker-compose logs and exit with code 1.
- No manual `psql -f` or `psql < file.sql` commands — PostgreSQL auto-runs `/docker-entrypoint-initdb.d/` scripts.
- End with a clear success message showing the connection string.

### kill.sh
Generate this script with the following EXACT structure — this is the required cleanup pattern:

**kill.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- MUST `cd /root/task` first so `docker-compose down` can find the `docker-compose.yml`.
- MUST run `docker-compose down --rmi all --volumes --remove-orphans` to remove compose-managed containers, named volumes, networks, and images in one step.
- MUST then explicitly force-stop ALL running containers with `docker ps -q` — this catches any container that `docker-compose down` missed.
- MUST explicitly remove ALL containers with `docker ps -aq` before pruning.
- MUST run `docker volume prune -f`, then `docker image prune -a -f`, then `docker system prune -a --volumes -f` — in this order. Running all three ensures nothing is left behind even if earlier steps partially succeed.
- MUST `rm -rf /root/task` as the final step after all Docker cleanup is done.
- Every destructive command MUST end with `|| true` so the script never exits early due to "already removed" errors.
- The script MUST be idempotent — safe to run multiple times on an already-clean droplet.
- Print a progress message before every major step.
- End with `echo "[kill.sh] Cleanup completed."`.

### init_database.sql
- Single file that runs to completion without errors. Creates schema (fact table + dimension tables), then inserts all data using `generate_series` for the large fact table.
- Intentional issues are logical/performance only — no syntax or runtime errors.
- No solution hints in comments.

### sample_queries.sql
- Analytics queries that currently run slowly or return incorrect results on the large fact table.
- Optional: include EXPLAIN output examples showing poor performance.
- Do not include fixed or optimized versions.

## CRITICAL REMINDERS

1. **SQL only** — No FastAPI, Flask, or any application code. Candidate works with SQL and a database client only.
2. **Large-scale schema** — The fact table MUST have 50,000–200,000 rows generated via `generate_series`. Dimension tables use realistic named data (hundreds to low thousands of rows). This models production large-scale analytics.
3. **Deployment must succeed in one go** — After run.sh, the database must be created, all data added, and everything working. No failed deployment. The candidate only fixes or improves SQL.
4. **Database must be fully queryable** — Schema and data load from init_database.sql with zero errors. Candidate connects and works with the DB; they do not fix setup or SQL syntax/runtime errors.
5. **Starter schema/data must match the "problem"** — Intentional issues are logical/performance only (missing indexes, non-sargable predicates, incorrect window partitioning, unbounded sorts). Provided SQL exhibits those issues without containing the solution or any execution errors.
6. **NO comments or files** that reveal the solution or give hints.
7. **Task must be completable within {minutes_range} minutes** by someone with 1-2 years of large-scale SQL/analytics experience.
8. **Focus on BASIC large-scale SQL concepts** — Core constructs on large tables, simple window functions, CTEs, composite indexes, EXPLAIN, non-sargable predicate awareness, fact/dimension schema understanding.
9. **README.md MUST be fully populated** with Task Overview, Objectives, Database Access, How to Verify, Helpful Tips (in that order).
10. **Task name** must be short, under 50 characters, kebab-case.
11. **Star-schema layout** — 1 large fact table + 2–4 dimension tables, realistic analytics business context (sales, events, orders, metrics, clickstream, etc.), clear and measurable success criteria.
12. **Use generate_series** for the fact table — never write 50k+ individual INSERT statements. This keeps Docker init fast and reliable.
13. **Select a different real-world scenario** each time for variety.
"""

PROMPT_REGISTRY = {
    "SQL - Large Scale Datasets (BASIC)": [
        PROMPT_SQL_LARGE_SCALE_CONTEXT,
        PROMPT_SQL_LARGE_SCALE_INPUT_AND_ASK,
        PROMPT_SQL_LARGE_SCALE_BASIC,
    ]
}
