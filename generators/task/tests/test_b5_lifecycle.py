"""Unit tests for the B5 transactional-task helpers."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from generators.task import persistence


def _fake_chain(returns):
    """Build a MagicMock chain emulating ``sb.table(...).update(...).eq(...).execute()``."""
    chain = MagicMock()
    chain.table.return_value.update.return_value.eq.return_value.execute.return_value = returns
    return chain


def test_insert_draft_task_sets_status_draft_and_returns_id():
    fake_sb = MagicMock()
    fake_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "11111111-2222-3333-4444-555555555555"}]
    )
    with patch.object(persistence, "init_supabase", return_value=fake_sb):
        task_id = persistence.insert_draft_task(
            {"created_at": "x", "task_blob": {"title": "t"}},
            env="dev",
        )

    args, _ = fake_sb.table.return_value.insert.call_args
    inserted = args[0]
    assert inserted["status"] == "draft"
    assert inserted["task_blob"]["title"] == "t"
    assert task_id == "11111111-2222-3333-4444-555555555555"


def test_insert_draft_task_raises_when_supabase_returns_nothing():
    fake_sb = MagicMock()
    fake_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    with patch.object(persistence, "init_supabase", return_value=fake_sb):
        with pytest.raises(Exception):
            persistence.insert_draft_task({"created_at": "x"}, env="dev")


def test_mark_task_ready_only_patches_supplied_fields():
    fake_sb = _fake_chain(MagicMock(data=[{"id": "tid", "status": "ready"}]))
    with patch.object(persistence, "init_supabase", return_value=fake_sb):
        row = persistence.mark_task_ready(
            "tid",
            env="dev",
            task_blob={"x": 1},
            solutions={"y": 2},
        )
    update_call = fake_sb.table.return_value.update.call_args
    payload = update_call[0][0]
    assert payload["status"] == "ready"
    assert payload["task_blob"] == {"x": 1}
    assert payload["solutions"] == {"y": 2}
    # eval_info/readme_content not set → not in payload
    assert "eval_info" not in payload
    assert "readme_content" not in payload
    assert row["status"] == "ready"


def test_mark_task_failed_swallows_supabase_errors():
    fake_sb = MagicMock()
    fake_sb.table.return_value.update.return_value.eq.return_value.execute.side_effect = RuntimeError("boom")
    with patch.object(persistence, "init_supabase", return_value=fake_sb):
        # Should NOT raise — best-effort cleanup.
        persistence.mark_task_failed("tid", env="dev", error="db down")


def test_delete_github_repo_noop_without_token():
    with patch.object(persistence, "GITHUB_UTKRUSHTAPPS_TOKEN", ""):
        persistence.delete_github_repo("any-repo")
    # Just ensure no exception raised.
