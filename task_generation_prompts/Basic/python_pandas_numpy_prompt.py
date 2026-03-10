PROMPT_PANDAS_NUMPY_CONTEXT_BASIC = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""
PROMPT_PANDAS_NUMPY_INPUT_AND_ASK_BASIC = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Pandas/NumPy assessment task.

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

1. What will the task be about? (Describe the business domain, data context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of data manipulation/analysis required, the expected deliverables, and how it aligns with the proficiency level)


Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_PANDAS_NUMPY_BASIC = """
## GOAL
As a senior data analyst super experienced in Python data manipulation libraries (Pandas, NumPy, data cleaning, data transformation), you are given a list of real world scenarios and proficiency levels for Python data analysis development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch or fix bugs in the existing code.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors
- The question should be a real-world scenario and not a trick question that is syntactic errors.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (1-2 years Pandas/NumPy experience), ensuring that no two questions generated are similar. 
- For BASIC level of proficiency, the questions must be more specific and less open ended. The scenarios must also be easily digestible and focus on fundamental Pandas/NumPy concepts like:
  - DataFrame creation and basic operations
  - Data loading from CSV/Excel files
  - Basic data cleaning (handling missing values, duplicates)
  - Data filtering and selection
  - Basic aggregations and groupby operations
  - Simple data transformations
  - Basic statistical calculations
  - Data type conversions
  - Merging and joining datasets
  - Basic data visualization preparation
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern Python best practices (Python 3.8+) and current Pandas/NumPy standards (Pandas 1.3+, NumPy 1.20+).
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

## AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Pandas/NumPy proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.

## Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Pandas/NumPy task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (1-2 years Pandas/NumPy experience), keeping in mind that AI assistance is allowed.
- Tests practical data manipulation skills that require more than a simple AI query to solve, focusing on fundamental concepts
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single dataset analysis or simple data pipeline rather than complex multi-source data integration or advanced statistical modeling

## Starter Code Instructions:
- The starter code should only provide starting directions so that the candidate is not clueless to begin with.
- The code files generated must be valid and executable with `python main.py` or in Jupyter notebooks.
- Keep the code files minimal and to the point.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly and not just fix the errors, so make sure the starter code leaves room for the candidate to implement the solution the way they want.
- If the task is to fix bugs, make sure the starter code has a logical bug (no syntactic errors) that is substantial enough to test the basic proficiency level.
- If the task is to implement a feature from scratch, make sure the starter code only provides a good starting point.
- Python starter code should include basic project structure but NOT require complex infrastructure setup (advanced database connections, complex data pipelines, distributed computing, etc.)
- Focus on CSV/Excel file-based data with simple file I/O operations for simplicity

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task name in <verb><subject> format within 50 characters, e.g. 'analyze sales data with pandas'",
   "question": "A short description of the task scenario including the specific ask from the candidate — what needs to be fixed/implemented?",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Python, virtual environment, and IDE exclusions",
      "requirements.txt": "Python dependencies (pandas, numpy, etc.)",
      "main.py": "Main Python script entry point",
      "sample_data.csv": "Sample dataset in CSV format",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Bullet-point list of expected results after completion, using simple, non-technical language. Each bullet must describe ONE clear deliverable or requirement and be understandable to non-engineers (e.g. HR or recruiters). One bullet MUST explicitly state: 'Write production level clean code with best practices including proper naming conventions, error handling, efficient memory usage, and code documentation.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level problem in a business context, (2) the specific goal, and (3) the expected outcome emphasizing maintainability and scalability.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required to complete the task. Mention things like Python 3.8+, pandas, numpy, IDE, Git, basic data analysis knowledge, etc.",
  "answer": "High-level solution approach for solving the task in few lines",
  "hints": "a single line hint on what a good approach to solve the task could include. These hints must NOT give away the answer, but gently nudge the candidate in the right direction.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

 
## Code file requirements:
- More than 1 files can be generated but make sure they are included in the JSON structure correctly.
- Code should follow modern Python best practices and PEP 8 style guidelines
- Use proper function/variable naming conventions
- Follow Pythonic patterns and idioms
- Use appropriate pandas/numpy methods and avoid anti-patterns
- **CRITICAL**: The generated code files MUST NOT contain the implementation for the core logic of the task. They should only provide the necessary boilerplate, file structure, and minimal setup code.
- The core data manipulation logic, analysis functions, or transformation operations that the candidate needs to implement MUST be left empty or with minimal structure.
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add logic here" or "Should implement data cleaning" etc.
- DO NOT add comments that give away hints or solution or implementation details

- The generated project structure should be runnable, but the code requiring implementation will not function correctly until the candidate completes the task.

## .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for Python projects including __pycache__, .pyc files, virtual environments (venv, env), IDE configurations (.idea, .vscode), Jupyter notebook checkpoints, data output files, and other common development artifacts that should not be tracked in version control.

## README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Objectives
   - How to Verify
   - Helpful Tips 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario, current situation. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why it matters.

### Objectives
  - Clear, measurable goals for the candidate appropriate for basic level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected data outputs, analysis results
  - Focus on fundamental Pandas/NumPy concepts and skills
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Extract meaningful insights from the dataset based on specific criteria"
    * "Transform raw data into a clean format suitable for analysis"
    * "Calculate key metrics that answer business questions"
    * "Identify patterns or trends within the data"
    * "Handle data quality issues appropriately"
  - Objectives should be measurable but not prescribe specific pandas methods or functions
  - Should guide candidates to think about: data quality, analysis approach, meaningful outputs
  - **CRITICAL**: Objectives describe the "what" needs to work, never the "how" to implement it

### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and basic code quality checks
  - Frame verification in terms of observable outcomes and data outputs
  - Examples of proper framing:
    * "Run the script and verify the output matches expected results"
    * "Check that missing data is handled appropriately"
    * "Confirm calculated metrics are accurate and make business sense"
    * "Verify the transformed data has the correct structure and format"
    * "Test with different input data to ensure robustness"
    * "Check that the code executes without errors on the sample dataset"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: data accuracy, error handling, output correctness, edge cases
  - **CRITICAL**: Describe what behaviors to verify, not the specific code or methods to check
  
### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring how pandas DataFrames organize and represent tabular data
  - Mention thinking about which operations are needed to clean and prepare data
  - Hint at considering how to filter data based on specific conditions
  - Recommend exploring how to perform calculations across rows or columns
  - Suggest thinking about how to group data and calculate aggregates
  - Point toward considering what happens with missing or invalid data
  - Hint at exploring how to merge or combine different datasets
  - Recommend considering how data types affect operations and memory usage
  - Suggest analyzing patterns in the data before deciding on transformations
  - Mention thinking about vectorized operations for better performance
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Look into"
  - **CRITICAL**: Tips should guide discovery toward fundamental pandas/numpy concepts, not provide direct solutions or specific code
  - Frame suggestions around learning and understanding rather than prescriptive instructions
  - Examples of proper framing:
    * "Consider how to identify and handle data quality issues"
    * "Think about which aggregation approaches best answer the business question"
    * "Explore how to efficiently filter large datasets"
    * "Review how different data types can be transformed"
    * "Look into how pandas handles time-based data"

### NOT TO INCLUDE in README: Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (pip install, python main.py, etc.)
  - Direct solutions or hints
  - Step-by-step implementation guides
  - Specific pandas/numpy methods or implementation approaches (e.g., "use .groupby()", "create .apply() function")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific function implementation details that would give away the solution to the task
  - Should not provide any particular method or approach to implement the solution
  - Function names or specific method usage patterns that would reveal the solution
  - Phrases like "you should implement", "make sure to use", "create a function called X"
  - Specific pandas or numpy API recommendations that would reveal the solution approach
  - Code structure details that would dictate the implementation approach

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, maximum 50 characters
3. **code_files** must include README.md, .gitignore, requirements.txt, main.py, and sample data file
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Pandas/NumPy terms
8. **Task must be completable within the allocated time** for BASIC proficiency (1-2 years)
9. **NO comments in code** that reveal the solution or give hints
10. **Use Python 3.8+ and modern Pandas/NumPy best practices** throughout
  """
PROMPT_REGISTRY = {
    "Python - Numpy (BASIC), Python - Pandas (BASIC)": [
        PROMPT_PANDAS_NUMPY_CONTEXT_BASIC,
        PROMPT_PANDAS_NUMPY_INPUT_AND_ASK_BASIC,
        PROMPT_PANDAS_NUMPY_BASIC,
    ]
}
