PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_INPUT_AND_ASK = """
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

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document or knowledge context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and LlamaIndex implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE LlamaIndex proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, LlamaIndex, and retrieval-augmented generation systems, you are given a list of real world scenarios and proficiency levels for Python and LlamaIndex.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a moderately complex LlamaIndex-based application using INTERMEDIATE-level Python and INTERMEDIATE-level LlamaIndex skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed Python scope
- Intermediate Python with functions, classes, modules, packages, and object-oriented design
- File operations and data serialization with JSON or CSV
- Use of third-party packages with pip and virtual environments
- API consumption or lightweight local app wiring where needed
- Basic networking and concurrency awareness where helpful, but not as the primary challenge
- Unit tests with pytest or unittest
- Debugging, refactoring, error handling, and code quality improvements
- Performance-minded improvements appropriate for a moderate-complexity local project

### Allowed LlamaIndex scope
- Full RAG pipeline design using document loaders, node parsing, indexing, retrieval, and response synthesis
- Local file ingestion or simple connectors appropriate for a self-contained repository
- Text splitting and node parsing choices
- Metadata enrichment and metadata-based filtering
- VectorStoreIndex, ListIndex, SummaryIndex, KeywordTableIndex, or a small composable setup if needed
- Persistence and reload using StorageContext
- Swappable embedding or LLM configuration through clear interfaces or settings
- Custom retriever behavior such as metadata-filtered retrieval or MMR-style selection
- Query engine improvements, citation formatting, and response shaping
- Guardrails for basic prompt-injection resistance or output validation
- Evaluation scripts or tests using practical metrics such as relevance, faithfulness, recall-style checks, or comparison across configurations
- Token, latency, or cost awareness at a practical local-project level
- Caching, batching, or simple retry/backoff where relevant

### Out of scope and MUST NOT be primary requirements
- Large-scale distributed deployment
- Kubernetes, microservices, or production infrastructure as the main task
- Complex cloud provisioning
- Heavy observability stacks as the main focus
- Advanced security engineering beyond practical secret handling and basic prompt-safety
- Fine-tuning models
- Building a full enterprise platform from scratch

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a feature from scratch or fix meaningful issues in an existing Python + LlamaIndex application.
- The task must be specific and well-scoped for INTERMEDIATE proficiency.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should focus on a single local application workflow with 4-5 connected concepts, such as:
  - document ingestion and node creation,
  - index persistence and reload,
  - metadata-aware or custom retrieval,
  - response formatting with citations,
  - evaluation or regression checks,
  - error handling and moderate performance improvements.
- The task must NOT depend on distributed systems design or external infrastructure as the main challenge.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### INTERMEDIATE proficiency calibration
For INTERMEDIATE level, the task should combine 4-5 concepts in a coherent workflow. Suitable combinations include:
- ingestion + chunking strategy + persisted index reload + metadata-filtered retrieval + citation formatting
- repairing a broken query pipeline + improving retriever behavior + adding evaluation coverage + handling invalid inputs
- comparing two retrieval approaches + adding structured response output + improving testability + reducing unnecessary rebuilds
- implementing a local knowledge assistant with source-aware answers + persistence + guardrails + regression tests

The task should require practical reasoning, debugging, and moderate architecture decisions, but it must remain solvable in one sitting.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can understand a moderate codebase, connect ingestion to retrieval to answer generation, and improve correctness, maintainability, and reliability.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + LlamaIndex task that:
- Draws inspiration from one selected scenario to determine the business context and document domain.
- Matches INTERMEDIATE proficiency for both Python and LlamaIndex.
- Tests practical skills with local documents, indexing, persistence, retrieval, response synthesis, and evaluation.
- Uses a lightweight local project structure suitable for the LLM_FRAMEWORK category.
- Avoids Docker and heavy infrastructure unless absolutely necessary.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## Infrastructure Requirements for LLM_FRAMEWORK category
- MUST be a Python project using LlamaIndex.
- MUST include requirements.txt.
- MUST include runnable source files.
- MAY include a lightweight interface such as:
  - a CLI script, or
  - a minimal FastAPI or Flask endpoint, or
  - a simple Streamlit or Gradio app.
- MUST keep the setup lightweight and local.
- MUST use local sample documents included in the repository.
- MUST support local persisted index storage on disk.
- If an API key is needed for one optional path, it must be handled via .env.example and must not be committed as a real secret.
- The baseline task should remain understandable even if the candidate swaps providers or uses a local-compatible setup.

## Starter Code Instructions
- The starter code should provide a clear starting point without solving the core task.
- The generated code files must be valid and executable.
- Keep the code files focused and reasonably modular.
- If the task is a bug-fix task, the starter code should contain logical issues, not syntax errors.
- If the task is a feature task, the starter code should include only the basic structure and wiring.
- The project should be runnable, but the core required behavior should remain incomplete, incorrect, or insufficient until the candidate finishes the task.
- Do NOT include comments that reveal the solution.
- Do NOT include TODO comments or placeholder hints.
- Include tests or evaluation scaffolding for INTERMEDIATE level, but do not implement the final passing logic.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Improve Source-Aware Knowledge Search for Support Playbooks', 'Fix Metadata-Aware Retrieval for Internal Policy Assistant', 'Enhance Local RAG Pipeline for Compliance Document Q&A'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local index artifacts, and .env",
    "requirements.txt": "Python dependencies including llama-index and any lightweight supporting libraries",
    ".env.example": "Example environment variables if needed, without real secrets",
    "app/main.py": "Application entry point",
    "app/config.py": "Configuration values and paths",
    "app/loaders.py": "Document loading module",
    "app/indexing.py": "Node parsing and index creation module",
    "app/retrieval.py": "Retriever or query engine module",
    "app/response.py": "Response shaping or citation formatting module",
    "app/evaluation.py": "Evaluation or regression-check module",
    "data/sample_doc_1.md": "Sample business document",
    "data/sample_doc_2.md": "Additional sample business document",
    "tests/test_app.py": "Test skeletons or regression tests",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, source quality, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, intermediate Python development, and LlamaIndex concepts such as document loading, node parsing, indexing, persistence, retrieval, and evaluation.",
  "answer": "High-level solution approach describing the intended architecture and reasoning at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "VectorStoreIndex": "An index that stores document chunks in a vector-based structure for semantic retrieval",
    "StorageContext": "A LlamaIndex component used to persist and reload index data",
    "Retriever": "A component that selects relevant nodes for a query",
    "Response Synthesizer": "A component that turns retrieved context into a final answer",
    "Metadata Filter": "A retrieval constraint that limits results based on document attributes such as source, type, or access tag"
  }}
}}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use clear module boundaries and readable project structure.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core ingestion, parsing, persistence, retrieval, response synthesis, evaluation, or optimization logic that the candidate must complete should be left empty or minimally stubbed.
- Do NOT include any comments that reveal the solution.
- Do NOT include TODO comments.
- The generated project structure should be runnable, but the required task behavior should remain incomplete until the candidate implements it.
- Include proper tests or evaluation scaffolding for INTERMEDIATE level where appropriate.

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
- Keep objectives measurable and appropriate for INTERMEDIATE level.
- Include expectations around correctness, source quality, persistence behavior, and robustness.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether documents are searchable, whether answers include relevant source context, whether persisted data can be reused, whether retrieval respects metadata or scenario constraints, and whether invalid input is handled gracefully.
- Include verification of tests or evaluation outputs where relevant.
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
2. The task must align with INTERMEDIATE proficiency and combine 4-5 concepts.
3. Use Python 3.10+ and current LlamaIndex conventions.
4. Keep the project local and lightweight for the LLM_FRAMEWORK category.
5. Include local sample documents and local persistence.
6. Include testing or evaluation expectations appropriate for INTERMEDIATE level.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
11. Do not require distributed systems, Kubernetes, or heavy production infrastructure as the main task.
"""

PROMPT_REGISTRY = {
    "Llamaindex (INTERMEDIATE), Python (INTERMEDIATE)": [
        PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_CONTEXT,
        PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_LLAMAINDEX_PYTHON_INTERMEDIATE_INSTRUCTIONS,
    ],
}