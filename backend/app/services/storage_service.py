"""Handles persisting uploaded media files to disk.

Storage is a local directory in this reference implementation, mounted as a
Docker volume in docker-compose.yml. Swapping this for S3 in production
only requires changing `save_upload` since callers only depend on the
returned storage path, not on the filesystem directly.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings

IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/webp"}
VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}


def get_media_type(content_type: str | None) -> str | None:
    if content_type in IMAGE_CONTENT_TYPES:
        return "image"
    if content_type in VIDEO_CONTENT_TYPES:
        return "video"
    return None


def save_upload(upload: UploadFile, contents: bytes) -> str:
    """Save the already-read file contents to the media storage directory
    and return the absolute path they were written to."""
    settings = get_settings()
    storage_dir = Path(settings.media_storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(upload.filename or "").suffix or ""
    unique_name = f"{uuid.uuid4()}{extension}"
    destination = storage_dir / unique_name

    with open(destination, "wb") as handle:
        handle.write(contents)

    return str(destination)
