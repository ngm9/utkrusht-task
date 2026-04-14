PROMPT_JAVASCRIPT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVASCRIPT_BASIC_INPUT_AND_ASK = """
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
2. What will the task look like? (Describe the type of JavaScript implementation or fix required, the expected deliverables, and how it aligns with BASIC JavaScript proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVASCRIPT_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in JavaScript, modern ES6+ features, DOM manipulation, and frontend/backend JavaScript development, you are given a list of real world scenarios and proficiency levels for JavaScript development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (0-1 years JavaScript experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental JavaScript concepts like:
  - Variables, data types, and operators (`var`, `let`, `const`, type coercion, truthy/falsy)
  - Control structures (`if/else`, `switch`, `for`, `while`, `for...of`)
  - Functions (declarations, expressions, arrow functions, default parameters)
  - Scope, hoisting, and closures (basic understanding)
  - DOM manipulation (`getElementById`, `querySelector`, `createElement`, `appendChild`, `textContent`, `innerHTML`)
  - Event handling (`addEventListener`, `click`, `input`, `submit`, event object basics)
  - ES6+ features (arrow functions, template literals, destructuring, spread/rest operators)
  - Higher-order array methods (`map`, `filter`, `reduce`, `forEach`, `find`)
  - Basic asynchronous JavaScript (Promises with `.then()/.catch()`, simple `async/await`)
  - Fetch API for simple HTTP requests (`fetch`, handling JSON responses)
  - Basic error handling (`try/catch`, throwing errors)
  - Simple form validation and dynamic content updates
  - String and array manipulation methods
  - Object basics (creation, property access, iteration)
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern JavaScript best practices (ES6+) and current development standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Task Environment**: Tasks should work as either browser-based JavaScript (with an HTML file) or Node.js scripts, depending on the scenario. For DOM-related tasks, include an HTML file. For data processing or API tasks, use Node.js.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic JavaScript proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a JavaScript task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (0-1 years JavaScript experience), keeping in mind that AI assistance is allowed.
- Tests practical JavaScript skills that require more than a simple AI query to solve, focusing on fundamental JavaScript concepts
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on small, self-contained applications that test core language features, DOM manipulation, async basics, and ES6+ usage
- Should NOT require frameworks (React, Angular, Vue), build tools (Webpack, Vite), or complex infrastructure

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and runnable (open HTML in browser, or run with `node`).
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- JavaScript starter code should include basic file structure but NOT require complex infrastructure setup (databases, build tools, package managers, etc.)
- For browser-based tasks: provide an HTML file with basic structure and a linked JS file
- For Node.js tasks: provide a simple package.json and entry point JS file

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Dynamic Product Filter for E-Commerce Dashboard', 'Fix Data Validation in Patient Registration Form', 'Build Interactive Task Tracker with Local Storage'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{{{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Node.js/web project exclusions",
    "index.html": "HTML file with basic structure (for browser-based tasks)",
    "src/app.js": "Main JavaScript entry point",
    "src/utils.js": "Utility/helper functions (if needed)",
    "package.json": "Node.js package file (for Node.js tasks)",
    "additional_file.js": "Other source files as needed"
  }}}},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper naming conventions, error handling, and code organization.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include modern browser or Node.js 18+, IDE, Git, and JavaScript fundamentals (ES6+ syntax, DOM manipulation, async/await, array methods, error handling).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on proper DOM element selection, event delegation, and input validation before processing data'",
  "definitions": {{{{
    "DOM": "Document Object Model — a programming interface for web documents that represents the page structure as a tree of nodes",
    "Closure": "A function that retains access to variables from its enclosing scope even after the outer function has returned",
    "Promise": "An object representing the eventual completion or failure of an asynchronous operation",
    "async/await": "JavaScript syntax for handling asynchronous operations in a synchronous-looking manner",
    "ES6+": "ECMAScript 2015 and later — modern JavaScript features including arrow functions, destructuring, template literals, and modules"
  }}}}
}}}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern JavaScript best practices (ES6+)
- Use a clean, simple file structure appropriate for the task type
- Use `let`/`const` instead of `var`, arrow functions where appropriate, template literals, destructuring
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core business logic, DOM manipulation handlers, data processing functions, or validation logic that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement validation" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for JavaScript projects including node_modules, environment files (.env), log files, IDE configurations (.idea, .vscode), coverage reports, build output directories, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE (JavaScript)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Suggest exploring how JavaScript handles different data types and edge cases
  - Mention thinking about how to safely access and modify DOM elements
  - Hint at considering how asynchronous operations should be sequenced and errors handled
  - Recommend exploring how modern array methods can simplify data transformations
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level JavaScript task:
  - Clear, measurable goals the candidate should achieve to complete the task
  - Functionality to implement, expected behavior, user interactions
  - Focus on fundamental JavaScript concepts (DOM updates, data processing, async handling, validation)
  - Frame objectives around outcomes, not specific APIs or methods
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Observable behaviors or outputs to validate (UI updates, console output, correct data transformations)
  - Functional testing and basic code quality checks
  - What to test and how to confirm success
  - **CRITICAL**: Describe what behaviors to verify, not specific code or methods to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (npm install, node app.js, etc.)
- Specific JavaScript APIs or method names that reveal the solution
- Phrases like "you should implement", "add the following code", "use Array.map to..."
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "product-filter-dashboard", "patient-form-validation")
3. **code_files** must include README.md, .gitignore, and JavaScript source files (plus HTML if browser-based)
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, naming conventions, error handling
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant JavaScript terms
9. **Task must be completable within the allocated time** for BASIC proficiency (0-1 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use modern JavaScript (ES6+)** conventions throughout
12. **Focus on fundamental JavaScript patterns**, not frameworks or complex build setups
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "Javascript (BASIC)": [
        PROMPT_JAVASCRIPT_BASIC_CONTEXT,
        PROMPT_JAVASCRIPT_BASIC_INPUT_AND_ASK,
        PROMPT_JAVASCRIPT_BASIC_INSTRUCTIONS,
    ],
}
