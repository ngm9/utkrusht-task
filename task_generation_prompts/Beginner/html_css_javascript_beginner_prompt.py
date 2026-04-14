PROMPT_HTML_CSS_JS_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_HTML_CSS_JS_BEGINNER_INPUT_AND_ASK = """
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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (BEGINNER: 0-1 year experience)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_HTML_CSS_JS_BEGINNER_INSTRUCTIONS = """
# HTML, CSS & JavaScript Beginner Task Requirements

## GOAL
As a technical architect experienced in HTML, CSS, and JavaScript, you are given real-world scenarios and proficiency levels for frontend web development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a simple feature from scratch or fix a small bug in the existing code.
- The task MUST involve HTML, CSS, and JavaScript together — not just one in isolation. Even at BEGINNER level, the fix or feature should touch at least two of the three technologies meaningfully.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question that is syntactic errors.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy or incomplete state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The function uses assignment (=) instead of comparison (===) in the conditional"; "The for loop starts at index 1 instead of 0, skipping the first item"; "The function body is empty — it reads the input but does not create or append any DOM element."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must load in a browser without errors (or with only the intentional bugs), but it must exhibit exactly these bugs or missing pieces.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Fix the comparison operator"; "Move the return statement outside the loop"; "Add DOM creation code to append a styled list item."
- The candidate's job is only to complete these required changes on top of the current implementation.

**Final Implementation Approach:**
- A high-level description of the correct approach (e.g. "Change = to ===, update the textContent and toggle the CSS class based on the comparison result.").
- The complexity of the task and specific ask expected from the candidate must align with BEGINNER proficiency level (0-1 year experience), ensuring that no two questions generated are similar.
- For BEGINNER level of proficiency, the questions must be very specific, narrow in scope, and focus on introductory concepts like:

  **HTML:**
  - Basic elements (`div`, `p`, `h1`-`h6`, `span`, `ul`, `ol`, `li`, `button`, `input`)
  - Linking CSS and JS files (`<link>`, `<script>`)
  - Simple forms (`<label>`, `<input>`, `<button>`)
  - `id` and `class` attributes
  - Basic accessibility (`alt` on images, `for`/`id` on labels)

  **CSS:**
  - Class and ID selectors (`.class`, `#id`)
  - Basic properties (`color`, `background-color`, `font-size`, `padding`, `margin`, `border`)
  - Display basics (`block`, `inline`, `none`)
  - Simple hover/active states (`:hover`, `:active`)
  - Applying and toggling CSS classes from JavaScript

  **JavaScript:**
  - Variables (`let`, `const`, `var`)
  - Data types (string, number, boolean)
  - Operators (arithmetic, comparison `===`, `!==`, `>`, `<`, assignment `=`)
  - Control structures (`if/else`, `for` loops)
  - Basic functions (declarations, parameters, return values)
  - DOM selection (`getElementById`, `querySelector`)
  - DOM manipulation (`textContent`, `classList.add/remove/toggle`, `createElement`, `appendChild`)
  - Simple event handling (`addEventListener`, `click`)
  - String methods (`.toLowerCase()`, `.toUpperCase()`, `.replace()`, `.split()`)
  - Array basics (indexing, `.length`, `.push()`)

- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern web standards (HTML5, CSS3, ES6+).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BEGINNER proficiency (0-1 year experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens). Examples like "budget-status-fix", "initials-badge-feature".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working web page** that loads in a browser successfully (open index.html).
- **ZERO JavaScript errors on load** — the page must load cleanly (minor logical bugs related to the task are acceptable, but no syntax errors or missing references).
- **All existing functionality in the starter code must work** — Any HTML rendering, CSS styling, or JS logic that are already implemented must function as intended for the "Current Implementation" state.
- **The candidate should NOT need to fix anything to make the page load** — The environment is already fully functional; the candidate's job is only to implement the requested feature or fix the specified bug.

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid HTML/CSS/JS that loads in a browser.
- Keep the code files minimal and to the point.
- MUST include separate files: index.html, styles.css, and app.js — properly linked.
- The HTML file must link to the CSS (`<link>`) and JS (`<script>`) files correctly.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the buggy or incomplete state described in the task. It must load and exhibit that state; it must NOT include any of the "Required Changes" or the final implementation approach.
- If the task is to fix bugs, the starter code has a simple logical bug (no syntax errors) that is appropriate for beginner level.
- If the task is to implement a feature from scratch, the starter code only provides a good starting point that matches the described current state.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.
- No build tools, no package.json, no npm — just raw HTML/CSS/JS files that open in a browser.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect beginner proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create an HTML/CSS/JavaScript task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BEGINNER proficiency level (0-1 year experience)
- Can be completed within {minutes_range} minutes
- Tests practical skills at an introductory level, focusing on one or two core concepts per task but touching HTML, CSS, and JS together
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-page features with minimal moving parts
- Pure browser-based — no Node.js, no npm, no build tools, no frameworks

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Fix Budget Status Conditional in Wallet Dashboard', 'Build Patient Initials Badge for Clinic Intake Form', 'Fix Product Size Rendering Loop on E-Commerce Page'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state the starter code implements (what we give). (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous so starter code can perfectly match Current Implementation and candidate knows exactly what to do.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Web project exclusions (IDE configs, OS files)",
    "index.html": "Main HTML file with proper structure, linked CSS and JS",
    "styles.css": "CSS file with starter styles",
    "app.js": "JavaScript file with starter logic (or logic needing fixes)"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, environment setup, and knowledge required. Include modern browser (Chrome/Firefox), code editor, Git, and basic knowledge of HTML5 (elements, attributes, forms), CSS3 (selectors, properties, classes), and JavaScript (variables, functions, DOM selection, event handling).",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "DOM": "Document Object Model — a programming interface for web documents that represents the page as a tree of nodes",
    "CSS Class": "A reusable style definition in CSS selected with a dot prefix (e.g., .card) that can be applied to HTML elements via the class attribute",
    "Event Listener": "A JavaScript function that runs when a specific event (like click or input) occurs on a DOM element",
    "Selector": "A pattern used to select HTML elements — in CSS for styling (.class, #id) or in JavaScript for DOM access (querySelector)",
    "textContent": "A JavaScript property that gets or sets the text inside an HTML element, without interpreting HTML tags"
  }}
}}


## README.md STRUCTURE (HTML, CSS & JavaScript Beginner)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for the task:

- Describe WHAT needs to work, not HOW to implement it
- Frame objectives around observable outcomes and expected behavior
- Do NOT specify exact implementation approaches, specific properties, or function calls
- **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:

- Use bullet points starting with "Consider", "Think about", "Explore", "Review"
- Guide the candidate toward discovery — suggest areas to explore, not specific solutions
- Do NOT specify exact implementation approaches, specific HTML tags, CSS properties, or JS methods
- **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches after implementation:

- Describe what behaviors to verify and how to confirm success
- Focus on observable outcomes (correct text, correct styling, correct interaction)
- Do NOT specify specific code, properties, or implementation details to check
- **CRITICAL**: Focus on measurable, verifiable outcomes. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS unless essential
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Direct solutions or hints
- Specific HTML tags, CSS properties, or JavaScript methods that would give away the solution
- Any specific implementation details that would reveal the solution
- Excessive bullets or verbose explanations — keep each section lean and focused


## CRITICAL REMINDERS

1. **Environment must be fully working** — The page must load perfectly in a browser; zero errors; the candidate does NOT fix the environment, only the task (feature/bug).
2. **Starter code must load in browser** but must NOT contain the core logic solution
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on introductory HTML/CSS/JS concepts** appropriate for BEGINNER level
7. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
8. **README.md MUST be fully populated** with meaningful, task-specific content
9. **Pure browser-based** — no Node.js, no npm, no build tools, no frameworks
10. **MUST include index.html, styles.css, and app.js** as separate files properly linked
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
13. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
14. **Task MUST touch at least two of the three technologies** meaningfully — not just a pure JS fix with boilerplate HTML/CSS
"""

PROMPT_REGISTRY = {
    "HTML and CSS (BEGINNER), Javascript (BEGINNER)": [
        PROMPT_HTML_CSS_JS_BEGINNER_CONTEXT,
        PROMPT_HTML_CSS_JS_BEGINNER_INPUT_AND_ASK,
        PROMPT_HTML_CSS_JS_BEGINNER_INSTRUCTIONS,
    ],
}
