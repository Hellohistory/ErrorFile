# 路径：ErrorFile/Detection/ArchiveInspector.py
"""压缩文件检测工具。"""

import zipfile

import rarfile


def check_zip_file(file_path):
    """检查 .zip 文件完整性。"""

    if not zipfile.is_zipfile(file_path):
        return False, "ZIP 文件签名无效，可能不是标准的 ZIP 压缩包。"
    try:
        with zipfile.ZipFile(file_path, "r") as archive:
            corrupted_member = archive.testzip()
            if corrupted_member:
                return (
                    False,
                    f"ZIP 压缩包中的文件 '{corrupted_member}' 无法通过校验，可能已损坏。",
                )
    except zipfile.BadZipFile as exc:
        return False, f"ZIP 压缩包已损坏: {exc}"
    except Exception as exc:  # pragma: no cover - 其他 IO 异常依赖环境
        return False, f"检测 ZIP 压缩包时发生错误: {exc}"
    return True, "ZIP 压缩包检查通过，未发现损坏。"


def check_rar_file(file_path):
    """检查 .rar 文件完整性。"""

    try:
        if not rarfile.is_rarfile(file_path):
            return False, "RAR 文件签名无效，可能不是标准的 RAR 压缩包。"
        try:
            with rarfile.RarFile(file_path) as archive:
                try:
                    archive.testrar()
                except rarfile.RarCannotExec:
                    return True, "RAR 压缩包格式有效，但缺少解压程序进行深度校验。"
        except rarfile.BadRarFile as exc:
            return False, f"RAR 压缩包结构损坏: {exc}"
        except rarfile.NeedFirstVolume:
            return False, "RAR 压缩包缺少分卷的首个文件，无法校验。"
        except rarfile.Error as exc:
            return False, f"读取 RAR 压缩包时发生错误: {exc}"
    except rarfile.Error as exc:
        return False, f"无法识别为 RAR 压缩包: {exc}"
    return True, "RAR 压缩包检查通过，未发现损坏。"
