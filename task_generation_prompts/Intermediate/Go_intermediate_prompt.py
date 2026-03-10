PROMPT_GOLANG_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_GOLANG_INPUT_AND_ASK = """
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
2. What will the task look like? (Describe the type of Go implementation or fix required, the expected deliverables, and how it aligns with the given Go proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_GO_INTERMEDIATE_INSTRUCTIONS="""
## GOAL
As a technical architect super experienced in Go and modern Go ecosystem, you are given a list of real world scenarios and proficiency levels for Go development. 
Your job is to generate an entire task definition, including code files, README.md, expected outcomes etc. that can be effectively used to assess the candidate's ability to effectively think, design, build, implement, debug or in general solve a problem end to end at an intermediate level.

## INSTRUCTIONS

### Nature of the Task 
- Task must ask to implement a feature from scratch, refactor existing code, or fix complex bugs in the existing codebase.
- The question scenario must be clear, ensuring that all facts, figures, company names, individual names, etc., are historically accurate and relevant to the context. 
- Generate enough starter code that gives the candidate a good starting point to start solving the task
- DO NOT GIVE AWAY THE SOLUTION IN THE STARTER CODE.
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper architecture decisions, and not just fix the errors
- The question should be a real-world scenario that tests architectural thinking and not just implementation skills.
- The complexity of the task and specific ask expected from the candidate must align with INTERMEDIATE proficiency level (3-5 years Go experience), ensuring that no two questions generated are similar. 
- For INTERMEDIATE level of proficiency, the questions should test deeper understanding and require candidates to demonstrate:
  - **Idiomatic Go Design**: Interface design, composition over inheritance, error handling patterns, context usage
  - **Architecture & Structure**: Clean architecture, dependency injection, package organization, module design
  - **Concurrency Patterns**: Goroutines, channels, select statements, sync primitives, context cancellation, worker pools
  - **Performance Optimization**: Efficient algorithms, memory management, profiling awareness, buffer pooling, avoiding allocations
  - **Advanced Go Features**: Generics (Go 1.18+), embedding, type assertions, reflection (when appropriate), functional options pattern
  - **Project Architecture**: Package structure design, internal vs exported APIs, module boundaries
  - **Error Handling**: Custom error types, error wrapping, sentinel errors, error inspection patterns
  - **Code Quality**: Go idioms, effective Go practices, proper documentation, gofmt/golint compliance
  - **Real-world Patterns**: Repository pattern, service layer, middleware, dependency injection, graceful shutdown
  - **Concurrency Safety**: Race condition prevention, proper mutex usage, atomic operations, immutability patterns
- The question must NOT include hints. The hints will be provided in the "hints" field. 
- Ensure that all questions and scenarios adhere to modern Go best practices (Go 1.18+) and current development standards. Use modern Go features appropriately.
- Tasks should require candidates to make architectural decisions and justify their approach.
- If you include diagrams, ensure they are written in mermaid format, properly indented and also in code blocks.

### AI AND EXTERNAL RESOURCE POLICY:
- Candidates are permitted and encouraged to use any external resources they find helpful, including but not limited to Google, Stack Overflow, official documentation, and AI-powered tools, agentic IDs, or Large Language Models (LLMs). 
- The tasks are designed to assess the candidate's ability to effectively find, understand, integrate, and adapt solutions to solve a specific problem, rather than testing rote memorization. Therefore, the complexity of the tasks should reflect intermediate Go proficiency while requiring genuine engineering and architectural skills that go beyond simple copy-pasting from a generative AI.
- Tasks should test the candidate's ability to evaluate different approaches and choose the most appropriate solution.

### Code Generation Instructions:
Based on the real-world scenarios provided in following conversations, create a Go task that:
- Draws inspiration from the input_scenarios given to determine the business context and technical requirements
- Matches the complexity level appropriate for INTERMEDIATE proficiency level (3-5 years Go experience), keeping in mind that AI assistance is allowed.
- Tests practical Go skills that require architectural thinking, performance considerations, and advanced pattern implementation
- Time constraints: Each task should be finished within {minutes_range} minutes.
- At every time pick different real-world scenario from the list provided above to ensure variety in task generation.
- Focus on multi-package applications that require thoughtful architecture and interface design
- Should test the candidate's ability to structure a scalable Go application

### Starter Code Instructions:
- The starter code should provide a foundation that allows candidates to demonstrate architectural skills
- The code files generated must be valid and executable with `go build` or `go run`.
- Provide a realistic project structure that mimics real-world Go applications
- A part of the task completion is to watch the candidate implement best practices, design the solution correctly, demonstrate proper package structure, and architectural decisions
- If the task is to fix bugs, make sure the starter code has logical bugs or architectural issues (no syntactic errors) that require intermediate-level thinking to resolve
- If the task is to implement a feature from scratch, provide a foundation that allows candidates to showcase proper interface design and architecture
- Go starter code should include realistic project structure but NOT require complex infrastructure setup
- Include some existing interfaces/structs/utilities that the candidate needs to work with or extend
- Provide partial implementations that require candidates to complete the architecture

## OUTPUT
The output should be a valid json schema:
  - README.md (CRITICAL - Follow exact structure specified below)
  - go.mod (Go module definition)
  - go.sum (Go dependencies checksum - can be empty initially)
  - .gitignore (Standard Go project gitignore)
  - Any code files that are to be included as a part of the task. These should not include the solution but should be a good starting point for the candidate to start solving the task.
  - Code files should demonstrate partial architecture that candidate needs to complete/extend
  - Include realistic folder structure (cmd/app/, internal/service/, internal/repository/, internal/model/, pkg/utils/, etc.)

## REQUIRED OUTPUT JSON STRUCTURE
{{
   "name": "Task Name",
   "question": "A detailed description of the task scenario including the specific ask from the candidate — what needs to be implemented/refactored/fixed? Include architectural considerations and requirements.",
   "code_files": {{
      "README.md": "Candidate-facing README with Task Overview, Helpful Tips, Objectives, and How to Verify",
      ".gitignore": "Proper Go exclusions",
      "go.mod": "Go module definition with intermediate-level dependencies",
      "go.sum": "Go dependencies checksum (can be empty)",
      "cmd/app/main.go": "Main application entry point",
      "internal/model/model.go": "Internal domain models",
      "internal/service/service.go": "Service layer interfaces and implementations",
      "internal/repository/repository.go": "Data access layer interfaces",
      "pkg/utils/utils.go": "Exported utility functions",
      "internal/errors/errors.go": "Custom error types (if needed)",
      "config/config.go": "Configuration structs (if needed)",
      "starter_code_file_name": "starter_code_file_content",
      "starter_code_file_name_2": "starter_code_file_content_2"
      ...
  }},
  "outcomes": "Expected results after completion focusing on architectural quality, performance, and code organization. 3-4 lines describing both functional and architectural outcomes.",
  "pre_requisites": "Bullet-point list of tools, libraries, and environment setup required. Include intermediate-level expectations like modern Go knowledge, concurrency patterns understanding, testing familiarity, etc.",
  "answer": "High-level solution approach with emphasis on architectural decisions and Go idioms",
  "hints": "a single line hint focusing on architectural approach or Go pattern that could be useful. These hints must NOT give away the answer, but guide towards idiomatic Go thinking.",
  "definitions": {{
    "terminology_1": "definition_1",
    "terminology_2": "definition_2",
    ...
    }}
}}

### Code file requirements:
- Generate realistic folder structure (cmd/app/, internal/service/, internal/repository/, internal/model/, pkg/, etc.)
- Code should follow Go best practices and demonstrate intermediate-level patterns
- Use appropriate Go idioms, interfaces, and composition patterns
- Focus on modern Go features (Go 1.18+) and development best practices
- **CRITICAL**: The generated code files should provide partial implementations that require architectural completion
- Include some existing interfaces/structs that need to be extended or integrated
- The core architectural decisions, interface design, concurrency patterns, or architecture solutions that the candidate needs to implement MUST be left for the candidate to design
- DO NOT include any 'TODO' or placeholder comments
- DO NOT include any comments that give away hints or solutions
- DO NOT include comments like "Add optimization here" or "Should implement pattern X" etc.
- DO NOT add comments that give away hints or solution or implementation details
- The generated project structure should be compilable with `go build`, but will require architectural completion to function properly
- Provide realistic dependencies in go.mod that intermediate developers should be familiar with

### .gitignore INSTRUCTIONS:
Create a comprehensive gitignore file that covers all standard exclusions for intermediate Go projects including binary executables, vendor directories, IDE configurations (.idea/, .vscode/, .DS_Store), compiled binaries, coverage files (*.out, *.test), log files, and other common development artifacts that should not be tracked in version control.

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

#### Task Overview

**CRITICAL REQUIREMENT**: This section MUST contain 3-4 meaningful sentences describing the business scenario, current situation, and why architectural considerations matter for this use case. 
NEVER generate empty content - always provide substantial business context that explains what the candidate is working on and why proper architecture is crucial.

#### Helpful Tips
Provide practical guidance without revealing specific implementations:
  - Suggest exploring Go patterns that promote interface segregation and composition
  - Mention thinking about how different packages should communicate through well-defined interfaces
  - Hint at considering Go idioms that make code idiomatic and maintainable
  - Recommend exploring how to handle errors idiomatically throughout the application
  - Suggest thinking about concurrency implications and safe goroutine communication patterns
  - Point toward considering how the code can be made testable with interface-based design
  - Recommend considering race conditions and proper synchronization mechanisms
  - Suggest analyzing whether common behaviors can be abstracted into reusable interfaces
  - Mention thinking about how to organize code into internal and exported packages appropriately
  - Use bullet points formatted as tips, starting with action words like "Consider", "Think about", "Explore", "Review", "Analyze"
  - **CRITICAL**: Tips should guide discovery toward idiomatic Go thinking, not provide direct solutions or specific patterns
  - **CRITICAL**: tips should not give way any code hints directly or indirectly should not include direct functions or code files or any methods 
  - Frame suggestions around Go principles and outcomes rather than specific implementations
  - Examples of proper framing:
    * "Consider how to separate concerns using Go's interface-based design"
    * "Think about organizing functionality into cohesive packages with clear boundaries"
    * "Explore approaches that allow concurrent operations without data races"
    * "Review how to propagate errors with sufficient context at each layer"
    * "Consider memory efficiency when processing large data streams"

#### Objectives
  - Clear, measurable goals for the candidate appropriate for intermediate level
  - This is what the candidate should be able to do successfully to say that they have completed the task
  - These objectives will also be used to verify the task completion and award points
  - What functionality should be implemented, expected behavior, and architectural qualities
  - Focus on both functional requirements and code quality metrics
  - Include expectations for package structure, interface design, and performance
  - Frame objectives around outcomes rather than specific technical implementations
  - Examples of proper framing:
    * "Implement functionality that processes requests concurrently while maintaining data integrity"
    * "Design a solution that allows new handlers to be added without modifying existing code"
    * "Create a system that handles various failure scenarios with proper error context"
    * "Organize code into packages that separate concerns and promote reusability"
    * "Ensure concurrent operations are safe from race conditions and deadlocks"
  - Objectives should be measurable but not prescribe specific patterns or approaches
  - Should guide candidates to think about: concurrency, maintainability, performance, testability, idiomatic Go
  - **CRITICAL**: Objectives describe the "what" and "why", never the "how"

#### How to Verify
  - Specific checkpoints after implementation, what to test and how to confirm success
  - Observable behaviors or outputs to validate both functionality and architecture
  - Code quality checkpoints (interface design, performance, error handling, concurrency safety)
  - These points will help the candidate to verify their own work and the video recording of them performing these steps will also help the assessor to see how thorough they are in checking their own work and award points
  - Include both functional testing and architectural assessment criteria
  - Performance, concurrency, and edge case validation points
  - Frame verification in terms of observable outcomes and system behaviors
  - Examples of proper framing:
    * "Test the system with various input scenarios including edge cases and malformed data"
    * "Verify that concurrent operations don't produce race conditions (consider using `go test -race`)"
    * "Confirm error messages provide sufficient context for debugging"
    * "Check that the solution performs efficiently with realistic workloads"
    * "Validate that changes to one package don't require modifications to unrelated packages"
    * "Ensure interfaces can be mocked for isolated unit testing"
  - Suggest what to verify and why it matters, not specific implementation details to check
  - Guide candidates to test: functionality, edge cases, performance, concurrency safety, error scenarios
  - **CRITICAL**: Describe what to verify and expected behaviors, not the specific implementation to check

#### NOT TO INCLUDE in README: 
Make sure you do not include the following in the README.md file:
  - SETUP INSTRUCTIONS OR COMMANDS (go mod tidy, go build, go test, go run, etc.)
  - Direct solutions or architectural decisions
  - Step-by-step implementation guides
  - Specific design patterns or implementation approaches (e.g., "use worker pool pattern", "implement middleware chain")
  - Direct answers and code snippets that would give away the solution to the task
  - Any specific interface or struct implementation details that would give away the solution
  - Should not provide any particular architectural approach or Go pattern to implement the solution
  - Interface names or specific implementation strategies that would reveal the solution
  - Package structure decisions that would dictate the architectural approach
  - Phrases like "you should implement", "make sure to add", "create an interface called X"
  - Specific Go standard library recommendations that would reveal the solution approach
  
  """
PROMPT_REGISTRY = {
    "Golang (INTERMEDIATE)": [
        PROMPT_GOLANG_CONTEXT,
        PROMPT_GOLANG_INPUT_AND_ASK,
        PROMPT_GO_INTERMEDIATE_INSTRUCTIONS,
    ]
}
