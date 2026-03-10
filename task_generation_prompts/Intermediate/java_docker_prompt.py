PROMPT_JAVA_DOCKER_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A backend software engineer with 2–4 years of experience in Java and Docker is expected to develop and deploy microservices-based backend components for an existing system. Their main responsibility includes implementing REST APIs using Java (preferably Spring Boot), integrating with external services, handling data persistence, and managing containerized environments using Docker. They should be familiar with building efficient Dockerfiles, optimizing image layers, and working with docker-compose for multi-service applications. The role requires balancing clean, maintainable Java code with reliable containerization practices to ensure consistency between local and staging environments.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_DOCKER_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java and Docker assessment task.

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
2. What will the task look like? (Describe the type of Java and Docker implementation required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_JAVA_DOCKER_OPTIMIZATION_INSTRUCTIONS_INTER = """
## GOAL
As a technical architect super experienced in Docker containerization and deployment, you are given a list of real world scenarios and proficiency levels for Docker.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a Java application that needs to be properly containerized and deployed using Docker with focus on Docker configuration, optimization, and deployment practices that require intermediate-level Docker skills.
The candidate's primary responsibility is to create, configure, and optimize the Docker setup. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a basic Java application (Spring Boot) with minimal or incomplete Docker configuration. The application includes:
- Complete REST API endpoints with business logic already implemented and functional
- Basic or missing Docker setup requiring the candidate to create proper Dockerfile and docker-compose.yml
- All necessary Java dependencies and code that requires minimal to no changes
- Complete Java models, services, and controllers that are already optimized
- Pre-configured application.properties with correct settings
- The focus is on Docker containerization, not Java code optimization

The candidate's primary responsibility is to focus on Docker implementation and optimization (90%) with minimal Java configuration changes (10%) only as needed to ensure proper containerization. The task completion involves demonstrating Docker best practices, efficient containerization, proper deployment strategies, and optimization techniques at an intermediate level (3-5 years experience in Docker).

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the intermediate-level Docker containerization and deployment scenario
- Task must provide a working Java application that needs proper Docker containerization and deployment setup
- **CRITICAL**: The Java application should be FULLY functional and well-optimized, requiring only minimal configuration changes for Docker compatibility
- **CRITICAL**: The primary focus (90%) is on Docker: creating proper Dockerfile, docker-compose.yml, implementing multi-stage builds, optimizing images, configuring resources, networking, volumes, and deployment strategies
- **CRITICAL**: Java changes (10%) should be minimal and only for Docker compatibility (e.g., updating application.properties for containerized environment, ensuring proper port binding, health check endpoints)
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working Java Spring Boot application with minimal or basic Docker setup that requires intermediate-level Docker expertise to properly containerize and deploy
- **PROVIDE BASIC/INCOMPLETE DOCKER SETUP**: Include basic or missing Dockerfile and docker-compose.yml that require significant Docker work (multi-stage builds, layer optimization, resource management, networking, volumes, health checks, security practices)
- The question should be a real-world business scenario requiring intermediate-level Docker containerization and deployment skills, NOT Java application development
- The complexity of the Docker task must align with intermediate proficiency level (3-5 years Docker experience) requiring advanced techniques:
  
  **Primary Docker Focus Areas (90% of task complexity):**
  - Creating efficient multi-stage Dockerfile builds
  - Optimizing Docker image size and layer caching
  - Implementing proper base image selection (Alpine, slim variants)
  - Configuring resource limits (CPU, memory) appropriately
  - Setting up proper health checks and readiness probes
  - Implementing efficient networking between containers
  - Configuring volumes and persistent storage correctly
  - Setting up proper docker-compose orchestration
  - Implementing container security best practices
  - Optimizing build times and startup sequences
  - Configuring proper logging and monitoring
  - Setting up environment-specific configurations
  - Implementing proper dependency management between services
  - Optimizing Docker layer caching strategies
  - Creating .dockerignore for efficient builds
  
  **Minimal Java Configuration Areas (10% of task complexity):**
  - Minor application.properties adjustments for Docker environment
  - Ensuring proper port configuration for containers
  - Verifying health check endpoint availability
  - Minimal connection string updates for containerized services
  - No code refactoring or optimization required

- The question must NOT include hints about specific Docker implementations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest Docker best practices for intermediate-level containerization
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively design, implement, and optimize Docker containerization and deployment at an intermediate level
- Tasks should involve multi-layered Docker challenges that require understanding of container orchestration, image optimization, networking, and deployment strategies
- Candidates will be encouraged to use AI to help with boilerplate configurations but not replace their own Docker architecture and optimization skills

## Code Generation Instructions:
Based on the real-world scenarios provided, create a Docker-focused containerization task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate Docker proficiency (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced Docker skills
- Tests practical intermediate-level Docker containerization, optimization, and deployment skills
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- **CRITICAL**: The Java Spring Boot application should be COMPLETE, FUNCTIONAL, and WELL-OPTIMIZED with minimal or basic Docker setup requiring significant Docker work
- All Spring Boot REST endpoints should be implemented, working, and optimized
- The application should have basic or incomplete Docker configuration requiring intermediate-level Docker expertise
- **CRITICAL**: The task focuses on Docker containerization and deployment (90%), NOT Java application development (10%)

## Infrastructure Requirements:
- MUST include a complete, fully functional, and optimized REST API using Java Spring Boot
- MUST include basic/incomplete Dockerfile requiring significant Docker optimization work
- MUST include basic/incomplete docker-compose.yml requiring proper service orchestration
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run scripts initially, but will need to fix and optimize the Docker setup

### Docker-compose Instructions:
  - Java Spring Boot service requiring proper Docker configuration
  - Additional services if needed (database, cache) requiring proper container orchestration
  - Volume mounts that need to be properly configured
  - Network configuration requiring optimization
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - Missing or incomplete configurations: resource limits, health checks, depends_on, restart policies, proper networking
  - **CRITICAL**: Docker-compose should require significant intermediate-level Docker orchestration work

### Dockerfile instructions:
- MUST be basic/incomplete or missing, requiring the candidate to create a production-ready Dockerfile:
  - No multi-stage build implementation (candidate should add)
  - Using inefficient base image (candidate should optimize)
  - Poor layer ordering (candidate should optimize)
  - Missing .dockerignore (candidate should create)
  - Running as root user (candidate should fix)
  - No health check implementation (candidate should add)
  - Inefficient dependency copying (candidate should optimize)
  - Missing security best practices (candidate should implement)
  - Poor build caching strategy (candidate should optimize)
- **CRITICAL: Provide basic Docker setup requiring intermediate-level Docker optimization and best practices implementation**

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d`
  + WAIT MECHANISM: Implements proper health check to wait for services to be fully ready
  + VALIDATION: Validates that Java application is responding correctly
  + MONITORING: Monitors container status and provides feedback on successful deployment
  + ERROR HANDLING: Includes proper error handling for failed container starts
  + LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  + BUILD PROCESS: Handles Docker image building and container startup

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile
- Instructions:
  1. Stop and remove all containers created by docker-compose
  2. Remove all associated Docker volumes
  3. Remove all Docker networks created for the task
  4. Force-remove all Docker images related to this task
  5. Run `docker system prune -a --volumes -f` to remove any dangling containers, images, networks, and volumes
  6. Delete the entire `/root/task/` folder where all the files were created
  7. The script should ignore errors if some resources are already removed (use `|| true` where necessary)
  8. Print logs at every step so the user knows what is happening
  9. After successful cleanup, print a final message like "Cleanup completed successfully! Droplet is now clean."

- Commands that should be included:
  - `docker-compose -f /root/task/docker-compose.yml down --volumes --remove-orphans || true`
  - `docker system prune -a --volumes -f`
  - `docker rmi -f $(docker images -q | grep -E 'task|java|openjdk') || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Java build files (`target/`, `.class files`, `.gradle/`, `build/`) are removed
  - Remove all volume mount directories

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Basic service configuration requiring optimization)
  - Dockerfile (Basic or missing - requires significant Docker work)
  - .dockerignore (Missing - candidate should create)
  - run.sh (Script to deploy and setup the complete environment)
  - kill.sh (Complete cleanup script)
  - pom.xml OR build.gradle (Maven or Gradle build configuration with all dependencies)
  - .gitignore (Java, Maven/Gradle, Docker, IDE exclusions)
  - All Java Spring Boot code files following standard project structure with optimized implementations
  - application.properties or application.yml with configurations ready for containerization
  - **CRITICAL**: Include proper Java package structure with all necessary files (already optimized)

## Code file requirements:
- Multiple files will be generated following Spring Boot project structure
- Java code should follow best practices and be well-optimized (no Java optimization needed)
- **CRITICAL**: The Java application files MUST be complete, fully functional, and optimized
- Docker configuration should be basic or incomplete, requiring significant Docker expertise
- **PRIMARY FOCUS**: 90% of candidate's work should be on Docker setup, configuration, and optimization
- DO NOT include any 'TODO' or placeholder comments in Java code
- DO include comments in Docker files indicating areas that need configuration
- The application should be immediately runnable once proper Docker setup is completed
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Java Spring Boot and Docker development that includes:
- Maven/Gradle build directories (target/, build/, .gradle/)
- IDE files (.idea/, .vscode/, *.iml, .eclipse/, .settings/)
- Java compiled files (*.class, *.jar, *.war)
- Log files (*.log, logs/)
- Docker volumes and data directories
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for Java/Spring Boot/Docker development

## .dockerignore INSTRUCTIONS:
Should be missing - candidate needs to create this as part of Docker optimization

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Application Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level Docker containerization and deployment
- Task Overview section MUST contain the exact business scenario and Docker containerization requirements
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Docker containerization scenario being generated
- Use concrete business context explaining why proper Docker setup is critical
- **CRITICAL**: Emphasize Docker containerization, optimization, and deployment throughout README
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the Docker containerization requirements. The Java application is already functional and optimized; the focus is on creating production-ready Docker containers.
NEVER generate empty content - always provide substantial business context that explains why proper Docker containerization is critical for deployment.

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest considering how container images can be built more efficiently using staged approaches
  - Mention thinking about what files are actually needed in the final container image
  - Hint at exploring different base image options and their trade-offs for production deployments
  - Recommend considering resource boundaries to prevent containers from consuming excessive system resources
  - Suggest thinking about how containers communicate and whether network isolation is properly configured
  - Point toward considering data persistence strategies when containers restart
  - Hint at exploring container lifecycle management and how to detect when services are truly ready
  - Recommend reviewing security implications of default container configurations
  - Suggest analyzing build cache behavior and how layer ordering affects rebuild times
  - Mention considering logging and monitoring approaches for containerized applications
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery, not provide direct solutions or specific commands

### Application Access
  - Provide the application access details (host, port, API endpoints)
  - Mention available monitoring endpoints (health, metrics if applicable)
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>)
  - Mention Docker commands for inspecting containers (docker stats, docker logs, docker inspect)
  - Emphasize Docker monitoring and optimization tools

### Objectives
Define clear goals that guide candidates toward solutions without explicitly stating implementations:
  - Frame objectives around outcomes rather than specific technical implementations
  - Focus on what the system should achieve, not how to achieve it
  - Examples of proper framing:
    * "Reduce container image footprint to improve deployment speed and resource utilization"
    * "Ensure containers restart automatically when failures occur without manual intervention"
    * "Implement health verification mechanisms so orchestration tools know when services are ready"
    * "Configure appropriate resource boundaries to prevent individual containers from affecting system stability"
    * "Establish proper isolation between services while enabling necessary communication"
    * "Minimize build times by optimizing how dependencies and artifacts are cached"
    * "Apply security hardening to reduce the container attack surface"
  - Objectives should be measurable but not prescribe specific Docker features or commands
  - Should guide candidates to think about: efficiency, reliability, security, scalability, observability
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"
  - Avoid phrases like "implement multi-stage builds" or "create health checks" - instead describe the desired outcome

### How to Verify
Provide verification approaches that help candidates validate their solutions without giving away implementation details:
  - Frame verification in terms of observable outcomes and system behaviors
  - Examples of proper framing:
    * "Compare the final container size against the initial baseline to measure optimization gains"
    * "Observe container behavior during restart scenarios to ensure recovery mechanisms work correctly"
    * "Monitor startup sequences to confirm services signal readiness only when fully operational"
    * "Test resource consumption under load to verify boundaries are properly enforced"
    * "Examine container logs and metrics to ensure visibility into application behavior"
    * "Perform clean builds to validate that caching strategies reduce rebuild times"
    * "Inspect running containers to confirm security configurations are applied"
  - Suggest using Docker inspection commands without specifying exact syntax
  - Mention metrics and behaviors to observe rather than specific tools or configurations
  - Guide candidates to test edge cases: concurrent access, failures, restarts, resource pressure
  - **CRITICAL**: Describe what to verify and why it matters, not the specific implementation to check
  - Avoid phrases like "verify health check is configured" - instead describe expected system behavior

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Step-by-step setup instructions (deployment is automated)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific Docker solutions or commands (e.g., "use multi-stage builds", "add HEALTHCHECK directive")
  - Direct implementation hints (e.g., "create a .dockerignore file", "use Alpine base image")
  - Java optimization instructions (Java code is already optimized)
  - Explicit technology choices (let candidates decide the approach)
  - Code snippets or configuration examples
  - Phrases like "you should implement", "make sure to add", "configure the following"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words) - must focus on Docker containerization and deployment",
   "question": "A short description of the intermediate-level Docker containerization task scenario - what Docker setup needs to be created/optimized to properly containerize and deploy the Java application? Focus on Docker requirements, NOT Java changes.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview focusing on Docker, Objectives for Docker containerization, and How to Verify Docker setup",
      ".gitignore": "Proper Java, Maven/Gradle, Docker, and IDE exclusions",
      ".dockerignore": "Should be missing - candidate creates this",
      "pom.xml": "Maven build configuration with all dependencies (OR build.gradle if using Gradle)",
      "docker-compose.yml": "Basic Docker services configuration requiring optimization",
      "Dockerfile": "Basic or incomplete Dockerfile requiring significant Docker work",
      "run.sh": "Complete setup script for deployment",
      "kill.sh": "Complete cleanup script to remove all resources",
      "src/main/java/com/example/app/Application.java": "Spring Boot main application class (already optimized)",
      "src/main/java/com/example/app/controller/ApiController.java": "REST controller (already functional and optimized)",
      "src/main/java/com/example/app/service/BusinessService.java": "Service layer (already optimized)",
      "src/main/java/com/example/app/model/Entity.java": "JPA entities (already configured)",
      "src/main/java/com/example/app/repository/Repository.java": "JPA repositories (already optimized)",
      "src/main/java/com/example/app/config/AppConfig.java": "Configuration class (already optimized)",
      "src/main/resources/application.properties": "Application configuration (ready for containerization with minimal changes)",
      "Additional Java files as needed following Spring Boot structure (all optimized)"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on successful Docker containerization, image optimization, and deployment efficiency. Use simple english.",
  "pre_requisites": "Bullet-point list of tools and environment setup required. Mention Docker, Docker Compose, basic understanding of Java Spring Boot (no Java expertise needed), Git, Docker monitoring tools, etc. Focus on Docker requirements.",
  "answer": "High-level solution approach focusing primarily on Docker containerization strategies: multi-stage builds, image optimization, layer caching, resource configuration, networking, volumes, health checks, security practices. Minimal Java configuration changes mentioned.",
  "hints": "A single line hint suggesting that candidates should focus on creating an optimized, production-ready Docker setup. Must NOT give away specific Docker implementations but gently nudge toward Docker best practices.",
  "definitions": {{
    "terminology_1": "definition_1 (should include Docker-focused terms)",
    "terminology_2": "definition_2"
    }}
}}
"""
PROMPT_REGISTRY = {
    "Docker (INTERMEDIATE), Java (INTERMEDIATE)": [
        PROMPT_JAVA_DOCKER_INTERMEDIATE_CONTEXT,
        PROMPT_JAVA_DOCKER_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_JAVA_DOCKER_OPTIMIZATION_INSTRUCTIONS_INTER,
    ]
}
