-- migrations/2026-05-22-task-runtime-column.sql
-- Adds the per-task task_runtime JSONB column on the tasks table.
-- Apply via the Supabase SQL editor on dev first, then prod.
--
-- The classifier writes here directly when a task is created or backfilled.
-- No separate cache table — see docs/research/task-classifier-and-templates.md.

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS task_runtime JSONB;

-- Secondary index for analytics queries by kind (e.g. "all app tasks").
CREATE INDEX IF NOT EXISTS idx_tasks_task_runtime_kind
    ON tasks ((task_runtime->>'kind'));
