PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python FastAPI System Design assessment task.

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
- CRITICAL: This is a DESIGN task — the candidate will NOT write any code. They will produce a written design document focused on Python/FastAPI ecosystem architecture.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What system or feature will the candidate design? (Describe the business domain, Python/FastAPI technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Note: the candidate receives a BLANK DESIGN.md with no guided sections — they must decide their own document structure. Describe what a strong design document would cover and how the challenge aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior Python backend architect with 15+ years of experience designing production Python/FastAPI systems, you are given real-world scenarios and proficiency levels for Python FastAPI System Design.
Your job is to generate a complete System Design assessment task where the candidate produces a written design document — NOT code. The candidate receives a GitHub repo with a problem statement, optional reference files describing an existing Python system, and a blank design document (DESIGN.md) where they write their design from scratch — no guided template, no pre-defined sections. The candidate must decide what sections to include, how to structure their document, and what to cover. This itself is part of the assessment.

This task specifically tests Python/FastAPI ecosystem design skills: how to architect FastAPI services, choose between sync and async patterns, design background task processing, structure API layers at scale, handle data access and caching patterns, and reason about Python-specific trade-offs.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any Python code, fix bugs, or implement features
- The candidate receives a GitHub repo containing ONLY markdown files and optional read-only reference files
- The candidate's deliverable is: write their complete system design in DESIGN.md (a blank file — no template, no guided sections)
- The candidate must decide their own document structure — this tests their ability to organize and communicate a design
- There is NO runnable code, NO requirements.txt, NO Dockerfiles, NO test files
- The assessment measures architectural thinking in the Python/FastAPI ecosystem, trade-off analysis, ability to structure a design document, and technical communication

## INSTRUCTIONS

### Nature of the Task
- Present a realistic Python/FastAPI system design challenge drawn from the provided scenarios
- The design challenge must be rooted in the Python/FastAPI ecosystem — the candidate should reason about Python-specific frameworks, libraries, patterns, and trade-offs
- The question must clearly state: what needs to be designed, the constraints, the current Python tech stack (if extending), and what sections the design document should cover
- The challenge should involve multi-component or multi-service design with distributed concerns
- Candidates should make 2-3 key technology/architecture decisions with justification
- Use realistic scale numbers, SLA requirements, and business constraints
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.

### Proficiency Level: INTERMEDIATE (Python/FastAPI-Specific)
For INTERMEDIATE level Python FastAPI System Design, the questions should test:
- **Service Architecture**: Designing multi-service Python systems — service boundaries, inter-service communication (REST vs gRPC vs messaging), FastAPI application structure with routers and dependency injection
- **Async & Concurrency**: async/await patterns, event loop considerations, blocking vs non-blocking I/O, asyncio task management, thread pool executors for CPU-bound work, GIL implications on concurrency strategy
- **Data Access Patterns**: SQLAlchemy 2.0 async vs sync, connection pooling, read replicas, caching layers (Redis, in-memory), N+1 prevention with eager loading, Alembic migration strategies
- **Background Task Processing**: Celery vs FastAPI BackgroundTasks vs ARQ vs Dramatiq, task queues with Redis/RabbitMQ, scheduled jobs, long-running task management, result backends
- **API Design & Gateway Patterns**: RESTful API design with FastAPI, Pydantic model design, API versioning, rate limiting (slowapi), middleware architecture, authentication/authorization (OAuth2, JWT)
- **Caching & Performance**: Redis caching strategies, cache invalidation patterns, response caching, database query caching, CDN integration, Pydantic model serialization performance
- **Observability Design**: Structured logging (structlog/loguru), distributed tracing (OpenTelemetry), metrics (Prometheus with prometheus-fastapi-instrumentator), health checks, alerting strategy
- **Deployment & Scaling**: Uvicorn/Gunicorn worker configuration, horizontal scaling, stateless service design, container sizing (memory/CPU for Python), graceful shutdown, rolling deployments
- **Python Framework Choices**: FastAPI vs Django vs Flask trade-offs, sync vs async frameworks, Pydantic v2 performance, ASGI vs WSGI considerations
- **Event-Driven Architecture**: Kafka/RabbitMQ integration with Python (aiokafka, aio-pika), event schemas, consumer design, dead letter handling
- The candidate IS expected to reason about distributed concerns: consistency, availability, partition tolerance at a practical level
- The candidate is NOT expected to: design custom async runtimes, build distributed databases from scratch, or solve theoretical CS problems

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine architectural reasoning specific to the Python/FastAPI ecosystem
- The design challenge should require nuanced trade-off analysis (e.g., "why Celery over FastAPI BackgroundTasks for this specific use case?") that tests real understanding

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given requirements, design a new FastAPI service or set of services — define service boundaries, APIs, data models, and infrastructure choices within the Python ecosystem
2. **Extend existing system**: Given a description of an existing Python system (FastAPI monolith, microservices, etc.), design how to add a major feature or capability — provide reference files describing the current Python architecture
3. **Diagnose & redesign**: Given a problematic Python architecture description (performance bottlenecks, scaling issues, tight coupling), identify issues and propose a better design — provide reference files showing the current flawed architecture with Python-specific details

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Concise design challenge description in 4-6 lines covering: business context, what Python/FastAPI system/component needs to be designed, current Python tech stack (if extending), key constraints (scale, latency, SLA), and what the candidate must deliver. Keep it brief and to the point — no long paragraphs.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (3-4 concise lines only), Design Challenge (bullet points only), Constraints (bullet points with concrete numbers), Deliverable (bullet points only), Evaluation Criteria (bullet points only). EVERY section except Task Overview MUST use bullet points exclusively — no paragraphs.",
      ".gitignore": "*.log\\n.DS_Store\\n*.tmp\\n",
      "DESIGN.md": "A blank file with ONLY a single title line: '# System Design Document' and a one-line instruction: 'Write your complete system design below. You decide the structure, sections, and level of detail.' — NOTHING else. No section headers, no guiding questions, no hints. The candidate must organize the document entirely on their own.",
      "reference/current_architecture.md": "Description of the current Python system — services, frameworks used, database setup, task queues, deployment. MUST include a mermaid architecture diagram showing high-level system components, services, databases, message brokers, caching layers and their connections. Follow the diagram with bullet points describing each component. Include enough detail about the Python stack (FastAPI version, SQLAlchemy config, Celery setup, Redis usage) that the candidate can reason about what to change.",
      "reference/current_flow.md": "Description of the current request/data flow through the system. MUST include a mermaid data flow diagram (sequence diagram or flowchart) showing how data moves through the system for the primary use case. Follow the diagram with bullet points describing each step in the flow. Show end-to-end flow from user action to final state.",
      "reference/current_api.md": "Current API contracts or endpoint definitions. Optional.",
      "reference/current_data_model.md": "Current database schema or SQLAlchemy model relationships. Optional."
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Should mention Python/FastAPI-specific design artifacts (e.g., service architecture, async strategy, background task design, framework choices).",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level Python/FastAPI design challenge, (2) what the candidate must produce (fill in DESIGN.md), (3) key evaluation criteria (Python ecosystem knowledge, trade-off reasoning, completeness, clarity)",
   "pre_requisites": "Bullet-point list of knowledge areas needed. Must include Python-specific items: understanding of FastAPI / Python web frameworks, experience with async/await and asyncio patterns, familiarity with SQLAlchemy or similar ORMs, knowledge of background task processing (Celery, task queues), understanding of Python concurrency (GIL, thread pools, multiprocessing), experience with caching strategies (Redis), familiarity with message brokers (Kafka/RabbitMQ), understanding of Uvicorn/Gunicorn deployment models, ability to create architecture diagrams in text or mermaid format.",
   "answer": "Thorough reference design approach — the evaluator's answer key. Must include: recommended Python framework choices with rationale (e.g., 'FastAPI with async SQLAlchemy 2.0 for the data ingestion service because of high-concurrency non-blocking I/O needs'), specific data access strategy, async/concurrency approach, inter-service communication design, background task architecture, failure handling with Python-specific patterns (retry with tenacity, circuit breakers, dead letter queues), and deployment considerations (Uvicorn worker count, container resources, memory profiling). This should be 4-6 paragraphs covering each DESIGN.md section.",
   "hints": "A single line nudge toward the right design direction using Python/FastAPI ecosystem context. Example: 'Consider how FastAPI's dependency injection and async background tasks could decouple the write path from downstream processing without introducing Celery complexity.'",
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

**CRITICAL FORMATTING REQUIREMENT**:
- Task Overview MUST be exactly 3-4 concise lines (sentences) — no more, no less. Keep it brief and to the point.
- ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no long prose. Every piece of information should be a discrete bullet point.
- ALL sections must have substantial content — no empty or placeholder text allowed.
- Use concrete Python/FastAPI ecosystem terminology where relevant.

#### Task Overview
Exactly 3-4 concise sentences describing: the business scenario, the current Python tech stack (if extending/redesigning), and why this design challenge matters. Keep it brief — detailed information goes in other sections.

#### Design Challenge
All content MUST be bullet points:
- What the candidate needs to design
- What is in scope
- What is out of scope
- Reference to DESIGN.md as the deliverable

#### Constraints
All content MUST be bullet points with concrete numbers and boundaries including Python-specific constraints:
- Scale (concurrent users, requests/second, data volume, background task throughput)
- Latency/SLA requirements (p99 latency, uptime)
- Technology constraints or preferences (must use FastAPI, must be compatible with existing Celery workers, etc.)
- Infrastructure constraints (number of services, container resources, worker counts)
- Team/org constraints if relevant (team familiarity with specific frameworks)

#### Deliverable
All content MUST be bullet points:
- Write your complete system design in DESIGN.md
- You decide the structure, sections, and level of detail
- Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate
- A strong design document is one that another engineer could use to implement the system

#### Evaluation Criteria
All content MUST be bullet points — what makes a good design document at the intermediate Python/FastAPI level:
- Document organization (logical structure, well-chosen sections, clear flow — the candidate defines their own structure)
- Completeness (all critical aspects of the design addressed with sufficient depth)
- Python ecosystem awareness (appropriate framework, library, and pattern choices)
- Trade-off reasoning (alternatives considered with Python-specific pros/cons, choices justified)
- Clarity (another Python engineer could implement from this design)
- Feasibility (design works within the stated constraints and Python runtime characteristics)
- Operational readiness (observability, failure handling, deployment considerations)

### NOT TO INCLUDE in README:
- Setup instructions or commands
- The actual design solution or specific framework recommendations
- Step-by-step implementation guides
- Specific code patterns or class hierarchies that reveal the answer

### DESIGN.md INSTRUCTIONS:
- MUST be essentially blank — only a title and a one-line instruction
- Content should be EXACTLY:
  ```
  # System Design Document

  Write your complete system design below. You decide the structure, sections, and level of detail.
  ```
- DO NOT include any section headers, guiding questions, hints, or suggested structure
- DO NOT include examples of what sections to write
- The candidate choosing their own document structure is a key part of the assessment
- A strong intermediate candidate is expected to independently identify relevant sections like: service architecture, data model, API design, async strategy, background processing, failure handling, trade-offs, etc.
- The README's Evaluation Criteria section should mention that "document organization and structure" is an evaluation factor — this is the only hint the candidate gets

### Reference Files:
- Place in a `reference/` directory
- Use descriptive names: `current_architecture.md`, `current_flow.md`, `current_api.md`, `current_data_model.md`, `current_config.md`
- **`reference/current_architecture.md`** (REQUIRED for ALL tasks): MUST include a mermaid architecture diagram (```mermaid code block) showing the high-level system components, services, databases, message brokers, caching layers, and their connections. Follow the diagram with bullet points describing each component. Use C4 container diagram, component diagram, or service architecture diagram style.
- **`reference/current_flow.md`** (REQUIRED for ALL tasks): MUST include a mermaid data flow diagram (```mermaid code block) — sequence diagram or flowchart — showing how data moves through the system for the primary use case / request flow. Follow the diagram with bullet points describing each step. Show end-to-end flow from user action to final state.
- Include Python-specific details: FastAPI configuration, SQLAlchemy models, Celery task definitions, Redis connection setup, Uvicorn worker settings
- Keep concise — just enough to understand the current Python system
- Clearly mark as "READ-ONLY reference material — do not modify these files"
- For "design from scratch" tasks, the architecture and flow files describe the target system context that the candidate must design within
- For extend/redesign tasks, the files describe the existing system the candidate must work with
- All content in reference files MUST use bullet points for descriptions (after diagrams)

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task** — NO Python source files (.py), NO requirements.txt, NO Dockerfiles, NO docker-compose.yml, NO test files in code_files
3. **code_files contains ONLY**: README.md, .gitignore, DESIGN.md, and reference/*.md files (reference/current_architecture.md and reference/current_flow.md are REQUIRED for all tasks; other reference files are optional)
4. **DESIGN.md must be blank** — only a title and one-line instruction. NO sections, NO guiding questions, NO hints
5. **The candidate decides the structure** — this is part of the assessment at intermediate level
6. **name** must be kebab-case and end with "-design", e.g., "order-processing-pipeline-design"
7. **Task must be completable in {minutes_range} minutes** — scope to 2-3 services max, not a full microservices ecosystem
8. **answer field** is the evaluator's answer key — make it thorough with specific Python framework choices, data model details, async strategy, and trade-off rationale
9. **definitions** must include 4-6 relevant Python architecture/design terms (e.g., dependency injection, event loop, task queue, connection pool, circuit breaker, back-pressure)
10. **Do NOT include any TODO comments or placeholder text** in any file
11. **Python ecosystem specificity**: The design challenge must require Python/FastAPI-specific reasoning — if you could solve it the same way in any language, it's too generic
12. **Reference files MUST include mermaid diagrams**: `reference/current_architecture.md` MUST have a mermaid architecture diagram, `reference/current_flow.md` MUST have a mermaid data flow diagram (sequence diagram or flowchart). These two reference files are REQUIRED for ALL tasks.
13. **README.md formatting**: Task Overview MUST be exactly 3-4 concise lines. ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no prose blocks. Every piece of information should be a discrete bullet point.
14. **Diagrams must be valid mermaid syntax** — use ```mermaid code blocks with proper graph/sequenceDiagram/flowchart syntax
15. **question field** must be concise — 4-6 lines only, not long paragraphs
"""

PROMPT_REGISTRY = {
    "Python FastAPI - System Design (INTERMEDIATE)": [
        PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_CONTEXT_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_PYTHON_FASTAPI_INTERMEDIATE_INSTRUCTIONS,
    ]
}
