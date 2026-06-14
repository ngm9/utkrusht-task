PROMPT_REACTJS_TAILWIND_CSS_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACTJS_TAILWIND_CSS_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React and Tailwind CSS assessment task.

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
- The task must reflect authentic challenges that would be encountered in the role described in the role context
- The task MUST stay within BASIC-level React and Tailwind CSS expectations: straightforward components, state/props, event handling, basic data fetching or form handling, responsive utility usage, accessible interaction states, and simple utility reuse
- The task MUST NOT require advanced architecture, complex state libraries, advanced Tailwind configuration work, backend development, or system design

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, UI context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of React and Tailwind implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACTJS_TAILWIND_CSS_BASIC_INSTRUCTIONS = """
# ReactJs + Tailwind CSS Basic Task Requirements

## GOAL
As a technical architect experienced in React and Tailwind CSS, you are given real-world scenarios and proficiency levels for frontend development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and related metadata that can be effectively used to assess a candidate's ability to understand a realistic UI problem, work within an existing codebase, and implement or fix a small but meaningful feature end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a well-scoped feature from scratch or fix logical/UI bugs in an existing React application styled with Tailwind CSS.
- The task must be realistic and business-oriented, not a trivia question or a syntax-only exercise.
- The question scenario must be clear and grounded in a believable product context.
- Generate enough starter code that gives the candidate a good starting point without giving away the solution.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years experience), ensuring that no two questions generated are similar.
- The task must be completable within {minutes_range} minutes by a candidate with BASIC proficiency.
- The task should focus on 2-3 combined concepts, not a large multi-feature build.

### Scope Alignment Requirements
The generated task MUST stay within the following BASIC-level competency boundaries:

**ReactJs (BASIC) concepts allowed:**
- Functional components with JSX
- Props and local state
- Basic event handling such as clicks and form submissions
- Conditional rendering
- Simple list rendering
- Basic data fetching with fetch or Axios
- Basic debugging-oriented fixes
- Logical component organization and reusability
- Basic accessibility and responsive UI awareness
- Optional simple React Router usage only if it is minor and not central to the task

**Tailwind CSS (BASIC) concepts allowed:**
- Utility classes for layout, spacing, sizing, typography, colors, borders, shadows, transitions, and interactivity
- Responsive breakpoint prefixes
- Hover, focus, active, disabled, group, and peer variants in simple scenarios
- Utility composition and small-scale reuse of repeated class patterns
- Dark mode support only if it is lightweight and already scaffolded
- Accessibility-aware styling such as visible focus states, contrast, hit area, and screen-reader utilities
- Minor configuration references only if already present in starter code; do not make configuration the main task

**Out of scope for this BASIC task:**
- Advanced state management libraries
- Complex routing flows
- System design or architecture-heavy decisions
- Advanced concurrency or performance engineering
- Security hardening
- Complex Tailwind plugin/configuration authoring
- Large-scale theming systems
- Full testing implementation as a primary requirement

### Preferred Task Styles
Prefer practical tasks such as:
- Fixing a broken responsive layout in a React component styled with Tailwind
- Improving a form with basic validation, error display, and accessible states
- Cleaning up duplicated Tailwind utility usage into a simple reusable pattern
- Adding loading, empty, or error states to a small fetched-data component
- Fixing inconsistent button, input, card, or list styling across breakpoints
- Improving focus, disabled, or hover states for keyboard and mouse users
- Making a small UI enhancement while preserving readability and maintainability

### Task Design Guidance
- The task should usually center on one screen or one small feature area.
- The candidate should need to read existing React code and Tailwind class strings, reason about the current behavior, and make practical improvements.
- The task should reward sound judgment: choosing straightforward React state updates, keeping Tailwind classes organized, avoiding conflicting utilities, and preserving accessibility basics.
- Avoid tasks that mainly test memorization of Tailwind class names or setup commands.
- Avoid requiring the candidate to build a backend, Docker setup, authentication flow, or advanced API integration.
- If data fetching is included, keep it simple and local to one component.
- If dark mode is included, it must be a minor styling extension, not the main challenge.

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- A complete, runnable frontend project in a PURE_CODE setup
- package.json with scripts and dependencies needed to run the app
- React application source files
- Tailwind CSS already wired into the project so the candidate does not spend time on setup
- Minimal but realistic project structure
- Starter code that runs successfully after install and start
- Existing UI that reflects the current incomplete or buggy implementation described in the task
- Enough code for the candidate to understand the scenario and begin solving immediately

**WHAT MUST NOT BE INCLUDED:**
- No Docker files
- No backend code
- No database setup
- No comments of any kind that reveal the solution
- No TODO comments
- No placeholder comments
- No implementation of the core fix or feature the candidate is supposed to complete

### Project Structure Requirements for PURE_CODE
- This is a PURE_CODE task: no Docker, no database, no server infrastructure
- Use a simple React project structure with source files and package.json only
- Tailwind must already be configured in the starter project
- Prefer Vite for simplicity, but Create React App is also acceptable if the generated files are coherent and runnable
- Include only the files necessary for a realistic frontend assessment

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including official documentation, search engines, community forums, and AI tools.
- The task should therefore assess practical reasoning, implementation quality, and the ability to adapt solutions to a concrete codebase rather than rote memorization.
- Even with AI assistance, the task should require the candidate to understand the current UI behavior, identify the real issue, and apply an appropriate BASIC-level React and Tailwind solution.

### Code Generation Instructions
Based on the real-world scenarios, create a React and Tailwind CSS task that:
- Draws inspiration from one of the provided scenarios for business context and technical direction
- Matches BASIC proficiency level (1-2 years experience)
- Can be completed within {minutes_range} minutes
- Tests practical React and Tailwind skills together
- Focuses on a small, realistic UI problem rather than a broad application build
- Uses functional React components with hooks
- Uses Tailwind utilities directly in component markup, with small reusable patterns where appropriate
- Encourages accessible and responsive UI behavior
- Keeps the implementation scope narrow enough for a short assessment
- Uses a short, descriptive, kebab-case task name under 50 characters

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented in the React + Tailwind UI?",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Standard Node.js/frontend exclusions",
    "package.json": "Dependencies and scripts",
    "index.html": "App entry HTML if using Vite",
    "src/main.jsx": "React entry point if using Vite",
    "src/App.jsx": "Main App component",
    "src/components/ComponentName.jsx": "Additional React component files",
    "src/data/sampleData.js": "Optional local data file",
    "src/index.css": "Tailwind import file and minimal base styles",
    "tailwind.config.js": "Tailwind configuration",
    "postcss.config.js": "PostCSS configuration"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js, npm/yarn, Git, basic React knowledge, and Tailwind CSS fundamentals.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "React state": "Data stored inside a component that can change over time and trigger a re-render",
    "Props": "Inputs passed from a parent component to a child component",
    "Responsive design": "An approach where the UI adapts to different screen sizes",
    "Tailwind utility class": "A small single-purpose CSS class used directly in markup to style an element",
    "Focus state": "The visible styling shown when an interactive element is selected by keyboard or similar input"
  }}
}}

## Code File Requirements
- The generated code must be valid and runnable.
- Use modern React with functional components and hooks only.
- Tailwind CSS must already be configured and available in the starter code.
- Keep the file set concise and realistic for a BASIC-level frontend task.
- The starter code should reflect the current buggy or incomplete state, not the final solution.
- If the task involves repeated Tailwind classes, it is acceptable to leave duplication in the starter code so the candidate can improve it.
- If the task involves responsiveness, the starter code may intentionally contain conflicting or incomplete responsive classes.
- If the task involves accessibility, the starter code may intentionally omit visible focus states, disabled states, or basic ARIA attributes where appropriate for the candidate to add.
- Do not include advanced abstractions, custom hooks, or architecture-heavy patterns unless they are very small and already scaffolded.
- Do not include comments that reveal implementation direction.

## README.md STRUCTURE

The README.md must contain the following sections:
- Task Overview
- Objectives
- Helpful Tips
- How to Verify

### Task Overview
- Must contain 2-3 substantial sentences
- Describe the business scenario, the current UI problem, and why it matters
- Use concrete, task-specific context
- Do not provide the solution

### Objectives
- Clear, measurable goals appropriate for BASIC level
- Focus on what the candidate should achieve in the UI and behavior
- Cover both React behavior and Tailwind styling where relevant
- Keep the objectives specific enough to verify completion

### Helpful Tips
- Practical guidance without revealing the implementation
- Use bullet points starting with words like "Consider", "Think about", "Explore", or "Review"
- Guide the candidate toward understanding the current code, UI states, responsiveness, and accessibility
- Do not provide exact code or class names that solve the task

### How to Verify
- Specific checkpoints after implementation
- Include observable UI behavior and basic code quality checks
- Cover the main success conditions such as responsive behavior, validation, loading/error handling, or interaction states
- Keep the verification measurable and concrete

### README MUST NOT INCLUDE
- Setup instructions or commands
- Step-by-step implementation instructions
- Exact code snippets
- Direct solutions
- Specific file-by-file implementation guidance that gives away the answer

## Calibration Notes
When generating the task, calibrate it to realistic BASIC-level React + Tailwind work such as:
- a small product card grid with broken mobile layout and missing button states
- a simple invite or contact form with missing validation and inconsistent input styling
- a list or dashboard widget that needs loading/error/empty states plus responsive cleanup
- a small component review/refactor where repeated Tailwind utility groups should become more readable

The task should feel like a real ticket a junior-to-early-mid frontend engineer could complete independently with some care.

## CRITICAL REMINDERS
1. The task must stay within BASIC React and BASIC Tailwind CSS scope only.
2. The task must be a PURE_CODE frontend project with no Docker, no database, and no backend.
3. The starter code must run successfully but must NOT contain the core solution.
4. Use functional React components with hooks exclusively.
5. Tailwind must already be set up in the starter project.
6. Focus on practical UI implementation, debugging, responsiveness, accessibility basics, and simple state handling.
7. Avoid advanced architecture, advanced configuration, or large open-ended builds.
8. README.md must be fully populated with meaningful, task-specific content.
9. The task must be completable within {minutes_range} minutes.
10. Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
"""

PROMPT_REGISTRY = {
    "ReactJs (BASIC), Tailwind CSS (BASIC)": [
        PROMPT_REACTJS_TAILWIND_CSS_BASIC_CONTEXT,
        PROMPT_REACTJS_TAILWIND_CSS_BASIC_INPUT_AND_ASK,
        PROMPT_REACTJS_TAILWIND_CSS_BASIC_INSTRUCTIONS,
    ]
}