PROMPT_FLUTTER_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competency:
{competencies}

Before generating the task, briefly summarize your understanding of:
1. The product/team context,
2. What an intermediate Flutter engineer is expected to handle here,
3. The kinds of mobile engineering decisions that should be reflected in the assessment.
"""

PROMPT_FLUTTER_INTERMEDIATE_INPUT_AND_ASK = """
Now use the following inputs to prepare a Flutter INTERMEDIATE assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

OPTIONAL CALIBRATION INPUT:
{question_prompt}

Task framing requirements:
- Generate exactly ONE Flutter task inspired by ONE realistic scenario.
- The task must fit INTERMEDIATE level and be completable within {minutes_range} minutes.
- The task must assess applied Flutter engineering, not trivia.
- Keep the scope inside pure Flutter/Dart code: source files, tests, and package configuration only.
- Do not require Docker, backend services, native platform code, CI/CD setup, or external infrastructure.
- The candidate should work from existing starter code that is runnable but incomplete or flawed.
- The task should combine 4-5 relevant Flutter concepts such as async state handling, architecture, widget composition, performance-minded UI updates, error handling, caching, and testing.
- Prefer a scenario where the candidate must reason about stale async results, state transitions, and unnecessary rebuilds rather than build an entire app from scratch.

Briefly confirm:
1. Which scenario/domain you chose,
2. What the current flawed implementation does,
3. What the candidate will need to change,
4. Why this is appropriate for an intermediate Flutter engineer.
"""

PROMPT_FLUTTER_INTERMEDIATE_INSTRUCTIONS = """
# Flutter INTERMEDIATE Task Generation Instructions

## GOAL
Generate a complete assessment task for an INTERMEDIATE Flutter developer. The task must evaluate practical Dart and Flutter skills through a realistic feature fix or refactor in an existing codebase.

The generated task must stay within these competency boundaries:
- Dart fundamentals in real code: async/await, Futures, Streams where appropriate, null safety, OOP, and clean separation of concerns.
- Flutter architecture and widget composition.
- State management using one mainstream approach such as Provider or Riverpod.
- API-style repository interaction simulated in code.
- Local caching or persistence at a lightweight level that can be represented in pure code.
- Error handling, loading states, and stale-data handling.
- Performance-minded UI structure such as reducing unnecessary rebuilds.
- Testing appropriate for intermediate level.

Do NOT make the task depend on:
- Docker, databases, web servers, Firebase setup, platform channels, or external services,
- advanced system design beyond a single Flutter codebase,
- security hardening as the main challenge,
- native mobile code,
- multi-service architecture.

## REQUIRED TASK SHAPE
Create a Flutter/Dart repository-style task with only pure code artifacts, for example:
- `pubspec.yaml`
- `README.md`
- `lib/...`
- `test/...`
- optional analysis/lint config files

Do not include Dockerfiles, compose files, backend code, SQL, or infrastructure files.

## TASK DESIGN REQUIREMENTS
- The task must be based on a realistic mobile product scenario.
- The candidate must modify existing starter code, not start from a blank project.
- The starter code must run cleanly and reflect the intentionally flawed current implementation.
- The task should require 4-5 concepts working together, such as:
  - repository + controller/provider separation,
  - async request coordination so stale responses do not overwrite newer state,
  - lightweight cache with TTL,
  - explicit loading/data/error state modeling,
  - widget decomposition to avoid broad rebuilds,
  - tests for controller/repository/UI behavior.
- The task should be completable within {minutes_range} minutes by a 3-5 year Flutter engineer.
- Include enough code to make the problem concrete, but do not give away the final solution.
- The candidate-facing question must clearly separate:
  1. Current Implementation
  2. Required Changes
  3. Constraints
  4. How to Verify

## RECOMMENDED SCENARIO STYLE
A strong fit is a data-driven screen where:
- filter changes trigger overlapping async loads,
- older responses can overwrite newer selections,
- the UI currently uses an oversimplified busy/error model,
- the last good data should remain visible during recoverable failures,
- repeated visits or repeated filter selections should avoid unnecessary fetches,
- the widget tree can be improved to reduce unnecessary rebuilds.

## STARTER CODE EXPECTATIONS
The generated starter code should typically include:
- a small app entry point,
- one screen with filter controls and a list/body,
- a controller/provider/state model,
- a repository and fake API client,
- simple domain models,
- at least one test file that currently reflects expected behavior targets but does not solve the task for the candidate.

The code should be realistic but compact. Avoid excessive boilerplate.

## REQUIRED OUTPUT JSON STRUCTURE
Return exactly one JSON object using these exact top-level keys:

{{
  "name": "short-kebab-case-task-name",
  "question": "Full candidate-facing task description",
  "code_files": {{
    "README.md": "Full file contents",
    "pubspec.yaml": "Full file contents",
    "lib/main.dart": "Full file contents"
  }},
  "answer": {{
    "summary": "Evaluator-facing high-level solution summary",
    "key_points": [
      "Important implementation expectations",
      "Important reasoning expectations"
    ]
  }},
  "definitions": {{
    "stale response": "A slower earlier request finishing after a newer request and incorrectly replacing newer state",
    "ttl cache": "A cache entry that is considered valid only for a fixed time window"
  }},
  "hints": "A brief non-solution hint that nudges the candidate toward the right area of focus.",
  "outcomes": "Bullet list describing what a successful submission should achieve.",
  "pre_requisites": "Bullet list describing tools and knowledge needed to run and complete the task.",
  "short_overview": "Bullet list summarizing the business context, implementation goal, and expected result."
}}

Do not use any synonym keys such as "title", "task_title", "files", "repository_structure", or "acceptance_criteria".

## README REQUIREMENTS
The `README.md` file inside `code_files` must include these sections with concrete task-specific content:
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

## QUALITY BAR
- The task must feel production-relevant for Flutter.
- The code must be internally consistent and runnable.
- The task must test judgment, not memorization.
- The candidate should have multiple valid implementation paths.
- The solution should not require internet access or real external APIs.
- If tests are included, they should be meaningful but not overly broad.

## IMPORTANT REMINDERS
1. Pure code only: no Docker, no backend, no database server, no infrastructure files.
2. Keep the task squarely within Flutter intermediate scope.
3. Use realistic async/state/performance concerns, but keep the repository small enough for the time box.
4. The starter code must match the described current implementation exactly.
5. Do not include solution comments or TODOs that reveal the answer.
6. The output JSON must use the exact canonical keys specified above.
"""

PROMPT_REGISTRY = {
    "Flutter (INTERMEDIATE)": [
        PROMPT_FLUTTER_INTERMEDIATE_CONTEXT,
        PROMPT_FLUTTER_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_FLUTTER_INTERMEDIATE_INSTRUCTIONS,
    ]
}