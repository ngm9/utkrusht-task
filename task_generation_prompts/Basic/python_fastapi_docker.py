PROMPT_FASTAPI_DOCKER_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI and Docker assessment task.

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
2. What will the task look like? (Describe the type of Docker containerization or optimization required, the expected deliverables, and how it aligns with BASIC Python FastAPI and Docker proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FASTAPI_DOCKER_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role expectations,
especially focusing on how Docker may be used in basic FastAPI-based systems — such as for containerization, environment consistency, or lightweight deployment?
"""


PROMPT_FASTAPI_DOCKER_OPTIMIZATION_INSTRUCTIONS_BASIC = """
## GOAL
As a technical architect experienced in Docker containerization, you are given real-world scenarios and proficiency levels for Docker. Your job is to generate a deployment-ready task for basic-level Docker practitioners (1-2 years experience) where a candidate receives a functional FastAPI application that needs proper containerization using Docker fundamentals.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios (input_scenarios) to frame the task. The business context, domain, and technical requirements should directly align with the given scenario while focusing primarily on Docker containerization (85%) with minimal Python/FastAPI configuration changes (15%).

The candidate's primary responsibility is to understand, configure, and apply basic Docker concepts. Be careful not to give away solutions or hint at implementations in task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a complete, working FastAPI REST API application with basic Docker setup requiring fundamental Docker knowledge to properly containerize. The application includes:
- Fully functional REST API endpoints with all business logic implemented
- Complete Python code requiring NO modifications
- All dependencies properly configured in requirements.txt
- Pre-configured configuration files ready for containerization
- Basic Docker files that need proper configuration and understanding

**PRIMARY FOCUS**: The candidate works on Docker containerization (85%) with minimal configuration adjustments (15%) only for Docker compatibility. The task demonstrates understanding of Docker basics, container lifecycle, basic optimization, and deployment practices suitable for 1-2 years Docker experience.

## CRITICAL: DEPLOYMENT WITH INTENTIONAL ISSUES

## Initial Deployment State (MANDATORY):
The provided Docker setup MUST be functional BUT suboptimal with intentional issues that demonstrate need for basic optimization:

### Required Issues to Include (Pick 3-4):
1. **Slow Startup Time**:
   - Using heavyweight base image (python:3.11 instead of python:3.11-slim)
   - Installing unnecessary system packages
   - Not using dependency caching layers properly
   - Example: Dockerfile copies everything before pip install, breaking cache

2. **Inefficient Build Process**:
   - Single-stage build copying unnecessary files
   - No .dockerignore file (or incomplete one)
   - Copying entire project including .git, __pycache__, tests
   - Large image size (800MB+ when could be 200MB)

3. **Poor Container Response**:
   - Missing or incorrect health checks in docker-compose
   - Using development server (uvicorn without workers) instead of production configuration
   - No gunicorn/uvicorn worker optimization
   - Container takes 30+ seconds to be "ready"

4. **Resource Issues**:
   - No resource limits defined in docker-compose
   - Application not configured for container environment
   - Missing proper logging configuration (logs not visible via docker logs)
   - No graceful shutdown handling

5. **Networking Problems**:
   - Database connection uses localhost instead of service name
   - Hardcoded ports causing conflicts
   - No proper wait mechanism for dependent services
   - Services start before dependencies are ready

6. **Security/Best Practice Issues**:
   - Running as root user in container
   - Exposing unnecessary ports
   - Including dev dependencies in production image
   - Credentials in docker-compose instead of environment variables

### Deployment Behavior:
- **MUST BE FUNCTIONAL**: Application eventually works after deployment
- **MUST BE SLOW**: Takes 30-60 seconds to become responsive
- **MUST BE OBVIOUS**: Issues should be noticeable through:
  - Slow `docker-compose up` execution
  - Large image size visible in `docker images`
  - Delayed API responses initially
  - Visible warnings/errors in logs that don't crash the app
  - Excessive memory usage in `docker stats`

### What Candidate MUST Fix:
- Optimize Dockerfile for faster builds and smaller images
- Implement proper multi-stage builds
- Create/improve .dockerignore
- Configure production-ready WSGI server setup
- Add proper health checks
- Fix service networking and dependencies
- Implement resource limits
- Improve container security posture
- Ensure proper logging visibility

**CRITICAL**: The initial deployment should work but make the candidate think "this works, but it's clearly not production-ready" - creating obvious optimization opportunities without breaking functionality.

## INSTRUCTIONS

### Nature of the Task
- **MANDATORY**: The task MUST be derived from and aligned with the provided input_scenarios. Use the scenario's business context, domain, technical stack, and requirements as the foundation
- **CRITICAL**: While the scenario provides the business context, ensure the PRIMARY focus (85%) remains on Docker containerization challenges, NOT FastAPI application development
- Task name MUST be within 50 words describing a clear basic-level Docker containerization scenario that reflects the input scenario's context
- Provide a FULLY WORKING FastAPI application that implements the business logic from the input scenario, requiring only basic Docker optimization
- **FASTAPI APPLICATION**: Complete and functional implementation of the scenario's requirements - requires ZERO Python code changes
- **PRIMARY FOCUS (85%)**: Basic Docker concepts - understanding Dockerfile structure, using appropriate base images, basic layer optimization, container commands, port mapping, basic docker-compose orchestration, fixing intentional deployment issues
- **MINIMAL CONFIGURATION (15%)**: Only environment-specific values in configuration files (database URLs, ports, service names) - minimal code changes but that should not affect the deployment
- **SCENARIO ADHERENCE**: The business problem, domain entities, API endpoints, and data flow should directly reflect the input scenario provided
- **DOCKER EMPHASIS**: Even though following the scenario, ensure the task complexity and deliverables focus on Docker containerization skills appropriate for 1-2 years experience
- **INTENTIONAL ISSUES**: Include 3-4 obvious but non-breaking issues in the Docker setup that candidate must identify and fix
- Generate complete FastAPI application implementing the scenario's requirements with suboptimal Docker setup requiring fundamental Docker knowledge to optimize
- Task complexity aligns with basic proficiency (1-2 years Docker experience):

  **Docker Focus Areas (85% of task):**
  - Understanding and optimizing Python base images (slim vs full vs alpine)
  - Proper WORKDIR, COPY, and layer caching strategies
  - Multi-stage builds for smaller images
  - Basic port exposure (EXPOSE directive)
  - Creating comprehensive .dockerignore
  - Basic docker-compose service definitions with health checks
  - Understanding container logs and basic debugging
  - Basic volume mounting for data persistence
  - Environment variable configuration
  - Understanding container networking basics
  - Basic resource limits and restart policies
  - Optimizing uvicorn/gunicorn configuration for containers
  - Understanding build vs runtime dependencies
  - Fixing slow startup and response times
  - Reducing image size through proper layering
  
  **Minimal Configuration (15% of task):**
  - Updating connection strings for containerized services
  - Ensuring correct port configuration matching the scenario's requirements
  - very minimal code refactoring or optimization needed but that should not affect the deployment

- Questions must NOT hint at solutions - hints provided separately
- Follow latest Docker best practices for basic containerization
- Diagrams in mermaid format, properly indented in code blocks

## Task Scenario Integration Requirements:
- **BUSINESS CONTEXT**: Extract and use the real-world business problem from input_scenarios
- **DOMAIN ALIGNMENT**: Implement models, services, and APIs that match the scenario's domain
- **TECHNICAL REQUIREMENTS**: Incorporate any specific technologies mentioned in the scenario (database type, external services, caching, etc.)
- **DOCKER CHALLENGE**: Frame the Docker containerization challenge around the scenario's deployment needs (e.g., "The API service works but takes too long to start and uses excessive resources", "The microservice is containerized but not production-ready")
- **CONSISTENCY**: Ensure README Task Overview, question description, and code implementation all reflect the same scenario
- **VARIETY**: Pick different scenarios from the input_scenarios list to ensure diverse task generation across multiple invocations

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates can use Google, Stack Overflow, Docker documentation, AI tools, LLMs
- Tasks assess ability to understand and apply basic Docker containerization concepts
- Challenges test fundamental Docker knowledge: image building, container running, basic orchestration, optimization
- AI helps with syntax but doesn't replace fundamental Docker understanding

## Code Generation Instructions:
Create Docker-focused tasks that:
- **MUST draw directly from input_scenarios** for business context, domain, and technical setup
- Match basic Docker proficiency (1-2 years experience) considering AI assistance
- Test practical basic Docker skills while implementing the scenario's business logic
- Time constraint: Completable within {minutes_range} minutes
- **Use varied scenarios** from the input_scenarios list to ensure diversity
- **CRITICAL**: FastAPI application is COMPLETE, FUNCTIONAL, but very minimal code refactoring or optimization needed but that should not affect the deployment
- All FastAPI endpoints implementing the scenario's API requirements are working
- Basic Docker configuration with intentional issues requiring fundamental Docker knowledge to fix
- **TASK FOCUS**: Docker containerization optimization (85%), NOT Python development (15% config only)
- **SCENARIO AUTHENTICITY**: The application should solve the real-world problem described in the input scenario
- **DEPLOYMENT ISSUES**: Include 3-4 obvious suboptimal configurations that work but need optimization

## Infrastructure Requirements:
**DEPLOYMENT ROBUSTNESS - CRITICAL REQUIREMENTS:**

1. **Python Dependency Configuration:**
   - requirements.txt MUST include ALL required packages with compatible versions
   - MUST include FastAPI, uvicorn (or gunicorn with uvicorn workers), pydantic
   - Dependencies MUST match what Docker build process expects AND what the scenario requires (e.g., SQLAlchemy for database scenarios, redis-py for caching scenarios, httpx for external API calls)
   - Include specific versions to ensure reproducibility (e.g., fastapi==0.104.1)
   - All dependency versions MUST be compatible and tested
   - NO dependency conflicts or missing packages
   - For intentional issues: May include dev dependencies (pytest, black, etc.) in main requirements.txt

2. **Dockerfile Build Strategy (WITH INTENTIONAL ISSUES):**
   - **INITIAL STATE**: Single-stage build with heavyweight image (python:3.11)
   - Copies entire project before pip install (breaks caching)
   - Installs both dev and prod dependencies
   - No user creation (runs as root)
   - Basic but functional - works but slow (60+ second build)
   - **WHAT CANDIDATE SHOULD IMPLEMENT**:
     - Multi-stage build (builder + runtime)
     - Use python:3.11-slim for smaller size
     - Proper layer ordering (copy requirements first, then code)
     - Separate dev and prod dependencies
     - Create non-root user
   - Structure should be deployable but obviously suboptimal

3. **Docker-Compose Configuration (WITH INTENTIONAL ISSUES):**
   - MUST NOT include version field (deprecated in Compose V2)
   - **INITIAL STATE**: Basic configuration with issues:
     - Missing health checks or incorrect health check intervals
     - No resource limits defined
     - No restart policies
     - May use localhost instead of service names in some places
     - Development server configuration (single uvicorn worker)
   - Service definitions should align with scenario requirements
   - Database service (if needed) with basic setup
   - **WHAT CANDIDATE SHOULD FIX**:
     - Add proper health checks with appropriate intervals
     - Define memory and CPU limits
     - Set restart: unless-stopped
     - Fix service name references
     - Configure production server setup (multiple workers)
   - Configuration must work but have obvious room for improvement

4. **Application Configuration Consistency:**
   - Configuration file (config.py or .env.example) with values ready for containers
   - Database URLs MUST match docker-compose service names
   - Port numbers MUST be consistent across:
     - Application configuration (app startup port)
     - Dockerfile EXPOSE directive
     - docker-compose ports mapping
   - Database credentials MUST match between config and docker-compose
   - Configuration should support the scenario's technical requirements
   - May have some hardcoded values that should be environment variables (intentional issue)

5. **File System and Permissions:**
   - All paths in scripts reference /root/task
   - Proper WORKDIR usage in Dockerfile
   - Volume mount paths properly configured
   - Initial .dockerignore may be missing or incomplete (intentional)

### Run.sh Requirements:
- **PRIMARY**: Executes `docker-compose up -d --build`
- **CRITICAL** THIS should eb there to runt he docker and docker compose 
- Implements robust waiting mechanism using health checks or custom verification
- Validates application responds (curl to health endpoint with retries)
- Monitors container status with proper error messages
- Error handling for failed builds or container crashes
- All paths reference /root/task
- Validates both build AND runtime success
- May show warnings about slow startup (expected with intentional issues)

### Kill.sh Requirements:
- Stop and remove containers: `docker-compose down --volumes --remove-orphans`
- Remove project-specific images: `docker rmi $(docker images -q 'task*') 2>/dev/null || true`
- System cleanup: `docker system prune -a --volumes -f`
- Remove task directory: `rm -rf /root/task`
- Idempotent - safe to run multiple times
- Clear logging at each step
- Success message after cleanup

### Dockerfile Instructions (WITH INTENTIONAL ISSUES):
- **INITIAL STATE**: Basic single-stage Dockerfile provided
- Uses heavyweight base image (python:3.11)
- Simple but inefficient layer ordering
- Copies everything at once (no .dockerignore or incomplete)
- Runs as root user
- Uses basic CMD with single uvicorn worker
- **INTENTIONAL ISSUES TO INCLUDE**:
  - No multi-stage build
  - Poor caching (copies code before pip install)
  - Includes unnecessary files
  - No security hardening
  - Development server configuration
- Should work correctly but be obviously suboptimal
- **CRITICAL**: Must build and run successfully despite issues

### Docker-Compose Instructions (WITH INTENTIONAL ISSUES):
- **INITIAL STATE**: Basic service definitions provided
- MUST NOT include version field
- NO environment variables or .env references initially - use hardcoded values
- Include services required by the scenario (database, cache, message queue, etc.)
- **INTENTIONAL ISSUES TO INCLUDE**:
  - Missing or inadequate health checks
  - No resource limits
  - No restart policies or wrong restart policy
  - Development server configuration (single worker)
  - Possibly incorrect depends_on without proper wait
- Service names MUST match application configuration references
- Database service (if needed) with basic but functional setup
- **CRITICAL**: Configuration must be deployment-ready but with obvious optimization opportunities

## Code File Requirements:
- Standard FastAPI project structure
- Python code fully optimized and functional, implementing the scenario's business requirements
- **CRITICAL**: Python files are COMPLETE - NO changes needed
- Docker files basic and functional but with intentional issues to fix
- **PRIMARY FOCUS**: 85% Docker optimization work, 15% configuration
- NO TODO comments in Python code
- May include comments in Docker files hinting at optimization opportunities
- Application immediately runnable after basic Docker setup (though slow/inefficient)
- **BASE DIRECTORY**: /root/task for all files
- **SCENARIO IMPLEMENTATION**: All routers, services, models, database setup implement the scenario's requirements
- **INTENTIONAL ISSUES**: Docker setup works but has 3-4 obvious optimization opportunities

## .gitignore INSTRUCTIONS:
Comprehensive file including:
- Python artifacts: __pycache__/, *.py[cod], *$py.class, *.so, .Python
- Virtual environments: venv/, env/, ENV/, .venv
- IDE files: .idea/, .vscode/, *.swp, *.swo
- Testing: .pytest_cache/, .coverage, htmlcov/
- FastAPI: .env (keep .env.example)
- Docker: .docker/
- OS: .DS_Store, Thumbs.db, desktop.ini
- Logs: *.log, logs/
- Distribution: dist/, build/, *.egg-info/
- Other: *.tmp, *.bak

## .dockerignore INSTRUCTIONS:
**INITIAL STATE**: Missing or very basic - candidate must create/improve (INTENTIONAL ISSUE):
- Initial file may only exclude: .git/, README.md
- **WHAT SHOULD BE EXCLUDED** (candidate discovers):
  - __pycache__/, *.pyc, *.pyo, *.pyd
  - .pytest_cache/, tests/, test_*.py
  - .venv/, venv/, env/
  - .git/, .gitignore, .dockerignore
  - .idea/, .vscode/
  - *.md (except needed ones)
  - .coverage, htmlcov/
  - *.log
  - .env (but keep .env.example if used)
  - docker-compose.yml, Dockerfile
- Missing .dockerignore contributes to large image size (intentional issue)

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Current Issues
   - Helpful Tips
   - Application Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing:
1. The business scenario from input_scenarios
2. That the FastAPI application is fully functional
3. That deployment works but has performance/efficiency concerns
4. The challenge is to optimize for production standards

NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why optimization matters.

### Current Issues

**CRITICAL REQUIREMENT**: List 4-6 observable problems as questions or symptoms:
- Frame as questions: "Why does...?", "What causes...?"
- Describe symptoms without revealing solutions
- Compare to expected standards
- Focus on observable behavior, not technical specifics

### Helpful Tips

Provide practical guidance without revealing specific implementations:
- Suggest exploring what files are essential for running services versus development
- Mention thinking about how different base choices impact artifact characteristics
- Hint at considering mechanisms for improving build efficiency when files haven't changed
- Recommend exploring how services communicate within container environments
- Suggest thinking about strategies for verifying service readiness before traffic routing
- Point toward how production patterns differ from development configurations
- Hint at approaches for minimizing security attack surface
- Recommend considering how to optimize repeated build operations
- Suggest exploring logging practices for operational visibility
- Mention thinking about resource allocation in containerized environments
- Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Investigate"
- **CRITICAL**: Tips should guide discovery toward fundamental containerization concepts, not provide direct solutions or specific code
- Frame suggestions around learning and understanding rather than prescriptive instructions
- Examples of proper framing:
  * "Consider what gets included in deployment artifacts and whether all of it is needed at runtime"
  * "Think about how build processes can reuse work when only certain files change"
  * "Explore how containerized services locate and communicate with each other"
  * "Review what makes a service 'ready' to handle requests versus just 'running'"
  * "Investigate how to separate development tooling from production runtime needs"

### Application Access

- Provide access details: host (use <DROPLET_IP> placeholder), port
- List scenario-specific API endpoints (e.g., "/api/inventory", "/api/products", "/health", "/docs")
- Mention monitoring/health endpoints if available
- Generic inspection guidance: "Use container platform tools to inspect running services"
- Suggest observing service behavior, logs, and resource usage
- **AVOID**: Specific command syntax

### Objectives

- Clear, measurable goals for the candidate appropriate for basic level
- This is what the candidate should be able to do successfully to say that they have completed the task
- These objectives will also be used to verify the task completion and award points
- Focus on deployment optimization outcomes and production readiness
- Frame objectives around outcomes rather than specific technical implementations
- Examples of proper framing:
  * "Improve deployment efficiency to meet modern CI/CD pipeline standards"
  * "Optimize artifact characteristics for faster distribution and reduced storage"
  * "Configure service initialization to achieve sub-10-second readiness targets"
  * "Implement operational safeguards for service reliability and automatic recovery"
  * "Reduce system resource footprint while maintaining performance"
  * "Align deployment security with container best practices"
  * "Enable operational visibility through proper logging mechanisms"
- Objectives should be measurable but not prescribe specific Docker commands or files
- Should guide candidates to think about: efficiency, resource usage, security, reliability, operational visibility
- **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify

- Specific checkpoints after optimization, what to test and how to confirm improvements
- Observable behaviors or metrics to validate
- These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
- Include both functional testing and optimization validation checks
- Frame verification in terms of observable outcomes and measurable improvements
- Examples of proper framing:
  * "Compare artifact sizes before and after optimization and verify significant reduction"
  * "Measure build time improvements and confirm faster deployment cycles"
  * "Verify service becomes responsive within expected timeframes after startup"
  * "Check system resource usage and confirm efficient operation"
  * "Test that services communicate correctly using orchestration naming"
  * "Confirm service recovers automatically from failure scenarios"
  * "Validate data persistence across service restarts"
  * "Ensure logs are properly accessible for operational monitoring"
  * "Verify all scenario-specific endpoints remain fully functional"
- Suggest what to verify and why it matters, not specific commands or tools to use
- Guide candidates to validate: build efficiency, resource usage, functionality, reliability, security posture
- **CRITICAL**: Describe what behaviors and metrics to verify, not the specific Docker commands or files to check

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
- Setup or deployment commands (docker build, docker-compose up, etc.)
- Direct solutions or implementation hints
- Step-by-step optimization guides
- Specific Docker technologies or approaches (e.g., "use multi-stage builds", "use slim images", "create .dockerignore")
- Direct answers and configuration snippets that would give away the solution to the task
- Any specific file names or implementation details that would give away the solution to the task
- Should not provide any particular method or approach to implement the solution
- File names or specific configuration patterns that would reveal the solution (.dockerignore, multi-stage, gunicorn)
- Phrases like "you should implement", "make sure to add", "create a file called X", "use technology Y"
- Specific Docker or container API recommendations that would reveal the solution approach
- Directory structure details that would dictate the implementation approach
- Technology names that reveal solutions (gunicorn, slim, alpine, multi-stage)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name (within 50 words) reflecting the scenario context and focusing on basic Docker optimization",
   "question": "Brief description incorporating the scenario's business problem, mentioning the application works but Docker setup needs optimization. Focus on Docker fundamentals for the given scenario, NOT Python changes. Clearly state the optimization challenge.",
   "code_files": {{
      "README.md": "Complete README with Task Overview reflecting the scenario and deployment issues, Current Issues section, Tips, Access with scenario-specific endpoints, Objectives focused on optimization, Verification with measurable criteria",
      ".gitignore": "Comprehensive exclusions for Python, FastAPI, Docker, IDE",
      ".dockerignore": "Missing or very basic (2-3 lines) - candidate must improve (INTENTIONAL)",
      "requirements.txt": "Complete dependencies required by the scenario with versions, may include dev deps mixed with prod (INTENTIONAL)",
      "docker-compose.yml": "Basic service definitions matching scenario needs, no version field, hardcoded values, missing health checks and resource limits (INTENTIONAL), development server config (INTENTIONAL)",
      "Dockerfile": "Single-stage with heavyweight image, poor layer ordering, runs as root (INTENTIONAL ISSUES), but functional",
      "run.sh": "Complete deployment script with health checks and validation",
      "kill.sh": "Complete cleanup script",
      "app/__init__.py": "Empty or basic init file",
      "app/main.py": "Complete FastAPI application initialization and router inclusion",
      "app/config.py": "Complete configuration management (or use .env.example)",
      "app/routers/*.py": "Complete API routers implementing scenario's endpoints",
      "app/services/*.py": "Complete service layer implementing scenario's business logic",
      "app/models/*.py": "Complete Pydantic models and database models matching scenario's domain",
      "app/database.py": "Complete database setup and session management (if needed)",
      "app/dependencies.py": "Dependency injection setup (if needed)"
  }},
  "outcomes": "Expected results in 2-3 lines: optimized Docker setup with 60%+ smaller image, faster build times, production-ready configuration, all while maintaining full functionality of the scenario's application. Include measurable improvements.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level problem in a business context, (2) the specific goal, and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": "Bullet points: Docker, Docker Compose, basic Python/FastAPI familiarity (no expertise needed), Git, curl/Postman for testing scenario-specific endpoints, understanding of Docker image layers and caching",
  "answer": "High-level solution focusing on basic Docker optimization for the scenario: multi-stage builds, slim base images, proper .dockerignore, layer caching optimization, production ASGI server configuration, health checks, resource limits, non-root user. Explain the intentional issues and how to fix them. Minimal mention of configuration changes.",
  "hints": "Single line suggesting focus on Docker image optimization, layer caching, and production configuration for containerizing the scenario's application. Must NOT reveal specific implementations but can mention the areas to investigate (image size, build time, server configuration).",
  "definitions": {{
     "terminology_1": "definition_1 ",
    "terminology_2": "definition_2"
    ...
    }}
}}

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, within 50 words
3. **code_files** must include README.md, .gitignore, requirements.txt, Docker files, run.sh, kill.sh, and all Python source files
4. **README.md** must follow the structure above with Task Overview, Current Issues, Helpful Tips, Application Access, Objectives, How to Verify
5. **FastAPI application** must be COMPLETE — NO Python changes needed, only Docker optimization
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Docker/Python terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **INTENTIONAL ISSUES** must be obvious but non-breaking — application works but needs optimization
10. **All paths** must reference /root/task as the base directory
"""

PROMPT_REGISTRY = {
    "Docker (BASIC), Python - FastAPI (BASIC)": [
        PROMPT_FASTAPI_DOCKER_BASIC_CONTEXT,
        PROMPT_FASTAPI_DOCKER_BASIC_INPUT_AND_ASK,
        PROMPT_FASTAPI_DOCKER_OPTIMIZATION_INSTRUCTIONS_BASIC,
    ]
}
