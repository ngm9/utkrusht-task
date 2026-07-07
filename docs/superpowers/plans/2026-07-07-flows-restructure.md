# Flows Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, recommended for this repo per project convention) or superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the repo into a symmetric `flows/` architecture (every flow a sibling package with an identical shape), moving the scattered tech pipeline + preflight into `flows/tech/`, collapsing the `multiagent.py`/`cli/`/`apps/` tangle into one `apps/cli`, and reconciling duplicated shared helpers into `infra/` — **without changing any runtime behavior.**

**Architecture:** Behavior-preserving reorganization. The subprocess-per-stage runner, per-stage logging under `.task_agent_runs/`, tracing, and resumability are all preserved — only module addresses change. A lightweight `flows/_base` (StageSpec + registry + extracted runner) provides the shared stage machinery; `flows/tech` becomes the tech flow, symmetric with `flows/pr_review` and `flows/non_tech`. No in-process Stage-ABC rewrite (deferred).

**Tech Stack:** Python 3.14, Click (CLI), argparse (pipeline + preflight + gist), pytest, Supabase client, dotenv, git (`git mv` to preserve history).

**Spec:** `docs/superpowers/specs/2026-07-07-flows-restructure-design.md`

## Global Constraints

- **Behavior-preserving:** the full existing `pytest` suite must stay green after every task. Tests are the safety net; do not modify test *assertions* to make them pass — only update *import paths*.
- **`git mv` for every move** — preserve file history.
- **No legacy shims** — update all in-repo callers in the same task (clean break, per project preference).
- **No flow imports a sibling flow** — `flows/<x>` may import only from `flows/_base` and `infra/` (and its own subpackages). Enforced by a guard test.
- **`illuminate_audit` MCP tool must be invoked before the first source edit of each task** (per `CLAUDE.md`); surface its response.
- **User reviews before every commit** (standing rule): each task ends with tests-green → STOP for review → commit on approval. Do not push.
- **Branch:** perform this work on a dedicated branch off `main` (e.g. `refactor/symmetric-flows`), not the current `research/…` branch.
- **PEP 8 + type annotations** on all new code (`flows/_base/*`, `apps/cli/*`, guard tests). `black`/`isort`/`ruff` clean.

---

### Task 0: `flows/_base` extraction + guard tests (no file moves yet)

Extract the generic runner machinery out of `run_pipeline.py` into `flows/_base/`, and add the two new guard tests. `run_pipeline.py` stays in place but imports from `flows/_base`. Proves the extraction is behavior-neutral before anything moves.

**Files:**
- Create: `flows/__init__.py` (already exists — confirm), `flows/_base/__init__.py`, `flows/_base/stage.py`, `flows/_base/runner.py`, `flows/_base/registry.py`
- Modify: `run_pipeline.py` (import runner helpers + registry instead of local defs)
- Test: `tests/test_flows_base.py` (new), `tests/test_flow_import_hygiene.py` (new)

**Interfaces:**
- Produces `flows._base.stage.StageSpec(name: str, module: str, traced: bool = False, exit0_on_reject: bool = False, live_markers: tuple[tuple[str, tuple[str, ...]], ...] = ())`
- Produces `flows._base.registry.TECH_STAGES: list[StageSpec]`
- Produces `flows._base.runner.pick_python() -> str`, `run_stage(combo_dir, label, cmd, live_split=None) -> dict`, `write_summary(combo_dir, names, level, stages, status, task_outcome="") -> None`, and the marker constants `E2B_GATE_MARKERS`, `EVAL_MARKERS`.

- [ ] **Step 1: Create `flows/_base/stage.py`**

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageSpec:
    """Static description of one pipeline stage.

    The dynamic argv (competency names, resolved paths, env) is built per-run by
    the flow's pipeline module; this spec captures only the invariant parts so
    the module addresses and streaming/tracing flags live in one manifest
    instead of being hardcoded inline.
    """
    name: str                                   # log label prefix, e.g. "00_preflight"
    module: str                                 # `python -m <module>` target
    traced: bool = False                        # sets PIPELINE_TRACING_ENABLED for this stage
    exit0_on_reject: bool = False               # stage exits 0 even on eval-gate reject
    live_markers: tuple[tuple[str, tuple[str, ...]], ...] = field(default_factory=tuple)
```

- [ ] **Step 2: Create `flows/_base/runner.py`** — move `_pick_python`, `_run_stage`, `_run_stage_streaming`, `_write_summary`, `_E2B_GATE_MARKERS`, `_EVAL_MARKERS` from `run_pipeline.py` **verbatim** (rename the four `_`-prefixed publics to `pick_python`/`run_stage`/`run_stage_streaming`/`write_summary`; keep the marker constants as `E2B_GATE_MARKERS`/`EVAL_MARKERS`). Replace the hardcoded `REPO_ROOT`/`RUNS_DIR` references with a `repo_root: Path` parameter threaded from the caller, OR keep `REPO_ROOT = Path(__file__).resolve().parents[2]` (repo root is two levels up from `flows/_base/`). Use the `parents[2]` form — simplest, behavior-identical.

  The `_traced` substring logic in `run_stage` (`_traced = ("input_files","scenarios","prompt","tasks")`) is replaced by an explicit `traced: bool` parameter on `run_stage` supplied from the StageSpec. Preserve the exact env keys (`SANDBOX_EVAL_ENABLED` setdefault, `PYTHONUNBUFFERED=1`, `PIPELINE_TRACING_ENABLED`).

- [ ] **Step 3: Create `flows/_base/registry.py`**

```python
from __future__ import annotations

from flows._base.runner import E2B_GATE_MARKERS, EVAL_MARKERS
from flows._base.stage import StageSpec

# Order IS the pipeline order. Module paths are the ONLY source of truth for
# `python -m <module>` targets — do not hardcode them in pipeline.py.
TECH_STAGES: list[StageSpec] = [
    StageSpec("00_preflight",   "flows.tech.stages.preflight"),
    StageSpec("01_input_files", "flows.tech.stages.input_files", traced=True),
    StageSpec("02_scenarios",   "flows.tech.stages.scenarios",   traced=True),
    StageSpec("03_prompt",      "flows.tech.stages.prompts",     traced=True),
    StageSpec("04_tasks",       "flows.tech.stages.generate",    traced=True,
              exit0_on_reject=True,
              live_markers=(("04_tasks.e2b_gate.log", E2B_GATE_MARKERS),
                            ("04_tasks.evals.log", EVAL_MARKERS))),
]
```

> NOTE: In Task 0 the `module` strings still point at the *future* locations. `run_pipeline.py` does NOT yet read `module` for its `-m` targets in Task 0 (the modules haven't moved). Task 0 only wires the **runner helpers**; the registry's `module` field is consumed starting in Task 5 when `pipeline.py` is built. Keep `TECH_STAGES` defined now so the guard test can assert its order.

- [ ] **Step 4: Modify `run_pipeline.py`** — delete the moved helper defs; add `from flows._base.runner import pick_python, run_stage, write_summary, E2B_GATE_MARKERS, EVAL_MARKERS`. Update call sites (`_pick_python()`→`pick_python()`, `_run_stage(...)`→`run_stage(...)` now passing the stage's `traced` bool, `_write_summary`→`write_summary`). Everything else (main, arg parsing, `_locate_input_files`, `_parse_resolved_inputs`, `_summarise_task_stage`, `_split_stage4_logs`, `scenarios_file_for`, `_combo_slug`) stays in `run_pipeline.py` for now.

- [ ] **Step 5: Write guard test `tests/test_flows_base.py`**

```python
from flows._base.registry import TECH_STAGES
from flows._base.stage import StageSpec


def test_tech_stage_order():
    names = [s.name for s in TECH_STAGES]
    assert names == ["00_preflight", "01_input_files", "02_scenarios",
                     "03_prompt", "04_tasks"]


def test_only_stage4_exits_zero_on_reject():
    exits = {s.name: s.exit0_on_reject for s in TECH_STAGES}
    assert exits["04_tasks"] is True
    assert all(v is False for k, v in exits.items() if k != "04_tasks")


def test_stagespec_is_frozen():
    spec = StageSpec("x", "m")
    try:
        spec.name = "y"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("StageSpec must be frozen")
```

- [ ] **Step 6: Write guard test `tests/test_flow_import_hygiene.py`** — asserts no `flows.<x>` module source imports a *sibling* flow.

```python
import pathlib
import re

FLOWS = pathlib.Path(__file__).resolve().parents[1] / "flows"
SIBLINGS = {"tech", "pr_review", "non_tech", "design_review"}


def test_no_flow_imports_a_sibling_flow():
    offenders = []
    for py in FLOWS.rglob("*.py"):
        parts = py.relative_to(FLOWS).parts
        if not parts or parts[0] not in SIBLINGS:
            continue
        own = parts[0]
        src = py.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?:from|import)\s+flows\.([a-z_]+)", src):
            other = m.group(1)
            if other in SIBLINGS and other != own:
                offenders.append(f"{py}: imports flows.{other}")
    assert not offenders, "\n".join(offenders)
```

- [ ] **Step 7: Run the suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS (same count as before + 4 new tests). Also `Run: .venv/bin/python run_pipeline.py --help` · Expected: help prints, no import error.

- [ ] **Step 8: `illuminate_audit` was invoked before Steps 1–6; STOP for user review, then commit**

```bash
git add flows/_base tests/test_flows_base.py tests/test_flow_import_hygiene.py run_pipeline.py
git commit -m "refactor: extract flows/_base runner + stage registry from run_pipeline"
```

---

### Task 1: Reconcile duplicated shared helpers into `infra/`

Three flows/apps reach into `generators/` for helpers that are **duplicated**. Reconcile to one home in `infra/` so the Task 3 move can't break them.

**Files:**
- Modify/create: `infra/supabase.py` (new — canonical `init_supabase`), `infra/utils.py` (already has `build_scenario_key` — make canonical), `infra/infra_kinds.py` (new — move `resolve` + the infra-kind table)
- Modify importers: `generators/task/persistence.py`, `generators/input_files/generator.py`, `gist_manager.py`, `generators/scenarios/generator.py`, `generators/prompts/infra_kinds.py`, `flows/pr_review/pr_review_multiagent.py`, `trace_ui/server.py`, `task_builder/{jobs,server,conversation_repo}.py`, `run_pipeline.py`
- Test: existing suite

**Interfaces:**
- Produces `infra.supabase.init_supabase(env: str = "dev") -> Client`
- Canonical `infra.utils.build_scenario_key(competencies: list[dict]) -> str`
- Produces `infra.infra_kinds.resolve(slug: str | None) -> dict` (+ the kinds table)

- [ ] **Step 1: `init_supabase` → `infra/supabase.py`.** Create `infra/supabase.py` with the single canonical `init_supabase` (copy from `generators/task/persistence.py:39`; confirm the three copies are byte-identical in behavior — env var names, client construction). Replace the three definitions with `from infra.supabase import init_supabase` re-exports (keep the name importable at the old paths so intra-generators callers still work until Task 3).

- [ ] **Step 2: `build_scenario_key` → canonical in `infra/utils.py`.** `infra/utils.py` already defines it. Make `generators/scenarios/generator.py:148` import from `infra.utils` (delete the local dup, re-export via `generators/scenarios/__init__.py` so `from generators.scenarios import build_scenario_key` still resolves for pr_review until Task 3). Verify the two implementations were equivalent before deleting; if they differ, keep the `infra/utils.py` one and note the diff in the commit body.

- [ ] **Step 3: `infra_kinds.resolve` → `infra/infra_kinds.py`.** `git mv generators/prompts/infra_kinds.py infra/infra_kinds.py`. Update the two intra-generators importers (`generators/prompts/agent.py:907`, `run_pipeline.py:487`) and the external `trace_ui/server.py:542,562` to `from infra.infra_kinds import resolve` / `import infra.infra_kinds`. Leave a thin `generators/prompts/infra_kinds.py`? No — clean break: update all importers now (they're enumerated).

- [ ] **Step 4: Point external consumers at `infra/`** — `task_builder/{jobs,server,conversation_repo}.py`: `from infra.supabase import init_supabase`. `flows/pr_review/pr_review_multiagent.py:350`: `from infra.utils import build_scenario_key`.

- [ ] **Step 5: Run suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS. Import-smoke: `Run: .venv/bin/python -c "from infra.supabase import init_supabase; from infra.utils import build_scenario_key; from infra.infra_kinds import resolve"` · Expected: no error.

- [ ] **Step 6: `illuminate_audit` before edits; STOP for review; commit**

```bash
git add -A
git commit -m "refactor: reconcile init_supabase/build_scenario_key/infra_kinds into infra/"
```

---

### Task 2: Move preflight into the tech flow

**Files:**
- Move: `git mv task_agent_preflight.py flows/tech/stages/preflight.py` (create `flows/tech/__init__.py`, `flows/tech/stages/__init__.py` first)
- Modify importers: `run_pipeline.py:424` (stage-0 cmd → `-m flows.tech.stages.preflight`), `generators/prompts/retriever.py`, `task_builder/{runner,jobs,server}.py`, `trace_ui/server.py`
- Test: `tests/test_preflight.py` (update import), plus any preflight import in `tests/`

- [ ] **Step 1: Create packages** — `flows/tech/__init__.py` and `flows/tech/stages/__init__.py` (empty).
- [ ] **Step 2: `git mv task_agent_preflight.py flows/tech/stages/preflight.py`.**
- [ ] **Step 3: Fix internal path refs in `preflight.py`** — if it computes `REPO_ROOT` from `__file__` (was repo root, now 3 levels up), recompute: `Path(__file__).resolve().parents[3]`. Grep the moved file for `__file__` / `Path(__file__)` and adjust depth.
- [ ] **Step 4: Update every importer** — `grep -rn "task_agent_preflight\|import preflight\|from preflight" --include=*.py .` and rewrite each to `flows.tech.stages.preflight`. Update `run_pipeline.py` stage-0 to `[py, "-m", "flows.tech.stages.preflight", "--combo", combo_arg, "--env", args.env]` (was a script-path invocation — now `-m`; preflight has a `__main__` guard so this works).
- [ ] **Step 5: Run suite** — `Run: .venv/bin/python -m pytest -q tests/test_preflight.py` then full `-q` · Expected: PASS. `Run: .venv/bin/python -m flows.tech.stages.preflight --help` · Expected: preflight help.
- [ ] **Step 6: `illuminate_audit`; STOP for review; commit** — `git commit -m "refactor: move preflight into flows/tech/stages"`

---

### Task 3: Move the four generators into `flows/tech/stages/`

The big move. `input_files`, `scenarios`, `prompts`, `task` → `flows/tech/stages/{input_files,scenarios,prompts,generate}` (note `task` → `generate`). Their bundled `tests/` move with them.

**Files:**
- Move (each with `git mv`, dir-at-a-time):
  - `generators/input_files` → `flows/tech/stages/input_files`
  - `generators/scenarios` → `flows/tech/stages/scenarios`
  - `generators/prompts` → `flows/tech/stages/prompts`
  - `generators/task` → `flows/tech/stages/generate`
- Modify: all intra-package imports (`generators.input_files`→`flows.tech.stages.input_files`, `generators.scenarios`→`…scenarios`, `generators.prompts`→`…prompts`, `generators.task`→`flows.tech.stages.generate`); external importers in `task_builder/*`, `trace_ui/server.py`, `flows/pr_review/*`, `run_pipeline.py`, `cli/generate.py`, `tests/*`
- Delete: empty `generators/` package once emptied (keep `generators/__init__.py` deletion for last).

- [ ] **Step 1: `git mv` the four dirs** one at a time (see paths above).
- [ ] **Step 2: Rewrite imports** — mechanical, per package. Use a scripted rewrite then eyeball:
  ```bash
  grep -rl --include=*.py 'generators\.input_files' . | xargs sed -i 's/generators\.input_files/flows.tech.stages.input_files/g'
  grep -rl --include=*.py 'generators\.scenarios'  . | xargs sed -i 's/generators\.scenarios/flows.tech.stages.scenarios/g'
  grep -rl --include=*.py 'generators\.prompts'    . | xargs sed -i 's/generators\.prompts/flows.tech.stages.prompts/g'
  grep -rl --include=*.py 'generators\.task'       . | xargs sed -i 's/generators\.task/flows.tech.stages.generate/g'
  ```
  Then manually review each changed file (esp. `run_pipeline.py` stage cmds, `cli/generate.py`, `trace_ui/server.py`, `task_builder/*`). NOTE the `generators.task`→`flows.tech.stages.generate` rename means `from generators.task import create_task` becomes `from flows.tech.stages.generate import create_task`.
- [ ] **Step 3: Fix `PROMPT_ROOT` depth** in `flows/tech/stages/prompts/{retriever.py,__main__.py}` — was `Path(__file__).parent.parent.parent / "task_generation_prompts"` (from `generators/prompts/`); the depth changes under `flows/tech/stages/prompts/`. Recompute to point at the eventual `flows/tech/prompt_templates/` (Task 4 relocates the templates; for THIS task keep it pointing at repo-root `task_generation_prompts/` so tests pass, then Task 4 repoints).
- [ ] **Step 4: Update `run_pipeline.py` stage cmds** — `-m generators.input_files`→`-m flows.tech.stages.input_files`, etc. (the `sed` above already did this — verify).
- [ ] **Step 5: Delete emptied `generators/`** — after the four dirs are gone, remove `generators/__init__.py` and the now-empty `generators/` dir. Confirm nothing imports `generators` anymore: `grep -rn --include=*.py 'generators' . | grep -v task_generation_prompts` → expect empty.
- [ ] **Step 6: Run suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS (moved `tests/` under the packages still collected via conftest/rootdir; confirm collection count unchanged). Import-smoke: `Run: .venv/bin/python -c "import flows.tech.stages.input_files, flows.tech.stages.scenarios, flows.tech.stages.prompts, flows.tech.stages.generate"` · Expected: no error.
- [ ] **Step 7: `illuminate_audit`; STOP for review; commit** — `git commit -m "refactor: move generators/{input_files,scenarios,prompts,task} into flows/tech/stages"`

---

### Task 4: Split prompt templates per flow

**Files:**
- Move: `git mv task_generation_prompts flows/tech/prompt_templates`, then `git mv` the two non_tech files back out to `flows/non_tech/prompt_templates/Basic/`
- Modify: `flows/tech/stages/prompts/{retriever,__main__}.py` `PROMPT_ROOT`; `flows/non_tech/non_tech_utils.py` imports
- Test: `tests/test_general_reference.py`, `tests/test_generic_agent_reference.py`, `generators`-moved retriever tests, non_tech behavior

- [ ] **Step 1: Audit the non_tech template set** — `grep -rn "task_generation_prompts\|prompt_templates\|get_task_prompt_by_technology_stack" flows/non_tech/` and inspect `get_task_prompt_by_technology_stack` to confirm it resolves ONLY the two known files (`Basic/Prompt_basic.py`, `Basic/ai_evals_for_product_managers_basic_prompt.py`) and not tech templates by slug. Record the exact set. If it dynamically pulls tech templates, STOP and revisit (shared-store fallback per spec §5).
- [ ] **Step 2: `git mv task_generation_prompts flows/tech/prompt_templates`.**
- [ ] **Step 3: Move non_tech's files out** — `mkdir -p flows/non_tech/prompt_templates/Basic` then `git mv flows/tech/prompt_templates/Basic/Prompt_basic.py flows/non_tech/prompt_templates/Basic/` and same for `ai_evals_for_product_managers_basic_prompt.py`. Add `__init__.py` files as needed for the import path.
- [ ] **Step 4: Repoint imports** — `flows/non_tech/non_tech_utils.py:20,25` → `from flows.non_tech.prompt_templates.Basic.Prompt_basic import …` / `…ai_evals_for_product_managers_basic_prompt import …`. In `flows/tech/stages/prompts/{retriever,__main__}.py` set `PROMPT_ROOT = Path(__file__).resolve().parents[N] / "prompt_templates"` (compute N so it lands on `flows/tech/prompt_templates`).
- [ ] **Step 5: Run suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS. Extra: `Run: .venv/bin/python -m flows.tech.stages.prompts --help` and a retriever unit test to confirm PROMPT_ROOT resolves.
- [ ] **Step 6: `illuminate_audit`; STOP for review; commit** — `git commit -m "refactor: split prompt templates into per-flow prompt_templates/"`

---

### Task 5: Move the pipeline orchestrator into the tech flow

**Files:**
- Move: `git mv run_pipeline.py flows/tech/pipeline.py`; create `flows/tech/__main__.py`
- Modify: `flows/tech/pipeline.py` (read `TECH_STAGES` module paths instead of hardcoded strings; stage-4 target → `-m flows.tech.stages.generate`); `task_builder/runner.py:10` import; any doc/test referencing `run_pipeline`
- Test: `tests/test_task_builder_runner.py`, `tests/test_stage4_sublogs.py`, `tests/test_locate_input_files.py`

- [ ] **Step 1: `git mv run_pipeline.py flows/tech/pipeline.py`.** Fix `REPO_ROOT = Path(__file__).parent.parent.parent.resolve()` (now under `flows/tech/`, repo root is 2 up → `parents[2]`).
- [ ] **Step 2: Drive stage cmds from the registry** — in `pipeline.py`, build each stage's `-m` target from `TECH_STAGES[i].module` and pass `traced`/`exit0_on_reject`/`live_markers` from the spec. The dynamic args (names, paths, env, focus areas) stay built inline. Stage-4 target becomes `[py, "-m", "flows.tech.stages.generate", ...]` replacing `[py, "multiagent.py", "generate_tasks", ...]` — **verify `flows/tech/stages/generate` runs as `-m`** (Task 6 adds its `__main__`; if not yet present, temporarily keep `-m apps.cli generate_tasks` and switch in Task 6). Keep arg flags identical (`-c/-b/-s/--env`).
- [ ] **Step 3: Create `flows/tech/__main__.py`**

```python
from flows.tech.pipeline import main
import sys

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Update `task_builder/runner.py:10`** — `from run_pipeline import (…)` → `from flows.tech.pipeline import (…)`. Verify the imported names (`run_pipeline_for_brief`, `StageEvent`, etc.) still exist post-move.
- [ ] **Step 5: Run suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS. `Run: .venv/bin/python -m flows.tech --help` · Expected: pipeline help. `Run: .venv/bin/python -m flows.tech --name Python --proficiency BASIC --skip-preflight --help`-style dry check.
- [ ] **Step 6: `illuminate_audit`; STOP for review; commit** — `git commit -m "refactor: move run_pipeline into flows/tech/pipeline + registry-driven stages"`

---

### Task 6: Consolidate entrypoints into `apps/cli`; delete the tangle

**Files:**
- Create: `apps/cli/__init__.py`, `apps/cli/__main__.py`, `apps/cli/generate.py`, `apps/cli/gist.py`; `flows/tech/stages/generate/__main__.py` (so the stage runs as `-m`)
- Move: `git mv cli/generate.py apps/cli/generate.py` (then adjust); `git mv gist_manager.py apps/cli/gist.py`
- Delete: `multiagent.py`, `cli/` (main.py, __init__.py, __main__.py, generate.py)
- Modify: `apps/__init__.py` (exists); the stage-4 target in `flows/tech/pipeline.py` if it was left on `apps.cli` in Task 5; docs referencing `multiagent.py`/`python -m cli`
- Test: existing CLI-touching tests; new `tests/test_apps_cli.py`

- [ ] **Step 1: Give the generate stage a `__main__`** — create `flows/tech/stages/generate/__main__.py` exposing the Click `generate_tasks` command (moved from `cli/generate.py`), so `python -m flows.tech.stages.generate` works as the stage-4 target. `generate_tasks` imports `create_task` from its own package (`flows.tech.stages.generate.creator` or the package `__init__`).
- [ ] **Step 2: Build `apps/cli`** — `apps/cli/generate.py` = thin re-export of the `generate_tasks` command from `flows.tech.stages.generate`. `apps/cli/__main__.py`:

```python
import click
from dotenv import load_dotenv

load_dotenv()

from flows.tech.stages.generate.__main__ import generate_tasks  # or wherever the command lives
from apps.cli.gist import gist as gist_group

cli = click.Group(help="Utkrusht task tooling (generate + gist; deploy lives in `python -m infra.e2b`).")
cli.add_command(generate_tasks, name="generate_tasks")
cli.add_command(gist_group, name="gist")

if __name__ == "__main__":
    cli()
```

- [ ] **Step 3: Fold gist** — `git mv gist_manager.py apps/cli/gist.py`. Wrap its argparse subcommands as a Click group `gist` (thin: each Click subcommand calls the existing functions `sync_prod_gists_to_dev`, `create_gists_for_tasks`, `create_prod_gists_for_missing`, `sync_is_enabled_to_dev`). Its local `init_supabase` (line 48) → `from infra.supabase import init_supabase`. Keep the argparse `main()` for back-compat callers OR delete if none — grep `gist_manager` usage first.
- [ ] **Step 4: Delete the tangle** — `git rm multiagent.py cli/main.py cli/__init__.py cli/__main__.py cli/generate.py` (after confirming `apps/cli/generate.py` covers it). `grep -rn "multiagent\|from cli\|import cli\|python -m cli" --include=*.py .` → expect empty (excluding docs/plans).
- [ ] **Step 5: Point stage-4 at the stage** — ensure `flows/tech/pipeline.py` stage-4 uses `-m flows.tech.stages.generate` (not `multiagent.py`).
- [ ] **Step 6: New test `tests/test_apps_cli.py`** — assert `python -m apps.cli --help` lists `generate_tasks` and `gist`, and that `python -m flows.tech.stages.generate --help` works.

```python
import subprocess, sys

def _run(mod):
    return subprocess.run([sys.executable, "-m", mod, "--help"],
                          capture_output=True, text=True)

def test_apps_cli_exposes_commands():
    out = _run("apps.cli")
    assert out.returncode == 0
    assert "generate_tasks" in out.stdout and "gist" in out.stdout

def test_generate_stage_runs_as_module():
    assert _run("flows.tech.stages.generate").returncode == 0
```

- [ ] **Step 7: Run suite** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS. Manual: `python -m apps.cli --help`, `python -m apps.cli gist --help`.
- [ ] **Step 8: `illuminate_audit`; STOP for review; commit** — `git commit -m "refactor: consolidate CLI into apps/cli; remove multiagent.py + cli/; fold gist"`

---

### Task 7: Documentation + design_review stub

**Files:**
- Modify: `CLAUDE.md` (module map + commands → new layout)
- Create: `docs/ARCHITECTURE.md` (the flow/symmetry contract), `flows/design_review/README.md` (reserve the name)

- [ ] **Step 1: Rewrite `CLAUDE.md`** — update the Module Responsibilities + Sub-packages tables and the Common Commands block: `python -m flows.tech …` (pipeline), `python -m apps.cli generate_tasks`, `python -m apps.cli gist …`, `python -m infra.e2b deploy-task`. Remove references to `multiagent.py`, `run_pipeline.py`, `cli/`, `generators/`.
- [ ] **Step 2: Write `docs/ARCHITECTURE.md`** — document: the `flows/` symmetry contract (each flow = `__main__` + `stages/` + own `prompt_templates/`; imports only `_base`/`infra`); `flows/_base` StageSpec+registry+runner; the shared-`infra/` rule; how to add a new flow.
- [ ] **Step 3: `flows/design_review/README.md`** — one paragraph: design-review flow code was removed; folder reserved; point at `docs/plans/2026-03-30-design-review-flow.md`.
- [ ] **Step 4: Run suite once more** — `Run: .venv/bin/python -m pytest -q` · Expected: PASS. Final import-hygiene: `tests/test_flow_import_hygiene.py` green.
- [ ] **Step 5: STOP for review; commit** — `git commit -m "docs: document symmetric flows architecture; reserve design_review"`

---

## Self-Review

**Spec coverage:** §3 target tree → Tasks 2–6. §4 shared extraction → Task 1. §5 template split → Task 4. §6 `_base` contract → Task 0. §7 entrypoints → Task 6. §8 caller checklist → distributed across Tasks 1–6 (every listed site has a step). §9 phases → Tasks 0–7 (1:1). §10 testing → per-task "Run suite" gates + `test_flows_base`/`test_flow_import_hygiene`/`test_apps_cli`. §11 YAGNI honored (no Stage-ABC, no pr_review/non_tech internal renames, design_review stub only).

**Placeholder scan:** the one deliberate branch is Task 5 Step 2 / Task 6 (stage-4 target timing) — resolved explicitly: keep `-m apps.cli generate_tasks` transiently if the stage `__main__` isn't in place until Task 6. No TBD/TODO left.

**Type consistency:** `StageSpec` fields (`name/module/traced/exit0_on_reject/live_markers`) used identically in `registry.py`, the guard test, and `pipeline.py` consumption. `init_supabase(env="dev") -> Client`, `build_scenario_key(list[dict]) -> str`, `resolve(str|None) -> dict` consistent across Task 1 and callers.

**Known risk to watch:** pytest **collection count** must be identical before/after Task 3 (moved `tests/` dirs under the packages) and Task 4 — if collection drops, `rootdir`/`conftest`/`__init__.py` wiring needs a fix before proceeding.
