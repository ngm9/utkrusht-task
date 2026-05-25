-- migrations/2026-05-25-create-template-registry.sql
-- B6 of docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md
--
-- One source of truth for "what does each runtime need" — the E2B template
-- name plus the build / test / compile recipe. Shared by:
--   • the combo classification cache (FK on template_runtime)
--   • the E2B build/test gate (sandbox_eval)
--   • future deploy
--
-- Apply via the Supabase SQL editor on dev first, then prod.
--
-- ORDER OF APPLICATION: this migration must land BEFORE
-- 2026-05-25-create-competency-combo-classification.sql, because the combo
-- cache has an FK to this table.

CREATE TABLE IF NOT EXISTS template_registry (
    runtime         text PRIMARY KEY,
    template_name   text NOT NULL,
    build_cmd       text NOT NULL,
    test_cmd        text NOT NULL,
    compile_cmd     text,
    needs_browser   boolean NOT NULL DEFAULT false,
    description     text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

-- Seed: python row mirrors the in-memory _TEMPLATES dict at
-- task_generation/runtime_resolver.py so the resolver can swap to a
-- DB-backed lookup without behaviour change.
INSERT INTO template_registry
    (runtime, template_name, build_cmd, test_cmd, compile_cmd, needs_browser, description)
VALUES (
    'python',
    'utkrusht-python',
    'pip install --break-system-packages -r requirements.txt',
    'python -m pytest -q --tb=short',
    'python -m compileall -q .',
    false,
    'Fat base: fastapi, flask, django, sqlalchemy, redis, pymongo, langchain, llama-index, pandas, numpy, pytest.'
)
ON CONFLICT (runtime) DO NOTHING;
