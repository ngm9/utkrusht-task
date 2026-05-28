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
                "description": (
                    "True iff blocking_issues is empty. SUGGESTIONS NEVER "
                    "AFFECT pass — they are nice-to-haves only."
                )
            },
            # blocking_issues: things that MUST be fixed before the task can
            # ship. Drive the retry loop. Critics must NOT invent new
            # requirements not stated in the task description here.
            "blocking_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Things that MUST be fixed before the task ships. "
                    "Only items that fail one of the explicit checklist "
                    "criteria in the prompt belong here. Do NOT add "
                    "production-readiness / observability / caching / "
                    "extra-feature demands unless the task description "
                    "explicitly mentions them."
                )
            },
            # suggestions: nice-to-haves the critic noticed but that do
            # NOT block. Stored on eval_info for human review, never
            # surfaced in the retry loop.
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Nice-to-have improvements that do NOT block. Stored "
                    "for human review only."
                )
            },
            "validated_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of criteria that were validated/met"
            },
            # Legacy fields kept for back-compat with callers that haven't
            # migrated. Critics should populate issues = blocking_issues
            # (same content) so legacy readers still work.
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "LEGACY — mirrors blocking_issues. New callers should "
                    "read blocking_issues directly."
                )
            },
            "feedback": {
                "type": "string",
                "description": "Detailed feedback if evaluation failed"
            }
        },
        "required": [
            "pass", "blocking_issues", "suggestions",
            "validated_criteria", "issues", "feedback"
        ],
        "additionalProperties": False
    },
    "strict": True
}

