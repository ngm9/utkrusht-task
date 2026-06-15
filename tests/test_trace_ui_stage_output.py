"""The per-stage output endpoint (backs the click-to-view modal) returns the
combo dir's <prefix>.* log files for a canonical stage, skips timing JSON, maps
all 04_tasks substages to the shared 04_tasks files, and rejects unknown stages
(allowlist → no path traversal).
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from trace_ui import tailer
from trace_ui.server import app

client = TestClient(app)
RUN_ID = "run-20260613T060041Z"


@pytest.fixture
def fake_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    runs = tmp_path / ".task_agent_runs"
    runs.mkdir()
    monkeypatch.setattr(tailer, "RUNS_DIR", runs)
    return runs


def _combo(runs: Path, combo: str = "nodejs_advanced") -> Path:
    cd = runs / RUN_ID / combo
    cd.mkdir(parents=True)
    return cd


def test_returns_stage_files_and_skips_json(fake_runs):
    cd = _combo(fake_runs)
    (cd / "01_input_files.stdout").write_text("line A\nline B\n", encoding="utf-8")
    (cd / "01_input_files.stderr").write_text("", encoding="utf-8")
    (cd / "01_input_files.timing.json").write_text("{}", encoding="utf-8")
    r = client.get(f"/api/runs/{RUN_ID}/stage/input_files")
    assert r.status_code == 200
    data = r.json()
    assert data["filestage"] == "01_input_files"
    names = {f["name"] for f in data["files"]}
    assert "01_input_files.stdout" in names
    assert "01_input_files.timing.json" not in names  # JSON metadata skipped
    stdout = next(f for f in data["files"] if f["name"].endswith(".stdout"))
    assert "line A" in stdout["content"] and stdout["stream"] == "stdout"


def test_all_04_substages_map_to_04_tasks(fake_runs):
    cd = _combo(fake_runs)
    (cd / "04_tasks.stderr").write_text("task log\n", encoding="utf-8")
    for canon in ("classifier", "task_gen", "eval", "gate", "quality", "solution"):
        r = client.get(f"/api/runs/{RUN_ID}/stage/{canon}")
        assert r.status_code == 200, canon
        assert r.json()["filestage"] == "04_tasks"


def test_unknown_canon_rejected(fake_runs):
    _combo(fake_runs)
    assert client.get(f"/api/runs/{RUN_ID}/stage/etc_passwd").status_code == 400


def test_no_combo_dir_404(fake_runs):
    (fake_runs / RUN_ID).mkdir(parents=True)  # run dir but no combo subdir
    assert client.get(f"/api/runs/{RUN_ID}/stage/prompt").status_code == 404
