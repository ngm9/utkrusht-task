-- Migration: register the python-base template
--
-- The lean Python substrate every member of the Python template family
-- inherits from (sibling-FROM approach per
-- docs/plans/2026-05-27-ai-engineering-task-category.html §"The
-- sandbox: the python-ai-agent template"). Carries the apt + Docker +
-- Python + DB client + pytest set; no web frameworks, no LLM
-- ecosystem. Members (python-web, python-ai-agent, ...) layer their
-- own framework sets on top.
--
-- The base is intentionally NOT a routable template — its
-- ``personas`` array is empty and the LLM classifier never picks it
-- for a task. It exists so the family is built on a shared substrate
-- the contributor can patch in one place.

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
    'utkrusht-python-base',
    'built',
    'python',
    ARRAY[]::text[],   -- no personas — base is not a routable template
    ARRAY['test_suite'],
    jsonb_build_object(
        'language_versions', jsonb_build_object('python', '3.12'),
        'frameworks', jsonb_build_array(),  -- base has no frameworks
        'datastores', jsonb_build_array('postgres', 'mysql', 'mongo', 'redis'),
        'protocols', jsonb_build_array('rest'),
        'tools', jsonb_build_array(
            'pytest', 'pytest-asyncio',
            'docker', 'docker-compose',
            'git', 'jq',
            'postgresql-client', 'default-mysql-client',
            'psycopg2-binary', 'pymongo', 'redis',
            'httpx', 'requests',
            'pandas', 'numpy',
            'ttyd', 'code-server', 'adminer'
        ),
        'requires', jsonb_build_object('browser', false, 'gpu', false),
        'tags', jsonb_build_array('python-base', 'family-root')
    ),
    'pip install --break-system-packages -r requirements.txt',
    'python -m pytest -q --tb=short',
    'python -m compileall -q .',
    'apt-get install -y python3 python3-pip',
    'python3 --version',
    15,
    'b94bec11b9ad5b2b701813927921ce02041a3bcd0167c15e97be57178fa6bf07',
    NOW(),
    1,
    'Lean Python 3.12 base — apt + Docker + DB clients + pytest. No web frameworks, no LLM ecosystem. Substrate for the Python template family (python-web, python-ai-agent, ...). Each member layers its own framework set on this base via the shared base_python_template() helper.'
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
