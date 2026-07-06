# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_TERRAFORM_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements,
particularly in relation to using Terraform for infrastructure-as-code design, state management, reusable modules,
provider configuration, safe planning, and production change review?
"""

PROMPT_TERRAFORM_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Terraform assessment task.

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
- The task must reflect authentic Terraform infrastructure-as-code challenges that would be encountered in the role described in the role context

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, infrastructure context, and Terraform problem the candidate will be solving)
2. What will the task look like? (Describe the type of Terraform review, refactor, state-safe remediation, provider/module fix, or plan-risk analysis required, the expected deliverables, and how it aligns with the intermediate proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_TERRAFORM_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Terraform infrastructure-as-code, you are given a list of real world scenarios and proficiency levels for Terraform.
Your job is to generate a task, with the given specifications, so that a candidate is presented with a FULLY FUNCTIONAL Terraform project and local infrastructure harness but with realistic configuration, state, provider, module, or workflow issues that require intermediate-level Terraform skills.
The candidate's responsibility is to identify the issue and fix it. So you'll have to be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Terraform repository that can be initialized, formatted, validated, planned, and applied against a local infrastructure emulator or equivalent safe sandbox. The Terraform project includes:
- Existing Terraform root module files, one or more reusable modules, variables, outputs, provider configuration, and documentation
- A docker-compose.yml and run.sh that start the local infrastructure service needed by the task, such as LocalStack for AWS-style resources
- Realistic but intentionally flawed Terraform design choices involving state strategy, provider pinning, aliases, module structure, variables, outputs, lifecycle rules, tagging, or plan safety
- Enough sample configuration and observed plan output context for the candidate to reason about risk without requiring real cloud credentials
- A task scope calibrated for intermediate Terraform practitioners with 3-5 years experience and a completion target of approximately {minutes_range} minutes

The candidate's responsibility is to analyze the Terraform code, interpret the current symptoms, make safe and maintainable infrastructure-as-code changes, and explain any state or migration steps needed before a real production apply. A part of the task completion is to watch the candidate demonstrate Terraform judgment around plan review, state safety, module maintainability, provider behavior, secrets handling, tagging, and collaboration practices at an intermediate level.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Terraform infrastructure-as-code scenario
- Task must provide a working Terraform project with existing files and intentionally suboptimal configuration requiring intermediate-level Terraform analysis and remediation skills
- **CRITICAL**: The Terraform project should be FULLY FUNCTIONAL and runnable in the sandbox, but should contain realistic issues that require the candidate to reason about state, modules, providers, variables, outputs, workspaces, lifecycle behavior, or plan impact
- **CRITICAL**: The exact problem described in the task scenario MUST be replicated in the generated Terraform files, README, and any provided plan excerpts. If the scenario mentions provider version drift, a risky replacement, a missing provider alias, shared state confusion, inconsistent tags, weak variable validation, or a module refactor risk, the actual files MUST contain that issue
- **CRITICAL**: The task focuses on fixing, refactoring, reviewing, or safely migrating existing Terraform configuration, NOT building infrastructure from scratch
- The task should resemble a realistic engineering work item, such as reviewing a pull request, fixing a broken Terraform change, designing a small reusable module, interpreting a risky plan, recovering from state drift, improving an environment strategy, or proposing a safe migration path
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, resource names, and operational constraints are historically accurate and relevant to the context
- Generate a complete Terraform repository suitable for an intermediate-level engineer with 3-5 years experience, with complexity that can be completed in approximately {minutes_range} minutes
- The Terraform task may include practical work involving:
  - Provider version pinning and Terraform version constraints
  - Multiple providers and provider aliases where the selected scenario needs them
  - Reusable modules with clear inputs, outputs, and source/version expectations
  - Typed variables, defaults, validations, and sensitive values
  - Outputs for cross-module or deployment consumption
  - Data sources and dependencies that reflect existing infrastructure lookup patterns
  - Conditional expressions, functions, dynamic blocks, and collection handling where appropriate
  - Workspaces or separate backend configuration for environment segregation
  - Lifecycle rules such as create_before_destroy, prevent_destroy, or ignore_changes when aligned with the scenario
  - State-safe refactoring using moved blocks or a clear state operation plan
  - Plan review and communication of destructive or risky changes
  - Compliance with naming, tagging, least-privilege IAM, and repository organization standards
- The task should NOT require expert-only Terraform architecture, large-scale cloud migrations, advanced custom providers, complex policy-as-code platforms, extensive Terratest setup, or rote memorization of Terraform commands
- The task should NOT require access to real AWS, Azure, or GCP accounts. Use a local emulator such as LocalStack or a safe local provider setup when cloud-like resources are needed
- The task should reward clear reasoning, safe infrastructure judgment, maintainable design, security awareness, pragmatic tradeoffs, and the ability to communicate risk
- The question must NOT include hints about the specific Terraform fixes needed. The hints will be provided in the "hints" field
- Ensure that all questions and scenarios adhere to Terraform best practices for intermediate-level infrastructure-as-code work
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Terraform documentation, cloud provider documentation, registry module documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs)
- The tasks are designed to assess the candidate's ability to identify and fix realistic Terraform infrastructure-as-code issues at an intermediate level, rather than testing rote memorization
- Therefore, the complexity of the task should require genuine intermediate-level Terraform reasoning around state, plan safety, provider behavior, module design, security, and maintainability
- Candidates will be encouraged to use AI to help with implementation and review, but should understand the concepts being applied and be able to justify their decisions

## Infrastructure-as-Code Generation Instructions
Based on the real-world scenarios provided above, create a Terraform infrastructure-as-code task that:
- Draws inspiration from the input_scenarios given below to determine the business context, infrastructure concern, operational constraints, and Terraform work item
- Matches the complexity level appropriate for intermediate proficiency level (3-5 years experience), keeping in mind that AI assistance is allowed but should not diminish the need for intermediate Terraform judgment
- Tests practical intermediate-level Terraform skills around maintainability, state safety, provider configuration, module design, plan interpretation, variables, outputs, lifecycle behavior, and collaboration
- Time constraints: Each task should be finished within {minutes_range} minutes
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation
- **CRITICAL**: The Terraform repository should be COMPLETE and FULLY FUNCTIONAL with all required files, modules, local infrastructure harness, and validation scripts, but with intentionally flawed Terraform decisions requiring intermediate-level remediation
- **CRITICAL**: The scaffold must contain enough working Terraform code for the candidate to modify existing infrastructure-as-code rather than starting from a blank repository
- The task should include a realistic plan-risk or failure symptom, such as a provider lookup failure, unintended resource replacement, inconsistent module behavior, unsafe workspace/backend strategy, missing state migration plan, inconsistent tagging, weak validation, or overly broad IAM policy
- The generated files must be valid and executable in /root/task, and candidates should be able to run standard Terraform commands after the environment is prepared
- Include realistic comments that explain business context or operational constraints, but DO NOT include comments that reveal the solution
- Do NOT include any TODO comments, placeholder comments, or direct fix instructions in Terraform files
- Do NOT include secrets, real credentials, real cloud account IDs, or environment variable based credential setup
- Prefer LocalStack-backed AWS-style examples when a cloud-like external service is needed, because it allows SQS, IAM-like configuration, S3-like state exercises, or other safe infrastructure behavior without real cloud credentials
- If the scenario is primarily a review or remediation plan, still provide concrete Terraform files and a candidate-facing README so the candidate can inspect and edit a realistic repository

## Infrastructure Requirements
- MUST include a complete Terraform project under /root/task with a working local infrastructure harness
- MUST include docker-compose.yml for the external service used by the scenario, such as LocalStack for AWS-style resources or another local emulator appropriate to the selected scenario
- MUST include run.sh which has the end-to-end responsibility of starting the local service and validating that the Terraform project can run basic checks
- MUST NOT include kill.sh. E2B sandboxes are destroyed as a whole, so container cleanup is automatic and a cleanup script is not needed
- **IMPORTANT**: The infrastructure setup is AUTOMATED - candidates will NOT manually deploy or run setup scripts before receiving the task. The task environment will be pre-deployed with the local service available
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory
- **CRITICAL**: All Docker, Terraform, and script references must account for the /root/task base directory

### Docker-compose Instructions
  - Include the local service required by the Terraform scenario, usually LocalStack when AWS-like resources such as SQS, S3, IAM, ACM, CloudFront-adjacent configuration, or ECS-adjacent examples are being emulated
  - Expose only the required local service ports to the host
  - **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>` for every service exposed to the host
  - Use named volumes only when persistence is required for the task to remain stable during validation
  - Include a deterministic network configuration for service communication if more than one service is needed
  - **MUST NOT include any version specification** in the docker-compose.yml file
  - **MUST NOT include environment variables or .env file references**
  - Use hardcoded configuration values in service commands or mounted config files only when absolutely necessary
  - The docker-compose.yml should start the local infrastructure emulator and leave Terraform execution to the candidate or validation script
  - Do NOT include application containers unless the selected scenario explicitly needs an application to demonstrate the Terraform problem

### LocalStack Configuration Instructions
- Use LocalStack or an equivalent local emulator only for the external cloud-like service needed by the selected scenario
- Keep the emulator setup minimal and deterministic so the assessment focuses on Terraform reasoning rather than emulator troubleshooting
- If pre-created local resources are needed for a data source or import/state scenario, create them through mounted initialization scripts or run.sh validation steps without revealing the Terraform fix
- Do NOT include real cloud credentials, real account IDs, real secrets, or environment variable based credential instructions
- Use localhost-bound endpoints and hardcoded dummy values that are safe for local emulation
- Ensure any local resources created for the scenario match the README symptom and Terraform files exactly

### Run.sh Instructions
  + PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`
  + WAIT MECHANISM: Implements a proper health check to wait for the local infrastructure service to be ready and accepting requests
  + VALIDATION: Validates that the Terraform working directory exists, Terraform files are present, and basic commands such as `terraform fmt -check` and `terraform validate` can be run after initialization
  + TERRAFORM SETUP: May run `terraform init` only when it is safe for the scaffold and does not mask the candidate's task; do not run `terraform apply` to solve the problem
  + DATA INITIALIZATION: May create minimal local emulator resources required for data source lookup or state-drift scenarios, but must not implement the Terraform solution
  + MONITORING: Monitors container status and provides feedback on successful local infrastructure startup
  + ERROR HANDLING: Includes proper error handling for failed container starts or unavailable local service endpoints
  + LOCATION: All files are located in /root/task directory, ensure Docker and Terraform paths reference this location
  + SIMPLIFIED APPROACH: No manual cleanup script is needed because the sandbox is disposable

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Local infrastructure service configuration with no version specification and no environment variables)
  - run.sh (Script to start the local infrastructure service and validate Terraform readiness)
  - .gitignore (Ignore Terraform, Docker, local state, editor, and log artifacts)
  - versions.tf (Terraform and provider version constraints with intentionally realistic issues when scenario requires)
  - providers.tf (Provider configuration, aliases, and local emulator endpoint configuration when scenario requires)
  - main.tf (Root module resources or module composition with realistic intermediate-level Terraform issues)
  - variables.tf (Typed input variables, defaults, validations, and sensitivity settings with improvement opportunities)
  - outputs.tf (Outputs for downstream modules or service integration with appropriate sensitivity where needed)
  - locals.tf (Naming, tagging, or collection transformation logic when useful for the scenario)
  - backend.tf or backend documentation file (Remote backend or environment strategy scaffold when the selected scenario involves state isolation or locking)
  - modules/<module_name>/main.tf (Reusable module implementation with realistic design or refactor issues)
  - modules/<module_name>/variables.tf (Module inputs with validation and clear typing expectations)
  - modules/<module_name>/outputs.tf (Module outputs needed by the root configuration or downstream service)
  - plan_excerpt.txt (Observed plan or failure excerpt that demonstrates the issue without giving away the solution)
  - docs/operational-notes.md (Brief internal notes about environments, constraints, and safety expectations when useful)

## Code file requirements
- More than 1 file can be generated but make sure every file is included in the JSON structure correctly
- Terraform files must be syntactically valid HCL and organized as a realistic repository
- The generated project should be immediately inspectable and runnable in /root/task after run.sh has started the local service
- **CRITICAL**: The Terraform files MUST contain the exact issue described in the task scenario. Do not describe a provider alias problem, state migration risk, lifecycle issue, or module refactor risk unless the generated files actually contain that problem
- **CRITICAL**: Do not implement the optimized solution in the starting files. The scaffold should be working or nearly working but flawed in the way the candidate is expected to diagnose and fix
- Include a concise plan excerpt or failure output that reflects the issue and gives the candidate evidence to investigate
- The Terraform code should use intermediate-level constructs only when they are relevant to the scenario, such as provider aliases, data sources, variables with validation, locals, dynamic blocks, lifecycle rules, outputs, moved blocks, or module composition
- DO NOT include comments that give away optimization, state migration, provider alias, lifecycle, or module refactor solutions
- DO NOT include hardcoded real secrets, real credentials, real cloud account IDs, or real production identifiers
- DO NOT include any `.env` files, `.env.example` files, or environment variable references
- The repository should include documentation that helps the candidate understand the business problem while leaving implementation decisions open-ended
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Terraform and Docker-based local infrastructure tasks that includes:
- Terraform working directories such as .terraform/
- Terraform local state files and backup files when appropriate for the local scaffold
- Terraform plan files and crash logs
- Override files and local variable files that may contain secrets
- LocalStack or Docker data directories
- Log files
- IDE and editor files
- OS-specific files such as .DS_Store and Thumbs.db
- Any other standard exclusions for Terraform infrastructure-as-code development

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md contains exactly the following sections, in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

The README.md file content MUST be fully populated with meaningful, specific content relevant to the generated Terraform infrastructure-as-code task. ALL sections must have substantial content; no empty or placeholder text allowed. Content must be directly relevant to the selected real-world scenario and the exact Terraform files generated.

### Task Overview
- This section MUST contain 3-4 meaningful sentences. No bullet list.
- It must describe the business scenario, current infrastructure-as-code state, and why the Terraform problem matters.
- It must make clear that the repository is already present and the candidate is expected to investigate and improve it, not rebuild it from scratch.
- It must be concise, concrete, and business-relevant.
- NEVER generate empty content.
- Do not include bold time-budget callouts.

### Objectives
- This section MUST contain 4-6 bullets max.
- Each objective must give the candidate enough context to understand the problem and start investigating — without revealing the specific fix.
- A good objective names: (1) what is broken or missing, (2) what observable impact that has on the system or user, and (3) what a resolved state looks like.
- It does NOT name the API, library, pattern, command, Terraform block, or algorithm that solves it.
- Objectives describe the 'what' and 'why', never the 'how'.
- Each bullet should be a full, context-rich sentence — not a two-word label.
- BAD: "Fix provider aliases."
- GOOD: "The staging plan cannot locate an existing certificate dependency and blocks a safe edge-domain update; after your changes, the plan should resolve the dependency consistently without changing unrelated resources."

### Helpful Tips
- This section MUST contain 4-5 bullets max.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery — they MUST NOT name the specific API, library, function, pattern, data structure, Terraform block, or exact command that solves the task.
- Tips should focus on Terraform reasoning such as plan review, state safety, module boundaries, provider behavior, environment isolation, tagging consistency, or sensitive data handling.
- If local service access information is needed, include it briefly within a tip without creating a separate connection section.

### How to Verify
- This section MUST contain 4-6 bullets max.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as validation output, plan scope, lack of destructive changes, consistent module outputs, no sensitive values displayed, or local service resources appearing as expected.
- Verification should help candidates compare the starting behavior and the resolved behavior without giving away the exact fix.
- Do NOT include setup commands such as package installation, docker compose startup, or manual environment deployment.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
- Setup commands such as `terraform init`, `terraform apply`, `docker compose up`, package installation commands, or any manual deployment instructions
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, Terraform block names, provider aliases, exact state commands, library names, pattern names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- Database connection sections, cloud credential instructions, host/port credential tables, or `<DROPLET_IP>` placeholders
- Directive phrases like "you should implement", "add this provider alias", "create this module", "use moved blocks", or "run this state command"

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "A kebab-case GitHub repository name under 50 characters that reflects the Terraform infrastructure-as-code task without using spaces or title casing.",
   "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from name and clearly describing the Terraform work the candidate will perform.",
   "question": "A complete candidate-facing task description that explains the selected business scenario, the current Terraform repository state, the observable issue or risk, the expected deliverables, and the constraints without revealing the specific fix.",
   "code_files": {{
      "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify, written with open-ended guidance and no direct solution details.",
      ".gitignore": "A comprehensive Terraform, Docker, local emulator, editor, operating system, and log exclusion file that avoids committing local state or sensitive variable files.",
      "docker-compose.yml": "A Docker Compose configuration for the local infrastructure service required by the scenario, with no version specification, no environment variables, and localhost-only port bindings.",
      "run.sh": "A complete executable setup script that starts the local infrastructure service with docker compose, waits for readiness, validates the Terraform project path, and avoids applying the candidate's solution.",
      "versions.tf": "Terraform version and provider constraint configuration that supports the scenario and may contain realistic versioning issues for the candidate to identify when appropriate.",
      "providers.tf": "Provider configuration for the local infrastructure emulator and any scenario-relevant provider aliases or missing alias behavior that the candidate must reason about.",
      "main.tf": "The root Terraform configuration containing existing resources, module calls, data sources, or locals that reproduce the scenario's infrastructure-as-code issue.",
      "variables.tf": "Typed Terraform input variables with defaults, validations, sensitivity expectations, and intentional quality gaps only when those gaps are part of the task.",
      "outputs.tf": "Terraform outputs needed by downstream services or modules, including realistic sensitivity or completeness concerns aligned with the scenario.",
      "locals.tf": "Terraform local values for naming, tagging, collection shaping, or shared expressions when useful to make the repository realistic and maintainable.",
      "backend.tf": "Backend or environment strategy scaffold used when the selected scenario involves remote state, locking, workspace separation, or migration reasoning.",
      "modules/<module_name>/main.tf": "A reusable Terraform module implementation that is realistic for the scenario and may contain maintainability, tagging, lifecycle, or refactor issues the candidate must improve.",
      "modules/<module_name>/variables.tf": "Module input declarations with type, validation, defaults, and sensitive handling expectations appropriate for intermediate Terraform work.",
      "modules/<module_name>/outputs.tf": "Module outputs that expose resource identifiers or integration values needed by the root module or downstream service.",
      "plan_excerpt.txt": "A realistic Terraform plan, validation, or failure excerpt that demonstrates the observable issue while avoiding direct solution hints.",
      "docs/operational-notes.md": "A short internal operations note describing environment constraints, collaboration expectations, and production-safety concerns without prescribing the fix."
   }},
   "answer": "An evaluator-facing high-level solution approach describing the Terraform reasoning, safe remediation path, state or migration considerations, module/provider changes, validation strategy, and risk tradeoffs expected from an intermediate candidate.",
   "definitions": "An object mapping important Terraform, infrastructure, state, provider, module, environment, or workflow terms used in the task to concise definitions that support consistent evaluation.",
   "hints": "A single line hint that nudges the candidate toward evidence-based Terraform investigation and plan safety without revealing the specific provider, module, state, lifecycle, or command-level fix.",
   "outcomes": "Expected results after completion in 2-3 lines focusing on measurable Terraform improvements such as safe plans, no unintended destroys, consistent provider behavior, maintainable modules, isolated environments, secure handling, or clear operational documentation. Use simple english.",
   "pre_requisites": "A bullet list of tools and knowledge needed for the task, including Terraform CLI familiarity, Docker and Docker Compose basics, Git workflow awareness, plan review, state concepts, provider/module usage, variables and outputs, and intermediate infrastructure-as-code troubleshooting.",
   "short_overview": "Exactly 3 plain sentences where the first sentence states what Terraform infrastructure work is being assessed, the second sentence states what the candidate must do, and the third sentence states what successful completion looks like, with no label prefixes of any kind."
}}

## CRITICAL REMINDERS
1. **TERRAFORM ONLY**: Do not generate application code unless the selected scenario absolutely requires a tiny local helper; the assessment should focus on Terraform infrastructure-as-code
2. **INFRA SHAPE REQUIRED**: Include docker-compose.yml and run.sh for the local external service used by the scenario
3. **NO KILL.SH**: Do not include kill.sh because E2B sandboxes are destroyed as a whole and cleanup is automatic
4. **NO REAL CLOUD CREDENTIALS**: Use local emulation or dummy-safe configuration only, with no real account IDs, secrets, or environment variable instructions
5. **INTERMEDIATE LEVEL**: Ensure complexity matches 3-5 years of Terraform experience and can be completed in approximately {minutes_range} minutes
6. **MEASURABLE PLAN SAFETY**: The task should have observable success criteria such as validation passing, no unintended destroys, stable provider selection, preserved resource identities, consistent outputs, or isolated environment state
7. **NO SOLUTIONS IN CODE**: Do not include fixed provider aliases, optimized module designs, correct state migration commands, or direct solution comments in the generated starter files
8. **README LIMITS**: README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no Database Access, setup commands, or direct implementation instructions
9. **TITLE REQUIRED**: `"title"` must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
10. **SHORT OVERVIEW FORMAT**: `"short_overview"` must be exactly 3 plain sentences with no label prefixes such as "Business problem:", "Technical focus:", or "Expected outcome:"
"""

PROMPT_REGISTRY = {
    "Terraform (INTERMEDIATE)": [
        PROMPT_TERRAFORM_INTERMEDIATE_CONTEXT,
        PROMPT_TERRAFORM_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_TERRAFORM_INTERMEDIATE_INSTRUCTIONS,
    ]
}