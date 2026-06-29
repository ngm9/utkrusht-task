"""Anthropic prompt caching for the OpenAI-SDK → Portkey Claude call path.

Anthropic caching is NOT automatic (OpenAI auto-caches ≥1024-token prefixes;
Anthropic needs explicit ``cache_control`` breakpoints). To enable it through the
OpenAI chat-completions shape that Portkey accepts, a message's ``content`` must
be a list of typed blocks with ``cache_control: {"type": "ephemeral"}`` on the
block that ends the stable prefix. Portkey forwards this to Anthropic's native
prompt caching — verified live: a repeat call reads the cached prefix at ~0.1×
input cost (``usage.cache_read_input_tokens`` / ``prompt_tokens_details
.cached_tokens`` > 0).

``cache_messages(messages)`` returns a NEW messages list (immutable — never
mutates the caller's list/dicts) with two breakpoints:

* the first ``system`` message — the frozen prefix reused across every call, and
* the last message — the growing-conversation prefix (the canonical multi-turn
  pattern; earlier breakpoints remain valid read points, so a multi-turn loop
  accrues hits incrementally).

Anthropic-only: OpenAI already auto-caches, and the GLM/OpenRouter path is left
as plain strings (``cache_control`` is Anthropic-specific), so this is a no-op
for the ``glm`` provider. Prefixes below the model minimum (~4096 tokens for
Opus, ~2048 for Sonnet) silently don't cache — harmless.
"""
from __future__ import annotations

from typing import Any

from infra.llm_provider import ANTHROPIC, active_provider

_EPHEMERAL = {"type": "ephemeral"}


def caching_enabled() -> bool:
    """True only for the anthropic (Portkey → Claude) provider."""
    return active_provider() == ANTHROPIC


def _as_blocks(content: Any) -> list:
    """Normalise a message's content to a list of typed blocks (copies dicts)."""
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [dict(b) if isinstance(b, dict) else {"type": "text", "text": str(b)}
                for b in content]
    return [{"type": "text", "text": str(content)}]


def _mark_last(blocks: list) -> list:
    """Add a cache_control breakpoint to the last block (returns a new list)."""
    if not blocks:
        return blocks
    out = list(blocks)
    out[-1] = {**out[-1], "cache_control": dict(_EPHEMERAL)}
    return out


def cache_messages(messages: list[dict]) -> list[dict]:
    """Return ``messages`` with Anthropic cache breakpoints on the first system
    message and the last message. Returns the input unchanged for non-anthropic
    providers or empty input. Never mutates the caller's list or dicts."""
    if not caching_enabled() or not messages:
        return messages
    sys_idx = next((i for i, m in enumerate(messages) if m.get("role") == "system"), None)
    mark_idxs = {i for i in (sys_idx, len(messages) - 1) if i is not None}

    out: list[dict] = []
    for i, m in enumerate(messages):
        blocks = _as_blocks(m.get("content"))
        if i in mark_idxs:
            blocks = _mark_last(blocks)
        out.append({**m, "content": blocks})
    return out
