"""``generate_tasks`` Click command.

Extracted verbatim from ``multiagent.py`` during the A1 refactor.
"""
import os
from pathlib import Path

import click

from infra.evals import EvalGateError
from generators.task import create_task, InfraTemplateMissingError
from infra.tracing import (
    new_trace_id,
    trace_run,
    upload_run_traces,
    write_manifest,
)
from infra.utils import read_json_file_robust


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

    # Bound up-front so the tracing `finally` block can never hit an
    # UnboundLocalError if an early-return path is added above it later.
    competency_names: list = []

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

    # Pipeline tracing: run_pipeline passes the run id via TRACE_RUN_ID so the
    # captured traces land under the same .task_agent_runs/run-<id>/ dir. A
    # direct (non-pipeline) invocation gets a fresh id and only traces if
    # PIPELINE_TRACING_ENABLED is set. All tracing is failure-isolated.
    run_id = os.getenv("TRACE_RUN_ID") or new_trace_id()
    # Recorded into the trace manifest so a run's traces are joinable to the task
    # it produced (the LLM-call records carry run_id but task_id=None, since every
    # LLM call happens before the DB insert).
    _trace_result = {"outcome": "unknown", "task_id": None, "task_name": None}
    try:
        print(" STEP 1: Creating Task(s)...")
        print("-" * 50)

        _validate_environment()

        with trace_run(run_id):
            result = create_task(competency_file, background_file, scenarios_file, env)
        _trace_result.update(
            outcome="created",
            task_id=result.get("task_id"),
            task_name=result.get("name"),
        )

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
        _trace_result["outcome"] = "eval_gate_rejected"
        print(" EVAL GATE REJECTED TASK")
        print("=" * 70)
        print(f" Reason: {e}")
        print(" No GitHub repo or Supabase row was created. Inspect the eval")
        print(" feedback in the log, fix the prompt or scope, then retry.")
        print("=" * 70)
    except InfraTemplateMissingError as e:
        _trace_result["outcome"] = "infra_template_missing"
        print(" INFRA TEMPLATE MISSING — TASK GENERATION ABORTED")
        print("=" * 70)
        print(f" Reason: {e}")
        print(" The task was classified as infra but no runtime template exists,")
        print(" so it can't be built/tested/deployed. No GitHub repo or Supabase")
        print(" row was created. Add an E2B template + capability sheet for this")
        print(" service, then retry.")
        print("=" * 70)
    except Exception as e:
        _trace_result["outcome"] = "error"
        print(f" ERROR CREATING TASK!")
        print("=" * 70)
        print(f" Error: {str(e)}")
        print(" Please check your configuration and try again.")
        print("=" * 70)
    finally:
        # Persist the run manifest + (env-gated) upload traces to S3. Both are
        # no-ops unless PIPELINE_TRACING_ENABLED / TRACE_S3_BUCKET are set, and
        # both are failure-isolated — they never affect the task outcome.
        try:
            write_manifest(
                {
                    "run_id": run_id,
                    "env": env,
                    "competencies": competency_names,
                    **_trace_result,
                    "schema_version": 1,
                },
                run_id=run_id,
            )
            upload_run_traces(run_id)
        except Exception:
            pass
