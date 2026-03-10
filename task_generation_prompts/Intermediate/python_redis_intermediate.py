PROMPT_FASTAPI_REDIS_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI and Redis assessment task.

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
2. What will the task look like? (Describe the type of Redis optimization or FastAPI integration required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_FASTAPI_REDIS_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, 
particularly in relation to using Redis for caching, queue management, background processing, or real-time communication in a FastAPI-based system?
"""

PROMPT_FASTAPI_REDIS_OPTIMIZATION_INSTRUCTIONS_INTER ="""
## GOAL
As a technical architect super experienced in Redis caching and Python FastAPI integration, you are given a list of real world scenarios and proficiency levels for Redis.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional API with Redis integration but either with logical bugs, suboptimal caching strategies, or performance issues that require intermediate-level Redis optimization skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL FastAPI application that is already connected to Redis cache with existing implementation and data. The FastAPI application includes:
- Complete REST API endpoints with business logic implemented but with suboptimal Redis caching patterns requiring intermediate-level optimization
- Full Redis connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete data models and API schemas
- Pre-configured Redis with realistic data and intentionally inefficient caching strategies, poor key patterns, missing TTLs, cache stampede issues, or improper data structures that demand advanced problem-solving

The candidate's responsibility is to identify and fix Redis caching issues according to the task requirements and then make any code changes in the app to support the fixes. A part of the task completion is to watch the candidate implement Redis optimization best practices and improve caching performance at an intermediate level (3-5 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Redis optimization scenario
- Task must provide a working application with existing Redis implementation and intentionally suboptimal caching patterns requiring intermediate-level optimization skills
- **CRITICAL**: The FastAPI application should be FULLY functional but performing poorly due to inefficient Redis usage that requires sophisticated analysis and optimization techniques
- **CRITICAL**: The exact problem described in the task scenario MUST be perfectly replicated in the code files. For example, if the scenario mentions "slow cache lookups due to improper key patterns", the actual code MUST contain those exact slow cache lookups with improper key patterns. If it mentions "cache stampede on popular endpoints", the code MUST have that exact issue implemented. The candidate should ONLY need to optimize/fix the code, NOT build anything from scratch.
- **CRITICAL**: Candidates must understand that optimizing Redis caching requires corresponding changes in the FastAPI application code. The task should make it clear that after fixing Redis issues (key patterns, TTL strategies, data structures, pipelining), they must also update the API endpoints, caching logic, and data access patterns in the FastAPI application to properly utilize these optimizations and maintain functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a complete, working FastAPI application with Redis caching that has performance issues or bugs according to the task requirements suitable for intermediate-level engineers (3-5 years experience).
- **PROVIDE PROBLEMATIC REDIS IMPLEMENTATION**: Include code with inefficient caching strategies such as:
  - Poor key naming patterns causing slow lookups
  - Missing or improper TTL configurations
  - Cache stampede vulnerabilities
  - Inefficient data structure usage (using strings when hashes/sets would be better)
  - Missing pipeline operations for bulk operations
  - No cache warming strategies
  - Improper cache invalidation patterns
  - Serialization inefficiencies
  - Missing connection pooling or improper connection handling
- The question should be a real-world business scenario requiring intermediate-level Redis caching optimization involving multiple endpoints, complex caching patterns, and advanced optimization strategies, NOT building from scratch.
- The complexity of the optimization task and specific improvements expected from the candidate must align with intermediate proficiency level (3-5 years experience) requiring advanced Redis optimization techniques including:
  - Advanced key pattern design and namespace strategies
  - Complex TTL and expiration strategies
  - Cache warming and preloading techniques
  - Pipeline and transaction optimization for bulk operations
  - Proper Redis data structure selection (Strings, Hashes, Sets, Sorted Sets, Lists)
  - Cache stampede prevention using locks or probabilistic early expiration
  - Connection pool optimization
  - Serialization optimization (JSON vs MessagePack vs Pickle)
  - Cache-aside pattern optimization
  - Read-through and write-through caching strategies
  - Redis monitoring and performance analysis
- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to the latest Redis best practices and versions for intermediate-level optimization.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Redis documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize Redis caching performance issues at an intermediate level, rather than testing rote memorization. Therefore, the complexity of the optimization tasks should require genuine intermediate-level Redis performance engineering and advanced problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Tasks should involve multi-layered caching optimization challenges that require understanding of Redis internals, caching patterns, and advanced Redis features.
- Candidates will be encouraged to use AI to help with boilerplate code and other bugs but not replace their own thinking and analysis skills.

## Code Generation Instructions:
Based on the real-world scenarios provided above, create a Redis optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- **CRITICAL**: The scenario description MUST be perfectly replicated in the actual code files. Every performance issue, slow operation, or bug mentioned in the scenario MUST exist in the generated code exactly as described.
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced Redis optimization skills.
- Tests practical intermediate-level Redis caching optimization and performance tuning skills that require deep understanding of Redis internals, caching patterns, and advanced optimization principles.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The FastAPI application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and Redis connection setup, but with intentionally inefficient caching patterns requiring intermediate-level optimization.
- The Redis connection setup should use proper connection pooling but with suboptimal configurations requiring optimization.
- All FastAPI routes should be implemented and working but with suboptimal Redis caching patterns that need intermediate-level optimization.
- Redis should come with realistic sample data and intentionally poor caching strategies requiring advanced optimization practices.
- The code files generated must be valid and executable but perform poorly due to Redis caching issues requiring intermediate-level solutions.
- **CRITICAL**: The task focuses on optimizing existing poorly performing caching patterns and Redis usage issues, NOT building from scratch.
- For INTERMEDIATE level proficiency: Use redis-py library with proper connection pooling, but implement suboptimal caching patterns that require intermediate-level optimization skills.

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Python FastAPI that integrates with Redis using advanced patterns
- MUST include a Dockerfile for the FastAPI application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Python FastAPI REST API and a docker for running the Redis cache.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and Redis connection.

### Docker-compose Instructions:
  - Redis service with proper configuration (port, persistence options if needed)
  - FastAPI service with dependency on Redis using depends_on
  - Volume mounts for Redis data persistence if needed
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - FastAPI service should start the application with inefficient Redis caching patterns requiring intermediate optimization
  - **CRITICAL**: Docker-compose handles container orchestration and service communication

### Redis Configuration Instructions:
- Redis should be configured with default settings but may have suboptimal configurations that need tuning
- Include realistic sample data in Redis through initialization scripts or application startup
- Create scenarios with poor key patterns, missing TTLs, or inefficient data structures
- Include cache stampede vulnerabilities or missing pipeline operations

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
  + WAIT MECHANISM: Implements proper health check to wait for Redis service to be fully ready and accepting connections
  + VALIDATION: Validates that FastAPI application is responding and connected to Redis
  + DATA INITIALIZATION: May include initial Redis data population with poor caching patterns
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling for failed container starts or Redis connection issues
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.  
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes (Redis volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and redis:7-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|redis:7-alpine' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Python bytecode files (`__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`) are also removed if present in `/root/task/`.
  - Remove all Redis data directories that were mounted via volumes (e.g., `/root/task/data/redis`).
  - Ensure that both the custom application container and the Redis container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile for the FastAPI application
  - Should use appropriate Python base image (python:3.11-slim or similar)
  - Should install dependencies from requirements.txt
  - Should expose appropriate port for FastAPI
  - Should include proper working directory set to /root/task
  - Should include proper entry point
  - Must be production-ready and follow Docker best practices
  - **DO NOT use environment variables or .env files**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location

**CRITICAL**: All Docker and script references must account for the /root/task base directory.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - requirements.txt (Python dependencies including fastapi, redis, uvicorn and other dependencies required for intermediate-level Redis usage)
  - docker-compose.yml (Redis and FastAPI services configuration)
  - Dockerfile (MUST be included - Docker configuration for FastAPI app)
  - run.sh (Script to deploy and setup the complete environment)
  - kill.sh (Complete cleanup script to remove all resources created by the task)
  - .gitignore (Ignore .pyc files, __pycache__, venv/, *.log, data/)
  - All FastAPI code files following the project structure with inefficient Redis caching patterns
  - **CRITICAL**: Include ALL __init__.py files for proper Python package structure

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Python PEP8 guidelines and include Redis caching anti-patterns requiring intermediate-level optimization
- **CRITICAL**: The FastAPI application files MUST be complete and fully functional with all endpoints, error handling, and Redis integration code, but with intentionally inefficient caching patterns.
- **CRITICAL**: The exact problems described in the task scenario MUST be present in the code. Do not implement optimized solutions - implement the problematic code exactly as described in the scenario.
- Redis connection setup and FastAPI routes should use suboptimal caching patterns that need intermediate-level improvement.
- Tasks should focus on identifying and optimizing existing caching performance bottlenecks requiring advanced Redis skills.
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: Handles container orchestration
  - run.sh: Starts containers, implements health checks, and validates deployment
  - FastAPI app: Should work but perform poorly due to Redis caching inefficiencies requiring intermediate-level solutions
- DO NOT include any 'TODO' or placeholder comments in FastAPI code
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that give way hints or any of the direct or indirect solution in the files 
- The FastAPI application should be immediately runnable but will perform poorly until candidate applies intermediate-level Redis optimization techniques.
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **REDIS CACHING ISSUES**: Existing caching patterns need advanced improvement - code contains inefficient Redis usage requiring intermediate-level solutions
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Redis and FastAPI development tasks that includes:
- Python bytecode and cache files
- Virtual environment directories
- Build and distribution artifacts
- IDE and editor files
- Log files
- Redis dump files (dump.rdb, appendonly.aof)
- Any other standard exclusions for Python/FastAPI/Redis development

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Redis Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level Redis optimization challenges
- Task Overview section MUST contain the exact business scenario and specific caching performance problems that need intermediate-level optimization
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Redis optimization scenario being generated
- Use concrete business context explaining caching performance bottlenecks requiring advanced optimization techniques, not generic descriptions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the specific caching performance problems affecting the application that need intermediate-level Redis optimization. Include details about which endpoints are slow, what caching issues exist (e.g., cache stampede, poor key patterns, missing TTLs), and the business impact.
NEVER generate empty content - always provide substantial business context that explains what caching performance issues exist and why advanced optimization is critical for business operations.

### Helpful Tips
Write practical tips in clear and comprehensive language so intermediate-level candidates understand the Redis optimization approach:
  - Provide actionable tips on analyzing Redis caching performance (e.g., monitoring cache hit rates, analyzing key patterns, checking TTL configurations)
  - Suggest tools and commands for Redis analysis (MONITOR, INFO, SLOWLOG, redis-cli --stat)
  - Mention key Redis concepts relevant to the optimization (pipelining, connection pooling, data structure selection)
  - Provide tips on identifying cache stampede issues, inefficient key patterns, or serialization bottlenecks
  - Suggest approaches for testing cache performance improvements
  - DO NOT provide actual solutions or specific code fixes
  - Use bullet points to keep the tips clean and readable
  - Focus on methodology and analysis techniques rather than direct answers

### Redis Access
  - Provide the Redis connection details (host(droplet-ip), port, database number if applicable)
  - Mention can use any preferred Redis client tools (e.g., redis-cli, RedisInsight, Medis) for analysis and monitoring
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address
  - Emphasize the importance of using Redis monitoring commands (MONITOR, SLOWLOG, INFO) for performance analysis
  - Include commands to check cache hit rates and key patterns

### Objectives
  - Clear, measurable goals for the candidate focusing on advanced Redis caching optimization requiring intermediate-level skills
  - This is what the candidate should be able to do successfully to demonstrate intermediate-level Redis optimization competency.
  - These objectives will also be used to verify the task completion and award points.
  - Should focus on caching performance improvement objectives with measurable outcomes (improved cache hit rates, reduced response times, eliminated cache stampede)
  - Include advanced optimization goals like key pattern improvements, TTL strategy implementation, and data structure optimization

### How to Verify
  - Specific checkpoints after optimization showing improved caching performance metrics
  - Observable behaviors to validate Redis caching performance improvements through the API
  - Should include verification steps for cache hit rate improvements and response time enhancements
  - Include methods to measure and compare before/after optimization results
  - Mention verification of proper TTL configurations, key patterns, and data structure usage
  - Include API endpoint testing to demonstrate performance improvements

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - FastAPI implementation guides (API is already complete)
  - Step-by-step Redis connection setup (connection details are provided)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific optimization solutions (candidates must analyze and implement advanced improvements)
  - Generic guidance that doesn't provide actionable tips

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words)",
   "question": "A short description of the intermediate-level Redis optimization task scenario including the specific caching performance problems in the existing application that need to be identified and resolved using advanced techniques — what caching performance bottlenecks exist, and what intermediate-level Redis optimizations are needed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Redis Access, Objectives, and How to Verify for intermediate-level optimization",
      ".gitignore": "Proper Python, Docker, and Redis exclusions",
      "requirements.txt": "Python dependencies list including Redis libraries (redis, fastapi, uvicorn, etc.)",
      "docker-compose.yml": "Docker services for Redis and FastAPI (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for FastAPI application",
      "run.sh": "Complete setup script for Redis and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      "app/__init__.py": "Empty file for Python package structure",
      "app/main.py": "Complete FastAPI application with all endpoints but inefficient Redis caching patterns requiring intermediate optimization",
      "app/redis_client.py": "Redis connection configuration with suboptimal settings",
      "app/cache/__init__.py": "Empty file for Python package structure",
      "app/cache/cache_manager.py": "Caching logic with inefficient patterns (poor key design, missing TTLs, no pipelining, etc.)",
      "app/routes/__init__.py": "Empty file for Python package structure",
      "app/routes/api.py": "Complete API route implementations with suboptimal caching patterns needing intermediate-level optimization",
      "app/schemas/__init__.py": "Empty file for Python package structure",
      "app/schemas/schemas.py": "Pydantic schemas for API requests/responses",
      "app/models/__init__.py": "Empty file for Python package structure (if needed)",
      "app/models/models.py": "Data models with poor serialization for Redis (if needed)"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable caching performance improvements and optimized Redis usage requiring intermediate-level skills. Use simple english.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the intermediate-level Redis optimization task. Mention things like Python 3.10+, Docker, Docker Compose, Redis client tools (redis-cli/RedisInsight), Git, pip, virtual environment support, Redis monitoring tools, redis-py library knowledge, intermediate Redis concepts, etc.",
  "answer": "High-level solution approach focusing on advanced Redis caching optimization strategies and intermediate-level performance tuning techniques for the given caching performance issues",
  "hints": "A single line hint on what a good intermediate-level approach to analyze and optimize the Redis caching performance could include. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward advanced caching performance analysis practices suitable for intermediate-level skills.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
    }}
}}
"""
PROMPT_REGISTRY = {
    "Python - FastAPI, Redis": [
        PROMPT_FASTAPI_REDIS_CONTEXT,
        PROMPT_FASTAPI_REDIS_OPTIMIZATION_INSTRUCTIONS_INTER,
        PROMPT_FASTAPI_REDIS_INPUT_AND_ASK,
    ]
}
