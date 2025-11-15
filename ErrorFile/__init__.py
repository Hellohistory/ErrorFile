# ErrorFile/__init__.py

from .Detection.FileInspector import FileInspector


def inspect_file(file_path, mode="precise"):
    """检查指定路径的文件是否损坏。"""
    try:
        inspector = FileInspector(file_path, mode=mode)
        is_ok, message = inspector.inspect()
        return is_ok, message
    except FileNotFoundError:
        return False, f"文件未找到: {file_path}"
    except Exception as e:
        return False, f"检查文件时发生未知错误: {str(e)}"
