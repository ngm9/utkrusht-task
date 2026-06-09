"""Unit tests for ``resolve_scenarios`` — the shared candidate-pool loader.

DB-first with a JSON fallback, used by both ``create_task`` (to feed the
generator) and the orchestrator's scenario stage (to surface candidates for
the human-in-the-loop selection step).
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from generators.task import creator

_COMPS = [{"name": "Langchain", "proficiency": "BASIC"}]


def test_resolve_scenarios_prefers_db():
    """When the DB returns rows, those are used and JSON is never read."""
    with patch("infra.utils.build_scenario_key", return_value="combo-key"), patch(
        "generators.scenarios.repository.load_scenarios_for_combo",
        return_value=["db-scenario-1", "db-scenario-2"],
    ) as db_loader, patch.object(creator, "load_relevant_scenarios") as json_loader:
        out = creator.resolve_scenarios(_COMPS, Path("/tmp/x.json"), env="dev")

    assert out == ["db-scenario-1", "db-scenario-2"]
    db_loader.assert_called_once()
    json_loader.assert_not_called()


def test_resolve_scenarios_falls_back_to_json_when_db_empty():
    """An empty DB result triggers the JSON-file fallback."""
    with patch("infra.utils.build_scenario_key", return_value="combo-key"), patch(
        "generators.scenarios.repository.load_scenarios_for_combo",
        return_value=[],
    ), patch.object(
        creator, "load_relevant_scenarios", return_value=["json-scenario"]
    ) as json_loader:
        out = creator.resolve_scenarios(_COMPS, Path("/tmp/x.json"), env="dev")

    assert out == ["json-scenario"]
    json_loader.assert_called_once()


def test_resolve_scenarios_defaults_proficiency_when_missing():
    """A competency without a proficiency falls back to BASIC for the lookup."""
    comps = [{"name": "Langchain"}]
    with patch("infra.utils.build_scenario_key", return_value="combo-key"), patch(
        "generators.scenarios.repository.load_scenarios_for_combo",
        return_value=["x"],
    ) as db_loader:
        creator.resolve_scenarios(comps, Path("/tmp/x.json"), env="dev")

    _, kwargs = db_loader.call_args
    assert kwargs["proficiency"] == "BASIC"
