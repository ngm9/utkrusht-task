-- migrations/2026-05-28-create-templates.sql
-- Phase 1 of docs/plans/2026-05-27-unified-classifier-template-schema.md
--
-- Creates the new `templates` table (renamed from template_registry).
-- Capability sheets the LLM reads to match tasks to deployable templates.
--
-- ADDITIVE: template_registry stays in place (used by existing code paths).
-- Phase 4 drops template_registry once all consumers cut over to `templates`.
--
-- Apply via the Supabase SQL editor on dev first, then prod.

CREATE TABLE IF NOT EXISTS templates (
    template_id           text PRIMARY KEY,
    status                text NOT NULL
                          CHECK (status IN ('built','proposed','deprecated')),

    -- Typed: closed enums, LLM picks one per task
    primary_runtime       text NOT NULL,
    personas              text[] NOT NULL,
    eval_methods          text[] NOT NULL
                          DEFAULT ARRAY['test_suite'],

    -- Extensible: new dimensions added without migration
    capabilities          jsonb NOT NULL DEFAULT '{}'::jsonb,

    -- Execution recipes
    build_cmd             text NOT NULL,
    test_cmd              text NOT NULL,
    compile_cmd           text,

    -- Polyglot install-at-boot
    install_cmd           text,
    install_verify        text,
    install_seconds       int,

    -- Drift control
    manifest_hash         text NOT NULL,
    manifest_generated_at timestamptz NOT NULL,
    registry_version      integer NOT NULL,

    description           text,
    created_at            timestamptz NOT NULL DEFAULT now(),
    updated_at            timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS templates_active_idx
    ON templates(status) WHERE status = 'built';
CREATE INDEX IF NOT EXISTS templates_primary_runtime_idx
    ON templates(primary_runtime) WHERE status = 'built';

-- Seed: copy from template_registry rows + augment with new columns.
-- The python row is the only `built` template today. Other proposed rows
-- get carried over with sensible defaults; the LLM never picks them
-- because the index filter is WHERE status='built'.
--
-- manifest_hash is the value from infra/e2b/templates/python-sql/manifest_hash
-- (committed in Phase 0). If that file changed since this migration was
-- written, regenerate by reading it at apply-time — but for safety we hard
-- code the known value here. Mismatch will be caught when the runtime
-- resolver reads the row + the on-disk hash and they disagree.

INSERT INTO templates (
    template_id, status, primary_runtime, personas, eval_methods,
    capabilities, build_cmd, test_cmd, compile_cmd,
    install_cmd, install_verify, install_seconds,
    manifest_hash, manifest_generated_at, registry_version,
    description
) VALUES (
    'utkrusht-python',
    'built',
    'python',
    ARRAY['backend','data','mle'],
    ARRAY['test_suite'],
    '{
        "language_versions": {"python": "3.13"},
        "frameworks": ["fastapi","django","flask","sqlalchemy"],
        "datastores": ["postgres","mysql","mongo","redis"],
        "protocols": ["rest","websocket"],
        "tools": ["pytest","docker","docker-compose","git","jq","psycopg2-binary","pandas"],
        "requires": {"browser": false, "gpu": false},
        "tags": []
    }'::jsonb,
    'pip install --break-system-packages -r requirements.txt',
    'python -m pytest -q --tb=short',
    'python -m compileall -q .',
    'apt-get install -y python3 python3-pip',
    'python3 --version',
    15,
    'a27ae796c238a1d30996a81e2a830ac76652fcc9717b163c5c4980570bad03f3',
    now(),
    1,
    'Python 3.13 base. Pre-installed: psycopg2-binary, sqlalchemy, pandas. Browser tools: ttyd, code-server, adminer. DinD via docker-ce.'
)
ON CONFLICT (template_id) DO NOTHING;
