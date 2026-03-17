"""Evaluation gates for PR Review task generation."""

import json
from logger_config import logger
from schemas import EVAL_RESPONSE_SCHEMA
from pr_review_flow.prompts.eval_prompts import BASE_REPO_EVAL_PROMPT, PR_EVAL_PROMPT
from pr_review_flow.pr_review_utils import extract_usage

EVAL_MODEL = "gpt-5-nano-2025-08-07"


def eval_base_repo(code_files: dict, competencies: list, openai_client) -> tuple:
    """Evaluate base repo quality. Returns (eval_result_dict, usage_dict)."""
    competencies_text = "\n".join(
        f"- {c.get('name', '')} ({c.get('proficiency', '')}): {c.get('scope', '')}"
        for c in competencies
    )
    code_files_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in code_files.items()
    )
    prompt = BASE_REPO_EVAL_PROMPT.format(
        competencies_text=competencies_text,
        code_files_text=code_files_text,
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
        logger.error(f"Base repo eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}


def eval_pr_and_answer_key(base_repo_files: dict, pr_data: dict, openai_client) -> tuple:
    """Evaluate PR flaws and answer key completeness. Returns (eval_result_dict, usage_dict)."""
    base_repo_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in base_repo_files.items()
    )
    pr_files = {**pr_data.get("modified_files", {}), **pr_data.get("added_files", {})}
    pr_files_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in pr_files.items()
    )
    if pr_data.get("deleted_files"):
        pr_files_text += "\n\nDeleted files: " + ", ".join(pr_data["deleted_files"])

    answer_key_text = json.dumps(pr_data.get("answer_key", {}), indent=2)

    prompt = PR_EVAL_PROMPT.format(
        base_repo_text=base_repo_text,
        pr_files_text=pr_files_text,
        answer_key_text=answer_key_text,
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
        logger.error(f"PR eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}
