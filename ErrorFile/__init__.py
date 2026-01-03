import os
import time
from typing import Iterable, Optional

from .cache import InspectionCache
from .Detection.FileInspector import FileInspector, normalize_mode
from .report import (
    InspectionReport,
    TAG_INVALID_MODE,
    TAG_NOT_FOUND,
    TAG_UNKNOWN_ERROR,
)

DEFAULT_CACHE = InspectionCache()


def inspect_file_report(
    file_path: str,
    mode: str = "deep",
    use_cache: bool = True,
    cache: Optional[InspectionCache] = None,
) -> InspectionReport:
    start = time.perf_counter()
    normalized_mode = None
    abs_path = os.path.abspath(file_path)
    extension = os.path.splitext(abs_path)[-1].lower()

    try:
        normalized_mode = normalize_mode(mode)
    except ValueError as exc:
        report = InspectionReport(
            file_path=abs_path,
            extension=extension,
            mode=str(mode),
            ok=False,
            message=str(exc),
            tags=(TAG_INVALID_MODE,),
            error=str(exc),
        )
        return report.with_duration((time.perf_counter() - start) * 1000)

    cache_key = None
    if use_cache:
        try:
            stat = os.stat(abs_path)
            cache_key = (abs_path, stat.st_size, stat.st_mtime_ns, normalized_mode)
        except FileNotFoundError as exc:
            report = InspectionReport(
                file_path=abs_path,
                extension=extension,
                mode=normalized_mode,
                ok=False,
                message=f"File not found: {file_path}",
                tags=(TAG_NOT_FOUND,),
                error=str(exc),
            )
            return report.with_duration((time.perf_counter() - start) * 1000)

        cache = cache or DEFAULT_CACHE
        cached = cache.get(cache_key)
        if cached:
            return cached.with_cache_hit(True).with_duration(
                (time.perf_counter() - start) * 1000
            )

    try:
        inspector = FileInspector(abs_path, mode=normalized_mode)
        finding = inspector.inspect()
        report = InspectionReport(
            file_path=abs_path,
            extension=extension,
            mode=normalized_mode,
            ok=finding.ok,
            message=finding.message,
            tags=finding.tags,
            error=finding.error,
        )
    except FileNotFoundError as exc:
        report = InspectionReport(
            file_path=abs_path,
            extension=extension,
            mode=normalized_mode,
            ok=False,
            message=f"File not found: {file_path}",
            tags=(TAG_NOT_FOUND,),
            error=str(exc),
        )
    except Exception as exc:
        report = InspectionReport(
            file_path=abs_path,
            extension=extension,
            mode=normalized_mode,
            ok=False,
            message=f"Unexpected error during inspection: {exc}",
            tags=(TAG_UNKNOWN_ERROR,),
            error=str(exc),
        )

    report = report.with_duration((time.perf_counter() - start) * 1000)

    if use_cache and cache_key is not None:
        cache = cache or DEFAULT_CACHE
        if TAG_NOT_FOUND not in report.tags and TAG_INVALID_MODE not in report.tags:
            cache.set(cache_key, report)

    return report


def inspect_file(
    file_path: str,
    mode: str = "deep",
    return_report: bool = False,
    use_cache: bool = True,
    cache: Optional[InspectionCache] = None,
):
    report = inspect_file_report(
        file_path,
        mode=mode,
        use_cache=use_cache,
        cache=cache,
    )
    if return_report:
        return report
    return report.ok, report.message


def inspect_files(
    file_paths: Iterable[str],
    mode: str = "deep",
    workers: Optional[int] = None,
    use_processes: bool = False,
    use_cache: bool = True,
    cache: Optional[InspectionCache] = None,
):
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

    paths = list(file_paths)
    if not paths:
        return []

    if use_processes:
        executor_cls = ProcessPoolExecutor
        # Shared in-memory cache cannot be used across processes safely.
        use_cache = False
        cache = None
    else:
        executor_cls = ThreadPoolExecutor

    results = [None] * len(paths)
    with executor_cls(max_workers=workers) as executor:
        future_to_index = {
            executor.submit(
                inspect_file_report,
                path,
                mode,
                use_cache,
                cache,
            ): index
            for index, path in enumerate(paths)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            results[index] = future.result()
    return results


__all__ = [
    "InspectionReport",
    "DEFAULT_CACHE",
    "inspect_file",
    "inspect_file_report",
    "inspect_files",
]
