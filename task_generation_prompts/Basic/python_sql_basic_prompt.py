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
- The task complexity must be appropriate for BASIC level (1-2 years experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python + SQL implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS = """
# Python + SQL Basic Task Requirements

## GOAL
As a technical architect experienced in Python and SQL/PostgreSQL, you are given real-world scenarios and proficiency levels for Python and SQL development. Your job is to generate an entire task definition, including Python code files, database setup, starter data, README.md, and expected outcomes, that can be effectively used to assess a candidate's ability to complete a small but realistic Python + SQL task at BASIC proficiency (1-2 years experience).

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive:
- A working Docker-based PostgreSQL database
- A small Python script project that connects to the database
- Starter code that runs, but has a clear bug or missing feature in a well-scoped workflow
- A realistic business task such as importing records, cleaning simple input data, updating existing rows, generating a small report, or fixing a query used by the script

The candidate's responsibility is to make a focused set of changes using basic Python and SQL skills. The task must be practical, specific, and limited enough to complete within {minutes_range} minutes.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement or fix a small Python script that interacts with PostgreSQL.
- The task must combine 2-3 BASIC-level concepts across Python and SQL, such as:
  - Python file I/O, loops, functions, dictionaries/lists, try/except, simple validation
  - SQL table creation or alteration, INSERT/UPDATE/SELECT, simple JOINs, WHERE, ORDER BY, GROUP BY, basic subqueries, constraints, transactions
- The question scenario must be clear, realistic, and grounded in a business workflow.
- The task must be specific and not open-ended.
- The starter code must give the candidate a clear starting point without giving away the solution.
- The question should not be a trick question based on syntax errors.
- The complexity must align with BASIC proficiency:
  - Appropriate: CSV/text import, deduplication using SELECT then UPDATE/INSERT, simple joined reporting, fixing incorrect filtering or ordering, adding a basic constraint or migration, handling invalid rows, small ETL-style transformation from one source file
  - Not appropriate: async/await, design patterns, system design, advanced concurrency, security hardening, advanced caching, complex partitioning, microservices, advanced ORM abstractions, broad architecture refactors, advanced performance tuning
- The question must NOT include hints. Hints belong only in the "hints" field.
- Ensure all code uses Python 3.10+ and PostgreSQL best practices suitable for BASIC level.
- TASK name should be short, descriptive, under 50 characters, and use kebab-case.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts:

**Current Implementation (what we give to the candidate):**
- Describe precisely the current buggy or incomplete behavior that the starter code implements.
- The starter code MUST exactly match this current implementation.
- Examples of suitable current states:
  - A script reads a CSV and inserts rows, but crashes on blank values
  - A script always inserts rows and creates duplicates instead of updating existing records
  - A report query only reads one table and misses related information from a simple JOIN
  - A script writes invalid values because it does not validate input before saving
  - A transaction is missing, so partial writes can happen when one row fails

**Required Changes (what the candidate must do):**
- List 2-4 specific changes appropriate for BASIC level.
- Examples:
  - Skip invalid rows using try/except and continue processing
  - Use a SELECT to check whether a row exists, then UPDATE or INSERT accordingly
  - Add a simple INNER JOIN or LEFT JOIN to include related data
  - Add a CHECK or UNIQUE constraint in SQL and adjust the script to handle violations
  - Wrap a small batch operation in BEGIN/COMMIT/ROLLBACK
  - Print a short import or processing summary

**Final Implementation Approach:**
- Provide a high-level description of the correct approach without giving the exact solution.
- The final approach should reflect BASIC-level Python and SQL knowledge:
  - Python: functions, loops, dictionaries/lists, file reading, standard library imports, try/except, simple command-line execution
  - SQL: DDL with basic constraints, CRUD, simple JOINs, WHERE/GROUP BY/HAVING/ORDER BY, simple subqueries, transactions, basic indexing awareness, selecting only needed columns
- Keep the task focused on correctness, reliability, and straightforward data handling.

### Starter Code Requirements

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- The starter code MUST be a complete, working Python script project that runs successfully after the database is deployed via run.sh.
- ZERO syntax errors and ZERO import errors.
- The database connection must work.
- The candidate should NOT need to fix the environment to begin the task.
- The starter code must implement the current buggy or incomplete behavior exactly, but still run.

**WHAT MUST BE INCLUDED:**
- A small Python project with 2-4 files total, such as:
  - main.py
  - db.py or helpers.py
  - optional seed/input file such as CSV or TXT
- requirements.txt with only the necessary dependencies
- Docker-based PostgreSQL setup:
  - docker-compose.yml
  - run.sh
  - kill.sh
  - init_database.sql
- README.md with the required sections below
- .gitignore suitable for Python and Docker
- If useful for the task, include one input data file such as:
  - data/input.csv
  - data/orders.txt
  - data/submissions.csv

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code
- DO NOT include advanced frameworks such as Flask, FastAPI, Django, SQLAlchemy, Celery, Kafka, etc.
- DO NOT require tests for BASIC level
- DO NOT include comments that reveal the solution
- DO NOT make the candidate fix broken infrastructure

### Infrastructure Requirements

Because the task category is SCRIPT_AND_DB, the generated task MUST include:
- Docker + PostgreSQL
- A Python script project
- No web framework

**docker-compose.yml:**
- PostgreSQL service only
- MUST NOT include any version specification
- MUST NOT include any environment variables or .env file references
- Use hardcoded configuration values
- Include a volume mount for data persistence
- Expose PostgreSQL on a standard port

**run.sh:**
- Starts Docker containers using docker-compose up -d
- Waits for PostgreSQL to be fully ready
- Executes init_database.sql to create schema and insert starter data if not using automatic mount-based initialization
- Installs Python dependencies with pip install -r requirements.txt
- Must assume files are located in /root/task

**kill.sh:**
- Stops and removes containers
- Removes volumes
- Runs docker system prune -a --volumes -f
- Deletes /root/task/
- Must be idempotent and print progress logs

**init_database.sql:**
- Must be a single SQL file that runs without errors
- Include 2-4 tables with realistic but modest schema
- Use proper primary keys and foreign keys where appropriate
- Include basic constraints when relevant to the scenario
- Include realistic sample data sufficient for the task
- May include a small migration or starter issue only if it aligns with BASIC SQL scope
- Must not contain the final solution if the candidate is expected to alter schema or queries

### AI and External Resource Policy
- Candidates are permitted to use any external resources including AI tools.
- Tasks should still require genuine reasoning, debugging, and implementation beyond simple copy-paste.

## Code Generation Instructions
Based on the real-world scenarios, create a Python + SQL task that:
- Draws inspiration from ONE input scenario for business context
- Matches BASIC proficiency (1-2 years experience)
- Can be completed within {minutes_range} minutes
- Tests practical Python + SQL skills for small scripts and database interactions
- Uses a different real-world scenario each time for variety
- Emphasizes correctness, simple data integrity, and clear handling of edge cases

## REQUIRED OUTPUT JSON STRUCTURE
{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state. (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous.",
  "code_files": {
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Python and Docker exclusions",
    "requirements.txt": "Minimal Python dependencies",
    "docker-compose.yml": "PostgreSQL service only with hardcoded config",
    "run.sh": "Script to start containers, wait for DB, load SQL if needed, install Python deps",
    "kill.sh": "Script to tear down containers, volumes, and clean /root/task",
    "init_database.sql": "Schema creation and sample data",
    "main.py": "Main Python script entry point",
    "db.py or helpers.py": "Database helper or utility module",
    "data/input.csv": "Optional input file if the scenario uses file import"
  },
  "outcomes": "Bullet-point list. Expected results after completion.",
  "short_overview": "Bullet-point list: (1) business context, (2) what the candidate must fix or implement, (3) expected outcome.",
  "pre_requisites": "Bullet-point list: Python 3.10+, pip, Docker, Docker Compose, PostgreSQL client optional, basic Python and SQL knowledge, Git.",
  "answer": "High-level solution approach only. No full code.",
  "hints": "Single line suggesting focus area. Must NOT give away the answer.",
  "definitions": {
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }
}

## README.md STRUCTURE (Python + SQL Basic)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated.

1. Task Overview
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview
- Must contain 2-3 substantial sentences.
- Describe the specific business workflow and the current issue in the Python + SQL process.
- Make clear that the candidate is working on a small script and database task, not a large application.
- Explain why the fix matters to the business process.

### Objectives
- Clear, measurable goals appropriate for BASIC Python + SQL level
- Focus on correctness, simple validation, reliable database writes, or correct query results
- Objectives should be directly verifiable

### Database Access
- Provide connection details with <DROPLET_IP> placeholder
- Mention that any PostgreSQL client tool may be used

### How to Verify
- Include concrete checks such as:
  - Run the script and confirm it completes
  - Confirm invalid rows are skipped or handled correctly
  - Confirm duplicates are not created
  - Confirm expected rows exist in the database
  - Confirm joined or filtered query output is correct
- Keep verification practical and measurable

### Helpful Tips
- Use general guidance only
- Examples of acceptable tip style:
  - Consider where input validation should happen before writing to the database
  - Review whether the script should insert a new row or update an existing one
  - Think about which related table should be joined to return complete results
  - Explore how try/except and transactions can improve reliability
- Do NOT provide direct solutions

### NOT TO INCLUDE:
- Setup instructions
- Step-by-step implementation guides
- Exact code solutions
- Advanced architecture advice outside BASIC scope

## CRITICAL REMINDERS

1. The environment must be fully working
2. The starter code must be runnable but incomplete or logically flawed in a specific way
3. The starter code must perfectly match the described Current Implementation
4. NO comments that reveal the solution
5. The task must be completable within {minutes_range} minutes
6. Focus on BASIC concepts only
7. Use Python 3.10+ and PostgreSQL
8. Keep file count modest and the scenario well-scoped
9. README.md must be fully populated
10. The task must fit SCRIPT_AND_DB exactly: Docker + DB + Python script, no web framework
"""

PROMPT_REGISTRY = {
    "Python (BASIC), SQL (BASIC)": [
        PROMPT_PYTHON_SQL_BASIC_CONTEXT,
        PROMPT_PYTHON_SQL_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS,
    ],
}