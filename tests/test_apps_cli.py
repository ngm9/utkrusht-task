"""Guard tests for the consolidated apps/cli entrypoint (Task 6)."""
import os
import subprocess
import sys

# The generate stage constructs an OpenAI client at import time; a dummy key lets
# `--help` render without a real credential (no API call happens for --help).
_ENV = {**os.environ, "OPENAI_API_KEY": "sk-test-dummy", "PORTKEY_API_KEY": "test"}


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", *args], capture_output=True, text=True, env=_ENV,
    )


def test_apps_cli_lists_generate_and_gist():
    out = _run("apps.cli", "--help")
    assert out.returncode == 0, out.stderr
    assert "generate_tasks" in out.stdout
    assert "gist" in out.stdout


def test_generate_stage_runs_as_module():
    """Stage-4 target `python -m flows.tech.stages.generate` must be runnable."""
    out = _run("flows.tech.stages.generate", "--help")
    assert out.returncode == 0, out.stderr
