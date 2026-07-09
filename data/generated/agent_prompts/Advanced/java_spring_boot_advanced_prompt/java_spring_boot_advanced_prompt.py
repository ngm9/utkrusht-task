# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_JAVA_SPRING_BOOT_CONTEXT_ADVANCED = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_ADVANCED = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java Spring Boot assessment task.

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
- The task should assess advanced Spring Boot engineering judgment across application architecture, persistence, transactions, security, resilience, observability, deployment readiness, and testing strategy as appropriate to the selected scenario

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and production-style Spring Boot problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation, debugging, optimization, refactor, or design remediation required, the expected deliverables, and how it aligns with ADVANCED Java Spring Boot proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_SPRING_BOOT_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java, Spring Boot, Spring Data JPA, Spring Security, distributed systems, observability, and production-grade backend services, you are given a list of real world scenarios and proficiency levels for Java Spring Boot.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an advanced level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to operate like an advanced Java Spring Boot engineer with 6+ years of experience who can independently diagnose difficult framework, persistence, performance, security, reliability, and runtime issues in production-style services.
The generated task should allow the reviewer to observe whether the candidate can reason about Spring Boot application structure, dependency injection, transaction boundaries, JPA behavior, REST contracts, resilient integrations, configuration, logging, metrics, testability, and deployment readiness without being handed a prescriptive implementation path.
The task should be realistic enough that the candidate must make trade-offs, clean up flawed starter code, improve behavior under realistic constraints, and explain why their chosen approach is safe, maintainable, observable, and production-ready.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, optimize a slow or unreliable path, fix complex bugs in the existing codebase, harden a production-facing service, or improve existing functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with ADVANCED proficiency level (6+ years Java Spring Boot experience).
- **CRITICAL**: This must be an advanced Spring Boot task, not a basic annotation recall exercise, syntax puzzle, framework trivia question, or setup-only task.
- **CRITICAL**: The task must be completable within {minutes_range} minutes, so keep the codebase focused while making the underlying engineering problem deep enough to reveal advanced judgment.
- **CRITICAL**: The generated task must include a FULLY FUNCTIONAL Spring Boot project and a FULLY POPULATED PostgreSQL-backed local infrastructure environment that runs from /root/task.
- **CRITICAL**: The candidate should need to reason through the problem from observable symptoms, tests, logs, metrics, API behavior, database behavior, or code structure rather than following explicit implementation steps.
- For ADVANCED level of proficiency, the questions should test deep practical understanding and require candidates to demonstrate several of the following Spring Boot capabilities:
  - **Core Java and Clean Design**: OOP, generics, streams, immutability, exception design, concurrency, SOLID principles, clean package boundaries, and maintainable service-layer logic.
  - **Spring Core and Boot Internals**: bean lifecycle, dependency injection, scopes, profiles, configuration properties, autoconfiguration, component scanning boundaries, circular dependency remediation, and proxy limitations.
  - **REST and Serialization**: Spring MVC or WebFlux API design, DTO boundaries, validation, exception mapping, advanced Jackson behavior, versioning, and consistent response contracts.
  - **Persistence and Transactions**: Spring Data JPA mapping, repository design, entity lifecycle, fetch strategies, N+1 diagnosis, pagination, migrations, transaction propagation/isolation, locking, and data consistency.
  - **Security**: Spring Security configuration, authentication and authorization, JWT or OAuth2/OIDC where appropriate, CORS/CSRF decisions, secure error handling, sensitive endpoint protection, and secure-by-default behavior.
  - **Integrations and Resilience**: WebClient or RestTemplate configuration, timeouts, retries, circuit breakers, bulkheads, fallbacks, messaging concepts, idempotency, and failure-mode design.
  - **Performance and Reliability**: connection pool tuning, thread pool implications, JVM/runtime considerations, stateless service design, rate limiting, graceful degradation, and database query optimization.
  - **Observability**: Spring Boot Actuator, Micrometer metrics, structured logging, MDC correlation IDs, health indicators, traces, and using runtime evidence to guide improvements.
  - **Testing Strategy**: unit, slice, integration, contract, MockMvc, TestRestTemplate, Testcontainers-style thinking, and CI/CD-friendly verification without making the task primarily about test framework mechanics.
  - **Deployment Readiness**: Docker packaging, runtime profiles, configuration separation, health checks, graceful shutdown, dependency management, and secure handling of runtime configuration.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Java best practices using Java 17+ or Java 21 and current Spring Boot 3.x development standards.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Spring Boot documentation, Java documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect advanced Java Spring Boot proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches, identify risks, choose the most appropriate production-grade solution, and communicate trade-offs clearly.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Java Spring Boot task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for ADVANCED proficiency level (6+ years Java Spring Boot experience), keeping in mind that AI assistance is allowed.
- Tests practical Spring Boot engineering skills that require architectural thinking, debugging, optimization, security or reliability judgment, and production-style implementation.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on a realistic Spring Boot service backed by PostgreSQL where the candidate must improve, fix, or extend a meaningful production path without being handed the exact implementation.
- Prefer scenarios involving advanced but bounded work such as eliminating JPA performance problems, repairing transaction or proxy behavior, hardening a REST endpoint, adding resilient external-call behavior around persisted workflows, improving observability, or making configuration and deployment behavior safer.
- Do not create a task whose primary difficulty is remembering exact annotations, property names, command-line flags, build-tool setup, or test-framework syntax.
- The generated project must include Maven or Gradle build files, Spring Boot application code, resource configuration, tests or verification scaffolding, local infrastructure, and concise candidate-facing README content.
- The Spring Boot starter code should be compilable and runnable, but the specific production issue should remain unresolved until the candidate completes the task.
- The task should include observable symptoms such as slow endpoint behavior, excessive SQL statements, inconsistent error responses, fragile transaction behavior, missing correlation IDs, insecure actuator exposure, blocking remote calls, or incorrect persistence semantics.
- The generated code should include realistic package structure such as src/main/java/com/company/domain, controller, service, repository, config, exception, dto, security, observability, and integration packages as appropriate to the scenario.
- The generated code should include realistic Spring Boot dependencies in pom.xml or build.gradle that advanced developers should be familiar with, such as spring-boot-starter-web, spring-boot-starter-data-jpa, spring-boot-starter-validation, spring-boot-starter-actuator, spring-boot-starter-security if needed, spring-boot-starter-webflux if needed for external calls, micrometer dependencies if useful, flyway-core or liquibase-core if migrations are part of the task, and postgresql.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## Infrastructure Requirements
The task is infra-shaped and must ship a local PostgreSQL-backed Spring Boot project with Docker-based infrastructure. The generated files must allow the task runner to start the required local services consistently in the E2B sandbox.

### Docker-compose Instructions
- Include a docker-compose.yml file for the Spring Boot application and PostgreSQL datastore used by the scenario.
- **MUST NOT include any version specification** in docker-compose.yml.
- **MUST NOT include environment variables or .env file references** in docker-compose.yml.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore or application port exposed to the host.
- The PostgreSQL service must use a stable image and must be configured so the application can connect to a local database without requiring any manual setup outside the generated files.
- The application service may be included in docker-compose.yml and should depend on PostgreSQL health readiness if containerized.
- Use healthchecks where appropriate so candidates can observe whether infrastructure is ready.
- Do not include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic.

### init_database.sql Instructions
- Include an init_database.sql file that creates the schema and seeds enough realistic data for the selected scenario to be testable immediately.
- The seed data must be FULLY POPULATED and representative enough to expose the intended Spring Boot issue, such as N+1 queries, inefficient pagination, transaction conflicts, serialization problems, security edge cases, or resilience-related state transitions.
- The SQL must be deterministic and safe to run in a fresh local PostgreSQL container.
- The SQL should not contain the final optimized solution if the task is about schema, indexing, or query optimization. Leave the candidate enough room to make the advanced design choice.
- If the task uses Flyway or Liquibase migrations in the application, ensure init_database.sql and the migration files do not conflict. Prefer using init_database.sql for base database creation and migrations for application-owned schema evolution when both are included.

### Run.sh Instructions
- Include a run.sh file located at /root/task/run.sh.
- run.sh must be executable in content and must start the local task environment from /root/task.
- run.sh must use `docker compose up -d` to start PostgreSQL and any containerized application service required by the task.
- run.sh must not run apt-get install, pip install, npm install, SDK installation, or any runtime installation commands.
- run.sh must not reference .env files or require secrets.
- run.sh should print concise verification information such as the application URL, health endpoint, or test command, without revealing the solution.
- Do not include kill.sh.

### Dockerfile Instructions
- Include a Dockerfile for the Spring Boot application container.
- The Dockerfile should build or run the application using the generated Maven or Gradle project in a production-like but assessment-friendly way.
- The Dockerfile should avoid unnecessary packages and should not install unrelated system dependencies.
- The Dockerfile should support a local Docker Compose workflow and should not contain secrets.
- The Dockerfile must not hide the task problem by applying the required candidate solution during image build.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pom.xml (Maven dependencies with Spring Boot starters) OR build.gradle (Gradle dependencies with Spring Boot plugin)
  - .gitignore (Standard Spring Boot, Java, Maven/Gradle, Docker, and IDE gitignore)
  - Dockerfile (Spring Boot application container definition)
  - docker-compose.yml (PostgreSQL and application service composition with localhost-only host bindings)
  - run.sh (Script that starts the local Docker Compose environment from /root/task)
  - init_database.sql (PostgreSQL schema and seed data for the scenario)
  - application.properties or application.yml (Spring Boot configuration)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial production-style Spring Boot architecture that candidate needs to complete, refactor, optimize, secure, or harden.
  - Include realistic folder structure such as src/main/java/com/company/package/, src/main/resources/, src/test/java/, and src/main/resources/db/migration/ if migrations are used.

## Code file requirements
- Generate realistic Spring Boot folder structure under /root/task with src/main/java, src/main/resources, and src/test/java.
- Code should follow modern Java best practices and demonstrate advanced Spring Boot architecture.
- Use appropriate Spring annotations, dependency injection, configuration properties, validation, exception handling, repository boundaries, and observability patterns where relevant.
- Use Java 17+ or Java 21 and Spring Boot 3.x conventions throughout.
- **CRITICAL**: The generated code files should provide partial implementations that require advanced architectural completion.
- Include existing controllers, services, repositories, entities, DTOs, configuration classes, exceptions, and integration clients that the candidate needs to work with or extend.
- The core architectural decisions, transaction boundary fixes, query optimization, security hardening, resilience policy, observability instrumentation, serialization boundary, or deployment-readiness improvements that the candidate needs to implement MUST be left for the candidate to design.
- Starter code must compile and start, but the relevant endpoint, workflow, or verification path should exhibit the intended problem until the candidate fixes it.
- If the task is to fix bugs, make sure the starter code has logical bugs, production risks, or architectural issues, not syntactic errors.
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper Spring Boot architecture and production-quality decisions.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT include comments like "Add @Transactional here", "Use EntityGraph here", "Configure circuit breaker here", "Add DTO projection here", or "Implement retry here".
- DO NOT add comments that give away hints or solution or implementation details.
- The generated project structure should be bootable, but will require advanced Spring Boot completion to satisfy the task outcomes.
- Include tests or verification scaffolding only if they help reveal observable behavior without encoding the full answer.
- Avoid hardcoded secrets in source files, logs, Docker files, README content, and configuration.
- Ensure generated code uses constructor injection as the default dependency injection style unless the scenario intentionally includes a flawed pattern for the candidate to refactor.
- Ensure controllers do not contain domain-heavy business logic unless the scenario intentionally includes that smell for the candidate to improve.
- Ensure any database-backed task has enough seed data to make performance, consistency, or serialization issues observable.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for advanced Spring Boot projects including target directories, build directories, IDE configurations (.idea/, .vscode/, .eclipse/, *.iml), compiled class files (*.class), JAR/WAR files, log files, Spring Boot local files (*.log, application-local.properties), H2 database files (*.db), Docker override files, OS files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

- The README.md file content MUST be fully populated with meaningful, specific content.
- Task Overview section MUST contain the exact business scenario from the task description.
- ALL sections must have substantial content - no empty or placeholder text allowed.
- Content must be directly relevant to the specific Spring Boot task scenario being generated.
- Use concrete business context, not generic descriptions.
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions.
- Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations.
- Do NOT specify exact implementation approaches, specific APIs, class names, method signatures, property names, migration names, query annotations, security configuration snippets, or resilience library calls.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### Task Overview
- Task Overview must be 3-4 meaningful sentences. No bullet list.
- It must describe the business scenario, current state, and why the problem matters.
- It must NEVER be empty.
- It must use concrete business context and explain the operational or user impact.
- It must contain NO bold time-budget callouts.
- It must not reveal the specific implementation fix.

### Objectives
- Objectives must contain 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: 'Improve query performance.'
- GOOD: 'The product search endpoint returns results in 4-6 seconds under normal load; after your changes it should respond in under 500ms for typical query patterns.'
- Objectives should be measurable but should not prescribe specific Spring Boot APIs, annotations, libraries, SQL constructs, or implementation approaches.
- Objectives should cover functional correctness plus advanced qualities such as maintainability, data integrity, security, observability, performance, or resilience where relevant to the chosen scenario.

### Helpful Tips
Provide practical guidance without revealing specific implementations.
- Helpful Tips must contain 4-5 bullets max.
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, annotation, pattern, data structure, query mechanism, or algorithm that solves the task.
- Frame suggestions around principles, symptoms, and outcomes rather than specific implementations.
- Examples of proper framing:
  - "Consider how data crosses the boundary between persistence models and public API responses."
  - "Think about which runtime symptoms indicate work is happening in the wrong layer."
  - "Explore how failures in one dependency should affect the user-visible workflow."
  - "Review whether operational signals would help explain the issue during an incident."
  - "Analyze whether the current structure keeps business rules, infrastructure concerns, and web concerns appropriately separated."

### How to Verify
- How to Verify must contain 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as test output, response shape, latency observation, log line, metric reading, database state, or error response.
- Verification should help the candidate prove the service is correct, safe, maintainable, and production-ready for the selected scenario.
- Do not include setup commands, Docker commands, Maven commands, Gradle commands, or exact implementation checks in the README.

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, `mvn spring-boot:run`, `gradle bootRun`, etc.)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, annotation names, property names, pattern names, query names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Controller, service, repository, security, configuration, or migration implementation details that would reveal the solution
- Database-connection details such as host, port, username, password, database name, client-tool suggestions, or connection strings
- <DROPLET_IP> placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>", "add this annotation", or "write this query"

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the Spring Boot task and is different from the human-readable title.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, clearly describing the advanced Spring Boot action and subject without duplicating the kebab-case name.",
  "question": "A detailed candidate-facing task description that explains the selected business scenario, the current broken or incomplete behavior, the expected advanced Spring Boot work, the constraints, and the deliverables without revealing the solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify, with open-ended guidance that does not reveal direct implementation details.",
    ".gitignore": "A comprehensive Spring Boot, Java, Maven or Gradle, Docker, IDE, log, build-artifact, and local-development exclusion file.",
    "pom.xml": "A Maven build file for a Java 17+ or Java 21 Spring Boot 3.x project with only the dependencies needed for the selected advanced Spring Boot scenario.",
    "build.gradle": "A Gradle build file for a Java 17+ or Java 21 Spring Boot 3.x project if Gradle is chosen instead of Maven, with only the dependencies needed for the selected scenario.",
    "Dockerfile": "A Dockerfile that builds or runs the Spring Boot application container for the local assessment environment without embedding secrets or applying the candidate solution.",
    "docker-compose.yml": "A Docker Compose definition for PostgreSQL and the Spring Boot application with no version specification, no .env references, and localhost-only host port bindings.",
    "run.sh": "An executable shell script located at /root/task/run.sh that starts the local Docker Compose environment from /root/task and prints concise non-solution verification information.",
    "init_database.sql": "A deterministic PostgreSQL initialization script that creates and seeds the scenario database with realistic data needed to expose the intended production issue.",
    "src/main/resources/application.yml": "Spring Boot configuration for datasource, JPA, logging, actuator, security, integration, or profile behavior needed by the task without hardcoded secrets.",
    "src/main/java/com/company/Application.java": "The Spring Boot main application class with the minimal bootstrapping needed for the generated project.",
    "src/main/java/com/company/controller/ControllerClass.java": "REST controller code exposing the scenario endpoint or workflow with realistic request and response boundaries but without the final solution logic.",
    "src/main/java/com/company/service/ServiceClass.java": "Service-layer code containing the central business workflow, flawed behavior, or incomplete advanced logic the candidate must improve.",
    "src/main/java/com/company/repository/RepositoryClass.java": "Spring Data repository interfaces or custom repository scaffolding relevant to the persistence portion of the selected scenario.",
    "src/main/java/com/company/domain/Entity.java": "JPA entity classes and relationships that model the selected scenario while leaving performance, serialization, or transaction improvements for the candidate.",
    "src/main/java/com/company/dto/DtoClass.java": "DTO classes for public API boundaries, validation, or response shaping needed by the scenario without giving away the complete fix.",
    "src/main/java/com/company/config/ConfigClass.java": "Configuration classes for Spring Boot, persistence, security, web, observability, or integration concerns needed to make the project realistic.",
    "src/main/java/com/company/exception/ExceptionHandlerClass.java": "Custom exception and global error-handling scaffolding for consistent API behavior where relevant to the scenario.",
    "src/main/java/com/company/integration/ClientClass.java": "External client scaffolding if the selected scenario includes remote HTTP or service integration behavior.",
    "src/main/java/com/company/observability/ObservabilityClass.java": "Logging, correlation, metrics, or health scaffolding if the selected scenario includes operational visibility concerns.",
    "src/main/resources/db/migration/V1__schema.sql": "Flyway or Liquibase migration files if application-managed migrations are appropriate for the selected scenario.",
    "src/test/java/com/company/ServiceOrControllerTest.java": "Focused test or verification scaffolding that exposes expected behavior without encoding the full implementation answer."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the main design changes, Spring Boot concepts, persistence or integration corrections, observability improvements, security considerations, and verification strategy expected from a strong advanced candidate.",
  "definitions": "An object mapping important Spring Boot, Java, persistence, security, resilience, observability, and deployment terms used in the task to concise definitions that help evaluators and candidates align on terminology.",
  "hints": "A single line hint on what a good advanced-level investigation could include, nudging toward symptoms, boundaries, and trade-offs without naming the specific fix, API, annotation, query, library, or pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable functional correctness, performance, reliability, security, observability, and maintainability improvements. Use simple english and include one line that says: Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.",
  "pre_requisites": "Exactly 2-3 concise bullets describing the required Java and Spring Boot runtime or toolchain, the local repository or Docker environment expectation, and any non-obvious domain knowledge needed for the scenario, with each bullet under 120 characters.",
  "short_overview": "Exactly 3 plain sentences: the first sentence states what is being built or repaired, the second sentence states what the candidate must do, and the third sentence states what success looks like, with no label prefixes."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, human-readable, and different from `name`.
4. **code_files** must include README.md, .gitignore, Maven or Gradle build file, Dockerfile, docker-compose.yml, run.sh, init_database.sql, Spring Boot configuration, Java source files, and relevant tests or verification scaffolding.
5. **README.md** must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no additional README sections.
6. **README.md** must not include setup commands, database connection details, direct implementation guidance, specific solution APIs, or code snippets.
7. **docker-compose.yml** must not include a version specification and must bind exposed ports to localhost only with `127.0.0.1:<port>:<port>`.
8. **run.sh** must use `docker compose up -d`, must reference /root/task as the base directory, and must not include installation commands.
9. **Do not include kill.sh** because E2B sandboxes are destroyed as a whole.
10. **Starter code** must be runnable and realistic but must NOT contain the final solution.
11. **NO comments in code** that reveal the solution or give hints.
12. **outcomes** must include one line explicitly stating: Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.
13. **short_overview** must be exactly 3 plain sentences with no label prefixes.
14. **hints** must be a single line and must not give away the specific fix.
15. The task must stay within advanced Java Spring Boot competency scope and must be completable within the allocated time.
"""

PROMPT_REGISTRY = {
    "Java - Spring Boot (ADVANCED)": [
        PROMPT_JAVA_SPRING_BOOT_CONTEXT_ADVANCED,
        PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_ADVANCED,
        PROMPT_JAVA_SPRING_BOOT_ADVANCED_INSTRUCTIONS,
    ],
}