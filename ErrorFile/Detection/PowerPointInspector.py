# 路径：ErrorFile/Detection/PowerPointInspector.py
"""PowerPoint 文件检测工具。"""

from pptx import Presentation
from pptx.exc import PackageNotFoundError


def check_pptx_file(file_path):
    """检查 .pptx 文件是否损坏，并提供详细信息。"""

    try:
        Presentation(file_path)
        return True, "PowerPoint 文档(.pptx)检查通过，文件未损坏。"
    except PackageNotFoundError as exc:
        return False, f"PowerPoint 文档(.pptx)损坏或不是有效的 pptx 格式: {exc}"
    except Exception as exc:  # pragma: no cover - 其他异常依赖第三方库实现
        return False, f"检测 PowerPoint 文档(.pptx)时发生错误: {exc}"
