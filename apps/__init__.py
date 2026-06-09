"""User-facing entry points — UI (task_builder), CLI, orchestrator.

Per the layout migration in docs/plans/2026-05-22-task-generator-production-readiness.md
this package will eventually own task_builder, cli, and orchestrator. Today
only ``apps.orchestrator`` lives here; the others ship in their existing
top-level locations until Phase 3 of the layout migration.
"""
