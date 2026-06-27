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

# Sample arguments used to dry-run ``str.format`` on each PROMPT_REGISTRY
# template. The downstream task-generation pipeline supplies these exact keys —
# any OTHER ``{...}`` substring in a template must be escaped as ``{{...}}``.
_FMT_DRYRUN_ARGS = {key: "<x>" for key in (REQUIRED_FORMAT_VARS | OPTIONAL_FORMAT_VARS)}

# JSON-schema keys the downstream task-generation LLM must emit. The pipeline
# (multiagent.py + utils.generate_task_with_code) reads these off task_data.
# A prompt that instructs synonym keys (task_title / files / context) makes
# multiagent.py read every field as empty -> a HOLLOW task. This was confirmed
# during the 2026-05-15 validation run as the PHP+Laravel failure root cause.
#
#   - `code_files` → file map written to the GitHub repo
#   - `question`   → candidate-facing task description
#   - `answer`     → top-level `tasks.answer` column (server-side solution)
#
# `name`/`title` is checked separately because EITHER is accepted by multiagent.
REQUIRED_JSON_SCHEMA_KEYS = ("code_files", "question", "answer")

# At least one of these must appear as a JSON key — multiagent.py reads
# `task_data.get("title") or task_data.get("name")`.
TITLE_KEY_ALTERNATIVES = ("name", "title")


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


def _json_key_present(source: str, key: str) -> bool:
    """True if `key` appears as a JSON key (`"key":`) anywhere in source.

    Prose mentions like `"answer" field` won't match — there's no colon after
    the quoted string.
    """
    return bool(re.search(rf'"{re.escape(key)}"\s*:', source))


def _missing_json_schema_keys(source: str) -> list[str]:
    """Return canonical output-schema keys absent from the prompt source.

    Covers both the always-required keys and the title alternatives (where any
    one of `name`/`title` satisfies the requirement).
    """
    missing = [k for k in REQUIRED_JSON_SCHEMA_KEYS if not _json_key_present(source, k)]
    if not any(_json_key_present(source, k) for k in TITLE_KEY_ALTERNATIVES):
        missing.append("/".join(TITLE_KEY_ALTERNATIVES))
    return missing


def _simulate_format_call(source: str) -> list[str]:
    """Exec the source in a sandbox namespace and dry-run ``str.format`` on
    every template inside PROMPT_REGISTRY. Returns a list of issues.

    Catches the most common LLM mistake: embedding a raw JSON example like
    ``{"title": "..."}`` without doubling the braces. When that lands on disk,
    ``utils.get_task_prompt_by_technology_stack`` crashes with
    ``KeyError: '\\n  "title"'`` and no task is ever generated.
    """
    issues: list[str] = []
    try:
        ns: dict = {}
        exec(compile(source, "<prompt_dryrun>", "exec"), ns)
    except Exception as e:
        return [f"Could not exec source to dry-run str.format(): {type(e).__name__}: {e}"]
    registry = ns.get("PROMPT_REGISTRY")
    if not isinstance(registry, dict):
        return ["PROMPT_REGISTRY is not a dict after exec; cannot dry-run format()"]
    for key, templates in registry.items():
        if not isinstance(templates, (list, tuple)):
            issues.append(f"PROMPT_REGISTRY[{key!r}] is not a list of templates")
            continue
        for i, template in enumerate(templates):
            if not isinstance(template, str):
                issues.append(f"PROMPT_REGISTRY[{key!r}][{i}] is not a str")
                continue
            try:
                template.format(**_FMT_DRYRUN_ARGS)
            except KeyError as e:
                bad = repr(e.args[0]) if e.args else "?"
                preview = bad[:80] + ("..." if len(bad) > 80 else "")
                issues.append(
                    f"PROMPT_REGISTRY[{key!r}][{i}] str.format() raises KeyError on placeholder "
                    f"{preview} — looks like an unescaped {{...}} inside the template (typically "
                    f"a JSON example). Double the braces to '{{{{' / '}}}}' or remove the example."
                )
            except (IndexError, ValueError) as e:
                issues.append(
                    f"PROMPT_REGISTRY[{key!r}][{i}] str.format() raises "
                    f"{type(e).__name__}: {e} — malformed format string."
                )
    return issues


def _expected_registry_key(competencies: list[dict], proficiency: str) -> str:
    """Compute the expected PROMPT_REGISTRY key for a (competencies, proficiency)
    combination. Format: 'Name1 (LEVEL), Name2 (LEVEL)' — alphabetically sorted.
    """
    proficiency = proficiency.upper()
    parts = sorted(f"{c['name']} ({proficiency})" for c in competencies)
    return ", ".join(parts)


# ── Agent-realness checks ───────────────────────────────────────────────────
# Agent-engineering tasks MUST integrate a REAL LLM/agent loop. The 2026-06 batch
# shipped fake LLMs (FakeLLM / regex intent parsers / time.sleep "agents") because
# the prompt template encoded "LLM-free / deterministic / stub" framing meant only
# for the readiness GATE. The DSPy verifier is intentionally OFF, so this
# deterministic validator is the guard.
# See docs/plans/2026-06-19-agent-task-fake-llm-rootcause.md
_AGENT_COMPETENCY_NAMES = {
    "multi-agent systems",
    "production agent engineering",
    "tool use for agents",
    "context engineering",
}

# Phrases in the generated PROMPT that signal it will produce a FAKE agent.
_AGENT_FAKE_PATTERNS = (
    "fakellm",
    "fake llm",
    "mock llm",
    "mocked llm",
    "stand-in for the llm",
    "stand in for the llm",
    "stand-in for the model",
    "deterministic stand-in",
    "no real llm",
    "without a real llm",
    "llm-free task",
    "simulate the agent",
    "simulate agent work",
    "sleep to simulate",
)

# At least one of these must appear — the prompt must AFFIRMATIVELY require a real
# model / agent loop in the generated task.
_AGENT_REAL_PATTERNS = (
    "real llm",
    "live llm",
    "actual llm",
    "real model",
    "live model",
    "call a real",
    "calls a real",
    "real agent loop",
    "genuine agent loop",
    "litellm",
)


def _is_agent_combo(competencies: list[dict]) -> bool:
    return any(
        (c.get("name") or "").strip().lower() in _AGENT_COMPETENCY_NAMES
        for c in competencies
    )


# Negation cues — when one appears just before a fake-pattern, the prompt is
# PROHIBITING the fake (good), not mandating it. Lets a fixed template say
# "NEVER use a FakeLLM" without tripping the check.
_NEGATIONS = (
    "never", "not ", "n't", "no ", "do not", "don't", "forbid", "avoid",
    "without", "must not", "instead of", "rather than", "no fake",
)


def _unnegated_fake_hits(low: str) -> list[str]:
    """Fake-pattern phrases that appear WITHOUT a nearby negation cue (within the
    preceding 60 chars). A prohibition ("never ship a FakeLLM") is not flagged."""
    flagged: set[str] = set()
    for p in _AGENT_FAKE_PATTERNS:
        start = 0
        while True:
            i = low.find(p, start)
            if i == -1:
                break
            window = low[max(0, i - 60):i]
            if not any(neg in window for neg in _NEGATIONS):
                flagged.add(p)
            start = i + len(p)
    return sorted(flagged)


def _agent_realness_issues(source: str) -> list[str]:
    """Issues when an agent-competency prompt would yield a FAKE LLM/agent."""
    low = source.lower()
    issues: list[str] = []
    hits = _unnegated_fake_hits(low)
    if hits:
        issues.append(
            "Agent prompt encodes a FAKE LLM/agent (found: "
            + ", ".join(hits)
            + "). Agent-competency tasks MUST integrate a REAL LLM/agent loop — the "
            "candidate-filled stubs are the agent logic (context build, tool dispatch, "
            "retry, parsing), NOT a stand-in model. Remove FakeLLM / regex intent / "
            "time.sleep simulation; require a real model call (provider SDK / litellm)."
        )
    if not any(p in low for p in _AGENT_REAL_PATTERNS):
        issues.append(
            "Agent prompt does not MANDATE a real LLM/agent loop. The generated prompt "
            "must require the task to call a real model and build a genuine agent loop "
            "(not a deterministic stand-in). 'LLM-free / no API key' applies ONLY to the "
            "readiness gate, never to the task's agent logic."
        )
    return issues


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

    # 5. Must instruct the downstream LLM to use the CANONICAL output JSON keys.
    # multiagent.py reads `code_files`, `question`, `answer`, and `name`/`title`
    # off the generated task. A prompt that instructs synonym keys (task_title,
    # files, context, ...) makes every field read empty -> a HOLLOW task. This
    # was the PHP+Laravel failure root cause (2026-05-15 validation run, F10).
    missing_keys = _missing_json_schema_keys(source)
    if missing_keys:
        quoted = ", ".join(f'"{k}"' for k in missing_keys)
        result.add_issue(
            f"INSTRUCTIONS prompt does not request the canonical output JSON key(s): {quoted}. "
            f"multiagent.py reads exactly these names — synonyms like 'task_title', 'files', "
            f"'context' cause a hollow task. Use the canonical keys in the output schema "
            f"inside the INSTRUCTIONS prompt."
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

    # 7. Every template inside PROMPT_REGISTRY must survive
    # ``str.format(**fmt_args)`` with the known placeholder set. Catches
    # unescaped JSON examples / dict literals — the single most common LLM
    # mistake we observed in the smoke test.
    for issue in _simulate_format_call(source):
        result.add_issue(issue)

    # 8. Agent competencies MUST yield a REAL LLM/agent loop (not a fake/stub/sleep
    # stand-in). The DSPy verifier is OFF — this deterministic check is the guard.
    if _is_agent_combo(expected_competencies):
        for issue in _agent_realness_issues(source):
            result.add_issue(issue)

    return result
