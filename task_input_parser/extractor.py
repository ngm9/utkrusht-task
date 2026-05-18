"""Task extractor — converts a BriefAST into one markdown file per task.

The pipeline runs in four steps, all orchestrated by run():
  1. _prefetch_links()   — calls fetch_external_code() directly for every URL in the
                           AST so the fetched code is ready before the LLM is called.
  2. _prefetch_images()  — calls process_image() directly for every embedded image so
                           Drive URLs are ready before the LLM is called.
  3. Single LLM call     — _build_user_message() assembles AST + fetched content into
                           one prompt; the LLM returns structured JSON:
                           {tasks: [{slug, markdown_content}]}.
  4. Post-process        — strips protected domain URLs from each task's markdown,
                           then calls emit_task() directly to write task-N-slug.md.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import httpx
import openai
from dotenv import load_dotenv
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from logger_config import logger
from task_input_parser.brief_parser import BriefAST
from task_input_parser.tools.emit import EmitTaskInput, LeakDetectedError, emit_task
from task_input_parser.tools.fetch import (
    FetchExternalCodeInput,
    FetchExternalCodeOutput,
    fetch_external_code,
)

load_dotenv()

MODEL = os.getenv("PARSER_MODEL", "gpt-5.4-mini")

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slug":             {"type": "string"},
                    "markdown_content": {"type": "string"},
                },
                "required": ["slug", "markdown_content"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["tasks"],
    "additionalProperties": False,
}

# Strips both full URLs (https://gist.github.com/...) and bare domain mentions
# (gist.github.com) so protected sources never appear in candidate-facing markdown.
_PROTECTED_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:"
    r"codepen\.io|codesandbox\.io|jsfiddle\.net|gist\.github\.com"
    r"|pastebin\.com|replit\.com|gitlab\.com/snippets"
    r")[^\s\)\"\']*",
    re.IGNORECASE,
)
_PROTECTED_BARE_RE = re.compile(
    r"(?:codepen\.io|codesandbox\.io|jsfiddle\.net|gist\.github\.com"
    r"|pastebin\.com|replit\.com|gitlab\.com/snippets)[^\s\)\"\']*",
    re.IGNORECASE,
)


@dataclass
class RunSummary:
    emitted_tasks: List[str] = field(default_factory=list)
    inline_notes: int = 0
    aborted: bool = False
    abort_reason: str = ""


def _init_client() -> openai.OpenAI:
    """Build the OpenAI client routed through the Portkey gateway."""
    return openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY"),
        ),
        timeout=httpx.Timeout(None),
    )


def _prefetch_links(ast: BriefAST, output_dir: Path) -> Dict[str, FetchExternalCodeOutput]:
    """Call fetch_external_code() for every URL in the AST before the LLM call.

    Returns a url → FetchExternalCodeOutput mapping so _build_user_message()
    can embed the fetched file contents directly in the prompt.
    """
    results: Dict[str, FetchExternalCodeOutput] = {}
    for link in ast.external_links:
        logger.info(f"[parser] pre-fetching {link.url}")
        try:
            result = fetch_external_code(
                FetchExternalCodeInput(url=link.url), output_dir=output_dir
            )
            results[link.url] = result
            logger.info(f"[parser]   -> status={result.status}")
        except Exception as e:
            logger.warning(f"[parser] fetch failed for {link.url}: {e}")
    return results


def _prefetch_images(ast: BriefAST, output_dir: Path) -> dict:
    """Call process_image() for every embedded image in the AST before the LLM call.

    Returns an image_ref → ProcessImageOutput mapping so _build_user_message()
    can embed the Drive thumbnail and full-res URLs directly in the prompt.
    Returns {} if the image tool is unavailable (missing Google credentials, etc.).
    """
    try:
        from task_input_parser.tools.image import ProcessImageInput, process_image
    except Exception:
        return {}

    results = {}
    for img in ast.embedded_images:
        logger.info(f"[parser] uploading image {img.image_ref}")
        try:
            result = process_image(
                ProcessImageInput(image_ref=img.image_ref), output_dir=output_dir
            )
            results[img.image_ref] = result
            logger.info(f"[parser]   -> {result.drive_thumbnail_url}")
        except Exception as e:
            logger.warning(f"[parser] image upload failed for {img.image_ref}: {e}")
    return results


def _build_user_message(
    ast: BriefAST,
    fetched_code: Dict[str, FetchExternalCodeOutput],
    uploaded_images: dict,
) -> str:
    """Assemble the single LLM prompt from the AST plus already-fetched resources.

    Embeds fetched code file contents and Drive image URLs directly in the prompt
    so the LLM receives everything it needs to produce the task markdown in one call.
    """
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

    if ast.code_fences:
        parts.append("## Inline code fences")
        for cf in ast.code_fences:
            parts.append(f"### Section {cf.section_index} ({cf.language or 'no-lang'})")
            parts.append("```")
            parts.append(cf.content)
            parts.append("```")
        parts.append("")

    if uploaded_images:
        parts.append("## Embedded images (uploaded to Drive)")
        for ref, result in uploaded_images.items():
            parts.append(f"- {ref}:")
            parts.append(f"  - thumbnail: {result.drive_thumbnail_url}")
            parts.append(f"  - full-res:  {result.drive_view_url}")
        parts.append("")
    elif ast.embedded_images:
        parts.append("## Embedded images (upload unavailable — omit Design Reference sections)")
        for img in ast.embedded_images:
            parts.append(f"- {img.image_ref}")
        parts.append("")

    if fetched_code:
        parts.append("## Fetched external code")
        for url, result in fetched_code.items():
            parts.append(f"### {url}  (status: {result.status})")
            if result.status == "ok" and result.files:
                for f in result.files:
                    lang = f.language or ""
                    parts.append(f"#### {f.filename}")
                    parts.append(f"```{lang}")
                    parts.append(f.content)
                    parts.append("```")
            else:
                parts.append(f"> {result.error or result.status}")
            parts.append("")

    return "\n".join(parts)


def run(ast: BriefAST, output_dir: Path) -> RunSummary:
    """Extract tasks from a BriefAST and write one markdown file per task.

    Called by cli.py after brief_parser.parse(). Runs the four-step pipeline:
    pre-fetch links → pre-upload images → single LLM call → write files.
    Returns a RunSummary listing the written file paths and any inline notes.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = RunSummary()
    client = _init_client()
    system_prompt = (
        Path(__file__).parent / "prompts" / "system.md"
    ).read_text(encoding="utf-8")

    # Step 1: pre-fetch all external links
    fetched_code = _prefetch_links(ast, output_dir)

    # Step 2: pre-upload all embedded images
    uploaded_images = _prefetch_images(ast, output_dir)

    # Step 3: single LLM call — structured output
    user_message = _build_user_message(ast, fetched_code, uploaded_images)
    logger.info("[parser] calling LLM for task extraction")

    try:
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type":   "json_schema",
                    "name":   "extraction_output",
                    "schema": _OUTPUT_SCHEMA,
                    "strict": True,
                }
            },
        )
    except Exception as e:
        summary.aborted = True
        summary.abort_reason = f"LLM call failed: {e}"
        logger.error(summary.abort_reason)
        return summary

    raw = getattr(resp, "output_text", None)
    if not raw:
        summary.aborted = True
        summary.abort_reason = "LLM returned no output"
        logger.error(summary.abort_reason)
        return summary

    try:
        tasks = json.loads(raw).get("tasks", [])
    except Exception as e:
        summary.aborted = True
        summary.abort_reason = f"Failed to parse LLM output: {e}"
        logger.error(summary.abort_reason)
        return summary

    if not tasks:
        summary.aborted = True
        summary.abort_reason = "LLM returned zero tasks"
        logger.warning(summary.abort_reason)
        return summary

    # Step 4: post-process — strip protected domains, write files
    for task in tasks:
        slug    = task.get("slug", "task")
        content = task.get("markdown_content", "")
        content = _PROTECTED_URL_RE.sub("", content)   # strip https://domain/... URLs
        content = _PROTECTED_BARE_RE.sub("", content)  # strip bare domain mentions
        try:
            result = emit_task(
                EmitTaskInput(slug=slug, markdown_content=content),
                output_dir=output_dir,
            )
            summary.emitted_tasks.append(result.written_to)
            summary.inline_notes += result.inline_note_count
            logger.info(f"[parser] emitted {result.written_to}")
        except LeakDetectedError as e:
            logger.error(
                f"[parser] task '{slug}' still contains protected domains after stripping "
                f"— skipping. Matched: {e.matched_domains}"
            )
        except Exception as e:
            logger.error(f"[parser] failed to write task '{slug}': {e}")

    return summary
