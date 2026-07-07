"""require_infra_template — hard-stop task generation when an infra-shaped task
has no runtime template (the RabbitMQ case: classified infra, no template, gate
silently skipped, task shipped anyway)."""
from __future__ import annotations

import pytest

from generators.task.runtime_resolver import (
    InfraTemplateMissingError,
    ResolvedPlan,
    require_infra_template,
)
from infra.classifier.runtime import TaskTemplateMatch


def _plan(template=None, match=None, combo="RabbitMQ (INTERMEDIATE)") -> ResolvedPlan:
    return ResolvedPlan(combo_key=combo, match=match, template=template)


def test_infra_without_template_raises_with_detail():
    m = TaskTemplateMatch(template_id=None, no_match_reason="no broker template",
                          suggested_template="rabbitmq-base")
    with pytest.raises(InfraTemplateMissingError) as ei:
        require_infra_template(_plan(match=m), "infra")
    msg = str(ei.value)
    assert "RabbitMQ" in msg            # combo surfaced
    assert "no broker template" in msg  # reason surfaced
    assert "rabbitmq-base" in msg       # suggestion surfaced


def test_infra_check_is_case_insensitive():
    with pytest.raises(InfraTemplateMissingError):
        require_infra_template(_plan(), "INFRA")


def test_infra_with_template_is_allowed():
    # any non-None template means the gate can boot it → no abort
    require_infra_template(_plan(template=object()), "infra")


def test_non_infra_without_template_is_allowed():
    # pure-local tasks legitimately have no template
    require_infra_template(_plan(), "non_infra")


def test_blank_or_missing_shape_is_allowed():
    require_infra_template(_plan(), "")
    require_infra_template(_plan(), None)


def test_infra_with_no_match_at_all_raises():
    # classifier returned nothing (match=None) but the task is infra → still abort
    with pytest.raises(InfraTemplateMissingError):
        require_infra_template(_plan(match=None), "infra")


def test_plan_none_infra_raises():
    with pytest.raises(InfraTemplateMissingError):
        require_infra_template(None, "infra")


def test_default_reason_when_match_has_none():
    m = TaskTemplateMatch(template_id=None)  # no_match_reason unset
    with pytest.raises(InfraTemplateMissingError) as ei:
        require_infra_template(_plan(match=m), "infra")
    assert "no built runtime template" in str(ei.value)
