PROMPT_JAVA_HIBERNATE_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_HIBERNATE_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java and Hibernate assessment task.

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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Java and Hibernate proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_HIBERNATE_BASIC_INSTRUCTIONS = """
## GOAL
As a senior Java engineer experienced in core Java and Hibernate ORM, you are given a list of real world scenarios and proficiency levels for Java development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes and starter code that can be used to assess a candidate's ability to solve a practical Java + Hibernate problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a small feature from scratch or fix logical bugs in an existing codebase.
- The task must stay within BASIC Java and BASIC Hibernate expectations only.
- The scenario must be realistic, concrete, and easy to understand for a 1-2 year Java engineer.
- The task should focus on a small persistence layer or domain module, not a full system.
- The task should test 2-3 combined concepts, not broad architecture.
- The task must be completable within {minutes_range} minutes.
- The task must NOT require system design, microservices, advanced concurrency, advanced caching, complex partitioning, deep performance tuning, many-to-many optimization, composite keys, custom UserTypes, interceptors, event listeners, multi-tenant setups, Flyway/Liquibase migrations, or advanced second-level cache work.
- The task must NOT depend on Docker, external databases, or web frameworks.
- The task should use plain Java with Maven or Gradle and a stand-alone Hibernate setup.
- The task should be inspired by ONE provided scenario and should fit the company and role context from {organization_background} and {role_context}.

### Skills to Assess
The generated task should primarily assess BASIC-level skills that are explicitly in scope:

#### Java BASIC
- Clean Java class design with proper packages and naming conventions
- Foundational Java syntax and control flow
- OOP basics: encapsulation, abstraction, inheritance or polymorphism where naturally useful
- Collections such as List, Set, or Map where appropriate
- Basic exception handling with try-catch-finally
- Maintainable code structure and small refactors for readability or correctness
- Straightforward JUnit tests
- Basic performance awareness such as avoiding obviously poor collection choices or unnecessary blocking/resource misuse

#### Hibernate BASIC
- Maven or Gradle configuration for Hibernate in stand-alone mode
- Externalized configuration through properties files
- JDBC driver and dialect wiring
- Simple entity mapping with identifiers and basic attributes
- Enums, embeddables, or Bean Validation only if naturally useful and still simple
- One-to-one, many-to-one, or one-to-many mappings with correct ownership and join columns
- Basic cascades and fetch choices where relevant
- Persistence context basics such as persist, update/merge, flush, and dirty checking at a simple level
- CRUD operations using Session API or EntityManager
- Straightforward HQL/JPQL or basic Criteria queries with secure parameter binding
- Programmatic transaction handling
- Catching and translating common Hibernate exceptions
- Integration tests using H2 or HSQLDB

### Complexity Calibration
- BASIC level means the task should be specific and well-scoped.
- Prefer one small domain such as orders, candidate notes, inventory reservations, support tickets, or course enrollments.
- Good task shapes include:
  - Fix an entity mapping so related records persist correctly
  - Add validation and encapsulation to a domain model
  - Replace unsafe query construction with parameter binding
  - Improve transaction handling and exception translation in a repository/service flow
  - Add a small query or update feature with tests against H2
- If concurrency or background work appears, it must remain minor and secondary to the Java + Hibernate task. Do not make async/concurrency the primary skill.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use external resources including documentation, search engines, forums, and AI tools.
- The task should therefore require practical reasoning and code adaptation, not memorization.
- Even with AI assistance, the task should still require the candidate to understand entity relationships, transactions, validation, and clean Java structure.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Java + Hibernate task that:
- Draws inspiration from the input scenarios to determine the business context and technical requirements
- Matches BASIC proficiency level for Java and Hibernate
- Focuses on a stand-alone persistence module rather than a web application
- Uses a PURE_CODE structure only
- Can be completed in {minutes_range} minutes
- Uses a small number of files with a clear starter structure
- Leaves the core logic incomplete enough that the candidate must implement or fix it

## Starter Code Instructions
- The starter code should provide a runnable Maven or Gradle Java project.
- The project must NOT require Docker.
- The project must include source code plus a build file and any needed resource files.
- The project should compile or be very close to compilable with only the intended task logic missing or incorrect.
- The starter code must NOT contain the full solution.
- If the task is a bug-fix task, the bugs must be logical and realistic, not syntax errors.
- If the task is a feature task, provide enough structure so the candidate can start quickly.
- Use Java 11+ conventions.
- Prefer a stand-alone main class or service-oriented console application structure.
- Include Hibernate configuration and H2-based tests where appropriate.
- Do NOT include any comments that reveal the solution.
- Do NOT include TODO comments or step-by-step implementation hints in code.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Order Persistence Flow for Inventory Checkout', 'Implement Candidate Note Persistence for Hiring Portal', 'Repair Course Enrollment Mapping in Training Platform'. The title must clearly describe the action and subject.",
  "question": "Short description of the business scenario and the specific Java + Hibernate problem the candidate must solve.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Java, Maven/Gradle, IDE, and local database exclusions",
    "pom.xml": "Maven build file with Hibernate, H2, JUnit, and logging dependencies",
    "src/main/resources/hibernate.properties": "Hibernate configuration with H2 settings and schema generation mode",
    "src/main/java/com/example/task/Main.java": "Entry point or small runner class",
    "src/main/java/com/example/task/config/HibernateUtil.java": "Hibernate SessionFactory bootstrap",
    "src/main/java/com/example/task/model/ExampleEntity.java": "Entity classes and related domain objects",
    "src/main/java/com/example/task/repository/ExampleRepository.java": "Repository using Session API or EntityManager",
    "src/main/java/com/example/task/service/ExampleService.java": "Service layer with transaction and exception handling",
    "src/main/java/com/example/task/exception/DomainException.java": "Custom exception classes if needed",
    "src/test/java/com/example/task/ExampleServiceTest.java": "JUnit tests using H2",
    "additional_files_as_needed": "Any other minimal Java files required by the task"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing the business problem, the persistence-layer issue or feature, and the expected outcome emphasizing correctness, maintainability, and safe data handling.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Java 11+, Maven or Gradle, IDE, Git, core Java fundamentals, Hibernate basics, H2, and JUnit.",
  "answer": "High-level solution approach describing the main domain model, mapping corrections or additions, transaction flow, validation, query approach, and tests.",
  "hints": "Single line suggesting a focus area without giving away the solution.",
  "definitions": {{
    "Entity": "A Java class mapped to a database table by Hibernate",
    "Session": "Hibernate interface used to manage persistence operations and queries",
    "Transaction": "A unit of work that groups database operations so they succeed or fail together",
    "Cascade": "A mapping rule that propagates persistence operations from one entity to related entities",
    "Parameter Binding": "Supplying query values safely through parameters instead of string concatenation",
    "Dirty Checking": "Hibernate feature that detects changes to managed entities and persists them during flush"
  }}
}}

## Code File Requirements
- The task category is PURE_CODE, so generate only source files, resource files, tests, and a build file.
- Do NOT generate Dockerfile, docker-compose.yml, run.sh, kill.sh, or any infrastructure scripts.
- Use a normal Java package structure.
- Code should follow modern Java best practices and Hibernate conventions.
- Use proper naming and organization for model, repository, service, config, and exception packages.
- The generated code files MUST NOT contain the completed core solution.
- The candidate should need to implement or fix the important mapping, validation, query, transaction, or exception-handling logic.
- The project should remain small and focused.
- Tests should be straightforward and aligned with BASIC proficiency.
- If tests are included, they should validate observable behavior without embedding the full solution in the test names or setup.

## .gitignore Instructions
Create a comprehensive .gitignore suitable for a Java Hibernate project, including:
- target/, build/, out/
- .idea/, .vscode/, *.iml, .classpath, .project, .settings/
- *.class, *.jar, *.war, *.log
- H2 database files such as *.mv.db and *.trace.db
- OS-specific files such as .DS_Store and Thumbs.db

## README.md Structure

### Task Overview
- 2-3 substantial sentences
- Describe the business scenario and current persistence problem
- Explain why the issue matters
- Do NOT directly tell the candidate the exact implementation steps

### Helpful Tips
- 3-4 bullets maximum
- Use bullets starting with "Consider", "Think about", "Explore", "Review", or "Look into"
- Guide discovery without naming the exact solution
- Focus on entity relationships, validation, transaction boundaries, query safety, and error handling

### Objectives
- 3-5 bullets maximum
- Describe what should work after completion
- Focus on observable outcomes such as correct persistence, rejected invalid input, safe query behavior, and maintainable code
- Do NOT prescribe exact annotations, methods, or class names

### How to Verify
- 3-5 bullets maximum
- Describe how to confirm the task is solved
- Focus on persisted records, related data behavior, invalid input handling, and test execution outcomes
- Do NOT reveal the exact implementation

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands
- Specific annotation combinations that reveal the answer
- Direct method signatures or class names that solve the task
- Excessive detail that removes the need for candidate reasoning

## CRITICAL REMINDERS
1. Output must be valid JSON only when generating the task definition
2. The generated task must stay within BASIC Java and BASIC Hibernate scope
3. The task must be a PURE_CODE project only
4. The task must not require Spring Boot, REST APIs, Docker, or external infrastructure
5. The task must use stand-alone Hibernate with a simple local database setup such as H2
6. The task must be completable within {minutes_range} minutes
7. The README must be concise and open-ended
8. The code must not contain comments that reveal the solution
9. The task should feel like a realistic small feature or bug fix from a team codebase
10. Prefer scenarios involving entity encapsulation, validation, one-to-many or many-to-one mapping, parameterized HQL/JPQL, transaction handling, and exception translation
11. Include placeholders exactly as provided in this prompt set, including {organization_background}, {role_context}, {competencies}, {real_world_task_scenarios}, and {minutes_range}
"""

PROMPT_REGISTRY = {
    "Java (BASIC), Java - Hibernate (BASIC)": [
        PROMPT_JAVA_HIBERNATE_BASIC_CONTEXT,
        PROMPT_JAVA_HIBERNATE_BASIC_INPUT_AND_ASK,
        PROMPT_JAVA_HIBERNATE_BASIC_INSTRUCTIONS,
    ]
}