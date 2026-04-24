"""TXT chat record parser - supports multiple TXT formats"""
import re
from typing import Optional
from app.services.parser.base_parser import BaseParser, ParsedMessage


class TxtParser(BaseParser):
    """Parser for TXT format chat records"""

    @staticmethod
    def parse(content: str) -> tuple[list[ParsedMessage], str]:
        """
        Parse TXT chat export file.
        Supports formats:
          - [2024-01-15 10:30:00] 张三: 消息内容
          - 2024-01-15 10:30:00 张三说: 消息内容
          - 张三(2024-01-15 10:30:00): 消息内容
          - 张三: 消息内容  (date on previous line)
        """
        try:
            messages = []
            lines = content.split('\n')
            current_date = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parsed = TxtParser._parse_line(line, current_date)
                if parsed:
                    msg, maybe_date = parsed
                    if maybe_date:
                        current_date = maybe_date
                    messages.append(msg)

            if messages:
                return messages, "success"
            return [], "failed"
        except Exception:
            return [], "failed"

    @staticmethod
    def _parse_line(line: str, current_date: Optional[str]) -> Optional[tuple[ParsedMessage, Optional[str]]]:
        """Parse a single line of text"""

        # Pattern 1: [timestamp] sender: content
        m = re.match(r'\[(\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{2}(?::\d{2})?)\]\s*(\S+?)[：:]\s*(.*)', line)
        if m:
            ts = m.group(1)
            sender = m.group(2)
            content = m.group(3)
            timestamp = TxtParser.parse_timestamp(ts)
            if timestamp:
                return ParsedMessage(
                    sender=sender,
                    content=content,
                    timestamp=timestamp,
                    message_type=TxtParser.detect_message_type(content),
                    is_from_me=("我" in sender or "me" in sender.lower())
                ), ts[:10]

        # Pattern 2: timestamp sender[: content]
        m = re.match(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{2}(?::\d{2})?)\s+(\S+?)[：:]\s*(.*)', line)
        if m:
            ts = m.group(1)
            sender = m.group(2)
            content = m.group(3)
            timestamp = TxtParser.parse_timestamp(ts)
            if timestamp:
                return ParsedMessage(
                    sender=sender,
                    content=content,
                    timestamp=timestamp,
                    message_type=TxtParser.detect_message_type(content),
                    is_from_me=("我" in sender or "me" in sender.lower())
                ), ts[:10]

        # Pattern 3: sender(timestamp): content
        m = re.match(r'(\S+?)\((\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{2}(?::\d{2})?)\)[：:]\s*(.*)', line)
        if m:
            sender = m.group(1)
            ts = m.group(2)
            content = m.group(3)
            timestamp = TxtParser.parse_timestamp(ts)
            if timestamp:
                return ParsedMessage(
                    sender=sender,
                    content=content,
                    timestamp=timestamp,
                    message_type=TxtParser.detect_message_type(content),
                    is_from_me=("我" in sender or "me" in sender.lower())
                ), ts[:10]

        # Pattern 4: standalone date line followed by sender: content (next iteration)
        m = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日(?:\s+\d{1,2}:\d{2})?)', line)
        if m:
            return None, m.group(1)

        # Pattern 5: sender: content (no date, use current_date)
        m = re.match(r'(\S+?)[：:]\s*(.*)', line)
        if m and current_date:
            sender = m.group(1)
            content = m.group(2)
            if sender and content:
                # Skip very long lines that are likely not messages
                if len(content) > 500:
                    return None, None
                return ParsedMessage(
                    sender=sender,
                    content=content,
                    timestamp=current_date,
                    message_type=TxtParser.detect_message_type(content),
                    is_from_me=("我" in sender or "me" in sender.lower())
                ), None

        return None, None
