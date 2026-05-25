# Task Builder — Conversational Web Front-End for the Task-Generation Pipeline

**Status:** Design approved 2026-05-18 · pending implementation plan
**Relates to:** the static mockup `chat_flow_mockup.html`; `run_pipeline.py` (linear orchestrator);
the autonomous-task-agent design (`docs/autonomous-task-agent/`).

---

## 1. Problem & goal

The task-generation pipeline is four CLI stages:

```
generate_input_files → scenario_generator → prompt_generator → multiagent.py generate_tasks
```

Today it is driven by hand, or by `run_pipeline.py` (a linear chainer). Operating it
requires knowing exact competency names, the proficiency enum, and how to pass JSON
file paths between stages. That is fine for an engineer; it is a wall for anyone else.

**Goal:** a conversational web app that interviews the user for the pipeline inputs in
plain language, validates every answer against real data (Supabase competencies, the
proficiency enum), shows a confirmable brief, then runs the pipeline with live
per-stage progress streamed back into the chat.

A static mockup (`chat_flow_mockup.html`) established the desired UX. This spec turns
that mockup into a real, integrated system.

---

## 2. Decisions locked in brainstorming (2026-05-18)

| Fork | Decision |
|---|---|
| Interview surface | **Web app** (not a terminal wizard) |
| Interaction model | **Fully conversational bot** — LLM asks the questions in natural language |
| Deployment scope | **Local internal tool** — `localhost`, single user, no auth |
| Focus-areas / domain plumbing | **Real parameters** threaded into `scenario_generator` |
| Run progress | **Live per-stage streaming** into the chat |
| Conversation engine | **Approach B — structured-output slot-filling** (one LLM call/turn returning strict JSON) |

---

## 3. Gap analysis — mockup vs. current pipeline

| Mockup question | Real pipeline input | Status |
|---|---|---|
| Q1 · Tech stack | `generate_input_files --competency-name` | exists |
| Q2 · Proficiency | `generate_input_files --proficiency` | exists |
| Q3 · Role description | `generate_input_files --role` → `role_context` | exists |
| Q4 · What to assess (focus areas) | *nothing* | **no parameter — Layer B adds it** |
| Q5 · Company domain | *nothing* | **no parameter — Layer B adds it** |
| Q6 · Confirm & generate | `run_pipeline.py` chains the four stages | exists (linear) |

Two specifics that justify Layer B:

- **Q4 (focus areas)** has no input today. `scenario_generator` derives *what gets
  assessed* from `questions_prompt`, and that string is LLM-generated from the
  competency `long_scope` in `generate_input_files/generator.py`. The user never picks
  the focus — the LLM infers it.
- **Q5 (domain)** is the *opposite* of current behaviour. The scenario prompt at
  `scenario_generator/prompts.py:308` hard-codes *"Each scenario MUST use a DIFFERENT
  business domain"* — it deliberately spreads scenarios across industries. The mockup
  wants the user to **pin one domain**. Supporting Q5 means a parameter that overrides
  that variety rule.

---

## 4. Scope

### In scope (v1)

- A new `task_builder/` package: FastAPI server + static front-end.
- A fully conversational slot-filling bot collecting a six-field `TaskBrief`.
- Server-owned, validated brief state; competency validation against Supabase.
- A background pipeline runner reusing the existing four CLI stages, with per-stage
  events streamed over SSE.
- **Layer B** — real `focus_areas` and `domain` parameters in `scenario_generator`.
- pytest coverage consistent with the existing suite.

### Out of scope (v1) — YAGNI

- No auth, no multi-user — it is a local tool.
- No persistence across server restarts — in-memory sessions.
- **No post-generation refinement.** The bot collects the brief conversationally;
  once "Generate" is pressed there is no "make scenario 3 about retries" re-run.
  Editing means changing an answer *before* generating.
- No Docker / deployment.
- The mockup's selectable chips — v1 is text-driven; chips may return later as
  bot-offered quick-picks (v1.1).

---

## 5. Architecture

A new top-level package `task_builder/`, alongside the existing CLI modules. It
*drives* them; it does not replace them.

```
task_builder/
  __init__.py
  __main__.py      python -m task_builder  →  launches uvicorn on localhost:8000
  server.py        FastAPI app + routes
  slots.py         TaskBrief schema + SessionState (authoritative server state)
  conversation.py  structured-output LLM engine (Approach B)
  validation.py    validates slot values against Supabase / enums
  runner.py        background pipeline runner; emits per-stage StageEvents
  prompts.py       the bot's system prompt
  static/
    index.html     live version of the mockup
    app.js         chat rendering, SSE consumption
    styles.css
```

**FastAPI** is the backend: async-native (required for SSE), Pydantic gives the slot
schema for free, idiomatic Python. `python -m task_builder` starts the server —
matching how every other module in this repo is launched.

The four pipeline modules (`generate_input_files`, `scenario_generator`,
`prompt_generator`, `multiagent`) are **unchanged in their core logic**; `runner.py`
invokes them exactly as `run_pipeline.py` does today. The only existing-code change is
Layer B (Section 10).

---

## 6. Data model — `TaskBrief` and `SessionState`

```python
class TaskBrief(BaseModel):
    competencies: list[str]      # Q1 — each must exist in Supabase `competencies`
    proficiency: str | None      # Q2 — BEGINNER | BASIC | INTERMEDIATE | ADVANCED
    role: str | None             # Q3 — free text → generate_input_files --role
    focus_areas: list[str]       # Q4 — NEW (Layer B)
    domain: str | None           # Q5 — NEW (Layer B)
    scenario_count: int = 6      # default

class SessionState:
    session_id: str
    brief: TaskBrief             # authoritative, server-owned
    history: list[Message]       # full conversation transcript
    corrective_calls_this_turn: int
```

Required slots: `competencies`, `proficiency`, `role`, `focus_areas`, `domain`.
`scenario_count` defaults to 6. The LLM *proposes* updates to the brief; the **server
decides what is true**.

---

## 7. Data flow

```
Browser ──POST /api/chat {session_id, message}──▶ server.py
                                                    │
   conversation.py: 1 LLM call → {reply, slots_update, ready_to_generate}
                                                    │
   validation.py: validate slots_update
     · competency → Supabase lookup (name + proficiency)
     · invalid?   → 1 corrective LLM call so the bot re-asks in the SAME response
                                                    │
   server merges only the VALID fields into SessionState.brief
                                                    │
Browser ◀──{reply, brief, missing_slots, ready}─────┘
   renders bot bubble; when ready → summary card + "Generate task" button

Browser ──POST /api/generate {session_id}──▶ server spawns runner.py (background)
   runner: preflight → input_files → scenarios → prompt → tasks
   after each stage → StageEvent pushed to an asyncio.Queue for that run
                                                    │
Browser ◀──GET /api/runs/{run_id}/events  (SSE)─────┘
   each StageEvent → a bot bubble; terminal event = GitHub link OR failure + stage
```

**Server owns state.** The LLM's `ready_to_generate` is only a suggestion. The `ready`
flag returned to the browser is:

```
ready = LLM_says_ready  AND  server_validation_says(all required slots present & valid)
```

That single rule is what keeps a "fully conversational" bot from running the pipeline
on a half-filled or invalid brief.

**Corrective-call trick.** Approach B's one weakness: the LLM speaks before the server
validates. Mitigation — when `slots_update` contains a competency, the server runs the
Supabase lookup *before* returning; on failure it makes **one** further LLM call
feeding back e.g. `competency 'Sprng Boot' not found — closest: Spring Boot, Spring`,
so the corrected question reaches the user in the same HTTP turn. Capped at one
corrective call per turn to bound cost and latency.

---

## 8. Conversation engine (Approach B — structured-output slot-filling)

`conversation.py` — exactly one LLM call per user message:

- **Input:** `[system_prompt, *history, user_message]`
- **Output (strict JSON):**
  ```json
  { "reply": "string shown to the user",
    "slots_update": { "<partial TaskBrief fields>" },
    "ready_to_generate": false }
  ```
- **Model:** reuse the existing Portkey gateway. Use **Claude Sonnet 4.6** (same as
  `multiagent.py` task generation) for reliable JSON adherence.
- **System prompt (`prompts.py`)** defines: the goal (assemble a complete
  `TaskBrief`), the six slots and their valid forms, the strict JSON output contract,
  the rule *"never claim generation has started — only set `ready_to_generate` true
  once every required slot is filled"*, and to ask about missing slots one topic at a
  time.
- **Robustness:** a non-JSON response → one retry with a "return valid JSON only"
  nudge → then a graceful *"I had trouble — could you rephrase?"* message.

---

## 9. Pipeline runner & streaming

`runner.py` runs the pipeline as a background job and emits events.

- On `POST /api/generate`, the server spawns a background task. The four stages are
  blocking subprocesses, so the runner uses a worker thread; events cross back to the
  async world via an `asyncio.Queue` keyed by `run_id`.
- The runner **reuses the stage logic of `run_pipeline.py`**. `run_pipeline.py` is
  refactored so its per-stage logic is importable functions (today `main()` does
  everything inline); its CLI `main()` becomes a thin wrapper. The terminal path and
  the web path then share one runner — no duplicated stage code.
- After each stage the runner emits a `StageEvent`:
  ```json
  { "stage": "02_scenarios",
    "status": "running | ok | failed",
    "duration_s": 90.4,
    "detail": "6 scenarios generated",
    "outcome": null }
  ```
- For stage 4 it reuses `_summarise_task_stage` to classify CREATED / REJECTED / ERROR
  and, on success, extracts the GitHub template link and task id.
- A terminal event closes the stream:
  ```json
  { "event": "done", "status": "completed | failed",
    "task_url": "...", "task_id": "...", "summary": "..." }
  ```
- `GET /api/runs/{run_id}/events` is an SSE endpoint draining that run's queue.

---

## 10. Layer B — `scenario_generator` changes (the "fix the task generator" part)

The **only existing code that changes**. Three files, all backward compatible — both
new flags optional; omitted = today's behaviour exactly.

1. **`scenario_generator/__main__.py`** — two new CLI options:
   - `--focus-areas` — comma-separated or repeated; what to assess.
   - `--domain` — a single business domain to pin all scenarios to.
2. **`scenario_generator/generator.py`** — thread `focus_areas` and `domain` through
   `generate_scenarios_for_competencies` → `build_generation_prompt`.
3. **`scenario_generator/prompts.py`** — two conditional blocks, using the existing
   conditional-block pattern (integration / dedup / feedback blocks already work this
   way):
   - `FOCUS_AREAS_BLOCK` — *"Bias scenarios toward these areas: …"* when set; empty
     string when not.
   - **Domain pinning** — when `--domain` is set, swap the hard-coded *"Each scenario
     MUST use a DIFFERENT business domain"* rule (`prompts.py:308`) for *"All
     scenarios take place in the {domain} domain."*

`run_pipeline.py` (and therefore `runner.py`) pass the new flags through when present.

**The task generator (`multiagent.py`) needs no new parameter** — focus and domain
ride into the task through the *scenarios*, which `generate_tasks` already consumes.
The thing that needed fixing was `scenario_generator`; the task generator gets richer
scenarios for free.

---

## 11. HTTP API

| Method & path | Body | Returns |
|---|---|---|
| `GET /` | — | serves `static/index.html` |
| `GET /static/*` | — | static assets |
| `POST /api/session` | — | `{ session_id, reply }` (bot greeting + first question) |
| `POST /api/chat` | `{ session_id, message }` | `{ reply, brief, missing_slots, ready }` |
| `POST /api/generate` | `{ session_id }` | `{ run_id }` (400 if `ready` is false) |
| `GET /api/runs/{run_id}/events` | — | SSE stream of `StageEvent` + terminal `done` |
| `GET /api/health` | — | `{ status: "ok" }` |

---

## 12. Front-end

`static/` — the existing mockup made live:

- Strip the hard-coded scripted conversation from the mockup HTML.
- `app.js`: on load `POST /api/session` → render the greeting; the free-text dock is
  the primary input (it is a conversational bot). Each `POST /api/chat` appends the
  user bubble and the bot `reply`.
- When the response has `ready: true`, render the summary card from `brief` plus a
  "Generate task" button.
- On "Generate" → `POST /api/generate`, then open an `EventSource` on
  `/api/runs/{run_id}/events`; append each `StageEvent` as a bot bubble; the terminal
  event renders the GitHub link or the failure reason.
- Keep the right-rail "Behind the chat" mapping, corrected for current reality
  (`generate_tasks` underscore form; the `prompt_generator` stage; nested
  `agent_generated_prompts/` folders).

---

## 13. Error handling

- LLM returns non-JSON → one retry with a nudge → graceful fallback message.
- Competency not found → close-match suggestions in the reply (Supabase returns all
  names; fuzzy-match locally).
- Proficiency changed after competencies were set → re-validate competencies, since a
  DB row is keyed on name + proficiency.
- A pipeline stage fails → `StageEvent` `status=failed` + reason; bot posts
  *"Stage N failed — &lt;reason&gt;. Logs: &lt;path&gt;."*; the run ends.
- Eval-gate rejection (stage 4 exit 0 but task rejected) → reuse `_summarise_task_stage`;
  surface *"task rejected after 3 attempts"*.
- Preflight runs as stage 0 (as `run_pipeline.py` already does) → missing env vars and
  registry problems surface before any generation work starts.
- Server restart → in-memory sessions are lost; acceptable for a local tool.

---

## 14. Testing

pytest, consistent with the existing suite + `conftest.py`:

- `test_task_builder_slots.py` — schema, required-field detection, merge logic.
- `test_task_builder_validation.py` — mock Supabase: competency found / not-found /
  close-match; proficiency enum.
- `test_task_builder_conversation.py` — mock the LLM JSON output; merge logic and the
  corrective-call path.
- `test_task_builder_runner.py` — mock the four stages; assert event emission ordering
  and failure handling.
- Layer B — `scenario_generator` prompt contains the focus block when `focus_areas`
  is set; domain pinning swaps the variety rule when `domain` is set.

---

## 15. Dependencies

Added to `requirements.txt`: `fastapi`, `uvicorn[standard]`, `sse-starlette`.
`httpx` for tests (FastAPI's `TestClient`).

---

## 16. File-by-file change list

**New files**

- `task_builder/__init__.py`, `__main__.py`, `server.py`, `slots.py`,
  `conversation.py`, `validation.py`, `runner.py`, `prompts.py`
- `task_builder/static/index.html`, `app.js`, `styles.css`
- `tests/test_task_builder_slots.py`, `test_task_builder_validation.py`,
  `test_task_builder_conversation.py`, `test_task_builder_runner.py`
- `tests/test_scenario_focus_domain.py` (Layer B)

**Modified files**

- `run_pipeline.py` — extract per-stage logic into importable functions; `main()`
  becomes a thin CLI wrapper.
- `scenario_generator/__main__.py` — `--focus-areas`, `--domain` options.
- `scenario_generator/generator.py` — thread the two new parameters.
- `scenario_generator/prompts.py` — `FOCUS_AREAS_BLOCK` + domain pinning.
- `requirements.txt` — new dependencies.

---

## 17. Future (v1.1+)

- Selectable chips as bot-offered quick-picks.
- Post-generation refinement ("make scenario 3 about retries") — re-entering
  individual pipeline stages; overlaps with the autonomous-task-agent design.
- Session persistence (SQLite or a local JSON store).
- Shared internal deployment (auth, multi-user, a real session store).
