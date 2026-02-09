from typing import Dict

from .base import InspectorCallable
from ..Detection.ArchiveInspector import (
    check_7z_file,
    check_bzip2_file,
    check_gzip_file,
    check_rar_file,
    check_tar_file,
    check_xz_file,
    check_zip_file,
)


def register(registry: Dict[str, InspectorCallable]) -> None:
    registry[".zip"] = check_zip_file
    registry[".rar"] = check_rar_file
    registry[".7z"] = check_7z_file
    registry[".tar"] = check_tar_file
    registry[".tar.gz"] = check_tar_file
    registry[".tar.bz2"] = check_tar_file
    registry[".tar.xz"] = check_tar_file
    registry[".gz"] = check_gzip_file
    registry[".bz2"] = check_bzip2_file
    registry[".xz"] = check_xz_file
