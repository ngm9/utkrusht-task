# Architecture — Symmetric `flows/`

_Last updated: 2026-07-07 (flows-restructure). This is the authoritative map of
the code layout; `CLAUDE.md` may lag._

## Layering (dependencies point downward only)

```
apps/            entrypoints (thin) — python -m apps.cli
  └─ depends on ▼
flows/           one package per assessment "flow"; the work lives here
  └─ depends on ▼
infra/  +  task_generation_prompts/   shared libraries + shared reference data
```

- **`apps/`** aggregates flow entrypoints into user-facing CLIs. Thin.
- **`flows/`** holds the flows. Each flow may import only from `flows/_base`,
  `infra/`, `task_generation_prompts/`, and its own subpackages — **never a
  sibling flow.** Enforced by `tests/test_flow_import_hygiene.py`.
- **`infra/`** is the shared bottom layer (Supabase client, GitHub utils, evals,
  tracing, e2b, classifier, pricing, `infra_kinds`, `utils`). Imports nothing
  from `flows/` or `apps/`.
- **`task_generation_prompts/`** is a shared reference-data package (curated
  prompt templates by level). Consumed by `infra/utils.py`, the tech flow (by
  filesystem path), and `non_tech` (by import). It is shared *data*, not flow
  logic, so it stays top-level — see the spec §5 correction for why it is not
  owned by `flows/tech`.

## The flow contract

Every flow under `flows/` is a package with this shape:

```
flows/<name>/
  __main__.py          # `python -m flows.<name>` — run the flow
  stages/              # (for multi-stage flows) one subpackage per stage,
                       #   each with its own __main__ so the runner can shell to it
  ...                  # flow-specific modules, prompts, evals
```

- `flows/tech/` — the main task-generation pipeline (preflight → input_files →
  scenarios → prompts → generate). `pipeline.py` orchestrates; `stages/*` are the
  stages; `python -m flows.tech` runs it.
- `flows/pr_review/`, `flows/non_tech/` — the secondary flows (own prompts,
  evals, `__main__`).
- `flows/design_review/` — reserved (code removed); see its README.

## `flows/_base` — shared pipeline machinery

- `stage.py` — `StageSpec(name, module, traced, exit0_on_reject, live_markers)`,
  the static description of one stage.
- `registry.py` — `TECH_STAGES`: the ordered list of `StageSpec`. **The `module`
  field is the single source of truth** for each stage's `python -m` target.
- `runner.py` — `run_stage` / `run_stage_streaming` / `pick_python` /
  `write_summary`: the subprocess runner (per-stage stdout/stderr/timing under
  `.task_agent_runs/`, live stderr sub-log splitting, stop-on-first-failure). A
  stage runs as its own subprocess — process isolation, per-stage logs, and
  resumability are preserved from the original `run_pipeline.py`.

## How to run

```bash
# Full tech pipeline (preflight -> ... -> generate)
python -m flows.tech --name "Python, SQL" --proficiency BASIC --count 3

# One task-creation run (stage 4 directly / human entry)
python -m apps.cli generate_tasks -c comp.json -b bg.json -s scenarios.json --env dev
python -m flows.tech.stages.generate -c comp.json -b bg.json -s scenarios.json --env dev  # same command

# Gist lifecycle
python -m apps.cli gist sync-prod-to-dev
python -m apps.cli gist create --task-ids <ID> --env dev

# Secondary flows
python -m flows.pr_review ...
python -m flows.non_tech ...

# Deploy / reset (unchanged — lives in infra)
python -m infra.e2b deploy-task --task-id <UUID> --env dev
```

## Adding a new flow

1. Create `flows/<name>/` with `__main__.py` (+ `stages/` if multi-stage).
2. Import only from `flows/_base`, `infra/`, `task_generation_prompts/`, and your
   own subpackages. Put anything another flow would need into `infra/`.
3. If it is a staged pipeline, add a `<NAME>_STAGES` list to
   `flows/_base/registry.py` and drive the runner from it.
4. Surface a human entrypoint in `apps/cli` if needed.
5. `tests/test_flow_import_hygiene.py` will fail if you import a sibling flow.

## History

This layout was produced by the 2026-07-07 flows-restructure
(`docs/superpowers/specs/2026-07-07-flows-restructure-design.md` +
`docs/superpowers/plans/2026-07-07-flows-restructure.md`), which moved the
scattered tech pipeline + `preflight` into `flows/tech/`, collapsed
`multiagent.py` + `cli/` into `apps/cli`, and reconciled duplicated helpers
(`init_supabase`, `build_scenario_key`, `infra_kinds`) into `infra/`.
