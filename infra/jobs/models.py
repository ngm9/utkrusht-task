"""Typed model for the ``generation_jobs`` row.

Mirrors the columns in the ``generation_jobs`` migration in the Utkrushta
backend repo (``supabase/migrations/20260530000002_create_generation_jobs.sql``)
so the rest of the codebase can pass a frozen dataclass around instead of
a raw dict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class GenerationJob:
    """One row in ``generation_jobs``."""

    id: str
    brief: dict[str, Any]
    status: JobStatus = JobStatus.QUEUED
    conversation_id: str | None = None
    stage: str | None = None
    log_url: str | None = None
    workspace_path: str | None = None
    result_task_id: str | None = None
    error: str | None = None
    env: str = "dev"
    locked_by: str | None = None
    locked_at: datetime | None = None
    attempts: int = 0
    max_attempts: int = 1
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "GenerationJob":
        """Build a ``GenerationJob`` from a raw Supabase row dict.

        Unknown / extra fields are stashed under ``extra`` rather than
        dropped — keeps forward-compat with column additions.
        """
        known = {
            "id", "brief", "status", "conversation_id", "stage", "log_url",
            "workspace_path", "result_task_id", "error", "env",
            "locked_by", "locked_at", "attempts", "max_attempts",
            "started_at", "finished_at", "created_at", "updated_at",
        }
        extra = {k: v for k, v in row.items() if k not in known}
        return cls(
            id=str(row["id"]),
            brief=row.get("brief") or {},
            status=JobStatus(row.get("status", "queued")),
            conversation_id=row.get("conversation_id"),
            stage=row.get("stage"),
            log_url=row.get("log_url"),
            workspace_path=row.get("workspace_path"),
            result_task_id=row.get("result_task_id"),
            error=row.get("error"),
            env=row.get("env", "dev"),
            locked_by=row.get("locked_by"),
            locked_at=_parse_ts(row.get("locked_at")),
            attempts=int(row.get("attempts") or 0),
            max_attempts=int(row.get("max_attempts") or 1),
            started_at=_parse_ts(row.get("started_at")),
            finished_at=_parse_ts(row.get("finished_at")),
            created_at=_parse_ts(row.get("created_at")),
            updated_at=_parse_ts(row.get("updated_at")),
            extra=extra,
        )


def _parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
