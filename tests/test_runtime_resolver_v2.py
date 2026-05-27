"""Unit tests for ``resolve_plan_v2`` — the unified classifier ↔ template path.

Mirrors the patterns in ``test_runtime_resolver.py`` (legacy v1 path) but
exercises the new ``task_template_match`` cache + ``classify_match_v2``.

Tests cover:
  1. Cache HIT (fresh) — no LLM call, returns the cached match + hydrated template.
  2. Cache HIT (stale by classifier_model) — re-classifies via LLM.
  3. Cache HIT (stale by registry_version) — re-classifies via LLM.
  4. Cache MISS — LLM call, upsert row, return.
  5. no_match path — template is None, match.no_match_reason populated.
  6. Classifier raises — empty plan returned, no crash.
  7. Cache unreachable (Supabase init fails) — direct LLM call, no persistence.
  8. Cache lookup fails — falls through to LLM.
  9. _is_match_fresh_v2 unit cases.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from infra.classifier.llm_classifier import ActiveTemplate
from infra.classifier.runtime import Competency, TaskTemplateMatch
from generators.task.runtime_resolver import (
    ResolvedPlanV2,
    TemplateSpecV2,
    _CLASSIFIER_MODEL_V2,
    _is_match_fresh_v2,
    _row_to_template_v2,
    resolve_plan_v2,
)


# ── helpers ──────────────────────────────────────────────────────────


def _comps(*pairs):
    return [Competency(name=n, proficiency=p) for n, p in pairs]


def _row(**kwargs) -> dict:
    """Build a ``templates`` row dict with sensible defaults."""
    base = dict(
        template_id="utkrusht-python",
        primary_runtime="python",
        personas=["backend", "data", "mle"],
        eval_methods=["test_suite"],
        capabilities={
            "frameworks": ["fastapi", "sqlalchemy"],
            "datastores": ["postgres"],
            "protocols": ["rest"],
            "tools": ["pytest"],
            "requires": {"browser": False, "gpu": False},
            "tags": [],
        },
        build_cmd="pip install -r requirements.txt",
        test_cmd="python -m pytest",
        compile_cmd="python -m compileall -q .",
        install_cmd="apt-get install -y python3 python3-pip",
        install_verify="python3 --version",
        install_seconds=15,
        manifest_hash="abc123",
        registry_version=1,
        description="Python 3.13 base.",
    )
    base.update(kwargs)
    return base


def _make_supabase(
    *,
    match_row: dict | None = None,
    template_rows: list[dict] | None = None,
    upsert_records: list | None = None,
) -> MagicMock:
    """Build a Supabase mock whose .table() routes by name.

    - ``task_template_match`` SELECT returns ``match_row`` (or empty).
    - ``templates`` SELECT returns ``template_rows`` (or empty).
    - ``task_template_match`` UPSERT appends payloads to ``upsert_records``.
    """
    client = MagicMock()

    def table(name: str):
        t = MagicMock()
        if name == "task_template_match":
            data_for_match = [match_row] if match_row else []
            (t.select.return_value
                .eq.return_value
                .limit.return_value
                .execute.return_value.data) = data_for_match

            def _upsert(payload):
                if upsert_records is not None:
                    upsert_records.append(payload)
                executed = MagicMock()
                executed.execute.return_value.data = [payload]
                return executed
            t.upsert.side_effect = _upsert
        elif name == "templates":
            rows = list(template_rows or [])
            # `.select(...)` returns chainable; both ".eq" (template_id lookup)
            # and ".execute" (load_active) paths are supported.
            select = t.select.return_value
            select.execute.return_value.data = rows  # load_active_templates_v2
            select.eq.return_value.execute.return_value.data = rows  # one-arg eq
            (select.eq.return_value.eq.return_value
                .limit.return_value.execute.return_value.data) = rows  # status-filtered + limit
        else:
            t.select.return_value.execute.return_value.data = []
        return t

    client.table.side_effect = table
    return client


# ── _is_match_fresh_v2 unit cases ────────────────────────────────────


def test_is_match_fresh_returns_true_when_model_and_version_match():
    t = TemplateSpecV2(
        template_id="x", primary_runtime="python",
        personas=[], eval_methods=[], capabilities={},
        build_cmd="", test_cmd="", registry_version=3,
    )
    assert _is_match_fresh_v2(_CLASSIFIER_MODEL_V2, 3, t) is True


def test_is_match_fresh_stale_when_model_differs():
    t = TemplateSpecV2(
        template_id="x", primary_runtime="python",
        personas=[], eval_methods=[], capabilities={},
        build_cmd="", test_cmd="", registry_version=1,
    )
    assert _is_match_fresh_v2("older-model", 1, t) is False


def test_is_match_fresh_stale_when_registry_version_bumped():
    t = TemplateSpecV2(
        template_id="x", primary_runtime="python",
        personas=[], eval_methods=[], capabilities={},
        build_cmd="", test_cmd="", registry_version=5,
    )
    assert _is_match_fresh_v2(_CLASSIFIER_MODEL_V2, 4, t) is False


def test_is_match_fresh_no_match_rows_survive_version_bumps():
    # template is None (no_match cached row). registry_version mismatch
    # should NOT invalidate — no_match only re-evaluates on model change.
    assert _is_match_fresh_v2(_CLASSIFIER_MODEL_V2, 1, None) is True
    assert _is_match_fresh_v2("older-model", 1, None) is False


# ── _row_to_template_v2 ──────────────────────────────────────────────


def test_row_to_template_v2_round_trip():
    row = _row(template_id="utkrusht-python", registry_version=7)
    spec = _row_to_template_v2(row)
    assert spec.template_id == "utkrusht-python"
    assert spec.registry_version == 7
    assert spec.personas == ["backend", "data", "mle"]
    assert spec.capabilities["frameworks"] == ["fastapi", "sqlalchemy"]


def test_row_to_template_v2_defaults_missing_columns():
    spec = _row_to_template_v2({
        "template_id": "minimal",
        "primary_runtime": "python",
        "build_cmd": "x", "test_cmd": "y",
    })
    assert spec.eval_methods == ["test_suite"]
    assert spec.personas == []
    assert spec.registry_version == 1
    assert spec.capabilities == {}


# ── resolve_plan_v2 ──────────────────────────────────────────────────


def test_cache_hit_returns_cached_match_no_llm():
    """Fresh cache row → no LLM, no upsert, returns hydrated template."""
    template_row = _row(template_id="utkrusht-python", registry_version=1)
    match_row = {
        "template_id": "utkrusht-python",
        "persona": "backend",
        "confidence": 0.92,
        "no_match_reason": None,
        "missing_capabilities": [],
        "suggested_template": None,
        "classifier_model": _CLASSIFIER_MODEL_V2,
        "registry_version": 1,
    }
    upserts: list = []
    client = _make_supabase(
        match_row=match_row,
        template_rows=[template_row],
        upsert_records=upserts,
    )

    with patch("infra.classifier.llm_classifier.classify_match_v2") as llm:
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    assert isinstance(plan, ResolvedPlanV2)
    assert plan.match is not None and plan.match.template_id == "utkrusht-python"
    assert plan.match.persona == "backend"
    assert plan.template is not None
    assert plan.template.template_id == "utkrusht-python"
    llm.assert_not_called()
    assert upserts == []  # no write on a fresh cache hit


def test_cache_hit_stale_model_triggers_reclassify():
    """Cached row with a stale classifier_model → LLM is called, upsert happens."""
    template_row = _row()
    stale_match = {
        "template_id": "utkrusht-python",
        "persona": "data",
        "confidence": 0.8,
        "no_match_reason": None,
        "missing_capabilities": [],
        "suggested_template": None,
        "classifier_model": "old-claude-sonnet",
        "registry_version": 1,
    }
    upserts: list = []
    client = _make_supabase(
        match_row=stale_match,
        template_rows=[template_row],
        upsert_records=upserts,
    )
    fresh_match = TaskTemplateMatch(
        template_id="utkrusht-python", persona="backend", confidence=0.95,
    )

    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=fresh_match,
    ) as llm:
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    llm.assert_called_once()
    assert plan.match.persona == "backend"  # fresh result, not stale "data"
    assert len(upserts) == 1
    assert upserts[0]["classifier_model"] == _CLASSIFIER_MODEL_V2


def test_cache_hit_stale_registry_version_triggers_reclassify():
    """Template registry_version bumped → cached row is stale → re-classify."""
    template_row = _row(registry_version=3)  # current
    stale_match = {
        "template_id": "utkrusht-python",
        "persona": "backend",
        "confidence": 0.9,
        "no_match_reason": None,
        "missing_capabilities": [],
        "suggested_template": None,
        "classifier_model": _CLASSIFIER_MODEL_V2,
        "registry_version": 1,  # cached at older version
    }
    upserts: list = []
    client = _make_supabase(
        match_row=stale_match,
        template_rows=[template_row],
        upsert_records=upserts,
    )

    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=TaskTemplateMatch(
            template_id="utkrusht-python", persona="backend", confidence=0.95),
    ) as llm:
        resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    llm.assert_called_once()
    assert upserts[0]["registry_version"] == 3  # writes the current version


def test_cache_miss_calls_llm_and_writes_row():
    """Empty cache → classify_match_v2 → upsert into task_template_match."""
    template_row = _row()
    upserts: list = []
    client = _make_supabase(
        match_row=None,
        template_rows=[template_row],
        upsert_records=upserts,
    )
    fresh_match = TaskTemplateMatch(
        template_id="utkrusht-python", persona="mle", confidence=0.88,
    )

    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=fresh_match,
    ) as llm:
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    llm.assert_called_once()
    # The active_templates argument should have been built from template_rows.
    call_args, _call_kwargs = llm.call_args
    active_arg = call_args[1]
    assert any(t.template_id == "utkrusht-python" for t in active_arg)
    assert plan.match is not None and plan.match.persona == "mle"
    assert len(upserts) == 1
    assert upserts[0]["combo_key"] == plan.combo_key


def test_no_match_path_writes_null_template_id():
    """LLM returns no_match → cached row has template_id=NULL + reason."""
    template_row = _row()
    upserts: list = []
    client = _make_supabase(
        match_row=None,
        template_rows=[template_row],
        upsert_records=upserts,
    )
    no_match = TaskTemplateMatch(
        no_match_reason="needs helm, terraform",
        missing_capabilities=["helm", "kubectl", "terraform"],
        suggested_template="utkrusht-infra",
        confidence=0.85,
    )

    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=no_match,
    ):
        plan = resolve_plan_v2(
            _comps(("Kubernetes", "INTERMEDIATE"), ("Helm", "INTERMEDIATE")),
            supabase=client,
        )

    assert plan.match is not None
    assert plan.match.template_id is None
    assert plan.match.no_match_reason == "needs helm, terraform"
    assert plan.template is None  # nothing to hydrate
    assert upserts[0]["template_id"] is None
    assert upserts[0]["missing_capabilities"] == ["helm", "kubectl", "terraform"]


def test_classifier_failure_returns_empty_plan():
    """LLM raises → empty plan (match=None, template=None), no crash."""
    template_row = _row()
    client = _make_supabase(match_row=None, template_rows=[template_row])

    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        side_effect=RuntimeError("portkey down"),
    ):
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    assert plan.match is None
    assert plan.template is None
    assert plan.combo_key == "Python (INTERMEDIATE)"


def test_no_cache_falls_through_to_llm():
    """supabase=None + _build_supabase_client fails → LLM only, no persistence."""
    fresh = TaskTemplateMatch(
        template_id="utkrusht-python", persona="backend", confidence=0.9,
    )
    with patch(
        "generators.task.runtime_resolver._build_supabase_client",
        side_effect=RuntimeError("no creds"),
    ), patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=fresh,
    ) as llm:
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")))

    llm.assert_called_once()
    # With no DB, active templates list passed to LLM is empty — see how
    # classify_match_v2 would handle that in real life (every output =
    # no_match). For this test we only verify resolve_plan_v2 doesn't crash.
    assert plan.match is fresh
    assert plan.template is None  # no DB, can't hydrate


def test_cache_lookup_failure_falls_through_to_llm():
    """Supabase lookup raises mid-call → resolve_plan_v2 still produces a plan."""
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = RuntimeError("supabase 500")

    fresh = TaskTemplateMatch(
        template_id="utkrusht-python", persona="backend", confidence=0.9,
    )
    # Match lookup will raise; but resolve_plan_v2 also tries to load
    # active templates after the miss-path branch — those calls also go
    # through the same broken client. We expect the empty active set
    # path to still let the LLM be called with []; mock that the LLM
    # itself returns a fresh match anyway.
    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=fresh,
    ) as llm:
        plan = resolve_plan_v2(_comps(("Python", "INTERMEDIATE")), supabase=client)

    llm.assert_called_once()
    assert plan.match is fresh


def test_resolved_plan_combo_key_is_canonical():
    """combo_key is sorted by name, proficiency-suffixed."""
    client = _make_supabase(match_row=None, template_rows=[_row()])
    with patch(
        "infra.classifier.llm_classifier.classify_match_v2",
        return_value=TaskTemplateMatch(
            template_id="utkrusht-python", persona="backend", confidence=0.9),
    ):
        plan_a = resolve_plan_v2(
            _comps(("Python", "INTERMEDIATE"), ("FastAPI", "INTERMEDIATE")),
            supabase=client,
        )
        plan_b = resolve_plan_v2(
            _comps(("FastAPI", "INTERMEDIATE"), ("Python", "INTERMEDIATE")),
            supabase=client,
        )
    assert plan_a.combo_key == plan_b.combo_key
    assert plan_a.combo_key == "FastAPI (INTERMEDIATE), Python (INTERMEDIATE)"
