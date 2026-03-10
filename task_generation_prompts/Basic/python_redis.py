PROMPT_FASTAPI_REDIS_BASIC_INPUT_AND_ASK = """
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
2. What will the task look like? (Describe the type of Redis caching implementation or fix required, the expected deliverables, and how it aligns with BASIC Python FastAPI and Redis proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_FASTAPI_REDIS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role expectations, 
especially focusing on how Redis may be used in simple FastAPI-based systems — such as for caching, background task handling, or lightweight data storage?
"""
PROMPT_FASTAPI_REDIS_OPTIMIZATION_INSTRUCTIONS_BASIC ="""
## GOAL
As a technical architect experienced in Redis caching and Python FastAPI integration, you are given a list of real world scenarios and proficiency levels for Redis. 
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional API with Redis integration but with basic logical bugs, missing implementations, or simple performance issues that require basic-level Redis optimization skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CRITICAL DEPLOYMENT AND IMPLEMENTATION PHILOSOPHY

**DEPLOYMENT SETUP REQUIREMENTS:**
This is the MOST CRITICAL aspect of basic-level task generation. The task generation must follow this exact pattern:

1. **WORKING BUT BROKEN DEPLOYMENT**: 
   - Generate files that will successfully deploy and run using run.sh
   - The API must start without errors and be accessible
   - Redis connection must be established successfully
   - All endpoints must be reachable and respond (even if slowly or incorrectly)
   - The application should NOT crash or fail to start

2. **PROBLEMS EXIST IN IMPLEMENTATION**:
   - The deployed application has basic Redis caching issues (missing caching, wrong data types, no TTL, inefficient patterns)
   - Some endpoints are slow because caching is not implemented
   - Some endpoints return stale data because cache invalidation is missing
   - Some endpoints don't use Redis at all when they should
   - Basic mistakes like wrong Redis commands, improper key names, or missing connection pooling
   - The issues are FUNCTIONAL - the code runs but performs poorly or incorrectly

3. **CANDIDATE RECEIVES WORKING ENVIRONMENT**:
   - Candidate gets a fully deployed environment with API running and Redis connected
   - They DO NOT need to fix deployment issues or Docker problems
   - They DO NOT need to troubleshoot connection failures
   - They ONLY need to refactor/optimize the caching implementation in the code
   - The basic setup is given - candidate focuses on improving the caching logic

4. **WHAT CANDIDATE MUST DO**:
   - Analyze the running application and identify basic caching issues
   - Add missing Redis caching where needed
   - Fix incorrect Redis usage patterns
   - Implement proper TTL strategies
   - Add basic cache invalidation logic
   - Optimize simple caching patterns
   - Refactor code to follow basic Redis best practices

**SEPARATION OF CONCERNS**:
- **run.sh + docker-compose.yml**: These MUST work perfectly and deploy without issues
- **FastAPI application code**: This is where the basic problems exist and need optimization
- Deployment = Working ✓
- Implementation = Needs fixing by candidate ✗

This separation ensures candidates focus on Redis optimization skills rather than debugging deployment issues.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY DEPLOYED and RUNNING FastAPI application that is already connected to Redis cache. The FastAPI application includes:
- Complete REST API endpoints that are accessible and responding
- Working Redis connection (no connection errors)
- All necessary basic structure and configuration
- Simple API schemas and response formatting
- Pre-configured Redis that is running and accessible
- Basic caching implementation with simple mistakes, missing features, or inefficient patterns that require basic-level fixes

The candidate's responsibility is to identify and fix basic Redis caching issues in the code and improve the implementation. A part of the task completion is to watch the candidate implement basic Redis caching best practices at an entry level (1-2 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the basic-level Redis optimization scenario
- Task must provide a WORKING and DEPLOYED application with basic Redis implementation issues requiring basic-level optimization skills
- **CRITICAL**: The FastAPI application should be FULLY DEPLOYED, RUNNING, and ACCESSIBLE but performing poorly or incorrectly due to basic Redis caching mistakes that require simple fixes
- **CRITICAL**: The deployment infrastructure (Docker, docker-compose, run.sh) MUST work perfectly without any errors. All deployment issues must be resolved in the generated files. The ONLY problems should be in the application code's Redis implementation.
- **CRITICAL**: The exact problem described in the task scenario MUST be perfectly replicated in the code files. For example, if the scenario mentions "endpoint X is slow because caching is missing", the actual code MUST have endpoint X without any caching. If it mentions "stale data because cache is never cleared", the code MUST have caching without any invalidation logic. The candidate should ONLY need to fix/add the caching implementation, NOT debug deployment.
- **CRITICAL**: Candidates must understand that fixing Redis caching issues means modifying the FastAPI application code. The task should make it clear that they need to add missing caching, fix incorrect Redis usage, implement TTL strategies, and add cache invalidation in the application endpoints.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are relevant to the context. 
- Generate a complete, DEPLOYED and RUNNING FastAPI application with Redis that has basic implementation issues according to the task requirements suitable for basic-level engineers (1-2 years experience).
- **PROVIDE BASIC PROBLEMATIC REDIS IMPLEMENTATION**: Include code with simple caching mistakes such as:
  - Missing caching on endpoints that should be cached
  - Using wrong Redis data types (storing complex objects as strings instead of hashes)
  - No TTL set on cached data
  - Basic key naming issues (not following conventions)
  - Missing cache invalidation on data updates
  - No error handling for Redis operations
  - Fetching from database even when cache exists
  - Inefficient get/set patterns (multiple calls instead of single operation)
  - Not using connection pooling properly
- The question should be a real-world business scenario requiring basic-level Redis caching implementation and simple optimization, NOT building from scratch.
- The complexity of the optimization task and specific improvements expected from the candidate must align with basic proficiency level (1-2 years experience) requiring fundamental Redis skills including:
  - Adding basic caching to endpoints
  - Setting appropriate TTL values
  - Implementing simple cache invalidation
  - Using correct Redis data types (strings, hashes)
  - Following basic key naming conventions
  - Adding basic error handling for Redis operations
  - Understanding cache-aside pattern
  - Implementing simple get/set operations
  - Basic connection handling
- The question must NOT include hints about the specific fixes needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to basic Redis practices suitable for entry-level developers.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Redis documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively implement and fix basic Redis caching patterns at an entry level, rather than testing rote memorization. Therefore, the complexity of the tasks should require genuine understanding of basic Redis concepts and practical implementation skills.
- Tasks should involve straightforward caching challenges that test fundamental Redis knowledge.
- Candidates will be encouraged to use AI to help with boilerplate code and learning Redis commands, but they must understand the basic caching concepts.

## Code Generation Instructions:
Based on the real-world scenarios provided above, create a Redis optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- **CRITICAL**: The scenario description MUST be perfectly replicated in the actual code files. Every missing caching implementation, incorrect usage, or basic mistake mentioned in the scenario MUST exist in the generated code exactly as described.
- **CRITICAL**: The deployment MUST work perfectly. All Docker, docker-compose, and run.sh files must be error-free and result in a running application. Test mentally that the deployment would succeed.
- Matches the complexity level appropriate for basic proficiency level (1-2 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for basic Redis implementation skills.
- Tests practical basic-level Redis caching implementation skills that require understanding of fundamental caching concepts.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided to ensure variety in task generation.
- **CRITICAL**: The FastAPI application should be COMPLETE, DEPLOYED, and RUNNING with all endpoints accessible, but with basic Redis implementation issues that need simple fixes.
- The Redis connection setup should work without errors.
- All FastAPI routes should be implemented and accessible but with missing or incorrect basic caching patterns.
- Redis should be running and accessible with proper configuration.
- The code files generated must be valid, deploy successfully, and run without crashes, but have basic caching implementation issues.
- **CRITICAL**: The task focuses on fixing existing basic caching implementation issues and adding missing simple caching, NOT building from scratch or debugging deployment.
- For BASIC level proficiency: Use redis-py library with simple get/set operations and basic patterns.

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Python FastAPI that connects to Redis
- MUST include a Dockerfile for the FastAPI application that builds without errors
- A run.sh which has the end-to-end responsibility of deploying the infrastructure successfully
- A docker-compose.yml file which contains all the applications — a docker for running the Python FastAPI REST API and a docker for running the Redis cache
- **CRITICAL - DEPLOYMENT MUST BE PERFECT**: The infrastructure setup MUST be fully automated and work without any errors. Candidates should receive a running application, NOT a broken deployment.
- **CRITICAL**: All deployment files (run.sh, docker-compose.yml, Dockerfile) must be thoroughly validated to ensure successful deployment

### Docker-compose Instructions:
  - Redis service with proper working configuration (port 6379, proper image)
  - FastAPI service with working dependency on Redis using depends_on
  - Proper network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - **CRITICAL**: FastAPI service MUST start successfully and be accessible
  - **CRITICAL**: Redis service MUST start successfully and be connectable
  - **TESTING REQUIREMENT**: Mentally verify that this docker-compose configuration will result in both services running successfully

### Redis Configuration Instructions:
- Redis should be configured with working default settings
- Redis MUST be accessible from the FastAPI application
- Connection MUST succeed without errors
- May include some sample data for testing

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d` and ensures successful deployment
  + **CRITICAL**: This script MUST work perfectly without any errors
  + WAIT MECHANISM: Implements proper health check to wait for Redis service to be fully ready and accepting connections
  + VALIDATION: Validates that FastAPI application is responding and connected to Redis successfully
  + DATA INITIALIZATION: May populate some initial test data in Redis
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling but should not encounter errors in normal execution
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  + **SUCCESS CONFIRMATION**: Script should clearly indicate successful deployment completion

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.  
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes (Redis volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and redis:7-alpine).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files were created, so that no project files remain.
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
  - Remove all Redis data directories that were mounted via volumes.
  - Ensure that both the custom application container and the Redis container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile for the FastAPI application
  - **CRITICAL**: Dockerfile MUST build successfully without errors
  - Should use appropriate Python base image (python:3.11-slim or similar)
  - Should install dependencies from requirements.txt correctly
  - Should expose appropriate port for FastAPI (typically 8000)
  - Should include proper working directory set to /root/task
  - Should include proper entry point that starts the application
  - Must follow Docker best practices
  - **DO NOT use environment variables or .env files**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location
  - **VALIDATION**: Ensure all COPY commands reference correct file paths

**CRITICAL**: All Docker and script references must account for the /root/task base directory and must result in successful deployment.

The output should be a valid json schema with proper file structure.

## Code file requirements:
- Multiple files will be generated and must be included in the JSON structure correctly
- Code should follow Python PEP8 guidelines and include basic Redis caching mistakes or missing implementations
- **CRITICAL**: The FastAPI application files MUST be complete and fully functional with all endpoints accessible, Redis connection working, but with basic caching implementation issues
- **CRITICAL**: The exact problems described in the task scenario MUST be present in the code. Do not implement optimized solutions - implement the problematic or missing code exactly as described in the scenario
- **CRITICAL**: Deployment files (Dockerfile, docker-compose.yml, run.sh) MUST be perfect and work without errors
- Redis connection setup should work correctly without connection errors
- FastAPI routes should be accessible but with missing or incorrect basic caching
- Tasks should focus on fixing existing basic caching issues and adding missing simple caching implementations
- **SEPARATION OF CONCERNS**: 
  - docker-compose.yml: MUST work perfectly ✓
  - run.sh: MUST deploy successfully ✓
  - Dockerfile: MUST build without errors ✓
  - FastAPI app: Should run but have basic caching issues that need fixing ✗
- DO NOT include any 'TODO' or placeholder comments in FastAPI code
- DO NOT include any comments that give away optimization solutions
- DO NOT include any comments that hint at the solution in the files
- The FastAPI application should be immediately runnable and accessible but will perform poorly or incorrectly until candidate fixes basic caching issues
- **CRITICAL**: All directories must contain __init__.py files for proper Python package structure
- **BASIC REDIS ISSUES**: Existing caching implementation needs basic fixes - code contains missing caching or incorrect usage requiring entry-level solutions
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Redis and FastAPI development tasks that includes:
- Python bytecode and cache files (__pycache__, *.pyc)
- Virtual environment directories (venv/, env/)
- Build and distribution artifacts
- IDE and editor files (.vscode/, .idea/)
- Log files (*.log)
- Redis dump files (dump.rdb, appendonly.aof)
- Docker volumes data
- Any other standard exclusions for Python/FastAPI/Redis development

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Redis Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to basic-level Redis tasks
- Task Overview section MUST contain the exact business scenario and specific basic caching problems that need fixes
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Redis scenario being generated
- Use concrete business context explaining basic caching issues, not generic descriptions
- Language should be beginner-friendly and clear
- DO NOT mention specific routes, file names, or code structure in examples
- Focus on business impact and performance issues, not technical implementation details

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-4 meaningful sentences describing:
1. The business context and what the application does
2. The current performance or functionality problems users are experiencing
3. The impact on business operations or user experience
4. What needs to be improved (without mentioning technical solutions)

NEVER generate empty content - always provide substantial business context that explains the problem from a user/business perspective.

**RULES:**
- Focus on WHAT is slow or broken, not HOW to fix it
- Describe user-facing problems (slow page loads, stale data, etc.)
- Explain business impact (customer complaints, lost revenue, poor experience)
- DO NOT mention specific endpoints, routes, files, or code structure
- DO NOT hint at solutions (like "needs caching" or "missing TTL")
- Keep it at business/product level, not technical implementation level

**Example of Good Task Overview:**
"An online bookstore application is experiencing slow performance during peak hours. Customers complain that browsing book listings takes too long, sometimes waiting 3-5 seconds per page. When store managers update book prices or inventory, customers continue to see old information for extended periods, leading to confusion and incorrect purchases. The slow response times and stale data are causing customer dissatisfaction and impacting sales."

**Example of Bad Task Overview (DO NOT DO THIS):**
"The GET /products endpoint is not using Redis caching. You need to add caching with TTL and implement cache invalidation on PUT endpoints." ❌

### Helpful Tips
Write practical, beginner-friendly tips in clear language so basic-level candidates understand how to approach the task:
  - Provide actionable tips on analyzing the problem and understanding caching concepts
  - Suggest approaches to identify what needs optimization
  - Mention tools or commands they can use to inspect and debug
  - Provide tips on testing and verifying their improvements
  - Explain relevant concepts in simple terms without giving solutions
  - Use bullet points (4-7 tips recommended)
  - DO NOT provide actual code solutions or specific implementation details
  - DO NOT mention specific file names or code structure
  - Focus on methodology, analysis techniques, and general best practices

**RULES:**
- Each tip should be actionable but not prescriptive
- Guide their thinking without giving away the answer
- Use beginner-friendly language
- Include tips about tools they can use
- Suggest ways to measure improvements
- Explain concepts they should understand

**Example of Good Helpful Tips:**
```
- Start by testing the application manually to identify which operations feel slow
- Use timing tools or browser developer tools to measure response times before making changes
- Check what data is being fetched repeatedly and consider if it changes frequently
- When storing temporary data, think about how long it should remain valid
- Remember that when source data changes, any stored copies should be updated or removed
- Use inspection tools to verify your optimizations are working as expected
- Test both the happy path and scenarios where data gets updated
```

**Example of Bad Tips (DO NOT DO THIS):**
```
- Add caching to the get_products() function in api.py ❌
- Set TTL to 300 seconds using SETEX command ❌
- Implement cache invalidation in the update route ❌
```

### Redis Access
  - Provide the Redis connection details in a clear format
  - Mention tools they can use to inspect Redis
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>)
  - Include basic inspection commands that help them understand Redis state
  - Keep it simple and focused on access information

**RULES:**
- Use clean, structured format for connection details
- Mention 2-3 useful tools (redis-cli, RedisInsight)
- Include 3-5 basic commands for inspection
- DO NOT include complex Redis commands
- Focus on read-only inspection commands

**Format Example:**
```
**Connection Details:**
- Host: <DROPLET_IP>
- Port: 6379
- Database: 0

**Access Tools:**
You can use redis-cli or RedisInsight to inspect the cache.

**Useful Commands:**
- View all keys: KEYS *
- Get value: GET key_name
- Check expiration: TTL key_name
- View key type: TYPE key_name
```

### Objectives
  - List 3-5 clear, measurable goals focusing on basic Redis caching implementation
  - Each objective should be specific and testable
  - Objectives should be achievable for 1-2 years experience level
  - These objectives will be used to verify task completion and award points
  - Focus on observable improvements (performance, correctness, functionality)
  - Use simple language and avoid technical jargon

**RULES:**
- Each objective must be measurable (include numbers, percentages, or observable behaviors)
- Start with action verbs (Improve, Reduce, Implement, Ensure, Achieve)
- DO NOT mention specific file names or code structure
- Focus on outcomes, not implementation details
- Keep objectives realistic for basic level

**Example of Good Objectives:**
```
- Improve response times for data retrieval operations by at least 60%
- Ensure data freshness by preventing stale information from being displayed after updates
- Reduce database load by minimizing redundant queries for frequently accessed data
- Achieve consistent performance during repeated requests for the same information
```

**Example of Bad Objectives (DO NOT DO THIS):**
```
- Add caching to api.py file ❌
- Use SETEX command with 300 second TTL ❌
- Implement cache_helper.py functions ❌
```

### How to Verify
  - Provide 4-7 specific verification steps in a numbered list
  - Each step should be clear and easy to follow for beginners
  - Include steps for both functional correctness and performance improvement
  - Steps should be ordered logically (test baseline, make changes, test again, verify specific behaviors)
  - Include ways to measure improvements objectively

**RULES:**
- Use numbered list for sequential steps
- Each step should be self-contained and clear
- Include both manual testing and inspection steps
- Show how to verify before/after improvements
- Mention tools for measurement when relevant
- DO NOT mention specific file names or code structure
- Focus on user-facing behaviors and observable outcomes

**Example of Good Verification Steps:**
```
1. Test the application before optimization - note the response times for data retrieval operations
2. Perform the same operation multiple times and observe if subsequent requests are faster
3. Check the data store to verify that information is being stored appropriately
4. Update or delete some data through the application
5. Immediately retrieve the same data and verify it reflects the latest changes
6. Measure the response time improvement - it should be at least 60% faster for repeated requests
7. Monitor system resources to confirm reduced load on the database
```

**Example of Bad Verification Steps (DO NOT DO THIS):**
```
1. Check if cache_helper.py has the caching functions ❌
2. Verify SETEX is used in api.py ❌
3. Run the code in main.py ❌
```

### NOT TO INCLUDE in README:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is already deployed)
  - How to run run.sh (it's already executed)
  - Docker or docker-compose instructions (infrastructure is ready)
  - Step-by-step installation guides (everything is already installed)
  - Specific code solutions or implementation details
  - File names, routes, function names, or code structure
  - Complex technical jargon or advanced concepts
  - Direct mentions of what to code or which files to modify

### OVERALL README TONE AND STYLE:
- Write from a product/business perspective, not technical implementation perspective
- Focus on WHAT needs to improve, not HOW to improve it
- Use clear, beginner-friendly language throughout
- Each section should provide value without giving away solutions
- Think like a product manager describing the problem, not a developer explaining the fix
- Keep the candidate focused on understanding the problem and exploring solutions

## REQUIRED OUTPUT JSON STRUCTURE

**CRITICAL**: The output MUST follow this EXACT JSON structure. DO NOT add or remove fields. DO NOT use alternative structures like "requirements", "evaluation_criteria", or "description".

{{
   "name": "Task Name (within 50 words)",
   "question": "A short description of the basic-level Redis caching task scenario including the specific simple caching problems in the existing running application that need to be identified and fixed — what basic caching issues exist (missing caching, no TTL, missing invalidation), and what simple fixes are needed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Redis Access, Objectives, and How to Verify for basic-level tasks",
      ".gitignore": "Proper Python, Docker, and Redis exclusions",
      "requirements.txt": "Python dependencies list including Redis libraries (redis==4.5.1, fastapi==0.104.1, uvicorn==0.24.0, pydantic==2.5.0)",
      "docker-compose.yml": "Docker services for Redis and FastAPI (NO version specifications, NO env vars, MUST WORK PERFECTLY)",
      "Dockerfile": "Docker configuration for FastAPI application (MUST BUILD WITHOUT ERRORS)",
      "run.sh": "Complete setup script for deployment (MUST WORK PERFECTLY AND DEPLOY SUCCESSFULLY)",
      "kill.sh": "Complete cleanup script to remove all resources",
      "app/__init__.py": "Empty file for Python package structure",
      "app/main.py": "Complete FastAPI application with all endpoints accessible but with missing or incorrect basic caching",
      "app/redis_client.py": "Redis connection configuration (MUST WORK - no connection errors)",
      "app/cache/__init__.py": "Empty file for Python package structure",
      "app/cache/cache_helper.py": "Basic caching helper functions with simple mistakes or missing implementations",
      "app/routes/__init__.py": "Empty file for Python package structure",
      "app/routes/api.py": "Complete API route implementations with missing or incorrect basic caching (endpoints MUST be accessible)",
      "app/schemas/__init__.py": "Empty file for Python package structure",
      "app/schemas/schemas.py": "Pydantic schemas for API requests/responses",
      "app/models/__init__.py": "Empty file for Python package structure (if needed)",
      "app/models/models.py": "Simple data models (if needed)",
      "app/database/__init__.py": "Empty file for Python package structure (if database is used)",
      "app/database/db.py": "Simple database connection or mock data (if needed)"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable basic caching improvements. Use simple english. Example: 'The application will demonstrate significantly faster response times for repeated data requests. Users will always see up-to-date information after any changes are made. Database load will be reduced through efficient temporary data storage.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level problem in a business context, (2) the specific goal, and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": [
    "Python 3.10 or higher installed",
    "Docker and Docker Compose installed and running",
    "Basic understanding of REST APIs and HTTP methods",
    "Familiarity with caching concepts and when to use caching",
    "Basic knowledge of key-value data stores",
    "Understanding of data expiration and Time-To-Live (TTL) concepts",
    "Basic command line proficiency",
    "Git installed for version control",
    "Redis inspection tools (redis-cli or RedisInsight) - optional but helpful",
    "Basic understanding of performance optimization principles"
  ],
  "answer": "give the high solution focusing on what optimizations are needed to improve the performance of the application",
  "hints": "A single line hint that gently guides toward the approach without giving away the solution. Example: 'Think about how you can temporarily store frequently accessed data to avoid fetching it from the source every time, and remember to refresh that stored data when the original information changes.'",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

"""

PROMPT_REGISTRY = {
    "Python - FastAPI (BASIC), Redis (BASIC)": [
        PROMPT_FASTAPI_REDIS_BASIC_CONTEXT,
        PROMPT_FASTAPI_REDIS_BASIC_INPUT_AND_ASK,
        PROMPT_FASTAPI_REDIS_OPTIMIZATION_INSTRUCTIONS_BASIC,
    ]
}