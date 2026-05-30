"""Backfill `generated_scenarios` from data/generated/scenarios/*.json.

One-off script. Run once per environment AFTER applying the
``generated_scenarios`` migration from the Utkrushta backend repo
(``supabase/migrations/20260530000003_create_generated_scenarios.sql``):

    python scripts/backfill_generated_scenarios.py --env dev
    python scripts/backfill_generated_scenarios.py --env prod

It maps each JSON file → a proficiency level and inserts every scenario
string as one row with ``source='curated'``. Idempotent: re-running skips
rows whose ``(combo_key, proficiency, scenario_hash)`` already exists.

File-to-proficiency mapping (matches ``generators/scenarios/generator.py``):

    task_scenarios.json                       → BASIC
    task_scenarios_intermediate.json          → INTERMEDIATE
    task_scenarios_no_code.json               → NO_CODE
    task_scenarios_pr_review.json             → BASIC
    task_scenarios_pr_review_intermediate.json→ INTERMEDIATE
    task_scenarios_system_design.json         → INTERMEDIATE

PR-review / system-design files share the same proficiency buckets as the
build-task files — the source column tracks origin if we later need to
distinguish them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from generators.task.persistence import init_supabase  # noqa: E402

logger = logging.getLogger("backfill_generated_scenarios")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_ROOT = REPO_ROOT / "data" / "generated" / "scenarios"

FILE_TO_PROFICIENCY: dict[str, str] = {
    "task_scenarios.json": "BASIC",
    "task_scenarios_intermediate.json": "INTERMEDIATE",
    "task_scenarios_no_code.json": "NO_CODE",
    "task_scenarios_pr_review.json": "BASIC",
    "task_scenarios_pr_review_intermediate.json": "INTERMEDIATE",
    "task_scenarios_system_design.json": "INTERMEDIATE",
}


def scenario_hash(text: str) -> str:
    """Stable hash matching `generators/scenarios/repository.py`."""
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()


def load_file(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(v, list)}


def backfill(env: str, dry_run: bool = False) -> dict[str, int]:
    """Insert every scenario into `generated_scenarios`. Returns counters."""
    counts = {"files": 0, "candidates": 0, "inserted": 0, "skipped": 0, "errors": 0}

    supabase = init_supabase(env) if not dry_run else None

    for filename, proficiency in FILE_TO_PROFICIENCY.items():
        path = SCENARIOS_ROOT / filename
        if not path.exists():
            logger.info("skip missing file: %s", filename)
            continue
        counts["files"] += 1
        scenarios_by_combo = load_file(path)

        for combo_key, scenarios in scenarios_by_combo.items():
            for scenario_text in scenarios:
                counts["candidates"] += 1
                if not isinstance(scenario_text, str) or not scenario_text.strip():
                    counts["skipped"] += 1
                    continue
                row: dict[str, Any] = {
                    "combo_key": combo_key,
                    "proficiency": proficiency,
                    "scenario_text": scenario_text,
                    "scenario_hash": scenario_hash(scenario_text),
                    "source": "curated",
                }
                if dry_run:
                    counts["inserted"] += 1
                    continue
                try:
                    # upsert by the unique constraint; ignore_duplicates=True
                    # treats prior rows as a no-op.
                    result = supabase.table("generated_scenarios").upsert(
                        row,
                        on_conflict="combo_key,proficiency,scenario_hash",
                        ignore_duplicates=True,
                    ).execute()
                    if result.data:
                        counts["inserted"] += 1
                    else:
                        counts["skipped"] += 1
                except Exception as exc:
                    counts["errors"] += 1
                    logger.warning("insert failed for combo=%r: %s", combo_key, exc)

    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("dev", "prod"), default="dev")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Walk files + report counters without contacting Supabase.",
    )
    args = parser.parse_args(argv)

    logger.info("backfill start env=%s dry_run=%s", args.env, args.dry_run)
    counts = backfill(env=args.env, dry_run=args.dry_run)
    logger.info("backfill done: %s", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
