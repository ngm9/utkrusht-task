# Autonomous Task Generator Agent — design

> Status: Design only. Nothing in this doc is shipped yet.
> Companion docs: [agent.md](../prompt-generator/agent.md), [task-eval-optimizer.md](../eval-system/task-eval-optimizer.md).
> The verifier gates proposed here lean on the persona-routed critics + sandbox gate in the eval-optimizer doc.

## TL;DR

`multiagent.py` is **2054 lines, ~30 functions, 4+ concerns** in one file. The name is also wrong — there are no agents in it, just a procedural orchestrator that calls one LLM and writes to four side-effect systems (Supabase / GitHub / Gist / DigitalOcean).

This doc proposes two consecutive phases:

| Phase | Goal | Risk |
|---|---|---|
| **Phase 1 — Break up the monolith** | Rename `multiagent.py` and split it into a focused `task_generator/` package. Pure mechanical refactor — same logic, smaller files. | Low |
| **Phase 2 — Wrap in an autonomous orchestrator** | Build `autonomous_task_agent/` that calls all four existing agents (input files, scenarios, prompt, task) via a Coordinator, with a Verifier gating each stage. | Medium |

After Phase 2 the user types `python -m autonomous_task_agent --name "Python, SQL" --proficiency BASIC --count 6` and gets 6 fully-validated tasks in Supabase + GitHub, with sub-agents dispatched only where their outputs are missing.

---

## Why `multiagent.py` needs to change

### Current state

| Concern | Lines | Functions |
|---|---|---|
| Task creation (LLM + retry loop + evals) | ~220 | `create_task`, `run_evaluations`, `validate_task`, `determine_task_type` |
| Task storage (Supabase write, GitHub repo create, Gist) | ~150 | `upload_files_to_github`, embedded in `create_task` |
| Droplet deployment (SSH, paramiko, port checks) | ~600 | `deploy_task_impl`, `reset_task_impl`, `deploy_task_by_id`, `deploy_existing_task` |
| Task lookup / status | ~300 | `find_task_by_competencies`, `update_task_deployment_status`, `update_task_undeploy_status` |
| Answer-code generation (separate LLM flow) | ~200 | `generate_answer_code_and_steps`, `create_answer_github_repo`, `upload_answer_files_to_repo` |
| CLI plumbing | ~150 | 3 `@click.command` definitions, env validation, init |

These don't share state. They share imports and they share `multiagent.py` as a filename. That's the only thing holding them together.

### Concrete pain

- **Surface area is unreviewable.** A PR touching one function rebases against 50 unrelated functions. Reviewers can't form an accurate mental model of "what changed."
- **Tests are impossible.** No existing test isolates `validate_task` from `upload_files_to_github`. Both live in the same module so mocking has to monkey-patch imports.
- **The name lies.** Newcomers grep "multiagent" looking for an agent framework; there isn't one. The file is named after an aspiration, not the implementation.
- **Reuse is blocked.** `pr_review_flow/` and `design_review_flow/` re-implement task-storage logic instead of importing it, because importing from `multiagent.py` drags in droplet code and 1500 unrelated lines.

---

## Phase 1 — Module breakdown

### Proposed name

The user's suggestion: `task_generator.py`. Worth refining because there's already a `task_generation_prompts/` directory and a future `task_eval_optimizer` module. Three candidates:

| Name | Pros | Cons |
|---|---|---|
| `task_generator/` | Matches the user's intent; clear | Slight naming clash with `task_generation_prompts/` |
| `task_creator/` | No clash | Less common verb in this codebase |
| `task_orchestrator/` | Best fit for what the file actually does | Conflates with Phase 2's autonomous orchestrator |

**Recommendation:** `task_generator/` for Phase 1 (the refactor of `multiagent.py`), reserving `autonomous_task_agent/` for Phase 2's wrapper. The package vs the prompt-templates directory is unambiguous at the import site (`from task_generator.create import ...` vs `task_generation_prompts/Basic/python_basic_prompt.py`).

### Module layout

```
task_generator/
├── __init__.py          # public API: create_task, deploy_task, reset_task
├── __main__.py          # Click CLI — replaces multiagent.py's @click commands
├── create.py            # ~220 LOC — create_task, run_evaluations, validate_task
├── storage.py           # ~150 LOC — Supabase write, GitHub repo create, Gist
├── deployment.py        # ~600 LOC — droplet SSH, deploy_task_impl, reset_task_impl
├── lookup.py            # ~300 LOC — find_task_by_competencies, status updates
├── answer.py            # ~200 LOC — generate_answer_code_and_steps + uploads
├── droplet_select.py    # ~100 LOC — IP selection, parse_competency_input
└── env.py               # ~30 LOC  — init_supabase, validate_environment
```

Total ~1700 LOC across 8 focused files, vs 2054 in one. The 350-LOC reduction comes from removing the dead code, duplicated helpers, and orphaned constants `multiagent.py` accumulated over time.

`multiagent.py` becomes a 5-line shim for backward compatibility:

```python
# multiagent.py — DEPRECATED, use task_generator instead.
from task_generator.__main__ import cli

if __name__ == "__main__":
    cli()
```

Shim lives for one release cycle so any external script calling `python multiagent.py ...` keeps working. Removed in the next.

### Refactor rules

- **No behaviour changes.** Same env vars, same CLI flags, same Supabase rows, same GitHub repos.
- **No new dependencies.** All imports stay; just move them.
- **Function signatures preserved.** Anywhere this is imported externally (only by `pr_review_flow/`, `design_review_flow/`, `non_tech_flow/` from what I see), the import path changes but the call signature does not.
- **One PR.** Mechanical, reviewable per-file, atomic.

### Validation

`task_generator/` passes the existing CLI smoke tests:

```bash
python -m task_generator generate-tasks -c <comp.json> -b <bg.json> -s <scenarios.json>
python -m task_generator deploy-task --task-id <UUID> --droplet-ip <IP>
python -m task_generator reset-task --task-id <UUID> --droplet-ip <IP> --script-path /root/task/kill.sh
```

Should produce byte-identical Supabase rows and GitHub repos compared to the same inputs against `multiagent.py` on `main`.

---

## Phase 2 — Autonomous task agent

Once the monolith is broken up, the building blocks for a real multi-agent system are in place:

| Sub-agent | Owned by | Already exists? |
|---|---|---|
| Input file generator | `generate_input_files/` | ✅ Yes |
| Scenario generator | `scenario_generator/` | ✅ Yes |
| Prompt template generator | `prompt_generator/` | ✅ Yes |
| Task creator (LLM + evals) | `task_generator/` (after Phase 1) | ✅ Yes (post-Phase 1) |
| Task deployer | `task_generator/deployment.py` (after Phase 1) | ✅ Yes (post-Phase 1) |

Today a user runs four separate CLI commands in sequence. The autonomous agent runs them itself, decides which to skip (because outputs already exist), gates each stage with a verifier, and produces the final task batch.

### Architecture

```
                ┌──────────────────────────────────────────────┐
                │            CLI / API entry point             │
                │  python -m autonomous_task_agent             │
                │   --name "Python, SQL"                       │
                │   --proficiency BASIC                        │
                │   --count 6                                  │
                └──────────────────────────────────────────────┘
                                    │
                                    ▼
                ┌──────────────────────────────────────────────┐
                │              COORDINATOR AGENT               │
                │  • Reads disk + Supabase to detect what      │
                │    inputs/scenarios/prompt already exist     │
                │  • Plans which sub-agents to dispatch        │
                │  • Sequences calls; handles retries          │
                │  • Emits structured run logs                 │
                └──────────────────────────────────────────────┘
                  │           │           │           │
        ┌─────────┘  ┌────────┘  ┌────────┘  ┌────────┘
        ▼            ▼           ▼           ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐
  │ Input   │  │Scenario │  │ Prompt  │  │   Task      │
  │ Files   │→ │  Gen    │→ │  Gen    │→ │  Creator    │
  │  Agent  │  │  Agent  │  │  Agent  │  │   Agent     │
  └─────────┘  └─────────┘  └─────────┘  └─────────────┘
       │            │            │             │
       ▼            ▼            ▼             ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐
  │ Input   │  │Scenario │  │ Prompt  │  │   Task      │
  │Verifier │  │Verifier │  │Verifier │  │  Verifier   │
  └─────────┘  └─────────┘  └─────────┘  └─────────────┘
       │            │            │             │
       └────────────┴────────────┴─────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │   Final run summary  │
                  │  to stdout + log     │
                  └──────────────────────┘
```

### Coordinator Agent

Lives in `autonomous_task_agent/coordinator.py`. Not an LLM — a deterministic planner.

#### Responsibilities

1. **State detection.** Before dispatching any sub-agent, read what's already on disk and in Supabase:
   - Does `task_input_files/input_<slug>/<level>/background_*.json` exist?
   - Does `task_input_files/task_scenarios/task_scenarios.json` have an entry for this combo?
   - Does `task_generation_prompts/<Level>/<slug>/<slug>.py` or `agent_generated_prompts/<Level>/<slug>/<slug>.py` exist?
   - How many tasks already exist in Supabase for this combo + level?

2. **Plan construction.** From state, build the minimal dispatch plan:
   ```
   [need_input_files] → input_files_agent
   [need_scenarios]   → scenario_agent
   [need_prompt]      → prompt_agent
   [need_tasks]       → task_creator_agent × N (where N = requested - existing)
   ```

3. **Stage sequencing.** Pre-task stages run sequentially because each depends on the previous. The task-creator stage can fan out — generate N tasks in parallel.

4. **Verifier gating.** After each sub-agent completes, run its verifier. If the verifier fails, retry the sub-agent up to a configurable cap (default 2). If still failing, halt the run and emit a structured failure report.

5. **Observability.** Every dispatch + verdict + retry is logged with a run ID. End-of-run summary lists which stages ran, which were skipped (cached), which retried, which failed.

#### Skeleton

```python
# autonomous_task_agent/coordinator.py — sketch

from dataclasses import dataclass

@dataclass
class StageResult:
    name: str
    skipped: bool
    passed: bool
    retries: int
    artifacts: list[Path]
    error: str | None = None


class Coordinator:
    def __init__(self, agents: AgentRegistry, verifiers: VerifierRegistry,
                 max_retries: int = 2):
        self.agents = agents
        self.verifiers = verifiers
        self.max_retries = max_retries

    def run(self, request: TaskRequest) -> RunResult:
        state = self._detect_state(request)
        plan = self._build_plan(request, state)
        results: list[StageResult] = []
        for stage in plan:
            result = self._execute_stage(stage, state)
            results.append(result)
            if not result.passed:
                return RunResult(results, status="FAILED", error=result.error)
            state = self._update_state(state, result)
        return RunResult(results, status="OK")
```

### Verifier Agents

One per sub-agent. Each runs after its agent and decides pass / fail / retry.

| Verifier | Checks |
|---|---|
| **Input files** | `questions_prompt` has ≥10 bullets, `role_context` is 3+ sentences with stated YoE, no placeholder text remains (`<TODO>`, `TBD`) |
| **Scenario** | Each scenario contains "Current Situation", "Your Task", "Success Criteria"; scenarios are textually distinct (cosine sim < 0.85 pairwise); count matches request |
| **Prompt** | Passes `prompt_generator/validator.py` (already exists — AST parse, `PROMPT_REGISTRY` key, required format vars); the registry key matches `'Name1 (LEVEL), Name2 (LEVEL)'` alphabetical convention |
| **Task** | `evals.py` `llm_task_eval` + `llm_code_eval` both pass — and (Phase 3) the persona-routed critic from [task-eval-optimizer.md §1](../eval-system/task-eval-optimizer.md). Optionally the sandbox-exec gate from §2. |
| **Deployment** *(optional stage)* | Ports listening, `kill.sh` cleans up — same as the eval-optimizer's sandbox gate |

#### Verifier interface

```python
# autonomous_task_agent/verifier.py

from typing import Protocol, runtime_checkable

@runtime_checkable
class Verifier(Protocol):
    name: str
    def verify(self, artifacts: list[Path], context: dict) -> VerificationResult:
        """Inspect artifacts; return pass/fail + diagnostic detail."""
        ...

@dataclass
class VerificationResult:
    passed: bool
    diagnostics: list[str]  # human-readable issues
    retry_hint: str | None  # if non-None, included in next sub-agent invocation
```

The `retry_hint` is what makes verifiers useful: when a task fails because the code provides too much of the answer, the hint *"Code at line 42 fully implements the function the candidate is supposed to write — remove and replace with TODO"* is passed back into the next task-creation attempt as a feedback signal. Same loop pattern the prompt generator already uses internally.

### Sub-agent adapters

Each existing package (`generate_input_files/`, `scenario_generator/`, `prompt_generator/`, `task_generator/`) gets a thin adapter that the Coordinator calls. Adapters do one thing: hide CLI parsing, expose a Python function.

```python
# autonomous_task_agent/agents/prompt_agent.py — sketch

from prompt_generator.agent import PromptGeneratorAgent
from prompt_generator.classifier import Competency

class PromptAgent:
    name = "prompt_generator"

    def run(self, request: TaskRequest) -> AgentResult:
        agent = PromptGeneratorAgent(max_iterations=5)
        comps = [Competency(n, request.proficiency) for n in request.competency_names]
        result = agent(competencies=comps, proficiency=request.proficiency, env=request.env)
        output_path = self._write(result)
        return AgentResult(artifacts=[output_path], metadata=result.input_files_metadata)
```

No new agent logic — the LLM work already happens inside the existing packages. The adapter is plumbing.

### Module layout

```
autonomous_task_agent/
├── __init__.py
├── __main__.py            # CLI: python -m autonomous_task_agent
├── coordinator.py         # the Coordinator class
├── state.py               # disk + Supabase state detector
├── plan.py                # plan-construction logic
├── agents/
│   ├── __init__.py
│   ├── base.py            # AgentResult, AgentProtocol
│   ├── input_files.py     # wraps generate_input_files/
│   ├── scenario.py        # wraps scenario_generator/
│   ├── prompt.py          # wraps prompt_generator/
│   ├── task_creator.py    # wraps task_generator/create.py
│   └── deployment.py      # wraps task_generator/deployment.py (optional)
└── verifiers/
    ├── __init__.py
    ├── base.py            # VerificationResult, Verifier protocol
    ├── input_files.py
    ├── scenario.py
    ├── prompt.py
    ├── task.py
    └── deployment.py
```

Total expected size: ~1500 LOC. Most of it is plumbing — the heavy lifting stays in the existing agent packages.

---

## How this composes with existing work

### With the prompt generator

The Prompt Agent adapter is a direct wrapper around `PromptGeneratorAgent`. Output land at:

```
task_generation_prompts/agent_generated_prompts/<Level>/<slug>/<slug>.py
```

(Same path the standalone `prompt_generator` CLI writes to today — see [agent.md](../prompt-generator/agent.md).)

The Coordinator checks whether either the agent-generated path *or* the curated path (`task_generation_prompts/<Level>/<slug>/<slug>.py`) already exists. If either does, the prompt stage is skipped. Curated prompts always take precedence.

### With the eval optimizer

The Task Verifier is exactly where the persona-routed critics ([task-eval-optimizer.md §1](../eval-system/task-eval-optimizer.md)) plug in. The Coordinator's "retry with feedback" loop is exactly where the verifier's `retry_hint` flows back into the Task Creator Agent as `feedback_from_previous_attempt` — the same pattern the prompt generator already uses.

The Deployment Verifier is where the sandbox-exec gate ([§2](../eval-system/task-eval-optimizer.md#section-2-empirical-sandbox-exec-gate)) lives.

In other words: implementing the eval optimizer first gives you better verifiers for free when the autonomous agent ships.

### With `pipeline/`

The existing `pipeline/` package already chains `generate_input_files` + `scenario_generator`. It can either be:

- **Subsumed by `autonomous_task_agent`** — the pipeline becomes a special case of the autonomous agent run with `--up-to scenarios`.
- **Kept as a fast-path** — for users who only want input files + scenarios and don't want to invoke the full agent loop.

Recommendation: keep `pipeline/` as a fast-path. It's a 2-step composition; the autonomous agent is a 5-step composition. Different ergonomics.

---

## Sequencing

```
┌───────────────────────────────────────────────────────┐
│ Phase 1 — Module breakdown                            │
│ • Rename multiagent.py → task_generator/              │
│ • Split 2054 LOC into 8 focused files                 │
│ • Add shim for back-compat                            │
│ • Zero behaviour change                               │
└───────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│ Phase 1.5 — Eval optimizer (separate doc)             │
│ • Persona-routed critics in evals.py                  │
│ • Optional: tasks.task_category Supabase column       │
│ Provides the verifier brain for Phase 2.              │
└───────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│ Phase 2 — Autonomous task agent                       │
│ • autonomous_task_agent/ package                      │
│ • Coordinator + 5 sub-agent adapters + 5 verifiers    │
│ • CLI replaces 4 manual commands with 1               │
│ • Per-stage retry with feedback hints                 │
└───────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│ Phase 3 — Production hardening (optional)             │
│ • Empirical sandbox-exec verifier (from eval doc §2)  │
│ • Multi-judge ensemble for high-stakes generations    │
│ • Run replay / DAG visualisation for debugging        │
└───────────────────────────────────────────────────────┘
```

Phase 1 is unblocked today and worth doing on its own merits regardless of Phase 2. Phase 1.5 (eval optimizer) is independently valuable. Phase 2 multiplies the value of both.

---

## Concrete user-facing change

### Before

```bash
# Today — 4 commands, manually sequenced
python -m generate_input_files --name "Python, SQL" --proficiency BASIC
python -m scenario_generator --competency-file task_input_files/.../comp.json --count 6 --append
python -m prompt_generator --name "Python, SQL" --proficiency BASIC
python multiagent.py generate-tasks -c <comp.json> -b <bg.json> -s <scenarios.json>
```

### After

```bash
# Tomorrow — 1 command, all stages dispatched as needed
python -m autonomous_task_agent --name "Python, SQL" --proficiency BASIC --count 6
```

Internally: detects what's missing, calls the sub-agents, gates each stage with a verifier, retries on feedback, writes the final tasks to Supabase + GitHub. Final stdout summary:

```
=== AUTONOMOUS TASK AGENT — RUN COMPLETE ===
Competencies:    Python, SQL (BASIC)
Tasks requested: 6
Tasks produced:  6 (4 first try, 1 retry, 1 retry)
Stages:
  ✓ input_files     skipped (already exists)
  ✓ scenarios       generated (6 new) — verifier passed
  ✓ prompt          generated — verifier passed (1 retry)
  ✓ task_creator    6/6 verified
  - deployment      skipped (--deploy not set)
Total time:      4m 12s
Run ID:          atg-20260114-103317
```

---

## Open questions

- **Concurrency model.** Sub-agents are mostly I/O bound (LLM calls). Should the Coordinator use threads, asyncio, or just sequential? Lean sequential for v1 — debuggability > throughput. Parallel task creation (the fan-out at the final stage) is worth adding once the sequential path is stable.
- **Where do verifier `retry_hint`s live?** Today the prompt generator's `VerifyPromptSignature` uses an LLM critic that produces verdict + reasoning. Should each verifier be an LLM critic (variable cost, contextual feedback) or a deterministic checker (cheap, brittle, less actionable feedback)? Recommend a mix: deterministic for structural checks (parse, registry key), LLM for semantic checks (realism, complexity).
- **State storage.** The Coordinator's `state` is rebuilt every run from disk + Supabase. Should it be cached between runs (e.g. SQLite at `.autonomous_task_agent/state.db`)? Probably not — disk + Supabase IS the source of truth, and a stale cache is worse than a re-read.
- **Naming for the wrapper.** `autonomous_task_agent` is descriptive but long at the CLI. Alternatives: `taskforge`, `taskbench`, `ata`. Lean to keep `autonomous_task_agent` for clarity, alias to `ata` for keystrokes.
- **What happens to non-tech flows?** `pr_review_flow/`, `design_review_flow/`, `non_tech_flow/` have their own pipelines. Out of scope for the first version. Once the pattern is proven, each can adopt the Coordinator + Verifier model.

---

## Risks

- **Phase 1 regression risk.** A mechanical refactor of 2054 lines will hit edge cases. Mitigate by keeping `multiagent.py` as a shim for one release cycle and running the full smoke-test command set against both old and new before merging.
- **Phase 2 over-design risk.** The Coordinator + Verifier abstraction could grow into a framework. Resist that. Each Verifier and Adapter should be < 100 LOC. If they grow, the abstraction is wrong, not the requirements.
- **Schema migration risk on the eval optimizer prerequisite.** If we tie Phase 2 to Phase 1.5's Supabase column, a delay there blocks the autonomous agent. Mitigate by making the persona routing work without the column (classify at eval time from competency names) and treating the column as a follow-up enabling analytics, not as a hard dep.

---

## References

- `multiagent.py` — current monolith (2054 LOC)
- [agent.md](../prompt-generator/agent.md) — the prompt-template sub-agent
- [task-eval-optimizer.md](../eval-system/task-eval-optimizer.md) — verifier brains for the task stage
- `generate_input_files/`, `scenario_generator/`, `pipeline/` — existing upstream agents
- `pr_review_flow/`, `design_review_flow/`, `non_tech_flow/` — sibling flows that could later adopt the same pattern
- Anthropic, *Building effective agents* — orchestrator-worker + evaluator-optimizer patterns this design borrows from
