PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company, product context, and role expectations, especially for an intermediate engineer working across a React frontend, Node.js API, and MongoDB-backed application?
"""

PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a MongoDB, Node.js, and React Framework assessment task.

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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- The generated task must involve all three competencies in a meaningful way: React frontend behavior, Node.js backend/API logic, and MongoDB query/schema/index usage

Before proceeding to the full task generation, briefly state:
1. Which scenario you selected and why it best fits a full-stack MongoDB + Node.js + React intermediate task
2. What the candidate will be asked to analyze, improve, or implement across frontend, backend, and database layers

Then immediately continue with the complete task output in the required JSON structure. Do NOT stop for confirmation.
"""

PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in MongoDB, Node.js, and React-based product development, you are given a list of real-world scenarios and proficiency levels for these competencies.
Your job is to generate an entire assessment task definition for an INTERMEDIATE candidate that evaluates practical full-stack problem solving in an existing MERN-style application.

The task must produce a COMPLETE, WORKING application and infrastructure setup where the candidate improves or extends an already functional system. The candidate should work across:
- React frontend behavior and data rendering
- Node.js REST API logic and application structure
- MongoDB schema/query/index usage through Mongoose

The task must be realistic for an intermediate engineer and completable within {minutes_range} minutes total.

## HARD SCOPE BOUNDARIES
Use the competency scopes as the source of truth.

### MongoDB scope that IS appropriate here
You MAY require intermediate MongoDB skills such as:
- Designing or refining document structure using embedded vs referenced documents where naturally relevant
- CRUD operations and aggregation pipelines using operators such as $match, $project, $group, $lookup, $facet, $bucket, $reduce, and pagination-friendly query patterns
- Update operators and arrayFilters where relevant to the business flow
- Query optimization using explain plans, early $match, covered-query thinking, and range/seek or standard paginated access patterns
- Index design and tuning using compound, multikey, partial, sparse, TTL, or hidden indexes when naturally justified by the scenario
- Mongoose ODM usage in application code
- JSON-schema-style validation concepts if reflected through schema validation or Mongoose validation

### MongoDB scope that must NOT be primary in this task
Do NOT make the task primarily about:
- Replica set administration, elections, step-downs, rollback drills
- Sharded cluster operations, balancer tuning, reshardCollection
- LDAP/x.509/FLE/FIPS/VPC configuration
- Backup/restore operations, PITR, Ops Manager, Atlas administration
- Kubernetes, Terraform, Ansible, Helm, or infrastructure automation as the main skill being assessed
- Change streams, tailable cursors, or advanced operational observability as the core requirement unless only mentioned lightly in context

### Node.js scope that IS appropriate here
You MAY require:
- Express-based REST API development
- Routing, middleware, validation, error handling
- Async/await, event loop awareness, Promise coordination
- Mongoose data modeling and database interaction
- Separation of concerns for maintainability
- Lightweight caching such as in-memory or Redis if included in a simple, bounded way
- Authentication/authorization only if it is already present and not the main challenge
- Structured logging, testing, and performance tuning at an intermediate level

### React Framework scope usage
The task MUST include meaningful React work, but keep it aligned to intermediate application development rather than a pure frontend optimization exercise. Appropriate asks include:
- Building or fixing a data-driven page/component connected to the API
- Managing loading, error, empty, and success states
- Implementing pagination, filters, or summary views
- Refactoring component structure for maintainability
- Avoiding obviously wasteful client behavior such as fetching too much data or duplicating requests
- Basic-to-intermediate React hooks usage and state management

Do NOT turn this into a purely advanced React performance internals task.

## TASK SHAPE
The candidate must receive a FULLY FUNCTIONAL app-and-db project with Dockerized infrastructure.
The project should boot successfully and expose:
- A Node.js API service
- A MongoDB database service
- A React frontend service

The codebase should already work, but contain a bounded set of realistic issues or missing capabilities that require intermediate full-stack reasoning.

The task should be inspired by ONE scenario from the provided real-world scenarios and should usually be one of these patterns:
- Balanced optimization task across frontend, API, and database
- Feature completion task with existing but incomplete/inefficient implementation
- Bug-fix plus performance-improvement task in a realistic business workflow

## INTERMEDIATE DIFFICULTY CALIBRATION
This is INTERMEDIATE level, so the task should involve 4-5 connected concepts and require architectural judgment, but remain solvable in under an hour.

Appropriate complexity includes combinations like:
- MongoDB aggregation + compound indexes + API pagination + React data table integration
- Mongoose schema refinement + backend validation/error handling + React workflow completion
- Reducing redundant backend queries + adding projection/pagination + frontend summary/dashboard updates
- Implementing a business flow with transactional thinking at application level, while keeping database work within normal Mongoose/MongoDB intermediate usage

Do NOT require:
- Microservices
- Advanced distributed systems design
- Heavy security hardening as the main task
- Complex concurrency control beyond normal async/await and request handling
- Large-scale infra administration

## REQUIRED TASK STYLE
The task must be framed as an existing production-like application that is already running but needs targeted improvement.
The candidate should not build the whole app from scratch.

Good examples of acceptable task focus:
- A fintech dashboard where transaction history is slow and the account summary page is incomplete
- A logistics operations dashboard where shipment listing loads too much data and the frontend lacks server-driven pagination
- A marketplace admin tool where order search and summary views are inconsistent because of inefficient API/database access patterns
- A SaaS operations console where a reporting endpoint and corresponding React page need better aggregation, filtering, and rendering behavior

## INFRASTRUCTURE CATEGORY: APP_AND_DB
You MUST generate an APP_AND_DB task.
That means the output JSON must define a project with:
- Dockerfile for the Node.js/React application setup or separate app containers if you choose a multi-container frontend/backend arrangement
- docker-compose.yml
- MongoDB database container
- Application code using a web framework on the backend
- React frontend code

Because this is APP_AND_DB, the generated code_files must include both app code and DB initialization/seed files.

## TECHNOLOGY EXPECTATIONS
Use a practical MERN-style stack:
- Backend: Node.js 18+, Express, Mongoose
- Frontend: React 18 with Vite or Create React App
- Database: MongoDB
- Containerization: Docker and docker-compose

A simple structure is preferred, for example:
- backend/...
- frontend/...
- docker-compose.yml
- run.sh
- kill.sh
- seed_database.js

You may also choose a single repository with separate frontend and backend folders.

## STARTER CODE REQUIREMENTS
The starter project must be complete and executable.
It must include:
- A working backend API with existing routes
- A working React frontend with at least one page relevant to the task
- A MongoDB seed file with realistic sample data
- Existing Mongoose models and schema definitions
- Existing but suboptimal or incomplete implementation that the candidate must improve

The starter code must NOT contain comments that reveal the solution.
Do NOT include TODO comments that directly tell the candidate what to change.
Do NOT leave the app broken on startup.

## WHAT THE CANDIDATE SHOULD TYPICALLY DO
Depending on the selected scenario, the candidate may need to do a balanced subset of the following:
- Improve a MongoDB query or aggregation pipeline used by a key endpoint
- Add or refine indexes that support the actual access pattern
- Refactor a Node.js endpoint to reduce redundant queries or payload size
- Add validation and clearer error handling for a business workflow
- Implement server-side pagination/filtering/sorting for a list endpoint
- Update the React frontend to consume the improved API correctly
- Build or fix a summary component, table, or detail view
- Handle loading/error/empty states in the UI
- Keep the code modular and production-like

## MONGODB-SPECIFIC GUIDANCE
If the task uses MongoDB optimization, keep it within intermediate application-facing scope. Suitable patterns include:
- Aggregation pipelines with $match, $lookup, $group, $project, $facet
- Pagination using skip/limit or seek/range patterns where appropriate
- Compound indexes aligned to filter + sort patterns
- Projection to reduce payload size
- Embedded vs referenced document trade-offs only where directly relevant to the scenario
- explain()-driven reasoning mentioned in verification or hints, not as an ops-heavy requirement

Do NOT require cluster administration or operational runbooks as the main deliverable.

## NODE.JS-SPECIFIC GUIDANCE
Suitable backend expectations include:
- Express route/controller/service separation
- Async/await-based data access
- Request validation and consistent API responses
- Error handling middleware
- Lightweight caching only if bounded and easy to reason about
- Jest-based tests if included, but keep testing scope moderate and focused

## REACT-SPECIFIC GUIDANCE
Suitable frontend expectations include:
- A page or dashboard that consumes the backend API
- Hooks-based data fetching
- Pagination/filter controls
- Summary cards or detail panels
- Clear UX states for loading, empty, and error
- Reasonable component decomposition

Avoid requiring advanced frontend architecture migrations.

## DOCKER / DEPLOYMENT REQUIREMENTS
The environment is automated and pre-deployed for the candidate.

### docker-compose.yml
- MUST NOT include a version field
- MUST use hardcoded values rather than .env references
- MUST include MongoDB service
- MUST include backend service
- MUST include frontend service
- MUST define service dependencies so startup is reliable
- MUST expose ports for frontend and backend
- MUST include MongoDB initialization via mounted seed files or startup command
- MUST avoid mounting a frontend/backend source volume in a way that breaks installed dependencies

### run.sh
- Must use bash and set -e
- Must start the full stack with docker-compose up -d --build or equivalent
- Must wait for MongoDB to be ready
- Must validate backend health
- Must validate frontend availability
- Must print useful status messages
- Must assume files live under /root/task

### kill.sh
- Must use bash and set -e
- Must clean up containers, volumes, networks, and related images
- Must be idempotent using || true where appropriate
- Must remove /root/task at the end
- Must print progress logs

### Dockerfiles
- Must be valid and production-like
- Must set WORKDIR to /root/task or appropriate subdirectory under it
- Must not rely on .env files

## README REQUIREMENTS
The generated README.md must contain these sections:
1. Task Overview
2. Objectives
3. How to Verify
4. Database Access
5. Helpful Tips

### README Task Overview
Must contain 3-4 substantial sentences describing:
- The business scenario
- The current application behavior
- The fact that the app works but has inefficiencies or incomplete behavior
- Why the candidate must improve frontend, backend, and database interaction

### README Objectives
Must describe outcomes, not implementation steps.
Examples of acceptable objective framing:
- Ensure key list/reporting endpoints return correct paginated results under realistic data volume
- Improve the consistency and responsiveness of the related React workflow
- Reduce unnecessary database and API work while preserving correctness
- Maintain clean, modular, production-ready code

### README How to Verify
Must include measurable or observable checks such as:
- Endpoint behavior before/after
- Pagination/filter correctness
- Reduced payload size or improved response time
- Correct rendering in the React UI
- Index usage or explain-plan improvement where relevant

### README Database Access
Must include:
- Host: <DROPLET_IP>
- Port
- Database name
- Username
- Password
- Mention that tools like MongoDB Compass or mongosh may be used

### README Helpful Tips
Must use bullets starting with words like:
- Consider
- Think about
- Explore
- Review
- Analyze

Tips must guide discovery without revealing the exact fix.

## REQUIRED OUTPUT JSON STRUCTURE
Your generated task must output valid JSON with this shape:

{
  "name": "Short task name under 50 words",
  "question": "Candidate-facing scenario and ask",
  "code_files": {
    "README.md": "...",
    ".gitignore": "...",
    "docker-compose.yml": "...",
    "run.sh": "...",
    "kill.sh": "...",
    "backend/Dockerfile": "...",
    "backend/package.json": "...",
    "backend/src/server.js": "...",
    "backend/src/app.js": "...",
    "backend/src/database.js": "...",
    "backend/src/models/index.js": "...",
    "backend/src/models/models.js": "...",
    "backend/src/routes/index.js": "...",
    "backend/src/routes/api.js": "...",
    "backend/src/middleware/index.js": "...",
    "backend/src/middleware/middleware.js": "...",
    "backend/src/utils/index.js": "...",
    "backend/src/utils/helpers.js": "...",
    "frontend/Dockerfile": "...",
    "frontend/package.json": "...",
    "frontend/index.html": "...",
    "frontend/src/main.jsx": "...",
    "frontend/src/App.jsx": "...",
    "frontend/src/components/...": "...",
    "frontend/src/hooks/...": "...",
    "frontend/src/pages/...": "...",
    "frontend/src/utils/...": "...",
    "seed_database.js": "..."
  },
  "outcomes": "Bullet-point list in simple language",
  "short_overview": "Bullet-point list in simple language",
  "pre_requisites": "Bullet-point list",
  "answer": "High-level solution approach",
  "hints": "Single-line hint",
  "definitions": {
    "term": "definition"
  }
}

## CODE FILE EXPECTATIONS
- The project must be runnable as provided
- The backend must be fully functional but contain bounded inefficiencies or incomplete business behavior
- The frontend must render and interact with the backend successfully
- The database must be seeded with realistic data volumes sufficient to expose the issue
- Use Mongoose for MongoDB access
- Use async/await rather than callbacks
- Keep the code quality realistic and production-like
- Do not include comments that reveal the answer

## CALIBRATION FROM SIMILAR TASKS
Use the similar tasks as complexity calibration:
- A balanced MERN task is appropriate
- Server-side pagination is a strong fit
- Aggregation-based transaction/reporting endpoints are a strong fit
- React should not be decorative; it must consume and reflect the backend improvements
- The task should feel like optimizing or completing a real business workflow, not solving isolated toy bugs

## GOOD TASK PATTERNS FOR THIS COMBINATION
Strong examples include:
- Fintech account summary + transaction history with aggregation, pagination, and React summary page
- Logistics shipment dashboard with server-side filtering/pagination and React table integration
- Marketplace order reporting with summary cards and efficient backend aggregation
- SaaS operations dashboard with list endpoint optimization and frontend state handling

## WHAT TO AVOID
- Pure database administration tasks
- Pure frontend-only optimization tasks
- Building a whole app from scratch
- Requiring advanced infra/security operations as the main challenge
- Requiring microservices or event-driven architecture

## FINAL REMINDERS
1. Use exactly one selected scenario from the provided real-world scenarios
2. Keep the task within INTERMEDIATE scope and {minutes_range} minutes
3. Ensure all three competencies are meaningfully exercised
4. Keep MongoDB work application-facing, not ops-heavy
5. Produce a complete APP_AND_DB task with Docker, backend, frontend, and seed data
6. Output valid JSON only in the generated task body
7. Do not include markdown fences
"""

PROMPT_REGISTRY = {
    "MongoDB (INTERMEDIATE), NodeJs (INTERMEDIATE), React Framework (INTERMEDIATE)": [
        PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_CONTEXT,
        PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_MONGODB_NODEJS_REACT_FRAMEWORK_INTERMEDIATE_INSTRUCTIONS,
    ]
}