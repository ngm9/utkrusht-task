# Task Builder — Backend API

The backend for Task Builder: a FastAPI service that interviews you (via the
conversational bot) for the task-generation pipeline's inputs and runs the
pipeline with live progress streamed over SSE. It exposes JSON at `/api/*`
only — **the web UI is a separate frontend service** (its own repo).

## Run it locally

    .venv/bin/python -m task_builder

Serves the API on http://127.0.0.1:8000 — browse the interactive docs at
http://127.0.0.1:8000/docs. Point the frontend dev server at this URL
(`VITE_API_BASE`), or run it same-origin behind a proxy.

## Requires (in .env)

See [`../.env.example`](../.env.example) for the full contract. Minimum for
the chat: `ANTHROPIC_API_KEY`, `PORTKEY_API_KEY` (the conversational bot),
`SUPABASE_URL_APTITUDETESTSDEV` + `SUPABASE_API_KEY_APTITUDETESTSDEV`
(competency validation + conversation persistence), plus everything the
pipeline stages need to actually generate.

> **Use the Supabase `service_role` key, not the `anon` key.** The
> `conversations` / `generation_jobs` tables are RLS-gated, so an anon key
> makes `POST /api/session` fail with 500 (anon INSERT → 401). Set
> `SUPABASE_API_KEY_APTITUDETESTSDEV` to the dev **service_role** key.

`CORS_ALLOW_ORIGINS` (comma-separated, default `*`) controls which frontend
origins may call the API from a browser.

## Deploy

Container image built from `task_builder/Dockerfile` (build context = repo
root), shipped by `.github/workflows/task-builder{-dev,}.yaml` to GHCR and
deployed via Coolify. Full runbook: [`DEPLOYMENT.md`](DEPLOYMENT.md).

Deployed instances MUST set `INTERNAL_PROXY_TOKEN` — every `/api/*` call must
carry it as `X-Internal-Token` (the SSE stream accepts `?access_token=`). The
frontend prompts the user for it once and attaches it from then on.

## How it works

The bot fills five slots — competencies, proficiency, role, focus areas,
domain — validates them (competencies against Supabase). When the brief is
complete a **review step** appears (human-in-the-loop, before any generation):

- **Instructions** — an optional authoritative free-text directive that shapes
  the task (infra vs non-infra, a required dependency like Redis, a deliverable
  like a Dockerfile). Passed to the prompt stage's `--instructions`. LLM-written
  suggestion chips (`GET /api/suggest-instructions`) offer competency-tailored
  starters.
- **Scenario** — optionally pick one scenario for the task. "Choose a scenario"
  builds the candidate pool (`POST /api/prepare` → preflight → input_files →
  scenarios) and shows it (`GET /api/scenarios`); the pick locks generation to
  that scenario (via the generate stage's new `--scenario-file`). Skip it and
  the pipeline auto-rotates the pool.

Generation then runs `preflight → input_files → scenarios → prompts → generate`
(stages 00–02 are skipped when the pool was already prepared), streaming
per-stage progress over Server-Sent Events.

See `docs/superpowers/specs/2026-05-18-task-builder-conversational-frontend-design.md`.
