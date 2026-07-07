# trace_ui — live pipeline trace/log viewer

A tiny, self-contained web viewer that streams a `run_pipeline.py` run's stage
logs **and** captured LLM traces to your browser in real time. No build step,
no extra dependencies — FastAPI + uvicorn (already vendored for `task_builder`)
plus one static HTML file with vanilla JS over Server-Sent Events.

## Run it

```bash
# from the repo root, with the project venv
.venv/bin/python -m trace_ui
# then open http://127.0.0.1:8765/
```

Bind config (local-only by default — the viewer exposes run logs and full LLM
prompts, so do **not** serve it on a public interface):

| env var         | default     | meaning            |
|-----------------|-------------|--------------------|
| `TRACE_UI_PORT` | `8765`      | listen port        |
| `TRACE_UI_HOST` | `127.0.0.1` | bind host          |

## Launch a run

**+ New run** opens a modal to start a pipeline (`POST /api/runs` →
`run_pipeline.py`). Besides competencies / proficiency / env / task-shape, the
**LLM provider** select chooses the backend for the Claude-role calls:
*Anthropic · Claude* (default) or *GLM · OpenRouter* (`--llm-provider glm`, needs
`OPENROUTER_API_KEY`; override the slug with `OPENROUTER_GLM_MODEL`). The OpenAI
answer-code + eval-judge steps are unaffected. The chosen provider is recorded in
the run summary and shown in the Result panel; each trace card's model field also
makes it obvious which backend ran (`z-ai/glm-5.2` vs `claude-opus-4-8`).

## What it shows

Pick a run from the top-bar dropdown (populated from `/api/runs`, which scans
`.task_agent_runs/run-*/`). The page is a 3-pane live dashboard:

- **Left — stage timeline.** The 9 canonical stages (`input_files`, `scenarios`,
  `prompt`, `classifier`, `task_gen`, `eval`, `gate`, `quality`, `solution`).
  Each row shows live status + duration, driven by the `stages.jsonl` trace
  events; the active stage spins.
- **Center — live log console.** Every `*.stdout` / `*.stderr` / `*.log` in the
  run's combo dir, tailed concurrently and interleaved. `stderr` lines are red.
  Auto-scrolls, but pauses the moment you scroll up (a "resume" button reappears
  at the bottom). A stage filter narrows the console to one stage.
- **Right — live trace feed.** Each captured LLM call arrives as a card showing
  the stage badge, model, attempt, in/out tokens, and latency. Click a card to
  expand the full request prompt and the response text. The top bar keeps a
  running total of calls + tokens.

## How it works

- `tailer.py` — `list_runs()`, a hardened `resolve_run_dir()` (rejects path
  traversal / absolute paths / anything escaping `.task_agent_runs/`), and async
  `tail_file()` / `tail_jsonl()` generators that follow appended files by polling
  offsets (~0.25s), tolerating a file that does not exist yet.
- `server.py` — FastAPI app. `GET /` serves the page; `GET /api/runs` lists
  runs; `GET /api/runs/{run_id}/stream/logs` and `.../stream/traces` are SSE
  endpoints built on a plain `StreamingResponse` (no `sse-starlette`). A
  heartbeat comment is emitted every ~15s so idle connections survive proxies.
- `static/index.html` — the whole UI: dark theme, CSS-grid layout, `EventSource`
  wiring. No external CDN.

## Live streaming note

`run_pipeline.py` sets `PYTHONUNBUFFERED=1` on every stage subprocess so each
stage flushes stdout/stderr to its log file line-by-line. Without that, the
non-task stages block-buffer their output and nothing would stream until the
stage exits.
