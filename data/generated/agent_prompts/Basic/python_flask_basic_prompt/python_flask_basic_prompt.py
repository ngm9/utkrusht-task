PROMPT_PYTHON_FLASK_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_FLASK_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python Flask assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST PICK EXACTLY ONE real-world scenario provided above to create the task
- The task's business domain, current implementation problem, and candidate ask MUST come from that chosen scenario
- The task complexity must be appropriate for BASIC proficiency and realistically completable within {minutes_range} minutes
- The task must reflect authentic Flask work for a 1-2 year backend engineer
- Keep the task well-scoped: combine only 2-3 foundational Flask concepts, not broad architecture work
- Prefer implementation or bug-fix work involving routes, request handling, templates, JSON responses, simple database CRUD, error handling, or basic tests
- Do not drift into the employer's domain unless that same domain appears in the chosen scenario

Before proceeding to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the chosen business domain, the current Flask implementation problem, and what the candidate must fix or implement.
2. What will the task look like? Describe the expected deliverables, starter code shape, and why the task fits BASIC Python - Flask proficiency.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_FLASK_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect highly experienced in Python Flask, you are given competency requirements, role context, and real-world scenarios.
Your job is to generate a complete assessment task definition for BASIC Python - Flask proficiency, including candidate-facing question text, starter code files, and evaluator-facing answer guidance.

## SCENARIO LOCK (mandatory)
- You MUST pick EXACTLY ONE scenario from `real_world_task_scenarios`.
- The generated task's BUSINESS DOMAIN must match the chosen scenario's domain exactly. DO NOT invent a new domain.
- The generated task's CURRENT IMPLEMENTATION problem and YOUR TASK bullet list must come from the chosen scenario, adapted to Python Flask at BASIC level.
- You may rename variables, entities, and file names, but the SHAPE of the problem and the DOMAIN must remain from the chosen scenario.
- The candidate's EMPLOYER is described in `organization_background`. That employer is administering the assessment; it is NOT the business domain of the task.
- If you find yourself writing about a domain that does NOT appear in `real_world_task_scenarios`, STOP and restart with one listed scenario.
- When `real_world_task_scenarios` is empty or `(none provided)`, explicitly state which generic domain you picked and why; do not silently default to the employer's domain.

## HARD SCOPE BOUNDARY
Generate a task only within BASIC Python - Flask scope. The task may assess only concepts that are explicitly in scope or naturally derived from them, including:
- creating and running a simple Flask app
- routes, decorators, HTTP methods, variable URL rules
- `url_for`, `redirect`, response types, JSON responses, status codes
- request data via `request.args`, `request.form`, `request.json`
- forms and simple file uploads
- Jinja2 templates, inheritance, includes, escaping, static files
- small app structure with modules, Blueprints, and basic application factory patterns
- basic extension setup such as SQLAlchemy, Migrate, WTF, Login, CORS
- basic CRUD and simple database configuration
- simple authentication/session basics only if minor and not the main challenge
- error handling with `abort` and custom handlers
- logging, debug mode awareness
- basic tests with Flask test client and `pytest` or `unittest`
- simple docs and dependency management

Do NOT require out-of-scope or too-advanced work such as:
- system design or multi-service architecture
- advanced concurrency or async patterns
- security hardening as the primary task
- advanced caching or performance engineering
- complex deployment engineering
- large-scale schema design or advanced database optimization

## PROFICIENCY TARGET
This is a BASIC task:
- target 1-2 years experience
- expected completion time: {minutes_range}
- combine only 2-3 concepts in one well-scoped task
- the ask should be specific, concrete, and easy to understand
- do not make testing, authentication, database migrations, and templating all mandatory at once; choose only what is needed for the chosen scenario

## AI AND EXTERNAL RESOURCE POLICY
- Candidates may use external resources, including documentation, search engines, and AI tools.
- Therefore, the task should still require practical reasoning, code reading, and implementation quality rather than rote recall.
- Keep the task realistic and engineering-focused, not trivia-based.

## TASK SHAPE
Create a Flask task where the candidate either:
- fixes a logical bug in an existing small Flask app, or
- implements a missing, well-scoped feature in an existing small Flask app

The task must feel like a real maintenance or feature request in a small backend/web application.

## STRUCTURE REQUIREMENTS DERIVED FROM TEMPLATE CAPABILITIES
The matched environment has Python runtime with Flask and common Python web libraries available.
Do NOT ask the downstream model to add package-install commands for Flask or common libraries inside scripts.

Because backend templates support datastores, apply these rules:
- If the chosen scenario naturally needs persistence, include exactly one simple datastore service in `docker-compose.yml` such as postgres.
- If persistence is not necessary for the chosen scenario, you may omit `docker-compose.yml` and keep the task file-only.
- If a datastore is included:
  - provide `docker-compose.yml`
  - provide `run.sh` that uses `docker compose up -d`
  - provide `kill.sh` that uses `docker compose down`
  - keep infrastructure minimal and reliable
- Do not include a Dockerfile unless it is truly necessary. Prefer simple local Flask execution plus compose only for datastore support.

## RECOMMENDED TASK PATTERNS
Use one of these BASIC-friendly patterns depending on the chosen scenario:
- Template safety and routing fix:
  - replace hardcoded URLs with `url_for`
  - fix unsafe template rendering by relying on Jinja escaping
- CRUD bug fix with form handling:
  - load the correct record from a route parameter
  - validate form input
  - handle commit failure with rollback and a simple error response
- JSON API consistency fix:
  - return JSON 404 instead of HTML 404
  - add 1-2 basic pytest tests using Flask test client

These are examples of shape only. Do not copy them verbatim unless they match the chosen scenario.

## STARTER CODE REQUIREMENTS
- Provide enough starter code that the candidate can run and understand the app quickly.
- The code must be valid and executable.
- The core task logic must be incomplete or incorrect in a realistic way.
- Do NOT give away the solution in comments, docstrings, or helper functions.
- Do NOT include `TODO`, `FIXME`, or comments that reveal intended logic.
- The app should be small: usually 4-9 files total depending on whether tests and templates are included.
- Prefer a simple structure such as:
  - `app/__init__.py`
  - `app/routes.py` or `app/views.py`
  - `app/models.py` when needed
  - `templates/...` when needed
  - `tests/...` when needed
  - `requirements.txt`
  - `README.md`
  - `.gitignore`
  - optional `docker-compose.yml`, `run.sh`, `kill.sh`

## CODE QUALITY REQUIREMENTS
- Follow Python 3.10+ and Flask best practices suitable for small apps.
- Use readable names and PEP 8 style.
- Keep logic simple and maintainable.
- If using SQLAlchemy, keep models and queries basic.
- If using tests, use only basic Flask test client patterns.
- If using templates, ensure the task genuinely exercises Jinja or `url_for`, not generic HTML editing.

## README REQUIREMENTS
`README.md` must contain these sections in this order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

Rules:
- Fully populate every section with meaningful, scenario-specific content.
- Do not include setup instructions or shell commands.
- Do not include direct solutions or step-by-step implementation guidance.
- Keep the README candidate-facing and business-context aware.

### Task Overview
- 2-3 meaningful sentences describing the business scenario, current implementation issue, and why it matters.

### Helpful Tips
- Bullet points only.
- Give general guidance about the app behavior, request/response expectations, templates, tests, or data flow as relevant.
- Do not reveal the exact fix.

### Objectives
- Bullet points only.
- Clear, measurable completion goals.

### How to Verify
- Bullet points only.
- Describe observable behaviors after the candidate completes the task.
- Include endpoint or UI behavior checks and test expectations if tests are part of the task.

## INFRASTRUCTURE FILE RULES
If you include a datastore:
- `docker-compose.yml` must be minimal and valid.
- Do NOT include a `version` field.
- Use hardcoded values instead of `.env` references.
- `run.sh` should:
  - start services with `docker compose up -d`
  - wait briefly or check readiness in a simple way
  - print clear status messages
- `kill.sh` should:
  - stop services with `docker compose down`
  - be safe to run multiple times
  - print clear status messages

If no datastore is needed:
- do not generate compose or shell scripts just for the sake of it.

## REQUIRED OUTPUT JSON STRUCTURE
You MUST output valid JSON only, using exactly these top-level keys and no substitutes:

{{
  "name": "short-kebab-case-task-name",
  "question": "Full candidate-facing task description with business context, current implementation, and specific ask.",
  "code_files": {{
    "README.md": "full file contents",
    ".gitignore": "full file contents",
    "requirements.txt": "full file contents",
    "app/__init__.py": "full file contents",
    "app/routes.py": "full file contents"
  }},
  "answer": {{
    "summary": "High-level evaluator-facing solution summary",
    "key_points": [
      "point 1",
      "point 2"
    ]
  }},
  "definitions": {{
    "term_1": "definition",
    "term_2": "definition"
  }},
  "hints": "A single-line gentle nudge that does not give away the answer.",
  "outcomes": [
    "Expected outcome 1",
    "Expected outcome 2"
  ],
  "pre_requisites": [
    "Requirement 1",
    "Requirement 2"
  ],
  "short_overview": [
    "Brief point 1",
    "Brief point 2",
    "Brief point 3"
  ]
}}

## CANONICAL KEY RULES
- Use exactly: `name`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, `short_overview`
- Do NOT use synonyms like `title`, `task_title`, `files`, `repository_structure`, `context`, or `acceptance_criteria`

## FIELD-SPECIFIC RULES
- `name`: short, descriptive, kebab-case
- `question`: complete candidate-facing task description; do not make it vague
- `code_files`: map file paths to full file contents
- `answer`: evaluator-facing canonical solution summary object
- `definitions`: 2-6 relevant Flask/Python terms
- `hints`: exactly one line
- `outcomes`, `pre_requisites`, `short_overview`: arrays of short bullet-style strings in simple language

## FILE CONTENT RULES
- `requirements.txt` must include only the dependencies actually needed by the generated task.
- `.gitignore` should sensibly cover Python artifacts, virtual environments, env files, caches, logs, and local database artifacts if relevant.
- If tests are included, they must be basic and aligned with the task.
- If templates are included, ensure all literal braces inside file contents are escaped correctly in the JSON string you output.
- Do not include solution comments in any code file.
- The starter project must run, but the target behavior should still be missing or incorrect until the candidate fixes it.

## CALIBRATION USING ROLE SIGNAL
Calibrate the task for a developer who can:
- write clean functions and simple classes
- use modules and imports sensibly
- handle errors with `try/except`
- use standard library modules
- write or interpret simple tests
- work under guidance in an existing codebase

Do not require:
- advanced framework internals
- complex architecture decisions
- advanced ORM patterns
- asynchronous programming
- deep security expertise

## FINAL REMINDERS
1. Output valid JSON only.
2. Pick EXACTLY ONE scenario.
3. Keep the domain locked to that scenario.
4. Keep the task within BASIC Flask scope.
5. Keep the task completable within {minutes_range}.
6. Do not invent extra top-level JSON keys.
7. Do not include markdown fences or explanatory prose outside the JSON.
8. Ensure all generated file contents are internally consistent with the scenario and with each other.
9. If you include tests, they must verify the exact behavior described in the question.
10. If you include a database, keep CRUD and error handling simple.
"""

PROMPT_REGISTRY = {
    "Python - Flask (BASIC)": [
        PROMPT_PYTHON_FLASK_BASIC_CONTEXT,
        PROMPT_PYTHON_FLASK_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_FLASK_BASIC_INSTRUCTIONS,
    ]
}