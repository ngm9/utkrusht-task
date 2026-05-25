"""Click CLI commands — A1 follow-up extraction from multiagent.py.

After the droplet path was removed, this package contains only the
``generate_tasks`` command. Deploy / reset for live tasks live in
``e2b_flow/`` (``python -m e2b_flow deploy-task`` / ``reset-task``).

``.env`` is loaded here so ``python -m cli`` works the same as
``python multiagent.py`` — the downstream ``evals`` module reads
``OPENAI_API_KEY`` at import time and would otherwise crash on a clean
shell.

Tracking: ``docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md``
"""
from dotenv import load_dotenv
load_dotenv()

from cli.generate import generate_tasks
from cli.main import cli

__all__ = ["cli", "generate_tasks"]
