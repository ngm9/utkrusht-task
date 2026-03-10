PROMPT_GOLANG_DOCKER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_DOCKER_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Golang and Docker assessment task.

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
2. What will the task look like? (Describe the type of Docker optimization or Golang implementation required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GOLANG_DOCKER_OPTIMIZATION_INSTRUCTIONS_INTER = """
## GOAL
As a technical architect experienced in Docker containerization and deployment, you are given real-world scenarios and proficiency levels for Docker. Your job is to generate a task where a candidate optimizes and properly containerizes a Golang REST API application using Docker, focusing on configuration, optimization, and deployment practices requiring intermediate-level Docker skills.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate receives a FULLY DEPLOYED Golang REST API application with a WORKING but SUBOPTIMAL Docker configuration. The application includes:
- Complete REST API endpoints with business logic already implemented and functional
- Functional Docker setup (Dockerfile and docker-compose.yml) that is deployed and running
- All necessary Go dependencies and code requiring minimal to no changes
- Complete Go handlers, services, and middleware that are already optimized
- Pre-configured application settings
- The application is accessible and responding but with performance issues

The candidate's primary responsibility is Docker optimization and refactoring (90%) with minimal Go configuration changes (10%) only as needed to enhance containerization.

# DEPLOYMENT BASELINE REQUIREMENT:
When generating task files, the Docker setup MUST be:
- Fully deployable and functional on first run
- Deliberately inefficient but not broken
- Measurably suboptimal with clear improvement opportunities
- Providing baseline metrics for candidates to improve upon
- Initial deployment should NOT fail - provide minimal working setup

The inefficiencies should be measurable:
- Slow container startup times (20+ seconds)
- Large image sizes (800MB+ when could be <20MB)
- Inefficient layer caching causing slow rebuilds
- Missing or improper health checks
- Resource limits not configured
- Running as root user
- Inefficient build process
- Poor network configuration
- Suboptimal base image choices
- Not utilizing Go build optimization flags

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be short, crisp, and clearly describe the Docker optimization scenario (within 50 words)
- Task provides a FULLY DEPLOYED Golang REST API application with WORKING but INEFFICIENT Docker setup
- The Golang application is fully functional and well-optimized, requiring only minimal configuration changes
- Primary focus (90%) is on Docker optimization and refactoring
- Go changes (10%) should be minimal and only for Docker optimization
- The question scenario must be clear with accurate facts and relevant context
- Generate a complete, working Golang REST API application with functional but suboptimal Docker setup
- The question should be a real-world business scenario requiring intermediate-level Docker optimization skills
- Complexity must align with intermediate proficiency level (3-5 years Docker experience)
- The question must NOT include hints about specific Docker optimizations needed
- Ensure adherence to latest Docker best practices for intermediate-level optimization
- If including diagrams, use mermaid format in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted to use any external resources including Google, Stack Overflow, Docker documentation, AI tools, LLMs
- Tasks assess the candidate's ability to effectively optimize and improve Docker containerization at an intermediate level
- Tasks involve multi-layered Docker optimization challenges requiring understanding of image optimization, build efficiency, networking, security, and deployment strategies
- Candidates use AI to help analyze inefficiencies but not replace their Docker optimization skills

## Code Generation Instructions:
Create a Docker-focused optimization task that:
- Draws inspiration from input_scenarios for business context and technical requirements
- Matches complexity for intermediate Docker proficiency (3-5 years experience)
- Tests practical intermediate-level Docker optimization and deployment efficiency skills
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list for variety
- The Golang REST API application should be COMPLETE, FUNCTIONAL, and WELL-OPTIMIZED
- All REST API endpoints should be implemented, working, and optimized
- The application has functional Docker configuration that is deployed but needs optimization
- Task focuses on Docker optimization and refactoring (90%), Go development (10%)

## Infrastructure Requirements:
- MUST include complete, fully functional REST API using Golang (gin, echo, or net/http)
- MUST include WORKING but INEFFICIENT Dockerfile requiring optimization
- MUST include WORKING but SUBOPTIMAL docker-compose.yml requiring refactoring
- A run.sh with end-to-end responsibility of deploying infrastructure and validating deployment
- Infrastructure must be ALREADY DEPLOYED and ACCESSIBLE when candidate starts

### Docker-compose Instructions:
- Golang REST API service with functional but suboptimal Docker configuration
- Additional services if needed (database, cache, message queue) with working orchestration
- Volume mounts that work but could be optimized
- Network configuration that functions but needs optimization
- MUST NOT include any version specification
- MUST NOT include environment variables or .env file references
- Use hardcoded configuration values
- Present but suboptimal configurations: inefficient resource limits, missing/poor health checks, suboptimal depends_on, basic restart policies
- Docker-compose should be functional and deployed but require optimization work

### Dockerfile Instructions:
MUST be functional and deployed but deliberately inefficient, requiring optimization:
- Single-stage build using golang:latest (convert to multi-stage with scratch/alpine/distroless)
- Using bloated base image instead of optimized alternatives
- Not leveraging Go module caching properly
- Inefficient layer ordering causing poor cache utilization
- Basic .dockerignore or missing
- Running as root user
- Missing or inefficient health check implementation
- Not using Go build optimization flags
- Not setting CGO_ENABLED=0 for static compilation
- Copying entire application context instead of selective copying
- Not separating dependency download from code compilation
- Poor build caching strategy
- Including unnecessary files in final image
- Not using build cache mounts for go modules
- Suboptimal GOOS/GOARCH configuration

### Run.sh Instructions:
- Starts Docker containers using `docker-compose up -d` and ensures deployment is complete
- Confirms that application is fully deployed and accessible
- Implements proper health check to wait for services to be fully ready
- Captures and displays initial performance metrics (build time, image size, startup time, binary size)
- Validates that Golang application is responding correctly with sample API calls
- Monitors container status and provides feedback on successful deployment
- Logs performance indicators that candidates can measure improvements against
- Includes proper error handling for failed container starts
- All files located in /root/task directory, ensure Docker paths reference this location
- Handles Docker image building and container startup with timing measurements
- Must ensure application is accessible and running before candidate starts optimization

## kill.sh File Instructions:
- Purpose: Completely clean up everything related to the `task` project
- Instructions:
  1. Stop and remove all containers created by docker-compose
  2. Remove all associated Docker volumes
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task
  5. Run `docker system prune -a --volumes -f` to remove dangling resources
  6. Delete the entire `/root/task/` folder
  7. Ignore errors if some resources are already removed (use `|| true`)
  8. Print logs at every step
  9. Print final message "Cleanup completed successfully! Droplet is now clean."

- Commands to include:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'task|golang|go') || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Remove Go build cache
  - Remove all volume mount directories
  - Remove Go module cache directories if mounted

- Extra instruction:
  - Script should be idempotent (safe to run multiple times)
  - Always use `set -e` at the top (except when explicitly ignored)

## Code File Requirements:
- Multiple files following Golang REST API project structure
- Go code should follow best practices and be well-optimized
- The Golang application files MUST be complete, fully functional, and optimized
- Docker configuration should be functional but inefficient
- PRIMARY FOCUS: 90% of candidate's work on Docker optimization and refactoring
- DO NOT include any comments in any files (Go, Docker, scripts, or configuration files)
- The application should be immediately accessible and responding, with measurable performance issues
- FILE LOCATION: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file for Golang and Docker development including:
- Go build artifacts (*.exe, *.exe~, *.dll, *.so, *.dylib, *.test, *.out)
- Go module cache and vendor directories
- IDE files (.idea/, .vscode/, *.swp, .DS_Store)
- Binary outputs
- Testing artifacts (coverage.*, *.coverprofile)
- Log files (*.log, logs/)
- Docker volumes and data directories
- OS-specific files (.DS_Store, Thumbs.db)
- Standard exclusions for Go/Docker development

## .dockerignore INSTRUCTIONS:
Should be basic or missing - candidate needs to optimize this as part of Docker optimization to reduce build context size and improve build performance

## README.md INSTRUCTIONS:
The README.md contains ONLY the following sections:
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

ALL sections must have substantial content - no empty or placeholder text allowed. Content must be directly relevant to the specific Docker optimization scenario.

### Task Overview
This section MUST contain 2-3 meaningful sentences describing the business scenario and the Docker optimization requirements. The Golang application is already functional, deployed, and accessible; the focus is on optimizing the Docker setup for production efficiency, performance, and cost reduction specific to Go applications.

Provide substantial business context explaining why Docker optimization is critical (e.g., reducing cloud costs through smaller images, improving deployment speed with faster builds, enhancing security with minimal attack surface, reducing resource consumption, leveraging Go's compilation advantages).

### Objectives
Define clear optimization goals that guide candidates toward solutions without explicitly stating implementations:
- Frame objectives around measurable improvements rather than specific technical implementations
- Focus on what the optimized system should achieve, not how to achieve it
- Examples of proper framing for Golang:
  * "Reduce Docker image from current baseline to below 50MB"
  * "Achieve sub-30-second build times for cached builds"
  * "Reduce container startup time to under 5 seconds"
  * "Minimize resource consumption while maintaining performance"
  * "Reduce compiled binary size by at least 60%"
  * "Implement security hardening to minimize attack surface"
  * "Optimize layer caching to ensure module changes don't require full rebuild"
  * "Improve build context efficiency to speed up builds by 70%+"
  * "Configure appropriate resource limits"
  * "Leverage Go's static compilation for maximum portability"
  * "Ensure zero-downtime deployments with proper health checks"
- Objectives should be measurable with specific improvements or target numbers
- Should guide candidates to think about: efficiency, performance, security, cost reduction, deployment speed, Go-specific optimizations
- Objectives describe measurable outcomes and targets, never the specific implementation approach

### Helpful Tips
Provide practical guidance without revealing specific implementations:
- Suggest exploring Go's static compilation capabilities and minimal runtime images
- Mention investigating difference between build-time and runtime dependencies
- Hint at examining different Go base image options and trade-offs
- Recommend analyzing Go module caching strategies during Docker builds
- Suggest considering how Go compilation flags can reduce binary size
- Point toward thinking about CGO dependencies and static vs dynamic linking
- Hint at exploring how Docker layer caching interacts with Go's build process
- Recommend measuring before and after metrics to quantify improvements
- Suggest thinking about security implications of including build tools in runtime images
- Mention considering container lifecycle signals and graceful shutdown
- Point toward analyzing what files are actually needed in build context
- Suggest exploring how Go's fast compilation can be leveraged
- Use bullet points formatted as tips, starting with action words like "Consider", "Investigate", "Explore", "Analyze","Think about"
- Tips should guide discovery of inefficiencies, not provide direct solutions

### How to Verify
Provide verification approaches that help candidates validate their optimizations with measurable results:
- Frame verification in terms of measurable metrics and observable improvements
- Examples for Golang:
  * "Compare the optimized image size against baseline using `docker images` - target below 50MB"
  * "Measure build time improvements with `time docker-compose build` for clean and cached builds"
  * "Test container startup time by timing from container start to first successful health check"
  * "Monitor resource consumption with `docker stats` and compare against baseline"
  * "Verify build cache efficiency by making small code change and measuring rebuild time"
  * "Inspect running container to confirm minimal base image and non-root user"
  * "Measure compiled binary size using `docker run --rm <image> ls -lh /app/binary`"
  * "Test application responsiveness and ensure optimization doesn't impact functionality"
  * "Validate that all API endpoints continue to work correctly"
  * "Verify static compilation by checking binary dependencies"
  * "Confirm Go module caching by rebuilding after dependency changes"
- Suggest comparing before/after metrics to quantify improvements
- Mention Docker commands for measurement without specifying exact implementation details
- Guide candidates to test that optimizations don't break functionality

### NOT TO INCLUDE in README:
- Manual deployment instructions (application is already deployed)
- Step-by-step setup instructions
- Instructions to run the run.sh file
- Specific Docker optimization solutions
- Direct implementation hints
- Go optimization instructions
- Explicit technology choices
- Code snippets or configuration examples
- Phrases like "you should implement", "make sure to add", "configure the following"
- Deployment troubleshooting
- Any comments or annotations

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words) - must focus on Kafka optimization and configuration",
   "question": "Brief description of the intermediate-level Docker optimization task scenario - what aspects of the deployed Docker setup need optimization? Focus on optimization requirements for Golang applications. Mention that application is currently deployed and functional but inefficient.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Objectives, How to Verify, and Helpful Tips only. NO COMMENTS.",
      ".gitignore": "Proper Go, Docker, and IDE exclusions. NO COMMENTS.",
      ".dockerignore": "Basic or missing - candidate optimizes this. NO COMMENTS.",
      "go.mod": "Go module file with all necessary dependencies. NO COMMENTS.",
      "go.sum": "Go module checksums. NO COMMENTS.",
      "docker-compose.yml": "Functional but suboptimal Docker services configuration. NO COMMENTS.",
      "Dockerfile": "Functional but inefficient Dockerfile requiring optimization. NO COMMENTS.",
      "run.sh": "Complete deployment script that measures and displays baseline metrics. NO COMMENTS.",
      "kill.sh": "Complete cleanup script to remove all resources. NO COMMENTS.",
      "main.go": "Main application entry point with server setup. NO COMMENTS.",
      "handlers/api_handlers.go": "HTTP request handlers. NO COMMENTS.",
      "services/business_service.go": "Business logic service layer. NO COMMENTS.",
      "models/models.go": "Data models and structs. NO COMMENTS.",
      "config/config.go": "Application configuration. NO COMMENTS.",
      "middleware/middleware.go": "HTTP middleware. NO COMMENTS.",
      "routes/routes.go": "Route definitions and setup. NO COMMENTS.",
      "utils/health.go": "Health check endpoint implementation. NO COMMENTS.",
      "Additional Go files as needed following standard project structure. NO COMMENTS."
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable Docker optimization improvements: dramatically reduced image size (800MB to <20MB), faster build times (3min to <30sec cached), quicker startup (<3sec), better resource efficiency, enhanced security. Use simple English with specific improvements.",
  "pre_requisites": "Bullet-point list of tools and environment setup required. Mention Docker, Docker Compose, basic understanding of Golang REST APIs, understanding of Go compilation process, Docker performance analysis tools (docker stats, docker history, docker inspect), time measurement tools.",
  "answer": "High-level solution approach focusing on Docker optimization strategies for Golang: implementing multi-stage builds, leveraging Go's static compilation, using build optimization flags, optimizing Go module caching, selecting minimal runtime base images, implementing proper layer ordering, configuring proper resource limits, adding security hardening, optimizing build context, implementing proper health checks. Include expected performance improvements with specific numbers.",
  "task_overview": [
    "3-4 concise bullet points matching the Task Overview from README.md",
    "Each point should be clear and describe what the task is about",
    "Focus on the optimization scenario and business context",
    "Should align with the README Task Overview section"
  ],
  "hints": "Single line hint suggesting candidates analyze current Docker setup to identify inefficiencies and focus on measurable optimization opportunities. Must NOT give away specific implementations but gently nudge toward measuring and improving performance metrics.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}
"""
PROMPT_REGISTRY = {}
