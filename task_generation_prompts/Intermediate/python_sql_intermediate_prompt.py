PROMPT_PYTHON_SQL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_SQL_INTERMEDIATE_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for INTERMEDIATE level (3-5 years experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python + SQL implementation required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_SQL_INTERMEDIATE_INSTRUCTIONS = """
# Python + SQL Intermediate Task Requirements

## GOAL
As a technical architect experienced in Python and SQL/PostgreSQL, you are given real-world scenarios and proficiency levels for Python and SQL development. Your job is to generate an entire task definition, including Python code files, database setup (Docker-based PostgreSQL), README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to optimize, refactor, and build robust Python applications that interact with SQL databases at INTERMEDIATE proficiency (3-5 years experience).

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive:
- A FULLY FUNCTIONAL Docker-based PostgreSQL database, pre-populated with schema and substantial sample data (100+ rows in main tables)
- Python starter code with a working but poorly performing or architecturally flawed application that connects to and queries the database
- The candidate's job is to optimize SQL queries, refactor Python code for better architecture, add proper error handling and caching, and write tests

The task may use lightweight web frameworks (Flask or FastAPI) for endpoint context, but the core challenge is about Python + SQL optimization and architecture — not web framework features.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to optimize, refactor, or fix architectural issues in a Python application that interacts with a PostgreSQL database.
- The task combines intermediate Python skills (OOP, decorators, context managers, connection pooling, caching, testing) with intermediate SQL skills (query optimization, indexing, EXPLAIN analysis, conditional aggregates, window functions, CTEs).
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point with the current (slow or poorly architected) implementation.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The question should be a real-world performance or architecture scenario.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts:

**Current Implementation (what we give to the candidate):**
- Describe precisely the poorly performing or architecturally flawed state the starter code implements.
- Examples: "The function loads all 500K rows into Python and groups in a loop instead of using SQL aggregation"; "Each request opens a new database connection instead of using a pool"; "Three separate COUNT queries run when one conditional aggregate would suffice."
- The **starter code MUST perfectly implement this current implementation**.

**Required Changes (what the candidate must do):**
- List the specific optimizations or refactors required: e.g. "Replace Python-side grouping with a single SQL query using GROUP BY and SUM"; "Add a composite index on (account_id, posted_at)"; "Implement a TTL cache"; "Add error handling that returns 503 on database failures."
- 3-5 discrete changes appropriate for 30-40 minutes of work.

**Final Implementation Approach:**
- A high-level description of the correct approach.
- The complexity must align with INTERMEDIATE proficiency (3-5 years Python + SQL experience).
- For INTERMEDIATE level, the questions must focus on:
  - Python: OOP refactoring, decorators, context managers, connection pooling (SQLAlchemy engine), simple caching (dict or functools), proper exception handling with custom error responses, pytest unit tests
  - SQL: query optimization (replacing N+1 or Python-side processing with efficient SQL), composite indexes, EXPLAIN ANALYZE, conditional aggregates (COUNT FILTER, CASE WHEN), CTEs, window functions where appropriate
  - Integration: SQLAlchemy engine/connection pooling, parameterized queries, repository pattern or service layer, error wrapping
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure all code adheres to Python 3.10+ and PostgreSQL best practices.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years experience).
- TASK name should be short and under 50 characters. Use kebab-case.

### Starter Code Requirements

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working Python application** that runs successfully after the database is deployed via run.sh.
- **ZERO syntax errors, ZERO import errors** — the application must run cleanly.
- **The database connection must work** — the application connects to PostgreSQL and executes queries (even if slowly or inefficiently).
- **The candidate should NOT need to fix anything to make the application run** — it works, just poorly.

**WHAT MUST BE INCLUDED:**
- Python starter code with multiple files (main module, service/repository layer, optional utils)
- requirements.txt with psycopg2-binary, SQLAlchemy, Flask or FastAPI, pytest (and any other needed packages)
- Docker-based PostgreSQL setup: docker-compose.yml, run.sh, kill.sh, init_database.sql
- init_database.sql: schema with 3-5 tables, proper relationships, and substantial realistic sample data (100+ rows in main tables, enough to demonstrate performance issues)
- README.md with Task Overview, Objectives, Database Access, How to Verify, and Helpful Tips
- .gitignore suitable for the task
- A tests/ directory with at least one placeholder test file

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code
- **Starter code must perfectly implement only the "Current Implementation"** — the slow/flawed state
- **NO comments** that reveal the solution or give hints
- DO NOT include the optimized queries, indexes, or caching logic

### Infrastructure Requirements

**docker-compose.yml:**
- PostgreSQL service with hardcoded configuration
- **MUST NOT include any version specification** in the docker-compose.yml file
- **MUST NOT include any environment variables or .env file references**
- Use hardcoded configuration values
- Volume mount for data persistence

**run.sh:**
- Starts Docker containers using docker-compose up
- Waits for PostgreSQL service to be fully ready
- Executes init_database.sql to create schema and insert sample data
- Installs Python dependencies (pip install -r requirements.txt)
- **LOCATION**: All files are located in /root/task directory

**kill.sh:**
- Stops and removes all containers
- Removes all Docker volumes
- Runs `docker system prune -a --volumes -f`
- Deletes `/root/task/`
- Idempotent and logs progress

**init_database.sql:**
- Schema with 3-5 tables, proper relationships (foreign keys, constraints)
- Substantial realistic sample data (100+ rows in main tables)
- All in a single file that runs without errors
- Data volume must be sufficient to demonstrate performance differences

### AI and External Resource Policy
- Candidates are permitted to use any external resources including AI tools.
- Tasks require genuine engineering and optimization skills beyond simple copy-pasting.

### Code Generation Instructions
Based on real-world scenarios, create a Python + SQL task that:
- Draws inspiration from ONE input scenario for business context
- Matches INTERMEDIATE proficiency (3-5 years experience)
- Can be completed within {minutes_range} minutes
- Tests practical optimization and architecture skills: query optimization, indexing, caching, connection management, error handling, testing
- Select a different real-world scenario each time for variety

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact slow/flawed state. (2) Required Changes — specific optimizations or refactors. Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Python and Docker exclusions",
    "requirements.txt": "Python dependencies (psycopg2-binary, SQLAlchemy, Flask/FastAPI, pytest, etc.)",
    "docker-compose.yml": "PostgreSQL service (NO version specs, NO .env, hardcoded config)",
    "run.sh": "Script to start containers, wait for DB, load SQL, install Python deps",
    "kill.sh": "Script to tear down containers, volumes, and clean /root/task",
    "init_database.sql": "Schema creation and substantial sample data (3-5 tables, 100+ rows)",
    "app.py or main.py": "Main application with slow/flawed database interaction",
    "service.py or db.py": "Service/data layer with inefficient implementation",
    "tests/test_placeholder.py": "Minimal test file as starting point"
  }},
  "outcomes": "Bullet-point list. Expected results after completion.",
  "short_overview": "Bullet-point list: (1) business context, (2) what to optimize/refactor, (3) expected outcome.",
  "pre_requisites": "Bullet-point list: Python 3.10+, pip, Docker, Docker Compose, PostgreSQL client, intermediate Python and SQL knowledge, pytest, Git.",
  "answer": "High-level solution approach (which optimizations, which indexes, architecture changes; no full code).",
  "hints": "Single line suggesting focus area. Must NOT give away the answer.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (Python + SQL Intermediate)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Objectives
3. Database Access
4. How to Verify
5. Helpful Tips

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a Python application interacts with PostgreSQL but has performance or architectural issues. Explain that the application works but is slow or poorly structured. The candidate must optimize queries, refactor code, and improve error handling.

### Objectives

- Clear, measurable goals appropriate for intermediate Python + SQL level
- What the candidate should optimize or refactor
- Include performance targets where applicable (e.g. response time under 500ms)
- These objectives will be used to verify task completion and award points

### Database Access

- Connection details with <DROPLET_IP> placeholder
- Mention database client tools

### How to Verify

- Performance benchmarks (before/after timing)
- Run tests to verify correctness
- Check EXPLAIN output for index usage
- Verify error handling with edge cases

### Helpful Tips

- Consider what SQL operations could replace Python-side data processing
- Think about how database connections are managed across requests
- Review query execution plans to identify bottlenecks
- Explore caching strategies for frequently accessed data
- Consider what happens when the database is temporarily unavailable

### NOT TO INCLUDE:
- Setup instructions
- Step-by-step implementation guides
- Exact code solutions or SQL query examples
- Direct solutions or hints

## CRITICAL REMINDERS

1. **Environment must be fully working** — Application runs but is slow/flawed
2. **Starter code must be runnable** but must NOT contain optimizations
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on INTERMEDIATE concepts** (query optimization, indexing, caching, connection pooling, error handling, testing)
7. **Use Python 3.10+ and PostgreSQL** best practices
8. **init_database.sql must have substantial data** (100+ rows) to demonstrate performance issues
9. **README.md MUST be fully populated**
10. **Task name** must be short, descriptive, under 50 characters, kebab-case
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), SQL (INTERMEDIATE)": [
        PROMPT_PYTHON_SQL_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_SQL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_SQL_INTERMEDIATE_INSTRUCTIONS,
    ],
}
