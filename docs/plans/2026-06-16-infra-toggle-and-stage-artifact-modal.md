# Plan — (A) Infra toggle for agent competencies, (B) Per-stage artifact modal

**Status:** PLAN (awaiting approval). No implementation code written yet.
**Date:** 2026-06-16 · **Repo:** utkrusht-task

Two trace_ui/pipeline features. (A) designed 2026-06-15 (toggle + infra-kind picker, "plan first").
(B) is new: the per-stage modal should show the GENERATED ARTIFACTS for each stage, rendered.

---

# PART A — Infra toggle (force infra tasks for agent competencies)

## Goal
Deliberately produce an `infra` task for an agent competency the shape classifier would call
`non_infra` (the 4 real dev ones: Production Agent Engineering, Multi-Agent Systems, Context
Engineering, Tool Use for Agents), choosing which self-hosted service backs it. Default stays
`auto` (classifier decides) -> non-breaking.

> Code frozenset AGENT_COMPETENCY_NAMES lists 6 but only 4 exist in dev DB
> (Multi-Modal Agent Engineering, AI Evaluation are dangling) — reconcile separately.

## Core principle — two coordinated levers
Flipping task_shape="infra" alone is shallow (contrived docker-compose on a mockable task). Do BOTH:
1. STEER scenarios (stage 02): ground every scenario in a self-hosted <service> the agent boots/uses
   as the system under test.
2. FORCE shape (stage 03): bypass classify_task_shape -> infra (determinism; with infra scenarios the
   classifier would agree anyway).

## Single source of truth — generators/prompts/infra_kinds.py (new)
Registry slug -> {label, service, directive} for: auto, vector-db (Qdrant/pgvector), redis, kafka,
postgres, mcp-server. UI reads {slug,label}; scenario step reads directive; prompt step reads service.
Helpers list_kinds() + resolve(slug). Add a kind = one edit here.

## Data flow
modal (task_shape, infra_kind) -> POST /api/runs -> RunRequest -> run_pipeline --task-shape infra
  --infra-kind <slug>
   - stage 02 scenarios: append INFRA_KINDS[kind].directive to --focus-areas
   - stage 03 prompt: agent.forward(task_shape_override="infra", infra_kind=...)
        - skip classify_task_shape -> task_shape="infra" (logged)
        - thread INFRA_KINDS[kind].service into the generate signature

## Files to change
1. generators/prompts/infra_kinds.py (new) — registry + list_kinds()/resolve().
2. run_pipeline.py — --task-shape {auto,infra,non_infra} (default auto) + --infra-kind; when infra,
   inject the kind directive into stage-02 --focus-areas and pass flags to stage 03.
3. generators/prompts/__main__.py — accept --task-shape/--infra-kind; pass into the agent.
4. generators/prompts/agent.py forward() (classifier call ~761) — task_shape_override + infra_kind;
   short-circuit classifier when set (log "forced by override"); feed service into the generate
   signature (the task_shape=="infra" branch already emits docker-compose/kill.sh).
5. trace_ui/server.py — RunRequest gains task_shape="auto" + infra_kind="auto" (allowlist -> 400);
   api_launch appends flags; new GET /api/infra-kinds.
6. trace_ui/static/index.html — New-run modal: "Task shape: Auto/Infra/Non-infra" + (when Infra) an
   "Infra service" select from /api/infra-kinds; send both in the launch POST.

## Tests
Registry validity + resolve() fallback; run_pipeline flag threading; agent.forward override skips
classifier (spy); RunRequest validation + cmd build + /api/infra-kinds.

## Backward compat
Default task_shape="auto" everywhere -> identical to today until the toggle is used.

---

# PART B — Per-stage ARTIFACT modal (view generated files, rendered)

## Goal
The ⤢ stage modal currently shows log lines. Add an ARTIFACTS view so clicking a stage's ⤢ shows the
files that stage GENERATED, rendered:

| Stage | Artifact(s) | Render as |
|---|---|---|
| Input files (01) | data/generated/input_files/input_<combo>/<level>/.../competency_*.json + background_forQuestions_*.json | pretty JSON / field cards (scope, role_context, questions_prompt) |
| Scenarios (02) | the generated scenarios for this combo+level | scenario CARDS — Current Implementation / Your Task / Success Criteria |
| Prompt (03) | data/generated/agent_prompts/<Level>/<combo>_prompt/<combo>_prompt.py | code view (monospace + light highlight) |
| Task gen (04) | data/generated/task_artifacts/<task_id>/task.json + code_files/ (README.md, source) | task summary + markdown README + per-file code |

Stages without artifacts (preflight, eval, gate, quality, solution) keep the log view only.

## How the trace_ui finds the artifacts (run -> data/generated)
Artifacts are keyed by competency/combo+level, NOT run-id. Parse the run's stage logs for the exact
paths:
- 01 input files: prefer the __INPUT_FILES_RESOLVED__ {competency, background} marker (added 9568641);
  fall back to the human lines "Output directory:" + "Competency file:" + "Background file:".
- 03 prompt: parse "Output path:" / "Wrote: <..._prompt.py>" from 03_prompt.stdout.
- 02 scenarios: query Supabase generated_scenarios by combo_key + proficiency (server already has
  creds via _supabase_creds); combo+proficiency from summary.json/manifest.json. Also surface the
  LOCKED scenario parsed from 04_tasks.stderr ("Locked scenarios: [...]").
- 04 task gen: task_id from manifest.json -> data/generated/task_artifacts/<task_id>/{task.json, code_files...}.

## Server — new endpoint
GET /api/runs/{run_id}/artifacts/{canon} -> {canon, artifacts:[{kind,title,...}]}, kind in
json|scenarios|code|markdown. PATH SAFETY: every resolved path confirmed inside
REPO_ROOT/data/generated (or the materialized run dir) before reading — reject otherwise (no
traversal). Missing files omitted softly, never 500.

## Frontend — modal gets an Artifacts <-> Logs switch
Segmented control at the modal top (default Artifacts where present, else Logs). Renderers by kind:
- json -> collapsible pretty tree / field cards (competency name/proficiency/scope; background
  role_context + questions_prompt).
- scenarios -> one card per scenario split into Current Implementation / Your Task / Success Criteria.
- code -> monospace + line numbers + copy-raw.
- markdown -> rendered markdown + raw toggle.
Reuse the existing modal shell + overlay/Esc close + styling.

## Caveat — S3 / teammate runs
data/generated is NOT uploaded to S3 (only logs + JSONL traces are). So Artifacts view works fully for
LOCAL runs. For S3-materialized runs: scenarios still render (DB-sourced); input/prompt/task show a
"generated locally — not archived" note. Optional later: upload artifacts to the S3 run prefix
(.../run=<ts>/artifacts/) + materialize them in trace_ui/s3_store.py. v1 = local runs.

## Files to change (Part B)
1. trace_ui/server.py — GET /api/runs/{id}/artifacts/{canon} (parse stdout for paths, read+shape,
   query generated_scenarios, path-guard).
2. trace_ui/static/index.html — Artifacts<->Logs switch + 4 renderers (json/scenarios/code/markdown).
3. (optional) infra/tracing/s3.py + run_pipeline.py + trace_ui/s3_store.py — S3 artifact upload +
   materialize for a portable view.

## Tests (Part B)
Path extraction from sample 01/03 stdout (marker + human-line fallbacks); traversal guard; endpoint
returns right kinds with a fixture run + tmp data/generated; scenario string -> {current,task,success}.

## Open questions
- Scenario source: DB (full pool, portable) vs run's locked scenario only. Rec: show both — locked
  highlighted + full pool below.
- Surface answer/solution files under the Solution stage too? (easy once task_artifacts reading exists)

## Rollout order
1. Part B server endpoint + artifact path-resolution (curl-testable on a local run).
2. Part B modal renderers (the visible win).
3. Part A engine (flags + agent override) -> Part A UI toggle.
4. (optional) S3 artifact upload.
