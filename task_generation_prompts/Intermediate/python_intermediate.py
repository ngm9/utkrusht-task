PROMPT_PYTHON_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_PYTHON_INTERMEDIATE_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (INTERMEDIATE: 3-5 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_INTERMEDIATE = """
# Python Intermediate Task Requirements

## GOAL
As a technical architect super experienced in Python, you are given real-world scenarios and proficiency levels for Python development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end at an INTERMEDIATE level.

## INSTRUCTIONS

### INTERMEDIATE PROFICIENCY SCOPE (What the task may assess)
Tasks MUST align with INTERMEDIATE Python (3-5 years). The task may assess one or more of the following; do NOT go beyond this scope into advanced/expert topics:

- **Core language and design**: Type hints, docstrings, clear function/module boundaries, OOP (classes, inheritance, composition, encapsulation), list/dict comprehensions, generators, context managers (`with`), decorators. PEP 8 and project structure.
- **APIs and web frameworks**: Simple routes or handlers (Flask or FastAPI), request/response handling, query/path parameters, request body parsing, structured JSON responses. Basic dependency injection or app structure. No complex auth or distributed systems.
- **Data and I/O**: Reading/writing files, parsing and serializing JSON/CSV, environment variables, optional simple DB access (e.g. one or two queries or ORM usage). Connection handling or basic error handling around I/O.
- **Error handling and validation**: try/except, custom exceptions, consistent error responses (e.g. 4xx/5xx or error payloads). Input validation (e.g. Pydantic or manual checks), handling missing keys, type errors, and invalid input. When to validate defensively vs raise.
- **Testing**: Unit tests with pytest (or unittest), fixtures, mocks for I/O or external calls. What to test (happy path, edge cases). Test layout (e.g. tests/ directory). No heavy integration or e2e requirements.
- **Working in a codebase**: Extending existing modules, refactoring for clarity (extract function, remove duplication), following existing conventions. Small, safe changes without redesigning core architecture.

Do NOT require: complex async/concurrency, microservices, advanced DB tuning, heavy infrastructure (Kubernetes, etc.), or expert-level algorithms. Keep the task completable in the given time by an intermediate developer.

### Nature of the Task
- Task must ask to implement a feature from scratch, fix bugs, or refactor/extend existing code. It may involve API design, validation, error handling, or adding tests.
- The question scenario must be clear, with facts and context historically accurate and relevant. Use a single, digestible business scenario (e.g. one API, one module, one small workflow).
- Generate enough starter code so the candidate has a runnable baseline (e.g. app runs, one or two modules present). DO NOT give away the solution in the starter code.
- Assessment focus: candidate implements best practices, correct design, and maintainable, testable code—not just making it "work."
- The question must be a real-world scenario, not a trick based on syntax or gotchas. Requirements should be explicit enough that an intermediate developer knows what "done" looks like.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the incomplete or buggy state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The API endpoint does not validate input"; "Error handling is missing for I/O failures"; "The module has no tests and duplicated logic."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must run without syntax errors, but must exhibit exactly these gaps or bugs. Do not accidentally include the solution in the starter code.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Add Pydantic validation and structured error responses"; "Use context managers and centralize error handling"; "Extract helpers, add unit tests, and remove duplication."
- The candidate's job is to complete these required changes on top of the current implementation.

**Final Implementation Approach:**
- Provide a high-level description of the correct approach (e.g. "Add a Pydantic model for the request body; validate in the route and return 400 with a structured error payload. Add pytest tests for valid and invalid input."). This guides the assessor and must align with the "Required Changes" and one of the INTERMEDIATE task types above.
- The complexity and scope must align with INTERMEDIATE (3-5 years): one primary ask with clear success criteria. Do not generate tasks that require advanced or expert knowledge.
- The question text must be specific: candidate should understand exactly what "Current Implementation" they receive and what "Required Changes" they must implement. No vague or open-ended wording. Do NOT include hints in the question; hints go in the "hints" field only.
- Ensure that all questions and scenarios adhere to Python 3 best practices (Python 3.8+) and PEP 8.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years Python experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "api-validation-refactor", "pytest-coverage-handlers".

### Task types suitable for INTERMEDIATE (pick one focus or a small combination)
- **Add validation and error handling**: Starter code has an endpoint or function that accepts input without validation or returns errors inconsistently; candidate adds validation (e.g. Pydantic), structured error responses, and clear error messages.
- **Implement a missing feature**: Starter has structure (e.g. route, module) but one clear feature is missing (e.g. a new endpoint, a helper that aggregates data, a file export). Candidate implements it with correct types and error handling.
- **Fix logical bugs or edge cases**: Code runs but fails on edge cases (empty input, missing file, invalid type). Candidate identifies and fixes with tests or at least clear handling.
- **Refactor for clarity and testability**: Starter has duplicated logic or one large function; candidate extracts helpers, adds or improves unit tests, and keeps behavior unchanged.
- **Add or improve tests**: Starter has little or no tests; candidate adds pytest tests (and fixtures/mocks as needed) for the critical paths or new code they add.
- **Extend an existing module**: One module or script exists; candidate adds a related function, endpoint, or small feature while following existing style and structure.

Avoid: multi-service setup, complex async flows, database migrations, or tasks that require deep domain or infrastructure knowledge. One clear "ask" (e.g. "add validation to this endpoint") is better than many unrelated asks.

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working Python script or small project** that runs successfully after setting up the environment (e.g. `pip install -r requirements.txt` if needed) and running the main entry point.
- **ZERO syntax errors, ZERO runtime errors** — the project must run cleanly out of the box.
- **All existing functionality in the starter code must work** for the "Current Implementation" state.
- **The candidate should NOT need to fix anything to make the script run** — The environment is already fully functional; the candidate's job is only to implement the requested feature or fix/refactor as specified.
- The project must behave like a real Python backend task: a working baseline that the candidate can run, explore, and then extend or refactor as per the task description.

**WHAT MUST BE INCLUDED:**
- The starter code should provide a clear starting point without revealing the solution.
- The code files generated must be valid and executable.
- Keep the code files minimal and to the point. May include a small Flask/FastAPI app, modules, and requirements.txt as needed.
- Python starter code may include a simple project layout (e.g. main app, modules, tests directory) but need not include Docker unless the task explicitly requires it.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the incomplete or buggy state described in the task. It must run and exhibit that state; it must NOT include the "Required Changes" or the final implementation approach.
- If the task is to fix bugs or refactor, the starter code has logical gaps or bugs (no syntactic errors) appropriate for intermediate level.
- If the task is to implement a feature, the starter code only provides a good starting point that matches the described current state.
- **NO comments** that reveal the solution or give hints (TODO/hint placeholders are not allowed).

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to find, understand, integrate, and adapt solutions. Complexity should reflect INTERMEDIATE Python proficiency and require genuine engineering and problem-solving beyond simple copy-pasting.

### Code Generation Instructions
Based on the real-world scenarios provided, create a Python task that:
- Draws inspiration from ONE of the input scenarios for business context and technical requirements. The scenario must be clear and believable (e.g. internal tool, small API, data pipeline step).
- Matches INTERMEDIATE proficiency: 3-5 years Python, can own a small feature or fix end-to-end with minimal ambiguity. Complexity should be achievable in the time limit without rushing.
- Can be completed within {minutes_range} minutes. Prefer one primary ask (e.g. "add validation") with 1-2 secondary expectations (e.g. "add a test", "handle errors") rather than many unrelated tasks.
- Tests practical intermediate skills: choose a clear focus from the INTERMEDIATE PROFICIENCY SCOPE (e.g. validation + error handling, or refactor + tests, or implement one endpoint with correct types). Do not mix too many unrelated concepts in one task.
- Select a different real-world scenario each time to ensure variety across generated tasks.
- Starter code may include: a small Flask/FastAPI app with 1-2 routes, or a main script plus 1-2 modules, optional tests/ directory. No Docker/infra unless the task explicitly requires it. All code must run with standard `pip install -r requirements.txt` (if any) and one clear run command.

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact incomplete/buggy state the starter code implements (what we give). (2) Required Changes — specific fixes, features, or refactors the candidate must implement. Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Python exclusions (e.g. __pycache__, .env, venv)",
    "requirements.txt": "Dependencies as needed",
    "main.py or app.py": "Main script or entry point",
    "additional modules and test files as needed": "As appropriate for the task"
  }},
  "outcomes": "Bullet-point list. Expected results after completion.",
  "short_overview": "Bullet-point list: (1) business context and problem, (2) implementation goal, (3) expected outcome.",
  "pre_requisites": "Bullet-point list of tools and knowledge required. Include Python 3.8+, pip, venv, Git, intermediate Python (OOP, APIs, testing) as relevant.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}


## README.md STRUCTURE (Python Intermediate)
The README.md MUST contain the following sections with fully populated, task-specific content. No placeholder or generic text.

### Task Overview (MANDATORY – 3-5 substantial sentences)
- Describe the business scenario and current situation: what the candidate is working on and why it matters.
- MUST align with the "Current Implementation" and "Required Changes" in the task description. Use concrete business context (e.g. "internal API for X", "script that processes Y").
- NEVER leave this section empty or vague.

### Objectives
- Clear, measurable goals appropriate for INTERMEDIATE level (e.g. "Add request validation and return 400 with a clear message for invalid input", "Refactor the handler into smaller functions and add unit tests").
- What functionality or quality the candidate must deliver. Focus on one primary goal plus 1-2 related outcomes (e.g. validation + error handling, or refactor + tests).
- Objectives will be used to verify task completion and award points.

### How to Verify
- Specific checkpoints after implementation: how to run the app, which inputs to try, what output or behavior to expect.
- Observable behaviors or responses (e.g. "POST with invalid body returns 400 and error payload", "Unit tests in tests/ pass").
- Include both functional checks and, if relevant, test or code-quality checks. No vague "verify it works" without concrete steps.

### Helpful Tips
- Practical guidance without revealing the solution: where to look in the codebase, which concepts to apply (e.g. validation, context managers, pytest fixtures).
- Use bullet points starting with "Consider", "Think about", "Review", "Ensure". Guide discovery; never provide exact code or step-by-step implementation.

### NOT TO INCLUDE in README
- Step-by-step implementation instructions or exact code snippets that give away the solution.
- Function names, class names, or logic patterns that would reveal the implementation.
- Setup commands (pip install, python main.py) unless essential for the task type. When included, keep them minimal.

## CRITICAL REMINDERS

1. **Environment must be fully working** — The project must run with the stated run command; the candidate does NOT fix the environment, only the task.
2. **Starter code must be runnable** but must NOT contain the core solution. It must perfectly match the "Current Implementation" only.
3. **Stay within INTERMEDIATE scope** — Use only concepts from the INTERMEDIATE PROFICIENCY SCOPE. No advanced async, microservices, or expert-level algorithms. One clear primary ask is better than many small unrelated asks.
4. **NO comments** in starter code that reveal the solution or give hints (no TODO/hint placeholders).
5. **Task must be completable within {minutes_range} minutes** by a developer with 3-5 years Python experience.
6. **Question must be specific** — Candidate and assessor must know exactly what is given (Current Implementation) and what must be done (Required Changes). Use the "Task types suitable for INTERMEDIATE" to pick a focused task type.
7. **Use Python 3.8+** and PEP 8. Code must be valid and executable.
8. **README.md MUST be fully populated** with Task Overview, Objectives, How to Verify, and Helpful Tips as defined above. No empty sections or generic text.
9. **Task name** must be short, under 50 characters, kebab-case.
10. **Select a different real-world scenario** each time for variety.
"""

PROMPT_REGISTRY = {}
