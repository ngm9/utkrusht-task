"""Canonical Supabase client factory (service_role-preferring).

Lifted from ``generators/task/persistence.py`` so the task-builder app, the
task-generation persistence layer, and any other consumer share ONE client
factory instead of duplicating it. Prefers the ``service_role`` key (bypasses
RLS for the v1 tables); falls back to the anon key where service_role isn't
provisioned.

Note: this is NOT the same as the anon-only competency reader in
``generators/input_files/generator.py`` (``init_supabase`` there) — that one is
intentionally anon-scoped for the legacy competency tables and is kept separate.
"""
from __future__ import annotations

import os

from supabase import Client, create_client


def init_supabase(env: str = "dev") -> Client:
    """Initialise a Supabase client for the dev or prod environment.

    Prefers the ``service_role`` key when present — it bypasses RLS, which is
    needed for the v1 task-builder tables (``conversations``,
    ``generation_jobs``, ``generated_scenarios``, ``templates``,
    ``task_template_match``) that carry ``service_role_all`` policies. Falls back
    to the anon key for environments where the service-role key isn't provisioned
    (CI smoke tests, contributors without prod access).
    """
    suffix = "DEV" if env == "dev" else ""
    url = os.getenv(f"SUPABASE_URL_APTITUDETESTS{suffix}")
    key = (
        os.getenv(f"SUPABASE_SERVICE_ROLE_KEY_APTITUDETESTS{suffix}")
        or os.getenv(f"SUPABASE_API_KEY_APTITUDETESTS{suffix}")
    )

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")

    return create_client(url, key)
