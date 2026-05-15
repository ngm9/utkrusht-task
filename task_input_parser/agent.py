"""LLM agent loop — orchestrates the per-brief extraction.

Uses gpt-5.4-mini via the OpenAI Responses API with reasoning effort=medium.
The Responses API is recommended over Chat Completions for reasoning models —
it preserves reasoning items across turns automatically when you append
response.output to the input list, giving better multi-turn coherence.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import httpx
import openai
from dotenv import load_dotenv
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from logger_config import logger
from task_input_parser.brief_parser import BriefAST
from task_input_parser.tools import all_tools, dispatch
from task_input_parser.tools.emit import LeakDetectedError

load_dotenv()

MODEL = os.getenv("PARSER_MODEL", "gpt-5.4-mini")
MAX_TOOL_TURNS = 30


@dataclass
class RunSummary:
    emitted_tasks: List[str] = field(default_factory=list)
    inline_notes: int = 0
    aborted: bool = False
    abort_reason: str = ""


def _init_client() -> openai.OpenAI:
    """Build an OpenAI client routed through the Portkey gateway using OPENAI_API_KEY and PORTKEY_API_KEY."""
    return openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY"),
        ),
        timeout=httpx.Timeout(None),
    )


def _format_ast_as_user_message(ast: BriefAST) -> str:
    """Render a BriefAST into a flat markdown string the LLM can read as the first user message."""
    parts = [
        f"# Parsed brief: {Path(ast.source_path).name}",
        f"(format: {ast.source_format}, source_hash: {ast.source_hash[:12]})",
        "",
    ]
    for section in ast.sections:
        heading = section.heading or "(no heading)"
        parts.append(f"## Section {section.index} (h{section.level}): {heading}")
        for para in section.paragraphs:
            parts.append(para)
        parts.append("")

    if ast.tables:
        parts.append("## Tables")
        for ti, t in enumerate(ast.tables):
            parts.append(f"### Table {ti} (section {t.section_index})")
            parts.append("| " + " | ".join(t.headers) + " |")
            parts.append("|" + "|".join("---" for _ in t.headers) + "|")
            for row in t.rows:
                parts.append("| " + " | ".join(row) + " |")
            parts.append("")

    if ast.embedded_images:
        parts.append("## Embedded images")
        for img in ast.embedded_images:
            parts.append(
                f"- image_ref={img.image_ref}, extension={img.extension}, "
                f"size_bytes={img.size_bytes}, hash={img.content_hash[:12]}"
            )
        parts.append("")

    if ast.external_links:
        parts.append("## External links (scrape candidates)")
        for link in ast.external_links:
            parts.append(f"- {link.url}" + (f"  ({link.anchor_text})" if link.anchor_text else ""))
        parts.append("")

    if ast.code_fences:
        parts.append("## Inline code fences (already in the brief, not scraped)")
        for cf in ast.code_fences:
            parts.append(f"### Section {cf.section_index} ({cf.language or 'no-lang'})")
            parts.append("```")
            parts.append(cf.content)
            parts.append("```")

    return "\n".join(parts)


def run(ast: BriefAST, output_dir: Path) -> RunSummary:
    """Run the agent loop against the parsed brief. Returns a RunSummary."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = RunSummary()
    client = _init_client()
    system_prompt = (Path(__file__).parent / "prompts" / "system.md").read_text(encoding="utf-8")

    # Responses API uses `input` list — system message + user message to start.
    # response.output is appended each turn so reasoning items are preserved.
    input_list: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": _format_ast_as_user_message(ast)},
    ]
    tools = all_tools()

    for turn in range(MAX_TOOL_TURNS):
        logger.info(f"[parser.agent] turn {turn + 1}/{MAX_TOOL_TURNS}")

        try:
            resp = client.responses.create(
                model=MODEL,
                input=input_list,
                tools=tools,
                reasoning={"effort": "medium"},
            )
        except Exception as e:
            summary.aborted = True
            summary.abort_reason = f"LLM call failed: {e}"
            logger.error(summary.abort_reason)
            break

        # Append full output (includes reasoning items + function_call items).
        input_list += resp.output

        # Collect function_call items from this response.
        tool_call_items = [item for item in resp.output if item.type == "function_call"]

        if not tool_call_items:
            break  # agent finished — no more tool calls

        # Execute each tool and append results to input_list.
        for item in tool_call_items:
            try:
                result = dispatch(item.name, item.arguments, output_dir)
                if item.name == "emit_task":
                    summary.emitted_tasks.append(result.written_to)
                    summary.inline_notes += getattr(result, "inline_note_count", 0)
                output_str = (
                    result.model_dump_json() if hasattr(result, "model_dump_json") else json.dumps(result)
                )
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": output_str,
                })
            except LeakDetectedError as e:
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "error_type": "LeakDetectedError",
                        "message": str(e),
                        "matched_domains": e.matched_domains,
                    }),
                })
                logger.warning(f"[parser.agent] leak detected on emit_task: {e.matched_domains}")
            except Exception as e:
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({"error_type": type(e).__name__, "message": str(e)}),
                })
                logger.warning(f"[parser.agent] tool {item.name} raised {type(e).__name__}: {e}")

    else:
        summary.aborted = True
        summary.abort_reason = f"Agent did not terminate within {MAX_TOOL_TURNS} tool turns"
        logger.error(summary.abort_reason)

    return summary
