"""Validate interview slot values against real data before they enter the brief."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Any

from task_builder.slots import VALID_PROFICIENCIES


@dataclass(frozen=True)
class SlotValidation:
    """Outcome of validating one slot value."""

    ok: bool
    cleaned: Any = None
    error: str | None = None
    suggestions: tuple[str, ...] = field(default_factory=tuple)


def validate_proficiency(value: str) -> SlotValidation:
    """Normalise a proficiency string to the canonical upper-case enum value."""
    if not value or not value.strip():
        return SlotValidation(ok=False, error="Proficiency is empty.")
    upper = value.strip().upper()
    if upper in VALID_PROFICIENCIES:
        return SlotValidation(ok=True, cleaned=upper)
    return SlotValidation(
        ok=False,
        error=f"'{value}' is not a valid proficiency. "
              f"Choose one of: {', '.join(VALID_PROFICIENCIES)}.",
    )


def _all_competency_names(supabase: Any) -> list[str]:
    """Fetch the distinct competency names in the table (for close-match suggestions)."""
    result = supabase.table("competencies").select("name").execute()
    return sorted({row["name"] for row in (result.data or []) if row.get("name")})


def validate_competency(name: str, proficiency: str, supabase: Any) -> SlotValidation:
    """Check that a competency exists in Supabase at the given proficiency.

    On miss, returns up to 5 close-name suggestions so the bot can re-ask.
    """
    if not name:
        return SlotValidation(ok=False, error="Competency name is empty.")
    stripped = name.strip()
    match = (
        supabase.table("competencies")
        .select("name")
        .ilike("name", stripped)
        .eq("proficiency", proficiency)
        .execute()
    )
    if match.data:
        return SlotValidation(ok=True, cleaned=match.data[0]["name"])

    all_names = _all_competency_names(supabase)
    suggestions = difflib.get_close_matches(stripped, all_names, n=5, cutoff=0.5)
    return SlotValidation(
        ok=False,
        error=f"No competency '{name}' at {proficiency} level.",
        suggestions=tuple(suggestions),
    )
