# ErrorFile/Detection/PDFInspector.py

import PyPDF2


def extract_text_from_page(page):
    """尝试从单页提取文本，返回文本或者None"""
    try:
        text = page.extract_text()
        if text:
            return text
        else:
            return None
    except Exception as e:
        print(f"提取文本时发生错误: {e}")
        return None


class PDFInspector:
    def __init__(self, file_path):
        self.file_path = file_path

    def detailed_check_pdf(self):
        """对PDF文件进行详细检查"""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                if num_pages == 0:
                    return False, "PDF文件没有页面，可能已损坏。"

                for i in range(num_pages):
                    page = reader.pages[i]
                    if extract_text_from_page(page) is None:
                        return False, f"第{i + 1}页文本提取失败，PDF文件可能包含无法识别的内容。"
        except PyPDF2.errors.PdfReadError as e:
            return False, f"PDF文件损坏: {e}"
        except Exception as e:
            return False, f"检测过程中发生错误: {str(e)}"

        return True, "PDF文件详细检查通过，未发现显著损坏。"

    def inspect(self):
        """提供统一的检测接口，内部调用详细检查方法"""
        return self.detailed_check_pdf()
