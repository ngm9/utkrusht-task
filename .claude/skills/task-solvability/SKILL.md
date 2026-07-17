---
name: task-solvability
description: Check whether ONE Utkrushta task is actually solvable — deploy it to an E2B sandbox, then YOU (the coding agent) solve it with your own tools in the code-server web IDE, RECORD the solve as a WebM by default (RED→fix→GREEN + think-aloud notes + a task-quality assessment), grade against the task's tests, and write a report to solvability_runs/<slug>/. The coding agent is the solver — no headless agent, no metered LLM API. Non-infra tasks (is_shared_infra_required = false) can run in --local mode — clone + install deps + solve + grade entirely on this machine, no E2B sandbox. Use when verifying a generated task can be completed (not just that it deploys — that's the deployment-test skill).
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

**Recording is ON by default** — every run produces a WebM of the solve in the
code-server web IDE. Use `--quick` only when you explicitly want to skip the video.

| Mode | What runs | Reliable? |
|---|---|---|
| **default** | deploy → I solve in the **code-server web IDE, RECORDED** (RED→fix→GREEN + notes) → grade → write report | ✅ |
| **`--quick`** | same, but **no video** (faster) — verdict + `solution.diff` + notes only | ✅ |
| **`--local`** | **non-infra tasks only** — clone + install deps + solve + grade entirely on THIS machine; no E2B sandbox, no video | ✅ (see "Local mode" below) |

**Auto-suggest local:** `load` prints `is_shared_infra_required`. If it's `false` and the
user didn't ask for a recording, prefer `--local` — it's faster and free
(no sandbox billing). If it's `true`, `--local` is INVALID (the task needs the template's
services) — hard-fail with that explanation and fall back to the sandbox flow.

## Outputs — `solvability_runs/<task-slug>/` (NOT `.task_agent_runs`)

Each run writes a clean, human-named report folder at the repo root (gitignored):
`solvability_runs/<task-slug>/` → `summary.md`, `notes.md` (think-aloud + task-quality), `result.json`, `solution.diff`, `solve.webm`, `frames/*.png`, `tour.md` (per-step tour verification, when the row has a tour — STEP 4b).

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
3. **Establish the baseline** — run the suite once on the clean starter:
   ```bash
   .venv/bin/python $H run --sandbox "$SANDBOX" --cmd "$TEST_CMD"
   ```
   Now read the **output**, not just the exit code. A task is **NOT required to
   ship tests** — "no tests" is a distinct outcome from "tests failed," and must
   never be reported as a fail. Classify what you see:

   | Output signal | Meaning | What to do |
   |---|---|---|
   | pytest `no tests ran` / exit **5**; npm `no test specified` or `Missing script: "test"`; go `[no test files]`; cargo `running 0 tests` (0 collected) | **no tests exist** | STOP the solve → verdict `unverified` / `no_tests` (STEP 4). Do NOT treat as red-to-fix; do NOT treat go/cargo's exit-0 as "already green." |
   | real assertions failed (non-zero **with** failing test names) | baseline **red** — good, there's something to solve | continue to step 4 |
   | tests were collected and all passed | clean starter already green | verdict `invalid` (nothing to solve), stop |

   ⚠️ **The trap that makes no-tests look like a fail:** pytest/npm with no tests
   exit **non-zero** (looks red), while go/cargo with no tests exit **zero** (looks
   already-solved). Both are `no_tests` — decide on whether tests were *collected*,
   never on the exit code alone.
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
| You made a real effort, suite still red | `unsolvable` | `tests_failed` |
| **Task ships NO tests** (0 collected on ANY stack — see STEP 3.3 signals; never a `fail`) | `unverified` | `no_tests` |
| Clean starter already passed | `invalid` | `already_green` |

For `unverified` (`no_tests`), record your **own judgment** ("implemented X per the
spec; looks complete") — but never call it `solvable` and **never call it `fail`**:
with no test oracle, execution can neither prove nor disprove the solution (and an
agent left to invent its own tests will just fabricate a pass). A missing test suite
is a **not-gradeable** outcome, not a failed one. Whether that's a task-quality
*defect* depends on the task: flag it if this kind of task is expected to ship tests;
note it neutrally if the task is legitimately graded some other way.

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

On `unverified` / `unsolvable`, say plainly what's wrong (no tests → not gradeable;
or the spec is underspecified / contradictory / needs resources that aren't there).

The `no_tests` outcome is reported as its own line — **not** as a red/failed suite:

```
baseline   ⚪ no tests — suite collected 0 tests (task ships none; not a failure)
solve      ⚪ unverified — implemented per the spec by inspection; no oracle to grade against
VERDICT: UNVERIFIED (no_tests)
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
plain Bash in `$WORK` — no `put`/sync loop, no `$H run`. Same ~8-cycle cap, same
"never edit the tests" rule, and the **same baseline classification** (STEP 3.3):
if the runner collects 0 tests, that's `unverified` / `no_tests`, never a fail —
even though `go test`/`cargo test` exit 0 with no test files. If the tests unexpectedly need a live service (connection
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

**STEP 5 (teardown)** — just `rm -rf "$WORK"` (nothing to kill). No WebM in local
mode (there's no code-server IDE to record) — local mode implies `--quick`; if the
user wants video proof, use the sandbox flow.

## Recorded mode (`--record`) — headless video proof

Produces a **WebM video** of the RED→solve→GREEN happening in the task's **real
sandbox environment** — so a Claude agent can run this fully headless and hand
back a recording that demonstrates **deployability + solvability** "like a human
working the task." No candidate frontend, no login, no device/screen-share gates,
no mocked media. (Driving the production candidate UI is rejected: it's brittle,
human-gated, and forces a *fake* screen-share — the recording would be a blank
canvas. Record the real sandbox instead.)

**Prereq:** `npm i -g agent-browser && agent-browser install` (Rust browser CLI;
no Playwright/MCP needed — drive it from Bash).

The sandbox template exposes a **browser terminal (ttyd) on port 7681** at
`https://7681-<sandbox_id>.e2b.app`. After STEP 2 (deploy), drive it:

```bash
TTYD="https://7681-${SANDBOX}.e2b.app"
tcmd(){ agent-browser keyboard type "$1"; agent-browser press Enter; sleep "$2"; }  # ttyd auto-focuses

agent-browser record start "$REC_DIR/solve.webm" "$TTYD"   # fresh ctx -> terminal; keystrokes target it
sleep 4
tcmd "cd /home/user/task" 1
tcmd "sed -n 1,8p README.md" 2                              # show the problem
tcmd "python -m pytest -q" 12                               # RED (baseline) ; screenshot red.png
# --- apply YOUR solution into the SAME sandbox (off-camera, via the helper) ---
#   sandbox.py put --sandbox $SANDBOX --local <fixed-file> --remote /home/user/task/<path>
tcmd "git --no-pager diff --stat" 2                         # show the fix on camera
tcmd "python -m pytest -q" 12                               # GREEN ; screenshot green.png
agent-browser record stop
agent-browser close --all
```

Notes that matter (learned live):
- `record start` makes a **fresh context** but subsequent `keyboard`/`screenshot`
  commands DO target it (verified). ttyd renders to a **canvas** → `.innerText` is
  empty; use `agent-browser screenshot` to capture RED/GREEN, not text scraping.
- Apply the solution via the helper `put` (e2b file API) between the two `pytest`
  runs — same sandbox filesystem the terminal sees — then `git diff` shows it.
- Save `solve.webm` + `red.png` + `green.png` under
  `.task_agent_runs/solvable/recordings/<task-id>/` and reference them in the
  `results.jsonl` row (add a `recording` field).

## Out of scope (deliberately)

- **Batch / many tasks** — one task-id at a time; the user picks it.
- **Driving the production candidate UI** — rejected (see Recorded mode): brittle,
  human-gated, fake screen-share. The sandbox recording is the headless substitute.
- **No fixes to the task, no commits** — solve in the sandbox, record, stop.
