PROMPT_NODEJS_MONGODB_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js and MongoDB assessment task.

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
2. What will the task look like? (Describe the type of Node.js and MongoDB optimization required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_MONGODB_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""


PROMPT_NODEJS_MONGODB_OPTIMIZATION_INSTRUCTIONS ="""
## GOAL
As a technical architect experienced in MongoDB database and Node.js REST API integration, you are given a list of real world scenarios and proficiency levels for MongoDB.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional REST API and some initial schema but either with logical bugs or performance issues that require basic-level database optimization skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL Node.js Express/Fastify REST API application that is already connected to MongoDB with existing schema and data. The Node.js application includes:
- Complete REST API endpoints with business logic implemented but with straightforward inefficiencies in database queries AND basic API endpoint performance issues requiring basic-level optimization
- Full database connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete database models and API schemas
- Pre-populated database with realistic data and intentionally clear inefficient queries/schema design that demand basic problem-solving

The candidate's responsibility is to fix an issue with the database according to the task requirements and then make any code changes in the app to support the fixes. A part of the task completion is to watch the candidate implement MongoDB optimization best practices alongside Node.js API endpoint optimization and improve application performance at a basic level (0-2 years experience).

**CRITICAL NODE.JS API OPTIMIZATION REQUIREMENT**: This task is NOT only about MongoDB query optimization. Candidates must also optimize the Node.js API endpoints themselves by:
- Identifying and removing unnecessary database queries in endpoints
- Adding basic indexes to speed up database queries
- Implementing simple caching strategies at API level
- Optimizing basic data processing and response structures
- Adding basic pagination to endpoints returning large datasets
- Implementing simple error handling improvements
- Refactoring basic async/await patterns
- Reducing redundant computations in endpoint logic
- Optimizing basic middleware execution
- Improving basic request validation

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 characters and clearly describe the basic-level optimization scenario for BOTH MongoDB queries AND Node.js API endpoints
- Task must provide a working application with existing database schema, data, and intentionally clear suboptimal queries/database design/API endpoint implementations requiring basic-level optimization skills
- **CRITICAL**: The Node.js Express/Fastify application should be FULLY functional but performing poorly due to:
  * Clear and straightforward database inefficiencies in MongoDB queries AND
  * Simple API endpoint performance issues requiring basic analysis and optimization techniques on both fronts
- **CRITICAL**: Candidates must understand that optimizing BOTH the database AND the Node.js API endpoints is required. The task should make it clear that after fixing basic database issues (indexes, queries), they must also update the API endpoints and database query implementations in the Node.js application to properly utilize optimizations and maintain functionality. Similarly, endpoints must be refactored to eliminate obvious data processing bottlenecks and implement basic caching.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate a complete, working Node.js Express/Fastify REST API with MongoDB database that has clear performance issues suitable for basic-level engineers (0-2 years experience).
- **PROVIDE STRAIGHTFORWARD PROBLEMATIC DATABASE DESIGN AND API IMPLEMENTATIONS**: Include seed_database.js with obvious inefficient collection structures AND missing basic indexes AND straightforward relationship issues AND clearly suboptimal queries. Include API endpoints with obvious data over-fetching, basic inefficiencies, and unoptimized request/response handling.
- The question should be a real-world business scenario requiring basic-level performance optimization involving:
  * MongoDB collections with straightforward query patterns
  * Basic optimization strategies
  * Simple inefficiencies in Node.js API endpoint logic
  * NOT building from scratch
- The complexity of the optimization task and specific improvements expected from the candidate must align with basic proficiency level (0-2 years experience) requiring fundamental optimization techniques including:
  
  **MongoDB Optimization :**
  - Simple query optimization with basic $lookup operations
  - Basic indexing strategies (single field indexes, simple compound indexes)
  - Basic understanding of MongoDB query performance
  - Simple database relationship improvements
  - Performance bottleneck identification in basic operations
  - Basic MongoDB features utilization (simple aggregations, basic $match)
  - Simple filter optimization
  - Basic aggregation understanding
  - Understanding connection pooling concepts
  
  **Node.js API Endpoint Optimization :**
  - Identifying obvious N+1 query problems in endpoints
  - Simple batch data fetching
  - Basic request/response optimization
  - Implementing simple pagination in endpoints
  - Basic caching concepts and simple in-memory caching
  - Understanding async/await and basic promise handling
  - Basic middleware understanding
  - Simple error handling in endpoints
  - Understanding database connection reuse
  - Reducing redundant computations
  - Basic field selection to fetch only required data

- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to MongoDB best practices and Node.js optimization patterns for basic-level learning.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, MongoDB documentation, Node.js documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to identify and fix basic MongoDB and Node.js performance issues at a basic level. Therefore, the complexity of the optimization tasks should require genuine basic-level database and application performance engineering and problem-solving skills.
- Tasks should involve straightforward optimization challenges that require understanding of basic database concepts and simple Node.js patterns.
- Candidates will be encouraged to use AI to help with implementation but should understand the concepts being applied.

## Code Generation Instructions:
Based on the real-world scenarios provided above, create a MongoDB and Node.js optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for basic proficiency level (0-2 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for basic database and application optimization understanding.
- Tests practical basic-level MongoDB query optimization AND Node.js API endpoint performance tuning skills that require understanding of basic database concepts and simple optimization principles on both fronts.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The Node.js application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and database connection setup, but with intentionally:
  * Clear inefficient database queries requiring basic-level MongoDB optimization
  * Simple inefficient endpoint implementations requiring basic-level API optimization
- The database connection setup should use MongoDB drivers with Mongoose ODM for basic-level complexity.
- All Express/Fastify routes should be implemented and working but with:
  * Simple suboptimal database queries involving collections and basic operations
  * Straightforward inefficient endpoint logic with obvious data processing issues and basic performance problems
- The database should come with realistic sample data and intentionally straightforward poor schema design requiring basic optimization practices.
- The code files generated must be valid and executable but perform poorly due to:
  - **CRITICAL**: not to use the callback functions in the code, use the async/await pattern instead for database connections.
  * Clear database issues requiring basic-level MongoDB solutions
  * Simple API endpoint implementations requiring basic-level Node.js solutions
- **CRITICAL**: The task focuses on optimizing existing clear inefficient queries AND API endpoints, NOT building from scratch.
- For basic level proficiency: **ORM/ODM USAGE**: Use Mongoose ODM straightforwardly with simple relationships and basic queries that require basic-level optimization skills. **API ENDPOINT LOGIC**: Implement endpoints with obvious inefficiencies in data fetching, basic processing, simple caching opportunities, and unoptimized response handling that require basic-level refactoring.

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Node.js (Express or Fastify) that integrates with MongoDB using basic patterns
- MUST include a Dockerfile for the Node.js application
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- A docker-compose.yml file which contains all the applications — a docker for running the Node.js REST API and a docker for running the MongoDB database.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working API and database connection.

### Docker-compose Instructions:
  - MongoDB service with proper configuration (database, username, password, initialization)
  - Database creation with User and Password is must 
  - Node.js service with dependency on MongoDB using depends_on
  - Volume mounts for data persistence (MongoDB data directory)
  - **Volume mount for seed files** - Mount the seed files directory to MongoDB container for initialization
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - **CRITICAL**: not to use the volume in the api container because it is overwriting the NODE_MODULES folder
  - For user and password, use hardcoded values in the docker-compose.yml file
  - **INITIALIZATION APPROACH**: Use MongoDB's built-in initialization through Docker entrypoint scripts or mounted seed files
  - Node.js service should start the application with simple inefficient database queries AND basic inefficient API endpoint implementations requiring basic optimization
  - **CRITICAL**: Docker-compose handles both container orchestration AND database initialization through volume mounts

### seed_database.js instructions:
- While the JavaScript seed file must create an initial schema/collections, BUT THEY SHOULD BE STRAIGHTFORWARD INEFFICIENT with clear performance issues requiring basic-level optimization skills.
- **CRITICAL: Do not implement the solution in the seed file, create straightforward schema with clear performance issues that require basic analysis and optimization approaches suitable for basic-level candidates.**
- Include collections with straightforward relationships requiring basic optimization
- Create scenarios involving simple queries, basic aggregations, and clear filter patterns
- Include missing basic indexes, straightforward schema design issues, and simple optimization opportunities
- Seed realistic data that exposes basic performance issues

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
  + WAIT MECHANISM: Implements proper health check to wait for MongoDB service to be fully ready and accepting connections
  + VALIDATION: Validates that Node.js application is responding and connected to database
  + DATABASE SETUP: Seed files are automatically executed during MongoDB container initialization
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling for failed container starts or database connection issues
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  + SIMPLIFIED APPROACH: No manual seed file execution - MongoDB handles initialization automatically through mounted volumes

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile.  
- Instructions:
  1. Stop and remove all containers created by docker-compose.
  2. Remove all associated Docker volumes (MongoDB volume, any named volumes, and anonymous volumes).
  3. Remove all Docker networks created for the task.
  4. Force-remove all Docker images related to this task (<image_name> and mongo).
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes that are not in use.
  6. Delete the entire `/root/task/` folder where all the files (run.sh, docker-compose.yml, Dockerfile, seed files, etc.) were created, so that no project files remain.
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary).
  8. Print logs at every step (e.g., "Stopping containers...", "Removing images...", "Deleting folder...") so the user knows what is happening.
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'docker_image_name|mongo' || true) || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Node.js files (`node_modules`, `*.log`, `.npm`, `.node-gyp`) are also removed if present in `/root/task/`.
  - Remove all MongoDB data directories that were mounted via volumes (e.g., `/root/task/data/mongo`).
  - Ensure that both the custom application container and the MongoDB container are cleaned up.

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors).
  - Always use `set -e` at the top to exit on error (except when explicitly ignored).

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile for the Node.js application
  - Should use appropriate Node.js base image (node:18-alpine or similar)
  - Should install dependencies from package.json using npm or yarn
  - Should expose appropriate port for Node.js API (typically 3000 or 5000)
  - Should include proper working directory set to /root/task
  - Should include proper entry point (npm start or node server.js)
  - Must be production-ready and follow Docker best practices
  - **DO NOT use environment variables or .env files**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location

**CRITICAL**: All Docker and script references must account for the /root/task base directory.

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Node.js, MongoDB, and Express/Fastify development tasks that includes:
- Node.js files (node_modules, .npm, .node-gyp)
- Build and distribution artifacts (dist/, build/)
- IDE and editor files (.vscode/, .idea/, *.swp)
- Environment files (.env, .env.local)
- Log files (*.log, logs/)
- MongoDB data directories
- Testing artifacts (.nyc_output/, coverage/)
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for Node.js/Express/Fastify/MongoDB development

## README.md STRUCTURE (Node.js + MongoDB Optimization)

The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the MongoDB and Node.js API optimization scenario being generated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Helpful Tips
3. Database Access
4. Objectives
5. How to Verify

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a Node.js REST API with MongoDB is experiencing performance issues. Explain that the application is fully functional but suffers from clear database and API performance problems (e.g., missing indexes, inefficient queries, N+1 patterns, over-fetching, missing pagination). Connect the business problem to the need for basic-level optimization on BOTH MongoDB and Node.js API endpoints. Make clear this is a **time-bounded optimization task** focusing on specific, achievable improvements. The README.md file content MUST be fully populated with meaningful, specific content relevant to basic-level optimization for BOTH MongoDB AND Node.js API. ALL sections must have substantial content - no empty or placeholder text allowed.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider what kinds of clear performance issues exist in the MongoDB database (e.g., missing indexes, unnecessary queries, simple inefficient data fetching)
- Think about what kinds of inefficiencies exist in the Node.js API endpoints (e.g., fetching all data instead of filtering, missing pagination, redundant database calls)
- Review which parts of the database AND API might be causing slowness involving collections and basic operations
- Consider that optimization will require understanding MongoDB query performance, adding indexes, optimizing queries, and refactoring endpoint logic
- Explore simple caching strategies, response payload optimization, and eliminating obvious redundancy
- Think about basic coordination between database and API changes
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### Database Access

- Provide the database connection details (host (droplet-ip), port, database name, username, password)
- Mention that candidates can use any preferred database client tools (e.g., MongoDB Compass, mongosh) for basic performance analysis
- For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address


### Objectives

Define goals focusing on outcomes for the optimization task:

- Noticeable improvement in API endpoint response times
- Faster MongoDB query execution
- Basic multi-collection operation improvements
- Reduced data transferred by endpoints
- Implementing simple caching and eliminating obvious redundant database calls
- Adding necessary indexes to collections and improving basic query efficiency
- Simple schema improvements and API endpoint refactoring
- Basic caching strategy implementation and reducing unnecessary data fetching

**CRITICAL**: Scope should be achievable within the allocated time; objectives serve as performance benchmarks for task completion and scoring


### How to Verify
- Specific checkpoints after optimization showing noticeable improvement in performance metrics on BOTH database and API fronts
- Observable behaviors to validate basic database performance improvements through the API
- Observable behaviors to validate basic API endpoint performance improvements
- Simple methods to measure and compare before/after optimization results
- Verification of index usage and basic query efficiency
- Verification of API response times and reduced database calls

**CRITICAL**: Focus on measurable, verifiable improvements

### NOT TO INCLUDE:
- Manual deployment instructions (environment is automated via run.sh)
- Node.js implementation guides (API is already complete)
- Optimization solutions or hints for database schemas and API endpoints
- Step-by-step database connection setup (connection details are provided)
- Instructions to run run.sh (deployment is automated)
- Specific optimization solutions or code snippets
- Phrases like "you should implement", "add the following code"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 characters, mentioning BOTH MongoDB and Node.js optimization at basic level)",
   "question": "A short description of the basic-level optimization task scenario including:
   - Specific clear performance problems in the existing MongoDB database that need to be identified and resolved
   - Specific straightforward inefficiencies in the Node.js API endpoints that need to be refactored
   - What straightforward performance bottlenecks exist at both database and API levels involving collections and basic operations
   - What basic-level optimizations are needed on BOTH fronts (MongoDB queries + Node.js endpoints)",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview (MANDATORY 2-3 sentences), Helpful Tips (practical guidance without revealing implementations), Database Access (connection details and client tools), Objectives (outcomes for the optimization task), and How to Verify (measurable verification approaches)",
      ".gitignore": "Proper Node.js, Docker, and MongoDB exclusions",
      "package.json": "Node.js dependencies list including express/fastify, mongoose, mongodb, nodemon, and other basic dependencies required for basic-level ODM usage and API optimization",
      "docker-compose.yml": "Docker services for MongoDB and Node.js API (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for Node.js application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      ".env.example": "Example environment configuration file (for reference only, actual configs hardcoded in docker-compose.yml)",
      "src/server.js": "Complete Node.js Express/Fastify application entry point with basic middleware, error handling, and database connection setup",
      "src/app.js": "Main application logic with straightforward inefficient endpoint implementations requiring basic optimization",
      "src/database.js": "Complete database connection configuration using Mongoose ODM with basic patterns",
      "src/models/index.js": "Empty file for Node.js module structure",
      "src/models/models.js": "Mongoose ODM models with simple relationships but inefficient design",
      "src/routes/index.js": "Empty file for Node.js module structure",
      "src/routes/api.js": "Complete API route implementations with simple suboptimal queries AND straightforward inefficient endpoint logic needing basic-level optimization",
      "src/schemas/index.js": "Empty file for Node.js module structure",
      "src/schemas/schemas.js": "Basic validation schemas for API requests/responses",
      "src/middleware/index.js": "Empty file for Node.js module structure",
      "src/middleware/middleware.js": "Basic middleware implementations (possibly with simple inefficiencies)",
      "src/utils/index.js": "Empty file for Node.js module structure",
      "src/utils/helpers.js": "Basic helper functions and utilities (possibly with straightforward performance issues)",
      "seed_database.js": "Complete database initialization file containing both straightforward collection creation with clear performance issues AND realistic sample data insertion"
   }},
   "outcomes": "Bullet-point list in simple language. Must include: 'Optimize Node.js + MongoDB application performance by implementing efficient query patterns, basic indexing, and improving API endpoint data fetching and response handling' and 'Write production-level clean code with best practices including proper error handling, naming conventions, basic schema design, and performance optimization techniques'",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level performance problem in a business context (database and/or API), (2) the specific optimization goal at basic level, and (3) the expected outcome emphasizing maintainability and scalability.",
   "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the basic-level optimization task. Include: Node.js 16+, npm/yarn, Docker, Docker Compose, MongoDB tools (MongoDB Compass, mongosh), Git, basic query tools, Mongoose ODM knowledge, Express/Fastify basics, basic MongoDB concepts, Node.js basics, basic API concepts, postman or similar for API testing, text editor/IDE, etc.",
   "answer": "High-level solution approach focusing on basic database optimization strategies AND Node.js API endpoint optimization strategies for the given straightforward performance issues. Address both fronts equally - MongoDB query optimization with simple indexing and basic query improvements alongside Node.js endpoint refactoring with basic data fetching improvements, simple caching, and straightforward code optimization.",
   "hints": "A single line hint on what a good basic-level approach to analyze and optimize the database AND API performance could include. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward basic database analysis AND simple Node.js profiling practices suitable for basic-level skills. Example hint format: 'Look for places where the API fetches all data when only some is needed, and places where the same database query runs multiple times.'",
   "definitions": {{
      "terminology_1": "definition_1",
      "terminology_2": "definition_2"
      }}
}}
"""
PROMPT_REGISTRY = {
    "MongoDB (BASIC), NodeJs (BASIC)": [
        PROMPT_NODEJS_MONGODB_CONTEXT,
        PROMPT_NODEJS_MONGODB_INPUT_AND_ASK,
        PROMPT_NODEJS_MONGODB_OPTIMIZATION_INSTRUCTIONS,
    ]
}
