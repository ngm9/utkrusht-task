import re
import json
import traceback
import requests
import base64
from urllib.parse import urlparse
from pathlib import Path
from logger_config import logger
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


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


PROFICIENCY_LEVELS = ["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED", "EXPERT"]

TASK_GENERATION_SYSTEM_PROMPT = """
You are a technical architect responsible for generating task definitions for given competencies. These task definitions are going to be given to candidates to solve in a timed format with or without AI assistance.
You have 15+ years of experience and have taken 500+ interviews so you understand the importance of generating real world scenarios for the given competencies and for the given proficiency levels.
"""

def read_json_file_robust(file_path: Path) -> dict:
    """
    Robust JSON file reader that tries multiple encodings to handle various file formats.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        dict: Parsed JSON data
        
    Raises:
        Exception: If file cannot be read with any encoding or JSON is invalid
    """
    # List of encodings to try in order of preference
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
            logger.error(f"JSON decode error in {file_path} with encoding {encoding}: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path} with encoding {encoding}: {str(e)}")
            last_exception = e
            continue
    
    # If we get here, all encodings failed
    raise Exception(f"Failed to read {file_path} with any encoding. Last error: {str(last_exception)}")

def parse_markdown_to_json(md_text):
    if not md_text:
        logger.warning("Empty README content received")
        return {
            "task_overview": "",
            "objectives": [],
            "how_to_verify": [],
            "helpful_tips": []
        }

    sections = {
        "task_overview": "",
        "objectives": [],
        "how_to_verify": [],
        "helpful_tips": []
    }

    current_section = None
    current_content = []
    lines = md_text.splitlines()

    for line in lines:
        line = line.strip()

        # Check for section headers first
        if re.match(r"^#+\s+Task\s*Overview", line, re.IGNORECASE):
            if current_section == "task_overview":
                sections["task_overview"] = " ".join(current_content).strip()
            current_section = "task_overview"
            current_content = []
            continue
        elif re.match(r"^#+\s+Objectives", line, re.IGNORECASE):
            if current_section == "task_overview":
                sections["task_overview"] = " ".join(current_content).strip()
            current_section = "objectives"
            current_content = []
            continue
        elif re.match(r"^#+\s+How\s+to\s+Verify", line, re.IGNORECASE):
            # Save previous section if needed
            if current_section == "task_overview":
                sections["task_overview"] = " ".join(current_content).strip()
            current_section = "how_to_verify"
            current_content = []
            continue
        elif re.match(r"^#+\s+Helpful\s+Tips", line, re.IGNORECASE):
            # Save previous section if needed
            if current_section == "task_overview":
                sections["task_overview"] = " ".join(current_content).strip()
            current_section = "helpful_tips"
            current_content = []
            continue
        elif line.startswith("#"):
            if current_section == "task_overview":
                sections["task_overview"] = " ".join(current_content).strip()
            current_section = None
            current_content = []
            continue

        if not line:
            if current_section == "task_overview":
                current_content.append("")
            continue

        if not current_section:
            continue

        if current_section == "task_overview":
            current_content.append(line)
        else:
            if line.startswith("- ") or line.startswith("* "):
                item = line[2:].strip()
                if item:
                    sections[current_section].append(item)
            elif line and sections[current_section]:
                sections[current_section][-1] += " " + line
            elif line:
                sections[current_section].append(line)

    if current_section == "task_overview" and current_content:
        sections["task_overview"] = " ".join(current_content).strip()

    # Clean up sections
    for key in ["objectives", "how_to_verify", "helpful_tips"]:
        sections[key] = [item.strip() for item in sections[key] if item.strip()]

    for section, content in sections.items():
        if not content:
            logger.warning(f"Empty section found in README: {section}")

    return sections

def has_shared_infra_files(code_data: Dict) -> bool:
    """Check if code_data contains Dockerfile or docker-compose files. Returns True if Docker files are found, False otherwise."""
    docker_filenames = [
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"
    ]
    files = code_data.get("files", {})
    
    # First check for Docker files - if found, return True immediately
    for fname in files.keys():
        if any(fname.lower() == d.lower() for d in docker_filenames):
            return True
    
    # If no Docker files found, return False
    return False

def format_pre_requisites(pre_requisites):
    """
    Format pre_requisites as a list of strings (array of bullet points).

    This mirrors the behavior in non_tech_flow/non_tech_utils.py so that:
    - If LLM already returns an array, we keep it as-is (after trimming).
    - If LLM returns a multi-line string, we split ONLY on newlines (not commas),
      strip any leading bullet markers ("-", "*") and whitespace, and keep each
      non‑empty line as one bullet.
    """
    if not pre_requisites:
        return []

    # If it's already a list, return it as-is (cleaned)
    if isinstance(pre_requisites, list):
        return [str(item).strip() for item in pre_requisites if str(item).strip()]

    # If it's a string, split by newlines only (not commas), strip bullet points, and keep as list
    if isinstance(pre_requisites, str):
        items = [
            item.strip("-* ").strip()
            for item in pre_requisites.split("\n")
            if item.strip("-* ").strip()
        ]
        return items

    # For any other type, convert to string and return as single-item list
    return [str(pre_requisites).strip()]

def format_outcomes(outcomes):
    """
    Format outcomes as a list of strings (array of bullet points).

    Behavior:
    - If already a list: trim each non-empty item and keep as-is.
    - If a multi-line string: split ONLY on newline characters, strip any leading
      bullet markers ("-", "*") and whitespace, and keep each non-empty line as
      one separate outcome.
    - If empty/None: return empty list.
    """
    if not outcomes:
        return []

    if isinstance(outcomes, list):
        return [str(item).strip() for item in outcomes if str(item).strip()]

    if isinstance(outcomes, str):
        items = [
            line.strip("-* ").strip()
            for line in outcomes.split("\n")
            if line.strip("-* ").strip()
        ]
        return items

    return [str(outcomes).strip()]

def split_steps_to_array(steps_str):
    """Split a solution steps string into an array of steps, formatted as 'Step N: ...'"""
    import re
    # Try to split by numbered list or bullet points, fallback to lines
    steps = []
    # Split by numbered list (e.g., 1. ... 2. ...)
    numbered = re.split(r'\n\s*\d+\.\s+', steps_str)
    if len(numbered) > 1:
        steps = [s.strip() for s in numbered if s.strip()]
    else:
        # Split by bullet points
        bullets = re.split(r'\n\s*[-*]\s+', steps_str)
        if len(bullets) > 1:
            steps = [s.strip() for s in bullets if s.strip()]
        else:
            # Fallback: split by lines, ignore empty
            steps = [s.strip() for s in steps_str.splitlines() if s.strip()]
    # Clean up and format each step as 'Step N: ...'
    formatted_steps = []
    for idx, step in enumerate(steps, 1):
        # Remove any leading numbering, bullets, or extra whitespace
        step = re.sub(r'^(\d+\.|[-*])\s*', '', step)
        step = step.strip()
        formatted_steps.append(f"Step {idx}: {step}")
    return formatted_steps

def unwrap_file_contents(files_dict):
    new_files = {}
    for file_path, content in files_dict.items():
        if isinstance(content, dict) and "content" in content and isinstance(content["content"], str):
            new_files[file_path] = content["content"]
        else:
            new_files[file_path] = content
    return new_files

def save_files_locally(task_id: str, task_data: Dict) -> Path:
    """Save generated files locally before uploading to GitHub and droplet."""
    try:
        base_dir = Path(__file__).parent / "infra_assets"
        local_task_dir = base_dir / "tasks" / task_id
        local_task_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving files locally to: {local_task_dir}")
 
        # Save task.json file (local only)
        task_json_path = local_task_dir / "task.json"
        with open(task_json_path, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
        logger.info("Saved task.json locally (local only)")

        # Save all files
        for file_path, content in task_data.get("code_files", {}).items():
            # Strip leading slash for local file path creation
            clean_file_path = file_path.lstrip('/')
            local_file_path = local_task_dir / clean_file_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_file_path, 'w', encoding='utf-8') as f:
                if isinstance(content, dict):
                    f.write(json.dumps(content, indent=2, ensure_ascii=False))
                else:
                    f.write(str(content))
            
            logger.info(f"Saved locally: {clean_file_path}")
        
        # Save scripts and README
        for script_name, script_key in [("install.sh", "install_script"), ("run.sh", "run_script"), ("README.md", "readme")]:
            if script_key in task_data:
                script_path = local_task_dir / script_name
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(task_data[script_key])
                logger.info(f"Saved {script_name} locally")
        
        return local_task_dir
        
    except Exception as e:
        logger.error(f"Error saving files locally: {str(e)}")
        raise

def clean_llm_json_response(response: str) -> str:
    """Clean LLM response to extract valid JSON"""
    try:
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        return response
    except Exception as e:
        logger.error(f"Error cleaning LLM response: {str(e)}")
        return response

def get_task_prompt_by_technology_stack(competency_stack, input_data):
    """Get task prompt by technology stack. Auto-discovered from PROMPT_REGISTRY in each prompt module."""
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
    """Generate task and code files using language_prompts with Responses API and reasoning.
    
    Args:
        openai_client: OpenAI client
        input_data: Dictionary containing:
            - competencies: List of competency data
            - background: Background data
            - scenarios: List of relevant scenarios
    Returns:
        Dict: Generated task data with code files
    """
    try:
        model = "gpt-5.1-2025-11-13"  # Specified model version
        competencies = input_data["competencies"]

        # Get competency names and create a single technology stack string
        competency_names = [comp.get("name") for comp in competencies] 
        competency_stack = ", ".join(competency_names) # e.g. "Python - FastAPI, PostgreSQL"
        
        logger.info(f"Using technology stack: {competency_stack} for competencies: {competency_names}")
            
        # Build input messages for Responses API - start with system message
        messages = [{
            "role": "system", 
            "content": TASK_GENERATION_SYSTEM_PROMPT
        }]
        
        task_generation_prompts = get_task_prompt_by_technology_stack(competency_stack, input_data)

        # Check if prompts are available for this technology stack
        if not task_generation_prompts:
            logger.error(f"No task generation prompts found for technology stack: {competency_stack}")
            raise ValueError(f"Unsupported technology stack: {competency_stack}. Please add prompts for this stack in get_task_prompt_by_technology_stack.")

        # Send prompts one by one and log each response using Responses API
        response = None
        for prompt in task_generation_prompts:
            messages.append({"role": "user", "content": prompt})
            response = openai_client.responses.create(
                model=model,
                input=messages,
                reasoning={"effort": "medium"},
                text={"verbosity": "medium"}
            )
            response_text = getattr(response, "output_text", "NO output_text on response")
            messages.append({"role": "assistant", "content": response_text})
            logger.info("=" * 70)
            logger.info(f" Prompt Response: ")
            logger.info(response_text)
            logger.info("=" * 70)

        # Basic safety checks
        if response is None or not getattr(response, "output_text", None):
            logger.error("No output_text received from OpenAI Responses API")
            raise RuntimeError("Failed to get output_text from OpenAI Responses API")

        # Parse JSON from the final response
        # Try to extract JSON from the response, handling cases where it might be embedded in text or markdown
        task_data = None
        response_text = response.output_text.strip()
        
        try:
            # First, try parsing the response directly as JSON
            task_data = json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code blocks
            logger.warning("Direct JSON parsing failed, attempting to extract JSON from markdown code blocks")
            
            # Look for JSON in markdown code blocks (```json ... ``` or ``` ... ```)
            json_patterns = [
                r'```json\s*(.*?)\s*```',  # JSON in ```json code block
                r'```\s*(\{.*?\})\s*```',  # JSON object in ``` code block
                r'(\{.*\})',  # Any JSON object in the text
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response_text, re.DOTALL)
                for match in matches:
                    try:
                        # Try to parse the matched content
                        extracted_json = match.strip()
                        task_data = json.loads(extracted_json)
                        logger.info("Successfully extracted JSON from markdown code block")
                        break
                    except json.JSONDecodeError:
                        continue
                
                if task_data is not None:
                    break
            
            # If still no JSON found, try to find the largest JSON object in the text
            if task_data is None:
                logger.warning("JSON extraction from code blocks failed, attempting to find JSON object in text")
                # Find all potential JSON objects (starting with { and ending with })
                brace_count = 0
                start_idx = -1
                for i, char in enumerate(response_text):
                    if char == '{':
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            potential_json = response_text[start_idx:i+1]
                            try:
                                task_data = json.loads(potential_json)
                                logger.info("Successfully extracted JSON object from text")
                                break
                            except json.JSONDecodeError:
                                continue
        
        if task_data is None:
            error_msg = f"Failed to parse JSON from response.output_text. Response preview: {response_text[:500]}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        task_data["created_at"] = datetime.now().isoformat()
        
        return task_data
        
    except Exception as e:
        logger.error(f"Error generating task with code: {str(e)}")
        raise

def build_scenario_key(competencies: List[Dict]) -> str:
    """Build the scenario lookup key from competencies list.

    Produces keys like 'Java (BASIC), Kafka (BASIC)' that match
    the key format used in task_scenarios.json files.
    Competencies are sorted alphabetically for consistent key generation.
    """
    formatted = []
    for comp in competencies:
        name = comp.get("name", "").strip()
        proficiency = comp.get("proficiency", "").upper()
        if name and proficiency:
            formatted.append(f"{name} ({proficiency})")
        else:
            logger.warning(f"Skipping malformed competency entry: {comp}. 'name' or 'proficiency' missing.")
    return ", ".join(sorted(formatted))


def save_generated_scenarios(scenarios: List[str], key: str, target_file: Path, append: bool = True):
    """Save scenarios to the target JSON file under the given key.

    Args:
        scenarios: List of scenario strings to save.
        key: The scenario key (e.g. 'Java (BASIC), Kafka (BASIC)').
        target_file: Path to the target scenario JSON file.
        append: If True, merge into existing file; if False, overwrite.
    """
    if append and target_file.exists():
        try:
            existing = read_json_file_robust(target_file)
        except Exception:
            existing = {}
        if key in existing and isinstance(existing[key], list):
            existing[key].extend(scenarios)
        else:
            existing[key] = scenarios
        data = existing
    else:
        data = {key: scenarios}

    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(scenarios)} scenarios to {target_file} under key '{key}'")


def load_relevant_scenarios(competencies: List[Dict], scenarios_file: Path) -> List[str]:
    """
    Load relevant scenarios for given competencies from scenarios file by constructing
    a combined key based on each competency's name and its specific proficiency level.
    The order of competencies in the input list will be normalized for key generation.
    """
    try:
        all_scenarios = read_json_file_robust(scenarios_file)

        if not competencies:
            logger.warning("No competencies provided to load scenarios.")
            return []

        # Use shared key builder
        primary_key = build_scenario_key(competencies)
        if not primary_key:
            logger.warning("No valid competency entries found after formatting.")
            return []

        # Construct possible keys (primary + reversed for 2-competency combos)
        possible_keys = [primary_key]
        parts = [p.strip() for p in primary_key.split(", ")]
        if len(parts) == 2:
            reversed_key = f"{parts[1]}, {parts[0]}"
            if reversed_key != primary_key:
                possible_keys.append(reversed_key)

        logger.info(f"Attempting to find scenarios with possible combined keys: {possible_keys}")

        found_scenarios = []
        for key in possible_keys:
            if key in all_scenarios:
                logger.info(f"Found scenarios for key: {key}")
                found_scenarios.extend(all_scenarios[key])
                break

        if not found_scenarios:
            logger.warning(f"No combined scenarios found for input competencies: {competencies}. Tried keys: {possible_keys}")

        return found_scenarios

    except FileNotFoundError:
        logger.error(f"Scenarios file not found at: {scenarios_file}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from scenarios file: {scenarios_file}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading scenarios: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def get_repo_headers(token: str) -> Dict[str, str]:
    """Get authentication headers for repository access"""
    auth_type = "Bearer" if token.startswith("github_pat_") else "token"
    return {
        "Authorization": f"{auth_type} {token}",
        "Accept": "application/vnd.github.v3+json"
    }


def get_gist_headers(token: str) -> Dict[str, str]:
    """Get authentication headers for Gist creation"""
    auth_type = "Bearer" if token.startswith("github_pat_") else "token"
    return {
        "Authorization": f"{auth_type} {token}",
        "Accept": "application/vnd.github.v3+json"
    }


def parse_github_repo_url(url: str) -> Tuple[str, str]:
    """Parse GitHub repo URL to get owner and repo name"""
    # Handle various formats:
    # https://github.com/owner/repo
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    # owner/repo
    
    if '/' in url and not url.startswith('http') and not url.startswith('git@'):
        # Assume format: owner/repo
        parts = url.split('/')
        if len(parts) == 2:
            return parts[0], parts[1]
    
    # Parse URL
    if url.startswith('git@'):
        # git@github.com:owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', url)
        if match:
            return match.group(1), match.group(2)
    else:
        # https://github.com/owner/repo
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 2:
                return path_parts[0], path_parts[1]
        except Exception as e:
            logger.debug(f"Could not parse URL '{url}' as HTTPS format: {e}")

    
    raise ValueError(f"Could not parse GitHub URL: {url}")


def verify_token(token: str, token_type: str) -> bool:
    """Verify that a token is valid"""
    headers = get_repo_headers(token)
    try:
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"[OK] {token_type} token valid for user: {user_data.get('login', 'Unknown')}")
            return True
        else:
            logger.warning(f"[WARN] {token_type} token validation failed: {response.status_code}")
            try:
                logger.debug(response.json())
            except Exception:
                logger.debug(response.text)
            return False
            return False
    except requests.Timeout:
        logger.error(f"[WARN] Timeout validating {token_type} token: Request timed out after 10 seconds")
        return False
    except requests.RequestException as e:
        logger.error(f"[WARN] Request error validating {token_type} token: {e}")
        return False
    except Exception as e:
        logger.error(f"[WARN] Error validating {token_type} token: {e}")
        return False


def fetch_repo_files(
    owner: str, 
    repo: str, 
    repo_token: str,
    branch: str = "main", 
    max_files: int = 50, 
    max_size_kb: int = 100
) -> Dict[str, str]:
    """Fetch files from a GitHub repository using the repo token"""
    headers = get_repo_headers(repo_token)
    
    logger.info(f"Fetching repository files from {owner}/{repo}...")
    
    # Try main branch first, then master
    branches_to_try = [branch, "main", "master"]
    tree_sha = None
    
    for branch_name in branches_to_try:
        try:
            branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch_name}"
            branch_response = requests.get(branch_url, headers=headers, timeout=10)
            if branch_response.status_code == 200:
                tree_sha = branch_response.json()['commit']['commit']['tree']['sha']
                logger.info(f"   Found branch: {branch_name}")
                break
        except requests.Timeout:
            logger.error(f"   Timeout accessing branch {branch_name}: Request timed out after 10 seconds")
            continue
        except requests.RequestException as e:
            logger.error(f"   Request error accessing branch {branch_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"   Could not access branch {branch_name}: {type(e).__name__}: {e}")
            continue
    
    if not tree_sha:
        raise ValueError(f"Could not find branch. Tried: {', '.join(branches_to_try)}")
    
    # Get tree recursively
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"
    try:
        tree_response = requests.get(tree_url, headers=headers, timeout=10)
        if tree_response.status_code != 200:
            raise ValueError(f"Failed to fetch repo tree: {tree_response.status_code} - {tree_response.text}")
    except requests.Timeout:
        raise ValueError(f"Timeout fetching repo tree: Request timed out after 10 seconds")
    except requests.RequestException as e:
        raise ValueError(f"Request error fetching repo tree: {e}")
    
    tree_data = tree_response.json()
    files = {}
    file_count = 0
    
    # Filter files (skip large files, binary files, etc.)
    for item in tree_data.get('tree', []):
        if item['type'] != 'blob':  # Only files, not directories
            continue
        
        path = item['path']
        size = item.get('size', 0)
        
        # Skip if too large
        if size > max_size_kb * 1024:
            continue
        
        # Skip common non-text files
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', 
                          '.exe', '.dll', '.so', '.dylib', '.bin', '.pyc', '.pyo',
                          '.woff', '.woff2', '.ttf', '.eot', '.svg', '.mp4', '.mp3',
                          '.avi', '.mov', '.wmv', '.flv', '.webm'}
        if any(path.lower().endswith(ext) for ext in skip_extensions):
            continue
        
        # Skip hidden files and common ignore patterns
        if any(part.startswith('.') for part in path.split('/')):
            if '.git' not in path and '.github' not in path:  # Allow .gitignore, .github/workflows
                continue
        
        # Skip node_modules, venv, etc.
        skip_dirs = {'node_modules', 'venv', '__pycache__', '.pytest_cache', 
                    'dist', 'build', '.next', '.nuxt', 'target'}
        if any(skip_dir in path.split('/') for skip_dir in skip_dirs):
            continue
        
        # Fetch file content
        try:
            file_url = item['url']
            file_response = requests.get(file_url, headers=headers, timeout=10)
            if file_response.status_code == 200:
                file_data = file_response.json()
                content = file_data.get('content', '')
                
                # Decode base64 content
                try:
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    files[path] = decoded_content
                    file_count += 1
                    
                    if file_count >= max_files:
                        logger.info(f"   Reached max_files limit ({max_files})")
                        break
                except UnicodeDecodeError:
                    # Skip binary files that can't be decoded
                    continue
        except requests.Timeout:
            logger.warning(f"   Warning: Timeout fetching {path}: Request timed out after 10 seconds")
            continue
        except requests.RequestException as e:
            logger.warning(f"   Warning: Request error fetching {path}: {e}")
            continue
        except Exception as e:
            logger.warning(f"   Warning: Could not fetch {path}: {e}")
            continue
    
    return files


def generate_folder_structure(files: Dict[str, str]) -> str:
    """Generate a visual folder structure tree from file paths"""
    # Build a tree structure
    tree = {}
    
    for path in sorted(files.keys()):
        parts = path.split('/')
        current = tree
        
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {}
            current = current[part]
    
    def build_tree_string(node: dict, prefix: str = "", is_last: bool = True) -> str:
        """Recursively build tree string representation"""
        lines = []
        items = sorted(node.items())
        
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            current_prefix = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{current_prefix}{name}")
            
            if children:
                extension = "    " if is_last_item else "│   "
                child_lines = build_tree_string(children, prefix + extension, is_last_item)
                lines.extend(child_lines)
        
        return lines
    
    tree_lines = build_tree_string(tree)
    return "\n".join(tree_lines)


def create_gist_from_files(
    files: Dict[str, str],
    owner: str,
    repo: str,
    gist_token: str,
    description: Optional[str] = None,
    public: bool = False
) -> Optional[str]:
    """Create a Gist from files using the Gist token"""
    headers = get_gist_headers(gist_token)
    
    logger.info(f"Creating Gist for {owner}/{repo}...")
    
    if not files:
        logger.error("[FAIL] No files to create Gist from")
        return None
    
    # Generate folder structure before filtering
    folder_structure = generate_folder_structure(files)
    structure_content = f"# {repo}\n\n## Folder Structure\n\n```\n{folder_structure}\n```\n"
    
    # Flatten paths for gist (gists don't support nested paths)
    # Convert "src/main.py" to "src_main.py" or keep original if no slashes
    flattened_files = {}
    for path, content in files.items():
        # Skip .gitignore files
        if path == '.gitignore' or path.endswith('/.gitignore'):
            logger.info(f"   Skipping .gitignore file: {path}")
            continue
        
        # Skip empty files
        if not content or not content.strip():
            continue
        
        # Check file size (GitHub Gist limit is ~1MB per file)
        if len(content.encode('utf-8')) > 1024 * 1024:  # 1MB
            logger.warning(f"   Warning: Skipping large file: {path} ({len(content.encode('utf-8'))} bytes)")
            continue
            
        # Replace slashes with underscores, but keep the structure visible
        flat_name = path.replace('/', '_').replace('\\', '_')
        
        # Remove invalid characters for filenames
        flat_name = flat_name.replace('\x00', '').strip()
        
        # Ensure we have a valid filename
        if not flat_name or flat_name == '.' or flat_name == '..':
            flat_name = f"file_{hash(path) % 10000}"
        
        # If name is too long, truncate but keep extension
        if len(flat_name) > 100:
            name_parts = flat_name.rsplit('.', 1)
            if len(name_parts) == 2:
                ext = '.' + name_parts[1]
                flat_name = flat_name[:100-len(ext)] + ext
            else:
                flat_name = flat_name[:100]
        
        flattened_files[flat_name] = {"content": content}
    
    if not flattened_files:
        logger.error("[FAIL] No valid files to create Gist from (all files were empty or filtered)")
        return None
    
    # Add folder structure file as `.<repo_name>.md` as the first file
    # This ensures it appears first and GitHub uses it for the Gist name
    structure_filename = f".{repo}.md"
    final_files = {structure_filename: {"content": structure_content}}
    final_files.update(flattened_files)
    logger.info(f"   Created folder structure file: {structure_filename} (added as first file)")
    
    # Determine the description to use
    gist_description = description if description else repo
    
    payload = {
        "description": gist_description,
        "public": public,
        "files": final_files
    }
    
    try:
        response = requests.post('https://api.github.com/gists', headers=headers, json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            gist_url = data['html_url']
            logger.info(f"[OK] Gist created successfully: {gist_url}")
            return gist_url
        else:
            logger.error(f"[FAIL] FAILED to create Gist. Status Code: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Response: {error_data}")
            except Exception:
                logger.error(f"Response text: {response.text}")
            return None
    except requests.Timeout:
        logger.error("[FAIL] Timeout creating Gist: Request timed out after 10 seconds")
        return None
    except requests.RequestException as e:
        logger.error(f"[FAIL] Request error creating Gist: {e}")
        return None
    except Exception as e:
        logger.error(f"[FAIL] Error creating Gist: {e}")
        return None


def create_gist_from_template(
    repo_url: str,
    repo_token: str,
    gist_token: str,
    max_files: int = 50,
    branch: str = "main",
    description: Optional[str] = None,
    public: bool = False
) -> Optional[str]:
    """
    Convert a GitHub repository template to a Gist.
    
    Args:
        repo_url: GitHub repository URL
        repo_token: Token for accessing the repository
        gist_token: Token for creating the Gist
        max_files: Maximum number of files to include
        branch: Branch to fetch from
        description: Custom description for the Gist
        public: Whether the Gist should be public
    
    Returns:
        Gist URL if successful, None otherwise
    """
    # Verify tokens
    logger.info("Verifying tokens...")
    if not verify_token(repo_token, "REPO"):
        logger.error("[FAIL] REPO_TOKEN is invalid.")
        return None
    
    if not verify_token(gist_token, "GIST"):
        logger.error("[FAIL] GIST_TOKEN is invalid.")
        return None
    
    # Parse repository URL
    try:
        owner, repo = parse_github_repo_url(repo_url)
        logger.info(f"Processing repository: {owner}/{repo}")
    except ValueError as e:
        logger.error(f"[FAIL] Error parsing repository URL: {e}")
        return None
    
    # Fetch repository files
    try:
        files = fetch_repo_files(owner, repo, repo_token, branch=branch, max_files=max_files)
        logger.info(f"Fetched {len(files)} files")
    except Exception as e:
        logger.error(f"[FAIL] Error fetching repository files: {e}", exc_info=True)
        return None
    
    # Create Gist using gist token
    gist_url = create_gist_from_files(files, owner, repo, gist_token, description, public)
    return gist_url
