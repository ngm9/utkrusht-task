# Task Builder

A conversational web app that interviews you for the task-generation
pipeline's inputs and runs the pipeline with live progress. The UI follows
the utkrusht.ai brand system (Inter, green ink `#0e6b3c`, white cards).

## Run it locally

    .venv/bin/python -m task_builder

Open http://127.0.0.1:8000

## Requires (in .env)

See [`../.env.example`](../.env.example) for the full contract. Minimum for
the chat: `ANTHROPIC_API_KEY`, `PORTKEY_API_KEY` (the conversational bot),
`SUPABASE_URL_APTITUDETESTSDEV` + `SUPABASE_API_KEY_APTITUDETESTSDEV`
(competency validation + conversation persistence), plus everything the
pipeline stages need to actually generate.

## Deploy

Container image built from `task_builder/Dockerfile` (build context = repo
root), shipped by `.github/workflows/task-builder{-dev,}.yaml` to GHCR and
deployed via Coolify. Full runbook: [`DEPLOYMENT.md`](DEPLOYMENT.md).

Deployed instances MUST set `INTERNAL_PROXY_TOKEN` — the UI prompts for it
once and sends it on every API call.

## How it works

The bot fills six slots — competencies, proficiency, role, focus areas, domain,
scenario count — validates them (competencies against Supabase), then runs
`preflight → input_files → scenarios → prompts → generate`, streaming
per-stage progress over Server-Sent Events.

See `docs/superpowers/specs/2026-05-18-task-builder-conversational-frontend-design.md`.
