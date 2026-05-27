"""End-to-end smoke test for resolve_plan_v2 against live dev Supabase.

Costs one real LLM call (~$0.001 via Portkey). Verifies the full path:
  1. cache miss in task_template_match
  2. load active templates (utkrusht-python)
  3. classify via classify_match_v2 (LLM)
  4. upsert task_template_match row
  5. hydrate the template
  6. cache hit on a second call

Run from repo root:
    python scripts/smoke_test_v2_end_to_end.py
"""
from __future__ import annotations

import sys
import time

from dotenv import load_dotenv

load_dotenv()

from infra.classifier.runtime import Competency  # noqa: E402
from generators.task.runtime_resolver import (  # noqa: E402
    _build_supabase_client,
    resolve_plan_v2,
)


def _hr(title: str) -> None:
    print(f"\n{'─' * 70}\n  {title}\n{'─' * 70}")


def show(plan) -> None:
    print(f"  combo_key:  {plan.combo_key!r}")
    if plan.match is None:
        print("  match:      None (LLM failure)")
    elif plan.match.template_id is None:
        print(f"  match:      NO_MATCH — {plan.match.no_match_reason}")
        print(f"  missing:    {plan.match.missing_capabilities}")
        print(f"  suggested:  {plan.match.suggested_template}")
    else:
        print(f"  template_id: {plan.match.template_id}")
        print(f"  persona:     {plan.match.persona}")
        print(f"  confidence:  {plan.match.confidence:.2f}")
    if plan.template:
        print(f"  template:   {plan.template.template_id} "
              f"(registry_version={plan.template.registry_version})")
        print(f"  build_cmd:  {plan.template.build_cmd}")
        print(f"  test_cmd:   {plan.template.test_cmd}")


def main() -> int:
    client = _build_supabase_client()

    # Pick a combo that should clearly match utkrusht-python.
    competencies = [
        Competency("Python", "INTERMEDIATE"),
        Competency("FastAPI", "INTERMEDIATE"),
        Competency("PostgreSQL", "INTERMEDIATE"),
    ]

    _hr(f"1. First call (expect cache MISS → LLM)")
    t0 = time.time()
    plan_1 = resolve_plan_v2(competencies, supabase=client)
    dt_1 = time.time() - t0
    print(f"  elapsed: {dt_1*1000:.0f} ms")
    show(plan_1)

    _hr(f"2. Second call (expect cache HIT)")
    t0 = time.time()
    plan_2 = resolve_plan_v2(competencies, supabase=client)
    dt_2 = time.time() - t0
    print(f"  elapsed: {dt_2*1000:.0f} ms")
    show(plan_2)
    print(f"\n  speedup: {dt_1/max(dt_2, 0.001):.1f}× faster (should be ≥5× if cache hit)")

    _hr("3. Polyglot-ish combo (no perfect template fit)")
    polyglot = [
        Competency("Rust", "INTERMEDIATE"),
        Competency("React", "INTERMEDIATE"),
    ]
    plan_3 = resolve_plan_v2(polyglot, supabase=client)
    show(plan_3)
    print("\n  (only utkrusht-python is built; LLM should return no_match here)")

    _hr("4. Infra task (definitely no_match)")
    infra = [
        Competency("Kubernetes", "INTERMEDIATE"),
        Competency("Helm", "INTERMEDIATE"),
        Competency("Terraform", "INTERMEDIATE"),
    ]
    plan_4 = resolve_plan_v2(infra, supabase=client)
    show(plan_4)

    _hr("Summary")
    print(f"  Call 1 (miss):     {dt_1*1000:>6.0f} ms — wrote row to task_template_match")
    print(f"  Call 2 (hit):      {dt_2*1000:>6.0f} ms — no LLM")
    print(f"  Polyglot rust/react: {plan_3.match.template_id or 'no_match'}")
    print(f"  Infra k8s/helm/tf:   {plan_4.match.template_id or 'no_match'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
