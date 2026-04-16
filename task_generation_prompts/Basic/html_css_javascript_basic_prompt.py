PROMPT_HTML_CSS_JS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_HTML_CSS_JS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an HTML, CSS, and JavaScript assessment task.

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
2. What will the task look like? (Describe the type of HTML/CSS/JavaScript implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_HTML_CSS_JS_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in HTML, CSS, and JavaScript, including semantic markup, responsive design, modern CSS layout techniques, DOM manipulation, and frontend development best practices, you are given a list of real world scenarios and proficiency levels for frontend web development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The task MUST test a combination of HTML, CSS, and JavaScript skills together — not just one in isolation.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (0-1 years experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental concepts across all three technologies:

  **HTML (Semantic Markup & Structure):**
  - Semantic elements (`header`, `nav`, `main`, `section`, `article`, `footer`, `aside`)
  - Forms with proper `<label>`, `<input>`, `<select>`, `<textarea>`, `<button>` usage
  - Linking labels to inputs with `for`/`id` attributes
  - Accessibility basics (`alt` attributes, `aria-describedby`, `aria-expanded`, `aria-live`, `aria-pressed`)
  - Proper use of headings hierarchy (`h1`-`h6`)
  - Lists (`ul`, `ol`, `li`) for repeated content
  - `data-*` attributes for storing custom data on elements

  **CSS (Styling & Layout):**
  - Flexbox layout (`display: flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `gap`)
  - CSS Grid layout (`display: grid`, `grid-template-columns`, `grid-template-rows`, `gap`)
  - Responsive design with media queries (`@media`)
  - CSS custom properties / variables (`:root`, `var()`)
  - BEM-style naming conventions (`.block__element--modifier`)
  - Box model (`margin`, `padding`, `border`, `box-sizing`)
  - Basic transitions (`transition` property for smooth state changes)
  - Selector specificity and avoiding `!important`
  - Class-based styling vs inline styles

  **JavaScript (DOM & Interactivity):**
  - DOM selection (`getElementById`, `querySelector`, `querySelectorAll`)
  - DOM manipulation (`createElement`, `appendChild`, `textContent`, `classList.add/remove/toggle`)
  - Event handling (`addEventListener`, `click`, `input`, `submit`, `change`)
  - ES6+ features (arrow functions, template literals, destructuring, `let`/`const`)
  - Higher-order array methods (`map`, `filter`, `reduce`, `forEach`, `find`)
  - Basic asynchronous JavaScript (Promises with `.then()/.catch()`, simple `async/await`)
  - Fetch API for simple HTTP requests (`fetch`, handling JSON responses)
  - Basic error handling (`try/catch`, throwing errors)
  - `data-*` attribute access (`dataset` property)
  - Show/hide elements (`hidden` attribute, `classList.toggle`)

- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern web development best practices (HTML5, CSS3, ES6+) and current standards.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Task Environment**: Tasks are browser-based. Every task MUST include an HTML file, a CSS file (or `<style>` block), and a JavaScript file. The candidate opens the HTML in a browser to test.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create an HTML/CSS/JavaScript task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (0-1 years experience), keeping in mind that AI assistance is allowed.
- Tests practical skills across all three technologies (HTML structure + CSS styling/layout + JavaScript interactivity) — the task MUST require meaningful work in each
- Time constraints: Each task should be finished within {{minutes_range}} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on small, self-contained browser-based applications that test semantic HTML, CSS layout/styling, and DOM manipulation together
- Should NOT require frameworks (React, Angular, Vue), build tools (Webpack, Vite), or complex infrastructure
- Should NOT require Node.js, npm, or any server-side setup — pure browser-based HTML/CSS/JS only

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and runnable (open HTML in browser).
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has logical bugs (no syntactic errors) that are substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Starter code MUST include separate files: an HTML file, a CSS file, and a JavaScript file (linked properly)
- The HTML file must link to the CSS and JS files correctly
- No build tools, no package.json, no npm — just raw HTML/CSS/JS files that open in a browser

## REQUIRED OUTPUT JSON STRUCTURE

{{{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Build Responsive Appointment Card Layout with Toggle Notes', 'Fix Filter Logic and Restyle Search Results Page', 'Refactor Checkout Form with Semantic HTML and Validation'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented across HTML, CSS, and JavaScript",
  "code_files": {{{{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Web project exclusions",
    "index.html": "Main HTML file with proper structure, linked CSS and JS",
    "styles.css": "CSS file with starter styles (or styles needing fixes)",
    "app.js": "JavaScript file with starter logic (or logic needing fixes)",
    "additional_file": "Other source files as needed (e.g., data.js, components/)"
  }}}},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper naming conventions, error handling, and code organization.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include modern browser (Chrome/Firefox), code editor, Git, and fundamentals of HTML5 (semantic elements, forms, accessibility attributes), CSS3 (Flexbox, Grid, media queries, variables), and JavaScript ES6+ (DOM manipulation, event handling, async/await, array methods).",
  "answer": "High-level solution approach describing main components and flow across HTML, CSS, and JS.",
  "hints": "Single line suggesting focus area. Example: 'Focus on connecting semantic HTML structure with responsive CSS layout and proper DOM event delegation in JavaScript'",
  "definitions": {{{{
    "Semantic HTML": "Using HTML elements that convey meaning about the content they contain, such as <nav>, <article>, <section>, rather than generic <div> tags",
    "Flexbox": "A CSS layout model for distributing space and aligning items in a container along a single axis (row or column)",
    "CSS Grid": "A two-dimensional CSS layout system for creating complex grid-based page layouts with rows and columns",
    "DOM": "Document Object Model — a programming interface for web documents that represents the page structure as a tree of nodes that JavaScript can manipulate",
    "BEM": "Block Element Modifier — a CSS naming convention that structures class names as .block__element--modifier for maintainability",
    "aria attribute": "Accessible Rich Internet Applications attributes that provide extra semantics for assistive technologies like screen readers",
    "CSS Custom Properties": "Variables defined with -- prefix in CSS (e.g., --primary-color) that can be reused throughout stylesheets using var()"
  }}}}
}}}}

## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern web standards (HTML5, CSS3, ES6+)
- MUST have separate HTML, CSS, and JS files properly linked
- Use semantic HTML elements, not generic `<div>` soup
- Use `let`/`const` instead of `var`, arrow functions where appropriate, template literals, destructuring
- CSS should use class-based selectors, avoid inline styles and `!important`
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core business logic, DOM manipulation handlers, CSS layout fixes, or HTML structural changes that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement validation" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a gitignore file that covers common web development exclusions including IDE configurations (.idea, .vscode), OS files (.DS_Store, Thumbs.db), and other development artifacts that should not be tracked in version control.

## README.md STRUCTURE (HTML, CSS & JavaScript)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario and current state of the application. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level task:
  - Clear, measurable goals the candidate should achieve to complete the task
  - Functionality to implement, expected behavior, user interactions
  - Must include objectives that span HTML (structure), CSS (styling/layout), and JavaScript (interactivity)
  - Frame objectives around outcomes, not specific APIs or methods
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.
  
### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Suggest exploring how semantic HTML elements can improve the page structure and accessibility
  - Mention thinking about CSS layout techniques for responsive behavior across screen sizes
  - Hint at considering how JavaScript can interact with the DOM to create dynamic behavior
  - Recommend reviewing how HTML, CSS, and JS work together (data attributes, class toggling, event-driven style changes)
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.


### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Observable behaviors or outputs to validate (UI updates, responsive behavior, correct interactions)
  - Visual checks (layout, styling), functional checks (JS behavior), and accessibility checks
  - What to test and how to confirm success
  - **CRITICAL**: Describe what behaviors to verify, not specific code or methods to check. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands or build tool references
- Specific HTML tags, CSS properties, or JavaScript APIs that reveal the solution
- Phrases like "you should implement", "add the following code", "use querySelector to..."
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "appointment-card-layout", "checkout-form-refactor")
3. **code_files** must include README.md, .gitignore, index.html, styles.css, and app.js at minimum
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, naming conventions, error handling
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant HTML/CSS/JS terms
9. **Task must be completable within the allocated time** for BASIC proficiency (0-1 years)
10. **NO comments in code** that reveal the solution or give hints
11. **Use modern web standards (HTML5, CSS3, ES6+)** throughout
12. **Task MUST require work across all three technologies** — not just JS with trivial HTML/CSS or vice versa
13. **Pure browser-based** — no Node.js, no npm, no build tools, no frameworks
14. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""

PROMPT_REGISTRY = {
    "HTML and CSS (BASIC), Javascript (BASIC)": [
        PROMPT_HTML_CSS_JS_BASIC_CONTEXT,
        PROMPT_HTML_CSS_JS_BASIC_INPUT_AND_ASK,
        PROMPT_HTML_CSS_JS_BASIC_INSTRUCTIONS,
    ],
}
