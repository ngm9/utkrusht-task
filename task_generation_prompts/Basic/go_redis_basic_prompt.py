PROMPT_GO_REDIS_BASIC_CONTEXT = """
Let me provide you with context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and role requirements?
"""

PROMPT_GO_REDIS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Go + Redis assessment task.

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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with the BASIC Go + Redis proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GO_REDIS_BASIC_INSTRUCTIONS = """
## GOAL
As a senior software architect experienced in Go, Redis, and backend API development, you are given a list of real-world scenarios and proficiency levels for Go + Redis development. Your job is to generate a task, with the given specifications, so that a candidate is presented with a functional Go REST API and some initial Redis caching data but either with logical bottlenecks or basic caching inefficiencies that require fundamental Go and Redis optimization skills. The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL Go REST API application that uses Redis for caching. The Go application includes:
- Complete REST API endpoints with business logic implemented but with straightforward inefficiencies in caching layer AND basic API endpoint performance issues requiring basic-level optimization
- Redis connection setup and configuration
- All necessary middleware, error handling, and response formatting
- Simple data models and API schemas
- Seeded Redis with realistic data and intentionally clear inefficient designs that demand basic problem-solving

The candidate's responsibility is to fix a caching or data access issue with Redis according to the task requirements and then make any code changes in the app to support the fixes. A part of the task completion is to apply Redis caching best practices alongside Go API endpoint optimization and improve application performance at a basic level (0-2 years experience).

**CRITICAL GO + REDIS API OPTIMIZATION REQUIREMENT**: This task is NOT only about Redis caching. Candidates must also optimize the Go API endpoints themselves by:
- Identifying and removing unnecessary data retrieval or repeated calls
- Adding basic in-memory or Redis-based caching strategies
- Implementing simple pagination or limited field selection in responses
- Refactoring async patterns (Go routines) where applicable
- Reducing redundant computations in endpoint logic
- Improving basic error handling
- Refactoring middleware order and data processing

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 characters and clearly describe the basic-level optimization scenario for BOTH Redis queries AND Go API endpoints
- Task must provide a working application with existing Redis-backed data and intentionally clear suboptimal caching patterns/design
- **CRITICAL**: The Go application should be FULLY FUNCTIONAL but performing poorly due to:
  * Clear and straightforward Redis data access inefficiencies AND
  * Simple API endpoint performance issues requiring basic analysis and optimization techniques on both fronts
- **CRITICAL**: Candidates must understand that optimizing BOTH the Redis data access AND the Go API endpoints is required. The task should make it clear that after fixing basic data access issues (caching, data loader patterns), they must also update the API endpoints and data access implementations in the Go application to properly utilize optimizations and maintain functionality. Similarly, endpoints must be refactored to avoid obvious data processing bottlenecks and implement basic caching.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate a complete, working Go REST API with Redis-backed data that has clear performance issues suitable for basic-level engineers (0-2 years experience).
- **PROVIDE STRAIGHTFORWARD PROBLEMATIC REDIS DATA ACCESS AND API ENDPOINT IMPLEMENTATIONS**: Include seed scripts that create simple inefficient caching patterns AND obvious repeated calls AND missing indexes in data loading.
- The scenario should be a real-world business scenario requiring basic-level performance optimization involving:
  * Redis cache patterns with straightforward data retrieval
  * Basic optimization strategies
  * Simple inefficiencies in Go API endpoint logic
  * NOT building from scratch
- The complexity of the optimization task must align with basic proficiency level.
  
- The "Infrastructure Requirements" must specify, "The in container environment uses docker-compose to run all services."
- The code should be maintainable.
- The code must be purely Go? We'll implement in pure Go.
- The "Infrastructure Requirements" includes: Dockerfile for Go service, run.sh, kill.sh, seed_redis script.
- The seed script must not contain solution hints.
- The code should use go-redis as the Redis client.
- The starter code should be minimal yet runnable and compile with docker-compose up --build.
- Starter code must include a docker-compose.yml with 2 services (Go API + Redis) plus seed data mechanism.
- Each service directory must have its own Dockerfile and go.mod/go.sum, plus source files organized under a sensible layout (cmd/, internal/, etc.).
- The project must seed Redis automatically on startup where feasible (via a seed script or startup logic).

### Docker-compose & Infrastructure Details
- DO NOT include a version field in docker-compose.yml; use the modern plain format
- Services: one Go API service and one Redis service. The Go API must depend_on Redis and wait for Redis health
- Hardened data persistence: Redis data directory mounted for persistence
- Seed data initially loaded into Redis using a seed script executed on container startup
- The container startup must be autonomous (no manual seed steps required by the candidate)
- A dedicated run.sh script must orchestrate docker-compose up and include health-check logic for Redis and Go API endpoints
- A corresponding kill.sh script must clean up all resources, prune Docker state, and remove the project directory

### Seed & Init Script Details
- seed_redis.sh (seed file) must populate Redis with simple key-value pairs and a few composite keys to illustrate cache usage
- The seed file should be executed automatically inside the Redis container initialization (via docker-entrypoint or an init script supported by the Redis image)
- The scripts must be idempotent and safe to run multiple times

### Starter Code & File Structure (Go + Redis)
- The starter code must be valid and compilable, with a Go REST API skeleton using net/http or a lightweight framework (e.g., Gin, Echo, or Chi) and a Redis client
- All code must be organized under:
  - service-go/
    - Dockerfile
    - go.mod, go.sum
    - main.go
    - redis_client.go
    - handlers/
      - cache.go
    - cmd/
      - server.go
  - seed_redis.sh
  - docker-compose.yml
  - run.sh
  - kill.sh
  - README.md (Task Overview, Helpful Tips, Objectives, How to Verify)
  - .gitignore
  - init_redis_seed.sh (optional helper to seed data on container startup)

### README.md STRUCTURE (Go + Redis Optimization)
CRITICAL: The README.md MUST contain the following sections in this order. Each section MUST be fully populated with meaningful, specific content; no empty or placeholder text allowed. Content must be directly relevant to the Go + Redis optimization scenario being generated.

1. Task Overview (MANDATORY - 2-3 substantial sentences)
2. Helpful Tips
3. Database Access
4. Objectives
5. How to Verify

### Task Overview (MANDATORY - 2-3 substantial sentences)
CRITICAL: Describe the specific business scenario where a Go REST API with Redis caching is experiencing performance issues. Explain that the application is fully functional but suffers from clear data access and API performance problems (e.g., cache misses, stale data, repeated fetches, missing pagination). Connect the business problem to the need for basic-level optimization on BOTH Redis and Go API endpoints. Make clear this is a time-bounded optimization task focusing on specific, achievable improvements. The README.md file content MUST be fully populated with meaningful, specific content relevant to basic-level optimization for BOTH Redis AND Go API.

### Helpful Tips
- Consider what kinds of clear performance issues exist in Redis (e.g., cache misses, inefficient data structures, unnecessary network calls)
- Think about inefficiencies in the Go API endpoints (e.g., redundant calls, no cache invalidation, unpaginated responses)
- Review which parts of the data flow might cause slowness involving Redis caches and API handlers
- Consider that optimization will require understanding Redis access patterns, caching strategies, and basic Go performance practices
- Explore simple caching strategies, response payload optimization, and eliminating obvious redundancy
- Think about basic coordination between Redis caching changes and Go handler changes
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

CRITICAL: Guide discovery, never provide direct solutions

### Database Access
- Provide Redis connection details (host, port, password if applicable)
- Mention that candidates can use redis-cli or a Redis GUI tool for basic performance analysis
- For the host, use a placeholder (e.g., <REDIS_HOST>) rather than an actual hostname

### Objectives
Define goals focusing on outcomes for the optimization task:
- Noticeable improvement in API endpoint response times
- Fewer Redis cache misses and improved hit rate
- Basic multi-key caching strategies and invalidation patterns
- Reduced data transferred by endpoints
- Implementing simple pagination and field selection where appropriate
- Simple schema improvements in cache usage and API endpoint refactoring
- Basic caching strategy implementation and reducing unnecessary data fetching
- CRITICAL: Scope should be achievable within the allocated time; objectives serve as performance benchmarks for task completion and scoring

### How to Verify
- Specific checkpoints after optimization showing measurable improvements in latency and cache hit rate on BOTH API and Redis fronts
- Observable behaviors to validate basic Redis cache effectiveness via the API
- Observable behaviors to validate basic API endpoint performance improvements
- Simple methods to measure before/after optimization results
- Verification of cache usage and basic query efficiency via Redis CLI or monitoring tool
- Verification of API response times and reduced Redis calls

**CRITICAL REMINDERS**
1. Output must be valid JSON only — no markdown, no explanations, no code fences
2. name must be short, descriptive, kebab-case (e.g., "go-redis-cache-optimization")
3. code_files must include README.md, .gitignore, docker-compose.yml, run.sh, kill.sh, Dockerfile, and source files for the Go service
4. README.md must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. Starter code must be runnable (docker-compose up --build) but must NOT contain the solution
6. Deployment must succeed in one go — After run.sh, all containers must be healthy, data seeded, all services accessible. The candidate only fixes or improves the Go + Redis problem, not deployment
7. run.sh must follow the exact rules above: health check loops for Redis and the Go API endpoints, fail with logs on error
8. kill.sh must follow the exact rules above: docker-compose down, force-stop containers, prune volumes/images/system, rm -rf /root/task, all with `|| true`
9. outcomes must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
10. short_overview, pre_requisites must be bullet-point lists in simple language
11. hints must be a single line; definitions must include relevant Go/Redis terms
12. Task must be completable within the allocated time for BASIC proficiency (0-2 years)
13. No comments in code that reveal the solution or give hints
14. Focus on fundamental Go + Redis patterns, not complex distributed systems or advanced architectural patterns
15. Each service must have its own directory, Dockerfile, and dependency file
16. "title" must be in `<action verb> <subject>` format and different from `name` — name is kebab-case for GitHub repo, title is human-readable for display

### NOT USED/REPLACED PARTS
- This prompt template avoids deep microservice orchestration patterns beyond a single Go service and Redis; use docker-compose for the two services only
- No advanced distributed transactions or complex event-driven patterns

## NOTATION
- Use {{}} double curly braces in this template to denote JSON blocks when necessary. These will be formatted by the downstream system, so ensure literal braces are escaped where needed in your final JSON output.

### Definitions
{
  "terminology_1": "definition_1",
  "terminology_2": "definition_2",
  "Redis Cache": "In-memory data store used as a cache or database, extremely fast key-value access",
  "Cache-Aside Pattern": "Application code checks cache first, loads from source of truth on cache miss, then updates cache",
  "Go routines": "Lightweight threads for concurrent operations in Go"
}

"""

PROMPT_REGISTRY = {
    "Golang (BASIC), Redis (BASIC)": [
        PROMPT_GO_REDIS_BASIC_CONTEXT,
        PROMPT_GO_REDIS_BASIC_INPUT_AND_ASK,
        PROMPT_GO_REDIS_BASIC_INSTRUCTIONS,
    ],
}
