PROMPT_JAVA_SPRING_MVC_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_SPRING_MVC_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java Spring MVC assessment task.

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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Java Spring MVC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_SPRING_MVC_BASIC = """
## GOAL
As a senior Java architect super experienced in Java frameworks (Spring MVC, Spring Boot, Hibernate/JPA, Maven/Gradle), you are given a list of real world scenarios and proficiency levels for Java development.
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
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental Java Spring MVC concepts like:
  - Spring MVC application structure and annotations (@Controller, @RequestMapping, @GetMapping, @PostMapping)
  - Request handling with @RequestParam, @PathVariable, @ModelAttribute
  - Form handling, data binding, and server-side validation with @Valid and BindingResult
  - View resolution with Thymeleaf or JSP (returning view names from controllers)
  - Service layer patterns and business logic separation
  - Basic data persistence with JPA/Hibernate
  - Exception handling with @ExceptionHandler and @ControllerAdvice
  - Redirect and forward patterns (Post-Redirect-Get)
  - Configuration management (application.properties/yml)
  - Basic testing with JUnit, MockMvc, and Spring Test
  - Maven/Gradle dependency management
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Java best practices (Java 11+) and current Spring framework standards (Spring Boot 2.7+ or 3.x with Spring MVC).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Java Spring MVC proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Java Spring MVC task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years Java framework experience), keeping in mind that AI assistance is allowed.
- Tests practical Java Spring MVC skills that require more than a simple AI query to solve, focusing on fundamental MVC concepts
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single Spring MVC application with controllers, services, and views rather than complex distributed systems or microservices
- Emphasize the MVC pattern: proper separation of controller logic, service layer, and view rendering

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `mvn spring-boot:run` or `gradle bootRun`.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Java starter code should include basic project structure but NOT require complex infrastructure setup (advanced database configurations, complex security setup, microservice orchestration, etc.)
- Focus on Spring Boot with embedded database (H2) or simple file-based persistence for simplicity
- Include at least one controller, one service, and appropriate model/entity classes in the starter code

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Form Validation for Payment Processing Module', 'Fix Order Detail View and Exception Handling in E-Commerce App', 'Build Product Search Controller with Pagination Support'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Java, Maven/Gradle, and IDE exclusions",
    "pom.xml": "Maven dependencies and build configuration (or build.gradle for Gradle projects)",
    "src/main/resources/application.properties": "Spring Boot configuration with Spring MVC settings",
    "src/main/java/com/example/Application.java": "Spring Boot main application class",
    "src/main/java/com/example/controller/ExampleController.java": "Spring MVC controller with request mappings",
    "src/main/java/com/example/service/ExampleService.java": "Service layer with business logic",
    "src/main/java/com/example/model/ExampleModel.java": "Model or entity class",
    "additional_file.java": "Other Java source files as needed (repository, DTO, exception classes)"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Java 11+, Maven 3.6+/Gradle 7+, IDE, Git, and Spring MVC fundamentals (controllers, request mappings, view resolution, form handling, validation, JPA/Hibernate basics).",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on controller request handling, proper validation with BindingResult, and service layer responsibility separation'",
  "definitions": {{
    "Spring MVC": "Web framework providing Model-View-Controller architecture for building web applications",
    "Controller": "Spring component that handles HTTP requests and returns views or response bodies",
    "ModelAttribute": "Annotation for binding request parameters to Java objects in form handling",
    "BindingResult": "Interface for validation results when using @Valid on form objects",
    "ControllerAdvice": "Global exception handler component for centralized error handling",
    "View Resolver": "Component that maps view names returned by controllers to actual view templates"
  }}
}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Java best practices and Spring MVC conventions
- Use proper package structure (com.example.taskname.controller, service, repository, model, etc.)
- Use appropriate Spring MVC annotations (@Controller, @RestController, @RequestMapping, @GetMapping, @PostMapping, @ModelAttribute, @Valid, etc.)
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

## README.md STRUCTURE (Java / Spring MVC)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery — suggest areas to explore, not specific solutions
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level Java Spring MVC task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around observable outcomes and expected behavior
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Describe what behaviors to verify and how to confirm success
  - Focus on observable outcomes (API responses, view rendering, form submissions, error handling)
  - Do NOT specify specific code, annotations, or implementation details to check
  - **CRITICAL**: Describe what behaviors to verify, not specific code or annotations to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (mvn spring-boot:run, etc.)
- Specific Spring annotations or class names that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "order-validation-mvc-fix")
3. **code_files** must include README.md, .gitignore, build file, application.properties/yml, and Java source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable (mvn spring-boot:run or gradle bootRun) but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant Java/Spring MVC terms
9. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use Java 11+ and Spring Boot 2.7+ or 3.x** conventions throughout
12. **Emphasize MVC pattern** — proper controller-service-view separation is key
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "Java - Spring MVC": [
        PROMPT_JAVA_SPRING_MVC_CONTEXT_BASIC,
        PROMPT_JAVA_SPRING_MVC_INPUT_AND_ASK_BASIC,
        PROMPT_JAVA_SPRING_MVC_BASIC,
    ],
    "Java - Spring MVC (BASIC)": [
        PROMPT_JAVA_SPRING_MVC_CONTEXT_BASIC,
        PROMPT_JAVA_SPRING_MVC_INPUT_AND_ASK_BASIC,
        PROMPT_JAVA_SPRING_MVC_BASIC,
    ],
}
