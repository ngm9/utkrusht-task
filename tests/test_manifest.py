"""Tests for ``infra/e2b/manifest.py``.

Covers the three primitives:

* :func:`compute_manifest_hash` — deterministic, key-order-insensitive.
* :func:`write_manifest`        — creates both artifacts with expected contents.
* :func:`read_manifest`         — round-trips.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from infra.e2b.manifest import (
    compute_manifest_hash,
    read_manifest,
    write_manifest,
)


# ---------------------------------------------------------------------------
# compute_manifest_hash
# ---------------------------------------------------------------------------


def test_compute_manifest_hash_is_deterministic() -> None:
    """Same dict (same content) must hash to the same value across calls."""
    manifest = {"template_id": "utkrusht-python", "primary_runtime": "python"}
    assert compute_manifest_hash(manifest) == compute_manifest_hash(manifest)


def test_compute_manifest_hash_is_key_order_insensitive() -> None:
    """Two dicts differing only in key insertion order must hash identically.

    This is the core durability property: callers can construct manifests in
    any order and the artifact on disk will round-trip to the same hash.
    """
    a = {"template_id": "utkrusht-python", "primary_runtime": "python"}
    b = {"primary_runtime": "python", "template_id": "utkrusht-python"}
    assert compute_manifest_hash(a) == compute_manifest_hash(b)


def test_compute_manifest_hash_is_key_order_insensitive_nested() -> None:
    """Nested dicts (capabilities.language_versions) also key-order-insensitive."""
    a = {
        "template_id": "x",
        "capabilities": {"language_versions": {"python": "3.13"}, "tags": []},
    }
    b = {
        "capabilities": {"tags": [], "language_versions": {"python": "3.13"}},
        "template_id": "x",
    }
    assert compute_manifest_hash(a) == compute_manifest_hash(b)


def test_compute_manifest_hash_differs_for_different_manifests() -> None:
    """Different content must produce different hashes."""
    a = {"template_id": "utkrusht-python"}
    b = {"template_id": "utkrusht-node"}
    assert compute_manifest_hash(a) != compute_manifest_hash(b)


def test_compute_manifest_hash_is_sha256_hex() -> None:
    """Output is a 64-char lowercase hex SHA256 digest."""
    digest = compute_manifest_hash({"k": "v"})
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


# ---------------------------------------------------------------------------
# write_manifest
# ---------------------------------------------------------------------------


def test_write_manifest_creates_both_files(tmp_path: Path) -> None:
    manifest = {"template_id": "utkrusht-python", "status": "built"}
    result = write_manifest(tmp_path, manifest)

    manifest_path = tmp_path / "manifest.json"
    hash_path = tmp_path / "manifest_hash"

    assert manifest_path.exists()
    assert hash_path.exists()
    assert result["manifest_path"] == str(manifest_path)
    assert result["hash_path"] == str(hash_path)
    assert result["manifest_hash"] == compute_manifest_hash(manifest)


def test_write_manifest_json_is_pretty_sorted(tmp_path: Path) -> None:
    """``manifest.json`` is human-readable: indent=2, sort_keys=True."""
    manifest = {"b": 2, "a": 1}
    write_manifest(tmp_path, manifest)

    raw = (tmp_path / "manifest.json").read_text(encoding="utf-8")
    # Sorted: "a" key appears before "b" key in the text.
    assert raw.index('"a"') < raw.index('"b"')
    # Pretty-printed: at least one newline + 2-space indent.
    assert "\n  " in raw
    # Parses back to the same logical content.
    assert json.loads(raw) == manifest


def test_write_manifest_hash_has_no_trailing_newline(tmp_path: Path) -> None:
    """The hash file is the raw hex digest, no trailing newline."""
    manifest = {"template_id": "x"}
    write_manifest(tmp_path, manifest)
    raw = (tmp_path / "manifest_hash").read_text(encoding="utf-8")
    assert raw == compute_manifest_hash(manifest)
    assert not raw.endswith("\n")


def test_write_manifest_creates_missing_template_dir(tmp_path: Path) -> None:
    """If the template_dir doesn't exist yet, it's created."""
    target = tmp_path / "new_template_dir"
    assert not target.exists()
    write_manifest(target, {"template_id": "x"})
    assert (target / "manifest.json").exists()
    assert (target / "manifest_hash").exists()


# ---------------------------------------------------------------------------
# read_manifest
# ---------------------------------------------------------------------------


def test_read_manifest_round_trips(tmp_path: Path) -> None:
    original = {
        "template_id": "utkrusht-python",
        "primary_runtime": "python",
        "capabilities": {
            "language_versions": {"python": "3.13"},
            "frameworks": ["fastapi", "django"],
            "requires": {"browser": False, "gpu": False},
        },
    }
    write_result = write_manifest(tmp_path, original)
    loaded, stored_hash = read_manifest(tmp_path)

    assert loaded == original
    assert stored_hash == write_result["manifest_hash"]
    assert stored_hash == compute_manifest_hash(loaded)


def test_read_manifest_missing_raises(tmp_path: Path) -> None:
    """Reading from a directory without a manifest raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_manifest(tmp_path)
