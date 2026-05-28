PROMPT_DSA_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DSA_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Data Structures and Algorithms assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}


CRITICAL TASK GENERATION REQUIREMENTS:
- The scenarios above are inspiration for the TYPE of problem (which algorithmic primitive to target — graph traversal, trie, heap, DP, sliding window) and a 1-2 sentence flavor wrapper. They are NOT a brief to embed the problem inside a real application, framework, route, or service module.
- The task you generate MUST be a CLASSIC DSA PROBLEM at INTERMEDIATE difficulty: one function (or one small class with 2-3 methods) to implement, typed inputs, typed output, explicit constraints, 2-3 worked examples, and an explicit target complexity — NOT an app build, NOT a refactor inside an existing service module.
- The task is LANGUAGE-AGNOSTIC: the candidate will pick ONE of five supported languages (Python, JavaScript, Java, C++, Go) and implement the function only in that language. The starter project ships stub + tests in ALL five languages.
- The task complexity must be appropriate for INTERMEDIATE level (3-5 years of experience).
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different inspiration scenario each time to ensure variety.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (The algorithmic primitive involved — graph / trie / heap / DP / sliding window — the function the candidate will implement, and the light real-world flavor used as context)
2. What will the task look like? (The single function deliverable, the five language stubs that will ship, and how it aligns with INTERMEDIATE DSA proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DSA_INTERMEDIATE = """
# Data Structures and Algorithms Intermediate Task Requirements

## GOAL
As a technical architect super experienced in core Data Structures and Algorithms, you are given inspiration scenarios and proficiency levels for DSA work at the INTERMEDIATE level (3-5 yoe). Your job is to generate a CLASSIC DSA PROBLEM at intermediate difficulty that can be solved in the candidate's choice of FIVE supported languages. This is NOT an app build and NOT a refactor inside an existing service module — the candidate implements ONE function (occasionally one small class with 2-3 methods) that takes typed inputs and returns a typed output. The starter project ships a solution stub + a small test file in EACH of the five supported languages so the candidate picks one language and codes against that language's skeleton.

## SUPPORTED LANGUAGES (the candidate picks ONE)
The starter MUST include solution + test scaffolds for ALL FIVE of the following languages. The candidate picks ONE based on their preference; the other four folders are left untouched.

1. **Python 3.10+** — solution at `python/solution.py`, tests at `python/test_solution.py`, runs via `pytest`
2. **JavaScript (Node 18+)** — solution at `javascript/solution.js`, tests at `javascript/solution.test.js`, runs via `jest` (declared in `javascript/package.json`)
3. **Java 17+** — solution at `java/src/main/java/Solution.java`, tests at `java/src/test/java/SolutionTest.java`, runs via Maven (`mvn test`) with `java/pom.xml`
4. **C++17** — solution at `cpp/solution.cpp` (with declaration in `cpp/solution.h`), tests at `cpp/test_solution.cpp` using only `<cassert>` from the standard library inside a plain `main()` runner, built via `cpp/Makefile` (`g++ -std=c++17`)
5. **Go 1.21+** — solution at `go/solution.go`, tests at `go/solution_test.go`, runs via `go test ./...`, with `go/go.mod`

The PROBLEM STATEMENT (function name, inputs, outputs, constraints, examples) is identical across all five languages — only the syntax differs.

## INSTRUCTIONS

### INTERMEDIATE PROFICIENCY SCOPE (3-5 yoe — what the task may assess)
Tasks MUST align with INTERMEDIATE DSA. The task may assess one or more of the following; do NOT go beyond this scope into expert/research-level topics:

- **Graph algorithms (foundational)**: BFS / DFS on adjacency lists, Dijkstra's algorithm using a priority queue, topological sort on DAGs, connected components, simple cycle detection. Sparse graphs only (~1K-50K nodes / edges in realistic problem sizes). NO Bellman-Ford, NO Floyd-Warshall, NO A*, NO max-flow.
- **Trees and tries**: Trie for prefix-based autocomplete / lookup, BST traversal patterns, simple LCA on small trees, k-ary tree traversal. NO red-black / B-tree / segment-tree implementations from scratch.
- **Heaps / priority queues**: Top-k via min-heap of size k, k-way merge, sliding-window medians via two heaps, scheduling with a priority queue. The candidate must understand WHY heap-of-k beats full-sort.
- **Dynamic programming (bounded)**: 1D and small 2D tabulation problems — coin change, longest increasing subsequence, edit distance, classic knapsack on small N, climbing stairs / house robber variants. The candidate must reason about state, transition, and base case clearly. NO bitmask DP, NO multi-dimensional DP beyond 2D, NO DP-on-trees.
- **Hashing + sliding window**: Rolling-window aggregates with a FIFO deque/queue and a counts map, anagram-window patterns, longest-substring-without-repeats. Maintaining O(n) under expiry.
- **Big-O reasoning under realistic data sizes**: Justifying complexity and writing tests that distinguish the new bound from a brute-force baseline.

Do NOT require: graph algorithms beyond Dijkstra (no NP-hard / approximation), advanced/balanced tree implementations from scratch, segment trees, suffix arrays/automata, advanced string algorithms (KMP/Aho-Corasick from scratch), bitmask DP, or anything that veers into research territory. Those are EXPERT-level.

### Nature of the Task
- Task must be a classic, self-contained DSA problem at intermediate difficulty: ONE function (occasionally one small class with 2-3 methods, e.g. an autocomplete index with `add` / `query`, or a top-k tracker with `record` / `top`) to implement, with clearly typed inputs and outputs, explicit constraints on input sizes, and 2-3 worked examples.
- The inspiration scenario may PROVIDE light real-world flavor in 1-2 sentences (e.g. "A routing service needs shortest-path distances between depots in a sparse road graph", "An autocomplete index needs popularity-ordered completions for a typed prefix"), but the deliverable is a PURE FUNCTION (or pure data structure) — not a service, route, controller, web framework handler, or module embedded in a wider application. No HTTP, no databases, no ORM models.
- The candidate implements the function in their chosen language's `solution.*` file and runs that language's test command to verify.
- The task must surface real INTERMEDIATE DSA judgment — picking the right primitive, justifying the complexity, handling edge cases (same-node path, unreachable destination, empty prefix, regional denominations breaking greedy, window expiry).
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The solution stub in each language must return a trivial placeholder (e.g. `return []`, `return None`, `return -1`, `return null`, `return false`) so the file compiles/runs but the tests fail until the candidate implements it correctly.

### Problem Statement Structure
Each task's problem statement MUST include:

**Context (light, 1-2 sentences):**
- A short real-world framing so it doesn't feel like a totally abstract puzzle. Examples: "Given a sparse road graph between depots, return the shortest travel time between two depots", "Given a stream of product views, return the top-k most popular products at any point". Keep it to 1-2 sentences — NOT a full system description.

**Function signature(s):**
- The exact function name(s), parameter names, parameter types, and return types the candidate must implement.
- State the signature in language-neutral form first (e.g. `shortest_path(graph: Dict[str, List[Tuple[str, int]]], start: str, end: str) -> Tuple[int, List[str]] | None`) and then list the equivalent signatures in EACH of the five supported languages.
- If the task is a small class (e.g. `Autocomplete` with `add(word, popularity)` and `query(prefix, k)`), specify the full class shape in all five languages.

**Inputs / Outputs / Constraints:**
- Explicit constraint ranges (e.g. `1 <= |V| <= 10^4`, `1 <= |E| <= 5 * 10^4`, `0 <= weight <= 10^4`, "the graph is directed and may have unreachable components").
- Behavior on edge cases: same-node path, unreachable destination, empty prefix, no valid answer (return what?), ties (deterministic tiebreak rule).

**Worked examples (2-3 of them):**
- Input -> Expected output with a one-line explanation. Keep the example graphs / inputs small (5-10 nodes, ~6-12 edges) so the candidate can verify mentally.

**Target Complexity:**
- An explicit target complexity (e.g. "O((V + E) log V) time and O(V) extra space", "O(prefix_len + k) per query after a one-time O(total_chars) build"). The tests should informally distinguish this from the brute-force baseline on the documented upper bound.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use external resources including search, language documentation, and AI tools.
- The task assesses whether the candidate can pick the right algorithmic primitive and translate it into clean code in their chosen language under time pressure — not memorization.
- Standard library and built-in primitives only — do NOT introduce specialized third-party DSA libraries (`numpy`, `networkx`, `sortedcontainers`, `lodash` collections, Guava containers, Boost) in any of the language scaffolds. JUnit (for Java) and Jest (for JavaScript) are allowed solely as the test framework — they are not DSA libraries.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by an INTERMEDIATE-level candidate (3-5 yoe). Hard cap at 40 minutes — if the scope cannot fit, simplify the input shape rather than dropping language scaffolds.

### Starter Code Requirements

**EACH language folder MUST contain:**
- A `solution.*` file with the function (or class) signature stubbed out — returning a placeholder value so the file compiles/runs cleanly but the tests fail.
- A test file containing 4-6 small assertion tests pinning the documented examples, edge cases (same-node, unreachable, empty prefix, ties, regional denominations, etc.), and at least one larger-input test that informally exercises the target complexity (the brute-force baseline would visibly struggle while the correct primitive completes quickly).
- The minimum project metadata files for that language's test command to run on a clean checkout:
  - Python: `python/pytest.ini` (or rely on default discovery — keep it minimal)
  - JavaScript: `javascript/package.json` declaring `jest` as a devDependency and a `"test": "jest"` script
  - Java: `java/pom.xml` with JUnit 5 (`junit-jupiter`) as the test dependency and the standard `maven-surefire-plugin`
  - C++: `cpp/Makefile` with a `test` target that compiles `solution.cpp` + `test_solution.cpp` with `g++ -std=c++17` and runs the resulting binary
  - Go: `go/go.mod` declaring the module

**FUNCTIONAL REQUIREMENTS:**
- All five language scaffolds must compile/parse/run cleanly out of the box. ZERO syntax errors. The tests are expected to FAIL against the stub (because the function isn't implemented yet) — but the test runner itself must launch and the failures must be assertion failures, not compile/import errors.
- The candidate should NOT need to fix project plumbing in any of the five languages to run that language's tests.

**WHAT MUST NOT BE INCLUDED:**
- The actual algorithmic solution in any of the language files (only the stub).
- `// TODO:`, `# hint:`, `// fix me`, or any comments that point at the fix (use whichever comment syntax the language uses, but the rule applies regardless).
- Frameworks, services, controllers, routes, databases, ORM models, async queues, web servers. This is a single-function DSA problem.
- Cross-language wiring — each language folder is fully self-contained; the candidate ignores the four they don't use.
- Specialized third-party DSA libraries (see AI policy above).

### Code Generation Instructions
Generate a classic DSA task at intermediate difficulty that:
- Has a clear, narrow function-level (or small-class-level) problem statement with constraints and worked examples
- Matches INTERMEDIATE proficiency level (3-5 years + core DSA)
- Can be completed within {minutes_range} minutes in any one of the five supported languages
- Tests practical INTERMEDIATE DSA judgment: picking the right algorithmic primitive, handling edge cases, hitting the target complexity
- Task name: short, descriptive, under 50 characters, kebab-case, and SHOULD describe the algorithmic shape (e.g. `shortest-path-sparse-graph`, `prefix-autocomplete-trie`, `top-k-stream`, `coin-change-min-count`, `longest-substring-no-repeats`)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "task-name-in-kebab-case",
   "question": "Classic DSA problem statement. MUST include: (1) Light real-world context (1-2 sentences). (2) The function (or class) signature — listed in language-neutral form and then in each of the FIVE supported languages (Python, JavaScript, Java, C++, Go). (3) Input / Output / Constraints with explicit ranges and edge-case behavior (same-node path, unreachable, empty prefix, ties, regional denominations breaking greedy, window expiry — whichever apply). (4) 2-3 worked examples with brief one-line explanations. (5) Target complexity (time + space, e.g. 'O((V+E) log V) time, O(V) space'). (6) An explicit note that the candidate must pick ONE of the five language folders, implement the stub in `solution.*`, and ensure that language's tests pass.",
   "code_files": {{
      "README.md": "Candidate-facing README following the structure below — required",
      ".gitignore": "Multi-language exclusions covering Python (`__pycache__/`, `.pytest_cache/`), Node (`node_modules/`, `dist/`), Java (`target/`, `*.class`), C++ (`*.o`, `*.out`, `build/`), Go (`bin/`, `vendor/`)",
      "python/solution.py": "Stub with the function / class signature returning a placeholder value (e.g. `return None` / `return []`)",
      "python/test_solution.py": "4-6 pytest tests pinning the documented examples, edge cases, and one larger-input test that informally exercises the target complexity",
      "python/pytest.ini": "Minimal pytest config (or omit if defaults suffice)",
      "javascript/solution.js": "Stub with the function / class signature returning a placeholder value, exported via CommonJS `module.exports`",
      "javascript/solution.test.js": "4-6 jest tests pinning the documented examples, edge cases, and one larger-input test",
      "javascript/package.json": "Declares jest as a devDependency and a `\\\"test\\\": \\\"jest\\\"` script",
      "java/src/main/java/Solution.java": "Stub class with the function / class signature returning a placeholder value",
      "java/src/test/java/SolutionTest.java": "4-6 JUnit 5 tests pinning the documented examples, edge cases, and one larger-input test",
      "java/pom.xml": "Maven config with JUnit 5 dependency (`junit-jupiter`) and `maven-surefire-plugin`",
      "cpp/solution.h": "Header declaring the function / class signature so the test file can include it",
      "cpp/solution.cpp": "Stub implementing the function from solution.h, returning a placeholder value",
      "cpp/test_solution.cpp": "Plain `main()` runner using `<cassert>` from the standard library — 4-6 assertions pinning the documented examples, edge cases, and one larger-input test, prints `\\\"All tests passed\\\\n\\\"` if every assert succeeds",
      "cpp/Makefile": "Tiny Makefile with a `test` target that compiles solution.cpp + test_solution.cpp with `g++ -std=c++17 -o test_solution` and runs `./test_solution`",
      "go/solution.go": "Stub with the function / class signature returning a placeholder value, in `package solution`",
      "go/solution_test.go": "4-6 `go test` cases pinning the documented examples, edge cases, and one larger-input test, in `package solution`",
      "go/go.mod": "Module declaration (e.g. `module solution` with `go 1.21`)"
   }},
   "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., shortest_path returns the correct total cost and ordered node list on the worked examples, returns the documented sentinel on unreachable, completes the 1K-node test in well under a second; autocomplete returns popularity-sorted top-k completions in time independent of catalog size; coin-change returns the optimal count and `-1` when unreachable).",
   "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~20-30 words). Bullet 1: the light real-world context and what the function takes / returns. Bullet 2: the input constraints and the key edge cases the candidate must handle. Bullet 3: the target complexity outcome plus a note that the candidate picks one of the five supported languages. Do NOT prefix bullets with bold mini-titles like '**Context:**' — start each bullet directly with the content.",
   "pre_requisites": "Bullet-point list of tools needed — the candidate only needs ONE language toolchain working: Python 3.10+ + pip + pytest, OR Node 18+ + npm, OR JDK 17+ + Maven, OR g++ with C++17 support + make, OR Go 1.21+. Always include Git and intermediate DSA knowledge (graph algorithms, tries, heaps, dynamic programming, big-O reasoning).",
   "answer": "High-level solution approach — the chosen primitive (e.g. Dijkstra with a priority queue / Trie / heap-of-k / bottom-up DP / sliding window with FIFO queue + counts map), the target complexity, and edge cases (same-node / unreachable / empty prefix / regional denominations / window expiry). Use language-neutral terms (priority queue, FIFO queue, sorted structure with binary search) rather than language-specific stdlib symbols. Do not give the exact code.",
   "hints": "Single line guiding the candidate toward the right algorithmic insight (e.g. 'Think about which graph algorithm gives shortest paths under non-negative weights without exploring every path' or 'Look for a way to keep only the running top-k instead of re-sorting the full counts list'). Must NOT name the algorithm by name.",
   "definitions": {{
     "terminology_1": "definition_1",
     "terminology_2": "definition_2"
   }}
}}

## README.md STRUCTURE (DSA Intermediate, language-agnostic)
The README.md MUST contain the following sections, in this order:
- Task Overview
- Problem Statement (signature + constraints + examples)
- Choose Your Language
- Objectives
- Helpful Tips
- How to Verify

### Task Overview (MANDATORY — 3-4 substantial sentences)
**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the light real-world context, the input shape and scale, the engineering judgment the problem is testing (which primitive, why), and what "done" looks like in behavioral terms. NEVER generate empty content.

### Problem Statement
- The function (or class) signature in language-neutral form, then in EACH of the five supported languages (Python, JavaScript, Java, C++, Go).
- Input constraints and ranges (V/E for graphs, catalog size for tries, stream length for top-k, denomination set for coin-change, etc.).
- Output specification including what to return when there is no valid answer (the documented sentinel — empty list, None / null / nullopt, -1, etc.).
- 2-3 worked examples with brief one-line explanations.
- Target complexity (e.g. "O((V + E) log V) time, O(V) space"; "O(prefix_len + k) per query after a one-time O(total_chars) build").

### Choose Your Language
- The candidate picks ONE of: `python/`, `javascript/`, `java/`, `cpp/`, `go/`.
- For each language, name the solution file the candidate edits (`solution.py`, `solution.js`, `Solution.java`, `solution.cpp`, `solution.go`) and the test file that pins the contract.
- Make it explicit that only the chosen folder needs to be edited — the other four are ignored.

### Objectives
Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name the algorithm, name a language-specific stdlib symbol, or otherwise tell the candidate what code to write.

**Allowed phrasing — describes outcome, hides solution:**
- "shortest_path returns the correct total cost and ordered node list on the worked examples; calling it with the same node as start and end returns zero cost and a single-node path; an unreachable destination returns the documented sentinel."
- "Autocomplete returns the top-k completions for any prefix in popularity order, and average lookup time is informally independent of catalog size on the larger-input test."
- "Coin-change returns the optimal coin count for `(14, [1, 7, 10])` and returns `-1` when the amount is unreachable."
- "The longest-substring function never re-scans a character more than a small constant number of times on the larger-input test."

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Use Dijkstra's algorithm with a priority queue." *(names the algorithm)*
- ❌ "Build a Trie at construction time and walk it on each query." *(names the data structure)*
- ❌ "Replace the full sort with a min-heap of size k." *(names the shape)*
- ❌ "Use a 1D bottom-up DP array indexed by amount." *(prescribes the DP shape)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behavior* the function must demonstrate, not the *code* it must contain.

Keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the function never raises on user input"). The remaining objectives must be specific to the problem's primary algorithmic primitive and complexity target.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.

### Helpful Tips
- Engineering considerations framed as questions ("Which graph algorithm guarantees shortest paths under non-negative edge weights without exploring every path?", "Where should the prefix-completion list live so query time is independent of catalog size?", "What does the window-expiry pattern look like when events must be removed in the same pass that adds new ones?", "Why does greedy fail on `[1, 7, 10]` for `14`, and what changes when you tabulate from the bottom up?")
- Important considerations: edge cases (same-node, unreachable, empty prefix, ties, regional denominations, expired events), big-O of the chosen approach, when to test correctness vs when to test performance informally
- 4-5 concise bullets MAX
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

### How to Verify
- Run the chosen language's test command (e.g. `pytest`, `npm test`, `mvn test`, `make test`, `go test ./...`).
- All committed tests in that language's folder pass — examples, edge cases, AND the larger-input test that informally exercises the target complexity.
- Standard library / built-in primitives only — no third-party DSA libraries.
- Public function / class signatures stable so the committed tests compile.

### NOT TO INCLUDE in README
- SETUP INSTRUCTIONS for any toolchain (the candidate is expected to already know how to run their chosen language's tests)
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Direct solutions or hints
- Names of specific algorithms or stdlib symbols in any language (do not say "use Dijkstra" — say "find a graph algorithm that guarantees shortest paths under non-negative weights"; do not say "use a Trie" — say "find a structure that makes prefix lookup independent of catalog size")
- Snippets that would reveal the algorithm or data structure choice

## CRITICAL REMINDERS

1. **This is a classic DSA problem, NOT an app build.** No frameworks, no controllers, no routes, no databases, no service classes, no business-layer abstractions. One function (or one small class), typed inputs, typed output.
2. **All FIVE language folders must be present and runnable** — Python, JavaScript, Java, C++, Go. Each has a solution stub + 4-6 tests + the minimum metadata for that language's test command to run.
3. **The candidate picks ONE language.** The other four are ignored. The problem statement is identical across all five.
4. **Solution stubs return a placeholder so tests fail** until the candidate implements the function. The starter must not contain the actual algorithmic answer.
5. **NO comments** that reveal the solution or give hints, in any of the five language stubs.
6. **Task must be completable within {minutes_range} minutes** with a hard cap at 40 minutes.
7. **Focus on INTERMEDIATE DSA only** — graph (BFS/DFS/Dijkstra), trees/tries, heaps for top-k / scheduling, 1D-2D DP, sliding-window with FIFO queue + counts map. AVOID expert/research topics (Bellman-Ford, Floyd-Warshall, A*, max-flow, segment trees, bitmask DP, suffix automata, etc.).
8. **Standard library / built-in primitives only** in every language. JUnit (Java) and Jest (JavaScript) are allowed as the test framework only.
9. **README.md must list the function / class signature in all FIVE languages** so the candidate sees how their chosen language declares it.
10. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD describe the algorithmic shape (e.g. `shortest-path-sparse-graph`, `prefix-autocomplete-trie`) rather than starting with a generic `dsa-` prefix.
11. **Select a different inspiration scenario** each time for variety, but always render the result as a classic DSA problem — not as a refactor of an existing app module.
"""

PROMPT_REGISTRY = {
    "Data Structures and Algorithms (INTERMEDIATE)": [
        PROMPT_DSA_INTERMEDIATE_CONTEXT,
        PROMPT_DSA_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_DSA_INTERMEDIATE,
    ]
}
