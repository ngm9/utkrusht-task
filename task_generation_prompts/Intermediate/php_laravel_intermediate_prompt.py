PROMPT_PHP_LARAVEL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PHP_LARAVEL_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a PHP - Laravel assessment task.

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
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and the architectural / performance / correctness problem the candidate will be solving)
2. What will the task look like? (Describe the type of Laravel refactor, feature, or bug-fix required, the expected deliverables, and how it aligns with INTERMEDIATE PHP - Laravel proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PHP_LARAVEL_INTERMEDIATE = """
## GOAL
As a senior Laravel architect with deep experience in PHP 8.x, Laravel 10+/11+, Eloquent ORM, service containers, queuing, caching, testing (PHPUnit/Pest), and PSR standards, you are given a list of real-world scenarios and proficiency levels for PHP - Laravel development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc., that can be effectively used to assess a 3-5 yoe Laravel candidate's ability to read a non-trivial codebase, identify the architectural / performance / correctness problem, and deliver a focused, well-structured fix or feature end-to-end.

**THE FRAMEWORK IS ALWAYS LARAVEL.** Every task must be implemented using Laravel idioms: Eloquent with eager loading and relationships, service container bindings, service providers, middleware, events/listeners, queued jobs, Cache facade, Gates/Policies, API Resources, repository interfaces. Do NOT fall back to vanilla PHP or raw PDO. Starter code must follow Laravel's standard directory layout. Provide only the files actually relevant to the task (controller, service, repository, event, job, resource, policy, migration, test) — NOT a full `laravel new` skeleton.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to refactor existing code, fix a complex/architectural bug, or implement a focused feature on top of provided starter code (extract a service, introduce a repository interface, fix N+1, add a cache layer, map domain exceptions, implement a queued job, add a Policy, etc.).
- The question scenario must be clear, with realistic facts, figures, company names, table/column names, route paths, query counts, latency numbers, and HTTP status codes that are consistent with the chosen domain.
- Generate enough starter code that the candidate has a realistic Laravel project to read into. The starter must be valid Laravel 10+/11+ code.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The wrong/inefficient/missing behaviour described in the scenario MUST actually be present in the starter implementation — verify by re-reading before finalising.
- A part of the task completion is to watch the candidate make the right architectural decisions (where to draw the seam between layers, which interface to introduce, how to scope a cache key, where to place domain exception mapping, how to structure the queued job) — not just patch the surface defect.
- The complexity of the task must align with INTERMEDIATE proficiency level (3-5 years Laravel experience), ensuring no two tasks generated are similar.
- The task MUST stay TIME-BOXED to {minutes_range} minutes. Pick ONE focused architectural change plus 1-2 supporting tests.

### INTERMEDIATE PROFICIENCY SCOPE (3-5 yoe — what the task may assess)
Tasks should test deeper Laravel and architectural understanding. The task may assess one or more of:

- **N+1 query resolution**: identifying and fixing eager loading gaps with `with()`, `load()`, `withCount()`, choosing between `select()` + `with()` and a single joined query
- **Service layer extraction**: moving business logic from a fat controller into a dedicated service class, injecting it via the container
- **Repository pattern**: introducing a repository interface, binding it in a service provider, injecting via constructor
- **Service container & providers**: binding interfaces to implementations (`bind`, `singleton`), contextual binding, deferred providers
- **Caching with Cache facade**: `Cache::remember()` with deterministic keys (user ID + endpoint), TTL strategy, `Cache::forget()` / tag-based invalidation, Cache::lock() for stampede protection
- **Exception design & HTTP mapping**: custom domain exceptions, mapping in the exception Handler, stable JSON error shapes (no Eloquent/Guzzle internals leaking)
- **Queued jobs**: writing `ShouldQueue` jobs with `handle()`, `failed()`, retry policies (`tries`, `backoff`), dispatching via `dispatch()` / `dispatchAfterResponse()`
- **Events & listeners**: event/listener pair, `EventServiceProvider` registration, queued listeners
- **Policies & Gates**: defining resource policies, `$this->authorize()`, returning `403 {{"code": ..., "message": ...}}` without leaking internals
- **API Resources**: `JsonResource` with `whenLoaded()`, `when()`, conditional relationships; resource collections
- **Artisan commands**: `$signature` with arguments/options, `chunk()`/`cursor()` for large datasets, `--dry-run` flag, progress bars
- **Testing at depth**: mocking services/repositories via `app()->instance()`, `Http::fake()`, `Queue::assertPushed()`, `Mail::assertSent()`, `Event::assertDispatched()`, factory states

- **Scope boundary**: Tasks MUST NOT ask the candidate to fix or modify migrations, alter DB schemas, or write seeders. The starter migration is always correct and complete. All DB interaction in tests uses Laravel's default in-memory SQLite via `RefreshDatabase` — no MySQL or Docker setup needed.

Do NOT require: CQRS, event sourcing, building a custom DI container, hexagonal architecture across multiple bounded contexts, or full-blown distributed system patterns.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts inside the question and README:

**Current Implementation (what we give to the candidate):**
- Describe precisely the architectural / performance / correctness problem, with concrete numbers (query counts, route paths, observed latency, error messages, HTTP codes the client currently sees).
- Examples: "`OrderController::index()` returns an `OrderResource` collection but calls `$order->customer`, `$order->items`, and `$order->shipment` inside the resource — on a 50-order page this generates 151 DB queries"; "`BookingController::store()` is 120 lines containing inline Guzzle calls to a seat-check service, pricing logic, payment processing, and email dispatch — a payment failure currently surfaces as a 500 with a raw Guzzle exception".
- The **starter code MUST perfectly implement this current behaviour** — the N+1 must really happen, the fat controller must really exist, the exception must really leak. Do NOT pre-fix anything.

**Required Changes (the candidate's deliverable):**
- A short, concrete checklist (3-5 items) of behaviour changes: which class to extract, which interface to introduce, which query to rewrite, which cache layer to add, which exception to map.
- Each item must be observable — a different DB query count, a different HTTP status, a different latency, a passing test. Vague "improve the architecture" items are a defect.
- Keep the checklist TIGHT — 3 to 5 items max. Time-box discipline is the single most common failure mode for INTERMEDIATE tasks.

**Out of scope for this prompt**: Any task requiring migration changes, schema fixes, seeder creation, or external DB setup. The fix lives entirely in PHP: controllers, service classes, Form Requests, middleware, jobs, events, Eloquent relationships, HTTP responses.

### AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources, including Google, Stack Overflow, official Laravel/PHP docs, and AI-powered tools or LLMs.
- The tasks are designed to assess judgment: which eager loading relationship to add, which seam to introduce, where to put the cache. Complexity should reflect INTERMEDIATE Laravel proficiency while requiring genuine engineering decisions.

### Code Generation Instructions
Based on the chosen real-world scenario, create a PHP - Laravel task that:
- Uses the business domain from the chosen scenario as the source of truth
- Matches INTERMEDIATE proficiency level (3-5 years Laravel experience), keeping in mind that AI assistance is allowed
- Tests practical Laravel architecture skills: refactoring for testability, eliminating N+1, introducing a focused abstraction, mapping domain exceptions to HTTP, writing meaningful tests
- Time constraints: the task should be finishable within {minutes_range} minutes — re-check this against the checklist of required changes
- Picks a different real-world scenario each generation to ensure variety
- Focuses on ONE service or endpoint at a time — NOT a cross-cutting refactor over many endpoints
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "order-resource-n1-fix", "booking-service-extraction", "portfolio-cache-layer")
- **CRITICAL - FILE NAMING**: All additional controller, service, repository, adapter, middleware, exception, job, event, listener, resource, and policy files MUST use meaningful, scenario-specific file names (e.g., `OrderRepository.php`, `BookingService.php`, `SeatUnavailableException.php`, `SendBookingConfirmation.php`, `PortfolioPolicy.php`). NEVER use generic placeholder names.

### Starter Code Instructions
- Provide only the files relevant to the task — controller, service (if one already exists), model(s), migration(s), route snippet, and one test file. Do NOT generate a full `laravel new` skeleton.
- The README must include a note: "This task assumes a fresh Laravel 10+/11+ installation. Copy these files to the appropriate directories and run the setup commands below."
- The architectural / performance / correctness defect from the scenario MUST actually be present in the starter — verify before finalising.
- **The starter migration must be correct and complete — the bug is in PHP code, not the schema.** Do not introduce any intentional schema defects.
- **Do NOT include a seeder.** Tests use `RefreshDatabase` with in-memory SQLite; all required rows are created inside the test files using model factories or `Model::create()`.
- **Do NOT include `docker-compose.yml`, `run.sh`, or `kill.sh`.** No Docker or external MySQL setup should be required.
- **README setup commands must be**: `composer install`, `cp .env.example .env`, `php artisan key:generate`, `php artisan migrate`, `php artisan test`. No seed step, no Docker step.
- Provide partial implementations that the candidate must complete or refactor — NOT a blank skeleton.
- Include at least one existing class/interface that the candidate either reuses, extends, or refactors against. This signals the architectural seam.
- Use `declare(strict_types=1);` at the top of every PHP source file. Use modern PHP 8.x features (constructor property promotion, readonly, enums, match) where natural to Laravel.
- DO NOT include `// TODO`, `// FIXME`, "implement this here", "add cache here", or any solution-revealing comment.
- DO NOT name variables, methods, or classes in a way that gives away the answer (e.g. `$cachedRepo`, `withEagerLoading()`, `extractedService()` when those are exactly what the candidate is supposed to introduce).

### REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Resolve N+1 Queries in Order Resource Collection', 'Extract Booking Service with Domain Exception Mapping', 'Add Cache Layer to Portfolio Summary Endpoint'. The title should clearly convey the action (implement, fix, build, refactor, extract, optimize, harden) and the subject. This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — current implementation, what is wrong (architecturally / performance-wise / correctness-wise), and the focused changes required. Use the two-part Current Implementation / Your Task / Success Criteria framing.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Objectives, How to Verify, Helpful Tips",
    ".gitignore": "Comprehensive PHP, Composer, Laravel, and IDE exclusions",
    "app/Http/Controllers/RelevantController.php": "Existing controller with the architectural / performance / correctness defect present",
    "app/Services/RelevantService.php": "Supporting service the candidate will refactor against (if the scenario involves service extraction)",
    "app/Models/RelevantModel.php": "Eloquent model with relationships relevant to the task",
    "app/Exceptions/RelevantException.php": "Existing domain exception classes if relevant — leave the missing ones to the candidate",
    "database/migrations/yyyy_mm_dd_create_relevant_table.php": "Migration for the tables the task depends on — must be correct and complete; the bug is never in the schema",
    "routes/api.php": "Route definitions for the task endpoints",
    "tests/Feature/RelevantTest.php": "Baseline PHPUnit/Pest feature test (passing or strategically failing) that the candidate's change must keep green / make green — uses RefreshDatabase with in-memory SQLite; rows are created inside the test, not via a seeder"
  }},
  NOTE — the following file types MUST NOT appear in code_files: docker-compose.yml, run.sh, kill.sh, database/seeders/*.php. Do not generate them.
  "outcomes": "Bullet-point list. Must include observable post-fix outcomes (specific query count, specific latency target, specific HTTP status / JSON shape on error paths, specific tests that must pass) and architectural quality outcomes (single seam introduced, interface bound in service provider, exception mapped in Handler).",
  "short_overview": "Bullet-point list describing: (1) the high-level business or technical problem, (2) the specific architectural / performance / correctness change required, (3) the expected outcome emphasising correctness, performance, and maintainability — without revealing the answer.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include PHP 8.1+, Composer 2.x, a fresh Laravel 10+/11+ installation, an IDE, Git, intermediate-level Laravel knowledge (Eloquent relationships, service container, PHPUnit/Pest), and any specific package if named in the scenario.",
  "answer": "High-level solution approach with emphasis on the architectural decision: which seam to introduce, which query to rewrite, where to place the cache and how to key it, which exception to add and where to map it. Do NOT paste full code.",
  "hints": "A single line guiding toward the architectural approach without naming the pattern. Example: 'Look at where the Eloquent relationships are resolved inside the resource and ask which queries that triggers per item in the collection — and what a single additional database call before the loop would look like'.",
  "definitions": {{
    "Eager loading": "Loading Eloquent relationships in a fixed number of additional queries (using with() or load()) to prevent the N+1 problem",
    "Service container binding": "Registering an interface-to-implementation mapping in a Laravel service provider so the container injects the right concrete class on resolution",
    "Repository pattern": "An abstraction over Eloquent data access behind an interface, letting the application layer depend on a contract rather than a concrete query implementation",
    "Cache-aside": "A caching strategy where the application reads from cache first, falls back to the source on a miss (Cache::remember), and writes the result back to the cache",
    "Domain exception": "A custom exception class representing a meaningful business condition (e.g. SeatUnavailableException, PaymentFailedException) that callers can catch and map to a stable HTTP response",
    "API Resource": "A Laravel JsonResource class that transforms an Eloquent model into a JSON-serialisable array, decoupling the model shape from the API contract",
    "PHPUnit / Pest": "The standard PHP testing frameworks used in Laravel for unit and feature tests"
  }}
}}

## Code file requirements
- Generate a realistic Laravel project structure for the task: `app/Http/Controllers`, `app/Services`, `app/Repositories`, `app/Models`, `app/Exceptions`, `routes/api.php`, `tests/Feature` or `tests/Unit`.
- Code must follow modern PHP 8.x best practices and demonstrate intermediate-level patterns: constructor property promotion, readonly value objects where appropriate, type-safe interfaces, PSR-12 formatting, Laravel coding conventions.
- Use appropriate, NAMED design seams — but DO NOT name them in a way that gives the solution away (e.g. don't preemptively create `CachedPortfolioRepository` if the candidate is supposed to introduce caching).
- **CRITICAL**: starter code MUST contain the architectural / performance / correctness defect described in the scenario, but MUST NOT contain the fix.
- Include some existing classes/interfaces that the candidate either reuses, refactors against, or extends — this signals the seam without dictating the fix.
- DO NOT include any `TODO`, `FIXME`, "implement this", "add cache here", or any comment that names the fix.
- DO NOT add comments that explain the architectural problem or its solution.
- DO NOT name new files/classes/methods after the fix the candidate is expected to deliver.
- Generated code must be valid PHP 8.x that would run after `composer install` and `php artisan migrate`. The defect must reproduce.

## .gitignore INSTRUCTIONS
Create a comprehensive PHP + Laravel `.gitignore` covering: `/vendor/`, `/.phpunit.result.cache`, `/.phpunit.cache/`, `.env`, `.env.local`, `*.log`, `/storage/logs/*`, `/bootstrap/cache/*`, IDE directories (`.idea/`, `.vscode/`, `*.swp`), and OS files (`.DS_Store`, `Thumbs.db`).

## README.md INSTRUCTIONS
- The README.md must contain (in this order): Task Overview, Objectives, How to Verify, Helpful Tips
- All sections must have substantial content — no empty or placeholder text
- Content must be directly relevant to the chosen scenario
- Use concrete business context, not generic descriptions
- Include at top: "This task assumes a fresh Laravel 10+/11+ installation. Copy files to the directories shown and run the setup commands below."
- **IMPORTANT**: Do NOT directly tell candidates which class to extract, which interface to introduce, which method to call, or which cache key to use — describe the symptom, the desired behaviour, and let them discover the seam.

### Task Overview
**CRITICAL**: 3-4 substantial sentences describing the business scenario, the current state of the code, and why the architectural / performance / correctness change matters. Always provide concrete business context (query counts, latency numbers, error shapes observed by clients).

### Objectives
  - Clear, observable goals appropriate for INTERMEDIATE level (specific query count target, specific HTTP responses on error paths, specific tests that must pass)
  - Frame around symptoms from "Current Implementation" and the success criteria from the scenario — not around design patterns
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Setup commands: `composer install`, `cp .env.example .env`, `php artisan key:generate`, `php artisan migrate`, `php artisan test` (no seed step — tests create their own data via factories or `Model::create()`)
  - Concrete `curl` commands or `php artisan test` invocations for success AND error paths
  - Expected HTTP status codes, JSON shapes, and DB / cache state after the fix
  - Performance verification where applicable (e.g. "DB::getQueryLog() should show N queries, not N+50")
  - **CRITICAL**: Describe what to verify and the expected behaviour, NOT the specific functions or classes to call.

### Helpful Tips
Practical guidance without revealing implementations:
  - Suggest reading the controller first to count how many queries the current code triggers per request
  - Mention thinking about which classes today know about which libraries (Guzzle, Cache, ORM) and whether that coupling is helping or hurting
  - Hint at considering what stops two endpoints sharing the same logic today, and what a single seam between them would look like
  - Recommend exploring how the same query result can be reused across requests and what an appropriate key strategy looks like
  - Suggest thinking about what a caller of this code should see when an upstream dependency fails, vs. what they see today
  - Point toward considering how to write a test that pins the new behaviour without depending on the upstream dependency
  - Use action-style bullets starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Tips guide toward architectural thinking — they do NOT name patterns, classes, or methods to introduce.

### NOT TO INCLUDE in README
  - Direct architectural prescriptions ("use the Repository pattern", "use Cache::remember", "extract a BookingService")
  - Step-by-step implementation guides
  - Specific class / method / interface names to introduce
  - Code snippets that reveal the fix
  - Phrases like "you should implement", "make sure to add a method called X", "create a class called Y"

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no surrounding code fences.
2. **name** must be short, descriptive, kebab-case (e.g., "order-resource-n1-fix")
3. **"title"** must be in `<action verb> <subject>` format, 50-80 characters, and different from `"name"`
4. **code_files** must include README.md, .gitignore, the relevant Laravel source files, and a test file.
5. **README.md** must follow the structure above.
6. **Starter code** must be valid PHP 8.x Laravel code that reproduces the architectural / performance / correctness defect — verify before finalising.
7. **Strict types**: every PHP source file must begin with `<?php` followed by `declare(strict_types=1);`
8. **No solution-revealing comments**, no TODO/FIXME, no class/method/variable names that pre-name the fix.
9. **Time-box discipline**: the checklist of required changes must be doable in {minutes_range} minutes by a 3-5 yoe Laravel developer with AI assistance. If in doubt, cut a checklist item.
10. **Do NOT generate a full `laravel new` skeleton** — provide only the files the task actually requires.
11. **Domain consistency**: route paths, table names, error codes, latency numbers in the README, starter code, and tests must all match the chosen scenario.
12. **One focused architectural change** per task — extract ONE service, introduce ONE interface, fix ONE N+1, add ONE cache layer, map ONE domain exception. Do not bundle multiple unrelated refactors.
13. **outcomes** and **short_overview** must NOT reveal the specific fix; **answer** and **hints** carry the higher-fidelity guidance.
14. **No schema bugs**: the starter migration is correct and complete. The bug lives in PHP code only. Never ask candidates to fix a migration or write a seeder. Tests run on Laravel's default in-memory SQLite via `RefreshDatabase` — no MySQL or Docker required.
"""

PROMPT_REGISTRY = {
    "PHP - Laravel (INTERMEDIATE)": [
        PROMPT_PHP_LARAVEL_INTERMEDIATE_CONTEXT,
        PROMPT_PHP_LARAVEL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PHP_LARAVEL_INTERMEDIATE,
    ]
}
