---
name: task-verify
description: Full verification of ONE Utkrushta task by composing existing skills in order — FIRST solve it via the task-solvability skill (auto-picking --local for non-infra tasks or the E2B sandbox flow for infra tasks), THEN audit the task's full Supabase row via the task-audit skill — and emit one combined verdict. Use when you want the complete "is this task shippable?" answer (solvable AND data-clean) in a single run, e.g. before enabling a task or assigning it to candidates.
---

# Task Verify (orchestrator)

A **composition skill** — it contains NO checking logic of its own. It runs two
existing skills in a fixed order and merges their results:

1. **`task-solvability`** — can the task actually be solved? (behavioral check)
2. **`task-audit`** — is the task's Supabase row complete and consistent? (data check)

Solve FIRST, audit SECOND: solvability is the expensive, decisive signal; if the
task can't even be solved, the audit findings are secondary context in the report.
Each sub-skill's own runbook is the source of truth — follow it as written; never
re-implement or inline its steps here. If a sub-skill's instructions change, this
skill picks the changes up automatically.

## Variables

- `TASK_ID` = first token of `$ARGUMENTS` — **required** (ask if absent).
- `ENV` = `dev` default; `prod` only if the user says so.
- Flags after the task id are passed through to `task-solvability`
  (e.g. `--quick`); `--local` is decided automatically in Step 1, don't require
  the user to pass it.

## STEP 1 — Route by infra flag (cheap, no sandbox)

Load the task once to decide the solvability mode:

```bash
.venv/bin/python .claude/skills/task-solvability/scripts/sandbox.py load \
  --task-id "$TASK_ID" --env "$ENV"
```

- `is_shared_infra_required: false` → run task-solvability in **`--local`** mode
  (solve on this machine — deps installed locally, no E2B sandbox).
- `is_shared_infra_required: true` → run task-solvability in its **default
  sandbox** mode (the task needs the template's live services).
- `load` fails (task missing / no starter repo) → **skip Step 2's solve**, but
  STILL run the audit (Step 3) — a broken row is exactly what the audit reports —
  and record the solvability leg as `not_run`.

## STEP 2 — Solve (invoke the task-solvability skill)

Invoke the **`task-solvability`** skill with the mode chosen in Step 1:

> `/task-solvability $TASK_ID --local --quick`   (non-infra)
> `/task-solvability $TASK_ID --quick`           (infra → sandbox flow)

Follow that skill's runbook end to end (preflight → clone/deploy → solve →
grade → teardown). Capture from its output:
`verdict` (`solvable` / `unsolvable` / `unverified` / `invalid`),
`grade_signal`, `iterations`, and the path to its report under
`solvability_runs/<slug>/`. Drop `--quick` only if the user explicitly asked
for a recording.

## STEP 3 — Audit (invoke the task-audit skill)

Invoke the **`task-audit`** skill on the same task:

> `/task-audit $TASK_ID --env $ENV`

Follow that skill's runbook as written (it is read-only). Capture its
per-field findings — including the `is_shared_infra_required ↔ template_id`
consistency result, which cross-checks the routing decision made in Step 1.

## STEP 4 — Combined verdict

Merge the two legs into ONE verdict — a task is only shippable when **both**
legs are clean:

| Solvability | Audit | Combined |
|---|---|---|
| `solvable` | clean | ✅ **PASS** — shippable |
| `solvable` | findings | ⚠️ **PASS_WITH_FINDINGS** — solvable but the row needs fixes (list them) |
| `unsolvable` / `invalid` | any | ❌ **FAIL** — do not ship (audit findings attached as context) |
| `unverified` (no tests) | any | ❌ **FAIL** — not gradeable; a generation defect |
| `not_run` (Step 1 load failed) | findings | ❌ **FAIL** — row too broken to even deploy |

Final report (single message, both legs always shown):

```
=== Task Verify — <task-id> (env <env>) ===
route        is_shared_infra_required=<bool> → <local|sandbox> mode

[1] SOLVABILITY   <verdict>   (<grade_signal>, <n> iterations)
    report: solvability_runs/<slug>/
[2] AUDIT         <clean | N findings>
    <field>: <problem>            (one line per finding)

COMBINED VERDICT: <PASS | PASS_WITH_FINDINGS | FAIL>
NEXT STEPS: <what to fix, or "none — shippable">
```

## Out of scope

- **Batch runs** — one task-id at a time, same as both sub-skills.
- **Fixing anything** — both legs are verify-only; report, don't repair.
- **Re-implementing sub-skill logic** — if either sub-skill can't run
  (missing env keys, etc.), surface ITS error verbatim; don't work around it here.
