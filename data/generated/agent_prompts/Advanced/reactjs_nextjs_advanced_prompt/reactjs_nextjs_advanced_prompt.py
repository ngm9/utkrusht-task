# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


PROMPT_REACTJS_NEXTJS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACTJS_NEXTJS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a ReactJs + NextJs assessment task.

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
- The task must be a pure local Next.js project with no external infrastructure, no Docker, no database setup, and no deployment scripts

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, frontend context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of ReactJs + NextJs implementation, refactor, debugging, testing, or optimization required, the expected deliverables, and how it aligns with ADVANCED proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACTJS_NEXTJS_ADVANCED_INSTRUCTIONS = """
# ReactJs + NextJs Advanced Task Requirements

## GOAL
As a technical architect super experienced in ReactJs and NextJs, you are given a list of real world scenarios and proficiency levels for ReactJs and NextJs. Your job is to generate an entire task definition, including TypeScript code files, README.md, expected outcomes, tests, answer, definitions, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, optimize, refactor, test, or in general solve a problem end to end at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to operate as an advanced ReactJs + NextJs engineer with 6+ years of experience. They should be able to independently reason through production-grade frontend architecture, rendering strategy, hydration behavior, state boundaries, performance trade-offs, accessibility, SEO, testing strategy, and maintainable component design.

The generated task should feel like a realistic work item in an existing product codebase rather than a trivia exercise. The project must be FULLY FUNCTIONAL and FULLY POPULATED as a local Next.js application that the candidate can run, inspect, test, and improve without repairing setup or infrastructure.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory when paths are mentioned in generated files or verification text.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement, debug, refactor, test, or optimize an existing ReactJs + NextJs TypeScript codebase.
- The task must be a pure local project using the Node.js/Next.js native package manifest and test command. It MUST NOT include docker-compose.yml, init_database.sql, kill.sh, Dockerfile, database services, cache services, queue services, or any datastore configuration.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the selected real-world scenario.
- Generate enough starter code that gives the candidate a clear, realistic starting point to begin solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct architecture, advanced React and Next.js patterns, high-quality TypeScript, robust testing, and thoughtful trade-off decisions.
- The question should be a real-world scenario and not a trick question based on syntax errors.
- **CRITICAL**: Starter code must compile, render, and test successfully before the candidate begins. Any issues in the starter code must be logical, architectural, behavioral, performance-related, accessibility-related, SEO-related, hydration-related, or maintainability-related, not setup failures.
- **CRITICAL**: The task must align with ADVANCED proficiency. It should require independent judgment around Next.js rendering strategy, React component architecture, typed data flow, state hydration, code-splitting, memoization boundaries, accessibility, SEO, error handling, testing, or performance profiling.
- **CRITICAL**: The task must remain completable within {minutes_range} minutes by an advanced candidate. Do not ask for an entire platform rewrite, a full authentication system, a full design system, micro-frontend infrastructure, production deployment, CI/CD implementation, or integration with real external services.
- Appropriate advanced task themes include:
  - Fixing a hydration mismatch or server/client boundary issue in a Next.js page or App Router flow
  - Refactoring an over-coupled page into reusable, typed, accessible React components
  - Improving performance for a data-heavy page using appropriate rendering boundaries, memoization, lazy loading, and code-splitting
  - Correcting state hydration and derived state bugs across server-rendered and client-rendered UI
  - Improving SEO and metadata behavior while preserving dynamic rendering requirements
  - Adding robust error and empty states with Error Boundaries or route-level error handling
  - Strengthening TypeScript types for complex props, API-like local data models, and reusable components
  - Adding meaningful unit and integration tests with React Testing Library for critical behavior
  - Addressing accessibility issues using semantic HTML, keyboard behavior, focus management, labels, and ARIA only where appropriate
- The task may use local mock data, static JSON files, in-memory service modules, or mocked API functions. It MUST NOT require real network credentials, real backend services, or datastore configuration.
- The task may simulate REST or GraphQL style data access through local TypeScript functions, but these must run in-process and must not require a server, database, Docker, or environment variables.
- For ADVANCED level, the questions should test deeper understanding and require candidates to demonstrate:
  - Advanced React composition patterns, reusable component design, and separation of concerns
  - Correct use of hooks, context, reducers, refs, portals, error boundaries, and memoization where appropriate
  - Next.js SSR, SSG, ISR, App Router or Pages Router behavior, route-level loading/error states, metadata, and server/client boundaries
  - Performance optimization using measurable improvements rather than premature optimization
  - TypeScript integration with complex types, interfaces, generics, discriminated unions, and strict component contracts
  - Testing with Jest and React Testing Library, including user-visible behavior and regression coverage
  - Accessibility and SEO improvements that are observable and relevant to the product scenario
  - Debugging of intricate bugs such as stale state, race conditions, unnecessary re-renders, hydration mismatches, memory leaks, or incorrect derived data
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React and Next.js best practices. Use functional components with hooks unless the selected scenario specifically requires understanding or refactoring legacy class components.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with ADVANCED proficiency (6+ years ReactJs + NextJs experience).
- TASK name should be short and under 50 characters. Use kebab-case lowercase with hyphens. Examples: "next-catalog-hydration-fix", "react-dashboard-render-tuning".

### Current Implementation vs Required Changes
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy, incomplete, inefficient, inaccessible, poorly typed, or architecturally weak state that the starter code implements.
- Examples: "The page renders local catalog data but hydration creates inconsistent filter results"; "The dashboard is functional but unnecessary re-renders make interaction sluggish"; "The metadata and semantic structure do not support the product's SEO and accessibility goals"; "The tests cover snapshots but miss the critical user-visible behavior."
- The starter code MUST perfectly implement this current implementation — no more, no less. The code must run and render, but it must exhibit exactly these issues or missing pieces. Do not accidentally fix the issues or add the solution in the starter code.

**Required Changes (what the candidate must do):**
- List the specific outcomes the candidate must achieve without prescribing the exact implementation.
- The candidate's job is only to complete these required changes on top of the current implementation.
- Required changes should be observable through application behavior, tests, performance measurements, accessibility checks, SEO metadata checks, or code quality.

**Final Implementation Approach:**
- Provide a high-level evaluator-facing description of the correct approach, including the architectural considerations and trade-offs expected from an advanced candidate.
- Do not expose this solution approach in the README or starter code.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, React documentation, Next.js documentation, TypeScript documentation, testing documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- The complexity of the tasks should reflect advanced ReactJs + NextJs proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates should be judged on correctness, maintainability, architectural judgment, testing quality, accessibility, performance awareness, and the clarity of their implementation choices.

## Code Generation Instructions
Based on real-world scenarios, create a ReactJs + NextJs task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches ADVANCED proficiency level (6+ years ReactJs + NextJs experience)
- Can be completed within {minutes_range} minutes
- Tests practical ReactJs + NextJs skills with architectural thinking and production-quality implementation
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- Creates a complete local Next.js TypeScript project that runs with the native package scripts and does not require infrastructure
- Includes a meaningful test suite that can be run with npm test and is relevant to the task requirements
- Includes local mock data, fixtures, or in-process service modules as needed for a realistic scenario
- Keeps the task scope focused enough for the time limit while still requiring advanced judgment
- Produces starter code that is FULLY FUNCTIONAL, FULLY POPULATED, and intentionally incomplete or flawed only in ways that the candidate is asked to address

The output should be a valid json schema:
- README.md
- .gitignore
- package.json
- tsconfig.json
- next.config.js or next.config.mjs
- jest.config.js
- jest.setup.ts
- src/app or src/pages files depending on the selected Next.js routing approach
- src/components files for reusable UI components
- src/lib or src/services files for local data access and business logic
- src/types files for TypeScript models and contracts
- src/__tests__ or colocated test files for Jest and React Testing Library coverage
- public files only when needed for the scenario

## Code file requirements
- Generate a realistic Next.js TypeScript project structure.
- Use either the App Router or Pages Router consistently. Do not mix routing approaches unless the task specifically concerns a migration or compatibility issue.
- Prefer App Router for modern Next.js tasks unless the selected scenario naturally calls for legacy Pages Router refactoring.
- The project must run locally using package.json scripts such as dev, build, start, test, and lint.
- The project must not require npm install commands in README instructions; package.json is enough for dependencies.
- Include all source files needed for the app to run and for tests to execute.
- Include strict TypeScript configuration and avoid any types unless the task specifically asks the candidate to remove unsafe typing.
- Starter code must be valid TSX/TS and must not contain syntax errors.
- Starter code must not include comments, TODOs, hints, or solution-revealing notes.
- Include realistic local data and fixtures that match the selected real-world scenario.
- Include tests that currently pass for the starter behavior or expose only the intended gap in a controlled way. Do not create a broken test environment.
- If candidate work includes testing, include a test harness and enough examples for them to extend without revealing the answer.
- Do not include real API keys, secrets, .env files, environment variable references, database connection strings, or external service configuration.
- Do not include docker-compose.yml, init_database.sql, run.sh, kill.sh, Dockerfile, Kubernetes files, Terraform files, or any infrastructure scripts.
- Keep file count realistic for an advanced frontend task, usually 10-18 files depending on scenario complexity.

## .gitignore INSTRUCTIONS
- Include a comprehensive .gitignore for a Next.js, React, TypeScript, Jest, and Node.js project.
- Must include node_modules, .next, out, build artifacts, coverage, logs, npm/yarn/pnpm debug logs, OS files, editor files, and local environment files.
- Do not include generated lockfiles unless they are explicitly included in code_files.
- Do not include secrets or environment-specific files.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md file content MUST be fully populated with meaningful, specific content. Content must be directly relevant to the specific ReactJs + NextJs task scenario being generated. Use concrete business context, not generic descriptions.

The README must contain these sections in this order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

Do not create a README section named "NOT TO INCLUDE in README". The "NOT TO INCLUDE in README" guidance below is for the task generator only and must not appear as a candidate-facing README section.

### Task Overview
- Task Overview must contain 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Mention that the application is already runnable and that the candidate is improving a specific product behavior or quality attribute, without revealing the implementation.

### Helpful Tips
- Helpful Tips must contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not mention exact file names, exact function names, exact component names, or exact hook usage that would reveal the solution.

### Objectives
- Objectives must contain 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should include functional correctness and may include performance, accessibility, SEO, type safety, or testing outcomes when relevant to the scenario.

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, rendered response shape, latency observation, console behavior, accessibility behavior, metadata behavior, or visual interaction result.
- Include verification that the app still builds and that relevant tests pass, but do not provide setup commands.

### NOT TO INCLUDE in README
The README must NOT include:
- Setup commands such as npm install, npm run dev, npm test, npm run build, or similar command walkthroughs
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", or "call this method"
- Database-connection details, hostnames, ports, usernames, passwords, client-tool suggestions, external service credentials, or deployment placeholders
- Docker, infrastructure, server setup, cloud deployment, or environment variable instructions

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that reflects the selected ReactJs + NextJs task scenario without revealing the solution.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, that is different from the repository name and clearly describes the work item.",
  "question": "A complete candidate-facing task description that includes the selected business scenario, Current Implementation, Required Changes, constraints, expected behavior, and completion boundaries without giving away the solution.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content using only the required README sections Task Overview, Helpful Tips, Objectives, and How to Verify, with concise and non-revealing guidance.",
    ".gitignore": "A comprehensive ignore file for a local Next.js, React, TypeScript, Jest, and Node.js project, including dependencies, build artifacts, coverage, logs, editor files, OS files, and local environment files.",
    "package.json": "A valid package manifest for a local Next.js TypeScript project with dependencies and scripts for development, production build, start, linting, and tests using the native Node.js workflow.",
    "tsconfig.json": "A strict TypeScript configuration suitable for a modern Next.js React application with JSX, module resolution, path aliases if used, and no unsafe defaults.",
    "next.config.js": "A minimal valid Next.js configuration file only when needed for the selected task, without environment variables or infrastructure configuration.",
    "jest.config.js": "A valid Jest configuration for testing React and Next.js TypeScript code with jsdom and appropriate setup files.",
    "jest.setup.ts": "A test setup file that configures testing-library matchers or safe mocks needed by the starter test suite.",
    "src/app/page.tsx": "The primary route or page file for an App Router based task, containing runnable starter UI that reflects the current implementation but not the required solution.",
    "src/app/layout.tsx": "The root layout file for an App Router based task with valid metadata or layout structure appropriate to the scenario.",
    "src/pages/index.tsx": "The primary page file only if the task uses Pages Router instead of App Router, containing runnable starter UI that reflects the current implementation but not the required solution.",
    "src/components/ComponentName.tsx": "Reusable React component files with TypeScript props and realistic starter behavior that may require refactoring, optimization, accessibility improvements, or testing.",
    "src/lib/moduleName.ts": "Local utility, data access, or business logic modules using in-process mock data or fixtures only, with typed exports and no external services.",
    "src/types/domain.ts": "TypeScript domain model definitions, interfaces, unions, or generic types used by the application and relevant to the task.",
    "src/__tests__/feature.test.tsx": "Jest and React Testing Library tests that validate important user-visible behavior or provide a harness the candidate can extend without exposing the solution.",
    "public/asset-file": "Static assets only when the selected scenario genuinely needs them, with contents or descriptions that support the local application."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the expected architectural decisions, React and Next.js concepts, TypeScript changes, testing strategy, and trade-offs without requiring one exact implementation.",
  "definitions": "An object of term-to-definition pairs for important ReactJs, NextJs, TypeScript, testing, accessibility, SEO, or performance terminology used in the task, with concise plain-English definitions.",
  "hints": "A single line nudging investigation toward the right area of the code or behavior without revealing the specific fix, API, pattern, or implementation.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable user-visible behavior, maintainability, testability, accessibility, SEO, or performance improvements. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed for the task, including Node.js 18+, npm or yarn, Git, advanced ReactJs, advanced NextJs, TypeScript, testing, performance, accessibility, and local frontend debugging knowledge.",
  "short_overview": "A bullet list summarising the business problem, the technical focus of the ReactJs + NextJs work item, and the expected outcome for the product or engineering team."
}}

## CRITICAL REMINDERS
1. **Environment must be fully working** — The project must run perfectly with the native Next.js package scripts; zero setup errors; the candidate does NOT fix the environment, only the requested task.
2. **Starter code must be runnable** and must NOT contain the core logic solution.
3. **Starter code must perfectly match the Current Implementation** described in the question.
4. **NO comments** that reveal solutions, TODOs, hints, or placeholder implementation guidance.
5. **Task must be completable within {minutes_range} minutes** by an advanced ReactJs + NextJs candidate.
6. **Focus on advanced ReactJs + NextJs concepts** appropriate for 6+ years of experience.
7. **Use TypeScript throughout** with strict and meaningful types.
8. **Code files MUST NOT contain** implementation for the core logic the candidate must implement.
9. **README.md MUST be fully populated** with meaningful, task-specific content and must remain concise.
10. **README.md MUST NOT include setup commands, direct solutions, step-by-step guides, or solution-revealing API names.**
11. **Do not create a candidate-facing README section named "NOT TO INCLUDE in README"; that guidance is only for generation quality control.**
12. **.gitignore** must cover standard Next.js, React, TypeScript, Jest, and Node.js exclusions.
13. **Task name** must be short, descriptive, under 50 characters, kebab-case.
14. **Use the provided real-world scenario as the basis for this task - do not invent a different domain.**
15. **Do not include Docker, docker-compose.yml, init_database.sql, run.sh, kill.sh, Dockerfile, database setup, cache setup, queue setup, cloud deployment, environment variables, or external service credentials.**
16. **The output JSON must include exactly the required canonical keys**: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, and short_overview.
17. **All braces in JSON-like content inside generated files must be valid for the final code contents and must not break JSON serialization.**
"""

PROMPT_REGISTRY = {
    "NextJs (ADVANCED), ReactJs (ADVANCED)": [
        PROMPT_REACTJS_NEXTJS_ADVANCED_CONTEXT,
        PROMPT_REACTJS_NEXTJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_REACTJS_NEXTJS_ADVANCED_INSTRUCTIONS,
    ]
}