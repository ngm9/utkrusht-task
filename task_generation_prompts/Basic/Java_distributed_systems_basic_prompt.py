PROMPT_JAVA_DISTRIBUTED_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_DISTRIBUTED_INPUT_AND_ASK_BASIC = """
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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Java Distributed Systems proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_DISTRIBUTED_BASIC = """
## GOAL
As a senior Java architect super experienced in Java distributed systems (Spring Boot, Spring Kafka, Spring AMQP, Redis, Resilience4j, Docker), you are given a list of real world scenarios and proficiency levels for Java distributed systems development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Java distributed systems experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental Java distributed systems concepts like:
  - Basic message broker concepts with Kafka/RabbitMQ (producing and consuming messages)
  - Spring Kafka basics (@KafkaListener, KafkaTemplate, basic producer/consumer setup)
  - Spring AMQP basics (RabbitTemplate, @RabbitListener, queue/exchange/binding)
  - Basic Redis integration (RedisTemplate, basic caching with @Cacheable)
  - REST-based inter-service communication (RestTemplate, WebClient basics)
  - Basic circuit breaker concept (Resilience4j @CircuitBreaker annotation)
  - Understanding eventual consistency at a conceptual level
  - Basic retry mechanisms (@Retryable, simple retry with Spring)
  - Docker Compose for local development with Kafka/Redis/RabbitMQ
  - Basic health checks and service monitoring (Spring Boot Actuator)
  - Understanding idempotency at a conceptual level
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Java best practices (Java 11+) and current Spring framework standards (Spring Boot 2.7+ or 3.x).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Java distributed systems proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Java distributed systems task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years Java distributed systems experience), keeping in mind that AI assistance is allowed.
- Tests practical Java distributed systems skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on 1-2 service interaction with a single message broker or cache, not complex microservice ecosystems or advanced architectural patterns

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `mvn spring-boot:run` or `gradle bootRun` (the application itself will start; distributed infra like Kafka/Redis/RabbitMQ runs via docker-compose).
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Java starter code should include basic project structure with Spring Boot and the required distributed systems dependencies already configured in pom.xml
- docker-compose.yml MUST be included to spin up any required infrastructure (Kafka, Redis, RabbitMQ, Zookeeper, etc.)
- Focus on a single Spring Boot application communicating with one or two infrastructure components (e.g., one Kafka broker, one Redis instance)

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Kafka Consumer for Real-Time Order Notifications', 'Fix Redis Cache Invalidation in Product Catalog Service', 'Build Message-Driven Payment Processing Pipeline'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Java, Maven/Gradle, and IDE exclusions",
    "pom.xml": "Maven dependencies and build configuration including Spring Kafka / Spring AMQP / Spring Data Redis / Resilience4j as needed",
    "src/main/resources/application.properties": "Spring Boot configuration with broker/Redis connection properties",
    "docker-compose.yml": "Docker Compose file for Kafka/Zookeeper, Redis, RabbitMQ, or other required infrastructure",
    "src/main/java/com/example/Application.java": "Spring Boot main application class",
    "src/main/java/com/example/config/KafkaConfig.java": "Configuration class for message broker or cache (as needed)",
    "src/main/java/com/example/producer/MessageProducer.java": "Producer or publisher starter code (as needed)",
    "src/main/java/com/example/consumer/MessageConsumer.java": "Consumer or listener starter code (as needed)",
    "src/main/java/com/example/service/ExampleService.java": "Service or other starter code",
    "additional_file.java": "Other Java source files as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Java 11+, Maven 3.6+/Gradle 7+, Docker and Docker Compose, IDE, Git, and Spring Boot fundamentals along with basic understanding of message brokers (Kafka/RabbitMQ) and/or Redis.",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on message serialization, consumer group configuration, and ensuring idempotent message processing'",
  "definitions": {{
    "Message Broker": "Middleware that translates messages between sender and receiver, enabling asynchronous communication between services",
    "Eventual Consistency": "A consistency model where the system guarantees that all replicas will eventually return the same value, given no new updates",
    "Idempotency": "The property where performing an operation multiple times produces the same result as performing it once",
    "Circuit Breaker": "A design pattern that prevents cascading failures by stopping requests to a failing service after a threshold is reached",
    "Dead Letter Queue": "A queue where messages that cannot be processed successfully are sent for later inspection or reprocessing"
  }}
}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Java best practices and Spring framework conventions
- Use proper package structure (com.example.taskname.config, producer, consumer, service, model, controller, etc.)
- Use appropriate Spring annotations (@SpringBootApplication, @Configuration, @Service, @KafkaListener, @RabbitListener, @Cacheable, @CircuitBreaker, etc.)
- Follow Java naming conventions and coding standards
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core business logic methods, message handlers, service implementations, or integration logic that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement business logic" etc.
- DO NOT add comments that give away hints or solution or implementation details
- docker-compose.yml must define the required infrastructure services (Kafka + Zookeeper, Redis, RabbitMQ, etc.) with correct ports and health checks

- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Java projects including target/build directories, IDE configurations (.idea, .eclipse, .vscode), compiled class files, JAR files, log files, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE (Java Distributed Systems)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution. Include context about the distributed nature of the problem (e.g., why messaging or caching is needed).

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery rather than prescribing specific implementations
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep it to 3-4 essential bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level Java Distributed Systems task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around outcomes, not specific annotations or methods
  - Content should be open-ended, guiding the candidate toward discovery rather than prescribing specific implementations
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 essential bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Observable behaviors or outputs to validate (messages produced/consumed, cache hits, API responses, circuit breaker behavior)
  - Describe what behaviors to verify, not specific code or annotations to check
  - Leave the solution approach entirely to the candidate
  - **CRITICAL**: Keep to 3-5 essential bullets only. Describe what to verify, not how to implement it.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (mvn spring-boot:run, docker-compose up, etc.)
- Specific Spring annotations or class names that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"
- Excessive bullets or overly detailed guidance that removes the need for the candidate to think

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "order-notification-kafka-consumer")
3. **docker-compose.yml** must be included if Kafka, Redis, or RabbitMQ is needed for the task
4. **code_files** must include README.md, .gitignore, pom.xml, application.properties, docker-compose.yml, and Java source files
5. **README.md** must follow the structure above with Task Overview (3-4 sentences), Helpful Tips, Objectives, How to Verify
6. **Starter code** must be runnable (mvn spring-boot:run) but must NOT contain the solution
7. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
8. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
9. **hints** must be a single line; **definitions** must include relevant distributed systems terms (message broker, eventual consistency, idempotency, circuit breaker, dead letter queue)
10. **Task must be completable within {minutes_range} minutes** for BASIC proficiency (1-2 years)
11. **NO comments in code** that reveal the solution or give hints
12. **Use Java 11+ and Spring Boot 2.7+ or 3.x** conventions throughout
13. **Focus on 1-2 service interaction**, not complex microservice ecosystems
14. **`title`** must be in `<action verb> <subject>` format and different from `name` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "Java (BASIC), Java - Distributed Systems (BASIC)": [
        PROMPT_JAVA_DISTRIBUTED_CONTEXT_BASIC,
        PROMPT_JAVA_DISTRIBUTED_INPUT_AND_ASK_BASIC,
        PROMPT_JAVA_DISTRIBUTED_BASIC,
    ],
}
