PROMPT_REACT_BEGINNER_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_REACT_BEGINNER_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React assessment task.

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

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_BEGINNER = """
# React Beginner Task Requirements

## GOAL
As a technical architect super experienced in React, you are given real-world scenarios and proficiency levels for React development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a simple feature from scratch or fix a small bug in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a clear starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement correct patterns and complete the solution.
- The question should be a real-world scenario and not a trick question that is syntactic errors.

### Task Scenario Structure (Current Implementation vs Required Changes)
Each task MUST be defined in two clear parts so the candidate and assessor know exactly what is given and what must be done:

**Current Implementation (what we give to the candidate):**
- Describe precisely the buggy or incomplete state that the starter code implements. This is the exact behavior and code state the candidate will receive.
- Examples: "The app fetches data from an API but does not show loading or error states"; "Fetch logic is in the component body, causing repeated calls"; "API data is rendered without proper type definitions."
- The **starter code MUST perfectly implement this current implementation** — no more, no less. The code must run and render, but it must exhibit exactly these bugs or missing pieces (e.g. no loading/error states, fetch in wrong place, untyped data). Do not accidentally fix the issues or add the solution in the starter code.

**Required Changes (what the candidate must do):**
- List the specific changes the candidate must make: e.g. "Move API logic into useEffect"; "Add loading and error states"; "Properly type API response data"; "Handle empty API results with a fallback UI."
- The candidate's job is only to complete these required changes on top of the current implementation.

**Final Implementation Approach :**
- A high-level description of the correct approach (e.g. "Maintain loading, error, and data state using useState. Trigger fetch inside useEffect with proper dependency array. Create a reusable ItemCard component. Use conditional rendering for loading/error/empty states.").
- The complexity of the task and specific ask expected from the candidate must align with BEGINNER proficiency level (0-1 year or first steps in React), ensuring that no two questions generated are similar.
- For BEGINNER level of proficiency, the questions must be very specific, narrow in scope, and focus on introductory React concepts like:
  - JSX and basic component structure
  - Passing and using props
  - Simple state with useState (single value or simple list)
  - Basic event handling (onClick, onChange)
  - Simple conditional rendering (show/hide, single condition)
  - Rendering lists with map (simple key usage)
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React best practices (React 18+) and current JavaScript standards. Use functional components with hooks exclusively.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BEGINNER proficiency (0-1 year React experience).
- TASK name should be short and under 50 characters. Use kebab-case (lowercase with hyphens).Examples like "node-postgres-optmization-api","dashboard-dataleak-fix".

### Starter Code Requirements

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working React application** that runs successfully immediately after `npm install` and `npm start`.
- **ZERO compilation errors, ZERO runtime errors, ZERO warnings** — the project must build and run cleanly out of the box.
- **All UI must render correctly** — Every component and UI element included in the starter code must display properly.
- **All existing functionality in the starter code must work** — Any event handlers, state updates, or features that are already implemented must function as intended.
- **The candidate should NOT need to fix anything to make the app run** — The environment is already fully functional; the candidate's job is only to implement the requested feature or fix the specified bug, not to repair a broken project.
- The project must behave like the basic/optimization React tasks: a fully working baseline that the candidate can run, explore, and then extend or fix as per the task description.

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- **Valid package.json** with all required dependencies and **all standard development scripts** (start, build, test, eject).
- **All standard Create React App files** so the app starts perfectly: public/index.html, public/manifest.json, public/robots.txt, src/index.js (entry point).
- The code files generated must be valid and executable with `npm start`.
- Keep the code files minimal and to the point.
- React starter code should use Create React App structure so `npm install` and `npm start` work without any extra setup.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- **Starter code must perfectly implement only the "Current Implementation"** — the buggy or incomplete state described in the task. It must run and display that state (e.g. missing loading/error states, fetch in wrong place); it must NOT include any of the "Required Changes" or the final implementation approach.
- If the task is to fix bugs, the starter code has a simple logical bug (no syntactic errors) that is appropriate for beginner level.
- If the task is to implement a feature from scratch, the starter code only provides a good starting point that matches the described current state.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect beginner React proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a React task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BEGINNER proficiency level (0-1 year React experience)
- Can be completed within {minutes_range} minutes
- Tests practical React skills at an introductory level, focusing on one or two core concepts per task
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-page application features with minimal moving parts

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Structured task description. MUST include: (1) Current Implementation — exact buggy/incomplete state the starter code implements (what we give). (2) Required Changes — specific fixes or features the candidate must implement. Keep concise but unambiguous so starter code can perfectly match Current Implementation and candidate knows exactly what to do.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive React/Node.js exclusions",
    "package.json": "All dependencies and all development scripts (start, build, test, eject)",
    "public/index.html": "HTML entry point",
    "public/manifest.json": "Web app manifest",
    "public/robots.txt": "Robots.txt file",
    "src/index.js": "React app entry point",
    "src/App.js": "Main App component",
    "additional_file.js": "Other component files",
    "additional_file_2.js": "Utility or helper files"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm/yarn, Git, basic JavaScript/React knowledge, etc.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}


## README.md STRUCTURE (React Beginner)
 - The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify 
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific React task scenario being generated
- Use concrete business context, not generic descriptions

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context.

### Objectives

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate appropriate for beginner level
- What functionality should be implemented, expected behavior
- Focus on one or two introductory React concepts
- This is what the candidate should be able to do successfully to say that they have completed the task

**CRITICAL**: Objectives will be used to verify task completion and award points

### How to Verify

Verification approaches after implementation:

- Specific checkpoints after implementation, what to test and how to confirm success
- Observable behaviors or outputs to validate
- Include both functional testing and basic code quality checks
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes


### Helpful Tips

Practical guidance without revealing implementations:

- Project context and guidance points suitable for beginner level React developers
- Simple React concepts and where to look in the codebase
- Important considerations for the implementation for the task
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (npm install, npm start, etc.)
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific React syntax examples or code snippets that would give away the solution
- Component names or specific hook usage patterns that would reveal the solution
- Any specific files or routes implementation details that would give away the solution


## PACKAGE.JSON AND PROJECT STRUCTURE (React Beginner)

### package.json MUST include:
{{
  "name": "task-name",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }},
  "browserslist": {{
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }}
}}

- Use react-scripts for all operations; entry point must be src/index.js.
- Include all four scripts: start, build, test, eject so the app gets started and built correctly.

### Required files for app to start perfectly:
- public/index.html — HTML entry point
- public/manifest.json — Web app manifest (standard CRA)
- public/robots.txt — Robots.txt (standard CRA)
- src/index.js — React app entry point that renders into root
- src/App.js — Main App component

## CRITICAL REMINDERS

1. **Environment must be fully working** — The project must run perfectly with `npm install` and `npm start`; zero errors or warnings; the candidate does NOT fix the environment, only the task (feature/bug).
2. **Starter code must be runnable** with `npm start` but must NOT contain the core logic solution
3. **Starter code must perfectly match the "Current Implementation"**
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on introductory React concepts** appropriate for BEGINNER level
7. **Use functional components with hooks exclusively** (React 18+)
8. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
9. **README.md MUST be fully populated** with meaningful, task-specific content
10. **.gitignore** must cover standard React/Node.js exclusions
11. **Task name** must be short, descriptive, under 50 characters, kebab-case
12. **Select a different real-world scenario** each time for variety
13. **package.json MUST include all dependencies and all four scripts** (start, build, test, eject) so the app gets started correctly
14. **Include all standard CRA files**: public/index.html, public/manifest.json, public/robots.txt; entry point must be src/index.js
15. **Must use react-scripts** for start, build, and test
"""

PROMPT_REGISTRY = {
    "ReactJs": [
        PROMPT_REACT_BEGINNER_CONTEXT,
        PROMPT_REACT_BEGINNER_INPUT_AND_ASK,
        PROMPT_REACT_BEGINNER,
    ]
}
