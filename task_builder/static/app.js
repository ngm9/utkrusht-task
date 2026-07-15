// Task Builder chat client — talks to the FastAPI backend.
// Layout: chat on the left; a live "Task brief" panel on the right that
// auto-fills from every /api/chat response (the server returns brief +
// missing_slots each turn) and hosts the Generate button + pipeline
// checklist.
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("send");
const newTaskBtn = document.getElementById("new-task");
const pdfBtn = document.getElementById("download-pdf");
const printDate = document.getElementById("print-date");
const slotsEl = document.getElementById("slots");
const progressFill = document.getElementById("brief-progress");
const progressLabel = document.getElementById("brief-progress-label");
const genBtn = document.getElementById("gen");
const genHint = document.getElementById("gen-hint");
const envSelect = document.getElementById("env");
const panelRun = document.getElementById("panel-run");
const runStagesEl = document.getElementById("run-stages");
const runResultEl = document.getElementById("run-result");
const startersEl = document.getElementById("starters");
const startersRow = document.getElementById("starters-row");
let sessionId = null;
let busy = false;
let generating = false;
let activeStream = null;

// ---- deployment access token ---------------------------------------------
// Deployed instances set INTERNAL_PROXY_TOKEN on the backend; every /api/*
// call must then carry it. The UI prompts once, stores the token in
// localStorage, and retries. Local dev (token unset server-side) never 403s,
// so the prompt never fires.
const TOKEN_KEY = "taskbuilder.token";
let apiToken = "";
try {
  apiToken = localStorage.getItem(TOKEN_KEY) || "";
} catch (e) {
  /* storage unavailable — token re-prompted per page load */
}

function promptForToken() {
  const t = prompt("This Task Builder deployment is protected.\nEnter the access token:");
  if (!t || !t.trim()) return false;
  apiToken = t.trim();
  try {
    localStorage.setItem(TOKEN_KEY, apiToken);
  } catch (e) {
    /* ignore */
  }
  return true;
}

// fetch() wrapper: attaches the token header and, on 403, prompts for the
// token and retries once.
async function api(path, opts = {}) {
  const doFetch = () => {
    const headers = { ...(opts.headers || {}) };
    if (apiToken) headers["X-Internal-Token"] = apiToken;
    return fetch(path, { ...opts, headers });
  };
  let res = await doFetch();
  if (res.status === 403 && promptForToken()) {
    res = await doFetch();
  }
  return res;
}

// EventSource cannot set headers — the backend accepts ?access_token= as a
// fallback for the SSE stream.
function withToken(url) {
  if (!apiToken) return url;
  return url + (url.includes("?") ? "&" : "?") + "access_token=" + encodeURIComponent(apiToken);
}

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

// ---- the task-brief panel --------------------------------------------------
// Mirrors task_builder/slots.py: five required slots + optional
// scenario_count (defaults to 6 server-side).
const SLOT_DEFS = [
  { key: "competencies", label: "Tech stack", list: true, required: true },
  { key: "proficiency", label: "Proficiency", required: true },
  { key: "role", label: "Role", required: true },
  { key: "focus_areas", label: "Focus areas", list: true, required: true },
  { key: "domain", label: "Domain", required: true },
  { key: "scenario_count", label: "Scenarios", required: false, fallback: "6 (default)" },
];
let panelState = { brief: {}, missing: [], ready: false };

function slotValue(def, brief) {
  const v = brief ? brief[def.key] : null;
  if (def.list) return (v || []).join(", ");
  if (v === null || v === undefined || v === "") return "";
  return String(v);
}

function renderBriefPanel() {
  const { brief, missing, ready } = panelState;
  slotsEl.innerHTML = "";
  const asking = missing.length ? missing[0] : null;
  let filledRequired = 0;
  for (const def of SLOT_DEFS) {
    const value = slotValue(def, brief);
    const filled = !!value;
    if (filled && def.required) filledRequired += 1;
    const li = document.createElement("li");
    li.className = filled ? "filled" : "empty";
    if (!generating && def.key === asking) li.classList.add("asking");
    const label = document.createElement("div");
    label.className = "slot-label";
    label.textContent = def.label;
    const val = document.createElement("div");
    val.className = "slot-value";
    val.textContent = filled ? value : (def.fallback || (def.key === asking ? "being asked now…" : "not set yet"));
    li.appendChild(label);
    li.appendChild(val);
    if (filled && !generating) {
      li.title = `Click to change ${def.label.toLowerCase()}`;
      li.onclick = () => {
        input.value = `Change the ${def.label.toLowerCase()} to `;
        input.focus();
      };
    }
    slotsEl.appendChild(li);
  }
  const total = SLOT_DEFS.filter((d) => d.required).length;
  progressFill.style.width = `${(filledRequired / total) * 100}%`;
  progressLabel.textContent = `${filledRequired} of ${total} fields`;
  genBtn.disabled = !(ready && sessionId && !generating);
  if (generating) {
    genHint.textContent = "Generation in progress — logs stream in the chat.";
  } else if (ready) {
    genHint.textContent = "Brief complete. Pick an environment and generate.";
  } else {
    genHint.textContent = "Answer the questions in the chat — the brief fills in here as you go.";
  }
}

function updateBrief(data) {
  panelState = {
    brief: data.brief || {},
    missing: data.missing_slots || [],
    ready: !!data.ready,
  };
  renderBriefPanel();
}

// The panel mirrors the CURRENT server-side conversation only. A page
// reload starts a fresh session (empty brief server-side), so the panel
// starts empty too — restoring an old brief here would enable Generate
// against a session that can't generate yet.
function resetBrief() {
  panelState = { brief: {}, missing: [], ready: false };
  renderBriefPanel();
}

// ---- pipeline checklist in the panel ---------------------------------------
const PIPELINE_STAGES = [
  ["00_preflight", "Preflight checks"],
  ["01_input_files", "Input files"],
  ["02_scenarios", "Scenarios"],
  ["03_prompt", "Prompts"],
  ["04_tasks", "Generate & evaluate"],
];
const panelStageEls = {};

function showRunPanel() {
  panelRun.hidden = false;
  runResultEl.hidden = true;
  runResultEl.innerHTML = "";
  runStagesEl.innerHTML = "";
  for (const [key, label] of PIPELINE_STAGES) {
    const li = document.createElement("li");
    const dot = document.createElement("span");
    dot.className = "dot";
    const text = document.createElement("span");
    text.textContent = label;
    const secs = document.createElement("span");
    secs.className = "secs";
    li.appendChild(dot);
    li.appendChild(text);
    li.appendChild(secs);
    runStagesEl.appendChild(li);
    panelStageEls[key] = { li, dot, secs };
  }
}

function setPanelStage(stageKey, status, durationS) {
  const entry = panelStageEls[stageKey];
  if (!entry) return;
  entry.li.className = status;
  if (status === "ok") {
    entry.dot.textContent = "✓";
    if (durationS != null) entry.secs.textContent = `${durationS}s`;
  } else if (status === "failed") {
    entry.dot.textContent = "✗";
  } else {
    entry.dot.textContent = "";
  }
}

function showRunResult(spec) {
  runResultEl.hidden = false;
  runResultEl.innerHTML = "";
  if (spec.status === "completed") {
    const strong = document.createElement("strong");
    strong.textContent = spec.task_name || "Task created";
    runResultEl.appendChild(strong);
    if (spec.task_id) {
      runResultEl.appendChild(document.createElement("br"));
      runResultEl.appendChild(document.createTextNode(`ID ${spec.task_id}`));
    }
    if (spec.task_url) {
      runResultEl.appendChild(document.createElement("br"));
      const a = document.createElement("a");
      a.href = spec.task_url;
      a.textContent = "Open repository →";
      a.target = "_blank";
      a.rel = "noopener";
      runResultEl.appendChild(a);
    }
  } else {
    runResultEl.textContent = spec.outcome || spec.detail || "Generation failed.";
  }
}

// ---- starter suggestion chips ----------------------------------------------
const STARTERS = [
  "An INTERMEDIATE React + TypeScript task for a frontend engineer, focused on state management, e-commerce domain",
  "A BASIC Java + Kafka task for a backend engineer, focused on consumer groups, logistics domain",
  "An ADVANCED Python task for a data engineer, focused on pipeline reliability, fintech domain",
];

function renderStarters() {
  startersRow.innerHTML = "";
  for (const text of STARTERS) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = text;
    b.onclick = () => {
      input.value = text;
      hideStarters();
      send();
    };
    startersRow.appendChild(b);
  }
  startersEl.hidden = false;
}

function hideStarters() {
  startersEl.hidden = true;
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

// Read-only task-brief card. Only used when restoring transcripts saved by
// the previous single-column UI — the live flow renders the brief in the
// side panel instead.
function summaryCard(brief) {
  const card = bubble("bot", "", "summary");
  card.innerHTML = `<h4>Task brief</h4><div class="kv">
    <div class="k">Tech stack</div><div class="v"></div>
    <div class="k">Proficiency</div><div class="v"></div>
    <div class="k">Role</div><div class="v"></div>
    <div class="k">Focus areas</div><div class="v"></div>
    <div class="k">Domain</div><div class="v"></div>
  </div>`;
  const v = card.querySelectorAll(".kv .v");
  v[0].textContent = (brief.competencies || []).join(", ");
  v[1].textContent = brief.proficiency || "";
  v[2].textContent = brief.role || "";
  v[3].textContent = (brief.focus_areas || []).join(", ");
  v[4].textContent = brief.domain || "";
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
    const res = await api("/api/session", { method: "POST" });
    if (res.status === 403) {
      addBubble("bot", "Access token required — reload the page to try again.");
      return;
    }
    const data = await res.json();
    sessionId = data.session_id;
    addBubble("bot", data.reply);
    renderBriefPanel();
  } catch {
    addBubble("bot", "Could not connect to the server. Is the backend running?");
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || busy || !sessionId) return;
  busy = true;
  input.value = "";
  hideStarters();
  addBubble("user", text);
  const thinking = bubble("bot", "…"); // transient — intentionally not recorded
  try {
    const res = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    thinking.textContent = data.reply;
    record({ kind: "bubble", role: "bot", text: data.reply, cls: "" });
    updateBrief(data);
  } catch (e) {
    const msg = "Network error — please try again.";
    thinking.textContent = msg;
    record({ kind: "bubble", role: "bot", text: msg, cls: "" });
  } finally {
    busy = false;
  }
}

function startGeneration() {
  if (generating || !panelState.ready || !sessionId) return;
  const env = envSelect ? envSelect.value : "dev";
  generating = true;
  if (envSelect) envSelect.disabled = true;
  renderBriefPanel();
  showRunPanel();
  addBubble("bot", `Generating in ${env}…`, "stage");
  api("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, env }),
  })
    .then((r) => r.json())
    .then((data) => streamRun(data.run_id))
    .catch(() => {
      generating = false;
      if (envSelect) envSelect.disabled = false;
      renderBriefPanel();
      addBubble("bot", "Could not start generation.", "stage failed");
    });
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
  showRunResult(spec);
  if (spec.status === "completed") {
    for (const [key] of PIPELINE_STAGES) {
      const entry = panelStageEls[key];
      if (entry && entry.li.className !== "failed") setPanelStage(key, "ok");
    }
  }
  generating = false;
  if (envSelect) envSelect.disabled = false;
  renderBriefPanel();
}

function streamRun(runId) {
  const panels = {};
  const stageItems = {};
  const es = new EventSource(withToken(`/api/runs/${runId}/events`));
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
      setPanelStage(e.stage, "running");
    } else if (e.status === "log") {
      panel.log.textContent += e.detail || "";
      panel.log.scrollTop = panel.log.scrollHeight;
    } else if (e.status === "ok") {
      const secs = e.duration_s != null ? ` · ${e.duration_s}s` : "";
      panel.summary.textContent = `✓ ${e.stage}${secs}`;
      panel.details.open = false;
      setPanelStage(e.stage, "ok", e.duration_s);
    } else if (e.status === "failed") {
      panel.summary.textContent = `✗ ${e.stage} ${e.detail || ""}`.trim();
      panel.details.open = true;
      setPanelStage(e.stage, "failed");
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
    generating = false;
    if (envSelect) envSelect.disabled = false;
    renderBriefPanel();
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
    summaryCard(item.brief || {});
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
  generating = false;
  if (envSelect) envSelect.disabled = false;
  panelRun.hidden = true;
  resetBrief();
  renderStarters();
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
if (genBtn) genBtn.onclick = startGeneration;

// Restore any saved transcript (read-only), mark a session boundary, then
// start a fresh chat session. The brief panel always starts empty — it
// mirrors the new session, not the restored history.
if (loadTranscript()) {
  divider("— new session —");
} else {
  renderStarters();
}
renderBriefPanel();
startSession();
