"""Tests for the durable prompt corpus + its retriever union.

Covers the two things that actually break:
  1. Slug identity — the corpus row key and the on-disk filename MUST match, or
     a promoted prompt never resolves as a reference (silent: no error, just a
     permanent fall back to the generic skeleton).
  2. The retriever union — approved prompts appear, curated ones still win.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from flows.tech.stages.prompts import corpus, retriever
from flows.tech.stages.prompts.__main__ import _expected_path


def test_slug_matches_on_disk_filename():
    """The corpus key and the generated filename come from one function."""
    for names, level in (
        (["Python", "SQL"], "BASIC"),
        (["Node.js"], "INTERMEDIATE"),
        (["Spring Boot", "Kafka"], "ADVANCED"),
    ):
        assert _expected_path(names, level).stem == corpus.slug_for(names, level)


def test_slug_normalises_names():
    assert corpus.slug_for(["Python", "SQL"], "BASIC") == "python_sql_basic_prompt"
    assert corpus.slug_for(["Node.js"], "INTERMEDIATE") == "nodejs_intermediate_prompt"
    assert corpus.slug_for(["HTML & CSS"], "BASIC") == "html_css_basic_prompt"


def _fake_approved_root(tmp_path: Path, level_folder: str, slug: str) -> Path:
    dest = tmp_path / level_folder / slug / f"{slug}.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("PROMPT_REGISTRY = {}\n")
    return tmp_path


def test_approved_prompts_join_the_reference_pool(tmp_path, monkeypatch):
    """An approved prompt is listed alongside the curated tree."""
    root = _fake_approved_root(tmp_path, "Basic", "zzz_fictional_stack_basic_prompt")
    monkeypatch.setattr(corpus, "approved_root", lambda env="dev": root)

    files = retriever._list_prompt_files("BASIC")
    names = [p.name for p in files]
    assert "zzz_fictional_stack_basic_prompt.py" in names
    # curated tree still present
    assert len(names) > 1


def test_curated_wins_and_sorts_first_on_collision(tmp_path, monkeypatch):
    """A promoted prompt never shadows or outranks a curated one of the same name."""
    curated = retriever._list_prompt_files("BASIC")
    assert curated, "expected a curated BASIC corpus to test against"
    clash = curated[0].name  # same filename as a real curated prompt
    slug = clash[:-3]

    root = _fake_approved_root(tmp_path, "Basic", slug)
    monkeypatch.setattr(corpus, "approved_root", lambda env="dev": root)

    files = retriever._list_prompt_files("BASIC")
    assert [p.name for p in files].count(clash) == 1, "duplicate slug leaked through"
    # the surviving one is the curated file, not the temp-dir copy
    assert next(p for p in files if p.name == clash) == curated[0]


def test_no_approved_corpus_is_a_noop(monkeypatch):
    """Corpus unreachable / empty => retrieval behaves exactly as before."""
    monkeypatch.setattr(corpus, "approved_root", lambda env="dev": None)
    assert retriever._list_prompt_files("BASIC") == sorted(
        retriever._scan_level_folder(retriever._level_folder("BASIC"))
    )


def test_save_candidate_never_raises(monkeypatch):
    """A corpus outage must not fail a task generation."""
    def boom(_env):
        raise RuntimeError("supabase down")

    monkeypatch.setattr(corpus, "init_supabase", boom)
    assert corpus.save_candidate(["Python"], "BASIC", "src", env="dev") is False


def test_approve_for_task_never_raises(monkeypatch):
    def boom(_env):
        raise RuntimeError("supabase down")

    monkeypatch.setattr(corpus, "init_supabase", boom)
    assert corpus.approve_for_task(
        [{"name": "Python", "proficiency": "BASIC"}], "task-1", env="dev"
    ) is False


def test_approve_for_task_ignores_empty_competencies():
    assert corpus.approve_for_task([], "task-1", env="dev") is False
    assert corpus.approve_for_task([{"name": "Python"}], "task-1", env="dev") is False
