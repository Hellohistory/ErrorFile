# ErrorFile/__init__.py

from .Detection.FileInspector import FileInspector

def inspect_file(file_path, mode='precise'):
    """
    检查指定路径的文件是否损坏。这是推荐给用户的顶层接口。

    :param file_path: 文件的完整路径。
    :param mode: 检测模式, 当前主要对图片有效 ('fast' 或 'precise')。
    :return: 一个元组 (is_ok, message)，is_ok是布尔值，message是描述信息。
    """
    try:
        # ✅ 修改了这里的参数名
        inspector = FileInspector(file_path, mode=mode)
        is_ok, message = inspector.inspect()
        return is_ok, message
    except FileNotFoundError:
        return False, f"文件未找到: {file_path}"
    except Exception as e:
        return False, f"检查文件时发生未知错误: {str(e)}"