PROMPT_NODEJS_MONGODB_INTERMEDIATE_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (intermediate: 3–5 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of Node.js and MongoDB optimization required, the expected deliverables, and how it aligns with the intermediate proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_MONGODB_INTERMEDIATE_CONTEXT = """
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
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional REST API and some initial schema but with subtle performance issues that require intermediate-level database optimization skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL Node.js Express/Fastify REST API application that is already connected to MongoDB with existing schema and data. The Node.js application includes:
- Complete REST API endpoints with business logic implemented but with subtle inefficiencies in database queries AND/OR API endpoint performance issues requiring intermediate-level optimization
- Full database connection and configuration setup
- All necessary middleware, error handling, and response formatting
- Complete database models and API schemas
- Pre-populated database with realistic data and intentionally subtle inefficient queries/schema design that demand intermediate problem-solving

**CRITICAL - SCENARIO-BASED OPTIMIZATION**:
The optimization requirements will VARY BASED ON INPUT_SCENARIO:
- **Database-Heavy Scenarios**: Focus primarily on MongoDB optimization (schema design, indexing, query optimization) with minimal API changes
- **API-Heavy Scenarios**: Focus primarily on Node.js API optimization (endpoint refactoring, caching, architectural patterns) with minimal database changes
- **Balanced Scenarios**: Require optimization across both database and API layers

The candidate's responsibility is to fix issues according to the task requirements and then make any code changes in the app to support the fixes. A part of the task completion is to watch the candidate implement MongoDB optimization best practices alongside Node.js API endpoint optimization and improve application performance at an intermediate level (2-5 years experience).

**CRITICAL NODE.JS API OPTIMIZATION REQUIREMENT**: Depending on the scenario, candidates may need to optimize:
- Identifying and removing unnecessary database queries in endpoints
- Adding compound indexes to speed up complex database queries
- Implementing caching strategies at API level
- Optimizing data processing and response structures
- Adding pagination to endpoints returning large datasets
- Implementing error handling improvements
- Refactoring async/await patterns
- Reducing redundant computations in endpoint logic
- Optimizing middleware execution
- Improving request validation

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the intermediate-level optimization scenario
- Task must provide a working application with existing database schema, data, and intentionally subtle suboptimal queries/database design/API endpoint implementations requiring intermediate-level optimization skills
- **CRITICAL**: The Node.js Express/Fastify application should be FULLY functional but performing poorly due to subtle issues aligned with the scenario focus
- **SCENARIO-DRIVEN**: The task focus MUST align with the input_scenario provided:
  * **Database-Focused**: Emphasize MongoDB optimization (schema, indexes, queries, aggregations)
  * **API-Focused**: Emphasize Node.js endpoint optimization (caching, architecture, data processing)
  * **Balanced**: Emphasize both database and API optimization equally
- **CRITICAL**: Candidates must understand that optimization scope depends on the scenario - whether it's primarily database work, primarily API work, or both
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate a complete, working Node.js Express/Fastify REST API with MongoDB database that has subtle performance issues suitable for intermediate-level engineers (2-5 years experience).
- **PROVIDE SUBTLE PROBLEMATIC DATABASE DESIGN AND/OR API IMPLEMENTATIONS**: Include seed_database.js with subtle inefficient collection structures AND/OR missing indexes AND/OR subtle relationship issues AND/OR suboptimal queries. Include API endpoints with subtle inefficiencies and performance bottlenecks aligned with scenario focus.
- The question should be a real-world business scenario requiring intermediate-level performance optimization involving:
  * MongoDB collections with subtle query patterns
  * Intermediate optimization strategies
  * Subtle inefficiencies in Node.js API endpoint logic (if scenario requires)
  * NOT building from scratch
- The complexity of the optimization task and specific improvements expected from the candidate must align with intermediate proficiency level (2-5 years experience) requiring intermediate optimization techniques including:
  
  **MongoDB Optimization (Intermediate) - FOR DATABASE-FOCUSED SCENARIOS:**
  - Complex query optimization with $lookup operations and aggregation pipelines
  - Advanced indexing strategies (compound indexes, partial indexes)
  - Query plan analysis and optimization using explain()
  - Schema design patterns (embedding vs referencing decisions)
  - Performance bottleneck identification in complex operations
  - Aggregation framework optimization
  - Data denormalization strategies
  - Optimizing aggregation performance
  - Connection pooling configuration
  - Working with large datasets and implementing efficient pagination
  - Implementing efficient search functionality
  
  **Node.js API Endpoint Optimization (Intermediate) - FOR API-FOCUSED SCENARIOS:**
  - Identifying and resolving N+1 query problems across multiple endpoints
  - Implementing efficient batch data fetching strategies
  - Advanced request/response optimization techniques
  - Implementing cursor-based and offset pagination strategies
  - Multi-layer caching architecture (in-memory caching patterns)
  - Advanced async/await patterns and Promise.all optimizations
  - Middleware optimization
  - Error handling patterns
  - Database connection management
  - Implementing data streaming for large responses
  - Query result projection and selective field loading
  - Implementing efficient sorting and filtering mechanisms
  - Request validation optimization
  - Response compression and payload optimization
  
  **IMPORTANT**: The actual optimization requirements will be determined by input_scenario. NOT all tasks require all these techniques.

- The question must NOT include hints about the specific optimizations needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to MongoDB best practices and Node.js optimization patterns for intermediate-level learning.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, MongoDB documentation, Node.js documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to identify and fix subtle MongoDB and Node.js performance issues at an intermediate level. Therefore, the complexity of the optimization tasks should require genuine intermediate-level database and application performance engineering and problem-solving skills.
- Tasks should involve subtle optimization challenges that require understanding of intermediate database concepts and intermediate Node.js patterns.
- Candidates will be encouraged to use AI to help with implementation but should understand the concepts being applied.

## Code Generation Instructions:
Based on the real-world scenarios provided above, create a MongoDB and Node.js optimization task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements AND the optimization focus area
- Matches the complexity level appropriate for intermediate proficiency level (2-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for intermediate database and application optimization understanding.
- Tests practical intermediate-level MongoDB query optimization AND/OR Node.js API endpoint performance tuning skills based on scenario focus
- Time constraints: Each task should be finished within 30-40 minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The Node.js application should be COMPLETE and FULLY FUNCTIONAL with all endpoints, middleware, error handling, and database connection setup, but with intentionally:
  * Subtle inefficient database queries requiring intermediate-level MongoDB optimization (for database-focused scenarios)
  * Subtle inefficient endpoint implementations requiring intermediate-level API optimization (for API-focused scenarios)
  * Both (for balanced scenarios)
- The database connection setup should use MongoDB drivers with Mongoose ODM for intermediate-level complexity.
- All Express/Fastify routes should be implemented and working but with:
  * Subtle suboptimal database queries involving collections and intermediate operations (for database-focused scenarios)
  * Subtle inefficient endpoint logic with performance problems (for API-focused scenarios)
- The database should come with realistic sample data and intentionally subtle poor schema design requiring intermediate optimization practices.
- The code files generated must be valid and executable but perform poorly due to:
  - **CRITICAL**: not to use the callback functions in the code, use the async/await pattern instead for database connections.
  * Subtle database issues requiring intermediate-level MongoDB solutions (for database-focused)
  * Subtle API endpoint implementations requiring intermediate-level Node.js solutions (for API-focused)
- **CRITICAL**: The task focuses on optimizing existing subtle inefficient queries AND/OR API endpoints, NOT building from scratch.
- For intermediate level proficiency: **ORM/ODM USAGE**: Use Mongoose ODM with intermediate relationships and queries that require intermediate-level optimization skills. **API ENDPOINT LOGIC**: Implement endpoints with subtle inefficiencies that require intermediate-level refactoring (based on scenario).

## Infrastructure Requirements:
- MUST include a complete, fully functional REST API structure using Node.js (Express or Fastify) that integrates with MongoDB using intermediate patterns
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
  - Node.js service should start the application with subtle inefficient database queries AND/OR subtle inefficient API endpoint implementations requiring intermediate optimization based on scenario
  - **CRITICAL**: Docker-compose handles both container orchestration AND database initialization through volume mounts

### seed_database.js instructions:
- While the JavaScript seed file must create an initial schema/collections, BUT THEY SHOULD BE SUBTLY INEFFICIENT with performance issues requiring intermediate-level optimization skills.
- **CRITICAL: Do not implement the solution in the seed file, create subtle schema with performance issues that require intermediate analysis and optimization approaches suitable for intermediate-level candidates.**
- Include collections with subtle relationships requiring intermediate optimization (for database-focused scenarios)
- Create scenarios involving intermediate queries, aggregations, and subtle filter patterns
- Include missing intermediate indexes, subtle schema design issues, and intermediate optimization opportunities
- Seed realistic data that exposes intermediate performance issues

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

## README.md INSTRUCTIONS

The README.md contains the following sections:
1. Task Overview
2. Objectives
3. How to Verify
4. Database Access
5. Helpful Tips
The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level optimization challenges. **CRITICAL**: The optimization focus (database-heavy, API-heavy, or balanced) MUST align with the input_scenario provided. Task Overview section MUST contain the exact business scenario and subtle performance problems that need intermediate-level optimization. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the specific optimization scenarios based on input_scenario. Use concrete business context explaining subtle performance bottlenecks requiring intermediate optimization techniques.

### README.md STRUCTURE (Node.js + MongoDB Intermediate Optimization)

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a Node.js REST API integrated with MongoDB is experiencing subtle performance issues. Explain that the application is fully functional but has subtle inefficiencies requiring intermediate-level optimization (e.g., suboptimal queries, missing indexes, N+1 patterns, redundant API logic). Connect the business problem to the need for optimization. State the optimization focus (database-heavy, API-heavy, or balanced) based on input_scenario. Make clear what subtle performance problems the candidate must identify and resolve. NEVER generate empty content; always provide substantial business context that explains what the candidate is working on and why intermediate optimization is crucial.

### Helpful Tips

Practical guidance without revealing specific implementations:

- Consider structuring Express/Fastify layers so routing, controllers, services, and data access remain isolated and easy to evolve
- Think about how asynchronous operations interact across the event loop, especially when coordinating MongoDB transactions or long-running jobs
- Explore using dependency injection or lightweight composition to keep modules testable without coupling to infrastructure details
- Review error propagation from the database driver up through API responses to guarantee consistent logging and client feedback
- Analyze how query patterns, indexes, and schema design choices affect performance under concurrent workloads
- Consider strategies that keep repositories and service modules mockable for unit and integration testing
- Think about leveraging modern Node.js language features (e.g., async/await, top-level await) for clarity without sacrificing performance
- Explore resilience techniques such as connection pooling, retries with backoff, and circuit breakers around MongoDB access
- Review opportunities to encapsulate shared logic (validation, caching, serialization) into reusable modules
- Analyze how to organize the project into domain-aligned folders (routes, services, models, utilities) that communicate intent
- Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Analyze"

### Database Access

- Provide the database connection details (host (droplet-ip), port, database name, username, password)
- Mention that candidates can use any preferred database client tools (e.g., MongoDB Compass, mongosh) for performance analysis
- For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>) rather than an actual IP address

### Objectives

Define goals focusing on outcomes for the intermediate-level optimization task:

- Clear, measurable goals appropriate for intermediate level (2-5 years experience)
- What the candidate should achieve to complete the task successfully
- Functional requirements, expected behavior, and architectural qualities
- Focus on both functional requirements and code quality metrics
- Expectations for modular project structure, API design, and performance
- Frame objectives around outcomes rather than specific technical implementations
- Guide candidates to think about: scalability, maintainability, performance, testability, extensibility

**CRITICAL**: Objectives describe the "what" and "why", never the "how"

### How to Verify

- Specific checkpoints after optimization showing improvement in performance metrics based on scenario focus
- Observable behaviors to validate intermediate database performance improvements through the API (for database-focused)
- Observable behaviors to validate intermediate API endpoint performance improvements (for API-focused)
- Methods to measure and compare before/after optimization results
- Verification of index usage and query efficiency (for database-focused)
- Verification of API response times and reduced database calls (for API-focused)

**CRITICAL**: Focus on measurable, verifiable improvements

### NOT TO INCLUDE:

- Step-by-step implementation instructions
- Exact code solutions or optimization hints
- Manual deployment instructions (environment is automated via run.sh)
- Node.js implementation guides (API is already complete)
- Step-by-step database connection setup (connection details are provided in Database Access)
- Instructions to run run.sh (deployment is automated)
- Specific optimization solutions (candidates must analyze and implement)
- Code snippets or solution code
- Phrases like "you should implement", "add the following code"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words, mentioning MongoDB and/or Node.js optimization at intermediate level based on scenario)",
   "question": "A description of the intermediate-level optimization task scenario including:
   - **SCENARIO-SPECIFIC**: Clearly state the optimization focus based on input_scenario (database-heavy, API-heavy, or balanced)
   - Specific subtle performance problems that need to be identified and resolved, aligned with the scenario focus
   - What subtle performance bottlenecks exist based on the scenario type
   - What intermediate-level optimizations are needed aligned with the scenario focus",
   "code_files": {{
      "README.md": "Candidate-facing README following structure below (Task Overview, Helpful Tips, Database Access, Objectives, How to Verify, NOT TO INCLUDE)",
      ".gitignore": "Proper Node.js, Docker, and MongoDB exclusions",
      "package.json": "Node.js dependencies list including express/fastify, mongoose, mongodb, nodemon, and other intermediate dependencies required for intermediate-level ODM usage and API optimization",
      "docker-compose.yml": "Docker services for MongoDB and Node.js API (NO version specifications, NO env vars)",
      "Dockerfile": "Docker configuration for Node.js application",
      "run.sh": "Complete setup script for database and API deployment (for environment setup only)",
      "kill.sh": "Complete cleanup script to remove all resources created by the task",
      ".env.example": "Example environment configuration file (for reference only, actual configs hardcoded in docker-compose.yml)",
      "src/server.js": "Complete Node.js Express/Fastify application entry point with intermediate middleware, error handling, and database connection setup",
      "src/app.js": "Main application logic with subtle inefficient implementations requiring intermediate optimization based on scenario",
      "src/database.js": "Complete database connection configuration using Mongoose ODM with intermediate patterns",
      "src/models/index.js": "Empty file for Node.js module structure",
      "src/models/models.js": "Mongoose ODM models with intermediate relationships but subtle inefficient design (for database-focused scenarios)",
      "src/routes/index.js": "Empty file for Node.js module structure",
      "src/routes/api.js": "Complete API route implementations with subtle suboptimal queries AND/OR subtle inefficient endpoint logic needing intermediate-level optimization based on scenario",
      "src/schemas/index.js": "Empty file for Node.js module structure",
      "src/schemas/schemas.js": "Intermediate validation schemas for API requests/responses",
      "src/middleware/index.js": "Empty file for Node.js module structure",
      "src/middleware/middleware.js": "Intermediate middleware implementations (possibly with subtle inefficiencies for API-focused scenarios)",
      "src/utils/index.js": "Empty file for Node.js module structure",
      "src/utils/helpers.js": "Intermediate helper functions and utilities (possibly with subtle performance issues)",
      "seed_database.js": "Complete database initialization file containing both subtle collection creation with performance issues AND realistic sample data insertion"
   }},
   "outcomes": "Bullet-point list in simple language. Must include: 'Optimize Node.js + MongoDB application performance by implementing advanced query optimization, indexing strategies, refactoring API endpoint logic, and applying intermediate patterns for scalability' and 'Write production-level clean code with best practices including proper architecture for scalability, comprehensive error handling, and performance optimization techniques' and 'Demonstrate ability to analyze performance bottlenecks (database and/or API based on scenario focus), make architectural decisions, and balance trade-offs between different optimization approaches'",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level performance problem in a business context affecting database and/or API layers (aligned with scenario focus), (2) the specific optimization goals requiring intermediate-level changes, (3) the expected outcome emphasizing maintainability, scalability, and production-readiness, and (4) the analytical approach needed to prioritize optimization efforts.",
   "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the intermediate-level optimization task. Include: Node.js 16+, npm/yarn, Docker, Docker Compose, MongoDB tools (MongoDB Compass, mongosh), Git, query analysis tools, Mongoose ODM knowledge, Express/Fastify intermediate knowledge, intermediate MongoDB concepts, intermediate Node.js concepts, intermediate API concepts, postman or similar for API testing, text editor/IDE, etc.",
   "answer": "High-level solution approach focusing on intermediate optimization strategies aligned with input_scenario focus. For database-focused: emphasize MongoDB optimization (indexing, query optimization, schema improvements). For API-focused: emphasize Node.js optimization (caching, endpoint refactoring, data fetching improvements). For balanced: address both appropriately.",
   "hints": "A single line hint on what a good intermediate-level approach to analyze and optimize could include, aligned with scenario focus. These hints must NOT give away the specific optimizations needed, but gently nudge the candidate toward intermediate analysis practices. Example hint format: 'Look for opportunities to reduce database queries and consider how data structures support the access patterns.' (balanced) or 'Examine query execution patterns to identify optimization opportunities.' (database-focused) or 'Review how endpoints fetch and process data for efficiency gains.' (API-focused)",
   "definitions": {{
      "terminology_1": "definition_1",
      "terminology_2": "definition_2"
      ...
   }}
}}
"""
PROMPT_REGISTRY = {}
