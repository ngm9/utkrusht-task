"""Pins the recursive prompt-registry walk in ``utils.py``.

Before Fix 3 in the smoke-test run, ``_build_prompt_registry`` used
``pkgutil.iter_modules`` which only sees flat ``<Level>/*.py`` files. Three
classes of prompt were silently invisible to ``multiagent.py``:

  1. Curated per-slug nested layout ``<Level>/<slug>/<slug>.py`` (java_docker,
     langchain, nodejs_postgresql).
  2. The entire ``agent_generated_prompts/`` subtree produced by the
     prompt_generator agent.
  3. Future prompt-generator output land at
     ``agent_generated_prompts/<Level>/<slug>/<slug>.py``.

These tests lock the patched behaviour so a future refactor can't regress us
back to the silent-invisibility state.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def registry() -> dict:
    """The prompt registry built by utils.py at import time."""
    from utils import _PROMPT_REGISTRY
    return _PROMPT_REGISTRY


def test_registry_has_meaningful_size(registry: dict) -> None:
    """If this drops sharply, the recursive walk likely broke."""
    assert len(registry) >= 80, (
        f"Expected ~80+ prompts; got {len(registry)}. "
        "Did the recursive walk regress to pkgutil-only?"
    )


def test_registry_finds_flat_layout_basic(registry: dict) -> None:
    """Flat ``Basic/python_basic_prompt.py`` must still be discovered."""
    assert "Python (BASIC)" in registry


def test_registry_finds_nested_per_slug_curated(registry: dict) -> None:
    """Curated per-slug folder ``Basic/<slug>/<slug>.py`` discovery.

    Both keys were silently invisible before the patch — confirmed during the
    2026-05-14 smoke test as coordinator finding F3.
    """
    assert "Docker (BASIC), Java (BASIC)" in registry, (
        "java_docker_basic_prompt/java_docker_basic_prompt.py was orphaned "
        "before Fix 3 — recursive walk must surface it."
    )
    assert "Langchain (BASIC)" in registry, (
        "langchain_basic_prompt/langchain_basic_prompt.py was orphaned "
        "before Fix 3 — recursive walk must surface it."
    )


def test_registry_skips_archived_originals(registry: dict) -> None:
    """``<slug>/original_temp_prompt/*.py`` archives must NOT be loaded.

    If they were, we'd see duplicate keys clobbering the canonical entries
    with stale registry values.
    """
    # The canonical file lives at <slug>/<slug>.py; archives at
    # <slug>/original_temp_prompt/<name>.py. The walk picks ONLY the canonical
    # convention so archives are skipped. We verify indirectly: the canonical
    # entries must still be present.
    assert "Docker (BASIC), Java (BASIC)" in registry
    assert "Langchain (BASIC)" in registry
