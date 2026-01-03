# ErrorFile/Detection/TextInspector.py
"""Plain text and structured data inspectors."""

import json
import xml.etree.ElementTree as ET

from ..report import TAG_INVALID_FORMAT, TAG_IO_ERROR, fail_finding, ok_finding


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
