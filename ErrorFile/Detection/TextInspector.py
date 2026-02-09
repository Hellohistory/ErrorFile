# ErrorFile/Detection/TextInspector.py
"""Plain text and structured data inspectors."""

import configparser
import csv
import email
from email import policy
import json
import sqlite3
from importlib.util import find_spec
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from ..report import TAG_INVALID_FORMAT, TAG_IO_ERROR, fail_finding, ok_finding


def _read_text_content(file_path, max_bytes=262144):
    try:
        with open(file_path, "rb") as raw_file:
            payload = raw_file.read(max_bytes)
    except IOError as exc:
        return None, fail_finding(
            f"Failed to read text file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )

    if b"\x00" in payload:
        return None, fail_finding(
            "Text file contains NUL bytes; likely binary or corrupted.",
            TAG_INVALID_FORMAT,
        )

    try:
        return payload.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, fail_finding(
            f"Text file is not valid UTF-8: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )


def check_json_file(file_path, mode="deep"):
    """Check .json syntax validity."""
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            json.load(json_file)
    except json.JSONDecodeError as exc:
        return fail_finding(
            f"JSON format error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except (IOError, UnicodeDecodeError) as exc:
        return fail_finding(
            f"Failed to read JSON file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("JSON check passed.")


def check_xml_file(file_path, mode="deep"):
    """Check .xml syntax validity."""
    try:
        ET.parse(file_path)
    except ET.ParseError as exc:
        return fail_finding(
            f"XML format error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except IOError as exc:
        return fail_finding(
            f"Failed to read XML file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("XML check passed.")


def check_plain_text_file(file_path, mode="deep"):
    """Check .txt/.md/.log basic readability."""
    _, finding = _read_text_content(file_path)
    if finding:
        return finding
    return ok_finding("Plain text check passed.")


def check_csv_file(file_path, mode="deep"):
    """Check .csv syntax validity."""
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file, strict=True)
            max_rows = 200 if mode == "fast" else None
            for index, _ in enumerate(reader):
                if max_rows is not None and index >= max_rows:
                    break
    except csv.Error as exc:
        return fail_finding(
            f"CSV format error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except (IOError, UnicodeDecodeError) as exc:
        return fail_finding(
            f"Failed to read CSV file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("CSV check passed.")


class _TagCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_count = 0

    def handle_starttag(self, tag, attrs):
        self.tag_count += 1


def check_html_file(file_path, mode="deep"):
    """Check .html/.htm parseability."""
    content, finding = _read_text_content(file_path)
    if finding:
        return finding

    parser = _TagCounter()
    try:
        parser.feed(content)
        parser.close()
    except Exception as exc:
        return fail_finding(
            f"HTML parse error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )

    if parser.tag_count == 0:
        return fail_finding(
            "HTML has no tags; file may be invalid.",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("HTML check passed.")


def check_ini_file(file_path, mode="deep"):
    """Check .ini/.cfg syntax validity."""
    parser = configparser.ConfigParser()
    try:
        with open(file_path, "r", encoding="utf-8") as ini_file:
            parser.read_file(ini_file)
    except configparser.Error as exc:
        return fail_finding(
            f"INI format error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except (IOError, UnicodeDecodeError) as exc:
        return fail_finding(
            f"Failed to read INI file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("INI check passed.")


def check_ndjson_file(file_path, mode="deep"):
    """Check .ndjson syntax validity."""
    max_lines = 200 if mode == "fast" else None
    try:
        with open(file_path, "r", encoding="utf-8") as ndjson_file:
            seen = 0
            for index, line in enumerate(ndjson_file, start=1):
                line = line.strip()
                if not line:
                    continue
                json.loads(line)
                seen += 1
                if max_lines is not None and seen >= max_lines:
                    break
            if seen == 0:
                return fail_finding(
                    "NDJSON file has no JSON records.",
                    TAG_INVALID_FORMAT,
                )
    except json.JSONDecodeError as exc:
        return fail_finding(
            f"NDJSON format error at line {index}: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except (IOError, UnicodeDecodeError) as exc:
        return fail_finding(
            f"Failed to read NDJSON file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("NDJSON check passed.")


def check_tsv_file(file_path, mode="deep"):
    """Check .tsv syntax validity."""
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as tsv_file:
            reader = csv.reader(tsv_file, delimiter="\t", strict=True)
            max_rows = 200 if mode == "fast" else None
            for index, _ in enumerate(reader):
                if max_rows is not None and index >= max_rows:
                    break
    except csv.Error as exc:
        return fail_finding(
            f"TSV format error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except (IOError, UnicodeDecodeError) as exc:
        return fail_finding(
            f"Failed to read TSV file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    return ok_finding("TSV check passed.")


def check_rtf_file(file_path, mode="deep"):
    """Check .rtf header validity."""
    try:
        with open(file_path, "rb") as rtf_file:
            header = rtf_file.read(5)
    except IOError as exc:
        return fail_finding(
            f"Failed to read RTF file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    if header != b"{\\rtf":
        return fail_finding(
            "RTF header invalid; file may be corrupted.",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("RTF check passed.")


def check_eml_file(file_path, mode="deep"):
    """Check .eml parseability."""
    try:
        with open(file_path, "rb") as eml_file:
            content = eml_file.read()
    except IOError as exc:
        return fail_finding(
            f"Failed to read EML file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    try:
        message = email.parser.BytesParser(policy=policy.default).parsebytes(content)
    except Exception as exc:
        return fail_finding(
            f"EML parse error: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    if len(message.keys()) == 0:
        return fail_finding(
            "EML file has no headers; file may be invalid.",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("EML check passed.")


def check_toml_file(file_path, mode="deep"):
    """Check .toml syntax validity."""
    content, finding = _read_text_content(file_path)
    if finding:
        return finding
    parser = None
    if find_spec("tomllib") is not None:
        import tomllib

        parser = tomllib.loads
    elif find_spec("tomli") is not None:
        import tomli

        parser = tomli.loads

    if parser is not None:
        try:
            parser(content)
            return ok_finding("TOML check passed.")
        except Exception as exc:
            return fail_finding(
                f"TOML format error: {exc}",
                TAG_INVALID_FORMAT,
                error=str(exc),
            )

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            continue
        if "=" in stripped:
            return ok_finding("TOML basic check passed.")
    return fail_finding(
        "TOML parser unavailable and no TOML-like key/value content found.",
        TAG_INVALID_FORMAT,
    )


def check_yaml_file(file_path, mode="deep"):
    """Check .yaml/.yml syntax validity."""
    content, finding = _read_text_content(file_path)
    if finding:
        return finding

    if find_spec("yaml") is not None:
        import yaml

        try:
            yaml.safe_load(content)
            return ok_finding("YAML check passed.")
        except Exception as exc:
            return fail_finding(
                f"YAML format error: {exc}",
                TAG_INVALID_FORMAT,
                error=str(exc),
            )

    meaningful = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in {"---", "..."}:
            continue
        meaningful += 1
        if ":" not in stripped and not stripped.startswith("- "):
            return fail_finding(
                "YAML parser unavailable and line lacks mapping/sequence syntax.",
                TAG_INVALID_FORMAT,
            )
    if meaningful == 0:
        return fail_finding(
            "YAML file has no meaningful content.",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("YAML basic check passed.")


def check_msg_file(file_path, mode="deep"):
    """Check .msg (OLE Compound File) header validity."""
    ole_signature = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    try:
        with open(file_path, "rb") as msg_file:
            header = msg_file.read(8)
    except IOError as exc:
        return fail_finding(
            f"Failed to read MSG file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    if header != ole_signature:
        return fail_finding(
            "MSG OLE header invalid; file may be corrupted.",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("MSG header check passed.")


def check_sqlite_file(file_path, mode="deep"):
    """Check .sqlite/.db database integrity."""
    signature = b"SQLite format 3\x00"
    try:
        with open(file_path, "rb") as db_file:
            header = db_file.read(16)
    except IOError as exc:
        return fail_finding(
            f"Failed to read SQLite file: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )
    if header != signature:
        return fail_finding(
            "SQLite header invalid; file may be corrupted.",
            TAG_INVALID_FORMAT,
        )

    try:
        with sqlite3.connect(file_path) as conn:
            pragma = "PRAGMA quick_check;" if mode == "fast" else "PRAGMA integrity_check;"
            row = conn.execute(pragma).fetchone()
    except sqlite3.DatabaseError as exc:
        return fail_finding(
            f"SQLite check failed: {exc}",
            TAG_INVALID_FORMAT,
            error=str(exc),
        )
    except Exception as exc:
        return fail_finding(
            f"SQLite read error: {exc}",
            TAG_IO_ERROR,
            error=str(exc),
        )

    status = (row[0] if row else "").strip().lower()
    if status != "ok":
        return fail_finding(
            f"SQLite integrity check failed: {status or 'unknown'}",
            TAG_INVALID_FORMAT,
        )
    return ok_finding("SQLite check passed.")
