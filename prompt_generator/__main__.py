"""
CLI entry point for the prompt_generator package.

Usage:
    python -m prompt_generator --name "Python, SQL" --proficiency BASIC
    python -m prompt_generator --name "Python" --name "Llamaindex" --proficiency BASIC
    python -m prompt_generator --name "Python, Vector Databases" --proficiency INTERMEDIATE --dry-run
    python -m prompt_generator --name "Java" --proficiency BASIC --force
"""

from __future__ import annotations

import re
from pathlib import Path

import click

from prompt_generator.agent import (
    PromptGeneratorAgent,
    configure_dspy,
)
from prompt_generator.classifier import Competency
from prompt_generator.retriever import LEVEL_FOLDERS


PROMPT_ROOT = Path(__file__).parent.parent / "task_generation_prompts"


def _slugify_filename(competency_names: list[str]) -> str:
    """Build the prompt filename from competency names: 'python_sql' for Python+SQL."""
    parts = []
    for name in competency_names:
        s = name.lower()
        s = re.sub(r"\.js\b", "js", s)
        s = re.sub(r"\s*[-/&]\s*", "_", s)
        s = re.sub(r"[\s.]+", "_", s)
        s = re.sub(r"[^a-z0-9_]", "", s)
        s = re.sub(r"_+", "_", s).strip("_")
        parts.append(s)
    return "_".join(parts)


def _expected_path(competency_names: list[str], proficiency: str) -> Path:
    folder = LEVEL_FOLDERS[proficiency.upper()]
    fname = f"{_slugify_filename(competency_names)}_{proficiency.lower()}_prompt.py"
    return PROMPT_ROOT / folder / fname


@click.command()
@click.option(
    "--name", "-n", required=True, multiple=True,
    help='Competency name(s). Use commas or repeat the flag: --name "Python, SQL"',
)
@click.option(
    "--proficiency", "-p", required=True,
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"], case_sensitive=False),
)
@click.option("--env", default="dev", type=click.Choice(["dev", "prod"]),
              help="Supabase environment for fetching scopes and similar tasks.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Generate and print but do not write to disk.")
@click.option("--force", is_flag=True, default=False,
              help="Overwrite an existing prompt file.")
@click.option("--max-iterations", default=5, type=int,
              help="Max generator/verifier iterations before giving up.")
@click.option("--model", default=None,
              help="Override the LLM (default: env PROMPT_GENERATOR_MODEL or openai/gpt-5.4).")
@click.option("--compiled-path", default="prompt_generator/compiled/agent_bootstrap.json",
              help="Path to a compiled agent JSON. If file exists, demos are loaded "
                   "into the generator. Pass empty string to disable.")
def cli(name, proficiency, env, dry_run, force, max_iterations, model, compiled_path):
    """Generate a new task generation prompt file using the DSPy agent."""

    # Parse competency names — supports both --name "A, B" and --name A --name B
    raw_names = list(name)
    names: list[str] = []
    for n in raw_names:
        names.extend(part.strip() for part in n.split(",") if part.strip())

    proficiency_upper = proficiency.upper()
    competencies = [Competency(name=n, proficiency=proficiency_upper) for n in names]
    output_path = _expected_path(names, proficiency_upper)

    click.echo(f"\n{'='*70}")
    click.echo(f" PROMPT GENERATOR")
    click.echo(f"{'='*70}")
    click.echo(f" Competencies: {' + '.join(names)}")
    click.echo(f" Proficiency:  {proficiency_upper}")
    click.echo(f" Env:          {env}")
    click.echo(f" Output path:  {output_path}")
    click.echo()

    # Check if the file already exists
    if output_path.exists() and not force and not dry_run:
        click.echo(f" File already exists: {output_path}")
        click.echo(" Use --force to overwrite or --dry-run to preview.")
        raise SystemExit(0)

    # Configure DSPy
    configure_dspy(model=model)
    click.echo(f" DSPy configured.")
    click.echo()

    # Run the agent
    agent = PromptGeneratorAgent(max_iterations=max_iterations)

    # Load compiled demos if available
    if compiled_path:
        from pathlib import Path
        cp = Path(compiled_path)
        if cp.exists():
            try:
                count = agent.load_compiled_demos(str(cp))
                click.echo(f" Loaded {count} compiled demos from {cp.name}")
            except Exception as e:
                click.echo(f" Warning: could not load compiled demos: {e}")
        else:
            click.echo(f" No compiled file at {cp} — running uncompiled.")

    click.echo(f" Running generator (max {max_iterations} iterations)...")
    result = agent(competencies=competencies, proficiency=proficiency_upper, env=env)

    # Report
    click.echo(f"\n{'─'*70}")
    click.echo(f" RESULT")
    click.echo(f"{'─'*70}")
    click.echo(f" Iterations:        {result.iterations}")
    click.echo(f" Verifier passed:   {result.passes_verifier}")
    click.echo(f" Bootstrap mode:    {result.bootstrap_mode}")
    click.echo(f" Fallback level:    {result.fallback_level}")
    click.echo(f" References used:   {len(result.references)}")
    for path in result.references:
        click.echo(f"   - {path.name}")
    click.echo(f" Similar DB tasks:  {result.similar_tasks_count}")
    click.echo()

    if not result.passes_verifier:
        click.echo(f" ⚠  Verifier did not pass after {result.iterations} iteration(s)")
        click.echo(f"     Last feedback: {result.verifier_feedback[:300]}")

    if result.validation:
        v = result.validation
        click.echo(f" Validation: {'PASS' if v.passed else 'FAIL'}")
        for issue in v.issues:
            click.echo(f"   ✗ {issue}")
        for warning in v.warnings:
            click.echo(f"   ⚠ {warning}")

    if dry_run:
        click.echo(f"\n{'─'*70}")
        click.echo(f" DRY RUN — Generated prompt (first 1500 chars):")
        click.echo(f"{'─'*70}")
        click.echo(result.new_prompt_file[:1500])
        click.echo("...")
        return

    # Write the file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.new_prompt_file, encoding="utf-8")
    click.echo(f"\n Wrote: {output_path}")

    if result.bootstrap_mode:
        click.echo(f" Note: Bootstrap mode (no exact reference). Manual review recommended.")


if __name__ == "__main__":
    cli()
