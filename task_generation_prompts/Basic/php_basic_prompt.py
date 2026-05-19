PROMPT_PHP_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PHP_BASIC_INPUT_AND_ASK = """
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
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of PHP implementation or fix required, the expected deliverables, and how it aligns with BASIC PHP proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PHP_BASIC = """
## GOAL
As a senior PHP backend architect with deep experience in modern PHP 8.x, Composer, PSR standards, PDO, and the most common PHP web stacks (vanilla PHP-FPM, Laravel, Symfony, Slim), you are given a list of real world scenarios and proficiency levels for PHP development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc., that can be effectively used to assess a 1-2 yoe candidate's ability to read existing PHP code, fix logical or design bugs, and implement small backend features end-to-end.

**FRAMEWORK / RUNTIME IS DERIVED FROM THE SCENARIO.** If the scenario explicitly names Laravel, Symfony, Slim, CodeIgniter, vanilla PHP, etc., the generated starter code, file layout, and run/test commands MUST match that stack. If the scenario is framework-agnostic, default to a small vanilla-PHP project using Composer + PSR-4 autoloading + PDO + PHPUnit — do NOT introduce a heavy framework where the scenario does not call for one.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to fix a logical bug in existing PHP code OR implement a small backend feature on top of provided starter code (a route handler, a service method, a repository, a validator, an exception mapper, etc.).
- The question scenario must be clear, with realistic facts, figures, company names, table/column names, and HTTP status codes that are consistent with the chosen domain.
- Generate enough starter code that the candidate has a real project to read into, not a blank slate. The starter must run on PHP 8.1+ with Composer installed (`composer install` then a documented run command).
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The wrong/buggy/incomplete behavior described in the scenario MUST actually be present in the starter implementation.
- A part of the task completion is to watch the candidate apply best practices: type declarations, `declare(strict_types=1)`, prepared statements, proper exception handling, JSON response shaping — not just patching the surface bug.
- The question should be a real-world product scenario (HR app, e-commerce checkout, logistics export, billing portal, etc.), NOT a syntax puzzle or framework-trivia question.
- The complexity of the task and the specific ask must align with BASIC proficiency level (1-2 years PHP experience), ensuring no two tasks generated are similar.

### BASIC PROFICIENCY SCOPE (1-2 yoe — what the task may assess)
Tasks MUST stay within BASIC scope. The task may assess one or more of the following; do NOT push into advanced topics:

- **Modern PHP 8.x syntax**: scalar/union/nullable types, constructor property promotion, named arguments, null-safe operator (`?->`), readonly properties, enums (basic usage), `match` expression
- **`declare(strict_types=1)` and type discipline**: explicit parameter and return types on functions/methods
- **Namespaces and PSR-4 autoloading via Composer**: correct `composer.json` `autoload` block, file paths matching namespaces
- **Procedural and simple OOP**: small classes with constructor injection of dependencies (no DI container required), interfaces, value objects/DTOs, simple factories
- **Request handling**: reading `php://input`, `$_GET`/`$_POST`, framework request objects (when scenario uses a framework), returning JSON with correct `Content-Type` and HTTP status codes
- **Validation and input sanitisation**: validating required fields, types, formats (dates, emails, numbers); rejecting invalid input with `400 Bad Request` and a stable JSON error shape
- **PDO basics**: prepared statements with positional or named parameters, `fetch`/`fetchAll`/`fetchColumn`, `lastInsertId()`, transactions (`beginTransaction`/`commit`/`rollBack`) — no ORM internals required
- **Error and exception handling**: throwing and catching `Exception`/`PDOException`/custom exceptions, mapping exceptions to HTTP responses, basic logging via `error_log` or PSR-3 logger if the scenario provides one
- **Composer dependencies**: adding/using a small package (e.g. `vlucas/phpdotenv`, `monolog/monolog`, `ramsey/uuid`) where the scenario calls for it
- **Testing fundamentals**: writing 1–3 focused PHPUnit tests for the new/fixed behaviour

Do NOT require: complex design patterns (Observer, Strategy, Decorator chains), event systems, message queues, multi-process workers, custom DI containers, advanced ORM internals, or framework-internal extensibility. Those are INTERMEDIATE+ topics.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts inside the question and README:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy / unsafe / incomplete state that the starter code implements. Include concrete details from the scenario (table names, route paths, sizes, error messages, HTTP codes).
- Examples: "`POST /api/time-off` reads `php://input`, calls `json_decode(..., true)` and passes the array straight to `TimeOffRepository::create(array $data)` which builds an `INSERT` via string interpolation — missing `employee_id` causes `Undefined array key`, and there is no validation of dates"; "`PriceCalculator::total(array $items)` reads `$_POST['items']` and calls `array_sum(array_column(...))` without checking that prices are numeric, so any malformed item yields `0` silently".
- The **starter code MUST perfectly implement this current behaviour** — the bug must reproduce, the missing validation must really be missing, the SQL must really be vulnerable. Do NOT pre-fix anything.

**Required Changes (the candidate's deliverable):**
- A small, concrete checklist of behaviour changes (validate input, switch to prepared statements, return correct status codes, catch and map exceptions, add 1-2 PHPUnit tests, etc.).
- Each item must be observable: a different HTTP status, a different DB write, a passing test — not a vague "improve the code".

### AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including Google, Stack Overflow, official PHP/Laravel/Symfony docs, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to read an unfamiliar PHP codebase, identify the real defect, and apply the right idiom — not rote memorisation of syntax. Complexity should reflect BASIC PHP proficiency while requiring genuine problem-solving that goes beyond a single AI prompt.

### Code Generation Instructions
Based on the chosen real-world scenario, create a PHP task that:
- Uses the business domain and stack from the chosen scenario as the source of truth
- Matches BASIC proficiency level (1-2 years PHP experience), keeping in mind that AI assistance is allowed
- Tests practical PHP skills: reading existing code, fixing logical bugs, writing safe SQL, validating input, returning proper JSON responses
- Time constraints: the task should be finishable within {minutes_range} minutes
- Picks a different real-world scenario each generation to ensure variety
- Focuses on a single small project (one front controller / one route file / one CLI script) — NOT a multi-service architecture
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "time-off-request-validation-fix", "appointment-csv-import-hardening")
- **CRITICAL - FILE NAMING**: All additional controller, service, repository, exception, DTO, and utility files MUST use meaningful, scenario-specific file names derived from the task (e.g., `AppointmentImportService.php`, `ShipmentRepository.php`, `TimeOffController.php`, `InvalidAppointmentRowException.php`, `DateValidator.php`). NEVER use generic placeholder names like `ServiceA.php`, `RepositoryX.php`, `MyController.php`, `Helper.php`, or `Utils.php` when a scenario-specific name is appropriate. File and class names should reflect the business domain and feature so generated code is identifiable and varies correctly per task.

### Starter Code Instructions
- The starter code must run on PHP 8.1+ with Composer installed. If a framework is implied by the scenario, follow that framework's idiomatic project layout.
- For vanilla PHP scenarios: provide `composer.json` (with PSR-4 autoload + `phpunit/phpunit` in `require-dev`), a `public/index.php` front controller, `src/` with the relevant classes, `tests/` with at least one passing baseline test, and a `.env.example` if config is needed.
- For Laravel scenarios: provide only the files actually relevant to the task (the controller, the service/repository, the route, the migration, the test) — NOT a full `laravel new` skeleton. State at the top of the README that the candidate should run inside an existing Laravel app or use the provided `composer.json` to install the framework.
- For Symfony / Slim scenarios: same — provide only the files the candidate needs to read and edit, plus the relevant config (`services.yaml`, route file, etc.).
- The buggy/incomplete behaviour from the scenario MUST actually be present in the starter — verify by re-reading the starter code against the scenario's "Current Implementation" before finalising.
- Keep starter code MINIMAL — enough to run, not enough to obscure the actual task.
- DO NOT include `// TODO`, `// FIXME`, "implement this", or any comment that names the fix or hints at the solution.
- DO NOT include comments explaining what the buggy code is doing wrong — let the candidate find it.
- Use `declare(strict_types=1);` at the top of every PHP source file in the starter.

### REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Fix Appointment CSV Import in Healthcare Clinic Service', 'Secure Shipment Delivery Update in Logistics Admin Panel', 'Implement Time-Off Request Validation for HR SaaS API'. The title should clearly convey the action (implement, fix, build, refactor, secure, validate, harden) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — current implementation, what is broken or missing, and the concrete changes the candidate must make. Use the two-part Current Implementation / Your Task / Success Criteria framing from the scenario.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive PHP, Composer, and IDE exclusions (vendor/, composer.lock should be tracked or not depending on convention, .phpunit.result.cache, .env, .idea/, .vscode/)",
    "composer.json": "Composer manifest with PSR-4 autoload, php 8.1+ requirement, phpunit/phpunit in require-dev, and any small library the scenario actually needs",
    "phpunit.xml": "PHPUnit configuration (only if tests are part of the task)",
    "public/index.php": "Front controller / entry script (for vanilla PHP scenarios)",
    "src/Path/To/RelevantClass.php": "Service / repository / controller starter code with the bug present",
    "tests/RelevantClassTest.php": "At least one baseline PHPUnit test that already passes (or one failing test that the candidate must make pass, depending on the scenario framing)",
    "additional_file.php": "Other PHP files as the scenario requires"
  }},
  "outcomes": "Bullet-point list in simple language. Must include the observable results after completion (correct HTTP status codes, correct DB writes, passing tests, no fatal errors on malformed input) and alignment with BASIC PHP proficiency.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, (3) the expected outcome emphasising correctness, input safety, and clean code.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include PHP 8.1+, Composer 2.x, an IDE, Git, basic PDO, basic PHPUnit, and (if relevant) the framework named in the scenario.",
  "answer": "High-level solution approach describing the main components and flow — what to validate, which method to refactor to use prepared statements, how to map exceptions to status codes, which tests to add. Do NOT paste full code.",
  "hints": "Single line suggesting the focus area without naming the fix. Example: 'Look at how input arrives at the repository and how it ends up in the SQL string — and what stops a missing field from breaking the request before it reaches the database'",
  "definitions": {{
    "PSR-4": "Composer's autoloading standard mapping namespaces to file paths",
    "PDO prepared statement": "A parameterised SQL statement that separates query structure from user-supplied values",
    "Strict types": "PHP's `declare(strict_types=1)` directive that enforces scalar type declarations at runtime",
    "PHPUnit": "The standard PHP testing framework for unit and integration tests",
    "JSON response": "An HTTP response with `Content-Type: application/json` and a JSON-encoded body, conventionally paired with a meaningful HTTP status code"
  }}
}}

## Code file requirements
- More than one file may be generated — make sure every file is included in the JSON `code_files` map with its full path.
- Code must follow modern PHP 8.x best practices: strict types, type declarations on parameters and returns, constructor property promotion where natural, no `mysql_*` functions (always PDO), PSR-12 formatting.
- Use proper namespaces matching the PSR-4 root in `composer.json` (e.g. `App\\` -> `src/`).
- **CRITICAL**: starter code MUST contain the bug or missing behaviour described in the scenario, but MUST NOT contain the fix.
- DO NOT include any `TODO`, `FIXME`, "implement here", "add validation here", or solution-revealing comment.
- DO NOT add comments that explain what the bug is or how to fix it.
- DO NOT name variables or methods in a way that gives away the answer (e.g. `$validatedInput`, `safeInsert()` when the bug is missing validation / unsafe insert).
- The generated project must be runnable end-to-end (`composer install`, then run via `php -S localhost:8000 -t public` for vanilla PHP, or the framework's standard run command, or `vendor/bin/phpunit` for test-driven scenarios). The buggy behaviour must reproduce on this run.

## .gitignore INSTRUCTIONS
Create a comprehensive PHP `.gitignore` covering: `/vendor/`, `/.phpunit.result.cache`, `/.phpunit.cache/`, `.env`, `.env.local`, `*.log`, `/storage/logs/*` (Laravel only), `/var/cache/*` and `/var/log/*` (Symfony only), IDE directories (`.idea/`, `.vscode/`, `*.swp`), and OS files (`.DS_Store`, `Thumbs.db`).

## README.md STRUCTURE (PHP)

### Task Overview (MANDATORY — 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the code. State concretely what is broken or missing. Use real business context from the chosen scenario; never leave empty or generic text. Do NOT directly tell candidates which functions to add or which patterns to apply — describe the symptom and the desired observable behaviour.

### Objectives

Define goals focusing on outcomes for a BASIC-level PHP task:
  - Clear, observable goals the candidate should achieve (correct status codes, correct DB rows, no fatal errors on malformed input, passing tests)
  - Frame around the symptom from the scenario's "Current Implementation" and the desired behaviour from "Success Criteria"
  - Focus on fundamental PHP concepts: input validation, safe SQL, exception handling, JSON response shape
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify

Verification approaches the candidate can run themselves:
  - Concrete `curl` examples (or framework-equivalent test commands) that exercise the success path AND the failure paths the bug currently mishandles
  - The specific HTTP status code, response body, and DB state to expect after the fix
  - The PHPUnit command and which tests should pass
  - **CRITICAL**: Describe what behaviours to verify, not which specific PHP functions to call

### Helpful Tips

Practical guidance without revealing implementations:
  - Suggest reading the request entry point first to understand how user input reaches the code that breaks
  - Mention thinking about which layer should validate input vs. which layer should talk to the database
  - Hint at considering how PHP behaves when an expected array key is missing and what HTTP response a real API should return in that case
  - Recommend exploring how PDO separates query structure from values, and what happens when values are concatenated into the SQL string
  - Suggest thinking about how exceptions should travel out of the data layer and what a caller should see when persistence fails
  - Point toward considering what the response body and status code should look like for both success and failure paths
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions or function names

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Phrases like "you should call `bindParam`", "wrap this in `try {{ ... }} catch (PDOException $e)`", "add a `validate()` method"
- Specific class/method names that reveal the solution structure
- Setup commands beyond `composer install` and the standard run command for the chosen stack

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no surrounding code fences. Emit the raw JSON object.
2. **name** must be short, descriptive, kebab-case (e.g., "time-off-request-validation-fix")
3. **"title"** must be in `<action verb> <subject>` format, 50-80 characters, and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
4. **code_files** must include README.md, .gitignore, composer.json, and the PHP source files needed for the scenario. If the task asks the candidate to write/fix tests, include phpunit.xml and at least one test file.
5. **README.md** must follow the structure above — Task Overview, Objectives, How to Verify, Helpful Tips (in this order)
6. **Starter code** must run via `composer install` + a documented run command (or `vendor/bin/phpunit`) and must reproduce the bug described in the scenario — verify before finalising.
7. **Strict types**: every PHP source file in the starter must begin with `<?php` followed by `declare(strict_types=1);`
8. **No solution-revealing comments**, no TODO/FIXME, no method/variable names that give away the fix.
9. **outcomes**, **short_overview**, **pre_requisites** must be bullet-point lists in simple language.
10. **hints** must be a single line; **definitions** must include relevant PHP terms (PSR-4, PDO prepared statement, strict types, PHPUnit, JSON response).
11. **Task must be completable within {minutes_range} minutes** for BASIC proficiency (1-2 years).
12. **Stack alignment**: if the scenario names a framework (Laravel, Symfony, Slim), the starter MUST use that framework's idioms — do NOT silently swap to vanilla PHP.
13. **Domain consistency**: route paths, table names, error codes, and currency / unit references in the README, starter code, and tests must all match the chosen scenario.
"""

PROMPT_REGISTRY = {
    "PHP (BASIC)": [
        PROMPT_PHP_BASIC_CONTEXT,
        PROMPT_PHP_BASIC_INPUT_AND_ASK,
        PROMPT_PHP_BASIC,
    ]
}
