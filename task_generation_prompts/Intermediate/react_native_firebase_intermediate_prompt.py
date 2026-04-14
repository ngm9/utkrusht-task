PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a React Native + Firebase assessment task.

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
2. What will the task look like? (Describe the type of React Native + Firebase implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_INSTRUCTIONS = """
# React Native + Firebase Intermediate Task Requirements

## GOAL
As a technical architect super experienced in React Native and Firebase, you are given real-world scenarios and proficiency levels for mobile development with Firebase backend. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end at an intermediate level.

## IMPORTANT: ARCHITECTURE CONTEXT

### How This Task Works
- The candidate receives a React Native (Expo) mobile app that connects to a **Firebase Emulator Suite** running on a remote DigitalOcean droplet.
- The Firebase Emulators (Firestore, Authentication) run inside Docker on the droplet — the candidate does NOT need to set up Firebase or create a Google account.
- The candidate's React Native app connects to the droplet IP for Firebase services (Firestore at `droplet_ip:8080`, Auth at `droplet_ip:9099`).
- The candidate runs the React Native app locally using Expo, makes code changes, and pushes to GitHub.

### What Gets Deployed to the Droplet
The following files run on the droplet inside `/root/task/`:
- `docker-compose.yml` — runs the Firebase Emulator Suite container
- `firebase.json` — configures which emulators to run and their ports
- `run.sh` — starts Docker containers, waits for emulators to be healthy
- `kill.sh` — tears down containers and cleans up
- Optionally: seed data scripts that pre-populate Firestore with test data

### What the Candidate Gets (GitHub Repo)
The candidate clones a repo with:
- React Native (Expo) app code with Firebase SDK configured to point to the droplet emulators
- Partial Firebase integration code with architectural issues or missing advanced patterns
- README with task description

### Separation of Concerns
- **Infrastructure (droplet)**: Docker, Firebase Emulators, seed data — MUST work perfectly, no errors
- **React Native app code**: This is where problems exist that the candidate must fix
- The candidate NEVER touches Docker, run.sh, or emulator configuration

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors.
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years React Native + Firebase experience), ensuring that no two questions generated are similar.
- For INTERMEDIATE level, the questions should test deeper understanding and require candidates to demonstrate:
  - **Advanced Firestore Patterns**: Compound queries, subcollections, data denormalization strategies, batch writes, transactions for atomic operations
  - **Real-time Architecture**: Efficient onSnapshot listeners with proper cleanup, listener management across screen navigation, optimistic UI updates with Firestore
  - **Auth Architecture**: Custom hooks for auth state management, protected route patterns with React Navigation, role-based access using custom claims or Firestore user profiles
  - **Data Layer Design**: Custom hooks encapsulating Firestore logic (useCollection, useDocument), separation of Firebase logic from UI components, caching and local state sync
  - **Performance**: Firestore query optimization (index usage, query cursors for pagination), minimizing reads, proper listener lifecycle management to avoid memory leaks
  - **Error Handling**: Comprehensive error boundaries for Firebase operations, offline handling with Firestore persistence, retry patterns for failed writes
  - **State Management with Firebase**: Context + useReducer for auth state, combining Firestore real-time data with local UI state, managing loading/error/success states across multiple Firebase operations
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions adhere to modern React Native best practices (Expo SDK 51) and Firebase JS SDK v9+ (modular API).
- Tasks should require candidates to make architectural decisions.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with INTERMEDIATE proficiency (3-5 years experience).

## CRITICAL DEPLOYMENT AND IMPLEMENTATION PHILOSOPHY

**DEPLOYMENT SETUP REQUIREMENTS:**

1. **WORKING DEPLOYMENT ON DROPLET**:
   - docker-compose.yml and run.sh MUST deploy Firebase Emulators without any errors
   - Firestore emulator MUST be accessible on port 8080
   - Auth emulator MUST be accessible on port 9099
   - Emulator UI MUST be accessible on port 4000
   - Seed data MUST load successfully into Firestore emulator
   - The candidate should NOT need to fix any infrastructure issues

2. **PROBLEMS EXIST IN REACT NATIVE CODE ONLY**:
   - The React Native app has architectural issues or missing advanced Firebase patterns
   - Firebase SDK is installed and basic operations work, but advanced patterns are missing
   - Data layer may lack proper abstraction, error handling, or optimization
   - The app runs with `npx expo start` but Firebase features are incomplete or poorly architected

3. **CANDIDATE RECEIVES**:
   - A running Firebase Emulator on the droplet with pre-populated test data
   - A React Native app repo with Firebase SDK configured
   - They ONLY fix/implement the React Native + Firebase integration code

**SEPARATION OF CONCERNS**:
- **run.sh + docker-compose.yml + firebase.json**: MUST work perfectly on the droplet
- **React Native app code**: This is where the problems exist
- Deployment = Working on droplet
- React Native Firebase code = Needs fixing by candidate

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- Provide a realistic project structure that mimics real-world mobile applications
- The React Native code must be valid and runnable with `npx expo start`
- Firebase SDK initialized and connected to emulators
- Use Expo managed workflow with Firebase JS SDK v9+ (modular imports)
- Include some existing components/hooks that the candidate needs to extend or refactor
- Provide partial implementations that require architectural completion

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code
- If the task is to fix bugs, the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments

### AI and External Resource Policy
- Candidates are permitted to use external resources including AI tools, documentation, Stack Overflow.
- Tasks assess ability to find, understand, integrate, and adapt solutions requiring genuine engineering and architectural skills.

### Code Generation Instructions
Based on real-world scenarios, create a React Native + Firebase task that:
- Draws inspiration from input scenarios for business context
- Matches INTERMEDIATE proficiency level (3-5 years experience)
- Can be completed within {minutes_range} minutes
- Tests practical skills requiring architectural thinking, Firebase optimization, and advanced patterns
- Select a different real-world scenario each time for variety
- Focus on multi-screen apps with Firebase data layer that requires thoughtful architecture
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "rn-firebase-order-system", "rn-firebase-chat-app")

## Infrastructure Requirements

### Docker-compose Instructions:
- Firebase Emulator Suite running in a Docker container
- Use a community Firebase emulator Docker image (e.g., `andreysenov/firebase-tools` or `spine3/firebase-tools` or similar well-maintained image)
- Expose ports: 4000 (Emulator UI), 8080 (Firestore), 9099 (Auth)
- **CRITICAL**: Ports MUST be bound to `0.0.0.0` (e.g., `"0.0.0.0:8080:8080"`) because the candidate's local React Native app needs to reach the droplet over the network
- Mount firebase.json and seed data into the container
- **MUST NOT include any version specification** in docker-compose.yml
- **MUST NOT include environment variables or .env file references**

### firebase.json Instructions:
- Configure Firestore emulator on port 8080
- Configure Auth emulator on port 9099
- Configure Emulator UI on port 4000
- Set `"host": "0.0.0.0"` for each emulator so they are accessible from outside the container
- Include Firestore rules file if the task involves security rules
- Reference seed data import directory if pre-populated data is needed

### Run.sh Instructions:
- PRIMARY RESPONSIBILITY: Starts Docker containers and ensures successful deployment
- **CRITICAL**: This script MUST work perfectly without any errors
- WAIT MECHANISM: Health check for Firebase Emulators (curl to emulator endpoints)
- SEED DATA: Populate Firestore emulator with realistic test data after startup
- LOCATION: All files in /root/task directory
- **SUCCESS CONFIRMATION**: Clearly indicate successful deployment

### kill.sh Instructions:
- Stop and remove all containers, volumes, networks
- Force-remove Docker images
- Run `docker system prune -a --volumes -f`
- Delete `/root/task/`
- Idempotent, use `set -e` and `|| true`
- Print logs at every step

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

**CRITICAL**: Do NOT include `"sdkVersion"` in app.json.

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
    "react-native": "0.74.5",
    "firebase": "^10.12.0"
  }},
  "devDependencies": {{
    "@babel/core": "^7.20.0"
  }}
}}

**CRITICAL**: `"main"` MUST be `"expo/AppEntry.js"`. Firebase JS SDK v10 uses modular v9+ API.

Note: Add additional dependencies as needed (e.g., @react-navigation/native, @react-navigation/native-stack, @react-navigation/bottom-tabs, react-native-safe-area-context, react-native-screens). Only include packages actually used.

### Firebase Configuration File (src/config/firebase.js):

import {{ initializeApp }} from 'firebase/app';
import {{ getFirestore, connectFirestoreEmulator }} from 'firebase/firestore';
import {{ getAuth, connectAuthEmulator }} from 'firebase/auth';

const DROPLET_IP = '<DROPLET_IP>';

const firebaseConfig = {{
  apiKey: 'demo-key',
  authDomain: 'demo-project.firebaseapp.com',
  projectId: 'demo-project',
  storageBucket: 'demo-project.appspot.com',
  messagingSenderId: '000000000000',
  appId: '1:000000000000:web:0000000000000000'
}};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

connectFirestoreEmulator(db, DROPLET_IP, 8080);
connectAuthEmulator(auth, `http://${{DROPLET_IP}}:9099`);

export {{ db, auth }};

**CRITICAL**: Use `'<DROPLET_IP>'` as placeholder. Dummy firebaseConfig values are fine for emulators.

### babel.config.js MUST include:
module.exports = function(api) {{
  api.cache(true);
  return {{
    presets: ['babel-preset-expo'],
  }};
}};

## README.md INSTRUCTIONS:

**CRITICAL**: The README must be concise and open-ended. Quality over quantity.

### Task Overview (MANDATORY - 3-4 substantial sentences)
Describe the business scenario, what Firebase services are involved, and what architectural issues exist. NEVER generate empty content.

### Firebase Emulator Access
- Firestore Emulator: `http://<DROPLET_IP>:8080`
- Auth Emulator: `http://<DROPLET_IP>:9099`
- Emulator UI: `http://<DROPLET_IP>:4000`
- Note the app is already configured to connect to emulators

### Helpful Tips (4-5 bullets MAX)
- Suggest exploring Firebase data modeling and query patterns
- Mention thinking about listener lifecycle and cleanup
- Hint at considering auth state management architecture
- Use "Consider", "Think about", "Explore", "Review"
- **CRITICAL**: Guide discovery, not direct solutions

### Objectives (4-6 bullets MAX)
- Clear, measurable goals for intermediate level
- Focus on both functional requirements and architectural quality
- Include expectations for data layer design and performance
- **CRITICAL**: Describe "what" and "why", never "how"

### How to Verify (4-6 bullets MAX)
- Observable behaviors on device/emulator AND in Firebase Emulator UI
- Include checking Firestore data structure and auth state in Emulator UI
- Architectural quality checkpoints
- **CRITICAL**: Describe what to verify, not specific implementation

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS for droplet or Docker
- How to run run.sh or docker-compose
- Direct solutions or architectural decisions
- Specific Firebase SDK method names that reveal the solution
- npm install or npx expo start instructions

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters.",
  "question": "Detailed description of the task scenario including architectural considerations.",
  "code_files": {{
    "README.md": "Candidate-facing README with Task Overview, Firebase Emulator Access, Helpful Tips, Objectives, How to Verify",
    ".gitignore": "Comprehensive React Native/Expo/Firebase/Docker exclusions",
    "package.json": "Dependencies including expo, react-native, firebase, navigation",
    "app.json": "Expo app configuration",
    "babel.config.js": "Babel configuration for Expo",
    "App.js": "Main App component (entry point)",
    "src/config/firebase.js": "Firebase SDK initialization connecting to droplet emulators",
    "src/navigation/AppNavigator.js": "Navigation configuration",
    "src/screens/ScreenName.js": "Screen component files",
    "src/components/ComponentName.js": "Reusable component files",
    "src/hooks/useCustomHook.js": "Custom hook files",
    "src/services/firestore.js": "Firestore service layer (if applicable)",
    "src/context/AuthContext.js": "Auth context provider (if applicable)",
    "docker-compose.yml": "Firebase Emulator Suite container (MUST WORK PERFECTLY)",
    "firebase.json": "Firebase emulator configuration",
    "firestore.rules": "Firestore security rules (if applicable)",
    "run.sh": "Deployment script for droplet (MUST WORK PERFECTLY)",
    "kill.sh": "Cleanup script for droplet",
    "seed_data.sh": "Script to seed Firestore with test data",
    "additional_file.js": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list. One bullet MUST state: 'Write production level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list: (1) business problem, (2) implementation goal, (3) expected outcome. but no need to mention in the start which point it belongs to. Just a concise 3-4 sentence overview.",
  "pre_requisites": "Bullet-point list Example :Node.js 18+, Expo CLI, Expo Go, Git, intermediate React Native + Firebase knowledge (Firestore queries, real-time listeners, auth patterns, custom hooks, data layer architecture).",
  "answer": "High-level solution approach with emphasis on architectural decisions",
  "hints": "Single line focusing on architectural approach. Must NOT give away the answer.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2"
  }}
}}

## Code file requirements:
- Generate realistic folder structure (src/screens/, src/components/, src/hooks/, src/services/, src/config/, src/context/, src/navigation/)
- Code should follow modern React Native + Firebase best practices at intermediate level
- Use functional components with hooks exclusively
- Firebase JS SDK v9+ modular imports throughout
- **CRITICAL**: Provide partial implementations that require architectural completion
- Include existing components/hooks that need extension or refactoring
- Core architectural decisions MUST be left for the candidate
- DO NOT include any TODO, hint, or solution-revealing comments
- Deployment files MUST be perfect; only React Native code has issues
- **All Docker/script paths reference /root/task**

## CRITICAL REMINDERS

1. **Infrastructure files MUST work perfectly** on the droplet — no deployment bugs
2. **React Native starter code must be runnable** with `npx expo start`
3. **Firebase SDK initialized and connected to emulators** via the config file
4. **NO comments** revealing the solution
5. **Task completable within {minutes_range} minutes**
6. **Focus on intermediate Firebase patterns** — architectural depth over task breadth
7. **Firebase JS SDK v9+ modular API** only
8. **Emulator ports bound to 0.0.0.0** for external access
9. **`<DROPLET_IP>` placeholder** in Firebase config
10. **Seed Firestore with realistic test data** — intermediate tasks should have meaningful data to work with
11. **"title"** in `<action verb> <subject>` format
"""
PROMPT_REGISTRY = {
    "Firebase (INTERMEDIATE), React Native (INTERMEDIATE)": [
        PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_CONTEXT,
        PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_REACT_NATIVE_FIREBASE_INTERMEDIATE_INSTRUCTIONS,
    ]
}
