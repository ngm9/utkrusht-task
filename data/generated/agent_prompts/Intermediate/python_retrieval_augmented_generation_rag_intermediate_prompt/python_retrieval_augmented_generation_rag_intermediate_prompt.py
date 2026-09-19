# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_PYTHON_RAG_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_RAG_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Retrieval Augmented Generation (RAG) assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL QUESTION CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document or knowledge context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and RAG implementation, debugging, or improvement required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE RAG proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_RAG_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Python and Retrieval Augmented Generation (RAG), you are given a list of real world scenarios and proficiency levels for Python and RAG.
Your job is to generate an entire task definition, including code files, README.md, docker-compose.yml, run.sh, expected outcomes, and verification guidance, that can be effectively used to assess the candidate's ability to build, debug, and improve a moderately complex Python RAG application backed by pgvector.
The candidate's responsibility is to identify the issues and improve the existing RAG workflow without being handed the solution. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Python project structure with a working pgvector datastore, local sample documents, starter RAG modules, and a visible invariant test suite. The application includes:
- A realistic Python package with multiple interacting modules for ingestion, chunking, embedding, retrieval, prompt-context assembly, generation, evaluation, and API wiring where appropriate
- A PostgreSQL database with pgvector enabled and initialized through Docker
- Local fixture documents grounded in the selected real-world scenario
- Starter code that runs and imports successfully, but contains incomplete or insufficient RAG behavior that the candidate must diagnose and improve
- A retrieval and answer workflow that should call a REAL LLM through a runtime SDK or router when the candidate runs end-to-end behavior with a provider key
- Invariant tests or evaluation checks that help the candidate validate retrieval quality, grounding, metadata handling, robustness, and Python code behavior

The candidate's responsibility is to read the moderate codebase, reason through the RAG flow, and make improvements across more than one module. A part of the task completion is to watch the candidate apply intermediate Python design practices, practical RAG judgment, testing discipline, and secure configuration handling rather than only patching one obvious line.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Python + RAG scenario.
- Task must ask the candidate to implement a meaningful feature, fix logical defects, or improve an existing Python RAG application backed by pgvector.
- **CRITICAL**: The starter project must be FULLY FUNCTIONAL as a project scaffold: dependencies can install, modules import, the database can start, and the readiness script exits successfully before the candidate solves the core task.
- **CRITICAL**: The core RAG behavior should remain incomplete, incorrect, weakly grounded, or insufficient until the candidate improves it.
- **CRITICAL**: This is an INTERMEDIATE task for a candidate with 2-5 years of Python experience and practical RAG experience. It should require moderate reasoning across multiple files, not advanced distributed architecture.
- The task should combine 4-5 connected concepts in a coherent workflow, such as ingestion idempotency, chunk metadata, pgvector retrieval, context assembly, citation behavior, refusal handling, evaluation checks, or latency/cost-aware batching.
- The project must be substantial and realistic, NOT a toy snippet. Require multiple interacting modules in a real Python package layout, non-trivial existing logic the candidate must read, and changes that span more than one file.
- The task must stay within intermediate Python scope: functions, classes, modules, packages, standard library usage, third-party packages, file and data handling, pytest, database interaction, debugging, refactoring, error handling, and moderate performance improvements.
- The task must stay within intermediate RAG scope: document ingestion, chunking, embeddings, vector storage, metadata-aware retrieval, hybrid or thresholded retrieval where useful, prompt construction, answer grounding, citations, evaluation, guardrails, and operational logging.
- The task must NOT require fine-tuning, GPU-only dependencies, Kubernetes, large-scale distributed systems, custom model training, or expert-only architecture decisions.
- The task must NOT use sentence-transformers, torch, transformers, or other heavyweight GPU-oriented dependencies. Use fastembed for local embeddings.
- The candidate's code MUST call a REAL model through a runtime SDK or router for end-to-end generation, such as OpenAI, Anthropic, or LiteLLM. The candidate supplies their own provider key at runtime through `.env`.
- **CRITICAL**: Do NOT create a FakeLLM, StubLLM, regex-based intent parser, deterministic stand-in for the LLM, or sleep-based simulation of model behavior. Offline readiness may avoid calling the LLM, but the task itself must require real generation behavior.
- For INTERMEDIATE level, keep the problem crisp and reproducible, but do not hand over the exact solution shape. Starter stubs may state a one-line purpose and symptom, but must not include exact dict keys, exact enum vocabularies, exact thresholds, or an implementation checklist that solves the task.
- The question must NOT include hints about the specific implementation needed. Hints belong only in the dedicated `hints` field.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- The task should be completable within {minutes_range} minutes.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Python documentation, RAG framework documentation, pgvector documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization.
- Therefore, the complexity of the tasks should require genuine intermediate-level Python and RAG problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Candidates are encouraged to use AI to help understand APIs, inspect retrieval behavior, and reason about implementation tradeoffs, but the generated task should still reward candidates who can read a moderate codebase, diagnose root causes, and make defensible RAG design choices.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Python + RAG task that:
- Draws inspiration from one selected scenario to determine the business context, document domain, and technical requirements.
- Matches INTERMEDIATE proficiency for both Python and Retrieval Augmented Generation.
- Tests practical skills with local documents, ingestion, chunking, metadata enrichment, fastembed embeddings, pgvector schema design, retrieval, prompt-context assembly, real LLM generation, and evaluation.
- Uses PostgreSQL with pgvector as the datastore. Do not invent additional datastores unless the selected scenario explicitly requires them.
- Uses the infrastructure stack defined below and does not deviate from it.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.
- Provides enough starter code for a realistic development experience, but does not solve the core task.
- Makes the candidate reason about the full RAG flow: query, retrieval, context assembly, prompt, generation, and post-processing.
- Includes visible invariant tests that the candidate can run locally, while keeping the readiness script separate from the grader-style test suite.

## Infrastructure Requirements
- MUST include a complete pgvector datastore deployment using Docker Compose.
- MUST include `docker-compose.yml` for the PostgreSQL pgvector service and `run.sh` for dependency installation plus datastore readiness validation.
- MUST NOT include `kill.sh`. E2B sandboxes are destroyed as a whole when the session ends, so container cleanup is automatic.
- The Python application runs on the host inside the sandbox, not inside an application container. Only pgvector runs in Docker.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- The infrastructure setup must be automated enough that `run.sh` can bring up pgvector, wait for health, install Python dependencies, apply or validate schema, perform an import smoke check, and exit successfully on the unsolved starter.
- The readiness script is NOT the grader. It MUST NOT run the invariant pytest suite if those tests are designed to fail until the candidate completes the task.
- The primary runtime is pre-installed by the E2B template, so do NOT apt-get or system-install Python. The task's own third-party dependencies are not pre-installed, so `run.sh` must install them as its first project step.
- For real LLM usage, include `.env.example` with provider key placeholders, but the readiness script must not require a live provider key.

### Docker-compose Instructions
- Generate a `docker-compose.yml` file with a single PostgreSQL pgvector service, usually named `db`.
- Use image `pgvector/pgvector:pg16`.
- **MUST NOT include any version specification** in the docker-compose.yml file.
- For the datastore service, REQUIRE the standard init env vars inline in `environment:`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- The init SQL, healthcheck, and connection string must use the same user and database.
- Forbid `.env` files and `${{VAR}}` host indirection in docker-compose. Inline service environment values are required so the container initializes correctly.
- Use hardcoded development values such as user `raguser`, password `ragpass`, and database `ragdb`.
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:5432:5432`.
- Include a healthcheck using `pg_isready` with the same database and user configured in the inline environment.
- Mount `init_database.sql` into `/docker-entrypoint-initdb.d/init_database.sql` so PostgreSQL initializes pgvector and baseline schema on first startup.
- Include a named volume or local directory for PostgreSQL data persistence, but ensure it is ignored by git.
- Do NOT add MySQL, MongoDB, Redis, Qdrant, or any other service unless the selected real-world scenario explicitly requires it. For this Python + RAG task, pgvector should normally be sufficient.

### init_database.sql Instructions
- Generate `init_database.sql` to initialize PostgreSQL with pgvector.
- Include `CREATE EXTENSION IF NOT EXISTS vector;`.
- Create a practical schema for RAG documents and chunks, including document identifiers, source metadata, chunk text, metadata fields, timestamps where relevant, and an `embedding vector(384)` column for fastembed `BAAI/bge-small-en-v1.5`.
- Include indexes that make the starter usable, but do NOT fully solve the task if the candidate is expected to improve schema, retrieval, filtering, deduplication, or performance.
- If the scenario centers on an existing bug, include intentionally incomplete or insufficient schema choices that are realistic and diagnosable, not syntax errors.
- Use realistic table and column names tied to the selected scenario.
- Do not include comments that reveal the solution.
- Keep initialization deterministic and small enough for the sandbox while still realistic for intermediate analysis.

### Run.sh Instructions
- Generate a `run.sh` script located at `/root/task/run.sh`.
- The script must start with `set -e` except where explicitly handling expected command exit codes.
- FIRST project step: install task dependencies using `python3 -m pip install -q -r /root/task/requirements.txt`.
- PRIMARY RESPONSIBILITY: starts Docker containers using `docker compose -f /root/task/docker-compose.yml up -d`.
- WAIT MECHANISM: poll the pgvector service health or use `pg_isready` until PostgreSQL is accepting connections.
- VALIDATION: confirm the database is reachable on localhost and that pgvector/schema initialization succeeded.
- EXPORTS: set `DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb` for smoke checks.
- READINESS CHECK: run a lightweight import or package smoke check such as `python3 -m compileall app` or `python3 -c "import app"` and, if appropriate, a schema validation script that does not require the candidate's final solution.
- MUST NOT run the invariant pytest suite when those tests are expected to fail before the candidate completes the task.
- MUST NOT call the real LLM or require `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or another provider key during readiness.
- MUST exit 0 when the datastore is healthy and the unsolved starter project imports or compiles successfully.
- MUST exit non-zero only when dependencies cannot install, Docker cannot start, PostgreSQL cannot become healthy, schema initialization fails, or the starter code cannot import.
- Every Python invocation inside shell scripts MUST use `python3`, never bare `python`.
- Before running ANY Python code that connects to the database, run.sh MUST verify the pgvector extension exists (e.g. `psql "$DATABASE_URL" -tAc "SELECT 1 FROM pg_extension WHERE extname='vector'"` in the wait loop, or an equivalent check). The `vector` extension is created ONLY by `init_database.sql` via the docker-entrypoint mount — Python code must NEVER be the first thing to touch the vector type.
- Print concise progress messages so the candidate can see what readiness step is running.
- Do not start a long-running uvicorn process unless the scenario specifically requires a running API; if you do start one, start it in the background so `run.sh` still exits.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastembed, psycopg, pytest, pydantic, python-dotenv, and a real LLM SDK or router. CRITICAL: requirements.txt MUST list EVERY third-party package imported anywhere in the generated code — e.g. if any file has `from openai import OpenAI` then `openai` must be listed; if any file imports `pydantic_settings` then `pydantic-settings` must be listed. Cross-check every import statement against requirements.txt before finalizing.)
  - .env.example (Provider key placeholders and local DATABASE_URL only)
  - docker-compose.yml (Single pgvector PostgreSQL service with localhost-bound port and inline init env vars)
  - run.sh (Readiness script that installs dependencies, starts pgvector, waits for health, validates schema/imports, and exits)
  - init_database.sql (pgvector extension and starter schema)
  - .gitignore (Python, environment, logs, and local database volume exclusions)
  - app package files for ingestion, chunking, embeddings, retrieval, generation, evaluation, configuration, and optional API wiring
  - data fixture files grounded in the selected scenario
  - invariants test files that candidates can run after making changes
  - any additional minimal files needed for a runnable Python project

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use clear module boundaries and readable project structure.
- The generated project should be a substantial intermediate codebase with multiple interacting files, not a single short script.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core ingestion, chunking, retrieval, metadata filtering, context assembly, generation, evaluation, schema, or robustness behavior that the candidate must complete should be left incomplete, weak, or logically flawed in a realistic way.
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors.
- If the task is a feature task, the starter code should include only the basic structure and wiring.
- Do NOT include TODO comments.
- Do NOT include comments that reveal the solution.
- Do NOT include fake LLMs, stub LLMs, deterministic stand-ins for model output, regex-only intent parsing, or sleep-based simulation of LLM behavior.
- Real LLM calls must be implemented through a provider SDK or router and configured from environment variables at runtime.
- Offline tests may exercise retrieval, formatting, redaction, citation validation, or evaluation helpers without calling a provider key, but they must not replace the actual generation path with a fake model as the central task.
- Include local sample documents that are specific to the selected real-world scenario and small enough for quick ingestion.
- Include focused invariant tests for INTERMEDIATE level, such as idempotent ingestion, metadata filtering, thresholded refusal, citation grounding, PII masking, empty-index behavior, or regression evaluation depending on the selected scenario.
- The generated project structure should be runnable, but required task behavior should remain incomplete until the candidate implements it.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.

## .gitignore INSTRUCTIONS
Create a sensible Python gitignore for a RAG task, including:
- __pycache__/
- *.pyc
- .venv/
- venv/
- .env
- .pytest_cache/
- .mypy_cache/
- *.log
- build/
- dist/
- *.egg-info/
- .DS_Store
- pgvector_data/
- postgres_data/
- .coverage
- htmlcov/
- local database volume directories
- any generated cache files for embeddings or evaluations that should not be committed

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain EXACTLY the following sections, in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the generated Python + RAG scenario. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the selected real-world scenario and must not include database connection details.

### Task Overview
- Must contain 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- Must be specific to the selected real-world scenario and document domain.
- NEVER empty.
- NO bold time-budget callouts.
- Explain the observable RAG failure or quality problem without naming the exact implementation fix.

### Objectives
- INTERMEDIATE objectives MUST be concise and OPEN-ENDED.
- Include 3-4 bullets maximum; fewer, tighter is better.
- Each objective states ONE desired outcome in a single short line, roughly 8-16 words.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, or direct code reference.
- Do NOT pad objectives into two-clause "after your changes" sentences.
- Do NOT collapse objectives into bare two-word labels.
- Good objective style: "Keep repeated document updates from degrading retrieval quality."
- Good objective style: "Return grounded answers when the knowledge base contains supporting evidence."
- Good objective style: "Avoid exposing sensitive source content in user-facing responses."
- Bad objective style: "Add chunk_hash in app/ingestion.py so duplicates are skipped."
- Bad objective style: "Use pgvector HNSW and similarity threshold constants."

### Helpful Tips
- Provide practical guidance without revealing specific implementations.
- Include 4-5 bullets maximum.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Helpful Tips should orient candidates toward the RAG symptom, data flow, quality checks, edge cases, and operational behavior without telling them where or how to patch the code.

### How to Verify
- Include 3-5 bullets maximum.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, response shape, retrieval quality, citation behavior, latency observation, log line, or refusal behavior.
- For tasks that call a real LLM through `.env.example`, How to Verify MUST open with a GitHub note admonition embedded INSIDE the section as a blockquote, never a new heading:
  > [!NOTE]
  > Copy `.env.example` to `.env` and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.
- Do not include setup commands such as package installation, Docker startup, or environment deployment commands.
- Do not include database connection details, host, port, username, password, psql instructions, or client-tool suggestions.
- If mentioning local service checks, use localhost only and avoid any droplet IP or remote-host placeholder.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of README.md:
- Setup commands such as `npm install`, `pip install`, `docker compose up`, `mvn test`, or similar deployment instructions
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database-connection details, including host, port, username, password, connection strings, or database client-tool suggestions
- Droplet IP placeholders such as `<DROPLET_IP>`
- Directive phrases like "you should implement", "add this middleware", "create this class", or "use <specific API>"

## REQUIRED OUTPUT JSON STRUCTURE
The generated response must be valid JSON only and must follow this exact structure. Each field's value must be fully populated and candidate-safe.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the selected Python RAG scenario without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name and specific to the selected RAG problem.",
  "question": "A complete candidate-facing task description explaining the business scenario, current RAG failure or missing capability, and what outcomes the candidate must achieve without revealing exact implementation steps.",
  "code_files": {{
    "README.md": "Candidate-facing README content that follows exactly the required four sections: Task Overview, Objectives, Helpful Tips, and How to Verify, with concise open-ended guidance and no setup commands or database credentials.",
    ".gitignore": "A comprehensive Python and pgvector project gitignore that excludes caches, virtual environments, environment files, logs, build artifacts, test artifacts, and local database volume directories.",
    "requirements.txt": "Python dependency list for the runnable project, including fastembed, psycopg binary support, python-dotenv, pytest, pydantic, and a real LLM SDK or router while excluding torch, transformers, and sentence-transformers.",
    ".env.example": "Example environment file containing empty provider key placeholders such as OPENAI_API_KEY or ANTHROPIC_API_KEY and a local DATABASE_URL using localhost with the same database credentials as docker-compose.",
    "docker-compose.yml": "Docker Compose configuration with no version key, a single pgvector PostgreSQL service, inline POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB values, a localhost-only port binding, a healthcheck, and an init SQL mount.",
    "run.sh": "Readiness script that installs dependencies, starts pgvector with docker compose, waits for database health, validates schema and imports, avoids running failing invariant tests, avoids real LLM calls, uses python3 for every Python invocation, and exits successfully on the unsolved starter.",
    "init_database.sql": "PostgreSQL initialization SQL that enables pgvector and creates the starter RAG schema with vector(384) embeddings, realistic metadata columns, and scenario-appropriate constraints or intentionally incomplete areas that do not reveal the solution.",
    "app/__init__.py": "Python package marker that keeps the application importable during readiness checks.",
    "app/config.py": "Configuration module that reads local environment settings safely, exposes database and provider configuration, and does not contain secrets.",
    "app/db.py": "Database connection and lightweight helper module for psycopg interactions with clear error handling and no solution-revealing comments.",
    "app/ingestion.py": "Starter ingestion module that reads scenario fixture documents, normalizes or parses content, coordinates chunking and embedding, and contains the realistic incomplete behavior the candidate must improve.",
    "app/chunker.py": "Starter chunking module that exposes reusable text splitting behavior and leaves room for the candidate to improve chunk quality or metadata handling.",
    "app/embeddings.py": "Fastembed wrapper module using BAAI/bge-small-en-v1.5 and 384-dimensional vectors, with practical batching behavior but no heavyweight model dependencies.",
    "app/retrieval.py": "Starter retrieval module that queries pgvector and contains scenario-appropriate weaknesses in filtering, thresholds, ranking, or result handling for the candidate to diagnose.",
    "app/generation.py": "Generation module that assembles retrieved context and calls a real LLM provider SDK or router using runtime credentials, without fake or deterministic LLM stand-ins.",
    "app/evaluation.py": "Evaluation helper module for retrieval quality, citation checks, faithfulness-oriented validation, refusal behavior, or regression measurements appropriate to the selected scenario.",
    "app/main.py": "Optional lightweight API or CLI entry point that wires the RAG workflow together and remains runnable without solving the core behavior.",
    "data/sample_doc_1.md": "A small scenario-specific source document with realistic business content used for local ingestion and retrieval testing.",
    "data/sample_doc_2.md": "A second scenario-specific source document that introduces contrasting metadata, edge cases, or evidence needed for meaningful retrieval evaluation.",
    "invariants/test_rag_behavior.py": "Visible pytest suite that candidates can run to validate observable RAG outcomes such as ingestion idempotency, metadata-aware retrieval, grounding, citations, redaction, refusal behavior, or empty-result handling without requiring a live LLM key.",
    "additional_files_as_needed": "Any other minimal project files needed to make the Python package runnable and the assessment realistic, while keeping the core task unsolved."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the intended RAG improvements, Python design changes, database or retrieval reasoning, testing strategy, and tradeoffs at a non-code level.",
  "definitions": "An object of concise term-to-definition pairs for concepts that help evaluate the task domain, such as embedding, chunking, metadata filtering, similarity search, pgvector, grounding, citation, retrieval recall, or faithfulness.",
  "hints": "A single-line candidate-safe hint that nudges investigation toward the relevant RAG flow or observable symptom without naming the exact fix, files, APIs, thresholds, or implementation details.",
  "outcomes": "Two to three concise lines describing measurable expected results after completion, including improved retrieval quality, grounded responses, robust error handling, and production-level clean code with proper naming, exception handling, logging, and clear project structure.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Python 3.11 proficiency, comfort with pytest and PostgreSQL-backed local development, familiarity with embeddings and RAG evaluation, and access to a provider key via .env when running end-to-end generation.",
  "short_overview": "A bullet list summarizing the business problem, the technical RAG focus, and the expected outcome in simple English, emphasizing correctness, retrieval quality, groundedness, and maintainability."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The generated task must align with INTERMEDIATE Python and INTERMEDIATE Retrieval Augmented Generation proficiency.
3. The project must be substantial and realistic, with multiple interacting Python modules and changes required across more than one file.
4. Use pgvector through PostgreSQL in Docker Compose; do not add extra datastores unless the selected scenario explicitly requires them.
5. docker-compose.yml must not include a version specification.
6. docker-compose.yml must use inline `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` values; do not use `.env` or `${{VAR}}` host indirection for datastore initialization.
7. **SECURITY-CRITICAL**: PostgreSQL port mapping must bind to localhost only using `127.0.0.1:5432:5432`.
8. Use fastembed with a 384-dimensional model such as `BAAI/bge-small-en-v1.5`; never use sentence-transformers, torch, or transformers.
9. Include `.env.example` for real LLM provider keys, but do not include real keys.
10. The task must require real LLM generation for end-to-end behavior; do not use FakeLLM, StubLLM, deterministic stand-ins, or regex-only model substitutes.
11. `run.sh` must install Python dependencies first, start pgvector, wait for health, validate schema/imports, avoid live LLM calls, avoid running failing grader-style tests, and exit 0 on the unsolved but deployable starter.
12. Every Python invocation inside shell scripts must use `python3`, never bare `python`.
13. Do not include `kill.sh`.
14. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, and no other sections.
15. README.md must not include setup commands, database connection details, client-tool suggestions, droplet IP placeholders, direct solutions, or step-by-step implementation guides.
16. README Objectives for INTERMEDIATE must be concise, open-ended, outcome-focused, and must not name files, methods, APIs, libraries, functions, variables, tables, or exact solution mechanisms.
17. The `pre_requisites` field must contain assumed prior knowledge only, not imperative setup or verification steps.
18. The title must be different from the name and use plain English.
19. The task must be completable within {minutes_range} minutes.
20. The generated task must reflect the selected real-world scenario closely and must not invent an unrelated domain.
21. requirements.txt MUST list every third-party package imported anywhere in the generated code (e.g. `openai` for `from openai import OpenAI`, `pydantic-settings` for `import pydantic_settings`). Before finalizing, cross-check every import statement in every generated .py file against requirements.txt — a missing dependency is an automatic rejection.
22. Dependency version pins must install on Python 3.13. Do NOT pin exact old versions (e.g. `fastembed==0.4.2` does not exist for Python 3.13 — fastembed needs `>=0.5`). Use lower-bound pins for fastembed (`fastembed>=0.5`), and for other packages either use lower-bound pins or exact versions you are certain support Python 3.13.
23. The pgvector `vector` extension must be created exclusively by `init_database.sql` mounted into `/docker-entrypoint-initdb.d/`, and `run.sh` must verify the extension exists (e.g. `SELECT 1 FROM pg_extension WHERE extname='vector'`) BEFORE invoking any Python that connects to the database. Python connection helpers must never call `pgvector`'s `register_vector` on a database where the extension might not yet exist — schema creation in Python must not be the mechanism that first requires the vector type.
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), Retrieval Augmented Generation (RAG) (INTERMEDIATE)": [
        PROMPT_PYTHON_RAG_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_RAG_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_RAG_INTERMEDIATE_INSTRUCTIONS,
    ]
}