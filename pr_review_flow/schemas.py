"""JSON schemas for PR Review structured LLM output."""

BASE_REPO_SCHEMA = {
    "name": "base_repo_response",
    "schema": {
        "type": "object",
        "properties": {
            "code_files": {
                "type": "object",
                "description": "File paths as keys, file contents as values",
                "additionalProperties": {"type": "string"}
            }
        },
        "required": ["code_files"],
        "additionalProperties": False
    },
    "strict": False
}

PR_GENERATION_SCHEMA = {
    "name": "pr_generation_response",
    "schema": {
        "type": "object",
        "properties": {
            "pr_title": {
                "type": "string",
                "description": "Realistic PR title"
            },
            "pr_description": {
                "type": "string",
                "description": "PR body/description as the developer would write it"
            },
            "modified_files": {
                "type": "object",
                "description": "Files modified by the PR (filepath: new content)",
                "additionalProperties": {"type": "string"}
            },
            "added_files": {
                "type": "object",
                "description": "New files added by the PR (filepath: content)",
                "additionalProperties": {"type": "string"}
            },
            "deleted_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File paths deleted by the PR"
            },
            "answer_key": {
                "type": "object",
                "properties": {
                    "flaws": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "string"},
                                "line_range": {"type": "string"},
                                "category": {"type": "string"},
                                "severity": {
                                    "type": "string",
                                    "enum": ["critical", "major", "minor", "nitpick"]
                                },
                                "description": {"type": "string"},
                                "correct_approach": {"type": "string"}
                            },
                            "required": ["file", "line_range", "category", "severity", "description", "correct_approach"],
                            "additionalProperties": False
                        }
                    },
                    "overall_verdict": {
                        "type": "string",
                        "enum": ["request_changes", "approve_with_comments"]
                    },
                    "pr_description_issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue": {"type": "string"},
                                "suggestion": {"type": "string"}
                            },
                            "required": ["issue", "suggestion"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["flaws", "overall_verdict", "pr_description_issues"],
                "additionalProperties": False
            }
        },
        "required": ["pr_title", "pr_description", "modified_files", "added_files", "deleted_files", "answer_key"],
        "additionalProperties": False
    },
    "strict": False
}
