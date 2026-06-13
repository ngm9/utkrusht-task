"""run_pipeline._split_stage4_logs — focused e2b-gate / eval sub-logs.

The infra_assessor logger interleaves the E2B gate output and the LLM eval
results into 04_tasks.stderr. The extractor splits them into dedicated files
so the gate verdict and eval outcomes are easy to inspect.
"""
from pathlib import Path

import run_pipeline as rp


_SAMPLE_STDERR = "\n".join([
    "2026-06-10 17:00:00 - infra_assessor - INFO - Task generation attempt 1/3",
    "2026-06-10 17:00:01 - infra_assessor - INFO - some unrelated chatter about files",
    "2026-06-10 17:00:02 - infra_assessor - INFO - Running task evaluations",
    "2026-06-10 17:00:03 - infra_assessor - INFO - task eval parsed: pass=True blockers=0",
    "2026-06-10 17:00:04 - infra_assessor - INFO - code eval parsed: pass=False blockers=1",
    "2026-06-10 17:00:05 - infra_assessor - INFO - [e2b-gate] booting sandbox from utkrusht-python-ai...",
    "2026-06-10 17:00:06 - infra_assessor - INFO - [e2b-gate] run.sh... exit=1 (0.2s)",
    "2026-06-10 17:00:07 - infra_assessor - INFO - [e2b-gate] verdict: runsh_failed [FAIL]",
    "2026-06-10 17:00:08 - infra_assessor - WARNING - Attempt 2: sandbox gate FAILED (runsh_failed)",
    "2026-06-10 17:00:09 - infra_assessor - INFO - { big task json dump that must NOT match }",
])


def test_split_writes_focused_logs(tmp_path: Path):
    (tmp_path / "04_tasks.stderr").write_text(_SAMPLE_STDERR, encoding="utf-8")

    written = rp._split_stage4_logs(tmp_path)
    assert set(written) == {"04_tasks.e2b_gate.log", "04_tasks.evals.log"}

    gate = (tmp_path / "04_tasks.e2b_gate.log").read_text().splitlines()
    assert any("[e2b-gate] verdict: runsh_failed" in ln for ln in gate)
    assert any("sandbox gate FAILED" in ln for ln in gate)
    # eval / unrelated lines must NOT leak into the gate log
    assert not any("task eval parsed" in ln for ln in gate)
    assert not any("unrelated chatter" in ln for ln in gate)

    evals = (tmp_path / "04_tasks.evals.log").read_text().splitlines()
    assert any("task eval parsed: pass=True" in ln for ln in evals)
    assert any("code eval parsed: pass=False" in ln for ln in evals)
    assert any("Task generation attempt 1/3" in ln for ln in evals)
    # gate / noise lines must NOT leak into the eval log
    assert not any("[e2b-gate]" in ln for ln in evals)
    assert not any("big task json dump" in ln for ln in evals)


def test_split_no_stderr_is_noop(tmp_path: Path):
    # No 04_tasks.stderr (e.g. stage 4 never reached) → nothing written, no error.
    assert rp._split_stage4_logs(tmp_path) == []
    assert not (tmp_path / "04_tasks.e2b_gate.log").exists()


def test_run_stage_enables_tracing_for_llm_stages_only(tmp_path: Path, monkeypatch):
    """_run_stage forces PIPELINE_TRACING_ENABLED='1' for the LLM-bearing stages
    (input_files / scenarios / prompt / tasks) and '0' for preflight — forced
    explicitly so an enabled parent-shell value can't leak into preflight — and
    passes the inherited TRACE_RUN_ID through to each child.
    """
    captured: dict = {}

    class _Proc:
        returncode = 0

    def _fake_run(cmd, stdout=None, stderr=None, cwd=None, env=None):
        captured["env"] = dict(env or {})
        return _Proc()

    monkeypatch.setattr(rp.subprocess, "run", _fake_run)
    monkeypatch.setenv("TRACE_RUN_ID", "20260611T000000Z")

    for label in ("01_input_files", "02_scenarios", "03_prompt", "04_tasks"):
        rp._run_stage(tmp_path, label, ["true"])
        assert captured["env"]["PIPELINE_TRACING_ENABLED"] == "1", label
        assert captured["env"]["TRACE_RUN_ID"] == "20260611T000000Z"  # inherited

    rp._run_stage(tmp_path, "00_preflight", ["true"])
    assert captured["env"]["PIPELINE_TRACING_ENABLED"] == "0"  # no LLM calls: off


def test_run_stage_streams_sublogs_live(tmp_path: Path):
    """_run_stage(live_split=...) fans the stage's stderr into focused sub-logs
    AS it runs (not via the post-hoc split): the eval + e2b-gate lines land in
    their files, noise is excluded, and the full stderr is still captured."""
    import sys

    script = (
        "import sys\n"
        "print('t - infra_assessor - INFO - Running task evaluations', file=sys.stderr)\n"
        "print('t - infra_assessor - INFO - [e2b-gate] booting sandbox', file=sys.stderr)\n"
        "print('t - infra_assessor - INFO - unrelated chatter line', file=sys.stderr)\n"
    )
    rec = rp._run_stage(
        tmp_path, "04_tasks", [sys.executable, "-c", script],
        live_split=[
            ("04_tasks.e2b_gate.log", rp._E2B_GATE_MARKERS),
            ("04_tasks.evals.log", rp._EVAL_MARKERS),
        ],
    )
    assert rec["exit_code"] == 0
    # Full stderr still captured (incl. the noise line).
    assert "unrelated chatter line" in (tmp_path / "04_tasks.stderr").read_text()
    # Sub-logs were written by the live stream, correctly filtered.
    evals = (tmp_path / "04_tasks.evals.log").read_text()
    assert "Running task evaluations" in evals
    assert "[e2b-gate]" not in evals and "unrelated chatter" not in evals
    gate = (tmp_path / "04_tasks.e2b_gate.log").read_text()
    assert "[e2b-gate] booting sandbox" in gate
    assert "Running task evaluations" not in gate


def test_split_only_writes_files_with_matches(tmp_path: Path):
    # stderr with eval lines but no gate lines → only the evals log is written.
    (tmp_path / "04_tasks.stderr").write_text(
        "2026-06-10 - infra_assessor - INFO - task eval parsed: pass=True blockers=0\n",
        encoding="utf-8",
    )
    written = rp._split_stage4_logs(tmp_path)
    assert written == ["04_tasks.evals.log"]
    assert not (tmp_path / "04_tasks.e2b_gate.log").exists()
