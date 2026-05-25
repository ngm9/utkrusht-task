-- migrations/2026-05-25-create-competency-combo-classification.sql
-- B1 of docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md
--
-- Per-combo classification cache. Each (organization_id, combo_key) is
-- classified by the LLM exactly once; every downstream consumer reads
-- through resolve_plan(), which performs a cache lookup keyed by combo_key.
--
-- Apply via the Supabase SQL editor on dev first, then prod.
--
-- Depends on: 2026-05-25-create-template-registry.sql (FK target).

CREATE TABLE IF NOT EXISTS competency_combo_classification (
    combo_key            text PRIMARY KEY,
    organization_id      uuid NOT NULL,
    runtime              text NOT NULL,
    kind                 text NOT NULL,
    frameworks           text[]  NOT NULL DEFAULT '{}',
    datastores           text[]  NOT NULL DEFAULT '{}',
    messaging            text[]  NOT NULL DEFAULT '{}',
    needs_browser        boolean NOT NULL DEFAULT false,
    template_runtime     text REFERENCES template_registry(runtime),
    classifier_version   text NOT NULL,
    confidence           numeric(3,2),
    created_at           timestamptz NOT NULL DEFAULT now(),
    updated_at           timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, combo_key)
);

CREATE INDEX IF NOT EXISTS idx_combo_classification_org
    ON competency_combo_classification (organization_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_combo_classification_kind
    ON competency_combo_classification (kind);

-- ``confidence`` is intentionally nullable: pre-existing rows backfilled
-- without a score remain valid. New rows from the LLM classifier carry the
-- model's self-reported confidence; rows below 0.7 are surfaced for human
-- review (per task-classifier-and-templates.md §"Safety rails").
