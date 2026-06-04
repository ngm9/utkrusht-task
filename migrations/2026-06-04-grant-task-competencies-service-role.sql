-- migrations/2026-06-04-grant-task-competencies-service-role.sql
-- Same class of fix as 2026-06-04-grant-tasks-service-role.sql.
--
-- The legacy task_competencies junction table was never granted to service_role
-- on dev, so the pipeline's task<->competency link insert fails with
-- "permission denied for table task_competencies" (SQLSTATE 42501) — surfaced by
-- the first successful end-to-end agent-task run (task c501b9f2...). The link is
-- skipped (non-fatal) but the normalized relationship is lost.
--
-- Prod already has the grant (service_role = arwdDxt on public.task_competencies);
-- this only brings DEV in line with prod. Dev-only.
--
-- Applied to dev via the Supabase MCP apply_migration.

GRANT ALL ON TABLE public.task_competencies TO service_role;
