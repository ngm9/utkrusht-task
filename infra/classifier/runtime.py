"""Structured runtime spec for a generated task.

Three concepts, three places:
  1. Capability sheet  → ``templates`` row (jsonb capabilities; read by LLM)
  2. Match decision    → ``task_template_match`` row (TaskTemplateMatch)
  3. Per-task intent   → ``tasks.task_intent`` column (TaskIntent)

See ``docs/plans/2026-05-27-unified-classifier-template-schema.md`` for
the full architecture.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


#: Role a datastore plays in a specific task. Per-task; not a template prop.
Role = Literal["primary", "replica", "source", "target", "cache"]

#: Wire protocol the task implements. Closed enum — LLM picks subset.
Protocol = Literal["rest", "grpc", "graphql", "websocket", "none"]

#: Which eval runner the gate dispatches for the task. Closed enum.
#: The runtime-specific command (pytest / mvn test / etc.) is read from
#: the matched template's ``test_cmd``; this field selects the *category*
#: of evaluation (test_suite vs notebook vs validator vs ...).
EvalMethod = Literal[
    "test_suite", "notebook", "validator",
    "lint", "benchmark", "compile_only",
]


class DatastoreRef(BaseModel):
    """One datastore the task uses, plus the role it plays in this task.

    The template's ``capabilities.datastores`` lists the MENU (what
    clients/drivers are installed). This carries the per-task SELECTION
    plus the role tag — same DB name can appear twice with different
    roles (e.g. postgres primary + postgres replica).
    """

    model_config = ConfigDict(frozen=True)

    name: str  # "postgres", "mysql", "redis", ...
    role: Role


class TaskIntent(BaseModel):
    """Per-task USE of the matched template's capabilities.

    Lives on ``tasks.task_intent``. Emitted by the content-generation LLM
    (which already sees the scenario), NOT by the classifier — see
    "Why scenario is NOT passed to the classifier" in the plan doc.

    All fields have safe defaults so an empty intent ``{}`` is valid for
    existing tasks backfilled by the schema migration.
    """

    model_config = ConfigDict(frozen=True)

    datastores: list[DatastoreRef] = Field(default_factory=list)
    protocols_used: list[Protocol] = Field(default_factory=list)
    eval_method: EvalMethod = "test_suite"
    secondary_runtimes: list[str] = Field(default_factory=list)
    persona_override: str | None = None


class TaskTemplateMatch(BaseModel):
    """The classifier's match decision for one competency combo.

    Cached per ``combo_key`` in the ``task_template_match`` Supabase table.
    Per-combo, not per-task — same competencies always produce the same
    match (modulo human edits via the override path).

    ``template_id`` is None iff no built template fits — in that case
    ``no_match_reason`` MUST be set (CHECK constraint on the table
    mirrors this; the Pydantic ``model_validator`` enforces the same).
    """

    model_config = ConfigDict(frozen=True)

    template_id: str | None = None
    persona: str | None = None
    confidence: float = 0.0

    # no_match path
    no_match_reason: str | None = None
    missing_capabilities: list[str] = Field(default_factory=list)
    suggested_template: str | None = None


@dataclass(frozen=True)
class Competency:
    """Normalised competency tuple — the classifier's input."""

    name: str
    proficiency: str

    @property
    def name_lower(self) -> str:
        return self.name.lower()
