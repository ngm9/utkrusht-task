# task_generation_prompts/Basic/multi_agent_systems_basic_prompt.py
#
# CURATED task-generation prompt module for Multi-Agent Systems BUILD-IT tasks.
# Competency: "Multi-Agent Systems"  ·  Proficiency: BASIC
#
# DROP-IN for infra/utils.py::_build_prompt_registry. The loader filesystem-walks
# task_generation_prompts/<Level>/<slug>.py and calls registry.update(PROMPT_REGISTRY).
# Contract (do NOT change without updating the loader):
#   * Export a top-level dict named exactly  PROMPT_REGISTRY.
#   * Key it exactly "Multi-Agent Systems (BASIC)" — the
#     "<name> (<PROFICIENCY-UPPER>)" string get_task_prompt_by_technology_stack builds.
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal {placeholders} are the six fmt_args keys:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.

PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Multi-Agent Systems assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

{question_prompt}

════════════════════════════════════════════════════════
HARD RULES — read every rule before generating anything.
These rules are non-negotiable and override any default behaviour.
════════════════════════════════════════════════════════

RULE 0 — SCENARIO IS AUTHORITATIVE (most important rule):
The real-world scenario above describes the EXACT system, framework, and bug to implement.
You MUST implement what the scenario describes:
  • Same LLM framework (CrewAI if the scenario says CrewAI; LangChain if it says LangChain)
  • Same bug (if the scenario describes a missing tool return field, implement THAT bug)
  • Same agent roles and names (ClassifierAgent/ResponderAgent if that is what the scenario says)
Do NOT substitute a different bug to avoid overlap with existing task titles. Existing task
titles show surface topic similarity — they do NOT mean the scenario's specific bug is the
same. Implement the scenario exactly as written.

RULE 1 — LLM-BASED AGENTS ONLY:
The task MUST use an LLM-powered agent framework. Choose exactly ONE:
  • LangChain (AgentExecutor / tool-calling agents)
  • CrewAI (Crew + Agent + Task)
  • AutoGen (AssistantAgent / UserProxyAgent)
Do NOT generate tasks with rule-based agents, plain HTTP coordinators,
Redis-backed message queues, or any system where agents do not make LLM calls.
There must be at least one real LLM API call inside an agent's logic.

RULE 2 — TASK SHAPE (pick exactly ONE):
  SHAPE A — BROKEN TOOL SCHEMA:
    An agent has a tool defined with a missing or incorrectly typed field
    in the schema (e.g., return type wrong, parameter name mismatch, or
    required field absent). The agent falls back to plain text instead of
    invoking the tool. Fix: correct the schema and update the agent's
    task/system description to explicitly use the tool.

  SHAPE B — WRONG AGENT ROUTING:
    A supervisor or router agent sends tasks to the wrong specialist agent
    because a condition is wrong or a branch is missing. Fix: correct the
    routing condition so each task type reaches the right agent.

  SHAPE C — MEMORY NOT PASSED:
    An agent loses structured output between steps because it writes to a
    local variable instead of shared crew/agent memory or the correct
    output field. The next agent in the chain receives None or an empty
    value. Fix: correct how the output is stored and passed downstream.

  SHAPE D — AGENT LOOP NOT TERMINATING:
    An agent keeps re-calling the same tool (loops) instead of returning a
    final answer because the stopping condition (max_iter, is_last_step
    check, or return_direct flag) is missing or wrong. Fix: add or correct
    the stopping/return condition.

RULE 3 — INFRASTRUCTURE:
  • Python only.
  • Framework: LangChain, CrewAI, or AutoGen — chosen consistently for the whole task.
    pyproject.toml or requirements.txt MUST list crewai, langchain, or pyautogen as
    the primary dependency. Do NOT list redis, fakeredis, or any message-broker package.
  • Tests: pytest with mocked LLM responses (unittest.mock or pytest-mock).
    Tests MUST run without a real API key.
  • No Redis, no Docker, no docker-compose.yml, no Dockerfile, no HTTP inter-agent calls,
    no message brokers, no run.sh that starts Docker services.
  • Keep the full codebase the candidate must read under 300 lines.

RULE 4 — FIX SIZE:
  The fix must be 20–50 lines of changes maximum. The candidate is NOT
  asked to design agents from scratch — only to find and fix one specific
  broken behaviour in an existing agent setup.

RULE 5 — TESTS:
  Include exactly 2 pytest tests that are failing (or incomplete) before
  the fix and pass after. Tests use mocked LLM responses — no live API calls.

RULE 6 — DOMAIN:
  Use a realistic business domain drawn from the real-world scenarios above
  (e.g., healthcare triage, customer support, HR screening, logistics dispatch,
  legal document review). Name agents clearly after their role
  (e.g., ClassifierAgent, ResponderAgent, ReviewerAgent, RouterAgent).

SCENARIO FOCUS:
The candidate is given a small, partially-built LLM multi-agent system for
a realistic business workflow — the specific domain and agent roles MUST
come from the chosen real-world scenario above.

The system has exactly ONE bug in the agent/tool layer (per RULE 2 above).
The bug must be plausible — something a junior engineer would ship when
first wiring up a multi-agent crew.

The candidate must:
(a) Read the existing agent setup and understand the intended agent flow
(b) Identify the single broken behaviour causing the wrong output or crash
(c) Fix it with a targeted, minimal code change (20–50 lines)
(d) Verify with the provided pytest suite (mocked LLM responses)

WHAT THIS TASK TESTS:
- Ability to read an LLM-based agent setup and trace the message/tool flow
- Understanding of agent tool schemas (parameter names, types, return fields)
- Understanding of how agents hand off outputs to each other
- Ability to fix one specific agent/tool wiring bug with a minimal change
- Practical awareness of LLM agent stopping conditions and routing logic

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Identifies the SPECIFIC line or config causing the agent to misbehave
- Fix is targeted and minimal — does not rewrite unrelated agent logic
- After the fix, the agent calls the tool (not plain text) OR routes correctly
  OR passes memory correctly OR terminates with a final answer
- Can explain WHY the bug causes the observed symptom
- Tests pass with mocked LLM responses

Before we proceed to the detailed task generation instructions, please confirm
your understanding by answering:

1. Which framework will you use? (Must be the framework named in the scenario — CrewAI if the
   scenario says CrewAI, LangChain if it says LangChain, etc.)
2. Which bug from the scenario will you implement? (Quote the exact bug described in the
   scenario — do NOT substitute a different bug archetype.)
3. What are the agent role names from the scenario?
4. What are the 2 pytest tests checking? (Must match the success criteria in the scenario.)

IMPORTANT: Your answers must match the scenario exactly. You are implementing the scenario —
not inventing a new one. If an existing task title seems similar, that is fine — the scenario's
specific bug is unique and must be implemented as written.

Please provide a brief summary confirming you will implement the scenario as-is.
"""

PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INSTRUCTIONS = """
## GOAL
As a senior multi-agent systems engineer experienced in LLM-based agent frameworks,
you are generating a realistic work-item assessment that tests whether a candidate
can read a small LLM agent setup, identify one specific broken behaviour in the
agent/tool layer, and fix it with a targeted code change. The domain, agent roles,
and pipeline shape come from the chosen real-world scenario. The task must feel like
a real bug ticket — the kind a junior engineer picks up when "the agent just returns
a wall of text instead of using the tool" or "the wrong specialist keeps getting the
request".

## HARD SCOPE BOUNDARY
You MUST stay within the BASIC multi-agent systems scope:
- Reading a small Python agent setup (< 300 lines across all files the candidate must touch)
- Understanding how agents use tools, pass outputs, route tasks, and terminate
- Fixing ONE plausible agent/tool wiring bug (schema, routing, memory, stopping)
- Using LangChain, CrewAI, or AutoGen — no custom MAS frameworks
- Verifying the fix with 2 pytest tests (mocked LLM responses, no real API key)

### Out of scope — MUST NOT be primary requirements
- Designing a multi-agent architecture from scratch
- Implementing custom agent communication protocols
- Production deployment, scaling, or containerisation
- Fine-tuning or training LLMs
- Complex multi-hop reasoning or planning algorithms
- Evaluation framework design

## INSTRUCTIONS

### Nature of the Task
- The task presents a small, runnable Python multi-agent project with ONE agent/tool bug.
- The candidate must find the bug, fix it, and verify with the provided pytest suite.
- The project uses exactly ONE framework: LangChain, CrewAI, or AutoGen.
- The starter code must run as-is (possibly crashing or producing wrong output).
  There must be no syntax errors or missing imports unrelated to the bug.
- The bug lives in ONE specific function, config block, or tool definition.
- Mocked LLM responses must be included in the test fixtures so tests run offline.

### BASIC Proficiency Calibration
A BASIC-level candidate should:
- Understand what an LLM agent is and how it uses tools to act on its environment
- Be able to read a small agent setup and trace: agent → tool call → result → agent response
- Know that tool schemas must match what the agent is instructed to call
- Know that agents in a crew pass outputs to each other via defined fields or shared memory
- Know that agents need a stopping condition (max_iter, return_direct, is_last_step)
- NOT be expected to design multi-agent architectures, implement custom protocols, or
  optimise embedding/retrieval pipelines

The bug fix should require 20–50 lines of code changes, not a full rewrite.
Suitable bug patterns per shape:

  SHAPE A — BROKEN TOOL SCHEMA:
    Tool missing `return_direct=True` so agent ignores result, OR tool schema
    has wrong parameter name (`document_id` vs `doc_id`), OR return type
    declared as `str` but agent expects a structured dict.

  SHAPE B — WRONG AGENT ROUTING:
    Router checks `if intent == "billing"` but the classifier returns `"Billing"`
    (case mismatch), OR missing `elif` branch so all non-billing tasks fall
    through to the wrong default agent.

  SHAPE C — MEMORY NOT PASSED:
    Agent writes result to `self.result = output` (instance variable) instead
    of returning it or writing to `crew.shared_memory["key"]`, so downstream
    agent receives None.

  SHAPE D — AGENT LOOP NOT TERMINATING:
    `max_iterations` not set (defaults to unlimited), OR `return_direct` missing
    on the final tool, OR `is_last_step` check never evaluates to True because
    a counter is not incremented.

### Scenario Selection
- You MUST use one of the provided real-world scenarios as direct inspiration
  for the business domain, agent roles, and workflow.
- The bug shape should feel natural for the chosen scenario.
- Vary the chosen scenario and shape across generations.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, documentation,
  and AI tools.
- The task rewards practical understanding of agent wiring — not memorisation of
  framework API names.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Multi-Agent Systems task that:
- Draws inspiration from one selected scenario (business domain, agent roles, workflow).
- Uses ONE bug shape from the four shapes above.
- Keeps the project lightweight — no Docker, no external services, no real API keys needed.
- Is completable within {minutes_range} minutes.
- Tests practical agent wiring judgment: tool schemas, routing logic, memory passing,
  stopping conditions.

## Infrastructure Requirements
- MUST be a Python project using LangChain, CrewAI, or AutoGen.
- MUST include requirements.txt.
- MUST include runnable Python source files.
- MUST include pytest tests with mocked LLM responses in tests/conftest.py.
- MUST keep setup lightweight and local (no Docker, no cloud dependencies).
- API key handled via .env.example — MUST NOT be required to run tests.

## Starter Code Instructions
- The starter code must be valid and executable.
- The agent/tool bug must be present but not annotated.
- Do NOT include TODO comments, placeholder hints, or comments that say "this is the issue".
- Do NOT include solution code.
- Include exactly 2 pytest tests (in tests/test_agents.py) that FAIL before the fix
  and PASS after.
- tests/conftest.py must provide mocked LLM responses so tests run without an API key.
- Keep the codebase small: the candidate should be able to read every file in < 10 minutes.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Tool Schema for Support Classifier Agent', 'Repair Agent Routing in HR Screening Crew', 'Fix Memory Handoff in Logistics Dispatch Agents'.",
  "question": "Short description of the scenario and the specific ask — what is wrong (observable symptom only, not root cause), what the candidate must fix, and how to verify. Frame it as a real work item (Slack message, Jira ticket). Do NOT reveal the root cause. 3-5 sentences.",
  "code_files": {{
    "README.md": "Candidate-facing README. MUST contain: Task Overview (2-3 sentences: business scenario + observable symptom), Helpful Tips (3-4 action bullets — guide discovery without revealing the bug), Objectives (3-5 bullets: what should work after the fix), How to Verify (2-3 checks: run pytest, observe agent output). Do NOT include setup commands, solution steps, or code snippets.",
    ".gitignore": "Standard Python gitignore including venv, .env, __pycache__, *.pyc, *.log",
    "requirements.txt": "Python dependencies: openai, langchain (or crewai or pyautogen), python-dotenv, pytest, pytest-mock",
    ".env.example": "Example environment variables — LLM API key only (e.g. OPENAI_API_KEY=sk-...). No real secrets.",
    "agents/crew.py": "The multi-agent setup — agent definitions, tool assignments, routing logic, crew/team wiring. This is where the bug lives. Must be valid Python. Do NOT annotate the bug.",
    "agents/tools.py": "Tool definitions used by the agents — schemas, handlers, return types. May also contain part of the bug (e.g. wrong schema field). Valid Python.",
    "agents/main.py": "Entry point — instantiates the crew/team and runs a sample task. Runnable. Shows the observable wrong behaviour when executed.",
    "tests/conftest.py": "pytest fixtures providing mocked LLM responses so all tests run without a real API key. Use unittest.mock.patch or pytest-mock.",
    "tests/test_agents.py": "Exactly 2 pytest tests that FAIL before the fix and PASS after. Test 1: the agent invokes the tool (not plain text) for a sample input. Test 2: the agent produces the correct output/routing/memory/termination for the scenario."
  }},
  "outcomes": [
    "The agent correctly invokes the designated tool (not falls back to plain text) for the sample input after the fix.",
    "Agent outputs, routing decisions, or memory values are correctly passed to the next agent in the crew.",
    "Both pytest tests pass with mocked LLM responses and no real API key required.",
    "The fix is targeted and minimal — unrelated agent logic is left unchanged.",
    "Agent behaviour is observable and traceable via the entry point in agents/main.py."
  ],
  "short_overview": [
    "The business domain, the agent roles, and the workflow the multi-agent crew is designed to perform.",
    "The specific shape of the bug (tool schema / routing / memory / stopping) and where it sits in the codebase.",
    "What the candidate must change and how the provided pytest suite verifies the fix."
  ],
  "pre_requisites": "Exactly 2–3 concise bullets. Each covers ONE item: (1) runtime/toolchain required, (2) repo/environment setup, (3) key domain knowledge if non-obvious. Each bullet ≤ 120 chars. No padding, no sub-lists.",
  "answer": "High-level solution approach at a non-code level. Name: (1) the specific bug (which file/line/config, what it does wrong), (2) the minimal fix (what change makes the agent behave correctly), (3) how to verify (what the pytest tests assert after the fix). Do NOT write full solution code here.",
  "hints": "A single gentle nudge pointing the candidate toward the right layer without revealing the fix. Example: 'Add a print or log statement showing what the agent actually calls after receiving the input — compare that to what it should call according to the tool schema.'",
  "definitions": {{
    "Agent": "An autonomous LLM-powered component that perceives inputs, decides which tool or action to take, and produces an output — distinct from a passive function or service.",
    "Tool": "A callable action an agent can invoke (e.g. search, classify, save) defined by a schema (name, description, parameters, return type) that the LLM uses to decide when and how to call it.",
    "Tool Schema": "The formal definition of a tool's interface — parameter names, types, descriptions, and return type — that the agent framework passes to the LLM so it knows how to call the tool correctly.",
    "Crew": "A group of agents configured to collaborate on a multi-step workflow, with defined roles, task assignments, and a shared or sequential output flow.",
    "Routing": "The logic that decides which agent receives a given task or message, typically based on intent, category, or a supervisor agent's decision.",
    "Agent Memory": "State shared between agents in a crew or between an agent's steps — could be a shared dict, a crew output field, or an external store — used to pass structured results downstream.",
    "Stopping Condition": "A rule that tells an agent when to stop calling tools and return a final answer (e.g. max_iterations reached, return_direct=True on the last tool, is_last_step flag).",
    "Mock LLM": "A test double that replaces a real LLM API call with a fixed, deterministic response — allows tests to run offline without an API key while still exercising agent logic."
  }}
}}

## Code File Requirements
- All files must be listed and populated in the JSON code_files dict.
- Python files must follow PEP 8.
- The starter code must be valid and runnable but exhibit wrong behaviour due to the bug.
- Do NOT reveal the fix in comments, TODO markers, or docstrings.
- Keep each file small enough for a BASIC candidate to read in under 3 minutes.
- tests/test_agents.py must have exactly 2 tests: both FAIL before the fix, both PASS after.
- tests/conftest.py must mock the LLM so no real API key is needed.

## README.md Structure
The README must contain exactly four sections:
- **Task Overview**: 2-3 sentences — the business scenario and the observable symptom.
- **Helpful Tips**: 3-4 action bullets — guide discovery without revealing the root cause.
  Use words like "Review", "Inspect", "Trace", "Check", "Compare".
- **Objectives**: 3-5 bullets — what should be working after the fix.
- **How to Verify**: 2-3 checks — run pytest, observe agent output in main.py.

Do NOT include: setup commands, solution steps, code snippets, or architecture diagrams.

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown fences, no explanations. Emit the raw
   JSON object starting with {{ and ending with }}.
2. name must be kebab-case, 3-6 words.
3. title must be plain English, verb-first, 50-80 characters.
4. The bug must be in the agent/tool layer — NOT a syntax error, import error, HTTP
   endpoint, or Redis store.
5. The framework MUST be LangChain, CrewAI, or AutoGen. No rule-based agents. No Redis. No Docker. pyproject.toml MUST list crewai, langchain, or pyautogen — NOT redis or fakeredis.
6. Starter code must be runnable Python 3.10+.
7. tests/test_agents.py must have exactly 2 tests that fail before and pass after the fix.
8. tests/conftest.py must mock the LLM — no live API calls in tests.
9. Do NOT reveal the bug in comments, the README, or the question field.
10. Keep the total candidate-visible codebase small: < 300 lines across files the
    candidate must read and touch.
11. Use ONE bug shape only — do not mix shapes in a single task.
12. The task must be completable within {minutes_range} minutes.
13. Domain, agent roles, and workflow all come from the chosen real-world scenario —
    vary across generations.
"""

PROMPT_REGISTRY = {
    "Multi-Agent Systems (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INPUT_AND_ASK,
        PROMPT_MULTI_AGENT_SYSTEMS_BASIC_INSTRUCTIONS,
    ]
}
