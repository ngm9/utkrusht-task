PROMPT_MICROSERVICES_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MICROSERVICES_INPUT_AND_ASK_INTERMEDIATE = """
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
PROMPT_MICROSERVICES_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in microservices architecture, distributed systems, event-driven design, API gateway patterns, resilience engineering, and container orchestration, you are given a list of real world scenarios and proficiency levels for Microservices development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase, implement a new feature or improve existing functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years microservices experience)
- **CRITICAL TIME BUDGET**: The total task time is 45 minutes. The candidate needs ~5 minutes to verify and test their implementation. So the actual implementation work must be completable in ~40 minutes by an intermediate-level developer (with AI assistance allowed).
- **CRITICAL SCOPE & DEPTH**: The task must ask the candidate to implement only 2-3 things, NOT 3-4 or more. However, each thing must be genuinely complex and require deep intermediate-level thinking to solve — not just boilerplate wiring. Prefer DEPTH over BREADTH. For example: one well-designed resilience pattern with proper edge-case handling is better than three shallow feature implementations. The candidate should spend most of their time reasoning about the right approach, not just writing more code.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate expertise in a FEW of these areas (pick 2-3 that align with the scenario, not all):
  - **Service Decomposition**: DDD-based bounded contexts, service splitting strategies, shared-nothing architecture
  - **API Design**: RESTful API versioning, GraphQL for service composition, OpenAPI/Swagger documentation, API gateway patterns (Kong, NGINX, Spring Cloud Gateway)
  - **Inter-Service Communication**: Synchronous (REST, gRPC) and asynchronous (Kafka, RabbitMQ) messaging, event-driven architecture, CQRS patterns
  - **Resilience Patterns**: Circuit breakers (Resilience4j, Hystrix), retries with backoff, bulkheads, timeouts, fallback mechanisms
  - **Service Mesh & Observability**: Distributed tracing (Jaeger, Zipkin), Prometheus metrics, structured logging, correlation IDs, health checks
  - **Data Management**: Database per service, saga patterns for distributed transactions, eventual consistency, event sourcing basics
  - **Security**: OAuth2/JWT authentication across services, API gateway auth, service-to-service mTLS, rate limiting
  - **Deployment**: Docker Compose for multi-service dev, Kubernetes basics, canary/blue-green deployment concepts
  - **Testing**: Contract testing (Pact), integration testing across services, WireMock for service stubs
  - **Performance**: Caching strategies (Redis), connection pooling, database indexing, latency optimization across service calls
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern development best practices and current framework standards.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- The task should involve 2-3 microservices with both synchronous and asynchronous communication patterns. Keep the service count low so the candidate can focus on depth of implementation rather than breadth of wiring.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate microservices proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Microservices task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years microservices experience), keeping in mind that AI assistance is allowed.
- Tests practical microservices skills that require architectural thinking, resilience design, and inter-service communication patterns
- Time constraints: Each task should be finished within 45 minutes total (including ~5 minutes for the candidate to verify/test their work, so ~40 minutes of actual implementation).
- **SCOPE CONSTRAINT**: Limit the task to 2-3 focused implementation objectives that are individually complex and deep. Do NOT create tasks with 4+ shallow objectives. Each objective should require the candidate to think deeply about the right architectural approach, not just write boilerplate code. Fewer things, higher complexity per thing.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-service architectures that leverage both sync and async patterns for real-world scenarios
- Should test the candidate's ability to reason deeply about 2-3 of: service boundaries, resilience patterns, distributed data, or observability — not all of them in one task

## Technology Stack Choice:
- The technology stack (language + framework) for each microservice MUST be determined by the real-world scenario and competencies provided in the input — do NOT hardcode a specific language
- The scenario text (from {real_world_task_scenarios}) or competency names will specify which language/framework to use (e.g., Java, Node.js, Python, Rust, C#, Go, etc.)
- If the scenario does not explicitly specify a language, infer the most appropriate one from the competencies input
- Different services in the same task may use different tech stacks if the scenario calls for it (polyglot microservices)
- Include the appropriate build files and dependency management for whatever language is chosen (e.g., pom.xml for Java, package.json for Node.js, requirements.txt for Python, Cargo.toml for Rust, go.mod for Go, .csproj for C#, etc.)
- Use idiomatic project structure and libraries for the chosen language (e.g., Spring Cloud for Java, express/fastify for Node.js, FastAPI for Python, actix-web for Rust, ASP.NET for C#, etc.)
- For resilience patterns, use language-appropriate libraries (Resilience4j for Java, opossum for Node.js, tenacity for Python, etc.)

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate microservices architectural skills
- The code files generated must be valid and executable with `docker-compose up --build`.
- Provide a realistic multi-service project structure that mimics real-world applications
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper service boundaries, resilience patterns, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper microservices architecture
- Starter code should include docker-compose.yml with 2-3 services, databases, and optionally message brokers
- Each service should have its own directory with its own code, dependencies, and Dockerfile
- Use the correct base Docker image for whatever language is chosen (e.g., openjdk:17-slim for Java, node:18-alpine for Node.js, python:3.11-slim for Python, rust:1.75-slim for Rust, mcr.microsoft.com/dotnet/sdk:8.0 for C#, golang:1.22-alpine for Go)
- Include some existing services that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architecture
- The starter code should be substantial enough that the candidate spends time on the 2-3 deep implementation objectives, not on boilerplate setup
- If Redis or message brokers are needed, include them in docker-compose.yml

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, all containers must start successfully, databases must be seeded, message brokers must be healthy, and all services must be ready. Deployment must NOT fail. The candidate receives a working multi-service environment from the start; their only job is to fix or improve the given microservices problem.

### docker-compose.yml
- Must include 2-3 microservice definitions plus databases, and optionally message brokers (Kafka, RabbitMQ), Redis, etc.
- Hardcoded configuration — no `.env` file references, no environment variable placeholders for service config.
- Each microservice must expose its API port to the host.
- **No `version:` field** in the compose file.
- Services must have proper `depends_on` with health checks so they start in correct order.
- If a database is used, mount `init_database.sql` to the appropriate entrypoint directory (e.g., `/docker-entrypoint-initdb.d/` for PostgreSQL).
- Use named volumes for database and message broker data persistence.

### run.sh
Generate this script with the following EXACT structure and behaviour:

**run.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- Run `docker-compose up -d --build` to start all services.
- Include a health check loop that waits for each infrastructure component and service to be ready:
  - Check database health first (e.g., `docker-compose exec -T postgres psql` for PostgreSQL).
  - Check message broker health if applicable (e.g., Kafka, RabbitMQ management API).
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

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Multi-service Docker Compose with databases and infrastructure)
  - .gitignore (Standard exclusions for chosen tech stack(s))
  - Per-service directories with Dockerfiles, dependency files, and source code
  - Database initialization scripts if needed (init_database.sql)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial microservices architecture that candidate needs to complete/extend

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name in <verb><subject> format within 50 characters and task related, e.g. 'Optimize Order Processing Pipeline' ",
   "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Event-Driven Order Pipeline with Saga Pattern', 'Fix Circuit Breaker in Payment Service Gateway', 'Refactor Monolithic Checkout into Resilient Microservices'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Service & Database Access (API endpoints, DB credentials, broker URLs, inter-service communication details), Objectives, How to Verify, and Helpful Tips",
      ".gitignore": "Proper exclusions for chosen tech stack(s)",
      "docker-compose.yml": "Docker Compose with multiple services, databases, and infrastructure — follows rules above",
      "run.sh": "Deploy script — follows run.sh rules above exactly",
      "kill.sh": "Cleanup script — follows kill.sh rules above exactly",
      "<service-name>/Dockerfile": "Dockerfile for each service — use appropriate base image for the chosen language (e.g., openjdk for Java, node for Node.js, python for Python, rust for Rust, mcr.microsoft.com/dotnet for C#, golang for Go)",
      "<service-name>/<dependency-file>": "Language-appropriate dependency file (pom.xml, package.json, requirements.txt, Cargo.toml, go.mod, .csproj, etc.)",
      "<service-name>/src/...": "Source code files following idiomatic project structure for the chosen language",
      "gateway/Dockerfile": "API gateway Dockerfile if applicable — use appropriate language/framework",
      "gateway/src/...": "Gateway source files if applicable",
      "init_database.sql": "Database initialization scripts",
      "additional files": "Other source files as needed — repeat service directory pattern for each microservice (2-3 services)"
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem requiring a distributed microservices solution, (2) the specific implementation, refactoring, or fix goal involving inter-service communication, resilience patterns, or event-driven architecture, and (3) the expected outcome emphasizing correctness, service isolation, scalability, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like Docker, Docker Compose, the chosen framework(s), microservices architecture, distributed systems concepts, resilience patterns, message brokers, API design, testing strategies.",
  "answer": "High-level solution approach for solving task",
  "hints": "a single line hint focusing on microservices architectural approach or distributed system pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}


## Code file requirements:
- Generate realistic multi-service folder structure with separate directories per service
- Code should follow modern best practices and demonstrate intermediate-level microservices patterns
- Use appropriate framework annotations, dependency injection, and configuration patterns
- Focus on modern framework features and microservices development best practices
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing services that need to be extended or integrated with new patterns
- The core architectural decisions, resilience patterns, inter-service communication, data management, or observability solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add circuit breaker here" or "Should implement saga pattern" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be buildable and bootable with docker-compose, but will require architectural completion to function properly
- Provide realistic dependencies in build files that intermediate developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for the chosen tech stack(s). Include build outputs appropriate for the language (target/ for Java, node_modules/ for Node.js, __pycache__/ for Python, target/ for Rust, bin/obj/ for C#, vendor/ for Go, etc.), IDE configurations (.idea/, .vscode/, .vs/, .eclipse/, *.iml), compiled files, environment files (.env, application-local.properties), database files, log files, Docker volumes, and other common development artifacts for the specific language(s) used.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Service & Database Access
   - Objectives
   - How to Verify
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific microservices task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own. Keep it open-ended so that the candidate's architectural decisions and design choices can be evaluated.
- README should NOT be heavy — each section should have only the essential points (4-6 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)
- Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations
- Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
- Objectives should describe WHAT needs to work, not HOW to implement it

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why microservices architecture considerations matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper distributed architecture is crucial.


### Service & Database Access

Provide all the access details the candidate needs to interact with the running environment:
  - **API endpoints for each microservice**: List each service name, its host as `<DROPLET_IP>`, and its exposed port (e.g., "Order Service: http://<DROPLET_IP>:3001")
  - **Database connection details**: For each database used, provide the host (`<DROPLET_IP>`), exposed port, database name, username, and password. Mention that candidates can use any preferred database client tools (e.g., pgAdmin, DBeaver, psql, mongosh, redis-cli)
  - **Message broker access** (if applicable): Provide connection details for Kafka, RabbitMQ, etc. (e.g., "RabbitMQ Management UI: http://<DROPLET_IP>:15672, credentials: guest/guest")
  - **Other service endpoints**: If the task includes Redis, API gateways, monitoring UIs (Prometheus, Jaeger), or any other infrastructure, list their access URLs
  - **Inter-service communication**: Briefly note that services communicate internally via Docker network using service names (e.g., "Services communicate internally using Docker service names — the Order Service calls the Inventory Service at http://inventory-service:3002")
  - Use `<DROPLET_IP>` as a placeholder for the actual IP — never hardcode an IP address
  - Keep this section factual and concise — just the connection details, no implementation hints

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate microservices level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and microservices code quality metrics
  - Include expectations for service design, resilience, inter-service communication, and observability
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Implement services that communicate reliably even when downstream dependencies are slow or unavailable"
    * "Design service boundaries that maintain data consistency across distributed operations"
    * "Create an architecture where adding a new service does not require changes to existing services"
    * "Ensure the system provides enough observability to diagnose issues across service boundaries"
  - Objectives should be measurable but not prescribe specific frameworks or approaches
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify

Give the candidate concrete, actionable ways to confirm each objective works — tell them exactly what API call to make, what response to expect, what to check in the database, cache, or message broker. Do NOT reveal HOW to implement the solution, but DO tell them HOW to TEST it.

Each bullet should follow this pattern: **action to take → expected observable result**

Examples of proper framing:
  * "Send 20 concurrent POST /transactions/transfer requests of $10 each from a wallet with $100 balance — exactly 10 should succeed (200) and 10 should be rejected (409), and the wallet balance should be exactly $0"
  * "Stop the Notification Service container, then call POST /orders — the order should still be created successfully with a status indicating notification is pending"
  * "Call GET /wallets/{{id}}/ledger after a failed transfer that was compensated — you should see a debit entry followed by a compensation credit entry with the same reference_id"
  * "Query the alerts table after sending a telemetry reading below the min threshold — a new ACTIVE alert should exist for that device and rule"
  * "After calling GET /payments/{{id}} twice within 60 seconds, check Redis — the second call should be served from cache (faster response, no DB query in logs)"

Rules:
  - Each bullet = one specific test the candidate can perform using curl, Postman, a DB client, or redis-cli
  - Mention the exact endpoint path, expected HTTP status code, and what to look for in the response, database, cache, or broker
  - Include at least one concurrency test (concurrent requests → expected exact count of successes/failures)
  - Include at least one failure/degradation test (stop a service container → expected graceful behavior)
  - Do NOT reveal implementation approach — only describe the test and expected outcome
  - **CRITICAL**: Keep to 4-6 concise bullets. Tell them WHAT to test and WHAT to expect, never HOW to implement.

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how to design services that are independently deployable and loosely coupled
  - Mention thinking about how to handle failures and timeouts in distributed communication
  - Hint at considering how data consistency is maintained when multiple services own different data
  - Recommend exploring how to trace requests as they flow through multiple services
  - Suggest thinking about how to version APIs without breaking existing consumers
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward microservices architectural thinking, not provide direct solutions

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (docker-compose up, mvn spring-boot:run, npm start, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific framework APIs or annotations that reveal the solution
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific class implementation details that would give away the solution
  - Controller/Service method signatures that would reveal the solution
  - Specific infrastructure configuration values that would dictate the implementation
  - Phrases like "you should implement", "add a circuit breaker using X", "create a Kafka consumer"

## CRITICAL REMINDERS:
- `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
- **code_files** must include run.sh, kill.sh, docker-compose.yml, Dockerfiles, and source files for each service
- **Deployment must succeed in one go** — After run.sh, all containers must be healthy, databases seeded, message brokers ready, all services accessible. The candidate only fixes or improves the microservices problem, not deployment.
- **run.sh** must follow the exact rules above: health check loops for DB, brokers, and each service, fail with logs on error
- **kill.sh** must follow the exact rules above: docker-compose down, force-stop containers, prune volumes/images/system, rm -rf /root/task, all with `|| true`
- **docker-compose.yml must NOT have a `version:` field** — use modern compose format
- **SCOPE**: Task must have exactly 2-3 implementation objectives — NOT more. Each objective must be individually complex and require deep intermediate-level reasoning. Prefer depth over breadth. The candidate should be able to complete implementation in ~40 minutes and have ~5 minutes to verify/test.
- **COMPLEXITY**: Each objective should test architectural thinking, not just code-writing speed. The challenge is in figuring out the RIGHT approach, not in writing MORE code.
"""
PROMPT_REGISTRY = {
    "Microservices (INTERMEDIATE)": [
        PROMPT_MICROSERVICES_CONTEXT_INTERMEDIATE,
        PROMPT_MICROSERVICES_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_MICROSERVICES_INTERMEDIATE_INSTRUCTIONS,
    ],
}
