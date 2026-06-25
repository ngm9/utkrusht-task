# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Target Competencies:
{competencies}

Based on this information, could you summarize what you understand about the company and role requirements? Use this only to calibrate the seniority and expectations for the candidate. The employer's industry is not automatically the domain of the assessment task unless it clearly matches one of the real-world scenarios.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Production Agent Engineering assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION CALIBRATION SIGNAL:
{question_prompt}

SCENARIO FOCUS:
The candidate is a BASIC-level Production Agent Engineering practitioner who should work on a small but realistic local agent project that behaves like a production support task. The task must test practical understanding of what production AI agents are, how prompt instructions and tool schemas shape behavior, how basic guardrails and validations prevent bad actions, and how simple tests/logging are used to keep an agent safe and reliable.

The package they receive is always a LEAN local project, never a sprawling repository. This is a coding task, not an essay, memo, architecture review, or quiz. The candidate should be able to run the project locally with the runtime's native test command, inspect a small amount of starter code and tests, and complete 1-2 focused stubbed functions. The task should feel like a real issue an engineer would pick up after observing an agent making avoidable mistakes in a controlled environment.

The project should be shaped like a tiny production-adjacent agent app:
- a small agent module that builds prompts, validates tool inputs, or handles model outputs
- one or two stubbed functions that raise `NotImplementedError`
- realistic fixtures or sample transcripts/messages
- a native runtime manifest for the language
- a test suite that captures the required behavior
- a concise README that explains the business situation without revealing the implementation

WHAT THIS TASK TESTS:
- Understanding the difference between an agent and a simple one-shot LLM feature
- Ability to read a small agent flow and identify where tool-calling, prompt rules, or validation are missing
- Ability to implement basic guardrails such as input validation, confirmation gates, output parsing, fallback handling, or context trimming
- Ability to reason about safe tool usage, predictable outputs, and simple production reliability behaviors
- Ability to use evidence from tests and provided artifacts rather than hand-wavy agent theory
- Ability to keep the solution local, deterministic, and small in scope

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Makes a targeted fix in the correct place instead of rewriting the whole project
- Preserves the intended user-facing behavior while preventing unsafe or malformed actions
- Uses clear validation and failure handling rather than silent assumptions
- Keeps changes aligned with the provided tests and business context
- Demonstrates practical understanding of prompt constraints, tool boundaries, or agent control flow at a BASIC level
- Avoids over-engineering with large frameworks, distributed systems, or advanced orchestration that the task did not ask for

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Select a different real-world scenario each time to ensure variety in task generation
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task must be completable within {minutes_range} minutes for a BASIC Production Agent Engineering candidate
- The task MUST remain a pure local project with no external datastore, no docker-compose, and no infrastructure scripts
- The candidate should write or fix roughly 30-90 lines of code total across 1-2 files
- The project should use straightforward, production-relevant concepts such as prompt building, tool argument validation, confirmation before side effects, output parsing, retries/timeouts handling, fallback messaging, context trimming, or basic regression tests
- Do NOT turn this into a full multi-agent system, RAG platform, deployment task, CI/CD task, or observability platform
- Do NOT require real API keys, hosted LLM access, vector databases, message queues, or cloud resources
- Do NOT reveal the exact fix in the README, question, comments, or test names beyond what is necessary for a realistic engineering task
- The provided repository should be FULLY FUNCTIONAL as a local starter project, except for the intentionally incomplete or incorrect BASIC-level production agent behavior the candidate must fix

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? Describe the chosen scenario, the local agent behavior that is currently wrong, and the specific candidate deliverable at a BASIC proficiency level.
2. What will the task look like? Describe the local project files, which file(s) contain the candidate's main work, what tests or fixtures are provided, and how the candidate verifies the solution locally.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in production AI agents, you are given a list of real world scenarios and proficiency levels for Production Agent Engineering. Generate ONE realistic BASIC-level local coding assessment that tests whether a candidate can make a small AI-agent workflow safer, more reliable, and easier to validate in a production-like codebase. The task must feel like a real engineering work item, not a tutorial, quiz, or greenfield build.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is expected to understand what production AI agents are: LLM-driven, tool-using, automated systems with prompts, tool schemas, control flow, and operational safeguards. At BASIC level, they should work with a small local project that exposes one practical issue such as malformed agent output handling, missing tool-argument validation, accidental side effects without confirmation, simple fallback behavior, or context trimming. **CRITICAL**: keep the task inside BASIC scope. The candidate is not expected to build full orchestration platforms, advanced multi-agent systems, evaluation infrastructure, cloud deployment, or distributed retrieval systems.

The repository should be small, readable, and intentionally incomplete in one focused place. It should let a strong BASIC candidate diagnose the issue from the code, tests, and sample data, then implement a targeted fix without needing external services. The task should be completable in {minutes_range}.

## INSTRUCTIONS

### Nature of the Task
- Generate exactly ONE local, pure-runtime Production Agent Engineering task inspired by ONE selected real-world scenario from the provided input.
- The task must be a realistic bug-fix or completion task in a small agent-oriented codebase.
- **CRITICAL**: this is a coding task, not a design memo, essay, prompt-writing-only exercise, or system-design interview.
- **CRITICAL**: keep the repository lean. A good target is 6-9 files total.
- **CRITICAL**: the candidate should mainly edit 1-2 files and write or adjust a small amount of code, usually around 30-90 lines.
- The project must be FULLY FUNCTIONAL as a starter environment, except for the intentionally incomplete logic under test.
- Use concepts naturally derived from BASIC Production Agent Engineering scope, such as:
  - prompt instructions and output format constraints
  - simple tool schema validation
  - basic branching or confirmation before a side effect
  - output parsing and fallback behavior
  - timeouts, retries, or graceful error handling at a simple level
  - context trimming or simple state handling
  - lightweight logging or regression tests
- Do NOT require advanced architecture decisions as the main challenge.
- Do NOT require hosted model access, vector stores, queues, cloud accounts, Kubernetes, distributed tracing, or complex framework-specific knowledge.
- The task should preserve realistic production framing: a teammate reports that the agent is doing the wrong thing in some cases, and the candidate must fix it safely.
- The candidate-facing `question` should read like a real work request from a teammate or manager and describe symptoms, impact, and expected outcomes without naming the exact implementation steps.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Production Agent Engineering documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- They may use online documentation and reference materials
- They may use AI tools to help reason about the bug, write tests, or draft code
- They may use their IDE, debugger, and local tooling freely
- The assessment measures engineering judgment, safe behavior, and the ability to deliver a working fix in context, not memorization

## Code Generation Instructions
Generate a pure local repository using the runtime's native manifest and test command. Since this task is non-infra, the candidate must be able to run the project locally without Docker, containers, external services, or infrastructure provisioning.

Use a simple Python local project shape:
- `pyproject.toml` as the native manifest
- source files under a small package such as `agent_app/` or `src/agent_app/`
- tests under `tests/`
- optional fixture files under `fixtures/` or `data/`
- `README.md`
- optional `run.sh` only if it simply runs the local test command without any install or infrastructure steps; it is not required
- no external datastore configuration

The generated repository should typically contain:
- one working module that establishes context, prompt text, or helper logic
- one candidate-work module with a focused incomplete function or flawed behavior
- one or more tests that clearly capture the expected outcome
- one sample data or fixture file if it improves realism
- a README that explains the business problem but does not reveal the solution

The task should be deterministic and local:
- no live API calls
- no environment variables required
- no network dependencies
- no secrets
- no remote services

Candidate work should center on one of these BASIC-level patterns:
- validate tool-call arguments before executing a side effect
- require an explicit confirmation flag before a tool action is allowed
- parse and validate structured agent output before downstream use
- catch and handle a common model/provider-style error in a simple local simulation
- trim context/history to avoid oversized requests in a helper function
- route invalid or ambiguous cases to human review instead of failing hard

## Infrastructure Requirements

### Docker-compose Instructions
Because `task_shape` is `non_infra`, you MUST NOT generate `docker-compose.yml`. You MUST NOT include any version specification because you must not include docker-compose at all for this task. **CRITICAL**: this repository is a pure local runtime project.

### Local Runtime Instructions
- Do NOT generate `init_database.sql`
- Do NOT generate datastore configuration
- Do NOT generate container setup
- Do NOT require Redis, PostgreSQL, queues, brokers, or vector databases
- Use the runtime's native manifest and the native test command only
- For Python, the verification path should be through `pytest`
- The codebase should run as a normal local project from `/root/task`

### Run.sh Instructions
For this non-infra task, `run.sh` is optional. If you include it, it must only invoke the native local verification command and must not install packages, start services, or call Docker. A valid minimal example is running the project's test suite from `/root/task`. Do not rely on `run.sh` as the only way to verify the task; the README must still mention the native test command.

## kill.sh file instructions
Because `task_shape` is `non_infra`, DO NOT generate a `kill.sh` file. The canonical cleanup script used for containerized tasks does not apply here. **CRITICAL**: no docker cleanup, no volume cleanup, no image cleanup, and no `/root/task` deletion script should be present in `code_files`.

The output should be a valid json schema:
- `name`: A short kebab-case GitHub-style repository name under 50 characters describing the task. It must be different from `title`.
- `title`: A human-readable display name in "<action verb> <subject>" format, ideally 50-80 characters, describing the candidate's work item.
- `question`: The full candidate-facing task description written like a real work request, including symptoms, business impact, and the expected high-level outcome without revealing the exact implementation steps.
- `code_files`: An object mapping each repository file path to the complete contents that should be written into that file for the starter project.
- `answer`: Evaluator-facing high-level solution guidance describing the root cause, expected fix shape, and what a strong submission demonstrates without dumping the full solved repository.
- `definitions`: An object of term-to-definition pairs for domain or agent-related terminology used in the task so reviewers can interpret the assessment consistently.
- `hints`: A single line nudging investigation in the right direction without revealing the exact fix or naming the implementation directly.
- `outcomes`: Expected results after completion in 2-3 lines focusing on measurable behavior improvements and safer agent operation. Use simple english.
- `pre_requisites`: A bullet list of the tools, local commands, and baseline knowledge required to work on the repository.
- `short_overview`: A bullet list summarising the business problem, the technical focus of the task, and the expected outcome in concise plain language.

## Code file requirements
- The repository must be lean and realistic, typically 6-9 files.
- Include `pyproject.toml` for a Python task.
- Include actual runnable source code and actual test code; do not use placeholders like "implement here".
- If the candidate must write code in one function, that function should raise `NotImplementedError` or contain a realistic flawed implementation that the tests expose.
- Keep the code approachable for BASIC level. The candidate should not need to understand advanced frameworks or hidden metaprogramming.
- Tests should verify observable behavior rather than internal implementation details.
- Prefer one focused module such as:
  - `agent_app/handler.py`
  - `agent_app/validation.py`
  - `agent_app/parser.py`
  - `agent_app/context.py`
- If using fixtures, keep them small and realistic.
- The task must not include solution comments, hidden answers, or step-by-step fix instructions in code comments.
- The `question` must not directly tell candidates the function names to edit.
- All file contents must be fully populated. No empty files. No pseudo-files.
- Internal consistency matters: file names, tool names, sample messages, expected outputs, and README wording should all align.
- The business domain should come from the selected scenario, not automatically from the employer's industry.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` file appropriate for a small local Python project.
It should ignore common Python artifacts such as:
- `__pycache__/`
- `.pytest_cache/`
- `.venv/`
- `dist/`
- `build/`
- `.DS_Store`

Do not include unrelated heavy tooling ignores unless the generated repository actually uses them.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README must use EXACTLY these section names, in this order:

1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify
5. NOT TO INCLUDE in README

### Task Overview
- Write 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- This section must NEVER be empty.
- Do NOT include bold time-budget callouts.
- Frame the system as a real agent or agent-powered feature operating in a business workflow.

### Helpful Tips
- Provide 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with one of: `Consider`, `Think about`, `Explore`, `Review`, `Analyze`
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Keep tips focused on investigating control flow, validation boundaries, failure handling, prompt/output contracts, and verification behavior.

### Objectives
- Provide 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical implementations. Objectives describe the "what" and "why", never the "how".
- Each bullet must state an observable end-state, not an implementation step.
- Good objectives include safer behavior, valid structured outputs, avoided accidental side effects, graceful review routing, or stable local verification.

### How to Verify
- Provide 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run locally, such as test results, output shape, fallback behavior, or review-path behavior.
- Mention the native local test command for the runtime.

### NOT TO INCLUDE in README
The README must explicitly instruct the downstream generator not to include:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or similar
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Directive phrases like "you should implement", "add this middleware", "create this class", "use <specific API>"
- Database connection details, hostnames, ports, usernames, passwords, or client-tool suggestions
- `<DROPLET_IP>` placeholders or infrastructure-specific instructions

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A description telling the generator to produce a short kebab-case repository name under 50 characters for the task.",
  "title": "A description telling the generator to produce a human-readable action-oriented title different from name and suitable for display.",
  "question": "A description telling the generator to write the full candidate-facing work item in a realistic teammate tone, describing the issue, business impact, and expected outcome without revealing the implementation.",
  "code_files": "A description telling the generator to produce a flat object mapping every repository filepath to its complete file contents for a small local Python project with source code, tests, README, manifest, and supporting files.",
  "answer": "A description telling the generator to provide evaluator-facing high-level guidance covering the root cause, the expected fix shape, important tradeoffs, and what evidence in the repository supports the diagnosis.",
  "definitions": "A description telling the generator to provide an object of concise term-definition pairs for agent-related concepts, domain vocabulary, or task-specific terminology used in the repository.",
  "hints": "A description telling the generator to provide a single line hint that nudges the candidate toward the relevant control-flow or validation boundary without giving away the fix.",
  "outcomes": "A description telling the generator to summarize the expected results after completion in 2-3 lines with measurable, observable improvements in safety, reliability, or structured agent behavior.",
  "pre_requisites": "A description telling the generator to provide a bullet list of local tools and baseline knowledge needed to run and complete the task, using simple practical language.",
  "short_overview": "A description telling the generator to provide a concise bullet list summarizing the business problem, the technical focus area, and the expected end result of the task."
}}

## CRITICAL REMINDERS
- Output must be raw valid JSON only when generating the task payload — no markdown fences, no explanations, no extra keys.
- Use EXACTLY these top-level keys: `name`, `title`, `question`, `code_files`, `answer`, `definitions`, `hints`, `outcomes`, `pre_requisites`, `short_overview`.
- Because this is a non-infra task, `code_files` MUST NOT include `docker-compose.yml`, `init_database.sql`, or `kill.sh`.
- Keep the project pure local and runnable with Python's native manifest plus `pytest`.
- The task must be inspired by ONE provided real-world scenario and should closely align with that scenario's domain and technical issue.
- Keep the challenge within BASIC Production Agent Engineering scope: prompt rules, tool usage boundaries, simple control flow, basic guardrails, local testing, and practical reliability.
- Do NOT turn the task into a full framework showcase, advanced orchestration problem, cloud deployment exercise, or system-design essay.
- The repository should be FULLY POPULATED and internally consistent.
- The candidate should be able to infer the right fix from the code, tests, and business context rather than from explicit instructions.
- `question` should sound like a real teammate request and should not expose exact file names or exact function names the candidate must edit.
- Prefer small, high-signal starter repositories over large complex ones.
- If you simulate agent output or tool calls, keep them deterministic and local.
- Ensure the tests clearly capture the intended production-safe behavior, but do not leak the full answer in comments or names.
"""

PROMPT_REGISTRY = {
    "Production Agent Engineering (BASIC)": [
        PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_CONTEXT,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_INPUT_AND_ASK,
        PROMPT_PRODUCTION_AGENT_ENGINEERING_BASIC_INSTRUCTIONS,
    ]
}