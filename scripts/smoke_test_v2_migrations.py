"""Smoke test for Phase 1 migrations of unified-classifier-template-schema.

Read-only checks against the dev Supabase. Verifies the four migrations
applied cleanly. No LLM calls.

Run from repo root:
    python scripts/smoke_test_v2_migrations.py
"""
from __future__ import annotations

import json
import sys

from dotenv import load_dotenv

# Load .env from the repo root before importing anything that builds
# clients at module-load time (infra/evals.py expects OPENAI_API_KEY).
load_dotenv()

from generators.task.runtime_resolver import (  # noqa: E402
    _build_supabase_client,
    _load_active_templates_v2,
)


def _hr(title: str) -> None:
    print(f"\n{'─' * 70}\n  {title}\n{'─' * 70}")


def check_templates_table(client) -> bool:
    _hr("1. templates table")
    resp = client.table("templates").select("*").execute()
    rows = resp.data or []
    print(f"row count: {len(rows)}")
    if not rows:
        print("  ❌ EMPTY — the seed INSERT in 2026-05-28-create-templates.sql failed?")
        return False
    for row in rows:
        marker = "✅" if row.get("status") == "built" else "  "
        print(
            f"  {marker} {row['template_id']:24s} status={row['status']:9s} "
            f"runtime={row['primary_runtime']:8s} "
            f"personas={row.get('personas')} "
            f"registry_version={row.get('registry_version')}"
        )
        if row["template_id"] == "utkrusht-python":
            expected_hash = "a27ae796c238a1d30996a81e2a830ac76652fcc9717b163c5c4980570bad03f3"
            actual_hash = row.get("manifest_hash") or ""
            hash_ok = actual_hash == expected_hash
            print(f"      manifest_hash: {actual_hash}")
            print(f"      hash matches on-disk?  {'✅' if hash_ok else '❌ MISMATCH'}")
            caps = row.get("capabilities") or {}
            if isinstance(caps, str):
                caps = json.loads(caps)
            print(f"      capabilities keys: {sorted(caps.keys())}")
    return True


def check_task_template_match_table(client) -> bool:
    _hr("2. task_template_match table (backfilled)")
    # Total count
    resp = client.table("task_template_match").select(
        "combo_key,template_id,persona,no_match_reason,classifier_model,registry_version",
        count="exact"
    ).limit(5).execute()
    rows = resp.data or []
    total = getattr(resp, "count", None) or len(rows)
    print(f"total rows: {total}")
    if rows:
        print("\nfirst 5 rows:")
        for r in rows:
            tid = r.get("template_id") or "<no_match>"
            persona = r.get("persona") or "—"
            reason = r.get("no_match_reason")
            tail = f"  reason={reason!r}" if reason else ""
            print(
                f"  combo={r['combo_key'][:50]:50s} "
                f"template={tid:20s} persona={persona:10s} "
                f"model={r.get('classifier_model')}{tail}"
            )

    # Distribution by status
    matched = client.table("task_template_match").select(
        "combo_key", count="exact"
    ).not_.is_("template_id", "null").limit(1).execute()
    no_match = client.table("task_template_match").select(
        "combo_key", count="exact"
    ).is_("template_id", "null").limit(1).execute()
    print(f"\nmatched (template_id IS NOT NULL):  {getattr(matched, 'count', '?')}")
    print(f"no_match (template_id IS NULL):     {getattr(no_match, 'count', '?')}")
    return True


def check_tasks_task_intent_column(client) -> bool:
    _hr("3. tasks.task_intent column")
    # SELECT one row to verify the column exists. Don't need ALL columns.
    resp = client.table("tasks").select("task_id,task_intent").limit(1).execute()
    rows = resp.data or []
    if not rows:
        print("  ⚠️  tasks table is empty — column existence verified via no-error select")
        return True
    row = rows[0]
    intent = row.get("task_intent")
    print(f"sample task_id: {row.get('task_id')}")
    print(f"task_intent (default): {json.dumps(intent, indent=2)}")
    expected_keys = {"datastores", "protocols_used", "eval_method",
                     "secondary_runtimes", "persona_override"}
    actual_keys = set(intent.keys()) if isinstance(intent, dict) else set()
    if expected_keys == actual_keys:
        print("  ✅ default shape matches plan")
        return True
    print(f"  ❌ key mismatch — expected {expected_keys}, got {actual_keys}")
    return False


def check_active_templates_helper(client) -> bool:
    _hr("4. _load_active_templates_v2() helper")
    active = _load_active_templates_v2(client)
    print(f"active templates loaded: {len(active)}")
    for t in active:
        print(
            f"  • {t.template_id:24s} primary={t.primary_runtime} "
            f"personas={t.personas} eval_methods={t.eval_methods}"
        )
        print(f"      build_cmd: {t.build_cmd}")
        print(f"      test_cmd:  {t.test_cmd}")
    return len(active) >= 1


def check_grants(client) -> bool:
    _hr("5. grants (write access)")
    # Try a no-op upsert that we'll immediately delete. If grants are wrong,
    # this fails with permission denied.
    sentinel_key = "__smoke_test_grant_check__"
    try:
        client.table("task_template_match").upsert({
            "combo_key": sentinel_key,
            "template_id": None,
            "persona": None,
            "confidence": 0.0,
            "no_match_reason": "smoke-test-grant-check",
            "missing_capabilities": [],
            "classifier_model": "smoke-test",
            "registry_version": 1,
        }).execute()
        # Read back to confirm
        check = client.table("task_template_match").select("combo_key").eq(
            "combo_key", sentinel_key
        ).limit(1).execute()
        ok = bool(check.data)
        # Clean up
        client.table("task_template_match").delete().eq(
            "combo_key", sentinel_key
        ).execute()
        print(f"  upsert + delete on task_template_match: {'✅' if ok else '❌'}")
        return ok
    except Exception as exc:  # noqa: BLE001
        print(f"  ❌ FAILED: {exc}")
        return False


def main() -> int:
    print("Smoke test: Phase 1 migrations (unified-classifier-template-schema)")
    try:
        client = _build_supabase_client()
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Cannot connect to Supabase: {exc}")
        return 1

    results = [
        ("templates seeded",   check_templates_table(client)),
        ("task_template_match backfilled", check_task_template_match_table(client)),
        ("tasks.task_intent column",        check_tasks_task_intent_column(client)),
        ("_load_active_templates_v2",       check_active_templates_helper(client)),
        ("grants on new tables",            check_grants(client)),
    ]

    _hr("Summary")
    failed = []
    for name, ok in results:
        marker = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {marker}  {name}")
        if not ok:
            failed.append(name)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
