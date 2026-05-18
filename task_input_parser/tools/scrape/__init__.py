"""Platform detection and dispatch for `fetch_external_code`."""
from __future__ import annotations

import re
from typing import Literal

Platform = Literal[
    "codepen",
    "gist",
    "codesandbox_unsupported",
    "jsfiddle_unsupported",
    "pastebin_unsupported",
    "replit_unsupported",
    "gitlab_snippet_unsupported",
    "unknown",
]

_PATTERNS: list[tuple[re.Pattern, Platform]] = [
    (re.compile(r"https?://(?:www\.)?codepen\.io/(?:team/)?[^/]+/(?:pen|details|full)/", re.IGNORECASE), "codepen"),
    (re.compile(r"https?://gist\.github\.com/[^/]+/[a-f0-9]+", re.IGNORECASE), "gist"),
    (re.compile(r"https?://(?:www\.)?codesandbox\.io/", re.IGNORECASE), "codesandbox_unsupported"),
    (re.compile(r"https?://(?:www\.)?jsfiddle\.net/", re.IGNORECASE), "jsfiddle_unsupported"),
    (re.compile(r"https?://(?:www\.)?pastebin\.com/", re.IGNORECASE), "pastebin_unsupported"),
    (re.compile(r"https?://(?:www\.)?replit\.com/", re.IGNORECASE), "replit_unsupported"),
    (re.compile(r"https?://gitlab\.com/snippets/", re.IGNORECASE), "gitlab_snippet_unsupported"),
]


def detect_platform(url: str) -> Platform:
    for pat, name in _PATTERNS:
        if pat.match(url):
            return name
    return "unknown"
