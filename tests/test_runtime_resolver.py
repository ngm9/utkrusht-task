"""Unit tests for task_generation.runtime_resolver — the single entry point
for resolving a competency combo into a plan.

The resolver now sits in front of the ``competency_combo_classification``
Supabase cache (B1). Tests exercise four paths:

  1. Cache hit  — Supabase returns a row → no LLM call.
  2. Cache miss — Supabase returns empty → LLM call → upsert.
  3. No cache   — UTKRUSHT_ORG_ID unset → LLM call, no DB touched.
  4. Failure   — classifier raises → empty plan, no crash.
"""
from unittest.mock import MagicMock, patch

import pytest

from infra.classifier.llm_classifier import ClassifierResult
from infra.classifier.runtime import Competency, TaskRuntime
from generators.task.runtime_resolver import (
    ResolvedPlan,
    make_combo_key,
    resolve_plan,
)


def _comps(*pairs):
    return [Competency(name=n, proficiency=p) for n, p in pairs]


def _fake_result(runtime="python", kind="app", confidence=0.92, **kwargs):
    rt = TaskRuntime(runtime=runtime, kind=kind, **kwargs)
    return ClassifierResult(runtime=rt, confidence=confidence)


def _fake_supabase_hit(row: dict) -> MagicMock:
    """Supabase mock that returns one row on .execute()."""
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = [row]
    return client


def _fake_supabase_miss() -> MagicMock:
    """Supabase mock that returns no rows on .execute()."""
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    return client


# --- make_combo_key (unchanged) --------------------------------------------

def test_combo_key_sorted_and_proficiency_suffixed():
    key = make_combo_key(_comps(("Python", "BASIC"), ("MongoDB", "BASIC")))
    assert key == "MongoDB (BASIC), Python (BASIC)"


def test_combo_key_stable_across_input_order():
    a = make_combo_key(_comps(("Python", "BASIC"), ("Redis", "BASIC")))
    b = make_combo_key(_comps(("Redis", "BASIC"), ("Python", "BASIC")))
    assert a == b


def test_combo_key_single_competency():
    assert make_combo_key(_comps(("Python", "INTERMEDIATE"))) == "Python (INTERMEDIATE)"


# --- No-cache path (UTKRUSHT_ORG_ID unset) ---------------------------------

def test_no_cache_falls_through_to_llm(monkeypatch):
    monkeypatch.delenv("UTKRUSHT_ORG_ID", raising=False)
    with patch("generators.task.runtime_resolver.classify_with_llm",
               return_value=_fake_result("python", "app")):
        plan = resolve_plan(_comps(("Python", "BASIC")))
    assert plan.task_runtime is not None
    assert plan.task_runtime.runtime == "python"
    assert plan.template is not None
    assert plan.template.name == "utkrusht-python"
    assert plan.gate_supported


def test_no_cache_runtime_without_template_marks_gate_unsupported(monkeypatch):
    monkeypatch.delenv("UTKRUSHT_ORG_ID", raising=False)
    with patch("generators.task.runtime_resolver.classify_with_llm",
               return_value=_fake_result("java", "app")):
        plan = resolve_plan(_comps(("Java", "BASIC")))
    assert plan.task_runtime is not None
    assert plan.template is None
    assert not plan.gate_supported


# --- Cache HIT path --------------------------------------------------------

def test_cache_hit_skips_llm(monkeypatch):
    monkeypatch.setenv("UTKRUSHT_ORG_ID", "fake-uuid-1")
    supabase = _fake_supabase_hit({
        "runtime": "python", "kind": "app",
        "frameworks": ["fastapi"], "datastores": ["postgres"],
        "messaging": [], "needs_browser": False,
    })
    with patch("generators.task.runtime_resolver.classify_with_llm") as llm:
        plan = resolve_plan(_comps(("Python", "BASIC")), supabase=supabase)
    assert plan.task_runtime is not None
    assert plan.task_runtime.runtime == "python"
    assert plan.task_runtime.frameworks == ["fastapi"]
    assert plan.task_runtime.datastores == ["postgres"]
    assert plan.template is not None and plan.template.name == "utkrusht-python"
    llm.assert_not_called()


# --- Cache MISS path (writes back) -----------------------------------------

def test_cache_miss_calls_llm_and_upserts(monkeypatch):
    monkeypatch.setenv("UTKRUSHT_ORG_ID", "fake-uuid-2")
    supabase = _fake_supabase_miss()
    with patch("generators.task.runtime_resolver.classify_with_llm",
               return_value=_fake_result("python", "app", confidence=0.91)):
        plan = resolve_plan(_comps(("Python", "BASIC")), supabase=supabase)
    assert plan.task_runtime is not None
    assert plan.task_runtime.runtime == "python"
    # upsert was called on the combo table
    supabase.table.assert_any_call("competency_combo_classification")
    upsert_calls = [c for c in supabase.table.return_value.upsert.call_args_list]
    assert len(upsert_calls) == 1
    payload = upsert_calls[0].args[0]
    assert payload["combo_key"] == "Python (BASIC)"
    assert payload["organization_id"] == "fake-uuid-2"
    assert payload["runtime"] == "python"
    assert payload["template_runtime"] == "python"
    assert payload["confidence"] == 0.91
    assert payload["classifier_version"] == "v1"


def test_cache_miss_unknown_runtime_writes_null_template_runtime(monkeypatch):
    """Runtimes without a template row must NOT set template_runtime (FK)."""
    monkeypatch.setenv("UTKRUSHT_ORG_ID", "fake-uuid-3")
    supabase = _fake_supabase_miss()
    with patch("generators.task.runtime_resolver.classify_with_llm",
               return_value=_fake_result("java", "app")):
        resolve_plan(_comps(("Java", "BASIC")), supabase=supabase)
    payload = supabase.table.return_value.upsert.call_args.args[0]
    assert payload["template_runtime"] is None
    assert payload["runtime"] == "java"


# --- Resilience: classifier failure should not crash -----------------------

def test_classifier_failure_returns_empty_plan(monkeypatch):
    monkeypatch.delenv("UTKRUSHT_ORG_ID", raising=False)
    with patch("generators.task.runtime_resolver.classify_with_llm",
               side_effect=RuntimeError("classifier blew up")):
        plan = resolve_plan(_comps(("Python", "BASIC")))
    assert plan.task_runtime is None
    assert plan.template is None
    assert not plan.gate_supported
    assert plan.combo_key == "Python (BASIC)"


def test_cache_lookup_failure_falls_through_to_llm(monkeypatch):
    """If Supabase select() blows up, the resolver must still classify."""
    monkeypatch.setenv("UTKRUSHT_ORG_ID", "fake-uuid-4")
    supabase = MagicMock()
    supabase.table.return_value.select.side_effect = RuntimeError("db down")
    with patch("generators.task.runtime_resolver.classify_with_llm",
               return_value=_fake_result("python", "app")):
        plan = resolve_plan(_comps(("Python", "BASIC")), supabase=supabase)
    assert plan.task_runtime is not None
    assert plan.task_runtime.runtime == "python"


# --- ResolvedPlan accessors safe when unclassified -------------------------

def test_resolved_plan_runtime_kind_safe_when_unclassified():
    p = ResolvedPlan(combo_key="x", task_runtime=None, template=None)
    assert p.runtime is None
    assert p.kind is None
    assert not p.gate_supported
