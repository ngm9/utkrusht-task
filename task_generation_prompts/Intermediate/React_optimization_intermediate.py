PROMPT_REACT_OPTIMIZATION_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_REACT_OPTIMIZATION_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React and TypeScript optimization assessment task.

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
2. What will the task look like? (Describe the type of React and TypeScript optimization required, the expected deliverables, and how it aligns with the given proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""
PROMPT_REACT_OPTIMIZATION_INTERMEDIATE= """
# React + TypeScript Optimization Task Requirements (INTERMEDIATE Level)

## GOAL
As a technical architect super experienced in React and TypeScript, you are given real-world scenarios and proficiency levels for React development. Your job is to generate an entire task definition, including TypeScript code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to optimize existing TypeScript React code
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context
- **Time Constraint**: Each task MUST be completable within 30-45 minutes by a candidate with INTERMEDIATE proficiency (3-5 years React experience)
- **Complexity Level**: Tasks should require deeper understanding of React internals, advanced TypeScript patterns, and architectural decision-making

### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL STARTER CODE

**TYPESCRIPT IMPLEMENTATION REQUIREMENTS:**
- **ALL code files MUST use TypeScript** (.tsx for components, .ts for utilities)
- **MUST include a valid tsconfig.json** with proper React and TypeScript configurations including strict mode enabled
- **MUST include proper type definitions** for props, state, API responses, function parameters, custom hooks, context providers, and higher-order components
- **INTERMEDIATE TypeScript features MUST be implemented**: generics, union types, intersection types, type guards, utility types (Partial, Pick, Omit, Record), conditional types where applicable
- **NO TypeScript errors** - The application must compile without any type errors
- **NO 'any' types** - All types must be properly defined with appropriate specificity (components, functions, API responses, event handlers, custom hooks, higher-order components, context values)
- **Package.json MUST include TypeScript dependencies**: typescript, @types/react, @types/react-dom, @types/node, and any additional @types packages for third-party libraries used
- **Advanced type patterns**: Proper typing for custom hooks with generics, discriminated unions for complex state, mapped types where appropriate
- **IMPORTANT FOR TASK DESIGN**: While the starter code must be fully runnable and type-safe overall, you SHOULD intentionally leave a few non-critical type definitions (for example, some derived state types, secondary utility function generics, or less central context value refinements) for the candidate to improve or complete as part of the exercise, and clearly call this out in the candidate-facing README description (without revealing exact solutions).

**FUNCTIONAL APPLICATION REQUIREMENTS:**
- **The starter code MUST be a complete, working React + TypeScript application** that runs successfully immediately after `npm install` and `npm start`
- **ZERO compilation errors, ZERO TypeScript errors, ZERO runtime errors, ZERO warnings**
- **All UI must render correctly** - Every component, page, and UI element must display properly
- **All existing functionality must work** - API calls execute, data loads and displays, user interactions work, forms submit, state management functions correctly
- **The candidate should NOT need to fix anything to make the app run** - The app is already fully functional
- **Application must include multiple interconnected features** - Multiple pages/views, complex state management, data dependencies between components

**CRITICAL REQUIREMENTS FOR UNOPTIMIZED CODE:**
- **DO NOT include ANY performance optimizations** - NO React.memo, NO useMemo, NO useCallback, NO request caching, NO request batching, NO debouncing, NO throttling, NO virtualization, NO lazy loading, NO code splitting, NO dynamic imports
- **DO NOT include efficient state management patterns** - NO normalized state, NO selector optimization, NO state colocation, NO context splitting
- **The code must be intentionally inefficient but functionally correct** - Perfect functionality but poor performance under load with multiple performance bottlenecks
- **The candidate's task is ONLY to optimize the working application** - Identify bottlenecks and implement optimizations, NOT fix broken functionality
- **Include architectural inefficiencies** - Prop drilling, context value recreation, unnecessary component coupling, inefficient data structures

### Task Complexity Requirements

**SCOPE FOR 30-45 MINUTE COMPLETION:**
- Task must be achievable within 30-45 minutes by an INTERMEDIATE level candidate
- Focus on 4-6 specific optimization areas that require analytical thinking
- Provide a working application with multiple interrelated performance issues
- Optimization should require architectural understanding and strategic decision-making
- Examples of appropriate 30-45 minute optimizations:
  - Optimize complex component trees (8-15 components) with multiple re-render cascades
  - Implement strategic memoization across custom hooks and utility functions
  - Refactor inefficient state management patterns (context optimization, state normalization)
  - Build request caching layer with cache invalidation strategy
  - Implement request deduplication and batching for multiple concurrent API calls
  - Add virtualization for multiple large lists with different data types
  - Optimize expensive computations across multiple components
  - Implement code splitting strategy for route-based or component-based lazy loading
  - Refactor context providers to prevent unnecessary re-renders
  - Optimize data transformation and filtering pipelines

**APPROPRIATE FOR INTERMEDIATE TASKS:**
- Analyzing and optimizing component hierarchies requiring architectural changes
- Implementing custom hooks for optimization logic (e.g., useDebounce, useThrottle, useMemoizedCallback)
- Building caching mechanisms with TypeScript-safe implementations
- Optimizing complex data flows and state dependencies
- Implementing performance monitoring and measurement strategies
- Making architectural decisions about state management optimization
- Advanced TypeScript patterns for performance (generics in hooks, proper typing for memoized values)
- Balancing multiple optimization strategies simultaneously

**INAPPROPRIATE FOR 30-45 MINUTE TASKS:**
- Complete migration to different state management libraries (Redux, Zustand, Recoil)
- Building entire custom framework or abstraction layer
- Implementing server-side rendering or complex SSR optimizations
- Building comprehensive testing suite for optimizations
- Complete TypeScript refactor to advanced patterns unrelated to performance
- Database or backend optimization
- Implementing complex animation optimization frameworks

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- Complete React + TypeScript project structure (standard Create React App with TypeScript template)
- **Valid tsconfig.json** with strict mode and proper compiler options for React
- **Valid package.json** with all TypeScript dependencies, development scripts, and any third-party libraries (properly typed)
- All files using TypeScript extensions (.tsx, .ts)
- Proper type definitions for all components, props, state, functions, custom hooks, and context providers
- Intermediate TypeScript features properly implemented (generics, union types, type guards, utility types)
- Working components with complete TypeScript implementation across multiple pages/features
- Functional API calls with properly typed responses using interfaces or types
- Working state management (Context API, local state) with proper TypeScript types
- Custom hooks with proper TypeScript generics and return type annotations
- All necessary imports and exports with correct types
- Valid TSX syntax throughout
- **All standard development scripts**: start, build, test, eject
- Multiple interconnected features requiring optimization across boundaries
- Complex data structures that benefit from normalization or transformation

**WHAT MUST NOT BE INCLUDED:**
- **NO optimization techniques**: NO React.memo, NO useMemo, NO useCallback, NO custom optimization hooks
- **NO efficient patterns**: NO caching, NO deduplication, NO batching, NO debouncing, NO throttling, NO request queuing
- **NO performance enhancements**: NO virtualization, NO lazy loading, NO code splitting, NO dynamic imports
- **NO comments of any kind**: NO TODO, NO hints, NO "optimize this", NO placeholder comments, NO performance suggestions
- **NO efficient state patterns**: NO normalized state, NO memoized selectors, NO context splitting, NO state colocation
- **NO advanced optimization patterns**: Keep TypeScript patterns functional but not optimized for performance
- **NO fully optimized code**: The code must be intentionally inefficient but functionally correct

### AI and External Resource Policy
- Candidates are permitted to use external resources including AI tools, documentation, Stack Overflow
- Tasks assess ability to find, understand, integrate, and adapt solutions with deeper analysis
- Complexity should require genuine problem-solving, architectural thinking, and strategic optimization beyond simple copy-pasting
- Candidates should demonstrate ability to evaluate trade-offs between different optimization approaches

### Code Generation Instructions
Based on real-world scenarios, create a React + TypeScript task that:
- Draws inspiration from input scenarios for business context
- Matches INTERMEDIATE proficiency level (3-5 years React + TypeScript experience)
- Can be completed within 30-45 minutes
- Tests practical React + TypeScript optimization skills with architectural considerations
- Focuses on multiple interconnected optimization opportunities requiring strategic thinking
- Includes measurable performance issues across different application layers
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "react-ts-analytics-platform-optimization")
- **CRITICAL - FILE NAMING**: All additional component, page, hook, context, and utility files MUST use meaningful, scenario-specific file names derived from the task (e.g., OrdersDashboard.tsx, AnalyticsChart.tsx, useOrders.ts, CartContext.tsx). NEVER use generic placeholder names like PageA, ComponentA, useCustomHook, SomeContext, or helpers.ts when a scenario-specific name is appropriate. File names should reflect the business domain and feature so generated code is identifiable and varies correctly per task.

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name",
   "question": "A detailed description of the React + TypeScript optimization task scenario including the specific performance challenges, architectural considerations, and what exactly the candidate needs to analyze and optimize.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Guidance, Objectives, and How to Verify for a React + TypeScript optimization scenario",
      ".gitignore": "Comprehensive React/TypeScript/Node.js exclusions",
      "package.json": "All dependencies including React, TypeScript, @types packages, third-party libraries, and all development scripts",
      "tsconfig.json": "Proper TypeScript configuration for React with strict mode",
      "public/index.html": "HTML entry point",
      "public/manifest.json": "Web app manifest",
      "public/robots.txt": "Robots.txt file",
      "src/index.tsx": "React app entry point with TypeScript",
      "src/App.tsx": "Main App component with TypeScript and routing/navigation",
      "src/react-app-env.d.ts": "React App environment types",
      "src/types.ts": "Type definitions and interfaces with intermediate TypeScript patterns",
      "src/components/ComponentName.tsx": "Component files as needed, using scenario-specific names (e.g. OrdersDashboard.tsx, AnalyticsChart.tsx) instead of generic placeholders",
      "src/hooks/useCustomHook.ts": "Custom hook files as needed, using scenario-specific names (e.g. useOrders.ts, useAnalyticsFilters.ts) instead of generic placeholders",
      "src/utils/utilityFile.ts": "Utility files as needed (e.g. formatCurrency.ts, calculateAverages.ts)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion focusing on performance improvements, architectural quality, and code organization. 3-4 lines describing both functional and optimization-focused outcomes, including the ability to analyze bottlenecks, apply React + TypeScript optimization techniques, and maintain clean, scalable architecture.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include expectations such as strong understanding of React rendering behavior, TypeScript basics and intermediate patterns, performance profiling tools, React optimization hooks, and architectural thinking.",
  "answer": "High-level solution approach with emphasis on which parts of the application to profile, what optimization techniques to apply, and how to balance performance, readability, and maintainability without exposing exact implementation details.",
  "hints": "A single line hint focusing on where to start optimization (e.g., component tree analysis, state management, data fetching) and suggesting architectural thinking without giving away the answer.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

## README.md STRUCTURE (React + TypeScript Optimization - INTERMEDIATE)

- The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify
   - Helpful Tips
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview (MANDATORY - 3-4 substantial sentences)
**CRITICAL**: Describe the specific business scenario where a React + TypeScript application is experiencing significant performance issues across multiple areas. Explain that the application is fully functional and type-safe, but suffers from complex performance problems under realistic load (e.g., cascading re-renders across features, redundant API calls from multiple sources, slow UI updates affecting user experience, inefficient state management). Connect the business problem (real-time analytics platform, complex SaaS dashboard, data-intensive application, multi-feature enterprise tool) to the need for comprehensive optimization requiring architectural thinking. Make clear this is a 30-45 minute optimization task focusing on multiple interconnected improvements requiring analysis and strategic decision-making.

### Objectives
Define goals focusing on outcomes for a 30-45 minute optimization task requiring architectural understanding:

- Analyze and identify performance bottlenecks across multiple application areas using profiling tools
- Reduce unnecessary component re-renders throughout complex component hierarchies
- Optimize state management patterns to prevent cascading updates
- Refactor API call patterns to eliminate redundancy and implement efficient caching strategies
- Implement strategic memoization across components, hooks, and utility functions
- Optimize context providers to minimize unnecessary consumer re-renders
- Improve UI responsiveness under realistic load conditions across all features
- Maintain TypeScript type safety while implementing architectural optimizations
- Apply advanced React performance best practices to critical rendering paths
- Make informed trade-off decisions between different optimization approaches
- Measure and verify performance improvements with quantitative metrics
- Ensure optimizations maintain code readability and maintainability

**CRITICAL**: Scope should be achievable in 30-45 minutes with multiple interconnected optimization opportunities

### How to Verify
Verification approaches for intermediate-level optimizations with quantitative measurement:

- Use React DevTools Profiler to measure render frequency, render duration, and component hierarchy performance before and after optimizations
- Monitor network tab to verify reduced API call count and identify request patterns
- Measure initial load time and time-to-interactive metrics
- Interact with all UI features and observe responsiveness improvements across the application
- Confirm TypeScript compilation remains error-free with no type safety regressions
- Verify all existing functionality still works correctly across all features
- Check console for any new warnings or errors introduced by optimizations
- Measure specific quantitative metrics (render count per interaction, API call count, computation time, memory usage) before/after
- Test edge cases and high-load scenarios to verify optimization effectiveness
- Profile expensive operations to confirm optimization impact
- Verify that optimizations maintain code readability and don't introduce complexity debt

**CRITICAL**: Focus on measurable, verifiable improvements with comprehensive testing

### Helpful Tips
Practical guidance without revealing implementations, geared toward intermediate-level analytical thinking:

- Consider how React's rendering cycle and reconciliation algorithm impact performance across component trees
- Think about when components unnecessarily re-render and how this cascades through the application
- Review how API calls are triggered from different parts of the application and identify duplication patterns
- Analyze data flow patterns and identify where state changes trigger unnecessary updates
- Consider TypeScript's role in maintaining type safety during architectural refactoring
- Explore React's built-in optimization hooks and when each is most appropriate
- Think about component composition patterns and responsibility separation across features
- Review browser DevTools (React Profiler, Performance tab, Network tab) for comprehensive performance analysis
- Consider context provider optimization and when to split contexts
- Explore custom hook patterns for encapsulating optimization logic
- Think about data normalization and efficient data structures
- Review expensive computations and identify memoization opportunities
- Consider code splitting strategies for reducing initial load
- Analyze the trade-offs between different optimization approaches
- Think about measuring performance improvements quantitatively
- Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Analyze"

**CRITICAL**: Guide discovery and analytical thinking, never provide direct solutions

### NOT TO INCLUDE:
- Step-by-step implementation instructions
- Exact code solutions
- Configuration examples with specific code
- Specific library recommendations beyond React built-ins and standard tools
- Phrases like "you should implement", "add the following code"
- Direct answers to architectural decisions

## TYPESCRIPT CONFIGURATION REQUIREMENTS

### tsconfig.json MUST include:

{
  "compilerOptions": {
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
    "jsx": "react-jsx",
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true
  },
  "include": [
    "src"
  ]
}


### package.json MUST include:

{
  "name": "task-name",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@types/react-router-dom": "^5.3.3",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
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
  }
}


## CRITICAL REMINDERS

1. **ALL files must use TypeScript** (.tsx, .ts extensions)
2. **NO 'any' types** - proper type definitions with intermediate TypeScript patterns required
3. **Application must run perfectly** with `npm install` && `npm start` && `npm run dev`
4. **NO TypeScript compilation errors** even with strict mode enabled
5. **Task must be completable in 30-45 minutes** by intermediate-level developers
6. **Focus on 4-6 interconnected optimization areas** requiring architectural thinking
7. **Code must be unoptimized but fully functional** with multiple performance bottlenecks
8. **NO comments that reveal solutions** or hint at specific optimization techniques
9. **Proper TypeScript configurations** in tsconfig.json with strict mode
10. **All required @types packages** in package.json for all third-party libraries
11. **Use standard Create React App with TypeScript template structure**
12. **All development scripts must be present**: start, build, test, eject
13. **Include all standard CRA files**: public/index.html, public/manifest.json, public/robots.txt, src/react-app-env.d.ts
14. **Entry point must be src/index.tsx**
15. **Must use react-scripts for all operations**
16. **Include custom hooks** with proper TypeScript generics where applicable
17. **Include Context providers** with inefficient value recreation patterns
18. **Multiple pages/features** requiring navigation and state coordination
19. **Complex data structures** that would benefit from normalization
20. **Intermediate TypeScript patterns** used functionally but not optimized (generics, union types, type guards)
21. **Performance issues must span multiple layers**: rendering, state management, data fetching, computations
22. **Application must demonstrate real-world complexity** appropriate for 3-5 years experience level

"""
PROMPT_REGISTRY = {
    "ReactJs, ReactJs - Optimization": [
        PROMPT_REACT_OPTIMIZATION_INTERMEDIATE_CONTEXT,
        PROMPT_REACT_OPTIMIZATION_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_REACT_OPTIMIZATION_INTERMEDIATE,
    ]
}
