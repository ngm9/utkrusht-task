PROMPT_NEXTJS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_NEXTJS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a ADVANCED assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must be an open-ended design-and-build or debugging-and-optimization task with real trade-offs.
- It must be completable within {minutes_range} minutes by a candidate with 5+ years of experience.
- The task should assess advanced Next.js judgment across rendering strategy, routing, performance, reliability, and maintainability.

Briefly confirm your understanding:
1. What will the task be about {{domain, context, problem}}?
2. What will the candidate build, fix, refactor, or optimize, and how does it match ADVANCED level?
"""

PROMPT_NEXTJS_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Next.js, you are given a list of real world scenarios and proficiency levels for Next.js.
Generate a complete assessment task that evaluates a candidate at ADVANCED proficiency through a realistic, production-style Next.js work sample. The task must result in a FULLY FUNCTIONAL local project with runnable starter code, clear candidate instructions, and evaluator-facing guidance.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to be an experienced engineer who can independently design, debug, optimize, and harden production-grade Next.js applications. The task should reflect advanced ownership of routing strategy, rendering mode decisions, data-fetching patterns, performance tuning, authentication and security considerations, testing, and maintainability.

The generated task must feel like a real engineering assignment from an existing codebase rather than a toy exercise. The candidate should need to reason about trade-offs, diagnose issues from current behavior, and implement a robust solution without being told the exact implementation steps.

## INSTRUCTIONS
### Nature of the Task
- Create an ADVANCED-level Next.js task appropriate for a candidate with 5+ years of experience.
- The task MUST be based on ONE selected real-world scenario from the provided scenario list.
- The task MUST be a realistic work-sample task where the candidate fixes, refactors, extends, secures, or optimizes an existing Next.js application.
- The task MUST stay within the provided competency scope for Next.js ADVANCED. This includes advanced routing, SSR/SSG/ISR decisions, performance optimization, caching strategy, secure authentication flows, server/client state boundaries, backend integration, testing, scalability, and maintainability.
- **CRITICAL**: Do NOT require skills outside the natural scope of advanced Next.js work. Avoid unrelated infrastructure-heavy platform engineering, unrelated database administration, or non-Next.js domain-specialist work as the primary challenge.
- **CRITICAL**: The task should test applied engineering judgment, not trivia or framework syntax recall.
- **CRITICAL**: The task must be completable within {minutes_range} minutes by a strong advanced candidate.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL and runnable as provided, while still containing the intended bug, limitation, or incomplete implementation.
- The task should require the candidate to understand the current implementation, identify the root causes of the observed issues, and implement a production-appropriate solution.
- Prefer scenarios involving one or more of the following, as long as they are grounded in the selected scenario: App Router or Pages Router behavior, server versus client component boundaries, concurrent data fetching, caching and revalidation, route protection, hydration correctness, SEO-sensitive rendering choices, partial failure handling, performance bottlenecks, or test coverage for critical flows.
- Include realistic acceptance criteria in the question so the candidate knows the expected outcomes, but do NOT reveal the exact implementation approach.
- The task name must be short, under 50 characters, and kebab-case.
- For executable code, always invoke tools by their explicit command names.
- The generated codebase should use the runtime's native project shape for Next.js and should run locally without requiring external services.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Next.js documentation, React documentation, testing documentation, and AI-powered tools, agentic IDEs, or Large Language Models {{LLMs}}.

This task is designed to assess the candidate's ability to work effectively in a modern engineering environment. Therefore:
- They may search for documentation, examples, and best practices.
- They may use AI tools to help reason about the problem, investigate errors, or draft code.
- They must still produce a working, coherent, and reviewable solution themselves.
- The evaluation is based on the quality, correctness, and completeness of the final deliverable, not on whether external help was used.

## Code Generation Instructions
- Generate a local Next.js project structure appropriate for an advanced assessment.
- The project must include enough starter code to make the current behavior concrete and reproducible.
- The starter code must reflect the exact "Current Implementation" described in the candidate-facing question.
- Do NOT include solution code, TODO markers, or comments that reveal the intended fix.
- The code should be realistic and maintainable, with multiple files where appropriate, but still scoped to the time limit.
- Include tests that run in the local project and validate the intended behavior boundaries. The tests may initially fail if they represent missing or broken functionality the candidate must fix.
- The task should naturally exercise advanced Next.js concepts such as rendering strategy, route behavior, caching, middleware, server/client boundaries, error handling, and testing.
- If authentication or security is part of the selected scenario, ensure the task focuses on secure request flow and rendering behavior rather than external identity-provider setup.
- If backend integration is needed, simulate it locally inside the project using route handlers, fixtures, or in-project service modules rather than external infrastructure.
- The codebase should be TypeScript-based unless there is a compelling scenario-specific reason not to do so.

## Infrastructure Requirements
### Run.sh Instructions
- Because this is a pure-runtime Next.js task with no required external datastore, do NOT include docker-compose.yml, init_database.sql, Redis configuration, or any other datastore configuration.
- The project should run locally using the runtime's native project files and commands.
- Include a run.sh only if it adds value for consistent verification. If included, it should use explicit commands and assume the Next.js runtime dependencies are already available in the environment.
- Do NOT include apt-get install, npm install of the runtime itself, or any environment bootstrap unrelated to the task.
- The verification flow should rely on the project's native scripts such as test or build commands appropriate to the generated project.

The output should be a valid json schema:
- "package.json": "The runtime-native package manifest describing the local Next.js project scripts and dependencies needed for the starter task."
- "tsconfig.json": "The TypeScript configuration required for the generated Next.js project to type-check consistently."
- "next.config.js" or "next.config.mjs": "The Next.js configuration file only when needed for the selected scenario, such as i18n, experimental flags, or build customization relevant to the task."
- "app/..." or "pages/...": "The route files, layouts, components, route handlers, middleware, and supporting modules that implement the current incomplete or buggy application state."
- "tests/..." or equivalent: "The integration or end-to-end style tests that verify the intended advanced behavior without revealing the exact implementation."
- "README.md": "The concise candidate-facing task description following the required README structure below."
- ".gitignore": "The standard ignore file for a local Next.js and TypeScript project."
- "run.sh": "An optional helper script for consistent local verification if the task benefits from it."

## Code file requirements
- Every generated file must be fully populated with realistic content. Do NOT leave placeholder text such as "implement here" or "add logic".
- The starter code must compile or run in a coherent way and must represent the exact current state described in the task.
- The code should be intentionally incomplete, buggy, inefficient, insecure, or architecturally weak only in the ways required by the task.
- Keep the file set focused. Include only the files necessary to establish the scenario, reproduce the issue, and support verification.
- Ensure imports, exports, and file paths are internally consistent.
- Avoid excessive boilerplate that does not contribute to the assessment.
- Tests should validate observable behavior and should not encode the exact implementation details of the solution.
- The candidate-facing question must align exactly with the generated codebase.

## .gitignore INSTRUCTIONS
- Include a standard .gitignore appropriate for a Next.js and TypeScript project.
- Ignore node_modules, build artifacts, test output artifacts, local environment files, coverage output, and editor-specific temporary files.
- Keep it practical and concise.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md entry inside code_files MUST contain these sections in this exact order:

1. Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, the current state of the application, and why the problem matters.
- This section must never be empty.
- Do NOT include bold time-budget callouts.

2. Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with one of these action words: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips must guide discovery only.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

3. Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state the completed task should achieve.

4. How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a concrete check the candidate can run or observe.

5. NOT TO INCLUDE in README
- Explicitly instruct that the README must NOT include setup commands such as npm install, pnpm install, yarn install, npm test, npm run dev, or docker commands.
- Do NOT include direct solutions or architectural decisions.
- Do NOT include step-by-step implementation guides.
- Do NOT include specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Do NOT include code snippets that give away the answer.
- Do NOT include directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Do NOT include connection details, hostnames, ports, usernames, passwords, or placeholder deployment values.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms because that produces a hollow, unusable task.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that uniquely identifies the task and is different from the title.",
  "title": "A human-readable display name in the format of an action verb followed by a subject, between 50 and 80 characters, and different from the name field.",
  "question": "The full candidate-facing task description that explains the business context, the current implementation, the observed problems, the required outcomes, and the acceptance criteria without revealing the exact solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README that uses exactly the required section names and order, stays open-ended, and does not reveal the implementation approach.",
    ".gitignore": "A practical ignore file for the generated Next.js and TypeScript project.",
    "package.json": "The runtime-native package manifest containing the scripts and dependencies required for the local Next.js task.",
    "tsconfig.json": "The TypeScript configuration needed for the project to type-check and run consistently.",
    "next.config.js or next.config.mjs": "The Next.js configuration file only when the selected scenario genuinely requires framework configuration such as i18n or build customization.",
    "application source files": "All route files, components, middleware, route handlers, utilities, fixtures, and supporting modules needed to represent the current buggy or incomplete implementation.",
    "test files": "The unit, integration, or end-to-end style tests that verify the intended advanced behavior through observable outcomes.",
    "run.sh": "An optional helper script for consistent local verification when useful for the task, using explicit commands and no environment bootstrapping."
  }},
  "answer": "A high-level evaluator-facing explanation of the intended solution approach, key trade-offs, and what a strong advanced submission should address, without being written as candidate instructions.",
  "definitions": {{
    "term": "A plain-English definition for a task-relevant technical term that may be unfamiliar or important for interpreting the scenario.",
    "term_2": "Another plain-English definition for a task-relevant concept used in the question or README."
  }},
  "hints": "A single line nudging investigation toward the right problem area without revealing the fix, exact API, or implementation pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable behavior improvements, correctness, reliability, performance, or security outcomes in simple English.",
  "pre_requisites": "A bullet list of the tools, local runtime familiarity, and practical knowledge needed to work on the task successfully.",
  "short_overview": "A bullet list summarizing the business problem, the technical focus of the task, and the expected end result in concise candidate-friendly language."
}}

## CRITICAL REMINDERS
1. The generated task must be based on ONE provided real-world scenario and should closely align with that scenario's domain and technical constraints.
2. The environment must feel FULLY FUNCTIONAL from the candidate's perspective; the candidate fixes the task, not the environment.
3. The starter code must be runnable and must exactly match the described current implementation.
4. Do NOT include solution-revealing comments, TODOs, or hidden instructions inside the code files.
5. Keep the task scoped to {minutes_range} minutes for an ADVANCED candidate.
6. Use the exact top-level JSON keys specified above.
7. Keep the task local and pure-runtime unless the selected scenario truly requires an external service. For this prompt, prefer an in-project Next.js-only setup.
8. The README section names and order are non-negotiable and must match exactly.
9. The task should evaluate advanced Next.js engineering judgment, including performance, correctness, security, resilience, and maintainability, without drifting into unrelated platform work.
"""

PROMPT_REGISTRY = {
    "NextJs (ADVANCED)": [
        PROMPT_NEXTJS_ADVANCED_CONTEXT,
        PROMPT_NEXTJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_NEXTJS_ADVANCED_INSTRUCTIONS,
    ]
}