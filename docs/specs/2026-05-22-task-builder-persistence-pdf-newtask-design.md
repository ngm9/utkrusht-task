# Task Builder — Session Persistence, PDF Export & New-Task Reset

**Date:** 2026-05-22
**Status:** Approved
**Scope:** `task_builder/static/` only — frontend-only change, no backend changes.

## Problem

The Task Builder web UI is fully ephemeral. A page refresh wipes the visible
conversation; there is no way to keep a record of a generated task off-screen;
and there is no way to start a clean conversation without restarting the server
or hand-clearing the page. Three small features close those gaps.

## Goals

1. **Persist the conversation** to `localStorage` so a page refresh re-displays
   it (read-only).
2. **Download the session as a PDF** — conversation, brief, outcome, and stage
   logs.
3. **"New task" button** — discard the current conversation and start fresh.

## Non-goals

- Resuming a live session after refresh. The server's `SESSIONS` store is
  in-memory; a persisted `session_id` may be dead. Restored content is therefore
  **read-only** and a refresh always starts a fresh chat session.
- Any backend / `server.py` change.
- A JS test framework (none exists in the project today).
- Server-side PDF rendering or a bundled PDF library.

## Decisions (from brainstorming)

- **State scope:** transcript-only restore — re-render the conversation for
  viewing; always start a fresh session for further chatting.
- **PDF approach:** browser print-to-PDF (`window.print()` + a print
  stylesheet). Zero new dependencies.
- **PDF content:** everything visible — conversation + brief card + final
  outcome + stage logs (force-expanded for print).
- **New task:** confirm before clearing.

---

## Feature 1 — `localStorage` session persistence

### Transcript model

`app.js` gains a module-level `transcript` array that mirrors everything in the
chat area. Each entry is a plain serializable object:

| `kind` | Fields | Represents |
|--------|--------|------------|
| `bubble` | `role` (`"user"`/`"bot"`), `text`, `cls` | One chat bubble |
| `divider` | `text` | A `— new session —` separator inserted on restore |
| `summary` | `brief` (the full brief object) | The task-brief card |
| `stage` | `label`, `summary`, `log`, `status` | One stage-log panel (snapshot) |
| `done` | `status`, `outcome`, `detail`, `task_url` | The terminal outcome bubble |

Rules:

- Every render path (`bubble`, `summaryCard`, `stagePanel` updates, `doneBubble`)
  also appends or updates the matching `transcript` entry.
- `stage` entries are keyed by `label` and **updated in place** as the stage
  progresses (`running` → `log…` → `ok`/`failed`), not appended repeatedly.
- After a mutation, `saveTranscript()` writes
  `localStorage["taskbuilder.transcript"]` as JSON. Saves during log streaming
  are **debounced (~500 ms)** so rapid `log` events don't hammer `localStorage`.
- `saveTranscript()` wraps `setItem` in `try/catch`; on a quota error it logs a
  `console.warn` and stops persisting for the rest of that session. The
  in-memory transcript and the on-screen UI are unaffected.

### Restore behaviour (on page load)

1. `loadTranscript()` reads and parses the saved JSON. Corrupt/absent data → no
   restore.
2. If a transcript was restored, each entry is re-rendered as **static,
   read-only** content:
   - `bubble` — a plain bubble, text via `textContent` (XSS-safe).
   - `summary` — the brief card showing its values, but **without** the
     environment picker and Generate button (that session is gone). Brief values
     are written via `textContent`, not `innerHTML` interpolation.
   - `stage` — a static `<details>` panel with its captured summary line and log
     text; collapsed when the stored `status` is `ok`, expanded otherwise
     (matching the live collapse rule).
   - `done` — the outcome bubble; its repo `<a>` link is kept (harmless).
3. A `divider` entry (`— new session —`) is appended, persisted, and rendered.
4. `startSession()` runs as normal, fetching a fresh `session_id` + greeting,
   which appends below the divider.
5. The fresh session continues appending to the **same** `transcript` array, so
   `localStorage` always mirrors the screen.

If there is no saved transcript (first visit, or after "New task"), load
proceeds straight to `startSession()` with no divider.

---

## Feature 2 — Download PDF

### Trigger

A **Download PDF** button in the header. Its handler:

1. Snapshots the `open` state of every stage-log `<details>` panel.
2. Sets `open = true` on all of them (so logs are visible to the print
   renderer).
3. Fills a print-only header element with the current date.
4. Calls `window.print()`.
5. On the `afterprint` event, restores the snapshotted `open` states.

The user chooses "Save as PDF" as the destination in the browser print dialog.

### Print stylesheet

A new `@media print` block in `styles.css`:

- Hides non-content chrome: `header` buttons and the input `.dock`.
- Reveals stage-log content regardless of panel state
  (`.stage-log details > *:not(summary) { display: block !important }`) as a
  belt-and-braces complement to the JS force-open.
- Bubbles render full-width with `page-break-inside: avoid`; fixed/sticky
  positioning is removed so content flows across pages.
- Shows a print-only `.print-head` element (hidden on screen) with
  `Task Builder — <date>`.

---

## Feature 3 — "New task" button

A **New task** button in the header. Its handler:

1. `confirm("Discard this conversation and start a new task?")`.
2. On confirm:
   - clears the `#chat` DOM,
   - empties the `transcript` array,
   - `localStorage.removeItem("taskbuilder.transcript")`,
   - resets `sessionId` to `null` and `busy` to `false`,
   - calls `startSession()` for a fresh session.

**Edge case:** if clicked while a generation run is streaming, the UI resets but
the server-side worker thread and pipeline run continue to completion (the task
is still created). This is acceptable; the confirm dialog is the safety net.

---

## Header layout

The header (`logo` + `h1`) gains a right-aligned action group:

```
[ logo ]  Task Builder            [ New task ]  [ Download PDF ]
```

A `.header-actions` flex container with `margin-left: auto`. Buttons reuse the
dark button styling of the existing `.cta`, sized smaller. Both buttons are
always enabled.

---

## Files touched

| File | Change |
|------|--------|
| `task_builder/static/index.html` | Add the two header buttons + a `.print-head` element |
| `task_builder/static/app.js` | `transcript` model; `saveTranscript`/`loadTranscript`/restore rendering; `downloadPdf` and `newTask` handlers; record into `transcript` from every render path |
| `task_builder/static/styles.css` | `.header-actions` + header button styles; `@media print` block; `.print-head` |

`task_builder/server.py` and the rest of the backend are **unchanged**.

## Testing

The project has no JavaScript test infrastructure (tests are Python/pytest,
backend-only). These features are pure frontend. Verification is **manual**:

1. **Persistence:** hold a conversation, refresh — the transcript re-renders
   read-only, a `— new session —` divider appears, a fresh greeting follows.
2. **Read-only restore:** a restored brief card shows values but no Generate
   button.
3. **PDF:** click Download PDF → print preview shows conversation + brief +
   outcome + fully-expanded stage logs; header buttons and input dock are
   absent; on-screen panel states are unchanged afterwards.
4. **New task:** click → confirm → chat clears, `localStorage` key is gone, a
   fresh session greeting appears. Cancel → nothing changes.
5. **Quota guard:** persistence failure (simulated) does not break the UI.

## Risks & edge cases

- **localStorage quota.** Long stage-log dumps can be large (~MB). Mitigation:
  `try/catch` + graceful stop-persisting, per Feature 1.
- **Divider accumulation.** Each refresh adds one `divider`. This is truthful
  (it marks reload boundaries) and bounded by how often the user reloads;
  accepted.
- **New task during an active run.** Documented above; accepted.
- **Print rendering varies by browser.** The print stylesheet targets the
  common case; exact pagination is browser-dependent and not pixel-controlled.

## Out of scope

- Live session resume across refresh / server restart.
- Multi-session history or a session list.
- Exporting formats other than PDF (e.g. Markdown, JSON).
