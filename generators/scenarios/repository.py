"""Supabase-backed CRUD for the ``generated_scenarios`` table.

This is the B4 implementation per docs/plans/2026-05-29-v1-schema.md.
It replaces the shared-file append in ``generators/scenarios/generator.py``
that caused JSON corruption under concurrent runs and left the repo tree
dirty after every pipeline run.

Public surface:

    scenario_hash(text)                      — stable hash for dedup
    upsert_scenarios(env, combo_key, …)      — idempotent insert
    load_scenarios_for_combo(env, combo, …)  — DB read, scoped to one combo
    load_all_scenarios_for_proficiency(env)  — DB read, broad dedup pool

Each call lazy-initialises a Supabase client and silently degrades to ``[]``
or ``0`` on connection error so callers can keep working off the curated
JSON files until the DB is reachable.
"""
from __future__ import annotations

import hashlib
import logging
from functools import lru_cache
from typing import Any, Iterable

logger = logging.getLogger(__name__)


def scenario_hash(text: str) -> str:
    """Stable hash used by the UNIQUE(combo_key, proficiency, scenario_hash) index.

    sha1 of the lower-cased, whitespace-trimmed text — small whitespace or
    casing diffs collapse to the same row, which is what we want for dedup.
    """
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()


@lru_cache(maxsize=2)
def _client(env: str) -> Any | None:
    """Cached Supabase client per env. Returns None on failure so callers
    can degrade gracefully."""
    try:
        from generators.task.persistence import init_supabase
        return init_supabase(env)
    except Exception as exc:
        logger.warning("scenarios repository: supabase init failed for env=%s: %s", env, exc)
        return None


def upsert_scenarios(
    env: str,
    combo_key: str,
    proficiency: str,
    scenarios: Iterable[str],
    *,
    source: str = "scenario_generator",
    generator_model: str | None = None,
    domain: str | None = None,
    focus_areas: list[str] | None = None,
) -> int:
    """Upsert each scenario for ``(combo_key, proficiency)``.

    Returns the number of new rows actually written. Existing rows
    (same scenario_hash) are no-ops thanks to the UNIQUE index +
    ``ignore_duplicates=True``.
    """
    client = _client(env)
    if client is None:
        return 0

    rows: list[dict[str, Any]] = []
    for text in scenarios:
        if not isinstance(text, str) or not text.strip():
            continue
        rows.append({
            "combo_key": combo_key,
            "proficiency": proficiency.upper(),
            "scenario_text": text,
            "scenario_hash": scenario_hash(text),
            "source": source,
            "generator_model": generator_model,
            "domain": domain,
            "focus_areas": focus_areas or [],
        })

    if not rows:
        return 0

    try:
        result = client.table("generated_scenarios").upsert(
            rows,
            on_conflict="combo_key,proficiency,scenario_hash",
            ignore_duplicates=True,
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as exc:
        logger.warning(
            "scenarios repository: upsert failed for combo=%r prof=%s: %s",
            combo_key, proficiency, exc,
        )
        return 0


def load_scenarios_for_combo(
    env: str,
    combo_key: str,
    proficiency: str,
    *,
    limit: int = 100,
    include_reversed: bool = True,
) -> list[str]:
    """Load existing scenarios for a single combo.

    For 2-competency combos we also check the reversed key shape
    ("B, A" vs "A, B") — the historical JSON files sometimes stored
    them in different orders.
    """
    client = _client(env)
    if client is None:
        return []

    keys = [combo_key]
    if include_reversed:
        parts = [p.strip() for p in combo_key.split(",")]
        if len(parts) == 2:
            reversed_key = f"{parts[1]}, {parts[0]}"
            if reversed_key != combo_key:
                keys.append(reversed_key)

    out: list[str] = []
    for k in keys:
        try:
            result = (
                client.table("generated_scenarios")
                .select("scenario_text")
                .eq("combo_key", k)
                .eq("proficiency", proficiency.upper())
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            out.extend(row["scenario_text"] for row in (result.data or []))
        except Exception as exc:
            logger.warning(
                "scenarios repository: select failed for combo=%r prof=%s: %s",
                k, proficiency, exc,
            )
    return out


def load_all_scenarios_for_proficiency(
    env: str,
    proficiency: str,
    *,
    limit: int = 1000,
) -> list[str]:
    """Broad dedup pool — every scenario text at a proficiency level."""
    client = _client(env)
    if client is None:
        return []
    try:
        result = (
            client.table("generated_scenarios")
            .select("scenario_text")
            .eq("proficiency", proficiency.upper())
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [row["scenario_text"] for row in (result.data or [])]
    except Exception as exc:
        logger.warning(
            "scenarios repository: dedup-pool select failed for prof=%s: %s",
            proficiency, exc,
        )
        return []
