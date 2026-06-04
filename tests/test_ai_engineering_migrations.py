"""Test the AI-engineering migration SQL — well-formed + right shape.

The migrations live as raw SQL (applied manually to Supabase). These
tests pin:

* the 4 AI competency rows have the load-bearing ``scope`` field (so
  the classifier's leanest-superset rule can route them);
* the 4 names are topic-style (matches the repo's convention; per
  ``docs/plans/2026-05-27-ai-engineering-task-category.html`` §"Compe-
  tency naming");
* the ``python-ai-agent`` capability sheet lists the agent frameworks
  (so the LLM classifier considers it for AI-engineering combos);
* the templates row's manifest_hash matches what's on disk (so the
  CI drift gate doesn't false-positive after the migration lands).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


MIGRATIONS = Path("migrations")


def _read(name: str) -> str:
    return (MIGRATIONS / name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Migration files exist
# ---------------------------------------------------------------------------


def test_migrations_dir_exists() -> None:
    assert MIGRATIONS.is_dir(), "migrations/ dir should exist for the new SQL files"


@pytest.mark.parametrize("filename", [
    "2026-06-03-insert-python-base.sql",
    "2026-06-03-insert-python-ai-agent.sql",
    "2026-06-03-insert-ai-engineering-competencies.sql",
    "2026-06-03-bump-registry-version.sql",
])
def test_migration_files_present(filename: str) -> None:
    assert (MIGRATIONS / filename).is_file(), f"{filename} should exist"


# ---------------------------------------------------------------------------
# The python-ai-agent row lists the load-bearing frameworks
# ---------------------------------------------------------------------------


def test_ai_agent_template_migration_lists_agent_frameworks() -> None:
    """The migration's JSON for ``python-ai-agent`` must include the
    frameworks the LLM classifier reads to route AI-engineering
    competencies to it. Without these, the leanest-superset rule
    can't pick the template.
    """
    sql = _read("2026-06-03-insert-python-ai-agent.sql")
    for framework in (
        "langgraph", "pydantic-ai", "crewai", "mem0",
        "litellm", "langfuse", "openinference-instrumentation",
        "anthropic", "openai",
    ):
        assert f"'{framework}'" in sql, (
            f"python-ai-agent capability sheet must list {framework!r} so "
            f"the classifier's leanest-superset rule can route AI "
            f"competencies to it"
        )


def test_ai_agent_template_migration_persona_includes_agent_engineer() -> None:
    """The AI-agent member must declare the ``agent_engineer`` persona
    so the classifier routes AI-engineering competencies with the
    right reviewer specialty."""
    sql = _read("2026-06-03-insert-python-ai-agent.sql")
    assert "'agent_engineer'" in sql


def test_ai_agent_template_migration_uses_actual_manifest_hash() -> None:
    """The manifest_hash in the migration must match the on-disk file
    — otherwise the CI drift gate false-positives on a fresh clone
    that has the migration applied but the wrong hash."""
    sql = _read("2026-06-03-insert-python-ai-agent.sql")
    on_disk = Path(
        "infra/e2b/templates/python-ai-agent/manifest_hash"
    ).read_text().strip()
    assert on_disk in sql, (
        f"manifest_hash {on_disk!r} from infra/e2b/templates/python-ai-agent/"
        f"manifest_hash must appear in the migration SQL"
    )


def test_python_base_template_migration_uses_actual_manifest_hash() -> None:
    sql = _read("2026-06-03-insert-python-base.sql")
    on_disk = Path(
        "infra/e2b/templates/python-base/manifest_hash"
    ).read_text().strip()
    assert on_disk in sql


def test_ai_agent_migration_is_upsert_safe() -> None:
    """Re-running the migration must be a no-op (``ON CONFLICT DO UPDATE``).
    Idempotent migrations are critical for the dev loop — a contributor
    applying the same file twice (e.g. across envs) should not error.
    """
    sql = _read("2026-06-03-insert-python-ai-agent.sql")
    assert "ON CONFLICT (template_id) DO UPDATE" in sql


# ---------------------------------------------------------------------------
# The 4 AI competencies — names, scopes, and the load-bearing signal
# ---------------------------------------------------------------------------


EXPECTED_COMPETENCIES = (
    "Production Agent Engineering",
    "Multi-Agent Systems",
    "Context Engineering",
    "Tool Use for Agents",
)


def test_competency_migration_has_four_rows() -> None:
    """The doc commits to 4 core task-surfaces in v1; multi-modal and
    AI evaluation are carried as tasks under Production Agent Engineering.
    """
    sql = _read("2026-06-03-insert-ai-engineering-competencies.sql")
    for name in EXPECTED_COMPETENCIES:
        assert f"'{name}'" in sql, f"{name!r} must be inserted by the migration"


def test_competency_migration_names_are_topic_style() -> None:
    """Topic-style names match the repo's convention (e.g. ``Vector
    Databases``, ``Microservices``). The doc calls this out as a
    deliberate decision — these are skill-areas, not technologies.
    """
    sql = _read("2026-06-03-insert-ai-engineering-competencies.sql")
    # The competency names should NOT include "Python" — they're
    # skill-areas, not technologies (per the doc's topic-style
    # naming decision).
    assert "Python" not in sql, (
        "competency names should be topic-style, not framework-specific "
        "(per docs/plans/2026-05-27-ai-engineering-task-category.html)"
    )


def test_competency_migration_scopes_name_frameworks() -> None:
    """Each competency's scope MUST name its primary framework — the
    load-bearing signal the classifier's leanest-superset rule reads.
    Without it, an abstract name like 'Production Agent Engineering'
    routes to ``python-web`` (which lists web frameworks only).
    """
    sql = _read("2026-06-03-insert-ai-engineering-competencies.sql")
    expected_frameworks = {
        "Production Agent Engineering": "LangGraph",
        "Multi-Agent Systems": "CrewAI",
        "Context Engineering": "LiteLLM",
        "Tool Use for Agents": "Anthropic",
    }
    for name, framework in expected_frameworks.items():
        # Locate the row for this competency, then assert the scope
        # text mentions the primary framework. Each row is a multi-
        # line VALUES tuple; we slice out the scope text by finding
        # the next single quote after the competency name + 'ADVANCED'.
        pattern = re.compile(
            rf"'{re.escape(name)}',\s*'ADVANCED',\s*'([^']{{50,}})'",
            re.DOTALL,
        )
        match = pattern.search(sql)
        assert match, f"could not parse scope for {name!r} from migration"
        scope = match.group(1)
        assert framework.lower() in scope.lower(), (
            f"{name!r} scope must name primary framework "
            f"{framework!r} so the classifier can route it to "
            f"python-ai-agent (the leanest superset). Got scope: "
            f"{scope[:200]!r}…"
        )


def test_competency_migration_deterministic_ids() -> None:
    """Competency UUIDs must be deterministic — referenced from the
    data/generated/input_files/ JSON sets so the same competency_id
    is used across envs and the migration is idempotent.
    """
    sql = _read("2026-06-03-insert-ai-engineering-competencies.sql")
    # All 4 should have a UUID-shaped value in the right column.
    for uuid in (
        "a1a1a1a1-1111-4111-8111-aaaaaaaaaaaa",
        "a2a2a2a2-2222-4222-8222-aaaaaaaaaaaa",
        "a3a3a3a3-3333-4333-8333-aaaaaaaaaaaa",
        "a4a4a4a4-4444-4444-8444-aaaaaaaaaaaa",
    ):
        assert uuid in sql, f"deterministic UUID {uuid!r} should be in the migration"


def test_competency_migration_upsert_safe() -> None:
    sql = _read("2026-06-03-insert-ai-engineering-competencies.sql")
    assert "ON CONFLICT (competency_id) DO UPDATE" in sql
