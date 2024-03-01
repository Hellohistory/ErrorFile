import os

from .ImageInspector_fast import ImageInspectorFast
from .ImageInspector_precise import ImageInspector as ImageInspectorPrecise
from .PDFInspector import PDFInspector
from .ExcelInspector import check_excel_file, check_xls_file
from .WordInspector import check_docx_file


class FileInspector:
    def __init__(self, file_path, image_mode='precise'):
        self.file_path = file_path
        self.mode = image_mode
        self.extension = os.path.splitext(file_path)[-1].lower()

    def inspect(self):
        if self.extension in ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']:
            return self.inspect_image()
        elif self.extension == '.pdf':
            return self.inspect_pdf()
        elif self.extension in ['.xlsx', '.xls']:
            return self.inspect_excel()
        elif self.extension == '.docx':
            return self.inspect_word()
        else:
            return False, f"不支持的文件类型: {self.extension}"

    def inspect_image(self):
        if self.mode == 'fast':
            inspector = ImageInspectorFast()
        elif self.mode == 'precise':
            inspector = ImageInspectorPrecise(self.file_path)
            return inspector.detailed_check_image()
        else:
            return False, "未知的检测模式"

        return inspector.check_image(self.file_path)

    def inspect_pdf(self):
        if self.mode not in ['fast', 'precise']:
            return False, "PDF检测不支持选择模式，将自动使用详细检测"
        inspector = PDFInspector(self.file_path)
        return inspector.detailed_check_pdf()

    def inspect_excel(self):
        if self.extension == '.xlsx':
            return check_excel_file(self.file_path)
        elif self.extension == '.xls':
            return check_xls_file(self.file_path)

    def inspect_word(self):
        return check_docx_file(self.file_path)


# 使用示例
def main(file_path, image_mode='precise'):
    try:
        inspector = FileInspector(file_path, image_mode)
        result, message = inspector.inspect()
        return message
    except Exception as e:
        return f"检查文件时出现错误: {str(e)}"


