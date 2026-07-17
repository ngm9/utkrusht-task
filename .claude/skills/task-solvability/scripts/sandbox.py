#!/usr/bin/env python
"""Sandbox helper for the `task-solvability` skill.

Thin, self-contained CLI over `infra.e2b.sandbox_manager` so the skill stays a
clean runbook. The CODING AGENT (Claude Code) is the solver — this script only
deploys the task, syncs files, runs commands, and tears down. No solving logic,
no headless agent.

Run from the repo root with the venv python:
    .venv/bin/python .claude/skills/task-solvability/scripts/sandbox.py <subcmd> ...

Subcommands:
    load    --task-id ID [--env dev]                 print task JSON (template, starter, test_cmd, has_problem)
    clone   --task-id ID [--env dev] --dest DIR      token-authed LOCAL clone of the starter (for native editing)
    deploy  --task-id ID [--env dev]                 boot sandbox + clone starter + run.sh; print {sandbox_id, test_cmd, ...}
    run     --sandbox SID --cmd "..."                exec in the sandbox task dir; prints output, exits with the cmd's code
    put     --sandbox SID --local PATH --remote PATH upload one file into the sandbox
    get     --sandbox SID --remote PATH              print a file from the sandbox
    diff    --sandbox SID                            git add -A && git diff (the agent's edits)
    tour    --task-id ID [--env dev] [--sandbox SID] print the task tour, vars resolved + steps flattened (walk to verify)
    kill    --sandbox SID                            tear the sandbox down
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Make `infra.*` importable + load .env, regardless of CWD (the script lives deep
# under .claude/skills/…/scripts/, so the repo root is parents[4]).
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
try:
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT / ".env", override=True)
except Exception:  # noqa: BLE001 — dotenv optional; env may already be set
    pass

_TASK_DIR = "/home/user/task"


# ── task load (ported minimal from the old runthrough/task_source) ──────────

def _default_test_cmd(template_id: str) -> str:
    tid = (template_id or "").lower()
    if "node" in tid or "js" in tid:
        return "npm test"
    if "go" in tid:
        return "go test ./..."
    if "rust" in tid:
        return "cargo test -- --test-threads=1"
    return "python -m pytest -q"   # python + default


def _first_str(*cands) -> str:
    for c in cands:
        if isinstance(c, str) and c.strip():
            return c.strip()
    return ""


def load_task(task_id: str, env: str = "dev") -> dict:
    """Fetch + parse a task row from Supabase into a plain dict. Raises on a task
    that can't be deployed (missing row / template / starter repo)."""
    from infra.e2b.supabase_helpers import init_supabase

    supabase = init_supabase(env)
    sel = "task_id, template_id, task_blob, readme_content, solutions, is_shared_infra_required, tour, expected_ports"
    res = supabase.table("tasks").select(sel).eq("task_id", task_id).execute()
    if not res.data:
        raise SystemExit(f"FATAL: task_id {task_id} not found in {env} Supabase")
    row = res.data[0]

    blob = row.get("task_blob") or {}
    resources = blob.get("resources") or {}
    readme = blob.get("readme_content") or row.get("readme_content") or {}
    if not isinstance(readme, dict):
        readme = {}
    problem = "\n\n".join(
        p for p in (readme.get("task_overview"), blob.get("question"))
        if isinstance(p, str) and p.strip()
    ).strip()
    solutions = blob.get("solutions") or row.get("solutions") or {}
    answer_repo = solutions.get("answer_repo") if isinstance(solutions, dict) else None
    template_id = _first_str(row.get("template_id"), blob.get("template_id"))
    starter_repo = _first_str(resources.get("github_repo"))
    tour = row.get("tour") if isinstance(row.get("tour"), dict) else None
    expected_ports = row.get("expected_ports") if isinstance(row.get("expected_ports"), list) else []

    if not template_id:
        raise SystemExit(f"FATAL: task {task_id} has no template_id — cannot boot a sandbox")
    if not starter_repo:
        raise SystemExit(f"FATAL: task {task_id} has no starter repo (task_blob.resources.github_repo)")

    return {
        "task_id": task_id,
        "template_id": template_id,
        "starter_repo": starter_repo,
        "answer_repo": answer_repo if isinstance(answer_repo, str) and answer_repo.strip() else None,
        "test_cmd": _default_test_cmd(template_id),
        "problem": problem,
        "has_problem": bool(problem),
        "is_shared_infra_required": bool(row.get("is_shared_infra_required")),
        "tour": tour,
        "has_tour": bool(tour and tour.get("sections")),
        "expected_ports": expected_ports,
    }


# ── task tour ────────────────────────────────────────────────────────────────

def resolve_tour_vars(spec: dict, sandbox_id: str | None) -> dict:
    """Resolve the tour template variables ({{repo.url}}, {{sandbox.*_url}}) to
    concrete values, GENERICALLY from the task's `expected_ports` — one
    `sandbox.<label>_url` per declared port role (terminal, editor, db_console,
    app_preview, …). Do NOT hardcode a fixed set of roles: a tour can reference any
    port the task exposes, so anything omitted here silently renders as a literal
    `{{…}}` for the candidate. sandbox.* need a live sandbox_id; without one they
    resolve to None (local/non-infra tasks have no e2b surfaces)."""
    def _url(port, url_params) -> str | None:
        if not sandbox_id or not port:
            return None
        url = f"https://{port}-{sandbox_id}.e2b.app"
        if url_params:
            from urllib.parse import urlencode
            url = f"{url}/?{urlencode(url_params)}"
        return url

    vars_: dict = {"repo.url": spec.get("starter_repo")}
    for p in spec.get("expected_ports") or []:
        if not isinstance(p, dict):
            continue
        label = str(p.get("label") or p.get("icon") or "").strip().lower()
        if not label:
            continue
        url = _url(p.get("port"), p.get("url_params") or {})
        vars_[f"sandbox.{label}_url"] = url
        # the tour uses `sandbox.preview_url` for the globe/app_preview role
        if label == "app_preview":
            vars_["sandbox.preview_url"] = url

    # fallbacks for the always-present template surfaces if a row omits expected_ports
    for label, dport in (("terminal", 7681), ("editor", 8443)):
        vars_.setdefault(f"sandbox.{label}_url", _url(dport, {} if label != "editor" else {"folder": _TASK_DIR}))
    return vars_


_VAR_RE = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")


def _leftover_vars(obj) -> set:
    """Recursively collect any {{var}} that survived substitution — the honest
    source of truth for `unresolved_variables` (never trust the known-keys list)."""
    found: set = set()
    if isinstance(obj, str):
        found.update(m.strip() for m in _VAR_RE.findall(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            found |= _leftover_vars(v)
    elif isinstance(obj, list):
        for v in obj:
            found |= _leftover_vars(v)
    return found


def _subst(s, vars_: dict):
    if not isinstance(s, str):
        return s
    for k, v in vars_.items():
        s = s.replace("{{" + k + "}}", v if isinstance(v, str) else ("" if v is None else str(v)))
    return s


def resolve_tour(spec: dict, sandbox_id: str | None) -> dict:
    """Return the tour with all {{vars}} substituted and steps flattened into a
    walkable list the agent can execute one by one. Command steps keep their
    expected `output`; link steps carry a resolved `url` + whether it's a sandbox
    surface (reachability-checkable) or the github repo (auth-gated)."""
    tour = spec.get("tour") or {}
    vars_ = resolve_tour_vars(spec, sandbox_id)
    out_sections = []
    for sec in tour.get("sections") or []:
        steps = []
        for st in sec.get("steps") or []:
            t = st.get("type")
            if t == "command":
                steps.append({"type": "command", "label": st.get("label"),
                              "command": _subst(st.get("command"), vars_),
                              "expected_output": ((st.get("output") or {}).get("body"))})
            elif t == "link":
                url = _subst(st.get("url"), vars_)
                steps.append({"type": "link", "label": st.get("label"), "url": url,
                              "is_sandbox_surface": isinstance(url, str) and ".e2b.app" in (url or ""),
                              "resolvable": "{{" not in (url or "")})
            else:  # markdown / other
                steps.append({"type": t, "body": _subst(st.get("body"), vars_)})
        out_sections.append({"id": sec.get("id"), "title": sec.get("title"), "steps": steps})
    # honest unresolved list: scan the RENDERED steps for any surviving {{var}}
    unresolved = sorted(_leftover_vars(out_sections))
    return {"enabled": tour.get("enabled", True), "has_tour": bool(out_sections),
            "variables": vars_, "unresolved_variables": unresolved, "sections": out_sections}


# ── sandbox ops ─────────────────────────────────────────────────────────────

def _connect(sandbox_id: str):
    from e2b import Sandbox
    return Sandbox.connect(sandbox_id)


def _run_in_sandbox(sb, cmd: str, timeout: int) -> tuple[int, str]:
    """Run a command in the task dir, normalizing the non-zero-exit exception."""
    from e2b import CommandExitException
    try:
        r = sb.commands.run(cmd, timeout=timeout, cwd=_TASK_DIR, user="root")
        return r.exit_code, (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if (r.stderr or "") else "")
    except CommandExitException as e:
        return getattr(e, "exit_code", 1), (getattr(e, "stdout", "") or "") + "\n" + (getattr(e, "stderr", "") or "")
    except Exception as exc:  # noqa: BLE001
        if "timeout" in str(exc).lower():
            return 124, f"command timed out: {exc}"
        raise


def cmd_load(a) -> int:
    print(json.dumps(load_task(a.task_id, a.env), indent=2))
    return 0


def cmd_clone(a) -> int:
    from infra.e2b.sandbox_manager import _authed_clone_url, _redact
    spec = load_task(a.task_id, a.env)
    authed = _authed_clone_url(spec["starter_repo"])
    subprocess.run(["rm", "-rf", a.dest], check=False)
    p = subprocess.run(["git", "clone", "--depth", "1", authed, a.dest],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"FATAL: clone failed: {_redact(p.stderr)[-300:]}")
    # scrub the token from .git/config so it never persists in the working copy
    subprocess.run(["git", "-C", a.dest, "remote", "set-url", "origin", spec["starter_repo"]], check=False)
    print(f"cloned starter -> {a.dest}")
    return 0


def cmd_deploy(a) -> int:
    from infra.e2b import sandbox_manager
    spec = load_task(a.task_id, a.env)
    handle = sandbox_manager.create_and_setup(
        template=spec["template_id"], repo_url=spec["starter_repo"], timeout_hours=a.timeout_hours,
    )
    print(json.dumps({
        "sandbox_id": handle.sandbox_id,
        "template_id": spec["template_id"],
        "test_cmd": spec["test_cmd"],
        "task_dir": _TASK_DIR,
        "ports": sorted(getattr(handle, "exposed_ports", {}) or {}),
        "has_problem": spec["has_problem"],
    }, indent=2))
    return 0


def cmd_run(a) -> int:
    from infra.e2b.sandbox_manager import _redact
    rc, out = _run_in_sandbox(_connect(a.sandbox), a.cmd, a.timeout)
    print(_redact(out))
    print(f"[exit {rc}]")
    return rc


def cmd_put(a) -> int:
    with open(a.local, "r", encoding="utf-8") as fh:
        content = fh.read()
    _connect(a.sandbox).files.write(a.remote, content)
    print(f"put {a.local} -> {a.remote}")
    return 0


def cmd_get(a) -> int:
    print(str(_connect(a.sandbox).files.read(a.remote)))
    return 0


def cmd_diff(a) -> int:
    from infra.e2b.sandbox_manager import _redact
    rc, out = _run_in_sandbox(_connect(a.sandbox),
                              f"cd {_TASK_DIR} && git add -A && git diff --cached", 60)
    print(_redact(out))
    return 0


def cmd_tour(a) -> int:
    """Print the task tour with variables resolved + steps flattened. Pass
    --sandbox to resolve the sandbox.* URLs (needed for infra tasks); omit it for
    local/non-infra tasks (sandbox.* stay None and link-to-sandbox steps are N/A).
    This does NOT execute anything — the agent walks the printed steps (run command
    steps via `run`/locally; reachability-check link steps) and grades them."""
    spec = load_task(a.task_id, a.env)
    if not spec["has_tour"]:
        print(json.dumps({"has_tour": False, "task_id": a.task_id, "env": a.env,
                          "note": "no tour on this row (tour column null/empty)"}, indent=2))
        return 0
    print(json.dumps(resolve_tour(spec, a.sandbox), indent=2))
    return 0


def cmd_kill(a) -> int:
    from infra.e2b import sandbox_manager
    sandbox_manager.kill(a.sandbox)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="task-solvability sandbox helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    def _task(sp):
        sp.add_argument("--task-id", required=True)
        sp.add_argument("--env", default="dev", choices=["dev", "prod"])

    s = sub.add_parser("load"); _task(s); s.set_defaults(fn=cmd_load)
    s = sub.add_parser("clone"); _task(s); s.add_argument("--dest", required=True); s.set_defaults(fn=cmd_clone)
    s = sub.add_parser("deploy"); _task(s); s.add_argument("--timeout-hours", type=float, default=1.0); s.set_defaults(fn=cmd_deploy)
    s = sub.add_parser("run"); s.add_argument("--sandbox", required=True); s.add_argument("--cmd", required=True); s.add_argument("--timeout", type=int, default=300); s.set_defaults(fn=cmd_run)
    s = sub.add_parser("put"); s.add_argument("--sandbox", required=True); s.add_argument("--local", required=True); s.add_argument("--remote", required=True); s.set_defaults(fn=cmd_put)
    s = sub.add_parser("get"); s.add_argument("--sandbox", required=True); s.add_argument("--remote", required=True); s.set_defaults(fn=cmd_get)
    s = sub.add_parser("diff"); s.add_argument("--sandbox", required=True); s.set_defaults(fn=cmd_diff)
    s = sub.add_parser("tour"); _task(s); s.add_argument("--sandbox", default=None); s.set_defaults(fn=cmd_tour)
    s = sub.add_parser("kill"); s.add_argument("--sandbox", required=True); s.set_defaults(fn=cmd_kill)

    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
