# Agent tasks ship a fake LLM — root cause & fix

**Date:** 2026-06-19 · **Owner:** task-generation pipeline · **Status:** fixing

## TL;DR

All 8 Intermediate agent tasks (Multi-Agent Systems, Production Agent Engineering,
Tool Use for Agents, Context Engineering) **never call a real LLM** — each replaces
the model with a deterministic stand-in (`FakeLLM`, a regex `llm_stub`, a "fixed
local planner"), and two literally simulate agent work with `time.sleep()`. So they
test backend plumbing dressed up as agents, not agent/LLM engineering.

This is **not** a wrong-file-picked bug. The generator selects the correct dedicated
prompt for each agent competency. The defect is in (a) the **prompt content**, which
is saturated with "LLM-free / deterministic / stub / no-API-key" instructions, and
(b) the **prompt-generation pipeline**, which seeds agent prompts from non-agent
backend prompts and has no trustworthy generic agent baseline to fall back to.

## What we fixed (summary)

Status: all changes on `feat/e2b-task-runthrough`, **uncommitted** — user reviews.
Verifier stays OFF by design; the **validator** is the guard. **60 tests green.**

| # | What | File(s) |
|---|------|---------|
| 1 | **Agent template §0 — "REAL LLM/AGENT LOOP MANDATORY"**: task must call a real model (litellm / anthropic / openai SDK); stubs ARE the agent logic; FORBID FakeLLM / regex intent / `time.sleep`-as-agent; "LLM-free / no key" scoped to the readiness GATE only | `task_generation_prompts/Intermediate/production_agent_engineering_intermediate_prompt/…py` |
| 2 | **Generator instruction — `HARD CONSTRAINT #8 — AGENT REALNESS`**: directly steers the DSPy generator to mandate a real LLM/agent loop and forbid the fakes | `generators/prompts/agent.py` |
| 3 | **Validator guard — agent-realness check** (negation-aware): FAILS agent prompts that mandate a fake LLM or lack a real-LLM mandate. This is the gate since the verifier is off | `generators/prompts/validator.py` |
| 4 | **Reference selection — LEVEL-0 agent pin**: agent competencies get a clean agent baseline as TOP reference instead of token-overlap routing to backend prompts / the generic Level-6 skeleton | `generators/prompts/retriever.py` |
| 5 | **NEW generic agent reference** (competency-neutral, reference-only — no `PROMPT_REGISTRY`, never loads into the task registry): the "generic agent prompt" agents lacked; pinned for all 4 agent competencies, level-aware | `task_generation_prompts/_general_reference/agent_general_intermediate_prompt.py` |
| 6 | **Fixed a pre-existing stale test** (`test_zero_reference_combo_hits_level_6`): used PHP+Laravel which now has prompts → switched to a synthetic reference-less combo | `tests/test_general_reference.py` |
| — | **Tests added** | `tests/test_agent_realness_validator.py` (9), `tests/test_generic_agent_reference.py` (7) |

**Live-proven:** regenerating Production Agent Engineering now yields a CLEAN real-LLM
prompt (realness guard `[]`). **Not fixed yet:** the 8 already-generated tasks still
ship fake LLMs — they need regeneration (commands at the bottom).

## The feedback (Naman, 2026-06-16)

> "How did we handle LLM calls here? I don't see any LLM calls in any of them — how
> are these agents if they don't do any LLM calls? You're trying to simulate agents
> by adding sleeps… all 8 of the tasks suffer from this problem."

Confirmed. Correct on both counts.

## What we verified (cloned all 8 starter repos)

A grep for any real LLM client (`openai`/`anthropic`/`portkey`/`google.genai`/
`chat.completions`/`messages.create`) across all 8 repos returned **zero hits**.
Reading the code:

| task | competency | stand-in for the LLM | severity |
|---|---|---|---|
| dispatch-quote-cache-correctness | Multi-Agent | `EtaAgent/CapacityAgent/WeatherAgent` = `await asyncio.sleep(0.01)` + dict lookup | **worst — sleep theater** |
| dispatch-quote-resilience | Multi-Agent | scripted fake tools (`time.sleep(delay)` = latency) | weak agent surface |
| bind-recruiting-reschedule-confirmation | Prod Agent Eng | `llm_stub.py` — regex `re.fullmatch(r"(yes\|confirm…)")` | weak |
| patient-triage-context-packer | Prod Agent Eng | `class FakeLLM` sink | most defensible (real skill = context builder) |
| travel-agent-seat-idempotency-fix | Tool Use | "planner is a fixed local function (no live LLM)" | weak |
| recruiting-copilot-invite-confirmation-gate | Tool Use | `agent_policy.py` "deterministic stand-in for the LLM" | weak |
| cargolink-pickup-context-repair | Context Eng | none (RAG/retrieval), no model | medium |
| fare-rules-context-cache | Context Eng | none (cache), no model | medium |

Common defect across all 8: **no real LLM/agent loop.** Sleep-as-agent specifically:
dispatch-quote-cache-correctness (and, more excusably, dispatch-quote-resilience).

## Root cause 1 — the prompt content

Selection is correct: each of the 4 agent competencies resolves to its own dedicated
~27K-char prompt in `infra/utils.py:_PROMPT_REGISTRY`. But all 4 keys are registered by
**one committed file** —
`task_generation_prompts/Intermediate/production_agent_engineering_intermediate_prompt/
production_agent_engineering_intermediate_prompt.py` — and its content is saturated
with faking instructions: `stub` ×24, `deterministic` ×2, `api key` ×5, `fixture` ×11.
Verbatim:

- *"a task that violates 'never call a stub' or **'LLM-free at the gate'**"*
- *"It runs at the deploy gate with **NO API key**."*
- *"**1. NEVER CALL A STUBBED FUNCTION.** Readiness IMPORTS the candidate-stub modules… Does NOT call the stubs or run the loop."*
- *"if os.getenv('ANTHROPIC_API_KEY'): # absent at the gate -> **skipped (free, deterministic)**"*

The intent was narrow — keep the **generation-time readiness gate** key-free/cheap.
But the framing is repeated so heavily it bled into the **whole task**: the generator
over-generalized "the gate must be LLM-free" into "the task must be LLM-free" and
replaced the real model with a stub.

## Root cause 2 — the generation pipeline (`generators/prompts/`)

Agent prompts are **generated at runtime** by a DSPy "PROMPT GENERATOR" (the
`03_prompt` pipeline stage), not hand-written. The run logs in `.task_agent_runs/`
show this is broken in several ways:

- **References are mostly non-agent backend prompts.** Every agent run pulled
  `PostgreSQL`, `Python_Fastapi`, `nodejs_mongodb`, `fastapi_docker`, `go_redis` as
  references. Only 1–2 of 5 were agent-related. So the generator learns the backend
  "deterministic / no-key / fixtures / stubs" pattern and applies it to agents.
- **`Verifier passed: False`** in nearly every run. (Verifier is intentionally OFF
  as a hard gate — the **validator** is the guard — but the validator does not catch
  the fake-LLM/stub/sleep anti-pattern, so bad prompts pass.)
- **Circular degradation.** By the June 15 runs (right before the 8 tasks were made),
  it fell back to `Fallback level: 2` using the agent template itself as the main
  reference → the flawed seed reinforces itself.
- **`Similar DB tasks: 0`** — no agent corpus to learn from (cold start), and there is
  **no hand-curated generic agent baseline** to anchor quality.
- **Uncompiled generator** — "No compiled file at prompt_generator/compiled/
  agent_bootstrap.json — running uncompiled."
- **One template → 4 competencies** — Multi-Agent / Tool Use / Context Engineering are
  not meaningfully differentiated and all inherit the same framing.

`summary.json` confirms the pipeline shipped anyway: `03_prompt` `exit_code: 0`,
`"task_outcome": "TASK CREATED"`, despite the prompt being unverified.

## Root cause 3 (meta) — the wrong grading assumption

Why does the template insist on an "LLM-free, deterministic, no-key gate"? Because it
assumed grading **runs the task** and must avoid cost/non-determinism. We verified this
week that **production grading runs nothing** — Gemini judges the candidate's git diff
+ screen recording against the competency rubric (see `prod-grader-llm-judge` memory).
So the determinism constraint that drove the mocking **was never needed.** The same
wrong assumption produced (a) these stubbed tasks, (b) the test-based run-through gates,
(c) the mocked-LLM task design. One root cause, three symptoms.

## Why there is no generic agent prompt (vs non-agent tasks)

- **Non-agent tasks** use hand-curated static per-technology prompts
  (`python_intermediate.py`, `java_intermediate_prompt.py`, …) — stable, reviewed,
  reused. Those *are* the generic prompts.
- **Agent tasks** were built on a generator instead of a curated baseline, on the
  theory that agent competencies are new/varied. But with bad references, no agent
  corpus, and a non-blocking verifier, there is nothing good to fall back to. The lone
  committed agent file is just a fallback seed — and it carries the flawed framing.
- **So the absence of a generic agent baseline is itself a root cause.**

## Fixes (this change)

1. **Generic agent baseline prompt** — a hand-curated, reviewed agent reference that
   MANDATES a real LLM/agent loop and FORBIDS fake-LLM / regex stand-in /
   `time.sleep()`-as-agent. Used as the top reference for all 4 agent competencies.
2. **Reference selection** — for agent competencies, prioritize the agent baseline (+
   real agent references) over backend prompts.
3. **Validator anti-pattern checks** — fail/feed-back when a generated agent prompt
   would yield: no real LLM call, FakeLLM/regex stand-in as the whole task, or
   `time.sleep()`-as-agent. (Validator is the guard since the verifier is off.)
4. **Template edit** — strip the "LLM-free TASK / NotImplementedError-stub-as-fake-LLM
   / no-key / deterministic-replaces-LLM" framing; KEEP the legit "key-free GATE" and
   fixtures-for-input-determinism.

> Exact files/lines are filled in the "Implementation" section below after the
> generator mapping completes.

## How to re-run after the fix

```bash
# regenerate the agent prompt for one competency (writes data/generated/agent_prompts/…)
python -m generators.prompts --competency "Production Agent Engineering" --proficiency INTERMEDIATE --env dev
# or the full pipeline (input_files → scenarios → prompt → tasks)
python run_pipeline.py ...
```

## Implementation (done 2026-06-19 — uncommitted, user reviews)

Note: the DSPy **verifier is intentionally OFF** (`PROMPT_VERIFIER_ENABLED`); the
deterministic **validator** is the guard. Fixes target the validator + the
generator signature + the baseline, not the verifier.

1. **Corrected agent baseline** — `task_generation_prompts/Intermediate/
   production_agent_engineering_intermediate_prompt/...py` (registers all 4 agent
   keys; it IS the de-facto agent baseline). Added `## 0. REAL LLM / AGENT LOOP —
   MANDATORY` right after the GOAL: the task MUST call a real model
   (litellm / anthropic / openai SDK on the candidate's key); the
   `NotImplementedError` stubs ARE the agent logic; FORBID `FakeLLM` / regex
   intent parser / `time.sleep()`-as-agent; "LLM-free / no key" is scoped to the
   readiness GATE only. (Prohibitions phrased with adjacent negations so the
   new validator doesn't self-trip.)

2. **Reference selection** — `generators/prompts/retriever.py`. Added
   `AGENT_COMPETENCIES` + `AGENT_BASELINE` + a **LEVEL 0** pin in
   `retrieve_references`: agent competencies always get the curated agent baseline
   as the TOP reference (verified for all 4), instead of token-overlap routing to
   backend prompts / the generic Level-6 reference.

3. **Validator guard** — `generators/prompts/validator.py`. Added
   `_agent_realness_issues` (called from `validate_prompt_file`, scoped via
   `_is_agent_combo`): FAILS when an agent prompt mandates a fake LLM
   (`FakeLLM` / regex stand-in / `time.sleep` simulation — negation-aware via
   `_unnegated_fake_hits`, so "NEVER a FakeLLM" is fine) OR lacks a real-LLM
   mandate. Verifier is off, so this is the gate.

4. **Generator signature** — `generators/prompts/agent.py`. Added
   `HARD CONSTRAINT #8 — AGENT REALNESS` to `GeneratePromptSignature` so the DSPy
   generator is directly instructed to mandate a real LLM/agent loop and forbid
   the fake patterns for agent competencies.

5. **Generic agent reference** — `task_generation_prompts/_general_reference/
   agent_general_intermediate_prompt.py` (NEW). A competency-neutral, reference-only
   agent baseline (defines NO `PROMPT_REGISTRY`, never loads into the task registry)
   derived from the corrected baseline. `retriever._agent_baseline_path(proficiency)`
   now pins THIS as the TOP reference for every agent competency (level-aware, falls
   back to INTERMEDIATE). This is the "generic agent prompt" the non-agent tasks have
   but agents lacked — and it gives even a self-excluded competency (e.g. regenerating
   Production Agent Engineering, whose own curated file is excluded as gold) a clean,
   non-excluded agent reference to learn from.

**Live proof (2026-06-19):** regenerated Production Agent Engineering via
`python -m generators.prompts` → output is CLEAN (`_agent_realness_issues == []`,
mandates a real model / litellm, no unnegated fake mandate). It regenerated in
bootstrap mode (own file excluded) yet still came out real — HARD CONSTRAINT #8
carried it; the generic reference now removes the bootstrap gap for next time.

Tests: `tests/test_agent_realness_validator.py` (9) + `tests/test_generic_agent_reference.py`
(7, incl. all 4 competencies pin the generic). Touched-area suite green
(`test_canonical_keys`, `test_validator_brace_escape`, `test_general_reference`,
`test_prompt_registry`, new file = 52 passed). One PRE-EXISTING failure
(`test_general_reference::test_zero_reference_combo_hits_level_6`) is unrelated —
it fails without these changes too (php_laravel prompt files now exist, so the
PHP+Laravel combo no longer falls to the Level-6 general reference).

## How to re-run after the fix

```bash
# regenerate ONE agent prompt (writes data/generated/agent_prompts/…)
python -m generators.prompts --name "Production Agent Engineering" --proficiency INTERMEDIATE --env dev
# the generated prompt now: pins the corrected baseline as reference, is steered
# by HARD CONSTRAINT #8, and is gated by the validator's agent-realness check.
# Then regenerate the task itself (full pipeline):
python run_pipeline.py --name "Production Agent Engineering" --proficiency INTERMEDIATE ...
```

Validate a generated prompt is real-agent (quick check):

```python
from generators.prompts.validator import _agent_realness_issues
print(_agent_realness_issues(open("data/generated/agent_prompts/.../<slug>.py").read()))  # [] == clean
```

## Residual / follow-ups

- The validator catches **explicit** fake mandates; it can't fully detect a prompt
  that omits a real-LLM loop while still mentioning "real model" in prose. The
  template rewrite + HARD CONSTRAINT #8 are the primary drivers; the validator is
  the net.
- The 8 already-generated tasks still ship fake LLMs — they need regeneration (or
  manual fix) after re-running the pipeline.
- The generic agent reference covers INTERMEDIATE (where all current agent
  competencies live). Add `agent_general_{basic,advanced}_prompt.py` if/when agent
  competencies appear at those levels (`_agent_baseline_path` already picks them up).
- Consider seeding a `similar_tasks` corpus from the regenerated tasks so agent
  generation stops being cold-start (`Similar DB tasks: 0`).
