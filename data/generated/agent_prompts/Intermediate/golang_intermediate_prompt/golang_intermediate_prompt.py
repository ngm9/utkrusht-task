# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


PROMPT_GOLANG_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Go (Golang) assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL SKILL CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Go implementation or fix required, the expected deliverables, and how it aligns with the given Go proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GOLANG_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Go and modern Go ecosystem, you are given a list of real world scenarios and proficiency levels for Go development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## CONTEXT & CANDIDATE EXPECTATION
- The candidate is being assessed for INTERMEDIATE Golang proficiency, typically 3-6 years of experience.
- The task should feel like a realistic production issue or feature request that an experienced Go engineer would handle independently.
- The starting repository must be FULLY FUNCTIONAL as a project skeleton and FULLY POPULATED with realistic starter files, but the core solution must remain incomplete, flawed, or insufficient so the candidate still has meaningful work to do.
- The task should evaluate strong command of Go core syntax, project structure with modules/packages, concurrency with goroutines and channels, error handling, testing, debugging, and performance awareness.
- The task should especially emphasize asynchronous and multithreaded programming patterns in Go, including safe coordination, cancellation, race-condition prevention, and concurrency-aware design.
- The candidate should be expected to reason about correctness, reliability, maintainability, and performance under concurrent load.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix errors.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and the specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-6 years Go experience), ensuring that no two questions generated are similar.
- **CRITICAL**: You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- **CRITICAL**: The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- **CRITICAL**: The task must be completable within {minutes_range} minutes by a strong intermediate Go engineer using external resources if needed.
- **CRITICAL**: Because this is a pure local runtime task, do NOT require Docker, external databases, caches, queues, brokers, or any other infrastructure services.
- **CRITICAL**: The task should focus on in-process Go concurrency and asynchronous workflow design, such as worker coordination, context cancellation, structured error propagation, race-condition prevention, goroutine lifecycle management, synchronization, and performance-sensitive execution.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Idiomatic Go Design**: Interface design, composition over inheritance, error handling patterns, context usage
  - **Architecture & Structure**: Clean package boundaries, dependency injection, module design, maintainable service organization
  - **Concurrency Patterns**: Goroutines, channels, select statements, sync primitives, context cancellation, worker coordination, fan-in/fan-out or pipeline-style thinking where appropriate
  - **Concurrency Safety**: Race condition prevention, proper mutex usage, safe shared state access, avoiding deadlocks, avoiding goroutine leaks
  - **Performance Optimization**: Efficient algorithms, memory management awareness, profiling and benchmarking readiness, minimizing blocking and contention
  - **Advanced Go Features**: Generics awareness where appropriate, embedding, type assertions, reflection only when justified, functional options only when natural to the scenario
  - **Error Handling**: Custom error types, error wrapping, error inspection patterns, coordinated failures across concurrent execution paths
  - **Code Quality**: Go idioms, effective Go practices, proper package design, gofmt-compliant code, testability, meaningful tests
  - **Real-world Patterns**: Service/repository boundaries when useful, adapter-style abstractions, graceful shutdown, lifecycle management
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Go best practices (Go 1.20+ is acceptable) and current development standards.
- Tasks should require candidates to make engineering decisions and justify their approach through code structure and behavior.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Go documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should reflect intermediate Go proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Go task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-6 years Go experience), keeping in mind that AI assistance is allowed.
- Tests practical Go skills that require architectural thinking, concurrency correctness, debugging ability, performance considerations, and robust error handling.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on a pure local multi-package Go application that runs with native Go tooling only.
- Should test the candidate's ability to structure a scalable Go application.
- Prefer scenarios where the candidate must analyze or repair concurrent behavior under realistic load or cancellation conditions.
- The repository should be runnable and testable with native Go commands such as `go test ./...` and, if appropriate, `go run ./...`.
- Include unit tests and/or integration-style tests using the standard `testing` package that expose the intended gap without revealing the exact implementation.
- The starter code should be valid and executable, but the tests should fail until the candidate correctly completes the task.

## Infrastructure Requirements

### Docker-compose Instructions
- This is a `non_infra` task.
- **CRITICAL**: MUST NOT include `docker-compose.yml`.
- **CRITICAL**: MUST NOT include any version specification because no compose file should exist for this task.
- **CRITICAL**: MUST NOT include environment variables or .env file references for infrastructure setup.
- **CRITICAL**: Do not expose ports, define services, volumes, or networks because this task must run purely with local Go tooling.
- If the selected real-world scenario mentions external systems, adapt the scenario into an in-memory, local, reproducible Go exercise instead of provisioning those systems.

### Native Runtime Instructions
- Use the runtime's native manifest and tooling for a pure local Go project.
- Include `go.mod` as the required manifest file.
- `go.sum` may be included and can be empty if no additional dependencies are needed.
- The task should run locally with standard Go commands only, with no shell setup required beyond what is naturally implied by the manifest and tests.
- Do NOT include `init_database.sql`, Redis configuration, message broker configuration, or any datastore bootstrap files.
- Favor standard library packages unless a very common Go dependency is genuinely necessary for the assessment.
- Include tests that validate concurrency behavior, cancellation behavior, error handling, and race-safety expectations where appropriate.

### Run.sh Instructions
- Because this is a pure local `non_infra` Go task, `run.sh` is optional and should generally be omitted.
- Prefer letting the candidate use native commands such as `go test ./...`.
- If you choose to include `run.sh`, it must only call native Go commands and must NOT call Docker, docker compose, apt-get, pip, npm, or any infrastructure bootstrap.
- Do NOT include package installation commands for Go itself or common libraries.
- Any optional script must reference `/root/task` as the base directory.

The output should be a valid json schema:
- `README.md`
- `.gitignore`
- `go.mod`
- `go.sum`
- `cmd/app/main.go` or another realistic Go entrypoint file
- `internal/...` package files for domain logic, concurrency orchestration, services, adapters, errors, or models as appropriate
- `_test.go` files that verify the intended behavior and expose the missing functionality or bug
- Additional Go source files that are needed as realistic starter code for the scenario
- Do NOT include `docker-compose.yml`
- Do NOT include `init_database.sql`
- Do NOT include `kill.sh`

## Code file requirements
- Generate a realistic folder structure such as `cmd/`, `internal/`, `pkg/`, and focused packages with clear responsibilities.
- Code should follow Go best practices and demonstrate intermediate-level patterns.
- Use appropriate Go idioms, interfaces, composition patterns, and context-aware APIs where relevant.
- Focus on concurrency-heavy or asynchronous workflows that require careful coordination and safe state management.
- **CRITICAL**: The generated code files should provide partial implementations or intentionally flawed logic that require architectural completion or debugging.
- Include some existing interfaces, structs, utilities, or tests that the candidate needs to work with or extend.
- The core concurrency design, synchronization fixes, cancellation wiring, performance improvements, or error-coordination logic that the candidate needs to implement MUST be left for the candidate to design.
- DO NOT include any `TODO` or placeholder comments.
- DO NOT include comments that give away hints or solutions.
- The generated project structure should be compilable with `go test ./...` or `go build ./...`, even if tests initially fail.
- Prefer standard library concurrency primitives and testing tools that are naturally within intermediate Go scope.
- Include tests that can surface issues such as goroutine leaks, race conditions, incorrect cancellation behavior, incomplete result aggregation, unsafe shared mutation, or deadlock-prone flows when appropriate.
- Make the business scenario concrete and realistic, but keep all execution fully local and deterministic.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Go projects including binary executables, vendor directories, IDE configurations (`.idea/`, `.vscode/`, `.DS_Store`), compiled binaries, coverage files (`*.out`, `*.test`, `coverage.*`), benchmark outputs, profile artifacts, log files, temporary files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections, in this exact order:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

### Task Overview
- This section MUST contain 3-4 meaningful sentences.
- No bullet list in this section.
- Describe the business scenario, current state, and why the problem matters.
- NEVER leave this section empty.
- Use the exact task scenario and domain selected from the real-world scenarios.
- Do NOT include bold time-budget callouts.
- Make the scenario feel authentic to the selected domain and role context.

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- 4-5 bullets maximum.
- Every bullet must start with an action word such as: `Consider`, `Think about`, `Explore`, `Review`, `Analyze`.
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Frame suggestions around outcomes, trade-offs, debugging angles, reliability, and maintainability.
- Good examples of framing:
  - `Consider how work should stop when one part of the system can no longer continue safely.`
  - `Think about where shared state may behave differently under concurrent access than under sequential tests.`
  - `Explore how partial failures should affect the final outcome returned to callers.`
  - `Review whether long-running work can outlive the request that started it.`
  - `Analyze what should remain observable when the system is exercised under higher load.`

### Objectives
- 4-6 bullets maximum.
- Frame objectives around outcomes rather than specific technical implementations.
- Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not a step or a named library/API choice.
- Cover both functional behavior and engineering quality.
- Suitable objective themes for this Go level include:
  - correct and reliable concurrent execution
  - safe handling of shared resources
  - graceful timeout or cancellation behavior
  - clear and debuggable error outcomes
  - maintainable package structure and testability
  - performance behavior that remains reasonable for realistic local workloads

### How to Verify
- 4-6 bullets maximum.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run or observe, such as test results, output shape, timing behavior, race-safety signals, or log behavior.
- Verification should guide candidates to validate:
  - normal success cases
  - failure and timeout paths
  - concurrency safety under repeated runs
  - absence of hangs or leaked work after cancellation
  - stability of behavior for realistic input sizes

### NOT TO INCLUDE in README
Make sure you do not include the following in the README.md file:
- Setup commands (e.g. `npm install`, `pip install`, `docker compose up`, `mvn test`, `go mod tidy`, `go build`, `go test`, `go run`)
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like `you should implement`, `add this middleware`, `create this class`, `use <specific API>`
- Any host, port, username, password, connection string, or client-tool suggestion
- Any `<DROPLET_IP>` placeholder
- Any infrastructure setup details because this task is intentionally local-only

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "Kebab-case GitHub repository name under 50 characters that is short, descriptive, and different from the title.",
  "title": "Human-readable display name in 50-80 characters using an action verb plus subject format, clearly different from the name.",
  "question": "Full candidate-facing task description describing the selected business scenario, the current codebase state, the expected deliverables, and the intermediate-level Go concurrency or architecture challenge to solve.",
  "code_files": {{
    "README.md": "Candidate-facing README content following the exact required section names and order, with concise but meaningful scenario-specific guidance.",
    ".gitignore": "A comprehensive Go project gitignore covering binaries, coverage artifacts, IDE files, logs, profiles, and temporary files.",
    "go.mod": "The Go module definition for the local project, using realistic module naming and only appropriate dependencies for the task.",
    "go.sum": "The dependency checksum file, which may be empty if the chosen project setup does not require additional resolved dependencies.",
    "cmd/app/main.go": "A realistic application entry point that wires together the starter components without containing the full solution.",
    "internal/model/model.go": "Domain models or value objects relevant to the scenario and task behavior.",
    "internal/service/service.go": "Service-layer orchestration or business logic starter code with intentionally incomplete or flawed behavior to be fixed or extended.",
    "internal/engine/engine.go": "Concurrency orchestration, workflow coordination, or processing logic starter code aligned with the scenario.",
    "internal/errors/errors.go": "Custom error types, sentinel errors, or error helpers if they are useful for the scenario.",
    "internal/config/config.go": "Configuration structs or defaults if they are useful for the local project structure.",
    "internal/...": "Additional internal package files needed to create a realistic intermediate Go repository with clear package boundaries.",
    "pkg/...": "Optional exported utility package files if they naturally fit the chosen scenario without giving away the solution.",
    "internal/..._test.go": "Scenario-specific tests using Go's testing package that expose the missing functionality, bug, race-risk, or cancellation behavior without solving it for the candidate."
  }},
  "answer": "Evaluator-facing high-level explanation of the intended solution approach, architectural decisions, concurrency reasoning, and the major issues the candidate is expected to address.",
  "definitions": "An object of term-to-definition pairs covering important Go, concurrency, and scenario-specific terminology that a candidate may encounter in the task.",
  "hints": "A single line nudging investigation toward a strong intermediate-level Go approach without revealing the exact fix, API, or implementation pattern.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable functional correctness, concurrency safety, cancellation behavior, and maintainable code organization. Use simple english.",
  "pre_requisites": "Bullet list of tools and knowledge needed, including Go modules, testing familiarity, debugging skills, and intermediate understanding of concurrency and error handling.",
  "short_overview": "Bullet list summarising the business problem, the technical focus of the task, and the expected outcome in concise, simple language."
}}

## CRITICAL REMINDERS
- Output must be valid JSON only when generating the task definition.
- `name` must be kebab-case and under 50 characters.
- `title` must be human-readable, 50-80 characters, and different from `name`.
- `code_files` must contain a FULLY POPULATED local Go project with meaningful starter code and tests.
- The task must be inspired by exactly one selected real-world scenario from the provided list.
- The task must remain within intermediate Golang scope: core syntax, modules/packages, concurrency, synchronization, error handling, testing, debugging, and performance awareness.
- Do NOT require advanced distributed systems infrastructure, external databases, external queues, Kubernetes, cloud services, or production deployment steps.
- Do NOT include docker-compose, init_database.sql, kill.sh, or other infrastructure bootstrap files.
- Keep the repository local-only and runnable with native Go tooling.
- The question must NOT include hints.
- The README must use the exact section names and order specified above.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
"""

PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE)": [
        PROMPT_GOLANG_INTERMEDIATE_CONTEXT,
        PROMPT_GOLANG_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_GOLANG_INTERMEDIATE_INSTRUCTIONS,
    ]
}