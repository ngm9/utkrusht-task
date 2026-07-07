"""Phase 1 of the Open-Ended Task Flag: the difficulty dial is decided once,
branches the generated prompt, and travels onto the task record.

These cover the PURE, network-free pieces:
  * the default-by-proficiency + override resolution rule
  * the DSPy signatures / GenerationResult carry the new field
  * the OPEN_ENDED constant prepend (idempotent) + CLI flag tri-state
  * the task-pipeline registry reader (get_open_ended_for)
"""
from __future__ import annotations

import dataclasses
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# resolve_open_ended — the one rule everyone shares
# ----------------------------------------------------------------------

def test_resolve_open_ended_defaults_by_proficiency():
    from generators.prompts.agent import resolve_open_ended
    # BASIC / BEGINNER → closed (specified)
    assert resolve_open_ended("BASIC", None) is False
    assert resolve_open_ended("BEGINNER", None) is False
    assert resolve_open_ended("basic", None) is False  # case-insensitive
    # INTERMEDIATE / ADVANCED → open (withhold the solution)
    assert resolve_open_ended("INTERMEDIATE", None) is True
    assert resolve_open_ended("ADVANCED", None) is True
    assert resolve_open_ended("intermediate", None) is True


def test_resolve_open_ended_override_wins():
    from generators.prompts.agent import resolve_open_ended
    # explicit choice beats the proficiency default in both directions
    assert resolve_open_ended("INTERMEDIATE", False) is False
    assert resolve_open_ended("BASIC", True) is True


# ----------------------------------------------------------------------
# the field plumbing exists on the signatures + result
# ----------------------------------------------------------------------

def test_signatures_declare_open_ended_input():
    from generators.prompts.agent import (
        GeneratePromptSignature,
        VerifyPromptSignature,
    )
    assert "open_ended" in GeneratePromptSignature.input_fields
    assert "open_ended" in VerifyPromptSignature.input_fields


def test_generation_result_has_open_ended_field():
    from generators.prompts.agent import GenerationResult
    names = {f.name for f in dataclasses.fields(GenerationResult)}
    assert "open_ended" in names
    # default is the safe/closed baseline
    assert GenerationResult.__dataclass_fields__["open_ended"].default is False


# ----------------------------------------------------------------------
# OPEN_ENDED constant prepend (mirrors _prepend_task_shape) + CLI flag
# ----------------------------------------------------------------------

def test_prepend_open_ended_emits_constant():
    from generators.prompts.__main__ import _prepend_open_ended
    out = _prepend_open_ended("PROMPT_REGISTRY = {}\n", True)
    assert "OPEN_ENDED = True" in out
    out_false = _prepend_open_ended("PROMPT_REGISTRY = {}\n", False)
    assert "OPEN_ENDED = False" in out_false


def test_prepend_open_ended_is_idempotent():
    from generators.prompts.__main__ import _prepend_open_ended
    once = _prepend_open_ended("PROMPT_REGISTRY = {}\n", True)
    twice = _prepend_open_ended(once, False)  # must NOT add a second assignment
    assert once == twice
    assert twice.count("OPEN_ENDED =") == 1


def test_prepended_constant_is_importable_and_correct(tmp_path):
    """The prepended source must be valid Python whose OPEN_ENDED reads back."""
    import importlib.util

    from generators.prompts.__main__ import _prepend_open_ended

    src = _prepend_open_ended("PROMPT_REGISTRY = {'k': [1, 2, 3]}\n", True)
    f = tmp_path / "prompt_mod.py"
    f.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("prompt_mod", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.OPEN_ENDED is True


def test_cli_has_open_ended_flag_defaulting_to_none():
    from generators.prompts.__main__ import cli
    params = {p.name: p for p in cli.params}
    assert "open_ended" in params
    # tri-state: unset → None (default by proficiency), --open-ended/--closed override
    assert params["open_ended"].default is None


# ----------------------------------------------------------------------
# task-pipeline reader — mirrors get_task_shape_for
# ----------------------------------------------------------------------

def test_get_open_ended_for_reads_registry(monkeypatch):
    from infra import utils
    monkeypatch.setattr(
        utils, "_OPEN_ENDED_REGISTRY", {"Python (INTERMEDIATE)": True}
    )
    inp = {"competencies": [{"name": "Python", "proficiency": "intermediate"}]}
    assert utils.get_open_ended_for(inp) is True


def test_get_open_ended_for_unknown_combo_is_none(monkeypatch):
    from infra import utils
    monkeypatch.setattr(utils, "_OPEN_ENDED_REGISTRY", {})
    inp = {"competencies": [{"name": "Rust", "proficiency": "BASIC"}]}
    # legacy / unannotated prompt → None (callers treat as False)
    assert utils.get_open_ended_for(inp) is None


def test_open_ended_persisted_in_both_draft_and_ready_blobs():
    """create_task must stamp open_ended onto BOTH the draft task_blob AND the
    ready task_blob — the ready blob REPLACES the draft's in mark_task_ready, so
    omitting it there silently drops the flag from the persisted DB row."""
    src = (_ROOT / "generators/task/creator.py").read_text(encoding="utf-8")
    # draft task_blob, ready task_blob, and task_data (task.json) → ≥3 refs
    assert src.count('"open_ended"') >= 3, (
        "open_ended must be set on the draft blob, the ready blob, and task_data"
    )


def test_taskblob_validation_tolerates_open_ended_key():
    """The ready-gate validator (TaskBlob) must IGNORE the extra open_ended key,
    not reject it — otherwise mark_task_ready's validate_task would fail."""
    from task_validation.base import TaskBlob
    blob = {
        "title": "t", "definitions": {"a": "b"}, "hints": "h",
        "resources": {"github_repo": "https://example.com/x"},
        "outcomes": ["o"], "question": "q", "short_overview": ["s"],
        "open_ended": True,
    }
    m = TaskBlob(**blob)        # must not raise
    assert m.title == "t"


def test_runrequest_has_open_ended_field():
    from trace_ui.server import RunRequest
    f = RunRequest.model_fields
    assert "open_ended" in f
    # tri-state default: None → defer to proficiency
    assert RunRequest(names=["Python"], proficiency="BASIC").open_ended is None


@pytest.mark.parametrize(
    "value,expected_flag",
    [(True, "--open-ended"), (False, "--closed")],
)
def test_launch_threads_open_ended(monkeypatch, value, expected_flag):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))

    srv.api_launch(RunRequest(names=["Python"], proficiency="INTERMEDIATE",
                              open_ended=value))
    cmd = cap["cmd"]
    assert expected_flag in cmd
    # the opposite flag must NOT also be present
    other = "--closed" if expected_flag == "--open-ended" else "--open-ended"
    assert other not in cmd


def test_launch_omits_open_ended_when_none(monkeypatch):
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))

    srv.api_launch(RunRequest(names=["Python"], proficiency="BASIC"))  # open_ended unset → None
    cmd = cap["cmd"]
    assert "--open-ended" not in cmd and "--closed" not in cmd


def test_get_open_ended_for_key_matches_task_shape_key(monkeypatch):
    """The open-ended key construction must stay in lockstep with task_shape so
    a single prompt module's two constants resolve under the same key."""
    from infra import utils
    captured = {"Java (BASIC), Python (BASIC)": True}
    monkeypatch.setattr(utils, "_OPEN_ENDED_REGISTRY", captured)
    monkeypatch.setattr(utils, "_TASK_SHAPE_REGISTRY", {"Java (BASIC), Python (BASIC)": "infra"})
    inp = {
        "competencies": [
            {"name": "Python", "proficiency": "basic"},
            {"name": "Java", "proficiency": "basic"},
        ]
    }
    # same sorted key drives both lookups
    assert utils.get_open_ended_for(inp) is True
    assert utils.get_task_shape_for(inp) == "infra"
