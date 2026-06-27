# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


"""Rust intermediate prompt.

Generates infra-shaped Rust assessment tasks using the canonical prompt
blueprint.
"""

PROMPT_RUST_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_RUST_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a INTERMEDIATE Rust assessment task.

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
- The task must be a realistic Rust work item involving a small service, repository, or data-processing component backed by PostgreSQL.
- The task must test intermediate Rust judgement: ownership and borrowing, domain types, collections, Result-based error handling, async database access, module boundaries, and focused tests.
- The task must be completable within {minutes_range} minutes by a candidate with 3-5 years of Rust experience.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match INTERMEDIATE Rust level?
3. Which PostgreSQL-backed workflow will be provided in the starter project, and what will remain incomplete for the candidate?
"""

PROMPT_RUST_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements (Rust)

## GOAL
As a technical architect super experienced in Rust, you are given a list of real world scenarios and proficiency levels for Rust. Generate a complete assessment task — description, starter Rust project, PostgreSQL infrastructure, README — that tests a candidate at INTERMEDIATE proficiency with 3-5 years of experience.

The generated task must be a practical Rust work item that asks the candidate to fix, refactor, or complete an existing code path. It must exercise idiomatic Rust, ownership-aware design, clear error handling, async database interaction, collection choice, module organization, and testing discipline without becoming an expert-level distributed-systems exercise.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate Rust developer expected to independently work in a medium-sized Rust codebase. They should be comfortable with Cargo, modules, structs, enums, traits, generics where useful, `Result` and `Option`, custom errors, iterator and collection usage, async runtimes such as Tokio, and database-facing code through ordinary Rust crate APIs.

The task should feel like a real production maintenance item: a current implementation is present, the environment is FULLY FUNCTIONAL, and the database is FULLY POPULATED with enough seed data to demonstrate the problem. The candidate should focus on the Rust task, not on fixing setup, dependency installation, schema wiring, or container startup.

## INSTRUCTIONS
- Generate a Rust assessment task based on ONE selected real-world scenario.
- The starter code must compile before the candidate begins and must represent the exact current buggy or incomplete implementation described in the question.
- The candidate should need to reason about 4-5 intermediate Rust concepts such as ownership, borrowing, collections, async boundaries, error propagation, typed domain models, trait-based abstractions, repository boundaries, structured logging, and tests.
- Keep the scope realistic for {minutes_range} minutes. Prefer one coherent service path or library workflow over many unrelated features.
- The task may ask candidates to improve correctness, performance, or reliability, but it must remain centered on Rust implementation rather than SQL trivia or Docker setup.
- Do NOT require expert-only unsafe Rust, advanced FFI, complex lifetime-heavy APIs, distributed consensus, service mesh design, macro authoring, or full observability platform integration.
- Do NOT include the solution, TODO comments, step-by-step hints, or solution-revealing comments in the starter Rust code.
- The question must clearly describe the Current Implementation and Required Changes, while leaving implementation decisions to the candidate.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- For executable code, always invoke tools by their explicit command name, such as `cargo`, `bash`, and `docker compose`.

### Nature of the Task
- **CRITICAL**: This is an INTERMEDIATE Rust task for a candidate with 3-5 years of experience. It should require judgement and implementation skill, not memorization.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL and must compile as provided. The missing behavior should be validated by tests or observable outputs after the candidate completes the work.
- **CRITICAL**: The PostgreSQL database must be FULLY POPULATED by init SQL so that the candidate can run the project locally without creating data by hand.
- **CRITICAL**: The core assessment should come from Rust code, not from Docker, shell scripting, or manual database administration.
- Good task themes include aggregating duplicate domain records before database writes, moving filtering from in-memory Rust code into a repository query while preserving Rust error semantics, or fixing an async/concurrent workflow that currently has poor ownership or error handling.
- The candidate may need to choose appropriate collections such as `HashMap`, `BTreeMap`, `Vec`, or sets, model domain errors with enums, use `?` for propagation, avoid unnecessary cloning, keep locks or borrows out of `.await` boundaries, and organize code into small modules.
- The task should have multiple reasonable implementation paths, but the expected outcome must be specific and measurable.
- Include focused visible tests or integration tests that describe the desired behavior without revealing the full implementation.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Rust documentation, PostgreSQL documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The assessment evaluates the candidate's ability to understand requirements, make appropriate technical decisions, validate behavior, and deliver working Rust code.
- External resources may be used for syntax, library usage, documentation lookup, debugging, and general guidance.
- The candidate remains responsible for the correctness, maintainability, and safety of the submitted solution.
- The task should not depend on hidden trivia or memorized commands that would unfairly penalize normal use of documentation.

## Rust Code Generation Instructions
- Generate a complete Cargo project under /root/task.
- Include `Cargo.toml`, `Cargo.lock` if appropriate, `src/lib.rs` or `src/main.rs`, supporting module files, and tests.
- Use stable Rust edition 2021 or newer.
- Choose a minimal, common dependency set suitable for the task, such as Tokio, SQLx or an equivalent PostgreSQL crate, Serde where serialization is needed, thiserror or anyhow where appropriate, tracing where diagnostics are useful, and a small test helper if needed.
- The primary runtime itself is already installed. Do NOT install Rust with apt-get, curlup, rustup, or system package managers.
- The task's third-party crates are not pre-installed, so the readiness script must fetch/build dependencies through Cargo.
- Starter code must compile on the unsolved task. Behavioral tests may fail until the candidate completes the work, but compile errors must not be present.
- Keep the public API small and clear. Favor type-driven Rust models over unstructured strings or maps.
- Use `Result` and custom domain errors for recoverable failures. Avoid `unwrap`, `expect`, and panics in production paths unless the task explicitly asks the candidate to remove them.
- Use async Rust only where it is part of the scenario. Do not introduce unnecessary concurrency just to make the task harder.
- If concurrency is included, keep it bounded and understandable for an intermediate candidate.
- Avoid solution-revealing comments. Comments may explain domain context or why a starter limitation exists, but must not tell candidates exactly what to write.
- Include enough seed data, fixtures, and tests for the task to be self-contained.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## Infrastructure Requirements
This is an infra-shaped Rust task. You MUST include PostgreSQL infrastructure because the scenario exercises database-backed behavior.

- Include `docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`.
- The PostgreSQL service must be the only datastore unless the selected scenario explicitly requires another external service.
- Do not invent Redis, MySQL, queues, search engines, or brokers if the selected scenario does not require them.
- The app itself does not need to run in Docker. The candidate should work in a local Rust Cargo project that connects to the PostgreSQL container.
- The run script is a READINESS/self-check only. It must bring PostgreSQL up, wait for health, verify that the starter project loads and compiles, and exit 0 on the unsolved starter.
- The run script MUST NOT run the grader test suite or any tests that are intentionally designed to fail until the candidate solves the task.

### Docker-compose Instructions
- Create `docker-compose.yml` in /root/task.
- **MUST NOT include any version specification** in docker-compose.
- Define a PostgreSQL service using an official postgres image.
- For PostgreSQL, REQUIRE the standard init environment variables inline in `environment:`:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- Do not use `.env` files or host-variable interpolation for required database initialization values. Inline service environment values are required because the image will not initialize without them.
- The init SQL, healthcheck, and Rust connection string must use the same user and database.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`.
- Mount `./init_database.sql` into the PostgreSQL container's initialization directory.
- Add a robust PostgreSQL healthcheck using `pg_isready` with the same database user and database name.
- Use a named Docker volume for PostgreSQL data.
- Keep service names simple and stable, such as `postgres`.
- Do not include an app container unless the scenario absolutely requires it; for this Rust task, prefer local Cargo execution.

### init_database.sql Instructions
- Create `init_database.sql` in /root/task.
- The SQL must be complete, idempotent enough for fresh container initialization, and aligned with the selected scenario.
- Include all required tables, indexes, constraints, and seed data needed for the starter code and tests.
- Seed enough rows to demonstrate the current implementation problem without making setup slow.
- Use realistic domain names and values from the selected scenario.
- If the task is about query performance, include the missing or incomplete index state in a way that lets the candidate add or adjust a migration-like SQL file or Rust-side repository query as part of the task.
- Do not place database host, port, username, or password details in the README.

### Run.sh Instructions
- Create `run.sh` in /root/task and make it executable.
- The first step must install or fetch the task's Rust dependencies through Cargo, such as `cargo fetch`.
- Start infrastructure using `docker compose up -d`.
- Wait for PostgreSQL to become healthy before running any Rust checks.
- Print clear progress logs at every step.
- Apply or rely on `init_database.sql` during container initialization. Do not require manual SQL execution by the candidate.
- Verify that the Rust starter project compiles with a command such as `cargo build --all-targets`.
- Optionally use `cargo test --no-run` to compile tests without executing failing assertions.
- Do NOT run `cargo test` if the visible tests are expected to fail before the candidate completes the task.
- The script must exit 0 when the unsolved starter environment is healthy and compiles.
- Use /root/task as the working directory.

## kill.sh file instructions
Create a `kill.sh` script in /root/task that performs complete cleanup for the task environment. The script must be idempotent and safe to run multiple times.

1. Print a clear message that cleanup is starting.
2. Change to /root/task if it exists; otherwise continue cleanup without failing.
3. Stop Docker containers with `docker compose down` and include `|| true` so the script remains idempotent.
4. Remove task-specific Docker volumes with `docker volume rm` or `docker compose down -v`, using `|| true`.
5. Remove task-specific Docker networks with `docker network rm` where applicable, using `|| true`.
6. Force-remove task-specific Docker images if any were built, using `docker rmi -f` and `|| true`.
7. Run `docker system prune -a --volumes -f` as a final Docker cleanup step.
8. Remove the task directory with `rm -rf /root/task` and use `|| true`.
9. Print logs at every step and end with the exact final message `Cleanup completed successfully!`.

The script must not fail if containers, volumes, networks, images, or /root/task are already absent.

The output should be a valid json schema:
- `README.md`: concise candidate-facing instructions with exactly the sections specified below.
- `.gitignore`: Rust, Cargo, editor, environment, and generated artifact exclusions.
- `Cargo.toml`: native Rust package manifest with required dependencies and test configuration.
- `src/lib.rs` or `src/main.rs`: starter Rust entry point or library root.
- `src/*.rs`: supporting modules for domain models, repository code, service logic, errors, and configuration.
- `tests/*.rs`: focused visible tests or integration tests that compile against the starter project.
- `docker-compose.yml`: PostgreSQL service definition with localhost-only port binding and no version field.
- `init_database.sql`: complete schema and seed data for the selected scenario.
- `run.sh`: readiness script that starts PostgreSQL and verifies the unsolved starter compiles.
- `kill.sh`: full cleanup script following the required 9-step shape.

## Code file requirements
- Every file in `code_files` must contain complete file contents, not fragments.
- All files must be placed under /root/task-relative paths.
- The generated Rust code must compile as provided.
- The starter implementation must intentionally contain the current incomplete or inefficient behavior described in the task.
- Tests should be specific enough to validate the desired end state but should not encode a single overly narrow implementation.
- Use deterministic seed data and deterministic tests where possible.
- Do not include hidden setup steps that are missing from the files.
- Do not include placeholders such as "fill this in", "your code here", or incomplete snippets.
- Do not include TODO comments in starter code.
- Keep the file count appropriate for a {minutes_range}-minute task: enough structure to feel realistic, not a full production service.
- Prefer readable Rust over clever abstractions. The candidate should be assessed on practical maintainability.

## .gitignore INSTRUCTIONS
The `.gitignore` file must be appropriate for a Rust Cargo project with Docker-backed local infrastructure.

Include exclusions for:
- `target/`
- local environment files such as `.env`
- editor and OS files
- logs and temporary files
- generated coverage or profiling output if included
- local database artifacts that should not be committed

Do not ignore source files, tests, Cargo manifest files, SQL files, Docker compose files, or scripts required for the assessment.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The `README.md` entry inside `code_files` MUST contain exactly these output sections, in this order, and no others:

### Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Do not include setup commands, database credentials, hostnames, ports, usernames, passwords, or client-tool suggestions.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not include direct commands or step-by-step implementation instructions.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should be measurable from tests, behavior, logs, or response data.
- Do not tell the candidate exactly which Rust type, crate API, SQL clause, or algorithm to use.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, response shape, latency observation, log line, or returned error behavior.
- Keep verification concise and task-specific.
- Do not include database connection details, usernames, passwords, hostnames, ports, or client-tool suggestions.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following out of the README entirely:
- Setup commands such as `cargo build`, `cargo test`, `docker compose up`, `npm install`, `pip install`, or similar.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use a specific API".
- Database-connection details including host, port, username, password, database name, or client-tool suggestions.
- Any heading named "NOT TO INCLUDE", "Do Not Include", "Database Schema Overview", "Database Access", or "Performance Issues".
- `<DROPLET_IP>` placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, or `context` because synonyms produce a hollow, unusable task.

Each field's value below is a description of what to fill in. In your final answer, produce valid JSON using exactly these keys:

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the Rust task domain without exposing the solution.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from the repository name.",
  "question": "The full candidate-facing task description including the selected business scenario, the Current Implementation, the Required Changes, constraints, and expected observable behavior without including the hidden solution.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content with exactly Task Overview, Helpful Tips, Objectives, and How to Verify sections in that order.",
    ".gitignore": "The complete Rust and local-development gitignore file content for generated artifacts, local environment files, editor files, logs, and temporary files.",
    "Cargo.toml": "The complete Cargo manifest content with package metadata and the minimal dependency set needed for the starter project.",
    "src/lib.rs": "The complete Rust library root or module declaration file that exposes the starter task API and compiles before candidate changes.",
    "src/main.rs": "The complete optional Rust executable entry point if the scenario benefits from a runnable command, otherwise omit this key.",
    "src/domain.rs": "The complete Rust domain model file using structs, enums, and typed values appropriate to the selected scenario.",
    "src/errors.rs": "The complete Rust error model file containing starter error types and conversions appropriate for recoverable task failures.",
    "src/repository.rs": "The complete Rust repository or database access starter file that connects the service logic to PostgreSQL.",
    "src/service.rs": "The complete Rust service logic starter file containing the current incomplete or inefficient implementation the candidate must improve.",
    "tests/integration.rs": "The complete visible integration or behavior test file that compiles against the starter and validates the expected outcomes after completion.",
    "docker-compose.yml": "The complete PostgreSQL docker-compose configuration with no version field, localhost-only port binding, inline initialization environment values, healthcheck, and named volume.",
    "init_database.sql": "The complete PostgreSQL schema and seed data file aligned with the selected scenario and starter tests.",
    "run.sh": "The complete executable readiness script that fetches Rust dependencies, starts PostgreSQL, waits for health, verifies the starter compiles, and exits successfully without running failing grader tests.",
    "kill.sh": "The complete executable cleanup script that idempotently stops containers, removes volumes, removes networks, force-removes images when applicable, prunes Docker, deletes /root/task, logs each step, and prints the required final success message."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended Rust design, data flow, error handling, database interaction, and tests without being shown to the candidate.",
  "definitions": "An object mapping Rust, PostgreSQL, async, domain, and task-specific terms to concise definitions that help evaluators interpret the task.",
  "hints": "A single line nudging investigation toward the important Rust design or correctness issue without revealing the specific fix, API, type, collection, or query.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable correctness, reliability, performance, and maintainability improvements. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Rust and Cargo familiarity, basic async Rust, Result-based error handling, and local Docker availability for PostgreSQL.",
  "short_overview": "A bullet list summarising the business problem, the Rust technical focus, and the expected observable outcome after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. The environment must run perfectly out of the box; the candidate fixes the Rust task, not the setup.
2. Because this is an infra-shaped task, include PostgreSQL `docker-compose.yml`, `init_database.sql`, `run.sh`, and `kill.sh`.
3. `run.sh` is a readiness check only and MUST NOT run failing grader tests.
4. PostgreSQL ports must be bound to localhost only with `127.0.0.1:5432:5432`.
5. docker-compose MUST NOT include any version specification.
6. PostgreSQL initialization values must be inline in the service `environment:` and must match the init SQL, healthcheck, and Rust connection configuration.
7. Starter Rust code must compile cleanly and must exactly match the Current Implementation described in the question.
8. Do not include the solution, TODO comments, solution-revealing README guidance, or step-by-step implementation instructions.
9. Keep the task within {minutes_range} minutes for an intermediate Rust candidate.
10. Output JSON uses the canonical key names exactly: `name`, `title`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, and `short_overview`.
"""

PROMPT_REGISTRY = {
    "Rust (INTERMEDIATE)": [
        PROMPT_RUST_INTERMEDIATE_CONTEXT,
        PROMPT_RUST_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_RUST_INTERMEDIATE_INSTRUCTIONS,
    ]
}