PROMPT_SYSTEM_DESIGN_GOLANG_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_GOLANG_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Golang System Design assessment task.

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
- CRITICAL: This is a DESIGN task — the candidate will NOT write any code. They will produce a written design document focused on system architecture.
- CRITICAL: This is a SYSTEM DESIGN assessment — do NOT prescribe, mandate, or constrain which technologies, frameworks, infrastructure, or tools the candidate must use. The candidate is free to choose ANY tech stack, ANY infrastructure, ANY framework they see fit. Only describe what currently exists in the system — the candidate decides what to keep, replace, or add.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What system or feature will the candidate design? (Describe the business domain, technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Note: the candidate receives a BLANK DESIGN.md with no guided sections — they must decide their own document structure. Describe what a strong design document would cover and how the challenge aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_GOLANG_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior Golang backend architect with 15+ years of experience designing production Go systems, you are given real-world scenarios and proficiency levels for Golang System Design.
Your job is to generate a complete System Design assessment task where the candidate produces a written design document — NOT new code. The candidate receives a GitHub repo containing a real Go project folder structure with existing code files that show the CURRENT system, plus a blank design document (DESIGN.md) where they write their design from scratch — no guided template, no pre-defined sections. The candidate must decide what sections to include, how to structure their document, and what to cover. This itself is part of the assessment.

The repo includes the actual Go project structure with real code files (main entrypoint under `cmd/`, internal packages under `internal/`, HTTP/gRPC handlers, service packages, repositories, models, middleware, config, `go.mod`, etc.) so the candidate can browse and understand what currently exists. The code is structural/high-level — it shows package layout, type definitions, function signatures, key logic flows, and configuration — enough to understand the current system's architecture, but NOT a full line-by-line production implementation. The candidate is completely free to propose ANY technology, framework, or infrastructure in their design. Do NOT constrain or prescribe their choices.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any code, fix bugs, or implement features
- The candidate receives a GitHub repo containing a real Go project folder structure with existing code files showing the current system
- The candidate's deliverable is: write their complete system design in DESIGN.md (a blank file — no template, no guided sections)
- The candidate must decide their own document structure — this tests their ability to organize and communicate a design
- The existing code files are READ-ONLY context — they show what is currently implemented so the candidate understands the system they are designing for
- The assessment measures architectural thinking, trade-off analysis, ability to structure a design document, and technical communication

## INSTRUCTIONS

### Nature of the Task
- Present a realistic system design challenge drawn from the provided scenarios
- The question must clearly state: what needs to be designed, the business constraints, the current system (if extending), and what the design document should cover
- The challenge should involve multi-component or multi-service design with distributed concerns
- Candidates should make 2-3 key technology/architecture decisions with justification — but these are THEIR choices, not prescribed by the task
- Use realistic scale numbers, SLA requirements, and business constraints
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.
- CRITICAL: Do NOT tell the candidate what technologies, frameworks, or infrastructure to use in their design. Only describe what currently exists. The candidate decides what to propose — this is a core part of the system design assessment.

### Proficiency Level: INTERMEDIATE
For INTERMEDIATE level System Design, the questions should test the candidate's ability to reason about:
- **Service Architecture**: Designing multi-service systems — service boundaries, inter-service communication patterns (REST vs gRPC vs messaging), API design, idiomatic Go package layout (cmd/internal/pkg), modular monolith vs microservices trade-offs
- **Goroutines & Concurrency**: Goroutine lifecycle management, worker pool sizing, channel-based pipelines (fan-in/fan-out), sync primitives (Mutex, RWMutex, sync.Map, sync.Pool, sync.Once, errgroup), avoiding goroutine leaks, backpressure handling
- **Context & Cancellation**: Proper `context.Context` propagation, deadlines and timeouts, request-scoped cancellation, graceful goroutine shutdown
- **Data Access Patterns**: Database access strategies, connection pool sizing (database/sql max open/idle), prepared statements, read replicas, N+1 prevention, transactional consistency, migration strategies
- **Background Task Processing**: Job queue design, scheduled jobs, long-running task management, retry/dead-letter strategies, worker pool sizing, supervision of long-lived goroutines
- **Event-Driven Architecture**: Message broker design, event schemas (protobuf/Avro/JSON), delivery guarantees (at-least-once, exactly-once), consumer strategies, dead letter handling, idempotent consumers
- **API Design & Middleware**: RESTful and/or gRPC API design, request/response model design, validation, API versioning, rate limiting, middleware chains (http.Handler composition or interceptors), authentication/authorization
- **Error Handling**: Error wrapping with `%w`, sentinel errors, error types, propagation through layers, structured error responses, panics vs returned errors
- **Caching & Performance**: Caching strategies, cache invalidation patterns, response caching, query caching, payload serialization efficiency (json vs protobuf vs msgpack)
- **Transaction Management**: Distributed transactions, saga pattern, eventual consistency, compensating transactions, idempotency keys
- **Observability Design**: Structured logging (zap/zerolog/slog), distributed tracing (OpenTelemetry), metrics (Prometheus), health checks, alerting, request correlation IDs
- **Deployment & Scaling**: Process model, horizontal scaling, stateless service design, container sizing (GOMAXPROCS tuning, memory limits), graceful shutdown using context, deployment strategies, zero-downtime rollouts
- The candidate IS expected to reason about distributed concerns: consistency, availability, partition tolerance at a practical level
- The candidate is NOT expected to: design from-scratch consensus algorithms, build custom distributed databases, or solve theoretical CS problems
- IMPORTANT: The above are areas the candidate should REASON about — do NOT prescribe specific technologies for any of these. The candidate chooses their own tools and frameworks.

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine architectural reasoning and technology selection skills
- The design challenge should require nuanced trade-off analysis (e.g., choosing between different messaging systems, database types, or architectural patterns) that tests real understanding

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given requirements, design a new service or set of services — define service boundaries, APIs, data models, and infrastructure choices (candidate picks the tech stack). The repo still includes code files showing the existing system context the new design must integrate with.
2. **Extend existing system**: Given an existing system (repo has full project code showing current implementation), design how to add a major feature or capability. The candidate browses the current code to understand the system, then proposes their design using any technology they choose.
3. **Diagnose & redesign**: Given a problematic system (repo has full project code showing the current flawed implementation with performance bottlenecks, scaling issues, or tight coupling), identify issues and propose a better design. The candidate is free to propose entirely different technologies.

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Concise design challenge description in 4-6 lines covering: business context, what system/component needs to be designed, what currently exists (if extending), key constraints (scale, latency, SLA), and what the candidate must deliver. Do NOT mention what technologies to use — only describe the problem and current state. Keep it brief and to the point — no long paragraphs.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (3-4 concise lines only), Design Challenge (bullet points only), Constraints (bullet points with concrete numbers), Deliverable (bullet points only), Evaluation Criteria (bullet points only). EVERY section except Task Overview MUST use bullet points exclusively — no paragraphs.",
      ".gitignore": "Standard Go .gitignore (bin/, *.exe, *.test, *.out, vendor/, .env, coverage.out, etc.)",
      "DESIGN.md": "A blank file with ONLY a single title line: '# System Design Document' and a one-line instruction: 'Write your complete system design below. You decide the structure, sections, and level of detail.' — NOTHING else. No section headers, no guiding questions, no hints. The candidate must organize the document entirely on their own.",

      "// ACTUAL PROJECT CODE FILES — the full folder structure of the current system": "See CODE FILE INSTRUCTIONS below for detailed requirements. Include ALL of these:",
      "// Build/config files": "go.mod with real dependencies, go.sum (optional), Dockerfile if applicable, docker-compose.yml if applicable, Makefile if applicable, .env.example, golangci.yml if applicable",
      "// Source code files": "Main entrypoint (e.g., cmd/<service>/main.go), HTTP/gRPC handlers (e.g., internal/transport/http/...), service packages (e.g., internal/service/...), repository packages (e.g., internal/repository/...), domain models (e.g., internal/domain/... or internal/models/...), middleware (e.g., internal/middleware/...), config package (e.g., internal/config/...), worker / job processor packages (e.g., internal/worker/...), message consumer/producer packages if applicable, pkg/... for any exported reusable packages",
      "// SQL/schema files": "Database schema or migration files if applicable (e.g., migrations/0001_initial.up.sql for golang-migrate, or schema.sql)"
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Should mention design artifacts (e.g., service architecture, scaling strategy, technology choices with justification).",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level design challenge, (2) what the candidate must produce (fill in DESIGN.md), (3) key evaluation criteria (trade-off reasoning, technology choices with justification, completeness, clarity)",
   "pre_requisites": "Bullet-point list of knowledge areas needed: understanding of Go's concurrency model (goroutines, channels, context), experience with HTTP/gRPC service design in Go, familiarity with databases and connection pool management in Go, knowledge of message brokers and event-driven systems, understanding of system scaling and stateless service design, ability to create architecture diagrams in text or mermaid format.",
   "answer": "Thorough reference design approach — the evaluator's answer key. Must include: recommended technology/framework choices with rationale, specific data access strategy, goroutine and concurrency approach, inter-service communication design, event schema examples, failure handling patterns, and deployment considerations. This should be 4-6 paragraphs covering each DESIGN.md section. Note: this is for the EVALUATOR only — candidates never see this.",
   "hints": "A single line nudge toward the right design direction. Example: 'Consider how a worker pool fed by a buffered channel could decouple ingestion from downstream processing while bounding goroutine count.'",
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
- Use concrete technical terminology where relevant, but do NOT prescribe specific technologies.

#### Task Overview
Exactly 3-4 concise sentences describing: the business scenario, what the current system does (if extending/redesigning), and why this design challenge matters. Keep it brief — detailed information goes in other sections. Do NOT mention what technologies the candidate should use.

#### Current System Architecture (REQUIRED)
A mermaid diagram showing the CURRENT system architecture — ONLY what exists today. Must follow the ARCHITECTURE DIAGRAM INSTRUCTIONS section exactly. This diagram helps the candidate visualize the existing system before they write their design. Do NOT include any proposed/future components in this diagram.

#### Current Data Flow (REQUIRED)
A mermaid sequence diagram or flowchart showing how data currently flows through the system for the primary use case — ONLY the current flow, NOT any proposed/future flow. Must follow the same ARCHITECTURE DIAGRAM INSTRUCTIONS for perfect mermaid syntax. Show end-to-end flow from user action to final state. This helps the candidate understand how the existing system processes requests before they write their design. Do NOT include any proposed steps, future improvements, or hints about what should change.

#### Design Challenge
All content MUST be bullet points:
- What the candidate needs to design (the problem, not the solution)
- What is in scope
- What is out of scope
- Reference to DESIGN.md as the deliverable
- Do NOT suggest or constrain technology choices — the candidate decides

#### Constraints
All content MUST be bullet points with concrete numbers and business/operational boundaries:
- Scale (concurrent users, requests/second, data volume, message throughput)
- Latency/SLA requirements (p99 latency, uptime)
- Business constraints (budget, timeline, team size)
- Current infrastructure description (what currently runs and how — for context only, NOT as a mandate to keep using it)
- CRITICAL: Do NOT include technology constraints that tell the candidate what to use. Do NOT say "must use X" or "must be compatible with Y". Only describe what currently exists — the candidate decides what to propose in their design.

#### Deliverable
All content MUST be bullet points:
- Write your complete system design in DESIGN.md
- You decide the structure, sections, and level of detail
- Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate
- A strong design document is one that another engineer could use to implement the system

#### Evaluation Criteria
All content MUST be bullet points — what makes a good design document at the intermediate level:
- Document organization (logical structure, well-chosen sections, clear flow — the candidate defines their own structure)
- Completeness (all critical aspects of the design addressed with sufficient depth)
- Technology choices with justification (candidate explains WHY they chose specific technologies, frameworks, and patterns)
- Trade-off reasoning (alternatives considered with pros/cons, choices justified)
- Clarity (another engineer could implement from this design)
- Feasibility (design works within the stated constraints)
- Operational readiness (observability, failure handling, deployment considerations)

### NOT TO INCLUDE in README:
- Setup instructions or commands
- The actual design solution or specific framework recommendations
- Step-by-step implementation guides
- Specific code patterns or class hierarchies that reveal the answer
- Any mandate or constraint telling the candidate which technologies, frameworks, or infrastructure they must use — the candidate chooses freely

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
- A strong intermediate candidate is expected to independently identify relevant sections like: service architecture, data model, API design, concurrency strategy, failure handling, trade-offs, etc.
- The README's Evaluation Criteria section should mention that "document organization and structure" is an evaluation factor — this is the only hint the candidate gets

### ARCHITECTURE DIAGRAM INSTRUCTIONS (CRITICAL — MUST BE PERFECT):
The README.md MUST include a mermaid architecture diagram showing the CURRENT system. This diagram must be syntactically perfect and render without errors. Follow these rules strictly:

**Diagram content rules:**
- The diagram MUST only show what CURRENTLY EXISTS in the system — components, services, databases, message brokers, and their connections as they are today
- Do NOT include future/proposed components, dotted lines for "planned" additions, or anything that hints at what the candidate should design
- The diagram is purely factual — it shows the current state of the system, nothing more

**Mermaid syntax rules to avoid rendering errors:**
- Always use `graph TD` or `graph LR` for flowcharts — never mix diagram types
- Node IDs must be simple alphanumeric (e.g., `A`, `B`, `ServiceA`) — no spaces, no special characters in IDs
- Use square brackets for labels: `A[Service Name]`, `B[(Database)]`, `C{{{{Message Broker}}}}`
- For subgraphs, always include an `end` keyword: `subgraph Name ... end`
- Arrow syntax: use `-->` for solid arrows, `-.->` for dotted arrows — do NOT use `-->>` or other invalid arrows in flowcharts
- Every opening bracket/parenthesis must have a matching close — double-check all `[`, `(`, `{{{{`, `[(` have their matching `]`, `)`, `}}}}`, `)]`
- Do NOT put special characters like `(`, `)`, `/`, `&`, `#` inside node labels unless wrapped in quotes: `A["Label with parens"]`
- Do NOT use HTML tags or markdown inside mermaid nodes
- Keep labels short and clean — long labels cause rendering issues
- Test mentally: read through each line and verify every node reference, bracket, and arrow is valid
**Sequence diagram syntax rules (for data flow diagrams):**
- Start with `sequenceDiagram` on its own line
- Declare participants before use: `participant A as Service Name`
- Use `->>` for synchronous calls, `-->>` for async responses — these are ONLY valid in sequenceDiagram, NOT in flowcharts
- Use `->` for solid arrows without arrowheads, `--)` for async fire-and-forget
- Every `alt`, `opt`, `loop`, `par`, `critical` block MUST have a matching `end`
- Use `Note over A,B: text` for annotations — NOT `Note left of` or `Note right of` with long text
- Do NOT put special characters in message labels — keep them simple text
- Do NOT nest `alt` inside `opt` unless absolutely necessary — each nesting level adds error risk
- Keep participant names short — long names cause rendering issues

**Example of correct flowchart (for architecture):**
```
graph TD
    Client[Client Application] --> LB[Load Balancer]
    LB --> API[Go API Service]
    API --> Auth[Auth Service]
    API --> DB[(PostgreSQL)]
    API --> Cache[(Redis Cache)]
    API --> MQ{{{{Message Broker}}}}
    MQ --> Worker[Worker Service]
    Worker --> DB
```

**Example of correct sequence diagram (for data flow):**
```
sequenceDiagram
    participant C as Client
    participant LB as Load Balancer
    participant API as Go API
    participant DB as Database
    participant MQ as Message Broker
    participant W as Worker

    C->>LB: POST /orders
    LB->>API: Forward request
    API->>DB: Insert order
    DB-->>API: Order saved
    API--)MQ: Publish OrderCreated event
    API-->>LB: 201 Created
    LB-->>C: Order response
    MQ->>W: Deliver event
    W->>DB: Update downstream state
```

**Common errors to AVOID:**
- Missing `end` after subgraph, alt, opt, loop, or par
- Unbalanced brackets: `A[Label(` instead of `A["Label()"]`
- Using spaces in node IDs: `Order Service` instead of `OrderService[Order Service]`
- Using `-->>` in flowcharts (only valid in sequenceDiagram)
- Using `-->` in sequenceDiagram (use `->>` or `-->>` instead)
- Forgetting to close parentheses in database nodes: `DB[(PostgreSQL]` instead of `DB[(PostgreSQL)]`
- Putting parentheses or special characters in message text — use simple text instead
- Missing participant declaration before use in sequenceDiagram
- Forgetting `end` for nested alt/opt/loop blocks — count every opening block and make sure each has an `end`

### CODE FILE INSTRUCTIONS (CRITICAL):
The repo must contain the actual Go project folder structure with real code files showing the current system. This is NOT pseudo code and NOT a full line-by-line production implementation. It is structural/high-level code that shows:

**What the code files SHOULD contain:**
- Real package/file structure with proper folder organization (e.g., `cmd/orders/main.go`, `internal/transport/http/order_handler.go`, `internal/service/order_service.go`, `internal/repository/order_repository.go`, `internal/domain/order.go`)
- Function/method signatures with brief high-level logic (what the function does, not every line)
- Real HTTP route registrations or gRPC server setup, handler functions, service methods, repository methods, model structs with tags, middleware functions, and config
- Configuration files (`go.mod` with real dependencies, `.env.example`, config loader package)
- Middleware functions showing auth, validation, recovery, request-logging middleware composition
- Service-layer packages showing business logic flow at a high level
- Repository packages showing data access patterns (database/sql or sqlx or gorm or pgx — whatever the current system uses)
- Worker / job processor packages if applicable (e.g., `internal/worker/email_worker.go`)
- Message consumer/producer packages if applicable
- `docker-compose.yml` if the system uses containers
- Migration files (e.g., `migrations/0001_initial.up.sql`) if applicable

**What the code files must NOT contain:**
- Full line-by-line production implementation — keep functions concise, show the structure and key logic, not every detail
- Pseudo code or fake placeholder code — the code should look like real code, just not exhaustively complete
- TODO comments, "implement this", or any hints about what the candidate should design or change
- Comments suggesting what needs to be added, improved, or redesigned
- Any indication of what the candidate's design should include

**Style guideline:**
- Each code file should feel like reading a real Go project's source — proper `package` declarations, `import` blocks, idiomatic Go (error returns, context propagation, struct receivers), real method signatures, real model structs with tags
- Functions should have real signatures and show the high-level flow (e.g., "fetch from DB, transform, publish to broker") with enough code to understand what happens, but not every utility method or edge case
- Config files should show real dependencies (`go.mod`), database connection setup, broker settings
- The candidate should be able to browse these files and understand: "this is what the system currently does and how it's built"

**Folder structure must be realistic:**
- Follow standard Go project conventions: `cmd/<service-name>/main.go` for entrypoints, `internal/...` for packages not meant for external import, `pkg/...` for exported reusable packages (only if applicable)
- Within `internal/`: typical layout includes `transport/http/`, `transport/grpc/`, `service/`, `repository/`, `domain/` (or `models/`), `middleware/`, `worker/`, `config/`
- Include build files (`go.mod`), config files, source files, and schema/migration files as appropriate
- The folder structure itself tells the candidate about the system's current architecture

**CRITICAL RULES for code files:**
- Code files are READ-ONLY context — they show what exists today
- Do NOT include any language that tells the candidate what to implement, change, or use
- Do NOT add comments like "// this could be improved" or "// consider replacing with X"
- The code simply shows the current state — the candidate figures out the design challenge from the README and makes their own technology choices

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task with real code context** — The repo contains actual Go project code files (source packages, config, build files) showing the current system. The candidate reads these to understand the current state, then writes their design in DESIGN.md.
3. **code_files MUST include**: README.md, .gitignore, DESIGN.md, AND the full project folder structure with real code files (source code, build/config files, migration/schema files). The code shows what currently exists — it is NOT the candidate's deliverable.
4. **DESIGN.md must be blank** — only a title and one-line instruction. NO sections, NO guiding questions, NO hints
5. **The candidate decides the structure** — this is part of the assessment at intermediate level
6. **name** must be kebab-case and end with "-design", e.g., "order-processing-pipeline-design"
7. **Task must be completable in {minutes_range} minutes** — scope to 2-3 services max, not a full microservices ecosystem
8. **answer field** is the evaluator's answer key — make it thorough with specific technology choices, data model details, concurrency/goroutine strategy, and trade-off rationale. This is for evaluators only, never shown to candidates.
9. **definitions** must include 4-6 relevant architecture/design terms (e.g., goroutine leak, worker pool, context cancellation, circuit breaker, saga pattern, connection pool, fan-out/fan-in, errgroup, backpressure, idempotency key)
10. **Do NOT include any TODO comments, "implement this", hints, or placeholder text** in ANY file — especially not in code files. The code shows what EXISTS, nothing more.
11. **Code files must be structural/high-level** — show package layouts, function signatures, key logic flows, and config. NOT full line-by-line production code, NOT pseudo code. The candidate should understand the current system by browsing the code.
12. **README.md formatting**: Task Overview MUST be exactly 3-4 concise lines. ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no prose blocks. Every piece of information should be a discrete bullet point.
13. **question field** must be concise — 4-6 lines only, not long paragraphs
14. **NEVER prescribe technology choices** — Do NOT tell the candidate what tech stack, framework, infrastructure, database, message broker, HTTP framework (net/http / Gin / Echo / Fiber / Chi / etc.), gRPC framework, ORM (gorm / sqlx / sqlc / ent / etc.), or any tool to use anywhere in ANY file. Only describe/show what currently exists. The candidate's technology choices and justifications are a core evaluation criterion. This applies to README.md, constraints, code files, comments — NOWHERE should the task mandate what the candidate must use.
15. **Code files must have realistic folder structure** — follow standard Go project conventions (`cmd/` for entrypoints, `internal/` for internal packages organized by responsibility, optional `pkg/` for reusable exported packages). The folder structure itself communicates the current architecture.
16. **Mermaid diagrams MUST be syntactically perfect** — Both the architecture diagram (flowchart) AND the data flow diagram (sequence diagram) must render without errors. Double-check: all brackets/parentheses are balanced, node IDs have no spaces or special characters, every `subgraph`/`alt`/`opt`/`loop`/`par` has a matching `end`, arrows use valid syntax for the diagram type (`-->` for flowcharts, `->>` for sequenceDiagram), participants are declared before use in sequenceDiagram, and special characters in labels are avoided or quoted. Both diagrams MUST only show the CURRENT system — no proposed/future components or flows, no hints about what to design. Read through each diagram line-by-line before outputting to verify correctness.
"""

PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE)": [
        PROMPT_SYSTEM_DESIGN_GOLANG_CONTEXT_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_GOLANG_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_GOLANG_INTERMEDIATE_INSTRUCTIONS,
    ]
}
