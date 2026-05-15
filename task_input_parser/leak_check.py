"""Source-URL leak detection (Principle VIII — No Customer-Source Leakage).

Shared module used by both `parser.tools.emit` (to reject markdown that
contains a banned domain before writing) and `parser.tools.fetch` (to
maintain the list of platforms whose source URLs must never appear in the
candidate-facing markdown).
"""
import re
from typing import List

LEAK_DOMAINS: List[str] = [
    r"codepen\.io",
    r"codesandbox\.io",
    r"jsfiddle\.net",
    r"gist\.github\.com",
    r"pastebin\.com",
    r"replit\.com",
    r"gitlab\.com/snippets",
]

_LEAK_PATTERN = re.compile("|".join(LEAK_DOMAINS), re.IGNORECASE)


def check_leak(text: str) -> List[str]:
    """Return the list of banned domain patterns matched in `text`.

    Empty list = clean. Non-empty = the markdown must NOT be written;
    the agent should remove the URLs and retry.
    """
    return list(set(_LEAK_PATTERN.findall(text)))
