PROMPT_LANGCHAIN_BASIC_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_LANGCHAIN_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a LangChain assessment task.

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
- The task must stay within BASIC LangChain scope: small local prototype, straightforward prompt or chain wiring, simple memory or retrieval flow, standard loaders/splitters/vector stores if used, basic validation, and lightweight debugging.
- Keep the task lightweight and practical for completion within {minutes_range} minutes.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, document or data context, and problem the candidate will be solving.)
2. What will the task look like? (Describe the type of LangChain implementation or fix required, the expected deliverables, and how it aligns with BASIC LangChain proficiency.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_LANGCHAIN_BASIC_INSTRUCTIONS = """
## GOAL
As a technical architect experienced in LangChain and lightweight LLM application development, you are given a list of real world scenarios and proficiency levels for LangChain.
Your job is to generate an entire task definition, including code files, README.md, expected outcomes, and verification guidance, that can be used to assess a candidate's ability to build, debug, and improve a small LangChain-based application using BASIC-level LangChain skills.

## HARD SCOPE BOUNDARY
You MUST stay within the provided competency scope.

### Allowed LangChain scope
- Explaining and using LangChain at a practical prototype level
- PromptTemplate usage in f-string or Jinja style
- Small chains such as LLMChain, SimpleSequentialChain, SequentialChain, or RouterChain
- Passing context with ConversationBufferMemory, ConversationSummaryMemory, or token-buffer memory
- Loading local documents or structured files such as text, PDF, HTML, JSON, or CSV with standard loaders
- Chunking text with RecursiveCharacterTextSplitter
- Creating embeddings with standard provider wrappers or sentence-transformer models
- Using FAISS, Chroma, or Pinecone with basic add, similarity_search, and delete operations
- Building a basic RAG flow with loader → splitter → embeddings → vector store → retriever → LLM
- Launching a pre-built ReAct or Conversational-ReAct agent with simple tools, if needed
- Using simple callbacks or tracing to observe token usage, latency, or cost
- Adding retries or exponential back-off in a lightweight way
- Building a CLI, notebook, or minimal API prototype
- Environment setup with virtualenv or poetry, dotenv or pydantic settings, and requirements.txt

### Out of scope and MUST NOT be primary requirements
- Advanced memory design
- Multi-vector retrieval
- Custom chain or custom agent framework development
- Security hardening as the main task
- Scalability engineering
- Complex evaluation frameworks
- Distributed systems or production infrastructure
- Heavy architecture work
- Fine-tuning models

## INSTRUCTIONS

### Nature of the Task
- Task must ask the candidate to implement a small feature from scratch or fix meaningful issues in an existing LangChain application.
- The task must be specific, narrow, and well-scoped for BASIC proficiency.
- The scenario must be realistic and business-oriented, not a toy example.
- The task should focus on one small local workflow using 2-3 connected concepts, such as:
  - prompt template + LLMChain + basic memory,
  - CSV or text loading + simple retrieval flow + answer generation,
  - fixing a broken RetrievalQA-style pipeline,
  - preserving session context across follow-up questions,
  - validating request input before invoking the chain,
  - handling missing files or missing records gracefully.
- The task must NOT depend on distributed systems design or heavy infrastructure.
- The task must NOT include hints in the question itself. Hints belong only in the dedicated "hints" field.
- The task should be completable within {minutes_range} minutes.

### BASIC proficiency calibration
For BASIC level, the task should combine only 2-3 concepts in a coherent workflow. Suitable task shapes include:
- fixing a prompt + memory flow so follow-up questions keep context,
- loading a small CSV or text corpus and using it as context for answers,
- repairing a simple vector-store-backed question-answer flow,
- validating request fields before running the chain,
- adding basic retries or error handling around model calls,
- returning a simple source-aware response from retrieved content.

The task should require practical debugging and small implementation decisions, but not architecture-heavy reasoning.

### Scenario selection
- You MUST use one of the provided real-world scenarios as the direct inspiration for the task.
- The generated business context, data shape, and user workflow should clearly resemble the selected scenario.
- Prefer scenarios involving straightforward internal knowledge lookup, FAQ assistance, course materials, support content, or similar small-document workflows when available.
- Vary the chosen scenario across generations.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, including official documentation, search engines, and AI tools.
- The task should still require practical reasoning and adaptation, not just copying boilerplate.
- The generated task should reward candidates who can understand a small codebase, connect ingestion to prompting or retrieval, and improve correctness and maintainability.

## Code Generation Instructions
Based on the real-world scenarios provided, create a LangChain task that:
- Draws inspiration from one selected scenario to determine the business context and document or data domain.
- Matches BASIC proficiency for LangChain.
- Tests practical skills with local data, simple chain composition, memory or retrieval, and basic validation.
- Uses a lightweight local project structure suitable for the LLM_FRAMEWORK category.
- Avoids Docker and heavy infrastructure.
- Can be completed within {minutes_range} minutes.
- Uses a different scenario each time to ensure variety.

## Infrastructure Requirements for LLM_FRAMEWORK category
- MUST be a Python project using LangChain.
- MUST include requirements.txt.
- MUST include runnable source files.
- MAY include one lightweight interface such as:
  - a CLI script, or
  - a minimal FastAPI or Flask endpoint, or
  - a simple notebook-style script.
- MUST keep the setup lightweight and local.
- MUST use local sample documents or data files included in the repository.
- MAY use a lightweight local vector store on disk if retrieval is part of the scenario.
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
- Keep testing lightweight: 1-2 simple tests or verification scaffolding is enough for BASIC level.

## REQUIRED OUTPUT JSON STRUCTURE

{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Follow-Up Context for Course Materials Assistant', 'Repair CSV-Based Knowledge Lookup for Support Team', 'Improve Session-Aware Q&A for Internal Training Content'.",
  "question": "Short description of the scenario and the specific ask from the candidate — what needs to be fixed or implemented.",
  "code_files": {
    "README.md": "Candidate-facing README following the structure below",
    ".gitignore": "Comprehensive Python exclusions including virtualenvs, caches, logs, local vector store artifacts, and .env",
    "requirements.txt": "Python dependencies including langchain and any lightweight supporting libraries",
    ".env.example": "Example environment variables if needed, without real secrets",
    "app/main.py": "Application entry point or request handler",
    "app/config.py": "Configuration values and paths",
    "app/pipeline.py": "LangChain pipeline or chain wrapper",
    "app/loaders.py": "Data loading module for CSV, text, or similar local files",
    "data/sample_data_file": "Scenario-specific local data such as CSV, JSON, or markdown",
    "tests/test_app.py": "1-2 lightweight tests or verification scaffolding",
    "additional_files_as_needed": "Any other minimal files needed for the task"
  },
  "outcomes": "Bullet-point list in simple language. One bullet MUST explicitly state: 'Write production-level clean code with best practices including proper naming conventions, exception handling, logging, and clear project structure.'",
  "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the implementation or fix goal, and (3) the expected outcome emphasizing correctness, response quality, and maintainability.",
  "pre_requisites": "Bullet-point list of tools, libraries, environment setup, and knowledge required. Include Python 3.10+, pip, virtual environment usage, and LangChain concepts such as prompt templates, simple chains, memory, loaders, or basic retrieval.",
  "answer": "High-level solution approach describing the intended flow at a non-code level.",
  "hints": "A single line hint that gently nudges the candidate toward a good approach without giving away the implementation.",
  "definitions": {
    "PromptTemplate": "A LangChain template used to format dynamic input into a prompt before sending it to a model",
    "LLMChain": "A simple LangChain chain that combines a prompt and a language model into one callable workflow",
    "ConversationBufferMemory": "A memory component that stores prior messages so follow-up questions can use earlier context",
    "Document Loader": "A component that reads local files such as CSV, text, or JSON and turns them into LangChain documents",
    "Vector Store": "A storage layer for embeddings that supports similarity search over document chunks"
  }
}

## Code file requirements
- More than one file may be generated, but all must be listed correctly in the JSON structure.
- Code should follow Python PEP 8 guidelines.
- Use a clear, readable project structure.
- The generated code files MUST NOT contain the implementation for the core logic of the task.
- The core prompt wiring, memory behavior, retrieval flow, validation logic, or response shaping that the candidate must complete should be left empty or minimally stubbed.
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
- local persisted vector store directories such as storage/, indexes/, chroma_db/, or faiss_index/

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
- Include expectations around correctness, context retention, source usage, validation, and robustness where relevant.

### How to Verify
- 3-5 bullets maximum.
- Describe observable behaviors to validate.
- Include checks such as whether local data is loaded correctly, whether answers use the provided context, whether follow-up questions preserve session context when required, whether invalid input is handled gracefully, and whether lightweight tests pass.
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
3. Use Python 3.10+ and current LangChain conventions.
4. Keep the project local and lightweight for the LLM_FRAMEWORK category.
5. Include local sample data and lightweight verification.
6. Do not require advanced evaluation, custom retrievers, multi-vector retrieval, or custom agent development.
7. Keep secrets out of version control.
8. The task must be completable within {minutes_range} minutes.
9. The title must be different from the name and use plain English.
10. The generated task must reflect the selected real-world scenario closely.
11. Prefer realistic work items such as fixing a broken prompt-and-memory flow, restoring simple retrieval over local files, validating request input, or making a small LangChain prototype more robust.
"""

PROMPT_REGISTRY = {
    "Langchain (BASIC)": [
        PROMPT_LANGCHAIN_BASIC_CONTEXT,
        PROMPT_LANGCHAIN_BASIC_INPUT_AND_ASK,
        PROMPT_LANGCHAIN_BASIC_INSTRUCTIONS,
    ],
}