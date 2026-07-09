"""Flow-agnostic pipeline machinery shared by every flow under ``flows/``.

Public surface:
- ``flows._base.stage.StageSpec`` — static description of one pipeline stage.
- ``flows._base.registry`` — ordered ``StageSpec`` lists, one per flow.
- ``flows._base.runner`` — the subprocess-per-stage runner (interpreter picker,
  per-stage log/timing capture, live stderr sub-log splitting, run summary).
"""
