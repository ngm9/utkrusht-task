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
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_BASIC = """
# Python Basic Task Requirements

## GOAL
As a technical architect experienced in Python, you are given real-world scenarios and proficiency levels for Python development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to think, design, build, implement, debug, and solve a problem end to end at BASIC proficiency (1-2 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a well-scoped feature or fix a bug in existing code that requires functions, modules, basic OOP, and/or structured error handling.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point and demonstrates the current (buggy or incomplete) implementation.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question or purely syntactic errors.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy or incomplete state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The module parses JSON but does not validate required fields"; "A class method mutates shared state incorrectly"; "Error handling swallows exceptions and returns None."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must run without syntax errors, but it must exhibit exactly these bugs or missing pieces. Do not accidentally fix the issues or add the solution in the starter code.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Validate input with a schema and raise ValueError for invalid data"; "Refactor into a class with proper encapsulation"; "Use try/except/finally and re-raise or log appropriately."
- The candidate's job is only to complete these required changes on top of the current implementation.

**Final Implementation Approach:**
- A high-level description of the correct approach (e.g. "Use a small module with one public function and helpers. Validate with a Pydantic model or simple checks. Use a class for state. Add unit tests for edge cases.").
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Python experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be well-scoped and focus on:
  - Functions and modules (structuring code, imports, packaging conventions)
  - OOP basics (classes with __init__, instance methods, simple inheritance)
  - Error handling (try/except/finally, raise, catch appropriate exceptions, avoid swallowing errors)
  - Data structures and standard library (list comprehensions, dict operations, collections.defaultdict/Counter, json, os, pathlib)
  - Testing and readability (simple unit tests with unittest or pytest, readable and maintainable code)
  - File I/O, CSV/JSON, or simple HTTP usage where appropriate
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to Python 3 best practices (Python 3.8+) and PEP 8 style where applicable.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years Python experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "json-validator-module", "config-loader-refactor".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working Python script or small project** that runs successfully after setting up the environment (e.g. `pip install -r requirements.txt` if needed) and running the main entry point.
- **ZERO syntax errors, ZERO runtime errors** — the project must run cleanly out of the box.
- **All existing functionality in the starter code must work** — Any functions, I/O, or logic that are already implemented must execute as intended for the "Current Implementation" state.
- **The candidate should NOT need to fix anything to make the script run** — The environment is already fully functional; the candidate's job is only to implement the requested feature or fix the specified bug, not to repair a broken project.
- The project must behave like a working baseline that the candidate can run, explore, and then extend or fix as per the task description.

**WHAT MUST BE INCLUDED:**
- The starter code should provide a clear structure (e.g. main script, optional module or package) so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable (e.g. `python main.py` or `python -m package.module`).
- Keep the code files minimal and to the point.
- Python starter code may include a simple project layout (main script, module, or package) but NOT require complex infrastructure.
- Use a requirements.txt only if the task needs third-party libraries; otherwise plain standard library is fine.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the buggy or incomplete state described in the task. It must run and exhibit that state; it must NOT include any of the "Required Changes" or the final implementation approach.
- If the task is to fix bugs, the starter code has logical or design bugs (no syntactic errors) that are appropriate for basic level.
- If the task is to implement a feature, the starter code only provides a good starting point that matches the described current state.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Python proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a Python task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BASIC proficiency level (1-2 years Python experience)
- Can be completed within {minutes_range} minutes
- Tests practical Python skills at basic level: functions, modules, OOP basics, error handling, standard library, and simple tests
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-module or small-package features with clear scope

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state the starter code implements (what we give). (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous so starter code can perfectly match Current Implementation and candidate knows exactly what to do.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Python exclusions (e.g. __pycache__, .env, venv)",
    "requirements.txt": "Only if third-party libs needed; otherwise omit or minimal",
    "main.py": "Main script or entry point",
    "additional_module.py": "Other modules or helpers as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, environment setup, and knowledge required. Include Python 3.8+, pip, Git, basic Python knowledge, unittest or pytest, etc.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}


## README.md STRUCTURE (Python Basic)
- The README.md contains the following sections:
  - Task Overview
  - Objectives
  - How to Verify
  - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Python task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context.

### Objectives

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate appropriate for basic level
- What functionality should be implemented, expected behavior
- Focus on functions, modules, OOP basics, error handling, or tests as appropriate
- This is what the candidate should be able to do successfully to say that they have completed the task

**CRITICAL**: Objectives will be used to verify task completion and award points

### How to Verify

Verification approaches after implementation:

- Specific checkpoints after implementation, what to test and how to confirm success
- Observable behaviors or outputs to validate
- Include both functional testing and basic code quality checks
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes

### Helpful Tips

Practical guidance without revealing implementations:

- Project context and guidance points suitable for basic-level Python developers
- Where to look in the codebase and which concepts (functions, classes, error handling) may be relevant
- Important considerations for the implementation for the task
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (pip install, python main.py, etc.) unless essential for the task type
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific Python syntax examples or code snippets that would give away the solution
- Function names or logic patterns that would reveal the solution
- Any specific file or module implementation details that would give away the solution


## CRITICAL REMINDERS

1. **Environment must be fully working** — The project must run perfectly with the stated run command; zero errors; the candidate does NOT fix the environment, only the task (feature/bug).
2. **Starter code must be runnable** but must NOT contain the core logic solution
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on BASIC Python concepts** (functions, modules, OOP basics, error handling, standard library, simple tests)
7. **Use Python 3.8+** and standard style (PEP 8 where applicable)
8. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
9. **README.md MUST be fully populated** with meaningful, task-specific content
10. **.gitignore** must cover standard Python exclusions
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
"""

PROMPT_REGISTRY = {
    "Python (BASIC)": [
        PROMPT_PYTHON_BASIC_CONTEXT,
        PROMPT_PYTHON_BASIC_INPUT_AND_ASK,
        PROMPT_PYTHON_BASIC,
    ]
}
