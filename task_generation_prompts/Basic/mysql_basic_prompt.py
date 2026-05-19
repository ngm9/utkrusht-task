PROMPT_MYSQL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MYSQL_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a MySQL assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS (short summary — full task specification is in QUESTION PROMPT below):
{real_world_task_scenarios}

INPUT QUESTION PROMPT (THIS IS THE AUTHORITATIVE TASK SPECIFICATION — READ THIS IN FULL BEFORE DOING ANYTHING ELSE):
{question_prompt}

## THE QUESTION PROMPT IS THE MOST IMPORTANT INPUT

The QUESTION PROMPT above is the single most important input you have received. It defines exactly what the final task must look like: which tables exist, which columns they have, which queries the candidate must answer, which identifiers and thresholds are used, and what seed data must support. Before you write a single line of the task, you MUST read the entire QUESTION PROMPT carefully and treat it as the source of truth. The task you generate is essentially a faithful packaging of the QUESTION PROMPT into a deployable repository — not a re-imagining of it.

CRITICAL TASK GENERATION REQUIREMENTS:
- The QUESTION PROMPT above may contain a complete, embedded task specification (explicit table schemas in markdown tables, specific query questions, badge thresholds, seed-data requirements, schema notes).
- When the QUESTION PROMPT contains such a complete specification (it will be obvious — it will explicitly list named tables, named columns, and numbered query questions), you MUST use it VERBATIM:
  - Use the exact same table names and column definitions (data types, PK/FK, constraints).
  - Honour any "Schema notes" in the QUESTION PROMPT that add or clarify columns.
  - Use the exact same query questions, in the same order, with the same identifiers (history_id values, event_id values, email addresses, page_id values, thresholds).
  - Do NOT invent additional or alternative tables, columns, queries, thresholds, or identifiers.
  - Produce ONE task that contains ALL listed queries together. Do NOT split queries across multiple tasks.
- When the QUESTION PROMPT does NOT contain an embedded specification, fall back to drawing inspiration from the real-world scenarios and the role context to design the task from scratch (still keeping it MySQL Basic).
- Each numbered query in the embedded specification MUST appear as a numbered item in the README's Objectives section, in the same order, paraphrased into a one-line objective.
- Seed data must satisfy any "Seed-data requirements" listed in the QUESTION PROMPT so that every query returns a non-empty, verifiable result.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. Does the QUESTION PROMPT above contain an embedded, authoritative task specification (yes/no)?
2. If yes, list the table names, the number of queries, and any identifier values (history_id, event_id, email, page_id, thresholds) you have detected.
3. What will the task look like? Confirm that all queries will live in ONE task and will appear in the Objectives section.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_MYSQL_BASIC = """
# MySQL Basic Task Requirements

## GOAL
As a technical architect super experienced in MySQL and relational databases, you are given a fixed task specification (the QUESTION PROMPT delivered in the previous turn) and supporting context. Your job is to generate a complete deployable task — MySQL 8 schema + seed data, deployment scripts, candidate-facing README, and an empty solutions file — that asks the candidate to write **every listed query question** in one sitting. The task is MySQL/database only — no application code (no FastAPI, Flask, Node, etc.).

## READ THE QUESTION PROMPT IN FULL BEFORE GENERATING

The QUESTION PROMPT supplied in the previous turn is the most important input you have. It defines exactly what the task must look like — tables, columns, queries, identifiers, thresholds, seed-data requirements, schema notes. Before you write any of the output JSON, you MUST have read and internalised the entire QUESTION PROMPT. The schema in `init_database.sql`, the query list in the README, the Objectives, the seed data, and the column projections in the candidate's expected answers are all dictated by the QUESTION PROMPT. Do NOT begin generating files until you have a clear mental model of every table, every column, and every query from that prompt. The candidate must be asked to answer **every query** listed — no opt-out wording, no "answer any N of M" phrasing.

## CRITICAL — USE THE EMBEDDED SPECIFICATION VERBATIM
- The QUESTION PROMPT given in the previous turn IS the task specification. When it contains explicit table schemas (markdown tables with column names and types), explicit numbered query questions, identifier values (e.g. `history_id = 12345`, `event_id = 59`, `testing@nerdium.tech`, `page_id = 794`, badge thresholds), and seed-data requirements, you MUST reproduce them **exactly** in the task you generate.
- The candidate must receive the same six (or N) queries listed in the QUESTION PROMPT, in the same order, with the same wording and same identifiers.
- The schema you generate in `init_database.sql` must match the QUESTION PROMPT schema **column for column**, including any columns flagged in "Schema notes" (e.g. `m_email`, `d_is_anonymous`).
- All listed queries belong to ONE task. Do not omit any. Do not split into multiple tasks.

## INSTRUCTIONS

### Nature of the Task
- The task asks the candidate to write MySQL queries against a fully working, pre-populated MySQL 8 database. Each query has a well-defined business question and a specified column projection.
- **CRITICAL — FULLY FUNCTIONAL DEPLOYMENT**: The candidate receives a MySQL database that is created and populated in ONE GO. When `run.sh` is executed, the database container starts, the schema and all seed data load without errors, and the database is ready to query. The candidate's ONLY job is to write the queries — they do NOT fix deployment, setup, or initialization failures.
- The schema must be free of syntax or runtime errors. There are NO intentional bugs to fix — this is a **write-from-scratch query task**, not an optimization task.
- DO NOT include the candidate's query solutions anywhere in the repo (no answer comments in `init_database.sql`, no example SQL in the README, no hints that hand-feed the solution).
- The question scenario must use the business context and identifiers exactly as specified in the QUESTION PROMPT.
- The complexity and specific asks align with BASIC MySQL proficiency (1-2 years experience). Skills exercised include: SELECT with WHERE, INNER and LEFT JOIN across 2-3 tables, GROUP BY with HAVING, aggregates (SUM, COUNT), CASE WHEN for conditional and tiered output, arithmetic on columns, and ORDER BY.
- **Time Constraint**: The task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency.
- **Task name**: short, under 50 characters, kebab-case (e.g. `mysql-nerdium-fundraiser-queries`).

### Database and SQL File Requirements

**WHAT MUST BE INCLUDED:**
- A complete, working MySQL 8 database deployment (Docker-based): `docker-compose.yml`, `run.sh`, `kill.sh`, `init_database.sql`. The database must be created and populated in one go when the environment is deployed.
- `init_database.sql`: schema **exactly matching the QUESTION PROMPT** (tables, columns, types, PK/FK, ENUM values, CHAR flags) + seed data that satisfies every seed-data requirement listed. Single file, runs to completion without errors.
- `solutions.sql`: an **empty starter file** with a single placeholder comment per query (e.g. `-- Query 1: <one-line restatement>` followed by blank space). The candidate writes their answers in this file. **No solution SQL** in this file.
- `README.md` with Task Overview, Objectives, Database Access, Query Questions, How to Verify, Helpful Tips (in that order). All six (or N) query questions reproduced verbatim from the QUESTION PROMPT. All queries listed as numbered Objectives.
- `.gitignore` suitable for the task (MySQL data dirs, logs, IDE/OS files).

**WHAT MUST NOT BE INCLUDED:**
- DO NOT include any application code (no FastAPI, Flask, Node, etc.).
- DO NOT include solution SQL anywhere (not in `init_database.sql` comments, not in the README, not in `solutions.sql`).
- DO NOT include "intentional bugs" or performance issues in the schema — this is a write-the-queries task, not an optimize-the-database task.
- DO NOT invent new tables, columns, queries, or thresholds beyond what the QUESTION PROMPT specifies.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including Google, Stack Overflow, official MySQL documentation, and AI-powered tools.
- The tasks assess the candidate's ability to read a schema, understand a business question, and write a correct MySQL query — not memorisation.

### Code Generation Instructions
Generate a MySQL Basic task that:
- Uses the embedded task specification from the QUESTION PROMPT **verbatim**.
- Ships a fully working MySQL 8 Docker deployment.
- Includes seed data that makes every listed query return a non-empty, verifiable result.
- Lists all listed query questions in the README, in the same order, with the same identifiers.
- Lists all listed query questions as numbered Objectives in the README.
- Provides an empty `solutions.sql` for the candidate's answers.

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the business scenario (Nerdium charity fundraising platform per the embedded spec) and what the candidate must do: write all listed MySQL queries against the provided 3-table schema. Mention that the candidate writes their answers in solutions.sql.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Objectives, Database Access, Query Questions, How to Verify, Helpful Tips in that order (see README structure below). The Query Questions section must reproduce every query from the QUESTION PROMPT verbatim.",
    ".gitignore": "MySQL/Docker and development exclusions",
    "docker-compose.yml": "MySQL 8 service only (no version specs, no .env; hardcoded config)",
    "run.sh": "Script to start the MySQL container and wait for the DB to be ready",
    "kill.sh": "Script to tear down containers, volumes, and clean task directory",
    "init_database.sql": "Schema (exactly matching the QUESTION PROMPT) + seed data satisfying all seed-data requirements. Single file. No solution hints.",
    "solutions.sql": "Empty starter file with one placeholder comment that candidate need to write ther query here . NO solution SQL."
  }},
  "outcomes": "Bullet-point list in simple language. Each bullet is one of the listed queries restated as an outcome (e.g. 'Correctly returns Y/N for the orgmember check on history_id = 12345', 'Correctly lists every event_id = 59 participant with the requested columns', etc.). One bullet per query.",
  "short_overview": "Bullet-point list: (1) business context (Nerdium fundraising platform per the embedded spec), (2) what the candidate must do (write all listed MySQL queries in solutions.sql against the provided schema), (3) expected outcome (all queries return correct results when run against the seeded database).",
  "pre_requisites": "Bullet-point list of tools and knowledge: Docker, Docker Compose, MySQL 8 client (mysql CLI, MySQL Workbench, DBeaver, DataGrip), basic SQL (SELECT, JOIN, GROUP BY/HAVING, CASE WHEN, aggregates, arithmetic).",
  "answer": "High-level solution approach for each listed query (one short sentence per query covering join paths, filters, and aggregation — no full SQL).",
  "hints": "Single line suggesting focus areas (e.g. 'Read the schema carefully, mind the d_status enum and the is_complete flag, and use (d_amount - d_refund_amount) for net donation totals.'). Must NOT give away the answer.",
  "definitions": {{
    "fundraiser": "A member who has a row in members_history for a given event_id, with a target and a running total_raised",
    "net_paid_donation": "A paid donation reduced by its refund: (d_amount - d_refund_amount) where d_status = 'paid'",
    "orgmember": "A member_type value in members_history indicating an organisation-level fundraiser",
    "is_complete": "CHAR(1) flag on members_history; 'Y' means the fundraiser is closed/completed"
  }}
}}

## README.md STRUCTURE (MySQL Basic — fixed query-writing task)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated; no placeholder text.

1. Task Overview
2. Objectives
3. Database Access
4. Query Questions
5. How to Verify
6. Helpful Tips

### Task Overview (MANDATORY — 2-3 substantial sentences)
Describe the Nerdium fundraising platform context per the embedded spec. State that the candidate is given a fully deployed MySQL 8 database with three tables (`members`, `members_history`, `donations`) and realistic seed data, and must write a set of MySQL queries to answer specific business questions. Make clear this is a **write-from-scratch query task** — the database is fully working; the candidate's job is to write correct queries in `solutions.sql`.

### Objectives
Reproduce every query from the QUESTION PROMPT as a numbered objective, in the same order. Each objective is a one-line restatement of the corresponding query question (e.g. "1. Return 'Y' or 'N' for whether the fundraiser with history_id = 12345 is an orgmember."). The candidate is expected to answer **every listed query**. Do NOT include any "answer N of M" / "any 4 of 6" / opt-out phrasing in the README — every query is required. Objectives are used to verify completion and award points.

### Database Access
- Host: `<DROPLET_IP>` placeholder
- Port: `3306`
- Database name: pick a sensible name (e.g. `nerdium`)
- Username and password: hardcoded values that match `docker-compose.yml`
- Mention preferred clients: `mysql` CLI, MySQL Workbench, DBeaver, DataGrip.

### Query Questions
Reproduce every query from the QUESTION PROMPT **verbatim**, in the same order, with the same identifiers, the same column projections, and the same constraints. Use the same numbering (Q1, Q2, ...). Include the badge-threshold table for the badge query. State that the candidate writes their answers in `solutions.sql` under the corresponding `-- Query N:` placeholder.

### How to Verify
- Explain how to connect with a MySQL client and run each query from `solutions.sql`.
- For each query, describe what a correct result looks like (e.g. "Q1 returns a single row with the value `Y`", "Q4 returns members with a `count` of 2", "Q6 returns at least 2 rows sorted descending by total raised").
- Mention that all queries should run cleanly against the seeded database with zero modifications to the schema or data.

### Helpful Tips
- Read the full schema (`init_database.sql`) carefully before writing any query.
- Note which columns are required by each question and project only those columns, in the order the question lists them.
- Mind the `d_status` ENUM filter (`'paid'`) and the `is_complete` CHAR flag (`'Y'`).
- Use `(d_amount - d_refund_amount)` for net donation amounts.
- Use `GROUP BY` + `HAVING` for the multi-event participation query.
- Use `CASE WHEN` for both the Y/N orgmember check and the tiered badge label.
- Use bullet points starting with "Consider", "Think about", "Review", "Note".

**CRITICAL**: Guide discovery, never provide direct SQL or solution snippets.

### NOT TO INCLUDE in README:
- Manual deployment instructions (deployment is automated via run.sh)
- Instructions to run run.sh
- Specific solution SQL or query patterns that give away the answer
- Phrases like "you should write `SELECT ...`"

## INFRASTRUCTURE REQUIREMENTS (Docker — MySQL 8)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, the database must be created and fully populated in one go. Deployment must NOT fail.

- **docker-compose.yml**: MySQL 8 service only. Hardcoded `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`. Mount `init_database.sql` to `/docker-entrypoint-initdb.d/`. Expose port 3306. No version pin, no .env. Ensure MySQL initializes successfully with the mounted SQL.
- **run.sh**: Run `docker-compose up -d`, wait for MySQL to be fully ready and accepting connections (e.g. `mysqladmin ping`), validate that the database and tables exist. No manual SQL execution — MySQL runs init scripts automatically.
- **kill.sh**: Stop and remove containers and volumes, remove task directory (`/root/task`). Idempotent, use `|| true` where needed. Print progress; end with a clear "Cleanup completed" message.
- **init_database.sql**: Single file that runs to completion. CREATE TABLES (exactly as specified in the QUESTION PROMPT, including the `m_email` and `d_is_anonymous` additions), then INSERT seed data that satisfies every seed-data requirement. No syntax or runtime errors. No solution hints in comments.
- **solutions.sql**: Empty starter file with placeholder comments only — one per query.

## CRITICAL REMINDERS

1. **Read the QUESTION PROMPT in full BEFORE generating.** It is the primary, authoritative input — the task is essentially a deployable packaging of that prompt.
2. **Use the QUESTION PROMPT verbatim** when it contains an embedded spec. Same tables, same columns, same queries, same identifiers, same thresholds.
3. **All queries live in ONE task.** Do not split.
4. **The candidate must answer every listed query.** Do NOT include any "answer any 4 of 6", "any N of M", or other opt-out phrasing in the README, Objectives, or anywhere else.
5. **All queries appear in Objectives.** Numbered, in order, one line each.
6. **Query Questions section reproduces every query verbatim** from the QUESTION PROMPT, including the badge-threshold table.
7. **MySQL only** — no application code.
8. **Deployment must succeed in one go.** The candidate only writes queries; they do not fix setup.
9. **No solution SQL anywhere.** Not in init_database.sql, not in README, not in solutions.sql.
10. **Seed data must make every query return non-empty, verifiable results** per the seed-data requirements.
11. **Task name** must be short, under 50 characters, kebab-case.
12. **Task must be completable within {minutes_range} minutes** by someone with 1-2 years MySQL experience.
"""

PROMPT_REGISTRY = {
    "MySQL (BASIC)": [
        PROMPT_MYSQL_BASIC_CONTEXT,
        PROMPT_MYSQL_BASIC_INPUT_AND_ASK,
        PROMPT_MYSQL_BASIC,
    ]
}
