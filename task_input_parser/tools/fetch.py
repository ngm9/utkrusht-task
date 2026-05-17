"""fetch_external_code — fetches starter code from external URLs before the LLM call.

Called directly by _prefetch_links() in extractor.py for every URL found in the BriefAST.
The result (fetched files or an error status) is embedded in the LLM prompt so the
LLM can include the code in the task markdown without making any tool calls itself.

v1 supports GitHub Gist (plain HTTP). Other platforms return a status that the LLM
uses to add an inline **Note:** in the task markdown:
  - "bot_protected"          — CodePen and other Cloudflare-gated platforms.
  - "platform_not_supported" — CodeSandbox, JSFiddle, Pastebin, Replit, GitLab snippets.
  - "fetch_failed"           — network or parse error on a supported platform.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from task_input_parser.tools.scrape import detect_platform
from task_input_parser.tools.scrape.base import (
    FetchedFile,
    read_cache,
    validate_files,
    write_cache,
)

Status = Literal[
    "ok",
    "bot_protected",
    "platform_not_supported",
    "fetch_failed",
    "validation_failed",
]


# Canonical fallback message — used verbatim by the system prompt when
# the LLM receives `status="bot_protected"` from this tool.
BOT_PROTECTED_GUIDANCE = (
    "Your document contains a link to a bot-protected external resource. "
    "We do not circumvent these protections (jurisdictional restrictions). "
    "What to do instead: open the link, copy the source file-by-file into "
    "this document, and re-run the parser."
)


class FetchExternalCodeInput(BaseModel):
    url: str = Field(..., description="Full external URL to fetch starter code from.")


class FetchExternalCodeOutput(BaseModel):
    platform_detected: str
    status: Status
    files: List[FetchedFile] = []
    error: Optional[str] = None


def fetch_external_code(
    inp: FetchExternalCodeInput,
    output_dir: Optional[Path] = None,
) -> FetchExternalCodeOutput:
    """Fetch starter-code files from an external URL and return the result.

    Called directly by extractor._prefetch_links() before the LLM call.
    Detects the URL platform, checks the on-disk cache, and fetches if needed.
    Returns FetchExternalCodeOutput with status="ok" and file contents on success,
    or status="bot_protected"/"platform_not_supported"/"fetch_failed" with an
    error message the LLM embeds as a **Note:** in the task markdown.
    """
    if output_dir is None:
        raise ValueError("fetch_external_code requires an output_dir")
    output_dir = Path(output_dir)

    platform = detect_platform(inp.url)

    # Cache check (all statuses are cached so repeated calls are no-ops)
    cached = read_cache(output_dir, inp.url)
    if cached:
        return FetchExternalCodeOutput.model_validate(cached)

    # CodePen is known to sit behind Cloudflare's bot-protection challenge.
    # Per policy we do not attempt to bypass it — return bot_protected
    # immediately with the canonical guidance.
    if platform == "codepen":
        out = FetchExternalCodeOutput(
            platform_detected=platform,
            status="bot_protected",
            error=BOT_PROTECTED_GUIDANCE,
        )
        write_cache(output_dir, inp.url, out.model_dump())
        return out

    # GitHub Gist — plain HTTP, no protection, no bypass needed.
    if platform == "gist":
        try:
            from task_input_parser.tools.scrape.gist import fetch_gist
            files = fetch_gist(inp.url)
        except Exception as e:
            out = FetchExternalCodeOutput(
                platform_detected=platform, status="fetch_failed", error=str(e)
            )
            write_cache(output_dir, inp.url, out.model_dump())
            return out

        ok, err = validate_files(files)
        if not ok:
            out = FetchExternalCodeOutput(
                platform_detected=platform, status="validation_failed", error=err
            )
            write_cache(output_dir, inp.url, out.model_dump())
            return out

        out = FetchExternalCodeOutput(
            platform_detected=platform, status="ok", files=files
        )
        write_cache(output_dir, inp.url, out.model_dump())
        return out

    # Known platforms we haven't implemented a fetcher for (CodeSandbox,
    # JSFiddle, Pastebin, Replit, GitLab snippets).
    if platform.endswith("_unsupported"):
        out = FetchExternalCodeOutput(
            platform_detected=platform,
            status="platform_not_supported",
            error=(
                f"v1 supports only GitHub Gist for automated fetching. "
                f"The URL points to {platform.replace('_unsupported', '')}, "
                f"which is not yet supported. Please paste the source "
                f"into this document and re-run the parser."
            ),
        )
        write_cache(output_dir, inp.url, out.model_dump())
        return out

    # Anything else — unrecognised URL pattern.
    out = FetchExternalCodeOutput(
        platform_detected=platform,
        status="platform_not_supported",
        error=f"Unknown URL pattern; no scraper available for {inp.url!r}.",
    )
    write_cache(output_dir, inp.url, out.model_dump())
    return out
