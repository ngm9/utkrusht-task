"""validate_scenario_structure now returns (is_valid, reason).

The reason is fed back into the generation retry loop so a structurally-bad
scenario (e.g. bullet overflow) is corrected on the next attempt instead of
being silently dropped and blindly regenerated.
"""
from generators.scenarios.generator import validate_scenario_structure

_INTRO = (
    "**Current Implementation:** A FastAPI endpoint GET /api/reports is slow "
    "because it runs three sequential PostgreSQL queries with no indexes and "
    "opens a new connection per request."
)
_SUCCESS = "**Success Criteria:** p95 latency drops under 800ms and connection churn is gone."


def _scenario(task_bullets: list[str]) -> str:
    bullets = "\n".join(f"- {b}" for b in task_bullets)
    return f"{_INTRO}\n\n**Your Task:**\n{bullets}\n\n{_SUCCESS}"


def test_valid_scenario_returns_true_empty_reason():
    ok, reason = validate_scenario_structure(
        _scenario(["Add composite indexes", "Combine into one CTE query", "Use an asyncpg pool"]),
        "INTERMEDIATE",
    )
    assert ok is True
    assert reason == ""


def test_bullet_overflow_returns_actionable_reason():
    six = _scenario([f"change {i}" for i in range(1, 7)])  # 6 bullets > INTERMEDIATE cap of 5
    ok, reason = validate_scenario_structure(six, "INTERMEDIATE")
    assert ok is False
    assert "Too many bullet points" in reason
    assert "6 found" in reason          # the actual count, so the LLM knows
    assert "max 5" in reason            # the hard cap


def test_missing_section_reason():
    no_success = f"{_INTRO}\n\n**Your Task:**\n- do the thing properly and carefully here"
    ok, reason = validate_scenario_structure(no_success, "INTERMEDIATE")
    assert ok is False
    assert "Missing required section" in reason
    assert "Success Criteria" in reason


def test_too_short_reason():
    ok, reason = validate_scenario_structure("**Current Implementation:** x", "INTERMEDIATE")
    assert ok is False
    assert "too short" in reason.lower()
