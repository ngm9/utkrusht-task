PROMPT_JAVASCRIPT_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVASCRIPT_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a JavaScript assessment task.

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
2. What will the task look like? (Describe the type of JavaScript implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE JavaScript proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVASCRIPT_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in JavaScript, modern ES6+ features, browser APIs, asynchronous patterns, performance optimization, and modular application design, you are given a list of real world scenarios and proficiency levels for JavaScript development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors or add features hastily.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-6 years JavaScript experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced Closures & Scope**: Closures for data privacy, module patterns, IIFE, lexical scoping in complex scenarios, `this` binding (bind, call, apply)
  - **Asynchronous Mastery**: Promise chaining, Promise.all/allSettled/race, async/await error handling, AbortController, fetch with retry logic, debouncing/throttling
  - **DOM & Browser APIs**: Efficient DOM manipulation, event delegation, MutationObserver, IntersectionObserver, Web Storage (localStorage/sessionStorage with TTL), custom events
  - **Design Patterns**: Singleton, Factory, Observer/PubSub, Strategy, Module pattern, revealing module pattern
  - **Performance Optimization**: Reducing reflows/repaints, lazy loading, virtual scrolling concepts, memory leak prevention, efficient event listeners, requestAnimationFrame
  - **Modular Architecture**: ES modules (import/export), dependency management, separation of concerns, clean API design between modules
  - **Error Handling & Resilience**: Custom error classes, graceful degradation, retry strategies, fallback mechanisms, user-friendly error messaging
  - **Security Awareness**: XSS prevention (textContent vs innerHTML), input sanitization, CSRF token handling, secure storage of tokens (JWT)
  - **Testing Concepts**: Unit testable code structure, mockable dependencies, assertion-friendly outputs
  - **API Integration**: Fetch API with interceptors, request/response transformation, caching API responses, handling pagination, concurrent requests
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern JavaScript best practices (ES6+) and current development standards.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate JavaScript proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a JavaScript task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-6 years JavaScript experience), keeping in mind that AI assistance is allowed.
- Tests practical JavaScript skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-module JavaScript applications that require proper architecture, async coordination, DOM efficiency, and design patterns
- Should test the candidate's ability to structure scalable JavaScript code, manage async flows, handle errors gracefully, and optimize performance
- Can be browser-based (with HTML + multiple JS modules) or Node.js-based, depending on the scenario

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills
- The code files generated must be valid and runnable (open HTML in browser, or run with `node`).
- Provide a realistic project structure that mimics real-world applications
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper module structure, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper modular design and architecture
- Include some existing modules, classes, or utility functions that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architectural work

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Refactor Payment Dashboard with Caching and Error Resilience', 'Implement Real-Time Notification System with Event Architecture', 'Optimize Product Catalog with Lazy Loading and DOM Efficiency'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed? Include architectural considerations and requirements.",
  "code_files": {{{{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
    ".gitignore": "Comprehensive JavaScript/Node.js project exclusions",
    "index.html": "HTML file with basic structure (for browser-based tasks)",
    "package.json": "Node.js package file (for Node.js tasks or if npm scripts are useful)",
    "src/app.js": "Main application entry point",
    "src/api.js": "API integration module (if needed)",
    "src/utils.js": "Utility/helper functions",
    "src/events.js": "Event management module (if needed)",
    "src/cache.js": "Caching module (if needed)",
    "src/components/exampleComponent.js": "UI component modules (if needed)",
    "additional_file.js": "Other source files as needed"
  }}}},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific JavaScript implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include intermediate-level expectations like modern browser or Node.js 18+, ES6+ modules, async/await patterns, DOM APIs, design patterns, performance optimization concepts, error handling strategies, security awareness (XSS, CSRF).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "A single line hint focusing on JavaScript architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{{{
    "Closure": "A function that retains access to variables from its enclosing scope even after the outer function has returned",
    "Event Delegation": "A pattern where a single event listener on a parent element handles events for multiple child elements",
    "Promise.all": "A method that takes an iterable of promises and returns a single promise that resolves when all input promises resolve",
    "AbortController": "A controller object that allows you to abort one or more web requests as and when desired",
    "Module Pattern": "A design pattern that uses closures to create private and public encapsulation for classes"
  }}}}
}}}}

## Code file requirements:
- Generate realistic file structure appropriate for the task complexity (src/, src/components/, src/utils/, src/services/, etc.)
- Code should follow modern JavaScript best practices (ES6+) and demonstrate intermediate-level patterns
- Use `const`/`let`, arrow functions, destructuring, template literals, ES modules
- Focus on clean, modular code with proper separation of concerns
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing modules, classes, or utilities that need to be extended, refactored, or optimized
- The core architectural decisions, design patterns, async coordination, caching strategies, performance optimizations, or security implementations that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add caching here", "Implement observer pattern", "Add sanitization", etc.
- DO NOT add comments that give away hints, solution, or implementation details
- The generated project structure should be runnable, but will require architectural work to function properly
- For browser-based tasks, use ES modules with `<script type="module">` or simple script loading

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for JavaScript projects including node_modules, environment files (.env), log files, IDE configurations (.idea, .vscode), coverage reports, build output directories (dist/, build/), and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
- The README.md contains the following sections:
  - Task Overview
  - Objectives
  - How to Verify
  - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
- README should NOT be heavy — each section should have only the essential points (4-6 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why proper architecture and performance matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper JavaScript architecture is crucial.

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate JavaScript level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and code quality metrics
  - Frame objectives around outcomes rather than specific technical implementations
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and architecture
  - UI behavior checkpoints, console output validation, performance indicators
  - Frame verification in terms of observable outcomes
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring modular architecture patterns and async coordination strategies
  - Mention thinking about how to structure code for testability and maintainability
  - Hint at considering caching, DOM efficiency, or security hardening
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery toward architectural thinking, not provide direct solutions or specific APIs

### NOT TO INCLUDE in README:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, node app.js, open index.html, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific JavaScript APIs, method names, or design pattern names that reveal the solution
  - Direct answers and code snippets that would give away the solution
  - Specific module implementations, event handling strategies, or caching approaches to use
  - Phrases like "you should implement", "use Promise.all", "add an IntersectionObserver"

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "payment-dashboard-refactor", "notification-event-system")
3. **code_files** must include README.md, .gitignore, and JavaScript source files (plus HTML if browser-based)
4. **README.md** must follow the structure above with Task Overview, Objectives, How to Verify, Helpful Tips
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant JavaScript terms
9. **Task must be completable within the allocated time** for INTERMEDIATE proficiency (3-6 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use modern JavaScript (ES6+)** conventions throughout
12. **Focus on production-grade JavaScript patterns** including modular architecture, async coordination, error resilience, DOM performance, and security
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "Javascript (INTERMEDIATE)": [
        PROMPT_JAVASCRIPT_CONTEXT_INTERMEDIATE,
        PROMPT_JAVASCRIPT_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_JAVASCRIPT_INTERMEDIATE_INSTRUCTIONS,
    ],
}
