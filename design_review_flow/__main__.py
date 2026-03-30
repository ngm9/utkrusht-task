"""CLI entry point for Design Review task generation.

Usage:
    python -m design_review_flow generate \
        --competency-file path/to/competency.json \
        --proficiency INTERMEDIATE \
        --scenario "SaaS onboarding redesign" \
        --library-entry-id lib-001 \
        --env dev

    python -m design_review_flow store \
        --spec-file path/to/design_task_spec.json \
        --figma-link "https://figma.com/file/...?duplicate" \
        --env dev
"""

import sys
import io
from pathlib import Path

import click

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from design_review_flow.design_review_multiagent import (
    create_design_review_task,
    store_design_review_task,
)


@click.group()
def cli():
    """Design Review Task Generator."""
    pass


@cli.command()
@click.option(
    "--competency-file", "-c",
    type=click.Path(exists=True), required=True,
    help="Path to competency JSON file",
)
@click.option(
    "--proficiency", "-p",
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"]),
    required=True,
    help="Proficiency level for flaw scaling",
)
@click.option(
    "--scenario", "-s",
    type=str, required=True,
    help="Design scenario description (e.g., 'SaaS onboarding redesign')",
)
@click.option(
    "--library-entry-id", "-l",
    type=str, required=True,
    help="ID of the Figma library entry to use (from figma_library.json)",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Generate and eval but don't save to disk",
)
def generate(competency_file, proficiency, scenario, library_entry_id, env, dry_run):
    """Generate a design review flaw spec + brief + rubric."""
    click.echo(f"\n{'='*70}")
    click.echo("  DESIGN REVIEW TASK GENERATOR")
    click.echo(f"{'='*70}")
    click.echo(f"  Competency file:  {competency_file}")
    click.echo(f"  Proficiency:      {proficiency}")
    click.echo(f"  Scenario:         {scenario}")
    click.echo(f"  Library entry:    {library_entry_id}")
    click.echo(f"  Environment:      {env}")
    if dry_run:
        click.echo("  Mode:             DRY RUN")
    click.echo()

    result = create_design_review_task(
        competency_file=Path(competency_file),
        proficiency=proficiency,
        scenario=scenario,
        library_entry_id=library_entry_id,
        env=env,
        dry_run=dry_run,
    )

    if not result:
        click.echo("\nTask generation failed. Check logs for details.", err=True)
        raise SystemExit(1)

    click.echo(f"\nSpec saved to: {result.get('local_dir', 'N/A')}")


@cli.command()
@click.option(
    "--spec-file", "-f",
    type=click.Path(exists=True), required=True,
    help="Path to generated design task spec JSON",
)
@click.option(
    "--figma-link", "-u",
    type=str, required=True,
    help="Figma duplicate link (URL) for the flawed design",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
def store(spec_file, figma_link, env):
    """Store a design review task in Supabase (after Figma plugin step)."""
    click.echo(f"\n{'='*70}")
    click.echo("  DESIGN REVIEW TASK STORE")
    click.echo(f"{'='*70}")
    click.echo(f"  Spec file:    {spec_file}")
    click.echo(f"  Figma link:   {figma_link}")
    click.echo(f"  Environment:  {env}")
    click.echo()

    result = store_design_review_task(
        spec_file=Path(spec_file),
        figma_link=figma_link,
        env=env,
    )

    if not result:
        click.echo("\nStore failed. Check logs for details.", err=True)
        raise SystemExit(1)

    click.echo(f"\nTask stored! task_id: {result.get('task_id', 'N/A')}")


if __name__ == "__main__":
    cli()
