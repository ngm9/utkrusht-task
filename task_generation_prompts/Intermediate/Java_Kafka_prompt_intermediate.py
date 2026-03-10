PROMPT_JAVA_KAFKA_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A backend software engineer with 2–4 years of experience in Java and Kafka is expected to design, implement, and maintain event-driven microservices that communicate through Apache Kafka. Their primary responsibility includes developing REST APIs using Java (preferably Spring Boot), producing and consuming Kafka messages, managing schema compatibility, and ensuring reliable message delivery across distributed systems. They should understand Kafka topics, partitions, consumer groups, and offset management, as well as apply best practices for asynchronous processing and error handling. The engineer should also focus on writing scalable, maintainable Java code while monitoring message flow and optimizing throughput under realistic workloads.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_KAFKA_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java and Apache Kafka assessment task.

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
2. What will the task look like? (Describe the type of Java and Kafka implementation required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_JAVA_KAFKA_OPTIMIZATION_INSTRUCTIONS_INTER = """
## GOAL
As a technical architect super experienced in Apache Kafka and distributed messaging systems, you are given a list of real world scenarios and proficiency levels for Kafka.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a Java application that uses Kafka messaging with a BASIC WORKING SETUP that needs to be properly optimized and configured using Kafka best practices that require intermediate-level Kafka skills.
The candidate's primary responsibility is to optimize, configure, and enhance the Kafka setup. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a Java application (Spring Boot with Kafka) with a BASIC WORKING KAFKA SETUP that requires optimization. The application includes:
- Complete REST API endpoints with business logic already implemented and functional
- BASIC WORKING Kafka setup (producers, consumers) that is functional but NOT optimized
- All necessary Java dependencies and code that requires minimal to no changes
- Complete Java models, services, and controllers that are already optimized
- Pre-configured application.properties with basic Kafka settings
- **CRITICAL**: The initial deployment MUST be successful and functional - candidate explores first, then optimizes
- The focus is on Kafka optimization and configuration, not Java code optimization

The candidate's primary responsibility is to focus on Kafka optimization and configuration (90%) with minimal Java configuration changes (10%) only as needed to enhance Kafka integration. The task completion involves demonstrating Kafka best practices, efficient messaging patterns, proper topic configuration, consumer group management, and optimization techniques at an intermediate level (3-5 years experience in Kafka).

## INSTRUCTIONS

### Nature of the Task 
- Task name MUST be within 50 words and clearly describe the intermediate-level Kafka optimization and configuration scenario
- Task must provide a working Java application with BASIC FUNCTIONAL Kafka setup that needs optimization
- **CRITICAL**: The Java application and basic Kafka setup should be FULLY functional from the start - initial deployment must succeed
- **CRITICAL**: The initial setup allows candidates to explore the application, test endpoints, and understand the messaging flow before optimization
- **CRITICAL**: The primary focus (90%) is on Kafka optimization: topic configuration, partitioning strategy, consumer group management, serialization, error handling, monitoring, throughput optimization, and message delivery guarantees
- **CRITICAL**: Java changes (10%) should be minimal and only for Kafka optimization (e.g., updating consumer configs, implementing custom serializers, adding monitoring endpoints)
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- Generate a complete, working Java Spring Boot application with BASIC WORKING Kafka integration that requires intermediate-level Kafka expertise to optimize
- **PROVIDE BASIC WORKING KAFKA SETUP**: Include functional but non-optimized Kafka producers/consumers that work but need optimization for production (proper topic config, partitioning, consumer groups, error handling, monitoring, performance tuning)
- The question should be a real-world business scenario requiring intermediate-level Kafka optimization and configuration skills, NOT Java application development
- The complexity of the Kafka task must align with intermediate proficiency level (3-5 years Kafka experience) requiring advanced techniques:
  
  **Primary Kafka Focus Areas (90% of task complexity):**
  - Optimizing topic configuration (partitions, replication factor, retention policies)
  - Implementing efficient partitioning strategies for message distribution
  - Configuring consumer groups for scalability and fault tolerance
  - Optimizing producer settings (acks, batch size, compression, idempotence)
  - Implementing proper consumer configurations (fetch size, session timeout, auto-commit)
  - Setting up efficient serialization/deserialization strategies (Avro, JSON, custom)
  - Implementing proper error handling and dead letter queues
  - Configuring message delivery guarantees (at-least-once, exactly-once)
  - Setting up Kafka monitoring and metrics collection
  - Implementing consumer lag monitoring and alerting
  - Optimizing throughput and latency for high-volume scenarios
  - Configuring proper offset management strategies
  - Implementing backpressure handling mechanisms
  - Setting up Kafka Connect for data integration (if needed)
  - Implementing schema registry integration (if applicable)
  - Configuring security settings (SSL, SASL if needed)
  
  **Minimal Java Configuration Areas (10% of task complexity):**
  - Minor application.properties adjustments for Kafka optimization
  - Adding monitoring/metrics endpoints for Kafka health
  - Implementing custom serializers if needed
  - Minor consumer/producer configuration updates
  - No code refactoring or business logic changes required

- The question must NOT include hints about specific Kafka implementations needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to the latest Kafka best practices for intermediate-level optimization
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Kafka documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively optimize and configure Kafka messaging systems at an intermediate level
- Tasks should involve multi-layered Kafka challenges that require understanding of distributed messaging, topic management, consumer groups, and performance optimization
- Candidates will be encouraged to use AI to help with boilerplate configurations but not replace their own Kafka architecture and optimization skills

## Code Generation Instructions:
Based on the real-world scenarios provided, create a Kafka-focused optimization task that:
- Draws inspiration from the input_scenarios to determine the business context and technical requirements
- Matches the complexity level appropriate for intermediate Kafka proficiency (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for advanced Kafka skills
- Tests practical intermediate-level Kafka optimization, configuration, and messaging pattern skills
- Time constraints: Each task should be finished within {minutes_range} minutes
- Pick different real-world scenarios from the list provided to ensure variety in task generation
- **CRITICAL**: The Java Spring Boot application should be COMPLETE, FUNCTIONAL, and WELL-OPTIMIZED with BASIC WORKING Kafka setup requiring optimization
- All Spring Boot REST endpoints should be implemented, working, and optimized
- **CRITICAL**: Initial Kafka setup must be FUNCTIONAL and DEPLOYABLE - basic producers/consumers work but need optimization
- **CRITICAL**: The task focuses on Kafka optimization and configuration (90%), NOT Java application development (10%)

## Infrastructure Requirements:
- MUST include a complete, fully functional, and optimized REST API using Java Spring Boot
- MUST include BASIC WORKING Kafka setup (producers, consumers, topics) that functions but needs optimization
- MUST include working docker-compose.yml with Kafka, Zookeeper, and application services
- **CRITICAL**: Initial deployment MUST succeed - all services start correctly and basic functionality works
- A run.sh which has the end-to-end responsibility of deploying the infrastructure, dependencies, tools etc
- **IMPORTANT**: The infrastructure setup is AUTOMATED and MUST work on first deployment - candidates explore, then optimize

### Docker-compose Instructions:
  - Java Spring Boot service with Kafka integration (working but not optimized)
  - Kafka broker service (single broker for basic setup)
  - Zookeeper service (for Kafka coordination)
  - Optional: Schema Registry, Kafka UI/monitoring tools for exploration
  - Volume mounts for Kafka data persistence
  - Network configuration for service communication
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values instead of environment variables
  - Basic configurations present: minimal broker settings, basic topic creation
  - **CRITICAL**: Docker-compose must successfully start all services on first run
  - Missing optimizations: replication, partitioning strategy, resource limits, monitoring, advanced configurations

### Dockerfile instructions:
- MUST be complete and functional with basic Kafka client dependencies
- Should include proper Java base image and Kafka client libraries
- Application must successfully connect to Kafka on startup
- Basic health checks should be present
- **CRITICAL**: Dockerfile must work correctly for initial deployment

### Run.sh Instructions:
  + PRIMARY RESPONSIBILITY: Starts all services using `docker-compose up -d`
  + WAIT MECHANISM: Implements proper health checks to wait for Kafka broker readiness
  + TOPIC CREATION: Creates basic Kafka topics with minimal configuration
  + VALIDATION: Validates that Java application connects to Kafka successfully
  + MONITORING: Provides feedback on successful deployment and service health
  + BASIC DATA: Optionally sends test messages to verify end-to-end flow
  + ERROR HANDLING: Includes proper error handling for failed service starts
  + LOCATION: All files are located in /root/task directory
  + **CRITICAL**: Must ensure complete working setup before candidate begins optimization

## kill.sh file instructions:
- Purpose: The script must completely clean up everything related to the `task` project that was created using run.sh, docker-compose.yml, and Dockerfile
- Instructions:
  1. Stop and remove all containers created by docker-compose (including Kafka, Zookeeper)
  2. Remove all associated Docker volumes (including Kafka data volumes)
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
  - `docker rmi -f $(docker images -q | grep -E 'task|java|kafka|zookeeper') || true`
  - `rm -rf /root/task`

- Dependencies cleanup:
  - Ensure that any cached Java build files (`target/`, `.class files`, `.gradle/`, `build/`) are removed
  - Remove all Kafka data volume directories
  - Remove all Zookeeper data directories

- Extra instruction:
  - The script should be idempotent (safe to run multiple times without errors)
  - Always use `set -e` at the top to exit on error (except when explicitly ignored)

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Complete working setup with basic Kafka configuration)
  - Dockerfile (Complete and functional)
  - .dockerignore (Proper exclusions for efficient builds)
  - run.sh (Script to deploy and setup the complete WORKING environment)
  - kill.sh (Complete cleanup script)
  - pom.xml OR build.gradle (Maven or Gradle build configuration with Kafka dependencies)
  - .gitignore (Java, Maven/Gradle, Docker, Kafka, IDE exclusions)
  - All Java Spring Boot code files following standard project structure with optimized implementations
  - Kafka producer and consumer implementations (working but not optimized)
  - application.properties or application.yml with basic Kafka configurations
  - **CRITICAL**: Include proper Java package structure with all necessary files (already optimized)

## Code file requirements:
- Multiple files will be generated following Spring Boot project structure
- Java code should follow best practices and be well-optimized (no Java optimization needed)
- **CRITICAL**: The Java application and basic Kafka setup MUST be complete, fully functional, and deployable
- **CRITICAL**: Initial deployment must succeed - candidate explores working system first
- Kafka configuration should be basic but functional, requiring optimization for production
- **PRIMARY FOCUS**: 90% of candidate's work should be on Kafka optimization and configuration
- DO NOT include any 'TODO' or placeholder comments in Java code
- DO include comments in Kafka configurations indicating areas that need optimization
- The application should be immediately runnable with basic Kafka functionality working
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for Java Spring Boot and Kafka development that includes:
- Maven/Gradle build directories (target/, build/, .gradle/)
- IDE files (.idea/, .vscode/, *.iml, .eclipse/, .settings/)
- Java compiled files (*.class, *.jar, *.war)
- Log files (*.log, logs/)
- Kafka data directories
- Zookeeper data directories
- Docker volumes and data directories
- OS-specific files (.DS_Store, Thumbs.db)
- Any other standard exclusions for Java/Spring Boot/Kafka development

## .dockerignore INSTRUCTIONS:
Generate a comprehensive .dockerignore file for efficient Docker builds:
- Maven/Gradle build directories (target/, build/)
- IDE files and directories
- Git directories (.git/)
- Documentation files (*.md except README)
- Test files (if not needed in container)
- Kafka local data directories

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Initial Setup Status
   - Helpful Tips
   - Application Access
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level Kafka optimization
- Task Overview section MUST contain the exact business scenario and Kafka optimization requirements
- **NEW SECTION**: Initial Setup Status - explains what is working and what needs optimization
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Kafka optimization scenario being generated
- Use concrete business context explaining why Kafka optimization is critical
- **CRITICAL**: Emphasize Kafka optimization, configuration, and performance tuning throughout README
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the Kafka optimization requirements. The Java application is already functional with basic Kafka setup; the focus is on optimizing Kafka for production workloads and performance.
NEVER generate empty content - always provide substantial business context that explains why Kafka optimization is critical for the messaging system.

### Initial Setup Status
**NEW CRITICAL SECTION**: This section explains what is already working and what needs optimization:
  - Clearly state that the application is DEPLOYED and FUNCTIONAL
  - List what is working: "Basic Kafka producers and consumers are operational", "Messages are being sent and received", "REST endpoints are accessible"
  - Explain the baseline setup: single broker, basic topic configuration, minimal consumer settings
  - Indicate that candidates should FIRST explore the application and understand the message flow
  - Mention that optimization is needed for: throughput, latency, reliability, monitoring, scalability
  - Example: "The application is currently running with a basic Kafka setup. You can access the endpoints and see messages flowing through the system. However, the current configuration uses default settings that are not suitable for production workloads requiring high throughput and reliability."

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how message distribution across partitions affects throughput and ordering
  - Mention thinking about what happens when consumers fail and how to ensure reliable message processing
  - Hint at considering different serialization formats and their impact on performance
  - Recommend exploring how consumer group configuration affects scalability and fault tolerance
  - Suggest thinking about message delivery guarantees and their trade-offs
  - Point toward investigating producer acknowledgment settings and their reliability implications
  - Hint at exploring monitoring approaches to understand consumer lag and system health
  - Recommend considering what happens to messages that fail processing
  - Suggest analyzing batch processing strategies for improved throughput
  - Mention exploring offset management strategies and their impact on exactly-once semantics
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery, not provide direct solutions or specific configurations

### Application Access
  - Provide the application access details (host, port, API endpoints for producing/consuming messages)
  - Mention Kafka monitoring endpoints and tools available (Kafka UI, metrics endpoints if included)
  - For the host, use a placeholder indicating the droplet IP (e.g., <DROPLET_IP>)
  - List useful Kafka CLI commands for exploration (kafka-topics, kafka-consumer-groups, kafka-console-consumer)
  - Mention how to check consumer lag and topic details
  - Emphasize exploring the working system first before making changes

### Objectives
Define clear goals that guide candidates toward solutions without explicitly stating implementations:
  - Frame objectives around outcomes rather than specific technical implementations
  - Focus on what the system should achieve, not how to achieve it
  - Examples of proper framing:
    * "Improve message processing throughput to handle peak loads efficiently"
    * "Ensure messages are reliably processed even when consumers temporarily fail"
    * "Minimize message processing latency while maintaining delivery guarantees"
    * "Enable the system to scale horizontally as message volume increases"
    * "Implement visibility into message flow and consumer health for operational monitoring"
    * "Reduce data transfer overhead through efficient serialization strategies"
    * "Ensure messages are processed in the correct order where business logic requires it"
    * "Prevent message loss during broker or consumer failures"
  - Objectives should be measurable but not prescribe specific Kafka features or settings
  - Should guide candidates to think about: performance, reliability, scalability, observability, ordering, fault-tolerance
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"
  - Avoid phrases like "configure partitions" or "set acks=all" - instead describe the desired business outcome

### How to Verify
Provide verification approaches that help candidates validate their solutions without giving away implementation details:
  - Frame verification in terms of observable outcomes and system behaviors
  - Examples of proper framing:
    * "Measure message processing throughput before and after optimization to quantify improvements"
    * "Simulate consumer failures to verify the system recovers and continues processing without data loss"
    * "Monitor consumer lag during high message volumes to ensure processing keeps pace"
    * "Test message ordering guarantees by producing sequential messages and verifying consumption order"
    * "Observe broker and consumer metrics to identify resource utilization improvements"
    * "Send bursts of messages to validate throughput under load conditions"
    * "Check message delivery guarantees by simulating various failure scenarios"
    * "Monitor end-to-end latency from production to consumption"
  - Suggest using Kafka monitoring tools without specifying exact commands
  - Mention metrics and behaviors to observe rather than specific configurations to check
  - Guide candidates to test edge cases: high load, failures, network issues, consumer restarts
  - **CRITICAL**: Describe what to verify and why it matters, not the specific implementation to check
  - Avoid phrases like "verify partitions are set to 3" - instead describe expected system behavior under load

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - MANUAL DEPLOYMENT INSTRUCTIONS (environment is automated via run.sh)
  - Step-by-step setup instructions (deployment is automated and working)
  - Instructions to run the run.sh file (deployment is automated)
  - Specific Kafka solutions or configurations (e.g., "set partitions to 10", "use acks=all")
  - Direct implementation hints (e.g., "add dead letter queue", "configure batch size to 1000")
  - Java optimization instructions (Java code is already optimized)
  - Explicit Kafka configuration parameters (let candidates discover appropriate values)
  - Code snippets or configuration examples
  - Phrases like "you should implement", "make sure to add", "configure the following"
  - Kafka CLI commands with specific syntax (mention tools conceptually only)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name (within 50 words) - must focus on Kafka optimization and configuration",
   "question": "A short description of the intermediate-level Kafka optimization task scenario - what Kafka optimizations need to be made to improve performance, reliability, and scalability of the messaging system? Focus on Kafka requirements, NOT Java changes. Mention that basic setup is working.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview focusing on Kafka optimization, Initial Setup Status, Objectives for Kafka improvements, and How to Verify optimization results",
      ".gitignore": "Proper Java, Maven/Gradle, Docker, Kafka, and IDE exclusions",
      ".dockerignore": "Proper exclusions for efficient Docker builds",
      "pom.xml": "Maven build configuration with Kafka dependencies (OR build.gradle if using Gradle)",
      "docker-compose.yml": "Complete working setup with Kafka, Zookeeper, and application",
      "Dockerfile": "Complete and functional Dockerfile",
      "run.sh": "Complete setup script that ensures working deployment",
      "kill.sh": "Complete cleanup script to remove all resources",
      "src/main/java/com/example/app/Application.java": "Spring Boot main application class (already optimized)",
      "src/main/java/com/example/app/controller/ApiController.java": "REST controller for producing/consuming messages (already functional and optimized)",
      "src/main/java/com/example/app/service/BusinessService.java": "Service layer (already optimized)",
      "src/main/java/com/example/app/kafka/KafkaProducer.java": "Basic working Kafka producer (needs optimization)",
      "src/main/java/com/example/app/kafka/KafkaConsumer.java": "Basic working Kafka consumer (needs optimization)",
      "src/main/java/com/example/app/config/KafkaConfig.java": "Basic Kafka configuration (needs optimization)",
      "src/main/java/com/example/app/model/Message.java": "Message model classes (already configured)",
      "src/main/resources/application.properties": "Application configuration with basic Kafka settings (needs optimization)",
      "Additional Java files as needed following Spring Boot structure (all optimized)"
  }},
  "outcomes": "Expected results after completion in 2-3 lines focusing on improved Kafka performance, enhanced reliability, optimized throughput, proper monitoring, and production-ready configuration. Use simple english.",
  "pre_requisites": "Bullet-point list of tools and environment setup required. Mention Kafka, Zookeeper, Docker, Docker Compose, basic understanding of Java Spring Boot (no Java expertise needed), Kafka CLI tools, monitoring tools, etc. Focus on Kafka requirements.",
  "answer": "High-level solution approach focusing primarily on Kafka optimization strategies: topic partitioning, consumer group configuration, producer/consumer settings, serialization, error handling, dead letter queues, monitoring, throughput optimization, delivery guarantees. Minimal Java configuration changes mentioned.",
  "hints": "A single line hint suggesting that candidates should focus on optimizing the Kafka setup for production workloads by exploring topic configuration, consumer groups, and delivery guarantees. Must NOT give away specific Kafka implementations but gently nudge toward Kafka best practices.",
  "definitions": {{
    "terminology_1": "definition_1 (should include Kafka-focused terms like partitions, consumer groups, offsets, replication)",
    "terminology_2": "definition_2 (Kafka-specific terminology)"
    ...
    }}
}}
"""
PROMPT_REGISTRY = {
    "Java, Kafka": [
        PROMPT_JAVA_KAFKA_INTERMEDIATE_CONTEXT,
        PROMPT_JAVA_KAFKA_OPTIMIZATION_INSTRUCTIONS_INTER,
        PROMPT_JAVA_KAFKA_INTERMEDIATE_INPUT_AND_ASK,
    ]
}
