"""
Core scenario generation logic — classification, LLM calls, validation, and pipeline orchestration.
"""

import json
import os
import re
import difflib
from pathlib import Path
from typing import Dict, List, Optional

import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from dotenv import load_dotenv

from logger_config import logger
from scenario_generator.prompts import (
    SCENARIO_SYSTEM_PROMPT,
    SCENARIO_GENERATION_SCHEMA,
    SCENARIO_EVAL_SCHEMA,
    PROFICIENCY_LIMITS,
    build_generation_prompt,
    build_eval_prompt,
)

# Load environment variables
load_dotenv()

# Model configuration — using gpt-5-nano for both generation and evaluation (cost-effective)
GENERATION_MODEL = "gpt-5-nano-2025-08-07"
EVAL_MODEL = "gpt-5-nano-2025-08-07"
MAX_RETRIES = 1

# Pricing per million tokens (https://platform.openai.com/docs/pricing)
PRICING = {
    GENERATION_MODEL: {"input": 0.50, "output": 2.00},    # gpt-5-nano
}

# ============================================================================
# COST TRACKING
# ============================================================================

def extract_usage(response) -> Dict:
    """Extract token usage from an OpenAI Responses API response."""
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }
    return {"input_tokens": 0, "output_tokens": 0}


def calculate_cost(total_usage: Dict, model: str) -> float:
    """Calculate cost in USD from token usage for a given model."""
    prices = PRICING.get(model, {"input": 1.25, "output": 10.00})
    input_cost = (total_usage["input_tokens"] / 1_000_000) * prices["input"]
    output_cost = (total_usage["output_tokens"] / 1_000_000) * prices["output"]
    return input_cost + output_cost


def format_cost_summary(usage_by_model: Dict) -> str:
    """Format a cost summary string from usage-by-model tracking dict."""
    lines = []
    grand_total_cost = 0.0
    grand_total_input = 0
    grand_total_output = 0

    for model, usage in usage_by_model.items():
        cost = calculate_cost(usage, model)
        grand_total_cost += cost
        grand_total_input += usage["input_tokens"]
        grand_total_output += usage["output_tokens"]
        lines.append(
            f"  {model}: {usage['input_tokens']:,} input + {usage['output_tokens']:,} output tokens = ${cost:.6f}"
        )

    lines.insert(0, "Cost Breakdown:")
    lines.append(f"  Total: {grand_total_input:,} input + {grand_total_output:,} output tokens = ${grand_total_cost:.6f}")
    return "\n".join(lines)


# ============================================================================
# COMPETENCY NAME HELPERS
# ============================================================================

# Names that indicate non-code competencies (used only for file routing)
NON_CODE_COMPETENCIES = {
    "Prompt Engineering",
    "Prompt Engineering for Product Managers",
    "AI Literacy",
    "AI Literacy for Leaders",
}


def is_non_code_competency(competencies: List[Dict]) -> bool:
    """Check if any competency is a non-code type (for file routing only)."""
    for comp in competencies:
        name = comp.get("name", "").strip()
        if name in NON_CODE_COMPETENCIES:
            return True
    return False


def get_competency_names(competencies: List[Dict]) -> str:
    """Extract competency names as a comma-separated string for prompt injection."""
    names = []
    for comp in competencies:
        name = comp.get("name", "").strip()
        if name:
            names.append(name)
    return ", ".join(names)


# ============================================================================
# SCENARIO KEY CONSTRUCTION
# ============================================================================

def build_scenario_key(competencies: List[Dict]) -> str:
    """Build the scenario lookup key from competencies list.

    Produces keys like 'Java (BASIC), Kafka (BASIC)' that match
    the key format used in task_scenarios.json files.
    """
    formatted = []
    for comp in competencies:
        name = comp.get("name", "").strip()
        proficiency = comp.get("proficiency", "").upper()
        if name and proficiency:
            formatted.append(f"{name} ({proficiency})")
    return ", ".join(sorted(formatted))


def get_target_scenario_file(competencies: List[Dict]) -> Path:
    """Determine the correct scenario file based on competency type and proficiency."""
    base = Path(__file__).parent.parent / "task_input_files" / "task_scenarios"
    proficiency = competencies[0].get("proficiency", "BASIC").upper() if competencies else "BASIC"

    if is_non_code_competency(competencies):
        return base / "task_sceanrio_no_code.json"
    elif proficiency == "INTERMEDIATE":
        return base / "task_scenarios_intermediate.json"
    else:
        return base / "task_scenarios.json"


# ============================================================================
# LOADING & SAVING SCENARIOS
# ============================================================================

def load_all_existing_scenarios(scenario_files: List[Path]) -> List[str]:
    """Load all scenarios from multiple files into a flat list for deduplication."""
    all_scenarios = []
    for f in scenario_files:
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                for key, scenarios in data.items():
                    if isinstance(scenarios, list):
                        all_scenarios.extend(scenarios)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not read scenarios from {f}: {e}")
    return all_scenarios


def load_scenarios_for_key(scenario_files: List[Path], key: str) -> List[str]:
    """Load existing scenarios for a specific key across all scenario files."""
    scenarios = []
    for f in scenario_files:
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if key in data and isinstance(data[key], list):
                    scenarios.extend(data[key])
                # Also try reversed key for 2-competency combos
                parts = [p.strip() for p in key.split(",")]
                if len(parts) == 2:
                    reversed_key = f"{parts[1]}, {parts[0]}"
                    if reversed_key in data and isinstance(data[reversed_key], list):
                        scenarios.extend(data[reversed_key])
            except (json.JSONDecodeError, IOError):
                pass
    return scenarios


def save_generated_scenarios(scenarios: List[str], key: str, target_file: Path, append: bool = True):
    """Save scenarios to the target JSON file under the given key."""
    if append and target_file.exists():
        try:
            with open(target_file, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
        except (json.JSONDecodeError, IOError):
            existing = {}
        if key in existing and isinstance(existing[key], list):
            existing[key].extend(scenarios)
        else:
            existing[key] = scenarios
        data = existing
    else:
        data = {key: scenarios}

    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(scenarios)} scenarios to {target_file} under key '{key}'")


# ============================================================================
# OPENAI CLIENT SETUP
# ============================================================================

def create_openai_client() -> openai.OpenAI:
    """Create OpenAI client with Portkey gateway, matching multiagent.py configuration."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=portkey_key,
        ),
    )


# ============================================================================
# COMPETENCY FORMATTING
# ============================================================================

def format_competencies_with_scopes(competencies: List[Dict]) -> str:
    """Format competencies with their scope descriptions for the prompt."""
    parts = []
    for comp in competencies:
        name = comp.get("name", "Unknown")
        proficiency = comp.get("proficiency", "BASIC").upper()
        scope = comp.get("scope", "No scope provided.")
        parts.append(
            f"- {name} ({proficiency}):\n  Scope: {scope}"
        )
    return "\n\n".join(parts)


def get_combined_scope_text(competencies: List[Dict]) -> str:
    """Get combined scope text from all competencies for evaluation."""
    scopes = []
    for comp in competencies:
        name = comp.get("name", "")
        scope = comp.get("scope", "")
        if scope:
            scopes.append(f"{name}: {scope}")
    return "\n".join(scopes)


# ============================================================================
# VALIDATION & DEDUPLICATION
# ============================================================================

def validate_scenario_structure(scenario: str, proficiency: str = "BASIC") -> bool:
    """Validate that a scenario meets structural requirements for its proficiency level.

    Checks for:
    - Minimum/maximum length (per proficiency)
    - Required bold-header sections
    - Word count limits (per proficiency)
    - Bullet point count limits (per proficiency)
    """
    limits = PROFICIENCY_LIMITS.get(proficiency, PROFICIENCY_LIMITS["BASIC"])

    if len(scenario) < 100:
        logger.warning(f"Scenario too short ({len(scenario)} chars): {scenario[:80]}...")
        return False

    if len(scenario) > limits["max_chars"]:
        logger.warning(
            f"Scenario too long for {proficiency} level ({len(scenario)} chars, "
            f"max {limits['max_chars']}): {scenario[:80]}..."
        )
        return False

    # Check for required bold-header sections
    required_headers = ["**Current Implementation:**", "**Your Task:**", "**Success Criteria:**"]
    for header in required_headers:
        if header not in scenario:
            logger.warning(f"Scenario missing required section '{header}': {scenario[:80]}...")
            return False

    # Check word count
    word_count = len(scenario.split())
    if word_count > limits["max_words"]:
        logger.warning(
            f"Scenario too verbose for {proficiency} level ({word_count} words, "
            f"max {limits['max_words']}): {scenario[:80]}..."
        )
        return False

    # Check bullet point count in "Your Task" section
    task_section = ""
    if "**Your Task:**" in scenario and "**Success Criteria:**" in scenario:
        task_start = scenario.index("**Your Task:**") + len("**Your Task:**")
        task_end = scenario.index("**Success Criteria:**")
        task_section = scenario[task_start:task_end]

    bullet_count = task_section.count("- ") + task_section.count("• ")
    # Also count numbered items like "1. ", "2. "
    numbered_bullets = len(re.findall(r'\d+\.\s', task_section))
    total_bullets = bullet_count + numbered_bullets

    if total_bullets > limits["max_bullets"]:
        logger.warning(
            f"Scenario has too many bullet points for {proficiency} level "
            f"({total_bullets} bullets, max {limits['max_bullets']}): {scenario[:80]}..."
        )
        return False

    return True


def validate_pr_review_scenario_structure(scenario: str, proficiency: str = "BASIC") -> bool:
    """Validate that a PR review scenario has the required three-section structure.

    Checks for:
    - Required bold-header sections: Project Context, PR Intent, Injected Flaws
    - Minimum length
    - At least 1 flaw in Injected Flaws section
    """
    if len(scenario) < 100:
        logger.warning(f"PR review scenario too short ({len(scenario)} chars)")
        return False

    required_headers = ["**Project Context:**", "**PR Intent:**", "**Injected Flaws:**"]
    for header in required_headers:
        if header not in scenario:
            logger.warning(f"PR review scenario missing required section '{header}'")
            return False

    # Check that Injected Flaws has at least one bullet
    if "**Injected Flaws:**" in scenario:
        flaws_start = scenario.index("**Injected Flaws:**") + len("**Injected Flaws:**")
        flaws_section = scenario[flaws_start:]
        bullet_count = flaws_section.count("- ")
        if bullet_count < 1:
            logger.warning("PR review scenario has no flaws listed in Injected Flaws section")
            return False

    return True


def check_similarity(new_scenario: str, existing_scenarios: List[str], threshold: float = 0.6) -> bool:
    """Check if a new scenario is too similar to any existing scenario.

    Returns True if the scenario is unique enough (below threshold).
    Returns False if it's too similar to an existing one.
    """
    for existing in existing_scenarios:
        ratio = difflib.SequenceMatcher(None, new_scenario.lower(), existing.lower()).ratio()
        if ratio > threshold:
            logger.warning(
                f"Scenario too similar (ratio={ratio:.2f}) to existing: {existing[:80]}..."
            )
            return False
    return True


# ============================================================================
# LLM CALLS
# ============================================================================

def call_llm_generate(
    client: openai.OpenAI,
    competencies: List[Dict],
    count: int,
    existing_scenarios: List[str],
    eval_feedback: List[Dict] = None,
    background: Optional[Dict] = None,
) -> tuple:
    """Call the LLM to generate task scenarios.

    Args:
        eval_feedback: Optional list of dicts with 'scenario' and 'reason' keys from
                       previous evaluation failures, so the LLM avoids the same mistakes.
        background: Optional background dict from background_forQuestions_*.json,
                    used to inject assessment scope into the prompt.

    Returns:
        (scenarios: List[str], usage: Dict with input_tokens/output_tokens)
    """
    proficiency = competencies[0].get("proficiency", "BASIC").upper()
    competency_names = get_competency_names(competencies)
    competencies_text = format_competencies_with_scopes(competencies)

    competency_names_list = [
        comp.get("name", "").strip()
        for comp in competencies
        if comp.get("name", "").strip()
    ]

    prompt = build_generation_prompt(
        competencies_with_scopes=competencies_text,
        proficiency=proficiency,
        competency_names=competency_names,
        count=count,
        existing_scenarios=existing_scenarios,
        eval_feedback=eval_feedback,
        background=background,
        competency_names_list=competency_names_list,
    )

    messages = [
        {"role": "system", "content": SCENARIO_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    logger.info(f"Calling LLM ({GENERATION_MODEL}) to generate {count} scenarios...")

    response = client.responses.create(
        model=GENERATION_MODEL,
        input=messages,
        reasoning={"effort": "medium"},
        text={
            "format": {
                "type": "json_schema",
                "name": SCENARIO_GENERATION_SCHEMA["name"],
                "schema": SCENARIO_GENERATION_SCHEMA["schema"],
                "strict": SCENARIO_GENERATION_SCHEMA["strict"],
            }
        },
    )

    usage = extract_usage(response)
    raw = getattr(response, "output_text", None)
    if not raw:
        raise RuntimeError("No output_text received from LLM for scenario generation")

    logger.info(f"Raw LLM generation response: {raw[:300]}...")

    result = json.loads(raw)
    return result.get("scenarios", []), usage


def call_llm_evaluate(
    client: openai.OpenAI,
    scenarios: List[str],
    competencies: List[Dict],
) -> tuple:
    """Call the LLM to evaluate generated scenarios.

    Returns:
        (evaluations: List[Dict], usage: Dict with input_tokens/output_tokens)
    """
    proficiency = competencies[0].get("proficiency", "BASIC").upper()
    tech_stack = ", ".join(c.get("name", "") for c in competencies)
    scope_text = get_combined_scope_text(competencies)

    prompt = build_eval_prompt(
        scenarios=scenarios,
        proficiency=proficiency,
        tech_stack=tech_stack,
        scope_text=scope_text,
    )

    messages = [{"role": "user", "content": prompt}]

    logger.info(f"Calling LLM ({EVAL_MODEL}) to evaluate {len(scenarios)} scenarios...")

    response = client.responses.create(
        model=EVAL_MODEL,
        input=messages,
        reasoning={"effort": "medium"},
        text={
            "format": {
                "type": "json_schema",
                "name": SCENARIO_EVAL_SCHEMA["name"],
                "schema": SCENARIO_EVAL_SCHEMA["schema"],
                "strict": SCENARIO_EVAL_SCHEMA["strict"],
            }
        },
    )

    usage = extract_usage(response)
    raw = getattr(response, "output_text", None)
    if not raw:
        logger.warning("No output_text from eval LLM, treating all as passed")
        return [{"scenario_index": i, "pass": True, "reason": ""} for i in range(len(scenarios))], usage

    logger.info(f"Raw LLM eval response: {raw[:300]}...")
    result = json.loads(raw)
    return result.get("evaluations", []), usage


# ============================================================================
# CORE GENERATION PIPELINE
# ============================================================================

def generate_scenarios_for_competencies(
    openai_client: openai.OpenAI,
    competencies: List[Dict],
    count: int = 6,
    existing_scenarios_files: Optional[List[Path]] = None,
    background: Optional[Dict] = None,
) -> tuple:
    """Generate, validate, evaluate, and return high-quality task scenarios.

    Args:
        openai_client: Configured OpenAI client.
        competencies: List of competency dicts from competency_*.json.
        count: Number of scenarios to generate.
        existing_scenarios_files: Paths to existing scenario JSON files for deduplication.
        background: Optional background context from background_forQuestions_*.json.

    Returns:
        (scenarios: List[str], usage_by_model: Dict[str, Dict]) — scenarios and cost tracking data.
    """
    # Track usage per model
    usage_by_model = {
        GENERATION_MODEL: {"input_tokens": 0, "output_tokens": 0},
        EVAL_MODEL: {"input_tokens": 0, "output_tokens": 0},
    }

    if not competencies:
        logger.error("No competencies provided")
        return [], usage_by_model

    scenario_key = build_scenario_key(competencies)
    competency_names = get_competency_names(competencies)
    proficiency = competencies[0].get("proficiency", "BASIC").upper()

    logger.info(f"Generating scenarios for: {scenario_key}")
    logger.info(f"Competencies: {competency_names}, Proficiency: {proficiency}")

    # Load existing scenarios for deduplication
    default_files = [
        Path(__file__).parent.parent / "task_input_files" / "task_scenarios" / "task_scenarios.json",
        Path(__file__).parent.parent / "task_input_files" / "task_scenarios" / "task_scenarios_intermediate.json",
        Path(__file__).parent.parent / "task_input_files" / "task_scenarios" / "task_sceanrio_no_code.json",
    ]
    scenario_files = existing_scenarios_files or default_files
    all_existing = load_all_existing_scenarios(scenario_files)
    key_existing = load_scenarios_for_key(scenario_files, scenario_key)

    logger.info(f"Loaded {len(all_existing)} total existing scenarios, {len(key_existing)} for this key")

    # --- Generation + Validation loop ---
    passing_scenarios = []
    eval_failure_feedback = []  # Collect failure reasons to feed back on retry
    attempts = 0

    while len(passing_scenarios) < count and attempts <= MAX_RETRIES:
        needed = count - len(passing_scenarios)
        attempts += 1

        logger.info(f"Generation attempt {attempts}: need {needed} more scenarios")

        try:
            generated, gen_usage = call_llm_generate(
                client=openai_client,
                competencies=competencies,
                count=needed,
                existing_scenarios=key_existing + passing_scenarios,
                eval_feedback=eval_failure_feedback if eval_failure_feedback else None,
                background=background,
            )
            usage_by_model[GENERATION_MODEL]["input_tokens"] += gen_usage["input_tokens"]
            usage_by_model[GENERATION_MODEL]["output_tokens"] += gen_usage["output_tokens"]
        except Exception as e:
            logger.error(f"LLM generation failed on attempt {attempts}: {e}")
            continue

        if not generated:
            logger.warning(f"LLM returned empty scenarios on attempt {attempts}")
            continue

        logger.info(f"LLM generated {len(generated)} scenarios")

        # Structural validation (with per-proficiency limits)
        structurally_valid = []
        for s in generated:
            if validate_scenario_structure(s, proficiency):
                structurally_valid.append(s)
            else:
                logger.warning(f"Scenario failed structural validation: {s[:80]}...")

        # Deduplication against all existing + already accepted
        combined_existing = all_existing + passing_scenarios
        unique = []
        for s in structurally_valid:
            if check_similarity(s, combined_existing):
                unique.append(s)
            else:
                logger.warning(f"Scenario rejected as duplicate: {s[:80]}...")

        if not unique:
            logger.warning(f"All scenarios from attempt {attempts} were filtered out")
            continue

        # LLM quality evaluation
        try:
            evals, eval_usage = call_llm_evaluate(openai_client, unique, competencies)
            usage_by_model[EVAL_MODEL]["input_tokens"] += eval_usage["input_tokens"]
            usage_by_model[EVAL_MODEL]["output_tokens"] += eval_usage["output_tokens"]
        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}. Accepting structurally valid scenarios.")
            evals = [{"scenario_index": i, "pass": True, "reason": ""} for i in range(len(unique))]

        for ev in evals:
            idx = ev.get("scenario_index", -1)
            if 0 <= idx < len(unique) and ev.get("pass", False):
                passing_scenarios.append(unique[idx])
                logger.info(f"Scenario {idx+1} passed evaluation")
            elif 0 <= idx < len(unique):
                reason = ev.get("reason", "unknown")
                logger.warning(f"Scenario {idx+1} failed evaluation: {reason}")
                # Collect failure feedback for next retry attempt
                eval_failure_feedback.append({
                    "scenario": unique[idx],
                    "reason": reason,
                })

        logger.info(f"After attempt {attempts}: {len(passing_scenarios)}/{count} scenarios ready")

    if len(passing_scenarios) < count:
        logger.warning(
            f"Only generated {len(passing_scenarios)}/{count} scenarios after {attempts} attempts"
        )

    return passing_scenarios[:count], usage_by_model
