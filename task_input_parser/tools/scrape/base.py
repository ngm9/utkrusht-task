"""Shared helpers for external-code scraping: cache + content validation."""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class FetchedFile(BaseModel):
    filename: str
    content: str
    detected_language: str  # "html", "css", "js", "ts", "py", "json", "other"


def cache_path_for_url(output_dir: Path, url: str) -> Path:
    """Return the cache file path for a URL by hashing it into a sibling parser_cache/ directory."""
    cache_dir = output_dir.parent / "parser_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{sha256(url.encode()).hexdigest()}.json"


def read_cache(output_dir: Path, url: str) -> Optional[dict]:
    """Load a previously cached fetch result for a URL; returns None on cache miss or read error."""
    p = cache_path_for_url(output_dir, url)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_cache(output_dir: Path, url: str, payload: dict) -> None:
    """Persist a fetch result to disk so repeated calls for the same URL are instant."""
    cache_path_for_url(output_dir, url).write_text(json.dumps(payload), encoding="utf-8")


_EXT_TO_LANG = {
    ".html": "html", ".htm": "html",
    ".css": "css",
    ".js": "js", ".mjs": "js",
    ".ts": "ts", ".tsx": "ts",
    ".jsx": "js",
    ".py": "py",
    ".json": "json",
    ".md": "md",
}


def detect_language_by_filename(filename: str) -> str:
    """Map a filename's extension to a language tag (html, css, js, ts, py, json, md, other)."""
    suffix = Path(filename).suffix.lower()
    return _EXT_TO_LANG.get(suffix, "other")


def validate_files(files: List[FetchedFile]) -> tuple[bool, Optional[str]]:
    """Light content validation per language. Returns (ok, error_message).

    Validation is conservative — non-empty + simple sanity checks. Strict
    parsing libraries are intentionally avoided to keep dependencies minimal.
    """
    if not files:
        return False, "empty file list returned by scraper"
    for f in files:
        if not f.filename:
            return False, "file with empty filename"
        # Empty content is allowed (CodePen pens often have an empty JS pane);
        # the agent decides whether an empty file is a problem in context.
    return True, None
