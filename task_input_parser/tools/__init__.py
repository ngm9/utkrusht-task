"""Tool registry for the LLM agent.

`all_tools()` returns the OpenAI-format function-calling tool list.
`dispatch()` is called by the agent loop when the LLM emits a tool_call.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from task_input_parser.tools.emit import EmitTaskInput, emit_task

try:
    from task_input_parser.tools.image import ProcessImageInput, process_image
    _HAS_IMAGE = True
except Exception:
    _HAS_IMAGE = False

try:
    from task_input_parser.tools.fetch import FetchExternalCodeInput, fetch_external_code
    _HAS_FETCH = True
except Exception:
    _HAS_FETCH = False


def _schema_from_pydantic(model_cls) -> Dict[str, Any]:
    """Convert a Pydantic model class to a JSON Schema dict suitable for OpenAI tool parameters."""
    schema = model_cls.model_json_schema()
    schema.setdefault("type", "object")
    return schema


def all_tools() -> List[Dict[str, Any]]:
    """Responses API flat tool format: {type, name, description, parameters}."""
    tools = [
        {
            "type": "function",
            "name": "emit_task",
            "description": (
                "Write the final per-task markdown to "
                "extract_<timestamp>/task-N-<slug>.md. The leak-check "
                "regex runs BEFORE writing; if any banned code-hosting "
                "domain is present, the call is rejected and the agent "
                "must remove the URL and retry."
            ),
            "parameters": _schema_from_pydantic(EmitTaskInput),
        },
    ]
    if _HAS_IMAGE:
        tools.append({
            "type": "function",
            "name": "process_image",
            "description": (
                "Extract an embedded image from the source document by "
                "its image_ref, upload it to the shared Google Drive "
                "task-resources folder, and return Drive thumbnail + view "
                "URLs plus basic metadata (width, height, content hash). "
                "Does NOT run vision-LLM analysis."
            ),
            "parameters": _schema_from_pydantic(ProcessImageInput),
        })
    if _HAS_FETCH:
        tools.append({
            "type": "function",
            "name": "fetch_external_code",
            "description": (
                "Fetch starter-code files from an external URL "
                "(GitHub Gist in v1). Returns {filename: content} dict "
                "+ platform-detected metadata. Other platforms return a "
                "'platform_not_supported' status which the agent surfaces "
                "as an inline **Note:** in the relevant task's markdown."
            ),
            "parameters": _schema_from_pydantic(FetchExternalCodeInput),
        })
    return tools


def dispatch(name: str, args_json: str, output_dir: Path):
    """Route a tool call by name to its implementation, validating args via Pydantic; raises ValueError for unknown tool names."""
    args = json.loads(args_json) if isinstance(args_json, str) else args_json
    if name == "emit_task":
        return emit_task(EmitTaskInput.model_validate(args), output_dir=output_dir)
    if name == "process_image" and _HAS_IMAGE:
        return process_image(ProcessImageInput.model_validate(args), output_dir=output_dir)
    if name == "fetch_external_code" and _HAS_FETCH:
        return fetch_external_code(FetchExternalCodeInput.model_validate(args), output_dir=output_dir)
    raise ValueError(f"Unknown tool: {name!r}")
