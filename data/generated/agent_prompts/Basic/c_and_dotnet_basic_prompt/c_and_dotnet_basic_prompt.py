# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_CSHARP_DOTNET_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and role requirements?
"""

PROMPT_CSHARP_DOTNET_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a C# and .NET assessment task.

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

1. What will the task be about? (Describe the business domain, API/data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of C# and .NET implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_CSHARP_DOTNET_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in C#, .NET, ASP.NET Core, and basic relational data access, you are given a list of real world scenarios and proficiency levels for C# and .NET.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL ASP.NET Core API connected to a relational database but with a small, realistic logical bug or missing behavior that requires BASIC-level C# and .NET skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL ASP.NET Core API application that is already connected to a relational database and populated with realistic seed data. The .NET application includes:
- Complete project and solution structure with a runnable API service
- Basic ASP.NET Core routing, controller or minimal API endpoints, JSON responses, and status codes
- Simple domain classes, DTOs, and data access code using Entity Framework Core or straightforward ADO.NET-style patterns
- A relational database container initialized with schema and seed data
- Basic logging and error handling already wired into the application
- One or two intentionally clear logical issues in C# endpoint or data-access logic that require entry-level debugging and implementation skills

The candidate's responsibility is to fix a small API/data behavior issue according to the task requirements and then verify the API behaves correctly. A part of the task completion is to use basic C# syntax, null handling, LINQ, simple validation, exception-safe code, readable classes, and maintainable .NET structure at a basic level (around 1 year experience).

The generated task should feel like a realistic backend maintenance ticket for a junior C# and .NET developer. It must not require the candidate to design a system from scratch, create complex architecture, tune advanced database performance, implement authentication, or debug infrastructure.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 characters and clearly describe the basic-level C# and .NET API fix scenario
- Task must provide a working ASP.NET Core API with relational data already seeded and an intentionally clear logic issue suitable for BASIC proficiency
- **CRITICAL**: The ASP.NET Core application should be FULLY FUNCTIONAL, deployed, running, and accessible, but one small API behavior should be incorrect due to basic C# logic or simple data-access mistakes
- **CRITICAL**: The deployment infrastructure must work perfectly. The candidate must not need to fix Docker, database initialization, dependency restore, build errors, or startup failures
- **CRITICAL**: The exact problem described in the task scenario MUST be replicated in the generated code files. For example, if the scenario says an endpoint ignores a query parameter, includes completed records incorrectly, or throws when a collection is empty, the code must contain that behavior in the relevant endpoint or service
- **CRITICAL**: Candidates must understand that fixing the task means modifying simple C#/.NET application code, not rebuilding the project or changing infrastructure
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are relevant to the context
- Generate a complete, running ASP.NET Core API application with a basic relational database schema and seed data suitable for a 15-minute BASIC-level task
- The scenario should be a real-world business scenario requiring basic-level implementation or bug fixing involving:
  * Simple ASP.NET Core route or controller behavior
  * Basic query parameter or request-body validation
  * LINQ filtering, ordering, projection, or FirstOrDefault-style safe handling
  * Basic HTTP status code selection and JSON response consistency
  * Simple data retrieval using EF Core or basic data access
  * NOT building the API from scratch
- The complexity of the implementation task must align with BASIC proficiency level and be completable within {minutes_range} minutes
- Appropriate task examples include a logistics delayed-shipment endpoint, support ticket filtering endpoint, appointment import/status endpoint, inventory restock endpoint, or training registration endpoint inspired by the supplied real-world scenarios
- Keep the domain small: 2-3 tables at most, 1-2 endpoints in focus, and only one primary bug cluster
- The task may ask the candidate to:
  * Validate a simple route or query parameter
  * Correct a LINQ filter or ordering condition
  * Return an empty list instead of throwing on no results
  * Return a clear 400 response for invalid input
  * Avoid unsafe parsing where external input is involved
  * Use properties, constructors, and small methods cleanly
  * Keep classes and methods readable and focused
- The task must NOT require:
  * Advanced concurrency, distributed systems, event sourcing, caching, message queues, or background jobs
  * Complex EF Core migrations or advanced SQL tuning
  * Authentication, authorization, rate limiting, or security architecture
  * Advanced dependency injection lifetime design
  * Advanced async orchestration or thread synchronization
  * Desktop UI, WPF, WinForms, or frontend work as the main task
  * Writing a full test framework setup from scratch
- The question must NOT include hints about the exact code changes needed. The hints will be provided only in the "hints" field and must remain non-revealing
- Ensure that all questions and scenarios adhere to basic C# and .NET practices suitable for entry-level developers
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, C# documentation, .NET documentation, ASP.NET Core documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively implement and fix basic C# and .NET API behavior, rather than testing rote memorization
- Tasks should involve straightforward challenges that require genuine understanding of basic C# syntax, ASP.NET Core routing, LINQ, validation, data access, and readable code structure
- Candidates will be encouraged to use AI to help with boilerplate code and documentation lookup, but they must understand the simple business logic and .NET code they change

## Code Generation Instructions
Based on the real-world scenarios provided above, create a C# and .NET BASIC task that:
- Draws inspiration from the input scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency, keeping in mind that AI assistance is allowed but should not diminish the need for basic C# implementation and debugging skills
- Tests practical C# and .NET skills including simple classes, properties, control flow, LINQ, null handling, input validation, exception-safe behavior, HTTP responses, and basic data access
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick a different real-world scenario from the list provided above to ensure variety in task generation
- **CRITICAL**: The ASP.NET Core application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, startup configuration, data access, and database connection setup, but with intentionally clear logical mistakes or missing behavior
- **CRITICAL**: The task focuses on fixing existing basic application behavior, NOT building from scratch or debugging deployment
- The database connection setup should work without errors and should not be the assessment focus
- All routes should be implemented and accessible, even when one route returns incorrect results or handles an edge case incorrectly
- The code files generated must be valid, build successfully, and run without crashes during startup
- Use a modern .NET project structure with a small number of files and clear naming
- Use ASP.NET Core minimal APIs or simple controllers; do not create layered enterprise architecture for a BASIC task
- Use Entity Framework Core for simple CRUD/query access where practical, or straightforward ADO.NET-style data access if the scenario is simpler
- Keep database tables and seed data small but realistic enough to expose the bug
- Do not include comments that reveal the solution or point directly to the line to change

## Infrastructure Requirements
- MUST include a complete, fully functional ASP.NET Core API structure that connects to a relational database container
- MUST include docker-compose.yml for the API service and the datastore service actually used by the scenario
- MUST include init_database.sql to initialize the relational database schema and seed data
- MUST include run.sh which has the end-to-end responsibility of deploying the infrastructure successfully
- MUST include a Dockerfile for the .NET application container
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so no cleanup script is needed
- **CRITICAL - DEPLOYMENT MUST BE PERFECT**: The infrastructure setup must be fully automated and work without any errors. Candidates should receive a running application, NOT a broken deployment
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- The in container environment uses docker-compose to run all services
- The relational datastore should be PostgreSQL unless the selected scenario makes another available datastore clearly more appropriate; do not invent extra services
- Use hardcoded local assessment configuration values in appsettings.json or source configuration files. Do not require candidates to create secrets or environment files
- The application container should expose one API port such as 8080 and the datastore port must be bound to localhost only

### Docker-compose Instructions
- Include exactly the services needed for the task: one ASP.NET Core API service and one relational database service
- **MUST NOT include any version specification** in the docker-compose.yml file
- **MUST NOT include environment variables or .env file references**
- Use hardcoded local configuration values instead of environment variables or .env files
- The API service must depend on the database service and must be able to connect using deterministic service names
- The database must initialize automatically from init_database.sql with schema and seed data before the candidate starts work
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host
- For PostgreSQL, bind the datastore as `127.0.0.1:5432:5432`; for any other relational datastore, apply the same localhost-only pattern with the correct port
- Bind the API port to localhost as well, for example `127.0.0.1:8080:8080`
- Provide a healthcheck for the database service and use depends_on with health conditions where supported
- Use a named volume for database persistence if needed
- Do not include Redis, queues, search services, or extra infrastructure unless the selected scenario explicitly requires them
- **CRITICAL**: Docker compose must result in both services running successfully
- **TESTING REQUIREMENT**: Mentally verify that this docker-compose configuration will start the database, initialize schema and seed data, build the .NET app, and expose the API

### init_database.sql Instructions
- init_database.sql must create a small relational schema that directly supports the selected business scenario
- Use 2-3 tables at most, with primary keys and simple foreign keys where useful
- Include realistic seed data that exposes the incorrect API behavior
- Keep SQL valid and executable in one pass
- Do not include solution hints in SQL comments
- Do not create advanced database features, stored procedures, triggers, partitioning, complex indexes, or DBA-heavy requirements
- The schema should support straightforward data access only
- Seed data should include edge cases relevant to the BASIC task, such as no matching records, completed versus open statuses, invalid or boundary dates, or multiple related rows
- The database must be FULLY POPULATED before the API health check succeeds

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d` and ensures successful deployment
- **CRITICAL**: This script must work perfectly without any errors
- Do not run apt-get install, dotnet restore, dotnet tool install, or package manager install commands in run.sh; the runtime and common libraries are pre-installed by the E2B template or handled by Docker build
- WAIT MECHANISM: Implements a proper health check loop to wait for the database service to be fully ready and accepting connections
- VALIDATION: Validates that the ASP.NET Core API is responding on a health endpoint or simple read endpoint
- DATA INITIALIZATION: Database initialization must be automatic through the database container initialization path, not manual candidate steps
- MONITORING: Prints clear progress logs and shows useful container logs on failure
- ERROR HANDLING: Exits clearly if the database or API does not become healthy
- LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
- **SUCCESS CONFIRMATION**: Script should clearly indicate successful deployment completion and the local API URL
- Do not include cleanup behavior in run.sh

### Dockerfile Instructions
- MUST generate a complete, valid Dockerfile for the ASP.NET Core application
- **CRITICAL**: Dockerfile MUST build successfully without errors
- Use an appropriate .NET SDK image for build and ASP.NET runtime image for runtime
- Use a multi-stage build with restore, build, publish, and runtime stages
- Copy the .csproj file first for better Docker layer caching, then copy source code
- Set WORKDIR to /root/task to match the file location
- Expose the API port used by the application, such as 8080
- Start the app with the published DLL
- Do not depend on .env files or environment variable references
- Ensure all COPY commands reference correct file paths
- Keep the Dockerfile simple and appropriate for a small ASP.NET Core API

The output should be a valid json schema with proper file structure and include:
- README.md
- .gitignore
- docker-compose.yml
- run.sh
- init_database.sql
- Dockerfile
- C# project file
- ASP.NET Core source files
- appsettings.json or equivalent local configuration file
- optional basic test or verification files only if they are lightweight and do not distract from the main task

## Code file requirements
- Multiple files will be generated and must be included in the JSON structure correctly
- Code should follow basic C# and .NET best practices with clear names, small methods, simple classes, and readable formatting
- **CRITICAL**: The ASP.NET Core application files must be complete and fully functional with all endpoints accessible and database connection working
- **CRITICAL**: The exact problems described in the task scenario must be present in the code. Do not implement the final corrected behavior
- **CRITICAL**: Deployment files, docker-compose.yml, Dockerfile, init_database.sql, and run.sh must be perfect and work without errors
- The bug or missing feature must be logical, not syntactic
- The application should build and start successfully
- Do NOT include TODO comments that reveal what to implement
- Do NOT include comments that give away the solution or hint at the exact fix
- Do NOT include placeholder code or empty files that make the project feel unfinished
- Keep the focused code path small enough for a BASIC candidate to understand quickly
- Use C# features within BASIC scope: variables, if/switch/loops, properties, constructors, simple classes, interfaces only when useful, List<T>, Dictionary<TKey,TValue>, basic LINQ, try/catch where meaningful, async/await for database calls without blocking
- Do not require advanced generics, reflection, expression trees, custom middleware design, complex DI lifetimes, advanced concurrency, or deep EF Core features
- Use dependency injection in a simple, standard way appropriate for ASP.NET Core
- Use ILogger with simple meaningful messages where helpful
- Include a health endpoint or simple known-good endpoint for run.sh validation
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for C#/.NET, Docker, and relational database development tasks that includes:
- .NET build artifacts such as bin/ and obj/
- User-specific IDE files such as .vs/, .vscode/, .idea/, *.user, and *.suo
- Test result and coverage folders such as TestResults/ and coverage/
- Log files such as *.log
- Local database and Docker volume data directories
- OS-specific files such as .DS_Store and Thumbs.db
- Temporary files and common editor swap files
- Environment files such as .env even though the task must not rely on them
- Any other standard exclusions for small ASP.NET Core projects

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the generated C# and .NET BASIC task. Content must describe the business impact and observable behavior without revealing the exact implementation.

### Task Overview
- Task Overview must be 3-4 meaningful sentences
- Do not use a bullet list in this section
- Describe the business scenario, the current state of the running API, and why the problem matters
- Make clear that the application is already deployed and running, but one focused API behavior is incomplete or incorrect
- Keep the description beginner-friendly and specific to the selected scenario
- NEVER leave this section empty
- Do NOT include bold time-budget callouts

### Objectives
- Objectives must contain 4-6 bullets maximum
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix. A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like. It does NOT name the API, library, pattern, or algorithm that solves it. Objectives describe the 'what' and 'why', never the 'how'
- Each bullet should be a full, context-rich sentence — not a two-word label
- BAD: "Improve query performance."
- GOOD: "The delayed shipments view includes delivered shipments and misses the requested delay threshold; after your changes it should return only active shipments that match the requested delay window."
- Include outcomes around correct response status codes, correct filtered results, safe empty-result handling, and readable maintainable code where appropriate
- Do not name the exact method, LINQ operator, class, or database query that solves the issue

### Helpful Tips
- Helpful Tips must contain 4-5 bullets maximum
- Provide practical guidance without revealing specific implementations
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze"
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task
- Focus on inspecting request inputs, response behavior, boundary cases, data relationships, and error messages
- Do not include specific code snippets, exact method names, exact query changes, or solution patterns

### How to Verify
- How to Verify must contain 4-6 bullets maximum
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write
- Each bullet is a check the candidate can run, such as an API response shape, status code, empty-list behavior, log message, or seeded-data scenario
- Include checks for valid inputs, invalid inputs, empty results, and business correctness where relevant
- Do not include setup commands or Docker commands
- Do not reveal the exact code changes required

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section):**
- Setup commands such as `dotnet restore`, `dotnet build`, `dotnet test`, `docker compose up`, or package installation commands
- Database-connection details, including host, port, username, password, client-tool suggestions, or `<DROPLET_IP>` placeholders
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this method", or "write this exact query"

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A short kebab-case GitHub repository name under 50 characters that describes the C# and .NET BASIC task without using spaces or title case.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name.",
  "question": "A complete candidate-facing task description that explains the selected business scenario, the running ASP.NET Core API, the focused incorrect behavior, the expected observable outcomes, and the time-bounded BASIC-level nature of the work without revealing the implementation solution.",
  "code_files": {{
    "README.md": "Candidate-facing README using exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with concise non-revealing business and verification guidance.",
    ".gitignore": "A comprehensive .gitignore for C#/.NET, IDE files, Docker artifacts, logs, local database data, temporary files, and environment files that are not used by the task.",
    "docker-compose.yml": "Docker Compose configuration with no version field, no .env references, no environment variable references, one ASP.NET Core API service, one relational database service, localhost-only port bindings, health checks, and deterministic service names.",
    "Dockerfile": "A multi-stage Dockerfile that builds and publishes the ASP.NET Core API from /root/task and runs the published application on the configured API port.",
    "run.sh": "A complete deployment and validation script that runs docker compose up -d from /root/task, waits for the database and API to become healthy, prints useful progress logs, and fails with container logs when deployment is not healthy.",
    "init_database.sql": "A complete relational schema and realistic seed data file that initializes the database in one pass and exposes the selected business edge cases without solution hints.",
    "TaskApi.csproj": "The .NET project file with the required ASP.NET Core and basic data-access package references needed by the generated application.",
    "Program.cs": "The ASP.NET Core application entry point with service registration, routing setup, basic logging, database connection configuration, and health endpoint wiring.",
    "appsettings.json": "Local assessment configuration values used by the app to connect to the database without requiring secrets, .env files, or manual setup.",
    "Models/DomainModels.cs": "Simple C# domain or entity classes with properties, constructors where useful, nullable annotations where appropriate, and names matching the selected business scenario.",
    "Data/AppDbContext.cs": "Basic Entity Framework Core DbContext or equivalent simple data-access setup that maps the small schema used by the task.",
    "Services/DomainService.cs": "A focused service class containing the intentionally incorrect or incomplete business/data logic that the candidate must inspect and correct.",
    "Controllers/DomainController.cs": "A simple ASP.NET Core controller or endpoint handler exposing the relevant API route with request validation, response formatting, and one focused behavior that needs correction."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the expected correction to validation, filtering, empty-result handling, status codes, data access, and code readability without requiring advanced architecture.",
  "definitions": "An object of term-to-definition pairs for the C#/.NET and business-domain terms used in the task, such as ASP.NET Core route, query parameter, LINQ, DTO, DbContext, HTTP 400, and seed data.",
  "hints": "A single line hint that nudges the candidate toward comparing request inputs, seeded data, and observed API responses without revealing the exact code change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable correctness improvements, safe edge-case handling, and maintainable C#/.NET code. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including basic C# syntax, ASP.NET Core API concepts, LINQ, simple HTTP status codes, basic relational data access, Docker Compose awareness, dotnet CLI familiarity, and Git.",
  "short_overview": "Exactly 3 plain sentences: first sentence states what is being built or fixed, second sentence states what the candidate must do, and third sentence states what success looks like. Do not use label prefixes or bullet labels."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no code fences
2. name must be short, descriptive, kebab-case, and under 50 characters
3. title must be in '<action verb> <subject>' format, 50-80 characters, and different from name
4. code_files must include README.md, .gitignore, docker-compose.yml, Dockerfile, run.sh, init_database.sql, .csproj, Program.cs, appsettings.json, and focused C# source files
5. code_files must NOT include kill.sh
6. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, and no other sections
7. README.md must not include setup commands, database connection details, solution snippets, direct implementation instructions, or `<DROPLET_IP>` placeholders
8. docker-compose.yml must include no version specification and must not include environment variables or .env file references
9. Every datastore port exposed to the host must be bound to localhost only using `127.0.0.1:<port>:<port>`
10. run.sh must use `docker compose up -d`, wait for services to become healthy, validate the API, and print logs on failure
11. Deployment must succeed in one go; the candidate fixes only the C#/.NET application behavior, not infrastructure
12. The starter code must compile and run, but must not contain the final corrected logic
13. No TODO comments, solution comments, or hint comments may appear in the generated code files
14. The task must stay within BASIC C# and .NET scope: simple classes, control flow, LINQ, null handling, validation, basic async/await, simple ASP.NET Core routing, and basic data access
15. Do not require advanced architecture, advanced EF Core behavior, authentication, background jobs, caching, distributed systems, complex performance tuning, or advanced concurrency
16. Ensure the task is completable within {minutes_range} minutes by a BASIC-level candidate
"""

PROMPT_REGISTRY = {
    "C# and DotNET (BASIC)": [
        PROMPT_CSHARP_DOTNET_BASIC_CONTEXT,
        PROMPT_CSHARP_DOTNET_BASIC_INPUT_AND_ASK,
        PROMPT_CSHARP_DOTNET_BASIC_INSTRUCTIONS,
    ],
}