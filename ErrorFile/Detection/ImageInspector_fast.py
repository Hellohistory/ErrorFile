# ErrorFile/ImageInspector_fast.py

class ImageInspectorFast:
    def check_jpeg(self, file_path):
        """快速检查JPEG文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                if not content.startswith(b'\xff\xd8') or not content.endswith(b'\xff\xd9'):
                    return False, "JPEG文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测JPEG文件时发生错误: {str(e)}"
        return True, "JPEG文件检查通过 (快速检查)。"

    def check_png(self, file_path):
        """快速检查PNG文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                if not content.startswith(b'\x89PNG\r\n\x1a\n') or not content.endswith(b'IEND\xaeB`\x82'):
                    return False, "PNG文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测PNG文件时发生错误: {str(e)}"
        return True, "PNG文件检查通过 (快速检查)。"

    def check_gif(self, file_path):
        """快速检查GIF文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read(6)
                if not content.startswith(b'GIF89a') and not content.startswith(b'GIF87a'):
                    return False, "GIF文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测GIF文件时发生错误: {str(e)}"
        return True, "GIF文件检查通过 (快速检查)。"

    def check_bmp(self, file_path):
        """快速检查BMP文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                if not file.read(2) == b'BM':
                    return False, "BMP文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测BMP文件时发生错误: {str(e)}"
        return True, "BMP文件检查通过 (快速检查)。"

    def check_webp(self, file_path):
        """快速检查WebP文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read(12)
                if not content.startswith(b'RIFF') or not content[8:12] == b'WEBP':
                    return False, "WebP文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测WebP文件时发生错误: {str(e)}"
        return True, "WebP文件检查通过 (快速检查)。"

    def check_tiff(self, file_path):
        """快速检查TIFF文件是否损坏"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read(4)
                if content not in [b'II*\x00', b'MM\x00*']:
                    return False, "TIFF文件标记不完整 (快速检查)。"
        except Exception as e:
            return False, f"检测TIFF文件时发生错误: {str(e)}"
        return True, "TIFF文件检查通过 (快速检查)。"

    def check_svg(self, file_path):
        """快速检查SVG文件是否损坏"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read(1024).strip()
                if '<svg' not in content:
                    return False, "SVG文件内容不完整或格式不正确 (快速检查)。"
        except Exception as e:
            return False, f"检测SVG文件时发生错误: {str(e)}"
        return True, "SVG文件检查通过 (快速检查)。"

    def check_image(self, file_path):
        """根据文件扩展名自动选择并执行相应的快速检测"""
        import os
        extension = os.path.splitext(file_path)[-1].lower().replace('.', '')
        if extension == 'jpg':
            extension = 'jpeg'

        method_name = f'check_{extension}'
        method = getattr(self, method_name, lambda p: (False, f"不支持的文件类型: .{extension}"))
        return method(file_path)