from typing import Dict

from .base import InspectorCallable
from ..Detection.PDFInspector import PDFInspector


def _inspect_pdf(file_path: str, mode: str):
    inspector = PDFInspector(file_path)
    return inspector.check_pdf(mode)


def register(registry: Dict[str, InspectorCallable]) -> None:
    registry[".pdf"] = _inspect_pdf
