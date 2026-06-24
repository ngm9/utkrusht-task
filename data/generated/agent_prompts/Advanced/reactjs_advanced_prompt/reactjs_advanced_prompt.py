# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


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

ADDITIONAL SKILL CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of React implementation, refactor, optimization, or bug-fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACTJS_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in React and the modern JavaScript ecosystem, you are given a list of real world scenarios and proficiency levels for React development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION
- The candidate is being assessed for ADVANCED React proficiency and should be treated as someone with 6+ years of hands-on React experience.
- The task should reflect the level of ownership expected from a senior engineer who can independently design, refactor, debug, optimize, and evolve complex front-end flows with minimal guidance.
- The candidate should be expected to reason about component boundaries, state flow, rendering behavior, maintainability, accessibility, asynchronous UI behavior, performance tradeoffs, and user-facing correctness.
- The assessment must reward strong technical judgment, not just code output.
- The starter project must feel like a realistic production codebase snapshot rather than a toy demo.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor an existing codebase area, fix complex bugs, improve architecture, or optimize problematic rendering and state management behavior in an existing React application.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a strong starting point to begin solving the task while still preserving substantial engineering decisions for the candidate to make.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just patch symptoms.
- The question should be a real-world scenario that tests architectural thinking and not just implementation mechanics.
- The complexity of the task and specific ask expected from the candidate must align with ADVANCED proficiency level, ensuring that no two questions generated are similar.
- For ADVANCED level of proficiency, the questions should test deeper understanding and require candidates to demonstrate several of the following in a natural way, but only when they fit the chosen scenario:
  - Advanced component composition and reusable UI architecture
  - Context design, reducer-driven state transitions, and pragmatic state ownership decisions
  - Performance optimization using memoization, render isolation, lazy loading, and bundle-aware decisions
  - Complex hooks usage and debugging of stale closures, effect dependencies, race conditions, or memory leaks
  - Error boundaries, graceful degradation, and production-ready failure handling
  - Accessibility and keyboard interaction considerations
  - Type-safe React design using TypeScript types, interfaces, and generics
  - Refactoring of legacy or overly coupled component structures into maintainable modules
  - Tradeoff analysis between readability, extensibility, performance, and developer ergonomics
  - Thoughtful API integration patterns, loading behavior, and user experience under asynchronous conditions
- **CRITICAL**: The task must stay within React competency scope. Do not turn it into a backend, infrastructure, authentication server, CI/CD, or database administration task.
- **CRITICAL**: The task must be a pure local React/runtime task. It MUST NOT require docker-compose.yml, init_database.sql, kill.sh, Redis configuration, database setup, or any other external service configuration.
- **CRITICAL**: Because external resources and AI tools are allowed, the task must require genuine engineering judgment, debugging, or architectural reasoning that goes beyond simple copy-pasting.
- **CRITICAL**: The task must be completable within {minutes_range} minutes by an advanced React candidate.
- **CRITICAL**: Use modern React 18+ practices and current JavaScript/TypeScript standards. Use functional components with hooks exclusively.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The scenario should feel like a production issue or enhancement request where the candidate must understand constraints, inspect the codebase, and decide how to improve it.
- Generate a FULLY FUNCTIONAL and FULLY POPULATED starter environment that runs locally with the runtime's native manifest and test command.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, React documentation, MDN, browser documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect advanced React proficiency while requiring genuine engineering, architectural, debugging, and tradeoff analysis skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches, identify risks, and choose the most appropriate solution under realistic constraints.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a React task that:
- Draws inspiration from the input scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for ADVANCED proficiency level, keeping in mind that AI assistance is allowed
- Tests practical React skills that require architectural thinking, debugging depth, performance considerations, maintainability improvements, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- Focus on multi-component applications that require thoughtful state management and component communication
- Should test the candidate's ability to structure or improve a scalable React application
- Should include enough realistic starter code for the candidate to inspect existing behavior and make non-trivial decisions
- Prefer TypeScript-based React projects for advanced tasks unless the chosen scenario strongly justifies plain JavaScript
- Include a small but meaningful automated test surface when appropriate so the candidate can validate behavior locally, but do not make the task primarily about test authoring
- The code files generated must be valid and executable with the runtime's native local commands through package.json
- The starter project should include realistic modules such as components, hooks, context, utilities, and tests where relevant

## Infrastructure Requirements

### Docker-compose Instructions
- This is a pure local non-infrastructure React task.
- **CRITICAL**: DO NOT generate docker-compose.yml.
- **CRITICAL**: DO NOT reference Docker, containers, services, or host-exposed ports.
- **CRITICAL**: Because this task is non_infra, the project must run directly from package.json scripts using the local runtime only.
- **CRITICAL**: **MUST NOT include any version specification** because docker-compose.yml must not exist at all for this task.

### React Local Project Instructions
- Use a native local React project manifest such as package.json.
- The project must be runnable and testable with native package scripts only.
- Prefer a modern local setup appropriate for advanced React work, such as Vite with React and TypeScript, unless the scenario clearly benefits from another standard React local setup.
- Include scripts necessary to run the project and run tests locally.
- **MUST NOT include environment variables or .env file references** unless they are absolutely unavoidable for the chosen scenario, and in normal cases they should not be used.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

### Run.sh Instructions
- For this non_infra React task, run.sh is optional.
- If you choose to include run.sh, it must only use package.json scripts for local execution and testing.
- It MUST NOT install the runtime itself and MUST NOT use apt-get, pip install, npm install of the runtime, Docker, or docker compose commands beyond what a standard local React project already requires through package.json.
- If included, run.sh should simply change into /root/task and run the appropriate local verification command such as the test script or build script.
- The task should still be fully workable even if the candidate uses the native commands directly from package.json instead of run.sh.

## kill.sh file instructions
- **CRITICAL**: DO NOT generate a kill.sh file for this task.
- This task is non_infra and must not include cleanup logic for containers, volumes, networks, images, or docker system prune commands.
- Do not mention docker compose down, container cleanup, volume cleanup, or infrastructure teardown in the generated task output.
- The output JSON must not contain a kill.sh entry in code_files.

### Dockerfile Instructions
- DO NOT generate a Dockerfile for this task.
- The task must be solved as a local React project using native package scripts only.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - package.json (Node.js manifest with scripts and dependencies required for the React task)
  - .gitignore (Standard React project gitignore)
  - tsconfig.json or jsconfig.json (depending on whether the generated project uses TypeScript or JavaScript)
  - vite.config.ts / vite.config.js or equivalent local bundler config if needed by the chosen setup
  - public/index.html or index.html depending on the chosen local React setup
  - Source files under src/ that provide a realistic but incomplete or flawed starting point
  - Optional test files if they help verify behavior
  - Code files should demonstrate partial architecture that candidate needs to complete, improve, debug, or refactor
  - Include realistic folder structure such as src/components/, src/hooks/, src/context/, src/utils/, src/types/, src/features/, src/test/ when relevant
  - **CRITICAL**: Do NOT include docker-compose.yml, init_database.sql, kill.sh, Dockerfile, or any datastore configuration files

## Code file requirements
- Generate a realistic folder structure for an advanced React project.
- Code should follow modern React best practices and demonstrate advanced-level patterns without giving away the final solution.
- Use functional components with hooks exclusively.
- Focus on current React and TypeScript/JavaScript best practices.
- **CRITICAL**: The generated code files should provide partial implementations, flawed architecture, missing behavior, or realistic bugs that require advanced-level reasoning to complete correctly.
- Include existing components, hooks, providers, utilities, or tests that the candidate needs to work with, extend, optimize, debug, or refactor.
- The core architectural decisions, state management improvements, performance optimizations, error handling strategy, accessibility improvements, or composition patterns that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT add comments like "Add optimization here" or "Should implement custom hook" etc.
- The generated project structure should be runnable, but it must still require meaningful engineering work to satisfy the task.
- Use dependencies that an advanced React engineer should reasonably be familiar with if they are required by the scenario, but do not overload the project with unnecessary libraries.
- Prefer clean, production-like starter code over artificially broken code.
- If tests are included, they should verify outcomes without revealing the exact implementation strategy.
- The task should not depend on any real external API. Use local mock data, local adapters, or in-project fake services if async flows are needed.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for advanced React projects including node_modules, dist/build directories, coverage output, environment files, log files, IDE configurations, OS artifacts, TypeScript build info, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections, in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

### Task Overview
- **CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences. No bullet list.
- It must describe the business scenario, current state of the application, and why the problem matters.
- It must NEVER be empty.
- It must use concrete, task-specific context from the selected scenario.
- It must not contain bold time-budget callouts.
- It must not reveal the implementation approach.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Include 4-5 bullets max.
- Each bullet must start with one of these action words: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips should guide discovery and investigation.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Keep tips aligned with advanced React concerns such as state boundaries, rendering behavior, user experience, resilience, maintainability, and edge cases.

### Objectives
- Include 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step, API choice, or library instruction.
- Focus on functional correctness, maintainability, performance, accessibility, resilience, and clarity of behavior as appropriate to the scenario.

### How to Verify
- Include 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run or observe, such as UI behavior, response shape, test output, rendering stability, loading/error behavior, accessibility behavior, or performance observation.
- Keep verification specific enough to be measurable without prescribing the design.

### NOT TO INCLUDE in README
The README must explicitly forbid the following:
- Setup commands (e.g. npm install, npm run dev, npm test, docker compose up, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Hostnames, ports, usernames, passwords, datastore access instructions, or any connection details
- Any mention of Docker, docker-compose, init_database.sql, or kill.sh for this task

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "Fill this with a short kebab-case GitHub repository name under 50 characters that matches the React task scenario and is different from the title.",
  "title": "Fill this with a human-readable display title in the format '<action verb> <subject>', between 50 and 80 characters, and clearly distinct from the name field.",
  "question": "Fill this with the full candidate-facing task description, including the business scenario, current application state, expected outcome, scope boundaries, and any constraints the candidate must respect, without adding solution hints.",
  "code_files": {{
    "README.md": "Fill this with a concise, fully populated candidate-facing README that follows the exact required section names and order described above.",
    ".gitignore": "Fill this with a comprehensive gitignore for a local React project covering dependency folders, build artifacts, editor files, logs, coverage output, and OS-specific files.",
    "package.json": "Fill this with the project manifest containing the task-specific name, scripts, dependencies, and devDependencies needed to run and verify the local React project.",
    "tsconfig.json": "Fill this with TypeScript compiler configuration if the project uses TypeScript, tuned for a local React application and appropriate test/build tooling.",
    "vite.config.ts": "Fill this with the local bundler configuration if the project uses Vite and TypeScript, containing only what is necessary for the task to run.",
    "index.html": "Fill this with the local HTML entry point if the chosen setup expects a root-level index.html file.",
    "public/index.html": "Fill this with the public HTML entry point only if the chosen local setup uses a public directory instead of a root-level index.html file.",
    "src/main.tsx": "Fill this with the React application bootstrap file if using TypeScript and a Vite-style entry point.",
    "src/index.tsx": "Fill this with the React application bootstrap file if using a setup that expects an index-based TypeScript entry point.",
    "src/App.tsx": "Fill this with the main application component that wires together the existing starter architecture without containing the full solution.",
    "src/components/ExampleComponent.tsx": "Fill this with a realistic component file that is relevant to the chosen scenario and provides meaningful starter behavior or existing flaws.",
    "src/hooks/useExample.ts": "Fill this with a realistic custom hook file when the task needs reusable state or async logic in starter form.",
    "src/context/ExampleContext.tsx": "Fill this with a realistic context/provider module when the task requires shared client-side state in the starter code.",
    "src/utils/example.ts": "Fill this with utility logic that supports the scenario without revealing the final implementation strategy.",
    "src/types/example.ts": "Fill this with task-relevant types, interfaces, or shared domain models when TypeScript is used.",
    "src/test/example.test.tsx": "Fill this with optional verification tests that check observable behavior without prescribing the exact solution.",
    "additional_relevant_file_path": "Fill this with any other source file contents needed to create a realistic, runnable, advanced React starter project for the scenario."
  }},
  "answer": "Fill this with an evaluator-facing high-level explanation of the intended solution approach, including key architectural decisions, tradeoffs, and what strong advanced-level submissions should demonstrate.",
  "definitions": {{
    "term_or_phrase_1": "Fill this with a short, task-relevant definition that clarifies a business or technical term used in the prompt.",
    "term_or_phrase_2": "Fill this with another short, task-relevant definition that helps the candidate understand the scenario wording without giving away the solution."
  }},
  "hints": "Fill this with a single-line nudge that points the candidate toward the right investigation area without revealing the exact fix or architecture.",
  "outcomes": "Fill this with 2-3 lines describing the measurable results expected after completion, focusing on observable user-facing behavior, maintainability improvements, or rendering/performance/resilience outcomes in simple English.",
  "pre_requisites": "Fill this with a bullet list of tools, local runtime knowledge, and React/TypeScript experience needed to work on the project using standard local package scripts.",
  "short_overview": "Fill this with a bullet list summarising the business problem, the technical focus of the task, and the expected end result in concise language."
}}

## CRITICAL REMINDERS
1. The task MUST be inspired by exactly one of the provided real-world scenarios and should closely align with that scenario's domain and constraints.
2. The task MUST target ADVANCED React proficiency and should expect strong architectural, debugging, optimization, and code-quality judgment.
3. The project MUST be FULLY FUNCTIONAL and FULLY POPULATED as a local React project.
4. The candidate must not need to repair broken setup before starting the actual task.
5. Use package.json as the native manifest and keep the project runnable with standard local scripts.
6. Because this task is non_infra, DO NOT include docker-compose.yml, init_database.sql, kill.sh, Dockerfile, or any datastore configuration.
7. The starter code must not contain the completed solution, direct hints, TODOs, or comments that reveal the answer.
8. The task question must not include hints.
9. The README.md MUST be fully populated, concise, task-specific, and use the exact required section names in the exact required order.
10. The output JSON schema must use the exact canonical keys: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, short_overview.
11. Keep the business problem realistic and high-signal, not academic or contrived.
12. The task should be challenging but realistically solvable within {minutes_range} minutes by an advanced React engineer using external resources if desired.
13. Use functional components with hooks exclusively and align with modern React 18+ practices.
14. If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
15. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
"""

PROMPT_REGISTRY = {
    "ReactJs (ADVANCED)": [
        PROMPT_REACTJS_ADVANCED_CONTEXT,
        PROMPT_REACTJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_REACTJS_ADVANCED_INSTRUCTIONS,
    ]
}