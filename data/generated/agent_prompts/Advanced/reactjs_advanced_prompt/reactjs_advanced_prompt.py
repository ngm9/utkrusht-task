PROMPT_REACTJS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACTJS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of React implementation, refactor, debugging, or optimization work required, the expected deliverables, and how it aligns with ADVANCED proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACTJS_ADVANCED_INSTRUCTIONS = """
# React Advanced Task Requirements

## GOAL
As a technical architect super experienced in React, you are given a list of real world scenarios and proficiency levels for React. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and evaluator guidance, that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, optimize, refactor, or in general solve a problem end to end at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION
- The candidate is an ADVANCED React professional expected to independently own complex front-end features and application flows.
- The task should reflect realistic product engineering work in a modern React codebase, not toy exercises or syntax quizzes.
- The candidate should receive a FULLY FUNCTIONAL and FULLY POPULATED local project with realistic starter code, meaningful data fixtures, and enough surrounding structure to reason about architecture and tradeoffs.
- The candidate is expected to demonstrate strong judgment around component architecture, state ownership, rendering performance, maintainability, resilience, accessibility awareness, and pragmatic delivery.
- The employer context comes from `organization_background`, but the actual business domain for the task must come from one selected scenario in `real_world_task_scenarios`.
- The task must be completable within {minutes_range} minutes by a candidate with ADVANCED React proficiency.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a non-trivial feature, refactor an existing flow, fix a complex bug, optimize rendering and data flow, or improve architecture in an existing React application.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, and domain details are historically accurate and relevant to the selected scenario.
- Generate enough starter code that gives the candidate a strong starting point to begin solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate make sound architectural decisions, not just patch symptoms.
- The question should be a real-world scenario that tests architectural thinking, debugging depth, performance reasoning, and maintainability.
- The complexity of the task and specific ask expected from the candidate must align with ADVANCED proficiency level, ensuring that no two questions generated are similar.
- For ADVANCED level, the questions should require candidates to demonstrate several of the following in a realistic but bounded way:
  - advanced state ownership and synchronization decisions using React Hooks, Context API, or reducer-based patterns
  - refactoring legacy or fragmented component logic into scalable, maintainable structures
  - performance optimization using memoization, stable callbacks, derived state control, lazy boundaries, or render isolation where appropriate
  - debugging race conditions, stale UI, memory leaks, unmounted updates, or inconsistent state across related views
  - designing reusable component boundaries, compound patterns, or shared abstractions without overengineering
  - robust error handling using error boundaries, resilient UI states, and partial-failure behavior
  - strong TypeScript integration with meaningful interfaces, unions, generics, and safe component contracts
  - testing meaningful behavior with unit and integration coverage using React Testing Library and Jest
  - accessibility-conscious implementation and verification for interactive UI
- **CRITICAL**: Stay within React competency scope. Do not make the task primarily about backend implementation, infrastructure setup, authentication server design, GraphQL server work, Next.js SSR, micro-frontends, CI/CD, or external platform configuration unless they are only incidental context.
- **CRITICAL**: The task must remain a pure frontend/local React assessment. Do not require Docker, databases, external services, or remote infrastructure.
- **CRITICAL**: The starter project must run locally and cleanly. The candidate should solve the React problem, not repair the environment.
- **CRITICAL**: The question must NOT include hints. Hints belong only in the `hints` field.
- **CRITICAL**: Use functional components with hooks for the main implementation. Legacy class components may exist only if the scenario explicitly involves refactoring or interoperability.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with ADVANCED proficiency.
- TASK name should be short and under 50 characters. Use kebab-case.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, React documentation, TypeScript documentation, browser documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- The complexity of the tasks should reflect advanced React proficiency while still requiring genuine engineering judgment that goes beyond simple copy-pasting from a generative AI.
- Candidates should be evaluated on the quality of the final solution, correctness, maintainability, reasoning, and tradeoff handling.

## Code Generation Instructions
- Based on real-world scenarios, create a React task that draws inspiration from the input scenarios for business context and technical requirements.
- Match ADVANCED proficiency by focusing on realistic architectural, debugging, optimization, and maintainability challenges in a modern React application.
- The project should be a local web application using React and TypeScript.
- Prefer a single-page or small multi-view application with enough moving parts to expose advanced React reasoning without requiring backend infrastructure.
- The task should include realistic starter code that is functionally runnable but contains architectural issues, performance problems, state synchronization flaws, or incomplete advanced behavior that the candidate must address.
- The generated task should feel like a real work item from a production codebase.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## Infrastructure Requirements

### Docker-compose Instructions
- Do NOT include `docker-compose.yml` for this task.
- **CRITICAL**: This is a pure local React task with no external service requirement.
- **MUST NOT include any version specification** because docker-compose must not exist for this task.
- **MUST NOT include environment variables or .env file references**.
- The candidate should run the project locally using the native React toolchain only.

### init_database.sql Instructions
- Do NOT include `init_database.sql` or any datastore configuration.
- Do NOT require Redis, PostgreSQL, Firebase, queues, brokers, or any external service.
- Use local mock data, in-memory modules, or static JSON fixtures if the scenario needs realistic data.

### Run.sh Instructions
- `run.sh` is optional for this task shape.
- Prefer not to include `run.sh`; the candidate should use the runtime's native commands from `package.json`.
- If you include `run.sh`, it must only wrap local frontend commands and must not install the runtime or common libraries.
- Do not include `apt-get install`, `npm install`, or any infrastructure bootstrapping in `run.sh`.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## kill.sh file instructions
- Do NOT include `kill.sh` for this task.
- This task does not use Docker containers, volumes, networks, or remote infrastructure.
- Cleanup should not be part of the generated files for this pure frontend assessment.

### Dockerfile Instructions
- Do NOT include a Dockerfile for this task.
- The project must run as a local React application using the native package manifest and scripts.

The output should be a valid json schema:
- `README.md` — candidate-facing task description following the required README structure below
- `.gitignore` — standard React, TypeScript, Node.js, coverage, and editor exclusions
- `package.json` — project manifest with dependencies and scripts required to run, build, and test the React application locally
- `tsconfig.json` — TypeScript configuration suitable for a React application
- `public/index.html` — HTML entry point for the web application
- `public/manifest.json` — standard web app manifest
- `public/robots.txt` — standard robots file
- `src/index.tsx` — React application entry point
- `src/App.tsx` — main application shell
- `src/react-app-env.d.ts` — React environment type declarations if needed by the chosen setup
- `src/types.ts` — shared domain and UI type definitions
- `src/data/*.ts` or `src/data/*.json` — local mock data or fixtures if needed by the scenario
- `src/components/*.tsx` — reusable UI components
- `src/pages/*.tsx` or `src/screens/*.tsx` — page-level components if the scenario needs multiple views
- `src/context/*.tsx` — context providers if the scenario requires shared state
- `src/hooks/*.ts` — custom hooks for reusable stateful logic
- `src/utils/*.ts` — utility helpers, formatters, selectors, or caching helpers
- `src/services/*.ts` — local data access abstractions if needed
- `src/__tests__/*.test.tsx` — meaningful unit or integration tests aligned to the task
- additional source files as needed to create a realistic, runnable project

## Code file requirements
- The starter code MUST be a complete, working React + TypeScript application that runs successfully immediately after dependency installation using the native package scripts.
- ZERO compilation errors, ZERO runtime errors, and no intentionally broken imports or syntax.
- All code files MUST use TypeScript where appropriate: `.tsx` for components and `.ts` for utilities and types.
- Include a valid `tsconfig.json`.
- Include proper type definitions for props, state, domain models, async results, and function parameters.
- Avoid `any` unless absolutely unavoidable; prefer explicit types, unions, interfaces, and generics where they add clarity.
- The starter code must be realistic and sufficiently populated, but it must NOT already contain the full solution.
- If the task is about fixing bugs or refactoring, the starter code must perfectly implement the problematic current state described in the question.
- If the task is about optimization, the code must be functionally correct but architecturally or performance-wise flawed in ways appropriate for advanced React work.
- If the task is about state synchronization or resilience, the code must expose those issues through realistic component interactions.
- Include tests, but do not fully encode the solution in the tests. Tests should validate important observable behavior while still leaving room for implementation decisions.
- Do NOT include comments of any kind that reveal the solution: no TODOs, no hints, no placeholder guidance.
- Prefer React 18+ patterns and modern testing practices.
- The project structure should be realistic and maintainable, not artificially minimal.

## .gitignore INSTRUCTIONS
- Include a comprehensive `.gitignore` for a React + TypeScript project.
- Ignore `node_modules`, build output, coverage output, cache directories, editor files, OS files, logs, and temporary files.
- Ignore `.DS_Store`, `dist`, `build`, `coverage`, `.cache`, `.idea`, `.vscode`, `npm-debug.log*`, `yarn-debug.log*`, `yarn-error.log*`.
- Do not rely on `.env` files or environment-variable-driven setup for this task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

### Task Overview
- This section is MANDATORY and must NEVER be empty.
- Write 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, the current state of the React application, and why the problem matters.
- Keep it specific to the selected real-world scenario.
- Do not include setup commands.
- Do not include direct implementation instructions.
- Do not include bold time-budget callouts.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with one of: `Consider`, `Think about`, `Explore`, `Review`, `Analyze`.
- Tips must guide discovery and investigation.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Good tips focus on state ownership, rendering behavior, failure handling, user experience consistency, and maintainability without prescribing the exact fix.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step.
- Focus on business correctness, UI consistency, resilience, performance, maintainability, and code quality appropriate for an advanced React task.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run through the UI, tests, or observable application behavior.
- Verification can mention response consistency, render stability, preserved UI state, visible fallback behavior, test results, or absence of warnings/errors.

### NOT TO INCLUDE in README
- Setup commands such as `npm install`, `npm start`, `npm test`, `yarn install`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Hostnames, ports, usernames, passwords, database access details, or any `<DROPLET_IP>` placeholders

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that matches the React task scenario.",
  "title": "A human-readable display name in '<action verb> <subject>' format, between 50 and 80 characters, clearly different from the repository name.",
  "question": "The full candidate-facing task description describing the business scenario, current implementation state, required outcomes, constraints, and what makes the problem important, without including hints that reveal the solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README that follows the exact required section names and ordering, stays open-ended, and provides scenario-specific guidance without revealing the implementation.",
    ".gitignore": "A complete ignore file for a local React and TypeScript project covering dependencies, build artifacts, coverage, logs, caches, editor files, and OS-generated files.",
    "package.json": "A valid project manifest describing the local React application dependencies, scripts, and metadata needed to run, build, and test the task.",
    "tsconfig.json": "A valid TypeScript configuration file appropriate for a React application with strict and practical compiler settings.",
    "public/index.html": "The HTML entry point used to mount the React application in the browser.",
    "public/manifest.json": "A standard web application manifest file for the React project.",
    "public/robots.txt": "A standard robots file included so the project structure is complete and runnable.",
    "src/index.tsx": "The React entry point that mounts the application and wires any top-level providers required by the starter code.",
    "src/App.tsx": "The main application shell that composes the primary page flow and reflects the current incomplete or problematic implementation state.",
    "src/react-app-env.d.ts": "Environment type declarations if required by the chosen React and TypeScript setup.",
    "src/types.ts": "Shared domain, UI, and state type definitions used across the project to keep contracts explicit and maintainable.",
    "src/data/mockData.ts": "Local mock data or fixtures that simulate realistic business inputs without requiring any external service.",
    "src/components/ComponentName.tsx": "Reusable presentational or container components that participate in the task scenario and expose the intended architectural or behavioral issues.",
    "src/pages/PageName.tsx": "Page-level components that coordinate the user flow and make the scenario feel like a realistic product surface.",
    "src/context/ContextName.tsx": "Shared state providers if the scenario requires cross-component coordination or a single source of truth.",
    "src/hooks/useSomething.ts": "Custom hooks that encapsulate reusable stateful logic and may intentionally need refactoring, hardening, or optimization.",
    "src/utils/helper.ts": "Utility helpers, selectors, formatters, or local caching helpers used by the application.",
    "src/services/localApi.ts": "A local data access abstraction that simulates asynchronous behavior, latency, or partial failures without relying on a backend.",
    "src/__tests__/feature.test.tsx": "Meaningful tests that validate observable behavior and important edge cases without fully prescribing the implementation.",
    "additional_file.tsx": "Any additional source file needed to make the project realistic, runnable, and aligned with the selected scenario."
  }},
  "answer": "A high-level evaluator-facing solution approach describing the intended architecture, reasoning, tradeoffs, and major fixes or improvements expected from a strong advanced React candidate.",
  "definitions": "An object of term-to-definition pairs that explains important React, TypeScript, UI, or product terms referenced in the task using simple and accurate language.",
  "hints": "A single line nudging investigation toward the right problem area without revealing the exact fix, APIs, or implementation pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements in correctness, consistency, resilience, maintainability, and React rendering behavior. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed to attempt the task, such as Node.js, npm or yarn, Git, React, TypeScript, and familiarity with debugging and testing frontend applications.",
  "short_overview": "A bullet list summarising the business problem, the technical focus of the React task, and the expected end-state after a successful solution."
}}

## CRITICAL REMINDERS
1. The task must be a pure local React assessment with no Docker, no compose, no database, no remote services, and no infrastructure setup burden.
2. The starter project must be FULLY FUNCTIONAL and runnable locally using the native package scripts.
3. The task must be inspired by exactly ONE real-world scenario from the provided scenarios.
4. The task must align with ADVANCED React proficiency and test architectural judgment, debugging depth, performance reasoning, and maintainability.
5. Stay within the React competency scope and do not make unrelated technologies the primary skill under assessment.
6. The starter code must not contain comments, TODOs, or hints that reveal the solution.
7. The README must use these exact section names in this exact order: Task Overview, Helpful Tips, Objectives, How to Verify, NOT TO INCLUDE in README.
8. The README must be concise and open-ended, and must not contain setup commands or direct implementation instructions.
9. The output JSON schema descriptions must be verbose one-sentence descriptions, not placeholder examples.
10. The repository `name` must be kebab-case and under 50 characters.
11. The `title` must be human-readable, 50-80 characters, and in "<action verb> <subject>" format.
12. Use TypeScript for the project and include meaningful tests appropriate for a frontend React task.
13. Ensure the task is realistically completable within {minutes_range} minutes by an advanced candidate.
"""

PROMPT_REGISTRY = {
    "ReactJs (ADVANCED)": [
        PROMPT_REACTJS_ADVANCED_CONTEXT,
        PROMPT_REACTJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_REACTJS_ADVANCED_INSTRUCTIONS,
    ]
}