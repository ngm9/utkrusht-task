# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""NestJS BASIC prompt registry entry.

This prompt generates pure local NestJS assessment tasks for BASIC proficiency.
"""

PROMPT_NESTJS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_NESTJS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a BASIC NestJS assessment task.

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
- The task must be a small practical NestJS feature, bug fix, or refactor combining 2-3 BASIC concepts only.
- The task must be completable within {minutes_range} minutes by a candidate with about 1 year of NestJS experience.
- The task must use a pure local NestJS project with package.json, source files, and tests. Do not require external services or datastore setup.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about, including the selected domain, current state, and problem?
2. What will the candidate build or fix, and how does it match BASIC NestJS proficiency?
"""

PROMPT_NESTJS_BASIC_INSTRUCTIONS = """
# BASIC Task Requirements for NestJS

## GOAL
As a technical architect super experienced in NestJS, you are given a list of real world scenarios and proficiency levels for NestJS.

Generate a complete assessment task — description, starter code files, README, and evaluator-facing answer — that tests a candidate at BASIC proficiency. The candidate should demonstrate practical understanding of NestJS modular architecture, controllers, services, dependency injection, DTO validation, simple REST endpoints, basic guards or exceptions when relevant, and maintainable separation of concerns.

The task must be a well-scoped feature, bug fix, or small refactor that can be completed within {minutes_range} minutes by someone with about 1 year of NestJS experience.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is applying for a role where BASIC NestJS proficiency means they can navigate a standard Nest project, understand the relationship between modules, controllers, and services, use dependency injection instead of manual class construction, define simple REST endpoints, apply DTO validation, return appropriate HTTP errors, and follow existing project patterns.

The task should reveal whether the candidate can work inside an already-created NestJS codebase without needing to design a new system. The candidate should not be asked to solve advanced production architecture, complex authentication flows, database infrastructure, microservices, custom deployment pipelines, or framework trivia.

**CRITICAL**: Keep this at BASIC level. The candidate may have shaky concepts and limited production experience, so the task should be narrow, realistic, and focused on applied NestJS fundamentals.

## INSTRUCTIONS
- Create a practical NestJS assessment grounded in one of the provided real-world scenarios.
- The task asks the candidate to implement a small feature, fix a broken endpoint, improve a simple controller/service flow, add straightforward validation, apply a basic guard or exception, or refactor obvious controller business logic into a service.
- Focus on 2-3 concepts from the BASIC NestJS scope, such as:
  - modules, controllers, and services;
  - constructor-based dependency injection;
  - REST route handlers, route parameters, request bodies, and status codes;
  - DTOs with class-validator and class-transformer;
  - ValidationPipe configuration;
  - basic HttpException subclasses such as NotFoundException, BadRequestException, or ForbiddenException;
  - simple guards or role checks when already scaffolded;
  - Nest Logger usage for small observable events;
  - basic Jest tests against controllers or services.
- Generate a FULLY FUNCTIONAL local NestJS starter project. The project must run cleanly before the candidate begins, even though the task behavior is incomplete or incorrect.
- Starter code must implement exactly the current buggy or incomplete state described in the question.
- Do NOT include the solution, TODO comments, solution-revealing comments, or hidden implementation instructions inside starter code.
- Do NOT require external datastores, queues, caches, Docker, deployment infrastructure, CI setup, Swagger decorator recall, Nest CLI command usage, or package installation mechanics.
- Avoid tasks that primarily assess pure TypeScript syntax, linting setup, formatting tools, advanced testing utilities, complex JWT strategies, database migrations, ORMs, transactions, performance tuning, or microservices.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- The generated task must be suitable for a pure local Node.js and NestJS project using the runtime's native manifest and test command.
- For executable commands, always use the runtime's explicit command names such as `npm test`.

### Nature of the Task
**CRITICAL**: This is a BASIC NestJS assessment for approximately 1 year of experience. The task should be small enough for the candidate to complete quickly while still showing whether they understand NestJS architecture and request flow.

**CRITICAL**: The candidate should work in an existing starter project. They should not create a project from scratch, install packages, configure Docker, or wire infrastructure.

**CRITICAL**: The task should evaluate applied competence, not trivia. Prefer a short broken endpoint, an overstuffed controller that needs service separation, a missing provider registration, a missing validation pipe, a simple role check using an existing pattern, or a missing NotFoundException over conceptual questions.

**CRITICAL**: Keep business logic out of controllers in the expected solution. Controllers should parse requests and delegate to services. Services should contain the relevant business behavior.

**CRITICAL**: The starter environment must be FULLY FUNCTIONAL and runnable. Tests may fail because the candidate has not completed the feature, but the project must not fail because of missing files, syntax errors, broken imports, missing package scripts, or missing dependencies in package.json.

**CRITICAL**: Do not ask the candidate to build a full authentication system, integrate a database, write deployment files, implement advanced custom providers, or design a full module architecture. If authentication or authorization appears, keep it to a tiny route-level role check using already-provided request user data or already-scaffolded guard/decorator patterns.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, NestJS documentation, TypeScript documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The assessment should be designed so that successful completion requires understanding and applying NestJS concepts, not memorizing syntax.
- Do not include instructions that forbid AI tools, documentation, search engines, or developer assistants.
- The task should be specific enough that candidates must adapt guidance to the provided codebase.
- The evaluator-facing answer should describe the expected approach clearly enough for review while never appearing in candidate-facing files.

## Code Generation Instructions
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

Generate a pure local NestJS project. The generated project MUST NOT include Docker, docker compose, database initialization scripts, datastore configuration, external services, or infrastructure cleanup scripts.

The project should include a native Node.js manifest and a small NestJS application structure. Prefer a compact file set that is easy to inspect and complete within the time box.

The generated project should normally include:
- `package.json` with scripts for running tests and, when useful, starting the Nest application locally.
- `tsconfig.json` and any minimal Jest or TypeScript configuration needed for the tests to run.
- `src/main.ts` when the task needs bootstrap behavior such as global validation.
- `src/app.module.ts` or a small feature module.
- One controller file and one service file, unless the selected task naturally requires a tiny guard, DTO, or helper.
- DTO files only when validation or request-body shape is part of the assessment.
- Test files that express the expected behavior without giving away the exact implementation.

The output should be a valid json schema:
- `README.md` must contain the candidate-facing task overview and guidance using the README instructions below.
- `.gitignore` must contain standard Node.js and NestJS exclusions.
- `package.json` must define a local project using NestJS and Jest-compatible scripts.
- `tsconfig.json` must support TypeScript compilation for the provided files.
- `src/main.ts` must be included when bootstrap-level behavior is part of the task.
- `src/app.module.ts` or a feature module must register controllers and providers needed by the starter project.
- Controller, service, DTO, guard, pipe, or filter files must be included only as needed by the selected BASIC task.
- Test files must verify the target behavior at an appropriate level for a small NestJS task.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

**MUST NOT include environment variables or .env file references** unless the selected task specifically tests a tiny configuration-management issue within BASIC scope. For most BASIC NestJS local tasks, avoid environment configuration entirely.

Do not include setup scripts that install Node.js, npm, Nest CLI, or packages. The runtime and common libraries are assumed to be available in the execution environment.

## Code file requirements
The generated starter code must be complete enough for the candidate to run tests immediately.

Code quality requirements:
- Use idiomatic NestJS file organization and naming.
- Keep the file count small and focused.
- Use TypeScript types where they clarify the API contract.
- Avoid `any` for request bodies when DTOs are relevant.
- Keep controller methods focused on routing and delegation.
- Keep service methods focused on business behavior.
- Register providers through Nest dependency injection rather than manual construction.
- Include meaningful test cases that fail for the incomplete behavior and pass when the candidate completes the expected change.
- Do not write tests that depend on timing, network services, external databases, or unavailable local resources.
- Do not add TODO comments, answer comments, or code snippets that reveal the fix.
- Do not include placeholder file contents. Every file must be FULLY POPULATED and internally consistent.

The starter code should intentionally contain a small, realistic gap such as:
- a controller manually creating a service instead of using dependency injection;
- a missing NotFoundException for absent in-memory data;
- a route returning the wrong status or shape;
- a DTO validation path not being triggered;
- business logic sitting in a controller that should be delegated to a service;
- a simple role check missing from a protected route when request user data is already available.

Use in-memory arrays or simple local objects when data is needed. Do not require a database.

## .gitignore INSTRUCTIONS
The `.gitignore` entry inside `code_files` must be appropriate for a local Node.js and NestJS project.

It should exclude:
- `node_modules/`
- `dist/`
- `coverage/`
- common log files
- local editor and OS files
- local environment files if present in tooling defaults, while the task itself should not require an `.env` file

Do not exclude source files, tests, package manifests, or README.md.

## README.md INSTRUCTIONS
The `README.md` entry inside `code_files` must contain exactly these output sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

### Task Overview
- Use 3-4 meaningful sentences.
- Do not use a bullet list.
- Describe the business scenario, current state, and why the problem matters.
- This section must NEVER be empty.
- Do not include bold time-budget callouts.
- Do not include setup commands.

### Objectives
- Use 4-6 bullets maximum.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet must state an observable end-state, not a step or an API/library to use.
- Do not mention exact implementation details, method names, decorator names, library calls, or file-by-file changes.

### Helpful Tips
- Use 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with one of these action words: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not include direct solution instructions.

### How to Verify
- Use 4-6 bullets maximum.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run, such as test output, response shape, expected status behavior, log line, or local application behavior.
- Include the native local test command only when necessary for verification, such as `npm test`.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of the README:
- Setup commands such as `npm install`, package installation steps, Docker commands, or environment provisioning steps.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use a specific API".
- Database connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or infrastructure placeholders.
- Any heading named "NOT TO INCLUDE", "Do Not Include", or similar exclusion wording in the generated README.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context` because synonyms produce a hollow, unusable task.

Each field value in the schema below is a description of what to fill in. The final output must be valid JSON using these exact keys.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that clearly identifies the NestJS BASIC task without using spaces or punctuation beyond hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters long, that is different from the repository name.",
  "question": "The full candidate-facing task description, including the selected business scenario, the current implementation state, the required behavioral change, and the constraints that keep the task at BASIC NestJS level.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content following exactly the required README sections and avoiding solution-revealing details.",
    ".gitignore": "A complete Node.js and NestJS oriented gitignore with standard local build, dependency, coverage, log, editor, and OS exclusions.",
    "package.json": "A complete Node.js package manifest for the local NestJS starter project with scripts for running the tests and any minimal runtime scripts needed for local verification.",
    "tsconfig.json": "A complete TypeScript configuration suitable for compiling and testing the provided NestJS source files.",
    "src/main.ts": "The NestJS bootstrap file when needed by the task, containing only the minimal application startup and global configuration relevant to the starter state.",
    "src/app.module.ts": "The root or feature module registration file that wires the starter controllers and providers in a way consistent with the described current implementation.",
    "src/example.controller.ts": "A task-specific controller file whose actual path and name should match the selected scenario and contain the incomplete or buggy request-handling behavior.",
    "src/example.service.ts": "A task-specific service file whose actual path and name should match the selected scenario and contain the relevant starter business logic without the final solution.",
    "src/example.dto.ts": "A task-specific DTO file included only when request validation or transformation is part of the selected BASIC task.",
    "test/example.spec.ts": "A focused Jest test file whose actual path and name should match the selected scenario and verify the expected behavior after the candidate completes the task."
  }},
  "answer": "An evaluator-facing high-level solution approach explaining the intended NestJS changes, why they satisfy the task, and what behavior should be observed after completion without including excessive code.",
  "definitions": "An object mapping important NestJS and HTTP terms used in the task to concise definitions that help evaluators understand the competency being assessed.",
  "hints": "A single line hint nudging the candidate toward the relevant NestJS concept without revealing the exact fix or naming the specific implementation to write.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on observable API behavior, passing tests, correct NestJS layering, and maintainable BASIC-level code.",
  "pre_requisites": "A bullet list of tools and knowledge needed, limited to Node.js, TypeScript, NestJS basics, REST fundamentals, and running the local test command.",
  "short_overview": "A bullet list summarising the business problem, the NestJS technical focus, and the expected outcome in simple english."
}}

## CRITICAL REMINDERS
1. The task must be based on ONE provided real-world scenario and must not invent a different domain.
2. Keep the task BASIC: small, practical, and completable within {minutes_range} minutes by a candidate with about 1 year of NestJS experience.
3. The generated project must be pure local NestJS with package.json, source files, and tests only.
4. Do not include Docker, docker compose, datastore setup, database initialization files, infrastructure cleanup scripts, deployment files, or external service requirements.
5. Starter code must be FULLY FUNCTIONAL, internally consistent, and runnable without syntax errors or missing imports.
6. Starter code must represent the exact current implementation described in the question.
7. Do not include solution code, TODO comments, or solution-revealing comments in starter files.
8. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, with no extra sections.
9. Output JSON must use the CANONICAL key names exactly: `name`, `title`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, and `short_overview`.
10. If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
"""

PROMPT_REGISTRY = {
    "NestJs (BASIC)": [
        PROMPT_NESTJS_BASIC_CONTEXT,
        PROMPT_NESTJS_BASIC_INPUT_AND_ASK,
        PROMPT_NESTJS_BASIC_INSTRUCTIONS,
    ]
}