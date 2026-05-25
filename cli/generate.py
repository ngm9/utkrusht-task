"""``generate_tasks`` Click command.

Extracted verbatim from ``multiagent.py`` during the A1 refactor.
"""
from pathlib import Path

import click

from evals import EvalGateError
from task_generation import create_task
from utils import read_json_file_robust


def _validate_environment() -> None:
    """Validate that all required environment variables are set."""
    import os

    required_vars = [
        'OPENAI_API_KEY',
        'PORTKEY_API_KEY',
        'GITHUB_UTKRUSHTAPPS_TOKEN',
        'REPO_OWNER',
        'SUPABASE_URL_APTITUDETESTSDEV',
        'SUPABASE_API_KEY_APTITUDETESTSDEV'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise OSError(
            "Missing required environment variables: " + ", ".join(missing_vars)
        )


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
@click.option('--env', type=click.Choice(['dev', 'prod']), default='dev',
              help='Supabase environment to store the generated task in (default: dev).')
def generate_tasks(competency_file: Path, background_file: Path, scenarios_file: Path, env: str):
    """
    Generate intelligent assessment tasks OR deploy existing tasks to droplets.

    DEFAULT MODE: Automatically detects single vs multi-competency and generates appropriate tasks.

    DEPLOYMENT MODE: Use --deploy-existing with a competency_id to deploy ALL existing undeployed tasks.
    """
    print(" INTELLIGENT TASK GENERATION AGENT")
    print(f" Storage environment: {env}")

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
        print(" STEP 1: Creating Task(s)...")
        print("-" * 50)

        _validate_environment()

        result = create_task(competency_file, background_file, scenarios_file, env)

        task_type = result.get("task_type", "unknown")
        # task_type is a Postgres text[] (e.g. ['BUILD']) — normalize before
        # any string operations so the success banner doesn't crash post-commit.
        if isinstance(task_type, list):
            task_type_display = ", ".join(task_type) if task_type else "unknown"
        else:
            task_type_display = str(task_type)
        competencies_covered = result.get("competencies_covered", [])

        print(f" Task Creation Successful!")
        print(f" Task Type: {task_type_display.replace('_', ' ').title()}")
        print(f" Task ID: {result.get('task_id')}")
        print(f" Task Name: {result.get('name', 'N/A')}")
        print(f" Competencies Covered: {', '.join(competencies_covered)}")
        print(f" GitHub Repository: {result.get('resources', {}).get('github_repo', 'N/A')}")
        print()

        print(" TASK CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f" Task Type: {task_type_display.replace('_', ' ').title()}")
        print(f" Competencies: {', '.join(competencies_covered)}")
        print(f" Repository: {result.get('resources', {}).get('github_repo')}")
        print()

    except EvalGateError as e:
        print(" EVAL GATE REJECTED TASK")
        print("=" * 70)
        print(f" Reason: {e}")
        print(" No GitHub repo or Supabase row was created. Inspect the eval")
        print(" feedback in the log, fix the prompt or scope, then retry.")
        print("=" * 70)
    except Exception as e:
        print(f" ERROR CREATING TASK!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check your configuration and try again.")
        print("=" * 70)
