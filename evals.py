import json
import os

import httpx
import openai
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from logger_config import logger
from schemas import EVAL_RESPONSE_SCHEMA

# Model configuration for evaluations.
# Routed via Portkey → OpenAI because EVAL_MODEL is an OpenAI model name and
# the openai_client passed in from multiagent.py points at Portkey → Anthropic
# (which 404s on this model name).
EVAL_MODEL = os.getenv("EVAL_MODEL", "gpt-5-nano-2025-08-07")

eval_openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.environ.get("PORTKEY_API_KEY"),
    ),
    timeout=httpx.Timeout(None),
)

def clean_llm_json_response(response: str) -> str:
    """Clean LLM response to extract valid JSON"""
    try:
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        return response
    except Exception as e:
        logger.error(f"Error cleaning LLM response: {str(e)}")
        return response

MAX_EVAL_RETRIES = 2


class EvalGateError(Exception):
    """Raised when the eval gate rejects a generated task after all retries.

    Carries the last evaluator verdicts so the caller can surface them. The
    presence of this exception means the task was NOT persisted to GitHub or
    Supabase — callers must NOT swallow it as success.
    """

    def __init__(self, attempts: int, last_eval_info: dict | None) -> None:
        self.attempts = attempts
        self.last_eval_info = last_eval_info or {}
        task_pass = self.last_eval_info.get("task_eval", {}).get("pass")
        code_pass = self.last_eval_info.get("code_eval", {}).get("pass")
        super().__init__(
            f"eval gate rejected after {attempts} attempt(s) "
            f"(last verdicts: task_eval.pass={task_pass}, code_eval.pass={code_pass})"
        )

TASK_EVAL_PROMPT = """
You are an expert technical assessment reviewer. Given the following task JSON, proficiency level, years of experience, and time constraint, answer the following:


1. Is the scenario realistic and relevant?

If the task PASSES all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of specific criteria that were met, e.g., 'Appropriate difficulty for {proficiency} level', 'Realistic time constraint of {time_constraint} minutes', 'Relevant scenario for {yoe} years experience', 'Well-balanced complexity']
}}

If the task FAILS any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["list of specific issues found"],
  "feedback": "detailed explanation of what needs to be fixed"
}}

TASK JSON:
{task_json}
"""

CODE_EVAL_PROMPT = """
You are an expert technical assessment reviewer. Given the following code files and task description, answer the following:

1. Are the code files appropriate for an assessment (i.e., not fully implemented, but structured for the candidate to complete)?
2. Do the files avoid providing the full solution or direct answers?
3. Are the files well-structured and relevant to the task?

If the code files PASS all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of specific criteria that were met, e.g., 'Code structure appropriate for assessment', 'No direct solutions provided', 'Well-organized file structure', 'Relevant to task requirements', 'Good balance of guidance and challenge']
}}

If the code files FAIL any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["list of specific issues found"],
  "feedback": "detailed explanation of what needs to be fixed"
}}

TASK DESCRIPTION:
{task_description}

CODE FILES:
{code_files}
"""

def llm_task_eval(task_json, proficiency, yoe, time_constraint, openai_client, model):
    """
    Evaluate task using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.
    """
    task_json_str = json.dumps(task_json, indent=2)
    prompt = TASK_EVAL_PROMPT.format(
        task_json=task_json_str,
        proficiency=proficiency,
        yoe=yoe,
        time_constraint=time_constraint
    )
    
    # Build messages for Responses API
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Use configured eval model for efficient evaluations
        response = eval_openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"]
                }
            }
        )
        
        # Extract output_text from response
        raw_response = getattr(response, "output_text", None)
        if not raw_response:
            logger.error("No output_text received from OpenAI Responses API for task eval")
            return {
                "pass": False,
                "issues": ["No response from evaluation API"],
                "validated_criteria": []
            }
        
        logger.info(f"Raw LLM task eval response: {raw_response[:200]}...")
        
        return json.loads(raw_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse task eval JSON response: {str(e)}")
        logger.error(f"Raw response: {raw_response}")
        # Return a default failure response
        return {
            "pass": False,
            "issues": ["Failed to parse evaluation response"],
            "validated_criteria": []
        }
    except Exception as e:
        logger.error(f"Unexpected error in task evaluation: {str(e)}")
        return {
            "pass": False,
            "issues": [f"Evaluation error: {str(e)}"],
            "validated_criteria": []
        }

def llm_code_eval(code_data, task_description, openai_client, model):
    """
    Evaluate code files using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.
    """
    # Handle both possible structures: direct files dict or nested under 'files' key
    if isinstance(code_data, dict):
        if 'files' in code_data:
            files_content = code_data.get('files', {})
        else:
            # Assume code_data is the files dict directly
            files_content = code_data
    else:
        files_content = {}
    
    prompt = CODE_EVAL_PROMPT.format(code_files=json.dumps(files_content, indent=2), task_description=task_description)
    
    # Build messages for Responses API
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Use configured eval model for efficient evaluations
        response = eval_openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"]
                }
            }
        )
        
        # Extract output_text from response
        raw_response = getattr(response, "output_text", None)
        if not raw_response:
            logger.error("No output_text received from OpenAI Responses API for code eval")
            return {
                "pass": False,
                "issues": ["No response from evaluation API"],
                "validated_criteria": []
            }
        
        logger.info(f"Raw LLM code eval response: {raw_response[:200]}...")
        
        return json.loads(raw_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse code eval JSON response: {str(e)}")
        logger.error(f"Raw response: {raw_response}")
        # Return a default failure response
        return {
            "pass": False,
            "issues": ["Failed to parse code evaluation response"],
            "validated_criteria": []
        }
    except Exception as e:
        logger.error(f"Unexpected error in code evaluation: {str(e)}")
        return {
            "pass": False,
            "issues": [f"Code evaluation error: {str(e)}"],
            "validated_criteria": []
        }
