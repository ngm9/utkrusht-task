PROMPT_EXPRESSJS_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_EXPRESSJS_INPUT_AND_ASK_INTERMEDIATE = """
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
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Express.js implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Express.js proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_EXPRESSJS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Express.js, Node.js ecosystem, and backend architecture, you are given a list of real world scenarios and proficiency levels for Express.js development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors or add features hastily.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Express.js/Node.js experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced API Design**: RESTful principles, resource-oriented architecture, HTTP methods and idempotency, status code semantics, pagination/filtering/sorting, response format standardization, API versioning
  - **Middleware Architecture**: Custom middleware composition, error handling middleware, request/response transformation, authentication/authorization middleware, rate limiting
  - **Performance & Optimization**: Async/await patterns, efficient data processing, caching strategies (in-memory, Redis), stream processing for large payloads, middleware performance, connection pooling
  - **Security**: Input validation and sanitization, Helmet, CORS configuration, JWT/OAuth flows, CSRF defence, rate limiting
  - **Business Logic Organization**: Service layer pattern, separation of concerns, modular routing, dependency injection patterns
  - **Error Handling & Logging**: Centralized error handling, structured logging (pino/winston), meaningful error messages, error response standardization
  - **Code Quality**: Modern JavaScript/ES6+ or TypeScript, clean code principles, automated testing with Jest/Supertest
  - **Containerization**: Docker multi-stage builds, docker-compose for local development
  - **Observability**: Request tracing, metrics, health checks
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Node.js best practices (Node.js 18+) and current JavaScript standards. Use async/await patterns exclusively.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate Express.js proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create an Express.js task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years Express.js/Node.js experience), keeping in mind that AI assistance is allowed.
- Tests practical Express.js skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-layered Express.js applications that require proper middleware architecture, error handling, and performance optimization
- Should test the candidate's ability to design scalable APIs, manage middleware composition, handle errors gracefully, and ensure observability

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills
- The code files generated must be valid and executable with `npm start` or `npm run dev`.
- Provide a realistic project structure that mimics real-world applications (src/routes/, src/controllers/, src/services/, src/middleware/, src/utils/, src/config/, src/models/)
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper folder structure, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper architecture and design patterns
- Express.js starter code should include realistic project structure with proper middleware configuration
- Include some existing routes, controllers, or services that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architectural work
- If database is needed, include a docker-compose.yml with the database service definition
- If Redis is needed for caching, include it in docker-compose.yml

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Scalable Order Processing API with Caching', 'Refactor Authentication Middleware for Multi-Tenant Platform', 'Build Real-Time Inventory Management Service'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed?",
  "code_files": {{{{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
    ".gitignore": "Comprehensive Node.js and IDE exclusions",
    "package.json": "Node.js dependencies and scripts with intermediate-level packages",
    "docker-compose.yml": "Docker Compose file with database/Redis/other services if needed",
    "Dockerfile": "Multi-stage Dockerfile if containerization is part of the task",
    "src/index.js": "Express app entry point with server listen",
    "src/app.js": "Express app setup, middleware configuration, route mounting",
    "src/config/config.js": "Configuration management with environment variables",
    "src/middleware/errorHandler.js": "Centralized error handling middleware",
    "src/middleware/auth.js": "Authentication middleware (if needed)",
    "src/routes/exampleRoutes.js": "Route definitions using express.Router",
    "src/controllers/exampleController.js": "Controller with route handler functions",
    "src/services/exampleService.js": "Business logic service layer",
    "src/models/exampleModel.js": "Data models (if needed)",
    "src/utils/logger.js": "Structured logging setup",
    "additional_file.js": "Other source files as needed"
  }}}},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific Express.js implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include intermediate-level expectations like Node.js 18+, Express.js middleware architecture, async/await patterns, REST API design, Docker basics, testing with Jest/Supertest, structured logging, security best practices.",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "A single line hint focusing on Express.js architectural approach or middleware pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{{{
    "Express.js": "A minimal and flexible Node.js web application framework for building APIs and web servers",
    "Middleware": "Functions that have access to the request and response objects and can modify them or end the request-response cycle",
    "Router": "An Express class that creates modular, mountable route handlers for organizing API endpoints",
    "Connection Pooling": "Technique of maintaining a cache of database connections for reuse, improving performance",
    "Rate Limiting": "Controlling the number of requests a client can make in a given time window to prevent abuse"
  }}}}
}}}}

## Code file requirements:
- Generate realistic folder structure (src/routes/, src/controllers/, src/services/, src/middleware/, src/utils/, src/config/, src/models/, src/validators/, etc.)
- Code should follow modern Express.js and Node.js best practices and demonstrate intermediate-level patterns
- Use async/await patterns exclusively, no callback-based code
- Focus on modern JavaScript/ES6+ features and Express.js best practices
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing routes, controllers, or services that need to be extended, refactored, or optimized
- The core architectural decisions, middleware composition, error handling strategies, caching patterns, or security implementations that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add middleware here", "Implement caching", "Add validation", etc.
- DO NOT add comments that give away hints, solution, or implementation details
- The generated project structure should be runnable locally with `npm start` or `npm run dev`, but will require architectural work to function properly
- Provide realistic dependencies in package.json that intermediate developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Node.js/Express projects including node_modules, environment files (.env), log files, IDE configurations, coverage reports, Docker volumes, and other common development artifacts that should not be tracked in version control.

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
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper Express.js architecture is crucial.

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate Express.js level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and code quality metrics
  - Frame objectives around outcomes rather than specific technical implementations
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and architecture
  - API testing checkpoints (endpoints respond correctly, error handling works, performance is acceptable)
  - Frame verification in terms of observable outcomes
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring middleware composition patterns and error handling strategies
  - Mention thinking about how to structure services for testability and maintainability
  - Hint at considering caching, connection management, or security hardening
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery toward architectural thinking, not provide direct solutions or specific APIs

### NOT TO INCLUDE in README:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, npm start, docker-compose up, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific Express.js middleware names or library recommendations that reveal the solution
  - Direct answers and code snippets that would give away the solution
  - Specific endpoint implementations, middleware chains, or caching strategies to use
  - Phrases like "you should implement", "add the following middleware", "use library X"

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "order-processing-api", "inventory-management-service")
3. **code_files** must include README.md, .gitignore, package.json, and all Express.js source files
4. **README.md** must follow the structure above with Task Overview, Objectives, How to Verify, Helpful Tips
5. **Starter code** must be runnable (`npm start` or `npm run dev`) but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant Express.js/Node.js terms
9. **Task must be completable within the allocated time** for INTERMEDIATE proficiency (3-5 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use Node.js 18+ and modern JavaScript/ES6+** conventions throughout
12. **Focus on production-grade Express.js patterns** including middleware architecture, error handling, security, and performance
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "ExpressJS (INTERMEDIATE)": [
        PROMPT_EXPRESSJS_CONTEXT_INTERMEDIATE,
        PROMPT_EXPRESSJS_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_EXPRESSJS_INTERMEDIATE_INSTRUCTIONS,
    ],
}
