-- Migration: bump the templates.registry_version to re-classify caches
--
-- After the python-base and python-ai-agent template rows land, the
-- existing task_template_match cache rows point at registry_version=1
-- (or whatever was the current value when they were classified). Bump
-- the registry_version on the existing utkrusht-python row so the
-- resolve_plan() freshness check re-classifies every cached combo,
-- and the LLM classifier sees the new python-ai-agent template as a
-- candidate for the AI-engineering competencies.
--
-- Per docs/task-classifier/classifier.md §"Cache invalidation has two
-- keys" — a registry_version bump invalidates the cache cleanly.

UPDATE templates
SET
    registry_version = registry_version + 1,
    manifest_generated_at = NOW()
WHERE template_id IN (
    'utkrusht-python',
    'utkrusht-python-base',
    'utkrusht-python-ai-agent'
);

-- Note: the cached task_template_match rows survive this update (they
-- store their OWN registry_version snapshot at classify time). On the
-- next resolve_plan() call, _is_match_fresh() compares cached_version
-- against the template's current registry_version and returns False
-- (stale) when they differ — triggering re-classification. This is
-- the cache-invalidation contract the classifier guarantees.
