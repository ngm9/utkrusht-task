PROMPT_SYSTEM_DESIGN_JAVA_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_JAVA_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Java System Design assessment task.

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
- CRITICAL: This is a DESIGN task — the candidate will NOT write any code. They will produce a written design document focused on Java/JVM ecosystem architecture.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What system or feature will the candidate design? (Describe the business domain, Java/JVM technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Describe the expected sections in their design document and how the challenge aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_JAVA_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior Java systems architect with 15+ years of experience designing production Java/JVM systems, you are given real-world scenarios and proficiency levels for Java System Design.
Your job is to generate a complete System Design assessment task where the candidate produces a written design document — NOT code. The candidate receives a GitHub repo with a problem statement, optional reference files describing an existing Java system, and a structured template (DESIGN_TEMPLATE.md) that they must fill in with their design.

This task specifically tests Java/JVM ecosystem design skills: how to architect Java services, choose between Java frameworks, design concurrent systems, structure Spring Boot applications at scale, handle data access patterns, and reason about JVM-specific trade-offs.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any Java code, fix bugs, or implement features
- The candidate receives a GitHub repo containing ONLY markdown files and optional read-only reference files
- The candidate's deliverable is: fill in DESIGN_TEMPLATE.md with their system design
- There is NO runnable code, NO pom.xml, NO Dockerfiles, NO test files
- The assessment measures architectural thinking in the Java ecosystem, trade-off analysis, and technical communication

## INSTRUCTIONS

### Nature of the Task
- Present a realistic Java system design challenge drawn from the provided scenarios
- The design challenge must be rooted in the Java/JVM ecosystem — the candidate should reason about Java-specific frameworks, libraries, patterns, and trade-offs
- The question must clearly state: what needs to be designed, the constraints, the current Java tech stack (if extending), and what sections the design document should cover
- The challenge should involve multi-component or multi-service design with distributed concerns
- Candidates should make 2-3 key technology/architecture decisions with justification
- Use realistic scale numbers, SLA requirements, and business constraints
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.

### Proficiency Level: INTERMEDIATE (Java-Specific)
For INTERMEDIATE level Java System Design, the questions should test:
- **Service Architecture**: Designing multi-service Java systems — service boundaries, inter-service communication (REST vs gRPC vs messaging), Spring Boot service structure
- **Concurrency & Threading**: Thread pool sizing, CompletableFuture orchestration, reactive vs imperative, virtual threads (Project Loom), concurrent data structures
- **Data Access Patterns**: JPA/Hibernate vs JDBC, connection pooling (HikariCP), read replicas, caching layers (Caffeine, Redis), N+1 prevention strategies
- **Event-Driven Architecture**: Kafka/RabbitMQ consumer/producer design, event schemas, exactly-once semantics, consumer group strategies, dead letter queues
- **API Gateway & Service Communication**: API gateway patterns, circuit breakers (Resilience4j), retry policies, timeouts, bulkhead pattern
- **Transaction Management**: Distributed transactions, saga pattern, eventual consistency, compensating transactions, idempotency
- **Observability Design**: Structured logging (SLF4J/Logback), distributed tracing (OpenTelemetry), metrics (Micrometer), health checks, alerting strategy
- **Deployment & Scaling**: Horizontal scaling considerations, stateless service design, container sizing (JVM heap/memory), graceful shutdown, rolling deployments
- **Java Framework Choices**: Spring Boot vs Quarkus vs Micronaut trade-offs, Spring Cloud components, reactive frameworks (WebFlux vs MVC)
- The candidate IS expected to reason about distributed concerns: consistency, availability, partition tolerance at a practical level
- The candidate is NOT expected to: design from-scratch consensus algorithms, build custom distributed databases, or solve theoretical CS problems

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine architectural reasoning specific to the Java ecosystem
- The design challenge should require nuanced trade-off analysis (e.g., "why Kafka over RabbitMQ for this specific use case?") that tests real understanding

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given requirements, design a new Java service or set of services — define service boundaries, APIs, data models, and infrastructure choices within the Java ecosystem
2. **Extend existing system**: Given a description of an existing Java system (Spring Boot monolith, microservices, etc.), design how to add a major feature or capability — provide reference files describing the current Java architecture
3. **Diagnose & redesign**: Given a problematic Java architecture description (performance bottlenecks, scaling issues, tight coupling), identify issues and propose a better design — provide reference files showing the current flawed architecture with Java-specific details

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Full design challenge description including: the business context, what Java system/component needs to be designed, the current Java tech stack (if extending), specific constraints (scale, latency, SLA, tech preferences within Java ecosystem), and exactly what sections the design document should cover. This should be 4-6 paragraphs — detailed enough that the candidate has complete clarity on what to produce. Mention specific Java ecosystem concerns (JVM memory, thread pools, framework choices) where relevant to the challenge.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (business scenario + current Java stack), Design Challenge (what to design), Constraints (scale/SLA/tech), Deliverable (fill in DESIGN_TEMPLATE.md), Evaluation Criteria",
      ".gitignore": "*.log\\n.DS_Store\\n*.tmp\\n",
      "DESIGN_TEMPLATE.md": "Structured template with 5-7 section headers and 1-2 guiding sub-questions per section. Sections are EMPTY — candidate fills them in. Sections should be Java-ecosystem-aware (e.g., 'Framework & Library Choices' instead of generic 'Technology Stack').",
      "reference/current_architecture.md": "For extend/redesign tasks: description of the current Java system — services, frameworks used, database setup, messaging, deployment. Include enough detail about the Java stack (Spring Boot version, JPA config, Kafka setup) that the candidate can reason about what to change.",
      "reference/current_api.md": "For extend/redesign tasks: current API contracts or service interfaces. Optional.",
      "reference/current_data_model.md": "For extend/redesign tasks: current database schema or entity relationships. Optional."
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Should mention Java-specific design artifacts (e.g., service architecture, thread pool strategy, framework choices).",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level Java design challenge, (2) what the candidate must produce (fill in DESIGN_TEMPLATE.md), (3) key evaluation criteria (Java ecosystem knowledge, trade-off reasoning, completeness, clarity)",
   "pre_requisites": "Bullet-point list of knowledge areas needed. Must include Java-specific items: understanding of Spring Boot / Java web frameworks, experience with relational databases and JPA/JDBC, familiarity with message brokers (Kafka/RabbitMQ), knowledge of Java concurrency (thread pools, CompletableFuture), understanding of JVM memory model and tuning basics, ability to create architecture diagrams in text or mermaid format.",
   "answer": "Thorough reference design approach — the evaluator's answer key. Must include: recommended Java framework choices with rationale (e.g., 'Spring Boot with WebFlux for the notification service because of non-blocking I/O needs'), specific data access strategy, concurrency approach, inter-service communication design, event schema examples, failure handling with Java-specific patterns (Resilience4j circuit breaker config, retry strategies), and deployment considerations (JVM heap sizing, container resources). This should be 4-6 paragraphs covering each DESIGN_TEMPLATE.md section.",
   "hints": "A single line nudge toward the right design direction using Java ecosystem context. Example: 'Consider how Spring Boot event listeners and an async executor could decouple the write path from downstream processing.'",
   "definitions": {{
     "term1": "definition1",
     "term2": "definition2"
   }}
}}

## code_files REQUIREMENTS:

### README.md INSTRUCTIONS:
The README.md contains the following sections:
  - Task Overview
  - Design Challenge
  - Constraints
  - Deliverable
  - Evaluation Criteria

**CRITICAL REQUIREMENT**: Task Overview section MUST contain 3-4 meaningful sentences describing the business scenario, the current Java tech stack (if extending/redesigning), and why this design challenge matters.
ALL sections must have substantial content — no empty or placeholder text allowed.
Use concrete Java ecosystem terminology where relevant.

#### Task Overview
3-4 sentences describing the business scenario, the current situation, the Java/JVM technologies in play, and why this design challenge matters to the business. For extend/redesign tasks, briefly mention the current stack (e.g., "The existing system is a Spring Boot 3.x monolith using JPA/Hibernate with PostgreSQL").

#### Design Challenge
Clear statement of what the candidate needs to design. Reference the sections in DESIGN_TEMPLATE.md. Be explicit about scope — what is in scope and what is out of scope.

#### Constraints
Concrete numbers and boundaries including Java-specific constraints:
- Scale (concurrent users, requests/second, data volume, message throughput)
- Latency/SLA requirements (p99 latency, uptime)
- Technology constraints or preferences (must use Spring Boot, must be compatible with existing Kafka cluster, etc.)
- Infrastructure constraints (number of services, JVM heap budget, container resources)
- Team/org constraints if relevant (team familiarity with specific frameworks)

#### Deliverable
"Fill in all sections of DESIGN_TEMPLATE.md with your design. Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate. Justify your Java framework and library choices."

#### Evaluation Criteria
What makes a good design document at the intermediate Java level:
- Completeness (all sections addressed with sufficient depth)
- Java ecosystem awareness (appropriate framework, library, and pattern choices)
- Trade-off reasoning (alternatives considered with Java-specific pros/cons, choices justified)
- Clarity (another Java engineer could implement from this design)
- Feasibility (design works within the stated constraints and JVM characteristics)
- Operational readiness (observability, failure handling, deployment considerations)

### NOT TO INCLUDE in README:
- Setup instructions or commands
- The actual design solution or specific framework recommendations
- Step-by-step implementation guides
- Specific code patterns or class hierarchies that reveal the answer

### DESIGN_TEMPLATE.md INSTRUCTIONS:
- Must have clear section headers (## level) matching what the README's Design Challenge section asks for
- Each section has 1-2 guiding sub-questions in italics to help the candidate understand what's expected
- ALL sections are left EMPTY for the candidate to fill in
- Sections should use Java-ecosystem-aware language
- Typical sections for INTERMEDIATE Java level (pick 5-7 relevant ones per task):
  - **Service Architecture & Boundaries**: What services exist? What are their responsibilities? How do they communicate? (Include a component/service diagram)
  - **Framework & Library Choices**: Which Java frameworks and libraries for each service? Why these over alternatives?
  - **API Design & Service Contracts**: What REST/gRPC endpoints or async interfaces exist? Request/response formats? Error responses?
  - **Data Model & Storage**: What are the core entities? Which database(s) and why? How is data partitioned across services?
  - **Event/Message Flow**: What events are published/consumed? What message broker and why? Event schemas? Consumer group strategy?
  - **Concurrency & Threading Strategy**: How are concurrent requests handled? Thread pool configuration? Async processing approach?
  - **Failure Handling & Resilience**: What happens when [specific service/dependency] fails? Circuit breaker strategy? Retry policy? Fallback behavior?
  - **Transaction & Consistency Strategy**: How is data consistency maintained across services? Saga vs 2PC? Idempotency approach?
  - **Observability & Monitoring**: Logging strategy? Distributed tracing? Key metrics and alerts? Health checks?
  - **Deployment & Scaling**: How are services deployed? JVM tuning considerations? Horizontal scaling triggers? Graceful shutdown?
  - **Trade-offs & Alternatives**: What alternative approaches were considered? Why was this design chosen?
- DO NOT include the answer or solution hints in the template
- DO NOT include example responses in the template sections

### Reference Files (ONLY for extend/redesign tasks):
- Place in a `reference/` directory
- Use descriptive names: `current_architecture.md`, `existing_api.md`, `current_data_model.md`, `current_config.md`
- Include Java-specific details: Spring Boot configuration, JPA entities, Kafka consumer config, thread pool settings
- Keep concise — just enough to understand the current Java system
- Clearly mark as "READ-ONLY reference material — do not modify these files"
- For "design from scratch" tasks, do NOT include reference files

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task** — NO Java source files (.java), NO pom.xml, NO build.gradle, NO Dockerfiles, NO application.properties, NO test files in code_files
3. **code_files contains ONLY**: README.md, .gitignore, DESIGN_TEMPLATE.md, and optionally reference/*.md files
4. **DESIGN_TEMPLATE.md** sections must align exactly with what the question and README ask for
5. **The template must NOT contain the answer** — only guiding questions per section
6. **name** must be kebab-case and end with "-design", e.g., "order-processing-pipeline-design"
7. **Task must be completable in {minutes_range} minutes** — scope to 2-3 services max, not a full microservices ecosystem
8. **answer field** is the evaluator's answer key — make it thorough with specific Java framework choices, data model details, concurrency strategy, and trade-off rationale
9. **definitions** must include 4-6 relevant Java architecture/design terms (e.g., circuit breaker, saga pattern, connection pool, event sourcing, back-pressure)
10. **Do NOT include any TODO comments or placeholder text** in any file
11. **Java ecosystem specificity**: The design challenge must require Java/JVM-specific reasoning — if you could solve it the same way in any language, it's too generic
"""

PROMPT_REGISTRY = {
    "Java - System Design (INTERMEDIATE)": [
        PROMPT_SYSTEM_DESIGN_JAVA_CONTEXT_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_JAVA_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_JAVA_INTERMEDIATE_INSTRUCTIONS,
    ]
}
