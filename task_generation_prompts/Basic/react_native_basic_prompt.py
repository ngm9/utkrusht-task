PROMPT_REACT_NATIVE_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACT_NATIVE_BASIC_INPUT_AND_ASK = """
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

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of React Native implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_NATIVE_BASIC_INSTRUCTIONS = """
# React Native Basic Task Requirements

## GOAL
As a technical architect super experienced in React Native and mobile app development, you are given real-world scenarios and proficiency levels for React Native development. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

## IMPORTANT: REACT NATIVE CONTEXT
- React Native is a mobile application framework. The candidate runs the app on their own machine using Expo Go (on a physical device or emulator/simulator).
- There is NO server/droplet deployment. The candidate clones the repo, runs `npm install` and `npx expo start`, and develops locally.
- The candidate submits their work by pushing code to the GitHub repo. No APK/IPA build artifacts are needed.
- Use **Expo SDK** (managed workflow) for simplicity — this avoids native build toolchain requirements.
- All UI is built with React Native components (View, Text, ScrollView, FlatList, etc.), NOT HTML/DOM elements.
- Styling uses React Native's `StyleSheet.create()`, NOT CSS files.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years React Native experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental React Native concepts like:
  - Core components (View, Text, Image, ScrollView, FlatList, TextInput, TouchableOpacity, Pressable)
  - Component composition and props
  - State management with useState and useEffect
  - Event handling (onPress, onChangeText, onSubmit)
  - Conditional rendering and list rendering with FlatList/SectionList
  - Basic navigation using React Navigation (Stack Navigator, Tab Navigator)
  - Form handling and input validation
  - Basic data fetching with fetch/axios and displaying results
  - React Native styling with StyleSheet (flexbox layout, platform-specific styles)
  - Safe area handling and basic responsive layout
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React Native best practices (React Native 0.72+ / Expo SDK 49+) and current JavaScript/TypeScript standards. Use functional components with hooks exclusively.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years React Native experience).

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and runnable with `npx expo start`.
- Keep the code files minimal and to the point.
- Use Expo managed workflow for simplicity (no native iOS/Android build configuration needed).
- Include a proper `app.json` with Expo configuration.
- Include a `package.json` with Expo and React Native dependencies.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- If the task is to fix bugs, the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, the starter code only provides a good starting point.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic React Native proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

### Code Generation Instructions
Based on real-world scenarios, create a React Native task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BASIC proficiency level (1-2 years React Native experience)
- Can be completed within {minutes_range} minutes
- Tests practical React Native skills that require more than a simple AI query to solve, focusing on fundamental mobile development concepts
- Select a different real-world scenario each time to ensure variety in task generation
- Focus on single-screen or simple multi-screen mobile features rather than complex multi-tab architectures
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "rn-inventory-tracker", "rn-contact-list-app")

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Build Product List Screen with Search and Filter', 'Fix Navigation and State Management in Delivery Tracker', 'Implement Order Form with Real-Time Validation'. The title should clearly convey the action (implement, fix, build, refactor, optimize, debug) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed/implemented?",
  "code_files": {{
    "README.md": "Candidate-facing README following structure below",
    ".gitignore": "Comprehensive React Native/Expo/Node.js exclusions",
    "package.json": "All dependencies including expo, react-native, react-navigation, etc.",
    "app.json": "Expo app configuration",
    "babel.config.js": "Babel configuration for Expo",
    "App.js": "Main App component (entry point)",
    "src/screens/ScreenName.js": "Screen component files",
    "src/components/ComponentName.js": "Reusable component files",
    "additional_file.js": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results after completion and one bullet explicitly stating: 'Write production-level clean code with best practices including proper naming conventions, error handling, and code organization.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business context and problem, (2) the specific implementation goal, and (3) the expected outcome.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. example: Node.js 18+, npm/yarn, Expo CLI, Expo Go app (on phone or emulator), Git, JavaScript/React Native knowledge, etc.",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer, but gently nudge the candidate in the right direction.",
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

Note: Add additional dependencies as needed for the specific task (e.g., @react-navigation/native, @react-navigation/native-stack, react-native-safe-area-context, react-native-screens, axios, etc.). Only include packages that are actually used in the starter code.

### babel.config.js MUST include:
module.exports = function(api) {{
  api.cache(true);
  return {{
    presets: ['babel-preset-expo'],
  }};
}};

## README.md STRUCTURE (React Native Basic)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: This section MUST contain 3-4 meaningful sentences describing the business scenario and current situation. Describe what the candidate is working on and why it matters. NEVER generate empty content — always provide substantial business context.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for the task:

- Clear, measurable goals for the candidate appropriate for basic level
- What functionality should be implemented, expected behavior
- Focus on fundamental React Native concepts and mobile development skills
- This is what the candidate should be able to do successfully to say that they have completed the task

**CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:

- Project context and guidance points suitable for basic level React Native developers
- General React Native best practices and mobile development notes
- Important considerations for the implementation for the task
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"

**CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.


### How to Verify (3-5 bullets MAX)

Verification approaches after implementation:

- Specific checkpoints after implementation, what to test and how to confirm success
- Observable behaviors or outputs to validate on the device/emulator
- Include both functional testing and basic code quality checks
- These points help the candidate verify their own work and the assessor to award points

**CRITICAL**: Focus on measurable, verifiable outcomes. Keep to 3-5 concise bullets only.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS OR COMMANDS (npm install, npx expo start, etc.)
- Step-by-step implementation instructions
- Exact code solutions or configuration examples
- Direct solutions or hints
- Specific React Native component names or hook usage patterns that would give away the solution
- Any specific files or navigation implementation details that would give away the solution
- Excessive bullets or verbose explanations — keep each section lean and focused

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for React Native/Expo projects including node_modules, .expo/, dist/, environment files (.env), log files, IDE configurations (.idea, .vscode), iOS build artifacts (ios/Pods/, ios/build/), Android build artifacts (android/app/build/, android/.gradle/), and other common development artifacts that should not be tracked in version control.

## CRITICAL REMINDERS

1. **Starter code must be runnable** with `npx expo start` but must NOT contain the core logic solution
2. **NO comments** that reveal the solution or give hints
3. **Task must be completable within {minutes_range} minutes**
4. **Focus on fundamental React Native concepts** appropriate for BASIC level
5. **Use functional components with hooks exclusively** (React Native 0.72+ / Expo SDK 49+)
6. **Code files MUST NOT contain** implementation for the core logic the candidate must implement
7. **README.md MUST be fully populated** with meaningful, task-specific content
8. **.gitignore** must cover standard React Native/Expo exclusions
9. **Task name** must be short, descriptive, under 50 characters, kebab-case
10. **Select a different real-world scenario** each time for variety
11. **Use React Native components** (View, Text, FlatList, etc.) — NOT HTML/DOM elements
12. **Styling via StyleSheet.create()** — NOT CSS files
13. **Entry point is App.js** which is loaded by Expo's AppEntry
14. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "React Native (BASIC)": [
        PROMPT_REACT_NATIVE_BASIC_CONTEXT,
        PROMPT_REACT_NATIVE_BASIC_INPUT_AND_ASK,
        PROMPT_REACT_NATIVE_BASIC_INSTRUCTIONS,
    ]
}
