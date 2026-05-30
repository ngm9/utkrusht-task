"""Unit tests for infra.storage.s3.

These tests never touch real S3 — boto3's ``put_object`` is replaced
with a stub that records the call. Real-S3 behaviour is verified
manually via the worker once.
"""
from __future__ import annotations

import json

import pytest

from infra.storage import s3


@pytest.fixture(autouse=True)
def _clear_cached_client():
    """Force a fresh client per test so env changes take effect."""
    s3.reset_client_cache()
    yield
    s3.reset_client_cache()


@pytest.fixture
def aws_env(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret")
    monkeypatch.setenv("S3_REGION", "ap-south-1")
    monkeypatch.setenv("S3_BUCKET", "aptitudetestsdev")
    monkeypatch.delenv("S3_BUCKET_DEV", raising=False)
    monkeypatch.delenv("S3_BUCKET_PROD", raising=False)


class _StubClient:
    """Records put_object calls without touching the network."""

    def __init__(self):
        self.calls: list[dict] = []

    def put_object(self, **kwargs):
        self.calls.append(kwargs)
        return {"ETag": '"stub"'}


@pytest.fixture
def stub_client(monkeypatch):
    stub = _StubClient()
    monkeypatch.setattr(s3, "_client", lambda: stub)
    return stub


def test_is_enabled_false_without_creds(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    assert s3.is_enabled() is False


def test_is_enabled_true_with_creds(aws_env):
    assert s3.is_enabled() is True


def test_bucket_for_prefers_env_suffix(monkeypatch, aws_env):
    monkeypatch.setenv("S3_BUCKET_DEV", "dev-bucket")
    monkeypatch.setenv("S3_BUCKET_PROD", "prod-bucket")
    assert s3.bucket_for("dev") == "dev-bucket"
    assert s3.bucket_for("prod") == "prod-bucket"


def test_bucket_for_falls_back_to_unsuffixed(aws_env):
    assert s3.bucket_for("dev") == "aptitudetestsdev"


def test_key_for_run_default_layout():
    key = s3.key_for_run("abc-123", "competency")
    assert key == "task_builder/abc-123/competency.json"


def test_key_for_run_custom_extension():
    key = s3.key_for_run("abc-123", "logs", ext="txt")
    assert key == "task_builder/abc-123/logs.txt"


def test_public_url_shape(aws_env):
    url = s3.public_url("aptitudetestsdev", "task_builder/run-1/competency.json")
    assert url == (
        "https://aptitudetestsdev.s3.ap-south-1.amazonaws.com/"
        "task_builder/run-1/competency.json"
    )


def test_upload_json_serializes_and_calls_put_object(aws_env, stub_client):
    url = s3.upload_json(
        "aptitudetestsdev",
        "task_builder/run-1/competency.json",
        {"name": "React", "level": "INTERMEDIATE"},
    )
    assert url.endswith("/competency.json")

    assert len(stub_client.calls) == 1
    call = stub_client.calls[0]
    assert call["Bucket"] == "aptitudetestsdev"
    assert call["Key"] == "task_builder/run-1/competency.json"
    assert call["ContentType"].startswith("application/json")
    assert call["ACL"] == "public-read"
    decoded = json.loads(call["Body"].decode("utf-8"))
    assert decoded == {"name": "React", "level": "INTERMEDIATE"}


def test_upload_text_uses_text_content_type(aws_env, stub_client):
    url = s3.upload_text(
        "aptitudetestsdev",
        "task_builder/run-1/logs.txt",
        "stage 01 output\nstage 02 output\n",
    )
    assert url.endswith("/logs.txt")
    call = stub_client.calls[0]
    assert call["ContentType"].startswith("text/plain")
    assert call["Body"] == b"stage 01 output\nstage 02 output\n"


def test_upload_raises_when_disabled(monkeypatch, stub_client):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    with pytest.raises(s3.StorageDisabledError):
        s3.upload_json("any-bucket", "any/key.json", {})


def test_upload_bytes_passthrough(aws_env, stub_client):
    url = s3.upload_bytes(
        "aptitudetestsdev",
        "task_builder/run-1/raw.bin",
        b"\x00\x01\x02",
        content_type="application/octet-stream",
    )
    assert url.endswith("/raw.bin")
    call = stub_client.calls[0]
    assert call["Body"] == b"\x00\x01\x02"
    assert call["ContentType"] == "application/octet-stream"
