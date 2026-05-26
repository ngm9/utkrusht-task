# Task Builder

A local conversational web app that interviews you for the task-generation
pipeline's inputs and runs the pipeline with live progress.

## Run it

    .venv/bin/python -m task_builder

Open http://127.0.0.1:8000

## Requires (in .env)

`ANTHROPIC_API_KEY`, `PORTKEY_API_KEY` (the conversational bot),
`SUPABASE_URL_APTITUDETESTSDEV` + `SUPABASE_API_KEY_APTITUDETESTSDEV`
(competency validation), plus everything the pipeline stages need.

## How it works

The bot fills six slots — competencies, proficiency, role, focus areas, domain,
scenario count — validates them (competencies against Supabase), then runs
`generate_input_files → scenario_generator → prompt_generator → multiagent
generate_tasks`, streaming per-stage progress over Server-Sent Events.

See `docs/superpowers/specs/2026-05-18-task-builder-conversational-frontend-design.md`.
