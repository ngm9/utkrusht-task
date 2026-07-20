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

Each run writes a clean, human-named report folder at the repo root (gitignored):
`solvability_runs/<task-slug>/` → `summary.md`, `notes.md` (think-aloud + task-quality), `result.json`, `solution.diff`, `tour.md` (per-step tour verification, when the row has a tour — STEP 4b).

### `summary.md` structure (required sections, in this order)

Write `summary.md` in your OWN words — never paste the README/problem statement in.

**Writing style (applies to every section) — "layered" framing:**

- Every issue and every fix is a **layered bullet**: the first line is ONE bold
  plain-English sentence anyone can understand (no jargon, no file names);
  indented lines underneath carry the precise technical detail.
- Short sentences, one idea per sentence. Active voice. Everyday words first;
  when a technical term is unavoidable, explain it in brackets — e.g.
  "a timezone-aware timestamp (a time that knows its timezone)".
- Never pack symptom + cause + fix into one long sentence — split them.

Layered bullet shape:

```
- **Looking up any product crashed the tool.**
  Detail: the code subtracted a timezone-aware database timestamp from a
  local time without a timezone — Python raises a TypeError on that.
  Fix: both times are now compared in UTC.
```

Sections:

1. **`## Current Implementation`** — one short plain paragraph on what the
   starter ships, then a **`### Verified by running it`** sub-section with the
   ACTUAL evidence from STEP 3's current-state check (never claim anything here
   you didn't observe by executing something): which services were up, real DB
   row counts / seeded data, real API responses (HTTP codes + bodies), build
   output, and the baseline test result line. Then **layered bullets, one per
   broken thing** (bold plain sentence + indented `Detail:` line with the
   technical cause + `Observed:` line quoting the runtime evidence — the actual
   error, wrong response, or failing output that proves it).
2. **`## Objectives`** — what the task asked to be solved, restated from the
   problem + failing tests in your own words (NOT copied from the README);
   short plain bullets, one objective per bullet, everyday words.
3. **`## What Was Solved`** — **layered bullets, one per fix**: bold plain
   sentence saying what now works, then indented `Detail:` (file + exact
   change) and why it was needed. Include the iteration count and the final
   test result line.
4. **`## Verdict`** — the verdict (`solvable` / `unsolvable` / `unverified` /
   `invalid`), `grade_signal`, and one-line justification.

## Variables

- `TASK_ID` = first token of `$ARGUMENTS` — **required** (ask if absent).
- `ENV` = `dev` default; `prod` only if the user says so.
- `PY` = `.venv/bin/python` — deps live in the venv, not system python.
- `H` = `.claude/skills/task-solvability/scripts/sandbox.py` — the sandbox helper.
- `SLUG` = the repo name (e.g. `cargolink-pickup-context-repair`); outputs go to `solvability_runs/$SLUG/`.

`.env` is auto-loaded by `infra/e2b/__main__.py`; the helper loads it too.

---

## STEP 1 — Preflight (cheap; fail before booting a sandbox)

```bash
cd <repo-root>
.venv/bin/python -c "import e2b; from infra.e2b import sandbox_manager" || echo "FATAL: run from .venv"
for k in E2B_API_KEY GITHUB_UTKRUSHTAPPS_TOKEN SUPABASE_URL_APTITUDETESTSDEV SUPABASE_API_KEY_APTITUDETESTSDEV; do
  grep -q "^$k=" .env || echo "FATAL: missing $k in .env"
done
.venv/bin/python .claude/skills/task-solvability/scripts/sandbox.py load --task-id "$TASK_ID" --env "$ENV"
```

**Hard-fail** if the import errors, a key is missing, or `load` raises (task not
found / no template / no starter repo). `load` prints `template_id`, `starter_repo`,
`test_cmd`, and `has_problem` — note them.

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
   These observations are REQUIRED input for summary.md's
   `### Verified by running it` sub-section — findings must be reported from
   execution evidence, not inferred from source code.
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
   | tests were collected and all passed | clean starter already green | verdict `invalid` (nothing to solve), stop |

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

Capture the agent's diff and append one JSON line to the log:

```bash
mkdir -p .task_agent_runs/solvable
.venv/bin/python $H diff --sandbox "$SANDBOX" > ".task_agent_runs/solvable/${TASK_ID}.diff"
```

**Verdict rules (be honest — never a hollow green):**

| Situation | `verdict` | `grade_signal` |
|---|---|---|
| Suite went green after your edits | `solvable` | `tests_passed` |
| **No test suite**, but you solved it and verified the behaviour by running it | `solvable` | `inspection` |
| You made a real effort, suite still red | `unsolvable` | `tests_failed` |
| **No test suite**, and you could not make the required behaviour work | `unsolvable` | `inspection` |
| Clean starter already passed | `invalid` | `already_green` |

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

Append to `.task_agent_runs/solvable/results.jsonl` (one line):

```json
{"task_id":"<id>","env":"<env>","template":"<tpl>","verdict":"solvable","grade_signal":"tests_passed","iterations":3,"used_answer":false,"diff":".task_agent_runs/solvable/<id>.diff","notes":"<one line>","ts":"<iso>"}
```

(Get `ts` from `date -u +%Y-%m-%dT%H:%M:%SZ` — the helper has no clock.)

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

**Record** a `tour.md` in the report folder: one line per step
(`✅ pass` / `⚠️ warn: <why>` / `❌ fail: <why>`), and add a `tour` block to
`result.json` with counts + the overall `tour_verdict`
(`ok` | `defects` | `n/a`). A tour with any `❌` is a **task-quality defect** — the
task can be *solvable* yet ship a *broken tour*; report both verdicts honestly, don't
let a green solve hide a red tour.

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
recorded   .task_agent_runs/solvable/<id>.diff  +  results.jsonl

VERDICT: SOLVABLE   (TOUR: OK)
NOTES: <what the task required / where it was tricky / or why it's unsolvable / unverified>
```

On `unsolvable`, say plainly what's wrong (the spec is underspecified /
contradictory / needs resources that aren't there).

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
only the Supabase + GitHub keys. Hard-fail `--local` if `is_shared_infra_required: true`.

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
manifests (real error output) — summary.md's `### Verified by running it`
section is required in local mode as well. Same ~8-cycle cap, same
"never edit the tests" rule, and the **same baseline classification** (STEP 3.3):
if the runner collects 0 tests, solve it anyway and grade by `inspection` — never
a fail, never `unverified` — even though `go test`/`cargo test` exit 0 with no
test files. If the tests unexpectedly need a live service (connection
refused to a DB/broker), the task is mis-flagged as non-infra — record that as a
task-quality defect and rerun via the sandbox flow.

**STEP 4 (grade + record)** — same verdict table. Capture the diff with
`git -C "$WORK" add -A && git -C "$WORK" diff --cached > solvability_runs/$SLUG/solution.diff`.
Add `"mode":"local"` to the `results.jsonl` row.

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
- **Video recording** — removed; the report folder (`summary.md` + `solution.diff`
  + `result.json`) is the proof of the solve.
- **Driving the production candidate UI** — brittle, human-gated; never do it.
- **No fixes to the task, no commits** — solve, grade, report, stop.
