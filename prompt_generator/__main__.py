"""
CLI entry point for the prompt generator package.

Usage:
    python -m prompt_generator --techs "Java,Kafka" --proficiency BASIC --deployment docker-backend
    python -m prompt_generator --techs "React" --proficiency BEGINNER --deployment no-docker --dry-run
"""

import sys
import io

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import click

from prompt_generator.generator import (
    generate_prompt,
    create_openai_client,
    format_cost_summary,
    get_output_path,
)
from prompt_generator.deployment_models import (
    derive_registry_key,
    derive_tech_slug,
    DEPLOYMENT_MODELS,
)


@click.command()
@click.option(
    "--techs",
    type=str,
    required=True,
    help="Comma-separated technology names (e.g., 'Java,Kafka')",
)
@click.option(
    "--proficiency",
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE"], case_sensitive=False),
    required=True,
    help="Proficiency level",
)
@click.option(
    "--deployment",
    type=click.Choice(list(DEPLOYMENT_MODELS.keys()), case_sensitive=True),
    required=True,
    help="Deployment model",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Override output file path (auto-derived if omitted)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print generated prompt to stdout without saving",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing file",
)
def generate_prompt_cli(techs, proficiency, deployment, output, dry_run, force):
    """Generate a task generation prompt template for a technology stack."""

    # Parse techs
    tech_list = [t.strip() for t in techs.split(",") if t.strip()]
    if not tech_list:
        raise click.ClickException("--techs must contain at least one technology name")

    proficiency = proficiency.upper()

    # Determine output path
    if output:
        from pathlib import Path
        output_path = Path(output)
    else:
        output_path = get_output_path(tech_list, proficiency)

    # Check if file already exists
    if output_path.exists() and not force and not dry_run:
        raise click.ClickException(
            f"File already exists: {output_path}\n"
            f"Use --force to overwrite or --output to specify a different path."
        )

    # Display config
    registry_key = derive_registry_key(tech_list, proficiency)
    tech_slug = derive_tech_slug(tech_list)

    click.echo(f"Technologies: {', '.join(tech_list)}")
    click.echo(f"Proficiency: {proficiency}")
    click.echo(f"Deployment: {deployment}")
    click.echo(f"Registry key: {registry_key}")
    click.echo(f"Tech slug: {tech_slug}")
    click.echo(f"Output: {output_path}")
    click.echo()

    # Create client
    try:
        client = create_openai_client()
    except RuntimeError as e:
        raise click.ClickException(str(e))

    click.echo("Generating prompt template...")
    click.echo()

    # Generate
    python_code, usage_by_model = generate_prompt(
        client=client,
        techs=tech_list,
        proficiency=proficiency,
        deployment_model=deployment,
    )

    if python_code is None:
        click.echo("ERROR: All generation attempts failed. See logs above.", err=True)
        raise SystemExit(1)

    # Display result
    click.echo(f"\n{'='*70}")
    click.echo(f"Generated prompt for: {registry_key}")
    click.echo(f"{'='*70}\n")

    if dry_run:
        click.echo(python_code)
        click.echo("\n[DRY RUN] Prompt not saved to file.")
    else:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(python_code, encoding="utf-8")
        click.echo(f"Saved to: {output_path}")

    # Cost summary
    click.echo(f"\n{'='*70}")
    click.echo(format_cost_summary(usage_by_model))
    click.echo(f"{'='*70}")

    click.echo(f"\nDone. Prompt generated successfully for {registry_key}.")


if __name__ == "__main__":
    generate_prompt_cli()
