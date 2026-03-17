"""
Task Scenario Generator package.

Generates realistic task scenarios for coding assessments based on
competency definitions and proficiency levels.

Usage as CLI:
    python -m scenario_generator --competency-file <path> [--count 6] [--append]

Usage as module:
    from scenario_generator import generate_scenarios_for_competencies, build_scenario_key
"""

from scenario_generator.generator import (
    generate_scenarios_for_competencies,
    build_scenario_key,
    get_competency_names,
    get_target_scenario_file,
    save_generated_scenarios,
    create_openai_client,
    format_cost_summary,
    validate_pr_review_scenario_structure,
)

__all__ = [
    "generate_scenarios_for_competencies",
    "build_scenario_key",
    "get_competency_names",
    "get_target_scenario_file",
    "save_generated_scenarios",
    "create_openai_client",
    "format_cost_summary",
    "validate_pr_review_scenario_structure",
]
