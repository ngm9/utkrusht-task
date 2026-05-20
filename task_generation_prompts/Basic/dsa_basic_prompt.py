PROMPT_DSA_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DSA_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Data Structures and Algorithms assessment task.

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
- The task must reflect authentic challenges that would be encountered in the role described in the role context — DSA work framed inside a real product surface (a cache, a lookup, a validator, a pricing tier), not abstract leetcode-style puzzles disconnected from a system.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the data structure / algorithm involved, and the specific problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC DSA proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DSA_BASIC = """
# Data Structures and Algorithms Basic Task Requirements

## GOAL
As a technical architect super experienced in core Data Structures and Algorithms across multiple languages, you are given real-world scenarios and proficiency levels for DSA work at the BASIC level. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess a 1-2 yoe candidate's ability to recognize the right data structure / algorithm for a small product problem and implement it correctly inside an existing module — NOT to solve abstract puzzles in isolation.

**LANGUAGE / RUNTIME IS DERIVED FROM THE SCENARIO.** Do NOT assume Python. The chosen scenario specifies the application stack (file extensions, module paths, runtime hints) — the generated starter code, file structure, build/run commands, and test framework MUST follow whatever language the scenario implies (e.g. Python with `pytest`, TypeScript/Node with `jest` or `vitest`, Java with JUnit + Maven/Gradle, Go with the built-in test runner, C# with xUnit). If the scenario is language-agnostic in wording, default to the most natural language for the domain described.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to fix a wrong or slow data-structure choice, refactor a brute-force algorithm into a more appropriate one, or implement a small algorithmic helper inside an existing module **in the language the scenario implies**. Do NOT ask the candidate to build a project from scratch.
- The starter project MUST include a small, runnable package (in whatever language the scenario specifies) with the buggy or slow implementation already wired in, plus at least one test file (in the language's idiomatic test framework — `pytest`, `jest`/`vitest`, JUnit, Go test, xUnit) that exercises the module. The candidate should NOT have to set up the project structure themselves.
- The question scenario must be clear, with realistic facts, figures, company names, and numbers (e.g. row counts, latency budgets, list sizes) that are consistent with the chosen domain.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The wrong/slow behavior described in the scenario MUST actually be present in the starter implementation.
- The task must surface real DSA judgment — picking the right structure (hash map vs. list scan, stack vs. counter, binary search vs. linear scan, heap vs. full sort, doubly-linked-list + hashmap for LRU), maintaining the right complexity, and writing tests that pin both correctness and the new performance contract.

### BASIC PROFICIENCY SCOPE (1-2 yoe — what the task may assess)
Tasks MUST align with BASIC DSA. The task may assess one or more of the following; do NOT go beyond this scope into advanced topics. Examples below name common helpers across languages — the candidate uses whatever ships with the chosen language's standard library or built-in primitives:

- **Arrays, hashing, sets**: O(n) one-pass scans, frequency counting with a hash map (e.g. Python `dict`/`Counter`, JS `Map`, Java `HashMap`, Go `map`), deduplication, two-sum / pair-finding patterns, grouping by key.
- **Stacks and queues**: balanced-brackets / nesting validation, simple undo-redo, BFS-style level traversal on small structures.
- **Hash map + linked list (LRU)**: O(1) get/put with proper recency tracking. Either via the language's ordered-map primitive (e.g. Python `OrderedDict`, Java `LinkedHashMap`) or a hand-rolled doubly-linked-list + hash map — the candidate must understand WHY both pieces are needed.
- **Sorting and binary search**: O(log n) lookups on sorted data using whatever binary-search helper the language provides (e.g. Python `bisect`, Java `Collections.binarySearch`, Go `sort.Search`); sort-then-scan patterns; stable sort by key.
- **Strings**: prefix/suffix checks, simple parsing, single-pass transformations.
- **Big-O reasoning**: justifying why the new implementation is O(n) / O(log n) / O(1) and writing a small performance test to pin it.
- **Standard library fluency in the chosen language**: ordered collections, hash maps, sorted-search helpers, FIFO queues, basic priority-queue primitives where appropriate.

Do NOT require: graph algorithms beyond a trivial BFS/DFS, dynamic programming, advanced trees (balanced trees, segment trees, tries beyond a toy example), backtracking, or NP-hard approximations. Those are INTERMEDIATE+ topics.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts:

**Current Implementation (what we give to the candidate):**
- Describe precisely the wrong-structure / brute-force / buggy state that the starter code implements. Include the data sizes, latency, and observed bug as concretely as the scenario does.
- Examples: "Cache uses a plain dict with a `pop(next(iter(...)))` eviction that does not respect recency"; "Duplicate finder runs O(n^2) and times out on the 200K-row file"; "Bracket validator counts open/close per type and accepts `([)]`"; "Tier lookup is a linear scan over 5K thresholds — p99 latency has crept to 180ms".
- The **starter code MUST perfectly implement this current behavior** — it must run, it must produce the observed wrong output / latency, and it must NOT accidentally include the fix.

**Required Changes (what the candidate must do):**
- List the specific structural / algorithmic changes the candidate must apply, expressed in terms of the data structure and its target complexity (not in stdlib symbols of any particular language). Examples: "Replace the dict eviction with a proper LRU policy so get/put move keys to the MRU end"; "Replace the nested loop with a single hash-grouped pass that compares within a 60-second window"; "Replace the counters with a stack-based balanced-brackets check"; "Replace the linear scan with a binary search and validate input is sorted".
- The candidate's job is only to apply these required changes on top of the current implementation, plus extend tests to pin the new contract.

**Final Implementation Approach:**
- A high-level description of the correct approach, including the chosen data structure and the target complexity. Use abstract terms (ordered map / FIFO queue / stack / sorted-search helper) rather than language-specific symbols. The candidate's solution does not have to match this verbatim, but must hit the same complexity class.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including Google, Stack Overflow, official language docs, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to recognize the right data structure for a real product problem and integrate it cleanly into an existing module — not to test rote memorization of algorithm boilerplate. Therefore, the complexity should reflect basic DSA proficiency while requiring genuine judgment that goes beyond pasting a generic LeetCode template.
- Use modern conventions for whichever language the scenario implies (Python 3.10+ / PEP 8, modern TypeScript/ESM, Java 17+, Go 1.21+, etc.). Use standard library and built-in primitives only — do NOT introduce specialized third-party DSA libraries (`numpy`, `networkx`, `sortedcontainers`, `lodash` collections, Guava, etc.) unless the scenario explicitly justifies it.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years).

### Starter Code Requirements

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- The starter code MUST be a complete, working project in the language implied by the scenario, runnable with the standard install + test commands for that ecosystem (e.g. Python: `pip install -r requirements.txt && pytest`; Node/TS: `npm install && npm test`; Java/Maven: `mvn test`; Go: `go test ./...`).
- ZERO syntax errors, ZERO runtime errors. The existing tests must run; the tests that pin the wrong/slow behaviour may pass against the starter (since they describe the current state), and any new tests the candidate adds will fail until the fix is applied.
- The candidate should NOT need to fix project setup to make tests run. Their job is the algorithmic fix and the new tests, not project plumbing.

**WHAT MUST BE INCLUDED:**
- A clear source folder layout matching the language's conventions, containing the buggy/slow module at the path the scenario implies (e.g. the scenario may explicitly reference `src/cache/session_cache.py`, `src/cache/SessionCache.ts`, `internal/recon/duplicate_finder.go`, etc.).
- A test directory using the language's idiomatic test framework, containing the minimal test file the scenario references.
- The minimum project metadata files required for tests to run on a clean checkout (e.g. Python: `pyproject.toml` and/or `pytest.ini` and `requirements.txt`; Node/TS: `package.json` and `tsconfig.json`; Java/Maven: `pom.xml`; Go: `go.mod`). NO third-party DSA libraries.

**LET THE SCENARIO DECIDE THE FILE LAYOUT.** The exact filenames, language extensions, and folder structure MUST be derived from the scenario's wording (file paths it references, technology cues like "Mongoose model", "Spring service", "Express handler") rather than imposed from a fixed template. If the scenario references `src/cache/session_cache.py`, generate Python; if it references `src/cache/SessionCache.ts`, generate TypeScript; and so on.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code. The replacement structure (ordered map / hashmap+DLL / stack / sorted-search helper / hash-grouped pass) MUST NOT already appear.
- DO NOT include `// TODO`, `// fix me`, `# hint:`, or any comments that point at the fix (use whichever comment syntax the language uses, but the rule applies regardless).
- DO NOT include the new tests the candidate is asked to add — only the pre-existing minimal tests.
- DO NOT scaffold unrelated modules or features that inflate scope beyond the BASIC time budget.

### Code Generation Instructions
Based on real-world scenarios, create a DSA task that:
- Draws inspiration from input scenarios for business context and the specific data-structure / algorithm problem
- Matches BASIC proficiency level (1-2 years in the language the scenario implies + core DSA)
- Can be completed within {minutes_range} minutes — the candidate's edits should land in 1 module + 1 test file, occasionally one helper module
- Tests practical DSA judgment: picking the right structure, hitting the right complexity, writing tests that pin BOTH correctness and the performance contract
- Select a different real-world scenario each time to ensure variety in task generation
- Task name: short, descriptive, under 50 characters, kebab-case, ideally incorporating the company/product name from the scenario rather than starting with `dsa-` (e.g., `sessioncache-lru-eviction-fix`, `paywise-tier-binary-lookup`)

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — the wrong/slow data-structure or algorithmic state the starter code implements. (2) Required Changes — the specific structural / algorithmic fix the candidate must implement, including any new tests they must add to pin correctness AND the performance contract. Keep concise but unambiguous so starter code can match Current Implementation exactly and the candidate knows what done looks like.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below — required for every language",
    ".gitignore": "Standard exclusions for whichever language the scenario implies",
    "<actual-source-path-from-scenario>": "The buggy/slow implementation matching the Current Implementation, at the file path the scenario references, in the language it implies",
    "<actual-test-path-from-scenario>": "The existing minimal test file using the language's idiomatic test framework (pytest / jest / vitest / JUnit / go test / xUnit)",
    "<project-metadata-files>": "The minimum metadata required for the test command to run on a clean checkout — chosen from the language's ecosystem (e.g. pyproject.toml + requirements.txt; package.json + tsconfig.json; pom.xml; go.mod; etc.)"
  }},
  "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., the cache evicts truly old entries, the duplicate finder runs in O(n) on a 50K-row test under 2s, the bracket validator correctly fails `([)]`, the tier lookup uses binary search and validates sorted input).",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words). Bullet 1: the business context and the existing data-structure / algorithmic problem. Bullet 2: the specific structural / algorithmic change the candidate must apply. Bullet 3: the expected outcome including the complexity / latency target. Do NOT prefix bullets with bold mini-titles like '**Business context:**' — start each bullet directly with the content.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required for the language the scenario implies (e.g. Python 3.10+ + pip + pytest; or Node 18+ + npm + jest/vitest; or JDK 17+ + Maven/Gradle + JUnit; or Go 1.21+ with the built-in test runner). Always include Git and basic DSA knowledge (hash maps, stacks, queues, sorting, binary search, big-O reasoning).",
  "answer": "High-level solution approach — the chosen data structure and target complexity, expressed in language-neutral terms (ordered map / FIFO queue / stack / sorted-search helper) rather than language-specific stdlib symbols. Do not give the exact code.",
  "hints": "Single line guiding the candidate toward the right structural insight (e.g. 'Think about which built-in primitive can keep both insertion order and O(1) lookup at once' or 'Look for a way to reduce the linear scan to logarithmic on already-sorted data'). Must NOT name the exact data structure or any language-specific stdlib symbol.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (DSA Basic)
- The README.md contains the following sections:
  - Task Overview
  - Objectives
  - How to Verify
  - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content — no empty or placeholder text allowed
- Content must be directly relevant to the specific DSA task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview (MANDATORY - 2-3 substantial sentences)
**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario, the data sizes / latency budget, and the observable bug or performance pain. NEVER generate empty content - always provide substantial business context.

### Objectives
Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name the chosen data structure, name a language-specific stdlib helper, or otherwise tell the candidate what code to write. The candidate should read the objectives and know WHAT "done" looks like, but still have to figure out HOW.

**Allowed phrasing — describes outcome, hides solution:**
- "Inserting `MAX_SIZE + 1` entries into the cache evicts the least-recently-used entry, not the first one inserted."
- "The duplicate finder produces identical pairs to the existing fixture and completes in under 2 seconds on a 50K-row generated test."
- "The validator rejects `([)]` and never raises on inputs containing stray closers."
- "Looking up a spend value on a 5K-entry threshold list completes in roughly the time of a logarithmic scan, not a linear one."

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Replace the hash map with an ordered map and move keys to the most-recently-used end on access." *(prescribes the fix shape)*
- ❌ "Use a binary-search helper to find the tier index." *(names the algorithm)*
- ❌ "Replace the nested loop with a hash map keyed by `(merchant_id, amount)`." *(names the structure and the key)*
- ❌ "Use a stack of opening brackets and pop on every closer." *(prescribes the algorithm)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behavior* the module must demonstrate, not the *code* it must contain.

Keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the function never raises on user input"). The remaining objectives must be specific to the scenario's primary data-structure or complexity target.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.

### How to Verify
Verification approaches after implementation:
- Specific checkpoints after the fix: run the language's test command (e.g. `pytest`, `npm test`, `mvn test`, `go test ./...`), the existing tests still pass, the new tests the candidate added (correctness + performance) all pass.
- Observable behaviors: targeted edge cases (boundary recency in LRU, three-way matches in duplicate finder, interleaved brackets, exact-boundary spend), and the complexity contract (the new performance test passes within the budget).
- Code-quality checks: standard library / built-in primitives only (no surprise third-party deps), no eviction or bracket logic baked into a single giant branch, public function signatures are stable.
- These points help the candidate verify their own work and the assessor to award points.

**CRITICAL**: Focus on measurable, verifiable outcomes.

### Helpful Tips
Practical guidance without revealing implementations:
- Project context and guidance points suitable for basic-level developers (in the language the scenario implies) reasoning about data-structure choice
- Engineering considerations framed as questions ("Which built-in primitive lets you keep both insertion order and O(1) lookup?", "What does Big-O become if the inner loop is replaced with a single hash lookup?", "Where does input validation belong if a wrong assumption silently corrupts results?")
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"
- 3-4 concise bullets MAX

**CRITICAL**: Guide discovery, never provide direct solutions.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (any install or test command for any ecosystem — `pip install`, `pytest`, `npm install`, `npm test`, `mvn test`, `go test`, etc.)
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Direct solutions or hints
- Names of specific stdlib classes in any language that point at the fix (do not say "use `OrderedDict`" — say "find a built-in primitive that can move a key to the most-recent end on access"; do not say "use `bisect`" — say "find a way to make lookup logarithmic instead of linear on sorted data")
- Snippets that would reveal the data structure or algorithm choice

## CRITICAL REMINDERS

1. **Starter project must be runnable** with the standard install + test commands of whichever language the scenario implies, with the existing tests passing AND the algorithmic problem reproducible (slow / wrong output) until the candidate applies the fix
2. **The starter MUST exhibit the described bug or performance issue.** Do NOT accidentally include the fix or a "good enough" partial solution. If the scenario says "linear scan over 5K entries", the starter must literally do a linear scan over the supplied threshold list.
3. **NO comments** that reveal the solution or give hints
4. **Task must be completable within {minutes_range} minutes** with a hard cap at 30 minutes
5. **Focus on BASIC DSA only** — hash maps, stacks/queues, simple LRU (ordered map or hashmap+DLL), sorting, binary search, simple heap usage. NO graph algorithms, NO DP, NO advanced trees.
6. **Language is decided by the scenario, not the prompt.** Use modern conventions for that language (Python 3.10+ / PEP 8, modern TypeScript/ESM, Java 17+, Go 1.21+, etc.) and built-in primitives / standard library only unless the scenario truly justifies a third-party dep
7. **Code files MUST NOT contain** the implementation for the core data-structure / algorithmic fix the candidate must apply
8. **README.md MUST be fully populated** with meaningful, task-specific content, and Objectives must describe end-states without naming stdlib symbols (see "Objectives" section above for FORBIDDEN phrasings)
9. **.gitignore** must cover standard exclusions for whichever language the scenario implies (Python: `__pycache__/`, `.pytest_cache/`, `.venv/`; Node: `node_modules/`, `dist/`; Java: `target/`, `.gradle/`; Go: `bin/`, `vendor/`; etc.)
10. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than a generic `dsa-` prefix
11. **Select a different real-world scenario** each time for variety
12. **The exact set of files in `code_files` is dictated by the scenario** — match the source/test paths the scenario references and add only the minimum project-metadata files needed for the test command to run on a fresh clone. Do NOT impose a Python-shaped layout on a non-Python scenario.
"""

PROMPT_REGISTRY = {
    "Data Structures and Algorithms (BASIC)": [
        PROMPT_DSA_BASIC_CONTEXT,
        PROMPT_DSA_BASIC_INPUT_AND_ASK,
        PROMPT_DSA_BASIC,
    ]
}
