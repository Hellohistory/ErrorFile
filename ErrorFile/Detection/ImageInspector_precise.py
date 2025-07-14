# ErrorFile/Detection/ImageInspector_fast.py

from PIL import Image

class ImageInspector:
    def __init__(self, file_path):
        self.file_path = file_path

    def detailed_check_image(self):
        """对图片文件进行详细检查 (精确模式)"""
        try:
            # 第一次打开，只为了验证
            with Image.open(self.file_path) as img:
                img.verify()

            with Image.open(self.file_path) as img_load:
                img_load.load()

            return True, "图片文件检查通过，未发现损坏 (精确检查)。"
        except (IOError, SyntaxError, Image.DecompressionBombError) as e:
            return False, f"图片文件损坏或格式错误: {e} (精确检查)。"
        except Exception as e:
            return False, f"检测图片时发生未知错误: {str(e)} (精确检查)。"