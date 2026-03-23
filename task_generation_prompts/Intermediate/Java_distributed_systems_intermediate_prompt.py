PROMPT_JAVA_DISTRIBUTED_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_DISTRIBUTED_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java Distributed Systems assessment task.

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
2. What will the task look like? (Describe the type of Java Distributed Systems implementation or fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_DISTRIBUTED_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java, distributed systems, message brokers (Kafka, RabbitMQ), caching (Redis), and resilience patterns, you are given a list of real world scenarios and proficiency levels for distributed systems development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase, implement a new feature or improve existing functionality related to distributed systems.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years distributed systems experience)
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Kafka Advanced**: Consumer group management, partition strategies, exactly-once semantics (transactions), Kafka Streams basics, schema registry (Avro/Protobuf), dead letter topics, manual offset management, consumer lag monitoring
  - **RabbitMQ Advanced**: Exchange types (direct, topic, fanout, headers), routing strategies, message acknowledgment modes, prefetch tuning, publisher confirms, dead letter exchanges, priority queues
  - **Redis Advanced**: Distributed locking (Redisson, RedisLock), pub/sub patterns, Redis Streams, cache invalidation strategies (cache-aside, write-through, write-behind), Redis cluster awareness, TTL management, Lua scripting basics
  - **Distributed Transactions**: Saga pattern (choreography vs orchestration), compensating transactions, outbox pattern, two-phase commit understanding, eventual consistency implementation
  - **Service Communication**: gRPC basics, REST vs messaging trade-offs, API gateway patterns, service mesh awareness, request/response vs event-driven patterns
  - **Resilience Patterns**: Circuit breaker (Resilience4j advanced config), retry with exponential backoff and jitter, bulkhead pattern, rate limiting, timeout management, fallback strategies
  - **Distributed Coordination**: Leader election basics, distributed locks, service discovery (Eureka/Consul), health checks, configuration management (Spring Cloud Config)
  - **Event-Driven Architecture**: Event sourcing basics, CQRS pattern, domain events, event schema evolution, idempotent consumers, deduplication strategies
  - **Observability**: Distributed tracing (OpenTelemetry/Zipkin/Jaeger), correlation IDs across services, centralized logging (ELK), metrics collection (Micrometer/Prometheus), alerting on distributed failures
  - **Deployment & Scaling**: Container orchestration awareness (Kubernetes basics), horizontal scaling, stateless service design, graceful shutdown with in-flight message handling, blue-green/canary deployments
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Java distributed systems best practices and current development standards. Use modern Spring Boot and Spring Cloud features appropriately.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate distributed systems proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Java Distributed Systems task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years distributed systems experience), keeping in mind that AI assistance is allowed.
- Tests practical distributed systems skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-service applications that require thoughtful distributed architecture and messaging patterns
- Should test the candidate's ability to structure a scalable distributed application with proper separation of concerns, message handling, and resilience

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate distributed systems architectural skills
- The code files generated must be valid and executable with `mvn spring-boot:run` or `gradle bootRun` alongside infrastructure services started via `docker-compose up`.
- Provide a realistic Spring Boot project structure with distributed components that mimics real-world applications
- A part of the task completion is to watch the candidate implement distributed systems best practices, design the solution correctly, demonstrate proper service communication, message handling, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper distributed architecture and messaging patterns
- Starter code should include realistic project structure with proper Spring Boot and Spring Cloud configuration
- Include some existing consumer/producer/service/controller classes that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the distributed architecture using appropriate patterns
- Include a docker-compose.yml that sets up required infrastructure services (Kafka, Redis, RabbitMQ, databases, etc.)

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pom.xml (Maven dependencies with Spring Boot starters and distributed systems libraries) OR build.gradle (Gradle dependencies)
  - .gitignore (Standard Spring Boot project gitignore)
  - docker-compose.yml (Infrastructure services: Kafka, Redis, RabbitMQ, databases as needed by the task)
  - application.properties or application.yml (Spring Boot configuration including broker/cache connection details)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial distributed systems architecture that candidate needs to complete/extend
  - Include realistic folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name in <verb><subject> format within 50 characters and task related, e.g. 'Harden Order Processing Pipeline' ",
   "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Saga Pattern for Distributed Order Fulfillment', 'Fix Kafka Consumer Lag in Real-Time Analytics Pipeline', 'Build Fault-Tolerant Event Processing with Dead Letter Handling'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed in the distributed system?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Spring Boot, Java and Maven/Gradle exclusions",
      "docker-compose.yml": "Infrastructure services setup (Kafka/Zookeeper, Redis, RabbitMQ, PostgreSQL, etc. as needed)",
      "pom.xml": "Maven dependencies with Spring Boot starters, Spring Cloud, Kafka, Redis, Resilience4j, and other distributed systems libraries",
      "src/main/resources/application.properties": "Spring Boot configuration including broker URLs, cache settings, retry configs (or application.yml)",
      "src/main/java/com/company/Application.java": "Spring Boot main application class with @SpringBootApplication and relevant @Enable annotations",
      "src/main/java/com/company/config/KafkaConfig.java": "Kafka producer/consumer configuration (if Kafka is used)",
      "src/main/java/com/company/config/RedisConfig.java": "Redis configuration and connection settings (if Redis is used)",
      "src/main/java/com/company/config/RabbitConfig.java": "RabbitMQ exchange/queue/binding configuration (if RabbitMQ is used)",
      "src/main/java/com/company/producer/ProducerClass.java": "Message producer classes for publishing events",
      "src/main/java/com/company/consumer/ConsumerClass.java": "Message consumer classes for processing events",
      "src/main/java/com/company/service/ServiceClass.java": "Service layer classes with distributed logic",
      "src/main/java/com/company/controller/ControllerClass.java": "REST controllers for API interaction",
      "src/main/java/com/company/model/Entity.java": "Domain entity and event classes",
      "src/main/java/com/company/dto/DtoClass.java": "DTO classes for API requests/responses and message payloads",
      "src/main/java/com/company/repository/RepositoryClass.java": "Repository interfaces for data persistence",
      "src/main/java/com/company/exception/CustomException.java": "Custom exception classes and @ControllerAdvice handlers",
      "src/main/resources/db/migration/V1__init.sql": "Database migration scripts (if applicable)",
      "src/test/java/com/company/ServiceTest.java": "Test class templates (if needed)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like Java, Spring Boot, Docker, message broker knowledge (Kafka/RabbitMQ), caching (Redis), distributed systems patterns, REST API design, database basics, etc.",
  "answer": "High-level solution approach for solving task",
  "hints": "a single line hint focusing on distributed systems architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good distributed systems architectural thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}


## Code file requirements:
- Generate realistic Spring Boot folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)
- Code should follow modern Java and Spring Boot best practices and demonstrate intermediate-level distributed systems patterns
- Use appropriate Spring annotations, Spring Cloud features, and dependency injection patterns
- Focus on modern Spring Boot features (Spring Boot 2.x/3.x) and distributed systems development best practices
- **CRITICAL**: The generated code files should provide partial implementations that require distributed systems architectural completion
- Include some existing producer/consumer/service classes that need to be extended or integrated
- The core architectural decisions, messaging patterns, resilience strategies, caching logic, or distributed coordination solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add retry logic here" or "Should implement circuit breaker" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be compilable and bootable, but will require distributed systems architectural completion to function properly
- Provide realistic dependencies in pom.xml/build.gradle that intermediate distributed systems developers should be familiar with (spring-boot-starter-web, spring-kafka, spring-boot-starter-data-redis, spring-boot-starter-amqp, resilience4j-spring-boot2, spring-cloud-starter-*, etc.)
- The docker-compose.yml must include all required infrastructure services (Kafka with Zookeeper, Redis, RabbitMQ, PostgreSQL/MySQL, etc.) with proper networking and health checks

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Spring Boot distributed systems projects including target directories, build directories, IDE configurations (.idea/, .vscode/, .eclipse/, *.iml), compiled class files (*.class), JAR files, log files, Spring Boot specific files (*.log, application-local.properties), H2 database files (*.db), Docker volumes, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific distributed systems task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own. Keep it open-ended so that the candidate's architectural decisions and design choices can be evaluated.
- README should NOT be heavy — each section should have only the essential points (4-6 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)
- Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations
- Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
- Objectives should describe WHAT needs to work, not HOW to implement it
- The README should give enough context for the candidate to understand the problem but leave the solution approach entirely to them

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why distributed systems architectural considerations matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper distributed systems architecture is crucial.


### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate distributed systems level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What messaging, caching, resilience, or coordination functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and distributed systems code quality metrics
  - Include expectations for message handling reliability, data consistency, fault tolerance, and observability
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Implement a messaging pipeline that reliably processes events without data loss"
    * "Design a caching strategy that improves response times while maintaining data consistency"
    * "Create a fault-tolerant service that gracefully handles downstream failures"
    * "Ensure messages are processed exactly once even in failure scenarios"
    * "Implement distributed coordination that prevents race conditions across service instances"
    * "Design an event-driven flow that decouples producers and consumers effectively"
  - Objectives should be measurable but not prescribe specific libraries or approaches
  - Should guide candidates to think about: message reliability, fault tolerance, data consistency, scalability, observability
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both distributed functionality and architectural quality
  - Message flow testing checkpoints (messages produced, consumed, retried, dead-lettered correctly)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and architectural assessment criteria
  - Data consistency verification and failure scenario validation points
  - Frame verification in terms of observable outcomes and system behaviors
  - Examples of proper framing:
    * "Verify that messages flow through the pipeline end-to-end and reach the expected destination"
    * "Simulate a downstream service failure and confirm the system recovers gracefully"
    * "Check that cached data is returned on subsequent requests and invalidated appropriately"
    * "Confirm that duplicate messages are handled without creating inconsistent state"
    * "Test the system under load and verify it scales without losing messages"
    * "Validate that distributed traces can be followed across service boundaries"
    * "Verify that failed messages land in the dead letter topic/queue for inspection"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: message flow, failure recovery, data consistency, caching behavior, observability
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific distributed systems implementation to check

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring distributed messaging patterns that promote loose coupling and reliability
  - Mention thinking about how producers, consumers, and services should interact in an event-driven architecture
  - Hint at considering how to handle message failures and retries without losing data
  - Recommend exploring how to design idempotent consumers that handle duplicate messages safely
  - Suggest thinking about caching strategies and how to keep cached data consistent with the source of truth
  - Point toward considering how to coordinate work across multiple service instances
  - Hint at exploring resilience patterns that prevent cascading failures across services
  - Recommend considering how to trace requests across distributed service boundaries
  - Suggest analyzing how to handle distributed transactions where traditional ACID guarantees are not available
  - Mention thinking about how to monitor and observe the health of a distributed system
  - Recommend exploring how to design services that can scale horizontally without state issues
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward distributed systems architectural thinking, not provide direct solutions or specific libraries
  - Frame suggestions around principles and outcomes rather than specific implementations
  - Examples of proper framing:
    * "Consider how to design your message consumers to be resilient against duplicate deliveries"
    * "Think about what happens when a downstream service is temporarily unavailable and how your system should respond"
    * "Explore approaches for maintaining data consistency across services without distributed transactions"
    * "Review how to structure your events so that consumers can evolve independently of producers"
    * "Consider how to make your services observable so failures can be diagnosed quickly in production"

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (mvn spring-boot:run, docker-compose up, gradle bootRun, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific library names or implementation approaches (e.g., "use Resilience4j", "add @KafkaListener", "configure RedisTemplate")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific class implementation details that would give away the solution to the task
  - Should not provide any particular architectural approach or distributed systems pattern to implement the solution
  - Producer/Consumer/Service method signatures that would reveal the solution
  - Specific Spring Boot or Spring Cloud configuration properties that would dictate the implementation
  - Package structure decisions that would dictate the architectural approach
  - Phrases like "you should implement", "make sure to add @Transactional", "create a consumer with @KafkaListener"
  - Specific Kafka/RabbitMQ/Redis configuration details that would reveal the solution
  - Circuit breaker or retry configuration specifics that would dictate the implementation

### CRITICAL REMINDER:
- `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display.
"""
PROMPT_REGISTRY = {
    "Java (INTERMEDIATE), Java - Distributed Systems Concurrency (INTERMEDIATE)": [
        PROMPT_JAVA_DISTRIBUTED_CONTEXT_INTERMEDIATE,
        PROMPT_JAVA_DISTRIBUTED_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_JAVA_DISTRIBUTED_INTERMEDIATE_INSTRUCTIONS,
    ],
}
