# ErrorFile/Detection/MediaInspector.py
"""Audio/video inspection utilities."""

from mutagen import File
from mutagen.mp3 import HeaderNotFoundError
from mutagen.mp4 import MP4StreamInfoError

from ..report import (
    TAG_CORRUPTED,
    TAG_INVALID_FORMAT,
    TAG_IO_ERROR,
    fail_finding,
    ok_finding,
)

MEDIA_TYPE_HINTS = {
    ".mp3": "MP3 audio",
    ".mp4": "MP4 video",
    ".flac": "FLAC audio",
    ".ogg": "OGG audio",
    ".oga": "OGG audio",
}


def check_media_file(file_path, extension, mode="deep"):
    """Use Mutagen to validate media file structure."""
    try:
        audio = File(file_path)
    except Exception as exc:  # pragma: no cover - IO depends on environment
        return fail_finding(
            f"Failed to read {MEDIA_TYPE_HINTS.get(extension, 'media')} file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )

    if audio is None:
        return fail_finding(
            f"Mutagen cannot recognize {MEDIA_TYPE_HINTS.get(extension, 'media')} format.",
            TAG_INVALID_FORMAT,
        )

    try:
        stream_info = getattr(audio, "info", None)
        if stream_info is None:
            return fail_finding(
                f"Missing stream info for {MEDIA_TYPE_HINTS.get(extension, 'media')} file.",
                TAG_CORRUPTED,
            )

        _ = getattr(stream_info, "length")
        for attr in ("bitrate", "sample_rate", "channels"):
            if hasattr(stream_info, attr):
                _ = getattr(stream_info, attr)
    except HeaderNotFoundError as exc:
        return fail_finding(
            f"{MEDIA_TYPE_HINTS.get(extension, 'media')} missing audio headers: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except MP4StreamInfoError as exc:
        return fail_finding(
            f"{MEDIA_TYPE_HINTS.get(extension, 'media')} missing moov atom: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        return fail_finding(
            f"Failed to read stream info: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )

    if mode == "fast":
        return ok_finding(
            f"{MEDIA_TYPE_HINTS.get(extension, 'media')} fast check passed."
        )

    tags = getattr(audio, "tags", None)
    if tags:
        try:
            for key in list(tags.keys()):
                _ = tags.get(key)
        except Exception as exc:  # pragma: no cover
            return fail_finding(
                f"Failed to parse tags: {exc}",
                TAG_IO_ERROR,
                error=str(exc),
            )

    try:
        audio.pprint()
    except HeaderNotFoundError as exc:
        return fail_finding(
            f"{MEDIA_TYPE_HINTS.get(extension, 'media')} missing audio headers: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except MP4StreamInfoError as exc:
        return fail_finding(
            f"{MEDIA_TYPE_HINTS.get(extension, 'media')} missing moov atom: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        return fail_finding(
            f"Failed to parse metadata: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )

    return ok_finding(f"{MEDIA_TYPE_HINTS.get(extension, 'media')} deep check passed.")
