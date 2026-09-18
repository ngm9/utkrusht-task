# Set by the prompt-generator shape classifier — do not edit.
# Consumed by infra.utils for the E2B-gate skip decision.
TASK_SHAPE = "infra"


PROMPT_SPARK_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SPARK_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an Apache Spark assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

OPTIONAL QUESTION CALIBRATION:
{question_prompt}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic Spark data engineering challenges that would be encountered in the role described in the role context.
- **CRITICAL**: This task MUST be delivered through docker-compose using a pre-built Spark image that already contains PySpark. Do NOT generate a bare host Python task that installs PySpark through pip.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, Spark data pipeline context, and production problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Spark performance, partitioning, shuffle, join, write-path, or reliability issue the candidate must diagnose and fix, the expected deliverables, and how it aligns with INTERMEDIATE Spark proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SPARK_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect super experienced in Apache Spark and PySpark data engineering, you are given a list of real world scenarios and proficiency levels for Spark.
Your job is to generate an entire task definition, including Spark job code, docker-compose delivery, fixture data, validation scripts, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to diagnose, optimize, and operate a production-like Spark workload.
The candidate's responsibility is to identify Spark execution issues and fix them in the job code or Spark configuration without being handed the solution. You must be careful about not giving away the solution or even hinting at it in your task definitions.

## CONTEXT & CANDIDATE EXPECTATION
The candidate will receive a FULLY FUNCTIONAL Spark project delivered through Docker Compose. The repository includes:
- A pre-built Spark container image with PySpark already installed inside the container
- A realistic PySpark ETL or ELT job with existing modular code, configuration, fixture data, and validation scripts
- FULLY POPULATED sample input data that reproduces observable correctness and performance symptoms at sandbox scale
- Deliberately suboptimal Spark logic involving intermediate-level concepts such as partition pruning, projection, shuffle cost, join strategy, output partitioning, idempotent writes, caching, checkpointing, or structured streaming trigger behavior
- A runnable environment where Spark commands execute inside the container, never through a host-level PySpark installation
- A visible validation suite or verification script that helps candidates confirm their changes after they diagnose and repair the workload

The candidate is expected to read the Spark code and observations, reason about driver/executor behavior, inspect explain plans or execution metrics, and make changes across multiple files in a realistic project layout. This is an INTERMEDIATE assessment for a candidate with approximately 3-5 years of Spark experience, so the repository must be substantial and realistic rather than a single toy script.

## INSTRUCTIONS

### Nature of the Task
- Task name MUST be within 50 words and clearly describe the intermediate-level Spark optimization or reliability scenario.
- The task must ask the candidate to fix an existing Spark data pipeline, not build Spark infrastructure from scratch.
- **CRITICAL**: This is an INFRA-shaped Spark delivery task. The generated task MUST include docker-compose.yml and run.sh, and MUST NOT include kill.sh.
- **CRITICAL**: PySpark MUST run inside a pre-built Spark Docker image such as `apache/spark:3.5.1-scala2.12-java11-python3-ubuntu` or another pullable Spark image that already contains `spark-submit` and PySpark. Do NOT put `pyspark` in requirements.txt and do NOT run `pip install pyspark` in run.sh.
- **CRITICAL**: The sandbox host only orchestrates Docker and may run thin helper scripts that do not import PySpark. All Spark jobs, Spark validation scripts, and PySpark imports must execute inside the Spark container through `docker compose exec` or `spark-submit`.
- **CRITICAL**: The Spark project should be FULLY FUNCTIONAL and executable on first checkout, but the job should have realistic Spark defects or inefficiencies that require intermediate-level diagnosis.
- **CRITICAL**: The generated starter codebase must be substantial and realistic for INTERMEDIATE level: require multiple interacting modules and files in a real project layout, non-trivial existing logic the candidate must read, and a solution that reasonably spans more than one file.
- **CRITICAL**: The defects must exercise genuine Spark competency, not Docker plumbing. Docker Compose is only the delivery mechanism to avoid disk-exhausting host-level PySpark installation.
- **CRITICAL — docker-compose YAML syntax**: if `entrypoint:` is overridden as a LIST (exec form, e.g. `["/bin/bash", "-lc"]`), `command:` MUST ALSO be a LIST with exactly one element containing the full shell script string (e.g. `command: ["mkdir -p /tmp/spark-local && tail -f /dev/null"]`). NEVER pair a list `entrypoint:` with a STRING `command:` — Compose shell-splits the string into separate tokens before appending them to entrypoint, so only the first word reaches `bash -c` as the script and everything else (flags, paths, `&&`, the rest of the pipeline) becomes bash's positional parameters and is silently dropped, producing a broken command like `mkdir: missing operand`. Simplest safe pattern: omit `entrypoint:` entirely and put the whole invocation as a LIST in `command:` (e.g. `command: ["/bin/bash", "-lc", "mkdir -p /tmp/spark-local && tail -f /dev/null"]`).
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the selected scenario.
- Generate a complete Spark workload with intentionally suboptimal logic suitable for intermediate-level engineers, such as:
  - Reading partitioned input without effective partition pruning
  - Carrying unnecessary columns through wide transformations
  - Choosing a shuffle-heavy join when small side data could be handled more efficiently
  - Using driver-side collection patterns where distributed processing is required
  - Ending a large write path with a single-output-file bottleneck
  - Producing non-idempotent output for reruns or backfills
  - Recomputing expensive intermediate DataFrames without appropriate persistence strategy
  - Misusing repartition and coalesce in ways that create skew or unnecessary shuffle
  - Failing to preserve schema evolution or data quality expectations in an incremental pipeline
  - Using structured streaming trigger, checkpoint, watermark, or state behavior that is operationally unsafe at an intermediate level
- Select a coherent subset of Spark issues that can be completed within {minutes_range} minutes; do not overload the task with every possible Spark topic.
- The question must NOT include hints about the specific fixes. Hints belong only in the dedicated `hints` field.
- Starter code may contain comments explaining business meaning, inputs, outputs, and observability, but MUST NOT contain comments that reveal the direct optimization solution.
- Ensure that all questions and scenarios adhere to current Spark 3.5-style best practices and PySpark DataFrame practices.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, Apache Spark documentation, PySpark documentation, and AI-powered tools, agentic IDEs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively analyze, diagnose, and optimize Spark workloads at an intermediate level, rather than testing rote memorization.
- Therefore, the complexity of the Spark task should require genuine understanding of Spark execution plans, stages, shuffles, partitions, joins, and operational tradeoffs that go beyond simple copy-pasting from a generative AI.
- Candidates may use AI to help interpret plans or reason about refactors, but the task must still require them to connect symptoms to code and validate the workload behavior.

## Code Generation Instructions
Based on the real-world scenarios provided above, create a Spark task that:
- Draws inspiration from one selected scenario to determine the business context, data domain, workload shape, and specific Spark symptoms.
- Matches INTERMEDIATE Spark proficiency for a candidate with approximately 3-5 years of production data engineering experience.
- Tests practical Spark skills involving DataFrame transformations, partitioning, join strategy, shuffle reduction, explain plan interpretation, write-path design, idempotency, or micro-batch reliability.
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- **CRITICAL**: The Spark codebase should be COMPLETE and FULLY FUNCTIONAL, but intentionally slow, wasteful, non-idempotent, or operationally unsafe in ways aligned with the selected scenario.
- Use a realistic repository structure with multiple files, for example Spark job modules, schemas, IO helpers, quality checks, fixture generators, validation scripts, and configuration files.
- Use repository-relative paths everywhere in generated scripts and documentation. Do NOT hardcode `/root/task` in run.sh, validation scripts, Spark code, README.md, or verification commands.
- Include deterministic fixture data small enough for the sandbox but shaped to expose the same Spark behavior as the production incident, such as skewed keys, partitioned dates, small dimension tables, late events, or repeated reruns.
- Include a visible verification script or invariant suite that can be executed inside the Spark container after candidate changes. The visible checks should validate observable output behavior and core performance indicators without giving away exact implementation choices.
- Do NOT require network access, cloud credentials, managed Spark services, Hive Metastore, Glue, Delta services, Kafka, or external object storage unless the selected scenario truly needs them and the docker-compose stack includes a working local substitute.
- Do NOT include FastAPI, Flask, Django, SQLAlchemy, or unrelated Python application framework code. The assessment is Spark-focused.

## Infrastructure Requirements
- MUST include docker-compose.yml using a pre-built Spark image that already contains PySpark and `spark-submit`.
- MUST include run.sh for automated environment readiness and smoke validation.
- MUST NOT include kill.sh; E2B sandboxes are destroyed as a whole when the session ends.
- MUST NOT include init_database.sql unless a selected scenario explicitly uses a relational database service; prefer Spark fixture files for this competency.
- run.sh is a readiness and deployability probe, NOT the grader. It brings the Spark container up, waits for readiness, verifies Spark can run a tiny job or import PySpark inside the container, validates fixture files exist, and confirms the starter project can load. It MUST exit 0 on the unsolved starter when the environment is deployable.
- If a visible candidate validation suite is included and is expected to fail before the candidate fixes the Spark job, run.sh MUST NOT run that suite as a pass/fail gate.
- The host runtime must never install PySpark. If the generated task contains a requirements.txt for thin helper scripts, it must exclude pyspark and any package that would transitively install PySpark.
- run.sh's first dependency step must install only the task's own lightweight host-side dependencies if such dependencies exist, using the runtime's native install command; otherwise it should explicitly skip host Python dependency installation with a log message explaining Spark dependencies live in the container.

### Docker-compose Instructions
- Generate a docker-compose.yml with a Spark service using a pullable pre-built Spark image that includes Python support and PySpark, such as `apache/spark:3.5.1-scala2.12-java11-python3-ubuntu`.
- **MUST NOT include any version specification** at the top of docker-compose.yml.
- The Spark service should stay alive for interactive `docker compose exec` and `spark-submit` commands, for example by running a long-lived shell command.
- Mount the repository into the Spark container using a repository-relative bind mount, not an absolute `/root/task` path.
- Set the container working directory to the mounted repository directory.
- If any service exposes ports to the host, **SECURITY-CRITICAL**: ports MUST be bound to localhost only using `127.0.0.1:<port>:<port>`.
- Do NOT use `.env` files or host-variable interpolation syntax for required container configuration. Use explicit inline service configuration where needed.
- Do NOT include PostgreSQL, MySQL, MongoDB, Redis, RabbitMQ, Qdrant, MinIO, or any other backing service unless the selected scenario truly needs that service for the Spark workload.
- If MinIO or another backing service is included because the selected scenario requires object storage behavior, configure it fully in docker-compose.yml with inline environment values, localhost-only port bindings, healthchecks, and matching paths used by the Spark job.
- Ensure `docker compose up -d` is sufficient to make the Spark execution environment available.
- Do NOT include a custom Dockerfile unless the selected task absolutely requires an app container; prefer the pre-built Spark image and mounted repository code.

### Spark Fixture Data Instructions
- Include fixture data files under a repository-relative data directory, using CSV, JSON, or Parquet-compatible input as appropriate for the scenario.
- Fixture data must be FULLY POPULATED and realistic enough to reproduce the Spark symptom at sandbox scale.
- Prefer date-partitioned fixture layouts, skewed join keys, small dimension tables, CDC-style incremental records, or late-arriving records when they fit the selected scenario.
- Include schema definitions or schema-loading code where appropriate so the task can assess schema handling and avoid relying only on inference.
- If expected output snapshots or golden datasets are included, they must validate business correctness without revealing the Spark optimization mechanism.
- Do NOT include optimized output data that gives away the answer.
- Do NOT include comments in fixture files or fixture-generation scripts that directly name the required fix.

### Run.sh Instructions
- PRIMARY RESPONSIBILITY: Starts Docker containers using `docker compose up -d`.
- PRE-PULL RESPONSIBILITY: Pre-pulls the Spark image and any backing service images before starting the stack to make failures explicit and avoid delayed image resolution.
- DEPENDENCY SAFETY: run.sh MUST NOT run `pip install pyspark`, MUST NOT list `pyspark` for host installation, and MUST NOT execute any host command that builds PySpark from source.
- HOST DEPENDENCIES: If a lightweight host requirements.txt exists, install it before Docker startup and ensure it excludes PySpark; otherwise log that no host Python dependency installation is required.
- WAIT MECHANISM: Implements a bounded readiness loop that waits for the Spark container to be running and capable of executing a tiny PySpark command inside the container.
- VALIDATION: Uses `docker compose exec` or `docker compose run` to verify `spark-submit` or a small PySpark import works inside the Spark container.
- PROJECT SMOKE: Verifies the starter Spark modules can be imported or the main job can display usage/help without running the candidate-facing failing validation suite.
- ERROR HANDLING: Includes proper error handling for failed container starts, missing fixture data, missing mounted files, or Spark command failures.
- PATH SAFETY: Uses repo-root-relative paths derived from the run.sh location, never hardcoded `/root/task`.
- GRADER SAFETY: Does not run the full grader or invariant suite when those checks are designed to fail until the candidate completes the task.

The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - docker-compose.yml (Spark service using a pre-built image with PySpark already installed)
  - run.sh (Readiness script that pre-pulls images, starts docker-compose, and smoke-tests Spark inside the container)
  - .gitignore (Ignore Python cache, Spark output, local data products, logs, and editor files)
  - requirements.txt (Optional lightweight host helper dependencies only; MUST NOT include pyspark)
  - pyproject.toml or setup.cfg (Optional project metadata for local linting or packaging that does not require PySpark on the host)
  - src/spark_task package files (Modular PySpark job code with intentional intermediate-level Spark issues)
  - config files (Scenario-specific job configuration using repository-relative paths)
  - data fixture files or fixture-generation scripts (Deterministic sandbox-scale input data)
  - scripts or invariants (Candidate-visible verification scripts executed inside the Spark container)
  - tests or validation files as needed (Do not require host-level PySpark installation)

## Code file requirements
- All generated Python code must be valid and formatted consistently with PEP8-style conventions.
- PySpark imports are allowed only in files intended to run inside the Spark container.
- requirements.txt MUST NOT include `pyspark` and run.sh MUST NOT execute `pip install pyspark`.
- The generated Spark project must include multiple realistic modules; do not ship only one short script.
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core optimization solution.
- Starter code should run and produce observable symptoms, but it should remain intentionally suboptimal or logically flawed according to the selected Spark scenario.
- If the task asks candidates to optimize a batch job, include a main job entry point, transformation modules, IO helpers, schema definitions, and validation or metric reporting.
- If the task asks candidates to improve a streaming workload, include a bounded local micro-batch fixture or file-stream simulation that can run in the Spark container without external cloud services.
- Include explain-plan or metric-capture utilities only if they do not directly reveal the required fix.
- DO NOT include any comments that give away hints or solutions, such as comments naming the exact join strategy, partitioning change, cache point, checkpoint policy, or write mode the candidate should use.
- DO NOT include syntactic errors. Defects should be logical, performance, reliability, or Spark execution issues.
- Use repository-relative paths in all code and scripts.

## .gitignore INSTRUCTIONS
Generate a comprehensive .gitignore file suitable for Spark and Python data engineering tasks that includes:
- Python cache directories and bytecode files
- Virtual environments and local tool caches
- Spark local directories and warehouse directories
- Spark event logs and runtime logs
- Generated output data, checkpoint directories, and temporary shuffle-style local artifacts
- Test and coverage artifacts
- IDE and editor files
- OS-specific files such as .DS_Store and Thumbs.db
- Do NOT ignore the deterministic input fixtures, configuration files, README.md, docker-compose.yml, run.sh, or validation scripts needed for the assessment

## README.md INSTRUCTIONS
The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.
Do NOT directly tell candidates what to implement — provide direction and guidance to help them discover solutions.

The README.md must contain EXACTLY the following sections, in this order:
1. Task Overview
2. Objectives
3. Helpful Tips
4. How to Verify

Each section MUST be emitted as an actual markdown heading using the same heading level, for example `## Task Overview`, `## Objectives`, `## Helpful Tips`, and `## How to Verify`. A plain unmarked text line with the section name is INVALID and counts as a missing section.

### Task Overview
- Must contain 3-4 meaningful sentences. No bullet list.
- Describes the business scenario, the current data pipeline state, and why the Spark problem matters operationally.
- Must be specific to the selected real-world scenario.
- Explain observable symptoms such as slow backfills, excessive shuffle, unreliable reruns, late data, skewed processing, or costly output behavior without naming the exact fix.
- NEVER empty. NO bold time-budget callouts.

### Objectives
- INTERMEDIATE objectives MUST be concise and OPEN-ENDED.
- Use 3-4 bullets maximum; fewer, tighter bullets are better.
- Each objective states ONE desired outcome as a full, natural sentence written from a stakeholder's point of view.
- Each objective should be roughly 10-24 words.
- Describe the what and why, NEVER the how.
- Do NOT name the API, library, framework, pattern, algorithm, config knob, file, file path, directory, function, method, class, variable, table, or any other direct code reference.
- Do NOT describe the current broken behavior or use phrasing like "currently does X" or "after your changes".
- State the desired end-state as a standing requirement, not a before/after diff.
- Good objective style: "Operations should be able to rerun a daily backfill without corrupting previously published results."
- Good objective style: "Downstream analysts should receive curated data quickly enough to meet the morning reporting window."
- Bad objective style: "Add a broadcast join to the hub lookup before writing the output."
- Bad objective style: "Fix the repartition call in the parcel ETA job."

### Helpful Tips
- 4-5 bullets maximum.
- Provide practical guidance without revealing specific implementations.
- Each bullet starts with an action word: "Consider", "Think about", "Explore", "Review", or "Analyze".
- Tips guide discovery and MUST NOT name the specific API, library, function, pattern, data structure, or algorithm that solves the task.
- Tips may orient candidates toward comparing inputs, outputs, execution observations, and rerun behavior, but must not reveal the direct Spark fix.

### How to Verify
- 3-5 bullets maximum.
- Frame verification in terms of observable outcomes. Describe WHAT to verify and the expected behavior, not the specific implementation to write.
- Each bullet is a check the candidate can run or observe, such as output correctness, rerun idempotency, explain-plan indicators at a high level, reduced runtime at sandbox scale, stable partitioned output, or validation script results.
- Verification commands, if included, must use repository-relative paths and must not hardcode `/root/task`.
- Do not include setup commands such as dependency installation or `docker compose up` as README instructions.
- Do not tell candidates to run run.sh; the environment is automated.

## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a section)
Keep the following OUT of README.md:
- Setup commands such as `pip install`, `docker compose up`, `spark-submit` for environment startup, or package installation steps
- Direct solutions or architectural decisions
- Step-by-step implementation guides
- Specific APIs, method names, library names, pattern names, config names, or data-structure names that reveal the solution
- Code snippets that give away the answer
- File paths, function names, or variable names that identify exactly where to change the code
- Directive phrases like "you should implement", "add this join strategy", "create this helper", or "use a specific Spark API"
- Host-level PySpark installation instructions
- Database connection details, remote-host placeholders, droplet IP placeholders, or client-tool connection guidance

## REQUIRED OUTPUT JSON STRUCTURE
The generated response must be valid JSON only and must follow this exact structure. Each field's value must be fully populated and candidate-safe.

{{
  "name": "A kebab-case GitHub repository name under 50 characters that reflects the selected Spark scenario without using spaces or punctuation other than hyphens.",
  "title": "A human-readable display title in '<action verb> <subject>' format, 50-80 characters, different from the repository name and specific to the selected Spark workload problem.",
  "question": "A complete candidate-facing task description explaining the business scenario, the observable Spark workload symptoms, and the outcomes the candidate must achieve without revealing file names, paths, functions, methods, variables, exact APIs, or the specific optimization mechanism.",
  "code_files": {{
    "README.md": "Candidate-facing README containing exactly Task Overview, Objectives, Helpful Tips, and How to Verify in that order, each written as a markdown heading (`## Task Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify`) — a plain unmarked text line with the section name is INVALID and counts as a missing section.",
    ".gitignore": "Comprehensive Spark and Python gitignore that excludes generated outputs, checkpoints, caches, logs, virtual environments, local Spark runtime artifacts, editor files, and OS-specific files while keeping all assessment fixtures tracked.",
    "docker-compose.yml": "Docker Compose configuration with no top-level version field, using a pre-built Spark image that already contains PySpark and spark-submit, repository-relative mounts, localhost-only port bindings if any ports are exposed, and no host-variable interpolation or .env dependency.",
    "run.sh": "Repository-relative readiness script that optionally installs only lightweight host helper dependencies, pre-pulls the Spark image, starts docker-compose, waits for the Spark container, verifies PySpark inside the container, and exits successfully on the unsolved deployable starter without running failing grader checks.",
    "requirements.txt": "Optional lightweight host-side dependency list for helper scripts only, explicitly excluding pyspark and any dependency that would install PySpark on the sandbox host.",
    "pyproject.toml": "Optional Python project metadata for packaging, linting, or helper tooling that does not require host-level PySpark installation.",
    "src/spark_task/__init__.py": "Package marker for the Spark task modules.",
    "src/spark_task/main.py": "Spark job entry point that runs inside the Spark container and wires together configuration, reads, transformations, quality checks, and writes while preserving the intentional intermediate-level defects.",
    "src/spark_task/config.py": "Scenario-specific configuration helpers using repository-relative paths and safe defaults for local container execution.",
    "src/spark_task/schemas.py": "Input and output schema definitions or schema utilities appropriate to the scenario without revealing optimization fixes.",
    "src/spark_task/io.py": "Spark read and write helpers containing realistic but intentionally suboptimal behavior where appropriate for the selected scenario.",
    "src/spark_task/transforms.py": "Core DataFrame transformation logic with realistic business rules and intentional Spark performance or reliability issues that the candidate must diagnose.",
    "src/spark_task/quality.py": "Data quality or reconciliation checks that validate business correctness without giving away the implementation approach.",
    "config/job_config.yaml": "Scenario configuration file with input locations, output locations, run dates, and sandbox-scale settings expressed as repository-relative paths.",
    "data/input_files": "Deterministic, fully populated input fixture files shaped to reproduce the selected Spark symptom at sandbox scale, such as partitioned events, skewed keys, dimension records, CDC updates, or late-arriving records.",
    "scripts/generate_fixtures.py": "Optional thin host-safe fixture generation script that uses only standard Python or lightweight dependencies and never imports PySpark.",
    "scripts/run_job_in_container.sh": "Optional repository-relative helper that invokes spark-submit inside the running Spark container without installing PySpark on the host.",
    "invariants/check_outputs.py": "Candidate-visible validation script or invariant suite intended to run inside the Spark container and verify observable correctness, rerun safety, and high-level performance indicators after the candidate's changes.",
    "additional_files_as_needed": "Any other minimal files needed for a realistic Spark project, while keeping the starter unsolved and avoiding unrelated frameworks or host-level Spark installation."
  }},
  "answer": "Evaluator-facing high-level solution approach describing the seeded Spark defects, their observable symptoms, the intended categories of repair, and the operational reasoning without needing to be candidate-safe.",
  "definitions": "An object of concise term-to-definition pairs for concepts relevant to the task, such as partition pruning, shuffle, stage, task, executor, broadcast exchange, skew, idempotent write, checkpoint, watermark, or adaptive execution.",
  "hints": "A single-line candidate-safe hint nudging investigation toward comparing Spark execution observations with the business outcome, without naming the exact API, join strategy, partitioning change, or file to edit.",
  "outcomes": "Two to three concise lines describing measurable expected results after completion, such as correct curated output, faster sandbox-scale execution, reduced shuffle or skew symptoms, safe reruns, and trustworthy downstream data.",
  "pre_requisites": "A bullet list of assumed prior knowledge only, using declarative capability phrases such as Spark DataFrame proficiency, comfort reading explain plans, understanding of partitions and shuffles, and basic Docker Compose familiarity.",
  "short_overview": "A bullet list summarizing the business problem, the Spark technical focus, and the expected operational outcome in simple English."
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only when this prompt is later used to generate a task.
2. The generated task must align with INTERMEDIATE Spark proficiency and remain within the Spark competency scope.
3. INFRA shape is mandatory: include docker-compose.yml and run.sh.
4. Do NOT include kill.sh.
5. Do NOT include init_database.sql unless the selected Spark scenario explicitly requires a relational database service; Spark fixture files are preferred.
6. PySpark MUST run inside the Docker Compose Spark container, not on the sandbox host.
7. Do NOT put `pyspark` in requirements.txt and do NOT run `pip install pyspark` in run.sh or any host script.
8. Use a pullable pre-built Spark image that already contains PySpark and spark-submit.
9. run.sh must pre-pull the Spark image and any backing service images before starting the stack.
10. run.sh is a readiness probe and must exit 0 on a deployable unsolved starter; it must not run a grader suite that is designed to fail before the candidate fixes the task.
11. Use repository-relative paths everywhere in generated scripts, code, verification helpers, and README content; never hardcode `/root/task`.
12. The defects must exercise genuine Spark competency such as partitioning, shuffle behavior, joins, caching, write idempotency, checkpointing, or structured streaming semantics, not Docker plumbing.
13. The starter codebase must be substantial and realistic, with multiple interacting modules and changes that reasonably span more than one file.
14. The candidate-facing question must not leak file names, paths, functions, methods, variables, exact APIs, or direct solution statements.
15. README.md must contain exactly Task Overview, Objectives, Helpful Tips, and How to Verify, in that order, each as a markdown heading.
16. INTERMEDIATE README objectives must be open-ended, stakeholder-framed, and must describe outcomes rather than implementation mechanisms.
17. The `pre_requisites` field must contain assumed prior knowledge only, not imperative setup or verification steps.
18. The `title` must be different from the `name` and use plain English in the requested action-verb format.
19. Every third-party host-side import anywhere in helper scripts must be listed in requirements.txt, and requirements.txt must still exclude PySpark.
20. The task must be completable within {minutes_range} minutes and must reflect the selected real-world scenario closely.
"""

PROMPT_REGISTRY = {
    "Spark (INTERMEDIATE)": [
        PROMPT_SPARK_INTERMEDIATE_CONTEXT,
        PROMPT_SPARK_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_SPARK_INTERMEDIATE_INSTRUCTIONS,
    ]
}