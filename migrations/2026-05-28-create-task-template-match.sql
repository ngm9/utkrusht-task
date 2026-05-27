-- migrations/2026-05-28-create-task-template-match.sql
-- Phase 1 of docs/plans/2026-05-27-unified-classifier-template-schema.md
--
-- Creates `task_template_match` — the LLM's match decision per combo.
-- Replaces `competency_combo_classification` (kept until Phase 4 cutover).
--
-- One row per combo_key. template_id NULL = no_match (first-class signal).
--
-- Depends on: 2026-05-28-create-templates.sql (FK target).
-- Apply via the Supabase SQL editor on dev first, then prod.

CREATE TABLE IF NOT EXISTS task_template_match (
    combo_key             text PRIMARY KEY,

    template_id           text REFERENCES templates(template_id)
                          ON DELETE SET NULL,
    persona               text,
    confidence            real,

    -- no_match path
    no_match_reason       text,
    missing_capabilities  text[],
    suggested_template    text,

    -- Cache invalidation
    classifier_model      text NOT NULL,
    registry_version      integer NOT NULL,
    classified_at         timestamptz NOT NULL DEFAULT now(),

    CHECK (
        (template_id IS NOT NULL AND no_match_reason IS NULL) OR
        (template_id IS NULL     AND no_match_reason IS NOT NULL)
    )
);

-- Backfill from the existing classification cache where possible.
-- Existing competency_combo_classification rows have `runtime` (text) and
-- `template_runtime` (text, FK to template_registry). Map:
--   template_runtime → template_id (1:1 by name, since template_registry
--                     rows match templates rows for builts)
--   `kind` → persona (one of backend/data/mle — closest match)
-- Set persona='backend' as a safe default for any classification that
-- doesn't map cleanly; humans can edit rows post-migration.

INSERT INTO task_template_match (
    combo_key, template_id, persona, confidence,
    classifier_model, registry_version, classified_at
)
SELECT
    c.combo_key,
    -- Only set template_id when there's a matching `built` template.
    -- Rows with no matching built template get NULL + a no_match_reason.
    CASE
        WHEN t.template_id IS NOT NULL THEN t.template_id
        ELSE NULL
    END AS template_id,
    CASE
        WHEN t.template_id IS NOT NULL THEN COALESCE(
            CASE c.kind
                WHEN 'app'       THEN 'backend'
                WHEN 'script'    THEN 'data'
                WHEN 'llm'       THEN 'mle'
                WHEN 'vector_db' THEN 'mle'
                WHEN 'db_only'   THEN 'data'
                ELSE 'backend'
            END,
            'backend'
        )
        ELSE NULL
    END AS persona,
    COALESCE(c.confidence::real, 0.9) AS confidence,
    COALESCE(c.classifier_version, 'backfill-2026-05-28') AS classifier_model,
    1 AS registry_version,
    COALESCE(c.created_at, now()) AS classified_at
FROM competency_combo_classification c
LEFT JOIN templates t
    ON t.template_id = (
        CASE c.template_runtime
            WHEN 'python' THEN 'utkrusht-python'
            ELSE NULL
        END
    )
WHERE NOT EXISTS (
    SELECT 1 FROM task_template_match m WHERE m.combo_key = c.combo_key
);

-- For backfilled rows with no template match, set the no_match reason so
-- the CHECK constraint isn't violated.
UPDATE task_template_match
SET no_match_reason = 'backfill: no built template for original runtime',
    missing_capabilities = ARRAY[]::text[]
WHERE template_id IS NULL
  AND no_match_reason IS NULL;
