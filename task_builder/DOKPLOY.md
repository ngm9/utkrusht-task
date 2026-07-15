# Task Builder — Dokploy Deployment

Dokploy builds the image **on your Dokploy host** straight from this repo, so
there's no registry/CI step: it clones the branch, builds `task_builder/Dockerfile`,
and runs it. Two ways to do it — the UI (version-proof) or the API script.

## Prerequisites

- A Dokploy instance you can reach, and a **GitHub connection** configured in
  Dokploy (Settings → Git) so it can clone this private repo. (Or use a raw git
  URL + deploy key.)
- The app env values — copy `../.env.example`, fill it, and keep it out of git
  (e.g. `.env.dokploy`). Non-negotiable on a deployed instance:
  `INTERNAL_PROXY_TOKEN` (the access token — without it the API is public), the
  Supabase dev pair, `ANTHROPIC_API_KEY`, `PORTKEY_API_KEY`, `OPENAI_API_KEY`,
  `GITHUB_UTKRUSHTAPPS_TOKEN`, `GITHUB_GIST_TOKEN`, `REPO_OWNER`, `E2B_API_KEY`.

## Option A — UI (recommended, version-proof)

1. **New Project** → e.g. `task-builder`.
2. **New Application** inside it.
3. **Source** → GitHub → repo `ngm9/utkrusht-task`, branch
   `claude/task-builder-backend-deploy-jeccvk` (or `task-builder-service` after
   the PR merges).
4. **Build Type** → **Dockerfile**. Dockerfile path `task_builder/Dockerfile`,
   build context `.` (repo root — the image needs the whole repo to run the
   pipeline stages).
5. **Environment** → paste the filled env block (from `.env.example`).
6. **Domain** → add your host on **port 8000** (the container listens there; the
   Dockerfile healthcheck already probes `/api/health`). No domain? Use
   **Advanced → Ports** to publish a host port (e.g. `8080 → 8000`).
7. **Deploy**. Watch the Deployments tab. When health goes green, open the URL —
   the UI prompts once for `INTERNAL_PROXY_TOKEN`.

## Option B — API script

```bash
export DOKPLOY_URL="http://<host>:3000"
export DOKPLOY_API_KEY="<token>"          # rotate after deploying
export DOMAIN="taskbuilder.example.com"   # omit to publish a port instead
export APP_ENV_FILE="./.env.dokploy"      # your filled env file
./task_builder/dokploy_deploy.sh
```

The script creates the project → app → Git source → Dockerfile build → env →
domain → deploy, and prints the URL. Dokploy API field names drift between
versions; if a step 4xx's, check `$DOKPLOY_URL/swagger` and adjust that one
call's JSON key. The flow itself is stable.

## Sizing

This container runs the generation pipeline **in-process** (up to 3 concurrent
jobs, each a chain of `python -m` subprocesses making LLM + E2B calls). Give it
at least **2 GB RAM / 2 vCPU**. Lower the ceiling by reducing
`_MAX_CONCURRENT_JOBS` in `task_builder/jobs.py`.

## Smoke test after deploy

```bash
curl -fsS http://<host>/api/health                       # {"status":"ok"}
curl -is  http://<host>/api/greeting | head -1           # 403 without token
curl -fsS -H "X-Internal-Token: $TOKEN" http://<host>/api/greeting
```

Then open the UI, enter the token, run a conversation to a `dev` generation, and
watch the stage panels stream. The build being green and a task actually
generating are separate checks — the latter needs the LLM/Supabase/E2B keys
valid.
