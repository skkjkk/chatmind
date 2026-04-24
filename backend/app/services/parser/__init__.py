"""Parser services - auto-detect and dispatch based on file extension"""
import os
from app.services.parser.wechat_parser import WechatParser
from app.services.parser.txt_parser import TxtParser
from app.services.parser.json_parser import JsonParser
from app.services.parser.csv_parser import CsvParser
from app.services.parser.xwechat_parser import XwechatParser

__all__ = ["WechatParser", "TxtParser", "JsonParser", "CsvParser", "XwechatParser", "parse_file"]


def parse_file(file_name: str, content: str) -> tuple[list, str]:
    """
    Auto-detect file format and parse.
    Returns: (list of ParsedMessage, status string)
    """
    ext = os.path.splitext(file_name)[1].lower()

    ext_parsers = {
        ".html": [XwechatParser.parse, WechatParser.parse_html],
        ".htm": [XwechatParser.parse, WechatParser.parse_html],
        ".txt": [TxtParser.parse],
        ".json": [JsonParser.parse],
        ".csv": [CsvParser.parse],
    }

    parsers = ext_parsers.get(ext)
    if not parsers:
        # Unknown extension: try all
        parsers = [
            XwechatParser.parse, WechatParser.parse_html,
            TxtParser.parse, JsonParser.parse, CsvParser.parse
        ]

    for fn in parsers:
        messages, status = fn(content)
        if status == "success" and messages:
            return messages, status

    return [], "failed: unsupported format"
