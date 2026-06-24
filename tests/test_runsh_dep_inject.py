"""Deterministic run.sh dependency-install injection (2026-06-19).

The E2B gate doesn't pre-install a task's third-party deps; if run.sh imports
before `pip install`, readiness dies with ModuleNotFoundError (psycopg/litellm)
→ gate fail → expensive Opus retry that the LLM can't reliably fix. The creator
injects the install deterministically so tasks pass on attempt 1.
"""

from __future__ import annotations


def test_injects_pip_install_after_cd_before_import():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "psycopg[binary]\nlitellm\n",
        "run.sh": "#!/usr/bin/env bash\nset -euo pipefail\ncd /root/task\n"
                  "docker compose up -d\npython -m agent --selfcheck\necho ready\n",
    }
    _ensure_runsh_installs_deps(cf)
    rs = cf["run.sh"]
    assert "pip install -q -r requirements.txt" in rs
    # installed BEFORE the import/selfcheck...
    assert rs.index("pip install") < rs.index("python -m agent --selfcheck")
    # ...and AFTER the cd (so requirements.txt is in cwd)
    assert rs.index("cd /root/task") < rs.index("pip install")


def test_no_double_inject_when_already_present():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "x\n",
        "run.sh": "#!/usr/bin/env bash\npip install -q -r requirements.txt\npython -m agent\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert cf["run.sh"].count("pip install") == 1


def test_skips_when_no_requirements_file():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {"run.sh": "#!/usr/bin/env bash\npython -m agent\n"}
    _ensure_runsh_installs_deps(cf)
    assert "pip install" not in cf["run.sh"]


def test_handles_subdir_runsh_key():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "x\n",
        "repo/run.sh": "#!/usr/bin/env bash\ncd /root/task\npython -m agent\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "pip install -q -r requirements.txt" in cf["repo/run.sh"]


def test_noop_when_no_runsh():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {"requirements.txt": "x\n"}
    _ensure_runsh_installs_deps(cf)  # must not raise
    assert "run.sh" not in cf


# --- broadened "already installs" detection (the #2 follow-up) ------------------

def test_no_double_inject_for_python_dash_m_pip():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "x\n",
        "run.sh": "#!/usr/bin/env bash\ncd /root/task\npython -m pip install -r requirements.txt\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert cf["run.sh"].count("pip install") == 1


def test_no_double_inject_for_uv_pip():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "x\n",
        "run.sh": "#!/usr/bin/env bash\nuv pip install -r requirements.txt\npython -m app\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert cf["run.sh"].count("pip install") == 1


# --- runtime-agnostic injection (Node / Go / Rust) ------------------------------

def test_injects_npm_for_node():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "package.json": '{"name":"x"}',
        "run.sh": "#!/usr/bin/env bash\ncd /root/task\nnode server.js\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "npm install" in cf["run.sh"]
    assert cf["run.sh"].index("npm install") < cf["run.sh"].index("node server.js")


def test_no_double_inject_when_npm_ci_present():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "package.json": "{}",
        "run.sh": "#!/usr/bin/env bash\nnpm ci\nnode server.js\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "npm install" not in cf["run.sh"]


def test_injects_go_mod_download():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "go.mod": "module x\n",
        "run.sh": "#!/usr/bin/env bash\ncd /root/task\n./bootstrap.sh\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "go mod download" in cf["run.sh"]


def test_no_double_inject_when_go_build_present():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "go.mod": "module x\n",
        "run.sh": "#!/usr/bin/env bash\ngo build ./...\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "go mod download" not in cf["run.sh"]


def test_injects_cargo_fetch():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "Cargo.toml": "[package]\nname='x'\n",
        "run.sh": "#!/usr/bin/env bash\ncd /root/task\ndocker compose up -d\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "cargo fetch" in cf["run.sh"]


def test_no_double_inject_when_cargo_build_present():
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "Cargo.toml": "[package]\n",
        "run.sh": "#!/usr/bin/env bash\ncargo build --release\n",
    }
    _ensure_runsh_installs_deps(cf)
    assert "cargo fetch" not in cf["run.sh"]


def test_only_present_runtime_is_bootstrapped():
    """A Python task must not get npm/go/cargo lines."""
    from generators.task.creator import _ensure_runsh_installs_deps
    cf = {
        "requirements.txt": "x\n",
        "run.sh": "#!/usr/bin/env bash\ncd /root/task\npython -m app\n",
    }
    _ensure_runsh_installs_deps(cf)
    rs = cf["run.sh"]
    assert "pip install -q -r requirements.txt" in rs
    assert "npm install" not in rs and "go mod download" not in rs and "cargo fetch" not in rs
