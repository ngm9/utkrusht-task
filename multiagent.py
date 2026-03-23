"""
usage: 
python "c:\Utkrushta\Utkrushta\agents\infra_assessor\multiagent.py" generate-tasks -c "c:\Utkrushta\Utkrushta\utilities\input_collection\task\input_rag\basic\basic\competency_rag_basic_Utkrusht.json" -b "c:\Utkrushta\Utkrushta\utilities\input_collection\task\input_rag\basic\basic\background_for_task_utkrusht_rag_basic.json" -s "c:\Utkrushta\Utkrushta\utilities\input_collection\task_scenarios.json"

python multiagent.py reset-task --task-id b77bcb57-48be-4cc9-b738-702659d764bc  --droplet-ip 157.245.96.154  --script-path  /root/task/kill.sh

python multiagent.py deploy_task --task-id 6e20982e-9a4e-4a0d-b20f-1e0b1ba6e67a --droplet-ip 64.227.178.86 
"""
import json
import subprocess
import datetime
import os
import paramiko
import random
import string
import shutil
from pathlib import Path
from github import Github
import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from dotenv import load_dotenv
import click
from typing import Dict, List, Optional
from supabase import Client, create_client
import traceback
from evals import MAX_EVAL_RETRIES, llm_task_eval, llm_code_eval
from logger_config import logger
from schemas import ANSWER_CODE_SCHEMA
from utils import (parse_markdown_to_json,has_shared_infra_files,format_pre_requisites,format_outcomes,save_files_locally,load_relevant_scenarios,generate_task_with_code,read_json_file_robust,create_gist_from_template,)
from droplet_utils import get_droplet_info, get_available_droplet_ips, get_ssh_key, upload_files_to_droplet, execute_script_on_droplet
from github_utils import create_github_repo, create_github_template_repo, slugify ,upload_files_batch
import os
import click
import json
import datetime
import traceback
import shutil
import random
import paramiko


# Load environment variables
load_dotenv()

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai_client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.environ.get("PORTKEY_API_KEY")
    )
)
model = "gpt-5.1-2025-11-13"

# Static GitHub credentials
GITHUB_UTKRUSHTAPPS_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
GITHUB_GIST_TOKEN = os.getenv("GITHUB_GIST_TOKEN")

def run_evaluations(task_data: Dict) -> Dict:
    """Run LLM-based evaluations on the task and code."""
    # Get highest proficiency level
    prof_levels = [criteria["proficiency"].upper() for criteria in task_data.get("criterias", [])]
    yoe = task_data.get("background", {}).get("yoe", "")
    time_constraint = 25 if "ADVANCED" in prof_levels else 20 if "INTERMEDIATE" in prof_levels else 15
    
    # Task evaluation
    task_eval_result = llm_task_eval(task_data, 
                                   prof_levels[-1] if prof_levels else "BASIC",
                                   yoe,
                                   time_constraint,
                                   openai_client,
                                   model)
                                   
    # Code evaluation
    code_eval_result = llm_code_eval(task_data.get("code_files", {}),
                                   task_data.get("description", ""),
                                   openai_client,
                                   model)

                      
    # Add evaluation info to task data
    eval_info = {
        "task_eval": {
            "pass": task_eval_result.get("pass", False),
            "validated_criteria": task_eval_result.get("validated_criteria", [])
        },
        "code_eval": {
            "pass": code_eval_result.get("pass", False),
            "validated_criteria": code_eval_result.get("validated_criteria", [])
        }
    }
    
    return eval_info

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

def validate_environment() -> None:
    """Validate that all required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
        'PORTKEY_API_KEY', 
        'GITHUB_UTKRUSHTAPPS_TOKEN',
        'REPO_OWNER',
        'SUPABASE_URL_APTITUDETESTSDEV',
        'SUPABASE_API_KEY_APTITUDETESTSDEV'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Check for DigitalOcean token (either one is fine)
    if not os.getenv("DIGITALOCEAN_API_PAT"):
        logger.info("DIGITALOCEAN_API_PAT is not set.")
    
    logger.info("Environment validation completed successfully")

def determine_task_type(competencies: List[Dict], task_data: Dict) -> str:
    """
    Determine if task is backend or frontend based on competencies and task content.
    Returns 'backend' or 'frontend'.
    """
    try:
        # Check competency names and descriptions for backend/frontend indicators
        backend_keywords = [
            'api', 'database', 'sql', 'postgresql', 'fastapi', 'backend', 'server', 
            'orm', 'authentication', 'authorization', 'rest', 'microservice', 'docker',
            'container', 'deployment', 'infrastructure', 'security', 'middleware'
        ]
        
        frontend_keywords = [
            'react', 'nextjs', 'next.js', 'typescript', 'javascript', 'frontend', 
            'ui', 'ux', 'component', 'routing', 'client', 'browser', 'dom', 'css',
            'html', 'responsive', 'seo', 'accessibility', 'state management'
        ]
        
        # Check competency names and descriptions
        text_to_check = []
        for comp in competencies:
            text_to_check.append(comp.get('name', '').lower())
            text_to_check.append(comp.get('description', '').lower())
        
        # Also check task content
        text_to_check.extend([
            task_data.get('name', '').lower(),
            task_data.get('description', '').lower(),
            task_data.get('question', '').lower()
        ])
        
        combined_text = ' '.join(text_to_check)
        
        backend_score = sum(1 for keyword in backend_keywords if keyword in combined_text)
        frontend_score = sum(1 for keyword in frontend_keywords if keyword in combined_text)
        
        logger.info(f"Task type scoring - Backend: {backend_score}, Frontend: {frontend_score}")
        
        # Return the type with higher score, default to backend if tied
        if frontend_score > backend_score:
            return 'frontend'
        else:
            return 'backend'
            
    except Exception as e:
        logger.error(f"Error determining task type: {str(e)}")
        return 'backend'  # Default to backend

def validate_task(task: Dict) -> bool:
    """Validate task against required schema"""
    try:
        required_fields = [
            "created_at", "pre_requisites", "question", "resources", 
            "outcomes", "answer", "hints", "definitions", "name", "description", "criterias"
        ]
        
        if not all(field in task for field in required_fields):
            missing = [field for field in required_fields if field not in task]
            logger.error(f"Missing required fields: {missing}")
            return False
            
        if not isinstance(task.get("criterias"), list):
            logger.error("criterias field must be a list")
            return False
            
        outcomes_value = task.get("outcomes")
        if not isinstance(outcomes_value, (str, list)):
            logger.error("outcomes field must be a list of bullet points")
            return False
            
        # Validate definitions is non-empty object with meaningful content
        definitions = task.get("definitions", {})
        if not isinstance(definitions, dict):
            logger.error("definitions field must be an object")
            return False
        if len(definitions) == 0:
            logger.error("definitions field must not be empty")
            return False
        
        # Check if definitions contain meaningful content
        for key, value in definitions.items():
            if not isinstance(value, str) or len(value.strip()) == 0:
                logger.error(f"definitions field must contain meaningful definitions")
                return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating task: {str(e)}")
        return False

def get_examples_for_competency_proficiency(competency_id: str, proficiency: str, scenarios_file: Path) -> List[Dict]:
    """Get all real-world examples for a specific competency and proficiency level."""
    try:
        scenarios_data = read_json_file_robust(scenarios_file)
        
        for competency_entry in scenarios_data:
            if (competency_entry.get('competency_id') == competency_id and 
                competency_entry.get('proficiency', '').upper() == proficiency.upper()):
                
                examples = competency_entry.get('real_world_examples', [])
                logger.info(f"Found {len(examples)} real-world examples for {competency_entry.get('name')} at {proficiency} proficiency")
                return examples
        
        logger.info(f"No examples found for competency_id {competency_id} with proficiency {proficiency}")
        return []
        
    except Exception as e:
        logger.error(f"Error loading examples from scenarios file: {str(e)}")
        return []

def upload_files_to_github(repo: str, code_data: Dict) -> None:
    """Upload LLM-generated files to the GitHub repository in a single commit."""
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        # Try to get the repo using the current user first, then fallback to REPO_OWNER
        try:
            repo_obj = github.get_user().get_repo(repo)
        except:
            if REPO_OWNER:
                repo_obj = github.get_repo(f"{REPO_OWNER}/{repo}")
            else:
                raise Exception(f"Could not find repository {repo}. Please set REPO_OWNER environment variable.")
        
        main_branch = "main"
        
        # Get all files from code_data
        files_to_upload = code_data.get("code_files", {})
        
        if not files_to_upload:
            logger.warning(f"No files to upload to repository {repo}")
            return
        
        # Upload all files in a single commit using batch upload
        success = upload_files_batch(repo_obj, files_to_upload, "Initial commit", main_branch)
        
        if not success:
            # Delete the repo if upload failed
            logger.error(f"Failed to upload files in batch. Deleting repo {repo}...")
            try:
                repo_obj.delete()
                logger.info(f"Deleted repo {repo} due to upload failures.")
            except Exception as e:
                logger.error(f"Failed to delete repo {repo}: {str(e)}")
            raise Exception(f"Failed to upload files to GitHub in batch")

        logger.info(f"Successfully uploaded all {len(files_to_upload)} files to repository {repo} in a single commit")

    except Exception as e:
        logger.error(f"Error uploading LLM-generated files: {str(e)}")
        raise

def create_task(competency_file: Path, background_file: Path, scenarios_file: Path = None) -> Dict:
    """Generate an intelligent assessment task."""
    try:
        # Set default scenarios file if not provided
        if scenarios_file is None:
            scenarios_file = Path(__file__).parent.parent.parent / "utilities" / "input_collection" / "task_scenarios.json"
        
        # Load input files 
        logger.info(f"Reading competencies from {competency_file}")
        competency_data = read_json_file_robust(competency_file)
            
        # Convert single competency to list format
        competencies = competency_data if isinstance(competency_data, list) else [competency_data]
        logger.info(f"Successfully loaded {len(competencies)} competencies")
        logger.info(f"Competency details: {competencies}")
        
        logger.info(f"Reading background from {background_file}")
        background = read_json_file_robust(background_file)
            
        # Use current timestamp for created_at
        created_at = datetime.datetime.now(datetime.timezone.utc)
        
        # Load relevant scenarios
        logger.info(f"Loading scenarios from: {scenarios_file}")
        scenarios = load_relevant_scenarios(competencies, scenarios_file)
        logger.info(f"Loaded {len(scenarios)} relevant scenarios")
        logger.info(f"Scenarios: {scenarios}")
        
        input_data = {
            "competencies": [
                {
                    "name": comp.get("name"),
                    "scope": comp.get("scope"),
                    "proficiency": comp.get("proficiency")
                }
                for comp in competencies
            ],
            "background": background,
            "scenarios": scenarios
        }
        # Generate task with code in one step
        task_data = generate_task_with_code(openai_client, input_data)
        
        # Add metadata
        task_data["criterias"] = [{
            "name": comp.get("name"),
            "proficiency": comp.get("proficiency"),
            "competency_id": comp.get("competency_id") or comp.get("id")
        } for comp in competencies]
        
        # Generate code files and save them
        if "code_files" not in task_data:
            task_data["code_files"] = {}
    
        # Run evaluations
        # we need check conditions that if the eval_info is true then it should be passed
        logger.info("Running task evaluations")
        eval_info = run_evaluations(task_data)
        
        # Determine task type for shared infrastructure requirement
        task_type = determine_task_type(competencies, task_data)
        logger.info(f"Determined task type: {task_type}")
        
        # Generate answer code and solutions
        logger.info("Generating solution code and steps")
        solutions_data = generate_answer_code_and_steps(task_data) # steps, files
        
        # Use GitHub repo name from LLM-generated task or generate one
        repo_name_base = task_data.get("resources", {}).get("github_repo", "").split("/")[-1]
        if not repo_name_base:
            repo_name_base = slugify(task_data.get("name", "assessment-task"))
        
        # Limit repository name to 50 characters to avoid GitHub's character limits
        if len(repo_name_base) > 50:
            repo_name_base = repo_name_base[:50].rstrip('-')
        
        # Create GitHub template repo (public) using the template function
        logger.info("Creating public GitHub template repository")
        repo_name = create_github_template_repo(repo_name_base, is_private=True)
        
        # Update the GitHub URL with the final repository name
        github_repo_url = f"https://github.com/{REPO_OWNER}/{repo_name}"
        
        # Create answer repository
        logger.info("Creating answer repository")
        # Limit answer repo base name to 42 characters since "-answers" (8 chars) will be added
        answer_base_name = task_data.get("name", "assessment-task")
        if len(answer_base_name) > 42:
            answer_base_name = answer_base_name[:42].rstrip('-')
        answer_repo_name = create_answer_github_repo(answer_base_name)

        answer_repo_url = f"https://github.com/{REPO_OWNER}/{answer_repo_name}"
        # Upload solution files to answer repository
        logger.info("Uploading solution files to answer repository")
        upload_answer_files_to_repo(answer_repo_name, solutions_data)
        
        solutions_for_db = {
            "steps": solutions_data.get("steps", []),
            "answer_repo": answer_repo_url
        }
        
        # Ensure resources key exists
        if "resources" not in task_data:
            task_data["resources"] = {}
        task_data["resources"]["github_repo"] = github_repo_url
        
        # Save files locally and to GitHub
        logger.info("Saving files locally...")
        # Use repo name as temporary directory name since task ID doesn't exist yet
        local_task_dir = save_files_locally(repo_name, task_data)
        logger.info(f"Files saved locally to: {local_task_dir}")
        
        logger.info("Uploading files to GitHub repository...")
        upload_files_to_github(repo_name, task_data)
        
        # Create Gist from template repo (same content for quick view/share)
        gist_url = None     
        if GITHUB_GIST_TOKEN:
            try:
                gist_url = create_gist_from_template(
                    repo_url=github_repo_url,
                    repo_token=GITHUB_UTKRUSHTAPPS_TOKEN,
                    gist_token=GITHUB_GIST_TOKEN,
                    description=task_data.get("name", repo_name),
                    public=False,
                )
                if gist_url:
                    task_data["resources"]["gist_url"] = gist_url
                    logger.info(f"Gist created: {gist_url}")
            except Exception as e:
                logger.warning(f"Gist creation skipped or failed: {e}")
        else:
            logger.warning("No GITHUB_GIST_TOKEN for gist; skipping gist creation")
        
        # Store in Supabase
        logger.info("Storing task in Supabase...")
        
        # Determine is_shared_infra_required based on task type
        # Backend tasks (with Docker/FastAPI/PostgreSQL) require shared infrastructure
        # Frontend tasks (NextJS/React) typically don't
        if task_type == 'backend':
            is_shared_infra_required = True
        else:  # frontend
            is_shared_infra_required = False
        
        # Override with Docker detection if needed
        code_data = task_data.get("code_files", {})
        has_docker = has_shared_infra_files(code_data)
        if has_docker:
            is_shared_infra_required = True
            
        logger.info(f"Setting is_shared_infra_required to {is_shared_infra_required} (task_type: {task_type}, has_docker: {has_docker})")
        
        task_data_for_db = {
            "created_at": created_at.isoformat(),
            "pre_requisites": format_pre_requisites(task_data.get("pre_requisites", "")),
            "answer": task_data.get("answer", ""),
            "criterias": task_data["criterias"],
            "is_deployed": False,
            "task_blob": {
                "title": task_data.get("name", ""),
                "definitions": task_data.get("definitions", {}),
                "hints": task_data.get("hints", ""),
                "resources": dict(
                    {"github_repo": github_repo_url},
                    **({"github_gist": gist_url} if gist_url else {}),
                ),
                "outcomes": format_outcomes(task_data.get("outcomes", "")),
                "question": task_data.get("question", ""),
                # Allow short_overview to be a string or list and normalize to bullet points
                "short_overview": format_outcomes(task_data.get("short_overview", "")),
            },
            "is_shared_infra_required": is_shared_infra_required,
            "readme_content": parse_markdown_to_json(code_data.get("README.md", "")),
            "eval_info": eval_info,
            "solutions": solutions_for_db
        }
        
        supabase = init_supabase()
        result = supabase.table("tasks").insert(task_data_for_db).execute()
        
        if not result.data or len(result.data) == 0:
            raise Exception("Failed to insert task into Supabase - no data returned")
        
        supabase_task = result.data[0]
        task_id = supabase_task.get("id") or supabase_task.get("task_id")
        
        # Insert task-competency relationships
        for criteria in task_data["criterias"]:
            competency_id = criteria.get("competency_id")
            if competency_id:
                try:
                    supabase.table("task_competencies").insert({
                        "task_id": task_id,
                        "competency_id": competency_id
                    }).execute()
                except Exception as e:
                    logger.error(f"Failed to insert task-competency relationship: {str(e)}")
        
        task_data.update(supabase_task)
        task_data["task_id"] = task_id
        
        # Optionally rename local directory to use actual task ID
        try:
            new_local_task_dir = local_task_dir.parent / str(task_id)
            if local_task_dir != new_local_task_dir:
                shutil.move(str(local_task_dir), str(new_local_task_dir))
                logger.info(f"Renamed local directory to use task ID: {new_local_task_dir}")
        except Exception as e:
            logger.info(f"Could not rename local directory to task ID: {str(e)}")
        
        return task_data
        
    except Exception as e:
        logger.error(f"Error in create_task function: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Task creation failed: {str(e)}")

def deploy_task_impl(task_id: str, tasksession_id: str, droplet_ip: str = None, env: str = "dev"):
    """
    Deploy a task to a droplet.
    """

    if not task_id:
        print(" ERROR: --task-id must be provided.")
        return False
    
    
    # Run deployment workflow
    print("=" * 70)
    print(" TASK DEPLOYMENT AGENT - DEPLOY SPECIFIC TASK")
    print("    Find Task -> Download Files -> Upload to Droplet -> Execute -> Update DB")
    print("=" * 70)
    print(f" Task ID: {task_id}")
    
    print(" Droplet IP: Auto-select from available pool")
    print(f" Environment: {env}")
    print()
    
    try:
        success = deploy_task_by_id(task_id, tasksession_id, droplet_ip, env)
            
        if success:
            print()
            print(" DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(" The specified task has been:")
            print("   ✓ Found in database")
            print("   ✓ Downloaded from GitHub")
            print("   ✓ Uploaded to DigitalOcean droplets")
            print("   ✓ Executed on droplets")
            print("   ✓ Database updated")
            print()
            
        else:
            print()
            print(" DEPLOYMENT FAILED!")
            print("=" * 70)
            print(" Please check the logs for details and try again.")
            print()
            
        return success
    except Exception as e:
        print()
        print(" DEPLOYMENT ERROR!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check your configuration and try again.")
        print()
        
        return False

def reset_task_impl(task_id: str, droplet_ip: str, script_path: str, env: str = "dev"):
    """
    Execute a reset script on a droplet and mark the task as undeployed.
    
    This command will:
    1. Execute the specified script on the droplet
    2. Update the database to mark the task as undeployed
    3. Clear deployment information from the database
    """
    try:
        print("=" * 70)
        print(" TASK RESET AGENT - RESET AND UNDEPLOY TASK")
        print("    Execute Script -> Update Database -> Mark as Undeployed")
        print("=" * 70)
        print(f" Task ID: {task_id}")
        print(f" Droplet IP: {droplet_ip}")
        print(f" Script Path: {script_path}")
        print()
        
        # Execute the reset script on the droplet
        print("🔄 Executing reset script on droplet...")
        script_success = execute_script_on_droplet(droplet_ip, script_path)
        
        if script_success:
            print("✅ Reset script executed successfully")
            
            # Update database to mark task as undeployed
            print("🔄 Updating database to mark task as undeployed...")
            db_success = update_task_undeploy_status(task_id, env)
            
            if db_success:
                print("✅ Task successfully marked as undeployed in database")
                print()
                print(" RESET COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print(" Task has been reset and marked as undeployed.")
                print(" You can now redeploy this task if needed.")
                print()
            else:
                print("❌ Failed to update task status in database")
                print()
                print(" RESET PARTIALLY COMPLETED!")
                print("=" * 70)
                print(" Script executed successfully but database update failed.")
                print(" Please check the database manually.")
                print()
        else:
            print("❌ Reset script execution failed")
            print()
            print(" RESET FAILED!")
            print("=" * 70)
            print(" Could not execute reset script on droplet.")
            print(" Database was not updated.")
            print()
            
    except Exception as e:
        print(f"❌ Reset operation failed: {str(e)}")
        print()
        print(" RESET ERROR!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check the logs and try again.")
        print()

@click.command()
@click.option('--competency-id', '-c', type=str, help='ID of competency to deploy (mutually exclusive with --task-id)')
@click.option('--task-id', '-t', type=str, help='ID of specific task to deploy (mutually exclusive with --competency-id)')
@click.option('--droplet-ip', '-d',
              type=str,
              help='IP address of specific DigitalOcean droplet to use (optional - will auto-select if not provided)',
              default=None)
@click.option('--deploy-existing', '-e',
              type=str,
              help='Deploy ALL existing undeployed tasks by competency_id (only works with --competency-id)')
def deploy_task(competency_id: str, task_id: str, droplet_ip: str, deploy_existing: str = None, env: str = "dev"):
    """
    Deploy a task to a droplet.
    """
    # Validate mutually exclusive options for task deployment
    if competency_id and task_id:
        print(" ERROR: --competency-id and --task-id are mutually exclusive. Use only one.")
        return
    
    if not competency_id and not task_id:
        print(" ERROR: Either --competency-id or --task-id must be provided.")
        return
    
    # Validate deploy_existing only works with competency_id
    if deploy_existing and not competency_id:
        print(" ERROR: --deploy-existing can only be used with --competency-id, not with --task-id.")
        return
    
    # Run deployment workflow
    print("=" * 70)
    if task_id:
        print(" TASK DEPLOYMENT AGENT - DEPLOY SPECIFIC TASK")
        print("    Find Task -> Download Files -> Upload to Droplet -> Execute -> Update DB")
        print("=" * 70)
        print(f" Task ID: {task_id}")
    else:
        print(" TASK DEPLOYMENT AGENT - DEPLOY EXISTING TASKS")
        print("    Search Tasks -> Download Files -> Upload to Droplets -> Execute -> Update DB")
        print("=" * 70)
        print(f" Competency ID: {competency_id}")
    
    if droplet_ip:
        print(f" Droplet IP: {droplet_ip}")
    else:
        print(" Droplet IP: Auto-select from available pool")
    print(f" Environment: {env}")
    print()
    
    try:
        if task_id:
            # Deploy specific task by task ID
            success = deploy_task_by_id(task_id, None, droplet_ip, env)
        else:
            # Deploy existing tasks by competency ID
            success = deploy_existing_task(competency_id, droplet_ip, env)
            
        if success:
            print()
            print(" DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            if task_id:
                print(" The specified task has been:")
            else:
                print(" All available tasks for this competency have been:")
            print("   ✓ Found in database")
            print("   ✓ Downloaded from GitHub")
            print("   ✓ Uploaded to DigitalOcean droplets")
            print("   ✓ Executed on droplets")
            print("   ✓ Database updated")
            print()
        else:
            print()
            print(" DEPLOYMENT FAILED!")
            print("=" * 70)
            print(" Please check the logs for details and try again.")
            print()
    except Exception as e:
        print()
        print(" DEPLOYMENT ERROR!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check your configuration and try again.")
        print()
   

@click.command()
@click.option('--task-id', '-t', type=str, required=True, help='ID of specific task to reset/undeploy')
@click.option('--droplet-ip', '-d', type=str, required=True, help='IP address of the DigitalOcean droplet')
@click.option('--script-path', '-s', type=str, required=True, help='Path to the reset script to execute on the droplet')
def reset_task(task_id: str, droplet_ip: str, script_path: str, env: str = "dev"):
    """
    Execute a reset script on a droplet and mark the task as undeployed.
    
    This command will:
    1. Execute the specified script on the droplet
    2. Update the database to mark the task as undeployed
    3. Clear deployment information from the database
    """
    try:
        print("=" * 70)
        print(" TASK RESET AGENT - RESET AND UNDEPLOY TASK")
        print("    Execute Script -> Update Database -> Mark as Undeployed")
        print("=" * 70)
        print(f" Task ID: {task_id}")
        print(f" Droplet IP: {droplet_ip}")
        print(f" Script Path: {script_path}")
        print()
        
        # Execute the reset script on the droplet
        print("🔄 Executing reset script on droplet...")
        script_success = execute_script_on_droplet(droplet_ip, script_path)
        
        if script_success:
            print("✅ Reset script executed successfully")
            
            # Update database to mark task as undeployed
            print("🔄 Updating database to mark task as undeployed...")
            db_success = update_task_undeploy_status(task_id, env)
            
            if db_success:
                print("✅ Task successfully marked as undeployed in database")
                print()
                print(" RESET COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print(" Task has been reset and marked as undeployed.")
                print(" You can now redeploy this task if needed.")
                print()
            else:
                print("❌ Failed to update task status in database")
                print()
                print(" RESET PARTIALLY COMPLETED!")
                print("=" * 70)
                print(" Script executed successfully but database update failed.")
                print(" Please check the database manually.")
                print()
        else:
            print("❌ Reset script execution failed")
            print()
            print(" RESET FAILED!")
            print("=" * 70)
            print(" Could not execute reset script on droplet.")
            print(" Database was not updated.")
            print()
            
    except Exception as e:
        print(f"❌ Reset operation failed: {str(e)}")
        print()
        print(" RESET ERROR!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check the logs and try again.")
        print()

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
def generate_tasks(competency_file: Path, background_file: Path, scenarios_file: Path):
    """
    Generate intelligent assessment tasks OR deploy existing tasks to droplets.
    
    DEFAULT MODE: Automatically detects single vs multi-competency and generates appropriate tasks.
    
    DEPLOYMENT MODE: Use --deploy-existing with a competency_id to deploy ALL existing undeployed tasks.
    """
    # Run task creation workflow
    print(" INTELLIGENT TASK GENERATION AGENT")
    
    # Check how many competencies we have
    try:
        competencies = read_json_file_robust(competency_file)
        competency_count = len(competencies)
        competency_names = [comp.get('name') for comp in competencies]
        
        print(f" Found {competency_count} competencies:")
        for i, name in enumerate(competency_names, 1):
            print(f"   {i}. {name}")
        print()
        
    except Exception as e:
        print(f" Error reading competencies file: {str(e)}")
        return
    
    missing_files = []
    if not competency_file.exists():
        missing_files.append(str(competency_file))
    if not background_file.exists():
        missing_files.append(str(background_file))
    
    if missing_files:
        print(" Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return

    try:
        # Create task(s) - function automatically handles single vs multi
        print(" STEP 1: Creating Task(s)...")
        print("-" * 50)

        # Validate environment first
        validate_environment()
        
        result = create_task(competency_file, background_file, scenarios_file)
        
        task_type = result.get("task_type", "unknown")
        competencies_covered = result.get("competencies_covered", [])
        
        print(f" Task Creation Successful!")
        print(f" Task Type: {task_type.replace('_', ' ').title()}")
        print(f" Task ID: {result.get('task_id')}")
        print(f" Task Name: {result.get('name', 'N/A')}")
        print(f" Competencies Covered: {', '.join(competencies_covered)}")
        print(f" GitHub Repository: {result.get('resources', {}).get('github_repo', 'N/A')}")
        print()
        
        print(" TASK CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f" Task Type: {task_type.replace('_', ' ').title()}")
        print(f" Competencies: {', '.join(competencies_covered)}")
        print(f" Repository: {result.get('resources', {}).get('github_repo')}")
        print()
        
    except Exception as e:
        print(f" ERROR CREATING TASK!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check your configuration and try again.")
        print("=" * 70)

# === NEW DEPLOYMENT FUNCTIONS ===


def update_task_undeploy_status(task_id: str, env: str = "dev") -> bool:
    """
    Update the task in database to mark it as undeployed.
    Clears deployment_info and sets is_deployed to false.
    
    Args:
        task_id: The task ID to update
        env: Environment ("dev" or "prod")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = init_supabase(env)
        
        # Prepare update data - clear deployment info and mark as undeployed
        update_data = {
            "is_deployed": False,
            "deployment_info": None
        }
        
        logger.info(f"Updating task {task_id} to undeployed status")
        
        # Direct database update
        result = supabase.table("tasks").update(update_data).eq("task_id", task_id).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"Successfully updated task {task_id} to undeployed status")
            logger.info(f"   - is_deployed: False")
            logger.info(f"   - deployment_info: cleared")
            return True
        else:
            logger.error(f"Failed to update task {task_id} - no rows affected")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update task {task_id} undeploy status: {str(e)}")
        return False

def find_task_by_competencies(competency_ids: List[str], env: str = "dev") -> List[dict]:
    """
    Search for undeployed tasks that contain ALL specified competency_ids using Supabase RPC functions.
    
    Args:
        competency_ids: List of competency IDs to search for (all must be present in task)
        env: Environment ("dev" or "prod")
    
    Returns:
        List containing all task data found that contain ALL competency_ids
        Returns empty list if no tasks are found
    
    Raises:
        Exception: If database query fails
    """
    
    # Validate competency_ids
    if not competency_ids or not all(cid and cid.strip() for cid in competency_ids):
        raise ValueError(f"Invalid competency_ids: {competency_ids}. All must be non-empty strings.")
    
    supabase = init_supabase(env)
    
    try:
        # Use single RPC function for all competency searches
        logger.info(f"Searching for undeployed tasks with competencies: {competency_ids}")
        
        result = supabase.rpc("find_tasks_by_competencies", {
            "competency_ids_param": competency_ids
        }).execute()
        logger.info("Used find_tasks_by_competencies RPC function")
        
        if result.data and len(result.data) > 0:
            tasks = result.data
            
            # Add task name to each task object for easier access
            for task in tasks:
                task_name = "unknown"
                task_blob = task.get("task_blob", {})
                if isinstance(task_blob, dict):
                    task_name = task_blob.get("title") or task_blob.get("name") or "unknown"
                task["name"] = task_name
            
            if len(competency_ids) == 1:
                logger.info(f"Found {len(tasks)} undeployed task(s) for competency: {competency_ids[0]}")
            else:
                logger.info(f"Found {len(tasks)} undeployed task(s) containing ALL competencies: {competency_ids}")
            
            # Log task details
            for task in tasks:
                logger.info(f"  - Task ID: {task.get('task_id')}, Name: {task.get('name', 'unknown')}")
                
                # Show competencies in this task for verification
                criterias = task.get("criterias", [])
                if isinstance(criterias, list):
                    task_competencies = [c.get("competency_id") for c in criterias if isinstance(c, dict) and c.get("competency_id")]
                    logger.info(f"    Competencies: {task_competencies}")
            
            return tasks
        
        logger.info(f"No undeployed tasks found for competencies: {competency_ids}")
        return []
        
    except Exception as e:
        logger.error(f"Error calling RPC function for competencies {competency_ids}: {str(e)}")
        
        # Fallback method - direct database query
        logger.info("RPC function failed, using fallback method...")
        try:
            # Direct database query - select all necessary fields
            result = supabase.table("tasks").select(
                "task_id, criterias, task_blob, is_deployed, created_at, deployment_info, pre_requisites, answer, readme_content, eval_info, solutions, is_shared_infra_required"
            ).eq("is_deployed", False).execute()
            
            matching_tasks = []
            if result.data:
                logger.info(f"Found {len(result.data)} total undeployed tasks to search through")
                
                for task in result.data:
                    criterias = task.get("criterias", [])
                    if isinstance(criterias, list):
                        # Get all competency_ids from this task's criterias
                        task_competency_ids = set()
                        for criteria in criterias:
                            if isinstance(criteria, dict) and criteria.get("competency_id"):
                                task_competency_ids.add(criteria.get("competency_id"))
                        
                        # Check if ALL required competencies are present in this task
                        required_competencies = set(competency_ids)
                        if required_competencies.issubset(task_competency_ids):
                            # Extract task name from task_blob if available
                            task_name = "unknown"
                            task_blob = task.get("task_blob", {})
                            if isinstance(task_blob, dict):
                                task_name = task_blob.get("title") or task_blob.get("name") or "unknown"
                            
                            # Add the task name to the task object for easier access later
                            task["name"] = task_name
                            
                            matching_tasks.append(task)
                            logger.info(f"  - Matched Task ID: {task.get('task_id')}, Name: {task_name}")
                            logger.info(f"    Task competencies: {list(task_competency_ids)}")
            
            if matching_tasks:
                if len(competency_ids) == 1:
                    logger.info(f"Found {len(matching_tasks)} undeployed task(s) for competency: {competency_ids[0]} using fallback method")
                else:
                    logger.info(f"Found {len(matching_tasks)} undeployed task(s) containing ALL competencies: {competency_ids} using fallback method")
                return matching_tasks
            
            logger.info(f"No undeployed tasks found for competencies: {competency_ids} using fallback method")
            return []
            
        except Exception as fallback_e:
            logger.error(f"Fallback method also failed: {str(fallback_e)}")
            raise Exception(f"All search methods failed. RPC error: {str(e)}, Fallback error: {str(fallback_e)}")

def download_repo_files(github_repo_url: str, local_dir: str) -> bool:
    """
    Download all files from a GitHub repository to a local directory.
    
    Args:
        github_repo_url: Full GitHub repository URL
        local_dir: Local directory to download files to
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading repository {github_repo_url} to {local_dir}")
        repo_path = github_repo_url.replace("https://github.com/", "").split("/tree/")[0]
        
        g = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        logger.info(f"GitHub client initialized successfully")
        if not g:
            logger.error("Failed to initialize GitHub client")
            return False
        try:
            repo = g.get_repo(repo_path)
            logger.info("Repo ok: %s (private=%s)", repo.full_name, repo.private)
        except GithubException as e:
            logger.error("get_repo failed: HTTP %s | %s", e.status, getattr(e, "data", None))
            raise

        logger.info(f"Repository {repo_path} found successfully")
        
        # Create local directory
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local directory {local_dir} created successfully")
        
        # Get all files from the repository
        contents = repo.get_contents("")
        
        while contents:
            logger.info(f"Processing files")
            file_content = contents.pop(0)
            if file_content.type == "dir":
                # Add directory contents to the list
                contents.extend(repo.get_contents(file_content.path))
            else:
                # Download file
                file_path = local_path / file_content.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, "wb") as f:
                    f.write(file_content.decoded_content)
                
                logger.info(f"Downloaded: {file_content.path}")
        
        logger.info(f"Successfully downloaded repository to: {local_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading repository {github_repo_url}: {str(e)}")
        return False

def execute_run_script(droplet_ip: str, remote_dir: str = "/root/task") -> bool:
    """
    Execute run.sh script on the droplet.

    Args:
        droplet_ip: IP address of the droplet
        remote_dir: Remote directory containing the run.sh script

    Returns:
        True if successful, False otherwise
    """
    ssh_key = get_ssh_key()
    if not ssh_key:
        logger.error("Failed to load SSH key (set DROPLET_SSH_PRIVATE_KEY in env)")
        return False

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            droplet_ip,
            username="root",
            pkey=ssh_key,
            timeout=30
        )
        
        # Check if run.sh exists
        run_script_path = f"{remote_dir}/run.sh"
        stdin, stdout, stderr = ssh.exec_command(f"ls -la {run_script_path}")
        
        if stdout.channel.recv_exit_status() != 0:
            logger.info(f"run.sh not found at {run_script_path}")
            ssh.close()
            return False
        
        # Make run.sh executable
        ssh.exec_command(f"chmod +x {run_script_path}")
        
        # Execute run.sh
        logger.info(f"Executing run.sh on {droplet_ip}...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_dir} && ./run.sh")
        
        # Wait for completion and get output
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()
        
        if stdout_data:
            logger.info(f"run.sh output: {stdout_data}")
        if stderr_data:
            logger.info(f"run.sh errors: {stderr_data}")
        
        ssh.close()
        
        if exit_status == 0:
            logger.info("run.sh executed successfully")
            return True
        else:
            logger.error(f"run.sh failed with exit status: {exit_status}")
            return False
        
    except Exception as e:
        logger.error(f"Error executing run.sh on droplet {droplet_ip}: {str(e)}")
        return False

def update_task_deployment_status(task_id: str, droplet_ip: str, env: str = "dev") -> bool:
    """
    Update the task in database to mark it as deployed - direct database update only.
    Updates only two columns: is_deployed and deployment_info.
    
    Args:
        task_id: The task ID to update
        droplet_ip: IP address of the droplet where task was deployed
        env: Environment ("dev" or "prod")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = init_supabase(env)
        
        # Prepare deployment_info in the new required format
        deployment_info = {
            "server_id": "0f8122d5-f806-4496-b72e-b696145adeb5",
            "droplet_ip": droplet_ip,
            "deployed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "remote_directory": "/root/task",
            "deployment_method": "agent_task_creator",
            "deployment_status": "completed",
            "deployment_timestamp": datetime.datetime.now().timestamp(),
        }
        # Get additional droplet info from DigitalOcean API if available
        droplet_details = get_droplet_info(droplet_ip)
        if droplet_details:
            deployment_info["droplet_details"] = droplet_details
        
        # Prepare update data - only these two columns
        update_data = {
            "is_deployed": True,
            "deployment_info": deployment_info
        }
        
        logger.info(f"Updating task {task_id} deployment status directly in database")
        logger.info(f"Deployment info: {deployment_info}")
        
        # Direct database update
        result = supabase.table("tasks").update(update_data).eq("task_id", task_id).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f" Successfully updated task {task_id} deployment status")
            logger.info(f"   - is_deployed: True")
            logger.info(f"   - deployment_info: {json.dumps(deployment_info, indent=2)}")
            return True
        else:
            logger.error(f" Failed to update task {task_id} - no rows affected")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update task {task_id} deployment status: {str(e)}")
        return False

def parse_competency_input(competency_input: str) -> List[str]:
    """
    Parse competency input string to extract individual competency IDs.
    Supports various formats:
    - Single competency: "comp1"
    - Comma-separated: "comp1,comp2,comp3"
    - Space-separated: "comp1 comp2 comp3"
    - Mixed: "comp1, comp2 comp3"
    
    Args:
        competency_input: String containing one or more competency IDs
    
    Returns:
        List of competency IDs
    """
    if not competency_input or not competency_input.strip():
        return []
    
    # Replace commas with spaces and split
    competency_ids = [cid.strip() for cid in competency_input.replace(',', ' ').split() if cid.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_competency_ids = []
    for cid in competency_ids:
        if cid not in seen:
            seen.add(cid)
            unique_competency_ids.append(cid)
    
    return unique_competency_ids

def select_best_droplet_ip(droplet_ips: List[str]) -> str:
    """
    Check each IP for running Docker containers and return the first IP with no containers.
    """
    ssh_key = get_ssh_key()
    if not ssh_key:
        logger.error("Failed to load SSH key (set DROPLET_SSH_PRIVATE_KEY in env)")
        return None

    for ip in droplet_ips:
        logger.info(f"Checking IP {ip} for running containers")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(
                ip,
                username="root",
                pkey=ssh_key,
                timeout=10
            )
            
            # Execute docker ps to count containers
            stdin, stdout, stderr = ssh.exec_command("docker ps -q | wc -l")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                container_count = int(stdout.read().decode().strip())
                if container_count == 0:
                    logger.info(f"Found IP {ip} with no running containers")
                    return ip
                logger.info(f"IP {ip} has {container_count} containers running")
            else:
                error = stderr.read().decode().strip()
                logger.error(f"Failed to check containers on {ip}: {error}")
                
        except Exception as e:
            logger.error(f"Error checking {ip}: {str(e)}")
        finally:
            # Always close the SSH connection
            ssh.close()
    
    logger.info("No IPs found without running containers")
    return None

def deploy_existing_task(competency_input: str, droplet_ip: str = None, env: str = "dev") -> bool:
    """
    Deploy existing undeployed tasks for one or more competencies to available droplets.
    
    For single competency: Finds tasks containing that specific competency
    For multiple competencies: Finds tasks containing ALL specified competencies
    
    This function:
    1. Parses competency input (supports single or multiple competencies)
    2. Searches for ALL undeployed tasks with the given competency/competencies
    3. Gets ALL available droplet IPs (if not specified)
    4. Deploys only as many tasks as there are available droplets (one task per droplet)
    5. For each task: downloads files, uploads to droplet, executes run.sh, updates database
    
    Args:
        competency_input: Single competency ID or multiple competency IDs (comma/space separated)
        droplet_ip: IP address of specific droplet to use (if None, auto-select all available)
        env: Environment ("dev" or "prod")
    
    Returns:
        True if at least one deployment successful, False if all deployments failed
    """
    
    # Parse competency input to handle single or multiple competencies
    competency_ids = parse_competency_input(competency_input)
    
    if not competency_ids:
        print(f" Invalid competency input: {competency_input}")
        return False
    
    if len(competency_ids) == 1:
        print(f" Searching for ALL undeployed tasks with competency_id: {competency_ids[0]}")
    else:
        print(f" Searching for ALL undeployed tasks containing ALL competencies: {', '.join(competency_ids)}")
        print(f"   Note: Tasks must contain ALL {len(competency_ids)} competencies to be selected")
    
    # Step 1: Find ALL undeployed tasks for these competencies
    tasks = find_task_by_competencies(competency_ids, env)
    if not tasks:
        if len(competency_ids) == 1:
            print(f" No undeployed tasks found for competency_id: {competency_ids[0]}")
        else:
            print(f" No undeployed tasks found containing ALL competencies: {', '.join(competency_ids)}")
        return False
    
    if len(competency_ids) == 1:
        print(f" Found {len(tasks)} undeployed task(s) for competency: {competency_ids[0]}")
    else:
        print(f" Found {len(tasks)} undeployed task(s) containing ALL competencies: {', '.join(competency_ids)}")
    
    for i, task in enumerate(tasks, 1):
        task_name = task.get("name", "unknown")
        task_id = task.get("task_id")
        
        # Show which competencies this task contains
        criterias = task.get("criterias", [])
        task_competencies = []
        if isinstance(criterias, list):
            for criteria in criterias:
                if isinstance(criteria, dict) and criteria.get("competency_id"):
                    task_competencies.append(criteria.get("competency_id"))
        
        print(f"   {i}. {task_name} (ID: {task_id})")
        print(f"      Competencies: {', '.join(task_competencies) if task_competencies else 'None found'}")
    
    # Step 2: Get available droplet IPs
    if droplet_ip:
        # Use only the specified droplet IP
        available_droplets = [droplet_ip]
        print(f" Using specified droplet: {droplet_ip}")
    else:
        # Get all available droplet IPs
        print(f" Getting all available droplet IPs...")
        available_droplets = get_available_droplet_ips()
        if not available_droplets:
            print(f" No droplet IPs configured in environment variable EXISTING_DROPLET_IP")
            return False
        
        print(f" Found {len(available_droplets)} available droplet(s): {', '.join(available_droplets)}")
    
    # Step 3: Deploy tasks to available droplets (one task per droplet maximum)
    successful_deployments = 0
    failed_deployments = 0
    deployment_results = []
    
    # Limit tasks to number of available droplets (one task per droplet)
    max_deployments = len(available_droplets)
    tasks_to_deploy = tasks[:max_deployments]
    remaining_tasks = tasks[max_deployments:]
    
    if remaining_tasks:
        print(f"  Found {len(tasks)} tasks but only {len(available_droplets)} droplets available")
        print(f"    Only {len(tasks_to_deploy)} task(s) will be deployed (one per droplet)")
        print(f"     {len(remaining_tasks)} task(s) will remain undeployed:")
        for i, task in enumerate(remaining_tasks, 1):
            print(f"     {i}. {task.get('name', 'unknown')} (ID: {task.get('task_id')})")
    
    print(f"\n Starting deployment of {len(tasks_to_deploy)} task(s) to {len(available_droplets)} droplet(s)...")
    print("=" * 70)
    
    for task_index, task in enumerate(tasks_to_deploy):
        task_id = task.get("task_id")
        task_name = task.get("name", "unknown")
        github_repo_url = task.get("task_blob", {}).get("resources", {}).get("github_repo")
        
        # Show task competencies
        criterias = task.get("criterias", [])
        task_competencies = []
        if isinstance(criterias, list):
            for criteria in criterias:
                if isinstance(criteria, dict) and criteria.get("competency_id"):
                    task_competencies.append(criteria.get("competency_id"))
        
        # Assign task to specific droplet (one-to-one mapping)
        selected_droplet = available_droplets[task_index]
        
        print(f"\n DEPLOYING TASK {task_index + 1}/{len(tasks_to_deploy)}")
        print(f"   Task: {task_name} (ID: {task_id})")
        print(f"   Competencies: {', '.join(task_competencies) if task_competencies else 'None found'}")
        print(f"   Droplet: {selected_droplet}")
        print(f"   GitHub: {github_repo_url}")
        print("-" * 50)
        
        if not github_repo_url:
            print(f" No GitHub repository found for task: {task_name}")
            failed_deployments += 1
            deployment_results.append({
                "task_id": task_id,
                "task_name": task_name,
                "droplet_ip": selected_droplet,
                "status": "failed",
                "reason": "No GitHub repository",
                "competencies": task_competencies
            })
            continue
        
        # Download files from GitHub
        print(f" Downloading files from GitHub repository...")
        local_dir = f"temp_deploy_{task_id}"
        
        if not download_repo_files(github_repo_url, local_dir):
            print(f" Failed to download files from GitHub repository")
            failed_deployments += 1
            deployment_results.append({
                "task_id": task_id,
                "task_name": task_name,
                "droplet_ip": selected_droplet,
                "status": "failed",
                "reason": "GitHub download failed",
                "competencies": task_competencies
            })
            continue
        
        print(f" Files downloaded to: {local_dir}")
        
        # Upload files to droplet
        print(f" Uploading files to droplet: {selected_droplet}")
        
        if not upload_files_to_droplet(local_dir, selected_droplet):
            print(f" Failed to upload files to droplet")
            # Clean up local files
            try:
                import shutil
                shutil.rmtree(local_dir)
            except:
                pass
            failed_deployments += 1
            deployment_results.append({
                "task_id": task_id,
                "task_name": task_name,
                "droplet_ip": selected_droplet,
                "status": "failed",
                "reason": "Upload to droplet failed",
                "competencies": task_competencies
            })
            continue
        
        print(f" Files uploaded to droplet")

        # Execute run.sh script
        print(f"  Executing run.sh script on droplet...")
        
        run_script_success = execute_run_script(selected_droplet)
        if not run_script_success:
            print(f"  Failed to execute run.sh script")
            print(f"   Files are uploaded but run.sh failed - skipping database update")
            db_update_success = False
        else:
            print(f" run.sh executed successfully")
            
            # Only update database if run.sh executes successfully
            print(f" Updating database to mark task as deployed...")
            
            db_update_success = update_task_deployment_status(task_id, selected_droplet, env)
            if not db_update_success:
                print(f" Failed to update database")
                print(f"   Task is deployed but database update failed")
            else:
                print(f" Database updated successfully")
        
        # Clean up local files
        try:
            import shutil
            shutil.rmtree(local_dir)
            print(f"🧹 Cleaned up local files")
        except Exception as e:
            print(f"  Failed to clean up local files: {str(e)}")
        
        # Determine if this deployment was successful
        if run_script_success and db_update_success:
            print(f" Task '{task_name}' deployed successfully to {selected_droplet}")
            successful_deployments += 1
            deployment_results.append({
                "task_id": task_id,
                "task_name": task_name,
                "droplet_ip": selected_droplet,
                "status": "success",
                "ssh_access": f"ssh root@{selected_droplet}",
                "remote_directory": "/root/task",
                "competencies": task_competencies
            })
        else:
            print(f"  Task '{task_name}' partially deployed to {selected_droplet} (some steps failed)")
            failed_deployments += 1
            deployment_results.append({
                "task_id": task_id,
                "task_name": task_name,
                "droplet_ip": selected_droplet,
                "status": "partial",
                "reason": f"run.sh: {'OK' if run_script_success else 'FAILED'}, db_update: {'OK' if db_update_success else 'FAILED'}",
                "competencies": task_competencies
            })
    
    # Step 4: Display final deployment summary
    print("\n" + "=" * 70)
    print(" DEPLOYMENT SUMMARY")
    print("=" * 70)
    if len(competency_ids) == 1:
        print(f" Target Competency: {competency_ids[0]}")
    else:
        print(f" Target Competencies: {', '.join(competency_ids)} (ALL required)")
    print(f" Total Tasks Found: {len(tasks)}")
    print(f" Tasks Attempted for Deployment: {len(tasks_to_deploy)}")
    print(f"  Tasks Not Deployed (No Available Droplets): {len(remaining_tasks) if remaining_tasks else 0}")
    print(f" Successful Deployments: {successful_deployments}")
    print(f" Failed Deployments: {failed_deployments}")
    print(f"  Available Droplets: {len(available_droplets)}")
    print()
    
    if remaining_tasks:
        print("  TASKS NOT DEPLOYED (No Available Droplets):")
        for task in remaining_tasks:
            criterias = task.get("criterias", [])
            task_competencies = []
            if isinstance(criterias, list):
                for criteria in criterias:
                    if isinstance(criteria, dict) and criteria.get("competency_id"):
                        task_competencies.append(criteria.get("competency_id"))
            print(f"   • {task.get('name', 'unknown')} (ID: {task.get('task_id')})")
            print(f"     Competencies: {', '.join(task_competencies) if task_competencies else 'None found'}")
        print()
    
    if successful_deployments > 0:
        print(" SUCCESSFUL DEPLOYMENTS:")
        for result in deployment_results:
            if result["status"] == "success":
                print(f"   • {result['task_name']} -> {result['droplet_ip']}")
                print(f"     Competencies: {', '.join(result['competencies']) if result['competencies'] else 'None found'}")
                print(f"     SSH: {result['ssh_access']}")
                print(f"     Directory: {result['remote_directory']}")
        print()
    
    if failed_deployments > 0:
        print(" FAILED/PARTIAL DEPLOYMENTS:")
        for result in deployment_results:
            if result["status"] in ["failed", "partial"]:
                print(f"   • {result['task_name']} -> {result['droplet_ip']} ({result.get('reason', 'Unknown error')})")
                print(f"     Competencies: {', '.join(result['competencies']) if result['competencies'] else 'None found'}")
        print()
    # Return True if at least one deployment was successful
    return successful_deployments > 0

def deploy_task_by_id(task_id: str, tasksession_id: Optional[str] = None, droplet_ip: str = None, env: str = "dev") -> bool:
    """
    Deploy a specific task by its task ID to a droplet.
    
    Args:
        task_id: The specific task ID to deploy
        droplet_ip: IP address of specific droplet to use (if None, auto-select)
        env: Environment ("dev" or "prod")
    
    Returns:
        True if deployment successful, False otherwise
    """
    
    logger.info(f" Searching for task with ID: {task_id}")
    
    # Step 1: Find the specific task by ID
    try:
        supabase = init_supabase(env)
        
        # Get the specific task
        result = supabase.table("tasks").select(
            "task_id, criterias, task_blob, is_deployed, created_at, deployment_info, pre_requisites, answer, readme_content, eval_info, solutions, is_shared_infra_required"
        ).eq("task_id", task_id).execute()
        
        if not result.data or len(result.data) == 0:
            logger.info(f" Task with ID {task_id} not found in database")
            return False
        
        task = result.data[0]
        
        # Check if task is already deployed
        if task.get("is_deployed", False):
            logger.info(f" Task {task_id} is already deployed")
            
            # Show deployment info if available
            deployment_info = task.get("deployment_info", {})
            if isinstance(deployment_info, dict):
                droplet_ip = deployment_info.get("droplet_ip", "unknown")
                logger.info(f"   Deployed to: {droplet_ip}")    
        
        # Extract task details
        task_name = "unknown"
        github_repo_url = None
        task_blob = task.get("task_blob", {})
        if isinstance(task_blob, dict):
            task_name = task_blob.get("title") or task_blob.get("name") or "unknown"
            resources = task_blob.get("resources", {})
            if isinstance(resources, dict):
                github_repo_url = resources.get("github_repo")
        
         
        if not github_repo_url:
            logger.info(f" No GitHub repository found for task: {task_name}")
            return False

        if tasksession_id:  
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "GitHub Repository found for the task"}
            }).eq("tasksession_id", tasksession_id).execute()
        
    except Exception as e:
        logger.info(f" Error finding task {task_id}: {str(e)}")
        return False
    
    # Step 2: Get droplet IP
    if droplet_ip:
        selected_droplet = droplet_ip
        logger.info(f" Using specified droplet: {selected_droplet}")
    else:
        logger.info(f" Getting available droplet IPs...")

        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Getting available droplet IPs..."}
            }).eq("tasksession_id", tasksession_id).execute()
        available_droplets = get_available_droplet_ips()
        if not available_droplets:
            logger.info(f" No droplet IPs configured in environment variable DIGITAL_OCEAN_IPS")
            return False
        
        selected_droplet = select_best_droplet_ip(available_droplets)
        logger.info(f" Auto-selected droplet: {selected_droplet}")
        if not selected_droplet:
            if tasksession_id:
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "FAILED", "message": "No available droplets found"}
                }).eq("tasksession_id", tasksession_id).execute()
            logger.info(f" No available droplets found")
            return False
        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Droplet Selected"}
            }).eq("tasksession_id", tasksession_id).execute()
    
    # Step 3: Deploy the task
    
    try:
        # Download files from GitHub
        logger.info(f" Downloading files from GitHub repository...")
        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Downloading files from GitHub repository..."}
            }).eq("tasksession_id", tasksession_id).execute()
        local_dir = f"temp_deploy_{task_id}"
        
        if not download_repo_files(github_repo_url, local_dir):
            if tasksession_id:
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "FAILED", "message": "Failed to download files from GitHub repository"}
                }).eq("tasksession_id", tasksession_id).execute()
            logger.info(f" Failed to download files from GitHub repository")
            return False
        
        logger.info(f" Files downloaded to: {local_dir}")
        
        # Upload files to droplet
        logger.info(f" Uploading files to droplet: {selected_droplet}")
        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Uploading files to droplet..."}
            }).eq("tasksession_id", tasksession_id).execute()
        
        if not upload_files_to_droplet(local_dir, selected_droplet):
            if tasksession_id:
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "FAILED", "message": "Failed to upload files to droplet"}
                }).eq("tasksession_id", tasksession_id).execute()
            logger.info(f" Failed to upload files to droplet")
            # Clean up local files
            try:
                shutil.rmtree(local_dir)
            except:
                pass
            return False
        
        logger.info(f" Files uploaded to droplet")
        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Files uploaded to droplet"}
            }).eq("tasksession_id", tasksession_id).execute()

        # Execute run.sh script
        logger.info(f"  Executing run.sh script on droplet...")
        if tasksession_id:
            #update deployment log table with task id
            supabase.table("task_deployment_jobs").update({
                "log": {"status": "STARTED", "message": "Executing run.sh script on droplet..."}
            }).eq("tasksession_id", tasksession_id).execute()
        
        run_script_success = execute_run_script(selected_droplet)
        if not run_script_success:
            if tasksession_id:
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "FAILED", "message": "Failed to execute run.sh script"}
                }).eq("tasksession_id", tasksession_id).execute()
            logger.info(f" Failed to execute run.sh script")
            logger.info(f"   Files are uploaded but run.sh failed")
            # Do not update database if run.sh fails
            db_update_success = False
        else:
            logger.info(f" run.sh executed successfully")
            if tasksession_id:
                #update deployment log table with task id
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "STARTED", "message": "run.sh executed successfully"}
                }).eq("tasksession_id", tasksession_id).execute()
            # Only update database if run.sh succeeds
            db_update_success = update_task_deployment_status(task_id, selected_droplet, env)
            if not db_update_success:
                logger.info(f" Failed to update database")
                logger.info(f"   Task is deployed but database update failed")
            else:
                logger.info(f" Database updated successfully")
        
        # Clean up local files
        try:
            shutil.rmtree(local_dir)
            logger.info(f" Cleaned up local files")
        except Exception as e:
            logger.info(f" Failed to clean up local files: {str(e)}")
        
        # Determine if deployment was successful
        if run_script_success and db_update_success:
            logger.info(f"\n Task '{task_name}' deployed successfully to {selected_droplet}")
            logger.info(f"   SSH access: ssh root@{selected_droplet}")
            logger.info(f"   Remote directory: /root/task")
            if tasksession_id:
                #update deployment log table with task id
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "STARTED", "message": "Task deployed successfully to {selected_droplet}"}
                }).eq("tasksession_id", tasksession_id).execute()

            # schedule task after everything is done

            logger.info(f"DEPLOYMENT DONE, back to scheduling")
            if tasksession_id:
                #update deployment log table with task id
                supabase.table("task_deployment_jobs").update({
                    "log": {"status": "STARTED", "message": "Scheduling your task..."}
                }).eq("tasksession_id", tasksession_id).execute()
            server_id = None
            task_blobs = []
        
            # Refresh task data to get the latest deployment info
            task_response = supabase.table('tasks').select('*').eq('task_id', task_id).execute()
            if task_response.data:
                task = task_response.data[0]
                logger.info(f"Refreshed task data with deployment info")
                server_id = task['deployment_info']['server_id'] if task['deployment_info'] else None
            else:
                logger.error(f"Failed to refresh task data after deployment for task_id: {task_id}")
                return JSONResponse({
                    "status": "error",
                    "message": "Failed to refresh task data after deployment"
                }, status_code=500)
            logger.info(f"Fetching keys for server_id={server_id} from task_servers table")
            try:
                server_row = supabase.table('task_servers').select('private_key_master_path, public_key_master_path').eq('server_id', server_id).single().execute()
                if server_row.data:
                    private_key = server_row.data.get('private_key_master_path')
                    public_key = server_row.data.get('public_key_master_path')
                    logger.info(f"Found keys for server_id={server_id}: private_key={'set' if private_key else 'not set'}, public_key={'set' if public_key else 'not set'}")
                else:
                    logger.info(f"No keys found for server_id={server_id} in task_servers table")
            except Exception as e:
                logger.error(f"Error querying task_servers for server_id={server_id}: {str(e)}")

            try:
                logger.info(f"preparing task blob")
                logger.info(f"task deployment info: {task['deployment_info']}")
                task_blob = {
                    "q_id": task['task_id'],
                    "type": 'task',
                    "score": 0,
                    "question_blob": {
                        "hints": task['task_blob']['hints'],
                        "title": task['task_blob']['title'],
                        "outcomes": task['task_blob']['outcomes'],
                        "question": task['task_blob']['question'],
                        "resources": task['task_blob']['resources'],
                        "definitions": task['task_blob']['definitions'],
                        "prerequisites": task['pre_requisites'],
                        "private_key": private_key,
                        "public_key": public_key,
                        "competencies": task['criterias'],
                        "droplet_ip": task['deployment_info']['droplet_ip'] if task['deployment_info'] else None
                    },
                    "answerChosen": None,
                    "isCorrect": None,
                    "analysis": None,
                    "start_ts": None,
                    "check_ts": None,
                    "skip_ts": None,
                    "next_ts": None,
                    "duration_seconds": 0,
                }
                task_blobs.append(task_blob)
                response = supabase.table('task_sessions').update({
                    'tasks': task_blobs,
                }).eq("tasksession_id", tasksession_id).execute()

                report = response.data[0] if response.data else None
                logger.info(f"\n *** Task blob added: {report['tasksession_id']}\n")
                if tasksession_id:
                    #update deployment log table with task id
                    supabase.table("task_deployment_jobs").update({
                        "log": {"status": "COMPLETED", "message": "Task ready"}
                    }).eq("tasksession_id", tasksession_id).execute()
            except Exception as e:
                logger.error(f"Error adding task blob: {str(e)}")
            return True
        else:
            print(f"\n Task '{task_name}' partially deployed to {selected_droplet}")
            print(f"   run.sh: {'OK' if run_script_success else 'FAILED'}")
            print(f"   database update: {'OK' if db_update_success else 'FAILED'}")
            return False
    
    except Exception as e:
        print(f" Error during deployment: {str(e)}")
        # Clean up local files on error
        try:
            shutil.rmtree(f"temp_deploy_{task_id}")
        except:
            pass
        return False

# --- 1. Add function to generate answer code and steps ---
def generate_answer_code_and_steps(task_data: Dict) -> Dict:
    """
    Generate fully implemented answer code files and a step-by-step solution guide using the LLM.
    Returns: {"files": {...}, "steps": [...]}
    """
    try:
        task_description = task_data.get("description", "")
        task_question = task_data.get("question", "")
        task_name = task_data.get("name", "")
        task_outcomes = task_data.get("outcomes", "")
        criterias = task_data.get("criterias", [])
        
        if criterias and isinstance(criterias, list):
            competency_names = [c.get("name", "") for c in criterias]
            competency_info = f"Competencies: {', '.join(competency_names)}"
        else:
            competency_info = "No specific competencies"
        
        # Use imported schema from schema_models.py
        answer_code_schema = ANSWER_CODE_SCHEMA
        
        system_prompt = (
            "You are an expert engineer. Given the following assessment task, generate the fully implemented solution code files (with correct implementation) for all files the candidate is supposed to complete. "
            "Also, provide a step-by-step solution guide (as an array of strings) that explains how to implement the solution. "
            "The 'files' object must contain the full, correct implementation for each file the candidate is expected to complete. "
            "The 'steps' field must be an array of clear, high-level, step-by-step instructions for a human to follow to implement the solution. "
            "No need to generate the README file."
        )
        
        user_prompt = (
            f"TASK NAME: {task_name}\n"
            f"TASK DESCRIPTION: {task_description}\n"
            f"QUESTION: {task_question}\n"
            f"EXPECTED OUTCOMES: {task_outcomes}\n"
            f"{competency_info}\n"
            "---\n"
            "Generate the fully implemented code files for this task, and a step-by-step solution guide."
        )
        
        # Build messages for Responses API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use Responses API with reasoning and structured JSON output
        response = openai_client.responses.create(
            model=model,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "verbosity": "medium",
                "format": {
                    "type": "json_schema",
                    "name": answer_code_schema["name"],
                    "schema": answer_code_schema["schema"],
                    "strict": answer_code_schema["strict"]
                }
            }
        )
        
        # Extract output_text from response
        response_text = getattr(response, "output_text", None)
        if not response_text:
            logger.error("No output_text received from OpenAI Responses API")
            raise RuntimeError("Failed to get output_text from OpenAI Responses API")
        
        # Parse JSON from response
        answer_data = json.loads(response_text)
        
        logger.info(f"Generated solution with {len(answer_data.get('files', {}))} files and {len(answer_data.get('steps', []))} steps")
        return answer_data
        
    except Exception as e:
        logger.error(f"Error generating answer code and steps: {str(e)}")
        # Return empty structure as fallback
        return {"files": {}, "steps": []}

# --- 2. Add function to create answer repo and upload files ---
def create_answer_github_repo(base_name: str) -> str:
    """Create a new GitHub repository for the answer/solution files."""
    # Apply slugify to ensure the base name is GitHub-compatible
    slugified_base = slugify(base_name)
    return create_github_repo(slugified_base + "-answers", is_public=True)

def upload_answer_files_to_repo(repo_name: str, answer_code_data: Dict):
    """Upload answer files to the answer GitHub repo in a single commit."""
    try:
        # Validate files before upload
        if not answer_code_data or "files" not in answer_code_data:
            logger.info("No files provided in answer_code_data")
            return
            
        files = answer_code_data["files"]
 
        # Validate each file has content
        def is_empty_content(content):
            if not content:
                return True
            if isinstance(content, str):
                return not content.strip()
            if isinstance(content, dict):
                return not any(content.values())
            return False

        empty_files = [path for path, content in files.items() if is_empty_content(content)]
        if empty_files:
            logger.info(f"Empty content found for files: {empty_files}")
            # Filter out empty files
            files = {path: content for path, content in files.items() if not is_empty_content(content)}

        # Convert dictionary content to JSON string if necessary and strip leading slashes
        processed_files = {}
        for path, content in files.items():
            # Strip leading slash from file path as GitHub API doesn't allow paths starting with /
            clean_path = path.lstrip('/')
            if isinstance(content, dict):
                processed_files[clean_path] = json.dumps(content, indent=2)
            else:
                processed_files[clean_path] = content
        
        # Create SOLUTION.md file
        if "steps" in answer_code_data and answer_code_data["steps"]:
            solution_md_content = "# Solution Steps\n\n"
            steps = answer_code_data["steps"]
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    solution_md_content += f"{i}. {step}\n\n"
            else:
                solution_md_content += str(steps)
            processed_files["SOLUTION.md"] = solution_md_content
                
     
        logger.info(f"Uploading {len(processed_files)} files to answer repository: {repo_name} in a single commit")
        upload_files_to_github(repo_name, {"code_files": processed_files})

    except Exception as e:
        logger.error(f"Error uploading answer files to repo {repo_name}: {str(e)}")
        # Don't raise exception to avoid breaking main task creation

if __name__ == "__main__":
    cli = click.Group()
    cli.add_command(generate_tasks, name="generate_tasks")
    cli.add_command(deploy_task, name="deploy_task")
    cli.add_command(reset_task, name="reset_task")
    cli()