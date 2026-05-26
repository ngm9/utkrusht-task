# Task Builder — Live Collapsible Stage Logs

**Date:** 2026-05-19
**Status:** Approved

## Problem

When the Task Builder runs the five-stage pipeline, the UI shows only a
one-line status per stage (`✓ 01_input_files`). The user is blind to what each
stage is doing or how far along it is — a stage can run for minutes with no
visible signal.

## Goal

Stream each stage's real log output into the chat UI **live, while the stage
runs**, inside a **collapsible panel** per stage.

## Decisions

- **Log source:** both `.stdout` and `.stderr` per stage, merged. The pipeline
  stages write inconsistently — `00_preflight` and `01_input_files` write only
  to stdout (their `.stderr` is empty), while `02_scenarios`, `03_prompt`,
  `04_tasks` write live progress via Python `logging` to stderr. Showing both
  means no stage panel is ever blank.
- **Collapse behaviour:** the running stage auto-expands; it auto-collapses to a
  one-line summary when it finishes `ok`; a `failed` stage stays expanded.

## Approach

A background **file tailer** watches each stage's log files while the stage
runs and pushes new content onto the **existing SSE event queue** as a new
`status="log"` event. `server.py` needs no changes — it already forwards any
`StageEvent`.

### New module — `task_builder/log_tail.py`

`StageLogTailer(paths, emit, *, interval_s=0.5)`:

- Daemon thread. Every `interval_s`, reads bytes appended to each path since the
  last read (tracked per-path byte offset), decodes `utf-8` with
  `errors="replace"`, and calls `emit(chunk)` for any non-empty chunk.
- A missing file yields an empty read (the file is created by `_run_stage`
  shortly after the tailer starts).
- `stop()` signals the thread and joins it; the thread performs one **final
  drain** so block-buffered stdout flushed at process exit is not lost.

### `task_builder/runner.py`

In the `_stage()` closure:

```
emit(running) → tailer.start() → _run_stage() [blocks] → tailer.stop() → emit(ok/failed)
```

The tailer's `emit` wraps each chunk as
`StageEvent(stage=label, status="log", detail=chunk)`. Per-stage event order is
therefore always `running → log… → ok/failed`.

### `StageEvent`

No schema change. `status` is a plain `str` (a `"log"` value is valid); the
chunk rides in the existing `detail` field.

### `task_builder/static/app.js`

`streamRun()` keeps a `label → panel` map. Each stage renders as a `<details>`
bubble:

- `running` → create/open the panel, summary `⏳ <stage>`
- `log` → append `detail` to the panel's `<pre>`, auto-scroll
- `ok` → summary `✓ <stage> (<n>s)`, collapse
- `failed` → summary `✗ <stage> <detail>`, stay open
- `done` → existing outcome bubble + repo link

### `task_builder/static/styles.css`

Styles for the `<details>` panel and a monospace, scrollable `<pre>` log area.

## Testing

`tests/test_task_builder_log_tail.py` (new): tailer emits appended content,
final-flushes remaining content on `stop()`, tolerates a not-yet-created file,
and merges two files. Existing `tests/test_task_builder_runner.py` confirms
stage-event ordering still holds (it mocks `_run_stage`, so the tailer sees no
files and emits nothing — harmless).

## Out of scope

- Persisting logs beyond the in-memory run (logs already live on disk in
  `.task_agent_runs/`).
- Perfect chronological interleaving of stdout vs stderr (approximate, by poll
  order — acceptable).
