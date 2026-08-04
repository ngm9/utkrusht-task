# Task Builder — Deployment Runbook

The service deploys the same way as the Utkrushta backend services:
GitHub Actions builds a `linux/arm64` image on the self-hosted `udev1`
runner, pushes it to GHCR, and triggers a Coolify deploy webhook.

```
push → .github/workflows/task-builder-dev.yaml
     → test (ubuntu-hosted) → build linux/arm64 (self-hosted udev1)
     → ghcr.io/ngm9/utkrusht-task-builder-dev:{latest, sha-<sha>}
     → curl Coolify webhook → Coolify pulls image → container healthy via /api/health
```

## One-time setup (dev)

### 1. Register the udev1 runner to this repo

The `udev1` self-hosted runner is registered to `ngm9/Utkrushta`; runners on
personal accounts are per-repo, so it must also be registered to
`ngm9/utkrusht-task`:

1. utkrusht-task → **Settings → Actions → Runners → New self-hosted runner**
   (Linux / ARM64) and copy the registration token.
2. On the udev-1 droplet, add a second runner instance in a new directory
   (a runner process serves exactly one repo):
   `./config.sh --url https://github.com/ngm9/utkrusht-task --token <TOKEN> --labels udev1`
   then install it as a service (`sudo ./svc.sh install && sudo ./svc.sh start`).

Alternative (no droplet access needed): change `runs-on` in both workflows to
a GitHub-hosted ARM runner. Slower cold builds, no shared cache with the
other services.

### 2. GitHub environment + secrets

Create environment **`task-builder-dev`** in utkrusht-task repo settings with:

| Secret | Value |
|---|---|
| `COOLIFY_DEPLOY_API_TOKEN` | Same Coolify API token the Utkrushta repo uses |
| `COOLIFY_TASK_BUILDER_DEV_DEPLOY_WEBHOOK` | Webhook URL from the Coolify app (step 3) |

(`GITHUB_TOKEN` is automatic; GHCR push works because the workflow has
`packages: write`.)

### 3. Coolify application

On the dev Coolify instance create a new **Docker Image** resource:

- **Image:** `ghcr.io/ngm9/utkrusht-task-builder-dev:latest`
- **Port:** 8000 (the Dockerfile HEALTHCHECK probes `/api/health`; Coolify
  reads container health — no extra healthcheck config needed)
- **Domain:** e.g. `taskbuilder-dev.utkrusht.ai`
- **Env vars:** everything in [`../.env.example`](../.env.example). Non-negotiable
  on a deployed instance: `INTERNAL_PROXY_TOKEN` (access token — without it
  the API is open to the internet), the Supabase dev pair (use the
  **service_role** key — see [Supabase key](#supabase-key)), `ANTHROPIC_API_KEY`,
  `PORTKEY_API_KEY`, `OPENAI_API_KEY`, GitHub tokens + `REPO_OWNER`,
  `E2B_API_KEY`, and `CORS_ALLOW_ORIGINS` (the frontend origin, or `*`).
- Copy the app's **deploy webhook URL** into the GitHub secret above.

### 4. Sizing

Unlike the other services this container *runs the generation pipeline
in-process* (up to 3 concurrent jobs, each a chain of `python -m`
subprocesses making LLM calls and E2B evals). Give it at least **2 GB RAM /
2 vCPU**. To lower the ceiling, reduce `_MAX_CONCURRENT_JOBS` in
`task_builder/jobs.py`.

## Prod

Same steps against the prod Coolify instance with the
`task-builder` GitHub environment, `COOLIFY_TASK_BUILDER_DEPLOY_WEBHOOK`
secret, image `ghcr.io/ngm9/utkrusht-task-builder`, prod Supabase env pair,
and `TASK_BUILDER_ENV=prod`. Deploys trigger from the `release` branch
(`task-builder.yaml`).

## Access control

`INTERNAL_PROXY_TOKEN` is a single shared access token:

- Every `/api/*` request must send it as `X-Internal-Token`; the SSE stream
  may pass it as `?access_token=` instead (EventSource cannot set headers).
- The frontend (separate service) prompts for it on the first 403, stores it
  in localStorage, and attaches it from then on.
- `/` (service descriptor) and `/api/health` stay public (liveness probe).
- Empty token env = auth disabled; acceptable only for `python -m task_builder`
  on localhost.

## CORS

The frontend is a separate origin, so the browser needs CORS headers.
`CORS_ALLOW_ORIGINS` (comma-separated, default `*`) is the allow-list — `*` is
safe because `INTERNAL_PROXY_TOKEN` still gates every call. Lock it to the
frontend URL in prod if you prefer. Preflight `OPTIONS` is always allowed.

## Supabase key

Use the dev **`service_role`** key for `SUPABASE_API_KEY_APTITUDETESTSDEV`.
The `conversations` / `generation_jobs` tables are RLS-gated; the anon key
makes `POST /api/session` fail (anon INSERT → 401 → 500).

## Smoke test after first deploy

```bash
curl -fsS https://taskbuilder-dev.utkrusht.ai/api/health   # {"status":"ok"}
curl -is https://taskbuilder-dev.utkrusht.ai/api/greeting | head -1   # 403 without token
curl -fsS -H "X-Internal-Token: $TOKEN" https://taskbuilder-dev.utkrusht.ai/api/greeting
```

Then point the separate frontend service at this API (`VITE_API_BASE`), enter
the token when prompted, run a conversation through to a `dev` generation, and
watch the stage panels stream.
