PROMPT_SYSTEM_DESIGN_REACTJS_CONTEXT_INTERMEDIATE = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SYSTEM_DESIGN_REACTJS_INPUT_AND_ASK_INTERMEDIATE = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a ReactJs Frontend System Design assessment task.

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
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- CRITICAL: This is a DESIGN task — the candidate will NOT write any code. They will produce a written design document focused on frontend architecture.
- CRITICAL: This is a FRONTEND SYSTEM DESIGN assessment — do NOT prescribe, mandate, or constrain which libraries, state-management solutions, data-fetching tools, styling approaches, build tools, or infrastructure the candidate must use. The candidate is free to choose ANY tooling they see fit. Only describe what currently exists in the frontend application — the candidate decides what to keep, replace, or add.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What frontend feature, page, or application area will the candidate design? (Describe the user-facing problem, technical context, and the design challenge)
2. What design artifacts will the candidate produce? (Note: the candidate receives a BLANK DESIGN.md with no guided sections — they must decide their own document structure. Describe what a strong frontend design document would cover and how the challenge aligns with the given intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SYSTEM_DESIGN_REACTJS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a senior frontend architect with 15+ years of experience designing production React applications, you are given real-world scenarios and proficiency levels for ReactJs Frontend System Design.
Your job is to generate a complete Frontend System Design assessment task where the candidate produces a written design document — NOT new code. The candidate receives a GitHub repo containing a real React project folder structure with existing code files that show the CURRENT frontend application, plus a blank design document (DESIGN.md) where they write their design from scratch — no guided template, no pre-defined sections. The candidate must decide what sections to include, how to structure their document, and what to cover. This itself is part of the assessment.

The repo includes the actual React project structure with real code files (entrypoint, App shell, pages/routes, feature components, hooks, services/API client, store/context, styling, build config) so the candidate can browse and understand what currently exists. The code is structural/high-level — it shows component hierarchies, prop interfaces, hook signatures, route definitions, store shape, and configuration — enough to understand the current frontend architecture, but NOT a full line-by-line production implementation. The candidate is completely free to propose ANY library, framework, build tool, or pattern in their design. Do NOT constrain or prescribe their choices.

## CRITICAL: THIS IS A DESIGN TASK, NOT A CODING TASK
- The candidate does NOT write any code, fix bugs, or implement features
- The candidate receives a GitHub repo containing a real React project folder structure with existing code files showing the current frontend application
- The candidate's deliverable is: write their complete frontend system design in DESIGN.md (a blank file — no template, no guided sections)
- The candidate must decide their own document structure — this tests their ability to organize and communicate a design
- The existing code files are READ-ONLY context — they show what is currently implemented so the candidate understands the frontend they are designing for
- The assessment measures frontend architectural thinking, trade-off analysis, ability to structure a design document, and technical communication

## INSTRUCTIONS

### Nature of the Task
- Present a realistic frontend system design challenge drawn from the provided scenarios
- The question must clearly state: what needs to be designed, the user-experience constraints, the current frontend (if extending), and what the design document should cover
- The challenge should involve multi-feature or multi-layer frontend design (e.g., component architecture + state strategy + data layer + performance/UX concerns)
- Candidates should make 2-3 key technology/architecture decisions with justification — but these are THEIR choices, not prescribed by the task
- Use realistic scale numbers (DAU, payload sizes, list lengths), latency/UX requirements, and business constraints
- Time Constraint: The task must be designed so candidates can complete it within {minutes_range} minutes
- The question must NOT include hints. The hints will be provided in the "hints" field.
- CRITICAL: Do NOT tell the candidate what libraries, frameworks, state managers, data-fetching tools, styling solutions, or build tools to use in their design. Only describe what currently exists. The candidate decides what to propose — this is a core part of the frontend system design assessment.

### Proficiency Level: INTERMEDIATE
For INTERMEDIATE level Frontend System Design with React, the questions should test the candidate's ability to reason about:
- **Component Architecture**: Component hierarchy and composition, container/presentational separation, smart vs dumb components, prop drilling vs composition vs context, controlled vs uncontrolled components, compound components, render props, boundaries between feature modules and shared UI
- **State Management Strategy**: Local state vs lifted state vs global state, choosing between Context/Redux/Zustand/Jotai/Recoil/MobX (and reasoning about WHY), server state vs client state separation, derived state, normalization of nested data, avoiding unnecessary re-renders
- **Data Fetching & Server State**: Fetch patterns (REST/GraphQL/RPC), data-fetching libraries (React Query/SWR/Apollo/RTK Query), caching layers, request deduplication, optimistic updates, pagination/infinite scroll, polling vs WebSocket vs SSE for real-time, retry/error handling, prefetching strategies
- **Rendering Performance**: React rendering model (render vs commit), reconciliation, keys, memoization (`React.memo`, `useMemo`, `useCallback`), virtualization for long lists (react-window/react-virtualized), avoiding layout thrashing, image optimization, deferred rendering with `startTransition`/`useTransition`, Suspense boundaries
- **Code Splitting & Bundle Strategy**: Route-based code splitting, component-level lazy loading (`React.lazy`), dynamic imports, bundle analysis, tree-shaking, vendor chunking, preloading vs prefetching, evaluating third-party library cost
- **Routing & Navigation**: Route structure, nested routes, layout routes, route-level data loading, navigation guards, deep linking, search params/state, browser history management
- **Rendering Mode Trade-offs**: CSR vs SSR vs SSG vs ISR vs streaming SSR — when each fits, SEO implications, hydration cost, first-paint vs interactive timing
- **Authentication & Authorization Flow**: Auth flow in SPA (token storage trade-offs: localStorage/sessionStorage/cookies/in-memory), refresh token handling, protected routes, role/permission-based UI, secure handling of sensitive data on the client
- **Real-time & Push Updates**: WebSocket/SSE integration, optimistic UI, conflict resolution, reconnection strategy, fallback when the connection drops
- **Forms & Validation**: Form state management, controlled vs uncontrolled, validation strategy (schema-based vs ad-hoc), error display patterns, accessibility of form errors
- **Styling Architecture**: CSS strategy (CSS-in-JS / utility-first / CSS Modules / vanilla-extract / etc.) — trade-offs between bundle size, runtime cost, design-system support, and developer ergonomics
- **Accessibility & i18n**: Semantic HTML, ARIA, keyboard navigation, focus management, color contrast, i18n architecture (message catalogs, RTL, locale-aware formatting)
- **Error Handling & Resilience**: Error boundaries, fallback UIs, retry strategies, offline behaviour, graceful degradation, telemetry on client errors
- **Observability**: Client-side error tracking (Sentry-like), performance metrics (Core Web Vitals: LCP, FID/INP, CLS), real-user monitoring, feature usage analytics
- **Build & Tooling**: Build tool choice (Vite/Webpack/Parcel/Turbopack/Rspack), dev-server experience, environment configuration, source maps, CI build pipeline considerations
- The candidate IS expected to reason about frontend distributed concerns: state consistency across tabs, optimistic updates with eventual server reconciliation, offline-first patterns at a practical level
- The candidate is NOT expected to: design from-scratch rendering engines, build custom virtual DOM, or solve theoretical CS problems
- IMPORTANT: The above are areas the candidate should REASON about — do NOT prescribe specific libraries or tools for any of these. The candidate chooses their own stack.

### AI and External Resource Policy
- Candidates are encouraged to use AI tools, documentation, and any external resources
- Tasks should assess genuine frontend architectural reasoning and library selection skills
- The design challenge should require nuanced trade-off analysis (e.g., choosing between data-fetching libraries, state managers, or rendering strategies) that tests real understanding

### Design Challenge Types (pick ONE per task based on the scenario):
1. **Design from scratch**: Given product requirements, design a new frontend feature or application section — define component architecture, state strategy, data layer, routing, and performance approach (candidate picks the stack). The repo still includes code files showing the existing application context the new design must integrate with.
2. **Extend existing app**: Given an existing React application (repo has full project code showing the current implementation), design how to add a major feature or area (e.g., add a real-time collaboration view, an offline mode, or a complex data dashboard). The candidate browses the current code to understand the app, then proposes their design using any libraries they choose.
3. **Diagnose & redesign**: Given a problematic frontend (repo has full project code showing the current flawed implementation — e.g., uncontrolled prop drilling, no memoization on a hot list, ad-hoc fetch with no caching, monolithic store), identify issues and propose a better design. The candidate is free to propose entirely different libraries or patterns.

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "descriptive-kebab-case-name-design",
   "question": "Concise design challenge description in 4-6 lines covering: business/product context, what frontend feature or area needs to be designed, what currently exists (if extending), key constraints (scale, latency, UX, device), and what the candidate must deliver. Do NOT mention what libraries or tools to use — only describe the problem and current state. Keep it brief and to the point — no long paragraphs.",
   "code_files": {{
      "README.md": "Problem statement with: Task Overview (3-4 concise lines only), Design Challenge (bullet points only), Constraints (bullet points with concrete numbers), Deliverable (bullet points only), Evaluation Criteria (bullet points only). EVERY section except Task Overview MUST use bullet points exclusively — no paragraphs.",
      ".gitignore": "Standard Node/React .gitignore (node_modules/, dist/, build/, .env, .env.local, coverage/, .vite/, .turbo/, .next/, .DS_Store, etc.)",
      "DESIGN.md": "A blank file with ONLY a single title line: '# Frontend System Design Document' and a one-line instruction: 'Write your complete frontend system design below. You decide the structure, sections, and level of detail.' — NOTHING else. No section headers, no guiding questions, no hints. The candidate must organize the document entirely on their own.",

      "// ACTUAL PROJECT CODE FILES — the full folder structure of the current React application": "See CODE FILE INSTRUCTIONS below for detailed requirements. Include ALL of these:",
      "// Build/config files": "package.json with real dependencies and scripts, build-tool config (e.g., vite.config.js or webpack.config.js or next.config.js — match whatever the current app uses), tsconfig.json if TypeScript, .env.example, index.html entry, eslint/prettier config if applicable",
      "// Source code files": "App shell / root component (e.g., src/App.jsx or src/App.tsx), entry point (e.g., src/main.jsx or src/index.tsx), route definitions (e.g., src/routes/... or src/pages/...), feature components organized by feature folders (e.g., src/features/<feature>/...), shared UI components (e.g., src/components/...), custom hooks (e.g., src/hooks/...), API/services layer (e.g., src/services/... or src/api/...), state store or context (e.g., src/store/... or src/contexts/...), styling files (CSS modules / styled-components / Tailwind config — whatever the current app uses), utility/helper modules (e.g., src/utils/...)",
      "// Type definitions if applicable": "Shared TypeScript type definitions (e.g., src/types/... or src/models/...) if the project is TypeScript"
   }},
   "outcomes": "Expected design document components in 2-3 lines using simple language. Should mention design artifacts (e.g., component architecture, state strategy, data-fetching approach, performance plan, technology choices with justification).",
   "short_overview": "Bullet-point list in simple language describing: (1) the high-level frontend design challenge, (2) what the candidate must produce (fill in DESIGN.md), (3) key evaluation criteria (trade-off reasoning, library/pattern choices with justification, completeness, clarity)",
   "pre_requisites": "Bullet-point list of knowledge areas needed: understanding of React's rendering and reconciliation model, experience with state management patterns and libraries, familiarity with data-fetching/caching strategies (React Query/SWR/Apollo/etc.), knowledge of code splitting and bundle optimization, understanding of routing and rendering-mode trade-offs (CSR/SSR/SSG), ability to create component diagrams and data-flow diagrams in text or mermaid format.",
   "answer": "Thorough reference design approach — the evaluator's answer key. Must include: recommended library/framework choices with rationale (state, data-fetching, styling, routing, build tool), component hierarchy and boundaries, state-management strategy (what lives where), data-fetching/caching plan, performance optimizations (memoization, virtualization, code splitting), routing structure, failure handling patterns, and deployment/bundling considerations. This should be 4-6 paragraphs covering each likely DESIGN.md section. Note: this is for the EVALUATOR only — candidates never see this.",
   "hints": "A single line nudge toward the right design direction. Example: 'Consider how separating server state from client state — and choosing a dedicated server-state library — could simplify caching, deduplication, and refetch logic across the dashboard.'",
   "definitions": {{
     "term1": "definition1",
     "term2": "definition2"
   }}
}}

## code_files REQUIREMENTS:

### README.md INSTRUCTIONS:
The README.md contains the following sections:
  - Task Overview
  - Design Challenge
  - Constraints
  - Deliverable
  - Evaluation Criteria

**CRITICAL FORMATTING REQUIREMENT**:
- Task Overview MUST be exactly 3-4 concise lines (sentences) — no more, no less. Keep it brief and to the point.
- ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no long prose. Every piece of information should be a discrete bullet point.
- ALL sections must have substantial content — no empty or placeholder text allowed.
- Use concrete technical terminology where relevant, but do NOT prescribe specific libraries or tools.

#### Task Overview
Exactly 3-4 concise sentences describing: the product/UX scenario, what the current frontend does (if extending/redesigning), and why this design challenge matters. Keep it brief — detailed information goes in other sections. Do NOT mention what libraries or tools the candidate should use.

#### Current Frontend Architecture (REQUIRED)
A mermaid diagram showing the CURRENT frontend architecture — ONLY what exists today. Components, hooks, state stores/contexts, API/service layer, and external APIs the app talks to. Must follow the ARCHITECTURE DIAGRAM INSTRUCTIONS section exactly. This diagram helps the candidate visualize the existing app before they write their design. Do NOT include any proposed/future components in this diagram.

#### Current User Interaction Flow (REQUIRED)
A mermaid sequence diagram or flowchart showing how data and user actions currently flow through the frontend for the primary use case — ONLY the current flow, NOT any proposed/future flow. Must follow the same ARCHITECTURE DIAGRAM INSTRUCTIONS for perfect mermaid syntax. Show end-to-end flow from user action (click/typing/route change) through component state, hooks, services, to backend API and back to UI update. This helps the candidate understand how the existing frontend processes interactions before they write their design. Do NOT include any proposed steps, future improvements, or hints about what should change.

#### Design Challenge
All content MUST be bullet points:
- What the candidate needs to design (the problem, not the solution)
- What is in scope
- What is out of scope
- Reference to DESIGN.md as the deliverable
- Do NOT suggest or constrain library/tool choices — the candidate decides

#### Constraints
All content MUST be bullet points with concrete numbers and product/UX boundaries:
- Scale (DAU, simultaneous users in a session, list/grid item counts, payload sizes)
- UX/performance requirements (LCP/FID/INP/CLS targets, interaction latency, time-to-interactive)
- Device/browser support (mobile vs desktop, low-end devices, browser matrix)
- Business constraints (timeline, team size, design-system constraints if any)
- Current frontend description (what the app does today, current stack — for context only, NOT as a mandate to keep using it)
- CRITICAL: Do NOT include technology constraints that tell the candidate what to use. Do NOT say "must use X" or "must be compatible with Y library". Only describe what currently exists — the candidate decides what to propose in their design.

#### Deliverable
All content MUST be bullet points:
- Write your complete frontend system design in DESIGN.md
- You decide the structure, sections, and level of detail
- Use text descriptions, bullet points, and diagrams (mermaid or ASCII) where appropriate
- A strong design document is one that another frontend engineer could use to implement the feature

#### Evaluation Criteria
All content MUST be bullet points — what makes a good frontend design document at the intermediate level:
- Document organization (logical structure, well-chosen sections, clear flow — the candidate defines their own structure)
- Completeness (all critical aspects of the frontend design addressed with sufficient depth)
- Library/pattern choices with justification (candidate explains WHY they chose specific libraries, state managers, data-fetching tools, etc.)
- Trade-off reasoning (alternatives considered with pros/cons, choices justified)
- Clarity (another frontend engineer could implement from this design)
- Feasibility (design works within the stated constraints — including performance and bundle budgets)
- Performance & UX readiness (rendering performance, perceived performance, accessibility, error and loading states)

### NOT TO INCLUDE in README:
- Setup instructions or commands
- The actual design solution or specific library recommendations
- Step-by-step implementation guides
- Specific code patterns or component hierarchies that reveal the answer
- Any mandate or constraint telling the candidate which libraries, frameworks, or tools they must use — the candidate chooses freely

### DESIGN.md INSTRUCTIONS:
- MUST be essentially blank — only a title and a one-line instruction
- Content should be EXACTLY:
  ```
  # Frontend System Design Document

  Write your complete frontend system design below. You decide the structure, sections, and level of detail.
  ```
- DO NOT include any section headers, guiding questions, hints, or suggested structure
- DO NOT include examples of what sections to write
- The candidate choosing their own document structure is a key part of the assessment
- A strong intermediate candidate is expected to independently identify relevant sections like: component architecture, state strategy, data-fetching/caching, performance plan, routing, error/loading handling, accessibility, trade-offs, etc.
- The README's Evaluation Criteria section should mention that "document organization and structure" is an evaluation factor — this is the only hint the candidate gets

### ARCHITECTURE DIAGRAM INSTRUCTIONS (CRITICAL — MUST BE PERFECT):
The README.md MUST include a mermaid architecture diagram showing the CURRENT frontend. This diagram must be syntactically perfect and render without errors. Follow these rules strictly:

**Diagram content rules:**
- The diagram MUST only show what CURRENTLY EXISTS in the frontend — components, hooks, state stores/contexts, API/service modules, and external APIs as they are today
- Do NOT include future/proposed components, dotted lines for "planned" additions, or anything that hints at what the candidate should design
- The diagram is purely factual — it shows the current state of the frontend, nothing more

**Mermaid syntax rules to avoid rendering errors:**
- Always use `graph TD` or `graph LR` for flowcharts — never mix diagram types
- Node IDs must be simple alphanumeric (e.g., `A`, `B`, `Dashboard`) — no spaces, no special characters in IDs
- Use square brackets for labels: `A[App Shell]`, `B[(Store)]`, `C{{{{Context}}}}`
- For subgraphs, always include an `end` keyword: `subgraph Name ... end`
- Arrow syntax: use `-->` for solid arrows, `-.->` for dotted arrows — do NOT use `-->>` or other invalid arrows in flowcharts
- Every opening bracket/parenthesis must have a matching close — double-check all `[`, `(`, `{{{{`, `[(` have their matching `]`, `)`, `}}}}`, `)]`
- Do NOT put special characters like `(`, `)`, `/`, `&`, `#` inside node labels unless wrapped in quotes: `A["Label with parens"]`
- Do NOT use HTML tags or markdown inside mermaid nodes
- Keep labels short and clean — long labels cause rendering issues
- Test mentally: read through each line and verify every node reference, bracket, and arrow is valid

**Sequence diagram syntax rules (for interaction flow diagrams):**
- Start with `sequenceDiagram` on its own line
- Declare participants before use: `participant U as User`
- Use `->>` for synchronous calls, `-->>` for async responses — these are ONLY valid in sequenceDiagram, NOT in flowcharts
- Use `->` for solid arrows without arrowheads, `--)` for async fire-and-forget
- Every `alt`, `opt`, `loop`, `par`, `critical` block MUST have a matching `end`
- Use `Note over A,B: text` for annotations — NOT `Note left of` or `Note right of` with long text
- Do NOT put special characters in message labels — keep them simple text
- Do NOT nest `alt` inside `opt` unless absolutely necessary — each nesting level adds error risk
- Keep participant names short — long names cause rendering issues

**Example of correct flowchart (for frontend architecture):**
```
graph TD
    User[User] --> App[App Shell]
    App --> Router[React Router]
    Router --> Dashboard[Dashboard Page]
    Router --> Settings[Settings Page]
    Dashboard --> Chart[Chart Component]
    Dashboard --> List[Item List]
    Dashboard --> Hook[useDashboardData Hook]
    Hook --> API[API Service]
    Hook --> Store[(Global Store)]
    API --> Backend[Backend REST API]
```

**Example of correct sequence diagram (for interaction flow):**
```
sequenceDiagram
    participant U as User
    participant C as Component
    participant H as Hook
    participant S as API Service
    participant B as Backend

    U->>C: Click Refresh
    C->>H: trigger refetch
    H->>S: GET /items
    S->>B: HTTP request
    B-->>S: 200 items
    S-->>H: items payload
    H-->>C: setState items
    C-->>U: re-render list
```

**Common errors to AVOID:**
- Missing `end` after subgraph, alt, opt, loop, or par
- Unbalanced brackets: `A[Label(` instead of `A["Label()"]`
- Using spaces in node IDs: `Item List` instead of `ItemList[Item List]`
- Using `-->>` in flowcharts (only valid in sequenceDiagram)
- Using `-->` in sequenceDiagram (use `->>` or `-->>` instead)
- Forgetting to close parentheses in store nodes: `S[(Store]` instead of `S[(Store)]`
- Putting parentheses or special characters in message text — use simple text instead
- Missing participant declaration before use in sequenceDiagram
- Forgetting `end` for nested alt/opt/loop blocks — count every opening block and make sure each has an `end`

### CODE FILE INSTRUCTIONS (CRITICAL):
The repo must contain the actual React project folder structure with real code files showing the current frontend. This is NOT pseudo code and NOT a full line-by-line production implementation. It is structural/high-level code that shows:

**What the code files SHOULD contain:**
- Real module/file structure with proper folder organization (e.g., `src/App.jsx`, `src/main.jsx`, `src/pages/Dashboard.jsx`, `src/features/<feature>/<Feature>.jsx`, `src/components/Button.jsx`, `src/hooks/useDashboardData.js`, `src/services/api.js`, `src/store/index.js`)
- Component definitions with real prop interfaces (TypeScript types or PropTypes/JSDoc), JSX returning the actual high-level structure, key state and effect hooks shown — but not every detail
- Real route definitions (e.g., a routes config or top-level `<Routes>` declaration), App shell composition, layout components
- Custom hooks with real signatures showing what they encapsulate (fetching, subscriptions, state)
- API/service modules showing endpoints called, response handling at a high level
- State store / context setup (e.g., a Redux store with slices/reducers, a Zustand store, a Context with provider) — whatever the current app uses
- Styling setup (Tailwind config, CSS modules, styled-components theme, etc.) — whatever the current app uses
- Configuration files (`package.json` with real dependencies and scripts, `vite.config.js`/`webpack.config.js`/`next.config.js` as applicable, `tsconfig.json` if TypeScript, `index.html` entry)

**What the code files must NOT contain:**
- Full line-by-line production implementation — keep components concise, show the structure and key logic, not every event handler or edge case
- Pseudo code or fake placeholder code — the code should look like real code, just not exhaustively complete
- TODO comments, "implement this", or any hints about what the candidate should design or change
- Comments suggesting what needs to be added, improved, or redesigned
- Any indication of what the candidate's design should include

**Style guideline:**
- Each code file should feel like reading a real React project's source — proper `import` statements, default/named exports, idiomatic React (function components, hooks, JSX), real prop interfaces, real hook signatures
- Components should have real prop shapes and show the high-level JSX/state flow (e.g., "fetch via hook, render header + list, handle empty/loading states") with enough code to understand what happens, but not every utility helper or edge case
- Config files should show real dependencies (`package.json`), real build config (entry, plugins, aliases)
- The candidate should be able to browse these files and understand: "this is what the current frontend does and how it's structured"

**Folder structure must be realistic:**
- Follow common React project conventions: `src/` root with subfolders like `pages/` or `routes/`, `features/` (feature-sliced) or `components/` + `containers/`, `hooks/`, `services/` or `api/`, `store/` or `contexts/`, `utils/`, `types/` (if TS), and optional `assets/`
- Include build files (`package.json`, build-tool config, `tsconfig.json` if TS, `index.html`), and source files as appropriate
- The folder structure itself tells the candidate about the current frontend architecture

**CRITICAL RULES for code files:**
- Code files are READ-ONLY context — they show what exists today
- Do NOT include any language that tells the candidate what to implement, change, or use
- Do NOT add comments like "// this could be improved" or "// consider replacing with X"
- The code simply shows the current state — the candidate figures out the design challenge from the README and makes their own library/pattern choices

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **This is a DESIGN task with real code context** — The repo contains actual React project code files (components, hooks, services, store, config, build files) showing the current frontend. The candidate reads these to understand the current state, then writes their design in DESIGN.md.
3. **code_files MUST include**: README.md, .gitignore, DESIGN.md, AND the full project folder structure with real code files (components, hooks, services, store, styling, build/config files). The code shows what currently exists — it is NOT the candidate's deliverable.
4. **DESIGN.md must be blank** — only a title and one-line instruction. NO sections, NO guiding questions, NO hints
5. **The candidate decides the structure** — this is part of the assessment at intermediate level
6. **name** must be kebab-case and end with "-design", e.g., "realtime-dashboard-frontend-design"
7. **Task must be completable in {minutes_range} minutes** — scope to a single feature or app area (e.g., a dashboard, a search-and-filter view, a real-time collaboration panel), not an entire SaaS application
8. **answer field** is the evaluator's answer key — make it thorough with specific library choices (state, data-fetching, styling, build tool), component hierarchy, performance plan, and trade-off rationale. This is for evaluators only, never shown to candidates.
9. **definitions** must include 4-6 relevant frontend architecture/design terms (e.g., reconciliation, hydration, server state vs client state, virtualization, code splitting, Suspense boundary, render prop, error boundary, optimistic update, debouncing, throttling, Core Web Vitals)
10. **Do NOT include any TODO comments, "implement this", hints, or placeholder text** in ANY file — especially not in code files. The code shows what EXISTS, nothing more.
11. **Code files must be structural/high-level** — show component hierarchies, prop interfaces, hook signatures, JSX structure, store shape, and config. NOT full line-by-line production code, NOT pseudo code. The candidate should understand the current frontend by browsing the code.
12. **README.md formatting**: Task Overview MUST be exactly 3-4 concise lines. ALL other sections (Design Challenge, Constraints, Deliverable, Evaluation Criteria) MUST use bullet points ONLY — no paragraphs, no prose blocks. Every piece of information should be a discrete bullet point.
13. **question field** must be concise — 4-6 lines only, not long paragraphs
14. **NEVER prescribe technology choices** — Do NOT tell the candidate what state manager (Redux / Zustand / Jotai / Context / etc.), data-fetching library (React Query / SWR / Apollo / RTK Query / etc.), router (React Router / TanStack Router / Next.js routing / etc.), styling solution (Tailwind / styled-components / CSS Modules / vanilla-extract / etc.), build tool (Vite / Webpack / Parcel / Turbopack / etc.), or rendering framework (CRA / Vite / Next.js / Remix / etc.) to use anywhere in ANY file. Only describe/show what currently exists. The candidate's library and pattern choices and justifications are a core evaluation criterion. This applies to README.md, constraints, code files, comments — NOWHERE should the task mandate what the candidate must use.
15. **Code files must have realistic folder structure** — follow common React project conventions (`src/` with subfolders for pages/components/hooks/services/store/utils as appropriate to the current app). The folder structure itself communicates the current architecture.
16. **Mermaid diagrams MUST be syntactically perfect** — Both the architecture diagram (flowchart) AND the interaction flow diagram (sequence diagram) must render without errors. Double-check: all brackets/parentheses are balanced, node IDs have no spaces or special characters, every `subgraph`/`alt`/`opt`/`loop`/`par` has a matching `end`, arrows use valid syntax for the diagram type (`-->` for flowcharts, `->>` for sequenceDiagram), participants are declared before use in sequenceDiagram, and special characters in labels are avoided or quoted. Both diagrams MUST only show the CURRENT frontend — no proposed/future components or flows, no hints about what to design. Read through each diagram line-by-line before outputting to verify correctness.
"""

PROMPT_REGISTRY = {
    "ReactJs (INTERMEDIATE)": [
        PROMPT_SYSTEM_DESIGN_REACTJS_CONTEXT_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_REACTJS_INPUT_AND_ASK_INTERMEDIATE,
        PROMPT_SYSTEM_DESIGN_REACTJS_INTERMEDIATE_INSTRUCTIONS,
    ]
}
