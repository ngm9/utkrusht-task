PROMPT_REACT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_REACT_BASIC_INPUT_AND_ASK = """
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

PROMPT_REACT_BASIC = """
# React Basic Task Requirements

## GOAL
As a technical architect super experienced in React, you are given real-world scenarios and proficiency levels for React development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years React experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental React concepts like:
  - Component composition and props
  - State management with useState and useEffect
  - Event handling
  - Conditional rendering
  - Form handling and validation
  - Basic data fetching
  - Component lifecycle understanding
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React best practices (React 18+) and current JavaScript/TypeScript standards. Use functional components with hooks exclusively.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years React experience).

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `npm start`.
- Keep the code files minimal and to the point.
- React starter code should include basic project structure but NOT require complex infrastructure setup (advanced build configurations, complex testing setup, etc.).
- Focus on Create React App or Vite setup for simplicity.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- If the task is to fix bugs, the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, the starter code only provides a good starting point.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic React proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a React task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BASIC proficiency level (1-2 years React experience)
- Can be completed within {minutes_range} minutes
- Tests practical React skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-page application features rather than complex routing or state management libraries
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "react-inventory-app", "react-form-validation")

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed/implemented?",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive React/Node.js exclusions",
    "package.json": "All dependencies and development scripts",
    "public/index.html": "HTML entry point",
    "src/index.js": "React app entry point",
    "src/App.js": "Main App component",
    "additional_file.js": "Other component files",
    "additional_file_2.js": "Utility or helper files"
  }},
  "outcomes": "Bullet-point list in simple language. Expected results after completion.",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm/yarn, Git, JavaScript/React knowledge, etc.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## README.md STRUCTURE (React Basic)

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: This section MUST contain 2-3 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content - always provide substantial business context.

### Helpful Tips

Practical guidance without revealing implementations:

- Project context and guidance points suitable for basic level React developers
- General React best practices and architectural notes
- Important considerations for the implementation for the task
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### Objectives

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate appropriate for basic level
- What functionality should be implemented, expected behavior
- Focus on fundamental React concepts and skills
- This is what the candidate should be able to do successfully to say that they have completed the task

**CRITICAL**: Objectives will be used to verify task completion and award points

### How to Verify

Verification approaches after implementation:

- Specific checkpoints after implementation, what to test and how to confirm success
- Observable behaviors or outputs to validate
- Include both functional testing and basic code quality checks
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (npm install, npm start, etc.)
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific React syntax examples or code snippets that would give away the solution
- Component names or specific hook usage patterns that would reveal the solution
- Any specific files or routes implementation details that would give away the solution


## CRITICAL REMINDERS

1. **Starter code must be runnable** with `npm start` but must NOT contain the core logic solution
2. **NO comments** that reveal the solution or give hints
3. **Task must be completable within {minutes_range} minutes**
4. **Focus on fundamental React concepts** appropriate for BASIC level
5. **Use functional components with hooks exclusively** (React 18+)
6. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
7. **README.md MUST be fully populated** with meaningful, task-specific content
8. **.gitignore** must cover standard React/Node.js exclusions
9. **Task name** must be short, descriptive, under 50 characters, kebab-case
10. **Select a different real-world scenario** each time for variety
"""
PROMPT_REGISTRY = {
    "ReactJs (BASIC)": [
        PROMPT_REACT_BASIC_CONTEXT,
        PROMPT_REACT_BASIC_INPUT_AND_ASK,
        PROMPT_REACT_BASIC,
    ]
}
