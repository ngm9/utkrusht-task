PROMPT_PLAYWRIGHT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PLAYWRIGHT_BASIC_INPUT_AND_ASK = """
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
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic Playwright work that a QA Automation Engineer would actually own — fixing a flaky test, refactoring for isolation, scoping a locator inside a frame, replacing a hard sleep with a proper wait, mocking a network call with `page.route`, etc.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the existing test situation, and the specific Playwright problem the candidate will be solving)
2. What will the task look like? (Describe the type of test fix/extension required, the expected deliverables, and how it aligns with the BASIC proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PLAYWRIGHT_BASIC = """
# Playwright Basic Task Requirements

## GOAL
As a technical architect super experienced in Playwright end-to-end testing, you are given real-world scenarios and proficiency levels for QA automation work. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess a candidate's ability to write, debug, refactor, and stabilize Playwright tests against a small application under test.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to fix a flaky/broken Playwright test, refactor an existing spec for correctness/isolation, or extend an existing spec with one focused new assertion. Do NOT ask the candidate to build a Playwright project from scratch.
- The starter project MUST include a small, runnable application under test (a single static HTML page served via a tiny script, OR a minimal Express/Node static server, OR an HTML file Playwright opens directly via `file://` or `page.setContent(...)`). The candidate should NOT have to stand up the application themselves.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are realistic and consistent with the chosen domain.
- Generate enough starter code that gives the candidate a working baseline: app files, `playwright.config.ts`, at least one existing `*.spec.ts` file that exhibits the problem described in the scenario, and a `package.json` with `@playwright/test` as a dev dependency.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE. The broken/flaky behavior described in the scenario MUST actually be present in the starter spec.
- The task must surface real Playwright judgment — choosing user-facing locators (`getByRole`, `getByLabel`, `getByText`), preferring web-first assertions (`expect(locator).toHaveText(...)`) over manual polling, scoping to a `frameLocator` for iframes, using `request` fixture for API setup, using `page.route` for network mocking, and using `beforeEach` for test isolation.
- The question must NOT include hints. The hints will be provided in the "hints" field.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Playwright/QA automation experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must focus on fundamental Playwright concepts like:
  - Choosing resilient, user-facing locators over brittle CSS/XPath selectors
  - Replacing `waitForTimeout` / hard sleeps with web-first assertions or `waitForResponse`
  - Working with iframes via `frameLocator`
  - Using `beforeEach` (NOT `beforeAll`) for test isolation and clean state
  - Using the built-in `request` fixture for API-driven test setup
  - Using `page.route` to mock a single API response for deterministic tests
  - Writing one focused assertion or a small number of related assertions
- Ensure all generated code uses Playwright Test (`@playwright/test`), TypeScript (`*.spec.ts`), and modern Playwright APIs (locators, web-first assertions). Do NOT use the deprecated `page.$`, `page.$$`, or raw `waitForSelector` patterns in starter code that the candidate is expected to keep.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years Playwright experience).

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- A `package.json` with `@playwright/test` (and any minimal app deps like `express` if used) and a `test` script (`"test": "playwright test"`).
- A `playwright.config.ts` with `testDir: 'tests'`, a single browser project (chromium is fine), `use.baseURL` pointing at the local app, and a `webServer` block that boots the app under test before tests run (when an Express/Node server is used).
- The app under test: enough HTML/JS/CSS (and a tiny server file if needed) to reproduce the scenario described — e.g., a product card grid for the cart scenario, a page with the relevant `iframe` for the iframe scenario, a small list view for the candidate-list scenario.
- One `tests/<feature>.spec.ts` file that contains the broken/flaky/wrongly-isolated behavior the candidate must fix. It must run (i.e. compile and execute) but FAIL or be flaky in the way described.
- A `.gitignore` covering `node_modules/`, `test-results/`, `playwright-report/`, and `playwright/.cache/`.
- A `README.md` following the structure below.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code or in comments. The fix the candidate must apply MUST NOT already appear in the spec.
- DO NOT include `// TODO`, `// fix me`, `// hint:` or any other comments that point at the fix.
- DO NOT scaffold a fully passing test suite — at least one test in the target spec must fail or flake until the candidate applies the right fix.
- DO NOT include tests for unrelated features that would inflate scope beyond the BASIC time budget.
- DO NOT use Page Object Model abstractions or fixtures beyond what the scenario requires — keep the starter shape flat and obvious for a BASIC candidate.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official Playwright documentation, and AI-powered tools or LLMs.
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific Playwright problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Playwright proficiency while requiring genuine debugging and judgment that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a Playwright task that:
- Draws inspiration from input scenarios for business context and the specific test problem
- Matches BASIC proficiency level (1-2 years Playwright / QA automation experience)
- Can be completed within {minutes_range} minutes — the candidate's edits should land in 1-2 spec files, not across the whole project
- Tests practical Playwright skills: locator selection, waiting strategy, frames, isolation, or simple network mocking — not advanced patterns like sharding, custom reporters, or visual regression
- Select a different real-world scenario each time to ensure variety in task generation
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "playwright-cart-flake-fix", "playwright-iframe-eligibility", "playwright-test-isolation")

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what test needs to be fixed/refactored/extended and why?",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "node_modules/, test-results/, playwright-report/, playwright/.cache/",
    "package.json": "Includes @playwright/test (and any minimal app deps), with `test` script",
    "playwright.config.ts": "testDir, baseURL, single browser project, webServer block if a server is used",
    "tests/<feature>.spec.ts": "The existing spec file that exhibits the problem the candidate must fix",
    "app/<file>.html": "Minimal HTML page(s) that reproduce the UI under test",
    "server.js": "Tiny static/Express server if the scenario requires HTTP routes (otherwise omit)"
  }},
  "outcomes": "Bullet-point list in simple language describing the expected results after completion (e.g., the failing test now passes reliably, no hard sleeps remain, the spec uses a frame-scoped locator, beforeEach replaces beforeAll).",
  "short_overview": "Bullet-point list of exactly 3 short bullets (one sentence each, ~15-25 words). Bullet 1: the business context and the existing test problem. Bullet 2: the specific Playwright change the candidate must make. Bullet 3: the expected outcome. Do NOT prefix bullets with bold mini-titles like '**Business context:**' or '**Expected outcome:**' — start each bullet directly with the content.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm, `npx playwright install` to fetch browsers, Git, and basic TypeScript/Playwright knowledge.",
  "answer": "High-level solution approach — the locator strategy, waiting mechanism, frame scoping, fixture choice, etc. — without giving the exact code.",
  "hints": "Single line suggesting focus area (e.g., 'Look at how Playwright scopes interactions inside iframes and how its assertions auto-wait'). Must NOT give away the fix.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (Playwright Basic)

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario and the current test situation. Describe what feature the test covers, who relies on it, and why the current state is unacceptable. NEVER generate empty content - always provide substantial business context.

### Objectives

Objectives describe the **observable end-state** the candidate must reach. They MUST NOT prescribe the implementation, name Playwright APIs, name the broken code by selector/method, or otherwise tell the candidate what code to write. The candidate should read the objectives and know WHAT "done" looks like, but still have to figure out HOW.

**Allowed phrasing — describes outcome, hides solution:**
- "The test consistently identifies and clicks the 'Add to cart' button for the 'Wireless Mouse' card regardless of the order products render in."
- "After the click, the test confirms the cart badge and the success toast reflect the add-to-cart action only once the backend has actually processed it — without relying on a fixed delay."
- "The previously-failing test passes on five consecutive runs of `npx playwright test`."
- "The spec contains no hard-coded delays or arbitrary sleeps."

**FORBIDDEN phrasing — names the fix, gives the answer away:**
- ❌ "Replace `.product-card .btn-primary` with a resilient, user-facing locator targeting 'Wireless Mouse'."  *(names the broken selector AND prescribes the fix shape)*
- ❌ "Remove the `waitForTimeout(2000)` call entirely."  *(names the exact line to delete)*
- ❌ "Wait using `page.waitForResponse` or a retrying assertion."  *(names the API)*
- ❌ "Use `frameLocator` to scope queries inside the iframe."  *(names the API)*
- ❌ "Use `beforeEach` instead of `beforeAll` for test isolation."  *(names both APIs)*
- ❌ "Use the `request` fixture to seed test data via `POST /api/test/candidates`."  *(names the fixture and the endpoint)*

**Rule of thumb:** if a candidate could copy the objective into an LLM and get the working code back, the objective is too prescriptive. Rewrite it to describe the *behavior* the test must demonstrate, not the *code* it must contain.

Also keep the rubric balanced — at most ONE objective should be a generic hygiene check ("the spec contains no hard-coded delays"). The remaining objectives must be specific to the scenario's primary skill.

**CRITICAL**: Objectives will be used to verify task completion and award points. They must be measurable end-states, never implementation prescriptions.
### Helpful Tips

Practical guidance without revealing implementations:

- Project context and guidance points suitable for basic-level Playwright users
- General Playwright best practices: prefer user-facing locators, prefer web-first assertions, avoid hard sleeps, isolate test state
- Important considerations for the implementation, framed as questions ("Which Playwright API lets you scope queries to an iframe?", "What happens to test state when `beforeAll` is used instead of `beforeEach`?")
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### How to Verify

Verification approaches after implementation:

- Specific checkpoints after the fix: run `npx playwright test`, the previously-failing spec passes, repeat the run to confirm no flakes
- Observable behaviors: assertion targets are user-facing (role/label/text), spec contains no `waitForTimeout`, iframe interactions go through `frameLocator`, each test gets fresh state
- Include both functional checks (tests pass) and code-quality checks (locator quality, isolation, no hard sleeps)
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (npm install, npx playwright install, npx playwright test, etc.)
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific Playwright API names that point exactly at the fix (e.g., do not say "use frameLocator" — say "scope your queries to the right frame")
- Snippets that would reveal locator strategy, frame scoping, or waiting mechanism


## CRITICAL REMINDERS

1. **Starter project must be runnable** with `npm install && npx playwright install && npx playwright test` and the target spec must reproducibly fail or flake until the candidate applies the right fix
2. **The starter test MUST FAIL — no trivially-true assertions.** A test that passes in the starter is a defect. Do NOT use weak checks like `expect(count).toBeGreaterThanOrEqual(0)`, `expect(arr).toBeDefined()`, or asserting only on a count without checking the actual content. The assertion must be tight enough that the bug described in the scenario produces a visible failure (e.g., if the scenario is "wrong product card is clicked", the assertion must verify *which* product was added, not just that *something* was added).
3. **`webServer.url` MUST point at a route that returns HTTP 200**, otherwise Playwright's readiness probe times out and tests never start. Either:
   - Add `app.use(express.static(path.join(__dirname, 'app')))` so `GET /` serves an `index.html`, OR
   - Add an explicit `app.get('/', ...)` handler, OR
   - Set `webServer.url` to a specific route the server actually serves (e.g., `http://localhost:PORT/candidates`).
4. **`webServer.reuseExistingServer` MUST be `false`** — never `true`, never `!process.env.CI`. A candidate machine with anything on the chosen port will silently bind to the wrong server and produce nonsense test output.
5. **Pick a port that does NOT clash with common dev tooling.** Allowed: `3456`, `4321`, `5173`, `7890`, `8123`. Forbidden: `3000` (Next.js/CRA), `8080`, `8000`, `5000` (macOS AirPlay), `4000` (Phoenix), `5432` (Postgres), `6379` (Redis), `27017` (Mongo). Use the same port consistently in `server.js`, `playwright.config.ts` `baseURL`, and `webServer.url`.
6. **NO comments** that reveal the solution or give hints
7. **Task must be completable within {minutes_range} minutes**
8. **Focus on fundamental Playwright concepts** appropriate for BASIC level (locators, waits, frames, isolation, simple network mocking)
9. **Use TypeScript and `@playwright/test` exclusively** — no `playwright` standalone, no JS specs
10. **Keep the candidate's edit surface small** — ideally one spec file, occasionally one spec + one tiny config tweak
11. **README.md MUST be fully populated** with meaningful, task-specific content, and Objectives must describe end-states without naming Playwright APIs (see "Objectives" section above for FORBIDDEN phrasings)
12. **.gitignore** must cover `node_modules/`, `test-results/`, `playwright-report/`, `playwright/.cache/`
13. **Task name** must be short, descriptive, under 50 characters, kebab-case, and SHOULD incorporate the company/product name from the scenario rather than starting with `playwright-` (e.g., `shopnest-cart-determinism`, `medverify-visit-summary-load`)
14. **Select a different real-world scenario** each time for variety
"""

PROMPT_REGISTRY = {
    "Playwright (BASIC)": [
        PROMPT_PLAYWRIGHT_BASIC_CONTEXT,
        PROMPT_PLAYWRIGHT_BASIC_INPUT_AND_ASK,
        PROMPT_PLAYWRIGHT_BASIC,
    ]
}
