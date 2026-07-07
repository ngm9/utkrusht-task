# Set by the prompt-generator open-ended dial — do not edit.
# Consumed by infra.utils so the task row records which kind of task
# (specified vs withhold-the-solution) this combo produces.
OPEN_ENDED = False


# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


# task_generation_prompts/Intermediate/context_engineering_intermediate_prompt/context_engineering_intermediate_prompt.py
#
# CURATED task-generation prompt module for AI-agent BUILD-IT tasks.
# Competency: "Context Engineering"  ·  Proficiency: INTERMEDIATE
#
# Contract:
#   * Export a top-level dict named exactly PROMPT_REGISTRY.
#   * Key it exactly "Context Engineering (INTERMEDIATE)".
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal {placeholders} are:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.

PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role.

Company Context:
{organization_background}

Role Context:
{role_context}

Target Competencies:
{competencies}

Use this context ONLY to gauge who is hiring and how senior the engineer must be.
The employer's industry is NOT the business domain of the assessment task unless
the scenario you pick explicitly matches it. Do not drift the task into the
employer's domain. You are generating an assessment for an INTERMEDIATE engineer
who can build, debug, and improve context pipelines for real LLM applications.
"""

PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic, INTERMEDIATE "build-it" assessment task for a
Context Engineering candidate. The candidate clones a runnable Python agent
repository, sets their own provider key in `.env`, runs `./run.sh`, and writes
roughly 60-140 lines of code inside 1-2 focused stub files. This is a coding
session, NOT a write-a-memo / essay / quiz exercise.

CALIBRATION: this probes practical context-engineering judgment for a candidate
with a few years of experience. The task should isolate ONE clear context
decision, or at most two tightly-related decisions, such as bounded context
packing, tenant-scoped retrieval, memory freshness/deduplication, prompt-section
separation, citation-grounding, or token-budget tradeoffs. Do not turn it into a
whole platform build.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget
it as: ~5 minutes setup, ~5 minutes reading fixtures and traces, and ~20 minutes
writing or adjusting code. Keep the repository lean and focused.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CORE JOB — BUILD ONE CONTEXT-ENGINEERING AGENT REPO from these fields:
  **Stack:** Python 3 with a real model client such as litellm, openai, or anthropic; local fixtures; pytest invariants.
  **Domain:** The business setting from one provided real-world scenario.
  **Candidate writes:** The stub file(s) that assemble, retrieve, budget, cache, or manage context.
  **Provided broken:** A context pipeline flaw such as dump-all retrieval, unsafe tenant mixing, unbounded prompt growth, stale memory, missing source separation, or lossy truncation.
  **Invariants:** Candidate-facing tests that inspect constructed context, retrieval decisions, memory updates, citations, and guardrails.
  **Senior signal:** The candidate's context-modeling judgment: what to include, exclude, order, scope, summarize, cite, retain, or redact.

SCENARIO HANDLING — READ CAREFULLY:
- You MUST draw inspiration from ONE of the real-world scenarios provided above
  to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent
  a different domain. When multiple scenarios are listed, pick the one whose
  technical surface area best fits Context Engineering at INTERMEDIATE level.
- The task scenario should closely align with the business context, technical
  requirements, and domain described in the selected real-world scenario.
- If the provided scenario is mostly about tool validation, enrollment safety, or
  concurrency, translate only the context-relevant surface into a context task:
  evidence selection, prompt assembly, session state, explicit confirmation
  context, tenant scoping, source separation, or latency-aware context assembly.
- If `REAL-WORLD SCENARIOS` is empty or "(none provided)", design a realistic
  domain yourself, but keep it centered on context construction, retrieval,
  memory/state, token budgeting, grounding, privacy, or access control.

Before generating, briefly internalize:
1. Which scenario you selected and why it is a Context Engineering task.
2. Which context failure is observably present in the shipped repo.
3. Which candidate stubs isolate the context decision without handing over the fix.
4. Which local fixtures and invariant tests make the problem reproducible without
   replacing the real LLM path.
"""

PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Context Engineering for LLM-backed
systems, you are given a list of real world scenarios and proficiency levels for
Context Engineering. Generate ONE INTERMEDIATE Context Engineering "build-it"
task: a FULLY FUNCTIONAL local Python repository that is deliberately incomplete
in the context pipeline. It ships working scaffolding, realistic fixtures, a real
LLM call path, and candidate stubs that raise `NotImplementedError`; the
candidate makes the agent grounded, scoped, safe, and token-aware by filling the
stubs and fixing the planted context flaws.

The agent calls a REAL model via litellm or the anthropic/openai SDK on the
candidate's key. NEVER use a FakeLLM. NEVER use a regex / keyword intent parser
as the agent's reasoning. NEVER use a deterministic stand-in for the model.
NEVER use time.sleep / asyncio.sleep to simulate the agent. Fixtures may make
local tool inputs, retrieved documents, traces, and expected context artifacts
deterministic; they must NOT replace the model's reasoning.

The generated task must be a coding exercise, not an essay, not a framework
syntax drill, and not a pure prompt-writing exercise. The candidate should work
inside a small Python project that can run locally from `/root/task`.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an INTERMEDIATE Context Engineering practitioner. They should
already understand runtime context as the information supplied to a model at
inference time: system instructions, task instructions, user input, prior turns,
retrieved evidence, tool outputs, user/session state, metadata, safety policy,
and application configuration. They can distinguish model knowledge from runtime
grounding data, analyze what context a business problem requires, and implement
a pragmatic context pipeline with token limits, retrieval filters, memory/state
handling, source separation, and evaluation fixtures.

**CRITICAL**: Stay within Context Engineering scope. The task may use an agent
loop, but the assessed work is context construction: retrieval and grounding,
chunk selection, metadata filtering, prompt layout, context budgeting,
conversation memory, tenant/user scoping, citation support, prompt-injection
resistance, PII minimization, caching/freshness, and failure analysis from
traces. Do NOT make the primary skill model fine-tuning, ML training,
infrastructure provisioning, frontend work, SQL tuning, or generic tool-call
schema validation.

**CRITICAL**: The task should be solvable within {minutes_range}. Keep the
candidate-written code to 1-2 files and about 60-140 lines. Include tests that
surface the expected behavior, but do not require the generated `run.sh` to pass
those tests on the unsolved starter.

## INSTRUCTIONS

### Nature of the Task
Create a realistic work item where a context-rich LLM application is failing in
production because the assembled context is incomplete, noisy, stale,
over-broad, unsafe, or too large. The repository must be FULLY FUNCTIONAL as a
starter: dependencies install, fixtures load, imports succeed, `./run.sh` exits
successfully, and the candidate can inspect the code, traces, and tests before
implementing the missing context logic.

Valid INTERMEDIATE Context Engineering task shapes include:
- A support or workflow assistant that dumps an entire local knowledge base into
  the prompt instead of retrieving a small tenant-scoped evidence set.
- A multi-turn assistant that loses decision-critical session facts or carries
  stale memory into unrelated turns.
- A RAG answerer whose prompt mixes instructions, retrieved evidence, user text,
  and untrusted content without delimiters or citation structure.
- A context-budgeting middleware that must count tokens and preserve the most
  relevant policy/evidence/user-state sections under a model input ceiling.
- A retrieval pipeline that must filter by tenant, permission, freshness, source
  quality, or document type before ranking evidence.
- A context-aware cache or summary layer that must respect freshness and
  permissions rather than serving stale or cross-tenant context.

**CRITICAL**: The task must contain a real LLM/agent loop. The live path must call
a real model through litellm, openai, or anthropic using the candidate's own key
from `.env`. The candidate-filled stubs are the context logic around that real
model: retrieval selection, context packing, memory/state updates, prompt
assembly, redaction, token budgeting, or source ordering. The stubs are NOT a
fake model and NOT a regex intent parser.

**CRITICAL**: For Context Engineering, deterministic grading fixtures may assert
the constructed prompt sections, selected evidence IDs, memory records, token
counts, source citations, or access-control decisions. Those fixtures may not
pretend to be the LLM. The real model path must remain available for the
candidate's end-to-end run.

**CRITICAL**: The candidate-facing README, question, comments, and stub
docstrings may describe the symptom and the expected business outcome, but they
must not leak the reference answer. Since `open_ended` is false for this
generation style, tests and stub contracts MAY describe observable return shapes
and acceptance conditions, but avoid writing the solution in prose.

If you include diagrams, ensure they are written in mermaid format, properly
indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Python
documentation, LangChain/LlamaIndex/LiteLLM/OpenAI/Anthropic documentation,
tiktoken documentation, fastembed documentation, and AI-powered tools, agentic
IDEs, or Large Language Models (LLMs).

- The assessment evaluates applied Context Engineering judgment, not
  memorization.
- Candidates may use AI assistance, but they must still inspect the repository,
  understand the context failure, and produce a working implementation.
- External resources should not be required to infer hidden business rules; the
  repository must contain enough fixtures, tests, traces, and docs to make the
  problem fair.
- Do not include rules that ban AI tools or external documentation.

## Code Generation Instructions
Generate a pure local Python project. Use Python 3.11-compatible code, a
`requirements.txt` manifest, package-style source files under an `agent/` or
`context_agent/` directory, candidate-facing tests under `invariants/`, and
realistic local fixtures under `fixtures/`. **FILE LOCATION**: All code and
scripts must reference /root/task as the base directory.

The repository should normally contain 8-12 files:
- `README.md` with the exact four candidate-facing sections described below.
- `requirements.txt` listing every third-party package the project imports.
- `.env.example` declaring `OPENAI_API_KEY=` and/or `ANTHROPIC_API_KEY=`, plus
  model-name configuration if needed.
- `run.sh` as a deployability/readiness probe.
- `agent/__init__.py` and `agent/__main__.py` or equivalent package entrypoint.
- A complete model client wrapper, such as `agent/llm_client.py`, that performs
  a real provider call when a key is present and the end-to-end agent is invoked.
- Working support modules such as `agent/prompts.py`, `agent/schema.py`,
  `agent/fixtures.py`, or `agent/tracing.py`.
- Candidate-stub modules such as `agent/context_builder.py`,
  `agent/retrieval.py`, `agent/memory.py`, or `agent/budget.py`; these should
  raise `NotImplementedError` in the functions the candidate must fill.
- `fixtures/*.json` or `fixtures/*.jsonl` containing documents, policies, users,
  session turns, traces, or evaluation cases.
- `invariants/test_*.py` containing candidate-facing pytest tests that fail until
  the candidate completes the context logic.

Use real libraries when appropriate:
- `litellm`, `openai`, or `anthropic` for real model calls.
- `python-dotenv` for loading `.env`.
- `tiktoken` for token accounting when the task involves prompt budgets.
- `fastembed` for local embeddings when the task involves semantic retrieval.
- `pytest` for invariant tests.
Avoid heavyweight dependencies such as torch or sentence-transformers unless the
scenario absolutely requires them.

The generated repo must not require any external datastore, vector database,
cache, queue, browser, or server process. If retrieval is needed, use local JSON,
JSONL, Markdown, SQLite from the Python standard library, in-memory indexes, or
local fastembed vectors persisted inside the repository.

## Infrastructure Requirements
This is a non-infrastructure task. The generated repository MUST be a pure local
Python project using native Python packaging and test commands. Do not require
any Docker daemon, external datastore, hosted vector database, queue, cache,
search engine, or database service.

### Docker-compose Instructions
Do not generate a compose file. Do not include compose commands in setup,
readiness, verification, README, or tests. This task must run locally with Python
and the dependencies installed from `requirements.txt`.

### Local Fixture and Configuration Instructions
Use local fixtures only. Do not generate database initialization scripts or
datastore configuration. Local documents, traces, policies, tenant metadata,
session histories, and evaluation cases should live under `fixtures/` and should
be internally consistent with the README, tests, and code comments. Secrets must
not appear in fixtures. The `.env.example` file must declare provider key names
but must not contain real credentials.

### Run.sh Instructions
Generate `run.sh` and make it executable in spirit with a proper shebang:
`#!/usr/bin/env bash`. It must use `/root/task` as the working directory and its
FIRST substantive step must install the task's own dependencies with
`pip install -q -r requirements.txt`. Do NOT apt-get or system-install Python;
the runtime is already available.

`run.sh` is a DEPLOYABILITY probe, NOT the grader. It proves that the starter repo
is usable before the candidate solves it:
1. Change to `/root/task`.
2. Install dependencies from `requirements.txt`.
3. Load `.env` only if present; absence of a provider key must not fail readiness.
4. Run an import/static self-check such as `python -m agent --selfcheck`.
5. The self-check may validate fixture files, schema shapes, prompt templates,
   tokenizers, and local embedding initialization.
6. The self-check must NOT invoke candidate stubs that still raise
   `NotImplementedError`.
7. The self-check must NOT run the full agent loop or require a model call.
8. If a provider key is present, an optional direct one-token provider ping may
   run through the model client, but it must not call the unfinished agent logic.
9. Print a clear final readiness message such as `ready`.

If `run.sh` also runs pytest collection or candidate-facing invariant tests, it
must treat pytest exit code 0 and exit code 1 as deployable because failing tests
are expected on the unsolved starter. It must exit non-zero only for collection,
configuration, dependency, internal, or no-tests-collected failures. For pytest,
capture the exit code and branch so that 0 and 1 exit successfully while 2, 3, 4,
or 5 fail the readiness probe.

## kill.sh file instructions
Do not generate a cleanup script for this task. There are no containers, volumes,
networks, or datastore processes to stop. Keep the repository pure local and
Python-native.

### Dockerfile Instructions
Do not generate a Dockerfile. This task does not need an application container.

The output should be a valid json schema:
- `README.md`: Candidate-facing overview with exactly the four required sections.
- `requirements.txt`: Python dependency manifest with every imported third-party package.
- `.env.example`: Provider key and model configuration template with no secrets.
- `run.sh`: Local readiness script using `/root/task` and installing dependencies first.
- `agent/__init__.py`: Minimal package marker or package exports.
- `agent/__main__.py`: CLI entrypoint supporting `--selfcheck` and optionally an end-to-end run.
- `agent/llm_client.py`: Complete real provider client wrapper used by the live agent path.
- `agent/context_builder.py` or similar: Candidate-stub file for assembling context.
- `agent/retrieval.py`, `agent/memory.py`, or `agent/budget.py`: Candidate-stub or supporting context logic files as needed by the scenario.
- `agent/prompts.py` or `agent/schema.py`: Working prompt templates and structured context schemas.
- `fixtures/*.json` or `fixtures/*.jsonl`: Realistic local documents, traces, sessions, policies, or eval cases.
- `invariants/test_context_*.py`: Candidate-facing tests for constructed context, retrieval scope, memory behavior, citations, privacy, or token budgets.

## Code file requirements
All generated `code_files` must be complete file contents, not snippets. The
starter repository must import and self-check successfully before the candidate
implements the stubs. Candidate stubs should raise `NotImplementedError` with a
neutral one-line message naming the purpose, not the solution.

The code should model context explicitly. Prefer typed dictionaries, dataclasses,
or Pydantic models for context sections, evidence records, tenant metadata,
session state, citations, and assembled prompt payloads. Keep prompt templates
clear and separated into instructions, policy, user input, retrieved evidence,
memory/session state, and tool/output constraints. Use delimiters around
untrusted content and preserve source identifiers for attribution.

Include realistic failure evidence without annotating it as the fix: traces may
show hallucinated answers from noisy evidence, cross-tenant snippets appearing in
context, stale memory overriding fresh user input, excessive prompt token counts,
or missing citations. Tests may assert observable behavior such as no cross-tenant
evidence, bounded token count, required source IDs, retention of recent decision
facts, or graceful "unknown" behavior when evidence is insufficient.

Do not leak the reference answer into candidate-facing code, README, comments, or
fixture names. The full solution approach belongs only in the `answer` field.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` when useful. It should ignore Python caches, virtual
environments, pytest caches, local `.env`, coverage artifacts, editor folders,
and temporary outputs. It must not ignore fixtures, invariant tests, README,
requirements, or source files needed to run the task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the
implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and
guidance to help them discover solutions.

The README.md must contain EXACTLY these output sections, in this order, and no
others:

### Task Overview
Task Overview must be 3-4 meaningful sentences. No bullet list. It describes the
business scenario, current state, and why the context failure matters. It is
NEVER empty. Do not include bold time-budget callouts. Do not name the stub
functions or give the implementation plan.

### Objectives
Objectives must contain 4-6 bullets max. Frame objectives around outcomes rather
than specific technical implementations. Objectives describe the "what" and
"why", never the "how". Each bullet states an observable end-state, not a step,
API, library, or function to use.

### Helpful Tips
Helpful Tips must contain 4-5 bullets max. Provide practical guidance without
revealing specific implementations. Each bullet starts with an action word:
"Consider", "Think about", "Explore", "Review", or "Analyze". Tips guide
discovery — they MUST NOT name the specific API, library, function, pattern, data
structure, or algorithm that solves the task.

### How to Verify
How to Verify must contain 4-6 bullets max. Frame verification in terms of
observable outcomes. Describe WHAT to verify and the expected behavior, not the
specific implementation to write. Each bullet is a check the candidate can run:
test output, response shape, prompt/context inspection, source/citation presence,
token reading, privacy observation, or log line.

For tasks that call a real LLM and include `.env.example` declaring
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, How to Verify MUST open with a GitHub
note admonition embedded INSIDE the section as a blockquote, never as a new
heading:
> [!NOTE]
> Copy `.env.example` to `.env` and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, or shell
  command walkthroughs beyond high-level verification language.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create
  this class", or "use this specific API".
- Database connection details, hostnames, ports, usernames, passwords, client
  tool suggestions, or infrastructure placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each value
below describes what to fill in; replace descriptions with the generated task
content.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that is distinct from the human-readable title and reflects the context-engineering work item.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, describing the main context-engineering improvement without revealing the solution.",
  "question": "The full candidate-facing task description written like a realistic work ticket or incident-channel request, stating the observable context failure, business impact, constraints, and how to start without naming the solution.",
  "code_files": "An object mapping each repository filepath to the complete file contents for a runnable local Python project, including README, requirements, .env.example, run.sh, source modules, fixtures, and invariant tests.",
  "answer": "Evaluator-facing high-level solution guidance summarizing root causes, expected fix shape, tradeoffs, residual risks, and evidence reviewers should look for, without duplicating full solution files.",
  "definitions": "An object mapping context-engineering terms used in the task to concise definitions that clarify concepts such as grounding, token budget, retrieved evidence, memory, tenant isolation, prompt injection, or citation.",
  "hints": "A single line or short list nudging investigation toward the observable context symptom without revealing the specific implementation or reference fix.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable improvements to groundedness, relevance, safety, token control, source traceability, and production-clean code quality.",
  "pre_requisites": "A bullet list of assumed prior knowledge and skills expressed as declarative capability phrases only, such as Python 3.11 proficiency, comfort with pytest, familiarity with runtime context, understanding of RAG or memory concepts, and a provider key via .env.",
  "short_overview": "A bullet list summarizing the business problem, the context-engineering focus, the starter repository shape, and the expected observable outcome."
}}

Use these EXACT keys. Do NOT use synonyms such as `task_title`, `files`,
`repository`, `context`, `solution`, or `criteria`. Do NOT emit `criterias`; the
pipeline injects it. Output raw JSON only — no markdown fences and no prose
around the JSON object.

## CRITICAL REMINDERS
1. Output must be valid JSON only, starting with `{{` and ending with `}}`.
2. Generate a pure local Python project; do not include container, compose,
   datastore, database initialization, or cleanup infrastructure.
3. `run.sh` must install dependencies first and must pass on the unsolved starter
   without invoking candidate stubs or requiring an API key.
4. The live agent path must call a real model through litellm, openai, or
   anthropic using the candidate's provider key.
5. NEVER use a FakeLLM.
6. NEVER use a regex / keyword intent parser as the agent's reasoning.
7. NEVER use a deterministic stand-in for the model.
8. NEVER use time.sleep / asyncio.sleep to simulate the agent.
9. Fixtures may make local tool inputs, retrieved documents, traces, and expected
   context artifacts deterministic; they must NOT replace the model's reasoning.
10. Center the task on Context Engineering: context assembly, retrieval,
    grounding, token budgeting, memory/state, prompt sectioning, privacy,
    access-control, injection resistance, caching, evaluation, or debugging.
11. Keep the candidate-written work focused: 1-2 stub files, roughly 60-140 lines,
    and solvable within {minutes_range}.
12. README.md must contain exactly four sections in this order: Task Overview,
    Objectives, Helpful Tips, How to Verify.
13. Do not leak the reference answer into README, code comments, fixtures, tests,
    question, hints, or stub docstrings.
14. The `answer` field is evaluator-facing and should include the expected fix
    approach, root cause, tradeoffs, and review signals.
15. All file paths and scripts must assume `/root/task` as the base directory.
"""

PROMPT_REGISTRY = {
    "Context Engineering (INTERMEDIATE)": [
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_CONTEXT,
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS,
    ]
}