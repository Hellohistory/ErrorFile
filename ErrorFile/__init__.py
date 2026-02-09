import os
import time
from typing import Iterable, Optional, Tuple

from .cache import InspectionCache
from .Detection.FileInspector import FileInspector, normalize_mode
from .report import (
    InspectionReport,
    TAG_INVALID_MODE,
    TAG_NOT_FOUND,
    TAG_UNKNOWN_ERROR,
)

DEFAULT_CACHE = InspectionCache()
DEFAULT_STAGED_FAST_EXTENSIONS = (
    ".pdf",
    ".xlsx",
    ".xls",
    ".docx",
    ".pptx",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
    ".gz",
    ".bz2",
    ".xz",
    ".mp3",
    ".mp4",
    ".flac",
    ".ogg",
    ".oga",
    ".wav",
    ".sqlite",
    ".db",
    ".msg",
)


def inspect_file_report(
    file_path: str,
    mode: str = "deep",
    use_cache: bool = True,
    cache: Optional[InspectionCache] = None,
    signature_precheck: bool = True,
    signature_precheck_allowlist: Optional[Iterable[str]] = None,
    signature_precheck_denylist: Optional[Iterable[str]] = None,
) -> InspectionReport:
    start = time.perf_counter()
    normalized_mode = None
    abs_path = os.path.abspath(file_path)
    extension = os.path.splitext(abs_path)[-1].lower()
    normalized_allowlist = _normalize_extension_filter(signature_precheck_allowlist)
    normalized_denylist = _normalize_extension_filter(signature_precheck_denylist)

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
            cache_key = (
                abs_path,
                stat.st_size,
                stat.st_mtime_ns,
                normalized_mode,
                signature_precheck,
                normalized_allowlist,
                normalized_denylist,
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
            return report.with_duration((time.perf_counter() - start) * 1000)

        cache = cache or DEFAULT_CACHE
        cached = cache.get(cache_key)
        if cached:
            return cached.with_cache_hit(True).with_duration(
                (time.perf_counter() - start) * 1000
            )

    try:
        inspector = FileInspector(
            abs_path,
            mode=normalized_mode,
            signature_precheck=signature_precheck,
            signature_precheck_allowlist=normalized_allowlist,
            signature_precheck_denylist=normalized_denylist,
        )
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
    signature_precheck: bool = True,
    signature_precheck_allowlist: Optional[Iterable[str]] = None,
    signature_precheck_denylist: Optional[Iterable[str]] = None,
):
    report = inspect_file_report(
        file_path,
        mode=mode,
        use_cache=use_cache,
        cache=cache,
        signature_precheck=signature_precheck,
        signature_precheck_allowlist=signature_precheck_allowlist,
        signature_precheck_denylist=signature_precheck_denylist,
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
    staged_deep: bool = False,
    signature_precheck: bool = True,
    signature_precheck_allowlist: Optional[Iterable[str]] = None,
    signature_precheck_denylist: Optional[Iterable[str]] = None,
    staged_deep_allowlist: Optional[Iterable[str]] = None,
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

    index_groups = {}
    for index, path in enumerate(paths):
        index_groups.setdefault(path, []).append(index)

    unique_paths = list(index_groups.keys())
    results = [None] * len(paths)
    normalized_staged_allowlist = _normalize_extension_filter(staged_deep_allowlist)
    staged_extensions = (
        normalized_staged_allowlist
        if normalized_staged_allowlist is not None
        else DEFAULT_STAGED_FAST_EXTENSIONS
    )

    def _run_reports(target_paths, target_mode, target_signature_precheck):
        reports = {}
        with executor_cls(max_workers=workers) as executor:
            future_to_path = {
                executor.submit(
                    inspect_file_report,
                    path,
                    target_mode,
                    use_cache,
                    cache,
                    target_signature_precheck,
                    signature_precheck_allowlist,
                    signature_precheck_denylist,
                ): path
                for path in target_paths
            }
            for future in as_completed(future_to_path):
                reports[future_to_path[future]] = future.result()
        return reports

    def _run_one_staged(path):
        if not _path_matches_extensions(path, staged_extensions):
            return inspect_file_report(
                path,
                "deep",
                use_cache,
                cache,
                signature_precheck,
                signature_precheck_allowlist,
                signature_precheck_denylist,
            )
        fast_report = inspect_file_report(
            path,
            "fast",
            use_cache,
            cache,
            signature_precheck,
            signature_precheck_allowlist,
            signature_precheck_denylist,
        )
        if not fast_report.ok:
            return _report_with_mode(fast_report, "deep")
        return inspect_file_report(
            path,
            "deep",
            use_cache,
            cache,
            False,
            signature_precheck_allowlist,
            signature_precheck_denylist,
        )

    normalized_mode = None
    try:
        normalized_mode = normalize_mode(mode)
    except ValueError:
        pass

    unique_reports = {}
    if staged_deep and normalized_mode == "deep" and not use_processes:
        with executor_cls(max_workers=workers) as executor:
            future_to_path = {
                executor.submit(_run_one_staged, path): path for path in unique_paths
            }
            for future in as_completed(future_to_path):
                unique_reports[future_to_path[future]] = future.result()
    elif staged_deep and normalized_mode == "deep":
        staged_paths = [path for path in unique_paths if _path_matches_extensions(path, staged_extensions)]
        passthrough_paths = [
            path for path in unique_paths if not _path_matches_extensions(path, staged_extensions)
        ]
        fast_reports = _run_reports(staged_paths, "fast", signature_precheck) if staged_paths else {}
        deep_targets = [path for path, report in fast_reports.items() if report.ok]
        deep_reports = _run_reports(deep_targets, "deep", False) if deep_targets else {}
        passthrough_reports = (
            _run_reports(passthrough_paths, "deep", signature_precheck)
            if passthrough_paths
            else {}
        )
        unique_reports.update(passthrough_reports)
        for path in staged_paths:
            report = deep_reports.get(path)
            if report is None:
                report = _report_with_mode(fast_reports[path], "deep")
            unique_reports[path] = report
    else:
        unique_reports = _run_reports(unique_paths, mode, signature_precheck)

    for path in unique_paths:
        report = unique_reports[path]
        for index in index_groups[path]:
            results[index] = report
    return results


def _normalize_extension_filter(
    extensions: Optional[Iterable[str]],
) -> Optional[Tuple[str, ...]]:
    if extensions is None:
        return None
    normalized = set()
    for extension in extensions:
        lowered = extension.lower()
        if not lowered.startswith("."):
            lowered = f".{lowered}"
        normalized.add(lowered)
    return tuple(sorted(normalized))


def _report_with_mode(report: InspectionReport, mode: str) -> InspectionReport:
    if report.mode == mode:
        return report
    return InspectionReport(
        file_path=report.file_path,
        extension=report.extension,
        mode=mode,
        ok=report.ok,
        message=report.message,
        tags=report.tags,
        error=report.error,
        cache_hit=report.cache_hit,
        duration_ms=report.duration_ms,
    )


def _path_matches_extensions(path: str, extensions: Iterable[str]) -> bool:
    lowered = path.lower()
    for extension in sorted(extensions, key=len, reverse=True):
        if lowered.endswith(extension):
            return True
    return False


__all__ = [
    "InspectionReport",
    "DEFAULT_CACHE",
    "inspect_file",
    "inspect_file_report",
    "inspect_files",
]
