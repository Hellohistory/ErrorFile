from importlib import import_module
from typing import Dict, Iterable, List, Tuple

from .base import InspectorCallable

DEFAULT_PLUGIN_MODULES = (
    "ErrorFile.plugins.image_plugin",
    "ErrorFile.plugins.pdf_plugin",
    "ErrorFile.plugins.office_plugin",
    "ErrorFile.plugins.archive_plugin",
    "ErrorFile.plugins.media_plugin",
    "ErrorFile.plugins.text_plugin",
)


def _is_internal_import_error(exc: Exception) -> bool:
    missing_name = getattr(exc, "name", None)
    return bool(missing_name and missing_name.startswith("ErrorFile"))


def load_default_plugins(
    registry: Dict[str, InspectorCallable],
    plugin_modules: Iterable[str] = DEFAULT_PLUGIN_MODULES,
) -> Dict[str, InspectorCallable]:
    loaded_modules: List[str] = []
    skipped_modules: List[str] = []

    for module_path in plugin_modules:
        try:
            module = import_module(module_path)
        except ModuleNotFoundError as exc:
            if _is_internal_import_error(exc):
                raise
            skipped_modules.append(module_path)
            continue
        except ImportError as exc:
            if _is_internal_import_error(exc):
                raise
            skipped_modules.append(module_path)
            continue

        register = getattr(module, "register")
        register(registry)
        loaded_modules.append(module_path)

    load_default_plugins.last_loaded_modules = tuple(loaded_modules)
    load_default_plugins.last_skipped_modules = tuple(skipped_modules)
    return registry


load_default_plugins.last_loaded_modules = tuple()  # type: Tuple[str, ...]
load_default_plugins.last_skipped_modules = tuple()  # type: Tuple[str, ...]
