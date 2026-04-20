# Autonomous Task Generation: V2 Research & Implementation Guide

> **Status**: Research complete. Extends [v1 research](./autonomous-task-generation-agents.md) with tool evaluation, verification architecture, and concrete implementation plan.
> **Date**: April 2026
> **Prerequisite**: Read [v1](./autonomous-task-generation-agents.md) first — this document assumes familiarity with the three-layer architecture (Intake → Generation Graph → Verification), framework trade-offs, and phased roadmap established there.

---

## 1. What V1 Established

V1 answered the strategic questions:

- **Why automate**: CLI-driven generation doesn't scale past 10 tasks/week. The combinatorial space (6 task types × 15+ tech stacks × 3 proficiencies × N domains) is too large for static prompts.
- **Architecture**: Three layers — Intake Agent, Generation Graph, Verification Tools — connected by a deterministic orchestrator.
- **Key insight**: Prompts become domain knowledge the agent loads as context, not fixed scripts. Verification tools (not LLM-checking-LLM) are the quality differentiator.
- **Framework choice**: Deferred pending model comparison. Anthropic Agent SDK, Pydantic AI + Portkey, and raw API + Portkey remained viable.
- **Roadmap**: Four phases from POC to customer-facing API.

V1 left open:

1. Which framework to use (and why)
2. Which specific verification tools to build/adopt
3. How to replace `evals.py` with structured evaluation
4. How to decompose 80+ prompt files into retrievable knowledge
5. How to deduplicate across generated tasks
6. How to validate that generated tasks are actually solvable
7. How the Coordinator Agent works (cross-task review, stochastic judgment)

This document answers all of these.

---

## 2. Current System: Module-by-Module Analysis

Before designing agents, we mapped every manual step in the current pipeline. This is the tactical bridge V1 was missing.

### 2.1 The Four-Command Pipeline

```
Command 1: python -m generate_input_files --name "Golang" --proficiency BASIC
    → Queries Supabase for competencies
    → LLM generates role_context + questions_prompt
    → Writes competency.json + background.json

Command 2: python -m scenario_generator --competency-file ... --count 6
    → LLM generates N real-world scenarios
    → Validates each (length, structure, dedup against existing)
    → Writes task_scenarios.json

Command 3: python multiagent.py generate-tasks -c ... -b ... -s ...
    → Reads 3 input JSONs
    → Selects prompt from PROMPT_REGISTRY by competency name + proficiency
    → Calls OpenAI (gpt-5.1 via Portkey) with 3-step conversation
    → Parses JSON response → runs task eval + code eval (gpt-5-nano)
    → Creates GitHub template repo + answer repo + gist
    → Inserts to Supabase

Command 4: python multiagent.py deploy-task --task-id UUID
    → Downloads files from GitHub
    → Uploads to DigitalOcean droplet via SSH/SFTP
    → Executes run.sh
    → Updates is_deployed in Supabase
```

### 2.2 Module Responsibilities

| Module | What It Does | Human Decisions Required |
|--------|-------------|--------------------------|
| `generate_input_files/` | Fetches competencies from Supabase, LLM generates `role_context` + `questions_prompt`, writes JSON files | Human picks tech name + proficiency level |
| `scenario_generator/` | LLM generates N scenarios, validates each (length per proficiency, structure, dedup), saves JSON | Human picks count, append vs overwrite |
| `task_generation_prompts/` | 80+ hand-crafted prompt files organized by `{Level}/{Tech}_prompt.py`. Each exports `PROMPT_REGISTRY` dict with 3-step conversation (Context → Instructions → Ask) | Human authored all prompts manually |
| `multiagent.py` | Orchestrator: reads inputs → selects prompt → calls LLM → parses → evals → GitHub → Supabase | Human provides 3 file paths, manually retries on eval failure |
| `utils.py` | JSON parsing, prompt lookup from registry, LLM API calls via Portkey, gist creation, file I/O | — |
| `evals.py` | Two LLM evals: task eval (difficulty, realism, time) + code eval (structure, no solution leakage). Uses `gpt-5-nano`. `MAX_EVAL_RETRIES=2` | Human retries if eval fails |
| `schemas.py` | JSON schemas for structured outputs (answer code response + eval response) | — |
| `github_utils.py` | Creates template repos (private, `is_template=True`), answer repos (public), batch file uploads | — |
| `gist_manager.py` | Syncs gists between prod/dev, creates missing gists, mirrors `is_enabled` flags | Human runs CLI commands |
| `droplet_utils.py` | SSH/SFTP to DigitalOcean, auto-selects droplet with 0 running containers | Human provides IP or lets it auto-pick |
| `pr_review_flow/` | Separate pipeline for PR review tasks — different prompts, evals, GitHub structure | Same manual steps as standard flow |
| `non_tech_flow/` | Separate pipeline for non-technical tasks (Sales, HR) — no code generation | Same manual steps |

### 2.3 Every Manual Decision That Agents Must Replace

| # | Current Manual Step | Agent That Replaces It |
|---|--------------------|-----------------------|
| 1 | Human decides which tech + proficiency to generate | Intake Agent parses recruiter request |
| 2 | Human runs `generate_input_files` CLI | Orchestrator fetches from Supabase directly |
| 3 | Human decides scenario count | Coordinator determines count based on batch size + diversity needs |
| 4 | Human runs `scenario_generator` CLI | Scenario Agent generates inline |
| 5 | Human selects prompt file via `PROMPT_REGISTRY` | Generator Agent loads decomposed guidelines from knowledge base |
| 6 | Human provides 3 file paths to `generate-tasks` | Orchestrator passes structured data between agents |
| 7 | Human retries on eval failure | Generator self-corrects with tool feedback; Coordinator routes eval feedback |
| 8 | Human checks if repos were created | Publish Agent handles deterministically with error recovery |
| 9 | Human runs `gist_manager.py` to sync | Publish Agent syncs automatically |
| 10 | Human decides deployment target | Deploy Agent auto-selects droplet |
| 11 | Human verifies task quality | Coordinator does cross-review; Solver Agent tests solvability |
| 12 | Human checks for duplicate tasks | Dedup check via embeddings before generation |

### 2.4 Data Structures (Reference)

**Competency JSON** (input):
```json
[{
  "competency_id": "uuid",
  "name": "Golang",
  "proficiency": "BASIC",
  "scope": "What a developer at this level should know..."
}]
```

**Background JSON** (input):
```json
{
  "organization": {
    "organization_id": "uuid",
    "organization_name": "Utkrusht",
    "organization_background": "Company description..."
  },
  "role_context": "What the candidate is expected to do...",
  "questions_prompt": "Assessment rubric...",
  "yoe": "1-2"
}
```

**Scenarios JSON** (input):
```json
{
  "Java (BASIC), Kafka (BASIC)": [
    "Scenario 1: A microservice team at Spotify needs...",
    "Scenario 2: Netflix's content delivery system..."
  ]
}
```

**Task Object** (output, stored in Supabase):
```json
{
  "task_id": "uuid",
  "is_deployed": false,
  "is_shared_infra_required": true,
  "criterias": [{"competency_id": "uuid", "proficiency": "BASIC", "name": "Java"}],
  "task_blob": {
    "title": "task name",
    "question": "full problem statement",
    "definitions": {},
    "hints": "single-line hint",
    "resources": {"github_repo": "url", "github_gist": "url"},
    "outcomes": [],
    "short_overview": []
  },
  "eval_info": {
    "task_eval": {"pass": true, "validated_criteria": []},
    "code_eval": {"pass": true, "validated_criteria": []}
  },
  "solutions": {
    "steps": [],
    "answer_repo": "url"
  }
}
```

### 2.5 Prompt Architecture (Current)

Each prompt file in `task_generation_prompts/{Level}/{Tech}_prompt.py` exports a `PROMPT_REGISTRY` with a 3-step conversation:

**Step 1 — Context**: Sets up company background, role responsibilities. Asks LLM to confirm understanding.

**Step 2 — Instructions** (~200-300 lines): Defines task complexity, code structure, required JSON fields, README structure. Contains the deep domain knowledge ("no comments in code", "README must not include setup commands", project structure conventions).

**Step 3 — Ask**: Injects real-world scenarios, asks LLM to select one and generate the task.

The proficiency-level guardrails embedded in these prompts:

| Proficiency | Time | Concepts | Max Scenario Words | Forbidden Topics |
|-------------|------|----------|-------------------|-----------------|
| Beginner | 20-30 min | 1 concept | 100 | async, auth, caching, design patterns |
| Basic | 20-30 min | 2-3 concepts | 150 | microservices, perf optimization, advanced ORM |
| Intermediate | 30-40 min | 4-5 concepts | 250 | (allowed: API design, caching, async, patterns) |

---

## 3. Framework Decision: Pydantic AI + Portkey

V1 left the framework choice open pending model comparison. After evaluating the full landscape, we recommend **Pydantic AI + Portkey** for all phases.

### 3.1 Framework Landscape (April 2026)

| Framework | Stars | Multi-Provider | Parallel Agents | State Mgmt | Assessment |
|-----------|-------|---------------|-----------------|------------|------------|
| **Pydantic AI** | 16.4k | Yes (OpenAI, Anthropic, Gemini, Ollama via configurable base URL) | Yes (graph API beta: broadcast/map fan-out) | Yes (DBOS durable execution) | **Selected.** Best fit for existing codebase |
| **LangGraph** | 29.4k | Yes (via LangChain adapters) | Yes (parallel branches) | Yes (built-in checkpointing) | Powerful but heavy. 60+ lines where Pydantic AI does it in 20. Tight LangChain coupling |
| **OpenAI Agents SDK** | 20.9k | No — OpenAI only | Yes (sessions) | Yes | Locked to OpenAI. Cannot use Claude for cross-provider eval |
| **Claude Agent SDK** | 6.4k | No — Claude only | Yes (sub-agent isolation) | Partial | Best sub-agent isolation but single-provider |
| **AutoGen / MS Agent Framework** | 57.1k | Yes | Yes (event-driven) | Yes | Fragmented ecosystem (v0.2 vs v0.4 vs AG2 vs 1.0). Too much churn |
| **CrewAI** | 46k | Yes (via LiteLLM) | Yes | Limited | Role-playing abstraction doesn't fit structured pipeline. No checkpointing |
| **Burr** | 2.0k | Yes | Limited (sequential) | Excellent (state snapshots, replay) | Great state management but sequential-only |
| **magentic** | 2.4k | Yes | No | No | Not an agent framework — `@prompt` decorator only. Useful as building block |

### 3.2 Why Pydantic AI

1. **Portkey compatibility**: We already route all LLM calls through Portkey (`PORTKEY_GATEWAY_URL`). Pydantic AI supports configurable base URLs — point it at Portkey and multi-provider works.

2. **Type-safe structured outputs**: Our `schemas.py` already defines JSON schemas for task output and eval response. Pydantic AI's `result_type` replaces these naturally with Pydantic models, getting validation for free.

3. **Graph API for parallel generation**: The beta graph API provides `broadcast()` and `map()` primitives for fan-out — exactly what we need to run 5 Generator Agents simultaneously.

4. **DBOS durable execution**: Handles the retry loops currently in `evals.py` with checkpointing. If GitHub API times out at step 6, resume from step 6 (not step 1).

5. **Cross-provider evaluation**: Use GPT-5.1 for generation (known-good) and Claude for evaluation (different blind spots). Just change the model string.

6. **Migration cost**: If Pydantic AI turns out to be wrong, the migration cost is ~50 lines of agent loop code. Tools are Python functions (portable), domain knowledge is in files (portable), schemas are Pydantic models (already Pydantic).

### 3.3 What We Ruled Out (and Why)

**LangGraph**: Too heavy for our use case. We don't need LangSmith observability, LangChain's abstraction layers, or graph-level checkpointing (Prefect handles that at the workflow level). The 60-line boilerplate for simple operations is a maintenance burden.

**Vendor SDKs (OpenAI Agents SDK, Claude Agent SDK)**: Single-provider lock-in. Our cross-provider eval strategy (GPT generates, Claude evaluates) requires multi-provider support. These SDKs are excellent for their respective providers but can't do both.

**CrewAI**: The role/goal/backstory abstraction is designed for "agents debating" — our agents have structured inputs and outputs, not open-ended conversations. No checkpointing means long-running generations can't recover from failures.

**AutoGen**: The ecosystem fragmentation (AutoGen 0.2 vs 0.4 vs AG2 community fork vs MS Agent Framework 1.0) means we'd be betting on which version survives. Too risky for production infrastructure.

---

## 4. Workflow Durability: Prefect

The current pipeline has no checkpointing. A GitHub API timeout at step 6 of 8 means restarting from scratch (and burning LLM tokens again). We need durable execution.

### 4.1 Options Evaluated

| Tool | Stars | What It Does | Assessment |
|------|-------|-------------|------------|
| **Prefect** | 22.2k | Python-native `@flow`/`@task` decorators. Retries, caching, scheduling, dashboard UI | **Selected for Phase 1-2.** Lowest friction for Python. Decorator-based — minimal refactoring |
| **Temporal** | 19.6k | Industrial-grade durable execution. Workflows survive crashes, resume from checkpoint | More powerful but requires running a separate Temporal server. Evaluate for Phase 3+ |
| **Hatchet** | 6.8k | AI-agent-specific checkpointing and recovery | Newer, less proven. YC-backed. Watch |
| **Inngest** | 5.2k | Event-driven workflow orchestration | Good for "Supabase event → auto-generate tasks" triggers. Phase 4 |

### 4.2 How Prefect Wraps Our Pipeline

```python
# Current: imperative, no recovery
def create_task(competency, background, scenarios):
    task_data = generate_task_with_code(...)  # If this fails at step 6...
    eval_info = run_evaluations(...)           # ...you lose everything
    repo_url = create_github_repo(...)
    insert_to_supabase(...)

# With Prefect: each step is checkpointed, cached, retryable
from prefect import flow, task

@task(retries=2, cache_key_fn=task_input_hash)
def generate_task(competency, background, scenario):
    return generate_task_with_code(...)

@task(retries=1)
def evaluate_task(task_data):
    return run_evaluations(...)

@task(retries=3, retry_delay_seconds=5)
def publish_to_github(task_data, eval_info):
    return create_github_repo(...)

@task(retries=2)
def store_in_supabase(task_data, eval_info, repo_url):
    return insert_to_supabase(...)

@flow(name="create-task")
def create_task_flow(competency, background, scenario):
    task_data = generate_task(competency, background, scenario)
    eval_info = evaluate_task(task_data)
    repo_url = publish_to_github(task_data, eval_info)
    store_in_supabase(task_data, eval_info, repo_url)
```

Benefits:
- **Caching**: If `generate_task` already succeeded with these inputs, skip it on retry
- **Retries**: GitHub API timeout? Retry 3 times with 5-second delay
- **Observability**: Prefect UI dashboard shows pipeline status, failures, timing
- **Scheduling**: Can schedule batch generation runs (e.g., "generate 20 tasks every Monday")

---

## 5. Verification Tools: The Quality Differentiator

V1 established that verification tools (not LLM-checking-LLM) are the biggest quality improvement. This section specifies exactly which tools, how they integrate, and when to run them.

### 5.1 Verification Tiers

**Tier 1: Fast Pass** (<1 second per file) — Run on every generated artifact.

| Tool | What It Validates | Languages | Install | Integration |
|------|------------------|-----------|---------|-------------|
| **tree-sitter** + `tree-sitter-language-pack` | Syntax correctness via AST parsing. Reports errors via `has_error` on root node | 173 languages: Go, Java, Python, JS, TS, SQL, YAML, JSON, HTML, CSS, Rust, Ruby, Bash, HCL, TOML | `pip install tree-sitter tree-sitter-language-pack` | 3 lines of code per file |
| **Python `ast`** | Python-specific AST parsing with exact `SyntaxError` messages and line numbers. Can extract function/class names for structural validation | Python only | Built-in | `ast.parse(code)` raises `SyntaxError` |
| **markdown-it-py** | README section validation. Parses markdown into tokens, checks for required sections (Task Overview, Objectives, How to Verify, Helpful Tips) | Markdown | `pip install markdown-it-py` | Parse tokens, filter headings |
| **Pydantic models** | Task JSON schema validation. Type checking, required fields, enum values | JSON | Already installed (v2.12.5) | Define `TaskOutput(BaseModel)` |
| **hadolint** | Dockerfile syntax + best practices (missing `HEALTHCHECK`, `apt-get` without `--no-install-recommends`) | Dockerfile | Binary download or Docker image | `subprocess.run(["hadolint", "--format", "json", ...])` |
| **yamllint** | YAML syntax + style validation | YAML | `pip install yamllint` | `subprocess.run(["yamllint", ...])` |

tree-sitter integration example:
```python
from tree_sitter_language_pack import get_parser

def verify_syntax(language: str, code: str) -> dict:
    """Returns {"valid": bool, "errors": list[str]}"""
    parser = get_parser(language)
    tree = parser.parse(code.encode())
    if tree.root_node.has_error:
        errors = [node for node in _walk(tree.root_node) if node.type == "ERROR"]
        return {"valid": False, "errors": [f"Syntax error at line {e.start_point[0]+1}" for e in errors]}
    return {"valid": True, "errors": []}
```

**Note**: tree-sitter's Dockerfile grammar reports false positives on valid `COPY . .` instructions. Use hadolint for Dockerfiles instead.

**Tier 2: Medium Pass** (5-30 seconds) — Run after Tier 1 passes.

| Tool | What It Validates | Languages | Install | Integration |
|------|------------------|-----------|---------|-------------|
| **lizard** | Code complexity: cyclomatic complexity, NLOC, token count, parameter count per function. Validates difficulty matches proficiency | 27 languages: Go, Java, Python, JS, TS, C/C++, Rust, Ruby, PHP, Swift, Kotlin, Scala, SQL | `pip install lizard` | `lizard.analyze_file.analyze_source_code(filename, code)` |
| **docker compose config** | Validates docker-compose.yml structure without building | Docker Compose | Already installed (v5.1.1) | `subprocess.run(["docker", "compose", "config"])` |
| **Language-specific CLIs** | Deep validation: `go vet`, `tsc --noEmit`, `javac`, `node --check`, `python -m py_compile` | Per-language | Requires toolchains (run inside Docker) | `subprocess.run()` inside language-specific containers |
| **Cosine similarity** | Deduplication check against existing task embeddings | Text | OpenAI API (already have) or `sentence-transformers` | Embed task description, compare against corpus |

Complexity-to-difficulty mapping:

| Proficiency | Cyclomatic Complexity (answer code) | Halstead Effort | File Count |
|-------------|--------------------------------------|-----------------|------------|
| Beginner | 1-5 per function | < 5,000 | 1-3 |
| Basic | 3-10 per function | 5,000-20,000 | 3-6 |
| Intermediate | 5-20 per function | 20,000-100,000 | 5-10 |

**Tier 3: Deep Pass** (30-120 seconds) — Run on final candidates before publishing.

| Tool | What It Validates | Install | Integration |
|------|------------------|---------|-------------|
| **docker-py** | Build Docker images, run containers, capture output. Verifies code compiles and services start | `pip install docker` (v7.1.0) | `client.images.build()`, `client.containers.run()` with resource limits |
| **testcontainers** | Spin up real PostgreSQL, Kafka, Redis, MongoDB, K3s for integration testing answer code. 40+ pre-built modules | `pip install testcontainers` (v4.14.2) | `with PostgresContainer("postgres:16") as pg: ...` |
| **SWE-bench pattern** | "Fail-to-pass" verification: tests FAIL on starter code, tests PASS on answer code. Gold standard for task correctness | Docker-based, build ourselves | Generate tests → run against starter (must fail) → run against answer (must pass) |

### 5.2 The SWE-bench Verification Pattern

SWE-bench (4,708 stars, MIT license) established the gold standard for verifying that coding tasks are solvable. Their pattern:

1. Each task has a "before" state (buggy/incomplete code) and an "after" state (fixed/complete code)
2. A test suite runs against both states in Docker
3. Tests must FAIL on "before" and PASS on "after"
4. If tests pass on "before" → task doesn't actually require work (bad task)
5. If tests fail on "after" → solution doesn't work (bad solution)

We adapt this for our task generation:

```
Generated Task
    ├── starter_code (what the candidate gets)
    ├── answer_code (the solution)
    └── test_suite (generated or hand-specified)

Verification:
    1. Build Docker container with language toolchain
    2. Mount starter_code + test_suite → run tests → MUST FAIL
    3. Mount answer_code + test_suite → run tests → MUST PASS
    4. If both conditions met → task is valid
    5. If not → feed failure info back to Generator Agent for self-correction
```

### 5.3 Solver Agent: Empirical Difficulty Calibration

Beyond verification tools, we can use an AI agent as a "test candidate" to empirically validate difficulty. Inspired by:

- **SWE-agent** (19k stars, MIT): Takes a problem description, explores code, edits files, runs tests, iterates. NeurIPS 2024.
- **OpenHands** (71.3k stars): Agents interact via code editor + terminal + browser in a sandbox. Model-agnostic.
- **Aider** (43.4k stars, Apache-2.0): Edit → lint → test → auto-fix loop.

The pattern:

```
Solver Agent receives:
    - ONLY the starter code + README (NOT the answer)
    - A Docker sandbox with the language toolchain
    - Time limit matching the proficiency level

Solver Agent attempts:
    - Read README, understand the task
    - Explore starter code
    - Write solution code
    - Run tests (if provided)

Outcomes:
    - Solved in <5 min  → task may be too easy for proficiency level
    - Solved in 5-20 min → task is appropriately calibrated
    - Cannot solve       → task may be ambiguous, impossible, or poorly specified
    - Partially solved   → some requirements may be unclear

The time-to-solve and success/failure become data points
for difficulty calibration, independent of LLM eval scores.
```

This is the **stochastic judgment** layer — not just checking boxes, but empirically testing whether the task works as intended. The solver agent encounters the task the way a real candidate would, revealing issues that LLM evaluation alone cannot catch (ambiguous requirements, missing context, unsolvable constraints).

---

## 6. Evaluation Framework: Replacing `evals.py`

The current `evals.py` uses raw OpenAI calls with custom prompts. This works but has no structure, no CI integration, no regression detection, and no repeatability guarantees.

### 6.1 Evaluation Tools Evaluated

| Tool | Stars | What It Does | Assessment |
|------|-------|-------------|------------|
| **promptfoo** | 20.1k | YAML-driven eval framework. Define criteria, run in CI, get regression alerts. Used internally by OpenAI and Anthropic | **Best for CI integration.** Define task eval criteria in YAML, run `promptfoo eval` in pipeline |
| **DeepEval** | 14.8k | 60+ metrics, drops into pytest. Scored metrics with explanations | **Best for pytest integration.** Plugs directly into Python test workflow |
| **RAGAS** | 13.4k | RAG evaluation + synthetic test data generation | Synthetic data generation pattern useful for scenario generation |
| **Braintrust AutoEvals** | 861 | Pre-built LLM judge functions + CI/CD GitHub Action | Lightweight. Good for eval-on-PR-merge |
| **Evidently AI** | 7.4k | LLM observability + monitoring. 100+ metrics. Track quality drift | Phase 3+ production monitoring |

### 6.2 Recommended Approach

**Phase 1**: Use **DeepEval** for structured task evaluation within our Python pipeline:

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase

# Define evaluation criteria as metrics
difficulty_metric = GEval(
    name="Difficulty Appropriateness",
    criteria="The task difficulty matches the stated proficiency level...",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)

# Run evaluation
test_case = LLMTestCase(
    input=f"Generate a {proficiency} task for {tech_stack}",
    actual_output=generated_task_json,
)
difficulty_metric.measure(test_case)
# Returns: score (0-1), reason (explanation)
```

**Phase 2**: Add **promptfoo** for CI regression testing:

```yaml
# promptfoo.yaml
prompts:
  - task_generation_prompt.txt
providers:
  - openai:gpt-5.1-2025-11-13
tests:
  - vars:
      tech_stack: Golang
      proficiency: BASIC
    assert:
      - type: llm-rubric
        value: "Task is completable in 20-30 minutes by a developer with 1-2 years experience"
      - type: python
        value: "output.get('code_files', {}).get('README.md') is not None"
```

### 6.3 Cross-Provider Evaluation

V1 noted: "Using GPT to generate and Claude to evaluate (or vice versa) catches more errors than same-model self-evaluation."

Implementation:
- **Generator Agent**: GPT-5.1 via Portkey (known-good for task generation)
- **Eval Agent**: Claude Opus 4.6 via Portkey (different model family, different blind spots)
- **Eval Agent receives**: Only the generated task output + eval rubric. NOT the generation conversation history. Fresh context prevents bias from seeing the generator's reasoning.

### 6.4 Pairwise Comparison (LMSYS Pattern)

Instead of absolute scoring ("rate this task 1-10"), use pairwise comparison:

- Show two generated tasks side by side
- Ask: "Which task better tests {competency} at {proficiency} level?"
- Bradley-Terry model produces reliable rankings from pairwise votes

This produces better calibration data than absolute scores and is the foundation for the DSPy optimization dataset (Phase 3).

---

## 7. Deduplication: Semantic Similarity

### 7.1 Tools Evaluated

| Tool | Stars | What It Does | Assessment |
|------|-------|-------------|------------|
| **OpenAI `text-embedding-3-small`** | — | Generate embeddings via existing Portkey gateway. $0.02/1M tokens | **Start here.** Already have API key, zero new dependencies |
| **sentence-transformers** | — | Local embeddings (`all-MiniLM-L6-v2`, 80MB). Free, no API | Better for batch processing. Consider `microsoft/codebert-base` for code-specific embeddings |
| **SemHash** | 910 | Purpose-built semantic dedup. Configurable cosine threshold | **Best dedup library.** Lightweight, designed for this exact use case |
| **FAISS** | — | Efficient similarity search at scale | Only needed at 10K+ tasks. Numpy is fine for <1K |
| **Chroma** | 27.5k | Embedded vector DB. In-process Python | Good when also storing prompt fragments / knowledge base |
| **Qdrant** | 30.4k | Rust-based vector DB with filtering | Production-scale. Requires running a server |

### 7.2 Recommended Approach

**Phase 1**: OpenAI embeddings + numpy cosine similarity:

```python
from openai import OpenAI
import numpy as np

def check_duplicate(new_task_desc: str, existing_embeddings: np.ndarray, threshold: float = 0.90) -> bool:
    client = OpenAI(base_url=PORTKEY_GATEWAY_URL, ...)
    response = client.embeddings.create(model="text-embedding-3-small", input=new_task_desc)
    new_embedding = np.array(response.data[0].embedding)
    similarities = np.dot(existing_embeddings, new_embedding)
    return bool(np.any(similarities > threshold))
```

**Phase 2+**: Move to SemHash for configurable thresholds + Chroma for knowledge retrieval.

### 7.3 Similarity Thresholds

Based on published research and practical experience:

| Cosine Similarity | Interpretation | Action |
|-------------------|---------------|--------|
| > 0.95 | Near-identical / duplicate | Reject automatically |
| 0.85 - 0.95 | Very similar | Flag for Coordinator review |
| 0.70 - 0.85 | Related but distinct | Acceptable |
| < 0.70 | Sufficiently different | No concern |

Embed both the task description AND a concatenated code structure summary for better differentiation. Two tasks with similar descriptions but different code structures are not duplicates.

---

## 8. Knowledge Management: Decomposing 80+ Prompt Files

### 8.1 The Problem

We have 80+ monolithic prompt files, each 200-300 lines. Each encodes:
- Technology-specific project structure (Go uses `cmd/internal/pkg/`, Java uses `src/main/java/`)
- Proficiency-calibrated difficulty rules (what's forbidden at BASIC vs allowed at INTERMEDIATE)
- README requirements (what sections, what's forbidden)
- Code style rules (no comments, no TODOs)
- Task structure requirements (JSON fields, output format)

New combinations (e.g., "Rust + INTERMEDIATE + DEBUG") require writing a new prompt file from scratch, even though 80% of the content is shared with existing prompts.

### 8.2 Decomposition Strategy

Split monolithic prompts into composable, retrievable chunks:

```
Current:
    task_generation_prompts/Basic/GO_basic_prompt.py  (270 lines, everything in one file)

Decomposed:
    knowledge/
    ├── tech/
    │   ├── go/
    │   │   ├── project-structure.md      ("cmd/, internal/, pkg/, config/")
    │   │   ├── code-style.md             ("no comments, no TODOs, Go 1.18+ conventions")
    │   │   └── common-patterns.md        ("error handling, goroutines, channels")
    │   ├── java/
    │   │   ├── project-structure.md      ("src/main/java/, Maven/Gradle")
    │   │   └── code-style.md
    │   └── react/
    │       ├── project-structure.md
    │       └── code-style.md
    ├── proficiency/
    │   ├── beginner.md                   ("1 concept, 20-30 min, forbidden: async, auth")
    │   ├── basic.md                      ("2-3 concepts, 20-30 min, forbidden: microservices")
    │   └── intermediate.md              ("4-5 concepts, 30-40 min, allowed: caching, async")
    ├── task-type/
    │   ├── build.md                      ("extend a skeleton, test architectural judgment")
    │   ├── debug.md                      ("broken service, test hypothesis formation")
    │   ├── design-review.md             ("doc with intentional gaps, test systems thinking")
    │   ├── pr-review.md                 ("flawed PR, test pattern recognition")
    │   ├── manage-infra.md              ("misconfigurations, test operational knowledge")
    │   └── ux-critical-thinking.md      ("design critique, test product thinking")
    ├── shared/
    │   ├── readme-rules.md               ("no setup commands, no solutions, required sections")
    │   ├── output-schema.md             ("required JSON fields, code_files structure")
    │   └── code-rules.md               ("no comments, no TODOs, valid and compilable")
    └── examples/
        ├── go-basic-build-001.json       (rated 4.5/5 — good example)
        ├── java-intermediate-debug-001.json  (rated 4.8/5)
        └── ...
```

The agent assembles context for any combination:
```
Request: "Go + BASIC + BUILD"

Agent loads:
    tech/go/project-structure.md      (Go-specific structure)
    tech/go/code-style.md             (Go-specific style)
    proficiency/basic.md              (BASIC difficulty rules)
    task-type/build.md                (BUILD task pattern)
    shared/readme-rules.md            (README requirements)
    shared/output-schema.md           (output format)
    shared/code-rules.md              (universal code rules)
    examples/go-basic-build-001.json  (example of a good task)
```

New combinations work without new prompt files. "Rust + INTERMEDIATE + DEBUG" loads `tech/rust/*`, `proficiency/intermediate.md`, `task-type/debug.md`, and shared rules.

### 8.3 Vector Retrieval (Phase 2+)

For Phase 1, file-based retrieval (load by path) is sufficient. For Phase 2+, embed knowledge chunks into Chroma for semantic retrieval:

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("task_knowledge")

# Index all knowledge chunks
collection.add(
    documents=["Go projects use cmd/, internal/, pkg/ structure..."],
    metadatas=[{"tech": "go", "type": "project-structure"}],
    ids=["tech-go-project-structure"]
)

# Retrieve relevant knowledge for a generation request
results = collection.query(
    query_texts=["Generate a Go debugging task for intermediate engineers"],
    n_results=10,
    where={"tech": {"$in": ["go", "shared"]}}
)
```

### 8.4 DSPy Optimization (Phase 3)

Once we have 50+ human-rated tasks per type, DSPy can optimize the generation prompts:

```python
import dspy

class TaskGenerator(dspy.Signature):
    """Generate a coding assessment task"""
    tech_stack: str = dspy.InputField()
    proficiency: str = dspy.InputField()
    task_type: str = dspy.InputField()
    guidelines: str = dspy.InputField()
    scenario: str = dspy.InputField()
    task_output: str = dspy.OutputField()

# DSPy finds the optimal prompting strategy
# (instructions, few-shot examples, chain-of-thought)
# by optimizing against human quality ratings
optimizer = dspy.MIPROv2(metric=task_quality_metric, num_candidates=10)
optimized = optimizer.compile(TaskGenerator(), trainset=rated_tasks)
```

**Action now**: Start collecting rated tasks. Every task a human reviews gets a 1-5 rating stored in Supabase (`task_ratings` table). Build the dataset passively while running Phase 1-2.

---

## 9. Agent Architecture: The Full Design

### 9.1 Agent Roles

```
┌─────────────────────────────────────────────────────────────┐
│  RECRUITER INPUT                                             │
│  "5 Java+Kafka debugging tasks, senior, fintech"            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  INTAKE AGENT                                                │
│                                                              │
│  Model: GPT-5.1 or Claude (either works)                    │
│  Input: Natural language, job descriptions, Slack messages    │
│  Output: Structured TaskRequest                              │
│                                                              │
│  Tools:                                                      │
│  - query_supabase(competency_name) → competency records     │
│  - get_org_history(org_id) → past tasks, ratings, feedback  │
│  - clarify(question) → ask recruiter for missing info       │
│                                                              │
│  Extracts:                                                   │
│  - competencies: [Java, Kafka]                              │
│  - proficiency: INTERMEDIATE (senior → 3-5 yoe)            │
│  - task_type: DEBUG                                          │
│  - count: 5                                                  │
│  - domain: fintech/payments                                  │
│  - constraints: "harder than last batch"                     │
│  - org_context: {from Supabase if available}                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  COORDINATOR AGENT  (the "senior engineer with taste")       │
│                                                              │
│  Model: Claude Opus 4.6 (deepest reasoning)                 │
│  Input: Structured TaskRequest + domain knowledge            │
│  Output: Approved batch of tasks ready for publishing        │
│                                                              │
│  Tools:                                                      │
│  - load_knowledge(tech, proficiency, task_type) → guidelines│
│  - check_dedup(task_desc, existing_embeddings) → similarity │
│  - compare_difficulty(task, proficiency) → calibration check │
│  - spawn_generator(request) → Generator Agent               │
│  - spawn_evaluator(task) → Eval Agent                       │
│  - spawn_solver(task) → Solver Agent                        │
│                                                              │
│  Responsibilities:                                           │
│  PRE-GENERATION:                                             │
│  - Reviews scenarios for realism, diversity, domain fit     │
│  - Checks dedup against existing tasks before generating    │
│  - Loads and assembles relevant domain knowledge            │
│                                                              │
│  GENERATION:                                                 │
│  - Spawns N Generator Agents in parallel (one per task)     │
│  - Each generator gets isolated context                      │
│                                                              │
│  POST-GENERATION:                                            │
│  - Cross-reviews all generated tasks for diversity          │
│  - "Tasks #2 and #4 are too similar — regenerate #4"        │
│  - Validates difficulty consistency across batch            │
│  - Routes eval feedback to specific generators for fixes    │
│  - Makes the "is this genuinely useful to recruiter" call   │
│                                                              │
│  This is the stochastic judgment layer — it doesn't just    │
│  check boxes, it reasons about whether the batch as a       │
│  whole serves the recruiter's actual need.                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ GENERATOR #1 │ │ GENERATOR #2 │ │ GENERATOR #3 │  ... (parallel)
│              │ │              │ │              │
│ Model:       │ │ Model:       │ │ Model:       │
│ GPT-5.1      │ │ GPT-5.1      │ │ GPT-5.1      │
│              │ │              │ │              │
│ Input:       │ │              │ │              │
│ - guidelines │ │              │ │              │
│ - competency │ │              │ │              │
│ - scenario   │ │              │ │              │
│ - constraints│ │              │ │              │
│              │ │              │ │              │
│ Tools:       │ │              │ │              │
│ - verify_    │ │ (same tools) │ │ (same tools) │
│   syntax()   │ │              │ │              │
│ - check_     │ │              │ │              │
│   structure()│ │              │ │              │
│ - validate_  │ │              │ │              │
│   dockerfile │ │              │ │              │
│ - check_     │ │              │ │              │
│   complexity │ │              │ │              │
│ - validate_  │ │              │ │              │
│   readme()   │ │              │ │              │
│              │ │              │ │              │
│ Self-correct:│ │              │ │              │
│ generate →   │ │              │ │              │
│ verify →     │ │              │ │              │
│ fix →        │ │              │ │              │
│ re-verify    │ │              │ │              │
│              │ │              │ │              │
│ Returns:     │ │              │ │              │
│ Verified     │ │              │ │              │
│ TaskOutput   │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       └────────────────┼────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ COORDINATOR      │
              │ (cross-review)   │
              │ - diversity      │
              │ - dedup          │
              │ - difficulty     │
              │ - quality gate   │
              └────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  EVAL AGENT  │ │  EVAL AGENT  │ │  EVAL AGENT  │  (parallel, fresh context)
│  (Claude)    │ │  (Claude)    │ │  (Claude)    │
│              │ │              │ │              │
│  Gets ONLY:  │ │              │ │              │
│  - task      │ │              │ │              │
│  - rubric    │ │              │ │              │
│  NOT:        │ │              │ │              │
│  - generation│ │              │ │              │
│    history   │ │              │ │              │
│              │ │              │ │              │
│  Returns:    │ │              │ │              │
│  - pass/fail │ │              │ │              │
│  - score     │ │              │ │              │
│  - feedback  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ COORDINATOR      │
              │ (final decision) │
              │                  │
              │ pass → PUBLISH   │
              │ fail → route     │
              │ feedback to      │
              │ generator, retry │
              │ (max 2 retries)  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ PUBLISH AGENT    │
              │ (deterministic,  │
              │  no LLM needed)  │
              │                  │
              │ - GitHub repos   │
              │ - Gists          │
              │ - Supabase       │
              │ - Optional deploy│
              └──────────────────┘
```

### 9.2 Agent ↔ Agent Communication

Agents communicate via structured Pydantic models, not free-form text:

```python
class TaskRequest(BaseModel):
    """Intake Agent → Coordinator"""
    competencies: list[Competency]
    proficiency: Literal["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"]
    task_type: Literal["BUILD", "DEBUG", "DESIGN_REVIEW", "PR_REVIEW", "MANAGE_INFRA", "UX_CRITICAL"]
    count: int
    domain: str | None = None
    constraints: list[str] = []
    org_context: OrgContext | None = None

class GenerationRequest(BaseModel):
    """Coordinator → Generator"""
    competencies: list[Competency]
    proficiency: str
    task_type: str
    scenario: str
    guidelines: str  # assembled from knowledge base
    constraints: list[str]
    dedup_embeddings: list[list[float]]  # existing task embeddings to avoid

class TaskOutput(BaseModel):
    """Generator → Coordinator"""
    name: str
    question: str
    code_files: dict[str, str]
    readme_content: str
    outcomes: list[str]
    hints: str
    definitions: dict[str, str]
    answer_code: dict[str, str]
    answer_steps: list[str]
    verification_results: VerificationResults

class EvalResult(BaseModel):
    """Eval Agent → Coordinator"""
    passed: bool
    score: float  # 0-1
    feedback: str
    validated_criteria: list[str]
    issues: list[str]

class VerificationResults(BaseModel):
    """Tool results attached to TaskOutput"""
    syntax_valid: bool
    syntax_errors: list[str]
    readme_sections_present: list[str]
    readme_sections_missing: list[str]
    complexity_score: float
    complexity_appropriate: bool
    dedup_max_similarity: float
    dedup_similar_tasks: list[str]
    docker_build_success: bool | None = None
    tests_pass_on_answer: bool | None = None
    tests_fail_on_starter: bool | None = None
```

### 9.3 Coordinator: The Stochastic Judgment Layer

The Coordinator is what makes this system genuinely intelligent rather than just automated. Its system prompt:

```
You are a senior engineering leader at Utkrusht reviewing a batch of
generated coding assessment tasks. Your job is NOT to check boxes — it is
to apply taste and judgment.

For each task, ask yourself:
- Would I be confident presenting this to a CTO as a hiring assessment?
- Does this task differentiate strong candidates from weak ones?
- Is the scenario realistic enough that a candidate takes it seriously?
- Is there a clear "aha moment" that separates good from great solutions?
- If I were the recruiter, would this batch give me diverse signal?

You have verification data (syntax checks, complexity scores, dedup
similarity) to inform your judgment, but your decision is holistic.
A task can pass all automated checks and still be mediocre.
A task can have a minor syntax issue and still be excellent (just fix it).

Your output for each task: APPROVE, REVISE (with specific feedback),
or REJECT (with reason). For the batch overall: assess diversity,
difficulty consistency, and whether the set serves the recruiter's need.
```

---

## 10. Implementation Roadmap

### Phase 1: Self-Correcting Generation (2-3 weeks)

**Goal**: Single BUILD task with verification tools and self-correction loop. Parity with current CLI quality, but automated.

**Build**:
1. `verify_syntax()` tool using tree-sitter (all languages)
2. `validate_readme()` tool using markdown-it-py
3. `check_complexity()` tool using lizard
4. Wrap `create_task()` in Pydantic AI agent with these tools
5. Add Prefect `@flow`/`@task` decorators around the pipeline
6. Create `task_generation_runs` table in Supabase

**Validate**:
- Generate 30 tasks with self-correction vs 30 without
- Compare first-pass success rate, retry count, quality scores
- Measure cost per task (tokens + tool execution time)

**Decisions answered**:
- Does tool-based self-correction improve quality?
- What's the cost overhead of verification tools?
- Is Pydantic AI ergonomic enough for our use case?

### Phase 2: Multi-Agent + Coordinator (4-6 weeks)

**Build**:
1. Coordinator Agent with cross-review logic
2. Parallel Generator Agents via Pydantic AI graph API
3. Cross-provider Eval Agents (GPT generates, Claude evaluates)
4. DeepEval integration replacing `evals.py`
5. Dedup via OpenAI embeddings + SemHash
6. Decompose 5 prompt files into knowledge chunks
7. Add DEBUG task type to prove architecture handles multiple types

**Validate**:
- Guidelines vs monolithic prompts quality comparison (10+10 tasks, blind)
- Cross-provider eval effectiveness (does GPT+Claude catch more issues than GPT+GPT?)
- Coordinator value: does cross-review improve batch quality?

**Decisions answered**:
- Can decomposed guidelines match monolithic prompt quality?
- Is the Coordinator Agent worth the extra cost?
- Does the architecture handle multiple task types?

### Phase 3: Scale + Intelligence (6-8 weeks)

**Build**:
1. Intake Agent (natural language → structured TaskRequest)
2. Chroma knowledge base for semantic retrieval of guidelines
3. Solver Agent for empirical difficulty calibration (SWE-bench pattern)
4. Docker-based deep verification (Tier 3)
5. testcontainers for database/service-dependent tasks
6. Confidence-based auto-approve (human reviews only low-confidence tasks)
7. DSPy optimization (if 50+ rated tasks available)
8. Add DESIGN REVIEW + PR REVIEW task types
9. Evaluate Temporal for replacing Prefect at this scale

**Target**: 100 tasks/day with <20% requiring human review

**Decisions answered**:
- How much does customer context improve task relevance?
- What auto-approve confidence threshold is safe?
- Does DSPy optimization measurably improve quality?
- Does Temporal's durability matter at this volume?

### Phase 4: Product (8-12 weeks)

**Build**:
1. REST API for recruiter-triggered generation
2. Per-org preference profiles in Supabase
3. Feedback loop (recruiter rates tasks → improves future generation)
4. Event-driven triggers (Inngest: "new competency added → auto-generate")
5. Dashboard UI (Windmill or custom)
6. Qdrant for production-scale knowledge base
7. Add remaining task types (MANAGE INFRA, UX/CRITICAL THINKING)

**Target**: Recruiter submits request → tasks generated, verified, published — no human in the loop for high-confidence tasks.

---

## 11. Supabase Schema Additions

### task_generation_runs

Tracks the state of each generation run:

```sql
CREATE TABLE task_generation_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    -- Request
    request JSONB NOT NULL,  -- Structured TaskRequest
    requested_by TEXT,        -- recruiter email or "system"

    -- State
    status TEXT NOT NULL DEFAULT 'intake',
    -- Values: intake, generating, evaluating, cross_review, publishing, completed, failed

    -- Progress
    total_tasks INT NOT NULL,
    completed_tasks INT DEFAULT 0,
    failed_tasks INT DEFAULT 0,

    -- Results
    task_ids UUID[] DEFAULT '{}',  -- Generated task IDs
    coordinator_notes TEXT,        -- Coordinator's batch assessment

    -- Cost tracking
    total_tokens_used JSONB DEFAULT '{}',  -- {model: {input: N, output: N}}
    total_cost_usd DECIMAL(10, 6) DEFAULT 0,

    -- Retry tracking
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 2,
    last_error TEXT
);
```

### task_ratings

Collects human quality ratings for DSPy optimization:

```sql
CREATE TABLE task_ratings (
    rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(task_id),
    rated_at TIMESTAMPTZ DEFAULT now(),
    rated_by TEXT NOT NULL,          -- reviewer identifier
    score INT NOT NULL CHECK (score BETWEEN 1 AND 5),
    dimensions JSONB,               -- {difficulty: 4, realism: 5, clarity: 3, ...}
    notes TEXT,                      -- free-form reviewer comments
    pairwise_comparison_id UUID      -- if rated via pairwise comparison
);
```

### task_embeddings

Stores embeddings for deduplication:

```sql
CREATE TABLE task_embeddings (
    task_id UUID PRIMARY KEY REFERENCES tasks(task_id),
    embedding VECTOR(1536),         -- text-embedding-3-small dimension
    description_hash TEXT,          -- SHA256 of description for exact dedup
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Similarity search index
CREATE INDEX ON task_embeddings USING ivfflat (embedding vector_cosine_ops);
```

---

## 12. Cost Model

### Per-Task Cost Breakdown (Estimated)

| Step | Model | Tokens (In/Out) | Cost |
|------|-------|-----------------|------|
| Generation | GPT-5.1 | ~2K / ~3K | $0.007 |
| Self-correction (1-2 rounds) | GPT-5.1 | ~1K / ~1K per round | $0.005 |
| Task eval | Claude Opus 4.6 | ~2K / ~500 | $0.008 |
| Code eval | Claude Opus 4.6 | ~3K / ~500 | $0.010 |
| Answer generation | GPT-5.1 | ~3K / ~2K | $0.010 |
| Embedding (dedup) | text-embedding-3-small | ~500 | $0.00001 |
| **Verification tools** | — | — | **$0.00** (local compute) |
| **Total per task** | | | **~$0.04** |

### Batch Cost (5 tasks)

| Step | Cost |
|------|------|
| Intake Agent | $0.005 |
| 5 × Generation + verification | $0.20 |
| Coordinator cross-review | $0.015 |
| 5 × Eval (cross-provider) | $0.09 |
| Coordinator final review | $0.010 |
| **Total for 5-task batch** | **~$0.32** |

### At Scale (100 tasks/day)

| | Daily | Monthly |
|---|---|---|
| LLM costs | ~$4.00 | ~$120 |
| Compute (Docker verification) | ~$2.00 | ~$60 |
| Embedding storage | negligible | negligible |
| **Total** | **~$6.00** | **~$180** |

Verification tools run locally — they cost compute time, not API dollars. This is a key advantage over LLM-only evaluation.

---

## 13. Open Questions (Experiments to Run)

These carry over from V1, refined with tool-specific hypotheses:

| # | Experiment | Hypothesis | How to Test | Unlocks |
|---|-----------|-----------|------------|---------|
| 1 | Model comparison | GPT-5.1 and Claude Opus produce equivalent task quality | 30 tasks each, blind rating | Framework decision (confirmed: Pydantic AI works either way) |
| 2 | Guidelines vs monolithic prompts | Decomposed knowledge produces ≥90% quality of monolithic prompts | 10+10 tasks, blind comparison | Knowledge base architecture |
| 3 | Self-correction effectiveness | Tool verification reduces retry rate by ≥50% | 50 tasks with tools, 50 without | Verification tool investment |
| 4 | Cross-provider eval | GPT+Claude eval catches ≥20% more issues than GPT+GPT | 50 tasks, compare eval hit rates | Multi-provider strategy |
| 5 | Solver Agent calibration | Time-to-solve by Solver Agent correlates (r>0.6) with human difficulty ratings | 30 tasks, solver time vs human rating | Automated difficulty calibration |
| 6 | Coordinator value | Coordinator cross-review improves batch diversity score by ≥30% | 10 batches with coordinator, 10 without | Coordinator agent cost justification |
| 7 | Dedup threshold | 0.90 cosine similarity correctly identifies 90%+ of human-flagged duplicates | Label 100 task pairs as dup/not-dup, sweep thresholds | Dedup automation |
| 8 | DSPy optimization | DSPy-optimized prompts improve quality scores by ≥10% | Requires 50+ rated tasks per type | Prompt optimization ROI |

---

## 14. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Pydantic AI graph API is beta | Parallel generation breaks | Fallback: `asyncio.gather()` with individual agents. Graph API is ergonomic, not essential |
| Verification tools add latency | Slower generation | Tier the verification: Tier 1 (<1s) always, Tier 2 (5-30s) on pass, Tier 3 (30-120s) only for final candidates |
| Decomposed guidelines lose quality | Tasks get worse | A/B test against monolithic prompts before committing. Keep original prompts as fallback |
| Coordinator Agent is expensive | Cost per batch increases | Coordinator only runs once per batch (not per task). Amortized cost is low |
| Docker verification requires infrastructure | Can't run in CI or serverless | Use testcontainers (auto-cleanup). For CI: GitHub Actions with Docker support |
| DSPy requires training data | Can't optimize without rated tasks | Start collecting ratings now. Passive — doesn't block anything |

---

## Appendix A: Tool Installation Quick Reference

```bash
# Verification tools
pip install tree-sitter tree-sitter-language-pack  # Syntax validation (173 languages)
pip install markdown-it-py                          # README section validation
pip install lizard                                  # Code complexity (27 languages)
pip install docker                                  # Docker SDK (build/run containers)
pip install testcontainers                          # Spin up Postgres/Kafka/Redis in tests
pip install yamllint                                # YAML syntax validation
pip install hadolint                                # Dockerfile linting (binary, not pip)

# Evaluation
pip install deepeval                                # LLM evaluation framework (pytest)
npm install -g promptfoo                            # YAML-driven eval (CI integration)

# Deduplication
pip install semhash                                 # Semantic deduplication
pip install faiss-cpu                               # Vector similarity search (if >10K tasks)
pip install chromadb                                # Embedded vector DB (knowledge retrieval)

# Agent framework
pip install pydantic-ai                             # Agent framework
pip install prefect                                 # Workflow durability

# Future (Phase 3+)
pip install dspy                                    # Prompt optimization
pip install qdrant-client                           # Production vector DB
pip install sentence-transformers                   # Local embeddings
```

## Appendix B: Existing Open-Source Projects Worth Studying

| Project | Stars | License | What to Borrow |
|---------|-------|---------|---------------|
| **SWE-bench** | 4.7k | MIT | Fail-to-pass test verification pattern. Docker-based execution. Gold standard for verifying coding tasks are solvable |
| **SWE-agent** | 19k | MIT | Agent loop: read problem → explore code → edit → run tests → iterate. Adaptable as a "task solver agent" for difficulty calibration |
| **OpenHands** | 71.3k | Custom | Sandbox execution model. Model-agnostic agent architecture. Reference for building verification sandboxes |
| **Aider** | 43.4k | Apache-2.0 | Edit → lint → test → auto-fix loop. Repo-map approach for codebase context |
| **promptfoo** | 20.1k | MIT | YAML-driven structured evaluation. Sandboxed code execution via epicbox. CI/CD integration pattern |
| **DeepEval** | 14.8k | Apache-2.0 | 60+ evaluation metrics. pytest integration. GEval for custom rubric-based evaluation |
| **RAGAS** | 13.4k | Apache-2.0 | Synthetic test data generation. Reference-free evaluation metrics |
| **SemHash** | 910 | MIT | Lightweight semantic deduplication with configurable thresholds |

## Appendix C: Migration Path from Current Codebase

The migration is incremental — each step adds value independently:

```
Step 1: Add tree-sitter verification to existing multiagent.py
    → Immediate quality improvement, no architecture change
    → ~50 lines of new code in utils.py

Step 2: Add Prefect decorators to existing functions
    → Retries, caching, observability
    → ~20 lines changed per function (add decorator)

Step 3: Replace evals.py with DeepEval
    → Structured, repeatable evaluation
    → ~100 lines replacing ~150 lines

Step 4: Wrap generate_task_with_code() in Pydantic AI agent
    → Self-correction loop with tool feedback
    → New file: agents/generator.py (~200 lines)

Step 5: Add Coordinator agent
    → Cross-review, dedup, difficulty consistency
    → New file: agents/coordinator.py (~150 lines)

Step 6: Add Intake agent
    → Natural language → structured request
    → New file: agents/intake.py (~100 lines)

Step 7: Decompose prompt files into knowledge base
    → New directory: knowledge/ (~30 files from existing prompts)
    → Generator loads from knowledge/ instead of PROMPT_REGISTRY

Each step can be deployed independently.
None require the previous step (except Step 5 depends on Step 4).
```

---

## 15. Task Taxonomy: What We Actually Generate (From Production DB)

> This section is derived from querying the dev Supabase database (271 tasks, 400+ competency records) and reading every prompt file and flow module. It defines the complete taxonomy of task types the agentic pipeline must support.

### 15.1 Database Snapshot (April 2026)

```
Total tasks:           271
With GitHub repo:      264
Proficiency split:     BASIC=227, INTERMEDIATE=159, BEGINNER=24
Unique competencies:   70+ (from Java to AI Native Leadership)
Unique combos:         70+ (single and multi-competency tasks)
```

### 15.2 The Seven Task Archetypes

Every task we generate falls into one of seven archetypes. Each archetype has a different generation pattern, different artifacts, different verification needs, and a different agent tool belt.

#### Archetype 1: CODE BUILD (Extend a Skeleton)

**What it is**: Candidate receives a partially implemented codebase and must add features, fix architecture, or complete functionality.

**Examples from DB**:
- Java + Spring Boot INTERMEDIATE: "Configure Conditional Feature AutoConfig" — replace hardwired beans with config-driven auto-configuration
- Golang + Docker BASIC: "go-docker-postgres-healthcheck" — fix Docker health checks, service dependencies, retry logic
- Python FastAPI + Kafka INTERMEDIATE: "Implement Reliable Assessment Result Processing Pipeline" — fix consumer offset management, idempotency, dead-letter routing
- NextJs + TypeScript BASIC: "Develop Weather Dashboard" — debouncing, race conditions, background logging
- React Native INTERMEDIATE: "Implement Infinite Scroll and Persistence in News Reader App" — pagination, bookmarks, performance

**Artifacts generated**:
```
code_files: {
    "README.md": "...",
    ".gitignore": "...",
    "cmd/main.go": "...",           # or src/main/java/... or app/page.tsx
    "internal/service/service.go": "...",
    "docker-compose.yml": "...",     # if shared_infra
    "Dockerfile": "...",             # if shared_infra
    "run.sh": "...",                 # if deployable
    "kill.sh": "..."                 # if deployable
}
```

**Verification needs**: Syntax (tree-sitter), complexity (lizard), Docker build (docker-py), README sections (markdown-it-py), answer code passes tests (SWE-bench pattern).

**Current prompt files**: 50+ files across Basic/Intermediate for Go, Java, Python, React, Node, SQL, etc.

**DB count**: ~231 tasks (85% of total)

---

#### Archetype 2: CODE DEBUG (Find and Fix)

**What it is**: Candidate receives a broken service with failing tests or runtime errors. Must diagnose root cause and fix.

**Examples from DB**: Currently generated via BUILD prompts with intentionally broken code. Not a separate archetype in prompts yet, but V1 research identifies it as a distinct generation pattern (two-phase: working system → inject bugs).

**Artifacts**: Same as BUILD but code has intentional bugs. Tests must FAIL on starter, PASS on answer.

**Verification needs**: SWE-bench fail-to-pass pattern is critical. Bugs must be realistic (not syntax errors).

**Current status**: No dedicated prompt files. Generated via BUILD prompts.

---

#### Archetype 3: PR REVIEW (Code Review Assessment)

**What it is**: Candidate reviews a pull request, identifies issues, provides feedback with severity ratings.

**Examples from DB**: Generated via `pr_review_flow/` module. Two-phase pipeline:
- Phase 1: Generate clean base repo (4-5+ source files, real code, no bugs)
- Phase 2: Generate flawed PR + answer key (intentional bugs with severity, category, line ranges)

**Artifacts**:
```
Phase 1 output (base repo):
    src/main.py, src/service.py, src/models.py, tests/test_*.py, README.md

Phase 2 output (PR):
    modified_files: {"src/service.py": "...with injected flaws..."}
    added_files: {"src/new_module.py": "..."}
    answer_key: [
        {file: "src/service.py", line_range: "23-27", category: "security",
         severity: "critical", description: "SQL injection via string format",
         correct_approach: "Use parameterized queries"}
    ]
```

**Verification needs**: Phase 1 eval (code quality, minimum files, reviewability) + Phase 2 eval (flaws reference valid files, answer key covers all intentional flaws, flaws look realistic not planted).

**Current module**: `pr_review_flow/` — separate pipeline with own prompts, evals, GitHub integration.

---

#### Archetype 4: SYSTEM DESIGN (Architecture Document)

**What it is**: Candidate designs a system component. No code — produces a written design document.

**Two variants from DB**:

**4a. BASIC (Guided Template)**:
```
code_files: {
    "README.md": "...",
    "DESIGN_TEMPLATE.md": "## Component Architecture\n## API Contract\n## Data Model\n## Trade-offs\n## Failure Handling",
    "reference/existing_architecture.md": "...",
    ".gitignore": "..."
}
```
Candidate fills in DESIGN_TEMPLATE.md with guiding sub-questions per section.

**4b. INTERMEDIATE (Blank Canvas + Reference Code)**:
```
code_files: {
    "README.md": "...",
    "DESIGN.md": "",  # completely blank — candidate structures their own
    "src/main/java/com/example/Service.java": "...",  # real code showing current system
    "src/main/java/com/example/Controller.java": "...",
    "pom.xml": "..."
}
```
Candidate sees actual project code and writes design from scratch — no template, no prescribed sections.

**Design challenge types**: (1) Design from scratch, (2) Extend existing system, (3) Diagnose & redesign.

**Verification needs**: README structure, design doc is not empty, reference files are realistic. No code compilation needed.

**Current prompt files**: `system_design_prompt.py` (BASIC), `system_design_java_intermediate_prompt.py`, `system_design_python_fastapi_intermediate_prompt.py`, `system_design_sql_intermediate_prompt.py`.

---

#### Archetype 5: AI/PROMPT ENGINEERING (Evaluation Framework Design)

**What it is**: Candidate analyzes operational data from an AI system and designs evaluation frameworks, prompt improvements, or go/no-go recommendations.

**Examples from DB**:
- Prompt Engineering BASIC: "Design Voice Agent Eval Framework" — analyze call logs, design evaluation dimensions, labeling scheme, ship/don't-ship threshold
- AI Native Leadership BASIC: Strategic AI integration tasks
- Prompt Engineering for Product Managers BASIC: AI system optimization from a product perspective

**Artifacts**:
```
code_files: {
    "README.md": "...",
    "call_logs.csv": "100 rows with patterns — failure types, agreement rates, versions",
    "interview_system_prompt.txt": "current prompt with embedded flaws",
    "agent_config.json": "parameters correlating with quality issues"
}
```

**Key property**: Data files contain **intentional patterns** the candidate must discover:
- ~60-65% overall agreement rate (system is mediocre, decision is genuinely ambiguous)
- Certain failure types have high DISAGREE rates
- Certain agent versions perform worse
- Config parameters correlate with failure patterns

**Candidate deliverable**: Written framework document with: (1) 5-7 evaluation dimensions, (2) labeling scheme for 100 calls, (3) ship/don't-ship threshold, (4) automation vs human-review matrix, (5) executive summary.

**Verification needs**: Data file structure (CSV has correct columns, 100 rows), patterns are discoverable, README doesn't give away the answer. No code to compile.

**Current prompt files**: `voice_agent_eval_prompt.py`, `Prompt_basic.py`.

---

#### Archetype 6: NON-TECHNICAL (Business Analysis)

**What it is**: Candidate analyzes business data and produces strategic deliverables. Zero executable code.

**Competencies from DB**: Agile, Agile Methodology, Agile/Scrum, AI Native Leadership, Prompt Engineering for PMs, and similar non-coding competencies.

**Artifacts**:
```
code_files: {
    "README.md": "...",
    "data.csv": "20-60 rows of business data with patterns",
    "context.json": "organizational context, constraints",
    "reference.txt": "additional context materials"
}
```

**Current module**: `non_tech_flow/` — separate pipeline with:
- `non_tech_multiagent.py` — orchestrator
- `non_tech_evals.py` — time-based + proficiency alignment evaluation
- `non_tech_utils.py` — utilities
- `models.py` — Pydantic `TaskResponse` schema (text-only fields)
- Uses `task_sceanrio_no_code.json` for scenarios

**Key differences from tech tasks**:
- `TaskResponse` Pydantic model (not raw JSON schema)
- Data files only — no executable code, no templates, no examples
- Evaluation focuses on: completable in 20 minutes? Appropriate for proficiency? Realistic business problem?
- No GitHub repo needed (optional)
- No Docker, no deployment

**Verification needs**: Data file validity (CSV structure, row count), README doesn't leak solution, time constraint is realistic.

---

#### Archetype 7: INFRASTRUCTURE / DEVOPS (Hands-On Ops)

**What it is**: Candidate works with Docker, Kubernetes, shell scripts, or cloud configs to fix operational issues.

**Examples from DB**:
- Docker BASIC: Container orchestration, health checks, networking
- Shell BASIC: "Automate Employee Timesheet CSV Reporting" — bash script processing CSV data
- RAG + Vector Databases BASIC: Full Docker Compose stack with ChromaDB, data-init service, RAG app

**RAG/Infrastructure tasks are special** — they provide a **fully deployable system** that works out of box:
```
code_files: {
    "Dockerfile": "...",
    "docker-compose.yml": "three services: chromadb, data-init, rag-app",
    "run.sh": "start stack, health checks, test queries",
    "kill.sh": "teardown",
    "app/main.py": "...",
    "app/requirements.txt": "...",
    "data/init_chromadb.py": "..."
}
```

Candidate improves robustness, enhances retrieval quality, optimizes deployment, adds observability — they don't build from scratch.

**Verification needs**: Docker build succeeds, `docker compose up` starts all services, health checks pass, `run.sh` executes without error.

---

### 15.3 Archetype Comparison Matrix

| | CODE BUILD | CODE DEBUG | PR REVIEW | SYSTEM DESIGN | AI/PROMPT | NON-TECH | INFRA/DEVOPS |
|---|---|---|---|---|---|---|---|
| **Candidate writes code** | Yes | Yes (fixes) | No (reviews) | No (writes design) | No (writes analysis) | No (writes analysis) | Yes (scripts/configs) |
| **Has executable code** | Yes | Yes (broken) | Yes (in PR) | No (or reference only) | No (data files) | No (data files) | Yes (Docker/scripts) |
| **Generation phases** | Single | Two (working → inject bugs) | Two (base repo → flawed PR) | Single | Single | Single | Single |
| **GitHub integration** | Template repo + answer repo | Template repo + answer repo | Real repo + real PR | Template repo | Optional | Optional | Template repo |
| **Deployable** | Sometimes (if Docker) | Sometimes | No | No | No | No | Yes (always) |
| **Shared infra needed** | Sometimes | Sometimes | No | No | No | No | Yes |
| **Eval focus** | Code quality, difficulty, completeness | Bug realism, test fail-to-pass | Flaw realism, answer key completeness | Design clarity, trade-offs | Data patterns, analysis quality | Time constraint, proficiency fit | Docker builds, services start |
| **Current pipeline** | `multiagent.py` | `multiagent.py` (no separate flow) | `pr_review_flow/` | `multiagent.py` | `multiagent.py` or `non_tech_flow/` | `non_tech_flow/` | `multiagent.py` |
| **Prompt files** | 50+ files | None (uses BUILD prompts) | Own prompts in `pr_review_flow/` | 4 files | 2 files | Own prompts in `non_tech_flow/` | 3-4 files |
| **DB count** | ~200 | ~0 (embedded in BUILD) | ~5 | ~1 | ~7 | ~25 | ~33 |

### 15.4 Competency Landscape (From DB)

**Coding competencies** (most tasks, 15+ tech stacks):
```
Backend:     Java, Golang, Python, Python-FastAPI, NodeJs, ExpressJS
Frontend:    ReactJs, React Native, NextJs, HTML/CSS, Javascript, TypeScript
Database:    PostgreSQL, MongoDB, SQL, Redis
Infra:       Docker, Kafka, Kubernetes (future)
Specialized: Java-Spring Boot, Java-Multithread, Java-Async, Java-Distributed Systems,
             Go-Multithread, Go-Async, Go-Concurrency, React-Optimization,
             Python-Pandas/Numpy
```

**AI/ML competencies**:
```
Prompt Engineering, Voice Agent Evaluation, AI Native Leadership,
AI Agents - Token Optimization, RAG, Vector Databases, Langchain
```

**Non-technical competencies**:
```
Agile, Agile Methodology, Agile/Scrum, REST APIs, Microservices,
Shell, Apache Camel, UI/UX Design Review
```

**Proficiency levels**: BEGINNER (0-1 yoe), BASIC (1-2 yoe), INTERMEDIATE (3-5 yoe), ADVANCED (6+ yoe)

**Multi-competency tasks**: ~40% of tasks test 2 competencies together (e.g., "Java + Kafka", "Golang + Docker", "ReactJs + NodeJs + MongoDB", "NextJs + TypeScript", "Python FastAPI + PostgreSQL")

---

## 16. Agentic Generation Graph: One Pipeline for All Seven Archetypes

The critical insight from the task taxonomy: **a single linear pipeline cannot generate all seven archetypes**. PR Review needs two phases. System Design produces no code. Non-tech needs different eval criteria. The pipeline must branch based on archetype.

### 16.1 The Generation Graph

```
┌─────────────────────────────────────────────────────────────────┐
│  INTAKE AGENT                                                    │
│                                                                  │
│  Input: "5 Java+Kafka debugging tasks, senior, fintech"         │
│  OR:    "Create a system design task for Python FastAPI"         │
│  OR:    "Prompt engineering eval for AI product managers"        │
│  OR:    "Agile methodology assessment for team leads"            │
│                                                                  │
│  Output: TaskRequest {                                           │
│    competencies, proficiency, archetype, count,                  │
│    domain, constraints, org_context                              │
│  }                                                               │
│                                                                  │
│  Archetype detection:                                            │
│  - "debugging" / "fix" / "broken" → CODE_DEBUG                  │
│  - "review PR" / "code review" → PR_REVIEW                      │
│  - "system design" / "architecture" → SYSTEM_DESIGN              │
│  - "prompt" / "eval framework" / "AI agent" → AI_PROMPT          │
│  - "agile" / "leadership" / "sales" → NON_TECH                  │
│  - "docker" / "shell" / "k8s" / "infra" → INFRA_DEVOPS         │
│  - default (coding competency) → CODE_BUILD                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  COORDINATOR AGENT                                                │
│                                                                   │
│  Routes to the correct generation strategy per archetype:         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  ARCHETYPE ROUTER                                         │    │
│  │                                                           │    │
│  │  CODE_BUILD ────────► SinglePhaseCodeGenerator            │    │
│  │  CODE_DEBUG ────────► TwoPhaseDebugGenerator              │    │
│  │  PR_REVIEW ─────────► TwoPhasePRGenerator                 │    │
│  │  SYSTEM_DESIGN ─────► DesignDocGenerator                  │    │
│  │  AI_PROMPT ─────────► DataAnalysisTaskGenerator            │    │
│  │  NON_TECH ──────────► NonTechTaskGenerator                │    │
│  │  INFRA_DEVOPS ──────► InfraTaskGenerator                  │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │GENERATOR │     │GENERATOR │     │GENERATOR │  (parallel per task)
    │  #1      │     │  #2      │     │  #3      │
    │          │     │          │     │          │
    │ Strategy │     │ Strategy │     │ Strategy │
    │ depends  │     │ depends  │     │ depends  │
    │ on       │     │ on       │     │ on       │
    │ archetype│     │ archetype│     │ archetype│
    └────┬─────┘     └────┬─────┘     └────┬─────┘
         └────────────────┼────────────────┘
                          ▼
                   Archetype-specific
                   verification + eval
                          │
                          ▼
                   COORDINATOR
                   cross-review
                          │
                          ▼
                   PUBLISH AGENT
```

### 16.2 Generator Strategies Per Archetype

Each archetype has a different generation strategy, different tools, and different eval criteria:

#### SinglePhaseCodeGenerator (CODE_BUILD, INFRA_DEVOPS)

```
1. Load guidelines: tech/{stack}/ + proficiency/{level}.md + task-type/build.md
2. Load scenario from scenario pool or generate new
3. Generate task JSON + code_files in single LLM call
4. Verify:
   ├── tree-sitter syntax check on all code files
   ├── markdown-it-py README section check
   ├── lizard complexity check on answer code
   ├── hadolint/yamllint on Docker/YAML files (if present)
   └── docker compose config (if Docker task)
5. Self-correct if verification fails (up to 3 rounds)
6. Generate answer code + solution steps
7. Verify answer:
   └── SWE-bench pattern: tests FAIL on starter, PASS on answer
8. Return verified TaskOutput
```

#### TwoPhaseDebugGenerator (CODE_DEBUG)

```
Phase 1: Generate WORKING system
   1. Load guidelines: tech/{stack}/ + proficiency/{level}.md + task-type/debug.md
   2. Generate complete, working codebase + passing tests
   3. Verify: all tests PASS, Docker builds (if applicable)

Phase 2: Inject realistic bugs
   1. Select 2-4 bugs appropriate for proficiency level
   2. Modify code to introduce bugs (NOT syntax errors — logical/architectural)
   3. Verify: tests now FAIL on buggy code, PASS on original
   4. Generate bug description hints (without giving away the fix)
   5. Package: buggy code as starter, working code as answer

Eval gate between phases: Phase 1 must produce genuinely working code
before Phase 2 can inject realistic bugs.
```

#### TwoPhasePRGenerator (PR_REVIEW)

```
Phase 1: Generate clean base repo
   1. Load guidelines from pr_review_flow/prompts/
   2. Generate 4-5+ source files (real code, properly structured)
   3. Eval gate: code quality, consistency, minimum file count, reviewability
   4. Create GitHub repo, upload base files to main branch

Phase 2: Generate flawed PR
   1. Generate modified_files + added_files with intentional flaws
   2. Generate answer_key: [{file, line_range, category, severity, description, correct_approach}]
   3. Eval gate: flaws reference valid files, answer key complete, flaws look realistic
   4. Create PR branch, push changes, open real GitHub PR

Output: GitHub repo URL + PR URL + answer key
```

#### DesignDocGenerator (SYSTEM_DESIGN)

```
1. Load guidelines: proficiency/{level}.md + task-type/design-review.md
2. Select design challenge type: from-scratch / extend / diagnose-redesign
3. If INTERMEDIATE: generate reference code files showing current system
4. Generate README with design problem description
5. Generate DESIGN_TEMPLATE.md (BASIC) or empty DESIGN.md (INTERMEDIATE)
6. Generate reference materials (existing architecture docs, etc.)
7. Generate answer key (high-level reference design, evaluator guide)
8. Verify: README doesn't leak solution, template sections are meaningful
9. NO code compilation needed — verify document structure only
```

#### DataAnalysisTaskGenerator (AI_PROMPT)

```
1. Load guidelines: task-type/ai-prompt.md + proficiency/{level}.md
2. Generate scenario (voice agent, RAG pipeline, prompt optimization, etc.)
3. Generate data files with INTENTIONAL PATTERNS:
   ├── call_logs.csv: 100 rows, ~60-65% agreement rate, failure correlations
   ├── system_prompt.txt: embedded flaws candidate should identify
   └── agent_config.json: parameters correlating with quality issues
4. Verify data files:
   ├── CSV has correct columns and row count
   ├── Patterns are statistically discoverable (not random noise)
   ├── Agreement rate is in the ambiguous range (not obviously pass/fail)
   └── README doesn't reveal the patterns
5. Generate answer: expected analysis, dimensions, thresholds
6. NO code to compile — verify data structure and pattern quality
```

#### NonTechTaskGenerator (NON_TECH)

```
1. Load guidelines from non_tech_flow/ prompts
2. Generate business scenario appropriate for competency (Agile, Leadership, etc.)
3. Generate data files: CSV/JSON with 20-60 rows of business data
4. Generate deliverable requirements (what candidate must produce)
5. Verify:
   ├── Completable in 20 minutes?
   ├── Appropriate for proficiency level?
   ├── Realistic business problem?
   ├── Data is small enough to analyze manually?
   └── README doesn't give away the analysis
6. Uses non_tech_flow/models.py TaskResponse (Pydantic, not raw JSON)
```

### 16.3 Archetype-Specific Tool Belts

Each generator strategy gets a different set of verification tools:

| Tool | CODE_BUILD | CODE_DEBUG | PR_REVIEW | SYSTEM_DESIGN | AI_PROMPT | NON_TECH | INFRA |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `verify_syntax()` (tree-sitter) | Yes | Yes | Yes | — | — | — | Yes |
| `validate_readme()` (markdown-it-py) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `check_complexity()` (lizard) | Yes | Yes | Yes | — | — | — | Yes |
| `validate_dockerfile()` (hadolint) | If Docker | If Docker | — | — | — | — | Yes |
| `validate_yaml()` (yamllint) | If YAML | If YAML | — | — | — | — | Yes |
| `validate_csv()` (custom) | — | — | — | — | Yes | Yes | — |
| `check_data_patterns()` (custom) | — | — | — | — | Yes | — | — |
| `docker_compose_config()` | If Docker | If Docker | — | — | — | — | Yes |
| `docker_build()` (docker-py) | Phase 3 | Phase 3 | — | — | — | — | Phase 2 |
| `run_tests()` (SWE-bench) | Phase 3 | Critical | — | — | — | — | — |
| `check_dedup()` (embeddings) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `validate_pydantic()` | Yes | Yes | Yes | Yes | Yes | Yes (TaskResponse) | Yes |
| `validate_pr_structure()` | — | — | Yes | — | — | — | — |
| `validate_answer_key()` | — | — | Yes | — | — | — | — |
| `check_design_structure()` | — | — | — | Yes | — | — | — |
| `time_estimate()` | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

### 16.4 New Verification Tools Needed (Beyond Section 5)

The task taxonomy reveals tools not identified in the earlier analysis:

**`validate_csv(csv_content, expected_columns, min_rows, max_rows)`**
- For AI/PROMPT and NON_TECH archetypes
- Verifies column names, row count, no empty cells in required fields
- Checks data types (numeric columns are numeric, dates are dates)

**`check_data_patterns(csv_content, expected_patterns)`**
- For AI/PROMPT archetype specifically
- Verifies that intentional patterns are statistically discoverable
- E.g., "failure_reason HALLUCINATED_SKILL should have >70% DISAGREE rate"
- E.g., "overall agreement should be 55-70% (ambiguous, not obvious)"
- Uses pandas for basic statistical checks

**`validate_pr_structure(base_files, pr_files, answer_key)`**
- For PR_REVIEW archetype
- Verifies modified_files reference real files in base repo
- Verifies answer_key line_ranges exist in the modified files
- Verifies each intentional flaw has a category + severity + description

**`check_design_structure(design_doc, variant)`**
- For SYSTEM_DESIGN archetype
- BASIC variant: verifies DESIGN_TEMPLATE.md has required sections with sub-questions
- INTERMEDIATE variant: verifies DESIGN.md is empty (candidate fills it), reference code files exist
- Both: verifies README describes the design challenge without leaking the solution

**`time_estimate(task_output, proficiency)`**
- For ALL archetypes
- Heuristic combining: file count, code line count, data row count, concept count
- Maps to expected completion time per proficiency level
- Flags tasks that are likely too easy (<50% expected time) or too hard (>150%)

---

## 17. Unified Pydantic Models for All Archetypes

### 17.1 TaskRequest (Intake → Coordinator)

```python
from pydantic import BaseModel
from typing import Literal

class Competency(BaseModel):
    competency_id: str
    name: str
    proficiency: Literal["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"]
    scope: str

class OrgContext(BaseModel):
    organization_id: str
    organization_name: str
    organization_background: str
    domain: str | None = None          # "fintech", "healthcare", "e-commerce"
    preferences: dict | None = None    # past feedback, style preferences

class TaskRequest(BaseModel):
    competencies: list[Competency]
    proficiency: Literal["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"]
    archetype: Literal[
        "CODE_BUILD", "CODE_DEBUG", "PR_REVIEW",
        "SYSTEM_DESIGN", "AI_PROMPT", "NON_TECH", "INFRA_DEVOPS"
    ]
    count: int = 1
    domain: str | None = None
    constraints: list[str] = []        # "harder than last batch", "focus on observability"
    org_context: OrgContext | None = None
    scenarios: list[str] | None = None # pre-generated or will be generated
```

### 17.2 TaskOutput (Generator → Coordinator) — Unified Across Archetypes

```python
class VerificationResults(BaseModel):
    # Tier 1: Fast (always run)
    syntax_valid: bool = True
    syntax_errors: list[str] = []
    readme_sections_present: list[str] = []
    readme_sections_missing: list[str] = []
    schema_valid: bool = True
    schema_errors: list[str] = []

    # Tier 2: Medium (run after Tier 1 passes)
    complexity_score: float | None = None
    complexity_appropriate: bool | None = None
    dedup_max_similarity: float | None = None
    dedup_similar_tasks: list[str] = []
    csv_valid: bool | None = None       # AI_PROMPT, NON_TECH
    data_patterns_valid: bool | None = None  # AI_PROMPT
    pr_structure_valid: bool | None = None   # PR_REVIEW
    design_structure_valid: bool | None = None  # SYSTEM_DESIGN
    time_estimate_minutes: float | None = None
    time_estimate_appropriate: bool | None = None

    # Tier 3: Deep (final candidates only)
    docker_build_success: bool | None = None
    tests_pass_on_answer: bool | None = None
    tests_fail_on_starter: bool | None = None

class TaskOutput(BaseModel):
    """Unified output for all archetypes."""
    archetype: str
    name: str
    question: str
    code_files: dict[str, str]          # all archetypes produce files
    outcomes: list[str]
    hints: str
    definitions: dict[str, str]
    pre_requisites: list[str]
    short_overview: list[str]
    answer: str                         # text explanation of solution
    is_shared_infra_required: bool = False

    # Answer artifacts (archetype-dependent)
    answer_code: dict[str, str] | None = None  # CODE_BUILD, CODE_DEBUG, INFRA
    answer_steps: list[str] = []

    # PR Review specific
    pr_base_files: dict[str, str] | None = None
    pr_modified_files: dict[str, str] | None = None
    pr_added_files: dict[str, str] | None = None
    pr_answer_key: list[dict] | None = None

    # Verification
    verification: VerificationResults = VerificationResults()
```

### 17.3 EvalResult (Eval Agent → Coordinator)

```python
class EvalResult(BaseModel):
    """Archetype-aware evaluation result."""
    archetype: str
    passed: bool
    score: float                        # 0.0-1.0
    feedback: str
    validated_criteria: list[str]
    issues: list[str]

    # Archetype-specific eval dimensions
    difficulty_appropriate: bool | None = None
    time_constraint_met: bool | None = None
    scenario_realistic: bool | None = None
    code_quality: bool | None = None        # CODE_BUILD, CODE_DEBUG, INFRA
    flaws_realistic: bool | None = None     # PR_REVIEW, CODE_DEBUG
    design_clarity: bool | None = None      # SYSTEM_DESIGN
    data_quality: bool | None = None        # AI_PROMPT, NON_TECH
    solution_leakage: bool | None = None    # all archetypes
```

---

## 18. Revised Implementation Roadmap (Archetype-Aware)

The original roadmap (Section 10) assumed mostly CODE_BUILD tasks. With seven archetypes, the phases shift:

### Phase 1: CODE_BUILD + Verification (2-3 weeks)
Same as before — single archetype with self-correction loop. This covers 85% of existing tasks.

### Phase 2: Multi-Archetype Foundation (4-6 weeks)

**Build**:
1. Archetype Router in Coordinator (detect from competencies + user intent)
2. `NonTechTaskGenerator` — port `non_tech_flow/` into agent architecture
3. `DesignDocGenerator` — port system design prompts into agent architecture
4. `DataAnalysisTaskGenerator` — port AI/prompt prompts into agent architecture
5. New verification tools: `validate_csv()`, `check_data_patterns()`, `check_design_structure()`
6. Unified `TaskOutput` Pydantic model replacing archetype-specific schemas
7. Cross-provider eval with archetype-aware rubrics

This phase makes the system capable of generating **5 of 7 archetypes** (CODE_BUILD, SYSTEM_DESIGN, AI_PROMPT, NON_TECH, INFRA_DEVOPS).

### Phase 3: Two-Phase Archetypes + Scale (6-8 weeks)

**Build**:
1. `TwoPhaseDebugGenerator` — working system → inject bugs → verify fail-to-pass
2. `TwoPhasePRGenerator` — port `pr_review_flow/` into agent architecture
3. `validate_pr_structure()`, `validate_answer_key()` tools
4. Docker-based deep verification (Tier 3) for CODE_BUILD and INFRA
5. Solver Agent for empirical difficulty calibration
6. SWE-bench fail-to-pass verification for CODE_DEBUG
7. Intake Agent (natural language → structured TaskRequest with archetype)

This phase completes **all 7 archetypes** and adds the most sophisticated verification.

### Phase 4: Product (8-12 weeks)
Same as before — API, per-org preferences, DSPy, feedback loop, dashboard.

---

## 19. Complete Agent ↔ Module Mapping

How the new agents map to existing codebase modules:

| Agent / Component | Replaces | New Code |
|---|---|---|
| **Intake Agent** | Human running CLI commands + selecting files | `agents/intake.py` (~100 lines) |
| **Coordinator Agent** | Human reviewing quality + managing retries | `agents/coordinator.py` (~200 lines) |
| **SinglePhaseCodeGenerator** | `multiagent.py:create_task()` + `utils.py:generate_task_with_code()` | `agents/generators/code_build.py` (~250 lines) |
| **TwoPhaseDebugGenerator** | Nothing (new capability) | `agents/generators/code_debug.py` (~300 lines) |
| **TwoPhasePRGenerator** | `pr_review_flow/pr_review_multiagent.py` | `agents/generators/pr_review.py` (~300 lines) |
| **DesignDocGenerator** | `multiagent.py` with system_design prompts | `agents/generators/system_design.py` (~150 lines) |
| **DataAnalysisTaskGenerator** | `multiagent.py` with voice_agent/prompt prompts | `agents/generators/ai_prompt.py` (~200 lines) |
| **NonTechTaskGenerator** | `non_tech_flow/non_tech_multiagent.py` | `agents/generators/non_tech.py` (~150 lines) |
| **InfraTaskGenerator** | `multiagent.py` with Docker/Shell/RAG prompts | `agents/generators/infra.py` (~200 lines) |
| **Eval Agent** | `evals.py` + `non_tech_flow/non_tech_evals.py` + `pr_review_flow/pr_review_evals.py` | `agents/eval.py` (~200 lines) |
| **Publish Agent** | `github_utils.py` + `gist_manager.py` + Supabase inserts | `agents/publish.py` (~150 lines) |
| **Verification Tools** | Nothing (new capability) | `tools/` directory (~500 lines total) |
| **Knowledge Base** | `task_generation_prompts/` (80+ files) | `knowledge/` directory (~30 decomposed files) |

**Total new code**: ~2,500 lines across agents + tools + knowledge files.
**Code replaced**: ~3,000 lines across multiagent.py, non_tech_flow/, pr_review_flow/.
**Net result**: Slightly less code, but modular, testable, and archetype-extensible.

---

## 20. Tool Deep-Dive: Pydantic AI (v1.84.0, April 2026)

> This section provides implementation-level detail on our chosen agent framework.

### 20.1 Current State

Pydantic AI reached V1 in September 2025 (API stability guaranteed). As of April 16, 2026, the latest release is **v1.84.0** with 16,000+ GitHub stars. Ships near-daily releases.

### 20.2 Multi-Agent Patterns (STABLE)

Three patterns supported, from simple to complex:

**Pattern 1: Agent-as-Tool (Delegation)** — a parent agent delegates to a sub-agent via a tool call. Sub-agents get isolated context. Usage tracking can be shared across agents via `usage=ctx.usage`.

```python
coordinator_agent = Agent('openai:gpt-5.2', instructions='...')
generator_agent = Agent('openai:gpt-5.1-2025-11-13', output_type=TaskOutput)

@coordinator_agent.tool
async def generate_task(ctx: RunContext[None], scenario: str) -> TaskOutput:
    r = await generator_agent.run(scenario, usage=ctx.usage)
    return r.output
```

**Pattern 2: Programmatic Hand-off** — application code controls the flow, calling different agents based on archetype. This is our primary pattern:

```python
async def generate_by_archetype(request: TaskRequest) -> TaskOutput:
    usage = RunUsage()
    if request.archetype == "CODE_BUILD":
        result = await code_build_agent.run(request, usage=usage)
    elif request.archetype == "PR_REVIEW":
        phase1 = await pr_base_agent.run(request, usage=usage)
        result = await pr_flaw_agent.run(phase1.output, usage=usage)
    # ... application code decides flow, not the LLM
```

**Pattern 3: Graph API (BETA)** — for parallel fan-out of N generators:

```python
from pydantic_ai.graph.beta import GraphBuilder, StepContext

g = GraphBuilder(state_type=BatchState, output_type=list[TaskOutput])

@g.step
async def generate_tasks(ctx: StepContext):
    return [scenario for scenario in ctx.state.scenarios]

# Fan-out: each scenario generates in parallel
g.add(
    g.edge_from(g.start_node).to(generate_tasks),
    g.edge_from(generate_tasks).map().to(single_task_generator),
    g.edge_from(single_task_generator).to(g.end_node),
)
```

**Graph API limitations**: No built-in state persistence. Parallel branches share the same state object (requires careful coordination). Step-by-step iteration available but parallel branches add complexity. If the graph API doesn't work, fallback is `asyncio.gather()` with individual agents (~10 extra lines).

### 20.3 Portkey Integration (WORKS)

Portkey is not a first-class provider — it works through the OpenAI provider with custom `base_url`. Portkey has official documentation for this.

```python
from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

portkey_client = AsyncOpenAI(
    api_key=os.environ["PORTKEY_API_KEY"],
    base_url="https://api.portkey.ai/v1",
    default_headers={
        "x-portkey-config": "YOUR_CONFIG_ID",
        "x-portkey-trace-id": f"task-gen-{run_id}",
        # Tag requests for cost analytics per archetype
        "x-portkey-metadata": json.dumps({
            "archetype": "CODE_BUILD",
            "tech_stack": "golang",
            "proficiency": "BASIC"
        })
    }
)

model = OpenAIModel(
    model_name="gpt-5.1-2025-11-13",
    provider=OpenAIProvider(openai_client=portkey_client),
)

agent = Agent(model=model, output_type=TaskOutput)
```

### 20.4 Structured Output (STABLE)

Five output modes: text, tool, native, prompted, auto. Complex nested models work with `NativeOutput`:

```python
from pydantic_ai import Agent, NativeOutput

agent = Agent(
    model,
    output_type=NativeOutput(
        [TaskOutput],
        name='task_output',
        description='Generated assessment task'
    ),
)
```

Output validators run after schema validation:
```python
@agent.output_validator
async def validate_task(ctx: RunContext, output: TaskOutput) -> TaskOutput:
    if not output.code_files.get("README.md"):
        raise ModelRetry('Task must include a README.md')
    return output
```

### 20.5 DBOS Durable Execution (STABLE)

Checkpoints every step to Postgres or SQLite. On crash, resumes from last checkpoint:

```python
from dbos import DBOS, DBOSConfig
from pydantic_ai.durable_exec.dbos import DBOSAgent

dbos_config: DBOSConfig = {
    'name': 'task_generator',
    'system_database_url': os.environ["SUPABASE_URL"]  # reuse Supabase Postgres
}
DBOS(config=dbos_config)

dbos_agent = DBOSAgent(agent)
result = await dbos_agent.run(scenario)  # checkpointed automatically
```

**Limitations**: Uses `pickle` for serialization — deps and tool outputs must be pickle-serializable. Keep checkpointed data under ~2 MB. Custom tools need explicit `@DBOS.step` decoration for I/O operations.

### 20.6 Context Management

**Provider-native compaction** for Anthropic:
```python
from pydantic_ai.capabilities import AnthropicCompaction
agent = Agent('anthropic:claude-opus-4-6', capabilities=[AnthropicCompaction(token_threshold=150_000)])
```

**Third-party `summarization-pydantic-ai`** package provides:
- `ContextManagerCapability` — real-time token tracking, auto-compression at threshold
- `SlidingWindowCapability` — zero-cost message trimming
- `LimitWarnerCapability` — "finish soon" hint before context limit

For our use case: generators are short-lived (~15-25K tokens). Context management is not a Phase 1 concern.

### 20.7 Cost Tracking (STABLE)

```python
result = await agent.run('Generate a Go BASIC task')
print(result.usage())
# Usage(requests=3, request_tokens=5200, response_tokens=8100, total_tokens=13300)
```

Usage is summed across all requests in a run. Share across agents via `usage=ctx.usage`. Budget enforcement via `pydantic-ai-shields`:
```python
from pydantic_ai_shields import CostTracking
agent = Agent('openai:gpt-5.1', capabilities=[CostTracking(budget_usd=0.50)])
```

### 20.8 Pydantic AI vs LangGraph (Benchmarks)

| Metric | Pydantic AI | LangGraph |
|--------|------------|-----------|
| P95 Latency | 1.8s | 3.2s |
| Error rate under load | 1x baseline | 5x baseline |
| Token consumption | 1x baseline | 2.7x baseline |
| Code for same app | ~160 lines | ~280 lines (75% more) |

Emerging 2026 pattern: Pydantic AI for agent logic + LangGraph for orchestration when needed. For our system, Pydantic AI + Prefect covers both.

---

## 21. Workflow Orchestration: Prefect 3

> Why Prefect over Temporal, Hatchet, Inngest, or plain asyncio.

### 21.1 Comparison

| Criterion | Prefect 3 | Temporal | Hatchet | Inngest | asyncio+Supabase |
|-----------|-----------|----------|---------|---------|-----------------|
| Integration effort | **~1 day** | ~1-2 weeks | ~2-3 days | ~3-5 days | ~2-3 days |
| Retry + state | Built-in caching | Event replay | Checkpoint resume | Step transactions | Manual (~80 lines) |
| Parallel execution | `ConcurrentTaskRunner` | asyncio in workflow | Native DAG | Fan-out | `asyncio.gather()` |
| Free tier | Generous (seat-based) | Dev namespace only | $5/mo credits | 50K exec/mo | Free |
| Python-native | Yes | Yes (with determinism constraints) | Yes | TypeScript-first | Yes |
| Maturity | Production (years) | Production (years) | Production (1B+ tasks/mo) | Production | N/A |

### 21.2 Why Prefect Wins

1. **Caching solves the retry problem**: If eval (step 6) fails, rerun the flow — steps 1-5 return cached LLM responses instantly without re-calling APIs or spending tokens.

2. **ConcurrentTaskRunner**: One line to run 5 generators in parallel.

3. **Zero infrastructure**: Run locally or free cloud tier. No Temporal server, no Hatchet Postgres, no Inngest webhooks.

4. **Decorator-based**: Add `@flow`/`@task` to existing functions. Keep Click CLI.

### 21.3 Implementation

```python
from prefect import task, flow
from prefect.task_runners import ConcurrentTaskRunner
from prefect.cache_policies import INPUTS
from datetime import timedelta

@task(retries=3, retry_delay_seconds=10, cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
async def generate_task_with_llm(scenario: dict, guidelines: str) -> TaskOutput:
    """LLM call. Cached on retry — no re-generation if later steps fail."""
    return await generator_agent.run(scenario + guidelines)

@task(retries=2)
async def evaluate_task(task_output: TaskOutput) -> EvalResult:
    """Cross-provider eval. If this fails, generate_task_with_llm is cached."""
    return await eval_agent.run(task_output)

@task(retries=3, retry_delay_seconds=5)
async def publish_to_github(task_output: TaskOutput) -> str:
    """GitHub API can timeout. Retries automatically."""
    return create_template_repo(task_output)

@flow(name="generate-task-batch", task_runner=ConcurrentTaskRunner())
async def generate_batch(requests: list[GenerationRequest]):
    """Generate N tasks in parallel with full durability."""
    futures = [generate_single_task.submit(req) for req in requests]
    results = [f.result() for f in futures]
    # Coordinator cross-review
    approved = await coordinator_review(results)
    # Publish approved tasks
    for task in approved:
        await publish_to_github.submit(task)
```

### 21.4 Upgrade Path

If we outgrow Prefect's durability (unlikely for task generation): **Hatchet** is the natural next step — Postgres-backed (works with Supabase), MIT licensed, production-proven at 1B+ tasks/month.

**Supabase Realtime** complements any orchestrator for progress tracking — subscribe to `task_generation_runs` table changes for real-time UI updates.

---

## 22. Code Sandbox & Verification Infrastructure

### 22.1 Sandbox Options

| Tool | Cold Start | Price/hr | Docker Builds | Best For |
|------|-----------|----------|---------------|---------|
| **E2B** | ~150ms | ~$0.05 | No (Firecracker VMs) | General code execution, test running |
| **Daytona** | ~90ms | ~$0.08 | OCI-compatible | Persistent workspaces with cached toolchains |
| **Modal** | <1s | ~$0.14 | OCI images (not Docker directly) | GPU tasks, ML model verification |
| **Fly.io Machines** | ~200ms | ~$0.07 | **Yes** (full VM) | Docker build verification |
| **Testcontainers** | 2-10s per service | Free (local Docker) | Yes | Database/service integration tests |
| **Self-hosted Docker** | 0ms (already running) | Free | Yes | Simplest for Docker-heavy tasks |
| **CodeSandbox SDK** | ~2s | Subscription | No | Frontend (React/Next.js) only |

### 22.2 Recommended Tiered Architecture

**Tier 1: Static Analysis** (< 1 second, $0) — Run on every generated file:
- **tree-sitter** (`tree-sitter-language-pack`, 305+ languages) — syntax parsing in microseconds
- **ast-grep** — structural verification rules in YAML ("must have main function", "must not import os.system")
- **hadolint** — Dockerfile linting
- **yamllint** — YAML validation
- **markdown-it-py** — README section checking

**Tier 2: Compilation & Test Execution** (5-30 seconds, ~$0.01-0.05) — Run after Tier 1 passes:
- **E2B or Daytona sandbox** — compile code + run test suite in isolated microVM
- **SWE-bench pattern**: tests FAIL on starter, PASS on answer
- Pre-build environment snapshots per language to minimize cold start

**Tier 3: Infrastructure Verification** (30-120 seconds, ~$0.05-0.20) — Run on final candidates:
- **Testcontainers** — spin up real Postgres/Kafka/Redis for integration tests
- **Fly.io Machines** — for Docker build verification (only option reliably supporting Docker-in-Docker)
- **Self-hosted Docker** — `docker compose config` + `docker compose up` for Docker tasks

### 22.3 ast-grep for Structural Verification

ast-grep (Rust-native, tree-sitter-based) enables structural code rules in YAML:

```yaml
# Verify generated Go code has a main function
id: go-must-have-main
language: go
rule:
  pattern: |
    func main() {
      $$$BODY
    }
message: "Generated Go code must have a main() function"
severity: error

# Verify React component exports default
id: react-must-export-default
language: tsx
rule:
  pattern: export default $COMPONENT
message: "React component must have a default export"
severity: error
```

### 22.4 Cost at Scale

| Tasks/day | Tier 1 Cost | Tier 2 Cost | Tier 3 Cost | Total |
|-----------|-------------|-------------|-------------|-------|
| 10 | $0 | $0.10-0.50 | $0.50-2.00 | ~$2.50 |
| 100 | $0 | $1.00-5.00 | $5.00-20.00 | ~$25 |
| 1000 | $0 | $10-50 | $50-200 | ~$250 |

Tier 1 is free (local compute). Tier 3 is optional — only for Docker/infrastructure archetypes.

---

## 23. LLM Evaluation: Replacing evals.py

### 23.1 Tool Selection

| Tool | Stars | Fit | Pricing | Use For |
|------|-------|-----|---------|---------|
| **DeepEval** | 14.8k | **Primary** — pytest integration, custom G-Eval metrics, CI/CD | Free (open source) | Replace `evals.py` with structured, archetype-aware metrics |
| **promptfoo** | 20.1k | **Regression testing** — YAML-driven, CI integration | Free (MIT). Acquired by OpenAI March 2026 | Catch prompt regressions on template changes |
| **Opik** | — | **Observability** — trace full generation pipeline, free self-hosted | Free (Apache 2.0) | Debug generation failures, track latency per step |
| **Portkey analytics** | — | **Cost tracking** — per-request cost by archetype/tech/proficiency | Already using | Tag metadata for granular cost breakdown |

**Skip**: Patronus AI (overkill), Galileo (Cisco acquisition), LangSmith (overlaps Portkey), Weave (requires W&B ecosystem).

### 23.2 DeepEval Integration

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Define archetype-specific eval metrics
task_realism = GEval(
    name="Task Realism",
    criteria="The task scenario is realistic and could occur in a real engineering team. "
             "The problem is specific enough to test real competency, not generic busywork.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    model="anthropic:claude-opus-4-6",  # cross-provider: GPT generates, Claude evaluates
)

difficulty_calibration = GEval(
    name="Difficulty Calibration",
    criteria=f"The task is appropriate for {proficiency} proficiency level "
             f"({yoe} years of experience). A candidate at this level should be able to "
             f"complete it in {time_constraint} minutes.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)

solution_leakage = GEval(
    name="No Solution Leakage",
    criteria="The starter code, README, and hints do NOT reveal the solution. "
             "The candidate must figure out the approach themselves.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
)

# Run evaluation
test_case = LLMTestCase(
    input=f"Generate {archetype} task for {tech_stack} at {proficiency}",
    actual_output=json.dumps(task_output.model_dump()),
)
task_realism.measure(test_case)
difficulty_calibration.measure(test_case)
solution_leakage.measure(test_case)
```

### 23.3 Cross-Model Judging

**2026 research finding**: Using the same model for generation and evaluation has ~40% inconsistency due to self-preference bias. Cross-model judging is critical:

| Generator Model | Evaluator Model | Why |
|----------------|-----------------|-----|
| GPT-5.1 | Claude Opus 4.6 | Different training data, different blind spots |
| Claude Opus 4.6 | GPT-5.1 | Same benefit, reversed |

For pairwise comparisons: evaluate both (A,B) and (B,A) orderings. Only count consistent wins. This eliminates position bias.

### 23.4 Immediate Win: Portkey Metadata Enrichment

You already use Portkey. Tag every request with archetype, tech_stack, proficiency:

```python
# In utils.py generate_task_with_code(), add headers:
headers = {
    "x-portkey-metadata": json.dumps({
        "archetype": archetype,
        "tech_stack": tech_stack,
        "proficiency": proficiency,
        "eval_attempt": attempt_number,
        "run_id": run_id
    })
}
```

This gives you per-archetype and per-technology cost analytics in the Portkey dashboard for free.

---

## 24. Knowledge Management & Prompt Optimization

### 24.1 Phase 1: File-Based Retrieval (No Vector DB Needed)

For Phase 1, decomposed knowledge chunks (Section 8.2) are loaded by file path:

```python
def load_guidelines(tech: str, proficiency: str, task_type: str) -> str:
    """Assemble relevant knowledge for a generation request."""
    chunks = []
    chunks.append(read_file(f"knowledge/tech/{tech}/project-structure.md"))
    chunks.append(read_file(f"knowledge/tech/{tech}/code-style.md"))
    chunks.append(read_file(f"knowledge/proficiency/{proficiency}.md"))
    chunks.append(read_file(f"knowledge/task-type/{task_type}.md"))
    chunks.append(read_file("knowledge/shared/readme-rules.md"))
    chunks.append(read_file("knowledge/shared/output-schema.md"))
    return "\n\n---\n\n".join(chunks)
```

This is simple, fast, and sufficient for 15 tech stacks × 4 proficiency levels × 7 archetypes.

### 24.2 Phase 2: Chroma for Semantic Retrieval

When you need to retrieve relevant knowledge for NEW combinations (tech stacks not yet in the knowledge base):

```python
import chromadb

client = chromadb.Client()
knowledge = client.create_collection("task_knowledge")

# Index all knowledge chunks
knowledge.add(
    documents=[chunk.content for chunk in all_chunks],
    metadatas=[{"tech": c.tech, "type": c.type, "proficiency": c.proficiency} for c in all_chunks],
    ids=[c.id for c in all_chunks]
)

# At generation time: retrieve relevant chunks
results = knowledge.query(
    query_texts=[f"Generate a {tech_stack} {proficiency} {task_type} task"],
    n_results=8,
    where={"$or": [{"tech": tech_stack}, {"tech": "shared"}]}
)
```

**Chroma over Qdrant**: At 1K-10K documents, Chroma runs in-process with zero infrastructure. Qdrant is the upgrade path if metadata filtering becomes complex.

### 24.3 Context7 MCP for Live Documentation

Context7 provides up-to-date, version-specific documentation for 9,000+ libraries. Integrate at generation time to prevent hallucinated APIs:

```python
# At generation time, fetch current docs for the tech stack
from context7 import resolve_library, query_docs

lib_id = resolve_library("fastapi")
docs = query_docs(lib_id, topic="dependency injection", tokens=2000)
# Inject into generator context alongside knowledge chunks
```

This ensures generated React code uses React 19 patterns (not React 16), generated FastAPI code uses current `Depends()` syntax, etc.

### 24.4 DSPy Prompt Optimization (Phase 3)

**When**: After collecting 50+ human-rated tasks per archetype.

**How**: Define each archetype's generation as a DSPy module, then optimize with MIPROv2:

```python
import dspy

class CodeBuildGenerator(dspy.Signature):
    """Generate a CODE_BUILD assessment task."""
    tech_stack: str = dspy.InputField()
    proficiency: str = dspy.InputField()
    scenario: str = dspy.InputField()
    guidelines: str = dspy.InputField()
    task_output: str = dspy.OutputField(desc="JSON task with code_files, outcomes, etc.")

# MIPROv2 optimizes the instruction text + few-shot examples
optimizer = dspy.MIPROv2(
    metric=lambda example, pred: human_quality_score(pred.task_output),
    num_candidates=10,
    max_bootstrapped_demos=5,
)
optimized_generator = optimizer.compile(
    CodeBuildGenerator(),
    trainset=rated_tasks_dataset,  # 50+ human-rated tasks
)
```

MIPROv2 has shown up to 13% accuracy improvement over hand-tuned prompts. At 271+ tasks, even 5% improvement saves significant human review.

**Start now**: Every task reviewed by a human gets a 1-5 rating in the `task_ratings` table. This is passive data collection that doesn't block anything.

---

## 25. Recommended Tool Stack (Final)

### The Complete Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RECRUITER INPUT                               │
│  "5 Java+Kafka debugging tasks, senior, fintech"                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PYDANTIC AI  +  PORTKEY GATEWAY                                     │
│                                                                      │
│  Intake Agent ──► Coordinator ──┬──► Generator #1 (GPT-5.1)        │
│  (Claude or GPT)  (Claude Opus) │    Generator #2 (GPT-5.1)        │
│                                  │    Generator #3 (GPT-5.1)        │
│                                  │    ... (parallel via Graph API)   │
│                                  │                                   │
│                                  ├──► Eval Agents (Claude Opus)     │
│                                  │    (cross-provider, fresh context)│
│                                  │                                   │
│                                  └──► Publish Agent (deterministic)  │
│                                                                      │
│  VERIFICATION TOOLS (per generator):                                 │
│  ├── tree-sitter (syntax, 305 languages)                            │
│  ├── ast-grep (structural rules, YAML-defined)                      │
│  ├── lizard (complexity calibration)                                │
│  ├── hadolint + yamllint (Docker/YAML)                              │
│  ├── markdown-it-py (README sections)                               │
│  └── Pydantic models (schema validation)                            │
│                                                                      │
│  DEEP VERIFICATION (Phase 3):                                        │
│  ├── E2B / Daytona (sandbox code execution)                         │
│  ├── Testcontainers (Postgres/Kafka/Redis)                          │
│  └── SWE-bench pattern (fail-to-pass)                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PREFECT 3  (workflow durability)                                    │
│                                                                      │
│  @flow: generate_batch ──► @task: generate (cached, retried)        │
│                          ──► @task: evaluate (cross-provider)       │
│                          ──► @task: publish (retried on API timeout) │
│                          ──► @task: store_supabase                  │
│                                                                      │
│  ConcurrentTaskRunner for parallel generation                        │
│  INPUTS cache policy — never re-generate on retry                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  EVALUATION & OBSERVABILITY                                          │
│                                                                      │
│  DeepEval (structured metrics, CI/CD, pytest)                       │
│  Portkey Analytics (cost per archetype/tech/proficiency)            │
│  Opik (pipeline tracing, free self-hosted)          [Phase 2]       │
│  promptfoo (regression tests on prompt changes)     [Phase 2]       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  KNOWLEDGE & OPTIMIZATION                                            │
│                                                                      │
│  knowledge/ directory (decomposed prompt files)     [Phase 1]       │
│  Context7 MCP (live library documentation)          [Phase 2]       │
│  Chroma (semantic knowledge retrieval)              [Phase 2]       │
│  DSPy + MIPROv2 (prompt optimization)               [Phase 3]       │
│  SemHash (task deduplication)                       [Phase 2]       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STORAGE & STATE                                                     │
│                                                                      │
│  Supabase: tasks, competencies, task_generation_runs,               │
│            task_ratings, task_embeddings                             │
│  GitHub: template repos, answer repos, gists                        │
│  DigitalOcean: droplet deployment (existing)                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase-by-Phase Tool Adoption

| Phase | New Tools | Why Now |
|-------|----------|---------|
| **Phase 1** (2-3 weeks) | Pydantic AI, Prefect `@flow`/`@task`, tree-sitter, lizard, markdown-it-py, Portkey metadata tags | Self-correcting generation loop with real verification. Zero new infrastructure. |
| **Phase 2** (4-6 weeks) | DeepEval, ast-grep, SemHash, Chroma, Context7, promptfoo, Opik | Structured evaluation, knowledge retrieval, dedup, regression testing. |
| **Phase 3** (6-8 weeks) | E2B/Daytona, Testcontainers, DSPy + MIPROv2, SWE-bench pattern | Sandbox execution, prompt optimization, empirical difficulty calibration. |
| **Phase 4** (8-12 weeks) | Qdrant (if needed), Inngest (event triggers), Supabase Realtime (progress UI) | Production scale, event-driven generation, real-time dashboards. |

### What We Explicitly Don't Need

| Tool | Why Not |
|------|---------|
| LangGraph | Pydantic AI + Prefect covers orchestration. 75% more code for the same functionality. |
| Temporal | Overkill — designed for multi-day workflows. Our pipeline runs in minutes. |
| CrewAI | Role-playing abstraction doesn't fit structured generation pipeline. |
| AutoGen | Ecosystem fragmented (4 competing versions). |
| LangSmith | Overlaps with Portkey analytics. |
| LiteLLM | Redundant with Portkey gateway. |
| Patronus AI | Enterprise/regulated focus. DeepEval is free and sufficient. |
| Galileo AI | Being acquired by Cisco. Strategic direction uncertain. |
| Knowledge graphs (Neo4j) | Premature at 15 tech stacks. JSON taxonomy is sufficient. |
