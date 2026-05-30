"""In-process orchestrator (A2).

Replaces the ``run_pipeline.py`` subprocess chain with a single Python
process that walks the five pipeline stages in order, capturing per-stage
logs to a per-run workspace and surfacing the final result.

Public surface:

* :class:`Orchestrator` — the runner; takes a brief and a workspace path.
* :class:`StageResult`  — typed outcome of one stage.
* :class:`PipelineResult` — typed outcome of the full pipeline.
* :func:`run_pipeline_for_job` — convenience for the B3 worker.
"""

from apps.orchestrator.pipeline import (
    Orchestrator,
    PipelineResult,
    StageResult,
    run_pipeline_for_job,
)

__all__ = [
    "Orchestrator",
    "PipelineResult",
    "StageResult",
    "run_pipeline_for_job",
]
