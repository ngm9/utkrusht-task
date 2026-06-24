---
name: task-solvability
description: Check whether ONE Utkrushta task is actually solvable — deploy it to an E2B sandbox, then YOU (the coding agent) solve it with your own tools in the code-server web IDE, RECORD the solve as a WebM by default (RED→fix→GREEN + think-aloud notes + a task-quality assessment), grade against the task's tests, and write a report to solvability_runs/<slug>/. The coding agent is the solver — no headless agent, no metered LLM API. Optional --frontend mode drives the full candidate frontend journey with the JWT. Use when verifying a generated task can be completed (not just that it deploys — that's the deployment-test skill).
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
| **`--frontend`** | also drive the full candidate FE journey with the JWT (gates) before the recorded solve | ✅ device gates pass with the media flags (below); ⚠️ provisioning UI may still be heavy |

**`--frontend` device/camera/screen-share gate — solved.** Launch agent-browser with
Chrome's fake-media flags so the camera + screen-share gates pass (the JS media mocks
were NOT enough — the device check calls the real `getUserMedia`, which headless Chrome
denies → "Device Access Denied"). Proven: camera → `tracks=1`, screen-share → `displaySurface=monitor`:

```bash
agent-browser open "<candidate_url>" \
  --args "--use-fake-ui-for-media-stream,--use-fake-device-for-media-stream,--auto-select-desktop-capture-source=Entire screen"
```

(also works via `AGENT_BROWSER_ARGS`). Set this on the launch/`record start` that drives the
candidate frontend; no `getUserMedia`/`getDisplayMedia` JS mock needed when the flags are on.

For `--frontend`, the deterministic infra is one command via the driver:
`.venv/bin/python .claude/skills/task-solvability/scripts/stack.py up`  (FE in Docker + verify flask)
then `… stack.py session --task-id T --class-id C` (creates the session + clears the gates + prints the candidate URL).
The backend itself is your compose stack: `docker compose -f /home/rsx/Desktop/utkrusht-ai/Utkrushta/docker-compose.local.yml up -d`.

## Outputs — `solvability_runs/<task-slug>/` (NOT `.task_agent_runs`)

Each run writes a clean, human-named report folder at the repo root (gitignored):
`solvability_runs/<task-slug>/` → `summary.md`, `notes.md` (think-aloud + task-quality), `result.json`, `solution.diff`, `solve.webm`, `frontend.webm` (frontend mode), `frames/*.png`.

## Variables

- `TASK_ID` = first token of `$ARGUMENTS` — **required** (ask if absent).
- `ENV` = `dev` default; `prod` only if the user says so.
- `PY` = `.venv/bin/python` — deps live in the venv, not system python.
- `H` = `.claude/skills/task-solvability/scripts/sandbox.py` — the sandbox helper.
- `STACK` = `.claude/skills/task-solvability/scripts/stack.py` — FE+session driver (`--frontend`).
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
   Expect it to FAIL (the task ships unsolved). If it already PASSES → record
   `verdict: invalid` (nothing to solve) and stop.
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
| **Task ships NO tests** (`pytest collected 0`) | `unverified` | `no_tests` |
| Clean starter already passed | `invalid` | `already_green` |

For `unverified`, record your **own judgment** ("implemented X per the spec; looks
complete") — but never call it `solvable`; with no test oracle, execution can't
prove it (and an agent will fabricate its own tests). Flag it as a task-quality
defect.

Append to `.task_agent_runs/solvable/results.jsonl` (one line):

```json
{"task_id":"<id>","env":"<env>","template":"<tpl>","verdict":"solvable","grade_signal":"tests_passed","iterations":3,"used_answer":false,"diff":".task_agent_runs/solvable/<id>.diff","notes":"<one line>","ts":"<iso>"}
```

(Get `ts` from `date -u +%Y-%m-%dT%H:%M:%SZ` — the helper has no clock.)

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
recorded   .task_agent_runs/solvable/<id>.diff  +  results.jsonl

VERDICT: SOLVABLE
NOTES: <what the task required / where it was tricky / or why it's unsolvable / unverified>
```

On `unverified` / `unsolvable`, say plainly what's wrong (no tests → not gradeable;
or the spec is underspecified / contradictory / needs resources that aren't there).

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
