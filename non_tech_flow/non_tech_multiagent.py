from pathlib import Path
import os
import json
import uuid
import traceback
import click
import sys
from typing import Dict, List
from dotenv import load_dotenv
from datetime import datetime, timezone
from supabase import Client, create_client

# Try to import OpenAI - if not available, we'll handle it gracefully
try:
    import openai
    from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI or Portkey not installed. Install with: pip install openai portkey-ai")
    OPENAI_AVAILABLE = False
    openai = None
    PORTKEY_GATEWAY_URL = None
    createHeaders = None

# Import prompts directly from task_generation_prompts folder
sys.path.append(str(Path(__file__).parent.parent))

from logger_config import logger

# Local test imports
try:
    from test_utils import (
        save_task_data_only,
        read_json_file_robust,
        load_relevant_scenarios,
        get_task_prompt_by_technology_stack,
        generate_task_with_code,
        convert_empty_to_none,
        format_pre_requisites
    )
    from test_evals import run_evaluations
except (ImportError, SystemError):
    from non_tech_utils import (
        save_task_data_only,
        read_json_file_robust,
        load_relevant_scenarios,
        get_task_prompt_by_technology_stack,
        generate_task_with_code,
        convert_empty_to_none,
        format_pre_requisites
    )
    from non_tech_evals import run_evaluations
from utils import create_gist_from_files
from google_drive_utils import create_google_drive_folder

# Load environment variables
load_dotenv()

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai_client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY")
        )
    )
else:
    openai_client = None
    
model = "gpt-5.1-2025-11-13"

# Validate environment and initialize variables after imports
def validate_environment() -> None:
    """Validate that all required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
        'PORTKEY_API_KEY',
        'SUPABASE_URL_APTITUDETESTSDEV',
        'SUPABASE_API_KEY_APTITUDETESTSDEV'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    if not OPENAI_AVAILABLE:
        raise ValueError("OpenAI and Portkey packages are required. Install with: pip install openai portkey-ai")
    
    logger.info("Environment validation completed successfully")

# Validate environment on module load
validate_environment()

def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client based on environment."""
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")
    
    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")
    
    return create_client(url, key)


def create_test_task(competency_file: Path, background_file: Path, scenarios_file: Path = None, env: str = "dev") -> Dict:
    """Generate a test task and insert into Supabase (no GitHub operations). Uses the exact same task generation logic as multiagent.py"""
    try:
        # Initialize Supabase client
        supabase = init_supabase(env)
        
        # Load input data - same as multiagent.py
        competencies_data = read_json_file_robust(competency_file)
        background_data = read_json_file_robust(background_file)
        
        # Handle single competency or list of competencies 
        if isinstance(competencies_data, dict) and "competencies" in competencies_data:
            competencies = competencies_data["competencies"]
        elif isinstance(competencies_data, list):
            competencies = competencies_data
        elif isinstance(competencies_data, dict):
            competencies = [competencies_data]
        else:
            raise ValueError("Invalid competencies data format")
        
        logger.info(f"Processing {len(competencies)} competencies")
        
        for i, competency in enumerate(competencies):
            competency_id = competency.get("competency_id") or competency.get("id") or "unknown"
            logger.info(f"Processing competency {i+1}: {competency_id} - {competency.get('name', 'unknown')}")
            
            # Generate unique task ID
            task_id = f"test-task-{uuid.uuid4().hex[:8]}"
            logger.info(f"Generated task ID: {task_id}")
            
            # Load relevant scenarios if provided 
            scenarios = []
            if scenarios_file and scenarios_file.exists():
                scenarios = load_relevant_scenarios([competency], scenarios_file)
            
            # Extract sample_dataset from competency if available
            sample_dataset = competency.get("sample_dataset", [])
            if sample_dataset:
                logger.info(f"Found sample_dataset with {len(sample_dataset)} entries for competency")
            
            # Prepare input data for task generation 
            input_data = {
                "competencies": [competency],
                "background": background_data,
                "scenarios": scenarios,
            }
            
            # Generate task using LLM 
            logger.info("Generating task with LLM using same prompts as multiagent.py...")
            task_data = generate_task_with_code(openai_client, input_data)
            
            if not task_data:
                logger.error("Failed to generate task data")
                continue
            
            # Add metadata BEFORE validation 
            task_data["task_id"] = task_id
            
            # Use competency_id if available, otherwise use id or competency_id
            competency_id = competency.get("competency_id") or competency.get("id") or competency.get("name", "unknown")
            task_data["criterias"] = [{
                "competency_id": competency_id,
                "proficiency": competency.get("proficiency", "BASIC"),
                "name": competency.get("name")
            }]
            
            # Add background to task_data for evals (needed for yoe)
            task_data["background"] = background_data
            
            # Run evaluations - check if task is too long or can be completed in 20 minutes
            logger.info("Running task evaluations (checking if task is too long or can be completed in 20 minutes)...")
            eval_info = run_evaluations(task_data, openai_client, model)
            task_data["eval_info"] = eval_info
            logger.info(f"Task eval passed: {eval_info['task_eval']['pass']}")
            
            # Prepare data for Supabase insert
            created_at = datetime.now(timezone.utc)
            
            # Format criterias with competency_id
            criterias_for_db = [{
                "name": competency.get("name"),
                "proficiency": competency.get("proficiency", "BASIC"),
                "competency_id": competency.get("competency_id") or competency.get("id")
            }]
            
            # Format prerequisites as array of bullet points
            pre_requisites_value = format_pre_requisites(task_data.get("pre_requisites", ""))

            # Get eval_info from task_data (generated by run_evaluations)
            eval_info = task_data.get("eval_info", {})

            # Upload task resources — prefer Google Drive (PM-friendly), fall back to Gist
            drive_url = None
            gist_url = None
            code_files = task_data.get("code_files", {})

            # Try Google Drive first (CSV → Sheets, TXT → Docs)
            service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_PATH")
            if service_account_key and code_files:
                try:
                    drive_url = create_google_drive_folder(
                        files=code_files,
                        task_name=task_data.get("name", "Assessment Task"),
                        service_account_key_path=service_account_key,
                    )
                    if drive_url:
                        logger.info(f"Google Drive folder created: {drive_url}")
                except Exception as e:
                    logger.warning(f"Google Drive upload failed: {e}")

            # Fall back to GitHub Gist if Drive not available
            if not drive_url:
                gist_token = os.getenv("GITHUB_GIST_TOKEN")
                if gist_token and code_files:
                    try:
                        task_name_slug = (task_data.get("name") or "task").replace(" ", "-").lower()
                        gist_url = create_gist_from_files(
                            files=code_files,
                            owner="utkrushtapps",
                            repo=task_name_slug,
                            gist_token=gist_token,
                            description=task_data.get("name", "Assessment Task Dataset"),
                            public=False
                        )
                        if gist_url:
                            logger.info(f"Gist created as fallback: {gist_url}")
                    except Exception as e:
                        logger.warning(f"Gist creation failed: {e}")

            # Build resources dict — Drive URL preferred, Gist as fallback
            resources = task_data.get("resources") or {}
            dataset_url = drive_url or gist_url
            if dataset_url:
                resources["dataset"] = dataset_url
            if drive_url:
                resources["google_drive"] = drive_url
            if gist_url:
                resources["github_gist"] = gist_url

            # Format short_overview as task_overview list
            short_overview = task_data.get("short_overview", "")
            if isinstance(short_overview, list):
                task_overview = short_overview
            elif isinstance(short_overview, str) and short_overview.strip():
                task_overview = [line.strip("- ").strip() for line in short_overview.split("\n") if line.strip("- ").strip()]
            else:
                task_overview = []

            task_data_for_db = {
                "created_at": created_at.isoformat(),
                "pre_requisites": pre_requisites_value,  # Store prerequisites properly
                "answer": task_data.get("answer") or None,  # Convert empty to None
                "criterias": criterias_for_db,
                "is_deployed": False,
                "task_blob": {
                    "title": task_data.get("name") or None,
                    "definitions": task_data.get("definitions") or {},
                    "hints": task_data.get("hints") or None,
                    "resources": resources,
                    "outcomes": task_data.get("outcomes") or None,
                    "question": task_data.get("question") or None,
                    "task_overview": task_overview,
                    "competencies": criterias_for_db,
                    "prerequisites": pre_requisites_value,
                },
                "is_shared_infra_required": False,  # Default to False for test tasks
                "readme_content": None,  # None for test tasks (no GitHub repo)
                "eval_info": eval_info,  # Store eval_info from evaluations
                "solutions": None  # None for test tasks (no answer repo)
            }
            
            # Convert all empty strings to None
            task_data_for_db = convert_empty_to_none(task_data_for_db)
            
            # Insert into Supabase 
            logger.info(f"Inserting task into Supabase: {task_id}")
            result = supabase.table("tasks").insert(task_data_for_db).execute()
            
            if not result.data:
                logger.error("Failed to insert task into Supabase")
                continue
            
            # Get the task_id from Supabase response
            supabase_task = result.data[0]
            db_task_id = supabase_task.get("id") or supabase_task.get("task_id")
            
            # Insert task-competency relationships
            for criteria in criterias_for_db:
                competency_id_for_relationship = criteria.get("competency_id")
                if competency_id_for_relationship:
                    try:
                        supabase.table("task_competencies").insert({
                            "task_id": db_task_id,
                            "competency_id": competency_id_for_relationship
                        }).execute()
                    except Exception as e:
                        logger.error(f"Failed to insert task-competency relationship: {str(e)}")
            
            # Save task data locally for reference
            task_data["task_id"] = db_task_id
            save_task_data_only(db_task_id, task_data)
            
            # Task generation completed successfully
            logger.info(f"[SUCCESS] Successfully generated and inserted test task: {db_task_id}")
            logger.info(f"   - Task Name: {task_data.get('name', 'unknown')}")
            logger.info(f"   - Competency: {competency.get('name', 'unknown')}")
            logger.info(f"   - Proficiency: {competency.get('proficiency', 'BASIC')}")
            logger.info(f"   - Task inserted into Supabase: {env}")
            logger.info(f"   - Database Task ID: {db_task_id}")
            logger.info(f"   - Task also saved locally for reference")
                
        return {"status": "completed", "message": "Test task generation and Supabase insert completed"}
        
    except Exception as e:
        logger.error(f"Error creating test task: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@click.command()
@click.option('--competency-file', '-c', 
              type=click.Path(exists=True, path_type=Path),
              help='Path to competencies.json file (supports single or multiple competencies)')
@click.option('--background-file', '-b',
              type=click.Path(exists=True, path_type=Path), 
              help='Path to background_for_tasks.json file')
@click.option('--scenarios-file', '-s',
              type=click.Path(exists=True, path_type=Path),
              help='Path to task_scenarios.json file')
def generate_test_tasks(competency_file: Path, background_file: Path, scenarios_file: Path):
    """Generate tasks and insert into Supabase database."""
    try:
        logger.info("=" * 50)
        logger.info("STARTING TEST TASK GENERATION")
        logger.info("=" * 50)
        logger.info("This flow will:")
        logger.info("[CHECK] Generate tasks from prompts")
        logger.info("[CHECK] Run evaluations ")
        logger.info("[CHECK] INSERT into Supabase database")
        logger.info("[CHECK] Save locally for reference")
       
        logger.info("=" * 50)
        
        # Validate input files
        if not competency_file.exists():
            raise ValueError(f"Competency file not found: {competency_file}")
        if not background_file.exists():
            raise ValueError(f"Background file not found: {background_file}")
        
        # Generate tasks 
        result = create_test_task(competency_file, background_file, scenarios_file)
        
        logger.info("=" * 50)
        logger.info("TEST TASK GENERATION COMPLETED")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error in test task generation: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    cli = click.Group()
    cli.add_command(generate_test_tasks)
    cli()