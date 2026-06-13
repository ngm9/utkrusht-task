"""Regression guard for the trace_ui log-level classifier (taxonomy).

The classifier lives in ``trace_ui/static/index.html`` as ``LOG_RULES`` +
``classifyLine`` — an ordered, first-match-wins set of regexes that color each
live log line by OUTCOME (pass→green, fail→red, warn→amber, info/debug→neutral)
rather than by stream. It is load-bearing: the whole pipeline logs INFO to
stderr, so mis-ordering a rule would repaint healthy runs red (the bug this
replaced) or, worse, paint a real failure green.

This test extracts the actual JS from the HTML and runs it under ``node``
against representative REAL log lines from this repo, so the taxonomy can't
drift silently. It skips if node is unavailable (e.g. minimal CI image).
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess

import pytest

_HTML = (
    pathlib.Path(__file__).resolve().parent.parent
    / "trace_ui" / "static" / "index.html"
)

# (raw log line, expected level). Grounded in real .task_agent_runs output.
CASES: list[tuple[str, str]] = [
    ("x - infra_assessor - INFO - [e2b-gate] verdict: runsh_failed [FAIL] — run.sh exited 1", "error"),
    ("x - infra_assessor - INFO - [e2b-gate] verdict: ready [PASS] — run.sh exited 0", "ok"),
    ("x - infra_assessor - INFO - [e2b-gate] verdict: infra_error [SKIP] — sandbox boot failed", "warn"),
    ("x - infra_assessor - INFO - code eval parsed: pass=False blockers=1 (len=2212)", "error"),
    ("x - infra_assessor - INFO - task eval parsed: pass=True blockers=0 (len=1680)", "ok"),
    ('x - infra_assessor - INFO - Raw LLM code eval response: {"pass": false, "blocking_issues": [', "error"),
    ('x - infra_assessor - INFO - Raw LLM task eval response: {"pass": true, "blocking_issues": [', "ok"),
    ("x - infra_assessor - INFO - [e2b-gate] run.sh… exit=1 (0.2s)", "error"),
    ("x - infra_assessor - INFO - [e2b-gate] run.sh… exit=0 (30.9s)", "ok"),
    ("x - infra_assessor - WARNING - Attempt 3: sandbox gate FAILED (runsh_failed)", "error"),
    ("x - infra_assessor - ERROR - Traceback (most recent call last):", "error"),
    ('  File "/app/foo.py", line 42, in run', "error"),
    ("x - infra_assessor - ERROR - Failed to parse JSON from response.output_text", "error"),
    ("x - infra_assessor - WARNING - resolve_plan: cache lookup failed", "warn"),
    ("x - infra_assessor - INFO - Successfully loaded 1 competencies", "ok"),
    ("x - infra_assessor - INFO - generating draft task for Python", "info"),
    ("[12:37:36] >>> 04_tasks :: .venv/bin/python multiagent.py generate_tasks", "info"),
    ("x - infra_assessor - INFO - Attempt 2: evals + gate passed (quality applied) - proceeding to storage", "ok"),
    ("x - infra_assessor - INFO - [e2b-gate]   |  897d797d2723 Extracting 1B", "debug"),
    ("## My Understanding", "info"),
]


def _extract_classifier() -> str:
    html = _HTML.read_text(encoding="utf-8")
    m = re.search(
        r"(const LOG_RULES = \[.*?\nfunction classifyLine\(line\) \{.*?\n\})",
        html,
        re.S,
    )
    assert m, "could not locate LOG_RULES / classifyLine in index.html"
    return m.group(1)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_log_classifier_matches_real_lines(tmp_path: pathlib.Path) -> None:
    runner = tmp_path / "run.js"
    runner.write_text(
        _extract_classifier()
        + "\nconst cases = JSON.parse(process.argv[2]);\n"
        + "process.stdout.write(JSON.stringify(cases.map(([line]) => classifyLine(line))));\n",
        encoding="utf-8",
    )
    res = subprocess.run(
        ["node", str(runner), json.dumps(CASES)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert res.returncode == 0, f"node failed: {res.stderr}"
    got = json.loads(res.stdout)
    mism = [
        (line, want, g) for (line, want), g in zip(CASES, got) if want != g
    ]
    assert not mism, "misclassified lines:\n" + "\n".join(
        f"  want {w!r} got {g!r}: {line[:80]}" for line, w, g in mism
    )
