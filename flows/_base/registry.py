"""Per-flow ordered stage manifests.

Order IS the pipeline order. The ``module`` field is the single source of truth
for each stage's ``python -m <module>`` target — flow pipeline modules read it
here instead of hardcoding module strings inline.
"""
from __future__ import annotations

from flows._base.runner import E2B_GATE_MARKERS, EVAL_MARKERS
from flows._base.stage import StageSpec

TECH_STAGES: list[StageSpec] = [
    StageSpec("00_preflight", "flows.tech.stages.preflight"),
    StageSpec("01_input_files", "flows.tech.stages.input_files", traced=True),
    StageSpec("02_scenarios", "flows.tech.stages.scenarios", traced=True),
    StageSpec("03_prompt", "flows.tech.stages.prompts", traced=True),
    StageSpec(
        "04_tasks",
        "flows.tech.stages.generate",
        traced=True,
        exit0_on_reject=True,
        live_markers=(
            ("04_tasks.e2b_gate.log", E2B_GATE_MARKERS),
            ("04_tasks.evals.log", EVAL_MARKERS),
        ),
    ),
]
