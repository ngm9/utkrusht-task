PROMPT_PYTHON_DJANGO_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_DJANGO_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python Django assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- Keep the task squarely within BASIC Django expectations: simple project structure, URLs, views, models, templates, forms, SQLite-friendly data handling, and basic debugging.
- Do not turn the task into a system design exercise or require advanced deployment, async behavior, security hardening, caching, or complex architecture.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the business domain, Django context, and the problem the candidate will be solving.
2. What will the task look like? Describe the type of implementation or bug fix required, the expected deliverables, and how it aligns with the given Python Django BASIC proficiency level.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_DJANGO_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python Django, you are given a list of real world scenarios and proficiency levels for Django.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and evaluator guidance that can be effectively used to assess the candidate's ability to build or fix a small end-to-end Django feature.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a well-scoped feature from scratch or fix logical bugs in an existing Django codebase.
- The scenario must be realistic, easy to understand, and grounded in a small business workflow.
- Generate enough starter code that gives the candidate a clear starting point without giving away the solution.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The task should assess practical Django skills at BASIC level: project structure, app structure, URLs, views, models, templates, forms, simple validation, and basic error handling.
- The task should be specific and bounded. For BASIC level, avoid open-ended product design or architecture-heavy asks.
- The question must NOT include hints. Hints belong only in the "hints" field.
- Ensure the task can be completed within {minutes_range} minutes.

### Scope Boundaries You Must Respect
The competency scope is the source of truth. Therefore:
- Allowed focus areas include Django settings, apps, URLs, models, views, templates, forms, simple model relationships, migrations, SQLite usage, Django Admin CRUD, static files, environment variables for local development, and basic debugging.
- The task may use either function-based views or minimal class-based views, but keep it simple.
- The task may ask the candidate to pass data from views to templates, validate a basic form, or fix a small bug in request handling or rendering.
- The task may include a small model and a simple relationship if needed, but do not require advanced ORM optimization or complex query design.
- The task may include a small amount of Python structure such as helper functions, simple classes, standard library usage, and basic tests if they remain lightweight and directly support the Django task.
- Do NOT require advanced deployment work, Docker, PostgreSQL, background jobs, async views, advanced security hardening, caching, microservices, API versioning, websockets, or performance tuning.
- Do NOT require system design, advanced concurrency, or complex test architecture.

### AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources they find helpful, including official documentation, search engines, community forums, and AI tools.
- The task should still require genuine reasoning, debugging, and implementation effort beyond a trivial copy-paste answer.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Django task that:
- Draws inspiration from one input scenario to determine the business context and technical requirements.
- Matches BASIC proficiency level and stays appropriate for a candidate with roughly 0-2 years of Django experience.
- Tests 2-3 combined concepts, such as view logic plus template rendering, or form validation plus model persistence, or URL handling plus error handling.
- Uses a small, realistic Django project that a candidate can run locally with standard commands.
- Keeps the implementation focused on a single app or a very small project layout.
- Uses modern, simple Django practices compatible with Python 3.10+.
- Uses PURE_CODE structure only: source files and requirements.txt. No Dockerfile, no docker-compose.yml, no infrastructure provisioning files.

## Recommended Task Shapes
Choose one of these patterns:
- Fix a broken form submission flow that currently crashes or stores invalid data.
- Fix a search/detail page where missing input or missing records cause errors and template context is incorrect.
- Implement a small create/list workflow using a model, form, view, URL, and template.
- Repair a simple admin-backed content workflow where the public page does not render or validate correctly.
- Add basic duplicate prevention or friendly validation in a small Django feature.

## Starter Code Requirements
- The starter code must be valid and runnable after installing dependencies.
- The project should include a minimal Django project structure with only the files needed for the task.
- Keep the code files minimal and focused.
- If the task is a bug-fix task, the starter code must contain logical bugs or incomplete behavior, not syntax errors.
- If the task is a feature task, the starter code should provide a clear baseline without implementing the core solution.
- The generated project must not require Docker or external services.
- Prefer SQLite-compatible defaults and simple local configuration.
- If environment variables are included, keep them minimal and local-development friendly.
- You may include a very small test file if it is lightweight and directly aligned with BASIC proficiency, but testing must not become the main skill being assessed.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "question": "A concise but complete candidate-facing task description. It must clearly describe the current behavior, the business scenario, and the specific implementation or bug fix required.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
    ".gitignore": "Sensible Python and Django exclusions",
    "requirements.txt": "Python dependencies list",
    "manage.py": "Django manage entry point",
    "project_name/settings.py": "Django settings",
    "project_name/urls.py": "Project URL configuration",
    "app_name/models.py": "Starter model code if needed",
    "app_name/views.py": "Starter view code",
    "app_name/forms.py": "Starter form code if needed",
    "app_name/urls.py": "App URL configuration if needed",
    "app_name/templates/app_name/template.html": "Starter template if needed"
  }},
  "outcomes": "Bullet-point list in simple language describing expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing the business problem, the implementation goal, and the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task.",
  "answer": "High-level solution approach for evaluators.",
  "hints": "A single-line hint that nudges the candidate in the right direction without giving away the answer.",
  "definitions": {{
    "term_1": "definition_1",
    "term_2": "definition_2"
  }}
}}

## Canonical Key Rules
- You MUST use exactly these top-level keys: "name", "question", "code_files", "answer", "definitions", "hints", "outcomes", "pre_requisites", "short_overview".
- Do NOT use synonyms such as "title", "task_title", "files", "repository_structure", "context", or "acceptance_criteria".

## Code File Requirements
- More than one file can be generated, but keep the project small and coherent.
- Code should follow basic Python and Django style conventions.
- The generated code files MUST NOT contain the completed core logic of the task.
- The starter code should be runnable, but the main requested behavior should remain incomplete or incorrect until the candidate fixes it.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments, placeholder comments, or explanatory comments that tell the candidate exactly what to change.
- Avoid fake complexity. Keep the code understandable for a BASIC-level candidate.

## PURE_CODE Category Requirements
- Include only source files and dependency files appropriate for a local Django project.
- Do NOT include Dockerfile, docker-compose.yml, init_database.sql, container configs, cloud deployment files, or infrastructure manifests.

## .gitignore Instructions
Provide a sensible Django/Python .gitignore, including entries such as:
- __pycache__/
- *.pyc
- .env
- .venv/
- db.sqlite3
- *.log
- .DS_Store
- .pytest_cache/
- .mypy_cache/
- build/
- dist/
- *.egg-info/

## README.md Instructions
The README.md must contain the following sections exactly:
- Task Overview
- Helpful Tips
- Objectives
- How to Verify

### README Content Rules
- The README.md file content MUST be fully populated with meaningful, task-specific content.
- Task Overview must contain the exact business scenario from the task description in 2-3 meaningful sentences.
- Helpful Tips must provide general guidance and project context without revealing the solution.
- Objectives must list clear, measurable goals that define successful completion.
- How to Verify must describe observable checks the candidate can perform after implementation.
- Do NOT include setup instructions or commands.
- Do NOT include direct solutions, code snippets, or step-by-step implementation instructions.

## Calibration Guidance
Use the role context and scenario inputs to calibrate the task:
- The candidate should need to read a few Django files and make focused changes.
- The task should reward readable functions, simple validation, correct template context, and basic error handling.
- If you include tests, keep them very small and easy to understand.
- The task should feel like a realistic bug fix or feature request in an existing small Django app.

## Good BASIC-Level Examples
Appropriate asks include:
- Handle invalid form input and show a friendly message instead of crashing.
- Prevent duplicate records for a simple model field combination.
- Fix a view so it passes the correct context to a template.
- Add a basic model form and save valid submissions.
- Handle missing GET or POST values safely and render the same page with feedback.

Inappropriate asks include:
- Designing a full authentication system from scratch.
- Building a multi-app architecture.
- Implementing advanced permissions or security hardening.
- Optimizing complex ORM queries.
- Requiring Redis, Celery, Docker, or cloud deployment.

## CRITICAL REMINDERS
1. Output must be valid JSON only when generating the task definition.
2. The task must stay within Django BASIC scope and PURE_CODE category.
3. The task must be completable within {minutes_range} minutes.
4. The starter code must be runnable but must NOT contain the full solution.
5. Use only the canonical top-level JSON keys.
6. README.md must be fully populated and task-specific.
7. Keep the project small, realistic, and focused on practical Django work.
"""

PROMPT_REGISTRY = {
    "Python - Django (BASIC)": [
        PROMPT_PYTHON_DJANGO_BASIC_CONTEXT,
        PROMPT_PYTHON_DJANGO_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_DJANGO_BASIC_INSTRUCTIONS,
    ]
}