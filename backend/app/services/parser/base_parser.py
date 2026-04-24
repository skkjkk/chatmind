"""Base parser with common message structure"""
from datetime import datetime
from typing import Optional


class ParsedMessage:
    """Parsed message structure"""
    def __init__(self, sender: str, content: str, timestamp: datetime,
                 message_type: str = "text", is_from_me: bool = False):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        self.message_type = message_type
        self.is_from_me = is_from_me


class BaseParser:
    """Base parser class"""

    @staticmethod
    def detect_message_type(content: str) -> str:
        """Detect message type from content"""
        if not content:
            return "text"
        if "[图片]" in content or "[Image]" in content:
            return "image"
        if "[语音]" in content or "[Voice]" in content:
            return "voice"
        if "[文件]" in content or "[File]" in content:
            return "file"
        if "[视频]" in content or "[Video]" in content:
            return "video"
        import re
        if re.search(r'[\U0001F300-\U0001F9FF]', content):
            return "emoji"
        return "text"

    @staticmethod
    def parse_timestamp(time_str: str) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not time_str:
            return None
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y年%m月%d日 %H:%M",
            "%m-%d %H:%M",
            "%m/%d %H:%M",
            "%H:%M",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        return None
