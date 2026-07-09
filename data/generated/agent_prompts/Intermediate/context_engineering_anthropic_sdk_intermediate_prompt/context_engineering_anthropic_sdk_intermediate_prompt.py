# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


# task_generation_prompts/Intermediate/context_engineering_anthropic_sdk_intermediate_prompt.py
#
# CURATED task-generation prompt module for Context Engineering with Anthropic SDK BUILD-IT tasks.
# Competency: "Context Engineering - Anthropic SDK"  ·  Proficiency: INTERMEDIATE
#
# DROP-IN for infra/utils.py::_build_prompt_registry. The loader filesystem-walks
# task_generation_prompts/<Level>/<slug>.py and calls registry.update(PROMPT_REGISTRY).
# Contract:
#   * Export a top-level dict named exactly PROMPT_REGISTRY.
#   * Key it exactly "Context Engineering - Anthropic SDK (INTERMEDIATE)".
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal {placeholders} are the fmt_args keys:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.

PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_CONTEXT = """
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
employer's domain. You are generating an assessment for an intermediate AI agent
engineer who can independently debug and improve RAG prompt construction, token
budgeting, and Anthropic SDK integrations.
"""

PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_INPUT_AND_ASK = """
You are generating ONE realistic, INTERMEDIATE "build-it" assessment task
for a Context Engineering - Anthropic SDK candidate. This is a coding session,
NOT a write-a-memo, essay, quiz, or framework-trivia exercise. The candidate
clones a small Python project, reads an existing RAG prompt assembly pipeline,
fixes the context construction bug, and validates the behavior with pytest.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Budget it
as: ~5 minutes setup and reading, ~5-10 minutes reproducing the failing tests and
inspecting the assembled prompt, and ~10-20 minutes writing targeted code. Keep
the candidate's likely changes concentrated in one function or one small module.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CORE JOB — BUILD ONE LOCAL PYTHON REPO from these fields:
  **Stack:** Python, anthropic>=0.25, claude-3-haiku-20240307, ChromaDB-style RAG pipeline, pytest, python-dotenv.
  **Domain:** legal research assistant over case-law chunks.
  **Candidate writes:** a targeted fix in the context assembly layer, centered on assemble_prompt().
  **Provided broken:** retrieved top-k chunks are concatenated with newlines, with no XML document boundaries and no token budget enforcement.
  **Invariants:** token overflow and XML structure tests must fail before the fix and pass after; Anthropic SDK calls are mocked through pytest fixtures.
  **Intermediate signal:** practical context engineering judgment: preserve system and user query context, count tokens with the Anthropic SDK token-counting utility, trim lowest-scoring retrieved chunks first, and separate untrusted retrieved evidence from the user query.

SCENARIO HANDLING — READ CAREFULLY:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- For this competency and directive, prefer the legal research assistant scenario using the Anthropic Python SDK and a ChromaDB RAG pipeline. Do not substitute a customer support bot, generic chat history task, or non-Anthropic provider task.

Before generating, briefly internalize:
1. The selected legal research RAG scenario and why it fits intermediate Context Engineering with the Anthropic SDK.
2. Which files are starter code, which file contains the broken context assembly behavior, and which tests expose the symptoms.
3. How the prompt should be structured so Claude can distinguish system instructions, retrieved case documents, and the user query.
4. How the token budget should be enforced so the assembled prompt never exceeds MAX_CONTEXT_TOKENS while preserving the system message and user query.
"""

PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Context Engineering with the Anthropic
SDK, you are given a list of real world scenarios and proficiency levels for
Context Engineering - Anthropic SDK. Generate ONE INTERMEDIATE build-it task: a
small, FULLY FUNCTIONAL local Python repository for a legal research assistant
that contains a deliberately incomplete context assembly implementation. The
candidate must repair the RAG prompt construction so retrieved case chunks are
wrapped in XML and the prompt stays within the configured Anthropic context budget.

The task must implement the directive's scenario: a legal research assistant uses
the Anthropic Python SDK with model `claude-3-haiku-20240307` and a ChromaDB-style
RAG pipeline. The existing `assemble_prompt()` function retrieves the top-5
relevant case chunks and concatenates them with simple newlines, which causes
`context_length_exceeded` failures and hallucinated citations when Claude confuses
retrieved content with the user query. The pytest suite mocks the Anthropic SDK,
so tests run without a real key; real runs work when `ANTHROPIC_API_KEY` is set
in `.env`.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate AI agent or context engineer with practical
experience building and debugging LLM applications. They should be able to:
- Trace how system instructions, retrieved evidence, user input, and configuration
  become the final model context.
- Use the Anthropic Python SDK to construct model calls and count tokens.
- Understand context window limits, tokenization, truncation, and the impact of
  prompt structure on groundedness and hallucination.
- Improve a RAG context assembly function without rewriting unrelated retrieval,
  CLI, or test infrastructure.
- Validate behavior with mocked SDK calls and a local pytest suite.

This is not a systems-design essay and not a pure prompt-writing exercise. The
candidate must make a targeted implementation change in a runnable Python project.

## INSTRUCTIONS

### Nature of the Task
- The task presents a small, runnable Python project with a legal research RAG
  prompt assembly bug.
- **CRITICAL**: The broken behavior must be in `context_builder.py`, centered on
  `assemble_prompt()`, and it must be plausible production code rather than a
  cartoonish syntax error.
- **CRITICAL**: The starter implementation retrieves the top-5 most relevant case
  chunks, then concatenates them with simple newlines. It does not wrap retrieved
  chunks in XML and does not enforce `MAX_CONTEXT_TOKENS`.
- **CRITICAL**: The candidate must count tokens using the Anthropic SDK token-
  counting utility exposed or mocked by the project, not by a hand-rolled word
  count. Tests may monkeypatch the SDK utility so they remain deterministic.
- **CRITICAL**: When the prompt exceeds budget, the fix must trim the lowest-
  scoring retrieved chunks first while always preserving the system message and
  user query.
- **CRITICAL**: Retrieved chunks must be wrapped in XML with a structure equivalent
  to `<documents><document index="N" score="...">...</document></documents>` so
  Claude can separate untrusted case text from the user query.
- The project should include a mocked Anthropic SDK path in `tests/conftest.py`,
  so `python -m pytest` runs without a real `ANTHROPIC_API_KEY`.
- The project may include `.env.example` and python-dotenv support. Real model
  calls may require a candidate-provided key, but tests must not.
- Keep the codebase small enough for the candidate to read quickly. The candidate
  should primarily modify one function or one module, roughly 40-100 lines of
  targeted code.
- The task must be completable within {minutes_range}.

Intermediate proficiency calibration:
- This task should be harder than a basic "include retrieved context in the
  prompt" bug because it requires token budget accounting, chunk scoring, ordering
  tradeoffs, and structured XML separation.
- It should be easier than an advanced platform task: no multi-tenant retrieval,
  no production deployment, no custom vector database implementation, no streaming
  orchestration, and no full evaluation framework.
- The task should test applied judgment in context construction, not memorization
  of Anthropic SDK syntax. Provide mocks and tests that make the expected behavior
  observable.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Anthropic
documentation, ChromaDB documentation, pytest documentation, and AI-powered tools,
agentic IDEs, or Large Language Models (LLMs).

They may use these resources to understand SDK behavior, XML prompt structuring,
token counting, pytest mocking, and Python implementation details.

They must still produce their own working code in the repository and should be
able to explain the behavior and tradeoffs of their implementation.

The assessment should reward practical debugging, context engineering judgment,
and clean implementation rather than closed-book recall.

## Code Generation Instructions
Based on the real-world scenario provided, create a Context Engineering -
Anthropic SDK task that:
- Uses a pure local Python project shape with no Docker, no docker-compose, no
  init database script, and no external datastore service.
- Includes a native Python project manifest such as `pyproject.toml`.
- Includes source code, sample case-law data, and pytest tests runnable with
  `python -m pytest`.
- Uses `anthropic>=0.25`, `chromadb`, `python-dotenv`, and `pytest` as appropriate
  project dependencies. Do NOT include install commands inside the README.
- Uses local sample data or an in-process ChromaDB-style collection abstraction so
  the tests remain deterministic and do not require a running Chroma server.
- Includes `.env.example` with `ANTHROPIC_API_KEY=` and `MAX_CONTEXT_TOKENS=`.
- Keeps all code and scripts referencing `/root/task` as the base directory when
  absolute paths are needed. **FILE LOCATION**: All code and scripts must reference
  `/root/task` as the base directory.
- Ensures any diagrams, if included, are written in mermaid format, properly
  indented and also in code blocks. Prefer no diagrams for this small task.

The task must include a broken-but-runnable starting implementation. It should
load sample legal chunks, build an assembled prompt, and expose failing tests
that clearly distinguish:
1. Prompts should never exceed `MAX_CONTEXT_TOKENS`.
2. Lower-scoring chunks are removed before higher-scoring chunks under tight
   budgets.
3. Retrieved case chunks are wrapped in XML document delimiters.
4. The user query remains outside the retrieved document block.

Recommended file set for this non-infra local project:
- `README.md`
- `.gitignore`
- `pyproject.toml`
- `.env.example`
- `src/legal_rag/__init__.py`
- `src/legal_rag/config.py`
- `src/legal_rag/context_builder.py`
- `src/legal_rag/retriever.py`
- `src/legal_rag/client.py`
- `src/legal_rag/main.py`
- `data/case_chunks.json`
- `tests/conftest.py`
- `tests/test_context_builder.py`

<The output should be a valid json schema: bullet list of files>
- `README.md`: Candidate-facing README with exactly the four required sections and no solution leakage.
- `.gitignore`: Standard Python ignores including virtual environments, caches, `.env`, test caches, local Chroma directories, and logs.
- `pyproject.toml`: Native Python project manifest with project metadata, dependencies, pytest configuration, and package discovery.
- `.env.example`: Example configuration only, including empty `ANTHROPIC_API_KEY` and a sample `MAX_CONTEXT_TOKENS` value.
- `src/legal_rag/config.py`: Configuration loader for model name, API key, and maximum context tokens.
- `src/legal_rag/context_builder.py`: The primary starter file containing `assemble_prompt()` with the planted context assembly defect.
- `src/legal_rag/retriever.py`: Lightweight local retrieval facade that returns scored legal case chunks from fixtures.
- `src/legal_rag/client.py`: Anthropic client wrapper that sends the assembled prompt in real runs but remains mockable in tests.
- `src/legal_rag/main.py`: Small CLI or demonstration entry point that loads data, assembles a prompt, and optionally calls Claude when a key is present.
- `data/case_chunks.json`: Realistic legal case chunks with ids, citations, scores, and text long enough to trigger budget behavior.
- `tests/conftest.py`: Mock fixtures for Anthropic token counting and client behavior so tests do not require a real key.
- `tests/test_context_builder.py`: Pytest tests for token overflow, XML structure, and relevance-based trimming.

## Code file requirements
- All files must be listed and FULLY POPULATED in the JSON `code_files` dict.
- The repository must be valid Python 3.10+ and runnable locally.
- The starter code must run as-is, but the target tests should fail before the
  candidate fixes `assemble_prompt()`.
- Do NOT include solution code, commented-out fixes, or TODO comments that reveal
  the implementation approach.
- The candidate-facing code may contain neutral NotImplementedError stubs only if
  necessary, but prefer a realistic broken implementation that the candidate must
  correct.
- The tests must be precise enough to validate the directive's success criteria:
  token budget enforcement, lowest-score-first trimming, XML delimiters, and
  preservation of system message plus user query.
- Tests must mock Anthropic SDK calls in `conftest.py`; do not require a live API
  key for `python -m pytest`.
- Real runs should work when `ANTHROPIC_API_KEY` is set in `.env`.
- Use clear names, simple types, and small functions. Avoid unnecessary frameworks,
  background services, Docker, migrations, queues, or deployment files.
- Do NOT include `docker-compose.yml`, `init_database.sql`, `Dockerfile`, or
  datastore configuration. This is a non-infra task.

## .gitignore INSTRUCTIONS
Generate a `.gitignore` suitable for a local Python Anthropic SDK project. Include:
- `.env` and other local secret files.
- `.venv/`, `venv/`, and virtual environment folders.
- `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, and coverage output.
- Local Chroma or vector-store artifacts such as `chroma_db/` only if the project
  creates local files.
- Logs and temporary outputs.

Do not ignore source files, tests, fixtures, README, or the project manifest.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the implementation
approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance
to help them discover solutions.

The candidate-facing README has EXACTLY these output sections, in this order, and
NO others:

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario,
current state, and why the problem matters. NEVER empty. NO bold time-budget
callouts. Mention that a legal research assistant is producing unreliable or
failing responses when many large case chunks are retrieved, but do not name the
specific fix.

### Objectives
Write 4-6 bullets max. Each objective must give the candidate enough context to
understand the problem and start investigating — without revealing the specific
fix. A good objective names: (1) what is broken or missing, (2) what observable
impact that has on the system or user, and (3) what a resolved state looks like.
It does NOT name the API, library, pattern, or algorithm that solves it. Objectives
describe the "what" and "why", never the "how".

Each bullet should be a full, context-rich sentence — not a two-word label.
BAD: "Improve query performance."
GOOD: "The legal research assistant fails on broad queries that retrieve several
large case chunks; after your changes it should keep requests within the configured
context limit while preserving the essential question and instructions."

### Helpful Tips
Write 4-5 bullets max. Provide practical guidance without revealing specific
implementations. Each bullet starts with an action word: "Consider", "Think about",
"Explore", "Review", or "Analyze". Tips guide discovery — they MUST NOT name the
specific API, library, function, pattern, data structure, or algorithm that solves
the task.

### How to Verify
Write 4-6 bullets max. Frame verification in terms of observable outcomes.
Describe WHAT to verify and the expected behavior, not the specific implementation
to write. Each bullet is a check the candidate can run or inspect, such as test
output, response shape, token-limit observation, or prompt boundary behavior.
Include `python -m pytest` as the primary validation command because the provided
tests mock external SDK calls.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the generated README. This is an instruction to you, not
a README section:
- Setup commands such as `pip install`, `docker compose up`, or package-manager
  installation steps.
- Docker or deployment instructions.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create
  this class", or "use a specific API".
- Database-connection details, hostnames, usernames, passwords, client-tool
  suggestions, or `<DROPLET_IP>` placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each field
must be fully populated and candidate-ready where applicable:

{{
  "name": "A kebab-case GitHub repository name under 50 characters that describes the legal RAG context-budget repair task without using placeholders.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name.",
  "question": "The full candidate-facing task description written like a realistic engineering ticket: describe the legal research assistant symptoms, the high-level expected outcome, the mocked-test validation path, and the real-key runtime note without revealing the exact implementation.",
  "code_files": {{
    "README.md": "The complete candidate-facing README content with exactly the four required sections in the required order: Task Overview, Objectives, Helpful Tips, and How to Verify.",
    ".gitignore": "A complete Python project gitignore covering local secrets, virtual environments, Python caches, pytest caches, logs, coverage, and optional local vector-store artifacts.",
    "pyproject.toml": "A complete native Python project manifest defining dependencies for anthropic, chromadb or a local Chroma-compatible facade, python-dotenv, pytest, package discovery, and pytest configuration.",
    ".env.example": "A safe example environment file containing empty Anthropic API key configuration and a configurable maximum context token budget with no real secrets.",
    "src/legal_rag/__init__.py": "A minimal package initializer for the legal_rag source package.",
    "src/legal_rag/config.py": "A complete configuration module that loads the model name, API key, and maximum context token budget from environment variables or .env defaults.",
    "src/legal_rag/context_builder.py": "A complete starter context assembly module containing the deliberately broken assemble_prompt behavior that retrieves scored case chunks but does not yet satisfy token-budget and XML-structure requirements.",
    "src/legal_rag/retriever.py": "A complete local retrieval module or fixture-backed Chroma-style facade that returns scored legal case chunks deterministically for tests and demos.",
    "src/legal_rag/client.py": "A complete Anthropic client wrapper that can call Claude in real runs when an API key is present while remaining easy for pytest fixtures to mock.",
    "src/legal_rag/main.py": "A complete local entry point that assembles a prompt for a sample legal query and optionally performs a real Anthropic call when configured.",
    "data/case_chunks.json": "Realistic legal research fixture data containing case chunk ids, citations, relevance scores, and text long enough to exercise token trimming behavior.",
    "tests/conftest.py": "Complete pytest fixtures that mock Anthropic SDK token counting and model calls so the test suite runs without a real API key.",
    "tests/test_context_builder.py": "Complete pytest tests that initially fail and verify token overflow prevention, lowest-score-first trimming, XML document delimiters, and query separation after the candidate fix."
  }},
  "answer": "Evaluator-facing high-level solution guidance describing the root cause, the expected shape of a strong fix, how token counting and relevance trimming should work, how XML boundaries should separate evidence from the user query, and what the tests prove; do not include full replacement source code.",
  "definitions": "An object of concise term-to-definition pairs for concepts such as context window, token budget, RAG, retrieved chunk, XML delimiter, relevance score, and mocked SDK call.",
  "hints": "A single-line nudge that points the candidate toward inspecting the assembled prompt and its token count without revealing the specific implementation.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on prompts staying within MAX_CONTEXT_TOKENS, relevant legal evidence remaining available, XML boundaries reducing citation hallucination risk, pytest passing, and production-clean Python code.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including Python 3.10+, pytest, basic RAG concepts, Anthropic SDK familiarity, context windows and tokenization, environment-based configuration, and reading small Python modules.",
  "short_overview": "A bullet list summarizing the business problem, the technical focus on Anthropic SDK context assembly for legal RAG, and the expected outcome of bounded, structured prompts validated by tests."
}}

Use these EXACT keys. Do NOT use synonyms: not `task_title` or `heading` for
`title`, not `files`, `repository_structure`, or `repo` for `code_files`, not
`context` or `prompt` for `question`, and not `solution` for `answer`. Do NOT emit
`criterias` because the pipeline injects it. Output raw JSON only — no markdown
fences and no prose around it.

## CRITICAL REMINDERS
- Output must be valid JSON only — no markdown fences, no explanations.
- Generate a pure local Python project. Do NOT include Docker, docker-compose,
  init database scripts, Dockerfiles, deployment files, or service containers.
- The task must match the legal research assistant scenario using the Anthropic
  Python SDK and a ChromaDB-style RAG pipeline.
- The candidate's primary work is in context assembly: token budget enforcement,
  relevance-based trimming, and structured XML separation of retrieved case chunks.
- The tests must run with `python -m pytest` and must mock Anthropic SDK calls so
  they do not require a real `ANTHROPIC_API_KEY`.
- Real runs should work when `ANTHROPIC_API_KEY` is set in `.env`.
- The starting repository must be FULLY FUNCTIONAL but intentionally wrong: it
  imports, loads fixtures, and runs tests, while the target behavioral tests fail
  until the candidate fixes the planted defect.
- Never leak the reference answer into `code_files`, README text, comments, or
  docstrings.
- README.md must contain exactly these four sections in this order: Task Overview,
  Objectives, Helpful Tips, How to Verify.
- Keep it INTERMEDIATE and solvable in {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Context Engineering - Anthropic SDK (INTERMEDIATE)": [
        PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_CONTEXT,
        PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_CONTEXT_ENGINEERING_ANTHROPIC_SDK_INTERMEDIATE_INSTRUCTIONS,
    ]
}