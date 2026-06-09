"""Unit tests for generators.scenarios.repository (B4)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from generators.scenarios import repository


def test_scenario_hash_is_stable_across_whitespace_and_case():
    a = repository.scenario_hash("  Hello World  ")
    b = repository.scenario_hash("hello world")
    assert a == b


def test_scenario_hash_distinguishes_distinct_text():
    assert repository.scenario_hash("one") != repository.scenario_hash("two")


def test_upsert_scenarios_skips_blanks_and_calls_supabase_once():
    fake_client = MagicMock()
    fake_table = fake_client.table.return_value
    fake_upsert = fake_table.upsert.return_value
    fake_upsert.execute.return_value = MagicMock(data=[{"id": "1"}, {"id": "2"}])

    with patch.object(repository, "_client", return_value=fake_client):
        inserted = repository.upsert_scenarios(
            env="dev",
            combo_key="Python (BASIC)",
            proficiency="BASIC",
            scenarios=["alpha", "", "   ", "beta"],
            source="scenario_generator",
        )

    assert inserted == 2
    fake_client.table.assert_called_once_with("generated_scenarios")
    args, kwargs = fake_table.upsert.call_args
    rows = args[0]
    assert len(rows) == 2
    assert {r["scenario_text"] for r in rows} == {"alpha", "beta"}
    assert kwargs["on_conflict"] == "combo_key,proficiency,scenario_hash"
    assert kwargs["ignore_duplicates"] is True


def test_upsert_scenarios_returns_zero_when_client_unavailable():
    with patch.object(repository, "_client", return_value=None):
        assert repository.upsert_scenarios(
            env="dev",
            combo_key="K",
            proficiency="BASIC",
            scenarios=["a"],
        ) == 0


def test_load_scenarios_for_combo_includes_reversed_key():
    fake_client = MagicMock()
    fake_query = fake_client.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value
    fake_query.execute.side_effect = [
        MagicMock(data=[{"scenario_text": "alpha"}]),
        MagicMock(data=[{"scenario_text": "beta"}]),
    ]

    with patch.object(repository, "_client", return_value=fake_client):
        out = repository.load_scenarios_for_combo(
            env="dev",
            combo_key="A, B",
            proficiency="BASIC",
        )

    assert out == ["alpha", "beta"]
    assert fake_query.execute.call_count == 2


def test_load_scenarios_for_combo_returns_empty_when_client_unavailable():
    with patch.object(repository, "_client", return_value=None):
        assert repository.load_scenarios_for_combo(
            env="dev",
            combo_key="Python (BASIC)",
            proficiency="BASIC",
        ) == []
