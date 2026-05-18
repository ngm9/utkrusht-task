"""GitHub Gist scraper — plain HTTP, no Cloudflare gate."""
from __future__ import annotations

import re
from typing import List

import requests

from task_input_parser.tools.scrape.base import FetchedFile, detect_language_by_filename

_GIST_URL_RE = re.compile(
    r"https?://gist\.github\.com/(?P<user>[^/]+)/(?P<id>[a-f0-9]+)",
    re.IGNORECASE,
)


def fetch_gist(url: str) -> List[FetchedFile]:
    """Fetch all files from a public GitHub Gist URL.

    Uses the GitHub API (https://api.github.com/gists/{id}) which returns
    JSON with all files including filename + content. No auth required for
    public gists.
    """
    m = _GIST_URL_RE.match(url)
    if not m:
        raise ValueError(f"Not a Gist URL: {url!r}")
    gist_id = m.group("id")
    api_url = f"https://api.github.com/gists/{gist_id}"

    resp = requests.get(api_url, timeout=30, headers={"Accept": "application/vnd.github+json"})
    resp.raise_for_status()
    data = resp.json()

    files: List[FetchedFile] = []
    for filename, payload in (data.get("files") or {}).items():
        content = payload.get("content") or ""
        files.append(FetchedFile(
            filename=filename,
            content=content,
            detected_language=detect_language_by_filename(filename),
        ))
    return files
