"""CLI entry point — `python -m task_input_parser <brief-path>`."""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

import click

from infra.logger_config import logger
from task_input_parser.brief_parser import parse
from task_input_parser.extractor import run as run_extractor


def _make_run_dir(output_root: Path) -> Path:
    """Create and return a fresh timestamped extract_<timestamp>/ directory inside output_root."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    base = datetime.utcnow().strftime("extract_%Y-%m-%d_%H-%M-%S")
    candidate = output_root / base
    suffix = 1
    while candidate.exists():
        candidate = output_root / f"{base}_{suffix}"
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


@click.command()
@click.argument("brief_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output-root", default="tmp", show_default=True, type=click.Path(file_okay=False, path_type=Path),
              help="Parent directory where the per-run extract_<timestamp>/ folder is created.")
def main(brief_path: Path, output_root: Path):
    """Convert a customer assessment brief into one markdown file per task."""
    start = time.monotonic()
    output_dir = _make_run_dir(output_root)
    click.echo(f"[parser] output dir: {output_dir}")

    try:
        ast = parse(brief_path)
    except Exception as e:
        click.echo(f"[parser] ERROR: failed to parse brief: {e}", err=True)
        sys.exit(2)
    click.echo(f"[parser] parsed: {len(ast.sections)} sections, "
               f"{len(ast.tables)} tables, "
               f"{len(ast.embedded_images)} images, "
               f"{len(ast.external_links)} external links, "
               f"{len(ast.code_fences)} code fences")

    try:
        summary = run_extractor(ast, output_dir)
    except Exception as e:
        click.echo(f"[parser] ABORTED: extraction failed: {e}", err=True)
        logger.exception("[parser] extraction crashed")
        sys.exit(3)

    elapsed = time.monotonic() - start

    click.echo("")
    click.echo("=" * 60)
    click.echo("[parser] run summary")
    click.echo("=" * 60)
    click.echo(f"  tasks emitted     : {len(summary.emitted_tasks)}")
    click.echo(f"  inline **Note:**  : {summary.inline_notes}")
    click.echo(f"  elapsed (s)       : {elapsed:.2f}")
    click.echo(f"  output dir        : {output_dir}")
    if summary.aborted:
        click.echo(f"  aborted           : {summary.abort_reason}")
    for path in summary.emitted_tasks:
        click.echo(f"    - {path}")

    sys.exit(0 if not summary.aborted else 4)


if __name__ == "__main__":
    main()
