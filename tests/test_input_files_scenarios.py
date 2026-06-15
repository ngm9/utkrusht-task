"""The stage-03 scenario reader (build_detailed_skill_signal's source) is
DB-FIRST so it sees what stage 02 actually wrote (the generated_scenarios DB
table, not task_scenarios.json), with the JSON index as a fallback.
"""
from __future__ import annotations

import types

import generators.scenarios.repository as scenario_repo
from generators.prompts import input_files as ifs


def _combo():
    return [
        types.SimpleNamespace(name="Golang", proficiency="BASIC"),
        types.SimpleNamespace(name="Kafka", proficiency="BASIC"),
    ]


def test_scenarios_db_first(monkeypatch):
    """When the DB has scenarios for the combo, they are used (DB-first)."""
    seen = {}

    def fake_db(env, combo_key, proficiency):
        seen.update(env=env, combo_key=combo_key, proficiency=proficiency)
        return ["S1 from DB", "S2 from DB"]

    monkeypatch.setattr(scenario_repo, "load_scenarios_for_combo", fake_db)
    # JSON path must NOT be consulted when the DB returns rows.
    monkeypatch.setattr(ifs, "_load_scenarios_index", lambda prof: {"x": ["should-not-use"]})

    out = ifs.load_scenarios_for_combo(_combo(), env="dev")
    assert out == ["S1 from DB", "S2 from DB"]
    # exact combo_key + proficiency the writer used
    assert seen == {"env": "dev", "combo_key": "Golang (BASIC), Kafka (BASIC)", "proficiency": "BASIC"}


def test_scenarios_json_fallback(monkeypatch):
    """When the DB returns nothing, fall back to the JSON index by combo key."""
    monkeypatch.setattr(scenario_repo, "load_scenarios_for_combo", lambda **k: [])
    monkeypatch.setattr(
        ifs, "_load_scenarios_index",
        lambda prof: {"Golang (BASIC), Kafka (BASIC)": ["JSON scenario text"]},
    )
    out = ifs.load_scenarios_for_combo(_combo(), env="dev")
    assert out == ["JSON scenario text"]


def test_scenarios_db_error_falls_back(monkeypatch):
    """A DB error is swallowed and the JSON fallback is used (failure-isolated)."""
    def boom(**k):
        raise RuntimeError("supabase down")

    monkeypatch.setattr(scenario_repo, "load_scenarios_for_combo", boom)
    monkeypatch.setattr(
        ifs, "_load_scenarios_index",
        lambda prof: {"Golang (BASIC), Kafka (BASIC)": ["fallback scenario"]},
    )
    out = ifs.load_scenarios_for_combo(_combo(), env="dev")
    assert out == ["fallback scenario"]
