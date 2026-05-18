"""emit_task — writes one task-N-slug.md file after a protected-domain check.

Called directly by extractor.run() in the post-process step, after the LLM call.
By that point extractor.run() has already stripped protected domains from the markdown
using its own regex pass. emit_task runs a final domain check as a safety net and
raises LeakDetectedError if anything slipped through, which extractor.run() catches and logs.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

# Domains that must never appear in candidate-facing markdown (Principle VIII).
_PROTECTED_DOMAINS = [
    r"codepen\.io",
    r"codesandbox\.io",
    r"jsfiddle\.net",
    r"gist\.github\.com",
    r"pastebin\.com",
    r"replit\.com",
    r"gitlab\.com/snippets",
]
_PROTECTED_DOMAIN_RE = re.compile("|".join(_PROTECTED_DOMAINS), re.IGNORECASE)


def _find_protected_domains(text: str) -> List[str]:
    return list(set(_PROTECTED_DOMAIN_RE.findall(text)))


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
    """Write the task markdown to task-N-<slug>.md after a final protected-domain check.

    Called directly by extractor.run() for each task returned by the LLM.
    Raises LeakDetectedError if a protected domain is still present in the markdown
    (extractor.run() catches this and logs it rather than writing a bad file).
    """
    if output_dir is None:
        raise ValueError("emit_task requires an output_dir")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    matched = _find_protected_domains(inp.markdown_content)
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
