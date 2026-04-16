PROMPT_REACT_NATIVE_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACT_NATIVE_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React Native assessment task.

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
2. What will the task look like? (Describe the type of React Native implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_NATIVE_INTERMEDIATE_INSTRUCTIONS = """
# React Native Intermediate Task Requirements

## GOAL
As a technical architect super experienced in React Native and mobile application development, you are given a list of real world scenarios and proficiency levels for React Native development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## IMPORTANT: REACT NATIVE CONTEXT
- React Native is a mobile application framework. The candidate runs the app on their own machine using Expo Go (on a physical device or emulator/simulator).
- There is NO server/droplet deployment. The candidate clones the repo, runs `npm install` and `npx expo start`, and develops locally.
- The candidate submits their work by pushing code to the GitHub repo. No APK/IPA build artifacts are needed.
- Use **Expo SDK** (managed workflow) for simplicity — this avoids native build toolchain requirements.
- All UI is built with React Native components (View, Text, ScrollView, FlatList, etc.), NOT HTML/DOM elements.
- Styling uses React Native's `StyleSheet.create()`, NOT CSS files.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years React Native experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced Navigation Patterns**: Nested navigators, deep linking, conditional navigation flows, passing params between screens, navigation state persistence
  - **State Management Architecture**: Context API with useReducer, global state patterns, state normalization, optimistic updates, custom hooks for state logic
  - **Performance Optimization**: FlatList optimization (getItemLayout, keyExtractor, windowSize), React.memo, useMemo, useCallback, avoiding unnecessary re-renders in list-heavy screens
  - **Advanced Hooks Usage**: useReducer, useContext, useRef, custom hooks for business logic, hook composition patterns
  - **API Integration & Data Layer**: Fetch/axios with interceptors, error handling, retry logic, caching strategies, pagination (infinite scroll), pull-to-refresh
  - **Animations & Gestures**: React Native Animated API, LayoutAnimation, basic gesture handling with react-native-gesture-handler
  - **Platform-Specific Code**: Platform.OS/Platform.select usage, platform-specific styling, handling platform differences gracefully
  - **Error Handling & Resilience**: Error boundaries, graceful degradation, user-friendly error states, offline handling patterns
  - **Component Architecture**: Compound components, render props, higher-order components adapted for mobile, presentational vs container pattern
  - **Local Storage**: AsyncStorage patterns, data persistence, caching fetched data locally
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React Native best practices (React Native 0.72+ / Expo SDK 49+) and current JavaScript standards. Use functional components with hooks exclusively.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years React Native experience).

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills
- The code files generated must be valid and runnable with `npx expo start`.
- Provide a realistic project structure that mimics real-world mobile applications
- Use Expo managed workflow for simplicity (no native iOS/Android build configuration needed).
- Include a proper `app.json` with Expo configuration.
- Include a `package.json` with Expo, React Native, and relevant dependencies.
- Include some existing components/utilities that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architecture

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper component design and state management
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate React Native proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

### Code Generation Instructions
Based on real-world scenarios, create a React Native task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches INTERMEDIATE proficiency level (3-5 years React Native experience)
- Can be completed within {minutes_range} minutes
- Tests practical React Native skills that require architectural thinking, performance considerations, and advanced mobile development patterns
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on multi-screen mobile applications that require thoughtful state management, navigation architecture, and component communication
- Should test the candidate's ability to structure a scalable React Native application
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "rn-order-management-app", "rn-realtime-dashboard")

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Refactor Navigation and State Architecture in Fleet Tracker', 'Implement Offline-First Data Sync for Field Service App', 'Optimize List Performance in Real-Time Inventory Dashboard'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed? Include architectural considerations and requirements.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
    ".gitignore": "Comprehensive React Native/Expo/Node.js exclusions",
    "package.json": "All dependencies including expo, react-native, react-navigation, and intermediate-level packages",
    "app.json": "Expo app configuration",
    "babel.config.js": "Babel configuration for Expo",
    "App.js": "Main App component (entry point)",
    "src/navigation/AppNavigator.js": "Navigation configuration",
    "src/screens/ScreenName.js": "Screen component files",
    "src/components/ComponentName.js": "Reusable component files",
    "src/hooks/useCustomHook.js": "Custom hook files as needed",
    "src/utils/utilityFile.js": "Utility files as needed",
    "src/context/ContextProvider.js": "Context providers as needed",
    "src/services/api.js": "API service files as needed",
    "additional_file.js": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation goal, and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Node.js 18+, npm/yarn, Expo CLI, Expo Go app (on phone or emulator), Git, intermediate React Native knowledge (navigation patterns, state management, performance optimization, API integration, custom hooks).",
  "answer": "High-level solution approach with emphasis on architectural decisions and design patterns",
  "hints": "A single line hint focusing on architectural approach or design pattern that could be useful. These hints must NOT give away the answer, but guide towards good architectural thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## EXPO AND REACT NATIVE CONFIGURATION REQUIREMENTS

### app.json MUST include:
{{
  "expo": {{
    "name": "task-name",
    "slug": "task-name",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "light",
    "ios": {{
      "supportsTablet": true
    }},
    "android": {{
      "adaptiveIcon": {{
        "backgroundColor": "#ffffff"
      }}
    }}
  }}
}}

**CRITICAL**: Do NOT include `"sdkVersion"` in app.json — it is deprecated. The SDK version is automatically inferred from the `expo` package version in package.json.

### package.json MUST include:
{{
  "name": "task-name",
  "version": "1.0.0",
  "main": "expo/AppEntry.js",
  "scripts": {{
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios"
  }},
  "dependencies": {{
    "expo": "~51.0.28",
    "expo-status-bar": "~1.12.1",
    "react": "18.2.0",
    "react-native": "0.74.5"
  }},
  "devDependencies": {{
    "@babel/core": "^7.20.0"
  }}
}}

**CRITICAL**: The `"main"` field MUST be `"expo/AppEntry.js"` (NOT `"node_modules/expo/AppEntry.js"` — that is the old format).

Note: Add additional dependencies as needed for the specific task (e.g., @react-navigation/native, @react-navigation/native-stack, @react-navigation/bottom-tabs, react-native-safe-area-context, react-native-screens, @react-native-async-storage/async-storage, axios, etc.). Only include packages that are actually used in the starter code.

### babel.config.js MUST include:
module.exports = function(api) {{
  api.cache(true);
  return {{
    presets: ['babel-preset-expo'],
  }};
}};

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
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions
- **CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
- README should NOT be heavy — each section should have only the essential points (4-6 bullets max for Objectives and How to Verify, 4-5 bullets for Helpful Tips)

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why architectural considerations matter for this mobile use case.
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper React Native architecture is crucial.


### Objectives (4-5 bullets max)
  - Clear, measurable goals for the candidate appropriate for intermediate React Native level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and code quality metrics
  - Include expectations for component design, state management, and performance
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"
  
### Helpful Tips (4-5 bullets max)
Provide practical guidance without revealing specific implementations:
  - Suggest exploring mobile-specific architectural patterns and state management strategies
  - Mention thinking about how to structure navigation for scalability and deep linking
  - Hint at considering performance optimization for list-heavy screens and data-intensive views
  - Recommend exploring how platform differences should influence component design
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review"
  - **CRITICAL**: Tips should guide discovery toward architectural thinking, not provide direct solutions or specific APIs

### How to Verify (4-5 bullets max)
  - Specific checkpoints after implementation, what to test and how to confirm success on device/emulator
  - Observable behaviors or outputs to validate both functionality and architecture
  - Mobile-specific verification: screen transitions, gesture responses, list scrolling performance, data persistence across app restarts
  - Code quality checkpoints (component structure, performance, error handling)
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

### NOT TO INCLUDE in README:
  - SETUP INSTRUCTIONS OR COMMANDS (npm install, npx expo start, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific React Native component names, hook implementations, or navigation configurations that reveal the solution
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific files implementation details that would give away the solution to the task
  - Should not provide any particular architectural approach or design pattern to implement the solution
  - Phrases like "you should implement", "use FlatList with getItemLayout", "add useReducer for state"

## Code file requirements:
- Generate realistic folder structure (src/screens/, src/components/, src/hooks/, src/utils/, src/services/, src/context/, src/navigation/, src/constants/)
- Code should follow modern React Native best practices and demonstrate intermediate-level patterns
- Use functional components with hooks exclusively, including advanced hooks usage
- Focus on modern JavaScript/ES6+ features and React Native best practices
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing components/utilities that need to be extended or integrated
- The core architectural decisions, advanced component patterns, performance optimizations, navigation architecture, or state management solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add optimization here" or "Should implement custom hook" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be runnable, but will require architectural completion to function properly
- Provide realistic dependencies in package.json that intermediate React Native developers should be familiar with

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for React Native/Expo projects including node_modules, .expo/, dist/, environment files (.env), log files, IDE configurations (.idea, .vscode), iOS build artifacts (ios/Pods/, ios/build/), Android build artifacts (android/app/build/, android/.gradle/), coverage reports, and other common development artifacts that should not be tracked in version control.

## CRITICAL REMINDERS

1. **Starter code must be runnable** with `npx expo start` but must NOT contain the core logic solution
2. **NO comments** that reveal the solution or give hints
3. **Task must be completable within {minutes_range} minutes**
4. **Focus on intermediate React Native concepts** requiring architectural thinking
5. **Use functional components with hooks exclusively** (React Native 0.72+ / Expo SDK 49+)
6. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
7. **README.md MUST be fully populated** with meaningful, task-specific content
8. **.gitignore** must cover standard React Native/Expo exclusions
9. **Task name** must be short, descriptive, under 50 characters, kebab-case
10. **Select a different real-world scenario** each time for variety
11. **Use React Native components** (View, Text, FlatList, etc.) — NOT HTML/DOM elements
12. **Styling via StyleSheet.create()** — NOT CSS files
13. **Entry point is App.js** which is loaded by Expo's AppEntry
14. **Multi-screen apps should use React Navigation** with proper navigator structure
15. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "React Native (INTERMEDIATE)": [
        PROMPT_REACT_NATIVE_INTERMEDIATE_CONTEXT,
        PROMPT_REACT_NATIVE_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_REACT_NATIVE_INTERMEDIATE_INSTRUCTIONS,
    ]
}
