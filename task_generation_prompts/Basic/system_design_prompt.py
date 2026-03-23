PROMPT_SYSTEM_DESIGN_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a System Design assessment task.

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
- CRITICAL: This is a DESIGN task — the candidate will NOT write any code. They will produce a written design document.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What system or feature will the candidate design? (Describe the business domain, technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Describe the expected sections in their design document and how the challenge aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_BASIC_INSTRUCTIONS = """
## GOAL
As a senior systems architect with 15+ years of experience designing production systems, you are given a list of real-world scenarios and proficiency levels for System Design.
Your job is to generate a complete System Design assessment task where the candidate produces a written design document — NOT code. The candidate receives a GitHub repo with a problem statement and a structured template (DESIGN_TEMPLATE.md) that they must fill in with their design.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any code, fix bugs, or implement features
- The candidate receives a GitHub repo containing ONLY markdown files and optional read-only reference files
- The candidate's deliverable is: fill in DESIGN_TEMPLATE.md with their system design
- There is NO runnable code, NO Docker, NO tests, NO build files
- The assessment measures design thinking, trade-off analysis, and communication — not coding ability

## INSTRUCTIONS

### Nature of the Task
- Present a realistic system design challenge drawn from the provided scenarios
- The question must clearly state: what needs to be designed, the constraints, and what sections the design document should cover
- The design challenge should focus on a SINGLE component or feature — not an entire distributed system
- Most constraints should be given to the candidate to reduce analysis paralysis and keep the task focused
- Candidates should be choosing between 1-2 key technology/approach decisions, not designing everything from scratch
- The question scenario must be clear, with realistic scale numbers, constraints, and business context
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.

### Proficiency Level: BASIC
For BASIC level System Design, the questions should test:
- **Component Design**: Breaking a feature into logical components and defining their responsibilities
- **API Contract Design**: Defining RESTful endpoints with request/response schemas, status codes, and error handling
- **Data Modeling**: Choosing appropriate data stores, designing table schemas, defining entity relationships
- **Basic Trade-offs**: SQL vs NoSQL, sync vs async, monolith vs simple service split, caching vs no caching
- **Sequence/Flow Design**: Drawing how a request flows through components (using text or mermaid diagrams)
- **Basic Failure Handling**: What happens when a dependency is down? Simple retry/fallback strategies
- The candidate is NOT expected to handle: distributed consensus, CAP theorem, sharding, multi-region, complex event sourcing, or advanced scaling patterns

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine architectural reasoning, not memorization of design patterns
- The design challenge should require trade-off analysis that goes beyond what a simple AI query can provide

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given requirements and constraints, design a new component/service
2. **Extend existing system**: Given a description of an existing system, design how to add a major feature (provide reference files describing the current system)
3. **Diagnose & redesign**: Given a problematic architecture description, identify issues and propose a better design (provide reference files showing the current flawed architecture)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Full design challenge description including: the business context, what system/component needs to be designed, specific constraints (scale, latency, tech preferences), and exactly what sections the design document should cover. This should be 3-5 paragraphs — detailed enough that the candidate has complete clarity on what to produce.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (business scenario), Design Challenge (what to design), Constraints (scale/tech/time), Deliverable (fill in DESIGN_TEMPLATE.md), Evaluation Criteria (what makes a good design)",
      ".gitignore": "*.log\\n.DS_Store\\n*.tmp\\n",
      "DESIGN_TEMPLATE.md": "Structured template with 4-5 section headers and 1-2 guiding sub-questions per section. Sections are EMPTY — candidate fills them in. Typical sections: Component Architecture, API Contract, Data Model, Trade-offs & Alternatives, Failure Handling. Each section has guiding questions like 'What are the main components? How do they communicate?'",
      "reference/optional_file.md": "ONLY for extend/redesign tasks — describes the current system architecture, existing API contracts, or current data model. Clearly marked as READ-ONLY context."
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Example: 'The candidate produces a complete design document covering component architecture, API contracts, data model, and trade-off analysis for the notification service.'",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level design challenge, (2) what the candidate must produce (fill in DESIGN_TEMPLATE.md), (3) key evaluation criteria (clarity, trade-off reasoning, completeness)",
   "pre_requisites": "Bullet-point list of knowledge areas needed. Example: Understanding of REST API design, basic database concepts (SQL/NoSQL), ability to create architecture diagrams in text or mermaid format, familiarity with common web architecture patterns (client-server, request-response, message queues).",
   "answer": "High-level reference design approach — what a good design would include. This is the evaluator's answer key, NOT shown to candidates. Cover: recommended component breakdown, suggested data model, key trade-off decisions and their rationale, expected API contracts.",
   "hints": "A single line nudge toward the right design direction without giving away the answer. Example: 'Consider how decoupling the notification dispatch from the main request flow could improve response times.'",
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

**CRITICAL REQUIREMENT**: Task Overview section MUST contain 2-3 meaningful sentences describing the business scenario and why this design matters.
ALL sections must have substantial content — no empty or placeholder text allowed.

#### Task Overview
2-3 sentences describing the business scenario, the current situation (if extending/redesigning), and why this design challenge matters to the business.

#### Design Challenge
Clear statement of what the candidate needs to design. Reference the sections in DESIGN_TEMPLATE.md.

#### Constraints
Concrete numbers and boundaries:
- Scale (users, requests/day, data volume)
- Latency/performance requirements
- Technology preferences or restrictions
- Budget/infrastructure constraints (e.g., "1-2 services max")

#### Deliverable
"Fill in all sections of DESIGN_TEMPLATE.md with your design. Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate."

#### Evaluation Criteria
What makes a good design document:
- Completeness (all sections addressed)
- Trade-off reasoning (alternatives considered, choices justified)
- Clarity (another engineer could implement from this design)
- Feasibility (design works within the stated constraints)

### NOT TO INCLUDE in README:
- Setup instructions or commands (there is nothing to set up)
- The actual design solution
- Specific technology recommendations that would give away the answer
- Step-by-step implementation guides

### DESIGN_TEMPLATE.md INSTRUCTIONS:
- Must have clear section headers (## level) matching what the README's Design Challenge section asks for
- Each section has 1-2 guiding sub-questions in italics to help the candidate understand what's expected
- ALL sections are left EMPTY for the candidate to fill in
- Typical sections for BASIC level (pick 4-5 relevant ones per task):
  - **Component Architecture**: What are the main components/services? How do they interact? (Include a diagram)
  - **API Contract**: What endpoints or interfaces exist? What are the request/response formats?
  - **Data Model**: What are the core entities? What relationships exist? Which data store and why?
  - **Request Flow**: How does a typical request flow through the system? (Sequence diagram encouraged)
  - **Trade-offs & Alternatives**: What alternatives did you consider? Why did you choose this approach?
  - **Failure Handling**: What happens when [specific component] fails? How does the system recover?
  - **Caching Strategy**: What data is cached? Where? What invalidation strategy?
- DO NOT include the answer or solution hints in the template
- DO NOT include example responses in the template sections

### Reference Files (ONLY for extend/redesign tasks):
- Place in a `reference/` directory
- Use descriptive names like `current_architecture.md`, `existing_api.md`, `current_schema.md`
- Keep concise — just enough to understand the current system
- Clearly mark as "READ-ONLY — do not modify these files"
- For "design from scratch" tasks, do NOT include reference files

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task** — NO source code files (.py, .java, .go, etc.), NO Dockerfiles, NO requirements.txt, NO package.json, NO test files in code_files
3. **code_files contains ONLY**: README.md, .gitignore, DESIGN_TEMPLATE.md, and optionally reference/*.md files
4. **DESIGN_TEMPLATE.md** sections must align exactly with what the question and README ask for
5. **The template must NOT contain the answer** — only guiding questions per section
6. **name** must be kebab-case and end with "-design", e.g., "notification-service-design"
7. **Task must be completable in {minutes_range} minutes** — scope accordingly (single component, not full system)
8. **answer field** is the evaluator's answer key — make it thorough with specific technology choices, data models, and trade-off rationale
9. **definitions** must include 3-5 relevant architectural/design terms that a BASIC-level candidate might need clarified
10. **Do NOT include any TODO comments or placeholder text** in any file
"""

PROMPT_REGISTRY = {
    "System Design (BASIC)": [
        PROMPT_SYSTEM_DESIGN_CONTEXT,
        PROMPT_SYSTEM_DESIGN_INPUT_AND_ASK,
        PROMPT_SYSTEM_DESIGN_BASIC_INSTRUCTIONS,
    ]
}
