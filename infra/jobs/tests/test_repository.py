"""Unit tests for infra.jobs.repository (B3)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from infra.jobs import repository as repo
from infra.jobs.models import GenerationJob, JobStatus


def _make_supabase(insert_data=None, select_data=None, update_data=None,
                   single_data=None):
    sb = MagicMock()
    if insert_data is not None:
        sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=insert_data)
    if select_data is not None:
        sel = sb.table.return_value.select.return_value
        sel.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=select_data)
        sel.eq.return_value.lte.return_value.execute.return_value = MagicMock(data=select_data)
        if single_data is not None:
            sel.eq.return_value.single.return_value.execute.return_value = MagicMock(data=single_data)
    if update_data is not None:
        upd = sb.table.return_value.update.return_value
        upd.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=update_data)
        upd.eq.return_value.execute.return_value = MagicMock(data=update_data)
    return sb


def test_enqueue_job_returns_id():
    sb = _make_supabase(insert_data=[{"id": "j1"}])
    with patch.object(repo, "init_supabase", return_value=sb):
        job_id = repo.enqueue_job(brief={"x": 1}, env="dev")
    assert job_id == "j1"
    insert_call = sb.table.return_value.insert.call_args[0][0]
    assert insert_call["status"] == "queued"
    assert insert_call["brief"] == {"x": 1}


def test_claim_next_job_returns_none_when_queue_empty():
    sb = _make_supabase(select_data=[])
    with patch.object(repo, "init_supabase", return_value=sb):
        assert repo.claim_next_job(env="dev") is None


def test_claim_next_job_promotes_oldest_queued():
    sb = MagicMock()
    # select -> one candidate
    sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"id": "j1", "attempts": 0}])
    # update -> success
    sb.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "j1"}])
    # single fetch -> full row
    sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
        data={"id": "j1", "brief": {"x": 1}, "status": "running", "env": "dev"}
    )
    with patch.object(repo, "init_supabase", return_value=sb):
        job = repo.claim_next_job(env="dev")
    assert isinstance(job, GenerationJob)
    assert job.id == "j1"
    assert job.status == JobStatus.RUNNING


def test_claim_next_job_loses_race_returns_none():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"id": "j1", "attempts": 0}])
    sb.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    with patch.object(repo, "init_supabase", return_value=sb):
        assert repo.claim_next_job(env="dev") is None


def test_mark_done_writes_status_and_task_id():
    sb = MagicMock()
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "j1"}])
    with patch.object(repo, "init_supabase", return_value=sb):
        repo.mark_done("j1", env="dev", result_task_id="t1")
    update_payload = sb.table.return_value.update.call_args[0][0]
    assert update_payload["status"] == "done"
    assert update_payload["result_task_id"] == "t1"
    assert update_payload["stage"] == "done"


def test_mark_failed_truncates_long_error():
    sb = MagicMock()
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "j1"}])
    long_error = "x" * 5000
    with patch.object(repo, "init_supabase", return_value=sb):
        repo.mark_failed("j1", env="dev", error=long_error)
    update_payload = sb.table.return_value.update.call_args[0][0]
    assert update_payload["status"] == "failed"
    assert len(update_payload["error"]) == 2000


def test_requeue_stuck_jobs_returns_count():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.lte.return_value.execute.return_value = MagicMock(
        data=[
            {"id": "j1", "attempts": 0, "max_attempts": 1},
            {"id": "j2", "attempts": 1, "max_attempts": 1},
        ]
    )
    sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "x"}])
    with patch.object(repo, "init_supabase", return_value=sb):
        count = repo.requeue_stuck_jobs(env="dev")
    assert count == 2
    # j1 should be re-queued, j2 should be failed
    update_payloads = [c[0][0] for c in sb.table.return_value.update.call_args_list]
    statuses = [p.get("status") for p in update_payloads]
    assert "queued" in statuses
    assert "failed" in statuses


def test_generation_job_from_row_round_trip():
    row = {
        "id": "j1", "brief": {"x": 1}, "status": "running",
        "conversation_id": "c1", "stage": "02_scenarios",
        "env": "dev", "attempts": 2, "max_attempts": 3,
        "locked_at": "2026-05-29T10:00:00Z",
    }
    job = GenerationJob.from_row(row)
    assert job.id == "j1"
    assert job.brief == {"x": 1}
    assert job.status == JobStatus.RUNNING
    assert job.stage == "02_scenarios"
    assert job.attempts == 2
    assert job.max_attempts == 3
    assert job.locked_at is not None
