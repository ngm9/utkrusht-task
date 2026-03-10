PROMPT_JAVA_DOCKER_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A backend software engineer with 1–2 years of experience in Java and Docker is expected to work on small-scale service development and deployment workflows. Their main responsibility is to understand the existing application structure, implement new features or fix minor bugs in Java code, and use Docker for containerizing and running applications locally. They should be able to write simple Java classes, handle basic REST endpoints, and build Docker images using Dockerfiles. The candidate is not required to handle complex CI/CD pipelines or advanced multi-container orchestration but should understand basic containerization concepts, image building, and running containers efficiently.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_DOCKER_BASIC_INPUT_AND_ASK = """
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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Java and Docker proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_DOCKER_OPTIMIZATION_INSTRUCTIONS_BASIC = """
## GOAL
As a technical architect experienced in Docker containerization, you are given real-world scenarios and proficiency levels for Docker. Your job is to generate a deployment-ready task for basic-level Docker practitioners (1-2 years experience) where a candidate receives a functional Java Spring Boot application that needs proper containerization using Docker fundamentals.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios (input_scenarios) to frame the task. The business context, domain, and technical requirements should directly align with the given scenario while focusing primarily on Docker containerization (85%) with minimal Java configuration changes (15%).

The candidate's primary responsibility is to understand, configure, and apply basic Docker concepts. Be careful not to give away solutions or hint at implementations in task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a complete, working Java Spring Boot REST API application with basic Docker setup requiring fundamental Docker knowledge to properly containerize. The application includes:
- Fully functional REST API endpoints with all business logic implemented
- Complete Java code requiring NO modifications
- All dependencies properly configured in pom.xml/build.gradle
- Pre-configured application.properties ready for containerization
- Basic Docker files that need proper configuration and understanding

**PRIMARY FOCUS**: The candidate works on Docker containerization (85%) with minimal configuration adjustments (15%) only for Docker compatibility. The task demonstrates understanding of Docker basics, container lifecycle, basic optimization, and deployment practices suitable for 1-2 years Docker experience.

## INSTRUCTIONS

### Nature of the Task
- **MANDATORY**: The task MUST be derived from and aligned with the provided input_scenarios. Use the scenario's business context, domain, technical stack, and requirements as the foundation
- **CRITICAL**: While the scenario provides the business context, ensure the PRIMARY focus (85%) remains on Docker containerization challenges, NOT Java application development
- Task name MUST be within 50 words describing a clear basic-level Docker containerization scenario that reflects the input scenario's context
- Provide a FULLY WORKING Java application that implements the business logic from the input scenario, requiring only basic Docker setup
- **JAVA APPLICATION**: Complete and OPTIMIZED implementation of the scenario's requirements - requires ZERO Java code changes
- **PRIMARY FOCUS (85%)**: Basic Docker concepts - understanding Dockerfile structure, using appropriate base images, basic layer optimization, container commands, port mapping, basic docker-compose orchestration
- **MINIMAL CONFIGURATION (15%)**: Only environment-specific values in application.properties (database URLs, ports, service names) - NO code changes
- **SCENARIO ADHERENCE**: The business problem, domain entities, API endpoints, and data flow should directly reflect the input scenario provided
- **DOCKER EMPHASIS**: Even though following the scenario, ensure the task complexity and deliverables focus on Docker containerization skills appropriate for 1-2 years experience
- Generate complete Java Spring Boot application implementing the scenario's requirements with basic Docker setup requiring fundamental Docker knowledge
- Task complexity aligns with basic proficiency (1-2 years Docker experience):

  **Docker Focus Areas (85% of task):**
  - Understanding and using official JDK base images correctly
  - Proper WORKDIR, COPY, and CMD/ENTRYPOINT usage
  - Basic port exposure (EXPOSE directive)
  - Simple .dockerignore creation
  - Basic docker-compose service definitions
  - Understanding container logs and basic debugging
  - Basic volume mounting for data persistence
  - Simple environment variable configuration
  - Understanding container networking basics
  - Basic health check implementation (if needed)
  - Running containers with proper port mapping
  - Understanding build vs runtime dependencies
  
  **Minimal Configuration (15% of task):**
  - Updating connection strings in application.properties for containerized services
  - Ensuring correct port configuration matching the scenario's requirements
  - NO code refactoring or optimization needed

- Questions must NOT hint at solutions - hints provided separately
- Follow latest Docker best practices for basic containerization
- Diagrams in mermaid format, properly indented in code blocks

## Task Scenario Integration Requirements:
- **BUSINESS CONTEXT**: Extract and use the real-world business problem from input_scenarios
- **DOMAIN ALIGNMENT**: Implement entities, services, and APIs that match the scenario's domain
- **TECHNICAL REQUIREMENTS**: Incorporate any specific technologies mentioned in the scenario (database type, external services, etc.)
- **DOCKER CHALLENGE**: Frame the Docker containerization challenge around the scenario's deployment needs (e.g., "The e-commerce platform needs to be containerized for deployment", "The inventory management system requires Docker setup for multi-environment deployment")
- **CONSISTENCY**: Ensure README Task Overview, question description, and code implementation all reflect the same scenario
- **VARIETY**: Pick different scenarios from the input_scenarios list to ensure diverse task generation across multiple invocations

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates can use Google, Stack Overflow, Docker documentation, AI tools, LLMs
- Tasks assess ability to understand and apply basic Docker containerization concepts
- Challenges test fundamental Docker knowledge: image building, container running, basic orchestration
- AI helps with syntax but doesn't replace fundamental Docker understanding

## Code Generation Instructions:
Create Docker-focused tasks that:
- **MUST draw directly from input_scenarios** for business context, domain, and technical setup
- Match basic Docker proficiency (1-2 years experience) considering AI assistance
- Test practical basic Docker skills while implementing the scenario's business logic
- Time constraint: Completable within {minutes_range} minutes
- **Use varied scenarios** from the input_scenarios list to ensure diversity
- **CRITICAL**: Java application is COMPLETE, FUNCTIONAL, FULLY OPTIMIZED implementation of the scenario
- All Spring Boot endpoints implementing the scenario's API requirements are working
- Basic Docker configuration requiring fundamental Docker knowledge
- **TASK FOCUS**: Docker containerization (85%), NOT Java development (15% config only)
- **SCENARIO AUTHENTICITY**: The application should solve the real-world problem described in the input scenario

## Infrastructure Requirements:
**DEPLOYMENT ROBUSTNESS - CRITICAL REQUIREMENTS:**

1. **Maven/Gradle Build Configuration:**
   - pom.xml MUST include ALL required Spring Boot dependencies with correct versions
   - MUST use Spring Boot parent POM with stable version (2.7.x or 3.x series)
   - Dependencies MUST match what Docker build process expects AND what the scenario requires (e.g., JPA for database scenarios, Redis for caching scenarios)
   - Include spring-boot-maven-plugin with proper configuration
   - All dependency versions MUST be compatible and tested
   - NO dependency conflicts or missing transitive dependencies

2. **Dockerfile Build Strategy:**
   - **CRITICAL**: Dockerfile MUST use Maven/Gradle through Docker image, NOT local installation
   - Use official maven:3.8-openjdk-17 or gradle:7-jdk17 as build image
   - Structure: Build stage → Runtime stage
   - Build stage: Copy pom.xml + src, run mvn clean package
   - Runtime stage: Copy JAR from build stage, use slim JDK image
   - NEVER assume local Maven/Gradle installation

3. **Docker-Compose Configuration:**
   - MUST NOT include version field (deprecated in Compose V2)
   - Use hardcoded values - NO environment variables or .env files
   - Service dependencies MUST use correct service names matching actual container names
   - Service definitions should align with scenario requirements (e.g., include PostgreSQL for inventory systems, Redis for caching scenarios)
   - Health checks with proper intervals and retries
   - Port mappings MUST match application.properties configuration
   - Volume paths MUST exist or be creatable
   - Network configuration if multiple services communicate
   - Database service (if needed by scenario) MUST include:
     - Correct initialization commands
     - Proper volume mounting for data persistence
     - Health check that actually verifies database readiness
     - Correct port exposure

4. **Application Configuration Consistency:**
   - application.properties database URLs MUST match docker-compose service names
   - Port numbers MUST be consistent across:
     - application.properties (server.port)
     - Dockerfile EXPOSE directive
     - docker-compose ports mapping
   - Database credentials MUST match between application.properties and docker-compose
   - Connection pool settings appropriate for containerized environment
   - Configuration should support the scenario's technical requirements

5. **File System and Permissions:**
   - All paths in scripts reference /root/task
   - JAR file naming in Dockerfile MUST match Maven output (*.jar or specific name)
   - No permission issues - proper WORKDIR usage
   - Volume mount paths properly configured

### Run.sh Requirements:
- **PRIMARY**: Executes `docker-compose up -d --build`
- Implements robust waiting mechanism using docker-compose health checks or custom health verification
- Validates application responds (curl to health endpoint with retries)
- Monitors container status with proper error messages
- Error handling for failed builds or container crashes
- All paths reference /root/task
- Validates both build AND runtime success

### Kill.sh Requirements:
- Stop and remove containers: `docker-compose down --volumes --remove-orphans`
- Remove project-specific images: `docker rmi $(docker images -q 'task*') 2>/dev/null || true`
- System cleanup: `docker system prune -a --volumes -f`
- Remove task directory: `rm -rf /root/task`
- Idempotent - safe to run multiple times
- Clear logging at each step
- Success message after cleanup

### Dockerfile Instructions:
- Basic but complete Dockerfile provided
- Uses official Maven/Gradle Docker image for building (NOT local installation)
- May use single-stage build (candidate can optimize to multi-stage)
- Basic base image selection (candidate can optimize)
- Simple COPY and CMD instructions
- May be missing .dockerignore (candidate should create)
- Should work correctly but have room for basic optimization
- **CRITICAL**: Must build successfully without requiring local Maven/Gradle

### Docker-Compose Instructions:
- Basic service definitions provided
- May need additional configuration (health checks, restart policies, resource limits)
- MUST NOT include version field
- NO environment variables or .env references - use hardcoded values
- Include services required by the scenario (database, cache, message queue, etc.)
- Database service (if needed) with correct initialization
- Basic volume and network setup
- Service names MUST match application.properties references
- **CRITICAL**: Configuration must be deployment-ready with consistent naming and ports

## Code File Requirements:
- Standard Spring Boot project structure
- Java code fully optimized and functional, implementing the scenario's business requirements
- **CRITICAL**: Java files are COMPLETE - NO changes needed
- Docker files basic but functional
- **PRIMARY FOCUS**: 85% Docker work, 15% configuration
- NO TODO comments in Java code
- May include comments in Docker files for learning
- Application immediately runnable after basic Docker setup
- **BASE DIRECTORY**: /root/task for all files
- **SCENARIO IMPLEMENTATION**: All controllers, services, models, repositories implement the scenario's requirements

## .gitignore INSTRUCTIONS:
Comprehensive file including:
- Maven/Gradle artifacts: target/, build/, .gradle/, .mvn/
- IDE files: .idea/, .vscode/, *.iml, .eclipse/, .settings/, .classpath, .project
- Compiled Java: *.class, *.jar (exclude root), *.war
- Logs: *.log, logs/, spring.log
- Docker: .docker/
- OS: .DS_Store, Thumbs.db, desktop.ini
- Spring Boot: .springBeans
- Other: *.tmp, *.bak, *.swp

## .dockerignore INSTRUCTIONS:
May be missing or basic - candidate creates/improves:
- Should exclude: target/, .git/, .idea/, *.md (except needed), .gitignore, *.log
- Keep: src/, pom.xml/build.gradle, application.properties

## README.md STRUCTURE:

### Task Overview (MANDATORY - 2-3 substantial sentences)
**CRITICAL**: This section MUST describe the specific business scenario from input_scenarios and explain why Docker containerization is needed for this particular use case. Explain the Java application is fully functional and focus is on Docker setup. Connect the scenario's business problem to the containerization challenge. NEVER empty content.

### Helpful Tips
Practical guidance without revealing implementations:
- "Consider what files are needed in your container image vs. what should be excluded"
- "Think about how Maven/Gradle can be used within the Docker build process"
- "Explore how containers find and connect to other services"
- "Consider how to verify your application is ready before accepting traffic"
- "Review how Docker manages application logs"
- "Think about data persistence when containers restart"
Use bullets, action words like "Consider", "Think about", "Review"
**CRITICAL**: Guide discovery, never provide direct solutions

### Application Access
- Provide access details: host (use <DROPLET_IP> placeholder), port, API endpoints relevant to the scenario
- Health/monitoring endpoints if available
- Docker inspection commands: docker logs, docker stats, docker inspect
- Mention checking container status
- List the scenario-specific endpoints (e.g., "/api/products", "/api/inventory")

### Objectives
Define goals focusing on outcomes, not implementations, aligned with the scenario's deployment needs:
- "Ensure application runs reliably in a container with proper dependency management"
- "Configure networking so services can communicate using service names"
- "Implement container restart behavior for handling failures"
- "Reduce unnecessary files in container image"
- "Verify application readiness before serving traffic"
- Frame objectives around the scenario's deployment context
**CRITICAL**: Describe "what" and "why", never "how"

### How to Verify
Verification approaches without revealing implementations, using scenario-specific examples:
- "Check that containers start successfully and remain running"
- "Verify application responds to requests on configured ports" (mention scenario-specific endpoints)
- "Test service communication by checking database connectivity"
- "Observe container logs to ensure application starts without errors"
- "Compare container image size before and after optimization"
- "Confirm data persists after container restarts"
- "Test the scenario-specific API endpoints to ensure functionality"
**CRITICAL**: Describe what to verify and expected behaviors

### NOT TO INCLUDE:
- Manual deployment instructions (automated via run.sh)
- Step-by-step setup guides
- Specific Docker commands or solutions
- Code snippets or configuration examples
- Java optimization instructions
- Phrases like "you should implement", "add the following"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name (within 50 words) reflecting the scenario context and focusing on basic Docker containerization",
   "question": "Brief description incorporating the scenario's business problem and what Docker setup needs to be understood and configured. Focus on Docker fundamentals for the given scenario, NOT Java changes.",
   "code_files": {{
      "README.md": "Complete README with Task Overview reflecting the scenario, Tips, Access with scenario-specific endpoints, Objectives, Verification",
      ".gitignore": "Comprehensive exclusions for Java, Maven/Gradle, Docker, IDE",
      ".dockerignore": "Basic file or missing - candidate improves",
      "pom.xml": "Complete Maven config with ALL dependencies required by the scenario, correct versions, Spring Boot plugin (OR build.gradle)",
      "docker-compose.yml": "Basic but complete service definitions matching scenario needs, no version field, hardcoded values, proper service naming",
      "Dockerfile": "Basic Dockerfile using Maven/Gradle Docker image for building, functional but simple",
      "run.sh": "Complete deployment script with health checks",
      "kill.sh": "Complete cleanup script",
      "src/main/java/com/example/app/Application.java": "Complete Spring Boot main class",
      "src/main/java/com/example/app/controller/*.java": "Complete REST controllers implementing scenario's API",
      "src/main/java/com/example/app/service/*.java": "Complete service layer implementing scenario's business logic",
      "src/main/java/com/example/app/model/*.java": "Complete entities matching scenario's domain",
      "src/main/java/com/example/app/repository/*.java": "Complete repositories for scenario's data access",
      "src/main/resources/application.properties": "Complete configuration with values ready for containerization, matching scenario requirements"
  }},
  "outcomes": "Expected results in 2-3 lines: successful containerization of the scenario's application, running service, basic Docker understanding demonstrated. Simple language.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific Docker containerization goal, and (3) the expected outcome emphasizing correctness and maintainability.",
  "pre_requisites": "Bullet points: Docker, Docker Compose, basic Java Spring Boot familiarity (no expertise needed), Git, curl/Postman for testing scenario-specific endpoints",
  "answer": "High-level solution focusing on basic Docker concepts for the scenario: using official images, proper Dockerfile structure, docker-compose basics for the scenario's services, container networking, basic debugging. Minimal mention of configuration changes.",
  "hints": "Single line suggesting focus on Docker fundamentals for containerizing the scenario's application. Must NOT reveal specific implementations.",
  "definitions": {{
    "terminology_1": "Docker-focused definition relevant to the scenario",
    "terminology_2": "Container-related definition or scenario-specific technical term"
    ...
    }}
}}

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (within 50 words)
3. **code_files** must include README.md, .gitignore, build file, Dockerfile, docker-compose.yml, run.sh, kill.sh, and Java source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Application Access, Objectives, How to Verify
5. **Starter code** must be runnable but must NOT contain the Docker solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Docker/Java terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **NO comments in Docker files** that reveal the solution or give hints
10. **Use Java 11+ and Spring Boot 2.7+ or 3.x** conventions throughout
"""
PROMPT_REGISTRY = {
    "Docker (BASIC), Java (BASIC)": [
        PROMPT_JAVA_DOCKER_BASIC_CONTEXT,
        PROMPT_JAVA_DOCKER_BASIC_INPUT_AND_ASK,
        PROMPT_JAVA_DOCKER_OPTIMIZATION_INSTRUCTIONS_BASIC,
    ]
}
