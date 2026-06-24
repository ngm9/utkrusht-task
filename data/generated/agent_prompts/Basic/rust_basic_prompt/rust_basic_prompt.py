# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""Rust BASIC prompt registry entry.

This prompt generates pure local Cargo-based Rust assessment tasks for BASIC
proficiency candidates.
"""

PROMPT_RUST_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_RUST_BASIC_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a BASIC Rust assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL QUESTION CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must be a small, realistic Rust feature or bug fix combining 2-3 BASIC concepts.
- It must be completable within {minutes_range} minutes by a candidate with roughly 1 year of Rust experience.
- Prefer applied engineering work over syntax recall: ownership fixes, enum modeling, Result/Option handling, collection transformations, small module boundaries, or unit-test-backed behavior changes.
- The task must be a pure local Cargo project. Do not require external services, databases, containers, network setup, or cloud resources.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match BASIC Rust level?
3. Which 2-3 Rust concepts will be assessed without exceeding the BASIC proficiency boundary?
"""

PROMPT_RUST_BASIC_INSTRUCTIONS = """
# BASIC Task Requirements (Rust)

## GOAL
As a technical architect super experienced in Rust, you are given a list of real world scenarios and proficiency levels for Rust. Generate a complete assessment task — description, starter code files, README — that tests a candidate at BASIC proficiency (roughly 1 year of Rust experience). The task must be a well-scoped feature or bug fix combining 2-3 practical Rust concepts.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to work in an existing Rust codebase and complete a small, realistic change. They should be comfortable with Cargo, modules, structs, enums, pattern matching, Result and Option, references and mutable references, standard collections, strings, iterators, and unit tests.

The candidate is NOT expected to design large systems, build services from scratch, perform advanced lifetime engineering, use unsafe code, implement complex async orchestration, tune low-level performance, or introduce infrastructure. The task should evaluate applied competence, practical problem-solving, and the ability to improve existing Rust code safely and idiomatically.

## INSTRUCTIONS
- Generate a FULLY FUNCTIONAL local Rust project that runs with Cargo.
- The task asks the candidate to implement a feature or fix a bug in existing starter code. Focus on 2-3 concepts such as:
  - using structs and enums to model domain state,
  - replacing fragile string logic with pattern matching,
  - changing an API from owned values to borrowed references,
  - handling errors with Result or Option instead of unwrap, panic, or silent fallback,
  - using Vec, HashMap, HashSet, slices, String, &str, or iterators appropriately,
  - organizing a small library module and adding unit tests.
- Generate enough starter code to give a clear starting point WITHOUT giving away the solution.
- The starter code MUST run cleanly (zero syntax errors, zero compilation errors) before the candidate changes it.
- The starter code MUST implement exactly the "Current Implementation" buggy or incomplete state described in the question.
- Do NOT include the solution, TODO comments, solution-revealing comments, or hidden implementation guidance in the starter code.
- The candidate should be able to run the initial project and see tests that describe the desired behavior. It is acceptable for one or more tests to fail before the candidate completes the task, but the project must compile.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- For executable commands, always use explicit runtime commands such as `cargo test`, `cargo fmt`, and `cargo clippy`.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### Nature of the Task
- **CRITICAL**: This is BASIC Rust. Keep the task narrow and practical. The candidate should modify a small number of files and reason about ordinary compiler feedback, ownership, enums, matching, collections, or error handling.
- **CRITICAL**: The candidate should not need advanced production experience. Do not require complex lifetimes, unsafe Rust, macros, FFI, custom allocators, advanced trait-object architecture, complex async runtime behavior, lock-free concurrency, or sophisticated performance profiling.
- **CRITICAL**: The task must remain an applied engineering exercise, not a quiz about Rust terminology, Cargo command memorization, edition trivia, or isolated syntax facts.
- Prefer a scenario where the current implementation is plausible but flawed: raw string statuses, silently ignored invalid input, overuse of unwrap, unnecessary moves that prevent later use, counting logic that includes excluded records, or a small API that should return Result.
- Keep the starter code small enough for a BASIC candidate to understand quickly. A good shape is:
  - one Cargo manifest,
  - one library entry file,
  - one domain module,
  - one integration or unit test file,
  - README and .gitignore.
- The assessment should test that the candidate can read existing Rust code, make a safe local change, and verify behavior with tests.
- Do not turn the task into dependency management. Third-party crates may be used only when directly useful and already represented in the starter project. For most BASIC tasks, prefer the Rust standard library only.
- Do not require external network calls, credentials, background services, containers, databases, queues, caches, browsers, or cloud resources.
- The task must be FULLY FUNCTIONAL and self-contained as a local Rust project.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Rust documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The assessment is designed to evaluate the candidate's ability to:
- understand requirements and constraints,
- use resources effectively to solve realistic engineering problems,
- reason about Rust compiler feedback and safe implementation choices,
- deliver working, maintainable code within the expected time.

Candidates should not be penalized for using external references, provided the submitted work satisfies the task requirements and demonstrates understanding.

## Code Generation Instructions
The generated project must be a pure local Rust project using Cargo.

Required project characteristics:
- Include a `Cargo.toml` manifest.
- Include source files under `src/`.
- Include tests either inside `src/` modules with `#[cfg(test)]` or under `tests/`.
- The initial code must compile with `cargo test`, even if one or more behavioral tests fail before the candidate completes the task.
- Keep dependencies minimal. If dependencies are included, they must be ordinary Cargo dependencies and must not require system services.
- Use Rust 2021 edition unless the scenario explicitly requires another stable edition.
- Avoid unstable features and nightly-only APIs.
- Avoid unsafe code entirely.
- Avoid starter comments that reveal the implementation path. The README may describe the required outcomes, but source files should look like normal incomplete or buggy production-like code.

The generated starter code should create a meaningful gap between current behavior and desired behavior. Examples of appropriate BASIC Rust task shapes include:
- a function that consumes a value when it should borrow it,
- a raw string field that should be modeled as an enum,
- a parser that uses unwrap where it should return Result,
- a summary function that counts the wrong records,
- a module that exposes too much mutable state and needs a small public method,
- a collection transformation that should avoid unnecessary cloning while remaining readable.

## Infrastructure Requirements
This is a non-infrastructure task. The output must be a local Rust project only.

Do not include external service configuration, datastore setup, container orchestration, database initialization scripts, service health checks, credentials, ports, or environment files. The candidate must be able to complete and verify the task using the Rust toolchain and Cargo commands only.

The project should be runnable from `/root/task` with the runtime's native command:
- `cargo test`

The generated files must not require network services, databases, queues, caches, search engines, object stores, or message brokers.

The output should be a valid json schema:
- `Cargo.toml`: Rust package manifest for the local assessment project.
- `src/lib.rs`: Library entry point that exposes the module or functions under assessment.
- `src/<module>.rs`: Domain module containing the starter implementation that the candidate will modify.
- `tests/<behavior>_test.rs` or inline unit tests: Behavioral tests that verify the expected outcome.
- `README.md`: Candidate-facing instructions using the required README sections.
- `.gitignore`: Standard Rust exclusions.

## Code file requirements
- All files must be placed under `/root/task` paths in the generated JSON.
- The project must compile in its initial state.
- The starter code must be intentionally incomplete or behaviorally wrong in a way that matches the task question.
- Keep the implementation small and readable. Avoid sprawling examples, large fixtures, or unrelated boilerplate.
- Use idiomatic Rust names and module organization.
- Avoid `unsafe`.
- Avoid broad use of `unwrap`, `expect`, or `panic!` in production-like paths unless the task is specifically asking the candidate to remove or replace them.
- Tests may use assertions freely.
- Do not include solution comments such as "replace this with an enum", "use match here", or "return Result here".
- Include enough tests to make the expected behavior clear, but avoid overconstraining the implementation. For BASIC tasks, 2-4 focused tests are usually sufficient.
- The files should represent a realistic existing codebase, not a puzzle or toy syntax drill.
- If the task involves JSON or serialization, include only simple static data and keep parsing expectations straightforward.
- If the task involves concurrency or async, keep it very small and basic. Do not require complex synchronization, advanced Send/Sync reasoning, or multi-step async orchestration for BASIC proficiency.

## .gitignore INSTRUCTIONS
The `.gitignore` file must be appropriate for a Rust Cargo project and should include standard generated artifacts such as:
- `/target/`
- `Cargo.lock` only if the generated project is intended to behave like a library template; otherwise include or exclude it consistently with the project type
- editor and OS noise such as `.DS_Store`, `.idea/`, and `.vscode/`
- temporary logs or local scratch files

Do not include exclusions for datastore files, container volumes, service credentials, or infrastructure artifacts because this is a pure local Rust task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md entry inside code_files MUST contain exactly these sections, in this order, and no others:

### Task Overview
- 3-4 meaningful sentences.
- No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Do not mention setup commands, dependency installation, container commands, datastore access, hostnames, ports, usernames, passwords, or client-tool suggestions.

### Helpful Tips
- 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not give away the exact enum names, method names, trait bounds, collection APIs, or error conversion strategy.

### Objectives
- 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet states an observable end-state, not a step or an API/library to use.
- Objectives should be specific enough to verify completion but not so specific that they reveal the exact solution.

### How to Verify
- 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, response shape, error behavior, log line, or memory/ownership-related behavior.
- For this Rust project, verification should be based on local Cargo behavior and observable tests.
- Do not include container, database, service, or network verification.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README content:
- Setup commands such as `cargo build`, `cargo test`, dependency installation commands, container commands, or operating system package installation.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this enum", "create this method", "use match", "use HashMap::entry", or "return Result".
- Any heading named "NOT TO INCLUDE", "CONTENT TO EXCLUDE", "Database Schema Overview", "Database Access", or "Performance Issues".
- Any database-connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or `<DROPLET_IP>` placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as `task_title`, `files`, `context`, or `solution`. Synonyms produce a hollow, unusable task.

The output should be valid JSON with the following exact keys. Each value below describes what to fill in:

{{
  "name": "A short kebab-case GitHub repository name under 50 characters that reflects the Rust task domain and does not duplicate the display title.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name.",
  "question": "The full candidate-facing task description including the business scenario, the Current Implementation, the Required Changes, and clear success criteria without revealing the solution.",
  "code_files": {{
    "Cargo.toml": "The complete Cargo manifest for a self-contained local Rust project using the stable toolchain and minimal dependencies.",
    "src/lib.rs": "The complete Rust library entry file exposing only the modules and public items needed by the task.",
    "src/<domain_module>.rs": "The complete starter Rust module containing the intentionally incomplete or flawed implementation that compiles and matches the Current Implementation.",
    "tests/<behavior>_test.rs": "The complete behavioral test file, when integration tests are useful, with focused assertions describing the expected candidate-visible outcomes.",
    "README.md": "The concise candidate-facing README containing exactly Task Overview, Helpful Tips, Objectives, and How to Verify in that order.",
    ".gitignore": "The complete Rust-appropriate ignore file for generated Cargo artifacts, editor files, OS noise, and local temporary files."
  }},
  "answer": "Evaluator-facing high-level solution approach explaining the expected Rust changes, important ownership or error-handling reasoning, and the behavior that should pass after completion.",
  "definitions": "An object mapping Rust or domain terms used in the task to concise definitions that help evaluators understand the assessment focus.",
  "hints": "A single line hint nudging the candidate toward the right investigation area without naming the exact implementation, API, enum, method, or collection operation to use.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable behavior, passing tests, safe ownership, and idiomatic Rust error or data handling. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, such as stable Rust, Cargo, reading compiler messages, basic ownership, structs, enums, Result or Option, collections, and unit tests.",
  "short_overview": "A bullet list summarising the business problem, the Rust technical focus, and the expected observable outcome after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. The environment must be FULLY FUNCTIONAL out of the box; the candidate fixes the task, not the environment.
2. This is a pure local Rust project; do not include external services, datastore configuration, container configuration, service credentials, host ports, or cloud dependencies.
3. Starter code must compile before the candidate begins.
4. Starter code must perfectly match the "Current Implementation" described in the question.
5. Do not include the solution, TODO comments, or solution-revealing source comments.
6. Keep the task BASIC: 2-3 Rust concepts, small file count, practical bug fix or feature, completable within {minutes_range} minutes.
7. Use the canonical output JSON key names exactly.
8. The README must contain exactly Task Overview, Helpful Tips, Objectives, and How to Verify, in that order, and no extra sections.
9. The task must assess applied Rust ability, not trivia, installation, infrastructure, or memorized commands.
"""

PROMPT_REGISTRY = {
    "Rust (BASIC)": [
        PROMPT_RUST_BASIC_CONTEXT,
        PROMPT_RUST_BASIC_INPUT_AND_ASK,
        PROMPT_RUST_BASIC_INSTRUCTIONS,
    ]
}