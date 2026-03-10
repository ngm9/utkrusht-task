PROMPT_SHELL_SCRIPT_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}
A DevOps or backend engineer with 1–2 years of experience in Shell scripting is expected to write simple automation scripts to streamline basic system and deployment tasks. Their primary responsibility includes creating scripts to manage files, automate backups, perform log rotations, schedule jobs using cron, or monitor resource usage. They should understand shell fundamentals, including variables, loops, conditionals, functions, and file permissions. The engineer should also be able to write clean, reusable, and well-documented scripts that work reliably in Linux or Unix environments. While they may not be required to write complex production-grade automation, they should know how to test, debug, and safely execute their scripts in real-world scenarios.

Based on this information, could you summarize what you understand about the company and role requirements?
Keep your summary focused, and remember that any generated task name must stay concise—no more than 50 words.
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
   "name": "Task Name (within 50 words) reflecting the scenario context and focusing on basic shell scripting",
   "question": "A short description of the task scenario including the specific ask from the candidate — what needs to be fixed/implemented?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper shell script, log files, and temporary file exclusions",
      "scripts/.gitkeep": "Placeholder for scripts directory",
      "data/sample_file.csv": "Sample dataset according to the scenario requirements",
      "logs/.gitkeep": "Placeholder for logs directory if needed",
      "starter_file_name": "starter_file_content",
      "starter_file_name_2": "starter_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion in 2-3 lines. Use simple english.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level operational or business problem, (2) the specific shell scripting implementation or fix goal, and (3) the expected outcome emphasizing correctness, reliability, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, environment, and knowledge required to complete the task. Mention things like Bash 4.0+, Unix/Linux system, basic command-line tools (grep, sed, awk, find), text editor, Git, understanding of file permissions, etc.",
  "answer": "High-level solution approach",
  "hints": "a single line hint on what a good approach to solve the task could include. These hints must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
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
- Every task name you produce must be concise and limited to 50 words or fewer, reflecting the core scenario clearly.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for shell script projects including log files (*.log), temporary files (*.tmp, .*.swp), backup files (*~, *.bak), OS-specific files (.DS_Store, Thumbs.db), generated output directories, and other common artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact operational scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete operational context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the operational scenario, current situation, and what problem needs to be solved. 
NEVER generate empty content - always provide substantial context that explains what the candidate is working on and why it matters in a real DevOps/SysAdmin environment.

### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how Unix command-line tools can be chained together to process data efficiently
  - Mention thinking about how to make scripts safe to run multiple times without causing issues
  - Hint at considering what happens when expected files or directories don't exist
  - Recommend exploring how to validate inputs before processing them
  - Suggest thinking about how to provide useful feedback during script execution
  - Point toward considering proper file permission management for security
  - Hint at exploring how exit codes communicate success or failure to the system
  - Recommend considering how to handle edge cases like empty inputs or special characters
  - Suggest analyzing how to make scripts maintainable with clear variable names and structure
  - Mention thinking about efficient text processing tools available in Unix/Linux
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Tips should guide discovery toward fundamental shell scripting concepts, not provide direct solutions or specific commands
  - Frame suggestions around learning and understanding rather than prescriptive instructions
  - Examples of proper framing:
    * "Consider how to check if a directory exists before attempting operations on it"
    * "Think about which Unix tools are best suited for processing structured text data"
    * "Explore how to make your script communicate what it's doing to anyone watching"
    * "Review how file permissions affect who can read, write, or execute files"
    * "Look into how command pipelines can transform data step by step"

### Objectives
  - Clear, measurable goals for the candidate appropriate for basic level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected script behavior, input/output requirements
  - Focus on fundamental shell scripting concepts and skills
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Create a script that organizes files based on specific criteria"
    * "Implement functionality that processes text data and produces cleaned output"
    * "Build a solution that handles errors gracefully and reports what went wrong"
    * "Design a script that can safely run multiple times without causing problems"
    * "Ensure the script validates its inputs before attempting to process them"
  - Objectives should be measurable but not prescribe specific bash commands or approaches
  - Should guide candidates to think about: functionality, data validation, error handling, idempotency
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and basic script quality checks
  - Frame verification in terms of observable outcomes and script behaviors
  - Examples of proper framing:
    * "Run the script with the provided test data and verify it produces the expected output"
    * "Test the script with missing files or directories and confirm it handles errors appropriately"
    * "Execute the script multiple times and verify it produces consistent, correct results"
    * "Check that generated files have the correct permissions and ownership"
    * "Test edge cases like empty input, special characters, or very large files"
    * "Verify the script exits with appropriate status codes for success and failure scenarios"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: functionality, error handling, idempotency, edge cases
  - **CRITICAL**: Describe what behaviors to verify, not the specific commands or logic to check

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (chmod +x script.sh, ./script.sh, etc.)
  - Direct solutions or hints
  - Step-by-step implementation guides
  - Specific bash commands or implementation approaches (e.g., "use find command", "create a for loop with")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific command syntax or pipeline details that would give away the solution to the task
  - Should not provide any particular tool or approach to implement the solution
  - Script names or specific command patterns that would reveal the solution
  - Phrases like "you should write", "make sure to use", "create a function called X"
  - Specific Unix tool recommendations that would reveal the solution approach
  - Directory structure details that would dictate the implementation approach

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, within 50 words
3. **code_files** must include README.md, .gitignore, and relevant starter scripts/data files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter files** must be realistic but must NOT contain the solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Shell/Bash terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **NO comments in scripts** that reveal the solution or give hints
10. **Use Bash 4.0+** best practices throughout
  """
PROMPT_REGISTRY = {
    "Shell (BASIC)": [
        PROMPT_SHELL_SCRIPT_BASIC_CONTEXT,
        PROMPT_SHELL_SCRIPT_BASIC_INPUT_AND_ASK,
        PROMPT_SHELL_SCRIPT_BASIC,
    ]
}
