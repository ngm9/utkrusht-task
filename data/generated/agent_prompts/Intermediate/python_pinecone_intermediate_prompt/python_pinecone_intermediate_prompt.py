PROMPT_PYTHON_PINECONE_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_PINECONE_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Pinecone assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, retrieval/search or ingestion context, and the problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python and Pinecone implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE Pinecone proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_PINECONE_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python and Pinecone-backed retrieval systems, you are given a list of real world scenarios and proficiency levels for Python and Pinecone.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a moderately complex Python application that integrates with Pinecone using INTERMEDIATE-level skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Intermediate Python with functions, classes, modules, packages, and object-oriented design
- File operations and data serialization with JSON or CSV
- Use of third-party packages with pip and virtual environments
- API creation or consumption where needed
- Basic networking and concurrency awareness only if helpful, but not as the main challenge
- Unit tests with pytest or unittest
- Debugging, refactoring, error handling, and code quality improvements
- Moderate performance-minded improvements suitable for a single service or script-based project

### Allowed Pinecone scope
- Pinecone indexes, namespaces, vectors, metadata, and collections
- Similarity search fundamentals including metric choice, top-k retrieval, and ANN vs exact-search tradeoffs at a conceptual level
- Data modeling for semantic search, RAG, and multi-tenant retrieval
- Ingestion pipelines using upsert, update, delete, and fetch APIs
- Batch ingestion, retry handling, idempotent writes, and validation of vector dimensions and metadata
- Querying with metadata filters, namespace routing, and result shaping
- Retrieval tuning, top-k selection, and practical quality/performance tradeoffs
- Integration with embedding generation and Python application backends
- Reliability patterns such as retries, timeout handling, fallback behavior, and safe API key handling
- Observability through logging, simple metrics-oriented checks, and troubleshooting ingestion/query issues
- Testing retrieval behavior, ingestion correctness, and regression scenarios
- Documentation of architecture, data lifecycle, and troubleshooting notes

### Out of scope and MUST NOT be primary requirements
- Kubernetes, Helm, Terraform, or infrastructure-as-code as the main challenge
- Multi-service distributed systems or microservices architecture
- Advanced security hardening as the main task
- Full LLM orchestration frameworks as the main competency
- Fine-tuning embedding models
- Heavy cloud provisioning or enterprise platform administration
- Complex distributed observability stacks

## INTERMEDIATE PROFICIENCY CALIBRATION
For INTERMEDIATE level, the task should combine 4-5 connected concepts in one coherent workflow. Suitable combinations include:
- ingestion + deterministic IDs + metadata enrichment + Pinecone upsert batching + regression tests
- fixing a broken search API + namespace or metadata filter corrections + timeout/error handling + result shaping
- improving retrieval quality + reducing duplicates + validating embedding/index consistency + adding evaluation checks
- implementing a moderate Pinecone-backed search flow with tenant-aware filtering, robust Python structure, and measurable verification

The task should require practical reasoning, debugging, and moderate architecture decisions, but it must remain solvable in one sitting within {minutes_range} minutes.

## NATURE OF THE TASK
- Task must ask the candidate to implement a feature from scratch or fix meaningful issues in an existing Python + Pinecone application
- The scenario must be realistic and business-oriented, not a toy example
- The task must be specific and well-scoped for INTERMEDIATE proficiency
- The task should focus on a single application workflow with 4-5 connected concepts, such as:
  - record or document ingestion,
  - embedding generation or validation,
  - Pinecone index or namespace usage,
  - metadata-aware search,
  - retries and timeout handling,
  - result shaping,
  - evaluation or regression checks,
  - logging and error handling
- The task must NOT depend on real Pinecone credentials or external cloud setup during assessment runtime
- The task must use a Pinecone-compatible abstraction or mockable adapter so the environment is runnable locally while still clearly assessing Pinecone concepts and APIs
- The task must NOT include hints in the question itself
- The task should be completable within {minutes_range} minutes

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools
- The task should still require practical reasoning and adaptation, not just copying boilerplate
- The generated task should reward candidates who can understand a moderate codebase, connect ingestion to indexing to retrieval, and improve correctness, maintainability, and reliability

## INFRASTRUCTURE REQUIREMENTS FOR VECTOR_DB CATEGORY
The task category is VECTOR_DB, so the generated project MUST follow this structure:
- MUST be a Python project
- MUST include Docker-based infrastructure
- MUST include a Python application service
- MUST include requirements.txt
- MUST include runnable source files
- MUST include local sample data in the repository
- MUST include run.sh and kill.sh
- The baseline environment must start successfully before the candidate begins work

Because Pinecone is a managed external service, do NOT require a live Pinecone account or real API key for the candidate to start the task. Instead:
- Use Docker for the Python application service and any local support service needed for the runnable baseline
- Model Pinecone integration through a dedicated adapter module that mirrors realistic Pinecone operations such as upsert, query, fetch, delete, namespace selection, and metadata filtering
- The task must still explicitly assess Pinecone concepts, data modeling, retrieval behavior, and operational reasoning
- If you include a local mock service, keep it lightweight and focused on enabling a runnable environment rather than replacing the Pinecone concepts being tested

## STARTER CODE INSTRUCTIONS
- The starter code should provide a clear starting point without solving the core task
- The generated code files must be valid and executable
- Keep the code files focused and reasonably modular
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors
- If the task is a feature task, the starter code should include only the basic structure and wiring
- The project should be runnable, but the core required behavior should remain incomplete, incorrect, or insufficient until the candidate finishes the task
- Do NOT include comments that reveal the solution
- Do NOT include TODO comments or placeholder hints
- Include tests or evaluation scaffolding for INTERMEDIATE level, but do not implement the final passing logic

## DEPLOYMENT REQUIREMENTS
The environment must be fully deployable in one go.

### docker-compose.yml
- MUST include the Python application service
- MAY include one lightweight local support service if needed for the runnable baseline
- MUST NOT include a version field
- MUST use hardcoded configuration values rather than .env references for service wiring
- MUST expose the application port if an API is used
- Keep the compose file minimal and reliable

### Dockerfile
- MUST build a working Python application image
- MUST install dependencies from requirements.txt
- MUST run the application with a simple command
- MUST be valid and functional on first build

### run.sh
Generate this script with the following behavior:
- Use `#!/usr/bin/env bash` and `set -e`
- Start services with `docker-compose up -d --build`
- Wait for the application service to become reachable
- If startup fails, print docker-compose logs and exit with code 1
- End with a clear success message showing the application URL and any relevant local endpoints

### kill.sh
Generate this script with the following behavior:
- Use `#!/usr/bin/env bash` and `set -e`
- `cd /root/task` before cleanup
- Run `docker-compose down --rmi all --volumes --remove-orphans || true`
- Force-stop and remove any remaining containers with `docker ps -q` and `docker ps -aq` commands using `|| true`
- Run `docker volume prune -f || true`, `docker image prune -a -f || true`, and `docker system prune -a --volumes -f || true`
- Remove `/root/task` at the end with `rm -rf /root/task || true`
- Print progress messages before each major step
- End with `echo "[kill.sh] Cleanup completed."`
- The script must be idempotent

## DATA AND TASK DESIGN REQUIREMENTS
- Include a small but realistic local dataset in JSON or CSV
- Include metadata fields that matter to the scenario, such as tenant, category, status, language, region, or document type
- The task should explicitly involve Pinecone-style concepts such as:
  - deterministic vector IDs,
  - namespace strategy,
  - metadata filters,
  - top-k tuning,
  - duplicate prevention,
  - retry-safe ingestion,
  - timeout or degraded-mode handling,
  - retrieval verification
- Include an evaluation or regression script and/or tests that check observable behavior
- Evaluation should stay practical and lightweight, such as checking whether relevant records appear in top-k results, whether filters exclude unrelated records, whether duplicate ingestion is prevented, or whether invalid requests are handled cleanly

## RECOMMENDED TASK SHAPES
Prefer one of these task shapes:
1. A search API with broken Pinecone query behavior:
   - missing namespace or metadata filters,
   - overly large top_k,
   - poor timeout handling,
   - duplicate or cross-tenant results,
   - weak result shaping,
   - missing regression tests

2. An ingestion job with broken lifecycle behavior:
   - random IDs causing duplicate vectors,
   - no batching,
   - no retry/backoff for transient failures,
   - missing metadata needed for filtering,
   - no ingest report,
   - no idempotency test

3. A retrieval-quality improvement task:
   - mismatched embedding dimensions or metric assumptions,
   - poor metadata schema,
   - irrelevant results due to over-broad queries,
   - no evaluation script,
   - weak logging and error handling

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters.",
  "question": "Structured task description. Clearly describe the current implementation and the required changes. The current implementation must exactly match the starter code state. The required changes must be specific, measurable, and aligned to Python and Pinecone intermediate scope.",
  "code_files": {{{{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python and Docker exclusions",
    "requirements.txt": "Python dependencies including fastapi or flask if used, pytest, and any libraries required by the starter project",
    "docker-compose.yml": "Docker Compose for the application service and any lightweight support service",
    "Dockerfile": "Dockerfile for the Python application",
    "run.sh": "Deployment script that starts services and waits for readiness",
    "kill.sh": "Cleanup script",
    "app/main.py": "Application entry point",
    "app/config.py": "Configuration values and paths",
    "app/models.py": "Request and response models",
    "app/pinecone_adapter.py": "Pinecone integration abstraction or mockable adapter",
    "app/embeddings.py": "Embedding generation or embedding adapter module",
    "app/ingestion.py": "Data loading and ingestion module",
    "app/search.py": "Search and result shaping module",
    "app/evaluation.py": "Evaluation or regression-check module",
    "data/sample_records.json": "Sample business records or documents with metadata",
    "tests/test_search.py": "Test skeletons or regression tests",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }}}},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing the business problem, the implementation or fix goal, and the expected outcome emphasizing correctness, Pinecone-aware retrieval behavior, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, Docker, Docker Compose, intermediate Python development, and Pinecone concepts such as indexes, namespaces, metadata filters, top-k retrieval, and idempotent ingestion.",
  "answer": "High-level solution approach describing the intended architecture and reasoning at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{{{
    "Namespace": "A logical partition within a Pinecone index used to isolate groups of vectors",
    "Metadata Filter": "A constraint applied during retrieval to limit results by attributes such as tenant, category, or status",
    "Top-k Retrieval": "Returning the k most relevant results for a query",
    "Idempotent Ingestion": "An ingestion process that can be run multiple times without creating unintended duplicates",
    "Vector ID": "The unique identifier used to upsert, update, fetch, or delete a vector record"
  }}}}
}}}}

## CODE FILE REQUIREMENTS
- More than one file may be generated, but all must be listed correctly in the JSON structure
- Code should follow Python PEP 8 guidelines
- Use clear module boundaries and readable project structure
- The generated code files MUST NOT contain the implementation for the core logic of the task
- The core ingestion, ID generation, metadata filtering, query shaping, retry logic, timeout handling, evaluation logic, or optimization logic that the candidate must complete should be left empty or minimally stubbed
- Do NOT include comments that reveal the solution
- Do NOT include TODO comments
- The generated project structure should be runnable, but the required task behavior should remain incomplete until the candidate implements it
- Include proper tests or evaluation scaffolding for INTERMEDIATE level where appropriate

## README.md STRUCTURE
The README.md must contain the following sections:
- Task Overview
- Helpful Tips
- Objectives
- How to Verify

The README must be concise and candidate-safe.

### Task Overview
- Must contain 2-3 meaningful sentences describing the business scenario and current state of the application
- Must explain why the task matters in the business context
- Must be specific to the generated scenario

### Helpful Tips
- 3-4 bullets maximum
- Use action words like "Consider", "Review", "Explore", "Think about"
- Guide discovery without revealing the implementation
- Do not mention exact solution steps or exact method names that would give away the answer

### Objectives
- 3-5 bullets maximum
- Describe what should work after completion
- Focus on outcomes, not implementation details
- Keep objectives measurable and appropriate for INTERMEDIATE level
- Include expectations around metadata behavior, namespace or ID correctness where relevant, retrieval quality, robustness, and verification

### How to Verify
- 3-5 bullets maximum
- Describe observable behaviors to validate
- Include checks such as whether records are searchable, whether filters exclude unrelated results, whether duplicate ingestion is handled correctly if relevant, whether retries or degraded behavior work as expected, and whether tests or evaluation outputs pass
- Do not include setup commands

### NOT TO INCLUDE in README
- Step-by-step implementation instructions
- Direct solutions
- Code snippets
- Setup commands
- Candidate-facing solution explanations

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The task must align with INTERMEDIATE proficiency and combine 4-5 concepts.
3. Use Python 3.10+ and current Python package conventions.
4. The task category is VECTOR_DB, so the generated project MUST include Docker-based infrastructure plus a Python app.
5. The task must explicitly assess Pinecone concepts, not generic vector database concepts alone.
6. Do not require real Pinecone credentials or external cloud provisioning for the runnable baseline.
7. Include local sample data and realistic metadata.
8. Include testing or evaluation expectations appropriate for INTERMEDIATE level.
9. Keep secrets out of version control and mention safe API key handling only at the design level.
10. The task must be completable within {minutes_range} minutes.
11. The title must be different from the name and use plain English.
12. The generated task must reflect one selected real-world scenario closely.
13. Prefer a working baseline where deployment succeeds first and the candidate focuses on Python implementation quality, Pinecone-aware data modeling, retrieval correctness, and reliability.
"""

PROMPT_REGISTRY = {
    "Pinecone (INTERMEDIATE), Python (INTERMEDIATE)": [
        PROMPT_PYTHON_PINECONE_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_PINECONE_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_PINECONE_INTERMEDIATE_INSTRUCTIONS,
    ]
}