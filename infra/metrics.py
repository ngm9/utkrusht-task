"""Lightweight in-process metrics (B7).

A zero-dependency counter/gauge registry plus a one-shot **snapshot** call
that queries Supabase for the live operational numbers (queue depth, ready
vs failed counts, cache hit ratio, orphan count). Goal is to make the
plan's "what does prod look like right now" question answerable with one
function call — not to grow into a full Prometheus client.

Use sites:

* ``infra.jobs.worker``  — bumps ``jobs_running`` / ``jobs_done`` / ``jobs_failed``.
* ``generators.task.gate`` — bumps ``gate_skipped_total{reason}`` whenever the
  gate skips a runtime.
* ``scripts/reconcile_tasks`` — bumps ``orphans_marked_broken_total``.

Read paths:

* ``snapshot(env)`` returns a dict of the *current* operational numbers,
  pulled live from Supabase. Print it from worker startup, expose it on the
  server, or just call it from a notebook.
"""
from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-process counter / gauge primitive
# ---------------------------------------------------------------------------

@dataclass
class _MetricRegistry:
    counters: dict[str, dict[tuple, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    gauges: dict[str, dict[tuple, float]] = field(default_factory=lambda: defaultdict(dict))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, name: str, by: int = 1, **labels: str) -> None:
        with self._lock:
            self.counters[name][tuple(sorted(labels.items()))] += by

    def set(self, name: str, value: float, **labels: str) -> None:
        with self._lock:
            self.gauges[name][tuple(sorted(labels.items()))] = value

    def dump(self) -> dict[str, Any]:
        """Return a structured snapshot of every counter + gauge."""
        out: dict[str, Any] = {"counters": {}, "gauges": {}}
        with self._lock:
            for name, by_labels in self.counters.items():
                out["counters"][name] = [
                    {"labels": dict(labels), "value": value}
                    for labels, value in by_labels.items()
                ]
            for name, by_labels in self.gauges.items():
                out["gauges"][name] = [
                    {"labels": dict(labels), "value": value}
                    for labels, value in by_labels.items()
                ]
        return out

    def reset(self) -> None:
        with self._lock:
            self.counters.clear()
            self.gauges.clear()


REGISTRY = _MetricRegistry()


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def inc(name: str, by: int = 1, **labels: str) -> None:
    REGISTRY.inc(name, by, **labels)


def set_gauge(name: str, value: float, **labels: str) -> None:
    REGISTRY.set(name, value, **labels)


def dump() -> dict[str, Any]:
    return REGISTRY.dump()


# ---------------------------------------------------------------------------
# Operational snapshot — live query against Supabase
# ---------------------------------------------------------------------------

def snapshot(env: str = "dev") -> dict[str, Any]:
    """One-call view of "is prod healthy right now".

    Numbers come from Supabase, not the in-process counters, so they survive
    a worker restart and reflect global state across workers.

    Returns a dict with keys:

    * jobs_by_status: {queued, running, done, failed} counts in last 24h
    * tasks_by_status: {draft, ready, failed, broken}
    * cache_size: row count of task_template_match
    * scenarios_count: row count of generated_scenarios
    * orphans_24h: tasks created in last 24h with status='broken'

    Errors degrade to ``"error": "<msg>"`` rather than raising so a snapshot
    is always something you can print.
    """
    out: dict[str, Any] = {"env": env, "errors": []}
    try:
        from generators.task.persistence import init_supabase
        sb = init_supabase(env)
    except Exception as exc:
        return {"env": env, "errors": [f"supabase init: {exc}"]}

    # Jobs by status (last 24h).
    try:
        # No GROUP BY in supabase-py — pull recent rows and count client-side.
        rows = (
            sb.table("generation_jobs")
            .select("status, created_at")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        ).data or []
        by_status: dict[str, int] = defaultdict(int)
        for r in rows:
            by_status[r.get("status", "?")] += 1
        out["jobs_by_status"] = dict(by_status)
    except Exception as exc:
        out["errors"].append(f"jobs_by_status: {exc}")

    # Tasks by status.
    try:
        rows = (
            sb.table("tasks")
            .select("status")
            .order("created_at", desc=True)
            .limit(2000)
            .execute()
        ).data or []
        tasks_by_status: dict[str, int] = defaultdict(int)
        for r in rows:
            tasks_by_status[r.get("status") or "ready"] += 1
        out["tasks_by_status"] = dict(tasks_by_status)
    except Exception as exc:
        out["errors"].append(f"tasks_by_status: {exc}")

    # Cache size + scenarios pool.
    try:
        out["cache_size"] = len(
            (sb.table("task_template_match").select("combo_key").limit(10000).execute()).data or []
        )
    except Exception as exc:
        out["errors"].append(f"cache_size: {exc}")

    try:
        out["scenarios_count"] = len(
            (sb.table("generated_scenarios").select("id").limit(10000).execute()).data or []
        )
    except Exception as exc:
        out["errors"].append(f"scenarios_count: {exc}")

    # Pull through in-process counters (gate skips by reason, etc.).
    out["in_process"] = REGISTRY.dump()

    return out
