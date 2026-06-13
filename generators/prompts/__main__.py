"""
CLI entry point for the prompt_generator package.

Generated files are written to::

    data/generated/agent_prompts/<Level>/<slug>/<slug>.py

This keeps agent output separate from the curated, hand-reviewed prompts in
``task_generation_prompts/<Level>/`` that the retriever uses as references.
(The agent-generated subtree moved out of ``task_generation_prompts/`` on
2026-05-25 to match the data/curated vs. data/generated split.)

Usage:
    python -m prompt_generator --name "Python, SQL" --proficiency BASIC
    python -m prompt_generator --name "Python" --name "Llamaindex" --proficiency BASIC
    python -m prompt_generator --name "Python, Vector Databases" --proficiency INTERMEDIATE --dry-run
    python -m prompt_generator --name "Java" --proficiency BASIC --force
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import click

from generators.prompts.agent import (
    PromptGeneratorAgent,
    configure_dspy,
)
from infra.classifier.classifier import Competency
from generators.prompts.retriever import LEVEL_FOLDERS


# ``.parent.parent.parent`` because this module lives at
# ``generators/prompts/__main__.py`` after Phase 2 — bumps up to repo root.
_REPO_ROOT = Path(__file__).parent.parent.parent
PROMPT_ROOT = _REPO_ROOT / "task_generation_prompts"

# Agent-generated prompts live in their own subtree so they stay separate from
# curated, hand-reviewed prompts. The retriever reads curated prompts from
# `<level>/*.py` (non-recursive), so the nested data/generated/agent_prompts/
# layout keeps agent output from being picked up as a reference for future
# generations.
AGENT_OUTPUT_ROOT = _REPO_ROOT / "data" / "generated" / "agent_prompts"

logger = logging.getLogger("prompt_generator")


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
    slug = f"{_slugify_filename(competency_names)}_{proficiency.lower()}_prompt"
    return AGENT_OUTPUT_ROOT / folder / slug / f"{slug}.py"


def _prepend_task_shape(source: str, task_shape: str) -> str:
    """Prepend ``TASK_SHAPE = "<value>"`` to the generated prompt source.

    Idempotent: if the LLM somehow already emitted a TASK_SHAPE constant
    (it shouldn't — nothing in the GeneratePromptSignature asks for one),
    we skip the prepend to avoid duplicate assignments.
    """
    if re.search(r"^\s*TASK_SHAPE\s*=", source, re.MULTILINE):
        return source
    header = (
        f'# Set by the prompt-generator shape classifier — do not edit.\n'
        f'# Consumed by infra.utils for the E2B-gate skip decision.\n'
        f'TASK_SHAPE = "{task_shape}"\n\n\n'
    )
    return header + source.lstrip()


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
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Enable detailed step-by-step logging of every internal stage "
                   "(file lookups, Supabase queries, LLM call sizes, verifier feedback).")
def cli(name, proficiency, env, dry_run, force, max_iterations, model, compiled_path, verbose):
    """Generate a new task generation prompt file using the DSPy agent."""

    # Configure verbose logging if requested. Adds a clean console stream handler
    # so step-by-step trace lines flow inline with the banner output.
    log_level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(log_level)
    if verbose and not any(
        getattr(h, "is_promptgen_console", False) for h in logger.handlers
    ):
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(
            "  [%(levelname)-5s] %(message)s"
        ))
        handler.is_promptgen_console = True
        logger.addHandler(handler)
        logger.propagate = False

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
            click.echo(f" No compiled file at {cp} -- running uncompiled.")

    click.echo(f" Running generator (max {max_iterations} iterations)...")
    result = agent(competencies=competencies, proficiency=proficiency_upper, env=env)

    # Report
    click.echo(f"\n{'-'*70}")
    click.echo(f" RESULT")
    click.echo(f"{'-'*70}")
    click.echo(f" Task shape:        {result.task_shape}")
    if result.task_shape_reason:
        click.echo(f"   reason: {result.task_shape_reason}")
    click.echo(f" Iterations:        {result.iterations}")
    click.echo(f" Bootstrap mode:    {result.bootstrap_mode}")
    click.echo(f" Fallback level:    {result.fallback_level}")
    click.echo(f" References used:   {len(result.references)}")
    for path in result.references:
        click.echo(f"   - {path.name}")
    click.echo(f" Similar DB tasks:  {result.similar_tasks_count}")

    # Input-files signal (detailed_skill_signal): role_context + questions_prompt + scenarios
    meta = result.input_files_metadata or {}
    if meta.get("background_found") or meta.get("scenarios_count"):
        click.echo(
            f" Input files used:  yes  "
            f"(questions={meta.get('questions_chars', 0)}c, "
            f"role={meta.get('role_context_chars', 0)}c, "
            f"scenarios={meta.get('scenarios_count', 0)}, "
            f"signal={meta.get('signal_chars', 0)}c)"
        )
    else:
        click.echo(f" Input files used:  no (brand-new combo, signal empty)")
    click.echo()

    if not result.passes_verifier:
        click.echo(f" [WARN] Review did not pass after {result.iterations} iteration(s)")
        click.echo(f"        Last feedback: {result.verifier_feedback[:300]}")

    if result.validation:
        v = result.validation
        click.echo(f" Validation: {'PASS' if v.passed else 'FAIL'}")
        for issue in v.issues:
            click.echo(f"   [x] {issue}")
        for warning in v.warnings:
            click.echo(f"   [!] {warning}")

    # Prepend the shape classifier's verdict as a module-level constant so
    # downstream consumers (the E2B gate in particular) can discover the
    # task shape from the loaded prompt module via `getattr(module,
    # "TASK_SHAPE", None)` — no extra plumbing, no separate metadata file.
    final_source = _prepend_task_shape(result.new_prompt_file, result.task_shape)

    if dry_run:
        click.echo(f"\n{'-'*70}")
        click.echo(f" DRY RUN -- Generated prompt (first 1500 chars):")
        click.echo(f"{'-'*70}")
        click.echo(final_source[:1500])
        click.echo("...")
        return

    # Write the file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_source, encoding="utf-8")
    click.echo(f"\n Wrote: {output_path}")

    if result.bootstrap_mode:
        click.echo(f" Note: Bootstrap mode (no exact reference). Manual review recommended.")


if __name__ == "__main__":
    cli()
