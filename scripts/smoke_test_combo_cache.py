"""Smoke test for the competency_combo_classification cache (B1).

Resolves the same competency combo twice:
  1. First call should be a cache MISS → LLM call → row INSERTed.
  2. Second call should be a cache HIT → no LLM call.

Run after the two migrations have been applied to the Supabase dev DB:
  • migrations/2026-05-25-create-template-registry.sql
  • migrations/2026-05-25-create-competency-combo-classification.sql

Usage:
  python -m scripts.smoke_test_combo_cache
"""
from __future__ import annotations

import os
import sys
import time

# Load .env so SUPABASE_URL_APTITUDETESTSDEV / UTKRUSHT_ORG_ID are present.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from prompt_generator.runtime import Competency
from task_generation.runtime_resolver import resolve_plan


def _banner(text: str) -> None:
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def main() -> int:
    if not os.getenv("UTKRUSHT_ORG_ID"):
        print("ERROR: UTKRUSHT_ORG_ID not set in env. Aborting.", file=sys.stderr)
        return 1
    if not os.getenv("SUPABASE_URL_APTITUDETESTSDEV"):
        print("ERROR: SUPABASE_URL_APTITUDETESTSDEV not set. Aborting.", file=sys.stderr)
        return 1

    comps = [
        Competency(name="Python", proficiency="INTERMEDIATE"),
        Competency(name="FastAPI", proficiency="INTERMEDIATE"),
    ]

    _banner("Call 1 — expected: cache MISS, LLM call, row inserted")
    t0 = time.perf_counter()
    plan1 = resolve_plan(comps)
    dt1 = time.perf_counter() - t0
    print(f"  combo_key       : {plan1.combo_key}")
    print(f"  runtime         : {plan1.runtime}")
    print(f"  kind            : {plan1.kind}")
    if plan1.task_runtime:
        print(f"  frameworks      : {plan1.task_runtime.frameworks}")
        print(f"  datastores      : {plan1.task_runtime.datastores}")
        print(f"  needs_browser   : {plan1.task_runtime.needs_browser}")
    print(f"  template        : {plan1.template.name if plan1.template else '(none)'}")
    print(f"  elapsed         : {dt1:.2f}s")

    _banner("Call 2 — expected: cache HIT, no LLM call, ~10ms")
    t0 = time.perf_counter()
    plan2 = resolve_plan(comps)
    dt2 = time.perf_counter() - t0
    print(f"  combo_key       : {plan2.combo_key}")
    print(f"  runtime         : {plan2.runtime}")
    print(f"  kind            : {plan2.kind}")
    print(f"  elapsed         : {dt2:.2f}s")

    _banner("Verdict")
    if plan1.runtime is None:
        print("  FAILED — first call returned an empty plan (classifier failure?)")
        return 2
    if plan1.runtime != plan2.runtime or plan1.kind != plan2.kind:
        print("  FAILED — second call returned different classification than first")
        return 3
    if dt2 > dt1 * 0.5:
        print(f"  WARNING — second call ({dt2:.2f}s) was not noticeably faster than first ({dt1:.2f}s).")
        print("            Cache might not have been hit. Check Supabase row.")
        return 4

    speedup = dt1 / dt2 if dt2 > 0 else float("inf")
    print(f"  OK — second call was {speedup:.1f}x faster ({dt1:.2f}s → {dt2:.2f}s)")
    print(f"  Cached row should be visible in Supabase dev: "
          f"competency_combo_classification WHERE combo_key = {plan1.combo_key!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
