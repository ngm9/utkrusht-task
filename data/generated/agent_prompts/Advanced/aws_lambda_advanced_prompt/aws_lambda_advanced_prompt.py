# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_AWS_LAMBDA_ADVANCED_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, particularly in relation to architecting, hardening, and operating production-grade AWS Lambda event-driven workflows?
"""

PROMPT_AWS_LAMBDA_ADVANCED_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an AWS Lambda assessment task.

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
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies (advanced: 6-10 years)
- Ensure the candidate can realistically complete the task in the allocated time
- Select a different real-world scenario each time to ensure variety in task generation
- The task must reflect authentic production-grade AWS Lambda reliability challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, event-driven workflow, and Lambda reliability/operability problem the candidate will be solving)
2. What will the task look like? (Describe the type of Lambda hardening, event-source-mapping fix, idempotency/DLQ remediation, or timing-coherence correction required, the expected deliverables, and how it aligns with the advanced proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_AWS_LAMBDA_ADVANCED_INSTRUCTIONS = """
## GOAL
As a staff-level engineer super experienced in AWS Lambda, event-driven architecture, and production serverless reliability, you are given a list of real world scenarios and proficiency levels for AWS Lambda.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL local Lambda-based event-driven workflow (deployed via Terraform against LocalStack) that behaves correctly on the happy path but has realistic, production-shaped reliability defects that require advanced-level AWS Lambda skills to diagnose and fix.
The candidate's responsibility is to analyze the existing workflow, identify the defects from observed behavior, and harden the system without being told the exact solution. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL local serverless project deployable through Docker Compose + LocalStack (image `localstack/localstack:3.5` or newer) and Terraform. The project includes:
- Terraform infrastructure (`infra/`) targeting the LocalStack endpoint (`http://localhost:4566`) that provisions an SQS queue (and an already-created but not fully wired dead-letter queue), a batch-consuming Lambda function (Python 3.11) via an event source mapping, and downstream state stores (S3 and/or DynamoDB) used to record the workflow's business outcome
- Complete, runnable handler code under `functions/` that processes SQS batch records and produces a business side effect (a settlement, a shipment, a notification, or similar) against the downstream store(s)
- A docker-compose.yml that starts LocalStack with the `SERVICES` needed for the scenario (at minimum `lambda`, `sqs`, plus `s3` and/or `dynamodb` as the scenario requires), the Docker socket mounted so LocalStack can run the Lambda runtime container, and a healthcheck
- A run.sh readiness script that packages the function code, starts Docker Compose, waits for the LocalStack health endpoint and the required services, runs `terraform init`/`apply` against the local scaffold, and performs a lightweight smoke check (queue exists, bucket/table exists, function exists) — it must NOT run the grading tests and must NOT apply the candidate's solution
- Sample event fixtures under `fixtures/` (including at least one fixture that is well-formed but exercises redelivery, and one fixture that is deterministically malformed) and helper scripts under `scripts/` to send/replay events and inspect state
- tests/ scripts that are RED against the unsolved starter and GREEN only after a correct advanced-level fix, verifying behavior end-to-end against the running local stack rather than by static inspection

The candidate's responsibility is to investigate delivery and failure behavior empirically (by sending and replaying events against the running stack), diagnose the specific reliability defect(s) from symptoms, and harden the Lambda-based workflow. A part of the task completion is to watch the candidate reason at an advanced level about at-least-once delivery, idempotency, partial-batch failure handling, dead-letter routing, and the coherence between SQS visibility timeout and Lambda function timeout.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the advanced-level AWS Lambda reliability-hardening scenario
- Task must provide a working local Lambda project with existing Terraform infrastructure, sample events, scripts, and realistic handler code; it must NOT be a blank design exercise or a pure essay
- **CRITICAL**: The generated project should be FULLY FUNCTIONAL and deployable locally (`terraform apply` succeeds, the starter smoke check passes), but it should exhibit realistic symptoms — duplicate side effects on redelivery, one bad message stalling or duplicating a whole batch, a poison message looping forever with no dead-letter routing, or delivery timing misaligned with function execution time — that require the candidate to inspect event-source-mapping configuration, handler logic, and queue/DLQ configuration before deciding what to change
- **CRITICAL**: The candidate-facing question and README must describe observable symptoms and desired outcomes, not the exact mechanism (do not name `ReportBatchItemFailures`, specific IAM actions, or exact Terraform attributes) needed to solve them
- **CRITICAL**: Do not hard-code the selected scenario's solution into the README, file comments, hints, objectives, or verification steps. The handler and Terraform may contain the flawed implementation, but comments must not label the flaw or point to the fix
- The task must select and combine AT LEAST TWO of the following advanced reliability defect categories in the starter, chosen to fit the selected scenario, so the task has genuine advanced depth (not a single-line fix):
  1. Missing or incorrect idempotency — repeated delivery of the same logical unit of work (a payment, refund, order, notification, etc.) produces a duplicate business side effect (a second object write, a second ledger/table row, a second downstream call) instead of exactly one
  2. Missing partial-batch failure handling — one malformed or failing record in a batch causes the whole batch to be treated as failed (and thus fully redelivered, duplicating already-successful work) or causes the entire invocation to raise instead of isolating just the bad record
  3. Missing or misconfigured dead-letter routing — a dead-letter queue or destination exists in the infrastructure but is not actually wired to the event source (no redrive policy, or a redrive policy with an unreasonable/absent maxReceiveCount), so a deterministically-failing message is retried forever instead of becoming inspectable
  4. Incoherent delivery timing — the queue's visibility timeout is shorter than (or too close to) the function's timeout, so an in-flight invocation can be concurrently redelivered to a second invocation while still processing
  5. Missing or unusable operational traceability — logs are unstructured or omit stable identifiers (a business id, correlation id, or message id), making it impractical to trace one unit of work through a failure
- The task should be based on ONE selected real-world scenario and should closely match its domain, workflow, symptoms, and constraints
- The generated task must stay within advanced AWS Lambda scope: event source mapping semantics and tuning, SQS/DynamoDB Streams/Kinesis/EventBridge-driven Lambda, idempotency and dedupe design, partial batch failure reporting, DLQ/redrive design, concurrency and timeout/visibility-timeout coherence, IAM least-privilege for the function's actual downstream calls, structured logging and traceability, and Terraform-based deployment against LocalStack
- Avoid requiring expert-only topics unrelated to Lambda reliability such as multi-region active-active architecture, custom Lambda runtime/bootstrap engineering, or provider-internal implementation trivia
- The question should be a real-world business scenario requiring advanced-level analysis and implementation across more than one file
- The starter codebase MUST be substantial and realistic, NOT a toy snippet. Require MULTIPLE interacting modules/files in a real project layout, with non-trivial existing logic the candidate must read and reason about before changing
- Changes should normally span more than one file (Terraform infra, handler code, and possibly a small client/helper module)
- Time constraints: Each task should be finished within {minutes_range} minutes
- Ensure that the work can be completed by an advanced candidate in the allotted time by keeping the workflow focused and bounded (one primary Lambda function and at most one or two downstream stores)
- The candidate should not need a real AWS account; all deployability should be local through Docker Compose, LocalStack, and Terraform
- The question must NOT include hints about the specific fixes needed. The hints will be provided only in the "hints" field and must still avoid revealing the solution
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, AWS Lambda/SQS documentation, Terraform documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively diagnose and remediate realistic production-grade Lambda reliability issues at an advanced level, rather than testing rote memorization
- Therefore, the complexity of the tasks should require genuine advanced-level serverless reliability judgment, event-driven reasoning, and operational problem-solving skills that go beyond simple copy-pasting from a generative AI
- Candidates will be encouraged to use AI to help with boilerplate, documentation lookup, and troubleshooting, but not replace their own diagnostic reasoning

## Code Generation Instructions
Based on the real-world scenarios provided above, create an AWS Lambda task that:
- Draws inspiration from the input_scenarios given below to determine the business context, event flow, downstream stores, operational symptoms, and constraints
- Matches the complexity level appropriate for advanced proficiency level (6-10 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for reliability-engineering reasoning
- Tests practical advanced-level Lambda implementation, review, debugging, and reliability-hardening skills
- Uses Terraform as the infrastructure-as-code tool, targeting the LocalStack endpoint with the standard local test-credentials provider block (access_key/secret_key `"test"`, `s3_use_path_style = true`, `skip_credentials_validation`, `skip_metadata_api_check`, `skip_requesting_account_id`, and an `endpoints` block covering every emulated service used)
- Packages the Lambda function as a zip built by a `scripts/package_functions.sh`-style script and referenced from Terraform via `filename` / `source_code_hash`
- Uses Python 3.11 as the Lambda runtime for handler code
- Uses LocalStack as the local cloud emulator, exposing only the local edge endpoint (4566) needed for the task, with the Docker socket mounted so Lambda invocations actually run
- Includes realistic event fixtures and helper scripts that reproduce the observable symptoms of the selected scenario (at least one "replay the same valid event" flow and, when a partial-batch or poison-message defect category is selected, one deterministically-malformed fixture)
- Includes tests/ or checks/ scripts that exercise the running local stack end-to-end (send/replay events, wait, then assert on actual downstream state such as object counts or table rows) to verify the specific defect categories selected — these must fail against the unsolved starter and pass only after a correct fix, but run.sh must NOT execute them
- The starter must be deployable, readable, and realistic, with multiple interacting files such as:
  - docker-compose.yml for LocalStack
  - run.sh for automated local readiness (package → up → wait → terraform init/apply → smoke check)
  - infra/main.tf, infra/variables.tf, infra/outputs.tf for the Terraform scaffold
  - functions/ handler code (and a small client/helper module when the scenario benefits from one)
  - scripts/ for packaging, sending, and replaying events, and inspecting downstream state
  - fixtures/ event payloads
  - tests/ verification scripts
  - README.md and .gitignore
- **CRITICAL**: The scenario description must be reflected in the actual files. If the question describes duplicate side effects, a batch that stalls on one bad record, a poison message that loops forever, or timing-related redelivery, the generated scaffold must contain the corresponding flawed behavior or configuration without comments that reveal the fix
- **CRITICAL**: The task focuses on hardening an existing Lambda-based workflow, NOT building serverless infrastructure from scratch
- **CRITICAL**: Keep exact solution choices out of candidate-facing instructions. Explain symptoms, constraints, and desired outcomes; allow multiple valid advanced-level approaches

## Infrastructure Requirements
- MUST include docker-compose.yml for LocalStack, with the Docker socket mounted (`/var/run/docker.sock:/var/run/docker.sock`) and `SERVICES` covering at least `lambda,sqs` plus whatever downstream services (`s3`, `dynamodb`) the scenario needs
- MUST include run.sh using the package → `docker compose up -d` → wait-for-health → `terraform init`/`apply` → smoke-check sequence
- MUST NOT include kill.sh; E2B sandboxes are destroyed as a whole and do not need per-task cleanup scripts
- The infrastructure setup is AUTOMATED - candidates will receive a project that can be brought up by the readiness script and should not be asked to manually install or configure cloud services
- The generated project must not require a real AWS account, real cloud credentials, or remote endpoints
- Use hardcoded local development values where necessary for the emulator; do not use .env files or host-variable interpolation
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **CRITICAL**: run.sh is a readiness/self-check script, NOT the grader. It packages the function, brings infrastructure up, waits for health, applies the Terraform scaffold, performs a lightweight smoke check, then exits 0 on the UNSOLVED starter

### Docker-compose Instructions
  - Include exactly one `localstack/localstack:3.5`-or-newer service
  - **SECURITY-CRITICAL**: bind the edge port to localhost only, `127.0.0.1:4566:4566`
  - **MUST NOT include any version specification** in the docker-compose.yml file (no top-level `version:` key)
  - **MUST NOT include .env file references or host-variable interpolation syntax**
  - Set `SERVICES`, `AWS_DEFAULT_REGION`, and `DOCKER_HOST=unix:///var/run/docker.sock` inline as environment values
  - Mount `/var/run/docker.sock:/var/run/docker.sock` so LocalStack can run the Lambda runtime container
  - Include a healthcheck against `/_localstack/health` so run.sh can wait reliably
  - Include a named volume for LocalStack data only if useful

### Terraform / LocalStack Configuration Instructions
- Generate complete Terraform under `/root/task/infra` for the SQS queue, the (existing but under-wired) dead-letter queue, the Lambda function, its execution role/policy, the event source mapping, and any S3/DynamoDB resources the scenario needs
- Provider block must target LocalStack: `access_key`/`secret_key` = `"test"`, `s3_use_path_style = true`, `skip_credentials_validation = true`, `skip_metadata_api_check = true`, `skip_requesting_account_id = true`, and an `endpoints` block listing every emulated service used, all pointing at `var.localstack_endpoint` (default `http://localhost:4566`)
- Keep resource names, tags, and ownership metadata realistic and consistent with the selected business domain
- Do not include comments in Terraform or handler code that identify the defect category, name the exact missing setting, or explain the solution
- The generated starter should pass a readiness deployment (`terraform apply`) against the local emulator

### Run.sh Instructions
  - FIRST STEP: package the Lambda function code into the zip(s) Terraform expects
  - PRIMARY RESPONSIBILITY: Starts LocalStack using `docker compose up -d`
  - WAIT MECHANISM: Waits for the LocalStack health endpoint and for every required service to be reported healthy before proceeding
  - DEPLOYMENT VALIDATION: Runs `terraform init` then `terraform apply -auto-approve` against the local scaffold
  - STARTER SMOKE CHECK: Confirms the queue(s), function, and downstream store(s) exist via `awslocal` calls through `docker compose exec`
  - NO GRADER EXECUTION: run.sh MUST NOT run the tests/ verification scripts
  - ERROR HANDLING: Fails fast with a clear message if LocalStack never becomes healthy, Terraform fails, or the smoke check fails
  - MONITORING: Prints concise `[run]`-prefixed status messages for each stage
  - LOCATION: All files are located in /root/task directory
  - The script must exit 0 when the unsolved starter deploys and the smoke check passes

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - .gitignore (Ignore Terraform, local emulator, package, log, cache, and editor artifacts)
  - docker-compose.yml (LocalStack service configuration as specified above)
  - run.sh (Readiness script: package, up, wait, terraform init/apply, smoke check)
  - infra/main.tf (Complete Terraform resources for the selected scenario)
  - infra/variables.tf and infra/outputs.tf (Supporting Terraform files)
  - functions/handler_file.py (Complete runnable Lambda handler code, Python 3.11)
  - scripts/package_functions.sh and other scripts/ helpers for sending/replaying events and inspecting state
  - fixtures/*.json event payloads that reproduce the scenario symptoms
  - tests/check_*.sh verification scripts that assert on real running-stack behavior (RED on the unsolved starter, GREEN after a correct fix)

## Code file requirements
- More than one file MUST be generated, and the project must be substantial enough for an advanced candidate to inspect multiple interacting components
- All Terraform files must be syntactically valid HCL and target the local emulator by default
- All shell scripts must be valid Bash and use `/root/task` as the base directory
- Handler code must be complete and runnable; do not include placeholder TODOs or incomplete stubs
- Do not include comments that give away the solution, identify the exact missing configuration, or label the intended fix
- Do not include fake tests that pass without exercising the scenario against the real running stack
- Do not include real cloud credentials, remote account IDs, production endpoints, or any instruction requiring a candidate to deploy outside the sandbox
- Use realistic event payloads, identifiers, timestamps, and business metadata, but avoid personal data or secrets
- The exact defect categories described in the task scenario must be present in the generated handler and/or infrastructure
- The generated scaffold should be deployable locally before the candidate begins, even though the workflow behavior is intentionally flawed
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for local Terraform + LocalStack Lambda development that includes:
- Terraform working directories and state files such as .terraform/, *.tfstate, *.tfstate.backup, .terraform.lock.hcl, and crash logs
- Lambda build artifacts such as build/, *.zip, *.tar.gz
- Local emulator data directories such as localstack/, data/, and temporary volume folders
- Runtime caches such as __pycache__/, *.pyc, .pytest_cache/
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

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected advanced-level AWS Lambda scenario. ALL sections must have substantial content; no empty or placeholder text allowed.

### Task Overview
- Must be 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, current state, and why the reliability problem matters.
- It should explain observable symptoms and business impact without naming the exact solution.
- NEVER generate empty content.
- Do not include bold time-budget callouts.

### Objectives
- Include 3-5 bullets max; fewer, tighter is better.
- Objectives MUST be concise and OPEN-ENDED.
- Each objective states ONE desired outcome in a single short line, roughly 8-16 words.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, or config knob (no "ReportBatchItemFailures", no "redrive policy", no exact function/file names).
- Good objective style: "Ensure a refund settles exactly once no matter how many times its message is delivered."
- Bad objective style: "Add function_response_types = [\\"ReportBatchItemFailures\\"] to the event source mapping."

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Follow", "Look", "Compare", "Consider", or "Think about".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, resource, or config attribute that solves the task.
- Tips may refer to broad reliability ideas such as delivery semantics, batch reporting, timing coherence, and traceability.

### How to Verify
- Include 3-5 bullets max.
- Frame verification in terms of observable outcomes the candidate can produce by running the local stack.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Use localhost in any verification command that legitimately references the local emulator endpoint.
- Do not include cloud-account instructions, real cloud deployment steps, or droplet IP placeholders.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
- Setup commands such as `terraform apply`, `docker compose up`, package installation commands, or manual deployment instructions
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, Terraform resource/attribute names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database connection sections, cloud credential instructions, host/port credential tables, or `<DROPLET_IP>` placeholders
- Directive phrases like "you should implement", "add a redrive policy", "set ReportBatchItemFailures", or "raise the visibility timeout"

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "A kebab-case GitHub repository name under 50 characters that reflects the AWS Lambda reliability-hardening task without using spaces or title casing.",
   "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name and clearly describing the Lambda reliability work the candidate will perform.",
   "question": "A complete candidate-facing task description that explains the selected business scenario, the current Lambda workflow state, the observable symptoms, the expected deliverables, and the constraints without revealing the specific fix.",
   "code_files": {{
      "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify, written with open-ended guidance and no direct solution details.",
      ".gitignore": "A comprehensive Terraform, Docker, local emulator, editor, operating system, and log exclusion file that avoids committing local state or build artifacts.",
      "docker-compose.yml": "A Docker Compose configuration for LocalStack with the Docker socket mounted and the required SERVICES, with localhost-only port bindings and no version specification.",
      "run.sh": "A complete executable readiness script that packages the function, starts docker compose, waits for readiness, applies the Terraform project, and smoke-checks — without applying the candidate's solution or running tests.",
      "infra/main.tf": "The Terraform configuration containing the SQS queue, DLQ, Lambda function, execution role, event source mapping, and downstream store(s) that reproduce the scenario's reliability issue.",
      "infra/variables.tf": "Terraform input variables including the LocalStack endpoint and region.",
      "infra/outputs.tf": "Terraform outputs needed by scripts and candidates to discover local resource identifiers.",
      "functions/handler.py": "Complete, runnable Python 3.11 Lambda handler code containing the realistic reliability defect(s) the candidate must diagnose and fix.",
      "scripts/package_functions.sh": "A packaging script that zips the handler code for Terraform to deploy.",
      "scripts/<send_or_replay>.sh": "Helper scripts to send or replay events against the local queue.",
      "scripts/<inspect>.sh": "Helper scripts to inspect downstream state (object/table contents, DLQ depth).",
      "fixtures/<event>.json": "Realistic event payloads, including at least one valid event and, when relevant, one deterministically malformed event.",
      "tests/check_<behavior>.sh": "Verification scripts that exercise the running local stack end-to-end and assert on real downstream state; these fail on the unsolved starter and pass only after a correct advanced-level fix."
   }},
   "answer": "An evaluator-facing high-level solution approach describing the reliability engineering reasoning, the specific Terraform and handler changes, and the validation strategy expected from an advanced candidate.",
   "definitions": "An object mapping important Lambda, event-driven, delivery-semantics, and reliability terms used in the task to concise definitions that support consistent evaluation.",
   "hints": "A single line hint that nudges the candidate toward evidence-based investigation of delivery and failure behavior without revealing the specific resource, API, or configuration fix.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable reliability improvements such as exactly-once business outcomes, isolated batch failures, bounded dead-letter routing, and traceable logs. Use simple english.",
   "pre_requisites": "A bullet list of tools and knowledge needed for the task, including Terraform CLI familiarity, Docker Compose basics, AWS Lambda event-source-mapping concepts, SQS delivery semantics, and advanced-level reliability engineering judgment.",
   "short_overview": "Exactly 3 plain sentences where the first sentence states what Lambda reliability work is being assessed, the second sentence states what the candidate must do, and the third sentence states what successful completion looks like, with no label prefixes of any kind."
}}

## CRITICAL REMINDERS
1. **LAMBDA RELIABILITY FOCUS**: The task must center on hardening an existing, already-deployable Lambda-based event-driven workflow, not building one from scratch
2. **AT LEAST TWO DEFECT CATEGORIES**: Combine at least two of the five advanced reliability defect categories listed above, chosen to fit the selected scenario
3. **NO KILL.SH**: Do not include kill.sh because E2B sandboxes are destroyed as a whole and cleanup is automatic
4. **NO REAL CLOUD CREDENTIALS**: Use LocalStack test credentials only, with no real account IDs, secrets, or environment variable instructions
5. **ADVANCED LEVEL**: Ensure complexity matches 6-10 years of experience and can be completed in approximately {minutes_range} minutes
6. **BEHAVIORAL VERIFICATION**: tests/ scripts must assert on actual running-stack state (object counts, table rows, queue depth), not just static code inspection, and must be RED on the unsolved starter
7. **NO SOLUTIONS IN CODE**: Do not include fixed batch-failure reporting, correct redrive policies, or direct solution comments in the generated starter files
8. **README LIMITS**: README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no setup commands or direct implementation instructions
9. **TITLE REQUIRED**: `"title"` must be in `<action verb> <subject>` format and different from `"name"`
10. **SHORT OVERVIEW FORMAT**: `"short_overview"` must be exactly 3 plain sentences with no label prefixes
"""

PROMPT_REGISTRY = {
    "AWS Lambda (ADVANCED)": [
        PROMPT_AWS_LAMBDA_ADVANCED_CONTEXT,
        PROMPT_AWS_LAMBDA_ADVANCED_INPUT_AND_ASK,
        PROMPT_AWS_LAMBDA_ADVANCED_INSTRUCTIONS,
    ]
}
