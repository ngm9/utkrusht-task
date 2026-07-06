# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


PROMPT_MULTI_AGENT_SYSTEMS_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MULTI_AGENT_SYSTEMS_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a BASIC Multi-Agent Systems assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- For this run, the task MUST be based on the customer support triage CrewAI scenario where a ClassifierAgent should invoke a classify_ticket tool and a ResponderAgent should use the structured category returned by that tool
- The task MUST stay local and Python-native: do not include docker-compose.yml, Dockerfile, init_database.sql, datastore configuration, or external service containers

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the customer support triage domain, the CrewAI multi-agent context, and the tool-schema communication problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python CrewAI bug fix required, the expected deliverables, and how it aligns with BASIC Multi-Agent Systems proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python, CrewAI, LLM-agent orchestration, agent roles, tools, and basic multi-agent system design, you are given a list of real world scenarios and proficiency levels for Multi-Agent Systems.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at a basic level.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to understand basic Multi-Agent Systems concepts such as agent roles, autonomy, simple coordination, message schemas, tool use, and the difference between structured agent communication and unstructured plain text reasoning.
The candidate should be able to configure LLM-based agent roles and tools using an orchestration library, extend a simple agent workflow, wire up communication between agents, design simple tests, and diagnose basic failure modes in agent coordination.
The candidate is not expected to design advanced multi-agent planning, auctions, distributed consensus, multi-agent reinforcement learning, complex deployment infrastructure, or production-grade observability systems.
The generated task should assess whether the candidate can fix a small but realistic CrewAI support triage workflow where one agent must use a tool and another agent must consume the structured output of that tool.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to fix bugs in an existing Python CrewAI codebase for a customer support triage system.
- The task MUST use the following scenario: a customer support triage system uses a CrewAI multi-agent setup with two agents, a ClassifierAgent and a ResponderAgent.
- The ClassifierAgent reads an incoming customer message and decides the support category: billing, technical, or general.
- The ResponderAgent drafts an appropriate reply based on the category.
- **CRITICAL**: The ClassifierAgent has a classify_ticket tool defined in tools.py, but the tool schema is missing the category field in its return type annotation.
- **CRITICAL**: The classify_ticket tool implementation itself is correct and returns a structured result containing category and confidence, such as category values billing, technical, or general with a float confidence.
- **CRITICAL**: Because the schema declaration is incomplete, the ClassifierAgent falls back to reasoning in plain text instead of invoking the tool, and the ResponderAgent receives an unstructured string it cannot parse.
- **CRITICAL**: The candidate's task must include fixing the classify_ticket tool schema in tools.py so it correctly declares the category return field.
- **CRITICAL**: The candidate's task must include updating the ClassifierAgent task description in crew.py so it is explicitly instructed to use the classify_ticket tool rather than reason in plain text.
- **CRITICAL**: The candidate's task must include ensuring the ResponderAgent receives and uses the structured category from the tool output to select the correct response template.
- **CRITICAL**: The pytest suite must mock LLM calls using conftest.py fixtures so tests run without a real OpenAI key.
- Real runs may use OpenAI when OPENAI_API_KEY is provided through the local environment or a developer-created .env file, but the generated starter files MUST NOT include any real API key or secret value.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The task should provide a FULLY FUNCTIONAL local Python project structure and a FULLY POPULATED README, tests, and starter implementation, while intentionally preserving the logical bug that the candidate must diagnose and fix.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is only about syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level in Multi-Agent Systems, focusing on simple agent roles, tool configuration, message schemas, and handoff between agents.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenario must be easily digestible and focus on fundamental Multi-Agent Systems concepts like:
  - Understanding what an agent role is and why agents communicate through structured outputs
  - Configuring a simple LLM-based agent role in a CrewAI workflow
  - Understanding when an agent should invoke a tool instead of relying on free-form reasoning
  - Recognizing a basic message schema mismatch between agents
  - Passing structured output from one agent to another
  - Designing simple tests that verify expected task completion behavior
  - Handling a basic failure mode where unstructured messages cause downstream fallback behavior
  - Understanding why tool schemas matter for LLM-agent orchestration
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Python best practices and current CrewAI usage patterns for a small local project.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, CrewAI documentation, OpenAI documentation, Python documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Candidates may use AI assistance, but they are responsible for validating the final behavior with the provided tests and explaining the reasoning behind their changes.
- The generated task should require genuine problem-solving around agent roles, tool schemas, and structured communication, not just copy-pasting a generic CrewAI example.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Python CrewAI Multi-Agent Systems task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements.
- Uses the customer support triage CrewAI scenario described above as the concrete basis for this run.
- Matches the complexity level appropriate for BASIC proficiency level in Multi-Agent Systems, keeping in mind that AI assistance is allowed.
- Tests practical Multi-Agent Systems skills that require more than a simple AI query to solve, focusing on fundamental agent-tool configuration and structured inter-agent communication.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation, unless a specific scenario is explicitly required for this run.
- Focus on a small local Python project with two agents, one tool, deterministic response templates, and a pytest suite.
- The task MUST NOT include docker-compose.yml, Dockerfile, init_database.sql, datastore configuration, database containers, cache containers, queues, brokers, or any other infrastructure service.
- The generated project MUST be runnable with Python's native tooling and tests MUST run with `python -m pytest`.
- Include a Python package manifest such as pyproject.toml with the dependencies needed for a local CrewAI project and pytest-based tests.
- Do not include `apt-get install`, `pip install`, `npm install`, or any runtime installation commands in code files or scripts.
- The starter project may include a run.sh only if it simply runs the native local test command from /root/task; it must not start containers or install dependencies.
- The code may support real OpenAI-backed runs when OPENAI_API_KEY is supplied by the user, but tests must not require a real key because LLM calls are mocked.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pyproject.toml (Python project manifest with CrewAI, pytest, and any lightweight local dependencies needed for the starter project)
  - .gitignore (Standard Python, pytest, virtual environment, cache, IDE, and local secret exclusions)
  - src/support_triage/__init__.py (Python package marker)
  - src/support_triage/tools.py (Starter classify_ticket tool with a logical schema declaration bug and a correct implementation body)
  - src/support_triage/crew.py (Starter CrewAI workflow with ClassifierAgent and ResponderAgent wiring that requires the candidate to fix task instructions and structured handoff)
  - src/support_triage/responder.py (Response template selection logic that should use the structured category and currently demonstrates the fallback problem)
  - src/support_triage/models.py (Simple typed structures or enums needed by the starter project, without giving away the complete fix)
  - src/support_triage/main.py (Small local entry point for optional manual runs)
  - tests/conftest.py (pytest fixtures that mock LLM calls so tests run without a real OpenAI key)
  - tests/test_support_triage.py (billing and technical ticket tests that fail until the candidate fixes schema declaration, tool invocation instruction, and structured response handling)
  - run.sh (Optional local helper script that changes to /root/task and runs python -m pytest; omit it if not needed)
  - Any additional Python source files that are necessary for a runnable local project, but do not include the solution

## Code file requirements
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Python best practices and simple CrewAI conventions.
- Use a clean package structure under /root/task/src/support_triage and tests under /root/task/tests.
- Include pyproject.toml as the native Python manifest.
- Include pytest tests that can be run with `python -m pytest`.
- Include conftest.py fixtures that mock LLM calls or CrewAI execution paths so no real OpenAI API key is required during tests.
- Real manual runs may read OPENAI_API_KEY from the local environment or from a developer-created .env file, but starter files must not contain a real key.
- **MUST NOT include any version specification** in docker-compose because docker-compose.yml must not be generated at all for this non-infrastructure task.
- **MUST NOT include environment variables or .env file references** in any Docker or datastore configuration because no Docker or datastore configuration should be generated.
- Do not include docker-compose.yml, Dockerfile, init_database.sql, database configuration, Redis configuration, message broker configuration, or container orchestration files.
- **CRITICAL**: The generated code files MUST NOT contain the completed implementation for the core logic of the task.
- **CRITICAL**: The classify_ticket tool implementation body may be correct, but its schema or return type declaration should intentionally contain the logical bug described in the task so the candidate has something meaningful to fix.
- **CRITICAL**: The starter crew.py should contain enough structure to show the ClassifierAgent and ResponderAgent workflow, but should leave the candidate responsible for correcting the classifier task instruction and structured category handoff.
- The ResponderAgent or response selection code should contain a generic fallback behavior that makes the bug observable in tests.
- The billing ticket test and technical ticket test must fail before the candidate fixes the task and pass after the expected fixes.
- The tests should assert observable outcomes, such as billing-specific and technical-specific response content, and should make it possible to infer whether the structured category was used.
- The code should be valid Python with no syntax errors.
- Keep the code files minimal and to the point.
- If the task is to fix bugs, make sure the starter code has logical bugs that are substantial enough to test BASIC Multi-Agent Systems proficiency.
- DO NOT include any 'TODO' or placeholder comments.
- DO NOT include any comments that give away hints or solutions.
- DO NOT include comments like "Add logic here" or "Should implement business logic" etc.
- DO NOT add comments that give away hints or solution or implementation details.
- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file that covers all standard exclusions for Python projects including __pycache__ directories, .pytest_cache, .mypy_cache, .ruff_cache, virtual environments, build artifacts, coverage files, IDE configurations, log files, and local secret files such as .env. Do not include any real secret values anywhere in the generated task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content.
Task Overview section MUST contain the customer support triage business scenario from the task description.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific CrewAI multi-agent support triage task scenario being generated.
Use concrete business context, not generic descriptions.
The README should NOT contain setup commands, install commands, database connection details, Docker commands, or solution-revealing implementation details.

### Task Overview
- Task Overview must be 3-4 meaningful sentences. No bullet list.
- It must describe the business scenario, current state, and why the problem matters.
- It must explain that customer support messages should be categorized before a response is drafted, and that the current workflow produces generic replies because the agent handoff is not structured correctly.
- NEVER generate empty content and never use generic filler text.
- Do not include bold time-budget callouts.

### Objectives
- Objectives must be 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: 'Fix the tool schema.'
- GOOD: 'Support tickets that clearly describe billing or technical issues currently receive the same generic response; after your changes, each ticket should receive a reply that reflects the category identified by the classifier.'
- Objectives should remain appropriate for BASIC Multi-Agent Systems proficiency and focus on tool use, structured category handoff, response selection, and test validation.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Do NOT specify exact implementation approaches, method signatures, class internals, schema syntax, or code snippets.
- Good tips should guide the candidate to inspect how the classifier communicates results, how the responder interprets the handoff, and how mocked tests describe the desired behavior.

### How to Verify
- How to Verify must be 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run, such as test output, response shape, category-specific reply content, mocked call behavior, or optional manual run behavior.
- Include verification that `python -m pytest` passes and that the billing and technical ticket tests produce category-specific responses.
- Include verification that tests run without a real OpenAI API key because LLM calls are mocked.
- If mentioning real manual runs, state only that they can work when the user supplies their own OpenAI credentials locally; do not include keys or secret values.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
- Setup commands such as `pip install`, `python -m pytest`, `docker compose up`, `npm install`, `mvn test`, or similar commands as instructional setup steps. The How to Verify section may mention the observable test command only as a verification check, not as a setup guide.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, schema syntax, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Exact class implementation details that would give away the solution to the task.
- Phrases like "you should implement", "add this middleware", "create this class", "use a specific API", "fix the return annotation by adding this field", or any equivalent directive that reveals the answer.
- Docker, docker-compose, database connection details, hostnames, ports, usernames, passwords, client-tool suggestions, or datastore setup instructions.
- Any real OpenAI API key, fake key that looks real, or secret value.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Kebab-case GitHub repo name under 50 characters that clearly identifies the CrewAI support triage task without duplicating the human-readable title.",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, such as a concise phrase describing the candidate action and the multi-agent support triage subject.",
  "question": "Full candidate-facing task description that explains the customer support triage scenario, the broken ClassifierAgent to ResponderAgent flow, the expected category-specific behavior, the mocked pytest validation, and the requirement to keep the project local and Python-native without revealing the exact code solution.",
  "code_files": {{
    "README.md": "Candidate-facing README following exactly the required Task Overview, Objectives, Helpful Tips, and How to Verify sections with concise open-ended guidance.",
    ".gitignore": "Comprehensive Python gitignore covering caches, virtual environments, build artifacts, coverage files, IDE files, logs, and local secret files such as .env.",
    "pyproject.toml": "Python project manifest for the local CrewAI support triage package including pytest configuration and only the dependencies needed for the starter project.",
    "src/support_triage/__init__.py": "Package initialization file for the support_triage source package.",
    "src/support_triage/models.py": "Simple typed model definitions used by the starter workflow to represent support ticket inputs and classification-related values without giving away the complete fix.",
    "src/support_triage/tools.py": "Starter classify_ticket tool file containing the correct categorization implementation body but an intentionally incomplete schema or return declaration that the candidate must diagnose and fix.",
    "src/support_triage/crew.py": "Starter CrewAI workflow defining the ClassifierAgent and ResponderAgent task wiring with enough structure for the candidate to correct tool usage instructions and structured handoff.",
    "src/support_triage/responder.py": "Response selection module that demonstrates the current generic fallback and is intended to use the structured category once the candidate fixes the flow.",
    "src/support_triage/main.py": "Small optional local entry point for manually running the support triage workflow with user-provided local credentials when available.",
    "tests/conftest.py": "Pytest fixture file that mocks CrewAI or LLM interactions so the tests run deterministically without a real OpenAI API key.",
    "tests/test_support_triage.py": "Pytest test suite with billing and technical ticket scenarios that fail against the starter bug and pass when the classifier tool output and responder handoff work correctly.",
    "run.sh": "Optional local helper script that uses /root/task as the base directory and runs the native Python test command without installing packages or starting any external infrastructure."
  }},
  "answer": "Evaluator-facing high-level solution approach describing that the correct fix is to align the tool's declared structured output with its actual category and confidence result, make the classifier task require tool invocation, and ensure the responder consumes the structured category for template selection while preserving mocked test behavior.",
  "definitions": "Object of Multi-Agent Systems term to definition pairs covering concepts such as Agent, Tool, Message Schema, Structured Output, Agent Handoff, Mocked LLM Call, and Fallback Response, with clear BASIC-level definitions relevant to the task.",
  "hints": "A single line nudging the candidate to compare the classifier's declared communication contract with what the responder expects, without revealing the exact schema or code change.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable category-specific replies, reliable structured agent handoff, passing mocked pytest tests, and clean maintainable Python code.",
  "pre_requisites": "Bullet list of tools and knowledge needed, including Python basics, pytest, basic CrewAI or LLM-agent orchestration familiarity, simple type annotations or schemas, and understanding of agent roles and structured communication.",
  "short_overview": "Bullet list summarising the customer support business problem, the Multi-Agent Systems technical focus on tool-based classification and responder handoff, and the expected outcome of category-specific replies validated by tests."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **name** must be short, descriptive, kebab-case, and under 50 characters.
3. **title** must be in `<action verb> <subject>` format, 50-80 characters, and different from `name` — name is kebab-case for GitHub repo, title is human-readable for display.
4. **code_files** must include README.md, .gitignore, pyproject.toml, Python source files, and pytest files for the local CrewAI support triage project.
5. **Do not include docker-compose.yml, Dockerfile, init_database.sql, datastore configuration, database services, Redis services, queues, brokers, or any container infrastructure.**
6. **README.md** must follow exactly the four required sections in this order: Task Overview, Objectives, Helpful Tips, How to Verify.
7. **README.md** must be concise and open-ended and must not include direct solutions, step-by-step implementation instructions, or solution-revealing API/schema details.
8. **Starter code** must be runnable locally with Python tooling and tests must run with `python -m pytest`, but the starter code must NOT contain the completed solution.
9. **The intended bug must be logical, not syntactic**: the project should import and tests should execute, but billing and technical behavior should fail until the candidate fixes the structured tool/agent handoff.
10. **The classify_ticket implementation body should be correct**, while the schema or return declaration should be incomplete enough to cause the ClassifierAgent to avoid or fail structured tool use.
11. **The ClassifierAgent task description in starter code should be incomplete enough that the candidate must make tool use explicit**, but do not reveal the exact corrected wording.
12. **The ResponderAgent flow should make the generic fallback observable** until it receives and uses the structured category.
13. **Tests must mock real LLM calls** so the pytest suite works without OPENAI_API_KEY.
14. **Real manual runs may work with a user-provided OpenAI key**, but no generated file may contain a real secret value.
15. **outcomes** must include clear measurable results and should mention clean, maintainable Python code with appropriate naming, small functions, and understandable error handling.
16. **short_overview** and **pre_requisites** must be bullet-point lists in simple language.
17. **hints** must be a single line and must not reveal the exact fix.
18. **definitions** must include relevant BASIC Multi-Agent Systems terms tied to this task.
19. **Task must be completable within {minutes_range} minutes** for BASIC Multi-Agent Systems proficiency.
20. **NO comments in code** that reveal the solution or give hints.
"""

PROMPT_REGISTRY = {
    "Multi-Agent Systems (BASIC)": [
        PROMPT_MULTI_AGENT_SYSTEMS_CONTEXT_BASIC,
        PROMPT_MULTI_AGENT_SYSTEMS_INPUT_AND_ASK_BASIC,
        PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INSTRUCTIONS,
    ],
}