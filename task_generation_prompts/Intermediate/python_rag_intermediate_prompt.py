PROMPT_RAG_PYTHON_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_RAG_PYTHON_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and Retrieval-Augmented Generation (RAG) assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document or knowledge context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and RAG implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE RAG proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_RAG_PYTHON_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, retrieval-augmented generation, and vector search, you are given a list of real world scenarios and proficiency levels for Python and RAG.
Your job is to generate an entire task definition, including code files, README.md, run.sh, kill.sh, docker-compose.yml, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a moderately complex RAG application using INTERMEDIATE-level Python and INTERMEDIATE-level RAG skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Intermediate Python with functions, classes, modules, packages, and object-oriented design
- File operations and data serialization with JSON or CSV
- Use of third-party packages with pip and virtual environments
- API consumption or lightweight local app wiring where needed
- Basic networking and concurrency awareness where helpful, but not as the primary challenge
- Unit tests with pytest
- Debugging, refactoring, error handling, and code quality improvements
- Performance-minded improvements appropriate for a moderate-complexity local project

### Allowed RAG scope
- End-to-end retrieval pipeline: document ingestion, splitting, embedding, indexing, retrieval, generation
- Document loaders for local files (text, PDF, CSV, Markdown)
- Text splitting strategies (recursive character, sentence, token-aware) and their trade-offs
- Embedding models — see the INFRASTRUCTURE section for the required choice; tasks must NOT pin sentence-transformers / torch-based models
- Vector indexing in pgvector (HNSW or IVFFlat) with explicit `vector(N)` columns and similarity operators (`<=>`, `<#>`, `<->`)
- Metadata-aware retrieval and filtering (e.g. `WHERE source = $1 AND embedding <=> $2 LIMIT k`)
- Hybrid retrieval combining keyword search (`ILIKE`, `tsvector`) and vector search where the scenario benefits from it
- Re-ranking, MMR-style diversification, or threshold-based filtering
- Prompt construction with retrieved context, citation formatting, and answer grounding
- Token, latency, or cost awareness at a practical project level
- Evaluation: faithfulness checks, retrieval recall, citation correctness, regression tests against a small fixture set
- Caching, batching, idempotent ingestion, and graceful degradation when retrieval returns nothing
- Guardrails: prompt-injection resistance, output validation, empty-result handling

### Out of scope and MUST NOT be primary requirements
- Large-scale distributed deployment
- Kubernetes or microservices architectures as the main task
- Fine-tuning embedding or generation models
- GPU-only paths (the sandbox is CPU-only)
- sentence-transformers, torch, transformers — these inflate the install footprint by multiple gigabytes and break the sandbox; pick fastembed instead

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a feature from scratch or fix meaningful issues in an existing Python + RAG application backed by pgvector.
- The task must be specific and well-scoped for INTERMEDIATE proficiency.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should focus on a single application workflow with 4-5 connected concepts, such as:
  - ingestion + chunking strategy + pgvector schema design,
  - embedding generation + indexing + similarity search,
  - metadata-aware retrieval + citation formatting,
  - empty-corpus and malformed-input handling,
  - evaluation or regression coverage.
- The task must NOT depend on distributed systems design or external infrastructure as the main challenge.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### INTERMEDIATE proficiency calibration
For INTERMEDIATE level, the task should combine 4-5 concepts in a coherent workflow. Suitable combinations include:
- broken ingestion (missing metadata, no deduplication) + retriever returning wrong sources + add evaluation harness + handle empty index
- swap a placeholder embedding for a real one + add an HNSW index + tune k and similarity threshold + add citation extraction
- design the pgvector schema + add hybrid retrieval (keyword + vector) + harden the API for malformed input + add a regression test set
- repair a faithfulness leak (LLM ignoring retrieved context) + tighten the prompt + add a faithfulness check + add a fallback when retrieval is empty

The task should require practical reasoning, debugging, and moderate architecture decisions, but it must remain solvable in one sitting.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can read a moderate codebase, understand the RAG pipeline end to end, and make defensible choices on schema, retrieval, and grounding.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + RAG task that:
- Draws inspiration from one selected scenario to determine the business context and document domain.
- Matches INTERMEDIATE proficiency for both Python and RAG.
- Tests practical skills with local documents, pgvector schema, embedding, retrieval, generation, and evaluation.
- Uses the INFRASTRUCTURE stack defined below — this is non-negotiable.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## INFRASTRUCTURE — REQUIRED STACK (do not deviate)

This task must run on the sandboxed E2B environment, which is CPU-only and disk-constrained. Pick the lightweight stack:

- **Database:** pgvector (image `pgvector/pgvector:pg16`) brought up by `docker-compose.yml`. Expose port 5432 on localhost. Use POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB env vars.
- **Embeddings:** `fastembed` (`pip install fastembed`). Default model `BAAI/bge-small-en-v1.5` (384 dimensions). NEVER use sentence-transformers / torch.
- **LLM (generation):** OpenAI via `.env.example` (`OPENAI_API_KEY`). The candidate may swap providers, but the baseline must work with OpenAI. Do NOT include real keys.
- **API surface:** FastAPI on port 5000 with at least one POST endpoint for the RAG query.
- **Database driver:** `psycopg[binary] >= 3.1` (or `psycopg2-binary >= 2.9.10` if the candidate prefers; pin >=2.9.10 to avoid Python 3.13 build failures on `psycopg2-binary==2.9.9`).
- **App run model:** the FastAPI app runs on the host inside the sandbox (NOT in a container). Only pgvector runs in Docker. The `run.sh` brings pgvector up, waits for it to become healthy, runs migrations / ingestion, and then starts uvicorn. This avoids torch-class image-build problems.

### Required files in the repo

The task MUST generate these files in addition to the application code. They are non-negotiable for E2B deployment:

- `docker-compose.yml` — defines a single `db` service using `pgvector/pgvector:pg16` with a healthcheck (`pg_isready`).
- `run.sh` — `set -e`, brings up `docker-compose up -d`, polls until pg is healthy, `pip install -r requirements.txt`, runs ingestion / migration script, then starts uvicorn on `0.0.0.0:5000`. Must export `DATABASE_URL=postgresql://USER:PASS@localhost:5432/DB`. Must NOT block forever — uvicorn should be started with `nohup` or similar so the script returns.
- `kill.sh` — `docker-compose down -v` and `pkill -f uvicorn || true`.
- `requirements.txt` — pinned to fastembed, fastapi, uvicorn, psycopg[binary]>=3.1 (or psycopg2-binary>=2.9.10), pydantic, openai, python-dotenv, plus pypdf or markdown loader as the scenario needs.
- `.env.example` — `OPENAI_API_KEY=`, `DATABASE_URL=postgresql://courseuser:coursepass@localhost:5432/coursedb` (placeholders).
- `app/main.py`, `app/schema.sql` (or migration script), `app/ingestion.py`, `app/embeddings.py`, `app/retrieval.py`, `app/generation.py`, `app/evaluation.py`.
- `data/sample_doc_1.md`, `data/sample_doc_2.md` — small sample documents grounded in the scenario.
- `tests/test_app.py` — at least two tests covering the failure modes the task asks the candidate to fix.

## Starter Code Instructions
- The starter code should provide a clear starting point without solving the core task.
- The generated code files must be valid and executable.
- Keep the code files focused and reasonably modular.
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors.
- If the task is a feature task, the starter code should include only the basic structure and wiring.
- The project should be runnable, but the core required behavior should remain incomplete, incorrect, or insufficient until the candidate finishes the task.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments or placeholder hints.
- Include tests or evaluation scaffolding for INTERMEDIATE level, but do not implement the final passing logic.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Course-Aware RAG Retrieval over pgvector', 'Harden Document Ingestion and Retrieval for Policy Q&A', 'Improve Faithfulness and Citation Quality in Support Assistant'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, .env, and the pgvector data volume",
    "requirements.txt": "Python dependencies (see INFRASTRUCTURE section). MUST pin fastembed; MUST NOT include sentence-transformers/torch/transformers.",
    ".env.example": "OPENAI_API_KEY= and DATABASE_URL=postgresql://courseuser:coursepass@localhost:5432/coursedb",
    "docker-compose.yml": "Single `db` service using pgvector/pgvector:pg16 on port 5432 with a pg_isready healthcheck",
    "run.sh": "set -e; docker-compose up -d; wait-for-healthy loop; pip install -r requirements.txt; python -m app.ingestion (or schema.sql apply); nohup uvicorn app.main:app --host 0.0.0.0 --port 5000 > uvicorn.log 2>&1 &",
    "kill.sh": "docker-compose down -v; pkill -f uvicorn || true",
    "app/main.py": "FastAPI app entry point with the RAG endpoint(s)",
    "app/schema.sql": "CREATE EXTENSION vector; CREATE TABLE documents (id, source, chunk, metadata, embedding vector(384), ...); CREATE INDEX (HNSW or IVFFlat) on embedding",
    "app/embeddings.py": "fastembed wrapper exposing `embed_texts(list[str]) -> list[list[float]]` and the model name",
    "app/ingestion.py": "Loads sample docs, splits them, embeds via embeddings.py, and inserts into pgvector",
    "app/retrieval.py": "Similarity search query against pgvector, with metadata filter and k parameter",
    "app/generation.py": "Prompt assembly with retrieved context, citation extraction, OpenAI client call (or stub for offline tests)",
    "app/evaluation.py": "Helpers for the regression test set: faithfulness check, retrieval recall, citation correctness",
    "data/sample_doc_1.md": "Sample business document",
    "data/sample_doc_2.md": "Additional sample business document",
    "tests/test_app.py": "pytest skeletons covering at minimum: empty-index handling and one scenario-specific failure mode",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, retrieval quality, and groundedness.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, Docker + docker-compose, intermediate Python development, basic SQL, and RAG concepts (chunking, embedding, similarity search, prompt grounding, evaluation).",
  "answer": "High-level solution approach describing the intended architecture and reasoning at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "Embedding": "A fixed-size vector that represents the semantic content of text",
    "Chunking": "Splitting documents into smaller passages so retrieval can find precise context",
    "Similarity Search": "Finding the chunks whose embeddings are closest to the query embedding under a chosen distance metric (cosine, L2, inner product)",
    "pgvector": "A Postgres extension that adds a vector data type and similarity operators (<=>, <#>, <->) plus HNSW and IVFFlat indexes",
    "Faithfulness": "Whether the generated answer is grounded in the retrieved context and does not invent claims"
  }}
}}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use clear module boundaries and readable project structure.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core ingestion, retrieval, generation, evaluation, or schema design that the candidate must complete should be left empty or minimally stubbed.
- Do NOT include any comments that reveal the solution.
- Do NOT include TODO comments.
- The generated project structure should be runnable, but the required task behavior should remain incomplete until the candidate implements it.
- Include proper tests or evaluation scaffolding for INTERMEDIATE level where appropriate.

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
- pgvector_data/ or any local volume directory

## README.md STRUCTURE

The README.md must contain the following sections:
- Task Overview
- Helpful Tips
- Objectives
- How to Verify

The README must be concise and open-ended. Each section should contain only the essential points needed to understand the task. Do NOT overload it with too many bullets.

### Task Overview
- Must contain 2-3 meaningful sentences describing the business scenario and current state of the application.
- Must explain why the task matters in the business context.
- Must be specific to the generated scenario.

### Helpful Tips
- 3-4 bullets maximum.
- Use action words like "Consider", "Review", "Explore", "Think about".
- Guide discovery without revealing the implementation.
- Do not mention exact solution steps or exact method names that would give away the answer.

### Objectives
- 3-5 bullets maximum.
- Describe what should work after completion.
- Focus on outcomes, not implementation details.
- Keep objectives measurable and appropriate for INTERMEDIATE level.
- Include expectations around correctness, retrieval quality, faithfulness, and robustness.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether documents are searchable, whether answers cite the right sources, whether the schema and index exist in pgvector, whether retrieval respects metadata, and whether invalid input is handled gracefully.
- Include verification of tests or evaluation outputs where relevant.
- Do not include setup commands.

### NOT TO INCLUDE in README
- Step-by-step implementation instructions
- Direct solutions
- Code snippets
- Setup commands
- Candidate-facing solution explanations
- Heavy architecture discussion unrelated to the task

## Candidate-visible output policy
- The generated task JSON must be candidate-safe.
- Keep solution guidance out of candidate-visible files.
- The task should assess implementation skill, debugging ability, and practical reasoning rather than memorization.

## CRITICAL REMINDERS
1. Output must be valid JSON only when the prompt is later used to generate a task.
2. The task must align with INTERMEDIATE proficiency and combine 4-5 concepts.
3. Use Python 3.10+ and pgvector for the vector store.
4. Use fastembed for embeddings — never sentence-transformers, torch, or transformers.
5. Include local sample documents and a working pgvector schema.
6. Include testing or evaluation expectations appropriate for INTERMEDIATE level.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
11. docker-compose.yml must use `pgvector/pgvector:pg16` and only the `db` service. The Python app runs on the host.
12. run.sh must end with uvicorn started in the background so the script returns.
"""

PROMPT_REGISTRY = {
    "Python (INTERMEDIATE), Retrieval Augmented Generation (RAG) (INTERMEDIATE)": [
        PROMPT_RAG_PYTHON_INTERMEDIATE_CONTEXT,
        PROMPT_RAG_PYTHON_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_RAG_PYTHON_INTERMEDIATE_INSTRUCTIONS,
    ],
}
