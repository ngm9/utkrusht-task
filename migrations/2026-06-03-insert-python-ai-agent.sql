-- Migration: register the python-ai-agent template
--
-- This is the AI-engineering member of the Python template family,
-- shipped as part of the AI-engineering task category
-- (docs/plans/2026-05-27-ai-engineering-task-category.html §"The
-- sandbox: the python-ai-agent template"). It carries the ~6 agent
-- frameworks on top of the lean python-base substrate, isolated from
-- the web/DB tasks on python-web.
--
-- Apply order:
--   1. python-base (separate migration: 2026-06-03-insert-python-base.sql)
--   2. python-ai-agent (this file)
--   3. 2026-06-03-bump-registry-version.sql  (re-classifies all caches)
--
-- Pre-reqs: the ``templates`` table exists per the unified-classifier-
-- template-schema migration (2026-05-28-create-templates.sql). The
-- ``python-base`` row exists so this row's "family-member" tag
-- resolves to a real base.

INSERT INTO templates (
    template_id,
    status,
    primary_runtime,
    personas,
    eval_methods,
    capabilities,
    build_cmd,
    test_cmd,
    compile_cmd,
    install_cmd,
    install_verify,
    install_seconds,
    manifest_hash,
    manifest_generated_at,
    registry_version,
    description
) VALUES (
    'utkrusht-python-ai-agent',
    'built',
    'python',
    ARRAY['agent_engineer', 'mle'],
    ARRAY['test_suite'],
    jsonb_build_object(
        'language_versions', jsonb_build_object('python', '3.12'),
        'frameworks', jsonb_build_array(
            'langgraph',
            'pydantic-ai',
            'crewai',
            'mem0',
            'litellm',
            'langfuse',
            'openinference-instrumentation',
            'fastembed',
            'anthropic',
            'openai',
            'google-generativeai'
        ),
        'datastores', jsonb_build_array(
            'postgres', 'mysql', 'mongo', 'redis', 'qdrant'
        ),
        'protocols', jsonb_build_array('rest', 'websocket'),
        'tools', jsonb_build_array(
            'pytest', 'pytest-asyncio',
            'docker', 'docker-compose',
            'git', 'jq',
            'postgresql-client', 'default-mysql-client',
            'psycopg2-binary', 'pymongo', 'redis',
            'httpx', 'requests',
            'pandas', 'numpy',
            'ttyd', 'code-server', 'adminer',
            'litellm', 'tiktoken', 'fastembed', 'langfuse'
        ),
        'requires', jsonb_build_object('browser', false, 'gpu', false),
        'tags', jsonb_build_array(
            'python-ai-agent', 'family-member', 'agent-frameworks'
        )
    ),
    'pip install --break-system-packages -r requirements.txt',
    'python -m pytest -q --tb=short',
    'python -m compileall -q .',
    'apt-get install -y python3 python3-pip',
    'python3 --version',
    15,
    'eb93272e1e61ce661de6952f9214c1c5d20ecc5d1992420f6e418dc94023bf1c',
    NOW(),
    1,
    'AI-agent Python 3.12 runtime. Layers the agent frameworks (langgraph, pydantic-ai, crewai, mem0) on the lean python-base substrate, plus LiteLLM for model routing and tiktoken for context budgeting. Provider SDKs (anthropic, openai, google-generativeai) are pre-installed so the candidate''s agent code can call models directly via the candidate''s own API key. Observability via langfuse + openinference. The gate is LLM-free — no API key sits in this image at generation; the candidate''s session brings their own key in.'
)
ON CONFLICT (template_id) DO UPDATE
SET
    status = EXCLUDED.status,
    primary_runtime = EXCLUDED.primary_runtime,
    personas = EXCLUDED.personas,
    eval_methods = EXCLUDED.eval_methods,
    capabilities = EXCLUDED.capabilities,
    build_cmd = EXCLUDED.build_cmd,
    test_cmd = EXCLUDED.test_cmd,
    compile_cmd = EXCLUDED.compile_cmd,
    install_cmd = EXCLUDED.install_cmd,
    install_verify = EXCLUDED.install_verify,
    install_seconds = EXCLUDED.install_seconds,
    manifest_hash = EXCLUDED.manifest_hash,
    manifest_generated_at = EXCLUDED.manifest_generated_at,
    registry_version = EXCLUDED.registry_version,
    description = EXCLUDED.description;

-- No RLS — the templates table is platform-global (see
-- 2026-05-25-grant-cache-tables.sql pattern for the GRANT).
