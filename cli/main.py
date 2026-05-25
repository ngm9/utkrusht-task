"""Click group entry point for the task-generation CLI.

Re-used by:

* ``python -m cli``               — direct module entry
* ``python multiagent.py X``      — the thin shim preserved for run_pipeline.py + docs

Deploy / reset for live tasks live in ``e2b_flow/`` and are invoked via
``python -m e2b_flow deploy-task`` / ``reset-task``. Droplet deploys were
removed alongside this CLI's ``deploy_task`` / ``reset_task`` commands.

Tracking: ``docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md``
"""
import click

from cli.generate import generate_tasks


cli = click.Group(help="Utkrusht task-generation CLI (generate only — deploy lives in e2b_flow).")
cli.add_command(generate_tasks, name="generate_tasks")


if __name__ == "__main__":
    cli()
