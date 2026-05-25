PROMPT_SCALA_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

You are generating an INTERMEDIATE-level Scala assessment. Before producing the task, briefly summarize:
1. What kind of Scala systems or modules this company likely builds.
2. What level of ownership and technical judgment the role expects.
3. Which Scala capabilities are most relevant to assess from the provided context.
"""

PROMPT_SCALA_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating an INTERMEDIATE Scala assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

ADDITIONAL QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- Generate a PURE_CODE task only: a small Scala codebase with source files, tests, build files, and README. Do NOT use Docker, databases, web servers, or external infrastructure.
- The task must fit INTERMEDIATE level: 45-60 minutes, requiring 4-5 connected concepts and meaningful implementation judgment.
- Stay grounded in Scala application/library work that is directly supported by the competency scope: idiomatic Scala, ADTs, pattern matching, collections, Futures or effect handling, error modeling, modular design, and testing.
- Prefer a realistic service/library module rather than trivia or framework setup.
- The candidate should modify/fix existing starter code rather than build everything from scratch.
- Draw inspiration from ONE realistic scenario. Good fits include: async aggregation, typed error handling, collection pipeline refactoring, safe Java interop, or domain modeling cleanup.
- Do NOT make the task primarily about sbt configuration, advanced distributed systems, full HTTP service implementation, Spark jobs, or heavy framework wiring.

Briefly confirm your plan before generating the final task:
1. What business/domain scenario will you use?
2. What existing Scala module is broken or incomplete?
3. Which 4-5 Scala skills will the candidate need to demonstrate?
4. Why is the task appropriate for INTERMEDIATE level within {minutes_range} minutes?
"""

PROMPT_SCALA_INTERMEDIATE_INSTRUCTIONS = """
# Scala INTERMEDIATE Task Generation Instructions

## GOAL
Generate a complete Scala assessment task for an INTERMEDIATE candidate. The task must evaluate practical Scala engineering ability through a realistic, bounded code change in an existing codebase.

## HARD BOUNDARIES
- Stay strictly within the Scala competency scope provided.
- The task must be PURE_CODE only.
- Include a runnable Scala project structure using sbt.
- Do NOT require Docker, databases, message brokers, web frameworks, cloud services, or external APIs.
- Do NOT make the task mainly about infrastructure setup, obscure type-system tricks, or framework-specific configuration.
- The task should assess applied Scala coding and reasoning, not memorization.

## TASK SHAPE
Create a task where the candidate fixes and improves an existing Scala module. The best task shape is:
- a small domain modeled with case classes and sealed traits,
- one service or processor with flawed async/error-handling/collection logic,
- one Java-interop boundary or nullable input edge case,
- tests that currently fail or are incomplete,
- clear expected behavior after the candidate's changes.

The task should naturally exercise several of these Scala skills:
- domain modeling with case classes and sealed traits,
- pattern matching and safe decoding,
- `Option`, `Either`, `Try`, or typed domain errors,
- `Future` composition with `ExecutionContext`,
- collection choice and transformation efficiency,
- avoiding unsafe partial functions and null handling,
- modular refactoring for readability and maintainability,
- unit tests for correctness and edge cases.

## DIFFICULTY CALIBRATION
This is INTERMEDIATE level, so the task MUST:
- combine 4-5 concepts in one coherent implementation,
- require design judgment and correctness reasoning,
- include proper testing expectations,
- include error handling and at least modest performance/refactoring concerns,
- remain solvable by one candidate in {minutes_range} minutes.

Avoid making the task too large. A good target is:
- 5-8 files total,
- 2-4 Scala source files,
- 1-3 test files,
- `build.sbt`,
- `README.md`,
- optionally `.gitignore`.

## REQUIRED PROJECT STRUCTURE
Because this is PURE_CODE, the generated `code_files` should contain only source/build/documentation files such as:
- `build.sbt`
- `README.md`
- `.gitignore`
- `src/main/scala/...`
- `src/test/scala/...`

Do not include Dockerfiles, compose files, SQL files, or web app scaffolding.

## STARTER CODE REQUIREMENTS
- The starter code must compile or be very close to compiling with only task-related failures to fix.
- The starter code must reflect the exact "Current Implementation" described in the task.
- Do not include solution comments, TODOs that reveal the answer, or hidden shortcuts.
- The code should be incomplete or flawed in realistic ways: unsafe pattern matching, nested futures, sequential async work, null-heavy Java interop, unnecessary intermediate collections, weak domain modeling, or missing typed errors.
- Keep dependencies lightweight and appropriate for Scala. Typical acceptable choices: Scala standard library, ScalaTest or MUnit, and optionally a small JSON or Cats dependency only if truly needed. Do not require heavy framework knowledge.

## README REQUIREMENTS
The `README.md` inside `code_files` must include these fully written sections:
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

The README must explain the business scenario, what is currently wrong, and what observable outcomes should be true after the candidate finishes.

## QUESTION REQUIREMENTS
The `"question"` field must be candidate-facing and clearly structured. It MUST include:
1. A short scenario description.
2. A **Current Implementation** section describing the exact current buggy/incomplete behavior already present in the starter code.
3. A **Required Changes** section listing the concrete changes the candidate must make.
4. A **Constraints** section clarifying boundaries such as keeping the public API stable where appropriate, avoiding unnecessary rewrites, and preserving project simplicity.
5. A **What Good Looks Like** section describing expected correctness, error handling, and code quality outcomes.

## OUTPUT JSON STRUCTURE
Return exactly one JSON object using these exact top-level keys and no synonyms:

{{
  "name": "short-kebab-case-task-name",
  "question": "full candidate-facing task description",
  "code_files": {{
    "README.md": "full file contents",
    "build.sbt": "full file contents",
    ".gitignore": "full file contents",
    "src/main/scala/example/File1.scala": "full file contents",
    "src/main/scala/example/File2.scala": "full file contents",
    "src/test/scala/example/File1Spec.scala": "full file contents"
  }},
  "answer": {{
    "summary": "evaluator-facing high-level solution summary",
    "key_points": [
      "important implementation point 1",
      "important implementation point 2"
    ]
  }},
  "definitions": {{
    "term_1": "definition",
    "term_2": "definition"
  }},
  "hints": "brief non-revealing hint",
  "outcomes": "bullet list of expected outcomes",
  "pre_requisites": "bullet list of tools and knowledge required",
  "short_overview": "bullet list summarizing the task"
}}

Use these exact key names:
- `name`
- `question`
- `code_files`
- `answer`
- `definitions`
- `hints`
- `outcomes`
- `pre_requisites`
- `short_overview`

Do not rename any of them.

## RECOMMENDED TASK PROFILE FOR THIS COMBINATION
A strong fit for this Scala INTERMEDIATE prompt is a small asynchronous aggregation or event-processing module where the candidate must:
- replace unsafe string/status handling with a sealed trait ADT and safe decoder,
- return typed errors with `Either` or similar,
- compose `Future` operations idiomatically instead of nesting or sequencing unnecessarily,
- handle nullable Java-style input safely with `Option`,
- improve a collection transformation to avoid unsafe partial functions or wasteful intermediate allocations,
- add or fix tests covering edge cases and failure paths.

This is guidance, not a mandatory exact scenario, but the final task should feel similar in complexity and style.

## QUALITY BAR
The generated task should reveal whether the candidate can:
- write idiomatic Scala rather than Java-in-Scala style code,
- model a domain clearly,
- make pragmatic choices around async and error handling,
- reason about correctness and edge cases,
- improve maintainability without overengineering,
- write focused tests.

## FINAL REMINDERS
1. Keep the task realistic and self-contained.
2. Keep it within INTERMEDIATE scope and time box.
3. Ensure the starter project is coherent and runnable as a PURE_CODE Scala project.
4. Ensure every file in `code_files` has complete contents.
5. Ensure the task does not depend on any unavailable external service.
6. Ensure the output is a single JSON object with the exact canonical keys above.
"""

PROMPT_REGISTRY = {
    "Scala (INTERMEDIATE)": [
        PROMPT_SCALA_INTERMEDIATE_CONTEXT,
        PROMPT_SCALA_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_SCALA_INTERMEDIATE_INSTRUCTIONS,
    ]
}