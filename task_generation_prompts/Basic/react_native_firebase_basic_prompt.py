PROMPT_REACT_NATIVE_FIREBASE_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_REACT_NATIVE_FIREBASE_BASIC_INPUT_AND_ASK = """
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

1. What will the task be about? (Describe the business domain, context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of React Native + Firebase implementation or fix required, the expected deliverables, and how it aligns with BASIC proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_REACT_NATIVE_FIREBASE_BASIC_INSTRUCTIONS = """
# React Native + Firebase Basic Task Requirements

## GOAL
As a technical architect super experienced in React Native and Firebase, you are given real-world scenarios and proficiency levels for mobile development with Firebase backend. Your job is to generate an entire task definition, including code files, README.md, expected outcomes, etc., that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug, or in general solve a problem end to end.

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
- The Firebase integration code (some working, some broken or missing — this is what they fix)
- README with task description

### Separation of Concerns
- **Infrastructure (droplet)**: Docker, Firebase Emulators, seed data — MUST work perfectly, no errors
- **React Native app code**: This is where problems exist that the candidate must fix
- The candidate NEVER touches Docker, run.sh, or emulator configuration

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a feature from scratch or fix bugs in the existing React Native + Firebase code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context.
- Generate enough starter code that gives the candidate a good starting point to start solving the task.
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors.
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years React Native + Firebase experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental React Native + Firebase concepts like:
  - Firebase Authentication (email/password sign-up, sign-in, sign-out, auth state listener with onAuthStateChanged)
  - Firestore CRUD operations (addDoc, getDoc, getDocs, updateDoc, deleteDoc)
  - Firestore queries (where, orderBy, limit) and reading query results
  - Firestore real-time listeners (onSnapshot for live data updates)
  - Connecting auth state to navigation (showing login vs main screens)
  - Displaying Firestore data in FlatList with proper loading/error states
  - Basic form handling for creating/updating Firestore documents
  - Firebase SDK initialization and configuration
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern React Native best practices (Expo SDK 51) and Firebase JS SDK v9+ (modular API).
- Use functional components with hooks exclusively.
- **Time Constraint**: Each task MUST be completable within {minutes_range} minutes by a candidate with BASIC proficiency (1-2 years experience).

## CRITICAL DEPLOYMENT AND IMPLEMENTATION PHILOSOPHY

**DEPLOYMENT SETUP REQUIREMENTS:**
This is the MOST CRITICAL aspect of task generation. The task must follow this exact pattern:

1. **WORKING DEPLOYMENT ON DROPLET**:
   - docker-compose.yml and run.sh MUST deploy Firebase Emulators without any errors
   - Firestore emulator MUST be accessible on port 8080
   - Auth emulator MUST be accessible on port 9099
   - Emulator UI MUST be accessible on port 4000
   - Seed data (if any) MUST load successfully into Firestore emulator
   - The candidate should NOT need to fix any infrastructure issues

2. **PROBLEMS EXIST IN REACT NATIVE CODE ONLY**:
   - The React Native app has missing or broken Firebase integration code
   - Firebase SDK is installed and configured but some features are not wired up
   - Auth flows may be incomplete (e.g., sign-up works but sign-in doesn't)
   - Firestore reads/writes may be missing or have logical bugs
   - The app runs with `npx expo start` but Firebase features don't work correctly

3. **CANDIDATE RECEIVES**:
   - A running Firebase Emulator on the droplet (already deployed)
   - A React Native app repo with Firebase SDK configured to point to the droplet
   - They ONLY fix/implement the React Native + Firebase integration code

**SEPARATION OF CONCERNS**:
- **run.sh + docker-compose.yml + firebase.json**: MUST work perfectly on the droplet
- **React Native app code**: This is where the problems exist
- Deployment = Working on droplet
- React Native Firebase code = Needs fixing by candidate

### Starter Code Requirements

**WHAT MUST BE INCLUDED:**
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The React Native code files must be valid and runnable with `npx expo start`.
- Firebase SDK must be installed and initialized (connecting to the droplet emulators).
- Use Expo managed workflow with Firebase JS SDK v9+ (modular imports).
- Include `app.json`, `package.json`, `babel.config.js` for the React Native app.

**WHAT MUST NOT BE INCLUDED:**
- DO NOT give away the solution in the starter code.
- If the task is to fix bugs, the starter code has logical bugs (no syntactic errors) in the Firebase integration.
- If the task is to implement a feature, the starter code provides the UI skeleton but the Firebase logic is missing.
- **NO comments of any kind**: NO TODO, NO hints, NO placeholder comments.

### AI and External Resource Policy
- Candidates are permitted and encouraged to use any external resources they find helpful.
- Tasks assess ability to find, understand, integrate, and adapt solutions for React Native + Firebase.

### Code Generation Instructions
Based on real-world scenarios, create a React Native + Firebase task that:
- Draws inspiration from input scenarios for business context and technical requirements
- Matches BASIC proficiency level (1-2 years experience)
- Can be completed within {minutes_range} minutes
- Tests practical React Native + Firebase skills focusing on fundamental concepts
- Select a different real-world scenario each time to ensure variety
- Task name: short, descriptive, under 50 characters, kebab-case (e.g., "rn-firebase-todo-app", "rn-firebase-inventory")

## Infrastructure Requirements

### Docker-compose Instructions:
- Firebase Emulator Suite running in a Docker container
- Use a community Firebase emulator Docker image (e.g., `andreysenov/firebase-tools` or `spine3/firebase-tools` or similar well-maintained image)
- Expose ports: 4000 (Emulator UI), 8080 (Firestore), 9099 (Auth)
- **CRITICAL**: Ports MUST be bound to `0.0.0.0` (e.g., `"0.0.0.0:8080:8080"`) because the candidate's local React Native app needs to reach the droplet over the network — unlike Redis/Postgres tasks where the candidate SSHs into the droplet, here the candidate's phone/emulator connects directly
- Mount firebase.json and seed data into the container
- **MUST NOT include any version specification** in docker-compose.yml
- **MUST NOT include environment variables or .env file references**

### firebase.json Instructions:
- Configure Firestore emulator on port 8080
- Configure Auth emulator on port 9099
- Configure Emulator UI on port 4000
- Set `"host": "0.0.0.0"` for each emulator so they are accessible from outside the container
- Optionally include Firestore rules file if the task involves security rules
- Optionally reference seed data import directory

### Run.sh Instructions:
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker-compose up -d` and ensures successful deployment
- **CRITICAL**: This script MUST work perfectly without any errors
- WAIT MECHANISM: Implements proper health check to wait for Firebase Emulators to be fully ready (curl to `http://localhost:4000` or `http://localhost:8080`)
- SEED DATA: If the task requires pre-populated data, seed it into Firestore emulator after it starts (using curl to the Firestore REST API or a seed script)
- MONITORING: Monitors container status and provides feedback on successful deployment
- ERROR HANDLING: Includes proper error handling but should not encounter errors in normal execution
- LOCATION: All files are located in /root/task directory
- **SUCCESS CONFIRMATION**: Script should clearly indicate successful deployment completion

### kill.sh Instructions:
- Stop and remove all containers created by docker-compose
- Remove all associated Docker volumes and networks
- Force-remove all Docker images related to this task
- Run `docker system prune -a --volumes -f`
- Delete the entire `/root/task/` folder
- Script should be idempotent (safe to run multiple times)
- Use `set -e` at top, `|| true` where necessary
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

**CRITICAL**: Do NOT include `"sdkVersion"` in app.json — it is deprecated.

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

**CRITICAL**: The `"main"` field MUST be `"expo/AppEntry.js"`.
**CRITICAL**: Firebase JS SDK v10 (`"firebase": "^10.12.0"`) uses the modular v9+ API (import from `firebase/app`, `firebase/firestore`, `firebase/auth`).

Note: Add additional dependencies as needed (e.g., @react-navigation/native, @react-navigation/native-stack, react-native-safe-area-context, react-native-screens). Only include packages actually used in the starter code.

### Firebase Configuration File (src/config/firebase.js):
The React Native app MUST include a Firebase config file that connects to the emulators on the droplet:

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

**CRITICAL**: The `DROPLET_IP` will be replaced with the actual droplet IP during deployment. Use `'<DROPLET_IP>'` as a placeholder in the generated code. The `firebaseConfig` values can be dummy values (e.g., `'demo-key'`, `'demo-project'`) because emulators don't validate them.

### babel.config.js MUST include:
module.exports = function(api) {{
  api.cache(true);
  return {{
    presets: ['babel-preset-expo'],
  }};
}};

## README.md STRUCTURE (React Native + Firebase Basic)

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific business scenario, what the app does, and what Firebase features are involved. Explain what is working and what is broken/missing. NEVER generate empty content.

### Firebase Emulator Access

Provide connection details:
- Firestore Emulator: `http://<DROPLET_IP>:8080`
- Auth Emulator: `http://<DROPLET_IP>:9099`
- Emulator UI (for inspecting data): `http://<DROPLET_IP>:4000`
- Note that the React Native app is already configured to connect to these emulators

### Objectives (3-5 bullets MAX)

- Clear, measurable goals for basic level
- Focus on Firebase CRUD, auth flows, and data display
- **CRITICAL**: Objectives describe the "what", never the "how".

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
- Use bullet points starting with "Consider", "Think about", "Explore", "Review"
- **CRITICAL**: Guide discovery, never provide direct solutions.

### How to Verify (3-5 bullets MAX)

- Observable behaviors on device/emulator AND in the Firebase Emulator UI
- Include checking Firestore data in the Emulator UI at `http://<DROPLET_IP>:4000`
- **CRITICAL**: Focus on measurable, verifiable outcomes.

### NOT TO INCLUDE:
- SETUP INSTRUCTIONS for the droplet or Docker (already deployed)
- How to run run.sh or docker-compose (already done)
- Direct solutions or hints
- Specific Firebase SDK method names that reveal the solution
- npm install or npx expo start instructions

## REQUIRED OUTPUT JSON STRUCTURE
{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters.",
  "question": "Short description of the scenario and specific ask from the candidate.",
  "code_files": {{
    "README.md": "Candidate-facing README following structure above",
    ".gitignore": "Comprehensive React Native/Expo/Node.js exclusions",
    "package.json": "Dependencies including expo, react-native, firebase",
    "app.json": "Expo app configuration",
    "babel.config.js": "Babel configuration for Expo",
    "App.js": "Main App component (entry point)",
    "src/config/firebase.js": "Firebase SDK initialization connecting to droplet emulators",
    "src/screens/ScreenName.js": "Screen component files",
    "src/components/ComponentName.js": "Reusable component files",
    "docker-compose.yml": "Firebase Emulator Suite container (MUST WORK PERFECTLY)",
    "firebase.json": "Firebase emulator configuration",
    "run.sh": "Deployment script for droplet (MUST WORK PERFECTLY)",
    "kill.sh": "Cleanup script for droplet",
    "seed_data.sh": "Optional: script to seed Firestore with test data",
    "additional_file.js": "Other source files as needed"
  }},
  "outcomes": "Bullet-point list in simple language. Must include expected results and one bullet: 'Write production-level clean code with best practices including proper naming conventions, error handling, and code organization.'",
  "short_overview": "Bullet-point list: (1) business problem, (2) implementation goal, (3) expected outcome. but no need to mention in the start which point it belongs to. Just a concise 3-4 sentence overview.",
  "pre_requisites": "Bullet-point list: Node.js 18+, npm/yarn, Expo CLI, Expo Go app, Git, JavaScript/React Native knowledge, basic Firebase concepts (Firestore, Auth).",
  "answer": "High-level solution approach",
  "hints": "Single line suggesting focus area. Must NOT give away the answer.",
  "definitions": {{
    "Firestore": "Firebase's NoSQL cloud database that stores data in documents organized into collections",
    "Firebase Authentication": "Firebase service for managing user sign-up, sign-in, and identity",
    "Firebase Emulator": "Local version of Firebase services for development and testing without needing a real Firebase project",
    "onSnapshot": "Firestore method that listens for real-time updates to a document or query",
    "onAuthStateChanged": "Firebase Auth method that listens for changes to the user's sign-in state"
  }}
}}

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore covering React Native/Expo exclusions (node_modules, .expo/, dist/), Firebase exclusions (firebase-debug.log, firestore-debug.log, ui-debug.log), Docker exclusions, IDE configs, environment files, and OS artifacts.

## CRITICAL REMINDERS

1. **Infrastructure files (docker-compose.yml, run.sh, kill.sh, firebase.json) MUST work perfectly** on the droplet
2. **React Native starter code must be runnable** with `npx expo start` but must NOT contain the core logic solution
3. **Firebase SDK must be initialized and connected to emulators** — the config file connecting to the droplet must be provided
4. **NO comments** that reveal the solution or give hints
5. **Task must be completable within {minutes_range} minutes**
6. **Focus on fundamental React Native + Firebase concepts** appropriate for BASIC level
7. **Use Firebase JS SDK v9+ modular API** (import from 'firebase/firestore', 'firebase/auth')
8. **Use functional components with hooks exclusively**
9. **Firestore emulator ports must be accessible from outside the droplet** (bind to 0.0.0.0)
10. **Use `<DROPLET_IP>` as placeholder** in the React Native Firebase config — it will be replaced during deployment
11. **All Docker/script paths must reference /root/task** as the base directory
12. **"title"** must be in `<action verb> <subject>` format
13. **Seed data**: If the task requires existing data in Firestore, include a seed script that populates the emulator after startup
"""
PROMPT_REGISTRY = {
    "Firebase (BASIC), React Native (BASIC)": [
        PROMPT_REACT_NATIVE_FIREBASE_BASIC_CONTEXT,
        PROMPT_REACT_NATIVE_FIREBASE_BASIC_INPUT_AND_ASK,
        PROMPT_REACT_NATIVE_FIREBASE_BASIC_INSTRUCTIONS,
    ]
}
