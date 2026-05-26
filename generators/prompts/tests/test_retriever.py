"""Regression tests for the retriever's matching and listing helpers.

Pins three previously-broken behaviours:

  1. Filename token matching must use word boundaries, not substring — "Java"
     should not match a ``javascript_*`` file, "Go" should not match
     ``mongodb_*``.
  2. ``_list_prompt_files`` must surface canonical per-slug nested prompts
     (``<level>/<slug>/<slug>.py``) and must NOT surface archived originals
     under ``<level>/<slug>/original_temp_prompt/``.
  3. Known competency aliases (Go/Golang, Node/NodeJS) must match each other.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from infra.classifier.classifier import Competency
from generators.prompts.retriever import (
    _file_matches_competency,
    _filename_tokens,
    _list_prompt_files,
    _name_tokens,
)


# ----------------------------------------------------------------------
# Word-boundary matching
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("comp_name", "filename", "should_match"),
    [
        # The leakage cases the new matcher is built to prevent.
        ("Java", "javascript_basic_prompt.py", False),
        ("Java", "html_css_javascript_beginner_prompt.py", False),
        ("Go", "mongodb_react_node_basic_prompt.py", False),
        ("Go", "html_css_javascript_beginner_prompt.py", False),

        # Still match the things we want.
        ("Java", "java_docker_basic_prompt.py", True),
        ("Java", "Java_spring_boot_prompt.py", True),
        ("Go", "go_redis_basic_prompt.py", True),

        # Aliases — Go must find Golang files, NodeJS must find Node files.
        ("Go", "golang_docker_prompt.py", True),
        ("Golang", "go_redis_basic_prompt.py", True),
        ("Node.js", "nodejs_postgresql_basic_prompt.py", True),

        # Multi-token competency — "Spring Boot" should match a file
        # named after either Spring or Boot.
        ("Spring Boot", "Java_spring_boot_prompt.py", True),
    ],
)
def test_file_matches_competency(comp_name, filename, should_match):
    comp = Competency(name=comp_name, proficiency="BASIC")
    assert (
        _file_matches_competency(Path(filename), comp) is should_match
    ), f"{comp_name!r} vs {filename!r}: expected {should_match}"


def test_filename_tokens_splits_on_separators():
    assert _filename_tokens(Path("Java_spring_boot_prompt.py")) == {
        "java", "spring", "boot", "prompt",
    }
    assert _filename_tokens(Path("python-fastapi.docker.py")) == {
        "python", "fastapi", "docker",
    }


def test_name_tokens_includes_aliases():
    go_tokens = _name_tokens(Competency(name="Go", proficiency="BASIC"))
    assert {"go", "golang"}.issubset(go_tokens)

    node_tokens = _name_tokens(Competency(name="Node.js", proficiency="BASIC"))
    assert {"node", "nodejs"}.issubset(node_tokens)


# ----------------------------------------------------------------------
# Canonical per-slug folder discovery
# ----------------------------------------------------------------------


def test_list_prompt_files_includes_canonical_nested(tmp_path, monkeypatch):
    """A ``<slug>/<slug>.py`` file is treated as curated and surfaced."""

    fake_root = tmp_path / "task_generation_prompts"
    level = fake_root / "Basic"
    level.mkdir(parents=True)

    # Flat-style prompt
    (level / "flat_prompt.py").write_text("# flat", encoding="utf-8")

    # Canonical per-slug folder
    slug_dir = level / "java_docker_basic_prompt"
    slug_dir.mkdir()
    (slug_dir / "java_docker_basic_prompt.py").write_text("# canonical", encoding="utf-8")
    # Archived original — must NOT appear in results.
    archive = slug_dir / "original_temp_prompt"
    archive.mkdir()
    (archive / "Java_docker_basic_prompt.py").write_text("# archived", encoding="utf-8")

    # Dunder file — must be skipped.
    (level / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr("prompt_generator.retriever.PROMPT_ROOT", fake_root)

    files = _list_prompt_files("BASIC")
    names = {p.name for p in files}

    assert "flat_prompt.py" in names
    assert "java_docker_basic_prompt.py" in names
    assert "__init__.py" not in names
    # The archived file shares a stem with the canonical one — guard by parent.
    parents = {p.parent.name for p in files}
    assert "original_temp_prompt" not in parents
