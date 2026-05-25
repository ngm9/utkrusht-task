"""Thin entry point — backward-compat for ``python multiagent.py X``.

After the A1 refactor:

* Task generation lives in ``task_generation/``.
* Deploy / reset code lives in ``deployment/``.
* Click commands live in ``cli/``.

The Click group below preserves the existing CLI surface for ``run_pipeline.py``,
shell scripts, and docs that still call ``python multiagent.py generate_tasks``.
Phase 3 of the layout migration deletes this file once those callers are
moved to ``python -m apps.cli``.

Tracking: ``docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md``
"""
from dotenv import load_dotenv
load_dotenv()

from cli.main import cli


if __name__ == "__main__":
    cli()
