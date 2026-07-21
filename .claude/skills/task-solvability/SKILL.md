---
name: task-solvability
description: Check whether ONE Utkrushta task is actually solvable — deploy it to an E2B sandbox, then YOU (the coding agent) solve it with your own tools (RED→fix→GREEN + think-aloud notes + a task-quality assessment), grade against the task's tests where it has them and by running the behaviour where it doesn't, and write a report to solvability_runs/<slug>/. The coding agent is the solver — no headless agent, no metered LLM API. Non-infra tasks (is_shared_infra_required = false) can run in --local mode — clone + install deps + solve + grade entirely on this machine, no E2B sandbox. Use when verifying a generated task can be completed (not just that it deploys — that's the deployment-test skill).
---

# Task Solvability

Answers one question for one task: **can it actually be solved?** It deploys the
task to a real E2B sandbox, then **YOU — the coding agent — solve it** using your
native tools, grade against the task's own test suite, and record the outcome.
`deployment-test` proves a task *deploys*; this proves it's *solvable*.

## How to run it

This is a **Claude Code skill** — a coding agent (me) runs it; there is no pure-bash
one-liner, because the *solving* and *adaptive gate-clicking* need the model. Invoke it:

> **`/task-solvability <task-id>`**  (or: "run the solvability flow on task `<id>`")

| Mode | What runs | Reliable? |
|---|---|---|
| **default** | deploy → I solve it (RED→fix→GREEN + notes) → grade → write report | ✅ |
| **`--local`** | **non-infra tasks only** — clone + install deps + solve + grade entirely on THIS machine; no E2B sandbox | ✅ (see "Local mode" below) |

**Auto-suggest local:** `load` prints `is_shared_infra_required`. If it's `false`,
prefer `--local` — it's faster and free (no sandbox billing). If it's `true`,
`--local` is INVALID (the task needs the template's services) — hard-fail with
that explanation and fall back to the sandbox flow.

## Outputs — `solvability_runs/<task-slug>/` (NOT `.task_agent_runs`)

Each run writes ONE folder at the repo root (gitignored) with **five files**:

- **`result.json`** — the whole report as structured data (schema below). This is the
  **source of truth**; the three `.md` files are human-readable renderings of its
  content, nothing more. Cross-run querying is `glob solvability_runs/*/result.json`.
- **`solution.diff`** — the diff of your edits, verbatim.
- **`summary.md`** — human render of `result.json.summary` (see **Markdown renderings**).
- **`notes.md`** — human render of `result.json.notes`.
- **`tour.md`** — human render of `result.json.tour` (per-step). Write it even when
  `tour_verdict` is `n/a` (a one-line "no tour on this task").

The `.md` files must never disagree with `result.json` — they're generated FROM it, so
fill `result.json` first, then render. No content lives only in a `.md` file.

Additionally, every run **appends one row** to the cross-run log
`solvability_runs/task_audits.csv` (STEP 4e) — same columns as the Supabase
`task_audits` table, with the `detail` column carrying the run's full
`result.json`. The per-run folder stays five files; the CSV is the one shared,
accumulating artifact across runs.

### `result.json` schema

Write every prose field in your OWN words — never paste the README/problem statement in.
**Writing style for the nested prose** (the `summary` / `notes` fields): short sentences,
one idea per sentence, active voice; the `summary` line is a plain-English sentence anyone
can read (no jargon, no file names), and `detail` / `observed` / `verified` carry the
precise technical text. Never pack symptom + cause + fix into one sentence — that's what
the three sub-keys are for.

```jsonc
{
  // ── identity ──
  "task_id": "<id>", "env": "<env>", "template": "<tpl>",
  "sandbox_id": "<id|null>",          // null in --local mode
  "starter_repo": "<url>", "mode": "sandbox",   // or "local"

  // ── overall (the rollup — computed LAST, from the three components below) ──
  "overall": "fail",                  // pass | fail | inconclusive  (see rule under the schema)

  // ── solvability verdict (flat, machine-queryable) ──
  "verdict": "solvable",              // solvable | unsolvable | broken | unverified
  "grade_signal": "inspection",       // tests_passed | tests_failed | inspection | already_solved | env_unavailable
  "baseline": "<what the clean starter's suite did>",
  "iterations": 3, "used_answer": false,

  // ── summary (was summary.md) ──
  "summary": {
    "current_implementation": {
      "overview": "one plain paragraph on what the starter ships",
      "verified_by_running_it": [        // REAL evidence from STEP 3's current-state check —
        "services up, row counts, API codes+bodies, baseline test line"
      ],
      "issues": [                        // one per broken thing
        {"summary": "plain sentence, no jargon",
         "detail": "the technical cause",
         "observed": "the runtime evidence that proves it (actual error/response)"}
      ]
    },
    "objectives": ["what the task asked, restated plainly — one per item"],
    "what_was_solved": [                 // one per fix
      {"summary": "what now works",
       "detail": "file + exact change + why",
       "verified": "the runtime evidence the fix holds"}
    ],
    "verdict_note": "one-line justification for the verdict"
  },

  // ── notes (was notes.md) ──
  "notes": {
    "think_aloud": "free-prose reflection: where it was tricky, judgment calls, whether you consulted the answer repo",
    "task_quality": [                    // task-quality defects/observations, or [] if none
      {"summary": "short defect", "detail": "why it matters / what a candidate hits"}
    ]
  },

  // ── tour (was tour.md; STEP 4b) ──
  "tour": {
    "tour_verdict": "ok",                // ok | defects | n/a
    "counts": {"steps": 7, "pass": 7, "warn": 0, "fail": 0},   // null when n/a
    "steps": [                           // one per tour step walked, in order; [] when n/a
      {"section": "<section title>", "label": "<step label>",
       "type": "command|link|markdown", "result": "pass|warn|fail",
       "note": "why (required for warn/fail; short 'runs clean, output matches' for pass)"}
    ]
  },

  // ── audit (data-integrity, from the task-audit skill; STEP 4c) ──
  "audit": {                             // null if the task-audit skill isn't available
    "verdict": "pass",                   // pass | warn | fail
    "checks": {"pass": 11, "warn": 0, "fail": 0},
    "failures": [{"field": "criterias", "detail": "..."}],   // [] when clean
    "warnings": []
  },

  "ts": "<iso>"
}
```

Do NOT also emit a top-level `evidence` or `quality_defects` array — that runtime
proof now lives in `summary.*.verified` / `verified_by_running_it`, and defects live
in `notes.task_quality`. One home per fact, no duplication.

### The `overall` rollup — one verdict over all three checks

A run has three independent checks — **solvability** (`verdict`), **tour**
(`tour.tour_verdict`), **audit** (`audit.verdict`). `overall` collapses them into one
answer to "is this task fit to assign?" **If ANY one fails, `overall` is `fail`** — a
solvable task with a broken tour is still a failed task. Compute it LAST, after all
three are filled, by this rule (a failure anywhere wins):

| Condition (checked in order) | `overall` |
|---|---|
| `verdict` ∈ {`unsolvable`, `broken`} **OR** `tour_verdict` == `defects` **OR** `audit.verdict` == `fail` | **`fail`** |
| else `verdict` == `unverified` (couldn't grade — env broke) | `inconclusive` |
| else (solvable/solvable-by-inspection, tour ok-or-n/a, audit pass-or-warn) | `pass` |

Notes: a `tour_verdict` of `n/a` (no tour) never counts against `overall`. An audit
`warn` does not fail `overall` on its own, but surface it. If `audit` is `null` (audit
skill absent), ignore it in the rollup.

### Markdown renderings (`summary.md` / `notes.md` / `tour.md`)

Render these FROM the filled `result.json` — same facts, human layout. Keep the
"layered bullet" style: a bold plain-English line, then indented technical detail.

- **`summary.md`** — a `# <title>` H1 and a one-line **Overall: PASS/FAIL/INCONCLUSIVE**
  banner, then `## Current Implementation` (the `overview`, a `### Verified by running it`
  list, and one layered bullet per `issues[]` entry: bold `summary` + `Detail:` +
  `Observed:`), `## Objectives`, `## What Was Solved` (one layered bullet per fix: bold
  `summary` + `Detail:` + `Verified:`), and `## Verdict` (`verdict` + `grade_signal` +
  `verdict_note`).
- **`notes.md`** — `## Think-aloud` (the prose) then `## Task-quality` (one bullet per
  `task_quality[]`: bold `summary` + indented `detail`; "none" if empty).
- **`tour.md`** — a header line with the resolved sandbox/env, then one line per
  `tour.steps[]` entry (`✅ pass` / `⚠️ warn: <note>` / `❌ fail: <note>`, grouped by
  `section`), and a footer with the counts + `tour_verdict`. When `n/a`: a single line
  "No tour on this task (checked both envs)."

## Variables

- `TASK_ID` = first token of `$ARGUMENTS` — **required** (ask if absent).
- `ENV` = `prod` — tasks are picked from **prod ONLY**; use `dev` only if the
  user explicitly asks to verify a dev task.
- `PY` = `.venv/bin/python` — deps live in the venv, not system python.
- `H` = `.claude/skills/task-solvability/scripts/sandbox.py` — the sandbox helper.
- `SLUG` = the repo name (e.g. `cargolink-pickup-context-repair`); outputs go to `solvability_runs/$SLUG/`.

`.env` is auto-loaded by `infra/e2b/__main__.py`; the helper loads it too.

---

## STEP 1 — Preflight (cheap; fail before booting a sandbox)

```bash
cd <repo-root>
.venv/bin/python -c "import e2b; from infra.e2b import sandbox_manager" || echo "FATAL: run from .venv"
for k in E2B_API_KEY GITHUB_UTKRUSHTAPPS_TOKEN SUPABASE_URL_APTITUDETESTS SUPABASE_API_KEY_APTITUDETESTS; do
  grep -q "^$k=" .env || echo "FATAL: missing $k in .env"
done
# (only with an explicit --env dev run, check the ...APTITUDETESTSDEV keys instead)
.venv/bin/python .claude/skills/task-solvability/scripts/sandbox.py load --task-id "$TASK_ID" --env "$ENV"
```

**Hard-fail** if the import errors, a key is missing, or `load` raises (task not
found / no template / no starter repo). `load` prints `is_enabled`, `template_id`,
`starter_repo`, `test_cmd`, and `has_problem` — note them.

- **`is_enabled: false` → STOP (the FIRST gate, in BOTH modes — sandbox and
  `--local`).** Only enabled tasks get verified: do not deploy, clone, or solve —
  report plainly that the task is disabled (`is_enabled = false`) and end the run
  with no verdict. Proceed anyway ONLY if the user explicitly says to verify a
  disabled task.
- `has_problem: false` → **warn**: there's no problem statement to solve from;
  you'll be solving against the tests alone (or it may be unsolvable-by-spec).

---

## STEP 2 — Deploy + clone

```bash
# boot the sandbox (has the real services); ~60–120s
.venv/bin/python $H deploy --task-id "$TASK_ID" --env "$ENV"   # prints {sandbox_id, test_cmd, task_dir, ports}
# local copy for fast native editing
.venv/bin/python $H clone  --task-id "$TASK_ID" --env "$ENV" --dest "$WORK"
```

Capture `SANDBOX` (the `sandbox_id`) and `TEST_CMD` from the deploy JSON. The
starter is cloned to both the sandbox (`/home/user/task`, with services) and
`$WORK` (local, for editing).

---

## STEP 3 — Solve it (YOU are the solver)

This is the point of the skill — solve it like a candidate would:

1. **Read the problem** (the `problem` field from `load`, and `$WORK/README.md`).
2. **Read the code** in `$WORK` with your native tools; understand what's missing.
2b. **Verify the current state by RUNNING it** — never describe the starter from
   reading alone; prove what it actually does. In the sandbox, probe every piece
   of infrastructure the task depends on and record the REAL outputs:
   ```bash
   # what is actually running / listening
   $H run --sandbox "$SANDBOX" --cmd "ps aux | grep -vE 'ps aux|grep' | head -20; (ss -tln || netstat -tln) 2>/dev/null"
   # DB-backed task → is the DB up AND populated? (adapt creds/table names from the starter)
   $H run --sandbox "$SANDBOX" --cmd "psql <DB_URL> -c '\dt' -c 'SELECT count(*) FROM <seeded_table>;' -c 'SELECT * FROM <seeded_table> LIMIT 3;'"
   # API task → does the app build, start, and answer? hit real endpoints, note codes + bodies
   $H run --sandbox "$SANDBOX" --cmd "curl -s -m 5 -w '\n%{http_code}\n' localhost:<port>/<endpoint>"
   # broker/cache/etc. → the equivalent liveness + data check for each service
   ```
   Check EVERYTHING the task claims to provide: services reachable, seed data
   actually populated (row counts, sample rows), endpoints responding, and how
   each suspected defect manifests at runtime (capture the actual error/output).
   These observations are REQUIRED input for
   `summary.current_implementation.verified_by_running_it` in `result.json` —
   findings must be reported from execution evidence, not inferred from source code.
3. **Establish the baseline** — run the suite once on the clean starter:
   ```bash
   .venv/bin/python $H run --sandbox "$SANDBOX" --cmd "$TEST_CMD"
   ```
   Now read the **output**, not just the exit code. **A task is NOT required to
   ship tests, and a missing suite never stops the run** — most tasks are graded
   in production by an LLM judge over the diff, not by pytest, so "no tests" is a
   normal shape, not a defect and not a failure. Classify what you see:

   | Output signal | Meaning | What to do |
   |---|---|---|
   | no tests collected — pytest `no tests ran` / exit **5**; npm `no test specified` or `Missing script: "test"`; go `[no test files]`; cargo `running 0 tests` | **no test oracle** | **Solve it anyway** (continue to step 4). Grade by inspection at STEP 4 → `grade_signal: inspection`. Do NOT stop; do NOT treat pytest/npm's non-zero exit as red-to-fix; do NOT treat go/cargo's exit-0 as "already green." |
   | real assertions failed (non-zero **with** failing test names) | baseline **red** — there's something to solve | continue to step 4 |
   | tests were collected and all passed | **the untouched starter already passes its own suite** — nothing for a candidate to do | verdict `broken` (STEP 4), stop. This is a task defect, not a neutral outcome. |

   ⚠️ **Read collection, not the exit code:** pytest/npm with no tests exit
   **non-zero** (looks red), while go/cargo with no tests exit **zero** (looks
   already-solved). Neither is a real signal — decide on whether tests were
   *collected*, never on the exit code alone.
4. **Implement** the solution by editing files in `$WORK` (Edit/Write).
5. **Sync changed files → sandbox, then run the suite there** (services live there):
   ```bash
   for f in $(git -C "$WORK" diff --name-only); do
     .venv/bin/python $H put --sandbox "$SANDBOX" --local "$WORK/$f" --remote "/home/user/task/$f"
   done
   .venv/bin/python $H run --sandbox "$SANDBOX" --cmd "$TEST_CMD"
   ```
6. **Iterate** 4–5 until the suite is green or you've made a genuine, bounded
   effort (cap ~8 edit→test cycles so a stuck task doesn't run forever).
   **With no test suite**, iterate against the runtime instead: exercise the
   thing you changed (hit the endpoint, run the script, query the DB) and stop
   when the behaviour the problem statement asks for actually holds.

Do NOT edit the task's tests to force a pass — fix the implementation. (Isolation
doesn't matter here, so consulting the answer repo is allowed if you're stuck;
note in the record whether you did.)

---

## STEP 4 — Grade + record

Capture the agent's diff into the report folder (the ONLY diff file — no second copy):

```bash
mkdir -p "solvability_runs/$SLUG"
.venv/bin/python $H diff --sandbox "$SANDBOX" > "solvability_runs/$SLUG/solution.diff"
```

**Verdict rules (be honest — never a hollow green):**

| Situation | `verdict` | `grade_signal` |
|---|---|---|
| Suite went green after your edits | `solvable` | `tests_passed` |
| **No test suite**, but you solved it and verified the behaviour by running it | `solvable` | `inspection` |
| You made a real effort, suite still red | `unsolvable` | `tests_failed` |
| **No test suite**, and you could not make the required behaviour work | `unsolvable` | `inspection` |
| **Nothing to solve** — the untouched starter already satisfies every objective/outcome | `broken` | `already_solved` |

**`broken` — the task itself is defective (a FAILURE, not a neutral skip).**
Emit it when the starter you were handed already does everything the task asks,
so a candidate would have nothing to do. Two ways you'll detect it:

- the task ships tests and they **pass on the clean starter** (before any edit), or
- the task ships no tests but, by inspection, **every stated objective and outcome
  is already implemented and works** when you run the starter.

`broken` is ALWAYS a task-quality failure — it MUST carry a `notes.task_quality`
entry naming the defect (e.g. "starter repo ships the full solution"). Do not soften
it to a neutral outcome; a pre-solved task cannot assess a candidate.

⚠️ **Guard against a false `broken`:** a starter that merely *builds and runs* is not
broken. `broken` requires that EVERY objective/outcome is already met with no gap.
If the starter is complete but the task asks for something **beyond** what's there (an
extension, a new endpoint, a bug the outcomes describe that still reproduces), then
that beyond-part IS the task — solve it and grade normally; it is not `broken`. When
in doubt, check the answer repo: if it's only a *stylistic* rewrite of the starter, the
starter is functionally complete (`broken`); if it adds real behaviour the starter
lacks, that gap is the task.

**A missing test suite is not a verdict of its own** — it only changes
`grade_signal` from `tests_passed`/`tests_failed` to `inspection`. Never emit
`unverified` / `no_tests` for it, and never report it as a failure or a
task-quality defect; production grades most tasks by LLM judge over the diff, so
shipping no tests is a normal task shape.

When grading by `inspection`, the bar is **runtime evidence, not your opinion**:
say what you ran and what it returned (endpoint responses, DB state, script
output) showing the behaviour the problem statement asked for now holds. Do not
write tests to grade yourself with — an agent inventing its own oracle will just
fabricate a pass. If you cannot demonstrate the behaviour by running something,
that's `unsolvable` / `inspection`, not a green.

Reserve `unverified` for the case where the environment stopped you from
grading at all (toolchain missing, sandbox broken) — `grade_signal: env_unavailable`.

Now write `solvability_runs/$SLUG/result.json` in the schema from **Outputs** above —
the identity + verdict fields plus the `summary` and `notes` objects. (The `tour` block
is filled in by STEP 4b; if the row has no tour, set it to
`{"tour_verdict":"n/a","counts":null,"steps":[]}`. The `audit` block is STEP 4c; the
`overall` rollup is computed in STEP 4d once all three are in.) Get `ts` from
`date -u +%Y-%m-%dT%H:%M:%SZ` — the helper has no clock.

Then render **`summary.md`** and **`notes.md`** from the `summary` / `notes` objects you
just wrote (per **Markdown renderings** in Outputs). `tour.md` comes in STEP 4b, the
`overall` banner in STEP 4d.

---

## STEP 4b — Verify the task tour (when the row has one)

Many task rows carry a **`tour`** — the candidate-facing guided walkthrough shown
in the product (sections of `markdown` / `link` / `command` steps). If a task ships
one, its steps must actually **work in the deployed environment** — a broken command
or a dead link is a task-quality defect the candidate will hit. Verify it here, while
the sandbox from STEP 2 is **still alive** (do this before STEP 5 teardown).

> Heads-up: the tour is often populated on **prod** but null on **dev** (it's written
> late in the pipeline). `has_tour: false` on your `$ENV` is not a failure — try the
> other env's row before concluding there's no tour. If neither has one → `tour: n/a`,
> skip this step.

**Resolve the tour** (substitutes `{{repo.url}}` + `{{sandbox.*_url}}` from the live
sandbox's ports — the helper does NOT execute anything):

```bash
# infra tasks: pass the live sandbox so sandbox.* URLs resolve
.venv/bin/python $H tour --task-id "$TASK_ID" --env "$ENV" --sandbox "$SANDBOX"
# non-infra / --local: omit --sandbox; sandbox.* stay null (no e2b surfaces)
.venv/bin/python $H tour --task-id "$TASK_ID" --env "$ENV"
```

Then **walk every step in order** and grade it. Run this AFTER the solve (STEP 3) so
that steps promising the solved state hold — reuse the SAME sandbox:

| Step type | How to verify | Pass / warn / fail |
|---|---|---|
| `command` | run it — **in the sandbox** via `$H run --sandbox "$SANDBOX" --cmd "<command>"` (infra), or **locally** in `$WORK` (non-infra). Commands are **stateful + ordered** (`up -d` → `ps` → `init` → …) — run them top-to-bottom, never reordered. | **fail** = the mechanics break (command/tool not found, service unreachable, non-zero for an infra reason). **warn** = it runs but the real output doesn't match the step's promised `expected_output`. **pass** = runs clean and output matches. |
| `link` | `is_sandbox_surface: true` → reachability-check the resolved e2b URL (e.g. `curl -sS -o /dev/null -w '%{http_code}' <url>` — expect it to answer, not hang/refuse). `repo.url` → the private starter repo (auth-gated; a plain 404 from an unauth'd curl is expected — confirm the repo exists via the authed clone you already did in STEP 2). | **fail** = sandbox surface refuses/times out, or the URL still has an unresolved `{{var}}` (see `unresolved_variables`). **pass** = answers. |
| `markdown` | no execution — sanity-read the claim against reality (e.g. "LocalStack on 4566" ⇒ 4566 is in `expected_ports`). | **warn** if the prose asserts something false. |

**The starter-vs-solved rule (important):** some tour commands promise the *solved*
outcome (e.g. `terraform plan` → "0 to destroy"), which won't hold on the unsolved
starter. That's why you verify the tour **after** your STEP 3 solve. If you must judge
a step on the starter, separate **"mechanics work"** (tool present, port up, command
runs) — which must ALWAYS pass — from **"output matches"** — which only holds once the
repo is in the state the step assumes. Never fail a tour step just because a
solved-state output didn't appear on the unsolved starter.

**Record** the tour into `result.json`'s `tour` block: one entry per step in
`tour.steps[]` (`section`, `label`, `type`, `result` = `pass`/`warn`/`fail`, and a
`note` — required for warn/fail), plus `counts` and the overall `tour_verdict`
(`ok` | `defects` | `n/a`). Then render **`tour.md`** from that block (per **Markdown
renderings**). A tour with any `fail` is a **task-quality defect** — the task can be
*solvable* yet ship a *broken tour*; report both verdicts honestly, don't let a green
solve hide a red tour (and it flips `overall` to `fail` in STEP 4d).

---

## STEP 4c — Data-integrity audit (fold in the task-audit verdict)

Solvability + tour answer "does the task *work*"; the **task-audit** skill answers
"is the task's *data* well-formed" (required fields, content rules, GitHub/gist
reachability, the infra ↔ template rule). They're orthogonal — a task can build and
solve cleanly yet have a dangling competency id or a broken gist — so fold that verdict
into the same `result.json`.

If the task-audit skill is present, run it in JSON mode for this one task and drop the
result into the `audit` block:

```bash
.venv/bin/python .claude/skills/task-audit/scripts/task_audit.py \
    --env "$ENV" --task-id "$TASK_ID" --json
```

It prints one object (`verdict`, `checks`, `failures`, `warnings`, `fields`) — copy
`verdict` + `checks` + `failures` + `warnings` into `result.json`'s `audit` block.
If the script isn't there (task-audit not installed alongside this skill), set
`"audit": null` and move on — it's best-effort, not a hard dependency. An audit
`fail` is a **task-quality defect** in the same spirit as a red tour: report it, don't
let a green solve hide it.

---

## STEP 4d — Roll up `overall` (all three checks in one verdict)

Now that solvability (`verdict`), `tour.tour_verdict`, and `audit.verdict` are all
filled, compute the top-level **`overall`** by the rule in **The `overall` rollup**
(Outputs): **`fail` if ANY of the three failed** (`unsolvable`/`broken`, tour
`defects`, or audit `fail`); `inconclusive` if solvability is `unverified` and nothing
outright failed; else `pass`. Write it into `result.json`, and put the matching
**Overall: PASS / FAIL / INCONCLUSIVE** banner at the top of `summary.md`.

The point: a run is only fit-to-assign when *every* check is clean. Do not report a
`pass` overall while a component is red — a solvable task with a broken tour or a failed
audit is an `overall: fail`.

---

## STEP 4e — Append the run to the local `task_audits` CSV

Every completed run (whatever the verdict) is logged as ONE row in a single
local CSV that mirrors the Supabase `task_audits` table column-for-column.
The script creates the CSV with a header if it doesn't exist and appends
otherwise:

```bash
.venv/bin/python .claude/skills/task-solvability/scripts/log_csv.py \
    --result "solvability_runs/$SLUG/result.json"
# optional: --duration-s <seconds> --cost-usd <usd> --solved-by <id> --csv <path>
```

Columns (same as the table): `audit_id` (fresh UUID), `task_id`, `verdict`
(`PASS` | `PASS_WITH_FINDINGS` | `FAIL` | `INCONCLUSIVE` — solvable+clean,
solvable+findings, unsolvable/broken, unverified respectively), `findings`
(JSON array of "field: problem" strings — audit failures + audit warnings +
tour warn/fail steps + `task_quality` notes), `solvable`, `solved_by`,
`failure_reason` (the `verdict_note` when not a PASS), `trace_url` (the local
run folder), **`detail` — the FULL `result.json`, verbatim compact JSON**,
`content_hash` (sha256 of result.json), `harness`, `cost_usd`, `duration_s`,
`created_at` (the run's `ts`).

Run it AFTER STEP 4d — the row snapshots `result.json`, so `overall`, `tour`
and `audit` must already be filled in. This step applies in **BOTH modes**
(sandbox and `--local`).

---

## STEP 5 — Teardown

```bash
.venv/bin/python $H kill --sandbox "$SANDBOX"
rm -rf "$WORK"
```

Always kill the sandbox (even on failure) — they bill by uptime.

---

## Final Report

```
=== Solvability — task <id> (env <env>) ===
template <tpl>   sandbox <id>

baseline   ❌ red (suite failed on clean starter — good, there's something to solve)
solve      ✅ solvable   — suite green after 3 edit→test cycles
tour       ✅ ok (7/7 steps) — or  ⚠️ defects (5/7; 1 dead link, 1 command fails)  or  n/a
audit      ✅ pass (11/0/0) — or  ✗ fail (2 dangling competency ids)  or  n/a
recorded   solvability_runs/<slug>/  →  result.json + solution.diff + summary.md + notes.md + tour.md

OVERALL: PASS   (solve ✅ · tour ✅ · audit ✅)
 — or —  OVERALL: FAIL   (solve ✅ · tour ❌ defects · audit ✅)   ← any one red ⇒ FAIL
NOTES: <what the task required / where it was tricky / or why it's unsolvable / broken>
```

On `unsolvable`, say plainly what's wrong (the spec is underspecified /
contradictory / needs resources that aren't there).

A `broken` task (nothing to solve) reports as a **failure**, not a neutral skip —
the diff is empty because there was nothing to fix, and the task-quality defect is
the whole point:

```
baseline   ❌ nothing to solve — the untouched starter already satisfies every outcome
solve      ⛔ broken — starter ships the full solution; a candidate has nothing to do
VERDICT: BROKEN (already_solved)   — TASK DEFECT, must be fixed before assigning
```

A task with no test suite reports as a normal solve, with the baseline line
noting there was no oracle — **never** as a red/failed suite:

```
baseline   ⚪ no tests collected (task ships none — graded by inspection, not a failure)
solve      ✅ solvable   — behaviour verified by running it after 3 edit cycles
VERDICT: SOLVABLE (inspection)
```

## Local mode (`--local`) — non-infra tasks, no sandbox

For tasks with `is_shared_infra_required: false` the starter is self-contained
(no shared Postgres/Kafka/etc. from the E2B template), so the whole flow runs on
this machine. Same verdict rules, same report — only the environment differs.
**Local mode still does BOTH checks:** solvability (STEP 3–4) **and** tour
verification (STEP 4b) if the row ships a tour — you produce a `solve` verdict AND
a `tour` verdict, exactly like the sandbox flow, just without an e2b box.

**STEP 1 (preflight)** — same `load` as above, but E2B keys are NOT required;
only the Supabase + GitHub keys. The **`is_enabled` gate applies here exactly as
in the sandbox flow**: `is_enabled: false` → STOP before cloning or installing
anything (unless the user explicitly asks to verify a disabled task). Hard-fail
`--local` if `is_shared_infra_required: true`.

**STEP 2 (clone + install)** — no `deploy`, just:

```bash
.venv/bin/python $H clone --task-id "$TASK_ID" --env "$ENV" --dest "$WORK"
```

Then install dependencies **inside `$WORK`, isolated from this repo's venv**, by stack
(look at the files actually present — the template_id heuristic is a fallback):

| Present in `$WORK` | Install | Test (default) |
|---|---|---|
| `package.json` | `npm ci \|\| npm install` | `npm test` |
| `requirements.txt` / `pyproject.toml` | `python3 -m venv .taskvenv && .taskvenv/bin/pip install -r requirements.txt` (or `.taskvenv/bin/pip install -e .`) | `.taskvenv/bin/python -m pytest -q` |
| `go.mod` | `go mod download` | `go test ./...` |
| `Cargo.toml` | (cargo fetches on build) | `cargo test -- --test-threads=1` |

If the toolchain itself is missing on this machine (no `go`, wrong node major, etc.),
STOP and report `unverified` / `env_unavailable` — do NOT globally install toolchains;
suggest the sandbox flow instead. If install itself fails on the clean starter, that's
a task-quality defect — record it.

**STEP 3 (solve)** — identical to the sandbox STEP 3, except tests run locally with
plain Bash in `$WORK` — no `put`/sync loop, no `$H run`. Step 2b (verify the
current state by RUNNING it) applies here too, with local commands: build the
project, start the app if it has an entrypoint and hit its endpoints with curl,
inspect any bundled fixtures/seed files, and capture how each defect actually
manifests (real error output) — `summary.current_implementation.verified_by_running_it`
is required in local mode as well. Same ~8-cycle cap, same
"never edit the tests" rule, and the **same baseline classification** (STEP 3.3):
if the runner collects 0 tests, solve it anyway and grade by `inspection` — never
a fail, never `unverified` — even though `go test`/`cargo test` exit 0 with no
test files. If the tests unexpectedly need a live service (connection
refused to a DB/broker), the task is mis-flagged as non-infra — record that as a
task-quality defect and rerun via the sandbox flow.

**STEP 4 (grade + record)** — same verdict table, same five output files, and the
same STEP 4e CSV append (`log_csv.py`) once `result.json` is complete. Capture the
diff with
`git -C "$WORK" add -A && git -C "$WORK" diff --cached > solvability_runs/$SLUG/solution.diff`,
write `solvability_runs/$SLUG/result.json` with `"mode":"local"` and
`"sandbox_id":null`, then render `summary.md` / `notes.md` / `tour.md` and roll up
`overall` (STEP 4d) exactly as in the sandbox flow.

**STEP 4b (verify the tour)** — applies here too, if the row has one (check both
envs — often null on dev, set on prod). Resolve it **without** `--sandbox`
(`.venv/bin/python $H tour --task-id "$TASK_ID" --env "$ENV"`); `sandbox.*` URLs stay
null and any link-to-sandbox step is `n/a` (no e2b surface in local mode). Run
`command` steps **locally in `$WORK`**, in order — same pass/warn/fail and
starter-vs-solved rules as the sandbox path.

Mirror of the STEP 3 mis-flag check: a truly non-infra task's tour should also be
self-contained (build/test/git commands + the repo link). If a tour `command` here
needs a live service (`docker-compose up`, `curl localhost:4566`, connection refused
to a DB/broker), the task is **mis-flagged as non-infra** — record it as a
task-quality defect and re-verify the tour via the sandbox flow.

**STEP 5 (teardown)** — just `rm -rf "$WORK"` (nothing to kill).

## Out of scope (deliberately)

- **Batch / many tasks** — one task-id at a time; the user picks it.
- **Video recording** — removed; the report folder (`result.json` + `solution.diff`
  + the three rendered `.md` files) is the proof of the solve.
- **Driving the production candidate UI** — brittle, human-gated; never do it.
- **No fixes to the task, no commits** — solve, grade, report, stop.
