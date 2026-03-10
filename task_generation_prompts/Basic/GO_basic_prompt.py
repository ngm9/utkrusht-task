PROMPT_GOLANG_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Go (Golang) assessment task.

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

1. What will the task be about? (Describe the business domain, technical context, and problem the candidate will be solving)
2. What will the task look like? (Describe the type of implementation or fix required, the expected deliverables, and how it aligns with BASIC Go proficiency)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""


PROMPT_GO_BASIC_INSTRUCTIONS="""
## GOAL
As a technical architect super experienced in Go and modern Go ecosystem, you are given a list of real world scenarios and proficiency levels for Go development.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at a basic/beginner level.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a straightforward feature, complete partially implemented code, or fix simple bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement basic Go practices, demonstrate proper syntax usage, and fundamental problem-solving skills
- The question should be a real-world scenario that tests fundamental understanding and not just syntax memorization.
- The complexity of the task and specific ask expected from the candidate must align with BASIC proficiency level (0-2 years Go experience or beginner), ensuring that no two questions generated are similar. 
- For BASIC level of proficiency (1-2 years experience), the questions should test fundamental understanding and require candidates to demonstrate:
  - **Go Fundamentals**: Variables, data types, constants, operators, control flow (if/else, switch, for loops)
  - **Functions**: Function declaration, parameters, return values, multiple return values, basic error handling
  - **Data Structures**: Arrays, slices, maps, structs, and common operations
  - **Pointers**: Understanding pointer basics, pass by value vs reference, when to use pointers
  - **Error Handling**: Understanding error type, checking errors, returning errors, basic error wrapping
  - **Package Organization**: Understanding internal/ vs pkg/, proper package structure, import management
  - **Project Structure**: Familiarity with cmd/, internal/, pkg/ layout patterns
  - **Interfaces**: Basic interface usage, satisfying interfaces, type assertions
  - **String Manipulation**: Common string operations, formatting, basic parsing
  - **File I/O**: Reading and writing files using os and io packages, working with JSON/CSV
  - **Code Quality**: Proper naming conventions, code organization, gofmt compliance, basic documentation
  - **Standard Library**: Working knowledge of fmt, strings, strconv, time, os, io, encoding/json, net/http basics
  - **Basic Concurrency**: Understanding goroutines and channels at a fundamental level
  - **Dependency Management**: Understanding go.mod, go.sum, module imports
  - **HTTP Basics**: Simple HTTP servers/clients, request/response handling (if applicable)
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern Go best practices (Go 1.18+) but focus on fundamental concepts.
- Tasks should be straightforward and focus on solidifying basic Go knowledge.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, and apply basic solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect basic Go proficiency while requiring genuine problem-solving skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to understand and apply fundamental Go concepts.

### Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Go task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for BASIC proficiency level (0-2 years Go experience or beginner), keeping in mind that AI assistance is allowed.
- Tests practical Go skills that require fundamental understanding and basic problem-solving abilities
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on single-package or simple multi-file applications that demonstrate basic Go structure
- Should test the candidate's ability to write clean, functional Go code with proper fundamentals
- **CRITICAL**: any type of comments in the code files is strictly prohibited. The code files should not contain any comments at all.

### Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate proper Go project organization and fundamental skills
- The code files generated must be valid and executable with `go build ./cmd/...` or `go run ./cmd/main.go`.
- Provide a professional project structure appropriate for 1-2 years experience:
  - **cmd/**: Application entry point(s) with main package
  - **internal/**: Private packages organized by layer (models, service, handler, repository, validator)
  - **pkg/**: Exportable utility packages
  - **config/**: Configuration management
 - Include test files demonstrating table-driven test patterns
- A part of the task completion is to watch the candidate work with proper package structure, implement clean separation of concerns, and demonstrate fundamental problem-solving
- If the task is to fix bugs, make sure the starter code has simple logical bugs across different packages (no syntactic errors) that require basic-level thinking to resolve
- If the task is to implement a feature from scratch, provide a clear foundation with proper folder/package structure that candidates can follow and extend
- Go starter code should follow standard Go project layout (internal/, pkg/, cmd/ structure)
- Include clearly defined structs/interfaces across appropriate packages that the candidate needs to work with or complete
- Provide partial implementations with clear gaps distributed across packages that require basic Go knowledge to fill
- **CRITICAL**: comments in any of the code files are strictly prohibited. The code files should not contain any comments at all.


## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "Task Name",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/completed/fixed? Include clear functional requirements.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Go exclusions",
      "go.mod": "Go module definition with basic dependencies",
      "go.sum": "Go dependencies checksum (can be empty)",
      "cmd/main.go": "Main application entry point",
      "internal/models/models.go": "Data models and structs",
      "internal/service/service.go": "Core business logic and service functions",
      "internal/handler/handler.go": "Request handlers and processing logic",
      "internal/validator/validator.go": "Input validation logic",
      "internal/repository/repository.go": "Data access layer (if needed)",
      "pkg/utils/utils.go": "Exported utility functions",
      "pkg/errors/errors.go": "Custom error definitions (if needed)",
      "config/config.go": "Configuration structures and loading",
       "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion focusing on functionality and code correctness. 2-3 lines describing functional outcomes and basic code quality.",
  "short_overview": "Bullet-point list in simple language describing: (1) the high-level business or technical problem, (2) the specific implementation or fix goal, and (3) the expected outcome emphasizing correctness, structure, and maintainability.",
  "pre_requisites": "Bullet-point list of basic tools and environment setup required. Include basic Go knowledge expectations like understanding packages, modules, basic data structures, error handling, etc.",
  "answer": "Clear solution approach with step-by-step guidance on fundamental concepts to apply",
  "hints": "a single line hint focusing on the fundamental Go concept or approach that could be useful. These hints must NOT give away the answer, but guide towards basic Go thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

### Code file requirements:
- Generate realistic folder structure following Go project conventions:
-Code should follow Go best practices with proper package organization
- Use clear variable names and straightforward but well-structured logic
- Focus on fundamental Go features while demonstrating proper project organization
- Each package should have a clear, single responsibility
- **CRITICAL**: The generated code files should provide partial implementations that require basic completion
- Include clear function signatures and interfaces that need to be implemented
- Demonstrate proper Go project layout that 1-2 year experienced developers should be familiar with
- The core logic, algorithms, or implementations that the candidate needs to complete MUST be left for the candidate to implement
- DO NOT include any 'TODO' or placeholder comments
- **CRITICAL**:not include any comments in any file (comments should not be there at all)
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add your code here" or "Implement function X" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project should be compilable with `go build ./cmd/...`, but will require implementation to function properly
- Use standard library primarily, with common basic dependencies when appropriate (e.g., popular libraries for JSON, HTTP, testing)

### .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for basic Go projects including binary executables, IDE configurations (.idea/, .vscode/, .DS_Store), compiled binaries, coverage files (*.out, *.test), log files, and other common development artifacts that should not be tracked in version control.

### README.md INSTRUCTIONS:
 - The README.md contains the following sections:
   - Task Overview
   - Helpful Tips
   - Objectives
   - How to Verify 
- The README.md file content MUST be fully populated with meaningful, specific content
- Task Overview section MUST contain the exact business scenario from the task description
- ALL sections must have substantial content - no empty or placeholder text allowed
- Content must be directly relevant to the specific task scenario being generated
- Use concrete business context, not generic descriptions
- **IMPORTANT**: Do NOT directly tell candidates what to implement - provide direction and guidance to help them discover solutions

### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 2-3 meaningful sentences describing the business scenario, what needs to be built, and why this functionality is useful.
NEVER generate empty content - always provide substantial context that explains what the candidate is working on in simple, clear terms.

### Helpful Tips
Provide conceptual and discovery-focused guidance that helps learners reason about the problem **without revealing specific implementations**:
  - Encourage exploration of Go’s fundamental concepts rather than prescribing exact solutions
  - Avoid mentioning any direct implementation details such as goroutines, channels, or specific library functions
  - Suggest reviewing relevant Go documentation sections related to concurrency, timing, and data coordination
  - Mention thinking about what data types or structures could represent both inputs and their results
  - Hint at considering how multiple operations might be coordinated or synchronized conceptually
  - Recommend exploring how timing and delays could affect overall task performance
  - Suggest thinking about how to simulate slower or failed operations for more realistic testing
  - Remind learners to record or measure how long processes take, focusing on logic rather than tools
  - Encourage considering how to handle cases where some tasks take much longer or fail entirely
  - Recommend reflecting on how to clearly represent the status or outcome of each task
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Review", "Remember", "Check"
  - **CRITICAL**: Tips should guide exploration of Go fundamentals and reasoning, not provide direct implementation steps
  - Frame suggestions around Go concepts and outcomes rather than specific code constructs
  - Examples of proper framing:
    * "Think about how you might coordinate multiple tasks and wait for all of them to finish"
    * "Consider what kind of data structure could track both input and its result"
    * "Review how Go handles timing or delays during execution"
    * "Remember to handle operations that might take longer than expected"
    * "Check how you could measure the total time for an entire process"


### Objectives
  - Define clear, measurable goals that reflect successful task completion at a foundational Go level
  - Describe **what** the candidate should achieve functionally, not **how** to implement it  
  - Objectives will serve to verify completion, assess understanding, and allocate points  
  - Emphasize expected behavior, correctness, and adherence to good Go coding principles  
  - Focus on **functional outcomes**, not on the specific tools, libraries, or concurrency mechanisms used  
  - Highlight expectations for logical structuring, type safety, and meaningful error handling  
  - Encourage clarity in data flow, maintainability, and consistency with Go’s general coding style  
  - Frame objectives around **results and reasoning**, avoiding explicit references to technical constructs  
  - Include expectations that the candidate demonstrates:
    * Correct handling of various input conditions and edge cases  
    * Sensible organization of code into small, purposeful functions  
    * Clear communication of outcomes or statuses through return values or output  
    * Proper validation and error checking where necessary  
    * Readable, maintainable code following Go’s naming and formatting conventions  
  - Objectives should remain **verifiable and outcome-driven**, without prescribing approaches or naming constructs  
  - Guide candidates to think about: correctness, clarity, reliability, testing, and code design fundamentals  
  - **CRITICAL**: Objectives must describe the *intended results* and *reasoning goals*, never the *implementation details*


### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and basic code quality
  - Basic code quality checkpoints (proper error handling, readable code, correct data type usage)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and basic code quality checks
  - Edge case and error scenario validation points
  - Frame verification in terms of observable outcomes and expected behaviors
  - Examples of proper framing:
    * "Test the program with various inputs including edge cases like empty strings or zero values"
    * "Verify that error messages are clear and informative"
    * "Confirm the output matches the expected format for different scenarios"
    * "Check that the code runs without panics or crashes"
    * "Validate that the solution handles invalid input gracefully"
    * "Ensure the code follows Go formatting standards (use gofmt)"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: functionality, edge cases, error handling, code formatting
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

### NOT TO INCLUDE in README:
Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (go mod tidy, go build, go test, go run, etc.)
  - Direct solutions or implementation steps
  - Step-by-step coding guides
  - Specific algorithms or logic to implement (e.g., "use a for loop from 0 to n", "create a map to store counts")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific function implementations that would give away the solution
  - Should not provide any particular approach or algorithm to implement the solution
  - Function names or specific implementation strategies that would reveal the solution
  - Phrases like "you should implement", "make sure to add", "create a function called X"
  - Specific Go standard library function names that would reveal the solution approach

## CRITICAL REMINDERS

1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, kebab-case
3. **code_files** must include README.md, .gitignore, go.mod, and Go source files
4. **README.md** must follow the structure above with Task Overview, Helpful Tips, Objectives, How to Verify
5. **Starter code** must be runnable but must NOT contain the solution
6. **outcomes** and **short_overview** must be bullet-point lists in simple language
7. **hints** must be a single line; **definitions** must include relevant Go terms
8. **Task must be completable within the allocated time** for BASIC proficiency (0-2 years)
9. **NO comments in code** that reveal the solution or give hints
10. **Use Go 1.18+** conventions throughout
"""
PROMPT_REGISTRY = {
    "Golang": [
        PROMPT_GOLANG_BASIC_CONTEXT,
        PROMPT_GO_BASIC_INSTRUCTIONS,
        PROMPT_GOLANG_BASIC_INPUT_AND_ASK,
    ]
}
