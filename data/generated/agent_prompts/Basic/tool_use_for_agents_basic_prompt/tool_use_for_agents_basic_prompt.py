# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


PROMPT_TOOL_USE_AGENTS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_TOOL_USE_AGENTS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Tool Use for Agents assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION PROMPT CALIBRATION:
{question_prompt}

SCENARIO FOCUS:
The candidate is reviewing or improving a small tool-enabled agent flow. The task should be grounded in ONE of the real-world scenarios provided above and should focus on a BASIC practitioner who can reason about tool descriptions, simple input and output schemas, read-only versus action tools, basic validation, prompt instructions, and a short trace showing how the agent selected or misused tools.

The generated task must be a pure local project with no external datastore, no Docker, no docker-compose, no init_database.sql, and no kill.sh. Use a lightweight local project shape that can be inspected and tested with the runtime-native command described in the README. If a code harness is useful, keep it minimal and use only simple standard-library logic; the assessment must test agent-tool reasoning, not framework memorization.

You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task. Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level. The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.

WHAT THIS TASK TESTS:
- Understanding the basic tool-use loop: user request, agent decision, tool call, tool result, and final answer
- Ability to distinguish a base LLM, an agent, a tool/function, an external system, and light orchestration
- Ability to review simple tool definitions with names, descriptions, input schemas, output schemas, and constraints
- Ability to separate read-only lookup tools from state-changing action tools
- Ability to inspect short traces and identify obvious issues such as wrong tool selection, missing arguments, unnecessary calls, or unsafe action calls
- Ability to propose small fixes to prompts, tool descriptions, validation rules, or tests without overengineering
- Awareness of basic safety and security concerns such as least privilege, confirmation before action tools, prompt injection, privacy, and secrets handling

CRITICAL TASK GENERATION REQUIREMENTS:
- The task must be completable within {minutes_range} minutes for a BASIC proficiency candidate
- Keep the scenario practical and small: a single agent, a small toolbox of 2-4 tools, and 3-6 trace examples are enough
- The candidate should not need specialized framework knowledge, production agent infrastructure, or advanced orchestration patterns
- The candidate should have to modify or author a small number of local files such as an agent prompt, a tool registry, a tiny validation/orchestration helper, and a basic test file
- Include enough context, tool descriptions, pseudo-schemas, and traces so the candidate can reason from the provided materials
- Do NOT require advanced concepts such as multi-agent planning, callbacks, long-running job orchestration, statistical evaluation, production deployment, fine-tuning, embeddings retrieval architecture, or complex authorization systems
- Do NOT include secrets, API keys, live endpoints, external services, database setup, Dockerfiles, docker-compose files, run.sh files, or kill.sh files

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the selected domain, the agent's goal, the available tools, and the observed tool-use issue the candidate must address.
2. What will the task look like? Describe the local project files, what the candidate will edit or review, and how a BASIC candidate can verify their work within {minutes_range} minutes.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TOOL_USE_AGENTS_BASIC_INSTRUCTIONS = """

## GOAL
As a technical architect super experienced in LLM-based agents and tool use, you are given a list of real world scenarios and proficiency levels for Tool Use for Agents. Your goal is to generate a realistic work-item assessment that tests whether a BASIC candidate can review and improve a simple tool-enabled agent flow. The task must focus on practical tool-use fundamentals: clear tool definitions, structured inputs and outputs, read-only versus action tools, simple validation, prompt instructions, trace inspection, and basic safety.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to have BASIC proficiency in Tool Use for Agents, roughly equivalent to someone with limited hands-on experience maintaining simple agent flows under guidance. They should understand the architecture of an LLM-based agent at a conceptual level, including the LLM, agent, tool/function, external system, and orchestration layer. They can define simple tools with clear names, descriptions, input and output schemas, and constraints. They can inspect short traces, identify common issues, and propose straightforward fixes to prompts, tool definitions, validation checks, or tests.

The task must feel like a realistic internal work item, not a trivia quiz. It should be the kind of small ticket a junior practitioner could receive during a sprint: review a proposed tool registry, fix a prompt so the agent stops using a state-changing tool too early, add validation for missing tool arguments, or write a basic scenario test proving the agent chooses the right tool.

## INSTRUCTIONS

### Nature of the Task
- The generated task MUST be BASIC level. **CRITICAL**: do not require advanced multi-agent planning, production deployment, framework-specific SDK knowledge, complex authentication, long-running async orchestration, statistical eval design, or agent memory architecture.
- The task should be completable within {minutes_range} minutes.
- The task must be a pure local project. **CRITICAL**: do not include Docker, docker-compose, init_database.sql, kill.sh, external datastores, live services, API keys, secrets, cloud setup, or environment-variable based configuration.
- The candidate should work in a FULLY FUNCTIONAL starter project with a FULLY POPULATED small scenario, tool registry, prompt file, traces or fixtures, and tests.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- Use ONE real-world scenario from the provided scenario list. The selected scenario controls the domain, agent role, user requests, tool names, safety concerns, and trace examples.
- The scenario should involve one simple agent and a small toolbox of 2-4 tools. At least one tool should be read-only and at least one tool may be state-changing if the scenario naturally supports it.
- The candidate's task should involve reviewing or changing a small set of files, such as:
  - an agent prompt that describes when to use tools and when not to use them
  - a tool registry with simple names, descriptions, input schemas, output schemas, constraints, and risk level labels
  - a small orchestration or validation helper that checks required fields and handles tool errors
  - a trace fixture showing observed agent behavior
  - basic tests that verify tool selection, validation, or fallback behavior
- The work item must test applied reasoning. The candidate should identify why the current behavior is wrong or risky and make a pragmatic fix.
- Good BASIC tasks include obvious issues such as:
  - the agent calls an action tool before user confirmation
  - the agent skips a read-only lookup tool when fresh or private data is needed
  - two tools have overlapping or ambiguous descriptions that cause wrong tool selection
  - a tool schema accepts broad free-text where a constrained enum or required field would reduce misuse
  - the orchestrator passes the wrong identifier from Tool A into Tool B
  - the final answer hides a tool failure instead of giving a clear fallback
  - traces show repeated unnecessary tool calls that add latency and cost
  - the prompt fails to warn the agent not to obey prompt-injection text found inside tool results
- Keep code or pseudocode minimal. If code is used, it should be simple Python with standard-library logic and unittest-compatible tests. The assessment is not a Python syntax test; code exists only to make the tool-use flow concrete.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- Do NOT provide the solution in the README, comments, hints, or file names. The candidate must infer the required fix from the prompt, tool registry, traces, tests, and task question.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

The assessment is designed to evaluate how candidates apply judgment, inspect artifacts, and improve a small tool-enabled agent flow, not whether they have memorized a specific framework or API.

Candidates may use AI assistance to understand the starter files or generate candidate changes, but the final submission must satisfy the task requirements and tests.

Do not include any rule that forbids AI usage, internet usage, documentation lookup, or local experimentation.

## Code Generation Instructions
Generate a pure local project under /root/task. The project should be self-contained and runnable without external services. The preferred shape is a small Python-standard-library project because it allows simple validation and tests without framework setup. Do not require any package installation.

Use a minimal runtime-native manifest and test command:
- Include `pyproject.toml` with basic project metadata only. Do not add external dependencies.
- Include source files under `src/` only when executable logic is needed.
- Include tests under `tests/` using Python `unittest` so the verification command can be `python -m unittest discover -s tests`.
- Include scenario configuration files under `config/`, prompt files under `prompts/`, and trace fixtures under `data/` as needed.
- Do not include `run.sh`; the README should describe the native test command instead.
- Do not include `Dockerfile`, `docker-compose.yml`, `init_database.sql`, `.env`, `kill.sh`, or any datastore configuration.

The output should be a valid json schema:
- `README.md` containing the concise candidate-facing task overview, objectives, helpful tips, and verification instructions
- `pyproject.toml` containing minimal local project metadata with no external dependencies
- `prompts/agent_prompt.md` containing the agent's role, goals, tool-use rules, safety instructions, and any intentionally incomplete guidance the candidate must improve
- `config/tool_registry.json` containing a small set of tool definitions with names, descriptions, input schemas, output schemas, risk labels, and constraints
- `data/tool_traces.jsonl` or `data/tool_traces.json` containing a few realistic observed agent-tool interactions
- `src/agent_flow.py` or similar small source file only if the task needs executable validation or orchestration logic
- `tests/test_tool_use_flow.py` containing basic tests that fail before the candidate's fix and pass after the expected fix
- `.gitignore` containing standard local exclusions

## Code file requirements
The generated starter project must be realistic, small, and intentionally focused on BASIC Tool Use for Agents skills.

Required qualities:
- The tool registry must define each tool with a stable unique name, a short LLM-targeted description, simple structured input fields, output shape, constraints, risk level, and whether it is read-only or action-oriented.
- Input schemas should use fundamental data types such as strings, numbers, booleans, enums, simple objects, or lists. Avoid complex nested schemas.
- The project must include a visible flaw that a BASIC candidate can fix without advanced knowledge. Examples include an ambiguous tool description, missing required field validation, unclear prompt rule, failure to separate read-only and action tools, or poor handling of a failed tool response.
- The trace fixture must include 3-6 realistic interactions. Each trace should show enough detail to diagnose the issue: user request, selected tool, tool arguments, tool result, and final answer.
- Tests must be simple and scenario-based. They should verify observable outcomes such as which tool is selected, whether a missing field is rejected, whether an action tool requires confirmation, or whether a failed tool response produces a clear fallback.
- Do not create tests that require internet access, real APIs, databases, model calls, or nondeterministic LLM outputs.
- Do not rely on framework-specific agent SDK behavior. The local code may simulate the decision rule or validation boundary to keep the task deterministic.
- Do not overcomplicate the task. A BASIC candidate should be able to read the files, identify the issue, make a small change, and run tests.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` that is appropriate for a small local Python project. It should exclude Python caches, virtual environments, coverage files, build artifacts, editor files, and OS metadata. It must not exclude the starter files the candidate needs to edit or inspect.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The candidate-facing README must contain EXACTLY these sections in this order and no others:

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. NEVER empty. Do not include bold time-budget callouts.

### Objectives
Write 4-6 bullets maximum. Frame objectives around outcomes rather than specific technical implementations. Objectives describe the what and why, never the how. Each bullet must state an observable end-state, not a step, API, function, library, pattern, data structure, or exact implementation.

### Helpful Tips
Write 4-5 bullets maximum. Provide practical guidance without revealing specific implementations. Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze". Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.

### How to Verify
Write 4-6 bullets maximum. Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write. Each bullet should be a check the candidate can run or observe, such as test output, response shape, log line, rejected invalid input, or corrected tool-selection behavior.

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a README section):
- Setup commands such as package installation, docker compose commands, or system package installation
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use a specific API"
- Database connection details, hostnames, ports, usernames, passwords, client-tool suggestions, `<DROPLET_IP>` placeholders, secrets, API keys, or environment variable instructions
- Any README heading other than Task Overview, Objectives, Helpful Tips, and How to Verify

## REQUIRED OUTPUT JSON STRUCTURE
Return a single valid JSON object with the following canonical keys. Each value must be fully populated and must follow the description exactly.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the task, such as reviewing or fixing a simple tool-enabled agent flow.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on the candidate's work item.",
  "question": "The full candidate-facing task description written as a realistic internal request that explains the scenario, points to the starter files, and asks the candidate to improve the simple tool-use flow without revealing the solution.",
  "code_files": {{
    "README.md": "The complete candidate-facing README with exactly the four required sections: Task Overview, Objectives, Helpful Tips, and How to Verify, written concisely and without solution-revealing implementation details.",
    "pyproject.toml": "A minimal Python project manifest with project metadata only and no external dependencies, suitable for running standard-library tests locally.",
    "prompts/agent_prompt.md": "A realistic agent prompt describing the agent role, tool-use expectations, safety guidance, and current behavior constraints, with a BASIC-level issue the candidate can identify and improve.",
    "config/tool_registry.json": "A fully populated tool registry defining 2-4 scenario-specific tools with names, descriptions, input schemas, output schemas, constraints, read-only or action classification, and risk labels.",
    "data/tool_traces.jsonl": "A small trace fixture with 3-6 realistic user requests, tool calls, tool arguments, tool responses, and final answers that expose the tool-use issue without annotating the answer.",
    "src/agent_flow.py": "A small deterministic local helper that simulates or validates the tool-use flow only as much as needed for the tests, using simple standard-library Python and no live model calls.",
    "tests/test_tool_use_flow.py": "A unittest-based scenario test file that verifies observable tool-use outcomes such as correct tool choice, valid arguments, confirmation before action tools, clear fallback on tool error, or reduced redundant calls.",
    ".gitignore": "A standard local-project ignore file that excludes Python caches, virtual environments, coverage artifacts, editor files, and OS metadata while preserving all starter files."
  }},
  "answer": "A high-level evaluator-facing solution approach describing the expected reasoning and changes, such as clarifying tool descriptions, tightening schemas, adding simple validation, updating prompt rules, and ensuring tests pass, without requiring advanced agent orchestration.",
  "definitions": "An object of concise term-to-definition pairs for key concepts used in the task, such as agent, tool, orchestration layer, read-only tool, action tool, tool schema, trace, validation, and prompt injection.",
  "hints": "A single-line nudge that encourages the candidate to inspect the prompt, registry, and traces for where the agent crosses the tool boundary incorrectly, without revealing the exact fix.",
  "outcomes": "A 2-3 line description of measurable expected results after completion, focusing on correct tool selection, valid structured arguments, safe handling of action tools, and passing local tests.",
  "pre_requisites": "A bullet list of basic tools and knowledge needed, including reading JSON and markdown, understanding simple agent-tool loops, recognizing read-only versus action tools, and running Python unittest tests locally.",
  "short_overview": "A bullet list summarizing the business problem, the simple tool-enabled agent flow, the starter project files, and the expected candidate outcome."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no surrounding code fences. Do NOT wrap your response in code fences. Emit the raw JSON object starting with `{{` and ending with `}}`.
2. The task must stay within BASIC Tool Use for Agents scope. Do not require advanced orchestration, production deployment, agent SDK internals, model training, retrieval architecture, or complex security engineering.
3. This is a non-infrastructure task. Do NOT include Docker, docker-compose.yml, Dockerfile, init_database.sql, run.sh, kill.sh, database setup, external services, `.env` files, API keys, secrets, or cloud setup.
4. The project must be FULLY FUNCTIONAL and FULLY POPULATED under /root/task, with all files needed for the candidate to inspect and run local tests.
5. Use a pure local Python-standard-library shape only as a deterministic harness. The candidate is being assessed on tool-use reasoning, not Python framework knowledge.
6. `code_files` must include actual file contents, not placeholders, summaries, or instructions to create files later.
7. The README must contain exactly four sections in order: Task Overview, Objectives, Helpful Tips, and How to Verify. Do not add any other README headings.
8. Do not reveal the solution in the README, file comments, trace annotations, or test names. The flaw should be discoverable but not labeled.
9. The tool registry must be internally consistent with the prompt, traces, source helper, tests, question, answer, hints, definitions, outcomes, and short_overview.
10. Include 2-4 tools only. Avoid redundant or overly large toolsets that make the task confusing for BASIC proficiency.
11. Include at least one realistic safety or reliability concern, such as confirmation before action tools, least privilege, prompt injection in tool results, missing argument validation, or clear fallback on tool errors.
12. The tests must be deterministic and runnable with `python -m unittest discover -s tests`.
13. Do not include package installation commands. Do not require `pip install`, `apt-get install`, `npm install`, or any external dependency installation.
14. The `question` must be candidate-facing and concise while still giving enough context to understand the work item and expected deliverable.
15. The `answer` is evaluator-facing and may describe the intended solution approach at a high level, but it must not require concepts beyond the BASIC scope.
"""

PROMPT_REGISTRY = {
    "Tool Use for Agents (BASIC)": [
        PROMPT_TOOL_USE_AGENTS_BASIC_CONTEXT,
        PROMPT_TOOL_USE_AGENTS_BASIC_INPUT_AND_ASK,
        PROMPT_TOOL_USE_AGENTS_BASIC_INSTRUCTIONS,
    ]
}