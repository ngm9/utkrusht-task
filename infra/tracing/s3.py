"""End-of-run upload of a run's trace JSONL to S3 — the training corpus.

Env-gated on ``TRACE_S3_BUCKET`` (no bucket → no-op, returns None) and
failure-isolated (an upload error logs a warning and returns None; it never
breaks the pipeline). Objects are partitioned for ML consumption:

    s3://<bucket>/traces/dt=<YYYY-MM-DD>/combo=<slug>/run=<run_id>/{llm_calls,stages}.jsonl
    s3://<bucket>/traces/dt=<YYYY-MM-DD>/combo=<slug>/run=<run_id>/manifest.json

The ``combo`` partition is the competency+level slug (e.g.
``python_redis_intermediate``), so the corpus is queryable/browsable by
competency. It is taken from the ``TRACE_COMBO`` env (set by run_pipeline),
falling back to ``adhoc`` for a standalone ``generate`` run with no combo.

``boto3`` is imported lazily so the package has no hard dependency on it.
"""
from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from typing import Optional

from infra.logger_config import logger
from infra.tracing.sink import trace_dir

_FILES = ("llm_calls.jsonl", "stages.jsonl", "manifest.json")
# Human-readable stage logs uploaded alongside the JSONL traces.
_LOG_SUFFIXES = (".stdout", ".stderr", ".log", ".json")

# Competency/combo slug → safe S3 key segment. Empty → "adhoc" (e.g. a
# standalone `generate` run with no pipeline-provided combo).
_COMBO_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_combo(combo: Optional[str]) -> str:
    if not combo:
        return "adhoc"
    slug = _COMBO_SANITIZE_RE.sub("-", combo).strip("-._")
    return slug or "adhoc"


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
    combo: Optional[str] = None,
) -> Optional[str]:
    """Upload a run's trace files to S3. Returns the s3:// prefix, or None when
    disabled (no bucket) or on any failure (logged, never raised).

    ``combo`` (the competency+level slug) becomes a Hive partition; it defaults
    to the ``TRACE_COMBO`` env, then ``adhoc``."""
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
    combo = _safe_combo(combo or os.getenv("TRACE_COMBO"))
    prefix = f"{root}/dt={date}/combo={combo}/run={run_id}"

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
    combo: Optional[str] = None,
) -> Optional[str]:
    """Upload a run's human-readable stage logs (the combo dir's
    ``*.stdout``/``*.stderr``/``*.log``/``*.json`` — incl. the live
    ``04_tasks.evals.log`` / ``04_tasks.e2b_gate.log`` and ``summary.json``) to
    ``<prefix>/dt=<date>/combo=<slug>/run=<run_id>/logs/``.

    ``combo`` defaults to the ``TRACE_COMBO`` env, then the log dir's own name
    (which IS the combo dir), then ``adhoc``.

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
    combo = _safe_combo(combo or os.getenv("TRACE_COMBO") or log_dir.name)
    prefix = f"{root}/dt={date}/combo={combo}/run={run_id}/logs"

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


def upload_solvability_run(
    slug: str,
    *,
    task_id: Optional[str] = None,
    bucket: Optional[str] = None,
    date: Optional[str] = None,
    run_dir: Optional[Path] = None,
    legacy_dir: Optional[Path] = None,
) -> Optional[str]:
    """Upload one `task-solvability` skill run to S3 — the audit-flow counterpart
    to ``upload_run_traces``/``upload_run_logs`` above. Same env gate
    (``TRACE_S3_BUCKET``), same failure isolation (logs a warning and returns
    None; never raises).

    Uploads, if present:
      ``solvability_runs/<slug>/**``   (summary.md, notes.md, result.json,
                                        solution.diff, solve.webm, frames/*.png)
      ``.task_agent_runs/solvable/<task_id>.diff``
      ``.task_agent_runs/solvable/recordings/<task_id>/**``

    to ``s3://<bucket>/solvability/dt=<date>/task=<slug>/...``.
    """
    bucket = bucket or os.getenv("TRACE_S3_BUCKET")
    if not bucket:
        return None

    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    slug_safe = _safe_combo(slug)
    prefix = f"solvability/dt={date}/task={slug_safe}"

    run_dir = Path(run_dir) if run_dir else Path("solvability_runs") / slug
    legacy_dir = Path(legacy_dir) if legacy_dir else Path(".task_agent_runs/solvable")
    targets = [(run_dir, "")]
    if task_id:
        targets.append((legacy_dir / f"{task_id}.diff", ""))
        targets.append((legacy_dir / "recordings" / task_id, "recordings"))

    try:
        s3 = _s3_client()
        uploaded = 0
        for src, sub in targets:
            if not src.exists():
                continue
            if src.is_file():
                key = f"{prefix}/{sub}/{src.name}" if sub else f"{prefix}/{src.name}"
                s3.upload_file(str(src), bucket, key)
                uploaded += 1
                continue
            for p in sorted(src.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(src).as_posix()
                    key = f"{prefix}/{sub}/{rel}" if sub else f"{prefix}/{rel}"
                    s3.upload_file(str(p), bucket, key)
                    uploaded += 1

        if uploaded == 0:
            logger.warning(f"[solvability] s3 upload skipped — no artifacts found for slug={slug_safe}")
            return None
        logger.info(
            f"[solvability] uploaded {uploaded} file(s) to s3://{bucket}/{prefix}/"
        )
        return f"s3://{bucket}/{prefix}/"
    except Exception as exc:  # noqa: BLE001 — upload must never break the run
        logger.warning(f"[solvability] s3 upload failed: {exc}")
        return None


def upload_all_solvability_artifacts(
    *,
    bucket: Optional[str] = None,
    runs_dir: Optional[Path] = None,
    legacy_dir: Optional[Path] = None,
) -> Optional[str]:
    """Sync EVERY local task-solvability artifact to S3 in one shot — every
    ``solvability_runs/<slug>/`` report plus any batch-level file at its root
    (e.g. ``_batch-<date>-summary.md``), and the whole legacy
    ``.task_agent_runs/solvable/`` tree (the ``results.jsonl`` ledger, every
    ``<task_id>.diff``, every recording).

    This is deliberately NOT a loop over ``upload_solvability_run`` per slug:
    the two local trees don't share a reliable join key (most
    ``solvability_runs/<slug>/result.json`` predate the ``task_id`` field, and
    the legacy ledger is keyed by ``task_id`` alone), so most of
    ``.task_agent_runs/solvable/`` can't be attributed back to a slug. Lands
    under ``solvability/backfill/...`` — a separate namespace from
    ``upload_solvability_run``'s ``solvability/dt=<date>/task=<slug>/...`` —
    so a one-time flat dump never collides with the partitioned per-run
    corpus. Use for backfilling runs that predate S3 wiring, or a periodic
    full-sync cron. Same env gate (``TRACE_S3_BUCKET``) and failure isolation
    as the rest of this module.
    """
    bucket = bucket or os.getenv("TRACE_S3_BUCKET")
    if not bucket:
        return None

    runs_dir = Path(runs_dir) if runs_dir else Path("solvability_runs")
    legacy_dir = Path(legacy_dir) if legacy_dir else Path(".task_agent_runs/solvable")
    targets = [(runs_dir, "reports"), (legacy_dir, "legacy")]

    try:
        s3 = _s3_client()
        uploaded = 0
        for src, sub in targets:
            if not src.exists():
                continue
            for p in sorted(src.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(src).as_posix()
                    s3.upload_file(str(p), bucket, f"solvability/backfill/{sub}/{rel}")
                    uploaded += 1

        if uploaded == 0:
            logger.warning("[solvability] full sync skipped — no local artifacts found")
            return None
        logger.info(f"[solvability] synced {uploaded} file(s) to s3://{bucket}/solvability/backfill/")
        return f"s3://{bucket}/solvability/backfill/"
    except Exception as exc:  # noqa: BLE001 — upload must never break the run
        logger.warning(f"[solvability] full sync failed: {exc}")
        return None
