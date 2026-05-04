PROMPT_PYTHON_SQL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_SQL_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python + SQL assessment task.

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
2. What will the task look like? (Describe the type of Python + SQL implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS = """
# Python + SQL Basic Task Requirements

## GOAL
As a technical architect experienced in Python and SQL/PostgreSQL, you are given real-world scenarios and proficiency levels for Python and SQL development. Your job is to generate an entire task definition, including Python code files, database setup (Docker-based PostgreSQL), README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to write Python scripts that interact with a SQL database — reading, writing, validating, and transforming data end to end at BASIC proficiency (1-2 years experience).

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive:
- A FULLY FUNCTIONAL Docker-based PostgreSQL database, pre-populated with schema and sample data
- Python starter code with a working but buggy or incomplete script that connects to and queries the database
- The candidate's job is to fix bugs in the Python code and/or SQL queries, add missing validation, improve error handling, and potentially write simple tests

This is NOT a web framework task. There is NO FastAPI, Flask, Django, or any HTTP server. The task is about Python scripts that directly interact with a PostgreSQL database using a driver like psycopg2 or sqlite3-compatible patterns.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to fix bugs or implement missing features in a Python script that reads from or writes to a PostgreSQL database.
- The task combines Python skills (functions, error handling, file I/O, data structures) with SQL skills (SELECT, JOIN, WHERE, GROUP BY, INSERT, UPDATE, basic indexing).
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point and demonstrates the current (buggy or incomplete) implementation.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question or purely syntactic errors.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy or incomplete state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The Python function queries the database but uses string concatenation instead of parameterized queries"; "The script reads CSV and inserts into DB but crashes on NULL values"; "The SQL JOIN is wrong and returns duplicate rows."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must run without syntax errors, but it must exhibit exactly these bugs or missing pieces. Do not accidentally fix the issues or add the solution in the starter code.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Fix the SQL query to use LEFT JOIN and handle NULLs with COALESCE"; "Add input validation before inserting into the database"; "Use parameterized queries instead of string formatting."
- The candidate's job is only to complete these required changes on top of the current implementation.

**Final Implementation Approach:**
- A high-level description of the correct approach.
- The complexity must align with BASIC proficiency level (1-2 years Python + SQL experience).
- For BASIC level, the questions must focus on:
  - Python: functions, modules, error handling (try/except), file I/O (CSV/JSON), basic data structures, simple unit tests
  - SQL: SELECT with JOINs (2-3 tables), WHERE, GROUP BY, aggregates, INSERT/UPDATE, basic indexing, parameterized queries, NULL handling
  - Integration: using psycopg2 or similar driver, reading query results into Python data structures, writing Python data to the database
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure all code adheres to Python 3.8+ and PostgreSQL best practices.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "quiz-score-export-fix", "inventory-import-cleanup".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working Python script** that runs successfully after the database is deployed via run.sh.
- **ZERO syntax errors, ZERO import errors** — the script must run cleanly.
- **The database connection must work** — the script connects to PostgreSQL and executes queries (even if the queries are buggy or incomplete).
- **The candidate should NOT need to fix anything to make the script run** — The environment is already fully functional; the candidate's job is only to fix the specified bugs or implement the requested features.

**WHAT MUST BE INCLUDED:**
- Python starter code with a main script and optionally one helper module
- requirements.txt with psycopg2-binary (and any other needed packages)
- Docker-based PostgreSQL setup: docker-compose.yml, run.sh, kill.sh, init_database.sql
- init_database.sql: schema with 2-4 tables, basic relationships (foreign keys), and realistic sample data (20-50 rows) — all in a single file that runs without errors
- README.md with Task Overview, Objectives, Database Access, How to Verify, and Helpful Tips
- .gitignore suitable for the task

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code
- **Starter code must perfectly implement only the "Current Implementation"** — the buggy or incomplete state
- **NO comments** that reveal the solution or give hints (no TODO, no "fix this", no "implement here")
- DO NOT include any web framework (no FastAPI, Flask, Django)
- DO NOT include advanced patterns beyond BASIC level (no async, no ORMs, no connection pooling)

### Infrastructure Requirements

**docker-compose.yml:**
- PostgreSQL service with hardcoded configuration (database name, username, password)
- **MUST NOT include any version specification** in the docker-compose.yml file
- **MUST NOT include any environment variables or .env file references**
- Use hardcoded configuration values
- Volume mount for data persistence

**run.sh:**
- Starts Docker containers using docker-compose up
- Waits for PostgreSQL service to be fully ready and accepting connections
- Executes init_database.sql to create schema and insert sample data
- Installs Python dependencies (pip install -r requirements.txt)
- **LOCATION**: All files are located in /root/task directory
- **CRITICAL**: The database must be fully populated and ready before the candidate starts

**kill.sh:**
- Stops and removes all containers created by docker-compose
- Removes all associated Docker volumes
- Runs `docker system prune -a --volumes -f`
- Deletes the entire `/root/task/` folder
- Idempotent (safe to run multiple times)
- Prints progress logs at every step

**init_database.sql:**
- Schema with 2-4 tables, basic relationships (foreign keys, one-to-many)
- Realistic sample data (20-50 rows per main table)
- All in a single file that runs to completion without errors
- The schema and data must support the task scenario (the queries in the Python script must be answerable from this data)

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official Python/PostgreSQL documentation, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to analyze, diagnose, and fix/implement using Python + SQL, rather than testing rote memorization.

### Code Generation Instructions
Based on real-world scenarios, create a Python + SQL task that:
- Draws inspiration from ONE input scenario for business context and technical focus
- Matches BASIC proficiency (1-2 years Python + SQL experience)
- Can be completed within {minutes_range} minutes
- Tests practical Python + SQL skills: database queries, data processing, error handling, input validation
- Select a different real-world scenario each time for variety
- Focus on Python scripts that interact with PostgreSQL — not web APIs

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state the starter code implements (what we give). (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Python and Docker exclusions",
    "requirements.txt": "Python dependencies (psycopg2-binary and any others needed)",
    "docker-compose.yml": "PostgreSQL service (NO version specs, NO .env, hardcoded config)",
    "run.sh": "Script to start containers, wait for DB, load SQL, install Python deps",
    "kill.sh": "Script to tear down containers, volumes, and clean /root/task",
    "init_database.sql": "Schema creation and sample data (2-4 tables, 20-50 rows, realistic data)",
    "main.py": "Main Python script with buggy/incomplete database interaction",
    "additional_module.py": "Optional helper module if needed"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list: (1) business context and problem, (2) what the candidate must fix/implement in Python + SQL, (3) expected outcome.",
  "pre_requisites": "Bullet-point list of tools and knowledge: Python 3.8+, pip, Docker, Docker Compose, PostgreSQL client (psql/pgAdmin/DBeaver), basic Python and SQL knowledge, Git.",
  "answer": "High-level solution approach (which Python fixes, which SQL fixes; no full code).",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but nudge toward the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (Python + SQL Basic)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a Python script interacts with a PostgreSQL database but has bugs or missing features. Explain that the database is fully deployed and populated, and the Python script runs but produces incorrect results or crashes on certain inputs. The candidate must fix the Python code and/or SQL queries. The README.md file content MUST be fully populated with meaningful, specific content. ALL sections must have substantial content - no empty or placeholder text allowed.

### Objectives

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate appropriate for basic Python + SQL level
- What the candidate should fix or implement in both the Python code and SQL queries
- These objectives will be used to verify task completion and award points
- Scope should be achievable within the allocated time

**CRITICAL**: Focus on measurable, verifiable outcomes

### Database Access

- Provide the database connection details (host (use placeholder <DROPLET_IP>), port, database name, username, password)
- Mention that candidates can use any preferred database client tools (e.g. pgAdmin, DBeaver, psql, DataGrip) for analysis
- Note that the same credentials are used by the Python script

### How to Verify

- Specific checkpoints after the candidate's fix: run the Python script, check output, verify database state
- Observable behaviors to validate (script completes without errors, correct output, data integrity)
- Simple methods to verify (run script, check CSV output, query database directly)
- Include concrete steps or commands where helpful

**CRITICAL**: Focus on measurable, verifiable improvements

### Helpful Tips

Practical guidance without revealing implementations:

- Consider how the Python script connects to and queries the database
- Think about what happens when the script encounters unexpected data (NULLs, missing rows, invalid input)
- Review the SQL queries to ensure they return the expected results
- Explore error handling patterns for database operations in Python
- Consider how to verify your changes by running the script and checking the output
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (the environment is pre-deployed)
- Step-by-step implementation instructions
- Exact code solutions or SQL query examples
- Direct solutions or hints
- Specific Python or SQL syntax that would give away the solution

## CRITICAL REMINDERS

1. **Environment must be fully working** — Database deployed, Python script runs (but has bugs), candidate does NOT fix infrastructure
2. **Starter code must be runnable** but must NOT contain the solution
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on BASIC Python + SQL concepts** (functions, error handling, JOINs, parameterized queries, data validation)
7. **Use Python 3.8+ and PostgreSQL** best practices
8. **NO web frameworks** — this is a pure Python script + database task
9. **README.md MUST be fully populated** with meaningful, task-specific content
10. **init_database.sql must run without errors** and populate realistic data
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
"""

PROMPT_REGISTRY = {
    "Python (BASIC), SQL (BASIC)": [
        PROMPT_PYTHON_SQL_BASIC_CONTEXT,
        PROMPT_PYTHON_SQL_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS,
    ],
}
