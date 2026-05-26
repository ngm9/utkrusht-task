PROMPT_JAVA_SPRING_BOOT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competencies:
{competencies}

Based on this information, briefly summarize your understanding of the company, the role expectations, and the kind of Spring Boot work this candidate should be able to perform at a BASIC level.
"""

PROMPT_JAVA_SPRING_BOOT_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, here are the inputs for generating a Java Spring Boot assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above.
- The task must feel like a realistic business feature or bug fix for a Spring Boot application used by the organization described above.
- The task must align with BASIC proficiency: a well-scoped feature or bug fix combining 2-3 Spring Boot concepts, suitable for completion in {minutes_range} minutes.
- Prefer practical Spring Boot work such as REST endpoints, DTO validation, service/repository layering, simple persistence with H2, pagination/sorting, configuration, global exception handling, or focused unit/web/data tests.
- The task must remain implementation-focused and not drift into system design, microservices, advanced concurrency, or security hardening.
- Select a different scenario when possible to keep generated tasks varied.
- The task should reflect authentic day-to-day work for a 1-2 year Java engineer working with guidance from senior developers.

Before generating the full task, confirm your understanding by answering briefly:

1. What business problem will the candidate solve?
2. What kind of Spring Boot implementation or fix will the candidate perform?
3. Why is this appropriate for BASIC Java Spring Boot proficiency?

Keep the summary short and concrete.
"""

PROMPT_JAVA_SPRING_BOOT_BASIC_INSTRUCTIONS = """
## GOAL
You are a senior Java engineer and Spring Boot architect designing a practical assessment for a candidate with BASIC proficiency in Java - Spring Boot.
Your job is to generate a complete assessment task definition as a JSON object. The task should evaluate whether the candidate can work effectively in a small Spring Boot codebase, implement or fix a focused feature, and demonstrate sound fundamentals in REST APIs, validation, layering, persistence, error handling, and testing.

## SCOPE BOUNDARY
The task MUST stay within BASIC Spring Boot scope. It may naturally use:
- Spring Boot project structure and configuration
- Spring MVC REST controllers and request mapping
- DTO binding with `@RequestBody`, `@PathVariable`, `@RequestParam`
- Validation with `@Valid` / JSR-380 annotations
- Global exception handling with `@ControllerAdvice`
- Layered architecture: controller, service, repository, domain
- Spring Data JPA with H2 for a lightweight local datastore
- Simple entity/repository/query usage, pagination, sorting, and straightforward filtering
- Basic tests using JUnit 5, Mockito, `@WebMvcTest`, `@DataJpaTest`, or focused service tests
- Logging and clean code practices
- `application.properties` or `application.yml`

The task MUST NOT require as primary skills:
- Microservices or distributed systems
- Advanced concurrency or reactive programming
- Complex security configuration as the main challenge
- Performance tuning as the main challenge
- Docker, Kubernetes, or production infrastructure as the main challenge
- Complex caching, advanced JVM tuning, or architecture-heavy design work

## TASK SHAPE
Create a small Spring Boot application task where the candidate either:
- implements a missing feature from partially wired starter code, or
- fixes a realistic bug in an otherwise runnable application.

The task should be specific, concrete, and easy to understand. It should not be open-ended. The candidate should be able to complete it in {minutes_range} minutes.

## CALIBRATION
Use the company and role context to choose an appropriate business domain.
Use ONE scenario from the provided real-world scenarios as inspiration.
Use the calibration signal to keep the task at BASIC level:
- a 1-2 year Java engineer
- comfortable with core Java and standard Spring Boot patterns
- able to implement small-to-medium modules under supervision
- may demonstrate simple async or performance awareness only in a limited, supporting way
- do not make async/concurrency the primary challenge unless it is very basic and secondary to the Spring Boot task

## PREFERRED TASK CHARACTERISTICS
A strong BASIC Spring Boot task usually combines 2-3 of these:
- request DTO validation
- repository-backed filtering or lookup
- pagination and sorting
- business-friendly error handling
- mapping between DTOs and entities
- one or two focused tests
- small configuration cleanup
- clear HTTP status codes and JSON responses

Examples of acceptable task themes:
- add validation to a create endpoint and return readable 400 errors
- replace a repository `.get()` failure path with a custom 404 response
- implement a filtered and paginated listing endpoint using repository queries
- fix a controller/service flow so invalid input no longer returns 500
- add a small create/list/update REST feature with proper layering and tests

## AI AND EXTERNAL RESOURCE POLICY
Candidates are allowed to use external resources, including documentation, search engines, and AI tools.
Therefore, the task should not be trivial boilerplate. It should still require the candidate to understand the codebase, make correct Spring Boot decisions, and produce maintainable code.

## STARTER CODE REQUIREMENTS
Generate starter code that is runnable but incomplete or logically incorrect in the area being assessed.
The starter code:
- MUST compile or be very close to compiling with minimal setup
- MUST use Maven
- MUST be executable with `./mvnw test` and `./mvnw spring-boot:run` after the candidate completes the task
- MUST include enough structure so the candidate is not starting from a blank project
- MUST NOT include the full solution to the core task
- MUST NOT include comments that reveal the solution
- MUST NOT include `TODO`, `FIXME`, or instructional comments in code
- SHOULD use H2 when persistence is needed so the task remains self-contained
- SHOULD keep the file count modest and focused

## INFRASTRUCTURE RULES
Because this task uses `runtime=java`, `frameworks=["spring-boot"]`, `datastores=[]`, and `kind="app"`:
- Do NOT include `docker-compose.yml`
- Do NOT include `Dockerfile`
- Do NOT include `run.sh` or `kill.sh`
- Do NOT include external service containers
- Keep the project self-contained with Maven and Spring Boot
- If persistence is needed, use embedded H2

## REQUIRED OUTPUT JSON STRUCTURE
Return valid JSON only, using exactly these top-level keys:

{{
  "name": "short-kebab-case-task-name",
  "question": "candidate-facing task description",
  "code_files": {{
    "README.md": "candidate-facing README",
    ".gitignore": "gitignore contents",
    "pom.xml": "maven build file",
    "mvnw": "maven wrapper script contents",
    "mvnw.cmd": "windows maven wrapper script contents",
    ".mvn/wrapper/maven-wrapper.properties": "wrapper properties",
    "src/main/resources/application.properties": "spring boot configuration",
    "src/main/java/com/example/task/Application.java": "main application class",
    "src/main/java/com/example/task/...": "other source files",
    "src/test/java/com/example/task/...": "test files as needed"
  }},
  "answer": "high-level evaluator-facing solution summary",
  "definitions": {{
    "Term": "Definition"
  }},
  "hints": "short hint text",
  "outcomes": "bullet-point list as a single string",
  "pre_requisites": "bullet-point list as a single string",
  "short_overview": "bullet-point list as a single string"
}}

Do not use any other top-level key names.

## FIELD REQUIREMENTS

### 1) name
- kebab-case
- short and descriptive
- suitable as a repository name

### 2) question
- candidate-facing description of the business scenario and the exact expected outcome
- clearly state what is broken or missing
- clearly state what behaviors should work when the task is complete
- do not reveal the implementation
- keep it specific and bounded

### 3) code_files
Must contain a complete small Maven Spring Boot project.
Include only the files needed for the task.
Recommended files for many tasks:
- README.md
- .gitignore
- pom.xml
- mvnw
- mvnw.cmd
- .mvn/wrapper/maven-wrapper.properties
- src/main/resources/application.properties
- src/main/java/com/example/task/Application.java
- controller, service, repository, entity, dto, exception classes as needed
- src/test/java/... with 1-3 focused tests

Do not include unnecessary infrastructure files.

### 4) answer
Provide a concise evaluator-facing summary of the intended solution:
- what classes or flows should be updated
- what validation, repository, mapping, or exception-handling behavior is expected
- what tests should pass
Do not provide a full code dump here.

### 5) definitions
Include 4-7 relevant Spring Boot terms, for example:
- DTO
- `@Valid`
- `@ControllerAdvice`
- Repository
- Pagination
- Service Layer

### 6) hints
- one short line only
- should gently nudge without giving away the solution

### 7) outcomes
A bullet-point list stored as a single string.
Must include one bullet exactly stating:
- Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.

### 8) pre_requisites
A bullet-point list stored as a single string.
Include:
- Java 17+
- Maven
- basic Spring Boot knowledge
- IDE and Git
- basic REST and testing familiarity

### 9) short_overview
A bullet-point list stored as a single string summarizing:
- the business problem
- the implementation/fix goal
- the expected result

## README REQUIREMENTS
The generated `README.md` must be concise and candidate-facing with these sections in this order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

Rules for README:
- Keep it concise and open-ended
- Do not include step-by-step implementation instructions
- Do not include code snippets that reveal the solution
- Do not include setup commands
- Do not prescribe exact class names or method signatures unless already present in starter code
- Focus on observable behavior and business context

### README section guidance

#### Task Overview
- 3-4 substantial sentences
- explain the business scenario and current issue
- explain why the endpoint or feature matters
- do not directly tell the candidate how to solve it

#### Helpful Tips
- 3-4 bullets maximum
- each bullet should begin with words like: Consider, Review, Explore, Think about, Look into
- guide discovery without revealing implementation details

#### Objectives
- 3-5 bullets maximum
- describe what should work after completion
- focus on outcomes, not implementation steps

#### How to Verify
- 3-5 bullets maximum
- describe observable behaviors to test
- include API behavior, validation/error cases, and any relevant test execution expectations

## CODE QUALITY RULES
- Use modern Java and Spring Boot conventions
- Prefer constructor injection
- Keep package structure clean
- Use layered architecture
- Use meaningful names
- Include basic logging only if it fits naturally
- Keep the codebase small and realistic
- No comments that reveal the solution
- No placeholder comments
- No intentionally broken syntax
- If using JPA, keep schema simple and self-contained

## TESTING GUIDANCE
For BASIC level, include a small amount of testing:
- 1-3 focused tests are enough
- tests may be incomplete or failing until the candidate fixes the task
- acceptable test styles: `@WebMvcTest`, `@DataJpaTest`, or focused service tests with Mockito
- do not turn the task into a testing-only exercise

## FINAL REMINDERS
- Output must be valid JSON only
- Use exactly the canonical top-level keys: `name`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, `short_overview`
- Keep the task within BASIC Spring Boot scope
- Make the task realistic, bounded, and completable within {minutes_range} minutes
- Use the provided company context, role context, competencies, and one real-world scenario for inspiration
- Ensure the generated starter project is coherent and runnable as a small Spring Boot Maven app
"""

PROMPT_REGISTRY = {
    "Java - Spring Boot (BASIC)": [
        PROMPT_JAVA_SPRING_BOOT_BASIC_CONTEXT,
        PROMPT_JAVA_SPRING_BOOT_BASIC_INPUT_AND_ASK,
        PROMPT_JAVA_SPRING_BOOT_BASIC_INSTRUCTIONS,
    ],
}