PROMPT_SYSTEM_DESIGN_SQL_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_SQL_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a SQL System Design assessment task.

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
- CRITICAL: This is a DESIGN task — the candidate will NOT write any SQL code. They will produce a written design document focused on SQL/database architecture and data engineering.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What system or feature will the candidate design? (Describe the business domain, SQL/data engineering technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Note: the candidate receives a BLANK DESIGN.md with no guided sections — they must decide their own document structure. Describe what a strong design document would cover and how the challenge aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_SQL_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior data architect with 15+ years of experience designing production database systems and data platforms, you are given real-world scenarios and proficiency levels for SQL System Design.
Your job is to generate a complete System Design assessment task where the candidate produces a written design document — NOT code. The candidate receives a GitHub repo with a problem statement, optional reference files describing an existing database system, and a blank design document (DESIGN.md) where they write their design from scratch — no guided template, no pre-defined sections. The candidate must decide what sections to include, how to structure their document, and what to cover. This itself is part of the assessment.

This task specifically tests SQL/database architecture and data engineering design skills: how to design database schemas at scale, choose between storage engines and database technologies, architect data pipelines and ETL workflows, design partitioning and sharding strategies, handle data consistency and integrity, and reason about performance trade-offs specific to relational databases.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any SQL code, fix queries, or implement database objects
- The candidate receives a GitHub repo containing ONLY markdown files and optional read-only reference files
- The candidate's deliverable is: write their complete system design in DESIGN.md (a blank file — no template, no guided sections)
- The candidate must decide their own document structure — this tests their ability to organize and communicate a design
- There is NO runnable SQL, NO Docker containers, NO init_database.sql, NO sample_queries.sql
- The assessment measures database architecture thinking, data modeling expertise, trade-off analysis, ability to structure a design document, and technical communication

## INSTRUCTIONS

### Nature of the Task
- Present a realistic SQL/database system design challenge drawn from the provided scenarios
- The design challenge must be rooted in the SQL/data engineering ecosystem — the candidate should reason about database-specific patterns, technologies, indexing strategies, and trade-offs
- The question must clearly state: what needs to be designed, the constraints, the current database stack (if extending), and what the design document should cover
- The challenge should involve multi-component data architecture with concerns around schema design, data flow, performance, and consistency
- Candidates should make 2-3 key technology/architecture decisions with justification
- Use realistic scale numbers, SLA requirements, and business constraints
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.

### Proficiency Level: INTERMEDIATE (SQL/Data Engineering-Specific)
For INTERMEDIATE level SQL System Design, the questions should test:
- **Schema Architecture**: Designing normalized vs denormalized schemas for different workloads (OLTP vs OLAP), star/snowflake schema design, dimensional modeling, slowly changing dimensions (SCD Type 1/2/3)
- **Partitioning & Sharding Strategy**: Table partitioning (range, list, hash), partition pruning awareness, horizontal sharding approaches, shard key selection trade-offs
- **Indexing Strategy**: B-tree, GIN, GiST, BRIN index selection, partial indexes, expression indexes, covering indexes, composite index column ordering, index maintenance overhead
- **Data Pipeline Architecture**: ETL vs ELT design, staging tables, data quality validation, incremental vs full load strategies, CDC (Change Data Capture) patterns
- **Query Performance Design**: Materialized views, query pre-computation strategies, read replicas for analytics, connection pooling (PgBouncer), query plan awareness in schema design
- **Transaction & Consistency Design**: Isolation levels for mixed workloads, advisory locks for application-level coordination, optimistic vs pessimistic locking strategies, eventual consistency patterns
- **Data Lifecycle Management**: Archival strategies, data retention policies, hot/warm/cold storage tiers, time-series data management
- **Stored Procedures & Functions**: When to use server-side logic vs application-side, PL/pgSQL design patterns, trigger design for audit trails and data integrity
- **Monitoring & Observability**: pg_stat_statements, auto_explain, slow query identification, connection pool monitoring, replication lag tracking
- **Migration & Evolution**: Schema migration strategies, zero-downtime migrations, backward-compatible changes, blue-green database deployments
- The candidate IS expected to reason about data consistency, availability, and performance at a practical level
- The candidate is NOT expected to: design custom storage engines, build distributed databases from scratch, or solve theoretical database research problems

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine architectural reasoning specific to the SQL/data engineering ecosystem
- The design challenge should require nuanced trade-off analysis (e.g., "why partition by date vs by tenant for this specific use case?") that tests real understanding

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given requirements, design a new database architecture or data platform — define schema, indexes, data flows, and infrastructure choices within the SQL/data engineering ecosystem
2. **Extend existing system**: Given a description of an existing database system (single PostgreSQL instance, data warehouse, etc.), design how to add a major feature or scale to new requirements — provide reference files describing the current database architecture
3. **Diagnose & redesign**: Given a problematic database architecture description (performance bottlenecks, scaling issues, data integrity problems), identify issues and propose a better design — provide reference files showing the current flawed architecture with SQL-specific details

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Concise design challenge description in 4-6 lines covering: business context, what database system/component needs to be designed, current SQL tech stack (if extending), key constraints (scale, latency, data volume), and what the candidate must deliver. Keep it brief and to the point — no long paragraphs.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (3-4 concise lines only), Design Challenge (bullet points only), Constraints (bullet points with concrete numbers), Deliverable (bullet points only), Evaluation Criteria (bullet points only). EVERY section except Task Overview MUST use bullet points exclusively — no paragraphs.",
      ".gitignore": "*.log\\n.DS_Store\\n*.tmp\\n",
      "DESIGN.md": "A blank file with ONLY a single title line: '# System Design Document' and a one-line instruction: 'Write your complete system design below. You decide the structure, sections, and level of detail.' — NOTHING else. No section headers, no guiding questions, no hints. The candidate must organize the document entirely on their own.",
      "reference/current_architecture.md": "Description of the current database system — database engines, schema overview, replication setup, ETL pipelines, monitoring. MUST include a mermaid architecture diagram showing high-level system components, databases, data pipelines, caching layers, and their connections. Follow the diagram with bullet points describing each component. Include enough detail about the SQL stack (PostgreSQL version, partitioning config, index strategy, connection pool setup) that the candidate can reason about what to change.",
      "reference/current_flow.md": "Description of the current data flow through the system. MUST include a mermaid data flow diagram (sequence diagram or flowchart) showing how data moves through the system for the primary use case — from data ingestion to final query result. Follow the diagram with bullet points describing each step in the flow. Show end-to-end flow from data arrival to analytical query result.",
      "reference/current_schema.md": "Current database schema, entity relationships, and data model. Optional but recommended.",
      "reference/current_performance.md": "Current performance characteristics, bottlenecks, and monitoring data. Optional."
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Should mention SQL-specific design artifacts (e.g., schema architecture, partitioning strategy, indexing design, data pipeline architecture).",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level SQL/data engineering design challenge, (2) what the candidate must produce (fill in DESIGN.md), (3) key evaluation criteria (database architecture knowledge, trade-off reasoning, completeness, clarity)",
   "pre_requisites": "Bullet-point list of knowledge areas needed. Must include SQL-specific items: understanding of relational database architecture (PostgreSQL preferred), experience with schema design and normalization (3NF, star schema, dimensional modeling), familiarity with indexing strategies (B-tree, GIN, partial, covering indexes), knowledge of partitioning and sharding concepts, understanding of transaction isolation levels and consistency patterns, experience with ETL/data pipeline design, awareness of query optimization and EXPLAIN plan interpretation, ability to create architecture diagrams in text or mermaid format.",
   "answer": "Thorough reference design approach — the evaluator's answer key. Must include: recommended schema design with rationale (e.g., 'star schema with date-based range partitioning on the fact table because analytical queries always filter by date range'), specific indexing strategy, partitioning approach, data pipeline design, consistency and transaction strategy, performance optimization approach with SQL-specific patterns (materialized views, connection pooling), and operational considerations (monitoring, migration strategy). This should be 4-6 paragraphs covering each DESIGN.md section.",
   "hints": "A single line nudge toward the right design direction using SQL/data engineering context. Example: 'Consider how range partitioning on the time dimension combined with materialized views could address both the ingestion throughput and analytical query latency requirements.'",
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
- Use concrete SQL/data engineering terminology where relevant.

#### Task Overview
Exactly 3-4 concise sentences describing: the business scenario, the current SQL tech stack (if extending/redesigning), and why this design challenge matters. Keep it brief — detailed information goes in other sections.

#### Design Challenge
All content MUST be bullet points:
- What the candidate needs to design
- What is in scope
- What is out of scope
- Reference to DESIGN.md as the deliverable

#### Constraints
All content MUST be bullet points with concrete numbers and boundaries including SQL-specific constraints:
- Scale (data volume, row counts, daily ingestion rate, query volume)
- Latency/SLA requirements (query response time, data freshness, ETL completion window)
- Technology constraints or preferences (must use PostgreSQL, must be compatible with existing data warehouse, etc.)
- Infrastructure constraints (number of database instances, storage budget, connection pool limits)
- Team/org constraints if relevant (team familiarity with specific database technologies)

#### Deliverable
All content MUST be bullet points:
- Write your complete system design in DESIGN.md
- You decide the structure, sections, and level of detail
- Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate
- A strong design document is one that another engineer could use to implement the system

#### Evaluation Criteria
All content MUST be bullet points — what makes a good design document at the intermediate SQL level:
- Document organization (logical structure, well-chosen sections, clear flow — the candidate defines their own structure)
- Completeness (all critical aspects of the design addressed with sufficient depth)
- SQL/data engineering ecosystem awareness (appropriate database, schema, indexing, and pipeline choices)
- Trade-off reasoning (alternatives considered with SQL-specific pros/cons, choices justified)
- Clarity (another data engineer could implement from this design)
- Feasibility (design works within the stated constraints and database characteristics)
- Operational readiness (monitoring, migration strategy, data lifecycle management)

### NOT TO INCLUDE in README:
- Setup instructions or commands
- The actual design solution or specific schema recommendations
- Step-by-step implementation guides
- Specific SQL queries, index definitions, or schema DDL that reveal the answer

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
- A strong intermediate candidate is expected to independently identify relevant sections like: schema design, indexing strategy, partitioning approach, data pipeline architecture, consistency model, performance optimization, migration strategy, etc.
- The README's Evaluation Criteria section should mention that "document organization and structure" is an evaluation factor — this is the only hint the candidate gets

### Reference Files:
- Place in a `reference/` directory
- Use descriptive names: `current_architecture.md`, `current_flow.md`, `current_schema.md`, `current_performance.md`
- **`reference/current_architecture.md`** (REQUIRED for ALL tasks): MUST include a mermaid architecture diagram (```mermaid code block) showing the high-level system components, databases, data pipelines, caching layers, and their connections. Follow the diagram with bullet points describing each component. Use C4 container diagram, component diagram, or data architecture diagram style.
- **`reference/current_flow.md`** (REQUIRED for ALL tasks): MUST include a mermaid data flow diagram (```mermaid code block) — sequence diagram or flowchart — showing how data moves through the system for the primary use case / data pipeline. Follow the diagram with bullet points describing each step. Show end-to-end flow from data ingestion to analytical result.
- Include SQL-specific details: PostgreSQL configuration, partitioning setup, index configuration, connection pool settings, replication topology
- Keep concise — just enough to understand the current database system
- Clearly mark as "READ-ONLY reference material — do not modify these files"
- For "design from scratch" tasks, the architecture and flow files describe the target system context that the candidate must design within
- For extend/redesign tasks, the files describe the existing system the candidate must work with
- All content in reference files MUST use bullet points for descriptions (after diagrams)

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task** — NO SQL files (.sql), NO Docker files, NO init_database.sql, NO sample_queries.sql, NO application code in code_files
3. **code_files contains ONLY**: README.md, .gitignore, DESIGN.md, and reference/*.md files (reference/current_architecture.md and reference/current_flow.md are REQUIRED for all tasks; other reference files are optional)
4. **DESIGN.md must be blank** — only a title and one-line instruction. NO sections, NO guiding questions, NO hints
5. **The candidate decides the structure** — this is part of the assessment at intermediate level
6. **name** must be kebab-case and end with "-design", e.g., "data-warehouse-pipeline-design"
7. **Task must be completable in {minutes_range} minutes** — scope to 2-3 database components max, not a full enterprise data platform
8. **answer field** is the evaluator's answer key — make it thorough with specific schema choices, indexing strategy, partitioning approach, and trade-off rationale
9. **definitions** must include 4-6 relevant SQL architecture/design terms (e.g., star schema, materialized view, partitioning, CDC, connection pooling, isolation level)
10. **Do NOT include any TODO comments or placeholder text** in any file
11. **SQL ecosystem specificity**: The design challenge must require SQL/database-specific reasoning — if you could solve it the same way without database knowledge, it's too generic
12. **Reference files MUST include mermaid diagrams**: `reference/current_architecture.md` MUST have a mermaid architecture diagram, `reference/current_flow.md` MUST have a mermaid data flow diagram (sequence diagram or flowchart). These two reference files are REQUIRED for ALL tasks.
13. **README.md formatting**: Task Overview MUST be exactly 3-4 concise lines. ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no prose blocks. Every piece of information should be a discrete bullet point.
14. **Diagrams must be valid mermaid syntax** — use ```mermaid code blocks with proper graph/sequenceDiagram/flowchart syntax
15. **question field** must be concise — 4-6 lines only, not long paragraphs
"""

PROMPT_REGISTRY = {
    "SQL - System Design (INTERMEDIATE)": [
        PROMPT_SYSTEM_DESIGN_SQL_CONTEXT_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_SQL_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_SQL_INTERMEDIATE_INSTRUCTIONS,
    ]
}
