"""Tests for the general reference prompts + retriever Level 6 fallback (Fix B).

The general reference is the retriever's last resort: when the 5-level ladder
finds zero references, the generator still gets a skeleton carrying the
canonical output JSON schema. Without it, bootstrap-mode combos invent synonym
keys and produce hollow tasks (finding F10).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from infra.classifier.classifier import Competency
from generators.prompts.retriever import (
    GENERAL_REFERENCE_DIR,
    _general_reference_path,
    retrieve_references,
)
from generators.prompts.validator import _missing_json_schema_keys, _simulate_format_call


LEVELS = ("beginner", "basic", "intermediate", "advanced")


# ---------------------------------------------------------------------------
# The four general reference files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("level", LEVELS)
def test_general_reference_file_exists(level: str) -> None:
    p = GENERAL_REFERENCE_DIR / f"general_{level}_prompt.py"
    assert p.exists(), f"missing general reference for {level}"


@pytest.mark.parametrize("level", LEVELS)
def test_general_reference_loads_and_has_registry(level: str) -> None:
    p = GENERAL_REFERENCE_DIR / f"general_{level}_prompt.py"
    spec = importlib.util.spec_from_file_location(f"gr_{level}", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "PROMPT_REGISTRY")
    keys = list(mod.PROMPT_REGISTRY.keys())
    assert len(keys) == 1
    assert keys[0] == f"General Reference ({level.upper()})"


@pytest.mark.parametrize("level", LEVELS)
def test_general_reference_uses_canonical_keys(level: str) -> None:
    """The whole point of the general reference: carry the canonical schema."""
    src = (GENERAL_REFERENCE_DIR / f"general_{level}_prompt.py").read_text()
    assert _missing_json_schema_keys(src) == [], (
        f"general_{level} is missing canonical output keys"
    )


@pytest.mark.parametrize("level", LEVELS)
def test_general_reference_formats_cleanly(level: str) -> None:
    """No unescaped braces — must survive downstream str.format()."""
    src = (GENERAL_REFERENCE_DIR / f"general_{level}_prompt.py").read_text()
    assert _simulate_format_call(src) == []


# ---------------------------------------------------------------------------
# Retriever Level 6
# ---------------------------------------------------------------------------


def test_general_reference_path_resolves_each_level() -> None:
    for level in ("BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"):
        p = _general_reference_path(level)
        assert p is not None and p.exists()
        assert level.lower() in p.name


def test_general_reference_path_unknown_level_falls_back() -> None:
    """An unknown proficiency must still resolve (to BASIC), never None."""
    p = _general_reference_path("EXPERT")
    assert p is not None and p.exists()


def test_zero_reference_combo_hits_level_6() -> None:
    """A combo with NO curated prompt at any level must anchor on the general
    reference (Level 6). Was PHP+Laravel (the F10 combo), but php_laravel prompt
    files now exist, so it's no longer reference-less — use a synthetic competency
    guaranteed to match no filename token and have no tech-family sibling."""
    r = retrieve_references(
        [Competency("Nonexistent Synthetic Discipline", "INTERMEDIATE")],
        "INTERMEDIATE",
    )
    assert r.used_general_fallback is True
    assert r.fallback_level == 6
    assert len(r.references) == 1
    assert r.references[0].name == "general_intermediate_prompt.py"


def test_well_referenced_combo_does_not_hit_level_6() -> None:
    """Java+Docker BASIC has real curated references — must NOT use the fallback."""
    r = retrieve_references(
        [Competency("Java", "BASIC"), Competency("Docker", "BASIC")],
        "BASIC",
    )
    assert r.used_general_fallback is False
    assert r.fallback_level < 6
    assert r.references, "expected real references for Java+Docker"


def test_general_reference_not_loaded_into_task_registry() -> None:
    """The _general_reference/ folder must NOT pollute utils._PROMPT_REGISTRY —
    those are reference skeletons, not real task prompts."""
    from infra.utils import _PROMPT_REGISTRY
    for key in _PROMPT_REGISTRY:
        assert not key.startswith("General Reference ("), (
            f"general reference {key!r} leaked into the task registry"
        )
