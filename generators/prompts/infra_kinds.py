"""Infra-kind registry — the self-hosted services an INFRA task can be grounded in.

Single source of truth for "force infra" mode (docs/plans/2026-06-16-...). A slug
maps to a UI label, the docker service the generated prompt should boot, and the
scenario-steering ``directive`` fed to the scenario generator so the scenarios
genuinely require that service (not a mock).

When forcing infra for an agent competency the classifier would otherwise call
``non_infra``, two coordinated levers run: (1) steer the scenarios via
``directive`` and (2) force ``task_shape=infra`` — so the result is a real infra
task, not docker-compose bolted onto a mockable one.
"""
from __future__ import annotations

INFRA_KINDS: dict[str, dict] = {
    "auto": {
        "label": "Auto — generator picks a fitting service",
        "service": None,
        "directive": (
            "Ground every scenario in a self-hosted datastore / vector-DB / cache / "
            "queue / tool-or-MCP server that the system must boot and use as the "
            "system under test — pick whatever best fits the competency."
        ),
    },
    "vector-db": {
        "label": "Vector DB (pgvector / Qdrant / Weaviate)",
        "service": "qdrant",
        "directive": (
            "Ground every scenario in a self-hosted vector store the system ingests "
            "into and queries (retrieval / RAG); the vector store is the system "
            "under test, never a mock."
        ),
    },
    "redis": {
        "label": "Redis (cache / idempotency / memory)",
        "service": "redis",
        "directive": (
            "Ground every scenario in a self-hosted Redis used for caching, "
            "idempotency keys, rate limiting or agent memory; Redis is the system "
            "under test."
        ),
    },
    "kafka": {
        "label": "Kafka (event-driven / streaming)",
        "service": "kafka",
        "directive": (
            "Ground every scenario in a self-hosted Kafka the system produces to and "
            "consumes from; the broker is the system under test."
        ),
    },
    "postgres": {
        "label": "PostgreSQL (relational datastore)",
        "service": "postgres",
        "directive": (
            "Ground every scenario in a self-hosted PostgreSQL the system reads and "
            "writes as the system under test (schema, queries, transactions)."
        ),
    },
    "mcp-server": {
        "label": "MCP / tool server (boot + call)",
        "service": "mcp",
        "directive": (
            "Ground every scenario in a self-hosted tool / MCP server the system must "
            "boot and call over the network; that server is the system under test."
        ),
    },
}

DEFAULT_INFRA_KIND = "auto"


def is_valid(slug: str | None) -> bool:
    """True if ``slug`` is a known infra kind."""
    return (slug or "").strip().lower() in INFRA_KINDS


def list_kinds() -> list[dict]:
    """``[{slug, label}]`` for the UI dropdown, in registry order."""
    return [{"slug": k, "label": v["label"]} for k, v in INFRA_KINDS.items()]


def resolve(slug: str | None) -> dict:
    """Registry entry for ``slug`` (``{slug, label, service, directive}``),
    falling back to ``auto`` for unknown / empty values."""
    key = (slug or "").strip().lower()
    if key not in INFRA_KINDS:
        key = DEFAULT_INFRA_KIND
    return {"slug": key, **INFRA_KINDS[key]}
