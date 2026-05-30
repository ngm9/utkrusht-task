"""Postgres-backed worker loop — B3 of the production-readiness plan.

Run as a long-lived process. Polls ``generation_jobs`` for queued rows,
claims one at a time, runs the in-process orchestrator, persists the
outcome. Restart-safe: crash mid-run leaves a ``running`` row that the
watchdog returns to ``queued`` or fails after ``max_attempts``.

CLI:

    python -m infra.jobs.worker --env dev
    python -m infra.jobs.worker --env dev --once       # process one job and exit
    python -m infra.jobs.worker --env dev --interval 5 # custom poll interval

Configure concurrency by running multiple worker processes — each one
claims a distinct row via the SKIP-LOCKED-style update in
``repository.claim_next_job``.
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from apps.orchestrator import run_pipeline_for_job
from apps.orchestrator.pipeline import PipelineResult, StageResult
from infra import metrics
from infra.jobs import repository as jobs_repo
from infra.jobs.models import GenerationJob
from infra.storage import s3 as storage_s3

logger = logging.getLogger("jobs.worker")


def _configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )


def process_job(job: GenerationJob) -> None:
    """Run one claimed job to completion."""
    log_prefix = f"[jobs:{job.id[:8]}]"
    logger.info("%s claimed (env=%s)", log_prefix, job.env)
    metrics.inc("jobs_claimed_total", env=job.env)

    def on_stage(stage: StageResult) -> None:
        jobs_repo.update_stage(job.id, stage.label, env=job.env)
        metrics.inc(
            "stage_total",
            env=job.env, stage=stage.label, status=stage.status,
        )
        logger.info(
            "%s stage %s -> %s (%.2fs)",
            log_prefix, stage.label, stage.status, stage.duration_s,
        )
        # Persist the stage's log tail so the admin UI can show it without
        # filesystem access to the worker. Cheap on every stage; only the
        # last ~4 KB is kept per stage.
        if stage.log_path:
            try:
                text = Path(stage.log_path).read_text(
                    encoding="utf-8", errors="replace",
                )
            except Exception as exc:  # noqa: BLE001
                text = f"(log unavailable: {exc})"
            jobs_repo.append_stage_log(
                job.id, stage.label, text, env=job.env,
            )

    try:
        workspace = Path(job.workspace_path) if job.workspace_path else None
        result = run_pipeline_for_job(
            job_id=job.id, brief=job.brief, env=job.env,
            workspace=workspace, on_stage=on_stage,
        )
        # Persist the post-run brief (with stamped file paths + S3 URLs).
        # Best-effort: a failed brief write shouldn't override the run result.
        try:
            jobs_repo.update_brief(job.id, job.brief, env=job.env)
        except Exception as exc:  # noqa: BLE001
            logger.warning("%s update_brief failed: %s", log_prefix, exc)

        stage_urls = _upload_stage_logs(job.id, job.env, result)
        if stage_urls:
            try:
                jobs_repo.update_stage_log_urls(job.id, stage_urls, env=job.env)
            except Exception as exc:  # noqa: BLE001
                logger.warning("%s update_stage_log_urls failed: %s", log_prefix, exc)
        # `log_url` (singular) points to the failing stage's log when the
        # run failed — a useful "click here to see what broke" pointer for
        # the row's top-level error. Null on success since per-stage URLs
        # in stage_log_urls cover that case.
        focus_log_url = None
        if result.status != "ok" and result.stages:
            focus_log_url = stage_urls.get(result.stages[-1].label)

        if result.status == "ok":
            jobs_repo.mark_done(
                job.id, env=job.env, result_task_id=result.task_id,
            )
            metrics.inc("jobs_done_total", env=job.env)
            logger.info(
                "%s done task_id=%s total=%.1fs stages_uploaded=%d",
                log_prefix, result.task_id, result.total_duration_s,
                len(stage_urls),
            )
        else:
            jobs_repo.mark_failed(
                job.id, env=job.env, error=result.error or "",
                log_url=focus_log_url,
            )
            metrics.inc("jobs_failed_total", env=job.env)
            logger.warning(
                "%s failed at %s: %s log_url=%s",
                log_prefix, result.stages[-1].label if result.stages else "?",
                result.error, focus_log_url or "-",
            )
    except Exception as exc:
        # Watchdog will surface this; explicitly mark failed too.
        logger.exception("%s crashed: %s", log_prefix, exc)
        jobs_repo.mark_failed(job.id, env=job.env, error=str(exc))
        metrics.inc("jobs_crashed_total", env=job.env)


def _upload_stage_logs(
    job_id: str, env: str, result: PipelineResult,
) -> dict[str, str]:
    """Upload each stage's full log file as its own S3 object.

    Returns a {stage_label: public_url} map for stages that uploaded
    successfully. Stages with missing/unreadable log files are skipped
    silently (their absence shows up as a missing key in the map).

    Layout: ``task_builder/{job_id}/{stage_label}.log`` — mirrors the
    legacy ``.task_agent_runs/<run>/{stage}.stdout`` layout (stdout +
    stderr merged, since the orchestrator captures them into a single
    buffer via ``contextlib.redirect_stderr`` aliasing).

    Never raises — a per-stage upload failure logs a warning and that
    stage simply doesn't appear in the returned map.
    """
    urls: dict[str, str] = {}
    if not storage_s3.is_enabled():
        return urls
    bucket = storage_s3.bucket_for(env)
    for stage in result.stages:
        if not stage.log_path:
            continue
        try:
            text = Path(stage.log_path).read_text(
                encoding="utf-8", errors="replace",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[jobs:%s] could not read log for stage %s: %s",
                job_id[:8], stage.label, exc,
            )
            continue
        if stage.error:
            text = f"{text}\n\n--- error ---\n{stage.error}\n"
        try:
            key = storage_s3.key_for_run(job_id, stage.label, ext="log")
            urls[stage.label] = storage_s3.upload_text(
                bucket, key, text,
                content_type="text/plain; charset=utf-8",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[jobs:%s] log upload failed for stage %s: %s",
                job_id[:8], stage.label, exc,
            )
    return urls


class WorkerLoop:
    def __init__(
        self,
        *,
        env: str = "dev",
        interval_seconds: float = 5.0,
        watchdog_every_seconds: float = 300.0,
    ) -> None:
        self.env = env
        self.interval = interval_seconds
        self.watchdog_every = watchdog_every_seconds
        self._last_watchdog = 0.0
        self._stopping = False
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)

    def _stop(self, *_args: Any) -> None:
        logger.info("stop signal received — finishing in-flight job and exiting")
        self._stopping = True

    def step(self) -> bool:
        """One tick of the loop. Returns True if a job ran, False if idle."""
        now = time.monotonic()
        if now - self._last_watchdog > self.watchdog_every:
            try:
                jobs_repo.requeue_stuck_jobs(env=self.env)
            except Exception as exc:
                logger.warning("watchdog tick failed: %s", exc)
            self._last_watchdog = now

        try:
            job = jobs_repo.claim_next_job(env=self.env)
        except Exception as exc:
            logger.warning("claim_next_job failed: %s", exc)
            return False
        if job is None:
            return False
        process_job(job)
        return True

    def run_forever(self) -> None:
        logger.info("worker loop start env=%s interval=%.1fs", self.env, self.interval)
        while not self._stopping:
            ran = self.step()
            if not ran:
                time.sleep(self.interval)
        logger.info("worker loop exit")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("dev", "prod"), default="dev")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="Poll interval in seconds when queue is empty.")
    parser.add_argument("--once", action="store_true",
                        help="Process one job (or noop if queue empty) and exit.")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    args = parser.parse_args(argv)
    _configure_logging(args.log_level)

    loop = WorkerLoop(env=args.env, interval_seconds=args.interval)
    if args.once:
        loop.step()
        return 0
    loop.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
