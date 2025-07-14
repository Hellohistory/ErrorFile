import os
from .ImageInspector_fast import ImageInspectorFast
from .ImageInspector_precise import ImageInspector as ImageInspectorPrecise
from .PDFInspector import PDFInspector
from .ExcelInspector import check_excel_file, check_xls_file
from .WordInspector import check_docx_file

class FileInspector:
    def __init__(self, file_path, mode='precise'):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的文件路径不存在: {file_path}")
        self.file_path = file_path
        self.mode = mode
        self.extension = os.path.splitext(file_path)[-1].lower()

    def inspect(self):
        if self.extension in ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']:
            return self.inspect_image()
        elif self.extension == '.pdf':
            return self.inspect_pdf()
        elif self.extension == '.xlsx':
            return check_excel_file(self.file_path)
        elif self.extension == '.xls':
            return check_xls_file(self.file_path)
        elif self.extension == '.docx':
            return self.inspect_word()
        else:
            return False, f"不支持的文件类型: {self.extension}"

    def inspect_image(self):
        if self.mode == 'fast':
            inspector = ImageInspectorFast()
            return inspector.check_image(self.file_path)
        elif self.mode == 'precise':
            inspector = ImageInspectorPrecise(self.file_path)
            return inspector.detailed_check_image()
        else:
            return False, f"未知的图片检测模式: {self.mode}"

    def inspect_pdf(self):
        inspector = PDFInspector(self.file_path)
        return inspector.detailed_check_pdf()

    def inspect_word(self):
        return check_docx_file(self.file_path)