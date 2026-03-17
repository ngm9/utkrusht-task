"""CLI entry point for PR Review task generation.

Usage:
    python -m pr_review_flow \
        --competency-file path/to/competency.json \
        --background-file path/to/background.json \
        --scenarios-file path/to/task_scenarios_pr_review.json
"""

import sys
import io
from pathlib import Path

import click

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pr_review_flow.pr_review_multiagent import create_pr_review_task


@click.command()
@click.option(
    "--competency-file", "-c",
    type=click.Path(exists=True), required=True,
    help="Path to competency JSON file",
)
@click.option(
    "--background-file", "-b",
    type=click.Path(exists=True), required=True,
    help="Path to background JSON file",
)
@click.option(
    "--scenarios-file", "-s",
    type=click.Path(exists=True), required=True,
    help="Path to PR review scenarios JSON file",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Run LLM generation but skip GitHub and Supabase operations",
)
def main(competency_file, background_file, scenarios_file, env, dry_run):
    """Generate a PR Review assessment task."""
    click.echo(f"\n{'='*70}")
    click.echo("  PR REVIEW TASK GENERATOR")
    click.echo(f"{'='*70}")
    click.echo(f"  Competency file: {competency_file}")
    click.echo(f"  Background file: {background_file}")
    click.echo(f"  Scenarios file:  {scenarios_file}")
    click.echo(f"  Environment:     {env}")
    if dry_run:
        click.echo("  Mode:            DRY RUN")
    click.echo()

    result = create_pr_review_task(
        competency_file=Path(competency_file),
        background_file=Path(background_file),
        scenarios_file=Path(scenarios_file),
        env=env,
        dry_run=dry_run,
    )

    if not result:
        click.echo("\nTask generation failed. Check logs for details.", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
