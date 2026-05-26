-- Drop the per-task task_runtime snapshot column.
--
-- Why: the column was write-only — populated on every task by
-- multiagent.py (and once by scripts/backfill_task_runtime.py), and
-- never read by any consumer. The classification is now (Phase 1 of
-- docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md)
-- moving to a per-combo cache keyed by competency-set, which makes the
-- per-task snapshot redundant.
--
-- Data loss: ~341 rows of snapshot values are dropped. Reconstructable
-- by re-classifying each unique competency combo (~50 combos in dev,
-- ~$0.001 per LLM call → ~$0.05 to rebuild).
--
-- The in-memory `task_runtime` value in multiagent.py.create_task is
-- unchanged — it still drives eval-persona routing and the E2B gate's
-- template lookup within the same run. Only the DB column is removed.

ALTER TABLE tasks DROP COLUMN IF EXISTS task_runtime;
