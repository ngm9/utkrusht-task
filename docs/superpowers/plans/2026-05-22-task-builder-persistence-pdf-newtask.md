# Task Builder — Session Persistence, PDF Export & New-Task Reset — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `localStorage` transcript persistence, a print-to-PDF download button, and a "New task" reset button to the Task Builder web UI.

**Architecture:** Frontend-only. `app.js` gains a serializable `transcript` array that mirrors the chat area and is saved to `localStorage`; on load it is re-rendered read-only, then a fresh chat session starts. PDF export uses `window.print()` plus a print stylesheet. The "New task" button confirms, clears state, and restarts the session. No backend changes.

**Tech Stack:** Vanilla JavaScript (no framework, no build step), HTML, CSS, the browser `localStorage` and print APIs.

**Spec:** `docs/superpowers/specs/2026-05-22-task-builder-persistence-pdf-newtask-design.md`

---

## Before you start

- **Branch:** all work happens on **`feat/task-builder`** — that is where the
  `task_builder/` package lives. Check it out (or use a worktree) before
  starting. The plan file and spec live in the main repo's `docs/`.
- **Commits are user-gated.** Per project rule, do **not** commit. Each task
  ends by *staging* the changes (`git add`) and pausing for the user to review
  and commit. The commit-message text in the final step is a suggestion for the
  user.
- **No server restart needed for verification.** FastAPI's `StaticFiles` and
  the `index.html` `FileResponse` read from disk on every request — after
  editing a static file, just **hard-refresh** the browser (Ctrl+Shift+R). Only
  start the server once: `python -m task_builder`, then open
  `http://127.0.0.1:8000`.
- **No automated tests.** The project has no JavaScript test infrastructure;
  every task is verified **manually** in the browser, with exact steps given.

## File structure

Three existing files are modified. No files are created.

| File | Responsibility after this change |
|------|----------------------------------|
| `task_builder/static/index.html` | Page skeleton + two header buttons + a print-only document header |
| `task_builder/static/styles.css` | Existing styling + header-button styles + a `divider` style + an `@media print` block |
| `task_builder/static/app.js` | Existing chat client + transcript model, persistence, restore, and the two new button handlers |

---

## Task 1: Header buttons & print-header element (`index.html`)

**Files:**
- Modify: `task_builder/static/index.html` (full-file replacement — 26 lines → 29)

- [ ] **Step 1: Replace the entire contents of `task_builder/static/index.html`**

The only changes vs. the current file: a `.header-actions` group with two
buttons inside `<header>`, and a `.print-head` element after `</header>`.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Task Builder</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <header>
    <div class="logo" aria-hidden="true"></div>
    <h1>Task Builder</h1>
    <div class="header-actions">
      <button id="new-task" class="hbtn" type="button">New task</button>
      <button id="download-pdf" class="hbtn" type="button">Download PDF</button>
    </div>
  </header>
  <div class="print-head" aria-hidden="true">Task Builder — <span id="print-date"></span></div>
  <main><div class="chat" id="chat"></div></main>
  <div class="dock">
    <div class="dock-inner">
      <input type="text" id="msg" placeholder="Type a message…" autocomplete="off" />
      <button id="send">Send</button>
    </div>
  </div>
  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify the buttons appear**

Start the server (`python -m task_builder`), open `http://127.0.0.1:8000`,
hard-refresh.
Expected: two buttons — "New task" and "Download PDF" — appear in the header.
They will be unstyled and right-positioned awkwardly (Task 2 styles them) and do
nothing yet (Task 3 wires them). The chat still works as before.

- [ ] **Step 3: Stage for review**

```bash
git add task_builder/static/index.html
```
Pause. The user reviews and commits. Suggested message:
`feat(task-builder): add header buttons + print-head element`

---

## Task 2: Header-button styles, divider style & print stylesheet (`styles.css`)

**Files:**
- Modify: `task_builder/static/styles.css` (append a block at end of file)

- [ ] **Step 1: Append this block to the end of `task_builder/static/styles.css`**

Append after the existing final rule (the `.dock button { … }` rule). Add
nothing elsewhere.

```css

/* Header action buttons */
.header-actions { margin-left:auto; display:flex; gap:8px; }
.hbtn {
  background:var(--text); color:#fff; border:0; border-radius:9px;
  padding:7px 12px; font:inherit; font-size:13px; font-weight:600;
  cursor:pointer;
}
.hbtn:hover { opacity:.88; }

/* Conversation divider — inserted between a restored transcript and the
   fresh session that starts after a page reload. */
.divider {
  align-self:center; color:var(--muted); font-size:12px;
  font-family:"Roboto",-apple-system,BlinkMacSystemFont,sans-serif;
  letter-spacing:0.02em; margin:6px 0; user-select:none;
}

/* Print-only document header — hidden on screen, shown when printing. */
.print-head { display:none; }

/* Print-to-PDF stylesheet. Triggered by the Download PDF button via
   window.print(). Hides chrome, lets content flow across pages, and forces
   every stage-log panel fully open so the logs print. */
@media print {
  header, .dock { display:none !important; }
  body { overflow:visible; height:auto; }
  main { overflow:visible; padding:0; display:block; }
  .chat { width:100%; }
  .print-head {
    display:block; padding:12px 0 14px; font-weight:600; font-size:15px;
    border-bottom:1px solid var(--border); margin-bottom:14px;
  }
  .row, .summary, .stage-log { page-break-inside:avoid; }
  .bubble { max-width:100% !important; }
  .stage-log details > *:not(summary) { display:block !important; }
  .stage-log pre.log { max-height:none !important; }
}
```

- [ ] **Step 2: Verify header styling**

Hard-refresh `http://127.0.0.1:8000`.
Expected: the two header buttons are now dark, rounded, and pushed to the
right-hand end of the header (the `.header-actions` `margin-left:auto`).

- [ ] **Step 3: Verify the print stylesheet**

In the browser, open the print dialog (Ctrl+P).
Expected in the print preview: the header bar and the bottom input dock are
gone; a "Task Builder — " line appears at the top (the date is blank for now —
Task 3 fills it). Close the dialog without printing.

- [ ] **Step 4: Stage for review**

```bash
git add task_builder/static/styles.css
```
Pause. The user reviews and commits. Suggested message:
`feat(task-builder): style header buttons + add print stylesheet`

---

## Task 3: Transcript model, persistence, restore & button handlers (`app.js`)

**Files:**
- Modify: `task_builder/static/app.js` (full-file replacement — ~153 lines → ~210)

This task replaces the whole file. The new file keeps every existing behaviour
and adds: the `transcript` model + `localStorage` persistence, the read-only
restore path, and the `newTask` / `downloadPdf` handlers.

- [ ] **Step 1: Replace the entire contents of `task_builder/static/app.js`**

```javascript
// Task Builder chat client — talks to the FastAPI backend.
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("send");
const newTaskBtn = document.getElementById("new-task");
const pdfBtn = document.getElementById("download-pdf");
const printDate = document.getElementById("print-date");
let sessionId = null;
let busy = false;

// ---- transcript persistence (localStorage) -------------------------------
// `transcript` is a serializable mirror of the chat area. It is saved to
// localStorage so a page reload can re-render the conversation (read-only).
const STORE_KEY = "taskbuilder.transcript";
let transcript = [];
let restoring = false;       // true while replaying a saved transcript
let saveTimer = null;
let persistDisabled = false; // set true after a quota error

function saveTranscript() {
  if (restoring || persistDisabled) return;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(transcript));
    } catch (e) {
      persistDisabled = true;
      console.warn("Task Builder: transcript persistence disabled —", e);
    }
  }, 500);
}

// Append a transcript item (skipped during restore) and schedule a save.
function record(item) {
  if (restoring) return;
  transcript.push(item);
  saveTranscript();
}

// Update (or create) the single transcript item for one pipeline stage.
function recordStage(label, fields) {
  if (restoring) return;
  let item = transcript.find((x) => x.kind === "stage" && x.label === label);
  if (!item) {
    item = { kind: "stage", label, summary: "", log: "", status: "" };
    transcript.push(item);
  }
  Object.assign(item, fields);
  saveTranscript();
}

// ---- rendering primitives ------------------------------------------------
// Low-level DOM helper. Does NOT record — used directly for transient UI
// (the "…" placeholder) and as the primitive behind addBubble/summaryCard.
function bubble(role, text, cls) {
  const row = document.createElement("div");
  row.className = "row " + (role === "user" ? "user" : "bot");
  const avatar = `<div class="avatar ${role}">${role === "user" ? "Y" : "U"}</div>`;
  const bubbleDiv = `<div class="bubble ${cls || ""}"></div>`;
  row.innerHTML = role === "user" ? bubbleDiv + avatar : avatar + bubbleDiv;
  const el = row.querySelector(".bubble");
  el.textContent = text;
  chat.appendChild(row);
  row.scrollIntoView({ behavior: "smooth", block: "end" });
  return el;
}

// bubble() + record it as a transcript item.
function addBubble(role, text, cls) {
  const el = bubble(role, text, cls);
  record({ kind: "bubble", role, text, cls: cls || "" });
  return el;
}

// A centered separator line (used between a restored transcript and the
// fresh session). Recorded so it survives the next reload too.
function divider(text) {
  const el = document.createElement("div");
  el.className = "divider";
  el.textContent = text;
  chat.appendChild(el);
  record({ kind: "divider", text });
}

// The task-brief card. live=true wires the Generate button and records the
// item; live=false renders a static, read-only card (used on restore).
function summaryCard(brief, live = true) {
  const card = bubble("bot", "", "summary");
  const actions = live
    ? `<div class="actions">
         <label class="env-pick">Environment
           <select id="env">
             <option value="dev">dev</option>
             <option value="prod">prod</option>
           </select>
         </label>
         <button class="cta" id="gen">Generate task →</button>
       </div>`
    : "";
  card.innerHTML = `<h4>Task brief</h4><div class="kv">
    <div class="k">Tech stack</div><div class="v"></div>
    <div class="k">Proficiency</div><div class="v"></div>
    <div class="k">Role</div><div class="v"></div>
    <div class="k">Focus areas</div><div class="v"></div>
    <div class="k">Domain</div><div class="v"></div>
  </div>${actions}`;
  const v = card.querySelectorAll(".kv .v");
  v[0].textContent = (brief.competencies || []).join(", ");
  v[1].textContent = brief.proficiency || "";
  v[2].textContent = brief.role || "";
  v[3].textContent = (brief.focus_areas || []).join(", ");
  v[4].textContent = brief.domain || "";
  if (live) {
    card.querySelector("#gen").onclick = startGeneration;
    record({ kind: "summary", brief });
  }
}

// Build one collapsible stage-log panel and return handles to its parts.
function makeStagePanel() {
  const el = bubble("bot", "", "stage-log");
  el.innerHTML =
    '<details open><summary></summary><pre class="log"></pre></details>';
  return {
    details: el.querySelector("details"),
    summary: el.querySelector("summary"),
    log: el.querySelector("pre"),
  };
}

// Get (creating on first use) the live stage panel for one stage label.
function stagePanel(panels, label) {
  if (panels[label]) return panels[label];
  const panel = makeStagePanel();
  panels[label] = panel;
  return panel;
}

// Render the terminal outcome bubble. Shared by the live and restore paths.
function renderDone(spec) {
  const cls = spec.status === "completed" ? "stage ok" : "stage failed";
  const el = bubble("bot", spec.outcome || spec.detail || spec.status, cls);
  if (spec.status === "completed" && spec.task_url) {
    el.appendChild(document.createElement("br"));
    const a = document.createElement("a");
    a.href = spec.task_url;
    a.textContent = spec.task_url;
    a.target = "_blank";
    a.rel = "noopener";
    el.appendChild(a);
  }
}

// ---- live conversation flow ----------------------------------------------
async function startSession() {
  try {
    const res = await fetch("/api/session", { method: "POST" });
    const data = await res.json();
    sessionId = data.session_id;
    addBubble("bot", data.reply);
  } catch {
    addBubble("bot", "Could not connect to the server. Is the backend running?");
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || busy || !sessionId) return;
  busy = true;
  input.value = "";
  addBubble("user", text);
  const thinking = bubble("bot", "…"); // transient — intentionally not recorded
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    thinking.textContent = data.reply;
    record({ kind: "bubble", role: "bot", text: data.reply, cls: "" });
    if (data.ready) summaryCard(data.brief);
  } catch (e) {
    const msg = "Network error — please try again.";
    thinking.textContent = msg;
    record({ kind: "bubble", role: "bot", text: msg, cls: "" });
  } finally {
    busy = false;
  }
}

function startGeneration() {
  const gen = document.getElementById("gen");
  const envSel = document.getElementById("env");
  const env = envSel ? envSel.value : "dev";
  if (gen) gen.disabled = true;
  if (envSel) envSel.disabled = true;
  addBubble("bot", `Generating in ${env}…`, "stage");
  fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, env }),
  })
    .then((r) => r.json())
    .then((data) => streamRun(data.run_id))
    .catch(() => addBubble("bot", "Could not start generation.", "stage failed"));
}

// Terminal "done" event — final outcome bubble plus a repo link on success.
function doneBubble(e) {
  const spec = {
    status: e.status,
    outcome: e.outcome || "",
    detail: e.detail || "",
    task_url: e.task_url || "",
  };
  renderDone(spec);
  record({ kind: "done", ...spec });
}

function streamRun(runId) {
  const panels = {};
  const es = new EventSource(`/api/runs/${runId}/events`);
  es.onmessage = (ev) => {
    const e = JSON.parse(ev.data);
    if (e.stage === "done") {
      doneBubble(e);
      es.close();
      return;
    }
    const panel = stagePanel(panels, e.stage);
    if (e.status === "running") {
      panel.summary.textContent = `⏳ ${e.stage}`;
      panel.details.open = true;
    } else if (e.status === "log") {
      panel.log.textContent += e.detail || "";
      panel.log.scrollTop = panel.log.scrollHeight;
    } else if (e.status === "ok") {
      const secs = e.duration_s != null ? ` · ${e.duration_s}s` : "";
      panel.summary.textContent = `✓ ${e.stage}${secs}`;
      panel.details.open = false;
    } else if (e.status === "failed") {
      panel.summary.textContent = `✗ ${e.stage} ${e.detail || ""}`.trim();
      panel.details.open = true;
    }
    recordStage(e.stage, {
      summary: panel.summary.textContent,
      log: panel.log.textContent,
      status: e.status,
    });
  };
  es.onerror = () => es.close();
}

// ---- restore a saved transcript (read-only) ------------------------------
function renderItem(item) {
  if (item.kind === "bubble") {
    bubble(item.role, item.text, item.cls);
  } else if (item.kind === "divider") {
    const el = document.createElement("div");
    el.className = "divider";
    el.textContent = item.text;
    chat.appendChild(el);
  } else if (item.kind === "summary") {
    summaryCard(item.brief, false);
  } else if (item.kind === "stage") {
    const panel = makeStagePanel();
    panel.summary.textContent = item.summary;
    panel.log.textContent = item.log;
    panel.details.open = item.status !== "ok";
  } else if (item.kind === "done") {
    renderDone(item);
  }
}

// Returns true if a saved transcript was found and re-rendered.
function loadTranscript() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
  } catch {
    saved = [];
  }
  if (!Array.isArray(saved) || saved.length === 0) return false;
  restoring = true;
  saved.forEach(renderItem);
  restoring = false;
  transcript = saved; // keep appending to the restored transcript
  return true;
}

// ---- header button handlers ----------------------------------------------
function newTask() {
  if (!confirm("Discard this conversation and start a new task?")) return;
  clearTimeout(saveTimer);
  transcript = [];
  try {
    localStorage.removeItem(STORE_KEY);
  } catch (e) {
    /* ignore */
  }
  persistDisabled = false;
  chat.innerHTML = "";
  sessionId = null;
  busy = false;
  startSession();
}

function downloadPdf() {
  const panels = chat.querySelectorAll(".stage-log details");
  const wasOpen = [];
  panels.forEach((d) => {
    wasOpen.push(d.open);
    d.open = true;
  });
  if (printDate) printDate.textContent = new Date().toLocaleString();
  function restoreOpen() {
    panels.forEach((d, i) => {
      d.open = wasOpen[i];
    });
    window.removeEventListener("afterprint", restoreOpen);
  }
  window.addEventListener("afterprint", restoreOpen);
  window.print();
}

// ---- bootstrap -----------------------------------------------------------
sendBtn.onclick = send;
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});
if (newTaskBtn) newTaskBtn.onclick = newTask;
if (pdfBtn) pdfBtn.onclick = downloadPdf;

// Restore any saved transcript (read-only), mark a session boundary, then
// start a fresh chat session.
if (loadTranscript()) {
  divider("— new session —");
}
startSession();
```

- [ ] **Step 2: Verify the conversation still works**

Hard-refresh `http://127.0.0.1:8000`. Have a short conversation with the bot
(answer a couple of questions).
Expected: the chat behaves exactly as before — bubbles appear, the "…"
placeholder is replaced by the reply.

- [ ] **Step 3: Verify persistence + read-only restore**

With that conversation on screen, **reload the page** (F5).
Expected: the previous conversation re-renders at the top; a centered
`— new session —` divider appears; a fresh bot greeting follows below it. If
your earlier conversation had reached the brief card, the restored card shows
the values but has **no** environment picker and **no** Generate button.

- [ ] **Step 4: Verify the "New task" button**

Click **New task** → a confirm dialog appears. Click **Cancel** — nothing
changes. Click **New task** again → **OK**.
Expected: the chat clears entirely and a single fresh greeting appears. In
DevTools → Application → Local Storage, the `taskbuilder.transcript` key is
gone (it will reappear once the new greeting is saved ~0.5 s later, containing
just that greeting).

- [ ] **Step 5: Verify the "Download PDF" button**

Run a conversation through to a generated task if possible (so there are
stage-log panels), then click **Download PDF**.
Expected: the print dialog opens; the preview shows the top "Task Builder — "
header **with today's date filled in**, the full conversation, the brief card,
the outcome, and every stage-log panel **expanded with its logs visible**. The
header bar and input dock are absent. Close the dialog — on screen, any
stage-log panels that were collapsed are collapsed again (state restored).

- [ ] **Step 6: Verify the quota guard (optional)**

In the DevTools console, run `localStorage.setItem = () => { throw new Error("quota"); }`
then send a chat message.
Expected: a `console.warn` appears ("transcript persistence disabled"); the
chat continues to work normally. Reload the page to undo the override.

- [ ] **Step 7: Stage for review**

```bash
git add task_builder/static/app.js
```
Pause. The user reviews and commits. Suggested message:
`feat(task-builder): persist transcript + add PDF export and New task`

---

## Self-Review

**1. Spec coverage:**
- Transcript model + `localStorage` save (debounced, quota-guarded) → Task 3,
  Step 1 (`transcript`, `record`, `recordStage`, `saveTranscript`).
- Read-only restore + `— new session —` divider → Task 3, Step 1
  (`loadTranscript`, `renderItem`, `divider`, bootstrap).
- Restored brief card without controls → `summaryCard(brief, false)`.
- Restored stage panel open/closed by status → `renderItem` `stage` branch.
- Download PDF button + force-open + date + `afterprint` restore → `downloadPdf`.
- Print stylesheet (hide chrome, expand logs, page breaks, print-head) → Task 2.
- New task button + confirm + clear + restart → `newTask`.
- Header layout (`.header-actions`, buttons, `.print-head`) → Tasks 1 & 2.
- No backend change → confirmed; only `static/` files touched.
All spec sections map to a task. No gaps.

**2. Placeholder scan:** No "TBD"/"TODO"/vague steps. Every code step shows
complete code; every verification step states exact actions and expected
results.

**3. Type consistency:** Item `kind` values (`bubble`, `divider`, `summary`,
`stage`, `done`) are consistent between `record`/`recordStage` (write) and
`renderItem` (read). Stage item fields (`label`, `summary`, `log`, `status`)
match between `recordStage` and the `renderItem` `stage` branch. Element IDs
(`new-task`, `download-pdf`, `print-date`) match between `index.html` and the
`app.js` `getElementById` calls. CSS classes (`header-actions`, `hbtn`,
`divider`, `print-head`) match between `index.html`/`app.js` and `styles.css`.
Consistent.
