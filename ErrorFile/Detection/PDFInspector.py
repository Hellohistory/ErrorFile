# ErrorFile/Detection/PDFInspector.py

import PyPDF2
from PyPDF2.errors import PdfReadError


class PDFInspector:
    def __init__(self, file_path):
        self.file_path = file_path

    def detailed_check_pdf(self):
        """对PDF文件进行详细的结构性检查"""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file, strict=True)

                if reader.is_encrypted:
                    # 如果文件被密码保护，我们无法深入检查，但文件本身是有效的
                    return True, "PDF文件已加密，无法进行深入检查，但文件结构有效。"

                if len(reader.pages) == 0:
                    return False, "PDF文件不包含任何页面，可能已损坏。"

                # 尝试访问每一页的核心对象
                for page in reader.pages:
                    # 这是一个比提取文本更可靠的底层检查
                    page.get_contents()

        except PdfReadError as e:
            return False, f"PDF文件损坏，无法读取: {e}"
        except Exception as e:
            return False, f"检测PDF过程中发生错误: {str(e)}"

        return True, "PDF文件检查通过，未发现结构性损坏。"