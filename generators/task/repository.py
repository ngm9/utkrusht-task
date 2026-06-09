"""Tasks DAO — Supabase data access for the ``tasks`` + ``task_competencies`` tables.

The repository/DAO surface for tasks, mirroring ``generators/scenarios/repository.py``
and ``infra/jobs``' repository pattern. The B5 lifecycle helpers
(``insert_draft_task`` / ``mark_task_ready`` / ``mark_task_failed`` /
``fetch_existing_task_titles``) are owned by ``generators/task/persistence.py`` and
re-exported here so callers have a single tasks-DAO import surface. This module
adds the remaining tasks-table accessors that did not have a home yet:
``get_task`` and ``insert_task_competencies``.

``persistence`` never imports this module, so the one-way import below is
cycle-free.

Validation is delegated to ``task_validation`` (main's Pydantic DAO layer) —
this module is the single tasks-DAO seam, so :func:`validate_task` wraps
``BaseTaskDAO.validate`` rather than duplicating any schema logic.
"""
from __future__ import annotations

from typing import Dict, List

from infra.logger_config import logger
from generators.task.persistence import (  # noqa: F401 — re-exported DAO surface
    fetch_existing_task_titles,
    init_supabase,
    insert_draft_task,
    mark_task_failed,
    mark_task_ready,
)
from task_validation import (  # noqa: F401 — re-exported so callers raise/catch via the seam
    BaseTaskDAO,
    TaskValidationError,
)

__all__ = [
    "insert_draft_task",
    "mark_task_ready",
    "mark_task_failed",
    "fetch_existing_task_titles",
    "get_task",
    "insert_task_competencies",
    "validate_task",
    "TaskValidationError",
]


def validate_task(payload: Dict, env: str = "dev") -> None:
    """Validate a fully-assembled task against the canonical ``TaskForDB``
    schema (main's ``task_validation`` layer) before it is marked ready.

    Schema + FK pre-flight only — does NOT write. Raises
    :class:`task_validation.TaskValidationError` on any failure (the caller's
    build try/except then marks the draft failed and cleans up artifacts).

    Agent (free-form) tasks pass this unchanged: verified that generated agent
    tasks populate ``definitions`` / ``hints`` / ``pre_requisites`` / ``answer``
    / ``resources.github_repo`` / ``solutions.answer_repo`` — exactly what
    ``TaskForDB`` requires — so no agent-specific relaxation is needed.
    """
    BaseTaskDAO(init_supabase(env)).validate(payload, env=env)


def get_task(task_id: str, env: str = "dev", fields: str = "*") -> Dict | None:
    """Fetch a single ``tasks`` row by ``task_id`` (``None`` on miss / error)."""
    try:
        result = (
            init_supabase(env)
            .table("tasks")
            .select(fields)
            .eq("task_id", task_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as exc:
        logger.warning("get_task failed (task_id=%s env=%s): %s", task_id, env, exc)
        return None


def insert_task_competencies(
    task_id: str, competency_ids: List[str], env: str = "dev"
) -> List[Dict]:
    """Insert ``task_competencies`` junction rows linking a task to its competencies.

    Best-effort per row: a relationship failure is logged, not raised — the task
    itself is already persisted, so a missing link must not abort the create.
    Returns the inserted rows.
    """
    sb = init_supabase(env)
    inserted: List[Dict] = []
    for competency_id in competency_ids:
        if not competency_id:
            continue
        try:
            result = (
                sb.table("task_competencies")
                .insert({"task_id": task_id, "competency_id": competency_id})
                .execute()
            )
            if result.data:
                inserted.extend(result.data)
        except Exception as exc:
            logger.error(
                "Failed to insert task-competency relationship (task=%s comp=%s): %s",
                task_id, competency_id, exc,
            )
    return inserted
