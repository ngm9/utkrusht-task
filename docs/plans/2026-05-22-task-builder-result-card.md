# Task Builder — End-of-Run Result Card — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** At the end of a successful generation run, show a result card with the task's ID, name, type, competencies, environment, and repository link — instead of just a one-line link.

**Architecture:** The runner already receives the task's name/type/competencies in stage-4 stdout and knows the `env`. Extend the runner's stdout extractor to parse those lines, carry them on the `done` event, and render them in the frontend as a key/value card. No `multiagent.py` change.

**Tech Stack:** Python (the runner, pytest), vanilla JavaScript + CSS (the frontend).

**Spec:** `docs/specs/2026-05-22-task-builder-result-card-design.md`

---

## Before you start

- **Branch:** work on **`feat/task-builder`** (the main repo is already checked out on it).
- **Commits are user-gated.** Do **not** `git commit`. Each task ends by *staging* (`git add`); the user reviews and commits. Commit-message text is a suggestion.
- **Builds on uncommitted work.** `app.js` and `styles.css` already contain the staged (uncommitted) transcript-persistence feature. Edit the files as they currently are on disk — the "old" code blocks below are quoted from that current state.
- **Running tests:** `.venv/bin/python -m pytest <path> -v` from the repo root.
- **Frontend verification:** no JS test infrastructure — `node --check` for syntax, then manual browser checks. FastAPI serves static files from disk per request, so a browser hard-refresh (Ctrl+Shift+R) picks up edits with no server restart.

## File structure

| File | Responsibility after this change |
|------|----------------------------------|
| `task_builder/runner.py` | `StageEvent` gains 4 fields; `_extract_task_result` parses 5 lines and returns a dict; the `completed` event carries the new fields + `env` |
| `tests/test_task_builder_runner.py` | Updated + new unit tests for the dict-returning extractor and the enriched `done` event |
| `task_builder/static/app.js` | `renderDone` renders a result card on success; `doneBubble` / `renderItem` carry the new fields |
| `task_builder/static/styles.css` | `.result-card` reuses the `.summary` card styling |

---

## Task 1: Backend — extended extractor, `StageEvent` fields, enriched `done` event

**Files:**
- Modify: `task_builder/runner.py`
- Test: `tests/test_task_builder_runner.py`

This task is TDD: tests first.

- [ ] **Step 1: Update the two existing extractor tests and add four new tests**

In `tests/test_task_builder_runner.py`, **replace** the two existing tests
`test_extract_task_result_parses_id_and_url` and
`test_extract_task_result_missing_file_returns_none` (the function's return type
changes from a 2-tuple to a dict), and **add four new tests**. Replace this
block:

```python
def test_extract_task_result_parses_id_and_url(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(" Task ID: abc-123\n Task Name: x\n"
                      " GitHub Repository: https://github.com/org/repo\n")
    task_id, url = _extract_task_result(stdout)
    assert task_id == "abc-123"
    assert url == "https://github.com/org/repo"


def test_extract_task_result_missing_file_returns_none(tmp_path):
    from task_builder.runner import _extract_task_result
    task_id, url = _extract_task_result(tmp_path / "nope.out")
    assert task_id is None and url is None
```

with:

```python
def test_extract_task_result_parses_id_and_url(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(" Task ID: abc-123\n Task Name: x\n"
                      " GitHub Repository: https://github.com/org/repo\n")
    result = _extract_task_result(stdout)
    assert result["task_id"] == "abc-123"
    assert result["task_url"] == "https://github.com/org/repo"
    assert result["task_name"] == "x"


def test_extract_task_result_missing_file_returns_none(tmp_path):
    from task_builder.runner import _extract_task_result
    result = _extract_task_result(tmp_path / "nope.out")
    assert result["task_id"] is None
    assert result["task_url"] is None
    assert result["task_name"] is None
    assert result["task_type"] is None
    assert result["competencies"] is None


def test_extract_task_result_parses_full_success_block(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(
        " Task Creation Successful!\n"
        " Task Type: BUILD\n"
        " Task ID: 11111111-2222-3333-4444-555555555555\n"
        " Task Name: Idempotent payment webhook\n"
        " Competencies Covered: Java, Spring Boot\n"
        " GitHub Repository: https://github.com/org/task-repo\n"
        " TASK CREATION COMPLETED SUCCESSFULLY!\n"
    )
    result = _extract_task_result(stdout)
    assert result["task_id"] == "11111111-2222-3333-4444-555555555555"
    assert result["task_name"] == "Idempotent payment webhook"
    assert result["task_type"] == "BUILD"
    assert result["competencies"] == "Java, Spring Boot"
    assert result["task_url"] == "https://github.com/org/task-repo"


def test_extract_task_result_missing_lines_yield_none(tmp_path):
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(" Task ID: only-an-id\n")
    result = _extract_task_result(stdout)
    assert result["task_id"] == "only-an-id"
    assert result["task_name"] is None
    assert result["task_type"] is None
    assert result["competencies"] is None
    assert result["task_url"] is None


def test_extract_task_result_competencies_covered_not_summary_line(tmp_path):
    """Reads 'Competencies Covered:' and ignores the later bare
    'Competencies:' summary line."""
    from task_builder.runner import _extract_task_result
    stdout = tmp_path / "s.out"
    stdout.write_text(
        " Competencies Covered: Real Value\n"
        " Competencies: Different Summary Value\n"
    )
    result = _extract_task_result(stdout)
    assert result["competencies"] == "Real Value"


def test_done_event_carries_task_fields_and_env(tmp_path):
    """The completed 'done' event surfaces the extracted task fields + env."""
    events: list[StageEvent] = []
    stage4_stdout = tmp_path / "04.out"
    stage4_stdout.write_text(
        " Task ID: tid-9\n Task Name: Demo\n Task Type: BUILD\n"
        " Competencies Covered: Go\n"
        " GitHub Repository: https://github.com/org/r\n"
    )

    def fake_stage(d, label, c):
        rec = _stage_ok(label)
        if label == "04_tasks":
            rec["stdout"] = str(stage4_stdout)
        return rec

    with patch("task_builder.runner._run_stage", side_effect=fake_stage), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r-fields", emit=events.append,
                               env="prod", runs_root=tmp_path)

    done = events[-1]
    assert done.stage == "done" and done.status == "completed"
    assert done.task_id == "tid-9"
    assert done.task_name == "Demo"
    assert done.task_type == "BUILD"
    assert done.competencies == "Go"
    assert done.task_url == "https://github.com/org/r"
    assert done.env == "prod"
```

- [ ] **Step 2: Run the tests — verify they fail**

Run: `.venv/bin/python -m pytest tests/test_task_builder_runner.py -v`
Expected: the six tests above FAIL — the updated ones because `_extract_task_result` still returns a 2-tuple (tuple has no string keys / `done` event lacks the new attributes), the new ones for the same reasons.

- [ ] **Step 3: Add the four new `StageEvent` fields**

In `task_builder/runner.py`, in the `StageEvent` dataclass, replace:

```python
    task_id: str | None = None
    task_url: str | None = None
```

with:

```python
    task_id: str | None = None
    task_url: str | None = None
    task_name: str | None = None
    task_type: str | None = None
    competencies: str | None = None
    env: str | None = None
```

- [ ] **Step 4: Rewrite `_extract_task_result` to return a dict of five fields**

In `task_builder/runner.py`, replace the entire `_extract_task_result` function:

```python
def _extract_task_result(stdout_path: Path) -> tuple[str | None, str | None]:
    """Pull (task_id, github_url) from the stage-4 stdout. Returns (None, None)
    if the file is missing or the lines are absent."""
    if not stdout_path.exists():
        return None, None
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    task_id = task_url = None
    for line in text.splitlines():
        if "Task ID:" in line:
            task_id = line.split("Task ID:", 1)[1].strip() or None
        elif "GitHub Repository:" in line:
            task_url = line.split("GitHub Repository:", 1)[1].strip() or None
    return task_id, task_url
```

with:

```python
# stage-4 stdout label -> result-dict key. "Competencies Covered:" is matched
# as the full phrase so it does not also catch the later bare "Competencies:"
# summary line.
_RESULT_LABELS: tuple[tuple[str, str], ...] = (
    ("Task ID:", "task_id"),
    ("Task Name:", "task_name"),
    ("Competencies Covered:", "competencies"),
    ("Task Type:", "task_type"),
    ("GitHub Repository:", "task_url"),
)


def _extract_task_result(stdout_path: Path) -> dict[str, str | None]:
    """Pull the task's identifying fields from the stage-4 stdout.

    Returns a dict with keys task_id, task_url, task_name, task_type,
    competencies — each None when its line is absent (a failed run, a missing
    file, or an older multiagent.py).
    """
    fields: dict[str, str | None] = {
        "task_id": None, "task_url": None, "task_name": None,
        "task_type": None, "competencies": None,
    }
    if not stdout_path.exists():
        return fields
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        for label, key in _RESULT_LABELS:
            if label in line:
                fields[key] = line.split(label, 1)[1].strip() or None
                break
    return fields
```

- [ ] **Step 5: Update the `completed` event to carry the new fields + `env`**

In `task_builder/runner.py`, in `run_pipeline_for_brief`, replace:

```python
        task_id, task_url = _extract_task_result(Path(rec["stdout"]))
        emit(StageEvent("done", "completed", detail=outcome, outcome=outcome,
                        task_id=task_id, task_url=task_url))
```

with:

```python
        result = _extract_task_result(Path(rec["stdout"]))
        emit(StageEvent("done", "completed", detail=outcome, outcome=outcome,
                        task_id=result["task_id"], task_url=result["task_url"],
                        task_name=result["task_name"],
                        task_type=result["task_type"],
                        competencies=result["competencies"], env=env))
```

- [ ] **Step 6: Run the full runner test file — verify all pass**

Run: `.venv/bin/python -m pytest tests/test_task_builder_runner.py -v`
Expected: PASS — all tests, including the pre-existing runner tests (the
`done`-event change only adds optional fields, so the ordering/failure tests are
unaffected).

- [ ] **Step 7: Stage for review**

```bash
git add task_builder/runner.py tests/test_task_builder_runner.py
```
Pause. The user reviews and commits. Suggested message:
`feat(task-builder): extract task name/type/competencies for the done event`

---

## Task 2: Frontend — result card rendering

**Files:**
- Modify: `task_builder/static/app.js`
- Modify: `task_builder/static/styles.css`

- [ ] **Step 1: Replace `renderDone` and add the `kvRow` helper in `app.js`**

In `task_builder/static/app.js`, replace this block:

```javascript
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
```

with:

```javascript
// Append a label/value row to a `.kv` grid. `value` is plain text, or a DOM
// node (e.g. a link) to place in the value cell.
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
```

- [ ] **Step 2: Extend the `doneBubble` spec with the new fields**

In `task_builder/static/app.js`, replace this block:

```javascript
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
```

with:

```javascript
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
```

- [ ] **Step 3: Extend the `renderItem` done branch so a restored card is complete**

In `task_builder/static/app.js`, in `renderItem`, replace this block:

```javascript
  } else if (item.kind === "done") {
    renderDone({
      status: item.status || "",
      outcome: item.outcome || "",
      detail: item.detail || "",
      task_url: item.task_url || "",
    });
  }
```

with:

```javascript
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
```

- [ ] **Step 4: Make `.result-card` reuse the summary-card styling**

In `task_builder/static/styles.css`, replace these two lines:

```css
.summary { background:var(--bg); border:1px solid var(--border);
  border-radius:14px; padding:14px 16px; }
.summary h4 { margin:0 0 10px; font-size:13px; font-weight:600; }
```

with:

```css
.summary, .result-card { background:var(--bg); border:1px solid var(--border);
  border-radius:14px; padding:14px 16px; }
.summary h4, .result-card h4 { margin:0 0 10px; font-size:13px; font-weight:600; }
```

(The `.kv` / `.k` / `.v` grid classes are already shared, so the result card
needs no further CSS.)

- [ ] **Step 5: Syntax-check the JavaScript**

Run: `node --check task_builder/static/app.js`
Expected: no output (exit 0) — syntax OK.

- [ ] **Step 6: Stage for review**

```bash
git add task_builder/static/app.js task_builder/static/styles.css
```
Pause. The user reviews and commits. Suggested message:
`feat(task-builder): show task ID/name/type/competencies/env result card`

---

## Self-Review

**1. Spec coverage:**
- `StageEvent` +4 fields (`task_name`, `task_type`, `competencies`, `env`) → Task 1 Step 3.
- `_extract_task_result` parses 5 lines, returns a dict → Task 1 Step 4.
- `completed` event carries the new fields + `env` → Task 1 Step 5.
- `renderDone` result card on success, outcome text on failure → Task 2 Step 1.
- Rows rendered only when non-empty; repository as a link; text via `textContent` → Task 2 Step 1 (`if (value)` guard, `kvRow` link branch, `textContent`).
- `doneBubble` records the new fields; `renderItem` passes them through → Task 2 Steps 2–3.
- `.result-card` reuses summary styling → Task 2 Step 4.
- Backend TDD test for the extractor → Task 1 Steps 1–2, 6.
- Failed-run display unchanged → Task 2 Step 1 (the non-completed branch is the
  original `bubble("bot", …, "stage failed")`).
All spec sections map to a step. No gaps.

**2. Placeholder scan:** No "TBD"/"TODO"/vague steps. Every code step shows
complete code; every command step states the command and expected result.

**3. Type consistency:** `_extract_task_result` returns a dict with keys
`task_id`, `task_url`, `task_name`, `task_type`, `competencies` — the same keys
are read in Task 1 Step 5 (`result["task_id"]` …) and asserted in the Step 1
tests. `StageEvent` field names (`task_name`, `task_type`, `competencies`,
`env`) match between Step 3, the Step 5 `emit(...)` kwargs, and the
`test_done_event_carries_task_fields_and_env` assertions. The frontend `spec`
object keys (`task_id`, `task_name`, `task_type`, `competencies`, `env`,
`task_url`, `status`) are consistent across `renderDone`, `doneBubble`, and the
`renderItem` done branch. The `done` transcript item written by `record({ kind:
"done", ...spec })` carries exactly the keys `renderItem` reads back. Consistent.
