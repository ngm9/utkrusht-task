PROMPT_NODEJS_GRAPHQL_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how GraphQL is used in Node.js-based backend systems at an intermediate level — such as for schema evolution, resolver design, authentication and authorization, integration with existing REST services, batching/caching, and production-grade API performance and security?
"""

PROMPT_NODEJS_GRAPHQL_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js and GraphQL assessment task.

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

1. What will the task be about? (Describe the business domain, GraphQL API context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Node.js and GraphQL implementation, refactor, or fix required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_GRAPHQL_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Node.js, GraphQL, backend API architecture, and schema-driven service design, you are given a list of real world scenarios and proficiency levels for Node.js + GraphQL development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL or near-FULLY FUNCTIONAL Node.js backend project with an existing GraphQL API surface, starter schema, resolver structure, and supporting service modules already wired together.
The project should feel like a realistic production codebase where the candidate must extend, refactor, debug, or secure an existing GraphQL API rather than build everything from scratch.
The candidate is expected to work within a maintainable Node.js project structure, reason about schema and resolver behavior, and make sound implementation decisions that balance correctness, performance, security, and backward compatibility.
The task should reflect intermediate expectations for someone with roughly 3-6 years of hands-on Node.js experience and solid GraphQL experience, while still being completable within the allocated time with AI assistance allowed.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors or add features hastily.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-6 years Node.js and GraphQL experience), ensuring that no two questions generated are similar.
- **CRITICAL**: The task must stay within the competency scope for intermediate Node.js and GraphQL. Focus on schema design using SDL, resolver implementation, nested object resolution, integration with existing REST-style service modules, batching/caching patterns such as DataLoader-style approaches, authentication/authorization via request context, structured error handling, query complexity awareness, and safe schema evolution.
- **CRITICAL**: Do NOT make the task primarily about advanced federation, full subscription infrastructure, cluster management, microservices orchestration, CI/CD setup, cloud deployment, or highly specialized scaling patterns. Awareness of these may appear in context, but they must not be the core implementation requirement.
- **CRITICAL TIME BUDGET**: The total task time is {minutes_range}. The candidate needs a few minutes to verify and test their implementation. So the actual implementation work must be realistically completable by an intermediate-level developer within that time, with multiple valid solution paths.
- **CRITICAL SCOPE**: The task must have 3-4 focused objectives that test intermediate Node.js + GraphQL concepts such as:
  - Extending or refactoring an existing GraphQL schema safely without breaking consumers
  - Implementing or fixing nested resolvers and parent-child resolution behavior
  - Integrating GraphQL resolvers with one or more existing in-process service modules that simulate REST or legacy backends
  - Improving resolver performance by reducing repeated data fetching and avoiding N+1 style behavior
  - Implementing authentication and authorization checks using request context
  - Improving mutation contracts, validation, and structured error responses
  - Adding schema descriptions, deprecations, or non-breaking evolution patterns
  - Adding pragmatic protections for expensive queries such as depth or complexity limits
  - Improving logging or observability around resolver execution and failures
- For INTERMEDIATE level, the scenarios should require architectural thinking and involve:
  - A schema with multiple related types and at least one interface, union, enum, input type, or custom scalar where relevant to the scenario
  - Existing resolvers with logical gaps, performance issues, authorization flaws, or maintainability problems
  - A realistic brownfield integration shape where GraphQL wraps existing service functions or legacy endpoints
  - Tradeoffs around schema evolution, error modeling, and consumer impact
  - Practical Node.js backend structure using TypeScript or modern JavaScript with async/await patterns exclusively
- The question must NOT include hints. The hints will be provided in the \"hints\" field.
- Ensure that all questions and scenarios adhere to modern Node.js best practices (Node.js 18+) and current GraphQL development standards.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Node.js documentation, GraphQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate Node.js and GraphQL proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Node.js + GraphQL task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-6 years Node.js and GraphQL experience), keeping in mind that AI assistance is allowed
- Tests practical GraphQL and backend Node.js skills that require architectural thinking, schema design judgment, resolver implementation quality, performance considerations, and security awareness
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- Focus on an existing GraphQL API that requires schema extension, resolver fixes, authorization hardening, performance improvement, or legacy integration refinement
- The task environment should be a local Node.js project using the runtime's native manifest and test command, with no external datastore required unless the selected scenario truly depends on one
- The starter code should simulate realistic backend integrations through service modules, fixtures, or lightweight adapters so the candidate can focus on GraphQL and Node.js reasoning rather than infrastructure setup

## Infrastructure Requirements
- This is a pure-runtime backend task and should be shipped as a local Node.js project using the runtime's native package manifest and source files.
- **CRITICAL**: Do NOT include docker-compose.yml, init_database.sql, Redis configuration, or any datastore configuration when the selected scenario can be fully assessed through in-process code and tests.
- **CRITICAL**: Do NOT include kill.sh for this backend pure-runtime shape.
- **CRITICAL**: The project must run locally using Node.js and the package manifest only.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

### Docker-compose Instructions
- Do NOT generate a docker-compose.yml file for this task.
- Do NOT require any external database, cache, queue, or broker unless the selected scenario explicitly depends on one as a core part of the assessment.
- **CRITICAL**: Even if template datastores are available, they are optional here and must not be included for a pure GraphQL + Node.js runtime task.
- **MUST NOT include any version specification** because no compose file should be generated.
- **MUST NOT include environment variables or .env file references**.

### Local Project Instructions
- Generate a valid Node.js project using package.json as the native manifest.
- The code files generated must be valid and executable with the runtime's native commands such as `npm test`, `npm run test`, `npm run dev`, or `npm start`.
- Use modern Node.js 18+ conventions and TypeScript if that best matches the runtime/framework context.
- The starter code should provide a realistic project structure that mimics real-world GraphQL backend applications, such as src/schema/, src/resolvers/, src/services/, src/context/, src/middleware/, src/utils/, and tests/.
- Include enough existing code that the system partially works and the candidate extends, refactors, or fixes the problematic parts.
- Include some existing schema modules, resolver modules, service adapters, and tests that the candidate needs to work with or extend.
- Provide partial implementations that require candidates to complete the architectural work.
- If the scenario includes legacy integration, represent it through local service modules or mock HTTP clients rather than requiring live external systems.

### Run.sh Instructions
- run.sh is optional for this pure-runtime backend task.
- If you include run.sh, use `#!/usr/bin/env bash` and `set -e` at the top.
- If included, it should only run local verification steps such as changing to `/root/task`, validating Node.js availability, and running the native test command.
- It must NOT install the runtime, framework, or common libraries because they are pre-installed by the template.
- It must NOT use Docker or Docker Compose.
- It should print clear progress logs and end with a success message if verification passes.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Node.js and TypeScript exclusions)
  - package.json (Native Node.js manifest with scripts and dependencies)
  - tsconfig.json or jsconfig.json (if TypeScript or path configuration is used)
  - run.sh (Optional local verification script only if useful)
  - src/index.ts or src/index.js (Application entry point)
  - src/app.ts or src/server.ts (GraphQL server bootstrap and middleware wiring)
  - src/schema/*.ts or src/schema/*.js (SDL modules and schema composition)
  - src/resolvers/*.ts or src/resolvers/*.js (Resolver implementations)
  - src/services/*.ts or src/services/*.js (Legacy/REST/data-source adapters)
  - src/context/*.ts or src/context/*.js (Request context and auth helpers)
  - src/utils/*.ts or src/utils/*.js (Shared helpers such as error formatting, logging, validation, or batching utilities)
  - tests/*.test.ts or tests/*.test.js (Verification-focused tests)
  - additional files as needed for realistic project structure

## Code file requirements
- Generate realistic folder structure appropriate for an intermediate Node.js + GraphQL backend task.
- Code should follow modern Node.js best practices and demonstrate intermediate-level GraphQL patterns.
- Use async/await patterns exclusively, no callback-based code.
- Focus on clean modular code with proper separation of concerns between schema, resolvers, service layer, context, and utilities.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion.
- Include some existing schema modules, resolvers, or services that need to be extended, refactored, secured, or optimized.
- The core architectural decisions, schema evolution choices, resolver composition, batching/caching strategy, authorization approach, error model, or query protection mechanisms that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT include comments like \"Add DataLoader here\", \"Implement auth check\", \"Use depth limit\", or similar.
- DO NOT add comments that give away hints, solution, or implementation details.
- The generated project structure should be runnable locally with the native Node.js commands, but will require architectural work to function correctly or pass all tests.
- Provide realistic dependencies in package.json that intermediate developers should be familiar with in a Node.js + GraphQL backend.
- If tests are included, they should validate observable behavior and leave room for multiple valid implementations.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for Node.js and TypeScript backend projects including node_modules/, build outputs (dist/, build/), IDE configurations (.idea/, .vscode/, *.swp, *.swo), compiled files, environment files (.env), log files (*.log, logs/), coverage reports (.nyc_output/, coverage/), and other common development artifacts.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

- The README.md file content MUST be fully populated with meaningful, specific content.
- Task Overview section MUST contain the exact business scenario from the task description.
- ALL sections must have substantial content - no empty or placeholder text allowed.
- Content must be directly relevant to the specific task scenario being generated.
- Use concrete business context, not generic descriptions.
- The README must NOT contain database connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### Task Overview
- This section MUST contain 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- It should explain the GraphQL API problem in realistic product terms, such as schema evolution pressure, resolver correctness issues, authorization gaps, performance regressions, or legacy integration constraints.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- 4-5 bullets max.
- Each bullet starts with an action word: \"Consider\", \"Think about\", \"Explore\", \"Review\", \"Analyze\".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Helpful Tips should guide the candidate toward reasoning about schema boundaries, resolver behavior, consumer impact, performance tradeoffs, and security concerns without prescribing the implementation.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the \"what\" and \"why\", never the \"how\".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Focus on both functional requirements and code quality metrics.
- Objectives should be appropriate for intermediate Node.js + GraphQL level and may cover schema correctness, resolver behavior, authorization, performance, and maintainability.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as response shape, error behavior, authorization outcome, repeated query behavior, or test results.
- Verification should focus on externally visible GraphQL behavior and maintainability signals rather than internal implementation details.

### NOT TO INCLUDE in README
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like \"you should implement\", \"add this middleware\", \"create this class\", \"use <specific API>\"
- Database access details, host/port information, usernames, passwords, or client-tool suggestions

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Kebab-case GitHub repository name under 50 characters that matches the task theme and is different from the title.",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 characters, clearly describing the candidate-facing task in plain English.",
  "question": "Full candidate-facing task description explaining the business scenario, the current GraphQL and Node.js backend behavior, the specific problem to solve, and the expected scope without revealing the solution.",
  "code_files": "Object mapping each filepath to the complete file contents that should be created for the starter project, including README.md, package.json, source files, tests, and any supporting configuration files needed for a runnable local Node.js GraphQL project.",
  "answer": "Evaluator-facing high-level solution approach describing the intended architecture, key schema and resolver decisions, performance/security considerations, and what a strong intermediate-level solution should accomplish.",
  "definitions": "Object of term-to-definition pairs covering relevant Node.js and GraphQL concepts used in the task, written in simple clear language for assessment metadata.",
  "hints": "A single line nudging investigation toward a productive intermediate-level direction without revealing the fix or naming the exact implementation to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable behavior improvements, correctness, maintainability, and production-grade API quality. Use simple english.",
  "pre_requisites": "Bullet list of tools, environment, and knowledge required to complete the task, such as Node.js runtime familiarity, GraphQL schema/resolver understanding, and ability to run local tests.",
  "short_overview": "Bullet list summarising the business problem, the technical GraphQL/Node.js focus, and the expected end result in simple language."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and different from **title**.
3. **code_files** must include README.md, .gitignore, package.json, source files, and any configuration files needed for a local Node.js GraphQL project.
4. **README.md** must follow the exact structure above with these exact section names in this order: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.
5. **Starter code** must be runnable locally with native Node.js commands but must NOT contain the solution.
6. **Task must be completable within the allocated time** for INTERMEDIATE proficiency.
7. **NO comments in code** that reveal the solution or give hints.
8. **Use Node.js 18+ and modern JavaScript/TypeScript conventions throughout**.
9. **Focus on production-grade GraphQL patterns** including schema design, resolver architecture, authorization, error handling, performance awareness, and maintainability.
10. **Do NOT include Docker, docker-compose, kill.sh, or datastore configuration** unless the selected scenario explicitly requires an external service as a core part of the task.
11. **MUST NOT include environment variables or .env file references** in the generated task files.
12. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
13. The task should feel like realistic day-to-day backend work: extending an existing GraphQL API safely, debugging resolver behavior or performance issues, improving a mutation contract or error model, integrating with a legacy service module, fixing authorization gaps, reducing repeated data fetching problems, or evaluating schema evolution choices.
"""

PROMPT_REGISTRY = {
    "GraphQL (INTERMEDIATE), NodeJs (INTERMEDIATE)": [
        PROMPT_NODEJS_GRAPHQL_CONTEXT_INTERMEDIATE,
        PROMPT_NODEJS_GRAPHQL_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_NODEJS_GRAPHQL_INTERMEDIATE_INSTRUCTIONS,
    ],
}