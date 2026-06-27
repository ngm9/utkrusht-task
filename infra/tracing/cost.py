"""Per-stage + overall LLM cost from captured token usage.

Shared by the pipeline's end-of-run summary (``run_pipeline``) and the trace_ui
Result panel (``trace_ui.server``) so both use ONE pricing table — no drift.

Cost is an ESTIMATE: rates mirror the pipeline's own PRICING (infra/utils.py,
generators/scenarios + input_files); unknown models fall back to a mid rate, so
callers should label the number as approximate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Optional

# Single source of truth for token pricing (see infra/pricing.py). Re-exported
# so any external importer of ``cost.PRICING`` keeps working, but the actual
# lookup goes through ``price_per_million`` which warns on an unknown model
# instead of silently undercounting it.
from infra.pricing import PRICING, PRICING_DEFAULT, price_per_million  # noqa: F401

# Canonical pipeline-stage order for the cost/time table (matches the timeline).
STAGE_ORDER = [
    "input_files", "scenarios", "prompt", "classifier",
    "task_gen", "eval", "gate", "quality", "solution",
]


def _iter_jsonl(path: Path) -> Iterator[dict]:
    """Yield each parseable JSON object from a .jsonl file; tolerate junk."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except Exception:  # noqa: BLE001 — skip a partial/corrupt line
            continue


def compute_cost(traces_dir) -> Optional[dict]:
    """Per-stage + overall cost from ``llm_calls.jsonl`` (token usage × pricing)
    merged with per-stage wall time from ``stages.jsonl``.

    Returns ``None`` when there are no captured calls. Shape::

        {total_usd, total_tokens, input_tokens, output_tokens,
         by_stage: [{stage, usd, input_tokens, output_tokens, duration_ms}],
         estimated: True}
    """
    traces_dir = Path(traces_dir)
    calls = traces_dir / "llm_calls.jsonl"
    if not calls.exists():
        return None

    agg: dict[str, list] = {}  # stage -> [in, out, usd]
    tin = tout = 0
    tusd = 0.0
    for rec in _iter_jsonl(calls):
        usage = rec.get("usage") or {}
        i = int(usage.get("input_tokens") or 0)
        o = int(usage.get("output_tokens") or 0)
        pin, pout = price_per_million(rec.get("model"))
        usd = i / 1_000_000 * pin + o / 1_000_000 * pout
        a = agg.setdefault(rec.get("stage") or "?", [0, 0, 0.0])
        a[0] += i
        a[1] += o
        a[2] += usd
        tin += i
        tout += o
        tusd += usd
    if not agg:
        return None

    durations: dict[str, int] = {}  # last span wins per stage
    for rec in _iter_jsonl(traces_dir / "stages.jsonl"):
        if rec.get("stage") and rec.get("duration_ms") is not None:
            durations[rec["stage"]] = rec["duration_ms"]

    def _order(s: str) -> int:
        return STAGE_ORDER.index(s) if s in STAGE_ORDER else len(STAGE_ORDER)

    rows = [
        {
            "stage": s,
            "usd": round(agg.get(s, [0, 0, 0.0])[2], 4),
            "input_tokens": agg.get(s, [0, 0, 0.0])[0],
            "output_tokens": agg.get(s, [0, 0, 0.0])[1],
            "duration_ms": durations.get(s),
        }
        for s in sorted(set(agg) | set(durations), key=_order)
    ]
    return {
        "total_usd": round(tusd, 4),
        "total_tokens": tin + tout,
        "input_tokens": tin,
        "output_tokens": tout,
        "by_stage": rows,
        "estimated": True,
    }
