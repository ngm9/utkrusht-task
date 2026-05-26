"""Enables ``python -m cli`` as an alternate entry point.

Equivalent to ``python multiagent.py`` — same Click group, same commands.
"""
from cli.main import cli


if __name__ == "__main__":
    cli()
