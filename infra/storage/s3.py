"""S3 uploader for task-builder generated artifacts.

Mirrors the boto3 pattern used by the backend Airflow DAGs
(`Utkrushta/airflow/dags/task_session_analysis_dag.py`) — plain
`put_object` with `ACL='public-read'` and `ContentType` set per blob.
Reads AWS creds + bucket/region from environment so the same code path
works from the local worker, the docker worker, and CI.

Dev fallback: when AWS_ACCESS_KEY_ID is unset, `is_enabled()` returns
False and `upload_*` raises `StorageDisabledError`. Callers are expected
to gate uploads on `is_enabled()` so missing creds degrade gracefully to
local-only writes instead of crashing the pipeline.
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Any

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)


DEFAULT_REGION = "ap-south-1"
DEFAULT_PREFIX = "task_builder"


class StorageDisabledError(RuntimeError):
    """Raised when an upload is attempted without configured AWS creds."""


def is_enabled() -> bool:
    """True iff we have the env vars required to talk to S3."""
    return bool(os.getenv("AWS_ACCESS_KEY_ID")) and bool(
        os.getenv("AWS_SECRET_ACCESS_KEY")
    )


def bucket_for(env: str) -> str:
    """Resolve the bucket name for ``env`` (``"dev"`` or ``"prod"``).

    Prefers env-suffixed names (``S3_BUCKET_DEV`` / ``S3_BUCKET_PROD``)
    so dev and prod can coexist in the same process. Falls back to the
    single ``S3_BUCKET`` env var to stay compatible with the backend's
    convention.
    """
    suffix = "_PROD" if env == "prod" else "_DEV"
    return (
        os.getenv(f"S3_BUCKET{suffix}")
        or os.getenv("S3_BUCKET")
        or _missing("S3_BUCKET")
    )


def region() -> str:
    return os.getenv("S3_REGION") or DEFAULT_REGION


def public_url(bucket: str, key: str) -> str:
    """Construct the public HTTPS URL for an object.

    Matches the URL shape produced by ``upload_file_to_s3`` in the
    backend's ``flask_service/util.py``.
    """
    return f"https://{bucket}.s3.{region()}.amazonaws.com/{key}"


def key_for_run(job_id: str, kind: str, *, ext: str = "json") -> str:
    """Deterministic S3 key for a per-job artifact.

    Layout: ``{prefix}/{job_id}/{kind}.{ext}``. The job-scoped prefix
    makes retention rules trivial (delete prefix older than N days) and
    avoids collisions across concurrent runs.
    """
    prefix = os.getenv("S3_TASK_BUILDER_PREFIX") or DEFAULT_PREFIX
    return f"{prefix}/{job_id}/{kind}.{ext}"


def upload_json(
    bucket: str,
    key: str,
    data: Any,
    *,
    acl: str = "public-read",
) -> str:
    """Serialize ``data`` to JSON and upload. Returns the public URL."""
    body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    return upload_bytes(
        bucket, key, body,
        content_type="application/json; charset=utf-8",
        acl=acl,
    )


def upload_text(
    bucket: str,
    key: str,
    text: str,
    *,
    content_type: str = "text/plain; charset=utf-8",
    acl: str = "public-read",
) -> str:
    """Upload a plain-text blob (e.g. a log bundle). Returns public URL."""
    return upload_bytes(
        bucket, key, text.encode("utf-8"),
        content_type=content_type, acl=acl,
    )


def upload_bytes(
    bucket: str,
    key: str,
    body: bytes,
    *,
    content_type: str,
    acl: str = "public-read",
) -> str:
    """Low-level byte upload. Use upload_json / upload_text instead when
    possible — they encode for you.
    """
    if not is_enabled():
        raise StorageDisabledError(
            "AWS creds missing — set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"
        )
    client = _client()
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
        ACL=acl,
    )
    url = public_url(bucket, key)
    logger.info("s3 upload ok bucket=%s key=%s bytes=%d", bucket, key, len(body))
    return url


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _client():
    """boto3 S3 client memoized for the process. Reads creds from env."""
    return boto3.client(
        "s3",
        region_name=region(),
        config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    )


def reset_client_cache() -> None:
    """Drop the cached client. Call from tests or after env rotation."""
    _client.cache_clear()


def _missing(name: str) -> str:
    raise RuntimeError(f"missing required env var: {name}")
