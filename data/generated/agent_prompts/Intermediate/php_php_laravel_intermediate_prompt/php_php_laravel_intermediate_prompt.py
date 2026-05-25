PROMPT_PHP_LARAVEL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

You are generating an INTERMEDIATE-level assessment for these competencies:
{competencies}

Based on this information, summarize what you understand about the company, the role expectations, and the kind of PHP/Laravel work this candidate should be able to handle before proceeding.
"""

PROMPT_PHP_LARAVEL_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating an INTERMEDIATE assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- The task must fit the PURE_CODE category exactly: source code only, with no Docker, no containers, and no external infrastructure files.
- Use PHP 8.x and Laravel conventions.
- The task should feel like a realistic production work item for an intermediate Laravel engineer: extending or refactoring an existing module, endpoint, service, migration, or query path.
- The task must combine 4-5 relevant concepts, such as typed PHP service design, controller/service separation, Eloquent query improvement, migration/index changes, caching, error handling, or a focused feature test.
- Prefer a scenario grounded in an existing Laravel codebase rather than greenfield app creation.
- The candidate should implement or fix code, not set up the environment.
- Keep the scope completable within {minutes_range} minutes.
- Draw inspiration from ONE scenario above. If one scenario is especially concrete and well-scoped, prefer it.

Briefly confirm your plan before generating the task:
1. What business/domain scenario will the task use?
2. What existing Laravel code will the candidate modify?
3. Which intermediate-level concepts will be assessed, and why are they appropriate?
"""

PROMPT_PHP_LARAVEL_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements — PHP + Laravel

## GOAL
As a technical architect, generate a complete assessment task for an INTERMEDIATE PHP/Laravel engineer. The task must evaluate practical implementation ability in a realistic Laravel codebase using modern PHP 8.x and Laravel patterns.

The task must stay within the competency scope for PHP and Laravel at INTERMEDIATE level. That means it may include typed PHP code, namespaces, PSR-4 structure, SOLID-oriented refactoring, Laravel controllers/services/middleware/container usage, Eloquent relationships and eager loading, migrations, caching, transactions, validation, HTTP response behavior, and focused testing. Do not make the task primarily about infrastructure setup, distributed systems, Kubernetes, advanced concurrency, or large-scale system design.

## TASK SHAPE
- Build a task around an existing Laravel feature that is buggy, slow, incomplete, or poorly structured.
- The candidate should modify starter code that already runs and reflects the current broken/incomplete implementation.
- The task should require design judgment, not just syntax repair.
- The task should be completable by one candidate in {minutes_range} minutes.
- The task should have multiple reasonable implementation paths, while still having clear expected outcomes.

## REQUIRED TECHNICAL BOUNDARIES
- Category is PURE_CODE.
- Do NOT include Docker, docker-compose, container configs, Kubernetes manifests, external databases spun up by containers, or deployment files.
- Use a source-only repository layout.
- Prefer a Laravel-style file set such as composer.json, routes, app/Http/Controllers, app/Services, app/Models, database/migrations, tests, config, bootstrap or minimal framework-supporting files as needed.
- Include only the minimum files needed to make the task coherent and runnable in principle.

## WHAT TO ASSESS
The task should assess 4-5 of the following, chosen naturally from the scenario:
- typed PHP 8.x code and clean method signatures
- refactoring controller-heavy logic into a service or repository-style class
- Eloquent relationship loading strategy and N+1 mitigation
- query constraints, select narrowing, scopes, or batching/chunking where appropriate
- a migration adding an index or constraint relevant to the problem
- Laravel cache usage with correct key design and TTL
- transaction boundaries or error handling where relevant
- request validation or response shaping where relevant
- one focused PHPUnit/Laravel feature or unit test
- preserving existing response shape or business behavior while improving internals

## AVOID
- Do not require full application installation steps as the core challenge.
- Do not make testing the primary skill; one focused test is enough.
- Do not require websockets, OAuth server setup, Horizon setup, Octane setup, or multi-service architecture.
- Do not require advanced security implementation as the main task, though basic safe coding can be part of the scenario.
- Do not turn the task into a broad architecture essay.

## STARTER CODE REQUIREMENTS
- Starter code must be valid and internally consistent.
- It must implement exactly the "Current Implementation" described in the task.
- It must not already contain the final fix.
- It must not contain TODO comments, solution hints, or commented-out answers.
- Keep the codebase compact but realistic.
- If including a Laravel endpoint, provide the relevant route, controller, model stubs/relationships, service stub if applicable, migration file(s), and one test file scaffold or partially implemented test setup.
- If using caching or query optimization, the current implementation should clearly be missing or misusing it.

## TASK DIFFICULTY CALIBRATION
This is INTERMEDIATE, so the task should reflect a candidate who can independently deliver small-to-medium Laravel features and fix common production issues. Good examples include:
- refactoring a slow API endpoint suffering from N+1 queries into a typed service with constrained eager loading
- adding a migration for a missing composite index tied to a real query path
- introducing short-lived caching while preserving response shape and correctness
- moving business logic out of a controller and adding one focused feature test

A strong default pattern is a realistic API optimization/refactor task in an existing Laravel module.

## REQUIRED OUTPUT JSON STRUCTURE (CANONICAL — use these EXACT key names)
The downstream system reads these exact top-level keys. Do NOT rename them.

{{
  "name": "task-name-in-kebab-case",
  "question": "Full candidate-facing task description.",
  "code_files": {{
    "README.md": "Candidate-facing README with the required sections below.",
    "composer.json": "Project dependencies and scripts.",
    ".gitignore": "Standard PHP/Laravel exclusions.",
    "app/Http/Controllers/ExampleController.php": "Starter controller code.",
    "app/Services/ExampleService.php": "Starter service or stub if relevant.",
    "app/Models/Example.php": "Starter model(s) as needed.",
    "routes/api.php": "Relevant route definitions.",
    "database/migrations/2026_01_01_000000_example.php": "Relevant migration(s).",
    "tests/Feature/ExampleTest.php": "Focused test file as needed"
  }},
  "outcomes": "Bullet list of expected results after completion.",
  "short_overview": "Bullet list covering business context, implementation goal, and expected outcome.",
  "pre_requisites": "Bullet list of tools and knowledge required.",
  "answer": "Evaluator-facing high-level solution summary.",
  "hints": "A brief nudge that does not reveal the solution.",
  "definitions": {{
    "n-plus-one-query": "When related records are loaded with one initial query plus many follow-up queries.",
    "eager-loading": "Loading related models up front to reduce repeated database queries."
  }}
}}

## README.md STRUCTURE
The README.md inside code_files must contain these sections with concrete, task-specific content:
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

## QUESTION CONTENT REQUIREMENTS
The "question" field must be candidate-facing and must include:
1. A short business scenario.
2. A "Current Implementation" section describing the exact current behavior represented by the starter code.
3. A "Required Changes" section listing the concrete changes the candidate must make.
4. Clear constraints, such as preserving response shape, keeping route names stable, or limiting cache TTL.
5. A concise completion target appropriate for {minutes_range} minutes.

## FILE CONTENT GUIDANCE
- Use realistic Laravel naming and structure.
- Keep the repository small enough to inspect quickly.
- Include enough code for the candidate to reason about relationships and data flow.
- Prefer one endpoint or one module over multiple unrelated features.
- If you include a migration for an index, ensure the current code actually uses a query that benefits from it.
- If you include a cache requirement, ensure the current implementation lacks that cache path.
- If you include a test, make it focused on the intended behavior rather than broad framework coverage.

## QUALITY BAR
The best tasks for this competency pair usually involve a Laravel API or internal module where the candidate must improve correctness and performance without changing the outward contract. The task should reward candidates who recognize separation of concerns, Eloquent loading strategy, indexing, and pragmatic Laravel implementation choices.

## CRITICAL REMINDERS
1. Output must be valid JSON using the exact canonical keys above.
2. The task must remain within PHP and Laravel INTERMEDIATE scope.
3. The repository must be PURE_CODE only.
4. The starter code must be runnable in principle and match the described current state.
5. Do not include the full solution in starter files.
6. Do not use placeholder text inside README sections.
7. Keep the task realistic, specific, and implementation-oriented.
"""

PROMPT_REGISTRY = {
    "PHP (INTERMEDIATE), PHP - Laravel (INTERMEDIATE)": [
        PROMPT_PHP_LARAVEL_INTERMEDIATE_CONTEXT,
        PROMPT_PHP_LARAVEL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PHP_LARAVEL_INTERMEDIATE_INSTRUCTIONS,
    ]
}