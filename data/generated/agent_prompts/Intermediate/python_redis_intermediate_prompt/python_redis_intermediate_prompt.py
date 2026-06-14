PROMPT_PYTHON_REDIS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
particularly in relation to building and maintaining Python backend or automation code that uses Redis for caching,
rate limiting, coordination, or queue-like workflows?
"""

PROMPT_PYTHON_REDIS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Redis assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for INTERMEDIATE level.
- Ensure the candidate can realistically complete the task in the allocated time window.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- Because this task uses Python with Redis and no framework, the assessment should be a script or small service-style codebase, not a web framework app.

Before proceeding to the full task generation, please confirm your understanding by answering:

1. What will the task be about? Describe the business domain, technical context, and the Redis-backed Python problem the candidate will solve.
2. What will the task look like? Describe the existing script or service behavior, the Redis issue or design flaw to be fixed, the expected deliverables, and why this fits INTERMEDIATE proficiency.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_REDIS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python and Redis, you are given real-world scenarios and proficiency levels for Python and Redis.
Your job is to generate a complete assessment task for an INTERMEDIATE candidate. The candidate should receive a working Python codebase that already uses Redis but contains realistic correctness, consistency, concurrency, or performance issues. The candidate's responsibility is to analyze the existing implementation and fix or improve it.

The task must stay within the competency scope:
- Python: modular code, functions/classes, data structures, error handling, file/data handling where useful, debugging, refactoring, testing, performance-minded implementation, and moderate architecture decisions.
- Redis: key naming, TTL strategy, choosing core data structures, pipelining, MULTI/EXEC, WATCH, Lua where appropriate, client pooling, cache consistency, rate limiting, task queue or coordination patterns, and diagnosis of common latency/correctness issues.
- Do NOT require advanced Redis operations as the primary task focus such as Sentinel deployment, Cluster resharding, persistence migration, ACL/TLS hardening, or full observability stack setup. Those may be mentioned as context only, not required deliverables.

## TASK SHAPE
This task must match the runtime metadata:
- Runtime: python
- Frameworks: none
- Datastore: Redis via docker-compose
- Kind: script

Therefore:
- Generate a Python script-style repository, not a FastAPI/Flask app.
- Include docker-compose.yml that starts Redis.
- Include run.sh that uses `docker compose up -d`.
- Include kill.sh that uses `docker compose down`.
- Do not include a Dockerfile for the Python app unless absolutely necessary. For this kind, the Python code should run directly on the host/task environment.
- The candidate should work on Python modules, scripts, and tests.

## CANDIDATE EXPECTATION
The candidate will receive:
- A working Python repository with Redis integration already implemented.
- A Redis container started by docker-compose.
- Existing code that runs but has intermediate-level issues such as stale cache behavior, non-atomic updates, poor key design, missing TTLs, unnecessary round-trips, weak failure handling, or inefficient Redis usage.
- A small test suite or verification script that demonstrates the current broken or suboptimal behavior.

The candidate's job is to improve the implementation without rebuilding the project from scratch.

## NATURE OF THE TASK
- The task must be grounded in ONE scenario from {real_world_task_scenarios}.
- The task must be realistic for an engineer with 3-5 years of experience.
- The task should combine 4-5 concepts, not just one isolated syntax fix.
- The task should be completable within {minutes_range}.
- The codebase must be fully runnable before the candidate changes anything.
- The exact problem described in the question must exist in the code files.
- The candidate should need to modify existing Python and Redis integration logic, not infrastructure.
- The task should allow multiple reasonable solution paths where appropriate.

## GOOD INTERMEDIATE PYTHON + REDIS TASK THEMES
Choose one theme inspired by the provided scenarios:
- Read-through cache with stale data and cache stampede risk.
- Atomic rate limiter implemented incorrectly with separate Redis commands.
- Inventory or quota reservation with non-atomic read-modify-write logic.
- Batch retrieval or aggregation code that makes many Redis round-trips and should use pipelining or better key/data structure choices.
- Queue or retry workflow with weak failure handling and inconsistent Redis state.

## WHAT THE STARTER CODE SHOULD CONTAIN
The generated repository should usually include files like these, adapted to the chosen scenario:
- README.md
- .gitignore
- requirements.txt
- docker-compose.yml
- run.sh
- kill.sh
- src/__init__.py
- src/config.py
- src/redis_client.py
- src/models.py
- src/service.py
- src/tasks.py or src/worker.py or src/cache_logic.py
- src/main.py
- tests/test_task.py
- Optional sample JSON/CSV fixture files if they support the scenario

All Python package directories must include __init__.py.

## IMPLEMENTATION REQUIREMENTS
- Use Python 3.10+ compatible code.
- Use redis-py.
- Use a shared Redis client or connection pool in the starter code, but it may still be suboptimal in behavior.
- Include realistic domain models or data structures using classes and functions where helpful.
- Include proper but incomplete error handling so the app runs, while leaving meaningful improvements for the candidate.
- Include tests or a verification script that expose the bug, race, stale-data issue, or inefficiency.
- If concurrency is part of the scenario, keep it moderate and practical, such as parallel requests simulated by threads in tests.
- Do not require external services other than Redis.
- Do not require advanced deployment or cloud setup.

## REDIS-SPECIFIC REQUIREMENTS
The task may require the candidate to reason about some of the following, but only as appropriate to the chosen scenario:
- Better key naming and namespacing.
- TTL selection aligned to freshness needs.
- Atomicity using Lua, WATCH/MULTI/EXEC, or a safer Redis pattern.
- Pipelining to reduce round-trips.
- Choosing String, Hash, Set, List, or Sorted Set appropriately.
- Graceful behavior when Redis is temporarily unavailable.
- Avoiding stale cache after successful writes.
- Preventing duplicate work under concurrent cache misses.

Do not make the task depend on Redis Cluster, Sentinel, persistence tuning, ACLs, TLS, or exporter/dashboard setup.

## INFRASTRUCTURE REQUIREMENTS
### docker-compose.yml
- Must include a Redis service.
- Redis port must be bound to localhost only using `127.0.0.1:6379:6379`.
- Must NOT include a version field.
- Must NOT include .env references.
- Use simple hardcoded configuration.

### run.sh
- Must use `docker compose up -d`.
- Must wait until Redis is ready.
- Must validate Redis is reachable.
- Must avoid installing the Python runtime itself.
- May install Python dependencies from requirements.txt if needed.
- Must be robust and readable.

### kill.sh
- Must use `docker compose down`.
- Must be idempotent.
- Must clean up project-related artifacts safely.

## README REQUIREMENTS
README.md must contain these sections in this order:
1. Task Overview
2. Objectives
3. How to Verify
4. Helpful Tips

Guidance:
- Task Overview: 3-4 sentences describing the business scenario and the current problem in product terms.
- Objectives: measurable outcomes, focused on correctness, consistency, latency, or maintainability.
- How to Verify: concrete checks the candidate can run after changes.
- Helpful Tips: open-ended guidance that nudges investigation without prescribing the exact fix.
- Do not include step-by-step solution instructions.
- Do not mention exact implementation details that give away the answer.

## TESTING REQUIREMENTS
Because INTERMEDIATE Python scope includes testing, include a small pytest suite.
- Tests should fail or expose the issue before the candidate fixes the code.
- Tests should be realistic and focused on behavior.
- If concurrency is relevant, include a bounded concurrency test that is still practical.

## AI AND EXTERNAL RESOURCE POLICY
Candidates may use external resources and AI tools. The task should still require real reasoning about Python design, Redis behavior, and tradeoffs.

## REQUIRED OUTPUT JSON STRUCTURE
You must output a single JSON object using exactly these top-level keys:
- "name"
- "question"
- "code_files"
- "answer"
- "definitions"
- "hints"
- "outcomes"
- "pre_requisites"
- "short_overview"

Do not use alternative top-level keys such as "title", "task_title", "files", "repository_structure", or "acceptance_criteria".

Use this exact schema shape:
{{
  "name": "short-task-name-in-kebab-case",
  "question": "Candidate-facing task description. Clearly describe the current implementation and the required changes without revealing the exact solution.",
  "code_files": {{
    "README.md": "...",
    ".gitignore": "...",
    "requirements.txt": "...",
    "docker-compose.yml": "...",
    "run.sh": "...",
    "kill.sh": "...",
    "src/__init__.py": "...",
    "src/config.py": "...",
    "src/redis_client.py": "...",
    "src/models.py": "...",
    "src/service.py": "...",
    "src/main.py": "...",
    "tests/__init__.py": "...",
    "tests/test_task.py": "..."
  }},
  "answer": "High-level evaluator-facing solution summary.",
  "definitions": {{
    "term_1": "definition",
    "term_2": "definition"
  }},
  "hints": "A single-line hint that nudges investigation without giving away the fix.",
  "outcomes": "2-4 short bullet-style lines describing expected end-state behavior.",
  "pre_requisites": "Bullet-style list of tools and knowledge needed.",
  "short_overview": "Bullet-style list summarizing the business problem, technical focus, and expected outcome."
}}

## QUALITY BAR
- The repository must be coherent and runnable.
- The scenario, README, tests, and buggy code must all match.
- The task must assess applied Python and Redis competence, not trivia.
- The task must not drift into framework-specific web development unless the chosen scenario naturally uses simple script-based request simulation.
- Keep the scope moderate enough for the allotted time while still requiring meaningful engineering judgment.
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), Redis (INTERMEDIATE)": [
        PROMPT_PYTHON_REDIS_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_REDIS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_REDIS_INTERMEDIATE_INSTRUCTIONS,
    ]
}