"""Main orchestrator for Design Review task generation."""

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
from design_review_flow.schemas import (
    FLAW_SPEC_SCHEMA,
    CANDIDATE_BRIEF_SCHEMA,
    EVALUATION_RUBRIC_SCHEMA,
)
from design_review_flow.prompts import (
    FLAW_SPEC_SYSTEM_PROMPT,
    FLAW_SPEC_GENERATION_PROMPT,
    BRIEF_SYSTEM_PROMPT,
    BRIEF_GENERATION_PROMPT,
    RUBRIC_SYSTEM_PROMPT,
    RUBRIC_GENERATION_PROMPT,
    EVAL_FEEDBACK_BLOCK,
    EVAL_FEEDBACK_BLOCK_EMPTY,
)
from design_review_flow.design_review_evals import eval_flaw_spec, eval_candidate_brief
from design_review_flow.design_review_utils import (
    get_library_entry,
    load_layer_tree,
    extract_layer_names,
    format_frames_for_prompt,
    validate_flaw_layers,
    validate_spec_file,
    validate_figma_link,
    extract_usage,
    format_cost_summary,
    save_design_task_locally,
)
from utils import read_json_file_robust

load_dotenv()

GENERATION_MODEL = "gpt-5.1-2025-11-13"
EVAL_MODEL = "gpt-5-nano-2025-08-07"
MAX_RETRIES = 2


def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client for the given environment."""
    if env == "prod":
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for env '{env}'")
    return create_client(url, key)


def init_openai_client() -> openai.OpenAI:
    """Initialize OpenAI client via Portkey gateway."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if not portkey_key:
        raise RuntimeError("PORTKEY_API_KEY not set")
    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=portkey_key,
        ),
    )


def _track_usage(usage_by_model: dict, model: str, usage: dict):
    """Accumulate token usage by model."""
    if model not in usage_by_model:
        usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0}
    usage_by_model[model]["input_tokens"] += usage.get("input_tokens", 0)
    usage_by_model[model]["output_tokens"] += usage.get("output_tokens", 0)


# ─── Phase 1: Generate Flaw Spec ───

def generate_flaw_spec(
    openai_client,
    library_entry: Dict,
    layer_tree: Dict,
    competencies: List[Dict],
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
    eval_feedback: str = "",
) -> Optional[Dict]:
    """Generate flaw injection spec via LLM."""
    # Format inputs
    layer_names = extract_layer_names(layer_tree)
    layer_tree_text = "\n".join(layer_names)
    frames_text = format_frames_for_prompt(library_entry.get("frames", {}))
    competencies_text = "\n".join(
        f"- {c.get('name', '')} ({c.get('proficiency', '')}): {c.get('scope', '')}"
        for c in competencies
    )
    feedback_block = EVAL_FEEDBACK_BLOCK.format(feedback=eval_feedback) if eval_feedback else EVAL_FEEDBACK_BLOCK_EMPTY

    prompt = FLAW_SPEC_GENERATION_PROMPT.format(
        library_id=library_entry["id"],
        library_name=library_entry["name"],
        domain=library_entry["domain"],
        screens=", ".join(library_entry.get("screens", [])),
        frames_text=frames_text,
        layer_tree_text=layer_tree_text,
        competencies_text=competencies_text,
        proficiency=proficiency,
        scenario=scenario,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": FLAW_SPEC_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": FLAW_SPEC_SCHEMA["name"],
                    "schema": FLAW_SPEC_SCHEMA["schema"],
                    "strict": FLAW_SPEC_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from flaw spec generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Flaw spec generation error: {e}\n{traceback.format_exc()}")
        return None


def run_flaw_spec_generation(
    openai_client,
    library_entry: Dict,
    layer_tree: Dict,
    competencies: List[Dict],
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate flaw spec with eval gate and retry loop."""
    layer_names = extract_layer_names(layer_tree)
    layer_tree_text = "\n".join(layer_names)
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Flaw spec generation attempt {attempt + 1}/{MAX_RETRIES + 1}")

        flaw_spec = generate_flaw_spec(
            openai_client, library_entry, layer_tree,
            competencies, proficiency, scenario,
            usage_by_model, eval_feedback,
        )
        if not flaw_spec:
            eval_feedback = "Generation returned no output. Try again."
            continue

        # Pre-validation: check layer names exist
        invalid_layers = validate_flaw_layers(flaw_spec.get("flaws", []), layer_names)
        if invalid_layers:
            eval_feedback = f"Invalid layer references: {'; '.join(invalid_layers)}"
            logger.warning(f"Pre-validation failed: {eval_feedback}")
            continue

        # LLM eval gate
        eval_result, eval_usage = eval_flaw_spec(
            flaw_spec, layer_tree_text, proficiency, openai_client
        )
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Flaw spec passed evaluation")
            return flaw_spec

        eval_feedback = eval_result.get("feedback", "Evaluation failed")
        logger.warning(f"Flaw spec eval failed (attempt {attempt + 1}): {eval_feedback}")

    logger.error("Flaw spec generation failed after all retries")
    return None


# ─── Phase 2: Generate Candidate Brief ───

def generate_candidate_brief(
    openai_client,
    library_entry: Dict,
    flaw_spec: Dict,
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
    eval_feedback: str = "",
) -> Optional[Dict]:
    """Generate candidate brief via LLM."""
    flaw_types = list(set(f.get("type", "") for f in flaw_spec.get("flaws", [])))
    flaw_types_summary = ", ".join(flaw_types)
    feedback_block = EVAL_FEEDBACK_BLOCK.format(feedback=eval_feedback) if eval_feedback else EVAL_FEEDBACK_BLOCK_EMPTY

    prompt = BRIEF_GENERATION_PROMPT.format(
        library_name=library_entry["name"],
        domain=library_entry["domain"],
        screens=", ".join(library_entry.get("screens", [])),
        flaw_types_summary=flaw_types_summary,
        proficiency=proficiency,
        scenario=scenario,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": BRIEF_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": CANDIDATE_BRIEF_SCHEMA["name"],
                    "schema": CANDIDATE_BRIEF_SCHEMA["schema"],
                    "strict": CANDIDATE_BRIEF_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from brief generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Brief generation error: {e}\n{traceback.format_exc()}")
        return None


def run_brief_generation(
    openai_client,
    library_entry: Dict,
    flaw_spec: Dict,
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate candidate brief with eval gate and retry loop."""
    flaw_types = [f.get("type", "") for f in flaw_spec.get("flaws", [])]
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Brief generation attempt {attempt + 1}/{MAX_RETRIES + 1}")

        brief = generate_candidate_brief(
            openai_client, library_entry, flaw_spec,
            proficiency, scenario, usage_by_model, eval_feedback,
        )
        if not brief:
            eval_feedback = "Generation returned no output. Try again."
            continue

        # LLM eval gate
        eval_result, eval_usage = eval_candidate_brief(brief, flaw_types, openai_client)
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Candidate brief passed evaluation")
            return brief

        eval_feedback = eval_result.get("feedback", "Evaluation failed")
        logger.warning(f"Brief eval failed (attempt {attempt + 1}): {eval_feedback}")

    logger.error("Brief generation failed after all retries")
    return None


# ─── Phase 3: Generate Evaluation Rubric ───

def generate_evaluation_rubric(
    openai_client,
    flaw_spec: Dict,
    brief: Dict,
    proficiency: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate evaluation rubric via LLM. No eval gate — rubric structure is schema-enforced."""
    flaw_spec_summary = json.dumps(
        {"flaws": [{"type": f["type"], "severity": f["severity"], "rationale": f["rationale"]} for f in flaw_spec.get("flaws", [])]},
        indent=2
    )
    brief_summary = json.dumps(
        {"title": brief.get("title"), "change_requests": brief.get("change_requests")},
        indent=2
    )

    prompt = RUBRIC_GENERATION_PROMPT.format(
        flaw_spec_summary=flaw_spec_summary,
        brief_summary=brief_summary,
        proficiency=proficiency,
    )

    messages = [
        {"role": "system", "content": RUBRIC_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVALUATION_RUBRIC_SCHEMA["name"],
                    "schema": EVALUATION_RUBRIC_SCHEMA["schema"],
                    "strict": EVALUATION_RUBRIC_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from rubric generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Rubric generation error: {e}\n{traceback.format_exc()}")
        return None


# ─── Entry Points ───

def create_design_review_task(
    competency_file: Path,
    proficiency: str,
    scenario: str,
    library_entry_id: str,
    env: str = "dev",
    dry_run: bool = False,
) -> Optional[Dict]:
    """Generate a design review task: flaw spec + brief + rubric.

    Returns dict with local_dir path, or None on failure.
    """
    openai_client = init_openai_client()
    usage_by_model = {}

    # Load inputs
    competencies = read_json_file_robust(competency_file)
    if isinstance(competencies, dict):
        competencies = competencies.get("competencies", [competencies])
    if not isinstance(competencies, list):
        competencies = [competencies]

    library_entry = get_library_entry(library_entry_id)
    if not library_entry:
        logger.error(f"Library entry '{library_entry_id}' not found in figma_library.json")
        return None

    layer_tree = load_layer_tree(library_entry_id)
    if not layer_tree:
        logger.error(f"Layer tree not found for '{library_entry_id}'")
        return None

    # Phase 1: Generate flaw spec
    logger.info("Phase 1: Generating flaw injection spec...")
    flaw_spec = run_flaw_spec_generation(
        openai_client, library_entry, layer_tree,
        competencies, proficiency, scenario, usage_by_model,
    )
    if not flaw_spec:
        print(format_cost_summary(usage_by_model))
        return None

    # Phase 2: Generate candidate brief
    logger.info("Phase 2: Generating candidate brief...")
    brief = run_brief_generation(
        openai_client, library_entry, flaw_spec,
        proficiency, scenario, usage_by_model,
    )
    if not brief:
        print(format_cost_summary(usage_by_model))
        return None

    # Phase 3: Generate evaluation rubric
    logger.info("Phase 3: Generating evaluation rubric...")
    rubric = generate_evaluation_rubric(
        openai_client, flaw_spec, brief, proficiency, usage_by_model,
    )
    if not rubric:
        print(format_cost_summary(usage_by_model))
        return None

    # Validate rubric weights sum to 100
    total_weight = sum(c.get("weight", 0) for c in rubric.get("criteria", []))
    if total_weight != 100:
        logger.error(f"Rubric weights sum to {total_weight}, expected 100")
        print(format_cost_summary(usage_by_model))
        return None

    # Build eval info
    eval_info = {
        "flaw_spec_eval": {"passed": True},
        "brief_eval": {"passed": True},
    }

    # Save locally
    if not dry_run:
        local_dir = save_design_task_locally(
            library_entry_id, flaw_spec, brief, rubric, library_entry, eval_info,
            competencies,
        )
    else:
        local_dir = "DRY_RUN"

    # Print cost summary
    print(format_cost_summary(usage_by_model))

    logger.info(f"Design review task generated successfully")
    return {
        "local_dir": str(local_dir),
        "dry_run": dry_run,
        "flaw_count": len(flaw_spec.get("flaws", [])),
    }


def store_design_review_task(
    spec_file: Path,
    figma_link: str,
    env: str = "dev",
) -> Optional[Dict]:
    """Store a generated design review task in Supabase.

    Called after the Figma plugin step, when the flawed design is ready.
    """
    # Load and validate spec file
    spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
    errors = validate_spec_file(spec_data)
    if errors:
        logger.error(f"Spec file validation failed: {'; '.join(errors)}")
        return None

    # Validate Figma link
    if not validate_figma_link(figma_link):
        logger.error(f"Invalid Figma link: {figma_link}")
        return None

    flaw_spec = spec_data["flaw_spec"]
    brief = spec_data["candidate_brief"]
    rubric = spec_data["evaluation_rubric"]
    library_entry = spec_data["library_entry"]
    eval_info = spec_data.get("eval_info", {})

    # Build Supabase record
    created_at = datetime.now(timezone.utc)

    # Build criterias from library entry domain
    criterias_for_db = [
        {
            "name": "UI/UX Design",
            "proficiency": flaw_spec.get("flaws", [{}])[0].get("severity", "INTERMEDIATE").upper()
                if flaw_spec.get("flaws") else "INTERMEDIATE",
        }
    ]

    # Use competency info if available in the spec
    if "competencies" in spec_data:
        criterias_for_db = [
            {
                "competency_id": c.get("competency_id") or c.get("id"),
                "name": c.get("name"),
                "proficiency": c.get("proficiency", "BASIC"),
            }
            for c in spec_data["competencies"]
        ]

    task_data = {
        "created_at": created_at.isoformat(),
        "pre_requisites": "Figma account (free tier), understanding of UX principles",
        "answer": "",
        "criterias": criterias_for_db,
        "is_deployed": False,
        "task_blob": {
            "title": brief.get("title", "Design Review Task"),
            "task_type": "design_review",
            "question": f"Review the provided Figma design and complete the change requests. "
                        f"Submit your modified Figma link and written rationale.",
            "short_overview": brief.get("domain_context", ""),
            "outcomes": "Candidate identifies UX flaws, makes design improvements, and provides written rationale",
            "resources": {
                "figma_source_link": library_entry.get("figma_community_url", ""),
                "figma_flawed_link": figma_link,
            },
            "hints": "",
            "definitions": {},
            "domain_context": brief.get("domain_context", ""),
            "constraints": brief.get("constraints", []),
            "change_requests": brief.get("change_requests", []),
            "submission_requirements": brief.get("submission_requirements", {}),
            "time_limit_minutes": brief.get("time_limit_minutes", 45),
            "attribution": f"{library_entry.get('attribution', 'Unknown')}, {library_entry.get('license', 'CC BY 4.0')}",
        },
        "is_shared_infra_required": False,
        "readme_content": None,
        "eval_info": eval_info,
        "solutions": {
            "flaw_spec": flaw_spec,
            "answer_key": flaw_spec.get("answer_key", {}),
            "evaluation_rubric": rubric,
        },
    }

    # Insert into Supabase
    try:
        supabase = init_supabase(env)
        result = supabase.table("tasks").insert(task_data).execute()
        task_id = result.data[0].get("id") or result.data[0].get("task_id")
        logger.info(f"Task stored in Supabase ({env}): {task_id}")

        # Insert task-competency relationships
        for criteria in criterias_for_db:
            comp_id = criteria.get("competency_id")
            if comp_id:
                supabase.table("task_competencies").insert({
                    "task_id": task_id,
                    "competency_id": comp_id,
                }).execute()

        return {"task_id": task_id, "env": env}

    except Exception as e:
        logger.error(f"Supabase insert error: {e}\n{traceback.format_exc()}")
        return None
