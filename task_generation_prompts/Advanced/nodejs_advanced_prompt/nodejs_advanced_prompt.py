PROMPT_NODEJS_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and the role requirements, particularly focused on advanced Node.js engineering — including event-loop reasoning, concurrency and async coordination, streaming and backpressure, worker_threads and cluster usage, and writing maintainable production-grade Node.js modules?
"""

PROMPT_NODEJS_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Node.js assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the technical context, problem shape, and domain described in the selected real-world scenario
- The task complexity must be appropriate for ADVANCED Node.js proficiency (6+ years of experience)
- Ensure the candidate can realistically complete the task on a local machine in the allocated time
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that an advanced Node.js engineer would face

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the technical context and the specific Node.js problem the candidate will be solving)
2. What will the task look like? (Describe the type of Node.js implementation or fix required, the expected deliverables, and how it aligns with ADVANCED Node.js proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_NODEJS_ADVANCED_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Node.js — including the event loop, asynchronous patterns, streams and backpressure, worker_threads, cluster, performance instrumentation, and modular runtime design — you are given a list of real world scenarios and proficiency levels for Node.js.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to design, debug, optimize, and extend production-grade Node.js code at an advanced level. The task must be pure Node.js: a candidate can clone the repo and run it locally with `npm install` followed by `npm test` or `node <entrypoint>`.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing Node.js codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are realistic and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate apply best practices, reason about asynchronous behavior, demonstrate proper architectural decisions, and not just patch the surface error.
- The question should be a real-world scenario that tests engineering judgment, not just implementation skill.
- The complexity of the task must align with ADVANCED Node.js proficiency (6+ years experience). For ADVANCED level, the task should test deep understanding of one or more of:
  - **Event loop & microtasks**: distinguishing macrotasks vs microtasks, identifying blocked event loop, using `setImmediate`/`process.nextTick`/`queueMicrotask` correctly, measuring loop lag
  - **Asynchronous mastery**: bounded concurrency, `Promise.allSettled` / `Promise.race`, cancellation with `AbortController` / `AbortSignal`, retry with backoff, timeouts wrapped around any async operation
  - **Streams**: readable/writable/duplex/transform streams, `pipeline`, backpressure (`.write()` returning false, `drain` events), object-mode streams, async iteration over streams
  - **Concurrency primitives**: `worker_threads` (transferring `ArrayBuffer`, `MessageChannel`, `SharedArrayBuffer` / `Atomics`), `cluster`, child_process for CPU-bound or isolation-required work
  - **Performance & observability**: `perf_hooks` (`performance.now`, PerformanceObserver), event loop monitoring (`perf_hooks.monitorEventLoopDelay`), heap snapshots, identifying memory leaks
  - **EventEmitter & async iteration**: building robust emitters, listener leak detection, `on('error')` discipline, async iterators (`for await...of`)
  - **Error propagation**: distinguishing synchronous throws vs Promise rejections vs `EventEmitter` errors, `try/catch` around `await`, `process.on('unhandledRejection')`, custom Error subclasses
  - **Modular architecture & types**: clean module boundaries, ESM vs CommonJS, dependency injection, TypeScript at the type-system level (generics, conditional types, narrowing) where relevant
  - **Native APIs**: `Buffer` semantics, encoding pitfalls, `fs.promises` and streaming file IO, `crypto` for hashing/HMAC where it fits the scenario, `net`/`http` raw socket behavior
- The task must NOT include hints. The hints will be provided in the "hints" field.
- The task must be self-contained: runnable with only Node.js installed locally. No external services (no PostgreSQL, no MongoDB, no Redis, no Kafka, no HTTP framework beyond raw `http`/`net` unless the scenario specifically requires Express/Fastify as the surface).
- If you include diagrams, ensure they are written in mermaid format, properly indented and in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Node.js documentation, MDN, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The task is designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific Node.js problem rather than testing rote memorization. Therefore, the task complexity should require genuine engineering judgment that goes beyond simple copy-pasting from an LLM.
- Candidates should be able to evaluate different approaches and justify their chosen solution.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Node.js task that:
- Draws inspiration from the input_scenarios to determine the technical context and problem shape
- Matches the complexity level appropriate for ADVANCED Node.js proficiency (6+ years experience), keeping in mind that AI assistance is allowed
- Tests practical advanced-level Node.js engineering: event-loop reasoning, async concurrency, streaming, worker isolation, performance instrumentation, or robust error propagation — depending on the selected scenario
- Time constraints: Each task should be finished within {minutes_range}.
- At every time pick a different real-world scenario from the list provided above to ensure variety in task generation.
- Produces a runnable Node.js project structure that uses only the Node.js standard library and npm dependencies.
- The starter code must be runnable locally via `npm install` followed by `npm test` or `node <entrypoint>`. The candidate runs everything on their own machine.

## Starter Code Instructions
- The starter code should provide a foundation that allows candidates to demonstrate architectural and async-correctness skills.
- The code files generated must be valid and parseable JavaScript or TypeScript.
- Provide a realistic project structure that mimics a real-world Node.js module or service (e.g., `src/`, `tests/`, `src/lib/`, `src/workers/`).
- Include some existing modules, classes, or utilities that the candidate needs to work with, extend, or refactor.
- Provide partial implementations that require the candidate to complete the meaningful engineering work.

### Stub Quality — REQUIRED
The starter MUST be visibly incomplete. Each location the candidate is expected to change MUST be in ONE of these two shapes (see `infra/evals.py` STUB QUALITY criterion):
  - (a) **STUB SHAPE**: a function or method whose body contains a `// TODO:` comment together with `throw new Error('Not implemented')`, for behavior the candidate must IMPLEMENT from scratch. The function signature, name, and call sites already exist; the body is the placeholder.
  - (b) **BUGGY-CODE SHAPE**: the broken code is present, runs, and exhibits the exact bug or inefficiency named in the task description (e.g., a sequential `await` loop for a "make it concurrent" task; a missing `try/catch` around an emitter for an "error-resilience" task; a stream consumer that ignores backpressure for a "stream-correctness" task). The bug MUST stay visible in the starter code.

- The starter MUST NOT already implement the fix. If the task says "make calls concurrent", the starter MUST still be sequential. If the task says "add cancellation", there must be NO `AbortController` plumbing in the starter. If the task says "respect backpressure", the starter MUST ignore the `drain` signal.
- **Comment policy**: it is OK and encouraged to mark WHAT is broken or missing using neutral comments such as `// TODO: implement bounded concurrency`, `// FIXME: sequential — see task brief`, or `// TODO: add cancellation`. These comments MUST NOT reveal HOW to fix the issue — never name the specific API, function, or pattern that solves it (do not write "use Promise.allSettled", "use AbortController", "use stream.pipeline", etc.).
- DO NOT include comments that give away hints or solutions.
- The project should be runnable locally (with `npm install && npm test` or `node <entrypoint>`), but solving the task must require meaningful code changes by the candidate.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "Kebab-case GitHub repository name under 50 characters that matches the generated task and is suitable as a folder/repo name.",
  "title": "Human-readable display name in '<action verb> <subject>' format, 50-80 characters, clearly describing the advanced Node.js task. Examples: 'Implement Bounded Concurrency for a Webhook Fan-Out Worker', 'Fix Stream Backpressure in a Log-Tailer Pipeline', 'Refactor Worker Pool for CPU-Bound Image Processing'. The title must be different from the kebab-case `name`.",
  "question": "A detailed candidate-facing description of the task scenario explaining the current Node.js behavior, the specific problems to address, the constraints, and what the candidate is expected to deliver — without revealing the exact solution.",
  "code_files": {{
    "README.md": "Candidate-facing README with the four required sections (Task Overview, Objectives, How to Verify, Helpful Tips) following the structure below.",
    ".gitignore": "Comprehensive Node.js exclusions (node_modules, dist, .env, logs, coverage, IDE files, OS files).",
    "package.json": "Realistic Node.js manifest with dependencies, devDependencies, and scripts (e.g., 'test', 'start') that let the candidate run the project locally with no external services.",
    "src/...": "Source code modules implementing the partial/buggy starter. Use a realistic folder layout (e.g., src/index.js, src/lib/, src/workers/, src/streams/) appropriate for the scenario.",
    "tests/...": "Test files using Node's built-in test runner (node:test) or Jest/Vitest if package.json declares them. Tests MUST initially fail in a way that matches the task description (the failure IS the task).",
    "additional_files": "Any other files needed to make the project realistic and runnable, such as sample input fixtures, config modules, or type definitions."
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable. One bullet MUST explicitly state: 'Write production level clean code with best practices including proper error handling, clear module boundaries, and idiomatic Node.js patterns.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level Node.js problem in plain terms, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, resilience, and maintainability.",
  "pre_requisites": "Bullet-point list of tools and knowledge required: Node.js 20+ installed locally, npm or pnpm, familiarity with async/await, Promises, streams, EventEmitter, worker_threads, and the Node.js standard library. Optionally TypeScript if the task uses it.",
  "answer": "Evaluator-facing high-level solution approach describing the intended engineering direction and the major changes a correct submission should make, without prescribing exact code.",
  "hints": "A single-line hint pointing the candidate toward the right area of investigation (e.g., 'Think about which Promise combinator gives you settled outcomes for every call rather than short-circuiting on the first failure'). Must NOT reveal the specific API or pattern.",
  "definitions": {{
    "Event Loop": "Node.js's mechanism for handling asynchronous operations by polling phases (timers, pending callbacks, poll, check, close) and draining microtasks between them.",
    "Backpressure": "A flow-control signal in Node.js streams indicating that a writable destination cannot accept more data; producers must wait for the 'drain' event before continuing to write.",
    "Worker Thread": "A separate JavaScript execution context running on its own thread, used to offload CPU-bound work without blocking the main event loop; communicates with the parent via message passing.",
    "AbortController": "A standard API for signalling cancellation to async operations; the paired AbortSignal can be passed to fetch, timers, and any cancellation-aware function.",
    "Microtask": "A task queued to run after the currently executing synchronous code and before the next macrotask; created by Promise resolutions and queueMicrotask. Microtasks can starve the event loop if produced unbounded."
  }}
}}

## Code file requirements
- Generate a realistic folder structure for the task complexity (e.g., `src/`, `src/lib/`, `src/workers/`, `src/streams/`, `tests/`).
- Code should follow modern Node.js best practices: ESM or CommonJS consistently, `const`/`let`, async/await, structured error handling, and clear module boundaries.
- **CRITICAL**: The generated code files MUST contain the visibly-incomplete stub shape OR the visible buggy shape described above. A starter that already implements the fix will be rejected.
- The candidate should need to make important engineering decisions around async correctness, stream behavior, worker coordination, performance, or maintainability.
- The task must run with only Node.js and npm-installed packages on the candidate's local machine.

## .gitignore INSTRUCTIONS
Create a comprehensive .gitignore that covers all standard exclusions for a Node.js project:
- `node_modules/`
- build outputs such as `dist/`, `build/`, `.tsbuildinfo`
- environment files such as `.env`, `.env.local`
- log files such as `*.log`, `logs/`
- coverage reports such as `.nyc_output/`, `coverage/`
- IDE configurations such as `.idea/`, `.vscode/`, `*.swp`, `*.swo`
- OS-specific files such as `.DS_Store`, `Thumbs.db`

## README.md INSTRUCTIONS
- The README.md contains the following sections in this exact order:
  - Task Overview
  - Objectives
  - How to Verify
  - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content.
- Task Overview section MUST contain the exact business / technical scenario from the task description.
- ALL sections must have substantial content — no empty or placeholder text.
- Content must be directly relevant to the specific Node.js task scenario being generated.
- Use concrete technical context, not generic descriptions.
- **IMPORTANT**: Do NOT directly tell candidates what to implement — provide direction and guidance so they discover the solution.
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity.
- README should NOT be heavy — each section should have **4-6 bullets max for Objectives**, **4-6 bullets max for How to Verify**, and **4-5 bullets for Helpful Tips**.

### Task Overview
- This section MUST contain 3-4 meaningful sentences describing the technical scenario, the current behavior of the Node.js code, and why the problem matters at scale or in production.
- Never generate empty content; always provide substantial context that explains what the candidate is working on and why correct Node.js engineering is crucial here.

### Objectives
- Clear, measurable goals for the candidate appropriate for advanced Node.js level.
- 4-6 bullets, each describing ONE outcome the candidate should achieve to complete the task successfully.
- These objectives will also be used to verify task completion.
- Focus on outcomes (what behavior should be true after the fix), not on prescribed implementation details.
- Include both functional correctness and production-quality expectations such as resilience, maintainability, observability.
- **CRITICAL**: Objectives describe the "what" and "why", never the "how".

### How to Verify
- 4-6 bullets, each describing one observable check the candidate can run locally to confirm the fix.
- Use the available tooling: `npm test`, running a script with `node`, inspecting logs, comparing timing measurements, checking memory usage, observing stream throughput.
- Frame verification in terms of observable outcomes (response time, test pass/fail, output shape, log lines).
- **CRITICAL**: Describe what to verify and the expected behavior — do not describe the specific implementation to write to make the check pass.

### Helpful Tips
- 4-5 bullets, each starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze".
- Guide the candidate toward investigating the right Node.js area (event-loop behavior, async boundaries, stream backpressure, worker coordination, error propagation) depending on the scenario.
- Tips must guide discovery and technical reasoning — never provide direct solutions or name the specific API/pattern that solves the task.

### NOT TO INCLUDE in README
Make sure you do NOT include the following in README.md:
- Setup commands such as `npm install`, `npm start`, `node app.js`, `npm test`
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific Node.js APIs, method names, or design pattern names that reveal the solution (do not write "use Promise.allSettled", "use stream.pipeline", "use AbortController", "use worker_threads.MessageChannel", etc.)
- Code snippets that give away the answer
- Phrases like "you should implement", "add this middleware", "create this class"

## CRITICAL REMINDERS
1. Output must be valid JSON only when generating the task instance — no markdown, no explanations, no code fences.
2. `name` must be short, descriptive, kebab-case (e.g., "bounded-concurrency-worker", "stream-backpressure-fix", "worker-pool-image-processor").
3. `code_files` MUST include README.md, .gitignore, package.json, and realistic source/test files.
4. **STUB QUALITY IS NON-NEGOTIABLE**: every concern named in `question` must map to a visibly-incomplete spot in the code — either a `// TODO:` + `throw new Error('Not implemented')` stub, or the exact bug/inefficiency described in the task, left in place untouched. A starter that already implements the fix will be rejected.
5. Comments may name WHAT is broken or missing (e.g., `// TODO: implement bounded concurrency`, `// FIXME: ignores backpressure`) but MUST NOT name HOW to fix it.
6. The README must follow the exact 4 sections in order: Task Overview, Objectives, How to Verify, Helpful Tips. Section sizes: Task Overview 3-4 sentences; Objectives 4-6 bullets; How to Verify 4-6 bullets; Helpful Tips 4-5 bullets.
7. The task must be runnable on a candidate's local machine using only Node.js and npm-installed packages.
8. The task must be completable within the allocated time for ADVANCED proficiency (6+ years experience), assuming AI assistance is allowed.
9. NO code comments may reveal the solution or name the specific API/pattern that fixes the issue.
10. Use modern Node.js (20+) conventions — async/await, ESM or CommonJS consistently, structured logging via `console` or a tiny helper, `node:test` or jest/vitest for tests.
11. Focus on pure Node.js engineering — event loop, async coordination, streams, worker_threads, cluster, performance, error propagation, EventEmitter. Use `http`/`net` only when the selected scenario genuinely needs raw HTTP behavior.
12. `title` must be in `<action verb> <subject>` format and different from `name` — name is kebab-case for GitHub repo, title is human-readable for display.
"""

PROMPT_REGISTRY = {
    "NodeJs (ADVANCED)": [
        PROMPT_NODEJS_ADVANCED_CONTEXT,
        PROMPT_NODEJS_ADVANCED_INPUT_AND_ASK,
        PROMPT_NODEJS_ADVANCED_INSTRUCTIONS,
    ],
}
