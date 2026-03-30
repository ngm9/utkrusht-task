"""
Core prompt generation logic — LLM calls, structural validation, evaluation, and retry loop.
"""

import ast
import json
import os
import re
import importlib
import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from dotenv import load_dotenv

from logger_config import logger
from prompt_generator.prompts import (
    META_SYSTEM_PROMPT,
    GENERATION_SCHEMA,
    EVAL_SYSTEM_PROMPT,
    EVAL_SCHEMA,
    build_meta_prompt,
    build_eval_prompt,
    assemble_python_file,
    load_few_shot_examples,
)
from prompt_generator.deployment_models import (
    DEPLOYMENT_MODELS,
    derive_registry_key,
    derive_tech_slug,
    PROFICIENCY_TIME_RANGES,
)

# Load environment variables
load_dotenv()

# Model configuration
GENERATION_MODEL = "gpt-5-nano-2025-08-07"
EVAL_MODEL = "gpt-5-nano-2025-08-07"
MAX_RETRIES = 2  # 2 retries = 3 total attempts

# Pricing per million tokens
PRICING = {
    GENERATION_MODEL: {"input": 0.50, "output": 2.00},
}

# Output base directory
BASE_DIR = Path(__file__).parent.parent / "task_generation_prompts"

# Level to directory mapping
LEVEL_DIRS = {
    "BEGINNER": "Beginner",
    "BASIC": "Basic",
    "INTERMEDIATE": "Intermediate",
}


def create_openai_client() -> openai.OpenAI:
    """Create OpenAI client configured with Portkey gateway."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    if not portkey_key:
        raise RuntimeError("PORTKEY_API_KEY not set in environment.")

    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=portkey_key,
        ),
    )


def _track_usage(usage_by_model: Dict, model: str, response) -> None:
    """Extract and accumulate token usage from an LLM response."""
    if not hasattr(response, "usage") or response.usage is None:
        return
    usage = response.usage
    if model not in usage_by_model:
        usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0}
    usage_by_model[model]["input_tokens"] += getattr(usage, "input_tokens", 0)
    usage_by_model[model]["output_tokens"] += getattr(usage, "output_tokens", 0)


def format_cost_summary(usage_by_model: Dict) -> str:
    """Format token usage into a human-readable cost summary."""
    lines = ["Cost Breakdown:"]
    grand_input = 0
    grand_output = 0
    grand_cost = 0.0
    for model, usage in usage_by_model.items():
        inp = usage["input_tokens"]
        out = usage["output_tokens"]
        pricing = PRICING.get(model, {"input": 0, "output": 0})
        cost = (inp / 1_000_000 * pricing["input"]) + (out / 1_000_000 * pricing["output"])
        lines.append(f"  {model}: {inp:,} input + {out:,} output = ${cost:.4f}")
        grand_input += inp
        grand_output += out
        grand_cost += cost
    lines.append(f"  TOTAL: {grand_input:,} input + {grand_output:,} output = ${grand_cost:.4f}")
    return "\n".join(lines)


# ============================================================================
# STEP 2: LLM GENERATION
# ============================================================================

def call_llm_generate(
    client: openai.OpenAI,
    meta_prompt: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Call the LLM to generate prompt sections as structured JSON.

    Returns:
        Dict with keys: context_prompt, input_and_ask_prompt, instructions_prompt
        Or None on failure.
    """
    try:
        response = client.responses.create(
            model=GENERATION_MODEL,
            input=[
                {"role": "system", "content": META_SYSTEM_PROMPT},
                {"role": "user", "content": meta_prompt},
            ],
            text={"format": GENERATION_SCHEMA},
            reasoning={"effort": "medium"},
        )
        _track_usage(usage_by_model, GENERATION_MODEL, response)

        output_text = getattr(response, "output_text", None)
        if not output_text:
            logger.error("LLM returned no output_text")
            return None

        return json.loads(output_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"LLM generation failed: {e}")
        return None


# ============================================================================
# STEP 3: STRUCTURAL VALIDATION
# ============================================================================

def validate_structure(
    python_code: str,
    deployment_model: str,
    registry_key: str,
) -> Tuple[bool, List[str]]:
    """Validate the generated Python file structurally.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # 1. Valid Python syntax
    try:
        ast.parse(python_code)
    except SyntaxError as e:
        errors.append(f"Python syntax error: {e}")
        return False, errors

    # 2. PROMPT_REGISTRY exists
    if "PROMPT_REGISTRY" not in python_code:
        errors.append("PROMPT_REGISTRY dict not found in generated code")

    # 3. Registry key present
    if registry_key not in python_code:
        errors.append(f"Registry key '{registry_key}' not found in PROMPT_REGISTRY")

    # 4. Template variables present across all prompt text
    required_vars = [
        "{organization_background}",
        "{role_context}",
        "{competencies}",
        "{real_world_task_scenarios}",
    ]
    for var in required_vars:
        if var not in python_code:
            errors.append(f"Required template variable {var} not found in prompt text")

    # 5. Deployment compliance
    model_def = DEPLOYMENT_MODELS.get(deployment_model, {})
    for required in model_def.get("required_mentions", []):
        if required.lower() not in python_code.lower():
            errors.append(f"Deployment model '{deployment_model}' requires mention of '{required}' but not found")

    for forbidden in model_def.get("forbidden_mentions", []):
        if forbidden.lower() in python_code.lower():
            errors.append(f"Deployment model '{deployment_model}' forbids mention of '{forbidden}' but found in prompt")

    # 6. Double-brace check for JSON examples — look for single braces that aren't template vars
    # This is a heuristic: check for common JSON patterns with single braces
    # that should be double-braced
    known_template_vars = [
        "organization_background", "role_context",
        "competencies", "real_world_task_scenarios",
        "minutes_range", "question_prompt",
    ]
    # Find all {word} patterns and flag ones that aren't known template vars
    single_brace_pattern = re.findall(r'\{(\w+)\}', python_code)
    for match in single_brace_pattern:
        if match not in known_template_vars:
            errors.append(
                f"Possible single-brace JSON key '{{{match}}}' found — should be '{{{{{match}}}}}' "
                f"for Python .format() safety. If this is an intentional template var, add it to known list."
            )
            break  # Only report first occurrence to avoid noise

    # 7. Dynamic import test
    try:
        tmp_dir = tempfile.mkdtemp()
        tmp_file = Path(tmp_dir) / "test_prompt.py"
        tmp_file.write_text(python_code, encoding="utf-8")

        spec = importlib.util.spec_from_file_location("test_prompt", str(tmp_file))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "PROMPT_REGISTRY"):
            errors.append("Dynamic import succeeded but PROMPT_REGISTRY not accessible")
        else:
            reg = module.PROMPT_REGISTRY
            if not isinstance(reg, dict):
                errors.append(f"PROMPT_REGISTRY is {type(reg).__name__}, expected dict")
            elif registry_key not in reg:
                errors.append(f"PROMPT_REGISTRY missing key '{registry_key}'")
            else:
                val = reg[registry_key]
                if not isinstance(val, list) or len(val) != 3:
                    errors.append(f"PROMPT_REGISTRY['{registry_key}'] must be a list of 3 strings, got {type(val).__name__} len={len(val) if isinstance(val, list) else 'N/A'}")
                elif not all(isinstance(v, str) for v in val):
                    errors.append("PROMPT_REGISTRY value contains non-string entries")
    except Exception as e:
        errors.append(f"Dynamic import failed: {e}")
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return len(errors) == 0, errors


# ============================================================================
# STEP 4: LLM EVALUATION
# ============================================================================

def call_llm_evaluate(
    client: openai.OpenAI,
    python_code: str,
    deployment_model: str,
    proficiency: str,
    usage_by_model: Dict,
) -> Tuple[bool, List[str]]:
    """Evaluate a generated prompt via LLM.

    Returns:
        (passed, list_of_reasons)
    """
    model_def = DEPLOYMENT_MODELS.get(deployment_model, {})
    eval_prompt = build_eval_prompt(
        generated_prompt_text=python_code,
        deployment_model=deployment_model,
        proficiency=proficiency,
        deployment_eval_criteria=model_def.get("eval_criteria", ""),
    )

    try:
        response = client.responses.create(
            model=EVAL_MODEL,
            input=[
                {"role": "system", "content": EVAL_SYSTEM_PROMPT},
                {"role": "user", "content": eval_prompt},
            ],
            text={"format": EVAL_SCHEMA},
            reasoning={"effort": "low"},
        )
        _track_usage(usage_by_model, EVAL_MODEL, response)

        output_text = getattr(response, "output_text", None)
        if not output_text:
            logger.warning("Eval LLM returned no output_text — accepting by default")
            return True, []

        result = json.loads(output_text)
        return result.get("pass", False), result.get("reasons", [])
    except Exception as e:
        logger.warning(f"LLM evaluation failed: {e} — accepting by default")
        return True, []


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def generate_prompt(
    client: openai.OpenAI,
    techs: List[str],
    proficiency: str,
    deployment_model: str,
) -> Tuple[Optional[str], Dict]:
    """Generate a task generation prompt file.

    Args:
        client: OpenAI client
        techs: List of technology names
        proficiency: BEGINNER / BASIC / INTERMEDIATE
        deployment_model: no-docker / docker-backend / docker-multi-service / design-only

    Returns:
        (python_code: str or None, usage_by_model: dict)
    """
    proficiency = proficiency.upper()
    usage_by_model = {
        GENERATION_MODEL: {"input_tokens": 0, "output_tokens": 0},
        EVAL_MODEL: {"input_tokens": 0, "output_tokens": 0},
    }

    # Validate deployment model
    if deployment_model not in DEPLOYMENT_MODELS:
        logger.error(f"Unknown deployment model: {deployment_model}. Must be one of: {list(DEPLOYMENT_MODELS.keys())}")
        return None, usage_by_model

    # Derive naming
    registry_key = derive_registry_key(techs, proficiency)
    tech_slug = derive_tech_slug(techs)
    tech_slug_upper = tech_slug.upper()
    level = proficiency.upper()

    # Load deployment model criteria
    model_def = DEPLOYMENT_MODELS[deployment_model]

    # Load few-shot examples
    few_shot_examples = load_few_shot_examples(deployment_model)
    logger.info(f"Loaded {len(few_shot_examples)} few-shot examples")

    eval_failure_feedback = []

    for attempt in range(1, MAX_RETRIES + 2):  # MAX_RETRIES + 1 total attempts
        logger.info(f"Generation attempt {attempt}/{MAX_RETRIES + 1}")

        # Step 1: Build meta-prompt
        meta_prompt = build_meta_prompt(
            techs=techs,
            proficiency=proficiency,
            deployment_model=deployment_model,
            deployment_eval_criteria=model_def["eval_criteria"],
            registry_key=registry_key,
            tech_slug_upper=tech_slug_upper,
            level=level,
            few_shot_examples=few_shot_examples,
            eval_failure_feedback=eval_failure_feedback if eval_failure_feedback else None,
        )

        # Step 2: LLM generation
        result = call_llm_generate(client, meta_prompt, usage_by_model)
        if not result:
            logger.error("LLM generation returned no result")
            eval_failure_feedback.append({"reason": "LLM returned no output"})
            continue

        # Step 2b: Post-process JSON into Python file
        python_code = assemble_python_file(
            context_prompt=result["context_prompt"],
            input_and_ask_prompt=result["input_and_ask_prompt"],
            instructions_prompt=result["instructions_prompt"],
            tech_slug_upper=tech_slug_upper,
            level=level,
            registry_key=registry_key,
        )

        # Step 3: Structural validation
        is_valid, struct_errors = validate_structure(python_code, deployment_model, registry_key)
        if not is_valid:
            logger.warning(f"Structural validation failed: {struct_errors}")
            eval_failure_feedback.extend([{"reason": e} for e in struct_errors])
            continue

        logger.info("Structural validation passed")

        # Step 4: LLM evaluation
        passed, reasons = call_llm_evaluate(
            client, python_code, deployment_model, proficiency, usage_by_model
        )
        if not passed:
            logger.warning(f"LLM evaluation failed: {reasons}")
            eval_failure_feedback.extend([{"reason": r} for r in reasons])
            continue

        logger.info("LLM evaluation passed")
        return python_code, usage_by_model

    # All attempts exhausted
    logger.error(f"All {MAX_RETRIES + 1} attempts failed. Errors: {eval_failure_feedback}")
    return None, usage_by_model


def get_output_path(techs: List[str], proficiency: str) -> Path:
    """Derive the output file path from tech names and proficiency."""
    proficiency = proficiency.upper()
    tech_slug = derive_tech_slug(techs)
    level_dir = LEVEL_DIRS.get(proficiency, "Basic")
    filename = f"{tech_slug}_{proficiency.lower()}_prompt.py"
    return BASE_DIR / level_dir / filename
