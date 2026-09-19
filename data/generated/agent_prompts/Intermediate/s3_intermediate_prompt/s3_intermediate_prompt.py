# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_S3_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements, particularly in relation to designing, securing, operating, and troubleshooting Amazon S3-backed storage systems?
"""

PROMPT_S3_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Amazon S3 assessment task.

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
- The task must assess applied S3 design, security, lifecycle, data protection, troubleshooting, cost, or integration judgment rather than trivia or memorized command flags

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, S3 storage context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of S3 infrastructure, policy, lifecycle, object-layout, or operational fix required, the expected deliverables, and how it aligns with the intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_S3_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Amazon S3 storage architecture, security, lifecycle governance, and infrastructure automation, you are given a list of real world scenarios and proficiency levels for S3.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL local S3-compatible infrastructure project with existing Terraform, policies, scripts, and validation artifacts but with realistic S3 design, security, lifecycle, access, or operational issues that require intermediate-level S3 skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION:
The candidate will receive a FULLY FUNCTIONAL infrastructure-as-code project that provisions and exercises an S3-compatible environment using LocalStack. The project includes:
- Existing Terraform configuration for S3 buckets, bucket policies, encryption settings, versioning, lifecycle rules, object tags, event notifications, or replication-style design artifacts as appropriate for the selected scenario
- Docker Compose infrastructure for a local S3-compatible endpoint
- Shell scripts that deploy the local infrastructure and perform readiness checks
- Realistic starter objects, policies, metadata examples, key naming examples, or operational reports that reflect an authentic production S3 problem
- Intentionally incomplete, insecure, inefficient, or operationally risky S3 design choices that demand intermediate-level problem-solving

The candidate's responsibility is to analyze the existing S3 infrastructure, diagnose the scenario-specific issue, and modify the Terraform, policy JSON, scripts, or lightweight support files to produce a secure, cost-aware, operationally sound S3 design. The task should evaluate practical S3 judgment at an intermediate level (3-5 years experience), not memorization of provider syntax.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level S3 infrastructure scenario
- Task must provide a working local S3 infrastructure project with existing Terraform and intentionally flawed S3 configuration requiring intermediate-level S3 design, security, lifecycle, or troubleshooting skills
- **CRITICAL**: The S3-compatible environment should be FULLY FUNCTIONAL but configured with realistic flaws such as overly broad access, missing Block Public Access controls, poor object key layout, absent lifecycle tagging, weak encryption defaults, incorrect version cleanup, unsafe public access patterns, missing CORS constraints, or inefficient analytics partitioning
- **CRITICAL**: The exact problem described in the task scenario MUST be replicated in the generated files. If the scenario mentions that lifecycle transitions do not apply to closed objects, the Terraform and seed objects must reflect that. If the scenario mentions that browser downloads fail with 403, the policy, CORS, and URL artifacts must reflect that. If the scenario mentions analytics scans too much data, the object layout and catalog artifact must reflect that.
- **CRITICAL**: The candidate should ONLY need to improve or fix the existing S3 infrastructure and related support files, NOT build an entire storage platform from scratch
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, object names, prefixes, policy examples, and operational symptoms are internally consistent and relevant to the context
- Generate a complete, working infrastructure project suitable for intermediate-level cloud engineers (3-5 years experience)
- **PROVIDE PROBLEMATIC S3 INFRASTRUCTURE DESIGN**: Include Terraform or equivalent IaC with scenario-specific S3 flaws such as:
  - Bucket policies that are too broad or fail least-privilege expectations
  - Missing or incomplete S3 Block Public Access and Object Ownership controls
  - Incomplete default encryption or KMS-related policy assumptions where appropriate
  - Versioning enabled without safe noncurrent-version lifecycle cleanup
  - Lifecycle rules that do not target the intended prefixes or object tags
  - Object key naming that prevents efficient listing, analytics partitioning, or lifecycle targeting
  - Missing object tags or metadata required for retention, chargeback, lifecycle, or governance
  - CORS rules that are too permissive or fail a realistic browser upload/download flow
  - Pre-signed URL or direct-access flow artifacts that expose more access than intended
  - Event notification or integration configuration that does not match the object prefix/suffix contract
- The question should be a real-world business scenario requiring intermediate-level S3 reasoning involving object structure, access control, data protection, lifecycle, cost, and operations. Do not create trivia-style prompts.
- The complexity of the task and specific improvements expected from the candidate must align with intermediate proficiency level (3-5 years experience) requiring practical S3 techniques including:
  - Designing bucket and object key structures aligned to business domains, environments, tenants, dates, regions, datasets, and lifecycle needs
  - Applying least-privilege IAM and bucket policy principles for scoped S3 access
  - Enabling and reasoning about S3 Block Public Access, Object Ownership, and avoidance of legacy ACL dependence
  - Using server-side encryption, versioning, object tags, metadata, and lifecycle policies for data protection and cost control
  - Designing lifecycle transitions and cleanup for current versions, noncurrent versions, delete markers, and tagged object segments
  - Reasoning about S3 storage classes, Intelligent-Tiering, Glacier retrieval trade-offs, and request/storage cost drivers
  - Troubleshooting common S3 symptoms such as 403 AccessDenied, 404 NoSuchKey, CORS failures, lifecycle mismatch, and unexpected scan cost
  - Designing S3 access for compute, analytics, browser/mobile, and content delivery flows at an architectural level
  - Using CloudTrail, Storage Lens, server access log summaries, or simplified monitoring artifacts to diagnose operational issues
  - Documenting S3 design decisions, operational runbooks, and safe change plans for security and compliance stakeholders
- The task may include simplified LocalStack-compatible S3 implementation artifacts, plus textual or JSON policy/configuration artifacts for AWS-only features that LocalStack cannot fully emulate. Do not require expert-only AWS networking, organization-wide SCP design, or high-risk compliance architecture as the primary skill.
- The question must NOT include hints about the specific fixes needed. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to current Amazon S3 best practices for intermediate-level infrastructure work.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, AWS S3 documentation, Terraform documentation, LocalStack documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and improve realistic S3 infrastructure issues at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the task should require genuine intermediate-level cloud storage engineering, security judgment, lifecycle reasoning, and practical problem-solving skills that go beyond simple copy-pasting from a generative AI
- Tasks should involve applied S3 trade-offs and scenario-specific constraints involving security, cost, durability, access, operations, or analytics layout
- Candidates will be encouraged to use AI to help with Terraform syntax and AWS documentation lookup but not replace their own diagnostic thinking and design judgment

## Infrastructure Code Generation Instructions:
Based on the real-world scenarios provided above, create an S3 infrastructure task that:
- Draws inspiration from the input_scenarios given below to determine the business context, S3 usage pattern, and technical requirements
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for practical S3 engineering judgment
- Tests intermediate-level S3 design, access-control, lifecycle, data-protection, cost-optimization, troubleshooting, or migration reasoning using infrastructure files and operational artifacts
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- **CRITICAL**: The infrastructure project should be COMPLETE and FULLY FUNCTIONAL with Docker Compose, LocalStack, Terraform, policies, scripts, and starter data, but with intentionally flawed S3 configuration requiring intermediate-level improvement
- The task should focus on one coherent S3 problem path, such as:
  - Securing a previously public bucket behind a safer access pattern while preserving browser or content-delivery behavior
  - Improving object key layout and metadata for analytics workloads so filtered reports avoid scanning unrelated data
  - Adding lifecycle and tagging behavior that reduces cost without violating retention or legal-hold requirements
  - Troubleshooting cross-account, compute-role, or browser access failures caused by policy, ownership, public access, or CORS interactions
  - Strengthening versioning, delete-marker cleanup, replication-style design, or recovery runbooks for accidental deletion scenarios
  - Reviewing and improving a migration, backup, or data lake object layout with validation and operational safeguards
- Include enough concrete artifacts for the candidate to reason without needing real AWS credentials: policy excerpts, Terraform resources, sample object keys, lifecycle summaries, cost symptoms, access logs, CloudTrail-like events, Storage Lens-like summaries, or verification scripts
- Do not require the candidate to use real AWS. The generated environment must use LocalStack or local files for execution and validation.
- Use AWS CLI commands against the LocalStack endpoint, Terraform configuration targeting LocalStack, or shell validation scripts. If the generated task includes AWS-only concepts not supported by LocalStack, represent them as Terraform/policy/configuration artifacts and validate them structurally.
- **CRITICAL**: The task focuses on improving existing S3 infrastructure, policies, object layout, lifecycle, or operational artifacts, NOT building from scratch.

## Infrastructure Requirements:
- MUST include a complete local S3-compatible deployment using Docker Compose and LocalStack
- MUST include a run.sh which has the end-to-end responsibility of deploying the local infrastructure, installing Terraform provider dependencies, applying the starter infrastructure if appropriate, and performing readiness checks
- MUST include a docker-compose.yml file containing the LocalStack service for S3
- MUST NOT include docker-compose services for PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, or any unrelated datastore
- MUST NOT include init_database.sql or any database initialization file
- MUST NOT include kill.sh — E2B sandboxes are destroyed as a whole when the session ends, so container cleanup is automatic
- Do not include a Dockerfile unless the selected scenario truly requires an application container. For S3 infrastructure-only tasks, omit Dockerfile.
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy cloud services. The task environment will be pre-deployed with working local S3 infrastructure where possible.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

### Docker-compose Instructions:
  - LocalStack service configured for S3 and any minimal supporting AWS-compatible services required by the selected scenario
  - **SECURITY-CRITICAL**: LocalStack ports MUST be bound to localhost only using `127.0.0.1:4566:4566` — NEVER use `4566:4566`
  - Use inline service environment values where LocalStack needs them, such as `SERVICES=s3` and a default region. Do not use `.env` files or `${{VAR}}` host indirection.
  - Network configuration for local service communication if needed
  - Volume mounts for LocalStack state may be included when useful for persistence during the task
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include .env file references or host environment variable indirection**
  - Use hardcoded local configuration values instead of host environment variables
  - LocalStack should expose the edge endpoint on localhost and be ready for Terraform and AWS CLI commands from the sandbox terminal
  - **CRITICAL**: Docker Compose handles service orchestration; run.sh handles readiness checks and Terraform/bootstrap validation

### S3 and LocalStack Configuration Instructions:
- Create Terraform files under an infrastructure directory such as `infra/terraform/` that target the LocalStack S3 endpoint with static dummy credentials
- Include a realistic S3 bucket design with bucket names, object prefixes, tags, metadata, lifecycle rules, encryption configuration, versioning, public access settings, CORS rules, bucket policies, or event notification artifacts as required by the selected scenario
- **CRITICAL: Do not implement the solution in the starter infrastructure files. Create a realistic flawed S3 configuration that requires intermediate analysis and improvement.**
- Include seed objects or scripts that create representative S3 objects with realistic keys, metadata, and tags. Object keys must reflect the selected business scenario, such as `tenant={{tenantId}}/study={{studyId}}/series={{seriesId}}/image={{imageId}}.dcm`, `delivery_events/dt=YYYY-MM-DD/region={{region}}/batch-{{uuid}}.json.gz`, or `posters/{{titleId}}/{{imageId}}.jpg` depending on the selected scenario.
- Include policy JSON, lifecycle summaries, cost reports, access-log excerpts, CloudTrail-like events, or Storage Lens-like CSV/JSON artifacts where they help reveal the issue without giving away the fix
- For lifecycle tasks, include current-version and noncurrent-version behavior that the candidate can reason about, including object tags or prefixes when relevant
- For access-control tasks, include IAM policy and bucket policy artifacts with enough detail to diagnose 403, public-access, Object Ownership, or Block Public Access interactions
- For analytics-layout tasks, include object-key examples and a simplified Glue/Athena-style table definition or query report showing scan-volume symptoms
- For browser/mobile tasks, include CORS and pre-signed/direct-access flow artifacts but do not reveal the exact implementation fix
- Keep all generated artifacts valid, parseable, and runnable where they are intended to run locally

### Run.sh Instructions:
  - FIRST STEP: Change to `/root/task` and install or initialize the task's own infrastructure dependencies, such as running `terraform init` in the Terraform directory to download provider plugins. Do not apt-get or system-install the primary runtime.
  - PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  - WAIT MECHANISM: Implements a proper health check to wait for LocalStack to be fully ready and accepting requests on `localhost:4566`
  - VALIDATION: Validates that the LocalStack S3 endpoint is responding and that the starter Terraform configuration parses, initializes, validates, and applies successfully if the scenario uses Terraform-managed starter resources
  - READINESS ONLY: run.sh is a readiness/self-check, NOT the grader. It must bring LocalStack up, wait for health, verify the starter infrastructure compiles/loads, optionally create starter objects, and then exit 0 on the UNSOLVED starter.
  - TEST SEPARATION: If the task includes Bats, ShellSpec, or verification scripts that are designed to fail until the candidate solves the task, run.sh MUST NOT run those grader-style tests. The candidate or grader runs them separately.
  - MONITORING: Monitors container status and provides feedback on successful deployment
  - ERROR HANDLING: Includes proper error handling for failed container starts, LocalStack health failures, Terraform initialization failures, or S3 endpoint failures
  - LOCATION: All files are located in /root/task directory, ensure Docker and Terraform paths reference this location
  - SIMPLIFIED APPROACH: No real AWS credentials are required. Use LocalStack endpoints and dummy credentials for local execution.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (LocalStack S3 service configuration with localhost-only port binding and no version specification)
  - run.sh (Script to deploy LocalStack, initialize infrastructure dependencies, validate Terraform, and perform readiness checks only)
  - .gitignore (Ignore Terraform state, LocalStack data, logs, editor files, and OS files)
  - infra/terraform/main.tf (Terraform S3 resources with realistic scenario-specific flaws requiring intermediate S3 fixes)
  - infra/terraform/providers.tf (Terraform provider configuration targeting LocalStack with dummy local credentials)
  - infra/terraform/variables.tf (Terraform variables with safe local defaults where useful)
  - infra/terraform/outputs.tf (Outputs that help candidates inspect bucket names, prefixes, and local endpoint details without exposing a solution)
  - policies/ or config/ artifacts (Scenario-specific IAM policy, bucket policy, CORS, lifecycle, event, Glue/Athena, or CloudFront-style configuration files as needed)
  - scripts/seed_s3.sh or scripts/bootstrap_objects.sh (Script that creates representative starter objects, tags, and metadata in LocalStack without implementing the fix)
  - scripts/verify_s3_state.sh or tests/*.bats (Candidate-run checks that focus on observable S3 outcomes and may fail until the task is solved)

## Code file requirements:
- More than one file can be generated but make sure every file is included in the JSON structure correctly
- Terraform files should be valid HCL and should initialize against LocalStack without real AWS credentials
- Shell scripts should be valid POSIX shell or Bash, include meaningful error handling, and reference `/root/task` as the base directory
- Generated policy/configuration files should be valid JSON, YAML, or HCL as appropriate
- **CRITICAL**: The existing infrastructure must be complete and runnable but intentionally flawed according to the selected S3 scenario
- **CRITICAL**: The exact S3 issue described in the task scenario MUST be present in the generated files. Do not describe an issue that is absent from the Terraform, policy, object layout, lifecycle, or script artifacts.
- Do not implement optimized bucket policies, final lifecycle rules, final object key layout, final CORS settings, or final access patterns in the starter files
- Do not include TODO comments, placeholder comments, or comments that reveal the solution
- Do not include comments that give away direct or indirect solution hints in code, Terraform, policy, or script files
- Keep the task focused on S3 and supporting infrastructure artifacts. Do not generate full application code unless the selected scenario absolutely requires a tiny helper function or config file to expose the S3 problem.
- If a small helper function or script is included, it must exist only to demonstrate the S3 integration issue and must not become the primary competency being assessed
- Include realistic business-specific object keys, prefixes, tags, metadata, lifecycle filters, or policy resource ARNs
- For AWS-only features not fully emulated by LocalStack, include configuration artifacts and structural verification rather than requiring live AWS behavior
- The generated files should let candidates inspect, apply, and iterate locally without real AWS credentials
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS:
Generate a comprehensive .gitignore file suitable for S3 infrastructure and Terraform development tasks that includes:
- Terraform state and cache files such as `.terraform/`, `*.tfstate`, `*.tfstate.*`, and crash logs
- LocalStack data directories and generated local object data
- Shell script logs and temporary files
- AWS CLI cache or local credentials files if accidentally created
- Test output files and coverage artifacts if Bats or ShellSpec tests are included
- IDE and editor files
- OS-specific files such as `.DS_Store` and `Thumbs.db`
- Any other standard exclusions for Terraform, Docker Compose, LocalStack, and shell-based infrastructure tasks

## README.md INSTRUCTIONS:
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains the following sections, exactly in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the selected intermediate-level S3 infrastructure scenario. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the specific S3 problem being generated, using concrete business context while avoiding direct solution disclosure.

### Task Overview
- This section MUST contain 3-4 meaningful sentences. No bullet list.
- Describe the business scenario, current state, and why the S3 problem matters.
- Mention the observable symptoms or operational risk at a high level, such as unexpected storage cost, access failures, public exposure risk, inefficient analytics scans, lifecycle gaps, recovery risk, or governance concerns.
- NEVER generate empty content.
- Do not include bold time-budget callouts.

### Objectives
- Include 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Improve bucket security."
- GOOD: "Poster images are currently reachable through a path that conflicts with the company's public-access guardrails; after your changes, approved users should still see images while broad public bucket access is no longer required."

### Helpful Tips
- Include 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, Terraform resource, AWS setting, or algorithm that solves the task.
- Keep tips focused on S3 reasoning, access boundaries, object organization, lifecycle impact, operational symptoms, cost trade-offs, and validation thinking.

### How to Verify
- Include 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as Terraform validation output, LocalStack S3 object state, policy behavior, blocked or allowed access outcome, lifecycle configuration shape, expected object metadata/tags, reduced scan-scope evidence, or script/test output.
- Use `localhost` for any local endpoint reference. Never use a droplet IP or remote-host placeholder.
- Do not include database connection details or client-tool suggestions unrelated to S3.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Make sure you do not include the following in the README.md file:
- Setup commands such as `docker compose up`, `terraform init`, `terraform apply`, `npm install`, `pip install`, `mvn test`, or similar
- Instructions to run the run.sh file
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, Terraform resource names, AWS setting names, library names, pattern names, or data-structure names that reveal the solution
- Code snippets, policy snippets, Terraform snippets, or command sequences that give away the answer
- Database connection details, datastore credentials, droplet IP placeholders, or unrelated client-tool guidance
- Directive phrases like "you should implement", "add this middleware", "create this class", "use this specific API", or "set this exact property"

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "A kebab-case GitHub repository name under 50 characters that concisely identifies the S3 infrastructure task without duplicating the display title.",
   "title": "A human-readable task title in '<action verb> <subject>' format, 50-80 characters, describing the S3 action and subject in plain English and differing from the kebab-case name.",
   "question": "A candidate-facing description of the intermediate-level S3 scenario, the existing flawed infrastructure state, the observable business or operational impact, and the expected outcome without revealing the specific fix.",
   "code_files": {{
      "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify, with open-ended guidance and no direct solution disclosure.",
      ".gitignore": "A comprehensive ignore file for Terraform, Docker Compose, LocalStack, shell scripts, logs, local AWS cache files, test output, editor files, and operating-system artifacts.",
      "docker-compose.yml": "A Docker Compose configuration for LocalStack S3 with no version specification, localhost-only 127.0.0.1:4566:4566 port binding, inline service environment values, and no .env or host-variable indirection.",
      "run.sh": "A readiness script that changes to /root/task, starts LocalStack with docker compose up -d, initializes infrastructure dependencies, waits for localhost S3 readiness, validates or applies the starter Terraform as appropriate, seeds starter objects if needed, and exits successfully on the unsolved scaffold without running grader tests.",
      "infra/terraform/providers.tf": "Terraform provider configuration that targets the LocalStack AWS-compatible endpoint with static dummy credentials and avoids any dependency on real AWS credentials.",
      "infra/terraform/main.tf": "Main Terraform S3 infrastructure containing the scenario-specific bucket, policy, encryption, versioning, lifecycle, CORS, notification, tagging, or object-layout flaw that the candidate must diagnose and improve.",
      "infra/terraform/variables.tf": "Terraform variable definitions with safe local defaults for bucket names, prefixes, regions, tags, and scenario-specific configuration values.",
      "infra/terraform/outputs.tf": "Terraform outputs that expose useful local inspection values such as bucket names, prefixes, endpoint URLs, or verification handles without revealing the solution.",
      "scripts/bootstrap_objects.sh": "A shell script that creates realistic LocalStack S3 starter objects, metadata, tags, or prefixes matching the selected business scenario while preserving the intentional flaw.",
      "scripts/verify_s3_state.sh": "A candidate-run verification script that checks observable S3 outcomes and may fail until the candidate completes the task, while remaining separate from run.sh readiness.",
      "policies/example_policy.json": "A scenario-specific IAM, bucket, access, or service policy artifact that is valid JSON and reflects the flawed access or governance state the candidate must reason about.",
      "config/scenario_artifact.yml": "A scenario-specific configuration artifact such as a lifecycle summary, CORS definition, analytics table definition, replication-style plan, cost report, Storage Lens excerpt, or operational log used to support diagnosis."
   }},
   "answer": "An evaluator-facing high-level solution approach that explains the intended S3 diagnosis and the kinds of infrastructure, policy, lifecycle, object-layout, tagging, encryption, access, or operational changes that would resolve the scenario.",
   "definitions": "An object mapping S3, Terraform, LocalStack, security, lifecycle, policy, cost, or operations terms used in the task to concise definitions that help evaluation without giving candidates extra README sections.",
   "hints": "A single line nudging candidates toward a sound intermediate-level investigation approach without naming the specific S3 setting, Terraform resource, command, or fix required.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable S3 security, access, lifecycle, cost, durability, analytics, or operational improvements using simple English.",
   "pre_requisites": "A bullet list of assumed prior knowledge using declarative capability phrases only, such as Terraform familiarity, comfort with S3 bucket policies and lifecycle concepts, and basic shell/Docker Compose workflow awareness, with no imperative setup or verification steps.",
   "short_overview": "A bullet list summarizing the business problem, the S3 technical focus, the flawed starting point, and the expected secure, cost-aware, or operationally reliable outcome."
}}

## CRITICAL REMINDERS:
1. `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
2. **S3 ONLY**: Keep the primary competency focused on Amazon S3 design, access, lifecycle, data protection, operations, cost, or integration; do not turn the task into a general application-development exercise
3. **INTERMEDIATE LEVEL**: Ensure complexity matches 3-5 years of S3 and cloud infrastructure experience; avoid expert-only organization-wide architecture as the main requirement
4. **FULLY FUNCTIONAL STARTER**: The LocalStack and Terraform scaffold must deploy or validate in its intentionally flawed starting state
5. **NO REAL AWS REQUIRED**: Use LocalStack, dummy credentials, local scripts, and structural artifacts so candidates can work entirely in the E2B sandbox
6. **NO DATABASE FILES**: Do not include docker-compose services for unrelated datastores and do not include init_database.sql
7. **NO KILL SCRIPT**: Do not generate kill.sh because the sandbox is destroyed as a whole
8. **NO SOLUTIONS IN CODE**: Do not include final fixed policies, lifecycle rules, object layouts, or comments that reveal the solution in generated starter files
9. **LOCALHOST ONLY**: Any exposed local service port must bind to localhost, and any local verification endpoint must use localhost rather than a droplet IP or remote placeholder
10. **RUN.SH IS READINESS ONLY**: run.sh must not run failing-as-designed grader tests; it should prove the unsolved scaffold is deployable
"""

PROMPT_REGISTRY = {
    "S3 (INTERMEDIATE)": [
        PROMPT_S3_INTERMEDIATE_CONTEXT,
        PROMPT_S3_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_S3_INTERMEDIATE_INSTRUCTIONS,
    ]
}