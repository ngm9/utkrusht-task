-- migrations/2026-05-28-add-task-intent-to-tasks.sql
-- Phase 1 of docs/plans/2026-05-27-unified-classifier-template-schema.md
--
-- Adds task_intent jsonb to the tasks table — captures per-task USE of the
-- matched template's capabilities (datastore roles, protocols used,
-- eval method, polyglot secondaries, optional persona override).
--
-- Backfill default: empty intent. Existing tasks have no recorded intent;
-- consumers fall back to template defaults.
--
-- Apply via the Supabase SQL editor on dev first, then prod.

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS task_intent jsonb NOT NULL DEFAULT '{
        "datastores": [],
        "protocols_used": [],
        "eval_method": "test_suite",
        "secondary_runtimes": [],
        "persona_override": null
    }'::jsonb;

COMMENT ON COLUMN tasks.task_intent IS
    'Per-task use of matched template capabilities. Emitted by the '
    'content-generation LLM (not by the classifier). See '
    'docs/plans/2026-05-27-unified-classifier-template-schema.md '
    '"What task_intent is".';
