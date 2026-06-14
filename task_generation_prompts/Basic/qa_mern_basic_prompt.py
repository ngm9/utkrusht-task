PROMPT_QA_MERN_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_QA_MERN_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a QA & Automation - MERN Stack assessment task.

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
- The task must reflect authentic QA work in a MERN codebase that a 1-2 yoe QA Automation Engineer would actually own — fixing a flaky integration test that leaks Mongo state between tests, replacing brittle CSS-class queries in a React Testing Library spec with user-facing queries plus async findBy*, mocking the network layer in a component test with MSW so it does not depend on a real Express server, fixing a Supertest spec where middleware ordering inside the test app does not match production, tightening loose assertions on an Express response shape, writing unit tests for a Mongoose helper or an Express middleware called directly with mock req/res, or covering both a React component and the Node-side helper it calls.
- BASIC QA-MERN tasks are LOCAL-ONLY — they run with `npm install && npm test` and nothing else. Do NOT generate Docker, docker-compose, run.sh, or kill.sh files. In-process replacements (mongodb-memory-server, MSW, in-process Supertest) cover every BASIC use case.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the existing test situation, and the specific QA-on-MERN problem the candidate will be solving)
2. What will the task look like? (Describe the type of test fix/refactor required, the expected deliverables, and how it aligns with the BASIC proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_QA_MERN_BASIC = """
# QA & Automation - MERN Stack Basic Task Requirements

## GOAL
As a technical architect super experienced in QA automation for MERN-stack (MongoDB, Express, React, Node.js) applications, you are given real-world scenarios and proficiency levels for QA work at the BASIC level. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess a 1-2 yoe candidate's ability to fix, refactor, or extend Jest-based tests for either:
- An Express backend service (using Supertest + Mongoose + an in-process MongoDB), OR
- A React frontend component (using React Testing Library + MSW for network mocking)

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to fix a flaky/broken test, refactor an existing test for correctness/isolation, or extend an existing test with one focused new assertion or new test case. Do NOT ask the candidate to build a Jest/RTL/Supertest project from scratch.
- The starter project MUST include a small, runnable application under test:
  - For backend scenarios: a tiny Express app + Mongoose models + the relevant route handlers, runnable via `npm test`
  - For frontend scenarios: a small React component (one or two `.tsx` files) renderable in a Jest + jsdom environment
  - The candidate should NOT have to stand up the application themselves
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are realistic and consistent with the chosen domain.
- Generate enough starter code that gives the candidate a working baseline: app/component files, a Jest config, at least one existing `*.test.ts` or `*.test.tsx` file that exhibits the problem described in the scenario, and a `package.json` listing every required dev dependency (`jest`, `ts-jest`, `@types/jest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `supertest`, `@types/supertest`, `mongoose`, `mongodb-memory-server`, `express`, `@types/express`, `msw` — only the ones the chosen scenario actually needs).
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The flaky/brittle/over-coupled behaviour described in the scenario MUST actually be present in the starter test.
- The task must surface real BASIC QA judgment — choosing user-facing queries over CSS classes, preferring async findBy*/waitFor over fixed sleeps, isolating Mongo state with per-test cleanup, mocking the network layer with MSW (or `jest.mock` on a module-level api client) so frontend tests do not depend on a live backend, exposing the Express app for in-process Supertest, etc.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years QA + MERN experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open-ended. The scenarios must focus on fundamental QA-on-MERN concepts like:
  - User-facing React Testing Library queries (`getByRole`, `getByLabelText`, `getByText`) over brittle CSS-class or DOM-structure queries
  - Distinguishing `getBy*`, `queryBy*`, and `findBy*` and using each one correctly
  - Replacing hard-coded `setTimeout`-style sleeps with `findBy*` / `waitFor`
  - Per-test cleanup of MongoDB collections in a `beforeEach` hook (with an in-process Mongo such as `mongodb-memory-server`)
  - HTTP-level integration tests with Supertest against an Express app that is exported separately from `app.listen`
  - Network mocking with MSW (global handlers + per-test overrides) or `jest.mock` on a module-level API client
  - Test isolation under parallel Jest execution (no `--runInBand` workaround)
  - Writing one focused assertion or a small set of related assertions per test
- Ensure all generated code uses Jest as the test runner, TypeScript (`*.test.ts` / `*.test.tsx`), and modern testing-library APIs. Do NOT use deprecated patterns in starter code that the candidate is expected to keep:
  - Do NOT use `enzyme` shallow rendering (use React Testing Library)
  - Do NOT use raw `fireEvent` where `userEvent` is the modern equivalent
  - Do NOT use `jest.runAllTimers` without a clear reason
  - Do NOT use `chai` / `mocha` / `expect.js` — Jest's built-in `expect` only
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years QA + MERN experience).

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- A `package.json` listing every required dependency (see the dependency-walk rule in CRITICAL REMINDERS) plus a `test` script (`"test": "jest"`).
- A `jest.config.ts` (or `.js`) with the right `testEnvironment` (`jsdom` for component tests, `node` for backend tests), `transform` for TypeScript via `ts-jest`, and `setupFilesAfterEnv` if the scenario needs one (e.g., for MSW lifecycle or `mongodb-memory-server` boot).
- A `tsconfig.json` compatible with `ts-jest`.
- The app under test:
  - For backend tasks: an Express app exposed via `module.exports = app` (or `export default app`) in a file like `src/app.ts`, separate from any `app.listen(...)` call (which lives in `src/server.ts` or similar and is NOT imported by tests). Mongoose models in `src/models/`. Route handlers in `src/routes/`.
  - For frontend tasks: one or two small React `.tsx` components in `src/`.
- One `*.test.ts` or `*.test.tsx` file containing the broken/flaky/wrongly-isolated behaviour the candidate must fix. It must run (i.e. compile and execute under `npm test`) but FAIL or be flaky in the way described.
- For scenarios involving MSW or `mongodb-memory-server`, the heavy boilerplate (MSW `setupServer` + `listen/resetHandlers/close` lifecycle, OR `MongoMemoryServer.create()` + `mongoose.connect/disconnect`) MUST be pre-wired in a Jest setup file (e.g., `jest.setup.ts`). The candidate's job is to add the missing per-test cleanup hook OR the missing handlers, NOT to wire up the entire test infrastructure from scratch (that would push the task past the BASIC time budget).
- A `.gitignore` covering `node_modules/`, `coverage/`, `dist/`, `build/`, `.env`.
- A `README.md` following the structure below.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code or in comments. The fix the candidate must apply MUST NOT already appear in the spec.
- DO NOT include `// TODO`, `// fix me`, `// hint:` or any other comments that point at the fix.
- DO NOT scaffold a fully passing test suite — at least one test in the target spec must fail or flake until the candidate applies the right fix.
- DO NOT include tests for unrelated features that would inflate scope beyond the BASIC time budget.
- DO NOT use Page Object Model abstractions, custom test runners, or fixture frameworks beyond what the scenario requires — keep the starter shape flat and obvious for a BASIC candidate.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official docs (Jest, React Testing Library, Supertest, MSW, Mongoose), and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific QA/test problem in a MERN codebase, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic QA proficiency while requiring genuine debugging and judgment that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a QA-MERN task that:
- Draws inspiration from input scenarios for business context and the specific test problem
- Matches BASIC proficiency level (1-2 years QA + MERN experience)
- Can be completed within {minutes_range} minutes — the candidate's edits should land in 1-2 files (typically the test file alone, occasionally the test file + a tiny addition to a Jest setup file)
- Tests practical QA-on-MERN skills: user-facing RTL queries, async findBy/waitFor, per-test Mongo cleanup, MSW handler definitions, Supertest integration assertions — NOT advanced patterns like custom Jest reporters, snapshot frameworks, contract testing, full POM, or visual regression
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- Task name: short, descriptive, under 50 characters, kebab-case, **incorporating the company/product name from the chosen scenario** rather than starting with `qa-mern-` (e.g., for the LMS enrollment-isolation scenario: `learnloop-enrollment-test-isolation`; for the React courselist scenario: `studyhub-courselist-rtl-async`; for the login-mocking scenario: `vaultid-login-msw-mocking`)

## SCENARIO-TYPE INFRASTRUCTURE CHECKLIST

Before generating any code, classify the chosen scenario into one of the types below and ensure EVERY listed prerequisite is present in the starter project. The starter must be fully bootable — running `npm install && npm test` on a clean machine must reach the actual test code and fail with the EXACT symptom the rubric is grading, not a setup error.

The four scenario types below tell you WHICH FILES to generate. Some scenarios touch the database (Type A1), some are pure Express + Node without DB (Type A2), some are React + jsdom (Type B), and some are pure Node unit tests with neither HTTP nor DB (Type C). **Generate ONLY the prerequisites listed for the type you pick — do not include Mongo lifecycle for a scenario that does not need Mongo, do not include MSW for a scenario that does not fetch, do not include Supertest for a scenario that never makes an HTTP call.**

### Type A1 — Backend API integration test WITH MongoDB (Supertest + Express + Mongoose + mongodb-memory-server)
Use this when the scenario is about: testing an Express route that reads/writes Mongoose models, DB-state isolation between tests, or DB-aware route behaviour. Indicators in the scenario text: words like "Mongoose", "model", "collection", "duplicate record", "DB state".

PRE-REQUISITES that MUST be present in the starter:
- `src/app.ts` (or equivalent) builds the Express app and exports it via `export default app`. All middleware (json, cookies, cors, auth) is registered here in the correct order.
- `src/server.ts` (or equivalent) does `app.listen(...)` for production use and is NOT imported by any test file.
- `src/models/*.ts` defines every Mongoose model the routes touch. Models are imported by `src/app.ts` (or its callers) so they get registered with the Mongoose connection.
- `src/routes/*.ts` (or inline in `src/app.ts`) implements the route handlers the test exercises.
- `jest.config.ts` has `testEnvironment: 'node'` and a `setupFilesAfterEnv` entry pointing at `jest.setup.ts`.
- `jest.setup.ts` (pre-wired):
  - `beforeAll`: `MongoMemoryServer.create()`, `mongoose.connect(<uri>)`
  - `afterAll`: `mongoose.disconnect()`, `mongod.stop()`
  - `jest.setTimeout(60_000)` at the top of the file (mongodb-memory-server downloads a binary on first run)
- The Mongoose connection is established BEFORE any test executes (so route handlers can write/read).
- `package.json` lists every dep used: `express`, `@types/express`, `mongoose`, `mongodb-memory-server`, `supertest`, `@types/supertest`, plus any middleware deps (`cookie-parser`, `cors`, etc.) actually `require`d in `src/`.

What the candidate's spec MUST be missing (the rubric):
- Whatever the scenario explicitly asks for — typically the per-test `beforeEach` cleanup hook, OR a payload assertion, OR a middleware-ordering fix.

### Type A2 — Backend API integration test WITHOUT MongoDB (Supertest + Express only)
Use this when the scenario is about: testing an Express route or middleware that does NOT touch a database — assertion tightness, response body shape, status codes, content negotiation, rate-limit behaviour, fake-timer-driven middleware, in-memory store route handlers. Indicators in the scenario text: explicit phrases like "no database in this scenario", "in-memory array", "rate-limit", "fake timers", "content negotiation", "validation error shape" — WITHOUT any mention of Mongoose or models.

PRE-REQUISITES that MUST be present in the starter:
- `src/app.ts` builds the Express app and exports it via `export default app`. Any in-process state (in-memory arrays, simple Maps) is owned by the route handler module and exposed through a small reset helper if the test needs to clear it.
- `src/server.ts` does `app.listen(...)` and is NOT imported by tests.
- `src/routes/*.ts` and/or `src/middleware/*.ts` for the units under test.
- `jest.config.ts` has `testEnvironment: 'node'` and a `setupFilesAfterEnv` entry pointing at `jest.setup.ts` ONLY IF the test needs setup (e.g., enabling `jest.useFakeTimers('modern')`). If no setup is needed, omit `jest.setup.ts` entirely.
- `package.json` lists `express`, `@types/express`, `supertest`, `@types/supertest`, plus any middleware deps actually used (e.g., `express-rate-limit`).
- DO NOT include `mongoose`, `mongodb-memory-server`, or any model file. Generating those for a non-Mongo scenario inflates install time and confuses the candidate.

What the candidate's spec MUST be missing (the rubric):
- The tightened assertion(s), the missing error-path / throttled-path / recovered-path test, OR the missing fake-timer setup.

### Type B — React component test (RTL + jsdom + network mocking)
Use this when the scenario is about: querying React components by user-facing role/text, async UI patterns, network-mocked component behaviour, loading/error/success states, or form interactions.

PRE-REQUISITES that MUST be present in the starter:
- `src/components/<Name>.tsx` (or equivalent) is a renderable React component. If the component needs Context providers (Router, Theme, QueryClient, an Auth provider), include a `renderWithProviders` helper in the test file or in `src/test/utils.tsx` — do NOT make the candidate wrap providers themselves.
- `jest.config.ts` has `testEnvironment: 'jsdom'` and a `setupFilesAfterEnv` entry pointing at `jest.setup.ts`.
- `jest.setup.ts` (pre-wired):
  - `import '@testing-library/jest-dom'` so the matchers are available
  - If the component fetches from the network: either MSW is wired up (`setupServer` + `server.listen/resetHandlers/close` lifecycle) OR `jest.mock` is set up against a module-level `src/api/client.ts`. Either way, `fetch` calls inside the component MUST resolve to SOMETHING during the test — never reach a real network.
- If MSW is the chosen mocking approach: `src/test/mswHandlers.ts` (or inline) holds the handlers array. Handlers may be empty (if the candidate must add them) or present (if the candidate must fix RTL queries instead).
- `package.json` lists every dep used: `react`, `react-dom`, `@types/react`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, plus `msw` if MSW is involved.
- DO NOT include `express`, `mongoose`, `mongodb-memory-server`, or `supertest` for a Type B scenario. The component test does not need a real backend or DB.

What the candidate's spec MUST be missing (the rubric):
- Whatever the scenario explicitly asks for — typically replacing CSS-class queries with role/label/text queries, OR replacing fixed sleeps with `findBy*`/`waitFor`, OR adding/overriding MSW handlers, OR adding a "spinner gone" assertion.

### Type B+N — React component PLUS a Node-side helper used by the component
Use this when the scenario tests BOTH a React component AND a pure Node-side utility/helper that the component imports (e.g., a date formatter, a number formatter, a small data-shaping function). Indicators: the scenario explicitly references a util file path and a component file path, and asks for tests at both levels.

PRE-REQUISITES that MUST be present in the starter:
- All Type B prerequisites above
- The Node-side helper file (`src/utils/<helper>.ts`) is implemented but has NO tests, OR has only a placeholder smoke test
- The helper has no Express/Mongo dependencies — it's pure functions
- A single `jest.config.ts` with `testEnvironment: 'jsdom'` is sufficient for both the component test and the helper unit test (Node-side functions are usable from jsdom). Do NOT use Jest projects unless the helper genuinely cannot run in jsdom.
- DO NOT include `express`, `mongoose`, `mongodb-memory-server`, or `supertest`.

What the candidate's spec MUST be missing (the rubric):
- The unit-test cases for the Node-side helper, AND the missing user-facing assertion in the component test.

### Type C — Pure Node / Jest unit test (no Express server, no Mongo, no React)
Use this when the scenario is about: testing a Node-side function in isolation — an Express middleware called directly with mock req/res/next, a utility helper, a data-access helper that uses Mongoose models WITHOUT spinning up an Express app. Indicators in the scenario text: phrases like "unit test", "called directly", "in isolation", "pure function", or a helper module that the test will import and invoke directly without HTTP.

PRE-REQUISITES that MUST be present in the starter:
- `jest.config.ts` has `testEnvironment: 'node'` and a `setupFilesAfterEnv` entry pointing at `jest.setup.ts` ONLY IF setup is needed (e.g., to bootstrap mongodb-memory-server for a Mongoose-helper unit test).
- `tsconfig.json` compatible with `ts-jest`.
- The unit under test exists in `src/`:
  - For middleware unit tests: `src/middleware/<name>.ts` exporting the middleware function
  - For Mongoose-helper unit tests: `src/helpers/<name>.ts` and `src/models/<name>.ts`
  - For pure utility unit tests: `src/utils/<name>.ts`
- If the unit-under-test uses Mongoose: `mongodb-memory-server` is pre-wired in `jest.setup.ts` exactly as in Type A1 (with `jest.setTimeout(60_000)`). The helper test still seeds and asserts directly via the model — NO Express app, NO Supertest.
- `package.json` lists ONLY the deps actually used by the unit under test:
  - For pure utility units: `jest`, `ts-jest`, `@types/jest`, `typescript`, `ts-node`. Nothing else.
  - For middleware units: above + (optionally) `express` and `@types/express` if the middleware signature uses Express types
  - For Mongoose-helper units: above + `mongoose`, `mongodb-memory-server`. Still NO `express`, `supertest`.
- DO NOT include `react`, `@testing-library/*`, `msw`, `supertest`, or `express` (unless the middleware specifically needs Express types) for a Type C scenario.

What the candidate's spec MUST be missing (the rubric):
- The actual assertion-bearing unit tests — the existing test asserts only weak smoke checks like `expect(next).toHaveBeenCalled()` without verifying the function's real effect.

### General rule (applies to all types)
Anything the rubric ASKS the candidate to ADD must be MISSING from the starter.
Anything the rubric does NOT ask must be PRE-WIRED in the starter.
The bug or gap must be the FIRST thing the candidate sees when they run `npm test`, not the LAST thing after they fix three setup errors first.

## DEPLOYMENT vs LOCAL EXECUTION (FILE-GENERATION RULES)

Every BASIC QA-MERN scenario in this prompt should be **runnable locally** with `npm install && npm test` and nothing else. The candidate should NOT need Docker, a running Mongo daemon, a deployed backend, a droplet, or any external service. In-process replacements (mongodb-memory-server for Mongo, MSW for HTTP, in-process Supertest for Express) cover every BASIC use case.

This means the file structure of a BASIC task is **lean**:

**For LOCAL-ONLY tasks (every scenario in this prompt):**
- Generate ONLY: `package.json`, `jest.config.ts`, `tsconfig.json`, `.gitignore`, `README.md`, optional `jest.setup.ts`, the `src/` files, and the test file(s)
- DO NOT generate: `Dockerfile`, `docker-compose.yml`, `compose.yaml`, `run.sh`, `kill.sh`, `.dockerignore`, any GitHub Actions / CI YAML, any deployment script
- The presence of any Docker / shell deployment file would cause the deployment pipeline to mark the task as `is_shared_infra_required = True`, kicking off a droplet workflow that this task does not actually need. That wastes infra and confuses the candidate.

**Decision rule for whether a scenario needs deployment:**
A scenario needs deployment files (Dockerfile + run.sh + kill.sh) ONLY IF the candidate's `npm test` cannot complete without a long-running external service that no in-process equivalent can replace. In practice for BASIC level, **this never happens** — every BASIC scenario above maps to either A1, A2, B, B+N, or C, and all five are local-only. If you find yourself wanting to add a Dockerfile, stop and re-classify the scenario; you have probably picked the wrong type.

**Concrete examples:**
- Scenario tests an Express route that writes to Mongo → Type A1, mongodb-memory-server in `jest.setup.ts`, NO Docker.
- Scenario tests an Express route + middleware with no DB → Type A2, no Mongo prereqs at all, NO Docker.
- Scenario tests a React component that fetches → Type B, MSW intercepts the fetch, NO Docker, NO real backend.
- Scenario tests a React component AND its date-format helper → Type B+N, single jsdom Jest config covers both, NO Docker.
- Scenario tests a Mongoose helper directly (no Express) → Type C, mongodb-memory-server only, NO Express app, NO Supertest, NO Docker.
- Scenario tests an Express middleware with mock req/res → Type C, no Express app, no HTTP, NO Docker.

## SELF-CHECK BEFORE FINALISING

Before producing the final JSON, mentally walk a candidate through their first `npm install && npm test` and answer each of these honestly. If any answer is no, the starter is incomplete — go back and add the missing infrastructure.

1. **Did you pick the right type?** Re-read the scenario. If it never mentions Mongo / models / collections, you should NOT be in Type A1. If it never mentions a React component, you should NOT be in Type B. If it asks for direct unit tests of a function (no HTTP, no rendering), you should be in Type C.
2. **Does `npm install` succeed?** Every `require(...)` and `import` in `src/`, `tests/`, `jest.config.ts`, `jest.setup.ts` traces back to a dep listed in `package.json`? AND conversely — is every `dependency` / `devDependency` actually used somewhere? (Don't list `mongoose` for a Type A2 / B / pure-utility C scenario.)
3. **Does Jest boot?** No "Cannot find module", no "transform error", no "testEnvironment not found"? `ts-jest` is wired up if any test or src file is `.ts`/`.tsx`? `ts-node` is in devDependencies if `jest.config.ts` is TypeScript?
4. **Does the test file actually load?** No top-level import error? No "Cannot use useNavigate outside a Router" thrown before the first `describe`? No "fetch is not defined" before the first assertion?
5. **For Type A1 / Type C with Mongoose:** Is the Mongoose connection established BEFORE the first test runs? Is the MongoMemoryServer URI passed to `mongoose.connect`? Is `jest.setTimeout(60_000)` set so the binary download does not time out on first run?
6. **For Type A2:** Have you actually OMITTED `mongoose` and `mongodb-memory-server`? The package.json should NOT list them. The `jest.setup.ts` should NOT import them. Adding them "just in case" inflates install time on a non-Mongo task.
7. **For Type B / B+N:** Are the testing-library matchers available (i.e., is `@testing-library/jest-dom` imported in `jest.setup.ts`)? If the component fetches anything, is that fetch intercepted (MSW handler or `jest.mock`)?
8. **For Type C:** Have you OMITTED `react`, `@testing-library/*`, `express`, `supertest`, `msw` (only kept the deps the unit-under-test actually imports)? The unit test calls the function directly — no HTTP layer, no jsdom rendering needed unless the unit itself touches the DOM.
9. **Are deployment files absent?** No `Dockerfile`, no `docker-compose.yml`, no `run.sh`, no `kill.sh`, no `.dockerignore`. BASIC QA-MERN tasks are local-only — adding any of these would flip `is_shared_infra_required` to True and break the assessment flow.
10. **Does the FIRST failing test fail for the EXACT reason the rubric grades?** Not a connection error, not a missing-handler error, not a missing-provider error, not an `EBINARYDOWNLOAD` from mongodb-memory-server — the actual scenario bug or gap.
11. **Is the failure message clear enough** that a candidate can map it to the README objectives without guessing?

If you answered all 11 yes, the starter is ready. If not, fix the gap before outputting JSON.

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what test needs to be fixed/refactored/extended and why?",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "node_modules/, coverage/, dist/, build/, .env",
    "package.json": "Includes ALL required deps + test script (see dependency-walk rule)",
    "jest.config.ts": "testEnvironment, transform, setupFilesAfterEnv if needed",
    "tsconfig.json": "Standard TypeScript config compatible with ts-jest",
    "jest.setup.ts": "ONLY if the scenario uses MSW or mongodb-memory-server — pre-wires the boilerplate lifecycle so the candidate does not have to",
    "<src/component or src/app paths>": "App-under-test files: React component(s) for frontend scenarios OR Express + Mongoose for backend scenarios",
    "<test file path>": "The existing test that exhibits the problem the candidate must fix"
  }},
  "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., the failing test now passes deterministically across N runs, no fixed sleeps remain, the spec uses user-facing RTL queries, Mongo collections are cleaned per test, MSW handlers are scoped correctly without leaking).",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words). Bullet 1: the business context and the existing test problem. Bullet 2: the specific QA change the candidate must make. Bullet 3: the expected outcome. Do NOT prefix bullets with bold mini-titles like '**Business context:**' or '**Expected outcome:**' — start each bullet directly with the content.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm, basic TypeScript / Jest / React Testing Library / Supertest / Mongoose knowledge as relevant to the chosen scenario.",
  "answer": "High-level solution approach — the query strategy, async wait pattern, cleanup hook, MSW handler shape, etc. — without giving the exact code.",
  "hints": "Single line suggesting focus area (e.g., 'Look at how the testing library prefers queries that match what the user actually sees on screen'). Must NOT name APIs by name and must NOT give away the fix.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (QA-MERN Basic)

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the current test situation. Describe what behaviour the test covers, who relies on it, and why the current state is unacceptable. NEVER generate empty content - always provide substantial business context.

### Objectives

Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name testing-library / Jest / Mongoose / MSW / Supertest APIs, name the broken code by selector or method, or otherwise tell the candidate what code to write. The candidate should read the objectives and know WHAT "done" looks like, but still have to figure out HOW.

**The FIRST bullet has a special job — it must orient the candidate WITHOUT hinting at the bug type or the fix.** It MUST contain exactly three things:
  1. The file path where the failing test lives (e.g., `__tests__/api/enrollments.int.test.ts`)
  2. A generic acknowledgement that running `npm test` on the unmodified starter produces failures in that file — DO NOT quote the exact error message, DO NOT name the failing assertion or matcher, DO NOT describe the bug category (no "duplicate key", no "iframe scoping", no "ECONNREFUSED", no "test isolation", no "race condition", no "missing mock"). The candidate should read the error themselves and figure out what kind of problem it is.
  3. The green outcome — typically "get the suite (or this test) to a state where every test passes whenever it runs". Avoid phrases that hint at the bug type, e.g., DO NOT say "regardless of execution order" (hints at parallelism), "without `--runInBand`" (hints at parallelism), "without any backend running" (hints at network mocking), "regardless of CSS rename" (hints at locator strategy).
This is the bare minimum orienting information — file + "tests fail" + "make them pass". Anything more than that risks giving the candidate the bug category, which short-circuits the diagnostic skill we are trying to assess.

The remaining bullets describe additional measurable end-states (clean Jest exit, no fixed sleeps, parallel safety, runtime budget, etc.) WITHOUT naming APIs and WITHOUT prescribing the fix. These bullets MAY imply the bug type indirectly via what they require (e.g., "each test starts from a clean DB state" implies isolation is the goal) — that is acceptable because they describe end-states, not solutions.

**Allowed phrasing — minimally orients candidate without leaking bug category:**
- (FIRST BULLET) "When you run `npm test` on the unmodified starter, some tests in `__tests__/api/enrollments.int.test.ts` fail. Get the suite to a state where every test in it passes whenever it runs."
- (FIRST BULLET) "Running `npm test` on the unmodified starter shows the test in `src/components/__tests__/CourseList.test.tsx` failing. Bring it back to green."
- (FIRST BULLET) "Running `npm test` on the unmodified starter produces failures in `src/auth/__tests__/LoginForm.test.tsx`. Get every test in the file passing."
- (FOLLOW-UP BULLET) "Each test in the suite must start from a clean database state, so no test's outcome depends on data created by a previous test."
- (FOLLOW-UP BULLET) "The Jest process must exit cleanly when the suite finishes — no open-handles or pending-async warnings."
- (FOLLOW-UP BULLET) "The spec must contain no hard-coded delays or arbitrary sleeps anywhere."
- (FOLLOW-UP BULLET) "A per-test mock override must not affect any other test in the suite."

**Forbidden in the FIRST bullet — these all leak the bug category:**
- ❌ "fails with `MongoServerError: E11000 duplicate key error`" *(reveals the bug is duplicate-key → state leakage)*
- ❌ "fails with `ECONNREFUSED` because the test calls a real backend" *(reveals the bug is unmocked network)*
- ❌ "fails because the form input is inside an iframe" *(reveals the bug is frame scoping)*
- ❌ "regardless of execution order" / "without `--runInBand`" *(reveals it's a parallelism/order bug)*
- ❌ "refactor the test so it..." *(prescribes editing the test specifically — could also be a setup file or component change)*

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Use `mongodb-memory-server` to spin up an in-process Mongo." *(names the library)*
- ❌ "Add a `beforeEach` that calls `mongoose.connection.collections[...].deleteMany({{}})`." *(prescribes exact code)*
- ❌ "Replace `container.querySelector` with `getByRole` and `findByText`." *(names both APIs)*
- ❌ "Set up MSW with `setupServer` and `server.listen / resetHandlers / close` and use `server.use(...)` for per-test overrides." *(names the entire API surface)*
- ❌ "Define a handler with `rest.post('/api/auth/login', (req, res, ctx) => res(ctx.status(200), ctx.json({{...}})))`." *(prescribes exact handler shape)*
- ❌ "Replace `setTimeout` with `findByText`." *(names both APIs)*
- ❌ "Replace `fireEvent.click` with `userEvent.click`." *(names both APIs)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behaviour* the test must demonstrate, not the *code* it must contain.

Keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the spec contains no hard-coded delays"). The remaining objectives must be specific to the scenario's primary skill.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.

### Helpful Tips

Practical guidance without revealing implementations:

- Project context and guidance points suitable for basic-level QA-on-MERN candidates
- General testing best practices: prefer user-facing queries, avoid hard sleeps, isolate test state, mock at the network layer
- Important considerations for the implementation, framed as questions ("Which testing-library query priority does the team's style guide recommend?", "What happens when two tests share the same Mongo collection between runs?", "How would you intercept a fetch call without spinning up a real backend server?", "What does `findBy*` give you that `getBy*` does not?")
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### How to Verify

Verification approaches after implementation:

- Specific checkpoints after the fix: run `npm test`, the previously-failing spec passes, repeat the run several times to confirm no flakes
- Observable behaviours: assertion targets are user-facing (role/label/text), spec contains no fixed sleeps, Mongo collections start each test empty, MSW handlers reset between tests, the Jest process exits cleanly
- Include both functional checks (tests pass) and code-quality checks (query quality, test isolation, no hard sleeps)
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (`npm install`, `npm test`, etc.)
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific testing-library / MSW / Mongoose / Supertest API names that point exactly at the fix (e.g., do not say "use `findByText`" — say "use the testing-library query that waits for an element to appear")
- Snippets that would reveal the query strategy, cleanup mechanism, or handler shape


## CRITICAL REMINDERS

1. **Starter project must be runnable** with `npm install && npm test` and the target test must reproducibly fail or flake until the candidate applies the right fix. NO Docker, NO docker-compose, NO run.sh, NO kill.sh — every BASIC QA-MERN scenario runs purely in-process (mongodb-memory-server for Mongo, MSW for HTTP, in-process Supertest for Express, direct function calls for unit tests).
2. **The starter test MUST FAIL — no trivially-true assertions.** A test that passes deterministically in the starter is a defect. Do NOT use weak checks like `expect(arr.length).toBeGreaterThanOrEqual(0)`, `expect(result).toBeDefined()`, or asserting only that "a response came back" without checking the body. The assertion must be tight enough that the bug described in the scenario produces a visible failure (e.g., if the scenario is "Mongo state leaks between tests", the failing test must produce an unambiguous mismatch like a 409 instead of an expected 201, not just "test was slow"). Exception: for pure refactoring scenarios where the test is "correct but brittle/coupled" (e.g., uses CSS-class queries that survive today but will break on rename), the README must explicitly state the engineering problem since the test will not fail today.
3. **Every `require` and `import` in the starter MUST be listed in `package.json` AND every dep listed must actually be used.** Before finalising `package.json`, walk through EVERY `require(...)` and `import` statement in `jest.config.ts`, `jest.setup.ts`, every `*.test.ts(x)` file, every component file, every route handler, every Mongoose model, every server file. Each non-built-in module name MUST appear in `dependencies` or `devDependencies`. Conversely, a dep listed in `package.json` MUST be imported by some file in `src/` or the test files — do not list `mongoose` for a Type A2 / B / pure-utility C task, do not list `react` for a Type A1 / A2 / Type C task, do not list `supertest` for a Type B / Type C task. Deps per type:
   - **Always**: `jest`, `ts-jest`, `@types/jest`, `typescript`, `ts-node` (REQUIRED when `jest.config.ts` is TypeScript — Jest uses ts-node internally to parse `.ts` config files; missing it produces `Cannot find package 'ts-node'` and Jest will not start)
   - **Type A1 (backend + Mongo)**: `express`, `@types/express`, `mongoose`, `mongodb-memory-server`, `supertest`, `@types/supertest`, plus `cookie-parser` / `body-parser` / `cors` if used
   - **Type A2 (backend, no Mongo)**: `express`, `@types/express`, `supertest`, `@types/supertest`, plus the actual middleware deps used (e.g., `express-rate-limit`). Do NOT include `mongoose` or `mongodb-memory-server`.
   - **Type B (React component)**: `react`, `react-dom`, `@types/react`, `@types/react-dom`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, plus `msw` if MSW is involved. Do NOT include `express`, `mongoose`, `supertest`.
   - **Type B+N (React + Node helper)**: same as Type B; the helper is a pure function so it adds no extra runtime deps.
   - **Type C (pure unit test)**: only the deps the unit-under-test actually imports. For a pure utility: nothing beyond the Always list. For a Mongoose helper: add `mongoose`, `mongodb-memory-server`. For an Express-typed middleware: add `express`, `@types/express`. Do NOT include `react`, `@testing-library/*`, `msw`, `supertest`.
   Do NOT import a module unless you list it. Do NOT list a module unless it is imported.
4. **For backend scenarios using Supertest, the Express app MUST be exported separately from `app.listen()`.** The starter file (e.g., `src/app.ts`) must do `export default app` (or `module.exports = app`), and any `app.listen(...)` must live in a separate file (e.g., `src/server.ts`) that is NOT imported by tests. Otherwise Supertest cannot load the app in-process and tests will hang or bind a real port.
5. **For scenarios using MSW, the `setupServer` lifecycle MUST be pre-wired** in a Jest setup file (`jest.setup.ts`) — `server.listen()` in `beforeAll`, `server.resetHandlers()` in `afterEach`, `server.close()` in `afterAll`. The handlers array can be empty OR contain only the broken/missing handler the candidate must fix. The candidate's job is to ADD or FIX handlers, NOT to wire up the entire MSW lifecycle from scratch (that's INTERMEDIATE-level work). Wire `jest.setup.ts` into Jest via `setupFilesAfterEnv: ['<rootDir>/jest.setup.ts']` in `jest.config.ts`.
6. **For scenarios using `mongodb-memory-server`, the in-process Mongo MUST be pre-wired** in a Jest setup file — `MongoMemoryServer.create()` and `mongoose.connect(...)` in `beforeAll`, `mongoose.disconnect()` and `mongod.stop()` in `afterAll`. The candidate's job is to ADD the missing per-test cleanup hook (`beforeEach` to wipe the relevant collections), NOT to bootstrap the entire in-process Mongo from scratch. The starter must demonstrate the LEAK problem; the candidate fixes the LEAK. **CRITICAL:** the `beforeAll` hook MUST be given an explicit timeout long enough to absorb the first-run mongod binary download (typically 60+ seconds) — either via `beforeAll(async () => {{...}}, 60_000)` or by calling `jest.setTimeout(60_000)` at the top of `jest.setup.ts`. Without this, the very first `npm test` run on a candidate's machine hangs and times out at the default 5-second hook limit while mongodb-memory-server downloads the ~150 MB binary, before any test code ever runs.
7. **NO comments** that reveal the solution or give hints
8. **Task must be completable within {minutes_range} minutes**
9. **Focus on fundamental QA-on-MERN concepts** appropriate for BASIC level (RTL user-facing queries, `findBy*`/`waitFor` for async, `beforeEach` for Mongo cleanup, MSW global vs per-test handlers, Supertest for HTTP integration). AVOID advanced patterns (custom Jest reporters, snapshot frameworks, contract testing, full POM, visual regression).
10. **Use TypeScript and modern testing libraries exclusively** — Jest as the runner, React Testing Library (NOT Enzyme), `userEvent` over raw `fireEvent` for user interactions, MSW for network mocking. No `enzyme`, no `chai`, no `mocha`, no `expect.js`.
11. **Keep the candidate's edit surface small** — ideally one test file, occasionally one test file plus a small addition to `jest.setup.ts` (e.g., adding a missing handler)
12. **README.md MUST be fully populated** with meaningful, task-specific content, and Objectives must describe end-states without naming testing-library / Jest / MSW / Mongoose / Supertest APIs (see "Objectives" section above for FORBIDDEN phrasings — e.g., never say "use `findByText`", "use `getByRole`", "use `setupServer`", "use `mongodb-memory-server`", "add a `beforeEach`")
13. **.gitignore** must cover `node_modules/`, `coverage/`, `dist/`, `build/`, `.env`
14. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than starting with `qa-mern-` or `mern-` (e.g., for an LMS enrollment-isolation scenario: `learnloop-enrollment-test-isolation`; for a React dashboard scenario: `studyhub-courselist-rtl-async`; for a login mocking scenario: `vaultid-login-msw-mocking`)
15. **Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
"""

PROMPT_REGISTRY = {
    "QA and Automation - MERN Stack (BASIC)": [
        PROMPT_QA_MERN_BASIC_CONTEXT,
        PROMPT_QA_MERN_BASIC_INPUT_AND_ASK,
        PROMPT_QA_MERN_BASIC,
    ]
}
