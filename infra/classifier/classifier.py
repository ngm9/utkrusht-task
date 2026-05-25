"""Public classifier entry point — thin wrapper around the LLM classifier.

The classifier returns a ``TaskRuntime`` for the supplied competencies via a
single LLM call. There is no separate cache table — persistence happens at the
caller's layer (typically: write the result onto ``tasks.task_runtime`` when
the task row is created or backfilled).

Callers that want the confidence score for human-review queues can call
``classify_with_llm`` from ``prompt_generator.llm_classifier`` directly; this
wrapper drops it for the common case where only the runtime is needed.
"""
from __future__ import annotations

import openai

from infra.classifier.llm_classifier import classify_with_llm
from infra.classifier.runtime import Competency, TaskRuntime


def classify_task_runtime(
    competencies: list[Competency],
    *,
    llm_client: openai.OpenAI | None = None,
) -> TaskRuntime:
    """Classify these competencies via the LLM and return the TaskRuntime.

    Raises ``ValueError`` if the LLM produces invalid JSON after one retry.
    """
    if not competencies:
        raise ValueError("classify_task_runtime requires at least one competency")
    return classify_with_llm(competencies, client=llm_client).runtime


def to_competencies(items: list[dict]) -> list[Competency]:
    """Convert raw dicts (from competency JSON files) to Competency objects."""
    return [
        Competency(name=item["name"], proficiency=item.get("proficiency", "BASIC"))
        for item in items
    ]
