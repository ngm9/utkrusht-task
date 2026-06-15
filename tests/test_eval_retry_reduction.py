"""Regression tests for the retry-reduction fixes.

Two eval-gate failures used to force full task regenerations on fields the
generator does not control:

  * PROFICIENCY FIT failed because ``yoe`` was read from a never-populated
    ``background.yoe`` key (always blank).
  * CRITERIA COVERAGE failed because the judge demanded competencies that
    were never declared inputs (criterias is code-stamped).

These tests lock in: (1) a deterministic proficiency→YoE/time profile,
(2) ``run_evaluations`` always feeding the critic a concrete (non-blank) YoE
at the ceiling proficiency, and (3) the ``blockers_are_deterministic_only``
gate the retry loop uses to re-score instead of regenerate.
"""
from __future__ import annotations

import generators.task.evaluator as ev
from generators.task import (
    blockers_are_deterministic_only,
    proficiency_profile,
)


def _ok():
    return {"pass": True, "blocking_issues": [], "suggestions": [], "validated_criteria": []}


# ── proficiency_profile ──────────────────────────────────────────────────
def test_proficiency_profile_known_levels():
    assert proficiency_profile("ADVANCED") == ("6+ years", 25)
    assert proficiency_profile("INTERMEDIATE") == ("3-5 years", 20)
    assert proficiency_profile("BASIC") == ("1-2 years", 15)


def test_proficiency_profile_case_insensitive_and_fallback():
    assert proficiency_profile("advanced") == ("6+ years", 25)
    assert proficiency_profile("") == ("1-2 years", 15)        # blank → BASIC
    assert proficiency_profile("wizard") == ("1-2 years", 15)  # unknown → BASIC


# ── run_evaluations feeds a concrete, non-blank YoE ──────────────────────
def _patch_critics(monkeypatch):
    captured = {}

    def fake_task_eval(task_json, proficiency, yoe, time_constraint, client,
                       persona=None, scenarios=None, **kw):
        captured.update(proficiency=proficiency, yoe=yoe, time_constraint=time_constraint)
        return _ok()

    monkeypatch.setattr(ev, "llm_task_eval", fake_task_eval)
    monkeypatch.setattr(ev, "llm_code_eval",
                        lambda code, desc, client, persona=None, **kw: _ok())
    return captured


def test_run_evaluations_derives_nonblank_yoe_advanced(monkeypatch):
    captured = _patch_critics(monkeypatch)
    task = {"criterias": [{"proficiency": "ADVANCED"}, {"proficiency": "ADVANCED"}],
            "code_files": {}, "description": ""}
    ev.run_evaluations(task)
    assert captured["yoe"] == "6+ years"     # never blank (the old bug)
    assert captured["time_constraint"] == 25
    assert captured["proficiency"] == "ADVANCED"


def test_run_evaluations_judges_mixed_combo_at_ceiling(monkeypatch):
    captured = _patch_critics(monkeypatch)
    # mixed levels → ceiling (ADVANCED) wins, YoE + time agree with it
    task = {"criterias": [{"proficiency": "BASIC"}, {"proficiency": "ADVANCED"}],
            "code_files": {}, "description": ""}
    ev.run_evaluations(task)
    assert captured["proficiency"] == "ADVANCED"
    assert captured["yoe"] == "6+ years"
    assert captured["time_constraint"] == 25


def test_run_evaluations_yoe_never_blank_for_any_level(monkeypatch):
    for level, expected in [("BASIC", "1-2 years"), ("INTERMEDIATE", "3-5 years")]:
        captured = _patch_critics(monkeypatch)
        task = {"criterias": [{"proficiency": level}], "code_files": {}, "description": ""}
        ev.run_evaluations(task)
        assert captured["yoe"] == expected and captured["yoe"] != ""


# ── blockers_are_deterministic_only ──────────────────────────────────────
def test_deterministic_only_true_for_proficiency_and_coverage():
    e = {"code_eval": {"pass": True},
         "task_eval": {"blocking_issues": [
             "Criterion 5 (CRITERIA COVERAGE): PostgreSQL unreferenced",
             "Criterion 2: PROFICIENCY FIT — YoE blank",
         ]}}
    assert blockers_are_deterministic_only(e) is True


def test_deterministic_only_matches_names_without_numbers():
    e = {"code_eval": {"pass": True},
         "task_eval": {"blocking_issues": ["PROFICIENCY FIT issue", "CRITERIA COVERAGE issue"]}}
    assert blockers_are_deterministic_only(e) is True


def test_deterministic_only_false_for_content_criterion():
    e = {"code_eval": {"pass": True},
         "task_eval": {"blocking_issues": ["Criterion 1 (SCENARIO REALISM): contrived"]}}
    assert blockers_are_deterministic_only(e) is False


def test_deterministic_only_false_when_mixed_with_content():
    e = {"code_eval": {"pass": True},
         "task_eval": {"blocking_issues": [
             "Criterion 5 (CRITERIA COVERAGE): ...",
             "Criterion 3 (SCOPE COHERENCE): orphaned requirement",
         ]}}
    assert blockers_are_deterministic_only(e) is False


def test_deterministic_only_false_when_code_eval_failed():
    e = {"code_eval": {"pass": False},
         "task_eval": {"blocking_issues": ["Criterion 5 (CRITERIA COVERAGE): ..."]}}
    assert blockers_are_deterministic_only(e) is False


def test_deterministic_only_false_when_no_blockers():
    e = {"code_eval": {"pass": True}, "task_eval": {"blocking_issues": []}}
    assert blockers_are_deterministic_only(e) is False
