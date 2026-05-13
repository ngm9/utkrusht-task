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

from prompt_generator.agent import (
    GeneratePromptSignature,
    PromptGeneratorAgent,
    configure_dspy,
)
from prompt_generator.metric import quality_metric, metric_summary
from prompt_generator.trainset import (
    collect_training_pairs,
    to_dspy_examples,
    to_dspy_examples_rich,
)


COMPILED_DIR = Path(__file__).parent / "compiled"
COMPILED_DIR.mkdir(exist_ok=True)


class TrainingSubset(dspy.Module):
    """Wrap PromptGeneratorAgent's Generate step for compilation.

    Rich examples (``to_dspy_examples_rich``) pre-compute all 8 inputs and
    declare them via ``.with_inputs(...)``, so the trainable module is just
    ChainOfThought over the real GeneratePromptSignature — no live I/O, no
    leakage, no Supabase calls during compile. Each demo trial is just one
    LLM call per example, which is what makes BootstrapFewShot tractable.
    """

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.ChainOfThought(GeneratePromptSignature)

    def forward(
        self,
        competencies: str,
        proficiency: str,
        task_category: str,
        competency_scopes: str,
        reference_prompts: str,
        similar_tasks: str,
        detailed_skill_signal: str,
        feedback_from_previous_attempt: str = "",
    ) -> dspy.Prediction:
        out = self.generate(
            competencies=competencies,
            proficiency=proficiency,
            task_category=task_category,
            competency_scopes=competency_scopes,
            reference_prompts=reference_prompts,
            similar_tasks=similar_tasks,
            detailed_skill_signal=detailed_skill_signal,
            feedback_from_previous_attempt=feedback_from_previous_attempt,
        )
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
              help="Cap the training set size (controls cost). 0 = no cap.")
@click.option("--holdout", default=4, type=int,
              help="How many pairs to set aside for A/B scoring (0 = skip A/B).")
@click.option("--require-quality-signal/--no-require-quality-signal", default=True,
              help="Only use prompts that have produced enabled DB tasks. "
                   "Use --no-require-quality-signal to include all pairs.")
@click.option("--rich/--minimal", default=True,
              help="Rich: pre-compute all 8 inputs per example (no live I/O, no leakage). "
                   "Minimal: legacy 2-input examples (kept for compatibility).")
@click.option("--output", type=click.Path(), default=None,
              help="Where to save the compiled program JSON.")
@click.option("--model", default=None,
              help="LLM to use for compilation calls.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Build the trainset, print stats, and exit without LLM calls.")
def compile_cli(optimizer, max_examples, holdout, require_quality_signal,
                rich, output, model, dry_run):
    """Compile the prompt generator agent."""
    click.echo(f"\n{'='*70}")
    click.echo(" COMPILING PROMPT GENERATOR AGENT")
    click.echo(f"{'='*70}")
    click.echo(f" Optimizer:    {optimizer}")
    click.echo(f" Max examples: {max_examples}")
    click.echo(f" Hold-out:     {holdout}")
    click.echo(f" Quality only: {require_quality_signal}")
    click.echo(f" Example shape: {'rich (8 inputs)' if rich else 'minimal (2 inputs)'}")
    click.echo()

    # 1. Build training set
    click.echo(" Collecting training pairs...")
    pairs = collect_training_pairs(
        env="dev",
        require_quality_signal=require_quality_signal,
    )
    click.echo(f"   Found {len(pairs)} training pairs")

    # Prefer pairs with the most DB task signal first
    pairs = sorted(pairs, key=lambda p: -p.db_task_count)

    if max_examples > 0 and len(pairs) > max_examples + holdout:
        pairs = pairs[: max_examples + holdout]

    # Split: top quality → trainset, next slice → holdout
    if holdout > 0 and len(pairs) > holdout:
        train_pairs = pairs[:-holdout]
        holdout_pairs = pairs[-holdout:]
    else:
        train_pairs = pairs
        holdout_pairs = []

    click.echo(f"   Trainset: {len(train_pairs)} pairs")
    for p in train_pairs:
        names = " + ".join(p.competency_names)
        click.echo(f"     - {names} ({p.proficiency}) [{p.db_task_count} DB tasks]")
    if holdout_pairs:
        click.echo(f"   Hold-out: {len(holdout_pairs)} pairs (used for A/B scoring)")
        for p in holdout_pairs:
            names = " + ".join(p.competency_names)
            click.echo(f"     - {names} ({p.proficiency}) [{p.db_task_count} DB tasks]")

    # 2. Build dspy.Examples
    if rich:
        click.echo("\n Pre-computing rich inputs for trainset (1 Supabase query per pair)...")
        train_examples = to_dspy_examples_rich(train_pairs, env="dev")
        holdout_examples = (
            to_dspy_examples_rich(holdout_pairs, env="dev") if holdout_pairs else []
        )
    else:
        train_examples = to_dspy_examples(train_pairs)
        holdout_examples = to_dspy_examples(holdout_pairs) if holdout_pairs else []
    click.echo(
        f"   Built {len(train_examples)} train examples"
        + (f" + {len(holdout_examples)} hold-out" if holdout_examples else "")
    )

    if dry_run:
        click.echo("\n[DRY RUN] Stopping before LLM calls.")
        # Print one example's field sizes so the operator can sanity-check
        if train_examples:
            ex = train_examples[0]
            click.echo(f"\n First example field sizes:")
            for f in (
                "competencies", "proficiency", "task_category", "competency_scopes",
                "reference_prompts", "similar_tasks", "detailed_skill_signal",
                "feedback_from_previous_attempt", "new_prompt_file",
            ):
                v = getattr(ex, f, None)
                if v is None:
                    continue
                if isinstance(v, str):
                    click.echo(f"   {f:35s} {len(v):>6} chars")
        return

    # 3. Configure DSPy with the cheap COMPILE model (Haiku by default).
    configure_dspy(model=model, mode="compile")
    click.echo(f"\n DSPy configured (mode=compile, model={model or 'default Haiku'}).")

    # 4. Build the trainable module
    program = TrainingSubset()

    # 5. Optimize
    click.echo(f"\n Compiling with {optimizer}...")
    start = time.time()
    if optimizer == "bootstrap":
        opt = dspy.BootstrapFewShot(
            metric=quality_metric,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
            max_rounds=1,
        )
        compiled = opt.compile(program, trainset=train_examples)
    else:
        opt = dspy.MIPROv2(
            metric=quality_metric,
            num_threads=2,
            auto="light",
        )
        compiled = opt.compile(
            program,
            trainset=train_examples,
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
        )
    elapsed = time.time() - start
    click.echo(f" Compilation took {elapsed:.1f}s")

    # 6. Save
    if output is None:
        output = COMPILED_DIR / f"agent_{optimizer}.json"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    compiled.save(str(output))
    click.echo(f"\n Saved compiled program to: {output}")

    # 7. Optional A/B scoring on the held-out slice
    if holdout_examples:
        click.echo(f"\n{'='*70}")
        click.echo(" A/B SCORING ON HOLD-OUT")
        click.echo(f"{'='*70}")
        uncompiled = TrainingSubset()
        uncompiled_scores: list[float] = []
        compiled_scores: list[float] = []
        for ex in holdout_examples:
            inputs = ex.inputs().toDict() if hasattr(ex.inputs(), "toDict") else dict(ex.inputs())
            try:
                pred_u = uncompiled(**inputs)
                pred_c = compiled(**inputs)
            except Exception as e:
                click.echo(f"   ⚠ skipping {ex.competencies}: {e}")
                continue
            su = quality_metric(ex, pred_u)
            sc = quality_metric(ex, pred_c)
            uncompiled_scores.append(su)
            compiled_scores.append(sc)
            click.echo(
                f"   {ex.competencies:60s} "
                f"uncompiled={su:.3f}  compiled={sc:.3f}  Δ={sc-su:+.3f}"
            )
        if uncompiled_scores:
            avg_u = sum(uncompiled_scores) / len(uncompiled_scores)
            avg_c = sum(compiled_scores) / len(compiled_scores)
            click.echo()
            click.echo(f"   Average uncompiled: {avg_u:.3f}")
            click.echo(f"   Average compiled:   {avg_c:.3f}")
            click.echo(f"   Lift:               {avg_c - avg_u:+.3f}")
            verdict = (
                "ship" if (avg_c - avg_u) >= 0.05
                else "marginal — collect more trainset" if (avg_c - avg_u) >= 0
                else "regression — investigate before shipping"
            )
            click.echo(f"   Verdict:            {verdict}")


if __name__ == "__main__":
    compile_cli()
