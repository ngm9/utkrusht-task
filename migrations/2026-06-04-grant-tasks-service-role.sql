-- migrations/2026-06-04-grant-tasks-service-role.sql
-- Fix for the half-finished migration in commit 07b3d0a.
--
-- 07b3d0a switched generators/task/persistence.py::init_supabase() to PREFER
-- the service_role key (needed for the v1 task-builder tables that carry
-- service_role_all policies). But the legacy public.tasks table was never
-- granted to service_role, so insert_draft_task / mark_task_ready fail on dev
-- with "permission denied for table tasks" — the pipeline can never persist a
-- generated task.
--
-- Prod already has this grant (service_role = arwdDxt on public.tasks); this
-- only brings DEV in line with prod. Dev-only — no prod change needed.
--
-- Applied to dev (ctzweurujanstonppfyh) via the Supabase MCP apply_migration.

GRANT ALL ON TABLE public.tasks TO service_role;
