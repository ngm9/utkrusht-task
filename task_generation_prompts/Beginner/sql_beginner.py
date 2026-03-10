PROMPT_SQL_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SQL_BEGINNER_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (BEGINNER: 0-1 year SQL experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SQL_BEGINNER = """
# SQL Beginner Task Requirements

## GOAL
As a technical architect super experienced in SQL and relational databases, you are given real-world scenarios and proficiency levels for SQL development. Your job is to generate an entire task definition, including database schema files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to think, design, write, and fix simple SQL. The task is SQL/database only — no application code. The level is BEGINNER (0-1 year SQL experience).

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to write or fix simple SQL only: e.g. write a SELECT query for a report, fix a wrong query (incorrect WHERE/JOIN/aggregate), complete a missing filter or ORDER BY, or write a simple JOIN between two tables.
- The question scenario must be clear, with facts and context historically accurate and relevant.
- **CRITICAL - FULLY FUNCTIONAL DEPLOYMENT**: The candidate receives a database that is created and populated in ONE GO. When run.sh is executed, the database must be created successfully, all schema and data must be loaded without errors, and the deployment must NOT fail. The environment must be fully working from the start. The candidate's ONLY job is to write or fix the given SQL (e.g. correct a query, add a simple report)—they do NOT fix deployment, setup, or initialization failures.
- The database has a simple, correct schema (2-3 tables, primary/foreign keys). Intentional issues are only in the *queries* or *task ask* (e.g. a sample query that returns wrong results, or a report the candidate must write from scratch). There must be no syntax or runtime errors in the provided init_database.sql.
- DO NOT GIVE AWAY THE SOLUTION in the schema files, sample_queries.sql, or documentation. The candidate must figure out the correct query or fix.
- The question should be a real-world scenario and not a trick based on syntax gotchas.
- The complexity must align with BEGINNER proficiency (0-1 year). For BEGINNER, focus only on:
  - SELECT with WHERE, ORDER BY, LIMIT
  - Tables, columns, primary keys, foreign keys (understanding only; candidate is not asked to design schema)
  - Simple JOINs between two tables (one join condition)
  - Basic aggregates: COUNT, SUM, AVG, MIN, MAX and GROUP BY on one column
  - Running queries in a client (psql, pgAdmin, DBeaver)
- Do NOT require: indexing, EXPLAIN, query optimization, multi-table complex JOINs, subqueries, or window functions.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure all scenarios use standard SQL and PostgreSQL (current stable). Use a single database engine (PostgreSQL).
- If you include diagrams, use mermaid format, properly indented and in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BEGINNER proficiency (0-1 year SQL experience).
- **Task name**: short, under 50 characters, kebab-case (e.g. "sql-sales-report", "sql-fix-order-query").

### Database and SQL File Requirements

**WHAT MUST BE INCLUDED:**
- A complete, working PostgreSQL database deployment (Docker-based): docker-compose.yml, run.sh, kill.sh, init_database.sql. **CRITICAL**: The database must be created and populated in one go when the environment is deployed. run.sh must result in a successful deployment with zero failures—schema created, all data inserted, database ready to query. The candidate only writes or fixes the given SQL; they do not fix deployment or initialization.
- init_database.sql: schema with 2-3 tables, simple relationships (foreign keys, one-to-many), and realistic sample data—all in a single file that runs to completion without errors. The schema itself should be correct and simple (no intentional schema bugs for beginner). The *task* is about writing or fixing a query, not the schema.
- sample_queries.sql: one or more example queries that are either wrong (candidate must fix) or placeholders showing what kind of report is needed (candidate must write the query). No solutions in this file.
- README.md with Task Overview, Helpful Tips, Database Access, Objectives, How to Verify (in that order). All sections fully populated.
- .gitignore suitable for the task (data dirs, logs, backups, IDE/OS files).

**WHAT MUST NOT BE INCLUDED:**
- DO NOT include any application code. The task is SQL only.
- DO NOT give away the correct query or the fix in any file or comments.
- **NO comments** that reveal the solution or give hints in any generated file.

### AI and External Resource Policy
- Candidates are permitted to use external resources (Google, Stack Overflow, documentation, AI tools). Tasks should still require understanding of simple SQL (SELECT, WHERE, JOIN, aggregates) rather than pure copy-paste.

### Code Generation Instructions
Based on real-world scenarios, create an SQL beginner task that:
- Draws inspiration from ONE input scenario for business context
- Matches BEGINNER proficiency (0-1 year SQL experience)
- Can be completed within {minutes_range} minutes using only SQL and a database client
- Tests simple SQL: writing a report query, fixing a wrong query, or completing a missing WHERE/JOIN/ORDER BY/aggregate
- Select a different real-world scenario each time for variety
- Use 2-3 tables, simple relationships, one clear ask (one report or one query to fix)

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed/implemented?",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Database Access, Objectives, and How to Verify in that order (see README structure below)",
    ".gitignore": "PostgreSQL/Docker and development exclusions",
    "docker-compose.yml": "PostgreSQL service only (no version specs, no .env; hardcoded config)",
    "run.sh": "Script to start containers and wait for DB ready",
    "kill.sh": "Script to tear down containers, volumes, and clean task directory",
    "init_database.sql": "Schema creation and sample data with intentional beginner-level issues (single file for execution order)",
    "sample_queries.sql": "Sample queries that demonstrate current performance or correctness problems"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion (e.g. faster queries, correct results, indexes in place).",
  "short_overview": "Bullet-point list: (1) business context and problem, (2) what the candidate must do in SQL, (3) expected outcome.",
  "pre_requisites": "Bullet-point list of tools, knowledge, and environment required to complete the beginner-level task. Mention things like Docker, Docker Compose, PostgreSQL client tools (pgAdmin/DBeaver/psql), basic SQL knowledge, etc.",
  "answer": "High-level solution approach focusing on beginner database/query strategies for the given simple issues. No full code.",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate toward simple SQL/database analysis.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (SQL Beginner)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the SQL/database scenario being generated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a PostgreSQL database has a simple query or correctness issue. Explain that the database is fully deployed and populated (schema and data load in one go with no deployment failure), but has intentional beginner-level issues (e.g. wrong query results, missing report query, incorrect filter or JOIN) that the candidate must identify and fix using SQL only. Connect the business problem to the need for beginner-level SQL. Make clear this is a **time-bounded optimization/fix task**—the candidate only fixes or improves the given problem; they do not fix deployment or setup. The README.md file content MUST be fully populated with meaningful, specific content relevant to beginner-level SQL. ALL sections must have substantial content - no empty or placeholder text allowed.

### Objectives

Define goals focusing on outcomes for the optimization/fix task:

- Clear, measurable goals for the candidate appropriate for beginner SQL level (e.g. write query that returns X, fix the query so it correctly filters by Y, ensure report shows correct columns).
- What the candidate should be able to do successfully to demonstrate task completion. Objectives will be used to verify completion and award points.
- Scope should be achievable within the allocated time; objectives serve as benchmarks for task completion and scoring.

**CRITICAL**: Focus on measurable, verifiable outcomes (e.g. correct result set, correct columns, correct counts).

### Database Access

- Provide the database connection details (host (use placeholder e.g. <DROPLET_IP>), port, database name, username, password).
- Mention that candidates can use any preferred database client tools (e.g. pgAdmin, DBeaver, psql, DataGrip) for analysis and running SQL.

### How to Verify

- Specific checkpoints after the candidate's fix: how to run sample queries, what to measure (result correctness, row counts), and how to confirm success (e.g. results match expected set).
- Observable behaviors to validate beginner-level database correctness improvements.
- Simple methods to measure and compare before/after (e.g. query results, expected vs actual).
- Include concrete steps or commands where helpful.

**CRITICAL**: Focus on measurable, verifiable improvements.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider which tables and columns are relevant to the report or fix
- Think about how the tables are related (foreign keys) for JOINs
- Review simple SELECT, WHERE, ORDER BY, and aggregate usage
- Consider foundational SQL concepts: primary/foreign keys, simple JOINs, basic aggregates
- Explore which sample queries return wrong results and why
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions or specific query rewrites.

### NOT TO INCLUDE:
- Manual deployment instructions (environment is automated via run.sh; deployment must succeed in one go)
- Instructions to run run.sh (deployment is automated)
- Specific optimization solutions or exact SQL that gives away the answer
- Step-by-step solution guides or query rewrites that reveal the fix
- Phrases like "you should implement", "add the following code"

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL - ONE-GO DEPLOYMENT**: When run.sh is executed, the database must be created and fully populated in one go. Deployment must NOT fail. The candidate must receive a working database from the start; their only job is to fix or improve the given SQL/database problem.

- **docker-compose.yml**: PostgreSQL service only. Hardcoded database name, user, password. Mount init SQL to `/docker-entrypoint-initdb.d/`. Expose port 5432. No version pin, no .env. Ensure PostgreSQL initializes successfully with the mounted SQL.
- **run.sh**: Run `docker-compose up -d`, wait for PostgreSQL to be fully ready and accepting connections, validate that the database is created and accessible. No manual SQL execution—PostgreSQL runs init scripts automatically. Deployment must succeed; candidate does not fix setup.
- **kill.sh**: Stop and remove containers and volumes, remove task directory (/root/task). Idempotent, use `|| true` where needed. Print progress; end with a clear "Cleanup completed" message.
- **init_database.sql**: Single file that runs to completion without errors: CREATE tables (2-3), relationships, then INSERT all sample data. The file must execute fully so that the database is created and populated in one go. Intentional issues are logical/correctness only (e.g. wrong query in sample_queries.sql, missing report)—no syntax or runtime errors in init_database.sql. No solution hints in comments.
- **sample_queries.sql**: Queries that currently run slowly or return wrong results. Do not include fixed/optimized versions.

## CRITICAL REMINDERS

1. **SQL only** — No FastAPI, Flask, or any application code. Candidate works with SQL and database tools only.
2. **Deployment must succeed in one go** — After run.sh, the database must be created, all data added, and everything working. No failed deployment. The candidate only fixes or improves the given problem; they do not fix deployment or initialization.
3. **Database must be runnable** — Schema and data load fully from init_database.sql with zero errors. Candidate connects and works with the DB; they do not fix setup or SQL syntax/runtime errors.
4. **Starter schema/data must match the "problem"** — Intentional issues are logical/correctness only (e.g. wrong query, missing report). The provided SQL must exhibit those issues without containing the solution or any execution errors in init_database.sql.
5. **NO comments or files** that reveal the solution or give hints.
6. **Task must be completable within {minutes_range} minutes** by someone with 0-1 years SQL experience.
7. **Focus on beginner SQL concepts** — SELECT, WHERE, ORDER BY, LIMIT, simple two-table JOIN, basic aggregates, GROUP BY on one column. No indexing, EXPLAIN, or optimization.
8. **README.md MUST be fully populated** with Task Overview, Objectives, Database Access, How to Verify, Helpful Tips (in that order).
9. **Task name** must be short, under 50 characters, kebab-case.
10. **Select a different real-world scenario** each time for variety.
11. **2-3 tables**, simple relationships, clear and measurable success criteria.
"""

PROMPT_REGISTRY = {
    "SQL": [
        PROMPT_SQL_BEGINNER_CONTEXT,
        PROMPT_SQL_BEGINNER_INPUT_AND_ASK,
        PROMPT_SQL_BEGINNER,
    ]
}
