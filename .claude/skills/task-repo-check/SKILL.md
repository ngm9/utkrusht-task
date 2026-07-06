---
name: task-repo-check
description: Use when you need to inspect an Utkrushta task GitHub repository — to understand what candidates must implement, verify the starter code is appropriately incomplete (nothing is accidentally pre-solved), and flag any files that give away too much. Run this before assigning tasks to candidates or after generating a new task repo.
---

# Task Repo Check Skill

Fetches every source file from a `UtkrushtApps/` GitHub repo, reads the README objectives, cross-checks against the actual code, and reports what candidates must implement plus any accidental over-implementation in the starter code.

## Authentication

Always read the token from the project `.env` — **never hardcode it**:

```bash
GITHUB_TOKEN=$(grep GITHUB_UTKRUSHTAPPS_TOKEN D:\Utkrushta_task\.env | cut -d= -f2)
```

## Steps

### 1 — Resolve the repo name

`$ARGUMENTS` is the repo URL or short name. Extract just `owner/repo`:

- `https://github.com/UtkrushtApps/express-todo-crud-api` → `UtkrushtApps/express-todo-crud-api`
- `express-todo-crud-api` → `UtkrushtApps/express-todo-crud-api`

### 2 — List all files

```bash
GITHUB_TOKEN="<from .env>"
REPO="UtkrushtApps/<repo-name>"

curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/git/trees/HEAD?recursive=1" \
  | python -c "import sys,json; [print(f['path']) for f in json.load(sys.stdin).get('tree',[]) if f['type']=='blob']"
```

### 3 — Fetch every file's content

For each file path, decode the base64 content:

```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/contents/<file-path>" \
  | python -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

Fetch all files in parallel if there are many. Always fetch `README.md` first.

### 4 — Extract objectives from README

Read the README and identify:
- **Objectives / Requirements section** — what the candidate must implement
- **How to Verify section** — test cases that must pass
- **Helpful Tips** — hints about intended approach

List each objective as a bullet.

### 5 — Cross-check implementation vs objectives

For each objective, search the source files for an implementation:

| Signal | Meaning |
|---|---|
| Function/route/handler is completely absent | ✅ Appropriately missing — candidate must add |
| Function exists but has empty/stub body | ✅ Appropriately incomplete |
| Function exists with partial logic (e.g. no error handling) | ✅ Acceptable incomplete |
| Function is fully implemented and correct | ❌ Pre-solved — needs to be removed or stubbed out |
| Middleware is wired in `app.js` but empty in its own file | ✅ Fine — wiring as a hint is intentional |

### 6 — Produce the report

Output in this structure:

---

**Repo:** `UtkrushtApps/<repo-name>`

**What candidates must implement:**
- [ ] `<objective 1>` — missing from `<file>`
- [ ] `<objective 2>` — stub exists in `<file>` (body empty)
- ...

**Starter code assessment:**

| File | Status | Notes |
|---|---|---|
| `src/middleware/logger.js` | ✅ Appropriately incomplete | Body is empty stub |
| `src/services/tasksService.js` | ✅ Missing update/delete | Only CRUD reads wired |
| `src/routes/tasks.js` | ❌ PUT route pre-implemented | Candidate should add this |

**Issues to fix** (if any):
- `src/routes/tasks.js` line 12: DELETE route already implemented — remove or stub out
- ...

**Validation nuances** (things candidates must reason through):
- e.g. "POST validation middleware requires description always, but PATCH must allow omitting it — candidate must write separate logic"

---

If nothing is pre-solved, end with: **"Starter code is appropriately incomplete. No changes needed."**

### 7 — Fix pre-solved code (if flagged)

If step 6 finds any ❌ items, propose the minimal stub that removes the implementation without removing the structure:

**Before (pre-solved):**
```js
exports.deleteTask = async (id) => {
  const idx = tasks.findIndex(t => t.id === id);
  if (idx === -1) return null;
  return tasks.splice(idx, 1)[0];
};
```

**After (appropriate stub):**
```js
exports.deleteTask = async (id) => {
  // TODO: implement
};
```

Ask the user before pushing any changes to the repo.

## What "Appropriately Incomplete" Means

The starter code should:
- Have the **file structure and imports** in place (so candidates aren't fighting setup)
- Have **working examples** of the existing patterns (GET/POST done → candidate adds PUT/DELETE)
- Have **middleware wired** in the right place but with empty bodies
- **NOT** have any of the objectives already solved, even partially

The README's "Helpful Tips" section is the intended level of hint — the code itself should not go further.

## Common Patterns Seen in Utkrushta Repos

| Framework | Typical missing pieces |
|---|---|
| Express.js | PUT/PATCH + DELETE routes, update/delete service methods, logger middleware body |
| FastAPI | POST/PUT endpoint handlers, Pydantic validation, dependency injection |
| React/Next.js | Component logic, state management hooks, API integration |
| Java Spring | Service layer methods, controller endpoints, exception handlers |
| SQL | Missing queries, unoptimised joins, missing indexes |

## Required env vars

- `GITHUB_UTKRUSHTAPPS_TOKEN` — read from `D:\Utkrushta_task\.env`
