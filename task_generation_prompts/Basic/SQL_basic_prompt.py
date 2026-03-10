PROMPT_SQL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SQL_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an SQL assessment task.

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

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SQL_BASIC = """
# SQL Basic Task Requirements

## GOAL
As a technical architect super experienced in SQL and relational databases, you are given real-world scenarios and proficiency levels for SQL development. Your job is to generate an entire task definition, including database schema files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end using SQL only. The task is SQL/database only — no application code (no FastAPI, Flask, or other app frameworks).

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement or fix something using SQL only: e.g. write/fix queries, optimize performance, correct schema or data issues, add indexes, or complete missing SQL logic.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- **CRITICAL - FULLY FUNCTIONAL DEPLOYMENT**: The candidate receives a database that is created and populated in ONE GO. When run.sh is executed, the database must be created successfully, all schema and data must be loaded without errors, and the deployment must NOT fail. The environment must be fully working from the start. The candidate's ONLY job is to fix or improve the given SQL/database problem (e.g. add indexes, fix slow queries, correct logic)—they do NOT fix deployment, setup, or initialization failures.
- The database may have intentional basic-level issues (e.g. missing indexes, inefficient queries, simple schema gaps) that the candidate must identify and fix using SQL and database tools only. All such issues must be logical/performance issues only; there must be no syntax or runtime errors in the provided SQL.
- DO NOT GIVE AWAY THE SOLUTION in the schema files or documentation. The candidate must analyze and implement the fix.
- A part of the task completion is to watch the candidate apply correct SQL practices, design choices, and not just patch errors.
- The question should be a real-world scenario and not a trick question based on syntax gotchas.
- The complexity and specific ask must align with BASIC proficiency level (1-2 years SQL/database experience). For BASIC level, focus on:
  - SELECT, JOIN (2-3 tables), WHERE, ORDER BY, LIMIT, GROUP BY, basic aggregates
  - Primary keys, foreign keys, basic data types
  - Basic indexing (single-column indexes on frequently queried columns)
  - Simple query optimization and EXPLAIN
  - NULL handling, basic WHERE clause optimization
  - Understanding sequential vs index scans at a foundational level
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure all scenarios adhere to standard SQL and PostgreSQL best practices (current stable versions). Use a single database engine (PostgreSQL) for the task.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years SQL experience).
- **Task name**: short, under 50 characters, kebab-case (e.g. "sql-order-report-fix", "sql-index-optimization").

### Database and SQL File Requirements

**WHAT MUST BE INCLUDED:**
- A complete, working PostgreSQL database deployment (Docker-based): docker-compose.yml, run.sh, kill.sh, init_database.sql. **CRITICAL**: The database must be created and populated in one go when the environment is deployed. run.sh must result in a successful deployment with zero failures—schema created, all data inserted, database ready to query. The candidate only fixes or improves the given problem; they do not fix deployment or initialization.
- init_database.sql: schema with 2-4 tables, basic relationships (foreign keys, one-to-many), and realistic sample data—all in a single file that runs to completion without errors. The schema and data must intentionally include basic-level issues (e.g. missing indexes on frequently queried columns, simple inefficient queries) that the candidate will fix using SQL only. No syntax or execution errors in this file.
- sample_queries.sql: example queries that demonstrate the current performance or correctness problems (e.g. slow queries, wrong results). No solutions in this file.
- README.md with Task Overview, Helpful Tips, Database Access, Objectives, How to Verify (in that order). All sections fully populated.
- .gitignore suitable for the task (data dirs, logs, backups, IDE/OS files).

**WHAT MUST NOT BE INCLUDED:**
- DO NOT include any application code (no FastAPI, Flask, Node, etc.). The task is SQL and database only.
- DO NOT give away the solution in init_database.sql or any file (no correct indexes, no optimized queries, no comments that hint at the fix).
- If the task is to fix/optimize: the starter schema and data must run and be queryable, but exhibit the problems the candidate must fix. No syntactic errors in SQL.
- **NO comments** that reveal the solution or give hints in any generated file.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official SQL/PostgreSQL documentation, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to analyze, diagnose, and fix/optimize using SQL, rather than testing rote memorization. Complexity should reflect basic SQL proficiency and require genuine problem-solving beyond copy-pasting.

### Code Generation Instructions
Based on real-world scenarios, create an SQL task that:
- Draws inspiration from ONE input scenario for business context and technical focus
- Matches BASIC proficiency (1-2 years SQL/database experience)
- Can be completed within {minutes_range} minutes using only SQL and a database client (e.g. psql, pgAdmin, DBeaver)
- Tests practical SQL skills: queries, basic optimization, indexes, or simple schema/data fixes
- Select a different real-world scenario each time for variety
- Use 2-4 tables, simple relationships, and clear success criteria (measurable performance improvement or correct query results)

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask — what SQL/database problem must the candidate fix or implement? Include what is wrong or missing in the current database and what the candidate must deliver.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Database Access, Objectives, and How to Verify in that order (see README structure below)",
    ".gitignore": "PostgreSQL/Docker and development exclusions",
    "docker-compose.yml": "PostgreSQL service only (no version specs, no .env; hardcoded config)",
    "run.sh": "Script to start containers and wait for DB ready",
    "kill.sh": "Script to tear down containers, volumes, and clean task directory",
    "init_database.sql": "Schema creation and sample data with intentional basic-level issues (single file for execution order)",
    "sample_queries.sql": "Sample queries that demonstrate current performance or correctness problems"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion (e.g. faster queries, correct results, indexes in place).",
  "short_overview": "Bullet-point list: (1) business context and problem, (2) what the candidate must do in SQL, (3) expected outcome.",
  "pre_requisites": "Bullet-point list of tools and knowledge: Docker, Docker Compose, PostgreSQL client (psql/pgAdmin/DBeaver), basic SQL, EXPLAIN, basic indexing and query concepts, etc.",
  "answer": "High-level solution approach (which indexes, query changes, or schema fixes; no full code).",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but nudge toward good SQL/database analysis.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (SQL Basic)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the SQL/database optimization scenario being generated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a PostgreSQL database is experiencing performance or correctness issues. Explain that the database is fully deployed and populated (schema and data load in one go with no deployment failure), but has intentional basic-level issues (e.g. slow reports, missing indexes, incorrect query logic) that the candidate must identify and fix using SQL only. Connect the business problem to the need for basic-level SQL optimization. Make clear this is a **time-bounded optimization/fix task**—the candidate only fixes or improves the given problem; they do not fix deployment or setup. The README.md file content MUST be fully populated with meaningful, specific content relevant to basic-level SQL optimization. ALL sections must have substantial content - no empty or placeholder text allowed.

### Objectives

Define goals focusing on outcomes for the optimization/fix task:

- Clear, measurable goals for the candidate appropriate for basic SQL level (e.g. reduce query time for report X, ensure query Y returns correct results, add indexes for frequently queried columns).
- What the candidate should be able to do successfully to demonstrate task completion. Objectives will be used to verify completion and award points.
- Scope should be achievable within the allocated time; objectives serve as benchmarks for task completion and scoring.

**CRITICAL**: Focus on measurable, verifiable outcomes (e.g. faster execution, correct result set, index in place).

### Database Access

- Provide the database connection details (host (use placeholder e.g. <DROPLET_IP>), port, database name, username, password).
- Mention that candidates can use any preferred database client tools (e.g. pgAdmin, DBeaver, psql, DataGrip) for analysis and running SQL.

### How to Verify

- Specific checkpoints after the candidate's fix: how to run sample queries, what to measure (execution time, result correctness), and how to confirm success (e.g. EXPLAIN shows index usage, results match expected set).
- Observable behaviors to validate basic database performance or correctness improvements.
- Simple methods to measure and compare before/after (e.g. query timing, EXPLAIN output).
- Include concrete steps or commands where helpful.

**CRITICAL**: Focus on measurable, verifiable improvements.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider what kinds of basic performance or correctness issues might exist in the database (e.g. missing indexes, full table scans, inefficient queries)
- Think about which columns are frequently queried or used in JOINs and WHERE clauses
- Review how to use EXPLAIN to understand query execution and identify bottlenecks
- Consider foundational SQL/PostgreSQL concepts: indexes, sequential vs index scans, primary/foreign keys
- Explore which sample queries run slowly or return wrong results and why
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions or specific index names/query rewrites.

### NOT TO INCLUDE:
- Manual deployment instructions (environment is automated via run.sh; deployment must succeed in one go)
- Instructions to run run.sh (deployment is automated)
- Specific optimization solutions or exact SQL that gives away the answer
- Step-by-step solution guides or index names/query rewrites that reveal the fix
- Phrases like "you should implement", "add the following code"

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL - ONE-GO DEPLOYMENT**: When run.sh is executed, the database must be created and fully populated in one go. Deployment must NOT fail. The candidate must receive a working database from the start; their only job is to fix or improve the given SQL/database problem.

- **docker-compose.yml**: PostgreSQL service only. Hardcoded database name, user, password. Mount init SQL to `/docker-entrypoint-initdb.d/`. Expose port 5432. No version pin, no .env. Ensure PostgreSQL initializes successfully with the mounted SQL.
- **run.sh**: Run `docker-compose up -d`, wait for PostgreSQL to be fully ready and accepting connections, validate that the database is created and accessible. No manual SQL execution—PostgreSQL runs init scripts automatically. Deployment must succeed; candidate does not fix setup.
- **kill.sh**: Stop and remove containers and volumes, remove task directory (/root/task). Idempotent, use `|| true` where needed. Print progress; end with a clear "Cleanup completed" message.
- **init_database.sql**: Single file that runs to completion without errors: CREATE tables (2-4), relationships, then INSERT all sample data. The file must execute fully so that the database is created and populated in one go. Intentional issues are logical/performance only (e.g. missing indexes, no primary key on lookup)—no syntax or runtime errors. No solution hints in comments.
- **sample_queries.sql**: Queries that currently run slowly or return wrong results. Optional: include EXPLAIN output examples showing poor performance. Do not include fixed/optimized versions.

## CRITICAL REMINDERS

1. **SQL only** — No FastAPI, Flask, or any application code. Candidate works with SQL and database tools only.
2. **Deployment must succeed in one go** — After run.sh, the database must be created, all data added, and everything working. No failed deployment. The candidate only fixes or improves the given problem; they do not fix deployment or initialization.
3. **Database must be runnable** — Schema and data load fully from init_database.sql with zero errors. Candidate connects and works with the DB; they do not fix setup or SQL syntax/runtime errors.
4. **Starter schema/data must match the "problem"** — Intentional issues are logical/performance only (e.g. missing indexes, slow queries). The provided SQL must exhibit those issues without containing the solution or any execution errors.
5. **NO comments or files** that reveal the solution or give hints.
6. **Task must be completable within {minutes_range} minutes** by someone with 1-2 years SQL experience.
7. **Focus on basic SQL concepts** — SELECT, JOINs, WHERE, indexes, EXPLAIN, primary/foreign keys, simple optimization.
8. **README.md MUST be fully populated** with Task Overview, Helpful Tips, Database Access, Objectives, How to Verify (in that order).
9. **Task name** must be short, under 50 characters, kebab-case.
10. **Select a different real-world scenario** each time for variety.
11. **2-4 tables**, simple relationships, clear and measurable success criteria.
"""

PROMPT_REGISTRY = {
    "SQL (BASIC)": [
        PROMPT_SQL_BASIC_CONTEXT,
        PROMPT_SQL_BASIC_INPUT_AND_ASK,
        PROMPT_SQL_BASIC,
    ]
}
