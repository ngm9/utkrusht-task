"""Object-storage adapters for the task-builder pipeline.

Right now there's only the S3 implementation. If we ever add a second
backend (Supabase Storage, R2, etc.) it goes here as a sibling module
exposing the same upload_json/upload_text/key_for_run/is_enabled API.
"""
from infra.storage import s3  # noqa: F401  re-exported for callers
