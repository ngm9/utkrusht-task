PROMPT_NODEJS_KAFKA_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
especially focusing on how Kafka is used in Node.js-based event-driven systems at an intermediate level — such as for reliable asynchronous service communication, event sourcing patterns, consumer group orchestration, dead-letter topic strategies, and production-grade message processing?
"""

PROMPT_NODEJS_KAFKA_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js and Kafka assessment task.

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

PROMPT_NODEJS_KAFKA_INTERMEDIATE = """
## GOAL
As a technical architect experienced in event-driven architectures, Node.js, and Apache Kafka, you are given a list of real-world scenarios and proficiency levels for Node.js + Kafka development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to design and implement production-grade event-driven Node.js services that communicate via Kafka at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs involving Kafka producer/consumer patterns, event-driven workflows, or distributed message processing.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The complexity of the task must align with INTERMEDIATE proficiency level (3-5 years experience in Node.js and Kafka).
- **CRITICAL TIME BUDGET**: The total task time is 45 minutes. The candidate needs ~5 minutes to verify and test their implementation. So the actual implementation work must be completable in ~40 minutes by an intermediate-level developer (with AI assistance allowed).
- **CRITICAL SCOPE**: The task must have 3-4 focused objectives that test intermediate Kafka concepts:
  - Designing multi-topic event flows with proper message key strategies for partition-based ordering
  - Implementing idempotent consumers that handle duplicate messages gracefully
  - Building retry mechanisms with dead-letter topics for failed message processing
  - Consumer group management with proper offset commit strategies (manual vs auto)
  - Error handling across async boundaries in producer/consumer pipelines
  - Backpressure handling and batch processing patterns
  - Structured logging and observability for Kafka message flows
  - Data consistency patterns between Kafka events and database state
- For INTERMEDIATE level, the scenarios should require architectural thinking and involve:
  - Multiple Kafka topics with different message flows
  - Consumer group coordination and partition-aware processing
  - Idempotent message handling and deduplication strategies
  - Dead-letter topic patterns with configurable retry policies
  - Proper error categorization (retryable vs non-retryable)
  - Database + Kafka consistency (outbox pattern or transactional writes)
  - Structured logging with correlation IDs across message flows
  - Graceful shutdown with in-flight message handling
- The task should involve 2-3 Node.js services with Kafka as the message broker. At least one service should have significant architectural issues or missing functionality that the candidate must design and implement.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools.
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem.

## Code Generation Instructions:
Based on the real-world scenarios provided, create a Node.js + Kafka task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years experience)
- Tests practical Kafka architecture and implementation skills in Node.js
- Time constraints: Each task should be finished within {minutes_range} minutes total
- At every time pick different real-world scenario from the list to ensure variety
- Focus on 2-3 Node.js services communicating via Kafka topics with intermediate-level patterns
- The task environment must use Docker Compose to run Kafka broker(s), any databases needed, and all Node.js services
- At least one service should have significant architectural issues or missing functionality

## Technology Stack:
- **Runtime**: Node.js 18+ with Express.js for REST endpoints
- **Kafka Client**: kafkajs
- **Kafka Broker**: Use `bitnami/kafka` with KRaft mode (no Zookeeper) or `confluentinc/cp-kafka` in Docker Compose
- **Containerization**: Docker and Docker Compose

## Starter Code Instructions:
- The starter code should provide a working but architecturally flawed or incomplete system.
- The code files generated must be valid and executable with `docker-compose up --build`.
- Starter code should include a docker-compose.yml with Kafka broker, all service definitions, and database services.
- Each service should have its own directory with its own code, dependencies, and Dockerfile.
- Use `node:18-alpine` as the base Docker image for Node.js services.
- **CRITICAL**: The Kafka broker must be healthy and topics must be auto-created or created via a startup script before services try to use them.
- Include enough working code that the system partially functions — the candidate extends, refactors, or fixes the problematic parts.

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, all containers must start successfully, Kafka must be ready, topics must exist, databases must be seeded (if any), and all services must be healthy. Deployment must NOT fail.

### docker-compose.yml
- Must include Kafka broker, all Node.js service definitions, and any database services.
- Hardcoded configuration — no `.env` file references.
- Each Node.js service must expose its API port to the host.
- **No `version:` field** in the compose file.
- Services must have proper `depends_on` with health checks so they start in correct order.
- Kafka must be fully ready before Node.js services start.
- Use named volumes for Kafka data and database persistence.
- Kafka environment variables must include proper listener configuration for internal Docker network communication.

### run.sh
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- Run `docker-compose up -d --build` to start all services.
- Include a health check loop that waits for Kafka to be ready.
- Then check each service health endpoint.
- If any check fails after retries, print docker-compose logs and exit with code 1.
- End with a clear success message showing the URLs for each service.

### kill.sh
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- MUST `cd /root/task` first.
- MUST run `docker-compose down --rmi all --volumes --remove-orphans`.
- MUST force-stop ALL running containers with `docker ps -q`.
- MUST explicitly remove ALL containers with `docker ps -aq`.
- MUST run `docker volume prune -f`, then `docker image prune -a -f`, then `docker system prune -a --volumes -f`.
- MUST `rm -rf /root/task` as the final step.
- Every destructive command MUST end with `|| true`.
- Print a progress message before every major step.
- End with `echo "[kill.sh] Cleanup completed."`.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Architect Idempotent Order Processing Pipeline with Kafka', 'Implement Dead-Letter Retry Strategy for Payment Events'.",
  "question": "Short description of the scenario and specific ask — what architectural issues exist and what the candidate must design/implement involving Kafka patterns",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive exclusions for Node.js, Kafka, Docker",
    "docker-compose.yml": "Docker Compose with Kafka broker, all Node.js services, and database(s)",
    "run.sh": "Deploy script — follows run.sh rules above",
    "kill.sh": "Cleanup script — follows kill.sh rules above",
    "<service-name>/Dockerfile": "Dockerfile for each service using node:18-alpine",
    "<service-name>/package.json": "Dependencies including express, kafkajs, pg/mongoose, etc.",
    "<service-name>/src/...": "Source code for each service",
    "init_database.sql": "Database initialization script if needed",
    "additional files": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list. Must include: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list describing: (1) the high-level business problem requiring event-driven communication, (2) the specific Kafka architecture/implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list examples: Node.js, Express.js, kafkajs, Docker, Docker Compose, intermediate Kafka concepts (partitioning, consumer groups, offset management, dead-letter topics, idempotency), REST API design, async/await patterns.",
  "answer": "High-level solution approach describing the Kafka architecture, message flow design, and key implementation decisions.",
  "hints": "Single line suggesting focus area for Kafka event flow design, idempotency, and error handling strategy.",
  "definitions": {{
    "Kafka Topic": "A named channel in Kafka where messages are published and consumed",
    "Consumer Group": "A set of consumers that cooperatively consume messages from topics, with each partition assigned to exactly one consumer in the group",
    "Dead Letter Topic": "A topic where messages that cannot be processed after exhausting retry attempts are sent for later analysis or manual intervention",
    "Idempotent Consumer": "A consumer designed to produce the same result regardless of how many times the same message is processed, preventing duplicate side effects",
    "Offset": "A sequential ID assigned to each message within a partition, used to track consumption progress",
    "Partition Key": "A value used to determine which partition a message is written to, ensuring messages with the same key are always sent to the same partition for ordering guarantees"
  }}
}}

## Code file requirements:
- Generate realistic multi-service folder structure with separate directories per service
- Code should follow modern Node.js best practices (ES modules or CommonJS, async/await, structured error handling)
- Use appropriate framework patterns, dependency injection, and configuration patterns
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing services that need to be extended or integrated with new Kafka patterns
- The core architectural decisions, event flow design, consumer/producer patterns, retry logic, or observability solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add consumer here" or "Should implement dead-letter topic" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be buildable and bootable with docker-compose, but will require architectural completion to function properly
- Provide realistic dependencies in package.json that intermediate developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Node.js: node_modules/, build outputs (dist/, build/), IDE configurations (.idea/, .vscode/, *.swp, *.swo), compiled files, environment files (.env), database files, log files (*.log, logs/), Docker volumes, coverage reports (.nyc_output/, coverage/), and other common development artifacts.

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
- Content must be directly relevant to the specific Kafka task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own. Keep it open-ended so that the candidate's architectural decisions and design choices can be evaluated.
- README should NOT be heavy — each section should have only the essential points (4-6 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)
- Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations
- Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
- Objectives should describe WHAT needs to work, not HOW to implement it

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why event-driven architecture considerations matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper Kafka integration is crucial.

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate Kafka level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and event-driven code quality metrics
  - Include expectations for message flow design, resilience, error handling, and observability
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Implement services that process events reliably even when downstream consumers fail or restart"
    * "Design message flows that maintain data consistency between Kafka events and database state"
    * "Ensure failed messages are captured and can be retried without losing data or processing duplicates"
    * "Provide enough observability to diagnose message processing issues across service boundaries"
  - Objectives should be measurable but not prescribe specific frameworks or approaches
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"
  
### Service & Database Access

Provide all the access details the candidate needs to interact with the running environment:
  - **API endpoints for each service**: List each service name, its host as `<DROPLET_IP>`, and its exposed port (e.g., "Order Service: http://<DROPLET_IP>:3001")
  - **Database connection details**: For each database used, provide the host (`<DROPLET_IP>`), exposed port, database name, username, and password. Mention that candidates can use any preferred database client tools (e.g., pgAdmin, DBeaver, psql, mongosh)
  - **Kafka broker access**: Provide Kafka broker connection details (e.g., "Kafka Broker: `<DROPLET_IP>:9092`"). If using a Kafka UI tool, list its access URL
  - **Inter-service communication**: Briefly note that services communicate via Kafka topics using Docker service names (e.g., "Services publish/consume events via Kafka broker at `kafka:29092` internally")
  - Use `<DROPLET_IP>` as a placeholder for the actual IP — never hardcode an IP address
  - Keep this section factual and concise — just the connection details, no implementation hints

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and event-driven architecture
  - API testing checkpoints (endpoints respond correctly, events are produced/consumed, error handling works)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how event-driven services handle failures differently from synchronous request-response
  - Mention thinking about what happens to in-flight messages when a consumer crashes mid-processing
  - Hint at considering how to ensure the same message processed twice doesn't corrupt data
  - Recommend exploring how to categorize errors that should be retried vs errors that should not
  - Suggest thinking about how to maintain consistency between database writes and Kafka publishes
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward event-driven architectural thinking, not provide direct solutions

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (docker-compose up, npm start, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific framework APIs or library methods that reveal the solution
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific implementation details that would give away the solution
  - Specific Kafka configuration values or consumer/producer code patterns
  - Phrases like "you should implement", "add a dead-letter topic using X", "create a consumer group"
  - Technology names that reveal specific solution approaches (e.g., specific retry libraries, specific patterns by name)

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **code_files** must include README.md, .gitignore, docker-compose.yml, run.sh, kill.sh, Dockerfiles, package.json, and source files for each service
3. **Deployment must succeed in one go** — Kafka must be ready, topics must exist, services must be healthy
4. **kill.sh** must follow the exact cleanup pattern specified above
5. **Task must be completable within the allocated time** for INTERMEDIATE proficiency
6. **NO comments in code** that reveal the solution
7. **Focus on 2-3 Node.js services** communicating via Kafka with intermediate patterns
8. **docker-compose.yml must NOT have a `version:` field**
9. **SCOPE**: 3-4 implementation objectives focused on Kafka architecture, idempotent processing, dead-letter patterns, and production-grade error handling
10. **INTERMEDIATE COMPLEXITY**: Tasks should require architectural decisions, not just wiring code. Candidates should reason about message ordering, delivery guarantees, and consistency patterns.
"""

PROMPT_REGISTRY = {
    "Kafka (INTERMEDIATE), NodeJs (INTERMEDIATE)": [
        PROMPT_NODEJS_KAFKA_CONTEXT_INTERMEDIATE,
        PROMPT_NODEJS_KAFKA_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_NODEJS_KAFKA_INTERMEDIATE,
    ],
}
