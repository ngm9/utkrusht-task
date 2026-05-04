# Prompt Generator Agent — Design Doc

> Status: Design — not yet implemented
> Author: Claude + Rohan
> Date: 2026-04-20

## Problem

We currently have ~60 hand-written prompt files in `task_generation_prompts/` (Basic / Beginner / Intermediate). Each new tech stack or proficiency level requires writing a new ~200-300 line `.py` file by hand.

This is unsustainable as we add more competencies. From the recent task list, we have ~25 new tasks to create across ~15 distinct prompt files (Microservices, Javascript, Java Spring MVC, Langchain, Llamaindex, Vector Databases, RAGs, MongoDB indexing, PostgreSQL schema/indexing/large-scale, Kafka, etc.).

We need a way to **automatically generate** new prompt files that are consistent with the existing ones, without losing the domain judgment those hand-written files encode.

---

## Why templating won't work

A naive approach would be a templating engine with conditionals:

```python
if "SQL" in techs or "PostgreSQL" in techs:
    add_docker_section()
    add_init_sql_file()
    if has_web_framework(techs):
        add_app_dockerfile()
        add_api_layer()
    else:
        add_python_script()
if proficiency == "INTERMEDIATE":
    add_caching_section()
    add_indexing_section()
```

This breaks for every new tech (Redis? Vector DBs? RAG? Each needs new branches). It also can't capture the subtle judgment in the existing prompts — e.g., "BEGINNER Python tasks should focus on a single concept, not multi-step refactors."

---

## Design: Generator → Verifier → Refiner Agent

The right pattern is a multi-agent loop where one LLM **generates** a candidate prompt, a senior **verifier** checks it against the knowledge base, and they iterate until quality is met (Reflexion / Self-Refine pattern).

```
┌──────────────────────────────────────────────────┐
│ KNOWLEDGE BASE                                   │
│  - 60+ existing prompt files (.py)               │
│  - Supabase tasks table (task_blob, eval_info)   │
│  - task_competencies, criterias mappings         │
└──────────────────────────────────────────────────┘
                    ↓
        ┌─────────────────────┐
        │  RETRIEVER          │
        │  Picks 3-5 most     │
        │  relevant refs      │
        └─────────────────────┘
                    ↓
        ┌─────────────────────┐
        │  GENERATOR          │
        │  Synthesizes new    │
        │  prompt file        │
        └─────────────────────┘
                    ↓
        ┌─────────────────────────────────────┐
        │  SENIOR VERIFIER                    │
        │  Checks against:                    │
        │  - Structural patterns              │
        │  - Similar prompts in same category │
        │  - Successful tasks from dev DB     │
        │  - Proficiency scope adherence      │
        └─────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │   PASSES?     │
            └───────────────┘
              YES ↓     ↑ NO (with feedback)
                  │     │
            Final ┘     └→ back to GENERATOR (max 3 iterations)
```

---

## Knowledge base — what feeds the agent

### 1. Existing prompt files (`task_generation_prompts/`)

These ARE the knowledge base. We don't build a separate index — the prompts themselves encode the patterns. Categorical retrieval (not vector search) is sufficient because:

- Files are small enough (~5-10K tokens) to use as full in-context examples
- They're already organized by Basic/Beginner/Intermediate + tech stack
- Retrieval rules are deterministic ("if SQL in techs, include `SQL_basic_prompt.py`")

### 2. Dev Supabase DB — ground truth signal

This is what makes the generator measurable. The dev DB has:

| Source | What we get |
|---|---|
| `task_competencies` + `tasks` | (competencies, proficiency) → actual generated task |
| `task_blob.resources.github_repo` | Link back to the prompt that generated it |
| `eval_info` | Quality signal — did the LLM eval pass? |
| `is_enabled` | Quality signal — was this task used in production? |
| `review` field | Human signal if reviews exist |

This gives us **labeled training data**:
- **Input**: `(competencies, proficiency, reference prompts)`
- **Output**: a prompt that produced an enabled, eval-passing task
- **Metric**: did the resulting task get enabled? did eval pass?

---

## Component design

### Retriever

Rule-based selection of 2-4 most relevant whole prompt files. No vector search needed.

```python
def retrieve_references(competencies, proficiency):
    refs = []

    # Always include each individual competency's prompt at the same level
    for comp in competencies:
        path = find_prompt(comp, proficiency)
        if path:
            refs.append(path)

    # If both DB + backend in techs, include similar combined examples
    if has_db(competencies) and has_backend(competencies):
        refs.append("Basic/NodeJs_postgres_basic_prompt.py")

    # Always include same-level combined-stack prompts as style references
    refs.extend(find_combined_prompts(level=proficiency, limit=2))

    return refs[:5]  # cap at 5 references
```

### Generator (DSPy ChainOfThought)

Takes competencies + proficiency + reference prompts + similar tasks from DB, outputs a new prompt file as a string.

```python
class GeneratePromptSignature(dspy.Signature):
    """Generate a task generation prompt from references."""
    competencies = dspy.InputField()
    proficiency = dspy.InputField()
    reference_prompts = dspy.InputField()
    similar_tasks = dspy.InputField(
        desc="Existing successful tasks in Supabase with same/similar competencies"
    )
    new_prompt = dspy.OutputField(
        desc="Complete .py file content with PROMPT_REGISTRY"
    )
```

### Senior Verifier

The crucial second agent. Acts as a senior engineer reviewing junior work. Reads:
- The newly generated prompt
- 2-3 reference prompts from the same category
- Recent successful tasks from Supabase that match similar competencies (their `eval_info`, `criterias`, `task_blob`)

Outputs `passes: bool` + `feedback: str`. If it fails, the feedback feeds back into the generator.

### What the verifier checks

Beyond structural validation, the verifier exercises **judgment**:

1. **Structure**: Does it have CONTEXT, INPUT_AND_ASK, INSTRUCTIONS sections?
2. **Registry**: Is the `PROMPT_REGISTRY` key formatted correctly? (e.g., `"Python (BASIC), SQL (BASIC)"`)
3. **Format strings**: Are `{organization_background}`, `{role_context}`, `{competencies}`, `{real_world_task_scenarios}`, `{minutes_range}` all present?
4. **Category fit**: For Python+SQL, is there a Docker section? Are there NO web framework references? (because we determined this is a script+DB task)
5. **Proficiency fit**: For BASIC, are advanced concepts (async, connection pooling) excluded? For INTERMEDIATE, does it require those?
6. **Output JSON structure**: Does it specify all required fields (`name`, `question`, `code_files`, `outcomes`, `short_overview`, `pre_requisites`, `answer`, `hints`, `definitions`)?
7. **README structure**: Are the right sections in the right order? (Database Access placement differs by category)
8. **Comparable to similar successful prompts**: Does it match the patterns of similar combinations that produced eval-passing, enabled tasks in the DB?

```python
class VerifyPromptSignature(dspy.Signature):
    """Senior reviewer verifies the prompt meets standards."""
    new_prompt = dspy.InputField()
    reference_prompts = dspy.InputField()
    similar_tasks = dspy.InputField()
    passes = dspy.OutputField(desc="boolean — does this meet quality bar?")
    feedback = dspy.OutputField(desc="specific issues to fix if not passing")
```

### Refiner loop

Up to 3 iterations of generate → verify. If it still fails after 3 attempts, fall back to manual review.

```python
class PromptGeneratorAgent(dspy.Module):
    def __init__(self):
        self.generate = dspy.ChainOfThought(GeneratePromptSignature)
        self.verify = dspy.ChainOfThought(VerifyPromptSignature)

    def forward(self, competencies, proficiency):
        refs = retrieve_references(competencies, proficiency)
        similar = fetch_similar_tasks_from_supabase(competencies, proficiency)

        feedback = ""
        for attempt in range(3):
            result = self.generate(
                competencies=competencies,
                proficiency=proficiency,
                reference_prompts=refs,
                similar_tasks=similar,
                # include feedback from previous iteration
            )
            verdict = self.verify(
                new_prompt=result.new_prompt,
                reference_prompts=refs,
                similar_tasks=similar,
            )
            if verdict.passes:
                return result
            feedback = verdict.feedback
        return result  # return last attempt with feedback noted
```

---

## Cold-start: when the DB has nothing for this competency

For a brand-new competency like `"Llamaindex (BASIC)"` with no existing tasks in the DB, the pipeline degrades gracefully through a fallback ladder. The system never truly fails — it just shifts from "we have direct evidence this works" to "we're synthesizing from similar patterns."

### Fallback hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ LEVEL 1 (Best): Same competency, same proficiency       │
│   DB tasks for "Python + Llamaindex (BASIC)" exist?     │
│   Static prompt python_llamaindex_basic_prompt.py?      │
└─────────────────────────────────────────────────────────┘
                ↓ (if nothing found)
┌─────────────────────────────────────────────────────────┐
│ LEVEL 2: Same competency, ADJACENT proficiency          │
│   "Python + Llamaindex (INTERMEDIATE)" tasks?           │
│   (Drop down complexity in the prompt)                  │
└─────────────────────────────────────────────────────────┘
                ↓ (if nothing found)
┌─────────────────────────────────────────────────────────┐
│ LEVEL 3: Similar tech family, same proficiency          │
│   Llamaindex ≈ Langchain (both Python RAG frameworks)   │
│   Vector DB ≈ Llamaindex (adjacent ecosystem)           │
└─────────────────────────────────────────────────────────┘
                ↓ (if nothing found)
┌─────────────────────────────────────────────────────────┐
│ LEVEL 4: Individual competency at any level             │
│   "Python (BASIC)" prompt + tasks → backbone language   │
└─────────────────────────────────────────────────────────┘
                ↓ (if nothing found)
┌─────────────────────────────────────────────────────────┐
│ LEVEL 5: Generic same-proficiency prompts               │
│   Any "(BASIC)" prompts → compose from competency scope │
└─────────────────────────────────────────────────────────┘
                ↓
        Generate using competency.scope from Supabase
        + general structural patterns
        (verifier in "bootstrap mode")
```

### Concrete example: bootstrapping `Python + Llamaindex (BASIC)`

```python
# Level 1: Exact match — none found
db.query("Python + Llamaindex (BASIC)") → []

# Level 2: Adjacent proficiency — none found
db.query("Python + Llamaindex (INTERMEDIATE)") → []

# Level 3: Tech family — Langchain found!
db.query("Python + Langchain (BASIC)") → [task_x, task_y]
fs.find("python_langchain_basic_prompt.py") → exists

# Level 4: Backbone — Python BASIC found
db.query("Python (BASIC)") → [task_z, ...]
fs.find("python_basic_prompt.py") → exists
```

The agent tells the LLM:

> "No exact references exist for `Python + Llamaindex (BASIC)`. Closest references:
>
> 1. **`python_langchain_basic_prompt.py`** — same proficiency, similar tech family. Use as primary structural template.
> 2. **`python_basic_prompt.py`** — for Python proficiency scope and complexity.
> 3. **Llamaindex competency scope** from Supabase: '*Llamaindex BASIC users should understand document loaders, basic indexing, simple query engines...*'
>
> Synthesize a new prompt that inherits structure from #1, replaces Langchain-specific parts with Llamaindex equivalents (per scope #3), and keeps Python BASIC complexity (per #2)."

### Verifier in bootstrap mode

When no exact-match tasks exist in the DB, the verifier shifts criteria:

| Verifier check | Normal mode | Bootstrap mode |
|---|---|---|
| Match successful task patterns in DB | Required | **Skipped** (no data) |
| Structural validity (format strings, registry key) | Required | Required |
| Proficiency scope adherence | Required | Required |
| Match similar tech family patterns | Optional | **Required** (heavier weight) |
| Pull from `competency.scope` field | Optional | **Required** (primary truth) |

The verifier essentially says: "I can't compare to real generated tasks, so I'll be stricter about structural patterns and the competency scope."

### The competency `scope` field becomes critical

In bootstrap mode, the `scope` field from the `competencies` table is the primary source of truth:

```json
{
  "competency_id": "...",
  "name": "Llamaindex",
  "proficiency": "BASIC",
  "scope": "A BASIC Llamaindex user understands document loaders, simple indexing strategies, basic query engines, integration with vector stores like Chroma or FAISS, and can build a simple RAG pipeline. They are not expected to handle advanced retrieval strategies, custom node parsers, or production-scale optimizations."
}
```

The verifier checks the generated prompt against this scope to ensure it tests the right concepts.

### Bootstrap improves over time (cold-start → warm-start)

```
Day 1:  Generate prompt for "Python + Llamaindex (BASIC)"
        → uses Langchain as fallback reference
        → produces first task

Day 2:  First task gets reviewed, eval_info.passed = true, is_enabled = true
        → DB now has 1 example for this exact combo

Day 7:  Generate another prompt variant or refresh existing one
        → DB now has real reference data
        → Verifier can compare against actual successful task

Day 30: Multiple tasks exist for the combo
        → DSPy can be re-compiled with these as training examples
        → System gets sharper for this specific stack
```

Manual review of the very **first** task is more important — it sets the pattern that future generations learn from.

### CLI surfacing

```bash
$ python -m prompt_generator --name "Python, Llamaindex" --proficiency BASIC

Searching DB for similar tasks...
- Exact match (Python + Llamaindex BASIC): 0 tasks
- Adjacent (Python + Llamaindex INTERMEDIATE): 0 tasks
- Tech family (Python + Langchain BASIC): 3 tasks ✓
- Backbone (Python BASIC): 12 tasks ✓

Searching prompt files...
- Exact: not found
- Tech family (python_langchain_basic_prompt.py): found ✓
- Backbone (python_basic_prompt.py): found ✓

Mode: BOOTSTRAP (no exact references — using fallbacks)
Running generator (attempt 1/3)...
Running verifier...
Verifier passed.
Written: task_generation_prompts/Basic/python_llamaindex_basic_prompt.py
Note: First-time generation. Manual review recommended.
```

### Precondition: competency must exist in Supabase

If the competency record doesn't exist in `competencies` table at all, the pipeline can't start because `generate_input_files` would fail. The team must:

1. Add the competency row to Supabase first (with `name`, `proficiency`, `scope`, `organization_id`)
2. Then run the pipeline

For the upcoming new competencies (`PostgreSQL - Schema Management`, `MongoDB - Indexing and Aggregation`, etc.), this DB seeding is a manual prerequisite.

---

## Where DSPy fits in the pipeline

DSPy isn't the whole system — it's specifically wrapping the **LLM-powered steps**. Here's the pipeline annotated with what's DSPy and what's plain Python:

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Retrieve references                          PYTHON  │
│   - Query Supabase for similar tasks                         │
│   - Glob filesystem for prompt files                         │
│   - Apply fallback ladder (cold-start handling)              │
│   → outputs: list of reference paths + DB task examples      │
│   ✗ NOT DSPy — pure Python data fetching                     │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Generate candidate prompt                    DSPy    │
│   dspy.ChainOfThought(GeneratePromptSignature)               │
│   - Input: competencies, proficiency, refs, similar_tasks    │
│   - Output: new_prompt (string)                              │
│   ✓ DSPy — auto-tunes meta-prompt + few-shot examples        │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Verify candidate                             DSPy    │
│   dspy.ChainOfThought(VerifyPromptSignature)                 │
│   - Input: new_prompt, refs, similar_tasks                   │
│   - Output: passes (bool), feedback (str)                    │
│   ✓ DSPy — auto-tunes verification reasoning                 │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Orchestrate generate ↔ verify loop           DSPy    │
│   dspy.Module forward() with up to 3 iterations              │
│   - Pass verifier feedback back into generator               │
│   ✓ DSPy — module composition; entire flow is compilable     │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Validate output is parseable Python          PYTHON  │
│   - ast.parse(generated_prompt)                              │
│   - Check PROMPT_REGISTRY key exists                         │
│   - Verify {format_variables} all present                    │
│   ✗ NOT DSPy — deterministic checks                          │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Write file to disk                           PYTHON  │
│   - task_generation_prompts/{Level}/{name}_prompt.py         │
│   ✗ NOT DSPy — pure I/O                                      │
└──────────────────────────────────────────────────────────────┘
```

### What DSPy specifically helps with

DSPy's value at steps 2-4 is that it **auto-tunes the meta-prompts** instead of us hand-engineering them.

| Without DSPy (raw LLM call) | With DSPy |
|---|---|
| We hand-write the instruction: *"You are a senior engineer. Generate a prompt that..."* | We declare a signature: `competencies, proficiency → new_prompt` |
| We hand-pick which examples go in context (e.g., always 3 prompts) | DSPy learns which examples produce the best output (`BootstrapFewShot`) |
| If quality drops, we manually iterate on the wording | DSPy compiler (MIPROv2) searches over instruction variants |
| Adding a new model = re-tune by hand | `dspy.settings.configure(lm=new_model)` and re-compile |
| Verifier criteria are hard-coded text | DSPy can learn what verification checks correlate with task quality |

### The compilation step (one-time, ahead of usage)

```python
import dspy

# Configure LLM
dspy.settings.configure(lm=dspy.LM("claude-sonnet-4-6"))

# Pull training data: existing prompts + the tasks they produced
trainset = build_trainset_from_db_and_files()
# trainset[i] = Example(competencies, proficiency, expected_prompt)

# Define metric: how good is a generated prompt?
def metric(example, prediction, trace=None):
    score = 0
    if parses_as_python(prediction.new_prompt):           score += 0.2
    if has_correct_registry_key(prediction.new_prompt):    score += 0.2
    if has_all_format_vars(prediction.new_prompt):         score += 0.2
    if test_task = generate_test_task(prediction.new_prompt):
        if test_task.eval_info.passed:                     score += 0.4
    return score

# Compile (this is the expensive step — runs once)
optimizer = dspy.MIPROv2(metric=metric)
compiled_agent = optimizer.compile(
    PromptGeneratorAgent(),
    trainset=trainset,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
)

# Save the compiled program (it's a JSON of optimized prompts + selected examples)
compiled_agent.save("prompt_generator/compiled.json")
```

### Runtime usage (cheap, fast)

```python
# Load the pre-compiled program
agent = PromptGeneratorAgent()
agent.load("prompt_generator/compiled.json")

# Use it — no re-compilation needed
result = agent(
    competencies=["Python", "Llamaindex"],
    proficiency="BASIC",
)

write_file(
    "task_generation_prompts/Basic/python_llamaindex_basic_prompt.py",
    result.new_prompt
)
```

### When to re-compile

- **Initially** — when first building the system
- **When new prompt files are added manually** — adds new training examples
- **When LLM model changes** — Claude 4.6 → 4.7 may need different prompts
- **Periodically** — every few months as the DB grows with more eval-passed tasks

### What DSPy is NOT doing

To be clear:
- ✗ Not the retriever (steps 1, 5, 6 are plain Python)
- ✗ Not training a model — it tunes prompts and example selection only
- ✗ Not vector search — retrieval is rule-based
- ✗ Not the CLI — that's plain Python around the DSPy module
- ✗ Not the Supabase fetching — also plain Python

DSPy is specifically the wrapper around the LLM-calling parts (steps 2, 3, 4) that makes those calls **optimizable** instead of hand-engineered.

---

## Why DSPy fits

I initially dismissed DSPy as overkill. After reconsidering, it's a strong fit because:

### We have a real metric

```python
def prompt_quality_metric(generated_prompt, expected_outputs):
    score = 0
    # 1. Does it parse as valid Python?
    if not parses_as_python(generated_prompt): return 0
    # 2. Does PROMPT_REGISTRY key match expected format?
    if not has_correct_registry_key(generated_prompt): return 0
    # 3. When run through task generation, does the output:
    #    - Pass eval_info checks?
    #    - Have all required code_files?
    #    - Match expected criterias structure?
    task = generate_test_task_with_prompt(generated_prompt)
    if task.eval_info.passed: score += 0.4
    if task.has_required_files: score += 0.3
    # 4. Does the verifier approve it?
    if verifier_passes: score += 0.3
    return score
```

### We have training data — in the dev DB

```python
def build_trainset_from_db():
    """Build (input, output) pairs from successful tasks in Supabase."""

    tasks = supabase.table("tasks") \
        .select("task_id, criterias, task_blob, eval_info, is_enabled") \
        .eq("is_enabled", True) \
        .execute()

    examples = []
    for task in tasks.data:
        if not task["eval_info"] or not task["eval_info"].get("passed"):
            continue

        # Identify the prompt file used
        competencies = [c["name"] for c in task["criterias"]]
        proficiency = task["criterias"][0]["proficiency"]
        prompt_file = lookup_prompt_file(competencies, proficiency)

        if not prompt_file:
            continue

        examples.append(dspy.Example(
            competencies=competencies,
            proficiency=proficiency,
            new_prompt=read_file(prompt_file),  # the "good" answer
        ).with_inputs("competencies", "proficiency"))

    return examples
```

### What DSPy gives us beyond a hand-rolled loop

| Feature | Hand-rolled | DSPy |
|---|---|---|
| Generator + verifier loop | Yes (we'd code it) | Yes (`dspy.Module`) |
| Auto-tune prompts to LLM | No — we hand-write them | Yes — MIPROv2 / BootstrapFewShot optimizes |
| Auto-select best examples per case | No — fixed retrieval | Yes — DSPy can learn which references work best |
| Cost tracking + caching | We'd build it | Built-in |
| Swap models easily | Manual | `dspy.settings.configure(lm=...)` |
| Reproducible compilation | Maybe | Yes — saves compiled program |

The killer feature is **auto-tuning the meta-prompts**. We don't need to manually engineer the perfect "Now generate the prompt..." instruction — DSPy searches over variants based on what produces high-quality outputs.

### Compilation flow

```python
import dspy

# Configure LLM (Claude or GPT)
dspy.settings.configure(lm=dspy.LM("claude-sonnet-4-6"))

# Build training set from dev DB
trainset = build_trainset_from_db()

# Compile the agent
optimizer = dspy.MIPROv2(metric=prompt_quality_metric)
compiled_agent = optimizer.compile(PromptGeneratorAgent(), trainset=trainset)

# Use it
result = compiled_agent(
    competencies=["Python", "Vector Databases"],
    proficiency="INTERMEDIATE"
)
write_file("task_generation_prompts/Intermediate/python_vector_databases_intermediate_prompt.py", result.new_prompt)
```

---

## What we are NOT doing

### Not RAG with vector search

You might think this is "just RAG for prompts." It's similar but simpler:

| | RAG | Our approach |
|---|---|---|
| Retrieval | Vector search over chunks | Rule-based file selection |
| Storage | Vector DB | Source code in repo |
| Granularity | Chunks | Whole prompt files |

We don't need vector search because:
1. Our "documents" (prompt files) are categorized (Basic/Intermediate/by tech)
2. The retrieval rules are deterministic
3. We can include the **whole file** as context (~5-10K tokens each)

### Not training a custom model

DSPy compilation tunes prompts and example selection — it doesn't fine-tune model weights. The base LLM stays the same; the meta-prompts and few-shot examples get optimized.

---

## Implementation plan

### Phase 1: Foundation (1-2 days)

- [ ] Pull training data from dev DB (script)
- [ ] Build prompt-to-task mapping (which prompt produced which tasks)
- [ ] Implement `retrieve_references()` rule-based logic
- [ ] Implement `lookup_prompt_file()` to map (competencies, proficiency) → existing prompt file path
- [ ] Implement `fetch_similar_tasks_from_supabase()` for verifier context

### Phase 2: DSPy module (2-3 days)

- [ ] Set up DSPy with Portkey/Claude
- [ ] Build `GeneratePromptSignature` and `VerifyPromptSignature`
- [ ] Implement `PromptGeneratorAgent` module with iteration loop
- [ ] Build the `prompt_quality_metric` function
- [ ] Test on existing prompt that we know works (sanity check)

### Phase 3: Compilation (1-2 days)

- [ ] Build training set from existing prompts + DB
- [ ] Run MIPROv2 optimizer
- [ ] Save compiled program
- [ ] Validation: hold out 5-10 existing prompts, see if compiled agent reproduces them well

### Phase 4: Integration (1 day)

- [ ] CLI: `python -m prompt_generator --name "Python, Vector Databases" --proficiency INTERMEDIATE`
- [ ] Wire into `pipeline/__main__.py` so the unified pipeline runs:
  1. `generate_input_files`
  2. `prompt_generator` (NEW)
  3. `scenario_generator`
  4. `multiagent generate_tasks`

### Phase 5: Test on real targets (1 day)

Generate prompts for the upcoming task list:
- Python + Langchain (BASIC, INTERMEDIATE)
- Python + Llamaindex (BASIC, INTERMEDIATE)
- Python + Vector Databases (BASIC, INTERMEDIATE)
- Python + RAGs (INTERMEDIATE)
- Java + Spring MVC (BEGINNER, BASIC, INTERMEDIATE)
- Java + Spring Webservices (BASIC, INTERMEDIATE)
- Node.js + MongoDB indexing (INTERMEDIATE)
- Python + FastAPI + PostgreSQL Schema/Indexing/Large-Scale (BASIC)
- Microservices (BASIC, INTERMEDIATE)
- Kafka (INTERMEDIATE)

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Generated prompts produce low-quality tasks | Verifier loop catches it; falls back to manual review on persistent failures |
| LLM hallucinates incorrect tech assumptions (e.g., suggesting wrong libraries) | Verifier checks against successful tasks in DB; reference prompts ground the output |
| DSPy compilation cost is high | Compile once per LLM model; cache results |
| Edge cases for very novel tech combinations | Always include a "manual override" — generated prompt can be edited before commit |
| Drift over time as new prompts are added | Re-compile periodically; verifier always uses current refs |

---

## Open questions

1. Should the generator only run when no prompt exists for the combo, or should it always re-generate (and we keep the better version)?
2. Where does compilation happen — on each developer's machine, or centrally?
3. What's the fallback if all 3 iterations fail? Manual? Skip and generate task without it?
4. Should we version-control the compiled DSPy program (it's a JSON file)?
5. Do we need a "human in the loop" approval step before the generated prompt is committed?

---

## References

- DSPy: https://dspy.ai/
- Reflexion paper: https://arxiv.org/abs/2303.11366
- Self-Refine paper: https://arxiv.org/abs/2303.17651
- Existing prompts: `task_generation_prompts/` (Basic, Beginner, Intermediate)
- Supabase tasks table schema: see `multiagent.py` (line ~451 onwards)
