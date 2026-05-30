"""B5 reconciler — verify task artifacts still exist; mark drift.

For every ``tasks`` row with status='ready':

* Confirm the GitHub template repo at ``task_blob.resources.github_repo``
  is reachable. If gone (404 / not_found), flip the row to ``broken`` with
  an explanatory error.
* Confirm the gist at ``task_blob.resources.github_gist`` is reachable;
  flip to ``broken`` if missing.

For every ``tasks`` row with status='failed' older than
``--retention-days`` (default 7), delete the row + best-effort delete
any partial GitHub repos referenced on the row. v1 conservative default:
disabled unless ``--delete-failed`` is passed.

Run on a cron (daily):

    python scripts/reconcile_tasks.py --env dev
    python scripts/reconcile_tasks.py --env prod --delete-failed

Exit codes:
    0  success
    1  uncaught error (caller's monitor should alert)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import logging
import os
import sys
from typing import Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("reconcile_tasks")


GITHUB_API = "https://api.github.com"


def _github_headers() -> dict[str, str]:
    token = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN") or ""
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def repo_full_name_from_url(repo_url: str) -> str | None:
    """Extract ``owner/repo`` from a github.com URL."""
    if not repo_url:
        return None
    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    return f"{parts[0]}/{parts[1]}"


def gist_id_from_url(gist_url: str) -> str | None:
    if not gist_url:
        return None
    parsed = urlparse(gist_url)
    parts = [p for p in parsed.path.split("/") if p]
    # gist URLs look like https://gist.github.com/owner/<gist_id>
    return parts[-1] if parts else None


def check_repo(repo_url: str) -> tuple[bool, str | None]:
    """Returns (exists, error_message_if_not)."""
    name = repo_full_name_from_url(repo_url)
    if not name:
        return True, None  # nothing to check
    try:
        resp = requests.get(f"{GITHUB_API}/repos/{name}", headers=_github_headers(), timeout=10)
    except requests.RequestException as exc:
        return True, f"network error: {exc}"  # don't flip broken on transient net issues
    if resp.status_code == 200:
        return True, None
    if resp.status_code == 404:
        return False, "repo 404"
    return True, f"unexpected status {resp.status_code}"


def check_gist(gist_url: str) -> tuple[bool, str | None]:
    gist_id = gist_id_from_url(gist_url)
    if not gist_id:
        return True, None
    token = os.getenv("GITHUB_GIST_TOKEN") or os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN") or ""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    try:
        resp = requests.get(f"{GITHUB_API}/gists/{gist_id}", headers=headers, timeout=10)
    except requests.RequestException as exc:
        return True, f"network error: {exc}"
    if resp.status_code == 200:
        return True, None
    if resp.status_code == 404:
        return False, "gist 404"
    return True, f"unexpected status {resp.status_code}"


def reconcile_ready_tasks(sb: Any, limit: int = 1000) -> dict[str, int]:
    """Walk ready rows and mark broken ones. Returns counts."""
    counts = {"scanned": 0, "broken": 0, "ok": 0, "errors": 0}

    rows = (
        sb.table("tasks")
        .select("id, task_blob")
        .eq("status", "ready")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    ).data or []

    for row in rows:
        counts["scanned"] += 1
        blob = row.get("task_blob") or {}
        resources = blob.get("resources") or {}
        repo_url = resources.get("github_repo") or ""
        gist_url = resources.get("github_gist") or ""

        try:
            repo_ok, repo_err = check_repo(repo_url)
            gist_ok, gist_err = check_gist(gist_url)
        except Exception as exc:
            logger.warning("reconcile %s scan failed: %s", row["id"], exc)
            counts["errors"] += 1
            continue

        if repo_ok and gist_ok:
            counts["ok"] += 1
            continue

        reason_parts = []
        if not repo_ok:
            reason_parts.append(f"github_repo: {repo_err}")
        if not gist_ok:
            reason_parts.append(f"github_gist: {gist_err}")
        reason = "; ".join(reason_parts)

        broken_blob = dict(blob)
        broken_blob["reconciler_error"] = reason
        broken_blob["reconciled_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        sb.table("tasks").update({"status": "broken", "task_blob": broken_blob}).eq("id", row["id"]).execute()
        counts["broken"] += 1
        logger.warning("marked task %s broken: %s", row["id"], reason)

    return counts


def delete_old_failed_tasks(sb: Any, retention_days: int = 7) -> int:
    """Delete failed task rows older than ``retention_days``. Best-effort
    delete of any GitHub repos referenced on the row first.
    """
    cutoff = (
        _dt.datetime.now(_dt.timezone.utc)
        - _dt.timedelta(days=retention_days)
    ).isoformat()

    rows = (
        sb.table("tasks")
        .select("id, task_blob")
        .eq("status", "failed")
        .lte("created_at", cutoff)
        .limit(500)
        .execute()
    ).data or []

    deleted = 0
    for row in rows:
        blob = row.get("task_blob") or {}
        resources = blob.get("resources") or {}
        for url_key in ("github_repo",):
            url = resources.get(url_key) or ""
            name = repo_full_name_from_url(url)
            if name:
                try:
                    requests.delete(
                        f"{GITHUB_API}/repos/{name}",
                        headers=_github_headers(), timeout=10,
                    )
                except Exception as exc:
                    logger.warning("delete repo %s failed: %s", name, exc)
        try:
            sb.table("tasks").delete().eq("id", row["id"]).execute()
            deleted += 1
        except Exception as exc:
            logger.warning("delete failed task %s: %s", row["id"], exc)
    return deleted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("dev", "prod"), default="dev")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Max ready rows to scan per run.")
    parser.add_argument("--delete-failed", action="store_true",
                        help="Also delete failed rows + their partial GitHub repos.")
    parser.add_argument("--retention-days", type=int, default=7,
                        help="Failed rows older than this are eligible for delete.")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    from generators.task.persistence import init_supabase
    sb = init_supabase(args.env)

    counts = reconcile_ready_tasks(sb, limit=args.limit)
    logger.info("reconciler: ready-scan %s", counts)

    if args.delete_failed:
        deleted = delete_old_failed_tasks(sb, retention_days=args.retention_days)
        logger.info("reconciler: deleted %d failed rows", deleted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
