PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role.

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competency:
{competencies}

Please briefly summarize your understanding of the company context, the role expectations, and the kind of PostgreSQL large-scale data work this assessment should target.
"""

PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, here are the concrete inputs for generating the assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST PICK EXACTLY ONE scenario from the real-world scenarios above.
- The task's business domain, current implementation problem, and candidate task list MUST come from that chosen scenario.
- The employer described in the company context is administering the assessment; it is NOT the business domain unless the chosen scenario explicitly says so.
- The task must align with INTERMEDIATE proficiency and be realistically completable within {minutes_range} minutes.
- The task must assess PostgreSQL work on large datasets and operationally realistic database behavior, not generic software engineering.
- The task should feel like work a 3-5 year backend/data engineer would do on an existing system with meaningful data volume and production-like constraints.

Before generating the full task, briefly confirm:
1. Which single scenario you picked.
2. What the business domain and current database problem will be.
3. What kind of PostgreSQL deliverables the candidate will modify or add.
"""

PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
You are an expert PostgreSQL architect designing an INTERMEDIATE assessment for PostgreSQL - Large Scale Datasets.

Generate a realistic task where the candidate works on an existing PostgreSQL environment handling large data volume and production-like operational concerns. The task must require 4-5 intermediate concepts combined, but remain solvable within {minutes_range} minutes.

The candidate should work primarily through SQL, PostgreSQL configuration-adjacent artifacts, and operational scripts/documentation. Do not turn this into an application-framework task.

## HARD SCOPE BOUNDARY
You MUST stay within the competency scope implied by:
- PostgreSQL architecture awareness: process model, shared buffers, WAL, autovacuum behavior
- Size/statistics interpretation using pg_class and pg_stat_* views
- Scalable schema design, data types, keys, schema evolution, audit/history tables
- Index selection and maintenance: B-tree, GIN, BRIN, partial indexes, expression indexes, index usage analysis
- EXPLAIN / EXPLAIN ANALYZE interpretation and planner-aware query optimization
- Table partitioning design, lifecycle handling, and bloat awareness
- MVCC, isolation levels, lock contention diagnosis, batched/bulk operations
- Autovacuum tuning awareness, VACUUM / REINDEX scheduling, bloat diagnosis
- COPY, staging tables, ETL patterns, WAL/index/constraint trade-offs
- Streaming replication, failover basics, backup/restore and PITR participation
- Monitoring with PostgreSQL stats plus Prometheus/Grafana awareness, key metrics, capacity planning
- RBAC, basic encryption awareness, row-level security, retention/auditing
- Core tools such as psql, pg_dump, pg_basebackup, pg_repack, PgBouncer, Flyway/Liquibase
- Operational collaboration, documentation, incident-response style reasoning

Do NOT require concepts outside that scope as primary skills.

## SCENARIO LOCK (mandatory)
- You MUST pick EXACTLY ONE scenario from `real_world_task_scenarios`.
- The generated task's BUSINESS DOMAIN must match the chosen scenario's domain exactly. DO NOT invent a new domain.
- The generated task's CURRENT IMPLEMENTATION problem and YOUR TASK bullet list must come from the chosen scenario, adapted to PostgreSQL large-scale dataset work.
- The candidate's EMPLOYER is described in `organization_background`. That employer is administering the assessment; it is NOT the task domain unless the chosen scenario explicitly says so.
- If you find yourself writing about a domain that does NOT appear in `real_world_task_scenarios`, STOP and restart with one listed scenario.
- When `real_world_task_scenarios` is empty or "(none provided)", explicitly state which generic domain you picked and why. Do not silently default to the employer's domain.

## TASK SHAPE
Create a task where the candidate receives a working PostgreSQL-focused repository with intentionally suboptimal large-scale data design and operations. The candidate should need to inspect schema, data-loading flow, query plans, statistics, and maintenance/operational artifacts, then improve them.

The task should feel like one of these shapes, adapted to the chosen scenario:
- large fact table query slowdown with poor indexing and missing partitioning
- bulk ingestion pipeline causing WAL/locking pain and stale statistics
- audit/history table growth causing bloat and poor retention handling
- reporting query degradation due to planner-unfriendly predicates and missing expression/partial indexes
- high-concurrency update workflow with lock contention and poor batching
- operational readiness gap around monitoring, backup/restore notes, or replication lag interpretation

Use 4-5 intermediate concepts together, for example:
- EXPLAIN analysis + index redesign + partitioning
- COPY/staging ETL + WAL/index trade-offs + post-load maintenance
- pg_stat_* diagnosis + autovacuum/bloat remediation plan + query rewrite
- MVCC/locking diagnosis + batching strategy + index support
- schema evolution + audit/history design + retention/RLS basics

## PROFICIENCY CALIBRATION
INTERMEDIATE means:
- 3-5 years experience
- 45-60 minute task
- 4-5 concepts combined
- proper testing/verification, error handling, and performance reasoning are expected

Do NOT make it a full system design exercise.
Do NOT require microservices or unrelated application code.
Do NOT require advanced security hardening beyond basic RBAC / RLS / retention / auditing that is already in scope.

## PERSONA AND TEMPLATE CAPABILITIES
This template is for persona: data.
Primary runtime is SQL-oriented.
Datastore containers may be available through docker compose, but this assessment must remain centered on PostgreSQL because that is the competency being assessed.

Infrastructure expectations for this persona:
- Include database-focused files, not web application code.
- Because datastore support is available, include a `docker-compose.yml`.
- `run.sh` should use `docker compose up -d`.
- `kill.sh` should use `docker compose down`.
- Include PostgreSQL initialization SQL and any supporting SQL/scripts needed for the task.
- You may include monitoring/config/reference files if they help the scenario, but keep the repository compact.

Do not include MySQL-specific task requirements unless the chosen scenario explicitly needs a comparison artifact. PostgreSQL must remain the primary and only assessed database engine.

## REQUIRED REPOSITORY STYLE
Generate a compact but realistic repository. Prefer files such as:
- README.md
- .gitignore
- docker-compose.yml
- run.sh
- kill.sh
- init_database.sql
- sample_queries.sql
- diagnostics.sql
- expected_metrics.md
- optional files like retention_policy.sql, load_data.sql, or monitoring_notes.md if scenario-appropriate

The environment should start successfully and initialize the PostgreSQL database automatically through mounted SQL files.

## DATABASE CONTENT REQUIREMENTS
Your generated SQL should create a realistic large-data scenario:
- multiple related tables, typically 4-8 tables
- at least one clearly large table or partitioned candidate table
- realistic row counts or data-generation SQL sufficient to expose planner/index/maintenance issues
- intentionally suboptimal choices that the candidate can improve
- no direct solution comments in code files

Possible intentional issues, chosen according to the scenario:
- missing or wrong index type
- missing composite index on common filter/sort path
- planner-unfriendly predicate shape
- non-partitioned append-heavy table that should be partitioned
- poor retention/history handling
- bulk load path that updates indexes/constraints inefficiently
- stale stats / missing ANALYZE step in workflow
- lock-heavy update/delete pattern
- bloat-prone maintenance gap
- weak role / RLS / audit setup for a large shared dataset
- missing operational notes for backup/restore or replication checks

## WHAT THE CANDIDATE SHOULD DO
The candidate-facing task should ask for concrete improvements, such as:
- analyze current schema and query plans
- improve query performance for a named workload
- add or revise indexes
- introduce or complete a partitioning strategy
- improve bulk-load or staging flow
- reduce lock contention through batching or transaction changes
- add or refine audit/history or retention handling
- add monitoring/diagnostic SQL for key metrics
- document verification steps and operational trade-offs

Do not ask them to build an API or frontend.

## README REQUIREMENTS
README.md must contain meaningful, scenario-specific sections:
- Task Overview
- Database Access
- Guidance
- Objectives
- How to Verify

README must:
- describe the chosen business domain from the scenario
- explain the current implementation problem without revealing the exact fix
- mention database access details using <DROPLET_IP> placeholder
- include measurable verification guidance such as EXPLAIN ANALYZE improvements, reduced scanned rows, better index usage, lower lock wait exposure, improved maintenance workflow, or cleaner partition pruning
- avoid manual deployment instructions
- avoid giving exact solutions

## RUN / CLEANUP REQUIREMENTS
### docker-compose.yml
- Must not include a version field.
- Must not use .env references.
- Use hardcoded values.
- Must define a PostgreSQL service.
- Mount SQL initialization files into `/docker-entrypoint-initdb.d/`.
- Expose PostgreSQL on 5432.
- Keep it simple and valid.

### run.sh
- Use `docker compose up -d`
- Wait until PostgreSQL is ready
- Validate connectivity with psql or pg_isready
- Print useful status logs
- No package installation steps for PostgreSQL itself

### kill.sh
- Use `docker compose down --volumes --remove-orphans || true`
- Remove task-local artifacts if created
- Be idempotent
- Print progress logs

## OUTPUT JSON SCHEMA
Return exactly one JSON object using these exact top-level keys:
- "name"
- "question"
- "code_files"
- "answer"
- "definitions"
- "hints"
- "outcomes"
- "pre_requisites"
- "short_overview"

Do NOT use alternate key names.

Use this exact shape:
{{
  "name": "Short task title under 50 words",
  "question": "Full candidate-facing task description",
  "code_files": {{
    "README.md": "full file content",
    ".gitignore": "full file content",
    "docker-compose.yml": "full file content",
    "run.sh": "full file content",
    "kill.sh": "full file content",
    "init_database.sql": "full file content",
    "sample_queries.sql": "full file content"
  }},
  "answer": {{
    "summary": "high-level evaluator summary",
    "key_points": [
      "point 1",
      "point 2"
    ]
  }},
  "definitions": {{
    "term_1": "definition",
    "term_2": "definition"
  }},
  "hints": [
    "single gentle hint"
  ],
  "outcomes": [
    "expected outcome 1",
    "expected outcome 2"
  ],
  "pre_requisites": [
    "requirement 1",
    "requirement 2"
  ],
  "short_overview": [
    "overview point 1",
    "overview point 2"
  ]
}}

## FILE CONTENT RULES
- Every file in `code_files` must contain full contents, not summaries.
- SQL must be valid PostgreSQL SQL.
- Shell scripts must be executable-style bash.
- Do not include solution-revealing comments.
- Keep the repository size reasonable for an interview task.
- Ensure the task is self-contained and realistic.

## QUALITY BAR
The best tasks for this competency:
- feel like a real production incident or backlog item in the chosen scenario domain
- require diagnosis, not just syntax editing
- make the candidate reason about large-scale PostgreSQL behavior
- include measurable before/after verification
- stay focused on PostgreSQL large-scale datasets rather than drifting into generic backend work

Generate the JSON only.
"""

PROMPT_REGISTRY = {
    "PostgreSQL - Large Scale Datasets (INTERMEDIATE)": [
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_CONTEXT,
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_POSTGRESQL_LARGE_SCALE_DATASETS_INTERMEDIATE_INSTRUCTIONS,
    ]
}