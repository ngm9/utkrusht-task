"""Regression tests for input_files directory matching.

Pins the fix where ``input_files._find_background_file`` previously did a
strict ``input_{combo_slug}*`` glob and missed real folders whose naming
diverged from the slug convention (e.g. ``input_mongodb_node_react_task_intermediate``
for a ``MongoDB + NodeJs + React Framework`` combo).
"""

from __future__ import annotations

import json

import pytest

from prompt_generator import input_files


@pytest.fixture
def fake_input_root(tmp_path, monkeypatch):
    """Point ``input_files`` at a temp dir we'll populate per-test."""
    root = tmp_path / "task_input_files"
    root.mkdir()
    monkeypatch.setattr(input_files, "INPUT_FILES_ROOT", root)
    return root


def _write_background(folder, level_token, payload):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"background_utkrusht_{level_token}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_finds_mern_folder_with_diverged_naming(fake_input_root):
    """The MERN slug-mismatch case the original bug exposed.

    Combo slug from the agent: ``mongodb_nodejs_react_framework``.
    On-disk folder name:       ``input_mongodb_node_react_task_intermediate``.
    The matcher must still resolve it via alias-aware token scoring.
    """
    folder = fake_input_root / "input_mongodb_node_react_task_intermediate"
    _write_background(folder, "intermediate", {
        "role_context": "MERN engineer",
        "questions_prompt": "- API\n- Schema",
    })

    path = input_files._find_background_file(
        ["MongoDB", "NodeJs", "React Framework"], "INTERMEDIATE",
    )
    assert path is not None
    assert path.parent.name == "input_mongodb_node_react_task_intermediate"


def test_rejects_folder_missing_a_competency(fake_input_root):
    """All competencies must match — a 2-of-3 folder should not be picked."""
    _write_background(
        fake_input_root / "input_mongodb_node_intermediate",
        "intermediate",
        {"role_context": "no react here"},
    )

    path = input_files._find_background_file(
        ["MongoDB", "NodeJs", "React Framework"], "INTERMEDIATE",
    )
    assert path is None


def test_prefers_folder_with_level_token(fake_input_root):
    """When two candidates match, prefer the one whose dir name carries the level."""
    bare = fake_input_root / "input_python_sql"
    leveled = fake_input_root / "input_python_sql_intermediate_task"
    _write_background(bare, "intermediate", {"role_context": "bare"})
    leveled_path = _write_background(leveled, "intermediate", {"role_context": "leveled"})

    picked = input_files._find_background_file(
        ["Python", "SQL"], "INTERMEDIATE",
    )
    assert picked == leveled_path


def test_rejects_cross_level_pollution(fake_input_root):
    """A Basic folder must not be returned for an Intermediate lookup."""
    _write_background(
        fake_input_root / "input_python_sql_basic_task",
        "basic",
        {"role_context": "basic only"},
    )
    path = input_files._find_background_file(["Python", "SQL"], "INTERMEDIATE")
    assert path is None


def test_finds_level_via_subpath(fake_input_root):
    """Some folders nest by level: ``input_<combo>/<level>/background_*.json``."""
    nested = fake_input_root / "input_python_sql" / "intermediate"
    _write_background(nested, "intermediate", {"role_context": "nested"})
    path = input_files._find_background_file(["Python", "SQL"], "INTERMEDIATE")
    assert path is not None


def test_node_js_alias_matches_node_folder(fake_input_root):
    """Node.js competency should match a folder whose name uses 'node'."""
    folder = fake_input_root / "input_node_mongo_task"
    _write_background(folder, "basic", {"role_context": "ok"})
    path = input_files._find_background_file(["Node.js", "MongoDB"], "BASIC")
    assert path is not None


def test_react_framework_alias_matches_reactjs_folder(fake_input_root):
    """'React Framework' should match a folder containing 'reactjs'."""
    folder = fake_input_root / "input_reactjs_nodejs_mongodb"
    _write_background(folder, "intermediate", {"role_context": "ok"})
    path = input_files._find_background_file(
        ["React Framework", "NodeJs", "MongoDB"], "INTERMEDIATE",
    )
    assert path is not None


def test_returns_none_when_root_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(input_files, "INPUT_FILES_ROOT", tmp_path / "nope")
    assert input_files._find_background_file(["Python"], "BASIC") is None


def test_load_role_context_uses_token_matching(fake_input_root):
    """End-to-end: load_role_context resolves the MERN folder through the new matcher."""
    folder = fake_input_root / "input_mongodb_node_react_task_intermediate"
    _write_background(folder, "intermediate", {
        "role_context": "MERN engineer with 3-5 years experience.",
    })
    role = input_files.load_role_context(
        ["MongoDB", "NodeJs", "React Framework"], "INTERMEDIATE",
    )
    assert "MERN engineer" in role


def test_load_questions_prompt_uses_token_matching(fake_input_root):
    folder = fake_input_root / "input_mongodb_node_react_task_intermediate"
    _write_background(folder, "intermediate", {
        "questions_prompt": "Lead.\n- one\n- two",
    })
    q = input_files.load_questions_prompt(
        ["MongoDB", "NodeJs", "React Framework"], "INTERMEDIATE",
    )
    assert "- one" in q and "- two" in q
