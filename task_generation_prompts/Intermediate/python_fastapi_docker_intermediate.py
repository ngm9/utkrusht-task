PROMPT_PYTHON_DOCKER_OPTIMIZATION_INSTRUCTIONS_INTER = """
## GOAL
As a technical architect super experienced in Docker containerization and deployment, you are given a list of real world scenarios and proficiency levels for Docker.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a Python FastAPI application that needs to be optimized and properly containerized using Docker with focus on Docker configuration, optimization, and deployment practices that require intermediate-level Docker skills.

**CRITICAL DEPLOYMENT SETUP REQUIREMENT:**
The candidate's primary responsibility is to OPTIMIZE and REFACTOR an existing Docker setup that is ALREADY DEPLOYED and FUNCTIONAL but has performance issues, inefficiencies, or suboptimal configurations. The task provides a fully working deployment with deliberate inefficiencies that the candidate must identify and fix.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY DEPLOYED Python FastAPI application with a WORKING but SUBOPTIMAL Docker configuration. The application includes:
- Complete REST API endpoints with business logic already implemented and functional
- FULLY FUNCTIONAL Docker setup (Dockerfile and docker-compose.yml) that is DEPLOYED and RUNNING
- **CRITICAL**: The Docker setup works but has deliberate inefficiencies such as:
  - Slow container startup times (30+ seconds)
  - Large image sizes (500MB+ when could be <150MB)
  - Inefficient layer caching causing slow rebuilds
  - Missing or improper health checks causing delayed readiness
  - Resource limits not configured leading to potential memory/CPU issues
  - Running as root user (security concern)
  - Inefficient dependency installation
  - Poor network configuration
  - Missing volume optimization
  - Suboptimal base image choices
- All necessary Python dependencies and code that requires minimal to no changes
- Complete Python models, services, and routers that are already optimized
- Pre-configured application settings with correct configurations
- The application is ACCESSIBLE and RESPONDING but with performance issues
- The focus is on Docker OPTIMIZATION and REFACTORING, not Python code development

The candidate's primary responsibility is to focus on Docker optimization and refactoring (90%) with minimal Python configuration changes (10%) only as needed to enhance containerization. The task completion involves identifying inefficiencies, implementing Docker best practices, optimizing images, improving build times, enhancing security, and applying optimization techniques at an intermediate level (3-5 years experience in Docker).

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the intermediate-level Docker optimization and refactoring scenario
- Task must provide a FULLY DEPLOYED and FUNCTIONAL Python FastAPI application with WORKING but INEFFICIENT Docker setup
- **CRITICAL DEPLOYMENT PARADIGM**: The Docker setup must be ALREADY DEPLOYED and RUNNING when candidate starts, but with measurable performance/efficiency issues
- **CRITICAL**: The Python application should be FULLY functional and well-optimized, requiring only minimal configuration changes for Docker optimization
- **CRITICAL**: The primary focus (90%) is on Docker OPTIMIZATION: refactoring Dockerfile, optimizing docker-compose.yml, implementing multi-stage builds, reducing image size, optimizing layer caching, improving startup times, configuring resources properly, enhancing networking, optimizing volumes, and improving deployment efficiency
- **CRITICAL**: Python changes (10%) should be minimal and only for Docker optimization (e.g., adjusting ASGI server configurations, optimizing health check endpoints, improving logging for containerized environment)
- **CRITICAL BASELINE SETUP**: The provided Docker configuration must be:
  - Fully deployable and functional (passes basic smoke tests)
  - Deliberately inefficient but not broken
  - Measurably suboptimal (slow builds, large images, slow startups, resource waste)
  - Provides clear baseline metrics for candidates to improve upon
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working Python FastAPI application with FUNCTIONAL but SUBOPTIMAL Docker setup that requires intermediate-level Docker expertise to optimize and refactor
- **PROVIDE WORKING BUT INEFFICIENT DOCKER SETUP**: Include functional Dockerfile and docker-compose.yml that work but need significant optimization (multi-stage builds, image size reduction, layer optimization, resource management, security hardening, build time improvements)
- The question should be a real-world business scenario requiring intermediate-level Docker optimization and refactoring skills, NOT Python application development
- The complexity of the Docker task must align with intermediate proficiency level (3-5 years Docker experience) requiring optimization techniques:

- The question must NOT include hints about specific Docker optimizations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest Docker best practices for intermediate-level optimization
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively optimize, refactor, and improve Docker containerization and deployment at an intermediate level
- Tasks should involve multi-layered Docker optimization challenges that require understanding of image optimization, build efficiency, networking, security, and deployment strategies
- Candidates will be encouraged to use AI to help analyze inefficiencies but not replace their own Docker optimization and architecture skills

## Code Generation Instructions:
Based on the real-world scenarios provided, create a Docker-focused optimization task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate Docker proficiency (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced Docker optimization skills
- Tests practical intermediate-level Docker optimization, refactoring, and deployment efficiency skills
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- **CRITICAL**: The Python FastAPI application should be COMPLETE, FUNCTIONAL, and WELL-OPTIMIZED with WORKING but INEFFICIENT Docker setup requiring significant optimization work
- All FastAPI endpoints should be implemented, working, and optimized
- The application should have FUNCTIONAL Docker configuration that is DEPLOYED but needs optimization
- **CRITICAL**: The task focuses on Docker optimization and refactoring (90%), NOT Python application development (10%)
- **CRITICAL BASELINE**: Provide measurable baseline metrics (image size, build time, startup time) that candidates can improve

## Infrastructure Requirements:
- MUST include a complete, fully functional, and optimized REST API using Python FastAPI
- MUST include WORKING but INEFFICIENT Dockerfile requiring significant optimization
- MUST include WORKING but SUBOPTIMAL docker-compose.yml requiring refactoring and optimization
- A run.sh which has the end-to-end responsibility of deploying the infrastructure and validating deployment
- **CRITICAL DEPLOYMENT STATE**: The infrastructure must be ALREADY DEPLOYED and ACCESSIBLE when candidate starts, with clear performance/efficiency issues to optimize

### Docker-compose Instructions:
  - Python FastAPI service with FUNCTIONAL but SUBOPTIMAL Docker configuration
  - Additional services if needed (database, cache) with working but inefficient orchestration
  - Volume mounts that work but could be optimized
  - Network configuration that functions but needs optimization
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - Present but SUBOPTIMAL configurations: inefficient resource limits, missing/poor health checks, suboptimal depends_on, basic restart policies, inefficient networking
  - **CRITICAL**: Docker-compose should be FUNCTIONAL and DEPLOYED but require significant optimization work
  - **MEASURABLE INEFFICIENCIES**: Include configurations that cause slow startups, resource waste, or poor orchestration

### Dockerfile instructions:
- MUST be FUNCTIONAL and DEPLOYED but DELIBERATELY INEFFICIENT, requiring the candidate to optimize:
  - Single-stage build (candidate should convert to multi-stage)
  - Using bloated base image like python:3.11 instead of python:3.11-slim or alpine (candidate should optimize)
  - Inefficient layer ordering causing poor cache utilization (candidate should optimize)
  - Basic .dockerignore or missing (candidate should optimize)
  - Running as root user (candidate should fix for security)
  - Missing or inefficient health check implementation (candidate should optimize)
  - Inefficient dependency installation (pip install without caching, reinstalling on every build)
  - Installing unnecessary system packages (candidate should minimize)
  - Poor build caching strategy causing slow rebuilds (candidate should optimize)
  - Copying entire application context instead of selective copying (candidate should optimize)
  - Not using pip cache mounts or layer caching for dependencies
- **CRITICAL: Provide WORKING but INEFFICIENT Docker setup with measurable optimization opportunities (build time, image size, startup time)**
- **BASELINE METRICS**: Initial setup should produce:
  - Image size: 500MB+ (target: <150MB)
  - Build time: 2-3 minutes (target: <30 seconds with cache)
  - Startup time: 20-30 seconds (target: <5 seconds)

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d` and ensures deployment is complete
  + DEPLOYMENT VALIDATION: Confirms that application is FULLY DEPLOYED and ACCESSIBLE
  + WAIT MECHANISM: Implements proper health check to wait for services to be fully ready
  + BASELINE METRICS: Captures and displays initial performance metrics (build time, image size, startup time)
  + VALIDATION: Validates that Python application is responding correctly with sample API calls
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + PERFORMANCE LOGGING: Logs performance indicators that candidates can measure improvements against
  + ERROR HANDLING: Includes proper error handling for failed container starts
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  + BUILD PROCESS: Handles Docker image building and container startup with timing measurements
  + **CRITICAL**: Must ensure application is ACCESSIBLE and RUNNING before candidate starts optimization

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile
- Instructions:
  1. Stop and remove all containers created by docker-compose
  2. Remove all associated Docker volumes
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes
  6. Delete the entire `/root/task/` folder where all the files were created
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'task|python|fastapi') || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python files (`__pycache__/`, `*.pyc`, `.pytest_cache/`) are removed
  - Remove all volume mount directories
  - Remove Python virtual environments if any

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (FUNCTIONAL but SUBOPTIMAL service configuration requiring optimization)
  - Dockerfile (FUNCTIONAL but INEFFICIENT - requires significant optimization work)
  - .dockerignore (Basic or missing - candidate should optimize)
  - run.sh (Script to deploy, validate, and measure baseline performance)
  - kill.sh (Complete cleanup script)
  - requirements.txt (Python dependencies with all necessary packages)
  - .gitignore (Python, Docker, IDE exclusions)
  - All Python FastAPI code files following standard project structure with optimized implementations
  - **CRITICAL**: Include proper Python package structure with all necessary files (already optimized)

## Code file requirements:
- Multiple files will be generated following FastAPI project structure
- Python code should follow best practices and be well-optimized (no Python optimization needed)
- **CRITICAL**: The Python application files MUST be complete, fully functional, and optimized
- Docker configuration should be FUNCTIONAL but INEFFICIENT, requiring significant optimization
- **PRIMARY FOCUS**: 90% of candidate's work should be on Docker optimization, refactoring, and performance improvement
- DO NOT include any 'TODO' or placeholder comments in Python code
- DO include comments in Docker files indicating areas with known inefficiencies or optimization opportunities
- The application should be immediately accessible and responding, but with measurable performance issues
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **BASELINE DOCUMENTATION**: Include initial metrics in comments for candidates to improve upon

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Python FastAPI and Docker development that includes:
- Python cache directories (__pycache__/, *.pyc, *.pyo, *.pyd)
- Virtual environments (venv/, env/, .venv/)
- IDE files (.idea/, .vscode/, *.swp, .python-version)
- Testing artifacts (.pytest_cache/, .coverage, htmlcov/)
- Log files (*.log, logs/)
- Docker volumes and data directories
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for Python/FastAPI/Docker development

## .dockerignore INSTRUCTIONS:
Should be basic or missing - candidate needs to optimize this as part of Docker optimization to reduce build context size

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Current State & Baseline Metrics
   - Helpful Tips
   - Application Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level Docker optimization and refactoring
- Task Overview section MUST contain the exact business scenario and Docker optimization requirements
- **CRITICAL NEW SECTION**: "Current State & Baseline Metrics" must document the DEPLOYED state and measurable inefficiencies
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Docker optimization scenario being generated
- Use concrete business context explaining why Docker optimization is critical for production deployment
- **CRITICAL**: Emphasize Docker optimization, refactoring, and performance improvement throughout README
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover optimization opportunities

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the Docker optimization requirements. The Python application is already functional, deployed, and accessible; the focus is on optimizing the Docker setup for production efficiency, performance, and cost reduction.
NEVER generate empty content - always provide substantial business context that explains why Docker optimization is critical (e.g., reducing cloud costs, improving deployment speed, enhancing security, reducing resource consumption).

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how Docker images are built in layers and how staging can reduce final image size
  - Mention investigating what actually needs to be in the final runtime image versus build-time dependencies
  - Hint at examining different Python base image options and their size trade-offs
  - Recommend analyzing what gets copied into the image and whether all of it is necessary
  - Suggest considering how Python dependencies are installed and cached during builds
  - Point toward thinking about who the container runs as and security implications
  - Hint at exploring how Docker caches layers and what affects cache invalidation
  - Recommend measuring before and after metrics to quantify improvements
  - Suggest thinking about resource boundaries for production deployments
  - Mention considering container lifecycle signals and readiness verification
  - Use bullet points formatted as tips, starting with action words like "Consider", "Investigate", "Explore", "Analyze"
  - **CRITICAL**: Tips should guide discovery of inefficiencies, not provide direct solutions

### Application Access
  - Provide the application access details with deployed status: "The application is currently running at http://<DROPLET_IP>:8000"
  - List available API endpoints (e.g., GET /health, GET /docs, GET /api/v1/...)
  - Mention FastAPI automatic documentation: "Interactive API docs available at http://<DROPLET_IP>:8000/docs"

### Objectives
Define clear optimization goals that guide candidates toward solutions without explicitly stating implementations:
  - Frame objectives around measurable improvements rather than specific technical implementations
  - Focus on what the optimized system should achieve, not how to achieve it
  - Examples of proper framing:
    * "Reduce Docker image from the current baseline to minimize storage costs and improve deployment speed"
    * "Improve build times for cached builds to accelerate development and CI/CD pipelines"
    * "Reduce container startup time to enable faster scaling and deployments"
    * "Minimize resource consumption while maintaining application performance and reduce the memory and CPU usage"
    * "Implement security hardening to reduce attack surface and follow production best practices"
    * "Optimize layer caching to ensure that code changes don't require full dependency reinstallation"
    * "Improve build context efficiency to speed up image builds"
    * "focus on improving the cache and layer caching to speed up the build process"
    * "Configure appropriate resource limits to prevent runaway resource consumption"
  - Objectives should be measurable with specific improvements or target numbers
  - Should guide candidates to think about: efficiency, performance, security, cost reduction, deployment speed
  - **CRITICAL**: Objectives describe measurable outcomes and targets, never the specific implementation approach
  - Avoid phrases like "implement multi-stage builds" or "use Alpine base image" - instead describe the desired improvement

### How to Verify
Provide verification approaches that help candidates validate their optimizations with measurable results:
  - Frame verification in terms of measurable metrics and observable improvements
  - Examples of proper framing:
    * "Compare the optimized image size against the baseline using `docker images` - target reduction of the image size"
    * "Measure build time improvements with `time docker-compose build` for both clean and cached builds"
    * "Test container startup time by timing from container start to first successful health check"
    * "Monitor resource consumption with `docker stats` and compare against baseline metrics"
    * "Verify build cache efficiency by making a small code change and measuring rebuild time"
    * "Inspect the running container to confirm security improvements are applied"
    * "Test application responsiveness and ensure optimization doesn't impact functionality"
    * "Validate that all API endpoints continue to work correctly after optimization"
  - Suggest comparing before/after metrics to quantify improvements
  - Mention Docker commands for measurement without specifying exact implementation details
  - Guide candidates to test that optimizations don't break functionality
   Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery, not provide direct solutions or specific commands

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (application is already deployed)
  - Step-by-step setup instructions (deployment is automated and complete)
  - Instructions to run the run.sh file (deployment is already done)
  - Specific Docker optimization solutions (e.g., "use multi-stage builds", "switch to Alpine image")
  - Direct implementation hints (e.g., "add BuildKit cache mounts", "copy requirements.txt separately")
  - Python optimization instructions (Python code is already optimized)
  - Explicit technology choices (let candidates decide the optimization approach)
  - Code snippets or configuration examples
  - Phrases like "you should implement", "make sure to add", "configure the following"
  - Deployment troubleshooting (application is working, focus is on optimization)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words) - must focus on Docker optimization and refactoring of deployed application should be short and crisp tot eh point as per the task scenario",
   "question": "A short description of the intermediate-level Docker optimization task scenario - what aspects of the DEPLOYED Docker setup need to be optimized and refactored? Focus on optimization requirements, NOT Python changes. Mention that application is currently deployed and functional but inefficient.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Current State & Baseline Metrics, Objectives for Docker optimization, and How to Verify improvements with measurable targets",
      ".gitignore": "Proper Python, Docker, and IDE exclusions",
      ".dockerignore": "Basic or missing - candidate optimizes this",
      "requirements.txt": "Python dependencies with all necessary packages",
      "docker-compose.yml": "FUNCTIONAL but SUBOPTIMAL Docker services configuration requiring optimization",
      "Dockerfile": "FUNCTIONAL but INEFFICIENT Dockerfile requiring significant optimization work",
      "run.sh": "Complete deployment script that measures and displays baseline performance metrics",
      "kill.sh": "Complete cleanup script to remove all resources",
      "app/main.py": "FastAPI main application file (already optimized)",
      "app/api/routes.py": "API route definitions (already functional and optimized)",
      "app/services/business_logic.py": "Business logic service layer (already optimized)",
      "app/models/schemas.py": "Pydantic models for request/response (already configured)",
      "app/core/config.py": "Application configuration (already optimized)",
      "app/core/health.py": "Health check endpoint (already implemented)",
      "Additional Python files as needed following FastAPI structure (all optimized)"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable Docker optimization improvements: reduced image size, faster build times, quicker startup, better resource efficiency, enhanced security. Use simple english with specific improvements.",
  "pre_requisites": "Bullet-point list of tools and environment setup required. Mention Docker, Docker Compose, basic understanding of Python FastAPI (no Python expertise needed), Docker performance analysis tools (docker stats, docker history), time measurement tools. Focus on Docker optimization requirements.",
  "answer": "High-level solution approach focusing primarily on Docker optimization strategies: converting to multi-stage builds for size reduction, selecting appropriate base images (Alpine/slim), optimizing layer caching for faster rebuilds, implementing efficient dependency installation with caching, configuring proper resource limits, adding security hardening (non-root user), optimizing build context with .dockerignore, implementing proper health checks for faster readiness. Minimal Python configuration changes mentioned. Include expected performance improvements with specific numbers.",
  "task_overview": ["Array of strings where each string is a 3-4bullet point similar as the task scenario overview from the README.md file. Each point should be concise and what task is all about giving out the overview of that"],
  "hints": "A single line hint suggesting that candidates should analyze the current Docker setup to identify inefficiencies and focus on measurable optimization opportunities (image size, build time, startup time, resource usage, security). Must NOT give away specific Docker implementations but gently nudge toward measuring and improving performance metrics.",
  "definitions": {{
    "terminology_1": "definition_1 ",
    "terminology_2": "definition_2 "
    ...
    }}
}}
"""

PROMPT_REGISTRY = {
    "Docker (INTERMEDIATE), Python - FastAPI (INTERMEDIATE)": [
        PROMPT_PYTHON_DOCKER_OPTIMIZATION_INSTRUCTIONS_INTER,
    ]
}
