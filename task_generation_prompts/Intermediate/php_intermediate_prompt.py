PROMPT_PHP_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PHP_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a PHP assessment task.

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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and the architectural / performance / correctness problem the candidate will be solving)
2. What will the task look like? (Describe the type of PHP refactor, feature, or bug-fix required, the expected deliverables, and how it aligns with INTERMEDIATE PHP proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PHP_INTERMEDIATE = """
## GOAL
As a senior PHP architect with deep experience across modern PHP 8.x, the major PHP frameworks (Laravel, Symfony, Slim), Composer, PSR standards, PDO, Eloquent/Doctrine, queueing, caching, and PHPUnit, you are given a list of real-world scenarios and proficiency levels for PHP development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc., that can be effectively used to assess a 3-5 yoe PHP candidate's ability to read a non-trivial codebase, identify the architectural / performance / correctness problem, and deliver a focused, well-structured fix or feature end-to-end.

**FRAMEWORK / RUNTIME IS DERIVED FROM THE SCENARIO.** If the scenario explicitly names Laravel, Symfony, Slim, or vanilla PHP, the starter code, file layout, container/DI wiring, and run/test commands MUST follow that stack's conventions. Do NOT silently swap stacks. If the scenario is framework-agnostic, default to a small Composer + PSR-4 project using PDO and PHPUnit.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to refactor existing code, fix a complex/architectural bug, or implement a focused feature on top of provided starter code (extract a service, introduce a repository interface, fix N+1, add a cache layer, map domain exceptions to HTTP responses, etc.).
- The question scenario must be clear, with realistic facts, figures, company names, table/column names, route paths, latency numbers, and HTTP status codes that are consistent with the chosen domain.
- Generate enough starter code that the candidate has a realistic project to read into. The starter must run on PHP 8.1+ with Composer installed.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The wrong/inefficient/missing behaviour described in the scenario MUST actually be present in the starter implementation — verify by re-reading before finalising.
- A part of the task completion is to watch the candidate make the right architectural decisions (where to draw the seam between layers, which interface to introduce, how to scope a transaction, where to place the cache, how to surface a domain exception) — not just patch the surface defect.
- The complexity of the task must align with INTERMEDIATE proficiency level (3-5 years PHP experience), ensuring no two tasks generated are similar.
- The task MUST stay TIME-BOXED to {minutes_range} minutes. If the candidate would need to refactor multiple endpoints, introduce multiple new abstractions, redesign indexes, AND write a full test suite — the task is over-scoped and must be cut down. Pick ONE focused architectural change plus 1-2 supporting tests.

### INTERMEDIATE PROFICIENCY SCOPE (3-5 yoe — what the task may assess)
Tasks should test deeper PHP and architectural understanding. The task may assess one or more of:

- **Modern PHP 8.x mastery**: readonly properties, enums, first-class callable syntax, union/intersection types, attributes used for routing/validation/DI, null-safe access, `match` expressions
- **Architectural decomposition**: extracting a service from a controller, introducing a repository or adapter interface, separating domain/application/infrastructure layers, applying SOLID principles in a focused way
- **Dependency injection**: framework container wiring (Laravel service container, Symfony DI / `services.yaml`), constructor injection, binding interfaces to implementations
- **Performance and data-access patterns**: eliminating N+1 with eager loading or grouped queries, switching to streaming/cursor/chunked iteration for large exports, adding the right index, choosing between query-side aggregation and PHP-side reduction
- **Caching**: cache-aside with deterministic keys, sensible TTLs, invalidation tied to a domain event, awareness of cache stampede in mild form
- **Exception design and HTTP mapping**: custom domain exceptions, exception hierarchy, mapping to stable HTTP status codes and JSON error shapes without leaking internal details (no Guzzle/PDO messages reaching the client)
- **Concurrency and consistency at the request boundary**: PDO/Eloquent/Doctrine transactions, idempotency keys, retry-safe operations
- **Testing**: writing focused PHPUnit tests (unit + a couple of integration-style tests with an in-memory or sqlite DB), mocking via interfaces, asserting on observable behaviour rather than internal calls
- **Modern tooling**: Composer scripts, autoloading via PSR-4, `phpstan`/`psalm` awareness (the candidate doesn't have to run them, but the task code should not produce obviously wrong types)

Do NOT require: CQRS, event sourcing, custom annotation/attribute parsers, building a DI container, hexagonal architecture across multiple bounded contexts, or full-blown distributed system patterns. Those go beyond INTERMEDIATE.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts inside the question and README:

**Current Implementation (what we give to the candidate):**
- Describe precisely the architectural / performance / correctness problem implemented in the starter code, with concrete numbers from the scenario (table names, route paths, request volumes, observed latency, error messages, HTTP codes the client currently sees).
- Examples: "`ExportController::buildCsv()` loads all matching `Shipment` models into memory and concatenates one giant CSV string — `php artisan shipments:export` fails with `Allowed memory size exhausted` on the 180k-row dataset and the HTTP variant times out at 504"; "`AvailabilityController::show()` and `FareRulesController::show()` each instantiate `new GuzzleHttp\\Client()` and call the supplier API on every request, taking ~1.7s and turning supplier 404/429 responses into `500 Undefined array key 'data'`".
- The **starter code MUST perfectly implement this current behaviour** — the N+1 must really happen, the per-request client must really be created, the exception leakage must really occur. Do NOT pre-fix anything.

**Required Changes (the candidate's deliverable):**
- A short, concrete checklist of behaviour changes: which class to extract, which interface to introduce, which query to rewrite, which exception to add and where to map it, which 1-2 tests to add.
- Each item must be observable — a different latency number, a different DB query count, a different HTTP status, a passing test. Vague "improve the architecture" items are a defect.
- Keep the checklist TIGHT — 3 to 5 items. If you are tempted to add a sixth, drop the least observable one. Time-box discipline is the single most common failure mode for INTERMEDIATE tasks.

### AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources, including Google, Stack Overflow, official PHP/Laravel/Symfony/Doctrine docs, and AI-powered tools or LLMs.
- The tasks are designed to assess judgment: which seam to introduce, which query to rewrite, where to put the cache. Complexity should reflect INTERMEDIATE PHP proficiency while requiring genuine engineering decisions that go beyond a single AI prompt.

### Code Generation Instructions
Based on the chosen real-world scenario, create a PHP task that:
- Uses the business domain and stack from the chosen scenario as the source of truth
- Matches INTERMEDIATE proficiency level (3-5 years PHP experience), keeping in mind that AI assistance is allowed
- Tests practical PHP architecture skills: refactoring for testability, eliminating N+1, introducing a focused abstraction, mapping domain exceptions to HTTP, writing a couple of meaningful tests
- Time constraints: the task should be finishable within {minutes_range} minutes — re-check this against the checklist of required changes
- Picks a different real-world scenario each generation to ensure variety
- Focuses on ONE service or endpoint at a time — NOT a cross-cutting refactor over many endpoints
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "shipments-export-streaming-refactor", "flight-supplier-adapter-extraction", "payment-intent-idempotency-middleware")
- **CRITICAL - FILE NAMING**: All additional controller, service, repository, adapter, middleware, exception, DTO, and utility files MUST use meaningful, scenario-specific file names derived from the task (e.g., `FlightSupplierAdapter.php`, `ShipmentExportService.php`, `EnsureIdempotency.php`, `PaymentIntentController.php`, `SupplierUnavailableException.php`). NEVER use generic placeholder names like `ServiceA.php`, `RepositoryX.php`, `MyAdapter.php`, `Helper.php`, or `Utils.php` when a scenario-specific name is appropriate. File and class names should reflect the business domain and feature so generated code is identifiable and varies correctly per task.

### Starter Code Instructions
- The starter code must run on PHP 8.1+ with Composer installed. If a framework is named in the scenario, follow its idiomatic project layout.
- For vanilla PHP scenarios: provide `composer.json` (PSR-4 autoload + `phpunit/phpunit` in `require-dev`), a `public/index.php` front controller, `src/` with the relevant classes (controller, service, repository, exception classes), `tests/` with at least one baseline test, and a `phpunit.xml`.
- For Laravel scenarios: provide only the files relevant to the task (controller, service/repository, route definition, the relevant migration, the test, the binding in a service provider if it matters). Do NOT generate a full `laravel new` skeleton; instead, the README states the assumption that Laravel is installed via the provided `composer.json` and explains how to run the relevant artisan/test commands.
- For Symfony / Slim scenarios: same — provide only the files the candidate needs to touch, plus the relevant `services.yaml` / route file / DI binding.
- The architectural / performance / correctness defect from the scenario MUST actually be present in the starter — verify before finalising.
- Provide partial implementations that the candidate must complete or refactor — NOT a blank skeleton.
- Include at least one existing class/interface that the candidate either reuses, extends, or refactors against. This signals the architectural seam.
- Use `declare(strict_types=1);` at the top of every PHP source file. Use modern PHP 8.x features (constructor property promotion, readonly, enums, attributes) where natural to the framework.
- DO NOT include `// TODO`, `// FIXME`, "implement this here", "add cache here", or any solution-revealing comment.
- DO NOT name variables, methods, or classes in a way that gives away the answer (e.g. `$cachedRepo`, `mappedException`, `streamCsv()` when those are exactly what the candidate is supposed to introduce).

### REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Idempotency Middleware for Payment Intent API', 'Refactor Shipments CSV Export with Streaming and Generators', 'Extract Flight Supplier Adapter with Caching and Error Mapping'. The title should clearly convey the action (implement, fix, build, refactor, extract, optimize, harden) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — current implementation, what is wrong (architecturally / performance-wise / correctness-wise), and the focused changes required. Use the two-part Current Implementation / Your Task / Success Criteria framing.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
    ".gitignore": "Comprehensive PHP, Composer, framework, and IDE exclusions",
    "composer.json": "Composer manifest with PSR-4 autoload, php 8.1+ requirement, phpunit/phpunit in require-dev, and any libraries the scenario actually needs (guzzle, monolog, doctrine, illuminate components, etc.)",
    "phpunit.xml": "PHPUnit configuration",
    "src/Path/To/ControllerOrService.php": "Existing class with the architectural / performance / correctness defect present",
    "src/Path/To/RepositoryOrAdapter.php": "Supporting class the candidate will refactor against",
    "src/Path/To/Exception/RelevantException.php": "Existing exception classes if relevant — leave the missing ones to the candidate",
    "tests/RelevantTest.php": "Baseline PHPUnit test (passing or strategically failing) that the candidate's change must keep green / make green",
    "additional_file.php": "Other PHP files as the scenario requires"
  }},
  "outcomes": "Bullet-point list. Must include observable post-fix outcomes (specific latency target, specific HTTP status / JSON shape on error paths, specific DB query count or memory ceiling, specific tests that must pass) and architectural quality outcomes (single seam introduced, single interface used by both endpoints, exception mapping in one place).",
  "short_overview": "Bullet-point list describing: (1) the high-level business or technical problem, (2) the specific architectural / performance / correctness change required, (3) the expected outcome emphasising correctness, performance, and maintainability — without revealing the answer.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include PHP 8.1+, Composer 2.x, an IDE, Git, intermediate-level PHP knowledge (PSR-4, DI, PDO/Eloquent/Doctrine basics, PHPUnit), and the specific framework if named in the scenario.",
  "answer": "High-level solution approach with emphasis on the architectural decision: which seam to introduce, which query to rewrite, where to place the cache and how to key it, which exception to add and where to map it. Do NOT paste full code.",
  "hints": "A single line guiding toward the architectural approach without naming the pattern. Example: 'Look at where the supplier call lives today and ask which classes today have to know about Guzzle to do their job — and where a domain exception could be mapped once instead of in every controller'.",
  "definitions": {{
    "PSR-4": "Composer's autoloading standard mapping namespaces to file paths",
    "Repository pattern": "An abstraction over data access that lets the application layer depend on an interface rather than a concrete query implementation",
    "N+1 query": "An access pattern that issues one query for a list and then one additional query per item, instead of a single batched query",
    "Cache-aside": "A caching strategy where the application reads from cache first, falls back to the source on miss, and writes the result back to the cache",
    "Domain exception": "A custom exception class representing a meaningful business condition (e.g. supplier unavailable, invalid date range) that callers can catch and map to a stable response",
    "Service container / DI": "A framework component (Laravel container, Symfony services) that resolves dependencies and wires interfaces to concrete implementations",
    "PHPUnit": "The standard PHP testing framework for unit and integration tests"
  }}
}}

## Code file requirements
- Generate a realistic project structure for the chosen stack: vanilla (`public/`, `src/`, `tests/`), Laravel (`app/Http/Controllers`, `app/Services`, `app/Repositories`, `routes/api.php`, `tests/Feature` or `tests/Unit`), Symfony (`src/Controller`, `src/Service`, `config/services.yaml`, `tests/`).
- Code must follow modern PHP 8.x best practices and demonstrate intermediate-level patterns: constructor property promotion, readonly value objects where appropriate, type-safe interfaces, PSR-12 formatting.
- Use appropriate, NAMED design seams — but DO NOT name them in a way that gives the solution away (e.g. don't preemptively create `CachedFooRepository` if the candidate is supposed to introduce caching).
- Focus on modern PHP features and the chosen framework's idioms. Do not introduce frameworks or libraries the scenario does not justify.
- **CRITICAL**: starter code MUST contain the architectural / performance / correctness defect described in the scenario, but MUST NOT contain the fix.
- Include some existing classes/interfaces that the candidate either reuses, refactors against, or extends — this signals the seam without dictating the fix.
- DO NOT include any `TODO`, `FIXME`, "implement this", "add cache here", or any comment that names the fix.
- DO NOT add comments that explain the architectural problem or its solution.
- DO NOT name new files/classes/methods after the fix the candidate is expected to deliver.
- Generated project must be runnable end-to-end (`composer install`, then the documented run command for the stack, plus `vendor/bin/phpunit`). The defect must reproduce.

## .gitignore INSTRUCTIONS
Create a comprehensive PHP `.gitignore` covering: `/vendor/`, `/.phpunit.result.cache`, `/.phpunit.cache/`, `.env`, `.env.local`, `*.log`, `/storage/logs/*` and `/bootstrap/cache/*` (Laravel only), `/var/cache/*` and `/var/log/*` (Symfony only), IDE directories (`.idea/`, `.vscode/`, `*.swp`), and OS files (`.DS_Store`, `Thumbs.db`).

## README.md INSTRUCTIONS
- The README.md must contain (in this order): Task Overview, Objectives, How to Verify, Helpful Tips
- All sections must have substantial content — no empty or placeholder text
- Content must be directly relevant to the chosen scenario
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates which class to extract, which interface to introduce, or which method to call — describe the symptom, the desired behaviour, and let them discover the seam.

### Task Overview

**CRITICAL**: 3-4 substantial sentences describing the business scenario, the current state of the code, and why the architectural / performance / correctness change matters. Always provide concrete business context.

### Objectives
  - Clear, observable goals appropriate for INTERMEDIATE level (specific latency targets, specific HTTP responses on error paths, specific query count, specific tests that must pass)
  - Frame around symptoms from "Current Implementation" and the success criteria from the scenario — not around design patterns
  - Should guide candidates to think about: layering, performance, correctness, testability, error surface
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Concrete commands the candidate can run: `curl` examples for the success path AND for each error path, `vendor/bin/phpunit` (or framework-equivalent) with the specific test class
  - The expected HTTP status codes, JSON shapes, and DB / cache state after the fix
  - Performance verification (e.g. "the second call to the same endpoint should return in under X ms" or "the export should not exceed Y MB peak memory")
  - **CRITICAL**: Describe what to verify and the expected behaviour, NOT the specific functions or classes the candidate should call.

### Helpful Tips
Practical guidance without revealing implementations:
  - Suggest reading the request entry point first to see how dependencies are constructed and reused
  - Mention thinking about which classes today know about which libraries (the HTTP client, the framework's cache, the ORM) and whether that coupling is helping or hurting
  - Hint at considering what stops two endpoints sharing the same logic today, and what a single seam between them would look like
  - Recommend exploring how the same query can be expressed in one round trip instead of one per item, and what indexing would support it
  - Suggest thinking about what a caller of this code should see when an upstream dependency fails, vs. what they see today
  - Point toward considering how to write a test that pins the new behaviour without depending on the upstream dependency
  - Use action-style bullets starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Tips guide toward architectural thinking — they do NOT name patterns, classes, or methods to introduce.

### NOT TO INCLUDE in README
  - Setup commands beyond `composer install` and the documented run command for the stack
  - Direct architectural prescriptions ("use the Repository pattern", "wrap this in a Decorator", "use Laravel's `Cache::remember`")
  - Step-by-step implementation guides
  - Specific class / method / interface names to introduce
  - Code snippets that reveal the fix
  - Phrases like "you should implement", "make sure to add a method called X", "create a class called Y"

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no surrounding code fences.
2. **name** must be short, descriptive, kebab-case (e.g., "shipments-export-streaming-refactor")
3. **"title"** must be in `<action verb> <subject>` format, 50-80 characters, and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
4. **code_files** must include README.md, .gitignore, composer.json, phpunit.xml, and the PHP source files needed to reproduce the defect from the scenario.
5. **README.md** must follow the structure above.
6. **Starter code** must run via `composer install` + the documented run command, must compile/run cleanly, and must reproduce the architectural / performance / correctness defect described in the scenario — verify before finalising.
7. **Strict types**: every PHP source file must begin with `<?php` followed by `declare(strict_types=1);`
8. **No solution-revealing comments**, no TODO/FIXME, no class/method/variable names that pre-name the fix.
9. **Time-box discipline**: the checklist of required changes must be doable in {minutes_range} minutes by a 3-5 yoe PHP developer with AI assistance. If in doubt, cut a checklist item — over-scoped tasks are the single most common defect at INTERMEDIATE level.
10. **Stack alignment**: if the scenario names a framework (Laravel, Symfony, Slim), the starter MUST use that framework's idioms — do NOT silently swap stacks.
11. **Domain consistency**: route paths, table names, error codes, latency numbers, currency / unit references in the README, starter code, and tests must all match the chosen scenario.
12. **One focused architectural change** per task — extract ONE service, introduce ONE interface, fix ONE N+1, add ONE cache, map ONE domain exception. Do not bundle multiple unrelated refactors into a single task.
13. **outcomes** and **short_overview** must NOT reveal the specific fix; **answer** and **hints** carry the higher-fidelity guidance.
"""

PROMPT_REGISTRY = {
    "PHP (INTERMEDIATE)": [
        PROMPT_PHP_INTERMEDIATE_CONTEXT,
        PROMPT_PHP_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PHP_INTERMEDIATE,
    ]
}
