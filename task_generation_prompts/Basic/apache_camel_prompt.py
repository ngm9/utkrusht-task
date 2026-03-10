PROMPT_APACHE_CAMEL_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_APACHE_CAMEL_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Apache Camel assessment task.

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

1. What will the task be about? (Describe the business domain, integration context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Apache Camel and Docker proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_APACHE_CAMEL_BASIC = """
## GOAL
As a technical architect experienced in Docker containerization and Apache Camel integration, you are given real-world scenarios and proficiency levels for Docker. Your job is to generate a deployment-ready task for basic-level Docker practitioners (1-2 years experience) where a candidate receives an Apache Camel integration application that needs proper containerization using Docker fundamentals.

**CRITICAL**: You MUST strictly follow the provided real-world task scenarios (input_scenarios) to frame the task. The business context, domain, integration patterns, and technical requirements should directly align with the given scenario. The balance between Docker containerization work and Camel configuration/code work will naturally depend on the specific scenario requirements.

The candidate's primary responsibility is to understand, configure, and apply Docker concepts appropriate to the scenario. This may involve containerizing Apache Camel applications with their dependent services, and may also require understanding and potentially modifying Camel routes or integration patterns as dictated by the scenario. Be careful not to give away solutions or hint at implementations in task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives an Apache Camel integration application with varying levels of completeness based on the scenario requirements. The application includes:
- Camel routes implementing integration logic (completeness varies by scenario)
- Java/XML route definitions that may or may not require modifications based on scenario
- Dependencies configured in pom.xml with appropriate Camel components
- Application configuration files that may need adjustments
- Docker files that need proper configuration and understanding
- Dependent services that need orchestration (databases, message brokers, caches, external services, etc.)

**TASK SCOPE**: The task naturally balances Docker containerization work with Camel application work based on the scenario. The task demonstrates understanding appropriate for 1-2 years Docker experience, with Camel complexity matching the scenario requirements.

## INSTRUCTIONS

### Nature of the Task
- **MANDATORY**: The task MUST be derived from and aligned with the provided input_scenarios. Use the scenario's business context, integration patterns, dependent services, and requirements as the foundation
- **SCENARIO-DRIVEN**: Let the scenario dictate the balance between Docker work and Camel application work
- Provide a Camel application with completeness level appropriate to the scenario requirements
- **SCENARIO ADHERENCE**: The integration problem, data flow, service dependencies, and required work should directly reflect the input scenario provided
- Generate Apache Camel Spring Boot application with completeness matching scenario requirements and Docker setup requiring fundamental Docker knowledge
- Task complexity aligns with basic proficiency (1-2 years Docker experience), with Camel complexity driven by scenario

  **Docker Focus Areas (as relevant to scenario):**
  - Understanding and using official JDK base images correctly for Camel applications
  - Proper WORKDIR, COPY, and CMD/ENTRYPOINT usage for Java-based integration apps
  - Port exposure for management and application endpoints
  - .dockerignore creation for Maven projects
  - Multi-service docker-compose definitions for all services required by scenario
  - Understanding service dependencies and startup ordering
  - Container networking for service-to-service communication
  - Service name resolution in containerized environments
  - Volume mounting for data persistence as needed
  - Environment configuration for connection strings and service endpoints
  - Understanding container logs and debugging
  - Health check implementation for services
  - Running multi-container applications with proper port mapping
  - Understanding build vs runtime dependencies
  - Service containerization based on scenario needs
  - Restart policies for resilient services
  
  **Camel Application Work (as required by scenario):**
  - Implementing integration logic if scenario provides partial implementation
  - Configuring Camel components for containerized services
  - Route modifications as specified by scenario
  - Implementing patterns or behaviors described in scenario
  - Custom processors or beans if scenario requires
  - Understanding and applying Camel concepts as needed
  - Connection string and endpoint configuration updates for containerized environment
  - Any scenario-specific implementation requirements

- Questions must NOT hint at solutions - hints provided separately
- Follow latest Docker best practices for basic containerization of integration applications
- Diagrams in mermaid format, properly indented in code blocks, showing service architecture

## Task Scenario Integration Requirements:
- **BUSINESS CONTEXT**: Extract and use the real-world integration problem from input_scenarios
- **INTEGRATION PATTERN**: Implement Camel routes that match the scenario's integration pattern
- **DEPENDENT SERVICES**: Include all services mentioned in the scenario
- **IMPLEMENTATION REQUIREMENTS**: Determine from scenario what needs to be implemented vs what is provided
- **COMPLETENESS LEVEL**: Determine from scenario whether Camel application should be fully complete, partially implemented, or requiring specific additions
- **TECHNICAL REQUIREMENTS**: Incorporate all technologies and components mentioned in the scenario
- **DOCKER CHALLENGE**: Frame the Docker containerization challenge around the scenario's deployment needs
- **CONSISTENCY**: Ensure README Task Overview, question description, and code implementation all reflect the same integration scenario
- **VARIETY**: Pick different scenarios from the input_scenarios list to ensure diverse task generation across multiple invocations

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates can use Google, Stack Overflow, Docker documentation, Apache Camel documentation, AI tools, LLMs
- Tasks assess ability to understand and apply Docker containerization concepts for integration applications
- Tasks may also assess ability to implement Camel integration logic as required by scenario
- Challenges test fundamental knowledge appropriate to basic proficiency level
- AI helps with syntax but doesn't replace fundamental understanding

## Code Generation Instructions:
Create scenario-driven tasks that:
- **MUST draw directly from input_scenarios** for all requirements
- Match basic Docker proficiency (1-2 years experience) considering AI assistance
- Test practical skills appropriate to the scenario requirements
- **BASE DIRECTORY**: /root/task for all files
- **SCENARIO IMPLEMENTATION**: Code reflects scenario requirements and expected candidate work
- Time constraint: Completable within {minutes_range} minutes
- **Use varied scenarios** from the input_scenarios list to ensure diversity
- **SCENARIO-APPROPRIATE COMPLETENESS**: Provide code with completeness level that matches scenario focus
- **TASK FOCUS**: Naturally balanced based on scenario requirements
- **SCENARIO AUTHENTICITY**: The application should solve the real-world integration problem described in the input scenario

## Infrastructure Requirements:
**DEPLOYMENT ROBUSTNESS - CRITICAL REQUIREMENTS:**

1. **Maven Build Configuration:**
   - pom.xml MUST include ALL required dependencies based on scenario
   - Use camel-spring-boot-starter as parent or dependency management
   - Include specific Camel components required by scenario (camel-jdbc, camel-http, camel-jms, camel-redis, camel-file, camel-timer, etc.)
   - Spring Boot version compatible with Camel version (e.g., Camel 3.x with Spring Boot 2.7.x or 3.x)
   - Include all necessary client libraries (database drivers, messaging clients, etc.)
   - All dependency versions MUST be compatible and tested
   - NO dependency conflicts or missing transitive dependencies
   - spring-boot-maven-plugin with proper configuration
   - The pom.xml MUST define a fixed `<finalName>` such as:
     `<finalName>integration-app</finalName>`
   - The Dockerfile MUST reference this exact name:
     `COPY --from=build target/integration-app.jar app.jar`
   - DO NOT use wildcard patterns like `target/*.jar` because they cause ambiguous builds.

2. **Dockerfile Build Strategy:**
   - **CRITICAL**: Dockerfile MUST use Maven through Docker image, NOT local installation
   - Use official maven:3.8-openjdk-17 or maven:3.9-eclipse-temurin-17 as build image
   - Structure: Build stage → Runtime stage
   - Build stage: Copy pom.xml + src, run mvn clean package -DskipTests
   - Runtime stage: Copy JAR from build stage, use eclipse-temurin:17-jre-alpine or similar
   - NEVER assume local Maven installation
   - Expose ports as required by scenario
    - ONLY use widely available and official base images:
     - `maven:3.8-openjdk-17`, `maven:3.9-eclipse-temurin-17`
     - `eclipse-temurin:17-jre-alpine`
   - NEVER invent non-standard or overly specific image tags (e.g., “-alpine3.19-slim”).


3. **Docker-Compose Multi-Service Configuration:**
   - MUST NOT include version field (deprecated in Compose V2)
   - Use hardcoded values - NO environment variables or .env files
   - **CRITICAL SERVICE ORCHESTRATION**: Define ALL services required by scenario
   - Main Camel application service
   - Any backend services mentioned in scenario (databases, message brokers, caches, etc.)
   - Any external service simulations required by scenario
   
   - **Service Dependencies Configuration**:
     - Use depends_on with condition: service_healthy for proper startup ordering
     - Camel app MUST depend on all backend services being healthy
     - Each dependent service MUST have a health check defined
   
   - **Service Configuration Best Practices**:
     - Use appropriate official images for each service type
     - Environment variables for service configuration (hardcoded values)
     - Volume mounts for data persistence where needed
     - Health checks using service-specific commands
     - Port exposure for debugging and access
     - Proper initialization scripts if scenario requires pre-populated data
   
   - **Network Configuration**:
     - Implicit bridge network is sufficient for basic tasks
     - All services can resolve each other by service name
     - Camel app connects to services using service names (not localhost)
   
   - **Restart Policies**:
     - Camel app: restart: unless-stopped or on-failure
     - Backend services: restart: unless-stopped
   
   - Service names MUST match what's referenced in application.properties
   - Health checks with proper intervals (10-30s), timeout (5-10s), retries (3-5)
   - Port mappings MUST match application.properties configuration
   - Volume paths MUST exist or be creatable
    - For standard backend services, ONLY use simple and widely available official tags:
       - postgres:14
       - mysql:8
       - redis:7
       - rabbitmq:3-management
       - mongo:6
     - DO NOT generate custom, rare, or unstable image tags.

4. **Application Configuration Consistency:**
   - application.properties MUST use docker-compose service names for all connections (never localhost)
   - Port numbers MUST be consistent across application.properties, Dockerfile, and docker-compose
   - Credentials MUST match between application.properties and docker-compose service definitions
   - Camel component configurations point to containerized services
   - Connection pool settings appropriate for containerized environment
   - Configuration should support all scenario requirements

5. **File System and Permissions:**
   - All paths in scripts reference /root/task
   - JAR file naming in Dockerfile MUST match Maven output (*.jar or specific name)
   - No permission issues - proper WORKDIR usage
   - Volume mount paths properly configured for all services
   - Data directories created with proper permissions

6. **Additional Service Implementations (if scenario requires):**
   - Provide complete code for any additional services needed by scenario
   - Each service should have its own Dockerfile
   - Services must implement exact behavior described in scenario
   - All services included in docker-compose.yml
   - Services have appropriate health checks
   - Services log relevant information for debugging

### Run.sh Requirements:
- **PRIMARY**: Executes `docker-compose up -d --build`
- Creates data directories as needed based on services
- Implements robust waiting mechanism:
  - Wait for all service health checks to pass
  - Poll Camel management endpoint or health endpoint with retries (up to 60 seconds)
  - Check logs for successful startup messages
- Validates application responds appropriately
- Monitors container status with proper error messages
- Error handling for failed builds or container crashes
- All paths reference /root/task
- Validates both build AND runtime success for ALL services
- Clear output showing startup progress for all services

### Kill.sh Requirements:
- Stop and remove all containers: `docker-compose down --volumes --remove-orphans`
- Remove project-specific images: `docker rmi $(docker images -q 'task*') 2>/dev/null || true`
- Remove data directories: `rm -rf data/` (if persistent volumes used)
- System cleanup: `docker system prune -a --volumes -f`
- Remove task directory: `rm -rf /root/task`
- Idempotent - safe to run multiple times
- Clear logging at each step
- Success message after cleanup

### Dockerfile Instructions (for Camel Application):
- Basic but complete Dockerfile provided
- Uses official Maven Docker image for building (NOT local installation)
- Multi-stage build: maven image for build, JRE image for runtime
- Build stage: COPY pom.xml, COPY src, RUN mvn clean package -DskipTests
- Runtime stage: COPY --from=build target/*.jar app.jar
- EXPOSE appropriate ports based on scenario
- CMD ["java", "-jar", "/app.jar"]
- Should work correctly but have room for basic optimization
- **CRITICAL**: Must build successfully without requiring local Maven

### Dockerfiles for Additional Services (if applicable):
- Simple, functional Dockerfiles for any additional services required by scenario
- Use appropriate base images
- Services must be fully functional and implement scenario requirements

### Docker-Compose Instructions:
- Multi-service definitions provided
- MUST NOT include version field
- NO environment variables or .env references - use hardcoded values
- Include ALL services required by the scenario
- **CRITICAL depends_on Configuration with health checks**
- Service names MUST match application.properties references exactly
- Volume definitions for data persistence where needed
- Port mappings for debugging and access
- Restart policies for resilience
- **CRITICAL**: Configuration must be deployment-ready with consistent naming, ports, and health checks

## .gitignore INSTRUCTIONS:
Comprehensive file including:
- Maven artifacts: target/, .mvn/, pom.xml.tag, pom.xml.releaseBackup
- IDE files: .idea/, .vscode/, *.iml, .eclipse/, .settings/, .classpath, .project
- Compiled Java: *.class, *.jar (exclude root), *.war
- Logs: *.log, logs/, camel.log
- Docker: .docker/
- Data directories: data/
- OS: .DS_Store, Thumbs.db, desktop.ini
- Spring Boot: .springBeans
- Camel: camel-context.xml (if generated)
- Other: *.tmp, *.bak, *.swp

## .dockerignore INSTRUCTIONS:
May be missing or basic - candidate creates/improves:
- Should exclude: target/, .git/, .idea/, *.md (except needed), .gitignore, *.log, data/
- Keep: src/, pom.xml, application.properties

## README.md STRUCTURE:
- The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify
   - Helpful Tips 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview (MANDATORY - 3-4 substantial sentences)
**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario, current situation. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why it matters.

### Objectives
  - Clear, measurable goals for the candidate appropriate for basic level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What integration functionality should work, expected data transformations, service connectivity
  - Focus on fundamental Apache Camel integration concepts and skills
  - Frame objectives around integration outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Establish connectivity between systems and ensure data flows correctly from source to destination"
    * "Transform data from one format to another as it moves through the integration route"
    * "Route messages to appropriate destinations based on content or business rules"
    * "Consume data from a source system and deliver it to one or more target systems"
    * "Handle integration errors gracefully with appropriate error handling or dead letter channels"
    * "Process and enrich messages with additional information during integration"
  - Objectives should be measurable but not prescribe specific Camel components or EIP patterns
  - Should guide candidates to think about: data flow, message routing, transformation, error handling, system connectivity
  - **CRITICAL**: Objectives describe the "what" needs to work in terms of integration behavior, never the "how" to implement it
 
 ### Application Access
- Provide access details: host (use <DROPLET_IP> placeholder), port for relevant endpoints
- Health/monitoring endpoints if available
- Docker inspection commands for multi-service setup:
  - `docker-compose ps` - Check all service status
  - `docker-compose logs <service-name>` - View logs for each service
  - `docker-compose exec <service-name> <command>` - Execute commands in containers
  - `docker network inspect task_default` - Inspect network configuration
  - `docker stats` - Monitor resource usage
- Mention checking logs for relevant information based on scenario
- List the scenario-specific integration endpoints and data flows

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and basic code quality checks
  - Frame verification in terms of observable integration outcomes and data flow behaviors
  - Examples of proper framing:
    * "Verify that data flows from the source system to the destination system correctly"
    * "Check that messages are being consumed from the input endpoint and processed"
    * "Confirm that data transformations produce the expected output format"
    * "Test that messages are routed to the correct destinations based on routing logic"
    * "Verify the integration routes start successfully and all connections are established"
    * "Check logs to confirm messages are being processed without errors"
    * "Test error scenarios by sending invalid data and verify error handling behavior"
    * "Confirm data enrichment or processing steps add the expected information to messages"
  - Suggest what integration behaviors to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: data flow, message routing, transformations, error handling, system connectivity
  - **CRITICAL**: Describe what integration behaviors to verify, not the specific Camel DSL or components to check
   
### Helpful Tips
Practical guidance without revealing implementations. Adapt tips based on what the scenario requires:

**General Docker orchestration tips:**
- "Consider how services in docker-compose discover and connect to each other"
- "Think about the order in which services need to start"
- "Explore how to verify that services are ready before starting dependent services"
- "Review how Docker manages application logs across multiple containers"
- "Consider how to persist data when containers restart"
- "Think about what files are needed in containers vs. what should be excluded"
- "Explore how Maven can be used within the Docker build process"
- "Consider how to test connectivity between services"
- "Review how to configure connection strings for containerized services"

Use bullets, action words like "Consider", "Think about", "Review", "Explore"
**CRITICAL**: Guide discovery, never provide direct solutions

### NOT TO INCLUDE:
- Manual deployment instructions (automated via run.sh)
- Step-by-step setup guides
- Specific Docker commands or solutions
- Code snippets or configuration examples
- Specific implementation details
- Phrases like "you should implement", "add the following", "configure X as follows"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name (within 50 characters) reflecting the scenario context and required work, eg:-'Fix Broken Order Event Routing'",
   "question": "Brief description incorporating the scenario's integration problem, service architecture, current state (if applicable), and what needs to be done. Be clear about what work is expected based on scenario.",
   "code_files": {{
      "README.md": "Complete README with Task Overview reflecting scenario and required work, Tips tailored to task requirements, Access with scenario-specific commands, Objectives aligned with scenario, Verification for expected outcomes",
      ".gitignore": "Comprehensive exclusions for Java, Maven, Docker, IDE, data directories",
      ".dockerignore": "Basic file or missing - candidate improves",
      "pom.xml": "Complete Maven config with ALL dependencies required by scenario, correct versions",
      "docker-compose.yml": "Multi-service definitions matching scenario, no version field, hardcoded values, proper depends_on with health checks, volumes as needed, restart policies",
      "Dockerfile": "Basic Dockerfile using Maven Docker image, multi-stage build",
      "run.sh": "Complete deployment script with health checks for all services",
      "kill.sh": "Complete cleanup script including data directories if used",
      "src/main/java/com/example/integration/Application.java": "Complete Camel Spring Boot main class",
      "src/main/java/com/example/integration/route/*.java": "Camel route definitions with completeness matching scenario requirements",
      "src/main/java/com/example/integration/processor/*.java": "Processors/beans if needed (completeness per scenario)",
      "src/main/java/com/example/integration/model/*.java": "POJOs/entities for data being integrated",
      "src/main/resources/application.properties": "Configuration with service names, matching scenario requirements",
      "<additional-service-directory>/Dockerfile": "Dockerfile for additional service (if scenario requires)",
      "<additional-service-directory>/<service-files>": "Complete service implementation (if applicable)",
      "init-scripts/<init-file>": "Initialization scripts if needed (optional)"
   }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business integration problem, (2) the specific Docker containerization and Camel implementation goal, and (3) the expected outcome emphasizing correctness and reliability.",
   "pre_requisites": "Bullet points: Docker, Docker Compose, basic Apache Camel familiarity (level appropriate to scenario), understanding of relevant concepts, Git, curl/testing tools",
   "answer": "High-level solution describing approach to scenario requirements. Focus on concepts and patterns, not specific implementations. Adapt to what scenario requires.",
   "hints": "Single line suggesting focus area(s) based on scenario. Must NOT reveal specific implementations.",
   "definitions": {{
     "terminology_1": "Key concept relevant to scenario (Docker, Camel, or domain-specific)",
     "terminology_2": "Important term related to scenario requirements",
     "terminology_3": "Technical concept involved in the scenario",
     "terminology_4": "Pattern or practice relevant to scenario solution"
     ...
   }}
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, within 50 characters
3. **code_files** must include README.md, .gitignore, pom.xml, Docker files, run.sh, kill.sh, and all Java/Camel source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Application Access, Objectives, How to Verify
5. **Starter code** must be appropriate for scenario but must NOT contain the full solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Docker/Camel terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **NO solutions revealed** in starter code — follow scenario-appropriate completeness
10. **All paths** must reference /root/task as the base directory
"""
PROMPT_REGISTRY = {
    "Apache Camel (BASIC)": [
        PROMPT_APACHE_CAMEL_CONTEXT_BASIC,
        PROMPT_APACHE_CAMEL_INPUT_AND_ASK_BASIC,
        PROMPT_APACHE_CAMEL_BASIC,
    ]
}
