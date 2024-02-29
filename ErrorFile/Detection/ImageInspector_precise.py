# ErrorFile/Detection/ImageInspector_fast.py

from PIL import Image


def check_image(file_path):
    """检查图片是否损坏"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # 验证图片完整性
            return True, "图片文件检查通过，未发现损坏。"
    except (IOError, SyntaxError) as e:
        return False, f"图片文件损坏: {e}"


class ImageInspector:
    def __init__(self, file_path):
        self.file_path = file_path

    def detailed_check_image(self):
        """对图片文件进行详细检查"""
        result, message = check_image(self.file_path)
        return result, message
