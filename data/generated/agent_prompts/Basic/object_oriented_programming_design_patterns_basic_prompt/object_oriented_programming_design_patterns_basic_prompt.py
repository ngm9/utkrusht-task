TASK_SHAPE = "non_infra"


PROMPT_OOP_DESIGN_PATTERNS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for BASIC proficiency — a candidate with roughly 1-2 years of software engineering experience
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role — OOP design patterns applied inside a real product module, not textbook exercises in isolation
- CRITICAL: This is a pure local coding and refactoring task. Do NOT create docker-compose.yml, Dockerfile, init_database.sql, database configuration, cache configuration, queue configuration, or any datastore setup
- CRITICAL: The language and runtime are derived from the scenario — do NOT assume Python unless the selected scenario clearly implies Python or is otherwise language-neutral and Python is the most natural fit

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What small feature or refactor will the candidate complete? Describe the business domain, the existing OO design problem, and what a correct solution looks like.
2. What language does this scenario imply, and what will the starter project structure look like? Include package layout, test framework, build manifest, and native test command.

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_OOP_DESIGN_PATTERNS_BASIC_INSTRUCTIONS = """
# Object Oriented Programming - Design Patterns Basic Task Requirements

## GOAL
As a technical architect super experienced in object-oriented programming and design patterns across multiple languages, you are given a list of real world scenarios and proficiency levels for OOP Design Patterns work at the BASIC level. Your job is to generate an entire task definition — code files, README.md, expected outcomes, etc. — that assesses a 1-2 yoe candidate's ability to recognise a design smell, apply an appropriate entry-level GoF pattern, keep the implementation simple, and preserve observable behaviour with tests.

**LANGUAGE / RUNTIME IS DERIVED FROM THE SCENARIO.** Do NOT assume Python. The chosen scenario determines the application stack, file extensions, module paths, runtime hints, build manifest, and test command. If the scenario is language-agnostic in wording, default to the most natural language for the domain described, such as Java or Kotlin for enterprise services, TypeScript for web or API modules, Python for scripting or data-adjacent modules, C# for .NET backends, or Swift/Kotlin for mobile-adjacent modules.

## CONTEXT & CANDIDATE EXPECTATION
The candidate receives a FULLY FUNCTIONAL local starter project with a small OO design smell already present. The starter project must run without syntax errors, runtime errors, missing files, or broken project configuration before the candidate begins. Existing tests must pass and must demonstrate the current behaviour; the candidate's job is to improve the internal design and add or update focused tests without changing the intended product behaviour.

**FILE LOCATION**: All code and scripts must reference /root/task as the base directory when mentioning file paths or commands.

A BASIC-level candidate should be able to reason about abstraction, encapsulation, inheritance, polymorphism, association, aggregation, composition, dependencies, SRP, OCP, DRY, KISS, YAGNI, cohesion, and coupling. They may apply ONE entry-level GoF pattern from the allowed scope, but they are not expected to architect multi-module systems, invent custom patterns, combine multiple advanced patterns, or solve nuanced concerns like multithreaded singletons.

If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks. Diagrams are optional and should only be included when they clarify the current small module structure without revealing the solution.

## INSTRUCTIONS

### Nature of the Task
- The task must ask the candidate to apply ONE entry-level GoF pattern to fix a small, well-scoped OO design problem inside an existing module — NOT to build a project from scratch or architect a multi-module system.
- **CRITICAL**: The starter project MUST include a small, runnable package in the language implied by the scenario, with the design smell already present, plus at least one test file using the language's idiomatic test framework that exercises the existing behaviour.
- **CRITICAL**: DO NOT REVEAL THE PATTERN NAME OR THE FIX in the starter code, README, or question. The candidate should infer the improvement from reading the tests, current code, and business requirement.
- The design problem must be visible in the code but not exaggerated. A God Object requiring a large redesign is OUT OF SCOPE; a class that branches on type codes, accumulates vendor-specific logic, duplicates notification dispatch, exposes a construction hotspot, or mixes optional behaviours in nested conditionals is appropriate.
- The task must focus on one of these BASIC-level pattern applications:
  - Adapter: wrap an incompatible third-party or legacy interface so the consuming service stays insulated from vendor-specific field names or method signatures.
  - Facade: hide a small multi-step subsystem behind a simple interface so callers are not tangled in internal dependencies.
  - Decorator: add optional behaviour such as validation, audit metadata, fees, or formatting around an object without subclass explosion.
  - Strategy: replace a growing conditional over behaviour type with interchangeable algorithms selected at runtime.
  - Observer: decouple a producer from multiple consumers by having listeners react to events rather than being called directly.
  - Template Method: lift a shared algorithm skeleton into a base class and let subclasses provide the variable steps.
  - Factory Method or Simple Factory: centralise object creation logic so callers request a product by type without knowing the concrete class.
- **CRITICAL**: Do NOT require Abstract Factory depth beyond surface-level explanation, thread-safe Singleton, distributed-system patterns, reflection-heavy frameworks, advanced dependency injection containers, event-bus infrastructure, or multi-pattern combinations. Those are outside BASIC scope.
- The candidate should write or update unit tests to pin the new or corrected behaviour. Keep test doubles simple: plain fakes, stubs, or lightweight in-memory collaborators are acceptable; advanced mocking frameworks must not be required.
- The current code must compile and run before the candidate changes it. The task should not make candidates fix build plumbing, dependency installation, formatting configuration, or unrelated broken tests.
- Time Constraint: The task must be completable within {minutes_range} minutes by a BASIC-level candidate.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, language documentation, design pattern references, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The task must assess practical OO reasoning, code comprehension, pattern intent, and implementation discipline — not rote memorisation of pattern names.
- Candidates may use external resources to understand the language, test framework, or relevant pattern vocabulary, but the submitted solution must be coherent, runnable, and appropriate to the provided starter code.
- Do not design the task so that success depends on obscure APIs, specialised frameworks, paid services, network access, or hidden environment setup.

## Code Generation Instructions
Based on real-world scenarios, create an OOP Design Patterns task that:
- Draws inspiration from the selected scenario for business context and the specific design smell.
- Matches BASIC proficiency level, approximately 1-2 years of professional experience.
- Can be completed within {minutes_range} minutes, with candidate edits typically landing in 1-3 source files and 1 test file.
- Tests practical OO judgment: recognising the smell, applying the right entry-level pattern intent, keeping names and responsibilities clear, and keeping tests green.
- Produces a FULLY FUNCTIONAL, pure local project using the language's native manifest and native test command.
- Selects a different real-world scenario each time for variety.
- Uses a short, descriptive, domain-inspired kebab-case task name under 50 characters, such as carrier-normalisation-refactor, notification-publish-cleanup, receipt-options-refactor, or course-export-routing. Do NOT use a generic oop- prefix.
- **CRITICAL**: This is a non-infrastructure task. Do NOT include docker-compose.yml, Dockerfile, init_database.sql, datastore configuration, cache configuration, queue configuration, service credentials, or environment-variable setup.
- The output should be a valid json schema:
  - README.md must be present and must follow the README.md instructions below.
  - .gitignore must be present and must match the chosen language ecosystem.
  - Source files must be present and must show the current smelly implementation without accidentally including the fix.
  - Test files must be present and must run using the language's idiomatic local test command.
  - A runtime-native project manifest must be present, such as pyproject.toml, package.json, tsconfig.json, pom.xml, build.gradle, go.mod, a .csproj file, Package.swift, or the equivalent manifest implied by the chosen language.

## Code file requirements
- The generated code_files must contain a realistic, runnable starter project rooted at /root/task.
- The starter code must be complete enough that the candidate can run the tests immediately using the native test command for the chosen ecosystem, such as pytest, npm test, mvn test, gradle test, go test ./..., dotnet test, swift test, or an equivalent standard command.
- Existing tests must pass on the unmodified starter project and must cover the current behaviour. They should not already assert the new behaviour that the candidate is expected to implement.
- The current implementation must contain the design smell naturally, not as a contrived anti-pattern lecture. Examples include duplicated branching logic, a tightly coupled dispatcher, vendor-specific mapping in a core service, optional behaviours implemented through nested conditionals, or repeated construction decisions spread across callers.
- The starter code must not include solution-revealing comments, TODO comments, placeholder methods, pass-only stubs, ellipses, pseudo-code, or comments such as fix this, use a pattern, create an interface, or refactor here.
- Keep the project small and focused. Avoid unrelated controllers, data models, background jobs, UI code, migrations, network services, or configuration files that inflate the task beyond the BASIC time budget.
- Use proper naming, visibility, packaging, and idioms for the chosen language. The generated files should feel like a small real project, not isolated textbook snippets.
- The candidate's expected change should be achievable without introducing third-party DI, AOP, plugin, event-bus, or code-generation frameworks.
- Do NOT include docker-compose.yml, Dockerfile, init_database.sql, database files, external service setup, environment variable files, or .env references.

## .gitignore INSTRUCTIONS
- Include a .gitignore appropriate to the chosen language and tooling.
- Exclude dependency folders, build outputs, caches, coverage artifacts, IDE metadata, compiled binaries, and OS-specific noise.
- Do not exclude source files, tests, README.md, or the native project manifest.
- Do not reference .env files as required setup, and do not create an .env file.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain EXACTLY these four sections in this order — no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
- Write 3-4 meaningful sentences.
- Do not use a bullet list in this section.
- Describe the business scenario, current state of the code, and why the problem matters.
- This section must NEVER be empty.
- Do not include bold time-budget callouts.
- Do not mention the pattern name, the class to add, a specific API, or any implementation step.

### Objectives
- Write 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the what and why, never the how.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: Improve query performance.
- GOOD: The product export flow silently produces an empty file for unsupported formats; after your changes, unsupported formats should fail clearly while existing supported exports remain unchanged.
- Do not name the exact pattern, interface, class, method, or factory that would reveal the solution.

### Helpful Tips
- Write 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word: Consider, Think about, Explore, Review, or Analyze.
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, interface, class, or algorithm that solves the task.
- Keep the tips focused on reading the current responsibilities, identifying coupling or duplicated behaviour, and preserving observable behaviour.

### How to Verify
- Write 4-6 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet must be a check the candidate can run or observe, such as test output, response shape, generated value, thrown error, class responsibility boundary, or regression behaviour.
- Mention the native test command for the selected language where relevant.
- Include checks that the full test suite passes, the new business behaviour is present, existing behaviour is unchanged, and the core class no longer carries the smell described in the task.

### CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README entirely:
- Setup commands such as npm install, pip install, docker compose up, mvn install, gradle build setup commands, or equivalent dependency-install commands.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, class names, interface names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like you should implement, add this middleware, create this class, use a specific API, extract this interface, or apply a named pattern.
- Database connection details, host names, ports, usernames, passwords, client-tool suggestions, or placeholders such as DROPLET_IP.

## REQUIRED OUTPUT JSON STRUCTURE
Return valid JSON only with exactly the following top-level keys. Each value must be fully populated and useful to the candidate or evaluator.

{{
  "name": "A domain-specific kebab-case GitHub repository name under 50 characters that does not start with a generic oop prefix.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, and different from the repository name.",
  "question": "A complete candidate-facing task description that explains the current implementation, the observable design problem, the required end state in terms of responsibilities and behaviour, the expected test workflow, and the time constraint without naming the exact pattern or giving away the fix.",
  "code_files": {{
    "README.md": "A concise candidate-facing README that contains exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, following all README instructions without revealing the solution.",
    ".gitignore": "A language-appropriate .gitignore that excludes generated, dependency, cache, build, coverage, IDE, and operating-system artifacts while preserving source, tests, README, and manifests.",
    "<runtime-native-project-manifest>": "The minimum manifest or build file required for the selected language's native test command to run on a clean local checkout.",
    "<source-file-paths>": "The complete starter source files in the language implied by the scenario, containing the current smelly but working implementation without TODO comments, pseudo-code, or the intended refactor.",
    "<test-file-paths>": "The existing unit tests using the language's idiomatic test framework, passing against the starter behaviour and leaving room for the candidate to add or update tests for the requested change."
  }},
  "answer": "An evaluator-facing high-level solution approach that names the expected BASIC-level GoF pattern, explains why it fits, describes which responsibilities should move or be separated, identifies the tests that prove the fix, and states what design qualities a successful solution demonstrates without providing exact code.",
  "definitions": {{
    "<relevant BASIC-level OO or pattern term>": "A concise one-sentence definition of the term as it applies to the generated task.",
    "<second relevant BASIC-level OO or pattern term>": "A concise one-sentence definition of the term as it applies to the generated task.",
    "<third relevant BASIC-level OO or pattern term>": "A concise one-sentence definition of the term as it applies to the generated task."
  }},
  "hints": "A single-line hint that nudges the candidate toward the right OO insight without naming the pattern, the class to add, the method to write, or any language-specific symbol.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on passing tests, preserved behaviour, removal of the specific design smell, and a clearer extension path for the scenario's new requirement.",
  "pre_requisites": "A bullet list of the selected language runtime and test framework, Git, basic OOP fundamentals, unit testing basics, and awareness of entry-level GoF pattern intent needed to complete the task.",
  "short_overview": "Exactly 3 plain sentences: first state the business domain and the design problem in the starter code, second state what the candidate must do, and third state what success looks like with no label prefixes."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences.
2. **Language is decided by the scenario** — never assume Python unless the scenario naturally implies it; follow the scenario's technology cues for file extensions, package layout, manifest, and test framework.
3. **This is a pure local coding task** — NO docker-compose.yml, NO Dockerfile, NO init_database.sql, NO database setup, NO cache setup, NO queue setup, and NO external service configuration.
4. **code_files MUST include** README.md, .gitignore, realistic source files in the scenario's language, test files in the language's idiomatic test framework, and the minimum native project manifest for tests to run.
5. **Task must be completable in {minutes_range} minutes** — scope to ONE focused GoF pattern, 1-3 source files, and 1 test file for candidate changes.
6. **README.md must contain exactly four sections** in order: Task Overview, Objectives, Helpful Tips, How to Verify.
7. **README.md must not name the pattern, the class to add, the interface to extract, or provide step-by-step implementation instructions.**
8. **The answer field is for evaluators only** — it should clearly name the expected pattern, explain why it fits, and describe what the tests prove.
9. **definitions must include 3-5 relevant BASIC-level OO or design pattern terms** appropriate to the generated task.
10. **short_overview must be exactly 3 plain sentences** with no label prefixes such as Business problem, Technical focus, Expected outcome, or any other Label: prefix.
11. **DO NOT include** TODO comments, placeholder text, pass-only stubs, ellipses, pseudo-code, solution-revealing comments, or broken files in any generated file.
12. **DO NOT require** multi-pattern combinations, thread-safe Singleton, distributed concerns, advanced DI containers, custom pattern variants, or any INTERMEDIATE+ topic.
13. **Use the selected real-world scenario as the domain basis** — keep the repo small, realistic, behaviour-focused, and aligned with BASIC OOP Design Patterns scope.
14. **All file paths inside code and test commands must reference /root/task as the base directory** when mentioning paths.
15. **The exact set of files in code_files is dictated by the scenario** — match the language's conventions and do NOT impose a Python-shaped layout on a Java, TypeScript, C#, Go, Kotlin, Swift, or C++ scenario.
"""


PROMPT_REGISTRY = {
    "Object Oriented Programming - Design Patterns (BASIC)": [
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_CONTEXT,
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_INPUT_AND_ASK,
        PROMPT_OOP_DESIGN_PATTERNS_BASIC_INSTRUCTIONS,
    ]
}