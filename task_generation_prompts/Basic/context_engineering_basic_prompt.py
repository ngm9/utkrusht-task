# task_generation_prompts/Basic/context_engineering_basic_prompt.py
#
# CURATED task-generation prompt module for Context Engineering BUILD-IT tasks.
# Competency: "Context Engineering"  ·  Proficiency: BASIC
#
# DROP-IN for infra/utils.py::_build_prompt_registry. The loader filesystem-walks
# task_generation_prompts/<Level>/<slug>.py and calls registry.update(PROMPT_REGISTRY).
# Contract (do NOT change without updating the loader):
#   * Export a top-level dict named exactly  PROMPT_REGISTRY.
#   * Key it exactly "Context Engineering (BASIC)" — the
#     "<name> (<PROFICIENCY-UPPER>)" string get_task_prompt_by_technology_stack builds.
#   * Value is a LIST of prompt strings, replayed as sequential user turns.
#   * The ONLY legal {placeholders} are the six fmt_args keys:
#       organization_background, role_context, minutes_range,
#       competencies, real_world_task_scenarios, question_prompt
#     EVERY other literal brace is doubled ({{ }}) so str.format() survives.

PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_CONTEXT_ENGINEERING_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Context Engineering assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

{question_prompt}

SCENARIO FOCUS:
The candidate is given a small, partially-built context pipeline for an AI feature — the specific feature, domain, and data type MUST come from the chosen real-world scenario above. Do not default to any one domain. The pipeline could be:
  - A RAG (Retrieval-Augmented Generation) pipeline that retrieves relevant document chunks and injects them into a prompt before calling the LLM
  - A multi-turn chatbot that needs to manage conversation history within a token budget
  - A prompt-assembly system that combines multiple context sources (system instructions, retrieved knowledge, user state) into a single LLM call
  - A document-ingestion pipeline that chunks, embeds, and stores text for later retrieval

The starter code has one or two FUNCTIONAL issues in the context assembly layer — e.g. conversation history that grows unbounded and truncates the document context, retrieved chunks that are injected in the wrong order, a chunking strategy that breaks sentences mid-way, a prompt template that loses the grounding instruction when combined with retrieved context, or a retrieval call that returns zero results due to a misconfigured similarity threshold.

The candidate must:
(a) Identify the root cause of the context issue (not just symptoms) by reading the code and the sample data
(b) Fix the issue so that the pipeline actually uses the provided context to ground the LLM's responses
(c) Verify the fix using the included sample data or lightweight test scaffolding

WHAT THIS TASK TESTS:
- Ability to read a small context pipeline and understand what flows into the LLM's context window
- Ability to identify a realistic context engineering bug (unbounded history, wrong chunk order, broken retrieval, prompt template that drops context)
- Ability to fix context assembly so retrieved or historical information is actually present in the prompt
- Understanding that context quality (what is IN the prompt) determines answer quality
- Practical awareness of token budgets — not all context can always fit
- Ability to verify the fix with sample data or a simple test

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Identifies the specific line or block causing the context failure — not just "the prompting is wrong"
- Fix is targeted and minimal: adds or adjusts the context assembly logic without rewriting unrelated code
- After the fix, the pipeline's LLM call actually receives the relevant chunk/history in the prompt
- Shows awareness of WHY the issue causes bad answers (e.g., "without the retrieved chunk the model hallucinates", "history overflow pushes the system instruction out of the context window")
- Verification is grounded in the sample data, not just "it looks correct now"

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from ONE of the real-world scenarios above to set the business domain, data type, and pipeline shape. Do not substitute a different domain.
- Across multiple generations, vary which scenario and pipeline shape you pick — RAG, multi-turn history, multi-source prompt assembly, ingestion chunking. Never bias toward one shape.
- The task must be completable within {minutes_range} minutes for a BASIC proficiency Context Engineer.
- The starter code must be valid Python that runs as-is (possibly with wrong outputs). The bug must be in the context assembly layer (chunking, retrieval, prompt construction, history management) — not a syntax error or a missing import.
- The bug must be plausible and non-obvious — something a junior engineer could ship accidentally. Do NOT make it cartoonishly broken or annotate it with a comment that says "this is wrong".
- Use one of these FOUR pipeline shapes — let the scenario drive the choice:
    SHAPE 1 — RAG FIX: a retriever returns documents but the prompt template does not include them in the final LLM call, OR the similarity threshold is set so high that results are always empty.
    SHAPE 2 — HISTORY OVERFLOW: a multi-turn chatbot appends every prior turn to the prompt without any truncation; older turns push out the system prompt or the retrieved knowledge chunk.
    SHAPE 3 — CONTEXT ORDER / STRUCTURE: retrieved chunks are injected in the wrong order (least relevant first) or the prompt structure puts the user query before the context block, causing the model to answer from parametric memory instead of the provided docs.
    SHAPE 4 — CHUNKING BREAK: a document is split at a fixed character count that slices mid-sentence or mid-table; the resulting chunks lack enough context to answer the query, even when retrieved correctly.
- Include 2-3 realistic sample documents or sample conversation turns in a data/ folder so the candidate can observe the bug without calling a real LLM.
- Do NOT include a rubric, hints file, or comments that say "fix this". Hints belong only in the dedicated `hints` field.

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the pipeline shape — RAG fix / history overflow / context order / chunking break — and what the candidate must fix.)
2. What will the starter code look like? (Describe the key files, where the context bug sits, and what observable symptom tells the candidate something is wrong.)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_CONTEXT_ENGINEERING_BASIC_INSTRUCTIONS = """
## GOAL
As a senior context engineer experienced in building LLM pipelines, you are generating a realistic work-item assessment that tests whether a candidate can read a small context pipeline, identify a realistic context engineering bug, and fix it so that the LLM actually receives the information it needs to answer correctly. The specific domain, data type, and pipeline shape come from the chosen real-world scenario. The task must feel like a real ticket — the kind a junior engineer picks up when an AI feature is returning hallucinated or unhelpful answers despite the fact that the team "definitely loaded the knowledge base".

## HARD SCOPE BOUNDARY
You MUST stay within the BASIC context engineering scope:
- Reading a small Python context pipeline (< 300 lines across all files the candidate must touch)
- Understanding how chunks, history turns, or multi-source context are assembled into a prompt string
- Fixing ONE plausible context assembly bug (chunking, retrieval injection, history truncation, prompt structure)
- Using a local vector store (FAISS or Chroma) or in-memory retrieval — NOT production-scale infrastructure
- Verifying the fix with sample data and/or a lightweight test (1-2 assertions)

### Out of scope — MUST NOT be primary requirements
- Implementing a full vector DB from scratch
- Fine-tuning or training models
- Advanced multi-hop retrieval or query decomposition
- Production deployment, scaling, or CI/CD
- Evaluation framework design
- Complex agent orchestration

## INSTRUCTIONS

### Nature of the Task
- The task presents a small, runnable Python project with a context assembly bug.
- The candidate must find the bug, fix it, and verify the fix.
- The project must be scoped to ONE pipeline shape (RAG fix, history overflow, context order/structure, or chunking break) — chosen from the scenario.
- The starter code must run as-is (possibly producing wrong output). There must be no syntax errors or missing imports.
- The bug lives in ONE specific function or block in the context assembly layer.
- Sample data (2-3 documents or conversation turns) must be included so the bug is observable without a live LLM call.

### BASIC Proficiency Calibration
A BASIC-level candidate should:
- Understand that the LLM's answer quality depends on what is in its context window
- Be able to read a small context assembly function and trace what ends up in the prompt
- Know the difference between chunking (splitting docs for indexing) and retrieval (finding relevant chunks)
- Know that conversation history must be bounded to avoid overflowing the context window
- Be able to run a simple similarity search and inspect what comes back
- NOT be expected to design an evaluation framework, optimize embedding models, or build multi-hop retrieval

The bug fix should require 10-20 lines of code changes, not a full rewrite. Suitable bug patterns:
- `prompt = f"{{system_instruction}}\n\nUser: {{user_query}}"` — retrieved docs never added to prompt
- `history.append(turn); prompt = "\n".join(history)` — no truncation, history grows without bound
- Chunks assembled as `sorted(chunks)` by ID (alphabetical) instead of by relevance score
- `text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)` — chunks too small / overlap=0 breaks sentences

### Scenario Selection
- You MUST use one of the provided real-world scenarios as direct inspiration for the business domain and data type.
- The pipeline shape (RAG / history / order / chunking) should feel natural for the chosen scenario.
- Vary the chosen scenario and pipeline shape across generations.

## AI AND EXTERNAL RESOURCE POLICY
- Candidates are permitted and encouraged to use external resources, documentation, and AI tools.
- The task should reward practical understanding of context assembly — not memorization of API names.

## Code Generation Instructions
Based on the real-world scenarios provided, create a Context Engineering task that:
- Draws inspiration from one selected scenario (business domain, document type, query type).
- Uses ONE pipeline shape from the four shapes above.
- Keeps the project lightweight and local — FAISS or Chroma for vector search, local text files or JSON for sample data.
- Is completable within {minutes_range} minutes.
- Tests practical context engineering judgment: what flows into the LLM's context window.

## Infrastructure Requirements
- MUST be a Python project.
- MUST include requirements.txt.
- MUST include runnable Python source files.
- MUST include sample data files (2-3 documents or turns) in a data/ folder.
- MUST keep the setup lightweight and local (no Docker, no cloud dependencies).
- MUST use a local vector store (FAISS or Chroma) OR in-memory retrieval — configurable via .env if needed.
- API key for the LLM provider (OpenAI) handled via .env.example — should NOT be required to observe the bug (use a mock or stub for the LLM call in tests).

## Starter Code Instructions
- The starter code must be valid and executable.
- The core context assembly bug must be present but not annotated.
- Do NOT include TODO comments, placeholder hints, or comments that say "this is the issue".
- Do NOT include solution code.
- Include 1-2 lightweight test stubs that a candidate can use to verify their fix (e.g., assert that the prompt string contains the expected chunk text after the fix).
- Keep the codebase small: the candidate should be able to read every file in < 10 minutes.

## REQUIRED OUTPUT JSON STRUCTURE

{{
  "name": "task-name-in-kebab-case",
  "title": "Human-readable task title in '<action verb> <subject>' format, 50-80 characters. Examples: 'Fix Context Injection for Support Knowledge Base', 'Repair History Overflow in Customer Chatbot', 'Fix Chunk Ordering in Document Q&A Pipeline'.",
  "question": "Short description of the scenario and the specific ask — what is wrong, what the candidate must fix, and how to verify the fix. Frame it as a real work item (Slack message, Jira ticket) from an eng or ops colleague. Do NOT reveal the root cause. 3-5 sentences.",
  "code_files": {{
    "README.md": "Candidate-facing README. MUST contain: Task Overview (2-3 sentences: business scenario + current symptom), Helpful Tips (3-4 action bullets — guide discovery, do NOT reveal the bug), Objectives (3-5 bullets: what should work after the fix), How to Verify (3-5 observable checks the candidate can run). Do NOT include setup commands, solution steps, or code snippets.",
    ".gitignore": "Standard Python gitignore including venv, .env, __pycache__, *.pyc, chroma_db/, faiss_index/, *.log",
    "requirements.txt": "Python dependencies: openai (or anthropic), langchain or llama-index if used, faiss-cpu or chromadb, python-dotenv, pytest",
    ".env.example": "Example environment variables — LLM API key only. No real secrets.",
    "app/pipeline.py": "Context assembly pipeline — this is where the bug lives. Must be valid Python. The bug is in the context assembly function (chunk injection, history management, prompt construction, or chunk ordering). Do NOT annotate the bug.",
    "app/retriever.py": "Retrieval module — similarity search over the local vector store or in-memory index. Valid Python.",
    "app/main.py": "Entry point — wires pipeline + retriever and runs a sample query against the sample data. Runnable.",
    "data/sample_docs.txt": "2-3 realistic sample documents for the chosen scenario, in plain text or JSON. Long enough that chunking or retrieval is non-trivial.",
    "tests/test_pipeline.py": "1-2 lightweight test stubs that check whether the assembled prompt contains the expected context. The tests should FAIL before the fix and PASS after."
  }},
  "outcomes": "Bullet-point list in plain language. One bullet MUST explicitly state: 'Write clean, targeted code changes — fix the context assembly bug without rewriting unrelated logic.' Include: correctly grounded LLM responses using the provided sample data, prompt string contains the expected chunk or history, lightweight tests pass, code is readable and follows Python conventions.",
  "short_overview": "Bullet-point list in plain language: (1) the business domain and AI feature, (2) the pipeline shape and where the bug is, (3) what the candidate must do to fix it and verify the fix.",
  "pre_requisites": "Exactly 2–3 concise bullets. Each covers ONE item: (1) runtime/toolchain required, (2) repo/environment setup, (3) key domain knowledge if non-obvious. Each bullet ≤ 120 chars. No padding, no sub-lists.",
  "answer": "High-level solution approach at a non-code level. Name: (1) the specific bug (which line/block, what it does wrong), (2) the fix (what change makes the context appear in the prompt), (3) how to verify (what the test checks or what the prompt string should contain after the fix). Do NOT write full solution code here.",
  "hints": "A single gentle nudge that points the candidate toward the right layer (e.g., 'Print the full prompt string that gets sent to the LLM and check whether the retrieved chunks actually appear in it.').",
  "definitions": {{
    "Context Window": "The maximum number of tokens an LLM can process in one call — everything the model sees (system prompt, retrieved docs, conversation history, user query) must fit inside it",
    "RAG (Retrieval-Augmented Generation)": "A pattern where relevant document chunks are retrieved from a knowledge base and injected into the LLM's prompt so the model answers from provided evidence rather than parametric memory",
    "Chunk": "A fixed-size or semantically meaningful piece of a document, produced by splitting long text so it can be embedded and retrieved individually",
    "Context Assembly": "The step in an LLM pipeline that combines system instructions, retrieved chunks, conversation history, and the user query into the final prompt string sent to the model",
    "Similarity Search": "A retrieval operation that finds the stored chunks whose embeddings are closest (most semantically similar) to the query embedding, returning the top-k matches",
    "History Truncation": "A strategy that limits conversation history length — typically keeping the N most recent turns or summarizing older ones — so that earlier turns do not push essential context out of the window"
  }}
}}

## Code File Requirements
- All files must be listed and populated in the JSON code_files dict.
- Python files must follow PEP 8.
- The starter code must be valid and runnable but produce wrong or empty outputs due to the context bug.
- Do NOT reveal the fix in comments, TODO markers, or docstrings.
- Keep each file small enough for a BASIC candidate to read in under 3 minutes.
- tests/test_pipeline.py must fail before the fix and pass after.

## README.md Structure
The README must contain exactly four sections:
- **Task Overview**: 2-3 sentences — the business scenario and the current symptom (e.g., "the chatbot ignores the knowledge base and gives generic answers").
- **Helpful Tips**: 3-4 action bullets — guide discovery without revealing the root cause. Use words like "Review", "Inspect", "Consider", "Trace".
- **Objectives**: 3-5 bullets — what should be working after the fix (observable outcomes, not implementation steps).
- **How to Verify**: 3-5 observable checks — what the candidate can run or inspect to confirm the fix works.

Do NOT include: setup commands, solution steps, code snippets, or architecture deep-dives.

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown fences, no explanations. Emit the raw JSON object starting with {{ and ending with }}.
2. name must be kebab-case, 3-6 words.
3. title must be plain English, verb-first, 50-80 characters.
4. The bug must be in the context assembly layer — NOT a syntax error, import error, or unrelated logic.
5. Starter code must be runnable Python 3.10+.
6. Include sample data realistic enough that the bug is observable without a live LLM call.
7. tests/test_pipeline.py must fail before the fix and pass after.
8. Do NOT reveal the bug in comments, the README, or the question field.
9. Keep the total candidate-visible codebase small: < 300 lines across files the candidate must read and touch.
10. Use one pipeline shape only — RAG fix, history overflow, context order/structure, or chunking break. Do not mix shapes in a single task.
11. The task must be completable within {minutes_range} minutes.
12. Domain, data type, and pipeline shape all come from the chosen real-world scenario — vary across generations.
"""

PROMPT_REGISTRY = {
    "Context Engineering (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_CONTEXT_ENGINEERING_BASIC_INPUT_AND_ASK,
        PROMPT_CONTEXT_ENGINEERING_BASIC_INSTRUCTIONS,
    ]
}
