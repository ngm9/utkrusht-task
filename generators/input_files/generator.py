"""
Core logic for generating competency and background input files from Supabase.

Usage:
    # Single competency
    python -m generate_input_files --competency-name "Java" --proficiency BASIC --role "Software Engineer"

    # Multiple competencies combined into one file (comma-separated)
    python -m generate_input_files --competency-name "React, Python, Node.js" --proficiency BASIC --role "Frontend Engineer"

    # Also works with multiple --competency-name flags
    python -m generate_input_files --competency-name "Java" --competency-name "Kafka" --proficiency BASIC --role "Backend Engineer"

    # Role from a file
    python -m generate_input_files --competency-name "AI Evals for Product Managers" --proficiency BASIC --role path/to/role_description.txt

    # With custom folder name
    python -m generate_input_files --competency-name "Java, Kafka" --proficiency INTERMEDIATE --role "Backend Engineer" --folder-name "input_java_kafka_intermediate_task"

    # Preview without writing
    python -m generate_input_files --competency-name "React" --proficiency BEGINNER --role "Frontend Engineer" --dry-run
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

from infra.tracing.client import trace_client

# Load environment variables
load_dotenv()

# Constants
BASE_DIR = Path(__file__).parent.parent.parent / "data" / "generated" / "input_files"
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

# Default candidate time budget (the {minutes_range} prompt placeholder), per
# proficiency. Written into the background input file so a user can EDIT it to
# influence the generated task's time scope. The task generator reads it back in
# infra/utils.get_task_prompt_by_technology_stack — keep these values in sync
# with the fallback map there.
_MINUTES_RANGE_BY_PROFICIENCY = {
    "BASIC": "15-20",
    "INTERMEDIATE": "20-25",
    "ADVANCED": "25-30",
}

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

    return trace_client(
        openai.OpenAI(
            api_key=api_key,
            base_url=PORTKEY_GATEWAY_URL,
            default_headers=createHeaders(
                provider="openai",
                api_key=portkey_key,
            ),
        ),
        provider="openai",
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


def load_role_description(role: str | None) -> str | None:
    """Resolve --role value: read from file if a valid path, otherwise return as-is."""
    if not role:
        return None
    role_path = Path(role)
    if role_path.exists() and role_path.is_file():
        return role_path.read_text(encoding="utf-8").strip()
    return role.strip()


def generate_role_context(
    client: openai.OpenAI,
    scope: str,
    name: str,
    proficiency: str,
    yoe: str,
    role_description: str | None,
) -> tuple[str, dict]:
    """Generate role_context from competency scope using OpenAI Responses API.

    Returns (text, usage_dict).
    """
    role_line = f"Role: {role_description}" if role_description else f"Competency: {name}"

    prompt = f"""
You are a hiring expert with 15 years of experience writing role expectations for technical and non-technical assessments.

Given a competency scope and role context, generate a role_context paragraph (3-4 sentences) that describes
what a {role_description or name} with {yoe} years of experience is expected to do at the {proficiency} proficiency level.

The paragraph must:
- Describe the candidate's expected day-to-day responsibilities at this proficiency level
- Reflect their degree of independence and the complexity of work they own vs. work guided by seniors
- Capture the technical or functional depth and judgment expected, grounded in the competency scope
- Be specific to the role — avoid generic filler like "works collaboratively" or "contributes to the team"

Do NOT use markdown formatting. Return only the paragraph text.

INPUT:
{role_line}
Proficiency: {proficiency} ({yoe} years experience)
Competency scope:

{scope}
"""

    response = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": prompt}],
        reasoning={"effort": "low"},
    )

    return response.output_text.strip(), extract_usage(response)


def generate_organization(client: openai.OpenAI, domain: str) -> tuple[dict, dict]:
    """Generate a fictional company background for a business domain.

    Returns (organization_dict, usage_dict). The ``organization_id`` is kept
    stable (the platform org) because downstream consumers may treat it as an
    FK — only the company name and narrative background reflect the domain.
    """
    prompt = f"""You are writing the company background for a realistic coding-assessment task.

Invent a plausible fictional company that operates squarely in the "{domain}" business domain, and write its background.

Return STRICT JSON only — no markdown, no commentary — with exactly these two keys:
{{"organization_name": "<short company name>", "organization_background": "<2-3 sentences: what the company does, its product, and rough scale>"}}

The background must read like a real company a candidate could be hired into — concrete product, customers, scale. Do NOT mention assessments, hiring, or proof-of-skills.
"""

    response = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": prompt}],
        reasoning={"effort": "low"},
    )

    raw = response.output_text.strip()
    # The model is asked for bare JSON; strip a stray markdown fence defensively.
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    parsed = json.loads(match.group(0) if match else raw)

    organization = {
        "organization_id": HARDCODED_ORGANIZATION["organization_id"],
        "organization_name": parsed["organization_name"],
        "organization_background": parsed["organization_background"],
    }
    return organization, extract_usage(response)


def generate_questions_prompt(client: openai.OpenAI, long_scope: str, name: str, proficiency: str, yoe: str) -> tuple[str, dict]:
    """Generate questions_prompt from competency scope using OpenAI Responses API.

    Returns (text, usage_dict).
    """
    TIMING_AND_COMPLEXITY_INSTRUCTIONS = {
        "BEGINNER": (
            "This is a beginner proficiency, so the tasks need to be simple and not multi-step or complicated. "
            "Let the candidate be able to finish this within 10 to 15 minutes."
        ),
        "BASIC": (
            "This is a basic proficiency, so the tasks need to match one year of experience only. "
            "Somebody with one year of experience does not have extensive production experience and their concepts are usually shaky, "
            "so the complexity of the task needs to be basic only. "
            "Let the candidate be able to finish this within 15 minutes."
        ),
        "INTERMEDIATE": (
            "This is an intermediate proficiency, so somebody attempting this task has a few years of experience but is not an expert in these domains. "
            "Ensure that tasks are around fundamentals, and candidates should be able to finish this within 20 minutes. "
            "Let there be multiple ways to achieve the correct outcome — the idea is to see what paths the candidate picks. "
            "Make the tasks subjective yet specific and clear in their expected outcomes."
        ),
    }
    timing_instruction = TIMING_AND_COMPLEXITY_INSTRUCTIONS.get(proficiency, TIMING_AND_COMPLEXITY_INSTRUCTIONS["BASIC"])

    GENEARTE_QUESTIONS_PROMPT = f"""
You are a technical assessment designer with 15 years of experience designing bar-raiser style technical assessments.
The assessments generated from the prompts you produce require candidates to solve / fix / build / review a real work item in a real scenario.
You calibrate difficulty using the proficiency level and years of experience provided.

The prompts you generate surface technical and conceptual depth, but never encourage trick questions, configuration look-ups, or pure syntax/semantics questions.
Your prompts always ask for logical, functional, architectural, or problem-solving scenarios.

INSTRUCTIONS:
1. Start with "Please ensure the questions you ask cover the key functional, logical, architectural, implementation, debugging, optimization, review, and problem-solving areas from the competency scope for {{name}}, matched to {{proficiency}} proficiency ({{yoe}} years experience)."
2. Read the competency long scope provided below. Extract and list only the topic areas and sub-skills that are NOT about testing frameworks, test configuration, tool installation/setup, language/library syntax, or pure semantics. Embed these specific extracted items directly and explicitly in the output prompt — do NOT use a {{long_scope}} placeholder in your output.
3. Include this line exactly: "{timing_instruction}"
4. Include guidance that tasks should prefer scenarios assessing: understanding of requirements and constraints, reasoning about ambiguous real-world situations, quality of technical decisions and tradeoff analysis, identifying root causes / risks / edge cases, proposing or implementing pragmatic solutions, and reviewing/improving existing work.
5. End with a summary sentence starting with "The goal is to evaluate applied competence, practical problem-solving, implementation and review ability, sound technical judgment, and the candidate's ability to deliver realistic solutions within the expected time constraints for their proficiency level."
6. Use \\n for newlines. Return only the prompt text.
7. In the output, use {{name}}, {{proficiency}}, {{yoe}} as template placeholders (literal curly braces) — these will be filled in at task generation time.

INPUT:
Competency: {name}
Proficiency: {proficiency} ({yoe} years experience)
Competency Long Scope:

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
    "--competency-name", "-n", required=True, multiple=True,
    help='Competency name(s) to search for. Use comma-separated or multiple flags: --competency-name "Java, Kafka"',
)
@click.option(
    "--proficiency", "-p", required=True,
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"], case_sensitive=False),
    help="Proficiency level",
)
@click.option(
    "--role", "-r", default=None,
    help="Role title or description for this assessment — a short string (e.g. 'Product Manager') or a path to a text file with a longer description.",
)
@click.option(
    "--domain", default=None,
    help="Business domain to set the task in (e.g. 'e-commerce', 'healthcare'). When given, the organization background is generated for this domain instead of the default.",
)
@click.option("--folder-name", "-f", default=None, help="Override the auto-generated task subfolder name")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files if they exist")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be created without writing files")
@click.option(
    "--env", default="prod",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: prod)",
)
def generate_input_files(competency_name, proficiency, role, domain, folder_name, force, dry_run, env):
    """Generate competency and background input files from the Supabase competency table.

    For multiple competencies in one combined file, use comma-separated names:

    \b
        python -m generate_input_files --competency-name "Java, Kafka" --proficiency BASIC --role "Backend Engineer"

    Or use --competency-name multiple times:

    \b
        python -m generate_input_files --competency-name "Java" --competency-name "Kafka" --proficiency BASIC --role "Backend Engineer"
    """
    # Support both comma-separated and multiple --competency-name flags
    raw_names = list(competency_name)
    names = []
    for n in raw_names:
        parts = [part.strip() for part in n.split(",") if part.strip()]
        names.extend(parts)

    proficiency_upper = proficiency.upper()
    names_display = " + ".join(f"'{n}'" for n in names)
    click.echo(f"\nSearching for competencies: {names_display} at {proficiency_upper} level (env: {env})")

    role_description = load_role_description(role)
    if role_description:
        click.echo(f"Role: {role_description[:80]}{'...' if len(role_description) > 80 else ''}")

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
        role_context, usage = generate_role_context(openai_client, combined_scope, combined_name, proficiency_upper, yoe, role_description)
        total_usage["input_tokens"] += usage["input_tokens"]
        total_usage["output_tokens"] += usage["output_tokens"]
        click.echo("  role_context generated.")
    except Exception as e:
        click.echo(f"  WARNING: Failed to generate role_context: {e}")
        click.echo("  Using fallback role_context.")
        role_label = role_description or combined_name
        role_context = (
            f"A {role_label} with {yoe} years of experience in {combined_name} "
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

    # 4b. Generate a domain-specific organization when a domain was supplied.
    #     Without a domain, fall back to the default platform organization so
    #     existing CLI callers (no --domain) are unaffected.
    organization = HARDCODED_ORGANIZATION
    if domain:
        click.echo(f"Generating organization background for domain: {domain}")
        try:
            organization, org_usage = generate_organization(openai_client, domain)
            total_usage["input_tokens"] += org_usage["input_tokens"]
            total_usage["output_tokens"] += org_usage["output_tokens"]
            click.echo(f"  organization generated: {organization['organization_name']}")
        except Exception as e:
            click.echo(f"  WARNING: Failed to generate domain organization: {e}")
            click.echo("  Using the default organization.")
            organization = HARDCODED_ORGANIZATION

    # Display LLM cost summary
    total_cost = calculate_cost(total_usage)
    click.echo(f"\n  LLM Usage: {total_usage['input_tokens']} input + {total_usage['output_tokens']} output tokens")
    click.echo(f"  LLM Cost:  ${total_cost:.6f}")

    # 5. Build background JSON
    background_data = {
        "organization": organization,
        "role_context": role_context,
        "questions_prompt": questions_prompt,
        "yoe": yoe,
        # Candidate time budget — EDIT this to influence the generated task's
        # time scope. Defaulted by proficiency (BASIC 15-20 / INTERMEDIATE
        # 20-25 / ADVANCED 25-30).
        "minutes_range": _MINUTES_RANGE_BY_PROFICIENCY.get(proficiency_upper, "15-20"),
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
