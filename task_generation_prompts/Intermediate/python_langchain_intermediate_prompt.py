PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Python and LangChain assessment task.

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

1. What will the task be about? (Describe the business domain, document or knowledge context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of Python and LangChain implementation or fix required, the expected deliverables, and how it aligns with INTERMEDIATE Python + INTERMEDIATE LangChain proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in Python, LangChain, and retrieval-augmented generation systems, you are given a list of real world scenarios and proficiency levels for Python and LangChain.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a moderately complex LangChain-based application using INTERMEDIATE-level Python and INTERMEDIATE-level LangChain skills.

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

### Allowed LangChain scope
- Building chains using LCEL (LangChain Expression Language) or the classic chain APIs
- Prompt templates, output parsers (StrOutputParser, PydanticOutputParser, JSON parsers), and structured outputs
- Document loaders for local files (text, PDF, CSV, Markdown), text splitters, and embeddings
- Vector stores using lightweight local options such as FAISS or Chroma in-memory mode
- RetrievalQA, ConversationalRetrievalChain, and history-aware retrieval patterns
- Custom retrievers, metadata filtering, and contextual compression
- Tools, agents (function-calling or structured-chat), and bounded ReAct loops with safe tool sets
- Memory abstractions such as ConversationBufferMemory or summary-style memory for short sessions
- Callbacks and tracing hooks for observability
- LCEL composition, branching, fallbacks, and `with_retry` / `with_fallbacks` patterns
- Streaming responses where appropriate
- Guardrails for prompt-injection resistance, output validation, and tool-arg validation
- Evaluation scripts using practical metrics such as exact-match, regex match, retrieval recall, citation correctness, or comparison across configurations
- Token, latency, or cost awareness at a practical local-project level
- Caching, batching, simple retry/backoff, and idempotency where relevant

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
- Task must ask the candidate to implement a feature from scratch or fix meaningful issues in an existing Python + LangChain application.
- The task must be specific and well-scoped for INTERMEDIATE proficiency.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should focus on a single local application workflow with 4-5 connected concepts, such as:
  - document ingestion + splitting + embedding + retrieval,
  - prompt design + structured output parsing,
  - bounded agent or tool use with guardrails,
  - chain composition with retries, fallbacks, or branching,
  - evaluation or regression checks,
  - error handling and moderate performance improvements.
- The task must NOT depend on distributed systems design or external infrastructure as the main challenge.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### INTERMEDIATE proficiency calibration
For INTERMEDIATE level, the task should combine 4-5 concepts in a coherent workflow. Suitable combinations include:
- ingestion + splitter strategy + persisted vector store reload + metadata-filtered retrieval + citation formatting
- repairing a broken RetrievalQA pipeline + improving retriever behavior + adding evaluation coverage + handling invalid inputs
- comparing two prompt or retrieval approaches + adding structured output parser + improving testability + reducing unnecessary rebuilds
- implementing a bounded function-calling or structured-chat agent with a small safe toolset + tool-argument validation + max-iteration guardrails + regression tests

The task should require practical reasoning, debugging, and moderate architecture decisions, but it must remain solvable in one sitting.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can understand a moderate codebase, connect ingestion to retrieval to answer generation, and improve correctness, maintainability, and reliability.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Python + LangChain task that:
- Draws inspiration from one selected scenario to determine the business context and document or tool domain.
- Matches INTERMEDIATE proficiency for both Python and LangChain.
- Tests practical skills with local documents or tools, chain composition, retrieval, structured output, and evaluation.
- Uses a lightweight local project structure suitable for the LLM_FRAMEWORK category.
- Avoids Docker and heavy infrastructure unless absolutely necessary.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## Infrastructure Requirements for LLM_FRAMEWORK category
- MUST be a Python project using LangChain.
- MUST include requirements.txt.
- MUST include runnable source files.
- MAY include a lightweight interface such as:
  - a CLI script, or
  - a minimal FastAPI or Flask endpoint, or
  - a simple Streamlit or Gradio app.
- MUST keep the setup lightweight and local.
- MUST use local sample documents or fixtures included in the repository.
- MUST support local persisted vector store on disk if the scenario uses retrieval (FAISS save_local or Chroma persist directory).
- If an API key is needed for one optional path, it must be handled via .env.example and must not be committed as a real secret.
- The baseline task should remain understandable even if the candidate swaps providers (OpenAI, Anthropic, or a local-compatible setup).

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
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Harden Bounded Agent for Refund Policy Lookup', 'Fix Citation-Aware RetrievalQA for Internal Knowledge Base', 'Improve Structured Output Pipeline for Support Triage'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {{
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local vector store artifacts, and .env",
    "requirements.txt": "Python dependencies including langchain (with langchain-core, langchain-community, and a provider package such as langchain-openai if used) plus any lightweight supporting libraries",
    ".env.example": "Example environment variables if needed, without real secrets",
    "app/main.py": "Application entry point",
    "app/config.py": "Configuration values and paths",
    "app/loaders.py": "Document loading or data ingestion module",
    "app/chains.py": "Chain composition module (LCEL or chain classes)",
    "app/retrieval.py": "Retriever or vector-store module",
    "app/output.py": "Structured output parsing or response shaping module",
    "app/evaluation.py": "Evaluation or regression-check module",
    "data/sample_doc_1.md": "Sample business document or fixture",
    "data/sample_doc_2.md": "Additional sample business document or fixture",
    "tests/test_app.py": "Test skeletons or regression tests",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  }},
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, response quality, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, intermediate Python development, and LangChain concepts such as document loaders, splitters, vector stores, retrievers, prompts, output parsers, and basic agents or tools.",
  "answer": "High-level solution approach describing the intended architecture and reasoning at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {{
    "LCEL": "LangChain Expression Language — a declarative way to compose runnables (prompts, models, parsers, retrievers) into chains with `|` piping",
    "RetrievalQA": "A high-level chain that combines a retriever with an LLM to answer questions over indexed documents",
    "Output Parser": "A LangChain component that converts raw LLM text into a structured Python value (string, JSON, Pydantic model)",
    "Vector Store": "A datastore that holds document embeddings and supports similarity search; FAISS and Chroma are common local options",
    "Tool": "A callable that an agent can invoke; tools have a name, description, and a typed argument schema"
  }}
}}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use clear module boundaries and readable project structure.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core ingestion, chain composition, retrieval, output parsing, evaluation, or optimization logic that the candidate must complete should be left empty or minimally stubbed.
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
- local persisted vector store directories such as storage/, indexes/, chroma_db/, or faiss_index/

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
- Include expectations around correctness, response quality, persistence behavior, and robustness.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether documents are searchable, whether answers include relevant source context, whether persisted data can be reused, whether retrieval respects metadata or scenario constraints, whether agents stay within the safe tool set, and whether invalid input is handled gracefully.
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
3. Use Python 3.10+ and current LangChain conventions (langchain-core, provider packages, LCEL where natural).
4. Keep the project local and lightweight for the LLM_FRAMEWORK category.
5. Include local sample documents or fixtures and local persistence where retrieval is involved.
6. Include testing or evaluation expectations appropriate for INTERMEDIATE level.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
11. Do not require distributed systems, Kubernetes, or heavy production infrastructure as the main task.
"""

PROMPT_REGISTRY = {
    "Langchain (INTERMEDIATE), Python (INTERMEDIATE)": [
        PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_CONTEXT,
        PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_INPUT_AND_ASK,
        PROMPT_LANGCHAIN_PYTHON_INTERMEDIATE_INSTRUCTIONS,
    ],
}
