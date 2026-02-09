from typing import Dict

from .base import InspectorCallable
from ..Detection.TextInspector import (
    check_csv_file,
    check_eml_file,
    check_html_file,
    check_ini_file,
    check_json_file,
    check_msg_file,
    check_ndjson_file,
    check_plain_text_file,
    check_rtf_file,
    check_sqlite_file,
    check_toml_file,
    check_tsv_file,
    check_xml_file,
    check_yaml_file,
)


def register(registry: Dict[str, InspectorCallable]) -> None:
    registry[".json"] = check_json_file
    registry[".ndjson"] = check_ndjson_file
    registry[".xml"] = check_xml_file
    registry[".toml"] = check_toml_file
    registry[".yaml"] = check_yaml_file
    registry[".yml"] = check_yaml_file
    registry[".tsv"] = check_tsv_file
    registry[".rtf"] = check_rtf_file
    registry[".eml"] = check_eml_file
    registry[".msg"] = check_msg_file
    registry[".sqlite"] = check_sqlite_file
    registry[".db"] = check_sqlite_file
    registry[".txt"] = check_plain_text_file
    registry[".md"] = check_plain_text_file
    registry[".log"] = check_plain_text_file
    registry[".csv"] = check_csv_file
    registry[".html"] = check_html_file
    registry[".htm"] = check_html_file
    registry[".ini"] = check_ini_file
    registry[".cfg"] = check_ini_file
