PROMPT_TYPESCRIPT_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_TYPESCRIPT_BEGINNER_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a TypeScript assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (BEGINNER: 0-1 year TypeScript experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TYPESCRIPT_BEGINNER = """
# TypeScript Beginner Task Requirements

## GOAL
As a technical architect super experienced in TypeScript, you are given real-world scenarios and proficiency levels for TypeScript development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a simple feature from scratch or fix a small bug in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question that is syntactic errors.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy or incomplete state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The function accepts string parameters instead of proper typed parameters"; "A utility returns any instead of a typed result"; "Type narrowing is missing causing runtime errors."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must compile without errors (or with only the intentional type issues), but it must exhibit exactly these bugs or missing pieces.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Add proper type annotations"; "Refactor to use typed parameters"; "Add type guards for input validation."
- The candidate's job is only to complete these required changes on top of the current implementation.

**Final Implementation Approach:**
- A high-level description of the correct approach (e.g. "Define an interface for the input. Use number types instead of string. Add a type guard function. Return a properly typed result object.").
- The complexity of the task and specific ask expected from the candidate must align with BEGINNER proficiency level (0-1 year TypeScript experience), ensuring that no two questions generated are similar.
- For BEGINNER level of proficiency, the questions must be very specific, narrow in scope, and focus on introductory TypeScript concepts like:
  - Basic types (number, string, boolean, array)
  - Type annotations on variables and function parameters/return types
  - Interfaces and simple type definitions
  - Type narrowing and basic type guards (typeof)
  - Union types and literal types
  - Simple generics (Array<T>, Promise<T>)
  - Enums (string and numeric)
  - Optional properties and parameters
  - Basic module imports/exports
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to TypeScript 4.5+ best practices and modern ECMAScript standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BEGINNER proficiency (0-1 year TypeScript experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "fee-calculator-type-fix", "product-tag-dedup".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working TypeScript project** that compiles and runs successfully after setup (e.g. `npm install && npx ts-node src/index.ts` or `npm start`).
- **ZERO compilation errors** — the project must compile cleanly out of the box (minor type warnings related to the task are acceptable, but no hard errors).
- **All existing functionality in the starter code must work** — Any functions, I/O, or logic that are already implemented must execute as intended for the "Current Implementation" state.
- **The candidate should NOT need to fix anything to make the project run** — The environment is already fully functional; the candidate's job is only to implement the requested feature or fix the specified bug.

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid TypeScript that compiles and runs.
- Keep the code files minimal and to the point.
- TypeScript starter code should include a simple project layout (e.g. src/ directory, tsconfig.json, package.json) but NOT require complex infrastructure setup.
- Include tsconfig.json with appropriate compiler options for beginners (strict mode enabled).
- Include package.json with TypeScript and ts-node as dev dependencies.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the buggy or incomplete state described in the task. It must compile and exhibit that state; it must NOT include any of the "Required Changes" or the final implementation approach.
- If the task is to fix bugs, the starter code has a simple logical or type-related bug (no hard compilation errors) that is appropriate for beginner level.
- If the task is to implement a feature from scratch, the starter code only provides a good starting point that matches the described current state.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect beginner TypeScript proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a TypeScript task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BEGINNER proficiency level (0-1 year TypeScript experience)
- Can be completed within {minutes_range} minutes
- Tests practical TypeScript skills at an introductory level, focusing on one or two core type system concepts per task
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-file or small-module features with minimal moving parts

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Refactor Fee Calculator to Use Typed Number Parameters', 'Fix Product Tag Deduplication with Proper Type Annotations', 'Implement Typed BMI Computation for Health API'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state the starter code implements (what we give). (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous so starter code can perfectly match Current Implementation and candidate knows exactly what to do.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Node/TypeScript exclusions (node_modules, dist, .env, etc.)",
    "package.json": "Project config with TypeScript and ts-node dependencies",
    "tsconfig.json": "TypeScript compiler configuration with strict mode",
    "src/index.ts": "Main entry point",
    "src/additional_module.ts": "Other modules as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, environment setup, and knowledge required. Include Node.js 16+, npm, Git, basic TypeScript knowledge (types, interfaces, type annotations).",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "Type Annotation": "Explicit type label on a variable, parameter, or return value (e.g., x: number)",
    "Interface": "A TypeScript construct that defines the shape of an object",
    "Type Guard": "A runtime check that narrows a variable's type within a conditional block",
    "Union Type": "A type that can be one of several types (e.g., string | number)",
    "Generic": "A type parameter that lets functions and types work with multiple types"
  }}
}}


## README.md STRUCTURE (TypeScript Beginner)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:

- Use bullet points starting with "Consider", "Think about", "Explore", "Review"
- Guide the candidate toward discovery — suggest areas to explore, not specific solutions
- Do NOT specify exact implementation approaches, specific APIs, type definitions, or function signatures
- **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for the task:

- Describe WHAT needs to work, not HOW to implement it
- Frame objectives around observable outcomes and expected behavior
- Do NOT specify exact implementation approaches, specific type definitions, or function signatures
- **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches after implementation:

- Describe what behaviors to verify and how to confirm success
- Focus on observable outcomes (correct types, compilation, runtime results)
- Do NOT specify specific code, type annotations, or implementation details to check
- **CRITICAL**: Focus on measurable, verifiable outcomes. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (npm install, npx ts-node, etc.) unless essential for the task type
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific TypeScript syntax examples or code snippets that would give away the solution
- Interface definitions or type patterns that would reveal the solution
- Any specific file or module implementation details that would give away the solution
- Excessive bullets or verbose explanations — keep each section lean and focused


## CRITICAL REMINDERS

1. **Environment must be fully working** — The project must compile and run perfectly; zero errors; the candidate does NOT fix the environment, only the task (feature/bug).
2. **Starter code must be compilable** but must NOT contain the core logic solution
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on introductory TypeScript concepts** appropriate for BEGINNER level
7. **Use TypeScript 4.5+** with strict mode enabled in tsconfig.json
8. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
9. **README.md MUST be fully populated** with meaningful, task-specific content
10. **.gitignore** must cover standard Node.js/TypeScript exclusions
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""

PROMPT_REGISTRY = {
    "Typescript": [
        PROMPT_TYPESCRIPT_BEGINNER_CONTEXT,
        PROMPT_TYPESCRIPT_BEGINNER_INPUT_AND_ASK,
        PROMPT_TYPESCRIPT_BEGINNER,
    ],
    "Typescript (BEGINNER)": [
        PROMPT_TYPESCRIPT_BEGINNER_CONTEXT,
        PROMPT_TYPESCRIPT_BEGINNER_INPUT_AND_ASK,
        PROMPT_TYPESCRIPT_BEGINNER,
    ],
}
