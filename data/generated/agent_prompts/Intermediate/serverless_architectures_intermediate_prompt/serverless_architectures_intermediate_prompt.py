# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, particularly in relation to designing, operating, and improving serverless event-driven systems?
"""

PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Serverless Architectures assessment task.

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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (intermediate: 3-5 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, serverless architecture context, and operational problem the candidate will be solving)
2. What will the task look like? (Describe the type of serverless workflow, infrastructure, reliability, observability, or event-driven improvement required, the expected deliverables, and how it aligns with the intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in serverless architectures, event-driven systems, and cloud-native operations, you are given a list of real world scenarios and proficiency levels for Serverless Architectures.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL local serverless-style environment and a realistic infrastructure/code scaffold with operational, reliability, security, cost, or event-flow issues that require intermediate-level serverless architecture skills.
The candidate's responsibility is to analyze the existing workflow, identify the issues, and improve the system without being told the exact solution. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL serverless project that can be deployed locally through Docker Compose using a serverless cloud emulator such as LocalStack. The project includes:
- Infrastructure-as-code for a realistic event-driven serverless workflow using managed-service equivalents such as functions, API gateways, event buses, queues, topics, NoSQL tables, object storage, logs, and alarms as appropriate to the selected scenario
- Function or handler code that is already runnable but has realistic gaps in reliability, idempotency, retries, error handling, event contracts, observability, IAM-style permissions, cost controls, or operational readiness
- Sample events, request payloads, and local verification scripts that reproduce the scenario symptoms without requiring access to a real cloud account
- A docker-compose.yml file that starts the required local infrastructure services for the selected scenario
- A run.sh readiness script that starts the infrastructure, waits for services to become healthy, initializes the local serverless resources, validates that the starter project deploys or loads, and exits successfully on the unsolved starter

The candidate's responsibility is to investigate the existing serverless workflow, make appropriate changes across infrastructure and supporting code, and demonstrate that the system behaves reliably under the scenario constraints. A part of the task completion is to watch the candidate reason through event-driven design, managed-service trade-offs, operational safety, observability, and cost/performance considerations at an intermediate level (3-5 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level serverless architecture improvement scenario
- Task must provide a working local serverless-style project with existing infrastructure-as-code, sample events, scripts, and realistic function/handler code; it must NOT be a blank design exercise or a pure essay
- **CRITICAL**: The generated project should be FULLY FUNCTIONAL and deployable locally, but it should exhibit realistic symptoms that require the candidate to inspect event flow, cloud-service configuration, handler behavior, and operational signals before deciding what to change
- **CRITICAL**: The candidate-facing question and README must describe business symptoms and expected outcomes, not the exact mechanisms or configuration changes needed to solve them
- **CRITICAL**: Do not hard-code the selected scenario's solution into the README, file comments, hints, objectives, or verification steps. The code and infrastructure may contain the flawed implementation, but comments must not label the flaw or point to the fix
- The task should be based on ONE selected real-world scenario and should closely match its domain, workflow, symptoms, and constraints
- The generated task must stay within intermediate Serverless Architectures scope: managed compute, managed APIs, event buses, queues, topics, NoSQL/object storage, workflow/orchestration, event contracts, retries, dead-letter handling, concurrency, cold-start/performance reasoning, least-privilege permissions, observability, cost-aware configuration, and infrastructure-as-code
- Avoid requiring expert-only topics such as multi-region active-active architecture, deep provider internals, custom platform engineering, advanced formal verification, or exact memorization of cloud-provider CLI syntax
- The question should be a real-world business scenario requiring intermediate-level analysis and implementation across more than one file
- The starter codebase MUST be substantial and realistic, NOT a toy snippet. Require MULTIPLE interacting modules/files in a real project layout, with non-trivial existing logic the candidate must read and reason about before changing
- Changes should normally span more than one file, such as infrastructure definitions, handler logic, event fixtures, tests, documentation, or operational checks
- Time constraints: Each task should be finished within {minutes_range} minutes
- Ensure that the work can be completed by an intermediate candidate in the allotted time by keeping the workflow focused and bounded
- The candidate should not need a real cloud account; all deployability should be local through Docker Compose and the generated serverless emulator stack
- If the selected scenario needs a managed persistence or messaging resource such as a queue, event bus, topic, object store, or NoSQL table, model it through the local serverless emulator rather than inventing unrelated PostgreSQL, MySQL, MongoDB, Redis, or Elasticsearch services
- Only include postgres, mysql, mongo, redis, or elasticsearch services if the selected real-world scenario explicitly requires that datastore; otherwise do not add them just because they are available in the template
- The task should emphasize serverless reasoning around events, triggers, retries, delivery semantics, state, permissions, observability, cost, and operational readiness rather than traditional server administration
- The question must NOT include hints about the specific fixes needed. The hints will be provided only in the "hints" field and must still avoid revealing the solution
- Ensure that all questions and scenarios adhere to current serverless best practices while avoiding provider-specific trivia
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, AWS/Azure/GCP serverless documentation, Terraform documentation, Serverless Framework documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and improve realistic serverless architecture issues at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the tasks should require genuine intermediate-level serverless engineering judgment, event-driven reasoning, and operational problem-solving skills that go beyond simple copy-pasting from a generative AI
- Candidates will be encouraged to use AI to help with boilerplate, documentation lookup, and troubleshooting, but not replace their own thinking and diagnostic skills

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Serverless Architectures task that:
- Draws inspiration from the input_scenarios given below to determine the business context, event flow, managed-service choices, operational symptoms, and constraints
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for serverless architecture reasoning
- Tests practical intermediate-level serverless implementation, review, debugging, and operational improvement skills
- Uses infrastructure-as-code as the main project artifact, such as Terraform, Serverless Framework, SAM-style templates, or equivalent declarative definitions appropriate to the selected scenario
- Includes realistic local function or handler code only as needed to make the serverless workflow concrete and testable
- Uses a local cloud emulator such as LocalStack for AWS-style serverless services when the selected scenario is AWS-oriented
- If the selected scenario is Azure- or GCP-oriented, still keep the local scaffold practical and self-contained; use a local emulator, mockable managed-service equivalent, or provider-neutral infrastructure representation only when it can be deployed and verified locally without a real cloud account
- For AWS-style scenarios, prefer LocalStack-backed services such as Lambda, API Gateway or HTTP endpoints where practical, EventBridge, SQS, SNS, DynamoDB, S3, CloudWatch-style logs, or Step Functions equivalents as appropriate to the scenario
- Do not include unrelated external datastores. The local infrastructure must match the selected scenario's actual serverless resources and not add PostgreSQL, MySQL, MongoDB, Redis, or Elasticsearch unless the scenario explicitly requires them
- Include sample events, request fixtures, and/or lightweight scripts that reproduce the observable symptoms of the selected scenario
- Include tests or verification scripts where appropriate, but do not make run.sh run a grader suite that is expected to fail until the candidate solves the task
- The starter must be deployable, readable, and realistic, with multiple interacting files such as:
  - docker-compose.yml for LocalStack or the selected local serverless emulator
  - run.sh for automated local readiness
  - infrastructure-as-code files under infra/
  - handler or function code under functions/ or src/
  - scripts for packaging, deployment, or local invocation
  - fixtures/events for sample events and payloads
  - tests or checks that candidates can run after making changes
  - README.md and .gitignore
- **CRITICAL**: The scenario description must be reflected in the actual files. If the question describes duplicate side effects, dropped messages, unexpected retries, missing operational visibility, unsafe public access, cost spikes, timeout symptoms, or schema compatibility issues, the generated scaffold must contain the corresponding flawed behavior or configuration without comments that reveal the fix
- **CRITICAL**: The task focuses on improving an existing serverless workflow, NOT building a serverless platform from scratch
- **CRITICAL**: Keep exact solution choices out of candidate-facing instructions. Explain symptoms, constraints, and desired outcomes; allow multiple valid approaches within serverless best practices

## Infrastructure Requirements
- MUST include docker-compose.yml for the local infrastructure services required by the selected scenario
- MUST include run.sh using `docker compose up -d` to start the required local infrastructure
- MUST NOT include kill.sh; E2B sandboxes are destroyed as a whole and do not need per-task cleanup scripts
- The infrastructure setup is AUTOMATED - candidates will receive a project that can be brought up by the readiness script and should not be asked to manually install or configure cloud services
- The default serverless infrastructure service for AWS-style scenarios should be LocalStack, exposing only the local edge endpoint needed for the task
- The generated project must not require a real AWS, Azure, or GCP account, real cloud credentials, or remote endpoints
- Use hardcoded local development values where necessary for the emulator; do not use .env files or host-variable interpolation
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **CRITICAL**: run.sh is a readiness/self-check script, NOT the grader. It brings infrastructure up, waits for health, initializes or deploys the starter stack, verifies the starter compiles/loads or deploys, performs a lightweight smoke check, then exits 0 on the UNSOLVED starter

### Docker-compose Instructions
  - Include the local serverless emulator service required by the selected scenario, such as LocalStack for AWS-style serverless resources
  - Configure only the managed-service emulations needed by the selected scenario, such as functions, queueing, event routing, NoSQL tables, object storage, logs, or workflow services
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every service exposed to the host
  - For LocalStack, bind the edge port to localhost only, for example `127.0.0.1:4566:4566`
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include .env file references or host-variable interpolation syntax**
  - Inline service environment values are allowed when required for a container to initialize correctly
  - Use hardcoded local configuration values for emulator services, regions, access keys, and local endpoints
  - Include healthchecks for infrastructure services so run.sh can wait reliably
  - Include named volumes only if persistence is needed for the local emulator between commands
  - If the selected scenario explicitly requires PostgreSQL, MySQL, MongoDB, Redis, or Elasticsearch in addition to serverless resources, include only the required datastore and bind its exposed port to localhost
  - For PostgreSQL services, environment must set POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB inline in the service definition; the init SQL, healthcheck, and connection string must use the same user/database
  - For MySQL services, environment must set the required MYSQL_* initialization variables inline in the service definition; the init SQL, healthcheck, and connection string must use the same user/database
  - Do not add init_database.sql unless a SQL database is explicitly part of the selected scenario
  - Docker Compose should handle container orchestration and local infrastructure availability; manual cloud setup must not be required

### LocalStack Serverless Configuration Instructions
- Generate local serverless infrastructure that is complete enough for the selected scenario and deployable without real cloud credentials
- Include infrastructure-as-code files under `/root/task/infra` that define the required functions, event sources, permissions, queues, topics, event buses, tables, buckets, alarms, or workflow resources
- Keep resource names, tags, and ownership metadata realistic and consistent with the selected business domain
- Include local endpoint/provider configuration so Terraform or the selected IaC tool targets the emulator rather than a real cloud account
- Include scripts or make targets only when they help package or deploy the local serverless resources
- Do not require candidates to memorize exact provider CLI syntax; provide enough scaffold for them to inspect and modify the architecture
- Include sample event fixtures under `/root/task/fixtures` that exercise the workflow symptoms from the selected scenario
- If function code is included, it should be complete and runnable but contain realistic serverless design or operational issues aligned with the selected scenario
- Do not include comments in IaC or handler code that identify the bug category, name the exact missing resource, or explain the solution
- Avoid fake cloud resources that cannot be deployed locally; the generated starter should pass a readiness deployment against the local emulator

### Run.sh Instructions
  - FIRST STEP: perform any project dependency initialization required by the generated scaffold, such as Terraform provider download, package-manager install for handler dependencies, or archive/package generation
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  - WAIT MECHANISM: Implements proper health checks to wait for the local serverless emulator and any explicitly required datastore to be fully ready and accepting connections
  - DEPLOYMENT VALIDATION: Initializes and applies the infrastructure-as-code against the local emulator, or otherwise validates that the generated serverless resources can be created successfully
  - STARTER SMOKE CHECK: Performs a lightweight smoke check that confirms the starter workflow can be invoked or that key resources exist, without requiring the candidate's final solution to be present
  - NO GRADER EXECUTION: run.sh MUST NOT run the final grader test suite or any tests intentionally designed to fail before the candidate solves the task
  - ERROR HANDLING: Includes proper error handling for failed container starts, failed local emulator readiness, failed dependency initialization, or failed starter deployment
  - MONITORING: Prints concise status messages showing dependency initialization, infrastructure startup, readiness, local deployment, and smoke-check results
  - LOCATION: All files are located in /root/task directory, and Docker paths must reference this location
  - The script must exit 0 when the unsolved starter is deployable and the local emulator smoke check runs successfully
  - The script must exit non-zero only when the scaffold cannot boot, dependencies cannot initialize, infrastructure cannot deploy, or the smoke check cannot run

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Ignore Terraform, local emulator, package, log, cache, and editor artifacts)
  - docker-compose.yml (Local serverless emulator and any explicitly required datastore service configuration)
  - run.sh (Readiness script to initialize dependencies, start infrastructure, wait for health, deploy local serverless resources, and smoke-check the starter)
  - infra/main.tf or equivalent IaC entrypoint (Complete serverless resources for the selected scenario)
  - infra/variables.tf and infra/outputs.tf or equivalent supporting IaC files
  - Function or handler files under functions/ or src/ when needed for the scenario
  - scripts/ files for packaging, deployment helpers, or local invocation if needed
  - fixtures/ event or request payloads that reproduce the scenario symptoms
  - tests/ or checks/ files only if useful for candidate verification; these must not be run as the readiness gate if they are expected to fail on the unsolved starter

## Code file requirements
- More than one file MUST be generated, and the project must be substantial enough for an intermediate candidate to inspect multiple interacting components
- All infrastructure-as-code files must be syntactically valid for the selected tool and target the local emulator by default
- All shell scripts must be valid Bash, executable in intent, and use `/root/task` as the base directory
- Handler or function code must be complete and runnable if included; do not include placeholder TODOs or incomplete stubs
- Do not include comments that give away the solution, identify the exact missing configuration, or label the intended fix
- Do not include fake tests that pass without exercising the scenario
- Do not include real cloud credentials, remote account IDs, production endpoints, or any instruction requiring a candidate to deploy outside the sandbox
- Use realistic event payloads, identifiers, timestamps, and business metadata, but avoid personal data or secrets
- The exact problem described in the task scenario must be present in the generated code or infrastructure
- The generated scaffold should be deployable locally before the candidate begins, even though the workflow behavior is intentionally flawed
- If a datastore service is explicitly included, its docker-compose healthcheck, connection values, init scripts, and verification commands must use localhost for host-facing access and consistent inline credentials where applicable
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for local serverless infrastructure development that includes:
- Terraform working directories and state files such as .terraform/, *.tfstate, *.tfstate.backup, and crash logs
- Serverless build artifacts, packaged archives, deployment bundles, and generated handler packages
- Local emulator data directories such as localstack/, data/, and temporary volume folders
- Runtime caches such as __pycache__/, *.pyc, node_modules/, .npm/, .pytest_cache/, coverage/, dist/, and build/ when relevant to generated files
- Environment and credential files such as .env, .env.local, credentials, and local override files
- Log files, temporary files, and shell output artifacts
- IDE and editor files such as .vscode/, .idea/, *.swp
- OS-specific files such as .DS_Store and Thumbs.db

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected intermediate-level serverless architecture scenario. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the specific workflow, symptoms, and operational constraints from the selected real-world scenario.

### Task Overview
- Must be 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the problem matters.
- It should explain observable symptoms and business impact without naming the exact solution.
- NEVER generate empty content.
- Do not include bold time-budget callouts.

### Objectives
- For INTERMEDIATE level, include 3-4 bullets max; fewer, tighter is better.
- Objectives MUST be concise and OPEN-ENDED.
- Each objective states ONE desired outcome in a single short line, roughly 8-16 words.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, algorithm, or config knob.
- Do NOT name any file, file path, directory, function, method, class, variable, table, resource name, or any other direct code reference.
- Do NOT pad objectives into two-clause "after your changes..." sentences.
- Good objective style: "Ensure repeated event delivery does not create repeated business side effects."
- Good objective style: "Improve workflow recovery so failed work remains visible and actionable."
- Bad objective style: "Add a dead-letter queue to the payment queue."
- Bad objective style: "Fix the createShipment handler in functions/createShipment.py."

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, resource, data structure, or algorithm that solves the task.
- Tips may refer to broad serverless ideas such as delivery semantics, downstream safety, operational visibility, event contracts, permissions, latency, and cost.
- Do not include direct commands, exact service names to add, or exact configuration knobs.

### How to Verify
- Include 3-5 bullets max.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as workflow behavior, response shape, repeated-event behavior, failure visibility, log correlation, latency, or local smoke output.
- Use localhost in any verification command that legitimately references the local emulator endpoint.
- Do not include cloud-account instructions, real cloud deployment steps, or droplet IP placeholders.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
- Setup commands such as package installs, docker compose commands, Terraform initialization, or test-runner commands
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, resource names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database connection details, remote host placeholders, cloud credentials, account IDs, or droplet IP placeholders
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this service", or "configure this policy"

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "A kebab-case GitHub repository name under 50 characters that summarizes the selected serverless workflow improvement task.",
   "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name and focused on the serverless workflow outcome.",
   "question": "A candidate-facing task description that explains the selected business scenario, the existing local serverless workflow, the observable symptoms, and the desired outcomes without revealing exact fixes.",
   "code_files": {{
      "README.md": "Candidate-facing README that follows exactly the required Task Overview, Objectives, Helpful Tips, and How to Verify sections with concise open-ended guidance.",
      ".gitignore": "A comprehensive ignore file for Terraform or equivalent IaC artifacts, local emulator data, generated packages, logs, caches, credentials, and editor files.",
      "docker-compose.yml": "Docker Compose configuration for the local serverless emulator and only the additional services explicitly required by the selected scenario, with no version specification and localhost-only port bindings.",
      "run.sh": "A Bash readiness script that initializes project dependencies, starts Docker Compose, waits for local infrastructure health, deploys the starter serverless resources, performs a smoke check, and does not run failing grader tests.",
      "infra/main.tf": "Primary infrastructure-as-code definition for the local serverless workflow resources, permissions, event sources, and operational configuration relevant to the selected scenario.",
      "infra/variables.tf": "Supporting infrastructure variables or local configuration values needed to keep the local deployment self-contained and readable.",
      "infra/outputs.tf": "Useful local outputs that help scripts and candidates discover emulator endpoints or resource identifiers without exposing a solution.",
      "functions/handler_file.ext": "Complete runnable function or handler code for the selected workflow, containing realistic existing behavior that candidates must inspect and improve.",
      "scripts/package_or_deploy.sh": "Optional helper script for packaging, deploying, or invoking the local serverless workflow when this makes the scaffold more realistic.",
      "fixtures/sample_event.json": "Representative event or request payloads that reproduce the selected scenario symptoms and support local verification.",
      "tests/or_checks/check_file": "Optional lightweight checks or tests candidates can run after changes; these should focus on observable workflow outcomes rather than revealing implementation details."
   }},
   "answer": "Evaluator-facing high-level solution approach describing the architectural reasoning, infrastructure changes, handler changes, operational safeguards, and trade-offs that a strong intermediate solution would address.",
   "definitions": "An object of serverless, event-driven, reliability, security, observability, and cost-related term-to-definition pairs that help evaluate the candidate's conceptual understanding.",
   "hints": "A single-line hint that nudges the candidate toward investigating event flow, operational signals, and failure behavior without naming the exact resource, API, pattern, file, or fix.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable workflow correctness, reliability, observability, and operational readiness improvements in simple English.",
   "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Terraform familiarity, Docker Compose comfort, serverless event-flow understanding, and local emulator awareness; do not include setup or verification steps.",
   "short_overview": "A bullet list summarizing the business problem, the serverless technical focus, the expected operational outcome, and the type of reasoning the task evaluates."
}}

## CRITICAL REMINDERS
1. `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
2. Do not generate kill.sh
3. Do not include README sections other than Task Overview, Objectives, Helpful Tips, and How to Verify
4. Do not include docker-compose version specifications
5. Do not use droplet IP placeholders anywhere
6. Bind every exposed local infrastructure port to localhost using `127.0.0.1:<port>:<port>`
7. Do not invent PostgreSQL, MySQL, MongoDB, Redis, or Elasticsearch services unless the selected scenario explicitly requires that datastore
8. Do not include candidate-facing solution hints in README, code comments, objectives, verification steps, or the question
9. The starter project must be deployable locally before the candidate begins
10. The task must remain within intermediate Serverless Architectures scope and require realistic changes across multiple interacting files
"""

PROMPT_REGISTRY = {
    "Serverless Architectures (INTERMEDIATE)": [
        PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_CONTEXT,
        PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_SERVERLESS_ARCHITECTURES_INTERMEDIATE_INSTRUCTIONS,
    ]
}