"""
Generate competency and background input files from the Supabase competency table.

Usage as CLI:
    python -m generators.input_files --name "Java" --proficiency BASIC

Usage as module:
    from generators.input_files import generate_input_files
"""

from generators.input_files.generator import (
    generate_input_files,
    fetch_competencies_from_db,
    init_supabase,
    init_openai_client,
    sanitize_folder_name,
    resolve_output_folder,
)

__all__ = [
    "generate_input_files",
    "fetch_competencies_from_db",
    "init_supabase",
    "init_openai_client",
    "sanitize_folder_name",
    "resolve_output_folder",
]
