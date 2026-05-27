-- migrations/2026-05-28-grant-new-tables.sql
-- Phase 1 of docs/plans/2026-05-27-unified-classifier-template-schema.md
--
-- Grants the same access policy as 2026-05-25-grant-cache-tables.sql:
-- supabase-py uses anon/authenticated/service_role to read+write.
-- Without this the new tables silently fail every Python call.
--
-- Apply via the Supabase SQL editor on dev first, then prod.

GRANT SELECT, INSERT, UPDATE, DELETE ON templates           TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON task_template_match TO anon, authenticated, service_role;

-- tasks.task_intent inherits the existing tasks-table grants — no change
-- needed (the column is on an already-granted table).
