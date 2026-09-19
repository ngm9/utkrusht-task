"""is_shared_infra_required determination + the audit's template/infra rule.

Two coupled defects, both surfaced by the 2026-07-20 agent tasks:

1. `is_shared_infra_required` was `has_shared_infra_files` (docker files only).
   The python-ai base image already ships postgres + redis, so a task can need
   those shared services without a repo docker-compose — docker-only
   under-detects. `needs_shared_infra` widens to the other infra-plumbing
   markers while keeping pure-runtime tasks non-infra.

2. The audit coupled template_id to the infra flag (False ⇒ template_id must be
   null). But template_id is the base runtime image every deployable task
   needs; nulling it would make the task un-deployable. They are orthogonal.
"""
import importlib.util
import pathlib

from infra.utils import has_shared_infra_files, needs_shared_infra


# ---- Fix 2: needs_shared_infra ----

def test_docker_still_counts_as_infra():
    assert needs_shared_infra({"docker-compose.yml": "services:", "app.py": "x"})


def test_sql_init_counts_even_without_docker():
    """The key case: talks to the template's postgres via seeded SQL, no compose."""
    files = {"init_database.sql": "CREATE TABLE t(...);", "app/main.py": "x"}
    assert not has_shared_infra_files(files), "no docker — old check says non-infra"
    assert needs_shared_infra(files), "but it declares a DB it seeds — infra"


def test_kill_sh_counts():
    assert needs_shared_infra({"kill.sh": "docker compose down", "app.py": "x"})


def test_pure_python_agent_is_not_infra():
    """redact-pii shape: JSONL fixture + pytest, no service. Must stay non-infra."""
    files = {
        "agent/redaction.py": "...",
        "fixtures/subscriptions.jsonl": "{}",
        "invariants/test_x.py": "...",
        "run.sh": "pip install -r requirements.txt\npython -m agent --selfcheck",
        "requirements.txt": "pydantic",
    }
    assert not needs_shared_infra(files)


def test_nested_files_shape_supported():
    assert needs_shared_infra({"files": {"schema.sql": "CREATE ..."}})


# ---- Fix 1: audit decouples template_id from the infra flag ----

def _load_audit():
    p = (pathlib.Path(__file__).parents[1]
         / ".claude/skills/task-audit/scripts/task_audit.py")
    spec = importlib.util.spec_from_file_location("task_audit", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KNOWN = {"utkrusht-python-ai", "utkrusht-go-base"}


def test_non_infra_with_base_template_is_ok():
    """The false positive: non-infra task carrying its base runtime image."""
    audit = _load_audit()
    status, _ = audit.check_infra_template(
        {"is_shared_infra_required": False, "template_id": "utkrusht-python-ai"}, KNOWN)
    assert status == audit.PASS


def test_infra_without_template_still_fails():
    audit = _load_audit()
    status, msg = audit.check_infra_template(
        {"is_shared_infra_required": True, "template_id": None}, KNOWN)
    assert status == audit.FAIL and "null" in msg


def test_dangling_template_still_fails_either_way():
    audit = _load_audit()
    for needs in (True, False):
        status, msg = audit.check_infra_template(
            {"is_shared_infra_required": needs, "template_id": "utkrusht-ghost"}, KNOWN)
        assert status == audit.FAIL and "dangling" in msg


def test_non_infra_with_no_template_is_ok():
    audit = _load_audit()
    status, _ = audit.check_infra_template(
        {"is_shared_infra_required": False, "template_id": None}, KNOWN)
    assert status == audit.PASS
