"""Inline candidate-tour generation for the task-creation pipeline.

Generates the ``tasks.tour`` JSONB walkthrough for every task the pipeline
creates, right after the E2B gate passes — grounded in the in-memory code
files (never a GitHub fetch), verified before it is ever persisted.

Self-contained by design: the one-off ``backfill_task_tours.py`` script was
the *spec* for this module (prompt shape, boilerplate, decision logic,
validation rules) but is reference-only and slated for deletion — nothing
here imports from it.

The core flow (``generate_tour``):

1. ``decide_kind`` — sandbox / local / skip. PR_REVIEW is skipped for now
   (tour design not finalised); infra-without-template is skipped because
   its sandbox can never boot. Everything else gets a tour.
2. ``render_code_files`` — in-memory files → one capped, priority-ordered
   text blob (README → config/build → source).
3. ``build_middle_prompt`` — ask the LLM for ONLY the task-specific middle
   sections (a bare JSON array); head/tail boilerplate is code-owned.
4. ``parse_middle`` + ``assemble_tour`` — deterministic validation: shape,
   size budget (whole tour ≤ 7 sections), variable allowlist, kind guards.
5. Verification: an LLM judge (``eval_tour``) + an empirical layer —
   ``run_tour_in_sandbox`` executes the commands in the gate's still-live
   sandbox (sandbox kind) / ``check_against_manifests`` cross-checks the
   commands against package.json / requirements.txt / pom.xml (local kind).
6. Retry with the failure as critique, up to ``MAX_TOUR_EVAL_RETRIES``.
   Exhausted → ``None``; the caller ships the task with ``tour = NULL``
   (a tour failure must never block a good task).

All LLM calls go through the Portkey gateway (``_clients.openai_client``).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from infra.logger_config import logger


# ------------------------------------------------------------------ config

# Tour generation + judge run on the OpenAI (GPT) Portkey client — same
# client family as the task-creation/answer-code steps. NB the confusing
# names in _clients.py: `openai_via_portkey` IS the OpenAI/GPT client;
# `openai_client` is Anthropic-via-Portkey (only used here if someone
# overrides TOUR_MODEL to a claude-* id).
# gpt-5.5 (not -nano): the nano tier can't reliably ground tour commands in the
# repo or apply the judge's grounding/candidate-safety rules — it flags fixed
# boilerplate it's told to ignore and emits self-contradictory critiques, which
# is what shipped most infra tasks with tour=NULL. The stronger model produces
# coherent, actionable verdicts and grounded tours. Override via env if needed.
TOUR_MODEL = os.getenv("TOUR_MODEL", "gpt-5.5")
TOUR_JUDGE_MODEL = os.getenv("TOUR_JUDGE_MODEL", "gpt-5.5")
MAX_TOUR_EVAL_RETRIES = int(os.getenv("MAX_TOUR_EVAL_RETRIES", "3"))
_MAX_TOKENS = 4000

# Hard size cap: a tour is orientation, not documentation. Fewer is fine;
# more fails validation and regenerates (never silently trimmed).
# Sandbox budget is 4 so a full infra task can carry build-and-run + run-tests +
# test-endpoints + seed-data without the judge's completeness demands colliding
# with the section cap (an unwinnable loop). Head(3)+tail(1)+middle(4) = 8.
MAX_TOUR_SECTIONS = 8
_MIDDLE_BUDGET = {"sandbox": 4, "local": 4}

# Prompt-size bounds for the file blob.
PER_FILE_CHAR_CAP = 8000
TOTAL_FILES_CHAR_CAP = 60000
MAX_FILES_RENDERED = 30

# Files that never help the model understand how to run the project.
SKIP_DIR_PARTS = {".git", "node_modules", "dist", "build", "vendor", "__pycache__",
                  ".next", "target", "coverage", ".venv", "venv", ".idea", ".vscode"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
              "go.sum", "Cargo.lock", "composer.lock"}
SKIP_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".pdf",
             ".zip", ".tar", ".gz", ".tgz", ".woff", ".woff2", ".ttf", ".eot",
             ".mp4", ".mov", ".mp3", ".wav", ".bin", ".so", ".dylib", ".class",
             ".jar", ".pyc", ".db", ".sqlite"}
# High-signal config/build/entrypoint files, rendered right after the README.
PRIORITY_FILES = {"docker-compose.yml", "docker-compose.yaml", "dockerfile",
                  "requirements.txt", "package.json", "pyproject.toml", "go.mod",
                  "pom.xml", "build.gradle", "makefile", "run.sh", "kill.sh",
                  ".env.example"}
PRIORITY_EXTS = {".sql", ".sh", ".yml", ".yaml", ".env"}

# The only template variables the candidate-app runtime can substitute.
ALLOWED_VARIABLES = [
    "repo.url",
    "repo.clone_url",
    "candidate.github_username",
    "sandbox.editor_url",
    "sandbox.terminal_url",
    "sandbox.db_console_url",
    "sandbox.preview_url",
]

_TASK_DIR = "/home/user/task"


# ------------------------------------------------------- boilerplate (code-owned)

# Head/tail sections are canonical constants: they carry platform facts the
# LLM cannot know from the repo (sandbox path, invite flow, submit mechanics)
# and must read identically on every task.
_EXPLORE_SANDBOX = {
    "id": "explore-code-base", "title": "Explore the code base", "steps": [
        {"type": "markdown", "body": "You are given a scenario. Explore the repository to understand it — a private copy is on GitHub and it is already cloned in your sandbox."},
        {"type": "link", "label": "Open your repository on GitHub", "url": "{{repo.url}}"}]}
_EXPLORE_LOCAL = {
    "id": "explore-code-base", "title": "Explore the code base", "steps": [
        {"type": "markdown", "body": "Accept the GitHub collaborator invite sent to {{candidate.github_username}} — you cannot push without it. Then open the repo to understand the scenario."},
        {"type": "link", "label": "Open your repository on GitHub", "url": "{{repo.url}}"}]}
_EDITOR = {
    "id": "access-code-editor", "title": "Access your environment via Code Editor", "steps": [
        {"type": "markdown", "body": "Your scenario is fully deployed in a sandbox. The link below opens a VS Code editor in your browser."},
        {"type": "link", "label": "Open the Code Editor (VS Code)", "url": "{{sandbox.editor_url}}"}]}
_TERMINAL = {
    "id": "access-terminal", "title": "Access your environment via Terminal", "steps": [
        {"type": "markdown", "body": "Your scenario is fully deployed in a sandbox. The link below gives you terminal access to it."},
        {"type": "link", "label": "Open the Terminal", "url": "{{sandbox.terminal_url}}"},
        {"type": "command", "label": "List your project files", "command": f"ls {_TASK_DIR}"}]}
_LOCAL_CLONE = {
    "id": "clone-repo", "title": "Clone the repo", "steps": [
        {"type": "command", "label": "Clone", "command": "git clone {{repo.clone_url}}"}]}
_SUBMIT_SANDBOX = {
    "id": "submit", "title": "Submit your work", "steps": [
        {"type": "markdown", "body": "You are graded from your pushed commits. Push your changes from the Terminal before you submit."},
        {"type": "command", "label": "Commit & push", "command": f"cd {_TASK_DIR} && git add -A && git commit -m \"solution\" && git push"}]}
_SUBMIT_LOCAL = {
    "id": "submit", "title": "Submit your work", "steps": [
        {"type": "markdown", "body": "Graded from your pushed commits. Commit and push from the cloned folder before you submit."},
        {"type": "command", "label": "Commit & push", "command": "git add -A && git commit -m \"solution\" && git push"}]}

TOUR_HEAD = {
    "sandbox": [_EXPLORE_SANDBOX, _EDITOR, _TERMINAL],
    "local": [_EXPLORE_LOCAL, _LOCAL_CLONE],
}
TOUR_TAIL = {
    "sandbox": [_SUBMIT_SANDBOX],
    "local": [_SUBMIT_LOCAL],
}
# Section ids owned by head/tail — silently dropped if the model emits them.
_BOILERPLATE_IDS = {"explore-code-base", "access-code-editor", "access-terminal",
                    "clone-repo", "get-starter", "submit", "submit-github", "submit-zip"}


# ------------------------------------------------------------------ kind

def decide_kind(meta: Dict[str, Any]) -> str:
    """Which tour shape this task needs — a router, not a filter.

    Ordered, first match wins:
      1. PR_REVIEW           → 'skip'    (deferred — tour design not finalised)
      2. infra + template    → 'sandbox' (candidate works in a browser sandbox)
      3. infra, no template  → 'skip'    (sandbox can never boot — a tour
                                          would promise surfaces that don't exist)
      4. everything else     → 'local'   (frontend / library-only: candidate
                                          clones and runs on their own machine)
    """
    types = meta.get("task_type") or []
    if isinstance(types, str):
        types = [types]
    if "PR_REVIEW" in types:
        return "skip"
    if meta.get("is_shared_infra_required") is True:
        return "sandbox" if meta.get("template_id") else "skip"
    return "local"


# ------------------------------------------------------------- file blob

def _file_priority(path: str) -> int:
    name = path.rsplit("/", 1)[-1].lower()
    ext = ("." + name.rsplit(".", 1)[-1]) if "." in name else ""
    depth = path.count("/")
    if name.startswith("readme"):
        return 0
    if name in PRIORITY_FILES:
        return 1
    if ext in PRIORITY_EXTS:
        return 2
    return 3 + min(depth, 5)


def _is_skippable(path: str) -> bool:
    parts = path.split("/")
    if any(p in SKIP_DIR_PARTS for p in parts[:-1]):
        return True
    name = parts[-1].lower()
    if name in SKIP_FILES:
        return True
    ext = ("." + name.rsplit(".", 1)[-1]) if "." in name else ""
    return ext in SKIP_EXTS


def _as_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, (dict, list)):
        return json.dumps(content, indent=2, ensure_ascii=False)
    return str(content)


def render_code_files(code_files: Dict[str, Any]) -> str:
    """Render the in-memory code files into the labelled blob the prompt
    consumes: a full file-tree listing (the model sees the whole structure),
    then contents as ``=== FILE: path ===`` blocks in priority order —
    README first, then config/build files, then source — under hard caps."""
    paths = {str(p).lstrip("/"): _as_text(c) for p, c in (code_files or {}).items()}

    listing = "\n".join(f"{p} ({len(c)}b)" for p, c in sorted(paths.items()))
    parts: List[str] = [f"=== FILE TREE ===\n{listing}\n"]
    total = len(parts[0])

    candidates = sorted(
        (p for p in paths if not _is_skippable(p)),
        key=lambda p: (_file_priority(p), p),
    )
    rendered = 0
    for path in candidates:
        if rendered >= MAX_FILES_RENDERED or total >= TOTAL_FILES_CHAR_CAP:
            break
        content = paths[path]
        if len(content) > PER_FILE_CHAR_CAP:
            content = content[:PER_FILE_CHAR_CAP] + "\n... [truncated]"
        block = f"=== FILE: {path} ===\n{content}\n"
        if total + len(block) > TOTAL_FILES_CHAR_CAP:
            continue
        parts.append(block)
        total += len(block)
        rendered += 1
    return "\n".join(parts)


def detect_task_dir(code_files: Dict[str, Any]) -> str:
    """Pick the working directory the tour should use so it matches the repo's
    OWN scripts LITERALLY (a weak judge won't honour "these paths are aliases").

    ``/home/user/task`` is the canonical sandbox clone path; ``/root/task`` is a
    symlink alias created in BOTH the deploy runtime (``sandbox_manager``) and the
    E2B gate (``sandbox_eval``), so either works at runtime. Some generated repos
    hardcode ``/root/task`` in ``run.sh`` / invariants; when they do, the tour
    must use the same path or the judge flags a (spurious) groundedness mismatch.
    Prefer what ``run.sh`` uses; fall back to the canonical default."""
    blob = ""
    for p, c in (code_files or {}).items():
        name = str(p).rsplit("/", 1)[-1].lower()
        if name in ("run.sh", "kill.sh") or name.endswith(".sh"):
            blob += _as_text(c) + "\n"
    if "/root/task" in blob and "/home/user/task" not in blob:
        return "/root/task"
    return _TASK_DIR


# ------------------------------------------------------------- surfaces

def surfaces_block(meta: Dict[str, Any]) -> str:
    """Describe the sandbox surfaces THIS task actually exposes (from
    ``expected_ports``), so the model links only real ones."""
    ports = meta.get("expected_ports")
    ports = ports if isinstance(ports, list) else []
    by_label = {p["label"]: p for p in ports if isinstance(p, dict) and p.get("label")}
    avail, forbidden = [], []
    for lbl, var in (("app_preview", "{{sandbox.preview_url}}"),
                     ("db_console", "{{sandbox.db_console_url}}")):
        p = by_label.get(lbl)
        if p:
            title = p.get("title") or lbl
            ins = f" — {p['instructions']}" if p.get("instructions") else ""
            avail.append(f"  - `{var}` → port {p.get('port')}, titled \"{title}\"{ins}")
        else:
            forbidden.append(var)
    lines = ["## Sandbox surfaces this task exposes (from expected_ports — link ONLY these)"]
    lines.append("\n".join(avail) if avail
                 else "  - only Terminal + Editor (already in the fixed steps); no preview or DB console.")
    if forbidden:
        lines.append(f"Do NOT use {', '.join(forbidden)} — this task does not expose them.")
    lines.append("When you link a surface, use its real title for the label, not a generic one.")
    return "\n".join(lines)


# ------------------------------------------------------------- prompt

SYSTEM_PROMPT = """You write candidate-facing "tours" for a hands-on technical assessment platform (Utkrusht). \
A tour is a short, ordered walkthrough that orients a candidate for a single assessment task. The fixed setup and \
submit steps are handled separately — your job is to write ONLY the task-specific middle sections, grounded in the \
task's actual files. Output JSON only — no prose, no markdown fences."""

_STEP_SCHEMA = '''A section is {"id": "<kebab-id>", "title": "<short title>", "steps": [<step>, ...]}.
A step is one of:
- markdown: {"type": "markdown", "body": "<text>"}
- link:     {"type": "link", "label": "<short label>", "url": "<url, may contain a {{variable}}>"}
- command:  {"type": "command", "label": "<short label>", "command": "<shell command>", "output": {"type": "markdown", "body": "<=3 lines, grounded in the repo's real values>"}}  (output optional)'''

_KIND_INTRO = {
    "sandbox": f"The candidate works in an ALREADY-DEPLOYED sandbox: the repo is cloned at {_TASK_DIR} and the "
               f"platform has already run the project's boot script, so its services (DB container, app process, etc.) "
               f"are ALREADY UP before the candidate arrives. `{_TASK_DIR}` and `/root/task` are the SAME directory "
               f"(the latter is a symlink alias); commands may use either. Do NOT tell the candidate to bring the "
               f"environment up from scratch — orient them to what is already running and how to re-apply their own "
               f"changes.",
    "local": "The candidate clones the repo to their OWN machine and works locally (no sandbox).",
}

_MIDDLE_GUIDANCE = {
    "sandbox": f"""GROUND EVERY COMMAND IN THE REPO'S OWN `run.sh` AND `docker-compose.yml`. The environment is
already deployed and running (see the intro); read `run.sh` to learn EXACTLY how this repo brings its services up —
mirror its Compose invocation form, its service names, its ports, and its paths. Do NOT guess or use a generic recipe.

Use Docker Compose v2 syntax — `docker compose` (a space), never the legacy `docker-compose` hyphen binary — UNLESS the
repo's own `run.sh` uses the hyphen form, in which case match the repo. Reference ONLY services that actually appear in
`docker-compose.yml`: if Compose defines only a datastore (e.g. just `postgres`) and the app runs as a host process,
do NOT invent an app service or tail app logs from Compose — start/inspect the app the way `run.sh` does.

Pick only the sections THIS repo needs, in this order, using these EXACT ids — and AT MOST {_MIDDLE_BUDGET['sandbox']}
sections total (fewer is better; keep the ones the candidate cannot succeed without, in this priority:
build-and-run > run-tests > seed-data > one inspection section):
- `build-and-run` — keep this MINIMAL and trivially grounded. The stack is ALREADY UP, so this section only orients
  the candidate and lets them confirm it: ONE markdown line saying the environment is already running, plus ONE
  status/health check that is unambiguously in the repo — `docker compose ps`, or a `curl` on the app's REAL health
  route/port. If a Compose service needs a nudge after a change, `docker compose restart <real-service>` (real service
  name from `docker-compose.yml`) is fine. Do NOT reconstruct a host process's start command, its `PYTHONPATH`/port/
  env exports, or any PID-file kill/restart logic — that is the boot script's job and any guess will be ungrounded.
  Do NOT tell the candidate to run `run.sh` itself, do NOT bring the whole stack up from scratch, and do NOT run the
  test suite or seed scripts here.
- `run-tests` — REQUIRED whenever the repo ships ANY test/verification material (a test suite, `invariants/`,
  `verification_*.sql`, a `validate.sh`, etc.): the repo's REAL verification command, shown in its current FAILING
  state first, with a one-line note to re-run after the fix. Do NOT name which individual tests/checks fail.
- `seed-data` — ONLY if the repo ships an EXPLICIT seed script the candidate must run themselves. If the data layer is
  seeded automatically at boot (e.g. `init_database.sql` mounted into the DB container, or a seed run by the boot
  script), the sandbox has ALREADY loaded it — do NOT add a seed-data section; at most note it in one line elsewhere.
- `inspect-database` — ONLY if the repo has a real SQL/Mongo database AND `{{{{sandbox.db_console_url}}}}` is an available
  surface. LINK-ONLY: the db-console link PLUS one markdown line with the real login read from docker-compose env.
  No psql/mongosh commands.
- `open-redis` — ONLY if the repo uses Redis: `cd {_TASK_DIR} && docker compose exec <SERVICE> redis-cli` (real service
  name), then a few orienting commands (`DBSIZE`, `SCAN 0 MATCH <real-prefix>:* COUNT 100`).
- `test-endpoints` — REQUIRED whenever the repo exposes HTTP routes AND `{{{{sandbox.preview_url}}}}` is an available
  surface. Lead with a docs link (`{{{{sandbox.preview_url}}}}/docs` for Swagger/OpenAPI) or a real route; may add one
  short curl check against a REAL route on the app's REAL port. Never invent a route, a port, or a response field.
If the deliverable is a design doc (e.g. DESIGN.md) rather than running code, emit a single `write-design` section instead.
Commands run in the sandbox at {_TASK_DIR}; use the real service names/ports/db/tables/files/endpoints from the repo.
The ONLY placeholders you may use are `{{{{sandbox.db_console_url}}}}` and `{{{{sandbox.preview_url}}}}`.""",
    "local": f"""Emit the run/test section(s) — what the candidate does in their cloned folder after cloning, before
submitting. Typically ONE `run-project` (or `run-tests`) section, AT MOST {_MIDDLE_BUDGET['local']} sections total.
The commands MUST match this repo's tech stack, read from its own manifest files:
- package.json → `npm install`, then the REAL script names from its `scripts` block (`npm run dev` only if a `dev`
  script exists; `npm start` only if `start` exists; `npm test` only if a test script exists).
- requirements.txt / pyproject.toml → `pip install -r requirements.txt`, then the real entrypoint
  (`uvicorn app.main:app`, `python main.py`); `pytest` only if tests exist.
- pom.xml / build.gradle → `mvn spring-boot:run` / `./gradlew bootRun`; `mvn test` / `./gradlew test`.
- go.mod → `go run .`; `go test ./...`.
Commands run LOCALLY in the cloned folder — NOT {_TASK_DIR}, and never `docker compose` unless the repo ships it.
Use NO `sandbox.*` placeholders.""",
}

# Compact shape examples (kept tiny — the guidance above carries the rules).
_MIDDLE_EXAMPLES = {
    "sandbox": json.dumps([{
        "id": "build-and-run", "title": "Run the app", "steps": [
            {"type": "markdown", "body": "The stack is already up (Postgres in Compose; the app runs as a host process). Re-apply your changes with the repo's own commands."},
            {"type": "command", "label": "Restart the app after a change",
             "command": f"cd {_TASK_DIR} && docker compose restart <real-service>",
             "output": {"type": "markdown", "body": "[+] Restarting 1/1\n ✔ Container task-db-1  Started"}},
            {"type": "command", "label": "Check services are healthy",
             "command": f"cd {_TASK_DIR} && docker compose ps"}]},
        {"id": "run-tests", "title": "Run the test suite", "steps": [
            {"type": "markdown", "body": "Your work is verified by the repo's test suite. Run it to see the current (failing) state first."},
            {"type": "command", "label": "Run the tests",
             "command": f"cd {_TASK_DIR} && python -m pytest -q",
             "output": {"type": "markdown", "body": "5 failed, 2 passed in 1.42s"}},
            {"type": "markdown", "body": "Re-run after each change until the suite is green."}]},
    ], indent=1),
    "local": json.dumps([{
        "id": "run-project", "title": "Run the project", "steps": [
            {"type": "markdown", "body": "In the cloned folder, install dependencies and start the dev server."},
            {"type": "command", "label": "Install dependencies", "command": "npm install"},
            {"type": "command", "label": "Start the dev server", "command": "npm run dev",
             "output": {"type": "markdown", "body": "VITE v5.2.0  ready in 412 ms\n➜  Local:   http://localhost:5173/"}}]},
    ], indent=1),
}


def build_middle_prompt(kind: str, meta: Dict[str, Any], repo_text: str,
                        critique: Optional[str] = None,
                        task_dir: str = _TASK_DIR) -> str:
    """Prompt for ONLY the dynamic middle sections (a JSON array); the fixed
    head/tail are assembled in code. ``critique`` carries the previous
    attempt's failure (judge verdict or the failing command's output).
    ``task_dir`` is the working directory the tour must use (matched to the
    repo's own ``run.sh``; see ``detect_task_dir``)."""
    surfaces = ("\n\n" + surfaces_block(meta)) if kind == "sandbox" else ""
    task_dir_line = (
        f"\n\n## Working directory\nRun every sandbox command from `{task_dir}` — this is the path THIS repo's own "
        f"`run.sh` uses. Use it verbatim and consistently; do NOT use any other task path.\n"
        if kind == "sandbox" else ""
    )
    critique_block = (
        f"\n\n## Your previous attempt FAILED verification — fix exactly this\n{critique}"
        if critique else ""
    )
    return f"""{_KIND_INTRO[kind]}
The tour's fixed setup and submit steps are already written. Generate ONLY the task-specific MIDDLE sections.

## Output
A JSON ARRAY of section objects — nothing else (no prose, no markdown fences).
{_STEP_SCHEMA}

## What to emit
{_MIDDLE_GUIDANCE[kind]}{surfaces}{task_dir_line}

## Rules
- Do NOT emit any boilerplate section (explore-code-base, access-code-editor, access-terminal, clone-repo, submit) —
  those are added for you.
- No "understand/explore/review the codebase" filler — every section is a concrete action.
- GROUND EVERY COMMAND, PATH, SERVICE NAME, AND PORT IN THE REPO'S OWN `run.sh` / `docker-compose.yml` / manifests.
  If you cannot point to where a command/service/port comes from in the repo files below, do not emit it. Mirror the
  repo's Compose form (`docker compose` unless its `run.sh` uses the hyphen) and its working directory exactly.
- Outputs are OPTIONAL and SHORT (<=3 lines), grounded in the repo's real values. NEVER invent package counts or
  reproduce install warnings / log dumps. Do NOT assert a specific response body, JSON field, row count, or metric
  value unless the repo SEEDS it deterministically — describe WHAT to check, not the exact value you expect back.
- Keep it tight: one short sentence per markdown body, few steps per section. Never invent a DB, endpoints, ports, or
  services the repo lacks; reference only services that actually appear in `docker-compose.yml`.
- NEVER reveal the solution or point at the fix. Do NOT name the specific bug, the exact line/function/file to change,
  which individual tests or checks fail (or why), or tell the candidate "fix <file>" / "make <test> pass". Showing the
  test suite FAILING IN AGGREGATE is fine; naming the failing tests/checks or the file that must be edited is a LEAK.
  Naming the general CLASS of files already disclosed by the task's own problem statement is fine ("the defects are in
  the Docker layer") — narrowing to ONE specific file/section is not. Orient only: how to run it and see its current
  failing state, never what to change. NEVER paste full or substantial file contents (a whole file or a large chunk of one) — short illustrative
  commands/snippets the candidate could type themselves are fine. Orient only — how to run the project and see its
  current (failing) state, not what to fix.

## Example MIDDLE sections (shape + tone — adapt to THIS repo, do not copy specifics)
{_MIDDLE_EXAMPLES[kind]}

## This task
Title: {meta.get('title') or '(none)'}
Question / scenario:
{meta.get('question') or '(none)'}

## Repository files
{repo_text}{critique_block}

Now output ONLY the JSON array of middle sections for this task."""


# ------------------------------------------------------------- parse / assemble

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
_VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")

_clone = lambda x: json.loads(json.dumps(x))  # noqa: E731


def parse_middle(raw: str, kind: str) -> List[Dict[str, Any]]:
    """Extract + validate the middle sections the model returned. Drops any
    boilerplate it emitted anyway; rejects filler and over-budget output."""
    text = _FENCE_RE.sub("", raw).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("no JSON array in model output")
    arr = json.loads(text[start:end + 1])
    if not isinstance(arr, list):
        raise ValueError("middle is not a JSON array")

    middle: List[Dict[str, Any]] = []
    for sec in arr:
        if not isinstance(sec, dict) or not sec.get("id") or not sec.get("title"):
            raise ValueError(f"bad section: {sec!r:.120}")
        sid = sec["id"]
        if sid in _BOILERPLATE_IDS:
            continue  # boilerplate is code-owned — ignore the model's version
        if "understand" in sid or "review-reference" in sid or sid in (
                "read-reference-material", "review-the-codebase"):
            raise ValueError(f"filler/redundant section not allowed: {sid}")
        steps = sec.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"section {sid!r} has no steps")
        for st in steps:
            if not isinstance(st, dict) or st.get("type") not in ("markdown", "link", "command"):
                raise ValueError(f"bad step in {sid!r}: {st!r:.120}")
        middle.append(sec)

    budget = _MIDDLE_BUDGET[kind]
    if len(middle) > budget:
        raise ValueError(
            f"middle exceeds the section budget: {len(middle)} > {budget} "
            f"(whole tour is capped at {MAX_TOUR_SECTIONS} sections — emit fewer, higher-value sections)"
        )
    return middle


def assemble_tour(kind: str, middle: List[Dict[str, Any]],
                  task_dir: str = _TASK_DIR) -> Dict[str, Any]:
    """Wrap the middle in the fixed head/tail and enforce the global rules:
    total-section cap, variable allowlist, and the kind guard (no sandbox.*
    vars in a local tour — they would hang the candidate app's tour panel).

    ``task_dir`` normalises EVERY task path in the assembled tour (head/tail
    boilerplate included) to the one the repo's own ``run.sh`` uses, so the
    whole tour is path-consistent and matches the repo literally."""
    sections = _clone(TOUR_HEAD[kind]) + middle + _clone(TOUR_TAIL[kind])
    if kind == "sandbox" and task_dir != _TASK_DIR:
        # Distinctive path strings — a plain rewrite over the serialized tour
        # normalises boilerplate + model output + any stray alias in one pass.
        sections = json.loads(json.dumps(sections).replace(_TASK_DIR, task_dir))
    if len(sections) > MAX_TOUR_SECTIONS:
        raise ValueError(
            f"tour exceeds the {MAX_TOUR_SECTIONS}-section cap ({len(sections)} sections)"
        )
    tour = {"enabled": True, "version": 1, "sections": sections}
    # Exclude Go-template dots (`docker ps --format '{{.Names}}'`) — shell
    # syntax, not tour variables.
    used = sorted({v for v in _VAR_RE.findall(json.dumps(tour)) if not v.startswith(".")})
    unknown = [v for v in used if v not in ALLOWED_VARIABLES]
    if unknown:
        raise ValueError(f"tour uses unknown template variables: {unknown}")
    if kind == "local":
        sandbox_vars = [v for v in used if v.startswith("sandbox.")]
        if sandbox_vars:
            raise ValueError(f"local tour must not use sandbox vars: {sandbox_vars}")
    tour["variables"] = used
    return tour


# ------------------------------------------------------------- verdicts

@dataclass
class Verdict:
    passed: bool
    critique: str = ""


# ------------------------------------------------- layer 3a: manifest check (local)

_NPM_RUN_RE = re.compile(r"\bnpm\s+run\s+([A-Za-z0-9:_-]+)")
_PIP_REQ_RE = re.compile(r"\bpip3?\s+install\s+-r\s+(\S+)")


def _has_tests(paths: List[str]) -> bool:
    for p in paths:
        name = p.rsplit("/", 1)[-1].lower()
        if name.startswith("test_") or name.endswith("_test.py") or name.endswith(".test.js") \
                or name.endswith(".test.ts") or name.endswith(".spec.js") or name.endswith(".spec.ts"):
            return True
        if "/tests/" in f"/{p}" or p.startswith("tests/") or "/test/" in f"/{p}":
            return True
    return False


def check_against_manifests(tour: Dict[str, Any], code_files: Dict[str, Any]) -> Verdict:
    """Deterministic stack check for LOCAL tours: every install/run/test
    command must be backed by the repo's own manifest files. No LLM."""
    paths = {str(p).lstrip("/"): _as_text(c) for p, c in (code_files or {}).items()}
    names = set(paths)

    pkg_scripts: Dict[str, Any] = {}
    if "package.json" in names:
        try:
            pkg_scripts = (json.loads(paths["package.json"]) or {}).get("scripts") or {}
        except (ValueError, AttributeError):
            pkg_scripts = {}

    problems: List[str] = []
    for sec in tour.get("sections", []):
        for st in sec.get("steps", []):
            if st.get("type") != "command":
                continue
            cmd = st.get("command") or ""
            for m in _NPM_RUN_RE.finditer(cmd):
                script = m.group(1)
                if "package.json" not in names:
                    problems.append(f"`npm run {script}` but the repo has no package.json")
                elif script not in pkg_scripts:
                    problems.append(
                        f"`npm run {script}` but package.json defines no '{script}' script "
                        f"(has: {sorted(pkg_scripts) or 'none'})"
                    )
            if re.search(r"\bnpm\s+(install|ci|test)\b", cmd) and "package.json" not in names:
                problems.append("npm command but the repo has no package.json")
            for m in _PIP_REQ_RE.finditer(cmd):
                if m.group(1).lstrip("./") not in names:
                    problems.append(f"`pip install -r {m.group(1)}` but that file is not in the repo")
            if re.search(r"\bpytest\b", cmd) and not _has_tests(list(names)):
                problems.append("`pytest` but the repo has no test files")
            if re.search(r"\bmvn\b", cmd) and "pom.xml" not in names:
                problems.append("`mvn` but the repo has no pom.xml")
            if re.search(r"(\./)?gradlew?\b", cmd) and not any(
                    n.startswith("build.gradle") for n in names):
                problems.append("gradle command but the repo has no build.gradle")
            if re.search(r"\bgo\s+(run|test|build)\b", cmd) and "go.mod" not in names:
                problems.append("go command but the repo has no go.mod")

    if problems:
        return Verdict(False, "stack mismatch: " + "; ".join(sorted(set(problems))))
    return Verdict(True, "")


# ------------------------------------------- layer 3b: live sandbox check (sandbox)

# REPL-style lines (DBSIZE, SCAN 0 MATCH ..., INFO keyspace) — these run inside
# redis-cli, not a shell; executing them verbatim would fail or hang.
_REPL_RE = re.compile(r"^[A-Z][A-Z0-9_]*(\s|$)")
_REDIS_EXEC_RE = re.compile(r"docker[- ]compose\s+exec\s+(?:-T\s+)?(\S+)\s+redis-cli\s*$")

_BUILD_TIMEOUT_S = int(os.getenv("TOUR_SANDBOX_BUILD_TIMEOUT_S", "600"))
_CMD_TIMEOUT_S = int(os.getenv("TOUR_SANDBOX_CMD_TIMEOUT_S", "120"))
_MISSING_MARKERS = ("command not found", "no such file or directory", "not recognized")


def _run(sandbox, cmd: str, timeout: int):
    """Run a command in the sandbox; return ``(exit_code, stdout, stderr)``.

    Real E2B ``commands.run`` RAISES ``CommandExitException`` on a non-zero
    exit (it does not return a result) — and a red test suite is the expected
    starting state for most tasks, so that exception is a normal outcome here.
    Normalise both paths into a plain tuple, exactly like the gate's own
    ``sandbox_eval._run``. Duck-typed on ``exit_code`` so tests don't need the
    ``e2b`` package installed.
    """
    try:
        r = sandbox.commands.run(cmd, timeout=timeout, user="root")
        return (getattr(r, "exit_code", 1),
                getattr(r, "stdout", "") or "", getattr(r, "stderr", "") or "")
    except Exception as e:  # noqa: BLE001 — normalised below; truly unknown re-raises
        code = getattr(e, "exit_code", None)
        if code is not None or type(e).__name__ == "CommandExitException":
            out = getattr(e, "stdout", "") or ""
            err = getattr(e, "stderr", "") or ""
            if code is None:
                m = re.search(r"code (\d+)", str(e))
                code = int(m.group(1)) if m else 1
                err = err or str(e)
            return code, out, err
        if "timeout" in str(e).lower() or "deadline" in str(e).lower():
            return 124, "", str(e)
        raise


def run_tour_in_sandbox(tour: Dict[str, Any], sandbox, meta: Dict[str, Any]) -> Verdict:
    """Execute the tour's command steps in the gate's still-live sandbox.

    Per-section expectations:
      * build-and-run / seed-data / test-endpoints / other: every executable
        command must exit 0.
      * run-tests: the command must RUN — a red (non-zero) result is the
        expected starting state; only a missing runner (exit 126/127 or a
        'command not found' marker) fails.
      * open-redis: the bare ``redis-cli`` REPL opener is replaced with a
        non-interactive ping probe; REPL-style steps (DBSIZE, SCAN…) are skipped.
      * Every port behind a linked {{sandbox.*}} surface must be listening.
    """
    problems: List[str] = []
    try:
        for sec in tour.get("sections", []):
            sid = sec.get("id", "")
            if sid in _BOILERPLATE_IDS or sid == "inspect-database":
                continue  # nothing executable (links / logins only)
            for st in sec.get("steps", []):
                if st.get("type") != "command":
                    continue
                cmd = (st.get("command") or "").strip()
                if not cmd or "{{" in cmd:
                    continue  # placeholder commands resolve at candidate runtime
                if _REPL_RE.match(cmd):
                    continue  # REPL-inner command — not a shell command
                repl_open = _REDIS_EXEC_RE.search(cmd)
                if repl_open:
                    svc = repl_open.group(1)
                    probe = f"cd {_TASK_DIR} && docker compose exec -T {svc} redis-cli ping"
                    code, out, err = _run(sandbox, probe, _CMD_TIMEOUT_S)
                    if code != 0:
                        problems.append(
                            f"[{sid}] redis probe failed for service '{svc}': "
                            f"{(err or out)[:300]}"
                        )
                    continue
                timeout = _BUILD_TIMEOUT_S if "--build" in cmd else _CMD_TIMEOUT_S
                code, out, err = _run(sandbox, cmd, timeout)
                combined = f"{out}\n{err}".lower()
                if sid == "run-tests":
                    if code in (126, 127) or any(m in combined for m in _MISSING_MARKERS):
                        problems.append(
                            f"[run-tests] test runner missing: `{cmd}` -> exit {code}: "
                            f"{(err or out)[:300]}"
                        )
                    continue  # red tests are the expected starting state
                if code != 0:
                    problems.append(
                        f"[{sid}] `{cmd}` failed (exit {code}): {(err or out)[:300]}"
                    )

        # Every linked sandbox surface must actually be listening.
        ports = {p.get("label"): p.get("port") for p in (meta.get("expected_ports") or [])
                 if isinstance(p, dict)}
        used_vars = set(tour.get("variables") or [])
        for var, label in (("sandbox.preview_url", "app_preview"),
                           ("sandbox.db_console_url", "db_console")):
            port = ports.get(label)
            if var in used_vars and port:
                probe = f"timeout 5 bash -c 'exec 3<>/dev/tcp/127.0.0.1/{port}'"
                code, _out, _err = _run(sandbox, probe, 15)
                if code != 0:
                    problems.append(
                        f"tour links {{{{{var}}}}} but nothing is listening on port {port}"
                    )
    except Exception as exc:  # noqa: BLE001 — a sandbox hiccup must not crash the pipeline
        return Verdict(False, f"sandbox verification error: {exc}")

    if problems:
        return Verdict(False, "sandbox check failed: " + " | ".join(problems))
    return Verdict(True, "")


# ------------------------------------------------------------- LLM plumbing

def _default_llm(prompt: str, model: str = None) -> str:
    """All LLM traffic goes through the Portkey gateway.

    Default is the OpenAI (GPT) client — the same one task creation's
    answer-code step uses. A claude-* model override routes to the Anthropic
    client instead. gpt-5.x rejects ``max_tokens`` and requires
    ``max_completion_tokens``; Anthropic is the reverse (mirrors the
    ``_token_kwargs`` split in ``infra/utils.generate_task_with_code``).
    """
    from flows.tech.stages.generate import _clients
    model = model or TOUR_MODEL
    if model.startswith("gpt-"):
        client = _clients.openai_via_portkey
        token_kwargs = {"max_completion_tokens": _MAX_TOKENS}
    else:
        client = _clients.openai_client
        token_kwargs = {"max_tokens": _MAX_TOKENS}
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        **token_kwargs,
    )
    return (resp.choices[0].message.content or "") if resp.choices else ""


_JUDGE_PROMPT = """You are a strict reviewer of candidate-facing assessment tours. Judge whether this tour is TRUE
and COMPLETE for this repository.

What the kinds mean (do NOT flag behaviour that IS the kind's design):
- kind=sandbox: the task is pre-deployed in a browser sandbox and the platform has ALREADY run the boot script, so the
  services are ALREADY UP. The candidate never clones. `/home/user/task` and `/root/task` are the SAME directory (the
  latter is a symlink alias) — treat them as equivalent and NEVER flag a `/root/task` vs `/home/user/task` mismatch,
  nor flag one because the repo's `run.sh` uses the other. A tour that shows how to RE-APPLY changes (restart a service
  / re-run the host process) is CORRECT — do NOT require it to bring the whole stack up from scratch.
- kind=local: the candidate accepts a GitHub collaborator invite, CLONES the repo to their OWN machine, works there,
  and pushes to submit. The explore/invite and clone-repo steps are CORRECT for this kind — never flag them.

`docker compose` (v2, a space) and `docker-compose` (v1, a hyphen) are EQUIVALENT invocations — do NOT flag one merely
because the repo's `run.sh` uses the other form; only flag a Compose command if the SERVICE it names is absent from
`docker-compose.yml`.

The sections with ids explore-code-base, access-code-editor, access-terminal, clone-repo, and submit are FIXED
code-owned boilerplate — assume they are correct and do NOT judge them. Judge ONLY the other (task-specific) sections.

Fail the tour if ANY of these hold in the task-specific sections:
- a command, service name, port, file path, DB name, or login does not exist in the repo (groundedness). NB: a path
  difference between `/root/task` and `/home/user/task`, or `docker compose` vs `docker-compose`, is NOT groundedness.
- the repo has a test/verification suite (test files, `invariants/`, `verification_*.sql`, `validate.sh`) but the tour
  has no run-tests section; HTTP routes plus an available preview surface but no test-endpoints (completeness). Do NOT
  require a seed-data section when the data is seeded automatically at boot (e.g. `init_database.sql` mounted into the
  DB, or a boot-script seed) — in a pre-deployed sandbox that data is ALREADY loaded and the candidate does not re-seed.
- a section covers a capability the repo lacks — a DB section with no DB, endpoints with no HTTP surface, a Compose
  service the repo does not define, or a predicted response field/value the repo does not deterministically produce
  (over-promising)
- kind mismatch: a local tour running things in a sandbox path or via `docker compose` the repo doesn't ship; a
  sandbox tour telling the candidate to clone, OR telling them to bring up / manually start services that the boot
  script already started (kind fit)
- commands don't match the tech stack's own manifests (stack fit)
- a section adds no real value — padding (compactness)
- the tour reveals the SOLUTION or points at the fix: naming the specific bug, the exact line/function to change,
  which individual tests or checks fail (or why), telling the candidate to "fix <file>" / "make <test> pass", a
  SPECIFIC file the defect lives in or must be edited (e.g. "the problem is in docker-compose.yml's healthcheck"
  or "edit api-entrypoint.sh"), or pasting full/substantial file contents (a code block reproducing a whole file or a
  large chunk of one) instead of a short illustrative command/snippet the candidate could type themselves. Showing the
  test suite failing IN AGGREGATE (e.g. "5 failed, 2 passed") is fine; listing the failing test/check names is a LEAK.
  Naming the
  general CLASS of files already disclosed by the task's own problem statement is fine (e.g. "fix the bugs in
  docker-compose.yml and the Dockerfiles" when the question already says the defects are in the Docker layer) —
  naming or narrowing to ONE specific file/section within that class is not. Orientation (how to run, how to see the
  current failing state, which general area to explore) is fine and expected (candidate-safety)

Tour kind: {kind}

## The tour (JSON)
{tour_json}

## Repository files
{repo_text}

Reply with ONLY a JSON object: {{"passed": true|false, "critique": "<empty if passed; otherwise the specific problems,
actionable enough to regenerate from>"}}"""


def eval_tour(tour: Dict[str, Any], repo_text: str, kind: str,
              llm: Optional[Callable[[str], str]] = None) -> Verdict:
    """LLM judge (layer 2) — scores the assembled tour against the repo blob.
    Unparseable judge output counts as a failure (never a silent pass)."""
    prompt = _JUDGE_PROMPT.format(
        kind=kind,
        tour_json=json.dumps(tour, indent=1, ensure_ascii=False),
        repo_text=repo_text,
    )
    raw = (llm or (lambda p: _default_llm(p, TOUR_JUDGE_MODEL)))(prompt)
    text = _FENCE_RE.sub("", raw or "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return Verdict(False, "judge output was not JSON")
    try:
        obj = json.loads(text[start:end + 1])
        return Verdict(bool(obj.get("passed")), str(obj.get("critique") or ""))
    except ValueError:
        return Verdict(False, "judge output was not valid JSON")


# ------------------------------------------------------------- entry point

def build_tour_meta(candidate: Dict[str, Any], template_id: Optional[str]) -> Dict[str, Any]:
    """Derive the tour-kind inputs from a pipeline candidate — the same
    functions the pipeline itself uses (``has_shared_infra_files`` for the
    infra/non-infra split, ``build_expected_ports`` for the surfaces), so the
    tour kind can never disagree with how the rest of the pipeline treats
    the task."""
    from infra.utils import has_shared_infra_files
    from flows.tech.stages.generate.expected_ports import build_expected_ports

    code = candidate.get("code_files", {}) or {}
    return {
        "task_type": ["BUILD"],
        "is_shared_infra_required": has_shared_infra_files(code),
        "template_id": template_id,
        "expected_ports": build_expected_ports(code),
        "title": candidate.get("title", "") or candidate.get("name", ""),
        "question": candidate.get("question", ""),
    }


def generate_tour(
    code_files: Dict[str, Any],
    meta: Dict[str, Any],
    sandbox: Any = None,
    llm: Optional[Callable[[str], str]] = None,
    judge: Optional[Callable[..., Verdict]] = None,
) -> Optional[Dict[str, Any]]:
    """Generate + verify the tour for one task. Returns the tour dict, or
    ``None`` (skip kind, or every retry failed) — the caller ships the task
    either way; a tour failure must never block a good task.

    ``sandbox`` is the E2B gate's still-live sandbox (sandbox kind only);
    ``llm`` / ``judge`` are injectable for tests.
    """
    kind = decide_kind(meta)
    if kind == "skip":
        logger.info("tour: kind=skip (%s) — no tour generated",
                    "PR_REVIEW deferred" if "PR_REVIEW" in str(meta.get("task_type")) else
                    "shared-infra without template")
        return None

    repo_text = render_code_files(code_files)
    task_dir = detect_task_dir(code_files)
    call_llm = llm or _default_llm
    call_judge = judge or (lambda t, r, k: eval_tour(t, r, k))

    critique: Optional[str] = None
    for attempt in range(1, MAX_TOUR_EVAL_RETRIES + 1):
        try:
            raw = call_llm(build_middle_prompt(kind, meta, repo_text, critique, task_dir))
            middle = parse_middle(raw, kind)
            tour = assemble_tour(kind, middle, task_dir)
        except (ValueError, json.JSONDecodeError) as exc:
            critique = f"your output failed validation: {exc}"
            logger.warning("tour attempt %d/%d: validation failed: %s",
                           attempt, MAX_TOUR_EVAL_RETRIES, exc)
            continue

        verdict = call_judge(tour, repo_text, kind)
        if verdict.passed:
            if kind == "sandbox" and sandbox is not None:
                verdict = run_tour_in_sandbox(tour, sandbox, meta)
            elif kind == "local":
                verdict = check_against_manifests(tour, code_files)

        if verdict.passed:
            logger.info("tour: generated + verified (kind=%s, attempt %d, sections=%s)",
                        kind, attempt, [s["id"] for s in tour["sections"]])
            return tour

        critique = verdict.critique
        logger.warning("tour attempt %d/%d failed verification: %s",
                       attempt, MAX_TOUR_EVAL_RETRIES, (critique or "")[:500])

    logger.warning("tour: all %d attempts failed — task ships without a tour (tour=NULL)",
                   MAX_TOUR_EVAL_RETRIES)
    return None
