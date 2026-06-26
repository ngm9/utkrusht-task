# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_JAVA_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Advanced Java assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Advanced Java implementation, optimization, debugging, or architectural improvement required, the expected deliverables, and how it aligns with ADVANCED Java proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java, Spring Boot, JVM performance, concurrency, enterprise persistence, and production-grade service architecture, you are given a list of real world scenarios and proficiency levels for Java.
Your job is to generate a task where a candidate is presented with a Java Spring Boot application backed by PostgreSQL with a BASIC WORKING SETUP that needs to be properly diagnosed, optimized, secured, and made production-ready using advanced Java engineering practices.
The candidate's primary responsibility is to improve a working but flawed enterprise Java service. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a Java Spring Boot application with PostgreSQL persistence and a FULLY FUNCTIONAL baseline implementation that exposes realistic API behavior but contains production-level weaknesses requiring advanced Java judgment. The application includes:
- Complete REST API endpoints with business logic already implemented and functional
- FULLY POPULATED PostgreSQL schema and seed data for realistic investigation
- Spring Data JPA repositories, service classes, DTOs, controllers, and tests that provide a strong starting point
- Basic observability, logging, and application configuration that works but is not sufficient for production diagnosis
- Concurrency, persistence, memory, security, or architectural tradeoffs that are intentionally suboptimal but not syntactically broken
- **CRITICAL**: The initial deployment MUST be successful and functional - candidate explores first, then improves
- **CRITICAL**: The task must assess advanced Java engineering, not setup, installation, trivia, or framework memorization

The candidate's primary responsibility is to diagnose and improve the service at an advanced level (6+ years experience), demonstrating deep Java skill across application design, concurrency, JPA/Hibernate persistence behavior, JVM performance reasoning, secure coding, observability, and production readiness. The task completion involves delivering a robust, maintainable, high-performance solution while communicating tradeoffs through clean code, tests, and concise documentation.

## INSTRUCTIONS

### Nature of the Task
- Task must provide a working Java Spring Boot application with PostgreSQL that requires advanced Java diagnosis, optimization, and implementation work
- **CRITICAL**: The Java application, database schema, seed data, and API baseline should be FULLY functional from the start - initial deployment must succeed
- **CRITICAL**: The initial setup allows candidates to explore the application, reproduce symptoms, run tests, inspect logs, and understand the service flow before improving it
- **CRITICAL**: The task must align with ADVANCED Java proficiency (6+ years experience) and require practical design judgment, not just filling in boilerplate
- **CRITICAL**: The task should test applied Java expertise in areas such as thread safety, CompletableFuture or ExecutorService usage, JPA/Hibernate query behavior, DTO boundaries, memory allocation, logging, metrics, secure data handling, and maintainable architecture
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working Java Spring Boot application with a PostgreSQL-backed business scenario that has production-like symptoms such as high latency, N+1 queries, excessive object allocation, unsafe shared state, incomplete error handling, insufficient authorization boundaries, or weak observability
- **PROVIDE BASIC WORKING DATABASE SETUP**: Include a functional PostgreSQL schema and enough seed data to demonstrate the performance, persistence, or correctness issue without requiring external setup by the candidate
- The question should be a real-world business scenario requiring advanced Java implementation and troubleshooting skills, NOT a trick question about syntax errors
- The complexity of the task must align with advanced proficiency level (6+ years Java experience) requiring techniques such as:

  **Primary Advanced Java Focus Areas:**
  - Applying object-oriented design, encapsulation, abstraction, and modular layering to improve maintainability
  - Choosing appropriate collections, generics, streams, and functional constructs based on readability, performance, and memory tradeoffs
  - Diagnosing and fixing concurrency issues involving shared mutable state, visibility, race conditions, bounded executors, timeouts, and safe aggregation
  - Using CompletableFuture, ExecutorService, concurrent collections, synchronization strategies, or ForkJoin-style parallelism where the scenario naturally requires it
  - Improving JPA/Hibernate persistence boundaries, query efficiency, lazy loading behavior, transaction handling, DTO mapping, and repository design
  - Avoiding N+1 query patterns, excessive in-memory filtering, entity leakage through controllers, stale data risks, and inappropriate entity/domain coupling
  - Reasoning about JVM behavior, garbage collection symptoms, memory pressure, object allocation, and runtime performance without requiring vendor-specific tuning memorization
  - Strengthening observability through meaningful logs, metrics, traces, health indicators, and diagnostic signals
  - Applying secure coding practices around input validation, authorization boundaries, sensitive data exposure, injection prevention, and compliance-aware retention
  - Improving resilience and operational readiness with graceful degradation, fault isolation, timeouts, retries where appropriate, and clear error semantics
  - Writing or extending meaningful automated tests using JUnit, Mockito, and Spring Boot integration testing patterns
  - Making architecture tradeoffs explicit through maintainable code structure, design patterns, and clear boundaries

  **Acceptable Scenario Shapes:**
  - A PostgreSQL-backed e-commerce, healthcare, payments, logistics, or scheduling service with slow endpoint behavior caused by JPA query design, lazy loading, DTO leakage, or in-memory processing
  - A service integration path that calls multiple downstream clients concurrently while preserving partial results, bounded resource usage, timeout behavior, and thread safety
  - A production incident reproduction where logs, metrics, and seed data reveal memory pressure, concurrency errors, latency spikes, or insecure data exposure
  - A modular refactoring task where behavior must be preserved while improving domain boundaries, repository usage, observability, and testability

- The question must NOT include hints about specific Java APIs, exact query annotations, exact design patterns, exact data structures, or exact configuration keys needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to modern Java best practices using Java 17+ and current Spring Boot conventions
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Java documentation, Spring documentation, Hibernate documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively diagnose, reason about, implement, and validate production-grade Java improvements at an advanced level
- Tasks should involve multi-layered Java challenges that require understanding of architecture, concurrency, persistence, JVM behavior, observability, security, and performance tradeoffs
- Candidates will be encouraged to use AI to help with boilerplate or documentation lookup but not replace their own Java architecture, debugging, and optimization skills

## Code Generation Instructions:
Based on the real-world scenarios provided, create an Advanced Java task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for ADVANCED Java proficiency (6+ years experience), keeping in mind that AI assistance is allowed but should not diminish the need for deep Java problem-solving skills
- Tests practical advanced-level Java implementation, debugging, optimization, and architectural judgment
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- **CRITICAL**: The Java Spring Boot application should be COMPLETE, FUNCTIONAL, and FULLY POPULATED with PostgreSQL data before the candidate begins
- **CRITICAL**: Initial database and application setup must be FUNCTIONAL and DEPLOYABLE - the task is to improve the service, not repair broken setup
- **CRITICAL**: Starter code may include intentionally weak design, performance, security, observability, or concurrency choices, but it must not contain syntax errors or missing dependencies
- Include tests that establish baseline behavior and allow the candidate to verify their improvements
- Include realistic logs, metrics endpoints, or small load-test utilities when useful for diagnosing advanced production symptoms
- Do NOT require Kubernetes manifests, cloud provider configuration, CI/CD vendor syntax, or exact JVM flag memorization as the primary task
- Avoid asking the candidate to simply recite APIs, remember exact configuration names, or perform installation/setup work

## Infrastructure Requirements:
- MUST include a complete, fully functional Java Spring Boot application
- MUST include a PostgreSQL database service with schema and seed data that supports the selected business scenario
- MUST include working docker-compose.yml with PostgreSQL and the Java application service
- MUST include init_database.sql that creates the schema and FULLY POPULATES realistic seed data
- **CRITICAL**: Initial deployment MUST succeed - all services start correctly and baseline functionality works
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- **IMPORTANT**: The infrastructure setup is AUTOMATED and MUST work on first deployment - candidates explore, then improve
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

### Docker-compose Instructions:
  - Java Spring Boot service with PostgreSQL integration
  - PostgreSQL service with initialization mounted from /root/task/init_database.sql
  - Volume mounts for PostgreSQL data persistence
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host
  - PostgreSQL port must be bound as `127.0.0.1:5432:5432` if exposed to the host
  - Application port must be bound to localhost only, for example `127.0.0.1:8080:8080`
  - **CRITICAL**: Docker-compose must successfully start all services on first run
  - Do not include optional services that are not necessary for the selected scenario

### init_database.sql Instructions:
  - Create a PostgreSQL schema that directly supports the selected real-world scenario
  - Include realistic tables, primary keys, foreign keys, indexes where appropriate for baseline functionality, and seed data
  - Seed enough rows to make performance, query-count, pagination, concurrency, or memory issues observable without requiring huge files
  - Keep the database FULLY POPULATED and deterministic so tests and verification steps produce stable results
  - Do not include credentials, secrets, environment variable placeholders, or external connection details in the README
  - If the scenario involves sensitive data, use synthetic data only and avoid real personal or payment information
  - The schema should support advanced Java work such as DTO projection, transaction boundaries, query optimization, lazy-loading diagnosis, or consistency validation

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts all services using `docker compose up -d`
  + WAIT MECHANISM: Implements proper health checks to wait for PostgreSQL readiness and Java application readiness
  + DATABASE VALIDATION: Confirms that PostgreSQL is reachable and seeded before declaring the task ready
  + APPLICATION VALIDATION: Validates that the Spring Boot application starts and can reach the database successfully
  + TEST FEEDBACK: Optionally runs a lightweight smoke test or health endpoint check after services start
  + ERROR HANDLING: Includes proper error handling for failed service starts
  + LOCATION: All files are located in /root/task directory
  + **CRITICAL**: Must ensure complete working setup before candidate begins diagnosis or optimization
  + Do not run `apt-get install`, `pip install`, `npm install`, or other runtime installation commands

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile
- Instructions:
  1. Stop and remove all containers created by docker-compose (including PostgreSQL and the Java application)
  2. Remove all associated Docker volumes (including PostgreSQL data volumes)
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes
  6. Delete the entire `/root/task/` folder where all the files were created
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'task|java|postgres|spring') || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Java build files (`target/`, `.class files`, `.gradle/`, `build/`) are removed
  - Remove all PostgreSQL data volume directories
  - Remove any generated logs, reports, and temporary files

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

### Dockerfile Instructions
- MUST be complete and functional for a Java 17+ Spring Boot application
- Should use a practical Java base image and build/run the application reliably
- Application must successfully connect to PostgreSQL on startup using hardcoded local compose service configuration
- Basic health checks should be present where practical
- Do not include package-manager installation commands for the Java runtime or common libraries already provided by the build image
- **CRITICAL**: Dockerfile must work correctly for initial deployment

The output should be a valid json schema:
- `README.md` with concise candidate-facing task details using the required README sections
- `.gitignore` with Java, Maven/Gradle, IDE, Docker, PostgreSQL, logs, and OS exclusions
- `.dockerignore` with efficient Docker build exclusions
- `pom.xml` or `build.gradle` with Java 17+ Spring Boot dependencies
- `docker-compose.yml` with PostgreSQL and application services and no version specification
- `Dockerfile` for the Java application service
- `run.sh` for automated deployment and validation
- `kill.sh` for complete cleanup
- `init_database.sql` for PostgreSQL schema and seed data
- Java source files under `src/main/java`
- Test files under `src/test/java`
- Resource files under `src/main/resources`

## Code file requirements:
- Multiple files will be generated following a standard Spring Boot project structure
- Java code should follow modern Java 17+ best practices, Spring conventions, and clear package organization
- Use proper package structure such as `com.example.taskname.controller`, `service`, `repository`, `domain`, `dto`, `config`, and `observability`
- Include controllers, services, repositories, domain entities, DTOs, configuration, tests, and any helper classes needed for a realistic advanced Java task
- **CRITICAL**: The generated code files MUST provide a working baseline but MUST NOT contain the completed optimized solution for the core task
- **CRITICAL**: The starter application must be runnable and functional, but the candidate must still need to diagnose and improve meaningful advanced Java issues
- Do not include syntax errors, missing imports, missing dependencies, non-compiling code, empty files, or broken setup
- Do not include comments that give away hints or solutions
- Do not include comments like "Add logic here", "Use EntityGraph here", "Make this concurrent", "Fix the N+1 query", or any similar direct implementation guidance
- If comments are necessary, keep them neutral and business-oriented, not solution-oriented
- Include tests that pass for baseline behavior where appropriate and tests that reveal performance, safety, or edge-case expectations where appropriate
- Include realistic but bounded data volumes so the task remains completable within the allocated time
- The application should be immediately deployable with baseline PostgreSQL functionality working
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Java Spring Boot and PostgreSQL development that includes:
- Maven/Gradle build directories (`target/`, `build/`, `.gradle/`)
- IDE files (`.idea/`, `.vscode/`, `*.iml`, `.eclipse/`, `.settings/`)
- Java compiled files (`*.class`, `*.jar`, `*.war`)
- Log files (`*.log`, `logs/`)
- Test reports and temporary files
- Docker and local PostgreSQL data directories
- OS-specific files (`.DS_Store`, `Thumbs.db`)
- Any other standard exclusions for Java/Spring Boot/PostgreSQL development

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections, in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

### Task Overview
- This section MUST contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- Explain that the service is already deployed and functional, but has production-readiness concerns that require advanced Java investigation and improvement.
- NEVER generate empty content — always provide substantial business context relevant to the selected real-world scenario.
- NO bold time-budget callouts.
- Do not include database host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Use 4-5 bullets max.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, annotation, query technique, configuration key, or algorithm that solves the task.
- Do not directly tell candidates what to implement.

### Objectives
- Use 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Focus on correctness, latency, scalability, reliability, security, observability, maintainability, and production-level code quality where relevant.
- Do not specify exact Java APIs, class names, query annotations, framework methods, or implementation patterns.

### How to Verify
- Use 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as test output, response shape, latency observation, log line, query-count observation, memory reading, or error response behavior.
- Do not include setup commands or database connection details.
- Do not prescribe exact code, annotations, APIs, or internal implementation details to inspect.

### NOT TO INCLUDE in README
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, annotations, query techniques, configuration keys, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Database-connection details such as host, port, username, password, JDBC URL, or client-tool suggestions
- `<DROPLET_IP>` placeholders
- Excessive bullets or verbose explanations that reduce candidate discovery

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Kebab-case GitHub repository name under 50 characters that summarizes the Advanced Java task without using spaces or uppercase letters.",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 characters, clearly describing the Java system or service the candidate will improve and different from the kebab-case name.",
  "question": "Complete candidate-facing task description explaining the selected real-world business scenario, the current working baseline, the observable production symptoms, and the advanced Java outcomes expected without revealing exact implementation steps.",
  "code_files": {{
    "README.md": "Candidate-facing README content following the required sections exactly: Task Overview, Helpful Tips, Objectives, How to Verify, and NOT TO INCLUDE in README, written concisely without setup commands or solution-revealing details.",
    ".gitignore": "Comprehensive ignore file for Java, Maven or Gradle, IDE files, Docker artifacts, PostgreSQL local data, logs, test reports, temporary files, and operating-system files.",
    ".dockerignore": "Docker build ignore file that excludes build outputs, IDE files, Git metadata, local logs, test reports where appropriate, PostgreSQL data directories, and other unnecessary files from the image build context.",
    "pom.xml": "Maven build configuration for a Java 17+ Spring Boot application with web, validation, data persistence, PostgreSQL, actuator, test, and other necessary dependencies for the scenario.",
    "docker-compose.yml": "Complete working compose configuration with no version field, no environment variables or .env references, localhost-only port bindings, PostgreSQL service, Java application service, volumes, health checks, and network configuration.",
    "Dockerfile": "Complete Dockerfile that builds and runs the Spring Boot application reliably inside the compose setup without requiring manual runtime installation.",
    "run.sh": "Executable deployment script using /root/task as the base directory, starting services with docker compose up -d, waiting for PostgreSQL and application readiness, validating seed data and health, and printing clear status logs.",
    "kill.sh": "Executable idempotent cleanup script that stops compose services, removes volumes and networks, force-removes task-related images, prunes Docker resources, deletes /root/task, ignores already-removed resources with || true, and prints progress logs plus a final cleanup success message.",
    "init_database.sql": "PostgreSQL schema and deterministic seed data for the selected scenario, including realistic relational tables, constraints, indexes where useful for baseline operation, and enough data to expose the advanced Java issue.",
    "src/main/resources/application.properties": "Spring Boot configuration for the local compose application with hardcoded non-secret values suitable for the generated service, basic logging, actuator exposure, and persistence settings.",
    "src/main/java/com/example/task/Application.java": "Spring Boot main application class that starts the generated application successfully.",
    "src/main/java/com/example/task/controller/DomainController.java": "REST controller exposing the business endpoint or endpoints relevant to the scenario while delegating to service-layer logic.",
    "src/main/java/com/example/task/service/DomainService.java": "Service layer containing the working but improvable business flow where the candidate must apply advanced Java judgment without the completed solution already present.",
    "src/main/java/com/example/task/repository/DomainRepository.java": "Spring Data repository or repositories supporting the baseline persistence behavior and leaving room for candidate improvement.",
    "src/main/java/com/example/task/domain/DomainEntity.java": "Representative JPA entity classes for the selected scenario with realistic relationships and persistence mapping.",
    "src/main/java/com/example/task/dto/DomainDto.java": "DTO or response model classes used by the API boundary and expected to support safer, clearer service responses.",
    "src/main/java/com/example/task/config/AppConfig.java": "Configuration classes needed for the working baseline, such as executor, validation, persistence, or observability configuration when relevant to the task.",
    "src/test/java/com/example/task/DomainServiceTest.java": "JUnit tests covering core behavior, edge cases, and candidate-verifiable expectations without embedding the full solution.",
    "src/test/java/com/example/task/DomainIntegrationTest.java": "Spring Boot integration tests or repository tests validating database-backed behavior and observable task outcomes.",
    "Additional Java files as needed": "Any additional controllers, services, repositories, entities, DTOs, exceptions, clients, metrics helpers, or tests required to make the scenario realistic and fully functional."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the expected advanced Java reasoning, likely areas of improvement, validation strategy, and production-readiness tradeoffs without requiring a single rigid implementation.",
  "definitions": "Object mapping important Advanced Java, Spring, JPA, concurrency, JVM, observability, security, and persistence terms used in the task to concise definitions that help evaluators interpret the generated assessment.",
  "hints": "A single line nudging investigation toward the most relevant symptoms and tradeoffs without naming the exact APIs, annotations, queries, configuration keys, design patterns, or data structures needed to solve the task.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements such as correct behavior, reduced latency or query count, safe concurrency, stronger observability, secure data handling, and production-level clean code. Use simple english.",
  "pre_requisites": "Bullet list of tools and knowledge needed, including Java 17+, Maven or Gradle, Docker, Docker Compose, Spring Boot, JUnit, PostgreSQL, JPA/Hibernate fundamentals, concurrency concepts, JVM performance reasoning, observability basics, and secure coding awareness.",
  "short_overview": "Bullet list summarising the business problem, the advanced Java technical focus, and the expected outcome in simple language suitable for quickly understanding the assessment."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case and under 50 characters
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
4. **code_files** must include README.md, .gitignore, .dockerignore, pom.xml or build.gradle, docker-compose.yml, Dockerfile, run.sh, kill.sh, init_database.sql, Java source files, resource files, and test files
5. **README.md** must follow the exact structure above with Task Overview, Helpful Tips, Objectives, How to Verify, and NOT TO INCLUDE in README
6. **README.md** must not include setup commands, direct solutions, database connection details, `<DROPLET_IP>` placeholders, or solution-revealing API/library/pattern names
7. **Starter code** must be fully deployable and functional with PostgreSQL — candidate diagnoses and improves a working system
8. **outcomes** must include one bullet or line stating production-level clean code expectations including best practices, design patterns, naming conventions, exception handling, logging, and observability
9. **short_overview** and **pre_requisites** must be bullet-point lists in simple language
10. **hints** must be a single line and must not reveal the specific implementation
11. **definitions** must be an object of term-to-definition pairs, not a placeholder example
12. **Task must be completable within the allocated time** for ADVANCED proficiency (6+ years)
13. **Initial deployment MUST succeed** — the candidate explores a working system, then improves it
14. **docker-compose.yml MUST NOT include any version specification**
15. **docker-compose.yml MUST NOT include environment variables or .env file references**
16. **SECURITY-CRITICAL**: datastore ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`
17. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
"""

PROMPT_REGISTRY = {
    "Java (ADVANCED)": [
        PROMPT_JAVA_ADVANCED_CONTEXT,
        PROMPT_JAVA_ADVANCED_INPUT_AND_ASK,
        PROMPT_JAVA_ADVANCED_INSTRUCTIONS,
    ],
}