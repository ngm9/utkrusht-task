"""CLI entry point for the E2B deployment flow.

Usage:
    python -m e2b_flow deploy-task --task-id <UUID>
    python -m e2b_flow reset-task --task-id <UUID>
    python -m e2b_flow list-sandboxes
"""

import io
import json
import os
import sys

import click
from dotenv import load_dotenv

from e2b_flow import sandbox_manager, supabase_helpers
from logger_config import logger

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# override=True so the .env at cwd is the source of truth for this CLI.
# Without it, when invoked from inside the fastapi container (which already
# has GITHUB_UTKRUSHTAPPS_TOKEN / SUPABASE_* set from .env.local), those
# values would shadow the (possibly different) ones in utkrusht-task/.env
# and break things like git clone.
load_dotenv(override=True)


@click.group()
def cli():
    """E2B sandbox-based deploy/reset for assessment tasks."""


@cli.command("deploy-task")
@click.option("--task-id", "-t", required=True, help="Task UUID in Supabase")
@click.option(
    "--template",
    default="utkrusht-python-sql-dev",
    help="E2B template name (default: utkrusht-python-sql-dev)",
)
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment",
)
@click.option(
    "--timeout-hours",
    default=1.0,
    type=float,
    help="Sandbox idle timeout in hours (default: 1; fractional values "
         "ok, e.g. 0.1 ≈ 6min for abandonment tests). E2B free/standard "
         "tiers cap at 1h, Pro tiers allow longer.",
)
def deploy_task(task_id, template, env, timeout_hours):
    """Provision an E2B sandbox for a task and record the deployment."""
    _require_env("E2B_API_KEY")

    repo_url = supabase_helpers.get_repo_url(task_id, env)
    if not repo_url:
        click.echo(f"No repo_url found for task {task_id} in {env}", err=True)
        raise SystemExit(1)

    try:
        handle = sandbox_manager.create_and_setup(
            template=template,
            repo_url=repo_url,
            timeout_hours=timeout_hours,
        )
    except Exception as exc:
        click.echo(f"Sandbox setup failed: {exc}", err=True)
        raise SystemExit(2)

    ok = supabase_helpers.update_e2b_deployment_status(
        task_id=task_id,
        sandbox_id=handle.sandbox_id,
        template=handle.template,
        terminal_url=handle.terminal_url,
        exposed_ports=handle.exposed_ports,
        timeout_seconds=handle.timeout_seconds,
        env=env,
    )
    if not ok:
        click.echo(
            "Sandbox is running but Supabase update failed. "
            "You may want to manually kill it: "
            f"python -m e2b_flow kill-sandbox --sandbox-id {handle.sandbox_id}",
            err=True,
        )

    click.echo(
        json.dumps(
            {
                "task_id": task_id,
                "sandbox_id": handle.sandbox_id,
                "template": handle.template,
                "terminal_url": handle.terminal_url,
                "exposed_ports": handle.exposed_ports,
                "timeout_seconds": handle.timeout_seconds,
            },
            indent=2,
        )
    )


@cli.command("reset-task")
@click.option("--task-id", "-t", required=True, help="Task UUID in Supabase")
@click.option(
    "--env",
    default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment",
)
def reset_task(task_id, env):
    """Kill the sandbox associated with a task and clear deployment_info."""
    _require_env("E2B_API_KEY")

    sandbox_id = supabase_helpers.get_e2b_sandbox_id(task_id, env)
    if not sandbox_id:
        click.echo(
            f"No active E2B sandbox recorded for task {task_id} in {env} — nothing to reset",
            err=True,
        )
        raise SystemExit(1)

    killed = sandbox_manager.kill(sandbox_id)
    if not killed:
        click.echo(
            f"Sandbox {sandbox_id} kill returned False (may already be gone). "
            "Proceeding to clear Supabase row.",
            err=True,
        )

    ok = supabase_helpers.update_e2b_undeploy_status(task_id, env)
    if not ok:
        raise SystemExit(2)
    click.echo(json.dumps({"task_id": task_id, "sandbox_id": sandbox_id, "killed": killed}, indent=2))


@cli.command("list-sandboxes")
def list_sandboxes():
    """List all active sandboxes for the configured E2B account."""
    _require_env("E2B_API_KEY")
    rows = sandbox_manager.list_active()
    click.echo(json.dumps(rows, indent=2))


@cli.command("kill-sandbox")
@click.option("--sandbox-id", required=True, help="E2B sandbox handle")
def kill_sandbox(sandbox_id):
    """Force-kill a sandbox by ID (debug/cleanup)."""
    _require_env("E2B_API_KEY")
    ok = sandbox_manager.kill(sandbox_id)
    click.echo(json.dumps({"sandbox_id": sandbox_id, "killed": ok}))
    if not ok:
        raise SystemExit(1)


def _require_env(name: str):
    if not os.getenv(name):
        click.echo(f"Missing required env var: {name}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
