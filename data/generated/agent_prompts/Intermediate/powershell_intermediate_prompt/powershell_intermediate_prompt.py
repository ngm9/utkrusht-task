# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""PowerShell INTERMEDIATE prompt."""

PROMPT_POWERSHELL_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_POWERSHELL_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a INTERMEDIATE assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task must run on PowerShell Core only: pwsh 7+ on Ubuntu Linux.
- Do not include any Windows-only surfaces: no registry, no Active Directory, no Task Scheduler, no WMI/CIM, and no Windows services.
- The task is NON-INFRA: no Docker, no databases, no external services, and no datastore configuration.
- The task must ship as a local PowerShell project containing a .psm1 module, .ps1 scripts, and a Pester 5 test suite.
- The starter code must be runnable and structurally valid, but intentionally broken in the observable ways required by the selected scenario.
- The task should exercise intermediate PowerShell module work: advanced functions, pipeline behavior, reusable module structure, streaming over large inputs, and testable DateTime logic with injectable clocks.
- The task must be completable within {minutes_range} minutes by a candidate with 3-5 years of experience.
- Pick a different scenario each time for variety.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate build or fix, and how does it match INTERMEDIATE PowerShell level?
"""

PROMPT_POWERSHELL_INTERMEDIATE_INSTRUCTIONS = """
# INTERMEDIATE Task Requirements - PowerShell Core

## GOAL
As a technical architect super experienced in PowerShell Core automation on Linux, you are given a list of real world scenarios and proficiency levels for PowerShell.

Generate a complete assessment task - description, starter code files, README, run script, and Pester tests - that tests a candidate at INTERMEDIATE proficiency with PowerShell. The task must assess applied module maintenance and automation pipeline judgment, not trivia. It must be a realistic work item involving a reusable PowerShell module and scripts that run under pwsh 7+ on Ubuntu Linux.

The task must be completable within {minutes_range} minutes.

## CONTEXT & CANDIDATE EXPECTATION
Company Context:
{organization_background}

Role Context:
{role_context}

Competencies:
{competencies}

Real-world scenarios:
{real_world_task_scenarios}

The candidate is expected to have 3-5 years of practical automation experience. They should be able to read an existing PowerShell Core module, understand advanced function behavior, reason about pipeline input and large input streams, preserve structured output, and improve testability without being handed the implementation approach.

The generated repository must be FULLY FUNCTIONAL as a local PowerShell project on Ubuntu: dependencies can be installed by run.sh, the module imports without syntax errors, scripts are present, and the Pester suite can be collected and executed. The starter implementation should remain intentionally incorrect in the scenario-specific behavior so that tests fail until the candidate completes the task.

## INSTRUCTIONS
- Generate a realistic task based on ONE selected real-world scenario above.
- The employer context explains who is administering the assessment; the task domain should come from the selected scenario.
- The task must be NON-INFRA. Do not include Docker, docker-compose, databases, caches, queues, brokers, search services, init SQL, or any external service.
- The task must run with PowerShell Core only: pwsh 7+ on Ubuntu Linux.
- Absolutely no Windows-only PowerShell surfaces are allowed: no registry provider, no Active Directory modules, no Task Scheduler, no WMI/CIM, and no Windows services.
- Tests must use Pester 5 and be runnable with pwsh -Command Invoke-Pester.
- Create a small but realistic local project layout with multiple interacting files. For INTERMEDIATE level, the codebase must be more than a toy snippet: include a .psm1 module, one or more .ps1 scripts, a native PowerShell module manifest where useful, fixtures or sample data, and a Pester test suite.
- The candidate must need to reason across more than one file. Avoid a one-line fix in an obvious location.
- The starter code MUST run cleanly enough for the test runner to collect and execute tests, but the tests should fail because the task behavior is incomplete or buggy.
- Do NOT include the solution, solution-shaped TODO comments, or comments that tell the candidate which PowerShell construct to use.
- For executable code, always invoke PowerShell explicitly as pwsh, never powershell.exe or Windows PowerShell.
- Time box: each task MUST be completable within {minutes_range} minutes.

### Nature of the Task
**CRITICAL**: This is an INTERMEDIATE PowerShell Core task. The candidate should see a realistic existing module and scripts with observable behavior problems, not a blank exercise and not an expert-level architecture problem.

**CRITICAL**: Keep the task within PowerShell intermediate scope. It may involve reusable .psm1 module structure, advanced functions, controlled exports, parameter validation, pipeline input behavior, structured object output, CSV or JSON handling, semantic version comparison, DateTime parsing and clock injection, large-input streaming, per-item error handling, idempotent dry-run behavior, REST-shaped code with mocks only if the selected scenario calls for it, and Pester 5 tests.

**CRITICAL**: Do not require Windows administration knowledge or Windows-only APIs. The scenario, code, tests, and README must be Linux-safe and pwsh 7+ compatible on Ubuntu.

**CRITICAL**: The task must assess outcomes, not memorization. The generated README Objectives for INTERMEDIATE level must be concise and open-ended. They should describe what is wrong and what successful behavior looks like without naming the exact API, function, method, file, parameter, pattern, or data structure that solves it.

**CRITICAL**: Do not reveal the fix by listing exact broken implementation choices in the candidate-facing README or in obvious starter-code comments. Describe observable symptoms in the question and README. The code itself may naturally contain flawed logic, but it must not announce the intended repair.

**CRITICAL**: The starter code should be broken in the specific ways the selected scenario describes. For example, if the scenario is about unsafe batch processing, the repository should demonstrate unsafe observable outcomes under test; if the scenario is about incorrect time-window handling, the repository should demonstrate incorrect observable behavior around the supplied fixtures. Do not replace scenario-specific behavior with unrelated generic bugs.

**CRITICAL**: Because this is INTERMEDIATE, the project must include multiple files with realistic interactions. The candidate should need to inspect the module, scripts, fixtures, and tests to understand the expected behavior.

The task should generally involve improving an operational automation module or data-processing workflow. Suitable task themes include safer batch processing, robust CSV or JSON ingestion, stream-friendly reporting over many files, testable time-window filtering, version comparison in deployment reports, idempotent dry-run behavior, or a mocked API client workflow if that is clearly part of the selected scenario. Do not add live external API calls or require credentials.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PowerShell documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- Candidates may use these tools to research syntax, understand errors, and explore implementation ideas.
- The assessment evaluates their ability to deliver a working, maintainable solution in the provided codebase.
- Do not prohibit or discourage use of AI tools or documentation.
- The generated task must still require the candidate to understand, adapt, and validate the code rather than paste a generic answer.

## PowerShell Core Generation Instructions
- Generate a PowerShell Core project that runs on Ubuntu with pwsh 7+.
- Include a .psm1 module containing exported functions relevant to the selected scenario.
- Include .ps1 scripts that exercise the module in a realistic command-line workflow.
- Include a Pester 5 test suite under a tests directory.
- Include fixtures or sample files when useful for the scenario. Keep them small enough for the prompt output but representative enough to expose edge cases.
- Include a PowerShell module manifest file if useful for a native module layout. The manifest must be Linux-safe and must not reference Windows-only assemblies, paths, or editions.
- Use advanced-function style where appropriate for the starter module, but do not place solution-revealing comments in the code.
- Include pipeline-oriented behavior in the task surface. The candidate should have to preserve or repair behavior when records are passed through the pipeline as well as through script parameters.
- Include DateTime-dependent behavior with a testable injected reference clock when the selected scenario involves age, freshness, cutoff windows, scheduling reports, retention, or similar time logic.
- Keep data processing stream-friendly. The generated task should make large-input behavior relevant without forcing enormous files into the prompt.
- Pester tests should cover normal cases, edge cases, and at least one scalability or streaming-oriented expectation appropriate for an intermediate task.
- The tests should be visible to the candidate and should fail on the starter implementation because of scenario behavior, not because of environment setup.
- The tests may use Pester mocks for command boundaries, filesystem fixtures, or script invocation checks, but they must not require external services or credentials.
- All paths and scripts must work on Linux. Use forward-compatible path construction in PowerShell source rather than hardcoded Windows paths.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## Infrastructure Requirements
This is a pure local PowerShell project. It must not provision infrastructure, start services, or require network-accessible dependencies beyond installing PowerShell or Pester if missing.

### Docker-compose Instructions
Do not create docker-compose.yml. Do not mention docker compose commands in the README. Do not include any datastore service.

### Datastore / init_database.sql Instructions
Do not create init_database.sql. Do not include any database schema, database connection details, seed data for a database, or datastore configuration.

### Run.sh Instructions
Create a run.sh script at the repository root.

The run.sh script is a deployability probe, not the grader. It must prepare the local PowerShell test environment and prove that the Pester suite can be collected and executed. It must not require the tests to pass on the unsolved starter code.

run.sh must:
- Use /root/task as the working directory.
- Install PowerShell Core if pwsh is missing. The script may use apt-based installation suitable for Ubuntu, including Microsoft package setup if needed, but it must not install or invoke Windows PowerShell.
- Install Pester 5 if it is missing or if only an incompatible Pester version is available. Installing with pwsh and Install-Module is acceptable when needed.
- Run the Pester suite with pwsh -NoProfile -Command Invoke-Pester or an equivalent pwsh command that invokes Pester 5.
- Capture the Pester result and distinguish between a collected suite with failing tests and a broken scaffold.
- Exit 0 when Pester collected and executed the suite, even if some tests fail as designed on the starter code.
- Exit non-zero only when the project cannot boot, the module cannot import, Pester cannot run, no tests are collected, or the test runner itself errors.
- Avoid a bare set -e around the test invocation because failing tests are expected before the candidate solves the task.
- Print concise diagnostic output showing the pwsh version and Pester version used.

### Dockerfile Instructions
Do not create a Dockerfile. This task must run directly in the Ubuntu sandbox with pwsh.

The output should be a valid json schema:
- "README.md": Candidate-facing task overview with exactly the required README sections.
- ".gitignore": Linux and PowerShell appropriate ignores.
- "run.sh": Local deployability probe that installs pwsh and Pester if missing, then invokes Pester 5 while honoring the failing-tests-are-deployable contract.
- "module manifest": Native PowerShell module manifest when useful for the project structure.
- "module .psm1 file": Starter module implementation with realistic incomplete or buggy behavior.
- "scripts .ps1 files": Scenario-oriented scripts that import and exercise the module.
- "tests/*.Tests.ps1": Pester 5 tests that collect and execute on Ubuntu.
- "fixtures or sample data": Small CSV, JSON, or text fixtures when useful to demonstrate the scenario.

## Code file requirements
- The generated code_files object must contain every file needed to run the task locally.
- The starter code must be syntactically valid PowerShell Core and must import under pwsh 7+ on Ubuntu.
- The module must be organized as reusable PowerShell code rather than a single monolithic script.
- Use .psm1 for module code and .ps1 for executable scripts.
- Pester tests must use Pester 5 syntax and be executable via pwsh.
- Keep the current implementation intentionally flawed in scenario behavior, but do not create syntax errors, missing files, broken imports, or invalid test configuration.
- The candidate should need to modify more than one file or reason across more than one file to complete the task.
- Do not include solution-revealing TODO markers or comments such as "fix streaming here", "add CmdletBinding here", "use begin/process/end here", "inject clock here", or "replace this with semantic version comparison".
- Prefer observable broken behavior in tests and sample outputs over explanatory comments that reveal the repair.
- Keep the project self-contained. No Docker, no databases, no external services, and no required API keys.
- Do not include Windows-only examples, paths, providers, cmdlets, services, or assumptions.
- The answer field may describe the high-level evaluator-facing solution approach, but the candidate-facing README and code comments must remain open-ended.

## .gitignore INSTRUCTIONS
Generate a .gitignore appropriate for a PowerShell Core project on Linux. Include common temporary files, logs, coverage output, editor directories, Pester artifacts, and local scratch data. Do not ignore the module, scripts, tests, fixtures, README, or run.sh.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md file must contain EXACTLY these sections in this order and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Do not add Database Schema Overview, Database Access, Performance Issues, Setup, Installation, Architecture, Implementation Plan, or NOT TO INCLUDE sections. Do not include database-connection details, hostnames, ports, usernames, passwords, client-tool suggestions, Docker commands, or droplet placeholders.

### Task Overview
- Write 3-4 meaningful sentences.
- Do not use a bullet list.
- Describe the business scenario, the current state, and why the problem matters.
- NEVER leave this section empty.
- Do not include bold time-budget callouts.
- Mention only observable symptoms and business impact. Do not name the exact fix.

### Objectives
- For INTERMEDIATE level, include 3-4 bullets maximum.
- Objectives MUST be concise and OPEN-ENDED.
- Each objective states ONE desired outcome in a single short line, roughly 8-16 words.
- Describe the what and why, NEVER the how.
- Do NOT name the API, cmdlet, library, framework, pattern, algorithm, configuration knob, file, file path, directory, function, method, class, variable, test name, or any direct code reference.
- Do NOT write long two-clause sentences that spell out before-and-after mechanics.
- Do NOT collapse objectives into bare labels.
- Objectives must read as NATURAL full sentences from a stakeholder's point of view (operator, on-call engineer, downstream consumer) — never as terse noun-phrase labels.
- Do NOT phrase objectives so they point at where a defect lives (e.g. naming a specific input shape or condition that only matters because of the bug).
- Good style: "Make the findings trustworthy enough to rely on during a live incident review."
- Good style: "Results must be correct no matter what time of day the process runs."
- Good style: "A few bad input files must not invalidate the run, and the operator should know they occurred."
- Bad style (too label-like): "Preserve newest retained artifacts for each repository."
- Bad style (points at the defect): "Multi-page inputs should produce complete counts."

### Helpful Tips
- Include 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet must start with an action word such as "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips should guide discovery.
- Tips MUST NOT name the specific API, library, function, pattern, data structure, cmdlet, method, parameter, or algorithm that solves the task.

### How to Verify
- Include 3-5 bullets maximum.
- Frame verification in terms of observable outcomes.
- Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as test output, generated report shape, consistent dry-run behavior, stable results around supplied fixture dates, or acceptable behavior over larger sample inputs.
- It is acceptable to say that the Pester suite should pass after the task is completed, but do not reveal individual assertion internals.

**CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section):**
Keep the following out of the README:
- Setup commands such as apt install, pwsh installation commands, Install-Module, docker compose up, npm install, pip install, or similar.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, cmdlet names, parameters, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this parameter", "create this function", "use this cmdlet", or "change this file".

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as "task_title", "files", or "context" — synonyms produce a hollow, unusable task.

Return a single valid JSON object with exactly this structure. Each value below describes what to fill in:

{{
  "name": "A short kebab-case GitHub repository name under 50 characters that is distinct from the title and specific to the selected PowerShell task.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters long, different from name, and focused on the task outcome.",
  "question": "The full candidate-facing task description. It must include the selected business scenario, the observable current implementation problems, the required behavioral outcomes, the Linux-only pwsh 7+ constraint, and the expectation that the candidate works in the provided module, scripts, and tests without revealing the implementation solution.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no additional sections and no solution-revealing setup or implementation commands.",
    ".gitignore": "A PowerShell Core and Linux appropriate gitignore that excludes temporary files, logs, editor folders, coverage output, and local scratch artifacts while keeping all task source and fixtures tracked.",
    "run.sh": "A Bash deployability probe located at the repository root that works from /root/task, installs pwsh and Pester 5 if missing, invokes the Pester suite with pwsh, exits 0 when tests are collected and executed even if assertions fail, and exits non-zero only for broken setup or runner failures.",
    "ModuleName.psd1": "A native PowerShell module manifest if included, configured for Linux-safe PowerShell Core module loading and exports without Windows-only references.",
    "ModuleName.psm1": "The starter PowerShell module containing realistic advanced-function-oriented automation code with scenario-specific observable flaws, valid syntax, no solution comments, and exported behavior used by scripts and tests.",
    "scripts/example-script.ps1": "One or more Linux-safe PowerShell scripts that import the module and exercise the scenario workflow using the included fixtures or sample input.",
    "tests/Module.Tests.ps1": "A Pester 5 test suite that imports the module, uses local fixtures or mocks as needed, covers normal and edge cases plus an intermediate-level scale or streaming expectation, and fails on the starter implementation for behavioral reasons.",
    "fixtures/sample-data-file": "Small representative CSV, JSON, text, or directory fixtures needed by the scripts and tests to reproduce the selected scenario without external services."
  }},
  "answer": "Evaluator-facing high-level solution approach in prose. Summarize the kinds of corrections a strong intermediate PowerShell solution would make, the tradeoffs involved, and why those changes satisfy the tests, without needing to include full code.",
  "definitions": "An object mapping task-relevant terms to concise definitions. Include only terms helpful for understanding the scenario and PowerShell automation context; do not include solution-revealing implementation vocabulary.",
  "hints": "A single-line hint that nudges investigation toward the observable symptom and relevant code area without naming the exact fix, API, cmdlet, parameter, pattern, or data structure.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable behavioral correctness, reliable Linux PowerShell execution, and robust processing of the supplied inputs. Use simple english.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as PowerShell Core 7 proficiency, comfort with reusable modules and scripts, familiarity with Pester-based verification, and understanding of structured automation output. Do not include setup, install, run, configure, or verify steps.",
  "short_overview": "A bullet list summarising the business problem, the PowerShell module or automation focus, and the expected candidate outcome."
}}

## CRITICAL REMINDERS
1. Output JSON must use the canonical key names exactly: name, title, question, code_files, answer, definitions, hints, outcomes, pre_requisites, short_overview.
2. The task must be PowerShell Core on Linux only: pwsh 7+ on Ubuntu.
3. Absolutely no Windows-only surfaces: no registry, no Active Directory, no Task Scheduler, no WMI/CIM, and no Windows services.
4. This is NON-INFRA: do not include Docker, docker-compose.yml, init_database.sql, databases, caches, queues, brokers, search services, or external services.
5. The repository must include a .psm1 module, .ps1 scripts, run.sh, and Pester 5 tests.
6. run.sh must install pwsh and Pester if missing, run Invoke-Pester via pwsh, and exit 0 when tests are collected and executed even if tests fail on the unsolved starter.
7. Starter code must be FULLY FUNCTIONAL as a scaffold: imports work, tests collect, scripts are present, and failures are behavioral.
8. Starter code must preserve the specific observable broken state from the selected scenario without solution-revealing comments.
9. README must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, and no other sections.
10. INTERMEDIATE README objectives must be concise and open-ended; do not name implementation mechanisms, files, functions, cmdlets, APIs, methods, parameters, patterns, or data structures.
11. The codebase must be substantial enough for 3-5 years experience: multiple interacting files, realistic module structure, and non-trivial behavior to reason about.
12. All code and scripts must reference /root/task as the base directory.
13. If diagrams are included, ensure they are written in mermaid format, properly indented and also in code blocks.
14. Completable within {minutes_range} minutes.
"""

PROMPT_REGISTRY = {
    "PowerShell (INTERMEDIATE)": [
        PROMPT_POWERSHELL_INTERMEDIATE_CONTEXT,
        PROMPT_POWERSHELL_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_POWERSHELL_INTERMEDIATE_INSTRUCTIONS,
    ]
}