"""E2B template manifest helpers.

A *manifest* is the source-of-truth declaration of what a template provides
(language versions, frameworks, datastores, eval commands, ...). It lives in
each template directory as ``manifest.json`` next to ``template.py``.

The manifest is intentionally separate from the imperative ``AsyncTemplate``
build steps so that downstream systems (the LLM classifier, the future
``templates`` SQL table, drift checks) can read template *capabilities*
without executing Python or shelling out to E2B.

This module provides three primitives:

* :func:`compute_manifest_hash` — canonical-JSON SHA256 of a manifest dict.
* :func:`write_manifest`       — persist ``manifest.json`` + ``manifest_hash``.
* :func:`read_manifest`        — round-trip read for drift checks.

Phase 0 of ``docs/plans/2026-05-27-unified-classifier-template-schema.md``
introduces the artifacts; CI gate enforcement is deferred (honor system
until GitHub Actions is configured separately).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_MANIFEST_FILENAME = "manifest.json"
_HASH_FILENAME = "manifest_hash"


def compute_manifest_hash(manifest: dict) -> str:
    """Return the SHA256 hex digest of *manifest* in canonical JSON form.

    Canonical form is ``json.dumps(..., sort_keys=True, separators=(",", ":"))``
    so that two semantically-equal dicts (differing only in key insertion
    order or whitespace) hash to the same digest.
    """
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_manifest(template_dir: Path, manifest: dict) -> dict:
    """Write ``manifest.json`` and ``manifest_hash`` into *template_dir*.

    ``manifest.json`` is pretty-printed (``indent=2, sort_keys=True``) for
    human review; ``manifest_hash`` holds the canonical-JSON hex digest with
    no trailing newline.

    Returns a dict suitable for logging::

        {
            "manifest_hash": "<hex>",
            "manifest_path": "<absolute path to manifest.json>",
            "hash_path":     "<absolute path to manifest_hash>",
        }
    """
    template_dir = Path(template_dir)
    template_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = template_dir / _MANIFEST_FILENAME
    hash_path = template_dir / _HASH_FILENAME

    manifest_hash = compute_manifest_hash(manifest)

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    hash_path.write_text(manifest_hash, encoding="utf-8")

    return {
        "manifest_hash": manifest_hash,
        "manifest_path": str(manifest_path),
        "hash_path": str(hash_path),
    }


def read_manifest(template_dir: Path) -> tuple[dict, str]:
    """Read ``manifest.json`` and ``manifest_hash`` from *template_dir*.

    Returns ``(manifest_dict, stored_hash)``. The caller is responsible for
    comparing ``stored_hash`` against :func:`compute_manifest_hash` on the
    dict if they want a drift check — this primitive only reads.
    """
    template_dir = Path(template_dir)
    manifest_path = template_dir / _MANIFEST_FILENAME
    hash_path = template_dir / _HASH_FILENAME

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stored_hash = hash_path.read_text(encoding="utf-8").strip()
    return manifest, stored_hash
