-- migrations/2026-05-28-disable-rls-on-new-tables.sql
-- Phase 1 of docs/plans/2026-05-27-unified-classifier-template-schema.md
--
-- Supabase enables RLS by default on tables created via the SQL editor.
-- The `templates` and `task_template_match` tables therefore have RLS on
-- but no policies — every read returns 0 rows for the API roles (anon /
-- authenticated / service_role), and every write fails with
-- "new row violates row-level security policy".
--
-- The existing template_registry + competency_combo_classification
-- tables don't have RLS enabled (created earlier, before the default
-- changed). Mirror that policy for the new tables.
--
-- Apply via the Supabase SQL editor on dev first, then prod.

ALTER TABLE templates           DISABLE ROW LEVEL SECURITY;
ALTER TABLE task_template_match DISABLE ROW LEVEL SECURITY;

-- Re-apply grants in case the prior migration ran but the GRANT was
-- shadowed by RLS visibility. Idempotent.
GRANT SELECT, INSERT, UPDATE, DELETE ON templates           TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON task_template_match TO anon, authenticated, service_role;

-- Sanity: after this migration the anon role should see the seeded
-- utkrusht-python row and the backfilled task_template_match rows.
-- Verify with:
--   SELECT count(*) FROM templates;            -- expect >= 1
--   SELECT count(*) FROM task_template_match;  -- expect = count of
--     competency_combo_classification at backfill time (~50 in dev)
