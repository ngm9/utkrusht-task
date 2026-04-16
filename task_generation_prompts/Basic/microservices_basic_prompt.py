PROMPT_MICROSERVICES_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MICROSERVICES_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Microservices assessment task.

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

Based on the above inputs, briefly state:
1. Which scenario you selected and why
2. What the task will involve

Then immediately proceed to generate the full task JSON as defined in the next instructions. Do NOT stop or ask for confirmation — continue directly with the complete task output.
"""
PROMPT_MICROSERVICES_BASIC = """
## GOAL
As a senior software architect super experienced in microservices architecture, RESTful API design, Docker, inter-service communication, and distributed systems fundamentals, you are given a list of real world scenarios and proficiency levels for Microservices development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years microservices experience), ensuring that no two questions generated are similar.
- **CRITICAL TIME BUDGET**: The total task time is 30 minutes. The candidate needs ~5 minutes to verify and test their implementation. So the actual implementation work must be completable in ~25 minutes by a basic-level developer (with AI assistance allowed).
- **CRITICAL SCOPE**: The task must have exactly 2 focused objectives. Each objective should test a fundamental microservices concept clearly — not too shallow (just wiring code) and not too deep (saga patterns, distributed transactions). The candidate should spend time understanding inter-service communication, error handling, and request/response patterns.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental microservices concepts like:
  - Understanding microservices architecture principles (single responsibility, bounded context, independent deployability)
  - Designing and implementing simple stateless RESTful microservices
  - Using appropriate frameworks for the language specified in the scenario/competencies
  - Basic CRUD operations with service-owned databases
  - Inter-service communication: synchronous HTTP/REST calls between services
  - Service discovery basics and API gateway patterns
  - Docker containerization of individual services
  - Docker Compose for local multi-service development
  - Health check endpoints and basic monitoring
  - Configuration management (environment variables, config files)
  - Basic error handling across service boundaries (timeouts, retries, fallbacks)
  - API documentation (Swagger/OpenAPI basics)
  - Simple logging and request tracing across services
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern development best practices and current framework standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- The task should involve 2 microservices — one fully implemented dependency service and one broken/incomplete caller service that the candidate must fix

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic microservices proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Microservices task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years microservices experience), keeping in mind that AI assistance is allowed.
- Tests practical microservices skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within 30 minutes total (including ~5 minutes for the candidate to verify/test their work, so ~25 minutes of actual implementation).
- **SCOPE CONSTRAINT**: Limit the task to exactly 2 focused implementation objectives. Do NOT create tasks with 3+ objectives. Each objective should test a clear fundamental microservices concept — inter-service HTTP calls, error handling across service boundaries, response parsing, or data validation using cross-service data. Do NOT include advanced patterns like saga, circuit breaker, event-driven, or distributed transactions — those are intermediate level.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on 2 service architectures with synchronous HTTP communication, not complex event-driven or saga patterns
- The task environment must use Docker Compose to run all services together
- One service should be fully implemented (the dependency), and the candidate fixes/implements the other service (the caller)

## Technology Stack Choice:
- The technology stack (language + framework) for each microservice MUST be determined by the real-world scenario and competencies provided in the input — do NOT hardcode a specific language
- The scenario text (from {real_world_task_scenarios}) or competency names will specify which language/framework to use (e.g., Java, Node.js, Python, Rust, C#, Go, etc.)
- If the scenario does not explicitly specify a language, infer the most appropriate one from the competencies input
- Each microservice in the task can use a different tech stack if the scenario calls for it (polyglot microservices), but keeping them uniform is also acceptable
- Include the appropriate build files and dependency management for whatever language is chosen (e.g., pom.xml for Java, package.json for Node.js, requirements.txt for Python, Cargo.toml for Rust, go.mod for Go, .csproj for C#, etc.)
- Use idiomatic project structure for the chosen language (e.g., src/main/java for Java, src/ for Node.js, app/ for Python, etc.)

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `docker-compose up --build`.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Starter code should include a docker-compose.yml with 2 service definitions, each with its own Dockerfile
- Each service should have its own directory with its own code, dependencies, and Dockerfile
- Use the correct base Docker image for whatever language is chosen (e.g., openjdk:17-slim for Java, node:18-alpine for Node.js, python:3.11-slim for Python, rust:1.75-slim for Rust, mcr.microsoft.com/dotnet/sdk:8.0 for C#, golang:1.22-alpine for Go)
- Include database service(s) in docker-compose.yml (PostgreSQL, MongoDB, or other DB as appropriate for the scenario)

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, all containers must start successfully, databases must be seeded, and all services must be healthy. Deployment must NOT fail. The candidate receives a working multi-service environment from the start; their only job is to fix or improve the given microservices problem.

### docker-compose.yml
- Must include 2 microservice definitions plus database service(s).
- Hardcoded configuration — no `.env` file references, no environment variable placeholders for service config.
- Each microservice must expose its API port to the host.
- **No `version:` field** in the compose file.
- Services must have proper `depends_on` with health checks so they start in correct order.
- If a database is used, mount `init_database.sql` to the appropriate entrypoint directory (e.g., `/docker-entrypoint-initdb.d/` for PostgreSQL).
- Use named volumes for database data persistence.

### run.sh
Generate this script with the following EXACT structure and behaviour:

**run.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- Run `docker-compose up -d --build` to start all services.
- Include a health check loop that waits for each service to be ready:
  - Check database health first (e.g., `docker-compose exec -T postgres psql` for PostgreSQL).
  - Then check each microservice health endpoint.
- If any check fails after retries, print docker-compose logs and exit with code 1.
- End with a clear success message showing the URLs for each service.

### kill.sh
Generate this script with the following EXACT structure — this is the required cleanup pattern:

**kill.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- MUST `cd /root/task` first so `docker-compose down` can find the `docker-compose.yml`.
- MUST run `docker-compose down --rmi all --volumes --remove-orphans` to remove compose-managed containers, named volumes, networks, and images in one step.
- MUST then explicitly force-stop ALL running containers with `docker ps -q` — this catches any container that `docker-compose down` missed.
- MUST explicitly remove ALL containers with `docker ps -aq` before pruning.
- MUST run `docker volume prune -f`, then `docker image prune -a -f`, then `docker system prune -a --volumes -f` — in this order.
- MUST `rm -rf /root/task` as the final step after all Docker cleanup is done.
- Every destructive command MUST end with `|| true` so the script never exits early due to "already removed" errors.
- The script MUST be idempotent — safe to run multiple times on an already-clean droplet.
- Print a progress message before every major step.
- End with `echo "[kill.sh] Cleanup completed."`.

### init_database.sql (if applicable)
- Single file that creates the schema and inserts seed data, runs to completion without errors.
- No solution hints in comments.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Order Service Communication with Inventory API', 'Fix Inter-Service Health Check in E-Commerce Platform', 'Build User Authentication Microservice with Gateway'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive exclusions for the chosen tech stack(s)",
    "docker-compose.yml": "Docker Compose with 2 microservice definitions plus database(s) — follows rules above",
    "run.sh": "Deploy script — follows run.sh rules above exactly",
    "kill.sh": "Cleanup script — follows kill.sh rules above exactly",
    "<service-name>/Dockerfile": "Dockerfile for each service — use appropriate base image for the chosen language (e.g., openjdk for Java, node for Node.js, python for Python, rust for Rust, mcr.microsoft.com/dotnet for C#, golang for Go)",
    "<service-name>/<dependency-file>": "Language-appropriate dependency file (pom.xml, package.json, requirements.txt, Cargo.toml, go.mod, .csproj, etc.)",
    "<service-name>/src/...": "Source code files following idiomatic project structure for the chosen language",
    "init_database.sql": "Database initialization script if needed",
    "additional files": "Other source files as needed — repeat service directory pattern for each microservice (2 services)"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem requiring a microservices solution, (2) the specific implementation or fix goal involving inter-service communication, service boundaries, or containerized deployment, and (3) the expected outcome emphasizing correctness, service isolation, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Docker, Docker Compose, the chosen framework(s), REST API fundamentals, basic microservices concepts (service boundaries, inter-service communication, containerization).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on clear service boundaries, proper error handling across HTTP calls, and health check endpoints for each service'",
  "definitions": {{
    "Microservice": "A small, independently deployable service that focuses on a single business capability",
    "Service Discovery": "The mechanism by which services locate and communicate with each other in a distributed system",
    "API Gateway": "A single entry point that routes requests to appropriate backend microservices",
    "Bounded Context": "A design boundary within which a particular domain model is defined and applicable",
    "Health Check": "An endpoint that reports the operational status of a service and its dependencies"
  }}
}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern best practices for the chosen framework(s)
- Use proper project structure with separate directories per service
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core inter-service communication, business logic, API endpoints, or data layer implementations that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add service call here" or "Should implement REST client" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable with docker-compose, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for the chosen tech stack(s). Include build outputs appropriate for the language (target/ for Java, node_modules/ for Node.js, __pycache__/ for Python, target/ for Rust, bin/obj/ for C#, vendor/ for Go, etc.), IDE configurations (.idea, .vscode, .vs), environment files (.env), log files, Docker volumes, and other common development artifacts for the specific language(s) used.

## README.md STRUCTURE (Microservices)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the multi-service application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level microservices task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around observable outcomes and expected behavior
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### Service & Database Access

Provide all the access details the candidate needs to interact with the running environment:
  - **API endpoints for each microservice**: List each service name, its host as `<DROPLET_IP>`, and its exposed port (e.g., "Order Service: http://<DROPLET_IP>:3001")
  - **Database connection details**: For each database used, provide the host (`<DROPLET_IP>`), exposed port, database name, username, and password. Mention that candidates can use any preferred database client tools (e.g., pgAdmin, DBeaver, psql)
  - **Inter-service communication**: Briefly note that services communicate internally via Docker network using service names (e.g., "Services communicate internally using Docker service names — the Order Service calls the Inventory Service at http://inventory-service:3002")
  - Use `<DROPLET_IP>` as a placeholder — never hardcode an IP address
  - Keep this section factual and concise — just the connection details, no implementation hints

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery — suggest areas to explore, not specific solutions
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.
  
### How to Verify (3-5 bullets MAX)

Give the candidate concrete, actionable ways to confirm each objective works — tell them exactly what API call to make, what response to expect, or what to check in the database. Do NOT reveal HOW to implement the solution, but DO tell them HOW to TEST it.

Each bullet should follow this pattern: **action to take → expected observable result**

Examples of proper framing:
  * "Call POST /orders with a product that has 0 stock — you should receive a 409 response with a message about insufficient inventory"
  * "After a successful order, query the Inventory Service directly at GET /inventory/{{productId}} — the available_stock should be decremented by the ordered quantity"
  * "Call POST /orders while the Inventory Service container is stopped — you should receive a 503 response"
  * "Check the orders database table after a failed stock check — no new row should have been created"

Rules:
  - Each bullet = one specific test the candidate can perform right now using curl, Postman, or a DB client
  - Mention the exact endpoint path, expected HTTP status code, and what to look for in the response or database
  - Include at least one negative/error case test (service down, invalid input, business rule violation)
  - Do NOT reveal implementation approach — only describe the test and expected outcome
  - **CRITICAL**: Keep to 3-5 concise bullets. Tell them WHAT to test and WHAT to expect, never HOW to implement.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (docker-compose up, mvn spring-boot:run, npm start, etc.)
- Specific framework class names or methods that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "order-inventory-microservices")
3. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, kill.sh, Dockerfiles, and source files for each service
4. **README.md** must follow the structure above with Task Overview, Service & Database Access, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable (docker-compose up --build) but must NOT contain the solution
6. **Deployment must succeed in one go** — After run.sh, all containers must be healthy, databases seeded, all services accessible. The candidate only fixes or improves the microservices problem, not deployment.
7. **run.sh** must follow the exact rules above: health check loops for DB and each service, fail with logs on error
8. **kill.sh** must follow the exact rules above: docker-compose down, force-stop containers, prune volumes/images/system, rm -rf /root/task, all with `|| true`
9. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
10. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
11. **hints** must be a single line; **definitions** must include relevant microservices terms
12. **Task must be completable within 30 minutes** (25 min implementation + 5 min testing) for BASIC proficiency (1-2 years)
13. **NO comments in code** that reveal the solution or give hints
14. **Focus on 2 service architectures** with synchronous HTTP communication — one service fully implemented, candidate fixes/implements the other
15. **Each service must have its own directory**, Dockerfile, and dependency file
16. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
17. **docker-compose.yml must NOT have a `version:` field** — use modern compose format
18. **SCOPE**: Task must have exactly 2 implementation objectives — NOT more, NOT less. One objective should focus on inter-service communication (making HTTP calls, parsing responses, data validation). The other should focus on error handling across service boundaries (service down, timeouts, different error status codes). Do NOT include advanced patterns (saga, circuit breaker, event-driven, distributed transactions).
19. **PATTERN**: One service is the dependency (fully working, candidate does NOT touch it). The other service is the caller (broken/incomplete, candidate must fix it by adding inter-service calls, validation, and error handling).
"""
PROMPT_REGISTRY = {
    "Microservices (BASIC)": [
        PROMPT_MICROSERVICES_CONTEXT_BASIC,
        PROMPT_MICROSERVICES_INPUT_AND_ASK_BASIC,
        PROMPT_MICROSERVICES_BASIC,
    ],
}
