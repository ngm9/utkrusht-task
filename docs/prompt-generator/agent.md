# Prompt Generator — Architecture, Design & Operating Guide

> **Single-source documentation for the `prompt_generator/` package.**
> Decision: ship uncompiled. Compilation experiments empirically regressed quality.
> The infrastructure for compilation is built and disabled.

---

## Table of contents

1. [TL;DR](#tldr)
2. [The decision: uncompiled wins](#the-decision-uncompiled-wins)
3. [What the agent does](#what-the-agent-does)
4. [Pipeline overview](#pipeline-overview)
5. [Module-by-module breakdown](#module-by-module-breakdown)
6. [The five context signals](#the-five-context-signals)
7. [Full walkthrough — Python + SQL BASIC](#full-walkthrough--python--sql-basic)
8. [The Generate ⇄ Verify ⇄ Validate loop](#the-generate-verify-validate-loop)
9. [What DSPy gives us](#what-dspy-gives-us)
10. [Compilation — what it is, why we tried, why we stopped](#compilation--what-it-is-why-we-tried-why-we-stopped)
11. [What's in the `compiled/` folder right now](#whats-in-the-compiled-folder-right-now)
12. [How to run the prompt generator](#how-to-run-the-prompt-generator)
13. [Configuration knobs](#configuration-knobs)
14. [Common errors and fixes](#common-errors-and-fixes)
15. [Future work](#future-work)

---

## TL;DR

`prompt_generator/` is an agent that produces **task-generation prompt template files**
(e.g. `task_generation_prompts/Basic/python_sql_basic_prompt.py`) for any
`(competencies, proficiency)` combination.

```
input  : ("Python, SQL", "BASIC")
            │
            ▼  via DSPy agent (Generate ⇄ Verify ⇄ Validate loop)
            │
output : task_generation_prompts/Basic/python_sql_basic_prompt.py
            │
            ▼  consumed by multiagent.py at runtime
            │
result : actual coding tasks the candidate sees
```

The agent gathers 5 context signals from your codebase + Supabase, asks one LLM to
**Generate** a prompt template, asks a second LLM to **Verify** it against 4
hard-fail rules, then runs a deterministic Python **Validator**. If anything fails,
it loops with feedback up to 5 times. Once approved, writes the file.

**Compilation (few-shot demos baked into the prompt) was built, tested 3 times, and
disabled** — all experiments showed negative lift. The agent currently runs
**uncompiled** at ~0.74–0.97 metric score on diverse holdouts.

---

## The decision: uncompiled wins

We tested compilation 4 ways. All regressed:

```
┌─────────────────────────────────────────────────┬────────┬───────────────────────┐
│                   Experiment                    │ Setup  │         Lift          │
├─────────────────────────────────────────────────┼────────┼───────────────────────┤
│ Hand-built, gpt-4.1-mini, 4 demos               │ $0     │ -0.675 (catastrophic) │
│ Sonnet 4 compile, 23 pairs, 3 demos, 2 holdouts │ ~$1    │ -0.035                │
│ Sonnet 4 compile, 30 pairs, 3 demos, 8 holdouts │ ~$1    │ -0.021                │
│ Blind regen, HTML+CSS, Sonnet 4 demos           │ ~$0.30 │ -0.173                │
└─────────────────────────────────────────────────┴────────┴───────────────────────┘
```

### Why compilation hurts on this codebase

```
                  agent.forward() at runtime
                            │
                            ▼
   ┌──────────────────────────────────────────────────────┐
   │ Already-rich context for every call (uncompiled):    │
   │                                                       │
   │   • signature docstring (the rules)                  │
   │   • competency_scopes  (Supabase, per-combo)         │
   │   • reference_prompts  (retriever, per-combo)        │
   │   • similar_tasks      (Supabase, per-combo)         │
   │   • detailed_skill_signal (input_files, per-combo)   │
   │   • verifier's 4 hard-fails                          │
   │   • deterministic validator                          │
   └──────────────────────────────────────────────────────┘
                            +
                  fixed 3-4 worked examples
                            =
              redundant structural signal that
                  drifts cross-category
```

The per-call signals (especially `reference_prompts` from the 5-level fallback
ladder) already do the structural-pattern job that compiled demos are supposed
to do — **and they do it per-combo**, not fixed. Adding 3 fixed demos creates
cross-category contamination (see the HTML+CSS regression in §10).

### What we ship

| Component | Status |
|---|---|
| `prompt_generator/` package | ✅ Production-ready, uncompiled mode |
| Generate ⇄ Verify ⇄ Validate loop | ✅ Working |
| 5 context signals all wired | ✅ Working |
| `agent_bootstrap.json` (compiled demos) | ❌ Absent. Three failed attempts kept aside for forensics |
| Registry-key cleanup of 26 broken files | ✅ Applied |

---

## What the agent does

When you invoke:

```bash
python -m prompt_generator --name "Python, SQL" --proficiency BASIC
```

the agent produces a `.py` file that registers a `PROMPT_REGISTRY` entry the
existing `multiagent.py` pipeline can consume to generate actual tasks.

```
┌────────────────────────────────────────────────────────────────────┐
│ The PROMPT GENERATOR's job                                          │
│                                                                     │
│   You ask for:  "Python, SQL" + BASIC                              │
│                       │                                            │
│                       ▼                                            │
│   It produces:  task_generation_prompts/Basic/                     │
│                 python_sql_basic_prompt.py                         │
│                       │                                            │
│                       ▼                                            │
│   The file contains:                                               │
│     PROMPT_PYTHON_SQL_BASIC_CONTEXT       = """..."""              │
│     PROMPT_PYTHON_SQL_BASIC_INPUT_AND_ASK = """..."""              │
│     PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS  = """..."""              │
│     PROMPT_REGISTRY = {                                            │
│         "Python (BASIC), SQL (BASIC)": [                           │
│             PROMPT_PYTHON_SQL_BASIC_CONTEXT,                       │
│             PROMPT_PYTHON_SQL_BASIC_INPUT_AND_ASK,                 │
│             PROMPT_PYTHON_SQL_BASIC_INSTRUCTIONS,                  │
│         ]                                                          │
│     }                                                              │
│                                                                     │
│   That file is then used by multiagent.py to generate              │
│   actual candidate-facing tasks.                                   │
└────────────────────────────────────────────────────────────────────┘
```

The agent is **scope-respecting** (bounded by `competency.scope`),
**complexity-calibrated** (bounded by `role_context` + `proficiency`), and
**category-correct** (bounded by `task_category`).

---

## Pipeline overview

```
                    ┌─────────────────────────────────┐
                    │  CLI: python -m prompt_generator│
                    │  --name "Python, SQL" -p BASIC  │
                    └─────────────────┬───────────────┘
                                      │
                                      ▼
                ┌───────────────────────────────────────┐
                │   __main__.py                          │
                │   • parse args                         │
                │   • configure DSPy LLM provider        │
                │   • load compiled demos (if present)   │
                │   • call agent(...)                    │
                └─────────────────┬─────────────────────┘
                                  │
                                  ▼
              ┌──────────────────────────────────────────┐
              │   agent.forward()                        │
              │   pure-Python orchestration              │
              └──────────────────────────────────────────┘
                                  │
   ┌──────────────────────────────┼──────────────────────────────────┐
   │                              │                                  │
   │  STEP 1: classifier.py       │   pure rules, no I/O             │
   │  ────────────────────────    │   competencies → task_category   │
   │                              │                                  │
   │  STEP 2: retriever.py        │   filesystem glob, no I/O        │
   │  ────────────────────────    │   5-level fallback ladder        │
   │                              │   → 2-5 reference prompt files   │
   │                              │                                  │
   │  STEP 3: db_queries.py       │   Supabase queries               │
   │  ────────────────────────    │   → competency.scope per comp    │
   │                              │   → 5-7 enabled+eval-passed tasks│
   │                              │                                  │
   │  STEP 4: input_files.py      │   local file glob                │
   │  ────────────────────────    │   → role_context                 │
   │                              │   → questions_prompt             │
   │                              │   → 3 example scenarios          │
   │                              │   (bundled as detailed_skill_    │
   │                              │    signal; empty if missing)     │
   │                              │                                  │
   │  STEP 5: assemble payload    │   build context strings          │
   │  ────────────────────────    │                                  │
   │                              │                                  │
   │  STEP 6: Generate ⇄ Verify   │   2 LLM calls per attempt        │
   │           ⇄ Validate loop    │   max 5 attempts, feedback flows │
   │  ────────────────────────    │   into each next attempt         │
   │                              │                                  │
   └──────────────────────────────┴──────────────────────────────────┘
                                  │
                                  ▼
                ┌───────────────────────────────────────┐
                │   write task_generation_prompts/      │
                │   Basic/python_sql_basic_prompt.py    │
                └───────────────────────────────────────┘
```

---

## Module-by-module breakdown

| File | Role | LLM? |
|---|---|---|
| `__main__.py` | CLI entry point. Parses args, configures DSPy, instantiates agent, writes file. | ❌ |
| `classifier.py` | Pure Python rules: competency mix → `TaskCategory` enum. | ❌ |
| `retriever.py` | Filesystem reader. 5-level fallback ladder for finding reference prompts. | ❌ |
| `db_queries.py` | Supabase reader. Pulls `competency.scope` + enabled+eval-passed similar tasks. | ❌ |
| `input_files.py` | Local file reader. Bundles `role_context` + `questions_prompt` + scenarios into `detailed_skill_signal`. | ❌ |
| `agent.py` | DSPy module. Holds `GeneratePromptSignature` + `VerifyPromptSignature`, runs the loop. | ✅ |
| `validator.py` | Deterministic AST + regex check on generated source. | ❌ |
| `trainset.py` | Builds training data from existing prompts (used only by compile). | ❌ |
| `metric.py` | `[0.0, 1.0]` scoring function comparing predicted prompt to gold. | ❌ |
| `compile.py` | Offline compiler that picks few-shot demos (currently disabled). | ✅ |
| `compiled/agent_bootstrap.json` | Optional artifact with picked demos. Not present today. | n/a |

**LLM is touched only in two places**: inside `agent.forward()`'s Generate/Verify
steps at runtime, and inside `compile.py` at compile time. Everything else is
plain Python.

---

## The five context signals

The agent feeds five context sources to the LLM. Three come from Supabase, two from
the local filesystem. Together they give the LLM enough material to write a
prompt template scoped correctly to the requested combo.

```
                ╔═══════════════════════════════════════════╗
                ║       THE 5 CONTEXT SIGNALS                ║
                ║       (all fed to the Generate LLM call)   ║
                ╚═══════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────┐
  │ 1. competency_scopes      (db_queries.py — Supabase)            │
  │    AUTHORITATIVE skill bounds. ~2K chars per competency.        │
  │    Source of truth for what the candidate CAN and CAN'T be      │
  │    asked. Verifier's #1 hard-fail check is against this.        │
  └─────────────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────────────┐
  │ 2. reference_prompts      (retriever.py — local files)          │
  │    2-5 existing prompt files via 5-level fallback ladder.       │
  │    Provides STRUCTURAL template — section ordering, JSON shape, │
  │    README format. ~10-60K chars total.                          │
  └─────────────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────────────┐
  │ 3. similar_tasks          (db_queries.py — Supabase)            │
  │    5-7 actual tasks from prod that match this combo,            │
  │    is_enabled + eval_info.passed. ~1-2K chars of summaries.     │
  │    Calibrates complexity, file count, question style.           │
  └─────────────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────────────┐
  │ 4. detailed_skill_signal  (input_files.py — local files)        │
  │    BUNDLED:                                                     │
  │      • questions_prompt — 30 sub-skill bullets                  │
  │      • role_context — candidate YoE + day-to-day responsibilities│
  │      • 3 example scenarios from task_scenarios.json             │
  │    ~2-4K chars total. EMPTY for brand-new combos (graceful).    │
  └─────────────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────────────┐
  │ 5. task_category          (classifier.py — pure Python)         │
  │    Enum from rules-based classifier. One of:                    │
  │      pure_code, db_only, script_and_db, app_and_db,             │
  │      frontend, llm_framework, vector_db, messaging,             │
  │      microservices, non_code                                    │
  │    HARD CONSTRAINT — determines file shape (Docker yes/no,      │
  │    web framework yes/no, etc.)                                  │
  └─────────────────────────────────────────────────────────────────┘

       +  feedback_from_previous_attempt   (verifier output, loop only)
```

The **5-level retriever fallback ladder** deserves its own diagram:

```
   Looking for reference prompts for: Rust + ScyllaDB (BASIC)

   Level 1: exact match at this level
   ─────────────────────────────────────────
   Search Basic/ for files containing "rust" AND "scylladb"
   Found? No → drop to Level 2 (bootstrap_mode = True)

   Level 2: same combo at adjacent proficiency
   ─────────────────────────────────────────
   Search Beginner/ and Intermediate/ for same combo
   Found? No → drop to Level 3

   Level 3: per-competency at this level + tech-family siblings
   ─────────────────────────────────────────
   Search Basic/ for any Rust file. Found? Add.
   Search Basic/ for any ScyllaDB file. Found? Add.
   Search Basic/ for tech-family (cassandra, mongodb) siblings.
   Result: 1 reference found.

   Level 4: per-competency at any level
   ─────────────────────────────────────────
   Search Intermediate/, Beginner/ for Rust or ScyllaDB files.
   Add what we find.

   Level 5: any prompt in the same task_category
   ─────────────────────────────────────────
   Add ~2 prompts matching task_category=db_only or app_and_db
   for structural template.

   Final references: 3-5 files at fallback_level 4 or 5
```

---

## Full walkthrough — Python + SQL BASIC

Concrete trace of every step the agent takes.

### Step 0 — User invokes the CLI

```bash
PYTHONPATH=. .venv/bin/python -m prompt_generator \
    --name "Python, SQL" --proficiency BASIC --env dev --verbose
```

### Step 1 — `classifier.py`

```python
competencies = [Competency("Python", "BASIC"), Competency("SQL", "BASIC")]
category = classify_task_category(competencies)
# Pure rules:
#   has_db        = True   (SQL matches _DB_TOKENS)
#   has_backend   = True   (Python matches _BACKEND_LANG_TOKENS)
#   has_framework = False  (no FastAPI/Flask/etc.)
#   has_web_app   = False  (Python NOT in _WEB_APP_LANG_TOKENS)
# Result: TaskCategory.SCRIPT_AND_DB
```

Output: `"script_and_db"`.

### Step 2 — `retriever.py`

```
Level 1 search: Basic/ files matching "python" AND "sql"
  → python_sql_basic_prompt.py  FOUND

Level 1+ category examples: pull 1-2 more script_and_db prompts
  → mongodb_python_basic_prompt.py
  → (also others, capped at max_refs=5)

Result:
  bootstrap_mode = False
  fallback_level = 1
  references = [
    python_sql_basic_prompt.py,        # 16K chars
    mongodb_python_basic_prompt.py,    # 22K chars
    ...
  ]
```

### Step 3 — `db_queries.py`

```
fetch_similar_tasks(supabase, ["Python", "SQL"], "BASIC")
→ 5-7 TaskExample objects, each with:
    • task_id, title, question (~280c), code_file_names, eval_passed

fetch_competency_scope(supabase, "Python", "BASIC")
→ scope text (~1.8K chars from competencies.scope)

fetch_competency_scope(supabase, "SQL", "BASIC")
→ scope text (~1.8K chars)
```

### Step 4 — `input_files.py`

```
slug = "python_sql"

Looking for background file under task_input_files/input_python_sql*/...
  Scanning input_python_sql/
    Candidate: background_forQuestions_utkrusht_python_sql_basic.json
    Picked (best slug-token overlap)

bg = json.load(...)
  questions_prompt = bg["questions_prompt"]   # 30 bullets, ~1300 chars
  role_context     = bg["role_context"]       # 800 chars

scenarios = task_scenarios.json
  Key: "Python (BASIC), SQL (BASIC)"
  Result: 2 scenarios loaded

Bundled detailed_skill_signal: ~4K chars
```

### Step 5 — Build context strings

```
competencies               27 chars   "Python (BASIC), SQL (BASIC)"
proficiency                 5 chars   "BASIC"
task_category              13 chars   "script_and_db"
competency_scopes        3649 chars
reference_prompts       80256 chars   (full source of 2-5 files)
similar_tasks            1941 chars
detailed_skill_signal    4027 chars
feedback_from_previous_attempt  0 chars   (first attempt)
```

### Step 6 — Generate ⇄ Verify ⇄ Validate loop (attempt 1)

```
─── GENERATE ─────────────────────────────────────────
LLM call: dspy.ChainOfThought(GeneratePromptSignature)
Input: all 8 fields above
Output:
  rationale       : "The competencies are Python+SQL at BASIC.
                     task_category is script_and_db, so I need
                     Docker + Postgres + a Python script with no
                     web framework. The scopes say no window
                     functions..." (~1K chars, discarded)
  new_prompt_file : ~15K chars of Python source

─── VERIFY ───────────────────────────────────────────
LLM call: dspy.ChainOfThought(VerifyPromptSignature)
Input: candidate + same context as Generate
Output:
  passes   : true
  feedback : ""

─── VALIDATE (deterministic) ─────────────────────────
ast.parse(source)                        ✓
"PROMPT_REGISTRY" in source              ✓
registry key == "Python (BASIC), SQL (BASIC)"  ✓
format vars present                      ✓
top-level prompt variables present       ✓

─── LOOP DECISION ────────────────────────────────────
verify_out.passes AND validation.passed  →  BREAK
```

### Step 7 — Write the file

```
output_path = task_generation_prompts/Basic/python_sql_basic_prompt.py
output_path.write_text(new_prompt, encoding="utf-8")
```

Done. One iteration. Two LLM calls. Total time ~60-90 seconds with Sonnet 4.

---

## The Generate ⇄ Verify ⇄ Validate loop

The heart of the agent. Up to 5 iterations, feedback flows between them.

```
                        ┌────────────────────┐
                        │  feedback = ""     │
                        │  (empty first time)│
                        └─────────┬──────────┘
                                  │
                                  ▼
                ┌──────────────────────────────────┐
                │  GENERATE                        │
                │  ChainOfThought(GenerateSig)     │
                │                                  │
                │  inputs: 8 fields (incl feedback)│
                │  outputs:                        │
                │    rationale       (discarded)   │
                │    new_prompt_file (kept)        │
                └─────────────────┬────────────────┘
                                  │
                                  ▼
                ┌──────────────────────────────────┐
                │  VERIFY                          │
                │  ChainOfThought(VerifySig)       │
                │                                  │
                │  Checks 4 HARD-FAIL conditions:  │
                │    1. SCOPE VIOLATION            │
                │    2. CATEGORY MISMATCH          │
                │    3. STRUCTURAL DAMAGE          │
                │    4. SOLUTION LEAK              │
                │                                  │
                │  outputs:                        │
                │    passes  (bool)                │
                │    feedback (str)                │
                └─────────────────┬────────────────┘
                                  │
                                  ▼
                ┌──────────────────────────────────┐
                │  VALIDATE (deterministic)        │
                │                                  │
                │  • ast.parse(source) succeeds    │
                │  • PROMPT_REGISTRY present       │
                │  • registry key is alpha-sorted  │
                │    "Name (LEVEL), Name (LEVEL)"  │
                │  • all 5 format vars present     │
                │  • 3 prompt vars defined         │
                │                                  │
                │  outputs:                        │
                │    passed (bool)                 │
                │    issues (list[str])            │
                └─────────────────┬────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────┐
                │ verifier.passes AND          │
                │ validator.passed?            │
                └────────┬───────────┬─────────┘
                         │ YES       │ NO
                         ▼           ▼
                ┌──────────┐  ┌───────────────────────┐
                │ BREAK    │  │ feedback =            │
                │ write    │  │   verifier.feedback   │
                │ to disk  │  │   +                   │
                └──────────┘  │   validator.issues    │
                              │ attempt += 1          │
                              │ goto GENERATE         │
                              └───────────────────────┘
                              if attempt >= 5: BREAK
                              (use last result)
```

### Why two LLM calls (Generate + Verify) instead of one?

If the same LLM both writes AND critiques, it tends to confirm its own output —
self-critique is biased. A separate `VerifyPromptSignature` with **different
instructions** (focused on 4 hard-fail conditions only) acts as a real adversary.

### Why ChainOfThought wraps both?

Adds an automatic `reasoning` output field that forces the LLM to write out
its thinking BEFORE its final answer. For Generate, this means thinking
through scope/category/format-vars before writing code. For Verify, this means
explicitly checking each hard-fail condition before voting pass/fail. The
reasoning is discarded — but writing it improves the final answer.

### What "feedback" looks like in iteration 2+

```
Reviewer feedback:
1. Scope violation: candidate prompt requires window functions
   (line 47: ROW_NUMBER() OVER ...). SQL BASIC scope explicitly
   excludes window functions. Remove and use GROUP BY + COUNT.

Deterministic validator issues (MUST fix):
- PROMPT_REGISTRY key 'Python+SQL' does not match expected
  'Python (BASIC), SQL (BASIC)'.
```

This text is fed back into `Generate` as
`feedback_from_previous_attempt`. The docstring tells Generate:
*"When non-empty, every issue mentioned MUST be addressed in the new output."*

---

## What DSPy gives us

DSPy turns LLM calls into **typed functions with declarative signatures**.
Without DSPy you'd have hand-rolled f-string templates and brittle JSON parsers
everywhere.

```
┌─────────────────────────────────────────────────────────────────┐
│  DSPy Feature           │   What you'd write by hand without it │
├─────────────────────────────────────────────────────────────────┤
│  dspy.Signature class   │   200-line f-string template          │
│  dspy.ChainOfThought    │   Manual "think step by step" prompt  │
│                         │   + manual reasoning extraction       │
│  Typed output fields    │   json.loads + regex extraction       │
│                         │   + retry on malformed                │
│  dspy.Module composition│   Inline procedural code with strings │
│  configure_dspy()       │   Provider-specific HTTP clients      │
│  Compilation framework  │   Roll your own search algorithm      │
└─────────────────────────────────────────────────────────────────┘
```

### A signature is a Python class declaring inputs / outputs / rules

```python
class GeneratePromptSignature(dspy.Signature):
    """[Full docstring — the rules. Includes HARD CONSTRAINT sections
    for scope, structure, category, proficiency.]"""

    competencies:           str = dspy.InputField(desc="…")
    proficiency:            str = dspy.InputField(desc="…")
    task_category:          str = dspy.InputField(desc="…")
    competency_scopes:      str = dspy.InputField(desc="…")
    reference_prompts:      str = dspy.InputField(desc="…")
    similar_tasks:          str = dspy.InputField(desc="…")
    detailed_skill_signal:  str = dspy.InputField(desc="…")
    feedback_from_previous_attempt: str = dspy.InputField(desc="…")

    new_prompt_file:        str = dspy.OutputField(desc="…")
```

You declare this **once**, in code. DSPy uses it every time `self.generate(...)`
is called to:
1. Render the system prompt from the docstring + field descriptors.
2. Render the user message from your input values.
3. Send to the LLM.
4. Parse the response back into typed attributes (`gen_out.new_prompt_file`,
   `gen_out.reasoning`).

You never write a string template manually.

### `ChainOfThought` is one line that adds a reasoning scaffold

```python
self.generate = dspy.ChainOfThought(GeneratePromptSignature)
```

That's it. The LLM now writes reasoning first, answer second. You get the
clean answer in `gen_out.new_prompt_file`. The reasoning in `gen_out.reasoning`
is automatic and discardable.

### Provider abstraction is one function

```python
configure_dspy(model="openai/gpt-5.4")              # Portkey → OpenAI
configure_dspy(model="anthropic/claude-sonnet-4-6") # Portkey → Anthropic
configure_dspy(model="openrouter/google/gemma-4-26b-a4b-it:free")
```

Same agent code, three different providers.

### Verdict

Even with compilation disabled, DSPy is paying for itself just on the signature +
ChainOfThought + provider abstraction features alone. The agent code is ~200
lines instead of ~800.

---

## Compilation — what it is, why we tried, why we stopped

### What compilation does

```
   ┌───────────────────────────────────────────────────────────┐
   │ Compilation = offline search for the best few-shot demos  │
   │                                                            │
   │ Input:                                                     │
   │   ~30 quality (input, gold_output) pairs from your        │
   │   codebase, filtered by Supabase quality signal.          │
   │                                                            │
   │ Process:                                                   │
   │   For each pair, run the agent on its inputs.             │
   │   Score the agent's output against the gold using         │
   │   metric.py.                                              │
   │   Keep the first 3 that score above threshold.            │
   │                                                            │
   │ Output:                                                    │
   │   agent_bootstrap.json containing 3 demos.                │
   │                                                            │
   │ At runtime:                                                │
   │   Those 3 demos get prepended to every LLM call.          │
   └───────────────────────────────────────────────────────────┘
```

### Why we expected it to help

```
Theory: examples beat instructions. If the LLM sees 3 concrete
worked (input, output) examples before generating, it should
produce outputs more reliably matching the codebase's style.
```

### Why it didn't help, in detail

#### Reason 1 — Redundant signal

```
Already gets from the per-call context:
  ✓ docstring rules (structural format)
  ✓ reference_prompts (per-combo structural template — same job as demos)
  ✓ similar_tasks (per-combo style calibration)
  ✓ verifier 4 hard-fails (structural drift catcher)
  ✓ deterministic validator

Adding fixed demos = a 4th source of structural pattern, on top of
3 sources that already match the target combo better.
```

#### Reason 2 — Cross-category contamination (proven empirically)

Blind regen of `html_css_basic_prompt.py` after restoring Sonnet 4 demos
(Java, PostgreSQL, NodeJs+MongoDB):

```
┌─────────────────────────────────────────────────────────────┐
│ Gold HTML+CSS uses flat ## H2 section structure              │
│                                                              │
│  ## GOAL                                                     │
│  ## INSTRUCTIONS                                             │
│  ## AI AND EXTERNAL RESOURCE POLICY:                         │
│  ## Code Generation Instructions:                            │
│                                                              │
│ Uncompiled regen reproduces this flat ## structure.          │
│ Score: 0.967  (near-perfect)                                 │
│                                                              │
│ Compiled regen with 3 Java/Postgres demos:                   │
│ The demos use nested ### H3. Model imports that nesting     │
│ into HTML output:                                            │
│                                                              │
│  # HTML & CSS Basic Task Requirements                        │
│  ## GOAL                                                     │
│  ## INSTRUCTIONS                                             │
│  ### Nature of the Task                                      │
│  ### Task Scenario Structure                                 │
│  ### CRITICAL REQUIREMENTS FOR FULLY FUNCTIONAL ENVIRONMENT  │
│  ### AI and External Resource Policy                         │
│                                                              │
│ Score: 0.794  (drifted to demos' style)                     │
│ Δ: -0.173                                                    │
└─────────────────────────────────────────────────────────────┘

Mechanism:
  LLM has 4 sources of structural signal:
    1. references for HTML+CSS (flat ##)
    2. demos for Java/Postgres   (nested ###)
    3. docstring rules
    4. similar_tasks
  LLM tries to "average" → output drifts to fusion style.
```

#### Reason 3 — Trainset too small for safe selection

```
30 quality pairs total
─────────────────────
  C(30, 3) = 4,060 possible 3-demo combinations
  but constrained by task_category diversity → ~50-100 useful
  ones

  BootstrapFewShot needs holdout samples to score each combo.
  With ~10 holdout, variance per sample is ±0.10.
  Averaged variance over 10 samples is ±0.03.

  Lift signal we'd need to detect: +0.05 minimum.
  Statistically reliable detection requires variance < 0.02,
  which requires 25-40 holdout samples.

  At 30 trainset pairs, we can't have 25 holdout AND meaningful
  trainset. Need ~50+ pairs minimum.
```

#### The empirical record

```
Hand-built (4 picks, gpt-4.1-mini):     -0.675   catastrophic
Sonnet 4 compile, 23 pairs:             -0.035   ~noise
Sonnet 4 compile, 30 pairs:             -0.021   ~noise
Blind regen, HTML+CSS, Sonnet 4 demos:  -0.173   measurable drift
```

Three independent experiments, all negative. Not statistical fluke.

### When compilation WOULD help (none apply to us)

```
┌─────────────────────────────────────────────┬─────────────────────────────────┐
│ Condition                                   │ Your situation                  │
├─────────────────────────────────────────────┼─────────────────────────────────┤
│ Weak runtime model (Haiku, free models)     │ ❌ Using GPT-5.4 / Sonnet       │
│ No reference prompts available              │ ❌ Have 30+ quality references  │
│ Empty detailed_skill_signal for most combos │ ❌ Most combos have input files │
│ Need strict byte-level consistency          │ ❌ Not your use case            │
│ Trainset > 50 quality pairs                 │ ❌ Have 30                      │
└─────────────────────────────────────────────┴─────────────────────────────────┘
```

### Final decision

```
✓ Ship uncompiled. Permanent.
✗ Don't run compile again unless trainset grows past 50 quality pairs
  AND a specific quality regression appears that demos could target.
```

---

## What's in the `compiled/` folder right now

Three artifacts, all disabled. They're kept for forensics; runtime ignores
them because none of them is named `agent_bootstrap.json` (the active name).

```
prompt_generator/compiled/
├── agent_bootstrap.handbuilt.disabled.json    424 KB
│       Hand-built by me. 4 demos picked by diversity heuristic:
│       • PostgreSQL (BASIC)        category: db_only
│       • Java (BASIC)              category: pure_code
│       • NodeJs+MongoDB (INT)      category: app_and_db
│       • Python+SQL (BASIC)        category: script_and_db
│       Result on gpt-4.1-mini: -0.675 (catastrophic).
│       Model copied demo variable names into output → broken registry.
│
├── agent_bootstrap.regressed.json             214 KB
│       Sonnet 4 BootstrapFewShot, 23-pair trainset. 3 demos:
│       • Java (BASIC)
│       • PostgreSQL (BASIC)
│       • AI Evals for Product Managers (BASIC)
│       Result on Sonnet 4: -0.035 (noise).
│
└── agent_bootstrap.regressed.gemma.json       256 KB
        Sonnet 4 BootstrapFewShot, 30-pair trainset. 3 demos:
        • Java (INTERMEDIATE)
        • Java (BASIC)
        • PostgreSQL (BASIC)
        Filename misleading — Gemma was rate-limited, fell back to Sonnet 4.
        Result on Sonnet 4: -0.021 (noise).
```

The runtime CLI looks for `agent_bootstrap.json`. None exists → CLI prints
*"No compiled file at … — running uncompiled"* → agent runs without any demos.
**This is the desired state.**

You can safely delete all 3 files. They're kept only for forensic value
(future devs can inspect "what compile picked, why it didn't help").

---

## How to run the prompt generator

### Minimum command — uncompiled, dry-run, verbose

```bash
cd /home/rsx/Desktop/utkrusht-ai/utkrusht-task

PYTHONPATH=. .venv/bin/python -m prompt_generator \
    --name "Python, SQL" \
    --proficiency BASIC \
    --env dev \
    --compiled-path "" \
    --dry-run \
    --verbose
```

What each flag does:

```
--name "Python, SQL"      competencies, comma-separated
--proficiency BASIC       BEGINNER / BASIC / INTERMEDIATE / ADVANCED
--env dev                 Supabase environment (dev or prod)
--compiled-path ""        empty string = uncompiled mode
--dry-run                 generate to memory, do NOT write the file
--verbose                 step-by-step DEBUG logging
```

### Write the file (drop --dry-run, add --force if it already exists)

```bash
PYTHONPATH=. .venv/bin/python -m prompt_generator \
    --name "Python, SQL" \
    --proficiency BASIC \
    --env dev \
    --compiled-path "" \
    --force \
    --verbose
```

### Cwd-immune one-liner (subshell)

Useful if you're not in the project directory:

```bash
( cd /home/rsx/Desktop/utkrusht-ai/utkrusht-task && \
  PYTHONPATH=. .venv/bin/python -m prompt_generator \
      --name "Python, SQL" --proficiency BASIC --env dev \
      --compiled-path "" --dry-run --verbose )
```

### Brand-new combo (no references, no input files)

```bash
PYTHONPATH=. .venv/bin/python -m prompt_generator \
    --name "Rust, ScyllaDB" --proficiency BASIC \
    --compiled-path "" --dry-run --verbose
```

You'll see retriever fall through to levels 4-5 in the logs.
`input_files` will show `background_found=False`, `signal_chars=0`.
The agent still produces a valid prompt file using just scopes +
retriever fallbacks.

### Save the trace to a file

```bash
PYTHONPATH=. .venv/bin/python -m prompt_generator \
    --name "Python, SQL" --proficiency BASIC \
    --compiled-path "" --dry-run --verbose \
    2>&1 | tee /tmp/promptgen_trace.log

# Then later:
less /tmp/promptgen_trace.log
grep "STEP\|→" /tmp/promptgen_trace.log
```

A copy is also appended to `agent_task_creator.log` in cwd (from
`logger_config.py`).

---

## Configuration knobs

### CLI flags

| Flag | Default | Effect |
|---|---|---|
| `--name "X, Y"` | required | Competencies |
| `--proficiency` | required | BEGINNER / BASIC / INTERMEDIATE / ADVANCED |
| `--env` | `dev` | Supabase env (dev / prod) |
| `--dry-run` | off | Don't write the .py file |
| `--force` | off | Overwrite existing file |
| `--max-iterations` | `5` | Cap on Generate ⇄ Verify loop |
| `--model "openai/gpt-4.1-2025-04-14"` | env / `openai/gpt-5.4` | LLM override |
| `--compiled-path "path/to.json"` | `prompt_generator/compiled/agent_bootstrap.json` | Compiled demos file. `""` = uncompiled |
| `--verbose` / `-v` | off | Step-by-step logs |

### Environment variables (`.env`)

| Var | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI key (used via Portkey gateway) |
| `PORTKEY_API_KEY` | Portkey gateway key |
| `SUPABASE_URL_APTITUDETESTSDEV` | Supabase dev URL |
| `SUPABASE_API_KEY_APTITUDETESTSDEV` | Supabase dev key |
| `SUPABASE_URL_APTITUDETESTS` | Supabase prod URL |
| `SUPABASE_API_KEY_APTITUDETESTS` | Supabase prod key |
| `OPENROUTER_API_KEY` | Optional, for `--model openrouter/…` |
| `PROMPT_GENERATOR_MODEL` | Runtime model override (defaults `openai/gpt-5.4`) |
| `PROMPT_GENERATOR_COMPILE_MODEL` | Compile-time model (defaults `anthropic/claude-haiku-4-5`) |
| `LOG_FILE` | Override log file path (defaults `agent_task_creator.log`) |

### What `--verbose` shows

```
[INFO ] ========================================================================
[INFO ] AGENT START — competencies=['Python', 'SQL'] proficiency=BASIC env=dev
[INFO ] ========================================================================

[INFO ] STEP 1 / classifier.py — deciding task_category
[INFO ]   → task_category = script_and_db

[INFO ] STEP 2 / retriever.py — running 5-level fallback ladder
[INFO ]   → bootstrap_mode = False
[INFO ]   → fallback_level = 1
[INFO ]   → references found: 5
[INFO ]       • python_sql_basic_prompt.py
[INFO ]       • mongodb_python_basic_prompt.py
[DEBUG]       ladder: Level 1 (exact match): python_sql_basic_prompt.py

[INFO ] STEP 3 / db_queries.py — Supabase env=dev
[INFO ]   fetching similar tasks for ['Python', 'SQL'] ...
[INFO ]   → similar tasks fetched: 7
[INFO ]   fetching competency.scope for Python (BASIC) ...
[INFO ]     → scope text: 1842 chars

[INFO ] STEP 4 / input_files.py — building detailed_skill_signal
[DEBUG] input_files: scanning input_python_sql
[DEBUG] input_files: picked background_forQuestions_utkrusht_python_sql_basic.json
[INFO ]   → background_found  = True
[INFO ]   → total signal      = 4027 chars

[INFO ] STEP 5 — context payload sizes for the LLM call
[INFO ]   competencies                  27 chars
[INFO ]   reference_prompts          80256 chars

[INFO ] STEP 6 — Generate ⇄ Verify ⇄ Validate loop (max_iterations=5)
[INFO ]   ── attempt 1 / 5 ──
[INFO ]   calling Generate (ChainOfThought)...
[INFO ]     Generate done — new_prompt_file: 15234 chars, rationale: 1078 chars
[INFO ]   calling Verify (ChainOfThought)...
[INFO ]     Verify done — passes=True feedback=0 chars
[INFO ]     validator passed=True registry_key='Python (BASIC), SQL (BASIC)'
[INFO ]   ✓ both verifier and validator passed at attempt 1 — exiting loop

[INFO ] AGENT DONE — generated 15234 chars over 1 iteration(s)
```

---

## Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: prompt_generator` | Missing `PYTHONPATH=.` or wrong cwd | Set `PYTHONPATH=.` and run from project root |
| `AuthenticationError: invalid x-api-key` | LiteLLM grabbed `ANTHROPIC_API_KEY` directly, bypassing Portkey | `unset ANTHROPIC_API_KEY` or use an `openai/*` model |
| `OpenAI's reasoning models require temperature=1.0` | Using `gpt-5` / `gpt-5-nano` (reasoning model) | Use `openai/gpt-4.1-2025-04-14` instead |
| `File already exists: …` | Output path exists | Add `--force` or move the existing file aside |
| `NO SCOPE found for …` warning | Competency name doesn't match Supabase exactly | Check `competencies` table for the canonical name |
| Hangs on `calling Generate` | LLM call in progress; 30-120s normal | Be patient. Use `Ctrl+C` to abort cleanly |
| `litellm.RateLimitError: 429` | Free OpenRouter model rate-limited | Use a paid model or try again later |
| `Verifier did not pass after 5 iteration(s)` | LLM couldn't satisfy verifier rules within budget | Inspect `verifier_feedback` in output. May need to adjust scope or task_category |

---

## Future work

These are the only conditions under which we should reconsider:

### Compilation might become viable when

- Trainset of quality-signal prompts grows past 50 (currently 30).
- A specific quality regression appears that demos could target.
- We switch to a weaker runtime model (e.g. Haiku) where demos help more.

### Other improvements worth considering

- **Fix the 20 prompt files with `unparseable filename` errors.** These have
  `__pycache__`-confused parents or BOM characters. Cleanup PR would grow the
  trainset further and improve the retriever's fallback coverage.
- **`tasks.task_category` column in Supabase.** Today `task_category` is an
  in-memory enum. Promoting it to a real column would enable
  persona-routed eval critics (per `prompt-generator-optimized.md` §10.1)
  and category-aware retrieval at any scale.
- **Cross-combo embedding retrieval.** `retriever.py` is filename-based.
  An embedding index over prompt sources could find better references at
  levels 4-5 of the fallback ladder. Worth doing only if bootstrap mode
  triggers frequently.
- **Empirical eval gate.** Post-generation, spin up an E2B sandbox and try
  running the task. This is `prompt-generator-optimized.md` §10.2. It
  catches generation-level bugs that `evals.py` LLM-judging misses.

---

## Appendix — what gets passed to the LLM (the actual system prompt)

The `GeneratePromptSignature`'s docstring becomes the system prompt every
Generate call. Here's a condensed version of what the LLM sees:

```
Your input fields are:
1. `competencies` (str): Comma-separated competency names with proficiency …
2. `proficiency` (str): Target proficiency level (BASIC/BEGINNER/INTERMEDIATE)
3. `task_category` (str): Infrastructure category (e.g. script_and_db…)
4. `competency_scopes` (str): AUTHORITATIVE scope text …
5. `reference_prompts` (str): Source of 2-5 existing prompt files. Use as
   structural template only — DO NOT copy content; adapt to the target.
6. `similar_tasks` (str): Summaries of successful tasks …
7. `detailed_skill_signal` (str): Bundled calibration signal …
8. `feedback_from_previous_attempt` (str): Verifier feedback from prior
   iteration. When non-empty, every issue mentioned MUST be addressed.

Your output fields are:
1. `reasoning` (str): (auto-added by ChainOfThought)
2. `new_prompt_file` (str): Complete Python file source with PROMPT_REGISTRY
   definition. Output ONLY the Python source — no markdown fences.

All interactions will be structured in the following way, with the
appropriate values filled in:

[[ ## competencies ## ]]
{competencies}

[[ ## proficiency ## ]]
{proficiency}

... (all 8 input fields) ...

[[ ## reasoning ## ]]
{reasoning}

[[ ## new_prompt_file ## ]]
{new_prompt_file}

[[ ## completed ## ]]

In adhering to this structure, your objective is:

    Generate a complete Python file containing PROMPT_REGISTRY entry for a
    new (competencies, proficiency) combination.

    HARD CONSTRAINT — competency_scopes is the source of truth:
    The `competency_scopes` field describes EXACTLY what each competency
    covers at this proficiency level. The generated prompt MUST:
      - Only ask the candidate to use concepts that appear (or could be
        naturally derived from) the scope text.
      - Never require concepts the scope says are out of scope.
      - When the scope says "limited understanding of X" or "not yet
        expected to do Y", the generated task must NOT require X or Y as
        primary skills.

    HARD CONSTRAINT — output structure:
    The output MUST be a valid Python module that:
      - Defines three triple-quoted strings: CONTEXT, INPUT_AND_ASK,
        INSTRUCTIONS. Use names like PROMPT_<TECH>_<LEVEL>_*.
      - Contains placeholders {organization_background}, {role_context},
        {competencies}, {real_world_task_scenarios}, {minutes_range}.
      - Defines PROMPT_REGISTRY = { "<key>": [CONTEXT, INPUT_AND_ASK,
        INSTRUCTIONS] } where <key> is exactly: 'Name1 (LEVEL), Name2
        (LEVEL)' (alphabetically sorted with proficiency in parentheses).

    HARD CONSTRAINT — infrastructure category:
    The `task_category` field determines the file structure. Match exactly:
      - PURE_CODE: no Docker, just source + requirements.txt or package.json
      - DB_ONLY: Docker + PostgreSQL + init_database.sql, NO app code
      - SCRIPT_AND_DB: Docker + DB + a script (no web framework)
      - APP_AND_DB: Docker + DB + web framework (FastAPI/Flask/Express/…)
      - FRONTEND: package.json, no Docker, browser-side only
      - LLM_FRAMEWORK: Python + Langchain/Llamaindex
      - VECTOR_DB: Python + vector store (Milvus/Chroma/Pinecone)
      - MESSAGING: backend + Kafka/queue
      - MICROSERVICES: multi-service Docker setup
      - NON_CODE: data files only (CSV/JSON)

    HARD CONSTRAINT — proficiency level boundaries:
      - BEGINNER (0-1 yrs, 20-30 min): single concept, syntax fixes
      - BASIC (1-2 yrs, 30-45 min): 2-3 concepts combined
      - INTERMEDIATE (3-5 yrs, 45-60 min): 4-5 concepts, optimization

    REFERENCE PROMPTS: Use for structural template only.
    SIMILAR TASKS: Use to calibrate complexity, file count, question style.
```

The `VerifyPromptSignature` docstring is similar but with the 4 hard-fail
conditions and pass criteria.

---

## Appendix — Anatomy of a single demo entry

If a compiled artifact existed (it doesn't right now), one demo would look like
this in JSON:

```json
{
  "generate.predict": {
    "demos": [
      {
        "competencies": "Java (BASIC)",
        "proficiency": "BASIC",
        "task_category": "pure_code",
        "competency_scopes": "[Java (BASIC)] An individual at BASIC level …",
        "reference_prompts": "# ===== Reference: Java_intermediate_prompt.py … (~60K chars)",
        "similar_tasks": "Title: Implement a basic Java CLI …",
        "detailed_skill_signal": "=== SUB-SKILL CHECKLIST ===\n- …",
        "feedback_from_previous_attempt": "",
        "reasoning": "<LLM's reasoning trace from compile-time>",
        "new_prompt_file": "<14,649 chars: the entire Java BASIC gold file>"
      }
    ]
  }
}
```

3 demos × ~85 KB each = ~250 KB total JSON. At runtime, all 3 get
prepended to every Generate LLM call, adding ~250K chars to every prompt.
That's the cost. The (unrealized) hope is that the LLM's output quality
improves enough to be worth it. Our 4 experiments showed it doesn't.
