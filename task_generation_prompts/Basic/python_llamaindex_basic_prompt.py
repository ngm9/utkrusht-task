PROMPT_LLAMAINDEX_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_LLAMAINDEX_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and LlamaIndex assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

CRITICAL TASK GENERATION REQUIREMENTS:
- You MUST draw inspiration from ONE of the real-world scenarios provided above to create the task.
- The task scenario should closely align with the business context, technical requirements, and domain described in the selected real-world scenario.
- The task complexity must be appropriate for the given skill level and years of experience indicated in the competencies.
- Ensure the candidate can realistically complete the task in the allocated time.
- Select a different real-world scenario each time to ensure variety in task generation.
- The task must reflect authentic challenges that would be encountered in the role described in the role context.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document/data context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and LlamaIndex implementation or fix required, the expected deliverables, and how it aligns with BASIC Python + BASIC LlamaIndex proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_LLAMAINDEX_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, LlamaIndex, and practical retrieval-based AI applications, you are given a list of real world scenarios and proficiency levels for Python and LlamaIndex.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build or fix a small, practical LlamaIndex-based application using BASIC-level Python and BASIC-level LlamaIndex skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Basic Python syntax, functions, control flow, lists, dictionaries, sets, tuples
- Simple file I/O
- Basic exception handling with try/except
- Simple scripts and straightforward module organization
- Basic package management with pip
- Reading and making minor edits to existing code

### Allowed LlamaIndex scope
- Python 3.8+ environment setup
- Installing llama-index and related basic dependencies
- Loading a small-to-moderate local corpus using simple readers such as SimpleDirectoryReader
- Creating Document and Node objects through standard LlamaIndex flows
- Using default text splitting with simple chunk size / overlap adjustments if needed
- Building and persisting a VectorStoreIndex, ListIndex, or SummaryIndex
- Reloading an index from disk
- Using a basic retriever or query engine
- Running simple synchronous queries
- Returning answers with source information
- Basic local evaluation such as checking relevance manually or with simple precision-style checks
- Recording simple settings and results
- Keeping secrets out of version control
- Preventing trivial prompt injection in a basic way
- Providing a reproducible local demo

### Out of scope and MUST NOT be required
- Async query flows as a primary requirement
- Advanced tuning such as temperature, max_tokens, context_window as core task requirements
- Custom retrievers
- Hybrid retrieval
- Multi-index graphs
- Fine-tuning embeddings
- Advanced RAG evaluation frameworks
- Large-scale latency optimization
- High-availability or production-scale architecture
- Complex observability systems
- Multi-service distributed systems

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a feature from scratch or fix bugs in an existing small LlamaIndex application.
- The task must be specific and well-scoped for BASIC proficiency.
- The scenario must be realistic and business-oriented, not a toy puzzle.
- The task should focus on a single-application workflow such as:
  - ingesting a small document set,
  - building or repairing a local index,
  - persisting and reloading the index,
  - exposing a simple query flow through CLI, a lightweight script, or a minimal FastAPI/Flask/Streamlit interface.
- The task must NOT depend on advanced system design.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### BASIC proficiency calibration
For BASIC level, the task should combine only 2-3 concepts in a clear and digestible way. Suitable combinations include:
- document loading + index creation + simple querying
- persisted index reload + query response formatting
- metadata attachment + source display
- simple error handling + local index regeneration
- basic prompt-safety guardrails + document QA flow

The task should NOT require the candidate to invent architecture or design a complex RAG system.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can understand a small codebase, connect the document ingestion flow to the query flow, and produce a working local demo.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + LlamaIndex task that:
- Draws inspiration from one selected scenario to determine the business context and document domain.
- Matches BASIC proficiency for both Python and LlamaIndex.
- Tests practical skills with local documents, indexing, persistence, and simple querying.
- Uses simple synchronous workflows only.
- Avoids advanced retrieval architecture and advanced tuning requirements.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## Infrastructure Requirements for LLM_FRAMEWORK category
- MUST be a Python project using LlamaIndex.
- MUST include requirements.txt.
- MUST include runnable source files.
- MAY include a lightweight interface such as:
  - a CLI script, or
  - a minimal FastAPI/Flask endpoint, or
  - a simple Streamlit/Gradio app
- MUST NOT require Docker for this category unless absolutely necessary.
- MUST keep the setup lightweight and local.
- MUST use local sample documents included in the repository.
- MUST support local persisted index storage on disk.
- If an API key is needed for one optional path, it must be handled via .env.example and must not be committed as a real secret.
- The baseline task should remain understandable even if the candidate swaps providers or uses a local-compatible setup.

## Starter Code Instructions
- The starter code should provide a clear starting point without solving the core task.
- The generated code files must be valid and executable.
- Keep the code files minimal and focused.
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors.
- If the task is a feature task, the starter code should include only the basic structure and wiring.
- The project should be runnable, but the core required behavior should remain incomplete or incorrect until the candidate finishes the task.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments or placeholder hints.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Build Document Q&A Assistant for Policy Handbook', 'Fix Local Knowledge Search for Support Articles', 'Implement Source-Aware FAQ Retrieval for HR Docs'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local index artifacts, and .env",
    "requirements.txt": "Python dependencies including llama-index and any lightweight supporting libraries",
    ".env.example": "Example environment variables if needed, without real secrets",
    "app/main.py": "Application entry point",
    "app/indexing.py": "Document loading and index creation module",
    "app/query.py": "Query flow module",
    "app/config.py": "Configuration values and paths",
    "data/sample_doc_1.txt": "Sample business document",
    "data/sample_doc_2.txt": "Additional sample business document",
    "tests/test_app.py": "Basic test skeleton if included",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, clarity, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, basic Python scripting, and basic LlamaIndex concepts such as document loading, indexing, persistence, and querying.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "VectorStoreIndex": "An index that stores document chunks in a vector-based structure for semantic retrieval",
    "Retriever": "A component that finds the most relevant indexed content for a user query",
    "Query Engine": "A component that uses retrieval and response generation to answer a question",
    "Persistence": "Saving an index to disk so it can be reused without rebuilding every time",
    "Source Node": "A retrieved piece of source content used to support an answer"
  }}
}}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use simple project structure and readable module boundaries.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core indexing, persistence, reload, retrieval, or answer formatting logic that the candidate must complete should be left empty or minimally stubbed.
- Do NOT include any comments that reveal the solution.
- Do NOT include TODO comments.
- The generated project structure should be runnable, but the required task behavior should remain incomplete until the candidate implements it.

## .gitignore INSTRUCTIONS
Create a sensible Python gitignore for an LLM framework task, including:
- __pycache__/
- *.pyc
- .venv/
- venv/
- .env
- .pytest_cache/
- .mypy_cache/
- *.log
- build/
- dist/
- *.egg-info/
- .DS_Store
- local persisted index directories such as storage/ or indexes/

## README.md STRUCTURE

The README.md must contain the following sections:
- Task Overview
- Helpful Tips
- Objectives
- How to Verify

The README must be concise and open-ended. Each section should contain only the essential points needed to understand the task. Do NOT overload it with too many bullets.

### Task Overview
- Must contain 2-3 meaningful sentences describing the business scenario and current state of the application.
- Must explain why the task matters in the business context.
- Must be specific to the generated scenario.

### Helpful Tips
- 3-4 bullets maximum.
- Use action words like "Consider", "Review", "Explore", "Think about".
- Guide discovery without revealing the implementation.
- Do not mention exact solution steps or exact method names that would give away the answer.

### Objectives
- 3-5 bullets maximum.
- Describe what should work after completion.
- Focus on outcomes, not implementation details.
- Keep objectives measurable and appropriate for BASIC level.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether documents are searchable, whether answers include relevant source context, whether persisted data can be reused, and whether invalid input is handled gracefully.
- Do not include setup commands.

### NOT TO INCLUDE in README
- Step-by-step implementation instructions
- Direct solutions
- Code snippets
- Setup commands
- Advanced architecture discussion
- Any candidate-facing solution explanation

## Candidate-visible output policy
- The generated task JSON must be candidate-safe.
- Do NOT include any candidate-facing "answer" field or solution approach in the output schema.
- Keep solution guidance out of candidate-visible files.

## CRITICAL REMINDERS
1. Output must be valid JSON only when the prompt is later used to generate a task.
2. The task must align with BASIC proficiency and remain narrowly scoped.
3. Use simple synchronous workflows only.
4. Do not require advanced tuning or advanced retrieval architecture.
5. Use Python 3.10+ and current LlamaIndex conventions.
6. Include local sample documents and local persistence.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
"""

PROMPT_REGISTRY = {
    "Llamaindex (BASIC), Python (BASIC)": [
        PROMPT_LLAMAINDEX_BASIC_CONTEXT,
        PROMPT_LLAMAINDEX_BASIC_INPUT_AND_ASK,
        PROMPT_LLAMAINDEX_BASIC_INSTRUCTIONS,
    ],
}