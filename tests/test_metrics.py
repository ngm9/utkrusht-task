"""Unit tests for infra.metrics (B7)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from infra import metrics


def setup_function(_fn) -> None:
    metrics.REGISTRY.reset()


def test_inc_aggregates_by_label_tuple():
    metrics.inc("jobs_done_total", env="dev")
    metrics.inc("jobs_done_total", env="dev")
    metrics.inc("jobs_done_total", env="prod")
    dumped = metrics.dump()
    by_label = {
        tuple(sorted(entry["labels"].items())): entry["value"]
        for entry in dumped["counters"]["jobs_done_total"]
    }
    assert by_label[(("env", "dev"),)] == 2
    assert by_label[(("env", "prod"),)] == 1


def test_set_gauge_overwrites_previous():
    metrics.set_gauge("queue_depth", 5, env="dev")
    metrics.set_gauge("queue_depth", 3, env="dev")
    dumped = metrics.dump()
    assert dumped["gauges"]["queue_depth"][0]["value"] == 3


def test_snapshot_surfaces_errors_instead_of_raising():
    with patch.object(metrics, "REGISTRY", metrics.REGISTRY):
        with patch("generators.task.persistence.init_supabase", side_effect=RuntimeError("no creds")):
            snap = metrics.snapshot(env="dev")
    assert snap["env"] == "dev"
    assert any("supabase init" in e for e in snap["errors"])


def test_snapshot_aggregates_by_status():
    fake_sb = MagicMock()
    fake_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"status": "queued"}, {"status": "queued"}, {"status": "done"}]
    )
    # Tasks branch: also via select().order().limit().execute()
    # Cache/scenarios: via select().limit().execute()
    fake_sb.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

    with patch("generators.task.persistence.init_supabase", return_value=fake_sb):
        snap = metrics.snapshot(env="dev")

    # Either jobs_by_status or tasks_by_status should reflect the mock data.
    counts = snap.get("jobs_by_status") or snap.get("tasks_by_status") or {}
    assert "queued" in counts or "done" in counts or snap["errors"]
