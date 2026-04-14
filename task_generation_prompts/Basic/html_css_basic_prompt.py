PROMPT_HTML_CSS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_HTML_CSS_BASIC_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of HTML/CSS implementation required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_HTML_CSS_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in HTML and CSS, including semantic markup, responsive design, modern CSS layout techniques (Flexbox, Grid), accessibility best practices, and frontend styling patterns, you are given a list of real world scenarios and proficiency levels for frontend web development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

**CRITICAL**: This is an HTML and CSS ONLY task. There must be NO JavaScript in the task whatsoever. No `<script>` tags, no .js files, no event handlers, no DOM manipulation. The entire task must be solvable with pure HTML markup and CSS styling alone.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to build or significantly restyle a page layout and its components from a minimal or unstyled starting point.
- The task MUST test both HTML structure and CSS styling/layout together — not just one in isolation.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (0-1 years experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must focus on fundamental HTML and CSS concepts:

  **HTML (Semantic Markup & Structure):**
  - Semantic elements (`header`, `nav`, `main`, `section`, `article`, `footer`, `aside`)
  - Forms with proper `<label>`, `<input>`, `<select>`, `<textarea>`, `<button>` usage
  - Linking labels to inputs with `for`/`id` attributes
  - Accessibility basics (`alt` attributes, `aria-label`, `role` attributes)
  - Proper use of headings hierarchy (`h1`-`h6`)
  - Lists (`ul`, `ol`, `li`) for repeated content
  - Tables (`table`, `thead`, `tbody`, `th`, `td`) for tabular data
  - `<img>` with proper `alt`, `width`, `height` attributes
  - `<time>`, `<address>`, `<figure>`, `<figcaption>` for rich semantics

  **CSS (Styling & Layout):**
  - Flexbox layout (`display: flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `gap`)
  - CSS Grid layout (`display: grid`, `grid-template-columns`, `grid-template-rows`, `gap`, `grid-column`)
  - Responsive design with media queries (`@media`)
  - CSS custom properties / variables (`:root`, `var()`)
  - BEM-style naming conventions (`.block__element--modifier`)
  - Box model (`margin`, `padding`, `border`, `box-sizing`)
  - Transitions (`transition` property for smooth hover/state changes)
  - Pseudo-elements (`::before`, `::after`) for decorative elements
  - Pseudo-classes (`:hover`, `:focus`, `:nth-child`, `:first-child`, `:last-child`)
  - Selector specificity and avoiding `!important`
  - Class-based styling vs inline styles
  - Color systems (hex, rgb, hsl), typography (font-size, font-weight, line-height, letter-spacing)
  - Borders, border-radius, box-shadow for card/component styling
  - Background properties (background-color, background-image, gradients)
  - Overflow handling, text-overflow, white-space

- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern web development best practices (HTML5, CSS3) and current standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Task Environment**: Tasks are pure HTML/CSS — the candidate opens the HTML file in a browser to test. NO JavaScript files, NO `<script>` tags.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create an HTML/CSS task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (0-1 years experience), keeping in mind that AI assistance is allowed.
- Tests practical skills in both HTML structure and CSS styling/layout — the task MUST require meaningful work in both
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on building or restyling page layouts and components that test semantic HTML and modern CSS together
- Should NOT require JavaScript, frameworks (React, Angular, Vue), build tools (Webpack, Vite), or complex infrastructure
- Should NOT require Node.js, npm, or any server-side setup — pure browser-based HTML/CSS only
- The task should involve building 2 distinct components or sections (e.g., stat cards + styled table, responsive grid + notification panel, header + progress cards), not just single-property fixes

## Starter Code Instructions:
- The starter code should provide a minimal HTML structure with the raw content/data already in place, but with little to no CSS styling and potentially poor HTML structure (e.g., everything in `<div>` tags, inline styles, no semantic elements).
- The code files generated must be valid and viewable in a browser (open HTML file).
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly — the starter code should leave substantial room for the candidate to restructure HTML and write CSS from scratch.
- Starter code MUST include separate files: an HTML file and a CSS file (linked properly via `<link>` tag)
- The HTML file must link to the CSS file correctly
- **CRITICAL**: No JavaScript whatsoever — no .js files, no `<script>` tags, no inline event handlers
- No build tools, no package.json, no npm — just raw HTML/CSS files that open in a browser

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Build Responsive Appointment Card Grid for Patient Portal', 'Style Financial Dashboard with Stat Cards and Transaction Table', 'Create Course Catalog Layout with Color-Coded Badges'. The title should clearly convey the action (build, style, create, redesign, lay out) and the subject (what page/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be built or restyled in HTML and CSS",
  "code_files": {{{{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Web project exclusions",
    "index.html": "Main HTML file with raw content/data in place, linked to CSS, NO JavaScript",
    "styles.css": "CSS file — either empty or with minimal base styles that the candidate must build upon"
  }}}},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper semantic HTML, maintainable CSS with consistent naming conventions, and clean code organization.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation goal, and (3) the expected outcome emphasizing visual quality, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include modern browser (Chrome/Firefox), code editor, Git, and fundamentals of HTML5 (semantic elements, forms, tables, accessibility attributes) and CSS3 (Flexbox, Grid, media queries, variables, transitions, pseudo-elements, box model).",
  "answer": "High-level solution approach describing the HTML structure and CSS layout strategy.",
  "hints": "Single line suggesting focus area. Example: 'Focus on choosing the right CSS layout technique for each section and using semantic HTML elements that match the content purpose'",
  "definitions": {{{{
    "Semantic HTML": "Using HTML elements that convey meaning about the content they contain, such as <nav>, <article>, <section>, rather than generic <div> tags",
    "Flexbox": "A CSS layout model for distributing space and aligning items in a container along a single axis (row or column)",
    "CSS Grid": "A two-dimensional CSS layout system for creating complex grid-based page layouts with rows and columns",
    "BEM": "Block Element Modifier — a CSS naming convention that structures class names as .block__element--modifier for maintainability",
    "Media Query": "A CSS technique using @media rules to apply different styles based on screen size or device characteristics for responsive design",
    "CSS Custom Properties": "Variables defined with -- prefix in CSS (e.g., --primary-color) that can be reused throughout stylesheets using var()",
    "Box Model": "The CSS model where every element is a box consisting of content, padding, border, and margin"
  }}}}
}}}}

## Code file requirements:
- Code should follow modern web standards (HTML5, CSS3)
- MUST have separate HTML and CSS files properly linked
- **ABSOLUTELY NO JavaScript** — no .js files, no `<script>` tags, no onclick handlers, no event listeners
- Use semantic HTML elements, not generic `<div>` soup
- CSS should use class-based selectors, avoid inline styles and `!important`
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core styling/layout of the task. They should only provide the raw HTML content/data and minimal setup.
- The CSS layout, component styling, responsive behavior, and visual design that the candidate needs to implement MUST be left empty or with only a base font/reset rule.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add styles here" or "Should use flexbox" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project should be viewable in a browser, but the page will look unstyled/broken until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a gitignore file that covers common web development exclusions including IDE configurations (.idea, .vscode), OS files (.DS_Store, Thumbs.db), and other development artifacts that should not be tracked in version control.

## README.md STRUCTURE (HTML & CSS)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the page. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what CSS properties or HTML elements to use — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level task:
  - Clear, measurable goals the candidate should achieve to complete the task
  - Visual outcomes to implement (layouts, card designs, responsive behavior, styled components)
  - Must include objectives that span both HTML (structure/semantics) and CSS (styling/layout)
  - Frame objectives around visual/structural outcomes, not specific CSS properties
  - **CRITICAL**: Objectives describe the "what" needs to look like and work like, never the "how" to implement it. Keep to 3-5 concise bullets only.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Suggest exploring how semantic HTML elements can improve the page structure
  - Mention thinking about which CSS layout technique best fits each section
  - Hint at considering how to create visual hierarchy through typography and spacing
  - Recommend reviewing how CSS can create distinct visual states (hover, focus, active)
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Visual checks (layout correctness, responsive behavior, component appearance)
  - Resize the browser to test responsive breakpoints
  - Check that semantic HTML elements are used appropriately
  - Verify visual hierarchy, spacing consistency, and interactive states (hover/focus)
  - **CRITICAL**: Describe what visual/structural behaviors to verify, not specific CSS to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands or build tool references
- Specific CSS properties, selectors, or HTML elements that reveal the solution
- Phrases like "you should use flexbox", "add grid-template-columns", "wrap in a <nav>"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "dashboard-stat-cards", "patient-portal-layout")
3. **code_files** must include README.md, .gitignore, index.html, and styles.css — NO .js files
4. **README.md** must follow the structure above with Task Overview, Objectives, Helpful Tips, How to Verify
5. **Starter code** must be viewable in browser but must NOT contain the styling/layout solution
6. **outcomes** must include one bullet on production-level clean code with best practices and semantic HTML
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant HTML/CSS terms
9. **Task must be completable within the allocated time** for BASIC proficiency (0-1 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use modern web standards (HTML5, CSS3)** throughout
12. **ABSOLUTELY NO JavaScript** — no .js files, no script tags, no inline handlers
13. **Task MUST require meaningful work in both HTML and CSS** — restructuring markup AND writing substantial CSS
14. **Pure browser-based** — no Node.js, no npm, no build tools, no frameworks
15. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""

PROMPT_REGISTRY = {
    "HTML and CSS (BASIC)": [
        PROMPT_HTML_CSS_BASIC_CONTEXT,
        PROMPT_HTML_CSS_BASIC_INPUT_AND_ASK,
        PROMPT_HTML_CSS_BASIC_INSTRUCTIONS,
    ],
}
