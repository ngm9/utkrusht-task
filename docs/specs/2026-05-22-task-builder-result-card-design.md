# Task Builder — End-of-Run Result Card

**Date:** 2026-05-22
**Status:** Approved
**Scope:** `task_builder/` — the runner and the static frontend.

## Problem

When a generation run finishes successfully, the Task Builder UI shows only a
one-line outcome bubble plus a single GitHub repository link. The `done` event
already carries the `task_id`, and stage 4 already prints the task's name, type,
and covered competencies — but none of that reaches the user. The end of a run
should present a proper result, not just a link.

## Goals

Show, at the end of a **successful** run, a result card with:

- **Task ID** — the Supabase task UUID
- **Task name**
- **Task type** (e.g. `BUILD`)
- **Competencies covered**
- **Environment** (`dev` / `prod`)
- **GitHub repository** link (already shown today)

## Non-goals

- The GitHub **Gist** link and the **Answer repository** link — explicitly
  excluded by the user. (They would require plumbing new output through
  `multiagent.py`; not in scope.)
- Any change to `multiagent.py`. Every field above is already printed by stage 4
  or already known to the runner.
- Changing the **failed**-run display — it stays as the current outcome text.

## Decisions (from brainstorming)

- Fields to show: task ID, name, type, competencies, environment, repo link.
- Gist and answer-repo links are out of scope.
- No `multiagent.py` change — extend the runner's existing stdout extractor
  instead.
- Present the fields as a key/value **result card**, styled like the existing
  task-brief summary card.

## Background — what stage 4 already prints

`multiagent.py`'s `generate_tasks` success path prints these lines to stdout
(captured by the runner as `04_tasks.stdout`):

```
 Task Creation Successful!
 Task Type: <type>
 Task ID: <uuid>
 Task Name: <name>
 Competencies Covered: <comma-separated list>
 GitHub Repository: <url>
 ...
 TASK CREATION COMPLETED SUCCESSFULLY!
```

The runner's `_extract_task_result` currently parses only `Task ID:` and
`GitHub Repository:`. The other three lines are present and unparsed.

---

## Design

### Backend — `task_builder/runner.py`

**`StageEvent`** gains four optional fields (it already has `task_id`,
`task_url`):

```python
task_name: str | None = None
task_type: str | None = None
competencies: str | None = None   # the comma-joined string as printed
env: str | None = None
```

Being a frozen dataclass serialized with `dataclasses.asdict`, the new fields
flow to the browser over SSE automatically.

**`_extract_task_result`** is extended to parse five lines from the stage-4
stdout instead of two. It returns a `dict` with keys `task_id`, `task_url`,
`task_name`, `task_type`, `competencies` — each `None` when its line is absent
(e.g. a failed run, or an older `multiagent.py`):

- `Task ID:` → `task_id`
- `GitHub Repository:` → `task_url`
- `Task Name:` → `task_name`
- `Task Type:` → `task_type`
- `Competencies Covered:` → `competencies` (matched as the full phrase, so it
  does not collide with the later `Competencies:` summary line)

Each value is taken as the text after the first occurrence of its label,
`strip()`-ed; an empty result becomes `None`.

**The terminal `completed` event** is built from that dict plus `env` (the
existing `run_pipeline_for_brief` parameter):

```python
result = _extract_task_result(Path(rec["stdout"]))
emit(StageEvent("done", "completed", detail=outcome, outcome=outcome,
                task_id=result["task_id"], task_url=result["task_url"],
                task_name=result["task_name"], task_type=result["task_type"],
                competencies=result["competencies"], env=env))
```

The **failed** `done` events are unchanged — they carry none of these fields.

### Frontend — `task_builder/static/app.js`

`renderDone(spec)` is updated:

- On `spec.status === "completed"` → render a **result card** (a `bot` bubble
  with a `result-card` class) containing a `Task created` heading and a
  key/value grid. Rows, each rendered **only when its value is non-empty**:
  - Task ID — `spec.task_id`
  - Name — `spec.task_name`
  - Type — `spec.task_type`
  - Competencies — `spec.competencies`
  - Environment — `spec.env`
  - Repository — `spec.task_url`, rendered as a clickable `<a>` (target
    `_blank`, `rel="noopener"`)
  - All text values are written via `textContent` (XSS-safe); only the
    repository row is a link.
- On `spec.status` other than `completed` → unchanged: the current
  `stage failed` outcome bubble.

`doneBubble(e)` builds the `spec` from the event including the new fields, and
records the `done` transcript item with them. The `done` transcript item shape
becomes:

```
{ kind: "done", status, outcome, detail, task_url,
  task_id, task_name, task_type, competencies, env }
```

`renderItem`'s `done` branch already calls `renderDone` — it builds the spec
with the new fields defaulted to `""` (consistent with the existing
malformed-item hardening), so a restored transcript re-renders the full card.

### Styles — `task_builder/static/styles.css`

Add a `.result-card` rule that reuses the existing summary-card visual language
(border, radius, padding, the `.kv` two-column grid, the `.k` muted label
colour). It is essentially the `.summary` card without the action row. The
heading reuses the `.summary h4` style.

### Testing

- **Backend (TDD):** `_extract_task_result` is a pure function — add unit tests
  to `tests/test_task_builder_runner.py` covering: a full success block (all
  five fields parsed), a block missing some lines (those fields `None`), and the
  `Competencies Covered:` vs `Competencies:` distinction. Write the test first,
  watch it fail, then implement.
- **Frontend:** manual browser verification (no JS test infrastructure) — run a
  generation to completion and confirm the result card shows all six rows;
  reload the page and confirm the restored transcript shows the same card.

---

## `done` (completed) event — field reference

| Field | Source | Shown in card |
|-------|--------|---------------|
| `task_id` | stage-4 stdout `Task ID:` | Task ID |
| `task_name` | stage-4 stdout `Task Name:` | Name |
| `task_type` | stage-4 stdout `Task Type:` | Type |
| `competencies` | stage-4 stdout `Competencies Covered:` | Competencies |
| `task_url` | stage-4 stdout `GitHub Repository:` | Repository (link) |
| `env` | runner's `env` parameter | Environment |
| `outcome` / `detail` | `_summarise_task_stage` | (heading only) |

## Files touched

| File | Change |
|------|--------|
| `task_builder/runner.py` | `StageEvent` +4 fields; `_extract_task_result` parses 5 lines, returns a dict; `completed` event carries the new fields + `env` |
| `task_builder/static/app.js` | `renderDone` renders a result card on success; `doneBubble` records the new fields; `renderItem` done branch passes them through |
| `task_builder/static/styles.css` | `.result-card` style |
| `tests/test_task_builder_runner.py` | Unit tests for the extended `_extract_task_result` |

## Risks & edge cases

- **Missing lines.** A failed/rejected run does not print the success block;
  `_extract_task_result` returns `None`s and the failed-run display is used —
  unchanged behaviour.
- **Label collision.** `Task Type:` is printed twice and `Competencies:` also
  appears; the extractor matches the exact phrases `Competencies Covered:` and
  takes whichever `Task Type:` line (both hold the same value), so values are
  correct either way.
- **Persistence interaction.** This builds on the not-yet-committed transcript
  persistence feature. The `done` transcript item gains the new fields; restore
  re-renders the full card. No conflict — same `renderDone` path.

## Out of scope

- Gist link, answer-repo link.
- Any `multiagent.py` change.
- Changing the failed-run display.
- Showing these fields anywhere other than the end-of-run result card.
