from pathlib import Path
import json
import os
import re
from typing import Dict, List
import sys
from typing import Optional
from datetime import datetime
from logger_config import logger
from models import TaskResponse

# Add parent directory to path for logger and imports
sys.path.append(str(Path(__file__).parent.parent))
# Add current directory to path for same-folder imports
sys.path.append(str(Path(__file__).parent))

# Import Pydantic model from separate file
from models import TaskResponse

import importlib
import pkgutil
import task_generation_prompts.Basic as _basic_pkg
import task_generation_prompts.Intermediate as _inter_pkg
import task_generation_prompts.Beginner as _beginner_pkg


def _build_prompt_registry() -> dict:
    registry = {}
    for pkg in [_basic_pkg, _inter_pkg, _beginner_pkg]:
        for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
            module = importlib.import_module(f"{pkg.__name__}.{module_name}")
            if hasattr(module, "PROMPT_REGISTRY"):
                registry.update(module.PROMPT_REGISTRY)
    return registry


_PROMPT_REGISTRY = _build_prompt_registry()

def save_task_data_only(task_id: str, task_data: Dict) -> Path:
    """Save only clean task.json locally for reference (no extra files)."""
    try:
        base_dir = Path(__file__).parent / "test_assets"
        local_task_dir = base_dir / "tasks" / task_id
        local_task_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving clean test task data locally to: {local_task_dir}")
 
        # Clean the task data first - remove background and other unnecessary data
        clean_task_data = clean_task_data_for_output(task_data)
        
        # Save only task.json file (clean version)
        task_json_path = local_task_dir / "task.json"
        with open(task_json_path, 'w', encoding='utf-8') as f:
            json.dump(clean_task_data, f, indent=2, ensure_ascii=False)
        logger.info("Saved clean task.json locally")
        
        logger.info(f"✅ Clean test task data saved locally at: {local_task_dir}")
        return local_task_dir
        
    except Exception as e:
        logger.error(f"Error saving test task data locally: {str(e)}")
        raise

def format_pre_requisites(pre_requisites):
    """Format pre_requisites as a list of strings (array of bullet points)."""
    if not pre_requisites:
        return []
    
    # If it's already a list, return it as-is (cleaned)
    if isinstance(pre_requisites, list):
        return [str(item).strip() for item in pre_requisites if str(item).strip()]
    
    # If it's a string, split by newlines only (not commas), strip bullet points, and keep as list
    if isinstance(pre_requisites, str):
        items = [item.strip('- ').strip() for item in pre_requisites.split('\n') if item.strip('- ').strip()]
        return items
    
    # For any other type, convert to string and return as single-item list
    return [str(pre_requisites).strip()]

def clean_task_data_for_output(task_data: Dict) -> Dict:
    """Clean task data for output - save LLM output directly, only remove internal processing keys."""
    try:
        # Create a copy of the entire task_data
        cleaned_data = task_data.copy()
        
        # Remove only internal processing keys that shouldn't be in the final JSON
        internal_keys_to_remove = ["background"]
        for key in internal_keys_to_remove:
            cleaned_data.pop(key, None)
        
        # Format pre_requisites if they exist (formatting only, not filtering)
        if "pre_requisites" in cleaned_data:
            cleaned_data["pre_requisites"] = format_pre_requisites(cleaned_data["pre_requisites"])
        
        # Remove null values
        cleaned_data = {k: v for k, v in cleaned_data.items() if v is not None}
        
        logger.info("Cleaned task data for output - saved LLM output directly, removed only background and other internal keys")
        return cleaned_data
        
    except Exception as e:
        logger.error(f"Error cleaning task data for output: {str(e)}")
        return task_data

def validate_test_task_structure(task_data: Dict) -> bool:
    """Validate that test task has correct structure."""
    try:
        required_fields = [
            "task_id", "name", "question"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in task_data:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Test task missing required fields: {missing_fields}")
            return False
        
        logger.info("Test task structure validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Error validating test task structure: {str(e)}")
        return False

def format_test_task_summary(task_data: Dict) -> str:
    """Format a summary of the test task for logging."""
    try:
        competencies = task_data.get("competencies", [])
        competency_info = ""
        if competencies:
            comp = competencies[0]
            competency_info = f"{comp.get('competency_id', 'unknown')} ({comp.get('proficiency', 'BASIC')})"
        
        summary = f"""Test Task Summary:
==================
Task ID: {task_data.get('task_id', 'unknown')}
Task Name: {task_data.get('name', 'unknown')}
Competency: {competency_info}
Question: {task_data.get('question', 'No question')[:100]}...
==================
"""
        return summary
        
    except Exception as e:
        logger.error(f"Error formatting test task summary: {str(e)}")
        return f"Task ID: {task_data.get('task_id', 'unknown')}"

# ===== UTILITY FUNCTIONS =====

def read_json_file_robust(file_path: Path) -> dict:
    """
    Robust JSON file reader that tries multiple encodings to handle various file formats.
    """
    encodings_to_try = [
        'utf-8-sig',  # UTF-8 with BOM
        'utf-8',      # UTF-8 without BOM
        'utf-16',     # UTF-16 with BOM
        'utf-16-le',  # UTF-16 Little Endian without BOM
        'utf-16-be',  # UTF-16 Big Endian without BOM
        'latin1',     # Windows-1252 / ISO-8859-1
        'cp1252',     # Windows-1252
    ]
    
    last_exception = None
    
    for encoding in encodings_to_try:
        try:
            logger.debug(f"Trying to read {file_path} with encoding: {encoding}")
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            logger.info(f"Successfully read {file_path} with encoding: {encoding}")
            return data
        except (UnicodeDecodeError, UnicodeError) as e:
            logger.debug(f"Encoding {encoding} failed for {file_path}: {str(e)}")
            last_exception = e
            continue
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {str(e)}")
            raise
    
    # If we get here, all encodings failed
    raise Exception(f"Failed to read {file_path} with any encoding. Last error: {str(last_exception)}")

def load_relevant_scenarios(competencies: List[Dict], scenarios_file: Path) -> List[str]:
    """
    Load relevant scenarios for given competencies from scenarios file.
    """
    try:
        all_scenarios = read_json_file_robust(scenarios_file)

        if not competencies:
            logger.warning("No competencies provided for scenario loading")
            return []

        # Step 1: Format each competency with its specific proficiency
        formatted_competencies = []
        for comp in competencies:
            comp_name = comp.get("name", "").strip()
            comp_proficiency = comp.get("proficiency", "BASIC").strip().upper()
            if comp_name:
                formatted_comp = f"{comp_name} ({comp_proficiency})"
                formatted_competencies.append(formatted_comp)

        if not formatted_competencies:
            logger.warning("No valid competencies found for scenario loading")
            return []

        # Step 2: Sort the formatted competency strings to create a consistent primary key
        sorted_formatted_competencies = sorted(formatted_competencies)

        # Step 3: Construct possible combined keys
        possible_keys = []

        # Primary key: sorted and joined with proficiency levels
        primary_key = ", ".join(sorted_formatted_competencies)
        possible_keys.append(primary_key)

        # If there are exactly two competencies, also try the reverse order
        if len(sorted_formatted_competencies) == 2:
            reverse_key = ", ".join(reversed(sorted_formatted_competencies))
            if reverse_key != primary_key:
                possible_keys.append(reverse_key)

        logger.info(f"Attempting to find scenarios with possible combined keys: {possible_keys}")

        found_scenarios = []
        for key in possible_keys:
            if key in all_scenarios:
                found_scenarios = all_scenarios[key]
                logger.info(f"Found {len(found_scenarios)} scenarios for key: {key}")
                break
        
        if not found_scenarios:
            logger.info(f"No scenarios found for keys: {possible_keys}")

        return found_scenarios

    except FileNotFoundError:
        logger.error(f"Scenarios file not found at: {scenarios_file}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from scenarios file: {scenarios_file}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading scenarios: {str(e)}")
        return []

def get_task_prompt_by_technology_stack(competency_stack, input_data):
    """Get task prompt by technology stack. Auto-discovered from PROMPT_REGISTRY."""
    competencies = input_data.get("competencies", [])
    key_with_proficiency = ", ".join(
        sorted([f"{c.get('name')} ({c.get('proficiency', '').upper()})" for c in competencies if c.get("name")])
    ) if competencies else ""

    templates = (
        _PROMPT_REGISTRY.get(key_with_proficiency)
        or _PROMPT_REGISTRY.get(competency_stack)
    )
    if not templates:
        raise ValueError(
            f"No prompt registered for tech stack: '{key_with_proficiency or competency_stack}'. "
            f"Add PROMPT_REGISTRY to the prompt file."
        )

    fmt_args = {
        "organization_background": input_data["background"]["organization"]["organization_background"],
        "role_context": input_data["background"]["role_context"],
        "minutes_range": input_data.get("minutes_range", "15-20"),
        "competencies": input_data.get("competencies"),
        "real_world_task_scenarios": input_data.get("scenarios", ""),
        "question_prompt": input_data.get("background", {}).get("questions_prompt", ""),
    }
    return [t.format(**fmt_args) for t in templates]

def generate_task_with_code(openai_client, input_data: Dict) -> Dict:
    """Generate task and code files using language_prompts with Responses.create + high reasoning."""
    try:
        model = "gpt-5.1-2025-11-13"
        competencies = input_data["competencies"]

        # Get competency names and create a single technology stack string
        competency_names = [comp.get("name") for comp in competencies]
        competency_stack = ", ".join(competency_names)
        
        logger.info(f"Using technology stack: {competency_stack} for competencies: {competency_names}")
            
        # Task generation system prompt
        TASK_GENERATION_SYSTEM_PROMPT = """
        You are a senior AI product manager and assessment designer with 15+ years of experience in AI-native applications, prompt engineering, and enterprise AI systems. You have conducted 500+ technical interviews and specialize in designing assessments for AI literacy, flow design, prompt engineering, evaluation frameworks, and safety & governance.

        Your expertise focuses on creating realistic, production-grade AI scenarios that assess candidates' ability to:
        - Analyze AI system behavior, diagnose issues, and identify root causes in operational data
        - Design and optimize multi-step AI workflows, prompts, and guardrails
        - Build evaluation frameworks and measure AI system performance
        - Address safety, bias, and governance considerations
        - Communicate technical findings to executive stakeholders

        Generate task definitions that present authentic enterprise AI challenges (contact-center, enterprise applications) with real operational data files. Tasks must align with proficiency levels, be completable within time constraints, and assess genuine AI engineering judgment beyond simple tool usage. Candidates are encouraged to use AI tools, but tasks should require deep understanding of LLM behavior, prompt mechanics, and systematic problem-solving.
        """
        
        task_generation_prompts = get_task_prompt_by_technology_stack(competency_stack, input_data)

        # Check if prompts are available for this technology stack
        if not task_generation_prompts:
            logger.error(f"No task generation prompts found for technology stack: {competency_stack}")
            raise ValueError(
                f"Unsupported technology stack: {competency_stack}. "
                f"Please add prompts for this stack in get_task_prompt_by_technology_stack."
            )

        # Build input messages for Responses API - start with system message
        messages = [{
            "role": "system",
            "content": TASK_GENERATION_SYSTEM_PROMPT
        }]
        
        # Send prompts one by one and log each response (following utils.py pattern)
        response = None
        for prompt in task_generation_prompts:
            messages.append({"role": "user", "content": prompt})
            response = openai_client.responses.create(
                model=model,
                input=messages,
                reasoning={"effort": "medium"}
            )
            response_text = getattr(response, "output_text", "NO output_text on response")
            messages.append({"role": "assistant", "content": response_text})
            logger.info("=" * 70)
            logger.info(f" Prompt Response: ")
            logger.info(response_text)
            logger.info("=" * 70)

        # Basic safety checks
        if response is None or not getattr(response, "output_text", None):
            logger.error("No response_text received from OpenAI Responses API")
            raise RuntimeError("Failed to get response_text from OpenAI Responses API")

        # Parse JSON from the final response
        try:
            task_data = json.loads(response.output_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response.output_text: {e}")
            raise

        task_data["created_at"] = datetime.now().isoformat()
        
        return task_data
        
    except Exception as e:
        logger.error(f"Error generating task with code: {str(e)}")
        raise

def convert_empty_to_none(data: Dict) -> Dict:
    """Convert empty strings to None for database storage."""
    if isinstance(data, dict):
        return {k: convert_empty_to_none(v) if isinstance(v, (dict, list, str)) else (None if v == "" else v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_empty_to_none(item) for item in data]
    elif isinstance(data, str) and data == "":
        return None
    return data