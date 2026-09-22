"""
Task-shape classifier — decides INFRA vs NON-INFRA for a prompt-generation run.

This is the FIRST real decision step of ``PromptGeneratorAgent``. It reads the
authoritative competency scope text plus the per-combo skill signal
(role_context + sub-skill checklist + scenarios) and asks an LLM to classify
the prompt that is about to be generated as one of:

  * ``"infra"``      — the assessed task needs an external service to be
                       meaningful: a relational/document/key-value DB, a cache,
                       a message queue/broker, a search engine, or any
                       container-orchestrated runtime. The generated prompt
                       must include ``docker-compose.yml``, ``run.sh``, and
                       (where relevant) ``init_database.sql``. No ``kill.sh``
                       is needed — E2B sandboxes are destroyed as a whole.
  * ``"non_infra"``  — the task is pure-runtime / language-level / in-process /
                       algorithmic / UI / frontend work that runs locally
                       without external services. The generated prompt must
                       NOT include docker-compose, init_database.sql, or any
                       other E2B-infra plumbing; ship a pure local project
                       using the runtime's native manifest + test command instead.

Why this lives here (and not in ``infra/classifier/``):
  The existing ``infra/classifier`` package decides ``template_id`` and
  ``persona`` for the E2B deploy flow — it operates on the AVAILABLE-template
  set and emits a heavy ``TaskTemplateMatch``. This classifier is the LIGHT
  prompt-time decision: do we need infra at all? It does not touch templates,
  personas, or datastores, so it stays alongside the rest of the prompt-gen
  pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import dspy

logger = logging.getLogger("prompt_generator")


VALID_SHAPES = ("infra", "non_infra")


@dataclass
class ShapeDecision:
    """Outcome of the shape classifier call."""

    task_shape: str           # "infra" | "non_infra"
    reason: str               # short LLM-emitted justification
    raw_response: str = ""    # raw LLM output for debugging / audit


class ClassifyTaskShapeSignature(dspy.Signature):
    """Decide whether the prompt to be generated should produce an INFRA-shaped
    task or a NON_INFRA task, based on the competency scope and the scenarios
    selected for this combo.

    OUTPUT VALUES — return exactly one of:

      • ``"infra"``     The task involves ANY external service, database, cache,
                        message broker, search engine, or container-orchestrated
                        runtime that the candidate's code must connect to.
                        Pattern examples: "PostgreSQL query optimisation",
                        "Kafka consumer hardening", "Redis cache invalidation",
                        "Mongo aggregation pipeline", "EF Core + SQL Server",
                        "shipment scan API backed by a DB", any scenario where
                        the fix/feature touches real persistence or messaging.
                        AGENT example: agent/RAG that needs a self-hosted
                        vector DB (pgvector, Qdrant, Weaviate, Milvus) or a
                        tool/MCP server it must boot and call.

      • ``"non_infra"`` The task is pure-runtime / language-level / in-process /
                        algorithmic / UI / frontend work that runs entirely
                        locally without any external service.
                        Pattern examples: "React hook composition", "TypeScript
                        type design", "Java concurrency primitives", "Node.js
                        stream backpressure", "algorithm + data structure".
                        AGENT example: an in-process AI agent (tool dispatch,
                        multi-agent orchestration, context assembly, prompt/eval
                        harness) that calls an LLM over an API key only —
                        the LLM is a remote API, NOT a container to boot.

    ═══════════════════════════════════════════════════════════════════
    DECISION RULES  (apply in strict priority order — stop at first match)
    ═══════════════════════════════════════════════════════════════════

      0. ``user_directive`` override — HIGHEST PRIORITY.
         If non-empty it is an authoritative human instruction and OUTRANKS
         every rule below. Apply it literally:
           • Mentions deployment / containerisation / docker-compose /
             external service / datastore → ``infra``.
           • Explicitly asks for a pure local / in-process / no-container
             task → ``non_infra``.
         Only fall through to rules 1–5 when the directive is empty or
         silent on task shape.

      1. ANY external data-store or service mentioned → ALWAYS ``infra``.
         This rule is NON-NEGOTIABLE. Ask yourself: "Would the candidate's
         code FAIL or be meaningless if a particular service were not
         running?" If the answer is YES for any service in the scenario or
         scope, classify as ``infra`` immediately — do not proceed to other
         rules.

         Services that trigger this rule:
           • Relational databases — PostgreSQL, MySQL, MariaDB, MSSQL,
             SQL Server, Oracle, CockroachDB, Citus, SQLite when used
             via a server (not in-memory/embedded).
           • Document / key-value / cache stores — MongoDB, Redis,
             Memcached, DynamoDB, Cassandra, Couchbase, Valkey.
           • Search engines — Elasticsearch, OpenSearch, Solr, Typesense.
           • Time-series / analytics — InfluxDB, TimescaleDB, ClickHouse.
           • Vector databases — pgvector, Qdrant, Weaviate, Milvus,
             ChromaDB, Pinecone, FAISS (self-hosted).
           • Message queues / event brokers — Kafka, RabbitMQ, ActiveMQ,
             NATS, SQS, SNS, Azure Service Bus, Google Pub/Sub, Celery
             (with broker), BullMQ, Sidekiq.
           • Any other long-running process the candidate code connects to
             (session store, blob-storage emulator, SMTP server, etc.).

         Also classify as ``infra`` when the scenario involves:
           • Docker, docker-compose, Kubernetes, Helm, Dockerfile.
           • Connection strings, DATABASE_URL, REDIS_URL, DB_HOST, or any
             service URI the application reads at runtime.
           • "spin up / boot / start the database / service / broker".
           • EF Core (or any ORM) accessing a real DB — even if tests
             might use an in-memory fallback, the production context
             requires a live DB, so the task is infra-shaped.

      2. LLM-as-API is NOT infra.
         Calling an LLM (OpenAI, Anthropic, Gemini, Bedrock, Vertex AI)
         over an API key is NOT a container to boot and does NOT make a
         task infra. An agent/RAG task is ``infra`` ONLY when it ALSO
         needs a self-hosted datastore / vector-DB / tool server / broker
         as the system under test; otherwise it is ``non_infra``.

      3. Pure language / framework / UI / algorithmic work → ``non_infra``.
         If the competency scope is centred on browser/UI/component/hook/
         state patterns, framework-internal APIs (React, Next.js, Vue,
         Svelte), pure language features (concurrency primitives, typing,
         streams, algorithms) or in-process data structures — AND no
         external service from rule 1 is present — choose ``non_infra``.

      4. When genuinely uncertain — lean toward ``infra``.
         An unnecessary docker-compose file is a minor inconvenience.
         A ``non_infra`` task that actually needs a live database will
         fail completely for the candidate. Only choose ``non_infra`` when
         you are CONFIDENT no external service is needed.

    Output a SHORT, specific ``reason`` (≤ 240 chars) that cites the
    strongest piece of evidence — the exact phrase in scope or scenario
    that drove the decision. Do not restate the decision rules.
    """

    competencies: str = dspy.InputField(
        desc="Comma-separated competency names with proficiency, e.g. "
             "'React (ADVANCED)' or 'PostgreSQL (INTERMEDIATE), Python (INTERMEDIATE)'."
    )
    user_directive: str = dspy.InputField(
        desc="AUTHORITATIVE free-text user instruction for this run, or empty. When "
             "non-empty it OUTRANKS the scope/scenario heuristics for the shape "
             "decision: if it asks for deployment / containers / docker-compose / an "
             "external service, return 'infra'; if it asks for a pure local task, "
             "return 'non_infra'. Empty → decide from scope + scenarios as usual."
    )
    competency_scopes: str = dspy.InputField(
        desc="Authoritative scope text per competency from Supabase — the in/out-of-scope "
             "guardrails for this proficiency level."
    )
    detailed_skill_signal: str = dspy.InputField(
        desc="Bundled signal from input files: sub-skill checklist (questions_prompt), "
             "candidate role_context, and up to 3 example scenarios. MAY BE EMPTY for "
             "brand-new combos — when empty, decide from competency_scopes alone."
    )
    task_shape: str = dspy.OutputField(
        desc='Exactly one of "infra" or "non_infra" (lowercase, no quotes).'
    )
    reason: str = dspy.OutputField(
        desc="≤ 240 char justification citing the strongest signal from scope or scenario."
    )


def classify_task_shape(
    competencies_str: str,
    competency_scopes: str,
    detailed_skill_signal: str,
    user_directive: str = "",
) -> ShapeDecision:
    """Run the shape classifier and return a normalized :class:`ShapeDecision`.

    Defensive on the LLM output: anything other than the two valid values
    falls back to ``non_infra``. Rationale: ``non_infra`` is the
    lower-blast-radius default — it produces a local project that the
    candidate can still run; an incorrect ``infra`` output would ship broken
    docker-compose plumbing that fails the E2B gate downstream.
    """
    classifier = dspy.ChainOfThought(ClassifyTaskShapeSignature)
    result = classifier(
        competencies=competencies_str,
        user_directive=user_directive or "",
        competency_scopes=competency_scopes,
        detailed_skill_signal=detailed_skill_signal,
    )

    raw_shape = (getattr(result, "task_shape", "") or "").strip().lower()
    reason = (getattr(result, "reason", "") or "").strip()

    if raw_shape in VALID_SHAPES:
        shape = raw_shape
    else:
        logger.warning(
            "shape_classifier returned unrecognized value %r — defaulting to non_infra",
            raw_shape,
        )
        shape = "non_infra"
        prefix = f"[default after invalid output {raw_shape!r}] "
        reason = prefix + reason if reason else prefix.rstrip()

    # First-class decision log (prompt stage): WHAT it decided, WHAT it weighed,
    # and HOW it reasoned — so the call that drives the E2B-gate skip is fully
    # explainable from the logs + trace_ui (it's the first step of the Prompt
    # stage, not a separate stage).
    logger.info(
        "shape_classifier: task_shape=%s — %s", shape, reason or "(no reason given)"
    )
    logger.info(
        "shape_classifier: decided from competencies=%r (scopes=%dc, signal=%dc, directive=%dc)",
        competencies_str,
        len(competency_scopes or ""),
        len(detailed_skill_signal or ""),
        len(user_directive or ""),
    )
    cot = (getattr(result, "reasoning", "") or "").strip()
    if cot:
        logger.info("shape_classifier: reasoning — %s", cot[:600])
    return ShapeDecision(task_shape=shape, reason=reason, raw_response=raw_shape)
