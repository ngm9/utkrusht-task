"""Persona-routed eval critics — coverage + prompt-prepending behaviour."""
from unittest.mock import MagicMock, patch

from infra import evals
from infra.evals import PERSONA_PROMPTS, _persona_prefix, llm_code_eval, llm_task_eval


# Personas that any built template must currently route to. New template
# rows can introduce additional personas; the in-repo set lives in
# ``PERSONA_PROMPTS`` so this test guards the seeded baseline.
_BASELINE_PERSONAS = {"backend", "data", "mle"}


def test_persona_prompts_cover_baseline_personas():
    """utkrusht-python ships with personas=[backend,data,mle] — all must have prompts."""
    missing = _BASELINE_PERSONAS - set(PERSONA_PROMPTS)
    assert not missing, f"missing persona prompts for: {missing}"


def test_persona_prefix_empty_for_none():
    assert _persona_prefix(None) == ""


def test_persona_prefix_empty_for_unknown_persona():
    assert _persona_prefix("not-a-real-persona") == ""


def test_persona_prefix_populated_for_known_persona():
    prefix = _persona_prefix("dba")
    assert "senior database administrator" in prefix
    assert prefix.endswith("\n\n")  # cleanly separated from the generic body


def _mock_eval_response(payload: str) -> MagicMock:
    """Build a mock Responses-API response carrying `payload` as output_text."""
    resp = MagicMock()
    resp.output_text = payload
    return resp


_OK_PAYLOAD = '{"pass": true, "issues": [], "validated_criteria": []}'


def test_llm_task_eval_prepends_persona_when_supplied():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval({"name": "x"}, "BASIC", "2", 20, MagicMock(), "ignored",
                      persona="dba")

    prompt_sent = captured["input"][0]["content"]
    assert "senior database administrator" in prompt_sent
    # The generic checklist is still present after the persona block.
    assert "expert technical assessment reviewer" in prompt_sent


def test_llm_task_eval_no_persona_when_none():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval({"name": "x"}, "BASIC", "2", 20, MagicMock(), "ignored")

    prompt_sent = captured["input"][0]["content"]
    assert prompt_sent.lstrip().startswith("You are an expert technical assessment reviewer")
    for prompt in PERSONA_PROMPTS.values():
        assert prompt.strip() not in prompt_sent


def test_llm_code_eval_prepends_persona_when_supplied():
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_code_eval({"a.py": "x"}, "task desc", MagicMock(), "ignored",
                      persona="frontend")

    prompt_sent = captured["input"][0]["content"]
    assert "senior UX engineer" in prompt_sent
    # The new code-eval prompt (Layer A) leads with the bounded-rubric
    # framing instead of the generic "expert reviewer" language.
    assert "STARTER CODE BUNDLE" in prompt_sent
    # The guardrail must be present to prevent goalpost drift.
    assert "DO NOT INVENT REQUIREMENTS" in prompt_sent


# ─────────────────────────────────────────────────────────────────────
# Layer B helpers: _normalize_eval_response + _eval_failure
# ─────────────────────────────────────────────────────────────────────


def test_normalize_eval_response_mirrors_blocking_into_issues():
    from infra.evals import _normalize_eval_response
    result = _normalize_eval_response({
        "pass": False,
        "blocking_issues": ["Criterion 1: missing file"],
        "suggestions": ["consider adding type hints"],
        "validated_criteria": [],
        "issues": [],
        "feedback": "",
    })
    assert result["pass"] is False
    assert result["blocking_issues"] == ["Criterion 1: missing file"]
    # Legacy mirror — `issues` is populated from blocking_issues.
    assert result["issues"] == ["Criterion 1: missing file"]
    assert result["suggestions"] == ["consider adding type hints"]


def test_normalize_eval_response_back_fills_blocking_from_legacy_issues():
    """If a (legacy / mocked) critic only emits `issues`, treat as blockers."""
    from infra.evals import _normalize_eval_response
    result = _normalize_eval_response({
        "pass": False,
        "blocking_issues": [],
        "suggestions": [],
        "validated_criteria": [],
        "issues": ["legacy issue text"],
        "feedback": "",
    })
    assert result["blocking_issues"] == ["legacy issue text"]
    assert result["issues"] == ["legacy issue text"]


def test_normalize_eval_response_forces_pass_false_when_blockers_present():
    """A critic that says pass=True but lists blockers should be coerced
    to pass=False — defends against an LLM that gets the boolean wrong."""
    from infra.evals import _normalize_eval_response
    result = _normalize_eval_response({
        "pass": True,  # wrong — there are blockers
        "blocking_issues": ["Criterion 3: solution is filled in"],
        "suggestions": [],
        "validated_criteria": [],
        "issues": [],
        "feedback": "",
    })
    assert result["pass"] is False
    assert result["blocking_issues"] == ["Criterion 3: solution is filled in"]


def test_normalize_eval_response_keeps_pass_true_when_only_suggestions():
    """Suggestions never affect pass — that's the whole point of the split."""
    from infra.evals import _normalize_eval_response
    result = _normalize_eval_response({
        "pass": True,
        "blocking_issues": [],
        "suggestions": ["could improve naming", "consider extracting a helper"],
        "validated_criteria": ["criterion 1 met", "criterion 2 met"],
        "issues": [],
        "feedback": "",
    })
    assert result["pass"] is True
    assert result["suggestions"] == ["could improve naming", "consider extracting a helper"]


def test_normalize_eval_response_rejects_non_dict():
    from infra.evals import _normalize_eval_response
    result = _normalize_eval_response("not a dict")
    assert result["pass"] is False
    assert "blocking_issues" in result
    assert result["blocking_issues"] != []


def test_eval_failure_has_complete_shape():
    """_eval_failure must return both legacy + new fields so callers
    that only know one shape still work."""
    from infra.evals import _eval_failure
    result = _eval_failure("API timeout")
    for key in ("pass", "blocking_issues", "suggestions",
                "validated_criteria", "issues", "feedback"):
        assert key in result, f"missing key: {key}"
    assert result["pass"] is False
    assert "API timeout" in result["blocking_issues"]
    assert "API timeout" in result["issues"]  # legacy mirror


def test_task_eval_prompt_has_domain_alignment_criterion():
    """Fix 3: Criterion 6 DOMAIN ALIGNMENT must be present in the bounded
    rubric. Catches task-domain drift (e.g. invented 'assessment leaderboard'
    when every scenario was e-commerce / healthcare)."""
    from infra.evals import TASK_EVAL_PROMPT
    assert "DOMAIN ALIGNMENT" in TASK_EVAL_PROMPT
    assert "{scenarios_block}" in TASK_EVAL_PROMPT
    # The guardrail must call out the specific drift pattern.
    assert "employer" in TASK_EVAL_PROMPT.lower() or "employer" in TASK_EVAL_PROMPT


def test_render_scenarios_block_empty_passes_vacuously():
    """When no scenarios are provided (e.g. preflight, or test fixtures with
    no scenarios file), Criterion 6 must pass vacuously rather than block."""
    from infra.evals import _render_scenarios_block
    assert "vacuously" in _render_scenarios_block(None).lower()
    assert "vacuously" in _render_scenarios_block([]).lower()
    assert "vacuously" in _render_scenarios_block(["", "   "]).lower()


def test_render_scenarios_block_numbers_each_scenario():
    """The rendered block must enumerate scenarios so the eval LLM can
    quote them when failing Criterion 6 ('the task is in domain X, but
    the scenarios are #1 e-commerce / #2 healthcare / …')."""
    from infra.evals import _render_scenarios_block
    block = _render_scenarios_block([
        "**Current Implementation:** An e-commerce dashboard...",
        "**Current Implementation:** A patient portal API...",
    ])
    assert "#1:" in block
    assert "#2:" in block
    assert "e-commerce" in block
    assert "patient portal" in block


def test_render_scenarios_block_truncates_long_scenarios():
    """Each scenario truncated to ~500 chars so the eval prompt stays bounded
    even with 7+ long scenarios."""
    from infra.evals import _render_scenarios_block, _SCENARIO_PREVIEW_CHARS
    huge = "X" * (_SCENARIO_PREVIEW_CHARS * 3)
    block = _render_scenarios_block([huge])
    assert "[truncated]" in block
    # Each scenario's preview is capped at _SCENARIO_PREVIEW_CHARS chars;
    # the rendered scenario entry shouldn't exceed that by more than a small
    # framing overhead.
    assert len(block) < _SCENARIO_PREVIEW_CHARS + 200


def test_render_scenarios_block_total_cap():
    """Total block char count bounded so the eval prompt stays in budget
    even with very many scenarios."""
    from infra.evals import _render_scenarios_block, _SCENARIO_BLOCK_CHAR_CAP
    many = [f"Scenario {i}: " + ("Y" * 400) for i in range(50)]
    block = _render_scenarios_block(many)
    # Capped well below the explicit limit. Some scenarios get rendered;
    # the rest are summarized with an "omitted" line.
    assert len(block) < _SCENARIO_BLOCK_CHAR_CAP + 500
    assert "omitted" in block


def test_llm_task_eval_threads_scenarios_into_prompt():
    """run_evaluations passes `scenarios` into llm_task_eval, which formats
    them into the prompt so Criterion 6 can run."""
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval(
            {"name": "x"}, "INTERMEDIATE", "3-5", 20,
            MagicMock(), "ignored",
            scenarios=["**Current Implementation:** An e-commerce checkout..."],
        )

    prompt_sent = captured["input"][0]["content"]
    assert "INPUT SCENARIOS" in prompt_sent
    assert "e-commerce checkout" in prompt_sent
    # Criterion 6 wording must reach the LLM.
    assert "DOMAIN ALIGNMENT" in prompt_sent


def test_llm_task_eval_no_scenarios_renders_vacuous_block():
    """When scenarios=None, the block says Criterion 6 passes vacuously —
    avoids the eval LLM hallucinating that the task is in a bad domain."""
    captured = {}

    def _capture(**kwargs):
        captured["input"] = kwargs["input"]
        return _mock_eval_response(_OK_PAYLOAD)

    with patch.object(evals.eval_openai_client, "responses") as responses_mock:
        responses_mock.create.side_effect = _capture
        llm_task_eval({"name": "x"}, "BASIC", "2", 20, MagicMock(), "ignored")

    prompt_sent = captured["input"][0]["content"]
    assert "vacuously" in prompt_sent.lower()


def test_code_eval_prompt_anchors_to_task_description():
    """The new CODE_EVAL_PROMPT (Layer A) must echo the task description
    so the LLM evaluates AGAINST it, not against general principles."""
    from infra.evals import CODE_EVAL_PROMPT
    # The prompt template must have {task_description} as a format slot
    # so the actual task spec gets injected at call time.
    assert "{task_description}" in CODE_EVAL_PROMPT
    assert "TASK DESCRIPTION" in CODE_EVAL_PROMPT
    # The 5 criteria must be present as the bounded rubric.
    for criterion in ("SCAFFOLD COMPLETENESS", "STUB QUALITY",
                      "SOLUTION CONFIDENTIALITY", "SCAFFOLD SUFFICIENCY",
                      "RUNTIME REASONABLENESS"):
        assert criterion in CODE_EVAL_PROMPT, f"missing criterion: {criterion}"
    # The guardrail must be loud.
    assert "DO NOT INVENT REQUIREMENTS" in CODE_EVAL_PROMPT
    assert "GOALPOST DRIFT" in CODE_EVAL_PROMPT
