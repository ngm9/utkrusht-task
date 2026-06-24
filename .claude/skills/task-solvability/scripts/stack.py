#!/usr/bin/env python
"""Stack driver for the FULL frontend→backend candidate flow (the `--frontend` mode
of the task-solvability skill).

Encapsulates the deterministic infra so the agent doesn't re-derive it each run:
  - `up`      : verify the flask backend (:4000) is reachable; start the Next FE in
                a node:22 Docker container on :3000 (the host's node segfaults Next 16's
                swc, so we run it in a clean Debian container).
  - `session` : create a candidate task_session via flask `POST /v2/task-sessions`
                with the candidate JWT, then CLEAR the three gates that block the
                landing (org free-trial expiry, position/session valid_till) and
                print the candidate URL to drive.
  - `down`    : stop the FE container.

Run from the repo root with the venv python. Requires CANDIDATE_JWT in .env.

NOTE: the agent still drives the gate CLICKS + the solve (those need the model).
This script only stands the stack up + mints a drivable session. The candidate
frontend's provisioning screen streams live logs heavily and can hang a headless
browser — the code-server solve is recorded separately (see SKILL.md).
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
try:
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT / ".env", override=True)
except Exception:  # noqa: BLE001
    pass

import os

_ASSESSMENT_REPO = Path("/home/rsx/Desktop/utkrusht-ai/utkrushta-assessment")
_FE_CONTAINER = "utk-fe"
_FLASK = "http://localhost:4000"
_FE = "http://localhost:3000"


def _http_code(url: str, timeout: int = 3) -> int:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return 0


def cmd_up(a) -> int:
    flask = _http_code(_FLASK)
    print(f"flask backend :4000 -> {flask}" + ("" if flask else "  (DOWN — run: docker compose -f /home/rsx/Desktop/utkrusht-ai/Utkrushta/docker-compose.local.yml up -d)"))
    fe = _http_code(_FE)
    if fe:
        print(f"FE :3000 already up -> {fe}")
        return 0
    # is the container there but not ready?
    subprocess.run(["docker", "rm", "-f", _FE_CONTAINER], capture_output=True)
    print("starting FE in node:22-bookworm (host network, mounted repo)...")
    subprocess.run([
        "docker", "run", "-d", "--name", _FE_CONTAINER, "--network", "host",
        "-v", f"{_ASSESSMENT_REPO}:/app", "-w", "/app",
        "node:22-bookworm",
        "bash", "-lc", "corepack enable >/dev/null 2>&1; pnpm exec next dev --turbopack -H 0.0.0.0 -p 3000",
    ], check=False)
    # poll up to ~60s
    import time as _t  # noqa
    for i in range(12):
        _t.sleep(8)
        if _http_code(_FE):
            print(f"FE :3000 ready after ~{(i+1)*8}s")
            return 0
    print("FE did not become ready in 96s — check: docker logs utk-fe")
    return 1


def cmd_down(a) -> int:
    subprocess.run(["docker", "rm", "-f", _FE_CONTAINER], check=False)
    print("FE container stopped")
    return 0


def cmd_session(a) -> int:
    from infra.e2b.supabase_helpers import init_supabase
    jwt = os.environ.get("CANDIDATE_JWT", "").strip().strip('"').strip("'")
    if not jwt:
        raise SystemExit("FATAL: CANDIDATE_JWT not in .env (mint a candidate token: HS256 {role:'candidate',userId} with JWT_SECRET)")

    sb = init_supabase(a.env)
    cls = sb.table("classes").select("position").eq("class_id", a.class_id).execute().data[0]
    pos_id = a.position_id or cls["position"]
    org = sb.table("positions").select("organization_id").eq("position_id", pos_id).execute().data[0]["organization_id"]

    # --- create the session via the real backend (builds the correct question_blob) ---
    body = json.dumps({
        "users": [{"user_id": a.user_id}],
        "task_ids": [a.task_id],
        "class_id": a.class_id,
        "position_id": pos_id,
        "mode": "interview",
    }).encode()
    req = urllib.request.Request(
        f"{_FLASK}/v2/task-sessions", data=body, method="POST",
        headers={"Authorization": f"Bearer {jwt}", "X-Token-Source": "candidate", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    sess = resp["task_sessions"][0]["tasksession_id"]

    # --- clear the gates (dev test data) ---
    till = "2026-12-31T23:59:59+00:00"
    now = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc).isoformat()
    # 1) org free-trial: extend trial_ends_at so canUseResource('tasks') passes
    hist = sb.table("organization_plan_history").select("organization_plan_history_id").eq("organization_id", org).is_("ends_at", "null").execute().data
    for h in hist:
        sb.table("organization_plan_history").update({"trial_ends_at": till}).eq("organization_plan_history_id", h["organization_plan_history_id"]).execute()
    # 2) position + session validity
    sb.table("positions").update({"valid_till": till}).eq("position_id", pos_id).execute()
    sb.table("task_sessions").update({"valid_from": now, "valid_till": till}).eq("tasksession_id", sess).execute()

    url = f"{_FE}/task/{a.class_id}/interview/{sess}?task_ids={a.task_id}"
    print(json.dumps({"tasksession_id": sess, "candidate_url": url, "org": org}, indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="task-solvability stack driver (frontend+session)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("up").set_defaults(fn=cmd_up)
    sub.add_parser("down").set_defaults(fn=cmd_down)
    s = sub.add_parser("session")
    s.add_argument("--task-id", required=True)
    s.add_argument("--class-id", required=True)
    s.add_argument("--position-id", default=None)
    s.add_argument("--user-id", default="7c3ec160-c4ed-4d5f-a689-4a9ab0745d7d")
    s.add_argument("--env", default="dev", choices=["dev", "prod"])
    s.set_defaults(fn=cmd_session)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
