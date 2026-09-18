# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python, Retrieval-Augmented Generation (RAG), AI Evaluation, and Vector Databases assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- **CRITICAL**: The generated task must combine advanced RAG, vector database, and AI evaluation work in one coherent production incident or hardening scenario.
- **CRITICAL**: The task must be infrastructure-backed with real Qdrant, PostgreSQL, and Redis services when the selected scenario exercises dense retrieval, governance state, auditability, freshness, or cache behavior.
- **CRITICAL**: The end-to-end answer path must call a real LLM provider when configured through `.env`; readiness and invariant checks may run offline, but the task itself must not use a fake or deterministic model stand-in.
- **CRITICAL**: The generated repository must include docker-compose.yml, init_database.sql, run.sh, Python source, visible invariants, and ADVANCED-only hidden grading checks where visible checks would reveal the answer.
- **CRITICAL**: No kill.sh is needed because E2B sandboxes are destroyed as a whole when the session ends.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, retrieval corpus, vector index, evaluation failure, governance risk, and RAG incident the candidate will be solving.)
2. What will the task look like? (Describe the Python and advanced RAG/vector/evaluation implementation, debugging, architecture, and operational work required, the expected deliverables, and how it aligns with ADVANCED proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python, retrieval-augmented generation, vector databases, hybrid retrieval, production LLM systems, and AI evaluation, you are given a list of real world scenarios and proficiency levels for RAG, AI Evaluation, and Vector Databases.
Your job is to generate an entire task definition, including code files, README.md, docker-compose.yml, init_database.sql, run.sh, expected outcomes, hidden grading checks where appropriate, and verification guidance, that can be used to assess a candidate's ability to diagnose, redesign, implement, evaluate, and harden a production-grade RAG system using ADVANCED-level Retrieval Augmented Generation, AI Evaluation, and Vector Databases skills.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios to frame the task. The business context, domain, corpus, vector-index lifecycle, evaluation incident, governance constraints, and technical requirements should directly align with the selected scenario.
**CRITICAL**: The candidate must receive a FULLY FUNCTIONAL and FULLY POPULATED starting environment: local services start correctly, fixture corpora and metadata are present, schema initialization succeeds, vector collections can be seeded, and the project can be inspected and smoke-checked before the candidate changes anything.
**CRITICAL**: The task must assess advanced RAG, vector database, and AI evaluation judgment and implementation, not language trivia, command memorization, package setup, or rote framework syntax.
**CRITICAL**: The task must include a real LLM provider path for the end-to-end answer workflow. Offline readiness checks may avoid provider calls, but the assessed agent/RAG behavior must not be replaced by a fake model.
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an advanced RAG, AI Evaluation, and Vector Databases practitioner who is expected to independently own production-grade retrieval architecture, vector-index governance, answer grounding, evaluation methodology, observability, rollout safety, and operational trade-offs.

The candidate receives a realistic Python RAG service with multiple interacting modules and infrastructure services already wired together:
- A substantial Python application with retrieval, ranking, context assembly, generation, evaluation, telemetry, governance, and API or CLI boundaries.
- A Qdrant vector store with scenario-specific documents, embeddings, index metadata, payload filters, and provenance already loaded or loadable from fixtures.
- PostgreSQL initialized through init_database.sql for index manifests, document provenance, audit events, evaluation runs, source licensing, user feedback, rollout decisions, or governance state.
- Redis used for retrieval or answer caching where the scenario benefits from cache-versioning, freshness, fail-closed behavior, retry control, or rollout-safety reasoning.
- A real LLM integration using OpenAI, Anthropic, or a LiteLLM-compatible provider configured through `.env.example`; do NOT use fake LLMs, regex intent parsers, deterministic stand-ins, or sleeps to simulate agent/model behavior.
- Visible invariant tests that help the candidate self-check scaffold integrity and observable behavior, plus ADVANCED-only hidden grading checks for exact governance, evaluation, provenance, or reproducibility decisions that should not be revealed to the candidate.

The generated task should feel like a senior production incident, launch-quality gate, or architecture hardening work item. It should require the candidate to read and reason across multiple files, identify silent semantic failure modes, make defensible trade-offs, improve the system across more than one module, and validate the result with trustworthy evaluation. Do NOT ship a toy snippet, a single short file, or a one-line configuration fix.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to diagnose, redesign, implement, and evaluate a meaningful issue in an existing Python + RAG application backed by real infrastructure services.
- The task must be specific and well-scoped for ADVANCED proficiency, while still completable within {minutes_range} minutes.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should be based on one real-world scenario involving an advanced RAG/vector/evaluation failure mode such as cross-tenant leakage, jurisdiction or date-version mismatch, stale or mixed embedding versions, unsafe unfiltered fallback, weak provenance, unsupported citations, retrieval drift, blue/green index promotion risk, blended evaluation scores hiding failure dimensions, or non-reproducible evaluation gates.
- The task should require advanced concepts naturally derived from the competency scopes: dense and sparse retrieval trade-offs, ANN/vector-store metadata filtering, hybrid retrieval, retrieval contracts, context assembly, citation provenance, embedding and index versioning, cache invalidation, auditability, RAG-specific metrics, LLM-as-judge or rubric evaluation, stratified/adversarial evaluation, confidence and faithfulness checks, and rollout safety.
- The task must include a REAL LLM/agent loop for answer generation. The candidate's work must affect real context construction, retriever/tool selection, provider invocation, output validation, retry/timeout handling, grounded response behavior, or evaluation of generated answers.
- **CRITICAL**: FORBIDDEN in the generated task: `FakeLLM`, `StubLLM`, regex-only intent parsing standing in for the model, deterministic model stand-ins, or `time.sleep()` / `asyncio.sleep()` used to simulate agent or tool thinking.
- **CRITICAL**: LLM-free behavior applies only to readiness gates and offline invariant tests. The task itself must require a real provider call when an end-to-end answer run is executed with a provider key.
- **CRITICAL**: For ADVANCED level, underspecify the solution, never the problem. The incident, symptoms, reproducibility cues, corpus facts, evaluation failures, and business risk must be crisp and fair; the exact architecture, thresholds, return shapes, status enums, cache-key design, confidence values, metric weights, and policy constants must be left for the candidate to design and defend.
- **CRITICAL**: Starter stubs, if any, must use bare signatures plus one-line purpose statements that name the symptom only. Do NOT include "Expected shape" blocks, required dict keys, enum vocabularies, exact thresholds, named config constants, or implementation-shaped TODO comments.
- **CRITICAL**: Policy constants such as confidence floors, retry budgets, freshness windows, attribution windows, ACL status values, recall thresholds, and rollback thresholds must not be pre-set if those values are part of the advanced decision being assessed.
- **CRITICAL**: The starter code must be type-complete and importable on the unsolved starter. run.sh must exit 0 on the UNSOLVED starter without any candidate stub being filled in.
- The task must require a substantial and realistic codebase: multiple interacting modules/files in a real project layout, non-trivial existing logic, and required changes across more than one file.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task must avoid out-of-scope primary requirements such as implementing Kubernetes, Terraform/Helm delivery, GPU-only serving, billion-vector deployment, fine-tuning models, or building a distributed cluster as the candidate's main deliverable.
- The task may discuss blue/green index rollout, online evaluation, observability, privacy, residency, and governance as architecture constraints, but the implementation should remain bounded to the local Python/Qdrant/Redis/PostgreSQL scaffold.
- Use `fastembed` or provider embeddings where needed; avoid `sentence-transformers`, `torch`, and `transformers` in the generated starter unless absolutely unavoidable, because they inflate install footprint and can break the sandbox.
- Include REAL INFRASTRUCTURE, NOT A STAND-IN: Qdrant must genuinely run for vector retrieval, PostgreSQL must genuinely hold manifests/provenance/audit/evaluation state, Redis must genuinely run when freshness or cache behavior is part of the scenario, and the answer path must genuinely call a provider when configured.
- Include a scoping axis that a naive solution ignores, such as tenant, hospital, jurisdiction, product line, region, environment, document version, effective date, corpus lineage, or index generation. The failure should be silent and plausible rather than an obvious crash.
- Include traceability: every answer, citation, retrieved passage, evaluation verdict, or rollout decision should be attributable back to exact inputs such as document ids, chunk ids, character spans, embedding version, index manifest, query scope, retrieved evidence, provider run, or evaluation dataset version.
- Include a quality gate as a first-class deliverable: the task's own evaluation layer must report distinct failure dimensions separately, catch deliberate regressions in each dimension, and tell genuine regression from noise. A single blended "pass/fail" or "answer quality" score is not sufficient for ADVANCED.
- Include reproducibility under re-run: unchanged code and unchanged fixture data must produce the same retrieval set ordering where possible, evaluation dataset membership, metric verdicts, and audit decisions. Any source of nondeterminism introduced by model sampling, unordered iteration, cache state, wall-clock defaults, or unpinned dependencies should be something the candidate can reason about and control.
- The README, question, visible tests, definitions, hints, and starter comments must not enumerate all specific hidden instances the candidate is meant to discover. Name the class of concern, not every concrete policy or data trap.
- The candidate should demonstrate senior-level judgment: root-cause analysis, RAG anti-pattern detection, vector-index reasoning, evaluation design, implementation quality, trade-off articulation, and measurable validation.

For ADVANCED proficiency, the task should combine several connected concepts in a coherent production workflow. Suitable combinations include:
- ACL, residency, tenant, or date-version filters leaking across dense retrieval, sparse retrieval, reranking, context assembly, citation generation, and evaluation.
- Embedding-version mismatch across ingestion, Qdrant collections, PostgreSQL manifests, Redis cache keys, citations, and answer generation.
- Hybrid retrieval that silently degrades into unsafe unscoped evidence without low-confidence signaling or audit records.
- Index manifest and blue/green promotion logic that must keep corpus, embedding model, dimension, payload schema, retrieval configuration, and evaluation dataset version consistent.
- Retrieval-aware prompt construction with source provenance, citation enforcement, guarded abstention, provider-call observability, and post-generation validation.
- Offline evaluation fixtures for retrieval relevance, attribution, freshness, citation grounding, faithfulness, and failure-mode separation, plus hidden checks for governance-sensitive design choices.
- Telemetry and audit events that expose retrieval stage decisions, cache behavior, index freshness, evaluation drift, and failure modes without leaking PII.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, RAG/vector database documentation, Qdrant documentation, Redis documentation, PostgreSQL documentation, OpenAI/Anthropic/LiteLLM documentation, AI evaluation documentation, RAGAS/DeepEval/LangSmith/Promptfoo documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can read a substantial codebase, understand a RAG pipeline end to end, reason about vector retrieval contracts, and make defensible choices on governance, grounding, observability, evaluation, and rollout safety.
- AI assistance may help with syntax or research, but the assessment should evaluate whether the candidate can diagnose the incident, design safe retrieval behavior, implement production-quality changes, and build a trustworthy evaluation gate.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + advanced RAG/vector/evaluation task that:
- Draws inspiration from one selected scenario to determine the business context, corpus, vector index, incident, governance constraints, evaluation failure, and operational goals.
- Matches ADVANCED proficiency for Retrieval Augmented Generation, AI Evaluation, and Vector Databases.
- Tests applied skills with ingestion metadata, Qdrant vector retrieval, optional in-process sparse/hybrid scoring, Redis cache behavior, PostgreSQL index manifests/audit/evaluation records, real LLM generation, citation provenance, failure-mode evaluation, and fail-closed behavior.
- Uses the Infrastructure Requirements stack defined below.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.
- Includes enough realistic existing code that the candidate must read and reason about the system before changing it.
- Leaves the core advanced decisions for the candidate and does not reveal exact implementation details in README, question, hints, stubs, visible tests, or definitions.
- Includes a native Python project manifest or requirements file with every dependency imported anywhere in source, tests, bootstrap scripts, and configuration files.
- Ensures all imports and plugins are declared. Cross-check every module referenced by application code, test code, bootstrap code, and configuration before emitting.
- Ensures strict checks in run.sh cannot fail on the unsolved starter. If a candidate-facing test suite is intentionally red until the candidate solves the task, run.sh must treat it as a deployability probe or avoid running it.
- Uses Python 3.11-compatible dependencies such as fastapi, uvicorn, pydantic, pydantic-settings or python-dotenv, qdrant-client, redis, psycopg[binary], httpx, tenacity, fastembed, openai, anthropic or litellm, pytest, and lightweight evaluation helpers.
- Does NOT include heavy model packages such as torch, sentence-transformers, or transformers unless the scenario absolutely requires them.

The generated code files must be valid and executable. If the task is a bug-fix task, the starter code should contain logical RAG/vector/evaluation issues, not syntax errors. If the task is an architecture-hardening task, the starter code should include working but unsafe or incomplete behavior that reflects the selected incident.

## Infrastructure Requirements
This is an infra-shaped task. The generated repository MUST include docker-compose.yml, init_database.sql, and run.sh. No kill.sh is needed because E2B sandboxes are destroyed as a whole when the session ends.

Use this lightweight local infrastructure shape unless the selected scenario explicitly requires a narrower subset:
- Qdrant for dense vector retrieval over the scenario corpus.
- PostgreSQL for index manifests, document provenance, audit events, evaluation records, source licenses, feedback, rollout decisions, or governance state initialized by init_database.sql.
- Redis for cache/freshness/versioning behavior when the incident involves cached answers, retrieval candidates, stale evidence, retry budgets, deterministic replay, or rollout safety.
- The Python application runs on the host inside /root/task, not in an app container. Only datastores run in Docker.
- The end-to-end answer path must call a real LLM provider when a provider key is present. `.env.example` must declare provider key variables such as `OPENAI_API_KEY=` and/or `ANTHROPIC_API_KEY=` with no real secrets.
- Readiness checks and visible invariant tests must be able to run offline without a provider key by validating imports, fixtures, schemas, retrieval contracts, datastore health, and non-generation behavior only.

Required dependency approach:
- The primary Python runtime is pre-installed by the E2B template; do NOT apt-get or system-install Python.
- run.sh's FIRST project step after changing to /root/task MUST install the task's own dependencies, for example `python3 -m pip install -q -r requirements.txt`.
- The starter must be FULLY FUNCTIONAL and FULLY POPULATED on first boot.
- run.sh is a readiness/self-check script, NOT the grader.
- run.sh must exit 0 on the UNSOLVED starter, WITHOUT any candidate stub being filled in.

### Docker-compose Instructions
- Generate a docker-compose.yml with NO top-level `version` field. **MUST NOT include any version specification**.
- The compose file MUST define only the datastore services needed by the scenario; for the recommended advanced RAG/vector/evaluation incident shape, include `qdrant`, `redis`, and `postgres`.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Qdrant should use a stable qdrant image, expose `127.0.0.1:6333:6333`, define persistent storage, and include a healthcheck that verifies the HTTP readiness endpoint.
- Redis should use a stable redis image, expose `127.0.0.1:6379:6379`, define an appropriate healthcheck such as `redis-cli ping`, and avoid passwords unless the starter code consistently uses them.
- PostgreSQL MUST use inline service environment values:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- Forbid `.env` files or `${{VAR}}` host indirection for datastore initialization values. Inline service environment values are required because the image will NOT initialize without them.
- The init SQL, healthcheck, and application connection string must use the same PostgreSQL user and database.
- PostgreSQL ports MUST use `127.0.0.1:5432:5432`.
- PostgreSQL healthcheck MUST use `pg_isready` with the same inline user/database values.
- Do not include a Dockerfile unless you intentionally containerize an app helper. For this task, prefer host-run Python app plus containerized datastores.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else (flags, paths, `&&`, the rest of the pipeline) becomes bash's positional parameters and is silently dropped (e.g. `mkdir -p /a && tail -f /dev/null` breaks into `mkdir: missing operand`). Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.

### init_database.sql Instructions
- Generate init_database.sql at the repository root.
- It must be mounted into the PostgreSQL service via `/docker-entrypoint-initdb.d/init_database.sql:ro`.
- It must initialize realistic governance and operations tables for the chosen scenario, such as index manifests, document provenance, chunk lineage, retrieval audit events, generation audit events, evaluation datasets, evaluation cases, evaluation runs, source licenses, user feedback, rollout decisions, or safety incidents.
- It must be valid PostgreSQL SQL and idempotent where possible.
- It must not solve the candidate's task by encoding all policy decisions, final thresholds, exact scoring weights, exact status vocabulary, or complete retrieval contracts in a way that gives away the answer.
- It should include enough seed data to make the starter environment FULLY POPULATED and inspectable.
- It should include realistic related tables with foreign keys, indexes, constraints, status columns, audit columns such as created_at and updated_at, lifecycle or archived flags, and domain-specific names.
- It should seed enough rows that the answer cannot be seen by eyeballing the SQL file alone. Use deterministic generation patterns for volume where helpful, but keep seed size small enough to initialize in seconds.
- Seeded data should include production-like mess where relevant: nullable fields, duplicate-looking rows that differ in meaningful metadata, archived or superseded documents, unicode and apostrophes in names, timestamps across boundaries, exact decimal values for costs where needed, out-of-order sequences, and boundary cases around scope or lifecycle.
- The seeded data must be internally consistent: foreign keys resolve, manifests match declared collections, versions follow a legal lifecycle, and evaluation datasets form a coherent world.
- It should avoid secrets and avoid production credentials.

### Qdrant / Redis Configuration Instructions
- Qdrant fixtures should be loaded by a Python setup or ingestion script using scenario-specific documents, chunk text, tenant or scope metadata, embedding version metadata, source provenance, effective dates, and any ACL/residency fields that make the incident reproducible.
- Qdrant collections and payload fields should be realistic enough to expose advanced RAG/vector failure modes, but visible fixtures must not pre-decide all hidden grading expectations.
- Do not use fake embeddings if the retrieval path being assessed needs semantic behavior. Use fastembed or provider embeddings for corpus/query vectors in the scaffold.
- Redis may be pre-populated only with safe fixture keys that demonstrate stale or version-sensitive behavior; do not hard-code the final cache-key design the candidate should choose.
- Any cache keys shown in code or fixtures must be scenario-specific and must not reveal the complete solution contract.
- Redis behavior should remain bounded and deterministic enough for readiness and visible invariant checks.

### Run.sh Instructions
- Generate run.sh at the repository root and make it executable in the JSON file content.
- run.sh is a readiness/self-check script, NOT the grader.
- It MUST begin by changing to `/root/task`.
- It MUST install dependencies as its first project action, for example `python3 -m pip install -q -r requirements.txt`.
- It MUST run `docker compose up -d` for the datastore services.
- It MUST wait for PostgreSQL, Qdrant, and Redis health/readiness using bounded retry loops and clear error messages.
- It MUST export connection variables for the local host-run app, such as `DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb`, `QDRANT_URL=http://localhost:6333`, and `REDIS_URL=redis://localhost:6379/0`.
- It MUST initialize or verify fixture data using safe setup commands such as `python3 -m app.bootstrap` or `python3 -m app.ingestion`.
- It MUST verify the starter project compiles/loads using an import smoke or lightweight offline invariant check that does not require an LLM provider key.
- It MUST NOT run the grader test suite that is designed to fail until the candidate solves the task.
- If you include a visible invariant suite and run any test command from run.sh, run.sh must treat tests as a deployability probe only: exit 0 when the runner collected and executed the suite even if tests fail by design, and exit non-zero only for import errors, missing dependencies, collection/config errors, usage errors, or no tests collected. For pytest, mirror this shape:
  - `python3 -m pytest -q invariants; rc=$?`
  - If rc is 0 or 1, run.sh exits 0 for deployability.
  - If rc is 2 or greater, or rc is 5, run.sh exits non-zero.
- Prefer an import smoke over running candidate-facing tests from run.sh to avoid conflating designed failures with a broken scaffold.
- If the FastAPI app is started by run.sh, start uvicorn in the background using nohup so the script returns. Do not block forever.
- Every Python invocation inside shell scripts MUST use `python3`, never bare `python`.
- run.sh must exit 0 on the UNSOLVED starter, WITHOUT any candidate stub being filled in. Design the starter so that is true by construction.

### Dockerfile Instructions
- Do not include a Dockerfile unless the scenario intentionally containerizes an app helper.
- For this task, prefer a host-run Python app with only Qdrant, Redis, and PostgreSQL running in Docker.
- If a Dockerfile is included for a helper, it must use a lightweight official Python image, install only declared project dependencies, avoid runtime apt-get for Python itself, and not require provider keys or candidate-completed logic for readiness.

The output should be a valid json schema:
- `README.md` with the exact candidate-facing sections specified below.
- `.gitignore` with Python, environment, cache, log, and local datastore artifacts excluded.
- `.env.example` with provider key placeholders and local datastore URLs, but no secrets.
- `requirements.txt` with all Python project dependencies needed by the starter, bootstrap, real LLM integration, Qdrant, Redis, PostgreSQL access, evaluation helpers, and tests.
- `docker-compose.yml` with Qdrant, Redis, and PostgreSQL datastore services as required by the scenario, no version field, localhost-only port bindings, inline PostgreSQL initialization environment values, mounted init_database.sql, persistent volumes, and healthchecks.
- `init_database.sql` with PostgreSQL schema and seed data for manifests, provenance, audit, evaluation, or governance records.
- `run.sh` that installs dependencies, starts datastores, waits for readiness, seeds or verifies fixtures, performs an offline smoke check, and exits correctly on the unsolved starter.
- A substantial Python application under `app/` with multiple modules such as configuration, models, ingestion, embeddings, dense retrieval, sparse or hybrid retrieval, reranking, context assembly, generation, citations, audit logging, evaluation, and API entry points.
- Scenario-specific fixture data under `data/` or `fixtures/`.
- Visible invariant tests under `invariants/`.
- ADVANCED-only hidden grading tests under the optional top-level `hidden_tests` envelope when a check would reveal the solution if shipped to candidates.

## Code file requirements
- More than one file must be generated, and all files must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines and modern Python 3.11+ practices.
- Use clear module boundaries and a readable project structure.
- The generated starter code must be runnable and inspectable, with valid imports and no syntax errors.
- The generated starter code MUST NOT contain the full implementation for the core advanced logic of the task.
- The core retrieval contract, scope filtering strategy, cache-versioning strategy, fail-closed policy, citation provenance behavior, evaluation dimensions, reproducibility controls, or rollout decision logic that the candidate must design should be incomplete, flawed, or minimally stubbed while remaining type-complete and importable.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments, "implement this" comments, placeholder hints, empty pass-only bodies, or intentionally missing imports.
- Do NOT use fake LLMs or deterministic stand-ins for generation. The app's generation path must call a real provider through OpenAI, Anthropic, or LiteLLM when configured.
- Visible tests must not hard-code answer-revealing internal shapes, exact thresholds, enum values, metric weights, field names, or policy constants that the candidate is supposed to design.
- For ADVANCED level, split tests when needed: candidate-visible `invariants/` should check scaffold integrity and observable outcomes, while optional hidden tests may check governance-sensitive or exact contract behavior that would reveal the answer.
- The starter codebase must be substantial and realistic, not a toy snippet. Require multiple interacting modules and changes across more than one file.
- Include proper logging and error handling in the scaffold without solving the candidate's task.
- Ensure all paths reference /root/task as the base directory.
- The project must include enough fixture corpus and evaluation data for the candidate to inspect real retrieval behavior, citation behavior, failure dimensions, and reproducibility.
- The task's own evaluation layer must report distinct failure dimensions separately, such as retrieval relevance, attribution, citation grounding, freshness, scope isolation, faithfulness, latency, or cost. Do not generate one blended score as the only quality gate.
- The evaluation layer must be capable of catching deliberate regressions in each dimension without revealing hidden grading decisions in candidate-visible tests.
- The generated data and code must be bounded so install, seed, bootstrap, and readiness complete inside a small sandbox with 2 vCPU and about 2 GB RAM.

## .gitignore INSTRUCTIONS
Create a sensible Python gitignore for an advanced RAG/vector/evaluation task, including:
- __pycache__/
- *.pyc
- *.pyo
- *.pyd
- .Python
- .venv/
- venv/
- env/
- .env
- .pytest_cache/
- .mypy_cache/
- .ruff_cache/
- .coverage
- htmlcov/
- *.log
- logs/
- build/
- dist/
- *.egg-info/
- .DS_Store
- qdrant_storage/
- postgres_data/
- redis_data/
- tmp/
- .cache/
- generated evaluation outputs that are not committed fixtures
- local benchmark artifacts
- local datastore exports or dumps unless intentionally committed as fixtures

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain exactly the following output sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four README sections MUST be emitted as an actual markdown heading in this exact order: `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify`. A plain unmarked text line with the section name is INVALID and counts as a missing section.

### Task Overview
- 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Must be specific to the selected real-world scenario and the RAG/vector/evaluation incident.
- Must explain the downstream impact of untrustworthy retrieval, unsupported answers, stale evidence, unsafe scope leakage, weak evaluation, or rollout risk.
- Must not include setup commands, database connection details, credentials, client-tool suggestions, absolute working directories, or remote-host placeholders.

### Objectives
- INTERMEDIATE/ADVANCED objectives MUST be concise and OPEN-ENDED.
- Use 3-4 bullets maximum; fewer, tighter is better.
- Because this is an ADVANCED design/build/hardening task, use plain goal statements rather than stakeholder-framed before/after bullets.
- Each objective is ONE SHORT PLAIN SENTENCE, roughly 5-15 words, naming the outcome the system must achieve.
- One concern per bullet; split a bullet that bundles two separable concerns.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, or any other direct code reference.
- Do NOT describe current-vs-after behavior using phrasing like "currently does X" or "after your changes".
- Do NOT enumerate the specific instances the candidate is meant to discover. Name the class of concern; never list all concrete tenants, dates, jurisdictions, metrics, fields, tables, or policy traps.
- Every objective must pass the agent-paste test: pasted alone into an AI coding agent without the repository, it must not be sufficient instruction to implement anything.
- At ADVANCED level, ZERO enumerated instances should appear anywhere in the Objectives.
- Include AT LEAST ONE question-form objective that invites judgment beyond the stated scope.
- Good style examples:
  - "Keep generated answers grounded in eligible evidence."
  - "Make evaluation failures separable and reproducible."
  - "Preserve evidence provenance across the answer lifecycle."
  - "What other risks should the quality gate surface before rollout?"

### Helpful Tips
- 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, algorithm, exact threshold, enum vocabulary, or policy constant that solves the task.
- Keep tips oriented to symptoms, trade-offs, and places to reason, not step-by-step implementation.
- Do not enumerate the specific hidden instances the candidate is expected to infer from the corpus, manifests, audit records, and evaluation data.

### How to Verify
- 3-5 bullets maximum.
- Frame verification in terms of observable outcomes.
- Because this is an ADVANCED design/build/hardening task, name an experiment to run and where to look, without stating every correct result.
- Pattern: "<make this change or run this scenario>, and <where to look>", one probe per objective, in the same order where possible.
- Do NOT state the pass condition in a way that restores the implementation rule the Objectives withheld.
- Probes must not enumerate the concrete hidden instances the candidate is meant to discover.
- At most ONE bullet may reference the task environment directly.
- Because tasks with a real LLM use `.env.example` declaring provider keys, How to Verify MUST open with a GitHub note admonition embedded INSIDE the section as a blockquote, never as a new heading:
  - `> [!NOTE]`
  - `> Copy `.env.example` to `.env` and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.`
- Any legitimate local verification command must use localhost. Never use a droplet IP or remote-host placeholder.
- Do not include database host, port, username, password, or client-tool suggestions in the README.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, or similar install/start commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, data-structure names, algorithms, thresholds, metric weights, or policy constants that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Database-connection details including host, port, username, password, or client-tool suggestions.
- `<DROPLET_IP>` placeholders or any remote-host placeholder.
- Extra README sections such as Application Access, Database Schema Overview, Database Access, Architecture, Performance Issues, Evaluation Rubric, or NOT TO INCLUDE.

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the advanced RAG/vector/evaluation incident without duplicating the title.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on the scenario's RAG, vector-index, and evaluation improvement goal.",
  "question": "A full candidate-facing task description written as a scenario paragraph plus a direct imperative ask. It must explain who the candidate is, what system they are working on, the situation that makes the system untrusted, and the outcomes the work must achieve, without revealing the answer. Do not include file names, file paths, directory paths, function names, method names, class names, variable names, direct solution statements, exact policy constants, metric weights, or enumerated hidden instances. The question and README Objectives must be written at the same altitude and checked together so neither one gives away the mechanisms the other withholds.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (`## Task Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify`) — a plain unmarked text line with the section name is INVALID and counts as a missing section. The README must follow the open-ended ADVANCED guidance and exclude setup commands, connection details, direct solutions, and extra headings.",
    ".gitignore": "A comprehensive Python and local-infrastructure gitignore that excludes virtual environments, caches, logs, local environment files, local datastore artifacts, generated evaluation outputs, and benchmark artifacts.",
    ".env.example": "A safe environment template containing empty provider key placeholders such as OPENAI_API_KEY and ANTHROPIC_API_KEY plus local service URL defaults, with no real secrets.",
    "requirements.txt": "The Python dependencies needed to run the substantial starter application, bootstrap fixtures, real LLM provider integration, Qdrant, Redis, PostgreSQL access, evaluation helpers, and tests without heavy torch-based packages.",
    "docker-compose.yml": "A datastore-only compose file with no version field, localhost-only port bindings, Qdrant, Redis, and PostgreSQL services as required by the scenario, inline PostgreSQL initialization environment values, mounted init_database.sql, persistent volumes, and healthchecks.",
    "init_database.sql": "A PostgreSQL initialization script that creates and seeds realistic manifest, provenance, audit, evaluation, feedback, rollout, or governance tables needed by the scenario without encoding the final candidate solution.",
    "run.sh": "An executable readiness script that changes to /root/task, installs dependencies first, starts datastore services with docker compose up -d, waits for health, exports local connection variables, seeds or verifies fixtures, performs an offline smoke check, and exits successfully on the unsolved starter without running the failing grader suite.",
    "app/__init__.py": "A package marker for the Python application.",
    "app/config.py": "Configuration loading for local datastore URLs, provider selection, corpus identity, evaluation dataset identity, and runtime settings without hard-coding secrets or answer-revealing policy constants.",
    "app/models.py": "Pydantic request, response, evidence, citation, audit, manifest, and evaluation models with enough structure for the application to run while leaving advanced policy decisions to the candidate where appropriate.",
    "app/main.py": "The FastAPI or service entry point exposing health and scenario-specific answer or evaluation endpoints that orchestrate retrieval, context assembly, generation, auditing, evaluation, and error handling.",
    "app/bootstrap.py": "A bootstrap module that verifies datastore connectivity, initializes Qdrant collections or Redis fixture state, and loads scenario corpus fixtures using safe local commands.",
    "app/ingestion.py": "Ingestion logic for scenario documents, chunk metadata, provenance, embedding version fields, lifecycle fields, and Qdrant payloads, with realistic gaps tied to the incident.",
    "app/embeddings.py": "A lightweight embedding wrapper using fastembed or a provider embedding path appropriate for the scenario and compatible with the local sandbox.",
    "app/dense_retrieval.py": "Qdrant dense retrieval logic that is realistic and runnable but contains or exposes the scenario's advanced retrieval-contract issue.",
    "app/sparse_retrieval.py": "A lightweight sparse or lexical retrieval component used for hybrid behavior where the scenario benefits from dense and keyword evidence.",
    "app/hybrid_retrieval.py": "Hybrid candidate assembly logic that combines retrieval signals without revealing final weighting, confidence, fallback, or scoping decisions.",
    "app/rerank.py": "A reranking or candidate selection component that participates in the incident without revealing the final contract, threshold, or policy design.",
    "app/context_assembly.py": "Context construction and evidence packaging logic that passes retrieved material toward generation while leaving grounding and provenance fixes to the candidate.",
    "app/generation.py": "A real LLM provider integration that builds prompts from retrieved evidence and calls OpenAI, Anthropic, or LiteLLM when a provider key is configured, with no fake model stand-in.",
    "app/cache.py": "Redis-backed cache logic for answer or retrieval artifacts where the scenario requires freshness, index-version, rollout, or scope-safety reasoning.",
    "app/audit.py": "PostgreSQL-backed audit and manifest helpers that record retrieval, generation, evaluation, provenance, cache, or rollout events relevant to governance and operations.",
    "app/evaluation.py": "Offline evaluation helpers for retrieval quality, citation correctness, attribution, freshness, faithfulness proxies, reproducibility, or scenario-specific quality gates without exposing hidden grading decisions.",
    "app/cli.py": "A command-line entry point for bootstrapping fixtures, running offline evaluation, inspecting observable behavior, and invoking the real end-to-end answer path when provider keys are configured.",
    "data/corpus.jsonl": "Scenario-specific corpus fixtures with realistic text, provenance, scope metadata, lifecycle fields, embedding version fields, and document-level attributes needed for the incident.",
    "data/eval_queries.jsonl": "Scenario-specific evaluation queries and observable expectations that support self-checking across retrieval, grounding, attribution, freshness, and quality dimensions without revealing all hidden policies.",
    "data/regression_cases.jsonl": "Scenario-specific regression fixtures used by the starter evaluation layer to expose distinct quality dimensions without encoding the complete hidden oracle.",
    "invariants/test_scaffold.py": "Visible pytest checks that validate imports, fixture shape, datastore bootstrap behavior, and non-secret offline invariants.",
    "invariants/test_observable_behavior.py": "Visible pytest checks for candidate-observable RAG/vector/evaluation behavior that do not hard-code solution-only thresholds, status enums, metric weights, or internal policy constants."
  }},
  "hidden_tests": {{
    "grading/test_scope_and_provenance.py": "Optional ADVANCED-only hidden grading tests for exact scope isolation, provenance preservation, citation attribution, and fail-closed behavior that would reveal the solution if shipped to candidates.",
    "grading/test_evaluation_gate.py": "Optional ADVANCED-only hidden grading tests for separated evaluation dimensions, deliberate regression detection, reproducibility under re-run, and rollout-quality decisions that visible tests must not disclose."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the intended advanced RAG, vector database, and AI evaluation architecture, retrieval-contract reasoning, governance safeguards, provenance model, evaluation strategy, reproducibility approach, and operational trade-offs at a non-code level.",
  "definitions": "An object mapping important scenario-specific RAG, vector-index, retrieval, governance, cache, provenance, evaluation, grounding, rollout, and LLM-provider terms to concise definitions useful for evaluators and candidates without revealing the exact fix.",
  "hints": "A single-line nudge that points candidates toward investigating the evidence flow, scoping assumptions, quality-gate dimensions, and operational symptoms without naming the exact fix, thresholds, APIs, internal shapes, hidden instances, or policy constants.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable retrieval safety, vector-index correctness, answer grounding, freshness, auditability, separated evaluation dimensions, reproducibility, and production-level code quality; one line must explicitly mention clean code, naming, exception handling, logging, and clear project structure.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3.11 proficiency, comfort with Docker-backed datastores, advanced RAG retrieval knowledge, familiarity with Qdrant and vector metadata, understanding of AI evaluation methods, and familiarity with real LLM provider keys; never include imperative setup or verification steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first describe what the system is and who relies on it, second describe what this rework needs to achieve without mechanism names or enumerated defects, and third describe what separates a strong submission while closing on whether the design reasoning is sound."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The generated task must align with ADVANCED Retrieval Augmented Generation, AI Evaluation, and Vector Databases proficiency and the provided competency scopes.
3. The generated task must draw from one provided real-world scenario and must not invent an unrelated domain.
4. The generated repository MUST include docker-compose.yml, init_database.sql, and run.sh for this infra-shaped task.
5. No kill.sh is needed; E2B sandboxes are destroyed as a whole.
6. docker-compose.yml MUST NOT include any version specification.
7. Datastore ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
8. PostgreSQL MUST set POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB inline in the service environment, and init SQL, healthcheck, and connection strings must use the same user/database.
9. Qdrant must be a real running vector database for the assessed retrieval behavior; do not replace it with an in-memory list or stub.
10. Redis must be a real running service when the scenario uses cache, freshness, rollout, retry, or deterministic replay behavior.
11. run.sh must install Python dependencies first, start datastores, wait for health, seed or verify fixtures, and avoid running a failing grader suite.
12. run.sh must exit 0 on the unsolved starter when the scaffold is deployable.
13. Every Python invocation in shell scripts must use `python3`, never bare `python`.
14. The task must include a real LLM provider integration; do NOT generate FakeLLM, StubLLM, deterministic stand-ins, regex-only model replacements, or simulated thinking sleeps.
15. LLM-free behavior applies only to readiness gates and offline invariant tests; the end-to-end answer path must use a real provider when configured.
16. Visible README Objectives for ADVANCED must be concise, open-ended, and must not name solution APIs, files, functions, classes, algorithms, thresholds, metric weights, policy constants, or enumerated hidden instances.
17. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as a markdown heading, with no extra headings.
18. Do not include setup commands, direct solutions, database connection details, client-tool suggestions, or `<DROPLET_IP>` placeholders in the README.
19. Use substantial multi-file starter code appropriate for 3-5+ years of experience; do not generate a toy snippet or single-file fix.
20. Include a real scoping axis, exact traceability, a quality gate as a deliverable, and reproducibility under re-run.
21. The task's own evaluation layer must report distinct failure dimensions separately, not one blended score.
22. Split tests for ADVANCED only when visible checks would reveal the solution; use the optional hidden_tests envelope for answer-revealing grading checks.
23. Keep secrets out of version control and use `.env.example` only for empty provider-key placeholders.
24. Every dependency imported anywhere in source, bootstrap code, tests, or configuration must be declared in requirements.txt.
25. The generated starter must be FULLY FUNCTIONAL and FULLY POPULATED, with realistic but bounded data that seeds quickly in a small sandbox.
26. The task must be completable within {minutes_range} minutes.
"""

PROMPT_REGISTRY = {
    "AI Evaluation (ADVANCED), Retrieval Augmented Generation (RAG) (ADVANCED), Vector Databases (ADVANCED)": [
        PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_CONTEXT,
        PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_INPUT_AND_ASK,
        PROMPT_AI_EVALUATION_RAG_VECTOR_DATABASES_ADVANCED_INSTRUCTIONS,
    ]
}