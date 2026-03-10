PROMPT_NEXTJS_TYPESCRIPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_NEXTJS_TYPESCRIPT_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Next.js and TypeScript, you are given a list of real world scenarios and proficiency levels for Next.js + TypeScript.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with the proficiency level required in the competency definition, ensuring that no two questions generated are similar. 
- For BEGINNER and BASIC and INTERMEDIATE levels of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible for these levels.
- For ADVANCED and EXPERT levels of proficiency, the questions must be more open ended, require application of fundamental concepts and complex according to proficiency. The scenarios must also be complex and challenging for these levels.
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to the latest Next.js best practices and TypeScript versions. Strictly avoid using outdated versions of Next.js (below 13) or TypeScript in the code scenarios.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks for every proficiency level should reflect this, requiring genuine engineering and problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Next.js + TypeScript task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for proficiency level and years of experience given as input, keeping in mind that AI assistance is allowed.
- Tests practical Next.js + TypeScript skills that require more than a simple AI query to solve, even while keeping the competency scope and proficiency level in mind.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- If we are expecting from the user the app route implementation, ensure that the code files and structure do not reflect that.
- Complete app route structure should included when we are not expecting the user to implement app route structure or when already an complex implementation is expected from the user.

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `npm run dev`.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the proficiency levels given as input.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Next.js + TypeScript starter code should include basic project structure but NOT require complex infrastructure setup (advanced Docker configurations, complex CI/CD, etc.)

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A short description of the task scenario including the specific ask from the candidate — what needs to be fixed/implemented?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Next.js and Node.js exclusions",
      "package.json": "Node.js dependencies and scripts",
      "tsconfig.json": "TypeScript configuration for Next.js",
      "next.config.js": "Next.js configuration",
      "tailwind.config.js": "Tailwind CSS configuration (if applicable)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion in 2-3 lines. Use simple english.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task. Mention things like Node.js 18+, npm/yarn, Git, TypeScript knowledge, Next.js familiarity, etc.",
  "answer": "High-level solution approach",
  "hints": "a single line hint on what a good approach to solve the task could include. These hints must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}
 
## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow Next.js and TypeScript best practices
- Use proper TypeScript interfaces and types throughout
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core business logic functions, React components, API routes, or TypeScript interfaces that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions e.g. 
- DO NOT include comments like "Add logic here" or "Should implement loading states" etc.
- DO NOT add comments that give way hints or solution or implementation details
"

- The generated project structure should be runnable `, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Have a sensible gitignore suited for Next.js + TypeScript projects:
- node_modules/
- .next/
- out/
- build/
- .env*.local
- .DS_Store
- *.tsbuildinfo
- next-env.d.ts
- .vercel
- .swc/
- *.log
- npm-debug.log*
- yarn-debug.log*
- yarn-error.log*

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Objectives
   - How to Verify
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- do not give way any specific method for route and any file locations for implementation just provide the general guidance for any implementation

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario, current situation. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why it matters.

### Helpful Tips
  - Project context and guidance points
  - General architectural notes and best practices
  - Important considerations for the implementation

### Objectives
  - Clear, measurable goals for the candidate
  - This is what the candidate should be able to do successfully to say that they have completed the task.
  - These objectives will also be used to verify the task completion and award points.
  - What functionality should be implemented, expected behavior

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points.

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, npm run dev, etc.)
  - Direct solutions or hints
  - Step-by-step implementation guides
  - Specific TypeScript syntax examples
  - direct answers and code snippets that would give away the solution to the task
  - any routes also shouldn't be included
  - any specific files implementation details that would give away the solution to the task
  - should not provide any particular method or approach to implement the solution

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case
3. **code_files** must include README.md, .gitignore, package.json, tsconfig.json, and Next.js source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable with `npm run dev` but must NOT contain the solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Next.js/TypeScript terms
8. **Task must be completable within the allocated time** for BASIC proficiency
9. **NO comments in code** that reveal the solution or give hints
10. **Use Next.js 13+ and TypeScript** conventions throughout
"""

PROMPT_NEXTJS_TYPESCRIPT_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Next.js and TypeScript assessment task.

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
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Next.js and TypeScript proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_REGISTRY = {
    "NextJs (BASIC), TypeScript (BASIC)": [
        PROMPT_NEXTJS_TYPESCRIPT_CONTEXT,
        PROMPT_NEXTJS_TYPESCRIPT_INPUT_AND_ASK,
        PROMPT_NEXTJS_TYPESCRIPT_INSTRUCTIONS,
    ]
}
