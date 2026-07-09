# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""NestJS INTERMEDIATE prompt."""

PROMPT_NESTJS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_NESTJS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
an INTERMEDIATE assessment task.

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
- The task must be a practical NestJS work item requiring design judgement, refactoring, request handling correctness, dependency injection reasoning, and focused testing.
- The task must be completable within {minutes_range} minutes by a candidate with 3-5 years of experience.
- The generated project must be a pure local NestJS project using the Node and TypeScript ecosystem with a native package manifest and test command.
- The starter application must be FULLY FUNCTIONAL and runnable locally with no missing environment, installation, or external service work.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match INTERMEDIATE NestJS level?
"""

PROMPT_NESTJS_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements (NestJS)

## GOAL
As a technical architect super experienced in NestJS, you are given a list of real world scenarios and proficiency levels for NestJS.

Generate a complete assessment task — description, starter code files, README, tests, and evaluator-facing solution guidance — that tests a candidate at INTERMEDIATE proficiency in NestJS. The task must evaluate whether the candidate can work independently on a realistic NestJS backend feature or defect involving modules, controllers, providers, dependency injection, DTO validation, error handling, serialization, guards/interceptors/filters where appropriate, and focused unit or integration tests.

The task must be practical, bounded, and completable within {minutes_range} minutes by a candidate with 3-5 years of experience.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to be comfortable with NestJS as an opinionated, modular, dependency-injection-centric TypeScript framework. They should be able to reason about module boundaries, controller and provider responsibilities, constructor-based dependency injection, custom tokens when useful, DTOs, validation pipes, HTTP exceptions, serialization, guards, interceptors, filters, and Jest or Supertest-based tests.

The candidate is not being evaluated on infrastructure setup, package installation, or memorizing obscure framework configuration. They are being evaluated on applied NestJS judgement: identifying the flawed current implementation, preserving the working application shape, improving correctness and maintainability, and adding focused verification.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## INSTRUCTIONS

### Nature of the Task
- The task asks the candidate to implement a feature, fix a bug, or refactor flawed starter code in an existing NestJS application.
- **CRITICAL**: The starter code MUST be FULLY FUNCTIONAL and must run cleanly before the candidate begins. It may have intentionally incomplete business behavior, weak validation, leaky serialization, poor module boundaries, missing tests, or incorrect error handling, but it must not fail because of syntax errors, missing files, or broken project setup.
- **CRITICAL**: The task must focus on intermediate NestJS concepts, not expert-level distributed systems. Suitable concepts include modular architecture, controllers kept thin, providers/services encapsulating business logic, dependency injection, DTOs and validation, route params and request bodies, HTTP exceptions, response serialization, guards or interceptors where useful, configuration boundaries, and focused Jest/Supertest tests.
- **CRITICAL**: Do not require external datastores, message brokers, queues, caches, search engines, cloud services, or production deployment. If the scenario needs persistence behavior, model it with in-process repositories, fixture-backed stores, or mocked provider abstractions that let the candidate demonstrate NestJS structure without external service configuration.
- The task should require the candidate to touch a realistic but small set of files: typically a feature module, controller, service/provider, DTO, repository abstraction or in-memory repository, one cross-cutting NestJS component if relevant, and one or two tests.
- The task should test 4-5 concepts such as request validation, clear module/provider boundaries, correct HTTP status behavior, safe response shape, dependency injection design, and test coverage.
- The task should avoid circular dependency-heavy architecture unless the selected scenario explicitly centers on module boundary refactoring. If circular dependencies are used, the expected fix should be a small boundary improvement rather than broad architecture redesign.
- The task must include enough starter code to give a clear starting point WITHOUT giving away the solution.
- Do NOT include the solution, TODO comments, step-by-step hints, or solution-revealing comments in the starter code.
- The starter code must implement exactly the "Current Implementation" buggy or incomplete state described in the candidate-facing question.
- Avoid: full authentication platforms, OAuth provider integration, complex GraphQL schemas, real WebSocket infrastructure, microservice transports, production observability stacks, broad CI/CD setup, or anything that cannot be completed solo within the time box.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- For executable code, always invoke commands by their explicit runtime command names such as `npm test` or `npx jest`, never vague phrases like "run the tests".

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, NestJS documentation, TypeScript documentation, Jest documentation, Supertest documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

However:
1. The task must be designed so that external resources help with syntax and recall, but do not replace the candidate's need to reason about the existing code and requirements.
2. The starter code and README must not reveal the implementation approach or name the exact APIs, decorators, pipes, guards, interceptors, filters, functions, or patterns that solve the task.
3. The assessment should reward candidates who can evaluate tradeoffs, keep code maintainable, and verify behavior with tests.
4. The expected answer may describe the high-level solution approach for evaluators, but the candidate-facing README must remain concise and open-ended.

## Code Generation Instructions
Generate a complete NestJS TypeScript project that is ready to run locally from /root/task. The project must use a native Node package manifest and a native test command. The generated code must be realistic enough to evaluate NestJS competence, but small enough to understand quickly.

The output should be a valid json schema:
- `package.json` with scripts for running tests and any minimal local development command needed by the project.
- `tsconfig.json` and, if useful, `tsconfig.build.json` configured for a small NestJS TypeScript project.
- Jest configuration either in `package.json` or a separate Jest config file.
- `src/main.ts` showing the Nest bootstrap process and any global application behavior needed by the starter state.
- `src/app.module.ts` or equivalent root module wiring the feature modules.
- Feature module files such as controller, service/provider, DTOs, repository abstraction, in-memory repository or fixture provider, and any relevant NestJS cross-cutting component.
- Focused test files under `test/` or colocated with source files, using Jest and Supertest where endpoint behavior is important.
- `README.md` following the README instructions below.
- `.gitignore` following the .gitignore instructions below.

## Code file requirements
- Provide all required code files in the `code_files` JSON object. Every file path must be relative to /root/task.
- The project must be FULLY POPULATED. Do not leave placeholder files, missing imports, incomplete module wiring, or empty test suites.
- The starter application must compile and the provided tests must run against the intentionally incomplete or flawed current implementation.
- The initial tests may include a mix of passing tests and failing tests only when the failing tests directly express the required candidate outcome. If failing tests are included, the README and question must make clear that the candidate should make them pass.
- Keep controllers thin. The flawed starter code may violate this principle if it is part of the task, but the expected candidate work should encourage moving behavior into providers or focused abstractions.
- Use TypeScript features naturally: interfaces or types where helpful, readonly constructor injection where appropriate, typed DTOs, and explicit return shapes for important service/controller methods.
- Use NestJS modules, controllers, and providers in a realistic structure. Avoid placing the entire task in a single file.
- Use DTO validation and serialization concerns only at the level required by the chosen scenario. Do not create an excessive framework showcase.
- Include focused tests that verify observable behavior such as HTTP status codes, response shapes, provider interaction, validation failures, or module boundary behavior.
- Do not include comments that tell the candidate exactly what to change. Avoid TODO, FIXME, "candidate should", or equivalent solution markers in code.
- Do not include generated dependency folders, build output, coverage output, or editor-specific files in `code_files`.
- Keep the project local and self-contained. If persistence behavior is needed, use in-memory data or fixture-backed repositories through Nest providers.

## .gitignore INSTRUCTIONS
The `.gitignore` file must be appropriate for a NestJS TypeScript project and should exclude:
- `node_modules/`
- `dist/`
- `coverage/`
- `.env` and local environment override files
- log files
- temporary files
- editor and operating system artifacts

Do not ignore source files, tests, package manifests, TypeScript configuration, or README.md.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md entry inside code_files MUST contain exactly these sections, in this order, and no others:

### Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, decorator, pipe, guard, interceptor, filter, or algorithm that solves the task.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as test output, response shape, status code behavior, log observation, or validation result.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of the candidate-facing README:
- Setup commands such as `npm install`, `npm test`, `npx jest`, or similar command walkthroughs.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, decorators, pipes, guards, interceptors, filters, functions, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use a specific API".

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as "task_title", "files", or "context" — synonyms produce a hollow, unusable task.

Each field's value below is a one-sentence description of what to fill in, not a placeholder example. The final answer must be valid JSON using these exact key names.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the NestJS task without using generic names.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, and different from the repository name.",
  "question": "A full candidate-facing task description that includes the business context, the Current Implementation, the Required Changes, the expected verification behavior, and the time-boxed NestJS scope without revealing the solution.",
  "code_files": {{
    "README.md": "A complete candidate-facing README that uses exactly the required four sections and stays concise, open-ended, and non-revealing.",
    ".gitignore": "A NestJS and Node appropriate ignore file that excludes dependencies, build outputs, coverage, logs, environment files, and local editor artifacts.",
    "package.json": "A native Node package manifest with the minimal scripts and dependencies required for the local NestJS project and test command.",
    "tsconfig.json": "A TypeScript configuration file suitable for compiling and testing the provided NestJS starter project.",
    "src/main.ts": "The NestJS bootstrap entry point showing the current application startup behavior needed by the task.",
    "src/app.module.ts": "The root NestJS module that wires the feature module or modules used in the assessment.",
    "src/<feature>/<feature>.module.ts": "A feature module that declares and exports only the providers required by the scenario.",
    "src/<feature>/<feature>.controller.ts": "A REST controller implementing the current route behavior that the candidate must improve or complete.",
    "src/<feature>/<feature>.service.ts": "A provider containing the current business or application logic state that the candidate must reason about and improve.",
    "src/<feature>/dto/*.ts": "DTO files representing request or response contracts relevant to the selected scenario.",
    "src/<feature>/*.spec.ts or test/*.e2e-spec.ts": "Focused Jest or Supertest tests that verify the observable current behavior and target outcome for the task."
  }},
  "answer": "An evaluator-facing high-level solution approach that explains the intended NestJS design, validation, error handling, serialization, dependency injection, and testing changes without including full code.",
  "definitions": "An object of concise term-to-definition pairs for NestJS concepts used in the task, such as module, provider, DTO, validation pipe, interceptor, guard, repository abstraction, or exception filter when relevant.",
  "hints": "A single line hint nudging the candidate toward investigating boundaries, request contracts, and observable behavior without revealing the fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable API behavior, maintainable NestJS structure, and passing verification checks. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as Node, TypeScript, NestJS fundamentals, REST request handling, DTO validation concepts, and Jest or Supertest basics.",
  "short_overview": "A bullet list summarising the business problem, the NestJS technical focus, and the expected observable outcome."
}}

## CRITICAL REMINDERS
1. Environment runs perfectly out of the box; the candidate fixes the TASK, not the environment.
2. Starter code is runnable but does NOT contain the core solution.
3. Starter code perfectly matches the "Current Implementation" described in the question.
4. No solution-revealing comments, TODO markers, or hidden implementation instructions in code.
5. The README has exactly four sections: Task Overview, Objectives, Helpful Tips, and How to Verify.
6. README content must be concise, open-ended, and must not reveal exact APIs, decorators, functions, or implementation patterns.
7. The task must be a pure local NestJS project with a native package manifest and test command.
8. Completable within {minutes_range} minutes by an intermediate NestJS candidate with 3-5 years of experience.
9. Output JSON uses the CANONICAL key names above — this is non-negotiable.
"""

PROMPT_REGISTRY = {
    "NestJs (INTERMEDIATE)": [
        PROMPT_NESTJS_INTERMEDIATE_CONTEXT,
        PROMPT_NESTJS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_NESTJS_INTERMEDIATE_INSTRUCTIONS,
    ]
}