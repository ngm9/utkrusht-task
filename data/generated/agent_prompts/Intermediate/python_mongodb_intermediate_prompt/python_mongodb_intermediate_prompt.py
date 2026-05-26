PROMPT_MONGODB_PYTHON_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MONGODB_PYTHON_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and MongoDB assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- Prefer a task where the candidate improves an existing Python service that uses MongoDB rather than building a large system from scratch.
- Keep the task specific and bounded: one API area, one or two collections, and a clear success path.

Before proceeding to the full task generation, first confirm your understanding by answering:

1. What will the task be about? Describe the business domain, the Python service behavior, and the MongoDB data problem the candidate will solve.
2. What will the task look like? Describe the expected code changes, data-access improvements, and why they fit an INTERMEDIATE Python + MongoDB assessment.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_MONGODB_PYTHON_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python application development and MongoDB-backed services, you are given a list of real-world scenarios and proficiency levels.
Your job is to generate a complete assessment task definition that evaluates a candidate's ability to debug, refactor, implement, and improve a moderate-complexity Python application that uses MongoDB.

The generated task must stay within the competency scope for:
- Python (INTERMEDIATE)
- MongoDB (INTERMEDIATE)

The task should assess practical engineering ability, not rote recall.

## TASK SHAPE
Generate a task for a Python application that already runs and already connects to MongoDB, but has a small set of realistic issues in one bounded workflow. The candidate should need to:
- read and understand existing Python modules,
- improve MongoDB CRUD and/or aggregation behavior,
- add or correct indexes aligned to query patterns,
- improve validation and error handling,
- make the behavior more robust and maintainable,
- and verify the result with tests or clear checks.

The task must be completable within {minutes_range} minutes by an INTERMEDIATE candidate.

## SCOPE BOUNDARIES
Stay within these practical areas:
- Python modules, functions, classes, exceptions, file handling, JSON/CSV handling where relevant, standard library usage, API/service code, maintainable refactoring, debugging, unit tests, and moderate performance improvements.
- MongoDB CRUD operations, update operators, aggregation pipelines of moderate complexity, embedding vs referencing decisions when directly relevant, projections, pagination, duplicate-key handling, idempotent writes, and index design tied to the task's query patterns.
- Reasonable observability and verification such as logs, response behavior, and measurable before/after checks.

Do NOT make the task primarily about:
- replica set administration, sharding, elections, rollback drills, Atlas administration, Kubernetes, Terraform, LDAP, x.509, FLE, backup operations, or cluster-level operations;
- advanced distributed systems design;
- microservices architecture;
- browser automation or frontend work;
- security hardening as the main focus.

Security awareness may appear only in a limited, application-level way such as safe error handling or not exposing sensitive values.

## PREFERRED TASK STYLE
Use a realistic "fix and improve an existing service" format.
Good examples of acceptable focus:
- a Python API endpoint with inefficient MongoDB access patterns,
- incorrect update behavior causing duplicates or bad partial updates,
- missing index support for a common filtered listing,
- a CSV or JSON import flow that should become idempotent and more memory-safe,
- a reporting endpoint that should use aggregation and projection more effectively,
- a session or catalog workflow with better error handling and data consistency.

Avoid open-ended platform redesigns.

## PYTHON EXPECTATIONS
The generated starter project should reflect intermediate Python work:
- modular code split across a few files,
- at least one class or clearly structured service layer,
- proper exception handling,
- readable code organization,
- use of standard library where appropriate,
- unit tests using pytest or unittest,
- no syntactic traps or broken environment.

## MONGODB EXPECTATIONS
The generated task should reflect intermediate MongoDB work:
- one or two collections with realistic documents,
- query/update logic that can be improved,
- at least one meaningful index decision tied to the task,
- optional aggregation pipeline if it naturally fits the scenario,
- practical use of operators such as `$set`, `$unset`, `$inc`, `$addToSet`, `$push`, `$pull`, or upsert behavior where appropriate,
- clear trade-offs around correctness, maintainability, and performance.

Do not require cluster administration or advanced operational commands as the main deliverable.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use external resources, including official documentation, search engines, Stack Overflow, and AI tools.
Therefore, the task should require real engineering judgment: understanding the current implementation, identifying the root cause, making pragmatic code and data-access changes, and preserving behavior while improving correctness and performance.

## INFRASTRUCTURE REQUIREMENTS
This task is for:
- runtime: python
- frameworks: none
- datastore: MongoDB via docker compose
- kind: app

Therefore the generated task MUST include:
- a `docker-compose.yml` that starts MongoDB,
- a `run.sh` that runs `docker compose up -d`, waits for MongoDB readiness, seeds data if needed, and validates the app can run,
- a `kill.sh` that runs `docker compose down` and cleans up task resources,
- Python application files,
- `requirements.txt`,
- `.gitignore`,
- a seed script or initialization script for MongoDB,
- a README.md,
- and tests.

Do NOT include a Dockerfile for the Python app unless it is truly necessary. For this task shape, the Python app should run directly with the local runtime and connect to the MongoDB container started by docker compose.

Do NOT include `apt-get install`, `pip install`, or `npm install` commands for the runtime itself in `run.sh`.
If dependencies are needed, they should be declared in `requirements.txt`. Keep `run.sh` focused on starting MongoDB, waiting for readiness, and seeding/validating.

## STARTER CODE REQUIREMENTS
The starter code must be valid and executable, but incomplete or flawed in a realistic way.
It must:
- run without syntax errors,
- include enough structure that the candidate can start immediately,
- avoid giving away the final solution,
- contain logical issues or incomplete behavior aligned with the task,
- leave room for the candidate to implement the core fix.

The starter code MUST NOT:
- contain comments that reveal the intended solution,
- contain placeholder comments like TODO, FIXME, or "implement here",
- contain the final optimized query/index/update logic if that is what the candidate is meant to add.

## README REQUIREMENTS
The generated README.md must contain these sections exactly:
- Task Overview
- Guidance
- Objectives
- How to Verify

The README must be fully populated with meaningful, task-specific content.
Do not include setup commands or deployment instructions in the README.
Do not include direct hints or solution steps.

## OUTPUT JSON SCHEMA
Your output must be a single valid JSON object using exactly these top-level keys:

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
    "seed_data.py": "full file contents",
    "app.py": "full file contents",
    "config.py": "full file contents",
    "services/__init__.py": "",
    "services/catalog_service.py": "full file contents",
    "services/repository.py": "full file contents",
    "models.py": "full file contents",
    "tests/test_app.py": "full file contents"
  }},
  "answer": {{
    "summary": "High-level solution summary",
    "key_points": ["point 1", "point 2"],
    "verification": ["check 1", "check 2"]
  }},
  "definitions": {{
    "term": "definition"
  }},
  "hints": "A brief non-revealing hint",
  "outcomes": "Simple expected outcomes in 2-3 lines",
  "pre_requisites": "Bullet-point list of tools and knowledge required",
  "short_overview": "Bullet-point list summarizing the task"
}}

Use exactly those canonical keys:
- "name"
- "question"
- "code_files"
- "answer"
- "definitions"
- "hints"
- "outcomes"
- "pre_requisites"
- "short_overview"

Do not use synonyms such as "title", "files", "task_title", "candidate_instructions", or "repository_structure".

## FILE CONTENT REQUIREMENTS

### README.md
Must include:
- Task Overview: 2-3 concrete sentences about the business scenario and current problem.
- Guidance: short bullet points describing important files and boundaries.
- Objectives: measurable outcomes the candidate should achieve.
- How to Verify: observable checks after implementation.

### .gitignore
Use a sensible Python gitignore including items such as:
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.venv/`
- `venv/`
- `.env`
- `*.log`

### requirements.txt
Include only the dependencies actually needed for the task.
Reasonable examples for this task shape may include:
- Flask
- pymongo
- pytest
- requests

### docker-compose.yml
Must:
- start a MongoDB service,
- avoid a `version` field,
- use hardcoded values rather than env-file references,
- expose MongoDB on a standard port,
- mount an initialization or data directory only if needed.

### run.sh
Must:
- use `docker compose up -d`,
- wait until MongoDB is ready,
- seed the database if the task requires starter data,
- perform a lightweight validation step,
- print clear status messages,
- be idempotent enough for repeated runs.

### kill.sh
Must:
- use `docker compose down`,
- clean up related resources safely,
- ignore already-removed resources where appropriate,
- print clear status messages.

### Python application files
Must:
- be organized and readable,
- include a small but realistic API or service,
- connect to MongoDB through a repository or service layer,
- include the flawed or incomplete logic the candidate must improve,
- avoid embedding the final answer.

### tests/test_app.py
Must:
- include a few focused tests around the target behavior,
- be runnable,
- avoid giving away the entire implementation,
- verify externally visible behavior rather than internal implementation details only.

## TASK DESIGN GUIDANCE
Generate a task that is specific, realistic, and bounded. Prefer one of these patterns:

1. Existing API endpoint improvement
- Example shape: a listing or update endpoint is functionally present but has poor partial-update behavior, duplicate array values, weak error handling, and no supporting index.

2. Import or synchronization workflow
- Example shape: a CSV or JSON import path loads too much into memory, writes duplicate records, or stores inconsistent field types.

3. Reporting or summary endpoint
- Example shape: a Python endpoint computes summaries inefficiently in application code instead of using a more appropriate MongoDB query or aggregation pipeline.

For INTERMEDIATE level, combine around 4-5 concepts total, such as:
- Python refactoring,
- exception handling,
- MongoDB update semantics,
- index-aware query improvement,
- and tests or verification.

## QUALITY BAR
The generated task should:
- feel like a real ticket from a production team,
- have multiple valid implementation paths,
- reward sound trade-off decisions,
- be neither trivial nor architecture-heavy,
- and remain solvable within {minutes_range} minutes.

## FINAL REMINDERS
- Use one scenario from `{real_world_task_scenarios}` as inspiration.
- Align with `{role_context}` and `{competencies}`.
- Keep the task within intermediate Python and intermediate MongoDB scope.
- Ensure all braces in examples or JSON are escaped except valid placeholders.
- Return only a JSON object in the downstream generation step, not markdown.
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), Python (INTERMEDIATE)": [
        PROMPT_MONGODB_PYTHON_INTERMEDIATE_CONTEXT,
        PROMPT_MONGODB_PYTHON_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_MONGODB_PYTHON_INTERMEDIATE_INSTRUCTIONS,
    ]
}