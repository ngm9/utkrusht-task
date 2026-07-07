"""Guard tests for the extracted flows/_base stage machinery."""
from flows._base.registry import TECH_STAGES
from flows._base.stage import StageSpec


def test_tech_stage_order():
    names = [s.name for s in TECH_STAGES]
    assert names == [
        "00_preflight", "01_input_files", "02_scenarios", "03_prompt", "04_tasks",
    ]


def test_tech_stage_modules_are_flows_tech():
    for spec in TECH_STAGES:
        assert spec.module.startswith("flows.tech.stages."), spec.module


def test_only_stage4_exits_zero_on_reject():
    exits = {s.name: s.exit0_on_reject for s in TECH_STAGES}
    assert exits["04_tasks"] is True
    assert all(v is False for k, v in exits.items() if k != "04_tasks")


def test_preflight_is_the_only_untraced_stage():
    traced = {s.name: s.traced for s in TECH_STAGES}
    assert traced["00_preflight"] is False
    assert all(v is True for k, v in traced.items() if k != "00_preflight")


def test_stagespec_is_frozen():
    spec = StageSpec("x", "flows.tech.stages.x")
    try:
        spec.name = "y"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("StageSpec must be frozen")
