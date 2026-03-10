PROMPT_JAVA_SPRING_BOOT_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_INTERMEDIATE = """
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
2. What will the task look like? (Describe the type of Java Spring Boot implementation or fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_SPRING_BOOT_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java, Spring Boot, and modern Spring ecosystem, you are given a list of real world scenarios and proficiency levels for Spring Boot development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase, implement a new feature or improve existing functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Spring Boot experience) 
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Spring Boot Architecture**: RESTful API design, layered architecture (Controller-Service-Repository), Spring MVC patterns, request/response handling
  - **Dependency Injection & IoC**: Bean lifecycle, qualifier usage, component scanning, configuration management, profiles
  - **Data Access**: Spring Data JPA, repository patterns, entity relationships, query methods, transaction management, database migrations
  - **Spring Boot Configuration**: application.properties/yml, externalized configuration, @ConfigurationProperties, profile-specific configs
  - **Exception Handling**: @ControllerAdvice, global exception handlers, custom exceptions, proper HTTP status codes
  - **Validation & Security**: Bean validation (@Valid, @NotNull, etc.), input sanitization, Spring Security basics, authentication/authorization patterns
  - **Testing**: Spring Boot Test, @WebMvcTest, @DataJpaTest, MockMvc, integration testing, test slices
  - **Advanced Spring Features**: AOP basics, events and listeners, async processing, scheduling, caching strategies
  - **API Design**: DTO patterns, mapping strategies (MapStruct/ModelMapper), pagination, filtering, versioning
  - **Microservices Patterns**: Service communication, RestTemplate/WebClient, configuration management, health checks
  - **Performance & Optimization**: Connection pooling, lazy loading, N+1 query problems, caching (@Cacheable), async operations
  - **Monitoring & Actuator**: Spring Boot Actuator endpoints, health indicators, metrics, logging strategies
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern Spring Boot best practices (Spring Boot 2.x/3.x) and current development standards. Use modern Spring features appropriately.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate Spring Boot proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Spring Boot task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years Spring Boot experience), keeping in mind that AI assistance is allowed.
- Tests practical Spring Boot skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-layered Spring Boot applications that require thoughtful architecture and design patterns
- Should test the candidate's ability to structure a scalable Spring Boot application with proper separation of concerns

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate Spring Boot architectural skills
- The code files generated must be valid and executable with `mvn spring-boot:run` or `gradle bootRun`.
- Provide a realistic Spring Boot project structure that mimics real-world applications
- A part of the task completion is to watch the candidate implement Spring Boot best practices, design the solution correctly, demonstrate proper package structure, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper layered architecture and Spring Boot patterns
- Spring Boot starter code should include realistic project structure with proper Spring configuration
- Include some existing controllers/services/repositories/entities that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architecture using Spring Boot conventions

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pom.xml (Maven dependencies with Spring Boot starters) OR build.gradle (Gradle dependencies with Spring Boot plugin)
  - .gitignore (Standard Spring Boot project gitignore)
  - application.properties or application.yml (Spring Boot configuration)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial Spring Boot architecture that candidate needs to complete/extend
  - Include realistic folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name in <verb><subject> format within 50 charactersand task related, e.g. 'Harden Payment Gateway Integration' ",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Spring Boot, Java and Maven/Gradle exclusions",
      "pom.xml": "Maven dependencies with Spring Boot starters and plugins for intermediate-level applications",
      "src/main/resources/application.properties": "Spring Boot configuration properties (or application.yml)",
      "src/main/java/com/company/Application.java": "Spring Boot main application class with @SpringBootApplication",
      "src/main/java/com/company/controller/ControllerClass.java": "REST controllers with @RestController/@Controller",
      "src/main/java/com/company/service/ServiceClass.java": "Service layer classes with @Service",
      "src/main/java/com/company/repository/RepositoryClass.java": "Repository interfaces extending JpaRepository/CrudRepository",
      "src/main/java/com/company/model/Entity.java": "JPA entity classes with @Entity",
      "src/main/java/com/company/dto/DtoClass.java": "DTO classes for API requests/responses",
      "src/main/java/com/company/config/ConfigClass.java": "Configuration classes with @Configuration (if needed)",
      "src/main/java/com/company/exception/CustomException.java": "Custom exception classes and @ControllerAdvice handlers",
      "src/main/resources/db/migration/V1__init.sql": "Database migration scripts (if using Flyway/Liquibase)",
      "src/test/java/com/company/ControllerTest.java": "Test class templates using @WebMvcTest (if needed)",
      "src/test/java/com/company/ServiceTest.java": "Service test templates using @SpringBootTest (if needed)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like Spring Boot knowledge, REST API design, JPA/Hibernate understanding, testing familiarity, database basics, etc.",
  "answer": "High-level solution approach for solving task",
  "hints": "a single line hint focusing on Spring Boot architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good Spring Boot architectural thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

 
## Code file requirements:
- Generate realistic Spring Boot folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)
- Code should follow modern Spring Boot best practices and demonstrate intermediate-level patterns
- Use appropriate Spring annotations and dependency injection patterns
- Focus on modern Spring Boot features (Spring Boot 2.x/3.x) and development best practices
- **CRITICAL**: The generated code files should provide partial implementations that require Spring Boot architectural completion
- Include some existing controllers/services/repositories that need to be extended or integrated
- The core architectural decisions, layered design, REST API implementation, data access patterns, or architecture solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add @Transactional here" or "Should implement caching" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be compilable and bootable, but will require architectural completion to function properly
- Provide realistic Spring Boot dependencies in pom.xml/build.gradle that intermediate developers should be familiar with (spring-boot-starter-web, spring-boot-starter-data-jpa, etc.)

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Spring Boot projects including target directories, build directories, IDE configurations (.idea/, .vscode/, .eclipse/, *.iml), compiled class files (*.class), JAR files, log files, Spring Boot specific files (*.log, application-local.properties), H2 database files (*.db), and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify 
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Spring Boot task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why Spring Boot architectural considerations matter for this use case. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper Spring Boot architecture is crucial.


### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate Spring Boot level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What REST API functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and Spring Boot code quality metrics
  - Include expectations for layered architecture, REST API design, data persistence, and testing
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Implement REST endpoints that handle requests and return appropriate responses with correct HTTP status codes"
    * "Design a solution that persists data reliably and retrieves it efficiently"
    * "Create a system that validates incoming data and provides meaningful error messages"
    * "Organize code into layers that separate web handling, business logic, and data access"
    * "Ensure the application can be configured for different environments without code changes"
    * "Handle concurrent requests safely without data inconsistencies"
  - Objectives should be measurable but not prescribe specific Spring annotations or approaches
  - Should guide candidates to think about: REST API design, data modeling, transaction management, error handling, testing, configuration
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both REST API functionality and Spring Boot architecture
  - API testing checkpoints (endpoints work correctly, proper status codes, validation works)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and architectural assessment criteria
  - Data persistence verification and edge case validation points
  - Frame verification in terms of observable outcomes and API behaviors
  - Examples of proper framing:
    * "Test the API endpoints with various input scenarios including valid, invalid, and edge case data"
    * "Verify that data persists correctly and can be retrieved accurately"
    * "Confirm error responses include meaningful messages and appropriate HTTP status codes"
    * "Check that validation prevents invalid data from being processed"
    * "Validate that the application starts successfully and all beans are properly initialized"
    * "Ensure concurrent API requests don't cause data corruption or inconsistencies"
    * "Test the application behavior with different configuration settings"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: API endpoints, data operations, validation, error handling, configuration, concurrency
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific Spring Boot implementation to check
  
### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring Spring Boot layered architecture patterns that promote separation of concerns
  - Mention thinking about how controllers, services, and repositories should interact
  - Hint at considering dependency injection and how Spring manages bean lifecycles
  - Recommend exploring how to handle errors gracefully using Spring's exception handling mechanisms
  - Suggest thinking about data validation and how Spring Boot validates incoming requests
  - Point toward considering how to structure RESTful APIs following best practices
  - Hint at exploring Spring Data JPA features that simplify database operations
  - Recommend considering transaction boundaries and data consistency
  - Suggest analyzing how to configure and externalize application settings
  - Mention thinking about how to make the application testable using Spring Boot testing tools
  - Recommend exploring how to handle cross-cutting concerns efficiently
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward Spring Boot architectural thinking, not provide direct solutions or specific annotations
  - Frame suggestions around principles and outcomes rather than specific implementations
  - Examples of proper framing:
    * "Consider how to organize your application into logical layers that separate web, business, and data concerns"
    * "Think about how to handle different types of errors appropriately at each layer of your application"
    * "Explore approaches for validating data before it reaches your business logic"
    * "Review how to efficiently retrieve and persist data while maintaining performance"
    * "Consider how to make your configuration flexible for different environments"

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (mvn spring-boot:run, gradle bootRun, mvn clean install, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific Spring annotations or implementation approaches (e.g., "use @Transactional", "add @Cacheable")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific class implementation details that would give away the solution to the task
  - Should not provide any particular architectural approach or Spring Boot pattern to implement the solution
  - Controller/Service/Repository method signatures that would reveal the solution
  - Specific Spring Boot configuration properties that would dictate the implementation
  - Package structure decisions that would dictate the architectural approach
  - Phrases like "you should implement", "make sure to add @Service", "create a controller with @PostMapping"
  - Specific Spring Data JPA query method names or repository patterns that would reveal the solution
  - Spring Security configuration details or specific authentication approaches
"""
PROMPT_REGISTRY = {
    "Java - Spring Boot (INTERMEDIATE)": [
        PROMPT_JAVA_SPRING_BOOT_CONTEXT_INTERMEDIATE,
        PROMPT_JAVA_SPRING_BOOT_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_JAVA_SPRING_BOOT_INTERMEDIATE_INSTRUCTIONS,
    ]
}
