"""
Schema models for the multiagent infrastructure assessment flow.

This module contains all JSON schemas used for OpenAI API calls with structured outputs.
Schemas are organized by their purpose and usage in the task generation and evaluation flow.
"""

# ============================================================================
# TASK GENERATION SCHEMAS
# ============================================================================

ANSWER_CODE_SCHEMA = {
    "name": "answer_code_response",
    "schema": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "description": "Array of file objects. Each item is {path, content}.",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative file path within the answer repo (e.g. 'app/main.py')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Full file contents as a single string, including newlines"
                        }
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False
                }
            },
            "steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of step-by-step solution instructions"
            }
        },
        "required": ["files", "steps"],
        "additionalProperties": False
    },
    "strict": True
}


# ============================================================================
# EVALUATION SCHEMAS
# ============================================================================

EVAL_RESPONSE_SCHEMA = {
    "name": "eval_response",
    "schema": {
        "type": "object",
        "properties": {
            "pass": {
                "type": "boolean",
                "description": "Whether the evaluation passed or failed"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of issues found (empty if passed)"
            },
            "validated_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of criteria that were validated/met"
            },
            "feedback": {
                "type": "string",
                "description": "Detailed feedback if evaluation failed"
            }
        },
        "required": ["pass", "issues", "validated_criteria", "feedback"],
        "additionalProperties": False
    },
    "strict": True
}

