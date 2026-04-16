PROMPT_VECTOR_DATABASES_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_VECTOR_DATABASES_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Vector Databases assessment task.

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

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Vector Databases proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_VECTOR_DATABASES_BASIC = """
## GOAL
As a senior data engineer super experienced in vector databases, embeddings, similarity search, and retrieval-augmented generation (Milvus, Faiss, Weaviate, Qdrant, Pinecone, pgvector), you are given a list of real world scenarios and proficiency levels for Vector Databases development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years vector database experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental vector database concepts like:
  - Understanding vector vs relational/document stores and when to use each
  - Working with high-dimensional embeddings (text, image, audio embedding models)
  - Embedding dimension consistency, normalization, and validation
  - Cosine, dot-product, and Euclidean distance metrics and their trade-offs
  - Creating collections with correct parameters (dimension, metric type)
  - Basic CRUD operations on vector collections (insert, upsert, delete, query)
  - k-NN search, hybrid Boolean+vector search, and range queries
  - Index configuration basics (HNSW, IVF_FLAT, efConstruction, nlist, M, efSearch)
  - Connecting to vector stores via Python SDKs (pymilvus, qdrant-client, pinecone-client, etc.)
  - Basic ingestion pipelines: batching, idempotent upserts, metadata attachment
  - Simple retrieval quality checks (precision@k, recall@k)
  - Handling common errors: dimension mismatch, connection failures, memory issues
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Python best practices (Python 3.10+) and current vector database SDK standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic vector database proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Vector Databases task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years vector database experience), keeping in mind that AI assistance is allowed.
- Tests practical vector database skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single-service vector database patterns rather than complex distributed architectures
- The task environment should use Docker Compose to spin up the vector database (e.g., Milvus standalone, Qdrant, Weaviate) along with the Python application

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `docker-compose up` followed by running the Python application.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Starter code should include a docker-compose.yml with the vector database service and a basic Python project structure with requirements.txt
- Use Flask or FastAPI for the REST API layer for simplicity

## INFRASTRUCTURE REQUIREMENTS (Docker)

**CRITICAL — ONE-GO DEPLOYMENT**: When run.sh is executed, all containers must start successfully, the vector database must be healthy, and the application must be ready to use. Deployment must NOT fail. The candidate receives a working environment from the start; their only job is to fix or improve the given vector database problem.

### docker-compose.yml
- Must include the vector database service (Qdrant, Milvus standalone, or Weaviate) and the Python application service.
- Hardcoded configuration — no `.env` file references, no environment variable placeholders for service config.
- The vector database service must expose its default port to the host (e.g., Qdrant: 6333, Milvus: 19530, Weaviate: 8080).
- The Python application service must expose its API port (e.g., 5000 or 8000) to the host.
- Use a named volume for the vector database data so it persists across restarts.
- **No `version:` field** in the compose file.
- The application service must depend on the vector database service with a health check.
- If seed data needs to be loaded, mount the data files into the application container.

### run.sh
Generate this script with the following EXACT structure and behaviour:

**run.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- Run `docker-compose up -d --build` to start all services.
- Include a health check loop that waits for the vector database to be ready:
  - For Qdrant: curl the health endpoint `http://localhost:6333/healthz` or `/readyz`
  - For Milvus: check the gRPC port or health endpoint
  - For Weaviate: curl `http://localhost:8080/v1/.well-known/ready`
- After the vector DB is healthy, wait for the application service to be ready (curl the health or root endpoint).
- If either check fails after retries, print docker-compose logs and exit with code 1.
- End with a clear success message showing the application URL and vector DB connection info.

### kill.sh
Generate this script with the following EXACT structure — this is the required cleanup pattern:

**kill.sh rules:**
- Use `#!/usr/bin/env bash` and `set -e` at the top.
- MUST `cd /root/task` first so `docker-compose down` can find the `docker-compose.yml`.
- MUST run `docker-compose down --rmi all --volumes --remove-orphans` to remove compose-managed containers, named volumes, networks, and images in one step.
- MUST then explicitly force-stop ALL running containers with `docker ps -q` — this catches any container that `docker-compose down` missed.
- MUST explicitly remove ALL containers with `docker ps -aq` before pruning.
- MUST run `docker volume prune -f`, then `docker image prune -a -f`, then `docker system prune -a --volumes -f` — in this order. Running all three ensures nothing is left behind even if earlier steps partially succeed.
- MUST `rm -rf /root/task` as the final step after all Docker cleanup is done.
- Every destructive command MUST end with `|| true` so the script never exits early due to "already removed" errors.
- The script MUST be idempotent — safe to run multiple times on an already-clean droplet.
- Print a progress message before every major step.
- End with `echo "[kill.sh] Cleanup completed."`.

### Seed Data
- If the task involves pre-loaded vectors or documents, include a `data/` directory with seed data files (CSV, JSON, or text).
- Include a seed script (`seed_data.py` or similar) that loads the initial data into the vector database. This script should be run automatically by `run.sh` after the vector DB is healthy, OR by the application on startup.
- The seed data must load successfully without errors. The candidate should NOT need to fix data loading unless that IS the task.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Vector Search for Product Recommendations', 'Fix Embedding Ingestion Pipeline for Document Store', 'Build Semantic Search API with Milvus'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive Python and IDE exclusions",
    "requirements.txt": "Python dependencies including vector DB SDK, Flask/FastAPI, embedding libraries",
    "docker-compose.yml": "Docker Compose with vector database service (Qdrant/Milvus/Weaviate) and app service — follows rules above",
    "run.sh": "Deploy script — follows run.sh rules above exactly",
    "kill.sh": "Cleanup script — follows kill.sh rules above exactly",
    "Dockerfile": "Dockerfile for the Python application",
    "app/main.py": "Main application entry point with Flask/FastAPI",
    "app/vector_store.py": "Vector store connection and operations module",
    "app/ingestion.py": "Embedding ingestion pipeline module",
    "app/search.py": "Search/query module",
    "app/config.py": "Configuration and constants",
    "data/seed_data.csv or data/seed_data.json": "Seed data for initial vector loading (if applicable)",
    "seed_data.py": "Script to load seed data into vector DB (if applicable)",
    "additional_file.py": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, Docker, Docker Compose, vector database fundamentals (embeddings, similarity metrics, indexing), familiarity with at least one vector DB SDK.",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on embedding dimension consistency, proper upsert logic, and choosing the right distance metric for your use case'",
  "definitions": {{
    "Embedding": "A dense numerical vector representation of data (text, images, etc.) in high-dimensional space",
    "k-NN Search": "k-Nearest Neighbors search — finding the k most similar vectors to a query vector",
    "Cosine Similarity": "A distance metric measuring the cosine of the angle between two vectors, ranging from -1 to 1",
    "HNSW Index": "Hierarchical Navigable Small World — a graph-based approximate nearest neighbor index",
    "Upsert": "An insert-or-update operation that avoids duplicates by updating existing records with the same ID"
  }}
}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Python best practices (type hints, docstrings where needed, proper error handling)
- Use proper project structure (app/ directory with modules)
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core vector database operations, ingestion logic, search implementations, or index configuration that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement search" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Python projects including __pycache__, .pyc files, virtual environments (venv/, .venv/), IDE configurations (.idea, .vscode), .env files, log files, Docker volumes, and other common development artifacts that should not be tracked in version control.

## README.md STRUCTURE (Vector Databases)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery — suggest areas to explore, not specific solutions
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level vector database task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around observable outcomes and expected behavior
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Describe what behaviors to verify and how to confirm success
  - Focus on observable outcomes (search results relevance, ingestion success, error handling)
  - Do NOT specify specific code, SDK methods, or implementation details to check
  - **CRITICAL**: Describe what behaviors to verify, not specific code or APIs to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (docker-compose up, pip install, etc.)
- Specific vector DB SDK methods or class names that reveal the solution
- Phrases like "you should implement", "add the following code", "create a method called X"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "product-vector-search-api")
3. **code_files** must include README.md, .gitignore, requirements.txt, docker-compose.yml, run.sh, kill.sh, Dockerfile, and Python source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable (docker-compose up) but must NOT contain the solution
6. **Deployment must succeed in one go** — After run.sh, all containers must be healthy, vector DB ready, app accessible. The candidate only fixes or improves the vector database problem, not deployment.
7. **run.sh** must follow the exact rules above: health check loop for vector DB, wait for app, fail with logs on error
8. **kill.sh** must follow the exact rules above: docker-compose down, force-stop containers, prune volumes/images/system, rm -rf /root/task, all with `|| true`
9. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
10. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
11. **hints** must be a single line; **definitions** must include relevant vector database terms
12. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
13. **NO comments in code** that reveal the solution or give hints
14. **Use Python 3.10+** conventions throughout
15. **Focus on single service vector database patterns**, not complex distributed architectures
16. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
17. **docker-compose.yml must NOT have a `version:` field** — use modern compose format
"""
PROMPT_REGISTRY = {
    "Vector Databases (BASIC)": [
        PROMPT_VECTOR_DATABASES_CONTEXT_BASIC,
        PROMPT_VECTOR_DATABASES_INPUT_AND_ASK_BASIC,
        PROMPT_VECTOR_DATABASES_BASIC,
    ],
}
