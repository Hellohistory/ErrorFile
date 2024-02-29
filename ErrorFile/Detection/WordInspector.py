# ErrorFile/Detection/WordInspector.py

from docx import Document
from docx.opc.exceptions import PackageNotFoundError


def check_docx_file(file_path):
    """检查Word文档(.docx)是否损坏"""
    try:
        # 尝试打开Word文档
        doc = Document(file_path)
        # 如果没有抛出异常，则认为文件没有损坏
        return True, "Word文档(.docx)检查通过，文件未损坏。"
    except PackageNotFoundError as e:
        # 如果文件损坏，将抛出PackageNotFoundError异常
        return False, f"Word文档(.docx)损坏: {str(e)}"
    except Exception as e:
        # 处理其他可能的异常
        return False, f"检测Word文档(.docx)时发生错误: {str(e)}"

