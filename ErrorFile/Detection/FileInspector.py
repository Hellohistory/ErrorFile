import os
from typing import Callable, Dict, Iterable, Optional, Tuple

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

InspectorCallable = Callable[[str, str], Tuple[bool, str]]


def _wrap_path_only(func: Callable[[str], Tuple[bool, str]]) -> InspectorCallable:
    """将仅接收文件路径的检测函数包装为统一的注册表签名。"""

    def _wrapped(file_path: str, _: str) -> Tuple[bool, str]:
        return func(file_path)

    return _wrapped


def _inspect_image(file_path: str, _: str) -> Tuple[bool, str]:
    inspector = ImageInspectorPrecise(file_path)
    return inspector.detailed_check_image()


def _inspect_svg(file_path: str, _: str) -> Tuple[bool, str]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().lower()
    except Exception as e:  # pragma: no cover - IO 异常路径依赖环境
        return False, f"检测SVG文件时发生错误: {str(e)}"
    if "<svg" in content and "</svg" in content:
        return True, "SVG 文件检查通过，未发现损坏。"
    return False, "SVG 文件缺少必要的 <svg> 标签，可能已损坏。"


def _inspect_pdf(file_path: str, _: str) -> Tuple[bool, str]:
    inspector = PDFInspector(file_path)
    return inspector.detailed_check_pdf()


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
        def _wrapped(file_path: str, _: str) -> Tuple[bool, str]:
            return check_media_file(file_path, extension)

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
    """注册新的文件检测函数或类，便于扩展。"""

    normalized_extension = extension.lower()
    if not normalized_extension.startswith("."):
        normalized_extension = f".{normalized_extension}"
    INSPECTOR_REGISTRY[normalized_extension] = inspector


class FileInspector:
    def __init__(self, file_path, mode="precise"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的文件路径不存在: {file_path}")
        if mode not in (None, "precise"):
            raise ValueError("图片检测模式仅支持 'precise'")
        self.file_path = file_path
        self.mode = mode or "precise"
        self.file_path_lower = file_path.lower()
        self.extension = os.path.splitext(file_path)[-1].lower()

    def inspect(self):
        inspector = self._resolve_inspector()
        if inspector:
            return inspector(self.file_path, self.mode)
        return False, f"不支持的文件类型: {self.extension}"

    def _resolve_inspector(self) -> Optional[InspectorCallable]:
        for extension in sorted(INSPECTOR_REGISTRY.keys(), key=len, reverse=True):
            if self.file_path_lower.endswith(extension):
                return INSPECTOR_REGISTRY[extension]
        return None
