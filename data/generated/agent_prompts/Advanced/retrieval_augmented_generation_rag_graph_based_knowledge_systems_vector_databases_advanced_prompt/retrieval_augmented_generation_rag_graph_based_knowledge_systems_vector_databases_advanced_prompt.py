# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_GRAPH_RAG_VECTOR_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Target Competencies:
{competencies}

Use this context to calibrate the seniority, production expectations, and engineering judgment required for the assessment. The employer is administering the assessment; the task's business domain must come from the provided real-world scenarios, not necessarily the employer's own industry. The generated task must assess an advanced practitioner who can build and repair production-grade retrieval-augmented generation systems that combine vector search, graph-modeled knowledge, real LLM generation, provenance, governance, and trustworthy evaluation.
"""

PROMPT_GRAPH_RAG_VECTOR_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Graph-based Knowledge Systems + Retrieval Augmented Generation (RAG) + Vector Databases assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- **CRITICAL**: This task must be an ADVANCED infrastructure-backed Python task involving a real Qdrant vector store, a real PostgreSQL-backed graph/provenance layer, and a real LLM answer path when a provider key is present.
- **CRITICAL**: The candidate must receive a FULLY FUNCTIONAL and FULLY POPULATED starter repository that boots, seeds, imports, and smoke-checks successfully without an LLM key.
- **CRITICAL**: The repository may model graph knowledge in PostgreSQL node/edge/provenance tables because the available sandbox datastores do not include a dedicated graph database; do not invent Neo4j, JanusGraph, or other unavailable services.
- **CRITICAL**: The task must stay open-ended at ADVANCED level. Candidate-visible files must describe symptoms and desired outcomes, not exact filters, graph traversal rules, thresholds, status enums, return shapes, or hidden grading logic.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the selected business domain, retrieval corpus, graph-modeled knowledge, vector-index incident, provenance or governance risk, and RAG problem the candidate will be solving.)
2. What will the task look like? (Describe the Python repository, Qdrant/PostgreSQL/Redis infrastructure, real LLM path, planted advanced failure modes, visible invariants, hidden grading envelope where appropriate, and how the task remains open-ended while aligning with ADVANCED Graph-based Knowledge Systems, RAG, and Vector Databases proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GRAPH_RAG_VECTOR_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python, retrieval-augmented generation, graph-based knowledge systems, vector databases, hybrid retrieval, production LLM systems, semantic provenance, and retrieval governance, you are given a list of real world scenarios and proficiency levels for Graph-based Knowledge Systems, Retrieval Augmented Generation, and Vector Databases.
Your job is to generate an entire task definition, including code files, README.md, docker-compose.yml, init_database.sql, run.sh, expected outcomes, hidden grading checks where appropriate, and verification guidance, that can be used to assess a candidate's ability to diagnose, redesign, and improve a production-grade graph-grounded RAG system using ADVANCED-level skills.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios to frame the task. The business context, domain, corpus, graph relationships, governance constraints, and technical requirements should directly align with the selected scenario.
**CRITICAL**: The candidate must receive a FULLY FUNCTIONAL and FULLY POPULATED starting environment: local services start correctly, vector fixtures are loaded or loadable, graph/provenance schema initialization succeeds, cache or manifest fixtures are present when used, and the project can be inspected and smoke-checked before the candidate changes anything.
**CRITICAL**: The task must assess advanced RAG, graph modeling, vector retrieval, provenance, and evaluation judgment, not language trivia, command memorization, package setup, or toy prompt writing.
**FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is an advanced retrieval and knowledge systems practitioner who is expected to independently own production-grade RAG architecture, graph-modeled knowledge, vector retrieval quality, grounding, provenance, governance, observability, evaluation, and rollout safety.

The candidate receives a realistic Python graph-grounded RAG service with multiple interacting modules and infrastructure services already wired together:
- A FastAPI or service-layer Python application with substantial existing ingestion, graph modeling, vector indexing, dense retrieval, sparse or hybrid retrieval, graph expansion, context assembly, real LLM generation, citation, audit, and evaluation code.
- A Qdrant vector store with scenario-specific document chunks and metadata already loaded or loadable from fixtures.
- PostgreSQL initialized through init_database.sql for graph nodes and edges, ontology or relationship metadata, index manifests, source provenance, audit events, evaluation records, and governance state.
- Redis used only when the selected scenario benefits from retrieval cache, freshness, rollout, or answer-version behavior; do not include Redis for decoration if the scenario does not exercise it.
- A real LLM integration using OpenAI, Anthropic, or a LiteLLM-compatible provider configured through `.env.example`; do NOT use fake LLMs, regex intent parsers, deterministic stand-ins, or sleeps to simulate agent/model behavior.
- Visible invariant tests that help the candidate self-check the scaffold and key observable behavior, plus ADVANCED-only hidden grading checks for decisions that would reveal the solution if shipped to the candidate.

The generated task should feel like a senior production incident or architecture hardening work item. It should require the candidate to read and reason across multiple files, identify interacting failure modes, make defensible trade-offs, and implement changes spanning more than one module. Do NOT ship a toy snippet, a single obvious edit, or a narrow syntax exercise.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to diagnose, redesign, and improve a meaningful issue in an existing Python graph-grounded RAG application backed by infrastructure services.
- The task must be specific and well-scoped for ADVANCED proficiency, while still completable within {minutes_range} minutes.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should be based on one real-world scenario involving an advanced failure mode such as tenant or jurisdiction leakage, stale effective versions, unsafe graph expansion across partitions, mixed embedding versions, missing provenance, ungrounded citations, retrieval drift, weak evaluation, cache freshness bugs, or index-promotion risk.
- The task should require advanced concepts naturally derived from the competency scopes: dense-vs-sparse/hybrid retrieval, ANN/vector-store metadata filtering, graph-modeled entity and relationship constraints, temporal or tenant scoping, provenance and lineage, context assembly, citation grounding, embedding/index versioning, cache invalidation, auditability, faithfulness evaluation, and rollout safety.
- The task must include real infrastructure for the assessed components: Qdrant for vector retrieval, PostgreSQL for graph/provenance/governance data, and Redis only when cache/freshness behavior is part of the selected incident. Because the available sandbox services do not include a dedicated graph database, represent graph knowledge with real PostgreSQL node, edge, relationship, statement, provenance, and constraint tables rather than inventing Neo4j, JanusGraph, or any unavailable service.
- The task must include a REAL LLM/agent loop for answer generation. The candidate's work must affect real context construction, retriever/tool selection, provider invocation, output validation, retry/timeout handling, grounded response behavior, or audit behavior.
- **CRITICAL**: FORBIDDEN in the generated task: `FakeLLM`, `StubLLM`, regex-only intent parsing standing in for the model, deterministic model stand-ins, offline replay branches in production code, or `time.sleep()` / `asyncio.sleep()` used to simulate agent or tool thinking.
- **CRITICAL**: LLM-free behavior applies only to readiness gates and offline invariant tests. The task itself must require a real provider call when an end-to-end answer run is executed with a provider key.
- **CRITICAL**: For ADVANCED level, underspecify the solution, never the problem. The incident, symptoms, reproducibility cues, corpus facts, graph facts, and business risk must be crisp and fair; the exact architecture, traversal rules, metadata predicates, thresholds, return shapes, status enums, cache-key design, confidence values, and policy constants must be left for the candidate to design and defend.
- **CRITICAL**: Starter stubs must use bare signatures plus one-line purpose statements that name the symptom only. Do NOT include "Expected shape" blocks, required dict keys, enum vocabularies, exact thresholds, named config constants, or implementation-shaped TODO comments.
- **CRITICAL**: Policy constants such as confidence floors, traversal depth limits, retry budgets, freshness windows, ACL status values, index-promotion thresholds, and rollback thresholds must not be pre-set if those values are part of the advanced decision being assessed.
- **CRITICAL**: The task must include all five ADVANCED system properties in one coherent problem: real infrastructure, a scoping axis a naive solution ignores, traceability from answer to exact source inputs, a quality gate that reports distinct failure dimensions separately, and reproducibility under re-run.
- The scoping axis should be selected from the scenario and may involve tenant, jurisdiction, product, document version, effective date, region, environment, lineage, or lifecycle state. Do not enumerate the exact hidden instances in candidate-facing objectives or question text.
- Traceability must be precise enough that an auditor could re-derive each generated answer from exact Qdrant chunk IDs, graph edge or statement IDs, source document revisions, index manifests, and relevant upstream records.
- The quality gate must be a deliverable in the starter repository. It must separately report retrieval scope correctness, graph attribution, citation groundedness, answer faithfulness, freshness, or index/version consistency as distinct dimensions where relevant; it must not collapse everything into one pass/fail score.
- Re-running the same corpus, graph state, and evaluation fixtures on unchanged code must give the same verdict. Control nondeterminism in fixture ordering, seed generation, retrieval tie-breaking, model configuration where possible, and evaluation output.
- The task must require a substantial and realistic codebase: multiple interacting modules/files in a real project layout, non-trivial existing logic, and required changes across more than one file.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task must avoid out-of-scope primary requirements such as Kubernetes implementation, Terraform/Helm delivery, GPU-only serving, billion-vector benchmarking, dedicated graph database administration, or model fine-tuning as the candidate's main deliverable.
- The task may discuss blue/green index rollout, online evaluation, observability, privacy, and governance as architecture constraints, but the implementation should remain bounded to the local Python/Qdrant/PostgreSQL/Redis scaffold.
- Use `fastembed` or provider embeddings where needed; avoid `sentence-transformers`, `torch`, and `transformers` in the generated starter unless absolutely unavoidable, because they inflate install footprint and can break the sandbox.
- Data realism is required. PostgreSQL should include several related tables for graph nodes, graph edges, source documents, document revisions, entity crosswalks, index manifests, retrieval audit events, generation audit events, evaluation runs, and governance state, with foreign keys, indexes, status/lifecycle fields, audit columns, NULLs where realistic, soft-delete or archived flags, exact-decimal values where the domain uses money, and timestamps spanning boundary conditions.
- Seed enough rows and fixture documents that the answer cannot be found by eyeballing one file. Use hundreds to a few thousand rows/chunks where useful, generated programmatically or deterministically, while staying within the sandbox readiness budget.
- The seeded data must be internally CONSISTENT: foreign keys resolve, graph edges reference valid nodes, source revisions reconcile with manifests, status lifecycles are plausible, and provenance chains are coherent.
- Production concerns should be woven into the existing code rather than bolted on: metadata-filter ordering, graph traversal bounds, temporal scoping, tenant or region isolation, provenance preservation, cache invalidation, idempotent ingestion, index-version alignment, evaluation drift, and audit logging.

The candidate should demonstrate senior-level judgment: root-cause analysis, RAG and graph anti-pattern detection, vector index and metadata reasoning, provenance design, evaluation design, implementation quality, trade-off articulation, and measurable validation.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, RAG/vector database documentation, Qdrant documentation, PostgreSQL documentation, Redis documentation when Redis is used, OpenAI/Anthropic/LiteLLM documentation, graph modeling and semantic knowledge system references, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can read a substantial codebase, understand a graph-grounded RAG pipeline end to end, and make defensible choices on retrieval contracts, graph scope, governance, grounding, observability, and evaluation.
- AI assistance may help with syntax or research, but the assessment should evaluate whether the candidate can diagnose the incident, design safe retrieval behavior, and implement production-quality changes.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + graph-grounded advanced RAG task that:
- Draws inspiration from one selected scenario to determine the business context, corpus, graph-modeled entities and relationships, incident, governance constraints, and operational goals.
- Matches ADVANCED proficiency for Graph-based Knowledge Systems, Retrieval Augmented Generation, and Vector Databases.
- Tests applied skills with ingestion metadata, Qdrant vector retrieval, optional in-process sparse/hybrid scoring, PostgreSQL graph/provenance traversal, Redis cache behavior when relevant, real LLM generation, citation provenance, evaluation, and fail-closed behavior.
- Uses the Infrastructure Requirements stack defined below.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.
- Includes enough realistic existing code that the candidate must read and reason about the system before changing it.
- Leaves the core advanced decisions for the candidate and does not reveal exact implementation details in README, hints, stubs, visible tests, fixture comments, or question text.

The generated code files must be valid and executable. If the task is a bug-fix task, the starter code should contain logical RAG/graph/vector issues, not syntax errors. If the task is an architecture-hardening task, the starter code should include working but unsafe or incomplete behavior that reflects the selected incident.

## Infrastructure Requirements
This is an infra-shaped task. The generated repository MUST include docker-compose.yml, init_database.sql, and run.sh. No kill.sh is needed because E2B sandboxes are destroyed as a whole when the session ends.

Use this lightweight local infrastructure shape unless the selected scenario explicitly requires a narrower subset:
- Qdrant for dense vector retrieval over the scenario corpus.
- PostgreSQL for graph-modeled knowledge, source provenance, index manifests, audit events, evaluation records, governance state, and any relational business records needed by the selected scenario.
- Redis for retrieval or answer caching only when the incident involves cached answers, retrieval candidates, stale evidence, index rollout, or version-sensitive behavior.
- The Python application runs on the host inside /root/task, not in an app container. Only datastores run in Docker.
- The end-to-end answer path must call a real LLM provider when a provider key is present. `.env.example` must declare provider key variables such as `OPENAI_API_KEY=`, `ANTHROPIC_API_KEY=`, `OPENAI_BASE_URL=`, and model variables with no real secrets.
- Readiness checks and visible invariant tests must be able to run offline without a provider key by validating imports, fixtures, schemas, datastore connectivity, graph/vector bootstrap, retrieval contracts, and non-generation behavior only.

Required dependency approach:
- The primary Python runtime is pre-installed by the E2B template; do NOT apt-get or system-install Python.
- run.sh's FIRST project step after changing to /root/task MUST install the task's own dependencies, for example `python3 -m pip install -q -r requirements.txt`.
- Use Python 3.11-compatible dependencies such as fastapi, uvicorn, pydantic, pydantic-settings or python-dotenv, qdrant-client, redis if Redis is used, psycopg[binary] or SQLAlchemy, httpx, tenacity, fastembed, openai, anthropic or litellm, pytest, and any lightweight evaluation helpers needed.
- Do NOT include heavy model packages such as torch, sentence-transformers, or transformers unless the scenario absolutely requires them; prefer fastembed or provider embeddings.

### Docker-compose Instructions
- Generate a docker-compose.yml with NO top-level `version` field. **MUST NOT include any version specification**.
- The compose file MUST define only the datastore services needed by the scenario; for the recommended advanced graph-grounded RAG incident shape, include `qdrant`, `postgres`, and include `redis` only when freshness/cache/index-rollout behavior is part of the task.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every datastore exposed to the host.
- Qdrant should use a stable qdrant image, expose `127.0.0.1:6333:6333`, define persistent storage, and include a healthcheck that verifies the HTTP readiness endpoint.
- Redis, if used, should use a stable redis image, expose `127.0.0.1:6379:6379`, define an appropriate healthcheck such as `redis-cli ping`, and avoid passwords unless the starter code consistently uses them.
- PostgreSQL MUST use inline service environment values:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
- Forbid `.env` files or `${{VAR}}` host indirection for datastore initialization values. Inline service environment values are required because the image will NOT initialize without them.
- The init SQL, healthcheck, and application connection string must use the same PostgreSQL user and database.
- PostgreSQL ports MUST use `127.0.0.1:5432:5432`.
- PostgreSQL healthcheck MUST use `pg_isready` with the same inline user/database values.
- Do not include MySQL, MongoDB, Neo4j, JanusGraph, Kafka, Elasticsearch, MinIO, or additional services unless the selected scenario explicitly and unavoidably requires them and the service is available in the template.
- Do not include a Dockerfile unless you intentionally containerize an app helper. For this task, prefer host-run Python app plus containerized datastores.
- **CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`), `command:` MUST ALSO be a LIST with exactly one element holding the full shell script string. NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else becomes bash's positional parameters and is silently dropped. Simplest safe pattern: omit `entrypoint:` and put the whole invocation as a LIST in `command:`.

### init_database.sql Instructions
- Generate init_database.sql at the repository root.
- It must be mounted into the PostgreSQL service via `/docker-entrypoint-initdb.d/init_database.sql:ro`.
- It must initialize realistic graph, provenance, governance, and operations tables for the chosen scenario, such as graph_nodes, graph_edges, entity_crosswalks, ontology_terms, source_documents, document_revisions, index_manifests, document_provenance, retrieval_audit_events, generation_audit_events, evaluation_runs, quality_dimensions, user_feedback, or rollout_decisions.
- It must be valid PostgreSQL SQL and idempotent where possible.
- It must not solve the candidate's task by encoding all policy decisions, final thresholds, traversal rules, exact filters, or complete retrieval contracts in a way that gives away the answer.
- It should include enough seed data to make the starter environment FULLY POPULATED and inspectable.
- It should include realistic graph and document edge cases relevant to the selected scenario: time-varying relationships, lifecycle states, soft-deleted or archived records, near-duplicate source revisions, NULL supersession or deletion timestamps, boundary timestamps, multilingual or unicode names when appropriate, and provenance chains.
- It should avoid secrets and avoid production credentials.

### Qdrant / Redis Configuration Instructions
- Qdrant fixtures should be loaded by a Python setup or ingestion script using scenario-specific documents, chunk text, tenant/product/region/effective-time metadata, graph entity links, embedding version metadata, source provenance, and any ACL/residency fields that make the incident reproducible.
- Qdrant collections and payload fields should be realistic enough to expose advanced vector and graph-grounded RAG failure modes, but visible fixtures must not pre-decide all hidden grading expectations.
- Do not use fake embeddings if the retrieval path being assessed needs semantic behavior. Use fastembed or provider embeddings for corpus/query vectors in the scaffold.
- Redis may be pre-populated only with safe fixture keys that demonstrate stale or version-sensitive behavior; do not hard-code the final cache-key design the candidate should choose.
- Any cache keys shown in code or fixtures must be scenario-specific and must not reveal the complete solution contract.

### Run.sh Instructions
- Generate run.sh at the repository root and make it executable in the JSON file content.
- run.sh is a readiness/self-check script, NOT the grader.
- It MUST begin by changing to `/root/task`.
- It MUST install dependencies as its first project action, for example `python3 -m pip install -q -r requirements.txt`.
- It MUST run `docker compose up -d` for the datastore services.
- It MUST wait for PostgreSQL, Qdrant, and Redis if Redis is used, using bounded retry loops and clear error messages.
- It MUST export connection variables for the local host-run app, such as `DATABASE_URL=postgresql://kguser:kgpass@localhost:5432/kg_rag`, `QDRANT_URL=http://localhost:6333`, and `REDIS_URL=redis://localhost:6379/0` when Redis is used.
- It MUST initialize or verify fixture data using safe setup commands such as `python3 -m app.bootstrap` or `python3 -m app.ingestion.seed_corpus`.
- It MUST verify the starter project compiles/loads using an import smoke or lightweight offline invariant check that does not require an LLM provider key.
- It MUST NOT run the grader test suite that is designed to fail until the candidate solves the task.
- If you include a visible invariant suite and run any test command from run.sh, run.sh must treat tests as a deployability probe only: exit 0 when the runner collected and executed the suite even if tests fail by design, and exit non-zero only for import errors, missing dependencies, collection/config errors, usage errors, or no tests collected. For pytest, mirror this shape:
  - `python3 -m pytest -q invariants; rc=$?`
  - If rc is 0 or 1, run.sh exits 0 for deployability.
  - If rc is 2 or greater, or rc is 5, run.sh exits non-zero.
- Prefer an import smoke over running candidate-facing tests from run.sh to avoid conflating designed failures with a broken scaffold.
- run.sh must exit 0 on the UNSOLVED starter, without any candidate stub being filled in. Design the starter so that is true by construction.
- If a FastAPI app is started by run.sh, start uvicorn in the background using nohup so the script returns. Do not block forever.
- If any inline Python selfcheck in run.sh loads environment variables, it MUST call `load_dotenv('/root/task/.env')` or `load_dotenv('.env')` with an explicit path. A bare `load_dotenv()` executed via a stdin heredoc can crash inside `find_dotenv()` and must not be used.
- Every Python invocation inside shell scripts MUST use `python3`, never bare `python`.

### Dockerfile Instructions
- Do not include a Dockerfile for the main Python application unless the selected scenario truly requires an app container.
- If any helper container is included, use an official lightweight Python image, install only declared dependencies, avoid apt-get installing the Python runtime itself, and keep commands consistent with the Compose entrypoint/command form rules.
- For the preferred host-run application shape, omit Dockerfile entirely.

The output should be a valid json schema:
- `README.md` with the exact candidate-facing sections specified below.
- `.gitignore` with Python, environment, cache, log, and local datastore artifacts excluded.
- `.env.example` with provider key placeholders and local datastore URLs, but no secrets.
- `requirements.txt` with all Python project dependencies needed by the starter and tests.
- `docker-compose.yml` with Qdrant, PostgreSQL, and Redis only if required by the scenario, no version field, localhost-only port bindings, inline PostgreSQL initialization environment values, and healthchecks.
- `init_database.sql` with PostgreSQL schema and seed data for graph knowledge, manifests, provenance, audit, evaluation, or governance records.
- `run.sh` that installs dependencies, starts datastores, waits for readiness, seeds/verifies fixtures, performs an offline smoke check, and exits correctly.
- A substantial Python application under `app/` with multiple modules such as configuration, models, ingestion, embeddings, dense retrieval, sparse or hybrid retrieval, graph repository, graph expansion, context assembly, generation, citations, cache, audit logging, evaluation, API entry points, and selfcheck.
- Scenario-specific fixture data under `data/` or `fixtures/`.
- Visible invariant tests under `invariants/` and ADVANCED-only hidden grading tests under the optional `hidden_tests` envelope when a check would reveal the solution if shipped to candidates.

## Code file requirements
- More than one file must be generated, and all files must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use clear module boundaries and a readable project structure.
- The generated starter code must be runnable and inspectable, with valid imports and no syntax errors.
- The generated starter code MUST NOT contain the full implementation for the core advanced logic of the task.
- The core retrieval contract, graph scoping behavior, provenance chain, cache-versioning strategy, fail-closed policy, citation grounding behavior, evaluation thresholds, or rollout decision logic that the candidate must design should be incomplete, flawed, or minimally stubbed while remaining type-complete and importable.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments or placeholder hints.
- Do NOT use fake LLMs or deterministic stand-ins for generation. The app's generation path must call a real provider through OpenAI, Anthropic, or LiteLLM when configured.
- Visible tests must not hard-code answer-revealing internal shapes, exact thresholds, enum values, traversal rules, metadata predicates, graph edge types, or policy constants that the candidate is supposed to design.
- For ADVANCED level, split tests when needed: candidate-visible `invariants/` should check scaffold integrity and observable outcomes, while hidden tests under `hidden_tests` may check governance-sensitive or exact contract behavior that would reveal the answer.
- The starter codebase must be substantial and realistic, not a toy snippet. Require multiple interacting modules and changes across more than one file.
- Include proper logging and error handling in the scaffold without solving the candidate's task.
- Ensure all paths reference /root/task as the base directory.
- Every module referenced anywhere — application code, bootstrap code, test configuration, and build or tool configuration — MUST appear in the dependency manifest. Cross-check every import and plugin reference against requirements.txt before emitting.
- The unsolved starter must be type-complete and readiness-complete. If stubs exist, they must have correct signatures and safe placeholder behavior so run.sh passes without implementing the assessed behavior.

## .gitignore INSTRUCTIONS
Create a sensible Python gitignore for an advanced graph-grounded RAG task, including:
- __pycache__/
- *.pyc
- .venv/
- venv/
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
- local evaluation outputs or trace dumps generated by manual runs

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain exactly the following output sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each of the four sections MUST be written as an actual markdown heading, consistently using `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify`. A plain unmarked text line with the section name is INVALID and counts as a missing section.

### Task Overview
- 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- NEVER empty.
- NO bold time-budget callouts.
- Must be specific to the selected real-world scenario and the graph-grounded RAG incident.
- Describe symptoms and impact, not the root cause, exact files, exact functions, exact graph tables, exact payload fields, expected labels, hidden checks, or final architecture.
- Must not include setup commands, database connection details, credentials, client-tool suggestions, absolute task paths, or remote-host placeholders.

### Objectives
- ADVANCED objectives MUST be concise and OPEN-ENDED.
- Use 3-4 bullets maximum; fewer, tighter is better.
- This task is a repair task unless the selected scenario is explicitly a greenfield design/build. For repair tasks, each objective should be a full, natural sentence from a stakeholder's point of view, roughly 10-24 words, describing the desired outcome and why it matters operationally.
- For design/build variants, each objective should be one short plain goal statement, roughly 5-15 words, naming the outcome without stakeholder framing.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, graph edge type, payload field, vector index parameter, or any other direct code reference.
- Do NOT describe current-vs-after behavior; state desired end-state as a standing requirement.
- Do NOT enumerate the specific instances the candidate is supposed to discover. Name the class of concern, never the exact hidden tenants, jurisdictions, products, versions, statuses, edge types, dates, or payload fields.
- Apply the agent-paste test to every objective: if the bullet pasted alone into an AI coding agent would be enough to know what to implement without reading the repository and data, it is too specific.
- At ADVANCED level, ZERO enumerated instances are allowed in Objectives, and at least one question-form objective should be included when the task is a design/build task.
- Good repair style examples:
  - "Compliance reviewers should trust that generated guidance reflects the knowledge state authorized for the request."
  - "Auditors should be able to trace each answer back to the exact evidence that shaped it."
  - "Release owners should see quality failures separated clearly enough to make safe rollout decisions."
  - "End users should receive grounded answers without silent reliance on unrelated knowledge."
- Bad objective examples:
  - "Filter Qdrant by tenant_id before graph expansion."
  - "Join graph_edges to disclosure_versions using effective_start and effective_end."
  - "Set efSearch to 128 and add a BM25 reranker."
  - "Validate money, status, and deletion semantics in displayed rows."

### Helpful Tips
- 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, algorithm, exact threshold, enum vocabulary, graph edge type, table name, payload field, or policy constant that solves the task.
- Keep tips oriented to symptoms, trade-offs, evidence flow, graph boundaries, provenance, evaluation dimensions, and operational reasoning, not step-by-step implementation.

### How to Verify
- 3-5 bullets maximum.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as readiness output, invariant output, response grounding, citation traceability, audit records, evaluation dimension reports, latency observation, freshness behavior, or deterministic re-run results.
- Because tasks with a real LLM use `.env.example` declaring provider keys, How to Verify MUST open with a GitHub note admonition embedded INSIDE the section as a blockquote, never as a new heading:
  - `> [!NOTE]`
  - `> Copy `.env.example` to `.env` and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.`
- At most ONE bullet may reference the task environment directly.
- Do not include setup commands such as `pip install`, `docker compose up`, exact pytest command lines, or shell setup details.
- Any legitimate local verification command must use localhost. Never use a droplet IP or remote-host placeholder.
- Do not include database host, port, username, password, or client-tool suggestions in the README.
- Do not restore what the Objectives withheld. If Objectives say preserve authorized knowledge, do not list the exact tenants, regions, document versions, graph relationships, or lifecycle flags in How to Verify.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README:
- Setup commands such as `pip install`, `docker compose up`, `pytest`, `python -m ...`, or similar install/start commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, graph edge types, table names, payload fields, vector-index parameters, policy constants, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>".
- Database-connection details including host, port, username, password, or client-tool suggestions.
- `<DROPLET_IP>` placeholders or any remote-host placeholder.
- Extra README sections such as Application Access, Database Schema Overview, Database Access, Architecture, Performance Issues, Evaluation Details, or NOT TO INCLUDE.

## REQUIRED OUTPUT JSON STRUCTURE
Output a SINGLE raw JSON object with EXACTLY these keys and no others. Each field must be populated with candidate-safe task content, and the top-level JSON keys must use the exact names below:

{{
  "name": "A kebab-case GitHub repository name under 50 characters that summarizes the advanced graph-grounded RAG incident without duplicating the title.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, and focused on the scenario's graph-grounded RAG improvement goal.",
  "question": "A full candidate-facing task description written as a scenario paragraph plus a direct imperative ask. It must explain who the candidate is, what system they inherited, the operational situation, and the outcomes the work must achieve at the same altitude as the README Objectives. It MUST NOT leak the answer: no file names or paths, no function or method references, no directory paths, no exact graph tables, no exact payload fields, no exact filters, no vector-index parameters, no thresholds, no enum values, no hidden test details, and no direct solution statements.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (`## Task Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify`) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "A comprehensive Python and local-infrastructure gitignore that excludes virtual environments, caches, logs, local environment files, datastore artifacts, and generated trace or evaluation outputs.",
    ".env.example": "A safe environment template containing provider key placeholders such as OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENAI_BASE_URL, model variables, and local service URL placeholders, with no real secrets.",
    "requirements.txt": "The Python dependencies needed to run the substantial starter application, bootstrap fixtures, real LLM integration, Qdrant, PostgreSQL access, Redis access when Redis is used, and tests without heavy torch-based packages.",
    "docker-compose.yml": "A datastore-only compose file with no version field, localhost-only port bindings, Qdrant and PostgreSQL services, Redis only if required by the scenario, inline PostgreSQL initialization environment values, mounted init_database.sql, persistent volumes, and healthchecks.",
    "init_database.sql": "A PostgreSQL initialization script that creates and seeds realistic graph knowledge, source provenance, index manifest, audit, evaluation, and governance tables needed by the scenario without encoding the final candidate solution.",
    "run.sh": "An executable readiness script that changes to /root/task, installs dependencies first, starts datastore services with docker compose up -d, waits for health, exports local connection variables, seeds or verifies fixtures, performs an offline smoke check, and exits without running the failing grader suite.",
    "app/__init__.py": "A package marker for the Python application.",
    "app/config.py": "Configuration loading for local datastore URLs, provider selection, corpus identity, index identity, and runtime settings without hard-coding secrets or answer-revealing policy constants.",
    "app/models.py": "Pydantic request, response, evidence, graph entity, citation, provenance, evaluation, and audit models with enough structure for the application to run while leaving advanced policy decisions to the candidate where appropriate.",
    "app/main.py": "The FastAPI or service entry point exposing health and scenario-specific answer endpoints that orchestrate retrieval, graph expansion, context assembly, generation, auditing, and error handling.",
    "app/bootstrap.py": "A bootstrap module that verifies datastore connectivity, initializes Qdrant collections or Redis fixture state when used, and loads scenario corpus fixtures using safe local commands.",
    "app/ingestion.py": "Ingestion logic for scenario documents, graph links, metadata, provenance, embedding version fields, and Qdrant payloads, with realistic gaps tied to the incident.",
    "app/embeddings.py": "A lightweight embedding wrapper using fastembed or a provider embedding path appropriate for the scenario and compatible with the local sandbox.",
    "app/dense_retrieval.py": "Qdrant dense retrieval logic that is realistic and runnable but contains or exposes the scenario's advanced vector retrieval contract issue.",
    "app/sparse_retrieval.py": "A lightweight sparse or lexical retrieval component used for hybrid behavior where the scenario benefits from dense and keyword evidence.",
    "app/hybrid_retrieval.py": "Hybrid candidate selection code that combines retrieval signals without revealing the final weighting, filtering, or fail-closed policy the candidate must design.",
    "app/graph_repository.py": "PostgreSQL-backed graph access helpers for graph nodes, edges, statements, ontology metadata, provenance, and relationship lookup in the selected scenario.",
    "app/graph_expansion.py": "Graph expansion and evidence-enrichment logic that participates in the incident while leaving scoping, traversal, and provenance fixes to the candidate.",
    "app/context_assembly.py": "Context construction and citation preparation logic that passes retrieved and graph-expanded evidence toward generation while leaving grounding and provenance fixes to the candidate.",
    "app/generation.py": "A real LLM provider integration that builds prompts from retrieved evidence and calls OpenAI, Anthropic, or LiteLLM when a provider key is configured, with no fake model stand-in.",
    "app/cache.py": "Redis-backed cache logic for answer or retrieval artifacts when the scenario requires freshness, index-version, or tenant-safety reasoning; omit this file if Redis is not used.",
    "app/audit.py": "PostgreSQL-backed audit, provenance, and manifest helpers that record retrieval, graph expansion, generation, or evaluation events relevant to governance and operations.",
    "app/evaluation.py": "Offline evaluation helpers for retrieval quality, graph attribution, citation correctness, freshness, faithfulness proxies, and scenario-specific invariant checks without exposing hidden grading decisions.",
    "app/selfcheck.py": "A key-free readiness module that imports the package, loads configuration, checks fixture shape, verifies datastore connectivity, and confirms bootstrap state without calling the real answer path.",
    "data/corpus.jsonl": "Scenario-specific corpus fixtures with realistic text, provenance, tenant/product/region/effective-time metadata, graph entity references, embedding version fields, and document lifecycle signals.",
    "data/graph_seed.jsonl": "Scenario-specific graph fixture data for entities, relationships, statements, crosswalks, and provenance references, with no answer labels or comments explaining the trap.",
    "data/eval_queries.jsonl": "Scenario-specific evaluation queries and observable expectations that support self-checking without revealing all hidden policies, exact thresholds, or final contract shapes.",
    "invariants/test_scaffold.py": "Visible pytest checks that validate imports, fixture shape, datastore bootstrap behavior, and non-secret offline invariants.",
    "invariants/test_observable_behavior.py": "Visible pytest checks for candidate-observable graph-grounded RAG behavior that do not hard-code solution-only thresholds, status enums, internal policy constants, exact traversal rules, or hidden instance lists.",
    "hidden_tests": "An optional ADVANCED-only envelope containing grading tests for exact governance, graph scope, provenance, fail-closed, freshness, citation, reproducibility, or rollout behavior that would reveal the solution if shipped to candidates."
  }},
  "answer": "An evaluator-facing high-level solution approach describing the intended advanced graph-grounded RAG architecture, root-cause diagnosis, retrieval-contract reasoning, graph scoping strategy, provenance safeguards, evaluation design, reproducibility controls, and operational trade-offs at a non-code level.",
  "definitions": "An object mapping important scenario-specific graph, RAG, vector-index, retrieval, governance, cache, provenance, evaluation, grounding, and rollout terms to concise definitions useful for evaluators and candidates.",
  "hints": "A single-line nudge that points candidates toward investigating the evidence flow across retrieval, graph expansion, generation, and quality reporting without naming the exact fix, thresholds, APIs, internal shapes, hidden instances, or policy constants.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable retrieval safety, graph-scope correctness, answer grounding, exact provenance, freshness, deterministic evaluation, and production-level code quality; one line must explicitly mention clean code, naming, exception handling, logging, and clear project structure.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3.11 proficiency, comfort with Docker-backed Qdrant and PostgreSQL, advanced RAG and vector retrieval knowledge, graph modeling familiarity, and familiarity with real LLM provider keys via .env; never include imperative setup or verification steps.",
  "short_overview": "Exactly three bullets, one sentence each, in plain non-technical business English: first, what the system is and the one-line situation today; second, what this rework needs to achieve at outcome level without mechanism names; third, what separates a strong submission, closing on whether the design reasoning is sound."
}}

Use these EXACT keys. Do NOT use synonyms: not `task_title`, `files`, `repo`, `context`, `solution`, `criteria`, or `hidden_tests` as a top-level key outside the optional code_files envelope. Do NOT emit `criterias`; the pipeline injects it. Output raw JSON only — no markdown fences, no prose around it.

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The generated task must align with ADVANCED Graph-based Knowledge Systems, Retrieval Augmented Generation, and Vector Databases proficiency and the provided competency scopes.
3. The generated task must draw from one provided real-world scenario and must not invent an unrelated domain.
4. The generated repository MUST include docker-compose.yml, init_database.sql, and run.sh for this infra-shaped task.
5. No kill.sh is needed; E2B sandboxes are destroyed as a whole.
6. docker-compose.yml MUST NOT include any version specification.
7. Datastore ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
8. PostgreSQL MUST set POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB inline in the service environment, and init SQL, healthcheck, readiness probe, and connection strings must use the same user/database.
9. Use Qdrant for the real vector database and PostgreSQL for the real graph/provenance/governance layer; do not invent unavailable graph infrastructure.
10. Include Redis only when the selected scenario actually exercises freshness, caching, or rollout behavior.
11. run.sh must install Python dependencies first, start datastores, wait for health, seed or verify fixtures, and avoid running a failing grader suite.
12. run.sh must exit 0 on the UNSOLVED starter.
13. Every Python invocation in shell scripts must use `python3`, never bare `python`.
14. The task must include a real LLM provider integration; do NOT generate FakeLLM, StubLLM, deterministic stand-ins, regex-only model replacements, replay clients, or simulated thinking sleeps.
15. Visible README Objectives for ADVANCED must be concise and open-ended, and must not name solution APIs, files, functions, classes, algorithms, graph table names, payload fields, exact instances, thresholds, or policy constants.
16. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as a markdown heading, with no extra headings.
17. Do not include setup commands, direct solutions, database connection details, client-tool suggestions, absolute task paths, or `<DROPLET_IP>` placeholders in the README.
18. Use substantial multi-file starter code appropriate for 3-5+ years of experience; do not generate a toy snippet or single-file fix.
19. Split tests for ADVANCED only when visible checks would reveal the solution; use hidden_tests inside code_files for answer-revealing grading checks.
20. Keep secrets out of version control and use `.env.example` only for empty provider-key placeholders.
21. The task must be completable within {minutes_range} minutes.
"""

PROMPT_REGISTRY = {
    "Graph-based Knowledge Systems (ADVANCED), Retrieval Augmented Generation (RAG) (ADVANCED), Vector Databases (ADVANCED)": [
        PROMPT_GRAPH_RAG_VECTOR_ADVANCED_CONTEXT,
        PROMPT_GRAPH_RAG_VECTOR_ADVANCED_INPUT_AND_ASK,
        PROMPT_GRAPH_RAG_VECTOR_ADVANCED_INSTRUCTIONS,
    ]
}