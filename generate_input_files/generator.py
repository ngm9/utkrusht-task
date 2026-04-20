"""
Core logic for generating competency and background input files from Supabase.

Usage:
    # Single competency
    python -m generate_input_files --name "Java" --proficiency BASIC

    # Multiple competencies combined into one file (comma-separated)
    python -m generate_input_files --name "React, Python, Node.js" --proficiency BASIC

    # Also works with multiple --name flags
    python -m generate_input_files --name "Java" --name "Kafka" --proficiency BASIC

    # With custom folder name
    python -m generate_input_files --name "Java, Kafka" --proficiency INTERMEDIATE --folder-name "input_java_kafka_intermediate_task"

    # Preview without writing
    python -m generate_input_files --name "React" --proficiency BEGINNER --dry-run
"""

import os
import re
import json
from pathlib import Path

import click
import openai
from dotenv import load_dotenv
from supabase import Client, create_client
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

# Load environment variables
load_dotenv()

# Constants
BASE_DIR = Path(__file__).parent.parent / "task_input_files"
MODEL = "gpt-5.4"

PROFICIENCY_YOE_MAP = {
    "BEGINNER": "0+",
    "BASIC": "1-2",
    "INTERMEDIATE": "3-5",
    "ADVANCED": "6+",
}

HARDCODED_ORGANIZATION = {
    "organization_id": "bfbd7da3-a43b-47dc-b828-146733b5c81e",
    "organization_name": "Utkrusht",
    "organization_background": (
        "Utkrusht is a proof-of-skills marketplace that helps agile teams find talent "
        "with strong fundamental concepts with within days. We help aspiring professionals "
        "improve their profile with continuous improvement in their skills, documenting their "
        "journey and helping them fulfill their potential. We primarily build, conduct, proctor "
        "and disseminate proof-of-skill assessments in Technical domains like AI, ML, Fullstack "
        "development, High scale distributed systems, DevOps etc but do help non-tech roles "
        "like Sales, HR, Marketing etc"
    ),
}

COMPETENCY_FIELDS = "competency_id, created_at, proficiency, organization_id, name, scope, long_scope"

# Pricing per million tokens for gpt-5-nano (https://platform.openai.com/docs/pricing)
PRICE_PER_M_INPUT = 0.50    # $0.50 per 1M input tokens
PRICE_PER_M_OUTPUT = 2.00   # $2.00 per 1M output tokens


def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client based on environment."""
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")

    if not url or not key:
        raise click.ClickException(
            f"Missing Supabase credentials for environment: {env}. "
            f"Check your .env file for SUPABASE_URL and SUPABASE_API_KEY variables."
        )

    return create_client(url, key)


def init_openai_client() -> openai.OpenAI:
    """Initialize OpenAI client with Portkey gateway (same setup as multiagent.py)."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")

    if not api_key:
        raise click.ClickException("Missing OPENAI_API_KEY in .env file.")

    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=portkey_key,
        ),
    )


def fetch_competencies_from_db(supabase: Client, name: str, proficiency: str) -> list[dict]:
    """Fetch competency rows from the database matching name and proficiency."""
    result = (
        supabase.table("competencies")
        .select(COMPETENCY_FIELDS)
        .ilike("name", name)
        .eq("proficiency", proficiency)
        .execute()
    )

    if not result.data:
        available = (
            supabase.table("competencies")
            .select("name, proficiency")
            .execute()
        )
        if available.data:
            unique_names = sorted(set(
                f"  - {row['name']} ({row['proficiency']})"
                for row in available.data
            ))
            names_list = "\n".join(unique_names)
            raise click.ClickException(
                f"No competency found for name='{name}', proficiency='{proficiency}'.\n\n"
            )
        else:
            raise click.ClickException(
                f"No competency found for name='{name}', proficiency='{proficiency}'. "
                "The competencies table appears to be empty."
            )

    return result.data


def extract_usage(response) -> dict:
    """Extract token usage from a Responses API response."""
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }
    return {"input_tokens": 0, "output_tokens": 0}


def calculate_cost(total_usage: dict) -> float:
    """Calculate cost in USD from token usage."""
    input_cost = (total_usage["input_tokens"] / 1_000_000) * PRICE_PER_M_INPUT
    output_cost = (total_usage["output_tokens"] / 1_000_000) * PRICE_PER_M_OUTPUT
    return input_cost + output_cost


def generate_role_context(client: openai.OpenAI, scope: str, name: str, proficiency: str, yoe: str) -> tuple[str, dict]:
    """Generate role_context from competency scope using OpenAI Responses API.

    Returns (text, usage_dict).
    """
    prompt = (
        "You are a technical hiring expert. Given a competency scope description, "
        "generate a concise role_context paragraph (3-4 sentences) that describes "
        f"what a software engineer with {yoe} years of experience in {name} is "
        f"expected to do at the {proficiency} level. Focus on their expected "
        "responsibilities, independence level, and technical expectations. "
        "Do NOT use markdown formatting. Return only the paragraph text.\n\n"
        f"Competency scope:\n\n{scope}"
    )

    response = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": prompt}],
        reasoning={"effort": "low"},
    )

    return response.output_text.strip(), extract_usage(response)


def generate_questions_prompt(client: openai.OpenAI, long_scope: str, name: str, proficiency: str, yoe: str) -> tuple[str, dict]:
    """Generate questions_prompt from competency scope using OpenAI Responses API.

    Returns (text, usage_dict).
    """
    GENEARTE_QUESTIONS_PROMPT = f"""
    You are a technical assessment designer with 15 years of experience in designing technical assessments. The assessments generated from the prompts you generate are like bar raiser questions.
    They allow the candidate to solve / fix / build / review a real work item in a real scenario. Given a competency scope description, you take into account the 
    proficiency, the years of experience related to that proficiency to design the difficulty level of the task. 
    
    The prompts you generate will include technical, conceptual ideas required in a task. But they are also not prompts that encourage generating trick questions or configuration or semantics 
    related questions. Your prompt you will generate, always asks to generate logical or functional or other types of scenarios.

    INSTRUCTIONS:
    1. Start with "Please ensure the questions you ask cover" followed by key areas
    2. Include all sections from the long_scope that are not related to testing or configuration or semantics
    3. The question prompt includes lines to specify that BASIC proficiency task scenarios give the candidate only 15-20 minutes to solve the task, INTERMEDIATE proficiency task scenarios give 
    the candidate only 25-30 mins to solve the task
    4. End with a summary sentence starting with "The goal is to evaluate..." and add ideas of what the requirements for the tasks should be
    5. Use \\n for newlines within the output. Return only the prompt text.
    
    INPUT:
    Match the proficiency level: {proficiency} ({yoe} years experience) for {name}.
    Competency Long Scope:\n\n
    {long_scope}

    """

    response = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": GENEARTE_QUESTIONS_PROMPT}],
        reasoning={"effort": "low"},
    )

    return response.output_text.strip(), extract_usage(response)


def sanitize_folder_name(competency_name: str) -> str:
    """Convert a competency name into a folder-friendly slug prefixed with 'input_'.

    Examples:
        "Java" -> "input_java"
        "Java - Kafka" -> "input_java_kafka"
        "Node.js - MongoDB" -> "input_nodejs_mongodb"
        "Python - FastAPI" -> "input_python_fastapi"
        "React" -> "input_react"
    """
    name = competency_name.lower()
    # Remove .js suffix (e.g., Node.js -> Node)
    name = re.sub(r"\.js\b", "js", name)
    # Replace separators with underscore
    name = re.sub(r"\s*[-/&]\s*", "_", name)
    # Replace remaining spaces and dots with underscore
    name = re.sub(r"[\s.]+", "_", name)
    # Remove any non-alphanumeric characters except underscore
    name = re.sub(r"[^a-z0-9_]", "", name)
    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name)
    # Strip leading/trailing underscores
    name = name.strip("_")

    if not name.startswith("input_"):
        name = f"input_{name}"

    return name


def resolve_output_folder(tech_slug: str, level: str, folder_name: str | None = None) -> Path:
    """Build the full output directory path.

    Structure: task_input_files/{tech_slug}/{level}/{variant_subfolder}/
    """
    tech_short = tech_slug.replace("input_", "", 1)

    if folder_name:
        variant = folder_name
    else:
        variant = f"input_{tech_short}_{level}_task"

    output_dir = BASE_DIR / tech_slug / level / variant
    return output_dir


def write_json_safe(file_path: Path, data, force: bool = False) -> bool:
    """Write JSON data to file with overwrite protection.

    Returns True if file was written, False if skipped.
    """
    if file_path.exists() and not force:
        click.echo(f"  WARNING: File already exists, skipping: {file_path}")
        click.echo("  Use --force to overwrite.")
        return False

    if file_path.exists() and force:
        click.echo(f"  Overwriting existing file: {file_path}")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    click.echo(f"  Created: {file_path}")
    return True


@click.command()
@click.option(
    "--name", "-n", required=True, multiple=True,
    help='Competency name(s) to search for. Use comma-separated or multiple flags: --name "Java, Kafka"',
)
@click.option(
    "--proficiency", "-p", required=True,
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"], case_sensitive=False),
    help="Proficiency level",
)
@click.option("--folder-name", "-f", default=None, help="Override the auto-generated task subfolder name")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files if they exist")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be created without writing files")
@click.option(
    "--env", default="prod",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: prod)",
)
def generate_input_files(name, proficiency, folder_name, force, dry_run, env):
    """Generate competency and background input files from the Supabase competency table.

    For multiple competencies in one combined file, use comma-separated names:

    \b
        python -m generate_input_files --name "Java, Kafka" --proficiency BASIC

    Or use --name multiple times:

    \b
        python -m generate_input_files --name "Java" --name "Kafka" --proficiency BASIC
    """
    # Support both comma-separated and multiple --name flags
    raw_names = list(name)
    names = []
    for n in raw_names:
        parts = [part.strip() for part in n.split(",") if part.strip()]
        names.extend(parts)

    proficiency_upper = proficiency.upper()
    names_display = " + ".join(f"'{n}'" for n in names)
    click.echo(f"\nSearching for competencies: {names_display} at {proficiency_upper} level (env: {env})")

    # 1. Init clients
    supabase = init_supabase(env)
    click.echo("Connected to Supabase.")

    # 2. Fetch competencies from DB (one query per name, combined into one array)
    competency_data = []
    for comp_name in names:
        rows = fetch_competencies_from_db(supabase, comp_name, proficiency_upper)
        click.echo(f"  Found {len(rows)} row(s) for '{comp_name}'.")
        for c in rows:
            competency_data.append({
                "competency_id": c["competency_id"],
                "created_at": c["created_at"],
                "proficiency": c["proficiency"],
                "organization_id": c["organization_id"],
                "name": c["name"],
                "scope": c["scope"],
                "long_scope": c["long_scope"]
            })

    click.echo(f"Total: {len(competency_data)} competency row(s) combined.")

    # 3. Derive yoe from proficiency
    yoe = PROFICIENCY_YOE_MAP.get(proficiency_upper, "1-2")

    # 4. Generate background fields via OpenAI
    all_names = [c["name"] for c in competency_data]
    combined_name = " & ".join(all_names)
    combined_scope = "\n\n---\n\n".join(
        f"[{c['name']}]\n{c['long_scope']}" for c in competency_data
    )

    click.echo("Generating role_context and questions_prompt via LLM...")
    openai_client = init_openai_client()
    total_usage = {"input_tokens": 0, "output_tokens": 0}

    try:
        role_context, usage = generate_role_context(openai_client, combined_scope, combined_name, proficiency_upper, yoe)
        total_usage["input_tokens"] += usage["input_tokens"]
        total_usage["output_tokens"] += usage["output_tokens"]
        click.echo("  role_context generated.")
    except Exception as e:
        click.echo(f"  WARNING: Failed to generate role_context: {e}")
        click.echo("  Using fallback role_context.")
        role_context = (
            f"A software engineer with {yoe} years of experience in {combined_name} "
            f"is expected to work at the {proficiency_upper} proficiency level."
        )

    try:
        questions_prompt, usage = generate_questions_prompt(openai_client, combined_scope, combined_name, proficiency_upper, yoe)
        total_usage["input_tokens"] += usage["input_tokens"]
        total_usage["output_tokens"] += usage["output_tokens"]
        click.echo("  questions_prompt generated.")
    except Exception as e:
        click.echo(f"  WARNING: Failed to generate questions_prompt: {e}")
        click.echo("  Using fallback questions_prompt.")
        questions_prompt = (
            f"Please ensure the questions cover the key areas of {combined_name} "
            f"at the {proficiency_upper} level as described in the competency scope."
        )

    # Display LLM cost summary
    total_cost = calculate_cost(total_usage)
    click.echo(f"\n  LLM Usage: {total_usage['input_tokens']} input + {total_usage['output_tokens']} output tokens")
    click.echo(f"  LLM Cost:  ${total_cost:.6f}")

    # 5. Build background JSON
    background_data = {
        "organization": HARDCODED_ORGANIZATION,
        "role_context": role_context,
        "questions_prompt": questions_prompt,
        "yoe": yoe,
    }

    # 6. Resolve folder paths
    combined_slug_name = "_".join(n.lower() for n in names)
    tech_slug = sanitize_folder_name(combined_slug_name)
    level = proficiency_upper.lower()
    output_dir = resolve_output_folder(tech_slug, level, folder_name)

    tech_short = tech_slug.replace("input_", "", 1)
    comp_filename = f"competency_{tech_short}_{level}_Utkrusht.json"
    bg_filename = f"background_forQuestions_utkrusht_{tech_short}_{level}.json"

    comp_path = output_dir / comp_filename
    bg_path = output_dir / bg_filename

    # 7. Output
    click.echo(f"\nOutput directory: {output_dir}")
    click.echo(f"  Competency file: {comp_filename}")
    click.echo(f"  Background file: {bg_filename}")

    if dry_run:
        click.echo("\n--- DRY RUN (no files written) ---")
        click.echo(f"\nCompetency JSON preview:")
        click.echo(json.dumps(competency_data, indent=2, ensure_ascii=False)[:1000])
        click.echo(f"\nBackground JSON preview:")
        click.echo(json.dumps(background_data, indent=2, ensure_ascii=False)[:1000])
        return

    # Create directories
    os.makedirs(output_dir, exist_ok=True)

    # Write files
    click.echo("\nWriting files...")
    comp_written = write_json_safe(comp_path, competency_data, force)
    bg_written = write_json_safe(bg_path, background_data, force)

    if comp_written or bg_written:
        click.echo(f"\nDone! Files created in: {output_dir}")
    else:
        click.echo("\nNo files were written (all already exist). Use --force to overwrite.")
