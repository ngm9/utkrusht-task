"""The per-stage ARTIFACTS endpoint returns the generated files a stage produced
(input competency/background JSON, the prompt .py, scenario cards, task.json +
README + code), resolved from the run's stage logs, with a path-traversal guard.
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from trace_ui import server, tailer
from trace_ui.server import app

client = TestClient(app)
RUN = "run-20260616T010101Z"


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runs = tmp_path / ".task_agent_runs"
    runs.mkdir()
    monkeypatch.setattr(tailer, "RUNS_DIR", runs)
    gen = tmp_path / "data" / "generated"
    gen.mkdir(parents=True)
    monkeypatch.setattr(server, "_GEN_ROOT", gen)
    combo = runs / RUN / "nodejs_advanced"
    combo.mkdir(parents=True)
    (runs / RUN / "traces").mkdir()
    return {"runs": runs, "gen": gen, "combo": combo, "run_dir": runs / RUN}


def test_input_files_via_marker(env):
    gen, combo = env["gen"], env["combo"]
    d = gen / "input_files" / "input_nodejs" / "advanced" / "t"
    d.mkdir(parents=True)
    comp = d / "competency_nodejs_advanced.json"
    comp.write_text(json.dumps({"name": "NodeJs", "proficiency": "ADVANCED", "scope": "deep async"}))
    bg = d / "background.json"
    bg.write_text(json.dumps({"role_context": "6+ yrs", "questions_prompt": "- q1"}))
    marker = "__INPUT_FILES_RESOLVED__ " + json.dumps({"competency": str(comp), "background": str(bg)})
    (combo / "01_input_files.stdout").write_text("Output directory: x\n" + marker + "\n")

    arts = client.get(f"/api/runs/{RUN}/artifacts/input_files").json()["artifacts"]
    titles = {a["title"] for a in arts}
    assert comp.name in titles and bg.name in titles
    comp_art = next(a for a in arts if a["title"] == comp.name)
    assert comp_art["kind"] == "json" and comp_art["data"]["scope"] == "deep async"


def test_input_files_human_line_fallback(env):
    gen, combo = env["gen"], env["combo"]
    d = gen / "input_files" / "input_nodejs" / "advanced"
    d.mkdir(parents=True)
    (d / "competency_x.json").write_text(json.dumps({"name": "NodeJs"}))
    (combo / "01_input_files.stdout").write_text(
        f"Output directory: {d}\n  Competency file: competency_x.json\n")
    arts = client.get(f"/api/runs/{RUN}/artifacts/input_files").json()["artifacts"]
    assert any(a["title"] == "competency_x.json" for a in arts)


def test_input_files_traversal_blocked(env):
    combo = env["combo"]
    outside = env["runs"].parent / "secret.json"  # tmp_path/secret.json — outside gen + run_dir
    outside.write_text('{"x": 1}')
    marker = "__INPUT_FILES_RESOLVED__ " + json.dumps({"competency": str(outside), "background": str(outside)})
    (combo / "01_input_files.stdout").write_text(marker + "\n")
    r = client.get(f"/api/runs/{RUN}/artifacts/input_files")
    assert r.status_code == 200
    assert r.json()["artifacts"] == []  # traversal rejected


def test_prompt_artifact(env):
    gen, combo = env["gen"], env["combo"]
    pdir = gen / "agent_prompts" / "Advanced" / "nodejs_advanced_prompt"
    pdir.mkdir(parents=True)
    pf = pdir / "nodejs_advanced_prompt.py"
    pf.write_text("PROMPT_REGISTRY = {}\n")
    (combo / "03_prompt.stdout").write_text(f"Output path: {pf}\nWrote: {pf}\n")
    arts = client.get(f"/api/runs/{RUN}/artifacts/prompt").json()["artifacts"]
    assert len(arts) == 1 and arts[0]["kind"] == "code" and arts[0]["lang"] == "python"
    assert "PROMPT_REGISTRY" in arts[0]["content"]


def test_scenarios_artifact(env, monkeypatch):
    monkeypatch.setattr(server, "_scenario_pool", lambda run_dir, combo: [])  # no DB
    locked = "**Current Implementation:** Old code. **Your Task:** Fix it. **Success Criteria:** Works."
    (env["combo"] / "04_tasks.stderr").write_text("Locked scenarios: " + json.dumps([locked]) + "\n")
    arts = client.get(f"/api/runs/{RUN}/artifacts/scenarios").json()["artifacts"]
    assert len(arts) == 1 and arts[0]["kind"] == "scenarios"
    item = arts[0]["items"][0]
    assert item["locked"] is True
    assert "Old code" in item["current"] and "Fix it" in item["task"] and "Works" in item["success"]


def test_task_gen_artifacts(env):
    gen, run_dir = env["gen"], env["run_dir"]
    (run_dir / "traces" / "manifest.json").write_text(json.dumps({"task_id": "abc-123"}))
    tdir = gen / "task_artifacts" / "abc-123"
    tdir.mkdir(parents=True)
    (tdir / "task.json").write_text(json.dumps({"name": "t", "title": "T"}))
    (tdir / "README.md").write_text("# Hello\n\nbody")
    (tdir / "server.js").write_text("console.log(1)\n")
    arts = client.get(f"/api/runs/{RUN}/artifacts/task_gen").json()["artifacts"]
    kinds = [a["kind"] for a in arts]
    assert "json" in kinds and "markdown" in kinds and "code" in kinds
    assert "Hello" in next(a for a in arts if a["kind"] == "markdown")["content"]


def test_unknown_canon_400(env):
    assert client.get(f"/api/runs/{RUN}/artifacts/bogus").status_code == 400


def test_no_artifact_stage_returns_empty(env):
    r = client.get(f"/api/runs/{RUN}/artifacts/gate")  # gate has no artifacts
    assert r.status_code == 200 and r.json()["artifacts"] == []
