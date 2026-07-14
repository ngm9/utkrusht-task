"""Logging bootstrap for the task_builder service.

Mirrors the Utkrushta backend pattern (notifications/logging_setup.py):
stdout logging always; Better Stack (Logtail) shipping is added only when
BETTERSTACK_SOURCE_TOKEN is set, so local runs need no config.
"""
from __future__ import annotations

import logging
import os

from logtail import LogtailHandler

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    _configured = True

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    token = os.environ.get("BETTERSTACK_SOURCE_TOKEN", "").strip()
    if not token:
        return

    host = os.environ.get("BETTERSTACK_INGESTING_HOST", "").strip()
    kwargs = {"source_token": token}
    if host:
        kwargs["host"] = host
    logging.getLogger().addHandler(LogtailHandler(**kwargs))
