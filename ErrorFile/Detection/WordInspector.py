# ErrorFile/Detection/WordInspector.py

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

def check_docx_file(file_path):
    """检查Word文档(.docx)是否损坏"""
    try:
        Document(file_path)
        return True, "Word文档(.docx)检查通过，文件未损坏。"
    except PackageNotFoundError:
        return False, "Word文档(.docx)损坏或不是有效的docx格式。"
    except Exception as e:
        return False, f"检测Word文档(.docx)时发生错误: {str(e)}"
