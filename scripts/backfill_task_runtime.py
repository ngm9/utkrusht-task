"""One-shot backfill: classify every row in ``tasks`` and persist ``task_runtime``.

Usage:
    PYTHONPATH=. .venv/bin/python scripts/backfill_task_runtime.py --env dev
    PYTHONPATH=. .venv/bin/python scripts/backfill_task_runtime.py --env prod

In-memory dedup: tasks are grouped by their normalised competency-set; the LLM
is called ONCE per unique set and the resulting TaskRuntime fans out to every
task in the group. ~50 unique sets across 339 dev tasks → ~$0.05 total.

Idempotent: skips rows that already have a ``task_runtime`` value.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from dotenv import load_dotenv
from supabase import create_client

from prompt_generator.llm_classifier import classify_with_llm
from prompt_generator.runtime import Competency

_REVIEW_THRESHOLD = 0.7


def _env_creds(env: str) -> tuple[str, str]:
    """Read Supabase URL + key for the requested environment."""
    suffix = "" if env == "prod" else "DEV"
    url = os.environ[f"SUPABASE_URL_APTITUDETESTS{suffix}"]
    key = os.environ[f"SUPABASE_API_KEY_APTITUDETESTS{suffix}"]
    return url, key


def _fingerprint(criterias: list) -> frozenset[tuple[str, str]] | None:
    """Order-invariant fingerprint of a task's criterias for dedup grouping."""
    fp = frozenset(
        (c["name"].strip().lower(), c.get("proficiency", "BASIC"))
        for c in criterias if isinstance(c, dict) and c.get("name")
    )
    return fp or None


def _competencies_from(criterias: list) -> list[Competency]:
    return [
        Competency(name=c["name"], proficiency=c.get("proficiency", "BASIC"))
        for c in criterias if isinstance(c, dict) and c.get("name")
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--env", choices=("dev", "prod"), default="dev")
    ap.add_argument(
        "--limit", type=int, default=None,
        help="Optional row cap for testing (default: process all tasks).",
    )
    args = ap.parse_args()

    load_dotenv()
    url, key = _env_creds(args.env)
    sb = create_client(url, key)

    q = sb.table("tasks").select("task_id, criterias, task_runtime")
    if args.limit:
        q = q.limit(args.limit)
    rows = q.execute().data
    print(f"Loaded {len(rows)} rows from tasks ({args.env}).")

    # Group rows by unique competency fingerprint. Skip already-classified rows.
    groups: dict[frozenset, list[dict]] = {}
    already_classified = 0
    no_competencies = 0
    for r in rows:
        if r.get("task_runtime"):
            already_classified += 1
            continue
        fp = _fingerprint(r.get("criterias") or [])
        if fp is None:
            no_competencies += 1
            continue
        groups.setdefault(fp, []).append(r)

    print(
        f"  already_classified={already_classified}  "
        f"no_competencies={no_competencies}  "
        f"unique_groups_to_classify={len(groups)}"
    )

    classified_groups = failed_groups = tasks_updated = 0
    low_confidence: list[tuple[float, list[tuple[str, str]]]] = []
    start = time.time()

    for fp, tasks_in_group in groups.items():
        comps = _competencies_from(tasks_in_group[0]["criterias"])
        try:
            result = classify_with_llm(comps)
        except Exception as exc:  # noqa: BLE001 — surface anything to the operator
            failed_groups += 1
            print(f"  fail (group of {len(tasks_in_group)} tasks): {exc}")
            continue

        if result.confidence < _REVIEW_THRESHOLD:
            low_confidence.append((result.confidence, sorted(fp)))

        runtime_payload = result.runtime.model_dump()
        for r in tasks_in_group:
            sb.table("tasks").update({"task_runtime": runtime_payload}) \
                .eq("task_id", r["task_id"]).execute()
            tasks_updated += 1

        classified_groups += 1
        if classified_groups % 10 == 0:
            print(
                f"  ...classified {classified_groups}/{len(groups)} groups, "
                f"updated {tasks_updated} task rows "
                f"({time.time() - start:.1f}s elapsed)"
            )

    elapsed = time.time() - start
    print(
        f"\nDone. groups_classified={classified_groups}, failed={failed_groups}, "
        f"task_rows_updated={tasks_updated}, elapsed={elapsed:.1f}s."
    )

    if low_confidence:
        print(f"\n{len(low_confidence)} low-confidence groups for human review:")
        for conf, members in sorted(low_confidence):
            print(f"  {conf:.2f}  {members}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
