from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Dict, Optional, Tuple

TAG_OK = "ok"
TAG_CORRUPTED = "corrupted"
TAG_ENCRYPTED = "encrypted"
TAG_UNSUPPORTED = "unsupported"
TAG_INVALID_FORMAT = "invalid_format"
TAG_IO_ERROR = "io_error"
TAG_NOT_FOUND = "not_found"
TAG_UNKNOWN_ERROR = "unknown_error"
TAG_PARTIAL = "partial"
TAG_INVALID_MODE = "invalid_mode"


@dataclass(frozen=True)
class InspectionFinding:
    ok: bool
    message: str
    tags: Tuple[str, ...]
    error: Optional[str] = None


@dataclass(frozen=True)
class InspectionReport:
    file_path: str
    extension: str
    mode: str
    ok: bool
    message: str
    tags: Tuple[str, ...]
    error: Optional[str] = None
    cache_hit: bool = False
    duration_ms: Optional[float] = None

    def __iter__(self):
        yield self.ok
        yield self.message

    def with_cache_hit(self, cache_hit: bool) -> "InspectionReport":
        return replace(self, cache_hit=cache_hit)

    def with_duration(self, duration_ms: float) -> "InspectionReport":
        return replace(self, duration_ms=duration_ms)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "extension": self.extension,
            "mode": self.mode,
            "ok": self.ok,
            "message": self.message,
            "tags": self.tags,
            "error": self.error,
            "cache_hit": self.cache_hit,
            "duration_ms": self.duration_ms,
        }


def ok_finding(message: str, *tags: str) -> InspectionFinding:
    return InspectionFinding(True, message, (TAG_OK,) + tuple(tags))


def fail_finding(
    message: str, *tags: str, error: Optional[str] = None
) -> InspectionFinding:
    normalized_tags = tuple(tags) if tags else (TAG_UNKNOWN_ERROR,)
    return InspectionFinding(False, message, normalized_tags, error=error)
