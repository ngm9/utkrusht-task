"""``python -m flows.tech.stages.generate`` — the task-creation stage (stage 04).

Runs the ``generate_tasks`` Click command directly (no subcommand word), so the
pipeline's stage-4 subprocess invokes it as
``python -m flows.tech.stages.generate -c ... -b ... -s ... --env ...``.
The same command is also exposed for humans as ``python -m apps.cli generate_tasks``.
"""
from dotenv import load_dotenv

load_dotenv()

from flows.tech.stages.generate.cli import generate_tasks

if __name__ == "__main__":
    generate_tasks()
