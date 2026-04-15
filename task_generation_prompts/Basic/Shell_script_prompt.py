PROMPT_SHELL_SCRIPT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A DevOps or backend engineer with 1–2 years of experience in Shell scripting is expected to write simple automation scripts to streamline basic system and deployment tasks. Their primary responsibility includes creating scripts to manage files, automate backups, perform log rotations, schedule jobs using cron, or monitor resource usage. They should understand shell fundamentals, including variables, loops, conditionals, functions, and file permissions. The engineer should also be able to write clean, reusable, and well-documented scripts that work reliably in Linux or Unix environments. While they may not be required to write complex production-grade automation, they should know how to test, debug, and safely execute their scripts in real-world scenarios.

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_SHELL_SCRIPT_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Shell Scripting assessment task.

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

1. What will the task be about? (Describe the operational context, technical requirements, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of script to be implemented or fixed, the expected deliverables, and how it aligns with BASIC Shell Scripting proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_SHELL_SCRIPT_BASIC = """
## GOAL
As a senior DevOps engineer super experienced in shell scripting, Linux system administration, and automation (Bash, command-line tools, cron, log management, file processing), you are given a list of real world scenarios and proficiency levels for shell scripting.
Your job is to generate an entire task definition, including starter files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task
- Task must ask to implement a shell script from scratch or fix bugs in the existing script.
- The question scenario must be clear, ensuring that all facts, figures, directory names, file patterns, etc., are realistic and relevant to the context.
- Generate enough starter files/directories that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER FILES OR COMMENTS.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question with syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years shell scripting experience), ensuring that no two questions generated are similar.
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental shell scripting concepts like:
  - Basic bash syntax and control structures (if/else, loops, case statements)
  - File and directory operations (cp, mv, mkdir, rm, find)
  - Text processing with standard Unix tools (grep, sed, awk, sort, uniq, cut)
  - Basic error handling and exit codes
  - Command-line argument parsing
  - File permission management (chmod, chown)
  - Process management and command execution
  - Redirection and piping
  - Variables and command substitution
  - Cron job scheduling basics
  - Log file processing and rotation
  - CSV/text data manipulation
  - Idempotency and script safety
- The question must NOT include hints. The hints will be provided in the "hints" field.
- Ensure that all questions and scenarios adhere to modern bash best practices (Bash 4.0+) and POSIX compliance where applicable.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, man pages, bash documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs).
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic shell scripting proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Script Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a shell scripting task that:
- Draws inspiration from the input_scenarios given to determine the operational context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years shell scripting experience), keeping in mind that AI assistance is allowed.
- Tests practical shell scripting skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single-purpose automation scripts rather than complex orchestration or advanced system programming

## Starter Files Instructions:
- The starter files should only provide starting directions so that the candidate is not clueless to begin with.
- The files generated must be valid and realistic (proper directory structure, sample data files, broken scripts if debugging task).
- Ensure that any provided datasets (such as CSV or log samples) are complete, consistent, and accurately reflect the scenario requirements so candidates can validate their solutions.
- Keep the starter files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter files leave room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter script has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a script from scratch, make sure the starter files only provide sample data or directory structure.
- Shell script starter files should include realistic test data but NOT require complex infrastructure setup (no Docker, Kubernetes, cloud services, or advanced monitoring systems)
- Focus on standalone scripts that can be tested locally on any Unix/Linux system

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Describes what the candidate will do in plain English. Examples: 'Automate Log Rotation for Web Server Farm', 'Fix Backup Script for Database Export Pipeline', 'Build CSV Report Generator for Sales Data'. The title should clearly convey the action (automate, fix, build, implement, debug, optimize) and the subject (what system/feature/component). This is used for display purposes — 'name' is the kebab-case GitHub repo name, 'title' is the readable display name.",
  "question": "Short description of the scenario and specific ask from the candidate — what needs to be fixed or implemented",
  "code_files": {{
    "README.md": "Candidate-facing README following the README structure defined below",
    ".gitignore": "Proper shell script, log files, and temporary file exclusions",
    "scripts/.gitkeep": "Placeholder for scripts directory",
    "data/sample_file.csv": "Sample dataset according to the scenario requirements",
    "logs/.gitkeep": "Placeholder for logs directory if needed",
    "...": "All other starter files — sample data, broken scripts for debugging tasks, directory structure. Generate as many files as needed for a realistic project setup."
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper design patterns, naming conventions, exception handling, logging and observability.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level operational or business problem, (2) the specific shell scripting implementation or fix goal, and (3) the expected outcome emphasizing correctness, reliability, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, environment, and knowledge required to complete the task. Mention things like Bash 4.0+, Unix/Linux system, basic command-line tools (grep, sed, awk, find), text editor, Git, understanding of file permissions, etc.",
  "answer": "High-level solution approach describing main components and flow.",
  "hints": "Single line suggesting focus area. Example: 'Focus on chaining Unix text processing tools efficiently and handling edge cases like empty files or missing directories'",
  "definitions": {{
    "Shebang": "The #! line at the top of a script that tells the system which interpreter to use (e.g., #!/bin/bash)",
    "Exit Code": "A numeric value returned by a command or script to indicate success (0) or failure (non-zero) to the calling process",
    "Pipe": "The | operator that connects the stdout of one command to the stdin of another, enabling data processing chains",
    "Idempotency": "Property of a script where running it multiple times produces the same result as running it once, without unintended side effects",
    "Glob": "Shell pattern matching syntax using wildcards (*, ?, []) to match filenames and paths"
  }}
}}

## File requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Scripts should follow bash best practices and conventions
- Use proper shebang (#!/bin/bash) for all shell scripts
- Follow shell script naming conventions (lowercase with underscores, .sh extension)
- Use meaningful variable names with proper quoting
- **CRITICAL**: The generated starter files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary directory structure, sample data, and minimal setup.
- The core script logic, text processing pipelines, error handling, or business logic that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement validation" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be realistic, but the script requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for shell script projects including log files (*.log), temporary files (*.tmp, .*.swp), backup files (*~, *.bak), OS-specific files (.DS_Store, Thumbs.db), generated output directories, and other common artifacts that should not be tracked in version control.

## README.md STRUCTURE

**CRITICAL**: The README must be concise and open-ended. Each section should have only the essential points needed to understand the task. Do NOT overload with too many bullets — quality over quantity. The candidate should figure out the implementation approach on their own.

### Task Overview (MANDATORY - 3-4 substantial sentences)

**CRITICAL**: Describe the specific operational scenario and current state of the system/environment. Explain what the candidate is working on and why it matters. Use concrete business context; never leave empty or generic text. Do NOT directly tell candidates what to implement — provide direction so they can discover the solution.

### Objectives (3-5 bullets MAX)

Define goals focusing on outcomes for a BASIC-level Shell Scripting task:
  - Describe WHAT needs to work, not HOW to implement it
  - Frame objectives around observable outcomes and expected behavior
  - Do NOT specify exact implementation approaches, specific commands, or tool names
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it. Keep to 3-5 concise bullets only.

### How to Verify (3-5 bullets MAX)

Verification approaches for the task:
  - Describe what behaviors to verify and how to confirm success
  - Focus on observable outcomes (script output, file changes, exit codes)
  - Do NOT specify specific commands, pipelines, or implementation details to check
  - **CRITICAL**: Describe what behaviors to verify, not specific commands or logic to check. Keep to 3-5 concise bullets only.

### Helpful Tips (3-4 bullets MAX)

Practical guidance without revealing implementations:
  - Use bullet points starting with "Consider", "Think about", "Explore", "Review", "Look into"
  - Guide the candidate toward discovery — suggest areas to explore, not specific solutions
  - Do NOT specify exact commands, tool names, or pipeline patterns
  - **CRITICAL**: Guide discovery, never provide direct solutions. Keep to 3-4 concise bullets only.

### NOT TO INCLUDE IN README
- Step-by-step implementation instructions
- Exact code solutions or snippets
- Setup commands (chmod +x, ./script.sh, etc.)
- Specific bash commands or tool names that reveal the solution approach
- Phrases like "you should write", "make sure to use", "create a function called X"
- Excessive bullets or verbose explanations — keep each section lean and focused

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case (e.g., "log-rotation-automation", "csv-report-generator")
3. **code_files** must include README.md, .gitignore, and relevant starter scripts/data files
4. **README.md** must follow the structure above with Task Overview, Objectives, How to Verify, Helpful Tips (in that exact order)
5. **Starter files** must be realistic but must NOT contain the solution
6. **outcomes** must include one bullet on production-level clean code with best practices, design patterns, exception handling, logging
7. **short_overview**, **pre_requisites** must be bullet-point lists in simple language
8. **hints** must be a single line; **definitions** must include relevant Shell/Bash terms
9. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
10. **NO comments in scripts** that reveal the solution or give hints
11. **Use Bash 4.0+** best practices throughout
12. **"title"** must be in `<action verb> <subject>` format and different from `"name"` — name is kebab-case for GitHub repo, title is human-readable for display
"""
PROMPT_REGISTRY = {
    "Shell (BASIC)": [
        PROMPT_SHELL_SCRIPT_BASIC_CONTEXT,
        PROMPT_SHELL_SCRIPT_BASIC_INPUT_AND_ASK,
        PROMPT_SHELL_SCRIPT_BASIC,
    ]
}
