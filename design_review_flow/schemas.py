"""JSON schemas for Design Review structured LLM output."""

FLAW_SPEC_SCHEMA = {
    "name": "flaw_spec_response",
    "schema": {
        "type": "object",
        "properties": {
            "source_file": {
                "type": "string",
                "description": "Library entry ID"
            },
            "target_screens": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Screens where flaws are injected"
            },
            "flaws": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "screen": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "visual_hierarchy",
                                "accessibility",
                                "information_architecture",
                                "copy_microcopy",
                                "consistency",
                                "user_flow"
                            ]
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "major", "minor"]
                        },
                        "instruction": {
                            "type": "string",
                            "description": "Exact change to apply in Figma"
                        },
                        "target_layer": {
                            "type": "string",
                            "description": "Exact Figma layer name from layer tree"
                        },
                        "rationale": {
                            "type": "string",
                            "description": "UX principle this flaw violates"
                        }
                    },
                    "required": ["id", "screen", "type", "severity", "instruction", "target_layer", "rationale"],
                    "additionalProperties": False
                }
            },
            "answer_key": {
                "type": "object",
                "properties": {
                    "flaws_summary": {"type": "string"},
                    "expected_findings": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "overall_quality": {"type": "string"}
                },
                "required": ["flaws_summary", "expected_findings", "overall_quality"],
                "additionalProperties": False
            }
        },
        "required": ["source_file", "target_screens", "flaws", "answer_key"],
        "additionalProperties": False
    },
    "strict": False
}


CANDIDATE_BRIEF_SCHEMA = {
    "name": "candidate_brief_response",
    "schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "domain_context": {"type": "string"},
            "constraints": {
                "type": "array",
                "items": {"type": "string"}
            },
            "change_requests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["critique", "redesign"]
                        },
                        "prompt": {"type": "string"}
                    },
                    "required": ["type", "prompt"],
                    "additionalProperties": False
                }
            },
            "submission_requirements": {
                "type": "object",
                "properties": {
                    "figma_link": {"type": "string"},
                    "written_rationale": {"type": "string"}
                },
                "required": ["figma_link", "written_rationale"],
                "additionalProperties": False
            },
            "time_limit_minutes": {"type": "integer"}
        },
        "required": ["title", "domain_context", "constraints", "change_requests", "submission_requirements", "time_limit_minutes"],
        "additionalProperties": False
    },
    "strict": False
}


EVALUATION_RUBRIC_SCHEMA = {
    "name": "evaluation_rubric_response",
    "schema": {
        "type": "object",
        "properties": {
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "weight": {"type": "integer"},
                        "scoring": {
                            "type": "object",
                            "properties": {
                                "excellent": {"type": "string"},
                                "good": {"type": "string"},
                                "acceptable": {"type": "string"},
                                "poor": {"type": "string"}
                            },
                            "required": ["excellent", "good", "acceptable", "poor"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["name", "weight", "scoring"],
                    "additionalProperties": False
                }
            },
            "bonus_points": {"type": "string"}
        },
        "required": ["criteria", "bonus_points"],
        "additionalProperties": False
    },
    "strict": False
}
