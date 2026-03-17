"""PR Review utilities: branch naming, scenario parsing, validation, cost tracking."""

import re
import json
import random
import string
from pathlib import Path
from typing import Dict, List, Optional

from logger_config import logger


def slugify_branch_name(pr_title: str) -> str:
    """Convert PR title to a valid git branch name with collision-avoiding suffix."""
    slug = re.sub(r'[^a-z0-9/\-]+', '-', pr_title.lower()).strip('-')
    if not slug.startswith(('feature/', 'fix/', 'refactor/', 'chore/')):
        slug = f"feature/{slug}"
    suffix = ''.join(random.choices(string.hexdigits.lower(), k=4))
    return f"{slug}-{suffix}"


def parse_pr_review_scenario(scenario_text: str) -> Dict[str, str]:
    """Parse a PR review scenario into its three sections.

    Returns dict with keys: project_context, pr_intent, injected_flaws.
    """
    sections = {}
    current_key = None
    current_lines = []

    for line in scenario_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('**Project Context:**'):
            if current_key:
                sections[current_key] = '\n'.join(current_lines).strip()
            current_key = 'project_context'
            current_lines = [stripped.replace('**Project Context:**', '').strip()]
        elif stripped.startswith('**PR Intent:**'):
            if current_key:
                sections[current_key] = '\n'.join(current_lines).strip()
            current_key = 'pr_intent'
            current_lines = [stripped.replace('**PR Intent:**', '').strip()]
        elif stripped.startswith('**Injected Flaws:**'):
            if current_key:
                sections[current_key] = '\n'.join(current_lines).strip()
            current_key = 'injected_flaws'
            current_lines = [stripped.replace('**Injected Flaws:**', '').strip()]
        else:
            if current_key:
                current_lines.append(stripped)

    if current_key:
        sections[current_key] = '\n'.join(current_lines).strip()

    return sections


def validate_modified_files(modified_files: dict, base_repo_files: dict) -> List[str]:
    """Check that all modified_files keys exist in base_repo_files. Returns list of invalid paths."""
    invalid = []
    for path in modified_files:
        if path not in base_repo_files:
            invalid.append(path)
    return invalid


def format_competencies_with_scopes(competencies: list) -> str:
    """Format competencies with scopes for prompt injection."""
    parts = []
    for comp in competencies:
        name = comp.get("name", "Unknown")
        proficiency = comp.get("proficiency", "BASIC").upper()
        scope = comp.get("scope", "No scope provided.")
        parts.append(f"- {name} ({proficiency}):\n  Scope: {scope}")
    return "\n\n".join(parts)


def count_source_files(code_files: dict) -> int:
    """Count source files excluding README, .gitignore, and config files."""
    skip_patterns = {'readme.md', '.gitignore', '.env.example', '.env'}
    config_extensions = {'.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.lock'}
    count = 0
    for path in code_files:
        filename = path.split('/')[-1].lower()
        if '.' in filename:
            _, ext = filename.rsplit('.', 1)
        else:
            ext = ''
        if filename in skip_patterns:
            continue
        if ext and f'.{ext}' in config_extensions and filename not in {'package.json', 'tsconfig.json'}:
            continue
        count += 1
    return count


def extract_usage(response) -> Dict:
    """Extract token usage from an OpenAI Responses API response."""
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }
    return {"input_tokens": 0, "output_tokens": 0}


PRICING = {
    "gpt-5-nano-2025-08-07": {"input": 0.50, "output": 2.00},
    "gpt-5.1-2025-11-13": {"input": 2.00, "output": 8.00},
}


def calculate_cost(total_usage: Dict, model: str) -> float:
    """Calculate cost in USD from token usage."""
    prices = PRICING.get(model, {"input": 1.25, "output": 10.00})
    input_cost = (total_usage["input_tokens"] / 1_000_000) * prices["input"]
    output_cost = (total_usage["output_tokens"] / 1_000_000) * prices["output"]
    return input_cost + output_cost


def format_cost_summary(usage_by_model: Dict) -> str:
    """Format a cost summary string."""
    lines = ["Cost Breakdown:"]
    grand_total_cost = 0.0
    for model, usage in usage_by_model.items():
        cost = calculate_cost(usage, model)
        grand_total_cost += cost
        lines.append(f"  {model}: {usage['input_tokens']:,} in + {usage['output_tokens']:,} out = ${cost:.6f}")
    lines.append(f"  Total: ${grand_total_cost:.6f}")
    return "\n".join(lines)


def save_pr_review_locally(task_name: str, base_repo_files: dict, pr_data: dict, eval_info: dict):
    """Save generated PR review task files locally for inspection."""
    base_dir = Path(__file__).parent.parent / "infra_assets" / "pr_review_tasks" / task_name

    # Save base repo files
    repo_dir = base_dir / "base_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)
    for filepath, content in base_repo_files.items():
        file_path = repo_dir / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    # Save PR files
    pr_dir = base_dir / "pr_files"
    pr_dir.mkdir(parents=True, exist_ok=True)
    all_pr_files = {**pr_data.get("modified_files", {}), **pr_data.get("added_files", {})}
    for filepath, content in all_pr_files.items():
        file_path = pr_dir / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    # Save answer key
    answer_key = pr_data.get("answer_key", {})
    (base_dir / "answer_key.json").write_text(json.dumps(answer_key, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save metadata
    metadata = {
        "pr_title": pr_data.get("pr_title", ""),
        "pr_description": pr_data.get("pr_description", ""),
        "deleted_files": pr_data.get("deleted_files", []),
        "eval_info": eval_info,
    }
    (base_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"Saved PR review task locally: {base_dir}")
    return base_dir
