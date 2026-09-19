# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_DOCKER_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A software engineer or DevOps engineer with 1-2 years of Docker experience is expected to build, run, and troubleshoot small containerized applications on a single host. They should understand Dockerfiles, image layers, build context, .dockerignore, CMD/ENTRYPOINT behavior, exposed ports, environment variables, volumes, container users, and basic runtime verification. They are not expected to design advanced orchestration, Kubernetes deployments, or complex multi-host networking.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_DOCKER_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Docker assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario
- The task complexity must be appropriate for BASIC Docker proficiency and 1-2 years of practical Docker experience
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic Docker containerization problems encountered in day-to-day development or simple deployment workflows
- The application code itself must be small, correct, dependency-light, and already working when containerized correctly
- The bugs the candidate fixes MUST live in the Docker layer, not in the host application source code

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, host application stack, and Docker deployment problem the candidate will be solving)
2. What will the task look like? (Describe the Dockerfile/container runtime defects, expected deliverables, and how it aligns with BASIC Docker proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_DOCKER_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Docker, you are given a list of real world scenarios and proficiency levels for Docker.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a small, FULLY FUNCTIONAL host application whose source code is correct, but whose Docker packaging has basic deployment defects that require foundational Docker skills.
The candidate's responsibility is to identify and fix the Docker-layer issues. You must be careful about not giving away the solution or even hinting at it in your task definitions.

**CRITICAL**: The task is a Docker assessment, not an application programming assessment. Defects MUST be placed in Dockerfile instructions, build context, .dockerignore, ENTRYPOINT/CMD, EXPOSE/port behavior, environment variables, volume paths, permissions, user configuration, health checks, image size/layer choices, or container runtime flags/scripts. Defects MUST NOT be placed in the application source code.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL and small host application paired with a Docker setup that needs basic repair. The application includes:
- Correct application source code that requires NO modifications
- A small, flat project structure suitable for BASIC level work
- One mainstream host application stack chosen to fit the selected scenario: Node.js, Go, or Java
- Dependency-light implementation using standard library or near-standard library choices
- Docker packaging files with 3-4 focused Docker defects at most
- A verification script that builds and runs the container and checks observable behavior

The candidate's responsibility is to inspect the Docker configuration, build and run the image, diagnose basic containerization issues, and make the service run reliably from the container. The candidate should demonstrate basic Docker knowledge around build context, Dockerfile authoring, image size, port mapping, runtime configuration, file permissions, and container startup behavior.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the basic Docker containerization scenario
- **MANDATORY**: The task MUST be derived from and aligned with the provided input_scenarios. Use the scenario's business context, domain, and deployment need as the foundation
- **CRITICAL**: The selected task MUST pair Docker with exactly ONE mainstream host application stack: Node.js, Go, or Java. Choose the stack that best fits the scenario and vary the stack across generated tasks; do not always choose the same one
- **CRITICAL**: The application code must be SMALL, CORRECT, and dependency-light. The candidate must not need to modify application source files to complete the task
- **CRITICAL**: Bugs the candidate fixes must live in the Docker layer only — Dockerfile instructions, ENTRYPOINT/CMD, build context, .dockerignore, exposed ports, environment variables, volumes, permissions, image size/layer mistakes, or runtime configuration
- BASIC level: use a single service, one Dockerfile, small flat file structure, run.sh, README.md, .gitignore, optional .dockerignore, and a verification script. Keep the task focused with 3-4 Docker defects maximum
- Do NOT create complex microservices, Kubernetes manifests, advanced CI/CD pipelines, rootless Docker tasks, custom Docker plugins, or deep performance tuning beyond basic layer/build-context/image-size hygiene
- The app works when containerized correctly. Do not place broken logic, failing tests, missing handlers, incorrect routes, or business defects in the application source code
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are relevant to the selected scenario
- The complexity must align with BASIC proficiency (1-2 years Docker experience) requiring foundational Docker techniques including:
  - Understanding official base images and slim/alpine variants
  - Writing and correcting basic Dockerfile instructions
  - Using WORKDIR, COPY, RUN, ENV, CMD, ENTRYPOINT, EXPOSE, USER, LABEL, and HEALTHCHECK appropriately
  - Respecting .dockerignore and build context boundaries
  - Understanding container startup, process lifecycle, logs, and exit codes
  - Understanding port mapping and container-vs-host ports
  - Passing simple environment configuration into a container
  - Handling basic file permissions and non-root runtime users
  - Keeping images small through simple layer ordering and avoiding unnecessary files
  - Using docker build, docker run, docker logs, docker inspect, and docker exec for troubleshooting
- Questions must NOT hint at the specific Docker defects. Hints are provided separately in the "hints" field
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks
- **FILE LOCATION**: All code and scripts are generated under /root/task in the E2B environment. However, run.sh and verification scripts MUST use repo-root-relative path discovery such as `cd "$(dirname "$0")"` and MUST NOT hardcode `/root/task`, so the same commands work in the sandbox and in a candidate's local clone
- Time constraint: The task MUST be completable within {minutes_range} minutes

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Docker documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The task is designed to assess the candidate's ability to diagnose and fix basic Docker containerization issues rather than testing rote memorization
- AI tools can help candidates recall Docker syntax, but the task should still require understanding of build context, container process behavior, ports, image layers, and runtime configuration
- The generated task must be concrete enough for candidates to verify their result locally through container behavior and provided checks

## Docker Generation Instructions
Based on the real-world scenarios provided, create a Docker BASIC task that:
- Draws inspiration from the input_scenarios given above to determine the business context and deployment need
- Uses exactly ONE host application stack selected from Node.js, Go, or Java
- Keeps the host application dependency-light and fast to build
- Uses only slim/alpine base images:
  - Node.js: `node:20-alpine`
  - Go: `golang:1.22-alpine` for build and `alpine` or another small runtime stage where appropriate
  - Java: `eclipse-temurin:21-jre-alpine` for runtime and a lightweight build approach only when needed
- Pre-pulls the relevant base image(s) in run.sh before building
- Creates a Dockerfile that is intentionally flawed but close enough for a BASIC candidate to diagnose
- Places 3-4 focused defects in Docker packaging only, never in the application code
- Includes a verification script that builds the image, runs the container, and asserts observable behavior such as:
  - Container responds on the expected port
  - Environment configuration is honored
  - Expected files are present at runtime or generated in the right location
  - Container runs as the expected user or avoids root when appropriate
  - Container exits cleanly or remains healthy depending on the scenario
- Avoids large dependency installations, heavyweight frameworks, slow builds, and large sample datasets
- Ensures all generated commands in run.sh and verification scripts are repo-root-relative using the `cd "$(dirname "$0")"` pattern
- Produces a task where the fresh starter may fail the verification checks because the Docker defects are intentionally present, but the application source itself is correct

## Infrastructure Requirements
**DEPLOYMENT ROBUSTNESS - CRITICAL REQUIREMENTS:**

1. **Host Application Stack Pairing:**
   - Choose exactly ONE of Node.js, Go, or Java based on the selected scenario
   - Do not include multiple application stacks in the same task
   - Keep the application small, correct, and fast to build
   - Application source code must have no TODOs, no placeholders, and no candidate-required source edits

2. **Dockerfile Defect Placement:**
   - Dockerfile must contain the candidate-facing defects
   - Defects may involve incorrect or inefficient COPY ordering, missing or wrong WORKDIR, missing runtime file, wrong CMD/ENTRYPOINT form, mismatched port exposure, missing ENV defaults, unnecessary build-context bloat, root-only runtime path, missing executable permission, or avoidable image-size mistakes
   - Defects must be realistic and observable through build/run behavior
   - Keep to 3-4 focused defects maximum for BASIC level

3. **No Unnecessary External Services:**
   - Default to a single-service Docker task
   - Do NOT add a database, cache, broker, search engine, or compose stack unless the selected scenario genuinely requires a second service
   - If a second service is genuinely needed, include docker-compose.yml and keep it simple
   - No kill.sh is needed. E2B sandboxes are destroyed as a whole when the session ends

4. **Verification Design:**
   - Include a shell or pytest verification script such as `verify.sh` or `tests/test_container_behavior.py`
   - The verification script must build the image, run the container, check observable behavior, print useful failure messages, and clean up its own temporary container by name
   - The verification script must use repo-root-relative paths, not `/root/task`
   - The verification script must not require the candidate to install the host runtime locally; Docker is the runtime boundary

### Docker-compose Instructions
- For the default BASIC Docker task, DO NOT generate docker-compose.yml because the task is a single-service containerization exercise
- Generate docker-compose.yml only when the selected scenario genuinely needs a second service
- If docker-compose.yml is generated, it MUST NOT include any version specification
- If a datastore service is included, set required initialization environment variables inline in `environment:` using hardcoded service-local values; forbid `.env` files and `${{VAR}}` host indirection
- **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every external service exposed to the host
- Use simple service names, clear health checks, and minimal networking
- Do not include advanced compose profiles, Swarm-only options, Kubernetes manifests, or multi-host orchestration

### External Service Configuration Instructions
- Do not create `init_database.sql`, seed scripts, or datastore configuration unless the scenario genuinely requires a second service
- For this Docker BASIC task, prefer no datastore and no second service
- If a second service is truly required, keep initialization minimal and make the Docker defect remain in the application container layer, not in the datastore setup
- Ensure any healthcheck, connection string, and service environment values are consistent if a datastore is used
- Never expose datastore ports publicly; bind only to localhost

### Run.sh Instructions
- run.sh is required
- run.sh must use `#!/usr/bin/env bash` and robust shell options while still handling expected verification failures clearly
- run.sh must start from the repository root using:
  - `cd "$(dirname "$0")"`
- run.sh MUST NOT hardcode `/root/task`
- run.sh must pre-pull the selected base image(s) before building, for example `docker pull node:20-alpine`, `docker pull golang:1.22-alpine`, or `docker pull eclipse-temurin:21-jre-alpine`
- run.sh should execute a deployability/readiness check:
  - Confirm Docker is available
  - Pre-pull base image(s)
  - Build the image from the repo root
  - Run the container with deterministic name and localhost port mapping
  - Wait for the service to respond or for expected runtime behavior
  - Print container logs on failure
  - Clean up the temporary container it created
- If a verification script is included and is expected to fail on the unsolved starter, run.sh must treat that as an expected candidate-work signal only if the project still builds and the container runner executed. It must exit non-zero only when Docker cannot build/run/collect the check at all
- If docker-compose.yml is genuinely included, run.sh must use `docker compose up -d` and must wait for health without running a grader test suite designed to fail before the candidate fixes the task
- All commands must be compatible with Docker on Ubuntu in the E2B build/test gate

### Dockerfile Instructions
- A Dockerfile is required
- Use only slim/alpine base images appropriate to the selected host stack
- The Dockerfile should be close to correct but include 3-4 BASIC Docker defects for the candidate to fix
- The Dockerfile must not require a local Node.js, Go, or Java installation on the host
- The Dockerfile should be small enough to build quickly in E2B
- Do not use heavyweight base images, package managers for unnecessary tools, or large dependency installation steps
- Defects must be Docker-related and observable, not application-source defects
- Examples of appropriate BASIC Docker defect categories include:
  - Build context includes unnecessary files because .dockerignore is missing or incomplete
  - COPY paths do not match the intended runtime layout
  - CMD/ENTRYPOINT starts the wrong process or uses a fragile shell form
  - Port documented by the app does not match exposed/runtime port configuration
  - Required runtime ENV default is missing or incorrect
  - Runtime user cannot read or write required directories
  - Final image carries unnecessary build artifacts
- Do not include solution comments in the Dockerfile

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - Dockerfile (candidate-facing Dockerfile with BASIC Docker-layer defects)
  - run.sh (repo-root-relative deployability/readiness script that pre-pulls base images)
  - verify.sh or tests/test_container_behavior.py (builds/runs/checks observable container behavior using repo-root-relative paths)
  - .gitignore (standard development and Docker exclusions)
  - .dockerignore (may be missing, incomplete, or intentionally flawed if it is one of the selected Docker defects)
  - Host application source files for exactly one stack: Node.js, Go, or Java
  - Runtime-native manifest only when needed by the selected stack, such as package.json, go.mod, or a minimal Java build file
  - docker-compose.yml only if the scenario genuinely needs a second service

## Code file requirements
- The host application source code must be complete, correct, dependency-light, and require NO modifications
- Keep a small flat structure appropriate for BASIC level, for example:
  - `app/` containing source files
  - `Dockerfile`
  - `run.sh`
  - `verify.sh` or `tests/test_container_behavior.py`
  - `.gitignore`
  - optional `.dockerignore`
  - optional stack manifest such as `package.json` or `go.mod`
- Node.js tasks should prefer built-in `http` and minimal package.json scripts
- Go tasks should prefer standard `net/http` and a small go.mod
- Java tasks should prefer a tiny HTTP server or simple executable with minimal build complexity
- Do not generate application bugs, missing routes, failing business logic, or TODO comments in application source
- Do not include comments in any file that reveal the Docker fixes
- The verification script must assert observable behavior from the container, not inspect a hidden answer
- The starter repo may contain flawed Docker packaging, but application source must be immediately understandable and correct
- **FILE LOCATION**: All files are generated under /root/task in E2B, but scripts and tests must use repo-root-relative path discovery and must not hardcode `/root/task`

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for a small Docker task that includes:
- OS files: .DS_Store, Thumbs.db, desktop.ini
- IDE/editor files: .idea/, .vscode/, *.swp, *.swo, *~
- Logs and temporary files: *.log, logs/, tmp/, *.tmp, *.bak
- Docker/local artifacts: .docker/, docker-data/, container-logs/
- Node artifacts when Node.js is selected: node_modules/, npm-debug.log*, dist/, coverage/
- Go artifacts when Go is selected: bin/, *.test, *.out, coverage.out
- Java artifacts when Java is selected: target/, build/, out/, *.class, *.jar
- Environment files: .env, .env.local

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains EXACTLY the following sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Do NOT add Database Access, Application Access, Setup, Installation, Commands, Architecture, Known Issues, or NOT TO INCLUDE as README sections.

### Task Overview
- Must be 3-4 meaningful sentences
- No bullet list
- Describes the business scenario, current deployment state, and why reliable containerization matters
- Must state that the application behavior is already correct and the work is focused on Docker packaging/runtime reliability
- NEVER empty
- NO bold time-budget callouts
- Do not enumerate the Docker defects
- Do not name specific Dockerfile instructions, flags, file paths, or commands that reveal the fix

### Objectives
- BASIC level objectives for this Docker task MUST still be SHORT and OPEN-ENDED because this assessment focuses on Docker troubleshooting
- Include 4-6 bullets max
- Each objective must be one natural sentence, roughly 8-18 words
- Each objective must state a desired outcome from the operator's or user's point of view
- NEVER enumerate the defects
- NEVER say "currently does X"
- NEVER name Dockerfile instructions, flags, files, directories, commands, APIs, functions, or exact configuration knobs
- Good objective style: "The service must come up ready to serve traffic with a single documented command."
- Bad objective style: "The Dockerfile currently copies the wrong directory; fix the COPY instruction."
- Objectives may be concrete about WHAT outcome matters, but must not reveal HOW to fix it

### Helpful Tips
- Include 4-5 bullets max
- Provide practical guidance without revealing specific implementations
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze"
- Tips guide discovery and MUST NOT name the specific Dockerfile instruction, Docker command, flag, file path, method, pattern, or exact configuration that solves the task
- Focus on general Docker troubleshooting habits, container logs, runtime behavior, build context, ports, configuration, permissions, and image contents without giving direct fixes

### How to Verify
- Include 3-5 bullets max
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write
- Each bullet is a check the candidate can run or observe, such as build completion, container response, expected response shape, log output, clean shutdown, image size trend, or runtime configuration behavior
- You may mention that the included verification script exercises the container, but do not provide step-by-step fix instructions
- Do not include setup commands like `npm install`, `go build`, `docker compose up`, or package installation commands

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README.md:
- Setup commands such as `npm install`, `go build`, `docker build`, `docker run`, `docker compose up`, `mvn test`, or package installation commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific Dockerfile instruction names, Docker flags, method names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets or Docker snippets that give away the answer
- Defect enumeration such as "the wrong port is exposed" or "the copy path is wrong"
- Directive phrases like "you should implement", "add this instruction", "create this file", "use this flag", or "fix the CMD"
- Database connection details, droplet IP placeholders, usernames, passwords, or client-tool suggestions

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "A kebab-case GitHub repository name under 50 characters that reflects the selected scenario and Docker containerization focus.",
   "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name.",
   "question": "A full candidate-facing task description describing the selected business scenario, the correct small application, and the Docker-layer reliability problem to solve without naming the exact defects or giving the implementation away.",
   "code_files": {{
      "README.md": "Candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — plain unmarked text section names are INVALID. Concise and non-revealing.",
      ".gitignore": "Comprehensive ignore file for the selected host stack, Docker-local artifacts, logs, IDE files, OS files, and environment files.",
      ".dockerignore": "A Docker build-context ignore file that may be missing, incomplete, or intentionally flawed only if that is one of the BASIC Docker defects.",
      "Dockerfile": "Candidate-facing Dockerfile using the selected slim or alpine base image and containing 3-4 focused BASIC Docker-layer defects, with no solution comments.",
      "run.sh": "Repo-root-relative deployability script that pre-pulls base image(s), builds the image, runs a readiness check, prints useful diagnostics, and avoids hardcoded /root/task paths.",
      "verify.sh": "Repo-root-relative shell verification script that builds the image, runs the container, checks observable behavior, prints clear failures, and cleans up temporary containers.",
      "app/<source files>": "Complete, correct, small host application source for exactly one selected stack, requiring no candidate source-code changes.",
      "<runtime manifest if needed>": "Minimal runtime-native manifest such as package.json or go.mod only when required by the selected stack, kept dependency-light and fast to build.",
      "docker-compose.yml": "Include this file only if the scenario genuinely requires a second service; if included it must omit version, bind exposed service ports to localhost, and keep configuration minimal."
   }},
   "answer": "Evaluator-facing high-level solution approach explaining the Docker-layer categories a correct fix should address, without requiring application source-code changes.",
   "definitions": "An object mapping Docker and containerization terms relevant to the generated task to concise definitions useful for BASIC candidates.",
   "hints": "A single line nudging investigation toward Docker build and runtime behavior without naming the exact defective instruction, flag, file, or fix.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable container build success, runtime availability, correct configuration behavior, and reliable verification output. Use simple english.",
   "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Docker CLI familiarity, basic Dockerfile understanding, and comfort reading small Node.js, Go, or Java services; do not include setup or verification steps.",
   "short_overview": "A bullet list summarising the business problem, Docker packaging focus, and expected reliable container outcome."
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be kebab-case and under 50 characters
3. **title** must be human-readable, 50-80 characters, in '<action verb> <subject>' format, and different from name
4. **Dockerfile, run.sh, README.md, .gitignore, and a verification script are required**
5. **docker-compose.yml is optional and must be included only when the scenario genuinely needs a second service**
6. **Do not include kill.sh** — E2B sandboxes are destroyed as a whole
7. **Application source code must be correct and require NO modifications**
8. **All candidate-facing defects must live in the Docker layer only**
9. **BASIC level means one service by default, one Dockerfile, small flat structure, and 3-4 focused Docker defects maximum**
10. **run.sh must pre-pull selected base image(s) before building**
11. **run.sh and verification scripts must use repo-root-relative paths and must NOT hardcode /root/task**
12. **README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each as a markdown heading (## Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — plain unmarked section-name lines are INVALID**
13. **README Objectives must be short, open-ended, natural one-line outcomes and must not enumerate defects or name files, commands, flags, or Dockerfile instructions**
14. **Use only slim/alpine base images and keep builds fast**
15. **Task must be completable within {minutes_range} minutes for BASIC Docker proficiency**
"""

PROMPT_REGISTRY = {
    "Docker (BASIC)": [
        PROMPT_DOCKER_BASIC_CONTEXT,
        PROMPT_DOCKER_BASIC_INPUT_AND_ASK,
        PROMPT_DOCKER_BASIC_INSTRUCTIONS,
    ]
}