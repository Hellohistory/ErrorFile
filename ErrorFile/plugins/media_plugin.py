from typing import Dict

from .base import InspectorCallable
from ..Detection.MediaInspector import check_media_file


def _wrap_media(extension: str):
    def _wrapped(file_path: str, mode: str):
        return check_media_file(file_path, extension, mode)

    return _wrapped


def register(registry: Dict[str, InspectorCallable]) -> None:
    registry[".mp3"] = _wrap_media(".mp3")
    registry[".mp4"] = _wrap_media(".mp4")
    registry[".flac"] = _wrap_media(".flac")
    registry[".ogg"] = _wrap_media(".ogg")
    registry[".oga"] = _wrap_media(".ogg")
    registry[".wav"] = _wrap_media(".wav")
