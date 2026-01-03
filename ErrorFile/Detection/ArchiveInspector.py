# ErrorFile/Detection/ArchiveInspector.py
"""Archive inspection utilities."""

import bz2
import gzip
import tarfile
import zipfile

import py7zr
import rarfile

from ..report import (
    TAG_CORRUPTED,
    TAG_INVALID_FORMAT,
    TAG_IO_ERROR,
    TAG_PARTIAL,
    fail_finding,
    ok_finding,
)


def check_zip_file(file_path, mode="deep"):
    """Check .zip archive integrity."""
    if not zipfile.is_zipfile(file_path):
        return fail_finding(
            "ZIP signature invalid; not a standard ZIP archive.",
            TAG_INVALID_FORMAT,
        )
    try:
        with zipfile.ZipFile(file_path, "r") as archive:
            if mode == "fast":
                _ = archive.namelist()
                return ok_finding("ZIP fast check passed.")
            corrupted_member = archive.testzip()
            if corrupted_member:
                return fail_finding(
                    f"ZIP member '{corrupted_member}' failed CRC check.",
                    TAG_CORRUPTED,
                )
    except zipfile.BadZipFile as exc:
        return fail_finding(
            f"ZIP archive corrupted: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except Exception as exc:  # pragma: no cover - IO depends on environment
        return fail_finding(
            f"ZIP check failed: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("ZIP deep check passed.")


def check_rar_file(file_path, mode="deep"):
    """Check .rar archive integrity."""
    try:
        if not rarfile.is_rarfile(file_path):
            return fail_finding(
                "RAR signature invalid; not a standard RAR archive.",
                TAG_INVALID_FORMAT,
            )
        with rarfile.RarFile(file_path) as archive:
            if mode == "fast":
                _ = archive.namelist()
                return ok_finding("RAR fast check passed.")
            try:
                archive.testrar()
            except rarfile.RarCannotExec:
                return ok_finding(
                    "RAR format valid but no extractor available for deep validation.",
                    TAG_PARTIAL,
                )
    except rarfile.BadRarFile as exc:
        return fail_finding(
            f"RAR archive corrupted: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except rarfile.NeedFirstVolume:
        return fail_finding(
            "RAR archive missing the first volume.",
            TAG_CORRUPTED,
        )
    except rarfile.Error as exc:
        return fail_finding(
            f"RAR read error: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("RAR deep check passed.")


def check_gzip_file(file_path, mode="deep"):
    """Check .gz archive integrity."""
    try:
        with gzip.open(file_path, "rb") as gzip_file:
            gzip_file.read(1024 if mode == "deep" else 16)
    except (gzip.BadGzipFile, OSError, EOFError) as exc:
        return fail_finding(
            f"Gzip corrupted or invalid: {exc}",
            TAG_CORRUPTED,
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    return ok_finding("Gzip check passed.")


def check_bzip2_file(file_path, mode="deep"):
    """Check .bz2 archive integrity."""
    try:
        with bz2.BZ2File(file_path, "rb") as bzip_file:
            bzip_file.read(1024 if mode == "deep" else 16)
    except (OSError, EOFError) as exc:
        return fail_finding(
            f"Bzip2 corrupted or invalid: {exc}",
            TAG_CORRUPTED,
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    return ok_finding("Bzip2 check passed.")


def check_7z_file(file_path, mode="deep"):
    """Check .7z archive integrity."""
    try:
        with py7zr.SevenZipFile(file_path, "r") as archive:
            if mode == "fast":
                _ = archive.getnames()
                return ok_finding("7z fast check passed.")
            archive.test()
    except py7zr.exceptions.Bad7zFile:
        return fail_finding(
            "7z archive corrupted or invalid.",
            TAG_CORRUPTED,
            TAG_INVALID_FORMAT,
        )
    except Exception as exc:  # pragma: no cover - codec depends on environment
        return fail_finding(
            f"7z check failed: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("7z deep check passed.")


def check_tar_file(file_path, mode="deep"):
    """Check .tar and its compressed variants."""
    try:
        with tarfile.open(file_path, "r:*") as archive:
            if mode == "fast":
                _ = archive.getmembers()
                return ok_finding("Tar fast check passed.")
            for member in archive.getmembers():
                if member.issym() or member.islnk():
                    continue
                if member.isfile():
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        continue
                    try:
                        extracted.read(128)
                    finally:
                        extracted.close()
    except tarfile.ReadError as exc:
        return fail_finding(
            f"Tar archive corrupted: {exc}",
            TAG_CORRUPTED,
            error=str(exc),
        )
    except Exception as exc:  # pragma: no cover - IO and codec depend on environment
        return fail_finding(
            f"Tar check failed: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("Tar deep check passed.")
