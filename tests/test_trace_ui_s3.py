"""trace_ui S3 fallback: list completed runs from S3, materialize a run's files
into the local cache dir (so existing endpoints serve it), and merge S3 runs
into /api/runs (local wins on collision).
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from trace_ui import s3_store, tailer
from trace_ui.server import app

_PREFIX = "traces/dt=2026-06-13/combo=nodejs_advanced/run=20260613T060041Z/"
_OBJECTS = {
    _PREFIX + "manifest.json": '{"task_id": "abc", "task_name": "t"}',
    _PREFIX + "llm_calls.jsonl": '{"x": 1}\n',
    _PREFIX + "stages.jsonl": '{"stage": "prompt"}\n',
    _PREFIX + "logs/01_input_files.stdout": "hello input\n",
    _PREFIX + "logs/04_tasks.stderr": "task log\n",
    _PREFIX + "logs/summary.json": '{"status": "COMPLETED"}',
}


class _FakePaginator:
    def __init__(self, objects):
        self.objects = objects

    def paginate(self, Bucket=None, Prefix="", Delimiter=None):
        if Delimiter == "/":
            prefixes = set()
            for k in self.objects:
                if k.startswith(Prefix) and "/" in k[len(Prefix):]:
                    prefixes.add(Prefix + k[len(Prefix):].split("/", 1)[0] + "/")
            yield {"CommonPrefixes": [{"Prefix": p} for p in sorted(prefixes)]}
        else:
            yield {"Contents": [{"Key": k} for k in self.objects if k.startswith(Prefix)]}


class _FakeS3:
    def __init__(self, objects):
        self.objects = objects

    def get_paginator(self, name):
        return _FakePaginator(self.objects)

    def download_file(self, bucket, key, dest):
        Path(dest).write_text(self.objects[key], encoding="utf-8")


@pytest.fixture
def s3_on(monkeypatch):
    monkeypatch.setenv("TRACE_S3_BUCKET", "test-bucket")
    monkeypatch.setattr(s3_store, "_client", lambda: _FakeS3(_OBJECTS))
    s3_store._index_cache["at"] = 0.0
    s3_store._index_cache["data"] = {}


def test_list_s3_runs(s3_on):
    runs = s3_store.list_s3_runs()
    assert len(runs) == 1
    r = runs[0]
    assert r["run_id"] == "run-20260613T060041Z"
    assert r["combo"] == "nodejs_advanced"
    assert r["status"] == "completed" and r["source"] == "s3"
    assert r["started"] > 0


def test_materialize_run(s3_on, tmp_path):
    runs = tmp_path / ".task_agent_runs"
    runs.mkdir()
    assert s3_store.materialize_run("run-20260613T060041Z", runs) is True
    rd = runs / "run-20260613T060041Z"
    assert (rd / "traces" / "manifest.json").read_text() == _OBJECTS[_PREFIX + "manifest.json"]
    assert (rd / "traces" / "llm_calls.jsonl").exists()
    assert (rd / "nodejs_advanced" / "01_input_files.stdout").read_text() == "hello input\n"
    assert (rd / "nodejs_advanced" / "summary.json").exists()
    # idempotent
    assert s3_store.materialize_run("run-20260613T060041Z", runs) is True


def test_materialize_unknown_run(s3_on, tmp_path):
    runs = tmp_path / ".task_agent_runs"
    runs.mkdir()
    assert s3_store.materialize_run("run-19990101T000000Z", runs) is False


def test_disabled_when_no_bucket(monkeypatch):
    monkeypatch.delenv("TRACE_S3_BUCKET", raising=False)
    assert s3_store.s3_enabled() is False
    assert s3_store.list_s3_runs() == []


def test_api_runs_merges_and_dedupes(monkeypatch, tmp_path):
    runs = tmp_path / ".task_agent_runs"
    (runs / "run-20260101T000000Z" / "combo").mkdir(parents=True)  # one local run
    monkeypatch.setattr(tailer, "RUNS_DIR", runs)
    monkeypatch.setattr(s3_store, "list_s3_runs", lambda: [
        {"run_id": "run-20260202T000000Z", "combo": "x", "status": "completed", "started": 2, "source": "s3"},
        {"run_id": "run-20260101T000000Z", "combo": "dup", "status": "completed", "started": 1, "source": "s3"},
    ])
    data = TestClient(app).get("/api/runs").json()
    ids = [r["run_id"] for r in data]
    assert ids == ["run-20260202T000000Z", "run-20260101T000000Z"]  # newest first, deduped
    local = next(r for r in data if r["run_id"] == "run-20260101T000000Z")
    assert local.get("source") != "s3"  # local won the collision
