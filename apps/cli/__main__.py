"""``python -m apps.cli`` — unified task tooling (generate + gist).

Replaces the old ``multiagent.py`` shim + the top-level ``cli/`` package. The
``generate_tasks`` command lives in its flow stage (``flows.tech.stages.generate``);
this group just aggregates it alongside the gist tool. Deploy / reset live in
``python -m infra.e2b``.
"""
from dotenv import load_dotenv

load_dotenv()

import click

from apps.cli import gist as _gist
from flows.tech.stages.generate.cli import generate_tasks


@click.command(
    "gist",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False,
)
@click.argument("gist_args", nargs=-1, type=click.UNPROCESSED)
def gist_cmd(gist_args):
    """GitHub Gist lifecycle (sync / create / enable).

    Arguments pass straight through to the gist tool — run
    ``python -m apps.cli gist -h`` for its subcommands.
    """
    raise SystemExit(_gist.main(list(gist_args) or ["-h"]))


cli = click.Group(
    help="Utkrusht task tooling — generate tasks + manage gists. "
    "(Deploy / reset live in `python -m infra.e2b`.)"
)
cli.add_command(generate_tasks, name="generate_tasks")
cli.add_command(gist_cmd, name="gist")


if __name__ == "__main__":
    cli()
