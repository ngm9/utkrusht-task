"""Durable jobs queue — B3 of the production-readiness plan.

A Postgres-backed worker queue keyed off the ``generation_jobs`` table.
Workers claim a row via ``SELECT … FOR UPDATE SKIP LOCKED``, run the
pipeline in-process, then update the row. Restart-safe: a crash leaves
a ``running`` row that the watchdog returns to ``queued`` or marks
``failed`` after ``max_attempts``.

Modules:

* :mod:`infra.jobs.models`     — ``GenerationJob`` dataclass
* :mod:`infra.jobs.repository` — Supabase CRUD + claim / requeue helpers
* :mod:`infra.jobs.worker`     — poll loop entry point
"""

from infra.jobs.models import GenerationJob, JobStatus
from infra.jobs.repository import (
    claim_next_job,
    enqueue_job,
    mark_done,
    mark_failed,
    requeue_stuck_jobs,
    update_stage,
)

__all__ = [
    "GenerationJob",
    "JobStatus",
    "claim_next_job",
    "enqueue_job",
    "mark_done",
    "mark_failed",
    "requeue_stuck_jobs",
    "update_stage",
]
