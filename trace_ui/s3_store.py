"""trace_ui.s3_store — surface completed runs archived in S3.

The pipeline uploads each run's stage logs + JSONL traces to
``s3://<TRACE_S3_BUCKET>/<TRACE_S3_PREFIX|traces>/dt=<date>/combo=<combo>/run=<ts>/``:

  * run root : ``llm_calls.jsonl``, ``stages.jsonl``, ``manifest.json``
  * ``logs/`` : ``<stage>.stdout`` / ``.stderr`` / ``.log`` + ``summary.json``

This lets the trace_ui show those runs even when the viewer has no local
``.task_agent_runs`` copy (a teammate opening the UI). Strategy: list S3 runs for
the picker, and **materialize** a run's files into the local cache dir on first
open — every existing endpoint then works unchanged.

Env-gated on ``TRACE_S3_BUCKET``; every function is failure-isolated (returns
empty/False, never raises) so the local-only path is unaffected when S3 is off.

A trace_ui run_id is ``run-<ts>``; the S3 ``run=`` segment is the bare ``<ts>``.
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import time
from pathlib import Path

from infra.logger_config import logger

# The run index (run_id → {prefix, combo, ts}) is cached briefly: the run-picker
# polls /api/runs every few seconds, and walking dt=/combo=/run= prefixes on
# every tick would be wasteful. New completed runs appear within the TTL.
_INDEX_TTL_S = 60.0
_index_cache: dict = {"at": 0.0, "data": {}}


def s3_enabled() -> bool:
    return bool(os.getenv("TRACE_S3_BUCKET"))


def _bucket() -> str:
    return os.getenv("TRACE_S3_BUCKET", "")


def _root() -> str:
    return os.getenv("TRACE_S3_PREFIX", "traces").strip("/")


def _client():
    import boto3

    region = os.getenv("S3_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-south-1"
    return boto3.client("s3", region_name=region)


def _bare_ts(run_id: str) -> str:
    return run_id[4:] if run_id.startswith("run-") else run_id


def _read_manifest(s3, bucket: str, prefix: str) -> dict:
    """Fetch a run's ``manifest.json`` (carries task_id / task_name / competencies)
    so S3 runs show the task name in the picker and are searchable by it. One GET
    per run during the (60s-cached) index build; failure-isolated."""
    try:
        obj = s3.get_object(Bucket=bucket, Key=f"{prefix}manifest.json")
        return json.loads(obj["Body"].read())
    except Exception:  # noqa: BLE001 — manifest optional; never break the index
        return {}


def _common_prefixes(s3, bucket: str, prefix: str) -> list[str]:
    out: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []):
            out.append(cp["Prefix"])
    return out


def _build_index() -> dict:
    """Map ``run-<ts>`` → ``{prefix, combo, ts}`` by walking common prefixes.

    Depth-tolerant: descends dt=/combo= levels until it hits a ``run=<ts>``
    segment (which terminates the branch). This handles BOTH the current
    ``dt=/combo=/run=`` layout and the legacy ``dt=/run=`` layout (runs archived
    before the ``combo=`` Hive partition existed) — the latter just has
    ``combo=None``."""
    out: dict = {}
    if not s3_enabled():
        return out
    try:
        s3 = _client()
        bucket = _bucket()
        stack = [(f"{_root()}/", None)]  # (prefix, parent_segment)
        depth_guard = 0
        while stack and depth_guard < 10_000:
            depth_guard += 1
            pfx, parent = stack.pop()
            for child in _common_prefixes(s3, bucket, pfx):
                seg = child.rstrip("/").split("/")[-1]
                if seg.startswith("run="):
                    ts = seg.split("=", 1)[1]
                    combo = parent.split("=", 1)[1] if (parent or "").startswith("combo=") else None
                    mani = _read_manifest(s3, bucket, child)
                    if not combo and mani.get("competencies"):
                        combo = ", ".join(mani["competencies"])  # legacy runs w/o combo= partition
                    out[f"run-{ts}"] = {
                        "prefix": child, "combo": combo, "ts": ts,
                        "task_id": mani.get("task_id"),
                        "task_name": mani.get("task_name"),
                    }
                else:
                    stack.append((child, seg))  # dt= / combo= → descend
    except Exception as exc:  # noqa: BLE001 — S3 optional; never break the UI
        logger.warning(f"[trace_ui.s3] index build failed: {exc}")
    return out


def _index(force: bool = False) -> dict:
    if not s3_enabled():  # never serve a stale cache once S3 is turned off
        return {}
    now = time.time()
    if force or (now - _index_cache["at"]) > _INDEX_TTL_S:
        _index_cache["data"] = _build_index()
        _index_cache["at"] = now
    return _index_cache["data"]


def _ts_epoch(ts: str) -> float:
    try:
        return (datetime.datetime.strptime(ts, "%Y%m%dT%H%M%SZ")
                .replace(tzinfo=datetime.timezone.utc).timestamp())
    except ValueError:
        return 0.0


def list_s3_runs() -> list[dict]:
    """Run-picker entries for completed runs archived in S3 (same dict shape as
    ``tailer.list_runs`` entries, plus ``source='s3'``)."""
    return [
        {
            "run_id": run_id,
            "combo": info.get("combo"),
            "status": "completed",
            "started": _ts_epoch(info.get("ts", "")),
            "task_id": info.get("task_id"),
            "task_name": info.get("task_name"),
            "source": "s3",
        }
        for run_id, info in _index().items()
    ]


def materialize_run(run_id: str, runs_dir) -> bool:
    """Download an S3 run's files into ``runs_dir/run-<ts>/`` so the existing
    local endpoints can serve it.

    Layout written: ``logs/*`` → ``<combo>/*`` and the run-root trace files
    (``llm_calls.jsonl`` / ``stages.jsonl`` / ``manifest.json``) → ``traces/*``.

    Idempotent + crash-safe: downloads into a temp dir and atomically renames it
    into place, so ``run_dir`` only ever exists when fully populated. Returns True
    when the run is available locally afterwards; False when it isn't in S3 / S3
    is disabled / download failed.
    """
    if not s3_enabled():
        return False
    runs_dir = Path(runs_dir)
    ts = _bare_ts(run_id)
    run_dir = runs_dir / f"run-{ts}"
    if run_dir.exists():
        return True  # already local or previously materialized (atomic → complete)

    info = _index().get(f"run-{ts}") or _index(force=True).get(f"run-{ts}")
    if not info:
        return False

    prefix = info["prefix"]
    combo = info.get("combo") or "adhoc"  # legacy runs (no combo= partition)
    tmp_parent = runs_dir / f".s3tmp-{ts}-{os.getpid()}"
    tmp_run = tmp_parent / f"run-{ts}"
    try:
        s3 = _client()
        bucket = _bucket()
        combo_dir = tmp_run / combo
        traces_dir = tmp_run / "traces"
        combo_dir.mkdir(parents=True, exist_ok=True)
        traces_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                rel = key[len(prefix):]  # "logs/04_tasks.stderr" | "manifest.json"
                if not rel or rel.endswith("/"):
                    continue
                dest = (combo_dir / rel[len("logs/"):]) if rel.startswith("logs/") else (traces_dir / rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(bucket, key, str(dest))
                n += 1
        if n == 0:
            shutil.rmtree(tmp_parent, ignore_errors=True)
            return False
        try:
            os.replace(tmp_run, run_dir)  # atomic publish (same filesystem)
        except OSError:
            # another request materialized it first, or a partial collision
            return run_dir.exists()
        finally:
            shutil.rmtree(tmp_parent, ignore_errors=True)
        logger.info(f"[trace_ui.s3] materialized {run_id} ({n} files) from {prefix}")
        return True
    except Exception as exc:  # noqa: BLE001 — never break the UI on an S3 hiccup
        logger.warning(f"[trace_ui.s3] materialize {run_id} failed: {exc}")
        shutil.rmtree(tmp_parent, ignore_errors=True)
        return run_dir.exists()
