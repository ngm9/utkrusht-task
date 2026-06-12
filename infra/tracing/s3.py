"""End-of-run upload of a run's trace JSONL to S3 — the training corpus.

Env-gated on ``TRACE_S3_BUCKET`` (no bucket → no-op, returns None) and
failure-isolated (an upload error logs a warning and returns None; it never
breaks the pipeline). Objects are partitioned for ML consumption:

    s3://<bucket>/traces/dt=<YYYY-MM-DD>/run=<run_id>/{llm_calls,stages}.jsonl
    s3://<bucket>/traces/dt=<YYYY-MM-DD>/run=<run_id>/manifest.json

``boto3`` is imported lazily so the package has no hard dependency on it.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Optional

from infra.logger_config import logger
from infra.tracing.sink import trace_dir

_FILES = ("llm_calls.jsonl", "stages.jsonl", "manifest.json")
# Human-readable stage logs uploaded alongside the JSONL traces.
_LOG_SUFFIXES = (".stdout", ".stderr", ".log", ".json")


def _s3_client():
    import boto3

    region = (
        os.getenv("S3_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "ap-south-1"
    )
    return boto3.client("s3", region_name=region)


def upload_run_traces(
    run_id: str,
    *,
    bucket: Optional[str] = None,
    local_dir: Optional[Path] = None,
    date: Optional[str] = None,
) -> Optional[str]:
    """Upload a run's trace files to S3. Returns the s3:// prefix, or None when
    disabled (no bucket) or on any failure (logged, never raised)."""
    bucket = bucket or os.getenv("TRACE_S3_BUCKET")
    if not bucket:
        return None  # tracing→S3 disabled; local JSONL still captured

    src = Path(local_dir) if local_dir else trace_dir(run_id)
    if not src.exists():
        logger.warning(f"[trace] s3 upload skipped — no trace dir at {src}")
        return None

    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    root = os.getenv("TRACE_S3_PREFIX", "traces").strip("/")
    prefix = f"{root}/dt={date}/run={run_id}"

    try:
        s3 = _s3_client()  # lazy boto3; region from S3_REGION/AWS_DEFAULT_REGION
        uploaded = 0
        for fname in _FILES:
            p = src / fname
            if p.exists():
                s3.upload_file(str(p), bucket, f"{prefix}/{fname}")
                uploaded += 1
        logger.info(
            f"[trace] uploaded {uploaded} trace file(s) to s3://{bucket}/{prefix}/"
        )
        return f"s3://{bucket}/{prefix}/"
    except Exception as exc:  # noqa: BLE001 — upload must never break the run
        logger.warning(f"[trace] s3 upload failed: {exc}")
        return None


def upload_run_logs(
    run_id: str,
    log_dir,
    *,
    bucket: Optional[str] = None,
    date: Optional[str] = None,
) -> Optional[str]:
    """Upload a run's human-readable stage logs (the combo dir's
    ``*.stdout``/``*.stderr``/``*.log``/``*.json`` — incl. the live
    ``04_tasks.evals.log`` / ``04_tasks.e2b_gate.log`` and ``summary.json``) to
    ``<prefix>/dt=<date>/run=<run_id>/logs/<combo>/``.

    Called from ``run_pipeline`` at end-of-run (the only point where all logs are
    finalized). Env-gated on ``TRACE_S3_BUCKET``; returns the s3:// prefix, or
    None when disabled or on any failure (logged, never raised)."""
    bucket = bucket or os.getenv("TRACE_S3_BUCKET")
    if not bucket:
        return None

    log_dir = Path(log_dir)
    if not log_dir.exists():
        logger.warning(f"[trace] log upload skipped — no dir at {log_dir}")
        return None

    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    root = os.getenv("TRACE_S3_PREFIX", "traces").strip("/")
    prefix = f"{root}/dt={date}/run={run_id}/logs/{log_dir.name}"

    try:
        s3 = _s3_client()
        uploaded = 0
        for p in sorted(log_dir.iterdir()):
            if p.is_file() and p.suffix in _LOG_SUFFIXES:
                s3.upload_file(str(p), bucket, f"{prefix}/{p.name}")
                uploaded += 1
        logger.info(
            f"[trace] uploaded {uploaded} log file(s) to s3://{bucket}/{prefix}/"
        )
        return f"s3://{bucket}/{prefix}/"
    except Exception as exc:  # noqa: BLE001 — upload must never break the run
        logger.warning(f"[trace] log upload failed: {exc}")
        return None
