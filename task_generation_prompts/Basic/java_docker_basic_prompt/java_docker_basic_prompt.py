PROMPT_DOCKER_JAVA_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A software engineer with 1–2 years of experience in Java and Docker is expected to work on small internal tools and services that are easy to build, run, and hand off across environments. They should be comfortable writing clean Java code with basic object-oriented design, collections, exception handling, and simple tests. They should also understand how application structure, startup behavior, configuration, and build outputs affect containerization readiness, even when the task itself stays focused on source code and build artifacts rather than full deployment infrastructure.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DOCKER_JAVA_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java and Docker assessment task.

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

IMPORTANT CATEGORY CONSTRAINT:
- This task is PURE_CODE
- Do NOT require Docker Compose, databases, web frameworks, multiple services, or deployment infrastructure
- Keep the deliverable to Java source code, Maven/Gradle build files, tests, and candidate-facing documentation only
- Docker competency should be assessed through container-readiness concerns that are naturally visible in code and build outputs, such as predictable startup behavior, clean build artifacts, configuration handling, and avoiding machine-specific assumptions

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Java implementation required, the expected deliverables, and how it aligns with BASIC Java and Docker proficiency within a PURE_CODE task)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DOCKER_JAVA_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Java application development and Docker fundamentals, you are given a list of real-world scenarios and proficiency levels for Java and Docker.
Your job is to generate a complete assessment task definition for a BASIC-level candidate. The task must primarily assess practical Java coding ability while secondarily assessing whether the candidate can structure the application in a way that is easy to package and run consistently in a containerized environment later.

## HARD BOUNDARIES
- This is a PURE_CODE task.
- Do NOT generate Dockerfile, docker-compose.yml, shell deployment scripts, database setup, or any infrastructure files.
- Do NOT require Spring Boot, REST APIs, JDBC, message brokers, microservices, advanced concurrency, or system design.
- Keep the task scoped to a small Java application with source files, a build file, tests, and README only.
- Docker knowledge must stay BASIC and must be assessed indirectly through code/build decisions that support container-readiness:
  - clear application entrypoint
  - predictable command-line execution
  - simple configuration via arguments or environment abstraction
  - stdout/stderr logging instead of machine-specific UI assumptions
  - no hardcoded absolute local paths
  - clean dependency/build setup
- Do NOT require image signing, registries, compose orchestration, security hardening, resource tuning, advanced networking, or multi-stage builds as primary skills.

## PROFICIENCY ALIGNMENT
The task must align with BASIC proficiency (1–2 years, {minutes_range} minutes):
- Combine 2–3 concepts, not more
- Well-scoped feature work or bug fixing
- No advanced architecture
- No performance tuning as the main challenge
- No advanced synchronization or concurrency-heavy design
- Testing should be straightforward and limited in scope

## EXPECTED SKILL COVERAGE

### Java (BASIC) — allowed focus areas
Use only concepts naturally supported by the Java BASIC scope:
- packages and naming conventions
- classes, encapsulation, simple inheritance/polymorphism only if helpful
- control flow and foundational syntax
- collections such as List, Set, Map
- basic exception handling with try-catch-finally
- maintainable code organization
- small refactors for readability
- straightforward JUnit tests
- simple thread usage only if very minor, but avoid making concurrency the core of the task

### Docker (BASIC) — allowed focus areas in a PURE_CODE task
Since infrastructure files are out of scope, assess Docker-adjacent readiness through:
- application starts from a single obvious main class
- build produces a runnable artifact cleanly
- configuration is not tied to one developer machine
- file paths are relative and portable
- output is visible in console logs
- README describes how the application should be run and verified in a consistent way
- optional use of environment variables in Java is acceptable only at a very basic level

Do NOT make Docker the primary implementation surface in this task.

## NATURE OF THE TASK
- The task must ask the candidate to implement a small feature, fix a logical bug, or refactor a small Java codebase.
- The scenario must be realistic and inspired by one provided real-world scenario.
- The starter project must be runnable with Maven or Gradle from the command line.
- The candidate should need to modify Java code meaningfully.
- The task should also reveal whether the candidate understands how to keep the app easy to package and run consistently later.
- The task must not be a trick question or syntax-only exercise.

## RECOMMENDED TASK SHAPE
Use one of these patterns:
1. Small CLI application with incomplete feature logic
2. Small CLI/reporting tool with buggy collection handling and weak exception handling
3. Small file-processing or queue-like utility with poor structure that needs cleanup and tests

Best fit for this competency pair:
- a Java CLI tool or small console application
- uses collections and classes
- reads a small input file or in-memory sample data
- prints a summary/report to stdout
- has one or two bugs or missing behaviors
- needs a cleaner entrypoint and portable configuration handling

## STARTER CODE REQUIREMENTS
- Provide enough starter code so the candidate can begin immediately.
- The project must compile or be very close to compiling with only task-related fixes needed.
- Use standard Java project structure.
- Include a pom.xml or build.gradle.
- Include a main application entrypoint.
- Include 1-3 focused Java classes plus tests as needed.
- Do NOT include the full solution in starter code.
- Do NOT include TODO comments, placeholder comments, or hints in code.
- Keep the codebase small and readable.

## FILE STRUCTURE REQUIREMENTS
The output JSON must describe only PURE_CODE files such as:
- README.md
- .gitignore
- pom.xml OR build.gradle
- src/main/java/... Java source files
- src/test/java/... test files

Do NOT include:
- Dockerfile
- docker-compose.yml
- run.sh
- kill.sh
- database files
- framework-specific infrastructure
- package.json
- frontend assets

## README.md REQUIREMENTS
The README must be concise and candidate-facing with these sections:
- Task Overview
- Helpful Tips
- Objectives
- How to Verify

### Task Overview
- 2-4 meaningful sentences
- Describe the business scenario and current state of the Java tool/application
- Mention that the application should be easy to run consistently across environments
- Do not directly tell the candidate how to implement the solution

### Helpful Tips
- 3-5 bullets max
- Start bullets with words like "Consider", "Think about", "Review", "Explore"
- Guide discovery without giving away the answer
- May gently point toward portability, startup behavior, and clean input handling

### Objectives
- 3-5 bullets max
- Describe outcomes, not implementation steps
- Include correctness, maintainability, and consistent run behavior
- Avoid explicit Docker commands or infrastructure instructions

### How to Verify
- 3-5 bullets max
- Focus on observable outcomes:
  - application starts successfully
  - expected output is produced
  - invalid input is handled clearly
  - tests pass
  - behavior is consistent when run with different simple inputs

## AI AND EXTERNAL RESOURCE POLICY
- Candidates may use external resources, including AI tools and official documentation.
- The task should still require genuine reasoning about Java code structure, collections, exceptions, and basic run behavior.
- Avoid tasks that can be solved by a one-line syntax fix alone.

## REQUIRED OUTPUT JSON STRUCTURE
{
  "name": "short-kebab-case-task-name",
  "title": "Human-readable title in '<action verb> <subject>' format, 50-80 characters",
  "question": "Short scenario and specific ask. Make clear the candidate will complete or fix a small Java application and improve its consistency of execution.",
  "code_files": {
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, How to Verify",
    ".gitignore": "Standard Java and IDE exclusions",
    "pom.xml": "Maven build file with required dependencies, or build.gradle",
    "src/main/java/com/example/.../Application.java": "Main entrypoint",
    "src/main/java/com/example/.../*.java": "Supporting Java classes",
    "src/test/java/com/example/.../*.java": "Focused unit tests"
  },
  "outcomes": "Bullet-point list in simple language. Include expected behavior after completion. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing the business problem, the Java implementation goal, and the expected outcome.",
  "pre_requisites": "Bullet-point list including Java 11+ or 17+, Maven or Gradle, IDE, Git, and basic command-line familiarity.",
  "answer": "High-level solution approach focused on Java structure, collections, exception handling, tests, and portable run behavior.",
  "hints": "A single-line hint that nudges toward clean Java structure and consistent execution behavior without revealing the solution.",
  "definitions": {
    "Entrypoint": "The main class or command used to start an application",
    "Runnable Artifact": "A built application package that can be executed consistently in another environment",
    "Exception Handling": "The process of catching and responding to runtime problems in a controlled way",
    "Portable Configuration": "Settings that do not depend on one specific machine or absolute local paths",
    "Collection": "A Java data structure such as List, Set, or Map used to store groups of values"
  }
}

## CODE FILE REQUIREMENTS
- Java code should follow standard naming and package conventions.
- Use simple OOP structure.
- Use collections meaningfully.
- Include basic exception handling.
- Include straightforward tests.
- Keep the project small enough for BASIC level completion within {minutes_range} minutes.
- If using file input, keep it simple and local to the repository.
- Avoid advanced libraries unless absolutely necessary.
- Prefer plain Java plus JUnit.

## .gitignore REQUIREMENTS
Generate a standard Java .gitignore including:
- target/
- build/
- .gradle/
- .idea/
- .vscode/
- *.iml
- *.class
- *.log
- OS-specific files

## TASK CALIBRATION GUIDANCE
Calibrate toward tasks like:
- fixing collection logic in a small Java utility
- improving exception handling and output formatting
- making a CLI app easier to run from the command line
- adding a few focused tests
- ensuring the app does not rely on hardcoded local-machine assumptions

## CRITICAL REMINDERS
1. Output must be valid JSON only when the task is later generated.
2. The task must stay within Java BASIC and Docker BASIC scope.
3. Docker must be assessed indirectly because this is a PURE_CODE task.
4. Do not include any infrastructure or deployment files.
5. Keep the task practical, small, and realistic.
6. The candidate must write meaningful Java code, not just documentation.
7. The task must be solvable within {minutes_range} minutes.
8. The registry key for this prompt file is exactly "Docker (BASIC), Java (BASIC)".
"""

PROMPT_REGISTRY = {
    "Docker (BASIC), Java (BASIC)": [
        PROMPT_DOCKER_JAVA_BASIC_CONTEXT,
        PROMPT_DOCKER_JAVA_BASIC_INPUT_AND_ASK,
        PROMPT_DOCKER_JAVA_BASIC_INSTRUCTIONS,
    ]
}