"""process_image — extracts an embedded image from the source doc and uploads it to Drive.

Called directly by extractor._prefetch_images() before the LLM call, once per embedded
image in the BriefAST. Returns Drive thumbnail and full-res URLs that are embedded
in the LLM prompt so the LLM can reference them in the task markdown without needing
to make any tool calls itself.

Does NOT run vision-LLM analysis — image understanding is downstream's concern.
"""
from __future__ import annotations

import io
import json
import zipfile
from hashlib import sha256
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class ProcessImageInput(BaseModel):
    image_ref: str = Field(
        ...,
        description="Stable image identifier from the BriefAST (e.g. 'image_0').",
    )


class ProcessImageOutput(BaseModel):
    drive_thumbnail_url: str
    drive_view_url: str
    drive_file_id: str
    width_px: int
    height_px: int
    content_hash: str
    cached: bool = False


def _get_cache_path(output_dir: Path, content_hash: str) -> Path:
    cache_dir = output_dir.parent / "parser_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{content_hash}.drive.json"


def _extract_image_bytes(brief_path: Path, image_ref: str) -> tuple[bytes, str]:
    """Resolve image_ref → (bytes, original_extension) by reading the source doc.

    For .docx briefs the image_ref is `"image_N"` and we read from the
    `word/media/` zip entry at index N.
    """
    if brief_path.suffix.lower() == ".docx":
        with zipfile.ZipFile(brief_path) as zf:
            media_entries = [n for n in zf.namelist() if n.startswith("word/media/")]
            if not image_ref.startswith("image_"):
                raise ValueError(f"Unknown image_ref format for .docx: {image_ref!r}")
            idx = int(image_ref.split("_", 1)[1])
            if idx >= len(media_entries):
                raise ValueError(f"image_ref {image_ref!r} out of range for {brief_path}")
            entry = media_entries[idx]
            return zf.read(entry), Path(entry).suffix.lower()
    raise NotImplementedError(
        f"Image extraction not yet supported for source format {brief_path.suffix!r}"
    )


def _image_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) from image bytes via Pillow, or (0, 0) if unavailable."""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as img:
            return img.size
    except Exception:
        return (0, 0)


def _upload_to_drive(data: bytes, filename: str) -> tuple[str, str, str]:
    """Upload bytes to the shared Drive task-resources folder. Returns (file_id, view, thumbnail)."""
    # Imports deferred so the parser still imports cleanly without Google creds
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from flows.non_tech.google_utils import (
        get_google_credentials,
        get_or_create_task_resources_folder,
        _share_publicly,
    )

    creds = get_google_credentials()
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    parent_folder_id = get_or_create_task_resources_folder(drive)

    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="image/png", resumable=False)
    created = drive.files().create(
        body={"name": filename, "parents": [parent_folder_id], "mimeType": "image/png"},
        media_body=media,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    file_id = created["id"]
    _share_publicly(drive, file_id)
    view = f"https://drive.google.com/file/d/{file_id}/view"
    thumbnail = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200"
    return file_id, view, thumbnail


def process_image(inp: ProcessImageInput, output_dir: Optional[Path] = None) -> ProcessImageOutput:
    """Extract the image from the source doc, upload to Drive, and return its URLs.

    Called directly by extractor._prefetch_images() before the LLM call.
    Checks the on-disk cache first — if the same image (by content hash) was
    already uploaded in a previous run, returns the cached Drive URLs immediately.
    """
    if output_dir is None:
        raise ValueError("process_image requires an output_dir")
    output_dir = Path(output_dir)

    # Recover the brief path from the run's marker file written by the CLI.
    brief_path = _read_brief_path(output_dir)
    data, ext = _extract_image_bytes(brief_path, inp.image_ref)
    content_hash = sha256(data).hexdigest()

    cache_path = _get_cache_path(output_dir, content_hash)
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return ProcessImageOutput(**cached, cached=True)

    width, height = _image_dimensions(data)
    filename = f"{content_hash[:12]}{ext or '.png'}"
    file_id, view, thumbnail = _upload_to_drive(data, filename)

    result = ProcessImageOutput(
        drive_thumbnail_url=thumbnail,
        drive_view_url=view,
        drive_file_id=file_id,
        width_px=width,
        height_px=height,
        content_hash=content_hash,
        cached=False,
    )
    # Cache (without `cached=True` so future hits flip the flag explicitly)
    payload = result.model_dump()
    payload.pop("cached", None)
    cache_path.write_text(json.dumps(payload), encoding="utf-8")
    return result


def _read_brief_path(output_dir: Path) -> Path:
    """Recover the source-brief path that the CLI wrote at run start."""
    marker = output_dir / ".brief_path"
    if not marker.exists():
        raise RuntimeError(
            f"output_dir {output_dir} missing .brief_path marker — "
            f"was the CLI run normally?"
        )
    return Path(marker.read_text(encoding="utf-8").strip())
