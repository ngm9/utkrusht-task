"""Shim: re-export from non_tech_utils for backwards compatibility."""
from .non_tech_utils import (
    save_task_data_only,
    read_json_file_robust,
    load_relevant_scenarios,
    get_task_prompt_by_technology_stack,
    generate_task_with_code,
    convert_empty_to_none,
    format_pre_requisites,
)
