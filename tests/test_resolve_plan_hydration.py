"""resolve_plan(hydrate_template=False) — used for non_infra tasks — must skip
the boot-recipe DB fetch (_get_template) while still returning the match
(persona + template_id). Infra (hydrate_template=True) still hydrates.
"""
import types

import generators.task.runtime_resolver as rr
from infra.classifier.runtime import Competency


def _patch_cache_hit(monkeypatch, cached, template):
    """Force a fresh cache hit + spy on _get_template."""
    monkeypatch.setattr(rr, "_match_lookup",
                        lambda client, key: (cached, 1, rr._CLASSIFIER_MODEL))
    calls = []

    def fake_get_template(client, tid):
        calls.append(tid)
        return template

    monkeypatch.setattr(rr, "_get_template", fake_get_template)
    return calls


def test_non_infra_skips_template_hydration(monkeypatch):
    cached = types.SimpleNamespace(
        template_id="utkrusht-python-ai", persona="agent_engineer", confidence=0.82)
    calls = _patch_cache_hit(monkeypatch, cached, template=None)
    plan = rr.resolve_plan(
        [Competency(name="Production Agent Engineering", proficiency="INTERMEDIATE")],
        supabase=object(), hydrate_template=False,
    )
    assert plan.match is cached                       # persona + template_id kept
    assert plan.match.persona == "agent_engineer"
    assert plan.match.template_id == "utkrusht-python-ai"
    assert plan.template is None                      # recipe NOT hydrated
    assert calls == []                                # _get_template never called


def test_infra_still_hydrates(monkeypatch):
    cached = types.SimpleNamespace(
        template_id="utkrusht-python", persona="backend", confidence=0.9)
    fake_template = types.SimpleNamespace(registry_version=1)
    calls = _patch_cache_hit(monkeypatch, cached, template=fake_template)
    plan = rr.resolve_plan(
        [Competency(name="Python", proficiency="INTERMEDIATE")],
        supabase=object(), hydrate_template=True,
    )
    assert plan.template is fake_template             # recipe hydrated
    assert calls == ["utkrusht-python"]               # _get_template called
