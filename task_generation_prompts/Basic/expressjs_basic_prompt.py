PROMPT_EXPRESSJS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_EXPRESSJS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Express.js assessment task.

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

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Express.js proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_EXPRESSJS_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Express.js, Node.js ecosystem, and backend API development, you are given a list of real world scenarios and proficiency levels for Express.js development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Express.js/Node.js experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental Express.js concepts like:
  - Express application setup and configuration (express(), app.listen, port configuration)
  - Basic routing (app.get, app.post, app.put, app.delete, route parameters, query strings)
  - Request/Response handling (req.params, req.query, req.body, res.json, res.status)
  - Simple middleware usage (express.json(), express.urlencoded(), custom middleware basics)
  - Basic error handling (try/catch in async handlers, simple error middleware)
  - HTTP methods and status codes (200, 201, 400, 404, 500)
  - Simple CRUD operations with in-memory data or JSON files
  - Basic async/await patterns with Express route handlers
  - Serving static files (express.static)
  - Environment variables with dotenv
  - Basic input validation (checking required fields, data types)
  - Simple modular routing (express.Router)
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Node.js best practices (Node.js 18+) and current JavaScript standards. Use async/await patterns exclusively.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Database is OPTIONAL**: Tasks may or may not include database integration. When databases are not required, focus on in-memory data structures, JSON files, or simple file operations.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Express.js proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create an Express.js task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years Express.js/Node.js experience), keeping in mind that AI assistance is allowed.
- Tests practical Express.js skills that require more than a simple AI query to solve, focusing on fundamental Express.js concepts
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on simple API applications that test routing, middleware, request handling, and basic async patterns
- Should NOT require advanced patterns like complex caching, rate limiting, API versioning, or distributed systems

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `npm start` or `npm run dev`.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Express.js starter code should include basic project structure but NOT require complex infrastructure setup (databases, message queues, caching layers, etc.)
- Focus on Express.js with simple routing, middleware, and async/await for simplicity

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Product Catalog API for E-Commerce Platform', 'Fix Route Handling in Booking Management Service', 'Build User Registration Endpoint with Validation'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{{{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Node.js and IDE exclusions",
    "package.json": "Node.js dependencies and scripts",
    "src/index.js": "Express app entry point with server listen",
    "src/app.js": "Express app setup and middleware configuration",
    "src/routes/exampleRoutes.js": "Route definitions using express.Router",
    "src/controllers/exampleController.js": "Controller with route handler functions",
    "src/middleware/errorHandler.js": "Basic error handling middleware",
    "additional_file.js": "Other source files as needed"
  }}}},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm, IDE, Git, and Express.js fundamentals (routing, middleware, request/response handling, async/await, HTTP methods and status codes).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on proper route organization, middleware ordering, and consistent error response formatting'",
  "definitions": {{{{
    "Express.js": "A minimal and flexible Node.js web application framework for building APIs and web servers",
    "Middleware": "Functions that have access to the request and response objects and can modify them or end the request-response cycle",
    "Router": "An Express class that creates modular, mountable route handlers for organizing API endpoints",
    "async/await": "JavaScript syntax for handling asynchronous operations in a synchronous-looking manner",
    "REST": "Representational State Transfer — an architectural style for designing networked APIs using HTTP methods"
  }}}}
}}}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Express.js and Node.js best practices
- Use a clean project structure (src/routes/, src/controllers/, src/middleware/, etc.)
- Use async/await patterns exclusively, no callback-based code
- Focus on modern JavaScript/ES6+ features
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core route handlers, controller logic, middleware implementations, or service methods that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement validation" etc.
- DO NOT add comments that give away hints or solution or implementation details

- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Node.js projects including node_modules, environment files (.env), log files, IDE configurations (.idea, .vscode), coverage reports, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE (Express.js)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery — suggest areas to explore, not specific solutions
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level Express.js task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around observable outcomes and expected behavior
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Describe what behaviors to verify and how to confirm success
  - Focus on observable outcomes (response behavior, status codes, error handling)
  - Do NOT specify specific code, annotations, or implementation details to check
  - **CRITICAL**: Describe what behaviors to verify, not specific code or annotations to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (npm install, npm start, etc.)
- Specific Express.js APIs or method names that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "product-catalog-api", "booking-service-routes")
3. **code_files** must include README.md, .gitignore, package.json, and Express.js source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable (`npm start` or `npm run dev`) but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant Express.js/Node.js terms
9. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use Node.js 18+ and modern JavaScript/ES6+** conventions throughout
12. **Focus on fundamental Express.js patterns**, not complex distributed systems or advanced architectural patterns
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "ExpressJS (BASIC)": [
        PROMPT_EXPRESSJS_BASIC_CONTEXT,
        PROMPT_EXPRESSJS_BASIC_INPUT_AND_ASK,
        PROMPT_EXPRESSJS_BASIC_INSTRUCTIONS,
    ],
}
