PROMPT_PYTHON_FLASK_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and role requirements for this assessment.
"""

PROMPT_PYTHON_FLASK_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python Flask assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST PICK EXACTLY ONE scenario from the real-world scenarios provided above.
- The task's business domain, current implementation problem, and candidate ask MUST come from that chosen scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- The task must reflect authentic backend work that would be encountered in the role described in the role context.
- The employer described in the company context is administering the assessment; it is NOT the business domain unless the chosen scenario explicitly matches it.

Before proceeding to the detailed task generation instructions, confirm your understanding by answering:

1. Which single scenario will you use, and what is the business domain?
2. What existing Flask application problem will the candidate solve?
3. What will the task deliverables look like, and why is that appropriate for this INTERMEDIATE Flask assessment?

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_FLASK_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python Flask, generate a complete assessment task definition for an INTERMEDIATE Flask engineer. The task must assess practical backend engineering in an existing Flask codebase and stay strictly within the provided competency scope.

## SCENARIO LOCK (mandatory)
- You MUST pick EXACTLY ONE scenario from `real_world_task_scenarios`.
- The generated task's BUSINESS DOMAIN must match the chosen scenario's domain. DO NOT invent a new domain.
- The generated task's CURRENT IMPLEMENTATION problem and YOUR TASK bullet list must come from the chosen scenario, adapted to Python Flask.
- You may rename variables, models, and files, but the SHAPE of the problem and the DOMAIN must remain the chosen scenario's.
- The candidate's EMPLOYER is described in `organization_background`. That organization is administering the assessment; it is NOT the task domain unless the chosen scenario says so.
- If you find yourself writing about a domain that does NOT appear in `real_world_task_scenarios`, STOP and restart with one listed scenario.
- When `real_world_task_scenarios` is empty or "(none provided)", explicitly state which generic domain you picked and why. Do not silently default to the employer's domain.

## SCOPE BOUNDARY (mandatory)
Only use skills naturally supported by the competency scope for Python - Flask (INTERMEDIATE). The task may assess:
- Modular Flask structure using blueprints and app factory
- Routing, request/response lifecycle, contexts, and HTTP fundamentals
- Jinja2 templates and static/template organization per blueprint
- Input validation and serialization using WTForms, Marshmallow, or Pydantic
- SQLAlchemy integration and Flask-Migrate migrations
- Session/authentication/basic authorization patterns when relevant
- RESTful API design, versioned endpoints, CORS, structured error payloads, and external HTTP integration when relevant
- Centralized error handling, logging, health checks, and basic observability
- Environment-based configuration and Docker basics
- Security basics such as CSRF/XSS protections, secure cookies, headers, password hashing, and secret handling when relevant
- Unit/integration tests using pytest and Flask test client, with mocks where useful

Do NOT make the task primarily about out-of-scope topics such as distributed systems, microservices, advanced concurrency, or broad system design.

## PROFICIENCY TARGET
This is an INTERMEDIATE task:
- Target completion time: {minutes_range}
- Expect 4-5 connected concepts, not a single syntax fix
- The task should require implementation and reasoning across structure, correctness, error handling, and tests
- The task should still be well-scoped and specific, not open-ended architecture work

## TASK SHAPE
Generate a task where the candidate extends or fixes an existing Flask application. Good task shapes for this level include:
- Refactoring a monolithic Flask app into blueprints under an app factory while fixing broken routing and error handling
- Adding schema-based validation, serialization, pagination, and consistent JSON errors to existing API endpoints
- Improving an existing SQLAlchemy-backed endpoint with eager loading, a migration, simple caching, and request logging
- Combining one primary feature/fix with supporting tests and minimal infrastructure

The task should feel like everyday backend ownership work in an existing codebase.

## TECHNICAL REQUIREMENTS
- Primary runtime is Python.
- Use Flask as the main framework.
- You may use common preinstalled Python libraries/frameworks advertised by the template where helpful.
- Prefer a relational datastore for this task because Flask + SQLAlchemy + migrations are in scope.
- Since datastore support is available, include a `docker-compose.yml` for the datastore actually used by the task, and include:
  - `run.sh` that starts services with `docker compose up -d`
  - `kill.sh` that stops services with `docker compose down`
- Do NOT include `apt-get install`, `pip install`, or similar setup commands inside `run.sh`.
- Keep infrastructure minimal and aligned to the task. Do not overbuild the environment.

## STARTER CODE REQUIREMENTS
- Provide a runnable but incomplete or logically flawed Flask project.
- The starter code must NOT contain the full solution.
- Do NOT include placeholder comments like "TODO", "implement here", or comments that reveal the intended fix.
- The code should be executable enough for the candidate to inspect, run tests, and complete the task.
- If the task is bug-fix oriented, the bugs must be logical or structural, not syntax errors.
- If the task is feature-oriented, provide enough scaffolding that the candidate can complete it within the time limit.

## RECOMMENDED PROJECT CONTENT
For a backend Flask task at this level, the generated repository should usually include:
- `README.md`
- `.gitignore`
- `requirements.txt`
- `docker-compose.yml`
- `run.sh`
- `kill.sh`
- Flask application package using app factory structure such as `app/__init__.py`
- One or more blueprints such as `app/api/routes.py` and optionally `app/dashboard/routes.py`
- Models and database setup files such as `app/models.py` or package equivalents
- Schemas/forms/serializers if used
- Config file
- Migration bootstrap files or a simple migration file when the scenario requires schema/index changes
- Tests using pytest and Flask test client
- Optional template files if the chosen scenario includes a server-rendered dashboard
- Optional cache/logging helpers if relevant to the chosen scenario

## README REQUIREMENTS
The `README.md` must contain these sections:
1. Task Overview
2. Guidance
3. Objectives
4. How to Verify

Rules:
- Task Overview must describe the exact chosen business scenario and current implementation problem in 2-3 meaningful sentences.
- Guidance must briefly explain the important files in bullet points.
- Objectives must be clear, measurable, and candidate-facing.
- How to Verify must describe observable checks the candidate can perform after implementation.
- Do NOT include setup instructions or direct solution hints in the README.

## TESTING REQUIREMENTS
- Include meaningful tests for the intended Flask behavior.
- Tests should align with the task scope and verify the expected outcomes.
- Use pytest and Flask's test client.
- Mock dependencies only when appropriate.
- Do not make the task primarily about writing a huge test suite; tests should support the core backend task.

## OUTPUT JSON SCHEMA
Your output MUST be a valid JSON object using EXACTLY these top-level keys:

{{
  "name": "Short task title",
  "question": "Full candidate-facing task description",
  "code_files": {{
    "README.md": "full file contents",
    ".gitignore": "full file contents",
    "requirements.txt": "full file contents",
    "docker-compose.yml": "full file contents",
    "run.sh": "full file contents",
    "kill.sh": "full file contents",
    "app/__init__.py": "full file contents"
  }},
  "answer": {{
    "summary": "High-level solution approach",
    "key_steps": ["step 1", "step 2"],
    "verification": ["check 1", "check 2"]
  }},
  "definitions": {{
    "term": "definition"
  }},
  "hints": "Single-line hint that nudges without giving away the answer",
  "outcomes": "2-3 lines describing expected results in simple English",
  "pre_requisites": "Bullet-point list of tools and knowledge required",
  "short_overview": "Bullet-point list summarizing the business problem, implementation goal, and expected outcome"
}}

Use those exact key names only:
- `name`
- `question`
- `code_files`
- `answer`
- `definitions`
- `hints`
- `outcomes`
- `pre_requisites`
- `short_overview`

Do NOT use synonyms such as `title`, `task_title`, `files`, `repository_structure`, `context`, or `acceptance_criteria`.

## QUALITY BAR
- Keep the task realistic for an intermediate backend engineer.
- Make the ask specific enough to be completed within {minutes_range}.
- Ensure the task exercises Flask-specific structure and backend reasoning, not generic Python only.
- Use modern Flask and Python practices.
- Keep the generated files concise but complete enough to run.
- Ensure the chosen scenario, starter code, README, tests, and expected answer all align with one another.
"""

PROMPT_REGISTRY = {
    "Python - Flask (INTERMEDIATE)": [
        PROMPT_PYTHON_FLASK_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_FLASK_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_FLASK_INTERMEDIATE_INSTRUCTIONS,
    ]
}