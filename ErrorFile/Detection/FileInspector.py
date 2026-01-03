import os
from typing import Callable, Dict, Iterable, Optional

from .ArchiveInspector import (
    check_7z_file,
    check_bzip2_file,
    check_gzip_file,
    check_rar_file,
    check_tar_file,
    check_zip_file,
)
from .ExcelInspector import check_excel_file, check_xls_file
from .ImageInspector_precise import ImageInspector as ImageInspectorPrecise
from .MediaInspector import check_media_file
from .PDFInspector import PDFInspector
from .PowerPointInspector import check_pptx_file
from .TextInspector import check_json_file, check_xml_file
from .WordInspector import check_docx_file
from ..report import (
    InspectionFinding,
    TAG_CORRUPTED,
    TAG_INVALID_FORMAT,
    TAG_IO_ERROR,
    TAG_UNSUPPORTED,
    fail_finding,
    ok_finding,
)

InspectorCallable = Callable[[str, str], InspectionFinding]

SUPPORTED_MODES = {"fast", "deep"}


def normalize_mode(mode: Optional[str]) -> str:
    if mode is None:
        return "deep"
    if mode == "precise":
        return "deep"
    if mode not in SUPPORTED_MODES:
        raise ValueError("Unsupported mode; allowed: fast, deep")
    return mode


def _wrap_path_only(func: Callable[[str, str], InspectionFinding]) -> InspectorCallable:
    """Wrap inspectors with the common signature."""

    def _wrapped(file_path: str, mode: str) -> InspectionFinding:
        return func(file_path, mode)

    return _wrapped


def _inspect_image(file_path: str, mode: str) -> InspectionFinding:
    inspector = ImageInspectorPrecise(file_path)
    return inspector.check_image(mode)


def _inspect_svg(file_path: str, _: str) -> InspectionFinding:
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


def _inspect_pdf(file_path: str, mode: str) -> InspectionFinding:
    inspector = PDFInspector(file_path)
    return inspector.check_pdf(mode)


def _build_registry() -> Dict[str, InspectorCallable]:
    registry: Dict[str, InspectorCallable] = {}
    image_extensions: Iterable[str] = (
        ".jpeg",
        ".jpg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".tiff",
    )
    for extension in image_extensions:
        registry[extension] = _inspect_image
    registry[".svg"] = _inspect_svg
    registry[".pdf"] = _inspect_pdf
    registry[".xlsx"] = _wrap_path_only(check_excel_file)
    registry[".xls"] = _wrap_path_only(check_xls_file)
    registry[".docx"] = _wrap_path_only(check_docx_file)
    registry[".pptx"] = _wrap_path_only(check_pptx_file)
    registry[".zip"] = _wrap_path_only(check_zip_file)
    registry[".rar"] = _wrap_path_only(check_rar_file)
    registry[".7z"] = _wrap_path_only(check_7z_file)
    registry[".tar"] = _wrap_path_only(check_tar_file)
    registry[".tar.gz"] = _wrap_path_only(check_tar_file)
    registry[".tar.bz2"] = _wrap_path_only(check_tar_file)
    registry[".gz"] = _wrap_path_only(check_gzip_file)
    registry[".bz2"] = _wrap_path_only(check_bzip2_file)

    def _wrap_media(extension: str) -> InspectorCallable:
        def _wrapped(file_path: str, mode: str) -> InspectionFinding:
            return check_media_file(file_path, extension, mode)

        return _wrapped

    registry[".mp3"] = _wrap_media(".mp3")
    registry[".mp4"] = _wrap_media(".mp4")
    registry[".flac"] = _wrap_media(".flac")
    registry[".ogg"] = _wrap_media(".ogg")
    registry[".oga"] = _wrap_media(".ogg")

    registry[".json"] = _wrap_path_only(check_json_file)
    registry[".xml"] = _wrap_path_only(check_xml_file)
    return registry


INSPECTOR_REGISTRY = _build_registry()


def register_inspector(extension: str, inspector: InspectorCallable) -> None:
    """Register a new file inspector."""
    normalized_extension = extension.lower()
    if not normalized_extension.startswith("."):
        normalized_extension = f".{normalized_extension}"
    INSPECTOR_REGISTRY[normalized_extension] = inspector


class FileInspector:
    def __init__(self, file_path, mode="precise"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File path does not exist: {file_path}")
        mode = normalize_mode(mode)
        self.file_path = file_path
        self.mode = mode
        self.file_path_lower = file_path.lower()
        self.extension = os.path.splitext(file_path)[-1].lower()

    def inspect(self) -> InspectionFinding:
        inspector = self._resolve_inspector()
        if inspector:
            return inspector(self.file_path, self.mode)
        return fail_finding(
            f"Unsupported file type: {self.extension}",
            TAG_UNSUPPORTED,
        )

    def _resolve_inspector(self) -> Optional[InspectorCallable]:
        for extension in sorted(INSPECTOR_REGISTRY.keys(), key=len, reverse=True):
            if self.file_path_lower.endswith(extension):
                return INSPECTOR_REGISTRY[extension]
        return None
