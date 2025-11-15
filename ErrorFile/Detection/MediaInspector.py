# 路径：ErrorFile/Detection/MediaInspector.py
"""音视频文件检测工具。"""

from mutagen import File
from mutagen.mp3 import HeaderNotFoundError
from mutagen.mp4 import MP4StreamInfoError


MEDIA_TYPE_HINTS = {
    ".mp3": "MP3 音频",
    ".mp4": "MP4 视频",
    ".flac": "FLAC 无损音频",
    ".ogg": "OGG 音频",
    ".oga": "OGG 音频",
}


def check_media_file(file_path, extension):
    """使用 Mutagen 对音视频文件进行读取校验。"""

    try:
        audio = File(file_path)
    except Exception as exc:  # pragma: no cover - 文件 IO 异常依赖环境
        return (
            False,
            f"读取 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件时发生错误: {exc}",
        )

    if audio is None:
        return (
            False,
            f"Mutagen 无法识别该 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件的格式，可能已损坏。",
        )

    try:
        stream_info = getattr(audio, "info", None)
        if stream_info is None:
            return (
                False,
                f"未能解析 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件的音视频流信息，文件可能已损坏。",
            )

        _ = getattr(stream_info, "length")
        for attr in ("bitrate", "sample_rate", "channels"):
            if hasattr(stream_info, attr):
                _ = getattr(stream_info, attr)
    except HeaderNotFoundError as exc:
        return (
            False,
            f"{MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件音频帧缺失或损坏: {exc}",
        )
    except MP4StreamInfoError as exc:
        return (
            False,
            f"{MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件的 moov 元数据缺失或损坏: {exc}",
        )
    except Exception as exc:  # pragma: no cover - 取决于具体编解码器
        return (
            False,
            f"读取 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件音视频流信息时发生未知错误: {exc}",
        )

    tags = getattr(audio, "tags", None)
    if tags:
        try:
            for key in list(tags.keys()):
                _ = tags.get(key)
        except Exception as exc:  # pragma: no cover - 取决于标签结构
            return (
                False,
                f"解析 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件标签信息时发生错误: {exc}",
            )

    try:
        audio.pprint()
    except HeaderNotFoundError as exc:
        return (
            False,
            f"{MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件音频帧缺失或损坏: {exc}",
        )
    except MP4StreamInfoError as exc:
        return (
            False,
            f"{MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件的 moov 元数据缺失或损坏: {exc}",
        )
    except Exception as exc:  # pragma: no cover - 取决于具体编解码器
        return (
            False,
            f"解析 {MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件元数据时发生未知错误: {exc}",
        )

    return True, f"{MEDIA_TYPE_HINTS.get(extension, '媒体')} 文件检查通过，未发现损坏。"
