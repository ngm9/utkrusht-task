PROMPT_RAG_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_RAG_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a RAG (Retrieval-Augmented Generation) assessment task.

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

1. What will the task be about? (Describe the business domain, data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of data manipulation/analysis required, the expected deliverables, and how it aligns with the proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_RAG_BASIC = """
## GOAL
As a technical architect experienced in Docker containerization and RAG (Retrieval-Augmented Generation) systems, you are given real-world scenarios and proficiency levels for Docker. Your job is to generate a deployment-ready task for basic-level Docker practitioners (1-2 years experience) where a candidate receives a RAG application that is already fully containerized and deployable, and where the candidate must improve and harden the deployment and/or RAG pipeline based on the scenario.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios (input_scenarios) to frame the task. The business context, domain, RAG use case, and technical requirements should directly align with the given scenario. The balance between Docker containerization work and RAG pipeline improvement will naturally depend on the specific scenario requirements.
**CRITICAL**: This marked **updates are just what we ahve updated in the prompt then previously to track the previous version of the prompt and the changes we have made to the prompt.
**very important**: so the task should be completely build according to the task scenarios that will provided the task that is to be done by the candidate that should not be implemented already in teh code files
The candidate's primary responsibility is to understand, validate, and improve an existing Dockerized RAG system appropriate to the scenario. This may involve refining containerization (best practices, observability, configuration) and/or enhancing RAG retrieval quality or generation as dictated by the scenario. Do NOT generate broken configurations; do NOT give away solutions or hint at implementations in task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a RAG application with a working baseline, whose quality and robustness vary by scenario. The application includes:
- A basic but functional RAG system that is already deployable and working end-to-end
- ChromaDB vector database with pre-populated, queryable data
- RAG pipeline with retrieval and generation logic (may need enhancement based on scenario)
- Python/FastAPI application code that may require improvements
- Dependencies configured in requirements.txt
- Dockerfile and docker-compose.yml that are correct and functional but may be basic or suboptimal
- ChromaDB vector database that is containerized (NOT standalone) and accessible from the app
- **CRITICAL**: The system MUST be deployable and functional in its current state before any candidate changes
- **CRITICAL**: The baseline system MUST work without any external LLM/embedding API keys and without relying on internet access at runtime. Any integration with external LLM providers (e.g., OpenAI, Anthropic) MUST be optional and not required for core functionality.

**TASK SCOPE**: The task naturally balances Docker deployment hardening with RAG pipeline enhancement based on the scenario. It demonstrates understanding appropriate for 1-2 years Docker experience, focusing on improving an existing working system rather than making it run for the first time.

  **Docker Focus Areas (as relevant to scenario):**
  - Understanding and using official Python base images
  - Proper WORKDIR, COPY, and CMD/ENTRYPOINT usage
  - Port exposure for API endpoints
  - .dockerignore creation for Python projects
  - Docker-compose for RAG app + ChromaDB
  - Container networking between app and ChromaDB using service names
  - Volume mounting for ChromaDB persistence
  - Environment configuration for connections and non-secret configuration
  - Understanding container logs and debugging
  - **UPDATE**: Removed health check implementation focus - simplified startup without complex health dependencies
  - **UPDATE**: Optimized Dockerfile layer caching strategies (requirements before source code)
  - **CRITICAL**: ChromaDB MUST be deployed through Docker, not standalone, and MUST be reachable from the app

  **RAG Application Work (as required by scenario):**
  - Enhancing retrieval strategies if scenario requires
  - Improving embedding or search quality
  - Modifying RAG pipeline for better results
  - Implementing enhanced retrieval patterns (e.g., hybrid search, re-ranking)
  - Query optimization based on scenario
  - Prompt engineering and response formatting (even if generation is simple or template-based)
  - Any scenario-specific RAG improvements

- Questions must NOT hint at solutions - hints provided separately
- Follow Docker best practices for RAG applications
- Include diagrams in mermaid format showing architecture in README.md

## Task Scenario Integration Requirements:
- **BUSINESS CONTEXT**: Extract and use the real-world RAG use case from input_scenarios
- **RAG PATTERN**: Implement retrieval and generation pipeline matching the scenario
- **VECTOR DATABASE**: Must be ChromaDB containerized with pre-populated data
- **IMPLEMENTATION REQUIREMENTS**: Distinguish clearly between what is functional and what needs enhancement
- **COMPLETENESS LEVEL**: System works but may need improvements per scenario
- **TECHNICAL REQUIREMENTS**: Incorporate all technologies mentioned in scenario
- **DOCKER CHALLENGE**: Frame the challenge around improving robustness, maintainability, and observability of deployment, not rescuing a broken deployment
- **CONSISTENCY**: README, question, and code reflect same scenario
- **VARIETY**: Pick different scenarios to ensure diversity

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates can use Google, documentation, AI tools, LLMs
- Tasks assess ability to understand and apply Docker concepts for RAG applications
- May also assess ability to enhance RAG pipelines as required by scenario
- AI helps with syntax but doesn't replace fundamental understanding
- **CRITICAL**: The generated task must be fully solvable and the baseline system fully functional WITHOUT any external API keys or internet access. Optional extensions MAY allow external LLM providers via environment variables, but this MUST NOT be required.

## Code Generation Instructions:
Create scenario-driven tasks that:
- **MUST draw directly from input_scenarios**
- Match basic Docker proficiency (1-2 years experience)
- **BASE DIRECTORY**: /root/task for all files
- **DEPLOYABLE STATE**: System must work end-to-end before enhancements or refactors
- Time constraint: Completable within {minutes_range} minutes
- **Use varied scenarios** to ensure diversity
- **SCENARIO AUTHENTICITY**: Solve real-world RAG problem from scenario

## Infrastructure Requirements:
**DEPLOYMENT ROBUSTNESS - CRITICAL REQUIREMENTS:**

1. **Python Dependencies Configuration:**
   - requirements.txt MUST include ALL required dependencies
   - **MANDATORY for ChromaDB client & RAG**: chromadb>=0.5.0
   - Common: fastapi>=0.104.0, uvicorn>=0.24.0, pydantic>=2.0.0
   - **UPDATE**: Use ChromaDB's lightweight default embedding function - NO heavy ML dependencies like sentence-transformers or PyTorch required
   - **UPDATE**: chromadb>=0.5.0 includes built-in embedding functions that work without external dependencies
   - Optional: openai, anthropic, or similar ONLY if the scenario explicitly mentions them as optional extensions; the baseline must not depend on them
   - Other utilities: requests (for HTTP calls), python-dotenv (for .env support)
   - All versions compatible and tested
   - Pin major versions (e.g., fastapi>=0.104.0,<1.0.0, chromadb>=0.5.0,<1.0.0)
   - **UPDATE**: Minimal dependency set to reduce image size and startup time

2. **Dockerfile for RAG Application:**
   - Use python:3.11-slim or python:3.10-slim (avoid alpine for better compatibility)
   - WORKDIR /app
   - **UPDATE**: Optimized layer caching strategy:
```
     COPY requirements.txt .
     RUN pip install --no-cache-dir -r requirements.txt
     COPY src/ ./src/
```
   - This ensures dependency layers are cached and only rebuild when requirements.txt changes, not when source code changes
   - EXPOSE API port (typically 8000)
   - **UPDATE**: Install curl for basic connectivity checks: `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*`
   - CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   - Environment variables for configuration (e.g., CHROMA_HOST, CHROMA_PORT)
   - ONLY use official Python images

   **CRITICAL**: The generated Dockerfile MUST build successfully and run the FastAPI app without modification.

3. **ChromaDB Deployment - CRITICAL:**
   - **MANDATORY**: Deployed through Docker using official chromadb/chroma image
   - Use chromadb/chroma:latest or chromadb/chroma:0.5.0 (or recent stable version)
   - **DATA PRE-POPULATION REQUIRED**:
     - ChromaDB must have collections created and data embedded/indexed ready for querying
     - Use initialization script (Python) that runs BEFORE the main RAG app starts
     - Data relevant to scenario (20-50+ document chunks minimum)
     - **UPDATE**: Use ChromaDB's default embedding function (no external embedding model required)
   - **CRITICAL**: Candidate can query ChromaDB immediately without running any ingestion manually
   - **UPDATE**: ChromaDB network access:
     - Inside Docker network: accessible at http://chromadb:8000 (service name resolution)
     - Exposed to host: port 8001 mapped to container port 8000 (8001:8000)
   - **UPDATE**: Volume mounting - persistent data directory at /data:
     - volumes: ["chroma_data:/data"]
     - PERSIST_DIRECTORY=/data
   - **UPDATE**: Removed health check configuration - rely on simple startup ordering
   - Environment variables:
     - IS_PERSISTENT=TRUE
     - **UPDATE**: PERSIST_DIRECTORY=/data (changed from /chroma/chroma)
     - ANONYMIZED_TELEMETRY=FALSE

4. **Docker-Compose Configuration:**
   - MUST NOT include version field (deprecated)
   - Hardcoded values (except non-secret config can use .env)
   - **THREE MAIN SERVICES**:
     1. ChromaDB (chromadb/chroma)
     2. Data initialization service (runs once to populate ChromaDB, then exits)
     3. RAG application (Python/FastAPI)
   
   - **Service Definitions**:
   
     **chromadb service**:
     - image: chromadb/chroma:0.5.23
     - container_name: chromadb
     - **UPDATE**: ports: ["8001:8000"]  # host 8001 maps to container 8000 (ChromaDB's default port)
     - **UPDATE**: volumes: ["chroma_data:/data"]  # persistent volume at /data
     - environment:
       - IS_PERSISTENT=TRUE
       - **UPDATE**: PERSIST_DIRECTORY=/data  # changed from /chroma/chroma
       - ANONYMIZED_TELEMETRY=FALSE
        CHROMA_INIT_MAX_RETRIES: 60
      CHROMA_INIT_SLEEP_SECONDS: 3
     - **UPDATE**: Removed healthcheck configuration - simplified startup
     - **UPDATE**: restart: unless-stopped (automatic restart on failure)
   
     **chroma-init service** (data initialization):
     - build:
       - context: .
       - dockerfile: Dockerfile.init
     - container_name: chroma-init
     - **UPDATE**: Simple depends_on without health conditions:
```
       depends_on:
         - chromadb
```
     - environment:
       - CHROMA_HOST=chromadb
       - CHROMA_PORT=8000
     - volumes: ["./init-scripts:/app/init-scripts:ro"]
     - **UPDATE**: Add sleep/retry logic in the init script itself to wait for ChromaDB to be ready
     - command: python /app/init-scripts/load_data.py
     - **UPDATE**: restart: "no"  # Run once and exit, don't restart on failure
   
     **rag-app service**:
     - build:
       - context: .
       - dockerfile: Dockerfile
     - container_name: rag-app
     - **UPDATE**: Simple depends_on without health conditions:
```
       depends_on:
         - chromadb
         - chroma-init
```
     - **UPDATE**: Add retry logic in application startup code to wait for ChromaDB and data availability
     - **UPDATE**: ports: ["8000:8000"]  # host 8000 maps to container 8000
     - environment:
       - CHROMA_HOST=chromadb
       - CHROMA_PORT=8000
       # Optional: LLM_PROVIDER, LLM_API_KEY for scenarios that allow external LLMs, but baseline must not require them
     - volumes: ["./src:/app/src:ro"]
     - **UPDATE**: restart: unless-stopped (automatic restart on failure)
     - **UPDATE**: Removed healthcheck configuration - rely on application-level readiness
   
   - **Volumes**:
     - **UPDATE**: chroma_data: {{volume_name}} (named volume persists at /data in container)
   
   - **UPDATE**: Service names MUST match application code references (use "chromadb" as hostname for internal Docker network communication)
   - **UPDATE**: Proper service startup order: ChromaDB → Init → RAG app (enforced by depends_on, with retry logic in each service)

   **CRITICAL**: docker-compose.yml MUST successfully bring up all services and allow the RAG pipeline to run end-to-end as generated.

5. **Application Configuration:**
   - Python config file (src/config.py) or environment variables
   - **UPDATE**: ChromaDB connection using docker-compose service name on internal network: CHROMA_HOST=chromadb, CHROMA_PORT=8000
   - Ports consistent across code, Dockerfile, docker-compose
   - Optional environment variables for external LLM integration, but core functionality must not depend on them
   - **UPDATE**: No embedding model configuration needed - use ChromaDB's default embedding function
   - Collection name(s) consistent between init script and app
   - **CRITICAL**: RAG pipeline functional with current config, using ChromaDB's default embeddings and deterministic response generation (e.g., using retrieved context in a template) even without any external LLM

6. **ChromaDB Data Initialization - MANDATORY:**
   - **Dockerfile.init**: Separate Dockerfile for the initialization service
     - FROM python:3.11-slim
     - WORKDIR /app
     - **UPDATE**: Optimized layer caching:
```
       COPY requirements.txt .
       RUN pip install --no-cache-dir chromadb>=0.5.23 requests python-dotenv
       COPY init-scripts/ /app/init-scripts/
```
     - **UPDATE**: Removed heavy dependencies (sentence-transformers, PyTorch) - use ChromaDB's default embedding
     - CMD will be overridden in docker-compose
   
   - **init-scripts/load_data.py**: Python script that:
     - **UPDATE**: Implements retry logic (sleep + retry loop) to wait for ChromaDB to be ready before connecting adn time out should be 5 
     - Connects to ChromaDB at http://chromadb:8000 using service name resolution
     - Creates a collection (e.g., "documents", scenario-specific name)
     - **UPDATE**: Uses ChromaDB's default embedding function (no external model needed)
     - Loads data from init-scripts/sample_data.json
     - Adds documents to ChromaDB collection (embeddings generated automatically by ChromaDB)
     - Verifies data is queryable (performs a test query)
     - Is safe to run multiple times (idempotent: should not corrupt or duplicate data if executed more than once)
     - Logs success and exits with code 0
   
   - **init-scripts/sample_data.json**: JSON file with:
     - Array of documents, each with "id", "text", "metadata"
     - Data relevant to scenario domain (e.g., legal docs, customer support, medical info)
     - Sufficient quantity (20-50+ documents)
   
   - **CRITICAL INITIALIZATION FLOW**:
     1. docker-compose up starts chromadb first
     2. **UPDATE**: chroma-init service starts after chromadb (simple depends_on), implements its own retry logic to wait for ChromaDB readiness
     3. chroma-init runs load_data.py, populates ChromaDB, exits with code 0
     4. **UPDATE**: rag-app service starts after chroma-init (simple depends_on), implements its own retry logic to verify data availability
     5. RAG app connects to ChromaDB and finds data already present
   
   - Data should be:
     - Relevant to scenario domain
     - Sufficient quantity (20-50+ chunks)
     - **UPDATE**: Embedded using ChromaDB's default embedding function (no external model required)
     - Ready for immediate querying

7. **File System:**
   - All paths reference /root/task
   - Proper WORKDIR usage in Dockerfiles
   - **UPDATE**: Volume paths configured correctly (chroma_data named volume at /data in container)
   - **UPDATE**: No local model cache needed - ChromaDB's default embedding function has no heavy downloads

### Run.sh Requirements:
- Optionally load variables from a .env file if present, but MUST NOT depend on API keys for core functionality
- Executes `docker-compose up -d --build`
- **UPDATE**: Simplified waiting mechanism (no complex health check polling):
  - Wait for containers to start (check docker-compose ps)
  - **UPDATE**: Wait for chroma-init service to complete (check `docker-compose ps chroma-init` shows "Exited (0)") - poll every 5 seconds for up to 60 seconds
  - **UPDATE**: Wait for rag-app service to be running (check `docker-compose ps rag-app` shows "Up") - poll every 5 seconds for up to 60 seconds
  - **UPDATE**: Simple application readiness check: curl http://localhost:8000/health with retries (up to 30 seconds)
  - Check logs for successful startup messages if needed
  - **CRITICAL**: Verify data is queryable via a sample curl query to /query endpoint
- Test query example: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{{"query": "test query based on scenario"}}'`
- Error handling for failures at each stage
- All paths reference /root/task
- Clear output showing startup progress for each service
- Final verification that RAG pipeline is operational with data

**CRITICAL**: The generated run.sh MUST work as-is and MUST NOT rely on candidate modifications or any external API keys.

### Kill.sh Requirements:
- Stop and remove containers: `docker-compose down --volumes --remove-orphans`
- Remove project images: `docker rmi $(docker images -q '*task*') 2>/dev/null || true`
- Remove chroma_data volume explicitly: `docker volume rm $(docker volume ls -q | grep chroma_data) 2>/dev/null || true`
- Optionally, perform broader cleanup (e.g., docker system prune) ONLY if droplet is dedicated to this task
- Remove task directory: `rm -rf /root/task`
- Idempotent and safe to run multiple times
- Clear logging at each step

### Dockerfile Instructions (for RAG app):
- Clean, production-ready Dockerfile
- Official Python image (python:3.11-slim)
- **UPDATE**: Optimized layer caching strategy (requirements.txt first, then source code):
```
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ ./src/
  EXPOSE 8000
  CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- Install curl for basic connectivity checks
- Environment variable support for CHROMA_HOST, CHROMA_PORT, and optional LLM settings
- **UPDATE**: Minimal dependencies to reduce image size

### Dockerfile.init Instructions (for initialization):
- Minimal Dockerfile to run initialization script
- FROM python:3.11-slim
- **UPDATE**: Optimized layer caching (requirements first, then scripts)
- Install chromadb>=0.5.0, requests, python-dotenv
- **UPDATE**: No heavy ML dependencies (removed sentence-transformers, PyTorch)
- COPY init-scripts
- Default CMD can be overridden by docker-compose

### ChromaDB Configuration:
- Official chromadb/chroma image
- **UPDATE**: HTTP API exposed on port 8000 inside Docker network, mapped to host port 8001 (8001:8000)
- **UPDATE**: Persistent volume for data at /data in container
- Environment variables for server configuration (IS_PERSISTENT, PERSIST_DIRECTORY=/data, ANONYMIZED_TELEMETRY)
- **UPDATE**: Removed health check configuration - simplified startup
- **UPDATE**: restart: unless-stopped for automatic recovery
- **CRITICAL**: Fully functional with data pre-populated by init service

## .gitignore INSTRUCTIONS:
Comprehensive file including:
- Python: __pycache__/, *.py[cod], *$py.class
- Virtual environments: venv/, env/
- IDE: .idea/, .vscode/
- Data: data/, chroma_data/, *.db
- Logs: *.log, logs/
- Docker: .docker/
- Environment: .env, .env.local
- OS: .DS_Store, Thumbs.db
- Testing: .pytest_cache/, .coverage
- Distribution: dist/, build/, *.egg-info/

## .dockerignore INSTRUCTIONS:
May be missing or basic - candidate improves:
- Exclude: __pycache__/, .git/, .idea/, *.md, .gitignore, *.log, data/, chroma_data/, .env, venv/
- Keep: src/, init-scripts/, requirements.txt, Dockerfile, Dockerfile.init

## README.md STRUCTURE:

### Task Overview (MANDATORY - 3-4 substantial sentences)
**CRITICAL**: Must contain 2-3 meaningful sentences describing the business scenario, RAG use case, and current situation. 
Never generate empty content - provide substantial business context. 

### Objectives
 **CRITICAL**: Generate objectives DIRECTLY from the task_scenarios requirements, not from examples below.
  - Clear, measurable goals appropriate for basic level that align with the scenario
  - These objectives describe what the candidate should achieve to complete the task successfully
  - These objectives will be used to verify task completion and award points
  - Focus on the specific improvements or implementations required by the task_scenarios
  - Frame objectives around both Docker deployment AND RAG functionality as dictated by the scenario 
  - Examples:
    * "Ensure the system retrieves relevant information from ChromaDB based on queries"
    * "Verify generated responses use retrieved context from the vector database"
    * "Establish connectivity between RAG app and ChromaDB container using service names"
    * "Confirm embedding and retrieval pipeline processes queries correctly using ChromaDB's default embedding"
    * "Test vector similarity search returns appropriate results from ChromaDB"
    * "Validate that ChromaDB is pre-populated with data and queryable"
    * **UPDATE**: "Verify data persists across container restarts using Docker volumes"
  - Guide candidates on: retrieval quality, generation accuracy, connectivity, data availability, persistence
  - **CRITICAL**: Describe "what" needs to work, not "how"

### Application Access
- Access details: http://<DROPLET_IP>:8000 for RAG API
- API endpoints:
  - POST /query - Submit queries to the RAG system
  - GET /health - Health check endpoint
  - GET /docs - FastAPI Swagger documentation
- **UPDATE**: ChromaDB endpoints (for debugging):
  - GET http://<DROPLET_IP>:8001/api/v1/heartbeat - ChromaDB readiness
  - GET http://<DROPLET_IP>:8001/api/v1/collections - List collections
- Scenario-specific endpoints and expected behaviors

### How to Verify
  - Specific checkpoints after implementation
  - Observable behaviors to validate
  - Frame in terms of RAG outcomes
  - Examples:
    * "Send test queries and verify relevant information is retrieved from ChromaDB"
    * "Confirm generated responses incorporate context from retrieved documents"
    * "Test domain-specific questions get appropriate answers"
    * "Verify ChromaDB contains expected data by checking collections endpoint"
    * **UPDATE**: "Check that chroma-init service exited successfully (docker-compose ps shows Exited 0)"
    * "Test edge cases with no relevant data and verify graceful handling"
    * "Validate all Docker services started successfully"
    * **UPDATE**: "Restart containers and verify data persists (docker-compose restart chromadb)"
    * "Query ChromaDB directly via port 8001 to verify data presence"
  - Guide on testing: retrieval quality, generation accuracy, connectivity, data availability, persistence
  - **CRITICAL**: Describe what to verify, not implementation to check

### Helpful Tips
Practical guidance without revealing implementations:
- **UPDATE**: "Consider how the RAG app discovers ChromaDB using the service name 'chromadb' on the internal Docker network"
- **UPDATE**: "Think about the startup order: ChromaDB → data initialization → RAG app, and how retry logic helps handle timing"
- **UPDATE**: "Explore how to verify ChromaDB is ready by checking logs or testing the heartbeat endpoint"
- "Review how Docker manages logs for debugging the initialization process"
- **UPDATE**: "Consider how ChromaDB persists data at /data using the chroma_data named volume"
- **UPDATE**: "Think about what happens if initialization runs multiple times - how can the script be idempotent?"
- **UPDATE**: "Explore how port mapping works: ChromaDB listens on 8000 inside the container but is exposed as 8001 on the host"
- "Review how to configure application settings using environment variables"
- "Consider how to verify that collections are created and populated in ChromaDB"
- "Consider how retrieval relevance can be improved through different search strategies"
- "Think about evaluating if retrieved context is actually being used in responses"
- "Explore different approaches to combining retrieved information with generation"
- **UPDATE**: "Review how ChromaDB's default embedding function works and whether it's sufficient for your use case"
- "Consider handling cases where no relevant information is found in ChromaDB"
- "Think about how to measure and improve the quality of retrieved results"

Use action words: "Consider", "Think about", "Review", "Explore"
**CRITICAL**: Guide discovery, never provide solutions

### NOT TO INCLUDE:
- Manual deployment instructions (automated via run.sh)
- Step-by-step setup guides
- Specific Docker commands showing solutions
- Code snippets or configuration examples revealing implementations
- Specific implementation details

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name (within 50 characters), e.g., 'Improve Medical RAG System Retrieval Quality'",
   "question": "Brief description with scenario's RAG problem, architecture (mention ChromaDB with default embeddings, port mappings), current state, and required work. Emphasize that ChromaDB is deployed through Docker at /data with persistent volume, pre-populated with data using default embeddings, and that the candidate must improve robustness and/or retrieval quality.",
   "code_files": {{
      "README.md": "Complete README with scenario-specific content, mermaid architecture diagram showing ChromaDB (port 8001), init service, RAG app (port 8000), and persistent volume at /data",
      ".gitignore": "Comprehensive Python/Docker exclusions including chroma_data",
      ".dockerignore": "Basic file - candidate improves",
      "requirements.txt": "**UPDATE**: Minimal dependencies - chromadb>=0.5.0, fastapi>=0.104.0, uvicorn>=0.24.0, pydantic>=2.0.0, requests, python-dotenv. NO heavy ML libraries.",
      "docker-compose.yml": "**UPDATE**: Three services with simplified depends_on (no health conditions): chromadb (8001:8000, /data volume, unless-stopped), chroma-init (restart: no, simple depends_on chromadb), rag-app (8000:8000, unless-stopped, simple depends_on chromadb and chroma-init). Fully working as generated.",
      "Dockerfile": "**UPDATE**: Optimized layer caching - COPY requirements.txt, RUN pip install, then COPY src/. Clean Dockerfile, builds and runs successfully.",
      "Dockerfile.init": "**UPDATE**: Optimized layer caching - minimal dependencies (chromadb, requests, python-dotenv). No heavy ML libraries.",
      "run.sh": "**UPDATE**: Simplified waiting - check container status, wait for chroma-init exit, wait for rag-app running, curl health check with retries, test query. Fully working as generated.",
      "kill.sh": "Complete cleanup script including ChromaDB volume, idempotent",
      ".env.example": "**UPDATE**: Example with optional API key placeholders (OPENAI_API_KEY, ANTHROPIC_API_KEY) - not required for baseline",
      "src/main.py": "**UPDATE**: FastAPI entry point with /query and /health endpoints, includes retry logic to wait for ChromaDB and data availability at startup",
      "src/rag_pipeline.py": "**UPDATE**: RAG pipeline using ChromaDB's default embedding function (baseline functional, may need enhancement)",
      "src/vector_store.py": "**UPDATE**: ChromaDB client wrapper connecting at chromadb:8000 using service name (functional, may need enhancement)",
      "src/config.py": "Configuration management for ChromaDB connection (CHROMA_HOST=chromadb, CHROMA_PORT=8000)",
      "src/models.py": "Pydantic models for API requests/responses",
      "init-scripts/load_data.py": "**UPDATE**: Python script with retry logic to wait for ChromaDB readiness, connects at chromadb:8000, creates collection using default embedding, loads from sample_data.json, idempotent",
      "init-scripts/sample_data.json": "Domain-specific sample data (20-50+ documents) with id, text, metadata"
   }},
  "outcomes": "Bullet-point list in simple, non-technical language understandable by HR. Must include: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.' and 'Deploy ChromaDB vector database through Docker with persistent storage and pre-populated data ready for querying.'",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level problem in a business context, (2) the specific goal, and (3) the expected outcome emphasizing maintainability and scalability.",
   "pre_requisites": "Docker, Docker Compose, basic Python, basic RAG understanding, ChromaDB concepts, vector database knowledge, Git, curl, API concepts",
   "answer": "High-level solution describing approach. Focus on RAG concepts, ChromaDB deployment with default embeddings, data initialization flow, and persistent volume at /data. Emphasize the three-service architecture with simplified startup order and retry logic: ChromaDB → init → RAG app. Mention improvements in retrieval strategies, deployment robustness, or observability as relevant to scenario. Note the use of lightweight default embeddings and optimized Docker layer caching.",
   "hints": "Single line suggesting focus area(s). Must NOT reveal implementations. Can mention ChromaDB containerization with persistent volume, service networking, initialization retry logic, and RAG retrieval quality improvements using default embeddings.",
   "definitions": {{
     "terminology_1": "Vector Embedding - Numerical representation of text that captures semantic meaning, stored in ChromaDB using its default embedding function",
     "terminology_2": "Retrieval-Augmented Generation (RAG) - AI technique combining information retrieval from a knowledge base with text generation",
     "terminology_3": "ChromaDB - Open-source vector database designed for storing and querying embeddings with built-in default embedding function",
     "terminology_4": "Docker Service Networking - Container-to-container communication using service names on the internal Docker network",
     "terminology_5": "Initialization Service - One-time container that populates data before the main application starts, then exits",
     "terminology_6": "Layer Caching - Docker optimization that reuses unchanged layers (like dependencies) to speed up builds",
     "terminology_7": "Persistent Volume - Docker storage mechanism that retains data across container restarts and recreations"
   }}
}}

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, within 50 characters
3. **code_files** must include README.md, .gitignore, requirements.txt, Docker files, run.sh, kill.sh, and all source files
4. **README.md** must follow the structure above with Task Overview, Objectives, Application Access, How to Verify, Helpful Tips
5. **RAG system** must be COMPLETE and deployable — candidates improve it, not fix broken deployment
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant RAG/Docker terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **NO solutions revealed** in starter code — system must work but have room for improvement
10. **All paths** must reference /root/task as the base directory
"""
PROMPT_REGISTRY = {
    "Retrieval_Augmented_Generation (BASIC)": [
        PROMPT_RAG_CONTEXT_BASIC,
        PROMPT_RAG_INPUT_AND_ASK_BASIC,
        PROMPT_RAG_BASIC,
    ]
}
