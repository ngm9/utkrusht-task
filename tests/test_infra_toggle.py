"""Part A — force-infra toggle: the infra-kind registry, the agent.forward
override (skips the classifier + threads the service), and the trace_ui wiring
(/api/infra-kinds + api_launch flag threading)."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from generators.prompts import infra_kinds
from trace_ui import server
from trace_ui.server import app


# ── registry ─────────────────────────────────────────────────────────────
def test_list_kinds_order_and_membership():
    slugs = [k["slug"] for k in infra_kinds.list_kinds()]
    assert slugs[0] == "auto"
    assert {"vector-db", "redis", "kafka", "postgres", "mcp-server"} <= set(slugs)


def test_resolve_known_and_unknown():
    r = infra_kinds.resolve("redis")
    assert r["slug"] == "redis" and r["service"] == "redis" and r["directive"]
    assert infra_kinds.resolve("bogus")["slug"] == "auto"
    assert infra_kinds.resolve(None)["slug"] == "auto"
    assert infra_kinds.resolve("VECTOR-DB")["slug"] == "vector-db"  # case-insensitive


def test_is_valid():
    assert infra_kinds.is_valid("kafka")
    assert not infra_kinds.is_valid("nope")
    assert not infra_kinds.is_valid(None)


# ── agent.forward override ────────────────────────────────────────────────
def test_forward_override_skips_classifier_and_threads_service(monkeypatch):
    import generators.prompts.agent as ag

    def _boom(**k):
        raise AssertionError("classify_task_shape MUST be skipped when overriding")

    monkeypatch.setattr(ag, "classify_task_shape", _boom)
    monkeypatch.setattr(ag, "build_detailed_skill_signal", lambda comps, prof, env="dev": ("", {}))
    monkeypatch.setattr(ag, "init_supabase", lambda env: None)
    monkeypatch.setattr(ag, "fetch_competency_scope", lambda sb, name, prof: {"scope": "x"})
    monkeypatch.setattr(ag, "retrieve_references", lambda comps, prof, template=None:
                        SimpleNamespace(references=[], notes=[], bootstrap_mode=True, fallback_level=0))
    monkeypatch.setattr(ag, "fetch_similar_tasks", lambda sb, names, prof: [])
    monkeypatch.setattr(ag, "validate_prompt_file", lambda *a, **k:
                        SimpleNamespace(passed=True, issues=[], warnings=[], registry_key="k"))

    agent = ag.PromptGeneratorAgent(max_iterations=1)
    agent.verifier_enabled = False
    captured = {}
    agent.generate = lambda **kw: (captured.update(kw),
                                   SimpleNamespace(new_prompt_file="PROMPT_REGISTRY = {}", reasoning="r"))[1]

    from infra.classifier.runtime import Competency
    res = agent.forward(
        [Competency(name="Tool Use for Agents", proficiency="INTERMEDIATE")],
        "INTERMEDIATE", task_shape_override="infra", infra_kind="redis",
    )
    assert res.task_shape == "infra"
    assert "forced by override" in res.task_shape_reason
    assert "redis" in captured.get("datastores", "")   # service threaded into the generate signature


def test_forward_non_infra_override_no_service(monkeypatch):
    import generators.prompts.agent as ag
    monkeypatch.setattr(ag, "classify_task_shape", lambda **k: (_ for _ in ()).throw(AssertionError("skipped")))
    monkeypatch.setattr(ag, "build_detailed_skill_signal", lambda comps, prof, env="dev": ("", {}))
    monkeypatch.setattr(ag, "init_supabase", lambda env: None)
    monkeypatch.setattr(ag, "fetch_competency_scope", lambda sb, name, prof: {"scope": "x"})
    monkeypatch.setattr(ag, "retrieve_references", lambda comps, prof, template=None:
                        SimpleNamespace(references=[], notes=[], bootstrap_mode=True, fallback_level=0))
    monkeypatch.setattr(ag, "validate_prompt_file", lambda *a, **k:
                        SimpleNamespace(passed=True, issues=[], warnings=[], registry_key="k"))
    agent = ag.PromptGeneratorAgent(max_iterations=1)
    agent.verifier_enabled = False
    captured = {}
    agent.generate = lambda **kw: (captured.update(kw),
                                   SimpleNamespace(new_prompt_file="PROMPT_REGISTRY = {}", reasoning=""))[1]
    from infra.classifier.runtime import Competency
    res = agent.forward([Competency(name="DSA", proficiency="BASIC")], "BASIC", task_shape_override="non_infra")
    assert res.task_shape == "non_infra"
    assert captured.get("datastores") in ("[]", "")  # no service for non_infra


# ── trace_ui wiring ───────────────────────────────────────────────────────
client = TestClient(app)


def test_api_infra_kinds():
    data = client.get("/api/infra-kinds").json()
    slugs = {k["slug"] for k in data["kinds"]}
    assert {"auto", "vector-db", "redis"} <= slugs


def _capture_launch(monkeypatch):
    captured = {}
    monkeypatch.setattr(server, "_spawn_pipeline", lambda cmd: captured.setdefault("cmd", cmd))
    return captured


def test_api_launch_threads_infra_flags(monkeypatch):
    cap = _capture_launch(monkeypatch)
    r = client.post("/api/runs", json={"names": ["Tool Use for Agents"], "proficiency": "INTERMEDIATE",
                                       "task_shape": "infra", "infra_kind": "redis"})
    assert r.status_code == 200
    cmd = cap["cmd"]
    assert cmd[cmd.index("--task-shape") + 1] == "infra"
    assert cmd[cmd.index("--infra-kind") + 1] == "redis"


def test_api_launch_auto_omits_infra_kind(monkeypatch):
    cap = _capture_launch(monkeypatch)
    r = client.post("/api/runs", json={"names": ["Python"], "proficiency": "BASIC"})
    assert r.status_code == 200
    cmd = cap["cmd"]
    assert cmd[cmd.index("--task-shape") + 1] == "auto"
    assert "--infra-kind" not in cmd


def test_api_launch_bad_kind_falls_back_to_auto(monkeypatch):
    cap = _capture_launch(monkeypatch)
    r = client.post("/api/runs", json={"names": ["X"], "proficiency": "BASIC",
                                       "task_shape": "infra", "infra_kind": "bogus"})
    assert r.status_code == 200
    cmd = cap["cmd"]
    assert cmd[cmd.index("--infra-kind") + 1] == "auto"
