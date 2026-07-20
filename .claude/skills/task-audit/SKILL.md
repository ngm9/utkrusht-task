---
name: task-audit
description: Use when you need to audit task rows in Supabase for data integrity — checks all required fields, content rules, GitHub/gist reachability, and the is_shared_infra_required ↔ template_id consistency rule. Run this before assigning tasks to candidates, after bulk generation runs, or whenever data quality is in question.
---

# Task Audit Skill

Runs `task_audit.py` against the Supabase `tasks` table and reports which rows
and fields have problems. All checks are read-only — nothing is written.

## What it checks (per `ready` row)

| Field | Rule |
|---|---|
| `task_blob.title` | Non-empty, Title Case, not a kebab slug |
| `task_blob.short_overview` | Exactly 3 items, no Markdown glyph prefixes (•/-/*). Narrative shape: bullet[0] = what the task is, bullet[1] = what we currently have (the problem/existing state, in natural prose — no fixed template phrase required), bullet[2] = what needs to be improved + expected outcome. No file names/paths in any bullet. **WARN-only heuristic**: bullet[1] opening with an imperative verb ("Implement/Add/Build/...") often means the problem statement was skipped in favor of a second build instruction ("instruction-stacking") — but some tasks legitimately bundle two asks, so always read the actual bullet before rewriting |
| `task_blob.outcomes` | Non-empty list, each item non-empty, no glyph prefixes |
| `task_blob.question` | 120–1500 chars; must read as plain-prose "scenario paragraph + direct imperative ask" (per `task_quality/semantic.py`'s rubric) — no unrendered Markdown (`**bold**`, `` `code` ``, code fences), no numbered spec-list formatting (`1. ... 2. ...`), no leftover "Current Implementation:"/"Required Changes:" structural labels, and no setup/install/run instructions leaked in (`npm install`, `./run.sh`, `docker-compose up`, `git clone`, `.env` setup, README pointers — those belong in the README, not here). The candidate view renders this field as plain text, so any Markdown syntax shows up literally |
| `task_blob.hints` | Non-empty string |
| `task_blob.definitions` | Non-empty dict, each value non-empty string |
| `task_blob.resources.github_repo` | Present, valid URL format, repo exists on GitHub |
| `task_blob.resources.github_gist` | Present, gist exists and is accessible |
| `criterias` | Non-empty, each entry has competency_id/name/proficiency; no duplicates; all competency_ids exist in `competencies` table |
| `pre_requisites` | 2–3 items, each ≤ 120 chars |
| `answer` | Non-empty string |
| `is_shared_infra_required` + `template_id` | Orthogonal (template_id = base runtime image; is_shared_infra_required = needs shared services). A set template_id must exist in `templates` (never dangling); if is_shared_infra_required is True the template_id must be present. A non-infra task MAY carry a base template_id — that is not a failure |

**Skipped intentionally:** `eval_info`, `solutions`, `deployment_info`, `readme_content`

## Input

`$ARGUMENTS` — optional task UUID. If not provided, audits all `status='ready'` rows.

## Steps

### 1 — Determine scope and flags

Ask the user if not obvious:
- **Environment:** `dev` or `prod`? Default to `dev` unless they say prod.
- **Scope:** One specific task (`--task-id <uuid>`) or all ready tasks?
- **GitHub checks:** On by default. Suggest `--skip-github` if there are many tasks (>50) to avoid rate-limiting — GitHub API has 5,000 req/hr for authenticated calls; each task costs 2 calls (repo + gist).

If `$ARGUMENTS` is provided, treat it as the task UUID and run single-task mode.

### 2 — Run the audit script

```bash
# All ready tasks in dev (default)
python task_audit.py --env dev

# All ready tasks in prod
python task_audit.py --env prod

# Single task
python task_audit.py --env dev --task-id <uuid>

# Only tasks that are enabled (is_enabled=True)
python task_audit.py --env dev --enabled

# Only tasks for a specific competency (substring match, case-insensitive)
python task_audit.py --env dev --competency "React"
python task_audit.py --env dev --competency "Java"

# Combine filters — enabled React tasks only
python task_audit.py --env dev --enabled --competency "React"

# Skip GitHub API calls (faster for large batches)
python task_audit.py --env dev --skip-github

# Limit rows (useful for a quick sample)
python task_audit.py --env dev --limit 20
```

**Filter notes:**
- `--enabled` filters server-side (`is_enabled = True` in Supabase)
- `--competency` filters client-side after fetch (substring match on any `criterias[*].name`). Use the competency name or a keyword, e.g. `"React"` matches `"ReactJs"`, `"React Native"`, `"React + TypeScript"` etc.
- Both filters can be combined freely with `--task-id`, `--limit`, `--skip-github`

Run from `D:\Utkrushta_task\` (the project root where `task_audit.py` lives).

**Required env vars** (read from `.env` automatically):
- `SUPABASE_URL_APTITUDETESTSDEV` / `SUPABASE_API_KEY_APTITUDETESTSDEV` (dev)
- `SUPABASE_URL_APTITUDETESTS` / `SUPABASE_API_KEY_APTITUDETESTS` (prod)
- `GITHUB_UTKRUSHTAPPS_TOKEN` — for repo reachability checks
- `GITHUB_GIST_TOKEN` — for gist reachability (falls back to `GITHUB_UTKRUSHTAPPS_TOKEN` if not set)

### 3 — Read and report results

The script prints a per-task block and then a summary:

```
✓  task_id: abc-123   title: 'Build Rate Limiter Middleware'
      ✓  title              Build Rate Limiter Middleware
      ✓  short_overview     3 bullets, clean
      ✗  pre_requisites     4 items (max 3)
      ✗  question           87 chars (min 120)
      ✓  resources          repo + gist accessible
      ✗  criterias          competency_ids not in DB: ['xyz-999']

================================================================
SUMMARY  12 tasks   ✓ 9 pass   ⚠ 0 warn   ✗ 3 fail

Most common failures:
    pre_requisites: 2 task(s)
    question: 1 task(s)
```

Surface the full output to the user. If any tasks fail, summarize:
- How many tasks failed
- Which fields are failing most
- Whether the failures look like a systematic bug (e.g. all older tasks missing `github_gist`)
  or isolated data issues

### 4 — Triage guidance

Based on failures, suggest next steps:

| Failure | Likely cause | Fix |
|---|---|---|
| `github_gist missing` across many tasks | Tasks generated before gist creation was wired in | Run `python gist_manager.py create --task-ids <ids> --env dev` |
| `title` is kebab slug | Old task-gen prompt returned slugified names | Manual update in Supabase or a patch script |
| `pre_requisites` has wrong count | Content-quality rewrite produced too many/few items | Manual edit or re-run quality pass |
| `short_overview` bullet[1] opens with an imperative verb (WARN) | Generator wrote all 3 bullets as stacked instructions instead of context→problem→ask — bullet[1] became a second "Implement X" instead of stating what's currently broken | Read `question`/`outcomes` for grounding, then rewrite bullet[1] as the current-state/problem sentence (vary phrasing naturally — "the current X does not...", "right now...", "X is present but Y is missing" — no fixed template). Merge any 4th "instruction" bullet into bullet[2]'s outcome. **Confirm it's a real defect first** — a two-sub-fix task legitimately splitting the ask across bullets[0]/[1] is not a bug |
| `short_overview` references a file name/path (WARN) | Generator leaked an implementation-level file reference (e.g. `` `alertDispatcher.js` ``) into candidate-facing narrative prose | Strip the file name, keep the rest of the sentence — short_overview describes the system/behavior, not the file layout |
| `question` too short | LLM generated a stub question | Flag for regeneration |
| `question` contains `**`/`` ` ``/structural labels | Question was generated using the "Current Implementation:"/"Required Changes:" prompt template, but the candidate view renders it as plain text, not Markdown | Strip `**` and `` ` `` and the label text, collapse into one flowing paragraph — same wording, no rewrite. Check both `tasks.task_blob.question` AND any `task_sessions.tasks[].question_blob.question` snapshots already assigned to candidates |
| `question` too long and/or has a numbered spec-list / code fence | Question was written (or content-quality-rewritten) as a numbered requirements spec instead of scenario+ask prose — usually correlates with being well over 1500 chars | Rewrite as two-part plain prose: one scenario/symptom paragraph, one direct imperative ask. Preserve every concrete fact (exact colors/thresholds/field names/behavior) — only the spec-sheet packaging goes, not the content |
| `question` has setup/install/run instructions leaked in | Generator folded README-style onboarding text ("run ./run.sh", "npm install", "docker-compose up", "git clone", ".env" setup, "see the README") into the candidate-facing question | Delete the setup sentence(s) only; leave the rest of the scenario+ask untouched. That content belongs in the README, not here |
| `criterias` competency_id not in DB | FK dangling — competency was deleted | Investigate in Supabase dashboard |
| `infra_template` dangling | `template_id` points at a template not in the `templates` table | Investigate — the template was deleted/renamed, or the row has a stale id |
| `infra_template` missing | `is_shared_infra_required=True` but `template_id` is null | Set the base template so the task can boot its services |

### 5 — Exit code

The script exits `0` if all tasks pass or warn, `1` if any task has at least one `FAIL`.
Use exit code to decide if action is needed before reporting "all clear."
