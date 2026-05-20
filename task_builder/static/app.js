// Task Builder chat client — talks to the FastAPI backend.
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("send");
let sessionId = null;
let busy = false;

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

function summaryCard(brief) {
  const card = bubble("bot", "", "summary");
  card.innerHTML = `<h4>Task brief</h4><div class="kv">
    <div class="k">Tech stack</div><div>${brief.competencies.join(", ")}</div>
    <div class="k">Proficiency</div><div>${brief.proficiency}</div>
    <div class="k">Role</div><div>${brief.role}</div>
    <div class="k">Focus areas</div><div>${brief.focus_areas.join(", ")}</div>
    <div class="k">Domain</div><div>${brief.domain}</div>
  </div><div class="actions">
    <label class="env-pick">Environment
      <select id="env">
        <option value="dev">dev</option>
        <option value="prod">prod</option>
      </select>
    </label>
    <button class="cta" id="gen">Generate task →</button>
  </div>`;
  card.querySelector("#gen").onclick = startGeneration;
}

async function startSession() {
  try {
    const res = await fetch("/api/session", { method: "POST" });
    const data = await res.json();
    sessionId = data.session_id;
    bubble("bot", data.reply);
  } catch {
    bubble("bot", "Could not connect to the server. Is the backend running?");
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || busy || !sessionId) return;
  busy = true;
  input.value = "";
  bubble("user", text);
  const thinking = bubble("bot", "…");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    thinking.textContent = data.reply;
    if (data.ready) summaryCard(data.brief);
  } catch (e) {
    thinking.textContent = "Network error — please try again.";
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
  bubble("bot", `Generating in ${env}…`, "stage");
  fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, env }),
  })
    .then((r) => r.json())
    .then((data) => streamRun(data.run_id))
    .catch(() => bubble("bot", "Could not start generation.", "stage failed"));
}

// Get (creating on first use) the collapsible log panel for one stage.
function stagePanel(panels, label) {
  if (panels[label]) return panels[label];
  const el = bubble("bot", "", "stage-log");
  el.innerHTML =
    '<details open><summary></summary><pre class="log"></pre></details>';
  const panel = {
    details: el.querySelector("details"),
    summary: el.querySelector("summary"),
    log: el.querySelector("pre"),
  };
  panels[label] = panel;
  return panel;
}

// Terminal "done" event — final outcome bubble plus a repo link on success.
function doneBubble(e) {
  const cls = e.status === "completed" ? "stage ok" : "stage failed";
  const el = bubble("bot", e.outcome || e.detail || e.status, cls);
  if (e.status === "completed" && e.task_url) {
    el.appendChild(document.createElement("br"));
    const a = document.createElement("a");
    a.href = e.task_url;
    a.textContent = e.task_url;
    a.target = "_blank";
    a.rel = "noopener";
    el.appendChild(a);
  }
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
  };
  es.onerror = () => es.close();
}

sendBtn.onclick = send;
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
startSession();
