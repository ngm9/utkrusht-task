# Session Log — Python+SQL Tasks + Prompt Generator Agent

> Date: 2026-05-04 → 2026-05-05
> Author: Rohan + Claude
> Branch: `feat/python-sql-tasks` (Python+SQL work) + `feat/prompt-generator` (agent)

This is a chronological summary of two related streams of work: (1) creating the
first Python + SQL combined-stack tasks end-to-end, and (2) building a DSPy-powered
agent that auto-generates new task generation prompt files.

---

## 1. Python + SQL Task Creation

### Goal

Create two combined-stack tasks (Python + SQL) — one BASIC, one INTERMEDIATE —
following Naman's guidance that combined skill tasks must be "homogeneous" (all
components naturally fit together).

### Pipeline used

```
1. generate_input_files   →  competency + background JSONs (existing tool)
2. scenario_generator     →  task scenarios JSON (existing tool)
3. (manual) prompt template  →  task_generation_prompts/Basic|Intermediate (NEW for this combo)
4. multiagent generate_tasks  →  actual task + GitHub repo + Gist + Supabase row
```

### Artifacts created

#### Input files

| Path | Description |
|---|---|
| `task_input_files/input_python_sql/basic/input_python_sql_basic_task/competency_python_sql_basic_Utkrusht.json` | Combined Python + SQL BASIC competencies |
| `task_input_files/input_python_sql/basic/input_python_sql_basic_task/background_forQuestions_utkrusht_python_sql_basic.json` | LLM-generated role context |
| `task_input_files/input_python_sql/intermediate/...` | Same for INTERMEDIATE |

Generated via:
```bash
python -m generate_input_files --name "Python" --name "SQL" --proficiency BASIC
python -m generate_input_files --name "Python" --name "SQL" --proficiency INTERMEDIATE
```

Cost: ~$0.005 each (2 LLM calls per run).

#### Scenarios

Added to `task_input_files/task_scenarios/task_scenarios.json` and `task_scenarios_intermediate.json`:
- 2 BASIC scenarios under key `"Python (BASIC), SQL (BASIC)"` — quiz-score CSV importer + expiring-subscriptions endpoint
- 2 INTERMEDIATE scenarios under key `"Python (INTERMEDIATE), SQL (INTERMEDIATE)"` — fintech spend-summary optimizer + HR pipeline counts

Generated via:
```bash
python -m scenario_generator --competency-file <path> --count 2 --append
```

Cost: ~$0.01-0.02 per run.

#### Prompt templates (manually written)

| Path | Lines | Notes |
|---|---|---|
| `task_generation_prompts/Basic/python_sql_basic_prompt.py` | 270 | Adapted from `python_basic_prompt.py` + `SQL_basic_prompt.py` |
| `task_generation_prompts/Intermediate/python_sql_intermediate_prompt.py` | 250 | Adapted to add INTERMEDIATE complexity (caching, indexing, connection pooling) |

Both register `PROMPT_REGISTRY` with the alphabetically-sorted key
`"Python (LEVEL), SQL (LEVEL)"`. Category: `script_and_db` — Python script that
talks to PostgreSQL via psycopg2, with Docker-based DB infrastructure but NO
web framework.

#### Tasks generated

| Task | Level | Task ID | Repo |
|---|---|---|---|
| `quiz-score-importer-fix` | BASIC | `66615566-849a-4d7f-8227-fa1bb808b27e` | https://github.com/UtkrushtApps/quiz-score-importer-fix |
| `fintech-spend-summary-optimizer` | INTERMEDIATE | `4a64c937-25c9-4d66-9fad-d57cb4e5e6a6` | https://github.com/UtkrushtApps/fintech-spend-summary-optimizer |

A duplicate `quiz-score-import-fix` was generated then deleted.

#### Position created in Supabase

| Field | Value |
|---|---|
| Position ID | `b3f91812-84f6-4de2-9506-7ae59a0d3a63` |
| Title | Python + SQL Developer |
| Org | Experimental AI (`dc1bf217-a83b-4db7-82de-a4e310e766e9`) |
| Experience | BASIC |
| Competencies | Python (BASIC) + SQL (BASIC) |

A `class` row was added to link the position to a class_id (the recruiter web
app requires this for scheduling task sessions).

### Bugs fixed during this work

#### `multiagent.py` — unicode escape in docstring

Original docstring contained Windows paths with `\U...` which Python interpreted
as unicode escape sequences:

```python
# Before — broken
"""
python "c:\Utkrushta\..."
"""

# After — fixed (raw string)
r"""
python multiagent.py generate-tasks ...
"""
```

#### `schemas.py` — Anthropic API rejected `additionalProperties: object`

The original `ANSWER_CODE_SCHEMA` used:

```python
"files": {
    "type": "object",
    "additionalProperties": {"type": "string"}   # rejected by Anthropic
}
```

Anthropic's structured output validation requires `additionalProperties` to be
either `false` or absent. We restructured to an array of `{path, content}` objects:

```python
"files": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {"path": ..., "content": ...},
        "additionalProperties": False
    }
}
```

`generate_answer_code_and_steps()` was updated to convert the array back to a
dict after parsing for downstream compatibility.

NOTE: `schemas.py` was later reverted to its original schema by the user — this
is a known issue still affecting answer repo generation (the first task,
`quiz-score-importer-fix`, has an empty answer repo because of this).

---

## 2. Prompt Generator Agent

### Motivation

Hand-writing each new task generation prompt file (~200-300 lines of Python)
takes ~30 min and produces inconsistent results. From Naman's recent task
list, ~15 new prompt files are needed (Llamaindex, Vector DBs, Microservices,
Spring MVC, Kafka, etc.) — manual work would take days.

### Design

Generator → Verifier → Refiner agent loop using DSPy.

```
KNOWLEDGE BASE
  - 60+ existing prompt files in task_generation_prompts/
  - Supabase tasks (criterias, task_blob, eval_info, is_enabled)
  - Supabase competencies (scope field as truth source)
       ↓
RETRIEVER (rule-based, pure Python)
  - 5-level fallback ladder
  - Returns 3-5 reference prompt files
       ↓
GENERATOR (DSPy ChainOfThought)
  - Input: competencies + proficiency + references + scopes + similar tasks
  - Output: candidate .py file
       ↓
VERIFIER (DSPy ChainOfThought)
  - Reads candidate + references + scopes
  - 4 hard-fail checks: scope, category, structure, no leaks
  - Output: passes? + feedback
       ↓
   passes?
   ├── YES → VALIDATOR (deterministic Python checks) → WRITE FILE
   └── NO → feedback back to generator (max 5 iterations)
```

Full design doc: `docs/research/prompt-generator-agent.md`
Architecture diagram: `docs/research/prompt-generator-architecture.excalidraw`

### Package structure

```
prompt_generator/
├── __init__.py        # Package metadata
├── __main__.py        # CLI entry point (Click)
├── classifier.py      # Rule-based task category detection (10 categories)
├── retriever.py       # 5-level fallback ladder for reference selection
├── db_queries.py      # Supabase fetching (similar tasks + competency scopes)
├── validator.py       # Deterministic post-generation checks
├── agent.py           # DSPy module with Generate ↔ Verify loop
├── trainset.py        # Build training examples from prompts + DB
├── metric.py          # Quality scoring function
├── compile.py         # CLI for BootstrapFewShot / MIPROv2 compilation
└── compiled/
    └── agent_bootstrap.json  # Compiled program (4 demos baked in)
```

### Components

#### 1. Classifier (`classifier.py`)

Rule-based mapping from competency names to infrastructure category:
`PURE_CODE`, `DB_ONLY`, `SCRIPT_AND_DB`, `APP_AND_DB`, `FRONTEND`,
`LLM_FRAMEWORK`, `VECTOR_DB`, `MESSAGING`, `MICROSERVICES`, `NON_CODE`.

Tested on 14 known combinations — all classified correctly.

Key heuristic: backend language + DB + no framework = `script_and_db` (Python+SQL),
backend lang + DB + framework = `app_and_db` (FastAPI+Postgres), JS-family + DB
= `app_and_db` (Node+Postgres conventionally implies Express).

#### 2. Retriever (`retriever.py`)

5-level fallback ladder for picking reference prompts:

| Level | Match type |
|---|---|
| 1 | Exact match at requested proficiency |
| 2 | Same combination at adjacent proficiency |
| 3 | Per-competency at this level + tech-family siblings |
| 4 | Per-competency at any level |
| 5 | Same-category prompts at this level |

Sets `bootstrap_mode=True` if no exact match (Level 1 missed).

Tech-family map encodes adjacencies: Llamaindex ≈ Langchain, MongoDB ≈ PostgreSQL,
NodeJs ≈ ExpressJS, etc.

#### 3. DB Queries (`db_queries.py`)

Three queries against Supabase dev:
- `fetch_tasks_for_competency(name, proficiency)` — single-competency tasks
- `fetch_tasks_for_combination(names, proficiency)` — exact combo tasks
- `fetch_competency_scope(name, proficiency)` — the `scope` text field

Returns lightweight `TaskExample` objects (not full `task_blob` to keep
prompt context small).

#### 4. Validator (`validator.py`)

Deterministic checks after LLM generation:
- Parses as Python (`ast.parse`)
- Has `PROMPT_REGISTRY` definition
- Registry key matches expected format (alphabetical or input-order)
- Contains all required `{format_vars}`: `organization_background`, `role_context`,
  `competencies`, `real_world_task_scenarios`

#### 5. Agent (`agent.py`)

The DSPy module. Two `dspy.ChainOfThought` modules wired in a loop:
- `GeneratePromptSignature` — generator with strict scope-binding instructions
- `VerifyPromptSignature` — verifier with 4 hard-fail conditions

Generator instructions made `competency_scopes` AUTHORITATIVE — the agent must
stay within the scope text from Supabase. Verifier separated HARD-FAIL (must
reject) from SOFT-FAIL (don't block) checks for practical pass-bar.

#### 6. Trainset (`trainset.py`)

Walks `task_generation_prompts/` and parses each filename into
`(competencies, proficiency)`. Joins with Supabase to compute a quality signal
(`is_enabled` task exists).

Found 64 training pairs total:
- 26 with quality signal (enabled DB task exists)
- 41 with any DB task
- 23 with no DB tasks

#### 7. Metric (`metric.py`)

Scoring function for DSPy compilation:
- Structural validity (gated — must pass)
- Section coverage (Jaccard on markdown headers)
- Code files coverage (Jaccard on filenames)
- Length similarity (ratio of shorter to longer)

Self-similarity test: a prompt scored against itself returns 1.0.
Cross-similarity test: Java prompt vs Python prompt returns 0.0 (registry key mismatch fails the gate).

#### 8. Compile (`compile.py`)

CLI for DSPy compilation. Supports `bootstrap` (cheap) or `miprov2` (expensive).

Usage:
```bash
python -m prompt_generator.compile \
  --optimizer bootstrap \
  --max-examples 64 \
  --no-require-quality-signal \
  --model openrouter/deepseek/deepseek-chat-v3.1
```

### CLI usage

```bash
# Dry run (preview without writing)
python -m prompt_generator --name "Python, Llamaindex" --proficiency BASIC --dry-run

# Real run (generates and writes the .py file)
python -m prompt_generator --name "Python, Llamaindex" --proficiency BASIC

# With explicit model override
python -m prompt_generator --name "..." --proficiency BASIC --model openrouter/deepseek/deepseek-chat-v3.1
```

If `prompt_generator/compiled/agent_bootstrap.json` exists, demos are auto-loaded
into the generator (set via `--compiled-path "" ` to disable).

### Tests run during development

#### Test 1: Python+SQL BASIC reproduction

Generated `python_sql_basic_prompt.py` from scratch in bootstrap mode (Level 4
fallback — no exact match). Compared with the hand-written version on
`feat/python-sql-tasks` branch:

| | Hand-written | Agent-generated |
|---|---|---|
| Lines | 270 | 283 |
| Registry key | `Python (BASIC), SQL (BASIC)` | matches ✓ |
| Format vars | All 5 | All 5 ✓ |
| Headers | 20 sections | 27 (more granular) |
| Code files | 8 | 7 |

Result: structurally equivalent. Agent-generated had cleaner naming
convention. Generated file deleted post-test.

#### Test 2: NodeJs+MongoDB BASIC iteration test

3 runs to test signature improvements:

| Run | Verifier passed? | Iterations |
|---|---|---|
| Old signatures + 3 iter max | ❌ No (scope violation) | 3/3 |
| New signatures + 5 iter max | ✅ Yes | 2 |
| Compiled (1 pass, no verify) | n/a | 1 |

Signature improvements made `competency_scopes` AUTHORITATIVE, which fixed the
"async/await required at BASIC" scope violation the verifier had been catching.

Quality vs hand-written:
- Uncompiled: 0.5104
- Compiled: **0.7418** (+45% relative improvement)

#### Test 3: Python+Vector Databases BASIC (compiled run)

After compiling with DeepSeek + 64 pairs (4 demos baked in), generated
Python+Vector Databases BASIC:

- **Verifier passed in 1 iteration**
- Validation: PASS
- Cost: ~$0.10
- Sensible code_files spec for vector DB task (no web framework, separate
  modules for ingestion/search/db connection, Docker setup)

### Key decisions

#### Why DSPy (not raw LLM calls)

| | Raw LLM | DSPy |
|---|---|---|
| Auto-tune meta-prompts | No (hand-written) | Yes (MIPROv2 / BootstrapFewShot) |
| Reproducible compilation | Manual | Saves JSON artifact |
| Swap models easily | Manual | `dspy.settings.configure()` |
| Generator + Verifier loop | We code it | Built-in `dspy.Module` |

DSPy turns the generator/verifier into compilable programs. Few-shot demos and
meta-prompts get auto-tuned against a metric.

#### Why DeepSeek V3 (not gpt-5.4 or Sonnet)

Cost comparison (per 1M tokens, May 2026):

| Model | Input | Output | Notes |
|---|---|---|---|
| Qwen 3 Coder (free) | $0 | $0 | Free, rate-limited |
| **DeepSeek V3.2** | **$0.27** | **$1.10** | Frontier-quality, ~5x cheaper than Haiku |
| gpt-5.4 (gpt-5-nano) | $0.50 | $2.00 | Already wired via Portkey |
| Haiku 4.5 | $1.00 | $5.00 | Already wired via Portkey |
| Sonnet 4.6 | $3.00 | $15.00 | Strong but expensive |

Tradeoffs:
- DeepSeek V3 is frontier-quality at 1/100 of Sonnet's cost
- gpt-5.4 is already wired and only ~2x more expensive than DeepSeek
- For one-shot compilation, DeepSeek wins on cost
- For long-term: stay with what's wired (gpt-5.4) for simplicity

#### Why NOT CLIProxyAPI / subscription bypass

User asked about CLIProxyAPI to route through Claude Max subscription instead
of paying API costs.

Researched on Reddit, GitHub, news sources. Found:
- April 4, 2026: Anthropic blocked third-party harnesses from Max subscription
- 1.45M accounts banned in H2 2025 (only 3.3% appeal success)
- January 9, 2026: Active technical safeguards against proxies
- GitHub issue #2211 on CLIProxyAPI repo: user reported account banned

Decision: hard pass on subscription proxies. ToS risk + rate limits + reliability
concerns outweigh ~$2 savings on compilation.

### Compilation results (DeepSeek V3, 64 pairs)

Ran:
```bash
python -m prompt_generator.compile --optimizer bootstrap --max-examples 64 \
  --no-require-quality-signal --model openrouter/deepseek/deepseek-chat-v3.1
```

Result:
- 4 demos saved (max_bootstrapped_demos default cap)
- Demos picked greedily from highest-quality pairs:
  1. Java (INTERMEDIATE) — 25 DB tasks
  2. Java (BASIC) — 19 DB tasks
  3. PostgreSQL (BASIC) — 17 DB tasks
  4. Python (BASIC) — 10 DB tasks
- Compilation took 99s
- Cost: ~$0.30
- Saved to `prompt_generator/compiled/agent_bootstrap.json` (157.6 KB)

### Cost summary for the full session

| Activity | Calls | Approx cost |
|---|---|---|
| Python+SQL input files (BASIC + INTERMEDIATE) | ~4 | ~$0.01 |
| Python+SQL scenarios (BASIC + INTERMEDIATE) | ~10 | ~$0.05 |
| 2 task generations (multiagent) | ~30 | ~$1.50 |
| Prompt generator dev/testing | ~50 | ~$3 |
| DSPy compilation runs (multiple) | ~20 | ~$1 |
| **Total session cost** | **~115** | **~$5-6** |

### What's next

#### Short-term (when ready to use prompt generator at scale)

1. Wire `prompt_generator` into the unified pipeline so a single command runs
   `generate_input_files → prompt_generator → scenario_generator → multiagent generate_tasks`
2. Generate the ~15 new prompt files for Naman's task list:
   - Python + Langchain (BASIC, INTERMEDIATE)
   - Python + Llamaindex (BASIC, INTERMEDIATE)
   - Python + Vector Databases (BASIC, INTERMEDIATE)
   - Python + RAGs (INTERMEDIATE)
   - Java + Spring MVC (BEGINNER, BASIC, INTERMEDIATE)
   - Java + Spring Webservices (BASIC, INTERMEDIATE)
   - Microservices (BASIC, INTERMEDIATE)
   - Kafka (INTERMEDIATE)
   - PostgreSQL Schema/Indexing/Large-Scale + Python+FastAPI
3. Manually review each generated prompt before committing.

#### Medium-term

1. Re-compile with `max_bootstrapped_demos=8` to cover more combined-stack
   patterns (Java+SpringBoot, Node+Postgres) — costs ~$0.60 more per compile.
2. Consider MIPROv2 if BootstrapFewShot quality plateaus — would tune the
   meta-prompt instructions, not just demo selection. ~$5-10 cost.
3. Fix the `schemas.py` Anthropic-compatibility issue once and for all (currently
   reverted; affects answer repo generation).

#### Long-term

1. Re-compile periodically as the DB grows with more eval-passed tasks (the
   trainset improves as production data accumulates).
2. Add MIPROv2 compilation pipeline as an option for higher quality.
3. Consider a `human-in-the-loop` review step that auto-flags generated prompts
   needing manual edit before commit.

---

## Files added/modified in this session

### Added

```
prompt_generator/
├── __init__.py
├── __main__.py
├── classifier.py
├── retriever.py
├── db_queries.py
├── validator.py
├── agent.py
├── trainset.py
├── metric.py
├── compile.py
└── compiled/
    └── agent_bootstrap.json

task_input_files/input_python_sql/
├── basic/input_python_sql_basic_task/
│   ├── competency_python_sql_basic_Utkrusht.json
│   └── background_forQuestions_utkrusht_python_sql_basic.json
└── intermediate/input_python_sql_intermediate_task/
    ├── competency_python_sql_intermediate_Utkrusht.json
    └── background_forQuestions_utkrusht_python_sql_intermediate.json

task_generation_prompts/Basic/python_sql_basic_prompt.py            (on feat/python-sql-tasks)
task_generation_prompts/Intermediate/python_sql_intermediate_prompt.py  (on feat/python-sql-tasks)

docs/research/
├── prompt-generator-agent.md
├── prompt-generator-architecture.excalidraw
└── session-log-prompt-generator.md  (this file)
```

### Modified

- `requirements.txt` — added `dspy-ai`
- `multiagent.py` — fixed unicode escape in docstring; updated to handle array-format
  files in `generate_answer_code_and_steps`
- `schemas.py` — restructured `ANSWER_CODE_SCHEMA` for Anthropic API (later reverted)
- `task_input_files/task_scenarios/task_scenarios.json` — added Python+SQL BASIC scenarios
- `task_input_files/task_scenarios/task_scenarios_intermediate.json` — added Python+SQL INTERMEDIATE scenarios

### Database changes (Supabase dev)

- Added position `b3f91812-84f6-4de2-9506-7ae59a0d3a63` (Python + SQL Developer)
- Added class `a76e9943-e412-43d4-89c7-bd5ad6716ca9` linked to position
- Created task `66615566-849a-4d7f-8227-fa1bb808b27e` (quiz-score-importer-fix)
- Created task `4a64c937-25c9-4d66-9fad-d57cb4e5e6a6` (fintech-spend-summary-optimizer)
- Deleted task `6655a6fc-307e-4533-85ca-f5d3fc0da607` (duplicate quiz-score-import-fix)
- Set `paid_assessments_count = -1` on Experimental AI org (unlimited credits)

---

## References

- DSPy: https://dspy.ai/
- BootstrapFewShot docs: https://dspy.ai/api/optimizers/BootstrapFewShot/
- MIPROv2 docs: https://dspy.ai/api/optimizers/MIPROv2/
- Reflexion paper: https://arxiv.org/abs/2303.11366
- Self-Refine paper: https://arxiv.org/abs/2303.17651
- OpenRouter pricing: https://openrouter.ai/models
- DeepSeek V3.1 model card: https://openrouter.ai/deepseek/deepseek-chat-v3.1
