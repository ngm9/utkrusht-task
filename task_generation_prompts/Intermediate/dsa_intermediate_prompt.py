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
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (INTERMEDIATE: 3-5 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic INTERMEDIATE DSA work that a 3-5 yoe engineer would actually own — replacing a brute-force algorithm with a graph traversal / trie / heap / DP that materially changes the complexity, and pinning the new contract with both correctness tests AND a performance test on a realistic input size.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the data structure / algorithm involved, the complexity transition, and the specific problem the candidate will be solving)
2. What will the task look like? (Describe the type of refactor / fix / extension required, the expected deliverables, and how it aligns with INTERMEDIATE DSA proficiency)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DSA_INTERMEDIATE = """
# Data Structures and Algorithms Intermediate Task Requirements

## GOAL
As a technical architect super experienced in core Data Structures and Algorithms across multiple languages, you are given real-world scenarios and proficiency levels for DSA work at the INTERMEDIATE level (3-5 yoe). Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to recognize when a brute-force / wrong-shape implementation must be replaced with the right algorithmic primitive (graph traversal, trie, heap, dynamic programming) inside an existing module — and to pin the resulting contract with rigorous correctness AND performance tests.

**LANGUAGE / RUNTIME IS DERIVED FROM THE SCENARIO.** Do NOT assume Python. The chosen scenario specifies the application stack (file extensions, module paths, runtime hints) — the generated starter code, file structure, build/run commands, and test framework MUST follow whatever language the scenario implies (e.g. Python with `pytest`, TypeScript/Node with `jest` or `vitest`, Java with JUnit + Maven/Gradle, Go with the built-in test runner, C# with xUnit). If the scenario is language-agnostic in wording, default to the most natural language for the domain described.

## INSTRUCTIONS

### INTERMEDIATE PROFICIENCY SCOPE (3-5 yoe — what the task may assess)
Tasks MUST align with INTERMEDIATE DSA. The task may assess one or more of the following; do NOT go beyond this scope into expert/research-level topics. Examples below name common stdlib helpers across languages — the candidate uses whatever ships with the chosen language's standard library or built-in primitives:

- **Graph algorithms (foundational)**: BFS / DFS on adjacency lists, Dijkstra's algorithm using a priority queue (e.g. Python `heapq`, Java `PriorityQueue`, JS via heap implementation, Go `container/heap`), topological sort on DAGs, connected components, simple cycle detection. Sparse graphs only (~10K-50K nodes / edges in realistic scenarios). NO Bellman-Ford, NO Floyd-Warshall, NO A*, NO max-flow.
- **Trees and tries**: Trie for prefix-based autocomplete / lookup, BST traversal patterns, simple LCA on small trees, k-ary tree traversal. NO red-black trees, NO B-trees, NO segment-tree implementations from scratch.
- **Heaps / priority queues**: Top-k via min-heap of size k, k-way merge, sliding-window medians via two heaps, scheduling with a priority queue. The candidate must understand WHY heap-of-k beats full-sort.
- **Dynamic programming (bounded)**: 1D and small 2D tabulation problems — coin change, longest increasing subsequence, edit distance, classic knapsack on small N. The candidate must reason about state, transition, and base case clearly. NO bitmask DP, NO multi-dimensional DP beyond 2D, NO DP-on-trees.
- **Hashing + sliding window**: Rolling-window aggregates with a FIFO deque/queue and a counts map, anagram-window patterns, longest-substring-without-repeats. Maintaining O(n) under expiry.
- **Algorithm-aware refactoring inside a real module**: Replacing an O(n^2) inner loop with an O(n) hash-grouped pass; replacing a full sort with a heap-of-k; replacing a recursive DFS with iterative BFS to avoid stack-depth issues; replacing greedy with DP when greedy is provably wrong.
- **Big-O reasoning under realistic data sizes**: Justifying complexity, picking inputs that demonstrate the difference, writing a performance test that pins the new bound (e.g., "1000 nodes finishes in <100ms", "200K events tops out at 5ms per call").

Do NOT require: graph algorithms beyond Dijkstra (no NP-hard / approximation), advanced/balanced tree implementations from scratch, segment trees, suffix arrays/automata, advanced string algorithms (KMP/Aho-Corasick from scratch), bitmask DP, or anything that veers into research territory. Those are EXPERT-level.

### Nature of the Task
- Task must ask the candidate to refactor an existing brute-force / wrong-complexity-class implementation into the appropriate algorithmic primitive (graph traversal, trie, heap, DP) inside a realistic module **in the language the scenario implies**, OR to fix a logic bug AND tighten the complexity at the same time.
- The starter project MUST include a small, runnable package (in whatever language the scenario specifies) with the brute-force / buggy implementation already wired in, plus a test suite (using the language's idiomatic test framework — e.g. `pytest`, `jest`/`vitest`, JUnit, Go test, xUnit) that exercises both correctness on a small fixture and (often) the wrong/slow contract. The candidate should NOT have to set up project plumbing.
- The question scenario must be clear, with realistic facts, figures, company names, and numbers (graph sizes, query rates, latency budgets) that are consistent with the chosen domain.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The brute-force / wrong behavior described in the scenario MUST actually be present in the starter implementation.
- The task must surface real INTERMEDIATE DSA judgment — picking the right primitive, justifying the complexity, handling edge cases (same-node path, unreachable destination, empty prefix, regional denominations breaking greedy), and writing a performance test that distinguishes the new implementation from the old.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts:

**Current Implementation (what we give to the candidate):**
- Describe precisely the brute-force / wrong-algorithm / buggy state that the starter code implements. Include realistic input sizes, observed latency, and any concrete logic bug (e.g. "DFS returns None when start == end because the visited-guard treats it as already-visited").
- Examples: "shortest_path uses recursive DFS over 28K edges and times out at 5s"; "autocomplete linearly scans 180K product names per keystroke"; "top-k re-sorts the entire 200K-key dict on every dashboard tick"; "coin-change is greedy and produces wrong answers on regional denominations".
- The **starter code MUST perfectly implement this current behavior** — it must run, it must produce the observed latency / wrong answer, and it must NOT accidentally include the fix.

**Required Changes (what the candidate must do):**
- List the specific algorithmic / structural changes the candidate must apply, expressed in terms of the algorithm and its target complexity (not in stdlib symbols of any particular language). Examples: "Replace the recursive DFS with Dijkstra using a priority queue; return zero cost + single-node path for the same-node case and an unreachable sentinel for unreachable"; "Build a Trie at module-load time storing the popularity-sorted top-k completions per prefix node so query is O(prefix_len + k)"; "Replace the full sort with a min-heap of size k AND fix the window expiry with a FIFO queue keyed by timestamp"; "Replace greedy with bottom-up DP over a 1D table indexed by amount; return -1 when unreachable".
- The candidate's job is to apply these required changes on top of the current implementation, plus extend tests to pin the new correctness AND complexity contract.

**Final Implementation Approach:**
- A high-level description of the correct approach, including the chosen primitive (Dijkstra / Trie / Heap-of-k / Bottom-up DP) and the target complexity. Use abstract terms (priority queue, FIFO queue, sorted structure with binary search) rather than language-specific symbols. The candidate's solution does not have to match this verbatim, but must hit the same complexity class.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including Google, Stack Overflow, official language docs, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to recognize the right algorithmic primitive for a real product problem and integrate it cleanly into an existing module while pinning the new contract with tests — not to test rote memorization. Therefore, the complexity should reflect intermediate DSA proficiency while requiring genuine engineering judgment that goes beyond pasting a generic LeetCode template.
- Use modern conventions for whichever language the scenario implies (Python 3.10+ / PEP 8, modern TypeScript/ESM, Java 17+, Go 1.21+, etc.). Use standard library and built-in primitives only — do NOT introduce specialized third-party DSA libraries (`numpy`, `networkx`, `sortedcontainers`, `lodash` collections, Guava, etc.) unless the scenario explicitly justifies it.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years). Hard cap at 30 minutes — if the scope cannot fit, drop one of the new tests rather than splitting the algorithm work.

### Starter Code Requirements

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- The starter code MUST be a complete, working project in the language implied by the scenario, runnable with the standard install + test commands for that ecosystem (e.g. Python: `pip install -r requirements.txt && pytest`; Node/TS: `npm install && npm test`; Java/Maven: `mvn test`; Go: `go test ./...`).
- ZERO syntax errors, ZERO runtime errors. The existing tests must run; the brute-force / wrong-output behavior must be reproducible (e.g. the slow test exceeds the latency budget; the regression test for the regional denomination fails).
- The candidate should NOT need to fix project plumbing to make tests run.

**WHAT MUST BE INCLUDED:**
- A clear source folder layout matching the language's conventions, containing the brute-force / buggy module(s) at the path the scenario implies (e.g. the scenario may explicitly reference `src/routing/graph.py`, `src/search/Autocomplete.ts`, `internal/trending/top_products.go`, etc.).
- A test directory using the language's idiomatic test framework, containing the minimal test file the scenario references AND any committed fixtures referenced by the scenario.
- The minimum project metadata files required for tests to run on a clean checkout (e.g. Python: `pyproject.toml` and/or `pytest.ini` and `requirements.txt`; Node/TS: `package.json` and `tsconfig.json`; Java/Maven: `pom.xml`; Go: `go.mod`). NO third-party DSA libraries.

**LET THE SCENARIO DECIDE THE FILE LAYOUT.** The exact filenames, language extensions, and folder structure MUST be derived from the scenario's wording (file paths it references, technology cues like "Mongoose model", "Spring service", "Express handler") rather than imposed from a fixed template. If the scenario references `src/cache/session_cache.py`, generate Python; if it references `src/cache/SessionCache.ts`, generate TypeScript; and so on.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code. The replacement primitive (Dijkstra / Trie / heap-of-k / DP table) MUST NOT already appear.
- DO NOT include `// TODO`, `// fix me`, `# hint:`, or any comments that point at the fix (use whichever comment syntax the language uses, but the rule applies regardless).
- DO NOT include the new tests the candidate is asked to add — only the pre-existing tests.
- DO NOT scaffold unrelated modules or features that inflate scope beyond the INTERMEDIATE time budget.

### Code Generation Instructions
Based on real-world scenarios, create a DSA task that:
- Draws inspiration from input scenarios for business context and the specific algorithmic problem
- Matches INTERMEDIATE proficiency level (3-5 years in the language the scenario implies + core DSA)
- Can be completed within {minutes_range} minutes — the candidate's edits should land in 1-2 modules + 1 test file
- Tests practical INTERMEDIATE DSA judgment: picking the right primitive, handling edge cases, writing tests that pin BOTH correctness and the new complexity contract
- Select a different real-world scenario each time to ensure variety in task generation
- Task name: short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than starting with `dsa-` (e.g., for the routing scenario: `swiftdrop-driver-shortest-path`; for the autocomplete scenario: `shopnest-product-trie-autocomplete`; for the trending scenario: `pulseboard-top-trending-heap`; for the refund scenario: `wanderpay-voucher-coinchange`)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "task-name-in-kebab-case",
   "question": "Structured task description. MUST include: (1) Current Implementation — the brute-force / wrong-complexity / buggy state the starter code implements, with realistic input sizes and observed latency / wrong output. (2) Required Changes — the specific primitive the candidate must introduce (Dijkstra / Trie / heap-of-k / DP), the target complexity, and the new tests they must add (correctness + edge cases + a performance test pinning the new bound). (3) Engineering decisions — any non-obvious trade-off the candidate must reason about (e.g. trie build cost vs query cost, heap-of-k vs full sort threshold, DP table size vs recursion).",
   "code_files": {{
      "README.md": "Candidate-facing README following structure below — required for every language",
      ".gitignore": "Standard exclusions for whichever language the scenario implies",
      "<actual-source-path-from-scenario>": "The brute-force / buggy implementation matching the Current Implementation, at the file path the scenario references, in the language it implies",
      "<actual-test-path-from-scenario>": "The existing minimal test file using the language's idiomatic test framework (pytest / jest / vitest / JUnit / go test / xUnit)",
      "<project-metadata-files>": "The minimum metadata required for the test command to run on a clean checkout — chosen from the language's ecosystem (e.g. pyproject.toml + requirements.txt; package.json + tsconfig.json; pom.xml; go.mod; etc.)",
      "<fixture-files-if-referenced>": "Any committed fixture the existing tests rely on (only if the scenario explicitly references one)"
   }},
   "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., shortest_path returns correct distances and path lists in O((V+E) log V), the autocomplete returns popularity-sorted top-k completions in O(prefix_len + k), the trending top-50 stays under 5ms on 200K events, the coin-change DP returns the optimal voucher count for regional denominations).",
   "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~20-30 words). Bullet 1: the business context and the existing brute-force / wrong-algorithm problem. Bullet 2: the specific algorithmic primitive the candidate must introduce and what engineering decision is involved. Bullet 3: the expected outcome including the complexity / latency target. Do NOT prefix bullets with bold mini-titles like '**Business context:**' — start each bullet directly with the content.",
   "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required for the language the scenario implies (e.g. Python 3.10+ + pip + pytest; or Node 18+ + npm + jest/vitest; or JDK 17+ + Maven/Gradle + JUnit; or Go 1.21+ with the built-in test runner). Always include Git and intermediate DSA knowledge (graph algorithms, tries, heaps, dynamic programming, big-O reasoning).",
   "answer": "High-level solution approach — the chosen primitive (e.g. Dijkstra / Trie / heap-of-k / bottom-up DP), the target complexity, and edge cases (same-node path / unreachable / empty prefix / regional denominations / window expiry). Use language-neutral terms (priority queue, FIFO queue, sorted structure with binary search) rather than language-specific stdlib symbols. Do not give the exact code.",
   "hints": "Single line guiding the candidate toward the right algorithmic insight (e.g. 'Think about which graph algorithm gives shortest paths under non-negative weights without exploring every path' or 'Look for a way to keep only the running top-k instead of re-sorting the full counts dict'). Must NOT name the algorithm by name.",
   "definitions": {{
     "terminology_1": "definition_1",
     "terminology_2": "definition_2"
   }}
}}

## README.md STRUCTURE (DSA Intermediate)
- The README.md contains the following sections:
  - Task Overview
  - Objectives
  - Helpful Tips
  - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content — no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview (MANDATORY - 3-4 substantial sentences)
**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the business scenario, the data sizes / latency budget, the observable bug or performance pain, and why the engineering judgment matters for this use case. NEVER generate empty content.


### Objectives
Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name the algorithm, name a language-specific stdlib symbol, or otherwise tell the candidate what code to write.

**Allowed phrasing — describes outcome, hides solution:**
- "shortest_path returns the correct total travel time and ordered node list on a known fixture; calling it with the same node as start and end returns zero cost and a single-node path."
- "Autocomplete returns the top 10 product names in popularity order for any prefix, and average lookup time is under 1ms on the committed fixture across 1000 calls."
- "The trending top-50 result is identical to a brute-force sort on the 5K-event fixture, AND the 200K-event randomized test completes in under 5ms per call."
- "The voucher count is optimal for `(14, [1, 7, 10])` and the function never blows the language runtime's call stack on large inputs."

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Use Dijkstra's algorithm with a priority queue." *(names the algorithm)*
- ❌ "Build a Trie at module load time and walk it on each query." *(names the data structure)*
- ❌ "Replace the full sort with a min-heap of size 50 via `heapq.heappushpop`." *(names the function and shape)*
- ❌ "Use a 1D bottom-up DP array indexed by amount." *(prescribes the DP shape)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behavior* the module must demonstrate, not the *code* it must contain.

Keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the function never raises on user input"). The remaining objectives must be specific to the scenario's primary algorithmic primitive and complexity target.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.

### Helpful Tips
- Project context and guidance suitable for intermediate-level developers (in the language the scenario implies) reasoning about algorithmic choice
- Engineering considerations framed as questions ("Which graph algorithm guarantees the shortest path under non-negative edge weights without exploring every path?", "Where should the prefix-completion list live so query time is independent of catalog size?", "What does the window-expiry pattern look like when events must be removed in the same pass that adds new ones?", "Why does greedy fail on `[1, 7, 10]` for `14`, and what changes when we tabulate from the bottom up?")
- Important considerations: edge cases (same-node, unreachable, empty prefix, three-way matches, expired events), big-O of the new approach, when to test correctness vs when to test performance
- 4-5 concise bullets MAX

### How to Verify
- Specific checkpoints after the fix: run the language's test command (e.g. `pytest`, `npm test`, `mvn test`, `go test ./...`), the existing tests still pass, the new correctness tests pass, the new performance test passes within the stated budget.
- Observable behaviors: the targeted edge cases (same-node, unreachable, empty prefix, three-way matches, regional denominations, window expiry) all behave correctly.
- Code-quality checks: standard library / built-in primitives only (no specialized DSA library pulled in), no runtime stack overflow on large inputs, public function signatures stable, complexity claims hold under the committed perf test.
- These points help the candidate verify their own work and the assessor to award points.

### NOT TO INCLUDE in README
- SETUP INSTRUCTIONS OR COMMANDS (any install or test command for any ecosystem — `pip install`, `pytest`, `npm install`, `npm test`, `mvn test`, `go test`, etc.)
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Direct solutions or hints
- Names of specific algorithms or stdlib symbols in any language (do not say "use Dijkstra" — say "find a graph algorithm that guarantees shortest paths under non-negative weights"; do not say "use a Trie" — say "find a structure that makes prefix lookup independent of catalog size")
- Snippets that would reveal the algorithm or data structure choice

## CRITICAL REMINDERS

1. **Starter project must be runnable** with the standard install + test commands of whichever language the scenario implies, with the brute-force / wrong-algorithm problem reproducible until the candidate applies the fix
2. **The starter MUST exhibit the described bug or performance issue.** Do NOT accidentally include the fix or a "good enough" partial solution. If the scenario says "recursive DFS times out at 5s", the starter must literally use a recursive DFS that times out on a graph of the stated size.
3. **NO comments** that reveal the solution or give hints
4. **Task must be completable within {minutes_range} minutes** with a hard cap at 40 minutes
5. **Focus on INTERMEDIATE DSA only** — graph (BFS/DFS/Dijkstra), trees/tries, heaps for top-k / scheduling, 1D-2D DP, sliding-window with FIFO queue + counts map. AVOID expert/research topics (Bellman-Ford, Floyd-Warshall, A*, max-flow, segment trees, bitmask DP, suffix automata, etc.).
6. **Language is decided by the scenario, not the prompt.** Use modern conventions for that language (Python 3.10+ / PEP 8, modern TypeScript/ESM, Java 17+, Go 1.21+, etc.) and built-in primitives / standard library only unless the scenario truly justifies a third-party dep
7. **Code files MUST NOT contain** the implementation for the core algorithmic fix the candidate must apply
8. **README.md MUST be fully populated** with meaningful, task-specific content, and Objectives must describe end-states without naming algorithms or stdlib symbols (see "Objectives" section above for FORBIDDEN phrasings — never say "use Dijkstra", "use a Trie", "use a min-heap of size k", "use bottom-up DP")
9. **.gitignore** must cover standard exclusions for whichever language the scenario implies (Python: `__pycache__/`, `.pytest_cache/`, `.venv/`; Node: `node_modules/`, `dist/`; Java: `target/`, `.gradle/`; Go: `bin/`, `vendor/`; etc.)
10. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than starting with `dsa-`
11. **Select a different real-world scenario** each time for variety
12. **The exact set of files in `code_files` is dictated by the scenario** — match the source/test paths the scenario references and add only the minimum project-metadata files needed for the test command to run on a fresh clone. Do NOT impose a Python-shaped layout on a non-Python scenario.
"""

PROMPT_REGISTRY = {
    "Data Structures and Algorithms (INTERMEDIATE)": [
        PROMPT_DSA_INTERMEDIATE_CONTEXT,
        PROMPT_DSA_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_DSA_INTERMEDIATE,
    ]
}
