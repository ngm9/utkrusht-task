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
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an **INTERMEDIATE LEVEL (3-5 years of experience)**.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch or fix bugs in the existing code, with **moderate complexity requiring architectural decisions**.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- **For INTERMEDIATE level proficiency (3-5 years experience)**: Tasks should involve multiple interconnected components, require understanding of Next.js architecture patterns (App Router, Server Components, Client Components), state management considerations, API design, TypeScript generics and advanced types, performance optimization basics, and proper error handling strategies.
- **Complexity expectations**: The task should require candidates to make architectural decisions, implement custom hooks, handle complex data flows, work with multiple API endpoints, implement proper loading and error states, use TypeScript effectively for type safety, and demonstrate understanding of Next.js rendering strategies.
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to the latest Next.js best practices and TypeScript versions. Strictly avoid using outdated versions of Next.js (below 13) or TypeScript in the code scenarios.
- **Advanced patterns expected**: Server Actions, Suspense boundaries, proper data fetching patterns, middleware usage, dynamic imports, and optimization techniques.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- **For intermediate level**: The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem that requires architectural thinking and multiple technology integrations, rather than testing rote memorization. The complexity should require genuine engineering and problem-solving skills that go well beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Next.js + TypeScript task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- **Matches intermediate complexity (3-5 years experience)**: Should involve multiple components working together, API integrations, state management, performance considerations, and advanced TypeScript usage.
- Tests practical Next.js + TypeScript skills that require more than a simple AI query to solve, including architectural decisions and best practices implementation.
- **Time constraints: Each task should be finished within 45-90 minutes** (increased from basic level).
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **Expected technical depth**: Implementation should require understanding of App Router, Server Components vs Client Components, data fetching strategies, TypeScript generics, custom hooks, error boundaries, and performance optimization.
- Complete app route structure should be included when we are not expecting the user to implement app route structure or when already a complex implementation is expected from the user.

## TASK NAME:
- The task name should be consive
## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `npm run dev`.
- **For intermediate level**: Provide a more comprehensive project structure with multiple files, but leave the core business logic, complex components, and advanced features unimplemented.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- **If the task is to fix bugs**: Make sure the starter code has logical bugs that require understanding of Next.js lifecycle, TypeScript type issues, or architectural problems (not just syntactic errors).
- **If the task is to implement a feature from scratch**: Provide a solid foundation with proper project structure, but leave the complex implementations for the candidate.
- **Advanced setup expectations**: Include configurations for TypeScript strict mode, proper Next.js App Router structure, and modern development tools.

# OUTPUT

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - package.json (Node.js dependencies including Next.js 14+, TypeScript, React, and other dependencies required in the scenario)
  - tsconfig.json (TypeScript configuration optimized for Next.js with strict mode enabled)
  - next.config.js (Next.js configuration file with intermediate-level configurations)
  - .gitignore (Ignore node_modules/, .next/, out/, .env*.local, *.log, .DS_Store)
  - tailwind.config.js (if styling with Tailwind CSS is required)
  - **Multiple code files** that provide a solid foundation but require significant implementation from the candidate
  - Code files should not contain solution hints but should demonstrate proper project architecture

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be fixed/implemented? Should be more comprehensive than basic level tasks.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Guidance, Objectives, and How to Verify",
      ".gitignore": "Proper Next.js and Node.js exclusions",
      "package.json": "Node.js dependencies and scripts",
      "tsconfig.json": "TypeScript configuration for Next.js with strict mode",
      "next.config.js": "Next.js configuration",
      "tailwind.config.js": "Tailwind CSS configuration (if applicable)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2",
      "additional_files": "Additional files as needed for intermediate complexity"
  }},
  "outcomes": "Expected results after completion in 3-4 lines describing the functional application with multiple features working together. Use simple english.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Should include: Node.js 18+, npm/yarn, Git, **solid TypeScript knowledge**, **Next.js 13+ App Router familiarity**, **React hooks and state management understanding**, **API design principles**, etc.",
  "answer": "Comprehensive high-level solution approach covering architecture, implementation strategy, and key technical decisions",
  "hints": "A strategic hint focusing on architectural approach or key concept that guides thinking without revealing implementation details. Should help intermediate developers identify the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    "advanced_concept_1": "definition_for_intermediate_level_concept",
    "advanced_concept_2": "definition_for_intermediate_level_concept"
    }}
}}
 
## Code file requirements:
- **Multiple files required** (minimum 4-6 files) to reflect intermediate complexity
- Code should follow Next.js and TypeScript best practices with advanced patterns
- **Extensive use of TypeScript**: Proper interfaces, types, generics where appropriate, strict type checking
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should provide comprehensive boilerplate, proper project architecture, and foundation code.
- **Advanced patterns to leave unimplemented**: Complex business logic, data transformation functions, advanced React components, API route handlers, custom hooks, error handling strategies, performance optimizations.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement loading states" etc.
- DO NOT add comments that give away hints or solution or implementation details
- **The generated project should demonstrate intermediate-level architecture** but require significant implementation to be functional.

## .gitignore INSTRUCTIONS:Standard next project gitignore


## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Guidance
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content appropriate for intermediate level
- Task Overview section MUST contain detailed business scenario (3-4 sentences) explaining the technical context and business requirements
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- **Use complex business context** that requires architectural thinking and multiple technical considerations
- Do not give away any specific implementation methods, routes, or file locations - provide general architectural guidance

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the complex business scenario, current technical landscape, integration requirements, and business impact. 
NEVER generate empty content - always provide substantial business context that explains the technical challenges and business requirements the candidate needs to address.

### Helpful Tips
  - **Advanced project context** and architectural guidance points
  - **Technical architecture notes** covering Next.js patterns, TypeScript best practices, performance considerations
  - **Important considerations** for scalability, maintainability, user experience, and technical debt
  - **Integration patterns** and data flow considerations

### Objectives
  - **Clear, measurable technical goals** appropriate for intermediate developers
  - **Multiple interconnected objectives** that test various aspects of Next.js and TypeScript knowledge
  - **What functionality should be implemented**: Complex features with proper error handling, loading states, and user experience considerations
  - **Expected technical depth**: Proper component architecture, type safety, performance optimization, and code organization

### How to Verify
  - **Comprehensive checkpoints** covering functionality, code quality, performance, and user experience
  - **Technical validation points**: TypeScript compilation, proper error handling, responsive behavior, data flow
  - **Observable behaviors** that demonstrate intermediate-level implementation quality
  - **Code quality indicators** that help assess architectural decisions and best practices implementation

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, npm run dev, etc.)
  - Direct solutions or implementation hints
  - Step-by-step implementation guides
  - Specific TypeScript syntax examples or code snippets
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific files implementation details that would give away the solution to the task
  - Should not provide any particular architectural approach or design pattern to implement the solution
  
  - Specific routes, file paths, or implementation details
  - Particular methods or approaches that would reveal the solution strategy

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
2. What will the task look like? (Describe the type of Next.js and TypeScript implementation or fix required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_REGISTRY = {}
