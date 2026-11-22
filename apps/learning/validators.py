"""Validation helpers for CyberQuest lesson media.

These validators keep uploads small, recognisable and local to the project's
media directory. External URLs are never fetched by the server; they are only
checked before being handed to the browser's HTML5 video player.
"""

from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError

VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".ogv"}
VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "video/ogg",
    "application/ogg",
}
CAPTION_EXTENSIONS = {".vtt"}
MAX_VIDEO_UPLOAD_BYTES = 250 * 1024 * 1024
MAX_CAPTION_UPLOAD_BYTES = 1024 * 1024

_MAGIC_MP4 = b"ftyp"
_MAGIC_WEBM = b"\x1a\x45\xdf\xa3"
_MAGIC_OGG = b"OggS"


def _read_header(upload, length=12):
    """Read an upload header without changing the file position."""
    if not hasattr(upload, "read") or not hasattr(upload, "seek"):
        return b""
    position = upload.tell()
    try:
        return upload.read(length)
    finally:
        upload.seek(position)


def validate_lesson_video_file(upload):
    """Accept only small, plausibly valid MP4/WebM/Ogg video uploads."""
    extension = Path(upload.name or "").suffix.lower()
    if extension not in VIDEO_EXTENSIONS:
        raise ValidationError(
            "Unsupported video file type. Upload an MP4, WebM or Ogg video."
        )

    size = getattr(upload, "size", None)
    if size is not None and size > MAX_VIDEO_UPLOAD_BYTES:
        raise ValidationError("Lesson videos must be 250 MB or smaller.")

    content_type = (getattr(upload, "content_type", "") or "").split(";")[0]
    content_type = content_type.strip().lower()
    if content_type and content_type not in VIDEO_CONTENT_TYPES:
        raise ValidationError("The uploaded file does not have a video content type.")

    header = _read_header(upload)
    if extension == ".mp4" and _MAGIC_MP4 not in header:
        raise ValidationError("This file does not look like a valid MP4 video.")
    if extension == ".webm" and not header.startswith(_MAGIC_WEBM):
        raise ValidationError("This file does not look like a valid WebM video.")
    if extension in {".ogg", ".ogv"} and not header.startswith(_MAGIC_OGG):
        raise ValidationError("This file does not look like a valid Ogg video.")


def validate_lesson_caption_file(upload):
    """Accept only small WebVTT caption files."""
    extension = Path(upload.name or "").suffix.lower()
    if extension not in CAPTION_EXTENSIONS:
        raise ValidationError("Caption files must use the .vtt extension.")

    size = getattr(upload, "size", None)
    if size is not None and size > MAX_CAPTION_UPLOAD_BYTES:
        raise ValidationError("Caption files must be 1 MB or smaller.")

    header = _read_header(upload, 256).lstrip(b"\xef\xbb\xbf \t\r\n")
    if not header.startswith(b"WEBVTT"):
        raise ValidationError("Caption files must begin with WEBVTT.")


def validate_lesson_video_url(value):
    """Allow only direct HTTP(S) video files from permitted hosts."""
    if not value:
        return

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("Video URLs must use http or https.")
    if parsed.username or parsed.password:
        raise ValidationError("Video URLs must not include credentials.")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValidationError("Enter a complete video URL.")

    allowed_hosts = {
        str(item).lower() for item in getattr(settings, "LESSON_VIDEO_ALLOWED_HOSTS", [])
    }
    if allowed_hosts and host not in allowed_hosts:
        raise ValidationError("That video host is not permitted.")

    path = parsed.path.lower()
    if not path.endswith(tuple(VIDEO_EXTENSIONS)):
        raise ValidationError("Video URLs must point directly to an MP4, WebM or Ogg file.")
