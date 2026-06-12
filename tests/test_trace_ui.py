"""Hermetic tests for trace_ui.tailer (no real server, no network).

Covers the three required behaviours:

* ``resolve_run_dir`` rejects path traversal and absolute paths.
* ``list_runs`` reads a fake ``.task_agent_runs`` layout (tmp + monkeypatched
  RUNS_DIR).
* ``tail_file`` yields lines as they are appended to a file.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from trace_ui import tailer
from trace_ui.tailer import (
    InvalidRunIdError,
    RunNotFoundError,
    list_runs,
    resolve_run_dir,
    tail_file,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture()
def fake_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point tailer.RUNS_DIR at a tmp ``.task_agent_runs`` and return it."""
    runs_dir = tmp_path / ".task_agent_runs"
    runs_dir.mkdir()
    monkeypatch.setattr(tailer, "RUNS_DIR", runs_dir)
    return runs_dir


def _make_run(
    runs_dir: Path,
    run_id: str,
    combo: str = "python_redis_intermediate",
    *,
    summary_status: str | None = None,
    manifest: dict | None = None,
) -> Path:
    """Build a minimal but realistic fake run dir, return its path."""
    run_dir = runs_dir / run_id
    combo_dir = run_dir / combo
    combo_dir.mkdir(parents=True)
    (combo_dir / "04_tasks.stdout").write_text("hello\n", encoding="utf-8")
    if summary_status is not None:
        (combo_dir / "summary.json").write_text(
            json.dumps({"status": summary_status}), encoding="utf-8"
        )
    if manifest is not None:
        traces = run_dir / "traces"
        traces.mkdir()
        (traces / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return run_dir


# ----------------------------------------------------------------------
# resolve_run_dir — security boundary
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_id",
    [
        "../etc",
        "../../etc/passwd",
        "/etc/passwd",
        "foo/bar",
        "..",
        "a b",          # whitespace
        "x;rm -rf",     # shell-ish
        "",             # empty
        "run-‮",   # non-ascii control
    ],
)
def test_resolve_run_dir_rejects_bad_ids(fake_runs: Path, bad_id: str) -> None:
    with pytest.raises(InvalidRunIdError):
        resolve_run_dir(bad_id)


def test_resolve_run_dir_rejects_absolute_path(fake_runs: Path) -> None:
    # An absolute path string must be rejected (illegal chars / not a bare name).
    with pytest.raises(InvalidRunIdError):
        resolve_run_dir(str(fake_runs / "run-x"))


def test_resolve_run_dir_unknown_id_raises_not_found(fake_runs: Path) -> None:
    # A syntactically valid id with no directory raises RunNotFoundError.
    with pytest.raises(RunNotFoundError):
        resolve_run_dir("run-20990101T000000Z")


def test_resolve_run_dir_accepts_valid_existing_run(fake_runs: Path) -> None:
    run_dir = _make_run(fake_runs, "run-20260612T040014Z")
    resolved = resolve_run_dir("run-20260612T040014Z")
    assert resolved == run_dir.resolve()
    assert resolved.is_dir()


# ----------------------------------------------------------------------
# list_runs
# ----------------------------------------------------------------------

def test_list_runs_empty_when_no_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tailer, "RUNS_DIR", tmp_path / "does_not_exist")
    assert list_runs() == []


def test_list_runs_reads_fake_layout(fake_runs: Path) -> None:
    _make_run(
        fake_runs,
        "run-20260612T040014Z",
        combo="reactjs_advanced",
        summary_status="COMPLETED",
        manifest={"task_id": "abc-123", "task_name": "React thing"},
    )
    _make_run(fake_runs, "run-20260101T000000Z")  # no summary -> running
    # A non-run dir must be ignored.
    (fake_runs / "scratch").mkdir()

    runs = list_runs()
    assert {r["run_id"] for r in runs} == {
        "run-20260612T040014Z",
        "run-20260101T000000Z",
    }

    by_id = {r["run_id"]: r for r in runs}
    completed = by_id["run-20260612T040014Z"]
    assert completed["combo"] == "reactjs_advanced"
    assert completed["status"] == "COMPLETED"
    assert completed["task_id"] == "abc-123"
    assert completed["task_name"] == "React thing"

    running = by_id["run-20260101T000000Z"]
    assert running["status"] == "running"
    assert running["task_id"] is None


def test_list_runs_sorted_newest_first(fake_runs: Path) -> None:
    import os
    import time

    old = _make_run(fake_runs, "run-old")
    new = _make_run(fake_runs, "run-new")
    # Force a deterministic mtime ordering (old < new).
    now = time.time()
    os.utime(old, (now - 100, now - 100))
    os.utime(new, (now, now))

    ids = [r["run_id"] for r in list_runs()]
    assert ids.index("run-new") < ids.index("run-old")


def test_list_runs_orders_by_timestamp_not_mtime(fake_runs: Path) -> None:
    """A run with an OLDER embedded timestamp but a FRESHER dir mtime (e.g. an
    S3 log backfill re-touched it) must still sort below the newer-timestamp
    run — ordering follows the run name, not mtime."""
    import os
    import time

    older = _make_run(fake_runs, "run-20260515T084400Z")
    newer = _make_run(fake_runs, "run-20260612T042731Z")
    # Invert mtime vs timestamp: the OLD-timestamp dir is touched most recently.
    now = time.time()
    os.utime(newer, (now - 100, now - 100))
    os.utime(older, (now, now))

    ids = [r["run_id"] for r in list_runs()]
    assert ids.index("run-20260612T042731Z") < ids.index("run-20260515T084400Z")


# ----------------------------------------------------------------------
# tail_file
# ----------------------------------------------------------------------

def test_tail_file_yields_appended_lines(tmp_path: Path) -> None:
    log = tmp_path / "live.log"
    log.write_text("line1\nline2\n", encoding="utf-8")

    async def scenario() -> list[str]:
        collected: list[str] = []
        agen = tail_file(log, from_start=True, poll_interval=0.02)

        async def drain(n: int) -> None:
            for _ in range(n):
                collected.append(await asyncio.wait_for(agen.__anext__(), timeout=2.0))

        # Existing two lines come through first.
        await drain(2)
        # Append a third line; the tailer must pick it up on the next poll.
        with log.open("a", encoding="utf-8") as fh:
            fh.write("line3\n")
        await drain(1)
        await agen.aclose()
        return collected

    result = asyncio.run(scenario())
    assert result == ["line1", "line2", "line3"]


def test_tail_file_waits_for_missing_file(tmp_path: Path) -> None:
    log = tmp_path / "later.log"  # does not exist yet

    async def scenario() -> list[str]:
        agen = tail_file(log, from_start=True, poll_interval=0.02)
        anext = asyncio.ensure_future(agen.__anext__())
        # Let the tailer spin a few times against a missing file.
        await asyncio.sleep(0.1)
        assert not anext.done()
        # Now create the file with content.
        log.write_text("appeared\n", encoding="utf-8")
        line = await asyncio.wait_for(anext, timeout=2.0)
        await agen.aclose()
        return [line]

    assert asyncio.run(scenario()) == ["appeared"]


def test_tail_file_from_end_skips_existing(tmp_path: Path) -> None:
    log = tmp_path / "tail.log"
    log.write_text("old1\nold2\n", encoding="utf-8")

    async def scenario() -> list[str]:
        agen = tail_file(log, from_start=False, poll_interval=0.02)
        anext = asyncio.ensure_future(agen.__anext__())
        await asyncio.sleep(0.1)  # position at EOF, skipping old lines
        with log.open("a", encoding="utf-8") as fh:
            fh.write("new1\n")
        line = await asyncio.wait_for(anext, timeout=2.0)
        await agen.aclose()
        return [line]

    assert asyncio.run(scenario()) == ["new1"]


# ----------------------------------------------------------------------
# server: ordered replay helpers + result/cost parsing
# ----------------------------------------------------------------------

def test_read_complete_lines_handles_partial_and_offset(tmp_path: Path) -> None:
    from trace_ui.server import _read_complete_lines

    f = tmp_path / "x.log"
    f.write_text("a\nb\npartial", encoding="utf-8")  # trailing line: no newline yet
    lines, off = _read_complete_lines(f, 0)
    assert lines == ["a", "b"]
    assert off == len("a\nb\n")  # offset sits just past the last newline
    with f.open("a", encoding="utf-8") as fh:
        fh.write(" done\nc\n")
    lines2, _ = _read_complete_lines(f, off)
    assert lines2 == ["partial done", "c"]


def test_log_files_in_order_sorts_by_stage(tmp_path: Path) -> None:
    from trace_ui.server import _log_files_in_order

    combo = tmp_path / "combo"
    combo.mkdir()
    for name in (
        "04_tasks.stdout", "01_input_files.stderr", "02_scenarios.stdout",
        "03_prompt.stderr", "04_tasks.stderr", "00_preflight.stdout",
    ):
        (combo / name).write_text("x\n", encoding="utf-8")
    assert [p.name for p in _log_files_in_order(combo)] == [
        "00_preflight.stdout", "01_input_files.stderr", "02_scenarios.stdout",
        "03_prompt.stderr", "04_tasks.stderr", "04_tasks.stdout",
    ]


def test_parse_result_extracts_links_and_ids(tmp_path: Path) -> None:
    from trace_ui.server import _parse_result

    run_dir = tmp_path / "run-20260101T000000Z"
    combo = run_dir / "python_basic"
    combo.mkdir(parents=True)
    (run_dir / "traces").mkdir()
    (run_dir / "traces" / "manifest.json").write_text(json.dumps({
        "task_id": "f8109931-cdbe-4ac1-a5d6-014d9e5410d2",
        "task_name": "fix-thing", "outcome": "created",
        "env": "dev", "competencies": ["Python"],
    }), encoding="utf-8")
    (combo / "summary.json").write_text(json.dumps({
        "status": "COMPLETED", "task_outcome": "TASK CREATED",
        "proficiency": "BASIC", "total_duration_s": 564.1,
    }), encoding="utf-8")
    (combo / "04_tasks.stdout").write_text(
        "Gist created: https://gist.github.com/ngm9/abc123\n"
        "Template repo https://github.com/UtkrushtApps/shipment-csv-validator .\n",
        encoding="utf-8",
    )
    res = _parse_result(run_dir)
    assert res["task_id"] == "f8109931-cdbe-4ac1-a5d6-014d9e5410d2"
    assert res["task_name"] == "fix-thing"
    assert res["status"] == "COMPLETED" and res["task_outcome"] == "TASK CREATED"
    assert res["duration_s"] == 564.1 and res["proficiency"] == "BASIC"
    urls = {l["url"] for l in res["links"]}
    assert "https://gist.github.com/ngm9/abc123" in urls
    assert "https://github.com/UtkrushtApps/shipment-csv-validator" in urls


def test_compute_cost_by_stage(tmp_path: Path) -> None:
    from trace_ui.server import _compute_cost

    run = tmp_path / "run-x"
    tr = run / "traces"
    tr.mkdir(parents=True)
    (tr / "llm_calls.jsonl").write_text(
        json.dumps({"stage": "task_gen", "model": "claude-sonnet-4-6",
                    "usage": {"input_tokens": 1_000_000, "output_tokens": 0}}) + "\n"
        + json.dumps({"stage": "scenarios", "model": "gpt-5.4",
                      "usage": {"input_tokens": 0, "output_tokens": 1_000_000}}) + "\n",
        encoding="utf-8",
    )
    (tr / "stages.jsonl").write_text(
        json.dumps({"stage": "task_gen", "duration_ms": 5000}) + "\n", encoding="utf-8"
    )
    c = _compute_cost(run)
    # claude-sonnet input 3.0/M × 1M = 3.0 ; gpt-5.4 output 2.0/M × 1M = 2.0
    assert c["total_usd"] == 5.0
    assert c["total_tokens"] == 2_000_000
    by = {r["stage"]: r for r in c["by_stage"]}
    assert by["task_gen"]["usd"] == 3.0 and by["task_gen"]["duration_ms"] == 5000
    assert by["scenarios"]["usd"] == 2.0 and by["scenarios"]["duration_ms"] is None
    # rows follow canonical timeline order (scenarios before task_gen)
    assert [r["stage"] for r in c["by_stage"]] == ["scenarios", "task_gen"]
    assert _compute_cost(tmp_path / "nope") is None  # no traces dir → None


# ----------------------------------------------------------------------
# launcher: /api/competencies + POST /api/runs
# ----------------------------------------------------------------------

def test_list_competencies_dedup_and_sort(monkeypatch: pytest.MonkeyPatch) -> None:
    import types as _types
    import supabase as supabase_mod
    from trace_ui import server as srv

    class _Q:
        def select(self, *a, **k): return self
        def execute(self):
            return _types.SimpleNamespace(data=[
                {"name": "Redis", "proficiency": "BASIC"},
                {"name": "Python", "proficiency": "INTERMEDIATE"},
                {"name": "Python", "proficiency": "INTERMEDIATE"},   # dup → collapsed
                {"name": "", "proficiency": "BASIC"},                # empty → skipped
            ])

    class _Client:
        def table(self, name): assert name == "competencies"; return _Q()

    monkeypatch.setattr(supabase_mod, "create_client", lambda url, key: _Client())
    monkeypatch.setenv("SUPABASE_URL_APTITUDETESTSDEV", "u")
    monkeypatch.setenv("SUPABASE_API_KEY_APTITUDETESTSDEV", "k")

    out = srv._list_competencies("dev")
    names = [c["name"] for c in out]
    assert names.count("Python") == 1          # dup collapsed
    assert "" not in names                     # empty name skipped
    assert out == sorted(out, key=lambda r: (r["name"].lower(), r["proficiency"]))


def test_launch_validates_and_spawns(monkeypatch: pytest.MonkeyPatch) -> None:
    import json as _json
    import sys as _sys
    from fastapi import HTTPException
    from trace_ui import server as srv
    from trace_ui.server import RunRequest

    captured: dict = {}
    monkeypatch.setattr(srv, "_spawn_pipeline", lambda cmd: captured.update(cmd=cmd))

    resp = srv.api_launch(RunRequest(names=["Python", "Redis"], proficiency="basic", count=3, env="dev"))
    body = _json.loads(bytes(resp.body).decode())
    assert body["ok"] and body["proficiency"] == "BASIC" and body["count"] == 3
    assert captured["cmd"][:6] == [_sys.executable, "run_pipeline.py", "-p", "BASIC", "--env", "dev"]
    assert captured["cmd"].count("-n") == 2 and "Python" in captured["cmd"] and "Redis" in captured["cmd"]

    for bad in (
        RunRequest(names=["X"], proficiency="WIZARD"),     # bad proficiency
        RunRequest(names=["  "], proficiency="BASIC"),     # empty after strip
        RunRequest(names=["bad\nname"], proficiency="BASIC"),  # control char
    ):
        with pytest.raises(HTTPException) as ei:
            srv.api_launch(bad)
        assert ei.value.status_code == 400

    # count out of range is clamped to the default (2)
    resp2 = srv.api_launch(RunRequest(names=["X"], proficiency="BASIC", count=999))
    assert _json.loads(bytes(resp2.body).decode())["count"] == 2
