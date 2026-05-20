"""Slot validation against the proficiency enum and the Supabase competencies table."""
from unittest.mock import MagicMock

from task_builder.validation import validate_proficiency, validate_competency


def test_validate_proficiency_accepts_canonical_values():
    result = validate_proficiency("intermediate")
    assert result.ok is True
    assert result.cleaned == "INTERMEDIATE"


def test_validate_proficiency_rejects_unknown_value():
    result = validate_proficiency("expert")
    assert result.ok is False
    assert "BEGINNER" in result.error  # error lists valid options


def _supabase_returning(rows_for_match, all_names):
    """Fake Supabase client: the .ilike().eq().execute() chain returns the name+proficiency match; a plain .select().execute() returns the all-names list."""
    client = MagicMock()
    match_result = MagicMock(data=rows_for_match)
    all_result = MagicMock(data=[{"name": n} for n in all_names])
    table = client.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = match_result
    table.select.return_value.execute.return_value = all_result
    return client


def test_validate_competency_ok_when_row_exists():
    client = _supabase_returning([{"name": "Java"}], ["Java", "Python"])
    result = validate_competency("Java", "BASIC", client)
    assert result.ok is True
    assert result.cleaned == "Java"


def test_validate_competency_suggests_close_matches_when_missing():
    client = _supabase_returning([], ["Spring Boot", "Spring", "Java"])
    result = validate_competency("Sprng Boot", "BASIC", client)
    assert result.ok is False
    assert "Spring Boot" in result.suggestions


def test_validate_proficiency_rejects_empty_and_whitespace():
    assert validate_proficiency("").ok is False
    assert validate_proficiency("   ").ok is False


def test_validate_competency_rejects_empty_name():
    result = validate_competency("", "BASIC", MagicMock())
    assert result.ok is False
