PROMPT_PHP_LARAVEL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PHP_LARAVEL_BASIC_INPUT_AND_ASK = """
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

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Laravel implementation or fix required, the expected deliverables, and how it aligns with BASIC PHP - Laravel proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PHP_LARAVEL_BASIC = """
## GOAL
As a senior Laravel backend architect with deep experience in PHP 8.x, Laravel 10+/11+, Eloquent ORM, Form Requests, PSR standards, Composer, and production Laravel deployment, you are given a list of real-world scenarios and proficiency levels for PHP - Laravel development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc., that can be effectively used to assess a 1-2 yoe Laravel candidate's ability to read existing Laravel code, fix logical or design bugs, and implement small backend features end-to-end.

**THE FRAMEWORK IS ALWAYS LARAVEL.** Every task must be implemented using Laravel idioms: Eloquent models, Form Requests, resource routes, artisan commands, service providers, facades, and Laravel's testing helpers. Do NOT fall back to vanilla PHP or raw PDO. Starter code must follow Laravel's standard directory layout (app/Http/Controllers, app/Models, app/Http/Requests, database/migrations, routes/api.php or routes/web.php, tests/Feature).

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to fix a logical bug in existing Laravel code OR implement a small backend feature on top of provided starter code (a controller method, a Form Request rule, a migration, a service method, a simple Eloquent query fix, an Artisan command, etc.).
- The question scenario must be clear, with realistic facts, figures, company names, table/column names, route paths, and HTTP status codes that are consistent with the chosen domain.
- Generate enough starter code that the candidate has a real Laravel project to read into, not a blank slate. Provide only the files actually relevant to the task (the controller, the model, the Form Request, the migration, the route file, the test) — NOT a full `laravel new` skeleton. The README must state that the candidate runs this inside an existing Laravel app.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The wrong/buggy/incomplete behavior described in the scenario MUST actually be present in the starter implementation.
- A part of the task completion is to watch the candidate apply best practices: Form Request validation, Eloquent relationships, `declare(strict_types=1)`, correct HTTP status codes, proper exception handling, PHPUnit/Pest tests — not just patching the surface bug.
- The question should be a real-world product scenario (HR app, e-commerce checkout, healthcare portal, logistics export, billing dashboard, etc.), NOT a syntax puzzle or framework-trivia question.
- The complexity of the task and the specific ask must align with BASIC proficiency level (1-2 years Laravel experience), ensuring no two tasks generated are similar.

### BASIC PROFICIENCY SCOPE (1-2 yoe — what the task may assess)
Tasks MUST stay within BASIC Laravel scope. The task may assess one or more of the following; do NOT push into advanced topics:

- **Routing**: resource routes (`Route::apiResource`, `Route::resource`), middleware groups (`auth`, `throttle`), named routes
- **Controllers**: resource controller methods (index, show, store, update, destroy), returning `response()->json()` with correct HTTP status codes, injecting a service via constructor
- **Form Requests**: `authorize()` returning true/false, `rules()` with common rules (`required`, `string`, `max`, `email`, `exists`, `numeric`, `min`, `date`), accessing `$request->validated()`
- **Eloquent**: `create()`, `find()`, `findOrFail()`, `update()`, `delete()`, `where()`, `orderBy()`, `paginate()`, basic `hasMany`/`belongsTo`/`hasOne` relationships, `with()` for eager loading to avoid an obvious N+1
- **Migrations**: `Schema::create`, adding columns (`$table->string`, `$table->foreignId`, `$table->timestamps`, `nullable()`, `unique()`), `php artisan migrate`
- **Factories and seeders**: `User::factory()->create()`, `Model::factory()->count(n)->create()`, database seeders for deterministic test data
- **Testing**: PHPUnit/Pest feature tests using `$this->get()`, `$this->post()`, `actingAs()`, `assertStatus()`, `assertJson()`, `assertDatabaseHas()`, `assertDatabaseMissing()`, `RefreshDatabase`, `Mail::fake()`, `Queue::fake()`, `Storage::fake()`
- **Auth middleware**: protecting routes, using `Auth::user()` / `auth()->id()` in controllers, returning `403` for unauthorized access
- **Error handling**: `abort(404)`, `findOrFail()`, `abort_if()`, returning consistent JSON error shapes
- **Simple Artisan commands**: `make:*` Artisan commands, running `php artisan migrate`, basic custom command with `$signature` and `handle()`

- **Scope boundary**: Tasks MUST NOT ask the candidate to fix or modify migrations, alter DB schemas, or write seeders. The starter migration is always correct and complete. All DB interaction in tests uses Laravel's default in-memory SQLite via `RefreshDatabase` — no MySQL or Docker setup needed.

Do NOT require: complex design patterns (Observer chains, Strategy, Decorator), event sourcing, message queues (beyond basic dispatch), custom DI container bindings, advanced Eloquent polymorphic relationships, or Horizon/Telescope. Those are INTERMEDIATE+ topics.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts inside the question and README:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy / unsafe / incomplete state that the starter code implements. Include concrete details from the scenario (table names, route paths, HTTP codes, Eloquent method calls, validation rule gaps, missing eager loading).
- Examples: "`AppointmentController::show()` calls `$patient->appointments` in a loop without eager loading, causing N+1 queries and returning null doctor names"; "`ProductRequest::authorize()` returns `false`, silently bypassing all validation rules — any POST to `/api/products` succeeds without checking required fields".
- The **starter code MUST perfectly implement this current behaviour** — the bug must reproduce, the missing validation must really be missing. Do NOT pre-fix anything.

**Required Changes (the candidate's deliverable):**
- A small, concrete checklist of behaviour changes (add eager loading, fix authorize(), add Form Request rules, return correct status codes, add 1-2 feature tests, etc.).
- Each item must be observable: a different HTTP status, a different DB write, a passing test — not a vague "improve the code".

**Out of scope for this prompt**: Any task that requires modifying a migration, fixing a column type, adding/removing indexes, writing a seeder, or configuring an external database. Those belong in a separate infrastructure-focused prompt. Keep the fix entirely in PHP: controllers, Form Requests, service classes, middleware, Eloquent query logic, HTTP response codes.

### AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including Google, Stack Overflow, official Laravel docs, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to read an unfamiliar Laravel codebase, identify the real defect, and apply the right Laravel idiom — not rote memorisation of syntax.

### Code Generation Instructions
Based on the chosen real-world scenario, create a PHP - Laravel task that:
- Uses the business domain from the chosen scenario as the source of truth
- Matches BASIC proficiency level (1-2 years Laravel experience), keeping in mind that AI assistance is allowed
- Tests practical Laravel skills: reading existing code, fixing logical bugs, writing Form Requests, using Eloquent relationships correctly, returning proper JSON responses
- Time constraints: the task should be finishable within {minutes_range} minutes
- Picks a different real-world scenario each generation to ensure variety
- Focuses on a single small module (one controller / one Form Request / one Artisan command / one migration) — NOT a multi-service architecture
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "appointment-eager-loading-fix", "product-form-request-authorize-fix", "payroll-sync-command-chunking")
- **CRITICAL - FILE NAMING**: All additional controller, Form Request, service, model, migration, and test files MUST use meaningful, scenario-specific file names derived from the task (e.g., `AppointmentController.php`, `ShowPatientRequest.php`, `PayrollSyncCommand.php`, `CreateAppointmentsTable.php`). NEVER use generic placeholder names like `ControllerA.php`, `MyRequest.php`, or `Helper.php`. File and class names should reflect the business domain and feature.

### Starter Code Instructions
- Provide only the files actually relevant to the task — the controller, the relevant model(s), the Form Request (if applicable), the migration, the route file snippet, and the feature test — NOT a full `laravel new` skeleton.
- The README must state: "This task assumes a fresh Laravel 10+/11+ installation. Copy these files into the appropriate directories and run the setup commands below."
- The starter migration must be correct and complete — the bug lives in PHP code, not the schema.
- Do NOT include a seeder. Tests use `RefreshDatabase` with in-memory SQLite; any required rows are created inside the test using factories or `DB::table`.
- Include a `composer.json` only if the task requires a non-standard package; otherwise omit it and note that the standard Laravel composer.json is assumed.
- The buggy/incomplete behaviour from the scenario MUST actually be present in the starter — verify by re-reading the starter code against the scenario's "Current Implementation" before finalising.
- Keep starter code MINIMAL — enough to demonstrate the bug, not enough to obscure the actual task.
- DO NOT include `// TODO`, `// FIXME`, "implement this", or any comment that names the fix or hints at the solution.
- DO NOT include comments explaining what the buggy code is doing wrong — let the candidate find it.
- Use `declare(strict_types=1);` at the top of every PHP source file in the starter.

### REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Eager Loading in Healthcare Appointment Controller', 'Repair Form Request Authorization in Product API', 'Refactor Payroll Sync Command with Chunked Iteration'. The title should clearly convey the action (fix, repair, implement, build, refactor, validate, harden) and the subject. This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — current implementation, what is broken or missing, and the concrete changes the candidate must make. Use the two-part Current Implementation / Your Task / Success Criteria framing from the scenario.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "PHP, Composer, Laravel, and IDE exclusions (vendor/, .env, .phpunit.result.cache, storage/logs/*, bootstrap/cache/*, .idea/, .vscode/)",
    "app/Http/Controllers/RelevantController.php": "Controller with the bug present — resource method, route model binding, JSON response",
    "app/Models/RelevantModel.php": "Eloquent model with fillable, casts, relationships",
    "app/Http/Requests/RelevantRequest.php": "Form Request with the defect (wrong authorize(), missing rules) — if applicable to the task",
    "database/migrations/yyyy_mm_dd_create_relevant_table.php": "Migration creating the table the task depends on",
    "routes/api.php": "Route definitions for the task endpoints",
    "tests/Feature/RelevantTest.php": "At least one baseline PHPUnit/Pest feature test"
  }},
  "outcomes": "Bullet-point list in simple language. Must include the observable results after completion (correct HTTP status codes, correct DB writes, passing tests, no fatal errors on malformed input) and alignment with BASIC Laravel proficiency.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific Laravel implementation or fix goal, (3) the expected outcome emphasising correctness, input safety, and clean Laravel code.",
  "pre_requisites": "Bullet-point list of tools and knowledge required. Include: PHP 8.1+, Composer 2.x, a fresh Laravel installation, an IDE or text editor, Git, basic PHP/Eloquent knowledge, basic PHPUnit knowledge.",
  "answer": "High-level solution approach describing the main components and flow — which Form Request rule to add, which Eloquent method to fix, how to map exceptions to status codes, which tests to add. Do NOT paste full code.",
  "hints": "Single line suggesting the focus area without naming the fix. Example: 'Look at how the Form Request decides whether the request is authorised and what happens to the validation rules when it is not'",
  "definitions": {{
    "Form Request": "A Laravel class that encapsulates HTTP request validation and authorization, keeping validation logic out of the controller",
    "Eloquent eager loading": "Loading related models in a single additional query using with() to prevent N+1 query problems",
    "Route model binding": "Laravel's convention for automatically injecting an Eloquent model into a controller method based on a route parameter",
    "RefreshDatabase": "A PHPUnit trait that resets the database between each test using migrations, ensuring test isolation",
    "findOrFail()": "An Eloquent method that retrieves a model by primary key and throws ModelNotFoundException (mapped to HTTP 404) if not found"
  }}
}}

## Code file requirements
- Provide only the files the task actually needs — controller, model(s), Form Request, migration, routes, test. Do NOT generate a full Laravel skeleton.
- Code must follow modern PHP 8.x best practices: `declare(strict_types=1)`, typed parameters and return types, constructor property promotion where natural, PSR-12 formatting.
- Use proper Laravel namespaces: `App\\Http\\Controllers`, `App\\Models`, `App\\Http\\Requests`, `Database\\Migrations`, etc.
- **CRITICAL**: starter code MUST contain the bug or missing behaviour described in the scenario, but MUST NOT contain the fix.
- DO NOT include any `TODO`, `FIXME`, "implement here", "add validation here", or solution-revealing comment.
- DO NOT name variables or methods in a way that gives away the answer.
- The starter code must be syntactically valid PHP and runnable after `composer install` and `php artisan migrate` (or `php artisan test` for test-driven scenarios). The buggy behaviour must reproduce on this run.

## .gitignore INSTRUCTIONS
Create a comprehensive PHP + Laravel `.gitignore` covering: `/vendor/`, `/.phpunit.result.cache`, `/.phpunit.cache/`, `.env`, `.env.local`, `*.log`, `/storage/logs/*`, `/bootstrap/cache/*`, IDE directories (`.idea/`, `.vscode/`, `*.swp`), and OS files (`.DS_Store`, `Thumbs.db`).

## README.md STRUCTURE (PHP - Laravel)

### Task Overview (MANDATORY — 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the code. State concretely what is broken or missing. Use real business context from the chosen scenario; never leave empty or generic text. Do NOT directly tell candidates which functions to add or which patterns to apply — describe the symptom and the desired observable behaviour.

Note at the top: "This task assumes a fresh Laravel 10+/11+ installation. Copy files to the directories shown, run the setup commands, and then attempt the objectives."

### Objectives

Define goals focusing on outcomes for a BASIC-level Laravel task:
  - Clear, observable goals the candidate should achieve (correct status codes, correct DB rows, no fatal errors on malformed input, passing tests)
  - Frame around the symptom from the scenario's "Current Implementation" and the desired behaviour from "Success Criteria"
  - Focus on fundamental Laravel concepts: Form Request validation, Eloquent relationships, correct HTTP responses, exception handling
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify

Verification approaches the candidate can run themselves:
  - Setup: `composer install`, `cp .env.example .env`, `php artisan key:generate`, `php artisan migrate`. The default `.env.example` uses SQLite — no database configuration needed.
  - Concrete `curl` examples (or `php artisan test`) that exercise the success path AND the failure paths the bug currently mishandles
  - The specific HTTP status code, response body, and DB state to expect after the fix
  - The PHPUnit/Pest command (`php artisan test` or `./vendor/bin/pest`) and which tests should pass
  - **CRITICAL**: Describe what behaviours to verify, not which specific Laravel methods to call

### Helpful Tips

Practical guidance without revealing implementations:
  - Suggest reading the Form Request class first to understand how authorization and validation interact before the controller runs
  - Mention thinking about which layer should validate input vs. which layer should query the database
  - Hint at considering how Eloquent loads related models by default and what that means for a controller that loops over a collection
  - Recommend exploring what happens when a required model cannot be found and what HTTP response a real API should return
  - Suggest thinking about how the response body and status code should look for both success and failure paths
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions or method names

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Phrases like "you should call `with()`", "add a `rules()` method", "use `actingAs()`"
- Specific class/method names that reveal the solution structure
- Setup commands beyond `composer install`, `php artisan migrate`, and `php artisan test`

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no surrounding code fences. Emit the raw JSON object.
2. **name** must be short, descriptive, kebab-case (e.g., "appointment-eager-loading-fix")
3. **"title"** must be in `<action verb> <subject>` format, 50-80 characters, and different from `"name"`
4. **code_files** must include README.md, .gitignore, the controller, model(s), Form Request (if applicable), migration, route file, and at least one test file.
5. **README.md** must follow the structure above — Task Overview, Objectives, How to Verify, Helpful Tips (in this order)
6. **Starter code** must be valid PHP 8.x, use Laravel conventions, and reproduce the bug described in the scenario.
7. **Strict types**: every PHP source file in the starter must begin with `<?php` followed by `declare(strict_types=1);`
8. **No solution-revealing comments**, no TODO/FIXME, no method/variable names that give away the fix.
9. **outcomes**, **short_overview**, **pre_requisites** must be bullet-point lists in simple language.
10. **hints** must be a single line; **definitions** must include relevant Laravel terms (Form Request, eager loading, route model binding, RefreshDatabase, findOrFail).
11. **Task must be completable within {minutes_range} minutes** for BASIC proficiency (1-2 years).
12. **Do NOT generate a full `laravel new` skeleton** — provide only the files the task actually requires.
13. **Domain consistency**: route paths, table names, error codes, and field names in the README, starter code, and tests must all match the chosen scenario.
14. **No schema bugs**: The starter migration must be correct. The bug lives in PHP code only (controller, Form Request, service, middleware). Never ask candidates to fix a migration or write a seeder.
"""

PROMPT_REGISTRY = {
    "PHP - Laravel (BASIC)": [
        PROMPT_PHP_LARAVEL_BASIC_CONTEXT,
        PROMPT_PHP_LARAVEL_BASIC_INPUT_AND_ASK,
        PROMPT_PHP_LARAVEL_BASIC,
    ]
}
