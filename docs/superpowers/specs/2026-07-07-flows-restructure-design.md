# Flows Restructure — Symmetric `flows/` Architecture

**Date:** 2026-07-07
**Status:** Design (awaiting review) → implementation plan
**Author:** rohansx + Claude
**Scope decision:** Full symmetric `flows/` · behavior-preserving (convention + subprocess) · `task_generation_prompts` moves per-flow · `gist_manager` folds into `apps/cli`

---

## 1. Problem

The repo has grown into **3–4 distinct "flows"** (the main tech task-generation pipeline, `pr_review`, `non_tech`, and a since-removed `design_review`), but they are organized inconsistently, and there is leftover scaffolding from a half-finished 2026-05-22 layout migration.

Concrete, verified issues:

1. **`task_agent_preflight.py` is a loose root script but is actually stage 0 of the pipeline.** `run_pipeline.py` chains `preflight → generate_input_files → scenarios → prompts → generate_tasks`. A pipeline stage should live inside the pipeline.

2. **`multiagent.py` + `cli/` + empty `apps/` is migration debris.** `multiagent.py`'s own docstring says it is a temporary shim to be deleted "once those callers are moved to `python -m apps.cli`." That move never happened: `apps/` is empty, the real Click commands sit in top-level `cli/`, and `multiagent.py` re-exports them. Three places, one job.

3. **The tech flow is the one flow *not* under `flows/`.** It is smeared across `run_pipeline.py` (root), `generators/{input_files,scenarios,prompts,task}`, `task_agent_preflight.py` (root), and `cli/`. Meanwhile `flows/` contains only the *secondary* flows (`non_tech/`, `pr_review/`). The primary flow is organized least like a flow.

**Underlying theme:** multiple flows exist, but only the secondary ones are packaged as flows; the main one is scattered, plus there is dead migration scaffolding.

---

## 2. Decisions (locked)

| Decision | Choice |
|---|---|
| Ambition | **Full symmetric `flows/`** — every flow is a sibling package with an identical internal shape |
| Stage-execution model | **Convention + manifest, keep subprocess isolation** — behavior-preserving reorg, *not* an in-process Stage-ABC rewrite (deferred) |
| `task_generation_prompts/` | Move **per-flow** — tech templates → `flows/tech/prompt_templates/`; non_tech-consumed templates → `flows/non_tech/prompt_templates/` (see §5 nuance) |
| `gist_manager.py` | Fold into `apps/cli` as a `gist` subcommand |
| Backward-compat | **Clean break, single swing** — update all in-repo callers, no legacy shims |

---

## 3. Target structure

```
flows/
  _base/                     # generic, flow-agnostic pipeline machinery
    stage.py                 # @dataclass StageSpec(name, module, needs, log_dir, live_split)
    registry.py              # ordered StageSpec lists, one per flow (source of truth for stage order)
    runner.py                # subprocess runner extracted from run_pipeline.py (UNCHANGED behavior)
  tech/                      # THE main task-generation flow
    __main__.py              # `python -m flows.tech` → run the pipeline
    pipeline.py              # thin: reads registry, calls _base.runner  (was run_pipeline.py)
    stages/
      preflight.py           # was task_agent_preflight.py
      input_files/           # was generators/input_files/
      scenarios/             # was generators/scenarios/
      prompts/               # was generators/prompts/  (agent, retriever, validator, shape_classifier, …)
      generate/              # was generators/task/     (creator, evaluator, gate, persistence, runtime_resolver, …)
    prompt_templates/        # tech-specific {level}/{tech}_prompt.py (from task_generation_prompts/)
  pr_review/                 # already a flow — internals untouched (import updates only)
  non_tech/                  # already a flow — internals untouched
    prompt_templates/        # the Basic/* templates non_tech consumes (from task_generation_prompts/)
  design_review/             # reserve name + README stub (code was removed; not recreated)
apps/
  cli/                       # the ONE human entrypoint
    __main__.py              # `python -m apps.cli` (Click group)
    generate.py              # was cli/generate.py
    gist.py                  # was gist_manager.py (as `apps.cli gist …`)
infra/                       # shared libs — unchanged + receives lifted shared helpers (§4)
  supabase.py                #   init_supabase (lifted)
  infra_kinds.py             #   resolve() (lifted)
  scenario_key.py            #   build_scenario_key (lifted)
```

**Symmetry contract** — every flow package under `flows/` provides:
- a `__main__.py` (human/runner entry),
- a `stages/` package (or single module for trivial flows),
- its own `prompt_templates/` when it owns prompt files,
- and imports **only** from `flows/_base` and `infra/` — never from a sibling flow.

Each big stage keeps its own `__main__.py`, so the runner still shells out exactly like today (`python -m flows.tech.stages.prompts` replaces `python -m generators.prompts`). **Zero behavior change — only addresses change.**

---

## 4. Shared-helper extraction (the load-bearing step)

Other flows and apps reach into `generators/` today, so a naive move breaks them. **Rule: anything imported by a *different* flow or by `task_builder`/`trace_ui` is lifted to `infra/` (shared); everything else moves into the owning flow.**

Verified shared surface to lift:

| Symbol (today) | Consumers outside the tech flow | New home |
|---|---|---|
| `generators.task.persistence.init_supabase` | `task_builder/{jobs,server,conversation_repo}` (×5) | `infra/supabase.py` |
| `generators.scenarios.build_scenario_key` | `flows/pr_review/pr_review_multiagent.py` | `infra/scenario_key.py` |
| `generators.prompts.infra_kinds.resolve` | `trace_ui/server.py` (×2) | `infra/infra_kinds.py` |

After lifting, `flows/tech/` contains only tech-specific stage code, and **no flow imports another flow's guts.** The tech flow's own `persistence.py` / `scenarios` / `prompts` re-import these from `infra/`.

---

## 5. Nuance: `task_generation_prompts/` is shared by two flows

`flows/non_tech/non_tech_utils.py` imports `task_generation_prompts.Basic.Prompt_basic` and `…ai_evals_for_product_managers_basic_prompt`, and dynamically loads more via `get_task_prompt_by_technology_stack`. So `task_generation_prompts/` is **not** purely tech.

**Recommendation (truly symmetric):** split ownership.
- Tech-consumed templates → `flows/tech/prompt_templates/`
- non_tech-consumed templates → `flows/non_tech/prompt_templates/`
- Audit the exact non_tech set during implementation (the two static imports plus whatever `get_task_prompt_by_technology_stack` resolves at runtime).

This is better than dumping everything into `flows/tech/` (which would make `non_tech` import a sibling flow — the exact anti-pattern we're removing). `PROMPT_ROOT` path constants in `flows/tech/stages/prompts/{retriever,__main__}.py` (currently `repo_root/task_generation_prompts`) update to the new tech location.

**Partition verified (2026-07-07):** `non_tech` statically imports exactly two files — `Basic/Prompt_basic.py` and `Basic/ai_evals_for_product_managers_basic_prompt.py` (both non-tech-domain). The tech flow never references either by name (grep clean), and resolves templates by tech-stack slug, so it would never match them. **No single file is shared by both flows → per-flow ownership confirmed; a shared `assets/prompt_templates/` store is rejected as unnecessary.**
- `flows/tech/prompt_templates/` ← everything (incl. `_general_reference/`, all `{tech}_prompt.py`) **except** those two files.
- `flows/non_tech/prompt_templates/Basic/` ← `Prompt_basic.py` + `ai_evals_for_product_managers_basic_prompt.py`.

**Remaining check (Phase 4):** `non_tech`'s dynamic loader `get_task_prompt_by_technology_stack(...)` must be audited to confirm it only resolves non_tech's own templates. If it turns out to pull generic tech templates at runtime, revisit the shared-store option for just that shared subset.

---

## 6. `flows/_base` stage contract (behavior-preserving)

`run_pipeline.py` already contains all the machinery (`_pick_python`, `_run_stage`, `_run_stage_streaming`, per-stage env, timing/log dirs, `live_split` streaming, stop-on-first-failure). We **extract, not rewrite**:

```python
# flows/_base/stage.py
@dataclass(frozen=True)
class StageSpec:
    name: str                       # "preflight", "input_files", …
    module: str                     # "flows.tech.stages.preflight"  (python -m target)
    needs: tuple[str, ...] = ()     # ordering hint / doc; runner is linear today
    live_split: tuple = ()          # (filename, markers) streaming rules (stage 04 today)
    exit0_on_reject: bool = False   # stage 04 exits 0 even on eval-gate reject
```

```python
# flows/_base/registry.py
TECH_STAGES = [
    StageSpec("preflight",   "flows.tech.stages.preflight"),
    StageSpec("input_files", "flows.tech.stages.input_files"),
    StageSpec("scenarios",   "flows.tech.stages.scenarios"),
    StageSpec("prompts",     "flows.tech.stages.prompts"),
    StageSpec("generate",    "flows.tech.stages.generate", live_split=(...), exit0_on_reject=True),
]
```

`flows/_base/runner.py` = today's `_run_stage*` functions, iterating a `list[StageSpec]`. `flows/tech/pipeline.py` = today's `run_pipeline.py` CLI/arg-parsing, now building `cmd` from `StageSpec.module` instead of hardcoded strings. **The subprocess model, per-stage logging under `.task_agent_runs/`, resumability, and `--skip-preflight` all stay identical.**

Deferred (explicitly out of scope): a real `Stage` ABC with in-process `run(context)->result`. Recorded as a follow-up once the layout lands.

---

## 7. Entrypoint consolidation

- **Create `apps/cli/`** as the single Click group: `python -m apps.cli generate_tasks`, `python -m apps.cli gist …`.
  - `cli/generate.py` → `apps/cli/generate.py` (its `from generators.task import create_task` → `from flows.tech.stages.generate import create_task`).
  - `gist_manager.py` → `apps/cli/gist.py`, registered as a subcommand.
- **Delete** `multiagent.py` and top-level `cli/` (no shims).
- Deploy/reset stay as `python -m infra.e2b …` (already correctly placed).
- The pipeline's stage-04 subprocess target changes from `python multiagent.py generate_tasks` to `python -m flows.tech.stages.generate` (via the registry).

---

## 8. Backward-compat — caller-update checklist (single swing)

All functional callers are in-repo; docs/plans are historical and left as-is (except `CLAUDE.md`).

| File | Change |
|---|---|
| `task_builder/runner.py` | `from run_pipeline import …` → `from flows.tech.pipeline import …` |
| `task_builder/jobs.py`, `server.py`, `conversation_repo.py` | `generators.task.persistence.init_supabase` → `infra.supabase.init_supabase`; `generators.input_files.generator.init_supabase` → `infra.supabase.init_supabase` |
| `trace_ui/server.py` | `generators.scenarios.repository` → `flows.tech.stages.scenarios.repository`; `generators.prompts.infra_kinds` → `infra.infra_kinds` |
| `flows/pr_review/pr_review_multiagent.py` | `generators.scenarios.build_scenario_key` → `infra.scenario_key.build_scenario_key` |
| `flows/non_tech/non_tech_utils.py` | `task_generation_prompts.Basic.*` → `flows.non_tech.prompt_templates.*` |
| `flows/tech/stages/prompts/*` (was `generators/prompts/*`) | intra-flow imports `generators.prompts.*` → `flows.tech.stages.prompts.*`; `generators.task.runtime_resolver` → `flows.tech.stages.generate.runtime_resolver`; `PROMPT_ROOT` → tech templates dir |
| `flows/tech/stages/{input_files,scenarios,generate}/*` | intra-`generators.*` imports → intra-`flows.tech.stages.*` |
| `tests/*` | update imports (`test_preflight`, `test_stage4_sublogs`, `test_task_builder_runner`, `test_trace_ui`, `test_eval_personas`, `generators/**/tests/*`) |
| `CLAUDE.md` | rewrite module map + commands to the new layout |

---

## 9. Migration phases (tests green after each; `git mv` to preserve history)

Ordered so each phase is independently verifiable. You review before every commit (standing rule). `illuminate_audit` runs before source edits per `CLAUDE.md`.

- **Phase 0 — `_base` extraction.** Create `flows/_base/{stage,registry,runner}.py` by extracting `run_pipeline.py`'s generic logic. `run_pipeline.py` becomes a thin caller reading `TECH_STAGES`. No file moves yet. Verify: full `pytest` + `python run_pipeline.py --dry-run`.
- **Phase 1 — lift shared helpers** (§4) into `infra/`; update the shared importers (`task_builder`, `trace_ui`, `pr_review`). Verify: `pytest`.
- **Phase 2 — preflight** → `flows/tech/stages/preflight.py`; update its importers (`run_pipeline`/registry, `task_builder/runner`, `generators/prompts/retriever`, tests).
- **Phase 3 — move the four generators** → `flows/tech/stages/{input_files,scenarios,prompts,generate}`; update intra-flow imports + registry module paths.
- **Phase 4 — prompt templates** split → `flows/tech/prompt_templates/` and `flows/non_tech/prompt_templates/`; update `PROMPT_ROOT` + non_tech imports.
- **Phase 5 — pipeline** `run_pipeline.py` → `flows/tech/pipeline.py` + `__main__.py`; fix `task_builder/runner` import.
- **Phase 6 — entrypoints** → `apps/cli/` (generate + gist); delete `multiagent.py`, top-level `cli/`.
- **Phase 7 — docs** update `CLAUDE.md`; add `docs/ARCHITECTURE.md` describing the flow/symmetry contract; reserve `flows/design_review/README.md`.

Each phase ends with: `pytest` + a pipeline `--dry-run` smoke + an import-smoke over new module paths + commit.

---

## 10. Testing strategy

Behavior is preserved, so the **existing suite is the safety net.** Per phase:
1. `pytest` (full) — must stay green.
2. Import-smoke: `python -c "import flows.tech.pipeline, flows.tech.stages.preflight, apps.cli"` etc. for the phase's new paths.
3. Pipeline `--dry-run` (no LLM/network) to confirm the runner wires stages correctly.
4. One real end-to-end `--dry-run`-free run is **not** required per phase (cost); do a single live smoke after Phase 6.

New tiny tests to add: `tests/test_flows_base.py` (registry order + StageSpec→cmd construction), and an import-smoke test asserting no `flows.*` module imports a sibling flow.

---

## 11. Out of scope / YAGNI

- **No** in-process Stage ABC / execution rewrite (deferred follow-up).
- **No** renaming of `pr_review`/`non_tech` internal files (e.g. `pr_review_multiagent.py` → `multiagent.py`) — churn without value; import updates only.
- **No** recreation of `design_review` code (removed) — folder + README stub only.
- **No** changes to `infra/`, `task_validation/`, `task_quality/`, `task_input_parser/`, `task_builder/` internals beyond the import updates in §8.
- Dated `docs/plans/*` references to old paths are historical and left untouched.

---

## 12. Risks

- **Import fan-out:** ~15 functional import sites + intra-generators imports. Mitigated by phased `git mv` + `pytest` after each phase.
- **`PROMPT_ROOT` path constants** are computed from `__file__` depth; moving the packages changes the relative depth — must be recomputed, not just re-pathed.
- **Dynamic prompt loading** in non_tech (`get_task_prompt_by_technology_stack`) may resolve templates by name at runtime; the Phase 4 audit must capture the full non_tech template set, not just the two static imports.
- **`task_builder` is a deployed service** (Dockerfile) importing the pipeline in-process — its import updates (§8) must land in the same swing or it breaks on deploy.
