# Prompt Generator — Architecture & Design

## TL;DR

The `prompt_generator/` package generates a new task-generation prompt template (`task_generation_prompts/<level>/<tech>_<level>_prompt.py`) for any (competencies, proficiency) combo. It feeds the LLM five context sources — competency scopes, reference prompts, similar tasks, hand-curated sub-skill checklists, and existing scenarios — runs a Generate ⇄ Verify DSPy loop, and emits a deterministically-validated prompt file ready for `multiagent.py` to consume.

The agent is scope-respecting (bounded by `competency.scope`), complexity-calibrated (bounded by `role_context` + `proficiency`), and category-correct (bounded by `task_category`).

---

## 1. Where the prompt-generator sits in the pipeline

```
Supabase competencies  ──►  generate_input_files/
                                │  (caches scope, LLM-generates role_context + questions_prompt)
                                ▼
                            task_input_files/<combo>/<level>/{competency,background}_*.json
                                │
                                ▼
                            scenario_generator/
                                │  (LLM-generates real-world scenarios using scope + role + questions_prompt)
                                ▼
                            task_input_files/task_scenarios/task_scenarios*.json

                            ─────  prompt-generator (this doc)  ─────
                            prompt_generator/   ←── reads task_generation_prompts/<level>/*.py
                                │                ←── reads task_input_files/<combo>/<level>/*.json
                                │                ←── reads task_input_files/task_scenarios/*.json
                                │                ←── reads Supabase competencies + tasks
                                ▼
                            task_generation_prompts/<level>/<tech>_<level>_prompt.py
                            ────────────────────────────────────────────

                            multiagent.py
                                │  (combines: prompt template + competency JSON + background JSON + scenarios)
                                ▼
                            LLM (Portkey) → task description + code_files → evals.py → GitHub repo + Supabase tasks
```

The prompt-generator reads from every upstream stage so its output anchors against the same data the runtime task-generation will use.

---

## 2. Inputs the agent consumes

| Source | Where it comes from | Used as |
|---|---|---|
| `competencies` | CLI args | Direct LLM input |
| `proficiency` | CLI args | Direct LLM input |
| `task_category` | `classifier.py` (in-memory enum) | Hard constraint (LLM + verifier) |
| `competency_scopes` | Supabase `competencies.scope` (fallback `long_scope` if null) | Authoritative skill bounds |
| `reference_prompts` | 3-5 `.py` files via `retriever.py` (5-level fallback) | Structural template |
| `similar_tasks` | Supabase `tasks` table (enabled, eval-passed) | Calibration examples |
| `detailed_skill_signal` | `task_input_files/<combo>/<level>/.../background_*.json` + `task_scenarios.json` | Sub-skill checklist + role context + real scenarios |
| `feedback_from_previous_attempt` | Verifier output (loop only) | Self-correction signal |

### Why each signal exists

**`competency.scope`** — authoritative, dense paragraph (~200-400 words) describing what the candidate can do at this level. Source of truth for what the prompt is allowed to require. Falls back to `long_scope` only when `scope` is null (truncated to 800 words to prevent context bloat).

**Why not `long_scope` by default:** It's a 1500-3000 word multi-section curriculum (Core Deliverables, Day-to-Day Tasks, Foundational Concepts, Tools, Boundaries, Evidence of Mastery). Feeding it alongside `reference_prompts` (3-5 full files) and the detailed-skill-signal block pushes context to 35K+ tokens. `questions_prompt` is the action-shaped distillation of the same content.

**`reference_prompts`** — existing prompt files give the LLM a structural template (section ordering, JSON shape, README format). The 5-level fallback ladder ensures we always have *some* reference to anchor against.

**`similar_tasks`** — examples of past tasks for the same/related competencies that passed eval and are enabled in production. Calibrates complexity, file count, and question style.

**`detailed_skill_signal`** — a bundled context block with three parts:

1. **`questions_prompt`** — hand-curated sub-skills checklist (~50-100 bullets) from the input files. Action-shaped: "ensure questions cover X, Y, Z." Directly mappable to prompt requirements. Beats `competency.scope` alone because scope is high-level prose; `questions_prompt` is testable bullets.

2. **`role_context`** — 3-4 sentences describing day-to-day responsibilities and YoE for the target candidate. Calibrates *complexity* (what kind of work this person delivers) beyond the proficiency band's implicit YoE.

3. **Existing scenarios** — 3-5 real `**Current Implementation:** ... **Your Task:** ... **Success Criteria:** ...` blocks for the same `(combo, proficiency)` key. Teaches the LLM the format, complexity range, and business-domain mix to match.

When input files are missing for a brand-new combo, this signal degrades gracefully to empty — the agent continues using scopes + reference prompts + similar tasks alone.

---

## 3. Architecture diagram

```
                                     ┌─ CLI: python -m prompt_generator --name "Python, SQL" --proficiency BASIC ─┐
                                     │                                                                            │
                                     ▼                                                                            │
              ┌──────────────────────────────────────────────────┐                                                │
              │   classifier.py  (pure Python, deterministic)    │                                                │
              │   Python+SQL → SCRIPT_AND_DB                     │                                                │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              ┌──────────────────────────────────────────────────┐                                                │
              │   retriever.py  (5-level fallback ladder)         │   reads task_generation_prompts/<level>/*.py │
              │   → 3-5 reference prompt .py files                │                                              │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              ┌──────────────────────────────────────────────────┐                                                │
              │   db_queries.py  (Supabase reads)                │                                                │
              │   • competency.scope (long_scope fallback)       │                                                │
              │   • similar enabled+eval-passed tasks            │                                                │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              ┌──────────────────────────────────────────────────┐                                                │
              │   input_files.py                                  │   reads task_input_files/<combo>/<level>/...  │
              │   • questions_prompt (sub-skills checklist)       │                                              │
              │   • role_context     (responsibilities + YoE)     │                                              │
              │   • existing scenarios for this combo key         │                                              │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              ┌──────────────────────────────────────────────────┐                                                │
              │   agent.py — DSPy Generate ⇄ Verify loop          │                                              │
              │   ┌─────────────┐    ┌─────────────┐              │                                              │
              │   │  Generate   │───►│   Verify    │  feedback    │                                              │
              │   │ ChainOfTht  │    │ ChainOfTht  │  loop ≤ 5    │                                              │
              │   └─────────────┘    └─────────────┘              │                                              │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              ┌──────────────────────────────────────────────────┐                                                │
              │   validator.py — deterministic AST/regex checks   │                                              │
              │   parses, registry key, format vars present       │                                              │
              └────────────┬─────────────────────────────────────┘                                                │
                           │                                                                                      │
                           ▼                                                                                      │
              write task_generation_prompts/<level>/<combo>_<level>_prompt.py                                     │
                                                                                                                  │
   (offline) compile.py + trainset.py + metric.py  ─►  compiled/agent_bootstrap.json  (loaded by __main__.py) ────┘
```

---

## 4. Module responsibilities

| File | Role |
|---|---|
| `__main__.py` | CLI entry point. Parses args, slugifies output filename, configures DSPy, instantiates the agent, loads compiled demos, writes the file. |
| `classifier.py` | Pure-Python rules function. Maps a competency mix → `TaskCategory` enum. No I/O. No LLM. |
| `retriever.py` | Filesystem reader. 5-level fallback ladder picks 3-5 reference prompt files from `task_generation_prompts/`. |
| `db_queries.py` | Supabase reader. Pulls `competency.scope` and similar enabled+eval-passed tasks. |
| `input_files.py` | Input-file reader. Pulls `questions_prompt`, `role_context`, and matching scenarios from `task_input_files/`. Graceful degradation when files are absent. |
| `agent.py` | DSPy module. Holds `GeneratePromptSignature` + `VerifyPromptSignature`, runs the Generate ⇄ Verify loop, configures Portkey/OpenRouter LM routing, loads compiled few-shot demos. |
| `validator.py` | Deterministic post-flight check. AST-parse, `PROMPT_REGISTRY` exists, registry key matches expected format, required format vars present. |
| `trainset.py` | Builds DSPy training pairs from the existing prompt files filtered against Supabase quality signal (enabled + eval-passed tasks). |
| `metric.py` | Scoring function for compilation. Structural validity gate + Jaccard over headers/files + length similarity. |
| `compile.py` | One-time training step. BootstrapFewShot (cheap) or MIPROv2 (expensive) → `compiled/agent_bootstrap.json`. |
| `compiled/agent_bootstrap.json` | Compiled artifact. Demos auto-loaded by `__main__.py` at runtime. |

---

## 5. Real walkthrough — generating a `Python+SQL BASIC` prompt

End-to-end trace.

### Step 1 — CLI parse

```bash
python -m prompt_generator --name "Python, SQL" --proficiency BASIC --env dev
```

`__main__.py` parses → `competencies = [Competency("Python","BASIC"), Competency("SQL","BASIC")]`, output_path = `task_generation_prompts/Basic/python_sql_basic_prompt.py`.

### Step 2 — Classifier

```python
classify_task_category([Competency("Python","BASIC"), Competency("SQL","BASIC")])
# has_db=True, has_backend=True (Python), has_framework=False, has_web_app_lang=False
# → SCRIPT_AND_DB
```

The string `"script_and_db"` becomes the `task_category` LLM input.

### Step 3 — Retriever (5-level fallback)

```
Level 1: glob Basic/ for "python" AND "sql" in filename → python_sql_basic_prompt.py exists? ✓
         → returns [python_sql_basic_prompt.py]  (exact match found, fallback_level=1)

Level 1 also pulls 1-2 category examples for style:
         → mongodb_python_basic_prompt.py (script_and_db category)

Final: [python_sql_basic_prompt.py, mongodb_python_basic_prompt.py]
```

These are read fully into the `reference_prompts` text block.

### Step 4 — DB queries

```python
fetch_competency_scope(supabase, "Python", "BASIC")
# → "An individual at BASIC level, with 0-2 years of experience, understands Python syntax..."

fetch_competency_scope(supabase, "SQL", "BASIC")
# → "Understands relational schemas, can write CRUD, JOINs, basic indexes..."

fetch_similar_tasks(supabase, ["Python", "SQL"], "BASIC")
# Combination query first (containment match on criterias):
#   → 3 enabled + eval-passed tasks for this exact combo
# Per-competency fallback if combo is sparse:
#   → +2 Python tasks, +2 SQL tasks
# Total 7 tasks. Each summarized as: title + question (truncated 280 chars) + file names
```

### Step 5 — input_files.py

```python
slug = "python_sql"
folder = "task_input_files/input_python_sql/basic/input_python_sql_basic_task/"

bg = json.load(open(folder + "background_forQuestions_utkrusht_python_sql_basic.json"))

questions_prompt = bg["questions_prompt"]
# → "Please ensure the questions you ask cover the key functional, logical, architectural...
#    Python:
#    - Applying core data types and data structures to solve real problems...
#    - Control flow for business logic and workflow handling...
#    [40+ Python bullets]
#    SQL:
#    - Writing SELECT queries with WHERE, ORDER BY, LIMIT...
#    - Designing schemas with appropriate normalization...
#    [30+ SQL bullets]"

role_context = bg["role_context"]
# → "A junior Backend Engineer with 1-2 years of experience is expected to write
#    correct CRUD operations, basic data transformations, and simple SQL queries..."

scenarios = json.load(open("task_input_files/task_scenarios/task_scenarios.json"))
key = "Python (BASIC), SQL (BASIC)"
existing_scenarios = scenarios.get(key, [])[:5]
# → 5 real scenarios with **Current Implementation** / **Your Task** / **Success Criteria**
```

If any of these files are missing (brand-new combo), the loaders return empty strings and the agent proceeds without them.

### Step 6 — Generate (DSPy ChainOfThought)

The signature receives:

```
competencies            = "Python (BASIC), SQL (BASIC)"
proficiency             = "BASIC"
task_category           = "script_and_db"
competency_scopes       = "[Python (BASIC)]\n<scope>\n---\n[SQL (BASIC)]\n<scope>"
reference_prompts       = <full source of python_sql_basic_prompt.py + mongodb_python_basic_prompt.py>
similar_tasks           = "Title: ...\nFiles: ...\nQuestion: ...\n---\n[6 more]"
detailed_skill_signal   = "<questions_prompt sub-skill list>\n\n=== ROLE CONTEXT ===\n<role_context>\n\n=== EXAMPLE SCENARIOS ===\n<scenarios>"
feedback_from_previous_attempt = ""
```

LLM (gpt-5.4 via Portkey) emits the candidate `.py` source. ChainOfThought adds a `rationale` field that forces the LLM to reason through constraints before emitting the file.

### Step 7 — Verify (DSPy ChainOfThought)

The verifier signature receives the candidate + the same context, judges 4 hard-fail conditions:

1. **Scope violation** — does the prompt require skills beyond `competency_scopes`? E.g., asking for window functions when SQL BASIC scope says "basic JOINs only."
2. **Category mismatch** — does the spec match `task_category="script_and_db"`? Should have Docker + Postgres + a Python script. If it has Flask routes → REJECT.
3. **Structural damage** — missing PROMPT_REGISTRY, missing format vars (`{competencies}`, `{role_context}`, `{organization_background}`, `{real_world_task_scenarios}`), wrong registry key format.
4. **Solution leak** — starter code or comments give away the answer.

Outputs `passes: bool` + `feedback: str`.

### Step 8 — Loop (if needed)

If `passes=False`, feedback like:

> "1. Scope violation: prompt requires window functions, but SQL BASIC scope explicitly excludes them. 2. Missing format variable: {role_context} not present in INSTRUCTIONS string."

is fed into Generate's `feedback_from_previous_attempt` field on the next iteration. Up to 5 iterations. Stops on first pass.

### Step 9 — Validator (deterministic)

Even after the LLM verifier passes:

- AST-parse the generated source → must be valid Python
- `PROMPT_REGISTRY = {...}` exists, key matches `Python (BASIC), SQL (BASIC)` (alpha-sorted)
- Required format vars present in template strings
- Three prompt-stage variables (`*_CONTEXT`, `*_INPUT_AND_ASK`, `*_INSTRUCTIONS`) defined (warning, not failure)

Returns `ValidationResult(passed, issues, warnings, registry_key)`.

### Step 10 — Write file

`task_generation_prompts/Basic/python_sql_basic_prompt.py` is written. Done.

---

## 6. The Generate ⇄ Verify loop

The agent is a `dspy.Module` with two `dspy.ChainOfThought` modules wired in a feedback loop.

```python
feedback = ""
for attempt in range(1, max_iterations + 1):     # default 5
    gen_out = self.generate(
        ...,
        feedback_from_previous_attempt=feedback,
    )
    new_prompt = strip_code_fence(gen_out.new_prompt_file)

    verify_out = self.verify(
        new_prompt_file=new_prompt,
        competencies=...,
        task_category=...,
        competency_scopes=...,
        ...
    )

    if verify_out.passes:
        break
    feedback = verify_out.feedback
```

**Why two separate signatures rather than self-correction:** Same model self-critiquing tends to confirm its own output. A separate signature with different instructions (the 4 hard-fail conditions only) becomes a real adversary, not an echo chamber.

**Why ChainOfThought:** The Generate signature has many constraints (scope, category, proficiency, format vars). Forcing the LLM to think out loud about each before emitting code dramatically improves consistency. The Verify signature has 4 conditions to check; CoT lets it reason through each before committing to a boolean.

**Why the loop:** LLMs are good at reactive correction ("the verifier said the registry key was wrong, fix it") and bad at proactive perfection ("get every constraint right on first try"). The loop turns a hard one-shot problem into an easy multi-shot one.

---

## 7. Validator — deterministic safety net

Runs after the LLM verifier passes. Catches structural problems the LLM might miss.

| Check | What it catches |
|---|---|
| `ast.parse(source)` | Unterminated strings, broken syntax, import errors |
| `"PROMPT_REGISTRY" in source` | LLM forgot to define the registry dict (multiagent.py would `KeyError`) |
| Registry key matches `"Name1 (LEVEL), Name2 (LEVEL)"` (alpha-sorted) | Typo means the prompt is unreachable at runtime |
| Required format vars present (`{organization_background}`, `{role_context}`, `{competencies}`, `{real_world_task_scenarios}`) | Missing placeholder = silent value-substitution failure |
| `PROMPT_*_CONTEXT/INPUT_AND_ASK/INSTRUCTIONS` defined (warning) | Naming-convention drift |

LLM verifiers are good at semantic judgments ("does this require out-of-scope skills?") and bad at exact-pattern matching ("is the registry key alphabetically sorted with parenthesized levels?"). The split is intentional: LLM for semantics, regex for structure.

---

## 8. Compilation — turning vibes into measurement

Runtime is uncompiled by default. The compilation step (offline, one-time per training-data refresh) bakes few-shot examples into the agent.

### `trainset.py`

Walks `task_generation_prompts/`, parses each filename into `(competencies, proficiency)`, joins against Supabase to find prompts that have produced **enabled + eval-passing tasks**. Quality filter is the key step — we don't train on prompts that have never produced a working task.

Each pair becomes:
```
INPUT:  competencies="Python (BASIC), SQL (BASIC)", proficiency="BASIC"
OUTPUT: <full source of python_sql_basic_prompt.py>   ← gold answer
```

### `metric.py`

Given `(gold_prompt_source, predicted_prompt_source)` returns `[0.0, 1.0]`:

- Hard structural validity (parses, has `PROMPT_REGISTRY`, has format vars) → 0 if any fail
- Jaccard similarity over markdown headers → "do they have the same sections?"
- Jaccard similarity over code-file names → "do they generate the same starter files?"
- Length similarity → "is the prompt the right size?"

Weighted: 30% structural, 30% files, 25% sections, 15% length.

### `compile.py`

Two optimizer choices:

- **BootstrapFewShot** (cheap, fast): Tries each training example as a few-shot demo, scores with `metric`, keeps the highest-scoring demos.
- **MIPROv2** (expensive, $5-20 per compile): Same idea, but also searches over the instruction text in the signature docstring.

Output: `compiled/agent_bootstrap.json`. Loaded by `__main__.py` and the demos get injected into the LLM prompt as in-context examples.

### Why compilation matters

| Without compile | With compile |
|---|---|
| LLM gets a 200-line instruction and a fresh shot every time | LLM gets the same instruction + 4 worked examples baked into the prompt |
| Performance varies per call | Performance consistent and measurably better on held-out data |
| Improving the agent = manually tweaking the docstring | Improving the agent = adding more training pairs and recompiling |
| No quantitative quality measurement | `metric.py` gives objective score; A/B compile runs |

Prompt template generation is the kind of task where examples beat instructions. BootstrapFewShot picks the best examples for you, scored to maximize quality.

---

## 9. DSPy primer — what it gives us

DSPy treats LLM calls as **functions with typed inputs/outputs**. Three properties matter:

1. **Signatures decouple intent from prompt-string.** Declare *what* fields go in/out and *what* the constraints are; DSPy turns that into the actual prompt at runtime.
2. **`ChainOfThought` and other Modules wrap signatures with reasoning scaffolds.** Same signature, more structured calls.
3. **Compilable.** Given a metric and a training set, optimizers (`BootstrapFewShot`, `MIPROv2`) search for the best in-context examples (and with MIPROv2, the best instruction text).

**What hand-rolled prompts would lose:**
- Manual few-shot example selection (probably picks worse demos than BootstrapFewShot)
- Hand-built verifier-loop retry logic
- Hand-written chain-of-thought scaffolding
- Manual model-routing per call

DSPy makes prompt engineering an optimization problem with a metric, not a vibes-based exercise.

---

## 10. Eval gates downstream (post-task generation)

The prompt-generator produces a *template*; `multiagent.py` uses the template to produce *tasks* (description + code). Those tasks are validated by `evals.py` before being committed to GitHub + Supabase. Recommendations to strengthen that step (enabled by but separate from this package):

### 10.1 Persona-routed critics

`evals.py` today uses one generic prompt against `gpt-5-nano`. Use the `task_category` enum to route to specialized critics:

| `task_category` | Persona |
|---|---|
| `DB_ONLY` | senior DBA (normalization, indexes) |
| `SCRIPT_AND_DB` | senior backend (data flow, error handling) |
| `APP_AND_DB` | senior backend + API design |
| `LLM_FRAMEWORK` | senior MLE (chunking, retrieval eval) |
| `VECTOR_DB` | senior MLE + index sanity |
| `MESSAGING` | senior distributed-systems |
| `MICROSERVICES` | senior distributed-systems + service boundaries |
| `FRONTEND` | senior UX engineer (a11y, semantic HTML) |
| `PURE_CODE` | generic senior backend |
| `NON_CODE` | senior PM/eval engineer |

Wire by adding a `persona_prompt` dict keyed by category; `evals.py` selects which prompt per task.

### 10.2 Empirical sandbox-exec gate

LLM eval is "vibes by judge." Add a sandbox gate using E2B (already wired):

1. Boot a sandbox, copy the generated `code_files`
2. `docker-compose up` (if applicable) or `./run.sh`
3. Confirm processes start, ports listen, `kill.sh` cleans up
4. Reject the task even if LLM eval passed if any of those fail

Catches `python` vs `python3` / `pip install` failure / dependency-version classes of bug that LLM eval misses.

### 10.3 Multi-judge ensemble

Run 3 LLM judges (different temperature, optionally different model); require 2-of-3 to pass. ~3x cost — but cuts both false negatives and false positives substantially. Opt-in for high-stakes generations.

---

## 11. Implementation checklist

In dependency order:

1. `prompt_generator/input_files.py` — three loaders (`load_questions_prompt`, `load_role_context`, `load_scenarios_for_combo`) + slug helper mirrored from `retriever.py` and `__main__.py`
2. Add `detailed_skill_signal` `dspy.InputField` to `GeneratePromptSignature` and `VerifyPromptSignature`
3. Wire the new input into `agent.py:forward()` between scope-fetch and generate-call
4. Update CLI banner in `__main__.py` to surface "input files used: yes/no" + scenarios count
5. Sanity-check on an existing combo (e.g., Python+SQL BASIC) — diff outputs across two compile artifacts
6. Run on a brand-new combo (e.g., Go+PostgreSQL BASIC) where no input files exist — confirm graceful degradation
7. Re-run `compile.py` to refresh `compiled/agent_bootstrap.json` against the new signature shape
8. Update `prompt_generator/__init__.py` docstring with the full signal flow
9. Add a small note to `CLAUDE.md` describing the prompt-generator inputs

Estimated effort: ~120 lines of new code, no schema migrations, no new dependencies. Single PR.

---

## 12. Open questions / future work

- **`tasks.task_category` column** — promote `TaskCategory` from in-memory enum to Postgres column once persona-routed evals land?
- **Compilation budget** — switch `compile.py` from BootstrapFewShot to MIPROv2 once we have ~50 quality training pairs (currently ~30).
- **Cross-combo retrieval** — `retriever.py` is filename-based. A small embedding index over prompt sources could surface better references at level 4-5 of the fallback ladder. Worth doing only if bootstrap mode triggers frequently.
- **Auto-generate input files when missing** — if `input_files.py` finds nothing, optionally trigger `generate_input_files/` on the fly. Couples two stages; defer until clear use case.

---

## 13. References

- DSPy docs: https://dspy-docs.vercel.app/
- BootstrapFewShot / MIPROv2: `dspy.teleprompt`
- Anthropic, *Building effective agents* — evaluator-optimizer pattern (basis for the Generate ⇄ Verify loop)
- `task_generation_prompts/Intermediate/python_langchain_intermediate_prompt.py` — example of a hand-written prompt the agent should be able to reproduce structurally
- `task_input_files/input_python_langchain/intermediate/.../background_*.json` — canonical example of the input shape `input_files.py` consumes
