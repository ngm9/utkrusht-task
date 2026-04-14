PROMPT_HTML_CSS_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_HTML_CSS_BEGINNER_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an HTML and CSS assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (BEGINNER: 0-1 year experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of HTML/CSS implementation required, the expected deliverables, and how it aligns with the proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_HTML_CSS_BEGINNER_INSTRUCTIONS = """
# HTML & CSS Beginner Task Requirements

## GOAL
As a technical architect experienced in HTML and CSS, you are given real-world scenarios and proficiency levels for frontend web development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

**CRITICAL**: This is an HTML and CSS ONLY task. There must be NO JavaScript in the task whatsoever. No `<script>` tags, no .js files, no event handlers, no DOM manipulation. The entire task must be solvable with pure HTML markup and CSS styling alone.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or significantly restyle page components from a minimal or unstyled starting point.
- The task MUST involve both HTML structure and CSS styling together — not just one in isolation. The candidate should restructure HTML markup AND write substantial CSS.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- **CRITICAL**: Tasks must NOT be trivial one-liner fixes like fixing a typo, changing a selector, or adding an alt attribute. Each task should involve building 2-3 visual components or sections that require real implementation work (e.g., responsive card grid + button styling, Flexbox stat cards + table styling, header/footer + course cards with badges).

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the unstyled or poorly structured state that the starter code implements. This is the exact appearance and code state the candidate will receive.
- Examples: "Cards are displayed as a flat single-column list with inline styles and no spacing"; "The page content exists as plain text paragraphs with no visual structure or layout"; "Stat boxes are stacked vertically as plain `<p>` tags and the table has no styling."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must load in a browser without errors, but it must exhibit exactly this unstyled/unstructured state.

**Required Changes (what the candidate must do):**
- List the specific HTML restructuring and CSS styling the candidate must implement: e.g. "Build a responsive 3-column card grid with styled cards and buttons"; "Create Flexbox stat cards with accent borders and style the table with alternating rows."
- The candidate's job is to restructure the HTML and write the CSS to transform the page from the current state to the required state.
- Each task should have 2-3 distinct implementation steps, not single-line changes.

**Final Implementation Approach:**
- A high-level description of the correct approach.
- The complexity of the task and specific ask expected from the candidate must align with BEGINNER proficiency level (0-1 year experience), ensuring that no two questions generated are similar.
- For BEGINNER level of proficiency, the questions should focus on foundational but substantial concepts:

  **HTML:**
  - Basic semantic elements (`div`, `p`, `h1`-`h6`, `span`, `ul`, `ol`, `li`, `header`, `footer`, `nav`, `section`)
  - Proper heading hierarchy
  - Lists for repeated content
  - Tables for tabular data (`table`, `thead`, `tbody`, `th`, `td`)
  - Forms with `<label>`, `<input>`, `<button>`
  - `id` and `class` attributes for styling hooks
  - `<img>` with `alt` attributes
  - Linking CSS files with `<link>`

  **CSS:**
  - Class and ID selectors (`.class`, `#id`)
  - Basic properties (`color`, `background-color`, `font-size`, `padding`, `margin`, `border`, `border-radius`)
  - Flexbox basics (`display: flex`, `justify-content`, `align-items`, `gap`, `flex-wrap`)
  - CSS Grid basics (`display: grid`, `grid-template-columns`, `gap`)
  - Simple responsive design with one media query (`@media`)
  - Box-shadow for card effects
  - Hover states (`:hover`) and transitions
  - Alternating row styling (`:nth-child`)
  - Background colors and gradients (basic)
  - Typography (font-size, font-weight, text-align, line-height)
  - Inline-block elements for badges/tags

- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern web standards (HTML5, CSS3).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BEGINNER proficiency (0-1 year experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "appointment-card-grid", "portfolio-stat-table", "course-catalog-layout".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, viewable web page** that loads in a browser successfully (open index.html).
- **ZERO errors on load** — the page must load cleanly. The content should be visible, just unstyled or poorly structured.
- **All content/data in the starter code must be present** — The raw text, names, numbers, and information must be in the HTML already. The candidate's job is to restructure and style it, NOT to create content from scratch.
- **The candidate should NOT need to fix anything to make the page load** — The page is already viewable; the candidate's job is to restructure the HTML and build the CSS.

**WHAT MUST BE INCLUDED:**
- The starter code should provide all the raw content/data in the HTML, but with poor structure (e.g., everything in `<div>` or `<p>` tags, inline styles, no semantic elements).
- The code files generated must be valid HTML/CSS that loads in a browser.
- MUST include separate files: index.html and styles.css — properly linked.
- The HTML file must link to the CSS file via `<link>` tag.
- The CSS file should be nearly empty (just a body font-family rule at most) — the candidate writes the CSS from scratch.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the unstyled/unstructured state described in the task.
- **NO JavaScript of any kind**: No .js files, no `<script>` tags, no inline onclick/onchange handlers.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.
- No build tools, no package.json, no npm — just raw HTML/CSS files that open in a browser.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect beginner proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create an HTML/CSS task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BEGINNER proficiency level (0-1 year experience)
- Can be completed within {minutes_range} minutes
- Tests practical skills in building page layouts and styling components using HTML and CSS together
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-page layouts with 2-3 visual components to build
- Pure browser-based — no JavaScript, no Node.js, no npm, no build tools, no frameworks

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Build Responsive Appointment Card Grid for Healthcare Clinic', 'Style Portfolio Dashboard with Stat Cards and Holdings Table', 'Create Course Catalog with Header Footer and Badge Styling'. The title should clearly convey the action (build, style, create, redesign, lay out) and the subject (what page/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact unstyled/unstructured state the starter code implements (what we give). (2) Required Changes — specific HTML restructuring and CSS styling the candidate must implement (2-3 steps). Keep concise but unambiguous.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Web project exclusions (IDE configs, OS files)",
    "index.html": "Main HTML file with raw content in place, linked to CSS, NO JavaScript",
    "styles.css": "CSS file — empty or with only a base font rule"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, environment setup, and knowledge required. Include modern browser (Chrome/Firefox), code editor, Git, and basic knowledge of HTML5 (semantic elements, headings, lists, tables) and CSS3 (selectors, Flexbox, Grid, media queries, box model, hover states).",
  "answer": "High-level solution approach describing HTML restructuring and CSS strategy",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "Semantic HTML": "Using HTML elements that convey meaning about content, such as <header>, <nav>, <section>, rather than generic <div> tags",
    "Flexbox": "A CSS layout model for distributing space and aligning items along a single axis (row or column)",
    "CSS Grid": "A two-dimensional CSS layout system for creating grid-based layouts with rows and columns",
    "Box Model": "The CSS model where every element is a box consisting of content, padding, border, and margin",
    "Media Query": "A CSS technique using @media rules to apply styles based on screen size for responsive design"
  }}
}}


## README.md STRUCTURE (HTML & CSS Beginner)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for the task:

- Describe WHAT needs to look like, not HOW to implement it
- Frame objectives around visual and structural outcomes
- Do NOT specify exact CSS properties, selectors, or HTML elements
- **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:

- Use bullet points starting with "Consider", "Think about", "Explore", "Review"
- Guide the candidate toward discovery — suggest areas to explore, not specific solutions
- Do NOT specify exact CSS properties, layout techniques, or HTML elements
- **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches after implementation:

- Describe what visual behaviors to verify and how to confirm success
- Focus on observable outcomes (correct layout, responsive behavior, visual styling)
- Do NOT specify specific CSS properties or implementation details to check
- **CRITICAL**: Focus on measurable, verifiable visual outcomes. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS unless essential
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Direct solutions or hints
- Specific CSS properties, HTML elements, or layout techniques that would give away the solution
- Any specific implementation details that would reveal the solution
- Excessive bullets or verbose explanations — keep each section lean and focused


## CRITICAL REMINDERS

1. **Environment must be viewable** — The page must load in a browser; the content is visible but unstyled; the candidate does NOT fix load errors, only builds the styling/layout.
2. **Starter code must load in browser** but must NOT contain the styling/layout solution
3. **Starter code must perfectly match the "Current Implementation"** — unstyled/unstructured state
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **ABSOLUTELY NO JavaScript** — no .js files, no script tags, no inline handlers
7. **Code files MUST NOT contain** the CSS layout/styling the candidate must implement
8. **README.md MUST be fully populated** with meaningful, task-specific content
9. **Pure browser-based** — no Node.js, no npm, no build tools, no frameworks
10. **MUST include index.html and styles.css** as separate files properly linked — NO .js files
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"`
14. **Task MUST require meaningful work in both HTML and CSS** — not just adding one property
15. **Tasks must NOT be trivial** — each should involve building 2-3 visual components, not one-liner fixes
"""

PROMPT_REGISTRY = {
    "HTML and CSS (BEGINNER)": [
        PROMPT_HTML_CSS_BEGINNER_CONTEXT,
        PROMPT_HTML_CSS_BEGINNER_INPUT_AND_ASK,
        PROMPT_HTML_CSS_BEGINNER_INSTRUCTIONS,
    ],
}
