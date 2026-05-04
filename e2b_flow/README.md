# `e2b_flow` — E2B sandbox deploy/reset (PoC)

Alternate path for deploying assessment tasks to **E2B sandboxes** instead
of DigitalOcean droplets. The existing `multiagent.py deploy-task` /
`reset-task` flow is untouched; this module is a parallel CLI invoked via
`python -m e2b_flow`.

See `docs/research/deployment-infrastructure.md` for the full motivation,
alternatives, costs, and end-to-end design (frontend, backend, state).

## What this PoC proves

| Question | How |
|---|---|
| Can our `run.sh` / `kill.sh` task content survive unchanged? | Run a real Python+SQL task in a sandbox; verify Postgres comes up with seed data. |
| Is teardown atomic? | `reset-task` should leave no orphans; second deploy should be clean. |
| Does abandonment self-clean? | Set short idle timeout, do nothing, confirm the sandbox dies on its own. |
| Is re-deploy idempotent? | `deploy-task` twice in a row should not silently break. |
| Does DinD work inside the Firecracker microVM? | `docker compose up` inside the sandbox is the canonical test. |

## Layout

```
e2b_flow/
├── __init__.py
├── __main__.py              # Click commands: deploy-task, reset-task, list-sandboxes, kill-sandbox
├── sandbox_manager.py       # E2B SDK wrappers (only file that talks to `e2b`)
├── supabase_helpers.py      # Reads/writes for `tasks.deployment_info`
├── templates/
│   └── python-sql/
│       ├── template.py      # E2B v2 SDK template definition (AsyncTemplate)
│       ├── build_dev.py     # builds template `utkrusht-python-sql-dev`
│       ├── build_prod.py    # builds template `utkrusht-python-sql`
│       └── start.sh         # boots dockerd before sandbox supervisor
└── README.md                # this file
```

E2B moved templates from a Dockerfile-based v1 build to an SDK-based v2
build system. Template definition is now Python (`template.py`) using
`e2b.AsyncTemplate`. Builds are triggered by running `build_dev.py` /
`build_prod.py`, not by `e2b template build`.

## One-time setup

1. **Sign up at [e2b.dev](https://e2b.dev) and create an API key.**
2. **Add the key to `.env` at repo root:**
   ```bash
   E2B_API_KEY=e2b_...
   ```
3. **Install Python deps** (already pinned in `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```
4. **Install the E2B CLI** (one-time, global) — needed for `e2b auth login`:
   ```bash
   npm install -g @e2b/cli
   ```
5. **Authenticate the CLI:**
   ```bash
   e2b auth login
   ```
6. **Build the python-sql template** (one-time per template change).
   E2B uses a v2 SDK-based build, not `e2b template build`:
   ```bash
   cd e2b_flow/templates/python-sql
   python build_dev.py        # → builds `utkrusht-python-sql-dev`
   # python build_prod.py     # → builds `utkrusht-python-sql` (use once stable)
   ```
   The build streams logs to your terminal and registers the template
   under your E2B account. The deploy command defaults to the `-dev`
   template, so iterate freely with `build_dev.py` and only run
   `build_prod.py` once you want a stable name.

## Usage

### Deploy a task into a sandbox

```bash
python -m e2b_flow deploy-task --task-id <UUID> --env dev
# Optional: --template utkrusht-python-sql-dev  (default)
# Optional: --timeout-hours 2                   (sandbox idle timeout)
```

Output is JSON:

```json
{
  "task_id": "...",
  "sandbox_id": "...",
  "template": "utkrusht-python-sql",
  "terminal_url": "https://...",
  "exposed_ports": {
    "5432": "https://5432-...e2b.dev",
    "8000": "https://8000-...e2b.dev"
  },
  "timeout_seconds": 7200
}
```

`tasks.is_deployed` is set to `true` and `tasks.deployment_info` is
populated with `deployment_method = "e2b_sandbox"`, the sandbox handle,
and the URLs above.

### Reset (kill) the sandbox for a task

```bash
python -m e2b_flow reset-task --task-id <UUID> --env dev
```

Calls `Sandbox.connect(...).kill()` and clears
`tasks.deployment_info` / `is_deployed`.

### Debug commands

```bash
# List all sandboxes currently running for the configured account
python -m e2b_flow list-sandboxes

# Force-kill a sandbox by ID (bypasses Supabase)
python -m e2b_flow kill-sandbox --sandbox-id <id>
```

## Verification checklist

Pick a known-good Python+SQL task ID from Supabase dev (`is_deployed=false`).

1. **Deploy:**
   ```bash
   time python -m e2b_flow deploy-task --task-id $TASK_ID --env dev
   ```
   Expect ~15–25s. Capture the `terminal_url` and the `5432` host.
2. **Open the terminal URL** in a browser. Inside the sandbox:
   ```bash
   docker ps                                            # postgres up
   psql -h localhost -U postgres -d <db> -c "\\dt"      # tables exist
   psql -h localhost -U postgres -d <db> \
        -c "select count(*) from <seeded_table>"        # seed loaded
   ```
3. **Verify Supabase:** `tasks.is_deployed = true`,
   `tasks.deployment_info.sandbox_id` matches.
4. **Reset:**
   ```bash
   python -m e2b_flow reset-task --task-id $TASK_ID --env dev
   ```
5. **Verify cleanup:**
   - `python -m e2b_flow list-sandboxes` no longer shows it.
   - Supabase row: `is_deployed = false`, `deployment_info = null`.
6. **Idempotence:** re-run deploy twice without resetting between runs.
   The second call should produce a fresh sandbox without silent failure.
   (The current implementation overwrites `deployment_info` — capture both
   sandbox IDs so you can clean up the orphan with `kill-sandbox`. Phase 2
   moves this to a `sandbox_sessions` table that supports concurrent
   sessions per task cleanly.)
7. **Abandonment:** redeploy with `--timeout-hours 1` and a small fudge —
   pass `--timeout-hours 0.1` (6 min) if your shell tolerates it, or edit
   the default in `sandbox_manager.py` for the test. Do nothing for the
   timeout window; confirm via `list-sandboxes` that the sandbox vanishes
   without intervention. *This is the failure mode the droplet flow does
   not handle today.*

## Comparison to the droplet flow

| | `multiagent.py deploy-task` | `python -m e2b_flow deploy-task` |
|---|---|---|
| Provisioning | `select_best_droplet_ip()` polls `AVAILABLE_IPS` over SSH | None — `Sandbox.create()` |
| File transfer | `git clone` locally → SFTP upload to droplet | `git clone` runs *inside* the sandbox |
| Setup | SSH `bash run.sh` | `sb.commands.run("bash run.sh")` |
| Public URL | candidate gets droplet IP + SSH key | candidate gets HTTPS URLs (terminal + service) |
| Teardown | SSH + `kill.sh` + `rm -rf /root/task` | `sb.kill()` (atomic) |
| Abandonment | droplet stays "occupied"; manual cleanup | sandbox auto-destroys at idle timeout |
| State | Supabase + GitHub + droplet FS + droplet docker + IP pool | Supabase + GitHub + sandbox handle |

## Caveats / known limitations (PoC)

- **Raw TCP exposure** for Postgres/Redis from candidate's laptop
  (e.g., `psql -h <host> -p 5432`) is *not* validated yet. The
  in-sandbox terminal is the recommended fallback.
- **DinD** depends on the template booting `dockerd` cleanly. If
  `docker info` fails inside the sandbox, the template needs work.
  Check `/var/log/docker.log` from the in-sandbox terminal.
- **Concurrent sessions per task** are not modeled; `tasks.deployment_info`
  is single-valued. Phase 2 introduces `sandbox_sessions` to fix this.
- **`multiagent.py` is intentionally untouched.** This is a parallel path
  for the PoC; convergence is Phase 5+.

## Env vars used

| Var | Purpose |
|---|---|
| `E2B_API_KEY` | E2B SDK authentication |
| `SUPABASE_URL_APTITUDETESTSDEV`, `SUPABASE_API_KEY_APTITUDETESTSDEV` | Dev Supabase |
| `SUPABASE_URL_APTITUDETESTS`, `SUPABASE_API_KEY_APTITUDETESTS` | Prod Supabase |
