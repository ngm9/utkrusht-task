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
- The scenarios above are inspiration for the TYPE of problem (which data structure / algorithmic shape to target) and a 1-2 sentence flavor wrapper. They are NOT a brief to embed the problem inside a real application, framework, route, or service module.
- **IGNORE any LEGACY language-specific file paths, extensions, framework names, or test-file names mentioned in the scenarios** (e.g. references like `src/cache/session_cache.py`, `coupon.*`, `fares_test.*`, `tests/test_x.py`, "pytest", "jest"). These are legacy framing artefacts from older scenarios — disregard them.
- **READ THE LIST OF SUPPORTED LANGUAGES FROM THE SELECTED SCENARIO.** Each scenario declares which languages it supports — typically as a line like `**Supported Languages:** Python, JavaScript, Java` (or similar). The set of languages you must support is EXACTLY what the scenario declares — no more, no less. Do not add languages the scenario does not list. Do not drop languages it does list. For EACH language the scenario lists, you MUST emit a dedicated folder + a solution stub + a test file + the minimum project metadata for that language's test command to run. See the LANGUAGE SUPPORT section in the next prompt for conventional layouts per language.
- If the scenario does NOT declare any supported languages, default to: **Python, JavaScript, Java** (three languages).
- The task you generate MUST be a CLASSIC DSA PROBLEM: one function to implement, typed inputs, typed output, explicit constraints, 2-3 worked examples — NOT an app build, NOT a refactor inside an existing service module.
- The task is LANGUAGE-AGNOSTIC: the candidate will pick ONE of the supported languages declared in the scenario and implement the function only in that language. The starter project ships a stub + tests in each declared language.
- The task complexity must be appropriate for BASIC level (1-2 years of experience).
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different inspiration scenario each time to ensure variety.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (The data structure / algorithmic shape involved, the function the candidate will implement, and the light real-world flavor used as context)
2. What will the task look like? (The single function deliverable, the list of language stubs that will ship — exactly as declared by the selected scenario — and how it aligns with BASIC DSA proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DSA_BASIC = """
# Data Structures and Algorithms Basic Task Requirements

## GOAL
As a technical architect super experienced in core Data Structures and Algorithms, you are given inspiration scenarios and proficiency levels for DSA work at the BASIC level. Your job is to generate a CLASSIC DSA PROBLEM that can be solved in whichever languages the selected inspiration scenario declares as supported. This is NOT an app build and NOT a refactor inside an existing service module — the candidate implements ONE function (occasionally a small class) that takes typed inputs and returns a typed output. The starter project ships a solution stub + a small test file in EACH language declared by the scenario, so the candidate picks one language and codes against that language's skeleton.

## LANGUAGE SUPPORT (read from the selected inspiration scenario)

**RULE 1 — The scenario decides the set.** Each scenario carries a declaration of supported languages (e.g. `**Supported Languages:** Python, JavaScript, Java`). The set of language folders you ship MUST exactly match that declaration — no extras, no omissions. If the scenario does not declare any languages, default to **Python, JavaScript, Java**.

**RULE 2 — For EACH declared language, ship a self-contained folder.** Each folder must contain:
- A solution stub file with the function signature and a placeholder return value (so the file compiles/parses but the tests fail until the candidate implements it).
- A test file with 3-5 small assertions pinning the documented worked examples and edge cases.
- The minimum project metadata files needed for that language's test command to run on a clean checkout.

**RULE 3 — Use the conventional layout and test framework for each language.** Below are the conventions for languages most likely to appear in scenarios. If a scenario declares a language not in this list, fall back to the most idiomatic open-source convention for that language.

- **Python (3.10+)** — folder `python/`. `python/solution.py` (stub), `python/test_solution.py` (pytest), optional `python/pytest.ini` (minimal config or rely on default discovery).
- **JavaScript (Node 18+)** — folder `javascript/`. `javascript/solution.js` (stub, CommonJS `module.exports`), `javascript/solution.test.js` (jest), `javascript/package.json` declaring `jest` as a devDependency and a `"test": "jest"` script.
- **TypeScript (Node 18+, TS 5+)** — folder `typescript/`. `typescript/solution.ts` (stub, `export function`), `typescript/solution.test.ts` (jest with `ts-jest`), `typescript/package.json`, `typescript/tsconfig.json`.
- **Java (17+)** — folder `java/`. `java/src/main/java/Solution.java` (stub class), `java/src/test/java/SolutionTest.java` (JUnit 5), `java/pom.xml` (Maven) declaring `junit-jupiter` and `maven-surefire-plugin`.
- **C++ (C++17)** — folder `cpp/`. `cpp/solution.h` (declaration), `cpp/solution.cpp` (stub implementation), `cpp/test_solution.cpp` (plain `main()` runner using only `<cassert>` from the standard library — prints `"All tests passed\\n"` if every assert succeeds), `cpp/Makefile` with a `test` target that compiles via `g++ -std=c++17` and runs the binary.
- **Go (1.21+)** — folder `go/`. `go/solution.go` in `package solution` (stub), `go/solution_test.go` in `package solution` (built-in `testing`), `go/go.mod` declaring the module.
- **Ruby (3.2+)** — folder `ruby/`. `ruby/solution.rb` (stub), `ruby/solution_test.rb` using `minitest/autorun` from the standard library; runs via `ruby ruby/solution_test.rb`.
- **Rust (stable)** — folder `rust/`. `rust/src/lib.rs` (stub function + `#[cfg(test)] mod tests` block), `rust/Cargo.toml` declaring the crate; runs via `cargo test`.
- **C# (.NET 8+)** — folder `csharp/`. `csharp/Solution.cs` (stub), `csharp/SolutionTest.cs` (xUnit), `csharp/Solution.csproj` declaring xUnit + `Microsoft.NET.Test.Sdk`.
- **Kotlin (1.9+)** — folder `kotlin/`. `kotlin/src/main/kotlin/Solution.kt`, `kotlin/src/test/kotlin/SolutionTest.kt`, `kotlin/build.gradle.kts` declaring JUnit 5.
- **PHP (8.2+)** — folder `php/`. `php/Solution.php` (stub class), `php/SolutionTest.php` (PHPUnit), `php/composer.json` declaring `phpunit/phpunit`.

The PROBLEM STATEMENT (function name, inputs, outputs, constraints, examples) is identical across all declared languages — only the syntax differs.

## INSTRUCTIONS

### Nature of the Task
- Task must be a classic, self-contained DSA problem: ONE function (occasionally one small class with 2-3 methods, e.g. an LRU cache) to implement, with clearly typed inputs and outputs, explicit constraints on input sizes, and 2-3 worked examples.
- The inspiration scenario may PROVIDE light real-world flavor in 1-2 sentences (e.g. "A pricing service needs to look up a customer's spend tier from a sorted threshold list"), but the deliverable is a PURE FUNCTION — not a service, route, controller, web framework handler, or module embedded in a wider application. No HTTP, no databases, no ORM models, no business-layer abstractions.
- The candidate implements the function in their chosen language's `solution.*` file and runs that language's test command to verify.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The solution stub in each declared language must return a trivial placeholder (e.g. `return []`, `return None`, `return 0`, `return null`, `return false`) so the file compiles/runs but the tests fail until the candidate implements it correctly.

### BASIC PROFICIENCY SCOPE (1-2 yoe — what the task may assess)
Tasks MUST align with BASIC DSA. The task may assess one or more of the following; do NOT go beyond this scope into advanced topics:

- **Arrays, hashing, sets**: O(n) one-pass scans, frequency counting with a hash map, deduplication, two-sum / pair-finding patterns, grouping by key.
- **Stacks and queues**: balanced-brackets / nesting validation, simple undo-redo, BFS-style level traversal on small structures.
- **Hash map + linked list (LRU)**: O(1) get/put with proper recency tracking. The candidate must understand WHY both pieces are needed.
- **Sorting and binary search**: O(log n) lookups on sorted data and on locally monotonic data (peak-finding), sort-then-scan patterns, stable sort by key.
- **Strings**: prefix/suffix checks, simple parsing, single-pass transformations, palindrome / anagram checks.
- **Trivial graph algorithms on adjacency lists**: BFS / DFS on unweighted directed or undirected graphs, connected components in an undirected graph, cycle detection in a directed graph via DFS with three visit states (unvisited / in-progress / done). Sparse graphs only (~10^3-10^4 nodes, ~10^4-5*10^4 edges). The candidate must recognise that a plain `visited` set misses back-edges in diamond-shaped DAGs and reach for the three-state pattern.
- **Tree traversal and LCA**: in / pre / post-order traversal on a binary tree, depth / height, lowest common ancestor of two nodes via a single post-order traversal (no parent pointers, no upward walk-and-intersect), BST search.
- **Big-O reasoning**: justifying why the implementation is O(n) / O(log n) / O(1) / O(V + E).

Do NOT require: weighted shortest path (Dijkstra, Bellman-Ford, A*), dynamic programming, balanced trees, segment trees, tries beyond a single toy example, heaps / priority queues for top-k, sliding-window with multiple invariants, backtracking, or NP-hard approximations. Those are INTERMEDIATE+ topics.

### Problem Statement Structure
Each task's problem statement MUST include:

**Context (light, 1-2 sentences):**
- A short real-world framing so it doesn't feel like a totally abstract puzzle. Examples: "A pricing service needs to look up which spend tier a customer falls into from a sorted list of thresholds", "A session cache must evict the least-recently-used entry when it reaches capacity". Keep it to 1-2 sentences — NOT a full system description.

**Function signature(s):**
- Name the function the candidate must implement and describe in plain English what it takes as input and what it returns (e.g. "Implement `find_pair`, which takes a list of integers and a target integer, and returns the indices of the two numbers that sum to the target — or the documented sentinel when no such pair exists").
- Do NOT enumerate the signature in each supported language. The candidate sees the actual typed signature when they open their chosen language's `solution.*` stub file.

**Inputs / Outputs / Constraints:**
- Explicit constraint ranges (e.g. `1 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`, "the input list is sorted in ascending order").
- Behavior on edge cases: empty input, single element, no valid answer (return what?), ties.

**Worked examples (2-3 of them):**
- Input -> Expected output with a one-line explanation. Keep examples small (~3-8 elements) so the candidate can verify mentally.

**Target Complexity:**
- A target complexity for time and space (e.g. "Your solution should run in O(n) time and O(n) extra space"). This is a soft target reinforced by tests.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use external resources including search, language documentation, and AI tools.
- The task assesses whether the candidate can pick the right data structure and translate it into clean code in their chosen language under time pressure — not memorization.
- Standard library and built-in primitives only — do NOT introduce specialized third-party DSA libraries (`numpy`, `sortedcontainers`, `lodash` collections, Guava containers, Boost) in any of the language scaffolds. The standard test framework for the language is allowed (pytest, jest, JUnit, xUnit, PHPUnit, etc.) — they are not DSA libraries.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a BASIC-level candidate (1-2 yoe) working in any one of the declared supported languages.

### Starter Code Requirements

**EACH folder for a declared language MUST contain:**
- A solution stub file (at the conventional path for that language — see LANGUAGE SUPPORT) with the function signature and a placeholder return value so the file compiles/parses cleanly but the tests fail.
- A test file (at the conventional path) containing 3-5 small assertion tests pinning the documented examples and edge cases. These tests fail against the stub and pass when the candidate implements the function correctly.
- The minimum project metadata files needed for that language's test command to run on a clean checkout (see LANGUAGE SUPPORT for the conventional set per language).

**FUNCTIONAL REQUIREMENTS:**
- All declared-language scaffolds must compile/parse/run cleanly out of the box. ZERO syntax errors. The tests are expected to FAIL against the stub (because the function isn't implemented yet) — but the test runner itself must launch and the failures must be assertion failures, not compile/import errors.
- The candidate should NOT need to fix project plumbing in any of the declared languages to run that language's tests.

**WHAT MUST NOT BE INCLUDED:**
- The actual algorithmic solution in any of the language files (only the stub).
- `// TODO:`, `# hint:`, `// fix me`, or any comments that point at the fix (use whichever comment syntax the language uses, but the rule applies regardless).
- Frameworks, services, controllers, routes, databases, ORM models, async queues, web servers. This is a single-function DSA problem.
- Cross-language wiring — each language folder is fully self-contained; the candidate ignores all the folders they don't use.
- Specialized third-party DSA libraries (see AI policy above).
- Folders for languages NOT declared by the scenario. Match the scenario's declared list exactly.

### Code Generation Instructions
Generate a classic DSA task that:
- Has a clear, narrow function-level problem statement with constraints and worked examples
- Matches BASIC proficiency level (1-2 years + core DSA)
- Can be completed within {minutes_range} minutes in any one of the supported languages declared by the scenario
- Tests practical DSA judgment: picking the right data structure and hitting the right complexity
- Task name: short, descriptive, under 50 characters, kebab-case (e.g. `two-sum-sorted`, `lru-cache-basic`, `balanced-brackets`, `tier-binary-lookup`, `group-anagrams`, `detect-build-cycle`, `team-common-manager`, `connected-components`, `tree-depth`)

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Classic DSA problem statement in plain English. MUST include: (1) Light real-world context (1-2 sentences). (2) The function name + a one-sentence plain-English description of its inputs and output (NO code blocks, NO language-specific signatures — the candidate sees the actual typed signature in their chosen language's `solution.*` stub). (3) Input / Output / Constraints with explicit ranges and edge-case behavior. (4) 2-3 worked examples with brief one-line explanations. (5) Target complexity (time + space). (6) An explicit note that the candidate must pick ONE of the supported language folders, implement the stub in `solution.*`, and ensure that language's tests pass.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below — required",
    ".gitignore": "Exclusions covering all the languages declared by the scenario. Include only what applies: Python (`__pycache__/`, `.pytest_cache/`), Node/TS (`node_modules/`, `dist/`), Java (`target/`, `*.class`), C++ (`*.o`, `*.out`, `build/`), Go (`bin/`, `vendor/`), Ruby (`*.gem`), Rust (`target/`), C# (`bin/`, `obj/`), Kotlin (`build/`), PHP (`vendor/`).",
    "<per-language-files>": "FOR EACH LANGUAGE DECLARED BY THE SCENARIO, output the conventional set of files for that language at the top level of this code_files dict (use concrete keys, NOT a nested dict). The conventional set is: a solution stub file, a test file with 3-5 assertions, and the minimum project metadata files needed for that language's test command to run. See the LANGUAGE SUPPORT section above for the exact conventional paths and files per language. EXAMPLE: if the scenario declares Python + Java, output these keys: `python/solution.py` (stub), `python/test_solution.py` (3-5 pytest tests), `python/pytest.ini`, `java/src/main/java/Solution.java` (stub class), `java/src/test/java/SolutionTest.java` (3-5 JUnit 5 tests), `java/pom.xml`. The set of keys MUST match the scenario's declared languages exactly — no extras, no omissions."
  }},
  "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., the function returns the correct pair of indices for the worked examples, returns the documented sentinel when no pair exists, handles empty input gracefully, completes within the target complexity on a 10^5-element input).",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words). Bullet 1: the light real-world context and what the function takes / returns. Bullet 2: the input constraints and edge-case behavior. Bullet 3: the target complexity outcome plus a note that the candidate picks one of the supported language folders declared by the task. Do NOT prefix bullets with bold mini-titles like '**Context:**' — start each bullet directly with the content.",
  "pre_requisites": "Bullet-point list of tools and knowledge required. Include one bullet for Git, ONE bullet that lists all supported-language toolchains the scenario declares (candidate only needs ONE of them working — join them with OR, e.g. `Python 3.10+ with pip and pytest, OR Node 18+ with npm, OR JDK 17+ with Maven, OR g++ with C++17 + make, OR Go 1.21+`), and ONE bullet for basic DSA knowledge (hash maps, stacks, queues, sorting, binary search, big-O reasoning).",
  "answer": "High-level solution approach — the chosen data structure or algorithmic primitive and target complexity, expressed in language-neutral terms (hash map / stack / FIFO queue / ordered map / sorted-search helper / adjacency list with BFS or DFS / three-state DFS for cycle detection / post-order traversal for LCA) rather than language-specific stdlib symbols. Do not give the exact code.",
  "hints": "Single line guiding the candidate toward the right structural insight (e.g. 'Think about which structure can answer membership-and-lookup in constant time' or 'Look for a way to reduce the linear scan to logarithmic on already-sorted data'). Must NOT name the exact data structure or any language-specific stdlib symbol.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (DSA Basic — LeetCode-style, 4 sections ONLY)
The README is a LeetCode-style problem page. The candidate should be able to scan it like a LeetCode problem and know exactly what to implement. The README MUST contain EXACTLY the following four sections, in this order, and NOTHING else:

1. Task Overview
2. Examples
3. Constraints
4. How to Verify

Do NOT add any other section. NO "Objectives". NO "Helpful Tips". NO "Choose Your Language". NO separate "Problem Statement" header. NO setup instructions.

### 1. Task Overview (MANDATORY — LeetCode-style problem statement)
Multi-paragraph prose problem statement in the style of a LeetCode problem description (e.g. https://leetcode.com/problems/clone-graph). Aim for 3-6 sentences across 1-3 short paragraphs that describe:
  - What the function takes as input and what it returns
  - Any semantic rules the candidate must respect (e.g. "the input list is sorted ascending", "the graph is directed and may contain unreachable components", "treat upper and lower case as the same")
  - For non-trivial input data shapes (graph as adjacency list, binary tree node, linked-list node), include ONE small code block showing the data shape — e.g. a `class Node {{ int val; List<Node> neighbors; }}` block or a worded "Test case format:" explanation of how inputs are represented
  - End with a single short sentence naming the function the candidate must implement, e.g. "Implement `clone_graph` in your chosen language."

NO per-language signature enumeration. NO function-signature code blocks. Data-shape definitions (class layouts, adjacency-list format explanations) ARE allowed when the input is non-trivial.

### 2. Examples (MANDATORY — 2-3 worked examples, LeetCode-style)
Each example MUST follow this exact shape, including the BLANK LINES between the Input / Output / Explanation rows (the blank lines are required so each renders on its own line on GitHub — without them, Markdown collapses the three rows into one paragraph):

```
**Example N:**

[Optional small diagram block — see DIAGRAM RULES below]

**Input:** <literal input value>

**Output:** <literal output value>

**Explanation:** <one to three sentences explaining why this input produces this output>
```

The `**Input:**`, `**Output:**`, `**Explanation:**` labels MUST be bolded (markdown `**` around the label including the colon), and there MUST be a blank line between each of the three rows. Do not collapse them onto consecutive lines.

Use 2-3 examples total. Cover the happy path, at least one edge case (empty input, single element, no-match sentinel), and a representative non-trivial input. Keep inputs small (~3-8 elements / a handful of edges) so the candidate can verify mentally.

**DIAGRAM RULES:**
- Graph problems: include a Mermaid diagram in a fenced ```mermaid``` code block. Use `graph LR` for undirected (edges `1 --- 2`) and `graph LR` with `-->` for directed (edges `1 --> 2`). Example:
  ```mermaid
  graph LR
    1 --- 2
    2 --- 3
    3 --- 4
    4 --- 1
  ```
- Tree problems: use Mermaid `graph TD` with directed parent→child edges (`1 --> 2`, `1 --> 3`, etc.).
- Linked-list problems: use Mermaid `graph LR` with directed edges (`1 --> 2 --> 3`).
- Array, string, numeric, or other non-visual problems: SKIP the diagram. Just Input/Output/Explanation.
- Keep diagrams small (≤ 10 nodes). GitHub renders Mermaid natively.

### 3. Constraints (MANDATORY — pure bounds list)
Bullet list of the bounds and edge-case rules. Include:
- Input ranges (e.g. `1 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`, `0 <= V <= 10^4`, `0 <= E <= 5*10^4`).
- Assumptions on input shape (e.g. "the list is sorted in ascending order", "the graph is directed and may contain unreachable components", "the tree may be empty").
- Behavior on edge cases — what to return for empty input, single element, no valid answer (the documented sentinel — empty list, `None`/`null`/`nullopt`, `-1`, etc.), ties.
- Target complexity (e.g. "O(n) time, O(n) space"; "O(V + E) time").

NO examples sub-block in this section — Examples is its own section above. Just the bounds.

### 4. How to Verify (MANDATORY — bullet points, 3-4 bullets)
Provide verification checkpoints as a short bullet list:

  - Tell the candidate which stub to edit (the `solution.*` file inside their chosen language folder) and which test command to run for that language
  - Include the relevant test commands inline as compact code spans (e.g. `pytest`, `npm test`, `mvn test`, `make test`, `go test ./...`)
  - Specify that all committed tests in the chosen folder must pass
  - Note that only the standard library / built-in primitives may be used — no third-party DSA libraries
  - **CRITICAL**: Bullet points only. No paragraphs. No troubleshooting or setup instructions.

### NOT TO INCLUDE (anywhere in the README):
- An "Objectives" section, a "Helpful Tips" section, a "Choose Your Language" section, a separate "Problem Statement" header, or any other narrative section beyond the four above.
- Setup or install instructions for any toolchain.
- Step-by-step implementation instructions.
- Exact code solutions or snippets.
- Per-language function-signature code blocks (data-shape definitions are OK, function signatures are NOT).
- Names of specific stdlib classes in any language that point at the fix.
- Any prose that reveals the data structure or algorithm choice.

**CRITICAL:** NO section may name a data structure or algorithm. NO section may reveal the solution shape. The candidate derives the structural choice themselves from the Task Overview + Examples + Constraints.

## CRITICAL REMINDERS

1. **This is a classic DSA problem, NOT an app build.** No frameworks, no controllers, no routes, no databases, no service classes, no business-layer abstractions. One function, typed inputs, typed output.
2. **The set of language folders is decided by the SCENARIO, not the prompt.** Emit a folder + stub + test + metadata for EACH language declared by the scenario — no extras, no omissions. If the scenario declares no languages, default to Python + JavaScript + Java.
3. **For each declared language folder, ALL of: solution stub, test file, project metadata must be present and runnable.** ZERO compile/import errors. Tests fail against the stub but the test runner itself launches cleanly.
4. **The candidate picks ONE language.** The other declared folders are ignored. The problem statement is identical across all declared languages.
5. **Solution stubs return a placeholder so tests fail** until the candidate implements the function. The starter must not contain the actual algorithmic answer.
6. **NO comments** that reveal the solution or give hints, in any of the declared language stubs.
7. **Task must be completable within {minutes_range} minutes** with a hard cap at 30 minutes.
8. **Focus on BASIC DSA only** — hash maps, stacks/queues, simple LRU (ordered map or hashmap+DLL), sorting, binary search (sorted or locally monotonic), basic strings, trivial graph algorithms on adjacency lists (BFS / DFS / connected components / cycle detection via three-state DFS), binary-tree traversal and LCA via single post-order pass. NO weighted shortest path (Dijkstra), NO DP, NO balanced/segment trees, NO heaps for top-k, NO sliding-window with multiple invariants.
9. **Standard library / built-in primitives only** in every declared language. The standard test framework per language is allowed (pytest, jest, JUnit, xUnit, PHPUnit, etc.).
10. **README.md is language-agnostic prose** — NO per-language signature code blocks in the README. The actual typed signature lives in each language's `solution.*` stub file; the candidate sees it when they open their chosen folder.
11. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD describe the algorithmic shape (e.g. `two-sum-sorted`, `lru-cache-basic`) rather than starting with a generic `dsa-` prefix.
12. **Select a different inspiration scenario** each time for variety, but always render the result as a classic DSA problem — not as a refactor of an existing app module.
"""

PROMPT_REGISTRY = {
    "Data Structures and Algorithms (BASIC)": [
        PROMPT_DSA_BASIC_CONTEXT,
        PROMPT_DSA_BASIC_INPUT_AND_ASK,
        PROMPT_DSA_BASIC,
    ]
}
