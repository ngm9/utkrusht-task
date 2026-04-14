PROMPT_REST_APIS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REST_APIS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a REST APIs assessment task.

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
2. What will the task look like? (Describe the type of REST API implementation or architectural challenge required, the expected deliverables, and how it aligns with INTERMEDIATE REST API proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REST_APIS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in REST API design, HTTP protocols, distributed systems, and backend architecture, you are given a list of real world scenarios and proficiency levels for REST API development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

**IMPORTANT — Language / Framework Choice**
REST APIs is a language-agnostic competency. You MUST pick the language and framework that best fits the real-world scenario provided. The scenario's business domain, technical context, and requirements should naturally guide your choice. Rotate across different languages and frameworks to ensure variety — do NOT default to the same stack every time. The chosen stack must feel authentic for the scenario (e.g., enterprise contexts may suit Java, data-heavy APIs may suit Python, lightweight services may suit Node.js or Go, etc.). Let the scenario decide — do not force a particular stack.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to tackle a deep, substantial implementation challenge — NOT a checklist of many small fixes.
- **CRITICAL — Task Depth Over Breadth**: The task should present **1-2 major implementation areas** that are architecturally heavy and require deep thinking, NOT 3-4 shallow tasks bundled together. For example:
  - GOOD: "Redesign the entire order management API with cursor-based pagination, DTO mapping, and structured logging with correlation IDs" (one deep challenge touching multiple layers)
  - BAD: "Add JWT auth, add rate limiting, add ETags, add pagination, add error handling" (a shopping list of unrelated features)
- The candidate should spend most of their time on architecture and design decisions within the 1-2 core areas, not rushing through a checklist of disconnected features.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors or add features hastily.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years REST API experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate mastery in the specific area the task focuses on. The task should deeply test one or two of the following areas (not all):
  - **Advanced API Design**: RESTful resource modeling, proper URI hierarchies, sub-resource relationships, collection vs singleton resources, consistent response envelopes, pagination (cursor-based and offset), filtering, sorting, partial responses (field selection)
  - **HTTP Semantics Mastery**: Correct method semantics and idempotency, conditional requests (ETag, If-Match, If-None-Match), content negotiation, proper use of 2xx/3xx/4xx/5xx status codes, cache-control headers
  - **Versioning Strategies**: URI versioning, header versioning, media type versioning — trade-offs and implementation
  - **Authentication & Authorization**: OAuth 2.0 flows, JWT validation and refresh, RBAC/ABAC on endpoints, scope-based access control
  - **Security**: Input validation and sanitization, rate limiting and throttling, CORS policy configuration, HTTPS enforcement, protection against injection, CSRF, XSS, security headers
  - **Error Handling & Resilience**: Standardized error response format (RFC 7807 Problem Details), centralized exception handling, meaningful error messages, retry-friendly error codes, graceful degradation
  - **Performance & Caching**: HTTP caching (Cache-Control, ETag), application-level caching, query optimization, connection pooling, response compression
  - **Observability**: Structured logging (correlation IDs, request tracing), health check endpoints (liveness/readiness), metrics exposure, request/response logging middleware
  - **Documentation**: OpenAPI/Swagger spec generation, API contract testing
  - **Containerization**: Docker multi-stage builds, docker-compose for local dev with databases and cache services
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern best practices for the chosen language/framework.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate REST API proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a REST API task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years REST API experience), keeping in mind that AI assistance is allowed.
- Tests practical REST API skills that require architectural thinking, performance considerations, and deep design work in 1-2 focused areas
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on a deep, layered Spring Boot challenge that requires the candidate to make real architectural decisions — not a breadth-first checklist
- Should test the candidate's ability to design a well-structured API with proper layering, clean separation of concerns, and production-grade patterns

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills.
- The code files generated must be valid and executable using the standard run command for the chosen language/framework.
- Provide a realistic project structure that mimics real-world applications appropriate for the chosen stack.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper folder structure, and architectural decisions.
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve.
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper architecture and design patterns.
- Include some existing routes, controllers, or services that the candidate needs to work with or extend.
- Provide partial implementations that require candidates to complete the architectural work.
- If database is needed, include a docker-compose.yml with the database service definition.
- If Redis or other services are needed for caching, include them in docker-compose.yml.

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Scalable Order Processing API with Caching', 'Refactor Authentication Layer for Multi-Tenant Platform', 'Build Real-Time Inventory Management API'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed? This should describe 1-2 deep implementation areas, NOT a long list of small features.",
  "code_files": {{{{
    "README.md": "Candidate-facing README following the README structure defined below",
    ".gitignore": "Comprehensive language-specific and IDE exclusions",
    "...": "All other files appropriate for the chosen language/framework — dependency file, docker-compose.yml (if needed), Dockerfile (if needed), entry point, route/controller files, service layer files, middleware files, model/schema files, configuration files, utility files, etc. Use realistic file paths and names that follow the conventions of the chosen stack. Generate as many files as needed for a proper project structure."
  }}}},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific REST API implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include intermediate-level expectations like the specific runtime, REST API design principles, HTTP semantics, authentication/authorization, caching strategies, Docker basics, testing, structured logging, security best practices.",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "A single line hint focusing on REST API architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{{{
    "REST": "Representational State Transfer — an architectural style for designing networked APIs using HTTP methods and resource-oriented URIs",
    "Idempotency": "Property of an operation where performing it multiple times produces the same result as performing it once (GET, PUT, DELETE are idempotent)",
    "ETag": "Entity Tag — an HTTP header used for cache validation and conditional requests, enabling efficient resource synchronization",
    "Rate Limiting": "Controlling the number of requests a client can make in a given time window to prevent abuse and ensure fair usage",
    "HATEOAS": "Hypermedia As The Engine Of Application State — a REST constraint where responses include links to related resources and available actions"
  }}}}
}}}}

## Code file requirements:
- Use realistic file paths and names that follow the conventions of the chosen language/framework.
- Code should follow modern best practices and demonstrate intermediate-level patterns for the chosen stack.
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion in the 1-2 focused areas.
- Include some existing routes, controllers, or services that need to be extended, refactored, or optimized.
- The core architectural decisions that the candidate needs to make MUST be left for the candidate to design.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add service here", "Implement caching", "Add validation", etc.
- DO NOT add comments that give away hints, solution, or implementation details
- The generated project structure should be runnable locally, but will require architectural work to function properly.
- Provide realistic dependencies in the dependency file that intermediate developers should be familiar with.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for the chosen language/framework including dependency directories, environment files (.env), log files, IDE configurations, coverage reports, Docker volumes, build artifacts, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE
- The README.md contains the following sections in this exact order:
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
- README should NOT be heavy — each section should have only the essential points (4-5 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why proper API architecture and performance matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper REST API design is crucial.

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate REST API level
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
  - Suggest exploring API design patterns and resource modeling strategies
  - Mention thinking about how to structure services for testability and maintainability
  - Hint at considering caching, connection management, or security hardening
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery toward architectural thinking, not provide direct solutions or specific APIs

### NOT TO INCLUDE IN README:
  - SETUP INSTRUCTIONS OR COMMANDS (mvn install, mvn spring-boot:run, docker-compose up, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific library names or framework APIs that reveal the solution
  - Direct answers and code snippets that would give away the solution
  - Specific endpoint implementations, middleware chains, or caching strategies to use
  - Phrases like "you should implement", "add the following middleware", "use library X"

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "order-processing-api", "inventory-management-service")
3. **code_files** must include README.md, .gitignore, dependency file, and all source files with realistic paths for the chosen stack
4. **README.md** must follow the structure above with Task Overview, Objectives, How to Verify, Helpful Tips (in that exact order)
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant REST API terms
9. **Task must be completable within the allocated time** for INTERMEDIATE proficiency (3-5 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Rotate language/framework** — let the scenario naturally guide your choice, do NOT default to the same stack
12. **Task should focus on 1-2 deep implementation areas**, NOT a checklist of 3-4 shallow features
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""

PROMPT_REGISTRY = {
    "REST APIs (INTERMEDIATE)": [
        PROMPT_REST_APIS_INTERMEDIATE_CONTEXT,
        PROMPT_REST_APIS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_REST_APIS_INTERMEDIATE_INSTRUCTIONS,
    ],
}
