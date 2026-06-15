"""The pipeline must hand the EXACT competency/background files stage 1 produced
to the downstream stages.

Regression: selecting `NodeJs` (slug 'nodejs') mis-resolved to the
`input_reactjs_nodejs` combo dir because the legacy glob used a substring match
('nodejs' ⊂ 'reactjs_nodejs') with an mtime tiebreak. Two guards now prevent it:
(1) `_parse_resolved_inputs` consumes the exact paths stage 1 emits, and
(2) the `_locate_input_files` fallback matches the `input_{slug}` dir as an exact
path segment.
"""
from __future__ import annotations

import json
import os

import run_pipeline as rp


# ── _parse_resolved_inputs (the robust handoff) ──────────────────────────
def _write_marker(stdout_path, comp, bg):
    stdout_path.write_text(
        "Output directory: whatever\n"
        f'{rp._RESOLVED_INPUTS_MARKER} {json.dumps({"competency": str(comp), "background": str(bg)})}\n',
        encoding="utf-8",
    )


def test_parse_resolved_inputs_returns_exact_paths(tmp_path):
    comp = tmp_path / "competency_nodejs_advanced_Utkrusht.json"
    bg = tmp_path / "background_forQuestions_utkrusht_nodejs_advanced.json"
    comp.write_text("{}"); bg.write_text("{}")
    out = tmp_path / "01_input_files.stdout"
    _write_marker(out, comp, bg)
    assert rp._parse_resolved_inputs(out) == (comp, bg)


def test_parse_resolved_inputs_none_when_marker_absent(tmp_path):
    out = tmp_path / "01_input_files.stdout"
    out.write_text("Output directory: x\n  Competency file: y\n", encoding="utf-8")
    assert rp._parse_resolved_inputs(out) is None


def test_parse_resolved_inputs_none_when_file_missing(tmp_path):
    out = tmp_path / "01_input_files.stdout"
    _write_marker(out, tmp_path / "nope_comp.json", tmp_path / "nope_bg.json")
    assert rp._parse_resolved_inputs(out) is None


def test_parse_resolved_inputs_last_marker_wins(tmp_path):
    comp = tmp_path / "c.json"; bg = tmp_path / "b.json"
    comp.write_text("{}"); bg.write_text("{}")
    out = tmp_path / "01_input_files.stdout"
    out.write_text(
        f'{rp._RESOLVED_INPUTS_MARKER} {json.dumps({"competency": "/stale/c.json", "background": "/stale/b.json"})}\n'
        f'{rp._RESOLVED_INPUTS_MARKER} {json.dumps({"competency": str(comp), "background": str(bg)})}\n',
        encoding="utf-8",
    )
    assert rp._parse_resolved_inputs(out) == (comp, bg)


# ── _locate_input_files fallback: exact dir segment, no substring collision ──
def _make_combo(root, dirslug, *, mtime):
    d = root / dirslug / "advanced" / f"{dirslug}_advanced_task"
    d.mkdir(parents=True)
    comp = d / f"competency_{dirslug.replace('input_', '')}_advanced_Utkrusht.json"
    bg = d / f"background_forQuestions_utkrusht_{dirslug.replace('input_', '')}_advanced.json"
    comp.write_text("{}"); bg.write_text("{}")
    for f in (comp, bg):
        os.utime(f, (mtime, mtime))
    return comp


def test_locate_does_not_substring_collide(tmp_path, monkeypatch):
    """slug 'nodejs' must pick input_nodejs even when input_reactjs_nodejs is NEWER."""
    monkeypatch.setattr(rp, "INPUT_FILES_ROOT", tmp_path)
    want = _make_combo(tmp_path, "input_nodejs", mtime=1000)
    _make_combo(tmp_path, "input_reactjs_nodejs", mtime=9999)  # newer — must NOT win
    # since far in the future → nothing is "fresh" → exercises the fallback
    comp, _bg = rp._locate_input_files(["NodeJs"], "ADVANCED", since=10**12)
    assert comp == want
    assert "input_reactjs_nodejs" not in str(comp)
