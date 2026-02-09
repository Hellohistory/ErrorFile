# ErrorFile

ErrorFile is a Python library for detecting corrupted or invalid files across multiple formats.

## Installation

Install the minimal core package:

```bash
pip install ErrorFile
```

Install optional plugin dependencies by capability:

```bash
pip install ErrorFile[pdf]
pip install ErrorFile[image]
pip install ErrorFile[office]
pip install ErrorFile[archive]
pip install ErrorFile[media]
```

Install all optional dependencies:

```bash
pip install ErrorFile[all]
```

You can also combine extras:

```bash
pip install ErrorFile[pdf,image,office]
```

## Quick Start

```python
from ErrorFile import inspect_file

file_path = r"tests/files/TOM_损坏.jpg"
is_ok, message = inspect_file(file_path, mode="deep")
print(f"File: {file_path}\nOK: {is_ok}\nMessage: {message}")
```

## Detection Modes

- `fast`: quick structural checks for high throughput.
- `deep`: deeper parsing for better corruption coverage.
- `precise`: backward-compatible alias of `deep`.

## Public API

### `inspect_file(file_path, mode="deep", ...)`

Returns `(ok, message)` by default.

### `inspect_file_report(file_path, mode="deep", ...)`

Returns an `InspectionReport` with tags, timing, cache-hit metadata, and normalized mode.

### `inspect_files(file_paths, mode="deep", staged_deep=False, ...)`

Batch inspection API with path deduplication and optional staged deep mode.

## Plugin Architecture

ErrorFile now uses internal plugins to register inspectors by extension.

Default plugins:

- image plugin
- pdf plugin
- office plugin
- archive plugin
- media plugin
- text plugin

If a plugin dependency is missing, that plugin is skipped during default loading instead of crashing the package import.

You can inspect load status:

```python
from ErrorFile.Detection.FileInspector import DEFAULT_LOADED_PLUGINS, DEFAULT_SKIPPED_PLUGINS

print(DEFAULT_LOADED_PLUGINS)
print(DEFAULT_SKIPPED_PLUGINS)
```

Register custom inspectors dynamically:

```python
from ErrorFile.Detection.FileInspector import register_inspector
from ErrorFile.report import ok_finding


def check_dummy(path: str, mode: str):
    return ok_finding("Dummy check passed")


register_inspector(".dummy", check_dummy)
```

Or register a plugin registrar:

```python
from ErrorFile.Detection.FileInspector import register_plugin


def register(registry):
    registry[".abc"] = lambda path, mode: ...


register_plugin(register)
```

## Supported File Types

Current coverage includes:

- Images: `jpeg/jpg/png/gif/bmp/webp/tiff/svg`
- PDF: `pdf`
- Office: `xlsx/xls/docx/pptx`
- Archives: `zip/rar/7z/tar/tar.gz/tar.bz2/tar.xz/gz/bz2/xz`
- Media: `mp3/mp4/flac/ogg/oga/wav`
- Text & structured: `txt/md/log/csv/tsv/html/htm/ini/cfg/json/ndjson/xml/toml/yaml/yml/rtf/eml/msg/sqlite/db`

## Notes

- Signature precheck is enabled by default for selected formats.
- For process-based parallel mode in batch API, in-memory cache is disabled automatically.

## License

Apache-2.0. See `LICENSE`.
