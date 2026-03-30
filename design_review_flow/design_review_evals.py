"""Evaluation gates for Design Review task generation."""

import json
from logger_config import logger
from schemas import EVAL_RESPONSE_SCHEMA
from design_review_flow.prompts import FLAW_SPEC_EVAL_PROMPT, BRIEF_EVAL_PROMPT
from design_review_flow.design_review_utils import extract_usage

EVAL_MODEL = "gpt-5-nano-2025-08-07"


def eval_flaw_spec(flaw_spec: dict, layer_tree_text: str, proficiency: str, openai_client) -> tuple:
    """Evaluate flaw injection spec quality. Returns (eval_result_dict, usage_dict)."""
    flaw_spec_text = json.dumps(flaw_spec, indent=2)

    prompt = FLAW_SPEC_EVAL_PROMPT.format(
        layer_tree_text=layer_tree_text,
        flaw_spec_text=flaw_spec_text,
        proficiency=proficiency,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"Flaw spec eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}


def eval_candidate_brief(brief: dict, flaw_types: list, openai_client) -> tuple:
    """Evaluate candidate brief for answer leaking and coherence. Returns (eval_result_dict, usage_dict)."""
    brief_text = json.dumps(brief, indent=2)
    flaw_types_text = "\n".join(f"- {ft}" for ft in flaw_types)

    prompt = BRIEF_EVAL_PROMPT.format(
        flaw_types_text=flaw_types_text,
        brief_text=brief_text,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"Brief eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}
