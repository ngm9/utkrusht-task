PROMPT_PLAYWRIGHT_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PLAYWRIGHT_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Playwright assessment task.

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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic INTERMEDIATE Playwright work that a 3-5 yoe QA Automation Engineer would actually own — designing reusable fixtures with `storageState`, mocking multiple endpoints with `page.route` and asserting outgoing payloads, coordinating file upload + async job polling + download verification, refactoring brittle specs into small Page Objects, and replacing hard waits with deterministic synchronization.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the existing test situation, and the specific INTERMEDIATE Playwright problem the candidate will be solving)
2. What will the task look like? (Describe the type of test refactor / fix / extension required, the expected deliverables, and how it aligns with the INTERMEDIATE proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PLAYWRIGHT_INTERMEDIATE_INSTRUCTIONS = """
# Playwright Intermediate Task Requirements

## GOAL
As a technical architect super experienced in Playwright end-to-end testing, you are given real-world scenarios and proficiency levels for QA automation work at the INTERMEDIATE level. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess a 3-5 yoe candidate's ability to refactor, stabilize, and extend a non-trivial Playwright test against a small application under test, demonstrating deeper Playwright APIs and engineering judgment beyond the basics.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to refactor an existing spec for reuse/determinism, fix a flaky/over-coupled test, or extend an existing spec with one focused new capability (e.g., add a `storageState`-backed fixture, swap UI setup for `APIRequestContext`, add a coordinated `page.route` mock for multiple endpoints with payload assertions, or wire up a file upload + `expect.poll` + download verification flow). Do NOT ask the candidate to build a Playwright project from scratch.
- The starter project MUST include a small, runnable application under test (a single static HTML page served via a tiny script, OR a minimal Express/Node static server with a few API endpoints) that the candidate's spec runs against. The candidate should NOT have to stand up the application themselves.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are realistic and consistent with the chosen domain.
- Generate enough starter code that gives the candidate a working baseline: app files (HTML + tiny server with the relevant API routes), `playwright.config.ts`, at least one existing `*.spec.ts` file that exhibits the problem described in the scenario, a `package.json` with `@playwright/test` and any minimal app deps (e.g., `express`).
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The flaky/coupled/over-stubbed behavior described in the scenario MUST actually be present in the starter spec.
- The task must surface real INTERMEDIATE Playwright judgment — choosing where state belongs (test vs worker fixture, `storageState` vs per-test login), composing `page.route` handlers with conditional pass-through and selective fulfillment, asserting outgoing request payloads before fulfilling, replacing fixed sleeps with `expect.poll` / `waitForResponse` / `waitForEvent`, scoping interactions with `frameLocator` when needed, and keeping the spec parallel-safe under `--workers=N`.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Playwright / QA automation experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level of proficiency, the questions should test deeper Playwright understanding and require candidates to demonstrate:
  - **Fixtures & State Management**: Custom `test.extend` fixtures, `storageState` capture in a `setup` project, `playwright.config.ts` `dependencies` chaining, scoping (test vs worker fixtures)
  - **Network Layer Control**: `page.route` for multiple endpoints, conditional fulfillment per ID/path, selective pass-through, `request.postDataJSON()` payload assertions before fulfilling
  - **APIRequestContext**: Using the `request` fixture for test data seeding and verification alongside UI steps, sharing auth tokens between API and UI contexts
  - **Async Synchronization**: `expect.poll` for non-locator polling against an API or computed value, `waitForResponse` / `waitForRequest` with predicate functions, `waitForEvent('popup')` / `waitForEvent('download')`, `Promise.all` patterns for events triggered by clicks
  - **File I/O**: `setInputFiles` for uploads, `download.saveAs` + filesystem assertions for downloads, asserting downloaded file content (e.g., row counts in a CSV)
  - **Locator Discipline**: User-facing locators (`getByRole`, `getByLabel`, `getByText`), strict-mode-safe chained filters (`.filter`, `.nth`, `.locator`), avoiding `:nth-child`, `text=`, `>>` legacy syntax in code the candidate keeps
  - **Light POM Extraction**: Encapsulating a multi-step flow into a small `pages/<Feature>Page.ts` with a single public method per business action — NOT a full POM framework
  - **Parallelism Hygiene**: Tests must be safe under `--workers=N`, no shared mutable state across tests in the same file
- Tasks should require candidates to make engineering decisions (where does state live? which endpoint to mock vs let through? polling interval vs auto-wait?) and justify their approach.
- Ensure all generated code uses Playwright Test (`@playwright/test`), TypeScript (`*.spec.ts`), and modern Playwright APIs. Do NOT use the deprecated `page.$`, `page.$$`, raw `waitForSelector`, or `text=` shorthand in starter code that the candidate is expected to keep.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years Playwright experience). Hard cap at 30 minutes — if the scenario you are about to generate would take longer, narrow the scope (drop a bullet from "Your Task", or split off the POM extraction, or remove cross-browser coverage).

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official Playwright documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt Playwright APIs to solve a non-trivial test engineering problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate Playwright proficiency while requiring genuine engineering judgment that goes beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches (e.g., `expect.poll` vs `waitForResponse`, `storageState` vs per-test login, `request` fixture vs UI seeding) and choose the most appropriate one for the situation.

## Code Generation Instructions
Based on the real-world scenarios provided in following conversations, create a Playwright task that:
- Draws inspiration from the input_scenarios given to determine the business context and the specific test problem
- Matches the complexity level appropriate for INTERMEDIATE proficiency (3-5 years Playwright / QA automation experience), keeping in mind that AI assistance is allowed
- Tests practical Playwright skills: fixtures + `storageState`, multi-endpoint `page.route` mocking with payload assertions, `APIRequestContext` for setup/verification, `expect.poll` for async job polling, file upload + download verification, light POM extraction — NOT advanced patterns like custom selector engines, sharding strategies, monorepo orchestration, custom driver patches, visual regression frameworks, or full POM/Screenplay refactors
- Time constraints: Each task should be finishable within {minutes_range} minutes (hard cap 30 minutes)
- At every time pick a different real-world scenario from the list provided above to ensure variety in task generation
- Keep the candidate's edit surface focused — typically 1 spec file + 1 fixture/config file + (optionally) 1 small `pages/<Feature>Page.ts`. Do NOT spread the fix across the whole project.
- Task name: short, descriptive, under 50 characters, kebab-case, **incorporating the company/product name from the chosen scenario** rather than a generic `playwright-` prefix (e.g., for SaaS auth-state: `insightlab-cohort-export-auth-state`; for logistics route mocking: `swiftcargo-dispatch-mock-payload`; for EdTech upload+poll+download: `gradeup-bulk-grade-poll-download`)

## Starter Code Instructions
- The starter code should provide a foundation that allows the candidate to demonstrate INTERMEDIATE-level Playwright judgment
- The starter project must be runnable with `npm install && npx playwright install && npx playwright test` and the target spec must reproducibly fail or flake until the candidate applies the right fix
- Provide a realistic project structure (`tests/`, `pages/` if POM is involved, `fixtures/` if a custom fixture is involved, `app/` or `server.js` for the app under test, `playwright.config.ts` at the root)
- A part of the task completion is to watch the candidate make engineering decisions correctly — which fixture to use, where to mock vs let through, how to scope state — not just fix syntax errors
- If the task is to refactor for reuse/determinism, the starter spec must contain the inlined/duplicated/brittle pattern the candidate has to extract or replace
- If the task is to fix flake, the starter spec must actually flake reproducibly (e.g., backend endpoint that randomly returns 503, race between popup and assertion, hard wait that's too short for the slow path)
- Include partial scaffolding the candidate extends — e.g., an empty `fixtures/index.ts`, a `playwright/.auth/` directory in `.gitignore` but no setup script yet, a `pages/` folder with a stub `BasePage.ts` only — but do NOT include the actual fix
- Provide realistic dependencies in `package.json` (`@playwright/test`, optionally `express` for a tiny app server, `typescript` if not implicit)

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - package.json (Node.js dependencies including `@playwright/test` and any app deps the scenario needs)
  - .gitignore (Standard exclusions plus `node_modules/`, `test-results/`, `playwright-report/`, `playwright/.cache/`, `playwright/.auth/`)
  - playwright.config.ts (testDir, baseURL, browser project(s), `webServer` block if a server is used, `dependencies` chain if a setup project is involved)
  - Spec file(s) under `tests/` containing the broken/coupled/flaky behavior the candidate must address
  - App-under-test files: HTML pages and/or a small Express server with the relevant API routes
  - Stub files the candidate extends (e.g., empty `fixtures/index.ts`, stub `pages/BasePage.ts`) where appropriate

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "task-name-in-kebab-case",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what existing test/spec needs to be refactored/fixed/extended and why? Include the engineering decisions the candidate must make.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "node_modules/, test-results/, playwright-report/, playwright/.cache/, playwright/.auth/, .env, etc.",
      "package.json": "@playwright/test + any app deps (express, etc.) + scripts (test, server)",
      "playwright.config.ts": "testDir, baseURL, browser project(s), webServer block, dependencies chain if needed",
      "tests/<feature>.spec.ts": "The existing spec that exhibits the problem the candidate must address",
      "app/<file>.html": "HTML pages that reproduce the UI under test (if no server)",
      "server.js": "Tiny Express server with the API routes the scenario depends on (if needed)",
      "fixtures/index.ts": "Stub or partial fixture file the candidate extends (if scenario involves custom fixtures)",
      "pages/<Feature>Page.ts": "Stub POM file the candidate extends (if scenario involves POM)",
      "auth.setup.ts": "Empty or commented stub if storageState scenario, otherwise omit",
      "starter_code_file_name": "starter_code_file_content"
   }},
   "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., the failing test now passes deterministically across N runs, no `waitForTimeout` calls remain, the spec uses a custom fixture for auth, payload assertions confirm the UI sends the correct data, downloaded file content is verified).",
   "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~20-30 words). Bullet 1: the business context and the existing test problem. Bullet 2: the specific Playwright change the candidate must make and what engineering decision is involved. Bullet 3: the expected outcome. Do NOT prefix bullets with bold mini-titles like '**Business context:**' or '**Engineering decision:**' — start each bullet directly with the content.",
   "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm, `npx playwright install` to fetch browsers, Git, intermediate TypeScript/Playwright knowledge (fixtures, route mocking, APIRequestContext, expect.poll, downloads).",
   "answer": "High-level solution approach — which fixture to add, what `storageState` flow to wire, what mocking strategy, what polling/wait mechanism — without giving the exact code.",
   "hints": "Single line guiding the candidate toward the engineering decision (e.g., 'Think about which Playwright primitive lets you wait on a non-locator value with retries'). Must NOT name the API by name.",
   "definitions": {{
     "terminology_1": "definition_1",
     "terminology_2": "definition_2"
   }}
}}

## Code file requirements
- Generate a realistic project structure (`tests/`, `pages/`, `fixtures/`, `app/` or `server.js`, `playwright.config.ts`, `package.json`)
- Code should follow modern Playwright best practices and demonstrate intermediate-level patterns
- Use TypeScript and `@playwright/test` exclusively — no plain `playwright` library, no JS specs
- Focus on modern Playwright APIs (locators, web-first assertions, `route`, `request`, `expect.poll`, `download`, `setInputFiles`)
- **CRITICAL**: The generated code files should provide partial implementations that require the candidate's engineering completion. The core decisions (fixture shape, mock strategy, polling mechanism, payload assertion) MUST be left for the candidate.
- Include some existing code (the broken spec, stub fixture, stub POM) that needs to be extended or replaced
- DO NOT include any 'TODO', 'fix me', or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add fixture here" or "Should mock this endpoint" etc.
- The generated project should compile and run, but the target spec must reproducibly fail/flake until the candidate applies the right fix
- Provide realistic dependencies in `package.json` that intermediate Playwright users should be familiar with

## .gitignore INSTRUCTIONS
Create a comprehensive gitignore file covering: `node_modules/`, `test-results/`, `playwright-report/`, `playwright/.cache/`, `playwright/.auth/`, `*.log`, `.env`, `.env.local`, `dist/`, `build/`, IDE configurations (`.vscode/`, `.idea/`), and OS files (`.DS_Store`, `Thumbs.db`).

## README.md INSTRUCTIONS
- The README.md contains the following sections:
  - Task Overview
  - Helpful Tips
  - Objectives
  - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- Do not give away any specific Playwright APIs, fixture shapes, or mocking strategies that would hint at the solution

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, the current test situation, and why the engineering judgment matters for this use case.
NEVER generate empty content - always provide substantial business context that explains what feature the test covers, who relies on it, and why the current state is unacceptable.

### Helpful Tips
- Project context and guidance points suitable for intermediate-level Playwright users
- Engineering considerations framed as questions ("Where should auth state live so each worker doesn't redo the login?", "Which Playwright primitive lets you wait on a value computed by your test code, with retries?", "How do you assert what a click sent to the backend, before the response is returned?")
- Important considerations for the implementation focusing on:
  - Fixture scope and reuse (test vs worker, `storageState` lifecycle)
  - Network mocking strategy (which endpoints to mock vs let through, conditional fulfillment, payload assertions)
  - Synchronization choice (`expect.poll` vs `waitForResponse` vs auto-waiting assertion)
  - File I/O patterns (`setInputFiles`, `download.saveAs`, content verification)
  - Locator discipline (user-facing, strict-mode-safe, chained filters)
  - Parallelism safety (no shared mutable state across tests)
- Quality expectations for intermediate-level work (deterministic, parallel-safe, no hard sleeps)

### Objectives

Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name Playwright APIs, name the broken code by symbol/method, or otherwise tell the candidate what code to write. The candidate should read the objectives and know WHAT "done" looks like, but still have to figure out HOW.

**Allowed phrasing — describes outcome, hides solution:**
- "Authentication happens once at the start of the run and is reused by every test, with zero UI login calls inside any spec."
- "All 8 tests pass under `npx playwright test --workers=4` with no session-conflict failures, and the full run finishes in under 90 seconds."
- "The driver-assignment test runs deterministically without contacting the staging backend, and verifies that the request the UI sent matches the user's selection before the backend is allowed to respond."
- "The grading-job spec finishes in 6–10 seconds proportional to actual job duration, and verifies the downloaded report's filename and row count."
- "The spec is parallel-safe — no shared mutable state across tests in the file."

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Auth happens once via the setup project, never per-test." *(names the setup-project mechanism)*
- ❌ "Use `storageState` to capture the authenticated context once and replay it." *(names the API)*
- ❌ "Outgoing request payload is asserted before the response is fulfilled." *(prescribes route+payload-assert pattern)*
- ❌ "Use `page.route` to stub the assign endpoint and `request.postDataJSON()` to inspect the body." *(names two APIs)*
- ❌ "Use `expect.poll` against `GET /api/grade-jobs/:id` until status is done." *(names the API and the endpoint)*
- ❌ "Replace `waitForTimeout(15000)` with a polling primitive on the job-status endpoint." *(names the line to delete and prescribes the fix)*
- ❌ "Add a `setup` project to `playwright.config.ts` with `dependencies` chained from the dashboards project." *(prescribes config shape)*
- ❌ "Create a `fixtures/index.ts` exporting an `authedPage` fixture via `test.extend`." *(prescribes file path and fixture shape)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behavior* the test/suite must demonstrate, not the *code* it must contain.

Keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the spec contains no hard-coded delays"). The remaining objectives must be specific to the scenario's primary engineering decision.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.

### How to Verify
- Specific checkpoints after the fix: run `npx playwright test`, the previously-failing/flaky spec passes consistently, repeat the run several times to confirm no flakes
- Observable behaviors: assertion targets are user-facing (role/label/text), spec contains no `waitForTimeout`, mocked endpoints are coordinated, downloaded file content is verified, etc.
- Code-quality checkpoints (fixture shape, mock placement, polling discipline, no shared state)
- These points help the candidate verify their own work and the assessor to award points
- Include both functional checks (tests pass under `--workers=N`) and engineering-quality checks

### NOT TO INCLUDE in README
- SETUP INSTRUCTIONS OR COMMANDS (`npm install`, `npx playwright install`, `npx playwright test`, etc.)
- Direct solutions or specific fixture/mock/polling implementations
- Step-by-step implementation guides
- Specific Playwright API names that point exactly at the fix (e.g., do NOT say "use `storageState`" — say "find a way to capture the authenticated browser state once and replay it"; do NOT say "use `expect.poll`" — say "find the Playwright primitive that polls a value with retries")
- Code snippets that would reveal fixture shape, mock strategy, polling mechanism, or payload assertion
- Specific files or folder structure that would dictate the engineering approach

## CRITICAL REMINDERS

1. **Starter project must be runnable** with `npm install && npx playwright install && npx playwright test` and the target spec must reproducibly fail or flake until the candidate applies the right fix
2. **The starter test MUST FAIL or FLAKE — no trivially-true assertions.** A test that passes deterministically in the starter is a defect. Do NOT use weak checks like `expect(count).toBeGreaterThanOrEqual(0)`, `expect(arr).toBeDefined()`, or asserting only that "a download happened" without checking its contents. The assertion must be tight enough that the engineering problem described in the scenario produces a visible failure or measurable flake (e.g., "404 in 2 of 5 runs", "wrong payload sent", "wrong file content downloaded"). Exception: for pure refactoring scenarios (e.g., extracting a fixture from inlined login code) where the test is "correct but slow/duplicated", the README must explicitly state the engineering problem since the test won't fail.
3. **`webServer.url` MUST point at a route that returns HTTP 200**, otherwise Playwright's readiness probe times out and tests never start. Take the value of `webServer.url`, identify the path component (the bit after `localhost:PORT`), and confirm `server.js` has a route handler that matches that path AND returns HTTP 200. If `webServer.url` ends with `/`, you MUST either include `app.use(express.static(...))` in `server.js` OR add `app.get('/', (req, res) => res.send('ok'))`. If `webServer.url` is a deeper path (e.g., `/dispatch/board`), `server.js` MUST register that exact route. Generation is invalid otherwise.
4. **`webServer.reuseExistingServer` MUST be `false`** — never `true`, never `!process.env.CI`. A candidate machine with anything on the chosen port will silently bind to the wrong server and produce nonsense test output.
5. **Pick a port that does NOT clash with common dev tooling.** Allowed: `3456`, `4321`, `5173`, `7890`, `8123`. Forbidden: `3000` (Next.js/CRA), `8080`, `8000`, `5000` (macOS AirPlay), `4000` (Phoenix), `5432` (Postgres), `6379` (Redis), `27017` (Mongo). Use the same port consistently in `server.js`, `playwright.config.ts` `baseURL`, and `webServer.url`.
6. **NO comments** that reveal the solution or give hints
7. **Task must be completable within {minutes_range} minutes** with a hard cap at 30 minutes
8. **Focus on INTERMEDIATE-only Playwright concepts** appropriate for 3-5 yoe — fixtures + `storageState`, multi-endpoint `page.route` + payload assertions, `APIRequestContext` for setup/verification, `expect.poll`, file upload + download verification, light POM. AVOID advanced patterns (custom selector engines, sharding strategies, monorepo orchestration, full POM/Screenplay frameworks, visual regression).
9. **Use TypeScript and `@playwright/test` exclusively** — no `playwright` standalone, no JS specs
10. **Keep the candidate's edit surface focused** — ideally 1 spec file + 1 fixture/config file + optionally 1 stub POM file
11. **README.md MUST be fully populated** with meaningful, task-specific content, and Objectives must describe end-states without naming Playwright APIs (see "Objectives" section above for FORBIDDEN phrasings — e.g., never say "use `storageState`", "use `expect.poll`", "use `page.route`", "add a setup project")
12. **.gitignore** must cover `node_modules/`, `test-results/`, `playwright-report/`, `playwright/.cache/`, `playwright/.auth/`
13. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than starting with `playwright-` (e.g., for the SaaS analytics auth scenario: `insightlab-cohort-export-auth-state`; for the logistics dispatch scenario: `swiftcargo-dispatch-mock-payload`; for the EdTech grading scenario: `gradeup-bulk-grade-poll-download`)
14. **Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
"""

PROMPT_REGISTRY = {
    "Playwright (INTERMEDIATE)": [
        PROMPT_PLAYWRIGHT_INTERMEDIATE_CONTEXT,
        PROMPT_PLAYWRIGHT_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_PLAYWRIGHT_INTERMEDIATE_INSTRUCTIONS,
    ]
}
