PROMPT_LLAMAINDEX_PYTHON_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_LLAMAINDEX_PYTHON_BASIC_INPUT_AND_ASK = """
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
- Use the provided real-world scenario as the basis for this task - do not invent a different domain. When multiple scenarios are listed, pick the one whose technical surface area best fits the candidate level
- The task must reflect authentic challenges that would be encountered in the role described in the role context.
- The task must stay within BASIC Python and BASIC LlamaIndex scope: small local project, straightforward ingestion, one simple index, local persistence, simple query flow, basic parameter tuning, and basic error handling.
- Keep the task lightweight and practical for completion within {minutes_range} minutes.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document or knowledge context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and LlamaIndex implementation or fix required, the expected deliverables, and how it aligns with BASIC Python + BASIC LlamaIndex proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_LLAMAINDEX_PYTHON_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, LlamaIndex, and lightweight retrieval-augmented generation workflows, you are given a list of real world scenarios and proficiency levels for Python and LlamaIndex.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a small LlamaIndex-based application using BASIC-level Python and BASIC-level LlamaIndex skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Basic Python syntax, functions, dictionaries, lists, loops, conditionals, and file handling
- Simple modules and small project structure
- Basic exception handling with try/except
- Reading local files and returning JSON-like responses
- Using pip dependencies and a virtual environment
- Minor edits to existing code and straightforward debugging
- Simple scripts or a minimal API/CLI wrapper

### Allowed LlamaIndex scope
- Loading a small local corpus using packaged readers such as SimpleDirectoryReader
- Creating Document and Node objects with metadata
- Using default text splitting with small adjustments to chunk_size and overlap
- Building one simple index such as VectorStoreIndex, ListIndex, or SummaryIndex
- Persisting and reloading index data locally
- Using a basic retriever or query engine with standard settings
- Returning answer text plus source_nodes, citations, or similarity information
- Adjusting simple parameters such as similarity_top_k, chunk size, overlap, temperature, or max tokens
- Logging or printing simple observations about retrieval quality, latency, token usage, or errors
- Basic secret handling through .env.example
- Simple idempotent index regeneration scripts

### Out of scope and MUST NOT be primary requirements
- Custom retrievers
- Hybrid search
- Multi-index graphs or routing
- Fine-tuning models or embeddings
- Advanced evaluation frameworks
- Large-scale optimization
- Production-grade observability or HA design
- Complex security engineering
- Distributed systems or cloud infrastructure as the main task

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a small feature from scratch or fix meaningful issues in an existing Python + LlamaIndex application.
- The task must be specific, narrow, and well-scoped for BASIC proficiency.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should focus on one small local workflow using 2-3 connected concepts, such as:
  - loading local documents and preserving metadata,
  - building or reloading a persisted index,
  - fixing a broken query path,
  - improving chunking for better retrieval,
  - returning citations from source_nodes,
  - handling invalid input or missing storage gracefully.
- The task must NOT depend on distributed systems design or heavy infrastructure.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### BASIC proficiency calibration
For BASIC level, the task should be more specific and less open-ended. Suitable task shapes include:
- fixing a local query flow that returns an answer but no citations,
- reloading a persisted index instead of rebuilding it every run,
- preserving file metadata so source paths appear in results,
- adjusting chunk size and overlap so short policy or FAQ sections become retrievable,
- validating a minimal API or CLI input before calling the query engine,
- handling a missing storage directory or missing documents without crashing.

The task should require practical debugging and small implementation decisions, but not architecture-heavy reasoning.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can understand a small codebase, connect ingestion to indexing to querying, and improve correctness and maintainability.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + LlamaIndex task that:
- Draws inspiration from one selected scenario to determine the business context and document domain.
- Matches BASIC proficiency for both Python and LlamaIndex.
- Tests practical skills with local documents, one simple index, local persistence, retrieval, and source-aware answers.
- Uses a lightweight local project structure suitable for the LLM_FRAMEWORK category.
- Avoids Docker and heavy infrastructure.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## Infrastructure Requirements for LLM_FRAMEWORK category
- MUST be a Python project using LlamaIndex.
- MUST include requirements.txt.
- MUST include runnable source files.
- MAY include one lightweight interface such as:
  - a CLI script, or
  - a minimal Flask or FastAPI endpoint.
- MUST keep the setup lightweight and local.
- MUST use local sample documents included in the repository.
- MUST support local persisted index storage on disk.
- If an API key is needed for one optional path, it must be handled via .env.example and must not be committed as a real secret.
- The baseline task should remain understandable even if the candidate swaps providers or uses a local-compatible setup.

## Starter Code Instructions
- The starter code should provide a clear starting point without solving the core task.
- The generated code files must be valid and executable.
- Keep the code files focused and simple.
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors.
- If the task is a feature task, the starter code should include only the basic structure and wiring.
- The project should be runnable, but the core required behavior should remain incomplete, incorrect, or insufficient until the candidate finishes the task.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments or placeholder hints.
- Do NOT require advanced test suites; lightweight verification scaffolding is enough for BASIC level.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Source Citations for Internal FAQ Assistant', 'Improve Local Policy Search for Support Team', 'Repair Persisted Index Loading for Help Bot'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local storage artifacts, and .env",
    "requirements.txt": "Python dependencies including llama-index and any lightweight supporting libraries",
    ".env.example": "Example environment variables if needed, without real secrets",
    "app/main.py": "Application entry point or minimal API",
    "app/config.py": "Configuration values and paths",
    "app/loaders.py": "Document loading module",
    "app/indexing.py": "Index creation and persistence module",
    "app/query.py": "Query engine wrapper and response shaping module",
    "data/sample_doc_1.md": "Sample business document",
    "data/sample_doc_2.md": "Additional sample business document",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, source quality, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, basic Python development, and LlamaIndex concepts such as document loading, chunking, indexing, persistence, and querying.",
  "answer": "High-level solution approach describing the intended flow at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "Document": "A LlamaIndex object representing source content and its metadata before indexing",
    "Node": "A smaller chunk of a document used during indexing and retrieval",
    "VectorStoreIndex": "An index that stores document chunks for semantic retrieval",
    "QueryEngine": "A component that accepts a question and returns an answer using retrieved context",
    "source_nodes": "The retrieved chunks that support the final answer and can be used for citations"
  }}
}}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use a clear, readable project structure.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core ingestion, chunking adjustment, persistence, reload, query, citation extraction, or validation logic that the candidate must complete should be left empty or minimally stubbed.
- Do NOT include any comments that reveal the solution.
- Do NOT include TODO comments.
- The generated project structure should be runnable, but the required task behavior should remain incomplete until the candidate implements it.
- Keep the codebase small enough for a BASIC-level candidate to understand quickly.

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

The README must be concise and open-ended. Each section should contain only the essential points needed to understand the task.

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
- Include expectations around correctness, citations, persistence behavior, and robustness where relevant.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether documents are searchable, whether answers include relevant source context, whether persisted data can be reused, whether invalid input is handled gracefully, and whether retrieval improves after simple parameter changes where relevant.
- Do not include setup commands.

### NOT TO INCLUDE in README
- Step-by-step implementation instructions
- Direct solutions
- Code snippets
- Setup commands
- Candidate-facing solution explanations
- Heavy architecture discussion unrelated to the task

## Candidate-visible output policy
- The generated task JSON must be candidate-safe.
- Keep solution guidance out of candidate-visible files.
- The task should assess implementation skill, debugging ability, and practical reasoning rather than memorization.

## CRITICAL REMINDERS
1. Output must be valid JSON only when the prompt is later used to generate a task.
2. The task must align with BASIC proficiency and use only 2-3 connected concepts.
3. Use Python 3.10+ and current LlamaIndex conventions.
4. Keep the project local and lightweight for the LLM_FRAMEWORK category.
5. Include local sample documents and local persistence.
6. Do not require advanced testing, custom retrievers, hybrid search, or multi-index design.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
11. Prefer realistic work items such as fixing a broken retrieval flow, improving chunking, restoring citations, or making a minimal query path more robust.
"""

PROMPT_REGISTRY = {
    "Llamaindex (BASIC), Python (BASIC)": [
        PROMPT_LLAMAINDEX_PYTHON_BASIC_CONTEXT,
        PROMPT_LLAMAINDEX_PYTHON_BASIC_INPUT_AND_ASK,
        PROMPT_LLAMAINDEX_PYTHON_BASIC_INSTRUCTIONS,
    ],
}