"""Supabase reads/writes for the E2B deployment path.

Self-contained so the module does not import from ``multiagent.py``.
Mirrors the shape of ``update_task_deployment_status`` /
``update_task_undeploy_status`` in ``multiagent.py``, but writes
sandbox-specific fields into ``deployment_info`` and tags
``deployment_method = "e2b_sandbox"``.
"""

import datetime
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from logger_config import logger

load_dotenv()

TASK_SELECT_FIELDS = (
    "task_id, criterias, task_blob, is_deployed, created_at, deployment_info, "
    "pre_requisites, answer, readme_content, eval_info, solutions, "
    "is_shared_infra_required"
)


def init_supabase(env: str = "dev") -> Client:
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")
    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")
    return create_client(url, key)


def get_task(task_id: str, env: str = "dev") -> Optional[Dict]:
    supabase = init_supabase(env)
    result = (
        supabase.table("tasks")
        .select(TASK_SELECT_FIELDS)
        .eq("task_id", task_id)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]


def get_repo_url(task_id: str, env: str = "dev") -> Optional[str]:
    task = get_task(task_id, env)
    if not task:
        return None
    return task.get("task_blob", {}).get("resources", {}).get("github_repo")


def get_e2b_sandbox_id(task_id: str, env: str = "dev") -> Optional[str]:
    task = get_task(task_id, env)
    if not task:
        return None
    info = task.get("deployment_info") or {}
    if info.get("deployment_method") != "e2b_sandbox":
        return None
    return info.get("sandbox_id")


def update_e2b_deployment_status(
    task_id: str,
    sandbox_id: str,
    template: str,
    terminal_url: Optional[str],
    exposed_ports: Dict[str, str],
    timeout_seconds: int,
    env: str = "dev",
) -> bool:
    """Mark a task as deployed via an E2B sandbox.

    Writes sandbox-specific fields into the existing ``deployment_info``
    JSON column. ``deployment_method`` is set to ``e2b_sandbox`` so
    consumers can distinguish from the droplet path.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    deployment_info = {
        "deployment_method": "e2b_sandbox",
        "sandbox_id": sandbox_id,
        "template": template,
        "terminal_url": terminal_url,
        "exposed_ports": exposed_ports,
        "idle_timeout_seconds": timeout_seconds,
        "deployed_at": now.isoformat(),
        "deployment_status": "active",
        "deployment_timestamp": now.timestamp(),
    }
    update_data = {"is_deployed": True, "deployment_info": deployment_info}
    try:
        supabase = init_supabase(env)
        result = (
            supabase.table("tasks")
            .update(update_data)
            .eq("task_id", task_id)
            .execute()
        )
        if result.data:
            logger.info(f"E2B deployment recorded for task {task_id}: sandbox={sandbox_id}")
            return True
        logger.error(f"E2B deployment update affected 0 rows for task {task_id}")
        return False
    except Exception as exc:
        logger.error(f"Failed to record E2B deployment for {task_id}: {exc}")
        return False


def update_e2b_undeploy_status(task_id: str, env: str = "dev") -> bool:
    update_data = {"is_deployed": False, "deployment_info": None}
    try:
        supabase = init_supabase(env)
        result = (
            supabase.table("tasks")
            .update(update_data)
            .eq("task_id", task_id)
            .execute()
        )
        if result.data:
            logger.info(f"E2B undeploy recorded for task {task_id}")
            return True
        logger.error(f"E2B undeploy update affected 0 rows for task {task_id}")
        return False
    except Exception as exc:
        logger.error(f"Failed to record E2B undeploy for {task_id}: {exc}")
        return False
