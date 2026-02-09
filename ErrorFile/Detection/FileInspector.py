import os
from typing import Callable, Dict, Iterable, Optional, Set

from .ArchiveInspector import (
    check_7z_file,
    check_bzip2_file,
    check_gzip_file,
    check_rar_file,
    check_tar_file,
    check_xz_file,
    check_zip_file,
)
from .ExcelInspector import check_excel_file, check_xls_file
from .ImageInspector_precise import ImageInspector as ImageInspectorPrecise
from .MediaInspector import check_media_file
from .PDFInspector import PDFInspector
from .PowerPointInspector import check_pptx_file
from .TextInspector import (
    check_csv_file,
    check_html_file,
    check_ini_file,
    check_json_file,
    check_msg_file,
    check_ndjson_file,
    check_plain_text_file,
    check_rtf_file,
    check_eml_file,
    check_sqlite_file,
    check_tsv_file,
    check_toml_file,
    check_xml_file,
    check_yaml_file,
)
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


def _normalize_extension_filter(
    extensions: Optional[Iterable[str]],
) -> Optional[Set[str]]:
    if extensions is None:
        return None
    normalized = set()
    for extension in extensions:
        lowered = extension.lower()
        if not lowered.startswith("."):
            lowered = f".{lowered}"
        normalized.add(lowered)
    return normalized


def _starts_with(*prefixes: bytes):
    return lambda header: any(header.startswith(prefix) for prefix in prefixes)


def _is_mp4(header: bytes) -> bool:
    return len(header) >= 8 and header[4:8] == b"ftyp"


def _is_mp3(header: bytes) -> bool:
    if header.startswith(b"ID3"):
        return True
    return len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0


SIGNATURE_CHECKERS = {
    ".jpg": _starts_with(b"\xFF\xD8\xFF"),
    ".jpeg": _starts_with(b"\xFF\xD8\xFF"),
    ".png": _starts_with(b"\x89PNG\r\n\x1a\n"),
    ".gif": _starts_with(b"GIF87a", b"GIF89a"),
    ".bmp": _starts_with(b"BM"),
    ".webp": lambda header: len(header) >= 12
    and header[:4] == b"RIFF"
    and header[8:12] == b"WEBP",
    ".tiff": _starts_with(b"II*\x00", b"MM\x00*"),
    ".pdf": _starts_with(b"%PDF-"),
    ".zip": _starts_with(b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".xlsx": _starts_with(b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".docx": _starts_with(b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".pptx": _starts_with(b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".rar": _starts_with(b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00"),
    ".7z": _starts_with(b"7z\xbc\xaf'\x1c"),
    ".gz": _starts_with(b"\x1F\x8B"),
    ".bz2": _starts_with(b"BZh"),
    ".xz": _starts_with(b"\xFD7zXZ\x00"),
    ".tar.xz": _starts_with(b"\xFD7zXZ\x00"),
    ".mp3": _is_mp3,
    ".mp4": _is_mp4,
    ".flac": _starts_with(b"fLaC"),
    ".ogg": _starts_with(b"OggS"),
    ".oga": _starts_with(b"OggS"),
    ".wav": lambda header: len(header) >= 12
    and header[:4] == b"RIFF"
    and header[8:12] == b"WAVE",
    ".sqlite": _starts_with(b"SQLite format 3\x00"),
    ".db": _starts_with(b"SQLite format 3\x00"),
    ".msg": _starts_with(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"),
}


def _extension_candidates(file_path_lower: str) -> Iterable[str]:
    """
    Build likely extension candidates from longest to shortest.
    Examples:
    - a.tar.gz -> .tar.gz, .gz
    - a.tar.bz2 -> .tar.bz2, .bz2
    - a.pdf -> .pdf
    """
    name = os.path.basename(file_path_lower)
    parts = name.split(".")
    if len(parts) <= 1:
        return ()
    # Keep candidate count small and predictable for performance.
    # Current registry needs at most 2 suffixes, but 3 is still cheap.
    max_suffix_count = min(3, len(parts) - 1)
    candidates = []
    for suffix_count in range(max_suffix_count, 0, -1):
        candidates.append("." + ".".join(parts[-suffix_count:]))
    return tuple(candidates)


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
    registry[".tar.xz"] = _wrap_path_only(check_tar_file)
    registry[".gz"] = _wrap_path_only(check_gzip_file)
    registry[".bz2"] = _wrap_path_only(check_bzip2_file)
    registry[".xz"] = _wrap_path_only(check_xz_file)

    def _wrap_media(extension: str) -> InspectorCallable:
        def _wrapped(file_path: str, mode: str) -> InspectionFinding:
            return check_media_file(file_path, extension, mode)

        return _wrapped

    registry[".mp3"] = _wrap_media(".mp3")
    registry[".mp4"] = _wrap_media(".mp4")
    registry[".flac"] = _wrap_media(".flac")
    registry[".ogg"] = _wrap_media(".ogg")
    registry[".oga"] = _wrap_media(".ogg")
    registry[".wav"] = _wrap_media(".wav")

    registry[".json"] = _wrap_path_only(check_json_file)
    registry[".ndjson"] = _wrap_path_only(check_ndjson_file)
    registry[".xml"] = _wrap_path_only(check_xml_file)
    registry[".toml"] = _wrap_path_only(check_toml_file)
    registry[".yaml"] = _wrap_path_only(check_yaml_file)
    registry[".yml"] = _wrap_path_only(check_yaml_file)
    registry[".tsv"] = _wrap_path_only(check_tsv_file)
    registry[".rtf"] = _wrap_path_only(check_rtf_file)
    registry[".eml"] = _wrap_path_only(check_eml_file)
    registry[".msg"] = _wrap_path_only(check_msg_file)
    registry[".sqlite"] = _wrap_path_only(check_sqlite_file)
    registry[".db"] = _wrap_path_only(check_sqlite_file)
    registry[".txt"] = _wrap_path_only(check_plain_text_file)
    registry[".md"] = _wrap_path_only(check_plain_text_file)
    registry[".log"] = _wrap_path_only(check_plain_text_file)
    registry[".csv"] = _wrap_path_only(check_csv_file)
    registry[".html"] = _wrap_path_only(check_html_file)
    registry[".htm"] = _wrap_path_only(check_html_file)
    registry[".ini"] = _wrap_path_only(check_ini_file)
    registry[".cfg"] = _wrap_path_only(check_ini_file)
    return registry


INSPECTOR_REGISTRY = _build_registry()


def register_inspector(extension: str, inspector: InspectorCallable) -> None:
    """Register a new file inspector."""
    normalized_extension = extension.lower()
    if not normalized_extension.startswith("."):
        normalized_extension = f".{normalized_extension}"
    INSPECTOR_REGISTRY[normalized_extension] = inspector


class FileInspector:
    def __init__(
        self,
        file_path,
        mode="precise",
        signature_precheck: bool = True,
        signature_precheck_allowlist: Optional[Iterable[str]] = None,
        signature_precheck_denylist: Optional[Iterable[str]] = None,
    ):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File path does not exist: {file_path}")
        mode = normalize_mode(mode)
        self.file_path = file_path
        self.mode = mode
        self.file_path_lower = file_path.lower()
        self.extension = os.path.splitext(file_path)[-1].lower()
        self._extension_candidates = _extension_candidates(self.file_path_lower)
        self.signature_precheck = signature_precheck
        self.signature_precheck_allowlist = _normalize_extension_filter(
            signature_precheck_allowlist
        )
        self.signature_precheck_denylist = _normalize_extension_filter(
            signature_precheck_denylist
        )

    def inspect(self) -> InspectionFinding:
        signature_finding = self._precheck_signature()
        if signature_finding:
            return signature_finding

        inspector = self._resolve_inspector()
        if inspector:
            return inspector(self.file_path, self.mode)
        return fail_finding(
            f"Unsupported file type: {self.extension}",
            TAG_UNSUPPORTED,
        )

    def _precheck_signature(self) -> Optional[InspectionFinding]:
        if not self.signature_precheck:
            return None

        for extension in self._extension_candidates:
            checker = SIGNATURE_CHECKERS.get(extension)
            if checker is None:
                continue
            if self.signature_precheck_allowlist is not None:
                if extension not in self.signature_precheck_allowlist:
                    return None
            if (
                self.signature_precheck_denylist
                and extension in self.signature_precheck_denylist
            ):
                return None
            try:
                with open(self.file_path, "rb") as file:
                    header = file.read(32)
            except Exception as exc:
                return fail_finding(
                    f"Failed to read file header: {exc}",
                    TAG_IO_ERROR,
                    error=str(exc),
                )
            if not checker(header):
                return fail_finding(
                    f"File signature mismatch for {extension}; file may be invalid.",
                    TAG_INVALID_FORMAT,
                    TAG_CORRUPTED,
                )
            return None
        return None

    def _resolve_inspector(self) -> Optional[InspectorCallable]:
        for extension in self._extension_candidates:
            inspector = INSPECTOR_REGISTRY.get(extension)
            if inspector:
                return inspector
        return None
