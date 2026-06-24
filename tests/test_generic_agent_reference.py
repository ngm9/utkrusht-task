"""The competency-neutral GENERIC AGENT reference (2026-06-19).

`task_generation_prompts/_general_reference/agent_general_intermediate_prompt.py`
is the curated, reference-only agent baseline that the prompt-generator pins as
the TOP reference for every agent-engineering competency. These tests pin that it
exists, is clean (mandates a real LLM/agent loop), is reference-only (never loads
into the task registry), and is actually pinned by the retriever.

See docs/plans/2026-06-19-agent-task-fake-llm-rootcause.md
"""

from __future__ import annotations

from pathlib import Path

from infra.classifier.runtime import Competency
from generators.prompts.retriever import _agent_baseline_path, retrieve_references
from generators.prompts.validator import _agent_realness_issues

_GENERIC = (
    Path(__file__).parent.parent
    / "task_generation_prompts"
    / "_general_reference"
    / "agent_general_intermediate_prompt.py"
)

_AGENT_NAMES = (
    "Multi-Agent Systems",
    "Production Agent Engineering",
    "Tool Use for Agents",
    "Context Engineering",
)


def test_generic_agent_reference_exists() -> None:
    assert _GENERIC.exists()
    assert _agent_baseline_path("INTERMEDIATE") == _GENERIC


def test_baseline_path_falls_back_to_intermediate() -> None:
    # No agent_general_advanced_prompt.py yet → falls back to the INTERMEDIATE one.
    assert _agent_baseline_path("ADVANCED") == _GENERIC


def test_generic_is_clean_realness() -> None:
    src = _GENERIC.read_text(encoding="utf-8")
    assert _agent_realness_issues(src) == []


def test_generic_is_reference_only() -> None:
    src = _GENERIC.read_text(encoding="utf-8")
    # No module-level PROMPT_REGISTRY assignment — it must never resolve to a task.
    assert not any(line.startswith("PROMPT_REGISTRY") for line in src.splitlines())


def test_generic_not_in_task_registry() -> None:
    from infra.utils import _PROMPT_REGISTRY
    assert not any("generic" in k.lower() for k in _PROMPT_REGISTRY)


def test_retriever_pins_generic_for_all_agent_competencies() -> None:
    for name in _AGENT_NAMES:
        r = retrieve_references([Competency(name, "INTERMEDIATE")], "INTERMEDIATE")
        assert r.references, f"no references for {name}"
        assert r.references[0].name == "agent_general_intermediate_prompt.py", (
            f"{name}: top ref is {r.references[0].name}, expected the generic baseline"
        )


def test_non_agent_competency_does_not_pin_generic() -> None:
    r = retrieve_references([Competency("Python", "INTERMEDIATE")], "INTERMEDIATE")
    assert all(p.name != "agent_general_intermediate_prompt.py" for p in r.references)


def test_generic_encodes_agent_test_mode_pattern() -> None:
    """The generic must prescribe the proven stabilize wiring: a real model client
    (library-agnostic) + an AGENT_TEST_MODE toggle + .env.example (not a fake)."""
    src = _GENERIC.read_text(encoding="utf-8").lower()
    assert "agent_test_mode" in src
    assert ".env.example" in src
    # library is a free choice — at least one real-client option must be named
    assert any(c in src for c in ("litellm", "openai", "anthropic", "langgraph"))
