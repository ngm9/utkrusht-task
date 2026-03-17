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


# -- Phase 1: Base Repo Generation --


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


# -- Phase 2: Flawed PR + Answer Key Generation --


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


# -- Full Pipeline --


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

    # -- Load inputs --
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

    # -- Phase 1 --
    base_repo_files = run_phase1(openai_client, competencies, project_context, usage_by_model)
    if not base_repo_files:
        logger.error("Phase 1 failed -- aborting")
        print(format_cost_summary(usage_by_model))
        return None

    # -- Phase 2 --
    pr_data = run_phase2(openai_client, base_repo_files, pr_intent, injected_flaws, usage_by_model)
    if not pr_data:
        logger.error("Phase 2 failed -- aborting")
        print(format_cost_summary(usage_by_model))
        return None

    # -- Save locally --
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

    # -- GitHub operations --
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

    # -- Supabase insert --
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
            "question": "Review the open PR and provide feedback -- approve, request changes, or leave line comments where you see issues.",
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

    # -- Summary --
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
