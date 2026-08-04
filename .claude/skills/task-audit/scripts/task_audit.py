#!/usr/bin/env python
"""Data-integrity audit for the `task-audit` skill.

Read-only. Checks `tasks` rows in Supabase against the rule table in
../SKILL.md and prints a per-task block plus a summary. Nothing is written.

Run from the repo root with the venv python:
    .venv/bin/python .claude/skills/task-audit/scripts/task_audit.py --env prod
    .venv/bin/python .claude/skills/task-audit/scripts/task_audit.py --env prod --task-id <uuid>

Exit code: 0 if every task passes or only warns, 1 if any task has a FAIL.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Repo root is parents[4]: .claude/skills/task-audit/scripts/task_audit.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
try:
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT / ".env", override=True)
except Exception:  # noqa: BLE001 — dotenv optional; env may already be set
    pass

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_MARK = {PASS: "✓", WARN: "⚠", FAIL: "✗"}

GLYPH_RE = re.compile(r"^\s*[•\-\*·●▪]\s+")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$")
FILENAME_RE = re.compile(r"[\w/\\-]+\.(py|js|ts|tsx|jsx|go|rs|java|sql|ya?ml|json|sh|md|toml|env)\b")
IMPERATIVE_RE = re.compile(
    r"^\s*(implement|add|build|create|write|refactor|fix|update|introduce|design|develop|extend)\b",
    re.I,
)
# question must not carry markdown / spec-list / structural labels / setup steps
MD_BOLD_RE = re.compile(r"\*\*.+?\*\*", re.S)
MD_CODE_RE = re.compile(r"`[^`]+`|```")
NUM_LIST_RE = re.compile(r"(?m)^\s*\d+\.\s+\S")
LABEL_RE = re.compile(r"(current implementation|required changes|your task)\s*:", re.I)
SETUP_RE = re.compile(
    r"(npm (install|ci)\b|pip install\b|docker[- ]compose up\b|\./run\.sh|git clone\b|"
    r"\.env\b|see the readme|refer to the readme)",
    re.I,
)

QUESTION_MIN, QUESTION_MAX = 120, 1500
PREREQ_MIN, PREREQ_MAX, PREREQ_LEN = 2, 3, 120

SELECT = (
    "task_id, status, is_enabled, task_blob, criterias, pre_requisites, answer, "
    "template_id, is_shared_infra_required"
)


def _is_title_case(title: str) -> bool:
    """Most words capitalised; short joiners may stay lowercase."""
    small = {"a", "an", "and", "the", "or", "of", "in", "on", "for", "to", "at", "with", "from", "by"}
    words = [w for w in re.split(r"\s+", title.strip()) if w]
    if not words:
        return False
    checkable = [w for w in words if w[0].isalpha()]
    if not checkable:
        return False
    ok = sum(1 for w in checkable if w[0].isupper() or w.lower() in small)
    return ok >= max(1, int(len(checkable) * 0.8))


# ── individual field checks: each returns (level, message) ──────────────────

def check_title(blob: dict):
    title = (blob.get("title") or "").strip()
    if not title:
        return FAIL, "empty"
    if KEBAB_RE.match(title):
        return FAIL, f"kebab slug: {title!r}"
    if not _is_title_case(title):
        return FAIL, f"not Title Case: {title!r}"
    return PASS, title


def check_short_overview(blob: dict):
    items = blob.get("short_overview")
    if not isinstance(items, list) or not items:
        return FAIL, "missing or not a list"
    if len(items) != 3:
        return FAIL, f"{len(items)} bullets (must be exactly 3)"
    for i, b in enumerate(items):
        if not isinstance(b, str) or not b.strip():
            return FAIL, f"bullet[{i}] empty"
        if GLYPH_RE.match(b):
            return FAIL, f"bullet[{i}] has a glyph prefix"
    hits = [f"bullet[{i}]" for i, b in enumerate(items) if FILENAME_RE.search(b)]
    if hits:
        return WARN, f"file name/path in {', '.join(hits)}"
    if IMPERATIVE_RE.match(items[1]):
        return WARN, "bullet[1] opens with an imperative verb (possible instruction-stacking)"
    return PASS, "3 bullets, clean"


def check_outcomes(blob: dict):
    items = blob.get("outcomes")
    if not isinstance(items, list) or not items:
        return FAIL, "missing or empty"
    for i, o in enumerate(items):
        if not isinstance(o, str) or not o.strip():
            return FAIL, f"outcome[{i}] empty"
        if GLYPH_RE.match(o):
            return FAIL, f"outcome[{i}] has a glyph prefix"
    return PASS, f"{len(items)} outcomes, clean"


def check_question(blob: dict):
    q = blob.get("question")
    if not isinstance(q, str) or not q.strip():
        return FAIL, "missing or empty"
    n = len(q)
    problems = []
    if n < QUESTION_MIN:
        problems.append(f"{n} chars (min {QUESTION_MIN})")
    elif n > QUESTION_MAX:
        problems.append(f"{n} chars (max {QUESTION_MAX})")
    if MD_BOLD_RE.search(q):
        problems.append("unrendered **bold**")
    if MD_CODE_RE.search(q):
        problems.append("unrendered `code`/fence")
    if NUM_LIST_RE.search(q):
        problems.append("numbered spec-list formatting")
    if LABEL_RE.search(q):
        problems.append("structural label leaked in")
    if SETUP_RE.search(q):
        problems.append("setup/install instructions leaked in")
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, f"{n} chars, plain prose"


def check_hints(blob: dict):
    h = blob.get("hints")
    if not isinstance(h, str) or not h.strip():
        return FAIL, "missing or empty"
    return PASS, f"{len(h)} chars"


def check_definitions(blob: dict):
    d = blob.get("definitions")
    if not isinstance(d, dict) or not d:
        return FAIL, "missing or empty"
    for k, v in d.items():
        if not isinstance(v, str) or not v.strip():
            return FAIL, f"definition {k!r} has an empty value"
    return PASS, f"{len(d)} definitions"


def check_pre_requisites(row: dict):
    items = row.get("pre_requisites")
    if isinstance(items, str):
        items = [ln.strip(" -•") for ln in items.splitlines() if ln.strip()]
    if not isinstance(items, list) or not items:
        return FAIL, "missing or empty"
    if not (PREREQ_MIN <= len(items) <= PREREQ_MAX):
        return FAIL, f"{len(items)} items (must be {PREREQ_MIN}-{PREREQ_MAX})"
    for i, p in enumerate(items):
        if not isinstance(p, str) or not p.strip():
            return FAIL, f"item[{i}] empty"
        if len(p) > PREREQ_LEN:
            return FAIL, f"item[{i}] is {len(p)} chars (max {PREREQ_LEN})"
    return PASS, f"{len(items)} items"


def check_answer(row: dict):
    a = row.get("answer")
    if not isinstance(a, str) or not a.strip():
        return FAIL, "missing or empty"
    return PASS, f"{len(a)} chars"


def check_criterias(row: dict, known_competency_ids: set):
    crits = row.get("criterias")
    if not isinstance(crits, list) or not crits:
        return FAIL, "missing or empty"
    seen, ids = set(), []
    for i, c in enumerate(crits):
        if not isinstance(c, dict):
            return FAIL, f"criteria[{i}] is not an object"
        for key in ("competency_id", "name", "proficiency"):
            if not c.get(key):
                return FAIL, f"criteria[{i}] missing {key}"
        cid = str(c["competency_id"])
        if cid in seen:
            return FAIL, f"duplicate competency_id {cid}"
        seen.add(cid)
        ids.append(cid)
    dangling = [i for i in ids if i not in known_competency_ids]
    if dangling:
        return FAIL, f"competency_ids not in DB: {dangling}"
    return PASS, f"{len(crits)} competencies, all resolve"


def check_infra_template(row: dict, known_template_ids: set):
    """template_id and is_shared_infra_required are ORTHOGONAL.

    ``template_id`` is the BASE RUNTIME IMAGE the task boots on (python-ai,
    go-base, …) — every deployable task needs one, and a sandbox cannot boot
    without it. ``is_shared_infra_required`` is whether the task also needs
    SHARED BACKING SERVICES (postgres/kafka/redis) stood up. A pure-runtime task
    legitimately carries a base ``template_id`` while needing no shared services,
    so the old ``False ⇒ template_id must be null`` rule was a false positive
    (and nulling the template would make the task un-deployable). Validate the
    two facts independently:
      * a set ``template_id`` must resolve to a real template (never dangling);
      * infra-requiring tasks must have one (can't boot services without a base).
    A non-infra task may have a base template or none — both are fine.
    """
    needs = bool(row.get("is_shared_infra_required"))
    tid = row.get("template_id")
    if tid and tid not in known_template_ids:
        return FAIL, f"template_id {tid!r} not found in templates table (dangling)"
    if needs and not tid:
        return FAIL, "is_shared_infra_required=True but template_id is null (cannot boot services)"
    if needs:
        return PASS, f"shared infra required; base template {tid} exists"
    if tid:
        return PASS, f"no shared infra required; base template {tid} (runtime image, ok)"
    return PASS, "no shared infra required; no template_id"


def check_resources(blob: dict, session, skip_github: bool):
    res = blob.get("resources")
    if not isinstance(res, dict) or not res:
        return FAIL, "task_blob.resources missing"
    repo = res.get("github_repo")
    gist = res.get("github_gist")
    problems = []
    if not repo:
        problems.append("github_repo missing")
    elif not re.match(r"^https://github\.com/[\w.-]+/[\w.-]+/?$", repo.strip()):
        problems.append(f"github_repo malformed: {repo}")
    if not gist:
        problems.append("github_gist missing")
    elif not re.match(r"^https://gist\.github\.com/[\w.-]+/[0-9a-f]+/?$", gist.strip()):
        problems.append(f"github_gist malformed: {gist}")
    if problems:
        return FAIL, "; ".join(problems)
    if skip_github:
        return PASS, "repo + gist present (reachability skipped)"
    for label, url in (("repo", repo), ("gist", gist)):
        code = _http_status(session, _api_url(url))
        if code == 404:
            problems.append(f"{label} does not exist (404): {url}")
        elif code and code >= 400:
            problems.append(f"{label} unreachable (HTTP {code}): {url}")
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, "repo + gist accessible"


def _api_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if "gist.github.com" in url:
        return f"https://api.github.com/gists/{url.rsplit('/', 1)[-1]}"
    return "https://api.github.com/repos/" + url.split("github.com/", 1)[-1]


def _http_status(session, api_url: str):
    try:
        return session.get(api_url, timeout=20).status_code
    except Exception:  # noqa: BLE001 — network flake shouldn't abort the audit
        return None


# ── driver ──────────────────────────────────────────────────────────────────

def audit_row(row: dict, known_competency_ids, known_template_ids, session, skip_github):
    blob = row.get("task_blob") or {}
    return [
        ("title", *check_title(blob)),
        ("short_overview", *check_short_overview(blob)),
        ("outcomes", *check_outcomes(blob)),
        ("question", *check_question(blob)),
        ("hints", *check_hints(blob)),
        ("definitions", *check_definitions(blob)),
        ("pre_requisites", *check_pre_requisites(row)),
        ("answer", *check_answer(row)),
        ("criterias", *check_criterias(row, known_competency_ids)),
        ("infra_template", *check_infra_template(row, known_template_ids)),
        ("resources", *check_resources(blob, session, skip_github)),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit Supabase task rows (read-only).")
    ap.add_argument("--env", default="dev", choices=["dev", "prod"])
    ap.add_argument("--task-id", help="audit a single task")
    ap.add_argument("--enabled", action="store_true", help="only is_enabled=True rows")
    ap.add_argument("--competency", help="substring match on any criterias[*].name")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--skip-github", action="store_true", help="skip repo/gist reachability")
    ap.add_argument("--json", action="store_true",
                    help="emit machine JSON instead of the human report (single object for "
                         "--task-id, else an array). Same exit code.")
    a = ap.parse_args()

    import json
    import os
    import requests
    from infra.e2b.supabase_helpers import init_supabase

    supabase = init_supabase(a.env)

    q = supabase.table("tasks").select(SELECT)
    if a.task_id:
        q = q.eq("task_id", a.task_id)
    else:
        q = q.eq("status", "ready")
    if a.enabled:
        q = q.eq("is_enabled", True)
    if a.limit:
        q = q.limit(a.limit)
    rows = q.execute().data or []

    if a.competency:
        needle = a.competency.lower()
        rows = [
            r for r in rows
            if any(needle in str((c or {}).get("name", "")).lower()
                   for c in (r.get("criterias") or []) if isinstance(c, dict))
        ]
    if not rows:
        if a.json:
            print(json.dumps(None if a.task_id else []))
        else:
            print(f"No matching tasks in {a.env}.")
        return 0

    known_competency_ids = {
        str(c["competency_id"])
        for c in (supabase.table("competencies").select("competency_id").execute().data or [])
    }
    known_template_ids = {
        str(t["template_id"])
        for t in (supabase.table("templates").select("template_id").execute().data or [])
    }

    session = requests.Session()
    token = os.getenv("GITHUB_GIST_TOKEN") or os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    elif not a.skip_github and not a.json:
        print("WARNING: no GitHub token in env — reachability checks may 404 on private repos.\n")

    _VERDICT = {PASS: "pass", WARN: "warn", FAIL: "fail"}
    n_pass = n_warn = n_fail = 0
    failure_counts: dict[str, int] = {}
    reports = []   # one machine record per task (for --json)

    for row in rows:
        results = audit_row(row, known_competency_ids, known_template_ids, session, a.skip_github)
        worst = FAIL if any(r[1] == FAIL for r in results) else (
            WARN if any(r[1] == WARN for r in results) else PASS)
        if worst == FAIL:
            n_fail += 1
        elif worst == WARN:
            n_warn += 1
        else:
            n_pass += 1

        title = ((row.get("task_blob") or {}).get("title") or "<no title>")
        reports.append({
            "task_id": row["task_id"],
            "title": title,
            "verdict": _VERDICT[worst],
            "checks": {
                "pass": sum(1 for _, lv, _ in results if lv == PASS),
                "warn": sum(1 for _, lv, _ in results if lv == WARN),
                "fail": sum(1 for _, lv, _ in results if lv == FAIL),
            },
            "failures": [{"field": f, "detail": m} for f, lv, m in results if lv == FAIL],
            "warnings": [{"field": f, "detail": m} for f, lv, m in results if lv == WARN],
            "fields": {f: {"level": _VERDICT[lv], "detail": m} for f, lv, m in results},
        })

        if not a.json:
            print(f"{_MARK[worst]}  task_id: {row['task_id']}   title: {title!r}")
            for field, level, msg in results:
                print(f"      {_MARK[level]}  {field:<18} {msg}")
            print()
        for field, level, _ in results:
            if level == FAIL:
                failure_counts[field] = failure_counts.get(field, 0) + 1

    if a.json:
        # single object when a specific task was requested, else the array
        print(json.dumps(reports[0] if a.task_id else reports, indent=2))
        return 1 if n_fail else 0

    print("=" * 64)
    print(f"SUMMARY  {len(rows)} tasks   ✓ {n_pass} pass   ⚠ {n_warn} warn   ✗ {n_fail} fail")
    if failure_counts:
        print("\nMost common failures:")
        for field, count in sorted(failure_counts.items(), key=lambda kv: -kv[1]):
            print(f"    {field}: {count} task(s)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
