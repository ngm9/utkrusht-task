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


# ============================================================================
# CONTENT-QUALITY JUDGE + REWRITER SCHEMA
# ============================================================================
#
# ONE LLM call per attempt does BOTH (1) judge the candidate task on every
# content-quality rule (title shape, short_overview 3-part shape + count,
# bullet hygiene, question length, framing + relevance) AND (2) emit a
# corrected version of every failing field. The runner splices the
# rewrites into the candidate and proceeds — no retry burned on
# content-quality alone.
#
# Caller: task_quality.semantic.judge_and_rewrite_task_quality

CONTENT_QUALITY_RESPONSE_SCHEMA = {
    "name": "content_quality_response",
    "schema": {
        "type": "object",
        "properties": {
            "issues_found": {
                "type": "array",
                "description": (
                    "Every content-quality issue the judge detected. "
                    "Empty when the task already satisfies every rule."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "field_path": {
                            "type": "string",
                            "description": (
                                "Top-level candidate field the issue applies to: "
                                "one of 'title', 'short_overview', 'outcomes', "
                                "'pre_requisites', 'question'. May include an "
                                "index for list-typed fields, e.g. 'outcomes[2]'."
                            ),
                        },
                        "reason": {
                            "type": "string",
                            "description": "Concise, operator-readable description of what is wrong.",
                        },
                    },
                    "required": ["field_path", "reason"],
                    "additionalProperties": False,
                },
            },
            "rewrites": {
                "type": "object",
                "description": (
                    "Corrected values for every failing field. Set the key "
                    "to null when no rewrite is needed (field already passes)."
                ),
                "properties": {
                    "title": {
                        "type": ["string", "null"],
                        "description": (
                            "Human-readable Title Case title. Example: "
                            "'Design Voice Agent Eval Framework'. NOT a "
                            "kebab slug like 'voice-agent-eval-framework'."
                        ),
                    },
                    "short_overview": {
                        "type": ["array", "null"],
                        "description": (
                            "EXACTLY three bullets. "
                            "Bullet 0 describes the task artifact, "
                            "bullet 1 describes the candidate goal, "
                            "bullet 2 describes the expected outcome. "
                            "No leading bullet glyphs (•/-/*) and no "
                            "residual Markdown markers (**X**:)."
                        ),
                        "items": {"type": "string"},
                    },
                    "outcomes": {
                        "type": ["array", "null"],
                        "description": (
                            "Candidate-readable bullets, each anchored to "
                            "this specific task (no generic boilerplate). "
                            "No leading glyphs, no **X**: markers. No count cap."
                        ),
                        "items": {"type": "string"},
                    },
                    "pre_requisites": {
                        "type": ["array", "null"],
                        "description": (
                            "Same rules as outcomes: task-anchored, "
                            "candidate-readable sentences, no glyphs/markers. "
                            "No count cap."
                        ),
                        "items": {"type": "string"},
                    },
                    "question": {
                        "type": ["string", "null"],
                        "description": (
                            "Short, direct candidate-facing question, "
                            "120–1500 chars. Setup detail belongs in the README."
                        ),
                    },
                },
                "required": ["title", "short_overview", "outcomes", "pre_requisites", "question"],
                "additionalProperties": False,
            },
        },
        "required": ["issues_found", "rewrites"],
        "additionalProperties": False,
    },
    "strict": True,
}

