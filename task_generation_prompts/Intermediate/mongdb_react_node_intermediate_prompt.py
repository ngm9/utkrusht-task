PROMPT_FULLSTACK_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js, React.js, and MongoDB full-stack assessment task.

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
2. What will the task look like? (Describe the type of full-stack implementation or optimization required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FULLSTACK_CONTEXT ="""
## GOAL
As a full-stack architecture expert experienced in MongoDB, NodeJs, and ReactJs, you are given a list of real world scenarios and proficiency levels for full-stack development.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional full-stack application appropriate to the scenario (either with skeleton code requiring feature implementation, or with existing code requiring performance optimization).

The candidate's responsibility is to analyze the application and either BUILD complete features from the provided structure or OPTIMIZE the application across the entire stack. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a full-stack application that is either:
- A skeleton with folder structure, configuration, and empty stubs for feature implementation
- A working application with intentional inefficiencies or performance bottlenecks

In either case, the application includes MongoDB schema (documented or pre-populated), backend APIs (stubs or functional with issues), and frontend components (stubs or with performance problems). The candidate must analyze the requirements/performance issues and implement necessary changes across all layers.

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the intermediate-level full-stack scenario
- Task must provide an appropriate full-stack application structure based on the scenario requirements
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working full-stack application structure suitable for intermediate-level engineers (3-5 years experience)
- The complexity of the task and specific improvements/implementations expected from the candidate must align with intermediate proficiency level (3-5 years experience) requiring advanced techniques including:
  - MongoDB schema design, indexing strategies (compound indexes, sparse indexes, text indexes, geospatial indexes)
  - Complex aggregation pipeline design and optimization
  - MongoDB query optimization and execution plan analysis (explain())
  - Backend API design including pagination, filtering, sorting, n+1 query resolution
  - Caching strategies (in-memory caching, HTTP caching headers)
  - Asynchronous processing and background job handling
  - Connection pooling configuration
  - Backend code structure (middleware optimization, error handling)
  - React component optimization (memoization, useCallback, useMemo, code-splitting)
  - State management patterns and reducing unnecessary re-renders
  - Frontend bundle optimization and tree-shaking
  - Image optimization and lazy loading strategies
  - Network request optimization (request batching, deduplication)
  - Client-side caching strategies
  - Web vitals optimization (Core Web Vitals, Lighthouse metrics)
  - Production deployment considerations
- The question must NOT include hints about specific solutions. Hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest best practices for MongoDB, Node.js, React, and full-stack development for intermediate-level development
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, documentation, and AI-powered tools or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze and improve complex full-stack applications at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the tasks should require genuine intermediate-level full-stack engineering and advanced problem-solving skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve multi-layered challenges across database, backend, and frontend that require understanding of system architecture, query design/optimization, API design patterns, and React best practices
- Candidates will be encouraged to use AI to help with development but not replace their own thinking and diagnostic skills

## Application Generation Instructions:
Based on the real-world scenarios provided, create a full-stack task that:
- Draws inspiration from the input_scenarios given below to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced full-stack skills
- Tests practical intermediate-level full-stack skills requiring deep understanding of application architecture, query design/optimization, API design patterns, React implementation/optimization, and development principles
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided to ensure variety in task generation
- **CRITICAL**: The full-stack application should be appropriate to the scenario - either COMPLETE SKELETON with empty stubs, or FULLY POPULATED WORKING APPLICATION with intentional inefficiencies
- The application should contain proper folder structure with configuration files, database design, backend services, and frontend components as required by the scenario
- Include sample queries/API documentation demonstrating expected behavior or performance problems
- The application should expose clear requirements or bottlenecks that can be measured and improved
- **CRITICAL**: The task focuses on either implementing missing functionality from skeleton code or optimizing existing poorly performing application design, NOT building from scratch when optimization is required

## Infrastructure Requirements:
- MUST include complete application deployment using Docker Compose with MongoDB, Node.js backend, and React frontend
- A run.sh which has the end-to-end responsibility of deploying the entire full-stack infrastructure
- A docker-compose.yml file which contains MongoDB, Node.js backend, and React frontend services
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts. The task environment will be pre-deployed with working application
- A kill.sh script to completely clean up all resources

### Docker-compose Instructions:
  - MongoDB service with proper configuration (database, username, password, replica set if applicable)
  - Node.js backend service with Express.js
  - React frontend service (development or production build depending on scenario focus)
  - Database creation with User and Password is mandatory
  - Volume mounts for data persistence (MongoDB data directory, backend application files, frontend build)
  - Network configuration for inter-service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - For credentials, use hardcoded values in the docker-compose.yml file
  - **INITIALIZATION APPROACH**: Use MongoDB's built-in initialization with init scripts mounted to `/docker-entrypoint-initdb.d/` for MongoDB container, and volume mounts for backend and frontend code
  - Expose ports for MongoDB (27017), Node.js backend (5000), and React frontend (3000/3001)
  - **CRITICAL**: Docker-compose handles container orchestration AND application initialization

### Backend Application (Node.js/Express):
  - Create multiple API endpoints structured based on scenario requirements
  - Provide appropriate code implementation (empty stubs for skeleton tasks, functional code with inefficiencies for optimization tasks)
  - Routes may lack pagination, sorting, filtering optimization, or may require these features to be added based on scenario
  - Caching layers may be missing, documented, or implemented suboptimally depending on scenario
  - Error handling and logging implementation levels vary based on task requirements
  - Connection pooling may not be optimized or may require implementation based on scenario
  - Middleware stack may be incomplete or need optimization based on scenario
  - API endpoints demonstrate application state that can be either built or optimized

### Frontend Application (React):
  - Create multiple React components structured based on scenario requirements
  - Provide appropriate component implementation (empty stubs for skeleton tasks, functional components with issues for optimization tasks)
  - Routing structure may lack lazy loading or code-splitting based on scenario requirements
  - State management patterns may be incomplete or suboptimal depending on scenario
  - Bundle sizes may be large or require optimization based on scenario
  - Image assets and responsive image implementation based on scenario
  - Client-side caching strategies may be missing or need implementation based on scenario
  - Service worker integration may be absent or incomplete based on scenario
  - Components demonstrate application state appropriate to the scenario

### init_database.js instructions (MongoDB initialization):
- Create a comprehensive database schema with multiple collections (minimum 5-8 collections for intermediate level)
- Include realistic relationships between collections (references, embedded documents)
- Design the schema and data based on task scenario requirements
- Include performance optimization opportunities such as: indexing strategies, compound indexes, query optimization patterns, aggregation pipeline design, data model considerations, and efficient query patterns
- Populate collections with realistic data volumes appropriate to the scenario: lookup collections with hundreds to thousands of documents, main transactional collections with tens of thousands to hundreds of thousands of documents
- Use realistic data distributions appropriate to scenario requirements
- Include comments that describe the business context and application requirements
- Data structure should support the scenario requirements (either building new features or optimizing performance)

### Backend Code Structure:
- Place all backend code in `/backend` directory
- Include package.json with necessary dependencies (Express, MongoDB driver/Mongoose, Redis if applicable)
- Create routes in separate files organized by feature
- Include controller and service layers with implementations appropriate to scenario
- Include middleware files (auth, error handling, compression, etc.)
- Create database connection file with configuration appropriate to scenario
- Include server.js or index.js as entry point
- All code should be executable and functional with appropriate level of complexity

### Frontend Code Structure:
- Place all frontend code in `/frontend` directory
- Use Create React App or Vite setup
- Include public and src directories
- Create multiple components with implementations appropriate to scenario
- Include public directory with image assets (minimal for skeleton tasks, potentially large/unoptimized for optimization tasks)
- Create pages/routes using React Router
- Include state management (Context API or Redux) with patterns appropriate to scenario
- Include package.json with necessary dependencies
- All code should be executable and functional with appropriate level of complexity

### Run.sh Instructions:
  - PRIMARY RESPONSIBILITY: Starts all Docker containers using `docker-compose up -d`
  - WAIT MECHANISM: Implements proper health checks to wait for all services (MongoDB, backend, frontend) to be fully ready
  - VALIDATION: Validates that all services are responding and accessible
  - APPLICATION SETUP: MongoDB initialization scripts are automatically executed, backend dependencies installed, frontend built during container initialization
  - MONITORING: Monitors container status and provides feedback on successful deployment
  - ERROR HANDLING: Includes proper error handling for failed container starts or service connection issues
  - SIMPLIFIED APPROACH: No manual script execution - all services handle initialization automatically through mounted volumes

### Kill.sh Instructions:
- Purpose: The script must completely clean up everything related to the full-stack task project
- Instructions:
  1. Stop and remove all containers created by docker-compose (MongoDB, backend, frontend)
  2. Remove all associated Docker volumes (MongoDB data, any named volumes, anonymous volumes)
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task (MongoDB image, Node.js image, any custom images)
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes
  6. Delete the entire `/root/task/` folder where all files were created
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - Removal of any custom images
  - `rm -rf /root/task`

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Services for MongoDB, Node.js backend, React frontend)
  - run.sh (Script to deploy the full-stack application)
  - kill.sh (Complete cleanup script)
  - .gitignore (Ignore node_modules/, dist/, build/, .env, MongoDB data, etc.)
  - init_database.js (MongoDB initialization script with schema and data based on scenario)
  - Backend application files (server.js, routes, controllers, services, models, package.json)
  - Frontend application files (React components, pages, services, package.json, public assets)
  - sample_queries.js (Sample queries and API calls appropriate to scenario requirements)

## Code file requirements:
- All code files should be valid and executable
- Provide appropriate implementation based on scenario - either skeleton with empty stubs or fully functional application
- Include realistic business scenarios in data structures and operations
- DO NOT include any comments that give away solutions or implementation details
- The application should be immediately ready for candidate work, providing clear structure and requirements
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- Backend and Frontend code should be in separate directories under /root/task

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for full-stack development tasks that includes:
- Node.js directories (node_modules, npm-debug.log, yarn-error.log)
- MongoDB data directories
- Build outputs (dist/, build/)
- Environment files (.env, .env.local)
- IDE and editor files (.DS_Store, .vscode, .idea)
- Temporary files (*.log, *.tmp)
- OS-specific files (Thumbs.db)
- Package lock files (optional based on project preference)

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Database Access & API Configuration
   - Guidance
   - Objectives
   - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level full-stack development
- Task Overview section MUST contain the exact business scenario and clear description of what needs to be accomplished
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific full-stack scenario being generated

### Task Overview
**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing:
- The business scenario and motivation
- What needs to be accomplished (feature implementation, performance optimization, or specific improvements)
NEVER generate empty content - always provide substantial business context.

### Database Access & API Configuration
  - Provide MongoDB connection details (host, port, database name, username, password)
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>)

### Helpful Tips
- Architecture best practices and design patterns appropriate to task scenario
- Performance considerations and optimization strategies
- MongoDB schema design and query optimization approaches
- Backend API design patterns and efficiency considerations
- React component implementation and performance patterns
- State management approaches and best practices
- Testing and monitoring strategies
- Important considerations for scalability and maintainability

### Objectives
- Clear, measurable goals for full-stack development appropriate to scenario
- Feature implementation targets or performance improvement targets
- Code quality and architectural standards to achieve
- Scalability and maintainability considerations
- These objectives will be used to verify task completion and award points

### How to Verify
- Specific checkpoints and verification methods appropriate to scenario
- Performance metrics and measurement approaches
- Specific tools and commands to test implementation/optimization
- Browser DevTools approaches for frontend verification
- Backend monitoring and profiling approaches
- Code quality criteria to verify

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific implementation or optimization solutions
  - Step-by-step guides
  - Code snippets showing solutions

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words)",
   "question": "A short description of the intermediate-level full-stack task scenario including what needs to be accomplished - either building features from skeleton or optimizing performance, with specific requirements and business context",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Database Access & API Configuration, Guidance, Objectives, How to Verify",
      ".gitignore": "Proper Node.js, MongoDB, and full-stack development exclusions",
      "docker-compose.yml": "Docker services for MongoDB, Node.js backend, and React frontend (NO version specifications, NO env vars)",
      "run.sh": "Complete setup script for full-stack application deployment",
      "kill.sh": "Complete cleanup script to remove all resources",
      "init_database.js": "MongoDB initialization script with schema creation and sample data insertion",
      "backend/package.json": "Backend dependencies and scripts",
      "backend/server.js": "Express server entry point",
      "backend/routes/*.js": "API route definitions",
      "backend/controllers/*.js": "Business logic implementation",
      "backend/services/*.js": "Database service layer",
      "backend/models/*.js": "MongoDB schema definitions",
      "backend/middleware/*.js": "Custom middleware",
      "frontend/package.json": "React frontend dependencies and scripts",
      "frontend/src/App.js": "Main React component with routing",
      "frontend/src/components/*.js": "React components",
      "frontend/src/pages/*.js": "Page components",
      "frontend/src/services/api.js": "API client service",
      "frontend/public/*": "Static assets",
      "sample_queries.js": "Sample queries, API calls, and test documentation"
   }},
   "outcomes": "Bullet-point list in simple language describing measurable improvements or completed features across the full-stack application. Must include: 'Design and implement intermediate-level MongoDB schema with appropriate indexing and aggregation, integrate with a Node.js/Express backend using efficient query patterns, and build or optimize React components to deliver a performant, production-ready full-stack application' and 'Write clean, well-structured code following intermediate-level best practices: proper error handling, separation of concerns, connection pooling, query optimization, and React performance patterns'",
   "short_overview": "Bullet-point list in simple language describing: (1) the business scenario and current state of the full-stack application (what works and what is missing or slow), (2) what the candidate must build or optimize across all three layers (MongoDB schema/queries, Express API, React components), and (3) the expected outcome emphasizing production-quality, scalable, and maintainable full-stack code",
   "pre_requisites": "Bullet-point list of tools, knowledge, and environment required to complete the intermediate-level full-stack task. Include: Docker, Docker Compose, MongoDB (Compass, mongosh), Node.js 18+/Express, React (hooks, routing, state management), performance profiling tools (React DevTools, MongoDB explain()), API testing tools (Postman, curl), full-stack architecture knowledge (REST API design, database schema design, query optimization), Git for version control",
   "answer": "High-level solution approach focusing on architecture decisions, design patterns, optimization strategies, and implementation techniques across all layers appropriate to the scenario. Include specific approaches for: MongoDB schema design and indexing strategy, aggregation pipeline design, Express API structure and query optimization (pagination, filtering, N+1 resolution, caching), and React component optimization (memoization, lazy loading, state management, request deduplication).",
   "hints": "A single line hint on what a good intermediate-level approach to analyze and improve the full-stack application could include. This hint must NOT give away specific solutions, but gently nudge toward comprehensive analysis and best practices suitable for intermediate-level skills.",
   "definitions": {{
      "N+1 Query Problem": "A performance issue where an application makes one query to fetch parent records, then N additional queries to fetch related data for each parent record, resulting in N+1 total queries",
      "React Component Memoization": "Optimization technique using React.memo to prevent unnecessary re-renders of components when props haven't changed",
      "Aggregation Pipeline": "MongoDB feature that processes documents through multiple stages (match, group, sort, project) to transform and analyze data efficiently",
      "Code-Splitting": "Process of breaking JavaScript bundle into smaller chunks that are loaded on-demand, reducing initial load time",
      "Connection Pooling": "Management of database connections to reuse them instead of creating new connections for each request, improving performance"
   }},
   "criterias": [
      {{"name": "React Framework", "proficiency": "INTERMEDIATE", "competency_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p"}},
      {{"name": "NodeJs", "proficiency": "INTERMEDIATE", "competency_id": "f4a2e937-b85b-4b81-b28b-8f6b49d9599c"}},
      {{"name": "MongoDB", "proficiency": "INTERMEDIATE", "competency_id": "11987eb0-6be9-45ff-9193-295be37d17a1"}}
   ]
}}

"""

PROMPT_FULLSTACK_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements for this intermediate-level full-stack engineering position?
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), NodeJs (INTERMEDIATE), React Framework (INTERMEDIATE)": [
        PROMPT_FULLSTACK_INTERMEDIATE_CONTEXT,
        PROMPT_FULLSTACK_INPUT_AND_ASK,
        PROMPT_FULLSTACK_CONTEXT,
    ]
}
