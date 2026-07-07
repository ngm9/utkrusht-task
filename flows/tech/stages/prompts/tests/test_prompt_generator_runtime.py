"""Unified-schema runtime models — TaskTemplateMatch / TaskIntent / DatastoreRef.

Validates field defaults, enum constraints, JSON round-trip, and immutability.
"""
import pytest
from pydantic import ValidationError

from infra.classifier.runtime import (
    Competency,
    DatastoreRef,
    TaskIntent,
    TaskTemplateMatch,
)


def test_competency_lower():
    c = Competency(name="Python", proficiency="BASIC")
    assert c.name_lower == "python"
    assert c.proficiency == "BASIC"


# ── DatastoreRef ─────────────────────────────────────────────────────


def test_datastore_ref_minimum_fields():
    d = DatastoreRef(name="postgres", role="primary")
    assert d.name == "postgres"
    assert d.role == "primary"


def test_datastore_ref_invalid_role_rejected():
    with pytest.raises(ValidationError):
        DatastoreRef(name="postgres", role="leader")  # not in Role Literal


def test_datastore_ref_is_immutable():
    d = DatastoreRef(name="postgres", role="primary")
    with pytest.raises(ValidationError):
        d.name = "mysql"


# ── TaskIntent ───────────────────────────────────────────────────────


def test_task_intent_defaults():
    ti = TaskIntent()
    assert ti.datastores == []
    assert ti.protocols_used == []
    assert ti.eval_method == "test_suite"
    assert ti.secondary_runtimes == []
    assert ti.persona_override is None


def test_task_intent_full():
    ti = TaskIntent(
        datastores=[
            DatastoreRef(name="postgres", role="primary"),
            DatastoreRef(name="redis", role="cache"),
        ],
        protocols_used=["rest", "grpc"],
        eval_method="validator",
        secondary_runtimes=["node"],
        persona_override="data",
    )
    assert len(ti.datastores) == 2
    assert ti.protocols_used == ["rest", "grpc"]
    assert ti.eval_method == "validator"
    assert ti.persona_override == "data"


def test_task_intent_invalid_protocol_rejected():
    with pytest.raises(ValidationError):
        TaskIntent(protocols_used=["amqp"])  # not in Protocol Literal


def test_task_intent_invalid_eval_method_rejected():
    with pytest.raises(ValidationError):
        TaskIntent(eval_method="manual_review")


def test_task_intent_json_round_trip():
    original = TaskIntent(
        datastores=[DatastoreRef(name="postgres", role="primary")],
        protocols_used=["rest"],
    )
    serialised = original.model_dump()
    rebuilt = TaskIntent.model_validate(serialised)
    assert rebuilt == original


# ── TaskTemplateMatch ────────────────────────────────────────────────


def test_task_template_match_defaults():
    m = TaskTemplateMatch()
    assert m.template_id is None
    assert m.persona is None
    assert m.confidence == 0.0
    assert m.no_match_reason is None
    assert m.missing_capabilities == []
    assert m.suggested_template is None


def test_task_template_match_full():
    m = TaskTemplateMatch(
        template_id="utkrusht-python",
        persona="backend",
        confidence=0.95,
    )
    assert m.template_id == "utkrusht-python"
    assert m.persona == "backend"
    assert m.confidence == 0.95


def test_task_template_match_no_match():
    m = TaskTemplateMatch(
        no_match_reason="needs helm + terraform",
        missing_capabilities=["helm", "terraform"],
        suggested_template="utkrusht-infra",
        confidence=0.8,
    )
    assert m.template_id is None
    assert m.no_match_reason == "needs helm + terraform"
    assert m.missing_capabilities == ["helm", "terraform"]


def test_task_template_match_json_round_trip():
    original = TaskTemplateMatch(
        template_id="utkrusht-python", persona="mle", confidence=0.91,
    )
    serialised = original.model_dump()
    rebuilt = TaskTemplateMatch.model_validate(serialised)
    assert rebuilt == original


def test_task_template_match_is_immutable():
    m = TaskTemplateMatch(template_id="utkrusht-python", persona="backend")
    with pytest.raises(ValidationError):
        m.persona = "data"
