import json
import os

import httpx
import openai
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from infra.logger_config import logger
from infra.schemas import EVAL_RESPONSE_SCHEMA

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


class LLMOutputTruncated(Exception):
    """Raised when the generation LLM hit its max_tokens cap mid-output.

    Distinct from a generic parse error because the cause + fix are specific:
    the JSON is partial because we ran out of completion-token budget, not
    because the LLM produced malformed output. Caller (multiagent.create_task)
    catches this in its retry loop and feeds back "your last reply was cut off
    — keep the response shorter and close all braces".
    """

    def __init__(self, partial_text: str, attempt: int) -> None:
        self.partial_text = partial_text
        self.attempt = attempt
        super().__init__(
            f"LLM output truncated at attempt {attempt} "
            f"(partial response length: {len(partial_text)} chars)"
        )


# ----------------------------------------------------------------------
# Persona prompts — keyed by TaskRuntime.kind
# ----------------------------------------------------------------------
#
# The eval critic gets a domain-specific "reviewer persona" prepended to its
# generic checklist. A senior DBA notices a missing NOT NULL on a junction-
# table FK that a generic reviewer skims past; a senior MLE catches a chunking
# strategy that conflicts with the retrieval question; an SDET notices test
# isolation problems that look fine to a backend reviewer.
#
# Same prompt model (gpt-5-nano), same JSON schema, same call shape — the only
# delta is the persona block prepended before the generic TASK_EVAL_PROMPT /
# CODE_EVAL_PROMPT body.

PERSONA_PROMPTS: dict[str, str] = {
    "app": (
        "You are a senior backend engineer with 10+ years of experience shipping "
        "production services. Focus your review on: correctness of the request "
        "lifecycle, input validation, error handling at I/O boundaries, status-code "
        "semantics, and whether the candidate is asked to do realistic backend work "
        "(not toy CRUD)."
    ),
    "script": (
        "You are a senior backend / data engineer who writes one-off scripts and "
        "batch jobs in production. Focus your review on: data-flow correctness, "
        "transactional boundaries when DBs are involved, retries on transient "
        "failures, and idempotency. Reject toy examples that don't reflect real "
        "operational work."
    ),
    "mobile": (
        "You are a senior mobile engineer (Flutter, React Native, native iOS/"
        "Android). Focus your review on: UI lifecycle (rebuild costs, controller "
        "disposal), state management (Riverpod/Provider/Redux), offline-first "
        "behaviour and cache TTL, and concurrency around network calls. Reject "
        "tasks that ignore the offline/poor-connectivity reality of mobile."
    ),
    "frontend": (
        "You are a senior UX engineer. Focus your review on: accessibility "
        "(semantic HTML, ARIA, keyboard navigation), responsive layout behaviour, "
        "focus management, and whether the candidate is asked to write user-facing "
        "code rather than just style boilerplate."
    ),
    "testing": (
        "You are a senior SDET. Focus your review on: test isolation (no shared "
        "state between tests), assertion quality (testing visible behaviour vs "
        "implementation details), fixture hygiene, deterministic timing (no fixed "
        "sleeps), and whether the test would actually catch the bug being asked "
        "about."
    ),
    "db_only": (
        "You are a senior database administrator. Focus your review on: schema "
        "normalisation (3NF unless denormalisation is deliberate), NOT NULL "
        "discipline on FK columns, index coverage for the predicates the queries "
        "actually use, query-plan implications, and whether the task rewards good "
        "schema design over rote SQL writing."
    ),
    "llm": (
        "You are a senior ML engineer specialising in retrieval-augmented systems "
        "and LLM application design. Focus your review on: retrieval setup "
        "(chunking strategy, embedding model fit, top-k), prompt design and "
        "prompt-injection surface, eval methodology, and whether the task tests "
        "judgment about LLM behaviour rather than just glue-code wiring."
    ),
    "vector_db": (
        "You are a senior ML engineer focused on vector indexes. Focus your "
        "review on: embedding-model fit for the data, dimensionality choices, "
        "distance metric appropriateness (cosine / L2 / inner-product), metadata "
        "filtering correctness, and recall@k vs latency tradeoffs."
    ),
    "non_code": (
        "You are a senior product manager and evaluation engineer. Focus your "
        "review on: rubric clarity (what does a good answer look like?), anchor "
        "quality (specific metrics and thresholds, not vague adjectives), "
        "observable behaviours rather than feelings, and whether the task rewards "
        "judgment under realistic product constraints (cost, time, data "
        "availability)."
    ),
}


def _persona_prefix(kind: str | None) -> str:
    """Return the persona block to prepend, or '' when no kind is supplied or
    when the kind doesn't have a dedicated persona (in which case the eval
    runs with just the generic checklist — the prior behaviour).
    """
    if not kind:
        return ""
    persona = PERSONA_PROMPTS.get(kind)
    if not persona:
        return ""
    return persona.strip() + "\n\n"

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

def llm_task_eval(task_json, proficiency, yoe, time_constraint, openai_client, model,
                  kind: str | None = None):
    """
    Evaluate task using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.

    When ``kind`` is supplied (one of the TaskRuntime.kind values from
    prompt_generator.runtime), the matching persona prompt is prepended to the
    generic checklist. When None or unrecognised, the eval falls back to the
    plain prompt (prior behaviour).
    """
    task_json_str = json.dumps(task_json, indent=2)
    prompt = _persona_prefix(kind) + TASK_EVAL_PROMPT.format(
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

def llm_code_eval(code_data, task_description, openai_client, model,
                  kind: str | None = None):
    """
    Evaluate code files using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.

    When ``kind`` is supplied, the matching persona prompt is prepended to the
    generic checklist (see ``llm_task_eval`` for details).
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

    prompt = _persona_prefix(kind) + CODE_EVAL_PROMPT.format(
        code_files=json.dumps(files_content, indent=2),
        task_description=task_description,
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
