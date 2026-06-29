"""Per-stage resume: /api/runs/{id}/resume reconstructs the run_pipeline command
from a prior run's summary.json and threads --resume-from so earlier stages are
skipped (their artifacts reused)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException


def _setup(monkeypatch, summary, manifest=None):
    from trace_ui import server as srv
    run_dir = Path("/tmp/fake/run-20260101T000000Z")
    combo = run_dir / "combo"
    monkeypatch.setattr(srv, "_resolve_or_400", lambda rid: run_dir)
    monkeypatch.setattr(srv, "_combo_dir", lambda rd: combo)

    def fake_read(p):
        if p.name == "summary.json":
            return summary
        if p.name == "manifest.json":
            return manifest
        return None

    monkeypatch.setattr(srv, "_read_json", fake_read)
    cap: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: cap.update(cmd=cmd))
    return srv, cap


def test_resume_from_tasks_reconstructs_command(monkeypatch):
    summary = {"competencies": ["Production Agent Engineering"], "proficiency": "ADVANCED",
               "env": "dev", "llm_provider": "glm",
               "instructions": "include docker-compose", "count": 3}
    srv, cap = _setup(monkeypatch, summary)
    from trace_ui.server import ResumeRequest

    resp = srv.api_resume("run-x", ResumeRequest(from_stage="tasks"))
    body = json.loads(bytes(resp.body).decode())
    assert body["resumed_from"] == "tasks"
    cmd = cap["cmd"]
    assert cmd[cmd.index("--resume-from") + 1] == "tasks"
    assert cmd[cmd.index("-p") + 1] == "ADVANCED"
    assert cmd[cmd.index("--env") + 1] == "dev"
    assert cmd[cmd.index("--llm-provider") + 1] == "glm"
    assert cmd[cmd.index("--instructions") + 1] == "include docker-compose"
    assert cmd[cmd.index("-n") + 1] == "Production Agent Engineering"


def test_resume_input_files_is_full_rerun(monkeypatch):
    summary = {"competencies": ["Python"], "proficiency": "BASIC", "env": "dev",
               "llm_provider": "anthropic", "count": 2}
    srv, cap = _setup(monkeypatch, summary)
    from trace_ui.server import ResumeRequest
    srv.api_resume("run-x", ResumeRequest(from_stage="input_files"))
    assert "--resume-from" not in cap["cmd"]   # full re-run, no skip


def test_resume_missing_competencies_400(monkeypatch):
    srv, _ = _setup(monkeypatch, {"proficiency": "BASIC"})
    from trace_ui.server import ResumeRequest
    with pytest.raises(HTTPException) as ei:
        srv.api_resume("run-x", ResumeRequest(from_stage="tasks"))
    assert ei.value.status_code == 400


def test_resume_unknown_stage_defaults_to_tasks(monkeypatch):
    summary = {"competencies": ["Python"], "proficiency": "BASIC", "env": "dev"}
    srv, cap = _setup(monkeypatch, summary)
    from trace_ui.server import ResumeRequest
    srv.api_resume("run-x", ResumeRequest(from_stage="bogus"))
    cmd = cap["cmd"]
    assert cmd[cmd.index("--resume-from") + 1] == "tasks"
    # env/provider fall back to safe defaults when summary omits them
    assert cmd[cmd.index("--llm-provider") + 1] == "anthropic"
