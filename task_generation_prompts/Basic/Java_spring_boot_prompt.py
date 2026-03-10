PROMPT_JAVA_SPRING_BOOT_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java Spring Boot assessment task.

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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Java Spring Boot proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_SPRING_BOOT_BASIC = """
## GOAL
As a senior Java architect super experienced in Java frameworks (Spring Boot, Spring MVC, Hibernate/JPA, Maven/Gradle), you are given a list of real world scenarios and proficiency levels for Java development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Java framework experience), ensuring that no two questions generated are similar. 
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental Java framework concepts like:
  - Spring Boot application structure and annotations
  - REST API development with Spring MVC
  - Dependency injection and component management
  - Basic data persistence with JPA/Hibernate
  - Service layer patterns and business logic
  - Basic exception handling
  - Configuration management (application.properties/yml)
  - Basic testing with JUnit and Spring Boot Test
  - Maven/Gradle dependency management
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern Java best practices (Java 11+) and current Spring framework standards (Spring Boot 2.7+ or 3.x).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Java framework proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Java framework task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years Java framework experience), keeping in mind that AI assistance is allowed.
- Tests practical Java framework skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single microservice or standalone Spring Boot applications rather than complex distributed systems or advanced architectural patterns

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `mvn spring-boot:run` or `gradle bootRun`.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Java starter code should include basic project structure but NOT require complex infrastructure setup (advanced database configurations, complex security setup, microservice orchestration, etc.)
- Focus on Spring Boot with embedded database (H2) or simple file-based persistence for simplicity

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Java, Maven/Gradle, and IDE exclusions",
    "pom.xml": "Maven dependencies and build configuration (or build.gradle for Gradle projects)",
    "src/main/resources/application.properties": "Spring Boot configuration",
    "src/main/java/com/example/Application.java": "Spring Boot main application class",
    "src/main/java/com/example/controller/ExampleController.java": "Controller or other starter code",
    "src/main/java/com/example/service/ExampleService.java": "Service or other starter code",
    "additional_file.java": "Other Java source files as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Java 11+, Maven 3.6+/Gradle 7+, IDE, Git, and Spring Boot fundamentals (annotations, dependency injection, REST, JPA/Hibernate basics).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on service layer responsibility, REST response structure, and validation of inputs before processing'",
  "definitions": {{
    "Dependency Injection": "Spring mechanism for supplying dependencies to beans",
    "RestController": "Spring component for REST API endpoints",
    "JPA/Entity": "Java Persistence API and entity mapping",
    "Service layer": "Layer containing business logic",
    "Repository": "Data access abstraction in Spring"
  }}
}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Java best practices and Spring framework conventions
- Use proper package structure (com.example.taskname.controller, service, repository, model, etc.)
- Use appropriate Spring annotations (@RestController, @Service, @Repository, @Entity, etc.)
- Follow Java naming conventions and coding standards
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core business logic methods, service implementations, repository queries, or controller endpoints that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement business logic" etc.
- DO NOT add comments that give away hints or solution or implementation details

- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Java projects including target/build directories, IDE configurations (.idea, .eclipse, .vscode), compiled class files, JAR files, log files, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE (Java / Spring Boot)

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips

Practical guidance without revealing implementations:
  - Suggest exploring how Spring Boot organizes different types of components and their responsibilities
  - Mention thinking about which layer should handle specific types of operations (data access, business logic, request handling)
  - Hint at considering how Spring manages object creation and wiring between components
  - Recommend exploring how to map HTTP requests to Java methods that handle them
  - Suggest thinking about how data flows between the client, application layers, and data storage
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions

### Objectives

Define goals focusing on outcomes for a BASIC-level Java Spring Boot task:
  - Clear, measurable goals the candidate should achieve to complete the task
  - Functionality to implement, expected API behavior, data models
  - Focus on fundamental Java framework concepts (REST, services, persistence, error handling)
  - Frame objectives around outcomes, not specific annotations or methods
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify

Verification approaches for the task:
  - Observable behaviors or outputs to validate (API responses, persistence, error handling)
  - Functional testing and basic code quality checks
  - What to test and how to confirm success
  - **CRITICAL**: Describe what behaviors to verify, not specific code or annotations to check

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (mvn spring-boot:run, etc.)
- Specific Spring annotations or class names that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "payment-order-validation-fix")
3. **code_files** must include README.md, .gitignore, build file, application.properties/yml, and Java source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable (mvn spring-boot:run or gradle bootRun) but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant Java/Spring terms
9. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use Java 11+ and Spring Boot 2.7+ or 3.x** conventions throughout
"""
PROMPT_REGISTRY = {
    "Java, Java - Spring Boot": [
        PROMPT_JAVA_SPRING_BOOT_CONTEXT_BASIC,
        PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_BASIC,
        PROMPT_JAVA_SPRING_BOOT_BASIC,
    ],
    "Java (BASIC), Java - Spring Boot (BASIC)": [
        PROMPT_JAVA_SPRING_BOOT_CONTEXT_BASIC,
        PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_BASIC,
        PROMPT_JAVA_SPRING_BOOT_BASIC,
    ],
}
