"""emit_task tool — writes the final per-task markdown after leak-check.

The leak-check is the safety gate for constitution Principle VIII (No
Customer-Source Leakage). If the markdown contains a banned code-hosting
domain (codepen.io, gist.github.com, etc.), `emit_task` rejects the write
with a structured `LeakDetectedError` that the agent loop forwards back to
the LLM as a tool-error response. The LLM must remove the URL and retry.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from task_input_parser.leak_check import check_leak


class LeakDetectedError(Exception):
    """Raised when emit_task's leak check finds banned domains in the markdown."""

    def __init__(self, matched_domains: List[str], slug: str):
        self.matched_domains = matched_domains
        self.slug = slug
        super().__init__(
            f"emit_task(slug={slug!r}) rejected: markdown contains banned "
            f"code-hosting domain(s) {matched_domains!r}. Remove the URL(s) "
            f"and call emit_task again. The candidate must not see the "
            f"source URL of any scraped resource."
        )


_KEBAB_RE = re.compile(r"[^a-z0-9-]+")


def _kebab(s: str) -> str:
    """Convert any string to a kebab-case slug safe for use as a filename."""
    s = s.lower().strip().replace("_", "-")
    s = _KEBAB_RE.sub("-", s)
    return s.strip("-") or "task"


class EmitTaskInput(BaseModel):
    slug: str = Field(..., description="kebab-case slug for the filename (e.g. 'mysql', 'frontend-popup')")
    markdown_content: str = Field(..., description="The complete per-task markdown content")


class EmitTaskOutput(BaseModel):
    written_to: str
    file_size_bytes: int
    inline_note_count: int


def emit_task(inp: EmitTaskInput, output_dir: Optional[Path] = None) -> EmitTaskOutput:
    """Run leak-check on the markdown, then write it as task-N-<slug>.md in output_dir; raises LeakDetectedError if a banned domain is found."""
    if output_dir is None:
        raise ValueError("emit_task requires an output_dir")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    matched = check_leak(inp.markdown_content)
    if matched:
        raise LeakDetectedError(matched_domains=matched, slug=inp.slug)

    # Sequential file index based on existing task-*.md files in the dir.
    existing = sorted(p.name for p in output_dir.glob("task-*.md"))
    next_index = len(existing) + 1
    slug = _kebab(inp.slug)
    filename = f"task-{next_index}-{slug}.md"
    target = output_dir / filename
    target.write_text(inp.markdown_content, encoding="utf-8")

    inline_note_count = len(re.findall(r"\*\*Note:\*\*", inp.markdown_content))

    return EmitTaskOutput(
        written_to=str(target),
        file_size_bytes=target.stat().st_size,
        inline_note_count=inline_note_count,
    )
