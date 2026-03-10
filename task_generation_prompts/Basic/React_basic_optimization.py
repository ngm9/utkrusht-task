PROMPT_REACT_OPTIMIZATION_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_REACT_OPTIMIZATION_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Pandas/NumPy assessment task.

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

1. What will the task be about? (Describe the business domain, data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of data manipulation/analysis required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_REACT_OPTIMIZATION ="""
# React + TypeScript Optimization Task Requirements

## GOAL
As a technical architect super experienced in React and TypeScript, you are given real-world scenarios and proficiency levels for React development. Your job is to generate an entire task definition, including TypeScript code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to optimize existing TypeScript React code
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- **Time Constraint**: Each task MUST be completable within 30 minutes by a candidate with BASIC proficiency (1-2 years React experience)

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL STARTER CODE

**TYPESCRIPT IMPLEMENTATION REQUIREMENTS:**
- **ALL code files MUST use TypeScript** (.tsx for components, .ts for utilities)
- **MUST include a valid tsconfig.json** with proper React and TypeScript configurations
- **MUST include proper type definitions** for props, state, API responses, and function parameters
- **Basic TypeScript features MUST be implemented**: interfaces, types, type annotations, return types
- **NO TypeScript errors** - The application must compile without any type errors
- **NO 'any' types** - All types must be properly defined (components, functions, API responses, event handlers)
- **Package.json MUST include TypeScript dependencies**: typescript, @types/react, @types/react-dom, @types/node

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working React + TypeScript application** that runs successfully immediately after `npm install` and `npm start`
- **ZERO compilation errors, ZERO TypeScript errors, ZERO runtime errors, ZERO warnings**
- **All UI must render correctly** - Every component, page, and UI element must display properly
- **All existing functionality must work** - API calls execute, data loads and displays, user interactions work, forms submit
- **The candidate should NOT need to fix anything to make the app run** - The app is already fully functional

**CRITICAL REQUIREMENTS FOR UNOPTIMIZED CODE:**
- **DO NOT include ANY performance optimizations** - NO React.memo, NO useMemo, NO useCallback, NO request caching, NO request batching, NO debouncing, NO throttling, NO virtualization, NO lazy loading, NO code splitting
- **The code must be intentionally inefficient but functionally correct** - Perfect functionality but poor performance under load
- **The candidate's task is ONLY to optimize the working application** - Identify bottlenecks and implement optimizations, NOT fix broken functionality

### Task Complexity Requirements

**SCOPE FOR 30-MINUTE COMPLETION:**
- Task must be achievable within 30 minutes by a BASIC level candidate
- Focus on 2-3 specific optimization areas maximum
- Provide a working application with clear, identifiable performance issues
- Optimization should focus on fundamental React patterns, not complex architectural changes
- Examples of appropriate 30-minute optimizations:
  - Reduce unnecessary re-renders in a component tree (3-5 components)
  - Implement basic memoization for expensive computations
  - Optimize data fetching to reduce redundant API calls
  - Add request deduplication for concurrent identical requests
  - Implement basic virtualization for a single list component
  - Add proper React.memo usage to prevent cascading updates

**INAPPROPRIATE FOR 30-MINUTE TASKS:**
- Complete application architecture redesign
- Implementing complex state management solutions (Redux, Zustand)
- Building comprehensive caching layers
- Multiple simultaneous optimization areas requiring deep analysis
- Complex TypeScript refactoring or advanced type system features
- Building custom hooks frameworks or complex abstractions

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- Complete React + TypeScript project structure (standard Create React App with TypeScript template)
- **Valid tsconfig.json** with proper compiler options for React
- **Valid package.json** with all TypeScript dependencies and development scripts
- All files using TypeScript extensions (.tsx, .ts)
- Proper type definitions for all components, props, state, and functions
- Basic TypeScript features properly implemented (interfaces, types, type annotations)
- Working components with complete TypeScript implementation
- Functional API calls with properly typed responses
- Working state management with proper TypeScript types
- All necessary imports and exports with correct types
- Valid TSX syntax throughout
- **All standard development scripts**: start, build, test, eject

**WHAT MUST NOT BE INCLUDED:**
- **NO optimization techniques**: NO React.memo, NO useMemo, NO useCallback
- **NO efficient patterns**: NO caching, NO deduplication, NO batching, NO debouncing, NO throttling
- **NO performance enhancements**: NO virtualization, NO lazy loading, NO code splitting
- **NO comments of any kind**: NO TODO, NO hints, NO "optimize this", NO placeholder comments
- **NO advanced TypeScript patterns**: Focus on basic types, interfaces, and annotations only

### AI and External Resource Policy
- Candidates are permitted to use external resources including AI tools, documentation, Stack Overflow
- Tasks assess ability to find, understand, integrate, and adapt solutions
- Complexity should require genuine problem-solving beyond simple copy-pasting

### Code Generation Instructions
Based on real-world scenarios, create a React + TypeScript task that:
- Draws inspiration from input scenarios for business context
- Matches BASIC proficiency level (1-2 years React + TypeScript experience)
- **Can be completed within 30 minutes**
- Tests practical React + TypeScript optimization skills
- Focuses on fundamental concepts with clear, measurable performance issues
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "react-ts-dashboard-optimization")

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "question": "Short description of the scenario and specific optimization requirements",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive React/TypeScript/Node.js exclusions",
    "package.json": "All dependencies including TypeScript, @types packages, and all development scripts",
    "tsconfig.json": "Proper TypeScript configuration for React",
    "public/index.html": "HTML entry point",
    "public/manifest.json": "Web app manifest",
    "public/robots.txt": "Robots.txt file",
    "src/index.tsx": "React app entry point with TypeScript",
    "src/App.tsx": "Main App component with TypeScript",
    "src/react-app-env.d.ts": "React App environment types",
    "src/types.ts": "Type definitions and interfaces",
    "additional_file.tsx": "Other component files with TypeScript",
    "additional_file_2.ts": "Utility files with TypeScript"
  }},
  "outcomes": "Bullet-point list in simple language. Must include: 'Optimize React + TypeScript application performance by implementing efficient rendering patterns, reducing unnecessary re-renders, and improving data fetching strategies' and 'Write production-level clean code with best practices including proper TypeScript types, naming conventions, error handling, and performance optimization techniques'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level performance problem in a business context, (2) the specific optimization goal, and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include understanding of React rendering behavior and performance optimization techniques, including identifying unnecessary re-renders and improving data-fetching efficiency without changing user-visible behavior",
  "answer": "High-level solution approach describing optimization strategies",
  "hints": "Single line suggesting focus area. Example: 'Focus on React rendering patterns, component memoization, and TypeScript-safe API request optimization to improve performance under concurrent load'",
  "definitions": {{
    "React.memo": "React API for memoizing functional components",
    "useMemo": "React hook for memoizing expensive computations",
    "useCallback": "React hook for memoizing callback functions",
    "Type Guard": "TypeScript technique for narrowing types",
    "Interface vs Type": "TypeScript type definition approaches"
  }}
}}

## README.md STRUCTURE (React + TypeScript Optimization)

### Task Overview (MANDATORY - 2-3 substantial sentences)

**CRITICAL**: Describe the specific business scenario where a React + TypeScript application is experiencing performance issues. Explain that the application is fully functional and type-safe, but suffers from performance problems under load (e.g., unnecessary re-renders, redundant API calls, slow UI updates). Connect the business problem (real-time dashboard, analytics UI, high-traffic SaaS) to the need for optimization. Make clear this is a **30-minute optimization task** focusing on specific, achievable improvements.

### Helpful Tips

Practical guidance without revealing implementations:

- Consider how React's rendering cycle impacts performance
- Think about when components unnecessarily re-render
- Review how API calls are triggered and if they're duplicated
- Consider TypeScript's role in maintaining type safety during optimization
- Explore React's built-in optimization hooks
- Think about data flow and prop passing patterns
- Review browser DevTools for performance profiling
- Consider component composition and responsibility separation
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions

### Objectives

Define goals focusing on outcomes for a 30-minute optimization task:

- Reduce unnecessary component re-renders in the application
- Optimize API call patterns to eliminate redundancy
- Improve UI responsiveness under typical load conditions
- Maintain TypeScript type safety while implementing optimizations
- Apply React performance best practices to critical rendering paths
- Measure and verify performance improvements

**CRITICAL**: Scope should be achievable in 30 minutes

### How to Verify

Verification approaches for 30-minute optimizations:

- Use React DevTools Profiler to measure render frequency before and after
- Monitor network tab to verify reduced API call count
- Interact with UI elements and observe responsiveness improvements
- Confirm TypeScript compilation remains error-free
- Verify all existing functionality still works correctly
- Check console for any new warnings or errors
- Measure specific metrics (e.g., render count, API call count) before/after

**CRITICAL**: Focus on measurable, verifiable improvements

### NOT TO INCLUDE:
- Step-by-step implementation instructions
- Exact code solutions
- Configuration examples
- Specific library recommendations beyond React built-ins
- Complex architectural patterns
- Phrases like "you should implement", "add the following code"


## TYPESCRIPT CONFIGURATION REQUIREMENTS

### tsconfig.json MUST include:
{{
  "compilerOptions": {{
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "esnext"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  }},
  "include": [
    "src"
  ]
}}

### package.json MUST include:
{{
  "name": "task-name",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
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




## CRITICAL REMINDERS

1. **ALL files must use TypeScript** (.tsx, .ts extensions)
2. **NO 'any' types** - proper type definitions required
3. **Application must run perfectly** with `npm install` && `npm start`
4. **NO TypeScript compilation errors**
5. **Task must be completable in 30 minutes**
6. **Focus on 2-3 specific optimization areas**
7. **Code must be unoptimized but fully functional**
8. **NO comments that reveal solutions**
9. **Proper TypeScript configurations in tsconfig.json**
10. **All required @types packages in package.json**
11. **Use standard Create React App with TypeScript template structure**
12. **All development scripts must be present**: start, build, test, eject
13. **Include all standard CRA files**: public/index.html, public/manifest.json, public/robots.txt, src/react-app-env.d.ts
14. **Entry point must be src/index.tsx**
15. **Must use react-scripts for all operations**
"""
PROMPT_REGISTRY = {
    "ReactJs - Optimization (BASIC)": [
        PROMPT_REACT_OPTIMIZATION_CONTEXT,
        PROMPT_REACT_OPTIMIZATION_INPUT_AND_ASK_BASIC,
        PROMPT_REACT_OPTIMIZATION,
    ]
}
