# Prompt Generator — A Visual Reference

> [!note]
> The `prompt_generator/` package synthesizes a new task-generation prompt template for any
> `(competencies, proficiency)` combo. It fuses five context sources, runs a Generate ⇄ Verify
> ⇄ Validate loop, and emits a deterministically-checked Python file that `multiagent.py`
> consumes at task-generation time.

The agent is **scope-respecting** (bounded by `competency.scope`), **complexity-calibrated**
(bounded by `role_context` + proficiency), and **category-correct** (bounded by
`task_category`).

---

## Where it sits in the pipeline

The prompt-generator reads from every upstream stage so its output anchors against the same
data the runtime will use.

> [!visual] pipeline-flow

Three upstream caches feed the agent: Supabase competencies, hand-curated input files, and a
library of existing prompts. The agent emits a single `.py` template; `multiagent.py` then
uses that template at task-generation time.

---

## The seven input signals

Each signal exists for a specific reason — losing any one of them measurably degrades output
quality on at least one axis (scope, complexity, structure, or domain).

> [!visual] signals-grid

> [!tip]
> `detailed_skill_signal` degrades gracefully: when input files are absent for a brand-new
> combo, the loader returns empty strings and the agent continues on scopes + references
> alone, without flagging the absence as a constraint.

---

## The agent loop

The runtime intelligence is a `dspy.Module` with two `ChainOfThought` signatures wired in a
feedback loop, with a deterministic validator gating the exit.

> [!visual] agent-loop

> [!note]
> **Why two signatures, not self-correction:** a single model self-critiquing tends to confirm
> its own output. A separate Verify signature with only the four hard-fail conditions becomes
> a real adversary, not an echo chamber.
>
> **Why ChainOfThought:** forcing the LLM to reason through scope, category, proficiency, and
> structural constraints before emitting code measurably improves first-pass correctness.
>
> **Why a deterministic validator after a passing verifier:** LLM verifiers are good at
> semantic judgments and bad at exact-pattern matching. AST parse, registry key shape, and
> format-var presence are regex/AST checks — cheaper and stricter than another LLM call.

---

## Module responsibilities

| File | Role |
|---|---|
| `__main__.py` | CLI entry. Parses args, slugifies output path, configures DSPy, runs the agent, writes the file. |
| `classifier.py` | Pure-Python rule mapping `competencies → TaskCategory`. No I/O, no LLM. |
| `retriever.py` | Filesystem reader; 5-level fallback ladder picks 3-5 reference `.py` files. |
| `db_queries.py` | Supabase reader for `competency.scope` + enabled-and-eval-passed similar tasks. |
| `input_files.py` | Loads `questions_prompt`, `role_context`, and up to 3 scenarios; bundles + truncates into `detailed_skill_signal`. |
| `agent.py` | DSPy module holding both signatures, the loop, LM routing (Portkey/OpenRouter), and demo loading. |
| `validator.py` | Deterministic post-flight: AST parse, registry-key shape, required format vars. |
| `trainset.py` / `metric.py` / `compile.py` | Offline compilation pipeline — BootstrapFewShot / MIPROv2 producing `compiled/agent_bootstrap.json`. |

---

## Hard constraints encoded in the signatures

The Generate signature docstring carries four enforced constraints; the Verify signature
mirrors them as the four hard-fail conditions.

1. **Scope** — `competency_scopes` is the source of truth. The prompt may only require
   concepts that fall inside (or naturally derive from) the scope text.
2. **Structure** — the output must define `PROMPT_REGISTRY`, three triple-quoted
   `*_CONTEXT / *_INPUT_AND_ASK / *_INSTRUCTIONS` strings, and the placeholders
   `{organization_background}`, `{role_context}`, `{competencies}`,
   `{real_world_task_scenarios}`, `{minutes_range}`.
3. **Category** — file layout must match `task_category` exactly. `SCRIPT_AND_DB` with a
   Flask app, or `APP_AND_DB` without a web framework, is an instant reject.
4. **No solution leak** — starter code and comments must not hint at the answer.

The Verify signature is told to be **practical**, not perfectionist — it ships usable
prompts, not perfect ones. Style and minor naming drift are surface-level warnings, not
hard rejects.

---

## CLI surface

```bash
python -m prompt_generator --name "Python, SQL" --proficiency BASIC
python -m prompt_generator --name "Python" --name "Llamaindex" --proficiency BASIC
python -m prompt_generator --name "Python, Vector Databases" --proficiency INTERMEDIATE --dry-run
python -m prompt_generator --name "Java" --proficiency BASIC --force
```

Useful flags: `--env {dev,prod}` (Supabase env), `--dry-run` (preview without writing),
`--force` (overwrite), `--max-iterations` (default 5), `--model`, `--compiled-path`
(few-shot demos JSON).

---

## Compilation — turning vibes into measurement

Runtime is uncompiled by default. The offline compile step bakes few-shot examples into
the agent and gives us an objective quality score.

- **`trainset.py`** — walks `task_generation_prompts/`, joins against Supabase to keep
  only prompts that produced enabled + eval-passing tasks. Quality filter is the key step.
- **`metric.py`** — `[0.0, 1.0]` score: 30% hard structural validity, 30% file-name Jaccard,
  25% header Jaccard, 15% length similarity.
- **`compile.py`** — `BootstrapFewShot` (cheap, fast) or `MIPROv2` (expensive, also
  searches over the instruction text). Output: `compiled/agent_bootstrap.json`, auto-loaded
  by `__main__.py`.

> [!tip]
> Compilation matters because prompt-template generation is the kind of task where examples
> beat instructions. `BootstrapFewShot` picks the best worked examples for you, scored
> against held-out data — improving the agent becomes "add training pairs, recompile,"
> not "tweak the docstring."

---

## Status

| Component | State |
|---|---|
| CLI args (`competencies`, `proficiency`) | shipped |
| `task_category` via `classifier.py` | shipped (in-memory enum) |
| `competency_scopes` via `db_queries.py` | shipped (with `long_scope` fallback) |
| `reference_prompts` via `retriever.py` | shipped (5-level ladder) |
| `similar_tasks` via `db_queries.py` | shipped |
| `detailed_skill_signal` via `input_files.py` | shipped (graceful empty) |
| `feedback_from_previous_attempt` loop | shipped |
| `validator.py` deterministic post-flight | shipped |
| `compile.py` / `metric.py` / `trainset.py` | shipped (BootstrapFewShot live) |
| `tasks.task_category` column in Supabase | future work (in-memory only today) |

> [!risk]
> The remaining risk is downstream, not in this package: `evals.py` still uses one generic
> critic against `gpt-5-nano`. Persona-routed critics keyed off `task_category`, plus an
> empirical sandbox-exec gate via E2B, would catch a class of failures that LLM eval misses
> (e.g. `python` vs `python3`, dependency-version drift, broken `docker-compose`).

---

## References

- DSPy: <https://dspy-docs.vercel.app/>
- Anthropic, *Building effective agents* — evaluator-optimizer pattern (basis for the
  Generate ⇄ Verify loop)
- `task_generation_prompts/Intermediate/python_langchain_intermediate_prompt.py` — canonical
  hand-written prompt the agent should be able to reproduce structurally
- `task_input_files/input_python_langchain/intermediate/.../background_*.json` — canonical
  input shape `input_files.py` consumes
