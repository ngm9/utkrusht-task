PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Vector Databases assessment task.

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
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, retrieval/search context, and the problem the candidate will be solving)
2. What will the task look like? (Describe the type of Python and vector database implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE Vector Databases proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, vector search systems, embeddings, and retrieval APIs, you are given a list of real world scenarios and proficiency levels for Python and Vector Databases.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a moderately complex vector-search application using INTERMEDIATE-level Python and INTERMEDIATE-level Vector Database skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Intermediate Python with functions, classes, modules, packages, and object-oriented design
- File operations and data serialization with JSON or CSV
- Use of third-party packages with pip and virtual environments
- API creation or consumption where needed
- Basic concurrency awareness only if helpful, but not as the primary challenge
- Unit tests with pytest or unittest
- Debugging, refactoring, error handling, and code quality improvements
- Moderate performance-minded improvements suitable for a local project

### Allowed Vector Database scope
- End-to-end vector search workflow using Python and a vector store such as Qdrant, Weaviate, Milvus, pgvector, Elasticsearch, Pinecone, Chroma, or FAISS-backed local flow where appropriate
- Embedding generation and validation, including dimension consistency and basic batching
- Similarity search using cosine, inner product, or Euclidean distance
- Metadata-aware retrieval and simple hybrid-style filtering using attached metadata
- Chunking, deduplication, and ingestion of local documents or records
- Index creation and tuning at a practical local-project level
- Retrieval API implementation using FastAPI or Flask
- Basic reranking or result shaping if relevant, but keep it moderate
- Recall/latency tradeoff checks, simple evaluation scripts, and regression tests
- Persistence and reload of local vector data where supported by the chosen stack
- Troubleshooting common issues such as bad metadata filters, duplicate ingestion, dimension mismatch, poor recall, or unnecessary re-indexing

### Out of scope and MUST NOT be primary requirements
- Kubernetes, Helm, Terraform, or multi-node cluster operations
- Heavy cloud provisioning or managed platform administration
- Advanced security engineering as the main task
- Complex distributed systems design
- Full RAG orchestration with LLM frameworks as the main competency
- Fine-tuning embedding models
- Large-scale observability stacks as the main focus

## INTERMEDIATE PROFICIENCY CALIBRATION
For INTERMEDIATE level, the task should combine 4-5 concepts in one coherent workflow. Suitable combinations include:
- ingestion + metadata enrichment + vector persistence + filtered search + regression tests
- fixing a broken retrieval API + correcting embedding/index consistency + improving result ranking + adding error handling
- reducing duplicate vectors + improving query relevance + adding evaluation checks + preserving reload behavior
- implementing a local semantic search service with source metadata, filter support, and measurable retrieval quality checks

The task should require practical reasoning, debugging, and moderate architecture decisions, but it must remain solvable in one sitting within {minutes_range} minutes.

## NATURE OF THE TASK
- Task must ask the candidate to implement a feature from scratch or fix meaningful issues in an existing Python + vector database application
- The scenario must be realistic and business-oriented, not a toy example
- The task must be specific and well-scoped for INTERMEDIATE proficiency
- The task should focus on a single local application workflow with 4-5 connected concepts, such as:
  - document or record ingestion,
  - embedding generation and validation,
  - vector collection/index setup,
  - metadata-aware search,
  - persistence and reload,
  - evaluation or regression checks,
  - error handling and moderate performance improvements
- The task must NOT depend on distributed infrastructure as the main challenge
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field
- The task should be completable within {minutes_range} minutes

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools
- The task should still require practical reasoning and adaptation, not just copying boilerplate
- The generated task should reward candidates who can understand a moderate codebase, connect ingestion to indexing to retrieval, and improve correctness, maintainability, and reliability

## CODE GENERATION INSTRUCTIONS
Based on the real-world scenarios provided, create a Python + Vector Database task that:
- Draws inspiration from one selected scenario to determine the business context and search domain
- Matches INTERMEDIATE proficiency for both Python and Vector Databases
- Tests practical skills with local data ingestion, embeddings, vector indexing, metadata filtering, retrieval quality, and testing
- Uses a lightweight local project structure suitable for the VECTOR_DB category
- Can be completed within {minutes_range} minutes
- Uses a different scenario each time to ensure variety
- Keeps the focus on vector search quality and application correctness, not on infrastructure complexity

## INFRASTRUCTURE REQUIREMENTS FOR VECTOR_DB CATEGORY
- MUST be a Python project using a real vector store or vector database setup
- MUST include Docker-based infrastructure for the vector database service
- MUST include a Python application service
- MUST include requirements.txt
- MUST include runnable source files
- MUST include local sample data in the repository
- MUST include a run.sh and kill.sh
- The baseline environment must start successfully before the candidate begins work
- The candidate should inherit a working setup with intentionally incomplete, incorrect, or suboptimal vector-search behavior

### Recommended stack shape
Use one of these practical local setups:
- Qdrant + FastAPI + sentence-transformers or a deterministic local embedding helper
- Chroma + FastAPI if you keep Docker only for the app and local persistence, but prefer a true vector DB service for this category
- Weaviate or Milvus only if the setup remains lightweight and reliable

Prefer Qdrant for simplicity and reliability unless the selected scenario strongly suggests another option.

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
- MUST include the vector database service and the Python application service
- MUST NOT include a version field
- MUST use hardcoded configuration values rather than .env references for service wiring
- MUST expose the vector database port and application port
- MUST use a named volume for vector database persistence where appropriate
- The application service must depend on the vector database service and wait for readiness
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
- Wait for the vector database to become healthy
- Wait for the application service to become reachable
- If startup fails, print docker-compose logs and exit with code 1
- End with a clear success message showing the application URL and vector database connection details
- If seed data is required, ensure it is loaded automatically before the candidate starts

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

## DATA AND EVALUATION REQUIREMENTS
- Include a small but realistic local dataset in JSON, CSV, or markdown/text files
- Include enough records or chunks to make retrieval quality meaningful
- Include metadata fields that matter to the scenario, such as category, source, language, region, product line, or document type
- Include an evaluation or regression script and/or tests that check observable retrieval behavior
- Evaluation should stay practical and lightweight, such as checking whether relevant sources appear in top-k results or whether filters exclude unrelated records

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Improve Metadata-Aware Search for Support Knowledge Base', 'Fix Semantic Retrieval for Product Policy Lookup', 'Enhance Vector Search API for Internal Playbooks'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local storage artifacts, and .env",
    "requirements.txt": "Python dependencies including fastapi, uvicorn, vector DB client, pytest, and any embedding-related libraries used in the starter project",
    "docker-compose.yml": "Docker Compose with vector database service and app service",
    "Dockerfile": "Dockerfile for the Python application",
    "run.sh": "Deployment script that starts services and waits for readiness",
    "kill.sh": "Cleanup script that removes containers, volumes, images, and /root/task",
    "app/main.py": "Application entry point",
    "app/config.py": "Configuration values and paths",
    "app/models.py": "Request and response models",
    "app/embeddings.py": "Embedding generation or embedding adapter module",
    "app/ingestion.py": "Data loading and ingestion module",
    "app/vector_store.py": "Vector store connection and collection operations",
    "app/search.py": "Search and result shaping module",
    "app/evaluation.py": "Evaluation or regression-check module",
    "data/sample_records.json": "Sample business records or documents with metadata",
    "tests/test_search.py": "Test skeletons or regression tests",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, retrieval quality, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, Docker, Docker Compose, intermediate Python development, and vector database concepts such as embeddings, similarity metrics, metadata filters, indexing, and evaluation.",
  "answer": "High-level solution approach describing the intended architecture and reasoning at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "Embedding": "A dense numerical representation of data used for similarity search",
    "Metadata Filter": "A constraint applied during retrieval to limit results by attributes such as category or source",
    "Cosine Similarity": "A similarity measure based on the angle between two vectors",
    "Top-k Retrieval": "Returning the k most relevant results for a query",
    "Vector Index": "A data structure used to search embeddings efficiently"
  }}
}}

## CODE FILE REQUIREMENTS
- More than one file may be generated, but all must be listed correctly in the JSON structure
- Code should follow Python PEP 8 guidelines
- Use clear module boundaries and readable project structure
- The generated code files MUST NOT contain the implementation for the core logic of the task
- The core ingestion, embedding validation, vector upsert, metadata filtering, retrieval ranking, persistence handling, evaluation logic, or optimization logic that the candidate must complete should be left empty or minimally stubbed
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

The README must be concise and open-ended. Each section should contain only the essential points needed to understand the task.

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
- Include expectations around retrieval quality, metadata behavior, persistence or reload behavior, and robustness

### How to Verify
- 3-5 bullets maximum
- Describe observable behaviors to validate
- Include checks such as whether records are searchable, whether filters exclude unrelated results, whether duplicate ingestion is handled correctly if relevant, whether persisted data can be reused if relevant, and whether invalid input is handled gracefully
- Include verification of tests or evaluation outputs where relevant
- Do not include setup commands

### NOT TO INCLUDE in README
- Step-by-step implementation instructions
- Direct solutions
- Code snippets
- Setup commands
- Candidate-facing solution explanations
- Heavy architecture discussion unrelated to the task

## CANDIDATE-VISIBLE OUTPUT POLICY
- The generated task JSON must be candidate-safe
- Keep solution guidance out of candidate-visible files
- The task should assess implementation skill, debugging ability, and practical reasoning rather than memorization

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The task must align with INTERMEDIATE proficiency and combine 4-5 concepts.
3. Use Python 3.10+ and current vector database client conventions.
4. The task category is VECTOR_DB, so the generated project MUST include Docker-based vector database infrastructure plus a Python app.
5. Keep the project local and lightweight.
6. Include local sample data and realistic metadata.
7. Include testing or evaluation expectations appropriate for INTERMEDIATE level.
8. Keep secrets out of version control.
9. The task must be completable within {minutes_range} minutes.
10. The title must be different from the name and use plain English.
11. The generated task must reflect the selected real-world scenario closely.
12. Do not require Kubernetes, multi-node operations, or heavy cloud infrastructure as the main task.
13. Prefer a working baseline where deployment succeeds first and the candidate focuses on vector-search correctness and quality improvements.
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), Vector Databases (INTERMEDIATE)": [
        PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_CONTEXT,
        PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PYTHON_VECTOR_DATABASES_INTERMEDIATE_INSTRUCTIONS,
    ]
}