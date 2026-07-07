# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


# task_generation_prompts/Basic/context_engineering_basic_sports_ticket_context_prompt.py
#
# CURATED task-generation prompt module for Context Engineering BUILD-IT tasks.
# Competency: "Context Engineering"  ·  Proficiency: BASIC
#
# Contract:
#   * Export a top-level dict named exactly PROMPT_REGISTRY.
#   * Key it exactly "Context Engineering (BASIC)".
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal {placeholders} are:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.

PROMPT_CONTEXT_ENGINEERING_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Target Competencies:
{competencies}

Use this context only to gauge who is hiring, the expected candidate level, and the kind of engineering judgment being assessed. The employer's industry is not necessarily the task domain. The assessment task domain for this run is a sports ticketing API context propagation bug.
"""

PROMPT_CONTEXT_ENGINEERING_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Context Engineering assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

{question_prompt}

AUTHORITATIVE SCENARIO FOR THIS TASK:
You MUST build the assessment around this sports ticketing API scenario:

Current implementation:
- In a sports ticketing API, `RequestContext.data = {{}}` is defined as a class attribute.
- `POST /tickets/hold` sets `request_id` and `fan_id` on that shared data dict before calling `reserve_seat(section, row, seat)`.
- Two sequential requests in tests can share the previous fan's context, causing the wrong `fan_id` or `request_id` to appear in hold logs.

Required candidate work:
- Move context storage into `RequestContext.__init__()` so each request gets its own dict.
- Pass the context instance into `reserve_seat()` and `write_hold_log("hold_logs.json", ctx)`.
- Add one unit test proving two contexts do not share `fan_id`.

Success criteria:
- Holding seats for different fans writes separate log entries with the correct `request_id` and `fan_id`.
- No context value leaks between `RequestContext` instances.
- The fix is small, targeted, and does not rewrite unrelated ticketing behavior.

WHAT THIS TASK TESTS:
- Ability to identify shared mutable context as a context leakage bug.
- Ability to propagate request context through function calls rather than relying on global or class-level state.
- Ability to keep request metadata such as `request_id` and `fan_id` isolated per request.
- Ability to verify context isolation with a focused unit test.
- Basic understanding of context-aware logging for traceability and debugging.

CRITICAL TASK GENERATION REQUIREMENTS:
- Use the sports ticketing API scenario above as the direct basis for the generated task.
- Do not invent a different domain.
- Keep the project lightweight, local, and runnable with Python tests.
- Do not require any external services, databases, queues, browsers, cloud accounts, API keys, or network calls.
- The task must be completable within {minutes_range} minutes for a BASIC proficiency Context Engineering candidate.
- The starter code must be valid Python that runs as-is, but it must contain the shared context bug.
- The bug must be plausible and realistic, not a syntax error, missing import, or cartoonishly obvious comment.
- Do NOT include comments, TODO markers, hints files, or README text that directly says "class attribute data is the bug".
- The candidate should be asked to make a minimal fix and add one meaningful unit test.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the sports ticketing API context leak, the request metadata involved, and what the candidate must fix.
2. What will the starter code look like? Describe the key Python files, where the context bug sits, and what observable symptom tells the candidate something is wrong.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_CONTEXT_ENGINEERING_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in context propagation and context-aware logging, you are given a list of real world scenarios and proficiency levels for Context Engineering. Generate ONE realistic BASIC Context Engineering build-it task based on the sports ticketing API scenario. The candidate receives a FULLY FUNCTIONAL local Python project that runs, but it contains a request context leakage bug caused by shared mutable context state. The candidate must make a small targeted fix so each ticket hold request carries its own `request_id` and `fan_id` through the reservation and logging flow.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is a BASIC-level Context Engineering practitioner. They should understand request metadata, correlation IDs, user or session identifiers, context propagation across function calls, and the importance of preventing context leakage in logs and traces. They are not expected to design a distributed tracing platform, implement OpenTelemetry instrumentation, or build production infrastructure.

This task should feel like a small real work item from a backend team maintaining a sports ticketing API. The candidate should read a compact codebase, identify why context leaks between sequential requests, fix the request-scoped context handling, and add a focused unit test that proves separate contexts do not share `fan_id`.

**CRITICAL**: Stay within BASIC scope. The fix should require only a few lines of production code plus one test, not a framework migration or architecture rewrite.

**CRITICAL**: The generated project must be pure local Python. It must not require external services, datastore setup, container orchestration, cloud credentials, or network access.

## INSTRUCTIONS

### Nature of the Task
- The task presents a small, runnable Python project for a sports ticketing API's ticket-hold flow.
- The starter code includes a realistic context propagation bug: `RequestContext.data = {{}}` exists as shared mutable class-level state.
- The candidate must move context storage into instance initialization so each request gets its own context dict.
- The candidate must pass the context instance through the reservation and hold-log functions rather than relying on implicitly shared context.
- The candidate must add one unit test proving two independently created contexts do not share `fan_id`.
- The observable failure should involve sequential ticket hold requests producing incorrect or leaked `request_id` or `fan_id` values in `hold_logs.json`.
- The code must run as shipped, but tests should expose the incorrect behavior before the fix.
- Keep the task completable within {minutes_range} minutes.
- Keep the candidate-visible codebase small enough for a BASIC candidate to read quickly.

**CRITICAL**: Do not turn this into an LLM prompt-engineering task, a distributed tracing platform task, a REST framework configuration task, or a database task. The assessment is about basic request context isolation and propagation through local Python function calls.

**CRITICAL**: Do not add advanced concurrency, thread-local storage, async context variables, OpenTelemetry setup, Jaeger, Zipkin, message queues, or multi-service tracing as primary requirements. Those are outside the intended difficulty for this specific BASIC task.

**CRITICAL**: The generated candidate-facing README and question must describe symptoms and desired outcomes without directly spelling out the exact line to change. The evaluator-facing `answer` field may name the exact root cause and expected fix.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, context engineering documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The task must still be solvable by reading and modifying the provided local code.
- External resources should help candidates understand context propagation and shared mutable state, not be required for setup.
- Do not require paid services, API keys, remote accounts, or internet access to run the project.
- The assessment should reward practical debugging, minimal code changes, and clear verification.

## Code Generation Instructions
Based on the authoritative sports ticketing scenario, create a Context Engineering task that:
- Uses Python 3.10+ and pytest.
- Ships a small local project with a native Python manifest such as `pyproject.toml`.
- Models a ticket hold flow with request metadata including `request_id` and `fan_id`.
- Includes a `RequestContext` class whose starter implementation incorrectly shares context data between instances.
- Includes a ticket reservation function such as `reserve_seat(section, row, seat)` that must be updated to receive the request context.
- Includes a logging function such as `write_hold_log("hold_logs.json", ctx)` that must be updated or called with the request context instance.
- Writes hold log entries to a local JSON file, not to an external datastore.
- Includes tests that demonstrate the context leak before the fix and pass after the candidate isolates context per request.
- Requires the candidate to add one unit test proving two contexts do not share `fan_id`.
- Avoids unnecessary frameworks unless a tiny framework-free endpoint simulation is clearer and simpler.
- Does not require package installation commands inside candidate-facing instructions.

The generated task should be realistic but intentionally small. A good file shape is:
- `README.md`
- `.gitignore`
- `pyproject.toml`
- `app/__init__.py`
- `app/context.py`
- `app/tickets.py`
- `app/logging_utils.py`
- `tests/test_ticket_holds.py`

The output should be a valid json schema:
- `README.md`: Candidate-facing README with exactly the required four sections and no setup commands or solution details.
- `.gitignore`: Standard Python ignore rules for virtual environments, caches, test artifacts, local log files, and generated JSON logs.
- `pyproject.toml`: Native Python project manifest with pytest configuration and any minimal local dependencies required.
- `app/__init__.py`: Package marker for the local application package.
- `app/context.py`: Contains `RequestContext`; the starter bug lives here through shared mutable context data.
- `app/tickets.py`: Contains the ticket hold flow and reservation function; the starter code should demonstrate context propagation that needs to be corrected.
- `app/logging_utils.py`: Contains local JSON hold-log writing logic that records `request_id`, `fan_id`, and ticket information.
- `tests/test_ticket_holds.py`: Contains focused pytest tests for ticket holds and context isolation; at least one test should fail before the fix and pass after.

## Code file requirements
- All files must be listed and fully populated in the JSON `code_files` dict.
- Python files must follow PEP 8 and be readable by a BASIC candidate.
- The starter code must be valid and executable.
- The shared context bug must be present but not annotated with comments that reveal the fix.
- Do NOT include TODO comments, placeholder hints, or comments that say "this is wrong".
- Do NOT include solution code in candidate-facing files.
- Keep production code compact, ideally under 200 lines across files the candidate must read.
- The candidate should only need to modify `app/context.py`, `app/tickets.py`, `app/logging_utils.py`, and tests as needed.
- Tests must be deterministic and must use temporary paths for generated hold logs where appropriate.
- Do not depend on test order. If a test demonstrates sequential requests, make the sequential setup explicit inside the test.
- Include a clear way to inspect hold log entries without requiring any external service.
- The task must remain local and pure Python.

## .gitignore INSTRUCTIONS
Create a `.gitignore` appropriate for a small local Python project. It should include:
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.venv/`
- `venv/`
- `.env`
- generated local log artifacts such as `hold_logs.json`
- temporary files created by test runs

Do not include ignore rules for external datastore files or container artifacts because this is a pure local project.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The candidate-facing README must contain exactly these output sections, in this order, and no others:

1. `## Task Overview`
2. `## Objectives`
3. `## Helpful Tips`
4. `## How to Verify`

### Task Overview
- Write 3-4 meaningful sentences.
- Do not use a bullet list.
- Describe the business scenario, current state, and why the problem matters.
- Mention that ticket hold logs can show the wrong request or fan context after sequential requests.
- NEVER empty.
- NO bold time-budget callouts.
- Do not name the exact class attribute bug or tell the candidate exactly which line to change.

### Objectives
- Use 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the "what" and "why", never the "how".
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Fix context."
- GOOD: "Two ticket hold requests for different fans can produce hold logs with the wrong fan metadata; after your changes, each log entry should reflect only the request that created it."

### Helpful Tips
- Use 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery.
- They MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do not mention the exact `RequestContext.data = {{}}` root cause in the README.

### How to Verify
- Use 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, response shape, log entry contents, or isolation between two request objects.
- It is acceptable to refer to running the project's test suite, but do not include setup commands.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section)**:
Keep the following out of the README:
- Setup commands such as environment creation or package installation commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use this specific API".
- Any heading named "NOT TO INCLUDE", "Do not include", or similar.
- Database connection details, hostnames, ports, usernames, passwords, or client-tool suggestions.
- Placeholder deployment values.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each field must be filled with useful task-generation content, not placeholders.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the sports ticketing context-isolation task without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on fixing request context isolation in ticket holds.",
  "question": "The full candidate-facing task description written like a realistic work ticket from a teammate; describe the sports ticketing symptoms, the desired outcome, and the requirement to add a unit test without revealing the exact root-cause line.",
  "code_files": {{
    "README.md": "The complete candidate-facing README using exactly the four required sections in order: Task Overview, Objectives, Helpful Tips, and How to Verify, with concise non-revealing guidance.",
    ".gitignore": "The complete Python .gitignore content for caches, virtual environments, pytest artifacts, environment files, and generated local hold log files.",
    "pyproject.toml": "The complete native Python project manifest with project metadata and pytest configuration needed to run the local test suite.",
    "app/__init__.py": "A minimal package initializer for the sports ticketing application package.",
    "app/context.py": "The complete starter context module containing RequestContext with the intentionally flawed shared context storage that the candidate must isolate per request.",
    "app/tickets.py": "The complete starter ticket hold and reservation module that currently allows request metadata to leak through the reservation flow and must be updated to propagate the context instance.",
    "app/logging_utils.py": "The complete starter logging module that writes local hold log JSON entries and must participate in receiving the correct request context.",
    "tests/test_ticket_holds.py": "The complete pytest test file with focused tests for ticket hold logging behavior and context isolation, including a failing test signal that passes after the candidate fix."
  }},
  "answer": "Evaluator-facing high-level solution approach that names the shared mutable context root cause, explains moving context storage into RequestContext initialization, explains passing the context instance into reservation and logging calls, and describes the unit test proving no fan_id leakage.",
  "definitions": "An object of term-to-definition pairs explaining request context, context propagation, correlation ID, context leakage, structured logging, and unit test isolation in simple BASIC-level language.",
  "hints": "A single line nudging investigation toward comparing two independent ticket hold requests and inspecting the context values written to the hold log, without revealing the exact code change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on isolated request metadata, correct hold log entries for different fans, one added unit test for context isolation, and clean targeted code changes.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Python 3.10+, pytest basics, reading small Python modules, request metadata concepts, and basic context-aware logging.",
  "short_overview": "A bullet list summarizing the sports ticketing business problem, the context propagation bug, and the expected outcome of isolated request context per ticket hold."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown fences, no explanations. Emit the raw JSON object starting with {{ and ending with }}.
2. Use exactly these top-level keys: `name`, `title`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, and `short_overview`.
3. Do NOT use synonyms such as `task_title`, `files`, `repository`, `context`, `solution`, or `criteria`.
4. `name` must be kebab-case and under 50 characters.
5. `title` must be plain English, verb-first, 50-80 characters, and different from `name`.
6. The task must be a pure local Python project with a native Python manifest and pytest tests.
7. Do NOT include external services, datastore setup, container orchestration, cloud credentials, or network calls.
8. Do NOT include `docker-compose.yml`, `init_database.sql`, datastore configuration, deployment instructions, or external service health checks.
9. The starter code must be runnable Python 3.10+ and must contain the context leakage bug without syntax errors.
10. The bug must center on request context isolation and propagation, not authentication, seat pricing, payment processing, or database schema design.
11. The candidate-facing files must not reveal the reference answer through comments, TODOs, docstrings, README text, or overly explicit hints.
12. The evaluator-facing `answer` field should clearly explain the root cause and expected fix.
13. Include one unit-test expectation proving two contexts do not share `fan_id`.
14. Holding seats for different fans must write separate log entries with the correct `request_id` and `fan_id` after the fix.
15. Keep the task BASIC and completable within {minutes_range} minutes.
"""

PROMPT_REGISTRY = {
    "Context Engineering (BASIC)": [
        PROMPT_CONTEXT_ENGINEERING_BASIC_CONTEXT,
        PROMPT_CONTEXT_ENGINEERING_BASIC_INPUT_AND_ASK,
        PROMPT_CONTEXT_ENGINEERING_BASIC_INSTRUCTIONS,
    ]
}