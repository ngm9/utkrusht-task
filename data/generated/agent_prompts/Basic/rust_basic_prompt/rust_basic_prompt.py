PROMPT_RUST_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

You are generating a Rust assessment for the following competency set:
{competencies}

Before creating the task, briefly summarize your understanding of the company,
the role expectations, and the kind of Rust work that would be realistic for a
BASIC-level engineer in this setting.
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

ADDITIONAL QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- Generate a PURE_CODE Rust task only: source files plus Cargo metadata and
  README, with no Docker, no database, and no web framework.
- The task must fit BASIC proficiency: a well-scoped feature or bug fix
  combining 2-3 Rust concepts, completable within {minutes_range} minutes.
- Keep the task grounded in realistic day-to-day Rust work such as parsing,
  validation, ownership fixes, enum-driven logic, Result/Option handling,
  iterators, module organization, or small unit tests.
- Prefer an existing-code scenario where the candidate must fix or complete
  starter code rather than build a project from scratch.
- Stay within BASIC scope: no unsafe code, no advanced architecture, no
  microservices, no security hardening, and no heavy system design.
- If you use concurrency or async at all, keep it minimal and incidental rather
  than the primary challenge.
- Pick one scenario and keep the domain practical and business-oriented.

Briefly confirm your plan before producing the final task:
1. What business/domain scenario will you use?
2. What is the current buggy or incomplete behavior?
3. Which 2-3 Rust skills will the candidate need to apply?
4. Why is this appropriately scoped for BASIC level?
"""

PROMPT_RUST_BASIC_INSTRUCTIONS = """
# Rust BASIC Task Generation Instructions

## GOAL
As a technical architect, generate a complete Rust assessment task for a
candidate with BASIC proficiency. The task must assess applied Rust ability in a
small, realistic codebase and should be solvable within {minutes_range} minutes.

## SCOPE AND DIFFICULTY
Design a task that uses only BASIC-level Rust concepts naturally supported by
the competency scope, such as:
- idiomatic functions and modules
- structs and enums
- pattern matching with `match` or `if let`
- ownership and borrowing in straightforward code
- `String` and `&str`
- standard collections where useful
- `Option` and `Result`
- error propagation with `?`
- simple custom error types
- iterators and basic transformations
- derived traits like `Debug`, `Clone`, or `PartialEq`
- unit tests

Do NOT make the task primarily about:
- unsafe code
- advanced lifetime design
- complex trait systems
- system design or architecture-heavy decisions
- advanced concurrency patterns
- performance tuning as the main challenge
- framework setup trivia
- Cargo command memorization

## TASK SHAPE
The task should feel like a realistic bug fix or feature completion in an
existing Rust utility or library. Good examples include:
- replacing panic-based parsing with `Result`
- fixing an ownership/borrowing issue without unnecessary cloning
- validating input and modeling failures with enums
- improving enum-based control flow
- completing a small transformation pipeline using iterators
- organizing a small module boundary cleanly

The candidate should need to combine about 2-3 concepts, not just fix syntax.

## REQUIRED REPOSITORY SHAPE FOR PURE_CODE
Because this is a PURE_CODE task, the generated `code_files` should contain only
source code and standard project files. Do not include Docker, databases, or
service infrastructure.

Include files such as:
- `README.md`
- `.gitignore`
- `Cargo.toml`
- `src/lib.rs` or `src/main.rs`
- one or more additional Rust source files if needed
- optionally `tests/...` for integration tests if appropriate

## STARTER CODE RULES
- The starter code must compile or be very close to compiling with a clear,
  intentional implementation gap that the candidate is expected to fix.
- Prefer runnable starter code with failing tests or incomplete behavior over
  broken scaffolding.
- The starter code must reflect exactly the "Current Implementation" described
  in the task.
- Do not include the final solution in comments, TODOs, or hidden helpers.
- Do not make environment setup the challenge.
- Keep dependencies minimal and justified. If using crates such as `serde` or
  `serde_json`, use them only in a straightforward, established way.

## CANDIDATE-FACING QUESTION REQUIREMENTS
The `question` field must be a complete candidate-facing task description and
MUST include:
1. A short business scenario.
2. A "Current Implementation" section describing the exact current behavior of
   the provided starter code.
3. A "Required Changes" section listing the specific implementation work.
4. Clear constraints and expectations.
5. How the candidate can verify success.

The task should be concrete enough that an evaluator can compare the candidate's
changes against the intended outcome.

## REQUIRED OUTPUT JSON STRUCTURE
Return exactly one JSON object using these exact top-level keys and no
synonyms:

{{
  "name": "short-kebab-case-task-name",
  "question": "Full candidate-facing task description",
  "code_files": {{
    "README.md": "Full README contents",
    ".gitignore": "Git ignore contents",
    "Cargo.toml": "Cargo manifest contents",
    "src/lib.rs": "Rust source contents"
  }},
  "answer": {{
    "summary": "Evaluator-facing high-level solution summary",
    "key_points": [
      "Important implementation expectation 1",
      "Important implementation expectation 2"
    ]
  }},
  "definitions": {{
    "term_1": "definition",
    "term_2": "definition"
  }},
  "hints": "A brief nudge that helps without revealing the answer.",
  "outcomes": "Bullet list of expected observable outcomes after completion.",
  "pre_requisites": "Bullet list of tools and knowledge required.",
  "short_overview": "Bullet list summarizing the scenario, task, and expected result."
}}

Use the canonical key names exactly:
- `name`
- `question`
- `code_files`
- `answer`
- `definitions`
- `hints`
- `outcomes`
- `pre_requisites`
- `short_overview`

Do not use alternatives like `title`, `task_title`, `files`,
`repository_structure`, or `acceptance_criteria`.

## README REQUIREMENTS
The `README.md` inside `code_files` must contain these sections with specific,
task-relevant content:
- `# Task Overview`
- `## Objectives`
- `## How to Verify`
- `## Helpful Tips`

## QUALITY BAR
The generated task should:
- feel like work a BASIC Rust engineer would actually receive
- reward safe, idiomatic Rust choices
- encourage use of `Result`/`Option`, enums, borrowing, and clear control flow
- avoid unnecessary cloning and panic-driven logic
- be understandable without extra verbal explanation
- be solvable in {minutes_range} minutes

## FINAL REMINDERS
1. Output only the JSON object.
2. Ensure all file contents are complete and internally consistent.
3. Keep the task within BASIC Rust scope.
4. For PURE_CODE, do not include Docker, databases, or web servers.
5. Make the starter code realistic, incomplete, and non-solution-revealing.
"""

PROMPT_REGISTRY = {
    "Rust (BASIC)": [
        PROMPT_RUST_BASIC_CONTEXT,
        PROMPT_RUST_BASIC_INPUT_AND_ASK,
        PROMPT_RUST_BASIC_INSTRUCTIONS,
    ]
}