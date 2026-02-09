from typing import Dict

from .base import InspectorCallable
from ..Detection.ImageInspector_precise import ImageInspector as ImageInspectorPrecise
from ..report import (
    TAG_CORRUPTED,
    TAG_INVALID_FORMAT,
    TAG_IO_ERROR,
    fail_finding,
    ok_finding,
)


def _inspect_image(file_path: str, mode: str):
    inspector = ImageInspectorPrecise(file_path)
    return inspector.check_image(mode)


def _inspect_svg(file_path: str, _: str):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().lower()
    except Exception as exc:  # pragma: no cover - IO error depends on environment
        return fail_finding(
            f"SVG read error: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    if "<svg" in content and "</svg" in content:
        return ok_finding("SVG check passed.")
    return fail_finding(
        "SVG missing required <svg> tags; file may be corrupted.",
        TAG_CORRUPTED,
        TAG_INVALID_FORMAT,
    )


def register(registry: Dict[str, InspectorCallable]) -> None:
    image_extensions = (".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp", ".tiff")
    for extension in image_extensions:
        registry[extension] = _inspect_image
    registry[".svg"] = _inspect_svg
