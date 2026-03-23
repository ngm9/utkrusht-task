PROMPT_JAVA_MULTITHREAD_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_JAVA_MULTITHREAD_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java Multithreading assessment task.

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
2. What will the task look like? (Describe the type of Java Multithreading implementation or fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_JAVA_MULTITHREAD_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Java, concurrent programming, and the java.util.concurrent ecosystem, you are given a list of real world scenarios and proficiency levels for Java Multithreading development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a concurrency problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex concurrency bugs in the existing codebase, implement a new concurrent feature or improve existing multithreaded functionality.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper concurrency architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests concurrency thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Java concurrency experience)
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced Synchronization**: ReentrantLock, ReadWriteLock, StampedLock, Condition variables, lock fairness, tryLock with timeouts
  - **Concurrent Data Structures**: ConcurrentHashMap advanced operations (compute, merge, reduce), CopyOnWriteArrayList, ConcurrentLinkedQueue/Deque, TransferQueue
  - **Thread Pool Internals**: ThreadPoolExecutor tuning (corePoolSize, maxPoolSize, keepAliveTime, workQueue, RejectedExecutionHandler), ForkJoinPool customization, work-stealing algorithm understanding
  - **Synchronization Utilities**: CountDownLatch, CyclicBarrier, Semaphore, Phaser, Exchanger — choosing the right coordination primitive
  - **Atomic Operations**: AtomicReference, AtomicStampedReference, LongAdder, LongAccumulator, compare-and-swap (CAS) understanding
  - **Producer-Consumer Patterns**: Advanced BlockingQueue usage (LinkedBlockingQueue, ArrayBlockingQueue, PriorityBlockingQueue, DelayQueue), bounded buffer design, back-pressure handling
  - **Java Memory Model**: Happens-before relationships, memory visibility, instruction reordering, volatile vs synchronized, safe publication of objects
  - **Deadlock Prevention**: Deadlock detection strategies, lock ordering, timeout-based acquisition, resource hierarchy
  - **Virtual Threads (Project Loom)**: Virtual threads vs platform threads, structured concurrency basics, when to use virtual threads
  - **Performance & Profiling**: Thread contention analysis, lock profiling, identifying bottlenecks with JFR/VisualVM, thread dump analysis
  - **Testing Concurrent Code**: Stress testing, race condition detection, Awaitility, ConcurrentUnit, thread interleaving strategies
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern Java concurrency best practices (Java 17+/21+) and current development standards. Use modern concurrency features appropriately.
- Tasks should require candidates to make concurrency design decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate Java concurrency proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different concurrency approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Java Multithreading task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years Java concurrency experience), keeping in mind that AI assistance is allowed.
- Tests practical multithreading skills that require concurrency thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-layered concurrent applications that require thoughtful thread safety and synchronization design
- Should test the candidate's ability to structure a scalable concurrent application with proper thread management and resource sharing

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate Java concurrency skills
- The code files generated must be valid and compilable with `javac` or buildable with `mvn compile` / `gradle build`.
- Provide a realistic Java project structure that mimics real-world concurrent applications
- A part of the task completion is to watch the candidate implement concurrency best practices, design the solution correctly, demonstrate proper thread safety, and architectural decisions
- If the task is to fix bugs, make sure the starter code has concurrency bugs (race conditions, deadlocks, memory visibility issues, improper synchronization) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper concurrent design patterns and thread-safe architecture
- Starter code should include realistic project structure with proper package organization
- Include some existing classes, services, or components that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the concurrency architecture using appropriate synchronization primitives

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - pom.xml (Maven dependencies) OR build.gradle (Gradle dependencies)
  - .gitignore (Standard Java project gitignore)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial concurrency architecture that candidate needs to complete/extend
  - Include realistic folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name in <verb><subject> format within 50 characters and task related, e.g. 'Harden Order Processing Pipeline' ",
   "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Implement Thread-Safe Order Processing Engine', 'Fix Deadlock in Concurrent Transaction Handler', 'Optimize Lock Contention in High-Throughput Data Pipeline'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Java and Maven/Gradle exclusions",
      "pom.xml": "Maven dependencies with relevant libraries for intermediate-level concurrent applications",
      "src/main/java/com/company/Application.java": "Main application class or entry point",
      "src/main/java/com/company/service/ServiceClass.java": "Service layer classes with concurrency logic",
      "src/main/java/com/company/worker/WorkerClass.java": "Worker or task classes for thread pool execution",
      "src/main/java/com/company/model/ModelClass.java": "Model/domain classes with thread-safety considerations",
      "src/main/java/com/company/queue/QueueManager.java": "Queue or buffer classes for producer-consumer patterns (if applicable)",
      "src/main/java/com/company/sync/SyncCoordinator.java": "Synchronization coordination classes (if applicable)",
      "src/main/java/com/company/config/ConfigClass.java": "Configuration classes for thread pools and concurrency settings (if needed)",
      "src/main/java/com/company/exception/CustomException.java": "Custom exception classes for concurrency-related errors",
      "src/test/java/com/company/ConcurrencyTest.java": "Test class templates for concurrent code testing (if needed)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like Java concurrency knowledge, thread pool management, synchronization primitives, concurrent data structures, testing familiarity, etc.",
  "answer": "High-level solution approach for solving task",
  "hints": "a single line hint focusing on Java concurrency architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good concurrency design thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}


## Code file requirements:
- Generate realistic Java folder structure (src/main/java/com/company/package/, src/main/resources/, src/test/java/, etc.)
- Code should follow modern Java concurrency best practices and demonstrate intermediate-level patterns
- Use appropriate synchronization primitives, concurrent data structures, and thread management patterns
- Focus on modern Java concurrency features (Java 17+/21+) and development best practices
- **CRITICAL**: The generated code files should provide partial implementations that require concurrency architectural completion
- Include some existing classes, services, or worker threads that need to be extended or made thread-safe
- The core concurrency decisions, synchronization strategy, thread pool configuration, or coordination solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add synchronization here" or "Should use ReentrantLock" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be compilable, but will require concurrency completion to function properly under concurrent load
- Provide realistic Java dependencies in pom.xml/build.gradle that intermediate developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Java projects including target directories, build directories, IDE configurations (.idea/, .vscode/, .eclipse/, *.iml), compiled class files (*.class), JAR files, log files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific Java Multithreading task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own. Keep it open-ended so that the candidate's architectural decisions and design choices can be evaluated.

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why concurrency considerations matter for this use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper thread-safe architecture is crucial.


### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate Java concurrency level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - Objectives should describe WHAT needs to work, not HOW to implement it
  - Frame objectives around outcomes rather than specific technical implementations
  - Do NOT specify exact implementation approaches, specific APIs, class names, or method signatures
  - Objectives should be measurable but not prescribe specific lock types or synchronization approaches
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how". Keep to 4-6 bullets max — only the essential goals.
  - Examples of proper framing:
    * "Implement a system that processes multiple requests simultaneously without data corruption"
    * "Design a solution that coordinates multiple workers to complete tasks in parallel efficiently"
    * "Ensure shared resources are accessed safely by multiple threads without deadlocks or starvation"
    * "Build a system that gracefully handles thread interruption and shutdown scenarios"

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both concurrent functionality and thread-safety architecture
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Frame verification in terms of observable outcomes and concurrent behaviors, not specific implementation details to check
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific synchronization implementation to check. Keep to 4-6 bullets max.
  - Examples of proper framing:
    * "Run the application under concurrent load and verify that all results are consistent and correct"
    * "Confirm that no data is lost or duplicated when multiple threads access shared resources"
    * "Check that the system shuts down gracefully without leaving orphaned threads or incomplete tasks"
    * "Validate that the application handles high contention scenarios without deadlocking"

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring Java concurrency patterns that promote safe resource sharing between threads
  - Hint at considering how to manage thread lifecycles and pool configurations effectively
  - Suggest thinking about how to detect and prevent common concurrency hazards
  - Recommend considering how to test code that runs across multiple threads
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward concurrency design thinking, not provide direct solutions or specific synchronization primitives. Keep to 4-5 bullets max.
  - Frame suggestions around principles and outcomes rather than specific implementations
  - Examples of proper framing:
    * "Consider how to partition work across threads so that shared mutable state is minimized"
    * "Think about the trade-offs between coarse-grained and fine-grained locking strategies"
    * "Explore approaches for coordinating multiple threads that must wait for each other at certain points"
    * "Consider how to handle failure scenarios where one thread encounters an error while others continue"

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (javac, mvn compile, gradle build, java -jar, etc.)
  - Direct solutions or concurrency design decisions
  - Step-by-step implementation guides
  - Specific synchronization primitives or lock types (e.g., "use ReentrantLock", "add StampedLock", "use CountDownLatch")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific class implementation details that would give away the solution to the task
  - Should not provide any particular concurrency approach or synchronization pattern to implement the solution
  - Specific thread pool configurations or executor settings that would reveal the solution
  - Specific concurrent data structure recommendations that would dictate the implementation
  - Package structure decisions that would dictate the architectural approach
  - Phrases like "you should use synchronized", "make sure to add volatile", "create a thread pool with"
  - Specific java.util.concurrent class names or API methods that would reveal the solution
  - Lock ordering strategies or specific deadlock prevention techniques that would give away the approach

## CRITICAL REMINDER:
- `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display.
"""
PROMPT_REGISTRY = {
    "Java (INTERMEDIATE), Java - Multithread Programming (INTERMEDIATE)": [
        PROMPT_JAVA_MULTITHREAD_CONTEXT_INTERMEDIATE,
        PROMPT_JAVA_MULTITHREAD_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_JAVA_MULTITHREAD_INTERMEDIATE_INSTRUCTIONS,
    ],
}
