"""TaskRuntime model — fields, defaults, JSON round-trip."""
import pytest
from pydantic import ValidationError

from infra.classifier.runtime import TaskRuntime, Competency


def test_task_runtime_minimum_fields():
    rt = TaskRuntime(runtime="python", kind="script")
    assert rt.runtime == "python"
    assert rt.kind == "script"
    assert rt.frameworks == []
    assert rt.datastores == []
    assert rt.messaging == []
    assert rt.needs_browser is False


def test_task_runtime_full():
    rt = TaskRuntime(
        runtime="python",
        frameworks=["fastapi"],
        datastores=["postgres"],
        messaging=["kafka"],
        needs_browser=False,
        kind="app",
    )
    assert rt.runtime == "python"
    assert rt.kind == "app"
    assert rt.frameworks == ["fastapi"]
    assert rt.datastores == ["postgres"]
    assert rt.messaging == ["kafka"]
    assert rt.needs_browser is False


def test_task_runtime_invalid_runtime_rejected():
    with pytest.raises(ValidationError):
        TaskRuntime(runtime="cobol", kind="script")


def test_task_runtime_invalid_kind_rejected():
    with pytest.raises(ValidationError):
        TaskRuntime(runtime="python", kind="microservice")


def test_task_runtime_json_round_trip():
    original = TaskRuntime(
        runtime="node", frameworks=["express", "react"],
        datastores=["mongo"], kind="app",
    )
    serialised = original.model_dump()
    rebuilt = TaskRuntime.model_validate(serialised)
    assert rebuilt == original


def test_task_runtime_is_immutable():
    rt = TaskRuntime(runtime="python", kind="script")
    with pytest.raises(ValidationError):
        rt.runtime = "node"


def test_competency_lower():
    c = Competency(name="Python", proficiency="BASIC")
    assert c.name_lower == "python"
    assert c.proficiency == "BASIC"
