// Task Builder chat client — talks to the FastAPI backend.
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("send");
const newTaskBtn = document.getElementById("new-task");
const pdfBtn = document.getElementById("download-pdf");
const printDate = document.getElementById("print-date");
let sessionId = null;
let busy = false;
let activeStream = null;

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
  if (!restoring) row.scrollIntoView({ behavior: "smooth", block: "end" });
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

// Append a label/value row to a `.kv` grid. `value` is plain text, or a DOM
// node (e.g. a link) to place in the value cell.
// `value` must be a non-empty string or a DOM node.
function kvRow(kv, label, value) {
  const k = document.createElement("div");
  k.className = "k";
  k.textContent = label;
  const v = document.createElement("div");
  v.className = "v";
  if (typeof value === "string") v.textContent = value;
  else v.appendChild(value);
  kv.appendChild(k);
  kv.appendChild(v);
}

// Render the terminal "done" result. On success: a key/value result card with
// the task's identifying fields. On failure: the outcome text. Shared by the
// live and restore paths.
function renderDone(spec) {
  if (spec.status === "completed") {
    const card = bubble("bot", "", "result-card");
    const heading = document.createElement("h4");
    heading.textContent = "Task created";
    card.appendChild(heading);
    const kv = document.createElement("div");
    kv.className = "kv";
    const rows = [
      ["Task ID", spec.task_id],
      ["Name", spec.task_name],
      ["Type", spec.task_type],
      ["Competencies", spec.competencies],
      ["Environment", spec.env],
    ];
    for (const [label, value] of rows) {
      if (value) kvRow(kv, label, value);
    }
    if (spec.task_url) {
      const a = document.createElement("a");
      a.href = spec.task_url;
      a.textContent = spec.task_url;
      a.target = "_blank";
      a.rel = "noopener";
      kvRow(kv, "Repository", a);
    }
    card.appendChild(kv);
    return;
  }
  bubble("bot", spec.outcome || spec.detail || spec.status, "stage failed");
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
    task_id: e.task_id || "",
    task_name: e.task_name || "",
    task_type: e.task_type || "",
    competencies: e.competencies || "",
    env: e.env || "",
  };
  renderDone(spec);
  record({ kind: "done", ...spec });
}

function streamRun(runId) {
  const panels = {};
  const stageItems = {};
  const es = new EventSource(`/api/runs/${runId}/events`);
  activeStream = es;
  es.onmessage = (ev) => {
    const e = JSON.parse(ev.data);
    if (e.stage === "done") {
      doneBubble(e);
      es.close();
      activeStream = null;
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
    if (!restoring) {
      let item = stageItems[e.stage];
      if (!item) {
        item = { kind: "stage", label: e.stage, summary: "", log: "", status: "" };
        stageItems[e.stage] = item;
        transcript.push(item);
      }
      item.summary = panel.summary.textContent;
      item.log = panel.log.textContent;
      item.status = e.status;
      saveTranscript();
    }
  };
  es.onerror = () => {
    es.close();
    activeStream = null;
  };
}

// ---- restore a saved transcript (read-only) ------------------------------
function renderItem(item) {
  if (item.kind === "bubble") {
    bubble(item.role || "bot", item.text || "", item.cls || "");
  } else if (item.kind === "divider") {
    const el = document.createElement("div");
    el.className = "divider";
    el.textContent = item.text || "";
    chat.appendChild(el);
  } else if (item.kind === "summary") {
    summaryCard(item.brief || {}, false);
  } else if (item.kind === "stage") {
    const panel = makeStagePanel();
    panel.summary.textContent = item.summary || "";
    panel.log.textContent = item.log || "";
    panel.details.open = item.status !== "ok";
  } else if (item.kind === "done") {
    renderDone({
      status: item.status || "",
      outcome: item.outcome || "",
      detail: item.detail || "",
      task_url: item.task_url || "",
      task_id: item.task_id || "",
      task_name: item.task_name || "",
      task_type: item.task_type || "",
      competencies: item.competencies || "",
      env: item.env || "",
    });
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
  if (activeStream) {
    activeStream.close();
    activeStream = null;
  }
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
