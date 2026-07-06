# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""NestJs BEGINNER prompt.

Generated prompt registry entry for beginner-level NestJS assessment tasks.
"""

PROMPT_NESTJS_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_NESTJS_BEGINNER_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a BEGINNER NestJS assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must assess beginner-level NestJS work only: modules, controllers, services/providers, DTOs, simple validation awareness, basic route handlers, simple async/await, built-in HTTP exceptions, and in-memory data behavior.
- The task must be a small, realistic work item in an existing NestJS codebase, such as fixing one service method, adding one simple endpoint backed by in-memory data, moving misplaced logic into a service, or correcting basic request handling.
- The task must be completable within {minutes_range} minutes by a candidate with 0-1 years of experience.
- Do NOT require databases, Docker, authentication implementation, deployment setup, advanced configuration, complex test infrastructure, or production architecture.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match BEGINNER NestJS level?
"""

PROMPT_NESTJS_BEGINNER_INSTRUCTIONS = """
# BEGINNER Task Requirements (NestJS)

## GOAL
As a technical architect super experienced in NestJS, you are given a list of real world scenarios and proficiency levels for NestJS. Generate a complete assessment task — description, starter code files, README, and evaluator-facing answer — that tests a candidate at BEGINNER proficiency (0-1 years experience).

The generated task must be a small, realistic NestJS REST API work item in a FULLY FUNCTIONAL local TypeScript project. The candidate should modify or complete existing starter code, not create a project from scratch and not repair the environment.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is a beginner NestJS developer who should understand what NestJS is, how it builds on Node.js/Express, and how modules, controllers, services/providers, DTOs, dependency injection, and the request-response lifecycle fit together.

The candidate is expected to:
- Work inside a small existing NestJS project with clear module, controller, service, and DTO files.
- Keep controllers focused on HTTP request mapping and delegate basic business logic to services.
- Use in-memory arrays or maps for simple CRUD-style behavior without external persistence.
- Use basic TypeScript types, DTO classes, async/await where appropriate, and built-in HTTP exceptions such as NotFoundException or BadRequestException.
- Recognize simple validation and request-body shape expectations without being required to design complex validation infrastructure.
- Run local tests or endpoint checks and communicate basic design choices using correct NestJS terminology.

The candidate is NOT expected to implement authentication, JWT, Passport, database integration, migrations, Docker deployment, advanced ConfigModule setup, custom interceptors, complex guards, performance optimization, or advanced testing strategy.

## INSTRUCTIONS
Generate a complete coding task that asks the candidate to implement a feature or fix a bug in existing NestJS starter code.

### Nature of the Task
- **CRITICAL**: The task must remain BEGINNER level and completable within {minutes_range} minutes.
- **CRITICAL**: The task must focus on one isolated NestJS concept or one small combination of closely related beginner concepts.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL and runnable before the candidate begins. It may have failing tests or incomplete behavior that represents the task, but it must not have syntax errors, missing imports, broken package setup, or environment failures.
- **CRITICAL**: The Current Implementation described in the question must exactly match the code behavior in the starter files.
- **CRITICAL**: Do NOT include solution-revealing TODO comments, hidden hints, or comments that tell the candidate what exact line to change.
- Prefer one of these beginner NestJS task shapes:
  - Fix a service method that should create, read, update, delete, or filter in-memory data.
  - Add one simple REST endpoint and delegate the behavior to an existing service.
  - Correct controller/service responsibility so controller code maps requests and service code owns business logic.
  - Add or use a simple DTO to shape a request body for one endpoint.
  - Add simple NotFoundException or BadRequestException behavior for one obvious missing-resource or invalid-input case.
  - Fix a basic dependency injection or provider registration issue only when the cause is simple and visible in the module.
- Avoid multi-step architecture work. Do not require multiple feature areas, large refactors, authentication, persistence, deployment, microservices, queues, caching, or complex validation.
- Use the selected real-world scenario as the domain. The employer context is the assessment administrator, not necessarily the task domain.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- Title: human-readable display name in an "<action verb> <subject>" format, 50-80 characters, and different from the kebab-case name.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, NestJS documentation, TypeScript documentation, Node.js documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The task should be designed so that:
- External resources help the candidate understand syntax, framework conventions, and basic APIs, but do not replace the need to reason about the provided code.
- AI tools may assist with explanations or boilerplate, but the candidate must still inspect the starter code and make the correct beginner-level change.
- The solution cannot be completed by blindly copying a generic answer; it must depend on the specific current implementation and scenario.
- The README and question must not forbid AI or web usage.

## Code Generation Instructions
Generate a pure local NestJS project using Node.js, TypeScript, and the runtime-native package manifest. The project must not depend on any external datastore or infrastructure.

- Include a `package.json` with scripts for running tests and, if useful, starting the local NestJS app.
- Include TypeScript/NestJS configuration files needed for a small local project, such as `tsconfig.json`, `tsconfig.build.json`, and `nest-cli.json` when appropriate.
- Include source files under `src/` using normal NestJS naming conventions, such as `app.module.ts`, a feature module, a controller, a service, and one DTO file when relevant.
- Include a small Jest test file that verifies the intended behavior at a beginner level. The tests may initially fail because the candidate has not completed the task, but the test runner and project setup must work.
- The code must use in-memory data only. Do NOT include database clients, ORM configuration, schema files, migrations, Redis clients, queues, or any external service.
- Do NOT include `docker-compose.yml`, `init_database.sql`, `kill.sh`, `Dockerfile`, Kubernetes files, deployment manifests, or datastore configuration.
- Do NOT include `apt-get install`, `npm install`, or other installation steps in generated scripts. The runtime and common libraries are pre-installed by the template.
- Do NOT use environment variables or `.env` file references for this beginner local task.
- Keep the starter code small and readable. Use clear class names, method names, DTO names, and basic TypeScript types.
- Use async/await only where it naturally fits the controller/service flow. Do not introduce complex Promise orchestration.
- Ensure the generated task does not primarily assess CLI/tool installation, package setup, decorator memorization, advanced testing configuration, deployment mechanics, or pure TypeScript trivia.

The output should be a valid json schema:
- `README.md` must contain the candidate-facing task instructions using the README requirements below.
- `.gitignore` must contain appropriate Node.js/NestJS exclusions.
- `package.json` must define the local project metadata and native test/start scripts.
- `tsconfig.json` and any required TypeScript/NestJS config files must support the included source and tests.
- `src/**/*.ts` files must contain the starter NestJS module, controller, service, DTO, and related code for the selected scenario.
- `test/**/*.ts` or `src/**/*.spec.ts` files must contain focused tests for the expected behavior.
- Do not include infrastructure files, datastore files, or deployment files for this non-infra task.

## Code file requirements
- The generated code files must form a complete, coherent project under /root/task.
- The starter code must be FULLY FUNCTIONAL and must represent the incomplete or buggy Current Implementation described in the question.
- The code must not include the final solution.
- The code must not include comments such as `TODO`, `FIXME`, `implement this`, `your code here`, or any direct instruction that reveals the answer.
- The task should generally require changes in one primary file and at most one supporting file.
- The candidate-facing code should be readable enough for a beginner to navigate without advanced NestJS knowledge.
- Prefer simple REST-style routes using familiar HTTP methods such as GET, POST, PATCH, PUT, or DELETE.
- Prefer simple JSON response shapes such as `{{"message": "A short status message", "data": "The relevant response data"}}` when a wrapper is helpful, but do not require complex response conventions.
- If using validation, keep it simple and beginner appropriate. Do not require custom validators or advanced validation pipe configuration.
- If using exceptions, use standard NestJS built-in exceptions and keep the error condition obvious.
- Tests must validate observable behavior rather than implementation details whenever possible.
- All file paths in `code_files` must be relative paths suitable for creating files under /root/task.

## .gitignore INSTRUCTIONS
The `.gitignore` entry must be appropriate for a local NestJS/Node.js TypeScript project and should include common exclusions such as:
- `node_modules/`
- `dist/`
- `coverage/`
- `.env`
- `.env.*`
- `.DS_Store`
- npm/yarn/pnpm debug logs
- editor and operating-system noise where appropriate

Do not include exclusions that hide the starter source files, tests, package manifest, TypeScript configuration, or README.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The `README.md` file inside `code_files` MUST contain exactly these sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
- Must be 3-4 meaningful sentences.
- Must not be a bullet list.
- Must describe the business scenario, the current state, and why the problem matters.
- Must NEVER be empty.
- Must not include bold time-budget callouts.
- Must not include setup commands, package installation instructions, Docker commands, or database connection information.

### Objectives
- Must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step or an API/library to use.
- Do not reveal exact method names, exact code changes, or the line that must be edited.

### Helpful Tips
- Must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not include code snippets or solution-revealing examples.

### How to Verify
- Must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run or observe, such as test output, response shape, status behavior, console output, or an in-memory behavior visible through an endpoint.
- Do not include package installation commands or Docker commands.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
Keep the following out of the README entirely:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or similar installation/deployment commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Database connection details, including host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders.
- Any README heading named "NOT TO INCLUDE", "CONTENT TO EXCLUDE", or similar. The exclusion list is an instruction to you, not a README section.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context`; synonyms produce a hollow, unusable task.

Each field value below is a description of what you must generate. The final output must be valid JSON using these exact keys:

{{
  "name": "A kebab-case GitHub repository name under 50 characters that clearly reflects the beginner NestJS task without revealing the solution.",
  "title": "A human-readable display title in an '<action verb> <subject>' format, 50-80 characters long, different from the name, and suitable for a candidate assessment.",
  "question": "A complete candidate-facing task description that includes the selected business scenario, the Current Implementation that the starter code actually contains, the Required Changes stated as observable outcomes, the expected time range, and any beginner-level constraints without revealing the solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README following exactly the required Task Overview, Objectives, Helpful Tips, and How to Verify sections in that order.",
    ".gitignore": "A Node.js and NestJS appropriate gitignore file that excludes dependencies, build output, coverage, environment files, logs, and editor or operating-system noise.",
    "package.json": "A runtime-native Node.js package manifest for the local NestJS project with scripts needed to run tests and optionally start the app, without installation or infrastructure commands.",
    "tsconfig.json": "A TypeScript configuration file suitable for compiling and testing the included beginner NestJS source files.",
    "nest-cli.json": "A minimal NestJS CLI configuration file if needed for the generated project structure.",
    "src/app.module.ts": "The root NestJS module that imports or registers the small feature area used by the task.",
    "src/<feature>/<feature>.module.ts": "A simple feature module that groups the beginner-level controller and service when a feature module fits the task.",
    "src/<feature>/<feature>.controller.ts": "A NestJS controller containing route handlers for the selected scenario, with starter behavior that maps requests and delegates appropriately except for the intentional task gap.",
    "src/<feature>/<feature>.service.ts": "A NestJS service containing in-memory data and simple business behavior, with the intentional beginner-level bug or missing behavior reflected in the task description.",
    "src/<feature>/dto/<dto-name>.dto.ts": "A simple DTO file describing the relevant request body shape when the scenario requires request-body data.",
    "src/**/*.spec.ts": "Focused Jest tests that exercise the expected observable behavior and may initially fail until the candidate completes the task."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the intended beginner-level code change, why it works in NestJS terms, and how it satisfies the observable requirements without exposing unnecessary advanced details.",
  "definitions": "An object of task-relevant beginner NestJS terms mapped to short definitions, such as module, controller, service, provider, DTO, dependency injection, route handler, or HTTP exception.",
  "hints": "A single line nudging the candidate toward the relevant area of the NestJS request flow without revealing the exact fix, method name, or implementation.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable endpoint behavior, correct in-memory state changes, appropriate response shape or status behavior, and passing local tests. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as basic Node.js, TypeScript, NestJS modules/controllers/services, DTO awareness, HTTP request-response basics, and running a local test script.",
  "short_overview": "A bullet list summarising the business problem, the beginner NestJS technical focus, and the expected observable outcome after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. The task must be BEGINNER level for NestJS and completable within {minutes_range} minutes.
2. The generated project must be FULLY FUNCTIONAL and local-only; the candidate fixes the task, not the environment.
3. Do NOT include Docker, docker-compose, init database files, kill.sh, Dockerfile, external datastores, deployment scripts, or infrastructure requirements.
4. Starter code must compile and run, but must not contain the core solution.
5. Starter code must perfectly match the Current Implementation described in the question.
6. Keep the task focused on modules, controllers, services, DTOs, basic routes, in-memory data, async/await basics, or simple HTTP exceptions.
7. Do NOT require authentication implementation, database integration, advanced validation, custom guards, interceptors, ConfigModule, Swagger setup, or production deployment.
8. Do NOT include solution-revealing comments, TODO markers, or exact line-change hints in code or README.
9. README must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no extra sections.
10. Output JSON uses the CANONICAL key names above — this is non-negotiable.
"""

PROMPT_REGISTRY = {
    "NestJs (BEGINNER)": [
        PROMPT_NESTJS_BEGINNER_CONTEXT,
        PROMPT_NESTJS_BEGINNER_INPUT_AND_ASK,
        PROMPT_NESTJS_BEGINNER_INSTRUCTIONS,
    ]
}