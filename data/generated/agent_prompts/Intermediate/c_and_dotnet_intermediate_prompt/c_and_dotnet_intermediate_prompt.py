# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


"""C# and .NET — INTERMEDIATE prompt registry entry."""

PROMPT_CSHARP_DOTNET_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_CSHARP_DOTNET_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
an INTERMEDIATE C# and .NET assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The generated task must be an ASP.NET Core / C# work item that uses a SQL Server database through Entity Framework Core or equivalent .NET data access code.
- The task must be infra-shaped: include a docker-compose.yml for the database service and a run.sh that starts the database service with docker compose up -d.
- The task should evaluate practical intermediate C#/.NET engineering judgement, including API behavior, dependency injection, asynchronous code, data access, validation or error handling, maintainability, and testing.
- The task must be completable within {minutes_range} minutes by a candidate with 3-6 years of C# and .NET experience.
- Do not create a trivia exercise, tool-installation exercise, or broad architecture-only prompt.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about: domain, context, and current problem?
2. What will the candidate build or fix, and how does it match INTERMEDIATE C# and .NET proficiency?
3. Which single real-world scenario did you choose as inspiration, and why does it fit an ASP.NET Core plus SQL Server task?
"""

PROMPT_CSHARP_DOTNET_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements (C# and .NET)

## GOAL
As a technical architect super experienced in C#, .NET, ASP.NET Core, Entity Framework Core, and SQL Server-backed application development, you are given a list of real world scenarios and proficiency levels for C# and DotNET.

Generate a complete assessment task — description, starter code files, README, database infrastructure, and verification guidance — that tests a candidate at INTERMEDIATE proficiency with approximately 3-6 years of experience. The task must be a realistic C#/.NET work item involving an ASP.NET Core API or service layer backed by SQL Server, with enough existing code to diagnose and improve behavior without giving away the solution.

The task must be FULLY FUNCTIONAL and FULLY POPULATED as a starting environment: the project must build, the database container must start, the seed data must be present, and the tests or verification path must expose the current broken or incomplete behavior.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate C# and .NET developer. They are expected to independently work within an existing ASP.NET Core codebase, reason about moderately complex business logic, use async and await appropriately, interact with Entity Framework Core or ADO.NET data access code, follow dependency injection conventions, improve maintainability, and write or update tests for code they own.

The task should require practical engineering judgement rather than memorization. It may involve refactoring duplicated controller logic, moving inefficient LINQ operations into the database, fixing incorrect authorization or validation behavior, improving error handling, preventing mutable shared state bugs, or making a small service easier to test and reason about. It should not require expert-only distributed systems design, Kubernetes orchestration, cloud deployment, advanced OAuth provider setup, or obscure framework configuration.

## INSTRUCTIONS
### Nature of the Task
- **CRITICAL**: The task must ask the candidate to fix or improve an existing C#/.NET implementation, not build an entire application from scratch.
- **CRITICAL**: The task must use an ASP.NET Core API or service-layer scenario with SQL Server data persistence. Do not generate a pure console-only, in-memory-only, or desktop-only task.
- **CRITICAL**: The task must be grounded in ONE of the supplied real-world scenarios. Prefer scenarios involving API correctness, EF Core query behavior, duplicated business logic, entitlement or validation checks, or production-style performance defects.
- **CRITICAL**: The starter implementation must compile and run before the candidate starts. It should contain the exact incomplete, duplicated, inefficient, or buggy behavior described in the task.
- The task should test 4-5 intermediate concepts from the C# and .NET scope: ASP.NET Core routing/controllers, dependency injection, async service methods, Entity Framework Core LINQ queries, DTO projection, validation or consistent HTTP responses, unit/integration tests, and maintainable refactoring.
- The task should require design judgement and correctness reasoning but remain small enough for one candidate to complete within {minutes_range} minutes.
- The current implementation should be intentionally imperfect but realistic: for example, duplicated entitlement checks in two controllers, filtering after ToListAsync, mutable collections returned from a service, inconsistent error responses, missing cancellation token propagation, or hard-to-test static/shared state.
- The candidate-facing question must clearly describe the current behavior and desired observable outcomes, but it must not prescribe the exact API, LINQ expression, class design, or implementation steps.
- Avoid requiring setup of CI/CD pipelines, cloud deployment, Kubernetes, custom authentication provider configuration, advanced security infrastructure, or memorization of obscure C# syntax.
- Do NOT include solution-revealing TODO comments, method names that reveal the fix, or comments in starter code that tell the candidate exactly what to change.
- The time box is {minutes_range} minutes.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, C# and .NET documentation, ASP.NET Core documentation, Entity Framework Core documentation, SQL Server documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The generated task must therefore:
- Assess applied engineering judgement and implementation ability rather than memorization of syntax or framework trivia.
- Be specific enough that external resources help the candidate work faster but do not trivially reveal the whole answer.
- Require the candidate to integrate information into the provided codebase and validate behavior locally.
- Avoid asking for secret, proprietary, credential-based, or internet-dependent integrations.

## C# and .NET Code Generation Instructions
- Generate a complete .NET project using a standard runtime-native manifest such as a .csproj file.
- Use ASP.NET Core Web API conventions appropriate for an intermediate task. Minimal APIs are acceptable only if they still provide enough structure to assess services, data access, dependency injection, and testability.
- Use Entity Framework Core or ADO.NET with SQL Server as the backing datastore.
- The starter code must include realistic models, DTOs, DbContext or data access classes, services, controllers or endpoints, and tests or verification helpers.
- The code must compile with dotnet commands in /root/task.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- Use async/await for database and service operations where appropriate.
- Include enough seed data for the broken behavior to be observable without requiring the candidate to invent records manually.
- Use clear class and method names that fit the domain, but do not name classes or comments in a way that reveals the required fix.
- Keep the codebase small and focused. A good task usually has one ASP.NET Core project, one test project or verification script, a compose file, and seed data.
- If tests are included, they should initially expose the current failing behavior and pass after a correct candidate solution.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## Infrastructure Requirements
The generated task is infra-shaped and must include SQL Server as an external service. The candidate should not need to install SQL Server locally.

### Docker-compose Instructions
- Include a docker-compose.yml file at /root/task/docker-compose.yml.
- **MUST NOT include any version specification** in docker-compose.yml.
- Define only the services required for the assessment. For this task, include a SQL Server database service unless the selected scenario absolutely requires a different datastore from the provided scenario.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- The SQL Server service should expose port 1433 only on localhost, using a mapping such as `127.0.0.1:1433:1433`.
- **MUST NOT include environment variables or .env file references** for application configuration. If the database container image requires minimal container settings to start, keep them inline in docker-compose.yml and do not reference a .env file.
- Do not include unrelated services such as Redis, RabbitMQ, Elasticsearch, or application containers unless the selected real-world scenario actually requires them.
- Use stable, commonly available container images and simple health checks when useful.
- Do not include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic.

### SQL Server Database Instructions
- Include database initialization in a way that works automatically for the starter project. This may be done with an init_database.sql file, EF Core startup seeding, or a small bootstrap script, as long as the database is FULLY POPULATED before verification.
- If an init_database.sql file is included, it must create the database objects and seed rows needed to reproduce the current issue.
- Seed data must reflect the chosen business scenario: for example products, subscriptions, videos, users, restaurants, menu items, orders, or other domain records.
- Keep schema design small and readable. The goal is to assess intermediate application development, not DBA-level schema design.
- Do not include database connection details in the README. Connection strings may appear only in code or configuration files needed for the project to run.

### Run.sh Instructions
- Include /root/task/run.sh.
- run.sh must be executable in intent and written for bash.
- run.sh must use /root/task as the base directory.
- run.sh must start the SQL Server datastore with `docker compose up -d`.
- run.sh may wait briefly for the database to become ready and then run the appropriate dotnet build, test, or verification command.
- Do not include apt-get install, dotnet installation commands, SDK installation commands, package-manager bootstrap commands, or runtime installation steps.
- Do not use environment variables or .env file references for application configuration in run.sh.
- Keep run.sh simple and deterministic.

The output should be a valid json schema with code_files containing at minimum:
- "README.md": candidate-facing README with exactly the required sections and no solution-revealing material.
- ".gitignore": standard C#/.NET exclusions.
- "docker-compose.yml": SQL Server datastore definition for the task.
- "run.sh": script that starts the datastore and runs the local verification command.
- "src/<ProjectName>/<ProjectName>.csproj": the ASP.NET Core project manifest.
- "src/<ProjectName>/Program.cs": application startup, dependency injection, routing, and configuration required for the starter behavior.
- "src/<ProjectName>/Data/<DbContext>.cs": EF Core DbContext or equivalent data access setup.
- "src/<ProjectName>/Models/": domain models required for the scenario.
- "src/<ProjectName>/Services/": service code containing the realistic incomplete, duplicated, inefficient, or buggy behavior.
- "src/<ProjectName>/Controllers/": API endpoints or controllers exposing the current behavior.
- "tests/<ProjectName>.Tests/<ProjectName>.Tests.csproj": test project manifest when tests are included.
- "tests/<ProjectName>.Tests/": focused tests or verification fixtures that expose the intended behavior without containing the solution.

## Code file requirements
- Every file in code_files must contain complete file contents, not summaries.
- The starter project must be runnable from /root/task using the commands described in run.sh or README verification guidance.
- The generated code must not include placeholders such as "implementation goes here", "TODO: fix this", "your code here", or ellipses in place of real code.
- The starter code must represent the current broken or incomplete implementation exactly as described in the question.
- The code should be realistic but compact. Avoid excessive scaffolding that hides the assessment signal.
- Keep dependencies limited to common .NET packages suitable for ASP.NET Core, Entity Framework Core, SQL Server access, and testing.
- Do not require the candidate to install additional system packages.
- Do not include secrets, production credentials, or external network calls.
- Use deterministic seed data and deterministic tests wherever possible.
- Ensure all C# files use consistent namespaces and project references so the solution builds cleanly.
- The candidate should need to modify business logic, service/data access logic, controller behavior, or tests; they should not need to repair project structure or missing files.

## .gitignore INSTRUCTIONS
The .gitignore file must be appropriate for a C# and .NET repository. It should exclude:
- bin/ and obj/ directories.
- TestResults/ and coverage output.
- IDE folders such as .vs/, .vscode/ when appropriate, and Rider metadata.
- User-specific files such as *.user, *.suo, and *.rsuser.
- Logs and temporary files.
- Local database artifacts if any are generated.
Do not exclude source code, project files, README.md, docker-compose.yml, run.sh, or seed files required for the task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md entry inside code_files must contain exactly these sections, in this order, and no other headings:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
- Write 3-4 meaningful sentences.
- Do not use a bullet list.
- Describe the business scenario, current state, and why the problem matters.
- The section must NEVER be empty.
- Do not include bold time-budget callouts.

### Objectives
- Write 4-6 bullets maximum.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the "what" and "why", never the "how".
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Improve query performance."
- GOOD: "The product search endpoint returns results in 4-6 seconds under normal load; after your changes it should respond in under 500ms for typical query patterns."

### Helpful Tips
- Write 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not include direct solution steps.

### How to Verify
- Write 4-6 bullets maximum.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run or observe, such as test output, response shape, status code, latency observation, log line, or database-backed behavior.
- You may mention the provided verification command or test command, but do not include setup commands.

### Content to Exclude From the README (instruction — do not emit as a section)
Keep the following out of the README. This is an instruction to you, not a README section:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `dotnet restore`, `dotnet test`, `mvn test`, or similar installation/run commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Database-connection details such as host, port, username, password, connection strings, or client-tool suggestions.
- `<DROPLET_IP>` placeholders.
- Extra README sections such as "Database Schema Overview", "Database Access", "Performance Issues", "Setup", or "Installation".

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as "task_title", "files", or "context" because synonyms produce a hollow, unusable task.

Return a single valid JSON object matching this schema. Each value below describes what to fill in; do not return placeholder examples.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the selected C# and .NET task without using generic words like assessment or challenge.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from name, and specific to the selected scenario.",
  "question": "The full candidate-facing task description, including the business context, the Current Implementation with the exact buggy or incomplete behavior represented by the starter code, and the Required Changes expressed as observable outcomes without revealing the full implementation.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content using exactly the four required sections: Task Overview, Objectives, Helpful Tips, and How to Verify.",
    ".gitignore": "A complete C# and .NET .gitignore containing standard build, IDE, test, log, and temporary-file exclusions while keeping all task files trackable.",
    "docker-compose.yml": "A complete docker compose file for the SQL Server datastore, without a version specification, with localhost-only port binding, and without .env file references.",
    "run.sh": "A complete bash script that uses /root/task as the base directory, starts the datastore with docker compose up -d, waits if needed, and runs the project verification command without installing runtimes or packages.",
    "src/<ProjectName>/<ProjectName>.csproj": "The complete ASP.NET Core project file with the package references needed for the starter API, EF Core SQL Server access, and compilation.",
    "src/<ProjectName>/Program.cs": "The complete application startup file containing service registration, configuration, routing, and database initialization needed for the starter application to run.",
    "src/<ProjectName>/Data/<DbContext>.cs": "The complete EF Core DbContext or equivalent data access class representing the small SQL Server-backed schema used by the scenario.",
    "src/<ProjectName>/Models/<Model>.cs": "Complete domain model files for the selected scenario with realistic properties needed by the starter behavior and seed data.",
    "src/<ProjectName>/Dtos/<Dto>.cs": "Complete DTO files for API responses or request bodies where the scenario benefits from stable response shapes.",
    "src/<ProjectName>/Services/<Service>.cs": "Complete service-layer files containing the current incomplete, duplicated, inefficient, or buggy implementation the candidate must improve.",
    "src/<ProjectName>/Controllers/<Controller>.cs": "Complete API controller files or endpoint definitions exposing the current behavior to be fixed.",
    "tests/<ProjectName>.Tests/<ProjectName>.Tests.csproj": "The complete test project file when tests are included, referencing the application project and the chosen .NET test packages.",
    "tests/<ProjectName>.Tests/<TestFile>.cs": "Complete focused tests or integration checks that demonstrate the expected observable behavior without containing the candidate's solution."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the key changes a strong intermediate C# and .NET candidate would make, including service/data access/controller/test changes, without needing to provide a full patch.",
  "definitions": "An object mapping task-relevant C# and .NET terms to concise definitions, such as dependency injection, async query, DTO, service layer, controller action, cancellation token, or database projection, using only terms that genuinely appear in the task.",
  "hints": "A single line hint nudging the candidate toward investigating the right area of the C#/.NET application without naming the exact fix, API, method, pattern, or query transformation.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable API correctness, database-backed behavior, maintainability, performance, or consistent response improvements. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as C# and .NET, ASP.NET Core basics, EF Core or SQL-backed data access, Docker Compose for the provided database, and running local tests.",
  "short_overview": "Exactly 3 plain sentences: first sentence states what is being built or fixed, second sentence states what the candidate must do, and third sentence states what success looks like. Do not use label prefixes such as Business problem:, Technical focus:, Expected outcome:, or any other Label: form."
}}

## CRITICAL REMINDERS
1. **CRITICAL**: Output must be valid JSON and must use the canonical top-level keys exactly: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, and short_overview.
2. **CRITICAL**: Escape all JSON content correctly so that every file body is represented as a valid JSON string.
3. **CRITICAL**: The generated task must include docker-compose.yml and run.sh because this is an infra-shaped task.
4. **CRITICAL**: Do not include kill.sh.
5. **CRITICAL**: docker-compose.yml must not include a version specification and datastore ports must be bound to localhost only.
6. **CRITICAL**: The candidate's starting environment must be FULLY FUNCTIONAL and FULLY POPULATED.
7. **CRITICAL**: Starter code must compile and run, but must not contain the core solution.
8. **CRITICAL**: README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, with no additional README headings.
9. **CRITICAL**: The README must not include setup commands, direct solution steps, database connection details, or solution-revealing API/library/method names.
10. **CRITICAL**: The task must stay within intermediate C# and .NET scope and be completable within {minutes_range} minutes.
11. **CRITICAL**: All code and scripts must reference /root/task as the base directory.
12. **CRITICAL**: The short_overview value must be exactly 3 plain sentences with no label prefixes.
"""

PROMPT_REGISTRY = {
    "C# and DotNET (INTERMEDIATE)": [
        PROMPT_CSHARP_DOTNET_INTERMEDIATE_CONTEXT,
        PROMPT_CSHARP_DOTNET_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_CSHARP_DOTNET_INTERMEDIATE_INSTRUCTIONS,
    ]
}