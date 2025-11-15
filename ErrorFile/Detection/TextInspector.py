# 路径：ErrorFile/Detection/TextInspector.py
"""纯文本与结构化数据文件检测工具。"""

import json
import xml.etree.ElementTree as ET


def check_json_file(file_path):
    """检查 .json 文件是否为有效的 JSON 文档。"""

    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            json.load(json_file)
    except json.JSONDecodeError as exc:
        return False, f"JSON 文件格式错误: {exc}"
    except (IOError, UnicodeDecodeError) as exc:
        return False, f"无法读取 JSON 文件: {exc}"
    return True, "JSON 文件语法正确。"


def check_xml_file(file_path):
    """检查 .xml 文件是否能够成功解析。"""

    try:
        ET.parse(file_path)
    except ET.ParseError as exc:
        return False, f"XML 文件格式错误: {exc}"
    except IOError as exc:
        return False, f"无法读取 XML 文件: {exc}"
    return True, "XML 文件语法正确。"
