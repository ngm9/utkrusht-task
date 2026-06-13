"""
CLI entry point for the input-files generator.

Usage:
    python -m generators.input_files --name "Java" --proficiency BASIC
    python -m generators.input_files --name "Java, Kafka" --proficiency BASIC --dry-run
"""

from generators.input_files.generator import generate_input_files

if __name__ == "__main__":
    import os

    from infra.tracing import trace_run, trace_stage

    # Capture this stage's LLM calls under the pipeline run (TRACE_RUN_ID set by
    # run_pipeline). No-op unless PIPELINE_TRACING_ENABLED.
    with trace_run(os.getenv("TRACE_RUN_ID")), trace_stage("input_files"):
        generate_input_files()
