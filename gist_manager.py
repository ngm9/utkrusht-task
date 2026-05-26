"""
gist_manager.py — GitHub Gist management script for Utkrushta tasks.

Commands:
  sync-prod-to-dev           Copy github_gist URLs from every prod task to the
                             matching dev task (same task_id). Skips tasks that
                             already have a gist in dev.

  create-prod-missing-gists  Find every prod task without a github_gist and
                             create one from its github_repo. Updates prod DB.

  create --task-ids ID ...   Create a fresh gist from the task's github_repo and
           --env dev|prod    write the URL back to task_blob.resources.github_gist.
           [--force]         Supports bulk (multiple IDs). Use --force to overwrite
                             an existing gist URL.

  sync-is-enabled            Mirror is_enabled=True from prod to dev.
                             Tasks enabled in prod → enabled in dev.
                             All other dev tasks → is_enabled=False.

Usage examples:
  python gist_manager.py sync-prod-to-dev
  python gist_manager.py create-prod-missing-gists
  python gist_manager.py create --task-ids abc123 def456 --env dev
  python gist_manager.py create --task-ids abc123 --env prod --force
  python gist_manager.py sync-is-enabled
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from supabase import Client, create_client

from infra.logger_config import logger
from infra.utils import create_gist_from_template

load_dotenv()

GITHUB_UTKRUSHTAPPS_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
GITHUB_GIST_TOKEN = os.getenv("GITHUB_GIST_TOKEN")

# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client for the given environment."""
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")

    return create_client(url, key)


def _task_id_column(supabase: Client) -> str:
    """
    Return the primary-key column name for the tasks table.
    The DB may use 'task_id' or 'id'; we probe once and cache.
    """
    # Try fetching one row and inspect its keys.
    result = supabase.table("tasks").select("*").limit(1).execute()
    if result.data:
        row = result.data[0]
        if "task_id" in row:
            return "task_id"
        if "id" in row:
            return "id"
    return "task_id"  # fallback


def fetch_all_tasks(supabase: Client, pk_col: str, columns: str = "") -> list[dict]:
    """
    Fetch every row from the tasks table (paginated in chunks of 1000).

    Args:
        columns: Comma-separated column names to select. Defaults to
                 "{pk_col},task_blob" when empty.
    """
    select_cols = columns if columns else f"{pk_col},task_blob"
    all_tasks = []
    page = 0
    page_size = 1000
    while True:
        result = (
            supabase.table("tasks")
            .select(select_cols)
            .range(page * page_size, (page + 1) * page_size - 1)
            .execute()
        )
        batch = result.data or []
        all_tasks.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return all_tasks


def get_task_by_id(supabase: Client, task_id: str, pk_col: str) -> dict | None:
    """Fetch a single task row by its primary key."""
    result = supabase.table("tasks").select("*").eq(pk_col, task_id).execute()
    if result.data:
        return result.data[0]
    return None


def update_task_gist_url(supabase: Client, task_id: str, gist_url: str, pk_col: str) -> bool:
    """
    Write gist_url into task_blob.resources.github_gist for the given task.
    Fetches the current task_blob, patches it, and writes it back.
    """
    task = get_task_by_id(supabase, task_id, pk_col)
    if not task:
        logger.error(f"[update] Task {task_id} not found — cannot update gist URL")
        return False

    task_blob = task.get("task_blob") or {}
    resources = task_blob.get("resources") or {}
    resources["github_gist"] = gist_url
    task_blob["resources"] = resources

    result = (
        supabase.table("tasks")
        .update({"task_blob": task_blob})
        .eq(pk_col, task_id)
        .execute()
    )
    if result.data:
        return True
    logger.error(f"[update] Supabase update returned no data for task {task_id}")
    return False


# ---------------------------------------------------------------------------
# Command 1: sync prod → dev
# ---------------------------------------------------------------------------

def sync_prod_gists_to_dev() -> None:
    """
    Iterate every task in prod. For tasks that have a github_gist URL, copy
    that URL to the matching dev task (same task_id) if dev doesn't have one yet.
    """
    print("=" * 70)
    print("  SYNC: Prod gist URLs → Dev tasks")
    print("  Reads ALL prod tasks · writes missing gist URLs to dev")
    print("=" * 70)

    prod_supabase = init_supabase("prod")
    dev_supabase = init_supabase("dev")

    # Detect PK column name from prod (assume same schema in dev)
    pk_col = _task_id_column(prod_supabase)
    logger.info(f"Using primary key column: '{pk_col}'")

    print("Fetching all tasks from prod…")
    prod_tasks = fetch_all_tasks(prod_supabase, pk_col)
    print(f"Found {len(prod_tasks)} task(s) in prod.\n")

    synced = 0
    skipped_no_gist = 0
    skipped_already_has_gist = 0
    not_found_in_dev = 0
    failed = 0

    for prod_task in prod_tasks:
        task_id = prod_task.get(pk_col)
        task_blob = prod_task.get("task_blob") or {}
        resources = task_blob.get("resources") or {}
        prod_gist_url = resources.get("github_gist")

        if not prod_gist_url:
            skipped_no_gist += 1
            continue

        # Check dev task
        dev_task = get_task_by_id(dev_supabase, task_id, pk_col)
        if not dev_task:
            logger.warning(f"[sync] Task {task_id} not found in dev — skipping")
            not_found_in_dev += 1
            continue

        dev_task_blob = dev_task.get("task_blob") or {}
        dev_resources = dev_task_blob.get("resources") or {}
        dev_gist_url = dev_resources.get("github_gist")

        if dev_gist_url:
            logger.info(f"[sync] Task {task_id} already has gist in dev — skipping")
            skipped_already_has_gist += 1
            continue

        ok = update_task_gist_url(dev_supabase, task_id, prod_gist_url, pk_col)
        if ok:
            logger.info(f"[sync] Task {task_id} → gist synced: {prod_gist_url}")
            synced += 1
        else:
            logger.error(f"[sync] Task {task_id} → update failed")
            failed += 1

    print()
    print("=" * 70)
    print("  SYNC COMPLETE")
    print(f"  Synced               : {synced}")
    print(f"  Skipped (no prod gist): {skipped_no_gist}")
    print(f"  Skipped (dev has gist): {skipped_already_has_gist}")
    print(f"  Not found in dev     : {not_found_in_dev}")
    print(f"  Failed               : {failed}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Command 2: create gists for specific task IDs
# ---------------------------------------------------------------------------

def create_gists_for_tasks(task_ids: list[str], env: str, force: bool = False) -> None:
    """
    For each task_id, fetch the task from the given env, derive the github_repo
    URL, call create_gist_from_template, and write the result back to the DB.

    Args:
        task_ids: One or more task UUIDs.
        env:      "dev" or "prod".
        force:    If True, overwrite an existing github_gist URL.
    """
    print("=" * 70)
    print(f"  CREATE GISTS — env={env}  force={force}")
    print(f"  Task IDs: {task_ids}")
    print("=" * 70)

    if not GITHUB_UTKRUSHTAPPS_TOKEN:
        print("[ERROR] GITHUB_UTKRUSHTAPPS_TOKEN is not set — cannot read template repos.")
        sys.exit(1)
    if not GITHUB_GIST_TOKEN:
        print("[ERROR] GITHUB_GIST_TOKEN is not set — cannot create gists.")
        sys.exit(1)

    supabase = init_supabase(env)
    pk_col = _task_id_column(supabase)
    logger.info(f"Using primary key column: '{pk_col}'")

    created = 0
    skipped = 0
    failed = 0

    for task_id in task_ids:
        task_id = task_id.strip()
        if not task_id:
            continue

        print(f"\n--- Task {task_id} ---")

        task = get_task_by_id(supabase, task_id, pk_col)
        if not task:
            logger.error(f"[create] Task {task_id} not found in {env}")
            failed += 1
            continue

        task_blob = task.get("task_blob") or {}
        resources = task_blob.get("resources") or {}
        github_repo = resources.get("github_repo")
        existing_gist = resources.get("github_gist")

        if not github_repo:
            logger.error(f"[create] Task {task_id} has no github_repo in task_blob.resources — skipping")
            failed += 1
            continue

        if existing_gist and not force:
            logger.info(f"[create] Task {task_id} already has gist: {existing_gist} — use --force to overwrite")
            skipped += 1
            continue

        logger.info(f"[create] Creating gist from repo: {github_repo}")
        gist_url = create_gist_from_template(
            repo_url=github_repo,
            repo_token=GITHUB_UTKRUSHTAPPS_TOKEN,
            gist_token=GITHUB_GIST_TOKEN,
        )

        if not gist_url:
            logger.error(f"[create] Failed to create gist for task {task_id}")
            failed += 1
            continue

        ok = update_task_gist_url(supabase, task_id, gist_url, pk_col)
        if ok:
            logger.info(f"[create] Task {task_id} → gist created and saved: {gist_url}")
            created += 1
        else:
            logger.error(f"[create] Task {task_id} → gist created ({gist_url}) but DB update failed")
            failed += 1

    print()
    print("=" * 70)
    print("  CREATE COMPLETE")
    print(f"  Created  : {created}")
    print(f"  Skipped  : {skipped}  (already had gist; use --force to overwrite)")
    print(f"  Failed   : {failed}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Command 3: create gists for all prod tasks that are missing one
# ---------------------------------------------------------------------------

def create_prod_gists_for_missing() -> None:
    """
    Scan every task in prod. For tasks that have a github_repo but no
    github_gist, create a gist and write it back to prod.
    """
    print("=" * 70)
    print("  CREATE MISSING PROD GISTS")
    print("  Scans ALL prod tasks · creates gists where github_gist is absent")
    print("=" * 70)

    if not GITHUB_UTKRUSHTAPPS_TOKEN:
        print("[ERROR] GITHUB_UTKRUSHTAPPS_TOKEN is not set — cannot read template repos.")
        sys.exit(1)
    if not GITHUB_GIST_TOKEN:
        print("[ERROR] GITHUB_GIST_TOKEN is not set — cannot create gists.")
        sys.exit(1)

    prod_supabase = init_supabase("prod")
    pk_col = _task_id_column(prod_supabase)
    logger.info(f"Using primary key column: '{pk_col}'")

    print("Fetching all tasks from prod…")
    prod_tasks = fetch_all_tasks(prod_supabase, pk_col)
    print(f"Found {len(prod_tasks)} task(s) in prod.\n")

    created = 0
    skipped_has_gist = 0
    skipped_no_repo = 0
    failed = 0

    for prod_task in prod_tasks:
        task_id = prod_task.get(pk_col)
        task_blob = prod_task.get("task_blob") or {}
        resources = task_blob.get("resources") or {}
        existing_gist = resources.get("github_gist")
        github_repo = resources.get("github_repo")

        if existing_gist:
            skipped_has_gist += 1
            continue

        if not github_repo:
            logger.warning(f"[create-missing] Task {task_id} has no github_repo — skipping")
            skipped_no_repo += 1
            continue

        logger.info(f"[create-missing] Task {task_id} — creating gist from {github_repo}")
        gist_url = create_gist_from_template(
            repo_url=github_repo,
            repo_token=GITHUB_UTKRUSHTAPPS_TOKEN,
            gist_token=GITHUB_GIST_TOKEN,
        )

        if not gist_url:
            logger.error(f"[create-missing] Task {task_id} — gist creation failed")
            failed += 1
            continue

        ok = update_task_gist_url(prod_supabase, task_id, gist_url, pk_col)
        if ok:
            logger.info(f"[create-missing] Task {task_id} → saved: {gist_url}")
            created += 1
        else:
            logger.error(f"[create-missing] Task {task_id} → gist created ({gist_url}) but DB update failed")
            failed += 1

    print()
    print("=" * 70)
    print("  CREATE MISSING PROD GISTS COMPLETE")
    print(f"  Created              : {created}")
    print(f"  Skipped (had gist)   : {skipped_has_gist}")
    print(f"  Skipped (no repo)    : {skipped_no_repo}")
    print(f"  Failed               : {failed}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Command 4: sync is_enabled from prod → dev
# ---------------------------------------------------------------------------

def sync_is_enabled_to_dev() -> None:
    """
    Mirror is_enabled from prod to dev:
      - Dev tasks whose task_id appears as is_enabled=True in prod → is_enabled=True
      - All other dev tasks → is_enabled=False
    """
    print("=" * 70)
    print("  SYNC is_enabled: Prod → Dev")
    print("  Prod enabled tasks → enabled in dev · all other dev tasks → disabled")
    print("=" * 70)

    prod_supabase = init_supabase("prod")
    dev_supabase = init_supabase("dev")

    pk_col = _task_id_column(prod_supabase)
    logger.info(f"Using primary key column: '{pk_col}'")

    # 1. Collect all task_ids that are is_enabled=True in prod
    print("Fetching is_enabled status from prod…")
    prod_tasks = fetch_all_tasks(prod_supabase, pk_col, columns=f"{pk_col},is_enabled")
    prod_enabled_ids = {
        t[pk_col]
        for t in prod_tasks
        if t.get("is_enabled") is True
    }
    print(f"Found {len(prod_tasks)} prod task(s) · {len(prod_enabled_ids)} are enabled.\n")

    # 2. Fetch all dev task_ids
    print("Fetching all tasks from dev…")
    dev_tasks = fetch_all_tasks(dev_supabase, pk_col, columns=f"{pk_col},is_enabled")
    print(f"Found {len(dev_tasks)} dev task(s).\n")

    enabled_in_dev = 0
    disabled_in_dev = 0
    failed = 0

    for dev_task in dev_tasks:
        task_id = dev_task.get(pk_col)
        should_be_enabled = task_id in prod_enabled_ids
        current_value = dev_task.get("is_enabled")

        # Skip if already correct
        if current_value is should_be_enabled:
            if should_be_enabled:
                enabled_in_dev += 1
            else:
                disabled_in_dev += 1
            continue

        result = (
            dev_supabase.table("tasks")
            .update({"is_enabled": should_be_enabled})
            .eq(pk_col, task_id)
            .execute()
        )

        if result.data:
            if should_be_enabled:
                logger.info(f"[is_enabled] Task {task_id} → enabled in dev")
                enabled_in_dev += 1
            else:
                logger.info(f"[is_enabled] Task {task_id} → disabled in dev")
                disabled_in_dev += 1
        else:
            logger.error(f"[is_enabled] Task {task_id} → update failed")
            failed += 1

    print()
    print("=" * 70)
    print("  SYNC is_enabled COMPLETE")
    print(f"  Enabled in dev   : {enabled_in_dev}")
    print(f"  Disabled in dev  : {disabled_in_dev}")
    print(f"  Failed           : {failed}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage GitHub Gists for Utkrushta tasks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sync-prod-to-dev
    sub.add_parser(
        "sync-prod-to-dev",
        help="Copy github_gist URLs from every prod task to matching dev tasks.",
    )

    # create-prod-missing-gists
    sub.add_parser(
        "create-prod-missing-gists",
        help="Create gists in prod for all tasks that are missing one.",
    )

    # sync-is-enabled
    sub.add_parser(
        "sync-is-enabled",
        help="Mirror is_enabled=True from prod → dev; disable all other dev tasks.",
    )

    # create
    create_parser = sub.add_parser(
        "create",
        help="Create gists for specific task IDs (single or bulk).",
    )
    create_parser.add_argument(
        "--task-ids",
        nargs="+",
        required=True,
        metavar="TASK_ID",
        help="One or more task UUIDs.",
    )
    create_parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Target environment (default: dev).",
    )
    create_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing github_gist URL.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "sync-prod-to-dev":
        sync_prod_gists_to_dev()
    elif args.command == "create-prod-missing-gists":
        create_prod_gists_for_missing()
    elif args.command == "sync-is-enabled":
        sync_is_enabled_to_dev()
    elif args.command == "create":
        create_gists_for_tasks(args.task_ids, args.env, args.force)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
