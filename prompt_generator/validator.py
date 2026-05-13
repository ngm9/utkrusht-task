"""
Post-generation validator — deterministic checks on a generated prompt file.

Runs AFTER the DSPy verifier passes. Catches structural problems the LLM might
miss: invalid Python syntax, missing PROMPT_REGISTRY, wrong format variables,
etc. These are non-negotiable; if any fail the agent must regenerate.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Optional


# Format variables every prompt template must include in its INSTRUCTIONS string.
# Mirrors the placeholders used in scenario_generator and multiagent.py.
REQUIRED_FORMAT_VARS = {
    "organization_background",
    "role_context",
    "competencies",
    "real_world_task_scenarios",
}

# Optional format vars — present in many but not all prompt files.
OPTIONAL_FORMAT_VARS = {"minutes_range", "question_prompt", "sample_dataset"}

# JSON-schema keys the downstream task-generation LLM must emit. The pipeline
# (multiagent.py) reads these off task_data and stores them in Supabase:
#   - `answer`  → top-level `tasks.answer` column (server-side solution, never
#                 shown to candidates — `task_blob` is the candidate-visible blob)
# If a prompt template omits any of these from its REQUIRED OUTPUT JSON STRUCTURE
# block, the LLM won't produce them and the corresponding DB column stays empty.
REQUIRED_JSON_SCHEMA_KEYS = ("answer",)


@dataclass
class ValidationResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    registry_key: Optional[str] = None

    def add_issue(self, msg: str) -> None:
        self.issues.append(msg)
        self.passed = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def _parses_as_python(source: str) -> Optional[str]:
    """Return None if source parses, else the SyntaxError message."""
    try:
        ast.parse(source)
        return None
    except SyntaxError as e:
        return f"{e.msg} (line {e.lineno}, col {e.offset})"


def _extract_registry_key(source: str) -> Optional[str]:
    """Find the PROMPT_REGISTRY key inside the generated source."""
    # Look for: PROMPT_REGISTRY = { "Some Key": [...] }
    match = re.search(
        r'PROMPT_REGISTRY\s*=\s*\{\s*"([^"]+)"\s*:',
        source,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def _extract_format_vars_in_string(source: str) -> set[str]:
    """Find all {variable} placeholders in any triple-quoted string.

    We don't try to be perfect — just extract what looks like format keys.
    """
    found: set[str] = set()
    # Match {word} but not {{word}} (escaped braces)
    for match in re.finditer(r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})', source):
        found.add(match.group(1))
    return found


def _missing_json_schema_keys(source: str) -> list[str]:
    """Return required JSON-schema keys that don't appear as JSON keys in source.

    Looks for `"key":` (quoted, followed by colon). Prose mentions like
    `"answer" field` won't match because there's no colon after the quoted string.
    """
    missing = []
    for key in REQUIRED_JSON_SCHEMA_KEYS:
        if not re.search(rf'"{re.escape(key)}"\s*:', source):
            missing.append(key)
    return missing


def _expected_registry_key(competencies: list[dict], proficiency: str) -> str:
    """Compute the expected PROMPT_REGISTRY key for a (competencies, proficiency)
    combination. Format: 'Name1 (LEVEL), Name2 (LEVEL)' — alphabetically sorted.
    """
    proficiency = proficiency.upper()
    parts = sorted(f"{c['name']} ({proficiency})" for c in competencies)
    return ", ".join(parts)


def validate_prompt_file(
    source: str,
    expected_competencies: list[dict],
    expected_proficiency: str,
) -> ValidationResult:
    """Validate a generated prompt file source.

    Args:
        source:               full .py file content
        expected_competencies: list of {"name", "proficiency"} dicts
        expected_proficiency:  e.g. "BASIC"
    """
    result = ValidationResult(passed=True)

    # 1. Must parse as Python
    syntax_err = _parses_as_python(source)
    if syntax_err:
        result.add_issue(f"Python syntax error: {syntax_err}")
        return result  # bail early — other checks need a parsed AST

    # 2. Must define PROMPT_REGISTRY
    if "PROMPT_REGISTRY" not in source:
        result.add_issue("Missing PROMPT_REGISTRY definition.")
        return result

    # 3. Registry key must match expected format
    actual_key = _extract_registry_key(source)
    result.registry_key = actual_key
    if not actual_key:
        result.add_issue("Could not extract PROMPT_REGISTRY key from source.")
    else:
        expected_key = _expected_registry_key(expected_competencies, expected_proficiency)
        # Allow either alphabetical or input-order; both seen in existing files.
        input_order_key = ", ".join(
            f"{c['name']} ({expected_proficiency.upper()})" for c in expected_competencies
        )
        valid_keys = {expected_key, input_order_key}
        if actual_key not in valid_keys:
            result.add_issue(
                f"PROMPT_REGISTRY key '{actual_key}' does not match expected '{expected_key}' "
                f"or '{input_order_key}'."
            )

    # 4. Must contain all required format variables
    found_vars = _extract_format_vars_in_string(source)
    missing = REQUIRED_FORMAT_VARS - found_vars
    if missing:
        result.add_issue(
            f"Missing required format variables: {sorted(missing)}. "
            f"Found: {sorted(found_vars)}"
        )

    # 5. Must request all required JSON-schema keys from the downstream LLM.
    # Without these, the task-generation step produces JSON missing fields that
    # multiagent.py expects when writing to Supabase (e.g. the server-side
    # `answer` column).
    missing_keys = _missing_json_schema_keys(source)
    if missing_keys:
        quoted = ", ".join(f'"{k}"' for k in missing_keys)
        result.add_issue(
            f"REQUIRED OUTPUT JSON STRUCTURE is missing required key(s): {quoted}. "
            f"multiagent.py reads these off the generated task and writes them to Supabase. "
            f"Add them to the JSON template inside the INSTRUCTIONS prompt."
        )

    # 6. Must define the three prompt variables (CONTEXT, INPUT_AND_ASK, INSTRUCTIONS)
    # Existing files use the pattern PROMPT_<TECH>_<LEVEL>_<STAGE>
    expected_stages = ("CONTEXT", "INPUT_AND_ASK", "INSTRUCTIONS")
    missing_stages = [
        stage for stage in expected_stages
        if not re.search(rf"PROMPT_[A-Z0-9_]+_{stage}\s*=", source)
    ]
    if missing_stages:
        result.add_warning(
            f"Could not find PROMPT_*_{{stage}} for stages: {missing_stages}. "
            "This is OK if the file uses a different naming convention but reduces consistency."
        )

    return result
