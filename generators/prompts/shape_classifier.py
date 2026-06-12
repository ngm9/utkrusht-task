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
                       must include ``docker-compose.yml``, ``run.sh``,
                       ``kill.sh``, and (where relevant) ``init_database.sql``.
  * ``"non_infra"``  — the task is pure-runtime / language-level / in-process /
                       algorithmic / UI / frontend work that runs locally
                       without external services. The generated prompt must
                       NOT include docker-compose, init_database.sql, kill.sh,
                       or any other E2B-infra plumbing; ship a pure local
                       project using the runtime's native manifest + test
                       command instead.

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

      • ``"infra"``     The task NEEDS an external service to be meaningful:
                        a relational/document/key-value DB (PostgreSQL, MySQL,
                        MongoDB, Redis), a message queue or broker (Kafka,
                        RabbitMQ, SQS), a search engine (Elastic, OpenSearch),
                        or any other long-running container-orchestrated
                        service. Pattern examples: "PostgreSQL query
                        optimization", "Kafka consumer hardening", "Redis
                        cache invalidation", "Mongo aggregation pipeline".

      • ``"non_infra"`` The task is pure-runtime / language-level / in-process
                        / algorithmic / UI / frontend work that runs locally
                        without any external service. Pattern examples: "React
                        hook composition", "Next.js Server Component
                        conversion", "TypeScript type design", "Java
                        concurrency primitives", "Node.js stream backpressure",
                        "algorithm + data structure".

    Decision rules (in priority order):

      1. If the SCENARIO text explicitly requires connecting to a DB / cache /
         queue / external broker (mentions a service hostname, a docker
         compose file, an ``init_*.sql``, a connection URI, or names a
         datastore as the system under test) → ``infra``.

      2. If the competency_scope is centred on browser/UI/component/hook/state
         patterns, framework-internal APIs (React, Next.js, Vue, Svelte),
         pure language features (Java concurrency, Python typing, Node
         streams) or in-process algorithms → ``non_infra``.

      3. When in doubt — the scenario is observable via in-process tests,
         has no docker-compose or service hostname, and the scope is
         language-/framework-centric — choose ``non_infra``. The downstream
         non-infra path is the safer default: an incorrectly-classified
         "infra" task ships unusable docker-compose plumbing, while an
         incorrectly-classified "non_infra" task is just a local project.

    Output a SHORT, specific ``reason`` (≤ 240 chars) that cites the strongest
    piece of evidence — the exact phrase in scope or scenario that drove the
    decision. Do not restate the decision rules.
    """

    competencies: str = dspy.InputField(
        desc="Comma-separated competency names with proficiency, e.g. "
             "'React (ADVANCED)' or 'PostgreSQL (INTERMEDIATE), Python (INTERMEDIATE)'."
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

    return ShapeDecision(task_shape=shape, reason=reason, raw_response=raw_shape)
