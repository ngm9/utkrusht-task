# Autonomous Task Generator — v2 Architecture

**Date:** 2026-05-26
**Status:** Design ready to build
**Scope:** v1 — Utkrusht-internal admin panel; multi-tenant-ready schema from day one

---

## TL;DR

Today's pipeline is five subprocesses chained by `run_pipeline.py`. It works but is wasteful — every run starts from scratch, retries happen only inside Stage 4, and the model never sees real verification output during generation.

The v2 architecture replaces this with three layers:

1. **A deterministic Python coordinator** (`apps/orchestrator/`) that detects state, skips work already done, dispatches stages in-process, decides when to fall back across stage boundaries, and escalates to an **LLM supervisor** in the rare cases where deterministic rules can't decide.
2. **Stage adapters with two-layer verifiers** — structural check (deterministic, fail-fast) followed by an LLM semantic verifier (judges realism, scope-fit, competency-coverage). Stage 2 (scenarios) is where the LLM verifier earns the most; Stage 1 + 3 are lighter-touch but still LLM-judged for quality.
3. **A tool-using agent for Stage 4** (`generators/task/agent_creator.py`) that calls `run_tests`, `verify_code`, `check_files` as tools **inside one agent loop** — self-corrects without re-generating the whole task. Persona-routed LLM eval critics run ONCE on the verified output in fresh context.

Cost: ~14 working days to build v1. Outcome: a single command (`python -m apps.orchestrator --name "Python" --proficiency BASIC --count 6`) that produces six verified tasks in Supabase + GitHub, with per-stage caching, in-process dispatch, durable job rows, structured logs, structural-then-semantic verification at every stage, and a self-correcting code generator that boots E2B and reads its own pytest output.

---

## What problem this solves

Concrete pain points the v2 design fixes, in priority order:

| # | Pain | Today | After v2 |
|---|---|---|---|
| 1 | No state detection | Stage 1 re-runs even when `data/generated/input_files/input_python/` already has the files | Coordinator reads disk + Supabase; skips stages whose outputs exist |
| 2 | Subprocess chain (5 processes per run) | ~5–9 min/run, no shared memory, file-based handoff | One process, in-memory handoff between stages, ~2–5 min/run |
| 3 | Retry only within Stage 4 | If the prompt from Stage 3 was bad, we burn 3 Stage 4 attempts then fail | Coordinator can re-run Stage 3 with Stage 4's feedback (bounded retry) |
| 4 | Generator never sees gate output | Gate fires AFTER generation; model regenerates the whole task with a feedback string | Generator calls `run_tests` as a tool; fixes one file based on actual pytest stderr |
| 5 | Stage 2 races on a shared file | Two concurrent runs corrupt `task_scenarios.json` | Scenarios go to Supabase + per-run scratch; never to source tree |
| 6 | Run state is in-memory | Process crash = run gone | `generation_jobs` row in Postgres; worker can resume / watchdog can reap |
| 7 | LLM-checks-LLM at every eval | Correlated blind spots | Tools deliver ground truth (pytest exit code, compile errors); LLM eval runs ONCE at the end |
| 8 | No conversation memory across runs | Run #2 has no idea why Run #1 failed | `conversations` table; job rows link back |

What v2 does **not** do: parse messy customer briefs (intake stays manual), handle six task types (BUILD only at first), run DSPy optimization (needs a rated-task dataset we don't have).

---

## Core principles

Six rules the rest of the doc obeys. If a design choice violates one of these, it's wrong.

1. **The orchestrator is deterministic Python by default, with an LLM supervisor escape hatch.** The Coordinator decides what runs, in what order, with what fallback — using rules tables for the 95% of decisions that are obvious (file exists? counter < N?). For the 5% where rules don't fit (novel failure verdict, ambiguous partial state), it escalates to a single LLM supervisor call. LLM never sits in the default hot path.
2. **Tools in the agent's hands beat verifiers downstream of the agent.** Stage 4's generator gets `run_tests` and `verify_code` as tools it calls *during* generation. The pytest stderr lands in the model's context while it still remembers what it wrote.
3. **Two-layer verification at every stage: structural first, semantic second.** Structural checks (regex / JSON shape / embedding similarity / E2B gate) are deterministic, free, and catch shape errors fast. LLM semantic verifiers run only after structural passes, and judge what regex can't: realism, scope-fit, competency-coverage, didactic value. The two-layer pattern saves money (LLM never sees malformed input) and gives both kinds of actionable feedback.
4. **Skip cached. Don't re-do.** Every stage adapter checks "does this output already exist for this combo?" before firing. The coordinator builds the dispatch plan from the gaps.
5. **Per-run scratch lives in `/tmp/utkrusht-runs/<run_id>/`.** The source tree is code, not data. After any run, `git status` is clean. Generated outputs land in Supabase or per-run /tmp; never in the repo.
6. **Job rows are durable; in-memory state is not.** Every job is a `generation_jobs` row from the moment it's queued. A crashed worker doesn't lose the job — a watchdog returns it to the queue. Logs land in object storage; the row points at them.

---

## Architecture

```
                ┌────────────────────────────────────────────┐
                │       CLI / API entry point                │
                │  python -m apps.orchestrator …             │
                │  POST /api/generate (from task_builder)    │
                └────────────────────┬───────────────────────┘
                                     │ INSERT
                                     ▼
                ┌────────────────────────────────────────────┐
                │   generation_jobs  (Supabase / Postgres)   │
                │   id, org_id, conversation_id, brief,      │
                │   status, stage, log_url, result_task_id   │
                └────────────────────┬───────────────────────┘
                                     │ FOR UPDATE SKIP LOCKED
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │            apps/orchestrator/coordinator.py              │
        │           (deterministic Python — default path)          │
        │                                                          │
        │  • Detect state (disk + Supabase) for the requested combo│
        │  • Build the minimal stage plan                          │
        │  • Dispatch in-process, in /tmp/utkrusht-runs/<run_id>/  │
        │  • Update job row at each stage transition               │
        │  • Decide cross-stage fallback via decision table        │
        │  • Persist final result; emit run summary                │
        │                                                          │
        │  Escape hatch when rules don't fit:                      │
        │  ┌────────────────────────────────────────────────────┐  │
        │  │ LLM SUPERVISOR (rare path — novel failure verdicts,│  │
        │  │ ambiguous partial state, repeated cross-stage fail)│  │
        │  │ Reads job history + verdicts; emits structured     │  │
        │  │ decision: which stage to re-run with what feedback,│  │
        │  │ or escalate to human review.                       │  │
        │  └────────────────────────────────────────────────────┘  │
        └──┬─────────┬──────────┬──────────────────┬───────────────┘
           │         │          │                  │
           ▼         ▼          ▼                  ▼
       ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────────────┐
       │ S1     │ │ S2      │ │ S3       │ │ S4  TASK AGENT        │
       │ input  │ │ scen-   │ │ prompts  │ │ ────────────────────  │
       │ files  │ │ arios   │ │ (DSPy)   │ │ Pydantic AI + Portkey │
       │        │ │         │ │          │ │                       │
       │ struct │ │ struct  │ │ DSPy     │ │ TOOLS in the loop:    │
       │  +     │ │  +dedup │ │ Generate │ │  • run_tests(files)   │
       │ LLM    │ │  +LLM   │ │ /Verify  │ │  • verify_code(...)   │
       │ verify │ │ verify  │ │  +       │ │  • check_files(...)   │
       │(light) │ │(REQ'D)  │ │ LLM     │ │  • run_compose(...)   │
       │        │ │         │ │ semantic │ │                       │
       │        │ │         │ │ verify   │ │ Loop: write → tool →  │
       │        │ │         │ │ (opt)    │ │ read → fix local →    │
       │        │ │         │ │          │ │ tool again → return   │
       └────────┘ └─────────┘ └──────────┘ │ verified TaskOutput   │
                                            └──────────┬────────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────┐
                                            │ Eval Agent           │
                                            │ (fresh, isolated ctx)│
                                            │ Runs ONCE on the     │
                                            │ tool-verified output.│
                                            │ Persona-routed       │
                                            │ critics from         │
                                            │ infra/evals.py       │
                                            └──────────┬───────────┘
                                                          │
                                                          ▼
                                            ┌─────────────────────────┐
                                            │  Persistence            │
                                            │  • tasks row (Supabase) │
                                            │  • GitHub template repo │
                                            │  • Answer repo + gist   │
                                            │  • Transactional:       │
                                            │    draft → ready        │
                                            └─────────────────────────┘
```

`apps/cli/`, `apps/task_builder/`, and `apps/orchestrator/` are peer entry points. `cli` and `task_builder` both create job rows; the orchestrator drains them.

---

## Layer 1 — The Coordinator (`apps/orchestrator/coordinator.py`)

**Default path is pure Python. LLM supervisor is an escape hatch.** The Coordinator owns the entire job lifecycle. 95% of its decisions are deterministic boolean checks ("does the input file exist?", "is the retry counter < 2?"). For the 5% where rules don't fit, it escalates to a single LLM supervisor call. The LLM never sits in the default hot path — that would burn money rubber-stamping obvious decisions and introduce non-determinism into control flow.

### Responsibilities

1. **State detection.** For each incoming job, query disk + Supabase to find out what already exists for this combo:
   ```python
   @dataclass(frozen=True)
   class ComboState:
       input_files_dir: Path | None       # data/generated/input_files/<combo>/
       scenarios_count: int                # rows in generated_scenarios for combo_key
       prompt_path: Path | None           # task_generation_prompts/<level>/<slug>.py OR data/generated/agent_prompts/...
       tasks_in_db: int                   # tasks where combo_key=... AND status='ready'
       last_failed_run: Optional[GenerationJob]  # for cross-stage retry hints
   ```

2. **Plan construction.** Build the minimal dispatch list from the gaps:
   ```python
   def build_plan(brief: TaskBrief, state: ComboState) -> list[Stage]:
       plan = []
       if state.input_files_dir is None:           plan.append(InputFilesStage)
       if state.scenarios_count < brief.count:     plan.append(ScenariosStage)
       if state.prompt_path is None:               plan.append(PromptsStage)
       plan.extend([TaskStage] * (brief.count - state.tasks_in_db))
       return plan
   ```

   Empty plan is a valid outcome: "everything's already there; nothing to do."

3. **In-process dispatch.** Each stage is a Python function called inside the same process. No subprocesses. Stage outputs are typed objects passed to the next stage, not files on disk handed off via path strings.

4. **Per-stage retry policy.** Default 2 retries per stage. Each stage's verifier returns either `Ok(output)` or `Retry(feedback: str)`. The Coordinator passes feedback to the next attempt as part of the brief.

5. **Cross-stage retry policy.** If Stage 4 returns `Retry` 2× with a "hollow task" verdict, the Coordinator doesn't keep retrying Stage 4 — it reruns **Stage 3 (prompt)** with the Stage 4 feedback hint, then resumes from Stage 4. This is the loop the subprocess chain cannot do. Capped at 1 cross-stage retry to prevent thrashing.

6. **Job row updates.** Every state transition updates the `generation_jobs` row: `queued → running → stage=input_files → stage=scenarios → … → done` (or `failed` with a reason). Crashes mid-stage are reaped by a watchdog that flips long-stuck rows back to `queued` or `failed`.

7. **Structured logs.** Each stage's stdout/stderr captured to per-stage files in the run scratch dir; final bundle pushed to object storage and the URL stamped on the job row.

### Skeleton

```python
# apps/orchestrator/coordinator.py
@dataclass(frozen=True)
class StageOutcome:
    name: str
    status: Literal["ok", "skipped_cached", "retry", "failed"]
    artifacts: dict[str, Any]
    feedback: str | None
    elapsed_s: float


class Coordinator:
    def __init__(self, job: GenerationJob, *, max_retries: int = 2):
        self.job = job
        self.max_retries = max_retries
        self.run_id = job.id
        self.scratch = Path(f"/tmp/utkrusht-runs/{self.run_id}")
        self.scratch.mkdir(parents=True, exist_ok=True)

    def run(self) -> JobResult:
        state = detect_state(self.job.brief)
        plan = build_plan(self.job.brief, state)
        outcomes: list[StageOutcome] = []
        for stage_cls in plan:
            outcome = self._dispatch(stage_cls, state, outcomes)
            outcomes.append(outcome)
            if outcome.status == "failed":
                return self._finalize_failed(outcomes)
            state = state.with_stage_done(outcome)
        return self._finalize_ok(outcomes)

    def _dispatch(self, stage_cls, state, prior) -> StageOutcome:
        feedback = None
        for attempt in range(1, self.max_retries + 1):
            self._log(f"[stage {stage_cls.name}] attempt {attempt}")
            stage = stage_cls(self.job.brief, state, self.scratch, feedback=feedback)
            outcome = stage.run()
            if outcome.status in ("ok", "skipped_cached"):
                return outcome
            feedback = outcome.feedback
        # Stage exhausted retries — does cross-stage fallback apply?
        if stage_cls is TaskStage and not self._already_fell_back(prior):
            return StageOutcome("fallback_to_prompts", "retry",
                                {}, feedback=feedback, elapsed_s=0)
        return StageOutcome(stage_cls.name, "failed", {}, feedback, 0)
```

The Coordinator is the only place where retry math lives. Stages don't know about retries. Verifiers don't know about retries. Single source of truth for "what does the system do when something fails."

### LLM Supervisor — the escape hatch

The Coordinator's decision tables encode the failure modes we've already seen and reasoned about. They can't encode failure modes we haven't seen yet. When a job hits an unknown verdict, an ambiguous partial state, or has exhausted the cross-stage retry budget without converging, the Coordinator calls a single LLM **once** to decide what to do next.

```python
# apps/orchestrator/supervisor.py — sketch
from pydantic import BaseModel
from pydantic_ai import Agent

class SupervisorDecision(BaseModel):
    action: Literal["retry_stage", "rerun_earlier_stage", "fail", "escalate_human"]
    target_stage: str | None       # required when action involves a stage
    feedback: str | None           # passed back into next attempt
    reason: str                    # one-sentence justification (logged)

supervisor = Agent(
    model="anthropic/claude-haiku-4-5",   # cheap; this is a judgement call
    result_type=SupervisorDecision,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
)

def ask_supervisor(job: GenerationJob, outcomes: list[StageOutcome]) -> SupervisorDecision:
    """Called only when the deterministic decision table returns 'unknown'."""
    return supervisor.run_sync(_render_job_context(job, outcomes)).data
```

**When the supervisor fires:**

| Trigger | Example |
|---|---|
| Verdict not in the decision table | Stage 4 returns `verdict="prompt_injection_detected"` — we never saw it before |
| Repeated cross-stage failure | Rerunning Stage 3 once didn't help; rerunning a second time is uncharted |
| Partial state we can't classify | Input files exist but background.json is malformed mid-file |
| Cost threshold tripped | A single job has burned >$2 in retries; should we keep going? |

**Cost.** A supervisor call uses Haiku 4.5 at ~$0.005 per invocation. Even fired on 20% of runs (unlikely once decision rules mature), it adds <$0.01 amortized per job. The whole point is that the supervisor is rare — if it fires on >5% of runs, the deterministic decision tables need to absorb that failure pattern as a hard-coded rule, and the supervisor is rate-limited until they do.

**What the supervisor doesn't do:**

- It does NOT dispatch stages itself — it returns a decision, the Coordinator dispatches.
- It does NOT see code files or task content — only the job's metadata, stage outcomes, and verdicts. Keeps the context small and the cost low.
- It is NOT called multiple times per job — at most once per "unknown" failure event. If its decision fails too, the job is marked failed.

---

## Layer 2 — Stage adapters + two-layer verifiers (`apps/orchestrator/stages/`)

Each adapter is a thin Python class that calls into the existing `generators/` package as a function (no subprocess), then runs **two layers of verification** on the output: a structural check (deterministic, fail-fast) followed by an LLM semantic verifier (judges quality).

### The two-layer verifier pattern

```
        Stage generator runs → produces output
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ Structural verifier (free)        │
        │ • JSON shape / regex / sim sim    │
        │ • E2B build+test (Stage 4)        │
        └──────────────┬───────────────────┘
                fail   │   pass
                       │
              ┌────────┴───────┐
              ▼                ▼
       retry with        ┌──────────────────────────────────┐
       shape feedback    │ LLM semantic verifier (~$0.02–05)│
       (no LLM cost)     │ • Realism, scope-fit             │
                         │ • Competency-coverage            │
                         │ • Didactic value                 │
                         └──────────────┬───────────────────┘
                                 fail   │   pass
                                        │
                               ┌────────┴────────┐
                               ▼                 ▼
                         retry with         proceed to
                         LLM feedback       next stage
```

**Why two layers.** Cheap structural pre-checks reject malformed output for free, so the LLM only judges well-shaped output. Saves money (no LLM call on bad shape), produces actionable feedback at each layer (shape errors → "missing `code_files` key"; semantic errors → "scenario asks for distributed consensus at BASIC level"), and keeps the LLM verifier focused on judging quality rather than disambiguating broken output.

### Stage table

| # | Stage | Generator (existing) | **Structural verifier** | **LLM semantic verifier** |
|---|---|---|---|---|
| 0 | preflight | `task_agent_preflight.run_global_checks` | Built into preflight (env vars, imports, classifier reachable) | — |
| 1 | input_files | `generators.input_files.generator.generate_input_files` | `verify_input_files_shape()` — required JSON keys, no `<TODO>` strings, length bounds | **Optional / light.** Judges whether `role_context` matches the stated proficiency; whether `questions_prompt` actually probes the listed competency. Cost ~$0.02; can be flagged off via `--skip-llm-verify input_files` for speed. |
| 2 | scenarios | `generators.scenarios.generator.generate_scenarios_for_competencies` | `verify_scenarios_shape()` — three-section regex (`**Current Implementation:**`, `**Your Task:**`, `**Success Criteria:**`); length bounds; embedding cosine sim < 0.85 vs existing for same combo | **Required — biggest quality lift.** Per-scenario judgment across four dimensions: realism (is this an actual real-world problem?), scope-fit (completable in 30–60 min at this proficiency?), competency-coverage (does it exercise the listed competency or drift off-topic?), specificity (concrete current implementation, not abstract). Returns verdict + per-dimension feedback. Cost ~$0.05 per batch. |
| 3 | prompts | `generators.prompts.agent.PromptGeneratorAgent` | DSPy's existing `VerifyPromptSignature` (AST parse, `PROMPT_REGISTRY` key, format placeholders, canonical JSON keys) | **Optional.** Post-DSPy semantic check — does this prompt give a downstream LLM enough concrete context to produce a realistic task? Are instructions unambiguous? Will format-string templating fill all the placeholders? Cost ~$0.05. Often skipped because DSPy's internal Generate/Verify loop already iterates until structurally valid, and curated prompts (`task_generation_prompts/<Level>/`) bypass this stage entirely. |
| 4 | tasks | `generators.task.agent_creator.create_task_with_tools` (NEW — Layer 3) | **The E2B build+test gate is the structural verifier** — runs INSIDE the agent loop via tools (Layer 3). Verifies code compiles, tests run, files present. | **Already in place** — persona-routed `infra.evals.{llm_task_eval, llm_code_eval}`. Runs ONCE in fresh isolated context on the tool-verified output. Judges realism, didactic value, scope, code quality, answer correctness. Cost ~$0.10–0.15. |

**Stage 2 is where the LLM verifier earns the most.** Today's scenario generator has an internal "≥1 of 3 evals must pass" gate that's too lax — drifty or off-scope scenarios slip through, then poison Stages 3 and 4 downstream. A dedicated post-generation LLM verifier with structured per-dimension feedback ("scope-fit FAIL: completing this requires distributed-systems knowledge above BASIC") catches the failure at the cheapest possible point in the pipeline.

### What an LLM verifier looks like

These are lightweight Pydantic AI agents — single LLM call, structured output. Not multi-turn agents.

```python
# apps/orchestrator/verifiers/scenarios.py — sketch
from pydantic import BaseModel
from pydantic_ai import Agent

class ScenarioVerdict(BaseModel):
    passed: bool
    realism: Literal["pass", "fail"]
    scope_fit: Literal["pass", "fail"]
    competency_coverage: Literal["pass", "fail"]
    specificity: Literal["pass", "fail"]
    feedback: str   # actionable hint for the next attempt if any dim failed

scenario_verifier = Agent(
    model="anthropic/claude-haiku-4-5",   # cheap, fast
    result_type=ScenarioVerdict,
    system_prompt=SCENARIO_VERIFIER_PROMPT,
)

def verify_scenarios(scenarios: list[str], brief: TaskBrief) -> StageOutcome:
    # Structural first — cheap, fail fast
    struct = verify_scenarios_shape(scenarios, brief)
    if not struct.ok:
        return StageOutcome("scenarios", "retry", {}, struct.feedback, 0)

    # LLM second — only if structurally valid
    verdicts = [
        scenario_verifier.run_sync(_render(s, brief)).data
        for s in scenarios
    ]
    failed = [v for v in verdicts if not v.passed]
    if failed:
        return StageOutcome("scenarios", "retry", {},
                            _combine_feedback(failed), 0)
    return StageOutcome("scenarios", "ok", {"scenarios": scenarios}, None, 0)
```

The same pattern applies to all LLM verifiers — they're single-call judgments, not multi-turn agents.

### Stage adapter skeleton

```python
# apps/orchestrator/stages/input_files.py
class InputFilesStage:
    name = "input_files"

    def __init__(self, brief, state, scratch_dir, feedback=None):
        self.brief = brief
        self.state = state
        self.scratch = scratch_dir
        self.feedback = feedback  # ignored — input_files doesn't take feedback hints

    def run(self) -> StageOutcome:
        if self.state.input_files_dir is not None:
            return StageOutcome(self.name, "skipped_cached",
                                {"input_files_dir": self.state.input_files_dir},
                                None, 0)
        t0 = time.time()
        output_dir = generate_input_files(
            competency_name=", ".join(self.brief.competency_names),
            proficiency=self.brief.proficiency,
            env=self.brief.env,
            domain=self.brief.domain,
            output_root=self.scratch / "input_files",
        )
        verdict = verify_input_files_shape(output_dir)
        if not verdict.ok:
            return StageOutcome(self.name, "retry",
                                {}, verdict.feedback, time.time() - t0)
        return StageOutcome(self.name, "ok", {"input_files_dir": output_dir},
                            None, time.time() - t0)
```

Sub-100-LOC per stage. The generator is the existing module; the verifier is one function.

### Per-run scratch layout

```
/tmp/utkrusht-runs/<run_id>/
├── input_files/<combo>/
│   ├── competency_<combo>_<level>.json
│   └── background_<combo>_<level>.json
├── scenarios/
│   └── <combo>_<level>.json
├── prompt/
│   └── <combo>_<level>_prompt.py
├── task/
│   ├── code_files/             ← what the Stage 4 agent wrote
│   ├── task_output.json        ← the final TaskOutput
│   └── gate_logs/              ← E2B run logs from tools
└── stages/
    ├── 01_input_files.{stdout,stderr,timing.json}
    ├── 02_scenarios.{stdout,stderr,timing.json}
    ├── 03_prompts.{stdout,stderr,timing.json}
    └── 04_task.{stdout,stderr,timing.json}
```

End of run: the orchestrator bundles `stages/*` to object storage, stamps the URL on the job row, and `rm -rf`s the scratch dir. **`git status` clean after every run.**

---

## Layer 3 — The Stage 4 Task Agent (`generators/task/agent_creator.py`)

This is the one place the agent pattern earns its keep, and it replaces the current generate-then-eval-then-maybe-retry loop with a tool-using inner loop.

### Why this matters

Today's pattern (current `generators/task/creator.py`):

```
generate full task → eval critics → E2B gate → if fail, regenerate whole task with feedback string → repeat ×3
```

When the gate says "test_foo failed: AssertionError at line 12 of processor.py," the feedback flows back into the *next* generation as a string. The model re-writes the entire task, including the eight files that were already fine, with that string as one of many inputs. Wasteful and ineffective — small fixes turn into full regenerations.

The v2 pattern:

```
agent:
  write code_files
  call run_tests(code_files)
    → "exit=1, test_foo failed: AssertionError at processor.py:12"
  read pytest stderr, decide: "I need to fix processor.py only"
  rewrite processor.py
  call run_tests(code_files)
    → "exit=0, 5 passed"
  return TaskOutput
```

The model has the entire context of what it just wrote when it sees the error. It fixes one file. It re-checks. It returns once verified.

This is a textbook tool-using agent loop — the same pattern that makes Claude Code useful for coding. The Anthropic / OpenAI / Pydantic AI agent frameworks all implement this primitive; we just need to choose one and wire our tools.

### The agent loop

```python
# generators/task/agent_creator.py — sketch using Pydantic AI

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

class TaskOutput(BaseModel):
    name: str
    question: str
    code_files: dict[str, str]
    answer: str
    outcomes: str
    hints: str

class AgentCtx(BaseModel):
    combo_key: str
    template: TemplateSpec
    brief: TaskBrief

task_agent = Agent(
    model="anthropic/claude-sonnet-4-6",   # via Portkey
    deps_type=AgentCtx,
    result_type=TaskOutput,
    system_prompt=TASK_AGENT_SYSTEM_PROMPT,  # static, ~1K tokens
)

@task_agent.tool
async def run_tests(ctx: RunContext[AgentCtx], code_files: dict[str, str]) -> str:
    """Boot the E2B template, write code_files, run build_cmd + test_cmd.
    Returns a structured string with exit code + stderr tail."""
    plan = ResolvedPlan(combo_key=ctx.deps.combo_key,
                       task_runtime=infer_runtime(ctx.deps.template),
                       template=ctx.deps.template)
    result = run_sandbox_eval(code_files, plan)
    return f"exit={result.exit_code}\nverdict={result.verdict}\n--- output (tail) ---\n{result.stdout_tail}"

@task_agent.tool
async def verify_code(ctx: RunContext[AgentCtx], language: str, content: str) -> str:
    """Syntax check without booting a sandbox. Cheap pre-flight before run_tests."""
    return verify_syntax(language, content)  # py_compile / tsc --noEmit / javac

@task_agent.tool
async def check_files(ctx: RunContext[AgentCtx], code_files: dict[str, str]) -> str:
    """Confirm required artifacts present: README.md, requirements.txt,
    run.sh, tests/."""
    return check_required_files(code_files, REQUIRED_PATHS[ctx.deps.template.runtime])


def create_task_with_tools(brief: TaskBrief, plan: ResolvedPlan, prompt: str) -> TaskOutput:
    ctx = AgentCtx(combo_key=plan.combo_key, template=plan.template, brief=brief)
    user_message = build_task_user_prompt(brief, plan, prompt)
    return task_agent.run_sync(user_message, deps=ctx).data
```

After the agent returns, the eval critics run **once** in a fresh context (Pydantic AI agent with `result_type=EvalVerdict`). They never see the agent's tool-call history, so they can't be biased by "the agent already passed run_tests." The eval critic is the independent judge of semantic quality (scope fit, realism, didactic value). The agent's tools cover structural correctness (compiles, tests run).

### Tool catalog (Layer 3 dependency)

| Tool | What it does | Implementation | Cost / latency |
|---|---|---|---|
| `run_tests(code_files)` | E2B sandbox: `build_cmd` + `test_cmd` from `plan.template`. Returns exit code + stdout/stderr tail. | Wraps `infra.e2b.sandbox_eval.run_sandbox_eval` (already exists; B6 wiring already done) | ~30s per call; uses a real sandbox |
| `verify_code(language, content)` | Single-file syntax check. Faster than `run_tests`. Use for "did I just write valid Python?" before paying for an E2B boot. | `py_compile` (Python); `tsc --noEmit` (TS); `javac` (Java). New, ~50 LOC per language. | <1s per call; local |
| `check_files(code_files)` | Required-files presence check (README, requirements.txt, run.sh, tests/test_*.py). | New, ~20 LOC; consults the template's REQUIRED_PATHS map | <1ms; pure Python |
| `run_compose(code_files)` | `docker compose up -d --wait`. Only relevant when the task ships a `docker-compose.yml`. | Wraps the existing branch in `sandbox_eval` that already does this | ~60s; only fires when needed |
| `dedupe_scenario(scenario, combo_key)` | Embedding similarity vs existing scenarios for the same combo. Returns `(closest_existing, similarity_score)`. | Reuses fastembed (already a transitive dep); new ~30 LOC | <1s; local |

`run_tests` is the most expensive tool and the most valuable one. The agent's system prompt teaches it to call `verify_code` and `check_files` first (cheap), and only call `run_tests` once those pass.

### Framework: Pydantic AI + Portkey

Five reasons:

1. **Model-agnostic.** Today's code routes Claude Sonnet for evals (good at structured criticism) and GPT-5.4 for code generation (good at codegen). Locking to one model family throws that away. Pydantic AI's `model="anthropic/...|openai/...|portkey/..."` strings let us route per-call site.
2. **Pydantic schemas integrate cleanly.** `infra/schemas.py` already uses Pydantic; the agent's `result_type=TaskOutput` reuses the same model.
3. **Tool ergonomics.** `@agent.tool` is the same pattern as Anthropic's `@tool` but works against any model.
4. **Manual context management is fine.** Our agent runs are bounded — a typical Stage 4 run uses ~15–25K tokens total, well within any model's 200K window. We don't need automatic compaction.
5. **Portkey integration is officially supported** — same gateway we already route through.

What we don't get: automatic context compaction across long agent loops. We don't need it — see (4).

---

## Data model

Three tables. All multi-tenant from day one (`organization_id` column on every row, hardcoded to Utkrusht's UUID for v1).

### `generation_jobs`

```sql
CREATE TABLE generation_jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     uuid NOT NULL,
    conversation_id     uuid REFERENCES conversations(id),
    requested_by        uuid,
    brief               jsonb NOT NULL,            -- snapshot of TaskBrief at submit
    status              text NOT NULL DEFAULT 'queued',  -- queued|running|done|failed
    stage               text,                      -- last stage attempted
    log_url             text,                      -- object storage path
    result_task_id      uuid REFERENCES tasks(task_id),
    error               text,                      -- when status=failed
    cost_usd            numeric(8,4),              -- LLM spend for this run
    started_at          timestamptz,
    finished_at         timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON generation_jobs (status, created_at);
CREATE INDEX ON generation_jobs (organization_id, created_at DESC);
```

The orchestrator worker polls with `SELECT … FOR UPDATE SKIP LOCKED LIMIT 1`. Cap concurrent workers via process count. A watchdog cron returns rows that have been `running` for >30 min to `queued` or `failed`.

### `conversations`

```sql
CREATE TABLE conversations (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   uuid NOT NULL,
    started_by        uuid,
    messages          jsonb NOT NULL DEFAULT '[]',
    final_brief       jsonb,
    status            text NOT NULL DEFAULT 'active',
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    submitted_at      timestamptz,
    abandoned_at      timestamptz
);
```

One conversation captures the user-facing dialogue (`task_builder` chat). It can produce multiple `generation_jobs` (re-generate, refine brief, etc).

### `tasks` (existing — adds two columns)

```sql
ALTER TABLE tasks
    ADD COLUMN combo_key text REFERENCES competency_combo_classification(combo_key),
    ADD COLUMN created_by_job_id uuid REFERENCES generation_jobs(id);
```

`combo_key` ties tasks to the cache row that classified them. `created_by_job_id` ties tasks back to the run that produced them (audit + observability).

The existing B1 (`competency_combo_classification`) and B6 (`template_registry`) tables stay as-is — they're already wired.

---

## Cross-stage retry policy

The Coordinator owns this. Two retry budgets:

1. **Per-stage retries** (default 2). Inside the Coordinator's `_dispatch` loop. Used when the stage's *own* verifier says "retry with this feedback." Stage 4's tool-using agent makes this rare — the agent self-corrects internally before returning — but the budget exists for failures the agent can't fix (e.g., E2B infra outage; eval critic verdict).

2. **Cross-stage retry** (default 1). When Stage 4 exhausts its per-stage budget with a "hollow task" or "off-scope" verdict, the Coordinator doesn't keep hammering Stage 4. It returns to **Stage 3 (prompts)** with the Stage 4 feedback as a hint ("the prompt produced 3 hollow generations — try a more structurally specific instruction"), regenerates the prompt, then resumes from Stage 4. Capped at 1 cross-stage retry to prevent infinite loops.

Decision rules:

| Stage 4 failure verdict | Per-stage retry? | Cross-stage retry to Stage 3? |
|---|---|---|
| `gate_failed` (pytest exit ≠ 0, ≠ 5) | yes (agent fixes locally) | no |
| `pip_failed` | yes (agent fixes requirements) | no |
| `hollow_task` (eval critic) | yes (1×) | yes (1×) |
| `off_scope` (eval critic) | yes (1×) | yes (1×) |
| `infra_error` (E2B boot fail, etc) | yes (3×) | no |
| `truncated_output` | yes (with shorter prompt hint) | no |

Cross-stage retry is conservative because Stage 3 (DSPy prompt generation) takes 60–120s. We only do it when the failure pattern points at the prompt, not the task.

---

## Observability

Four sinks. All use the existing `[bracket-prefix]` log convention.

1. **Structured per-stage logs.** Every stage emits `[stage S]`-prefixed lines for boot, work, verdict. Same shape as the existing `[e2b-gate]` block. Captured to `/tmp/utkrusht-runs/<run_id>/stages/0X_*.{stdout,stderr,timing.json}`, bundled to object storage at run end.

2. **Job row updates.** `generation_jobs.stage` and `generation_jobs.status` updated at every transition; `log_url` stamped at completion. The web UI polls / streams from here.

3. **Metrics (Phase 3 of the migration below).** Counters: jobs queued/running/done/failed by org. Histograms: stage timings p50/p95. Gauges: queue depth, oldest queued job age. Counters: cross-stage retries fired, gate skip-by-reason, tool calls per stage, LLM cost per stage per model.

4. **Alerts** (Phase 3): classifier failure rate, gate skip-rate for *known* runtimes, queue depth > N, oldest queued > 1h, orphan-task count from the reconciler.

---

## CLI + API surface

After v1 ships, three entry points all converge on `generation_jobs`:

| Surface | Command | Behaviour |
|---|---|---|
| CLI (local) | `python -m apps.orchestrator --name "Python" -p BASIC --count 6 --env dev` | Inserts a job row; runs the worker inline (blocks until done); streams stage logs to stdout. |
| CLI (background) | `python -m apps.orchestrator submit --name "Python" -p BASIC --count 6` + `python -m apps.orchestrator worker` | Submit returns immediately with `job_id`. Worker process(es) drain the queue. |
| Web API | `POST /api/generate` (called by `apps/task_builder/`) | Creates a `conversations` row, inserts a `generation_jobs` row, returns `{ job_id, conversation_id }`. SSE stream from `/api/runs/<job_id>/events` reads from the worker's log location. |

`task_builder`'s `runner.py` becomes a thin SSE streamer — no more spawning subprocesses from a thread. The conversational chat UI stays unchanged.

The legacy `multiagent.py` shim stays for one release cycle. `run_pipeline.py` is deleted.

---

## A concrete walkthrough

User submits: `python -m apps.orchestrator --name "Python" -p BASIC --count 1 --env dev`

1. CLI inserts `generation_jobs` row (`status=queued`). Returns job_id.
2. Worker picks it up via `SELECT … FOR UPDATE SKIP LOCKED`. Marks `status=running`.
3. Coordinator reads state:
   - `data/generated/input_files/input_python/` **exists** (we generated it last week).
   - `generated_scenarios` table has **6 scenarios** for `combo_key="Python (BASIC)"` (≥1 → enough).
   - `task_generation_prompts/Basic/python_basic_prompt.py` **exists** (curated).
   - `tasks` table has **3 ready tasks** for this combo (count=1, so we need 1 more).
4. Plan: `[TaskStage]` only. Stages 1–3 skipped.
5. `TaskStage.run()` invokes `generators.task.agent_creator.create_task_with_tools(brief, plan, prompt)`.
6. The Pydantic AI agent:
   - Writes 8 code files (README, requirements.txt, run.sh, main.py, processor.py, data/shipments.csv, tests/test_processor.py, .gitignore).
   - Calls `verify_code("python", main.py)` → `ok`.
   - Calls `verify_code("python", processor.py)` → `ok`.
   - Calls `check_files(code_files)` → `ok`.
   - Calls `run_tests(code_files)` → exit=1, "test_foo failed: ValueError on processor.py:23".
   - Reads the error. Decides: the test was supposed to fail (by-design starter), but the answer file is wrong. Updates the answer.
   - Calls `run_tests(code_files)` again with the updated answer → exit=0, "5 passed".
   - Returns `TaskOutput`.
7. Eval critics fire ONCE on the verified output in fresh context. Both pass.
8. Persistence:
   - `INSERT INTO tasks (organization_id, combo_key, status='draft', ...) RETURNING task_id`.
   - Create GitHub template repo named after `task_id`.
   - Create answer repo, upload solution.
   - Create gist.
   - `UPDATE tasks SET status='ready', resources={...}`.
9. Coordinator marks `generation_jobs.status=done`, stamps `result_task_id`, bundles logs to object storage, writes `log_url`.
10. CLI prints summary; web UI sees the job complete via SSE.

Total time: probably 60–120s for this cached case (skip 3 stages, the agent loop has 1 internal retry). Compare today's ~9 min for the same combo because we re-do every stage.

---

## Migration phases

Seven chunks, ~14 working days. Each lands as a separate PR; each is independently shippable.

| # | Chunk | What | Days | Depends on |
|---|---|---|---|---|
| 1 | **Orchestrator skeleton** | `apps/orchestrator/{coordinator, state, plan, stages/*}`. In-process function calls; replaces `run_pipeline.py`. Per-run `/tmp/utkrusht-runs/<run_id>/` scratch. CLI invocation; no DB queue yet. | 2 | — |
| 2 | **Structural verifiers** | `verify_input_files_shape()`, `verify_scenarios_shape()` (regex + embedding dedup). Existing eval critics stay for Stage 4. | 1 | 1 |
| 3 | **LLM semantic verifiers** | `apps/orchestrator/verifiers/{input_files,scenarios,prompts}.py` — single-call Pydantic AI agents with structured per-dimension verdicts. Stage 2 (scenarios) is required and highest-ROI; Stages 1 + 3 ship as optional, flagged on by default. | 1.5 | 2 |
| 4 | **Job table + worker** | `generation_jobs`, `conversations` tables. `python -m apps.orchestrator worker` polls Postgres with `FOR UPDATE SKIP LOCKED`. Watchdog cron. | 3 | 3 |
| 5 | **Stage 4 tool-using agent** | `generators/task/agent_creator.py` + Pydantic AI + Portkey + 4 tools (`run_tests`, `verify_code`, `check_files`, `run_compose`). Coordinator picks via `--agent-mode={legacy,tools}` flag; side-by-side comparison runs. | 5 | 1 |
| 6 | **Transactional persistence + reconciler** | Reorder `create_task` to insert `tasks(status='draft')` BEFORE GitHub. Daily reconciler that marks `broken` on drift and deletes failed-task artifacts >7d old. | 1 | 1 |
| 7 | **Observability + LLM Supervisor** | `[orchestrator]` / `[stage N]` log blocks. Job-row log_url. Metrics endpoint. Initial alerts. Plus the `apps/orchestrator/supervisor.py` escape hatch fired on "unknown verdict" and cost-threshold tripwires. | 1.5 | 4 |

Phases 1+2+3 deliver value alone (skip-cached + better Stage 2 verification) even before the agent upgrade lands in Phase 5. Phase 5 is where the biggest quality lift happens — and where it's worth running both the legacy and agentic creators side-by-side for a few weeks to confirm the agent is genuinely better (eval critic verdicts + sandbox gate pass-rate + human review).

Phase 4 (job queue) is the heaviest but unblocks the web UI's "kick off a run and walk away" mode.

The LLM supervisor in Phase 7 ships *last* deliberately — we want to first observe which deterministic decision-table failures actually occur in production before deciding what the supervisor needs to reason about. Shipping it before we have that data risks building an over-general agent for problems we don't have.

---

## Out of scope (defer to v2)

Things deliberately not in v1:

| Item | Why defer |
|---|---|
| **Intake Agent** (parse messy customer briefs into a `TaskBrief`) | Different problem; needs the task_builder chat UI we already have to evolve before adding LLM parsing. The brief structure is the API contract; let humans fill it for now. |
| **6 task-type generation graph** (DEBUG, PR REVIEW, DESIGN REVIEW, UX, MANAGE INFRA) | BUILD is the only type running through this pipeline today. Add DEBUG using the same tool-using agent pattern once v1 BUILD is stable. Don't generalize for six types until two work. |
| **DSPy cross-codebase optimization** | Needs ≥50 human-rated tasks per type. We don't have the dataset. Start collecting ratings now; revisit when the corpus is there. |
| **Customer-specific generation** (per-org preferences, domain context injection) | v1 is single-org (Utkrusht). Multi-tenant schema is in place from day one (`organization_id` everywhere), so v2 is a data + RLS change, not a schema change. |
| **Multi-judge eval ensemble** (different model for generation vs eval ensemble) | Today we already route Claude Sonnet for evals + GPT for generation — that's de-facto cross-provider. Adding a *third* judge model for high-stakes verdicts is a v2 optimization once we have data on where single-judge fails. |
| **Run replay / DAG visualisation** | Nice to have. Job row + structured logs already cover the audit need. Build only when debugging becomes a real time sink. |

---

## Open questions to lock before starting

1. **Framework: confirm Pydantic AI + Portkey.** I'm strongly biased here (model-agnostic + tool ergonomics + already use Portkey + Pydantic). The alternative is Anthropic SDK (Claude-only, free context management). My recommendation: Pydantic AI. **Decide:** yes / no.
2. **Which LLM verifier stages ship enabled by default.** Stage 2 (scenarios) is required — biggest ROI. Stages 1 + 3 are optional. My recommendation: enable all three by default in Phase 3; provide `--skip-llm-verify <stage>` flag for fast dev iteration. The marginal cost is ~$0.12 per fully-verified run. **Decide:** enable 1+2+3 by default / enable only 2 by default / make all opt-in.
3. **LLM verifier model.** Haiku 4.5 for verifiers and supervisor (cheap, fast, good enough for judgement); Sonnet 4.6 for the Stage 4 generator agent and the persona-routed eval critics. **Decide:** Haiku-for-verifiers / Sonnet-for-everything.
4. **Cross-stage retry cap.** Default 1 (Stage 4 fails → Stage 3 reruns once → if Stage 4 still fails, mark job failed or escalate to LLM supervisor). Considering 2 if classifier confidence is low. **Decide:** 1 / 2.
5. **Single PR or split PRs for Phase 5.** "Legacy + tools side-by-side with a flag" lets us validate the new agent against the old. Or just commit fully to the agent and delete legacy on the same PR. **Decide:** side-by-side / cutover.
6. **Worker concurrency model.** Phase 4 ships with a single-process worker (one job at a time). Lifting to N parallel workers is trivial (process pool reading the same queue). When? **Decide:** v1 single-worker, v2 multi-worker / v1 multi-worker from day one.
7. **`task_builder/runner.py` rewrite timing.** It's the last spot still spawning subprocesses (from a thread per request, with `RUNS` as an in-memory dict). Rewrite it as an SSE streamer reading from the worker's log location — lands with Phase 4 (job table) or Phase 7 (observability)? **Decide:** with 4 / with 7 / separate small PR.

---

## What we get when v1 is done

- **One command.** `python -m apps.orchestrator --name "Python" -p BASIC --count 6` produces six verified tasks. The same command, run twice for the same combo, skips work that's already done.
- **Web UI submits jobs.** `POST /api/generate` from `task_builder` returns immediately with a job_id; SSE stream surfaces stage progress. No more subprocess-from-thread.
- **Two-layer verification at every stage.** Structural pre-check (free, fail-fast) plus an LLM semantic verifier (judges realism, scope-fit, competency-coverage). Stage 2's verifier catches off-scope and unrealistic scenarios before they poison downstream stages — biggest quality lift over today's pipeline.
- **Self-correcting code generation.** Stage 4's agent calls `run_tests` mid-generation, reads the actual pytest stderr, fixes one file, re-checks, returns. Fewer regenerations, higher first-pass success.
- **Deterministic coordinator with LLM escape hatch.** The control flow is plain Python decision tables; an LLM supervisor steps in only when those tables hit an unknown verdict or repeated cross-stage failure. Rare path, high judgment, low amortized cost.
- **Durable jobs.** Process crash mid-run doesn't lose the work — the row stays in `generation_jobs`; the watchdog reaps it or another worker picks it up.
- **Clean source tree.** All generated outputs land in `/tmp/utkrusht-runs/<run_id>/` or Supabase. `git status` clean after any number of runs.
- **Multi-tenant ready.** v2 opens to customer orgs without a schema change — just switching `UTKRUSHT_ORG_ID` from a constant to `auth.org_id()`.

---

## Reference: composition with existing infrastructure

The v2 architecture builds on these already-shipped pieces:

- **`generators/{input_files, scenarios, prompts, task}/`** — engines. v2 calls them as Python functions instead of subprocesses.
- **`infra/classifier/`** — TaskRuntime model + LLM classifier. v2 uses it through `generators.task.runtime_resolver.resolve_plan` (the combo cache).
- **`infra/e2b/sandbox_eval.run_sandbox_eval`** — already reads `plan.template.build_cmd/test_cmd` from the `template_registry` (B6 wiring done). Wraps cleanly as the `run_tests` tool for Stage 4.
- **`competency_combo_classification`** — combo classification cache (B1 done). Coordinator reads from this on every run.
- **`template_registry`** — DB-backed runtime → template mapping (B6 done). The agent's tools read recipes from here.
- **`infra/evals.py`** — persona-routed eval critics. Run once in fresh context after the agent returns its verified output.
- **`apps/cli/`** — Click commands. Picks up `python -m apps.orchestrator` as a new entry point alongside `generate_tasks`.

The new code is the Coordinator + stage adapters + the Stage 4 agent + structural verifiers + the worker + the two new tables. Everything else is existing infrastructure plugged into a saner shape.
