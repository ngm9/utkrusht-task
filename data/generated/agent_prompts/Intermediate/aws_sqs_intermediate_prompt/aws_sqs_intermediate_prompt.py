# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_AWS_SQS_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
particularly in relation to designing, operating, and troubleshooting AWS SQS based messaging workflows?
"""

PROMPT_AWS_SQS_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an AWS SQS assessment task.

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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, SQS messaging context, and operational problem the candidate will be solving)
2. What will the task look like? (Describe the type of SQS configuration, producer/consumer, retry, DLQ, idempotency, observability, or infrastructure-as-code improvement required, the expected deliverables, and how it aligns with the intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_AWS_SQS_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in AWS SQS, event-driven architecture, and infrastructure-as-code workflows, you are given a list of real world scenarios and proficiency levels for AWS SQS.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL local SQS-style messaging environment using LocalStack, Terraform, Docker, and a small producer/consumer worker scaffold, but with realistic logical bugs, misconfigurations, or operational weaknesses that require intermediate-level SQS problem-solving skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL and FULLY POPULATED local SQS simulation environment that is already deployed with existing queues, messages, queue configuration, and worker code. The environment includes:
- A LocalStack-backed SQS service that represents the production queue topology from the selected scenario
- Terraform or CloudFormation-style infrastructure definitions with intentionally suboptimal queue settings
- A small worker or producer/consumer scaffold that already sends, receives, processes, and deletes messages but contains intermediate-level SQS reliability issues
- Seed scripts or fixtures that create realistic messages, attributes, correlation IDs, and failure cases
- Operational evidence such as logs, sample metrics, README symptoms, or verification scripts showing backlog growth, duplicate processing, DLQ behavior, empty receives, or visibility timeout problems

The candidate's responsibility is to analyze the existing queue workflow, improve the SQS configuration and worker behavior, and preserve the business workflow. A part of the task completion is to watch the candidate apply practical AWS SQS mental models around at-least-once delivery, visibility timeout, long polling, batching, DLQs, idempotency, retries, observability, and cost/performance tradeoffs at an intermediate level (3-5 years experience).

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level SQS reliability or operations scenario
- Task must provide a working local SQS environment with existing infrastructure, queue definitions, seed data, and producer/consumer code requiring intermediate-level improvement
- **CRITICAL**: The LocalStack SQS environment should be FULLY functional but behaving poorly due to realistic SQS issues that require practical analysis and remediation
- **CRITICAL**: The exact problem described in the task scenario MUST be replicated in the generated files. For example, if the scenario mentions duplicate downstream side effects during slow processing, the worker code and queue settings MUST make that failure mode possible. If the scenario mentions excessive empty receives, the poller MUST use short polling or inefficient receive behavior. The candidate should ONLY need to improve/fix existing infrastructure and code, NOT build the whole system from scratch.
- **CRITICAL**: Keep the task at intermediate proficiency. The candidate should reason through queue configuration, worker behavior, retry boundaries, idempotency, and observability within a focused work item that can be completed within {minutes_range} minutes. Do not require expert-only topics such as complex multi-region disaster recovery, advanced cross-account security design, custom KMS key policy deep dives, or large migration planning.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the selected real-world scenario.
- Generate a complete, working LocalStack SQS environment with intentionally imperfect queue settings and worker behavior suitable for intermediate-level engineers (3-5 years experience).
- **PROVIDE PROBLEMATIC SQS DESIGN AND WORKER BEHAVIOR**: Include infrastructure and code issues such as:
  - Visibility timeout values that do not match observed processing time
  - Missing or poorly tuned DLQ redrive policy and maxReceiveCount
  - Short polling or single-message receive loops that increase cost and latency
  - Missing batch receive or batch delete behavior where batching would be appropriate
  - Message deletion before successful business completion, or missing delete after success
  - Consumer logic that is not idempotent under at-least-once delivery
  - Weak handling of transient vs non-retriable failures
  - Poor FIFO message group or deduplication strategy if the selected scenario genuinely requires FIFO ordering
  - Incomplete message attributes, correlation IDs, or schema metadata needed for operational tracing
  - Missing operational scripts or runbook notes for inspecting queue depth and DLQ messages
- The question should be a real-world business scenario requiring intermediate-level SQS troubleshooting and improvement involving queue configuration, producer/consumer lifecycle, error handling, DLQs, and observability, NOT building from scratch.
- The complexity of the task and specific improvements expected from the candidate must align with intermediate proficiency level requiring practical SQS techniques including:
  - Choosing or validating Standard vs FIFO queue behavior based on business ordering and throughput requirements
  - Configuring retention, visibility timeout, delivery delay, long polling, and DLQ redrive settings
  - Implementing long polling and receive batching to reduce empty receives and improve throughput
  - Handling per-message success and failure in batches without losing successful work
  - Deleting messages only after successful processing using the correct receipt-handle concept
  - Designing idempotent consumer behavior using business keys, correlation IDs, or durable deduplication records
  - Differentiating retriable, non-retriable, and poison-message failures
  - Applying retry and backoff behavior that respects visibility timeout and DLQ routing
  - Using message attributes for schema versioning, routing hints, tracing, and ownership
  - Adding useful logs and local operational checks that mirror CloudWatch queue-health investigation
  - Reasoning about cost and latency tradeoffs from polling frequency, batch size, and worker concurrency
  - Documenting queue purpose, SLA expectations, DLQ ownership, and safe reprocessing considerations
- The question must NOT include hints about the specific fixes needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to AWS SQS best practices for intermediate-level work while using LocalStack only as the local simulator.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, AWS SQS documentation, Terraform documentation, Docker documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and improve realistic SQS workflows at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the task should require genuine intermediate-level messaging, reliability, infrastructure, and operational reasoning that goes beyond simple copy-pasting from a generative AI
- Candidates will be encouraged to use AI to help with boilerplate, documentation lookup, and implementation mechanics, but not replace their own thinking about delivery semantics, failure handling, idempotency, and tradeoffs

## Infrastructure-as-Code Generation Instructions:
Based on the real-world scenarios provided above, create an AWS SQS task that:
- Draws inspiration from the input_scenarios given below to determine the business context, queue workflow, failure symptoms, and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for applied SQS reasoning
- Tests practical intermediate-level SQS configuration, worker lifecycle, DLQ, idempotency, retry, and observability skills
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- **CRITICAL**: The environment should be COMPLETE and FULLY FUNCTIONAL with LocalStack SQS, Terraform queue provisioning, realistic seed messages, and worker code, but with intentionally suboptimal queue settings and message-processing behavior
- **CRITICAL**: The task focuses on improving an existing incident-prone SQS workflow, NOT building a new queue system from scratch
- Prefer one focused scenario such as a healthcare reminder queue, logistics dispatch queue, order fulfillment queue, fraud-review queue, billing retry queue, notification fan-out queue, or batch processing work queue when it is present in the provided real-world scenarios
- The generated scaffold should include enough logs, seed data, and scripts for candidates to observe symptoms without requiring real AWS credentials
- Use LocalStack for local SQS behavior and Terraform for queue provisioning so the candidate can practice infrastructure-as-code changes safely
- If the scenario uses FIFO, ensure queue names, message group IDs, and deduplication behavior are represented consistently. If the scenario does not require strict ordering, prefer Standard queues and focus on idempotency and at-least-once processing.
- Include only the AWS SQS concepts naturally required by the selected scenario and the competency scope. Do not require SNS, Lambda, Step Functions, KMS, or cross-account IAM unless the selected scenario explicitly needs a small intermediate-level touchpoint.

## Infrastructure Requirements:
- MUST include a complete local SQS deployment using Docker Compose and LocalStack
- MUST include Terraform or equivalent IaC files that provision the queue, DLQ, redrive policy, and queue attributes used by the task
- MUST include a run.sh which has the end-to-end responsibility of deploying the local SQS infrastructure, waiting for readiness, applying IaC, seeding messages, and validating the starter scaffold loads
- MUST include a docker-compose.yml file containing LocalStack for SQS and, if the task includes a worker container, the worker service
- MUST include a Dockerfile when an app or worker container is generated
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy LocalStack or run bootstrap commands before beginning work
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- Do NOT include kill.sh. E2B sandboxes are destroyed as a whole when the session ends, so container cleanup is automatic.

### Docker-compose Instructions:
  - Include a LocalStack service configured for SQS with inline service environment values such as AWS region and enabled services
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every exposed service, including LocalStack on `127.0.0.1:4566:4566` and any worker/API diagnostic port if present
  - If a worker service is included, it should depend on LocalStack and use hardcoded local endpoint configuration suitable for the sandbox
  - Use named volumes or task-local data directories only when needed for LocalStack persistence
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - Do NOT use .env files or host environment interpolation. Inline service environment values are allowed when needed for the container to start.
  - Configure LocalStack and the worker so the starter stack boots reliably on the first `docker compose up`
  - The compose file should support local service communication through Docker networking while also exposing LocalStack to the candidate on localhost for inspection
  - **CRITICAL**: Docker Compose handles container orchestration while Terraform and seed scripts create the SQS resources and messages

### LocalStack SQS Configuration Instructions:
- Use LocalStack as the local AWS SQS simulator; do not require real AWS credentials or real AWS account access
- Terraform files should define the main queue, the DLQ, redrive policy, and queue attributes relevant to the scenario
- The generated IaC should intentionally contain intermediate-level SQS misconfiguration aligned with the scenario, but it must still apply successfully
- Include realistic queue names, tags, message retention choices, visibility timeout, long polling wait time, delivery delay if relevant, and FIFO attributes only when appropriate
- If IAM or queue policies are included, keep them local and conceptual enough for LocalStack while still testing least-privilege reasoning at an intermediate level
- Include seed data or a seed script that populates messages with business IDs, schema versions, correlation IDs, and realistic message attributes
- Do NOT include comments in Terraform or seed files that reveal the solution or directly identify which attributes to change
- Include operational artifacts such as sample logs, metric snapshots, or scripts that help candidates observe backlog, redelivery, and DLQ symptoms without prescribing the fix

### Run.sh Instructions:
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d` from `/root/task`
  - DEPENDENCY STEP: The first step must install or download task-owned dependencies that are not preinstalled, such as Terraform provider plugins via `terraform init`, package dependencies inside Docker builds, or any local script dependencies declared by the project
  - WAIT MECHANISM: Implements a proper readiness loop to wait for LocalStack to be healthy and accepting SQS requests
  - INFRASTRUCTURE SETUP: Applies the Terraform configuration against LocalStack so the queue and DLQ exist before validation
  - DATA INITIALIZATION: Seeds representative SQS messages only after the queues are created
  - VALIDATION: Verifies that LocalStack SQS responds, expected queues exist, and the starter worker or scripts can load without running the final grader or forcing the candidate solution
  - READINESS ONLY: run.sh is a readiness and self-check script, NOT the grader. It MUST NOT run a failing test suite that is designed to fail until the candidate solves the task.
  - MONITORING: Prints useful status messages showing container health, queue URLs, and seed completion without revealing solution steps
  - ERROR HANDLING: Includes proper error handling for failed container starts, failed Terraform apply, failed queue creation, or failed seed operations
  - LOCATION: All files are located in /root/task directory, ensure Docker paths reference this location
  - SIMPLIFIED APPROACH: Do not require real AWS credentials. Use local dummy credentials and LocalStack endpoints only.

### Dockerfile Instructions:
  - MUST generate a complete, valid Dockerfile if the task includes a worker, producer, API, or diagnostic application container
  - Should use an appropriate lightweight base image for the chosen worker runtime
  - Should install dependencies from the runtime's native manifest or requirements file
  - Should set the working directory to /root/task
  - Should include a proper entry point or command for the worker or diagnostic command
  - Must be production-like enough for the exercise while remaining simple and focused on SQS behavior
  - **DO NOT use .env files or host environment interpolation**
  - **CRITICAL**: Set WORKDIR to /root/task to match the file location

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (LocalStack SQS service configuration and worker service if generated)
  - Dockerfile (Required when a worker, producer, API, or diagnostic app container is generated)
  - run.sh (Script to deploy LocalStack, apply IaC, seed messages, and validate readiness)
  - .gitignore (Ignore Terraform, Docker, logs, local data, and runtime artifacts)
  - infra/main.tf (Terraform queue and DLQ resources with intentional intermediate-level SQS issues)
  - infra/variables.tf (Terraform variables only if needed for names, region, and local endpoint configuration)
  - infra/outputs.tf (Terraform outputs for queue URLs, ARNs, or names needed by scripts)
  - scripts/seed_messages.sh or scripts/seed_messages.py (Seed realistic SQS messages into the local queue)
  - scripts/inspect_queues.sh (Helper script for observing local queue and DLQ state without revealing fixes)
  - worker files for the selected runtime (Complete producer or consumer scaffold with realistic but suboptimal SQS behavior)
  - sample_logs/ or docs/incident_snapshot.md (Small operational evidence file showing symptoms such as backlog, duplicate processing, empty receives, or DLQ growth)

## Code file requirements:
- More than 1 file can be generated but make sure each file is included in the JSON structure correctly
- Infrastructure and code should be valid, executable, and immediately usable in /root/task
- **CRITICAL**: The LocalStack SQS environment, Terraform definitions, seed scripts, and worker scaffold MUST be complete and functional, but intentionally incident-prone according to the scenario
- **CRITICAL**: The exact problems described in the task scenario MUST be present in the generated files. Do not implement optimized solutions in the starter files.
- Worker code should focus on SQS message lifecycle and business processing behavior, not unrelated framework complexity
- Include producer or consumer code only as much as needed to exercise SQS concepts; avoid large application frameworks unless the selected scenario clearly requires them
- Include realistic message bodies and attributes, but avoid unnecessary PII and secrets in message payloads
- Use dummy local AWS credentials and LocalStack endpoints; do not require candidates to access real AWS
- DO NOT include any TODO comments or placeholder comments in worker code
- DO NOT include any comments that give away optimization solutions
- DO NOT include comments that hint at the direct or indirect solution in the files
- The worker should be immediately runnable but should exhibit the SQS problems candidates must diagnose and improve
- Include small operational scripts that inspect queue depth, DLQ count, approximate age indicators, or redelivery behavior where useful, without prescribing the exact fix
- If tests are included, they must be candidate-run verification aids and run.sh must not treat failing solution tests as a deployability failure
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for AWS SQS, Terraform, Docker, and worker development tasks that includes:
- Terraform local state and provider directories
- Terraform plan files and crash logs
- LocalStack data directories
- Docker and local runtime artifacts
- Log files and sample generated outputs
- Python, Node.js, or shell test cache files if that runtime is used
- Environment files such as .env and local credential files
- IDE and editor files
- OS-specific files such as .DS_Store and Thumbs.db
- Any other standard exclusions for local cloud-infrastructure development

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to intermediate-level AWS SQS reliability, operations, and infrastructure-as-code work.
Task Overview section MUST contain the exact business scenario and specific queue workflow symptoms that need intermediate-level improvement.
ALL sections must have substantial content - no empty or placeholder text allowed.
Content must be directly relevant to the specific SQS scenario being generated.
Use concrete business context explaining queue backlog, duplicate processing, DLQ, polling, visibility timeout, idempotency, ordering, or operational issues, not generic descriptions.
Do NOT include database-connection details, droplet placeholders, real AWS credentials, or remote-host placeholders. When local service access is legitimately mentioned, use localhost.

### Task Overview
- Task Overview must be 3-4 meaningful sentences. No bullet list.
- It describes the business scenario, current state, and why the problem matters.
- It must clearly state that the existing SQS-based workflow is already present but is failing operationally in ways the candidate must investigate.
- NEVER empty. NO bold time-budget callouts.

### Objectives
- Objectives must be 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix. A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like. It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the "what" and "why", never the "how".
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Improve polling."
- GOOD: "The worker generates excessive empty receives during normal traffic; after your changes the queue should be polled efficiently while still keeping message latency within the expected operational window."
- Objectives should focus on intermediate-level SQS outcomes such as safer message lifecycle handling, reduced duplicate business side effects, healthier backlog behavior, appropriate DLQ routing, clearer observability, and maintainable IaC.

### Helpful Tips
- Helpful Tips must be 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, Terraform attribute, or exact SQS setting that solves the task.
- Keep tips focused on SQS reasoning, failure modes, local queue inspection, business idempotency, and operational tradeoffs.
- If local access information is needed, include it briefly within a tip, using localhost only, such as mentioning that LocalStack is reachable from the sandbox at localhost:4566.

### How to Verify
- How to Verify must be 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as worker output, queue depth, DLQ movement, duplicate side-effect records, message age, retry behavior, log correlation, or reduced empty receive behavior.
- Verification bullets may mention task-provided scripts or local commands if those scripts exist, but they must not become step-by-step implementation instructions.
- Use localhost for LocalStack endpoint references when endpoint references are necessary.
- Do not include setup commands such as docker compose up, terraform init, package installation, or run.sh execution.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README:
- Setup commands such as package installation, docker compose up, terraform init, terraform apply, run.sh execution, or any manual deployment instructions
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, Terraform attribute names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Exact SQS setting values that solve the task unless they are already part of the broken incident evidence
- Real AWS credentials, real AWS account instructions, droplet IP placeholders, or remote-host connection details
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this API", or "set this exact attribute"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "A kebab-case GitHub repository name under 50 characters that summarizes the SQS task without spaces or punctuation beyond hyphens.",
   "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name and focused on the SQS workflow the candidate will improve.",
   "question": "A concise candidate-facing description of the intermediate-level AWS SQS task scenario, including the business workflow, the observable queue symptoms, and the reliability or operational outcomes expected without revealing the exact implementation fixes.",
   "code_files": {{
      "README.md": "Candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify sections with concise open-ended guidance for the SQS task.",
      ".gitignore": "A comprehensive ignore file for Terraform, Docker, LocalStack, logs, runtime caches, local credentials, editor files, and operating-system artifacts.",
      "docker-compose.yml": "Docker Compose configuration without a version field that starts LocalStack for SQS and any worker service, with all exposed ports bound to localhost only.",
      "Dockerfile": "A complete Dockerfile for the worker or diagnostic application container when generated, using /root/task as the working directory and installing declared dependencies.",
      "run.sh": "A readiness script that installs or downloads task-owned dependencies, starts Docker Compose, waits for LocalStack SQS, applies IaC, seeds messages, validates the starter scaffold, and does not run the final grader.",
      "infra/main.tf": "Terraform configuration that provisions the local SQS queue, DLQ, and related attributes through LocalStack while intentionally preserving the scenario's intermediate-level misconfiguration.",
      "infra/variables.tf": "Terraform variable declarations for local endpoint, region, queue names, or tags when needed by the generated task.",
      "infra/outputs.tf": "Terraform outputs exposing queue URLs, ARNs, or names required by local scripts without exposing real AWS account details.",
      "scripts/seed_messages.sh": "A script that inserts realistic scenario messages with business IDs, correlation metadata, and attributes into the LocalStack SQS queue after Terraform provisioning.",
      "scripts/inspect_queues.sh": "A helper script that shows observable local queue and DLQ state so candidates can investigate behavior without being told the fix.",
      "worker/worker_file": "Complete worker or consumer source files for the selected runtime containing realistic SQS lifecycle behavior with intentional reliability or efficiency issues aligned to the scenario.",
      "worker/dependency_manifest": "Runtime-native dependency manifest for the worker when a worker runtime is used, declaring only dependencies needed for SQS client access, local processing, and lightweight diagnostics.",
      "sample_logs/incident_snapshot.md": "A concise operational evidence file with sample logs or metric-style observations that match the business symptoms described in the task."
   }},
   "answer": "Evaluator-facing high-level solution approach describing the expected SQS configuration, worker lifecycle, idempotency, retry, DLQ, batching, and observability improvements appropriate for the generated scenario.",
   "definitions": "An object of term-to-definition pairs explaining SQS and local-simulation terminology used in the task, such as visibility timeout, DLQ, redrive policy, long polling, receipt handle, idempotency, and LocalStack.",
   "hints": "A single line hint nudging the candidate toward investigating queue behavior, message lifecycle, and operational symptoms without naming the exact fixes or settings.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable queue-health improvements, safer message processing, reduced duplicate side effects, and clearer operational behavior in simple English.",
   "pre_requisites": "A bullet list of assumed prior knowledge and skills only, such as Terraform familiarity, Docker-based local cloud simulation comfort, AWS SQS lifecycle understanding, and basic worker-code reading ability; do not include setup or verification steps.",
   "short_overview": "A bullet list summarising the business problem, the SQS technical focus, and the expected operational outcome after the candidate improves the workflow."
}}

## CRITICAL REMINDERS:
1. `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display.
2. **NO REAL AWS ACCOUNT REQUIRED**: Use LocalStack for SQS simulation and dummy local credentials only.
3. **NO kill.sh**: Do not generate cleanup scripts because E2B destroys the sandbox as a whole.
4. **INTERMEDIATE LEVEL**: Ensure complexity matches 3-5 years of AWS SQS experience and can be completed within {minutes_range} minutes.
5. **SCENARIO ACCURACY**: The broken behavior described in the question and README must exist in the generated Terraform, seed data, worker code, logs, or scripts.
6. **NO SOLUTIONS IN STARTER FILES**: Do not include corrected queue attributes, optimized polling loops, exact solution comments, or direct implementation hints in the generated starter files.
7. **LOCALHOST ONLY**: Any exposed Docker port must be bound to 127.0.0.1, and any legitimate endpoint reference must use localhost rather than a droplet IP or remote placeholder.
8. **RUN.SH IS READINESS ONLY**: It must deploy and validate the scaffold but must not run a failing grader or require the candidate's final solution.
9. **SQS SCOPE ONLY**: Keep the task centered on SQS configuration, message lifecycle, DLQs, retries, batching, idempotency, observability, and operational tradeoffs; avoid unrelated cloud services unless the selected scenario genuinely requires a small supporting mention.
"""

PROMPT_REGISTRY = {
    "AWS - SQS (INTERMEDIATE)": [
        PROMPT_AWS_SQS_INTERMEDIATE_CONTEXT,
        PROMPT_AWS_SQS_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_AWS_SQS_INTERMEDIATE_INSTRUCTIONS,
    ]
}