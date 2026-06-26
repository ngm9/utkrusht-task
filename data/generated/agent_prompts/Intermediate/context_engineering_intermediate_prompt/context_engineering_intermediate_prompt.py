# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


# task_generation_prompts/Intermediate/context_engineering_intermediate_prompt.py
#
# Task-generation prompt module for Context Engineering · INTERMEDIATE.
# Exports PROMPT_REGISTRY for infra/utils.py prompt loading.
# All literal braces inside prompt strings are doubled so downstream str.format()
# only consumes the supported placeholders.

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
who can design, debug, and implement practical context pipelines for LLM systems.
"""

PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide
you with the specific inputs for generating a Context Engineering assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

TIME EXPECTATION:
The task must fit in {minutes_range} for a strong INTERMEDIATE candidate. Scope it
as a focused build-it/debug-it work item: roughly 5 minutes to inspect the repo and
start the infrastructure, 10 minutes to understand the context pipeline failure,
and the remaining time to implement or repair one well-isolated context decision.

QUESTION CALIBRATION SIGNAL:
{question_prompt}

You are generating ONE realistic, INTERMEDIATE "build-it" assessment task for a
Context Engineering candidate. This is a coding/debugging session, NOT a
write-a-memo, essay, quiz, or pure system-design exercise.

You MUST draw inspiration from ONE of the real-world scenarios provided above to
create the task. Use the provided real-world scenario as the basis for this task -
do not invent a different domain. When multiple scenarios are listed, pick the one
whose technical surface area best fits the candidate level. The task scenario
should closely align with the business context, technical requirements, and domain
described in the selected real-world scenario.

The generated task should test applied context engineering judgment, such as:
- separating model knowledge from runtime context;
- assembling prompts with clear layers for instructions, user input, retrieved
  evidence, tool outputs, and state;
- improving a retrieval, caching, memory, or token-budget decision;
- preserving tenant/session boundaries and freshness constraints;
- debugging context failures using traces, fixtures, logs, or tests;
- validating groundedness, recall/precision, hallucination risk, latency, and
  context size.

For this task shape, include an external service in docker-compose because the
selected scenario exercises a datastore, cache, vector store, search service, or
similar backing context component. Do not add unrelated infrastructure. If the
scenario is the fare-rules latency/cache scenario, the external service should be
the cache or datastore actually used by the candidate-facing code, with the
business rule source and cache behavior represented consistently across fixtures,
tests, README, and scripts.

Before generating the final task, briefly internalize:
1. Which real-world scenario you selected and why it fits Context Engineering at
   INTERMEDIATE level.
2. Which single context-pipeline failure the candidate must fix: retrieval scope,
   stale/duplicated memory, prompt assembly, token budgeting, context-aware
   caching, tenant isolation, evidence formatting, or grounding behavior.
3. Which external service the task genuinely needs, and which files start the
   candidate in a FULLY FUNCTIONAL but intentionally incomplete local project.
"""

PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Context Engineering for LLM systems,
you are given a list of real world scenarios and proficiency levels for Context
Engineering. Generate ONE INTERMEDIATE build-it/debug-it task that requires the
candidate to improve a runnable context pipeline, not merely describe one.

The task must be practical and time-bounded. It should ship a FULLY FUNCTIONAL
starter project with a FULLY POPULATED local dataset or fixture set, an external
datastore/cache/vector/search service started by docker-compose, failing or
incomplete behavior that is visible through tests or traces, and a focused
candidate implementation area.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an intermediate AI Agent / Context Engineering practitioner with
a few years of experience. They should be able to independently reason about
runtime context, retrieval, memory/state, token budgets, prompt templates, access
scoping, and evaluation signals, but they should not be expected to design an
entire enterprise RAG platform from scratch.

The assessment should feel like a realistic work item from an engineering team:
a context-rich assistant is returning stale, noisy, slow, ungrounded, or unsafe
answers because of a narrow context-pipeline flaw. The candidate must inspect the
provided code, fixtures, and tests, then make a pragmatic fix.

The employer in `organization_background` is administering the assessment. The
task's business domain must come from ONE selected real-world scenario, not from
the employer background unless the scenario itself uses that domain.

## INSTRUCTIONS

### Nature of the Task
- Create a build-it/debug-it repository for Context Engineering at INTERMEDIATE
  level. The candidate should modify 1-2 source files, roughly 50-120 lines of
  implementation, and should not need to write a large new subsystem.
- **CRITICAL**: Stay within the Context Engineering scope. Valid task centers
  include context-aware caching, retrieval filtering/scoping, prompt assembly,
  evidence formatting, context token budgeting, memory deduplication/freshness,
  tenant/session isolation, or groundedness evaluation.
- **CRITICAL**: Do NOT turn this into a pure prompt-writing exercise, an essay,
  a generic LLM app wiring task, a frontend task, a fine-tuning/model-training
  task, or a framework trivia drill.
- **CRITICAL**: The candidate must interact with real project files and tests.
  The repo must be runnable locally and include realistic fixtures, traces, or
  seed data that expose the context failure indirectly.
- **CRITICAL**: Because this is an infra-shaped task, include docker-compose.yml,
  run.sh, and kill.sh. The compose stack must contain only the datastore/cache/
  vector/search service the selected scenario actually exercises.
- If the chosen scenario involves repeated access to a stable business-rule or
  reference-data source, a good task can focus on context-aware caching with a
  TTL/freshness key and reuse of cached evidence during final prompt assembly.
- If the chosen scenario involves noisy RAG answers, a good task can focus on
  retrieval filtering, metadata scoping, deduplication, top-k selection, or
  assembling the evidence block without dumping irrelevant documents.
- If the chosen scenario involves multi-turn support or workflow assistance, a
  good task can focus on compact state, memory expiry, durable facts, or session
  isolation.
- If the chosen scenario involves safety/privacy, a good task can focus on
  tenant-aware retrieval, PII redaction before context assembly, or prompt
  injection resistance through clear separation of trusted instructions and
  untrusted retrieved content.
- The difficulty must be INTERMEDIATE: one meaningful context engineering
  decision, at most two tightly-related concerns, no multi-service platform
  sprawl, and solvable within {minutes_range}.
- If you include diagrams, ensure they are written in mermaid format, properly
  indented and also in code blocks.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base
  directory.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find
helpful, including but not limited to Google, Stack Overflow, Context Engineering
articles, Python documentation, Redis/Qdrant/PostgreSQL documentation where
relevant, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- The task is designed to evaluate applied engineering judgment, debugging, and
  implementation ability rather than memorization.
- Candidates may use AI assistants to understand the codebase, but the submitted
  solution must satisfy the provided tests and preserve the stated constraints.
- The task should not depend on hidden trivia, obscure library APIs, or exact
  memorization of framework syntax.
- The candidate should still need to reason about context quality, freshness,
  access scope, token budget, and observable behavior; a one-shot generic LLM
  answer should not be enough to complete it correctly.

## Code Generation Instructions
Generate a local Python project unless the selected scenario explicitly requires
a different runtime. The project should be small, realistic, and runnable from
/root/task.

The candidate-facing repo should usually include:
- a package such as `app/` or `context_pipeline/` containing context assembly,
  retrieval, caching, memory, or prompt-template code;
- one or two candidate files with neutral stubs or intentionally incomplete logic;
- working helper modules for fixtures, tracing, token counting, data loading, or
  service clients;
- tests under `tests/` that check the expected context behavior after the
  candidate completes the work;
- fixtures under `fixtures/` or seed data loaded into the external service;
- README.md with only the required four candidate-facing sections;
- pyproject.toml or an equivalent native runtime manifest;
- docker-compose.yml, run.sh, kill.sh, and a datastore/cache/search configuration
  file when needed.

Do not leak the solution into code comments, README text, function names, fixture
labels, or hints. Candidate stubs may raise `NotImplementedError` with a neutral
one-line contract, but must not describe the implementation strategy. The answer
field is the only place where the reference approach belongs.

Common task patterns that fit this competency:
- a travel support assistant repeatedly fetching the same fare-rule context and
  needing request-scoped or TTL caching keyed by rule version;
- an internal policy Q&A assistant retrieving cross-tenant documents because
  metadata filters are missing or applied too late;
- a workflow copilot stuffing all prior turns into the prompt and exceeding a
  context budget instead of summarizing or selecting relevant state;
- a support agent using stale durable memory because it appends conflicting facts
  without freshness or deduplication;
- a RAG assistant hallucinating when evidence is missing because prompt assembly
  does not separate retrieved evidence, user input, and unknown behavior.

## Infrastructure Requirements
The generated task MUST include infrastructure because the authoritative task
shape is infra. Include only the external service needed by the selected scenario.
Do not add unrelated databases, queues, dashboards, or app containers.

The infrastructure must be deterministic and simple:
- docker-compose.yml starts the datastore/cache/vector/search service.
- run.sh starts the service with `docker compose up -d`, waits for readiness, and
  performs a lightweight readiness check.
- kill.sh tears down containers, volumes, networks, images, and /root/task
  idempotently.
- If seed data is needed, include it as an explicit file such as init_database.sql,
  redis seed commands, JSON fixtures loaded by run.sh, or a tiny Python seed
  script. The starter data must be FULLY POPULATED and internally consistent.

### Docker-compose Instructions
- docker-compose.yml MUST be included for the datastore/cache/vector/search
  service the task actually exercises.
- docker-compose.yml **MUST NOT include any version specification**.
- docker-compose.yml **MUST NOT include environment variables or .env file references**.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using
  `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Do not include an application container unless the scenario absolutely requires
  one. Prefer running the Python project directly on the host and using compose
  only for the backing service.
- Use stable official images where possible. Examples include Redis for
  context-aware caching, Qdrant for vector retrieval, or a simple search service
  when the scenario genuinely requires it.
- Name services clearly, such as `redis`, `qdrant`, or `context-store`.
- Include healthchecks or readiness-friendly commands only when they are reliable
  without credentials or external network calls.
- Keep volumes and networks minimal and named consistently with the repo.

### Redis Configuration Instructions
If the selected scenario uses Redis as the external cache or context store:
- Include a `redis.conf` only if custom TTL, persistence, or eviction behavior is
  needed for the scenario. Otherwise the default Redis image is acceptable.
- Bind Redis only to localhost in docker-compose using `127.0.0.1:6379:6379`.
- Seed data may live in JSON fixtures and be loaded by the app or tests; do not
  require manual Redis CLI setup from the candidate.
- The task may require the candidate to implement cache keys, TTL behavior,
  version-aware invalidation, or reuse of cached evidence, but the README must
  not reveal the implementation details.
- If a different datastore is more appropriate for the chosen scenario, replace
  this with the minimal configuration file or seed mechanism for that datastore,
  but keep the same simplicity and localhost-only binding rules.

### Run.sh Instructions
- Include a run.sh file at the repository root.
- run.sh must start with `#!/usr/bin/env bash` and `set -euo pipefail`.
- run.sh must `cd /root/task` before running project commands.
- run.sh MUST use `docker compose up -d` to start the required external service.
- run.sh must wait for the service to become reachable using a deterministic
  local check, not a sleep-only approach.
- run.sh must not call paid model APIs, require API keys, or contact external
  internet services.
- run.sh must not run the candidate's unfinished implementation in a way that
  causes the readiness check to fail before the candidate starts. It may perform
  imports, seed fixture data, check service connectivity, and print the native
  test command the candidate can run.
- Do not include `apt-get install`, `pip install`, or `npm install` commands for
  runtime or common libraries in run.sh.
- End run.sh with a clear success message such as `ready`.

## kill.sh file instructions
Create a kill.sh file that is safe to run multiple times and performs all cleanup
from /root/task. It must:

1. Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
2. Print a clear log line before every cleanup step.
3. Stop running compose containers with `docker compose down --remove-orphans`
   from /root/task, using `|| true` so the script is idempotent.
4. Remove compose volumes for the task with `docker compose down -v
   --remove-orphans || true`.
5. Remove task-specific Docker networks with `docker network rm <network-name>
   || true` where a custom network was created.
6. Force-remove task-specific images if an app image or custom image was created,
   using `docker rmi -f <image-name> || true`. If no custom image exists, include
   a logged no-op or skip safely.
7. Run `docker system prune -a --volumes -f || true`.
8. Remove the task directory with `rm -rf /root/task || true`.
9. Print `Cleanup completed successfully!` as the final message.

The script must use `|| true` for destructive cleanup commands so repeated runs
do not fail. It must not prompt for confirmation or depend on environment
variables.

The output should be a valid json schema:
- README.md: Candidate-facing concise task overview, helpful tips, objectives,
  and verification instructions only.
- docker-compose.yml: Localhost-bound datastore/cache/vector/search service,
  with no version specification and no environment variables.
- run.sh: Infrastructure startup and readiness script using docker compose up -d.
- kill.sh: Idempotent cleanup script following the nine-step shape above.
- pyproject.toml or equivalent manifest: Native runtime manifest with the small
  set of dependencies used by the project.
- Source files: Starter context pipeline code with one focused incomplete area.
- Tests: Candidate-facing tests that verify context behavior after completion.
- Fixtures or seed files: Fully populated realistic data supporting the scenario.
- Optional datastore configuration: redis.conf, init file, or seed script only
  when required by the chosen datastore.

## Code file requirements
- code_files must be a flat object mapping file paths to full file contents.
- Every file required to run the project must be present; do not reference files
  that are missing from code_files.
- Use realistic names, IDs, timestamps, document versions, tenant IDs, rule
  versions, scores, and trace rows that are internally consistent.
- Include enough data to expose the failure without making the task bulky.
- The source code must be readable and production-like: clear function names,
  typed interfaces where helpful, structured errors, and small modules.
- The candidate's unfinished area must be obvious from running or reading the
  code, but the correct implementation must not be spelled out.
- Tests should verify observable outcomes such as fewer repeated lookups, scoped
  retrieval, preserved citations, no stale context, token budget compliance, or
  safe unknown behavior.
- Avoid brittle tests that require one exact implementation. There should be
  multiple valid approaches that satisfy the context-engineering outcome.
- Do not require live LLM calls, external API keys, paid services, or internet
  access.
- If using a tokenizer or embedding library, keep it lightweight and local.
- If using a vector store, include preloaded or easily seeded data so the task is
  FULLY POPULATED before the candidate begins.

## .gitignore INSTRUCTIONS
Generate a .gitignore appropriate for the runtime and infrastructure. It should
exclude:
- virtual environments and local dependency folders;
- Python caches and test caches;
- local databases, dumps, and generated service data;
- logs, coverage output, and temporary files;
- .env files and local secret material.

Do not ignore source files, fixtures, README.md, tests, docker-compose.yml,
run.sh, kill.sh, or seed/config files required for the task.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the
essential points needed to understand the task. Do NOT overload with too many
bullets — quality over quantity. The candidate should figure out the
implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and
guidance to help them discover solutions.

README.md must contain EXACTLY these output sections, in this order, and no
others:
1. Task Overview
2. Helpful Tips
3. Objectives
4. How to Verify

### Task Overview
- Use the markdown heading `## Task Overview`.
- Write 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the problem matters.
- NEVER leave this section empty.
- Do not include bold time-budget callouts.
- Do not name the exact function, class, or algorithm that solves the issue.
- Do not include database connection details, hostnames, usernames, passwords,
  client-tool suggestions, or `<DROPLET_IP>` placeholders.

### Helpful Tips
- Use the markdown heading `## Helpful Tips`.
- Provide 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: `Consider`, `Think about`,
  `Explore`, `Review`, or `Analyze`.
- Tips guide discovery. They MUST NOT name the specific API, library, function,
  pattern, data structure, or algorithm that solves the task.
- Keep the tips focused on context quality, freshness, scoping, token budget,
  evidence inspection, or observable behavior.

### Objectives
- Use the markdown heading `## Objectives`.
- Provide 4-6 bullets max.
- Frame objectives around outcomes rather than specific technical
  implementations. Objectives describe the what and why, never the how.
- Each bullet must state an observable end-state, not a step or an API/library to
  use.
- Good objectives mention outcomes such as grounded responses, scoped evidence,
  reduced repeated context fetches, preserved freshness, bounded context size,
  tenant-safe retrieval, or stable verification results.
- Do not enumerate file names, function names, exact test names, or hidden
  thresholds as a checklist.

### How to Verify
- Use the markdown heading `## How to Verify`.
- Provide 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and
  the expected behavior, not the specific implementation to write.
- Each bullet should be a check the candidate can run or observe, such as command
  output, test results, response shape, latency observation, log line, cache hit
  count, retrieval trace, or memory reading.
- It may mention running `./run.sh` and the native test command, but it must not
  include setup commands like install commands or docker internals beyond what is
  necessary for verification.

CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):
Keep the following out of README.md:
- Setup commands such as `npm install`, `pip install`, `docker compose up`,
  `mvn test`, or similar installation instructions.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure
  names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like `you should implement`, `add this middleware`,
  `create this class`, or `use <specific API>`.
- Database-connection details such as host, port, username, password, or
  client-tool suggestions.
- Any heading named `NOT TO INCLUDE`, `CONTENT TO EXCLUDE`, or similar in the
  emitted README itself.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each value
must be populated with the generated task content.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the task without using placeholders.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name.",
  "question": "The full candidate-facing task description written like a realistic engineering ticket or incident note; it should describe symptoms, business impact, constraints, and how to start without revealing the implementation.",
  "code_files": "An object mapping every required filepath to the complete file contents for the candidate repository, including README.md, docker-compose.yml, run.sh, kill.sh, manifest, source files, tests, fixtures, and any required datastore configuration or seed files.",
  "answer": "Evaluator-facing high-level solution guidance describing the root cause, expected strong fix, relevant tradeoffs, and evidence in the provided files without duplicating full solution code.",
  "definitions": "An object of concise term-to-definition pairs for context engineering terms used in the task, such as runtime context, retrieved evidence, tenant scope, token budget, freshness, groundedness, cache key, or memory state.",
  "hints": "A single line nudging investigation without revealing the fix; it should point candidates toward inspecting traces, retrieved evidence, repeated lookups, context size, freshness, or access scope.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable context quality, correctness, latency, safety, or reliability improvements. Use simple english.",
  "pre_requisites": "A bullet list of tools and knowledge needed, including basic Python project navigation, docker compose for the provided service, context assembly concepts, retrieval or caching fundamentals, and running the provided tests.",
  "short_overview": "A bullet list summarising the business problem, the context engineering focus, the external service involved, and the expected observable outcome."
}}

Use these EXACT keys. Do NOT use synonyms: not `task_title` for `title`, not
`files` for `code_files`, not `context` for `question`, and not `solution` for
`answer`. Do NOT emit `criterias`; the pipeline injects it. Output raw JSON only
with no markdown fences and no commentary around it.

## CRITICAL REMINDERS
- Output raw JSON only, starting with `{{` and ending with `}}`.
- Generate ONE coherent INTERMEDIATE Context Engineering task, not a list of
  alternatives.
- Use ONE selected real-world scenario as the domain source. Do not drift into
  the employer's domain unless the scenario itself does.
- Because this is an infra-shaped task, code_files MUST include docker-compose.yml,
  run.sh, and kill.sh.
- docker-compose.yml **MUST NOT include any version specification**.
- docker-compose.yml **MUST NOT include environment variables or .env file
  references**.
- **SECURITY-CRITICAL**: every exposed datastore port must be localhost-bound
  using `127.0.0.1:<port>:<port>`.
- run.sh must use `docker compose up -d` and must not require API keys, paid model
  calls, internet access, or package installation.
- kill.sh must follow the nine-step cleanup shape and end with
  `Cleanup completed successfully!`.
- README.md must contain exactly four sections in this order: Task Overview,
  Helpful Tips, Objectives, How to Verify.
- The README must be concise, non-revealing, and must not include setup commands,
  solution steps, direct API names that reveal the fix, or database credentials.
- Keep the candidate work focused: one context decision, at most two tightly
  related concerns, and no advanced platform sprawl.
- The starter project must be FULLY FUNCTIONAL and FULLY POPULATED, while the
  target behavior remains incomplete until the candidate finishes the task.
- The solution and root cause belong only in the `answer` field, never in
  README.md, comments, hints, fixtures, or candidate-facing code.
- Ensure all literal file paths, ports, service names, fixture IDs, tenant IDs,
  versions, and expected behaviors are consistent across every generated file.
- The task must be solvable within {minutes_range}.
"""

PROMPT_REGISTRY = {
    "Context Engineering (INTERMEDIATE)": [
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_CONTEXT,
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_CONTEXT_ENGINEERING_INTERMEDIATE_INSTRUCTIONS,
    ]
}