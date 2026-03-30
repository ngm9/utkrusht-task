# PR Review Task Category Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PR Review assessment pipeline that generates GitHub repos with intentional flawed PRs for candidates to review.

**Architecture:** Two-phase LLM generation (base repo, then flawed PR + answer key) with evaluation gates, followed by GitHub operations (repo creation, branch, PR) and Supabase storage. Lives in `pr_review_flow/` as a separate module following the `non_tech_flow/` precedent.

**Tech Stack:** Python, OpenAI Responses API (gpt-5-nano for evals, configurable for generation), PyGithub, Supabase, Click (CLI)

**Spec:** `docs/superpowers/specs/2026-03-16-pr-review-task-category-design.md`

---

## Chunk 1: Schemas, Prompts, and Evaluation

### Task 1: Create package structure and schemas

**Files:**

- Create: `pr_review_flow/__init__.py`
- Create: `pr_review_flow/schemas.py`
- Create: `pr_review_flow/prompts/__init__.py`

- [ ] **Step 1: Create `pr_review_flow/__init__.py`**

```python
"""
PR Review Task Generation package.

Generates assessment tasks where candidates review GitHub PRs with intentional flaws.

Usage as CLI:
    python -m pr_review_flow --competency-file <path> --background-file <path> --scenarios-file <path>
"""
```

- [ ] **Step 2: Create `pr_review_flow/schemas.py`**

Define three JSON schemas for structured LLM output:

```python
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
    "strict": True
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
    "strict": True
}

# Reuse EVAL_RESPONSE_SCHEMA from root schemas.py — same structure works for PR review evals
```

- [ ] **Step 3: Create `pr_review_flow/prompts/__init__.py`**

```python
"""PR Review prompt templates."""

from pr_review_flow.prompts.base_repo_prompts import BASE_REPO_SYSTEM_PROMPT, BASE_REPO_GENERATION_PROMPT
from pr_review_flow.prompts.pr_generation_prompts import PR_SYSTEM_PROMPT, PR_GENERATION_PROMPT
from pr_review_flow.prompts.eval_prompts import BASE_REPO_EVAL_PROMPT, PR_EVAL_PROMPT
```

---

### Task 2: Create base repo generation prompts

**Files:**

- Create: `pr_review_flow/prompts/base_repo_prompts.py`

- [ ] **Step 1: Write `base_repo_prompts.py`**

```python
"""Prompts for Phase 1: generating clean, well-structured base repositories."""

BASE_REPO_SYSTEM_PROMPT = """You are a senior software engineer writing clean, production-quality code for a real project. Your code should:
- Follow industry best practices and idiomatic patterns for the tech stack
- Have consistent naming, error handling, and structure throughout
- Be realistic — not a tutorial or toy example
- Include a clear README.md describing the project
- Have proper configuration files (.gitignore, dependency files, etc.)"""

BASE_REPO_GENERATION_PROMPT = """Generate a complete, well-structured codebase for the following project.

COMPETENCIES:
{competencies_with_scopes}

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
- Generate a realistic project with at least 4-5 source code files (excluding README, .gitignore, config files)
- Code must follow consistent patterns throughout (naming conventions, error handling, project structure)
- Include proper dependency/config files for the tech stack
- The codebase should be substantial enough that a PR against it is meaningful to review
- README.md should describe what the project does, its structure, and how to run it
- Do NOT include any intentional bugs or issues — this is the "good" baseline code

OUTPUT FORMAT:
Return ONLY a JSON object with a single key "code_files" containing file paths as keys and file contents as values. No markdown, no explanation.

{eval_feedback_block}"""

EVAL_FEEDBACK_BLOCK = """PREVIOUS EVALUATION FEEDBACK — FIX THESE ISSUES:
{feedback_text}"""

EVAL_FEEDBACK_BLOCK_EMPTY = ""
```

---

### Task 3: Create PR generation prompts

**Files:**

- Create: `pr_review_flow/prompts/pr_generation_prompts.py`

- [ ] **Step 1: Write `pr_generation_prompts.py`**

```python
"""Prompts for Phase 2: generating flawed PRs with answer keys."""

PR_SYSTEM_PROMPT = """You are simulating a developer submitting a pull request. The PR should look like genuine work — it implements real functionality but contains realistic mistakes that a code reviewer should catch. The flaws should NOT look planted or artificial. They should be the kind of mistakes a real developer makes under time pressure or from inexperience."""

PR_GENERATION_PROMPT = """Generate a pull request with intentional flaws against the following codebase.

BASE REPOSITORY FILES:
{base_repo_files}

PR INTENT:
{pr_intent}

INJECTED FLAWS (introduce ALL of these — these are NOT shown to the candidate):
{injected_flaws}

REQUIREMENTS:
- The PR should implement the feature/fix described in PR Intent
- Introduce ALL the flaws listed above naturally — they should look like real developer mistakes
- The PR title and description should be what a developer would actually write (the description itself may be vague/incomplete if that is one of the listed flaws)
- modified_files: provide the COMPLETE new content of each modified file (not a diff)
- added_files: provide complete content of any new files the PR introduces
- deleted_files: list any files the PR removes (empty array if none)
- Generate a complete answer_key listing every intentional flaw with file, line_range, category, severity, description, and correct_approach
- The overall_verdict should be "request_changes" if any flaw is critical/major, "approve_with_comments" if all flaws are minor/nitpick
- Include pr_description_issues if the PR description itself has problems

OUTPUT FORMAT:
Return ONLY a JSON object with keys: pr_title, pr_description, modified_files, added_files, deleted_files, answer_key. No markdown, no explanation.

{eval_feedback_block}"""

EVAL_FEEDBACK_BLOCK = """PREVIOUS EVALUATION FEEDBACK — FIX THESE ISSUES:
{feedback_text}"""

EVAL_FEEDBACK_BLOCK_EMPTY = ""
```

---

### Task 4: Create evaluation prompts

**Files:**

- Create: `pr_review_flow/prompts/eval_prompts.py`

- [ ] **Step 1: Write `eval_prompts.py`**

```python
"""Evaluation prompts for PR Review generation gates."""

BASE_REPO_EVAL_PROMPT = """Evaluate this generated base repository for use in a PR review assessment.

COMPETENCIES BEING TESTED:
{competencies_text}

CODE FILES:
{code_files_text}

Evaluate STRICTLY against these criteria:

1. CODE QUALITY: Is the code clean, well-structured, and following best practices for the tech stack?
2. CONSISTENCY: Are patterns consistent throughout (naming, error handling, structure)?
3. REALISM: Does this look like a real project, not a tutorial or toy example?
4. MINIMUM SIZE: Are there at least 3 source code files (excluding README, .gitignore, config files)?
5. REVIEWABILITY: Is the codebase structured enough that a PR against it would be meaningful to review?

If the base repo PASSES all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of criteria met"],
  "feedback": ""
}}

If the base repo FAILS any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["specific issues found"],
  "validated_criteria": ["criteria that were met"],
  "feedback": "detailed explanation of what needs to be fixed"
}}"""

PR_EVAL_PROMPT = """Evaluate this generated PR and answer key for a code review assessment.

BASE REPOSITORY (the clean codebase the PR is against):
{base_repo_text}

PR FILES (modified/added by the PR):
{pr_files_text}

ANSWER KEY:
{answer_key_text}

Evaluate STRICTLY against these criteria:

1. FLAW REALISM: Do the flaws look like genuine developer mistakes, not planted or artificial?
2. ANSWER KEY COMPLETENESS: Does the answer key list EVERY intentional flaw? Are there flaws in the code not captured in the answer key?
3. SEVERITY RATINGS: Are the severity ratings (critical/major/minor/nitpick) appropriate for each flaw?
4. FLAW DESCRIPTIONS: Are the descriptions clear enough to grade a candidate's review against?
5. PR COHERENCE: Does the PR actually implement what the title/description claims, despite the flaws?
6. MODIFIED FILES VALIDITY: Do all modified files exist in the base repository?

If the PR PASSES all criteria, respond in JSON:
{{
  "pass": true,
  "issues": [],
  "validated_criteria": ["list of criteria met"],
  "feedback": ""
}}

If the PR FAILS any criteria, respond in JSON:
{{
  "pass": false,
  "issues": ["specific issues found"],
  "validated_criteria": ["criteria that were met"],
  "feedback": "detailed explanation of what needs to be fixed"
}}"""
```

---

### Task 5: Create evaluation module

**Files:**

- Create: `pr_review_flow/pr_review_evals.py`

- [ ] **Step 1: Write `pr_review_evals.py`**

Follow the pattern from `evals.py` (lines 78-138). Use `EVAL_RESPONSE_SCHEMA` from root `schemas.py`. Two functions: `eval_base_repo()` and `eval_pr_and_answer_key()`. Both use `gpt-5-nano` via the Responses API with `reasoning={"effort": "medium"}` and structured JSON output.

```python
"""Evaluation gates for PR Review task generation."""

import json
from logger_config import logger
from schemas import EVAL_RESPONSE_SCHEMA
from pr_review_flow.prompts.eval_prompts import BASE_REPO_EVAL_PROMPT, PR_EVAL_PROMPT
from pr_review_flow.pr_review_utils import extract_usage

EVAL_MODEL = "gpt-5-nano-2025-08-07"


def eval_base_repo(code_files: dict, competencies: list, openai_client) -> tuple:
    """Evaluate base repo quality. Returns (eval_result_dict, usage_dict)."""
    competencies_text = "\n".join(
        f"- {c.get('name', '')} ({c.get('proficiency', '')}): {c.get('scope', '')}"
        for c in competencies
    )
    code_files_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in code_files.items()
    )
    prompt = BASE_REPO_EVAL_PROMPT.format(
        competencies_text=competencies_text,
        code_files_text=code_files_text,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"Base repo eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}


def eval_pr_and_answer_key(base_repo_files: dict, pr_data: dict, openai_client) -> tuple:
    """Evaluate PR flaws and answer key completeness. Returns (eval_result_dict, usage_dict)."""
    base_repo_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in base_repo_files.items()
    )
    pr_files = {**pr_data.get("modified_files", {}), **pr_data.get("added_files", {})}
    pr_files_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in pr_files.items()
    )
    if pr_data.get("deleted_files"):
        pr_files_text += "\n\nDeleted files: " + ", ".join(pr_data["deleted_files"])

    answer_key_text = json.dumps(pr_data.get("answer_key", {}), indent=2)

    prompt = PR_EVAL_PROMPT.format(
        base_repo_text=base_repo_text,
        pr_files_text=pr_files_text,
        answer_key_text=answer_key_text,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"PR eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}
```

---

## Chunk 2: Utilities, GitHub Operations, and Scenario Validation

### Task 6: Create PR review utilities

**Files:**

- Create: `pr_review_flow/pr_review_utils.py`

- [ ] **Step 1: Write `pr_review_utils.py`**

Contains: `slugify_branch_name()`, `parse_pr_review_scenario()`, `validate_modified_files()`, `format_competencies_with_scopes()`, cost tracking helpers.

```python
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
        _, ext = (filename.rsplit('.', 1) if '.' in filename else (filename, ''))
        if filename in skip_patterns:
            continue
        if f'.{ext}' in config_extensions and filename not in {'package.json', 'tsconfig.json'}:
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
```

---

### Task 7: Create PR review GitHub operations

**Files:**

- Create: `pr_review_flow/pr_review_github.py`

- [ ] **Step 1: Write `pr_review_github.py`**

Reuses `github_utils.create_github_repo` and `github_utils.upload_files_batch`. Adds: `create_branch_from_main()`, `upload_pr_files_to_branch()` (supports deletions via `sha=None`), `open_pull_request()`, and the top-level `create_pr_review_repo()` orchestrator.

```python
"""GitHub operations for PR Review tasks: branch creation, PR file upload, PR opening."""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple

from github import Github, InputGitTreeElement, GithubException
from dotenv import load_dotenv

from github_utils import create_github_repo, upload_files_batch

load_dotenv()
logger = logging.getLogger(__name__)

REPO_OWNER = os.getenv("REPO_OWNER")
GITHUB_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
MAX_API_RETRIES = 2


def _get_repo_obj(repo_name: str):
    """Get PyGithub repo object."""
    github = Github(GITHUB_TOKEN)
    return github.get_repo(f"{REPO_OWNER}/{repo_name}")


def _retry_on_failure(func, *args, **kwargs):
    """Retry a function up to MAX_API_RETRIES times on transient GitHub failures."""
    last_error = None
    for attempt in range(MAX_API_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except GithubException as e:
            if e.status >= 500 or e.status == 403:  # Server error or rate limit
                last_error = e
                if attempt < MAX_API_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
            raise
        except Exception as e:
            last_error = e
            if attempt < MAX_API_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_error


def create_branch_from_main(repo_obj, branch_name: str) -> str:
    """Create a new branch from main. Returns the branch name."""
    main_ref = repo_obj.get_git_ref("heads/main")
    main_sha = main_ref.object.sha
    repo_obj.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
    logger.info(f"Created branch '{branch_name}' from main ({main_sha[:8]})")
    return branch_name


def upload_pr_files_to_branch(
    repo_obj,
    branch_name: str,
    modified_files: Dict[str, str],
    added_files: Dict[str, str],
    deleted_files: List[str],
    commit_message: str = "Add feature implementation",
) -> bool:
    """Upload PR files to a branch, supporting modifications, additions, and deletions.

    Unlike upload_files_batch, this supports file deletion via tree entries with sha=None.
    """
    try:
        ref = repo_obj.get_git_ref(f"heads/{branch_name}")
        base_commit = repo_obj.get_git_commit(ref.object.sha)
        base_tree = base_commit.tree

        element_list = []

        # Modified and added files — create blobs
        all_files = {**modified_files, **added_files}
        for file_path, content in all_files.items():
            clean_path = file_path.lstrip('/')
            if isinstance(content, dict):
                content = json.dumps(content, indent=2, ensure_ascii=False)
            blob = repo_obj.create_git_blob(str(content), "utf-8")
            element_list.append(
                InputGitTreeElement(path=clean_path, mode="100644", type="blob", sha=blob.sha)
            )

        # Deleted files — tree entries with sha=None
        for file_path in deleted_files:
            clean_path = file_path.lstrip('/')
            element_list.append(
                InputGitTreeElement(path=clean_path, mode="100644", type="blob", sha=None)
            )

        new_tree = repo_obj.create_git_tree(element_list, base_tree)
        new_commit = repo_obj.create_git_commit(
            message=commit_message, tree=new_tree, parents=[base_commit]
        )
        ref.edit(new_commit.sha)

        logger.info(f"Pushed {len(all_files)} files ({len(deleted_files)} deletions) to '{branch_name}'")
        return True
    except Exception as e:
        logger.error(f"Error uploading PR files to branch: {e}")
        return False


def open_pull_request(
    repo_obj, branch_name: str, title: str, body: str, base: str = "main"
) -> str:
    """Open a pull request. Returns the PR URL."""
    pr = repo_obj.create_pull(title=title, body=body, head=branch_name, base=base)
    logger.info(f"Opened PR #{pr.number}: {pr.html_url}")
    return pr.html_url


def create_pr_review_repo(
    task_name: str,
    base_repo_files: Dict[str, str],
    pr_data: Dict,
    branch_name: str,
) -> Tuple[str, str]:
    """Full GitHub flow: create repo, push base, create branch, push PR files, open PR.

    Returns (repo_url, pr_url).
    """
    # Step 1: Create repo
    repo_name = _retry_on_failure(create_github_repo, task_name, True)
    repo_url = f"https://github.com/{REPO_OWNER}/{repo_name}"
    logger.info(f"Created repo: {repo_url}")

    repo_obj = _get_repo_obj(repo_name)

    # Step 2: Push base files to main
    success = _retry_on_failure(
        upload_files_batch, repo_obj, base_repo_files, "Initial project setup", "main"
    )
    if not success:
        raise RuntimeError(f"Failed to push base files to main. Repo created: {repo_url}")

    # Step 3: Create branch
    _retry_on_failure(create_branch_from_main, repo_obj, branch_name)

    # Step 4: Push PR files to branch
    success = _retry_on_failure(
        upload_pr_files_to_branch,
        repo_obj,
        branch_name,
        pr_data.get("modified_files", {}),
        pr_data.get("added_files", {}),
        pr_data.get("deleted_files", []),
        f"feat: {pr_data.get('pr_title', 'Add feature')}",
    )
    if not success:
        raise RuntimeError(f"Failed to push PR files to branch. Repo: {repo_url}, Branch: {branch_name}")

    # Step 5: Open PR
    pr_url = _retry_on_failure(
        open_pull_request,
        repo_obj,
        branch_name,
        pr_data.get("pr_title", "Feature implementation"),
        pr_data.get("pr_description", ""),
    )

    return repo_url, pr_url
```

---

### Task 8: Add PR review scenario validation to scenario_generator

**Files:**

- Modify: `scenario_generator/generator.py` — add `validate_pr_review_scenario_structure()` function

- [ ] **Step 1: Add PR review scenario validation function**

Add after the existing `validate_scenario_structure()` function (around line 321 of `scenario_generator/generator.py`):

```python
def validate_pr_review_scenario_structure(scenario: str, proficiency: str = "BASIC") -> bool:
    """Validate that a PR review scenario has the required three-section structure.

    Checks for:
    - Required bold-header sections: Project Context, PR Intent, Injected Flaws
    - Minimum length
    - At least 1 flaw in Injected Flaws section
    """
    if len(scenario) < 100:
        logger.warning(f"PR review scenario too short ({len(scenario)} chars)")
        return False

    required_headers = ["**Project Context:**", "**PR Intent:**", "**Injected Flaws:**"]
    for header in required_headers:
        if header not in scenario:
            logger.warning(f"PR review scenario missing required section '{header}'")
            return False

    # Check that Injected Flaws has at least one bullet
    if "**Injected Flaws:**" in scenario:
        flaws_start = scenario.index("**Injected Flaws:**") + len("**Injected Flaws:**")
        flaws_section = scenario[flaws_start:]
        bullet_count = flaws_section.count("- ")
        if bullet_count < 1:
            logger.warning("PR review scenario has no flaws listed in Injected Flaws section")
            return False

    return True
```

- [ ] **Step 2: Export the new function**

Add `validate_pr_review_scenario_structure` to the exports in `scenario_generator/__init__.py`:

```python
from scenario_generator.generator import (
    # ... existing exports ...
    validate_pr_review_scenario_structure,
)

__all__ = [
    # ... existing exports ...
    "validate_pr_review_scenario_structure",
]
```

---

## Chunk 3: Main Orchestrator and CLI

### Task 9: Create the main orchestrator

**Files:**

- Create: `pr_review_flow/pr_review_multiagent.py`

- [ ] **Step 1: Write `pr_review_multiagent.py`**

This is the core orchestrator. It chains: load inputs → Phase 1 (generate base repo + eval) → Phase 2 (generate PR + answer key + eval) → GitHub operations → Supabase insert.

```python
"""Main orchestrator for PR Review task generation."""

import os
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

import openai
from dotenv import load_dotenv
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from supabase import Client, create_client

from logger_config import logger
from pr_review_flow.schemas import BASE_REPO_SCHEMA, PR_GENERATION_SCHEMA
from pr_review_flow.prompts.base_repo_prompts import (
    BASE_REPO_SYSTEM_PROMPT,
    BASE_REPO_GENERATION_PROMPT,
    EVAL_FEEDBACK_BLOCK,
    EVAL_FEEDBACK_BLOCK_EMPTY,
)
from pr_review_flow.prompts.pr_generation_prompts import (
    PR_SYSTEM_PROMPT,
    PR_GENERATION_PROMPT,
    EVAL_FEEDBACK_BLOCK as PR_EVAL_FEEDBACK_BLOCK,
    EVAL_FEEDBACK_BLOCK_EMPTY as PR_EVAL_FEEDBACK_BLOCK_EMPTY,
)
from pr_review_flow.pr_review_evals import eval_base_repo, eval_pr_and_answer_key
from pr_review_flow.pr_review_github import create_pr_review_repo
from pr_review_flow.pr_review_utils import (
    slugify_branch_name,
    parse_pr_review_scenario,
    validate_modified_files,
    format_competencies_with_scopes,
    count_source_files,
    extract_usage,
    format_cost_summary,
    save_pr_review_locally,
)

load_dotenv()

GENERATION_MODEL = "gpt-5.1-2025-11-13"
EVAL_MODEL = "gpt-5-nano-2025-08-07"
MAX_RETRIES = 1
REPO_OWNER = os.getenv("REPO_OWNER")


def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client."""
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")
    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for: {env}")
    return create_client(url, key)


def init_openai_client() -> openai.OpenAI:
    """Initialize OpenAI client with Portkey gateway."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(provider="openai", api_key=portkey_key),
    )


def _track_usage(usage_by_model: dict, model: str, usage: dict):
    """Accumulate token usage into tracking dict."""
    if model not in usage_by_model:
        usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0}
    usage_by_model[model]["input_tokens"] += usage["input_tokens"]
    usage_by_model[model]["output_tokens"] += usage["output_tokens"]


# ── Phase 1: Base Repo Generation ──────────────────────────────────────


def generate_base_repo(
    openai_client: openai.OpenAI,
    competencies: list,
    project_context: str,
    usage_by_model: dict,
    eval_feedback: str = "",
) -> Optional[dict]:
    """Generate a clean base repo. Returns code_files dict or None on failure."""
    competencies_text = format_competencies_with_scopes(competencies)

    feedback_block = (
        EVAL_FEEDBACK_BLOCK.format(feedback_text=eval_feedback)
        if eval_feedback
        else EVAL_FEEDBACK_BLOCK_EMPTY
    )

    prompt = BASE_REPO_GENERATION_PROMPT.format(
        competencies_with_scopes=competencies_text,
        project_context=project_context,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": BASE_REPO_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    logger.info(f"Phase 1: Generating base repo ({GENERATION_MODEL})...")
    response = openai_client.responses.create(
        model=GENERATION_MODEL,
        input=messages,
        reasoning={"effort": "medium"},
        text={
            "format": {
                "type": "json_schema",
                "name": BASE_REPO_SCHEMA["name"],
                "schema": BASE_REPO_SCHEMA["schema"],
                "strict": BASE_REPO_SCHEMA["strict"],
            }
        },
    )

    usage = extract_usage(response)
    _track_usage(usage_by_model, GENERATION_MODEL, usage)

    raw = getattr(response, "output_text", None)
    if not raw:
        logger.error("No output from base repo generation")
        return None

    result = json.loads(raw)
    return result.get("code_files", {})


def run_phase1(openai_client, competencies, project_context, usage_by_model) -> Optional[dict]:
    """Phase 1 with eval gate and retry. Returns code_files or None."""
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Phase 1 attempt {attempt + 1}/{MAX_RETRIES + 1}")

        code_files = generate_base_repo(
            openai_client, competencies, project_context, usage_by_model, eval_feedback
        )
        if not code_files:
            continue

        # Check minimum file count
        source_count = count_source_files(code_files)
        if source_count < 3:
            eval_feedback = f"Base repo only has {source_count} source files, need at least 3."
            logger.warning(eval_feedback)
            continue

        # Eval gate
        eval_result, eval_usage = eval_base_repo(code_files, competencies, openai_client)
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Phase 1 PASSED evaluation")
            return code_files

        eval_feedback = eval_result.get("feedback", "Evaluation failed without specific feedback.")
        logger.warning(f"Phase 1 FAILED evaluation: {eval_feedback}")

    logger.error("Phase 1 failed after all attempts")
    return None


# ── Phase 2: Flawed PR + Answer Key Generation ────────────────────────


def generate_pr_with_answer_key(
    openai_client: openai.OpenAI,
    base_repo_files: dict,
    pr_intent: str,
    injected_flaws: str,
    usage_by_model: dict,
    eval_feedback: str = "",
) -> Optional[dict]:
    """Generate flawed PR + answer key. Returns PR data dict or None."""
    base_repo_text = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in base_repo_files.items()
    )

    feedback_block = (
        PR_EVAL_FEEDBACK_BLOCK.format(feedback_text=eval_feedback)
        if eval_feedback
        else PR_EVAL_FEEDBACK_BLOCK_EMPTY
    )

    prompt = PR_GENERATION_PROMPT.format(
        base_repo_files=base_repo_text,
        pr_intent=pr_intent,
        injected_flaws=injected_flaws,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": PR_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    logger.info(f"Phase 2: Generating flawed PR + answer key ({GENERATION_MODEL})...")
    response = openai_client.responses.create(
        model=GENERATION_MODEL,
        input=messages,
        reasoning={"effort": "medium"},
        text={
            "format": {
                "type": "json_schema",
                "name": PR_GENERATION_SCHEMA["name"],
                "schema": PR_GENERATION_SCHEMA["schema"],
                "strict": PR_GENERATION_SCHEMA["strict"],
            }
        },
    )

    usage = extract_usage(response)
    _track_usage(usage_by_model, GENERATION_MODEL, usage)

    raw = getattr(response, "output_text", None)
    if not raw:
        logger.error("No output from PR generation")
        return None

    return json.loads(raw)


def run_phase2(openai_client, base_repo_files, pr_intent, injected_flaws, usage_by_model) -> Optional[dict]:
    """Phase 2 with pre-validation, eval gate, and retry. Returns PR data or None."""
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Phase 2 attempt {attempt + 1}/{MAX_RETRIES + 1}")

        pr_data = generate_pr_with_answer_key(
            openai_client, base_repo_files, pr_intent, injected_flaws, usage_by_model, eval_feedback
        )
        if not pr_data:
            continue

        # Pre-validation: check modified_files reference valid base repo files
        invalid_paths = validate_modified_files(
            pr_data.get("modified_files", {}), base_repo_files
        )
        if invalid_paths:
            eval_feedback = f"modified_files references nonexistent base repo files: {invalid_paths}"
            logger.warning(eval_feedback)
            continue

        # Eval gate
        eval_result, eval_usage = eval_pr_and_answer_key(base_repo_files, pr_data, openai_client)
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Phase 2 PASSED evaluation")
            return pr_data

        eval_feedback = eval_result.get("feedback", "Evaluation failed without specific feedback.")
        logger.warning(f"Phase 2 FAILED evaluation: {eval_feedback}")

    logger.error("Phase 2 failed after all attempts")
    return None


# ── Full Pipeline ──────────────────────────────────────────────────────


def create_pr_review_task(
    competency_file: Path,
    background_file: Path,
    scenarios_file: Path,
    env: str = "dev",
    dry_run: bool = False,
) -> Optional[Dict]:
    """End-to-end PR review task generation.

    Returns dict with task metadata including repo_url and pr_url, or None on failure.
    """
    openai_client = init_openai_client()
    usage_by_model = {}

    # ── Load inputs ────────────────────────────────────────────────────
    with open(competency_file, "r", encoding="utf-8") as f:
        competencies_data = json.load(f)
    # Handle all formats: {"competencies": [...]}, [...], or single dict
    if isinstance(competencies_data, dict) and "competencies" in competencies_data:
        competencies = competencies_data["competencies"]
    elif isinstance(competencies_data, list):
        competencies = competencies_data
    elif isinstance(competencies_data, dict):
        competencies = [competencies_data]
    else:
        raise ValueError("Invalid competencies data format")

    with open(background_file, "r", encoding="utf-8") as f:
        background = json.load(f)

    with open(scenarios_file, "r", encoding="utf-8") as f:
        scenarios_data = json.load(f)

    # Build scenario key and pick a scenario
    from scenario_generator import build_scenario_key
    scenario_key = build_scenario_key(competencies)
    available_scenarios = scenarios_data.get(scenario_key, [])
    if not available_scenarios:
        logger.error(f"No scenarios found for key: {scenario_key}")
        return None

    # Use first available scenario (caller can manage which to use)
    scenario_text = available_scenarios[0]
    parsed = parse_pr_review_scenario(scenario_text)

    project_context = parsed.get("project_context", "")
    pr_intent = parsed.get("pr_intent", "")
    injected_flaws = parsed.get("injected_flaws", "")

    if not all([project_context, pr_intent, injected_flaws]):
        logger.error(f"Scenario missing required sections: {list(parsed.keys())}")
        return None

    logger.info(f"Scenario key: {scenario_key}")
    logger.info(f"Project Context: {project_context[:100]}...")
    logger.info(f"PR Intent: {pr_intent[:100]}...")

    # ── Phase 1 ────────────────────────────────────────────────────────
    base_repo_files = run_phase1(openai_client, competencies, project_context, usage_by_model)
    if not base_repo_files:
        logger.error("Phase 1 failed — aborting")
        print(format_cost_summary(usage_by_model))
        return None

    # ── Phase 2 ────────────────────────────────────────────────────────
    pr_data = run_phase2(openai_client, base_repo_files, pr_intent, injected_flaws, usage_by_model)
    if not pr_data:
        logger.error("Phase 2 failed — aborting")
        print(format_cost_summary(usage_by_model))
        return None

    # ── Save locally ───────────────────────────────────────────────────
    task_name = pr_data.get("pr_title", "pr-review-task")
    from github_utils import slugify
    task_slug = slugify(task_name)
    eval_info = {"phase1": "passed", "phase2": "passed"}
    local_dir = save_pr_review_locally(task_slug, base_repo_files, pr_data, eval_info)

    if dry_run:
        logger.info("[DRY RUN] Skipping GitHub and Supabase operations")
        print(f"\nBase repo files: {list(base_repo_files.keys())}")
        print(f"PR title: {pr_data.get('pr_title')}")
        print(f"Modified files: {list(pr_data.get('modified_files', {}).keys())}")
        print(f"Added files: {list(pr_data.get('added_files', {}).keys())}")
        print(f"Answer key flaws: {len(pr_data.get('answer_key', {}).get('flaws', []))}")
        print(f"Local files: {local_dir}")
        print(format_cost_summary(usage_by_model))
        return {"dry_run": True, "local_dir": str(local_dir)}

    # ── GitHub operations ──────────────────────────────────────────────
    branch_name = slugify_branch_name(pr_data.get("pr_title", "feature"))
    logger.info(f"Creating GitHub repo and PR (branch: {branch_name})...")

    try:
        repo_url, pr_url = create_pr_review_repo(
            task_name=task_slug,
            base_repo_files=base_repo_files,
            pr_data=pr_data,
            branch_name=branch_name,
        )
    except Exception as e:
        logger.error(f"GitHub operations failed: {e}")
        logger.error(traceback.format_exc())
        print(format_cost_summary(usage_by_model))
        raise

    logger.info(f"Repo: {repo_url}")
    logger.info(f"PR: {pr_url}")

    # ── Supabase insert ────────────────────────────────────────────────
    supabase = init_supabase(env)
    created_at = datetime.now(timezone.utc)

    criterias_for_db = [
        {
            "competency_id": c.get("competency_id") or c.get("id"),
            "name": c.get("name"),
            "proficiency": c.get("proficiency", "BASIC"),
        }
        for c in competencies
    ]

    answer_key = pr_data.get("answer_key", {})
    solutions_for_db = {
        "steps": answer_key.get("flaws", []),
        "overall_verdict": answer_key.get("overall_verdict", "request_changes"),
        "pr_description_issues": answer_key.get("pr_description_issues", []),
    }

    task_data_for_db = {
        "created_at": created_at.isoformat(),
        "pre_requisites": "GitHub account, familiarity with PR review workflow",
        "answer": "",
        "criterias": criterias_for_db,
        "is_deployed": False,
        "task_blob": {
            "title": f"PR Review: {pr_data.get('pr_title', '')}",
            "task_type": "pr_review",
            "question": "Review the open PR and provide feedback — approve, request changes, or leave line comments where you see issues.",
            "short_overview": pr_intent,
            "outcomes": f"Candidate identifies flaws in the PR including: {', '.join(f['category'] for f in answer_key.get('flaws', []))}",
            "resources": {
                "github_repo": repo_url,
                "github_pr": pr_url,
            },
            "hints": "",
            "definitions": {},
        },
        "is_shared_infra_required": False,
        "readme_content": None,
        "eval_info": eval_info,
        "solutions": solutions_for_db,
    }

    result = supabase.table("tasks").insert(task_data_for_db).execute()
    if not result.data:
        raise RuntimeError("Failed to insert task into Supabase")

    supabase_task = result.data[0]
    task_id = supabase_task.get("id") or supabase_task.get("task_id")

    # Insert task-competency relationships
    for criteria in criterias_for_db:
        comp_id = criteria.get("competency_id")
        if comp_id:
            try:
                supabase.table("task_competencies").insert({
                    "task_id": task_id,
                    "competency_id": comp_id,
                }).execute()
            except Exception as e:
                logger.error(f"Failed to insert task-competency: {e}")

    # ── Summary ────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  PR REVIEW TASK CREATED SUCCESSFULLY")
    print(f"{'='*70}")
    print(f"  Task ID:    {task_id}")
    print(f"  Repo:       {repo_url}")
    print(f"  PR:         {pr_url}")
    print(f"  Flaws:      {len(answer_key.get('flaws', []))}")
    print(f"  Verdict:    {answer_key.get('overall_verdict', 'N/A')}")
    print(f"  Local:      {local_dir}")
    print(f"{'='*70}")
    print(format_cost_summary(usage_by_model))

    return {
        "task_id": task_id,
        "repo_url": repo_url,
        "pr_url": pr_url,
        "local_dir": str(local_dir),
    }
```

---

### Task 10: Create CLI entry point

**Files:**

- Create: `pr_review_flow/__main__.py`

- [ ] **Step 1: Write `__main__.py`**

```python
"""CLI entry point for PR Review task generation.

Usage:
    python -m pr_review_flow \
        --competency-file path/to/competency.json \
        --background-file path/to/background.json \
        --scenarios-file path/to/task_scenarios_pr_review.json
"""

import sys
import io
from pathlib import Path

import click

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pr_review_flow.pr_review_multiagent import create_pr_review_task


@click.command()
@click.option(
    "--competency-file", "-c",
    type=click.Path(exists=True), required=True,
    help="Path to competency JSON file",
)
@click.option(
    "--background-file", "-b",
    type=click.Path(exists=True), required=True,
    help="Path to background JSON file",
)
@click.option(
    "--scenarios-file", "-s",
    type=click.Path(exists=True), required=True,
    help="Path to PR review scenarios JSON file",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Run LLM generation but skip GitHub and Supabase operations",
)
def main(competency_file, background_file, scenarios_file, env, dry_run):
    """Generate a PR Review assessment task."""
    click.echo(f"\n{'='*70}")
    click.echo("  PR REVIEW TASK GENERATOR")
    click.echo(f"{'='*70}")
    click.echo(f"  Competency file: {competency_file}")
    click.echo(f"  Background file: {background_file}")
    click.echo(f"  Scenarios file:  {scenarios_file}")
    click.echo(f"  Environment:     {env}")
    if dry_run:
        click.echo("  Mode:            DRY RUN")
    click.echo()

    result = create_pr_review_task(
        competency_file=Path(competency_file),
        background_file=Path(background_file),
        scenarios_file=Path(scenarios_file),
        env=env,
        dry_run=dry_run,
    )

    if not result:
        click.echo("\nTask generation failed. Check logs for details.", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

---

### Task 11: Create empty scenario files

**Files:**

- Create: `task_input_files/task_scenarios/task_scenarios_pr_review.json`
- Create: `task_input_files/task_scenarios/task_scenarios_pr_review_intermediate.json`

- [ ] **Step 1: Create empty scenario files**

Both files start as empty JSON objects:

```json
{}
```

These will be populated by the scenario generator with PR-review-specific scenarios.

> **Deferred to follow-up plan:** Adding PR review scenario generation prompts to `scenario_generator/prompts.py` and extending `pipeline/` with `--task-type pr_review` support. These are listed in the spec but are separate concerns — the core generation pipeline works first with manually authored scenarios, then automated scenario generation can be layered on.

---

### Task 12: Update `pr_review_flow/__init__.py` with exports

**Files:**

- Modify: `pr_review_flow/__init__.py`

- [ ] **Step 1: Add exports**

```python
"""
PR Review Task Generation package.

Generates assessment tasks where candidates review GitHub PRs with intentional flaws.

Usage as CLI:
    python -m pr_review_flow --competency-file <path> --background-file <path> --scenarios-file <path>
"""

from pr_review_flow.pr_review_multiagent import create_pr_review_task

__all__ = ["create_pr_review_task"]
```

---

## Chunk 4: Integration and Manual Testing

### Task 13: Verify the module loads without errors

- [ ] **Step 1: Test module import**

Run: `cd /Users/manaspatidar/Utkrusht/utkrusht-task && python -c "from pr_review_flow import create_pr_review_task; print('Import OK')"`

Expected: `Import OK`

- [ ] **Step 2: Test CLI help**

Run: `cd /Users/manaspatidar/Utkrusht/utkrusht-task && python -m pr_review_flow --help`

Expected: Help text showing `--competency-file`, `--background-file`, `--scenarios-file`, `--env`, `--dry-run` options.

---

### Task 14: Create a test scenario and run dry-run

- [ ] **Step 1: Add a test PR review scenario to `task_scenarios_pr_review.json`**

Pick an existing competency file from `task_input_files/` (e.g., Python FastAPI BASIC) and manually write one test scenario following the `**Project Context:** / **PR Intent:** / **Injected Flaws:**` format.

- [ ] **Step 2: Run dry-run**

Run: `python -m pr_review_flow --competency-file <path-to-competency.json> --background-file <path-to-background.json> --scenarios-file task_input_files/task_scenarios/task_scenarios_pr_review.json --dry-run`

Expected: LLM generates base repo + PR with answer key, files previewed in console, saved locally under `infra_assets/pr_review_tasks/`. No GitHub or Supabase operations.

- [ ] **Step 3: Review local output**

Check `infra_assets/pr_review_tasks/<task-name>/`:

- `base_repo/` has 4+ source files with clean, consistent code
- `pr_files/` has modified/added files with intentional flaws
- `answer_key.json` lists all flaws with categories and severities
- `metadata.json` has PR title and description

---

### Task 15: Full end-to-end test (with GitHub + Supabase)

- [ ] **Step 1: Run without dry-run against dev environment**

Run: `python -m pr_review_flow --competency-file <path> --background-file <path> --scenarios-file task_input_files/task_scenarios/task_scenarios_pr_review.json --env dev`

Expected output:

```
PR REVIEW TASK CREATED SUCCESSFULLY
  Task ID:    <uuid>
  Repo:       https://github.com/<org>/<task-slug>
  PR:         https://github.com/<org>/<task-slug>/pull/1
  Flaws:      <N>
  Verdict:    request_changes
```

- [ ] **Step 2: Verify GitHub repo**

Open `repo_url` — check that `main` has clean base code. Open `pr_url` — check that the PR has a diff with the flawed changes and a realistic title/description.

- [ ] **Step 3: Verify Supabase record**

Query: `supabase.table("tasks").select("*").eq("task_id", "<task_id>").execute()`
Check: `task_blob.task_type == "pr_review"`, `task_blob.resources.github_pr` exists, `solutions.steps` contains flaw objects.
