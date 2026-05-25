# Task Builder — Architecture & File Reference

> Comprehensive guide to the `task_builder/` package: what it is, how the pieces
> fit together, what every file does, the request/SSE data flow, and an
> element-by-element walkthrough of the web UI.
>
> **Scope:** the `task_builder/` package on branch `feat/task-builder`.
> For the design rationale behind the live stage-logs feature see
> [`docs/superpowers/specs/2026-05-19-task-builder-stage-logs-design.md`](superpowers/specs/2026-05-19-task-builder-stage-logs-design.md).

---

## 1. What it is

Task Builder is a **local, single-user web app** that replaces the command-line
task-generation workflow with a conversation. Instead of hand-assembling
competency / background / scenario JSON files and running four CLI tools in
sequence, a hiring engineer:

1. opens a browser at `http://127.0.0.1:8000`,
2. chats with a bot that **interviews them** for the task inputs,
3. clicks **Generate task →**,

and the app runs the full **five-stage pipeline** in a background thread,
streaming each stage's live log output straight into the chat.

It is a thin **conversational front-end + threaded wrapper** around the existing
[`run_pipeline.py`](../run_pipeline.py) linear orchestrator. It reuses that
module's stage helpers (`_run_stage`, `_locate_input_files`, …) but adds two
things on top:

- an **LLM interview** that collects and validates the pipeline inputs, and
- **live per-stage log streaming** over Server-Sent Events (SSE).

There are two phases to every session:

| Phase | Driver | What happens |
|-------|--------|--------------|
| **Interview** | `conversation.py` | The bot fills the `TaskBrief` slots, one topic at a time, validating each value. |
| **Generation** | `runner.py` | The five-stage pipeline runs in a worker thread; logs stream to the browser. |

---

## 2. The big picture

```
┌────────────────────────────────────────────────────────────────────┐
│  Browser   static/index.html + app.js + styles.css                  │
│  ┌─────────────────┐                ┌──────────────────────────┐    │
│  │ Chat UI         │                │ EventSource (SSE client) │    │
│  └────────┬────────┘                └─────────────┬────────────┘    │
└───────────┼───────────────────────────────────────┼─────────────────┘
   POST /api/session                  GET /api/runs/{run_id}/events
   POST /api/chat                                    │
   POST /api/generate                                │
┌───────────▼───────────────────────────────────────▼─────────────────┐
│  FastAPI app   server.py                                             │
│    SESSIONS : dict[session_id -> SessionState]   (in-memory)         │
│    RUNS     : dict[run_id     -> queue.Queue[StageEvent]] (in-memory)│
└────┬──────────────────────────────────────────┬─────────────────────┘
     │ chat turn                                 │ generate
┌────▼────────────────────────┐   ┌──────────────▼──────────────────────┐
│ conversation.py             │   │ runner.py   (daemon worker thread)   │
│   apply_turn()              │   │   run_pipeline_for_brief()           │
│     run_turn()  ── LLM call │   │     _stage()  ×5                     │
│     _clean_slots_update()   │   │       StageLogTailer  (log_tail.py)  │
│       └─ validation.py      │   │       _run_stage()  (run_pipeline.py)│
│     merge_brief()           │   └──────────────┬───────────────────────┘
└────┬────────────────────────┘                  │  one subprocess per stage
     │                                  ┌─────────▼──────────────────────┐
┌────▼─────────────────┐                │ 00_preflight → 01_input_files →│
│ Portkey → Claude API │                │ 02_scenarios → 03_prompt →     │
│ Supabase (dev)       │                │ 04_tasks                       │
└──────────────────────┘                └────────────────────────────────┘
```

**Two in-memory registries** in `server.py` hold all state:

- `SESSIONS` — one `SessionState` per conversation (brief + chat history).
- `RUNS` — one thread-safe `queue.Queue` per pipeline run; the worker thread
  pushes `StageEvent`s onto it, the SSE endpoint drains it.

Both are plain dicts with no eviction and no persistence — they are lost on
server restart, which is acceptable for a local single-user tool.

---

## 3. File-by-file reference

The package is **9 Python modules** + **3 static front-end files**.

| File | Lines¹ | Responsibility |
|------|-------|----------------|
| `__init__.py` | 1 | Package marker / docstring. |
| `__main__.py` | 5 | Entry point — launches the uvicorn server. |
| `server.py` | ~137 | FastAPI app: HTTP routes, session/run registries, SSE stream. |
| `conversation.py` | ~194 | The interview engine — one LLM call per turn, structured-JSON output. |
| `slots.py` | ~54 | `TaskBrief` data model + `SessionState` + `merge_brief`. |
| `validation.py` | ~66 | Validates slot values (proficiency enum, competency vs Supabase). |
| `prompts.py` | ~33 | The bot's system prompt (the interview contract). |
| `runner.py` | ~147 | Runs the five-stage pipeline, emits a `StageEvent` per stage. |
| `log_tail.py` | ~86 | `StageLogTailer` — background thread that tails stage log files. |
| `static/index.html` | 26 | Page skeleton: header, chat area, input dock. |
| `static/app.js` | ~153 | Chat client: talks to the API, renders bubbles, consumes SSE. |
| `static/styles.css` | ~99 | Styling for chat, summary card, collapsible log panels. |

¹ Approximate.

---

### 3.1 `__init__.py`

```python
"""Task Builder — conversational web front-end for the task-generation pipeline."""
```

Just the package marker. No exports.

---

### 3.2 `__main__.py`

Makes the package runnable with `python -m task_builder`:

```python
import uvicorn
if __name__ == "__main__":
    uvicorn.run("task_builder.server:app", host="127.0.0.1", port=8000, reload=False)
```

- Binds to **`127.0.0.1`** only — the app is deliberately not reachable from
  other machines.
- `reload=False` — it is a tool, not a dev server.

---

### 3.3 `server.py` — the FastAPI app

The HTTP surface. Defines `app = FastAPI(title="Task Builder")`, mounts the
`static/` directory, and holds the two in-memory registries.

**Registries**

```python
SESSIONS: dict[str, SessionState]            # session_id -> conversation state
RUNS:     dict[str, queue.Queue[StageEvent]] # run_id     -> event queue
```

**Routes**

| Method & path | Purpose |
|---------------|---------|
| `GET /` | Serves `static/index.html`. |
| `GET /api/health` | Liveness check — returns `{"status": "ok"}`. |
| `POST /api/session` | Starts a conversation. Mints a `session_id`, stores a fresh `SessionState`, returns the bot's hard-coded greeting. |
| `POST /api/chat` | Runs **one** conversation turn for a session (body: `session_id`, `message`). Delegates to `conversation.apply_turn`. Returns `reply`, the full `brief`, `missing_slots`, and `ready`. |
| `POST /api/generate` | Starts a pipeline run for a session whose brief `is_complete()`. Body: `session_id`, `env` (`dev`/`prod`). Mints a `run_id`, launches the worker thread, returns `{run_id}`. |
| `GET /api/runs/{run_id}/events` | **SSE** stream of `StageEvent`s for a run. |

**Key behaviours**

- `_launch_run()` creates a `queue.Queue`, registers it under the `run_id`, and
  starts a **daemon thread** running `run_pipeline_for_brief`, wiring the
  queue's `.put` as the `emit` callback. The pipeline therefore runs entirely
  off the request thread.
- `chat()` builds a **fresh** bot client and Supabase client per call
  (`build_bot_client()`, `get_supabase()`).
- `get_supabase()` is hard-wired to the **`dev`** environment — competency
  validation always hits dev Supabase, even when generation later targets
  `prod` (see [§8 Gotchas](#8-known-limitations--gotchas)).
- The SSE generator `event_source()` runs the **blocking** `queue.get()` inside
  `loop.run_in_executor(...)` so the asyncio event loop is never blocked. It
  JSON-encodes each event with `dataclasses.asdict(event)`, and **breaks the
  loop when `event.stage == "done"`**, then pops the run from `RUNS`.
- `generate()` validates the `env` value and rejects an incomplete brief with
  HTTP 400; an unknown session is HTTP 404.

---

### 3.4 `conversation.py` — the interview engine

This is the heart of the **interview phase**. The design is called *Approach B*:
**one LLM call per turn that returns structured JSON**, rather than tool-calls or
a multi-agent loop.

**The output contract.** Every bot response must be a single JSON object:

```json
{
  "reply": "<message shown to the user>",
  "slots_update": { "<slots learned this turn>": <value> },
  "ready_to_generate": true | false
}
```

**Functions**

- `build_bot_client()` — builds an `openai.OpenAI` client pointed at the
  **Portkey gateway** with `provider="anthropic"`, mirroring `multiagent.py`.
  The model is `BOT_MODEL = "claude-sonnet-4-6"`.
- `_extract_json(text)` — pulls the **first top-level JSON object** out of an LLM
  response by brace-depth matching. Tolerates prose around the JSON; raises
  `ValueError` if none / unbalanced.
- `_to_turn(parsed)` — converts a parsed dict into a frozen `ConversationTurn`,
  defaulting every field (an empty `reply` becomes the canned fallback).
- `_call(client, messages)` — one chat-completion call, returns raw text.
- `run_turn(client, history, user_message)` — runs one turn:
  1. Build `messages` = system prompt + history + the new user message.
  2. Call the LLM, try to parse the JSON.
  3. **On unparseable JSON, retry once** — the bad reply is inserted as an
     `assistant` message and a corrective `user` nudge is appended (roles must
     alternate; the Anthropic API rejects two consecutive `user` messages).
  4. If the retry also fails, **degrade gracefully** to a fallback
     `ConversationTurn` instead of raising.
- `_clean_slots_update(update, supabase, current_proficiency)` — **validates a
  raw `slots_update` before anything is stored.** Returns
  `(accepted_fields, rejection_messages)`:
  - `proficiency` → `validate_proficiency`.
  - `competencies` → each name → `validate_competency`. Needs a proficiency:
    prefers the one accepted this turn, falls back to the session's existing
    proficiency (so a stack named *after* the level is still accepted). Bad
    names produce a rejection message with up to 5 "did you mean" suggestions.
  - `role`, `domain` → trimmed strings.
  - `focus_areas` → list of trimmed non-empty strings.
  - `scenario_count` → only accepted if a positive `int` (and not a `bool`).
  - **Rejected fields are dropped** — the server never stores an unvalidated
    value.
- `apply_turn(session, user_message, *, client, supabase)` — the full turn the
  `/api/chat` route calls:
  1. `run_turn()` → a `ConversationTurn`.
  2. `_clean_slots_update()` → accepted fields + rejections.
  3. `merge_brief()` → the session brief is replaced with a new, merged copy.
  4. **If anything was rejected**, run one **corrective turn**: the rejection
     messages are appended to the user message as a `SERVER VALIDATION:` note so
     the re-ask reaches the user inside the *same* HTTP response.
  5. Append the user message and the final reply to `session.history`.
  6. Return a `ChatResult` (`reply`, `brief`, `missing_slots`, `ready`).
  `ready = turn.ready_to_generate AND no missing slots` — the server has the
  final say; the LLM cannot force generation with an incomplete brief.

**Data classes:** `ConversationTurn` (frozen — one parsed bot turn) and
`ChatResult` (the result handed back to the route).

---

### 3.5 `slots.py` — the brief data model

Defines the **`TaskBrief`** — the interview answers, owned authoritatively by
the server (the LLM only *proposes* updates).

```python
class TaskBrief(BaseModel):
    competencies:   list[str]  = []
    proficiency:    str | None = None
    role:           str | None = None
    focus_areas:    list[str]  = []
    domain:         str | None = None
    scenario_count: int        = 6
```

- `REQUIRED_SLOTS` = `competencies, proficiency, role, focus_areas, domain` —
  **five** slots. `scenario_count` is **not** required (it defaults to `6` and
  the bot is told never to ask about it).
- `VALID_PROFICIENCIES` = `BEGINNER, BASIC, INTERMEDIATE, ADVANCED`.
- `missing_slots()` → required slots still empty, in canonical order.
- `is_complete()` → `not missing_slots()`.
- `merge_brief(brief, update)` → returns a **new** `TaskBrief` with `update`'s
  known fields applied; never mutates (immutable update via `model_copy`).

> **Note on "six slots".** The README mentions six slots; precisely, there are
> **five interview slots** the bot asks about plus `scenario_count`, which is an
> auto-defaulted field the user never sees.

**Also defined:** `Message` (a `role`/`content` chat turn) and `SessionState`
(`session_id` + `brief` + `history`) — the per-conversation in-memory state.

---

### 3.6 `validation.py` — slot validation against real data

Ensures a slot value is real **before** it enters the brief.

- `SlotValidation` — frozen result: `ok`, `cleaned`, `error`, `suggestions`.
- `validate_proficiency(value)` — upper-cases and checks against
  `VALID_PROFICIENCIES`; on miss, the error lists the valid choices.
- `validate_competency(name, proficiency, supabase)` — queries the Supabase
  `competencies` table for a row matching `name` (case-insensitive `ilike`) at
  the given `proficiency`. On a **miss**, fetches all distinct competency names
  and uses `difflib.get_close_matches` (`n=5`, `cutoff=0.5`) to offer close
  spellings — these become the bot's "did you mean" suggestions.

---

### 3.7 `prompts.py` — the bot's system prompt

A single `SYSTEM_PROMPT` string. It is the **interview contract**, telling the
LLM:

- the five slots it collects and their shapes;
- to ask about **missing** slots one topic at a time, concisely and warmly;
- **never** to ask the user how many scenarios/tasks to generate (that is
  automatic) and never to claim generation has started or finished;
- to set `ready_to_generate: true` **only** when all five slots are filled, and
  to summarise + ask for confirmation first;
- to apologise and re-ask, offering suggestions, when the server reports an
  unknown competency;
- the strict **JSON-only output contract** (no markdown, no code fences).

---

### 3.8 `runner.py` — the five-stage pipeline runner

Drives the **generation phase**. Executes the pipeline for a `TaskBrief` and
calls an `emit` callback with a `StageEvent` before and after each stage.

**`StageEvent`** (frozen dataclass) — the unit streamed to the browser:

| Field | Meaning |
|-------|---------|
| `stage` | A `STAGES` label, or `"done"` for the terminal event. |
| `status` | `running` / `ok` / `failed` / `completed`, or `log` for a live chunk. |
| `detail` | Free text — an error, an outcome, or a chunk of log output. |
| `duration_s` | Stage wall-clock time (on `ok`/`failed`). |
| `outcome` | Stage-4 classification string. |
| `task_id`, `task_url` | Set on a successful `done` event. |

**`STAGES`** = `00_preflight, 01_input_files, 02_scenarios, 03_prompt, 04_tasks`.

**`run_pipeline_for_brief(brief, *, run_id, emit, env, runs_root)`**

1. Picks the Python interpreter (`_pick_python` — prefers the project venv).
2. Creates a per-run log directory: `.task_agent_runs/web-<UTC-timestamp>-<run_id>/`.
3. Walks the five stages via the inner `_stage()` closure.
4. **Stops at the first failing stage** and always emits a terminal `"done"`
   event (`completed` or `failed`).
5. Any unexpected exception is caught and surfaced as a `failed` `done` event —
   a stage crash never kills the worker thread silently.

**The `_stage(label, cmd)` closure** — this is where live logs come from:

```
emit(running)
  → StageLogTailer.start()          # tails <label>.stdout + <label>.stderr
    → _run_stage()                  # blocks: runs the stage subprocess
  → StageLogTailer.stop()           # final flush of log files
emit(ok | failed)                   # with duration_s
```

The tailer's callback wraps each new chunk as
`StageEvent(stage=label, status="log", detail=chunk)`, so per-stage event order
is always **`running → log… → ok/failed`**.

**Per stage**

| Stage | Command | Notes |
|-------|---------|-------|
| `00_preflight` | `task_agent_preflight.py --combo "<names>:<LEVEL>" --env <env>` | Sanity-checks the combo before doing expensive work. |
| `01_input_files` | `python -m generate_input_files --competency-name … --proficiency … --role … --env …` | Writes competency + background JSON. |
| *(locate)* | `_locate_input_files()` | Finds the JSON files stage 1 just produced. |
| `02_scenarios` | `python -m scenario_generator --competency-file … --background-file … --count … --append` + `--focus-areas` / `--domain` | `focus_areas` and `domain` from the brief are threaded in. |
| `03_prompt` | `python -m prompt_generator --name … --proficiency … --env … --force --verbose` | Synthesises the tech-specific task prompt. |
| `04_tasks` | `python multiagent.py generate_tasks -c … -b … -s … --env <env>` | The actual task creation. `--env` **must** be threaded so a `prod` run stores in prod. |

**Outcome handling**

- `_summarise_task_stage()` (imported from `run_pipeline.py`) reads stage-4
  stdout and classifies it: `TASK CREATED` / `EVAL GATE REJECTED` / `ERROR` /
  `UNKNOWN`.
- The `done` event is `failed` if the exit code is non-zero **or** the outcome
  contains `REJECTED` / `ERROR` / `UNKNOWN` — i.e. a task that compiles but is
  rejected by the eval gate is still reported as a failure.
- `_extract_task_result()` scrapes `Task ID:` and `GitHub Repository:` lines
  from stage-4 stdout to populate `task_id` / `task_url` on success.

---

### 3.9 `log_tail.py` — live log tailing

`StageLogTailer` makes the per-stage logs appear **while the stage runs**,
instead of only after it finishes.

- Constructed with a list of file paths, an `emit` callback, and a poll
  interval (`interval_s`, default **0.5 s**).
- `start()` spins up a **daemon thread**; `stop()` signals it and joins.
- Each poll, `_drain()` calls `_read_new(path)` for every file:
  - tracks a **per-path byte offset**, `seek`s to it, reads the appended bytes;
  - decodes `utf-8` with `errors="replace"` (a chunk boundary may fall
    mid-line — harmless, chunks are concatenated downstream);
  - a not-yet-created file simply yields an empty read.
- The run loop uses `Event.wait(interval)` so `stop()` exits it promptly, and it
  performs **one final `_drain()`** after stopping — so block-buffered output
  flushed at subprocess exit is never lost.

This module needed **no changes to `server.py`** — the tailer rides the existing
SSE event queue by emitting ordinary `StageEvent`s with `status="log"`.

---

### 3.10 `static/index.html` — the page skeleton

A minimal single page:

- `<header>` — a square logo block + the `Task Builder` title.
- `<main><div class="chat" id="chat"></div></main>` — the scrolling message
  area; every bubble is appended here by `app.js`.
- `.dock` — a fixed bottom bar with the text `<input id="msg">` and the
  `<button id="send">`.
- Loads Google Fonts (Inter + Roboto), `styles.css`, and `app.js`.

No content is server-rendered — the page is an empty shell that `app.js` fills.

---

### 3.11 `static/app.js` — the chat client

All browser-side logic. ~150 lines, no framework, no build step.

**State:** `sessionId`, and a `busy` flag that blocks overlapping sends.

**Functions**

- `bubble(role, text, cls)` — creates one chat row (avatar + bubble), appends it
  to `#chat`, scrolls it into view, and returns the bubble element so callers
  can mutate it later. User text goes in via `textContent` (XSS-safe).
- `summaryCard(brief)` — renders the **task-brief card**: a key/value grid of
  the five slots, an **environment `<select>`** (`dev`/`prod`), and the
  **Generate task →** button wired to `startGeneration`.
- `startSession()` — `POST /api/session` on page load; shows the greeting, or a
  connection-error bubble if the backend is down.
- `send()` — reads the input, shows the user bubble + a `…` placeholder,
  `POST /api/chat`, replaces the placeholder with the reply. **If
  `data.ready`**, also renders the summary card.
- `startGeneration()` — disables the button + env picker, `POST /api/generate`,
  then hands the returned `run_id` to `streamRun`.
- `stagePanel(panels, label)` — lazily creates one **collapsible
  `<details>` panel** per stage (a `<summary>` line + a `<pre class="log">`).
- `doneBubble(e)` — the terminal bubble: the outcome text, plus a clickable
  repo link on success.
- `streamRun(runId)` — opens an `EventSource` on
  `/api/runs/{runId}/events` and maps each event to UI:

  | `status` | UI effect |
  |----------|-----------|
  | `running` | open the panel, summary `⏳ <stage>` |
  | `log` | append `detail` to the `<pre>`, auto-scroll to bottom |
  | `ok` | summary `✓ <stage> · <n>s`, **collapse** the panel |
  | `failed` | summary `✗ <stage> <detail>`, **stay expanded** |
  | `stage === "done"` | render `doneBubble`, close the stream |

**Bootstrap:** wires the Send button + Enter key, then calls `startSession()`.

---

### 3.12 `static/styles.css` — styling

A small, dependency-free stylesheet. A light theme driven by CSS custom
properties (`--bg`, `--panel`, `--border`, `--text`, `--muted`, …). Notable
pieces:

- **Chat bubbles** — `.row.user` right-aligned dark bubbles, `.row.bot`
  left-aligned light bubbles, each with a round avatar (`Y` for you, `U` for
  the bot).
- **`.stage`** — pipeline/status lines in Roboto, monochrome; `.stage.failed`
  is bold.
- **`.summary`** — the bordered task-brief card; `.kv` is a two-column grid;
  `.cta` is the dark Generate button; `.actions` / `.env-pick` lay out the env
  selector next to it.
- **`.stage-log`** — the collapsible panels: a full-width `<details>` with a
  custom ▸/▾ disclosure triangle and a scrollable monospace `<pre class="log">`
  (max-height 240 px). An empty `<pre>` is hidden.
- **`.dock`** — the fixed bottom input bar with a gradient fade behind it.

---

## 4. End-to-end data flow

### 4.1 Interview phase (one chat turn)

```
Browser                 server.py            conversation.py        external
   │  POST /api/chat        │                      │                   │
   ├───────────────────────▶│                      │                   │
   │                        │  apply_turn()        │                   │
   │                        ├─────────────────────▶│                   │
   │                        │                      │ run_turn() ───────▶ Claude (Portkey)
   │                        │                      │◀──────────────────┤ JSON turn
   │                        │                      │ _clean_slots_update()
   │                        │                      │   validate_competency ─▶ Supabase (dev)
   │                        │                      │ merge_brief()      │
   │                        │                      │ (corrective turn if rejected)
   │                        │◀─────────────────────┤ ChatResult         │
   │  {reply, brief,        │                      │                   │
   │   missing_slots, ready}│                      │                   │
   │◀───────────────────────┤                      │                   │
```

When `ready` is `true`, `app.js` renders the summary card and the user clicks
**Generate**.

### 4.2 Generation phase (SSE)

```
Browser              server.py           worker thread (runner.py)
   │ POST /api/generate   │                      │
   ├─────────────────────▶│ _launch_run()        │
   │                      ├─ queue.Queue ────────┤ run_pipeline_for_brief()
   │  {run_id}            │  RUNS[run_id]=q       │
   │◀─────────────────────┤                      │
   │ GET /api/runs/{id}/events (EventSource)      │
   ├─────────────────────▶│                      │
   │                      │  q.get() in executor │  _stage("00_preflight")
   │                      │◀─────────────────────┤  emit(running)
   │  data: {running}     │                      │  StageLogTailer →
   │◀─────────────────────┤◀─────────────────────┤  emit(log) ×N
   │  data: {log} ×N      │                      │  emit(ok)
   │◀─────────────────────┤◀─────────────────────┤   … stages 01–04 …
   │  data: {done}        │◀─────────────────────┤  emit(done)
   │◀─────────────────────┤  break; RUNS.pop()   │
```

The SSE stream is one-way; the queue decouples the synchronous worker thread
from the async HTTP response.

---

## 5. The web UI, element by element

```
┌──────────────────────────────────────────────────────────┐
│ ▪ Task Builder                                  ← header  │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  U  Hi! I'll help you put together a coding assessment…    │  ← bot bubble
│                                                            │
│                          What tech stack…?  Y             │  ← user bubble
│                                                            │
│  U  Great — what proficiency level?                        │
│                                                            │
│  ┌──────────────────────────────────────────────┐         │
│  │ Task brief                                    │         │  ← summary card
│  │ Tech stack   Java, Spring Boot                │         │    (appears when
│  │ Proficiency  INTERMEDIATE                     │         │     ready === true)
│  │ Role         Backend engineer                 │         │
│  │ Focus areas  idempotency, retries             │         │
│  │ Domain       fintech payments                 │         │
│  │ Environment [dev ▾]      [ Generate task → ]  │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  ▾ ✓ 01_input_files · 12.4s                                │  ← collapsible
│  ┌──────────────────────────────────────────────┐         │    stage-log panel
│  │ wrote competency_java_spring_boot…json        │         │
│  │ wrote background_…json                        │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  ⏳ 04_tasks            (running — auto-expanded)           │
│                                                            │
├──────────────────────────────────────────────────────────┤
│  [ Type a message…                          ] [ Send ]    │  ← input dock
└──────────────────────────────────────────────────────────┘
```

| Element | Behaviour |
|---------|-----------|
| **Header** | Static title bar. |
| **Bot / user bubbles** | Plain conversation. The bot bubble shows `…` while a turn is in flight, then is replaced in place with the reply. |
| **Summary card** | Appears once the brief is complete (`ready`). Shows the five slots, an environment picker, and the Generate button. |
| **Environment picker** | `dev` or `prod` — passed to `/api/generate`; selects which Supabase the **task storage** (stage 4) uses. Disabled once generation starts. |
| **Generate task →** | Starts the run; disables itself; opens the SSE stream. |
| **Stage-log panel** | One collapsible `<details>` per stage. The **running** stage auto-expands; on `ok` it collapses to a one-line `✓` summary with a duration; a **failed** stage stays expanded. |
| **Done bubble** | Final outcome line; on success it includes a clickable link to the generated GitHub repo. |
| **Input dock** | Text input + Send. Enter also sends. Overlapping sends are blocked by the `busy` flag. |

---

## 6. HTTP API reference

| Endpoint | Request body | Response |
|----------|--------------|----------|
| `GET /` | — | `index.html` |
| `GET /api/health` | — | `{"status": "ok"}` |
| `POST /api/session` | — | `{"session_id", "reply"}` |
| `POST /api/chat` | `{"session_id", "message"}` | `{"reply", "brief", "missing_slots", "ready"}` |
| `POST /api/generate` | `{"session_id", "env"}` | `{"run_id"}` |
| `GET /api/runs/{run_id}/events` | — | SSE stream of JSON `StageEvent`s |

**Error responses:** `404` for an unknown `session_id` / `run_id`; `400` for an
incomplete brief or an `env` that is not `dev`/`prod`.

---

## 7. Running it

```bash
.venv/bin/python -m task_builder
# then open http://127.0.0.1:8000
```

**Required environment variables** (in `.env`):

| Variable | Used by |
|----------|---------|
| `ANTHROPIC_API_KEY` | the conversational bot (the API key Portkey forwards) |
| `PORTKEY_API_KEY` | the Portkey gateway |
| `SUPABASE_URL_APTITUDETESTSDEV`, `SUPABASE_API_KEY_APTITUDETESTSDEV` | competency validation (dev) |
| *everything the pipeline stages need* | preflight, input files, scenarios, prompt, tasks — see `TASK_MANAGEMENT_GUIDE.md` |

---

## 8. Known limitations & gotchas

- **State is in-memory and unbounded.** `SESSIONS` and `RUNS` are plain dicts
  with no eviction and no persistence — everything is lost on restart. Fine for
  a local single-user tool; not safe for multi-user or long-running deployment.
- **Competency validation is always `dev`.** `get_supabase()` is hard-wired to
  the dev environment. A user can pick `prod` in the summary card for *task
  storage*, but the competency they were validated against came from dev. If
  dev and prod competency tables diverge, a `prod` run can hit a competency the
  interview accepted.
- **Chat is synchronous.** Each `/api/chat` call makes 1–2 blocking LLM calls
  on the request thread (a second one whenever a value is rejected).
- **The LLM proposes, the server disposes.** The bot can set
  `ready_to_generate`, but `apply_turn` only reports `ready` when the brief is
  genuinely complete, and `/api/generate` independently re-checks
  `brief.is_complete()`. An unvalidated slot value is never stored.
- **`scenario_count` is not interviewed.** It defaults to `6`; the prompt
  forbids the bot from asking about it.
- **Eval-gate rejections count as failures.** A stage-4 task that is generated
  but rejected by the eval gate produces a `failed` `done` event, not a partial
  success.

---

## 9. Tests

The package is covered by seven test modules under `tests/`:

| Test file | Covers |
|-----------|--------|
| `test_task_builder_conversation.py` | turn parsing, JSON extraction, validation, corrective turns |
| `test_task_builder_slots.py` | `TaskBrief` completeness, `merge_brief` immutability |
| `test_task_builder_validation.py` | proficiency + competency validation, suggestions |
| `test_task_builder_runner.py` | five-stage ordering, failure short-circuit, outcome classification |
| `test_task_builder_log_tail.py` | tailer emits appended content, final flush, missing-file tolerance |
| `test_task_builder_server.py` | route behaviour, session/run registries, error codes |
| `test_task_builder_integration.py` | end-to-end interview → generate flow |

---

## 10. Relationship to `run_pipeline.py`

Task Builder does **not** re-implement the pipeline. `runner.py` imports the
stage helpers directly from [`run_pipeline.py`](../run_pipeline.py):

| Imported | Role |
|----------|------|
| `REPO_ROOT`, `RUNS_DIR`, `SCENARIOS_FILE` | paths |
| `_pick_python` | choose the interpreter for subprocess stages |
| `_run_stage` | run one stage as a subprocess, capture stdout/stderr/timing |
| `_locate_input_files` | find the JSON files stage 1 produced |
| `_summarise_task_stage` | classify the stage-4 outcome |

The difference is the **stage loop**: `run_pipeline.py` `print`s progress to a
terminal; Task Builder's `runner.py` re-implements the loop to (a) emit
`StageEvent`s and (b) attach a `StageLogTailer` for live streaming. Everything
below the stage loop — the subprocess execution, the log files under
`.task_agent_runs/`, the outcome classification — is shared.

> `run_pipeline.py` is a plain **linear** orchestrator: no coordinator agent, no
> per-stage verifier agents, no prompt-level escalation. The "smart" autonomous
> version is a separate Phase-2 design
> (`docs/autonomous-task-agent/`).
