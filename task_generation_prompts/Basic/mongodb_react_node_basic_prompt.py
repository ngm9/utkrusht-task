PROMPT_FULLSTACK_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_FULLSTACK_BASIC_INPUT_AND_ASK = """
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
2. What will the task look like? (Describe the type of full-stack implementation required, the expected deliverables, and how it aligns with the BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_FULLSTACK_BASIC = """
# Node.js + React.js + MongoDB Full-Stack Task Requirements (BASIC Level)

## GOAL
As a full-stack architect experienced in MongoDB, Node.js, and React.js, you are given real-world scenarios and proficiency levels for full-stack development. Your job is to generate a complete task definition — including working starter code, Docker infrastructure, and README — that a BASIC-level candidate can use to demonstrate their ability to connect a React frontend to a Node.js/Express backend backed by MongoDB.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a full-stack application skeleton with:
- A running MongoDB instance with seed data already loaded
- A Node.js/Express backend with route stubs that return mock or empty data
- A React frontend with component stubs that are not yet wired to the real API

The candidate's job is to:
1. Replace mock/stub data in the Express controllers with real MongoDB queries using Mongoose
2. Wire up the React components to call the real backend API endpoints
3. Ensure end-to-end data flows correctly from MongoDB → Express → React UI

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 characters and clearly describe the basic-level full-stack scenario
- Generate a full-stack skeleton appropriate for BASIC proficiency level (1-2 years experience)
- The question scenario must be clear with accurate business context, company names, and relevant domain details
- The complexity MUST align with BASIC proficiency (1-2 years experience):
  - Simple MongoDB CRUD operations using Mongoose (find, findById, save, findByIdAndUpdate, findByIdAndDelete)
  - Basic query filtering and simple sorting (no complex aggregation pipelines)
  - Basic indexes (single-field indexes only, no compound or sparse indexes)
  - Simple Express routes with basic middleware (body parsing, CORS, basic error handling)
  - Simple React functional components using useState and useEffect hooks
  - Basic fetch or Axios calls from React to the Express API
  - Basic form handling and controlled components
  - No Redux, no Context API complexity, no advanced React patterns
  - No caching, no background jobs, no connection pooling concerns
- The task must NOT include hints about specific solutions — hints go in the "hints" field
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a BASIC level candidate

### What the Skeleton Must Include
- A complete, running React application that renders placeholder/mock UI (hardcoded arrays, empty states)
- A complete, running Node.js/Express server with route stubs returning mock JSON arrays or empty responses
- A running MongoDB container pre-seeded with realistic sample documents
- Mongoose models already defined (candidate does NOT need to redesign the schema)
- React components already structured (candidate wires them to real data, not redesigns them)
- Docker Compose configuration that starts all three services correctly
- CRITICAL: The basic setup MUST be completely working and running out-of-the-box. Frontend, backend, and database must all start without errors.
- CRITICAL: Ensure NO required boilerplate files are missing. (e.g., `public/index.html` and `src/index.js` for React, `server.js` for Express).

### What the Candidate Must Implement
- Replace mock data in Express controllers with real Mongoose queries (2-3 endpoints maximum)
- Connect React components to the real API using fetch or Axios (2-3 components maximum)
- Implement basic error handling for API calls on the frontend (loading states, error messages)
- Add one basic single-field MongoDB index relevant to the most common query

### Task Complexity Requirements for BASIC Level

**APPROPRIATE for 30-45 minute BASIC tasks:**
- Implementing a GET endpoint that queries a single MongoDB collection and returns results
- Implementing a POST endpoint that validates and inserts a new document
- Implementing a PATCH/PUT endpoint that updates a single document by ID
- Wiring a React list component to fetch data from the backend and render it
- Wiring a React form to POST data to the backend and update the UI
- Adding a single-field index on the most queried field
- Basic Mongoose model operations (no transactions, no multi-collection joins)

**INAPPROPRIATE for BASIC tasks:**
- Complex MongoDB aggregation pipelines ($group, $lookup, $facet)
- Advanced indexing strategies (compound, sparse, text, geospatial)
- React optimization (useMemo, useCallback, React.memo)
- Redux or complex state management
- Authentication/JWT implementation
- Background jobs or caching layers
- WebSocket or real-time features
- Multi-collection transactions
- Performance profiling or query explain plans

### Infrastructure Requirements

#### Docker Compose:
- MongoDB service seeded with realistic sample data via init script
- Node.js backend service with Express
- React frontend service (development mode)
- Network configuration for inter-service communication
- **MUST NOT include any version specification** in the docker-compose.yml
- **MUST NOT use environment variables or .env file references** — use hardcoded values
- Expose ports: MongoDB (27017), Node.js backend (5000), React frontend (3000)

#### run.sh Instructions:
- Start all Docker containers with `docker-compose up -d`
- Wait for MongoDB to be ready before proceeding
- Validate that all three services (MongoDB, backend, frontend) are responding
- Provide clear feedback messages at each step
- No manual script execution — all initialization is automatic through mounted volumes

#### kill.sh Instructions:
- Stop and remove all containers, volumes, and networks with docker-compose down
- Remove all Docker images related to this task
- Run `docker system prune -a --volumes -f`
- Delete the `/root/task/` directory entirely
- Use `|| true` where appropriate so the script is idempotent
- Print logs at every step

### Backend Code Structure (`/backend`):
- `package.json` with express, mongoose, cors, nodemon dependencies
- `server.js` as the entry point — already configured with middleware and MongoDB connection
- `src/models/` — Mongoose models already defined (candidate reads/uses them, not redesigns)
- `src/routes/` — Route files already registered (candidate fills in controller logic)
- `src/controllers/` — Controller stubs returning mock arrays or empty responses (candidate replaces with Mongoose queries)
- `seed.js` or inline seeding via MongoDB init script — seeds the database with 10-20 realistic documents

### Frontend Code Structure (`/frontend`):
- Standard Create React App structure
- `public/index.html` — REQUIRED basic HTML file with the root div for React mounting
- `src/index.js` — REQUIRED entry point that renders the React App
- `src/components/` — Functional components with placeholder/hardcoded data already rendering
- `src/services/api.js` — API base URL already configured (candidate uses it to make calls)
- React Router already set up with basic routes
- No TypeScript — plain JavaScript only

### MongoDB init_database.js Instructions:
- Create 1-2 collections (simple schema, no complex relationships)
- Insert 10-20 realistic sample documents per collection
- Include a single basic index on the primary query field
- Keep schema flat or with minimal embedding (no deep nesting)
- Include comments describing the business context

### AI and External Resource Policy:
- Candidates are permitted to use any external resources including AI, documentation, Stack Overflow
- Tasks assess ability to find, understand, integrate, and adapt solutions for a specific business context
- Complexity should require genuine BASIC-level problem-solving beyond simple copy-pasting

## README.md STRUCTURE

### Task Overview (MANDATORY — 2-3 sentences)
Describe the specific business scenario. Explain that the application skeleton is already running, and the candidate must connect the frontend to the backend and replace mock data with real MongoDB queries. Keep it clear and motivating.

### Database Access & API Configuration
Provide MongoDB connection details:
- Host: `<DROPLET_IP>`
- Port: `27017`
- Database name: (specific to the scenario)
- Username and password (hardcoded values from docker-compose)
- Base API URL: `http://<DROPLET_IP>:5000`

### Helpful Tips
Practical guidance without revealing implementations:
- Consider how Mongoose's `find()`, `findById()`, `save()` methods map to the existing route structure
- Think about what fields need to be sent in the request body for POST/PATCH endpoints
- Explore the existing Mongoose models to understand available fields and types
- Consider how React's `useEffect` hook can trigger data fetching when the component mounts
- Think about how to handle loading and error states in the React components
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery — never provide direct solutions

### Objectives
- Replace mock/hardcoded data in Express controllers with real Mongoose queries
- Wire React components to the live backend API so the UI displays real MongoDB data
- Implement basic error handling and loading states in the React frontend
- Add a single-field MongoDB index on the most queried field
- Ensure the full data flow works: MongoDB → Express API → React UI

### How to Verify
- Navigate to the React UI and confirm real data from MongoDB is displayed (not hardcoded)
- Use a MongoDB client (Compass, mongosh) to verify documents are being created/updated correctly
- Test each API endpoint with Postman or curl and verify correct JSON responses
- Confirm the frontend handles loading states and displays error messages appropriately
- Verify the added index appears in MongoDB Compass under the collection's Indexes tab

### NOT TO INCLUDE in README:
- Manual deployment instructions
- Instructions to run run.sh
- Specific implementation solutions or code snippets
- Step-by-step guides that give away the approach
- Phrases like "you should implement", "add the following code"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "task-name-in-kebab-case (under 50 characters)",
   "question": "A short description of the BASIC-level full-stack task: what business problem the candidate solves, which 2-3 endpoints they wire up, and what React components they connect to real data",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Database Access & API Configuration, Helpful Tips, Objectives, How to Verify",
      ".gitignore": "Node.js, React, MongoDB, Docker exclusions (node_modules, build/, .env, data/pgdata, etc.)",
      "docker-compose.yml": "Docker services for MongoDB, Node.js backend, React frontend (NO version, NO env vars, hardcoded credentials)",
      "run.sh": "Script to start Docker services, wait for health checks, validate all three services respond",
      "kill.sh": "Complete cleanup: containers, volumes, images, docker system prune, rm -rf /root/task",
      "init_database.js": "MongoDB initialization: create 1-2 collections, insert 10-20 sample documents, add single-field index",
      "backend/package.json": "express, mongoose, cors, nodemon dependencies",
      "backend/server.js": "Express entry point: middleware configured, MongoDB connection established, routes registered",
      "backend/src/models/ModelName.js": "Mongoose model already defined — candidate uses this, does not redesign",
      "backend/src/routes/api.js": "Route definitions already registered — stubs pointing to controller functions",
      "backend/src/controllers/controller.js": "Controller stubs returning mock arrays — candidate replaces with Mongoose queries",
      "frontend/package.json": "react, react-dom, react-router-dom, axios dependencies",
      "frontend/public/index.html": "Basic HTML file with <div id=\"root\"></div> for React to mount to (REQUIRED)",
      "frontend/src/index.js": "React entry file rendering App.js into the root element (REQUIRED)",
      "frontend/src/App.js": "Main app with React Router routes already set up",
      "frontend/src/components/ComponentName.js": "React component rendering hardcoded/placeholder data — candidate wires to API",
      "frontend/src/services/api.js": "Axios or fetch base configuration with backend URL already set"
   }},
   "outcomes": "Bullet-point list in simple language. Must include: 'Connect a React frontend to a Node.js/Express backend by replacing mock data with real MongoDB queries using Mongoose, ensuring the full data flow works end-to-end' and 'Write clean, production-ready code following basic best practices: proper error handling, meaningful variable names, and consistent API response shapes'",
   "short_overview": "Bullet-point list in simple language describing: (1) the business scenario and what the skeleton application currently does with mock data, (2) what the candidate must implement to make it real (wire frontend to backend, replace mocks with MongoDB queries), and (3) the expected outcome — a working full-stack application where real data flows from MongoDB through Express into the React UI",
   "pre_requisites": "Bullet-point list of tools and knowledge required: Node.js 18+, npm, Docker, Docker Compose, basic JavaScript (ES6+), basic React (useState, useEffect, functional components), basic Express (routes, middleware), basic MongoDB concepts (collections, documents, CRUD), Mongoose basics (models, queries), Postman or curl for API testing, MongoDB Compass or mongosh for database inspection, a code editor (VS Code recommended)",
   "answer": "High-level solution approach: (1) In each Express controller stub, import the Mongoose model and replace the mock array with the appropriate Mongoose query (find, findById, save, etc.) with basic error handling; (2) In each React component, replace hardcoded data with a useEffect that calls the backend API using fetch or Axios, stores results in useState, and renders loading/error states; (3) Add a createIndex call or Mongoose schema index option on the most frequently queried field",
   "hints": "Start by reading the existing Mongoose models and controller stubs side by side, then identify which mock return value maps to which MongoDB collection — once you understand the data shape, replacing mocks with Mongoose queries and wiring React components to those endpoints becomes straightforward.",
   "definitions": {{
      "Mongoose": "An ODM (Object Document Mapper) library for Node.js that provides a schema-based solution for modeling MongoDB data, making it easier to define, validate, and query documents",
      "Controller stub": "A route handler function that currently returns hardcoded mock data, intended to be replaced with real database logic",
      "useEffect": "A React hook that runs side effects (like API calls) after a component renders, commonly used to fetch data when a component mounts",
      "useState": "A React hook that lets functional components hold and update local state, used to store fetched data and track loading/error status",
      "CORS": "Cross-Origin Resource Sharing — a browser security mechanism that must be enabled on the Express server so the React frontend (on a different port) can make API calls to it"
   }},
   "criterias": [
      {{"name": "ReactJs", "proficiency": "BASIC", "competency_id": "f92566a6-b3fa-46ae-96cc-bf2559edd276"}},
      {{"name": "NodeJs", "proficiency": "BASIC", "competency_id": "e3f1c2ab-d4a7-4c9f-95d2-9d7f7fcb2c77"}},
      {{"name": "MongoDb", "proficiency": "BASIC", "competency_id": "22691b45-e133-426d-96df-335df1c1be1d"}}
   ]
}}

## CRITICAL REMINDERS

1. **Skeleton must run immediately** — `docker-compose up -d` brings up all 3 services with no errors. Frontend, backend, and DB MUST be fully functional out-of-the-box. Every file required to make it run (like index.html, index.js) must be present so that candidates can begin work immediately.
2. **Mock data must be obvious** — controllers return hardcoded arrays so it's clear what the candidate must replace
3. **Mongoose models must be pre-defined** — candidate does NOT redesign the schema
4. **React components must render placeholder UI** — candidate wires them to real data, not rebuilds them
5. **Task MUST be completable in {minutes_range} minutes** by a BASIC level developer
6. **No TypeScript** — plain JavaScript throughout
7. **No complex MongoDB queries** — simple find(), findById(), save(), findByIdAndUpdate() only
8. **No advanced React patterns** — useState and useEffect only
9. **Docker Compose NO version field** and NO environment variable references
10. **init_database.js must seed realistic data** so the candidate sees meaningful results immediately
11. **README must be fully populated** — no placeholder text
12. **Criterias array must match the output JSON exactly** — do not modify competency_ids
"""

PROMPT_REGISTRY = {
    "MongoDb (BASIC), NodeJs (BASIC), ReactJs (BASIC)": [
        PROMPT_FULLSTACK_BASIC_CONTEXT,
        PROMPT_FULLSTACK_BASIC_INPUT_AND_ASK,
        PROMPT_FULLSTACK_BASIC,
    ]
}
