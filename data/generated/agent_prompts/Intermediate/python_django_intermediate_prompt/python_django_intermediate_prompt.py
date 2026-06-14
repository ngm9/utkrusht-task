PROMPT_PYTHON_DJANGO_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""


PROMPT_PYTHON_DJANGO_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python Django assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST PICK EXACTLY ONE real-world scenario from the list above to create the task.
- The task's business domain MUST match the chosen scenario's domain exactly.
- The employer described in the company context is administering the assessment; it is NOT the business domain of the task.
- DO NOT invent a new domain and DO NOT blend the employer domain with the chosen scenario.
- If you notice you are drifting into a domain that does not appear in the scenarios, STOP and restart with one listed scenario.
- The task scenario should closely align with the business context, technical requirements, and implementation problem described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the chosen business domain, the Django or Django REST Framework context, and the concrete problem the candidate will solve.
2. What will the task look like? Describe the type of implementation, refactor, optimization, or bug fix required, the expected deliverables, and how it fits an INTERMEDIATE Django engineer.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_PYTHON_DJANGO_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect highly experienced in Python and Django, you are given a list of real-world scenarios and a target proficiency for Django.
Your job is to generate a complete assessment task definition that evaluates an INTERMEDIATE Django backend engineer through a realistic, well-scoped task in an existing codebase.

## SCENARIO LOCK (mandatory)
- You MUST pick EXACTLY ONE scenario from `real_world_task_scenarios`.
- The generated task's BUSINESS DOMAIN must match the chosen scenario's domain exactly. DO NOT invent a new domain.
- The generated task's current implementation problem and the candidate's task bullets must come from the chosen scenario, adapted to Django and the listed competencies.
- The candidate's employer is described in `organization_background`. The employer is administering the assessment; it is NOT the domain of the task.
- DO NOT use the employer's domain unless that same domain explicitly appears in `real_world_task_scenarios`.
- If you find yourself writing about a domain that does NOT appear in `real_world_task_scenarios`, STOP and restart with one of the listed scenarios.
- When `real_world_task_scenarios` is empty or `(none provided)`, explicitly state which generic domain you picked and why; do not silently default to the employer's domain.

## PROFICIENCY BOUNDARY
This task is for INTERMEDIATE proficiency and should fit within {minutes_range} minutes.
- Target 4-5 combined concepts, not a single trivial fix.
- Appropriate concepts include Django models, views, serializers, ORM query optimization, migrations, DRF authentication, pagination, filtering, unit tests, debugging, refactoring, basic caching, and basic security practices.
- The task may involve improving an existing moderate-complexity application with maintainable code and tests.
- Do NOT turn this into system design, microservices architecture, advanced distributed concurrency, security hardening programs, or broad cloud deployment work.
- Cloud or deployment tools may be mentioned in context only, but they must not be the primary skill being assessed.

## NATURE OF THE TASK
- The task must ask the candidate to implement a feature, refactor an existing implementation, fix logical bugs, optimize Django ORM usage, improve API behavior, or add tests in an existing Django codebase.
- The task must be specific and bounded, not open-ended architecture exploration.
- The question scenario must be realistic and grounded in the chosen scenario's current implementation problem.
- Generate enough starter code for the candidate to begin productively, but DO NOT give away the solution.
- The starter project should be runnable, but incomplete or inefficient in the exact areas the candidate must improve.
- The task must assess practical Django engineering judgment: correctness, maintainability, query efficiency, API consistency, validation, and testing.
- The question must NOT include hints. Hints belong only in the `hints` field.
- Use modern Python 3.10+ and current Django / Django REST Framework conventions.

## SKILLS TO ASSESS
The generated task should naturally assess several of the following, as long as they fit the chosen scenario:
- Django models, views, serializers, URL routing, and ORM usage
- Django REST Framework endpoint behavior
- Authentication or access control already present in the app, preserved or corrected
- Pagination and filtering behavior
- Query optimization using Django ORM tools such as `select_related`, `prefetch_related`, `annotate`, or better queryset structure
- Migrations for indexes or schema adjustments that support the scenario's access patterns
- Basic caching where appropriate for repeated reads
- Input validation and consistent JSON error responses
- Unit tests or API tests using Django test tools / pytest
- Refactoring duplicated logic into reusable modules, queryset methods, services, or utilities
- Basic security practices such as enforcing user scoping and avoiding data leakage

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including documentation, search engines, and AI tools.
- Therefore, the task must require real engineering judgment and integration skill, not something solvable by a single copy-paste snippet.
- The task should reward candidates who can reason about Django behavior, query patterns, validation, tests, and maintainable code changes.

## CODE GENERATION INSTRUCTIONS
Create a Django backend task that:
- Uses the chosen scenario as the source of truth for business domain and implementation shape.
- Matches INTERMEDIATE complexity for a backend engineer with roughly 3-5 years of experience.
- Focuses on moderate-complexity application work inside an existing Django codebase.
- Requires the candidate to make meaningful code changes across a few files, not dozens of files.
- Includes proper testing expectations and observable verification steps.
- Can be completed within {minutes_range} minutes.

## INFRASTRUCTURE REQUIREMENTS
Because datastore support is available, include containerized local infrastructure for the task.
- Include a `docker-compose.yml` that brings up the required datastore service or services used by the task.
- Include a `run.sh` that uses `docker compose up -d` and waits for the datastore to become ready.
- Include a `kill.sh` that uses `docker compose down` and cleans up task resources safely.
- Include Django application files and a `requirements.txt`.
- Do NOT include `apt-get install`, `pip install`, or other package installation commands for common runtime/framework dependencies inside `run.sh`.
- Keep infrastructure minimal and directly relevant to the task.
- Prefer a single datastore unless the chosen scenario clearly needs more than one.
- If using PostgreSQL, wire Django settings and compose consistently.
- If using Redis for caching, keep it basic and scenario-relevant.

## STARTER CODE REQUIREMENTS
- The generated code files must be valid and executable.
- The project should include a small but realistic Django app structure.
- The core logic the candidate must improve should be incomplete, inefficient, inconsistent, or logically incorrect.
- Do NOT include the final optimized implementation in the starter code.
- Do NOT include `TODO` comments or comments that reveal the intended fix.
- Avoid syntactic errors; use logical gaps or realistic suboptimal implementations instead.
- The task may include existing endpoints, serializers, models, tests, and migrations, but the candidate should still need to implement the important improvements.
- Keep the file set concise and focused.

## README REQUIREMENTS
The `README.md` must contain these sections:
- Task Overview
- Guidance
- Objectives
- How to Verify

Rules for README:
- `Task Overview` must contain 2-3 meaningful sentences describing the exact business scenario and current implementation problem from the chosen scenario.
- `Guidance` must briefly explain the purpose of the provided files in bullet points.
- `Objectives` must list clear, measurable outcomes the candidate should achieve.
- `How to Verify` must describe observable checks, API behaviors, or test commands/results the candidate can use to confirm success.
- Do NOT include setup instructions or solution steps in the README.
- Do NOT include direct hints in the README.

## OUTPUT JSON SCHEMA
Your output must be a valid JSON object using EXACTLY these top-level keys:

{{
  "name": "Short task title",
  "question": "Full candidate-facing task description with scenario, current implementation, and specific asks.",
  "code_files": {{
    "README.md": "Candidate-facing README content",
    ".gitignore": "Git ignore content",
    "requirements.txt": "Python dependencies",
    "docker-compose.yml": "Compose file for required datastore services",
    "run.sh": "Startup script using docker compose up -d",
    "kill.sh": "Cleanup script using docker compose down",
    "manage.py": "Django manage entrypoint",
    "project/settings.py": "Django settings",
    "project/urls.py": "Project URLs",
    "app/models.py": "Starter models or existing models",
    "app/views.py": "Starter views or viewsets",
    "app/serializers.py": "Starter serializers if needed",
    "app/urls.py": "App URLs if needed",
    "app/tests.py": "Starter tests or failing tests",
    "app/migrations/0001_initial.py": "Initial migration if needed"
  }},
  "answer": {{
    "summary": "High-level evaluator-facing solution summary",
    "key_points": ["point 1", "point 2"],
    "verification": ["check 1", "check 2"]
  }},
  "definitions": {{
    "term": "definition"
  }},
  "hints": "A single-line gentle nudge that does not reveal the solution.",
  "outcomes": "2-3 lines describing expected results in simple English.",
  "pre_requisites": "Bullet-point list of tools and environment assumptions.",
  "short_overview": "Bullet-point list in simple language summarizing the problem, implementation goal, and expected outcome."
}}

## CANONICAL KEY RULES
- Use `name`, not `title` or `task_title`.
- Use `question`, not `context` or `candidate_instructions`.
- Use `code_files`, not `files` or `repository_structure`.
- Use `answer` exactly as the evaluator-facing solution field.
- Also include `definitions`, `hints`, `outcomes`, `pre_requisites`, and `short_overview` exactly with those names.

## FILE CONTENT RULES
- `requirements.txt` should include Django, djangorestframework, and any minimal supporting packages actually used.
- `.gitignore` should ignore Python cache files, virtual environments, logs, local database artifacts if any, and editor noise.
- `run.sh` and `kill.sh` should be idempotent and concise.
- `docker-compose.yml` must not include a version field.
- Use hardcoded local development values rather than `.env` references.
- Keep code style clean and PEP 8 aligned.
- Ensure the generated repository is coherent: imports, settings, URLs, and app names should line up.

## TASK DESIGN CALIBRATION
Use the role context and competencies below to calibrate the task:
- Competencies: {competencies}
- Role context: {role_context}
- Real-world scenarios: {real_world_task_scenarios}

The final task should feel like a realistic backend ticket for an intermediate Django engineer: a moderate refactor or optimization with tests, validation, and maintainability concerns, not a greenfield platform build.
"""


PROMPT_REGISTRY = {
    "Python - Django (INTERMEDIATE)": [
        PROMPT_PYTHON_DJANGO_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_DJANGO_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_DJANGO_INTERMEDIATE_INSTRUCTIONS,
    ]
}