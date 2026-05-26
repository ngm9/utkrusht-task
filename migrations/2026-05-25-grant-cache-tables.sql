-- migrations/2026-05-25-grant-cache-tables.sql
-- Grant API-role access to the B1/B6 tables.
--
-- New tables created in the Supabase SQL editor default to postgres-only
-- ownership. The anon / authenticated / service_role roles (used by the
-- PostgREST API that supabase-py talks to) need explicit GRANTs to read
-- and write the rows.
--
-- Apply via the Supabase SQL editor on dev first, then prod.

GRANT SELECT, INSERT, UPDATE, DELETE
    ON template_registry
    TO anon, authenticated, service_role;

GRANT SELECT, INSERT, UPDATE, DELETE
    ON competency_combo_classification
    TO anon, authenticated, service_role;
