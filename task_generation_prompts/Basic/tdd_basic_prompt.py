PROMPT_TDD_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_TDD_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Test Driven Development assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}


CRITICAL TASK GENERATION REQUIREMENTS:
- The selected scenario describes 2-3 small classes that ALREADY WORK CORRECTLY in production but have NO tests. The classes have multiple distinct paths through their public method(s) — branches, guards, fallbacks — that the candidate must cover with characterization tests.
- The candidate's job is to WRITE CHARACTERIZATION TESTS: 3-6 tests that pin the current observable behaviour of the public method(s). The candidate does NOT write any production code — no refactor, no implementation change. The skill being assessed is identifying every distinct path through the existing code and writing one test per path.
- The task ships the SAME classes — same class names, same method signatures, same full correct implementation — in FIVE languages: Python, JavaScript, TypeScript, Java, C++. The candidate picks ONE language and works only inside that language's folder. The other four folders are ignored by that candidate.
- For each of the five languages, ship a self-contained folder with: (a) the source files for the 2-3 classes from the scenario, with the FULL correct existing implementation, (b) an EMPTY test file (only imports / framework scaffolding + a placeholder comment — no test functions / cases), (c) the minimum project metadata so the language's test command runs.
- Match the scenario's class names, method signatures, and observable behaviour EXACTLY.
- The PROBLEM STATEMENT (class names, method signatures, behaviour) is identical across all five languages — only the syntax differs.
- The README is written for THIRD-YEAR COLLEGE STUDENTS — use simple English everywhere, especially in Objectives.
- Select a different inspiration scenario each time to ensure variety.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What classes will ship in each language folder? (Class names, public method signatures, observable behaviour.)
2. What are the distinct paths through the public method(s) the candidate must cover with characterization tests? (Each named branch, fallback, guard, and edge case.)
3. What are the 3-6 characterization tests the candidate should write? (Plain English — input -> expected observable output.)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TDD_BASIC = """
# Test Driven Development Basic Task Requirements

## GOAL
As a senior software engineer experienced in characterization testing, you are given a real-world inspiration scenario describing 2-3 small classes that already work correctly in production but have NO tests. The public method(s) have multiple distinct paths — branches, guards, fallbacks — that need test coverage. Generate a complete starter project where the candidate will:

1. Read the README — it explains the existing implementation and the distinct paths through it.
2. Pick ONE of the supported languages (Python, JavaScript, TypeScript, Java, or C++) and open that language's folder.
3. Write 3-6 characterization tests in that language that pin the current observable behaviour, with at least one test per distinct path.
4. Run that language's test command. Every test passes against the existing code.

This is a CHARACTERIZATION TESTING task for an existing, correct implementation. The candidate does NOT write any production code — no refactor, no implementation change. The skill being assessed is identifying every distinct path through complex multi-branch code and pinning each one with a test that depends only on the public contract.

## LANGUAGE SUPPORT (5 languages, all shipped)

The starter ships the SAME classes — same class names, same method signatures, same full correct existing implementation — in EACH of these 5 languages. Each language folder is self-contained; the candidate picks ONE and ignores the other four.

- **Python (3.10+)** — folder `python/`. Files: `python/<class_name>.py` for EACH class in the scenario (snake_case method names, full correct existing implementation), `python/test_<main_class_name>.py` (placeholder — `from <module> import <ClassName>` for the class(es) under test plus a single `# Write your characterization tests below.` comment, NO `def test_...` functions), `python/pytest.ini` (minimal: `[pytest]` header and `testpaths = .`).
- **JavaScript (Node 18+)** — folder `javascript/`. Files: `javascript/<ClassName>.js` for EACH class (CommonJS, camelCase method names, full correct existing implementation, `module.exports = <ClassName>;`), `javascript/<MainClassName>.test.js` (placeholder — `require(...)` for the class(es) under test plus a single `// Write your characterization tests below.` comment, NO `test(...)` / `describe(...)` blocks), `javascript/package.json` (declares `jest` as devDependency, `"test": "jest"` script).
- **TypeScript (Node 18+, TS 5+)** — folder `typescript/`. Files: `typescript/<ClassName>.ts` for EACH class (`export class`, camelCase methods, explicit parameter and return types, full correct existing implementation), `typescript/<MainClassName>.test.ts` (placeholder — `import {{ ... }} from './...';` plus a single `// Write your characterization tests below.` comment, NO `test(...)` blocks), `typescript/package.json` (declares `jest`, `ts-jest`, `@types/jest`, `typescript` as devDependencies, `"test": "jest"` script with `ts-jest` preset), `typescript/tsconfig.json` (target ES2022, module commonjs, strict true).
- **Java (17+)** — folder `java/`. Files: `java/src/main/java/<ClassName>.java` for EACH class (public class, camelCase methods, explicit types, full correct existing implementation), `java/src/test/java/<MainClassName>Test.java` (placeholder — `import org.junit.jupiter.api.Test;` and `import static org.junit.jupiter.api.Assertions.*;` plus an empty `public class <MainClassName>Test {{ }}` body containing only a single `// Write your characterization tests below.` comment, NO `@Test` methods), `java/pom.xml` (Maven, JUnit Jupiter 5.10+, `maven-surefire-plugin`).
- **C++ (C++17)** — folder `cpp/`. Files: `cpp/<class_name>.h` and `cpp/<class_name>.cpp` for EACH class (full correct existing implementation — header has declarations, .cpp has bodies), `cpp/test_<main_class_name>.cpp` (placeholder — `#include <cassert>` and `#include` lines for the class(es) under test plus `int main() {{ /* Write your characterization tests below. */ return 0; }}`), `cpp/Makefile` with a `test` target compiling via `g++ -std=c++17 -Wall -o test_runner test_<main_class_name>.cpp <class>.cpp ...` (list every `.cpp`) and running `./test_runner`.

Class name casing: same identity across languages (e.g. `OrderSummary`, `DiscountEngine`, `Cart`). Filename casing follows each language's convention (Python: `discount_engine.py`; JS / TS / Java: `DiscountEngine.{{js,ts,java}}`; C++: `discount_engine.{{h,cpp}}`). Method name casing follows each language's convention (Python: `snake_case`; JS / TS / Java / C++: `camelCase`).

The PROBLEM STATEMENT (class names, method behaviours, distinct paths to test) is identical across all five languages — only the syntax of the shipped source files differs.

## TARGET AUDIENCE / TONE
The README — Task Overview, Objectives, How to Verify, Helpful Tips — is written for THIRD-YEAR COLLEGE STUDENTS (roughly 20-21 years old, 1-2 years of programming exposure, often using English as a second language). Use SIMPLE English everywhere:

- Short sentences (aim for under 20 words each).
- Common, direct words. AVOID jargon like "characterisation discipline", "observable contract", "establish a safety net", "pin the public surface", "implementation detail", "translate", "render", "narrative", "faithful translation".
- Say "write tests" not "characterise behaviour". Say "make sure every test passes" not "establish that the public surface is invariant".
- The candidate should be able to read each bullet once and know exactly what to do.

## BASIC TDD PROFICIENCY SCOPE (1-2 yoe — what the task assesses)
Tasks MUST exercise BASIC-level characterization-testing skills:

- **Multiple distinct paths through one public method**: the method has 3-6 distinct paths a candidate must identify (named branches, fallback cases, guard clauses, edge cases). The candidate must spot each one from reading the code and pin it with a test.
- **Hand-rolled fakes only when needed**: if a scenario involves a collaborator object, candidates may need a simple hand-written fake (no mocking library) — but most scenarios will be self-contained classes that don't require this.
- **Public-contract-only tests**: tests must depend only on the public return value (or a clearly visible side effect on an injected collaborator) — NOT on internal helper methods, private fields, or call ordering.
- **AAA structure**: each test is small (3-5 lines) following Arrange-Act-Assert with a single primary assertion.

Do NOT require: design-pattern knowledge, dependency-injection containers / frameworks, async testing, performance testing, integration testing, multi-class hierarchy testing, tests that span more than 2 source files per language.

## INSTRUCTIONS

### Nature of the Task
- Starter ships the SAME 2-3 classes (FULL correct existing implementation) in EACH of the 5 supported languages.
- Test files in EACH language are EMPTY placeholders (imports / framework scaffolding only — NO test functions / methods / cases).
- The candidate picks ONE language and writes characterization tests in that language's test file. They do NOT touch the source files.

### Starter Code Requirements

**For EACH of the 5 languages, the language's folder MUST contain:**
- A source file per class in the scenario (paths per LANGUAGE SUPPORT). Each source file contains the FULL correct existing implementation. The implementation must be idiomatic for the chosen language but use only standard-library primitives. Every documented behaviour must be implemented correctly — a hand-written characterization test would pass against it.
- A test file (path per LANGUAGE SUPPORT) that compiles/parses cleanly but contains NO test cases. It contains only: (a) imports needed to reference the class(es) under test, (b) any framework-mandated scaffolding (e.g. an empty test class for Java, `int main() {{ return 0; }}` for C++), (c) a single placeholder comment in that language's comment syntax saying `Write your characterization tests below.`
- The minimum project metadata files needed for that language's test command to run on a clean checkout (per LANGUAGE SUPPORT).

**MUST NOT contain in any language:**
- Any test cases / functions / methods in the test file. Only imports + scaffolding + the placeholder comment.
- Any bug in the source code. The existing behaviour must be correct.
- Any solution hint in the source code (`# TODO`, `# fix me`, etc.).
- Any tests, mocks, or fakes shipped in test helpers. No shared test setup file / `conftest.py` / fixtures file.
- Third-party libraries beyond each language's standard testing framework. No mocking libraries — hand-rolled fakes only when a fake is needed.

**FUNCTIONAL REQUIREMENTS (each language independently):**
- The source files compile / parse cleanly and the implementation is correct.
- The test command (`pytest`, `npm test`, `mvn test`, `make test`) runs cleanly and reports "no tests collected" or the equivalent. It must NOT error.
- After the candidate adds their characterization tests, the same test command runs them against the existing code and they PASS.

### Problem Statement Structure (for the `question` field)
The `question` field MUST describe in plain SIMPLE English:
1. The real-world context (1-2 short sentences from the scenario — the product / service / domain).
2. The classes shipped and what each public method does (plain words, no language-specific signatures).
3. The distinct paths through the public method(s) the candidate must cover — listed as a numbered or bulleted set of plain-English statements (each named branch, each fallback, each guard, each edge case).
4. A short note that the starter ships the SAME classes in 5 languages (Python, JavaScript, TypeScript, Java, C++) and the candidate picks ONE language to work in.
5. The rule: the candidate writes tests against the existing implementation. They do NOT modify any source file.

NO code snippets in the `question` field. NO test stubs. Plain prose only.

### README.md STRUCTURE (TDD Basic — 4 sections, in this order, SIMPLE ENGLISH throughout)
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

### Task Overview (2 short paragraphs, simple English)
Paragraph 1 (2-3 short sentences) — the WHAT:
- (a) the real-world context (where these classes would be used in plain words),
- (b) the 2-3 classes and what their public methods do (the distinct paths through the method — e.g. "the `apply` method picks a discount rate based on the tier, but a small cart total skips the discount entirely"),
- (c) the fact that the existing code works correctly today and no tests exist yet — the candidate's only job is to add the missing test coverage.

Paragraph 2 (1-2 sentences) — the LANGUAGE NOTE:
- State that the starter ships the SAME classes in 5 languages — `python/`, `javascript/`, `typescript/`, `java/`, `cpp/` — and the candidate picks ONE to work in.

### Objectives (SIMPLE ENGLISH for a 3rd-year college student — EXACTLY 3 short bullets, NO sub-bullets)
Plain prose bullets — NO bold lead-ins (no `**...**`). NO sub-bullets listing test cases — the candidate must DISCOVER which behaviours to test by reading the source code themselves. Keep each sentence short (≤ 25 words).

Use this EXACT template, replacing `<ClassName>` with the actual main class name from the scenario. Use ONLY the class name — NO `.methodName` suffix — because the source file is named after the class across every supported language (`<ClassName>.py`, `<ClassName>.java`, `<ClassName>.js`, `<ClassName>.ts`, `<class_name>.h`):

- Start by reading the `<ClassName>` code inside your chosen language folder.
- Identify every different way the method behaves for different inputs.
- Write one test for each behaviour you identify, all in the test file inside that same folder you choose.

DO NOT enumerate the specific behaviours / test cases as sub-bullets — the whole point is the candidate identifies them themselves by reading the code. DO NOT mention method names like `.apply` / `.isValid` / `.formatReceipt` — refer to the class only. DO NOT include a bullet about changing or refactoring the source code, running tests, making tests pass, or the RED/GREEN cycle — those do not belong in Objectives. DO NOT use words like: characterisation, observable behaviour, pin, contract, implementation detail, translate, render, narrative, faithful, scaffold, primitive, idiomatic, dispatch, tabular. DO NOT prefix bullets with bold lead-ins.

### How to Verify (SIMPLE ENGLISH — 3 short bullets)
- Run the test command in your chosen language folder after writing your tests. Every test should pass against the existing implementation.
- Your test suite covers every distinct path through `<methodName>` — each branch, fallback, and guard has at least one test.
- Each test only checks what `<methodName>` returns for given inputs, not what happens inside the method.

### Helpful Tips (SIMPLE ENGLISH — 2-3 short bullets)
Plain bullets starting with "Look at", "Make sure", "Try", "Remember", or similar simple openers. Example shape:
- Look at every "if" and "else" branch in the existing code. Each branch is a different behaviour and should have its own test.
- Make sure each test name describes what the test is checking (e.g. `test_gold_tier_returns_cart_with_20_percent_off`).
- Each test should only check what the method RETURNS. Do not check anything about the inside of the method.

### NOT TO INCLUDE in the README:
- Setup commands beyond the test command in How to Verify (no `pip install`, `npm install`, `mvn install` walkthrough).
- Step-by-step instructions for changing the source code, pseudocode diffs, or solution code.
- Exact code solutions, test stubs, or sample assertions.
- Names of specific library symbols that point at the fix.
- Literal `input -> expected output` enumeration inside Objectives.
- Heavy vocabulary or long sentences — keep it simple.

### Code Generation Instructions
Generate a characterization-testing task that:
- Has 2-3 source files implementing one scenario's feature correctly, replicated in 5 language folders (Python, JavaScript, TypeScript, Java, C++).
- The implementation has multiple distinct paths (3-6 branches / fallbacks / guards / edge cases) that the candidate must cover with tests.
- Can be completed within {minutes_range} minutes by a BASIC-level candidate (1-2 yoe) — design the source code so 20-30 minutes of genuine test-design work is needed.
- Task name: short, descriptive, under 50 characters, kebab-case, naming the class or behaviour being tested (e.g. `discount-engine-tests`, `order-summary-tests`, `tier-discount-engine`).

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Plain-SIMPLE-English description following the Problem Statement Structure above.",
  "code_files": {{
    "README.md": "Candidate-facing README following the 4-section structure above — required. Written in SIMPLE English for 3rd-year college students.",
    ".gitignore": "Exclusions covering all 5 languages: Python (`__pycache__/`, `.pytest_cache/`, `*.pyc`), Node/TS (`node_modules/`, `dist/`, `*.log`), Java (`target/`, `*.class`), C++ (`*.o`, `*.out`, `test_runner`, `build/`).",
    "python/<class_name>.py": "ONE FILE PER CLASS in the scenario. Snake_case method names. Each file contains the FULL correct existing implementation. NO solution hints, NO bugs.",
    "python/test_<main_class_name>.py": "Placeholder. Imports for the class(es) under test plus a single `# Write your characterization tests below.` comment. NO `def test_...` functions.",
    "python/pytest.ini": "Minimal: `[pytest]` header and `testpaths = .`",
    "javascript/<ClassName>.js": "ONE FILE PER CLASS. CommonJS, camelCase method names, full correct existing implementation. `module.exports = <ClassName>;` at the bottom of each file.",
    "javascript/<MainClassName>.test.js": "Placeholder. `require(...)` for the class(es) under test plus a single `// Write your characterization tests below.` comment. NO `test(...)` blocks.",
    "javascript/package.json": "Declares `jest` as devDependency, `\\"test\\": \\"jest\\"` script.",
    "typescript/<ClassName>.ts": "ONE FILE PER CLASS. `export class`, camelCase methods, explicit parameter and return types, full correct existing implementation.",
    "typescript/<MainClassName>.test.ts": "Placeholder. `import {{ ... }} from './...';` for the class(es) under test plus a single `// Write your characterization tests below.` comment. NO `test(...)` blocks.",
    "typescript/package.json": "Declares `jest`, `ts-jest`, `@types/jest`, `typescript` as devDependencies. `\\"test\\": \\"jest\\"` script. Jest config uses the `ts-jest` preset.",
    "typescript/tsconfig.json": "Target ES2022, module commonjs, strict true.",
    "java/src/main/java/<ClassName>.java": "ONE FILE PER CLASS. Public class, camelCase methods, explicit types, full correct existing implementation.",
    "java/src/test/java/<MainClassName>Test.java": "Placeholder. `import org.junit.jupiter.api.Test;` and `import static org.junit.jupiter.api.Assertions.*;`. Empty `public class <MainClassName>Test {{ }}` body containing only `// Write your characterization tests below.`. NO `@Test` methods.",
    "java/pom.xml": "Maven project. Declares JUnit Jupiter 5.10+ as a test dependency. `maven-surefire-plugin` configured for JUnit 5.",
    "cpp/<class_name>.h": "ONE HEADER PER CLASS. Class declaration + full existing implementation (header-only when small, declaration-only when split with a .cpp).",
    "cpp/<class_name>.cpp": "Optional companion file when the class implementation is split out of the header. Include only when the class is not header-only.",
    "cpp/test_<main_class_name>.cpp": "Placeholder. `#include <cassert>` and `#include` lines for the class(es) under test. `int main() {{ /* Write your characterization tests below. */ return 0; }}`. NO `assert(...)` calls.",
    "cpp/Makefile": "`test` target compiles `g++ -std=c++17 -Wall -o test_runner test_<main_class_name>.cpp <every-non-header-only-.cpp>` and runs `./test_runner`."
  }},
  "outcomes": "Bullet-point list in SIMPLE English describing the expected results: (a) the candidate has picked one of the 5 language folders, (b) 3-6 characterization tests exist in that folder's test file (one per distinct path through the public method), (c) all tests pass against the existing code, (d) each test name describes what it is checking, (e) the source files were NOT modified.",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words, simple English). Bullet 1: the real-world context and the 2-3 classes. Bullet 2: the starter ships the same classes in 5 languages — Python, JavaScript, TypeScript, Java, C++ — and the candidate picks one. Bullet 3: the two-phase workflow — write tests first that pass against the current code, then change the code to fix the smell, and the same tests still pass. Do NOT prefix bullets with bold mini-titles.",
  "pre_requisites": "Bullet-point list of tools and knowledge required: one bullet for Git, one bullet that lists all 5 supported-language toolchains the candidate only needs ONE of (Python 3.10+ with pytest, OR Node 18+ with npm, OR JDK 17+ with Maven, OR g++ with C++17 + make), and one bullet for basic unit-testing knowledge (AAA test structure, characterization tests, behaviour-vs-implementation testing).",
  "answer": "High-level solution approach in SIMPLE English: list the characterization-test inputs the candidate should pick (one per distinct path through the method). Briefly state that tests must depend only on the public return value and follow the AAA pattern. Do NOT give exact code in any language.",
  "hints": "Single short line guiding the candidate (e.g. 'Write one test for each branch in the existing code' or 'Your tests should only check what the method returns'). Simple English, no jargon.",
  "definitions": {{
    "characterization_test": "A test that checks how the existing code already behaves. You write it BEFORE changing the code, so you can be sure your change does not break anything.",
    "observable_behaviour": "What you can see from outside the method — what it returns, what errors it raises. NOT what happens inside the method (which variables it uses, which helper methods it calls)."
  }}
}}

## CRITICAL REMINDERS

1. **The starter ships the SAME classes in 5 languages: Python, JavaScript, TypeScript, Java, C++.** No more, no less. Each language folder is self-contained.
2. **The source files in every language ship the FULL correct existing implementation.** The existing code MUST be correct — every documented behaviour works as the spec describes.
3. **Test files in every language are EMPTY placeholders** (imports + framework scaffolding + a single placeholder comment, no test cases).
4. **README is written in SIMPLE English for 3rd-year college students.** Short sentences, common words, direct phrasing. No "characterisation", "observable behaviour", "pin the contract", "implementation detail", "translate", "render", "narrative", "faithful", "dispatch", "tabular".
5. **The public method(s) have multiple distinct paths** — branches, fallbacks, guards, edge cases. The candidate must identify and test each one.
6. **The README has EXACTLY 4 sections** — Task Overview, Objectives, How to Verify, Helpful Tips.
7. **Objectives bullets are plain prose** — no `**bold**` lead-ins. Each bullet ≤ 25 words. Tells the candidate what to do, in simple words. NO "Pick a language" or "Translate the code" bullet content beyond a single direct instruction to open one of the language folders.
8. **No tests, no test stubs, no example assertions anywhere in the starter** — not in source files, not in test files, not in the README.
9. **Each language scaffold must run its test command cleanly** out of the box (with the candidate's tests pending). ZERO compile/import errors.
10. **Task completable within {minutes_range} minutes** by a BASIC-level candidate. Design the source code so 20-30 minutes of genuine characterization-test work is needed.
11. **Select a different inspiration scenario each time** for variety. Always render the result as a CHARACTERIZATION TESTING task for an existing correct implementation — never as a stub-and-implement task, never as a refactor task, never as a bug fix.
"""

PROMPT_REGISTRY = {
    "Test Driven Development (BASIC)": [
        PROMPT_TDD_BASIC_CONTEXT,
        PROMPT_TDD_BASIC_INPUT_AND_ASK,
        PROMPT_TDD_BASIC,
    ]
}
