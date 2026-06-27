"""Canonical LLM token pricing — ONE table, no drift.

USD per 1,000,000 tokens as ``(input_rate, output_rate)``. Every cost estimate
in the pipeline MUST price through here — the per-run summary in
``infra/utils.py``, the scenario + input-file generators, and the trace_ui
Result panel (via ``infra/tracing/cost.py``). Before this module these were four
independent tables that silently drifted: ``cost.py`` lacked ``claude-opus-4-8``
and ``gpt-5.5`` (the models actually used), and the generators still priced
``gpt-5.5`` at the old ``gpt-5-nano`` rate — so trace_ui reported a fraction of
true spend. One table + a warn-on-unknown lookup means a model rename can never
again undercount silently.

Rates are ESTIMATES; treat any derived number as approximate.
"""
from __future__ import annotations

import re

from infra.logger_config import logger

# model -> (input_usd_per_1M, output_usd_per_1M)
PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    # OpenAI (gpt-5 family)
    "gpt-5.5": (5.0, 30.0),
    "gpt-5.4": (2.5, 15.0),
    "gpt-5.4-mini": (0.75, 4.5),
    "gpt-5.4-nano": (0.3, 1.5),
    "gpt-5.1-2025-11-13": (2.0, 8.0),
}

# Fallback for an unrecognised model. Deliberately NOT cheap — an unknown model
# is more likely a new frontier model than a nano, so we'd rather over- than
# under-estimate while the one-time warning prompts someone to add it.
PRICING_DEFAULT: tuple[float, float] = (5.0, 25.0)

_warned: set[str] = set()


def _canonical(model: str | None) -> str:
    """Normalise a model id: drop a provider prefix (``openai/gpt-5.5``) and a
    trailing ``-YYYY-MM-DD`` date stamp, but only when that lands on a known key
    (so dated keys like ``gpt-5.1-2025-11-13`` are preserved)."""
    if not model:
        return ""
    m = model.strip()
    if "/" in m:
        m = m.split("/", 1)[1]
    if m in PRICING:
        return m
    stripped = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", m)
    return stripped if stripped in PRICING else m


def price_per_million(model: str | None) -> tuple[float, float]:
    """``(input, output)`` USD per 1M tokens for ``model``.

    Warns exactly once per unknown model and returns :data:`PRICING_DEFAULT`, so
    a missing rate is loud (fix it in the table) rather than a silent undercount.
    """
    key = _canonical(model)
    if key in PRICING:
        return PRICING[key]
    if model and model not in _warned:
        _warned.add(model)
        logger.warning(
            f"[pricing] no rate for model '{model}' — using default "
            f"${PRICING_DEFAULT[0]}/${PRICING_DEFAULT[1]} per 1M (in/out). "
            f"Add it to infra/pricing.PRICING so cost reporting stays accurate."
        )
    return PRICING_DEFAULT


def cost_usd(model: str | None, input_tokens: int, output_tokens: int) -> float:
    """Estimated USD for a call's token usage at the canonical rate."""
    pin, pout = price_per_million(model)
    return input_tokens / 1_000_000 * pin + output_tokens / 1_000_000 * pout
