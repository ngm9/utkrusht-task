# Curated prompt for Object Oriented Programming - Design Patterns (BASIC).
# Language-agnostic by design: the language/runtime is derived from the scenario,
# not hard-coded here. Keep this in sync with dsa_basic_prompt.py conventions.
TASK_SHAPE = "non_infra"


PROMPT_OOP_DESIGN_PATTERNS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

20 with a mix across Kafka, Spark, CDC, ETL/ELT

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_OOP_DESIGN_PATTERNS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Object Oriented Programming - Design Patterns assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for BASIC proficiency — a candidate with roughly 1-2 years of software engineering experience
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role — OOP design patterns applied inside a real product module, not textbook exercises in isolation
- CRITICAL: This is a pure local coding and refactoring task. Do NOT create docker-compose.yml, Dockerfile, init_database.sql, database configuration, cache configuration, queue configuration, or any datastore setup
- CRITICAL: The language and runtime are derived from the scenario — do NOT assume Python

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What small feature or refactor will the candidate complete? (Describe the business domain, the existing OO design problem, and what a correct solution looks like)
2. What language does this scenario imply, and what will the starter project structure look like? (Package layout, test framework, build manifest)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_OOP_DESIGN_PATTERNS_BASIC_INSTRUCTIONS = """
# Object Oriented Programming - Design Patterns Basic Task Requirements

## GOAL
As a technical architect experienced in object-oriented programming and design patterns across multiple languages, you are given real-world scenarios and proficiency levels for OOP Design Patterns work at the BASIC level. Your job is to generate an entire task definition — code files, README.md, expected outcomes, etc. — that assesses a 1-2 yoe candidate's ability to recognise a design smell, apply an appropriate entry-level GoF pattern, and keep the observable behaviour correct and tested.

**LANGUAGE / RUNTIME IS DERIVED FROM THE SCENARIO.** Do NOT assume Python. The chosen scenario determines the application stack (file extensions, module paths, runtime hints) — the generated starter code, file structure, build/test commands, and test framework MUST follow whatever language the scenario implies (e.g. Python with `pytest`, TypeScript/Node with `jest` or `vitest`, Java with JUnit + Maven/Gradle, Go with the built-in test runner, C# with xUnit/NUnit). If the scenario is language-agnostic in wording, default to the most natural language for the domain described (e.g. Java/Kotlin for enterprise, TypeScript for web/API services, Python for data/scripting pipelines, C# for .NET backends).

## INSTRUCTIONS

### Nature of the Task
- The task must ask the candidate to apply ONE entry-level GoF pattern to fix a small, well-scoped OO design problem inside an existing module — NOT to build a project from scratch or architect a multi-module system.
- The starter project MUST include a small, runnable package (in whatever language the scenario implies) with the design smell already present, plus at least one test file using the language's idiomatic test framework that exercises the existing behaviour.
- The design problem must be visible in the code but not exaggerated: a God Object requiring a large redesign is OUT OF SCOPE; a class that branches on type codes, accumulates carrier-specific logic, duplicates notification dispatch, or exposes a constructor that leaks internals is appropriate.
- DO NOT REVEAL THE PATTERN NAME OR THE FIX in the starter code, README, or question. The candidate should infer what to do from reading the tests and the code.
- The candidate should write or update unit tests to pin the new or corrected behaviour. Keep mocking simple — plain stubs or fakes; do NOT require advanced mocking libraries.
- Time Constraint: The task must be completable within {minutes_range} minutes by a BASIC-level candidate.

### BASIC PROFICIENCY SCOPE (1-2 yoe — what the task may assess)
Tasks MUST align with BASIC OOP Design Patterns. The task may assess ONE of the following; do NOT go beyond this scope into advanced multi-pattern combinations or architectural concerns:

- **Adapter**: wrap an incompatible third-party or legacy interface so the consuming service stays insulated from vendor-specific field names or method signatures.
- **Facade**: hide a complex subsystem (multiple service calls, multi-step setup) behind a single simple interface so callers aren't tangled in internal dependencies.
- **Decorator**: add optional behaviour (logging, caching, validation, auditing) to an object at runtime without subclassing, keeping the base class clean.
- **Strategy**: replace a growing `if/elif/switch` over behaviour type (pricing tiers, shipping carriers, payment methods) with a family of interchangeable algorithms selected at runtime.
- **Observer / Event listener**: decouple a producer from multiple consumers by having listeners subscribe to events rather than being called directly.
- **Template Method**: lift a shared algorithm skeleton into a base class and let subclasses fill in the variable steps without altering the skeleton.
- **Factory Method / Simple Factory**: centralise object creation logic so callers request a product by type without knowing the concrete class; useful when adding a new variant should not require editing the consumer.

Do NOT require: multi-pattern combinations (Abstract Factory + Prototype), concurrent/thread-safe Singleton, distributed-system patterns, complex DI containers, reflection-heavy frameworks, or custom pattern variants. Those are INTERMEDIATE+ topics.

### Task Scenario Structure
Each task MUST be defined in two clear parts:

**Current Implementation (what we give the candidate):**
- Describe precisely the design smell the starter code has: duplicated branching logic, an incompatible interface, a bloated class, tightly coupled dispatcher, etc.
- Include realistic class names, method signatures, and a concrete observable failure or extensibility pain that the scenario motivates.
- The **starter code MUST perfectly implement this current broken/smelly state** — it must run, the tests must exercise the existing behaviour, and it MUST NOT accidentally include the fix.

**Required Changes (what the candidate must do):**
- List the specific structural changes the candidate must apply, expressed in terms of OO responsibilities and pattern intent (not in language-specific stdlib symbols).
- Example: "Move carrier-specific field mapping out of the tracking service into a per-carrier wrapper so the service always receives a normalised payload"; "Replace the `if notification_type == X` branching in the dispatcher with a pluggable handler per type"; "Wrap the audit side-effect around the core processor so the processor itself stays unchanged".
- The candidate extends tests to pin the corrected or newly added behaviour.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources: Google, language docs, design pattern references, AI-powered tools, or LLMs.
- The task assesses OO reasoning, code comprehension, and implementation discipline — not rote memorisation of pattern names.
- Use modern conventions for whichever language the scenario implies (Python 3.10+ / PEP 8, modern TypeScript/ESM, Java 17+, Go 1.21+, C# 10+, etc.). Standard library and built-in primitives only — do NOT introduce specialised third-party DI or AOP frameworks unless the scenario truly justifies it.

### Starter Code Requirements

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- The starter code MUST be a complete, working project in the language the scenario implies, runnable with the standard install + test commands for that ecosystem (e.g. Python: `pytest`; Node/TS: `npm test`; Java/Maven: `mvn test`; Go: `go test ./...`; C#: `dotnet test`).
- ZERO syntax errors, ZERO runtime errors on the unmodified starter. Existing tests run and pass against the starter behaviour. Any new tests the candidate adds for the corrected behaviour will fail until the fix is applied.
- The candidate should NOT need to fix project setup to run tests. Their job is the OO refactor and the new tests, not plumbing.

**WHAT MUST BE INCLUDED:**
- A clear source folder layout matching the language's conventions (e.g. `src/shipping/`, `src/notifications/`, `lib/billing/`, `internal/orders/`).
- A test directory using the language's idiomatic test framework.
- The minimum project metadata files for tests to run on a clean checkout (Python: `pyproject.toml`; Node/TS: `package.json` + `tsconfig.json`; Java/Maven: `pom.xml`; Go: `go.mod`; C#: `.csproj`). NO third-party DI or AOP libraries.

**LET THE SCENARIO DECIDE THE FILE LAYOUT.** Filenames, language extensions, and folder structure MUST be derived from the scenario's wording — technology cues, class names it mentions, file paths it references. If the scenario implies Java, generate Java; if it implies TypeScript, generate TypeScript.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the pattern or the fix in the starter code. The design smell MUST be present; the fix MUST NOT.
- DO NOT include `// TODO`, `# hint:`, `// fix me`, or any comment that points at the pattern or the fix.
- DO NOT include the new tests the candidate is asked to add — only the pre-existing tests covering current behaviour.
- DO NOT scaffold unrelated modules that inflate scope beyond the BASIC time budget.
- DO NOT include docker-compose.yml, Dockerfile, database config, environment variables, or any external service setup.

### Code Generation Instructions
Based on real-world scenarios, create an OOP Design Patterns task that:
- Draws inspiration from the selected scenario for business context and the specific design smell
- Matches BASIC proficiency level (1-2 years experience, one focused pattern, no multi-module redesign)
- Can be completed within {minutes_range} minutes — candidate edits land in 1-3 source files + 1 test file
- Tests practical OO judgment: recognising the smell, applying the right pattern, keeping tests green
- Selects a different real-world scenario each time for variety
- Task name: short, descriptive, under 50 characters, kebab-case, domain-inspired (e.g. `carrier-adapter-normalise`, `notification-strategy-refactor`, `order-factory-extract`) — NOT a generic `oop-` prefix

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "kebab-case repo name under 50 chars, domain-specific, not starting with 'oop-'",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 chars, different from the repo name.",
  "question": "Structured task description. MUST include: (1) Current Implementation — the specific design smell present in the starter code and what observable problem it causes or what extension pain it creates. (2) Required Changes — the structural OO improvement the candidate must make, expressed in terms of responsibilities and pattern intent, NOT naming the exact pattern. (3) Expected test workflow and time constraint. Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below — required for every language.",
    ".gitignore": "Standard exclusions for whichever language the scenario implies.",
    "<actual-source-path>": "The smelly implementation at the file path the scenario implies, in the language it implies — the design problem MUST be present in this code.",
    "<project-metadata-file>": "Minimum metadata needed for the test command to run on a clean checkout — chosen from the language's ecosystem (pyproject.toml; package.json + tsconfig.json; pom.xml; go.mod; .csproj; etc.)."
  }},
  "answer": "Evaluator-facing high-level solution approach: which BASIC-level GoF pattern fits the problem and why, what responsibilities move or get separated, which tests prove the fix, and what the candidate's code must demonstrate. Do NOT give exact code.",
  "definitions": {{
    "term_1": "definition_1",
    "term_2": "definition_2",
    "term_3": "definition_3"
  }},
  "hints": "Single line nudging the candidate toward the right OO insight without naming the pattern, the class to add, or any language-specific symbol. E.g. 'Think about where carrier-specific knowledge belongs and whether the service layer should be aware of it at all.'",
  "outcomes": "Expected results after completion in 2-3 lines: tests pass, the design smell is gone, the specific extensibility concern the scenario raised is resolved, and the core class stays clean.",
  "pre_requisites": "Exactly 2–3 concise bullets. Each covers ONE item: (1) runtime/toolchain required, (2) repo/environment setup, (3) key domain knowledge if non-obvious. Each bullet ≤ 120 chars. No padding, no sub-lists.",
  "short_overview": "Exactly 3 plain sentences: first state the business domain and the design problem in the starter code, second state what the candidate must do, third state what success looks like. No label prefixes like 'Business problem:' or 'Technical focus:'."
}}

## README.md STRUCTURE (OOP Design Patterns Basic)

The README.md must contain EXACTLY these four sections in this order — no others:
  - Task Overview
  - Objectives
  - Helpful Tips
  - How to Verify

### Task Overview (2-3 substantial sentences)
Describe the business scenario, the current state of the code, and why the design problem matters to the product. Never mention the pattern name, the class to add, or any implementation step. Never include setup commands.

### Objectives (4-6 bullets)
Describe the **observable end-state** the candidate must reach. Must NOT name the pattern, the new class, or any stdlib/framework symbol that points at the fix.

**Allowed phrasing — describes outcome, hides solution:**
- "A newly onboarded carrier returns status data in a different shape, and the shipment lookup should produce the same response fields for customers regardless of which carrier handled the package."
- "Adding a new notification channel should not require editing the dispatcher class itself."
- "The discount calculation for a new customer tier can be added without modifying the existing pricing class."

**FORBIDDEN phrasing — names the fix:**
- ❌ "Create an Adapter class that wraps CarrierYClient." *(names the pattern)*
- ❌ "Use the Strategy interface and implement a concrete class per tier." *(names the pattern + structure)*
- ❌ "Add a subscribe() method to the dispatcher." *(prescribes the API)*

### Helpful Tips (4-5 bullets)
Practical guidance that guides discovery without revealing the fix. Each bullet starts with "Consider", "Think about", "Explore", "Review", or "Analyze". Never name the pattern, the class to introduce, or any language-specific symbol.

### How to Verify (4-6 bullets)
Frame verification in terms of observable outcomes. Mention running the language's test command (e.g. `pytest -q`, `npm test`, `mvn test`, `go test ./...`, `dotnet test`) where relevant. Describe WHAT to verify, not the specific code to write. Include checks for:
- Full test suite passes after the change
- The specific behavioural guarantee the scenario requires (e.g. normalised response fields, correct tier lookup, notification received)
- The core service or dispatcher class no longer contains the branching or vendor-specific logic
- Existing behaviour is unchanged (regression check)

**NOT TO INCLUDE in the README:**
- Setup or install commands (pip install, npm install, mvn install, etc.)
- Pattern names or class names that reveal the solution
- Step-by-step implementation instructions
- Code snippets that give away the fix

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **Language is decided by the scenario** — never assume Python; follow the scenario's technology cues
3. **This is a pure local coding task** — NO docker-compose.yml, NO Dockerfile, NO database setup, NO external service configuration
4. **code_files MUST include** README.md, .gitignore, realistic source files in the scenario's language, test files in the language's idiomatic test framework, and the minimum project metadata for tests to run
5. **Task must be completable in {minutes_range} minutes** — scope to ONE focused GoF pattern, 1-3 source files + 1 test file
6. **README.md must contain exactly four sections** in order: Task Overview, Objectives, Helpful Tips, How to Verify
7. **README.md must not name the pattern, the class to add, or provide step-by-step instructions**
8. **The answer field is for evaluators only** — it should clearly name the expected pattern, explain why it fits, and describe what the tests prove
9. **definitions must include 3-5 relevant BASIC-level OO or design pattern terms** appropriate to the generated task
10. **short_overview must be exactly 3 plain sentences** with no label prefixes
11. **DO NOT include** TODO comments, placeholder text, pass-only stubs, ellipses, pseudo-code, or solution-revealing comments in any generated file
12. **DO NOT require** multi-pattern combinations, thread-safe Singleton, distributed concerns, advanced DI containers, or any INTERMEDIATE+ topic
13. **Use the selected real-world scenario as the domain basis** — keep the repo small, realistic, and behaviour-focused
14. **All file paths inside code and test commands must reference /root/task as the base directory** when mentioning paths
15. **The exact set of files in code_files is dictated by the scenario** — match the language's conventions; do NOT impose a Python-shaped layout on a Java or TypeScript scenario
"""

PROMPT_REGISTRY = {
    "Object Oriented Programming - Design Patterns (BASIC)": [
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_CONTEXT,
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_INPUT_AND_ASK,
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_INSTRUCTIONS,
    ]
}
