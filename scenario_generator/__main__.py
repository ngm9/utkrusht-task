"""
CLI entry point for the scenario generator package.

Usage:
    python -m scenario_generator --competency-file <path> [--count 6] [--output <path>] [--append]
"""

import json
import sys
import io
from pathlib import Path

import click

# Fix Unicode output on Windows (cp1252 can't handle chars like →, •, etc.)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from scenario_generator.generator import (
    generate_scenarios_for_competencies,
    non_code_scenarios_required,
    build_scenario_key,
    get_competency_names,
    get_target_scenario_file,
    save_generated_scenarios,
    create_openai_client,
    format_cost_summary,
)


@click.command()
@click.option(
    "--competency-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to competency JSON file (competency_*.json)",
)
@click.option(
    "--count",
    default=6,
    type=int,
    help="Number of scenarios to generate (default: 6)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path. If omitted, auto-selects based on proficiency level.",
)
@click.option(
    "--append",
    is_flag=True,
    default=False,
    help="Append/merge into existing scenario file instead of overwriting.",
)
@click.option(
    "--background-file",
    type=click.Path(exists=True),
    default=None,
    help="Optional background JSON file for additional context.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print generated scenarios to stdout without saving to file.",
)
def generate_scenarios_cli(competency_file, count, output, append, background_file, dry_run):
    """Generate task scenarios for coding assessments based on competency definitions."""

    # Load competency file
    try:
        with open(competency_file, "r", encoding="utf-8") as f:
            competencies = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        click.echo(f"Error reading competency file: {e}", err=True)
        raise SystemExit(1)

    if not isinstance(competencies, list) or not competencies:
        click.echo("Competency file must contain a non-empty JSON array.", err=True)
        raise SystemExit(1)

    # Load optional background
    background = None
    if background_file:
        try:
            with open(background_file, "r", encoding="utf-8") as f:
                background = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            click.echo(f"Warning: Could not read background file: {e}", err=True)

    # Create OpenAI client
    try:
        client = create_openai_client()
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    # Classify: code vs non-code (uses role_context from background if available)
    role_description = background.get("role_context", "") if background else None
    is_non_code = non_code_scenarios_required(client, competencies, role_description)
    click.echo(f"Scenario type: {'non-code (PM/analyst)' if is_non_code else 'code (engineering)'}")

    # Build key and determine output file
    scenario_key = build_scenario_key(competencies)
    if output:
        target_file = Path(output)
    else:
        target_file = get_target_scenario_file(competencies, is_non_code)

    click.echo(f"Scenario key: {scenario_key}")
    click.echo(f"Competencies: {get_competency_names(competencies)}")
    click.echo(f"Target file: {target_file}")
    click.echo(f"Generating {count} scenarios...")
    click.echo()

    # Generate scenarios
    scenarios, usage_by_model = generate_scenarios_for_competencies(
        openai_client=client,
        competencies=competencies,
        count=count,
        background=background,
        is_non_code=is_non_code,
    )

    if not scenarios:
        click.echo("No scenarios were generated. Check logs for details.", err=True)
        raise SystemExit(1)

    # Display results
    click.echo(f"\n{'='*70}")
    click.echo(f"Generated {len(scenarios)} scenarios for: {scenario_key}")
    click.echo(f"{'='*70}\n")
    for i, s in enumerate(scenarios, 1):
        click.echo(f"--- Scenario {i} ---")
        click.echo(s)
        click.echo()

    # Save to file
    if not dry_run:
        save_generated_scenarios(scenarios, scenario_key, target_file, append=append)
        click.echo(f"Saved to: {target_file} (key: '{scenario_key}', append={append})")
    else:
        click.echo("[DRY RUN] Scenarios not saved to file.")

    # Display cost summary
    click.echo(f"\n{'='*70}")
    click.echo(format_cost_summary(usage_by_model))
    click.echo(f"{'='*70}")

    click.echo(f"\nDone. {len(scenarios)}/{count} scenarios generated successfully.")


if __name__ == "__main__":
    generate_scenarios_cli()
