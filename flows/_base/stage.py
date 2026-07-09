from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageSpec:
    """Static description of one pipeline stage.

    The dynamic argv (competency names, resolved paths, env) is built per-run by
    the flow's pipeline module; this spec captures only the invariant parts so
    the module addresses and streaming/tracing flags live in one manifest
    instead of being hardcoded inline.
    """

    name: str
    """Log label prefix, e.g. ``"00_preflight"``."""

    module: str
    """``python -m <module>`` target for this stage's subprocess."""

    traced: bool = False
    """Whether the stage sets ``PIPELINE_TRACING_ENABLED=1`` (LLM-bearing stages)."""

    exit0_on_reject: bool = False
    """Stage exits 0 even when it rejects (stage 04 / eval-gate)."""

    live_markers: tuple[tuple[str, tuple[str, ...]], ...] = field(default_factory=tuple)
    """``(filename, markers)`` rules for live stderr sub-log splitting."""
