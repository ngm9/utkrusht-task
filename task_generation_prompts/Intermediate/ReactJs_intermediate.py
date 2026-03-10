PROMPT_REACT_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACT_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React.js assessment task.

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
2. What will the task look like? (Describe the type of React.js implementation or fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in React and modern JavaScript ecosystem, you are given a list of real world scenarios and proficiency levels for React development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years React experience), ensuring that no two questions generated are similar. 
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced Component Design**: Higher-order components, render props, compound components
  - **State Management Architecture**: Context API with reducers, custom hooks for state logic, prop drilling solutions
  - **Performance Optimization**: React.memo, useMemo, useCallback, code splitting, lazy loading
  - **Advanced Hooks Usage**: useReducer, useContext, useRef, useImperativeHandle, custom hooks
  - **Project Architecture**: Folder structure design, separation of concerns, modular design
  - **Error Handling**: Error boundaries, graceful degradation, user feedback patterns
  - **Testing Considerations**: Component testability, mock-friendly design
  - **Code Quality**: Modern JavaScript/ES6+ features, prop validation, clean code principles
  - **Real-world Patterns**: Data fetching patterns, caching strategies, form management
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern React best practices (React 18+) and current JavaScript standards. Use functional components with hooks exclusively.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate React proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a React task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years React experience), keeping in mind that AI assistance is allowed.
- Tests practical React skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-component applications that require thoughtful state management and component communication
- Should test the candidate's ability to structure a scalable React application

## Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills
- The code files generated must be valid and executable with `npm start`.
- Provide a realistic project structure that mimics real-world applications
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper folder structure, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper component design and state management
- React starter code should include realistic project structure but NOT require complex infrastructure setup
- Include some existing components/utilities that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architecture

# OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - package.json (Node.js dependencies including React, and other dependencies required in the scenario)
  - .gitignore (Standard React project gitignore)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial architecture that candidate needs to complete/extend
  - Include realistic folder structure (components/, hooks/, utils/, constants/, etc.)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed? Include architectural considerations and requirements.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Guidance, Objectives, and How to Verify",
      ".gitignore": "Proper React and Node.js exclusions",
      "package.json": "Node.js dependencies and scripts with intermediate-level packages",
      "public/index.html": "HTML entry point (if needed)",
      "src/index.js": "React app entry point",
      "src/App.js": "Main App component",
      "src/components/ComponentName.js": "Component files as needed",
      "src/hooks/useCustomHook.js": "Custom hook files as needed",
      "src/utils/utilityFile.js": "Utility files as needed",
      "src/types/types.js": "Type definitions or constants (if needed)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion focusing on architectural quality, performance, and code organization. 3-4 lines describing both functional and architectural outcomes.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like modern JavaScript knowledge, React patterns understanding, testing familiarity, etc.",
  "answer": "High-level solution approach with emphasis on architectural decisions and design patterns",
  "hints": "a single line hint focusing on architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

 
## Code file requirements:
- Generate realistic folder structure (src/components/, src/hooks/, src/utils/, src/constants/, etc.)
- Code should follow modern React best practices and demonstrate intermediate-level patterns
- Use functional components with hooks exclusively, including advanced hooks usage
- Focus on modern JavaScript/ES6+ features and React best practices
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing components/utilities that need to be extended or integrated
- The core architectural decisions, advanced component patterns, performance optimizations, or state management solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add optimization here" or "Should implement custom hook" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable, but will require architectural completion to function properly
- Provide realistic dependencies in package.json that intermediate developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate React projects including node modules, build directories, environment files, log files, IDE configurations, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Guidance
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- Do not give away any specific implementation details or architectural decisions that would hint at the solution

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why architectural considerations matter for this use case. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper architecture is crucial.

### Helpful Tips
  - Project context and guidance points suitable for intermediate level React developers
  - Architectural considerations and design pattern suggestions
  - Important considerations for the implementation focusing on:
    - Component architecture and reusability patterns
    - State management strategies and data flow
    - Performance optimization opportunities
    - Error handling and user experience
    - Code organization and maintainability
    - Testing and debugging considerations
  - Quality expectations for intermediate-level work

### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate level
  - This is what the candidate should be able to do successfully to say that they have completed the task.
  - These objectives will also be used to verify the task completion and award points.
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and code quality metrics
  - Include expectations for folder structure, component design, and performance

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and architecture
  - Code quality checkpoints (component structure, performance, error handling)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points.
  - Include both functional testing and architectural assessment criteria
  - Performance and user experience validation points

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, npm start, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific React patterns or hook implementations
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific files implementation details that would give away the solution to the task
  - Should not provide any particular architectural approach or design pattern to implement the solution
  - Component names or specific implementation strategies that would reveal the solution
  - Folder structure decisions that would dictate the architectural approach
"""
PROMPT_REGISTRY = {
    "ReactJs (INTERMEDIATE)": [
        PROMPT_REACT_INTERMEDIATE_CONTEXT,
        PROMPT_REACT_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_REACT_INTERMEDIATE_INSTRUCTIONS,
    ]
}
