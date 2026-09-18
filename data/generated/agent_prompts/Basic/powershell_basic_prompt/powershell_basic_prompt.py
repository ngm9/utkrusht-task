# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "non_infra"


"""PowerShell BASIC prompt for Linux pwsh scripting tasks."""

PROMPT_POWERSHELL_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, summarize what you understand about the company and
the role requirements before we proceed.
"""

PROMPT_POWERSHELL_BASIC_INPUT_AND_ASK = """
Now that you understand the company context, here are the inputs for generating
a BASIC PowerShell assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL QUESTION CALIBRATION SIGNAL:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task MUST be PowerShell Core on Linux ONLY and must run with pwsh 7+ on Ubuntu.
- Absolutely no Windows-only surfaces are allowed: no registry, no Active Directory, no Task Scheduler, no WMI/CIM, and no Windows services.
- The task is NON-INFRA: do not include Docker, docker-compose.yml, init_database.sql, databases, caches, queues, brokers, or external services.
- The task must use plain .ps1 scripts plus a Pester 5 test file.
- Include run.sh. It must install PowerShell and Pester if missing, then run the Pester suite via pwsh -Command Invoke-Pester.
- The starter code must be runnable but intentionally broken in the specific ways described by the selected scenario.
- The task must be a small, well-scoped feature or bug fix combining 2-3 BASIC PowerShell concepts.
- It must be completable within {minutes_range} minutes by a candidate with 1-2 years of experience.

Briefly confirm your understanding:
1. What will the task be about (domain, context, problem)?
2. What will the candidate fix or complete, and how does it match BASIC PowerShell level?
3. Which starter-code behaviors will be intentionally broken, and how will Pester expose them?
"""

PROMPT_POWERSHELL_BASIC_INSTRUCTIONS = """
# BASIC Task Requirements (PowerShell Core on Linux)

## GOAL
As a technical architect super experienced in PowerShell Core automation on Linux, you are given a list of real world scenarios and proficiency levels for PowerShell.

Generate a complete assessment task — description, starter code files, README, run.sh, and Pester tests — that tests a candidate at BASIC proficiency (1-2 years experience). The task must be a well-scoped PowerShell Core scripting feature or bug fix combining 2-3 concepts from everyday operational automation.

The generated task MUST run with pwsh 7+ on Ubuntu. It MUST NOT use Windows-only PowerShell surfaces such as registry, Active Directory, Task Scheduler, WMI/CIM, or Windows services.

## CONTEXT & CANDIDATE EXPECTATION
The candidate is a BASIC PowerShell practitioner with roughly 1-2 years of experience. They should be able to read and fix simple PowerShell Core scripts that automate routine operational tasks on Linux, including file handling, CSV or JSON processing, simple functions, pipeline filtering, structured objects, warnings, and basic error handling.

The task should be practical and realistic, but small. A good task might involve fixing a script that reads operational data from CSV or JSON, filters or groups records with the object pipeline, emits a structured report, validates input paths, handles malformed records gracefully, or supports a simple dry-run style behavior. The candidate should not need advanced PowerShell internals, production-scale design, complex remoting, or platform-specific Windows administration knowledge.

## INSTRUCTIONS
- The task asks the candidate to implement a feature or fix bugs in existing starter code.
- Focus on 2-3 BASIC PowerShell concepts only, such as:
  - variables, arrays, and hashtables for simple operational data;
  - if/elseif/else, switch, foreach, or while for straightforward control flow;
  - simple functions with named parameters and basic validation attributes;
  - object pipeline usage with Where-Object, Sort-Object, Group-Object, Select-Object, or Measure-Object;
  - Import-Csv, Export-Csv, ConvertFrom-Json, ConvertTo-Json, Get-Content, and Set-Content;
  - Test-Path, Get-ChildItem, New-Item, Copy-Item, Move-Item, Remove-Item, or Get-FileHash;
  - try/catch, -ErrorAction, Write-Warning, Write-Verbose, and clear failure behavior.
- Generate a small, focused starter codebase: a handful of files with one clear area to fix. Keep the surface area small and the reasoning shallow.
- The starter code MUST run cleanly enough for Pester to execute. It may fail assertions because the business logic is intentionally broken, but it must not have syntax errors, missing files, or broken imports.
- The starter code MUST implement exactly the "Current Implementation" buggy/incomplete state described in the candidate-facing task.
- The starter code must be broken in scenario-specific ways, not generic TODO placeholders. Examples of acceptable BASIC bugs include incorrect filtering, missing validation, unsafe overwrite behavior, unstructured output, skipped malformed input handling, case-sensitive path assumptions on Linux, or incorrect CSV/JSON field handling.
- Do NOT include the solution, TODO comments, solution-shaped comments, or hints in the starter code.
- Use plain PowerShell files: .ps1 scripts and .Tests.ps1 Pester tests. Do not create a module unless the selected scenario truly needs one.
- **CRITICAL**: The task is NON-INFRA. Do not include Docker, docker-compose.yml, Dockerfile, init_database.sql, databases, caches, queues, brokers, search services, or any other external service.
- **CRITICAL**: PowerShell Core on Linux ONLY. All commands and examples must use pwsh, Linux paths, and Ubuntu-compatible shell behavior.
- **CRITICAL**: No Windows-only surfaces: no registry, no Active Directory, no Task Scheduler, no WMI/CIM, no Windows services, no drive-letter assumptions, and no backslash-only paths.
- **CRITICAL**: Tests must use Pester 5 and must be runnable with pwsh -Command Invoke-Pester.
- Avoid: advanced remoting, DSC, runspaces, jobs, parallelism, complex security hardening, cloud provider automation, CI/CD deployment, system design, Windows administration, and broad cross-platform compatibility design beyond basic Linux path awareness.
- Time box: each task MUST be completable within {minutes_range} minutes.
- Task name: short, under 50 characters, kebab-case.
- **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### Nature of the Task
The task should simulate a small real-world operations scripting issue. The candidate receives a FULLY FUNCTIONAL local repository that can be opened and tested immediately in an Ubuntu sandbox, but the script's business behavior is incomplete or incorrect.

The README Objectives must be SHORT and OPEN-ENDED: one line per objective describing a desired outcome from the operator's point of view. Do NOT enumerate the specific defects ("the script currently ignores X"), name the broken behavior's location, or hint at the fix. The candidate must diagnose WHY behavior is wrong themselves; objectives only tell them what reliable behavior looks like.

The best BASIC PowerShell tasks are small and concrete:
- A reporting script reads CSV or JSON input but mishandles missing fields, invalid rows, or output sorting.
- A file cleanup script performs the right scan but ignores dry-run behavior or writes unsafe paths.
- A manifest validation script computes hashes but omits failed-file handling or emits raw strings instead of structured objects.
- A log summarizer groups records incorrectly or fails to emit warnings for malformed entries.

**CRITICAL**: The candidate should need to use PowerShell language fundamentals and common cmdlets, not memorize obscure options.

**CRITICAL**: The task should test practical scripting judgment: object pipeline use, structured output, safe file handling, basic validation, and clear warnings/errors.

**CRITICAL**: The generated repository must be small enough for a BASIC candidate to understand quickly, but realistic enough that the tests exercise meaningful behavior.

## AI AND EXTERNAL RESOURCE POLICY
Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, PowerShell documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).

- External resources may be used to look up syntax, standard cmdlet behavior, Pester usage, PowerShell Core behavior on Linux, and examples of common scripting patterns.
- Candidates must still understand, adapt, and integrate any information they use into the provided starter code.
- The final submitted work must be their own implementation and must satisfy the provided tests and task requirements.
- The assessment evaluates their ability to reason about the existing code, make safe practical changes, and verify observable behavior, not their ability to memorize documentation.

## Code Generation Instructions
Generate a pure local PowerShell project. The output should include plain .ps1 scripts, a Pester 5 test file, README.md, .gitignore, and run.sh. Do not include any Docker or datastore configuration.

The repository should be FULLY POPULATED and immediately usable under /root/task. The unsolved starter repository must allow the test runner to collect and execute tests. The tests may fail because the candidate has not fixed the script yet; that is expected.

Recommended file layout:
- README.md
- .gitignore
- run.sh
- scripts/<task-script>.ps1
- tests/<task-script>.Tests.ps1
- data/<small-input-file>.csv or data/<small-input-file>.json
- output/ or reports/ only if the scenario needs a generated destination directory

Keep the file count modest. For BASIC proficiency, a good starter codebase usually contains one main script, one test file, one or two small fixture files, README.md, .gitignore, and run.sh.

The script should:
- use pwsh-compatible syntax;
- avoid Windows-only cmdlets and providers;
- use Linux-safe relative paths or paths rooted under /root/task;
- define one or two simple functions when appropriate;
- produce structured output where the scenario calls for it;
- read or write CSV/JSON/files only when relevant to the selected scenario;
- fail fast or warn clearly for common malformed inputs;
- be idempotent and safe to re-run where the scenario involves generated files.

### Run.sh Instructions
Include a run.sh file at the repository root.

run.sh is a deployability and readiness probe for the local project, not a hidden grader. It must:
- use #!/usr/bin/env bash and set -u at minimum;
- cd to /root/task before running project commands;
- install PowerShell Core if pwsh is missing, using Ubuntu-compatible apt-based installation steps when possible;
- install Pester 5 if it is missing, using pwsh and Install-Module Pester with a CurrentUser scope or another Linux-compatible approach;
- run the Pester suite via pwsh -Command Invoke-Pester;
- capture the Pester exit code and distinguish a deployable failing starter from a broken scaffold.

For this BASIC test-suite shape, run.sh MUST exit 0 when Pester collected and executed the suite, even if assertions fail because the starter is intentionally broken. It must exit non-zero only when the project cannot boot, pwsh cannot run, Pester cannot be installed/imported, tests cannot be discovered, or the test command itself errors before meaningful execution.

The script must not use Docker. It must not start databases or external services. It must not install Windows-only components.

A suitable pattern is:
- check command -v pwsh;
- install pwsh only if missing;
- run pwsh -NoLogo -NoProfile -Command to install/import Pester 5 if needed;
- run pwsh -NoLogo -NoProfile -Command "Invoke-Pester -Path ./tests -PassThru";
- inspect the returned Pester result enough to detect whether tests were discovered and executed;
- exit 0 when tests ran, regardless of failed assertions;
- exit non-zero when no tests ran or Pester failed to start.

The output should be a valid json schema:
- README.md: concise candidate-facing task description with exactly the required README sections.
- .gitignore: standard exclusions for a local PowerShell scripting project.
- run.sh: Ubuntu-compatible readiness script that installs pwsh/Pester if missing and invokes Pester.
- scripts/<task-script>.ps1: runnable but intentionally buggy/incomplete PowerShell Core script matching the Current Implementation.
- tests/<task-script>.Tests.ps1: Pester 5 tests that expose the required behavior.
- data/<fixture>.csv or data/<fixture>.json: small deterministic input data if the scenario needs file processing.
- Any generated-output directory placeholder only when the scenario needs it, such as a .gitkeep file.

## Code file requirements
- All generated files must be complete and FULLY POPULATED. Do not use placeholders.
- All code and scripts must reference /root/task as the base directory when absolute paths are needed.
- PowerShell scripts must run with pwsh 7+ on Ubuntu.
- Use LF line endings and Linux-compatible paths.
- Do not include registry paths, Windows drive letters, backslash-only paths, Active Directory cmdlets, WMI/CIM cmdlets, Windows service cmdlets, Task Scheduler commands, or Windows-only assumptions.
- Pester tests must target the candidate-visible behavior and should be clear enough for a BASIC candidate to understand.
- Pester tests must not rely on external services, network access, databases, Docker, or Windows.
- The test file should import or invoke the .ps1 script in a simple way appropriate for a script-based task.
- The starter code must be intentionally incorrect only in the task-relevant business logic. Do not break setup, paths, syntax, or test discovery.
- Do not hide the solution in comments, verbose messages, test names, or fixture names.
- Do not include TODO comments. The README should describe the current broken behavior and required outcomes.
- Prefer PowerShell objects and pipeline operations over brittle raw text parsing where that is part of the intended assessment.
- Keep fixtures small and readable.

## .gitignore INSTRUCTIONS
Create a .gitignore appropriate for a local PowerShell scripting task. Include common transient files and outputs such as:
- generated report/output directories if the task creates them;
- temporary files;
- editor metadata;
- OS metadata;
- Pester test result files;
- PowerShell module cache or local tool cache only if the generated task creates one.

Do not ignore the starter scripts, tests, README, run.sh, or required fixture data.

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md entry inside code_files MUST contain exactly these sections, in this order, and no others:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

### Task Overview
Write 3-4 meaningful sentences. No bullet list. Describe the business scenario, current state, and why the problem matters. This section is NEVER empty. Do not include bold time-budget callouts.

For this PowerShell task, the overview should mention that the repository contains a Linux pwsh script with starter behavior that is currently incomplete or incorrect for the selected operational scenario. It should not mention Docker, databases, Windows administration, or any external service.

### Objectives
Include 4-6 bullets max. Objectives MUST be SHORT and OPEN-ENDED: one line each (roughly 8-18 words), stating a desired outcome from the operator's or consumer's point of view. Do NOT describe the current broken behavior, name where the defect lives, or hint at the mechanism of the fix — the candidate must diagnose the defects themselves.

Good style:
- Make the daily report reliable enough for another team to act on without double-checking the input.
- Invalid input should fail loudly; imperfect data inside valid files should never halt the run.
- Every input file in the directory must be considered, whatever its filename looks like.
- Each group should be summarized accurately, with correct counts and latest occurrences.

Bad style (do NOT do this — it enumerates the defects):
- The script currently ignores files whose names contain spaces; after your changes every file should be considered.
- The script currently stops on the first malformed record; after your changes it should continue and warn.

Do not include implementation-specific APIs, cmdlet names, exact code snippets, or step-by-step edits.

### Helpful Tips
Include 4-5 bullets max. Provide practical guidance without revealing specific implementations. Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".

Helpful Tips should guide discovery. They MUST NOT name the specific API, method, function, pattern, data structure, or exact command option that solves the task. It is acceptable to point candidates toward broad areas such as input validation, structured output, pipeline behavior, Linux path handling, or safe re-runs.

### How to Verify
Include 3-5 bullets max. Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write. Each bullet is a check the candidate can run or observe, such as test output, generated report content, warning behavior, idempotent re-run behavior, or absence of crashes on malformed input.

For this task, How to Verify may mention running the provided readiness/test script or invoking the Pester suite, but it must not include setup commands such as package installation instructions. Do not include database connection details, hostnames, ports, Docker commands, droplet IP placeholders, or external service references.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of the README. This is an instruction for generation, not a README heading:
- Setup commands such as apt commands, Install-Module commands, docker compose commands, npm install, pip install, mvn test, or similar.
- Direct solutions or architectural decisions.
- Step-by-step implementation guides.
- Specific APIs, method names, library names, pattern names, or data-structure names that reveal the solution.
- Code snippets that give away the answer.
- Directive phrases like "you should implement", "add this function", "create this class", "use <specific API>", or "call <specific cmdlet>".
- Windows-only guidance, registry references, Active Directory references, Task Scheduler references, WMI/CIM references, Windows service references, or drive-letter examples.
- Docker, database, cache, queue, broker, or external-service instructions.
- Database-connection details, client-tool suggestions, remote-host placeholders, or <DROPLET_IP> placeholders.

## REQUIRED OUTPUT JSON STRUCTURE
The downstream system reads these exact top-level keys. Do NOT rename them to synonyms such as "task_title", "files", or "context" — synonyms produce a hollow, unusable task.

Each field's value below is a one-sentence description of what to fill in. The final response must be valid JSON using exactly these keys.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that clearly reflects the PowerShell scripting task without using placeholders.",
  "title": "A human-readable display name in '<action verb> <subject>' format, 50-80 characters, different from name, describing the candidate's task.",
  "question": "The full candidate-facing task description including the selected business scenario, Current Implementation, Required Changes, Linux pwsh constraints, Pester verification expectations, and the expected time box.",
  "code_files": {{
    "README.md": "A concise candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify sections in that order, fully populated for the selected scenario.",
    ".gitignore": "A practical .gitignore for a local PowerShell Core scripting repository that excludes transient output while keeping all starter scripts, tests, run.sh, and fixtures tracked.",
    "run.sh": "A complete Ubuntu-compatible readiness script that installs pwsh and Pester 5 if missing, runs Invoke-Pester through pwsh, exits zero when tests execute even if assertions fail, and exits non-zero only for broken setup or undiscovered tests.",
    "scripts/<task-script>.ps1": "A complete runnable PowerShell Core starter script whose scenario-specific business logic is intentionally broken or incomplete while syntax, paths, and invocation remain valid.",
    "tests/<task-script>.Tests.ps1": "A complete Pester 5 test suite that runs on Linux with pwsh, exercises the required observable behavior, and exposes the starter script's intentional defects without relying on Windows-only surfaces or external services.",
    "data/<fixture-file>.csv or data/<fixture-file>.json": "Small deterministic fixture data required by the scenario, with enough valid and malformed or edge-case records to support the BASIC-level tests."
  }},
  "answer": "Evaluator-facing high-level solution approach explaining the intended fixes, the PowerShell concepts being assessed, and why the final behavior satisfies the scenario without exposing this text to the candidate.",
  "definitions": "An object of term-to-definition pairs explaining only task-relevant PowerShell or operational terms such as Pester, pipeline object, CSV record, JSON object, dry run, warning, or idempotent behavior.",
  "hints": "A single line nudging the candidate toward the relevant area of investigation without revealing the specific fix, exact cmdlets, or implementation steps.",
  "outcomes": "Expected results after completion in 2-3 lines focusing on measurable script behavior, passing Pester checks, safe handling of inputs, and correct structured output using simple English.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as PowerShell Core 7 familiarity, comfort running pwsh scripts on Linux, basic Pester awareness, and understanding of CSV or JSON processing; do not include setup, install, run, configure, or verification steps.",
  "short_overview": "A bullet list summarising the business problem, the PowerShell scripting focus, and the expected observable outcome after the candidate completes the task."
}}

## CRITICAL REMINDERS
1. Output JSON uses the CANONICAL key names above — this is non-negotiable.
2. Include both "name" and "title"; the title must be human-readable and different from the kebab-case name.
3. The task is NON-INFRA: do not include Docker, docker-compose.yml, Dockerfile, init_database.sql, databases, caches, queues, brokers, or external services.
4. The task must run with PowerShell Core pwsh 7+ on Ubuntu only.
5. Absolutely no Windows-only surfaces: no registry, no Active Directory, no Task Scheduler, no WMI/CIM, no Windows services, no Windows drive letters, and no Windows-only path assumptions.
6. Include plain .ps1 scripts plus a Pester 5 test file.
7. Include run.sh, and make it install PowerShell and Pester if missing before invoking Pester through pwsh.
8. run.sh is a deployability probe: it exits 0 when Pester tests are discovered and executed, even if assertions fail on the intentionally broken starter.
9. Starter code is runnable but does NOT contain the core solution.
10. Starter code perfectly matches the "Current Implementation" described to the candidate.
11. No solution-revealing comments, TODO comments, or hidden implementation hints.
12. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, with no additional README sections.
13. Completable within {minutes_range} minutes by a BASIC candidate.
14. **FILE LOCATION**: All code and scripts must reference /root/task as the base directory.
"""

PROMPT_REGISTRY = {
    "PowerShell (BASIC)": [
        PROMPT_POWERSHELL_BASIC_CONTEXT,
        PROMPT_POWERSHELL_BASIC_INPUT_AND_ASK,
        PROMPT_POWERSHELL_BASIC_INSTRUCTIONS,
    ]
}