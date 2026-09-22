"""`--from-task-json` / `seed_candidate`: score a recovered task, don't regenerate.

Rescue path for the failure seen on 2026-07-20: task generation succeeded, the
run died afterwards, and the finished task was thrown away. Seeding feeds that
recovered JSON back in at attempt 1 so evals / E2B gate / repos / gist /
Supabase all run without paying for generation a second time.
"""
import inspect
import json

import pytest
from click.testing import CliRunner

from flows.tech.stages.generate.cli import generate_tasks
from flows.tech.stages.generate.creator import create_task


def test_create_task_accepts_seed_candidate():
    assert "seed_candidate" in inspect.signature(create_task).parameters


def test_seed_candidate_defaults_to_none():
    """Default path must be untouched — no seeding unless explicitly asked for."""
    assert inspect.signature(create_task).parameters["seed_candidate"].default is None


def test_cli_exposes_from_task_json():
    names = {p.name for p in generate_tasks.params}
    assert "from_task_json" in names


def test_cli_rejects_json_that_is_not_a_task(tmp_path):
    """A JSON file lacking name/code_files must fail loudly, not half-run."""
    bad = tmp_path / "not_a_task.json"
    bad.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    result = CliRunner().invoke(generate_tasks, ["--from-task-json", str(bad)])
    assert result.exit_code != 0
    assert "not a task JSON" in result.output


def test_cli_rejects_missing_file():
    result = CliRunner().invoke(generate_tasks, ["--from-task-json", "/nope/missing.json"])
    assert result.exit_code != 0


@pytest.mark.parametrize("key", ["name", "code_files"])
def test_each_required_key_is_checked(tmp_path, key):
    payload = {"name": "t", "code_files": {"a.py": "x"}}
    payload.pop(key)
    p = tmp_path / "partial.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    result = CliRunner().invoke(generate_tasks, ["--from-task-json", str(p)])
    assert result.exit_code != 0
    assert key in result.output
