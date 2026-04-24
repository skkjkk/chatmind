"""Parser for xwechat export format (HTML with embedded JSON data)"""
import json
import re
from datetime import datetime
from app.services.parser.base_parser import BaseParser, ParsedMessage


class XwechatParser(BaseParser):
    """Parser for xwechat tool export format.

    The tool exports HTML files with message data embedded as a
    JavaScript variable: window.WEFLOW_DATA = [...]
    """

    @staticmethod
    def parse(html_content: str) -> tuple[list[ParsedMessage], str]:
        """
        Parse xwechat HTML with embedded WEFLOW_DATA.
        """
        try:
            # Extract contact name from <title>
            contact_name = None
            m_title = re.search(r'<title>(.*?)\s*-\s*聊天记录</title>', html_content)
            if m_title:
                contact_name = m_title.group(1).strip()

            # Extract JSON data from window.WEFLOW_DATA
            m = re.search(r'window\.WEFLOW_DATA\s*=\s*(\[[\s\S]*?\]);', html_content)
            if not m:
                return [], "failed"

            raw_json = m.group(1)
            data = json.loads(raw_json)

            if not isinstance(data, list) or len(data) == 0:
                return [], "failed"

            messages = []
            # s=0 is the other person, s=1 is me
            # Get the other person's name from the first message's avatar alt
            other_name = contact_name or "对方"
            my_name = "我"

            for item in data:
                msg = XwechatParser._parse_item(item, other_name, my_name)
                if msg:
                    messages.append(msg)

            if messages:
                return messages, "success"
            return [], "failed"

        except Exception:
            return [], "failed"

    @staticmethod
    def _parse_item(item: dict, other_name: str, my_name: str) -> ParsedMessage | None:
        """Parse a single WEFLOW_DATA item"""
        sender_id = item.get("s", 0)
        timestamp_unix = item.get("t")
        bubble_html = item.get("b", "")
        avatar_html = item.get("a", "")

        # Determine sender name from avatar alt if possible
        if sender_id == 0:
            # Extract name from avatar alt text
            m_name = re.search(r'alt="([^"]*)"', avatar_html)
            sender = m_name.group(1) if m_name else other_name
            is_from_me = False
        else:
            sender = my_name
            is_from_me = True

        # Parse unix timestamp
        timestamp = None
        if isinstance(timestamp_unix, (int, float)):
            try:
                if timestamp_unix > 1e10:
                    timestamp = datetime.fromtimestamp(timestamp_unix / 1000)
                else:
                    timestamp = datetime.fromtimestamp(timestamp_unix)
            except (ValueError, OSError):
                pass

        # Extract message text from bubble HTML
        content = ""
        if bubble_html:
            m_content = re.search(r'<div class="message-text">(.*?)</div>', bubble_html, re.DOTALL)
            if m_content:
                content_raw = m_content.group(1)
                # Replace img tags with their alt text (preserves emoji meanings)
                content = re.sub(r'<img[^>]*\s+alt="([^"]*)"[^>]*/>', r'\1', content_raw)
                # Strip remaining HTML tags
                content = re.sub(r'<[^>]+>', '', content)
                # Decode common HTML entities
                content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                content = content.replace('&nbsp;', ' ').replace('&quot;', '"')
                content = content.strip()

        # Extract display timestamp from bubble (for reference)
        if not timestamp and bubble_html:
            m_ts = re.search(r'<div class="message-time">(.*?)</div>', bubble_html)
            if m_ts:
                timestamp = XwechatParser.parse_timestamp(m_ts.group(1).strip())

        if not timestamp:
            return None

        # Detect message type
        message_type = "text"
        if content and re.search(r'\[图片\]|\[Image\]', content):
            message_type = "image"
        elif content and re.search(r'\[语音\]|\[Voice\]', content):
            message_type = "voice"
        elif content and re.search(r'\[文件\]|\[File\]', content):
            message_type = "file"
        elif content and re.search(r'\[视频\]|\[Video\]', content):
            message_type = "video"
        elif content and re.match(r'^\[.*?\]$', content.strip()):
            # Pure emoji content (just alt text like [捂脸])
            message_type = "emoji"

        # Ensure content is not empty for display
        if not content and bubble_html and 'inline-emoji' in bubble_html:
            message_type = "emoji"
            message_type = XwechatParser.detect_message_type(content)

        return ParsedMessage(
            sender=sender,
            content=content or "",
            timestamp=timestamp,
            message_type=message_type,
            is_from_me=is_from_me
        )
