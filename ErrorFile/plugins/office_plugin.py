from typing import Dict

from .base import InspectorCallable
from ..Detection.ExcelInspector import check_excel_file, check_xls_file
from ..Detection.PowerPointInspector import check_pptx_file
from ..Detection.WordInspector import check_docx_file


def register(registry: Dict[str, InspectorCallable]) -> None:
    registry[".xlsx"] = check_excel_file
    registry[".xls"] = check_xls_file
    registry[".docx"] = check_docx_file
    registry[".pptx"] = check_pptx_file
