PROMPT_TDD_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_TDD_BEGINNER_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Test Driven Development assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}


CRITICAL TASK GENERATION REQUIREMENTS:
- The selected scenario describes ONE small class with ONE public method that is ALREADY IMPLEMENTED and works correctly in production today. The README lists the rules the method follows. NO tests exist yet — the candidate's only job is to add the missing test coverage.
- The candidate writes unit tests (typically 5-8 tests, one per distinct rule the spec describes). The tests run against the existing implementation and PASS.
- The task ships the SAME class — same class name, same method signature, same full correct implementation — in FIVE languages: Python, JavaScript, TypeScript, Java, C++. The candidate picks ONE language and works only inside that language's folder. The other four folders are ignored by that candidate.
- For each of the five languages, ship a self-contained folder with: (a) the class source file with the FULL CORRECT IMPLEMENTATION of the method (every rule from the spec is implemented faithfully — no stub, no placeholder), (b) an EMPTY test file (only imports / framework scaffolding + a placeholder comment — no test functions / cases), (c) the minimum project metadata so the language's test command runs.
- The PROBLEM STATEMENT (class name, method signature, behaviour rules) is identical across all five languages — only the syntax differs.
- The README is written for THIRD-YEAR COLLEGE STUDENTS — use simple English everywhere, especially in Objectives.
- Select a different inspiration scenario each time to ensure variety.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What class will the starter ship (class name, the single public method's name, its arguments, its return type)?
2. What are the distinct rules the method follows? List them in plain English; aim for 5-8 distinct cases that each represent a different rule worth testing.
3. How does the method's existing implementation handle each rule? (Brief — one phrase per rule.)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TDD_BEGINNER = """
# Test Driven Development Beginner Task Requirements

## GOAL
As a senior software engineer experienced in introductory unit testing, you are given a real-world inspiration scenario describing a small class with one public method that is ALREADY IMPLEMENTED and works correctly. The class has no tests yet. Generate a complete starter project where the candidate will:

1. Read the rule list in the README — this is the spec the existing method follows.
2. Pick ONE of the supported languages (Python, JavaScript, TypeScript, Java, or C++) and open that language's folder.
3. Write unit tests in that language — one per distinct rule (typically 5-8 tests).
4. Run that language's test command. Every test passes against the existing implementation.

This is a UNIT-TESTING task for an existing, correct implementation. The candidate does NOT write any production code — only tests. There is no stub to implement, no refactor to perform. The skill being assessed is identifying meaningful test cases from a rule list, structuring AAA tests, and using the test framework correctly.

## LANGUAGE SUPPORT (5 languages, all shipped)

The starter ships the SAME class — same class name, same method signature, same full correct implementation — in EACH of these 5 languages. Each language folder is self-contained; the candidate picks ONE and ignores the other four.

- **Python (3.10+)** — folder `python/`. Files: `python/<class_name>.py` (class with one fully implemented public method, snake_case method name, correct implementation following every rule), `python/test_<class_name>.py` (placeholder — `from <class_name> import <ClassName>` plus a single `# Write your unit tests below.` comment, NO `def test_...` functions), `python/pytest.ini` (minimal: `[pytest]` header and `testpaths = .`).
- **JavaScript (Node 18+)** — folder `javascript/`. Files: `javascript/<ClassName>.js` (CommonJS class with one fully implemented method, camelCase method name, `module.exports = <ClassName>;` at the bottom), `javascript/<ClassName>.test.js` (placeholder — `const <ClassName> = require('./<ClassName>');` plus a single `// Write your unit tests below.` comment, NO `test(...)` / `describe(...)` blocks), `javascript/package.json` (declares `jest` as a devDependency and a `"test": "jest"` script).
- **TypeScript (Node 18+, TS 5+)** — folder `typescript/`. Files: `typescript/<ClassName>.ts` (`export class <ClassName>` with one fully implemented method, camelCase method name, explicit parameter and return types), `typescript/<ClassName>.test.ts` (placeholder — `import {{ <ClassName> }} from './<ClassName>';` plus a single `// Write your unit tests below.` comment, NO `test(...)` / `describe(...)` blocks), `typescript/package.json` (declares `jest`, `ts-jest`, `@types/jest`, `typescript` as devDependencies, and `"test": "jest"` script with the `ts-jest` preset configured), `typescript/tsconfig.json` (target ES2022, module commonjs, strict mode on).
- **Java (17+)** — folder `java/`. Files: `java/src/main/java/<ClassName>.java` (public class with one fully implemented public method, camelCase method name, explicit parameter and return types), `java/src/test/java/<ClassName>Test.java` (placeholder — `import org.junit.jupiter.api.Test;` and `import static org.junit.jupiter.api.Assertions.*;` plus an empty `public class <ClassName>Test {{ }}` body containing only a single `// Write your unit tests below.` comment, NO `@Test` methods), `java/pom.xml` (Maven, JUnit Jupiter 5.10+, `maven-surefire-plugin`).
- **C++ (C++17)** — folder `cpp/`. Files: `cpp/<class_name>.h` (header with the class declaration), `cpp/<class_name>.cpp` (full correct implementation of the method), `cpp/test_<class_name>.cpp` (placeholder — `#include <cassert>` and `#include "<class_name>.h"` plus `int main() {{ /* Write your unit tests below. */ return 0; }}`), `cpp/Makefile` with a `test` target that compiles via `g++ -std=c++17 -Wall -o test_runner test_<class_name>.cpp <class_name>.cpp` and runs `./test_runner`.

Class name casing: same identity across languages (e.g. `LineItemCalculator`, `UsernameValidator`). Filename casing follows each language's convention (Python file: `line_item_calculator.py`; JS/TS/Java file: `LineItemCalculator.{{js,ts,java}}`; C++ file: `line_item_calculator.{{h,cpp}}`). Method name casing follows each language's convention (Python: `snake_case`; JS / TS / Java / C++: `camelCase`).

The PROBLEM STATEMENT (class name, method signature in plain English, behaviour rules) is identical across all five languages — only the syntax of the shipped source files differs.

## TARGET AUDIENCE / TONE
The README — Task Overview, Objectives, How to Verify, Helpful Tips — is written for THIRD-YEAR COLLEGE STUDENTS (roughly 20-21 years old, 1-2 years of programming exposure, often using English as a second language). Use SIMPLE English everywhere:

- Short sentences (aim for under 20 words each).
- Common, direct words. AVOID jargon like "characterisation", "observable behaviour", "establish a safety net", "pin the contract", "implementation detail", "translate", "render", "narrative".
- Say "write tests" not "characterise behaviour". Say "make sure the test fails" not "establish a failing baseline". Say "the method returns" not "the public contract emits".
- The candidate should be able to read each bullet once and know exactly what to do.

## BEGINNER TDD PROFICIENCY SCOPE (0-1 yoe — what the task assesses)
Tasks MUST exercise BEGINNER-level TDD skills:

- **Single small class with one public method**: one class, one public method, no extra public methods, no collaborators, no module state.
- **Rule-driven spec**: the README lists the behaviour as a numbered set of rules (length limits, cap behaviour, rounding, validation, etc.). The candidate translates each rule into one or more test cases.
- **Multiple distinct test cases**: typically 5-8 tests (happy path + several edge / boundary / validation cases). The candidate must DISCOVER which inputs prove which rule, not be handed them.
- **AAA structure**: each test is small (3-5 lines) following Arrange-Act-Assert.
- **Single assertion per test**: each test asserts ONE expected outcome.

Do NOT require: multiple classes, inheritance, dependency injection, test doubles / mocks / fakes, characterization tests, refactoring, multi-method classes, file I/O, network calls, async, exceptions beyond simple validation.

## INSTRUCTIONS

### Nature of the Task
- Starter ships the SAME class — fully implemented and correct — in EACH of the 5 supported languages.
- Test files in EACH language are EMPTY placeholders (imports / framework scaffolding only — NO test functions / methods / cases).
- The candidate picks ONE language and writes unit tests in that language's test file. They do NOT touch the source file.

### Starter Code Requirements

**For EACH of the 5 languages, the language's folder MUST contain:**
- A source file (path per LANGUAGE SUPPORT) with the class declaration and the FULL correct implementation of the method. Every rule from the spec must be implemented faithfully — input validation that raises errors, the cap behaviour, rounding, etc. The implementation must be idiomatic for that language but use only standard-library primitives.
- A test file (path per LANGUAGE SUPPORT) that compiles/parses cleanly but contains NO test cases. It contains only: (a) the imports needed to reference the class under test, (b) any framework-mandated scaffolding required for the file to be recognised by the test runner (e.g. an empty `public class <ClassName>Test {{ }}` body for Java, `int main() {{ return 0; }}` for C++), (c) a single placeholder comment in that language's comment syntax saying `Write your unit tests below.`
- The minimum project metadata files needed for that language's test command to run on a clean checkout (per LANGUAGE SUPPORT).

**MUST NOT contain in any language:**
- A stub or placeholder method body. The method must be fully implemented and correct.
- Any test cases / functions / methods in the test file. Only imports + scaffolding + the placeholder comment.
- Solution hints in any file (`// TODO`, `# fix me`, etc.).
- Third-party libraries beyond each language's standard testing framework. No mocking libraries.

**FUNCTIONAL REQUIREMENTS (each language independently):**
- The source file compiles / parses cleanly and the implementation is correct (a hand-written unit test would pass against it).
- The test command (`pytest` in `python/`, `npm test` in `javascript/` and `typescript/`, `mvn test` in `java/`, `make test` in `cpp/`) runs cleanly and reports "no tests collected" or the equivalent. It must NOT error.
- After the candidate adds their unit tests, the same test command runs them against the existing implementation and they PASS.

### Problem Statement Structure (for the `question` field)
The `question` field MUST describe in plain SIMPLE English:
1. The real-world context (1-2 short sentences from the scenario — the product / service / domain).
2. The class the candidate must implement: its name, the single public method's name, what it takes as input and what it returns. Plain English, no language-specific signatures — the candidate sees the actual typed signature when they open their chosen language's source file.
3. The desired behaviour written as a NUMBERED LIST OF RULES (length limits, cap behaviour, rounding, validation, etc.). Describe rules, not test cases — the candidate must work out which inputs prove which rule.
4. A short note that the starter ships the SAME class in 5 languages (Python, JavaScript, TypeScript, Java, C++) and the candidate picks ONE language to work in.
5. The workflow in simple words: write failing tests first, then write the method code, then check that every test passes.

NO code snippets in the `question` field. NO test stubs. NO implementation diff. Plain prose only.

### README.md STRUCTURE (TDD Beginner — 4 sections, in this order, SIMPLE ENGLISH throughout)
- Task Overview
- Objectives
- How to Verify
- Helpful Tips

### Task Overview (2 short paragraphs, simple English)
Paragraph 1 (2-3 short sentences) — the WHAT:
- (a) the real-world context (where this class would be used in plain words),
- (b) the class name + the method's name + what the method should do (refer to the numbered rules listed in the problem statement),
- (c) the fact that the method body is empty and no tests exist.

Paragraph 2 (1-2 sentences) — the LANGUAGE NOTE:
- State that the starter ships the SAME class in 5 languages — `python/`, `javascript/`, `typescript/`, `java/`, `cpp/` — and the candidate picks ONE to work in.

### Objectives (SIMPLE ENGLISH for a 3rd-year college student — EXACTLY 3 short bullets, NO sub-bullets)
Plain prose bullets — NO bold lead-ins (no `**...**`). NO sub-bullets listing test cases — the candidate must DISCOVER which behaviours to test by reading the source code themselves. Keep each sentence short (≤ 25 words).

Use this EXACT template, replacing `<ClassName>` with the actual class name from the scenario. Use ONLY the class name — NO `.methodName` suffix — because the source file is named after the class across every supported language (`<ClassName>.py`, `<ClassName>.java`, `<ClassName>.js`, `<ClassName>.ts`, `<class_name>.h`):

- Start by reading the `<ClassName>` code inside your chosen language folder.
- Identify every different way the method behaves for different inputs.
- Write one test for each behaviour you identify, all in the test file inside that same folder you choose.

DO NOT enumerate the specific behaviours / test cases as sub-bullets — the whole point is the candidate identifies them themselves by reading the code. DO NOT mention method names like `.apply` / `.isValid` / `.computeTotal` — refer to the class only. DO NOT include a bullet about implementing the method, running tests, making tests pass, or the RED/GREEN cycle — those do not belong in Objectives. DO NOT use words like: characterisation, observable behaviour, pin, contract, implementation detail, translate, render, narrative, faithful, scaffold, primitive, idiomatic. DO NOT prefix bullets with bold lead-ins.

### How to Verify (SIMPLE ENGLISH — 3 short bullets)
- Run the test command in your chosen language folder. Every test you wrote should pass against the existing implementation.
- Each test should check what the method RETURNS (or what error it raises) for a given input, not what the method does inside.
- Your test suite should cover every rule from the spec — at least one test per distinct rule.

### Helpful Tips (SIMPLE ENGLISH — 2-3 short bullets)
Plain bullets starting with "Look at", "Make sure", "Try", "Remember", or similar simple openers. Example shape:
- Look at each rule one by one. Each rule needs at least one test. Some rules (like a minimum and a maximum length) need more than one test.
- Make sure each test name tells the reader what the test is checking (e.g. `test_negative_price_is_rejected`).
- Each test should follow the AAA pattern: Arrange (set up the input), Act (call the method), Assert (check the result).

DO NOT name a specific standard-library helper or operator that gives away the method body.

### NOT TO INCLUDE in the README:
- Setup commands beyond the test command in How to Verify (no `pip install`, `npm install`, `mvn install` walkthrough).
- Step-by-step implementation pseudocode or solution code.
- A worked example test or a sample assertion.
- The exact formula, operator, or library symbol that gives away the implementation.
- Literal `input -> expected output` enumeration inside Objectives.
- Heavy vocabulary or long sentences — keep it simple.

### Code Generation Instructions
Generate a unit-testing task that:
- Ships ONE class with one fully-implemented public method, replicated in 5 language folders (Python, JavaScript, TypeScript, Java, C++).
- Has a plain-English rule set that exposes 5-8 distinct behaviours worth testing.
- Can be completed within {minutes_range} minutes by a BEGINNER-level candidate (0-1 yoe) — design the rule set so 20-30 minutes of genuine test-design work is needed.
- Task name: short, descriptive, under 50 characters, kebab-case, naming the class (e.g. `line-item-calculator`, `username-validator`).

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Plain-SIMPLE-English description following the Problem Statement Structure above.",
  "code_files": {{
    "README.md": "Candidate-facing README following the 4-section structure above — required. Written in SIMPLE English for 3rd-year college students.",
    ".gitignore": "Exclusions covering all 5 languages: Python (`__pycache__/`, `.pytest_cache/`, `*.pyc`), Node/TS (`node_modules/`, `dist/`, `*.log`), Java (`target/`, `*.class`), C++ (`*.o`, `*.out`, `test_runner`, `build/`).",
    "python/<class_name>.py": "Python class with one FULLY IMPLEMENTED public method. Snake_case method name. The body implements every rule from the spec correctly (validation, cap, rounding, etc.).",
    "python/test_<class_name>.py": "Placeholder test file. Just `from <class_name> import <ClassName>` and a single `# Write your unit tests below.` comment. NO `def test_...` functions.",
    "python/pytest.ini": "Minimal: `[pytest]` header and `testpaths = .`",
    "javascript/<ClassName>.js": "CommonJS class with one FULLY IMPLEMENTED method. CamelCase method name. The body implements every rule from the spec correctly. `module.exports = <ClassName>;` at the bottom.",
    "javascript/<ClassName>.test.js": "Placeholder. `const <ClassName> = require('./<ClassName>');` and a single `// Write your unit tests below.` comment. NO `test(...)` blocks.",
    "javascript/package.json": "Declares `jest` as a devDependency and `\\"test\\": \\"jest\\"` script.",
    "typescript/<ClassName>.ts": "`export class <ClassName>` with one FULLY IMPLEMENTED method. CamelCase method name. Explicit parameter and return types. The body implements every rule from the spec correctly.",
    "typescript/<ClassName>.test.ts": "Placeholder. `import {{ <ClassName> }} from './<ClassName>';` and a single `// Write your unit tests below.` comment. NO `test(...)` blocks.",
    "typescript/package.json": "Declares `jest`, `ts-jest`, `@types/jest`, `typescript` as devDependencies. `\\"test\\": \\"jest\\"` script. Jest config uses the `ts-jest` preset.",
    "typescript/tsconfig.json": "Target ES2022, module commonjs, strict true.",
    "java/src/main/java/<ClassName>.java": "Public class with one FULLY IMPLEMENTED public method. CamelCase method name. Explicit parameter and return types. The body implements every rule from the spec correctly.",
    "java/src/test/java/<ClassName>Test.java": "Placeholder. `import org.junit.jupiter.api.Test;` and `import static org.junit.jupiter.api.Assertions.*;`. Empty `public class <ClassName>Test {{ }}` body containing only `// Write your unit tests below.`. NO `@Test` methods.",
    "java/pom.xml": "Maven project. Declares JUnit Jupiter 5.10+ as a test dependency. `maven-surefire-plugin` configured for JUnit 5.",
    "cpp/<class_name>.h": "Header with the class declaration (method signatures only, no bodies).",
    "cpp/<class_name>.cpp": "Companion file with the FULL CORRECT IMPLEMENTATION of the method (every rule from the spec is implemented).",
    "cpp/test_<class_name>.cpp": "Placeholder. `#include <cassert>` and `#include \\"<class_name>.h\\"`. `int main() {{ /* Write your unit tests below. */ return 0; }}`. NO `assert(...)` calls.",
    "cpp/Makefile": "`test` target compiles `g++ -std=c++17 -Wall -o test_runner test_<class_name>.cpp <class_name>.cpp` and runs `./test_runner`."
  }},
  "outcomes": "Bullet-point list in SIMPLE English describing the expected results: (a) the candidate has picked one of the 5 language folders, (b) the test file in that folder has 5-8 tests, one per distinct rule from the spec, (c) every test passes against the existing implementation, (d) each test name describes what it is checking.",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words, simple English). Bullet 1: the real-world context and the class the candidate writes tests for (the class is already implemented). Bullet 2: the starter ships the same class in 5 languages — Python, JavaScript, TypeScript, Java, C++ — and the candidate picks one. Bullet 3: the candidate writes one test per distinct rule from the spec and runs them — every test should pass against the existing implementation. Do NOT prefix bullets with bold mini-titles.",
  "pre_requisites": "Bullet-point list of tools and knowledge required: one bullet for Git, one bullet that lists all 5 supported-language toolchains the candidate only needs ONE of (Python 3.10+ with pytest, OR Node 18+ with npm, OR JDK 17+ with Maven, OR g++ with C++17 + make), and one bullet for basic TDD knowledge (red-green-refactor cycle at a concept level, AAA test structure, single assertion per test).",
  "answer": "High-level solution approach in SIMPLE English: list the distinct test cases the candidate should write (one per rule from the spec). Briefly state that each test should follow the AAA pattern, use the test framework of the chosen language, and assert one expected outcome. Do NOT give exact code in any language.",
  "hints": "Single short line guiding the candidate (e.g. 'Write at least one test per rule from the spec' or 'Pick test names that describe what the test is checking'). Simple English, no jargon.",
  "definitions": {{
    "unit_test": "A small piece of code that calls one method with a chosen input and checks what the method returns (or what error it raises). Each test focuses on one behaviour.",
    "AAA_pattern": "A test structure: Arrange (set up the input), Act (call the method), Assert (check the result). Keeps tests easy to read."
  }}
}}

## CRITICAL REMINDERS

1. **The starter ships the SAME class in 5 languages: Python, JavaScript, TypeScript, Java, C++.** No more, no less. Each language folder is self-contained.
2. **The method body in every language is FULLY IMPLEMENTED and correct** — every rule from the spec is implemented faithfully. NO stubs, NO placeholders, NO `pass` / `return 0` / `return null` bodies.
3. **Test files in every language are EMPTY placeholders** (imports + framework scaffolding + a single placeholder comment, no test cases).
4. **README is written in SIMPLE English for 3rd-year college students.** Short sentences, common words, direct phrasing. No "characterisation", "observable behaviour", "pin the contract", "implementation detail", "translate", "render", "narrative", "faithful".
5. **The README has EXACTLY 4 sections** — Task Overview, Objectives, How to Verify, Helpful Tips.
6. **Objectives bullets are plain prose** — no `**bold**` lead-ins. Tells the candidate WHAT TESTS to write and WHERE to place them. NO bullet about implementing / writing code / running tests / RED-or-GREEN cycle.
7. **ONE small class with ONE public method only** — no extra classes, no helper functions, no module state, no side effects.
8. **No solution hints anywhere** — not in the source, not in the test file, not in the README, not in comments.
9. **Each language scaffold must run its test command cleanly** out of the box (with the candidate's tests pending). ZERO compile/import errors.
10. **Task completable within {minutes_range} minutes** by a BEGINNER-level candidate. Design the rule set so 20-30 minutes of genuine test-design work is needed.
11. **Select a different inspiration scenario each time** for variety. Always render the result as a UNIT-TESTING task for an existing correct implementation — never as a stub-and-implement task, never as a refactor task.
"""

PROMPT_REGISTRY = {
    "Test Driven Development (BEGINNER)": [
        PROMPT_TDD_BEGINNER_CONTEXT,
        PROMPT_TDD_BEGINNER_INPUT_AND_ASK,
        PROMPT_TDD_BEGINNER,
    ]
}
