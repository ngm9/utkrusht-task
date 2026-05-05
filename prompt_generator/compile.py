"""
Compile the PromptGeneratorAgent against the training set using DSPy optimizers.

Why this matters: the uncompiled agent calls the LLM with hand-written
instructions in the signatures. The compiled agent has those instructions
auto-tuned plus learned few-shot examples baked in.

CLI:
    python -m prompt_generator.compile --optimizer bootstrap --max-examples 8 --output prompt_generator/compiled.json

Optimizers:
    - bootstrap (cheap, fast):     BootstrapFewShot — selects few-shot demos from
                                    the training set without auto-tuning prompts.
    - miprov2 (expensive, better): MIPROv2 — tunes both prompts and few-shot
                                    examples. Costs ~$5-20 per compilation depending
                                    on training set size.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

import click
import dspy

from prompt_generator.agent import PromptGeneratorAgent, configure_dspy
from prompt_generator.metric import quality_metric, metric_summary
from prompt_generator.trainset import collect_training_pairs, to_dspy_examples


COMPILED_DIR = Path(__file__).parent / "compiled"
COMPILED_DIR.mkdir(exist_ok=True)


class TrainingSubset(dspy.Module):
    """Wrap PromptGeneratorAgent so its forward signature matches dspy.Example.

    The full agent takes Competency objects + env. For compilation we need a
    simpler signature: (competencies_str, proficiency_str) → prediction with
    new_prompt_file.

    This wrapper does the conversion and uses a SINGLE iteration of the
    generator (not the verify loop) — compilation tunes the generator only.
    """

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("competencies, proficiency, task_category, "
                                             "competency_scopes, reference_prompts, "
                                             "similar_tasks, feedback_from_previous_attempt "
                                             "-> new_prompt_file")

    def forward(self, competencies: str, proficiency: str):
        # Lazy imports to avoid circular dependencies at import time.
        from prompt_generator.classifier import Competency, classify_task_category
        from prompt_generator.retriever import retrieve_references
        from prompt_generator.db_queries import (
            init_supabase, fetch_similar_tasks, fetch_competency_scope,
        )
        from prompt_generator.agent import PromptGeneratorAgent

        # Parse competencies string back into Competency objects
        comps = []
        for part in competencies.split(","):
            part = part.strip()
            if not part:
                continue
            import re
            m = re.match(r"^(.*?)\s*\((\w+)\)$", part)
            if m:
                comps.append(Competency(name=m.group(1).strip(), proficiency=m.group(2)))
            else:
                comps.append(Competency(name=part, proficiency=proficiency))

        category = classify_task_category(comps)
        retrieval = retrieve_references(comps, proficiency)

        supabase = init_supabase("dev")
        comp_names = [c.name for c in comps]
        similar = fetch_similar_tasks(supabase, comp_names, proficiency)

        scopes_text = []
        for c in comps:
            scope = fetch_competency_scope(supabase, c.name, proficiency)
            if scope and scope.get("scope"):
                scopes_text.append(f"[{c.name} ({proficiency})]\n{scope['scope']}")

        comp_str = ", ".join(f"{c.name} ({proficiency})" for c in comps)
        refs_text = PromptGeneratorAgent._build_references_text(retrieval)
        tasks_text = PromptGeneratorAgent._build_similar_tasks_text(similar)
        scopes_str = "\n\n---\n\n".join(scopes_text) if scopes_text else "(no scopes available)"

        out = self.generate(
            competencies=comp_str,
            proficiency=proficiency,
            task_category=category.value,
            competency_scopes=scopes_str,
            reference_prompts=refs_text,
            similar_tasks=tasks_text,
            feedback_from_previous_attempt="",
        )
        # Strip code fences
        text = (out.new_prompt_file or "").strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return dspy.Prediction(new_prompt_file=text)


@click.command()
@click.option("--optimizer", type=click.Choice(["bootstrap", "miprov2"]), default="bootstrap")
@click.option("--max-examples", default=8, type=int,
              help="Cap the training set size (controls cost).")
@click.option("--require-quality-signal/--no-require-quality-signal", default=True,
              help="Only use prompts that have produced enabled DB tasks. "
                   "Use --no-require-quality-signal to include all pairs.")
@click.option("--output", type=click.Path(), default=None,
              help="Where to save the compiled program JSON.")
@click.option("--model", default=None,
              help="LLM to use for compilation calls.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be compiled but don't actually run.")
def compile_cli(optimizer, max_examples, require_quality_signal, output, model, dry_run):
    """Compile the prompt generator agent."""
    click.echo(f"\n{'='*70}")
    click.echo(" COMPILING PROMPT GENERATOR AGENT")
    click.echo(f"{'='*70}")
    click.echo(f" Optimizer:    {optimizer}")
    click.echo(f" Max examples: {max_examples}")
    click.echo(f" Quality only: {require_quality_signal}")
    click.echo()

    # 1. Build training set
    click.echo(" Collecting training pairs...")
    pairs = collect_training_pairs(
        env="dev",
        require_quality_signal=require_quality_signal,
    )
    click.echo(f"   Found {len(pairs)} training pairs")

    if max_examples > 0:
        # Prefer pairs with the most DB task signal first
        pairs = sorted(pairs, key=lambda p: -p.db_task_count)[:max_examples]
    click.echo(f"   Using {len(pairs)} pairs for compilation")
    for p in pairs:
        names = " + ".join(p.competency_names)
        click.echo(f"     - {names} ({p.proficiency}) [{p.db_task_count} DB tasks]")

    if dry_run:
        click.echo("\n[DRY RUN] Stopping before compilation.")
        return

    # 2. Configure DSPy with the cheap COMPILE model (Haiku by default).
    # Runtime generation uses the stronger model — this only affects compilation calls.
    configure_dspy(model=model, mode="compile")
    click.echo(f"\n DSPy configured (mode=compile, model={model or 'default Haiku'}).")

    # 3. Build the trainable module
    program = TrainingSubset()
    examples = to_dspy_examples(pairs)

    # 4. Pick optimizer
    click.echo(f"\n Compiling with {optimizer}...")
    start = time.time()
    if optimizer == "bootstrap":
        opt = dspy.BootstrapFewShot(
            metric=quality_metric,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
            max_rounds=1,
        )
        compiled = opt.compile(program, trainset=examples)
    else:
        # MIPROv2 — much more expensive
        opt = dspy.MIPROv2(
            metric=quality_metric,
            num_threads=2,
            auto="light",  # 'light' is the smallest budget; 'medium'/'heavy' cost more
        )
        compiled = opt.compile(
            program,
            trainset=examples,
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
        )
    elapsed = time.time() - start
    click.echo(f" Compilation took {elapsed:.1f}s")

    # 5. Save
    if output is None:
        output = COMPILED_DIR / f"agent_{optimizer}.json"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    compiled.save(str(output))
    click.echo(f"\n Saved compiled program to: {output}")


if __name__ == "__main__":
    compile_cli()
