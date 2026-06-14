PROMPT_PYTHON_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for BASIC level Python proficiency.
- Ensure the candidate can realistically complete the task in the allocated time.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context.

Before proceeding to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the business domain, technical context, and the problem the candidate will solve.
2. What will the task look like? Describe the type of Python implementation or bug fix required, the expected deliverables, and how it aligns with BASIC proficiency.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_BASIC_INSTRUCTIONS = """
# Python BASIC Task Requirements

## GOAL
As a technical architect experienced in Python, you are given real-world scenarios and proficiency levels for Python development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and evaluator guidance, that can be used to assess a candidate's ability to complete a small but realistic Python task at BASIC proficiency.

The task must stay within BASIC Python scope:
- Python syntax, variables, strings, numbers, booleans
- if/elif/else, for/while loops
- functions with arguments and return values
- lists, tuples, dictionaries, sets
- file I/O with text or JSON files
- standard library usage such as json, csv, pathlib, os, math, random, datetime, collections
- try/except for straightforward error handling
- reading and making minor edits to existing code
- simple scripts and well-scoped bug fixes
- basic tests are allowed if they are simple and directly support the task

Do NOT require:
- async/await
- system design
- microservices
- advanced concurrency
- security hardening
- advanced caching
- complex architecture refactors
- framework-specific expertise
- advanced performance tuning

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive:
- A small Python script project
- Starter code that runs successfully
- A realistic bug fix or feature implementation task
- A focused problem involving 2-3 BASIC-level concepts combined

The candidate's responsibility is to make a limited set of changes using practical Python skills. The task must be specific, realistic, and narrow enough to complete within {minutes_range} minutes.

## INSTRUCTIONS

### Nature of the Task
- The task must ask the candidate to implement a small feature or fix a logical bug in an existing Python script project.
- The scenario must be realistic, business-grounded, and easy to understand.
- The task must be specific rather than open-ended.
- The starter code must provide a clear starting point without giving away the solution.
- The task must not be a trick question based on syntax errors or broken setup.
- The complexity must align with BASIC proficiency:
  - Appropriate examples:
    - reading a CSV, TXT, or JSON file and validating rows
    - transforming records into dictionaries or simple class instances
    - aggregating counts or totals using loops, dicts, Counter, or defaultdict
    - fixing incorrect filtering, grouping, or summary logic
    - handling invalid input with try/except and continuing safely
    - writing cleaned output to a text or JSON file
    - adding a small helper module or simple unit tests
  - Not appropriate:
    - advanced design patterns
    - distributed systems
    - complex inheritance hierarchies as the main challenge
    - metaprogramming
    - advanced decorators
    - heavy framework usage
    - deep algorithmic optimization
- The question must NOT include hints. Hints belong only in the "hints" field.
- Use Python 3.10+ best practices suitable for BASIC level.
- The task name should be short, descriptive, under 50 characters, and use kebab-case.

### Task Scenario Structure
Each task MUST be defined in two clear parts:

**Current Implementation (what we give to the candidate):**
- Describe precisely the current buggy or incomplete behavior implemented by the starter code.
- The starter code MUST exactly match this current implementation.
- Suitable examples:
  - A script reads rows from a CSV but crashes on blank lines or invalid numeric values
  - A report function groups records incorrectly because it uses the wrong dictionary key
  - A JSON export includes invalid records because validation is missing
  - A helper function swallows exceptions and hides which input row failed
  - A summary script writes totals incorrectly when duplicate keys appear

**Required Changes (what the candidate must do):**
- List 2-4 specific changes appropriate for BASIC level.
- Suitable examples:
  - Validate required fields before processing a row
  - Convert numeric strings safely and skip invalid rows
  - Use try/except to report row-level errors without crashing the whole script
  - Refactor repeated logic into a helper function
  - Write only valid records to an output file
  - Add or fix a small unit test file for the core behavior

**Final Implementation Approach:**
- Provide a high-level description of the correct approach without giving the exact solution.
- The final approach should reflect BASIC-level Python knowledge:
  - functions and modules
  - loops and conditionals
  - dictionaries/lists/sets
  - file reading and writing
  - standard library usage
  - try/except for clear error handling
  - readable, maintainable code
  - optional simple tests using unittest or pytest if included

### Starter Code Requirements

**FUNCTIONAL PROJECT REQUIREMENTS:**
- The starter code MUST be a complete, working Python script project.
- ZERO syntax errors and ZERO import errors.
- The project must run successfully in its current incomplete or buggy state.
- The candidate should NOT need to fix the environment to begin the task.
- The starter code must implement the current buggy or incomplete behavior exactly, but still run.

**WHAT MUST BE INCLUDED:**
- A small Python project with 2-5 files total, such as:
  - main.py
  - helpers.py or processor.py
  - one input data file such as data/orders.csv, data/events.json, or data/shipments.txt
  - optional simple test file such as tests/test_processor.py
- requirements.txt only if third-party dependencies are truly necessary; prefer standard library only
- README.md with the required sections below
- .gitignore suitable for Python

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- DO NOT include framework setup such as Flask, FastAPI, Django, Celery, or SQLAlchemy.
- DO NOT require Docker, docker-compose, databases, browsers, or external services.
- DO NOT include comments that reveal the solution.
- DO NOT make the candidate repair broken infrastructure.
- DO NOT include advanced testing setup; if tests are included, keep them simple and directly related to the task.

### Runtime and Project Shape Requirements
This task category is a Python script task:
- No Dockerfile
- No docker-compose.yml
- No database service
- No web framework
- Include a simple run.sh that executes the project with Python if a run script is included
- If you include kill.sh, it should be minimal and only clean generated local files; it must not assume containers exist
- Prefer standard library dependencies only

### AI and External Resource Policy
- Candidates are permitted to use external resources including AI tools.
- The task should still require genuine reasoning, debugging, and implementation beyond simple copy-paste.

## Code Generation Instructions
Based on the real-world scenarios, create a Python task that:
- Draws inspiration from ONE input scenario for business context
- Matches BASIC proficiency
- Can be completed within {minutes_range} minutes
- Tests practical Python skills for small scripts and helper modules
- Uses a different real-world scenario each time for variety
- Emphasizes correctness, readability, and straightforward error handling

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy or incomplete state. (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following the required structure",
    ".gitignore": "Python exclusions",
    "requirements.txt": "Minimal dependencies or empty if standard library only",
    "run.sh": "Optional script to run the project",
    "main.py": "Main Python script entry point",
    "helpers.py": "Helper or processing module",
    "data/input_file_name.ext": "Optional input data file",
    "tests/test_main.py": "Optional simple test file"
  }},
  "outcomes": "Bullet-point list. Expected results after completion.",
  "short_overview": "Bullet-point list: (1) business context, (2) what the candidate must fix or implement, (3) expected outcome.",
  "pre_requisites": "Bullet-point list: Python 3.10+, pip, Git, and basic Python knowledge.",
  "answer": "High-level solution approach only. No full code.",
  "hints": "Single line suggesting a focus area. Must NOT give away the answer.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## Code File Requirements
- More than 1 file may be generated, but keep the file count modest.
- Code should follow Python PEP 8 guidelines.
- The generated code files MUST NOT contain the full implementation for the core logic of the task.
- The project should be runnable, but the code requiring implementation should remain incomplete or logically flawed until the candidate fixes it.
- Do NOT include comments that reveal the solution.
- Do NOT include placeholder comments such as TODO, implement here, intended behavior, or similar.
- If tests are included, they must be simple and aligned with BASIC level. They may fail initially because the feature is incomplete or the bug is still present, but the project itself must still be runnable.

## .gitignore Instructions
Use a sensible Python .gitignore, including items such as:
- __pycache__/
- *.pyc
- .venv/
- venv/
- .pytest_cache/
- .mypy_cache/
- .DS_Store
- *.log

## README.md Structure
The README.md MUST contain the following sections in this order:
1. Task Overview
2. Objectives
3. How to Verify
4. Helpful Tips

### Task Overview
- Must contain 2-3 substantial sentences.
- Describe the specific business workflow and the current issue in the Python script.
- Make clear that the candidate is working on a small script task, not a large application.
- Explain why the fix or feature matters to the business process.

### Objectives
- Clear, measurable goals appropriate for BASIC Python level
- Focus on correctness, simple validation, reliable processing, readable code, and expected output
- Objectives should be directly verifiable

### How to Verify
- Include concrete checks such as:
  - run the script and confirm it completes
  - confirm invalid rows are skipped or reported correctly
  - confirm output files contain only valid records
  - confirm totals, summaries, or grouped results are correct
  - if tests are included, confirm the relevant tests pass after implementation
- Keep verification practical and measurable

### Helpful Tips
- Use general guidance only
- Acceptable tip style:
  - Consider where input validation should happen before a record is processed
  - Review whether repeated logic can be moved into a helper function
  - Think about how try/except can report bad rows without stopping the whole script
  - Explore whether a dictionary or Counter would simplify the summary logic
- Do NOT provide direct solutions

### NOT TO INCLUDE
- Setup instructions or shell commands
- Step-by-step implementation guides
- Exact code solutions
- Advanced architecture advice outside BASIC scope

## CRITICAL REMINDERS
1. The environment must be fully working.
2. The starter code must be runnable but incomplete or logically flawed in a specific way.
3. The starter code must perfectly match the described Current Implementation.
4. Use only BASIC Python concepts within scope.
5. The task must be completable within {minutes_range} minutes.
6. Prefer standard library modules.
7. Keep the scenario realistic and well-scoped.
8. README.md must be fully populated.
9. Output must be valid JSON only when generating the task artifact.
10. Use the exact canonical top-level keys: "name", "question", "code_files", "answer", "definitions", "hints", "outcomes", "pre_requisites", "short_overview".
"""

PROMPT_REGISTRY = {
    "Python (BASIC)": [
        PROMPT_PYTHON_BASIC_CONTEXT,
        PROMPT_PYTHON_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_BASIC_INSTRUCTIONS,
    ]
}