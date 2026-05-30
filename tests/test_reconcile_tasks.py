"""Unit tests for scripts/reconcile_tasks.py (B5 reconciler)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reconcile_tasks  # noqa: E402


def test_repo_full_name_from_url():
    assert reconcile_tasks.repo_full_name_from_url(
        "https://github.com/utkrushtapps/task-123"
    ) == "utkrushtapps/task-123"
    assert reconcile_tasks.repo_full_name_from_url("") is None
    assert reconcile_tasks.repo_full_name_from_url("https://github.com/x") is None


def test_check_repo_returns_false_on_404():
    fake_resp = MagicMock(status_code=404)
    with patch.object(reconcile_tasks.requests, "get", return_value=fake_resp):
        ok, err = reconcile_tasks.check_repo("https://github.com/owner/r")
    assert ok is False
    assert err == "repo 404"


def test_check_repo_returns_true_on_200():
    fake_resp = MagicMock(status_code=200)
    with patch.object(reconcile_tasks.requests, "get", return_value=fake_resp):
        ok, err = reconcile_tasks.check_repo("https://github.com/owner/r")
    assert ok is True
    assert err is None


def test_check_repo_treats_network_errors_as_transient():
    """Network errors should NOT flip a row to broken — return True."""
    with patch.object(reconcile_tasks.requests, "get",
                      side_effect=reconcile_tasks.requests.RequestException("conn refused")):
        ok, err = reconcile_tasks.check_repo("https://github.com/owner/r")
    assert ok is True
    assert "network error" in (err or "")


def test_reconcile_ready_tasks_flips_broken_when_repo_gone():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{
            "id": "task-1",
            "task_blob": {
                "resources": {
                    "github_repo": "https://github.com/utkrushtapps/task-1",
                    "github_gist": "https://gist.github.com/owner/abc123",
                }
            },
        }]
    )
    update_mock = sb.table.return_value.update.return_value.eq.return_value
    update_mock.execute.return_value = MagicMock(data=[{"id": "task-1"}])

    with patch.object(reconcile_tasks, "check_repo", return_value=(False, "repo 404")), \
         patch.object(reconcile_tasks, "check_gist", return_value=(True, None)):
        counts = reconcile_tasks.reconcile_ready_tasks(sb, limit=10)

    assert counts == {"scanned": 1, "broken": 1, "ok": 0, "errors": 0}
    payload = sb.table.return_value.update.call_args[0][0]
    assert payload["status"] == "broken"
    assert "github_repo: repo 404" in payload["task_blob"]["reconciler_error"]


def test_reconcile_ready_tasks_passes_through_when_artifacts_intact():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{
            "id": "task-2",
            "task_blob": {"resources": {"github_repo": "https://github.com/o/r"}},
        }]
    )
    with patch.object(reconcile_tasks, "check_repo", return_value=(True, None)), \
         patch.object(reconcile_tasks, "check_gist", return_value=(True, None)):
        counts = reconcile_tasks.reconcile_ready_tasks(sb, limit=10)
    assert counts["ok"] == 1
    assert counts["broken"] == 0
    # No UPDATE should fire on a healthy row.
    sb.table.return_value.update.assert_not_called()
